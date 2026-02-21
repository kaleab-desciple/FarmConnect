from fastapi import APIRouter

from .users.routes import router as users_router
from .products.routes import router as products_router
from .orders.routes import router as orders_router
from .payments.escrow import router as escrow_router
from .disputes.routes import router as disputes_router
from .ledger import router as ledger_router
from .accounting.routes import router as accounting_router
from .reports.routes import router as reports_router
from .auth.routes import router as auth_router
from .auth.provisioning_routes import router as provisioning_router
from .examples.protected_routes import router as examples_router
from .farms.routes import router as farms_router
from .monitoring.routes import router as monitoring_router
from .ai.routes import router as ai_router
from .weather.routes import router as weather_router
from .harvest.harvest_routes import router as harvest_router
from app.api.qc.routes import router as qc_router
from .aggregator.routes import router as aggregator_router

api_router = APIRouter()

# Register auth routers (public endpoints, no auth required)
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(provisioning_router, prefix="/auth", tags=["User Provisioning"])

# Register example protected routes
api_router.include_router(examples_router, prefix="/examples", tags=["Examples (Protected)"])

# Register all feature routers
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(products_router, prefix="/products", tags=["Products"])
api_router.include_router(orders_router, prefix="/orders", tags=["Orders"])
api_router.include_router(escrow_router, prefix="/escrows", tags=["Escrow"])
api_router.include_router(disputes_router, prefix="/disputes", tags=["Disputes"])
api_router.include_router(ledger_router, prefix="/ledger", tags=["Ledger"])
api_router.include_router(accounting_router, prefix="/accounting", tags=["Accounting"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])

# Register agricultural management routers
api_router.include_router(farms_router, prefix="/agri", tags=["Agricultural Management"])
api_router.include_router(monitoring_router, prefix="/agri", tags=["Monitoring & Data Entry"])
api_router.include_router(ai_router, prefix="/agri", tags=["AI Diagnosis"])
api_router.include_router(weather_router, prefix="/agri", tags=["Weather Service"])
api_router.include_router(harvest_router, prefix="/agri", tags=["Harvest Management"])

# QC/Grading Routes
api_router.include_router(qc_router, prefix="/qc", tags=["QC & Lab"])

# Aggregator Settlement Routes
api_router.include_router(aggregator_router, prefix="/aggregator", tags=["Aggregator & Settlement"])


# Advisory Routes
# api_router.include_router(notifications_router, prefix="/advisory/notifications", tags=["Notifications"])