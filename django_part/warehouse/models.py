from __future__ import annotations

from django.db import models

from shared.db import schema_table


class Warehouse(models.Model):
    name = models.CharField(max_length=128)
    address = models.TextField(blank=True)
    config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = schema_table("warehouse", "warehouse_warehouse")

    def __str__(self) -> str:
        return self.name


class Zone(models.Model):
    class ZoneType(models.TextChoices):
        PICKING = "picking", "Picking"
        STORAGE = "storage", "Storage"
        SHIPPING = "shipping", "Shipping"
        RECEIVING = "receiving", "Receiving"

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="zones")
    name = models.CharField(max_length=64)
    zone_type = models.CharField(max_length=20, choices=ZoneType.choices)

    class Meta:
        db_table = schema_table("warehouse", "warehouse_zone")
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "name"],
                name="warehouse_zone_warehouse_name_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.warehouse.name}: {self.name}"


class Location(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="locations")
    barcode = models.CharField(max_length=64, unique=True)
    coords = models.JSONField(
        default=dict,
        help_text='{"aisle": 3, "rack": 5, "level": 2}',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = schema_table("warehouse", "warehouse_location")
        indexes = [models.Index(fields=["barcode"])]

    def __str__(self) -> str:
        return self.barcode
