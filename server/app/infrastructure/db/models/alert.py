from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base

class AlertORM(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    field_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), ForeignKey("fields.id"), nullable=True)
    crop_cycle_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), ForeignKey("crop_cycles.id"), nullable=True)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    action_required: Mapped[str] = mapped_column(Text, nullable=True)
    action_url: Mapped[str] = mapped_column(String(500), nullable=True)
    related_entity_type: Mapped[str] = mapped_column(String(100), nullable=True)
    related_entity_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    acknowledged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    dismissed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dismissed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Using metadata_ to avoid conflict with Base.metadata
    metadata_: Mapped[dict] = mapped_column(JSONB, name="metadata", nullable=False, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
