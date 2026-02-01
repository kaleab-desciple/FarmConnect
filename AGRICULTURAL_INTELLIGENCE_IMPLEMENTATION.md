# Farm_Connect Agricultural Intelligence Extension - Implementation Guide

## Overview

This document provides a comprehensive guide to the Agricultural Intelligence Extension implementation for Farm_Connect. The extension adds four new service domains through separate bounded contexts that integrate with existing core services.

## Implementation Status

### ✅ Completed Components

1. **Database Schema Migration** (`server/app/alembic/versions/001_agricultural_intelligence.py`)
   - All 4 domains with 20+ tables
   - PostGIS-ready (using JSONB for geometry storage)
   - Complete with indexes, constraints, and foreign keys
   - Integration tables linking to existing system

2. **Domain Models** (`server/app/domain/agriculture/`)
   - `enums.py`: All enum types for agricultural intelligence
   - `entities.py`: Pydantic models for all entities across 4 domains

3. **Weather Provider** (`server/app/infrastructure/external/weather/`)
   - Abstract `WeatherProvider` interface
   - `OpenMeteoWeatherProvider` implementation with:
     - Current weather fetching
     - 7-day forecast
     - Historical data retrieval
     - Built-in risk assessment

4. **API Routes** (`server/app/api/v1/agriculture/farms/`)
   - Complete CRUD for farms and fields with role-based access control

### 🚧 Components to Complete

The following components follow the established patterns and can be implemented using the provided templates:

## Architecture

```
server/app/
├── alembic/versions/
│   └── 001_agricultural_intelligence.py  ✅ Complete
├── domain/agriculture/
│   ├── __init__.py                       ✅ Complete
│   ├── enums.py                          ✅ Complete
│   └── entities.py                       ✅ Complete
├── infrastructure/external/weather/
│   ├── __init__.py                       ✅ Complete
│   ├── provider.py                       ✅ Complete
│   └── open_meteo.py                     ✅ Complete
└── api/v1/agriculture/farms/             ✅ Complete
|__ api/v1/agriculture/crops/
|__ api/v1/agriculture/monitoring/
|__ api/v1/agriculture/tasks/
|__ api/v1/agriculture/weather/
|__ api/v1/agriculture/alerts/
|__ api/v1/agriculture/risk/
|__ api/v1/agriculture/advisory/
```


## API Endpoints Summary

POST   /api/v1/agriculture/farms                    # Create farm
GET    /api/v1/agriculture/farms                    # List farms
GET    /api/v1/agriculture/farms/{farm_id}          # Get farm
PUT    /api/v1/agriculture/farms/{farm_id}          # Update farm
DELETE /api/v1/agriculture/farms/{farm_id}          # Delete farm
POST   /api/v1/agriculture/farms/{farm_id}/fields   # Create field
GET    /api/v1/agriculture/farms/{farm_id}/fields   # List fields
```

#### Crop Cycles (📝 To Implement)
POST   /api/v1/agriculture/fields/{field_id}/crop-cycles
GET    /api/v1/agriculture/fields/{field_id}/crop-cycles
GET    /api/v1/agriculture/crop-cycles/{cycle_id}
PUT    /api/v1/agriculture/crop-cycles/{cycle_id}
POST   /api/v1/agriculture/crop-cycles/{cycle_id}/harvest
GET    /api/v1/agriculture/crop-cycles/active
```

