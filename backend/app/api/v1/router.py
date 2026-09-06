from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.geo import router as geo_router
from app.api.v1.eo import router as eo_router
from app.api.v1.change import router as change_router
from app.api.v1.intelligence import router as intelligence_router
from app.api.v1.forecast import router as forecast_router
from app.api.v1.ai import router as ai_router
from app.api.v1.operational import router as operational_router
from app.api.v1.fusion import router as fusion_router

api_router = APIRouter()

# Register API v1 sub-routers
api_router.include_router(health_router)
api_router.include_router(geo_router)
api_router.include_router(eo_router)
api_router.include_router(change_router)
api_router.include_router(intelligence_router)
api_router.include_router(forecast_router)
api_router.include_router(ai_router)
api_router.include_router(operational_router)
api_router.include_router(fusion_router)
