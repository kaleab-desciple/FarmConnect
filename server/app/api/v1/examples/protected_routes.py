"""
Example protected endpoints demonstrating authentication and authorization.

This file shows how to protect endpoints with different role requirements.
Copy these patterns to other route files as needed.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.auth import (
    TokenPayload,
    get_current_user,
    require_realm_role,
    require_client_role,
    require_permission,
    block_service_accounts,
    require_service_account
)

router = APIRouter()


class ExampleResponse(BaseModel):
    """Example response model."""
    message: str
    user_info: dict


# Example 1: Endpoint requiring mapping to realm roles (Human-only)
@router.get(
    "/protected/realm-only",
    summary="Realm-only endpoint",
    dependencies=[Depends(require_realm_role("AGENT", "MANAGER", "ADMIN"))]
)
def realm_only_endpoint(current_user: TokenPayload = Depends(require_realm_role("AGENT", "MANAGER", "ADMIN"))):
    return {
        "message": "Hello Human!",
        "your_realm_roles": current_user.realm_roles
    }


# Example 2: Endpoint requiring client roles (Machine-only)
@router.get(
    "/protected/client-only",
    summary="Client-only endpoint",
    dependencies=[Depends(require_permission("system:maintenance"))]
)
def client_only_endpoint(current_user: TokenPayload = Depends(require_permission("system:maintenance"))):
    return {
        "message": "Hello Service Account!",
        "your_client_roles": current_user.client_roles
    }


# Example 3: Endpoint requiring specific permission (Unified)
@router.post(
    "/protected/create-order",
    summary="Create order (permission-based)",
    description="Uses require_permission('orders:create')",
    dependencies=[Depends(require_permission("orders:create"))]
)
def create_order_endpoint(
    current_user: TokenPayload = Depends(require_permission("orders:create"))
):
    """
    Example of permission-based authorization.
    Works for both Realm Roles and Client Roles if they are in the matrix.
    """
    return {
        "message": "Operation authorized via permission",
        "user": current_user.username,
        "roles_used": current_user.all_roles
    }


# Example 4: Endpoint blocking service accounts
@router.get(
    "/protected/user-only",
    summary="User-only endpoint",
    description="Blocks service accounts",
    dependencies=[Depends(block_service_accounts)]
)
def user_only_endpoint(current_user: TokenPayload = Depends(block_service_accounts)):
    return {
        "message": "Hello Human User!",
        "realm_roles": current_user.realm_roles
    }


# Example 5: Service account only endpoint
@router.post(
    "/protected/internal-only",
    summary="Internal-only endpoint",
    description="Requires service account",
    dependencies=[Depends(require_permission("system:maintenance"))]
)
def internal_only_endpoint(current_user: TokenPayload = Depends(require_permission("system:maintenance"))):
    return {
        "message": "Hello Machine!",
        "client_roles": current_user.client_roles
    }


# Example 6: Custom authorization logic
@router.get(
    "/protected/custom/{resource_id}",
    summary="Custom authorization example",
    description="Demonstrates custom authorization logic"
)
def custom_authorization_endpoint(
    resource_id: str,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Example of custom authorization logic.
    Business rules:
    - Admins can access any resource
    - Other users can only access their own resources
    """
    # Admins have full access
    if current_user.has_realm_role("ADMIN"):
        return {
            "message": f"Admin access to resource {resource_id}",
            "resource_id": resource_id,
            "access_type": "admin"
        }
    
    # Other users can only access their own resources
    if resource_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own resources"
        )
    
    return {
        "message": f"User access to own resource",
        "resource_id": resource_id,
        "user_id": current_user.user_id,
        "access_type": "owner"
    }


# Example 7: Multiple role requirements
@router.delete(
    "/protected/critical-operation",
    summary="Critical operation",
    description="Requires both ADMIN and MANAGER roles"
)
def critical_operation_endpoint(current_user: TokenPayload = Depends(get_current_user)):
    required_roles = ["ADMIN", "MANAGER"]
    
    if not all(role in current_user.realm_roles for role in required_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This operation requires all of: {', '.join(required_roles)}"
        )
    
    return {
        "message": "Critical operation authorized",
        "user": current_user.username,
        "realm_roles": current_user.realm_roles
    }
