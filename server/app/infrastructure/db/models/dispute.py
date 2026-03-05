from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Enum as SAEnum, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base
from app.domain.common.enums import DisputeState, DisputeResolution

class DisputeORM(Base):
    __tablename__ = "disputes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    order_id: Mapped[str] = mapped_column(String, nullable=True)
    raised_by: Mapped[str] = mapped_column(String, nullable=True)
    state: Mapped[DisputeState] = mapped_column(SAEnum(DisputeState, name='dispute_state_enum'), nullable=True)
    reason: Mapped[str] = mapped_column(String, nullable=True)
    resolution: Mapped[DisputeResolution] = mapped_column(SAEnum(DisputeResolution, name='dispute_resolution_enum'), nullable=True)
    evidence_urls: Mapped[list] = mapped_column(JSONB, nullable=True)
    # Escalation chain fields (Gap 3)
    handler_role: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    escalated_to: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    escalation_note: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
