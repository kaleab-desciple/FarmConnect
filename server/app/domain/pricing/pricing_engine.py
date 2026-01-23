from typing import List
from decimal import Decimal
from .entities import PricingRule, RuleType, FeeType
from .value_objects import PricingInput, PricingBreakdown


class PricingEngine:
    """
    Deterministic pricing engine that applies rules in priority order.
    """

    def __init__(self, rules: List[PricingRule]):
        self.rules = sorted(rules, key=lambda r: r.priority, reverse=True)

    def calculate(self, input_data: PricingInput) -> PricingBreakdown:
        """
        Calculate pricing breakdown based on input and active rules.
        """
        subtotal = input_data.unit_price * input_data.quantity

        platform_fee = Decimal(0)
        delivery_fee = Decimal(0)
        delivery_margin = Decimal(0)
        quality_fee = Decimal(0)

        # Apply rules in priority order
        for rule in self.rules:
            if not rule.matches(
                input_data.product_category,
                input_data.quality_grade,
                input_data.region,
                input_data.distance_km
            ):
                continue

            fee_amount = self._calculate_fee_amount(rule, subtotal, input_data.distance_km)

            if rule.rule_type == RuleType.PLATFORM_FEE:
                platform_fee += fee_amount
            elif rule.rule_type == RuleType.DELIVERY:
                delivery_fee += fee_amount
            elif rule.rule_type == RuleType.QUALITY:
                quality_fee += fee_amount
            elif rule.rule_type == RuleType.DISTANCE:
                # For distance, it could be fee or margin, but per task, delivery has fee and margin separate
                # Assume DISTANCE is for delivery_fee
                delivery_fee += fee_amount

        # For delivery_margin, it's the difference between quoted and actual, but for now, set to 0
        # It will be updated later in delivery reconciliation

        total_price = subtotal + platform_fee + delivery_fee + delivery_margin + quality_fee

        return PricingBreakdown(
            subtotal=subtotal,
            platform_fee=platform_fee,
            delivery_fee=delivery_fee,
            delivery_margin=delivery_margin,
            quality_fee=quality_fee,
            total_price=total_price
        )

    def _calculate_fee_amount(self, rule: PricingRule, subtotal: Decimal, distance_km: float) -> Decimal:
        """Calculate the fee amount based on rule type and fee_type."""
        if rule.fee_type == FeeType.FIXED:
            return Decimal(str(rule.fee_value))
        elif rule.fee_type == FeeType.PERCENTAGE:
            return subtotal * Decimal(str(rule.fee_value / 100))
        else:
            return Decimal(0)