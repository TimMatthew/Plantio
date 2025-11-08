from fastapi import APIRouter

from app.models.disease import Disease

router = APIRouter()


@router.get("")
async def list_diseases(
    query: str | None = None,
    plant_id: str | None = None,
    sort: str | None = "-popularity",
    page: int = 0,
    size: int = 20,
):
    skip = max(page, 0) * max(size, 1)
    limit = min(max(size, 1), 100)

    q = {}
    if query:
        q["$or"] = [
            {"name.uk": {"$regex": query, "$options": "i"}},
            {"symptoms": {"$regex": query, "$options": "i"}},
        ]
    if plant_id:
        q["plant_id"] = plant_id

    sort_spec = [("popularity", -1)]
    if sort:
        sort_spec = []
        for field in sort.split(","):
            direction = -1 if field.startswith("-") else 1
            f = field[1:] if field.startswith("-") else field
            sort_spec.append((f, direction))

    cursor = Disease.find(q).sort(sort_spec).skip(skip).limit(limit)
    items = await cursor.to_list()
    return {"items": items, "page": page, "size": size, "count": len(items)}


@router.get("/{disease_id}")
async def get_disease(disease_id: str):
    disease = await Disease.get(disease_id)
    if not disease:
        return {"error": "not_found"}
    return disease
