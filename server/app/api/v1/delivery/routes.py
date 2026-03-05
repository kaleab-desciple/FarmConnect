from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.core.auth import require_permission, TokenPayload
from app.application.services.delivery_service import DeliveryService
from app.domain.common.enums import DeliveryStatus

router = APIRouter()

# --- Request / Response Models ---

class AssignDeliveryRequest(BaseModel):
    order_id: str
    carrier_id: str

class DeliveryResponse(BaseModel):
    id: str
    order_id: str
    carrier_id: str
    status: DeliveryStatus
    pickup_time: Optional[datetime] = None
    delivered_time: Optional[datetime] = None
    pickup_photo_url: Optional[str] = None
    delivery_photo_url: Optional[str] = None
    recipient_signature_url: Optional[str] = None
    notes: Optional[str] = None

class ConfirmPickupRequest(BaseModel):
    photo_url: str
    notes: Optional[str] = None

class CompleteDeliveryRequest(BaseModel):
    photo_url: Optional[str] = None
    signature_url: Optional[str] = None
    notes: Optional[str] = None


# --- Endpoints ---

@router.post("/assign", response_model=DeliveryResponse, dependencies=[Depends(require_permission("delivery:assign"))])
def assign_delivery(
    request: AssignDeliveryRequest,
    db: Session = Depends(get_db)
):
    """
    Assign an order to a delivery carrier (MANAGER / ADMIN only).
    
    Managers or administrators assign orders to specific delivery carriers
    for fulfillment. This creates a delivery record and initiates the
    delivery workflow.
    
    ## Request Body
    - **order_id**: UUID of the order to be delivered (required)
    - **carrier_id**: UUID of the carrier/courier to assign the delivery to (required)
    
    ## Authentication & Authorization
    Requires `delivery:assign` permission.
    Typically restricted to MANAGER or ADMIN roles.
    
    ## Validation
    - Order must exist and be in a state ready for delivery (e.g., CONFIRMED)
    - Carrier must exist and have a valid DELIVERY role
    - Carrier must not already have an active delivery for the same order
    
    ## Workflow
    After assignment:
    1. Delivery record is created with status PENDING
    2. Order status transitions to ASSIGNED (or similar)
    3. Carrier can view the assignment in their queue
    
    ## Responses
    - **200**: Delivery assigned successfully
    - **400**: Invalid request (order not ready, carrier invalid)
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing delivery:assign permission)
    - **404**: Order or carrier not found
    - **500**: Internal server error
    """
    service = DeliveryService(db)
    try:
        delivery = service.assign_delivery(request.order_id, request.carrier_id)
        db.commit()
        return delivery
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my-assignments", response_model=List[DeliveryResponse], dependencies=[Depends(require_permission("delivery:read"))])
def get_my_assignments(
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("delivery:read"))
):
    """
    List all deliveries assigned to the currently authenticated carrier.
    
    Retrieves all delivery assignments for the logged-in carrier, including
    both pending and in-progress deliveries. This is the primary endpoint
    for carriers to view their daily delivery queue.
    
    ## Authentication & Authorization
    Requires `delivery:read` permission.
    The carrier is identified from the JWT token (email).
    
    ## Response
    Returns array of delivery assignments with details:
    - Delivery identification (id, order_id)
    - Carrier assignment (carrier_id)
    - Current status (PENDING, PICKED_UP, IN_TRANSIT, DELIVERED, etc.)
    - Pickup and delivery timestamps
    - Photo and signature URLs (if available)
    - Notes
    
    ## Use Cases
    - Carrier's daily delivery queue
    - View pending pickups
    - Track in-progress deliveries
    - Review delivery history
    
    ## Delivery Statuses
    - **PENDING**: Assigned but not yet picked up
    - **PICKED_UP**: Carrier has collected the package
    - **IN_TRANSIT**: On the way to destination
    - **DELIVERED**: Successfully delivered
    - **FAILED**: Delivery could not be completed
    
    ## Responses
    - **200**: Deliveries retrieved successfully (may be empty array)
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing delivery:read permission)
    - **500**: Internal server error
    """
    from app.infrastructure.repositories.delivery_repo import DeliveryRepository
    from app.infrastructure.repositories.user_repo import UserRepository
    
    # Get the carrier's internal ID from the database using their email from the token
    user_repo = UserRepository(db)
    carrier = user_repo.get_by_email(current_user.email)
    if not carrier:
        return []
    
    repo = DeliveryRepository(db)
    
    # If MANAGER/ADMIN, maybe return all or deny? We'll let them see their own assignments (which is likely 0).
    # But mainly for DELIVERY role.
    deliveries = repo.get_by_carrier_id(carrier.id)
    return deliveries


