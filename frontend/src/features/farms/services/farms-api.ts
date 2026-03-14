/**
 * Farms API Service
 * FarmConnect - AgriManagement
 * 
 * API integration for farm, field, and crop cycle operations
 * Updated to match server-side DTOs from shared_models/farm.py
 */

import api from '../../../app/services/api';

// Type definitions - aligned with server shared_models

/**
 * Farm interface - aligned with server Farm model
 * Server fields: id (UUID), farmer_id, name, location_lat, location_lng, 
 *                location_address, total_area_ha, boundary_geojson, centroid_geojson,
 *                metadata, created_at, updated_at, deleted_at
 */
export interface Farm {
  id: string;
  farmer_id: string;
  name: string;
  location_lat?: number;
  location_lng?: number;
  location_address?: string;
  total_area_hectares?: number; // Note: Server uses total_area_ha, keeping frontend name for compatibility
  boundary_geojson?: any;
  centroid_geojson?: any;
  metadata?: any;
  created_at: string;
  updated_at?: string;
  deleted_at?: string;
}

export interface FarmCreate {
  farmer_id: string;
  name: string;
  location_lat?: number;
  location_lng?: number;
  location_address?: string;
  total_area_hectares?: number;
  boundary_geojson?: any;
  centroid_geojson?: any;
  metadata?: any;
}

export interface FarmUpdate {
  name?: string;
  location_lat?: number;
  location_lng?: number;
  location_address?: string;
  total_area_hectares?: number;
  boundary_geojson?: any;
  centroid_geojson?: any;
  metadata?: any;
}

/**
 * FarmListResponse - aligned with server FarmListResponse
 * Server returns: farms (not items), total, page, page_size, total_pages
 */
