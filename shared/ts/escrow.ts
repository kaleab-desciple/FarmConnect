// FarmConnect Escrow Types - Mirroring Python DTOs from shared_models
import { EscrowState, Provider } from "./enums";

/**
 * Base escrow model
 */
export interface EscrowBase {
  order_id: string;
  state?: EscrowState;
  amount?: number;
  penalty_applied?: boolean;
  provider?: Provider;
}

/**
 * Escrow response model
 */
export interface Escrow extends EscrowBase {
  id: string;
  created_at: string;
  updated_at?: string;
  funded_at?: string;
  released_at?: string;
  provider_reference?: string;
}

/**
 * Escrow creation request
 */
export interface EscrowCreate extends EscrowBase {}

/**
 * Escrow update request
 */
export interface EscrowUpdate {
  state?: EscrowState;
  amount?: number;
  penalty_applied?: boolean;
  provider?: Provider;
}

/**
 * Escrow funding request
 */
export interface EscrowFundRequest {
  order_id: string;
  amount: number;
  provider: Provider;
  payment_reference: string;
}

/**
 * Escrow release request
 */
export interface EscrowReleaseRequest {
  escrow_id: string;
  release_reason?: string;
}

/**
 * Escrow refund request
 */
export interface EscrowRefundRequest {
  escrow_id: string;
  refund_reason: string;
}
