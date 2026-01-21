from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
import logging

def setup_middleware(app: FastAPI):
    """
    Setup middleware like CORS, logging, etc.
    """
    # Example: CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Example: simple request logging
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger = logging.getLogger("app.requests")
        logger.info(f"Incoming request: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response