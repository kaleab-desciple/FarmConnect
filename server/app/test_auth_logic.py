import os
import sys
import logging
from uuid import uuid4
from datetime import datetime

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.insert(0, os.path.join(current_dir, "../../shared/py"))

# Mock imports for testing
from app.core.config import settings
from app.core.auth.dependencies import TokenPayload
from app.infrastructure.db.session import get_session
from app.api.v1.advisory.forums.service import ForumService
from app.infrastructure.repositories.user_repo import UserRepository
from shared_models import ForumThreadCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_user_resolution_and_thread_creation():
    logger.info("Starting user resolution test...")
    
    # 1. Setup Session
    session = next(get_session())
    
    try:
        # 2. Get existing user for test
        user_repo = UserRepository(session)
        # Using known user from previous DB check: FAR-00001 / c34618b2-e73f-42ef-89a7-65312190d2ad
        keycloak_id = "c34618b2-e73f-42ef-89a7-65312190d2ad"
        internal_id = "FAR-00001"
        
        logger.info(f"Looking up user with Keycloak ID: {keycloak_id}")
        user = user_repo.get_by_keycloak_id(keycloak_id)
        
        if not user:
            logger.error("User not found! Test cannot proceed.")
            return
            
        logger.info(f"✅ User found: {user.id} (Expected: {internal_id})")
        assert user.id == internal_id
        
        # 3. Create Service
        service = ForumService(session)
        
        # 4. Mock Token Payload using Keycloak UUID
        token_payload = TokenPayload({
            "sub": keycloak_id,
            "preferred_username": "testuser",
            "email": "user@example.com",
            "realm_access": {"roles": ["offline_access", "uma_authorization", "default-roles-farm-connect"]}
        })
        
        # 5. Attempt Thread Creation
        thread_data = ForumThreadCreate(
            title=f"Test Thread with Auth {uuid4().hex[:6]}",
            content_body="Testing foreign key resolution.",
            category="general",
            context_field_id="259df240-cef5-450b-b54d-ccff2d56c5c8" # Valid Field ID from DB check
        )
        
        logger.info("Attempting to create thread...")
        thread = service.create_thread(thread_data, token_payload)
        
        logger.info(f"✅ Thread created successfully! ID: {thread.id}")
        logger.info(f"Thread Author ID: {thread.author_id} (Should be {internal_id})")
        
        assert thread.author_id == internal_id
        
        # Clean up
        service.delete_thread(thread.id, token_payload)
        logger.info("Test thread deleted.")

    except Exception as e:
        logger.error(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    test_user_resolution_and_thread_creation()
