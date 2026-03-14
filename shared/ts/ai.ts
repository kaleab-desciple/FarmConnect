export interface AI {
    $schema:     string;
    $id:         string;
    title:       string;
    definitions: Definitions;
}

export interface Definitions {
    GeoLocation:         GeoLocation;
    SymptomDetail:       SymptomDetail;
    AnalysisDetection:   AnalysisDetection;
    ImageAnalysisResult: ImageAnalysisResult;
    TreatmentOption:     TreatmentOption;
    DiagnosisSession:    DiagnosisSession;
}

export interface AnalysisDetection {
    type:                 IDType;
    properties:           AnalysisDetectionProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface AnalysisDetectionProperties {
    detection_type:    DetectionType;
    name:              DetectionType;
    scientific_name:   ScientificName;
    confidence:        Confidence;
    bbox:              Bbox;
    severity:          ScientificName;
    affected_area_pct: AffectedAreaPct;
}

export interface AffectedAreaPct {
    type:         ScientificNameType[];
    minimum:      number;
    maximum:      number;
    description?: string;
}

export enum ScientificNameType {
    Null = "null",
    Number = "number",
    String = "string",
}

export interface Bbox {
    type:        string[];
    items:       ID;
    description: string;
}

export interface ID {
    type: IDType;
}

export enum IDType {
    Integer = "integer",
    Object = "object",
    String = "string",
}

export interface Confidence {
    type:         ConfidenceType;
    minimum:      number;
    maximum?:     number;
    description?: string;
}

export enum ConfidenceType {
    Integer = "integer",
    Number = "number",
}

export interface DetectionType {
    type:        IDType;
    description: string;
}

export interface ScientificName {
    type:        ScientificNameType[];
    description: string;
}

export interface DiagnosisSession {
    type:                 IDType;
    properties:           DiagnosisSessionProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface DiagnosisSessionProperties {
    id:                     ID;
    field_id:               DetectionType;
    crop_cycle_id:          ScientificName;
    location:               Location;
    region:                 FarmerFeedback;
    crop_type:              DetectionType;
    growth_stage:           DetectionType;
    planting_date:          FarmerFeedback;
    suspected_issue:        FarmerFeedback;
    issue_category:         DetectionType;
    affected_area_pct:      Confidence;
    symptoms_list:          ImageUrls;
    symptom_onset_days:     SymptomOnsetDays;
    symptom_severity:       ID;
    weather_recent:         FarmerFeedback;
    irrigation_type:        FarmerFeedback;
    soil_type:              FarmerFeedback;
    image_urls:             ImageUrls;
    priority:               Priority;
    farmer_notes:           FarmerFeedback;
    status:                 Status;
    confidence_score:       AffectedAreaPct;
    primary_diagnosis:      FarmerFeedback;
    symptom_details:        ImageAnalyses;
    image_analyses:         ImageAnalyses;
    treatments_recommended: ImageAnalyses;
    treatments_applied:     FollowUPS;
    follow_ups:             FollowUPS;
    farmer_feedback:        FarmerFeedback;
    created_at:             AtedAt;
    updated_at:             AtedAt;
}

export interface AtedAt {
    type:   IDType;
    format: string;
}

export interface FarmerFeedback {
    type: FarmerFeedbackType[];
}

export enum FarmerFeedbackType {
    Null = "null",
    Object = "object",
    String = "string",
}

export interface FollowUPS {
    type:  string[];
    items: ID;
}

export interface ImageAnalyses {
    type:  string;
    items: Location;
}

export interface Location {
    $ref: string;
}

export interface ImageUrls {
    type:  string;
    items: ID;
}

export interface Priority {
    type:    IDType;
    enum:    string[];
    default: string;
}

export interface Status {
    type:    IDType;
    default: string;
}

export interface SymptomOnsetDays {
    type:    string[];
    minimum: number;
}

export interface GeoLocation {
    type:                 IDType;
    properties:           GeoLocationProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface GeoLocationProperties {
    latitude:   Confidence;
    longitude:  Confidence;
    altitude_m: ScientificName;
    accuracy_m: ScientificName;
}

export interface ImageAnalysisResult {
    type:                 IDType;
    properties:           ImageAnalysisResultProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface ImageAnalysisResultProperties {
    analysis_id:          DetectionType;
    image_url:            DetectionType;
    analysis_type:        DetectionType;
    detections:           Detections;
    overall_health_score: Confidence;
    primary_issue:        ScientificName;
    confidence_score:     Confidence;
    model_used:           DetectionType;
    processing_time_ms:   Confidence;
    recommendations:      Recommendations;
    created_at:           AtedAt;
}

export interface Detections {
    type:        string;
    items:       Location;
    description: string;
}

export interface Recommendations {
    type:        string;
    items:       ID;
    description: string;
}

export interface SymptomDetail {
    type:                 IDType;
    properties:           SymptomDetailProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface SymptomDetailProperties {
    symptom_type:      DetectionType;
    location_on_plant: DetectionType;
    pattern:           ScientificName;
    progression:       ScientificName;
    description:       ScientificName;
}

export interface TreatmentOption {
    type:                 IDType;
    properties:           TreatmentOptionProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface TreatmentOptionProperties {
    treatment_id:              DetectionType;
    type:                      DetectionType;
    name:                      DetectionType;
    active_ingredient:         ScientificName;
    efficacy_score:            Confidence;
    cost_per_ha:               Confidence;
    application_method:        DetectionType;
    pre_harvest_interval_days: Confidence;
    reentry_interval_hours:    Confidence;
    restrictions:              Recommendations;
    safety_ppe:                Recommendations;
    environmental_warnings:    Recommendations;
    application_instructions:  DetectionType;
}
