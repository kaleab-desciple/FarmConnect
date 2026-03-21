// FarmConnect Monitoring Types - Mirroring Python DTOs from shared_models
import { NDVISource, StressLevel, SoilReadingSource, SeverityLevel, ReportType, TreatmentStatus } from "./enums";

// ============ Soil Reading Types ============

/**
 * Soil reading base model
 */
export interface SoilReadingBase {
  field_id: string;
  location_geojson?: Record<string, unknown>;
  sample_depth_cm?: number;
  sample_depth_range?: string;
  moisture_pct?: number;
  temperature_c?: number;
  ph?: number;
  nitrogen_ppm?: number;
  phosphorus_ppm?: number;
  potassium_ppm?: number;
  organic_matter_pct?: number;
  source: SoilReadingSource;
  lab_name?: string;
  lab_report_url?: string;
  recorded_by?: string;
  recorded_at?: string;
  weather_conditions?: string;
  days_since_rain?: number;
  cation_exchange_capacity?: number;
  electrical_conductivity_ms_cm?: number;
  texture_analysis?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

/**
 * Soil reading response model
 */
export interface SoilReading extends SoilReadingBase {
  id: string;
  created_at: string;
  updated_at?: string;
  deleted_at?: string;
}

/**
 * Soil reading creation request
 */
export interface SoilReadingCreate extends SoilReadingBase {}

/**
 * Soil reading update request
 */
export interface SoilReadingUpdate {
  location_geojson?: Record<string, unknown>;
  sample_depth_cm?: number;
  sample_depth_range?: string;
  moisture_pct?: number;
  temperature_c?: number;
  ph?: number;
  nitrogen_ppm?: number;
  phosphorus_ppm?: number;
  potassium_ppm?: number;
  cation_exchange_capacity?: number;
  electrical_conductivity_ms_cm?: number;
  texture_analysis?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

// ============ NDVI Snapshot Types ============

/**
 * NDVI snapshot base model
 */
export interface NDVISnapshotBase {
  field_id?: string;
  crop_cycle_id?: string;
  source?: string;
  source_metadata?: Record<string, unknown>;
  captured_at?: string;
  processed_at?: string;
  ndvi_mean?: number;
  ndvi_min?: number;
  ndvi_max?: number;
  ndvi_stddev?: number;
  stress_level?: StressLevel;
  cloud_cover_pct?: number;
  data_quality_score?: number;
  tile_urls?: Record<string, unknown>;
}

/**
 * NDVI snapshot response model
 */
export interface NDVISnapshot extends NDVISnapshotBase {
  id: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

/**
 * NDVI snapshot creation request
 */
export interface NDVISnapshotCreate extends NDVISnapshotBase {}

/**
 * NDVI snapshot update request
 */
export interface NDVISnapshotUpdate {
  source?: string;
  source_metadata?: Record<string, unknown>;
  captured_at?: string;
  processed_at?: string;
  ndvi_mean?: number;
  ndvi_min?: number;
  ndvi_max?: number;
  ndvi_stddev?: number;
  stress_level?: StressLevel;
  cloud_cover_pct?: number;
  data_quality_score?: number;
  tile_urls?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

// ============ Pest/Disease Report Types ============

/**
 * Pest/disease report base model
 */
export interface PestDiseaseReportBase {
  field_id?: string;
  crop_cycle_id?: string;
  report_type?: ReportType;
  pest_disease_name?: string;
  severity?: SeverityLevel;
  affected_area_pct?: number;
  location_geojson?: Record<string, unknown>;
  observed_at?: string;
  description?: string;
  treatment_status?: TreatmentStatus;
  reported_by?: string;
  image_urls?: string[];
}

/**
 * Pest/disease report response model
 */
export interface PestDiseaseReport extends PestDiseaseReportBase {
  id: string;
  created_at: string;
  updated_at?: string;
}

/**
 * Pest/disease report creation request
 */
export interface PestDiseaseReportCreate extends PestDiseaseReportBase {}

/**
 * Pest/disease report update request
 */
export interface PestDiseaseReportUpdate {
  severity?: SeverityLevel;
  affected_area_pct?: number;
  location_geojson?: Record<string, unknown>;
  description?: string;
  treatment_status?: TreatmentStatus;
  image_urls?: string[];
  metadata?: Record<string, unknown>;
}

// ============ Treatment Recommendation Types ============

/**
 * Treatment recommendation base model
 */
export interface TreatmentRecommendationBase {
  report_id?: string;
  product_name?: string;
  product_type?: string;
  application_method?: string;
  dosage?: string;
  application_timing?: string;
  reapplication_interval_days?: number;
  estimated_cost_usd?: number;
  effectiveness_score?: number;
  notes?: string;
}

/**
 * Treatment recommendation response model
 */
export interface TreatmentRecommendation extends TreatmentRecommendationBase {
  id: string;
  created_at: string;
  updated_at?: string;
  deleted_at?: string;
}

/**
 * Treatment recommendation creation request
 */
export interface TreatmentRecommendationCreate extends TreatmentRecommendationBase {}
