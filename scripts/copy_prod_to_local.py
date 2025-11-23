import asyncio
import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()
load_dotenv(".env.dev")
load_dotenv(".env.prod")

PROD_URI = os.getenv("PLANTIO_MONGO_URI_ATLAS")
DEV_URI = os.getenv("PLANTIO_MONGO_URI_LOCAL")
DB_NAME = os.getenv("PLANTIO_DATABASE_NAME", "plantio")

if not PROD_URI:
    raise RuntimeError("PLANTIO_MONGO_URI_ATLAS не заданий у змінних середовища")

if not DEV_URI:
    raise RuntimeError("PLANTIO_MONGO_URI_LOCAL не заданий у змінних середовища")


async def copy_collection(
    prod_db,
    dev_db,
    collection_name: str,
) -> int:
    """
    Копіює одну колекцію з prod у local.
    Повертає кількість скопійованих документів.
    """
    prod_coll = prod_db[collection_name]
    dev_coll = dev_db[collection_name]

    await dev_coll.drop()

    cursor = prod_coll.find({})
    docs: list[dict] = [doc async for doc in cursor]

    if docs:
        await dev_coll.insert_many(docs)

    return len(docs)


async def main() -> None:
    print("Підключення до MongoDB (prod / local)...")
    prod_client = AsyncIOMotorClient(PROD_URI)
    dev_client = AsyncIOMotorClient(DEV_URI)

    try:
        prod_db = prod_client[DB_NAME]
        dev_db = dev_client[DB_NAME]

        collections_to_copy = ["plants"]

        for coll_name in collections_to_copy:
            count = await copy_collection(prod_db, dev_db, coll_name)
            print(f"Скопійовано {count} документ(ів) у колекцію '{coll_name}'")

    finally:
        prod_client.close()
        dev_client.close()
        print("Готово.")


if __name__ == "__main__":
    asyncio.run(main())
