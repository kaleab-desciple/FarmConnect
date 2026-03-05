"""
API Permission Matrix and Constants.
Maps permissions to the roles that are allowed to perform them.

Roles describe WHO you are.
Permissions describe WHAT you can do.
"""

# Realm Roles (Human Users)
REALM_ROLES = ["ADMIN", "MODERATOR", "MANAGER", "AGENT", "FARMER", "MERCHANT", "DELIVERY", "AGRONOMIST", "FIELD_ANALYST"]

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
    "users:approve": ["ADMIN", "MANAGER"],
    "users:reputation": ["ADMIN", "MANAGER", "AGENT"],
    
    # Products Domain
    "products:create": ["ADMIN", "FARMER", "AGENT"],
    "products:update": ["ADMIN", "FARMER", "AGENT"],
    "products:read": ["ADMIN", "MANAGER", "AGENT", "FARMER", "MERCHANT", "DELIVERY"],
    "products:delete": ["ADMIN"],
    
    # Orders Domain
    "orders:create": ["ADMIN", "FARMER", "MERCHANT"],
    "orders:read": ["ADMIN", "MANAGER", "AGENT", "FARMER", "MERCHANT", "DELIVERY"],
    "orders:update": ["ADMIN", "MANAGER", "FARMER", "MERCHANT", "DELIVERY", "AGENT"],
    "orders:cancel": ["ADMIN", "MANAGER", "FARMER", "MERCHANT", "AGENT"],
    
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
    "disputes:resolve": ["ADMIN", "MANAGER", "MODERATOR"],
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
    # Farms 
    "farms:create": ["ADMIN", "FARMER", "AGENT"],
    "farms:read": ["ADMIN", "MANAGER", "AGENT", "FARMER", "AGRONOMIST", "FIELD_ANALYST"],
    "farms:update": ["ADMIN", "FARMER", "AGENT"],
    "farms:delete": ["ADMIN", "FARMER"],
    
    # Fields 
    "fields:create": ["ADMIN", "FARMER", "AGENT"],
    "fields:read": ["ADMIN", "MANAGER", "AGENT", "FARMER", "AGRONOMIST", "FIELD_ANALYST"],
    "fields:update": ["ADMIN", "FARMER", "AGENT"],
    "fields:delete": ["ADMIN", "FARMER"],
    
    # Crop Cycles
    "crop_cycles:create": ["ADMIN", "FARMER", "AGENT"],
    "crop_cycles:read": ["ADMIN", "MANAGER", "AGENT", "FARMER", "AGRONOMIST", "FIELD_ANALYST"],
    "crop_cycles:update": ["ADMIN", "FARMER", "AGRONOMIST", "AGENT"],
    "crop_cycles:delete": ["ADMIN", "FARMER"],
    
    # Harvests Domain
    "harvests:create": ["ADMIN", "FARMER", "AGENT"],
    "harvests:read": ["ADMIN", "MANAGER", "AGENT", "FARMER", "AGRONOMIST", "FIELD_ANALYST"],
    "harvests:update": ["ADMIN", "FARMER", "AGENT"],
    "harvests:delete": ["ADMIN"],
    
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
    
    # Advisory/Forums Domain
    "forums:create": ["ADMIN", "FARMER", "MERCHANT", "AGRONOMIST"],
    "forums:read": ["ADMIN", "FARMER", "MERCHANT", "AGRONOMIST", "MANAGER"],
    "forums:comment:create": ["ADMIN", "FARMER", "MERCHANT", "AGRONOMIST", "MANAGER"],
    "forums:comment:accept": ["ADMIN", "FARMER", "MERCHANT", "AGRONOMIST", "MANAGER"],
    "forums:vote": ["ADMIN", "FARMER", "MERCHANT", "AGRONOMIST", "MANAGER"],
    "forums:bookmark": ["ADMIN", "FARMER", "MERCHANT", "AGRONOMIST", "MANAGER"],
    "forums:moderate": ["ADMIN", "MODERATOR"],
    "forums:admin": ["ADMIN"],
    
    # Knowledge Base Domain
    "knowledge:read": ["ADMIN", "FARMER", "MERCHANT", "AGRONOMIST", "MANAGER", "FIELD_ANALYST"],
    "knowledge:create": ["ADMIN", "AGRONOMIST"],
    "knowledge:publish": ["ADMIN", "AGRONOMIST"],

    # Delivery Domain
    "delivery:assign": ["ADMIN", "MANAGER"],
    "delivery:update": ["DELIVERY"],
    "delivery:read": ["ADMIN", "MANAGER", "AGENT", "DELIVERY"]
}
