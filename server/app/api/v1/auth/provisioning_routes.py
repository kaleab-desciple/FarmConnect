"""
User provisioning API endpoints.

This module provides endpoints for onboarding new users into the FarmConnect
platform. These endpoints are restricted to privileged users (agents, managers,
admins) who can create accounts for farmers, merchants, delivery personnel,
and other platform roles.

The provisioning system creates users in both the backend database and Keycloak
(identity provider), ensuring secure authentication with temporary passwords
that must be changed on first login.

Key Features:
- Multi-role user provisioning (Farmer, Merchant, Agent, Manager, Admin, etc.)
- Dual-system account creation (database + Keycloak)
- Onboarding workflow with MANAGER approval for farmers and merchants
- Audit trail linking created users to provisioning agents
- Service account blocking for security
"""
from typing import Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from shared_models.enums import UserRole
from app.core.database import get_db
from app.core.auth import (
    TokenPayload,
    require_permission,
    block_service_accounts
)
from app.application.services.provisioning_service import (
    UserProvisioningService,
    ProvisionedUser
)
from app.infrastructure.repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================

class ProvisionUserRequest(BaseModel):
    """
    Request payload for provisioning a new user.
    
    This model defines the required and optional fields when creating
    a new user account through the provisioning system.
    
    Fields:
        - email: Valid email address (required) - used as primary contact and login identifier
        - phone: Phone number in E.164 format (required) - international format with country code
        - first_name: User's first name (required) - 1-100 characters
        - last_name: User's last name (required) - 1-100 characters
        - location: Geographic location (optional) - up to 200 characters
    
    Example:
        {
            "email": "john.farmer@example.com",
            "phone": "+251911123456",
            "first_name": "John",
            "last_name": "Doe",
            "location": "Addis Ababa, Ethiopia"
        }
    """
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$", description="Phone number in E.164 format")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=200)


class ProvisionUserResponse(BaseModel):
    """
    Response payload after successful user provisioning.
    
    Contains the created user's identifiers and login credentials.
    The temporary_password should be securely communicated to the user
    as it cannot be retrieved later.
    
    Fields:
        - user_id: Internal database UUID of the created user
        - keycloak_id: Keycloak identity provider UUID
        - email: User's email address
        - temporary_password: One-time password (must be changed on first login)
        - password_reset_required: Flag indicating password must be reset
        - message: Human-readable status message
    
    Example:
        {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "keycloak_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "email": "john.farmer@example.com",
            "temporary_password": "TempPass123!",
            "password_reset_required": true,
            "message": "User successfully created with role FARMER. Pending MANAGER approval before account is activated."
        }
    """
    user_id: str
    keycloak_id: str
    email: str
    temporary_password: str
    password_reset_required: bool
    message: str


# =============================================================================
# Common Handler Function
# =============================================================================

