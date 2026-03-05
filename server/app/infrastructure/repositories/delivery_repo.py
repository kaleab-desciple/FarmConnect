from typing import List, Optional
from sqlalchemy.orm import Session
from app.infrastructure.db.models.delivery import DeliveryORM
from app.domain.delivery.entities import Delivery as DomainDelivery

# We'll need mapper functions, so let's put them here or use a dedicated mapper file
def orm_to_domain(orm: DeliveryORM) -> DomainDelivery:
    return DomainDelivery(
        id=orm.id,
        order_id=orm.order_id,
        carrier_id=orm.carrier_id,
        status=orm.status,
        pickup_time=orm.pickup_time,
        delivered_time=orm.delivered_time,
        pickup_photo_url=orm.pickup_photo_url,
        delivery_photo_url=orm.delivery_photo_url,
        recipient_signature_url=orm.recipient_signature_url,
        notes=orm.notes,
        created_at=orm.created_at,
        updated_at=orm.updated_at
    )

def domain_to_orm(domain: DomainDelivery) -> DeliveryORM:
    return DeliveryORM(
        id=domain.id,
        order_id=domain.order_id,
        carrier_id=domain.carrier_id,
        status=domain.status,
        pickup_time=domain.pickup_time,
        delivered_time=domain.delivered_time,
        pickup_photo_url=domain.pickup_photo_url,
        delivery_photo_url=domain.delivery_photo_url,
        recipient_signature_url=domain.recipient_signature_url,
        notes=domain.notes,
        created_at=domain.created_at,
        updated_at=domain.updated_at
    )

class DeliveryRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, delivery: DomainDelivery) -> DomainDelivery:
        orm = domain_to_orm(delivery)
        merged_orm = self.session.merge(orm)
        self.session.flush()
        return orm_to_domain(merged_orm)

    def get_by_id(self, delivery_id: str) -> Optional[DomainDelivery]:
        orm = (
            self.session.query(DeliveryORM)
            .filter(DeliveryORM.id == delivery_id)
            .one_or_none()
        )
        if not orm:
            return None
        return orm_to_domain(orm)

    def get_by_order_id(self, order_id: str) -> Optional[DomainDelivery]:
        orm = (
            self.session.query(DeliveryORM)
            .filter(DeliveryORM.order_id == order_id)
            .one_or_none()
        )
        if not orm:
            return None
        return orm_to_domain(orm)

    def get_by_carrier_id(self, carrier_id: str) -> List[DomainDelivery]:
        orms = (
            self.session.query(DeliveryORM)
            .filter(DeliveryORM.carrier_id == carrier_id)
            .all()
        )
        return [orm_to_domain(orm) for orm in orms]

    def update(self, delivery_id: str, updates: dict) -> Optional[DomainDelivery]:
        orm = (
            self.session.query(DeliveryORM)
            .filter(DeliveryORM.id == delivery_id)
            .one_or_none()
        )
        if not orm:
            return None
        for key, value in updates.items():
            if hasattr(orm, key):
                setattr(orm, key, value)
        self.session.flush()
        return orm_to_domain(orm)
