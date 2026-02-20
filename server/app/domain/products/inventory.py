"""
Inventory domain entities: InventoryMovement (event-sourced ledger) and ProductBatch.

InventoryMovement uses signed quantities:
  - Positive = stock in (STOCK_IN, RETURN, ADJUSTMENT)
  - Negative = stock out (RESERVATION, SALE_CONFIRMED, SPOILAGE, EXPIRY)

Available balance = SUM(quantity) over all movements for a product.
"""

from decimal import Decimal
from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass

from app.domain.common.enums import InventoryMovementType, QualityGrade


@dataclass(frozen=True)
class InventoryMovement:
    """Immutable event in the inventory ledger."""
    product_id: str
    movement_type: InventoryMovementType
    quantity: Decimal                    # positive = in, negative = out
    reference_type: str                  # 'ORDER', 'SPOILAGE', 'ADJUSTMENT', 'RETURN'
    reference_id: str
    id: Optional[str] = None
    batch_id: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class ProductBatch:
    """A distinct batch of a product (different harvest lot, date, grade)."""
    product_id: str
    batch_code: str
    total_quantity: Decimal = Decimal(0)
    reserved_quantity: Decimal = Decimal(0)
    sold_quantity: Decimal = Decimal(0)
    spoiled_quantity: Decimal = Decimal(0)
    id: Optional[str] = None
    harvest_date: Optional[date] = None
    expiry_date: Optional[date] = None
    quality_grade: Optional[QualityGrade] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

    @property
    def available_quantity(self) -> Decimal:
        return (
            self.total_quantity
            - self.reserved_quantity
            - self.sold_quantity
            - self.spoiled_quantity
        )
