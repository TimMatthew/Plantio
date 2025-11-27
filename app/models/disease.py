from beanie import Document
from pydantic import Field


class Disease(Document):
    id: str = Field(default_factory=str)
    plant_id: str
    name: dict[str, str]
    symptoms: list[str] = []
    causes: str | None = None
    treatments: list[dict] = []
    gallery: list[str] = []
    popularity: int = 0

    class Settings:
        name = "diseases"
        indexes = [
            "plant_id",
            "popularity",
            [("name.uk", "text")],
        ]
