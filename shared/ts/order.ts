export interface Order {
    $schema:              string;
    $id:                  string;
    title:                string;
    type:                 string;
    required:             string[];
    properties:           Properties;
    additionalProperties: boolean;
}

export interface Properties {
    id:               EscrowID;
    farmer_id:        EscrowID;
    merchant_id:      EscrowID;
    product_id:       EscrowID;
    quantity:         DeliveryFee;
    unit_price:       DeliveryFee;
    delivery_cost:    DeliveryCost;
    platform_fee:     DeliveryCost;
    total_price:      TotalPrice;
    status:           Status;
    escrow_id:        EscrowID;
    created_at:       CreatedAt;
    subtotal:         DeliveryFee;
    delivery_fee:     DeliveryFee;
    delivery_margin:  DeliveryFee;
    quality_fee:      DeliveryFee;
    batch_id:         BatchID;
    cancelled_at:     CancelledAt;
    cancelled_reason: BatchID;
}

export interface BatchID {
    type:        string[];
    description: string;
}

export interface CancelledAt {
    type:        string[];
    format:      string;
    description: string;
}

export interface CreatedAt {
    type:   string;
    format: string;
}

export interface DeliveryCost {
    type:    string;
    minimum: number;
}

export interface DeliveryFee {
    type:             string;
    exclusiveMinimum: number;
}

export interface EscrowID {
    type: string;
}

export interface Status {
    $ref: string;
}

export interface TotalPrice {
    type:             string;
    exclusiveMinimum: number;
    description:      string;
}
