from __future__ import annotations

from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from warehouse.models import Location, Warehouse, Zone
from warehouse.serializers import LocationSerializer, WarehouseSerializer, ZoneSerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "address"]

    def get_queryset(self):
        user = self.request.user
        qs = Warehouse.objects.prefetch_related("zones")
        if user.role in (User.Role.MANAGER, User.Role.SUPERVISOR) and user.warehouse_id:
            return qs.filter(pk=user.warehouse_id)
        return qs


class ZoneViewSet(viewsets.ModelViewSet):
    serializer_class = ZoneSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Zone.objects.select_related("warehouse")
        warehouse_id = self.request.query_params.get("warehouse")
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        return qs


class LocationViewSet(viewsets.ModelViewSet):
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Location.objects.select_related("zone__warehouse")
        zone_id = self.request.query_params.get("zone")
        warehouse_id = self.request.query_params.get("warehouse")
        if zone_id:
            qs = qs.filter(zone_id=zone_id)
        if warehouse_id:
            qs = qs.filter(zone__warehouse_id=warehouse_id)
        return qs