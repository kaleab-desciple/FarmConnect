"""Farm domain entities for agricultural management."""
from datetime import datetime, date, time, timezone
from decimal import Decimal
from typing import Optional, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field as PydanticField, field_validator


class FarmBase(BaseModel):
    """Base Farm entity."""
    farmer_id: str
    name: str
    location_lat: Decimal = PydanticField(..., ge=-90, le=90)
    location_lng: Decimal = PydanticField(..., ge=-180, le=180)
    location_address: Optional[str] = None
    total_area_ha: Optional[Decimal] = PydanticField(None, gt=0)
    boundary_geojson: Optional[dict] = None
    centroid_geojson: Optional[dict] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class FarmCreate(FarmBase):
    """Farm creation entity."""
    pass


class FarmUpdate(BaseModel):
    """Farm update entity."""
    name: Optional[str] = None
    location_lat: Optional[Decimal] = PydanticField(None, ge=-90, le=90)
    location_lng: Optional[Decimal] = PydanticField(None, ge=-180, le=180)
    location_address: Optional[str] = None
    total_area_ha: Optional[Decimal] = PydanticField(None, gt=0)
    boundary_geojson: Optional[dict] = None
    centroid_geojson: Optional[dict] = None
    metadata: Optional[dict] = None


class Farm(FarmBase):
    """Farm domain entity with full fields."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FieldBase(BaseModel):
    """Base Field entity."""
    farm_id: UUID
    name: str
    area_ha: Decimal = PydanticField(..., gt=0)
    boundary_geojson: dict
    centroid_geojson: Optional[dict] = None
    soil_type: Optional[str] = None
    soil_classification: Optional[str] = None
    elevation_m: Optional[Decimal] = None
    slope_degree: Optional[Decimal] = PydanticField(None, ge=0, le=90)
    irrigation_type: Optional[str] = None
    drainage_type: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class FieldCreate(FieldBase):
    """Field creation entity."""
    pass


class FieldUpdate(BaseModel):
    """Field update entity."""
    name: Optional[str] = None
    area_ha: Optional[Decimal] = PydanticField(None, gt=0)
    boundary_geojson: Optional[dict] = None
    centroid_geojson: Optional[dict] = None
    soil_type: Optional[str] = None
    soil_classification: Optional[str] = None
    elevation_m: Optional[Decimal] = None
    slope_degree: Optional[Decimal] = PydanticField(None, ge=0, le=90)
    irrigation_type: Optional[str] = None
    drainage_type: Optional[str] = None
    metadata: Optional[dict] = None


class Field(FieldBase):
    """Field domain entity with full fields."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CropCycleBase(BaseModel):
    """Base Crop Cycle entity."""
    field_id: UUID
    product_category: str
    crop_name: str
    variety: Optional[str] = None
    cultivar: Optional[str] = None
    planting_date: date
    expected_harvest_date: Optional[date] = None
    actual_harvest_date: Optional[date] = None
    status: str = "PLANNED"
    expected_yield_kg: Optional[Decimal] = PydanticField(None, ge=0)
    actual_yield_kg: Optional[Decimal] = PydanticField(None, ge=0)
    yield_quality_grade: Optional[str] = None
    seed_source: Optional[str] = None
    planting_density_per_ha: Optional[int] = None
    seed_cost_usd: Optional[Decimal] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class CropCycleCreate(CropCycleBase):
    """Crop Cycle creation entity."""
    pass


class CropCycleUpdate(BaseModel):
    """Crop Cycle update entity."""
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
    planting_density_per_ha: Optional[int] = None
    seed_cost_usd: Optional[Decimal] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None


