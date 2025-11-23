from typing import Any

from fastapi import APIRouter, Query

from app.models.plant import Plant

router = APIRouter()


@router.get("")
async def list_plants(
    q: str | None = Query(default=None, description="Пошук по назві/опису рослини"),
    page: int = Query(0, ge=0),
    size: int = Query(20, ge=1, le=100),
):
    """
    Повертає список рослин з колекції MongoDB `plants`.

    - q: case-insensitive пошук по plantName / scientificName / description
    - page/size: пагінація
    """
    size = max(size, 1)
    page = max(page, 0)
    skip = page * size
    limit = size

    collection = Plant.get_pymongo_collection()

    filter_spec: dict[str, Any] = {}
    if q:
        regex = {"$regex": q, "$options": "i"}
        filter_spec = {
            "$or": [
                {"plantName": regex},
                {"scientificName": regex},
                {"description": regex},
            ]
        }

    cursor = collection.find(filter_spec).sort("plantName", 1).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)

    items = [
        {
            "id": str(doc.get("_id")),
            "plantName": doc.get("plantName"),
            "scientificName": doc.get("scientificName"),
            "description": doc.get("description"),
            "imageUrl": doc.get("imageUrl"),
        }
        for doc in docs
    ]

    return {
        "items": items,
        "page": page,
        "size": size,
        "count": len(items),
    }
