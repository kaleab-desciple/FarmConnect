from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.db.base import Base
import os
from datetime import datetime
from typing import Optional

# PostgreSQL connection - use sync driver for compatibility
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:password@postgres:5432/agri_db"
)

# MongoDB connection
MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb://localhost:27017/agri_db"
)

# Sync engine for database operations
engine = create_engine(DATABASE_URL, echo=True, future=True)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

# MongoDB client (lazy initialization)
_mongo_client = None

def get_mongo_db():
    """Get MongoDB database instance."""
    global _mongo_client
    if _mongo_client is None:
        from pymongo import MongoClient
        _mongo_client = MongoClient(MONGODB_URL)
    return _mongo_client["agri_db"]

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Async engine for startup (created lazily to avoid import issues)
_async_engine = None

def get_async_engine():
    """Get or create async engine for startup operations."""
    global _async_engine
    if _async_engine is None:
        # Convert sync URL to async URL
        async_url = DATABASE_URL.replace("postgresql+psycopg2", "postgresql+asyncpg")
        from sqlalchemy.ext.asyncio import create_async_engine
        _async_engine = create_async_engine(async_url, echo=True, future=True)
    return _async_engine


#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker

#engine = create_engine("postgresql+psycopg2://user:pass@localhost/farm_connect")
#SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

