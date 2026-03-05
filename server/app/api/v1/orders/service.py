from __future__ import annotations
from typing import Optional
from app.core.auth.dependencies import TokenPayload
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException
from shared_models import (
    Order as OrderDTO, 
    OrderCreate, 
    OrderUpdate, 
    Escrow as EscrowDTO
)
from app.domain.orders.entities import Order as DomainOrder
from app.domain.payments.entities import Escrow as DomainEscrow, EscrowState
from app.infrastructure.repositories.user_repo import UserRepository
from app.infrastructure.repositories.order_repo import OrderRepository
from app.infrastructure.repositories.payment_repo import EscrowRepository
from app.infrastructure.repositories.pricing_repo import PricingRuleRepository
from app.domain.pricing.pricing_engine import PricingEngine
from app.domain.pricing.value_objects import PricingInput
from app.application.services.inventory_service import (
    InventoryService, 
    InsufficientStockError as InventoryInsufficientStockError,
    ProductNotFoundError as InventoryProductNotFoundError,
    ReservationFailedError as InventoryReservationFailedError
)
from app.domain.common.enums import OrderStatus
from shared_models.escrow import Provider


class OrderService:
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.order_repo = OrderRepository(session)
        self.escrow_repo = EscrowRepository(session)
        self.pricing_repo = PricingRuleRepository(session)
        self.inventory_service = InventoryService(session)

    def create_order(self, order_data: OrderCreate) -> tuple[OrderDTO, EscrowDTO]:
        # Validate required fields
        if not order_data.unit_price or order_data.unit_price <= 0:
            raise HTTPException(status_code=400, detail="Unit price must be greater than 0")
        if not order_data.quantity or order_data.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

        # Check if farmer exists
        if order_data.farmer_id:
            farmer = self.user_repo.get_by_id(order_data.farmer_id)
            if not farmer:
                raise HTTPException(status_code=404, detail="Farmer not found")

        # Check if merchant exists
        if order_data.merchant_id:
            merchant = self.user_repo.get_by_id(order_data.merchant_id)
            if not merchant:
                raise HTTPException(status_code=404, detail="Merchant not found")

        # Calculate pricing using the pricing engine
        # For now, use a default distance - in production this would come from order data
        distance_km = getattr(order_data, 'distance_km', 10.0)  # Default 10km if not provided
        product_type = getattr(order_data, 'product_type', 'general')

        pricing_input = PricingInput(
            unit_price=Decimal(str(order_data.unit_price)),
            quantity=int(order_data.quantity),
            distance_km=distance_km,
            product_type=product_type
        )

        # Get active rules from database
        active_rules = self.pricing_repo.get_active_rules()
        engine = PricingEngine(active_rules)
        
        # Calculate pricing
        pricing_result = engine.calculate(pricing_input)

        # Reserve inventory AFTER creating order (to get order_id)
        # This prevents overselling when multiple merchants order simultaneously
        # First, create a placeholder order to get the ID
        now = datetime.now(timezone.utc)
        domain_order = DomainOrder(
            farmer_id=order_data.farmer_id,
            merchant_id=order_data.merchant_id,
            product_id=order_data.product_id,
            quantity=Decimal(str(order_data.quantity)),
            unit_price=Decimal(str(order_data.unit_price)),
            subtotal=pricing_result.subtotal,
            delivery_cost=pricing_result.delivery_fee + pricing_result.delivery_margin,
            delivery_fee=pricing_result.delivery_fee if pricing_result.delivery_fee > 0 else None,
            delivery_margin=pricing_result.delivery_margin if pricing_result.delivery_margin > 0 else None,
            platform_fee=pricing_result.platform_fee,
            quality_fee=pricing_result.quality_fee if pricing_result.quality_fee > 0 else None,
            total_price=pricing_result.total_price,
            status=OrderStatus.PENDING_PAYMENT,
            created_at=now
        )

        # Save order first to get ID
        saved_order = self.order_repo.save(domain_order)
        
        # Now reserve stock with the real order_id
        try:
            self.inventory_service.reserve_stock(
                product_id=order_data.product_id,
                order_id=saved_order.id,
                qty=Decimal(str(order_data.quantity))
            )
        except InventoryProductNotFoundError:
            raise HTTPException(status_code=404, detail="Product not found")
        except InventoryInsufficientStockError as e:
            # Rollback order using repository delete method
            self.order_repo.delete(saved_order.id)
            raise HTTPException(
                status_code=409, 
                detail=f"Insufficient stock: {e.available} available, {e.requested} requested"
            )
        except InventoryReservationFailedError as e:
            # Rollback order using repository delete method
            self.order_repo.delete(saved_order.id)
            raise HTTPException(
                status_code=409,
                detail=e.reason
            )
        except Exception as e:
            # Cleanup on any error using repository delete method
            self.order_repo.delete(saved_order.id)
            raise HTTPException(status_code=500, detail=str(e))

        # Create escrow
        domain_escrow = DomainEscrow(
            order_id=saved_order.id,
            state=EscrowState.CREATED,
            amount=saved_order.total_price,
            provider=Provider.BANK,  # default
            created_at=now
        )

        # Save escrow
        saved_escrow = self.escrow_repo.save(domain_escrow)

        # Update order with escrow_id
        updated_order = self.order_repo.update(saved_order.id, {"escrow_id": saved_escrow.id})

        # Convert to DTOs
        from app.infrastructure.db.mappers import domain_to_dto
        order_dto = domain_to_dto(updated_order)
        escrow_dto = domain_to_dto(saved_escrow)

        # Commit transaction
        self.session.commit()

        return order_dto, escrow_dto

    def list_orders(self, current_user: TokenPayload) -> list[OrderDTO]:
        """
        List orders with row-level authorization.
        - Farmers see their own orders.
        - Merchants see their own orders.
        - Agents see orders in their region.
        - Managers/Admins see all orders.
        """
        # Get orders with proper authorization
        orders = self.order_repo.list_all(current_user)
        
        # Convert to DTOs
        from app.infrastructure.db.mappers import domain_to_dto
        return [domain_to_dto(order) for order in orders]

    def get_order(self, order_id: str, current_user: TokenPayload) -> Optional[OrderDTO]:
        """
        Get order with row-level authorization.
        """
        # Get order with proper authorization
        order = self.order_repo.get_by_id(order_id, current_user)
        
        if not order:
            return None
            
        # Convert to DTO
        from app.infrastructure.db.mappers import domain_to_dto
        return domain_to_dto(order)
