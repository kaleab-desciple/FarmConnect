"""
Monitoring Shared Models - DTOs
Monitoring Service - Farm Connect AgriManagement
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field as PydanticField, ConfigDict


# ============ Soil Reading DTOs ============

class SoilReadingBase(BaseModel):
    """Base soil reading model"""
    field_id: str = PydanticField(..., description="ID of the field")
    location_geojson: Optional[Dict[str, Any]] = PydanticField(None, description="Location as GeoJSON")
    sample_depth_cm: Optional[int] = PydanticField(None, gt=0, description="Sample depth in cm")
    sample_depth_range: Optional[str] = PydanticField(None, description="Sample depth range description")
    moisture_pct: Optional[float] = PydanticField(None, ge=0, le=100, description="Moisture percentage")
    temperature_c: Optional[float] = PydanticField(None, description="Temperature in Celsius")
    ph: Optional[float] = PydanticField(None, ge=0, le=14, description="pH level")
    nitrogen_ppm: Optional[float] = PydanticField(None, description="Nitrogen in ppm")
    phosphorus_ppm: Optional[float] = PydanticField(None, description="Phosphorus in ppm")
    potassium_ppm: Optional[float] = PydanticField(None, description="Potassium in ppm")
    organic_matter_pct: Optional[float] = PydanticField(None, ge=0, le=100, description="Organic matter percentage")
    source: str = PydanticField(default="MANUAL_TEST", description="Data source")
    lab_name: Optional[str] = PydanticField(None, description="Lab name for analysis")
    lab_report_url: Optional[str] = PydanticField(None, description="Lab report URL")
    recorded_by: Optional[str] = PydanticField(None, description="Recorded by user")
    recorded_at: datetime = PydanticField(default_factory=datetime.utcnow, description="Recording timestamp")
    weather_conditions: Optional[str] = PydanticField(None, description="Weather conditions")
    days_since_rain: Optional[int] = PydanticField(None, ge=0, description="Days since last rain")


class SoilReadingCreate(SoilReadingBase):
    """Soil reading creation model"""
    pass


class SoilReadingUpdate(BaseModel):
    """Soil reading update model"""
    location_geojson: Optional[Dict[str, Any]] = None
    sample_depth_cm: Optional[int] = PydanticField(None, gt=0)
    sample_depth_range: Optional[str] = None
    moisture_pct: Optional[float] = PydanticField(None, ge=0, le=100)
    temperature_c: Optional[float] = None
    ph: Optional[float] = PydanticField(None, ge=0, le=14)
    nitrogen_ppm: Optional[float] = None
    phosphorus_ppm: Optional[float] = None
    potassium_ppm: Optional[float] = None
    organic_matter_pct: Optional[float] = PydanticField(None, ge=0, le=100)
    source: Optional[str] = None
    lab_name: Optional[str] = None
    lab_report_url: Optional[str] = None
    recorded_by: Optional[str] = None
    recorded_at: Optional[datetime] = None
    weather_conditions: Optional[str] = None
    days_since_rain: Optional[int] = PydanticField(None, ge=0)
    metadata: Optional[Dict[str, Any]] = None


class SoilReading(SoilReadingBase):
    """Soil reading response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


# ============ NDVI Snapshot DTOs ============

class NDVISnapshotBase(BaseModel):
    """Base NDVI snapshot model"""
    field_id: str = PydanticField(..., description="ID of the field")
    crop_cycle_id: Optional[str] = PydanticField(None, description="ID of the crop cycle")
    source: str = PydanticField(default="MANUAL", description="Data source")
    source_metadata: Optional[Dict[str, Any]] = PydanticField(None, description="Source metadata")
    captured_at: datetime = PydanticField(..., description="Capture timestamp")
    processed_at: Optional[datetime] = PydanticField(None, description="Processing timestamp")
    ndvi_mean: float = PydanticField(..., ge=-1, le=1, description="Mean NDVI value")
    ndvi_min: Optional[float] = PydanticField(None, ge=-1, le=1, description="Min NDVI value")
    ndvi_max: Optional[float] = PydanticField(None, ge=-1, le=1, description="Max NDVI value")
    ndvi_stddev: Optional[float] = PydanticField(None, description="NDVI standard deviation")
    stress_level: Optional[str] = PydanticField(None, description="Stress level")
    cloud_cover_pct: Optional[float] = PydanticField(None, ge=0, le=100, description="Cloud cover percentage")
    data_quality_score: Optional[float] = PydanticField(None, ge=0, le=1, description="Data quality score")
    tile_urls: Optional[Dict[str, Any]] = PydanticField(None, description="Tile URLs for imagery")
    metadata: Optional[Dict[str, Any]] = PydanticField(None, description="Additional metadata")


class NDVISnapshotCreate(NDVISnapshotBase):
    """NDVI snapshot creation model"""
    pass


