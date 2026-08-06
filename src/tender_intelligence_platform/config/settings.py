"""
Application configuration.

All environment variables are loaded and validated here.
No other module should directly access os.environ.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Tender Intelligence Platform"
    app_version: str = "0.1.0"
    debug: bool = False

    http_timeout: int = 30
    max_retries: int = 3

    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    print("Current working directory:", Path.cwd())
    print(".env exists:", Path(".env").exists())
    return Settings()


settings = get_settings()