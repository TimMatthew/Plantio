from pathlib import Path

import pytest

from app.models.diagnosis import Diagnosis


@pytest.mark.asyncio
async def test_diagnose_real_sample_image(client, monkeypatch):
    """
    Інтеграційна перевірка всього пайплайну:
    - читаємо реальне зображення із storage/samples
    - надсилаємо на /api/v1/diagnose
    - перевіряємо структуру відповіді
    Без реального збереження в Mongo, щоб уникнути конфлікту event loop.
    """

    async def fake_insert(self, *args, **kwargs):
        return self

    monkeypatch.setattr(Diagnosis, "insert", fake_insert, raising=False)

    image_path = Path("storage/samples/grape_black_rot_1.jpg")
    assert image_path.exists(), f"Sample image not found: {image_path}"

    with image_path.open("rb") as f:
        files = {
            "image": (image_path.name, f, "image/jpeg"),
        }
        data = {
            "topK": "3",
            "threshold": "0.01",
        }

        r = await client.post("/api/v1/diagnose", files=files, data=data)

    assert r.status_code == 200, r.text

    js = r.json()

    assert "diagnosisId" in js
    assert isinstance(js["diagnosisId"], str)
    assert js["diagnosisId"]

    assert "candidates" in js
    assert isinstance(js["candidates"], list)
    assert js["candidates"], "candidates list must not be empty"

    top = js["candidates"][0]
    assert "confidence" in top
    assert isinstance(top["confidence"], float | int)

    assert "plant_name" in top
    assert "disease_name" in top
