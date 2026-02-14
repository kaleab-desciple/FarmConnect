"""
User provisioning service for onboarding farmers, merchants, and delivery personnel.
"""
from typing import Optional
import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from shared_models.user import User
from shared_models.enums import UserRole
from app.infrastructure.repositories.user_repo import UserRepository
from app.infrastructure.external.keycloak_admin import (
    get_keycloak_admin,
    generate_temporary_password
)

logger = logging.getLogger(__name__)


@dataclass
class ProvisionedUser:
    """Result of user provisioning operation."""
    user_id: str  # Backend user ID
    keycloak_id: str  # Keycloak user ID
    email: str
    temporary_password: str
    password_reset_required: bool = True


class UserProvisioningService:
    """Service for provisioning new users in both backend and Keycloak."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.keycloak_admin = get_keycloak_admin()
    
    def provision_user(
        self,
        email: str,
        phone: str,
        first_name: str,
        last_name: str,
        role: UserRole,
        location: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> ProvisionedUser:
        """
        Provision a new user in both backend database and Keycloak.
        
        This is a transactional operation - if either step fails, both are rolled back.
        
        Args:
            email: User's email address
            phone: User's phone number
            first_name: User's first name
            last_name: User's last name
            role: User's role (FARMER, MERCHANT, DELIVERY)
            location: Optional location/address
            agent_id: ID of the agent creating this user
            
        Returns:
            ProvisionedUser with credentials
            
        Raises:
            Exception: If provisioning fails
        """
        keycloak_user_id = None
        backend_user_id = None
        
        try:
            # Step 1: Create user in Keycloak (Move to Step 1 to get ID first)
            logger.info(f"Creating user in Keycloak: {email}")
            keycloak_user_id = self.keycloak_admin.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                enabled=True,
                email_verified=False
            )

            # Step 2: Create user in backend database with Keycloak ID
            logger.info(f"Provisioning user in DB: {email} with role {role.value}")
            from shared_models.user import UserRole as ModelUserRole
            
            user = User(
                email=email,
                phone=phone,
                name=f"{first_name} {last_name}",
                role=ModelUserRole(role.value),
                keycloak_id=keycloak_user_id,  # Save the link!
                metadata={"location": location} if location else None
            )
            
            # Save to database (this will trigger ID generation in repo.save)
            try:
                self.user_repo.save(user)
                backend_user_id = user.id
                logger.info(f"Created user in database: {backend_user_id}")
            except IntegrityError as e:
                # ... keeps original integrity error handling ...
                error_msg = str(e.orig)
                if "users_phone_key" in error_msg:
                    raise Exception(f"User with phone number {phone} already exists")
                if "users_email_key" in error_msg:
                    raise Exception(f"User with email {email} already exists")
                raise Exception(f"Database error: {error_msg}")
            except Exception as e:
                # Catch other potential errors (like missing sequence)
                if "user_id_seq" in str(e):
                    logger.warning("user_id_seq missing, falling back to UUID")
                    import uuid
                    user.id = str(uuid.uuid4())
                    self.user_repo.save(user)
                    backend_user_id = user.id
                else:
                    raise e
            
            # Step 3: Assign to appropriate group
            group_name = self._get_group_name(role)
            self.keycloak_admin.assign_to_group(keycloak_user_id, group_name)
            
            # Step 4: Generate and set temporary password
            temp_password = generate_temporary_password()
            self.keycloak_admin.set_temporary_password(
                keycloak_user_id,
                temp_password,
                temporary=True
            )
            
            # Commit database transaction
            self.db.commit()
            
            logger.info(
                f"Successfully provisioned user {email} "
                f"(Backend: {backend_user_id}, Keycloak: {keycloak_user_id})"
            )
            
            return ProvisionedUser(
                user_id=backend_user_id,
                keycloak_id=keycloak_user_id,
                email=email,
                temporary_password=temp_password,
                password_reset_required=True
            )
            
        except Exception as e:
            # Rollback on any error
            logger.error(f"User provisioning failed: {e}")
            
            # Rollback database
            self.db.rollback()
            
            # Attempt to clean up Keycloak user if created
            if keycloak_user_id:
                try:
                    logger.info(f"Rolling back Keycloak user: {keycloak_user_id}")
                    self.keycloak_admin.delete_user(keycloak_user_id)
                except Exception as cleanup_error:
                    logger.error(f"Failed to cleanup Keycloak user: {cleanup_error}")
            
            raise Exception(f"User provisioning failed: {e}")
    
    def _get_group_name(self, role: UserRole) -> str:
        """Map role to Keycloak group name."""
        role_to_group = {
            UserRole.FARMER: "Farmers",
            UserRole.MERCHANT: "Merchants",
            UserRole.DELIVERY: "Delivery",
            UserRole.AGENT: "Agents",
            UserRole.MANAGER: "Managers",
            UserRole.ADMIN: "Admins",
            UserRole.MODERATOR: "Moderators",
            UserRole.AGRONOMIST: "Agronomists",
            UserRole.FIELD_ANALYST: "FieldAnalysts"
        }
        
        group = role_to_group.get(role)
        if not group:
            raise ValueError(f"Unknown role: {role}")
        
        return group
