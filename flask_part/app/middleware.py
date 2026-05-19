from __future__ import annotations

from dataclasses import dataclass
from functools import wraps

import jwt
from flask import g, request

from app.config import get_settings
from app.exceptions import AuthenticationError, PermissionDeniedError


@dataclass
class TokenPayload:
    user_id: int
    role: str
    warehouse_id: int | None = None


def _decode_token(token: str) -> TokenPayload:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")

    user_id = payload.get("user_id")
    role = payload.get("role")
    if user_id is None or not role:
        raise AuthenticationError("Invalid token payload")

    return TokenPayload(
        user_id=user_id,
        role=role,
        warehouse_id=payload.get("warehouse_id"),
    )


def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise AuthenticationError("Authorization header missing or malformed")
        token = auth_header.removeprefix("Bearer ").strip()
        g.current_user = _decode_token(token)
        return fn(*args, **kwargs)
    return wrapper


def require_role(*roles: str):
    def decorator(fn):
        @wraps(fn)
        @jwt_required
        def wrapper(*args, **kwargs):
            if g.current_user.role not in roles:
                raise PermissionDeniedError(
                    f"Required role: {', '.join(roles)}"
                )
            return fn(*args, **kwargs)
        return wrapper
    return decorator
