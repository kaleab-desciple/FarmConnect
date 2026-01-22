class PaymentFailed(Exception):
    pass


class InvalidEscrowTransitionError(Exception):
    """Raised when attempting an invalid escrow state transition."""
    pass