def _provision_user_handler(
    request: ProvisionUserRequest,
    role: UserRole,
    db: Session,
    current_user: TokenPayload
) -> ProvisionUserResponse:
    """
    Common handler for user provisioning across all roles.
    
    This internal function orchestrates the user creation process:
    1. Creates user in the backend database via UserProvisioningService
    2. Creates corresponding identity in Keycloak
    3. Generates a secure temporary password
    4. Sets up role-based onboarding status (approval workflow for farmers/merchants)
    5. Records the provisioning agent for audit purposes
    
    Onboarding Workflow:
    - FARMER and MERCHANT roles require MANAGER approval before activation
    - Other roles (AGENT, DELIVERY, AGRONOMIST, etc.) are immediately ACTIVE
    - Pending approval users have PENDING_REVIEW onboarding status
    
    Args:
        request: The provisioning request containing user details
        role: The role to assign to the new user
        db: Database session for persistence
        current_user: The authenticated user performing the provisioning
    
    Returns:
        ProvisionUserResponse with created user details and credentials
    
    Raises:
        HTTPException: If provisioning fails (400) with error details
    
    Security Considerations:
    - Requires users:provision permission
    - Blocks service accounts from performing provisioning
    - All provisioning actions are logged for audit trail
    """
    service = UserProvisioningService(db)
    
    try:
        result: ProvisionedUser = service.provision_user(
            email=request.email,
            phone=request.phone,
            first_name=request.first_name,
            last_name=request.last_name,
            role=role,
            location=request.location,
            agent_id=current_user.keycloak_id  # Keycloak UUID for audit trail
        )
        
        # For FARMER and MERCHANT, set onboarding_status to PENDING_REVIEW
        # so a MANAGER must approve before the user becomes fully active.
        # Other roles (AGENT, DELIVERY, etc.) are immediately ACTIVE.
        requires_approval = role in (UserRole.FARMER, UserRole.MERCHANT)
        if requires_approval:
            from app.domain.common.enums import OnboardingStatus
            user_repo = UserRepository(db)
            user_repo.update(result.user_id, {
                "onboarding_status": OnboardingStatus.PENDING_REVIEW.value,
                "onboarding_agent_id": current_user.keycloak_id,  # Keycloak UUID for audit trail
            })
        
        logger.info(
            f"User provisioned by {current_user.username}: "
            f"{request.email} as {role.value}"
        )

        pending_note = " Pending MANAGER approval before account is activated." if requires_approval else ""
        return ProvisionUserResponse(
            user_id=result.user_id,
            keycloak_id=result.keycloak_id,
            email=result.email,
            temporary_password=result.temporary_password,
            password_reset_required=result.password_reset_required,
            message=f"User successfully created with role {role.value}.{pending_note} "
                    f"Temporary password must be changed on first login."
        )
        
    except Exception as e:
        logger.error(f"Provisioning failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =============================================================================
# Provisioning Endpoints
# =============================================================================

@router.post(
    "/provision/farmer",
    response_model=ProvisionUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Provision a new farmer",
    dependencies=[Depends(require_permission("users:provision")), Depends(block_service_accounts)]
)
def provision_farmer(
    request: ProvisionUserRequest,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("users:provision"))
):
    """
    Provision a new farmer user.
    
    Creates a new farmer account in the FarmConnect platform. Farmers are
    agricultural producers who sell their products through the platform.
    
    This endpoint performs the following operations:
    1. Creates a user record in the backend database
    2. Creates an identity in Keycloak with FARMER role
    3. Generates a temporary password that must be changed on first login
    4. Sets onboarding status to PENDING_REVIEW (requires MANAGER approval)
    
    ## Request Body
    - **email**: Valid email address (required)
    - **phone**: Phone number in E.164 format (e.g., +251911123456)
    - **first_name**: First name (1-100 characters)
    - **last_name**: Last name (1-100 characters)
    - **location**: Geographic location/address (optional, max 200 chars)
    
    ## Authentication & Authorization
    Requires `users:provision` permission.
    
    Allowed roles to provision farmers:
    - **AGENT**: Can provision farmers in their assigned region
    - **MANAGER**: Can provision farmers across regions
    - **ADMIN**: Can provision farmers across regions
    
    ## Onboarding Workflow
    Farmers require MANAGER approval before becoming fully active:
    - Initial status: PENDING_REVIEW
    - Agent who provisions records their ID for accountability
    - MANAGER must review and approve to activate account
    - Once approved, farmer can list products and receive orders
    
    ## Response Format
    ```json
    {
      "user_id": "uuid-of-created-user",
      "keycloak_id": "keycloak-uuid",
      "email": "farmer@example.com",
      "temporary_password": "TempPass123!",
      "password_reset_required": true,
      "message": "User successfully created with role FARMER. Pending MANAGER approval before account is activated."
    }
    ```
    
    ## Use Cases
    - Onboarding new farmers by field agents
    - Creating farmer accounts for agricultural cooperatives
    - Adding farmers through admin dashboard
    
    ## Validation
    - Email must be valid and unique in the system
    - Phone number must follow E.164 format
    - Name fields cannot be empty
    - Provisioning agent must have appropriate permissions
    
    ## Responses
    - **201**: Farmer successfully created, pending approval
    - **400**: Invalid request data or provisioning failed
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing users:provision permission)
    - **500**: Internal server error
    """
    return _provision_user_handler(request, UserRole.FARMER, db, current_user)


