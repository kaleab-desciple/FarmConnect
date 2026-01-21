export interface DisputeSchema {
    $schema:              string;
    $id:                  string;
    title:                string;
    type:                 string;
    required:             string[];
    properties:           Properties;
    additionalProperties: boolean;
}

export interface Properties {
    id:            EscrowID;
    escrow_id:     EscrowID;
    raised_by:     RaisedBy;
    state:         State;
    reason:        Reason;
    resolution:    Resolution;
    evidence_urls: EvidenceUrls;
    created_at:    CreatedAt;
    resolved_at:   CreatedAt;
}

export interface CreatedAt {
    type:   string;
    format: string;
}

export interface EscrowID {
    type: string;
}

export interface EvidenceUrls {
    type:     string;
    items:    CreatedAt;
    maxItems: number;
}

export interface RaisedBy {
    type:        string;
    description: string;
}

export interface Reason {
    type:      string;
    minLength: number;
    maxLength: number;
}

export interface Resolution {
    type:      string;
    maxLength: number;
}

export interface State {
    $ref: string;
}
