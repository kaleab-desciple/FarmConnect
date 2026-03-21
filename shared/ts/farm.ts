// FarmConnect Farm, Field, and Crop Cycle Types - Mirroring Python DTOs from shared_models
import { CropCycleStatus } from "./enums";

/**
 * GeoJSON point for coordinates
 */
export interface GeoJSONPoint {
  type: "Point";
  coordinates: [number, number]; // [longitude, latitude]
}

/**
 * GeoJSON polygon for boundaries
 */
export interface GeoJSONPolygon {
  type: "Polygon";
  coordinates: number[][][]; // Array of rings, first ring is exterior
}

/**
 * Base farm model
 */
export interface FarmBase {
  farmer_id: string;
  name: string;
  location_lat: number; // Decimal in Python, number in TS
  location_lng: number;
  location_address?: string;
  total_area_ha?: number;
  boundary_geojson?: GeoJSONPolygon;
  centroid_geojson?: GeoJSONPoint;
  metadata?: Record<string, unknown>;
}

/**
 * Farm response model
 */
export interface Farm extends FarmBase {
  id: string;
  created_at: string; // ISO datetime
  updated_at: string;
  deleted_at?: string;
}

/**
 * Farm creation request
 */
export interface FarmCreate extends FarmBase {}

/**
 * Farm update request - all fields optional for partial updates
 */
export interface FarmUpdate {
  farmer_id?: string;
  name?: string;
  location_lat?: number;
  location_lng?: number;
  location_address?: string;
  total_area_ha?: number;
  boundary_geojson?: GeoJSONPolygon;
  centroid_geojson?: GeoJSONPoint;
  metadata?: Record<string, unknown>;
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

// ============ Field Types ============

/**
 * Base field model
 */
export interface FieldBase {
  farm_id: string;
  name: string;
  area_ha: number;
  boundary_geojson: GeoJSONPolygon;
  centroid_geojson?: GeoJSONPoint;
  soil_type?: string;
  soil_classification?: string;
  elevation_m?: number;
  slope_degree?: number;
  irrigation_type?: string;
  drainage_type?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Field response model
 */
export interface Field extends FieldBase {
  id: string;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

/**
 * Field creation request
 */
export interface FieldCreate extends FieldBase {}

/**
 * Field update request - all fields optional for partial updates
 */
export interface FieldUpdate {
  farm_id?: string;
  name?: string;
  area_ha?: number;
  boundary_geojson?: GeoJSONPolygon;
  centroid_geojson?: GeoJSONPoint;
  soil_type?: string;
  soil_classification?: string;
  elevation_m?: number;
  slope_degree?: number;
  irrigation_type?: string;
  drainage_type?: string;
  metadata?: Record<string, unknown>;
}

// ============ Crop Cycle Types ============

/**
 * Base crop cycle model
 */
export interface CropCycleBase {
  field_id: string;
  product_category: string;
  crop_name: string;
  variety?: string;
  cultivar?: string;
  planting_date: string; // date string (YYYY-MM-DD)
  expected_harvest_date?: string;
  actual_harvest_date?: string;
  status: CropCycleStatus;
  expected_yield_kg?: number;
  actual_yield_kg?: number;
  yield_quality_grade?: string;
  seed_source?: string;
  planting_density_per_ha?: number;
  seed_cost_usd?: number;
  notes?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Crop cycle response model
 */
export interface CropCycle extends CropCycleBase {
  id: string;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

/**
 * Crop cycle creation request
 */
export interface CropCycleCreate extends CropCycleBase {}

/**
 * Crop cycle update request - all fields optional for partial updates
 */
export interface CropCycleUpdate {
  field_id?: string;
  product_category?: string;
  crop_name?: string;
  variety?: string;
  cultivar?: string;
  planting_date?: string;
  expected_harvest_date?: string;
  actual_harvest_date?: string;
  status?: CropCycleStatus;
  expected_yield_kg?: number;
  actual_yield_kg?: number;
  yield_quality_grade?: string;
  seed_source?: string;
  planting_density_per_ha?: number;
  seed_cost_usd?: number;
  notes?: string;
  metadata?: Record<string, unknown>;
}

// ============ Field Status Map Types ============

/**
 * Active crop cycle info for field status map
 */
export interface FieldStatusMapCropCycle {
  id: string;
  crop_name: string;
  status: CropCycleStatus;
  planting_date?: string;
  expected_harvest_date?: string;
  expected_yield_kg?: number;
  variety?: string;
}

/**
 * Field status for map visualization
 */
export interface FieldStatusMapField {
  field_id: string;
  field_name: string;
  area_ha: number;
  boundary_geojson: GeoJSONPolygon;
  centroid_geojson?: GeoJSONPoint;
  irrigation_type?: string;
  soil_type?: string;
  active_crop_cycle?: FieldStatusMapCropCycle;
}

/**
 * Farm field status map response
 */
export interface FieldStatusMapResponse {
  farm_id: string;
  farm_name: string;
  fields: FieldStatusMapField[];
}
