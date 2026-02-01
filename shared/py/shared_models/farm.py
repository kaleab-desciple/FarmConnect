from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class FarmBase(BaseModel):
    name: str
    location_lat: Decimal
    location_lng: Decimal
    location_address: Optional[str] = None
    total_area_ha: Optional[Decimal] = None
    boundary_geojson: Optional[dict] = None
    metadata: dict = Field(default_factory=dict)

class FarmCreate(FarmBase):
    pass

class FarmUpdate(BaseModel):
    name: Optional[str] = None
    location_lat: Optional[Decimal] = None
    location_lng: Optional[Decimal] = None
    location_address: Optional[str] = None
    total_area_ha: Optional[Decimal] = None
    boundary_geojson: Optional[dict] = None
    metadata: Optional[dict] = None

class Farm(FarmBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    farmer_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

class FieldBase(BaseModel):
    name: str
    area_ha: Decimal
    boundary_geojson: dict
    centroid_geom: Optional[dict] = None
    soil_type: Optional[str] = None
    soil_classification: Optional[str] = None
    elevation_m: Optional[Decimal] = None
    slope_degree: Optional[Decimal] = None
    irrigation_type: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

class FieldCreate(FieldBase):
    pass

class FieldUpdate(BaseModel):
    name: Optional[str] = None
    area_ha: Optional[Decimal] = None
    boundary_geojson: Optional[dict] = None
    soil_type: Optional[str] = None
    soil_classification: Optional[str] = None
    elevation_m: Optional[Decimal] = None
    slope_degree: Optional[Decimal] = None
    irrigation_type: Optional[str] = None
    metadata: Optional[dict] = None

class Field(FieldBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    farm_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
