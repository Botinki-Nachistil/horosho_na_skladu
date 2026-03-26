from __future__ import annotations

from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from inventory.models import Inventory, Item
from inventory.serializers import InventorySerializer, ItemSerializer


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["sku", "name", "barcode"]

    def get_queryset(self):
        qs = Item.objects.all()
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        return qs


class InventoryViewSet(viewsets.ModelViewSet):
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Inventory.objects.select_related("item", "location__zone__warehouse")
        location_id = self.request.query_params.get("location")
        item_id = self.request.query_params.get("item")
        warehouse_id = self.request.query_params.get("warehouse")
        if location_id:
            qs = qs.filter(location_id=location_id)
        if item_id:
            qs = qs.filter(item_id=item_id)
        if warehouse_id:
            qs = qs.filter(location__zone__warehouse_id=warehouse_id)
        return qs