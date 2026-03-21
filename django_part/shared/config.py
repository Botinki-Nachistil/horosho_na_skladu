from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class AppConfig:
    secret_key: str
    jwt_secret: str
    jwt_algorithm: str
    database_dsn: str


def load_app_config() -> AppConfig:
    return AppConfig(
        secret_key=os.getenv("DJANGO_SECRET_KEY", "dev-secret-key-change-me"),
        jwt_secret=os.getenv(
            "JWT_SECRET",
            "jwt-secret-change-me-at-least-32-bytes",
        ),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        database_dsn=os.getenv("DATABASE_DSN", ""),
    )
