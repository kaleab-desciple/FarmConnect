// FarmConnect Order Types - Mirroring Python DTOs from shared_models
import { OrderStatus } from "./enums";

/**
 * Base order model
 */
export interface OrderBase {
  farmer_id: string;
  merchant_id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  delivery_cost?: number;
  platform_fee?: number;
  total_price?: number;
  status?: OrderStatus;
  escrow_id?: string;
  subtotal?: number;
  delivery_fee?: number;
  delivery_margin?: number;
  quality_fee?: number;
  batch_id?: string;
  cancelled_at?: string;
  cancelled_reason?: string;
}

/**
 * Order response model
 */
export interface Order extends OrderBase {
  id: string;
  created_at: string;
}

/**
 * Order creation request
 */
export interface OrderCreate extends OrderBase {}

/**
 * Order update request
 */
export interface OrderUpdate {
  status?: OrderStatus;
  escrow_id?: string;
  batch_id?: string;
  cancelled_at?: string;
  cancelled_reason?: string;
}

/**
 * Paginated order list response
 */
export interface OrderListResponse {
  orders: Order[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * Order with product and user details
 */
export interface OrderDetail extends Order {
  product_name: string;
  product_category: string;
  farmer_name: string;
  merchant_name: string;
  delivery_status?: string;
}

/**
 * Order summary for dashboard
 */
export interface OrderSummary {
  total_orders: number;
  pending_payment: number;
  in_delivery: number;
  completed: number;
  cancelled: number;
  total_value: number;
}
