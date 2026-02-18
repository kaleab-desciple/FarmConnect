"""Farm repository implementation."""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.domain.farm.entities import Farm, FarmCreate, FarmUpdate, Field, FieldCreate, FieldUpdate, CropCycle, CropCycleCreate, CropCycleUpdate
from app.infrastructure.db.models import FarmORM, FieldORM, CropCycleORM, FarmTaskORM


class FarmRepository:
    """Repository for Farm operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, farm_data: FarmCreate) -> Farm:
        """Create a new farm."""
        try:
            orm = FarmORM(
                farmer_id=farm_data.farmer_id,
                name=farm_data.name,
                location_lat=farm_data.location_lat,
                location_lng=farm_data.location_lng,
                location_address=farm_data.location_address,
                total_area_ha=farm_data.total_area_ha,
                boundary_geojson=farm_data.boundary_geojson,
                centroid_geojson=farm_data.centroid_geojson,
                metadata_=farm_data.metadata,
            )
            self.session.add(orm)
            self.session.flush()
            self.session.commit()
            self.session.refresh(orm)
            return self._to_domain(orm)
        except Exception as e:
            from sqlalchemy import exc
            if isinstance(e, exc.DBAPIError):
                self.session.rollback()
                raise Exception(f"Database error creating farm: {e.orig.detail if hasattr(e.orig, 'detail') else str(e)}")
            raise

    def get_by_id(self, farm_id: str) -> Optional[Farm]:
        """Get farm by ID."""
        orm = self.session.query(FarmORM).filter(
            and_(FarmORM.id == farm_id, FarmORM.deleted_at.is_(None))
        ).first()
        return self._to_domain(orm) if orm else None

    def get_by_farmer_id(self, farmer_id: str) -> List[Farm]:
        """Get all farms for a farmer."""
        orms = self.session.query(FarmORM).filter(
            and_(FarmORM.farmer_id == farmer_id, FarmORM.deleted_at.is_(None))
        ).all()
        return [self._to_domain(orm) for orm in orms]

    def update(self, farm_id: str, farm_data: FarmUpdate) -> Optional[Farm]:
        """Update a farm."""
        orm = self.session.query(FarmORM).filter(FarmORM.id == farm_id).first()
        if not orm:
            return None
        update_data = farm_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "metadata":
                setattr(orm, "metadata_", value)
            else:
                setattr(orm, key, value)
        self.session.flush()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def delete(self, farm_id: str) -> bool:
        """Soft delete a farm."""
        from datetime import datetime, timezone
        orm = self.session.query(FarmORM).filter(FarmORM.id == farm_id).first()
        if not orm:
            return False
        orm.deleted_at = datetime.now(timezone.utc)
        self.session.flush()
        return True

    def _to_domain(self, orm: FarmORM) -> Farm:
        """Convert ORM to domain entity."""
        return Farm(
            id=orm.id,
            farmer_id=orm.farmer_id,
            name=orm.name,
            location_lat=orm.location_lat,
            location_lng=orm.location_lng,
            location_address=orm.location_address,
            total_area_ha=orm.total_area_ha,
            boundary_geojson=orm.boundary_geojson,
            centroid_geojson=orm.centroid_geojson,
            metadata=orm.metadata_,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )


class FieldRepository:
    """Repository for Field operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, field_data: FieldCreate) -> Field:
        """Create a new field."""
        orm = FieldORM(
            farm_id=field_data.farm_id,
            name=field_data.name,
            area_ha=field_data.area_ha,
            boundary_geojson=field_data.boundary_geojson,
            centroid_geojson=field_data.centroid_geojson,
            soil_type=field_data.soil_type,
            soil_classification=field_data.soil_classification,
            elevation_m=field_data.elevation_m,
            slope_degree=field_data.slope_degree,
            irrigation_type=field_data.irrigation_type,
            drainage_type=field_data.drainage_type,
            metadata_=field_data.metadata,
        )
        self.session.add(orm)
        self.session.flush()
        self.session.commit()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def get_by_id(self, field_id: str) -> Optional[Field]:
        """Get field by ID."""
        orm = self.session.query(FieldORM).filter(
            and_(FieldORM.id == field_id, FieldORM.deleted_at.is_(None))
        ).first()
        return self._to_domain(orm) if orm else None

    def get_by_farm_id(self, farm_id: str) -> List[Field]:
        """Get all fields for a farm."""
        orms = self.session.query(FieldORM).filter(
            and_(FieldORM.farm_id == farm_id, FieldORM.deleted_at.is_(None))
        ).all()
        return [self._to_domain(orm) for orm in orms]

    def update(self, field_id: str, field_data: FieldUpdate) -> Optional[Field]:
        """Update a field."""
        orm = self.session.query(FieldORM).filter(FieldORM.id == field_id).first()
        if not orm:
            return None
        update_data = field_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "metadata":
                setattr(orm, "metadata_", value)
            else:
                setattr(orm, key, value)
        self.session.flush()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def delete(self, field_id: str) -> bool:
        """Soft delete a field."""
        from datetime import datetime, timezone
        orm = self.session.query(FieldORM).filter(FieldORM.id == field_id).first()
        if not orm:
            return False
        orm.deleted_at = datetime.now(timezone.utc)
        self.session.flush()
        return True

    def _to_domain(self, orm: FieldORM) -> Field:
        """Convert ORM to domain entity."""
        return Field(
            id=orm.id,
            farm_id=orm.farm_id,
            name=orm.name,
            area_ha=orm.area_ha,
            boundary_geojson=orm.boundary_geojson,
            centroid_geojson=orm.centroid_geojson,
            soil_type=orm.soil_type,
            soil_classification=orm.soil_classification,
            elevation_m=orm.elevation_m,
            slope_degree=orm.slope_degree,
            irrigation_type=orm.irrigation_type,
            drainage_type=orm.drainage_type,
            metadata=orm.metadata_,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )


class CropCycleRepository:
    """Repository for CropCycle operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, cycle_data: CropCycleCreate) -> CropCycle:
        """Create a new crop cycle."""
        orm = CropCycleORM(
            field_id=cycle_data.field_id,
            product_category=cycle_data.product_category,
            crop_name=cycle_data.crop_name,
            variety=cycle_data.variety,
            cultivar=cycle_data.cultivar,
            planting_date=cycle_data.planting_date,
            expected_harvest_date=cycle_data.expected_harvest_date,
            actual_harvest_date=cycle_data.actual_harvest_date,
            status=cycle_data.status,
            expected_yield_kg=cycle_data.expected_yield_kg,
            actual_yield_kg=cycle_data.actual_yield_kg,
            yield_quality_grade=cycle_data.yield_quality_grade,
            seed_source=cycle_data.seed_source,
            planting_density_per_ha=cycle_data.planting_density_per_ha,
            seed_cost_usd=cycle_data.seed_cost_usd,
            notes=cycle_data.notes,
            metadata_=cycle_data.metadata,
        )
        self.session.add(orm)
        self.session.flush()
        self.session.commit()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def get_by_id(self, cycle_id: str) -> Optional[CropCycle]:
        """Get crop cycle by ID."""
        orm = self.session.query(CropCycleORM).filter(
            and_(CropCycleORM.id == cycle_id, CropCycleORM.deleted_at.is_(None))
        ).first()
        return self._to_domain(orm) if orm else None

    def get_by_field_id(self, field_id: str) -> List[CropCycle]:
        """Get all crop cycles for a field."""
        orms = self.session.query(CropCycleORM).filter(
            and_(CropCycleORM.field_id == field_id, CropCycleORM.deleted_at.is_(None))
        ).all()
        return [self._to_domain(orm) for orm in orms]

    def update(self, cycle_id: str, cycle_data: CropCycleUpdate) -> Optional[CropCycle]:
        """Update a crop cycle."""
        orm = self.session.query(CropCycleORM).filter(CropCycleORM.id == cycle_id).first()
        if not orm:
            return None
        update_data = cycle_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "metadata":
                setattr(orm, "metadata_", value)
            else:
                setattr(orm, key, value)
        self.session.flush()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def delete(self, cycle_id: str) -> bool:
        """Soft delete a crop cycle."""
        from datetime import datetime, timezone
        orm = self.session.query(CropCycleORM).filter(CropCycleORM.id == cycle_id).first()
        if not orm:
            return False
        orm.deleted_at = datetime.now(timezone.utc)
        self.session.flush()
        return True

    def _to_domain(self, orm: CropCycleORM) -> CropCycle:
        """Convert ORM to domain entity."""
        return CropCycle(
            id=orm.id,
            field_id=orm.field_id,
            product_category=orm.product_category,
            crop_name=orm.crop_name,
            variety=orm.variety,
            cultivar=orm.cultivar,
            planting_date=orm.planting_date,
            expected_harvest_date=orm.expected_harvest_date,
            actual_harvest_date=orm.actual_harvest_date,
            status=orm.status,
            expected_yield_kg=orm.expected_yield_kg,
            actual_yield_kg=orm.actual_yield_kg,
            yield_quality_grade=orm.yield_quality_grade,
            seed_source=orm.seed_source,
            planting_density_per_ha=orm.planting_density_per_ha,
            seed_cost_usd=orm.seed_cost_usd,
            notes=orm.notes,
            metadata=orm.metadata_,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )

"""
class FarmTaskRepository:
    #Repository for FarmTask operations.

    def __init__(self, session: Session):
        self.session = session

    def create(self, task_data: FarmTaskCreate) -> FarmTask:
        # Create a new farm task.
        orm = FarmTaskORM(
            field_id=task_data.field_id,
            crop_cycle_id=task_data.crop_cycle_id,
            task_type=task_data.task_type,
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            scheduled_date=task_data.scheduled_date,
            scheduled_time=task_data.scheduled_time,
            duration_estimate_hours=task_data.duration_estimate_hours,
            window_start_date=task_data.window_start_date,
            window_end_date=task_data.window_end_date,
            completed_date=task_data.completed_date,
            completed_time=task_data.completed_time,
            completed_by=task_data.completed_by,
            duration_actual_hours=task_data.duration_actual_hours,
            assigned_to=task_data.assigned_to,
            labor_count=task_data.labor_count,
            equipment_needed=task_data.equipment_needed,
            materials_needed=task_data.materials_needed,
            estimated_cost_usd=task_data.estimated_cost_usd,
            actual_cost_usd=task_data.actual_cost_usd,
            parent_task_id=task_data.parent_task_id,
            depends_on_tasks=task_data.depends_on_tasks,
            weather_dependent=task_data.weather_dependent,
            soil_moisture_condition=task_data.soil_moisture_condition,
            auto_generated=task_data.auto_generated,
            generation_reason=task_data.generation_reason,
            notes=task_data.notes,
            completion_notes=task_data.completion_notes,
            completion_photos=task_data.completion_photos,
            metadata_=task_data.metadata,
        )
        self.session.add(orm)
        self.session.flush()
        self.session.commit()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def get_by_id(self, task_id: str) -> Optional[FarmTask]:
        # Get farm task by ID.
        orm = self.session.query(FarmTaskORM).filter(
            and_(FarmTaskORM.id == task_id, FarmTaskORM.deleted_at.is_(None))
        ).first()
        return self._to_domain(orm) if orm else None

    def get_by_field_id(self, field_id: str) -> List[FarmTask]:
        # Get all tasks for a field.
        orms = self.session.query(FarmTaskORM).filter(
            and_(FarmTaskORM.field_id == field_id, FarmTaskORM.deleted_at.is_(None))
        ).all()
        return [self._to_domain(orm) for orm in orms]

    def get_upcoming(self, field_id: str, days: int = 7) -> List[FarmTask]:
        # Get upcoming tasks for a field.
        from datetime import date, timedelta
        end_date = date.today() + timedelta(days=days)
        orms = self.session.query(FarmTaskORM).filter(
            and_(
                FarmTaskORM.field_id == field_id,
                FarmTaskORM.scheduled_date >= date.today(),
                FarmTaskORM.scheduled_date <= end_date,
                FarmTaskORM.status.in_(['PENDING', 'SCHEDULED']),
                FarmTaskORM.deleted_at.is_(None)
            )
        ).order_by(FarmTaskORM.scheduled_date).all()
        return [self._to_domain(orm) for orm in orms]

    def update(self, task_id: str, task_data: FarmTaskUpdate) -> Optional[FarmTask]:
        #Update a farm task.
        orm = self.session.query(FarmTaskORM).filter(FarmTaskORM.id == task_id).first()
        if not orm:
            return None
        update_data = task_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "metadata":
                setattr(orm, "metadata_", value)
            else:
                setattr(orm, key, value)
        self.session.flush()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def delete(self, task_id: str) -> bool:
        # Soft delete a farm task
        from datetime import datetime, timezone
        orm = self.session.query(FarmTaskORM).filter(FarmTaskORM.id == task_id).first()
        if not orm:
            return False
        orm.deleted_at = datetime.now(timezone.utc)
        self.session.flush()
        return True

    def _to_domain(self, orm: FarmTaskORM) -> FarmTask:
        # Convert ORM to domain entity.
        return FarmTask(
            id=orm.id,
            field_id=orm.field_id,
            crop_cycle_id=orm.crop_cycle_id,
            task_type=orm.task_type,
            title=orm.title,
            description=orm.description,
            status=orm.status,
            priority=orm.priority,
            scheduled_date=orm.scheduled_date,
            scheduled_time=orm.scheduled_time,
            duration_estimate_hours=orm.duration_estimate_hours,
            window_start_date=orm.window_start_date,
            window_end_date=orm.window_end_date,
            completed_date=orm.completed_date,
            completed_time=orm.completed_time,
            completed_by=orm.completed_by,
            duration_actual_hours=orm.duration_actual_hours,
            assigned_to=orm.assigned_to,
            labor_count=orm.labor_count,
            equipment_needed=orm.equipment_needed,
            materials_needed=orm.materials_needed,
            estimated_cost_usd=orm.estimated_cost_usd,
            actual_cost_usd=orm.actual_cost_usd,
            parent_task_id=orm.parent_task_id,
            depends_on_tasks=orm.depends_on_tasks,
            weather_dependent=orm.weather_dependent,
            soil_moisture_condition=orm.soil_moisture_condition,
            auto_generated=orm.auto_generated,
            generation_reason=orm.generation_reason,
            notes=orm.notes,
            completion_notes=orm.completion_notes,
            completion_photos=orm.completion_photos,
            metadata=orm.metadata_,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
"""