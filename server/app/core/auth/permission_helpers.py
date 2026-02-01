"""
Permission Helper Functions for Access Control.

These functions provide convenient ways to check permissions
and enforce access control in API endpoints.
"""

from typing import List, Optional
from fastapi import HTTPException, status


def has_permission(user_roles: List[str], permission_key: str, permissions_matrix: dict) -> bool:
    """
    Check if any of the user's roles have the specified permission.
    
    Args:
        user_roles: List of roles assigned to the user
        permission_key: The permission to check (e.g., "farms:read:own")
        permissions_matrix: The PERMISSIONS dictionary
        
    Returns:
        True if user has permission, False otherwise
    """
    if permission_key not in permissions_matrix:
        return False
    
    allowed_roles = permissions_matrix[permission_key]
    return any(role in allowed_roles for role in user_roles)


def require_permission(user_roles: List[str], permission_key: str, permissions_matrix: dict) -> None:
    """
    Raise HTTPException if user doesn't have the specified permission.
    
    Args:
        user_roles: List of roles assigned to the user
        permission_key: The permission to check
        permissions_matrix: The PERMISSIONS dictionary
        
    Raises:
        HTTPException: 403 Forbidden if permission denied
    """
    if not has_permission(user_roles, permission_key, permissions_matrix):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required: {permission_key}"
        )


def check_resource_access(
    user_id: str,
    user_roles: List[str],
    resource_owner_id: str,
    assigned_user_ids: Optional[List[str]],
    permission_base: str,
    permissions_matrix: dict
) -> str:
    """
    Determine the access level for a resource based on ownership and assignments.
    
    Args:
        user_id: The current user's ID
        user_roles: List of roles assigned to the user
        resource_owner_id: The ID of the resource owner
        assigned_user_ids: List of user IDs assigned to this resource (for AGRONOMIST access)
        permission_base: Base permission key (e.g., "farms:read")
        permissions_matrix: The PERMISSIONS dictionary
        
    Returns:
        The specific permission level: "own", "assigned", or "all"
        
    Raises:
        HTTPException: 403 Forbidden if no access
    """
    # Check for "all" access first (ADMIN, FIELD_ANALYST)
    if has_permission(user_roles, f"{permission_base}:all", permissions_matrix):
        return "all"
    
    # Check for "own" access (FARMER owns the resource)
    if user_id == resource_owner_id and has_permission(user_roles, f"{permission_base}:own", permissions_matrix):
        return "own"
    
    # Check for "assigned" access (AGRONOMIST assigned to the resource)
    if assigned_user_ids and user_id in assigned_user_ids:
        if has_permission(user_roles, f"{permission_base}:assigned", permissions_matrix):
            return "assigned"
    
    # No access
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this resource"
    )


def can_modify_resource(
    user_id: str,
    user_roles: List[str],
    resource_owner_id: str,
    assigned_user_ids: Optional[List[str]],
    operation: str,  # "update" or "delete"
    resource_type: str,  # "farms", "fields", "crop_cycles", etc.
    permissions_matrix: dict
) -> bool:
    """
    Check if user can modify (update/delete) a resource.
    
    Args:
        user_id: The current user's ID
        user_roles: List of roles assigned to the user
        resource_owner_id: The ID of the resource owner
        assigned_user_ids: List of user IDs assigned to this resource
        operation: "update" or "delete"
        resource_type: Type of resource (e.g., "farms", "fields")
        permissions_matrix: The PERMISSIONS dictionary
        
    Returns:
        True if user can modify, False otherwise
    """
    permission_base = f"{resource_type}:{operation}"
    
    # Check for "all" access (ADMIN)
    if has_permission(user_roles, f"{permission_base}:all", permissions_matrix):
        return True
    
    # Check for "own" access (FARMER owns the resource)
    if user_id == resource_owner_id and has_permission(user_roles, f"{permission_base}:own", permissions_matrix):
        return True
    
    # Check for "assigned" access (AGRONOMIST for crop_cycles updates only)
    if resource_type == "crop_cycles" and operation == "update":
        if assigned_user_ids and user_id in assigned_user_ids:
            if has_permission(user_roles, f"{permission_base}:assigned", permissions_matrix):
                return True
    
    return False
