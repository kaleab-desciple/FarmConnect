from uuid import uuid4
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, Enum as SAEnum, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import Base
from app.domain.accounting.entities import ReferenceType


class JournalEntryORM(Base):
    __tablename__ = "journal_entries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    reference_type: Mapped[str] = mapped_column(String)
    reference_id: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    lines: Mapped[list["JournalLineORM"]] = relationship("JournalLineORM", back_populates="journal_entry", cascade="all, delete-orphan")


class JournalLineORM(Base):
    __tablename__ = "journal_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    journal_entry_id: Mapped[str] = mapped_column(String, ForeignKey("journal_entries.id"))
    account_id: Mapped[str] = mapped_column(String, ForeignKey("accounts.id"))
    debit_amount: Mapped[Decimal] = mapped_column(Numeric(precision=15, scale=2), default=Decimal(0))
    credit_amount: Mapped[Decimal] = mapped_column(Numeric(precision=15, scale=2), default=Decimal(0))

    journal_entry: Mapped[JournalEntryORM] = relationship("JournalEntryORM", back_populates="lines")