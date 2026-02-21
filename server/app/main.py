# import asyncio
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from app.api.v1.router import api_router
from app.core.middleware import setup_middleware, limiter
from app.core.database import get_async_engine
from app.infrastructure.db.base import Base
from slowapi.errors import RateLimitExceeded
import logging

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """
    Creates FastAPI app with routers, middleware, and DB initialization.
    """
    app = FastAPI(title="Farmer-Merchant Connector")
    
    # Add rate limiter state
    if limiter is not None:
        app.state.limiter = limiter
    
    # Add exception handler for rate limit exceeded
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."}
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Handle database integrity errors (e.g., foreign key violations)."""
        error_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
        
        # Log the full error for debugging
        logger.error(f"Database IntegrityError: {error_msg}")
        
        # Check for foreign key violations specifically
        if "foreign key constraint" in error_msg.lower():
            detail = "Database integrity error: A referenced record (like a User or Field) does not exist."
            if "DETAIL:" in error_msg:
                detail = error_msg.split("DETAIL:")[1].split("[SQL:")[0].strip()
            
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": f"Invalid reference: {detail}"}
            )
        
        # Check for unique constraint violations
        if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
            detail = "Database integrity error: A record with this value already exists."
            if "DETAIL:" in error_msg:
                detail = error_msg.split("DETAIL:")[1].split("[SQL:")[0].strip()
            
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": f"Duplicate entry: {detail}"}
            )
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": f"Database integrity error occurred: {error_msg}"}
        )
    
    # Setup middleware
    setup_middleware(app)

    # Include API routers
    app.include_router(api_router, prefix="/api/v1")

    # Start QC activation worker on startup and stop on shutdown
    # from app.application.harvest.qc_activation_worker import start_worker, stop_worker

    # app.add_event_handler("startup", lambda: asyncio.create_task(start_worker(app)))
    # app.add_event_handler("shutdown", lambda: asyncio.create_task(stop_worker(app)))

    # Note: Database tables should be created via Alembic migrations, not on startup
    # Run: docker-compose exec api alembic upgrade head

    return app


app = create_app()
