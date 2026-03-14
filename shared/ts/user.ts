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
    id:                  ID;
    keycloak_id:         KeycloakID;
    role:                Role;
    name:                Name;
    email:               Email;
    phone:               KeycloakID;
    created_at:          CreatedAt;
    metadata:            Metadata;
    onboarding_status:   OnboardingStatus;
    onboarding_agent_id: OnboardingAgentID;
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

export interface KeycloakID {
    type: string[];
}

export interface Metadata {
    type:                 string;
    additionalProperties: boolean;
}

export interface Name {
    type:      string;
    minLength: number;
}

export interface OnboardingAgentID {
    type:        string[];
    description: string;
}

export interface OnboardingStatus {
    type:        string[];
    enum:        string[];
    description: string;
}

export interface Role {
    $ref: string;
}
