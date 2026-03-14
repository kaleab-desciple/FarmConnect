/**
 * Orders API Service
 * FarmConnect - AgriManagement
 * 
 * API integration for order management operations
 * Updated to match server-side DTOs from shared_models/order.py
 */

import api from '../../../app/services/api';

/**
 * Order status types - aligned with server OrderStatus enum
 * Server enum values: CREATED, CONFIRMED, IN_PROGRESS, IN_TRANSIT, DELIVERED, 
 *                    COMPLETED, CANCELLED, DISPUTED, LOAN_REQUESTED, 
 *                    LOAN_DISBURSED, LOAN_REPAID
 */
export type OrderStatus = 
  | 'CREATED'
  | 'CONFIRMED'
  | 'IN_PROGRESS'
  | 'IN_TRANSIT'
  | 'DELIVERED'
  | 'COMPLETED'
  | 'CANCELLED'
  | 'DISPUTED'
  | 'LOAN_REQUESTED'
  | 'LOAN_DISBURSED'
  | 'LOAN_REPAID';

/**
 * Order Type - aligned with server Order model
 * Server fields: id (UUID), farmer_id, merchant_id, product_id, quantity,
 *                unit_price, delivery_cost, platform_fee, status, escrow_id,
 *                subtotal, delivery_fee, delivery_margin, quality_fee, total_price,
 *                created_at, updated_at
 */
export interface Order {
  id: string;
  farmer_id: string;
  merchant_id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  delivery_cost?: number;
  platform_fee?: number;
  status: OrderStatus;
  escrow_id?: string;
  subtotal?: number;
  delivery_fee?: number;
  delivery_margin?: number;
  quality_fee?: number;
  total_price?: number;
  created_at: string;
  updated_at?: string;
}

/**
 * Order Create Type - aligned with server OrderCreate model
 */
export interface OrderCreate {
  farmer_id: string;
  merchant_id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  delivery_cost?: number;
  platform_fee?: number;
  delivery_address?: string;
}

/**
 * Order List Response Type - server returns array directly, not paginated
 */
export type OrderListResponse = Order[];

/**
 * Escrow Type - aligned with server Escrow model
 */
export interface Escrow {
  id: string;
  order_id: string;
  amount: number;
  status: 'PENDING' | 'FUNDED' | 'RELEASED' | 'REFUNDED';
  created_at: string;
  released_at?: string;
}

/**
 * Order list filters
 */
export interface OrderListParams {
  page?: number;
  page_size?: number;
  status?: OrderStatus;
  farmer_id?: string;
  merchant_id?: string;
}

/**
 * Order API endpoints
 */
export const ordersAPI = {
  /**
   * List orders with optional filters
   * Server endpoint: GET /orders/
   */
  list: async (params?: OrderListParams): Promise<OrderListResponse> => {
    const response = await api.get<OrderListResponse>('/orders/', { params });
    return response.data;
  },

  /**
   * Get a single order by ID
   * Server endpoint: GET /orders/{order_id}
   */
  get: async (orderId: string): Promise<Order> => {
    const response = await api.get<Order>(`/orders/${orderId}/`);
    return response.data;
  },

  /**
   * Create a new order
   * Server endpoint: POST /orders/
   */
  create: async (orderData: OrderCreate): Promise<{ order: Order; escrow: Escrow }> => {
    const response = await api.post<{ order: Order; escrow: Escrow }>('/orders/', orderData);
    return response.data;
  },

  /**
   * Update an order (e.g., schedule pickup)
   * Server endpoint: PATCH /orders/{order_id}
   */
  update: async (orderId: string, updates: Partial<Order>): Promise<Order> => {
    const response = await api.patch<Order>(`/orders/${orderId}`, updates);
    return response.data;
  },

  /**
   * Cancel an order
   * Server endpoint: POST /orders/{order_id}/cancel/
   */
  cancel: async (orderId: string, reason?: string): Promise<Order> => {
    const response = await api.post<Order>(`/orders/${orderId}/cancel/`, { reason });
    return response.data;
  },

  /**
   * Get order escrow details
   * Server endpoint: GET /orders/{order_id}/escrow/
   */
  getEscrow: async (orderId: string): Promise<Escrow> => {
    const response = await api.get<Escrow>(`/orders/${orderId}/escrow/`);
    return response.data;
  },

  /**
   * Fund escrow (for merchants)
   * Server endpoint: POST /orders/{order_id}/fund/
   */
  fundEscrow: async (orderId: string, paymentMethod: string): Promise<Escrow> => {
    const response = await api.post<Escrow>(`/orders/${orderId}/fund/`, { payment_method: paymentMethod });
    return response.data;
  },

  /**
   * Release escrow (for farmers after delivery)
   * Server endpoint: POST /orders/{order_id}/release/
   */
  releaseEscrow: async (orderId: string): Promise<Escrow> => {
    const response = await api.post<Escrow>(`/orders/${orderId}/release/`);
    return response.data;
  },

  /**
   * Confirm delivery (for buyers)
   * Server endpoint: POST /orders/{order_id}/confirm-delivery/
   */
  confirmDelivery: async (orderId: string, confirmationCode?: string): Promise<Order> => {
    const response = await api.post<Order>(`/orders/${orderId}/confirm-delivery/`, { 
      confirmation_code: confirmationCode 
    });
    return response.data;
  },

  /**
   * Get pricing for an order
   * Server endpoint: POST /orders/pricing/
   */
  getPricing: async (orderData: {
    unit_price: number;
    quantity: number;
    distance_km?: number;
    product_type?: string;
  }): Promise<{
    subtotal: number;
    delivery_fee: number;
    platform_fee: number;
    total_price: number;
  }> => {
    const response = await api.post('/orders/pricing/', orderData);
    return response.data;
  },
};

export default ordersAPI;
