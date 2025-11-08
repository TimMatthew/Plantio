from fastapi import APIRouter

from .endpoints import diagnose, diseases, health, plants

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(plants.router, prefix="/plants", tags=["plants"])
api_router.include_router(diseases.router, prefix="/diseases", tags=["diseases"])
api_router.include_router(diagnose.router, tags=["diagnose"])
