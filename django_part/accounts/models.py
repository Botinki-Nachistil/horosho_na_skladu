from __future__ import annotations

import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from shared.db import schema_table

pin_validator = RegexValidator(r"^\d{4,6}$", "PIN must contain 4-6 digits.")


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        SUPERVISOR = "supervisor", "Supervisor"
        WORKER = "worker", "Worker"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.WORKER)
    warehouse = models.ForeignKey(
        "warehouse.Warehouse",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    pin_code = models.CharField(
        max_length=128,
        blank=True,
        help_text="4-6-digit PIN for quick mobile login",
    )
    shift = models.CharField(
        max_length=20,
        blank=True,
        help_text="Current or default shift identifier",
    )

    class Meta:
        db_table = schema_table("auth", "accounts_user")
        verbose_name = "user"
        verbose_name_plural = "users"

    def save(self, *args, **kwargs):
        if self.pin_code and self.pin_code.isdigit():
            pin_validator(self.pin_code)
            self.pin_code = make_password(self.pin_code)
        super().save(*args, **kwargs)

    def set_pin(self, raw_pin: str) -> None:
        pin_validator(raw_pin)
        self.pin_code = make_password(raw_pin)

    def check_pin(self, raw_pin: str) -> bool:
        return bool(self.pin_code) and check_password(raw_pin, self.pin_code)


class RefreshToken(models.Model):
    jti = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="refresh_tokens")
    exp = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = schema_table("auth", "refresh_tokens")
        indexes = [
            models.Index(fields=["jti"]),
            models.Index(fields=["user", "exp"]),
        ]


class RBACPermission(models.Model):
    role = models.CharField(max_length=20, choices=User.Role.choices)
    resource = models.CharField(max_length=64)
    action = models.CharField(max_length=32)

    class Meta:
        db_table = schema_table("auth", "rbac_permissions")
        constraints = [
            models.UniqueConstraint(
                fields=["role", "resource", "action"],
                name="rbac_permissions_role_resource_action_uniq",
            )
        ]


class AuditLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=64)
    entity_type = models.CharField(max_length=64)
    entity_id = models.BigIntegerField()
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = schema_table("auth", "accounts_auditlog")
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["created_at"]),
        ]
