from dataclasses import dataclass
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum
from uuid import UUID


class OwnerType(Enum):
    USER = "USER"
    ESCROW = "ESCROW"
    SYSTEM = "SYSTEM"


class AccountType(Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class ReferenceType(Enum):
    ORDER = "ORDER"
    ESCROW = "ESCROW"
    DISPUTE = "DISPUTE"
    LOAN = "LOAN"


@dataclass(frozen=True)
class Account:
    id: UUID
    owner_type: OwnerType
    owner_id: str
    account_type: AccountType
    name: str
    currency: str
    created_at: datetime


@dataclass(frozen=True)
class JournalLine:
    account_id: UUID
    debit_amount: Decimal
    credit_amount: Decimal


@dataclass(frozen=True)
class JournalEntry:
    id: UUID
    reference_type: ReferenceType
    reference_id: str
    description: str
    lines: List[JournalLine]
    created_at: datetime