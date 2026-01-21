export interface Loan {
    $schema:              string;
    $id:                  string;
    title:                string;
    type:                 string;
    required:             string[];
    properties:           LoanProperties;
    additionalProperties: boolean;
}

export interface LoanProperties {
    id:                 FarmerID;
    farmer_id:          FarmerID;
    principal:          Principal;
    interest_rate:      InterestRate;
    state:              State;
    auto_approved:      AutoApproved;
    repayment_schedule: RepaymentSchedule;
    created_at:         ClosedAt;
    closed_at:          ClosedAt;
}

export interface AutoApproved {
    type:    string;
    default: boolean;
}

export interface ClosedAt {
    type:   string;
    format: string;
}

export interface FarmerID {
    type: string;
}

export interface InterestRate {
    type:    string;
    minimum: number;
}

export interface Principal {
    type:             string;
    exclusiveMinimum: number;
}

export interface RepaymentSchedule {
    type:  string;
    items: Items;
}

export interface Items {
    type:       string;
    required:   string[];
    properties: ItemsProperties;
}

export interface ItemsProperties {
    due_date: ClosedAt;
    amount:   Principal;
}

export interface State {
    $ref: string;
}
