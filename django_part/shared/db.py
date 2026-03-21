from __future__ import annotations

from django.conf import settings


def uses_sqlite() -> bool:
    return settings.DATABASES["default"]["ENGINE"].endswith("sqlite3")


def schema_table(schema: str, table: str) -> str:
    if uses_sqlite():
        return f"{schema}_{table}"
    return f'"{schema}".{table}'
