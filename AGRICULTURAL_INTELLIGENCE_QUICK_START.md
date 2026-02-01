# Agricultural Intelligence Extension - Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### 1. Run Database Migration

```bash
cd server/app
alembic upgrade head
```

This creates all agricultural intelligence tables.

### 2. Add New Roles to Keycloak

Add these roles in Keycloak Admin Console:
- `AGRONOMIST` - Agricultural experts who provide advice
- `FIELD_ANALYST` - Data analysts for field monitoring

### 3. Test the API

```bash
# Create a farm (as FARMER)
curl -X POST http://localhost:8000/api/v1/farms \
  -H "Authorization: Bearer $FARMER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Green Valley Farm",
    "location_lat": 9.0320,
    "location_lng": 38.7469,
    "total_area_ha": 25.5,
    "location_address": "Addis Ababa, Ethiopia"
  }'

# Create a field
curl -X POST http://localhost:8000/api/v1/farms/{farm_id}/fields \
  -H "Authorization: Bearer $FARMER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "North Field",
    "area_ha": 5.2,
    "boundary_geojson": {
      "type": "Polygon",
      "coordinates": [[[38.7469, 9.0320], [38.7479, 9.0320], [38.7479, 9.0330], [38.7469, 9.0330], [38.7469, 9.0320]]]
    },
    "soil_type": "Clay Loam",
    "irrigation_type": "Drip"
  }'
```

## 📊 What's Included

### ✅ Fully Implemented

1. **Database Schema** (20+ tables)
   - Farms & Fields
   - Crop Cycles
   - NDVI Monitoring
   - Soil Readings
   - Pest/Disease Reports
   - Farm Tasks
   - Weather Data
   - Alerts
   - Risk Scores
   - Advisory Sessions
   - Knowledge Base
   - Integration Tables

2. **Domain Models**
   - All entities with Pydantic validation
   - Complete enum types
   - Type-safe models

3. **Weather Provider**
   - Open-Meteo integration
   - Current weather
   - 7-day forecast
   - Historical data
   - Risk assessment

4. **Farm Management API**
   - CRUD operations for farms
   - CRUD operations for fields
   - Role-based access control
   - Soft delete support

### 📝 Ready to Implement (Templates Provided)

The following APIs follow the same pattern as farms.py:

1. **Crop Cycles** - Track planting to harvest
2. **Monitoring** - NDVI, soil, pest/disease
3. **Tasks** - Farm operation scheduling
4. **Weather** - Real-time weather integration
5. **Alerts** - Automated notifications
6. **Risk Scoring** - Field risk assessment
7. **Advisory** - Expert consultation system

## 🎯 Key Features

### 1. Precision Agriculture
- **Field Mapping**: GeoJSON boundary support
- **NDVI Monitoring**: Satellite-based crop health
- **Soil Analysis**: Multi-parameter tracking
- **Pest/Disease**: Image-based reporting

### 2. Smart Planning
- **Task Management**: Automated scheduling
- **Weather Integration**: Real-time forecasts
- **Risk Alerts**: Proactive notifications

### 3. Expert Support
- **Advisory Sessions**: Connect farmers with agronomists
- **Knowledge Base**: Searchable agricultural content
- **Treatment Recommendations**: Pest/disease solutions

### 4. Financial Integration
- **Loan Linkage**: Connect loans to crop cycles
- **Escrow Conditions**: Field-based release triggers
- **Order Traceability**: Track produce from field to market

## 🔐 Security & Access Control

### Role Permissions

```
FARMER:
  ✓ Manage own farms, fields, crops
  ✓ Create pest reports, tasks
  ✓ Request advisory sessions
  ✓ View own weather & alerts

AGRONOMIST:
  ✓ View assigned fields
  ✓ Provide treatment recommendations
  ✓ Respond to advisory sessions
  ✓ Create knowledge articles

FIELD_ANALYST:
  ✓ View all fields (read-only)
  ✓ Upload NDVI data
  ✓ Create soil readings
  ✓ Generate risk scores

ADMIN:
  ✓ Full access to all resources
```

## 📈 Data Flow Examples

### Example 1: Complete Crop Cycle

```
1. Farmer creates farm & field
2. Farmer starts crop cycle (planting)
3. System auto-generates tasks (irrigation, fertilization)
4. Field analyst uploads NDVI snapshots
5. System detects stress → creates alert
6. Farmer reports pest issue
7. Agronomist provides treatment recommendation
8. Farmer completes harvest
9. System links harvest to product inventory
10. Order created with field traceability
```

### Example 2: Weather-Based Alert

```
1. Weather service fetches forecast
2. System detects frost risk
3. Alert created for affected farmers
4. Farmer receives notification
5. Farmer takes protective action
6. Farmer acknowledges alert
```

### Example 3: Agricultural Loan

```
1. Farmer applies for loan
2. Agent reviews field risk scores
3. Loan approved and linked to crop cycle
4. Escrow created with field conditions
5. System monitors NDVI & weather
6. Conditions met → escrow released
7. Farmer repays from harvest proceeds
```

