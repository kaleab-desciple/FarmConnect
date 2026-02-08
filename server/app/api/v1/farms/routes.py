"""Farm and field API routes."""
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domain.farm.entities import Farm, FarmCreate, FarmUpdate, Field, FieldCreate, FieldUpdate, CropCycle, CropCycleCreate, CropCycleUpdate, FarmTask, FarmTaskCreate, FarmTaskUpdate
from app.infrastructure.repositories.farm_repo import FarmRepository, FieldRepository, CropCycleRepository, FarmTaskRepository

router = APIRouter()


@router.post("/farms", response_model=dict)
def create_farm(farm: FarmCreate, db: Session = Depends(get_db)):
    """Create a new farm."""
    repo = FarmRepository(db)
    created = repo.create(farm)
    return {"id": created.id, "status": "created"}


@router.get("/farms", response_model=List[dict])
def list_farms(farmer_id: str, db: Session = Depends(get_db)):
    """List all farms for a farmer."""
    repo = FarmRepository(db)
    farms = repo.get_by_farmer_id(farmer_id)
    return [
        {
            "id": f.id,
            "name": f.name,
            "location_lat": str(f.location_lat),
            "location_lng": str(f.location_lng),
            "total_area_ha": str(f.total_area_ha) if f.total_area_ha else None,
            "created_at": f.created_at.isoformat(),
        }
        for f in farms
    ]


