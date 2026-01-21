export interface Enums {
    $schema:     string;
    $id:         string;
    definitions: Definitions;
}

export interface Definitions {
    UserRole:          DisputeResolution;
    OrderStatus:       DisputeResolution;
    EscrowState:       DisputeResolution;
    DisputeState:      DisputeResolution;
    LoanState:         DisputeResolution;
    DisputeResolution: DisputeResolution;
}

export interface DisputeResolution {
    type: string;
    enum: string[];
}
