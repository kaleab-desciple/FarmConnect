from typing import List, Optional
from sqlalchemy.orm import Session

from shared_models import Product as ProductDTO
from app.infrastructure.db.mappers import orm_to_domain
from app.infrastructure.db.models import ProductORM
from app.domain.products.entities import Product as DomainProduct


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, product: DomainProduct) -> DomainProduct:
        orm = self.session.query(ProductORM).filter(ProductORM.id == product.id).one_or_none() if product.id else None
        
        if orm:
            # Update existing product
            from app.infrastructure.db.mappers import domain_to_orm
            updated_orm = domain_to_orm(product)
            for key, value in updated_orm.__dict__.items():
                if not key.startswith('_') and key != 'id':
                    setattr(orm, key, value)
        else:
            # Create new product
            from app.infrastructure.db.mappers import domain_to_orm
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

    def get_by_farmer_id(self, farmer_id: str) -> List[DomainProduct]:
        orms = (
            self.session.query(ProductORM)
            .filter(ProductORM.farmer_id == farmer_id)
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]

    def list_active(self) -> List[DomainProduct]:
        orms = (
            self.session.query(ProductORM)
            .filter(ProductORM.is_active == True)
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]

    def list_all(self) -> List[DomainProduct]:
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
        self.session.commit()
        return orm_to_domain(orm)

    def delete(self, product_id: str) -> bool:
        orm = (
            self.session.query(ProductORM)
            .filter(ProductORM.id == product_id)
            .one_or_none()
        )
        if not orm:
            return False
        self.session.delete(orm)
        self.session.commit()
        return True