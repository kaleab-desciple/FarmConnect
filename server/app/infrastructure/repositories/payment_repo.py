from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from shared_models import Escrow
from app.infrastructure.db.mappers import dto_to_orm, orm_to_domain, domain_to_dto
from app.infrastructure.db.models import EscrowORM
from app.domain.payments.entities import Escrow as DomainEscrow


class EscrowRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, escrow: DomainEscrow) -> DomainEscrow:
        dto = domain_to_dto(escrow)
        orm = dto_to_orm(dto)
        merged_orm = self.session.merge(orm)
        self.session.flush()  # to get id if new
        return orm_to_domain(merged_orm)

    def get_by_id(self, escrow_id: str) -> Optional[DomainEscrow]:
        orm = (
            self.session.query(EscrowORM)
            .filter(EscrowORM.id == escrow_id)
            .one_or_none()
        )
        if not orm:
            return None
        return orm_to_domain(orm)

    def get_by_order_id(self, order_id: str) -> Optional[DomainEscrow]:
        orm = (
            self.session.query(EscrowORM)
            .filter(EscrowORM.order_id == order_id)
            .one_or_none()
        )
        if not orm:
            return None
        return orm_to_domain(orm)

    def list_all(self) -> List[DomainEscrow]:
        orms = self.session.query(EscrowORM).all()
        return [orm_to_domain(orm) for orm in orms]

    def update(self, escrow_id: str, updates: dict) -> Optional[DomainEscrow]:
        orm = (
            self.session.query(EscrowORM)
            .filter(EscrowORM.id == escrow_id)
            .one_or_none()
        )
        if not orm:
            return None
        for key, value in updates.items():
            if hasattr(orm, key):
                setattr(orm, key, value)
        self.session.commit()
        return orm_to_domain(orm)

    def delete(self, escrow_id: str) -> bool:
        orm = (
            self.session.query(EscrowORM)
            .filter(EscrowORM.id == escrow_id)
            .one_or_none()
        )
        if not orm:
            return False
        self.session.delete(orm)
        self.session.commit()
        return True