from django.contrib import admin

from warehouse.models import Location, Warehouse, Zone


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "created_at")
    search_fields = ("name", "address")


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "zone_type", "warehouse")
    list_filter = ("zone_type", "warehouse")
    search_fields = ("name", "warehouse__name")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("barcode", "zone", "is_active")
    list_filter = ("is_active", "zone__warehouse", "zone__zone_type")
    search_fields = ("barcode", "zone__name", "zone__warehouse__name")
