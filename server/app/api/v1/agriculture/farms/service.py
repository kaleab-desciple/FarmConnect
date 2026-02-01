from __future__ import annotations
from typing import Optional
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from shared_models import (
    Farm as FarmDTO, 
    FarmCreate, 
    FarmUpdate, 
    Field as FieldDTO, 
    FieldCreate, 
    FieldUpdate
)
from app.domain.agriculture.entities import Farm as DomainFarm, Field as DomainField
from app.infrastructure.repositories.farm_repo import FarmRepository
from app.infrastructure.db.mappers import domain_to_dto, orm_to_domain

class FarmService:
    def __init__(self, session: Session):
        self.session = session
        self.farm_repo = FarmRepository(session)

    def create_farm(self, farmer_id: str, farm_data: FarmCreate) -> FarmDTO:
        domain_farm = DomainFarm(
            id=uuid4(),
            farmer_id=farmer_id,
            name=farm_data.name,
            location_lat=farm_data.location_lat,
            location_lng=farm_data.location_lng,
            location_address=farm_data.location_address,
            total_area_ha=farm_data.total_area_ha,
            boundary_geojson=farm_data.boundary_geojson,
            metadata=farm_data.metadata,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        saved_farm = self.farm_repo.save(domain_farm)
        self.session.commit()
        return domain_to_dto(saved_farm)

    def get_farm(self, farm_id: str) -> Optional[FarmDTO]:
        domain_farm = self.farm_repo.get_by_id(farm_id)
        if not domain_farm:
            return None
        return domain_to_dto(domain_farm)

    def list_farms(self, farmer_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> list[FarmDTO]:
        if farmer_id:
            domain_farms = self.farm_repo.get_by_farmer_id(farmer_id)
            # Apply slicing manually if needed or update repo, but usually farmer has few farms
            domain_farms = domain_farms[skip : skip + limit]
        else:
            domain_farms = self.farm_repo.list_all(skip=skip, limit=limit)
        
        return [domain_to_dto(farm) for farm in domain_farms]

    def update_farm(self, farm_id: str, farm_data: FarmUpdate) -> Optional[FarmDTO]:
        domain_farm = self.farm_repo.get_by_id(farm_id)
        if not domain_farm:
            return None
            
        update_dict = farm_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(domain_farm, key, value)
        
        domain_farm.updated_at = datetime.now(timezone.utc)
        updated_farm = self.farm_repo.save(domain_farm)
        self.session.commit()
        return domain_to_dto(updated_farm)

    def delete_farm(self, farm_id: str) -> bool:
        result = self.farm_repo.delete(farm_id)
        if result:
            self.session.commit()
        return result

    # Field Methods
    def create_field(self, farm_id: str, field_data: FieldCreate) -> FieldDTO:
        domain_field = DomainField(
            id=uuid4(),
            farm_id=farm_id,
            name=field_data.name,
            area_ha=field_data.area_ha,
            boundary_geojson=field_data.boundary_geojson,
            boundary_geom=field_data.boundary_geojson, # Legacy support
            centroid_geom=field_data.centroid_geom,
            soil_type=field_data.soil_type,
            soil_classification=field_data.soil_classification,
            elevation_m=field_data.elevation_m,
            slope_degree=field_data.slope_degree,
            irrigation_type=field_data.irrigation_type,
            metadata=field_data.metadata,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        saved_field = self.farm_repo.save_field(domain_field)
        self.session.commit()
        return domain_to_dto(saved_field)

    def list_fields(self, farm_id: str) -> list[FieldDTO]:
        domain_fields = self.farm_repo.list_fields_by_farm(farm_id)
        return [domain_to_dto(field) for field in domain_fields]