export interface FarmListResponse {
  farms: Farm[]; // Server uses 'farms' not 'items'
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * Field interface - aligned with server Field model
 * Server fields: id (UUID), farm_id (UUID), name, area_ha, boundary_geojson,
 *                centroid_geojson, soil_type, soil_classification, elevation_m,
 *                slope_degree, irrigation_type, drainage_type, metadata,
 *                created_at, updated_at, deleted_at
 */
export interface Field {
  id: string;
  farm_id: string;
  name: string;
  area_hectares: number; // Note: Server uses area_ha, keeping frontend name for compatibility
  boundary_geojson?: any;
  centroid_geojson?: any;
  soil_type?: string;
  soil_classification?: string;
  elevation_m?: number;
  slope_degree?: number;
  irrigation_type?: string;
  drainage_type?: string;
  metadata?: any;
  created_at: string;
  updated_at?: string;
}

export interface FieldCreate {
  farm_id: string;
  name: string;
  area_hectares: number;
  boundary_geojson?: any;
  centroid_geojson?: any;
  soil_type?: string;
  soil_classification?: string;
  elevation_m?: number;
  slope_degree?: number;
  irrigation_type?: string;
  drainage_type?: string;
  metadata?: any;
}

export interface FieldUpdate {
  name?: string;
  area_hectares?: number;
  boundary_geojson?: any;
  centroid_geojson?: any;
  soil_type?: string;
  soil_classification?: string;
  elevation_m?: number;
  slope_degree?: number;
  irrigation_type?: string;
  drainage_type?: string;
  metadata?: any;
}

/**
 * CropCycle interface - aligned with server CropCycle model
 * Server fields: id (UUID), field_id (UUID), product_category, crop_name, variety,
 *                cultivar, planting_date, expected_harvest_date, actual_harvest_date,
 *                status, expected_yield_kg, actual_yield_kg, yield_quality_grade,
 *                seed_source, planting_density_per_ha, seed_cost_usd, notes, metadata,
 *                created_at, updated_at, deleted_at
 */
export interface CropCycle {
  id: string;
  field_id: string;
  product_category: string;
  crop_name: string;
  variety?: string;
  cultivar?: string;
  planting_date: string;
  expected_harvest_date?: string;
  actual_harvest_date?: string;
  status: string;
  expected_yield_kg?: number;
  actual_yield_kg?: number;
  yield_quality_grade?: string;
  seed_source?: string;
  planting_density_per_ha?: number;
  seed_cost_usd?: number;
  notes?: string;
  metadata?: any;
  created_at: string;
  updated_at?: string;
}

export interface CropCycleCreate {
  field_id: string;
  product_category: string;
  crop_name: string;
  variety?: string;
  cultivar?: string;
  planting_date: string;
  expected_harvest_date?: string;
}

export interface CropCycleUpdate {
  product_category?: string;
  crop_name?: string;
  variety?: string;
  cultivar?: string;
  planting_date?: string;
  expected_harvest_date?: string;
  actual_harvest_date?: string;
  status?: string;
  expected_yield_kg?: number;
  actual_yield_kg?: number;
  yield_quality_grade?: string;
  seed_source?: string;
  planting_density_per_ha?: number;
  seed_cost_usd?: number;
  notes?: string;
  metadata?: any;
}

/**
 * Farm API endpoints
 */
export const farmsAPI = {
  /**
   * List all farms with pagination
   * Server endpoint: GET /agri/farms
   */
  list: async (params?: { page?: number; page_size?: number; farmer_id?: string }): Promise<FarmListResponse> => {
    const response = await api.get<FarmListResponse>('/agri/farms/', { params });
    return response.data;
  },

  /**
   * Get a single farm by ID
   * Server endpoint: GET /agri/farms/{farm_id}
   */
  get: async (farmId: string): Promise<Farm> => {
    const response = await api.get<Farm>(`/agri/farms/${farmId}/`);
    return response.data;
  },

  /**
   * Create a new farm
   * Server endpoint: POST /agri/farms
   */
  create: async (farmData: FarmCreate): Promise<Farm> => {
    const response = await api.post<Farm>('/agri/farms/', farmData);
    return response.data;
  },

  /**
   * Update an existing farm
   * Server endpoint: PUT /agri/farms/{farm_id}
   */
  update: async (farmId: string, farmData: FarmUpdate): Promise<Farm> => {
    const response = await api.patch<Farm>(`/agri/farms/${farmId}`, farmData);
    return response.data;
  },

  /**
   * Delete a farm (soft delete)
   * Server endpoint: DELETE /agri/farms/{farm_id}
   */
  delete: async (farmId: string): Promise<void> => {
    await api.delete(`/agri/farms/${farmId}`);
  },

  /**
   * Get fields for a specific farm
   * Server endpoint: GET /agri/fields/?farm_id={farm_id}
   */
  getFields: async (farmId: string): Promise<Field[]> => {
    const response = await api.get<Field[]>('/agri/fields/', { params: { farm_id: farmId } });
    return response.data;
  },

  /**
   * Create a new field for a farm
   * Server endpoint: POST /agri/fields
   */
  createField: async (fieldData: FieldCreate): Promise<Field> => {
    const response = await api.post<Field>('/agri/fields/', fieldData);
    return response.data;
  },

  /**
   * Get all fields (global)
   * Server endpoint: GET /agri/fields/
   * Note: Server requires farm_id as required query parameter
   */
  listFields: async (params: { farm_id: string }): Promise<Field[]> => {
    const response = await api.get<Field[]>('/agri/fields/', { params });
    return response.data;
  },

  /**
   * Get a single field by ID
   * Server endpoint: GET /agri/fields/{field_id}
   */
  getField: async (fieldId: string): Promise<Field> => {
    const response = await api.get<Field>(`/agri/fields/${fieldId}/`);
    return response.data;
  },

  /**
   * Update a field
   * Server endpoint: PUT /agri/fields/{field_id}
   */
  updateField: async (fieldId: string, fieldData: FieldUpdate): Promise<Field> => {
    const response = await api.patch<Field>(`/agri/fields/${fieldId}`, fieldData);
    return response.data;
  },

  /**
   * Delete a field
   * Server endpoint: DELETE /agri/fields/{field_id}
   */
  deleteField: async (fieldId: string): Promise<void> => {
    await api.delete(`/agri/fields/${fieldId}`);
  },

  /**
   * Get crop cycles for a field
   * Server endpoint: GET /agri/fields/{field_id}/crop-cycles/
   */
  getCropCycles: async (fieldId: string): Promise<CropCycle[]> => {
    const response = await api.get<CropCycle[]>(`/agri/fields/${fieldId}/crop-cycles/`);
    return response.data;
  },

  /**
   * Get all crop cycles (global)
   * Server endpoint: GET /agri/crop-cycles/
   */
  listCropCycles: async (params?: { field_id?: string; status?: string }): Promise<CropCycle[]> => {
    const response = await api.get<CropCycle[]>('/agri/crop-cycles/', { params });
    return response.data;
  },

  /**
   * Get a single crop cycle by ID
   * Server endpoint: GET /agri/crop-cycles/{cycle_id}
   */
  getCropCycle: async (cycleId: string): Promise<CropCycle> => {
    const response = await api.get<CropCycle>(`/agri/crop-cycles/${cycleId}/`);
    return response.data;
  },

  /**
   * Create a new crop cycle
   * Server endpoint: POST /agri/crop-cycles/
   */
  createCropCycle: async (cycleData: CropCycleCreate): Promise<CropCycle> => {
    const response = await api.post<CropCycle>('/agri/crop-cycles/', cycleData);
    return response.data;
  },

  /**
   * Update a crop cycle
   * Server endpoint: PUT /agri/crop-cycles/{cycle_id}
   */
  updateCropCycle: async (cycleId: string, cycleData: CropCycleUpdate): Promise<CropCycle> => {
    const response = await api.patch<CropCycle>(`/agri/crop-cycles/${cycleId}`, cycleData);
    return response.data;
  },

  /**
   * Delete a crop cycle
   * Server endpoint: DELETE /agri/crop-cycles/{cycle_id}
   */
  deleteCropCycle: async (cycleId: string): Promise<void> => {
    await api.delete(`/agri/crop-cycles/${cycleId}`);
  },

  /**
   * Get harvest statistics for dashboard
   * Server endpoint: GET /agri/harvests/statistics
   */
  getHarvestStatistics: async (farmerId?: string): Promise<{
    total_harvests: number;
    pending_harvests: number;
    completed_harvests: number;
    total_quantity_kg: number;
    by_status: Record<string, number>;
  }> => {
    const params = farmerId ? { farmer_id: farmerId } : {};
    const response = await api.get('/agri/harvests/statistics', { params });
    return response.data;
  },

  /**
   * Get farmer earnings
   * Server endpoint: GET /accounting/farmer/earnings
   */
  getFarmerEarnings: async (farmerId?: string): Promise<{
    total_earnings: number;
    pending_payments: number;
    completed_payments: number;
    recent_transactions: Array<{
      date: string;
      amount: number;
      description: string;
    }>;
  }> => {
    const params = farmerId ? { farmer_id: farmerId } : {};
    const response = await api.get('/accounting/farmer/earnings', { params });
    return response.data;
  },
};

export default farmsAPI;
