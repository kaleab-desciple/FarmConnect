export interface Weather {
    $schema:     string;
    $id:         string;
    title:       string;
    definitions: Definitions;
}

export interface Definitions {
    WeatherForecast:  WeatherForecast;
    WeatherSnapshot:  WeatherSnapshot;
    AdvisorySession:  AdvisorySession;
    AdvisoryMessage:  AdvisoryMessage;
    Alert:            Alert;
    FieldRiskScore:   FieldRiskScore;
    KnowledgeArticle: KnowledgeArticle;
}

export interface AdvisoryMessage {
    type:                 Type;
    properties:           AdvisoryMessageProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface AdvisoryMessageProperties {
    id:           ID;
    session_id:   Message;
    sender_id:    Message;
    message_type: MessageType;
    message:      Message;
    attachments:  Attachments;
    sent_at:      At;
    read_at:      At;
    metadata:     Attachments;
}

export interface Attachments {
    type: Type[];
}

export enum Type {
    Integer = "integer",
    Null = "null",
    Number = "number",
    Object = "object",
    String = "string",
}

export interface ID {
    type: Type;
}

export interface Message {
    type:        Type;
    description: string;
}

export interface MessageType {
    type:    Type;
    enum:    string[];
    default: string;
}

export interface At {
    type:   Type[];
    format: string;
}

export interface AdvisorySession {
    type:                 Type;
    properties:           AdvisorySessionProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface AdvisorySessionProperties {
    id:                    ID;
    farmer_id:             Message;
    agronomist_id:         AgronomistID;
    field_id:              AgronomistID;
    crop_cycle_id:         AgronomistID;
    topic:                 Message;
    title:                 Message;
    description:           AgronomistID;
    status:                MessageType;
    priority:              MessageType;
    requested_at:          At;
    scheduled_at:          At;
    started_at:            At;
    closed_at:             At;
    communication_method:  Attachments;
    meeting_link:          Attachments;
    resolution_summary:    Attachments;
    recommendations_given: RecommendationsGiven;
    farmer_rating:         FarmerRating;
    metadata:              Attachments;
    created_at:            CreatedAt;
}

export interface AgronomistID {
    type:        Type[];
    description: string;
}

export interface CreatedAt {
    type:   Type;
    format: string;
}

export interface FarmerRating {
    type:         Type[];
    minimum:      number;
    maximum:      number;
    description?: string;
}

export interface RecommendationsGiven {
    type:  string[];
    items: ID;
}

export interface Alert {
    type:                 Type;
    properties:           AlertProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface AlertProperties {
    id:           ID;
    user_id:      Message;
    field_id:     AgronomistID;
    alert_type:   AlertType;
    severity:     AlertType;
    title:        ID;
    message:      ID;
    acknowledged: Acknowledged;
    metadata:     Attachments;
    created_at:   CreatedAt;
}

export interface Acknowledged {
    type:    string;
    default: boolean;
}

export interface AlertType {
    type: Type;
    enum: string[];
}

export interface FieldRiskScore {
    type:                 Type;
    properties:           FieldRiskScoreProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface FieldRiskScoreProperties {
    id:            ID;
    field_id:      Message;
    crop_cycle_id: AgronomistID;
    score_date:    ScoreDate;
    overall_score: OverallScore;
    risk_trend:    Attachments;
    metadata:      Attachments;
    created_at:    CreatedAt;
}

export interface OverallScore {
    type:        Type;
    minimum:     number;
    maximum:     number;
    description: string;
}

export interface ScoreDate {
    type:        Type;
    format:      string;
    description: string;
}

export interface KnowledgeArticle {
    type:                 Type;
    properties:           KnowledgeArticleProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface KnowledgeArticleProperties {
    id:           ID;
    author_id:    Message;
    topic:        Message;
    title:        Message;
    slug:         AgronomistID;
    summary:      AgronomistID;
    content:      Message;
    status:       MessageType;
    published_at: At;
    metadata:     Attachments;
    created_at:   CreatedAt;
}

export interface WeatherForecast {
    type:                 Type;
    properties:           WeatherForecastProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface WeatherForecastProperties {
    id:                              ID;
    field_id:                        Message;
    source:                          Message;
    forecast_date:                   ScoreDate;
    forecast_hour:                   FarmerRating;
    forecast_horizon_hours:          AgronomistID;
    issued_at:                       ScoreDate;
    temperature_min_c:               AgronomistID;
    temperature_max_c:               AgronomistID;
    temperature_avg_c:               AgronomistID;
    precipitation_probability_pct:   FarmerRating;
    precipitation_mm:                AgronomistID;
    precipitation_type:              AgronomistID;
    wind_speed_max_mps:              AgronomistID;
    wind_direction_deg:              FarmerRating;
    humidity_avg_pct:                FarmerRating;
    pressure_hpa:                    AgronomistID;
    growing_degree_days_accumulated: AgronomistID;
    evapotranspiration_mm:           AgronomistID;
    risk_type:                       AgronomistID;
    risk_level:                      AgronomistID;
    risk_description:                AgronomistID;
    risk_confidence_pct:             FarmerRating;
    metadata:                        AgronomistID;
    created_at:                      CreatedAt;
}

export interface WeatherSnapshot {
    type:                 Type;
    properties:           WeatherSnapshotProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface WeatherSnapshotProperties {
    id:                         ID;
    field_id:                   Message;
    source:                     Message;
    source_station_id:          AgronomistID;
    source_station_distance_km: AgronomistID;
    recorded_at:                ScoreDate;
    temperature_c:              AgronomistID;
    feels_like_c:               AgronomistID;
    humidity_pct:               FarmerRating;
    pressure_hpa:               AgronomistID;
    wind_speed_mps:             AgronomistID;
    wind_direction_deg:         FarmerRating;
    wind_gust_mps:              AgronomistID;
    rainfall_mm:                AgronomistID;
    rainfall_intensity:         AgronomistID;
    snowfall_mm:                AgronomistID;
    cloud_cover_pct:            FarmerRating;
    visibility_m:               AgronomistID;
    uv_index:                   AgronomistID;
    soil_temperature_c:         AgronomistID;
    soil_moisture_pct:          FarmerRating;
    leaf_wetness_hours:         AgronomistID;
    evapotranspiration_mm:      AgronomistID;
    growing_degree_days:        AgronomistID;
    raw_data:                   AgronomistID;
    metadata:                   AgronomistID;
    created_at:                 CreatedAt;
}
