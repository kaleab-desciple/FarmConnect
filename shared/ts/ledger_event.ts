export interface LedgerEvent {
    $schema:              string;
    $id:                  string;
    title:                string;
    type:                 string;
    required:             string[];
    properties:           Properties;
    additionalProperties: boolean;
}

export interface Properties {
    id:             AggregateID;
    aggregate_type: AggregateType;
    aggregate_id:   AggregateID;
    event_type:     AggregateType;
    amount:         AggregateID;
    currency:       Currency;
    direction:      AggregateType;
    reference_type: AggregateType;
    reference_id:   AggregateID;
    event_metadata: EventMetadata;
    created_at:     CreatedAt;
}

export interface AggregateID {
    type: string;
}

export interface AggregateType {
    $ref: string;
}

export interface CreatedAt {
    type:   string;
    format: string;
}

export interface Currency {
    type:    string;
    default: string;
}

export interface EventMetadata {
    type:                 string;
    additionalProperties: boolean;
}
