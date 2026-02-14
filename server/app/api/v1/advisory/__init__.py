"""
Advisory Service Router
Farm Connect AgriManagement System
"""

from fastapi import APIRouter
from app.api.v1.advisory.forums import routes as forums_routes
from app.api.v1.advisory.knowledge import routes as knowledge_routes

router = APIRouter()

# Include forums routes
router.include_router(
    forums_routes.router,
    prefix="/forums",
    tags=["Forums"]
)

# Include knowledge base routes
router.include_router(
    knowledge_routes.router,
    prefix="/knowledge",
    tags=["Knowledge Base"]
)
