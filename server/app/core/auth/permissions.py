"""
API Permission Matrix and Constants.
Maps permissions to the roles that are allowed to perform them.

Roles describe WHO you are.
Permissions describe WHAT you can do.
"""

# Realm Roles (Human Users)
REALM_ROLES = ["ADMIN", "MANAGER", "AGENT", "FARMER", "MERCHANT", "DELIVERY"]

# Client Roles (Service Accounts)
CLIENT_ROLES = ["system_internal", "escrow_service", "reporting_service"]

# Permission Matrix
# Mapping: permission_key -> list of allowed roles
# Human endpoints use Realm Roles.
# Background/System endpoints use Client Roles.
# ADMIN (Realm Role) is typically added to most human endpoints.
PERMISSIONS = {
    # Users Domain
    "users:provision": ["ADMIN", "MANAGER", "AGENT"],
    "users:read": ["ADMIN", "MANAGER", "AGENT"],
    "users:write": ["ADMIN", "MANAGER"],
    "users:reputation": ["ADMIN", "MANAGER", "AGENT"],
    
    # Products Domain
    "products:create": ["ADMIN", "FARMER"],
    "products:update": ["ADMIN", "FARMER"],
    "products:read": ["ADMIN", "MANAGER", "AGENT", "FARMER", "MERCHANT", "DELIVERY"],
    "products:delete": ["ADMIN"],
    
    # Orders Domain
    "orders:create": ["ADMIN", "FARMER", "MERCHANT"],
    "orders:read": ["ADMIN", "MANAGER", "AGENT", "FARMER", "MERCHANT", "DELIVERY"],
    "orders:update": ["ADMIN", "MANAGER", "FARMER", "MERCHANT", "DELIVERY"],
    "orders:cancel": ["ADMIN", "MANAGER", "FARMER", "MERCHANT"],
    
    # Escrow Domain
    "escrow:read": ["ADMIN", "MANAGER", "reporting_service"],
    "escrow:fund": ["ADMIN", "escrow_service"], # Machine action primarily
    "escrow:release": ["ADMIN", "escrow_service"],
    "escrow:refund": ["ADMIN", "escrow_service"],

    
    # Loans Domain
    "loans:request": ["ADMIN", "FARMER"],
    "loans:approve": ["ADMIN", "MANAGER"],
    "loans:read": ["ADMIN", "MANAGER", "FARMER", "reporting_service"],
    "loans:disburse": ["ADMIN", "system_internal"],
    
    # Disputes Domain
    "disputes:create": ["ADMIN", "FARMER", "MERCHANT", "DELIVERY"],
    "disputes:resolve": ["ADMIN", "MANAGER"],
    "disputes:read": ["ADMIN", "MANAGER", "reporting_service"],
    
    # Reports Domain (Read-only)
    "reports:financial": ["ADMIN", "MANAGER", "reporting_service"],
    "reports:operational": ["ADMIN", "MANAGER", "AGENT", "reporting_service"],
    
    # Ledger Domain
    "ledger:read": ["ADMIN", "MANAGER", "reporting_service"],
    "ledger:write": ["ADMIN", "system_internal", "escrow_service"],
    
    # Internal / System Domain
    "system:maintenance": ["ADMIN", "system_internal"],
    "system:analytics": ["ADMIN", "reporting_service"],
}
