// FarmConnect Delivery Types - Mirroring Python DTOs from shared_models
import { DeliveryStatus } from "./enums";

/**
 * Base delivery model
 */
export interface DeliveryBase {
  order_id: string;
  carrier_id?: string;
  status?: DeliveryStatus;
  pickup_time?: string;
  delivered_time?: string;
  pickup_photo_url?: string;
  delivery_photo_url?: string;
  recipient_signature_url?: string;
  notes?: string;
}

/**
 * Delivery response model
 */
export interface Delivery extends DeliveryBase {
  id: string;
  created_at: string;
  updated_at?: string;
}

/**
 * Delivery creation request
 */
export interface DeliveryCreate extends DeliveryBase {}

/**
 * Delivery update request
 */
export interface DeliveryUpdate {
  carrier_id?: string;
  status?: DeliveryStatus;
  pickup_time?: string;
  delivered_time?: string;
  pickup_photo_url?: string;
  delivery_photo_url?: string;
  recipient_signature_url?: string;
  notes?: string;
}

/**
 * Delivery assignment request
 */
export interface DeliveryAssignRequest {
  order_id: string;
  carrier_id: string;
}

/**
 * Delivery status update request
 */
export interface DeliveryStatusUpdate {
  status: DeliveryStatus;
  notes?: string;
  pickup_photo_url?: string;
  delivery_photo_url?: string;
  recipient_signature_url?: string;
}

/**
 * Delivery tracking info
 */
export interface DeliveryTracking {
  delivery_id: string;
  order_id: string;
  status: DeliveryStatus;
  carrier_name: string;
  estimated_delivery_time?: string;
  current_location?: {
    latitude: number;
    longitude: number;
  };
  timeline: DeliveryTimelineEvent[];
}

/**
 * Delivery timeline event
 */
export interface DeliveryTimelineEvent {
  status: DeliveryStatus;
  timestamp: string;
  notes?: string;
}
