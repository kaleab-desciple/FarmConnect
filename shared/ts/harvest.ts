// FarmConnect Harvest Types - Mirroring Python DTOs from shared_models
import { BatchQCState, QCGrade, CertificationType } from "./enums";

// ============ Harvest Event Types ============

/**
 * Harvest event base model
 */
export interface HarvestEventBase {
  farm_id: string;
  field_id: string;
  crop_cycle_id?: string;
  collected_by?: string;
  harvested_at: string;
  gross_weight_kg: number;
  moisture_pct?: number;
  loss_kg?: number;
  photos?: Record<string, unknown>[];
  weighbridge_receipt?: Record<string, unknown>;
  location?: Record<string, unknown>;
  notes?: string;
}

/**
 * Harvest event response model
 */
export interface HarvestEvent extends HarvestEventBase {
  id: string;
  created_at: string;
  updated_at: string;
}

/**
 * Harvest event creation request
 */
export interface HarvestEventCreate extends HarvestEventBase {}

/**
 * Harvest event update request
 */
export interface HarvestEventUpdate {
  photos?: Record<string, unknown>[];
  weighbridge_receipt?: Record<string, unknown>;
  location?: Record<string, unknown>;
  notes?: string;
}

// ============ Harvest Batch Types ============

/**
 * Harvest batch base model
 */
export interface HarvestBatchBase {
  batch_code: string;
  aggregator_id?: string;
  notes?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Harvest batch response model
 */
export interface HarvestBatch extends HarvestBatchBase {
  id: string;
  aggregator_id?: string;
  status: string;
  aggregated_weight_kg?: number;
  moisture_avg?: number;
  sealed_at?: string;
  sealed_by?: string;
  seal_evidence?: Record<string, unknown>;
  lineage_hash?: string;
  lineage_signature?: string;
  created_at: string;
  updated_at: string;
  contributions: HarvestBatchContribution[];
}

/**
 * Harvest batch creation request
 */
export interface HarvestBatchCreate extends HarvestBatchBase {}

/**
 * Harvest batch seal request
 */
export interface HarvestBatchSealRequest {
  sealed_by: string;
  seal_evidence?: Record<string, unknown>;
}

// ============ Harvest Batch Contribution Types ============

/**
 * Harvest batch contribution base model
 */
export interface HarvestBatchContributionBase {
  harvest_batch_id: string;
  harvest_event_id: string;
  farmer_id: string;
  contributed_weight_kg: number;
  reported_moisture_pct?: number;
}

/**
 * Harvest batch contribution response model
 */
export interface HarvestBatchContribution extends HarvestBatchContributionBase {
  id: string;
  created_at: string;
}

/**
 * Harvest batch contribution creation request
 */
export interface HarvestBatchContributionCreate extends HarvestBatchContributionBase {}

// ============ Batch QC Report Types ============

/**
 * Batch QC report base model
 */
export interface BatchQCReportBase {
  batch_id: string;
  lab_id?: string;
  tested_at: string;
  metrics?: Record<string, unknown>;
  passed: boolean;
  report_url?: string;
  signed_hash?: string;
  notes?: string;
}

/**
 * Batch QC report response model
 */
export interface BatchQCReport extends BatchQCReportBase {
  id: string;
  created_at: string;
}

/**
 * Batch QC report creation request
 */
export interface BatchQCReportCreate extends BatchQCReportBase {}

// ============ Batch QC Report V2 Types ============

/**
 * Batch QC report V2 base model
 */
export interface BatchQCReportV2Base {
  batch_id: string;
  sample_id?: string;
  lab_id?: string;
  tested_at: string;
  metrics?: Record<string, unknown>;
  grade?: QCGrade;
  passed: boolean;
  report_url?: string;
  signed_hash?: string;
  verified?: boolean;
  notes?: string;
}

/**
 * Batch QC report V2 response model
 */
export interface BatchQCReportV2 extends BatchQCReportV2Base {
  id: string;
  created_at: string;
}

/**
 * Batch QC report V2 creation request
 */
export interface BatchQCReportV2Create extends BatchQCReportV2Base {}

// ============ Sample Types ============

/**
 * Sample base model
 */
export interface SampleBase {
  sample_code: string;
  harvest_batch_id: string;
  collected_by?: string;
  collected_at?: string;
  sample_points?: Record<string, unknown>;
  photos?: Record<string, unknown>[];
  chain_of_custody?: Record<string, unknown>;
  submitted_to_lab?: boolean;
}

/**
 * Sample response model
 */
export interface Sample extends SampleBase {
  id: string;
  created_at: string;
}

/**
 * Sample creation request
 */
export interface SampleCreate extends SampleBase {}

// ============ Lab Provider Types ============

/**
 * Lab provider base model
 */
export interface LabProviderBase {
  name: string;
  public_key?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Lab provider response model
 */
export interface LabProvider extends LabProviderBase {
  id: string;
  created_at: string;
}

/**
 * Lab provider creation request
 */
export interface LabProviderCreate extends LabProviderBase {}

// ============ Certification Types ============

/**
 * Certification base model
 */
export interface CertificationBase {
  harvest_batch_id: string;
  issuer: string;
  cert_type: CertificationType;
  cert_number?: string;
  valid_from: string;
  valid_to: string;
  cert_url?: string;
  signed_hash?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Certification response model
 */
export interface Certification extends CertificationBase {
  id: string;
  created_at: string;
}

/**
 * Certification creation request
 */
export interface CertificationCreate extends CertificationBase {}

// ============ QC Grade Rule Types ============

/**
 * QC grade rule base model
 */
export interface QCGradeRuleBase {
  commodity: string;
  grade: string;
  rules: Record<string, unknown>[];
  is_active?: boolean;
}

/**
 * QC grade rule response model
 */
export interface QCGradeRule extends QCGradeRuleBase {
  id: string;
  created_at: string;
  updated_at: string;
}

/**
 * QC grade rule creation request
 */
export interface QCGradeRuleCreate extends QCGradeRuleBase {}

// ============ Audit Event Types ============

/**
 * Audit event base model
 */
export interface AuditEventBase {
  event_type: string;
  entity_type: string;
  entity_id: string;
  payload?: Record<string, unknown>;
  payload_hash?: string;
  previous_event_hash?: string;
  user_id?: string;
  signature?: string;
}

/**
 * Audit event response model
 */
export interface AuditEvent extends AuditEventBase {
  id: string;
  created_at: string;
}

/**
 * Audit event creation request
 */
export interface AuditEventCreate extends AuditEventBase {}
