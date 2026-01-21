export interface ProductSchema {
    $schema:              string;
    $id:                  string;
    title:                string;
    description:          string;
    type:                 string;
    required:             string[];
    properties:           ProductSchemaProperties;
    additionalProperties: boolean;
}

export interface ProductSchemaProperties {
    id:                 FarmerID;
    farmer_id:          FarmerID;
    name:               Name;
    description:        Description;
    category:           Category;
    unit:               QualityGrade;
    base_price:         BasePrice;
    currency:           Currency;
    quantity_available: QuantityAvailable;
    quality_grade:      QualityGrade;
    harvest_date:       CreatedAt;
    expiry_date:        CreatedAt;
    location:           Location;
    images:             Images;
    is_active:          FarmerID;
    metadata:           Metadata;
    created_at:         CreatedAt;
    updated_at:         CreatedAt;
}

export interface BasePrice {
    type:             string;
    exclusiveMinimum: number;
    description:      string;
}

export interface Category {
    type: string;
    enum: string[];
}

export interface CreatedAt {
    type:   string;
    format: string;
}

export interface Currency {
    type:    string;
    pattern: string;
    default: string;
}

export interface Description {
    type:      string;
    maxLength: number;
}

export interface FarmerID {
    type:        string;
    description: string;
}

export interface Images {
    type:     string;
    items:    CreatedAt;
    maxItems: number;
}

export interface Location {
    type:        string;
    required:    string[];
    properties:  LocationProperties;
    description: string;
}

export interface LocationProperties {
    latitude:  Itude;
    longitude: Itude;
}

export interface Itude {
    type:    string;
    minimum: number;
    maximum: number;
}

export interface Metadata {
    type:                 string;
    additionalProperties: boolean;
    description:          string;
}

export interface Name {
    type:      string;
    minLength: number;
    maxLength: number;
}

export interface QualityGrade {
    type:        string;
    enum:        string[];
    description: string;
}

export interface QuantityAvailable {
    type:    string;
    minimum: number;
}
