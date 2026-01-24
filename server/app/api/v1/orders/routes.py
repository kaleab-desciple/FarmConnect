from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal
from app.core.database import get_db
from app.core.auth import require_permission, get_current_user, TokenPayload
from app.application.services.order_service import (
    OrderApplicationService,
    OrderCreationRequest,
    OrderCreationResult
)
from app.infrastructure.repositories.order_repo import OrderRepository

router = APIRouter()


class CreateOrderRequest(BaseModel):
    """API request model for order creation."""
    farmer_id: str
    merchant_id: str
    product_id: str
    unit_price: Decimal
    quantity: int
    distance_km: float
    product_type: str = "general"


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("orders:create"))])
def create_order(request: CreateOrderRequest, db: Session = Depends(get_db)):
    """
    Create order with automatic pricing, escrow, and accounting.

    This endpoint ensures atomicity: pricing → order → escrow → accounting.
    """
    try:
        # Convert to application request
        creation_request = OrderCreationRequest(
            farmer_id=request.farmer_id,
            merchant_id=request.merchant_id,
            product_id=request.product_id,
            unit_price=request.unit_price,
            quantity=request.quantity,
            distance_km=request.distance_km,
            product_type=request.product_type
        )

        # Use atomic application service
        service = OrderApplicationService(db)
        result = service.create_order_with_pricing_and_escrow(creation_request)

        # Return result with IDs (entities were created in the transaction)
        return {
            "order_id": result.order_id,
            "escrow_id": result.escrow_id,
            "total_price": str(result.total_price),
            "message": "Order created successfully"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[dict], dependencies=[Depends(require_permission("orders:read"))])
def list_orders(
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    List orders with row-level authorization.
    - Farmers see their own orders.
    - Merchants see their own orders.
    - Agents see orders in their region.
    - Managers/Admins see all orders.
    """
    repo = OrderRepository(db)
    orders = repo.list_all(current_user=current_user)
    
    # Simple conversion to dict for response
    return [
        {
            "id": o.id,
            "farmer_id": o.farmer_id,
            "merchant_id": o.merchant_id,
            "product_id": o.product_id,
            "total_price": str(o.total_price),
            "status": o.status,
            "created_at": o.created_at.isoformat() if o.created_at else None
        }
        for o in orders
    ]


@router.get("/{order_id}", response_model=dict, dependencies=[Depends(require_permission("orders:read"))])
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    """Get a specific order by ID with row-level authorization."""
    repo = OrderRepository(db)
    order = repo.get_by_id(order_id, current_user=current_user)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or access denied"
        )
    
    return {
        "id": order.id,
        "farmer_id": order.farmer_id,
        "merchant_id": order.merchant_id,
        "product_id": order.product_id,
        "quantity": float(order.quantity),
        "unit_price": float(order.unit_price),
        "total_price": float(order.total_price),
        "status": order.status,
        "escrow_id": order.escrow_id,
        "created_at": order.created_at.isoformat() if order.created_at else None
    }
