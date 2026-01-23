export interface Account {
    $schema:              string;
    $id:                  string;
    title:                string;
    type:                 string;
    required:             string[];
    properties:           Properties;
    additionalProperties: boolean;
}

export interface Properties {
    id:           ID;
    owner_type:   Type;
    owner_id:     ID;
    account_type: Type;
    name:         ID;
    currency:     Currency;
    created_at:   CreatedAt;
}

export interface Type {
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

export interface ID {
    type: string;
}
