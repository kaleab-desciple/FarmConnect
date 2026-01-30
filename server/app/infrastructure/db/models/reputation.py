from decimal import Decimal
from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base


class ReputationORM(Base):
    __tablename__ = "reputations"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    completed_orders: Mapped[int] = mapped_column(Integer, default=0)
    successful_orders: Mapped[int] = mapped_column(Integer, default=0)
    disputes_lost: Mapped[int] = mapped_column(Integer, default=0)

    avg_delivery_delay: Mapped[int] = mapped_column(Integer, nullable=True)
    reputation_score: Mapped[int] = mapped_column(Integer, default=50)