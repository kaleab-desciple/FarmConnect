import sqlalchemy
from sqlalchemy import create_engine, text
import os

DATABASE_URL = "postgresql+psycopg2://kaleab:From%401994@localhost/farm_connect"

def fix_version():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            # Update the version to the known valid head
            # 13c615f4297d is the head revision from `alembic history`
            
            print("Resetting alembic_version to '13c615f4297d'...")
            connection.execute(text("UPDATE alembic_version SET version_num = '13c615f4297d'"))
            connection.commit()
            print("Successfully updated alembic_version.")
            
    except Exception as e:
        print(f"Error fixing version: {e}")

if __name__ == "__main__":
    fix_version()
