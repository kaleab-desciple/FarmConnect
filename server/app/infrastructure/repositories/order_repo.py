from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from shared_models import Order
from app.infrastructure.db.mappers import dto_to_orm, orm_to_domain, domain_to_dto
from app.infrastructure.db.models import OrderORM, UserORM
from app.domain.orders.entities import Order as DomainOrder
from app.core.auth import TokenPayload


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def _apply_rla_filters(self, query, current_user: TokenPayload):
        """Apply row-level authorization filters based on user role."""
        if current_user.has_realm_role("ADMIN") or current_user.has_realm_role("MANAGER") or current_user.is_service_account:
            return query

        if current_user.has_realm_role("FARMER"):
            return query.filter(OrderORM.farmer_id == current_user.user_id)

        if current_user.has_realm_role("MERCHANT"):
            return query.filter(OrderORM.merchant_id == current_user.user_id)

        if current_user.has_realm_role("AGENT"):
            # Fetch agent's region from their user metadata
            agent_orm = self.session.query(UserORM).filter(UserORM.id == current_user.user_id).one_or_none()
            if not agent_orm or not agent_orm.metadata_:
                return query.filter(False)

            agent_region = agent_orm.metadata_.get("location") # location is used for region in provisioning
            if not agent_region:
                return query.filter(False)

            # Join with User table to filter by farmer's region
            # We alias the UserORM to avoid conflicts if needed, but here we just join for the farmer
            # Assuming farmer_id points to a User record with location in metadata
            from sqlalchemy.orm import aliased
            FarmerUser = aliased(UserORM)
            return (
                query.join(FarmerUser, OrderORM.farmer_id == FarmerUser.id)
                .filter(FarmerUser.metadata_["location"].astext == agent_region)
            )

        if current_user.has_realm_role("DELIVERY"):
            # Delivery can see orders they are involved in (though not explicitly in OrderORM yet)
            # For now, let's assume they see all or restrict to a placeholder
            return query

        # Default: No access
        return query.filter(False)

    def save(self, order: DomainOrder) -> DomainOrder:
        dto = domain_to_dto(order)
        orm = dto_to_orm(dto)
        merged_orm = self.session.merge(orm)
        self.session.flush()  # to get id
        return orm_to_domain(merged_orm)

    def get_by_id(self, order_id: str, current_user: Optional[TokenPayload] = None) -> Optional[DomainOrder]:
        query = self.session.query(OrderORM).filter(OrderORM.id == order_id)
        if current_user:
            query = self._apply_rla_filters(query, current_user)
        
        orm = query.one_or_none()
        if not orm:
            return None
        return orm_to_domain(orm)

    def list_all(self, current_user: Optional[TokenPayload] = None) -> List[DomainOrder]:
        query = self.session.query(OrderORM)
        if current_user:
            query = self._apply_rla_filters(query, current_user)
            
        orms = query.all()
        return [orm_to_domain(orm) for orm in orms]

    def get_by_farmer_id(self, farmer_id: str, current_user: Optional[TokenPayload] = None) -> List[DomainOrder]:
        query = self.session.query(OrderORM).filter(OrderORM.farmer_id == farmer_id)
        if current_user:
            query = self._apply_rla_filters(query, current_user)
        
        orms = query.all()
        return [orm_to_domain(orm) for orm in orms]

    def get_by_merchant_id(self, merchant_id: str, current_user: Optional[TokenPayload] = None) -> List[DomainOrder]:
        query = self.session.query(OrderORM).filter(OrderORM.merchant_id == merchant_id)
        if current_user:
            query = self._apply_rla_filters(query, current_user)
            
        orms = query.all()
        return [orm_to_domain(orm) for orm in orms]

    def update(self, order_id: str, updates: dict, current_user: Optional[TokenPayload] = None) -> Optional[DomainOrder]:
        query = self.session.query(OrderORM).filter(OrderORM.id == order_id)
        if current_user:
            query = self._apply_rla_filters(query, current_user)
            
        orm = query.one_or_none()
        if not orm:
            return None
            
        for key, value in updates.items():
            if hasattr(orm, key):
                setattr(orm, key, value)
        self.session.commit()
        return orm_to_domain(orm)

    def delete(self, order_id: str, current_user: Optional[TokenPayload] = None) -> bool:
        query = self.session.query(OrderORM).filter(OrderORM.id == order_id)
        if current_user:
            query = self._apply_rla_filters(query, current_user)
            
        orm = query.one_or_none()
        if not orm:
            return False
            
        self.session.delete(orm)
        self.session.commit()
        return True
