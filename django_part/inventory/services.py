from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from shared.exceptions import ValidationError
from inventory.models import Inventory, Item
from warehouse.models import Location


def _to_decimal(qty) -> Decimal:
    return Decimal(str(qty))


def reserve_inventory(item: Item, location: Location, qty) -> Inventory:
    qty = _to_decimal(qty)
    if qty <= 0:
        raise ValidationError("qty must be greater than zero.")
    with transaction.atomic():
        try:
            inv = Inventory.objects.select_for_update().get(item=item, location=location)
        except Inventory.DoesNotExist:
            raise ValidationError("Inventory record not found.")
        if inv.available_qty < qty:
            raise ValidationError("Not enough available quantity.")
        inv.reserved_qty += qty
        inv.save(update_fields=["reserved_qty"])
        inv.refresh_from_db(fields=["available_qty"])
        return inv


def release_inventory(item: Item, location: Location, qty) -> Inventory:
    qty = _to_decimal(qty)
    if qty <= 0:
        raise ValidationError("qty must be greater than zero.")
    with transaction.atomic():
        try:
            inv = Inventory.objects.select_for_update().get(item=item, location=location)
        except Inventory.DoesNotExist:
            raise ValidationError("Inventory record not found.")
        inv.reserved_qty = max(Decimal(0), inv.reserved_qty - qty)
        inv.save(update_fields=["reserved_qty"])
        inv.refresh_from_db(fields=["available_qty"])
        return inv


def adjust_inventory(item: Item, location: Location, qty) -> Inventory:
    qty = _to_decimal(qty)
    if qty < 0:
        raise ValidationError("qty cannot be negative.")
    with transaction.atomic():
        inv, _ = Inventory.objects.select_for_update().get_or_create(
            item=item,
            location=location,
            defaults={"quantity": 0, "reserved_qty": 0},
        )
        if qty < inv.reserved_qty:
            raise ValidationError(
                f"Cannot set qty to {qty}: {inv.reserved_qty} units are already reserved."
            )
        inv.quantity = qty
        inv.save(update_fields=["quantity"])
        inv.refresh_from_db(fields=["available_qty"])
        return inv
