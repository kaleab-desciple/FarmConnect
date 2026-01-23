export interface JournalLine {
    $schema:              string;
    $id:                  string;
    title:                string;
    type:                 string;
    required:             string[];
    properties:           Properties;
    additionalProperties: boolean;
}

export interface Properties {
    id:               AccountID;
    journal_entry_id: AccountID;
    account_id:       AccountID;
    debit_amount:     ItAmount;
    credit_amount:    ItAmount;
}

export interface AccountID {
    type: string;
}

export interface ItAmount {
    type:    string;
    default: number;
}
