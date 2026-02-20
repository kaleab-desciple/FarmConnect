from typing import Optional
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime
from app.domain.common.enums import OrderStatus


@dataclass
class Order:
    id: Optional[str] = None
    farmer_id: Optional[str] = None
    merchant_id: Optional[str] = None
    product_id: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    subtotal: Optional[Decimal] = None
    delivery_cost: Optional[Decimal] = None
    delivery_fee: Optional[Decimal] = None
    delivery_margin: Optional[Decimal] = None
    quality_fee: Optional[Decimal] = None
    platform_fee: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    status: Optional[OrderStatus] = None
    escrow_id: Optional[str] = None
    batch_id: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    cancelled_reason: Optional[str] = None
    delivered_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
