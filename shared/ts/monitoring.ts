export interface Monitoring {
    $schema:     string;
    $id:         string;
    title:       string;
    definitions: Definitions;
}

export interface Definitions {
    SoilReading:             SoilReading;
    NDVISnapshot:            NDVISnapshot;
    PestDiseaseReport:       PestDiseaseReport;
    TreatmentRecommendation: TreatmentRecommendation;
}

export interface NDVISnapshot {
    type:                 Type;
    properties:           NDVISnapshotProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface NDVISnapshotProperties {
    id:                 ID;
    field_id:           FieldID;
    crop_cycle_id:      CropCycleID;
    source:             FieldID;
    source_metadata:    CropCycleID;
    captured_at:        EdAt;
    processed_at:       ProcessedAt;
    ndvi_mean:          NdviMean;
    ndvi_min:           CloudCoverPct;
    ndvi_max:           CloudCoverPct;
    ndvi_stddev:        CropCycleID;
    stress_level:       CropCycleID;
    cloud_cover_pct:    CloudCoverPct;
    data_quality_score: CloudCoverPct;
    tile_urls:          CropCycleID;
    metadata:           CropCycleID;
    created_at:         CreatedAt;
}

export interface EdAt {
    type:        Type;
    format:      string;
    description: string;
}

export enum Type {
    Integer = "integer",
    Null = "null",
    Number = "number",
    Object = "object",
    String = "string",
}

export interface CloudCoverPct {
    type:        Type[];
    minimum:     number;
    maximum:     number;
    description: string;
}

export interface CreatedAt {
    type:   Type;
    format: string;
}

export interface CropCycleID {
    type:        Type[];
    description: string;
}

export interface FieldID {
    type:        Type;
    description: string;
}

export interface ID {
    type: Type;
}

export interface NdviMean {
    type:        Type;
    minimum:     number;
    maximum:     number;
    description: string;
}

export interface ProcessedAt {
    type:        Type[];
    format:      string;
    description: string;
}

export interface PestDiseaseReport {
    type:                 Type;
    properties:           PestDiseaseReportProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface PestDiseaseReportProperties {
    id:                ID;
    field_id:          FieldID;
    crop_cycle_id:     CropCycleID;
    report_type:       ReportType;
    pest_disease_name: FieldID;
    severity:          ReportType;
    affected_area_pct: NdviMean;
    location_geojson:  CropCycleID;
    observed_at:       EdAt;
    description:       CropCycleID;
    treatment_status:  TreatmentStatus;
    reported_by:       CropCycleID;
    image_urls:        ImageUrls;
    created_at:        CreatedAt;
    updated_at:        TedAt;
}

export interface ImageUrls {
    type:  string[];
    items: ID;
}

export interface ReportType {
    type:        Type;
    enum:        string[];
    description: string;
}

export interface TreatmentStatus {
    type:    Type;
    enum:    string[];
    default: string;
}

export interface TedAt {
    type:   Type[];
    format: string;
}

export interface SoilReading {
    type:                 Type;
    properties:           SoilReadingProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface SoilReadingProperties {
    id:                            ID;
    field_id:                      FieldID;
    location_geojson:              CropCycleID;
    sample_depth_cm:               CropCycleID;
    sample_depth_range:            CropCycleID;
    moisture_pct:                  CloudCoverPct;
    temperature_c:                 CropCycleID;
    ph:                            CloudCoverPct;
    nitrogen_ppm:                  CropCycleID;
    phosphorus_ppm:                CropCycleID;
    potassium_ppm:                 CropCycleID;
    organic_matter_pct:            CloudCoverPct;
    source:                        FieldID;
    lab_name:                      CropCycleID;
    lab_report_url:                CropCycleID;
    recorded_by:                   CropCycleID;
    recorded_at:                   EdAt;
    weather_conditions:            CropCycleID;
    days_since_rain:               CropCycleID;
    cation_exchange_capacity:      CropCycleID;
    electrical_conductivity_ms_cm: CropCycleID;
    texture_analysis:              CropCycleID;
    metadata:                      CropCycleID;
    created_at:                    CreatedAt;
    updated_at:                    TedAt;
    deleted_at:                    TedAt;
}

export interface TreatmentRecommendation {
    type:                 Type;
    properties:           TreatmentRecommendationProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface TreatmentRecommendationProperties {
    id:                          ID;
    report_id:                   FieldID;
    product_name:                FieldID;
    product_type:                FieldID;
    application_method:          FieldID;
    dosage:                      CropCycleID;
    application_timing:          CropCycleID;
    reapplication_interval_days: CropCycleID;
    estimated_cost_usd:          CropCycleID;
    effectiveness_score:         CloudCoverPct;
    notes:                       CropCycleID;
    created_at:                  CreatedAt;
    updated_at:                  TedAt;
}
