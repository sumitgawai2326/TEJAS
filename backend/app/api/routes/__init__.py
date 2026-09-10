"""
Central API Router for TEJAS.
"""
from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.subsystems import router as subsystems_router
from app.api.routes.fields import router as fields_router
from app.api.routes.vision import router as vision_router
from app.api.routes.disease import router as disease_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(subsystems_router)
api_router.include_router(fields_router)
api_router.include_router(vision_router)

# TEJAS Real Disease Inference API routes
api_router.include_router(disease_router, prefix="/v1/disease")
api_router.include_router(disease_router, prefix="/disease")

__all__ = [
    "api_router",
    "health_router",
    "subsystems_router",
    "fields_router",
    "vision_router",
    "disease_router"
]
