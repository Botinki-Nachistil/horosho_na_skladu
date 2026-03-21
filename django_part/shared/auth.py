from __future__ import annotations

from typing import Any

import jwt

from shared.config import load_app_config
from shared.exceptions import TokenValidationError


def encode_token(payload: dict[str, Any]) -> str:
    cfg = load_app_config()
    return jwt.encode(payload, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    cfg = load_app_config()
    try:
        return jwt.decode(token, cfg.jwt_secret, algorithms=[cfg.jwt_algorithm])
    except jwt.PyJWTError as exc:  # type: ignore[attr-defined]
        raise TokenValidationError(str(exc)) from exc
