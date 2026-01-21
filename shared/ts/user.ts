export interface User {
    $schema:              string;
    $id:                  string;
    title:                string;
    type:                 string;
    required:             string[];
    properties:           Properties;
    additionalProperties: boolean;
}

export interface Properties {
    id:         ID;
    role:       Role;
    name:       Name;
    email:      Email;
    phone:      Phone;
    created_at: CreatedAt;
    metadata:   Metadata;
}

export interface CreatedAt {
    type:   string;
    format: string;
}

export interface Email {
    type:   string[];
    format: string;
}

export interface ID {
    type: string;
}

export interface Metadata {
    type:                 string;
    additionalProperties: boolean;
}

export interface Name {
    type:      string;
    minLength: number;
}

export interface Phone {
    type: string[];
}

export interface Role {
    $ref: string;
}
