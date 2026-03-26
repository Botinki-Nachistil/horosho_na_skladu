from __future__ import annotations

from django.contrib.auth import authenticate

from accounts.models import User
from shared.exceptions import TokenValidationError, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken


def login_user(username: str | None, password: str | None, request) -> dict:
    if not username or not password:
        raise ValidationError("username and password are required.")
    user = authenticate(request, username=username, password=password)
    if not user:
        raise TokenValidationError("Invalid username or password.")
    if not user.is_active:
        raise TokenValidationError("Account is disabled.")
    return _make_token_response(user)


def pin_login(pin: str | None, warehouse_id: int | None) -> dict:
    if not pin or not pin.isdigit() or not (4 <= len(pin) <= 6):
        raise ValidationError("PIN must be 4-6 digits.")
    qs = User.objects.filter(role=User.Role.WORKER, is_active=True)
    if warehouse_id:
        qs = qs.filter(warehouse_id=warehouse_id)
    matched = next((u for u in qs if u.check_pin(pin)), None)
    if not matched:
        raise TokenValidationError("Invalid PIN.")
    return _make_token_response(matched)


def refresh_token(token: str | None) -> dict:
    if not token:
        raise ValidationError("refresh token is required.")
    try:
        refresh = RefreshToken(token)
        return {"access": str(refresh.access_token)}
    except Exception:
        raise TokenValidationError("Token is invalid or expired.")


def set_user_active(user: User, is_active: bool) -> User:
    user.is_active = is_active
    user.save(update_fields=["is_active"])
    return user


def _make_token_response(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    refresh["role"] = user.role
    refresh["warehouse_id"] = user.warehouse_id
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user_id": user.id,
        "role": user.role,
        "warehouse_id": user.warehouse_id,
    }