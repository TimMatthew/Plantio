import io
import os
import sys
import types
from pathlib import Path

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("PLANTIO_MIN_CONFIDENCE", "0.1")

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
async def app_lifespan():
    """
    Гарантує коректний startup/shutdown FastAPI для всієї тест-сесії.
    """
    async with LifespanManager(app):
        yield


@pytest.fixture(scope="session")
def transport():
    return ASGITransport(app=app)


@pytest.fixture
async def client(app_lifespan, transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
def sample_jpeg_bytes():
    """Невелике зображення 224x224 у пам'яті."""
    img = Image.new("RGB", (224, 224), (120, 180, 30))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def mock_storage_save(monkeypatch, tmp_path):
    from app.api.v1.endpoints import diagnose

    def fake_save(filename: str, content: bytes):
        return str(tmp_path / filename), "deadbeef"

    monkeypatch.setattr(diagnose, "_storage", types.SimpleNamespace(save=fake_save))
    return True


@pytest.fixture
def mock_plant_find_one(monkeypatch):
    from app.models import plant as plant_mod

    class DummyPlant:
        id = "507f1f77bcf86cd799439011"
        plantName = "Виноград"
        diseases = [{"diseaseName": "Grape Esca (Black Measles)"}]

    async def fake_find_one(*args, **kwargs):
        return DummyPlant()

    monkeypatch.setattr(plant_mod.Plant, "find_one", staticmethod(fake_find_one))
    return True


@pytest.fixture
def mock_diagnosis_insert(monkeypatch):
    from app.models import diagnosis as diag_mod

    async def fake_insert(self):
        self.id = "test-diagnosis-id"

    monkeypatch.setattr(diag_mod.Diagnosis, "insert", fake_insert)
    return True


@pytest.fixture
def mock_inference_success(monkeypatch):
    from app.services import inference as inf_mod

    def fake_predict_topk(image_bytes: bytes, topk: int = 3):
        return [
            {
                "plant_name": "Виноград",
                "disease_name": "Grape Esca (Black Measles)",
                "confidence": 0.22,
            },
            {"plant_name": "Соняшник", "disease_name": None, "confidence": 0.12},
        ]

    monkeypatch.setattr(inf_mod, "predict_topk", fake_predict_topk)
    return True


@pytest.fixture
def mock_inference_low(monkeypatch):
    from app.services import inference as inf_mod

    def fake_predict_topk(image_bytes: bytes, topk: int = 3):
        return [
            {
                "plant_name": "Виноград",
                "disease_name": "Grape Esca (Black Measles)",
                "confidence": 0.12,
            },
            {"plant_name": "Соняшник", "disease_name": None, "confidence": 0.10},
        ]

    monkeypatch.setattr(inf_mod, "predict_topk", fake_predict_topk)
    return True
