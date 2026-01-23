from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from app.domain.common.enums import DisputeResolution


@dataclass(frozen=True)
class DomainEvent:
    pass


@dataclass(frozen=True)
class OrderCompleted(DomainEvent):
    order_id: str
    farmer_id: str
    merchant_id: str
    was_successful: bool
    delivery_delay_days: Optional[int] = None


@dataclass(frozen=True)
class DisputeResolved(DomainEvent):
    dispute_id: str
    order_id: str
    raised_by: str
    resolution: DisputeResolution
    penalty_amount: Decimal = Decimal(0)
    winner: Optional[str] = None  # 'farmer' or 'merchant'


@dataclass(frozen=True)
class PenaltyApplied(DomainEvent):
    user_id: str
    order_id: str
    amount: Decimal
    reason: str