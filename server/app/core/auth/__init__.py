"""
Authentication and authorization module.
"""
from app.core.auth.jwt import (
    verify_token,
    extract_roles,
    is_service_account,
    get_user_id,
    get_username,
    get_email,
    JWTValidationError
)

from app.core.auth.dependencies import (
    TokenPayload,
    get_current_user,
    get_optional_user,
    require_realm_role,
    require_client_role,
    require_permission,
    block_service_accounts,
    require_service_account,
)

from app.core.auth.service_account import (
    get_service_token,
    validate_service_token,
    clear_token_cache
)

__all__ = [
    # JWT functions
    "verify_token",
    "extract_roles",
    "is_service_account",
    "get_user_id",
    "get_username",
    "get_email",
    "JWTValidationError",
    
    # Dependencies
    "TokenPayload",
    "get_current_user",
    "get_optional_user",
    "require_roles",
    "require_any_role",
    "require_permission",
    "block_service_accounts",
    "require_service_account",
    "ROLE_PERMISSIONS",
    
    # Service accounts
    "get_service_token",
    "validate_service_token",
    "clear_token_cache",
]
