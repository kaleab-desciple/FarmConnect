from typing import List, Optional
from sqlalchemy.orm import Session

from shared_models import Order
from app.infrastructure.db.mappers import dto_to_orm, orm_to_domain, domain_to_dto
from app.infrastructure.db.models import OrderORM
from app.domain.orders.entities import Order as DomainOrder


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, order: DomainOrder) -> DomainOrder:
        dto = domain_to_dto(order)
        orm = dto_to_orm(dto)
        merged_orm = self.session.merge(orm)
        self.session.flush()  # to get id
        return orm_to_domain(merged_orm)

    def get_by_id(self, order_id: str) -> Optional[DomainOrder]:
        orm = (
            self.session.query(OrderORM)
            .filter(OrderORM.id == order_id)
            .one_or_none()
        )
        if not orm:
            return None
        return orm_to_domain(orm)

    def get_by_farmer_id(self, farmer_id: str) -> List[DomainOrder]:
        orms = (
            self.session.query(OrderORM)
            .filter(OrderORM.farmer_id == farmer_id)
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]

    def get_by_merchant_id(self, merchant_id: str) -> List[DomainOrder]:
        orms = (
            self.session.query(OrderORM)
            .filter(OrderORM.merchant_id == merchant_id)
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]

    def list_all(self) -> List[DomainOrder]:
        orms = self.session.query(OrderORM).all()
        return [orm_to_domain(orm) for orm in orms]

    def update(self, order_id: str, updates: dict) -> Optional[DomainOrder]:
        orm = (
            self.session.query(OrderORM)
            .filter(OrderORM.id == order_id)
            .one_or_none()
        )
        if not orm:
            return None
        for key, value in updates.items():
            if hasattr(orm, key):
                setattr(orm, key, value)
        self.session.commit()
        return orm_to_domain(orm)

    def delete(self, order_id: str) -> bool:
        orm = (
            self.session.query(OrderORM)
            .filter(OrderORM.id == order_id)
            .one_or_none()
        )
        if not orm:
            return False
        self.session.delete(orm)
        self.session.commit()
        return True
