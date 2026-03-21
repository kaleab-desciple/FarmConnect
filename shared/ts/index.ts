// FarmConnect TypeScript Type Definitions
// This module exports all TypeScript types mirroring Python DTOs from shared_models
// Used for strict type safety across the frontend-backend boundary

// ============ Enums ============
export * from "./enums";

// ============ User Types ============
export * from "./user";

// ============ Farm, Field & Crop Cycle Types ============
export * from "./farm";

// ============ Product Types ============
export * from "./product";

// ============ Order Types ============
export * from "./order";

// ============ Escrow Types ============
export * from "./escrow";

// ============ Delivery Types ============
export * from "./delivery";

// ============ Dispute Types ============
export * from "./dispute";

// ============ Weather & Alert Types ============
export * from "./weather";

// ============ Monitoring Types ============
export * from "./monitoring";

// ============ Harvest Types ============
export * from "./harvest";

// ============ Accounting Types ============
export * from "./account";

// ============ AI Diagnosis Types ============
export * from "./ai";

// ============ Additional Types ============

/**
 * Pagination parameters for list endpoints
 */
export interface PaginationParams {
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

/**
 * Paginated response wrapper
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * API error response
 */
export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, unknown>;
  status_code: number;
}

/**
 * API success response wrapper
 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

/**
 * ID request parameter
 */
export interface IdParam {
  id: string;
}

/**
 * Delete response
 */
export interface DeleteResponse {
  success: boolean;
  message?: string;
}
