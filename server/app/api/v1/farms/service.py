"""
Farm Service - Business Logic Layer
Farm Connect AgriManagement

Following the same architecture, patterns, and structure as the forum implementation.
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, timezone
from decimal import Decimal
from uuid import UUID
import logging

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.auth.dependencies import TokenPayload
from shared_models import (
    Farm as FarmDTO,
    FarmCreate as FarmCreateDTO,
    FarmUpdate as FarmUpdateDTO,
    Field as FieldDTO,
    FieldCreate as FieldCreateDTO,
    FieldUpdate as FieldUpdateDTO,
    CropCycle as CropCycleDTO,
    CropCycleCreate as CropCycleCreateDTO,
    CropCycleUpdate as CropCycleUpdateDTO,
)
from app.domain.farm.entities import (
    Farm, FarmCreate, FarmUpdate,
    Field, FieldCreate, FieldUpdate,
    CropCycle, CropCycleCreate, CropCycleUpdate,
)
from app.infrastructure.repositories.farm_repo import (
    FarmRepository, FieldRepository, CropCycleRepository
)

logger = logging.getLogger(__name__)


class FarmService:
    """Service layer for farm operations following clean architecture patterns"""
    
    CROP_CYCLE_STATUSES = ['PLANNED', 'PLANTED', 'GROWING', 'HARVESTED', 'FAILED', 'ABANDONED']
    TASK_STATUSES = ['PENDING', 'SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED', 'CANCELLED', 'OVERDUE']
    TASK_PRIORITIES = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']
    TASK_TYPES = ['LAND_PREPARATION', 'SOWING', 'PLANTING', 'IRRIGATION', 'FERTILIZATION',
                 'WEEDING', 'PEST_CONTROL', 'DISEASE_CONTROL', 'PRUNING', 'THINNING',
                 'HARVESTING', 'POST_HARVEST', 'INSPECTION', 'MAINTENANCE', 'OTHER']
    
    def __init__(self, session: Session):
        self.session = session
        self.farm_repo = FarmRepository(session)
        self.field_repo = FieldRepository(session)
        self.crop_cycle_repo = CropCycleRepository(session)
        from app.infrastructure.repositories.user_repo import UserRepository
        self.user_repo = UserRepository(session)

    def _get_internal_user_id(self, token_payload: TokenPayload) -> str:
        """Resolve internal user ID from Keycloak ID in token"""
        user = None
        keycloak_id = token_payload.user_id
        
        if keycloak_id:
            user = self.user_repo.get_by_keycloak_id(keycloak_id)
            
        # Fallback: Try email if user not found by ID (e.g. missing sub claim)
        if not user and token_payload.email:
             user = self.user_repo.get_by_email(token_payload.email)
        
        if not user:
            logger.warning(f"User not found for Keycloak ID: {keycloak_id} or Email: {token_payload.email}")
            raise HTTPException(
                status_code=401,
                detail="User account not found. Please ensure you are registered."
            )
        
        return user.id
    
    # ============ Farm Operations ============
    
    def create_farm(
        self,
        farm_data: FarmCreate,
        current_user: TokenPayload
    ) -> Farm:
        """
        Create a new farm.
        
        Args:
            farm_data: Farm creation data
            current_user: Authenticated user (must be the farmer)
            
        Returns:
            Created farm
            
        Raises:
            HTTPException: Validation errors or unauthorized
        """
        # Resolve internal user ID
        internal_user_id = None
        if not current_user.is_service_account:
            internal_user_id = self._get_internal_user_id(current_user)

        # Verify user is the farmer
        if farm_data.farmer_id != internal_user_id:
            # Check if user has permission to create farms for others
            if not (current_user.has_realm_role("ADMIN") or 
                    current_user.has_realm_role("AGENT") or 
                    current_user.is_service_account):
                raise HTTPException(
                    status_code=403,
                    detail="You can only create farms for yourself"
                )
        
        # Validate coordinates
        if not (-90 <= float(farm_data.location_lat) <= 90):
            raise HTTPException(
                status_code=400,
                detail="Latitude must be between -90 and 90"
            )
        
        if not (-180 <= float(farm_data.location_lng) <= 180):
            raise HTTPException(
                status_code=400,
                detail="Longitude must be between -180 and 180"
            )
        
        # Create farm
        created = self.farm_repo.create(farm_data)
        
        logger.info(f"Created farm: {created.id} for farmer: {farm_data.farmer_id}")
        
        return created
    
    def get_farm(
        self,
        farm_id: str,
        current_user: TokenPayload
    ) -> Farm:
        """
        Get a farm by ID with ownership check.
        
        Args:
            farm_id: Farm ID
            current_user: Authenticated user
            
        Returns:
            Farm
            
        Raises:
            HTTPException: Farm not found or unauthorized
        """
        farm = self.farm_repo.get_by_id(farm_id)
        
        if not farm:
            raise HTTPException(status_code=404, detail="Farm not found")
        
        # Check access
        if not self._can_access_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return farm
    
    def list_farms(
        self,
        farmer_id: Optional[str] = None,
        current_user: Optional[TokenPayload] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        List farms with filtering and pagination.
        
        Args:
            farmer_id: Filter by farmer
            current_user: Authenticated user
            page: Page number
            page_size: Items per page
            
        Returns:
            Paginated farm list
        """
        # If user is provided, filter by their farms or allow access based on role
        if current_user:
            # Resolve internal ID if not skipping check
            internal_user_id = None
            if not current_user.is_service_account:
                try:
                    internal_user_id = self._get_internal_user_id(current_user)
                except HTTPException:
                    # If user not in DB, they can only see farms if they are Admin/Agent
                    if not (current_user.has_realm_role("ADMIN") or current_user.has_realm_role("AGENT")):
                        raise
            
            # If admin/agent, can see all farms or specific farmer's farms
            if farmer_id and not (
                current_user.has_realm_role("ADMIN") or 
                current_user.has_realm_role("AGENT")
            ):
                # Regular users can only see their own farms
                if farmer_id != internal_user_id:
                    raise HTTPException(status_code=403, detail="Access denied")
            
            # For regular users, default to their own farms
            if not farmer_id and not (
                current_user.has_realm_role("ADMIN") or 
                current_user.has_realm_role("AGENT") or
                current_user.is_service_account
            ):
                farmer_id = internal_user_id
        
        farms = self.farm_repo.get_by_farmer_id(farmer_id) if farmer_id else []
        
        # Apply pagination
        total = len(farms)
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        start = (page - 1) * page_size
        end = start + page_size
        paginated_farms = farms[start:end]
        
        return {
            "farms": [self._farm_to_response(f) for f in paginated_farms],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    def update_farm(
        self,
        farm_id: str,
        farm_data: FarmUpdate,
        current_user: TokenPayload
    ) -> Farm:
        """
        Update a farm with ownership check.
        
        Args:
            farm_id: Farm ID
            farm_data: Update data
            current_user: Authenticated user
            
        Returns:
            Updated farm
            
        Raises:
            HTTPException: Farm not found or unauthorized
        """
        # Check farm exists and access
        farm = self.farm_repo.get_by_id(farm_id)
        if not farm:
            raise HTTPException(status_code=404, detail="Farm not found")
        
        if not self._can_edit_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate coordinates if provided
        if farm_data.location_lat is not None:
            if not (-90 <= float(farm_data.location_lat) <= 90):
                raise HTTPException(
                    status_code=400,
                    detail="Latitude must be between -90 and 90"
                )
        
        if farm_data.location_lng is not None:
            if not (-180 <= float(farm_data.location_lng) <= 180):
                raise HTTPException(
                    status_code=400,
                    detail="Longitude must be between -180 and 180"
                )
        
        updated = self.farm_repo.update(farm_id, farm_data)
        
        logger.info(f"Updated farm: {farm_id}")
        
        return updated
    
    def delete_farm(
        self,
        farm_id: str,
        current_user: TokenPayload
    ) -> bool:
        """
        Delete a farm with ownership check.
        
        Args:
            farm_id: Farm ID
            current_user: Authenticated user
            
        Returns:
            True if deleted
            
        Raises:
            HTTPException: Farm not found or unauthorized
        """
        # Check farm exists and access
        farm = self.farm_repo.get_by_id(farm_id)
        if not farm:
            raise HTTPException(status_code=404, detail="Farm not found")
        
        if not self._can_edit_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = self.farm_repo.delete(farm_id)
        
        logger.info(f"Deleted farm: {farm_id}")
        
        return success
    
    def _can_access_farm(self, farm: Farm, current_user: TokenPayload) -> bool:
        """Check if user can access the farm"""
        if not current_user:
            return False
        
        # Admin/agent/service can access
        if (current_user.has_realm_role("ADMIN") or 
            current_user.has_realm_role("AGENT") or
            current_user.is_service_account):
            return True
            
        # Owner can access
        internal_user_id = self._get_internal_user_id(current_user)
        if farm.farmer_id == internal_user_id:
            return True
        
        return False
    
    def _can_edit_farm(self, farm: Farm, current_user: TokenPayload) -> bool:
        """Check if user can edit the farm"""
        if not current_user:
            return False
        
        # Admin/service can edit
        if (current_user.has_realm_role("ADMIN") or 
            current_user.is_service_account):
            return True
            
        # Owner can edit
        internal_user_id = self._get_internal_user_id(current_user)
        if farm.farmer_id == internal_user_id:
            return True
        
        return False
    
    def _farm_to_response(self, farm: Farm) -> Dict[str, Any]:
        """Convert farm to response dict"""
        return {
            "id": str(farm.id),
            "farmer_id": farm.farmer_id,
            "name": farm.name,
            "location_lat": str(farm.location_lat) if farm.location_lat else None,
            "location_lng": str(farm.location_lng) if farm.location_lng else None,
            "location_address": farm.location_address,
            "total_area_ha": str(farm.total_area_ha) if farm.total_area_ha else None,
            "boundary_geojson": farm.boundary_geojson,
            "created_at": farm.created_at.isoformat() if farm.created_at else None,
            "updated_at": farm.updated_at.isoformat() if farm.updated_at else None,
        }
    
    # ============ Field Operations ============
    
    def create_field(
        self,
        field_data: FieldCreate,
        current_user: TokenPayload
    ) -> Field:
        """Create a new field in a farm"""
        # Verify farm exists and user has access
        farm = self.farm_repo.get_by_id(str(field_data.farm_id))
        if not farm:
            raise HTTPException(status_code=404, detail="Farm not found")
        
        if not self._can_access_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        created = self.field_repo.create(field_data)
        
        logger.info(f"Created field: {created.id} in farm: {field_data.farm_id}")
        
        return created
    
    def get_field(
        self,
        field_id: str,
        current_user: TokenPayload
    ) -> Field:
        """Get a field by ID"""
        field = self.field_repo.get_by_id(field_id)
        
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        # Verify farm access
        farm = self.farm_repo.get_by_id(str(field.farm_id))
        if not farm or not self._can_access_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return field
    
    def list_fields(
        self,
        farm_id: str,
        current_user: TokenPayload
    ) -> List[Dict[str, Any]]:
        """List fields for a farm"""
        farm = self.farm_repo.get_by_id(farm_id)
        if not farm:
            raise HTTPException(status_code=404, detail="Farm not found")
        
        if not self._can_access_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        fields = self.field_repo.get_by_farm_id(farm_id)
        
        return [
            {
                "id": str(f.id),
                "farm_id": str(f.farm_id),
                "name": f.name,
                "area_ha": str(f.area_ha),
                "soil_type": f.soil_type,
                "irrigation_type": f.irrigation_type,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in fields
        ]
    
    def update_field(
        self,
        field_id: str,
        field_data: FieldUpdate,
        current_user: TokenPayload
    ) -> Field:
        """Update a field"""
        field = self.field_repo.get_by_id(field_id)
        
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        # Verify farm access
        farm = self.farm_repo.get_by_id(str(field.farm_id))
        if not farm or not self._can_edit_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return self.field_repo.update(field_id, field_data)
    
    def delete_field(
        self,
        field_id: str,
        current_user: TokenPayload
    ) -> bool:
        """Delete a field"""
        field = self.field_repo.get_by_id(field_id)
        
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        # Verify farm access
        farm = self.farm_repo.get_by_id(str(field.farm_id))
        if not farm or not self._can_edit_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return self.field_repo.delete(field_id)
    
    # ============ Crop Cycle Operations ============
    
    def create_crop_cycle(
        self,
        cycle_data: CropCycleCreate,
        current_user: TokenPayload
    ) -> CropCycle:
        """Create a new crop cycle"""
        # Verify field exists and user has access
        field = self.field_repo.get_by_id(str(cycle_data.field_id))
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        farm = self.farm_repo.get_by_id(str(field.farm_id))
        if not farm or not self._can_access_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate status
        if cycle_data.status and cycle_data.status not in self.CROP_CYCLE_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(self.CROP_CYCLE_STATUSES)}"
            )
        
        created = self.crop_cycle_repo.create(cycle_data)
        
        logger.info(f"Created crop cycle: {created.id} for field: {cycle_data.field_id}")
        
        return created
    
    def get_crop_cycle(
        self,
        cycle_id: str,
        current_user: TokenPayload
    ) -> CropCycle:
        """Get a crop cycle by ID"""
        cycle = self.crop_cycle_repo.get_by_id(cycle_id)
        
        if not cycle:
            raise HTTPException(status_code=404, detail="Crop cycle not found")
        
        # Verify field/farm access
        field = self.field_repo.get_by_id(str(cycle.field_id))
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        farm = self.farm_repo.get_by_id(str(field.farm_id))
        if not farm or not self._can_access_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return cycle
    
    def list_crop_cycles(
        self,
        field_id: str,
        current_user: TokenPayload
    ) -> List[Dict[str, Any]]:
        """List crop cycles for a field"""
        field = self.field_repo.get_by_id(field_id)
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        farm = self.farm_repo.get_by_id(str(field.farm_id))
        if not farm or not self._can_access_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        cycles = self.crop_cycle_repo.get_by_field_id(field_id)
        
        return [
            {
                "id": str(c.id),
                "field_id": str(c.field_id),
                "product_category": c.product_category,
                "crop_name": c.crop_name,
                "variety": c.variety,
                "planting_date": c.planting_date.isoformat() if c.planting_date else None,
                "expected_harvest_date": c.expected_harvest_date.isoformat() if c.expected_harvest_date else None,
                "status": c.status,
                "expected_yield_kg": str(c.expected_yield_kg) if c.expected_yield_kg else None,
            }
            for c in cycles
        ]
    
    def update_crop_cycle(
        self,
        cycle_id: str,
        cycle_data: CropCycleUpdate,
        current_user: TokenPayload
    ) -> CropCycle:
        """Update a crop cycle"""
        cycle = self.crop_cycle_repo.get_by_id(cycle_id)
        
        if not cycle:
            raise HTTPException(status_code=404, detail="Crop cycle not found")
        
        # Verify field/farm access
        field = self.field_repo.get_by_id(str(cycle.field_id))
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        farm = self.farm_repo.get_by_id(str(field.farm_id))
        if not farm or not self._can_edit_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate status if provided
        if cycle_data.status and cycle_data.status not in self.CROP_CYCLE_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(self.CROP_CYCLE_STATUSES)}"
            )
        
        return self.crop_cycle_repo.update(cycle_id, cycle_data)
    
