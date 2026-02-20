"""
Repository for inventory management: InventoryMovements and ProductBatches.

InventoryMovementRepository is append-only (event sourcing).
ProductBatchRepository supports standard CRUD.
"""

from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.infrastructure.db.models.inventory import InventoryMovementORM, ProductBatchORM
from app.domain.products.inventory import InventoryMovement, ProductBatch
from app.infrastructure.db.mappers import orm_to_domain, domain_to_orm


class InventoryMovementRepository:
    """Append-only event-sourced inventory ledger."""

    def __init__(self, session: Session):
        self.session = session

    def append(self, movement: InventoryMovement) -> InventoryMovement:
        """Append a movement event (never update or delete)."""
        orm = domain_to_orm(movement)
        self.session.add(orm)
        self.session.flush()
        return orm_to_domain(orm)

    def get_by_product(self, product_id: str) -> List[InventoryMovement]:
        """Get all movements for a product, ordered by creation time."""
        orms = (
            self.session.query(InventoryMovementORM)
            .filter(InventoryMovementORM.product_id == product_id)
            .order_by(InventoryMovementORM.created_at.asc())
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]

    def get_by_reference(self, reference_type: str, reference_id: str) -> List[InventoryMovement]:
        """Get all movements for a given reference (e.g., ORDER + order_id)."""
        orms = (
            self.session.query(InventoryMovementORM)
            .filter(
                InventoryMovementORM.reference_type == reference_type,
                InventoryMovementORM.reference_id == reference_id,
            )
            .order_by(InventoryMovementORM.created_at.asc())
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]

    def get_balance(self, product_id: str) -> Decimal:
        """
        Event-sourced truth: SUM(quantity) for product.
        Positive = net stock in, Negative = net stock out.
        """
        result = (
            self.session.query(func.coalesce(func.sum(InventoryMovementORM.quantity), 0))
            .filter(InventoryMovementORM.product_id == product_id)
            .scalar()
        )
        return Decimal(str(result))


class ProductBatchRepository:
    """Repository for product batch management."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, batch: ProductBatch) -> ProductBatch:
        """Create or update a product batch."""
        orm = (
            self.session.query(ProductBatchORM)
            .filter(ProductBatchORM.id == batch.id)
            .one_or_none()
        ) if batch.id else None

        if orm:
            # Update existing
            updated = domain_to_orm(batch)
            for key, value in updated.__dict__.items():
                if not key.startswith("_") and key != "id":
                    setattr(orm, key, value)
        else:
            orm = domain_to_orm(batch)
            self.session.add(orm)

        self.session.flush()
        return orm_to_domain(orm)

    def get_by_id(self, batch_id: str) -> Optional[ProductBatch]:
        orm = (
            self.session.query(ProductBatchORM)
            .filter(ProductBatchORM.id == batch_id)
            .one_or_none()
        )
        if not orm:
            return None
        return orm_to_domain(orm)

    def get_active_by_product(self, product_id: str) -> List[ProductBatch]:
        """Get all active batches for a product."""
        orms = (
            self.session.query(ProductBatchORM)
            .filter(
                ProductBatchORM.product_id == product_id,
                ProductBatchORM.is_active == True,
            )
            .order_by(ProductBatchORM.created_at.asc())
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]

    def get_all_by_product(self, product_id: str) -> List[ProductBatch]:
        """Get all batches (active and inactive) for a product."""
        orms = (
            self.session.query(ProductBatchORM)
            .filter(ProductBatchORM.product_id == product_id)
            .order_by(ProductBatchORM.created_at.asc())
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]
