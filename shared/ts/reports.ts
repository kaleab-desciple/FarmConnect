export interface Reports {
    $schema:     string;
    $id:         string;
    title:       string;
    definitions: Definitions;
}

export interface Definitions {
    BalanceSheet:     BalanceSheet;
    ProfitLoss:       ProfitLoss;
    CashFlow:         CashFlow;
    FinancialSummary: FinancialSummary;
}

export interface BalanceSheet {
    type:                 string;
    properties:           BalanceSheetProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface BalanceSheetProperties {
    as_of:       AsOf;
    assets:      Assets;
    liabilities: Assets;
    equity:      Assets;
}

export interface AsOf {
    type:        string;
    format:      string;
    description: string;
}

export interface Assets {
    type:                 string;
    additionalProperties: AdditionalProperties;
    description:          string;
}

export interface AdditionalProperties {
    type: string;
}

export interface CashFlow {
    type:                 string;
    properties:           CashFlowProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface CashFlowProperties {
    from_date: AsOf;
    to_date:   AsOf;
    operating: Assets;
    investing: Assets;
    financing: Assets;
}

export interface FinancialSummary {
    type:                 string;
    properties:           FinancialSummaryProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface FinancialSummaryProperties {
    period_start:      AsOf;
    period_end:        AsOf;
    total_revenue:     NetCashFlow;
    total_expenses:    NetCashFlow;
    net_profit:        NetCashFlow;
    total_assets:      NetCashFlow;
    total_liabilities: NetCashFlow;
    total_equity:      NetCashFlow;
    net_cash_flow:     NetCashFlow;
}

export interface NetCashFlow {
    type:        string;
    description: string;
}

export interface ProfitLoss {
    type:                 string;
    properties:           ProfitLossProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface ProfitLossProperties {
    from_date: AsOf;
    to_date:   AsOf;
    revenue:   Assets;
    expenses:  Assets;
}
