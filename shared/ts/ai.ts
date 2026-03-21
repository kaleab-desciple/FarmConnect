// FarmConnect AI Diagnosis Types - Mirroring Python DTOs from shared_models
import { Priority } from "./enums";

/**
 * Geo location model
 */
export interface GeoLocation {
  latitude: number;
  longitude: number;
  altitude_m?: number;
  accuracy_m?: number;
}

/**
 * Symptom detail model
 */
export interface SymptomDetail {
  symptom_type: string;
  location_on_plant: string;
  pattern?: string;
  progression?: string;
  description?: string;
}

/**
 * Analysis detection model
 */
export interface AnalysisDetection {
  detection_type: string;
  name: string;
  scientific_name?: string;
  confidence: number;
  bbox?: number[];
  severity?: string;
  affected_area_pct?: number;
}

/**
 * Image analysis result model
 */
export interface ImageAnalysisResult {
  analysis_id: string;
  image_url: string;
  analysis_type: string;
  detections: AnalysisDetection[];
  overall_health_score: number;
  primary_issue?: string;
  confidence_score: number;
  model_used: string;
  processing_time_ms: number;
  recommendations: string[];
  created_at: string;
}

/**
 * Image analysis result creation request
 */
export interface ImageAnalysisResultCreate {
  image_url: string;
  analysis_type: string;
  detections: AnalysisDetection[];
  overall_health_score: number;
  primary_issue?: string;
  confidence_score: number;
  model_used: string;
  processing_time_ms: number;
  recommendations?: string[];
}

/**
 * Treatment option model
 */
export interface TreatmentOption {
  treatment_id: string;
  type: string;
  name: string;
  active_ingredient?: string;
  efficacy_score: number;
  cost_per_ha: number;
  application_method: string;
  pre_harvest_interval_days: number;
  reentry_interval_hours: number;
  restrictions: string[];
  safety_ppe: string[];
  environmental_warnings: string[];
  application_instructions: string;
}

/**
 * Treatment option creation request
 */
export interface TreatmentOptionCreate {
  type: string;
  name: string;
  active_ingredient?: string;
  efficacy_score: number;
  cost_per_ha: number;
  application_method: string;
  pre_harvest_interval_days: number;
  reentry_interval_hours: number;
  restrictions?: string[];
  safety_ppe?: string[];
  environmental_warnings?: string[];
  application_instructions: string;
}

/**
 * Diagnosis session base model
 */
export interface DiagnosisSessionBase {
  field_id: string;
  crop_cycle_id?: string;
  location?: GeoLocation;
  region?: string;
  crop_type: string;
  growth_stage: string;
  planting_date?: string;
  suspected_issue?: string;
  issue_category: string;
  affected_area_pct: number;
  symptoms_list?: string[];
  symptom_onset_days?: number;
  symptom_severity: string;
  weather_recent?: string;
  irrigation_type?: string;
  soil_type?: string;
  image_urls?: string[];
  priority?: Priority;
  farmer_notes?: string;
}

/**
 * Diagnosis session response model
 */
export interface DiagnosisSession extends DiagnosisSessionBase {
  id: string;
  status: string;
  confidence_score?: number;
  primary_diagnosis?: string;
  symptom_details: SymptomDetail[];
  image_analyses: ImageAnalysisResult[];
  treatments_recommended: TreatmentOption[];
  treatments_applied?: Record<string, unknown>[];
  follow_ups?: Record<string, unknown>[];
  farmer_feedback?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

/**
 * Diagnosis session creation request
 */
export interface DiagnosisSessionCreate extends DiagnosisSessionBase {}

/**
 * Diagnosis session update request
 */
export interface DiagnosisSessionUpdate {
  agronomist_id?: string;
  field_id?: string;
  crop_cycle_id?: string;
  location?: GeoLocation;
  region?: string;
  crop_type?: string;
  growth_stage?: string;
  planting_date?: string;
  suspected_issue?: string;
  issue_category?: string;
  affected_area_pct?: number;
  symptoms_list?: string[];
  symptom_onset_days?: number;
  symptom_severity?: string;
  weather_recent?: string;
  irrigation_type?: string;
  soil_type?: string;
  image_urls?: string[];
  priority?: Priority;
  farmer_notes?: string;
  status?: string;
  confidence_score?: number;
  primary_diagnosis?: string;
  symptom_details?: SymptomDetail[];
  image_analyses?: ImageAnalysisResult[];
  treatments_recommended?: TreatmentOption[];
  treatments_applied?: Record<string, unknown>[];
  follow_ups?: Record<string, unknown>[];
  farmer_feedback?: Record<string, unknown>;
}
