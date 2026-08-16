from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized, typed application configuration.

    Values are loaded from environment variables (and, in development,
    from a `.env` file). Pydantic validates types and raises a clear
    error at startup if something required is missing or malformed,
    instead of failing later with a confusing runtime error.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    environment: str = "development"  # development | testing | staging | production
    api_v1_prefix: str = "/api/v1"

    # --- Database ---
    database_url: str

    # --- CORS (kept minimal for now, revisited later) ---
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.

    lru_cache ensures the .env file / environment is only parsed once,
    and every part of the app that calls get_settings() shares the
    same object instead of re-reading and re-validating config repeatedly.
    """
    return Settings()
