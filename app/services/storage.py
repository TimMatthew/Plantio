import hashlib
import os

from app.core.config import settings


class LocalFileStorage:
    def __init__(self, base_dir: str | None = None):
        self.base_dir = base_dir or settings.upload_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save(self, filename: str, content: bytes) -> tuple[str, str]:
        sha256 = hashlib.sha256(content).hexdigest()
        ext = os.path.splitext(filename)[1].lower() or ".jpg"
        stored = f"{sha256}{ext}"
        path = os.path.join(self.base_dir, stored)
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(content)
        return path, sha256
