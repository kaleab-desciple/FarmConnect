# Keycloak Authentication - Quick Reference

## 🚀 Quick Start

```bash
# 1. Start Keycloak
docker-compose up -d keycloak

# 2. Import realm (via Keycloak Admin Console at http://localhost:8080)
# Login: admin/admin
# Create Realm → Browse → keycloak_import.json

# 3. Update .env with client secret
KEYCLOAK_CLIENT_SECRET=<your-secret-from-keycloak>

# 4. Start backend
cd server
uvicorn app.main:app --reload --port 8000
```

## 🔑 Get a Token

### User Token (Password Grant)
```bash
curl -X POST http://localhost:8080/realms/farm-connect/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=farm-connect-backend" \
  -d "client_secret=YOUR_SECRET" \
  -d "grant_type=password" \
  -d "username=user@example.com" \
  -d "password=password123"
```

### Service Account Token (Client Credentials)
```bash
curl -X POST http://localhost:8080/realms/farm-connect/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=farm-connect-backend" \
  -d "client_secret=YOUR_SECRET" \
  -d "grant_type=client_credentials"
```

## 📝 Common API Calls

### Check Auth Info
```bash
curl http://localhost:8000/api/v1/auth/info
```

### Check Token Info
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/auth/me
```

### Provision a Farmer (as Agent/Manager/Admin)
```bash
curl -X POST http://localhost:8000/api/v1/auth/provision/farmer \
  -H "Authorization: Bearer YOUR_AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@example.com",
    "phone": "+251911234567",
    "first_name": "John",
    "last_name": "Doe",
    "location": "Addis Ababa"
  }'
```

## 🛡️ Protecting Your Endpoints

### Basic Authentication (Any User)
```python
from app.core.auth import get_current_user, TokenPayload
from fastapi import Depends

@router.get("/my-endpoint")
def my_endpoint(current_user: TokenPayload = Depends(get_current_user)):
    return {"user": current_user.username}
```

### Require Specific Role
```python
from app.core.auth import require_roles

@router.post("/admin-only", dependencies=[Depends(require_roles("ADMIN"))])
def admin_only(current_user: TokenPayload = Depends(require_roles("ADMIN"))):
    return {"message": "Admin access granted"}
```

### Require Any of Multiple Roles
```python
from app.core.auth import require_any_role

@router.get("/manage", dependencies=[Depends(require_any_role("MANAGER", "ADMIN"))])
def manage(current_user: TokenPayload = Depends(require_any_role("MANAGER", "ADMIN"))):
    return {"access": "management"}
```

### Permission-Based
```python
from app.core.auth import require_permission

@router.post("/create-order", dependencies=[Depends(require_permission("orders:create"))])
def create_order(current_user: TokenPayload = Depends(require_permission("orders:create"))):
    return {"message": "Order creation authorized"}
```

### Block Service Accounts
```python
from app.core.auth import block_service_accounts

@router.get("/profile", dependencies=[Depends(block_service_accounts)])
def user_profile(current_user: TokenPayload = Depends(block_service_accounts)):
    return {"user_id": current_user.user_id}
```

### Service Accounts Only
```python
from app.core.auth import require_service_account

@router.post("/internal/job", dependencies=[Depends(require_service_account)])
def internal_job(current_user: TokenPayload = Depends(require_service_account)):
    return {"job": "authorized"}
```

## 🎭 Roles & Permissions

### User Roles
- **ADMIN** - Full system access
- **MANAGER** - Operations management
- **AGENT** - User provisioning, field operations
- **FARMER** - Product listings, order creation
- **MERCHANT** - Order management, purchasing
- **DELIVERY** - Order status updates, delivery

### Service Roles (Client Roles)
- **system_internal** - System maintenance, ledger operations
- **escrow_service** - Escrow and payment management
- **reporting_service** - Analytics and reporting

### Permission Examples
```python
# Defined in app.core.auth.dependencies.ROLE_PERMISSIONS
"ADMIN": ["*"]  # All permissions
"FARMER": ["products:write", "orders:create", "loans:request"]
"MERCHANT": ["orders:write", "orders:read", "products:read"]
"AGENT": ["users:provision", "users:read"]
```

## 🔧 Development Mode

### Disable Authentication (for testing)
```bash
# In .env
AUTH_ENABLED=false
```

When disabled:
- All endpoints accessible without tokens
- Swagger UI works without authentication
- Mock user returned with ADMIN role

### Enable Authentication (production)
```bash
# In .env
AUTH_ENABLED=true
```

When enabled:
- All endpoints require valid JWT
- 401 for missing/invalid tokens
- 403 for insufficient permissions

## 🧪 Testing

### Test Service Account
```bash
cd server
python test_service_account.py
```

### Test with Swagger UI
1. Open http://127.0.0.1:8000/docs
2. Get a token (see "Get a Token" above)
3. Click "Authorize" button
4. Enter token
5. Test endpoints

## 📚 Available Endpoints

### Public (No Auth)
- `GET /api/v1/auth/info` - Auth configuration
- `GET /api/v1/auth/health` - Health check
- `GET /api/v1/auth/me` - Token info (optional auth)
- `POST /api/v1/auth/verify` - Verify token

### Provisioning (AGENT/MANAGER/ADMIN)
- `POST /api/v1/auth/provision/farmer`
- `POST /api/v1/auth/provision/merchant`
- `POST /api/v1/auth/provision/delivery`

### Examples (Various Roles)
- `GET /api/v1/examples/protected/basic` - Any authenticated user
- `GET /api/v1/examples/protected/admin-only` - ADMIN only
- `GET /api/v1/examples/protected/manager-or-admin` - MANAGER or ADMIN
- `POST /api/v1/examples/protected/create-order` - Permission-based
- `GET /api/v1/examples/protected/user-profile` - No service accounts
- `POST /api/v1/examples/protected/internal/reconcile` - Service accounts only

## 🐛 Troubleshooting

### "Failed to fetch JWKS"
- Check Keycloak is running: `docker-compose ps`
- Verify `KEYCLOAK_URL` in `.env`

### "Invalid token"
- Token expired (default: 5 min) - get new token
- Wrong issuer - check `KEYCLOAK_REALM`

### "User already exists"
- Check Keycloak Admin Console
- Delete user or use different email

### "Service account authentication failed"
- Verify `KEYCLOAK_CLIENT_SECRET` in `.env`
- Check "Service Accounts Enabled" in Keycloak client

## 📖 Full Documentation

- [KEYCLOAK_SETUP.md](file:///home/kaleab/Desktop/Farm_Connect/KEYCLOAK_SETUP.md) - Complete setup guide
- [walkthrough.md](file:///home/kaleab/.gemini/antigravity/brain/6b52bf4a-9e70-43a9-9bb4-6f864956ca0d/walkthrough.md) - Implementation walkthrough
- [implementation_plan.md](file:///home/kaleab/.gemini/antigravity/brain/6b52bf4a-9e70-43a9-9bb4-6f864956ca0d/implementation_plan.md) - Technical plan

## 🔗 Useful URLs

- Keycloak Admin: http://localhost:8080 (admin/admin)
- API Docs: http://127.0.0.1:8000/docs
- Auth Info: http://localhost:8000/api/v1/auth/info
- Health Check: http://localhost:8000/api/v1/auth/health
