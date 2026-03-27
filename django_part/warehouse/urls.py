from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from warehouse.views import LocationViewSet, WarehouseViewSet, ZoneViewSet

zone_router = DefaultRouter()
zone_router.register(r"", ZoneViewSet, basename="zone")

location_router = DefaultRouter()
location_router.register(r"", LocationViewSet, basename="location")

warehouse_router = DefaultRouter()
warehouse_router.register(r"", WarehouseViewSet, basename="warehouse")

urlpatterns = [
    path("zones/", include(zone_router.urls)),
    path("locations/", include(location_router.urls)),
    path("", include(warehouse_router.urls)),
]