@router.get("/farms/{farm_id}", response_model=dict)
def get_farm(farm_id: str, db: Session = Depends(get_db)):
    """Get a farm by ID."""
    repo = FarmRepository(db)
    farm = repo.get_by_id(farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return {
        "id": farm.id,
        "farmer_id": farm.farmer_id,
        "name": farm.name,
        "location_lat": str(farm.location_lat),
        "location_lng": str(farm.location_lng),
        "location_address": farm.location_address,
        "total_area_ha": str(farm.total_area_ha) if farm.total_area_ha else None,
        "boundary_geojson": farm.boundary_geojson,
        "created_at": farm.created_at.isoformat(),
        "updated_at": farm.updated_at.isoformat(),
    }


@router.put("/farms/{farm_id}", response_model=dict)
def update_farm(farm_id: str, farm: FarmUpdate, db: Session = Depends(get_db)):
    """Update a farm."""
    repo = FarmRepository(db)
    updated = repo.update(farm_id, farm)
    if not updated:
        raise HTTPException(status_code=404, detail="Farm not found")
    return {"id": updated.id, "status": "updated"}


@router.delete("/farms/{farm_id}", response_model=dict)
def delete_farm(farm_id: str, db: Session = Depends(get_db)):
    """Delete a farm."""
    repo = FarmRepository(db)
    if not repo.delete(farm_id):
        raise HTTPException(status_code=404, detail="Farm not found")
    return {"status": "deleted"}


# Field endpoints
@router.post("/fields", response_model=dict)
def create_field(field: FieldCreate, db: Session = Depends(get_db)):
    """Create a new field."""
    repo = FieldRepository(db)
    created = repo.create(field)
    return {"id": created.id, "status": "created"}


@router.get("/fields/{field_id}", response_model=dict)
def get_field(field_id: str, db: Session = Depends(get_db)):
    """Get a field by ID."""
    repo = FieldRepository(db)
    field = repo.get_by_id(field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return {
        "id": field.id,
        "farm_id": field.farm_id,
        "name": field.name,
        "area_ha": str(field.area_ha),
        "soil_type": field.soil_type,
        "irrigation_type": field.irrigation_type,
        "created_at": field.created_at.isoformat(),
    }


@router.get("/fields", response_model=List[dict])
def list_fields(farm_id: str, db: Session = Depends(get_db)):
    """List all fields for a farm."""
    repo = FieldRepository(db)
    fields = repo.get_by_farm_id(farm_id)
    return [
        {
            "id": f.id,
            "name": f.name,
            "area_ha": str(f.area_ha),
            "soil_type": f.soil_type,
            "irrigation_type": f.irrigation_type,
        }
        for f in fields
    ]


@router.put("/fields/{field_id}", response_model=dict)
def update_field(field_id: str, field: FieldUpdate, db: Session = Depends(get_db)):
    """Update a field."""
    repo = FieldRepository(db)
    updated = repo.update(field_id, field)
    if not updated:
        raise HTTPException(status_code=404, detail="Field not found")
    return {"id": updated.id, "status": "updated"}


@router.delete("/fields/{field_id}", response_model=dict)
def delete_field(field_id: str, db: Session = Depends(get_db)):
    """Delete a field."""
    repo = FieldRepository(db)
    if not repo.delete(field_id):
        raise HTTPException(status_code=404, detail="Field not found")
    return {"status": "deleted"}


# Crop Cycle endpoints
@router.post("/crop-cycles", response_model=dict)
def create_crop_cycle(cycle: CropCycleCreate, db: Session = Depends(get_db)):
    """Create a new crop cycle."""
    repo = CropCycleRepository(db)
    created = repo.create(cycle)
    return {"id": created.id, "status": "created"}


@router.get("/crop-cycles/{cycle_id}", response_model=dict)
def get_crop_cycle(cycle_id: str, db: Session = Depends(get_db)):
    """Get a crop cycle by ID."""
    repo = CropCycleRepository(db)
    cycle = repo.get_by_id(cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Crop cycle not found")
    return {
        "id": cycle.id,
        "field_id": cycle.field_id,
        "product_category": cycle.product_category,
        "crop_name": cycle.crop_name,
        "variety": cycle.variety,
        "planting_date": cycle.planting_date.isoformat() if cycle.planting_date else None,
        "expected_harvest_date": cycle.expected_harvest_date.isoformat() if cycle.expected_harvest_date else None,
        "status": cycle.status,
        "expected_yield_kg": str(cycle.expected_yield_kg) if cycle.expected_yield_kg else None,
    }


@router.get("/crop-cycles", response_model=List[dict])
def list_crop_cycles(field_id: str, db: Session = Depends(get_db)):
    """List all crop cycles for a field."""
    repo = CropCycleRepository(db)
    cycles = repo.get_by_field_id(field_id)
    return [
        {
            "id": c.id,
            "product_category": c.product_category,
            "crop_name": c.crop_name,
            "planting_date": c.planting_date.isoformat() if c.planting_date else None,
            "status": c.status,
        }
        for c in cycles
    ]


@router.put("/crop-cycles/{cycle_id}", response_model=dict)
def update_crop_cycle(cycle_id: str, cycle: CropCycleUpdate, db: Session = Depends(get_db)):
    """Update a crop cycle."""
    repo = CropCycleRepository(db)
    updated = repo.update(cycle_id, cycle)
    if not updated:
        raise HTTPException(status_code=404, detail="Crop cycle not found")
    return {"id": updated.id, "status": "updated"}


# Farm Task endpoints
@router.post("/tasks", response_model=dict)
def create_task(task: FarmTaskCreate, db: Session = Depends(get_db)):
    """Create a new farm task."""
    repo = FarmTaskRepository(db)
    created = repo.create(task)
    return {"id": created.id, "status": "created"}


@router.get("/tasks/{task_id}", response_model=dict)
def get_task(task_id: str, db: Session = Depends(get_db)):
    """Get a farm task by ID."""
    repo = FarmTaskRepository(db)
    task = repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "id": task.id,
        "field_id": task.field_id,
        "task_type": task.task_type,
        "title": task.title,
        "status": task.status,
        "priority": task.priority,
        "scheduled_date": task.scheduled_date.isoformat() if task.scheduled_date else None,
    }


@router.get("/tasks", response_model=List[dict])
def list_tasks(field_id: str, db: Session = Depends(get_db)):
    """List all tasks for a field."""
    repo = FarmTaskRepository(db)
    tasks = repo.get_by_field_id(field_id)
    return [
        {
            "id": t.id,
            "task_type": t.task_type,
            "title": t.title,
            "status": t.status,
            "priority": t.priority,
            "scheduled_date": t.scheduled_date.isoformat() if t.scheduled_date else None,
        }
        for t in tasks
    ]


@router.get("/tasks/upcoming", response_model=List[dict])
def list_upcoming_tasks(field_id: str, days: int = 7, db: Session = Depends(get_db)):
    """List upcoming tasks for a field."""
    repo = FarmTaskRepository(db)
    tasks = repo.get_upcoming(field_id, days)
    return [
        {
            "id": t.id,
            "task_type": t.task_type,
            "title": t.title,
            "status": t.status,
            "priority": t.priority,
            "scheduled_date": t.scheduled_date.isoformat() if t.scheduled_date else None,
        }
        for t in tasks
    ]


@router.put("/tasks/{task_id}", response_model=dict)
def update_task(task_id: str, task: FarmTaskUpdate, db: Session = Depends(get_db)):
    """Update a farm task."""
    repo = FarmTaskRepository(db)
    updated = repo.update(task_id, task)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"id": updated.id, "status": "updated"}
