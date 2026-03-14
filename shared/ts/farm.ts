export interface Farm {
    $schema:     string;
    $id:         string;
    title:       string;
    definitions: Definitions;
}

export interface Definitions {
    Farm:      FarmClass;
    Field:     Field;
    CropCycle: CropCycle;
}

export interface CropCycle {
    type:                 Type;
    properties:           CropCycleProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface CropCycleProperties {
    id:                      CreatedAt;
    field_id:                FieldID;
    product_category:        CropName;
    crop_name:               CropName;
    variety:                 ActualYieldKg;
    cultivar:                ActualYieldKg;
    planting_date:           FieldID;
    expected_harvest_date:   HarvestDate;
    actual_harvest_date:     HarvestDate;
    status:                  CropName;
    expected_yield_kg:       ActualYieldKg;
    actual_yield_kg:         ActualYieldKg;
    yield_quality_grade:     ActualYieldKg;
    seed_source:             ActualYieldKg;
    planting_density_per_ha: ActualYieldKg;
    seed_cost_usd:           ActualYieldKg;
    notes:                   ActualYieldKg;
    metadata:                ActualYieldKg;
    created_at:              CreatedAt;
    updated_at:              CreatedAt;
    deleted_at:              DeletedAt;
}

export interface HarvestDate {
    type:        Type[];
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

export interface ActualYieldKg {
    type:        Type[];
    description: string;
}

export interface CreatedAt {
    type:   Type;
    format: string;
}

export interface CropName {
    type:        Type;
    description: string;
}

export interface DeletedAt {
    type:   Type[];
    format: string;
}

export interface FieldID {
    type:        Type;
    format:      string;
    description: string;
}

export interface FarmClass {
    type:                 Type;
    properties:           FarmProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface FarmProperties {
    id:               CreatedAt;
    farmer_id:        CropName;
    name:             Name;
    location_lat:     LocationL;
    location_lng:     LocationL;
    location_address: ActualYieldKg;
    total_area_ha:    ActualYieldKg;
    boundary_geojson: ActualYieldKg;
    centroid_geojson: ActualYieldKg;
    metadata:         ActualYieldKg;
    created_at:       CreatedAt;
    updated_at:       CreatedAt;
    deleted_at:       DeletedAt;
}

export interface LocationL {
    type:        Type;
    minimum:     number;
    maximum:     number;
    description: string;
}

export interface Name {
    type:        Type;
    minLength:   number;
    maxLength:   number;
    description: string;
}

export interface Field {
    type:                 Type;
    properties:           FieldProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface FieldProperties {
    id:                  CreatedAt;
    farm_id:             FieldID;
    name:                Name;
    area_ha:             CropName;
    boundary_geojson:    CropName;
    centroid_geojson:    ActualYieldKg;
    soil_type:           ActualYieldKg;
    soil_classification: ActualYieldKg;
    elevation_m:         ActualYieldKg;
    slope_degree:        SlopeDegree;
    irrigation_type:     ActualYieldKg;
    drainage_type:       ActualYieldKg;
    metadata:            ActualYieldKg;
    created_at:          CreatedAt;
    updated_at:          CreatedAt;
    deleted_at:          DeletedAt;
}

export interface SlopeDegree {
    type:        Type[];
    minimum:     number;
    maximum:     number;
    description: string;
}
