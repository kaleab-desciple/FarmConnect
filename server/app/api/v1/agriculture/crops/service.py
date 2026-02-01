from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.infrastructure.repositories.crop_repo import CropCycleRepository
from app.infrastructure.repositories.farm_repo import FarmRepository
from app.infrastructure.db.mappers import domain_to_dto, domain_to_orm
from app.domain.agriculture.entities import CropCycle as DomainCropCycle
from shared_models import CropCycle as CropCycleDTO, CropCycleCreate, CropCycleUpdate, HarvestRecord

class CropCycleService:
    def __init__(self, session: Session):
        self.session = session
        self.crop_repo = CropCycleRepository(session)
        self.farm_repo = FarmRepository(session)

    def create_crop_cycle(self, field_id: str, cycle_data: CropCycleCreate) -> CropCycleDTO:
        """Create a new crop cycle"""
        domain_cycle = DomainCropCycle(
            id=uuid4(),
            field_id=UUID(field_id),
            product_category=cycle_data.product_category,
            crop_name=cycle_data.crop_name,
            variety=cycle_data.variety,
            cultivar=cycle_data.cultivar,
            planting_date=cycle_data.planting_date,
            expected_harvest_date=cycle_data.expected_harvest_date,
            expected_yield_kg=cycle_data.expected_yield_kg,
            seed_source=cycle_data.seed_source,
            planting_density_per_ha=cycle_data.planting_density_per_ha,
            notes=cycle_data.notes,
            metadata=cycle_data.metadata,
            status="PLANTED",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        saved_cycle = self.crop_repo.save(domain_cycle)
        self.session.commit()
        return domain_to_dto(saved_cycle)

    def get_crop_cycle(self, cycle_id: str) -> Optional[CropCycleDTO]:
        """Get crop cycle by ID"""
        domain_cycle = self.crop_repo.get_by_id(cycle_id)
        if not domain_cycle:
            return None
        return domain_to_dto(domain_cycle)

    def list_crop_cycles(
        self, 
        field_id: str, 
        status_filter: Optional[str] = None
    ) -> List[CropCycleDTO]:
        """List crop cycles for a field"""
        domain_cycles = self.crop_repo.list_by_field(field_id, status_filter)
        return [domain_to_dto(cycle) for cycle in domain_cycles]

    def list_active_cycles(self, farmer_id: Optional[str] = None) -> List[CropCycleDTO]:
        """List active crop cycles"""
        if farmer_id:
            domain_cycles = self.crop_repo.list_active_by_farmer(farmer_id)
        else:
            domain_cycles = self.crop_repo.list_all_active()
        return [domain_to_dto(cycle) for cycle in domain_cycles]

    def update_crop_cycle(self, cycle_id: str, cycle_data: CropCycleUpdate) -> Optional[CropCycleDTO]:
        """Update crop cycle"""
        domain_cycle = self.crop_repo.get_by_id(cycle_id)
        if not domain_cycle:
            return None
        
        # Update fields
        update_dict = cycle_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                setattr(domain_cycle, field, value)
        
        domain_cycle.updated_at = datetime.now(timezone.utc)
        
        saved_cycle = self.crop_repo.save(domain_cycle)
        self.session.commit()
        return domain_to_dto(saved_cycle)

    def record_harvest(self, cycle_id: str, harvest_data: HarvestRecord) -> Optional[CropCycleDTO]:
        """Record harvest for crop cycle"""
        domain_cycle = self.crop_repo.get_by_id(cycle_id)
        if not domain_cycle:
            return None
        
        domain_cycle.actual_harvest_date = harvest_data.actual_harvest_date
        domain_cycle.actual_yield_kg = harvest_data.actual_yield_kg
        domain_cycle.status = "HARVESTED"
        
        if harvest_data.notes:
            harvest_note = f"Harvest recorded: {harvest_data.notes}"
            if domain_cycle.notes:
                domain_cycle.notes = f"{domain_cycle.notes}\n\n{harvest_note}"
            else:
                domain_cycle.notes = harvest_note
        
        domain_cycle.updated_at = datetime.now(timezone.utc)
        
        saved_cycle = self.crop_repo.save(domain_cycle)
        self.session.commit()
        return domain_to_dto(saved_cycle)

    def delete_crop_cycle(self, cycle_id: str) -> bool:
        """Delete crop cycle"""
        result = self.crop_repo.delete(cycle_id)
        if result:
            self.session.commit()
        return result

    def get_field_farmer_id(self, field_id: str) -> Optional[str]:
        """Get farmer ID for a field (for permission checks)"""
        from app.infrastructure.db.models.farm import FieldORM, FarmORM
        
        result = self.session.query(FarmORM.farmer_id).join(
            FieldORM, FarmORM.id == FieldORM.farm_id
        ).filter(
            FieldORM.id == field_id,
            FieldORM.deleted_at == None,
            FarmORM.deleted_at == None
        ).first()
        
        return result[0] if result else None
