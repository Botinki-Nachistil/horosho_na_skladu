from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    postgres_dsn: str = "postgresql+asyncpg://warehouse:warehouse@postgres:5432/warehouse_db"
    redis_url: str = "redis://redis:6379/0"
    jwt_secret: str = "jwt-secret-change-me-at-least-32-bytes"
    jwt_algorithm: str = "HS256"
    debug: bool = False
    cors_origins: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
