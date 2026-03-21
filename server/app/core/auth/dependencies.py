"""
FastAPI dependencies for authentication and authorization.
"""
from typing import Optional, Callable, List
from functools import wraps
import logging

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.auth.jwt import (
    verify_token, 
    extract_realm_roles,
    extract_client_roles, 
    is_service_account,
    get_user_id,
    get_username,
    get_email,
    JWTValidationError
)
from app.core.auth.permissions import PERMISSIONS, REALM_ROLES

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


class TokenPayload:
    """
    Represents decoded and validated token data.

    Attributes:
        keycloak_id:    The Keycloak-generated user UUID (JWT ``sub`` claim).
                        Use this for Keycloak API calls, ``userinfo`` lookups,
                        and filtering on ``users.keycloak_id``.
        system_user_id: The internal system user ID (e.g. ``FAR-00001``).
                        Populated by the ``get_enriched_user`` dependency.
                        Use this for any DB foreign-key that references ``users.id``.
    """

    def __init__(self, payload: dict):
        self.raw_payload = payload
        self.keycloak_id: Optional[str] = get_user_id(payload)   # Keycloak sub claim
        self.system_user_id: Optional[str] = None                 # Populated lazily via get_enriched_user
        self.username = get_username(payload)
        self.email = get_email(payload)
        self.realm_roles = extract_realm_roles(payload)
        self.client_roles = extract_client_roles(payload)
        self.is_service_account = is_service_account(payload)
        self.subject = payload.get("sub")

    def has_realm_role(self, role: str) -> bool:
        return role in self.realm_roles

    def has_client_role(self, role: str) -> bool:
        return role in self.client_roles

    @property
    def all_roles(self) -> List[str]:
        return list(set(self.realm_roles + self.client_roles))


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> TokenPayload:
    """
    Dependency to extract and validate current user from JWT token.
    """
    if not settings.AUTH_ENABLED:
        logger.warning("Authentication is DISABLED - using mock user")
        mock = TokenPayload({
            "sub": "dev-user",
            "preferred_username": "dev-user",
            "email": "dev@example.com",
            "realm_access": {"roles": ["ADMIN"]},
            "resource_access": {
                settings.KEYCLOAK_CLIENT_ID: {"roles": ["system_internal", "escrow_service"]}
            },
            "azp": settings.KEYCLOAK_CLIENT_ID
        })
        mock.system_user_id = "dev-user"  # dev sentinel — matches onboarding_agent_id in fixtures
        return mock
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        payload = verify_token(token)
        token_payload = TokenPayload(payload)
        return token_payload
    except JWTValidationError as e:
        logger.warning(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[TokenPayload]:
    """
    Dependency to optionally extract user if token is present.
    Returns None if no token provided or if token is invalid.
    """
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        return TokenPayload(payload)
    except JWTValidationError:
        return None


def get_enriched_user(
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TokenPayload:
    """
    Enriches a validated ``TokenPayload`` with the internal system user_id.

    Makes a single DB lookup by ``keycloak_id`` (falling back to email) to
    populate ``current_user.system_user_id`` — the ``users.id`` value used
    as a foreign key throughout the application.

    Use this dependency (instead of ``get_current_user``) on any route that
    needs to compare or store the *internal* system user ID (e.g. FK references
    to ``users.id`` such as weather alert subscriptions, order ownership).
    """
    if current_user.system_user_id:  # already populated (dev mock or earlier call)
        return current_user
    if current_user.is_service_account or not current_user.keycloak_id:
        return current_user

    from app.infrastructure.repositories.user_repo import UserRepository
    user_repo = UserRepository(db)
    user = user_repo.get_by_keycloak_id(current_user.keycloak_id)
    if not user and current_user.email:
        user = user_repo.get_by_email(current_user.email)
    if user:
        current_user.system_user_id = user.id
    return current_user


def require_auth(
    current_user: TokenPayload = Depends(get_current_user)
) -> TokenPayload:
    """
    Dependency to require authentication.
    Ensures the user is logged in.
    """
    return current_user


def require_moderator(
    current_user: TokenPayload = Depends(get_current_user)
) -> TokenPayload:
    """
    Dependency to require moderator role.
    User must have MODERATOR realm role.
    """
    if "MODERATOR" not in current_user.realm_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator role required"
        )
    return current_user


def require_admin(
    current_user: TokenPayload = Depends(get_current_user)
) -> TokenPayload:
    """
    Dependency to require admin role.
    User must have ADMIN realm role.
    """
    if "ADMIN" not in current_user.realm_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return current_user


def require_realm_role(*allowed_roles: str):
    """Enforce that the user has at least one of the specified realm roles."""
    def dependency(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if not any(role in current_user.realm_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient realm roles. Required one of: {allowed_roles}"
            )
        return current_user
    return dependency


def require_client_role(*allowed_roles: str):
    """Enforce that the service account has at least one of the specified client roles."""
    def dependency(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if not any(role in current_user.client_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient client roles. Required one of: {allowed_roles}"
            )
        return current_user
    return dependency


def require_permission(permission_key: str):
    """
    Dependency factory to require a specific permission.
    Checks allowed roles from the PERMISSIONS matrix.
    """
    def dependency(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        allowed_roles = PERMISSIONS.get(permission_key, [])
        
        # Check if any of the user's roles are in the allowed list
        # We check both realm and client roles against the authoritative list
        if not any(role in current_user.all_roles for role in allowed_roles):
            logger.warning(
                f"Access denied: user {current_user.username} lacks permission '{permission_key}'"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission_key}"
            )
        
        return current_user
    
    return dependency


def block_service_accounts(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
    """
    Dependency to block service accounts from accessing user endpoints.
    
    Usage:
        @router.get("/profile", dependencies=[Depends(block_service_accounts)])
    """
    if current_user.is_service_account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Service accounts cannot access this endpoint"
        )
    return current_user


def require_service_account(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
    """
    Dependency to require service account authentication.
    
    Usage:
        @router.post("/internal/reconcile", dependencies=[Depends(require_service_account)])
    """
    if not current_user.is_service_account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires service account authentication"
        )
    return current_user
