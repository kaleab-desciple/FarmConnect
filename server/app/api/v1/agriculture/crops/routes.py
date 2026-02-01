from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.auth.dependencies import get_current_user, require_roles
from .service import CropCycleService
from .dto import CropCycle, CropCycleCreate, CropCycleUpdate, HarvestRecord

router = APIRouter()

@router.post("/fields/{field_id}/crop-cycles", response_model=CropCycle, status_code=status.HTTP_201_CREATED)
def create_crop_cycle(
    field_id: UUID,
    cycle_data: CropCycleCreate,
    current_user: dict = Depends(require_roles(["FARMER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Create new crop cycle"""
    service = CropCycleService(db)
    
    # Check field exists and user has access
    farmer_id = service.get_field_farmer_id(str(field_id))
    if not farmer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    if farmer_id != user_id and "ADMIN" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create crop cycles for this field"
        )
    
    return service.create_crop_cycle(str(field_id), cycle_data)


@router.get("/fields/{field_id}/crop-cycles", response_model=List[CropCycle])
def list_crop_cycles(
    field_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = Query(None, alias="status")
):
    """List crop cycles for a field"""
    service = CropCycleService(db)
    
    # Check field access
    farmer_id = service.get_field_farmer_id(str(field_id))
    if not farmer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    # Basic access check - farmers can only see their own, others can see all
    if "FARMER" in user_roles and "ADMIN" not in user_roles and "AGRONOMIST" not in user_roles:
        if farmer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view crop cycles for this field"
            )
    
    return service.list_crop_cycles(str(field_id), status_filter)


@router.get("/{cycle_id}", response_model=CropCycle)
def get_crop_cycle(
    cycle_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get crop cycle by ID"""
    service = CropCycleService(db)
    cycle = service.get_crop_cycle(str(cycle_id))
    
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop cycle not found"
        )
    
    # Check access via field
    farmer_id = service.get_field_farmer_id(str(cycle.field_id))
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    if "FARMER" in user_roles and "ADMIN" not in user_roles and "AGRONOMIST" not in user_roles:
        if farmer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this crop cycle"
            )
    
    return cycle


@router.put("/{cycle_id}", response_model=CropCycle)
def update_crop_cycle(
    cycle_id: UUID,
    cycle_data: CropCycleUpdate,
    current_user: dict = Depends(require_roles(["FARMER", "AGRONOMIST", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Update crop cycle"""
    service = CropCycleService(db)
    
    # Check cycle exists
    cycle = service.get_crop_cycle(str(cycle_id))
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop cycle not found"
        )
    
    # Check access
    farmer_id = service.get_field_farmer_id(str(cycle.field_id))
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    if farmer_id != user_id and "ADMIN" not in user_roles and "AGRONOMIST" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this crop cycle"
        )
    
    updated_cycle = service.update_crop_cycle(str(cycle_id), cycle_data)
    return updated_cycle


@router.post("/{cycle_id}/harvest", response_model=CropCycle)
def record_harvest(
    cycle_id: UUID,
    harvest_data: HarvestRecord,
    current_user: dict = Depends(require_roles(["FARMER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Record harvest for crop cycle"""
    service = CropCycleService(db)
    
    # Check cycle exists
    cycle = service.get_crop_cycle(str(cycle_id))
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop cycle not found"
        )
    
    # Check access
    farmer_id = service.get_field_farmer_id(str(cycle.field_id))
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    if farmer_id != user_id and "ADMIN" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to record harvest for this crop cycle"
        )
    
    updated_cycle = service.record_harvest(str(cycle_id), harvest_data)
    return updated_cycle


@router.get("/active", response_model=List[CropCycle])
def list_active_cycles(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all active crop cycles for current user"""
    service = CropCycleService(db)
    
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    if "FARMER" in user_roles and "ADMIN" not in user_roles:
        # Farmers see only their active cycles
        return service.list_active_cycles(farmer_id=user_id)
    else:
        # Others see all active cycles
        return service.list_active_cycles()


@router.delete("/{cycle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_crop_cycle(
    cycle_id: UUID,
    current_user: dict = Depends(require_roles(["FARMER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Soft delete crop cycle"""
    service = CropCycleService(db)
    
    # Check cycle exists
    cycle = service.get_crop_cycle(str(cycle_id))
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop cycle not found"
        )
    
    # Check access
    farmer_id = service.get_field_farmer_id(str(cycle.field_id))
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    if farmer_id != user_id and "ADMIN" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this crop cycle"
        )
    
    result = service.delete_crop_cycle(str(cycle_id))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop cycle not found or already deleted"
        )
