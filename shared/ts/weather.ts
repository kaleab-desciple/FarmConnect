// FarmConnect Weather Types - Mirroring Python DTOs from shared_models
import { WeatherSource, RiskType, RiskLevel, AlertType, AlertSeverity } from "./enums";

/**
 * Weather forecast base model
 */
export interface WeatherForecastBase {
  field_id: string;
  source: WeatherSource;
  forecast_date: string;
  forecast_hour?: number;
  forecast_horizon_hours?: number;
  issued_at: string;
  temperature_min_c?: number;
  temperature_max_c?: number;
  temperature_avg_c?: number;
  precipitation_probability_pct?: number;
  precipitation_mm?: number;
  precipitation_type?: string;
  wind_speed_max_mps?: number;
  wind_direction_deg?: number;
  humidity_avg_pct?: number;
  pressure_hpa?: number;
  growing_degree_days_accumulated?: number;
  evapotranspiration_mm?: number;
  risk_type: RiskType;
  risk_level: RiskLevel;
  risk_description?: string;
  risk_confidence_pct?: number;
  metadata?: Record<string, unknown>;
}

/**
 * Weather forecast response model
 */
export interface WeatherForecast extends WeatherForecastBase {
  id: string;
  created_at: string;
}

/**
 * Weather forecast creation request
 */
export interface WeatherForecastCreate extends WeatherForecastBase {}

/**
 * Weather snapshot base model
 */
export interface WeatherSnapshotBase {
  field_id: string;
  source: WeatherSource;
  source_station_id?: string;
  source_station_distance_km?: number;
  recorded_at: string;
  temperature_c?: number;
  feels_like_c?: number;
  humidity_pct?: number;
  pressure_hpa?: number;
  wind_speed_mps?: number;
  wind_direction_deg?: number;
  wind_gust_mps?: number;
  rainfall_mm?: number;
  rainfall_intensity?: string;
  snowfall_mm?: number;
  cloud_cover_pct?: number;
  visibility_m?: number;
  uv_index?: number;
  soil_temperature_c?: number;
  soil_moisture_pct?: number;
  leaf_wetness_hours?: number;
  evapotranspiration_mm?: number;
  growing_degree_days?: number;
  raw_data?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

/**
 * Weather snapshot response model
 */
export interface WeatherSnapshot extends WeatherSnapshotBase {
  id: string;
  created_at: string;
}

/**
 * Weather snapshot creation request
 */
export interface WeatherSnapshotCreate extends WeatherSnapshotBase {}

// ============ Alert Types ============

/**
 * Base alert model
 */
export interface AlertBase {
  user_id: string;
  field_id?: string;
  alert_type: AlertType;
  severity: AlertSeverity;
  title: string;
  message: string;
  acknowledged?: boolean;
  metadata?: Record<string, unknown>;
}

/**
 * Alert response model
 */
export interface Alert extends AlertBase {
  id: string;
  created_at: string;
}

/**
 * Alert creation request
 */
export interface AlertCreate extends AlertBase {}

/**
 * Alert update request
 */
export interface AlertUpdate {
  acknowledged?: boolean;
  metadata?: Record<string, unknown>;
}

/**
 * Paginated alert list response
 */
export interface AlertListResponse {
  alerts: Alert[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ============ Field Risk Score Types ============

/**
 * Field risk score model
 */
export interface FieldRiskScore {
  id: string;
  field_id: string;
  crop_cycle_id?: string;
  score_date: string;
  overall_score: number;
  risk_trend?: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

/**
 * Field risk score creation request
 */
export interface FieldRiskScoreCreate {
  field_id: string;
  crop_cycle_id?: string;
  score_date: string;
  overall_score: number;
  risk_trend?: string;
  metadata?: Record<string, unknown>;
}
