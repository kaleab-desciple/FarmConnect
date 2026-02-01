from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import Base

class FarmORM(Base):
    __tablename__ = "farms"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    farmer_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location_lat: Mapped[float] = mapped_column(Numeric(precision=10, scale=8), nullable=False)
    location_lng: Mapped[float] = mapped_column(Numeric(precision=11, scale=8), nullable=False)
    location_address: Mapped[str] = mapped_column(String(500), nullable=True)
    total_area_ha: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=True)
    boundary_geom: Mapped[dict] = mapped_column(JSONB, nullable=True)
    boundary_geojson: Mapped[dict] = mapped_column(JSONB, nullable=True)
    
    # Using metadata_ to avoid conflict with Base.metadata
    metadata_: Mapped[dict] = mapped_column(JSONB, name="metadata", nullable=False, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    fields = relationship("FieldORM", back_populates="farm", cascade="all, delete-orphan")


class FieldORM(Base):
    __tablename__ = "fields"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    farm_id: Mapped[str] = mapped_column(String, ForeignKey("farms.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    area_ha: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    boundary_geom: Mapped[dict] = mapped_column(JSONB, nullable=True)
    boundary_geojson: Mapped[dict] = mapped_column(JSONB, nullable=False)
    centroid_geom: Mapped[dict] = mapped_column(JSONB, nullable=True)
    soil_type: Mapped[str] = mapped_column(String(100), nullable=True)
    soil_classification: Mapped[str] = mapped_column(String(100), nullable=True)
    elevation_m: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=True)
    slope_degree: Mapped[float] = mapped_column(Numeric(precision=5, scale=2), nullable=True)
    irrigation_type: Mapped[str] = mapped_column(String(100), nullable=True)
    
    metadata_: Mapped[dict] = mapped_column(JSONB, name="metadata", nullable=False, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    farm = relationship("FarmORM", back_populates="fields")
    crop_cycles = relationship("CropCycleORM", back_populates="field", cascade="all, delete-orphan")
