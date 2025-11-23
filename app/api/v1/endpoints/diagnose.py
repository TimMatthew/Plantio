import time
from typing import Any, cast

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from loguru import logger

from app.core.config import settings
from app.core.label_mapping import normalize_names
from app.models.diagnosis import Diagnosis
from app.models.plant import Plant
from app.services import inference
from app.services.storage import LocalFileStorage

router = APIRouter()
_storage = LocalFileStorage()


async def _enrich_candidates_with_embedded(
    raw: list[dict[str, Any]],
    threshold: float,
) -> tuple[list[dict[str, Any]], str | None]:
    """
    Приймає кандидатів у форматі:
      {class_index?, plant_name?, disease_name?, plant_id?, disease_id?, confidence}

    Повертає:
      (список збагачених кандидатів, decided_disease_id | None)

    ВАЖЛИВО:
    - disease_id = те, що повернула модель (англійська назва / label з class_map.json),
      і саме ЦЕ значення віддаємо в decidedDiseaseId (щоб проходили тести).
    - disease_name = людиночитабельна назва (укр з БД, якщо є).
    """
    enriched: list[dict[str, Any]] = []
    decided: str | None = None

    for item in raw:
        conf = float(item.get("confidence", 0.0))

        plant_raw = (
            item.get("plant_name") or item.get("plant_label") or item.get("plant_id")
        )
        disease_raw = (
            item.get("disease_name")
            or item.get("disease_label")
            or item.get("disease_id")
        )

        plant_norm, disease_norm, _ = normalize_names(
            plant_raw if isinstance(plant_raw, str) else None,
            disease_raw if isinstance(disease_raw, str) else None,
        )

        disease_id: str | None = None
        raw_disease_id = item.get("disease_id")
        raw_disease_label = item.get("disease_label")

        if isinstance(raw_disease_id, str) and raw_disease_id:
            disease_id = raw_disease_id
        elif isinstance(raw_disease_label, str) and raw_disease_label:
            disease_id = raw_disease_label
        elif isinstance(disease_raw, str) and disease_raw:
            disease_id = disease_raw

        plant_ref = plant_norm or plant_raw
        disease_ref = disease_norm or disease_raw

        plant_name: str | None = None
        plant_oid: str | None = None
        disease_name: str | None = None

        doc: Any = None
        if isinstance(plant_ref, str) and plant_ref:
            try:
                doc = await Plant.find_one({"plantName": plant_ref})
                if doc is None and isinstance(plant_raw, str) and plant_raw:
                    doc = await Plant.find_one({"plantName": plant_raw})
            except Exception:
                logger.error(
                    "plant_lookup_failed for %r",
                    plant_ref,
                    exc_info=True,
                )
                doc = None

        if doc is not None:
            try:
                plant_name = (
                    getattr(doc, "plantName", None)
                    or getattr(doc, "name", None)
                    or getattr(doc, "plant_name", None)
                )

                if getattr(doc, "id", None) is not None:
                    plant_oid = str(doc.id)

                diseases = getattr(doc, "diseases", None) or getattr(
                    doc, "disease", None
                )

                if isinstance(disease_ref, str) and disease_ref and diseases:
                    try:
                        for d in diseases or []:
                            name = getattr(d, "diseaseName", None)
                            if name is None and isinstance(d, dict):
                                name = (
                                    d.get("diseaseName")
                                    or d.get("name")
                                    or d.get("disease_name")
                                )

                            if name and name == disease_ref:
                                disease_name = name
                                break
                    except Exception:
                        logger.exception(
                            "disease_lookup_failed on plant %r", plant_name
                        )
            except Exception:
                logger.exception("unexpected_plant_doc_shape: %r", doc)

        if plant_name is None and isinstance(plant_norm, str):
            plant_name = plant_norm
        if plant_name is None and isinstance(plant_raw, str):
            plant_name = plant_raw

        if disease_name is None and isinstance(disease_norm, str):
            disease_name = disease_norm
        if disease_name is None and isinstance(disease_raw, str):
            disease_name = disease_raw

        enriched.append(
            {
                "plant_id": plant_oid,
                "plant_name": plant_name,
                "disease_id": disease_id,
                "disease_name": disease_name,
                "confidence": conf,
            }
        )

        if decided is None and disease_id and conf >= threshold:
            decided = disease_id

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
        effective_threshold = max(
            threshold,
            getattr(settings, "min_confidence", threshold),
        )
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
