from fastapi import APIRouter

from app.api.v1.endpoints import diagnose, diseases, health, plants

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(diagnose.router, prefix="", tags=["diagnose"])
api_router.include_router(plants.router, prefix="/plants", tags=["plants"])
api_router.include_router(diseases.router, prefix="/diseases", tags=["diseases"])
