import io
import random

from PIL import Image


class DummyClassifier:
    """Temporary stub. Replace with real model later."""

    def __init__(self):
        # Example mapping: class index -> (plant_id, disease_id)
        self.class_map = [
            ("pl_sunflower", "dis_sclerotinia"),
            ("pl_wheat", "dis_rust"),
            ("pl_soy", "dis_fusarium"),
        ]

    def predict_topk(
        self, content: bytes, topk: int = 3
    ) -> list[tuple[str, str, float]]:
        # Validate image can be opened
        Image.open(io.BytesIO(content)).convert("RGB")
        # Produce stable pseudo-confidences
        random.seed(len(content))
        choices = random.sample(self.class_map, k=min(topk, len(self.class_map)))
        return [(p, d, round(random.uniform(0.6, 0.95), 2)) for (p, d) in choices]
