from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import AuditLog


def _json_ready(value):
    if isinstance(value, (date, datetime, Decimal, UUID)):
        return str(value)
    return value


def _serialize_instance(instance) -> dict:
    return {
        field.name: _json_ready(field.value_from_object(instance))
        for field in instance._meta.concrete_fields
        if field.name != "password"
    }


def _register(sender_label: str) -> None:
    sender = apps.get_model(sender_label)

    @receiver(post_save, sender=sender, weak=False, dispatch_uid=f"audit_{sender_label}")
    def audit_handler(sender, instance, created, **kwargs):  # type: ignore[no-redef]
        if kwargs.get("raw"):
            return
        if getattr(instance, "_skip_audit", False):
            return
        AuditLog.objects.create(
            action="create" if created else "update",
            entity_type=sender.__name__.lower(),
            entity_id=instance.pk,
            details={"model": sender.__name__, "state": _serialize_instance(instance)},
        )


for label in ["orders.Order", "operations.Task", "inventory.Inventory"]:
    _register(label)