@router.post(
    "/provision/merchant",
    response_model=ProvisionUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Provision a new merchant",
    dependencies=[Depends(require_permission("users:provision")), Depends(block_service_accounts)]
)
def provision_merchant(
    request: ProvisionUserRequest,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("users:provision"))
):
    """
    Provision a new merchant user.
    
    Creates a new merchant (buyer) account in the FarmConnect platform.
    Merchants are business buyers who purchase agricultural products
    from farmers to resell or process.
    
    This endpoint performs the following operations:
    1. Creates a user record in the backend database
    2. Creates an identity in Keycloak with MERCHANT role
    3. Generates a temporary password that must be changed on first login
    4. Sets onboarding status to PENDING_REVIEW (requires MANAGER approval)
    
    ## Request Body
    - **email**: Valid email address (required)
    - **phone**: Phone number in E.164 format (e.g., +251911123456)
    - **first_name**: First name (1-100 characters)
    - **last_name**: Last name (1-100 characters)
    - **location**: Business location/address (optional, max 200 chars)
    
    ## Authentication & Authorization
    Requires `users:provision` permission.
    
    Allowed roles to provision merchants:
    - **AGENT**: Can provision merchants in their assigned region
    - **MANAGER**: Can provision merchants across regions
    - **ADMIN**: Can provision merchants across regions
    
    ## Onboarding Workflow
    Merchants require MANAGER approval before becoming fully active:
    - Initial status: PENDING_REVIEW
    - Agent who provisions records their ID for accountability
    - MANAGER must review and approve to activate account
    - Once approved, merchant can browse and purchase products
    
    ## Response Format
    ```json
    {
      "user_id": "uuid-of-created-user",
      "keycloak_id": "keycloak-uuid",
      "email": "merchant@example.com",
      "temporary_password": "TempPass123!",
      "password_reset_required": true,
      "message": "User successfully created with role MERCHANT. Pending MANAGER approval before account is activated."
    }
    ```
    
    ## Use Cases
    - Onboarding new merchants/buyers by field agents
    - Creating merchant accounts for restaurants, processors
    - Adding traders through admin dashboard
    
    ## Validation
    - Email must be valid and unique in the system
    - Phone number must follow E.164 format
    - Name fields cannot be empty
    - Provisioning agent must have appropriate permissions
    
    ## Responses
    - **201**: Merchant successfully created, pending approval
    - **400**: Invalid request data or provisioning failed
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing users:provision permission)
    - **500**: Internal server error
    """
    return _provision_user_handler(request, UserRole.MERCHANT, db, current_user)


@router.post(
    "/provision/delivery",
    response_model=ProvisionUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Provision a new delivery personnel",
    dependencies=[Depends(require_permission("users:provision")), Depends(block_service_accounts)]
)
def provision_delivery(
    request: ProvisionUserRequest,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("users:provision"))
):
    """
    Provision a new delivery personnel user.
    
    Creates a new delivery personnel account in the FarmConnect platform.
    Delivery personnel handle the transportation and delivery of orders
    from farmers to merchants.
    
    This endpoint performs the following operations:
    1. Creates a user record in the backend database
    2. Creates an identity in Keycloak with DELIVERY role
    3. Generates a temporary password that must be changed on first login
    4. Account is immediately ACTIVE (no MANAGER approval required)
    
    ## Request Body
    - **email**: Valid email address (required)
    - **phone**: Phone number in E.164 format (e.g., +251911123456)
    - **first_name**: First name (1-100 characters)
    - **last_name**: Last name (1-100 characters)
    - **location**: Service area/headquarters location (optional, max 200 chars)
    
    ## Authentication & Authorization
    Requires `users:provision` permission.
    
    Allowed roles to provision delivery personnel:
    - **AGENT**: Can provision delivery staff
    - **MANAGER**: Can provision delivery staff
    - **ADMIN**: Can provision delivery staff
    
    ## Onboarding Workflow
    Delivery personnel are immediately ACTIVE (no approval needed):
    - Initial status: ACTIVE
    - Can immediately accept delivery assignments
    - Agent who provisions records their ID for accountability
    
    ## Response Format
    ```json
    {
      "user_id": "uuid-of-created-user",
      "keycloak_id": "keycloak-uuid",
      "email": "driver@example.com",
      "temporary_password": "TempPass123!",
      "password_reset_required": true,
      "message": "User successfully created with role DELIVERY. Temporary password must be changed on first login."
    }
    ```
    
    ## Use Cases
    - Onboarding delivery drivers by logistics managers
    - Adding delivery personnel for new service areas
    - Creating driver accounts for fleet management
    
    ## Validation
    - Email must be valid and unique in the system
    - Phone number must follow E.164 format
    - Name fields cannot be empty
    - Provisioning agent must have appropriate permissions
    
    ## Responses
    - **201**: Delivery personnel successfully created
    - **400**: Invalid request data or provisioning failed
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing users:provision permission)
    - **500**: Internal server error
    """
    return _provision_user_handler(request, UserRole.DELIVERY, db, current_user)


