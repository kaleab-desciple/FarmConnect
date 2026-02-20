"""
Product repository with concurrency control (SELECT ... FOR UPDATE).

Supports:
- Pessimistic locking via get_for_update()
- Soft delete (deleted_at) instead of hard delete
- Active product listing filters out soft-deleted products
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from shared_models import Product as ProductDTO
from app.infrastructure.db.mappers import orm_to_domain, domain_to_orm
from app.infrastructure.db.models import ProductORM
from app.domain.products.entities import Product as DomainProduct


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, product: DomainProduct) -> DomainProduct:
        orm = (
            self.session.query(ProductORM)
            .filter(ProductORM.id == product.id)
            .one_or_none()
        ) if product.id else None

        if orm:
            # Update existing product
            updated_orm = domain_to_orm(product)
            for key, value in updated_orm.__dict__.items():
                if not key.startswith('_') and key != 'id':
                    setattr(orm, key, value)
        else:
            # Create new product
            orm = domain_to_orm(product)
            self.session.add(orm)

        self.session.flush()
        return orm_to_domain(orm)

    def get_by_id(self, product_id: str) -> Optional[DomainProduct]:
        orm = (
            self.session.query(ProductORM)
            .filter(ProductORM.id == product_id)
            .one_or_none()
        )
        if not orm:
            return None
        return orm_to_domain(orm)

    def get_for_update(self, product_id: str) -> Optional[DomainProduct]:
        """
        SELECT ... FOR UPDATE — pessimistic lock for concurrency control.

        Use this when modifying inventory quantities to prevent overselling.
        The row lock is held until the transaction commits or rolls back.
        """
        orm = (
            self.session.query(ProductORM)
            .filter(ProductORM.id == product_id)
            .with_for_update()
            .one_or_none()
        )
        if not orm:
            return None
        return orm_to_domain(orm)

    def get_by_farmer_id(self, farmer_id: str) -> List[DomainProduct]:
        orms = (
            self.session.query(ProductORM)
            .filter(
                ProductORM.farmer_id == farmer_id,
                ProductORM.deleted_at.is_(None),
            )
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]

    def list_active(self) -> List[DomainProduct]:
        """List active products, excluding soft-deleted ones."""
        orms = (
            self.session.query(ProductORM)
            .filter(
                ProductORM.is_active == True,
                ProductORM.deleted_at.is_(None),
            )
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]

    def list_all(self) -> List[DomainProduct]:
        """List all products (including soft-deleted, for admin/audit)."""
        orms = self.session.query(ProductORM).all()
        return [orm_to_domain(orm) for orm in orms]

    def update(self, product_id: str, updates: dict) -> Optional[DomainProduct]:
        orm = (
            self.session.query(ProductORM)
            .filter(ProductORM.id == product_id)
            .one_or_none()
        )
        if not orm:
            return None
        for key, value in updates.items():
            if hasattr(orm, key):
                setattr(orm, key, value)
        self.session.flush()
        return orm_to_domain(orm)

    def update_with_version(self, product: DomainProduct) -> Optional[DomainProduct]:
        """
        Optimistic concurrency: update only if version matches.

        Returns None if version conflict (stale write detected).
        """
        orm = (
            self.session.query(ProductORM)
            .filter(
                ProductORM.id == product.id,
                ProductORM.version == product.version,
            )
            .one_or_none()
        )
        if not orm:
            return None  # Version conflict or not found

        updated_orm = domain_to_orm(product)
        for key, value in updated_orm.__dict__.items():
            if not key.startswith('_') and key not in ('id', 'version'):
                setattr(orm, key, value)
        orm.version = product.version + 1
        self.session.flush()
        return orm_to_domain(orm)

    def soft_delete(self, product_id: str) -> bool:
        """Soft delete: set deleted_at, deactivate. Keeps row for audit."""
        orm = (
            self.session.query(ProductORM)
            .filter(ProductORM.id == product_id)
            .one_or_none()
        )
        if not orm:
            return False
        from datetime import datetime, timezone
        orm.deleted_at = datetime.now(timezone.utc)
        orm.is_active = False
        self.session.flush()
        return True

    def delete(self, product_id: str) -> bool:
        """Hard delete — use soft_delete instead for production."""
        orm = (
            self.session.query(ProductORM)
            .filter(ProductORM.id == product_id)
            .one_or_none()
        )
        if not orm:
            return False
        self.session.delete(orm)
        self.session.flush()
        return True