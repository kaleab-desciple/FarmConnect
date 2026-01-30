
import sys
import os
import traceback
from decimal import Decimal
from datetime import datetime
from uuid import uuid4

# Add server directory to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.application.services.order_service import OrderApplicationService, OrderCreationRequest
from app.infrastructure.db.models import UserORM
from app.domain.common.enums import UserRole

def reproduce():
    db = SessionLocal()
    try:
        # 1. Ensure Farmer and Merchant exist
        farmer_id = "FAR-00001"
        merchant_id = "MER-00001"
        
        farmer = db.query(UserORM).filter_by(id=farmer_id).first()
        if not farmer:
            print(f"Creating mock farmer {farmer_id}")
            farmer = UserORM(id=farmer_id, name="Test Farmer", role=UserRole.FARMER, email="f@test.com")
            db.add(farmer)
            
        merchant = db.query(UserORM).filter_by(id=merchant_id).first()
        if not merchant:
            print(f"Creating mock merchant {merchant_id}")
            merchant = UserORM(id=merchant_id, name="Test Merchant", role=UserRole.MERCHANT, email="m@test.com")
            db.add(merchant)
        
        db.commit()
        
        # 2. Create OrderCreationRequest
        request = OrderCreationRequest(
            farmer_id=farmer_id,
            merchant_id=merchant_id,
            product_id=str(uuid4()), # Random product
            quantity=1,
            unit_price=Decimal(1.0),
            distance_km=10.0,
            product_type="general"
        )
        
        print("Attempting to create order...")
        service = OrderApplicationService(db)
        
        # OrderApplicationService.create_order_with_pricing_and_escrow
        result = service.create_order_with_pricing_and_escrow(request)
        print("Order created successfully!")
        print(f"Order ID: {result.order_id}, Escrow ID: {result.escrow_id}, Total: {result.total_price}")

    except Exception:
        print("Caught exception during order creation:")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    reproduce()
