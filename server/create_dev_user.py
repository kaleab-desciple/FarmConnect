import sys
import os

# Add the server directory to the Python path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from sqlalchemy import text

def create_user():
    session = SessionLocal()
    try:
        # Check if user exists
        print("Checking for dev-user...")
        result = session.execute(text("SELECT id FROM users WHERE id = 'dev-user'"))
        if result.fetchone():
            print("dev-user already exists.")
            return

        print("Creating dev-user...")
        # Insert user
        # Note: relying on postgres to cast 'FARMER' string to enum
        session.execute(text("""
            INSERT INTO users (id, email, name, role, created_at, keycloak_id)
            VALUES ('dev-user', 'dev@example.com', 'Dev User', 'FARMER', NOW(), 'dev-user-kc')
        """))
        session.commit()
        print("dev-user created successfully.")
    except Exception as e:
        print(f"Error creating user: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_user()
