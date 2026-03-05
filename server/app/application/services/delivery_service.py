from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.infrastructure.repositories.delivery_repo import DeliveryRepository
from app.infrastructure.repositories.order_repo import OrderRepository
from app.infrastructure.repositories.user_repo import UserRepository
from app.domain.orders.state_machine import OrderStateMachine
from app.domain.common.enums import DeliveryStatus, OrderStatus
from app.domain.delivery.entities import Delivery
from fastapi import HTTPException

class DeliveryService:
    def __init__(self, session: Session):
        self.session = session
        self.delivery_repo = DeliveryRepository(session)
        self.order_repo = OrderRepository(session)
        self.user_repo = UserRepository(session)

    def _resolve_carrier_id(self, carrier_id: str) -> str:
        """
        Resolve carrier ID to internal user ID.
        
        If carrier_id is a Keycloak UUID, look up the user and return their internal ID.
        Otherwise, return the carrier_id as-is.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.warning(f"DEBUG _resolve_carrier_id: input carrier_id = '{carrier_id}'")
        
        # Check if this looks like a Keycloak UUID (has dashes and is 36 chars)
        if carrier_id and len(carrier_id) == 36 and '-' in carrier_id:
            logger.warning(f"DEBUG: Looks like Keycloak UUID, searching for user with keycloak_id = '{carrier_id}'")
            user = self.user_repo.get_by_keycloak_id(carrier_id)
            logger.warning(f"DEBUG: User lookup result = {user}")
            if user:
                logger.warning(f"DEBUG: Found user, returning internal id = '{user.id}'")
                return user.id
        # Return as-is (carrier_id should be provided in the request body)
        logger.warning(f"DEBUG: Returning carrier_id as-is = '{carrier_id}'")
        return carrier_id

    def assign_delivery(self, order_id: str, carrier_id: str) -> Delivery:
        """Assign an order to a delivery carrier."""
        # Validate Carrier
        carrier = self.user_repo.get_by_id(carrier_id)
        if not carrier:
            raise HTTPException(status_code=404, detail="Carrier not found.")
        from app.domain.common.enums import UserRole
        if carrier.role != UserRole.DELIVERY:
            raise HTTPException(status_code=400, detail="Assigned user must have the DELIVERY role.")

        # Validate Order
        # Depending on how the repository is structured, it might need a TokenPayload
        # but internal services often bypass user scope checks or use a generic one.
        # Assuming an unscoped get_by_id or using the repo directly.
        from app.infrastructure.db.models.order import OrderORM
        from app.infrastructure.db.mappers import orm_to_domain as order_orm_to_domain
        
        order_orm = self.session.query(OrderORM).filter(OrderORM.id == order_id).one_or_none()
        if not order_orm:
            raise HTTPException(status_code=404, detail="Order not found.")

        # Order must be in a state ready for delivery, e.g., CONFIRMED
        if order_orm.status != OrderStatus.CONFIRMED:
            raise HTTPException(
                status_code=400, 
                detail=f"Order must be CONFIRMED to assign delivery. Current state: {order_orm.status.value}"
            )

        # Ensure not already assigned
        existing_delivery = self.delivery_repo.get_by_order_id(order_id)
        if existing_delivery and existing_delivery.status not in (DeliveryStatus.CANCELLED, DeliveryStatus.FAILED):
            raise HTTPException(status_code=400, detail="Order is already assigned to a delivery.")

        # Create Delivery record
        delivery = Delivery(
            order_id=order_id,
            carrier_id=carrier_id,
            status=DeliveryStatus.ASSIGNED,
            created_at=datetime.now(timezone.utc)
        )
        saved_delivery = self.delivery_repo.save(delivery)
        
        # We DO NOT move the order to IN_DELIVERY yet. 
        # IN_DELIVERY happens when the item is physically picked up.
        return saved_delivery

    def confirm_pickup(self, delivery_id: str, carrier_id: str, photo_url: str, notes: Optional[str] = None) -> Delivery:
        """Carrier confirms they have picked up the order."""
        delivery = self.delivery_repo.get_by_id(delivery_id)
        if not delivery:
            raise HTTPException(status_code=404, detail="Delivery not found.")
        
        # Resolve carrier_id: if it's a Keycloak UUID, resolve to internal user ID
        resolved_carrier_id = self._resolve_carrier_id(carrier_id)
        
        if delivery.carrier_id != resolved_carrier_id:
            raise HTTPException(status_code=403, detail="Unauthorized carrier.")

        try:
            delivery.confirm_pickup(photo_url=photo_url, notes=notes)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Save Delivery state
        saved_delivery = self.delivery_repo.update(delivery_id, {
            "status": delivery.status,
            "pickup_photo_url": delivery.pickup_photo_url,
            "pickup_time": delivery.pickup_time,
            "notes": delivery.notes
        })

        # Update Order State to IN_DELIVERY
        from app.infrastructure.db.models.order import OrderORM
        order_orm = self.session.query(OrderORM).filter(OrderORM.id == delivery.order_id).one()
        OrderStateMachine.transition(order_orm.status, OrderStatus.IN_DELIVERY)
        order_orm.status = OrderStatus.IN_DELIVERY
        self.session.flush()

        return saved_delivery

    def complete_delivery(self, delivery_id: str, carrier_id: str, photo_url: Optional[str] = None, signature_url: Optional[str] = None, notes: Optional[str] = None) -> Delivery:
        """Carrier confirms they have dropped off the order to the merchant."""
        delivery = self.delivery_repo.get_by_id(delivery_id)
        if not delivery:
            raise HTTPException(status_code=404, detail="Delivery not found.")
        
        # Resolve carrier_id: if it's a Keycloak UUID, resolve to internal user ID
        resolved_carrier_id = self._resolve_carrier_id(carrier_id)
        
        if delivery.carrier_id != resolved_carrier_id:
            raise HTTPException(status_code=403, detail="Unauthorized carrier.")

        try:
            delivery.confirm_delivery(photo_url=photo_url, signature_url=signature_url, notes=notes)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Save Delivery state
        saved_delivery = self.delivery_repo.update(delivery_id, {
            "status": delivery.status,
            "delivery_photo_url": delivery.delivery_photo_url,
            "recipient_signature_url": delivery.recipient_signature_url,
            "delivered_time": delivery.delivered_time,
            "notes": delivery.notes
        })

        # Update Order State to DELIVERED
        from app.infrastructure.db.models.order import OrderORM
        order_orm = self.session.query(OrderORM).filter(OrderORM.id == delivery.order_id).one()
        OrderStateMachine.transition(order_orm.status, OrderStatus.DELIVERED)
        order_orm.status = OrderStatus.DELIVERED
        order_orm.delivered_at = datetime.now(timezone.utc)
        self.session.flush()

        # NOTE: Escrow release is handled separately by the Escrow Service when the order completes.
        return saved_delivery
