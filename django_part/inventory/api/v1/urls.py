from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from inventory.api.v1.views import InventoryViewSet, ItemViewSet

router = DefaultRouter()
router.register("items", ItemViewSet, basename="item")
router.register("inventory", InventoryViewSet, basename="inventory")

urlpatterns = [
    path("", include(router.urls)),
]
