from datetime import UTC, datetime
from typing import Any

from beanie import Document
from pydantic import BaseModel, Field


def now_utc() -> datetime:
    return datetime.now(UTC)


class Candidate(BaseModel):
    plant_id: str | None = None
    plant_name: str | None = None
    disease_id: str | None = None
    disease_name: str | None = None
    confidence: float


class Diagnosis(Document):
    status: str = Field(default="DONE")
    created_at: datetime = Field(default_factory=now_utc)

    request: dict[str, Any]
    result: dict[str, Any] | None = None
    inference_ms: int | None = None

    class Settings:
        name = "diagnoses"
        indexes = ["status", "-created_at"]
