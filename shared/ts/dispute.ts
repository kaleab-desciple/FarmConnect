// FarmConnect Dispute Types - Mirroring Python DTOs from shared_models
import { DisputeState, DisputeResolution } from "./enums";

/**
 * Base dispute model
 */
export interface DisputeBase {
  order_id: string;
  raised_by: string;
  state?: DisputeState;
  reason?: string;
  resolution?: DisputeResolution;
  evidence_urls?: string[];
  handler_role?: string;
  escalated_to?: string;
  escalation_note?: string;
}

/**
 * Dispute response model
 */
export interface Dispute extends DisputeBase {
  id: string;
  created_at: string;
  resolved_at?: string;
}

/**
 * Dispute creation request
 */
export interface DisputeCreate extends DisputeBase {}

/**
 * Dispute update request
 */
export interface DisputeUpdate {
  state?: DisputeState;
  resolution?: DisputeResolution;
  evidence_urls?: string[];
  handler_role?: string;
  escalated_to?: string;
  escalation_note?: string;
}

/**
 * Dispute resolution request
 */
export interface DisputeResolveRequest {
  resolution: DisputeResolution;
  resolution_notes: string;
}

/**
 * Dispute escalation request
 */
export interface DisputeEscalateRequest {
  escalated_to: string;
  escalation_note: string;
}
