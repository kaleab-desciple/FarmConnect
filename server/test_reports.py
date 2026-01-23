import pytest
from datetime import date
from decimal import Decimal
from app.domain.reports.policies import FinancialReportPolicy
from app.domain.reports.entities import BalanceSheet, ProfitLoss, CashFlow


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


def test_balance_sheet_entity():
    """Test BalanceSheet entity creation and validation"""
    as_of = date(2026, 1, 1)
    assets = {'cash': Decimal('1000'), 'inventory': Decimal('500')}
    liabilities = {'loans': Decimal('800')}
    equity = {'capital': Decimal('700')}

    # Balanced
    bs = BalanceSheet(as_of, assets, liabilities, equity)
    assert bs.total_assets == Decimal('1500')
    assert bs.total_liabilities == Decimal('800')
    assert bs.total_equity == Decimal('700')

    # Unbalanced should raise
    with pytest.raises(ValueError):
        BalanceSheet(as_of, assets, liabilities, {'capital': Decimal('600')})


def test_profit_loss_entity():
    """Test ProfitLoss entity"""
    from_date = date(2026, 1, 1)
    to_date = date(2026, 1, 31)
    revenue = {'sales': Decimal('2000')}
    expenses = {'cost': Decimal('1200')}

    pl = ProfitLoss(from_date, to_date, revenue, expenses)
    assert pl.total_revenue == Decimal('2000')
    assert pl.total_expenses == Decimal('1200')
    assert pl.net_profit == Decimal('800')


def test_cash_flow_entity():
    """Test CashFlow entity"""
    from_date = date(2026, 1, 1)
    to_date = date(2026, 1, 31)
    operating = {'net_income': Decimal('800')}
    investing = {}
    financing = {'loans': Decimal('-200')}

    cf = CashFlow(from_date, to_date, operating, investing, financing)
    assert cf.total_operating == Decimal('800')
    assert cf.total_investing == Decimal('0')
    assert cf.total_financing == Decimal('-200')
    assert cf.net_cash_flow == Decimal('600')