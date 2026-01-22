"""
Unit tests for the pricing engine.

Tests cover:
- Normal pricing calculations
- Edge cases (zero distance, large quantities)
- Deterministic output
- Rounding correctness
- Input validation
"""

import pytest
from decimal import Decimal
from app.domain.pricing.calculator import PricingCalculator
from app.domain.pricing.value_objects import PricingInput
from app.domain.pricing.exceptions import InvalidPricingInputError


class TestPricingCalculator:
    """Test the main pricing calculator."""

    def test_normal_pricing_calculation(self):
        """Test normal pricing with typical values."""
        calculator = PricingCalculator()

        pricing_input = PricingInput(
            unit_price=Decimal('10.00'),
            quantity=2,
            distance_km=5.0,
            product_type='vegetables'
        )

        result = calculator.calculate(pricing_input)

        # Expected calculations:
        # base_price = 10.00 * 2 = 20.00
        # platform_fee = 20.00 * 0.05 = 1.00
        # delivery_cost = 20 + (5.0 * 2) * 1.0 = 30.00
        # total_price = 20.00 + 1.00 + 30.00 = 51.00

        assert result.base_price == Decimal('20.00')
        assert result.platform_fee == Decimal('1.00')
        assert result.delivery_cost == Decimal('30.00')
        assert result.total_price == Decimal('51.00')
        assert result.is_valid == True

    def test_zero_distance_pricing(self):
        """Test pricing with zero distance."""
        calculator = PricingCalculator()

        pricing_input = PricingInput(
            unit_price=Decimal('15.50'),
            quantity=1,
            distance_km=0.0,
            product_type='dairy'
        )

        result = calculator.calculate(pricing_input)

        # Expected calculations:
        # base_price = 15.50 * 1 = 15.50
        # platform_fee = 15.50 * 0.05 = 0.78
        # delivery_cost = 20 + (0.0 * 2) * 1.0 = 20.00
        # total_price = 15.50 + 0.78 + 20.00 = 36.28

        assert result.base_price == Decimal('15.50')
        assert result.platform_fee == Decimal('0.78')
        assert result.delivery_cost == Decimal('20.00')
        assert result.total_price == Decimal('36.28')
        assert result.is_valid == True

    def test_large_quantity_pricing(self):
        """Test pricing with large quantity."""
        calculator = PricingCalculator()

        pricing_input = PricingInput(
            unit_price=Decimal('5.99'),
            quantity=100,
            distance_km=25.5,
            product_type='grains'
        )

        result = calculator.calculate(pricing_input)

        # Expected calculations:
        # base_price = 5.99 * 100 = 599.00
        # platform_fee = 599.00 * 0.05 = 29.95
        # delivery_cost = 20 + (25.5 * 2) * 1.0 = 71.00
        # total_price = 599.00 + 29.95 + 71.00 = 699.95

        assert result.base_price == Decimal('599.00')
        assert result.platform_fee == Decimal('29.95')
        assert result.delivery_cost == Decimal('71.00')
        assert result.total_price == Decimal('699.95')
        assert result.is_valid == True

    def test_deterministic_output(self):
        """Test that same inputs produce same outputs."""
        calculator = PricingCalculator()

        pricing_input = PricingInput(
            unit_price=Decimal('12.34'),
            quantity=3,
            distance_km=7.5,
            product_type='fruits'
        )

        result1 = calculator.calculate(pricing_input)
        result2 = calculator.calculate(pricing_input)

        assert result1.base_price == result2.base_price
        assert result1.platform_fee == result2.platform_fee
        assert result1.delivery_cost == result2.delivery_cost
        assert result1.total_price == result2.total_price
        assert result1.breakdown == result2.breakdown

    def test_rounding_correctness(self):
        """Test that rounding is handled correctly."""
        calculator = PricingCalculator()

        pricing_input = PricingInput(
            unit_price=Decimal('7.777'),
            quantity=1,
            distance_km=1.0,
            product_type='test'
        )

        result = calculator.calculate(pricing_input)

        # All results should be rounded to 2 decimal places
        assert result.base_price == Decimal('7.78')  # 7.777 rounded up
        assert result.platform_fee == Decimal('0.39')  # 7.78 * 0.05
        assert result.delivery_cost == Decimal('22.00')  # 20 + (1.0 * 2) = 22.00
        assert result.total_price == Decimal('30.17')  # 7.78 + 0.39 + 22.00

    def test_breakdown_contains_calculation_details(self):
        """Test that breakdown contains calculation formulas and inputs."""
        calculator = PricingCalculator()

        pricing_input = PricingInput(
            unit_price=Decimal('8.00'),
            quantity=2,
            distance_km=3.0,
            product_type='test'
        )

        result = calculator.calculate(pricing_input)

        assert 'unit_price' in result.breakdown
        assert 'quantity' in result.breakdown
        assert 'distance_km' in result.breakdown
        assert 'product_type' in result.breakdown
        assert 'calculations' in result.breakdown
        assert 'base_price_formula' in result.breakdown['calculations']
        assert 'platform_fee_formula' in result.breakdown['calculations']
        assert 'delivery_cost_formula' in result.breakdown['calculations']
        assert 'total_price_formula' in result.breakdown['calculations']


class TestPricingInputValidation:
    """Test input validation for PricingInput."""

    def test_negative_unit_price_raises_error(self):
        """Test that negative unit price raises error."""
        with pytest.raises(ValueError, match="Unit price cannot be negative"):
            PricingInput(
                unit_price=Decimal('-1.00'),
                quantity=1,
                distance_km=1.0,
                product_type='test'
            )

    def test_zero_quantity_raises_error(self):
        """Test that zero quantity raises error."""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            PricingInput(
                unit_price=Decimal('10.00'),
                quantity=0,
                distance_km=1.0,
                product_type='test'
            )

    def test_negative_distance_raises_error(self):
        """Test that negative distance raises error."""
        with pytest.raises(ValueError, match="Distance cannot be negative"):
            PricingInput(
                unit_price=Decimal('10.00'),
                quantity=1,
                distance_km=-1.0,
                product_type='test'
            )

    def test_empty_product_type_raises_error(self):
        """Test that empty product type raises error."""
        with pytest.raises(ValueError, match="Product type cannot be empty"):
            PricingInput(
                unit_price=Decimal('10.00'),
                quantity=1,
                distance_km=1.0,
                product_type=''
            )