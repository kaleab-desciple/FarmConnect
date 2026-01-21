from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.infrastructure.db.mappers import dto_to_orm, orm_to_domain, domain_to_dto
from app.infrastructure.db.models import LedgerEventORM
from app.domain.ledger.entities import LedgerEvent, AggregateType, ReferenceType, Direction


class LedgerRepository:
    def __init__(self, session: Session):
        self.session = session

    def append(self, event: LedgerEvent) -> LedgerEvent:
        """Append-only operation - never update or delete events."""
        # dto = domain_to_dto(event)
        #orm = dto_to_orm(dto)
        orm = dto_to_orm(event)
        self.session.add(orm)
        self.session.flush()  # Get the ID
        return orm_to_domain(orm)

    def list_by_aggregate(self, aggregate_type: AggregateType, aggregate_id: str) -> List[LedgerEvent]:
        """Get all events for a specific aggregate (user, escrow, etc.)."""
        orms = (
            self.session.query(LedgerEventORM)
            .filter(
                LedgerEventORM.aggregate_type == (aggregate_type.value if hasattr(aggregate_type, 'value') else aggregate_type),
                # LedgerEventORM.aggregate_type == aggregate_type,
                LedgerEventORM.aggregate_id == aggregate_id
            )
            .order_by(LedgerEventORM.created_at)
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]

    def list_by_reference(self, reference_type: ReferenceType, reference_id: str) -> List[LedgerEvent]:
        """Get all events for a specific reference (order, escrow, dispute, loan)."""
        orms = (
            self.session.query(LedgerEventORM)
            .filter(
                LedgerEventORM.reference_type == (reference_type.value if hasattr(reference_type, 'value') else reference_type),
                LedgerEventORM.reference_id == reference_id
            )
            .order_by(LedgerEventORM.created_at)
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]

    def get_balance(self, aggregate_type: AggregateType, aggregate_id: str, currency: str = "ETB") -> float:
        """Calculate balance by summing all events for the aggregate."""
        result = (
            self.session.query(
                func.sum(
                    case(
                        (LedgerEventORM.direction == Direction.CREDIT, LedgerEventORM.amount),
                        else_=-LedgerEventORM.amount
                    )
                ).label('balance')
            )
            .filter(
                LedgerEventORM.aggregate_type == (aggregate_type.value if hasattr(aggregate_type, 'value') else aggregate_type),
                LedgerEventORM.aggregate_id == aggregate_id,
                LedgerEventORM.currency == currency
            )
            .scalar()
        )
        return float(result or 0.0)