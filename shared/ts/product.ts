// FarmConnect Product Types - Mirroring Python DTOs from shared_models
import { Category, ProductStatus, QualityGrade, Unit } from "./enums";

/**
 * Product location
 */
export interface ProductLocation {
  latitude: number;
  longitude: number;
}

/**
 * Base product model
 */
export interface ProductBase {
  farmer_id: string;
  name: string;
  description?: string;
  category: Category;
  unit: Unit;
  base_price: number;
  currency: string;
  total_quantity?: number;
  reserved_quantity?: number;
  sold_quantity?: number;
  spoiled_quantity?: number;
  harvest_id?: string;
  crop_cycle_id?: string;
  version?: number;
  deleted_at?: string;
  quality_grade?: QualityGrade;
  harvest_date?: string; // date string (YYYY-MM-DD)
  expiry_date?: string;
  location?: ProductLocation;
  images?: string[];
  is_active?: boolean;
  metadata?: Record<string, unknown>;
}

/**
 * Product response model
 */
export interface Product extends ProductBase {
  id: string;
  created_at: string;
  updated_at: string;
}

/**
 * Product creation request
 */
export interface ProductCreate extends ProductBase {}

/**
 * Product update request - all fields optional for partial updates
 */
export interface ProductUpdate {
  name?: string;
  description?: string;
  category?: Category;
  unit?: Unit;
  base_price?: number;
  currency?: string;
  total_quantity?: number;
  reserved_quantity?: number;
  sold_quantity?: number;
  spoiled_quantity?: number;
  quality_grade?: QualityGrade;
  harvest_date?: string;
  expiry_date?: string;
  location?: ProductLocation;
  images?: string[];
  is_active?: boolean;
  metadata?: Record<string, unknown>;
}

/**
 * Paginated product list response
 */
export interface ProductListResponse {
  products: Product[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * Product with farm info for listing
 */
export interface ProductWithFarm extends Product {
  farm_name: string;
  farm_location?: ProductLocation;
}

/**
 * Product inventory summary
 */
export interface ProductInventorySummary {
  product_id: string;
  total_quantity: number;
  reserved_quantity: number;
  available_quantity: number;
  spoiled_quantity: number;
}
