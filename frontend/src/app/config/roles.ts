/**
 * User Role Definitions
 * FarmConnect AgriManagement Platform
 */

// Role enumeration matching backend
export enum UserRole {
  FARMER = 'FARMER',
  MERCHANT = 'MERCHANT',
  DELIVERY = 'DELIVERY',
  AGENT = 'AGENT',
  MANAGER = 'MANAGER',
  ADMIN = 'ADMIN',
  MODERATOR = 'MODERATOR',
  AGRONOMIST = 'AGRONOMIST',
  FIELD_ANALYST = 'FIELD_ANALYST',
}

// Role metadata for display
export interface RoleMetadata {
  id: UserRole;
  name: string;
  description: string;
  icon: string;
  color: string;
}

export const ROLE_METADATA: Record<UserRole, RoleMetadata> = {
  [UserRole.FARMER]: {
    id: UserRole.FARMER,
    name: 'Farmer',
    description: 'Manage farms, fields, crops, and harvests',
    icon: 'Sprout',
    color: 'green',
  },
  [UserRole.MERCHANT]: {
    id: UserRole.MERCHANT,
    name: 'Merchant',
    description: 'Buy agricultural products from farmers',
    icon: 'Store',
    color: 'blue',
  },
  [UserRole.DELIVERY]: {
    id: UserRole.DELIVERY,
    name: 'Delivery',
    description: 'Deliver products from farmers to merchants',
    icon: 'Truck',
    color: 'purple',
  },
  [UserRole.AGENT]: {
    id: UserRole.AGENT,
    name: 'Agent',
    description: 'Support farmers and merchants with disputes',
    icon: 'Headphones',
    color: 'orange',
  },
  [UserRole.MANAGER]: {
    id: UserRole.MANAGER,
    name: 'Manager',
    description: 'Manage regional operations and teams',
    icon: 'Briefcase',
    color: 'indigo',
  },
  [UserRole.ADMIN]: {
    id: UserRole.ADMIN,
    name: 'Admin',
    description: 'Full platform administration access',
    icon: 'Shield',
    color: 'red',
  },
  [UserRole.MODERATOR]: {
    id: UserRole.MODERATOR,
    name: 'Moderator',
    description: 'Review content and manage disputes',
    icon: 'Eye',
    color: 'yellow',
  },
  [UserRole.AGRONOMIST]: {
    id: UserRole.AGRONOMIST,
    name: 'Agronomist',
    description: 'Provide expert agricultural advice',
    icon: 'Leaf',
    color: 'emerald',
  },
  [UserRole.FIELD_ANALYST]: {
    id: UserRole.FIELD_ANALYST,
    name: 'Field Analyst',
    description: 'Collect and analyze field data',
    icon: 'MapPin',
    color: 'teal',
  },
};

// Role hierarchy for permission inheritance
export const ROLE_HIERARCHY: Record<UserRole, UserRole[]> = {
  [UserRole.ADMIN]: [
    UserRole.ADMIN,
    UserRole.MANAGER,
    UserRole.MODERATOR,
  ],
  [UserRole.MANAGER]: [
    UserRole.MANAGER,
    UserRole.AGRONOMIST,
    UserRole.AGENT,
  ],
  [UserRole.MODERATOR]: [
    UserRole.MODERATOR,
    UserRole.AGENT,
  ],
  [UserRole.AGRONOMIST]: [
    UserRole.AGRONOMIST,
    UserRole.FIELD_ANALYST,
  ],
  [UserRole.FARMER]: [UserRole.FARMER],
  [UserRole.MERCHANT]: [UserRole.MERCHANT],
  [UserRole.DELIVERY]: [UserRole.DELIVERY],
  [UserRole.AGENT]: [UserRole.AGENT],
  [UserRole.FIELD_ANALYST]: [UserRole.FIELD_ANALYST],
};

