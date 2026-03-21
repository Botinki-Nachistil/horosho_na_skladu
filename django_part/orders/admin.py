from django.contrib import admin

from orders.models import Order, OrderLine


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "priority", "warehouse", "deadline")
    list_filter = ("status", "priority", "warehouse")
    inlines = [OrderLineInline]


@admin.register(OrderLine)
class OrderLineAdmin(admin.ModelAdmin):
    list_display = ("order", "item", "location", "qty_req", "qty_picked")
    list_filter = ("order__status",)
    search_fields = ("order__id", "item__sku", "location__barcode")
