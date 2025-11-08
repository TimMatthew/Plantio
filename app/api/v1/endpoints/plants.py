from fastapi import APIRouter

from app.models.plant import Plant

router = APIRouter()


@router.get("")
async def list_plants(query: str | None = None, page: int = 0, size: int = 20):
    skip = max(page, 0) * max(size, 1)
    limit = min(max(size, 1), 100)
    if query:
        cursor = (
            Plant.find(
                {
                    "$or": [
                        {"name.uk": {"$regex": query, "$options": "i"}},
                        {"aliases": {"$regex": query, "$options": "i"}},
                    ]
                }
            )
            .skip(skip)
            .limit(limit)
        )
    else:
        cursor = Plant.find_all().skip(skip).limit(limit)
    items = await cursor.to_list()
    return {"items": items, "page": page, "size": size, "count": len(items)}


@router.get("/{plant_id}")
async def get_plant(plant_id: str):
    plant = await Plant.get(plant_id)
    if not plant:
        return {"error": "not_found"}
    return plant
