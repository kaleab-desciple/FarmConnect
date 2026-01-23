from datetime import date
from typing import Protocol, Dict, Any
from app.domain.reports.entities import CashFlow
from app.domain.reports.policies import FinancialReportPolicy


class ReportRepository(Protocol):
    def get_cash_flow_data(self, from_date: date, to_date: date) -> Dict[str, Any]:
        ...


class GenerateCashFlowRequest:
    def __init__(self, from_date: date, to_date: date):
        self.from_date = from_date
        self.to_date = to_date


class GenerateCashFlow:
    def __init__(self, report_repo: ReportRepository):
        self.report_repo = report_repo

    def execute(self, request: GenerateCashFlowRequest) -> CashFlow:
        FinancialReportPolicy.validate_date_range(request.from_date, request.to_date)

        data = self.report_repo.get_cash_flow_data(request.from_date, request.to_date)

        return CashFlow(
            from_date=request.from_date,
            to_date=request.to_date,
            operating=data.get('operating', {}),
            investing=data.get('investing', {}),
            financing=data.get('financing', {})
        )