## 🔧 Configuration

Add to `.env`:

```env
# Weather API
WEATHER_PROVIDER=open_meteo
WEATHER_API_TIMEOUT=30

# Features
ENABLE_NDVI_MONITORING=true
ENABLE_WEATHER_ALERTS=true
ENABLE_ADVISORY_SYSTEM=true

# Alerts
ALERT_RETENTION_DAYS=90
CRITICAL_ALERT_EMAIL=true
```

## 📱 API Endpoints

### Farms & Fields ✅
```
POST   /api/v1/farms
GET    /api/v1/farms
GET    /api/v1/farms/{farm_id}
PUT    /api/v1/farms/{farm_id}
DELETE /api/v1/farms/{farm_id}
POST   /api/v1/farms/{farm_id}/fields
GET    /api/v1/farms/{farm_id}/fields
```

### Crop Cycles 📝
```
POST   /api/v1/fields/{field_id}/crop-cycles
GET    /api/v1/crop-cycles/{cycle_id}
POST   /api/v1/crop-cycles/{cycle_id}/harvest
```

### Monitoring 📝
```
POST   /api/v1/fields/{field_id}/ndvi-snapshots
GET    /api/v1/fields/{field_id}/ndvi-trend
POST   /api/v1/fields/{field_id}/soil-readings
POST   /api/v1/fields/{field_id}/pest-disease-reports
```

### Weather 📝
```
GET    /api/v1/fields/{field_id}/weather/current
GET    /api/v1/fields/{field_id}/weather/forecast
```

### Tasks 📝
```
POST   /api/v1/fields/{field_id}/tasks
GET    /api/v1/tasks/calendar
GET    /api/v1/tasks/overdue
```

### Alerts 📝
```
GET    /api/v1/alerts
POST   /api/v1/alerts/{alert_id}/acknowledge
```

### Advisory 📝
```
POST   /api/v1/advisory/sessions
GET    /api/v1/advisory/sessions
POST   /api/v1/advisory/sessions/{session_id}/messages
```

## 🧪 Testing

```bash
# Run tests
pytest tests/test_agriculture/

# Test specific module
pytest tests/test_agriculture/test_farms.py -v

# Test with coverage
pytest tests/test_agriculture/ --cov=app.api.v1.agriculture
```

## 📊 Database Schema Highlights

### Core Tables
- `farms` - Farm properties and boundaries
- `fields` - Individual field/plot data
- `crop_cycles` - Planting to harvest tracking
- `ndvi_snapshots` - Satellite crop health data
- `soil_readings` - Soil analysis results
- `pest_disease_reports` - Issue tracking
- `farm_tasks` - Operation scheduling
- `weather_snapshots` - Historical weather
- `weather_forecasts` - Future predictions
- `alerts` - User notifications
- `field_risk_scores` - Risk assessment
- `advisory_sessions` - Expert consultations
- `knowledge_articles` - Agricultural content

### Integration Tables
- `crop_cycle_products` - Links harvest to inventory
- `order_field_sources` - Field-to-order traceability
- `loan_crop_cycles` - Agricultural loan allocation
- `escrow_field_conditions` - Field-based escrow triggers

## 🎓 Learning Resources

### Understanding the Architecture

1. **Bounded Contexts**: Each domain (crops, monitoring, tasks, advisory) is independent
2. **Event-Driven**: Alerts and notifications triggered by data changes
3. **Integration Points**: Clean interfaces to existing loan/escrow/order systems
4. **Role-Based Security**: Fine-grained permissions per resource

### Key Design Patterns

- **Repository Pattern**: Data access abstraction (to be implemented)
- **Service Layer**: Business logic separation (to be implemented)
- **Provider Pattern**: Weather data abstraction (✅ implemented)
- **Soft Deletes**: Audit trail preservation
- **JSONB Metadata**: Extensibility without schema changes

## 🚦 Next Steps

1. **Implement Remaining APIs** (use templates in implementation guide)
2. **Add Background Jobs** (weather sync, NDVI processing)
3. **Build Alert Logic** (risk detection, notifications)
4. **Create Mobile App** (farmer-facing interface)
5. **Add ML Models** (yield prediction, pest detection)

## 📞 Support

- **Documentation**: See `AGRICULTURAL_INTELLIGENCE_IMPLEMENTATION.md`
- **API Docs**: http://localhost:8000/docs
- **Database Schema**: `server/app/alembic/versions/001_agricultural_intelligence.py`

## 🎉 Success Criteria

You'll know the system is working when:

✅ Farmers can create farms and fields
✅ Weather data is fetched for field locations
✅ NDVI snapshots show crop health trends
✅ Alerts notify farmers of risks
✅ Agronomists can provide advice
✅ Loans are linked to crop cycles
✅ Orders show field traceability

---

**Ready to revolutionize agricultural finance! 🌾🚜📊**
