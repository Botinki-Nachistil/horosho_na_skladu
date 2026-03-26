from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("auth/", include("accounts.urls")),
    path("warehouses/", include("warehouse.urls")),
    path("inventory/", include("inventory.urls")),
    path("orders/", include("orders.urls")),
    path("operations/", include("operations.urls")),
]