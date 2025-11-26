from __future__ import annotations

import io
import json
import time
from pathlib import Path
from typing import Any

import torchvision.transforms as transforms
from loguru import logger
from PIL import Image

try:
    import torch
    import torch.nn as nn

    TORCH_AVAILABLE = True
except Exception as e:  # noqa: BLE001
    logger.warning("Torch is not available: {}", e)
    TORCH_AVAILABLE = False


def _load_class_map(path: Path) -> dict[int, dict[str, Any]]:
    """
    Завантажує class_map.json у новому форматі:
    {
        "0": {
            "plant_label": "apple",
            "plant_name": "Яблуня",
            "disease_label": "black_rot",
            "disease_name": "Чорна гниль"
        }
    }
    """
    if not path.exists():
        logger.warning("class_map.json not found at {}", path)
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error("Failed to parse class_map.json: {}", e)
        return {}

    out = {}
    for key, v in data.items():
        try:
            idx = int(key)
            out[idx] = {
                "plant_label": v.get("plant_label"),
                "plant_name": v.get("plant_name"),
                "disease_label": v.get("disease_label"),
                "disease_name": v.get("disease_name"),
            }
        except Exception:
            logger.error("Invalid class_map entry for key {}: {}", key, v)

    return out


class _BaseClassifier:
    def predict_topk(self, image_bytes: bytes, topk: int = 3) -> list[dict[str, Any]]:
        raise NotImplementedError


class _DummyClassifier(_BaseClassifier):
    """Fallback, коли Torch/модель недоступні."""

    def __init__(self, class_map: dict[int, dict[str, str]]):
        self.class_map = class_map
        self.backend = "dummy"

    def predict_topk(self, image_bytes: bytes, topk: int = 3) -> list[dict[str, Any]]:
        confidences = [0.94, 0.88, 0.69, 0.55, 0.42]
        out: list[dict[str, Any]] = []
        for i, (_cls_idx, meta) in enumerate(list(self.class_map.items())[:topk]):
            out.append(
                {
                    "plant_id": meta.get("plant_id"),
                    "disease_id": meta.get("disease_id"),
                    "confidence": float(
                        confidences[i] if i < len(confidences) else 0.4
                    ),
                }
            )
        return out


class _TorchClassifier(_BaseClassifier):
    """
    Приймає вже завантажений nn.Module (TorchScript або pickled-модель)
    і class_map.
    """

    def __init__(
        self, model: nn.Module, class_map: dict[int, dict[str, str]], backend: str
    ):
        if not TORCH_AVAILABLE:
            raise RuntimeError("Torch not installed")
        self.model: nn.Module = model
        self.model.eval()
        self.class_map = class_map
        self.backend = backend
        logger.info("Torch model ready (backend: {})", backend)

    @staticmethod
    def _preprocess(image_bytes: bytes) -> torch.Tensor:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),  # автоматично /255
            ]
        )

        return transform(img).unsqueeze(0)

    @torch.inference_mode()  # type: ignore[misc]
    def predict_topk(self, image_bytes: bytes, topk: int = 3) -> list[dict[str, Any]]:
        x = self._preprocess(image_bytes)
        logits = self.model(x)  # type: ignore[operator]
        if isinstance(logits, tuple | list) and logits:
            logits = logits[0]
        probs = torch.softmax(logits, dim=1)
        vals, idxs = torch.topk(probs, k=topk, dim=1)

        out: list[dict[str, Any]] = []
        for conf, cls_idx in zip(vals[0].tolist(), idxs[0].tolist(), strict=False):
            meta = self.class_map.get(int(cls_idx), {})
            disease_name = meta.get("disease_name")
            if (disease_name is None or disease_name == "") and meta.get(
                "disease_label"
            ) == "healthy":
                disease_name = "Здорова рослина"

            out.append(
                {
                    "class_index": int(cls_idx),
                    "confidence": float(conf),
                    "plant_name": meta.get("plant_name"),
                    "plant_label": meta.get("plant_label"),
                    "disease_name": disease_name,
                    "disease_label": meta.get("disease_label"),
                    "plant_id": meta.get("plant_id"),
                    "disease_id": meta.get("disease_id"),
                }
            )
        return out


def _load_model_flexible(model_path: Path):
    """
    1) Пробуємо TorchScript (torch.jit.load)
    2) Якщо не вийшло — pickled nn.Module через torch.load(weights_only=False)
       + allowlist для torchvision MobileNetV2 (за потреби).
    Повертає (model, backend_str)
    """
    if not TORCH_AVAILABLE:
        raise RuntimeError("Torch is not available")

    try:
        m = torch.jit.load(str(model_path), map_location="cpu")
        m.eval()
        logger.info(f"Loaded TorchScript model from {model_path}")
        return m, "torchscript"
    except Exception as e_js:
        logger.error(f"Failed to load TorchScript model: {e_js}")

    try:
        try:
            from torch.serialization import add_safe_globals  # type: ignore

            try:
                from torchvision.models.mobilenetv2 import MobileNetV2  # type: ignore

                add_safe_globals([MobileNetV2])
            except Exception as e_tv:
                logger.debug(f"torchvision MobileNetV2 not available or failed: {e_tv}")
        except Exception as e_allow:
            logger.debug(f"add_safe_globals not available or failed: {e_allow}")

        obj = torch.load(str(model_path), map_location="cpu", weights_only=False)

        if isinstance(obj, nn.Module):
            obj.eval()
            logger.info(f"Loaded pickled nn.Module from {model_path}")
            return obj, "pickle-module"

        if isinstance(obj, dict) and obj:
            raise RuntimeError("state_dict provided without architecture")

        raise RuntimeError("Unsupported model object type")
    except Exception as e_pkl:
        logger.error(f"Fallback torch.load() failed: {e_pkl}")
        raise


# ---------- module-level singleton ----------
_CLASSIFIER: _BaseClassifier | None = None


def _build_classifier() -> _BaseClassifier:
    from app.core.config import settings

    model_path = Path(settings.model_path)

    class_map_path = (
        Path(settings.class_map_path)
        if getattr(settings, "class_map_path", None)
        else model_path.parent / "class_map.json"
    )
    class_map = _load_class_map(class_map_path)

    if not TORCH_AVAILABLE:
        logger.warning("Torch not available — using DummyClassifier.")
        return _DummyClassifier(class_map)

    if not model_path.exists():
        logger.warning(f"Model file not found at {model_path} — using DummyClassifier.")
        return _DummyClassifier(class_map)

    try:
        model, backend = _load_model_flexible(model_path)
        return _TorchClassifier(model, class_map, backend=backend)
    except Exception:
        logger.warning("Falling back to DummyClassifier due to model load failure.")
        return _DummyClassifier(class_map)


def _ensure_loaded() -> None:
    global _CLASSIFIER
    if _CLASSIFIER is None:
        _CLASSIFIER = _build_classifier()


def predict_topk(image_bytes: bytes, topk: int = 3) -> list[dict[str, Any]]:
    """Публічний API для ендпоінта діагностики."""
    _ensure_loaded()
    t0 = time.perf_counter()
    res = _CLASSIFIER.predict_topk(image_bytes, topk=topk)  # type: ignore[union-attr]
    dt_ms = int((time.perf_counter() - t0) * 1000)
    logger.debug("Inference: {} ms", dt_ms)
    return res


def model_backend() -> str:
    _ensure_loaded()
    try:
        return getattr(_CLASSIFIER, "backend", "unknown")  # type: ignore[union-attr]
    except Exception:
        return "unknown"


_ensure_loaded()
