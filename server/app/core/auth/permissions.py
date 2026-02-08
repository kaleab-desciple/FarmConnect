"""
API Permission Matrix and Constants.
Maps permissions to the roles that are allowed to perform them.

Roles describe WHO you are.
Permissions describe WHAT you can do.
"""

# Realm Roles (Human Users)
REALM_ROLES = ["ADMIN", "MANAGER", "AGENT", "FARMER", "MERCHANT", "DELIVERY", "AGRONOMIST", "FIELD_ANALYST"]

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
    
    # Agricultural Intelligence Domain
    # Farms - FARMER: Own CRUD, AGRONOMIST: Assigned R, FIELD_ANALYST: All R, ADMIN: All CRUD
    "farms:create": ["ADMIN", "FARMER"],
    "farms:read:own": ["FARMER"],
    "farms:read:assigned": ["AGRONOMIST"],
    "farms:read:all": ["ADMIN", "FIELD_ANALYST"],
    "farms:update:own": ["FARMER"],
    "farms:update:all": ["ADMIN"],
    "farms:delete:own": ["FARMER"],
    "farms:delete:all": ["ADMIN"],
    
    # Fields - FARMER: Own CRUD, AGRONOMIST: Assigned R, FIELD_ANALYST: All R, ADMIN: All CRUD
    "fields:create": ["ADMIN", "FARMER"],
    "fields:read:own": ["FARMER"],
    "fields:read:assigned": ["AGRONOMIST"],
    "fields:read:all": ["ADMIN", "FIELD_ANALYST"],
    "fields:update:own": ["FARMER"],
    "fields:update:all": ["ADMIN"],
    "fields:delete:own": ["FARMER"],
    "fields:delete:all": ["ADMIN"],
    
    # Crop Cycles - FARMER: Own CRUD, AGRONOMIST: Assigned RU, FIELD_ANALYST: All R, ADMIN: All CRUD
    "crop_cycles:create": ["ADMIN", "FARMER"],
    "crop_cycles:read:own": ["FARMER"],
    "crop_cycles:read:assigned": ["AGRONOMIST"],
    "crop_cycles:read:all": ["ADMIN", "FIELD_ANALYST"],
    "crop_cycles:update:own": ["FARMER"],
    "crop_cycles:update:assigned": ["AGRONOMIST"],
    "crop_cycles:update:all": ["ADMIN"],
    "crop_cycles:delete:own": ["FARMER"],
    "crop_cycles:delete:all": ["ADMIN"],
    
    # NDVI Data - FARMER: Own R, AGRONOMIST: Assigned R, FIELD_ANALYST: All CRUD, ADMIN: All CRUD
    "ndvi:create": ["ADMIN", "FIELD_ANALYST"],
    "ndvi:read:own": ["FARMER"],
    "ndvi:read:assigned": ["AGRONOMIST"],
    "ndvi:read:all": ["ADMIN", "FIELD_ANALYST"],
    "ndvi:update": ["ADMIN", "FIELD_ANALYST"],
    "ndvi:delete": ["ADMIN", "FIELD_ANALYST"],
    
    # Weather - FARMER: Own R, AGRONOMIST: Assigned R, FIELD_ANALYST: All R, ADMIN: All R
    "weather:read:own": ["FARMER"],
    "weather:read:assigned": ["AGRONOMIST"],
    "weather:read:all": ["ADMIN", "FIELD_ANALYST"],
    
    # Alerts - FARMER: Own RU, AGRONOMIST: Own RU, FIELD_ANALYST: Own RU, ADMIN: All CRUD
    "alerts:create": ["ADMIN"],
    "alerts:read:own": ["FARMER", "AGRONOMIST", "FIELD_ANALYST"],
    "alerts:read:all": ["ADMIN"],
    "alerts:update:own": ["FARMER", "AGRONOMIST", "FIELD_ANALYST"],
    "alerts:update:all": ["ADMIN"],
    "alerts:delete": ["ADMIN"],
}