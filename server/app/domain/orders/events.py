"""Domain events for the order and inventory lifecycle."""

from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, timezone


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class OrderCreated:
    order_id: str
    product_id: str
    quantity: Decimal
    timestamp: datetime = field(default_factory=_now)


@dataclass
class QuantityReserved:
    order_id: str
    product_id: str
    quantity: Decimal
    timestamp: datetime = field(default_factory=_now)


@dataclass
class SaleConfirmed:
    order_id: str
    product_id: str
    quantity: Decimal
    timestamp: datetime = field(default_factory=_now)


@dataclass
class ReservationReleased:
    order_id: str
    product_id: str
    quantity: Decimal
    reason: str
    timestamp: datetime = field(default_factory=_now)


@dataclass
class OrderCancelled:
    order_id: str
    reason: str
    timestamp: datetime = field(default_factory=_now)


@dataclass
class SpoilageRecorded:
    product_id: str
    quantity: Decimal
    reason: str
    timestamp: datetime = field(default_factory=_now)


@dataclass
class OrderUpdated:
    order_id: str
    timestamp: datetime = field(default_factory=_now)
