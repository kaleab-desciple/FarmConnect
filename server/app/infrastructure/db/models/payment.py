from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import String, Float, Enum as SAEnum, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base
from shared_models.enums import EscrowState  # enum from shared models
from shared_models.escrow import Provider

class EscrowORM(Base):
    __tablename__ = "escrows"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    order_id: Mapped[str] = mapped_column(String, nullable=True)
    state: Mapped[EscrowState] = mapped_column(SAEnum(EscrowState, name='escrow_state_enum'), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=True)
    penalty_applied: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    provider: Mapped[Provider] = mapped_column(SAEnum(Provider, name='provider_enum'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=True)
    funded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    released_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    provider_reference: Mapped[str] = mapped_column(String, nullable=True)
