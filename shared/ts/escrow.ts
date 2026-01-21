export interface Escrow {
    $schema:              string;
    $id:                  string;
    title:                string;
    type:                 string;
    required:             string[];
    properties:           Properties;
    additionalProperties: boolean;
}

export interface Properties {
    id:                 ID;
    order_id:           ID;
    state:              State;
    amount:             Amount;
    penalty_applied:    PenaltyApplied;
    provider:           Provider;
    created_at:         EdAt;
    updated_at:         EdAt;
    funded_at:          EdAt;
    released_at:        EdAt;
    provider_reference: ID;
}

export interface Amount {
    type:             string;
    exclusiveMinimum: number;
}

export interface EdAt {
    type:   string;
    format: string;
}

export interface ID {
    type: string;
}

export interface PenaltyApplied {
    type:    string;
    default: boolean;
}

export interface Provider {
    type: string;
    enum: string[];
}

export interface State {
    $ref: string;
}
