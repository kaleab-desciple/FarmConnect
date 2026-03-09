/**
 * Orders API Service
 * FarmConnect - AgriManagement
 * 
 * API integration for order management operations
 */

import api from '../../../app/services/api';

/**
 * Order status types
 */
export type OrderStatus = 
  | 'PENDING_PAYMENT'
  | 'PAYMENT_FAILED'
  | 'FUNDED'
  | 'PROCESSING'
  | 'PICKED_UP'
  | 'IN_TRANSIT'
  | 'DELIVERED'
  | 'COMPLETED'
  | 'CANCELLED'
  | 'DISPUTED';

/**
 * Order Type
 */
export interface Order {
  id: string;
  farmer_id: string;
  merchant_id: string;
  product_id: string;
  product_name: string;
  quantity: number;
  unit: string;
  unit_price: number;
  total_price: number;
  status: OrderStatus;
  delivery_address?: string;
  distance_km?: number;
  created_at: string;
  updated_at?: string;
}

/**
 * Order Create Type
 */
export interface OrderCreate {
  product_id: string;
  quantity: number;
  unit_price: number;
  delivery_address?: string;
}

/**
 * Order List Response Type
 */
export interface OrderListResponse {
  items: Order[];
  total: number;
  page: number;
  page_size: number;
}

/**
 * Escrow Type
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
   */
  list: async (params?: OrderListParams): Promise<OrderListResponse> => {
    const response = await api.get<OrderListResponse>('/orders/', { params });
    return response.data;
  },

  /**
   * Get a single order by ID
   */
  get: async (orderId: string): Promise<Order> => {
    const response = await api.get<Order>(`/orders/${orderId}/`);
    return response.data;
  },

  /**
   * Create a new order
   */
  create: async (orderData: OrderCreate): Promise<{ order: Order; escrow: Escrow }> => {
    const response = await api.post<{ order: Order; escrow: Escrow }>('/orders/', orderData);
    return response.data;
  },

  /**
   * Update an order (e.g., schedule pickup)
   */
  update: async (orderId: string, updates: Partial<Order>): Promise<Order> => {
    const response = await api.patch<Order>(`/orders/${orderId}`, updates);
    return response.data;
  },

  /**
   * Cancel an order
   */
  cancel: async (orderId: string, reason?: string): Promise<Order> => {
    const response = await api.post<Order>(`/orders/${orderId}/cancel/`, { reason });
    return response.data;
  },

  /**
   * Get order escrow details
   */
  getEscrow: async (orderId: string): Promise<Escrow> => {
    const response = await api.get<Escrow>(`/orders/${orderId}/escrow/`);
    return response.data;
  },

  /**
   * Fund escrow (for merchants)
   */
  fundEscrow: async (orderId: string, paymentMethod: string): Promise<Escrow> => {
    const response = await api.post<Escrow>(`/orders/${orderId}/fund/`, { payment_method: paymentMethod });
    return response.data;
  },

  /**
   * Release escrow (for farmers after delivery)
   */
  releaseEscrow: async (orderId: string): Promise<Escrow> => {
    const response = await api.post<Escrow>(`/orders/${orderId}/release/`);
    return response.data;
  },

  /**
   * Confirm delivery (for buyers)
   */
  confirmDelivery: async (orderId: string, confirmationCode?: string): Promise<Order> => {
    const response = await api.post<Order>(`/orders/${orderId}/confirm-delivery/`, { 
      confirmation_code: confirmationCode 
    });
    return response.data;
  },

  /**
   * Get pricing for an order
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