class NDVISnapshotUpdate(BaseModel):
    """NDVI snapshot update model"""
    source_metadata: Optional[Dict[str, Any]] = None
    processed_at: Optional[datetime] = None
    ndvi_mean: Optional[float] = PydanticField(None, ge=-1, le=1)
    ndvi_min: Optional[float] = PydanticField(None, ge=-1, le=1)
    ndvi_max: Optional[float] = PydanticField(None, ge=-1, le=1)
    ndvi_stddev: Optional[float] = None
    stress_level: Optional[str] = None
    cloud_cover_pct: Optional[float] = PydanticField(None, ge=0, le=100)
    data_quality_score: Optional[float] = PydanticField(None, ge=0, le=1)
    tile_urls: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class NDVISnapshot(NDVISnapshotBase):
    """NDVI snapshot response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    created_at: datetime


# ============ Pest/Disease Report DTOs ============

class PestDiseaseReportBase(BaseModel):
    """Base pest/disease report model"""
    field_id: str = PydanticField(..., description="ID of the field")
    crop_cycle_id: Optional[str] = PydanticField(None, description="ID of the crop cycle")
    report_type: str = PydanticField(..., description="Report type: PEST or DISEASE")
    pest_disease_name: str = PydanticField(..., description="Name of pest or disease")
    severity: str = PydanticField(..., description="Severity level")
    affected_area_pct: float = PydanticField(..., ge=0, le=100, description="Affected area percentage")
    location_geojson: Optional[Dict[str, Any]] = PydanticField(None, description="Location as GeoJSON")
    observed_at: datetime = PydanticField(..., description="Observation timestamp")
    description: Optional[str] = PydanticField(None, description="Description")
    treatment_status: str = PydanticField(default="REPORTED", description="Treatment status")
    reported_by: Optional[str] = PydanticField(None, description="Reported by")
    image_urls: Optional[List[str]] = PydanticField(default_factory=list, description="Image URLs")


class PestDiseaseReportCreate(PestDiseaseReportBase):
    """Pest/disease report creation model"""
    pass


class PestDiseaseReportUpdate(BaseModel):
    """Pest/disease report update model"""
    severity: Optional[str] = None
    affected_area_pct: Optional[float] = PydanticField(None, ge=0, le=100)
    location_geojson: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    treatment_status: Optional[str] = None
    image_urls: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class PestDiseaseReport(PestDiseaseReportBase):
    """Pest/disease report response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


# ============ Treatment Recommendation DTOs ============

class TreatmentRecommendationBase(BaseModel):
    """Base treatment recommendation model"""
    report_id: str = PydanticField(..., description="ID of the pest/disease report")
    product_name: str = PydanticField(..., description="Product/recommendation name")
    product_type: str = PydanticField(..., description="Product type")
    application_method: str = PydanticField(..., description="Application method")
    dosage: Optional[str] = PydanticField(None, description="Dosage")
    application_timing: Optional[str] = PydanticField(None, description="Application timing")
    reapplication_interval_days: Optional[int] = PydanticField(None, ge=0, description="Reapplication interval in days")
    estimated_cost_usd: Optional[float] = PydanticField(None, ge=0, description="Estimated cost in USD")
    effectiveness_score: Optional[float] = PydanticField(None, ge=0, le=1, description="Effectiveness score")
    notes: Optional[str] = PydanticField(None, description="Additional notes")


class TreatmentRecommendationCreate(TreatmentRecommendationBase):
    """Treatment recommendation creation model"""
    pass


class TreatmentRecommendationUpdate(BaseModel):
    """Treatment recommendation update model"""
    product_name: Optional[str] = None
    product_type: Optional[str] = None
    application_method: Optional[str] = None
    dosage: Optional[str] = None
    application_timing: Optional[str] = None
    reapplication_interval_days: Optional[int] = PydanticField(None, ge=0)
    estimated_cost_usd: Optional[float] = PydanticField(None, ge=0)
    effectiveness_score: Optional[float] = PydanticField(None, ge=0, le=1)
    notes: Optional[str] = None


class TreatmentRecommendation(TreatmentRecommendationBase):
    """Treatment recommendation response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


# ============ Enums (for reference) ============

class SoilReadingSource:
    """Soil reading source constants"""
    IOT_SENSOR = "IOT_SENSOR"
    MANUAL_TEST = "MANUAL_TEST"
    LAB_ANALYSIS = "LAB_ANALYSIS"
    ESTIMATED = "ESTIMATED"


class NDVISource:
    """NDVI source constants"""
    SENTINEL_2 = "SENTINEL_2"
    LANDSAT_8 = "LANDSAT_8"
    LANDSAT_9 = "LANDSAT_9"
    MODIS = "MODIS"
    MANUAL = "MANUAL"


class StressLevel:
    """Stress level constants"""
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ReportType:
    """Report type constants"""
    PEST = "PEST"
    DISEASE = "DISEASE"


class Severity:
    """Severity constants"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TreatmentStatus:
    """Treatment status constants"""
    REPORTED = "REPORTED"
    TREATMENT_RECOMMENDED = "TREATMENT_RECOMMENDED"
    TREATMENT_APPLIED = "TREATMENT_APPLIED"
    RESOLVED = "RESOLVED"
    NO_ACTION = "NO_ACTION"
