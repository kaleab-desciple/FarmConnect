from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from app.core.database import get_db
from app.infrastructure.repositories.report_repo import ReportRepository
from app.application.reports.generate_balance_sheet import GenerateBalanceSheet, GenerateBalanceSheetRequest, BalanceSheetDTO
from app.application.reports.generate_profit_loss import GenerateProfitLoss, GenerateProfitLossRequest, ProfitLossDTO
from app.application.reports.generate_cash_flow import GenerateCashFlow, GenerateCashFlowRequest, CashFlowDTO

# Use title-case tag to match how the router is included in the main api router
router = APIRouter(tags=["Reports"])


@router.get("/balance-sheet", response_model=dict)
def get_balance_sheet(as_of: date = Query(..., description="Balance sheet date"), db: Session = Depends(get_db)):
    report_repo = ReportRepository(db)
    use_case = GenerateBalanceSheet(report_repo)
    request = GenerateBalanceSheetRequest(as_of)
    report = use_case.execute(request)

    return {
        "as_of": report.as_of.isoformat(),
        "assets": {k: float(v) for k, v in report.assets.items()},
        "liabilities": {k: float(v) for k, v in report.liabilities.items()},
        "equity": {k: float(v) for k, v in report.equity.items()},
        "balanced": report.balanced
    }


@router.get("/profit-loss", response_model=dict)
def get_profit_loss(
    from_date: date = Query(..., description="Start date"),
    to_date: date = Query(..., description="End date"),
    db: Session = Depends(get_db)
):
    report_repo = ReportRepository(db)
    use_case = GenerateProfitLoss(report_repo)
    request = GenerateProfitLossRequest(from_date, to_date)
    report = use_case.execute(request)

    return {
        "period": {
            "from": report.from_date.isoformat(),
            "to": report.to_date.isoformat()
        },
        "revenue": {k: float(v) for k, v in report.revenue.items()},
        "expenses": {k: float(v) for k, v in report.expenses.items()},
        "net_income": float(report.net_income)
    }


@router.get("/cash-flow", response_model=dict)
def get_cash_flow(
    from_date: date = Query(..., description="Start date"),
    to_date: date = Query(..., description="End date"),
    db: Session = Depends(get_db)
):
    report_repo = ReportRepository(db)
    use_case = GenerateCashFlow(report_repo)
    request = GenerateCashFlowRequest(from_date, to_date)
    report = use_case.execute(request)

    return {
        "period": {
            "from": report.from_date.isoformat(),
            "to": report.to_date.isoformat()
        },
        "operating_activities": {k: float(v) for k, v in report.operating.items()},
        "investing_activities": {k: float(v) for k, v in report.investing.items()},
        "financing_activities": {k: float(v) for k, v in report.financing.items()},
        "net_cash_flow": float(report.net_cash_flow)
    }