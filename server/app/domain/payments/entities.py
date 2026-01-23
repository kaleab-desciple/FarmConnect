from typing import Optional
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime, timezone
from app.domain.common.enums import EscrowState, Provider


class EscrowStateTransitionError(Exception):
    pass


@dataclass
class Escrow:
    id: Optional[str] = None
    order_id: Optional[str] = None
    state: Optional[EscrowState] = None
    amount: Optional[Decimal] = None
    penalty_applied: Optional[bool] = False
    provider: Optional[Provider] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    funded_at: Optional[datetime] = None
    released_at: Optional[datetime] = None
    provider_reference: Optional[str] = None

    def mark_funded(self, reference: str) -> None:
        if self.state != EscrowState.CREATED:
            raise EscrowStateTransitionError(f"Cannot fund escrow in state {self.state}")
        self.state = EscrowState.FUNDED
        self.funded_at = datetime.now(timezone.utc)
        self.provider_reference = reference

    def release(self, reference: str) -> None:
        if self.state != EscrowState.FUNDED:
            raise EscrowStateTransitionError(f"Cannot release escrow in state {self.state}")
        self.state = EscrowState.RELEASED
        self.released_at = datetime.now(timezone.utc)
        self.provider_reference = reference

    def mark_disputed(self) -> None:
        if self.state != EscrowState.FUNDED:
            raise EscrowStateTransitionError(f"Cannot dispute escrow in state {self.state}")
        self.state = EscrowState.DISPUTED

    def resolve_release(self, reference: str) -> None:
        if self.state != EscrowState.DISPUTED:
            raise EscrowStateTransitionError(f"Cannot resolve release escrow in state {self.state}")
        self.state = EscrowState.RELEASED
        self.released_at = datetime.now(timezone.utc)
        self.provider_reference = reference

    def resolve_partial_release(self, penalty: Decimal, reference: str) -> None:
        if self.state != EscrowState.DISPUTED:
            raise EscrowStateTransitionError(f"Cannot resolve partial release escrow in state {self.state}")
        self.state = EscrowState.RELEASED
        self.released_at = datetime.now(timezone.utc)
        self.provider_reference = reference
        self.penalty_applied = penalty

    def resolve_refund(self, reference: str) -> None:
        if self.state != EscrowState.DISPUTED:
            raise EscrowStateTransitionError(f"Cannot refund escrow in state {self.state}")
        self.state = EscrowState.REFUNDED
        self.provider_reference = reference
