from fastapi import APIRouter

from app.services.inference import model_backend

router = APIRouter()


@router.get("/")
def health_root():
    return {"status": "ok"}


@router.get("/db")
async def health_db():
    return {"db": "ok"}


@router.get("/model")
def health_model():
    return {"backend": model_backend()}
