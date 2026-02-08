"""Weather and advisory ORM models."""
from uuid import uuid4
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, DateTime, Date, Numeric, Integer, Text, ForeignKey, ARRAY, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import Base


class WeatherForecastORM(Base):
    """Weather forecast entity for field-specific predictions."""
    __tablename__ = "weather_forecasts"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    field_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    source: Mapped[str] = mapped_column(
        ENUM('NOAA_GFS', 'NOAA_HRRR', 'OPEN_METEO', 'LOCAL_STATION', 'MANUAL', name='weather_source', create_type=False),
        nullable=False
    )
    forecast_date: Mapped[date] = mapped_column(Date, nullable=False)
    forecast_hour: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    forecast_horizon_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    temperature_min_c: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    temperature_max_c: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    temperature_avg_c: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    precipitation_probability_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    precipitation_mm: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    precipitation_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    wind_speed_max_mps: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    wind_direction_deg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    humidity_avg_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    pressure_hpa: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 2), nullable=True)
    growing_degree_days_accumulated: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    evapotranspiration_mm: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    risk_type: Mapped[Optional[str]] = mapped_column(
        ENUM('FROST', 'FREEZE', 'HEAT_STRESS', 'DROUGHT', 'HEAVY_RAIN', 'FLOOD',
             'HAIL', 'STRONG_WIND', 'STORM', 'HURRICANE', 'TORNADO', 'WILDFIRE',
             'PEST_OUTBREAK', 'DISEASE_OUTBREAK', name='risk_type', create_type=False),
        nullable=True
    )
    risk_level: Mapped[Optional[str]] = mapped_column(
        ENUM('MINIMAL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='risk_level', create_type=False),
        nullable=True
    )
    risk_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk_confidence_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class WeatherSnapshotORM(Base):
    """Weather snapshot for actual recorded weather conditions."""
    __tablename__ = "weather_snapshots"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    field_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    source: Mapped[str] = mapped_column(
        ENUM('NOAA_GFS', 'NOAA_HRRR', 'OPEN_METEO', 'LOCAL_STATION', 'MANUAL', name='weather_source', create_type=False),
        nullable=False
    )
    source_station_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_station_distance_km: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    temperature_c: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    feels_like_c: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    humidity_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    pressure_hpa: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 2), nullable=True)
    wind_speed_mps: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    wind_direction_deg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    wind_gust_mps: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    rainfall_mm: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    rainfall_intensity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    snowfall_mm: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    cloud_cover_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    visibility_m: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    uv_index: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    soil_temperature_c: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    soil_moisture_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    leaf_wetness_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    evapotranspiration_mm: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    growing_degree_days: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AdvisorySessionORM(Base):
    """Advisory session for farmer-agronomist consultations."""
    __tablename__ = "advisory_sessions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    farmer_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agronomist_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    field_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("fields.id", ondelete="SET NULL"), nullable=True)
    crop_cycle_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("crop_cycles.id", ondelete="SET NULL"), nullable=True)
    topic: Mapped[str] = mapped_column(
        ENUM('CROP_SELECTION', 'PEST_MANAGEMENT', 'DISEASE_MANAGEMENT', 'SOIL_HEALTH',
             'IRRIGATION', 'FERTILIZATION', 'HARVEST_TIMING', 'POST_HARVEST',
             'MARKET_ADVICE', 'FINANCIAL_PLANNING', 'GENERAL', name='advisory_topic', create_type=False),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        ENUM('REQUESTED', 'SCHEDULED', 'OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED', 'CANCELLED',
             name='advisory_status', create_type=False),
        default='REQUESTED'
    )
    priority: Mapped[str] = mapped_column(
        ENUM('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='task_priority', create_type=False),
        default='MEDIUM'
    )
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    communication_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    meeting_link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolution_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommendations_given: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    farmer_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    messages: Mapped[List["AdvisoryMessageORM"]] = relationship("AdvisoryMessageORM", back_populates="session", cascade="all, delete-orphan")


class AdvisoryMessageORM(Base):
    """Advisory message within a session."""
    __tablename__ = "advisory_messages"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("advisory_sessions.id", ondelete="CASCADE"), nullable=False)
    sender_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    message_type: Mapped[str] = mapped_column(
        ENUM('TEXT', 'IMAGE', 'DOCUMENT', 'VOICE', 'VIDEO', 'LOCATION', 'SYSTEM', name='message_type', create_type=False),
        default='TEXT'
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    attachments: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", default=dict)

    # Relationships
    session: Mapped["AdvisorySessionORM"] = relationship("AdvisorySessionORM", back_populates="messages")


class KnowledgeArticleORM(Base):
    """Knowledge article for agricultural best practices."""
    __tablename__ = "knowledge_articles"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    author_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    topic: Mapped[str] = mapped_column(
        ENUM('CROP_SELECTION', 'PEST_MANAGEMENT', 'DISEASE_MANAGEMENT', 'SOIL_HEALTH',
             'IRRIGATION', 'FERTILIZATION', 'HARVEST_TIMING', 'POST_HARVEST',
             'MARKET_ADVICE', 'FINANCIAL_PLANNING', 'GENERAL', name='advisory_topic', create_type=False),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='draft')
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AlertORM(Base):
    """Alert entity for notifications to users."""
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    field_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("fields.id", ondelete="CASCADE"), nullable=True)
    alert_type: Mapped[str] = mapped_column(
        ENUM('WEATHER_WARNING', 'FROST_ALERT', 'DROUGHT_ALERT', 'PEST_DETECTED',
             'DISEASE_DETECTED', 'NDVI_ANOMALY', 'SOIL_MOISTURE_LOW', 'SOIL_MOISTURE_HIGH',
             'TASK_OVERDUE', 'HARVEST_READY', 'LOAN_RISK', 'PAYMENT_DUE',
             'ESCROW_HOLD', 'PRICE_ALERT', 'SYSTEM_NOTIFICATION', name='alert_type', create_type=False),
        nullable=False
    )
    severity: Mapped[str] = mapped_column(
        ENUM('INFO', 'WARNING', 'CRITICAL', 'EMERGENCY', name='alert_severity', create_type=False),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class FieldRiskScoreORM(Base):
    """Field risk score for risk assessment."""
    __tablename__ = "field_risk_scores"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    field_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    crop_cycle_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("crop_cycles.id", ondelete="SET NULL"), nullable=True)
    score_date: Mapped[date] = mapped_column(Date, nullable=False)
    overall_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    risk_trend: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