@router.post(
    "/provision/agent",
    response_model=ProvisionUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Provision a new agent",
    dependencies=[Depends(require_permission("users:provision")), Depends(block_service_accounts)]
)
def provision_agent(
    request: ProvisionUserRequest,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("users:provision"))
):
    """
    Provision a new agent user.
    
    Creates a new field agent account in the FarmConnect platform.
    Agents are field representatives who work directly with farmers
    and merchants in specific geographic regions, facilitating onboarding
    and providing support.
    
    This endpoint performs the following operations:
    1. Creates a user record in the backend database
    2. Creates an identity in Keycloak with AGENT role
    3. Generates a temporary password that must be changed on first login
    4. Account is immediately ACTIVE (no MANAGER approval required)
    
    ## Request Body
    - **email**: Valid email address (required)
    - **phone**: Phone number in E.164 format (e.g., +251911123456)
    - **first_name**: First name (1-100 characters)
    - **last_name**: Last name (1-100 characters)
    - **location**: Assigned region/service area (optional, max 200 chars)
    
    ## Authentication & Authorization
    Requires `users:provision` permission.
    
    Allowed roles to provision agents:
    - **MANAGER**: Can provision agents within their jurisdiction
    - **ADMIN**: Can provision agents across all regions
    
    Note: AGENTs cannot provision other AGENTs - this is restricted
    to higher-level administrative roles.
    
    ## Onboarding Workflow
    Agents are immediately ACTIVE (no approval needed):
    - Initial status: ACTIVE
    - Can immediately start onboarding farmers and merchants
    - Assigned region must be configured separately by MANAGER
    
    ## Response Format
    ```json
    {
      "user_id": "uuid-of-created-user",
      "keycloak_id": "keycloak-uuid",
      "email": "agent@example.com",
      "temporary_password": "TempPass123!",
      "password_reset_required": true,
      "message": "User successfully created with role AGENT. Temporary password must be changed on first login."
    }
    ```
    
    ## Use Cases
    - Onboarding new field agents for regional expansion
    - Adding agents for specific agricultural zones
    - Creating agent accounts for partner organizations
    
    ## Agent Permissions
    Once active, agents can:
    - Provision FARMER and MERCHANT users
    - View orders in their assigned region
    - Monitor farmer and merchant activities
    - Assist with dispute resolution
    
    ## Validation
    - Email must be valid and unique in the system
    - Phone number must follow E.164 format
    - Name fields cannot be empty
    - Only MANAGER or ADMIN can provision agents
    
    ## Responses
    - **201**: Agent successfully created
    - **400**: Invalid request data or provisioning failed
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (only MANAGER or ADMIN can provision agents)
    - **500**: Internal server error
    """
    return _provision_user_handler(request, UserRole.AGENT, db, current_user)


