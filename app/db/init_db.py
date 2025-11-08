from beanie import init_beanie as beanie_init
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.models.diagnosis import Diagnosis
from app.models.disease import Disease
from app.models.plant import Plant

_client: AsyncIOMotorClient | None = None


async def init_db():
    global _client
    _client = AsyncIOMotorClient(settings.mongo_uri)
    db = _client.get_database(settings.database_name)
    await beanie_init(database=db, document_models=[Plant, Disease, Diagnosis])
