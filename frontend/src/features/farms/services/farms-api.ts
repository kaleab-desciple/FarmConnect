/**
 * Farms API Service
 * FarmConnect - AgriManagement
 * 
 * API integration for farm, field, and crop cycle operations
 */

import api from '../../../app/services/api';

// Type definitions
export interface Farm {
  id: string;
  name: string;
  location?: string;
  total_area_hectares?: number;
  farmer_id: string;
  created_at: string;
  updated_at?: string;
}

export interface FarmCreate {
  name: string;
  location?: string;
  total_area_hectares?: number;
}

export interface FarmUpdate {
  name?: string;
  location?: string;
  total_area_hectares?: number;
}

export interface FarmListResponse {
  items: Farm[];
  total: number;
  page: number;
  page_size: number;
}

export interface Field {
  id: string;
  name: string;
  farm_id: string;
  area_hectares: number;
  soil_type?: string;
  location?: any;
  geometry?: any;
  created_at: string;
}

export interface FieldCreate {
  name: string;
  farm_id: string;
  area_hectares: number;
  soil_type?: string;
  location?: any;
  geometry?: any;
}

export interface FieldUpdate {
  name?: string;
  area_hectares?: number;
  soil_type?: string;
  location?: any;
  geometry?: any;
}

export interface CropCycle {
  id: string;
  field_id: string;
  crop_type: string;
  planting_date: string;
  expected_harvest_date?: string;
  status: string;
  yield_estimate?: number;
  actual_yield?: number;
  created_at: string;
}

export interface CropCycleCreate {
  field_id: string;
  crop_type: string;
  planting_date: string;
  expected_harvest_date?: string;
}

export interface CropCycleUpdate {
  crop_type?: string;
  planting_date?: string;
  expected_harvest_date?: string;
  status?: string;
  yield_estimate?: number;
  actual_yield?: number;
}

/**
 * Farm API endpoints
 */
export const farmsAPI = {
  /**
   * List all farms with pagination
   */
  list: async (params?: { page?: number; page_size?: number; farmer_id?: string }): Promise<FarmListResponse> => {
    const response = await api.get<FarmListResponse>('/agri/farms/', { params });
    return response.data;
  },

  /**
   * Get a single farm by ID
   */
  get: async (farmId: string): Promise<Farm> => {
    const response = await api.get<Farm>(`/agri/farms/${farmId}/`);
    return response.data;
  },

  /**
   * Create a new farm
   */
  create: async (farmData: FarmCreate): Promise<Farm> => {
    const response = await api.post<Farm>('/agri/farms/', farmData);
    return response.data;
  },

  /**
   * Update an existing farm
   */
  update: async (farmId: string, farmData: FarmUpdate): Promise<Farm> => {
    const response = await api.patch<Farm>(`/agri/farms/${farmId}`, farmData);
    return response.data;
  },

  /**
   * Delete a farm (soft delete)
   */
  delete: async (farmId: string): Promise<void> => {
    await api.delete(`/agri/farms/${farmId}`);
  },

  /**
   * Get fields for a specific farm
   */
  getFields: async (farmId: string): Promise<Field[]> => {
    const response = await api.get<Field[]>(`/agri/farms/${farmId}/fields/`);
    return response.data;
  },

  /**
   * Create a new field for a farm
   */
  createField: async (fieldData: FieldCreate): Promise<Field> => {
    const response = await api.post<Field>('/agri/fields/', fieldData);
    return response.data;
  },

  /**
   * Get all fields (global)
   */
  listFields: async (params?: { farm_id?: string }): Promise<Field[]> => {
    const response = await api.get<Field[]>('/agri/fields/', { params });
    return response.data;
  },

  /**
   * Get a single field by ID
   */
  getField: async (fieldId: string): Promise<Field> => {
    const response = await api.get<Field>(`/agri/fields/${fieldId}/`);
    return response.data;
  },

  /**
   * Update a field
   */
  updateField: async (fieldId: string, fieldData: FieldUpdate): Promise<Field> => {
    const response = await api.patch<Field>(`/agri/fields/${fieldId}`, fieldData);
    return response.data;
  },

  /**
   * Delete a field
   */
  deleteField: async (fieldId: string): Promise<void> => {
    await api.delete(`/agri/fields/${fieldId}`);
  },

  /**
   * Get crop cycles for a field
   */
  getCropCycles: async (fieldId: string): Promise<CropCycle[]> => {
    const response = await api.get<CropCycle[]>(`/agri/fields/${fieldId}/crop-cycles/`);
    return response.data;
  },

  /**
   * Get all crop cycles (global)
   */
  listCropCycles: async (params?: { field_id?: string; status?: string }): Promise<CropCycle[]> => {
    const response = await api.get<CropCycle[]>('/agri/crop-cycles/', { params });
    return response.data;
  },

  /**
   * Get a single crop cycle by ID
   */
  getCropCycle: async (cycleId: string): Promise<CropCycle> => {
    const response = await api.get<CropCycle>(`/agri/crop-cycles/${cycleId}/`);
    return response.data;
  },

  /**
   * Create a new crop cycle
   */
  createCropCycle: async (cycleData: CropCycleCreate): Promise<CropCycle> => {
    const response = await api.post<CropCycle>('/agri/crop-cycles/', cycleData);
    return response.data;
  },

  /**
   * Update a crop cycle
   */
  updateCropCycle: async (cycleId: string, cycleData: CropCycleUpdate): Promise<CropCycle> => {
    const response = await api.patch<CropCycle>(`/agri/crop-cycles/${cycleId}`, cycleData);
    return response.data;
  },

  /**
   * Delete a crop cycle
   */
  deleteCropCycle: async (cycleId: string): Promise<void> => {
    await api.delete(`/agri/crop-cycles/${cycleId}`);
  },
};

export default farmsAPI;
