from datetime import date
from decimal import Decimal
from typing import Dict
from dataclasses import dataclass
from .policies import FinancialReportPolicy


@dataclass(frozen=True)
class BalanceSheet:
    as_of: date
    assets: Dict[str, Decimal]
    liabilities: Dict[str, Decimal]
    equity: Dict[str, Decimal]

    def __post_init__(self):
        total_assets = sum(self.assets.values())
        total_liabilities = sum(self.liabilities.values())
        total_equity = sum(self.equity.values())
        if not FinancialReportPolicy.validate_balance_sheet_balance(total_assets, total_liabilities, total_equity):
            raise ValueError("Balance sheet does not balance")

    @property
    def total_assets(self) -> Decimal:
        return sum(self.assets.values())

    @property
    def total_liabilities(self) -> Decimal:
        return sum(self.liabilities.values())

    @property
    def total_equity(self) -> Decimal:
        return sum(self.equity.values())


@dataclass(frozen=True)
class ProfitLoss:
    from_date: date
    to_date: date
    revenue: Dict[str, Decimal]
    expenses: Dict[str, Decimal]

    def __post_init__(self):
        FinancialReportPolicy.validate_date_range(self.from_date, self.to_date)

    @property
    def total_revenue(self) -> Decimal:
        return sum(self.revenue.values())

    @property
    def total_expenses(self) -> Decimal:
        return sum(self.expenses.values())

    @property
    def net_profit(self) -> Decimal:
        return FinancialReportPolicy.calculate_net_income(self.total_revenue, self.total_expenses)


@dataclass(frozen=True)
class CashFlow:
    from_date: date
    to_date: date
    operating: Dict[str, Decimal]
    investing: Dict[str, Decimal]
    financing: Dict[str, Decimal]

    def __post_init__(self):
        FinancialReportPolicy.validate_date_range(self.from_date, self.to_date)

    @property
    def total_operating(self) -> Decimal:
        return sum(self.operating.values())

    @property
    def total_investing(self) -> Decimal:
        return sum(self.investing.values())

    @property
    def total_financing(self) -> Decimal:
        return sum(self.financing.values())

    @property
    def net_cash_flow(self) -> Decimal:
        return self.total_operating + self.total_investing + self.total_financing