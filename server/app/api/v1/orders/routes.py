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
    Create a new order with automatic pricing, escrow, and accounting.

    This endpoint orchestrates a complex atomic transaction that:
    1. Validates product availability and pricing
    2. Creates the order record
    3. Establishes escrow account to hold buyer payment
    4. Records double-entry accounting journal entries
    5. Updates product inventory
    
    All operations are atomic - if any step fails, entire transaction rolls back.
    
    ## Request Body
    - **buyer_id**: UUID of the purchasing user (required)
    - **seller_id**: UUID of the farmer/seller (required)
    - **product_id**: UUID of the product being purchased (required)
    - **quantity_kg**: Quantity in kilograms (required)
    - **delivery_address**: Delivery location (required)
    - **delivery_date**: Expected delivery date (optional)
    - **notes**: Order notes or special instructions (optional)
    
    ## Authentication & Authorization
    Requires `orders:create` permission.
    Buyers can only create orders for themselves.
    
    ## Automatic Operations
    
    **Pricing**: Unit price fetched from product listing at order creation time
    
    **Escrow**: Buyer payment held in escrow account until delivery confirmed
    
    **Accounting**: Double-entry journal entries created:
    - Debit: Buyer Cash Account
    - Credit: Escrow Holding Account
    
    ## Response Format
    Returns both order and escrow details:
    ```json
    {
      "order": {
        "id": "order_uuid",
        "buyer_id": "buyer_uuid",
        "seller_id": "seller_uuid",
        "product_id": "product_uuid",
        "quantity_kg": 50.0,
        "unit_price_usd": 2.50,
        "total_price_usd": 125.00,
        "status": "PENDING",
        "created_at": "2024-01-15T10:00:00Z"
      },
      "escrow": {
        "id": "escrow_uuid",
        "order_id": "order_uuid",
        "amount_usd": 125.00,
        "status": "HOLDING"
      }
    }
    ```
    
    ## Order Status Workflow
    - **PENDING**: Order created, payment in escrow
    - **CONFIRMED**: Seller confirmed order
    - **IN_TRANSIT**: Order shipped/in delivery
    - **DELIVERED**: Buyer received order
    - **COMPLETED**: Payment released from escrow to seller
    - **CANCELLED**: Order cancelled, funds refunded
    
    ## Validation
    - Product must exist and have sufficient stock
    - Buyer must have sufficient cash balance
    - Quantity must be positive and not exceed available stock
    - Buyer and seller must be different users
    
    ## Responses
    - **201**: Order created successfully with escrow
    - **400**: Invalid order data or insufficient stock
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing orders:create permission)
    - **404**: Product, buyer, or seller not found
    - **500**: Internal server error (transaction rolled back)
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
    
    Retrieves orders based on user role and permissions, ensuring users
    only see orders they're authorized to view.
    
    ## Authentication & Authorization
    Requires `orders:read` permission.
    
    ## Row-Level Access Control
    Results are filtered based on user role:
    
    - **Farmers**: See orders where they are the seller
    - **Merchants/Buyers**: See orders where they are the buyer
    - **Agents**: See orders in their assigned region
    - **Managers/Admins**: See all orders in the system
    
    ## Response
    Returns array of order objects with complete details:
    - Order identification (id, order_number)
    - Participants (buyer_id, seller_id)
    - Product details (product_id, quantity, pricing)
    - Status and timestamps
    - Delivery information
    
    ## Use Cases
    - Order management dashboard
    - Sales tracking (farmers)
    - Purchase history (buyers)
    - Regional monitoring (agents)
    - Platform oversight (admins)
    
    ## Responses
    - **200**: Orders retrieved successfully
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing orders:read permission)
    - **500**: Internal server error
    """
    service = OrderService(db)
    return service.list_orders(current_user)

@router.get("/{order_id}", response_model=OrderDTO, dependencies=[Depends(require_permission("orders:read"))])
def get_order(order_id: str, db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    """
    Get detailed information about a specific order.
    
    Retrieves complete order details including participants, product,
    pricing, status, and delivery information. Access is controlled
    by row-level authorization.
    
    ## Path Parameters
    - **order_id**: UUID of the order (required)
    
    ## Authentication & Authorization
    Requires `orders:read` permission.
    
    ## Row-Level Access Control
    User can only access order if they are:
    - The buyer (purchased the order)
    - The seller (fulfilling the order)
    - An agent for the region
    - A manager/admin
    
    ## Response Fields
    - **id**: Order UUID
    - **buyer_id**: Buyer's user UUID
    - **seller_id**: Seller's user UUID
    - **product_id**: Product UUID
    - **quantity_kg**: Order quantity
    - **unit_price_usd**: Price per kg at order time
    - **total_price_usd**: Total order value
    - **status**: Current order status
    - **delivery_address**: Delivery location
    - **delivery_date**: Expected/actual delivery date
    - **created_at**: Order creation timestamp
    - **updated_at**: Last update timestamp
    - **notes**: Order notes or instructions
    
    ## Use Cases
    - Order detail page
    - Order tracking
    - Delivery management
    - Escrow release verification
    - Dispute resolution
    
    ## Responses
    - **200**: Order details retrieved successfully
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (not authorized to view this order)
    - **404**: Order not found
    - **500**: Internal server error
    """
    # Get order with proper authorization
    service = OrderService(db)
    order = service.get_order(order_id, current_user)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

