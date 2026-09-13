from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables (.env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"

    database_url: str = "postgresql+psycopg2://hangugeo:hangugeo@localhost:5432/hangugeo"

    jwt_secret_key: str = "changeme-dev-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    cors_allow_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
