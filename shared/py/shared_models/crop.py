from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator

class CropCycleBase(BaseModel):
    product_category: str
    crop_name: str
    variety: Optional[str] = None
    cultivar: Optional[str] = None
    planting_date: date
    expected_harvest_date: Optional[date] = None
    expected_yield_kg: Optional[Decimal] = None
    seed_source: Optional[str] = None
    planting_density_per_ha: Optional[int] = None
    notes: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

class CropCycleCreate(CropCycleBase):
    @field_validator('expected_harvest_date')
    @classmethod
    def validate_harvest_date(cls, v, info):
        if v is not None and 'planting_date' in info.data:
            planting_date = info.data['planting_date']
            if v <= planting_date:
                raise ValueError('expected_harvest_date must be after planting_date')
        return v

class CropCycleUpdate(BaseModel):
    status: Optional[str] = None
    expected_harvest_date: Optional[date] = None
    actual_harvest_date: Optional[date] = None
    expected_yield_kg: Optional[Decimal] = None
    actual_yield_kg: Optional[Decimal] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None
    
    @field_validator('expected_yield_kg', 'actual_yield_kg')
    @classmethod
    def validate_yields(cls, v):
        if v is not None and v < 0:
            raise ValueError('Yield values must be non-negative')
        return v

class HarvestRecord(BaseModel):
    actual_harvest_date: date
    actual_yield_kg: Decimal
    quality_grade: Optional[str] = None
    notes: Optional[str] = None

class CropCycle(CropCycleBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    field_id: UUID
    status: str
    actual_harvest_date: Optional[date] = None
    actual_yield_kg: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
