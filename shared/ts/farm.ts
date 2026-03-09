/**
 * Farm TypeScript Types
 * Farm Connect AgriManagement
 * 
 * TypeScript interfaces mirroring Python Pydantic models from shared_models/farm.py
 * Designed for React TypeScript frontend integration
 */

// ============================================================================
// Enums
// ============================================================================

/**
 * Crop cycle status values
 */
export enum CropCycleStatus {
  PLANNED = "PLANNED",
  PLANTED = "PLANTED",
  GROWING = "GROWING",
  HARVESTED = "HARVESTED",
  PARTIALLY_HARVESTED = "PARTIALLY_HARVESTED",
  FAILED = "FAILED",
  ABANDONED = "ABANDONED",
}

/**
 * Task status values
 */
export enum TaskStatus {
  PENDING = "PENDING",
  SCHEDULED = "SCHEDULED",
  IN_PROGRESS = "IN_PROGRESS",
  COMPLETED = "COMPLETED",
  SKIPPED = "SKIPPED",
  CANCELLED = "CANCELLED",
  OVERDUE = "OVERDUE",
}

/**
 * Task priority values
 */
export enum TaskPriority {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  URGENT = "URGENT",
}

/**
 * Task type values
 */
export enum TaskType {
  LAND_PREPARATION = "LAND_PREPARATION",
  SOWING = "SOWING",
  PLANTING = "PLANTING",
  IRRIGATION = "IRRIGATION",
  FERTILIZATION = "FERTILIZATION",
  WEEDING = "WEEDING",
  PEST_CONTROL = "PEST_CONTROL",
  DISEASE_CONTROL = "DISEASE_CONTROL",
  PRUNING = "PRUNING",
  THINNING = "THINNING",
  HARVESTING = "HARVESTING",
  POST_HARVEST = "POST_HARVEST",
  INSPECTION = "INSPECTION",
  MAINTENANCE = "MAINTENANCE",
  OTHER = "OTHER",
}

// ============================================================================
// GeoJSON Types
// ============================================================================

/**
 * GeoJSON Point geometry
 */
export interface GeoJSONPoint {
  type: "Point";
  coordinates: [number, number]; // [longitude, latitude]
}

/**
 * GeoJSON Polygon geometry
 */
export interface GeoJSONPolygon {
  type: "Polygon";
  coordinates: number[][][]; // Array of linear rings, first is exterior
}

/**
 * GeoJSON MultiPolygon geometry
 */
export interface GeoJSONMultiPolygon {
  type: "MultiPolygon";
  coordinates: number[][][][];
}

/**
 * GeoJSON Feature
 */
export interface GeoJSONFeature {
  type: "Feature";
  geometry: GeoJSONPoint | GeoJSONPolygon | GeoJSONMultiPolygon;
  properties: Record<string, unknown>;
}

/**
 * GeoJSON FeatureCollection
 */
export interface GeoJSONFeatureCollection {
  type: "FeatureCollection";
  features: GeoJSONFeature[];
}

// Union type for all GeoJSON geometry types
export type GeoJSONGeometry = GeoJSONPoint | GeoJSONPolygon | GeoJSONMultiPolygon;

// ============================================================================
// Farm Types
// ============================================================================

/**
 * Base Farm model - common fields for create and response
 */
export interface FarmBase {
  farmer_id: string;
  name: string;
  location_lat: string; // Decimal serialized as string
  location_lng: string; // Decimal serialized as string
  location_address?: string;
  total_area_ha?: string; // Decimal serialized as string
  boundary_geojson?: GeoJSONGeometry | GeoJSONFeature | GeoJSONFeatureCollection;
  centroid_geojson?: GeoJSONPoint;
  metadata?: Record<string, unknown>;
}

/**
 * Farm creation model - used when creating a new farm
 */
export interface FarmCreate extends FarmBase {}

/**
 * Farm update model - all fields optional for partial updates
 */
export interface FarmUpdate {
  name?: string;
  location_lat?: string;
  location_lng?: string;
  location_address?: string;
  total_area_ha?: string;
  boundary_geojson?: GeoJSONGeometry | GeoJSONFeature | GeoJSONFeatureCollection;
  centroid_geojson?: GeoJSONPoint;
  metadata?: Record<string, unknown>;
}

/**
 * Farm response model - complete farm with system fields
 */
export interface Farm extends FarmBase {
  id: string; // UUID serialized as string
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
  deleted_at?: string; // ISO 8601 datetime, null if not deleted
}

/**
 * Paginated farm list response
 */
