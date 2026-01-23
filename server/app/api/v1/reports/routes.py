from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from app.core.database import get_db
from app.infrastructure.repositories.report_repo import ReportRepository
from app.application.reports.generate_balance_sheet import GenerateBalanceSheet, GenerateBalanceSheetRequest
from app.application.reports.generate_profit_loss import GenerateProfitLoss, GenerateProfitLossRequest
from app.application.reports.generate_cash_flow import GenerateCashFlow, GenerateCashFlowRequest
from app.domain.reports.entities import BalanceSheet, ProfitLoss, CashFlow

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
        "total_assets": float(report.total_assets),
        "total_liabilities": float(report.total_liabilities),
        "total_equity": float(report.total_equity)
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
        "total_revenue": float(report.total_revenue),
        "total_expenses": float(report.total_expenses),
        "net_profit": float(report.net_profit)
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
        "operating": {k: float(v) for k, v in report.operating.items()},
        "investing": {k: float(v) for k, v in report.investing.items()},
        "financing": {k: float(v) for k, v in report.financing.items()},
        "total_operating": float(report.total_operating),
        "total_investing": float(report.total_investing),
        "total_financing": float(report.total_financing),
        "net_cash_flow": float(report.net_cash_flow)
    }