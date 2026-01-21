from uuid import uuid4
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, Enum as SAEnum, DateTime, Float, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base
from app.domain.ledger.entities import AggregateType, LedgerEventType, Direction, ReferenceType


class LedgerEventORM(Base):
    __tablename__ = "ledger_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    aggregate_type: Mapped[AggregateType] = mapped_column(SAEnum(AggregateType, name='aggregate_type_enum'))
    aggregate_id: Mapped[str] = mapped_column(String)
    event_type: Mapped[LedgerEventType] = mapped_column(SAEnum(LedgerEventType, name='ledger_event_type_enum'))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String, default="ETB")
    direction: Mapped[Direction] = mapped_column(SAEnum(Direction, name='direction_enum'))
    reference_type: Mapped[ReferenceType] = mapped_column(SAEnum(ReferenceType, name='reference_type_enum'))
    reference_id: Mapped[str] = mapped_column(String)
    event_metadata: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))