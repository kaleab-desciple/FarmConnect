from typing import Dict, Any
from app.infrastructure.repositories.ledger_repo import LedgerRepository
from app.domain.ledger.entities import AggregateType


class GetBalanceForUserUseCase:
    def __init__(self, ledger_repo: LedgerRepository):
        self.ledger_repo = ledger_repo

    def execute(self, user_id: str, currency: str = "ETB") -> Dict[str, Any]:
        balance = self.ledger_repo.get_balance(AggregateType.USER, user_id, currency)
        events = self.ledger_repo.list_by_aggregate(AggregateType.USER, user_id)
        return {
            "balance": balance,
            "currency": currency,
            "events": [self._event_to_dict(event) for event in events]
        }

    def _event_to_dict(self, event) -> Dict[str, Any]:
        return {
            "id": event.id,
            "event_type": event.event_type.value,
            "amount": float(event.amount),
            "direction": event.direction.value,
            "reference_type": event.reference_type.value,
            "reference_id": event.reference_id,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "metadata": event.event_metadata
        }


class GetBalanceForEscrowUseCase:
    def __init__(self, ledger_repo: LedgerRepository):
        self.ledger_repo = ledger_repo

    def execute(self, escrow_id: str, currency: str = "ETB") -> Dict[str, Any]:
        balance = self.ledger_repo.get_balance(AggregateType.ESCROW, escrow_id, currency)
        events = self.ledger_repo.list_by_aggregate(AggregateType.ESCROW, escrow_id)
        return {
            "balance": balance,
            "currency": currency,
            "events": [self._event_to_dict(event) for event in events]
        }

    def _event_to_dict(self, event) -> Dict[str, Any]:
        return {
            "id": event.id,
            "event_type": event.event_type.value,
            "amount": float(event.amount),
            "direction": event.direction.value,
            "reference_type": event.reference_type.value,
            "reference_id": event.reference_id,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "metadata": event.event_metadata
        }


class GetLedgerForReferenceUseCase:
    def __init__(self, ledger_repo: LedgerRepository):
        self.ledger_repo = ledger_repo

    def execute(self, reference_type: str, reference_id: str) -> Dict[str, Any]:
        from app.domain.ledger.entities import ReferenceType
        ref_type = ReferenceType(reference_type.upper())
        events = self.ledger_repo.list_by_reference(ref_type, reference_id)
        return {
            "reference_type": reference_type,
            "reference_id": reference_id,
            "events": [self._event_to_dict(event) for event in events]
        }

    def _event_to_dict(self, event) -> Dict[str, Any]:
        return {
            "id": event.id,
            "aggregate_type": event.aggregate_type.value,
            "aggregate_id": event.aggregate_id,
            "event_type": event.event_type.value,
            "amount": float(event.amount),
            "direction": event.direction.value,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "metadata": event.event_metadata
        }
