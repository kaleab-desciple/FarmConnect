from typing import Optional
from sqlalchemy.orm import Session

from app.infrastructure.db.mappers import dto_to_orm, orm_to_domain, domain_to_dto
from app.infrastructure.db.models import ReputationORM
from app.domain.reputation.entities import Reputation


class ReputationRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, reputation: Reputation) -> Reputation:
        dto = domain_to_dto(reputation)
        orm = dto_to_orm(dto)
        merged_orm = self.session.merge(orm)
        self.session.flush()
        return orm_to_domain(merged_orm)

    def get_by_user_id(self, user_id: str) -> Optional[Reputation]:
        orm = (
            self.session.query(ReputationORM)
            .filter(ReputationORM.user_id == user_id)
            .one_or_none()
        )
        if not orm:
            return None
        return orm_to_domain(orm)

    def create_or_get(self, user_id: str) -> Reputation:
        existing = self.get_by_user_id(user_id)
        if existing:
            return existing
        reputation = Reputation(user_id=user_id)
        return self.save(reputation)