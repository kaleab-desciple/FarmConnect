from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import require_permission, get_current_user, TokenPayload
from shared_models import Order as OrderDTO, OrderCreate
from shared_models.order_escrow_pair import OrderEscrowPair

from .service import OrderService


router = APIRouter()


@router.post(
    "/",
    response_model=OrderEscrowPair,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("orders:create"))],
)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """
    Create order with automatic pricing, escrow, and accounting.

    This endpoint ensures atomicity: pricing → order → escrow → accounting.
    """
    try:
        service = OrderService(db)
        order_dto, escrow_dto = service.create_order(order)
        return OrderEscrowPair(order=order_dto, escrow=escrow_dto)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[OrderDTO], dependencies=[Depends(require_permission("orders:read"))])
def list_orders(db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    """
    List orders with row-level authorization.
    - Farmers see their own orders.
    - Merchants see their own orders.
    - Agents see orders in their region.
    - Managers/Admins see all orders.
    """
    service = OrderService(db)
    return service.list_orders(current_user)

@router.get("/{order_id}", response_model=OrderDTO, dependencies=[Depends(require_permission("orders:read"))])
def get_order(order_id: str, db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    """
    Get order by ID with row-level authorization.
    """
    # Get order with proper authorization
    service = OrderService(db)
    order = service.get_order(order_id, current_user)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

