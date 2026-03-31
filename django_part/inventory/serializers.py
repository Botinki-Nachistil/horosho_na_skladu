from __future__ import annotations

from rest_framework import serializers

from inventory.models import Inventory, Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "sku", "name", "barcode", "unit", "weight", "dimensions", "is_active"]
        read_only_fields = ["id"]

    def validate_dimensions(self, value: dict) -> dict:
        if not isinstance(value, dict):
            raise serializers.ValidationError("dimensions must be a JSON object.")
        for key, val in value.items():
            if not isinstance(val, (int, float)):
                raise serializers.ValidationError(
                    f"dimensions['{key}'] must be a number, got {type(val).__name__}."
                )
        return value


class InventorySerializer(serializers.ModelSerializer):
    item_sku = serializers.CharField(source="item.sku", read_only=True)
    location_barcode = serializers.CharField(source="location.barcode", read_only=True)
    available_qty = serializers.DecimalField(max_digits=12, decimal_places=3, read_only=True)

    class Meta:
        model = Inventory
        fields = [
            "id",
            "item",
            "item_sku",
            "location",
            "location_barcode",
            "quantity",
            "reserved_qty",
            "available_qty",
            "updated_at",
        ]
        read_only_fields = ["id", "item", "location", "quantity", "reserved_qty", "available_qty", "updated_at", "item_sku", "location_barcode"]
