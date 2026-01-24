from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_permission

router = APIRouter()

@router.post("/", dependencies=[Depends(require_permission("loans:request"))])
def request_loan(db: Session = Depends(get_db)):
    return {"message": "Loan requested"}

@router.post("/{loan_id}/approve", dependencies=[Depends(require_permission("loans:approve"))])
def approve_loan(loan_id: str, db: Session = Depends(get_db)):
    return {"message": f"Loan {loan_id} approved"}

@router.get("/", dependencies=[Depends(require_permission("loans:read"))])
def list_loans(db: Session = Depends(get_db)):
    return {"loans": []}
