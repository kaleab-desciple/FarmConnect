"""
Farm API Routes - Complete Implementation
Farm Connect AgriManagement

Following the same architecture, patterns, and structure as the forum implementation.
Routes → Service → Repository pattern with proper authentication and authorization.
"""
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth.dependencies import get_current_user, get_optional_user, require_auth
from app.domain.farm.entities import (
    Farm, FarmCreate, FarmUpdate,
    Field, FieldCreate, FieldUpdate,
    CropCycle, CropCycleCreate, CropCycleUpdate,
    FarmTask, FarmTaskCreate, FarmTaskUpdate
)

from .service import FarmService


router = APIRouter()


# ============ Farm Routes ============

@router.post(
    "/farms",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
)
async def create_farm(
    farm: FarmCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Create a new farm.
    
    Requires authentication. Users can create farms for themselves,
    or agents/admins can create farms for farmers.
    """
    try:
        service = FarmService(db)
        created = service.create_farm(farm, current_user)
        
        return {
            "id": str(created.id),
            "farmer_id": created.farmer_id,
            "name": created.name,
            "location_lat": str(created.location_lat) if created.location_lat else None,
            "location_lng": str(created.location_lng) if created.location_lng else None,
            "location_address": created.location_address,
            "total_area_ha": str(created.total_area_ha) if created.total_area_ha else None,
            "created_at": created.created_at.isoformat() if created.created_at else None,
            "status": "created"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/farms", response_model=Dict[str, Any])
async def list_farms(
    farmer_id: Optional[str] = Query(None, description="Filter by farmer ID"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    List farms with filtering and pagination.
    
    - **farmer_id**: Filter by farmer (admins/agents can query any farmer)
    - **page**: Page number
    - **page_size**: Items per page
    
    Regular users can only see their own farms unless they have admin/agent role.
    """
    try:
        service = FarmService(db)
        return service.list_farms(farmer_id, current_user, page, page_size)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/farms/{farm_id}", response_model=Dict[str, Any])
async def get_farm(
    farm_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Get a farm by ID.
    
    Requires authentication. Users can only access their own farms
    unless they have admin/agent role.
    """
    try:
        service = FarmService(db)
        farm = service.get_farm(farm_id, current_user)
        
        return {
            "id": str(farm.id),
            "farmer_id": farm.farmer_id,
            "name": farm.name,
            "location_lat": str(farm.location_lat) if farm.location_lat else None,
            "location_lng": str(farm.location_lng) if farm.location_lng else None,
            "location_address": farm.location_address,
            "total_area_ha": str(farm.total_area_ha) if farm.total_area_ha else None,
            "boundary_geojson": farm.boundary_geojson,
            "centroid_geojson": farm.centroid_geojson,
            "metadata": farm.metadata,
            "created_at": farm.created_at.isoformat() if farm.created_at else None,
            "updated_at": farm.updated_at.isoformat() if farm.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/farms/{farm_id}", response_model=Dict[str, Any])
async def update_farm(
    farm_id: str,
    farm: FarmUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Update a farm.
    
    Only the farm owner or admin can update.
    """
    try:
        service = FarmService(db)
        updated = service.update_farm(farm_id, farm, current_user)
        
        return {
            "id": str(updated.id),
            "farmer_id": updated.farmer_id,
            "name": updated.name,
            "location_lat": str(updated.location_lat) if updated.location_lat else None,
            "location_lng": str(updated.location_lng) if updated.location_lng else None,
            "location_address": updated.location_address,
            "total_area_ha": str(updated.total_area_ha) if updated.total_area_ha else None,
            "updated_at": updated.updated_at.isoformat() if updated.updated_at else None,
            "status": "updated"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/farms/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farm(
    farm_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Delete a farm (soft delete).
    
    Only the farm owner or admin can delete.
    """
    try:
        service = FarmService(db)
        service.delete_farm(farm_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ Field Routes ============

@router.post(
    "/fields",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
)
async def create_field(
    field: FieldCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Create a new field in a farm.
    """
    try:
        service = FarmService(db)
        created = service.create_field(field, current_user)
        
        return {
            "id": str(created.id),
            "farm_id": str(created.farm_id),
            "name": created.name,
            "area_ha": str(created.area_ha),
            "soil_type": created.soil_type,
            "created_at": created.created_at.isoformat() if created.created_at else None,
            "status": "created"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fields", response_model=List[Dict[str, Any]])
async def list_fields(
    farm_id: str = Query(..., description="Farm ID"),
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    List all fields for a farm.
    """
    try:
        service = FarmService(db)
        return service.list_fields(farm_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fields/{field_id}", response_model=Dict[str, Any])
async def get_field(
    field_id: str,
    days: Optional[int] = Query(default=None, ge=1, le=14, description="Number of forecast days (optional, returns weather if provided)"),
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Get a field by ID.
    
    If days parameter is provided (1-14), returns complete weather data for the field.
    Otherwise returns field details.
    """
    try:
        service = FarmService(db)
        field = service.get_field(field_id, current_user)
        
        # If days parameter is provided, get weather data
        if days is not None:
            from app.application.weather.service import WeatherService
            weather_service = WeatherService(db_session=db)
            weather_data = weather_service.get_field_weather_data(field_id)
            
            if not weather_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Field {field_id} not found or has no location coordinates for weather"
                )
            
            # Merge field data with weather data
            return {
                "field": {
                    "id": str(field.id),
                    "farm_id": str(field.farm_id),
                    "name": field.name,
                    "area_ha": str(field.area_ha),
                    "boundary_geojson": field.boundary_geojson,
                    "centroid_geojson": field.centroid_geojson,
                    "soil_type": field.soil_type,
                    "soil_classification": field.soil_classification,
                    "elevation_m": str(field.elevation_m) if field.elevation_m else None,
                    "slope_degree": str(field.slope_degree) if field.slope_degree else None,
                    "irrigation_type": field.irrigation_type,
                    "drainage_type": field.drainage_type,
                    "metadata": field.metadata,
                    "created_at": field.created_at.isoformat() if field.created_at else None,
                    "updated_at": field.updated_at.isoformat() if field.updated_at else None,
                },
                "weather": weather_data
            }
        
        # Default: return field details only
        return {
            "id": str(field.id),
            "farm_id": str(field.farm_id),
            "name": field.name,
            "area_ha": str(field.area_ha),
            "boundary_geojson": field.boundary_geojson,
            "centroid_geojson": field.centroid_geojson,
            "soil_type": field.soil_type,
            "soil_classification": field.soil_classification,
            "elevation_m": str(field.elevation_m) if field.elevation_m else None,
            "slope_degree": str(field.slope_degree) if field.slope_degree else None,
            "irrigation_type": field.irrigation_type,
            "drainage_type": field.drainage_type,
            "metadata": field.metadata,
            "created_at": field.created_at.isoformat() if field.created_at else None,
            "updated_at": field.updated_at.isoformat() if field.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/fields/{field_id}", response_model=Dict[str, Any])
async def update_field(
    field_id: str,
    field: FieldUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Update a field.
    """
    try:
        service = FarmService(db)
        updated = service.update_field(field_id, field, current_user)
        
        return {
            "id": str(updated.id),
            "name": updated.name,
            "status": "updated"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/fields/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_field(
    field_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Delete a field (soft delete).
    """
    try:
        service = FarmService(db)
        service.delete_field(field_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ Crop Cycle Routes ============

@router.post(
    "/crop-cycles",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
)
async def create_crop_cycle(
    cycle: CropCycleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Create a new crop cycle.
    """
    try:
        service = FarmService(db)
        created = service.create_crop_cycle(cycle, current_user)
        
        return {
            "id": str(created.id),
            "field_id": str(created.field_id),
            "product_category": created.product_category,
            "crop_name": created.crop_name,
            "variety": created.variety,
            "planting_date": created.planting_date.isoformat() if created.planting_date else None,
            "status": created.status,
            "created_at": created.created_at.isoformat() if created.created_at else None,
            "status": "created"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crop-cycles", response_model=List[Dict[str, Any]])
async def list_crop_cycles(
    field_id: str = Query(..., description="Field ID"),
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    List all crop cycles for a field.
    """
    try:
        service = FarmService(db)
        return service.list_crop_cycles(field_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crop-cycles/{cycle_id}", response_model=Dict[str, Any])
async def get_crop_cycle(
    cycle_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Get a crop cycle by ID.
    """
    try:
        service = FarmService(db)
        cycle = service.get_crop_cycle(cycle_id, current_user)
        
        return {
            "id": str(cycle.id),
            "field_id": str(cycle.field_id),
            "product_category": cycle.product_category,
            "crop_name": cycle.crop_name,
            "variety": cycle.variety,
            "cultivar": cycle.cultivar,
            "planting_date": cycle.planting_date.isoformat() if cycle.planting_date else None,
            "expected_harvest_date": cycle.expected_harvest_date.isoformat() if cycle.expected_harvest_date else None,
            "actual_harvest_date": cycle.actual_harvest_date.isoformat() if cycle.actual_harvest_date else None,
            "status": cycle.status,
            "expected_yield_kg": str(cycle.expected_yield_kg) if cycle.expected_yield_kg else None,
            "actual_yield_kg": str(cycle.actual_yield_kg) if cycle.actual_yield_kg else None,
            "yield_quality_grade": cycle.yield_quality_grade,
            "notes": cycle.notes,
            "created_at": cycle.created_at.isoformat() if cycle.created_at else None,
            "updated_at": cycle.updated_at.isoformat() if cycle.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/crop-cycles/{cycle_id}", response_model=Dict[str, Any])
async def update_crop_cycle(
    cycle_id: str,
    cycle: CropCycleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Update a crop cycle.
    """
    try:
        service = FarmService(db)
        updated = service.update_crop_cycle(cycle_id, cycle, current_user)
        
        return {
            "id": str(updated.id),
            "status": "updated"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ Farm Task Routes ============

@router.post(
    "/tasks",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task: FarmTaskCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Create a new farm task.
    """
    try:
        service = FarmService(db)
        created = service.create_task(task, current_user)
        
        return {
            "id": str(created.id),
            "field_id": str(created.field_id),
            "task_type": created.task_type,
            "title": created.title,
            "status": created.status,
            "priority": created.priority,
            "scheduled_date": created.scheduled_date.isoformat() if created.scheduled_date else None,
            "created_at": created.created_at.isoformat() if created.created_at else None,
            "status": "created"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks", response_model=List[Dict[str, Any]])
async def list_tasks(
    field_id: str = Query(..., description="Field ID"),
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    List all tasks for a field.
    """
    try:
        service = FarmService(db)
        return service.list_tasks(field_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/upcoming", response_model=List[Dict[str, Any]])
async def list_upcoming_tasks(
    field_id: str = Query(..., description="Field ID"),
    days: int = Query(default=7, ge=1, le=90, description="Number of days to look ahead"),
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    List upcoming tasks for a field.
    """
    try:
        service = FarmService(db)
        return service.list_upcoming_tasks(field_id, days, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=Dict[str, Any])
async def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Get a farm task by ID.
    """
    try:
        service = FarmService(db)
        task = service.get_task(task_id, current_user)
        
        return {
            "id": str(task.id),
            "field_id": str(task.field_id),
            "crop_cycle_id": str(task.crop_cycle_id) if task.crop_cycle_id else None,
            "task_type": task.task_type,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "scheduled_date": task.scheduled_date.isoformat() if task.scheduled_date else None,
            "scheduled_time": task.scheduled_time.isoformat() if task.scheduled_time else None,
            "duration_estimate_hours": str(task.duration_estimate_hours) if task.duration_estimate_hours else None,
            "window_start_date": task.window_start_date.isoformat() if task.window_start_date else None,
            "window_end_date": task.window_end_date.isoformat() if task.window_end_date else None,
            "completed_date": task.completed_date.isoformat() if task.completed_date else None,
            "completed_by": task.completed_by,
            "duration_actual_hours": str(task.duration_actual_hours) if task.duration_actual_hours else None,
            "assigned_to": task.assigned_to,
            "estimated_cost_usd": str(task.estimated_cost_usd) if task.estimated_cost_usd else None,
            "actual_cost_usd": str(task.actual_cost_usd) if task.actual_cost_usd else None,
            "weather_dependent": task.weather_dependent,
            "notes": task.notes,
            "completion_notes": task.completion_notes,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/tasks/{task_id}", response_model=Dict[str, Any])
async def update_task(
    task_id: str,
    task: FarmTaskUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Update a farm task.
    """
    try:
        service = FarmService(db)
        updated = service.update_task(task_id, task, current_user)
        
        return {
            "id": str(updated.id),
            "status": "updated"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
