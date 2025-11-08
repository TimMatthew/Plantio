from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "dev"

    # Mongo: local and Atlas (choose via env)
    mongo_uri_local: str = "mongodb://localhost:27017/plantio"
    mongo_uri_atlas: str | None = None
    database_name: str = "plantio"

    # Model and files
    model_path: str = "./models/plantio/model.pth"
    upload_dir: str = "./storage/uploads"

    # HTTP
    app_name: str = "Plantio API"
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS for the future front
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PLANTIO_",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def mongo_uri(self) -> str:
        """Auto-selection of URI depending on profile."""
        if self.env.lower() == "prod" and self.mongo_uri_atlas:
            return self.mongo_uri_atlas
        return self.mongo_uri_local


settings = Settings()
