from __future__ import annotations

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field


class DiseaseInPlant(BaseModel):
    diseaseName: str
    description: str
    symptoms: list[str] = Field(default_factory=list)
    prevention: list[str] = Field(default_factory=list)
    treatment: list[str] = Field(default_factory=list)
    riskLevel: str | None = None
    images: list[str] = Field(default_factory=list)


class Plant(Document):
    id: PydanticObjectId | None = Field(default=None, alias="_id")

    plantName: str
    scientificName: str | None = None
    description: str | None = None
    imageUrl: str | None = None

    diseases: list[DiseaseInPlant] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

    class Settings:
        name = "plants"
