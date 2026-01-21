from datetime import date
from decimal import Decimal
from typing import Protocol, Dict, Any
from app.domain.reports.policies import FinancialReportPolicy


class ReportRepository(Protocol):
    def get_profit_loss_data(self, from_date: date, to_date: date) -> Dict[str, Any]:
        ...


class GenerateProfitLossRequest:
    def __init__(self, from_date: date, to_date: date):
        self.from_date = from_date
        self.to_date = to_date


class ProfitLossDTO:
    def __init__(self, from_date: date, to_date: date, revenue: Dict[str, Decimal], expenses: Dict[str, Decimal]):
        self.from_date = from_date
        self.to_date = to_date
        self.revenue = revenue
        self.expenses = expenses
        self.total_revenue = sum(revenue.values())
        self.total_expenses = sum(expenses.values())
        self.net_income = FinancialReportPolicy.calculate_net_income(self.total_revenue, self.total_expenses)


class GenerateProfitLoss:
    def __init__(self, report_repo: ReportRepository):
        self.report_repo = report_repo

    def execute(self, request: GenerateProfitLossRequest) -> ProfitLossDTO:
        FinancialReportPolicy.validate_date_range(request.from_date, request.to_date)

        data = self.report_repo.get_profit_loss_data(request.from_date, request.to_date)

        return ProfitLossDTO(
            from_date=request.from_date,
            to_date=request.to_date,
            revenue=data.get('revenue', {}),
            expenses=data.get('expenses', {})
        )