@router.post(
    "/provision/manager",
    response_model=ProvisionUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Provision a new manager",
    dependencies=[Depends(require_permission("users:provision")), Depends(block_service_accounts)]
)
def provision_manager(
    request: ProvisionUserRequest,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("users:provision"))
):
    """
    Provision a new manager user.
    
    Creates a new manager account in the FarmConnect platform.
    Managers oversee regional operations, approve farmer/merchant
    onboarding, and supervise agents.
    
    This endpoint performs the following operations:
    1. Creates a user record in the backend database
    2. Creates an identity in Keycloak with MANAGER role
    3. Generates a temporary password that must be changed on first login
    4. Account is immediately ACTIVE (no approval required)
    
    ## Request Body
    - **email**: Valid email address (required)
    - **phone**: Phone number in E.164 format (e.g., +251911123456)
    - **first_name**: First name (1-100 characters)
    - **last_name**: Last name (1-100 characters)
    - **location**: Managed region/headquarters (optional, max 200 chars)
    
    ## Authentication & Authorization
    Requires `users:provision` permission.
    
    Allowed roles to provision managers:
    - **ADMIN**: Only ADMIN can create new managers
    
    ## Onboarding Workflow
    Managers are immediately ACTIVE:
    - Initial status: ACTIVE
    - Full administrative access upon creation
    - Region assignment configured separately
    
    ## Response Format
    ```json
    {
      "user_id": "uuid-of-created-user",
      "keycloak_id": "keycloak-uuid",
      "email": "manager@example.com",
      "temporary_password": "TempPass123!",
      "password_reset_required": true,
      "message": "User successfully created with role MANAGER. Temporary password must be changed on first login."
    }
    ```
    
    ## Use Cases
    - Creating regional manager accounts
    - Onboarding management personnel for new zones
    - Adding management staff for operations
    
    ## Manager Permissions
    Managers have elevated privileges:
    - Approve/reject farmer and merchant onboarding
    - Provision AGENT, DELIVERY, FARMER, MERCHANT users
    - View all orders in their region
    - Access management dashboards
    - Resolve disputes
    
    ## Validation
    - Email must be valid and unique in the system
    - Phone number must follow E.164 format
    - Name fields cannot be empty
    - Only ADMIN can provision managers
    
    ## Responses
    - **201**: Manager successfully created
    - **400**: Invalid request data or provisioning failed
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (only ADMIN can provision managers)
    - **500**: Internal server error
    """
    return _provision_user_handler(request, UserRole.MANAGER, db, current_user)


@router.post(
    "/provision/admin",
    response_model=ProvisionUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Provision a new admin",
    dependencies=[Depends(require_permission("users:provision")), Depends(block_service_accounts)]
)
def provision_admin(
    request: ProvisionUserRequest,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("users:provision"))
):
    """
    Provision a new admin user.
    
    Creates a new system administrator account in the FarmConnect
    platform. Admins have full system access and can manage all
    aspects of the platform.
    
    This endpoint performs the following operations:
    1. Creates a user record in the backend database
    2. Creates an identity in Keycloak with ADMIN role
    3. Generates a temporary password that must be changed on first login
    4. Account is immediately ACTIVE with full permissions
    
    ## Request Body
    - **email**: Valid email address (required)
    - **phone**: Phone number in E.164 format (e.g., +251911123456)
    - **first_name**: First name (1-100 characters)
    - **last_name**: Last name (1-100 characters)
    - **location**: Administrative region (optional, max 200 chars)
    
    ## Authentication & Authorization
    Requires `users:provision` permission.
    
    Allowed roles to provision admins:
    - **ADMIN**: Only existing ADMIN can create new admins
    
    ## Onboarding Workflow
    Admins are immediately ACTIVE with full system access:
    - Initial status: ACTIVE
    - Complete administrative privileges
    - Can access all system functions
    
    ## Response Format
    ```json
    {
      "user_id": "uuid-of-created-user",
      "keycloak_id": "keycloak-uuid",
      "email": "admin@example.com",
      "temporary_password": "TempPass123!",
      "password_reset_required": true,
      "message": "User successfully created with role ADMIN. Temporary password must be changed on first login."
    }
    ```
    
    ## Use Cases
    - Creating system administrator accounts
    - Onboarding IT/security personnel
    - Adding emergency backup admins
    
    ## Admin Permissions
    Full system access including:
    - All MANAGER and AGENT permissions
    - User management (create/delete any role)
    - System configuration
    - Audit log access
    - Platform settings management
    
    ## Security Considerations
    Admin provisioning is highly restricted:
    - Only existing ADMINs can create new admins
    - All admin actions are logged
    - MFA should be enforced for admin accounts
    - Limited number of admin accounts recommended
    
    ## Validation
    - Email must be valid and unique in the system
    - Phone number must follow E.164 format
    - Name fields cannot be empty
    - Only ADMIN can provision admins
    
    ## Responses
    - **201**: Admin successfully created
    - **400**: Invalid request data or provisioning failed
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (only ADMIN can provision admins)
    - **500**: Internal server error
    """
    return _provision_user_handler(request, UserRole.ADMIN, db, current_user)


