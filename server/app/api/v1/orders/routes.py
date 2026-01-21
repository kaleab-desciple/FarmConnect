from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from shared_models import Order as OrderDTO, Escrow as EscrowDTO
from app.core.database import get_db
from .service import OrderService

router = APIRouter()

@router.post("/", response_model=dict)
def create_order(order: OrderDTO, db: Session = Depends(get_db)):
    service = OrderService(db)
    try:
        order_dto, escrow_dto = service.create_order(order)
        return {"order": order_dto, "escrow": escrow_dto}
    except Exception as e:
        db.rollback()
        raise e
