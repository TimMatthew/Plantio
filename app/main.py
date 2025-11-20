from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.api.v1.router import api_router
from app.db.init_db import _client, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up…")

    await init_db()
    logger.info("Database initialized")

    try:
        yield
    finally:
        logger.info("Shutting down…")

        if _client is not None:
            _client.close()
            logger.info("MongoDB client closed")


app = FastAPI(lifespan=lifespan)

app.include_router(api_router)
