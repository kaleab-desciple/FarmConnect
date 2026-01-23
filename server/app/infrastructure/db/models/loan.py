from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import String, Float, Enum as SAEnum, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base
from app.domain.common.enums import LoanState

class LoanORM(Base):
    __tablename__ = "loans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    farmer_id: Mapped[str] = mapped_column(String, nullable=True)
    principal: Mapped[float] = mapped_column(Float, nullable=True)
    interest_rate: Mapped[float] = mapped_column(Float, nullable=True)
    state: Mapped[LoanState] = mapped_column(SAEnum(LoanState, name='loan_state_enum'), nullable=True)
    auto_approved: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    repayment_schedule: Mapped[list] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True)
    closed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
