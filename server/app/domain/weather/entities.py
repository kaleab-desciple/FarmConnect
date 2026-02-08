"""Weather and advisory domain entities for agricultural management."""
from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class WeatherForecastBase(BaseModel):
    """Base Weather Forecast entity."""
    field_id: str
    source: str
    forecast_date: date
    forecast_hour: Optional[int] = Field(None, ge=0, le=23)
    forecast_horizon_hours: Optional[int] = None
    issued_at: datetime
    temperature_min_c: Optional[Decimal] = None
    temperature_max_c: Optional[Decimal] = None
    temperature_avg_c: Optional[Decimal] = None
    precipitation_probability_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    precipitation_mm: Optional[Decimal] = None
    precipitation_type: Optional[str] = None
    wind_speed_max_mps: Optional[Decimal] = None
    wind_direction_deg: Optional[int] = Field(None, ge=0, le=360)
    humidity_avg_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    pressure_hpa: Optional[Decimal] = None
    growing_degree_days_accumulated: Optional[Decimal] = None
    evapotranspiration_mm: Optional[Decimal] = None
    risk_type: Optional[str] = None
    risk_level: Optional[str] = None
    risk_description: Optional[str] = None
    risk_confidence_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class WeatherForecastCreate(WeatherForecastBase):
    """Weather Forecast creation entity."""
    pass


class WeatherForecast(WeatherForecastBase):
    """Weather Forecast domain entity with full fields."""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class WeatherSnapshotBase(BaseModel):
    """Base Weather Snapshot entity."""
    field_id: str
    source: str
    source_station_id: Optional[str] = None
    source_station_distance_km: Optional[Decimal] = None
    recorded_at: datetime
    temperature_c: Optional[Decimal] = None
    feels_like_c: Optional[Decimal] = None
    humidity_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    pressure_hpa: Optional[Decimal] = None
    wind_speed_mps: Optional[Decimal] = None
    wind_direction_deg: Optional[int] = Field(None, ge=0, le=360)
    wind_gust_mps: Optional[Decimal] = None
    rainfall_mm: Optional[Decimal] = None
    rainfall_intensity: Optional[str] = None
    snowfall_mm: Optional[Decimal] = None
    cloud_cover_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    visibility_m: Optional[Decimal] = None
    uv_index: Optional[Decimal] = None
    soil_temperature_c: Optional[Decimal] = None
    soil_moisture_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    leaf_wetness_hours: Optional[Decimal] = None
    evapotranspiration_mm: Optional[Decimal] = None
    growing_degree_days: Optional[Decimal] = None
    raw_data: Optional[dict] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class WeatherSnapshotCreate(WeatherSnapshotBase):
    """Weather Snapshot creation entity."""
    pass


class WeatherSnapshot(WeatherSnapshotBase):
    """Weather Snapshot domain entity with full fields."""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class AdvisorySessionBase(BaseModel):
    """Base Advisory Session entity."""
    farmer_id: str
    agronomist_id: Optional[str] = None
    field_id: Optional[str] = None
    crop_cycle_id: Optional[str] = None
    topic: str
    title: str
    description: Optional[str] = None
    status: str = "REQUESTED"
    priority: str = "MEDIUM"
    requested_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    communication_method: Optional[str] = None
    meeting_link: Optional[str] = None
    resolution_summary: Optional[str] = None
    recommendations_given: Optional[List[str]] = None
    farmer_rating: Optional[int] = Field(None, ge=1, le=5)
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class AdvisorySessionCreate(AdvisorySessionBase):
    """Advisory Session creation entity."""
    pass


class AdvisorySessionUpdate(BaseModel):
    """Advisory Session update entity."""
    agronomist_id: Optional[str] = None
    field_id: Optional[str] = None
    crop_cycle_id: Optional[str] = None
    topic: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    communication_method: Optional[str] = None
    meeting_link: Optional[str] = None
    resolution_summary: Optional[str] = None
    recommendations_given: Optional[List[str]] = None
    farmer_rating: Optional[int] = Field(None, ge=1, le=5)
    metadata: Optional[dict] = None


