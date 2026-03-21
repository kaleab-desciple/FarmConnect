/**
 * Data mappers for FarmConnect
 * Converts raw API responses to clean, typed domain objects.
 * Mirroring the backend's Data Transformation Layer (mappers.py).
 */

import type { Farm, Field, CropCycle } from "@shared/farm";
import type { PaginatedResponse } from "@/app/services/api";

/**
 * Generic mapper for paginated responses
 */
export const mapPaginated = <T>(
  data: any, 
  itemMapper: (item: any) => T
): PaginatedResponse<T> => {
  return {
    items: (data.items || []).map(itemMapper),
    total: Number(data.total) || 0,
    page: Number(data.page) || 1,
    page_size: Number(data.page_size) || 20,
    total_pages: Number(data.total_pages) || 1,
  };
};

/**
 * Maps raw farm data from API
 */
export const mapFarm = (data: any): Farm => {
  return {
    ...data,
    location_lat: Number(data.location_lat),
    location_lng: Number(data.location_lng),
    total_area_ha: data.total_area_ha ? Number(data.total_area_ha) : undefined,
  };
};

/**
 * Maps raw field data from API
 */
export const mapField = (data: any): Field => {
  return {
    ...data,
    area_ha: Number(data.area_ha),
    elevation_m: data.elevation_m ? Number(data.elevation_m) : undefined,
    slope_degree: data.slope_degree ? Number(data.slope_degree) : undefined,
  };
};

/**
 * Maps raw crop cycle data from API
 */
export const mapCropCycle = (data: any): CropCycle => {
  return {
    ...data,
    expected_yield_kg: data.expected_yield_kg ? Number(data.expected_yield_kg) : undefined,
    actual_yield_kg: data.actual_yield_kg ? Number(data.actual_yield_kg) : undefined,
    planting_density_per_ha: data.planting_density_per_ha ? Number(data.planting_density_per_ha) : undefined,
    seed_cost_usd: data.seed_cost_usd ? Number(data.seed_cost_usd) : undefined,
  };
};
