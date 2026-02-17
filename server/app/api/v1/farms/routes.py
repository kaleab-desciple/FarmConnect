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
    
    Creates a new farm entity with location, area, and ownership information.
    Regular users can create farms for themselves, while agents and admins
    can create farms on behalf of farmers.
    
    ## Request Body
    - **farmer_id**: UUID of the farmer who owns this farm (required)
    - **name**: Farm name (required)
    - **location_lat**: Latitude coordinate (optional)
    - **location_lng**: Longitude coordinate (optional)
    - **location_address**: Human-readable address (optional)
    - **total_area_ha**: Total farm area in hectares (optional)
    - **boundary_geojson**: GeoJSON polygon defining farm boundaries (optional)
    - **metadata**: Additional farm metadata as JSON (optional)
    
    ## Authentication
    Requires authentication. Permission checks:
    - Regular users can only create farms for themselves
    - Agents/admins can create farms for any farmer
    
    ## Responses
    - **201**: Farm created successfully
    - **400**: Invalid request data
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (insufficient permissions)
    - **500**: Internal server error
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
    
    Retrieves a paginated list of farms with optional filtering by farmer.
    Results depend on user role and permissions.
    
    ## Query Parameters
    - **farmer_id**: Filter farms by farmer UUID (optional)
      - Regular users: automatically filtered to their own farms
      - Agents/admins: can query any farmer's farms
    - **page**: Page number for pagination (default: 1, min: 1)
    - **page_size**: Number of items per page (default: 20, min: 1, max: 100)
    
    ## Authentication
    Optional authentication. Without authentication, returns public farms only.
    With authentication, applies row-level permissions:
    - Regular users: see only their own farms
    - Agents: see farms in their region
    - Admins: see all farms
    
    ## Response Format
    Returns paginated results with metadata:
    ```json
    {
      "farms": [...],
      "total": 42,
      "page": 1,
      "page_size": 20,
      "total_pages": 3
    }
    ```
    
    ## Responses
    - **200**: Successfully retrieved farms list
    - **400**: Invalid query parameters
    - **500**: Internal server error
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
    Get detailed information about a specific farm.
    
    Retrieves complete farm details including location, area, boundaries,
    and metadata. Access is restricted based on ownership and user role.
    
    ## Path Parameters
    - **farm_id**: UUID of the farm to retrieve (required)
    
    ## Authentication
    Requires authentication. Authorization rules:
    - Farm owner: full access to their own farm
    - Agents: access to farms in their region
    - Admins: access to all farms
    - Other users: access denied
    
    ## Response Fields
    - **id**: Farm UUID
    - **farmer_id**: Owner's user UUID
    - **name**: Farm name
    - **location_lat/lng**: GPS coordinates
    - **location_address**: Human-readable address
    - **total_area_ha**: Total area in hectares
    - **boundary_geojson**: Farm boundary polygon
    - **centroid_geojson**: Farm center point
    - **metadata**: Additional farm data
    - **created_at/updated_at**: Timestamps
    
    ## Responses
    - **200**: Farm details retrieved successfully
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (insufficient permissions)
    - **404**: Farm not found
    - **500**: Internal server error
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
    Update an existing farm's information.
    
    Allows modification of farm details including name, location, area,
    and boundaries. Only authorized users can perform updates.
    
    ## Path Parameters
    - **farm_id**: UUID of the farm to update (required)
    
    ## Request Body
    All fields are optional (partial update supported):
    - **name**: New farm name
    - **location_lat/lng**: Updated GPS coordinates
    - **location_address**: Updated address
    - **total_area_ha**: Updated total area
    - **boundary_geojson**: Updated farm boundaries
    - **metadata**: Updated metadata
    
    ## Authentication
    Requires authentication. Authorization rules:
    - Farm owner: can update their own farm
    - Admins: can update any farm
    - Other users: update denied
    
    ## Responses
    - **200**: Farm updated successfully
    - **400**: Invalid update data
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (insufficient permissions)
    - **404**: Farm not found
    - **500**: Internal server error
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
    
    Performs a soft deletion of the farm, marking it as deleted without
    removing it from the database. Associated fields and crop cycles are
    also soft-deleted.
    
    ## Path Parameters
    - **farm_id**: UUID of the farm to delete (required)
    
    ## Authentication
    Requires authentication. Authorization rules:
    - Farm owner: can delete their own farm
    - Admins: can delete any farm
    - Other users: delete denied
    
    ## Important Notes
    - This is a soft delete; data is retained with a deleted flag
    - Associated fields and crop cycles are also soft-deleted
    - Deletion can potentially be reversed by an administrator
    
    ## Responses
    - **204**: Farm deleted successfully (no content)
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (insufficient permissions)
    - **404**: Farm not found
    - **500**: Internal server error
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
    Create a new field within a farm.
    
    Fields are subdivisions of a farm used for different crops or purposes.
    Each field tracks its own area, soil type, and geographic boundaries.
    
    ## Request Body
    - **farm_id**: UUID of the parent farm (required)
    - **name**: Field name (required)
    - **area_ha**: Field area in hectares (required)
    - **soil_type**: Soil type classification (optional)
    - **soil_classification**: Detailed soil classification (optional)
    - **boundary_geojson**: GeoJSON polygon for field boundaries (optional)
    - **centroid_geojson**: GeoJSON point for field center (optional)
    - **elevation_m**: Elevation in meters (optional)
    - **slope_degree**: Slope in degrees (optional)
    - **irrigation_type**: Type of irrigation system (optional)
    - **drainage_type**: Type of drainage system (optional)
    
    ## Authentication
    Requires authentication. Only the farm owner or admin can create fields.
    
    ## Responses
    - **201**: Field created successfully
    - **400**: Invalid field data
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (not farm owner)
    - **404**: Parent farm not found
    - **500**: Internal server error
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
    List all fields belonging to a specific farm.
    
    Retrieves all fields for a farm, including their area, soil type,
    and geographic information. Access restricted to farm owner and admins.
    
    ## Query Parameters
    - **farm_id**: UUID of the farm whose fields to retrieve (required)
    
    ## Authentication
    Requires authentication. Only farm owner or admin can view fields.
    
    ## Response
    Returns an array of field objects with complete details.
    
    ## Responses
    - **200**: Fields retrieved successfully
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (not farm owner)
    - **404**: Farm not found
    - **500**: Internal server error
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
    Get detailed information about a specific field.
    
    Retrieves complete field details including boundaries, soil information,
    and optionally weather forecast data if the days parameter is provided.
    
    ## Path Parameters
    - **field_id**: UUID of the field to retrieve (required)
    
    ## Query Parameters
    - **days**: Number of forecast days (1-14, optional)
      - If provided: returns field info + weather forecast
      - If omitted: returns field info only
    
    ## Authentication
    Requires authentication. Only farm owner or admin can access field details.
    
    ## Response Variations
    
    **Without weather (days omitted):**
    Returns field details only.
    
    **With weather (days=7):**
    Returns combined object:
    ```json
    {
      "field": { /* field details */ },
      "weather": { /* current + forecast */ }
    }
    ```
    
    ## Responses
    - **200**: Field details retrieved successfully
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (not farm owner)
    - **404**: Field not found or no location for weather
    - **500**: Internal server error
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
    Update an existing field's information.
    
    Allows modification of field properties such as name, area, soil type,
    and geographic boundaries. Partial updates are supported.
    
    ## Path Parameters
    - **field_id**: UUID of the field to update (required)
    
    ## Request Body
    All fields are optional (partial update):
    - **name**: Updated field name
    - **area_ha**: Updated area in hectares
    - **soil_type**: Updated soil type
    - **soil_classification**: Updated soil classification
    - **boundary_geojson**: Updated boundaries
    - **elevation_m**: Updated elevation
    - **slope_degree**: Updated slope
    - **irrigation_type**: Updated irrigation system
    - **drainage_type**: Updated drainage system
    
    ## Authentication
    Requires authentication. Only farm owner or admin can update fields.
    
    ## Responses
    - **200**: Field updated successfully
    - **400**: Invalid update data
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (not farm owner)
    - **404**: Field not found
    - **500**: Internal server error
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
    
    Performs a soft deletion of the field, retaining the data but marking
    it as deleted. Associated crop cycles are also soft-deleted.
    
    ## Path Parameters
    - **field_id**: UUID of the field to delete (required)
    
    ## Authentication
    Requires authentication. Only farm owner or admin can delete fields.
    
    ## Important Notes
    - Soft delete: data retained with deleted flag
    - Associated crop cycles are also soft-deleted
    - Can potentially be reversed by administrator
    
    ## Responses
    - **204**: Field deleted successfully (no content)
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (not farm owner)
    - **404**: Field not found
    - **500**: Internal server error
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
    Create a new crop cycle for a field.
    
    A crop cycle represents a complete growing season for a specific crop,
    from planting to harvest. Tracks crop variety, dates, expected and
    actual yields.
    
    ## Request Body
    - **field_id**: UUID of the field where crop is planted (required)
    - **product_category**: Crop category (e.g., VEGETABLES, GRAINS) (required)
    - **crop_name**: Name of the crop (required)
    - **variety**: Crop variety (optional)
    - **cultivar**: Specific cultivar (optional)
    - **planting_date**: Date of planting (required)
    - **expected_harvest_date**: Expected harvest date (optional)
    - **expected_yield_kg**: Expected yield in kg (optional)
    - **status**: Cycle status (PLANNED, GROWING, HARVESTED, FAILED)
    - **notes**: Additional notes (optional)
    
    ## Authentication
    Requires authentication. Only farm owner or admin can create crop cycles.
    
    ## Responses
    - **201**: Crop cycle created successfully
    - **400**: Invalid crop cycle data
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (not field owner)
    - **404**: Field not found
    - **500**: Internal server error
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
    List all crop cycles for a specific field.
    
    Retrieves historical and current crop cycles for a field, showing
    planting dates, harvest dates, yields, and status.
    
    ## Query Parameters
    - **field_id**: UUID of the field whose crop cycles to retrieve (required)
    
    ## Authentication
    Requires authentication. Only field owner or admin can view crop cycles.
    
    ## Response
    Returns array of crop cycle objects ordered by planting date (most recent first).
    
    ## Responses
    - **200**: Crop cycles retrieved successfully
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (not field owner)
    - **404**: Field not found
    - **500**: Internal server error
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
    Get detailed information about a specific crop cycle.
    
    Retrieves complete crop cycle information including crop details,
    planting and harvest dates, yield data, and quality grades.
    
    ## Path Parameters
    - **cycle_id**: UUID of the crop cycle to retrieve (required)
    
    ## Authentication
    Requires authentication. Only field owner or admin can access.
    
    ## Response Fields
    - **id**: Crop cycle UUID
    - **field_id**: Parent field UUID
    - **crop_name**: Name of the crop
    - **variety**: Crop variety
    - **planting_date**: When planted
    - **expected_harvest_date**: Expected harvest
    - **actual_harvest_date**: Actual harvest (if completed)
    - **status**: Current status
    - **expected_yield_kg**: Expected yield
    - **actual_yield_kg**: Actual yield (if harvested)
    - **yield_quality_grade**: Quality grade
    - **notes**: Additional notes
    
    ## Responses
    - **200**: Crop cycle retrieved successfully
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (not field owner)
    - **404**: Crop cycle not found
    - **500**: Internal server error
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
    Update an existing crop cycle.
    
    Allows updating crop cycle information including dates, yields, status,
    and quality grades. Commonly used to record harvest results.
    
    ## Path Parameters
    - **cycle_id**: UUID of the crop cycle to update (required)
    
    ## Request Body
    All fields are optional (partial update):
    - **variety**: Updated crop variety
    - **expected_harvest_date**: Updated expected harvest
    - **actual_harvest_date**: Record actual harvest date
    - **status**: Update status (PLANNED, GROWING, HARVESTED, FAILED)
    - **expected_yield_kg**: Update expected yield
    - **actual_yield_kg**: Record actual yield
    - **yield_quality_grade**: Record quality grade
    - **notes**: Additional notes
    
    ## Authentication
    Requires authentication. Only field owner or admin can update.
    
    ## Responses
    - **200**: Crop cycle updated successfully
    - **400**: Invalid update data
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (not field owner)
    - **404**: Crop cycle not found
    - **500**: Internal server error
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