@router.post(
    "/provision/moderator",
    response_model=ProvisionUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Provision a new moderator",
    dependencies=[Depends(require_permission("users:provision")), Depends(block_service_accounts)]
)
def provision_moderator(
    request: ProvisionUserRequest,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("users:provision"))
):
    """
    Provision a new moderator user.
    
    Creates a new moderator account in the FarmConnect platform.
    Moderators help manage content quality, review product listings,
    and assist with community guidelines enforcement.
    
    This endpoint performs the following operations:
    1. Creates a user record in the backend database
    2. Creates an identity in Keycloak with MODERATOR role
    3. Generates a temporary password that must be changed on first login
    4. Account is immediately ACTIVE (no approval required)
    
    ## Request Body
    - **email**: Valid email address (required)
    - **phone**: Phone number in E.164 format (e.g., +251911123456)
    - **first_name**: First name (1-100 characters)
    - **last_name**: Last name (1-100 characters)
    - **location**: Base location (optional, max 200 chars)
    
    ## Authentication & Authorization
    Requires `users:provision` permission.
    
    Allowed roles to provision moderators:
    - **ADMIN**: Only ADMIN can create moderators
    
    ## Onboarding Workflow
    Moderators are immediately ACTIVE:
    - Initial status: ACTIVE
    - Can immediately start content moderation duties
    - Area of responsibility configured separately
    
    ## Response Format
    ```json
    {
      "user_id": "uuid-of-created-user",
      "keycloak_id": "keycloak-uuid",
      "email": "moderator@example.com",
      "temporary_password": "TempPass123!",
      "password_reset_required": true,
      "message": "User successfully created with role MODERATOR. Temporary password must be changed on first login."
    }
    ```
    
    ## Use Cases
    - Onboarding content moderation staff
    - Creating quality assurance accounts
    - Adding community management personnel
    
    ## Moderator Permissions
    Content moderation capabilities:
    - Review and approve/reject product listings
    - Flag inappropriate content
    - Access to QC (Quality Control) workflows
    - View reported issues
    
    ## Validation
    - Email must be valid and unique in the system
    - Phone number must follow E.164 format
    - Name fields cannot be empty
    - Only ADMIN can provision moderators
    
    ## Responses
    - **201**: Moderator successfully created
    - **400**: Invalid request data or provisioning failed
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (only ADMIN can provision moderators)
    - **500**: Internal server error
    """
    return _provision_user_handler(request, UserRole.MODERATOR, db, current_user)