@router.post("/{delivery_id}/pickup", response_model=DeliveryResponse, dependencies=[Depends(require_permission("delivery:update"))])
def confirm_pickup(
    delivery_id: str,
    request: ConfirmPickupRequest,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("delivery:update"))
):
    """
    Confirm package pickup, transitioning order to IN_DELIVERY status.
    
    When a carrier arrives at the pickup location and collects the package,
    they confirm pickup by providing photo evidence. This updates the delivery
    status and creates an audit trail.
    
    ## Path Parameters
    - **delivery_id**: UUID of the delivery record (required)
    
    ## Request Body
    - **photo_url**: URL of photo showing the picked up package (required)
    - **notes**: Optional notes about the pickup (optional)
    
    ## Authentication & Authorization
    Requires `delivery:update` permission.
    The carrier must be the one assigned to this delivery.
    
    ## Validation
    - Delivery must exist
    - Carrier must be the assigned carrier for this delivery
    - Delivery status must be PENDING or ASSIGNED
    - Photo URL must be provided
    
    ## Workflow
    Upon confirmation:
    1. Delivery status changes to PICKED_UP or IN_TRANSIT
    2. Order status transitions to IN_DELIVERY
    3. Pickup timestamp is recorded
    4. Photo is stored as evidence
    
    ## Responses
    - **200**: Pickup confirmed successfully
    - **400**: Invalid request (wrong status, not assigned to carrier)
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (not the assigned carrier)
    - **404**: Delivery not found
    - **500**: Internal server error
    """
    # Get the carrier's internal ID from the database using their email from the token
    from app.infrastructure.repositories.user_repo import UserRepository
    user_repo = UserRepository(db)
    
    # First try to find user by email (most reliable from JWT)
    carrier = user_repo.get_by_email(current_user.email)
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier user not found.")
    
    carrier_id = carrier.id
    
    service = DeliveryService(db)
    try:
        delivery = service.confirm_pickup(
            delivery_id=delivery_id,
            carrier_id=carrier_id,
            photo_url=request.photo_url,
            notes=request.notes
        )
        db.commit()
        return delivery
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{delivery_id}/complete", response_model=DeliveryResponse, dependencies=[Depends(require_permission("delivery:update"))])
def complete_delivery(
    delivery_id: str,
    request: CompleteDeliveryRequest,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("delivery:update"))
):
    """
    Confirm package delivery with signature or photo evidence.
    
    When a carrier successfully delivers the package to the recipient,
    they complete the delivery by providing proof of delivery (signature
    and/or photo). This finalizes the delivery and triggers payment release.
    
    ## Path Parameters
    - **delivery_id**: UUID of the delivery record (required)
    
    ## Request Body
    - **photo_url**: URL of photo showing delivered package (optional)
    - **signature_url**: URL of recipient's signature (optional)
    - **notes**: Optional notes about the delivery (optional)
    
    ## Authentication & Authorization
    Requires `delivery:update` permission.
    The carrier must be the one assigned to this delivery.
    
    ## Validation
    - Delivery must exist
    - Carrier must be the assigned carrier for this delivery
    - Delivery status must be PICKED_UP or IN_TRANSIT
    - At least one proof of delivery (photo or signature) is recommended
    
    ## Workflow
    Upon completion:
    1. Delivery status changes to DELIVERED
    2. Order status transitions to DELIVERED
    3. Delivered timestamp is recorded
    4. Proof of delivery is stored
    5. Payment escrow is released to farmer
    6. Order completion is finalized
    
    ## Use Cases
    - Successful package delivery
    - Customer received order
    - Partial delivery (with notes explaining)
    
    ## Responses
    - **200**: Delivery completed successfully
    - **400**: Invalid request (wrong status, not assigned to carrier)
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (not the assigned carrier)
    - **404**: Delivery not found
    - **500**: Internal server error
    """
    # Get the carrier's internal ID from the database using their email from the token
    from app.infrastructure.repositories.user_repo import UserRepository
    user_repo = UserRepository(db)
    
    # First try to find user by email (most reliable from JWT)
    carrier = user_repo.get_by_email(current_user.email)
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier user not found.")
    
    carrier_id = carrier.id
    
    service = DeliveryService(db)
    try:
        delivery = service.complete_delivery(
            delivery_id=delivery_id,
            carrier_id=carrier_id,
            photo_url=request.photo_url,
            signature_url=request.signature_url,
            notes=request.notes
        )
        db.commit()
        return delivery
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
