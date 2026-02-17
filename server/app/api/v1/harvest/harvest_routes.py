"""Harvest API routes."""
from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth.dependencies import require_auth
from app.domain.farm.entities import Harvest, HarvestCreate, HarvestUpdate
from app.application.harvest.service import HarvestService

router = APIRouter(prefix="/harvests")

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def record_harvest(
    data: HarvestCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """Record a new harvest event."""
    service = HarvestService(db)
    harvest = service.record_harvest(data, current_user)
    return {
        "id": str(harvest.id),
        "status": "recorded",
        "harvest_date": harvest.harvest_date.isoformat(),
        "quantity": str(harvest.quantity_harvested)
    }

@router.get("/crop-cycle/{cycle_id}", response_model=List[Dict[str, Any]])
async def list_harvests_for_cycle(
    cycle_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """List all harvests for a specific crop cycle."""
    service = HarvestService(db)
    harvests = service.harvest_repo.get_by_crop_cycle_id(cycle_id)
    return [
        {
            "id": str(h.id),
            "harvest_date": h.harvest_date.isoformat(),
            "quantity": str(h.quantity_harvested),
            "unit": h.unit,
            "quality_grade": h.quality_grade
        } for h in harvests
    ]

@router.post("/{harvest_id}/convert-to-product", response_model=Dict[str, Any])
async def convert_to_product(
    harvest_id: UUID,
    product_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """Convert a harvest into a sellable product."""
    service = HarvestService(db)
    product = service.convert_to_product(harvest_id, product_data, current_user)
    return {
        "id": str(product.id),
        "name": product.name,
        "quantity_available": str(product.quantity_available),
        "status": "converted"
    }
