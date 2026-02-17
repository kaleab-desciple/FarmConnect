"""Verification script for Harvest-to-Product workflow."""
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy.dialects.postgresql as psql
from sqlalchemy import JSON

# Mock JSONB and ARRAY for SQLite verification
psql.JSONB = JSON
psql.ARRAY = lambda x: JSON
import sqlalchemy
sqlalchemy.ARRAY = JSON

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.user import UserORM
from app.infrastructure.db.models.farm import FarmORM, FieldORM, CropCycleORM
from app.infrastructure.db.models.harvest import HarvestORM
from app.infrastructure.db.models.product import ProductORM
from app.domain.farm.entities import HarvestCreate
from app.domain.common.enums import CropCycleStatus, Unit, QualityGrade
from app.application.harvest.service import HarvestService

# Use in-memory SQLite for verification
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=engine)

def verify():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Setup Mock User
        farmer_id = str(uuid.uuid4())
        farmer = UserORM(id=farmer_id, name="Farmer Test", email="farmer@test.com")
        db.add(farmer)
        
        # 2. Setup Mock Farm and Field
        farm_id = str(uuid.uuid4())
        farm = FarmORM(id=farm_id, farmer_id=farmer_id, name="Test Farm", location_lat=0, location_lng=0)
        db.add(farm)
        
        field_id = str(uuid.uuid4())
        field = FieldORM(id=field_id, farm_id=farm_id, name="Paddy Field", area_ha=10.0, boundary_geojson={})
        db.add(field)
        
        # 3. Setup Crop Cycle
        cycle_id = str(uuid.uuid4())
        cycle = CropCycleORM(
            id=cycle_id, 
            field_id=field_id, 
            product_category="GRAINS", 
            crop_name="Rice", 
            planting_date=date(2026, 1, 1),
            expected_yield_kg=1000.0,
            status='PLANTED'
        )
        db.add(cycle)
        db.commit()
        
        print(f"Setup complete. Cycle Status: {cycle.status}")
        
        # 4. Record Harvest
        class MockUser:
            id = farmer_id
            role = "FARMER"
            
        service = HarvestService(db)
        harvest_data = HarvestCreate(
            farmer_id=farmer_id,
            crop_cycle_id=uuid.UUID(cycle_id),
            field_id=uuid.UUID(field_id),
            harvest_date=date(2026, 2, 17),
            quantity_harvested=Decimal("1200.0"),
            unit="KG",
            quality_grade="GRADE_A"
        )
        
        harvest = service.record_harvest(harvest_data, MockUser())
        print(f"Harvest recorded: ID={harvest.id}, Qty={harvest.quantity_harvested}")
        
        # Check cycle status update
        db.refresh(cycle)
        print(f"Updated Cycle Status: {cycle.status} (Expected: HARVESTED)")
        assert cycle.status == CropCycleStatus.HARVESTED
        
        # 5. Convert to Product
        product_info = {
            "name": "Premium Basmati Rice",
            "description": "High quality rice from Paddy Field",
            "category": "GRAINS",
            "base_price": 2.5,
            "currency": "USD",
            "quantity": 1200.0
        }
        
        product = service.convert_to_product(harvest.id, product_info, MockUser())
        print(f"Product created: ID={product.id}, Name={product.name}, Harvest_ID={product.harvest_id}")
        
        assert product.harvest_id == str(harvest.id)
        assert product.quantity_available == 1200.0
        
        print("VERIFICATION SUCCESSFUL")
        
    except Exception as e:
        print(f"VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify()
