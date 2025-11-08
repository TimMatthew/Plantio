from fastapi import FastAPI
from loguru import logger

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.init_db import init_db

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.on_event("startup")
async def on_startup():
    logger.info("Starting up…")
    await init_db()


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down…")


app.include_router(api_router, prefix="/api/v1")
