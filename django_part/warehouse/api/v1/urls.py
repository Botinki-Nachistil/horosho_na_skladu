from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from warehouse.api.v1.views import LocationViewSet, WarehouseViewSet, ZoneViewSet

router = DefaultRouter()
router.register("warehouses", WarehouseViewSet, basename="warehouse")
router.register("zones", ZoneViewSet, basename="zone")
router.register("locations", LocationViewSet, basename="location")

urlpatterns = [
    path("", include(router.urls)),
]
