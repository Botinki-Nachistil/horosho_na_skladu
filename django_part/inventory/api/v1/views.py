from __future__ import annotations

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import IsManager, IsSupervisor
from inventory.api.v1.serializers import InventorySerializer, ItemSerializer
from inventory.models import Inventory, Item
from inventory.services import adjust_inventory


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["sku", "name", "barcode"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsManager()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Item.objects.all()
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        return qs


class InventoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InventorySerializer

    def get_permissions(self):
        if self.action == "adjust":
            return [IsSupervisor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Inventory.objects.select_related("item", "location__zone__warehouse")
        if user.role != User.Role.ADMIN:
            qs = qs.filter(location__zone__warehouse_id__in=user.accessible_warehouse_ids)
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

    @action(detail=True, methods=["post"], url_path="adjust")
    def adjust(self, request, pk=None):
        inv = self.get_object()
        qty = request.data.get("qty")
        if qty is None:
            return Response({"error": "qty is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            qty = float(qty)
        except (TypeError, ValueError):
            return Response({"error": "qty must be a number."}, status=status.HTTP_400_BAD_REQUEST)
        inv = adjust_inventory(inv.item, inv.location, qty)
        return Response(InventorySerializer(inv).data)
