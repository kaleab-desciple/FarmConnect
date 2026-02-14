from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
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
    
    # Setup middleware
    setup_middleware(app)

    # Include API routers
    app.include_router(api_router, prefix="/api/v1")

    # Note: Database tables should be created via Alembic migrations, not on startup
    # Run: docker-compose exec api alembic upgrade head

    return app


app = create_app()
