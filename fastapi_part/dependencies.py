from __future__ import annotations

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from config import Settings, get_settings

bearer_scheme = HTTPBearer(auto_error=True)


class TokenPayload(BaseModel):
    user_id: int
    role: str
    warehouse_id: int | None = None


def _decode_token(token: str, settings: Settings) -> TokenPayload:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("user_id")
    role = payload.get("role")
    if user_id is None or not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    return TokenPayload(
        user_id=user_id,
        role=role,
        warehouse_id=payload.get("warehouse_id"),
    )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenPayload:
    return _decode_token(credentials.credentials, settings)


def require_role(*roles: str):
    async def _check(
        user: Annotated[TokenPayload, Depends(get_current_user)],
    ) -> TokenPayload:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {', '.join(roles)}",
            )
        return user
    return _check
