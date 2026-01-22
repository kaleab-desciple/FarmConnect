"""
Pricing rules for the deterministic pricing engine.

All calculations use Decimal for precision and are deterministic.
"""

from decimal import Decimal, ROUND_HALF_UP


# Platform fee configuration
PLATFORM_FEE_PERCENT = Decimal('0.05')  # 5%

# Delivery cost configuration
BASE_DELIVERY_COST = Decimal('20')
COST_PER_KM = Decimal('2')
PRODUCT_MULTIPLIER = Decimal('1.0')


def calculate_base_price(unit_price: Decimal, quantity: int) -> Decimal:
    """
    Calculate base product price.

    Formula: base_price = unit_price × quantity

    Args:
        unit_price: Price per unit
        quantity: Number of units

    Returns:
        Base price as Decimal
    """
    return (unit_price * Decimal(quantity)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_platform_fee(base_price: Decimal) -> Decimal:
    """
    Calculate platform fee (revenue).

    Formula: platform_fee = base_price × PLATFORM_FEE_PERCENT

    Args:
        base_price: Base product price

    Returns:
        Platform fee as Decimal
    """
    return (base_price * PLATFORM_FEE_PERCENT).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_delivery_cost(distance_km: float, product_type: str = None) -> Decimal:
    """
    Calculate delivery cost using rule-based approach.

    Formula: delivery_cost = BASE_DELIVERY_COST
                           + (distance_km × COST_PER_KM)
                           × PRODUCT_MULTIPLIER

    Args:
        distance_km: Delivery distance in kilometers
        product_type: Type of product (reserved for future use)

    Returns:
        Delivery cost as Decimal
    """
    distance_cost = Decimal(str(distance_km)) * COST_PER_KM
    total_delivery = BASE_DELIVERY_COST + distance_cost
    final_cost = total_delivery * PRODUCT_MULTIPLIER
    return final_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_total_price(base_price: Decimal, platform_fee: Decimal, delivery_cost: Decimal) -> Decimal:
    """
    Calculate total price (escrow amount).

    Formula: total_price = base_price + platform_fee + delivery_cost

    Args:
        base_price: Base product price
        platform_fee: Platform fee
        delivery_cost: Delivery cost

    Returns:
        Total price as Decimal
    """
    return (base_price + platform_fee + delivery_cost).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)