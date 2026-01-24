"""
User provisioning API endpoints.
Allows agents, managers, and admins to onboard new users.
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

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response models
class ProvisionUserRequest(BaseModel):
    """Request to provision a new user."""
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$", description="Phone number in E.164 format")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=200)


class ProvisionUserResponse(BaseModel):
    """Response after successful user provisioning."""
    user_id: str
    keycloak_id: str
    email: str
    temporary_password: str
    password_reset_required: bool
    message: str


def _provision_user_handler(
    request: ProvisionUserRequest,
    role: UserRole,
    db: Session,
    current_user: TokenPayload
) -> ProvisionUserResponse:
    """Common handler for user provisioning."""
    service = UserProvisioningService(db)
    
    try:
        result: ProvisionedUser = service.provision_user(
            email=request.email,
            phone=request.phone,
            first_name=request.first_name,
            last_name=request.last_name,
            role=role,
            location=request.location,
            agent_id=current_user.user_id
        )
        
        logger.info(
            f"User provisioned by {current_user.username}: "
            f"{request.email} as {role.value}"
        )
        
        return ProvisionUserResponse(
            user_id=result.user_id,
            keycloak_id=result.keycloak_id,
            email=result.email,
            temporary_password=result.temporary_password,
            password_reset_required=result.password_reset_required,
            message=f"User successfully created with role {role.value}. "
                    f"Temporary password must be changed on first login."
        )
        
    except Exception as e:
        logger.error(f"Provisioning failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


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
    
    Creates the user in both the backend database and Keycloak,
    assigns FARMER role, and generates a temporary password.
    
    **Required Roles:** AGENT, MANAGER, or ADMIN
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
    
    Creates the user in both the backend database and Keycloak,
    assigns MERCHANT role, and generates a temporary password.
    
    **Required Roles:** AGENT, MANAGER, or ADMIN
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
    
    Creates the user in both the backend database and Keycloak,
    assigns DELIVERY role, and generates a temporary password.
    
    **Required Roles:** AGENT, MANAGER, or ADMIN
    """
    return _provision_user_handler(request, UserRole.DELIVERY, db, current_user)