// Permission definitions
export const PERMISSIONS = {
  // Farm permissions
  'farm:create': [UserRole.FARMER],
  'farm:read:own': [UserRole.FARMER],
  'farm:read:all': [UserRole.ADMIN, UserRole.MANAGER, UserRole.AGRONOMIST],
  'farm:update:own': [UserRole.FARMER],
  'farm:delete': [UserRole.FARMER, UserRole.ADMIN],
  
  // Field permissions
  'field:create': [UserRole.FARMER],
  'field:read:own': [UserRole.FARMER],
  'field:read:all': [UserRole.ADMIN, UserRole.MANAGER, UserRole.AGRONOMIST, UserRole.FIELD_ANALYST],
  'field:update:own': [UserRole.FARMER],
  'field:delete': [UserRole.FARMER],
  
  // Crop permissions
  'crop:create': [UserRole.FARMER],
  'crop:read:own': [UserRole.FARMER],
  'crop:read:all': [UserRole.ADMIN, UserRole.MANAGER, UserRole.AGRONOMIST],
  'crop:update': [UserRole.FARMER],
  'crop:stage:transition': [UserRole.FARMER],
  
  // Harvest permissions
  'harvest:create': [UserRole.FARMER],
  'harvest:read:own': [UserRole.FARMER],
  'harvest:read:all': [UserRole.ADMIN, UserRole.MANAGER],
  'harvest:update': [UserRole.FARMER],
  'harvest:yield:record': [UserRole.FARMER],
  
  // Product permissions
  'product:create': [UserRole.FARMER],
  'product:read': [UserRole.MERCHANT, UserRole.FARMER],
  'product:update:own': [UserRole.FARMER],
  'product:delete:own': [UserRole.FARMER],
  'product:qc:review': [UserRole.ADMIN, UserRole.AGENT],
  
  // Order permissions
  'order:create': [UserRole.MERCHANT],
  'order:read:own': [UserRole.MERCHANT, UserRole.FARMER],
  'order:manage': [UserRole.ADMIN, UserRole.AGENT],
  'order:fulfill': [UserRole.FARMER],
  'order:cancel': [UserRole.MERCHANT, UserRole.FARMER, UserRole.ADMIN],
  
  // Delivery permissions
  'delivery:accept': [UserRole.DELIVERY],
  'delivery:read:own': [UserRole.DELIVERY],
  'delivery:track': [UserRole.MERCHANT, UserRole.FARMER],
  'delivery:complete': [UserRole.DELIVERY],
  'delivery:assign': [UserRole.ADMIN, UserRole.AGENT],
  
  // AI Diagnosis permissions
  'diagnosis:create': [UserRole.FARMER, UserRole.AGRONOMIST],
  'diagnosis:read:own': [UserRole.FARMER, UserRole.AGRONOMIST],
  'diagnosis:review': [UserRole.AGRONOMIST],
  'diagnosis:escalate': [UserRole.FARMER],
  
  // Weather permissions
  'weather:read': [UserRole.FARMER, UserRole.MERCHANT, UserRole.AGRONOMIST],
  'weather:alerts': [UserRole.FARMER, UserRole.MERCHANT],
  
  // Monitoring permissions
  'monitoring:read:own': [UserRole.FARMER],
  'monitoring:read:all': [UserRole.ADMIN, UserRole.MANAGER, UserRole.AGRONOMIST, UserRole.FIELD_ANALYST],
  'monitoring:observation:create': [UserRole.FARMER, UserRole.FIELD_ANALYST],
  'monitoring:ndvi:read': [UserRole.FARMER, UserRole.AGRONOMIST],
  
  // Dispute permissions
  'dispute:create': [UserRole.MERCHANT, UserRole.FARMER],
  'dispute:read:own': [UserRole.MERCHANT, UserRole.FARMER],
  'dispute:read:all': [UserRole.ADMIN, UserRole.MODERATOR, UserRole.AGENT],
  'dispute:resolve': [UserRole.ADMIN, UserRole.MODERATOR, UserRole.AGENT],
  'dispute:mediate': [UserRole.AGENT],
  
  // User permissions
  'user:create': [UserRole.ADMIN],
  'user:read': [UserRole.ADMIN, UserRole.MANAGER],
  'user:update': [UserRole.ADMIN, UserRole.MANAGER],
  'user:delete': [UserRole.ADMIN],
  'user:role:assign': [UserRole.ADMIN],
  
  // Reports permissions
  'reports:read:own': [UserRole.FARMER, UserRole.MERCHANT],
  'reports:read:region': [UserRole.MANAGER, UserRole.AGRONOMIST],
  'reports:read:all': [UserRole.ADMIN],
  'reports:generate': [UserRole.ADMIN, UserRole.MANAGER],
  
  // Accounting permissions
  'accounting:read:own': [UserRole.FARMER, UserRole.MERCHANT],
  'accounting:read:all': [UserRole.ADMIN],
  'accounting:escrow:manage': [UserRole.ADMIN],
  
  // Settings permissions
  'settings:read': [UserRole.ADMIN, UserRole.MANAGER],
  'settings:update': [UserRole.ADMIN],
} as const;

export type Permission = keyof typeof PERMISSIONS;

/**
 * Check if a role has a specific permission
 */
export function hasPermission(role: UserRole, permission: Permission): boolean {
  const allowedRoles = PERMISSIONS[permission] as readonly UserRole[];
  return allowedRoles.includes(role);
}

/**
 * Get all permissions for a role (including inherited from hierarchy)
 */
export function getPermissionsForRole(role: UserRole): Permission[] {
  const permissions: Permission[] = [];
  
  // Get roles in hierarchy
  const roles = ROLE_HIERARCHY[role] || [role];
  
  // Collect all permissions
  for (const perm in PERMISSIONS) {
    const allowedRoles = PERMISSIONS[perm as Permission] as readonly UserRole[];
    if (roles.some((r) => allowedRoles.includes(r))) {
      permissions.push(perm as Permission);
    }
  }
  
  return permissions;
}

/**
 * Get role display name
 */
export function getRoleName(role: UserRole): string {
  return ROLE_METADATA[role]?.name || role;
}

/**
 * Get role color
 */
export function getRoleColor(role: UserRole): string {
  return ROLE_METADATA[role]?.color || 'gray';
}
