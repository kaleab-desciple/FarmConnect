/**
 * Centralized route definitions for the application.
 */
export const ROUTES = {
  // Auth
  LOGIN: '/login',
  REGISTER: '/register',
  
  // Farmer Role
  FARMER_DASHBOARD: '/farmer/dashboard',
  FARMER_FARMS: '/farmer/farms',
  FARMER_FARM_SETTINGS: '/farmer/farms/:farmId/settings',
  FARMER_FIELDS: '/farmer/fields',
  FARMER_FIELD_DETAIL: '/farmer/fields/:id',
  FARMER_HARVEST_NEW: '/farmer/harvest/new',
  FARMER_INVENTORY: '/farmer/inventory',
  FARMER_ORDERS: '/farmer/orders',
  FARMER_AI_DIAGNOSIS: '/farmer/ai-diagnostics',
  FARMER_LOGS_NEW: '/farmer/logs/new',
  
  // Merchant Role
  MERCHANT_DASHBOARD: '/merchant/dashboard',
  MERCHANT_MARKETPLACE: '/merchant/marketplace',
  MERCHANT_ORDERS: '/merchant/orders',
  
  // Delivery Role
  DELIVERY_DASHBOARD: '/delivery/dashboard',
  DELIVERY_AVAILABLE: '/delivery/available',
  DELIVERY_ACTIVE: '/delivery/active/:id',
  
  // Common
  PROFILE: '/profile',
  SETTINGS: '/settings',
};
