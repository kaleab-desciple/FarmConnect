"""
Order State Machine — defines valid status transitions.

Pattern: Enum-driven state machine with explicit transition map.
Invalid transitions raise InvalidStateTransitionError.
"""

from app.domain.common.enums import OrderStatus


class InvalidStateTransitionError(Exception):
    """Raised when an invalid order state transition is attempted."""
    def __init__(self, current: OrderStatus, target: OrderStatus):
        self.current = current
        self.target = target
        super().__init__(
            f"Invalid order transition: {current.value} → {target.value}"
        )


class OrderStateMachine:
    """Enum-driven valid state transitions for the order lifecycle."""

    TRANSITIONS: dict[OrderStatus, list[OrderStatus]] = {
        OrderStatus.CREATED: [
            OrderStatus.PENDING_PAYMENT,
            OrderStatus.CANCELLED,
        ],
        OrderStatus.PENDING_PAYMENT: [
            OrderStatus.FUNDED,
            OrderStatus.CANCELLED,
        ],
        OrderStatus.FUNDED: [
            OrderStatus.CONFIRMED,
            OrderStatus.CANCELLED,
        ],
        OrderStatus.CONFIRMED: [
            OrderStatus.IN_DELIVERY,
            OrderStatus.CANCELLED,
        ],
        OrderStatus.IN_DELIVERY: [
            OrderStatus.DELIVERED,
            OrderStatus.DELIVERY_FAILED,
        ],
        OrderStatus.DELIVERED: [
            OrderStatus.COMPLETED,
            OrderStatus.RETURNED,
        ],
        OrderStatus.DELIVERY_FAILED: [
            OrderStatus.IN_DELIVERY,     # retry
            OrderStatus.CANCELLED,
            OrderStatus.RETURNED,
        ],
        OrderStatus.RETURNED: [
            OrderStatus.COMPLETED,       # after refund processed
        ],
        # Terminal states — no outgoing transitions
        OrderStatus.COMPLETED: [],
        OrderStatus.CANCELLED: [],
        OrderStatus.EXPIRED: [],
    }

    @classmethod
    def validate_transition(cls, current: OrderStatus, target: OrderStatus) -> bool:
        """Check if a transition from current to target is allowed."""
        allowed = cls.TRANSITIONS.get(current, [])
        return target in allowed

    @classmethod
    def transition(cls, current: OrderStatus, target: OrderStatus) -> OrderStatus:
        """Execute a state transition, raising on invalid."""
        if not cls.validate_transition(current, target):
            raise InvalidStateTransitionError(current, target)
        return target
