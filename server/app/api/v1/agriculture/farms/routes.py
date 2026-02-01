from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.auth.dependencies import get_current_user, require_roles
from .service import FarmService
from .dto import Farm, FarmCreate, FarmUpdate, Field, FieldCreate, FieldUpdate

router = APIRouter()

@router.post("", response_model=Farm, status_code=status.HTTP_201_CREATED)
def create_farm(
    farm_data: FarmCreate,
    current_user: dict = Depends(require_roles(["FARMER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Create a new farm"""
    service = FarmService(db)
    farmer_id = current_user["sub"]
    return service.create_farm(farmer_id, farm_data)


@router.get("", response_model=List[Farm])
def list_farms(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """List farms"""
    service = FarmService(db)
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    if "FARMER" in user_roles and "ADMIN" not in user_roles:
        # Farmers see only their farms
        return service.list_farms(farmer_id=user_id, skip=skip, limit=limit)
    else:
        # Others see all farms
        return service.list_farms(skip=skip, limit=limit)


@router.get("/{farm_id}", response_model=Farm)
def get_farm(
    farm_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get farm by ID"""
    service = FarmService(db)
    farm = service.get_farm(str(farm_id))
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    # Check access
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    if farm.farmer_id != user_id and "ADMIN" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )
    
    return farm


@router.put("/{farm_id}", response_model=Farm)
def update_farm(
    farm_id: UUID,
    farm_data: FarmUpdate,
    current_user: dict = Depends(require_roles(["FARMER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Update farm"""
    service = FarmService(db)
    
    # Check access first
    farm = service.get_farm(str(farm_id))
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
        
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    if farm.farmer_id != user_id and "ADMIN" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this farm"
        )
    
    updated_farm = service.update_farm(str(farm_id), farm_data)
    return updated_farm


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(
    farm_id: UUID,
    current_user: dict = Depends(require_roles(["FARMER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Delete farm"""
    service = FarmService(db)
    
    # Check access first
    farm = service.get_farm(str(farm_id))
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
        
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    if farm.farmer_id != user_id and "ADMIN" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this farm"
        )
    
    result = service.delete_farm(str(farm_id))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found or already deleted"
        )


# Field Endpoints

@router.post("/{farm_id}/fields", response_model=Field, status_code=status.HTTP_201_CREATED)
def create_field(
    farm_id: UUID,
    field_data: FieldCreate,
    current_user: dict = Depends(require_roles(["FARMER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Create a new field in a farm"""
    service = FarmService(db)
    
    # Check farm exists and user has access
    farm = service.get_farm(str(farm_id))
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    if farm.farmer_id != user_id and "ADMIN" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add fields to this farm"
        )
    
    return service.create_field(str(farm_id), field_data)


@router.get("/{farm_id}/fields", response_model=List[Field])
def list_fields(
    farm_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List fields in a farm"""
    service = FarmService(db)
    
    # Check farm exists and user has access
    farm = service.get_farm(str(farm_id))
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    if farm.farmer_id != user_id and "ADMIN" not in user_roles and "AGRONOMIST" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view fields in this farm"
        )
    
    return service.list_fields(str(farm_id))
