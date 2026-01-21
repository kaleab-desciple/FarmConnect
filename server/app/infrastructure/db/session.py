from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://user:password@localhost/farm_connect"
)

engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

# Dependency for FastAPI
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()