class AdvisorySession(AdvisorySessionBase):
    """Advisory Session domain entity with full fields."""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class AdvisoryMessageBase(BaseModel):
    """Base Advisory Message entity."""
    session_id: str
    sender_id: str
    message_type: str = "TEXT"
    message: str
    attachments: Optional[dict] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class AdvisoryMessageCreate(AdvisoryMessageBase):
    """Advisory Message creation entity."""
    pass


class AdvisoryMessage(AdvisoryMessageBase):
    """Advisory Message domain entity with full fields."""
    id: str

    class Config:
        from_attributes = True


class KnowledgeArticleBase(BaseModel):
    """Base Knowledge Article entity."""
    author_id: str
    topic: str
    title: str
    slug: Optional[str] = None
    summary: Optional[str] = None
    content: str
    status: str = "draft"
    published_at: Optional[datetime] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class KnowledgeArticleCreate(KnowledgeArticleBase):
    """Knowledge Article creation entity."""
    pass


class KnowledgeArticleUpdate(BaseModel):
    """Knowledge Article update entity."""
    topic: Optional[str] = None
    title: Optional[str] = None
    slug: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    published_at: Optional[datetime] = None
    metadata: Optional[dict] = None


class KnowledgeArticle(KnowledgeArticleBase):
    """Knowledge Article domain entity with full fields."""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class AlertBase(BaseModel):
    """Base Alert entity."""
    user_id: str
    field_id: Optional[str] = None
    alert_type: str
    severity: str
    title: str
    message: str
    acknowledged: bool = False
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class AlertCreate(AlertBase):
    """Alert creation entity."""
    pass


class AlertUpdate(BaseModel):
    """Alert update entity."""
    acknowledged: Optional[bool] = None
    metadata: Optional[dict] = None


class Alert(AlertBase):
    """Alert domain entity with full fields."""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class FieldRiskScoreBase(BaseModel):
    """Base Field Risk Score entity."""
    field_id: str
    crop_cycle_id: Optional[str] = None
    score_date: date
    overall_score: Decimal = Field(..., ge=0, le=100)
    risk_trend: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class FieldRiskScoreCreate(FieldRiskScoreBase):
    """Field Risk Score creation entity."""
    pass


class FieldRiskScore(FieldRiskScoreBase):
    """Field Risk Score domain entity with full fields."""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Forum/Community Entities (Section 3.4 Advisory & Collaboration Context)
class ForumThreadBase(BaseModel):
    """Base Forum Thread entity."""
    author_id: str
    author_username: str
    author_reputation: int = 0
    author_badge: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = None
    title: str
    slug: Optional[str] = None
    body: str
    format: str = "markdown"
    attachments: Optional[List[dict]] = None
    related_field_id: Optional[str] = None
    related_crop_cycle_id: Optional[str] = None
    crop_type: Optional[str] = None
    growth_stage: Optional[str] = None
    views: int = 0
    upvotes: int = 0
    downvotes: int = 0
    bookmarks: int = 0
    shares: int = 0
    status: str = "open"
    accepted_answer_id: Optional[str] = None
    helpful_count: int = 0
    resolution_summary: Optional[str] = None

    class Config:
        from_attributes = True


class ForumThreadCreate(ForumThreadBase):
    """Forum Thread creation entity."""
    pass


class ForumThread(ForumThreadBase):
    """Forum Thread domain entity with full fields."""
    id: str
    created_at: datetime
    last_activity: datetime
    bumped_at: datetime

    class Config:
        from_attributes = True


class ForumCommentBase(BaseModel):
    """Base Forum Comment entity."""
    thread_id: str
    author_id: str
    author_username: str
    author_badge: Optional[str] = None
    content: str
    parent_id: Optional[str] = None
    is_accepted_answer: bool = False
    upvotes: int = 0
    downvotes: int = 0

    class Config:
        from_attributes = True


class ForumCommentCreate(ForumCommentBase):
    """Forum Comment creation entity."""
    pass


class ForumComment(ForumCommentBase):
    """Forum Comment domain entity with full fields."""
    id: str
    created_at: datetime
    replies: Optional[List[dict]] = None

    class Config:
        from_attributes = True
