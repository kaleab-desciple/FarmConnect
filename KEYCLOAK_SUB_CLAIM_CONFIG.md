# How to Configure Keycloak to Include the `sub` Claim

## The Problem

Your JWT tokens are missing the `sub` (subject) claim. The token payload looks like:

```json
{
  "preferred_username": "far1@example.com",
  "email": "far1@example.com",
  "azp": "farm-connect-backend"
  // NO "sub" field!
}
```

## Solution: Add a Protocol Mapper

### Option 1: Via Keycloak Admin Console

1. Go to **Keycloak Admin Console** → http://localhost:8080/admin
2. Select your realm: `farm-connect`
3. Go to **Client Scopes** → **profile** → **Mappers** tab
4. Click **Add mapper** → **By configuration**
5. Select **User Property**
6. Configure:
   - **Name**: `subject`
   - **Property**: `id`
   - **Token Claim Name**: `sub`
   - **Add to ID token**: ON
   - **Add to access token**: ON
   - **Add to userinfo**: ON

### Option 2: Update keycloak_import.json

Add this mapper to your client scope configuration:

```json
{
  "name": "subject",
  "protocol": "openid-connect",
  "protocolMapper": "oidc-usermodel-property-mapper",
  "consentRequired": false,
  "config": {
    "user.attribute": "id",
    "claim.name": "sub",
    "jsonType.label": "String",
    "access.token.claim": "true",
    "id.token.claim": "true",
    "userinfo.token.claim": "true"
  }
}
```

Add this mapper to the `defaultClientScopes` in your client definition.

### Option 3: Fix the Audience (aud) Claim

Your token shows `"aud": "account"` which is wrong - it should be `"farm-connect-backend"`.

1. Go to **Clients** → **farm-connect-backend**
2. Check **Client Scopes** tab
3. Ensure `profile` and `email` are in "Default Client Scopes"
4. The audience should automatically be set to your client ID

## Alternative: Fix in Your Backend Code

The fix I already applied in `jwt.py` works as a fallback - it uses email/username when sub is missing:

```python
def get_user_id(payload: Dict[str, Any]) -> Optional[str]:
    user_id = payload.get("sub")
    if not user_id:
        user_id = payload.get("email") or payload.get("preferred_username")
    return user_id
```

This is a valid workaround, but configuring Keycloak properly is the recommended solution.
