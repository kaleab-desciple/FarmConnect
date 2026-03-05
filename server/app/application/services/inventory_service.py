"""
Application service for inventory management with concurrency control.

This service orchestrates all inventory operations:
- reserve_stock: Reserve quantity for an order (merchant places order)
- confirm_sale: Move reserved → sold (escrow funded)
- release_reservation: Release reserved back to available (order cancelled)
- record_spoilage: Record spoiled goods (reduces available)
- adjust_stock: Add stock (partial harvest, admin correction)
- process_return: Handle returns (add back to available)

Uses pessimistic locking (SELECT ... FOR UPDATE) to prevent overselling
when concurrent merchants order the same product.
"""

from typing import Optional
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.domain.products.entities import Product, InsufficientStockError
from app.domain.products.inventory import InventoryMovement, ProductBatch
from app.domain.common.enums import InventoryMovementType
from app.domain.orders.rules import InventoryPolicy
from app.infrastructure.repositories.product_repo import ProductRepository
from app.infrastructure.repositories.inventory_repo import InventoryMovementRepository, ProductBatchRepository


class InventoryServiceError(Exception):
    """Base exception for inventory service errors."""
    pass


class ProductNotFoundError(InventoryServiceError):
    """Raised when product is not found."""
    pass


class InsufficientStockError(InventoryServiceError):
    """Raised when requested quantity exceeds available stock."""
    def __init__(self, product_id: str, available: Decimal, requested: Decimal):
        self.product_id = product_id
        self.available = available
        self.requested = requested
        super().__init__(
            f"Insufficient stock for product {product_id}: "
            f"{available} available, {requested} requested"
        )


class ReservationFailedError(InventoryServiceError):
    """Raised when a stock reservation fails due to policy."""
    def __init__(self, product_id: str, reason: str):
        self.product_id = product_id
        self.reason = reason
        super().__init__(f"Reservation failed for product {product_id}: {reason}")


