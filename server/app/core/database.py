from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.db.base import Base
import os

# PostgreSQL connection
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://user:password@localhost/farm_connect"
)
#DATABASE_URL = "postgresql+psycopg2://user:password@localhost/farm_connect"

engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker

#engine = create_engine("postgresql+psycopg2://user:pass@localhost/farm_connect")
#SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

