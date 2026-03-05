from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from app.domain.common.enums import DeliveryStatus

@dataclass
class Delivery:
    id: Optional[str] = None
    order_id: Optional[str] = None
    carrier_id: Optional[str] = None
    status: Optional[DeliveryStatus] = None
    pickup_time: Optional[datetime] = None
    delivered_time: Optional[datetime] = None
    pickup_photo_url: Optional[str] = None
    delivery_photo_url: Optional[str] = None
    recipient_signature_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def confirm_pickup(self, photo_url: str, notes: Optional[str] = None) -> None:
        """Confirm the delivery has been picked up by the carrier."""
        if self.status != DeliveryStatus.ASSIGNED:
            raise ValueError(f"Pickup invalid. Current delivery status: {self.status.value}")
        self.status = DeliveryStatus.PICKED_UP
        self.pickup_photo_url = photo_url
        self.pickup_time = datetime.now(timezone.utc)
        if notes:
            self.notes = f"{self.notes or ''}\nPickup notes: {notes}".strip()

    def confirm_delivery(self, photo_url: Optional[str] = None, signature_url: Optional[str] = None, notes: Optional[str] = None) -> None:
        """Finalize the delivery."""
        if self.status not in (DeliveryStatus.PICKED_UP, DeliveryStatus.IN_TRANSIT):
            raise ValueError(f"Completion invalid. Current delivery status: {self.status.value}")
        if not photo_url and not signature_url:
            raise ValueError("Proof of delivery (photo or signature) is required.")

        self.status = DeliveryStatus.DELIVERED
        self.delivery_photo_url = photo_url
        self.recipient_signature_url = signature_url
        self.delivered_time = datetime.now(timezone.utc)
        if notes:
            self.notes = f"{self.notes or ''}\nDelivery notes: {notes}".strip()
