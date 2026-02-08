import sqlalchemy
from sqlalchemy import create_engine, text
import os

DATABASE_URL = "postgresql+psycopg2://kaleab:From%401994@localhost/farm_connect"

def check_version():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version_num FROM alembic_version"))
            version = result.fetchone()
            if version:
                print(f"Current alembic version in DB: {version[0]}")
            else:
                print("No version found in alembic_version table.")
            
            # Check if index exists just in case
            try:
                # This query is for postgres
                index_check = connection.execute(text("SELECT indexname FROM pg_indexes WHERE indexname = 'ix_accounts_owner_id' OR indexname = 'IX_accounts_owner_id'"))
                idx = index_check.fetchone()
                if idx:
                    print(f"Found index: {idx[0]}")
                else:
                    print("Index 'ix_accounts_owner_id' not found.")
            except Exception as e:
                print(f"Error checking index: {e}")

    except Exception as e:
        print(f"Error checking version: {e}")

if __name__ == "__main__":
    check_version()
