"""
Order business rules — Specification pattern for composable checks.
"""

from decimal import Decimal
from datetime import date
from typing import Tuple

from app.domain.products.entities import Product


class InventoryPolicy:
    """Specification pattern: composable availability checks."""

    @staticmethod
    def can_reserve(product: Product, requested_qty: Decimal) -> Tuple[bool, str]:
        """
        Check if the given quantity can be reserved from this product.

        Returns (True, "") on success, (False, reason) on failure.
        """
        if product.deleted_at:
            return False, "Product is no longer available"

        if product.expiry_date and product.expiry_date < date.today():
            return False, "Product has expired"

        if not product.is_active:
            return False, "Product listing is inactive"

        if requested_qty <= 0:
            return False, "Requested quantity must be positive"

        if requested_qty > product.available_quantity:
            return (
                False,
                f"Insufficient stock: {product.available_quantity} available, "
                f"{requested_qty} requested",
            )

        return True, ""

    @staticmethod
    def can_soft_delete(product: Product) -> Tuple[bool, str]:
        """Check if a product can be soft-deleted."""
        if product.reserved_quantity > 0:
            return False, "Cannot delete product with active reservations"
        return True, ""


class OrderRules:
    """Business rules for order operations."""

    @staticmethod
    def can_cancel_order(order_status: str) -> bool:
        """Check if an order can be cancelled based on its current status."""
        from app.domain.common.enums import OrderStatus
        cancellable = [OrderStatus.CREATED, OrderStatus.PENDING_PAYMENT]
        try:
            status = OrderStatus(order_status)
            return status in cancellable
        except ValueError:
            return False

    @staticmethod
    def can_modify_quantity(order_status: str) -> bool:
        """Check if order quantity can be modified."""
        from app.domain.common.enums import OrderStatus
        modifiable = [OrderStatus.CREATED, OrderStatus.PENDING_PAYMENT]
        try:
            status = OrderStatus(order_status)
            return status in modifiable
        except ValueError:
            return False