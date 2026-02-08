"""Soil readings and monitoring ORM models."""
from uuid import uuid4
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, DateTime, Date, Numeric, Integer, Text, ForeignKey, ARRAY, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import Base


class SoilReadingORM(Base):
    """Soil reading entity for manual or lab-based soil analysis."""
    __tablename__ = "soil_readings"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    field_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    location_geojson: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    sample_depth_cm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sample_depth_range: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    moisture_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    temperature_c: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    ph: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    nitrogen_ppm: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    phosphorus_ppm: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    potassium_ppm: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    organic_matter_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    cation_exchange_capacity: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    electrical_conductivity_ms_cm: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    texture_analysis: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    source: Mapped[str] = mapped_column(
        ENUM('IOT_SENSOR', 'MANUAL_TEST', 'LAB_ANALYSIS', 'ESTIMATED', name='soil_reading_source', create_type=False),
        nullable=False
    )
    lab_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    lab_report_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id"), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    weather_conditions: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    days_since_rain: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    field: Mapped["FieldORM"] = relationship("FieldORM", back_populates="soil_readings")


class NDVISnapshotORM(Base):
    """NDVI snapshot for vegetation health monitoring."""
    __tablename__ = "ndvi_snapshots"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    field_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    crop_cycle_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("crop_cycles.id", ondelete="SET NULL"), nullable=True)
    source: Mapped[str] = mapped_column(
        ENUM('SENTINEL_2', 'LANDSAT_8', 'LANDSAT_9', 'MODIS', 'MANUAL', name='ndvi_source', create_type=False),
        nullable=False
    )
    source_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ndvi_mean: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    ndvi_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4), nullable=True)
    ndvi_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4), nullable=True)
    ndvi_stddev: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4), nullable=True)
    stress_level: Mapped[Optional[str]] = mapped_column(
        ENUM('NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='stress_level', create_type=False),
        nullable=True
    )
    cloud_cover_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    data_quality_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    tile_urls: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class PestDiseaseReportORM(Base):
    """Pest and disease report for field health issues."""
    __tablename__ = "pest_disease_reports"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    field_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    crop_cycle_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("crop_cycles.id", ondelete="SET NULL"), nullable=True)
    reported_by: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    location_geojson: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    image_urls: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    drone_flight_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), nullable=True)
    suspected_issue: Mapped[str] = mapped_column(String(255), nullable=False)
    issue_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    scientific_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    common_names: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    ai_diagnosis_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), nullable=True)
    confidence_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    severity: Mapped[Optional[str]] = mapped_column(
        ENUM('TRACE', 'LOW', 'MEDIUM', 'HIGH', 'SEVERE', name='severity_level', create_type=False),
        nullable=True
    )
    affected_area_ha: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    affected_plant_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    symptoms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    spread_pattern: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    verified_by: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id"), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    first_observed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    crop_cycle: Mapped[Optional["CropCycleORM"]] = relationship("CropCycleORM", back_populates="pest_disease_reports")
    treatment_recommendations: Mapped[List["TreatmentRecommendationORM"]] = relationship("TreatmentRecommendationORM", back_populates="report", cascade="all, delete-orphan")


class TreatmentRecommendationORM(Base):
    """Treatment recommendation for pest/disease issues."""
    __tablename__ = "treatment_recommendations"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    report_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("pest_disease_reports.id", ondelete="CASCADE"), nullable=False)
    recommended_by: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    recommendation_source: Mapped[str] = mapped_column(
        ENUM('AGRONOMIST', 'SYSTEM', 'AI_MODEL', 'COMMUNITY', name='recommendation_source', create_type=False),
        nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    treatment_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    chemical_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    active_ingredient: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    formulation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    dosage_per_ha: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    application_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    application_timing: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    organic: Mapped[bool] = mapped_column(Boolean, default=False)
    restricted_use: Mapped[bool] = mapped_column(Boolean, default=False)
    required_ppe: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    reentry_interval_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pre_harvest_interval_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    withdrawal_period_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estimated_cost_per_ha_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    effectiveness_rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    expected_results_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    accepted_by_farmer: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    applied: Mapped[bool] = mapped_column(Boolean, default=False)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    application_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    report: Mapped["PestDiseaseReportORM"] = relationship("PestDiseaseReportORM", back_populates="treatment_recommendations")


# Import for type hints
from app.infrastructure.db.models.farm import FieldORM, CropCycleORM
