from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Plantio API"
    app_version: str = "0.1.0"
    env: str = "dev"

    mongo_uri_local: str = "mongodb://localhost:27017/plantio"
    mongo_uri_atlas: str | None = None
    database_name: str = "plantio"

    host: str = "0.0.0.0"
    port: int = 8000

    upload_dir: str = "./storage/uploads"
    model_path: str = "./app/models/plantio/model.pth"
    class_map_path: str | None = None

    allowed_origins: list[str] = []

    min_confidence: float = 0.6
    allow_healthy: bool = False
    min_margin: float = 0.0

    @property
    def mongo_uri(self) -> str:
        return self.mongo_uri_atlas or self.mongo_uri_local

    model_config = SettingsConfigDict(
        env_prefix="PLANTIO_",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _parse_allowed_origins(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            try:
                return json.loads(v)
            except Exception:
                return [s.strip() for s in v.split(",") if s.strip()]
        return []


def _read_env_selector(file: str = ".env") -> str | None:
    """
    Дістає PLANTIO_ENV з .env, ігнорує інлайн-коментарі: 'prod # dev/prod'.
    Без залежностей.
    """
    p = Path(file)
    if not p.exists():
        return None
    for raw in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("PLANTIO_ENV"):
            m = re.match(r"PLANTIO_ENV\s*=\s*(.+)", line, flags=re.I)
            if not m:
                continue
            val = m.group(1).strip()
            if "#" in val and not (
                val.startswith(("'", '"')) and val.endswith(("'", '"'))
            ):
                val = val.split("#", 1)[0].strip()
            val = val.strip().strip('"').strip("'")
            return val or None
    return None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    env_from_os = os.getenv("PLANTIO_ENV")
    env_from_file = _read_env_selector(".env")
    env = (env_from_os or env_from_file or "dev").strip().lower()

    is_prod = env == "prod" or env == "production" or env.startswith("prod")

    env_file = ".env.prod" if is_prod else ".env.dev"

    env_files = [env_file]
    if Path(".env.common").exists():
        env_files.insert(0, ".env.common")

    return Settings(_env_file=tuple(env_files))


settings = get_settings()