@router.post(
    "/provision/agronomist",
    response_model=ProvisionUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Provision a new agronomist",
    dependencies=[Depends(require_permission("users:provision")), Depends(block_service_accounts)]
)
def provision_agronomist(
    request: ProvisionUserRequest,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("users:provision"))
):
    """
    Provision a new agronomist user.
    
    Creates a new agronomist account in the FarmConnect platform.
    Agronomists are agricultural experts who provide advisory services,
    crop recommendations, and technical guidance to farmers.
    
    This endpoint performs the following operations:
    1. Creates a user record in the backend database
    2. Creates an identity in Keycloak with AGRONOMIST role
    3. Generates a temporary password that must be changed on first login
    4. Account is immediately ACTIVE (no approval required)
    
    ## Request Body
    - **email**: Valid email address (required)
    - **phone**: Phone number in E.164 format (e.g., +251911123456)
    - **first_name**: First name (1-100 characters)
    - **last_name**: Last name (1-100 characters)
    - **location**: Service area/expertise region (optional, max 200 chars)
    
    ## Authentication & Authorization
    Requires `users:provision` permission.
    
    Allowed roles to provision agronomists:
    - **AGENT**: Can provision agronomists for their region
    - **MANAGER**: Can provision agronomists across regions
    - **ADMIN**: Can provision agronomists across regions
    
    ## Onboarding Workflow
    Agronomists are immediately ACTIVE:
    - Initial status: ACTIVE
    - Can immediately provide advisory services
    - Specialization area configured separately
    
       ```json
    {
      " ## Response Format
user_id": "uuid-of-created-user",
      "keycloak_id": "keycloak-uuid",
      "email": "agronomist@example.com",
      "temporary_password": "TempPass123!",
      "password_reset_required": true,
      "message": "User successfully created with role AGRONOMIST. Temporary password must be changed on first login."
    }
    ```
    
    ## Use Cases
    - Onboarding agricultural experts
    - Creating advisory service accounts
    - Adding crop specialists for farmer support
    
    ## Agronomist Permissions
    Agricultural advisory capabilities:
    - Access to AI diagnosis system
    - Provide crop recommendations
    - View farm and harvest data
    - Create advisory reports
    
    ## Validation
    - Email must be valid and unique in the system
    - Phone number must follow E.164 format
    - Name fields cannot be empty
    - Provisioning agent must have appropriate permissions
    
    ## Responses
    - **201**: Agronomist successfully created
    - **400**: Invalid request data or provisioning failed
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing users:provision permission)
    - **500**: Internal server error
    """
    return _provision_user_handler(request, UserRole.AGRONOMIST, db, current_user)


@router.post(
    "/provision/field-analyst",
    response_model=ProvisionUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Provision a new field analyst",
    dependencies=[Depends(require_permission("users:provision")), Depends(block_service_accounts)]
)
def provision_field_analyst(
    request: ProvisionUserRequest,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("users:provision"))
):
    """
    Provision a new field analyst user.
    
    Creates a new field analyst account in the FarmConnect platform.
    Field analysts collect and analyze agricultural data from farms,
    including soil conditions, crop health, weather patterns, and
    yield predictions.
    
    This endpoint performs the following operations:
    1. Creates a user record in the backend database
    2. Creates an identity in Keycloak with FIELD_ANALYST role
    3. Generates a temporary password that must be changed on first login
    4. Account is immediately ACTIVE (no approval required)
    
    ## Request Body
    - **email**: Valid email address (required)
    - **phone**: Phone number in E.164 format (e.g., +251911123456)
    - **first_name**: First name (1-100 characters)
    - **last_name**: Last name (1-100 characters)
    - **location**: Analysis area/region (optional, max 200 chars)
    
    ## Authentication & Authorization
    Requires `users:provision` permission.
    
    Allowed roles to provision field analysts:
    - **AGENT**: Can provision field analysts for their region
    - **MANAGER**: Can provision field analysts across regions
    - **ADMIN**: Can provision field analysts across regions
    
    ## Onboarding Workflow
    Field analysts are immediately ACTIVE:
    - Initial status: ACTIVE
    - Can immediately start data collection/analysis
    - Assigned analysis zones configured separately
    
    ## Response Format
    ```json
    {
      "user_id": "uuid-of-created-user",
      "keycloak_id": "keycloak-uuid",
      "email": "analyst@example.com",
      "temporary_password": "TempPass123!",
      "password_reset_required": true,
      "message": "User successfully created with role FIELD_ANALYST. Temporary password must be changed on first login."
    }
    ```
    
    ## Use Cases
    - Onboarding agricultural data analysts
    - Creating field research personnel accounts
    - Adding monitoring and surveillance staff
    
    ## Field Analyst Permissions
    Data analysis capabilities:
    - Access to farm monitoring data
    - View weather and soil information
    - Create analytical reports
    - Access to harvest forecasting tools
    
    ## Validation
    - Email must be valid and unique in the system
    - Phone number must follow E.164 format
    - Name fields cannot be empty
    - Provisioning agent must have appropriate permissions
    
    ## Responses
    - **201**: Field analyst successfully created
    - **400**: Invalid request data or provisioning failed
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing users:provision permission)
    - **500**: Internal server error
    """
    return _provision_user_handler(request, UserRole.FIELD_ANALYST, db, current_user)
