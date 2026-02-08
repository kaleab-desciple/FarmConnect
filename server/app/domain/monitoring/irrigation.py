"""Irrigation and additional monitoring domain entities."""
from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


class IrrigationEventBase(BaseModel):
    """Base Irrigation Event entity."""
    field_id: str
    crop_cycle_id: Optional[str] = None
    scheduled_date: datetime
    duration_minutes: int
    water_volume_liters: Decimal = Field(..., gt=0)
    triggered_by: str = "manual"
    status: str = "scheduled"
    notes: Optional[str] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    actual_duration_minutes: Optional[int] = None
    water_actual_liters: Optional[Decimal] = None
    equipment_used: Optional[List[str]] = None
    weather_during_irrigation: Optional[dict] = None
    soil_moisture_before: Optional[Decimal] = None
    soil_moisture_after: Optional[Decimal] = None
    efficiency_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class IrrigationEventCreate(IrrigationEventBase):
    """Irrigation Event creation entity."""
    pass


class IrrigationEventUpdate(BaseModel):
    """Irrigation Event update entity."""
    status: Optional[str] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    actual_duration_minutes: Optional[int] = None
    water_actual_liters: Optional[Decimal] = None
    notes: Optional[str] = None
    soil_moisture_after: Optional[Decimal] = None
    efficiency_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    metadata: Optional[dict] = None


class IrrigationEvent(IrrigationEventBase):
    """Irrigation Event domain entity with full fields."""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class FieldVisitLogBase(BaseModel):
    """Base Field Visit Log entity."""
    field_id: str
    crop_cycle_id: Optional[str] = None
    visit_date: date
    visit_type: str
    purpose: Optional[str] = None
    visited_by: str
    weather_conditions: Optional[str] = None
    temperature_c: Optional[Decimal] = None
    humidity_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    soil_conditions: Optional[str] = None
    observations: Optional[str] = None
    issues_found: Optional[List[str]] = None
    photos: Optional[List[str]] = None
    recommendations: Optional[str] = None
    follow_up_required: bool = False
    follow_up_notes: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class FieldVisitLogCreate(FieldVisitLogBase):
    """Field Visit Log creation entity."""
    pass


class FieldVisitLog(FieldVisitLogBase):
    """Field Visit Log domain entity with full fields."""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
