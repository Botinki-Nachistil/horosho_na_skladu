from __future__ import annotations

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import IsManager
from warehouse.models import Location, Warehouse, Zone
from warehouse.serializers import LocationSerializer, WarehouseSerializer, ZoneSerializer
from warehouse.services import activate_location, deactivate_location


class WarehouseViewSet(viewsets.ModelViewSet):
    serializer_class = WarehouseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "address"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsManager()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Warehouse.objects.prefetch_related("zones")
        if user.role == User.Role.WORKER:
            return qs.filter(pk=user.warehouse_id)
        if user.role in (User.Role.MANAGER, User.Role.SUPERVISOR):
            return qs.filter(pk__in=user.accessible_warehouse_ids)
        return qs


class ZoneViewSet(viewsets.ModelViewSet):
    serializer_class = ZoneSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsManager()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Zone.objects.select_related("warehouse")
        if user.role != User.Role.ADMIN:
            qs = qs.filter(warehouse_id__in=user.accessible_warehouse_ids)
        warehouse_id = self.request.query_params.get("warehouse")
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        return qs


class LocationViewSet(viewsets.ModelViewSet):
    serializer_class = LocationSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "activate", "deactivate"):
            return [IsManager()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Location.objects.select_related("zone__warehouse")
        if user.role != User.Role.ADMIN:
            qs = qs.filter(zone__warehouse_id__in=user.accessible_warehouse_ids)
        zone_id = self.request.query_params.get("zone")
        warehouse_id = self.request.query_params.get("warehouse")
        if zone_id:
            qs = qs.filter(zone_id=zone_id)
        if warehouse_id:
            qs = qs.filter(zone__warehouse_id=warehouse_id)
        return qs

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        deactivate_location(self.get_object())
        return Response({"message": "Location deactivated."})

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        activate_location(self.get_object())
        return Response({"message": "Location activated."})