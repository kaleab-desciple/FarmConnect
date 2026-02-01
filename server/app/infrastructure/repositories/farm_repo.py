from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.infrastructure.db.mappers import orm_to_domain, domain_to_orm
from app.infrastructure.db.models.farm import FarmORM, FieldORM
from app.domain.agriculture.entities import Farm as DomainFarm, Field as DomainField

class FarmRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, farm: DomainFarm) -> DomainFarm:
        orm = self.session.query(FarmORM).filter(FarmORM.id == str(farm.id)).one_or_none() if farm.id else None
        
        if orm:
            # Update existing farm
            updated_orm = domain_to_orm(farm)
            for key, value in updated_orm.__dict__.items():
                if not key.startswith('_') and key != 'id':
                    setattr(orm, key, value)
        else:
            # Create new farm
            orm = domain_to_orm(farm)
            self.session.add(orm)
        
        self.session.flush()
        return orm_to_domain(orm)

    def get_by_id(self, farm_id: str) -> Optional[DomainFarm]:
        orm = self.session.query(FarmORM).filter(FarmORM.id == farm_id, FarmORM.deleted_at == None).one_or_none()
        if not orm:
            return None
        return orm_to_domain(orm)

    def get_by_farmer_id(self, farmer_id: str) -> List[DomainFarm]:
        orms = self.session.query(FarmORM).filter(FarmORM.farmer_id == farmer_id, FarmORM.deleted_at == None).all()
        return [orm_to_domain(orm) for orm in orms]

    def list_all(self, skip: int = 0, limit: int = 100) -> List[DomainFarm]:
        orms = self.session.query(FarmORM).filter(FarmORM.deleted_at == None).order_by(FarmORM.created_at.desc()).offset(skip).limit(limit).all()
        return [orm_to_domain(orm) for orm in orms]

    def delete(self, farm_id: str) -> bool:
        orm = self.session.query(FarmORM).filter(FarmORM.id == farm_id).one_or_none()
        if not orm:
            return False
        from datetime import datetime, timezone
        orm.deleted_at = datetime.now(timezone.utc)
        self.session.flush()
        return True

    # Field Methods
    def save_field(self, field: DomainField) -> DomainField:
        orm = self.session.query(FieldORM).filter(FieldORM.id == str(field.id)).one_or_none() if field.id else None
        
        if orm:
            # Update existing field
            updated_orm = domain_to_orm(field)
            for key, value in updated_orm.__dict__.items():
                if not key.startswith('_') and key != 'id':
                    setattr(orm, key, value)
        else:
            # Create new field
            orm = domain_to_orm(field)
            self.session.add(orm)
        
        self.session.flush()
        return orm_to_domain(orm)

    def get_field_by_id(self, field_id: str) -> Optional[DomainField]:
        orm = self.session.query(FieldORM).filter(FieldORM.id == field_id, FieldORM.deleted_at == None).one_or_none()
        if not orm:
            return None
        return orm_to_domain(orm)

    def list_fields_by_farm(self, farm_id: str) -> List[DomainField]:
        orms = self.session.query(FieldORM).filter(FieldORM.farm_id == farm_id, FieldORM.deleted_at == None).order_by(FieldORM.created_at.desc()).all()
        return [orm_to_domain(orm) for orm in orms]
