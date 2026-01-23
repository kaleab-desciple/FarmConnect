export interface PricingRule {
    $schema:              string;
    $id:                  string;
    title:                string;
    type:                 string;
    required:             string[];
    properties:           Properties;
    additionalProperties: boolean;
}

export interface Properties {
    id:               FeeValue;
    rule_type:        EType;
    product_category: MaxDistanceKM;
    quality_grade:    MaxDistanceKM;
    region:           MaxDistanceKM;
    min_distance_km:  MaxDistanceKM;
    max_distance_km:  MaxDistanceKM;
    fee_type:         EType;
    fee_value:        FeeValue;
    priority:         FeeValue;
    active:           Active;
    valid_from:       ValidFrom;
    valid_to:         ValidTo;
}

export interface Active {
    type:    string;
    default: boolean;
}

export interface EType {
    $ref: string;
}

export interface FeeValue {
    type: string;
}

export interface MaxDistanceKM {
    type: Type[];
}

export enum Type {
    Null = "null",
    Number = "number",
    String = "string",
}

export interface ValidFrom {
    type:   Type;
    format: string;
}

export interface ValidTo {
    type:   Type[];
    format: string;
}
