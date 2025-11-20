from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.models.diagnosis import Diagnosis
from app.services.inference import model_backend

router = APIRouter()


@router.get("/")
async def health_root():
    """
    Загальний health-check:
    - модель (backend != "dummy")
    - база даних (простий запит через Diagnosis)
    """
    backend = model_backend()
    model_ok = backend != "dummy"

    try:
        await Diagnosis.find_one()
        db_ok = True
    except Exception:
        db_ok = False

    if model_ok and db_ok:
        overall = "ok"
    elif model_ok or db_ok:
        overall = "degraded"
    else:
        overall = "error"

    return {
        "status": overall,
        "db": "ok" if db_ok else "error",
        "model_backend": backend,
    }


@router.get("/db")
async def health_db():
    """
    Перевірка доступності MongoDB/Beanie.
    Повертає:
    - 200 {"db": "ok"} якщо все добре
    - 503 {"db": "error"} якщо немає доступу до БД
    """
    try:
        await Diagnosis.find_one()
        return {"db": "ok"}
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"db": "error"},
        )


@router.get("/model")
def health_model():
    return {"backend": model_backend()}


@router.get("/app")
def health_app():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "env": settings.env,
    }
