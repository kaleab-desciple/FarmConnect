export interface Earnings {
    $schema:    string;
    title:      string;
    type:       string;
    properties: Properties;
    required:   string[];
}

export interface Properties {
    farmer_id:      FarmerID;
    total_earnings: TotalEarnings;
    period:         Period;
}

export interface FarmerID {
    type:   string;
    format: string;
}

export interface Period {
    type: string;
    enum: string[];
}

export interface TotalEarnings {
    type: string;
}
