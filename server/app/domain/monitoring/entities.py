"""Soil and monitoring domain entities for agricultural management."""
from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, List, Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class SoilReadingBase(BaseModel):
    """Base Soil Reading entity."""
    field_id: UUID
    location_geojson: Optional[dict] = None
    sample_depth_cm: Optional[int] = Field(None, gt=0)
    sample_depth_range: Optional[str] = None
    moisture_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    temperature_c: Optional[Decimal] = None
    ph: Optional[Decimal] = Field(None, ge=0, le=14)
    nitrogen_ppm: Optional[Decimal] = None
    phosphorus_ppm: Optional[Decimal] = None
    potassium_ppm: Optional[Decimal] = None
    organic_matter_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    cation_exchange_capacity: Optional[Decimal] = None
    electrical_conductivity_ms_cm: Optional[Decimal] = None
    texture_analysis: Optional[dict] = None
    source: Literal['IOT_SENSOR', 'MANUAL_TEST', 'LAB_ANALYSIS', 'ESTIMATED']
    lab_name: Optional[str] = None
    lab_report_url: Optional[str] = None
    recorded_by: Optional[str] = None
    recorded_at: datetime
    weather_conditions: Optional[str] = None
    days_since_rain: Optional[int] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class SoilReadingCreate(SoilReadingBase):
    """Soil Reading creation entity."""
    pass


class SoilReadingUpdate(BaseModel):
    """Soil Reading update entity."""
    location_geojson: Optional[dict] = None
    sample_depth_cm: Optional[int] = Field(None, gt=0)
    sample_depth_range: Optional[str] = None
    moisture_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    temperature_c: Optional[Decimal] = None
    ph: Optional[Decimal] = Field(None, ge=0, le=14)
    nitrogen_ppm: Optional[Decimal] = None
    phosphorus_ppm: Optional[Decimal] = None
    potassium_ppm: Optional[Decimal] = None
    organic_matter_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    cation_exchange_capacity: Optional[Decimal] = None
    electrical_conductivity_ms_cm: Optional[Decimal] = None
    texture_analysis: Optional[dict] = None
    source: Optional[Literal['IOT_SENSOR', 'MANUAL_TEST', 'LAB_ANALYSIS', 'ESTIMATED']] = None
    lab_name: Optional[str] = None
    lab_report_url: Optional[str] = None
    recorded_by: Optional[str] = None
    recorded_at: Optional[datetime] = None
    weather_conditions: Optional[str] = None
    days_since_rain: Optional[int] = None
    metadata: Optional[dict] = None


