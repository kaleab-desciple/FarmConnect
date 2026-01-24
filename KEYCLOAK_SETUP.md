# Keycloak Authentication Setup Guide

## Overview

This guide explains how to set up and use Keycloak authentication for the Farm Connect Platform.

## Prerequisites

1. Docker and Docker Compose installed
2. Python dependencies installed (`pip install -r requirements.txt`)
3. PostgreSQL database running

## Step 1: Start Keycloak

```bash
# Start Keycloak using Docker Compose
docker-compose up -d keycloak

# Wait for Keycloak to start (usually 30-60 seconds)
# Check logs
docker-compose logs -f keycloak
```

Keycloak will be available at: `http://localhost:8080`

## Step 2: Import Realm Configuration

### Option A: Using Keycloak Admin Console (Recommended for First Time)

1. Open `http://localhost:8080` in your browser
2. Click "Administration Console"
3. Login with:
   - Username: `admin`
   - Password: `admin`
4. Click "Create Realm" (or select realm dropdown)
5. Click "Browse" and select `keycloak_import.json`
6. Click "Create"

### Option B: Using Keycloak CLI (Advanced)

```bash
# Copy import file into container
docker cp keycloak_import.json <container_id>:/tmp/

# Import realm
docker exec <container_id> /opt/keycloak/bin/kc.sh import \
  --file /tmp/keycloak_import.json
```

## Step 3: Configure Client Secret

After importing, you need to set the actual client secret:

1. In Keycloak Admin Console, go to:
   - Realm: `farm-connect`
   - Clients → `farm-connect-backend`
   - Credentials tab
2. Click "Regenerate Secret" or note the existing secret
3. Copy the secret value
4. Update `.env` file:
   ```bash
   KEYCLOAK_CLIENT_SECRET=<your-secret-here>
   ```

## Step 4: Verify Configuration

### Check Realm Roles

In Keycloak Admin Console:
- Realm Settings → Roles
- Verify these roles exist:
  - ADMIN
  - MANAGER
  - AGENT
  - FARMER
  - MERCHANT
  - DELIVERY

### Check Groups

- Groups menu
- Verify these groups exist with correct role mappings:
  - Admins → ADMIN role
  - Managers → MANAGER role
  - Agents → AGENT role
  - Farmers → FARMER role
  - Merchants → MERCHANT role
  - Delivery → DELIVERY role

### Check Client Configuration

- Clients → `farm-connect-backend`
- Settings tab:
  - ✅ Service Accounts Enabled
  - ✅ Standard Flow Enabled
  - ✅ Direct Access Grants Enabled
- Service Account Roles tab:
  - Verify client roles exist:
    - system_internal
    - escrow_service
    - reporting_service

## Step 5: Start the Backend

```bash
cd server
uvicorn app.main:app --reload --port 8000
```

## Step 6: Test Authentication

### Test 1: Check Auth Info (No Auth Required)

```bash
curl http://localhost:8000/api/v1/auth/info
```

Expected response:
```json
{
  "keycloak_url": "http://localhost:8080",
  "realm": "farm-connect",
  "client_id": "farm-connect-backend",
  "token_endpoint": "http://localhost:8080/realms/farm-connect/protocol/openid-connect/token",
  "auth_enabled": false,
  "message": "To authenticate, obtain a token..."
}
```

### Test 2: Health Check

```bash
curl http://localhost:8000/api/v1/auth/health
```

Expected response:
```json
{
  "status": "healthy",
  "auth_enabled": false,
  "keycloak_reachable": true,
  "jwks_keys_count": 2
}
```

### Test 3: Service Account Token

```bash
cd server
python test_service_account.py
```

This will test:
- Token acquisition using client credentials
- Token validation
- Role extraction
- Service account detection

## Step 7: Create Test Users

### Create an Admin User (via Keycloak Console)

1. Users → Add User
2. Fill in:
   - Username: `admin@farmconnect.com`
   - Email: `admin@farmconnect.com`
   - First Name: `Admin`
   - Last Name: `User`
