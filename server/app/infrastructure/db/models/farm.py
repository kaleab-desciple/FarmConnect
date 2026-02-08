"""Farm and Field ORM models for agricultural management."""
from uuid import uuid4
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, DateTime, Date, Time, Numeric, Integer, Boolean, Text, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import JSONB, UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import Base


class FarmORM(Base):
    """Farm entity representing a farmer's agricultural land."""
    __tablename__ = "farms"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    farmer_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location_lat: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    location_lng: Mapped[Decimal] = mapped_column(Numeric(11, 8), nullable=False)
    location_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_area_ha: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    boundary_geojson: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    centroid_geojson: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    fields: Mapped[List["FieldORM"]] = relationship("FieldORM", back_populates="farm", cascade="all, delete-orphan")


class FieldORM(Base):
    """Field entity representing a specific plot within a farm."""
    __tablename__ = "fields"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    farm_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    area_ha: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    boundary_geojson: Mapped[dict] = mapped_column(JSONB, nullable=False)
    centroid_geojson: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    soil_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    soil_classification: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    elevation_m: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    slope_degree: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    irrigation_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    drainage_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    farm: Mapped["FarmORM"] = relationship("FarmORM", back_populates="fields")
    crop_cycles: Mapped[List["CropCycleORM"]] = relationship("CropCycleORM", back_populates="field", cascade="all, delete-orphan")
    soil_readings: Mapped[List["SoilReadingORM"]] = relationship("SoilReadingORM", back_populates="field", cascade="all, delete-orphan")
    farm_tasks: Mapped[List["FarmTaskORM"]] = relationship("FarmTaskORM", back_populates="field", cascade="all, delete-orphan")


class CropCycleORM(Base):
    """Crop cycle entity representing a planting-to-harvest cycle."""
    __tablename__ = "crop_cycles"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    field_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    product_category: Mapped[str] = mapped_column(String(50), nullable=False)
    crop_name: Mapped[str] = mapped_column(String(255), nullable=False)
    variety: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cultivar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    planting_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_harvest_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_harvest_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        ENUM('PLANNED', 'PLANTED', 'GROWING', 'HARVESTED', 'FAILED', 'ABANDONED', name='crop_cycle_status', create_type=False),
        default='PLANNED'
    )
    expected_yield_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    actual_yield_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    yield_quality_grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    seed_source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    planting_density_per_ha: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    seed_cost_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    field: Mapped["FieldORM"] = relationship("FieldORM", back_populates="crop_cycles")
    farm_tasks: Mapped[List["FarmTaskORM"]] = relationship("FarmTaskORM", back_populates="crop_cycle")
    pest_disease_reports: Mapped[List["PestDiseaseReportORM"]] = relationship("PestDiseaseReportORM", back_populates="crop_cycle")


class FarmTaskORM(Base):
    """Farm task entity for scheduling and tracking agricultural operations."""
    __tablename__ = "farm_tasks"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    field_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    crop_cycle_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("crop_cycles.id", ondelete="SET NULL"), nullable=True)
    task_type: Mapped[str] = mapped_column(
        ENUM('LAND_PREPARATION', 'SOWING', 'PLANTING', 'IRRIGATION', 'FERTILIZATION',
             'WEEDING', 'PEST_CONTROL', 'DISEASE_CONTROL', 'PRUNING', 'THINNING',
             'HARVESTING', 'POST_HARVEST', 'INSPECTION', 'MAINTENANCE', 'OTHER',
             name='task_type', create_type=False),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        ENUM('PENDING', 'SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED', 'CANCELLED', 'OVERDUE',
             name='task_status', create_type=False),
        default='PENDING'
    )
    priority: Mapped[str] = mapped_column(
        ENUM('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='task_priority', create_type=False),
        default='MEDIUM'
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    scheduled_time: Mapped[Optional[datetime]] = mapped_column(Time, nullable=True)
    duration_estimate_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    window_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    window_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_time: Mapped[Optional[datetime]] = mapped_column(Time, nullable=True)
    completed_by: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id"), nullable=True)
    duration_actual_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id"), nullable=True)
    labor_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    equipment_needed: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    materials_needed: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    estimated_cost_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    actual_cost_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    parent_task_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("farm_tasks.id"), nullable=True)
    depends_on_tasks: Mapped[Optional[List[str]]] = mapped_column(ARRAY(UUID(as_uuid=False)), nullable=True)
    weather_dependent: Mapped[bool] = mapped_column(Boolean, default=False)
    soil_moisture_condition: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    auto_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    generation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completion_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completion_photos: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    field: Mapped["FieldORM"] = relationship("FieldORM", back_populates="farm_tasks")
    crop_cycle: Mapped[Optional["CropCycleORM"]] = relationship("CropCycleORM", back_populates="farm_tasks")
