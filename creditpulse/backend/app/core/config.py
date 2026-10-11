"""Validated configuration shared by local commands and containers."""
from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

PROJECT_ROOT = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    APP_NAME: str = "CreditPulse API"
    DEBUG: bool = False
    POSTGRES_USER: str = "creditpulse"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "creditpulse_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = ""
    SECRET_KEY: str
    ALGORITHM: str = Field(default="HS256", validation_alias=AliasChoices("ALGORITHM", "JWT_ALGORITHM"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0)
    MODEL_PATH: Path = PROJECT_ROOT / "ml/model_registry/model.json"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8",
        case_sensitive=False, extra="ignore", populate_by_name=True,
    )

    @model_validator(mode="after")
    def validate_configuration(self):
        secret = self.SECRET_KEY.strip()
        if len(secret) < 32 or secret.lower().startswith(("change", "replace")):
            raise ValueError("SECRET_KEY must be a generated secret of at least 32 characters.")
        if self.ALGORITHM != "HS256":
            raise ValueError("This deployment supports ALGORITHM=HS256 only.")
        if "*" in self.CORS_ORIGINS:
            raise ValueError("CORS_ORIGINS must list explicit frontend origins.")
        if not self.DATABASE_URL:
            if not self.POSTGRES_PASSWORD:
                raise ValueError("Set DATABASE_URL or POSTGRES_PASSWORD.")
            self.DATABASE_URL = URL.create(
                "postgresql+psycopg2", username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD, host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT, database=self.POSTGRES_DB,
            ).render_as_string(hide_password=False)
        if not self.MODEL_PATH.is_absolute():
            self.MODEL_PATH = PROJECT_ROOT / self.MODEL_PATH
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
