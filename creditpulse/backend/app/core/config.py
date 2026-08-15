"""
config.py — Configuration centrale de l'application
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # ============================================================
    # APPLICATION
    # ============================================================

    APP_NAME: str = "CreditPulse API"
    DEBUG: bool = True

    # ============================================================
    # DATABASE
    # ============================================================

    DATABASE_URL: str = (
        "postgresql://postgres:12345@localhost:5432/creditpulse"
    )

    # ============================================================
    # SECURITY
    # ============================================================

    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ============================================================
    # MACHINE LEARNING
    # ============================================================

    MODEL_PATH: str = "ml/model_registry/model.json"

    # ============================================================
    # PYDANTIC SETTINGS
    # ============================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()