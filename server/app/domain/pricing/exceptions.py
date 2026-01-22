class PricingError(Exception):
    """Base exception for pricing-related errors."""
    pass


class InvalidPricingInputError(PricingError):
    """Raised when pricing input parameters are invalid."""
    pass


class PricingCalculationError(PricingError):
    """Raised when pricing calculation fails."""
    pass