from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from shared_models import Loan
from app.infrastructure.db.mappers import dto_to_orm, orm_to_domain
from app.infrastructure.db.models import LoanORM
from app.domain.loans.entities import Loan as DomainLoan


class LoanRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, loan: Loan) -> None:
        orm = dto_to_orm(loan)
        self.session.add(orm)
        self.session.commit()

    def get_by_id(self, loan_id: UUID) -> Optional[DomainLoan]:
        orm = (
            self.session.query(LoanORM)
            .filter(LoanORM.id == str(loan_id))
            .one_or_none()
        )
        if not orm:
            return None
        return orm_to_domain(orm)

    def get_by_farmer_id(self, farmer_id: UUID) -> List[DomainLoan]:
        orms = (
            self.session.query(LoanORM)
            .filter(LoanORM.farmer_id == str(farmer_id))
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]

    def list_all(self) -> List[DomainLoan]:
        orms = self.session.query(LoanORM).all()
        return [orm_to_domain(orm) for orm in orms]

    def update(self, loan_id: UUID, updates: dict) -> Optional[DomainLoan]:
        orm = (
            self.session.query(LoanORM)
            .filter(LoanORM.id == str(loan_id))
            .one_or_none()
        )
        if not orm:
            return None
        for key, value in updates.items():
            if hasattr(orm, key):
                setattr(orm, key, value)
        self.session.commit()
        return orm_to_domain(orm)

    def delete(self, loan_id: UUID) -> bool:
        orm = (
            self.session.query(LoanORM)
            .filter(LoanORM.id == str(loan_id))
            .one_or_none()
        )
        if not orm:
            return False
        self.session.delete(orm)
        self.session.commit()
        return True