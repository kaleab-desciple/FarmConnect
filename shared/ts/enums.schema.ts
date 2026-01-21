export interface EnumsSchema {
    $schema:     string;
    $id:         string;
    definitions: Definitions;
}

export interface Definitions {
    UserRole:     DisputeState;
    OrderStatus:  DisputeState;
    EscrowState:  DisputeState;
    DisputeState: DisputeState;
    LoanState:    DisputeState;
}

export interface DisputeState {
    type: string;
    enum: string[];
}
