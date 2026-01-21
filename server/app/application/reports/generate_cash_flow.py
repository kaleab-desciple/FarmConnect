from datetime import date
from decimal import Decimal
from typing import Protocol, Dict, Any
from app.domain.reports.policies import FinancialReportPolicy


class ReportRepository(Protocol):
    def get_cash_flow_data(self, from_date: date, to_date: date) -> Dict[str, Any]:
        ...


class GenerateCashFlowRequest:
    def __init__(self, from_date: date, to_date: date):
        self.from_date = from_date
        self.to_date = to_date


class CashFlowDTO:
    def __init__(self, from_date: date, to_date: date, operating: Dict[str, Decimal],
                 investing: Dict[str, Decimal], financing: Dict[str, Decimal]):
        self.from_date = from_date
        self.to_date = to_date
        self.operating = operating
        self.investing = investing
        self.financing = financing
        self.net_cash_flow = (sum(operating.values()) + sum(investing.values()) + sum(financing.values()))


class GenerateCashFlow:
    def __init__(self, report_repo: ReportRepository):
        self.report_repo = report_repo

    def execute(self, request: GenerateCashFlowRequest) -> CashFlowDTO:
        FinancialReportPolicy.validate_date_range(request.from_date, request.to_date)

        data = self.report_repo.get_cash_flow_data(request.from_date, request.to_date)

        return CashFlowDTO(
            from_date=request.from_date,
            to_date=request.to_date,
            operating=data.get('operating', {}),
            investing=data.get('investing', {}),
            financing=data.get('financing', {})
        )