"""    # ============ Farm Task Operations ============
    
    def create_task(
        self,
        task_data: FarmTaskCreate,
        current_user: TokenPayload
    ) -> FarmTask:
        # Create a new farm task
        # Verify field exists and user has access
        field = self.field_repo.get_by_id(str(task_data.field_id))
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        farm = self.farm_repo.get_by_id(str(field.farm_id))
        if not farm or not self._can_access_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate task type
        if task_data.task_type not in self.TASK_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid task type. Must be one of: {', '.join(self.TASK_TYPES)}"
            )
        
        # Validate status
        if task_data.status and task_data.status not in self.TASK_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(self.TASK_STATUSES)}"
            )
        
        created = self.task_repo.create(task_data)
        
        logger.info(f"Created task: {created.id} for field: {task_data.field_id}")
        
        return created
    
    def get_task(
        self,
        task_id: str,
        current_user: TokenPayload
    ) -> FarmTask:
        # Get a farm task by ID
        task = self.task_repo.get_by_id(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Verify field/farm access
        field = self.field_repo.get_by_id(str(task.field_id))
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        farm = self.farm_repo.get_by_id(str(field.farm_id))
        if not farm or not self._can_access_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return task
    
    def list_tasks(
        self,
        field_id: str,
        current_user: TokenPayload
    ) -> List[Dict[str, Any]]:
        # List tasks for a field
        field = self.field_repo.get_by_id(field_id)
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        farm = self.farm_repo.get_by_id(str(field.farm_id))
        if not farm or not self._can_access_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        tasks = self.task_repo.get_by_field_id(field_id)
        
        return [
            {
                "id": str(t.id),
                "field_id": str(t.field_id),
                "task_type": t.task_type,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "scheduled_date": t.scheduled_date.isoformat() if t.scheduled_date else None,
            }
            for t in tasks
        ]
    
    def list_upcoming_tasks(
        self,
        field_id: str,
        current_user: TokenPayload,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        # List upcoming tasks for a field
        field = self.field_repo.get_by_id(field_id)
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        farm = self.farm_repo.get_by_id(str(field.farm_id))
        if not farm or not self._can_access_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        tasks = self.task_repo.get_upcoming(field_id, days)
        
        return [
            {
                "id": str(t.id),
                "field_id": str(t.field_id),
                "task_type": t.task_type,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "scheduled_date": t.scheduled_date.isoformat() if t.scheduled_date else None,
            }
            for t in tasks
        ]
    
    def update_task(
        self,
        task_id: str,
        task_data: FarmTaskUpdate,
        current_user: TokenPayload
    ) -> FarmTask:
        # Update a farm task
        task = self.task_repo.get_by_id(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Verify field/farm access
        field = self.field_repo.get_by_id(str(task.field_id))
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        farm = self.farm_repo.get_by_id(str(field.farm_id))
        if not farm or not self._can_edit_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate status if provided
        if task_data.status and task_data.status not in self.TASK_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(self.TASK_STATUSES)}"
            )
        
        return self.task_repo.update(task_id, task_data)
"""