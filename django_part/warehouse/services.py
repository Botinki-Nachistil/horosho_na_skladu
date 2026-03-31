from __future__ import annotations

from warehouse.models import Location, Warehouse, Zone


def create_warehouse(name: str, address: str = "") -> Warehouse:
    return Warehouse.objects.create(name=name, address=address)


def create_zone(warehouse: Warehouse, name: str, zone_type: str) -> Zone:
    return Zone.objects.create(warehouse=warehouse, name=name, zone_type=zone_type)


def create_location(zone: Zone, barcode: str, coords: dict) -> Location:
    return Location.objects.create(zone=zone, barcode=barcode, coords=coords)


def deactivate_location(location: Location) -> Location:
    location.is_active = False
    location.save(update_fields=["is_active"])
    return location


def activate_location(location: Location) -> Location:
    location.is_active = True
    location.save(update_fields=["is_active"])
    return location