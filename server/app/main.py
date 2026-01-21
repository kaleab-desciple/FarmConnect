from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.middleware import setup_middleware
from app.core.database import engine, Base

def create_app() -> FastAPI:
    """
    Creates FastAPI app with routers, middleware, and DB initialization.
    """
    app = FastAPI(title="Farmer-Merchant Connector")

    # Setup middleware
    setup_middleware(app)

    # Include API routers
    app.include_router(api_router, prefix="/api/v1")

    # Create tables on startup (optional, Alembic preferred in prod)
    @app.on_event("startup")
    async def startup_event():
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()
