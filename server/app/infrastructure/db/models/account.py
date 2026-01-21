from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import String, Enum as SAEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base
from app.domain.accounting.entities import OwnerType, AccountType


class AccountORM(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    owner_type: Mapped[OwnerType] = mapped_column(SAEnum(OwnerType, name='owner_type_enum'))
    owner_id: Mapped[str] = mapped_column(String)
    account_type: Mapped[AccountType] = mapped_column(SAEnum(AccountType, name='account_type_enum'))
    name: Mapped[str] = mapped_column(String)
    currency: Mapped[str] = mapped_column(String, default="ETB")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))