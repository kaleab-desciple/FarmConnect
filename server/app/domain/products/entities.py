from decimal import Decimal
from datetime import datetime, date, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

from app.domain.common.enums import Category, Unit, QualityGrade, ProductStatus


class InsufficientStockError(Exception):
    """Raised when requested quantity exceeds available stock."""
    def __init__(self, product_id: str, available: Decimal, requested: Decimal):
        self.product_id = product_id
        self.available = available
        self.requested = requested
        super().__init__(
            f"Insufficient stock for product {product_id}: "
            f"{available} available, {requested} requested"
        )


class InvalidQuantityError(Exception):
    """Raised when a quantity operation is invalid."""
    pass


@dataclass
class Product:
    """Product Aggregate Root with inventory invariant methods."""
    category: Category
    unit: Unit
    base_price: Decimal
    id: Optional[str] = None
    farmer_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    currency: Optional[str] = "USD"
    total_quantity: Decimal = Decimal(0)
    reserved_quantity: Decimal = Decimal(0)
    sold_quantity: Decimal = Decimal(0)
    spoiled_quantity: Decimal = Decimal(0)
    quality_grade: Optional[QualityGrade] = None
    harvest_id: Optional[str] = None
    crop_cycle_id: Optional[str] = None
    harvest_date: Optional[date] = None
    expiry_date: Optional[date] = None
    location: Optional[Dict[str, Any]] = None
    images: Optional[List[str]] = None
    is_active: Optional[bool] = True
    metadata: Optional[Dict[str, Any]] = None
    deleted_at: Optional[datetime] = None
    version: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def available_quantity(self) -> Decimal:
        """Derived quantity: never stored in DB."""
        return (
            self.total_quantity
            - self.reserved_quantity
            - self.sold_quantity
            - self.spoiled_quantity
        )

    @property
    def status(self) -> ProductStatus:
        """Computed product status based on current state."""
        if self.deleted_at:
            return ProductStatus.DISCONTINUED
        if self.expiry_date and self.expiry_date < date.today():
            return ProductStatus.EXPIRED
        if self.available_quantity <= 0:
            return ProductStatus.SOLD_OUT
        if self.available_quantity < self.total_quantity * Decimal("0.1"):
            return ProductStatus.LOW_STOCK
        return ProductStatus.AVAILABLE

    def reserve(self, qty: Decimal) -> None:
        """Reserve quantity for an order. Raises if insufficient stock."""
        if qty <= 0:
            raise InvalidQuantityError("Reservation quantity must be positive")
        if qty > self.available_quantity:
            raise InsufficientStockError(self.id, self.available_quantity, qty)
        self.reserved_quantity += qty

    def confirm_sale(self, qty: Decimal) -> None:
        """Move reserved quantity to sold (escrow funded)."""
        if qty <= 0:
            raise InvalidQuantityError("Sale quantity must be positive")
        if qty > self.reserved_quantity:
            raise InvalidQuantityError(
                f"Cannot confirm {qty}: only {self.reserved_quantity} reserved"
            )
        self.reserved_quantity -= qty
        self.sold_quantity += qty

    def release_reservation(self, qty: Decimal) -> None:
        """Release reserved quantity back to available (order cancelled)."""
        if qty <= 0:
            raise InvalidQuantityError("Release quantity must be positive")
        self.reserved_quantity = max(Decimal(0), self.reserved_quantity - qty)

    def record_spoilage(self, qty: Decimal) -> None:
        """Record spoiled quantity, reducing available stock."""
        if qty <= 0:
            raise InvalidQuantityError("Spoilage quantity must be positive")
        if qty > self.available_quantity:
            raise InvalidQuantityError(
                f"Spoilage {qty} exceeds available {self.available_quantity}"
            )
        self.spoiled_quantity += qty

    def add_stock(self, qty: Decimal) -> None:
        """Add stock (partial harvest, adjustment)."""
        if qty <= 0:
            raise InvalidQuantityError("Stock addition must be positive")
        self.total_quantity += qty

    def soft_delete(self) -> None:
        """Soft delete: set deleted_at, deactivate. Keeps row for audit."""
        self.deleted_at = datetime.now(timezone.utc)
        self.is_active = False