3. Save
4. Credentials tab → Set Password
   - Password: `admin123`
   - Temporary: OFF
5. Groups tab → Join "Admins" group

### Create an Agent User (via Keycloak Console)

1. Users → Add User
2. Fill in:
   - Username: `agent@farmconnect.com`
   - Email: `agent@farmconnect.com`
   - First Name: `Field`
   - Last Name: `Agent`
3. Save
4. Credentials tab → Set Password
   - Password: `agent123`
   - Temporary: OFF
5. Groups tab → Join "Agents" group

## Step 8: Test User Authentication

### Get Token for Admin

```bash
curl -X POST http://localhost:8080/realms/farm-connect/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=farm-connect-backend" \
  -d "client_secret=<your-secret>" \
  -d "grant_type=password" \
  -d "username=admin@farmconnect.com" \
  -d "password=admin123"
```

Save the `access_token` from the response.

### Test Token Info

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

Expected response:
```json
{
  "valid": true,
  "user_id": "...",
  "username": "admin@farmconnect.com",
  "email": "admin@farmconnect.com",
  "roles": ["ADMIN"],
  "is_service_account": false,
  "expires_at": 1234567890
}
```

## Step 9: Test User Provisioning

### Provision a Farmer (as Agent)

First, get an agent token (same as Step 8, but with agent credentials).

Then:

```bash
curl -X POST http://localhost:8000/api/v1/auth/provision/farmer \
  -H "Authorization: Bearer <agent_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer1@example.com",
    "phone": "+251911234567",
    "first_name": "John",
    "last_name": "Farmer",
    "location": "Addis Ababa"
  }'
```

Expected response:
```json
{
  "user_id": "...",
  "keycloak_id": "...",
  "email": "farmer1@example.com",
  "temporary_password": "RandomPass123!",
  "password_reset_required": true,
  "message": "User successfully created with role FARMER..."
}
```

### Verify in Keycloak

1. Go to Keycloak Admin Console
2. Users → Search for `farmer1@example.com`
3. Verify user exists and is in "Farmers" group

## Step 10: Enable Authentication (Production Mode)

When ready to enforce authentication:

1. Update `.env`:
   ```bash
   AUTH_ENABLED=true
   ```

2. Restart the backend

3. All endpoints (except `/auth/*`) will now require authentication

## Using FastAPI Docs with Authentication

When `AUTH_ENABLED=false` (development):
- You can use Swagger UI at `http://127.0.0.1:8000/docs` without authentication
- All endpoints are accessible

When `AUTH_ENABLED=true` (production):
1. Open `http://127.0.0.1:8000/docs`
2. Click "Authorize" button (top right)
3. Enter your Bearer token: `<access_token>`
4. Click "Authorize"
5. Now you can test authenticated endpoints

## Troubleshooting

### "Failed to fetch JWKS"

- Check Keycloak is running: `docker-compose ps`
- Check Keycloak URL in `.env` is correct
- Verify realm name is `farm-connect`

### "Invalid token"

- Token may be expired (default: 5 minutes)
- Get a fresh token
- Check token issuer matches your Keycloak URL

### "User already exists"

- Check if user exists in Keycloak Admin Console
- Delete user and try again
- Or use a different email/phone

### "Service account authentication failed"

- Verify client secret in `.env` is correct
- Check "Service Accounts Enabled" in Keycloak client settings
- Verify client credentials grant type is enabled

## Security Notes

⚠️ **Important for Production:**

1. Change default admin password in Keycloak
2. Use strong client secrets (not `CHANGE_ME_BACKEND_SECRET`)
3. Enable HTTPS for Keycloak
4. Set `AUTH_ENABLED=true`
5. Configure proper token lifetimes in Keycloak
6. Enable rate limiting on provisioning endpoints
7. Use environment-specific secrets (not committed to git)

## Next Steps

- [ ] Add refresh token flow
- [ ] Implement password reset endpoints
- [ ] Add email verification
- [ ] Configure SMS notifications for temp passwords
- [ ] Add audit logging for provisioning actions
- [ ] Implement role-based UI in frontend