#### Monitoring (📝 To Implement)
POST   /api/v1/agriculture/fields/{field_id}/ndvi-snapshots
GET    /api/v1/agriculture/fields/{field_id}/ndvi-snapshots
GET    /api/v1/agriculture/fields/{field_id}/ndvi-trend
POST   /api/v1/agriculture/fields/{field_id}/soil-readings
GET    /api/v1/agriculture/fields/{field_id}/soil-readings
POST   /api/v1/agriculture/fields/{field_id}/pest-disease-reports
GET    /api/v1/agriculture/fields/{field_id}/pest-disease-reports
POST   /api/v1/agriculture/pest-disease-reports/{report_id}/treatments
```

### Domain 2: Planning & Operational Tools (📝 To Implement)
```
POST   /api/v1/agriculture/fields/{field_id}/tasks
GET    /api/v1/agriculture/fields/{field_id}/tasks
GET    /api/v1/agriculture/tasks/{task_id}
PUT    /api/v1/agriculture/tasks/{task_id}
POST   /api/v1/agriculture/tasks/{task_id}/complete
GET    /api/v1/agriculture/tasks/calendar
GET    /api/v1/agriculture/tasks/overdue
```

### Domain 3: Risk Mitigation & Intelligence (📝 To Implement)
```
GET    /api/v1/agriculture/fields/{field_id}/weather/current
GET    /api/v1/agriculture/fields/{field_id}/weather/forecast
GET    /api/v1/agriculture/fields/{field_id}/weather/risks
GET    /api/v1/agriculture/alerts
POST   /api/v1/agriculture/alerts/{alert_id}/acknowledge
GET    /api/v1/agriculture/fields/{field_id}/risk-score
```

### Domain 4: Expert Advisory & Community (📝 To Implement)
```
POST   /api/v1/advisory/sessions
GET    /api/v1/advisory/sessions
POST   /api/v1/advisory/sessions/{session_id}/messages
GET    /api/v1/knowledge/articles
POST   /api/v1/knowledge/articles
```

## Role-Based Access Control Matrix

| Resource | FARMER | MERCHANT | AGRONOMIST | FIELD_ANALYST | AGENT | MANAGER | ADMIN |
|----------|--------|----------|------------|---------------|-------|---------|-------|
| Farms | Own: CRUD | - | Assigned: R | All: R | - | All: CRUD | All: CRUD |
| Fields | Own: CRUD | - | Assigned: R | All: R | - | All: CRUD | All: CRUD |
| Crop Cycles | Own: CRUD | - | Assigned: RU | All: R | - | All: CRUD | All: CRUD |
| NDVI Data | Own: R | - | Assigned: R | All: CRUD | - | All: R | All: CRUD |
| Soil Readings | Own: CRUD | - | Assigned: RU | All: CRUD | - | All: R | All: CRUD |
| Pest Reports | Own: CRUD | - | Assigned: CRUD | All: R | - | All: R | All: CRUD |
| Tasks | Own: CRUD | - | Assigned: RU | - | - | All: CRUD | All: CRUD |
| Weather | Own: R | - | Assigned: R | All: R | - | All: R | All: R |
| Alerts | Own: RU | Own: RU | Own: RU | Own: RU | Own: RU | All: R | All: CRUD |
| Advisory | Own: CRUD | - | Assigned: CRUD | - | - | All: R | All: CRUD |

## Implementation Templates

### Template: Crop Cycles API (`crops.py`)

```python
"""Crop Cycle Management API Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import date

from app.core.database import get_db
from app.core.auth.dependencies import get_current_user, require_roles
from app.domain.agriculture.enums import CropCycleStatus
from pydantic import BaseModel

router = APIRouter(prefix="/crop-cycles", tags=["crop-cycles"])

class CropCycleCreate(BaseModel):
    product_category: str
    crop_name: str
    variety: Optional[str] = None
    planting_date: date
    expected_harvest_date: Optional[date] = None
    expected_yield_kg: Optional[Decimal] = None
    # ... other fields

@router.post("/fields/{field_id}/crop-cycles", response_model=CropCycleResponse)
async def create_crop_cycle(
    field_id: UUID,
    cycle_data: CropCycleCreate,
    current_user: dict = Depends(require_roles(["FARMER", "ADMIN"])),
    db: AsyncSession = Depends(get_db)
):
    """Create new crop cycle"""
    # Implementation follows farms.py pattern
    pass

# ... other endpoints
```

### Template: Weather API (`weather.py`)

```python
"""Weather Data API Routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from datetime import date

from app.core.database import get_db
from app.core.auth.dependencies import get_current_user
from app.infrastructure.external.weather.open_meteo import OpenMeteoWeatherProvider

router = APIRouter(prefix="/weather", tags=["weather"])

