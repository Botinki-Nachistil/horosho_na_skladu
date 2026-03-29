from __future__ import annotations

from django.contrib.auth import authenticate

from accounts.models import User
from shared.exceptions import PermissionDeniedError, TokenValidationError, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

_ALLOWED_ROLE_CREATION: dict[str, list[str]] = {
    User.Role.ADMIN: [User.Role.MANAGER, User.Role.SUPERVISOR, User.Role.WORKER],
    User.Role.MANAGER: [User.Role.SUPERVISOR, User.Role.WORKER],
    User.Role.SUPERVISOR: [User.Role.WORKER],
}


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


def create_user(
    creator: User,
    username: str,
    role: str,
    warehouse_id: int,
    password: str,
    first_name: str = "",
    last_name: str = "",
    pin: str | None = None,
) -> User:
    allowed = _ALLOWED_ROLE_CREATION.get(creator.role, [])
    if role not in allowed:
        raise PermissionDeniedError(
            f"Role '{creator.role}' cannot create users with role '{role}'."
        )
    user = User(
        username=username,
        role=role,
        warehouse_id=warehouse_id,
        first_name=first_name,
        last_name=last_name,
    )
    user.set_password(password)
    if pin:
        user.set_pin(pin)
    user.save()
    return user


def update_user(user: User, **fields) -> User:
    allowed = {"first_name", "last_name", "email", "shift"}
    update_fields = [k for k in fields if k in allowed]
    for k in update_fields:
        setattr(user, k, fields[k])
    if update_fields:
        user.save(update_fields=update_fields)
    return user


def change_password(user: User, old_password: str, new_password: str) -> User:
    if not user.check_password(old_password):
        raise ValidationError("Current password is incorrect.")
    user.set_password(new_password)
    user.save(update_fields=["password"])
    return user


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
