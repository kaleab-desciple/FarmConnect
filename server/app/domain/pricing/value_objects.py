from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any


@dataclass(frozen=True)
class PricingInput:
    """Input parameters for pricing calculation."""
    unit_price: Decimal
    quantity: int
    distance_km: float
    product_type: str

    def __post_init__(self):
        """Validate input parameters."""
        if self.unit_price < 0:
            raise ValueError("Unit price cannot be negative")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.distance_km < 0:
            raise ValueError("Distance cannot be negative")
        if not self.product_type:
            raise ValueError("Product type cannot be empty")


@dataclass(frozen=True)
class PricingBreakdown:
    """Detailed breakdown of pricing calculation."""
    subtotal: Decimal
    platform_fee: Decimal
    delivery_fee: Decimal
    delivery_margin: Decimal
    quality_fee: Decimal
    total_price: Decimal

    @property
    def is_valid(self) -> bool:
        """Check if the pricing breakdown is mathematically correct."""
        expected_total = self.subtotal + self.platform_fee + self.delivery_fee + self.delivery_margin + self.quality_fee
        return abs(self.total_price - expected_total) < Decimal('0.01')


@dataclass(frozen=True)
class PricingResult:
    """Result of pricing calculation."""
    base_price: Decimal
    platform_fee: Decimal
    delivery_cost: Decimal
    total_price: Decimal
    breakdown: Dict[str, Any]

    @property
    def is_valid(self) -> bool:
        """Check if the pricing result is mathematically correct."""
        expected_total = self.base_price + self.platform_fee + self.delivery_cost
        return abs(self.total_price - expected_total) < Decimal('0.01')