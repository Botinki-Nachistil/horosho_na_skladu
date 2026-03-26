from __future__ import annotations

from shared.exceptions import ValidationError
from inventory.models import Inventory, Item
from warehouse.models import Location


def reserve_inventory(item: Item, location: Location, qty) -> Inventory:
    try:
        inv = Inventory.objects.get(item=item, location=location)
    except Inventory.DoesNotExist:
        raise ValidationError("Inventory record not found.")
    if inv.available_qty < qty:
        raise ValidationError("Not enough available quantity.")
    inv.reserved_qty += qty
    inv.save(update_fields=["reserved_qty"])
    return inv


def release_inventory(item: Item, location: Location, qty) -> Inventory:
    try:
        inv = Inventory.objects.get(item=item, location=location)
    except Inventory.DoesNotExist:
        raise ValidationError("Inventory record not found.")
    inv.reserved_qty = max(0, inv.reserved_qty - qty)
    inv.save(update_fields=["reserved_qty"])
    return inv


def adjust_inventory(item: Item, location: Location, qty) -> Inventory:
    inv, _ = Inventory.objects.get_or_create(
        item=item,
        location=location,
        defaults={"quantity": 0, "reserved_qty": 0},
    )
    inv.quantity = qty
    inv.save(update_fields=["quantity"])
    return inv