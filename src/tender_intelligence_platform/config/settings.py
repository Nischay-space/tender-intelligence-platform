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

    cppp_base_url: str
    cppp_home_url: str

    database_url: str

    cors_allowed_origins: str = (
        "http://localhost:3000,http://localhost:5173"
    )

    ingestion_interval_seconds: int = 900

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    print("Current working directory:", Path.cwd())
    print(".env exists:", Path(".env").exists())
    return Settings()


settings = get_settings()