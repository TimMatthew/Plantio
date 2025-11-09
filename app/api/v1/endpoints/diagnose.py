import time
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from loguru import logger

from app.core.config import settings
from app.models.diagnosis import Diagnosis
from app.models.plant import Plant
from app.services.inference import predict_topk
from app.services.storage import LocalFileStorage

router = APIRouter()
_storage = LocalFileStorage()


async def _enrich_candidates_with_embedded(
    raw: list[dict[str, Any]], threshold: float
) -> tuple[list[dict[str, Any]], str | None]:
    """
    Під вашу схему Mongo:
      plants: { plantName: str, diseases: [ { diseaseName: str, ... } ] }
    Приймає кандидатів у форматі:
      {class_index?, plant_name?, disease_name?, plant_id?, disease_id?, confidence}
    Повертає (enriched, decided_disease_name|None)
    """
    enriched: list[dict[str, Any]] = []
    decided: str | None = None

    for item in raw:
        conf = float(item.get("confidence", 0.0))

        plant_ref = (
            item.get("plant_name") or item.get("plant_label") or item.get("plant_id")
        )
        disease_ref = (
            item.get("disease_name")
            or item.get("disease_label")
            or item.get("disease_id")
        )

        plant_name: str | None = None
        plant_oid: str | None = None
        disease_name: str | None = None
        disease_id: str | None = None

        doc: Plant | None = None
        if isinstance(plant_ref, str) and plant_ref:
            try:
                doc = await Plant.find_one(Plant.plantName == plant_ref)
            except Exception:
                logger.exception("plant_lookup_failed for %r", plant_ref)
                doc = None

        if doc:
            plant_name = getattr(doc, "plantName", None)
            try:
                plant_oid = str(doc.id)
            except Exception:
                plant_oid = None

            if (
                isinstance(disease_ref, str)
                and disease_ref
                and getattr(doc, "diseases", None)
            ):
                try:
                    for d in doc.diseases or []:
                        name = getattr(d, "diseaseName", None)
                        if name is None and isinstance(d, dict):
                            name = d.get("diseaseName")
                        if name == disease_ref:
                            disease_name = name
                            break
                except Exception:
                    logger.exception("disease_lookup_failed on plant %r", plant_name)

        if plant_name is None and isinstance(plant_ref, str):
            plant_name = plant_ref
        if disease_name is None and isinstance(disease_ref, str):
            disease_name = disease_ref

        enriched.append(
            {
                "plant_id": plant_oid,
                "plant_name": plant_name,
                "disease_id": disease_id,
                "disease_name": disease_name,
                "confidence": conf,
            }
        )

        if decided is None and disease_name and conf >= threshold:
            decided = disease_name

    return enriched, decided


@router.post("/diagnose")
async def diagnose(
    image: UploadFile = File(...),  # noqa: B008
    topK: int = Form(default=3),
    threshold: float = Form(default=0.6),
):
    content = await image.read()
    if not content:
        raise HTTPException(status_code=400, detail="empty_file")

    _, sha256 = _storage.save(image.filename, content)

    t0 = time.perf_counter()
    try:
        candidates = predict_topk(content, topk=topK)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"invalid_image: {e}") from e
    ms = int((time.perf_counter() - t0) * 1000)

    try:
        effective_threshold = max(threshold, settings.min_confidence)
        enriched, decided = await _enrich_candidates_with_embedded(
            candidates, effective_threshold
        )
    except Exception as e:
        logger.exception("_enrich_candidates_with_embedded failed")
        raise HTTPException(status_code=500, detail=f"enrich_failed: {e}") from e

    doc = Diagnosis(
        status="DONE",
        request={"imageSha256": sha256, "filename": image.filename},
        result={
            "plantId": enriched[0].get("plant_id") if enriched else None,
            "candidates": enriched,
            "decidedDiseaseId": decided,
        },
        inference_ms=ms,
    )
    try:
        await doc.insert()
    except Exception as e:
        logger.exception("diagnosis_insert_failed")
        raise HTTPException(status_code=500, detail=f"insert_failed: {e}") from e

    if decided is None:
        raise HTTPException(
            status_code=422,
            detail={"message": "low_confidence", "candidates": enriched},
        )

    return {
        "diagnosisId": str(doc.id),
        "decidedDiseaseId": decided,
        "candidates": enriched,
        "inferenceMs": ms,
    }
