export interface Product {
    $schema:              string;
    $id:                  string;
    title:                string;
    description:          string;
    type:                 string;
    required:             string[];
    properties:           ProductProperties;
    additionalProperties: boolean;
}

export interface ProductProperties {
    id:                 FarmerID;
    farmer_id:          FarmerID;
    name:               Name;
    description:        Description;
    category:           Category;
    unit:               Category;
    base_price:         BasePrice;
    currency:           Currency;
    quantity_available: QuantityAvailable;
    quality_grade:      Category;
    harvest_date:       CreatedAt;
    expiry_date:        CreatedAt;
    location:           Location;
    images:             Images;
    is_active:          FarmerID;
    metadata:           Metadata;
    created_at:         CreatedAt;
    updated_at:         CreatedAt;
    total_quantity:     Quantity;
    reserved_quantity:  Quantity;
    sold_quantity:      Quantity;
    spoiled_quantity:   Quantity;
    harvest_id:         CropCycleID;
    crop_cycle_id:      CropCycleID;
    version:            CropCycleID;
    deleted_at:         DeletedAt;
}

export interface BasePrice {
    type:             string;
    exclusiveMinimum: number;
    description:      string;
}

export interface Category {
    $ref: string;
}

export interface CreatedAt {
    type:   string;
    format: string;
}

export interface CropCycleID {
    type:        string[];
    description: string;
}

export interface Currency {
    type:        string;
    default:     string;
    description: string;
}

export interface DeletedAt {
    type:        string[];
    format:      string;
    description: string;
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

export interface QuantityAvailable {
    type:    string;
    minimum: number;
}

export interface Quantity {
    type:        string[];
    minimum:     number;
    description: string;
}
