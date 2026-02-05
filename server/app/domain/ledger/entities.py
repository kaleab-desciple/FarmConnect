from dataclasses import dataclass
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum


class AggregateType(Enum):
    USER = "USER"
    ESCROW = "ESCROW"
    SYSTEM = "SYSTEM"


class LedgerEventType(Enum):
    ESCROW_FUNDED = "ESCROW_FUNDED"
    ESCROW_RELEASED = "ESCROW_RELEASED"
    ESCROW_REFUNDED = "ESCROW_REFUNDED"
    PLATFORM_FEE_COLLECTED = "PLATFORM_FEE_COLLECTED"
    PENALTY_APPLIED = "PENALTY_APPLIED"


class Direction(Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class ReferenceType(Enum):
    ORDER = "ORDER"
    ESCROW = "ESCROW"
    DISPUTE = "DISPUTE"
    LOAN = "LOAN"


@dataclass(frozen=True)
class LedgerEvent:
    aggregate_type: AggregateType
    aggregate_id: str
    event_type: LedgerEventType
    amount: Decimal
    direction: Direction
    reference_type: ReferenceType
    reference_id: str
    id: Optional[str] = None
    currency: str = "ETB"
    event_metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None