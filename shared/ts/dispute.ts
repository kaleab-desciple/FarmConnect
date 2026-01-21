export interface Dispute {
    $schema:              string;
    $id:                  string;
    title:                string;
    type:                 string;
    required:             string[];
    properties:           Properties;
    additionalProperties: boolean;
}

export interface Properties {
    id:            ID;
    order_id:      ID;
    raised_by:     RaisedBy;
    state:         Resolution;
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

export interface EvidenceUrls {
    type:     string;
    items:    CreatedAt;
    maxItems: number;
}

export interface ID {
    type: string;
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
    $ref: string;
}
