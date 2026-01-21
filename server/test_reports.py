import pytest
from datetime import date
from decimal import Decimal
from app.domain.reports.policies import FinancialReportPolicy


def test_balance_sheet_balance_validation():
    """Test that balance sheet balance validation works"""
    assets = Decimal('1000')
    liabilities = Decimal('600')
    equity = Decimal('400')

    assert FinancialReportPolicy.validate_balance_sheet_balance(assets, liabilities, equity) == True

    # Unbalanced
    equity_unbalanced = Decimal('300')
    assert FinancialReportPolicy.validate_balance_sheet_balance(assets, liabilities, equity_unbalanced) == False


def test_date_range_validation():
    """Test date range validation"""
    from_date = date(2026, 1, 1)
    to_date = date(2026, 1, 31)

    # Should not raise
    FinancialReportPolicy.validate_date_range(from_date, to_date)

    # Invalid range
    with pytest.raises(ValueError, match="From date cannot be after to date"):
        FinancialReportPolicy.validate_date_range(to_date, from_date)


def test_net_income_calculation():
    """Test net income calculation"""
    revenue = Decimal('1000')
    expenses = Decimal('600')
    expected_net = Decimal('400')

    assert FinancialReportPolicy.calculate_net_income(revenue, expenses) == expected_net


def test_future_date_validation():
    """Test that future dates are rejected"""
    future_date = date(2030, 1, 1)

    with pytest.raises(ValueError, match="cannot be in the future"):
        FinancialReportPolicy.validate_as_of_date(future_date)