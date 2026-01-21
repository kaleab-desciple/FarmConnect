from typing import List, Optional
from sqlalchemy.orm import Session

from shared_models import Dispute
from app.infrastructure.db.mappers import dto_to_orm, orm_to_domain, domain_to_dto
from app.infrastructure.db.models import DisputeORM
from app.domain.disputes.entities import Dispute as DomainDispute


class DisputeRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, dispute: DomainDispute) -> DomainDispute:
        dto = domain_to_dto(dispute)
        orm = dto_to_orm(dto)
        merged_orm = self.session.merge(orm)
        self.session.flush()
        return orm_to_domain(merged_orm)

    def get_by_id(self, dispute_id: str) -> Optional[DomainDispute]:
        orm = (
            self.session.query(DisputeORM)
            .filter(DisputeORM.id == dispute_id)
            .one_or_none()
        )
        if not orm:
            return None
        return orm_to_domain(orm)

    def get_by_order_id(self, order_id: str) -> List[DomainDispute]:
        orms = (
            self.session.query(DisputeORM)
            .filter(DisputeORM.order_id == order_id)
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]

    def get_by_raised_by(self, raised_by: str) -> List[DomainDispute]:
        orms = (
            self.session.query(DisputeORM)
            .filter(DisputeORM.raised_by == raised_by)
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]

    def list_all(self) -> List[DomainDispute]:
        orms = self.session.query(DisputeORM).all()
        return [orm_to_domain(orm) for orm in orms]

    def update(self, dispute_id: str, updates: dict) -> Optional[DomainDispute]:
        orm = (
            self.session.query(DisputeORM)
            .filter(DisputeORM.id == dispute_id)
            .one_or_none()
        )
        if not orm:
            return None
        for key, value in updates.items():
            if hasattr(orm, key):
                setattr(orm, key, value)
        self.session.commit()
        return orm_to_domain(orm)

    def delete(self, dispute_id: str) -> bool:
        orm = (
            self.session.query(DisputeORM)
            .filter(DisputeORM.id == dispute_id)
            .one_or_none()
        )
        if not orm:
            return False
        self.session.delete(orm)
        self.session.commit()
        return True