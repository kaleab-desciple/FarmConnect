from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal
from app.core.database import get_db
from app.application.services.order_service import (
    OrderApplicationService,
    OrderCreationRequest,
    OrderCreationResult
)

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


@router.post("/", response_model=dict)
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
            "message": "Order created successfully with pricing, escrow, and accounting"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
