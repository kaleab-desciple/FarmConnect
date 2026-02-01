from typing import List, Optional
from sqlalchemy.orm import Session

from app.infrastructure.db.mappers import orm_to_domain, domain_to_orm
from app.infrastructure.db.models.crop import CropCycleORM
from app.domain.agriculture.entities import CropCycle as DomainCropCycle

class CropCycleRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, crop_cycle: DomainCropCycle) -> DomainCropCycle:
        orm = self.session.query(CropCycleORM).filter(CropCycleORM.id == str(crop_cycle.id)).one_or_none() if crop_cycle.id else None
        
        if orm:
            # Update existing crop cycle
            updated_orm = domain_to_orm(crop_cycle)
            for key, value in updated_orm.__dict__.items():
                if not key.startswith('_') and key != 'id':
                    setattr(orm, key, value)
        else:
            # Create new crop cycle
            orm = domain_to_orm(crop_cycle)
            self.session.add(orm)
        
        self.session.flush()
        return orm_to_domain(orm)

    def get_by_id(self, cycle_id: str) -> Optional[DomainCropCycle]:
        orm = self.session.query(CropCycleORM).filter(
            CropCycleORM.id == cycle_id, 
            CropCycleORM.deleted_at == None
        ).one_or_none()
        if not orm:
            return None
        return orm_to_domain(orm)

    def list_by_field(self, field_id: str, status_filter: Optional[str] = None) -> List[DomainCropCycle]:
        query = self.session.query(CropCycleORM).filter(
            CropCycleORM.field_id == field_id,
            CropCycleORM.deleted_at == None
        )
        
        if status_filter:
            query = query.filter(CropCycleORM.status == status_filter)
        
        orms = query.order_by(CropCycleORM.planting_date.desc()).all()
        return [orm_to_domain(orm) for orm in orms]

    def list_active_by_farmer(self, farmer_id: str) -> List[DomainCropCycle]:
        from app.infrastructure.db.models.farm import FarmORM, FieldORM
        
        orms = self.session.query(CropCycleORM).join(
            FieldORM, CropCycleORM.field_id == FieldORM.id
        ).join(
            FarmORM, FieldORM.farm_id == FarmORM.id
        ).filter(
            FarmORM.farmer_id == farmer_id,
            CropCycleORM.status.in_(['PLANTED', 'GROWING']),
            CropCycleORM.deleted_at == None
        ).order_by(CropCycleORM.planting_date.desc()).all()
        
        return [orm_to_domain(orm) for orm in orms]

    def list_all_active(self) -> List[DomainCropCycle]:
        orms = self.session.query(CropCycleORM).filter(
            CropCycleORM.status.in_(['PLANTED', 'GROWING']),
            CropCycleORM.deleted_at == None
        ).order_by(CropCycleORM.planting_date.desc()).all()
        
        return [orm_to_domain(orm) for orm in orms]

    def delete(self, cycle_id: str) -> bool:
        orm = self.session.query(CropCycleORM).filter(CropCycleORM.id == cycle_id).one_or_none()
        if not orm:
            return False
        from datetime import datetime, timezone
        orm.deleted_at = datetime.now(timezone.utc)
        self.session.flush()
        return True
