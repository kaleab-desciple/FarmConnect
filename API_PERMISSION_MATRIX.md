# Farm Connect - API Permission Matrix (Single Source of Truth)

This matrix defines the authoritative mapping between API domain endpoints and the roles allowed to access them.

## Roles Definitions

### Realm Roles (Humans)
- **ADMIN**: System Administrator (Full Access)
- **MANAGER**: Operations / Regional Manager
- **AGENT**: Field Agent (Onboarding focus)
- **FARMER**: Primary Producer
- **MERCHANT**: Buyer / Trader
- **DELIVERY**: Logistics Provider

### Client Roles (Machine / Service Accounts)
- **system_internal**: Internal backend background jobs
- **escrow_service**: Payment processing and settlement engine
- **reporting_service**: Analytics and financial reporting tools

---

## 🗺️ Matrix

| API Domain | Endpoint / Feature | Method | Required Permission | Allowed Roles |
| :--- | :--- | :--- | :--- | :--- |
| **Users** | Provision Farmer/Merchant/Delivery | POST | `users:provision` | ADMIN, MANAGER, AGENT |
| **Users** | Create User (General) | POST | `users:write` | ADMIN, MANAGER |
| **Users** | View User Profile / Details | GET | `users:read` | ADMIN, MANAGER, AGENT |
| **Users** | View/Update Reputation Score | GET/POST | `users:reputation` | ADMIN, MANAGER, AGENT |
| **Products** | Create Product Listing | POST | `products:create` | ADMIN, FARMER |
| **Products** | Update Product | PUT/PATCH | `products:update` | ADMIN, FARMER |
| **Products** | Delete Product | DELETE | `products:delete` | ADMIN |
| **Products** | List/Search Products | GET | `products:read` | *All Authenticated Users* |
| **Orders** | Create Order (Atomic) | POST | `orders:create` | ADMIN, FARMER, MERCHANT |
| **Orders** | Get Order Status | GET | `orders:read` | *All Authenticated Users* |
| **Orders** | Cancel Order | POST | `orders:cancel` | ADMIN, MANAGER, FARMER, MERCHANT |
| **Orders** | Update Order Details | PUT/PATCH | `orders:update` | ADMIN, MANAGER, FARMER, MERCHANT, DELIVERY |
| **Escrow** | Fund Escrow (External Payment) | POST | `escrow:fund` | ADMIN, escrow_service |
| **Escrow** | Release Escrow (Settlement) | POST | `escrow:release` | ADMIN, escrow_service |
| **Escrow** | Refund Escrow | POST | `escrow:refund` | ADMIN, escrow_service |
| **Escrow** | Penalize Escrow | POST | `escrow:penalize` | ADMIN, escrow_service |
| **Loans** | Request New Loan | POST | `loans:request` | ADMIN, FARMER |
| **Loans** | Approve Loan | POST | `loans:approve` | ADMIN, MANAGER |
| **Loans** | List/Read Loans | GET | `loans:read` | ADMIN, MANAGER, FARMER, reporting_service |
| **Loans** | Disburse Loan Funds | POST | `loans:disburse` | ADMIN, system_internal |
| **Ledger** | Read Financial Ledger | GET | `ledger:read` | ADMIN, MANAGER, reporting_service |
| **Ledger** | Record Entry (Accounting) | POST | `ledger:write` | ADMIN, system_internal, escrow_service |
| **Reports** | Financial Reports (P&L, Balance) | GET | `reports:financial` | ADMIN, MANAGER, reporting_service |
| **Reports** | Operational / Field Reports | GET | `reports:operational` | ADMIN, MANAGER, AGENT, reporting_service |
| **Internal** | System Maintenance | ALL | `system:maintenance` | ADMIN, system_internal |
| **Internal** | Platform Analytics | GET | `system:analytics` | ADMIN, reporting_service |

---

## 🛡️ Security Implementation Details

### Implementation Rules

1.  **Strict Separation**: Realm roles (humans) and Client roles (machines) are stored in separate lists in the `TokenPayload`.
2.  **No Logic in Routes**: Every endpoint uses the `require_permission(key)` dependency.
3.  **Audit Ready**: Permissions are resolved in the backend from a single `PERMISSIONS` dictionary in `app/core/auth/permissions.py`.
4.  **Admin Override**: The `ADMIN` role is explicitly granted access in the permission mapping for almost all endpoints.

### Usage in Code

```python
from app.core.auth import require_permission

@router.post("/orders", dependencies=[Depends(require_permission("orders:create"))])
def create_order(...):
    # Implementation
```

### Authorization Flow

1.  FastAPI receives Bearer JWT.
2.  `get_current_user` validates signature, expiry, and issuer.
3.  `TokenPayload` extracts `realm_roles` and `client_roles` from token claims.
4.  `require_permission` checks if any of the payload's roles exist in the authoritative allowed list for that key.
5.  If not, returns `403 Forbidden`.
