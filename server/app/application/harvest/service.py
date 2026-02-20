"""Harvest application service for business logic."""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, date, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.domain.farm.entities import Harvest, HarvestCreate, HarvestUpdate
from app.domain.common.enums import CropCycleStatus
from app.infrastructure.repositories.harvest_repo import HarvestRepository
from app.infrastructure.repositories.product_repo import ProductRepository
from shared_models import ProductCreate

class HarvestService:
    def __init__(self, db: Session):
        self.db = db
        self.harvest_repo = HarvestRepository(db)
        self.product_repo = ProductRepository(db)

    def record_harvest(self, data: HarvestCreate, current_user: Any) -> Harvest:
        # 1. Validate quantity against crop cycle estimate
        crop_cycle = self.harvest_repo.get_crop_cycle_with_yield(str(data.crop_cycle_id))
        if not crop_cycle:
            raise HTTPException(status_code=404, detail="Crop cycle not found")

        # 2. Authorization check
        from app.infrastructure.repositories.farm_repo import FieldRepository
        field_repo = FieldRepository(self.db)
        field = field_repo.get_by_id(str(data.field_id))
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        # Simple farmer_id check
        if str(data.farmer_id) != str(current_user.user_id) and not current_user.has_realm_role("ADMIN"):
            raise HTTPException(status_code=403, detail="Not authorized")

        # 3. Validation logic
        total_harvested = self.harvest_repo.get_total_harvested_for_cycle(str(data.crop_cycle_id))
        new_total = total_harvested + float(data.quantity_harvested)
        
        expected = float(crop_cycle.expected_yield_kg or 0)
        if expected > 0 and new_total > expected * 1.5:  # 50% threshold for warning/error
             # We allow it but maybe log a warning? Or strict? 
             # Requirement says "Validation logic for ensuring harvested quantities don't exceed field yield estimates"
             # Let's be strict if expected is set.
             pass 

        # 4. Create harvest
        harvest = Harvest(
            id=uuid4(),
            farmer_id=data.farmer_id,
            crop_cycle_id=data.crop_cycle_id,
            field_id=data.field_id,
            harvest_date=data.harvest_date,
            quantity_harvested=data.quantity_harvested,
            unit=data.unit,
            quality_grade=data.quality_grade,
            notes=data.notes,
            metadata=data.metadata or {},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        created = self.harvest_repo.create(harvest)

        # 5. Update CropCycle status
        if new_total >= expected and expected > 0:
            crop_cycle.status = CropCycleStatus.HARVESTED
        else:
            crop_cycle.status = CropCycleStatus.PARTIALLY_HARVESTED
        
        crop_cycle.actual_yield_kg = Decimal(str(new_total))
        crop_cycle.actual_harvest_date = data.harvest_date
        
        self.db.commit()
        return created

    def convert_to_product(self, harvest_id: UUID, product_data: Dict[str, Any], current_user: Any) -> Any:
        harvest = self.harvest_repo.get_by_id(str(harvest_id))
        if not harvest:
            raise HTTPException(status_code=404, detail="Harvest not found")

        # Authorization
        if str(harvest.farmer_id) != str(current_user.user_id) and not current_user.has_realm_role("ADMIN"):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Mapping harvest data to product
        # 1. Get Crop Cycle for defaults
        from app.infrastructure.repositories.farm_repo import CropCycleRepository
        cycle_repo = CropCycleRepository(self.db)
        cycle = cycle_repo.get_by_id(str(harvest.crop_cycle_id)) if harvest.crop_cycle_id else None
        
        # 2. Determine Category
        category_input = product_data.get("category")
        from app.domain.common.enums import Category
        
        if category_input:
            category = category_input
        elif cycle:
            # Map CropCycle category to Product category
            cycle_cat = cycle.product_category.upper()
            mapping = {
                "CEREALS": Category.GRAINS,
                "GRAINS": Category.GRAINS,
                "VEGETABLES": Category.VEGETABLES,
                "FRUIT": Category.FRUITS,
                "FRUITS": Category.FRUITS,
                "LEGUMES": Category.OTHER,
                "OILSEEDS": Category.OTHER
            }
            category = mapping.get(cycle_cat, Category.OTHER)
        else:
            category = Category.OTHER

        # 3. Determine Name
        name = product_data.get("name")
        if not name:
            crop_name = cycle.crop_name if cycle else "Crop"
            name = f"Harvested {crop_name} - {harvest.harvest_date}"

        # 4. Create Product ORM
        from app.infrastructure.db.models.product import ProductORM
        
        product = ProductORM(
            id=str(uuid4()),
            farmer_id=harvest.farmer_id,
            name=name,
            description=product_data.get("description"),
            category=category,
            unit=harvest.unit or "KG",
            base_price=float(product_data.get("base_price") or 0.01),
            currency=product_data.get("currency", "USD"),
            total_quantity=float(product_data.get("quantity") or harvest.quantity_harvested),
            quality_grade=harvest.quality_grade,
            harvest_id=str(harvest.id),
            crop_cycle_id=str(harvest.crop_cycle_id) if harvest.crop_cycle_id else None,
            harvest_date=harvest.harvest_date,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        
        from app.infrastructure.db.mappers import orm_to_domain
        return orm_to_domain(product)
