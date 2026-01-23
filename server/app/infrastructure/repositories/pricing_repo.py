from typing import List
from sqlalchemy.orm import Session
from app.infrastructure.db.mappers import orm_to_domain
from app.infrastructure.db.models.pricing import PricingRuleORM
from app.domain.pricing.entities import PricingRule


class PricingRuleRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_active_rules(self) -> List[PricingRule]:
        """Get all active pricing rules ordered by priority."""
        orms = (
            self.session.query(PricingRuleORM)
            .filter(PricingRuleORM.active == True)
            .order_by(PricingRuleORM.priority.desc())
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]