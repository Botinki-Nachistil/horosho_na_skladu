from django.contrib import admin

from inventory.models import Inventory, Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "barcode", "unit", "is_active")
    list_filter = ("unit", "is_active")
    search_fields = ("sku", "name", "barcode")


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("item", "location", "quantity", "reserved_qty", "available_qty")
    list_filter = ("location__zone__warehouse",)
    search_fields = ("item__sku", "location__barcode")
