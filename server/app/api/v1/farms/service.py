"""
Farm Service - Business Logic Layer
Farm Connect AgriManagement

Following the same architecture, patterns, and structure as the forum implementation.
"""
from __future__ import annotations
from typing import Optional, List
from datetime import datetime, date, timezone
import logging

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.auth.dependencies import TokenPayload
from shared_models import (
    Farm as FarmDTO,
    FarmCreate as FarmCreateDTO,
    FarmUpdate as FarmUpdateDTO,
    FarmListResponse,
    Field as FieldDTO,
    FieldCreate as FieldCreateDTO,
    FieldUpdate as FieldUpdateDTO,
    FieldListResponse,
    CropCycle as CropCycleDTO,
    CropCycleCreate as CropCycleCreateDTO,
    CropCycleUpdate as CropCycleUpdateDTO,
    CropCycleListResponse,
)
from app.domain.farm.entities import (
    Farm as DomainFarm, 
    FarmCreate as DomainFarmCreate, 
    FarmUpdate as DomainFarmUpdate,
    Field as DomainField, 
    FieldCreate as DomainFieldCreate, 
    FieldUpdate as DomainFieldUpdate,
    CropCycle as DomainCropCycle, 
    CropCycleCreate as DomainCropCycleCreate, 
    CropCycleUpdate as DomainCropCycleUpdate,
)
from app.infrastructure.repositories.farm_repo import (
    FarmRepository, FieldRepository, CropCycleRepository
)

logger = logging.getLogger(__name__)


