"""
Service account token management for internal backend jobs.
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import threading

import requests
from requests.auth import HTTPBasicAuth

from app.core.config import settings

logger = logging.getLogger(__name__)


class ServiceAccountTokenCache:
    """Thread-safe cache for service account tokens."""
    
    def __init__(self):
        self._tokens: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def get(self, service_name: str) -> Optional[str]:
        """Get cached token if still valid."""
        with self._lock:
            token_data = self._tokens.get(service_name)
            if not token_data:
                return None
            
            # Check if token is expired (with 60 second buffer)
            expires_at = token_data.get("expires_at")
            if expires_at and datetime.now() < expires_at - timedelta(seconds=60):
                return token_data.get("token")
            
            # Token expired, remove from cache
            del self._tokens[service_name]
            return None
    
    def set(self, service_name: str, token: str, expires_in: int):
        """Cache token with expiration."""
        with self._lock:
            self._tokens[service_name] = {
                "token": token,
                "expires_at": datetime.now() + timedelta(seconds=expires_in)
            }
    
    def clear(self, service_name: Optional[str] = None):
        """Clear cached token(s)."""
        with self._lock:
            if service_name:
                self._tokens.pop(service_name, None)
            else:
                self._tokens.clear()


# Global token cache
_token_cache = ServiceAccountTokenCache()


def get_service_token(service_name: str = "default") -> str:
    """
    Get a service account token using client credentials flow.
    
    Args:
        service_name: Name of the service (for cache key)
        
    Returns:
        JWT access token
        
    Raises:
        Exception: If token acquisition fails
    """
    # Check cache first
    cached_token = _token_cache.get(service_name)
    if cached_token:
        logger.debug(f"Using cached token for service: {service_name}")
        return cached_token
    
    # Acquire new token
    logger.info(f"Acquiring new service account token for: {service_name}")
    
    try:
        response = requests.post(
            settings.KEYCLOAK_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": settings.KEYCLOAK_CLIENT_ID,
                "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
            },
            timeout=10
        )
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in", 300)  # Default 5 minutes
        
        if not access_token:
            raise Exception("No access_token in response")
        
        # Cache the token
        _token_cache.set(service_name, access_token, expires_in)
        
        logger.info(f"Successfully acquired service token (expires in {expires_in}s)")
        return access_token
        
    except requests.RequestException as e:
        logger.error(f"Failed to acquire service account token: {e}")
        raise Exception(f"Service account authentication failed: {e}")


def validate_service_token(token: str, required_roles: Optional[list[str]] = None) -> Dict[str, Any]:
    """
    Validate a service account token and check roles.
    
    Args:
        token: JWT token to validate
        required_roles: Optional list of required client roles
        
    Returns:
        Decoded token payload
        
    Raises:
        Exception: If validation fails
    """
    from app.core.auth.jwt import verify_token, extract_roles, is_service_account
    
    # Verify token
    payload = verify_token(token)
    
    # Ensure it's a service account
    if not is_service_account(payload):
        raise Exception("Token is not from a service account")
    
    # Check required roles if specified
    if required_roles:
        token_roles = extract_roles(payload)
        
        # Check for client-specific roles
        resource_access = payload.get("resource_access", {})
        client_access = resource_access.get(settings.KEYCLOAK_CLIENT_ID, {})
        client_roles = client_access.get("roles", [])
        
        missing_roles = set(required_roles) - set(client_roles)
        if missing_roles:
            raise Exception(f"Service account missing required roles: {missing_roles}")
    
    return payload


def clear_token_cache(service_name: Optional[str] = None):
    """
    Clear cached service tokens.
    
    Args:
        service_name: Specific service to clear, or None for all
    """
    _token_cache.clear(service_name)
    logger.info(f"Cleared token cache for: {service_name or 'all services'}")
