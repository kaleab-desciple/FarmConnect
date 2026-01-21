export interface EscrowSchema {
    $schema:              string;
    $id:                  string;
    title:                string;
    type:                 string;
    required:             string[];
    properties:           Properties;
    additionalProperties: boolean;
}

export interface Properties {
    id:              ID;
    order_id:        ID;
    state:           State;
    amount:          Amount;
    penalty_applied: PenaltyApplied;
    provider:        Provider;
    created_at:      AtedAt;
    updated_at:      AtedAt;
}

export interface Amount {
    type:             string;
    exclusiveMinimum: number;
}

export interface AtedAt {
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
