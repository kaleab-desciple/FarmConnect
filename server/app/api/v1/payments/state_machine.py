from app.domain.payments.entities import EscrowState

class InvalidEscrowTransition(Exception):
    pass

ALLOWED = {
    EscrowState.CREATED: {EscrowState.FUNDED},
    EscrowState.FUNDED: {EscrowState.SETTLED, EscrowState.REVERSED},
    EscrowState.SETTLED: set(),
    EscrowState.REVERSED: set(),
}

def transition(current: EscrowState, target: EscrowState):
    if target not in ALLOWED[current]:
        raise InvalidEscrowTransition(f"{current} → {target}")
    return target


class PaymentStateMachine:
    pass