export interface FarmListResponse {
  farms: Farm[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ============================================================================
// Field Types
// ============================================================================

/**
 * Base Field model - common fields for create and response
 */
export interface FieldBase {
  farm_id: string; // UUID serialized as string
  name: string;
  area_ha: string; // Decimal serialized as string
  boundary_geojson: GeoJSONGeometry | GeoJSONFeature | GeoJSONFeatureCollection;
  centroid_geojson?: GeoJSONPoint;
  soil_type?: string;
  soil_classification?: string;
  elevation_m?: string; // Decimal serialized as string
  slope_degree?: string; // Decimal serialized as string
  irrigation_type?: string;
  drainage_type?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Field creation model
 */
export interface FieldCreate extends FieldBase {}

/**
 * Field update model - all fields optional
 */
export interface FieldUpdate {
  name?: string;
  area_ha?: string;
  boundary_geojson?: GeoJSONGeometry | GeoJSONFeature | GeoJSONFeatureCollection;
  centroid_geojson?: GeoJSONPoint;
  soil_type?: string;
  soil_classification?: string;
  elevation_m?: string;
  slope_degree?: string;
  irrigation_type?: string;
  drainage_type?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Field response model - complete field with system fields
 */
export interface Field extends FieldBase {
  id: string; // UUID serialized as string
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
  deleted_at?: string; // ISO 8601 datetime, null if not deleted
}

// ============================================================================
// Crop Cycle Types
// ============================================================================

/**
 * Base CropCycle model - common fields for create and response
 */
export interface CropCycleBase {
  field_id: string; // UUID serialized as string
  product_category: string;
  crop_name: string;
  variety?: string;
  cultivar?: string;
  planting_date: string; // ISO 8601 date (YYYY-MM-DD)
  expected_harvest_date?: string; // ISO 8601 date
  actual_harvest_date?: string; // ISO 8601 date
  status: CropCycleStatus | string;
  expected_yield_kg?: string; // Decimal serialized as string
  actual_yield_kg?: string; // Decimal serialized as string
  yield_quality_grade?: string;
  seed_source?: string;
  planting_density_per_ha?: number;
  seed_cost_usd?: string; // Decimal serialized as string
  notes?: string;
  metadata?: Record<string, unknown>;
}

/**
 * CropCycle creation model
 */
export interface CropCycleCreate extends CropCycleBase {}

/**
 * CropCycle update model - all fields optional
 */
export interface CropCycleUpdate {
  product_category?: string;
  crop_name?: string;
  variety?: string;
  cultivar?: string;
  planting_date?: string;
  expected_harvest_date?: string;
  actual_harvest_date?: string;
  status?: CropCycleStatus | string;
  expected_yield_kg?: string;
  actual_yield_kg?: string;
  yield_quality_grade?: string;
  seed_source?: string;
  planting_density_per_ha?: number;
  seed_cost_usd?: string;
  notes?: string;
  metadata?: Record<string, unknown>;
}

/**
 * CropCycle response model
 */
export interface CropCycle extends CropCycleBase {
  id: string; // UUID serialized as string
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
  deleted_at?: string; // ISO 8601 datetime, null if not deleted
}

// ============================================================================
// Farm Task Types (for future use - from service.py constants)
// ============================================================================

/**
 * Farm task model
 */
export interface FarmTask {
  id: string;
  field_id: string;
  crop_cycle_id?: string;
  task_type: TaskType | string;
  title: string;
  description?: string;
  status: TaskStatus | string;
  priority: TaskPriority | string;
  scheduled_date?: string; // ISO 8601 date
  scheduled_time?: string; // HH:MM:SS
  duration_estimate_hours?: number;
  window_start_date?: string;
  window_end_date?: string;
  completed_date?: string;
  completed_time?: string;
  completed_by?: string;
  duration_actual_hours?: number;
  assigned_to?: string;
  labor_count?: number;
  equipment_needed?: string[];
  materials_needed?: string[];
  estimated_cost_usd?: string;
  actual_cost_usd?: string;
  parent_task_id?: string;
  depends_on_tasks?: string[];
  weather_dependent?: boolean;
  soil_moisture_condition?: string;
  auto_generated?: boolean;
  generation_reason?: string;
  notes?: string;
  completion_notes?: string;
  completion_photos?: string[];
  metadata?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

// ============================================================================
// Farm User / Owner Types
// ============================================================================

/**
 * Farm owner/manager information
 */
export interface FarmUser {
  id: string;
  name?: string;
  email?: string;
  phone?: string;
  role?: string;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

/**
 * Error response
 */
export interface ApiError {
  detail: string;
  code?: string;
  errors?: Record<string, string[]>;
}

/**
 * Pagination params for list endpoints
 */
export interface PaginationParams {
  page?: number;
  page_size?: number;
}

/**
 * Sort params
 */
export interface SortParams {
  sort_by?: string;
  order?: "asc" | "desc";
}

// ============================================================================
// Serialized JSON Representations (for API request/response)
// ============================================================================

/**
 * Farm as JSON - all UUIDs and Decimals converted to strings
 */
export type FarmJSON = Farm;

/**
 * Field as JSON
 */
export type FieldJSON = Field;

/**
 * CropCycle as JSON
 */
export type CropCycleJSON = CropCycle;

/**
 * Farm list as JSON
 */
export type FarmListJSON = FarmListResponse;

// ============================================================================
// Type Guards / Helpers
// ============================================================================

/**
 * Check if string is a valid UUID
 */
export function isValidUUID(value: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(value);
}

/**
 * Check if string is a valid ISO date (YYYY-MM-DD)
 */
export function isValidISODate(value: string): boolean {
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
  return dateRegex.test(value);
}

/**
 * Check if string is a valid ISO datetime
 */
export function isValidISODateTime(value: string): boolean {
  const dateTimeRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$/;
  return dateTimeRegex.test(value);
}

/**
 * Parse Decimal string to number (use for calculations only, not storage)
 */
export function parseDecimal(value: string | number | undefined): number | undefined {
  if (value === undefined || value === null) return undefined;
  if (typeof value === "number") return value;
  return parseFloat(value);
}

/**
 * Format number to Decimal string (for API requests)
 */
export function formatDecimal(value: number | string | undefined): string | undefined {
  if (value === undefined || value === null) return undefined;
  if (typeof value === "string") return value;
  return value.toString();
}

/**
 * Format Date to ISO string (YYYY-MM-DD)
 */
export function formatDate(date: Date | string | undefined): string | undefined {
  if (date === undefined || date === null) return undefined;
  if (typeof date === "string") return date.split("T")[0];
  return date.toISOString().split("T")[0];
}

/**
 * Format DateTime to ISO string
 */
export function formatDateTime(date: Date | string | undefined): string | undefined {
  if (date === undefined || date === null) return undefined;
  if (typeof date === "string") return date;
  return date.toISOString();
}

// ============================================================================
// Default Values
// ============================================================================

/**
 * Default crop cycle status
 */
export const DEFAULT_CROP_CYCLE_STATUS = CropCycleStatus.PLANNED;

/**
 * Default task status
 */
export const DEFAULT_TASK_STATUS = TaskStatus.PENDING;

/**
 * Default task priority
 */
export const DEFAULT_TASK_PRIORITY = TaskPriority.MEDIUM;

// ============================================================================
// API Endpoint Types (for frontend routing)
// ============================================================================

/**
 * Farm API endpoints
 */
export const FarmApiEndpoints = {
  /** Create a new farm */
  create: "/api/v1/agri/farms",
  /** Get all farms (paginated) */
  list: "/api/v1/agri/farms",
  /** Get a specific farm by ID */
  get: (farmId: string) => `/api/v1/agri/farms/${farmId}`,
  /** Update a farm */
  update: (farmId: string) => `/api/v1/agri/farms/${farmId}`,
  /** Delete a farm */
  delete: (farmId: string) => `/api/v1/agri/farms/${farmId}`,
} as const;

/**
 * Field API endpoints
 */
export const FieldApiEndpoints = {
  /** Create a new field */
  create: "/api/v1/agri/fields",
  /** Get fields for a farm */
  list: (farmId: string) => `/api/v1/agri/farms/${farmId}/fields`,
  /** Get a specific field by ID */
  get: (fieldId: string) => `/api/v1/agri/fields/${fieldId}`,
  /** Update a field */
  update: (fieldId: string) => `/api/v1/agri/fields/${fieldId}`,
  /** Delete a field */
  delete: (fieldId: string) => `/api/v1/agri/fields/${fieldId}`,
} as const;

/**
 * CropCycle API endpoints
 */
export const CropCycleApiEndpoints = {
  /** Create a new crop cycle */
  create: "/api/v1/agri/crop-cycles",
  /** Get crop cycles for a field */
  listByField: (fieldId: string) => `/api/v1/agri/fields/${fieldId}/crop-cycles`,
  /** Get all crop cycles */
  list: "/api/v1/agri/crop-cycles",
  /** Get a specific crop cycle by ID */
  get: (cycleId: string) => `/api/v1/agri/crop-cycles/${cycleId}`,
  /** Update a crop cycle */
  update: (cycleId: string) => `/api/v1/agri/crop-cycles/${cycleId}`,
  /** Delete a crop cycle */
  delete: (cycleId: string) => `/api/v1/agri/crop-cycles/${cycleId}`,
} as const;