class SoilReading(SoilReadingBase):
    """Soil Reading domain entity with full fields."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class NDVISnapshotBase(BaseModel):
    """Base NDVI Snapshot entity."""
    field_id: UUID
    crop_cycle_id: Optional[UUID] = None
    source: Literal['SENTINEL_2', 'LANDSAT_8', 'LANDSAT_9', 'MODIS', 'MANUAL']
    source_metadata: Optional[dict] = None
    captured_at: datetime
    processed_at: Optional[datetime] = None
    ndvi_mean: Decimal = Field(..., ge=-1, le=1)
    ndvi_min: Optional[Decimal] = Field(None, ge=-1, le=1)
    ndvi_max: Optional[Decimal] = Field(None, ge=-1, le=1)
    ndvi_stddev: Optional[Decimal] = None
    stress_level: Optional[Literal['NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']] = None
    cloud_cover_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    data_quality_score: Optional[Decimal] = Field(None, ge=0, le=1)
    tile_urls: Optional[dict] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class NDVISnapshotCreate(NDVISnapshotBase):
    """NDVI Snapshot creation entity."""
    pass


class NDVISnapshotUpdate(BaseModel):
    """NDVI Snapshot update entity."""
    crop_cycle_id: Optional[UUID] = None
    processed_at: Optional[datetime] = None
    ndvi_mean: Optional[Decimal] = Field(None, ge=-1, le=1)
    ndvi_min: Optional[Decimal] = Field(None, ge=-1, le=1)
    ndvi_max: Optional[Decimal] = Field(None, ge=-1, le=1)
    ndvi_stddev: Optional[Decimal] = None
    stress_level: Optional[Literal['NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']] = None
    cloud_cover_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    data_quality_score: Optional[Decimal] = Field(None, ge=0, le=1)
    tile_urls: Optional[dict] = None
    metadata: Optional[dict] = None


class NDVISnapshot(NDVISnapshotBase):
    """NDVI Snapshot domain entity with full fields."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class PestDiseaseReportBase(BaseModel):
    """Base Pest/Disease Report entity."""
    field_id: UUID
    crop_cycle_id: Optional[UUID] = None
    reported_by: str
    location_geojson: Optional[dict] = None
    image_urls: Optional[List[str]] = None
    drone_flight_id: Optional[UUID] = None
    suspected_issue: str
    issue_type: Optional[str] = None
    scientific_name: Optional[str] = None
    common_names: Optional[List[str]] = None
    ai_diagnosis_id: Optional[UUID] = None
    confidence_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    severity: Optional[Literal['TRACE', 'LOW', 'MEDIUM', 'HIGH', 'SEVERE']] = None
    affected_area_ha: Optional[Decimal] = Field(None, gt=0)
    affected_plant_count: Optional[int] = None
    symptoms: Optional[str] = None
    spread_pattern: Optional[str] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
    first_observed_date: Optional[date] = None
    detected_at: datetime
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class PestDiseaseReportCreate(PestDiseaseReportBase):
    """Pest/Disease Report creation entity."""
    pass


class PestDiseaseReportUpdate(BaseModel):
    """Pest/Disease Report update entity."""
    issue_type: Optional[str] = None
    scientific_name: Optional[str] = None
    common_names: Optional[List[str]] = None
    confidence_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    severity: Optional[Literal['TRACE', 'LOW', 'MEDIUM', 'HIGH', 'SEVERE']] = None
    affected_area_ha: Optional[Decimal] = Field(None, gt=0)
    affected_plant_count: Optional[int] = None
    symptoms: Optional[str] = None
    spread_pattern: Optional[str] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
    metadata: Optional[dict] = None


class PestDiseaseReport(PestDiseaseReportBase):
    """Pest/Disease Report domain entity with full fields."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TreatmentRecommendationBase(BaseModel):
    """Base Treatment Recommendation entity."""
    report_id: UUID
    recommended_by: str
    recommendation_source: Literal['AGRONOMIST', 'SYSTEM', 'AI_MODEL', 'COMMUNITY']
    description: str
    treatment_type: Optional[str] = None
    chemical_name: Optional[str] = None
    active_ingredient: Optional[str] = None
    formulation: Optional[str] = None
    dosage_per_ha: Optional[str] = None
    application_method: Optional[str] = None
    application_timing: Optional[str] = None
    organic: bool = False
    restricted_use: bool = False
    required_ppe: Optional[List[str]] = None
    reentry_interval_hours: Optional[int] = None
    pre_harvest_interval_days: Optional[int] = None
    withdrawal_period_days: Optional[int] = None
    estimated_cost_per_ha_usd: Optional[Decimal] = None
    effectiveness_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    expected_results_days: Optional[int] = None
    accepted_by_farmer: Optional[bool] = None
    accepted_at: Optional[datetime] = None
    applied: bool = False
    applied_at: Optional[datetime] = None
    application_notes: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class TreatmentRecommendationCreate(TreatmentRecommendationBase):
    """Treatment Recommendation creation entity."""
    pass


class TreatmentRecommendationUpdate(BaseModel):
    """Treatment Recommendation update entity."""
    accepted_by_farmer: Optional[bool] = None
    accepted_at: Optional[datetime] = None
    applied: Optional[bool] = None
    applied_at: Optional[datetime] = None
    application_notes: Optional[str] = None
    metadata: Optional[dict] = None


class TreatmentRecommendation(TreatmentRecommendationBase):
    """Treatment Recommendation domain entity with full fields."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