class FarmService:
    """Service layer for farm operations following clean architecture patterns"""
    
    CROP_CYCLE_STATUSES = ['PLANNED', 'PLANTED', 'GROWING', 'HARVESTED', 'PARTIALLY_HARVESTED', 'FAILED', 'ABANDONED']
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
        from app.core.config import settings
        
        # Handle dev mode when AUTH_ENABLED=false
        if not settings.AUTH_ENABLED:
            # In dev mode, use any existing user for API testing
            logger.warning("AUTH_ENABLED=false - using dev mode fallback")
            
            # Check if this is the mock dev user
            if token_payload.keycloak_id == "dev-user" or token_payload.email == "dev@example.com":
                # If system_user_id is already set (dev mock does this), use it
                if token_payload.system_user_id:
                    return token_payload.system_user_id
                    
                # Try to find any existing user to use as fallback
                all_users = self.user_repo.list_all()
                if all_users:
                    logger.info(f"Using user {all_users[0].id} for dev mode")
                    return all_users[0].id
                else:
                    raise HTTPException(
                        status_code=401,
                        detail="No users found in database. Please provision a user first."
                    )
        
        # If system_user_id is already populated, return it immediately
        if token_payload.system_user_id:
            return token_payload.system_user_id
            
        user = None
        keycloak_id = token_payload.keycloak_id
        
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
        farm_data: FarmCreateDTO,
        current_user: TokenPayload
    ) -> FarmDTO:
        """
        Create a new farm.
        
        Args:
            farm_data: Farm creation data (DTO)
            current_user: Authenticated user (must be the farmer)
            
        Returns:
            Created farm (DTO)
            
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
        
        # Convert DTO to domain entity for repository
        domain_farm_data = DomainFarmCreate(
            farmer_id=farm_data.farmer_id,
            name=farm_data.name,
            location_lat=farm_data.location_lat,
            location_lng=farm_data.location_lng,
            location_address=farm_data.location_address,
            total_area_ha=farm_data.total_area_ha,
            boundary_geojson=farm_data.boundary_geojson,
            centroid_geojson=farm_data.centroid_geojson,
            metadata=farm_data.metadata,
        )
        
        # Create farm (repository returns domain entity)
        created_domain = self.farm_repo.create(domain_farm_data)
        
        # Convert domain entity to DTO for response
        from app.infrastructure.db.mappers import domain_to_dto
        created_dto = domain_to_dto(created_domain)
        
        logger.info(f"Created farm: {created_domain.id} for farmer: {farm_data.farmer_id}")
        
        return created_dto
    
    def get_farm(
        self,
        farm_id: str,
        current_user: TokenPayload
    ) -> FarmDTO:
        """
        Get a farm by ID with ownership check.
        
        Args:
            farm_id: Farm ID
            current_user: Authenticated user
            
        Returns:
            Farm (DTO)
            
        Raises:
            HTTPException: Farm not found or unauthorized
        """
        farm = self.farm_repo.get_by_id(farm_id)
        
        if not farm:
            raise HTTPException(status_code=404, detail="Farm not found")
        
        # Check access
        if not self._can_access_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Convert domain entity to DTO for response
        from app.infrastructure.db.mappers import domain_to_dto
        return domain_to_dto(farm)
    
    def list_farms(
        self,
        farmer_id: Optional[str] = None,
        current_user: Optional[TokenPayload] = None,
        page: int = 1,
        page_size: int = 20
    ) -> FarmListResponse:
        """
        List farms with filtering and pagination.
        
        Args:
            farmer_id: Filter by farmer
            current_user: Authenticated user
            page: Page number
            page_size: Items per page
            
        Returns:
            Paginated farm list (DTO)
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
            
            # If admin/manager/analyst/agent, can see all farms or specific farmer's farms
            if farmer_id and not (
                current_user.has_realm_role("ADMIN") or 
                current_user.has_realm_role("MANAGER") or 
                current_user.has_realm_role("FIELD_ANALYST") or
                current_user.has_realm_role("AGENT") or
                current_user.has_realm_role("AGRONOMIST")
            ):
                # Regular users can only see their own farms
                if farmer_id != internal_user_id:
                    raise HTTPException(status_code=403, detail="Access denied")
            
            # For regular users, default to their own farms
            if not farmer_id and not (
                current_user.has_realm_role("ADMIN") or 
                current_user.has_realm_role("MANAGER") or 
                current_user.has_realm_role("FIELD_ANALYST") or
                current_user.has_realm_role("AGENT") or
                current_user.has_realm_role("AGRONOMIST") or
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
        
        # Convert domain entities to DTOs
        from app.infrastructure.db.mappers import domain_to_dto
        farms_dto = [domain_to_dto(f) for f in paginated_farms]
        
        return FarmListResponse(
            items=farms_dto,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    def update_farm(
        self,
        farm_id: str,
        farm_data: FarmUpdateDTO,
        current_user: TokenPayload
    ) -> FarmDTO:
        """
        Update a farm with ownership check.
        
        Args:
            farm_id: Farm ID
            farm_data: Update data (DTO)
            current_user: Authenticated user
            
        Returns:
            Updated farm (DTO)
            
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
        
        # Convert DTO to domain entity for repository
        domain_farm_data = DomainFarmUpdate(
            name=farm_data.name,
            location_lat=farm_data.location_lat,
            location_lng=farm_data.location_lng,
            location_address=farm_data.location_address,
            total_area_ha=farm_data.total_area_ha,
            boundary_geojson=farm_data.boundary_geojson,
            centroid_geojson=farm_data.centroid_geojson,
            metadata=farm_data.metadata,
        )
        
        updated_domain = self.farm_repo.update(farm_id, domain_farm_data)
        
        # Convert domain entity to DTO for response
        from app.infrastructure.db.mappers import domain_to_dto
        updated_dto = domain_to_dto(updated_domain)
        
        logger.info(f"Updated farm: {farm_id}")
        
        return updated_dto
    
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
        
        # Admin/manager/analyst/service can access
        if (current_user.has_realm_role("ADMIN") or 
            current_user.has_realm_role("MANAGER") or 
            current_user.has_realm_role("FIELD_ANALYST") or
            current_user.is_service_account):
            return True

        # Agent/Agronomist can access
        if (current_user.has_realm_role("AGENT") or 
            current_user.has_realm_role("AGRONOMIST")):
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
            
        # Agent/Agronomist can edit
        if (current_user.has_realm_role("AGENT") or 
            current_user.has_realm_role("AGRONOMIST")):
            return True
            
        # Owner can edit
        internal_user_id = self._get_internal_user_id(current_user)
        if farm.farmer_id == internal_user_id:
            return True
        
        return False
    
    # ============ Field Operations ============
    
    def create_field(
        self,
        field_data: FieldCreateDTO,
        current_user: TokenPayload
    ) -> FieldDTO:
        """Create a new field in a farm (returns DTO)"""
        # Verify farm exists and user has access
        farm = self.farm_repo.get_by_id(str(field_data.farm_id))
        if not farm:
            raise HTTPException(status_code=404, detail="Farm not found")
        
        if not self._can_access_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Convert DTO to domain entity for repository
        domain_field_data = DomainFieldCreate(
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
            metadata=field_data.metadata,
        )
        
        created_domain = self.field_repo.create(domain_field_data)
        
        # Convert domain entity to DTO for response
        from app.infrastructure.db.mappers import domain_to_dto
        created_dto = domain_to_dto(created_domain)
        
        logger.info(f"Created field: {created_domain.id} in farm: {field_data.farm_id}")
        
        return created_dto
    
    def get_field(
        self,
        field_id: str,
        current_user: TokenPayload
    ) -> FieldDTO:
        """Get a field by ID (returns DTO)"""
        field = self.field_repo.get_by_id(field_id)
        
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        # Verify farm access
        farm = self.farm_repo.get_by_id(str(field.farm_id))
        if not farm or not self._can_access_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Convert domain entity to DTO for response
        from app.infrastructure.db.mappers import domain_to_dto
        return domain_to_dto(field)
    
    def list_fields(
        self,
        current_user: TokenPayload,
        farm_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> FieldListResponse:
        """List fields for a farm or for all farmer's farms if farm_id is None."""
        if farm_id:
            farm = self.farm_repo.get_by_id(farm_id)
            if not farm:
                raise HTTPException(status_code=404, detail="Farm not found")
            
            if not self._can_access_farm(farm, current_user):
                raise HTTPException(status_code=403, detail="Access denied")
            
            fields = self.field_repo.get_by_farm_id(farm_id)
        else:
            # Fetch all fields for all farms owned by this farmer
            # Note: current_user.system_user_id is the farmer_id
            fields = self.field_repo.get_by_farmer_id(current_user.system_user_id)
        
        # Apply pagination
        total = len(fields)
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        start = (page - 1) * page_size
        paginated = fields[start:start + page_size]
        
        # Convert domain entities to DTOs
        from app.infrastructure.db.mappers import domain_to_dto
        items = [domain_to_dto(f) for f in paginated]
        
        return FieldListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    def update_field(
        self,
        field_id: str,
        field_data: FieldUpdateDTO,
        current_user: TokenPayload
    ) -> FieldDTO:
        """Update a field (returns DTO)"""
        field = self.field_repo.get_by_id(field_id)
        
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        # Verify farm access
        farm = self.farm_repo.get_by_id(str(field.farm_id))
        if not farm or not self._can_edit_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Convert DTO to domain entity for repository
        domain_field_data = DomainFieldUpdate(
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
            metadata=field_data.metadata,
        )
        
        updated_domain = self.field_repo.update(field_id, domain_field_data)
        
        # Convert domain entity to DTO for response
        from app.infrastructure.db.mappers import domain_to_dto
        return domain_to_dto(updated_domain)
    
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
    
    def get_field_status_map(
        self,
        farm_id: str,
        current_user: TokenPayload
    ) -> dict:
        """
        Get field status map for a farm with GeoJSON boundaries and active crop cycles.
        
        Returns GeoJSON boundaries of all fields for a farm, alongside the currently
        active CropCycle mapped to each field (crop type and current growth stage),
        so frontend can color-code the map.
        
        Args:
            farm_id: Farm ID
            current_user: Authenticated user
            
        Returns:
            Dictionary with fields and their active crop cycle info
            
        Raises:
            HTTPException: Farm not found or unauthorized
        """
        # Check farm exists and access
        farm = self.farm_repo.get_by_id(farm_id)
        if not farm:
            raise HTTPException(status_code=404, detail="Farm not found")
        
        if not self._can_access_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all fields for the farm
        fields = self.field_repo.get_by_farm_id(farm_id)
        
        # Active crop cycle statuses
        active_statuses = ['PLANTED', 'GROWING']
        
        result = {
            "farm_id": farm_id,
            "farm_name": farm.name,
            "fields": []
        }
        
        for field in fields:
            # Get active crop cycle for this field (most recent one with active status)
            crop_cycles = self.crop_cycle_repo.get_by_field_id(str(field.id))
            active_cycle = None
            
            # Find the most recent active crop cycle
            for cycle in crop_cycles:
                if cycle.status in active_statuses:
                    if active_cycle is None or cycle.created_at > active_cycle.created_at:
                        active_cycle = cycle
            
            field_info = {
                "field_id": str(field.id),
                "field_name": field.name,
                "area_ha": str(field.area_ha) if field.area_ha else None,
                "boundary_geojson": field.boundary_geojson,
                "centroid_geojson": field.centroid_geojson,
                "irrigation_type": field.irrigation_type,
                "soil_type": field.soil_type,
                "active_crop_cycle": None
            }
            
            if active_cycle:
                field_info["active_crop_cycle"] = {
                    "crop_cycle_id": str(active_cycle.id),
                    "crop_name": active_cycle.crop_name,
                    "product_category": active_cycle.product_category,
                    "variety": active_cycle.variety,
                    "status": active_cycle.status,
                    "planting_date": active_cycle.planting_date.isoformat() if active_cycle.planting_date else None,
                    "expected_harvest_date": active_cycle.expected_harvest_date.isoformat() if active_cycle.expected_harvest_date else None,
                    "expected_yield_kg": str(active_cycle.expected_yield_kg) if active_cycle.expected_yield_kg else None,
                }
            
            result["fields"].append(field_info)
        
        return result

    
    # ============ Crop Cycle Operations ============
    
    def create_crop_cycle(
        self,
        cycle_data: CropCycleCreateDTO,
        current_user: TokenPayload
    ) -> CropCycleDTO:
        """Create a new crop cycle (returns DTO)"""
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
        
        # Convert DTO to domain entity for repository
        domain_cycle_data = DomainCropCycleCreate(
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
            metadata=cycle_data.metadata,
        )
        
        created_domain = self.crop_cycle_repo.create(domain_cycle_data)
        
        # Convert domain entity to DTO for response
        from app.infrastructure.db.mappers import domain_to_dto
        created_dto = domain_to_dto(created_domain)
        
        logger.info(f"Created crop cycle: {created_domain.id} for field: {cycle_data.field_id}")
        
        return created_dto
    
    def get_crop_cycle(
        self,
        cycle_id: str,
        current_user: TokenPayload
    ) -> CropCycleDTO:
        """Get a crop cycle by ID (returns DTO)"""
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
        
        # Convert domain entity to DTO for response
        from app.infrastructure.db.mappers import domain_to_dto
        return domain_to_dto(cycle)
    
    def list_crop_cycles(
        self,
        field_id: str,
        current_user: TokenPayload,
        page: int = 1,
        page_size: int = 20
    ) -> CropCycleListResponse:
        """List crop cycles for a field with pagination (returns CropCycleListResponse)"""
        field = self.field_repo.get_by_id(field_id)
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        farm = self.farm_repo.get_by_id(str(field.farm_id))
        if not farm or not self._can_access_farm(farm, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        cycles = self.crop_cycle_repo.get_by_field_id(field_id)
        
        # Apply pagination
        total = len(cycles)
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        start = (page - 1) * page_size
        paginated = cycles[start:start + page_size]
        
        # Convert domain entities to DTOs
        from app.infrastructure.db.mappers import domain_to_dto
        items = [domain_to_dto(c) for c in paginated]
        
        return CropCycleListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    def update_crop_cycle(
        self,
        cycle_id: str,
        cycle_data: CropCycleUpdateDTO,
        current_user: TokenPayload
    ) -> CropCycleDTO:
        """Update a crop cycle (returns DTO)"""
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
        
        # Convert DTO to domain entity for repository
        domain_cycle_data = DomainCropCycleUpdate(
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
            metadata=cycle_data.metadata,
        )
        
        updated_domain = self.crop_cycle_repo.update(cycle_id, domain_cycle_data)
        
        # Convert domain entity to DTO for response
        from app.infrastructure.db.mappers import domain_to_dto
        return domain_to_dto(updated_domain)
    
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