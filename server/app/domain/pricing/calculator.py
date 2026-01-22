"""
Pricing calculator - the main entry point for pricing calculations.

This module provides a pure, deterministic pricing engine that calculates
delivery_cost, platform_fee, and total_price based on rule-based formulas.
"""

from decimal import Decimal
from .value_objects import PricingInput, PricingResult
from .rules import (
    calculate_base_price,
    calculate_platform_fee,
    calculate_delivery_cost,
    calculate_total_price
)
from .exceptions import PricingCalculationError


class PricingCalculator:
    """
    Pure pricing calculator that computes prices based on deterministic rules.

    No dependencies on external services, databases, or frameworks.
    """

    def calculate(self, pricing_input: PricingInput) -> PricingResult:
        """
        Calculate pricing for the given input.

        Args:
            pricing_input: Validated pricing input parameters

        Returns:
            PricingResult with all calculated amounts and breakdown

        Raises:
            PricingCalculationError: If calculation fails
        """
        try:
            # Calculate base price
            base_price = calculate_base_price(
                pricing_input.unit_price,
                pricing_input.quantity
            )

            # Calculate platform fee
            platform_fee = calculate_platform_fee(base_price)

            # Calculate delivery cost
            delivery_cost = calculate_delivery_cost(
                pricing_input.distance_km,
                pricing_input.product_type
            )

            # Calculate total price
            total_price = calculate_total_price(
                base_price,
                platform_fee,
                delivery_cost
            )

            # Create breakdown for transparency
            breakdown = {
                "unit_price": str(pricing_input.unit_price),
                "quantity": pricing_input.quantity,
                "distance_km": pricing_input.distance_km,
                "product_type": pricing_input.product_type,
                "calculations": {
                    "base_price_formula": "unit_price × quantity",
                    "platform_fee_formula": f"base_price × {0.05}",
                    "delivery_cost_formula": f"{20} + (distance_km × {2}) × {1.0}",
                    "total_price_formula": "base_price + platform_fee + delivery_cost"
                }
            }

            result = PricingResult(
                base_price=base_price,
                platform_fee=platform_fee,
                delivery_cost=delivery_cost,
                total_price=total_price,
                breakdown=breakdown
            )

            # Validate result
            if not result.is_valid:
                raise PricingCalculationError("Pricing calculation resulted in invalid totals")

            return result

        except Exception as e:
            raise PricingCalculationError(f"Pricing calculation failed: {str(e)}") from e