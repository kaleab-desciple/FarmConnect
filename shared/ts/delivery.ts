export interface Delivery {
    $schema:              string;
    $id:                  string;
    title:                string;
    type:                 string;
    properties:           Properties;
    required:             string[];
    additionalProperties: boolean;
}

export interface Properties {
    id:                      ID;
    order_id:                OrderID;
    carrier_id:              CarrierID;
    status:                  Status;
    pickup_time:             Time;
    delivered_time:          Time;
    pickup_photo_url:        CarrierID;
    delivery_photo_url:      CarrierID;
    recipient_signature_url: CarrierID;
    notes:                   CarrierID;
    created_at:              CreatedAt;
    updated_at:              UpdatedAt;
}

export interface CarrierID {
    type:        Type[];
    description: string;
}

export enum Type {
    Null = "null",
    String = "string",
}

export interface CreatedAt {
    type:   Type;
    format: string;
}

export interface Time {
    type:        Type[];
    format:      string;
    description: string;
}

export interface ID {
    type: Type;
}

export interface OrderID {
    type:        Type;
    description: string;
}

export interface Status {
    type:        Type;
    enum:        string[];
    default:     string;
    description: string;
}

export interface UpdatedAt {
    type:   Type[];
    format: string;
}