class InventoryService:
    """
    Application service: orchestrates inventory with concurrency control.
    
    Uses pessimistic locking (SELECT ... FOR UPDATE) to prevent overselling
    when multiple merchants order the same product simultaneously.
    """

    def __init__(self, session: Session):
        self.session = session
        self.product_repo = ProductRepository(session)
        self.movement_repo = InventoryMovementRepository(session)
        self.batch_repo = ProductBatchRepository(session)

    def reserve_stock(
        self, 
        product_id: str, 
        order_id: str, 
        qty: Decimal,
        batch_id: Optional[str] = None
    ) -> Product:
        """
        Reserve quantity for an order (merchant places order).
        
        Flow:
        1. BEGIN TRANSACTION
        2. SELECT product FOR UPDATE (pessimistic lock)
        3. InventoryPolicy.can_reserve(product, qty)
        4. product.reserve(qty)
        5. Append InventoryMovement(RESERVATION, -qty, ref=ORDER)
        6. Save product
        7. COMMIT
        
        Args:
            product_id: Product to reserve from
            order_id: Order reference
            qty: Quantity to reserve
            batch_id: Optional batch to reserve from
            
        Returns:
            Updated Product entity
            
        Raises:
            ProductNotFoundError: Product doesn't exist
            InsufficientStockError: Not enough stock available
        """
        # Lock the product row for update (prevents concurrent overselling)
        product = self.product_repo.get_for_update(product_id)
        
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")
        
        # Check availability using domain policy
        can_reserve, reason = InventoryPolicy.can_reserve(product, qty)
        if not can_reserve:
            if "Insufficient stock" in reason:
                raise InsufficientStockError(product.id, product.available_quantity, qty)
            else:
                raise ReservationFailedError(product.id, reason)
        
        # Reserve quantity on product aggregate
        product.reserve(qty)
        
        # Record the movement in the event-sourced ledger
        movement = InventoryMovement(
            product_id=product_id,
            batch_id=batch_id,
            movement_type=InventoryMovementType.RESERVATION,
            quantity=-qty,  # Negative = stock out
            reference_type="ORDER",
            reference_id=order_id,
            notes=f"Reserved for order {order_id}",
            created_at=datetime.now(timezone.utc)
        )
        self.movement_repo.append(movement)
        
        # Save updated product
        self.product_repo.save(product)
        
        return product

    def confirm_sale(
        self, 
        product_id: str, 
        order_id: str, 
        qty: Decimal,
        batch_id: Optional[str] = None
    ) -> Product:
        """
        Confirm sale - move reserved → sold (escrow funded).
        
        When escrow is funded, the reserved quantity becomes sold.
        
        Args:
            product_id: Product sold
            order_id: Order reference
            qty: Quantity sold
            batch_id: Optional batch sold from
            
        Returns:
            Updated Product entity
            
        Raises:
            ProductNotFoundError: Product doesn't exist
        """
        # Lock the product row for update
        product = self.product_repo.get_for_update(product_id)
        
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")
        
        # Move reserved → sold
        product.confirm_sale(qty)
        
        # Record the movement
        movement = InventoryMovement(
            product_id=product_id,
            batch_id=batch_id,
            movement_type=InventoryMovementType.SALE_CONFIRMED,
            quantity=-qty,  # Still negative (reserved was already accounted)
            reference_type="ORDER",
            reference_id=order_id,
            notes=f"Sale confirmed for order {order_id}",
            created_at=datetime.now(timezone.utc)
        )
        self.movement_repo.append(movement)
        
        # Save updated product
        self.product_repo.save(product)
        
        return product

    def release_reservation(
        self, 
        product_id: str, 
        order_id: str, 
        qty: Decimal,
        reason: str,
        batch_id: Optional[str] = None
    ) -> Product:
        """
        Release reserved quantity back to available (order cancelled).
        
        When merchant cancels before escrow funded, release the reserved stock.
        
        Args:
            product_id: Product to release
            order_id: Order reference
            qty: Quantity to release
            reason: Reason for release (e.g., "order_cancelled", "escrow_failed")
            batch_id: Optional batch
            
        Returns:
            Updated Product entity
        """
        # Lock the product row for update
        product = self.product_repo.get_for_update(product_id)
        
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")
        
        # Release reservation
        product.release_reservation(qty)
        
        # Record the movement (positive = stock back in)
        movement = InventoryMovement(
            product_id=product_id,
            batch_id=batch_id,
            movement_type=InventoryMovementType.RESERVATION_RELEASE,
            quantity=qty,  # Positive = stock back in
            reference_type="ORDER",
            reference_id=order_id,
            notes=f"Reservation released: {reason}",
            created_at=datetime.now(timezone.utc)
        )
        self.movement_repo.append(movement)
        
        # Save updated product
        self.product_repo.save(product)
        
        return product

    def record_spoilage(
        self, 
        product_id: str, 
        qty: Decimal, 
        reason: str,
        user_id: str,
        batch_id: Optional[str] = None
    ) -> Product:
        """
        Record spoiled quantity (farmer reports spoilage).
        
        Reduces available stock by the spoiled amount.
        
        Args:
            product_id: Product with spoilage
            qty: Quantity spoiled
            reason: Reason for spoilage
            user_id: User reporting spoilage
            batch_id: Optional batch
            
        Returns:
            Updated Product entity
        """
        # Lock the product row for update
        product = self.product_repo.get_for_update(product_id)
        
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")
        
        # Record spoilage on product
        product.record_spoilage(qty)
        
        # Record the movement (negative = stock out)
        movement = InventoryMovement(
            product_id=product_id,
            batch_id=batch_id,
            movement_type=InventoryMovementType.SPOILAGE,
            quantity=-qty,
            reference_type="SPOILAGE",
            reference_id=product_id,
            notes=reason,
            created_by=user_id,
            created_at=datetime.now(timezone.utc)
        )
        self.movement_repo.append(movement)
        
        # Save updated product
        self.product_repo.save(product)
        
        return product

    def adjust_stock(
        self, 
        product_id: str, 
        qty: Decimal, 
        reason: str,
        user_id: str,
        batch_id: Optional[str] = None
    ) -> Product:
        """
        Adjust stock (farmer adds partial harvest, admin correction).
        
        Args:
            product_id: Product to adjust
            qty: Quantity to add (positive) or remove (negative)
            reason: Reason for adjustment
            user_id: User making adjustment
            batch_id: Optional batch
            
        Returns:
            Updated Product entity
        """
        # Lock the product row for update
        product = self.product_repo.get_for_update(product_id)
        
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")
        
        if qty > 0:
            # Adding stock
            product.add_stock(qty)
            movement_qty = qty
            movement_type = InventoryMovementType.STOCK_IN
        else:
            # Removing stock (should check availability first)
            remove_qty = abs(qty)
            can_reserve, _ = InventoryPolicy.can_reserve(product, remove_qty)
            if not can_reserve:
                raise InsufficientStockError(product.id, product.available_quantity, remove_qty)
            
            # For removal, we adjust total_quantity directly
            product.total_quantity -= remove_qty
            movement_qty = qty
            movement_type = InventoryMovementType.ADJUSTMENT
        
        # Record the movement
        movement = InventoryMovement(
            product_id=product_id,
            batch_id=batch_id,
            movement_type=movement_type,
            quantity=movement_qty,
            reference_type="ADJUSTMENT",
            reference_id=product_id,
            notes=reason,
            created_by=user_id,
            created_at=datetime.now(timezone.utc)
        )
        self.movement_repo.append(movement)
        
        # Save updated product
        self.product_repo.save(product)
        
        return product

    def process_return(
        self, 
        product_id: str, 
        order_id: str, 
        qty: Decimal,
        reason: str,
        batch_id: Optional[str] = None
    ) -> Product:
        """
        Process return (delivery failure, quality issue).
        
        Returns stock back to available after a failed delivery or return.
        
        Args:
            product_id: Product being returned
            order_id: Original order reference
            qty: Quantity returned
            reason: Reason for return
            batch_id: Optional batch
            
        Returns:
            Updated Product entity
        """
        # Lock the product row for update
        product = self.product_repo.get_for_update(product_id)
        
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")
        
        # Reduce sold quantity (return reverses the sale)
        # Note: This assumes the sale was already confirmed
        if qty > product.sold_quantity:
            qty = product.sold_quantity  # Can't return more than sold
        
        product.sold_quantity -= qty
        
        # Record the movement (positive = stock back in)
        movement = InventoryMovement(
            product_id=product_id,
            batch_id=batch_id,
            movement_type=InventoryMovementType.RETURN,
            quantity=qty,
            reference_type="ORDER",
            reference_id=order_id,
            notes=f"Return processed: {reason}",
            created_at=datetime.now(timezone.utc)
        )
        self.movement_repo.append(movement)
        
        # Save updated product
        self.product_repo.save(product)
        
        return product

    # ========== Batch Operations ==========
    
    def create_batch(
        self,
        product_id: str,
        batch_code: str,
        initial_qty: Decimal,
        harvest_date: Optional[datetime] = None,
        expiry_date: Optional[datetime] = None,
        quality_grade: Optional[str] = None
    ) -> ProductBatch:
        """
        Create a new batch for a product.
        
        Args:
            product_id: Product this batch belongs to
            batch_code: Unique batch code
            initial_qty: Initial quantity in batch
            harvest_date: When harvested
            expiry_date: Expiration date
            quality_grade: Quality grade
            
        Returns:
            Created ProductBatch
        """
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")
        
        batch = ProductBatch(
            product_id=product_id,
            batch_code=batch_code,
            total_quantity=initial_qty,
            harvest_date=harvest_date.date() if harvest_date else None,
            expiry_date=expiry_date.date() if expiry_date else None,
            quality_grade=quality_grade,
            created_at=datetime.now(timezone.utc)
        )
        
        saved_batch = self.batch_repo.save(batch)
        
        # Also record stock in movement
        movement = InventoryMovement(
            product_id=product_id,
            batch_id=saved_batch.id,
            movement_type=InventoryMovementType.STOCK_IN,
            quantity=initial_qty,
            reference_type="BATCH",
            reference_id=saved_batch.id,
            notes=f"Batch {batch_code} created with {initial_qty} units",
            created_at=datetime.now(timezone.utc)
        )
        self.movement_repo.append(movement)
        
        return saved_batch

    def get_inventory_history(self, product_id: str) -> list[InventoryMovement]:
        """
        Get complete inventory movement history for a product.
        
        This is the event-sourced ledger - the truth of all inventory changes.
        
        Args:
            product_id: Product to get history for
            
        Returns:
            List of all inventory movements for this product
        """
        return self.movement_repo.get_by_product(product_id)

    def get_inventory_balance(self, product_id: str) -> Decimal:
        """
        Get the current inventory balance from the event-sourced ledger.
        
        This is calculated as SUM(quantity) of all movements.
        Should equal: total_quantity - reserved_quantity - sold_quantity - spoiled_quantity
        
        Args:
            product_id: Product to get balance for
            
        Returns:
            Net inventory balance (positive = stock in, negative = stock out)
        """
        return self.movement_repo.get_balance(product_id)
