"""
Keycloak Admin API client for user provisioning.
"""
from typing import Optional, Dict, Any
import logging
import secrets
import string

from keycloak import KeycloakAdmin, KeycloakError
from keycloak.exceptions import KeycloakGetError, KeycloakPostError

from app.core.config import settings

logger = logging.getLogger(__name__)


class KeycloakAdminClient:
    """Wrapper for Keycloak Admin API operations."""
    
    def __init__(self):
        """Initialize Keycloak admin client."""
        self._admin = None
    
    @property
    def admin(self) -> KeycloakAdmin:
        """Lazy initialization of admin client."""
        if self._admin is None:
            try:
                self._admin = KeycloakAdmin(
                    server_url=settings.KEYCLOAK_URL,
                    username=settings.KEYCLOAK_ADMIN_USER,
                    password=settings.KEYCLOAK_ADMIN_PASSWORD,
                    realm_name=settings.KEYCLOAK_REALM,
                    user_realm_name="master",
                    verify=True,
                    timeout=30
                )
                logger.info("Keycloak admin client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Keycloak admin client: {e}")
                raise Exception(f"Keycloak admin initialization failed: {e}")
        
        return self._admin
    
    def create_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        enabled: bool = True,
        email_verified: bool = False
    ) -> str:
        """
        Create a new user in Keycloak.
        
        Args:
            email: User's email address (used as username)
            first_name: User's first name
            last_name: User's last name
            phone: Optional phone number
            enabled: Whether user account is enabled
            email_verified: Whether email is pre-verified
            
        Returns:
            Keycloak user ID
            
        Raises:
            Exception: If user creation fails
        """
        user_data = {
            "username": email,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "enabled": enabled,
            "emailVerified": email_verified,
        }
        
        # Add phone as user attribute if provided
        if phone:
            user_data["attributes"] = {
                "phone": [phone]
            }
        
        try:
            user_id = self.admin.create_user(user_data)
            logger.info(f"Created user in Keycloak: {email} (ID: {user_id})")
            return user_id
        except KeycloakPostError as e:
            error_msg = str(e)
            if "User exists" in error_msg or "409" in error_msg:
                logger.warning(f"User already exists in Keycloak: {email}")
                raise Exception(f"User with email {email} already exists in Keycloak")
            logger.error(f"Failed to create user in Keycloak: {e}")
            raise Exception(f"User creation failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating user: {e}")
            raise Exception(f"User creation failed: {e}")
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address.
        
        Args:
            email: User's email
            
        Returns:
            User data dict or None if not found
        """
        try:
            users = self.admin.get_users({"email": email})
            if users:
                return users[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None
    
    def assign_to_group(self, user_id: str, group_name: str):
        """
        Assign user to a group (which grants roles).
        
        Args:
            user_id: Keycloak user ID
            group_name: Name of the group (e.g., "Farmers", "Merchants")
            
        Raises:
            Exception: If group assignment fails
        """
        try:
            # Get group by name
            groups = self.admin.get_groups({"search": group_name})
            
            if not groups:
                raise Exception(f"Group '{group_name}' not found in Keycloak")
            
            group_id = groups[0]["id"]
            
            # Add user to group
            self.admin.group_user_add(user_id, group_id)
            logger.info(f"Added user {user_id} to group {group_name}")
            
        except Exception as e:
            logger.error(f"Failed to assign user to group: {e}")
            raise Exception(f"Group assignment failed: {e}")
    
    def set_temporary_password(
        self, 
        user_id: str, 
        password: str,
        temporary: bool = True
    ):
        """
        Set user password (temporary by default, requires reset on first login).
        
        Args:
            user_id: Keycloak user ID
            password: Password to set
            temporary: If True, user must reset password on first login
            
        Raises:
            Exception: If password setting fails
        """
        try:
            self.admin.set_user_password(
                user_id=user_id,
                password=password,
                temporary=temporary
            )
            logger.info(f"Set {'temporary' if temporary else 'permanent'} password for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to set user password: {e}")
            raise Exception(f"Password setting failed: {e}")
    
    def delete_user(self, user_id: str):
        """
        Delete a user from Keycloak.
        
        Args:
            user_id: Keycloak user ID
            
        Raises:
            Exception: If deletion fails
        """
        try:
            self.admin.delete_user(user_id)
            logger.info(f"Deleted user {user_id} from Keycloak")
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            raise Exception(f"User deletion failed: {e}")
    
    def send_verify_email(self, user_id: str):
        """
        Send email verification email to user.
        
        Args:
            user_id: Keycloak user ID
        """
        try:
            self.admin.send_verify_email(user_id)
            logger.info(f"Sent verification email to user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to send verification email: {e}")


def generate_temporary_password(length: int = 12) -> str:
    """
    Generate a secure temporary password.
    
    Args:
        length: Password length (minimum 12)
        
    Returns:
        Random password string
    """
    if length < 12:
        length = 12
    
    # Ensure password has mix of characters
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    # Ensure at least one of each type
    if not any(c.isupper() for c in password):
        password = password[:-1] + secrets.choice(string.ascii_uppercase)
    if not any(c.islower() for c in password):
        password = password[:-2] + secrets.choice(string.ascii_lowercase) + password[-1]
    if not any(c.isdigit() for c in password):
        password = password[:-3] + secrets.choice(string.digits) + password[-2:]
    
    return password


# Global admin client instance
_admin_client: Optional[KeycloakAdminClient] = None


def get_keycloak_admin() -> KeycloakAdminClient:
    """Get or create the global Keycloak admin client instance."""
    global _admin_client
    if _admin_client is None:
        _admin_client = KeycloakAdminClient()
    return _admin_client
