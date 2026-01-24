"""
Public authentication endpoints (no auth required).
"""
from typing import Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.config import settings
from app.core.auth import (
    TokenPayload,
    get_optional_user,
    verify_token,
    JWTValidationError,
    extract_roles,
    is_service_account,
    get_user_id,
    get_username,
    get_email
)

logger = logging.getLogger(__name__)

router = APIRouter()


class AuthInfoResponse(BaseModel):
    """Information about authentication configuration."""
    keycloak_url: str
    realm: str
    client_id: str
    token_endpoint: str
    auth_enabled: bool
    message: str


class TokenInfoResponse(BaseModel):
    """Information about a decoded token."""
    valid: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    roles: list[str] = []
    is_service_account: bool = False
    expires_at: Optional[int] = None


@router.get(
    "/info",
    response_model=AuthInfoResponse,
    summary="Get authentication configuration",
    description="Returns Keycloak configuration for obtaining tokens. No authentication required."
)
def get_auth_info():
    """
    Get authentication configuration information.
    
    Use this endpoint to discover how to authenticate with the API.
    """
    return AuthInfoResponse(
        keycloak_url=settings.KEYCLOAK_URL,
        realm=settings.KEYCLOAK_REALM,
        client_id=settings.KEYCLOAK_CLIENT_ID,
        token_endpoint=settings.KEYCLOAK_TOKEN_URL,
        auth_enabled=settings.AUTH_ENABLED,
        message=(
            "To authenticate, obtain a token from the token_endpoint using "
            "username/password (grant_type=password) or client credentials "
            "(grant_type=client_credentials). Include the token in the "
            "Authorization header as 'Bearer <token>'."
        )
    )


@router.get(
    "/health",
    summary="Authentication health check",
    description="Check if authentication system is operational. No authentication required."
)
def auth_health_check():
    """
    Health check for authentication system.
    
    Verifies that Keycloak is reachable and JWKS can be fetched.
    """
    try:
        from app.core.auth.jwt import get_jwks
        jwks = get_jwks()
        
        return {
            "status": "healthy",
            "auth_enabled": settings.AUTH_ENABLED,
            "keycloak_reachable": True,
            "jwks_keys_count": len(jwks.get("keys", []))
        }
    except Exception as e:
        logger.error(f"Auth health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Authentication service unavailable: {str(e)}"
        )


@router.get(
    "/me",
    response_model=TokenInfoResponse,
    summary="Get current user info",
    description="Decode and return information about the current user's token. Requires authentication."
)
def get_current_user_info(current_user: Optional[TokenPayload] = Depends(get_optional_user)):
    """
    Get information about the current authenticated user.
    
    If no token is provided or token is invalid, returns valid=False.
    """
    if not current_user:
        return TokenInfoResponse(
            valid=False,
            message="No valid authentication token provided"
        )
    
    return TokenInfoResponse(
        valid=True,
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        roles=current_user.all_roles,
        is_service_account=current_user.is_service_account,
        expires_at=current_user.raw_payload.get("exp")
    )


@router.post(
    "/verify",
    response_model=TokenInfoResponse,
    summary="Verify a token",
    description="Verify and decode a JWT token. No authentication required (token in body)."
)
def verify_token_endpoint(token: str):
    """
    Verify and decode a JWT token.
    
    Useful for debugging and testing token validity.
    """
    try:
        payload = verify_token(token)
        
        return TokenInfoResponse(
            valid=True,
            user_id=get_user_id(payload),
            username=get_username(payload),
            email=get_email(payload),
            roles=extract_roles(payload),
            is_service_account=is_service_account(payload),
            expires_at=payload.get("exp")
        )
    except JWTValidationError as e:
        return TokenInfoResponse(
            valid=False,
            message=str(e)
        )
