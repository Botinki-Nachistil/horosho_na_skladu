from __future__ import annotations

from rest_framework import serializers

from warehouse.models import Location, Warehouse, Zone


class WarehouseSerializer(serializers.ModelSerializer):
    zones_count = serializers.SerializerMethodField()

    class Meta:
        model = Warehouse
        fields = ["id", "name", "address", "config", "created_at", "zones_count"]
        read_only_fields = ["id", "created_at"]

    def get_zones_count(self, instance: Warehouse) -> int:
        return len(instance.zones.all())


class ZoneSerializer(serializers.ModelSerializer):
    warehouse_id = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(),
        source="warehouse",
    )
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = Zone
        fields = ["id", "warehouse_id", "warehouse_name", "name", "zone_type"]
        read_only_fields = ["id", "warehouse_name"]


class LocationSerializer(serializers.ModelSerializer):
    zone_id = serializers.PrimaryKeyRelatedField(
        queryset=Zone.objects.all(),
        source="zone",
    )
    zone = ZoneSerializer(read_only=True)

    class Meta:
        model = Location
        fields = ["id", "zone_id", "zone", "barcode", "coords", "is_active"]
        read_only_fields = ["id", "zone"]
