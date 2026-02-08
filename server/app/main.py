from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.middleware import setup_middleware
from app.core.database import get_async_engine
from app.infrastructure.db.base import Base
import logging

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """
    Creates FastAPI app with routers, middleware, and DB initialization.
    """
    app = FastAPI(title="Farmer-Merchant Connector")

    # Setup middleware
    setup_middleware(app)

    # Include API routers
    app.include_router(api_router, prefix="/api/v1")

    # Note: Database tables should be created via Alembic migrations, not on startup
    # Run: docker-compose exec api alembic upgrade head

    return app


app = create_app()