@router.get("/fields/{field_id}/current")
async def get_current_weather(
    field_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current weather for field"""
    # 1. Fetch field coordinates
    # 2. Call weather provider
    # 3. Store snapshot in database
    # 4. Return weather data
    
    weather_provider = OpenMeteoWeatherProvider()
    # ... implementation
    pass

@router.get("/fields/{field_id}/forecast")
async def get_weather_forecast(
    field_id: UUID,
    days: int = Query(7, ge=1, le=14),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get weather forecast for field"""
    weather_provider = OpenMeteoWeatherProvider()
    # ... implementation
    pass
```

## Database Migration

To apply the schema:

```bash
cd server/app
alembic upgrade head
```

This will create all tables, indexes, and constraints for the agricultural intelligence extension.

## Integration Points

### 1. Product → Crop Cycle Linkage

When harvest is recorded:
```python
# In crop cycle harvest endpoint
await db.execute("""
    INSERT INTO crop_cycle_products (crop_cycle_id, product_id, quantity_kg, harvest_date)
    VALUES (:cycle_id, :product_id, :quantity, :date)
""", {...})
```

### 2. Order → Field Source Tracking

When creating orders:
```python
# In order creation
await db.execute("""
    INSERT INTO order_field_sources (order_id, field_id, quantity_kg)
    VALUES (:order_id, :field_id, :quantity)
""", {...})
```

### 3. Loan → Crop Cycle Allocation

When approving agricultural loans:
```python
# In loan approval
await db.execute("""
    INSERT INTO loan_crop_cycles (loan_id, crop_cycle_id, allocated_amount_usd)
    VALUES (:loan_id, :cycle_id, :amount)
""", {...})
```

### 4. Escrow → Field Conditions

When creating escrow with field conditions:
```python
# In escrow creation
await db.execute("""
    INSERT INTO escrow_field_conditions (
        escrow_id, field_id, condition_type, condition_description, threshold_value
    ) VALUES (:escrow_id, :field_id, :type, :description, :threshold)
""", {...})
```

## Configuration

Add to `.env`:

```env
# Weather API Configuration
WEATHER_PROVIDER=open_meteo
WEATHER_API_TIMEOUT=30

# Agricultural Intelligence Features
ENABLE_NDVI_MONITORING=true
ENABLE_WEATHER_ALERTS=true
ENABLE_ADVISORY_SYSTEM=true

# Alert Configuration
ALERT_RETENTION_DAYS=90
CRITICAL_ALERT_EMAIL=true
```

## Testing

### Unit Tests Template

```python
# tests/test_agriculture/test_farms.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_farm(client: AsyncClient, farmer_token: str):
    response = await client.post(
        "/api/v1/agriculture/farms",
        json={
            "name": "Test Farm",
            "location_lat": 9.0320,
            "location_lng": 38.7469,
            "total_area_ha": 10.5
        },
        headers={"Authorization": f"Bearer {farmer_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Farm"
```

## Monitoring & Observability

Key metrics to track:

1. **Data Freshness**
   - Last NDVI update per field
   - Last weather sync timestamp
   - Stale data alerts

2. **System Health**
   - Weather API response times
   - NDVI processing queue depth
   - Alert delivery success rate

3. **User Engagement**
   - Active crop cycles
   - Task completion rate
   - Advisory session response time

## Next Steps

1. **Immediate** (Week 1-2):
   - Complete crop cycle management API
   - Implement monitoring endpoints (NDVI, soil, pest/disease)
   - Set up weather data sync job

2. **Short-term** (Week 3-4):
   - Implement task management system
   - Build alert generation logic
   - Create risk scoring algorithm

3. **Medium-term** (Month 2):
   - Implement advisory system
   - Build knowledge base
   - Create integration with existing loan/escrow systems

4. **Long-term** (Month 3+):
   - Add ML-based pest/disease detection
   - Implement yield prediction models
   - Build farmer mobile app integration

## Support & Documentation

- **API Documentation**: Auto-generated at `/docs` (FastAPI Swagger UI)
- **Database Schema**: See migration file for complete schema
- **Role Permissions**: See access control matrix above
- **Weather Provider**: Open-Meteo API (free tier: 10,000 calls/day)

## Security Considerations

1. **Data Privacy**: Farm locations and crop data are sensitive
2. **Access Control**: Strict role-based permissions enforced
3. **API Rate Limiting**: Implement for weather API calls
4. **Data Validation**: All inputs validated via Pydantic models
5. **Soft Deletes**: All entities use soft delete for audit trail

## Performance Optimization

1. **Database Indexes**: All foreign keys and common queries indexed
2. **Caching**: Consider Redis for weather data (TTL: 1 hour)
3. **Pagination**: All list endpoints support skip/limit
4. **Async Operations**: All I/O operations are async
5. **Batch Processing**: NDVI and weather sync should run as background jobs

## Conclusion

This implementation provides a solid foundation for agricultural intelligence in Farm_Connect. The modular architecture allows for incremental development while maintaining clean separation of concerns. Each domain can be developed and deployed independently, following the established patterns in the codebase.

For questions or issues, refer to the main Farm_Connect documentation or create an issue in the project repository.
