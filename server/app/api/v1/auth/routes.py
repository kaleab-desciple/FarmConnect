"""
Public authentication endpoints (no auth required).
"""
from typing import Optional
import logging
import os

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import httpx

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


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    """Login request with email and password."""
    email: str
    password: str


class LoginResponse(BaseModel):
    """Login response with tokens and user info."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class AuthInfoResponse(BaseModel):
    """Information about authentication configuration."""
    keycloak_url: str
    realm: str
    client_id: str
    token_endpoint: str
    auth_enabled: bool
    message: str


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User login",
    description="Authenticate user with email/password and return tokens. No authentication required."
)
async def login(request: LoginRequest):
    """
    Authenticate user with email and password via Keycloak.
    
    This endpoint proxies the authentication request to Keycloak's token endpoint
    using the password grant flow.
    """
    try:
        # Get Keycloak token endpoint
        keycloak_url = settings.KEYCLOAK_URL.rstrip('/')
        realm = settings.KEYCLOAK_REALM
        client_id = settings.KEYCLOAK_CLIENT_ID
        client_secret = getattr(settings, 'KEYCLOAK_CLIENT_SECRET', None)
        
        logger.info(f"Login attempt: keycloak_url={keycloak_url}, realm={realm}, client_id={client_id}")
        logger.info(f"Client secret present: {bool(client_secret)}")
        
        token_url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token"
        
        # Build token request data
        token_data = {
            "grant_type": "password",
            "client_id": client_id,
            "username": request.email,
            "password": request.password,
        }
        
        # Add client_secret if configured
        if client_secret:
            token_data["client_secret"] = client_secret
        
        # Request token from Keycloak
        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url,
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        
        logger.info(f"Keycloak response status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Keycloak error: {response.text}")
            error_detail = "Invalid email or password"
            try:
                error_data = response.json()
                error_detail = error_data.get("error_description", error_data.get("error", "Invalid email or password"))
            except:
                pass
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_detail
            )
        
        token_data = response.json()
        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token", "")
        expires_in = token_data.get("expires_in", 3600)
        
        # Try to get user info from Keycloak userinfo endpoint
        userinfo_url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/userinfo"
        userinfo = None
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
        
        if user_response.status_code == 200:
            userinfo = user_response.json()
        else:
            # Fallback: decode JWT token directly to get user info
            # This handles cases where userinfo endpoint is unavailable
            logger.warning(f"userinfo endpoint failed ({user_response.status_code}), falling back to JWT decode")
            try:
                # Decode JWT without verification to extract claims
                import base64
                import json
                token_parts = access_token.split('.')
                if len(token_parts) >= 2:
                    # Add padding if needed
                    payload = token_parts[1]
                    padding = 4 - len(payload) % 4
                    if padding != 4:
                        payload += '=' * padding
                    decoded = base64.urlsafe_b64decode(payload)
                    token_data = json.loads(decoded)
                    userinfo = {
                        "sub": token_data.get("sub"),
                        "preferred_username": token_data.get("preferred_username"),
                        "email": token_data.get("email"),
                        "name": token_data.get("name"),
                    }
            except Exception as e:
                logger.warning(f"JWT decode fallback failed: {e}")
        
        if userinfo:
            # Extract role from JWT token's realm_roles
            role = "FARMER"  # Default
            try:
                # Decode JWT without verification to extract claims
                import base64
                import json
                token_parts = access_token.split('.')
                if len(token_parts) >= 2:
                    # Add padding if needed
                    payload = token_parts[1]
                    padding = 4 - len(payload) % 4
                    if padding != 4:
                        payload += '=' * padding
                    decoded = base64.urlsafe_b64decode(payload)
                    token_data = json.loads(decoded)
                    realm_roles = token_data.get("realm_roles", [])
                    # Find the first real role (exclude default Keycloak roles)
                    default_roles = {"default-roles-farm-connect", "offline_access", "uma_authorization"}
                    for r in realm_roles:
                        if r not in default_roles:
                            role = r
                            break
            except Exception:
                pass
            
            user = {
                "id": userinfo.get("sub"),  # Can be None if token lacks sub claim
                "email": userinfo.get("email", request.email),
                "name": userinfo.get("name", userinfo.get("preferred_username", request.email)),
                "phone": userinfo.get("phone_number"),
                "role": role,
            }
        else:
            user = {
                "id": None,
                "email": request.email,
                "name": request.email,
                "role": "FARMER",
            }
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication service unavailable: {str(e)}"
        )


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
        user_id=current_user.keycloak_id,
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


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh access token",
    description="Refresh access token using a valid refresh token. No authentication required."
)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using a valid refresh token.
    
    This endpoint proxies the refresh request to Keycloak's token endpoint.
    """
    try:
        keycloak_url = settings.KEYCLOAK_URL.rstrip('/')
        realm = settings.KEYCLOAK_REALM
        client_id = settings.KEYCLOAK_CLIENT_ID
        client_secret = getattr(settings, 'KEYCLOAK_CLIENT_SECRET', None)
        
        token_url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token"
        
        # Build token request data
        token_data = {
            "grant_type": "refresh_token",
            "refresh_token": request.refresh_token,
            "client_id": client_id,
        }
        
        if client_secret:
            token_data["client_secret"] = client_secret
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=token_data)
            
            if response.status_code != 200:
                logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired refresh token"
                )
            
            token_response = response.json()
            
            return RefreshTokenResponse(
                access_token=token_response["access_token"],
                refresh_token=token_response.get("refresh_token", request.refresh_token),
                token_type=token_response.get("token_type", "bearer"),
                expires_in=token_response.get("expires_in", 3600)
            )
    except httpx.RequestError as e:
        logger.error(f"Token refresh request failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )
