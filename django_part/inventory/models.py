from __future__ import annotations

from django.db import models
from django.db.models import DecimalField, F

from shared.db import schema_table


class Item(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=256)
    barcode = models.CharField(max_length=64, unique=True, blank=True)
    unit = models.CharField(max_length=20, default="pcs")
    weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    dimensions = models.JSONField(default=dict, help_text='{"l": 10, "w": 5, "h": 3}')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = schema_table("warehouse", "inventory_item")
        indexes = [models.Index(fields=["sku"]), models.Index(fields=["barcode"])]

    def __str__(self) -> str:
        return f"{self.sku} - {self.name}"


class Inventory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="inventory")
    location = models.ForeignKey(
        "warehouse.Location",
        on_delete=models.PROTECT,
        related_name="inventory",
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    reserved_qty = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    available_qty = models.GeneratedField(
        expression=F("quantity") - F("reserved_qty"),
        output_field=DecimalField(max_digits=12, decimal_places=3),
        db_persist=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = schema_table("warehouse", "inventory_inventory")
        constraints = [
            models.UniqueConstraint(
                fields=["item", "location"],
                name="inventory_item_location_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["item", "available_qty"]),
            models.Index(fields=["location"]),
        ]
