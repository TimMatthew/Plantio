import time

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.diagnosis import Diagnosis
from app.models.disease import Disease
from app.models.plant import Plant
from app.services.inference import DummyClassifier
from app.services.storage import LocalFileStorage

router = APIRouter()

_storage = LocalFileStorage()
_classifier = DummyClassifier()


@router.post("/diagnose")
async def diagnose(
    image: UploadFile = File(...),  # noqa: B008
    topK: int = Form(3),
    threshold: float = Form(0.6),
):
    content = await image.read()
    if not content:
        raise HTTPException(status_code=400, detail="empty_file")

    path, sha256 = _storage.save(image.filename, content)
    t0 = time.perf_counter()
    try:
        candidates = _classifier.predict_topk(content, topk=topK)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"invalid_image: {e}") from e
    ms = int((time.perf_counter() - t0) * 1000)

    enriched = []
    decided = None
    for p_id, d_id, conf in candidates:
        plant = await Plant.get(p_id)
        disease = await Disease.get(d_id)
        item = {
            "plant_id": p_id,
            "plant_name": plant.name["uk"] if plant else None,
            "disease_id": d_id,
            "disease_name": disease.name["uk"] if disease else None,
            "confidence": conf,
        }
        enriched.append(item)
        if decided is None and conf >= threshold:
            decided = d_id

    doc = Diagnosis(
        status="DONE",
        request={"imageSha256": sha256, "filename": image.filename},
        result={
            "plantId": enriched[0]["plant_id"] if enriched else None,
            "candidates": enriched,
            "decidedDiseaseId": decided,
        },
        inference_ms=ms,
    )
    await doc.insert()

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
