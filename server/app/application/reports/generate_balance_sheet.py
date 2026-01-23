from datetime import date
from typing import Protocol, Dict, Any
from app.domain.reports.entities import BalanceSheet
from app.domain.reports.policies import FinancialReportPolicy


class ReportRepository(Protocol):
    def get_balance_sheet_data(self, as_of: date) -> Dict[str, Any]:
        ...


class GenerateBalanceSheetRequest:
    def __init__(self, as_of: date):
        self.as_of = as_of


class GenerateBalanceSheet:
    def __init__(self, report_repo: ReportRepository):
        self.report_repo = report_repo

    def execute(self, request: GenerateBalanceSheetRequest) -> BalanceSheet:
        FinancialReportPolicy.validate_as_of_date(request.as_of)

        data = self.report_repo.get_balance_sheet_data(request.as_of)

        return BalanceSheet(
            as_of=request.as_of,
            assets=data.get('assets', {}),
            liabilities=data.get('liabilities', {}),
            equity=data.get('equity', {})
        )