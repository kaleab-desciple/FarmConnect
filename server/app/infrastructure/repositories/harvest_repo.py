"""Harvest repository for database operations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.infrastructure.db.models.harvest import HarvestORM
from app.infrastructure.db.models.farm import CropCycleORM, FieldORM
from app.infrastructure.db.mappers import orm_to_domain, domain_to_orm
from app.domain.farm.entities import Harvest

class HarvestRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, harvest: Harvest) -> Harvest:
        orm = domain_to_orm(harvest)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return orm_to_domain(orm)

    def get_by_id(self, harvest_id: str) -> Optional[Harvest]:
        orm = self.db.query(HarvestORM).filter(HarvestORM.id == harvest_id).first()
        return orm_to_domain(orm) if orm else None

    def get_by_farmer_id(self, farmer_id: str) -> List[Harvest]:
        orms = self.db.query(HarvestORM).filter(HarvestORM.farmer_id == farmer_id).all()
        return [orm_to_domain(orm) for orm in orms]

    def get_by_crop_cycle_id(self, crop_cycle_id: str) -> List[Harvest]:
        orms = self.db.query(HarvestORM).filter(HarvestORM.crop_cycle_id == crop_cycle_id).all()
        return [orm_to_domain(orm) for orm in orms]

    def get_total_harvested_for_cycle(self, crop_cycle_id: str) -> float:
        from sqlalchemy import func
        result = self.db.query(func.sum(HarvestORM.quantity_harvested)).filter(HarvestORM.crop_cycle_id == crop_cycle_id).scalar()
        return float(result) if result else 0.0

    def get_crop_cycle_with_yield(self, crop_cycle_id: str):
        return self.db.query(CropCycleORM).filter(CropCycleORM.id == crop_cycle_id).first()
