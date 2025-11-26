import time
from typing import Any, cast

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from loguru import logger

from app.core.label_mapping import normalize_names
from app.models.diagnosis import Diagnosis
from app.models.plant import Plant
from app.services import inference
from app.services.storage import LocalFileStorage

router = APIRouter()
_storage = LocalFileStorage()


async def _enrich_candidates_with_embedded(raw, threshold):
    enriched = []
    decided = None

    for item in raw:
        conf = float(item.get("confidence", 0.0))

        plant_label_raw = (
            item.get("plant_label") or item.get("plant_name") or "unknown_plant"
        )

        disease_label_raw = (
            item.get("disease_label") or item.get("disease_name") or "unknown_disease"
        )

        plant_name_ua, disease_name_ua = normalize_names(
            plant_label_raw, disease_label_raw
        )

        plant_id = None
        disease_name_final = disease_name_ua

        try:
            plant_doc = await Plant.find_one(Plant.plantName == plant_name_ua)
        except Exception:
            plant_doc = None

        if plant_doc:
            plant_id = str(getattr(plant_doc, "id", None))
            try:
                for d in plant_doc.diseases:
                    name = d.get("diseaseName")
                    if name and disease_name_ua in name:
                        disease_name_final = name
                        break
            except Exception:
                pass

        enriched.append(
            {
                "plant_id": plant_id,
                "plant_name": plant_name_ua,
                "disease_id": disease_label_raw,  # RAW
                "disease_name": disease_name_final,
                "confidence": conf,
            }
        )

        if decided is None and conf >= threshold:
            decided = disease_label_raw

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
        candidates_raw = inference.predict_topk(content, topk=topK)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"invalid_image: {e}") from e
    ms = int((time.perf_counter() - t0) * 1000)

    try:
        effective_threshold = threshold

        enriched, decided = await _enrich_candidates_with_embedded(
            candidates_raw,
            effective_threshold,
        )
    except Exception as e:
        logger.exception("_enrich_candidates_with_embedded failed")
        raise HTTPException(status_code=500, detail=f"enrich_failed: {e}") from e

    result_payload: dict[str, Any] = {
        "plantId": enriched[0].get("plant_id") if enriched else None,
        "candidates": enriched,
        "decidedDiseaseId": decided,
    }

    doc = Diagnosis(
        status="DONE",
        request={"imageSha256": sha256, "filename": image.filename},
        result=cast(Any, result_payload),
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
        "diagnosisId": str(getattr(doc, "id", "")),
        "decidedDiseaseId": decided,
        "candidates": enriched,
        "inferenceMs": ms,
    }
