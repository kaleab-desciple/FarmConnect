"""
Farm Shared Models - DTOs
Farm Service - Farm Connect AgriManagement
"""
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field as PydanticField, ConfigDict


# ============ Farm DTOs ============

class FarmBase(BaseModel):
    """Base farm model"""
    farmer_id: str = PydanticField(..., description="ID of the farmer who owns the farm")
    name: str = PydanticField(..., min_length=1, max_length=200, description="Farm name")
    location_lat: Decimal = PydanticField(..., ge=-90, le=90, description="Latitude coordinate")
    location_lng: Decimal = PydanticField(..., ge=-180, le=180, description="Longitude coordinate")
    location_address: Optional[str] = PydanticField(None, description="Farm address")
    total_area_ha: Optional[Decimal] = PydanticField(None, gt=0, description="Total area in hectares")
    boundary_geojson: Optional[dict] = PydanticField(None, description="Farm boundary as GeoJSON")
    centroid_geojson: Optional[dict] = PydanticField(None, description="Farm centroid as GeoJSON")
    metadata: Optional[dict] = PydanticField(None, description="Additional metadata")


class FarmCreate(FarmBase):
    """Farm creation model"""
    pass


class FarmUpdate(BaseModel):
    """Farm update model"""
    name: Optional[str] = PydanticField(None, min_length=1, max_length=200)
    location_lat: Optional[Decimal] = PydanticField(None, ge=-90, le=90)
    location_lng: Optional[Decimal] = PydanticField(None, ge=-180, le=180)
    location_address: Optional[str] = None
    total_area_ha: Optional[Decimal] = PydanticField(None, gt=0)
    boundary_geojson: Optional[dict] = None
    centroid_geojson: Optional[dict] = None
    metadata: Optional[dict] = None


class Farm(FarmBase):
    """Farm response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class FarmListResponse(BaseModel):
    """Paginated farm list response"""
    farms: List[Farm]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============ Field DTOs ============

class FieldBase(BaseModel):
    """Base field model"""
    farm_id: UUID = PydanticField(..., description="ID of the farm this field belongs to")
    name: str = PydanticField(..., min_length=1, max_length=200, description="Field name")
    area_ha: Decimal = PydanticField(..., gt=0, description="Field area in hectares")
    boundary_geojson: dict = PydanticField(..., description="Field boundary as GeoJSON")
    centroid_geojson: Optional[dict] = PydanticField(None, description="Field centroid as GeoJSON")
    soil_type: Optional[str] = PydanticField(None, description="Soil type classification")
    soil_classification: Optional[str] = PydanticField(None, description="Detailed soil classification")
    elevation_m: Optional[Decimal] = PydanticField(None, ge=0, description="Elevation in meters")
    slope_degree: Optional[Decimal] = PydanticField(None, ge=0, le=90, description="Slope in degrees")
    irrigation_type: Optional[str] = PydanticField(None, description="Irrigation system type")
    drainage_type: Optional[str] = PydanticField(None, description="Drainage system type")
    metadata: Optional[dict] = PydanticField(None, description="Additional metadata")


class FieldCreate(FieldBase):
    """Field creation model"""
    pass


class FieldUpdate(BaseModel):
    """Field update model"""
    name: Optional[str] = PydanticField(None, min_length=1, max_length=200)
    area_ha: Optional[Decimal] = PydanticField(None, gt=0)
    boundary_geojson: Optional[dict] = None
    centroid_geojson: Optional[dict] = None
    soil_type: Optional[str] = None
    soil_classification: Optional[str] = None
    elevation_m: Optional[Decimal] = PydanticField(None, ge=0)
    slope_degree: Optional[Decimal] = PydanticField(None, ge=0, le=90)
    irrigation_type: Optional[str] = None
    drainage_type: Optional[str] = None
    metadata: Optional[dict] = None


class Field(FieldBase):
    """Field response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


# ============ Crop Cycle DTOs ============

class CropCycleBase(BaseModel):
    """Base crop cycle model"""
    field_id: UUID = PydanticField(..., description="ID of the field")
    product_category: str = PydanticField(..., description="Product category")
    crop_name: str = PydanticField(..., description="Name of the crop")
    variety: Optional[str] = PydanticField(None, description="Crop variety")
    cultivar: Optional[str] = PydanticField(None, description="Cultivar name")
    planting_date: date = PydanticField(..., description="Date of planting")
    expected_harvest_date: Optional[date] = PydanticField(None, description="Expected harvest date")
    actual_harvest_date: Optional[date] = PydanticField(None, description="Actual harvest date")
    status: str = PydanticField(default="PLANNED", description="Crop cycle status")
    expected_yield_kg: Optional[Decimal] = PydanticField(None, ge=0, description="Expected yield in kg")
    actual_yield_kg: Optional[Decimal] = PydanticField(None, ge=0, description="Actual yield in kg")
    yield_quality_grade: Optional[str] = PydanticField(None, description="Quality grade")
    seed_source: Optional[str] = PydanticField(None, description="Source of seeds")
    planting_density_per_ha: Optional[int] = PydanticField(None, ge=0, description="Plants per hectare")
    seed_cost_usd: Optional[Decimal] = PydanticField(None, ge=0, description="Seed cost in USD")
    notes: Optional[str] = PydanticField(None, description="Additional notes")
    metadata: Optional[dict] = PydanticField(None, description="Additional metadata")


class CropCycleCreate(CropCycleBase):
    """Crop cycle creation model"""
    pass


class CropCycleUpdate(BaseModel):
    """Crop cycle update model"""
    product_category: Optional[str] = None
    crop_name: Optional[str] = None
    variety: Optional[str] = None
    cultivar: Optional[str] = None
    planting_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    actual_harvest_date: Optional[date] = None
    status: Optional[str] = None
    expected_yield_kg: Optional[Decimal] = PydanticField(None, ge=0)
    actual_yield_kg: Optional[Decimal] = PydanticField(None, ge=0)
    yield_quality_grade: Optional[str] = None
    seed_source: Optional[str] = None
    planting_density_per_ha: Optional[int] = PydanticField(None, ge=0)
    seed_cost_usd: Optional[Decimal] = PydanticField(None, ge=0)
    notes: Optional[str] = None
    metadata: Optional[dict] = None


class CropCycle(CropCycleBase):
    """Crop cycle response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


# ============ Enums (for reference) ============

class CropCycleStatus:
    """Crop cycle status constants"""
    PLANNED = "PLANNED"
    PLANTED = "PLANTED"
    GROWING = "GROWING"
    HARVESTED = "HARVESTED"
    FAILED = "FAILED"
    ABANDONED = "ABANDONED"


class TaskStatus:
    """Task status constants"""
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"
    OVERDUE = "OVERDUE"


class TaskPriority:
    """Task priority constants"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TaskType:
    """Task type constants"""
    LAND_PREPARATION = "LAND_PREPARATION"
    SOWING = "SOWING"
    PLANTING = "PLANTING"
    IRRIGATION = "IRRIGATION"
    FERTILIZATION = "FERTILIZATION"
    WEEDING = "WEEDING"
    PEST_CONTROL = "PEST_CONTROL"
    DISEASE_CONTROL = "DISEASE_CONTROL"
    PRUNING = "PRUNING"
    THINNING = "THINNING"
    HARVESTING = "HARVESTING"
    POST_HARVEST = "POST_HARVEST"
    INSPECTION = "INSPECTION"
    MAINTENANCE = "MAINTENANCE"
    OTHER = "OTHER"
