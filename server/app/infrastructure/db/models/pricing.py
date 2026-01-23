from uuid import uuid4
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, Enum as SAEnum, DateTime, Float, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base
from app.domain.common.enums import RuleType, FeeType


class PricingRuleORM(Base):
    __tablename__ = "pricing_rules"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    rule_type: Mapped[RuleType] = mapped_column(SAEnum(RuleType, name='rule_type_enum'))
    product_category: Mapped[str] = mapped_column(String, nullable=True)
    quality_grade: Mapped[str] = mapped_column(String, nullable=True)
    region: Mapped[str] = mapped_column(String, nullable=True)
    min_distance_km: Mapped[float] = mapped_column(Float, nullable=True)
    max_distance_km: Mapped[float] = mapped_column(Float, nullable=True)
    fee_type: Mapped[FeeType] = mapped_column(SAEnum(FeeType, name='fee_type_enum'))
    fee_value: Mapped[float] = mapped_column(Float)
    priority: Mapped[int] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    valid_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)