class CropCycle(CropCycleBase):
    """Crop Cycle domain entity with full fields."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FarmTaskBase(BaseModel):
    """Base Farm Task entity."""
    field_id: UUID
    crop_cycle_id: Optional[UUID] = None
    task_type: str
    title: str
    description: Optional[str] = None
    status: str = "PENDING"
    priority: str = "MEDIUM"
    scheduled_date: date
    scheduled_time: Optional[time] = None
    duration_estimate_hours: Optional[Decimal] = None
    window_start_date: Optional[date] = None
    window_end_date: Optional[date] = None
    completed_date: Optional[date] = None
    completed_time: Optional[time] = None
    completed_by: Optional[str] = None
    duration_actual_hours: Optional[Decimal] = None
    assigned_to: Optional[str] = None
    labor_count: Optional[int] = None
    equipment_needed: Optional[List[str]] = None
    materials_needed: Optional[dict] = None
    estimated_cost_usd: Optional[Decimal] = None
    actual_cost_usd: Optional[Decimal] = None
    parent_task_id: Optional[UUID] = None
    depends_on_tasks: Optional[List[UUID]] = None
    weather_dependent: bool = False
    soil_moisture_condition: Optional[str] = None
    auto_generated: bool = False
    generation_reason: Optional[str] = None
    notes: Optional[str] = None
    completion_notes: Optional[str] = None
    completion_photos: Optional[List[str]] = None
    metadata: Optional[dict] = None

    @field_validator("scheduled_time", "completed_time", mode="before")
    @classmethod
    def parse_time(cls, v):
        """Allow parsing time from a full ISO datetime string."""
        if isinstance(v, str) and "T" in v:
            try:
                # Handle ISO8601 strings like "2026-02-14T17:56:40.736Z"
                dt_str = v.replace("Z", "+00:00")
                return datetime.fromisoformat(dt_str).time()
            except (ValueError, TypeError):
                pass
        return v

    class Config:
        from_attributes = True


class FarmTaskCreate(FarmTaskBase):
    """Farm Task creation entity."""
    pass


class FarmTaskUpdate(BaseModel):
    """Farm Task update entity."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    duration_estimate_hours: Optional[Decimal] = None
    window_start_date: Optional[date] = None
    window_end_date: Optional[date] = None
    completed_date: Optional[date] = None
    completed_time: Optional[time] = None
    completed_by: Optional[str] = None
    duration_actual_hours: Optional[Decimal] = None
    assigned_to: Optional[str] = None
    labor_count: Optional[int] = None
    equipment_needed: Optional[List[str]] = None
    materials_needed: Optional[dict] = None
    estimated_cost_usd: Optional[Decimal] = None
    actual_cost_usd: Optional[Decimal] = None
    weather_dependent: Optional[bool] = None
    soil_moisture_condition: Optional[str] = None
    notes: Optional[str] = None
    completion_notes: Optional[str] = None
    completion_photos: Optional[List[str]] = None
    metadata: Optional[dict] = None

    @field_validator("scheduled_time", "completed_time", mode="before")
    @classmethod
    def parse_time(cls, v):
        """Allow parsing time from a full ISO datetime string."""
        if isinstance(v, str) and "T" in v:
            try:
                dt_str = v.replace("Z", "+00:00")
                return datetime.fromisoformat(dt_str).time()
            except (ValueError, TypeError):
                pass
        return v


class FarmTask(FarmTaskBase):
    """Farm Task domain entity with full fields."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
class HarvestBase(BaseModel):
    """Base Harvest entity."""
    farmer_id: str
    crop_cycle_id: Optional[UUID] = None
    field_id: UUID
    harvest_date: date
    quantity_harvested: Decimal = PydanticField(..., gt=0)
    unit: Optional[str] = None
    quality_grade: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class HarvestCreate(HarvestBase):
    """Harvest creation entity."""
    pass


class HarvestUpdate(BaseModel):
    """Harvest update entity."""
    harvest_date: Optional[date] = None
    quantity_harvested: Optional[Decimal] = PydanticField(None, gt=0)
    unit: Optional[str] = None
    quality_grade: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None


class Harvest(HarvestBase):
    """Harvest domain entity with full fields."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
