"""Agricultural Intelligence Domain Entities"""
from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field as PydanticField, ConfigDict

from .enums import (
    CropCycleStatus, NDVISource, StressLevel, SoilReadingSource,
    SeverityLevel, RecommendationSource, TaskType, TaskStatus, TaskPriority,
    WeatherSource, RiskType, RiskLevel, AlertType, AlertSeverity,
    AdvisoryStatus, AdvisoryTopic, MessageType
)


# DOMAIN 1: PRECISION CROP & FIELD MANAGEMENT

class Farm(BaseModel):
    """Farm entity"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    farmer_id: str
    name: str
    location_lat: Decimal
    location_lng: Decimal
    location_address: Optional[str] = None
    total_area_ha: Optional[Decimal] = None
    boundary_geom: Optional[dict] = None
    boundary_geojson: Optional[dict] = None
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class Field(BaseModel):
    """Field/Plot entity"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    farm_id: UUID
    name: str
    area_ha: Decimal
    boundary_geom: dict
    boundary_geojson: dict
    centroid_geom: Optional[dict] = None
    soil_type: Optional[str] = None
    soil_classification: Optional[str] = None
    elevation_m: Optional[Decimal] = None
    slope_degree: Optional[Decimal] = None
    irrigation_type: Optional[str] = None
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class CropCycle(BaseModel):
    """Crop cycle entity"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    field_id: UUID
    product_category: str
    crop_name: str
    variety: Optional[str] = None
    cultivar: Optional[str] = None
    planting_date: date
    expected_harvest_date: Optional[date] = None
    actual_harvest_date: Optional[date] = None
    status: CropCycleStatus
    expected_yield_kg: Optional[Decimal] = None
    actual_yield_kg: Optional[Decimal] = None
    seed_source: Optional[str] = None
    planting_density_per_ha: Optional[int] = None
    notes: Optional[str] = None
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class NDVISnapshot(BaseModel):
    """NDVI satellite monitoring snapshot"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    field_id: UUID
    crop_cycle_id: Optional[UUID] = None
    source: NDVISource
    source_metadata: dict = PydanticField(default_factory=dict)
    ndvi_mean: Decimal
    ndvi_min: Optional[Decimal] = None
    ndvi_max: Optional[Decimal] = None
    ndvi_stddev: Optional[Decimal] = None
    stress_level: Optional[StressLevel] = None
    cloud_cover_pct: Optional[Decimal] = None
    captured_at: datetime
    processed_at: datetime
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime


class SoilReading(BaseModel):
    """Soil health reading"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    field_id: UUID
    location_geom: Optional[dict] = None
    depth_cm: Optional[int] = None
    moisture_pct: Optional[Decimal] = None
    temperature_c: Optional[Decimal] = None
    nitrogen_ppm: Optional[Decimal] = None
    phosphorus_ppm: Optional[Decimal] = None
    potassium_ppm: Optional[Decimal] = None
    ph: Optional[Decimal] = None
    organic_matter_pct: Optional[Decimal] = None
    electrical_conductivity: Optional[Decimal] = None
    source: SoilReadingSource
    sensor_id: Optional[str] = None
    lab_name: Optional[str] = None
    recorded_at: datetime
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime


class PestDiseaseReport(BaseModel):
    """Pest and disease report"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    field_id: UUID
    crop_cycle_id: Optional[UUID] = None
    reported_by: str
    location_geom: Optional[dict] = None
    image_urls: List[str] = PydanticField(default_factory=list)
    suspected_issue: str
    issue_type: Optional[str] = None
    scientific_name: Optional[str] = None
    confidence_pct: Optional[Decimal] = None
    severity: Optional[SeverityLevel] = None
    affected_area_ha: Optional[Decimal] = None
    symptoms: Optional[str] = None
    notes: Optional[str] = None
    detected_at: datetime
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class TreatmentRecommendation(BaseModel):
    """Treatment recommendation for pest/disease"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    report_id: UUID
    recommended_by: str
    recommendation_source: RecommendationSource
    description: str
    treatment_type: Optional[str] = None
    chemical_name: Optional[str] = None
    active_ingredient: Optional[str] = None
    dosage: Optional[str] = None
    application_method: Optional[str] = None
    organic: bool = False
    estimated_cost_usd: Optional[Decimal] = None
    effectiveness_rating: Optional[Decimal] = None
    safety_precautions: Optional[str] = None
    withdrawal_period_days: Optional[int] = None
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime
    updated_at: datetime


# DOMAIN 2: PLANNING & OPERATIONAL TOOLS

class FarmTask(BaseModel):
    """Farm task entity"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    field_id: UUID
    crop_cycle_id: Optional[UUID] = None
    task_type: TaskType
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    scheduled_date: date
    scheduled_time: Optional[time] = None
    completed_date: Optional[date] = None
    completed_time: Optional[time] = None
    assigned_to: Optional[str] = None
    estimated_duration_hours: Optional[Decimal] = None
    actual_duration_hours: Optional[Decimal] = None
    estimated_cost_usd: Optional[Decimal] = None
    actual_cost_usd: Optional[Decimal] = None
    labor_count: Optional[int] = None
    equipment_needed: List[str] = PydanticField(default_factory=list)
    materials_needed: Optional[dict] = None
    weather_dependent: bool = False
    notes: Optional[str] = None
    completion_notes: Optional[str] = None
    auto_generated: bool = False
    parent_task_id: Optional[UUID] = None
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class TaskCompletion(BaseModel):
    """Task completion record"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    task_id: UUID
    completed_by: str
    completion_photos: List[str] = PydanticField(default_factory=list)
    quality_rating: Optional[int] = None
    issues_encountered: Optional[str] = None
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime


# DOMAIN 3: RISK MITIGATION & INTELLIGENCE

class WeatherSnapshot(BaseModel):
    """Weather data snapshot"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    field_id: UUID
    source: WeatherSource
    source_station_id: Optional[str] = None
    temperature_c: Optional[Decimal] = None
    feels_like_c: Optional[Decimal] = None
    humidity_pct: Optional[Decimal] = None
    pressure_hpa: Optional[Decimal] = None
    wind_speed_mps: Optional[Decimal] = None
    wind_direction_deg: Optional[int] = None
    wind_gust_mps: Optional[Decimal] = None
    rainfall_mm: Optional[Decimal] = None
    rainfall_intensity: Optional[str] = None
    cloud_cover_pct: Optional[Decimal] = None
    visibility_m: Optional[Decimal] = None
    uv_index: Optional[Decimal] = None
    dew_point_c: Optional[Decimal] = None
    soil_temperature_c: Optional[Decimal] = None
    evapotranspiration_mm: Optional[Decimal] = None
    recorded_at: datetime
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime


class WeatherForecast(BaseModel):
    """Weather forecast"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    field_id: UUID
    source: WeatherSource
    forecast_date: date
    forecast_hour: Optional[int] = None
    temperature_min_c: Optional[Decimal] = None
    temperature_max_c: Optional[Decimal] = None
    precipitation_probability_pct: Optional[Decimal] = None
    precipitation_mm: Optional[Decimal] = None
    wind_speed_max_mps: Optional[Decimal] = None
    humidity_avg_pct: Optional[Decimal] = None
    risk_type: Optional[RiskType] = None
    risk_level: Optional[RiskLevel] = None
    risk_description: Optional[str] = None
    confidence_pct: Optional[Decimal] = None
    issued_at: datetime
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime


class Alert(BaseModel):
    """Alert entity"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: str
    field_id: Optional[UUID] = None
    crop_cycle_id: Optional[UUID] = None
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    action_required: Optional[str] = None
    action_url: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None
    expires_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    dismissed: bool = False
    dismissed_at: Optional[datetime] = None
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime


class AlertAction(BaseModel):
    """Alert action taken"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    alert_id: UUID
    user_id: str
    action_type: str
    action_details: Optional[str] = None
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime


class FieldRiskScore(BaseModel):
    """Field risk score"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    field_id: UUID
    crop_cycle_id: Optional[UUID] = None
    score_date: date
    overall_score: Decimal
    weather_risk_score: Optional[Decimal] = None
    pest_disease_risk_score: Optional[Decimal] = None
    soil_health_score: Optional[Decimal] = None
    crop_health_score: Optional[Decimal] = None
    management_score: Optional[Decimal] = None
    factors: Optional[dict] = None
    recommendations: List[str] = PydanticField(default_factory=list)
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime


# DOMAIN 4: EXPERT ADVISORY & COMMUNITY

class AdvisorySession(BaseModel):
    """Advisory session entity"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    farmer_id: str
    agronomist_id: Optional[str] = None
    field_id: Optional[UUID] = None
    crop_cycle_id: Optional[UUID] = None
    topic: AdvisoryTopic
    title: str
    description: Optional[str] = None
    status: AdvisoryStatus
    priority: TaskPriority
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    rating: Optional[int] = None
    feedback: Optional[str] = None
    tags: List[str] = PydanticField(default_factory=list)
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class AdvisoryMessage(BaseModel):
    """Advisory message"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    session_id: UUID
    sender_id: str
    message_type: MessageType
    message: str
    attachments: Optional[dict] = None
    attachment_urls: List[str] = PydanticField(default_factory=list)
    metadata: dict = PydanticField(default_factory=dict)
    sent_at: datetime
    read_at: Optional[datetime] = None
    edited_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class KnowledgeArticle(BaseModel):
    """Knowledge base article"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    author_id: str
    topic: AdvisoryTopic
    title: str
    content: str
    summary: Optional[str] = None
    tags: List[str] = PydanticField(default_factory=list)
    crop_types: List[str] = PydanticField(default_factory=list)
    region: Optional[str] = None
    language: str = "en"
    view_count: int = 0
    helpful_count: int = 0
    published: bool = False
    published_at: Optional[datetime] = None
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


# INTEGRATION ENTITIES

class CropCycleProduct(BaseModel):
    """Link between crop cycle and product"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    crop_cycle_id: UUID
    product_id: UUID
    quantity_kg: Decimal
    quality_grade: Optional[str] = None
    harvest_date: date
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime


class OrderFieldSource(BaseModel):
    """Link between order and field source"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    order_id: UUID
    field_id: UUID
    crop_cycle_id: Optional[UUID] = None
    quantity_kg: Decimal
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime


class LoanCropCycle(BaseModel):
    """Link between loan and crop cycle"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    loan_id: UUID
    crop_cycle_id: UUID
    allocated_amount_usd: Decimal
    purpose: Optional[str] = None
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime


class EscrowFieldCondition(BaseModel):
    """Escrow condition based on field data"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    escrow_id: UUID
    field_id: UUID
    condition_type: str
    condition_description: str
    threshold_value: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    met: bool = False
    checked_at: Optional[datetime] = None
    metadata: dict = PydanticField(default_factory=dict)
    created_at: datetime
    updated_at: datetime
