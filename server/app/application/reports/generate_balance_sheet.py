from datetime import date
from decimal import Decimal
from typing import Protocol, Dict, Any
from app.domain.reports.policies import FinancialReportPolicy


class ReportRepository(Protocol):
    def get_balance_sheet_data(self, as_of: date) -> Dict[str, Any]:
        ...


class GenerateBalanceSheetRequest:
    def __init__(self, as_of: date):
        self.as_of = as_of


class BalanceSheetDTO:
    def __init__(self, as_of: date, assets: Dict[str, Decimal], liabilities: Dict[str, Decimal], equity: Dict[str, Decimal]):
        self.as_of = as_of
        self.assets = assets
        self.liabilities = liabilities
        self.equity = equity
        self.total_assets = sum(assets.values())
        self.total_liabilities = sum(liabilities.values())
        self.total_equity = sum(equity.values())
        self.balanced = FinancialReportPolicy.validate_balance_sheet_balance(
            self.total_assets, self.total_liabilities, self.total_equity
        )


class GenerateBalanceSheet:
    def __init__(self, report_repo: ReportRepository):
        self.report_repo = report_repo

    def execute(self, request: GenerateBalanceSheetRequest) -> BalanceSheetDTO:
        FinancialReportPolicy.validate_as_of_date(request.as_of)

        data = self.report_repo.get_balance_sheet_data(request.as_of)

        return BalanceSheetDTO(
            as_of=request.as_of,
            assets=data.get('assets', {}),
            liabilities=data.get('liabilities', {}),
            equity=data.get('equity', {})
        )