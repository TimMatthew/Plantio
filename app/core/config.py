from __future__ import annotations

import json

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
        env_file=".env",
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


settings = Settings()
