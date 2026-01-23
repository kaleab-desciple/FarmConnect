export interface JournalEntry {
    $schema:              string;
    $id:                  string;
    title:                string;
    type:                 string;
    required:             string[];
    properties:           Properties;
    additionalProperties: boolean;
}

export interface Properties {
    id:             Description;
    reference_type: Description;
    reference_id:   Description;
    description:    Description;
    created_at:     CreatedAt;
}

export interface CreatedAt {
    type:   string;
    format: string;
}

export interface Description {
    type: string;
}
