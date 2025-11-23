from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.models.plant import Plant

router = APIRouter()


async def _load_flat_diseases() -> list[dict[str, Any]]:
    """
    Читає всі рослини з Mongo та розгортає масив `diseases`
    у плаский список словників.

    Використовуємо сирі dict'и з Motor (через get_pymongo_collection),
    щоб не падати на потенційно "кривих" старих документів.
    """
    collection = Plant.get_pymongo_collection()
    cursor = collection.find({"diseases": {"$exists": True, "$ne": []}})
    plants = await cursor.to_list(length=None)

    flat: list[dict[str, Any]] = []

    for plant in plants:
        plant_id = str(plant.get("_id"))
        plant_name = plant.get("plantName")

        for d in plant.get("diseases", []) or []:
            name = d.get("diseaseName")
            if not name:
                continue

            flat.append(
                {
                    "plantId": plant_id,
                    "plantName": plant_name,
                    "diseaseName": name,
                    "description": d.get("description"),
                    "symptoms": d.get("symptoms", []),
                    "prevention": d.get("prevention", []),
                    "treatment": d.get("treatment", []),
                    "riskLevel": d.get("riskLevel"),
                    "images": d.get("images", []),
                }
            )

    return flat


@router.get("")
async def list_diseases(
    q: str | None = Query(
        default=None,
        description="Пошук по назві, опису, симптомах, профілактиці та лікуванні",
    ),
    plant_id: str | None = Query(
        default=None,
        description="Фільтр за конкретною рослиною (id з /api/v1/plants)",
    ),
    sort: str | None = Query(
        default="-diseaseName",
        description="Сортування, напр. '-diseaseName' або 'plantName'",
    ),
    page: int = Query(0, ge=0),
    size: int = Query(20, ge=1, le=100),
):
    """
    Повертає плаский список хвороб (по всіх рослинах), з фільтрами та пагінацією.
    """
    all_items = await _load_flat_diseases()

    if plant_id:
        all_items = [d for d in all_items if d.get("plantId") == plant_id]

    if q:
        q_lower = q.lower()

        def matches(d: dict[str, Any]) -> bool:
            parts: list[str] = []

            for key in ("diseaseName", "description"):
                val = d.get(key)
                if isinstance(val, str):
                    parts.append(val)

            for key in ("symptoms", "prevention", "treatment"):
                arr = d.get(key) or []
                if isinstance(arr, list):
                    parts.extend(str(x) for x in arr)

            haystack = " ".join(parts).lower()
            return q_lower in haystack

        all_items = [d for d in all_items if matches(d)]

    if sort:
        parts = [p.strip() for p in sort.split(",") if p.strip()]
        if parts:
            first = parts[0]
            desc = first.startswith("-")
            field_name = first[1:] if desc else first

            def key_fn(item: dict[str, Any]):
                v = item.get(field_name)
                if v is None:
                    return ""

                if field_name == "riskLevel":
                    order = {"high": 3, "medium": 2, "low": 1, "none": 0}
                    return order.get(str(v).lower(), 0)

                return str(v)

            all_items.sort(key=key_fn, reverse=desc)

    total = len(all_items)
    size = max(size, 1)
    page = max(page, 0)
    start = page * size
    end = start + size
    page_items = all_items[start:end]

    return {
        "items": page_items,
        "page": page,
        "size": size,
        "count": total,
    }


@router.get("/{disease_id}")
async def get_disease(disease_id: str):
    """
    Деталі конкретної хвороби.

    disease_id = те саме, що decidedDiseaseId з /diagnose,
    тобто значення поля `diseases.diseaseName` у БД.

    Алгоритм:
    1) спочатку шукаємо точний збіг diseaseName;
    2) якщо немає — шукаємо за підрядком (для запитів типу /diseases/гниль).
    """
    all_items = await _load_flat_diseases()

    for d in all_items:
        if d.get("diseaseName") == disease_id:
            return d

    needle = disease_id.lower()
    for d in all_items:
        name = str(d.get("diseaseName") or "").lower()
        if needle in name:
            return d

    raise HTTPException(status_code=404, detail="disease_not_found")
