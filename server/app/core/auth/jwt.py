"""
JWT token validation and verification for Keycloak-issued tokens.
"""
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import logging
from functools import lru_cache

from jose import jwt, JWTError, jwk
from jose.exceptions import JWTClaimsError, ExpiredSignatureError
import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


class JWTValidationError(Exception):
    """Custom exception for JWT validation errors."""
    pass


@lru_cache(maxsize=1)
def get_jwks() -> Dict[str, Any]:
    """
    Fetch and cache JWKS (JSON Web Key Set) from Keycloak.
    
    Returns:
        Dict containing the JWKS keys
        
    Raises:
        JWTValidationError: If JWKS cannot be fetched
    """
    try:
        response = requests.get(settings.KEYCLOAK_JWKS_URL, timeout=10)
        response.raise_for_status()
        jwks_data = response.json()
        logger.debug(f"Fetched JWKS with {len(jwks_data.get('keys', []))} keys")
        return jwks_data
    except requests.RequestException as e:
        logger.error(f"Failed to fetch JWKS from Keycloak: {e}")
        raise JWTValidationError(f"Cannot fetch JWKS: {e}")


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token issued by Keycloak.
    
    Args:
        token: The JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        JWTValidationError: If token is invalid, expired, or verification fails
    """
    try:
        # Get JWKS
        jwks = get_jwks()
        
        # Decode header to get kid (key ID)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        if not kid:
            raise JWTValidationError("Token missing 'kid' in header")
        
        # Find the matching key
        rsa_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                rsa_key = key
                break
        
        if not rsa_key:
            raise JWTValidationError(f"No matching key found for kid: {kid}")
        
        # Build list of acceptable issuers
        # Keycloak might use localhost or the internal hostname depending on configuration
        keycloak_url = settings.KEYCLOAK_URL.rstrip('/')
        allowed_issuers = [
            settings.KEYCLOAK_ISSUER,
            f"{keycloak_url}/realms/{settings.KEYCLOAK_REALM}",
        ]
        # Add alternative with localhost if keycloak URL uses internal hostname
        if "keycloak" in keycloak_url:
            allowed_issuers.append(keycloak_url.replace("keycloak", "localhost") + f"/realms/{settings.KEYCLOAK_REALM}")
        if "localhost" not in keycloak_url:
            allowed_issuers.append(keycloak_url.replace("keycloak", "localhost") + f"/realms/{settings.KEYCLOAK_REALM}")
        
        logger.debug(f"Validating token issuer against: {allowed_issuers}")
        
        # Verify and decode token - try each allowed issuer
        payload = None
        last_error = None
        for issuer in allowed_issuers:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=settings.KEYCLOAK_AUDIENCE,
                    issuer=issuer,
                    options={
                        "verify_signature": True,
                        "verify_aud": True,
                        "verify_iss": True,
                        "verify_exp": True,
                    }
                )
                logger.debug(f"Token verified successfully with issuer: {issuer}")
                break
            except JWTClaimsError as e:
                last_error = e
                continue
        
        if payload is None and last_error:
            raise JWTValidationError(f"Invalid token claims: {last_error}")
        
        logger.debug(f"Token verified successfully for subject: {payload.get('sub')}")
        return payload
        
    except ExpiredSignatureError:
        logger.warning("Token has expired")
        raise JWTValidationError("Token has expired")
    except JWTClaimsError as e:
        logger.warning(f"Token claims validation failed: {e}")
        raise JWTValidationError(f"Invalid token claims: {e}")
    except JWTError as e:
        logger.warning(f"JWT validation error: {e}")
        raise JWTValidationError(f"Invalid token: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {e}")
        raise JWTValidationError(f"Token validation failed: {e}")


def extract_realm_roles(payload: Dict[str, Any]) -> list[str]:
    """Extract realm-level roles (Human users)."""
    roles = []
    
    # Standard realm access
    realm_access = payload.get("realm_access", {})
    if isinstance(realm_access, dict):
        realm_roles = realm_access.get("roles", [])
        if isinstance(realm_roles, list):
            roles.extend(realm_roles)
            
    # Custom realm_roles claim if present
    custom_realm_roles = payload.get("realm_roles", [])
    if isinstance(custom_realm_roles, list):
        roles.extend(custom_realm_roles)
        
    excluded_roles = {"offline_access", "uma_authorization", "default-roles-farm-connect"}
    return list(set(r for r in roles if r not in excluded_roles))


def extract_client_roles(payload: Dict[str, Any]) -> list[str]:
    """Extract client-level roles (Service accounts)."""
    resource_access = payload.get("resource_access", {})
    if not isinstance(resource_access, dict):
        return []
        
    client_access = resource_access.get(settings.KEYCLOAK_CLIENT_ID, {})
    if not isinstance(client_access, dict):
        return []
        
    client_roles = client_access.get("roles", [])
    if isinstance(client_roles, list):
        return list(set(client_roles))
    
    return []


def extract_roles(payload: Dict[str, Any]) -> list[str]:
    """
    Combined roles for backward compatibility or simple checks.
    Merges realm and client roles.
    """
    return list(set(extract_realm_roles(payload) + extract_client_roles(payload)))


def is_service_account(payload: Dict[str, Any]) -> bool:
    """
    Determine if the token belongs to a service account.
    
    Service accounts have:
    - azp (authorized party) claim
    - No 'preferred_username' or it starts with 'service-account-'
    
    Args:
        payload: Decoded JWT payload
        
    Returns:
        True if this is a service account token
    """
    username = payload.get("preferred_username", "")
    azp = payload.get("azp", "")
    
    is_service = (
        username.startswith("service-account-") or
        (azp == settings.KEYCLOAK_CLIENT_ID and not username)
    )
    
    return is_service


def get_user_id(payload: Dict[str, Any]) -> Optional[str]:
    """
    Extract user ID from token payload.
    
    Args:
        payload: Decoded JWT payload
        
    Returns:
        User ID (sub claim) or fallback to email/preferred_username for service accounts
    """
    if is_service_account(payload):
        return None
    
    # Try sub first, then fall back to email or preferred_username
    user_id = payload.get("sub")
    #if not user_id:
        # Fallback: use email as user identifier if sub is missing
    #    user_id = payload.get("email") or payload.get("preferred_username")
    
    return user_id


def get_username(payload: Dict[str, Any]) -> Optional[str]:
    """
    Extract username from token payload.
    
    Args:
        payload: Decoded JWT payload
        
    Returns:
        Username (preferred_username) or None
    """
    return payload.get("preferred_username")


def get_email(payload: Dict[str, Any]) -> Optional[str]:
    """
    Extract email from token payload.
    
    Args:
        payload: Decoded JWT payload
        
    Returns:
        Email address or None
    """
    return payload.get("email")
