export interface Reputation {
    $schema:              string;
    $id:                  string;
    title:                string;
    type:                 string;
    required:             string[];
    properties:           Properties;
    additionalProperties: boolean;
}

export interface Properties {
    user_id:            UserID;
    completed_orders:   CompletedOrders;
    successful_orders:  CompletedOrders;
    disputes_lost:      CompletedOrders;
    penalties_total:    CompletedOrders;
    avg_delivery_delay: AvgDeliveryDelay;
    reputation_score:   ReputationScore;
}

export interface AvgDeliveryDelay {
    type:     string;
    nullable: boolean;
}

export interface CompletedOrders {
    type:    string;
    default: number;
}

export interface ReputationScore {
    type:    string;
    minimum: number;
    maximum: number;
    default: number;
}

export interface UserID {
    type: string;
}
