export interface Enums {
    $schema:     string;
    $id:         string;
    definitions: { [key: string]: Definition };
}

export interface Definition {
    type: Type;
    enum: string[];
}

export enum Type {
    String = "string",
}
