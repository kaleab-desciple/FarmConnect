from typing import Optional
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime
from shared_models.enums import OrderStatus

@dataclass(frozen=True)
class Order:
    id: Optional[str] = None
    farmer_id: Optional[str] = None
    merchant_id: Optional[str] = None
    product_id: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    delivery_cost: Optional[Decimal] = None
    platform_fee: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    status: Optional[OrderStatus] = None
    escrow_id: Optional[str] = None
    created_at: Optional[datetime] = None
