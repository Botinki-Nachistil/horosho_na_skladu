from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("auth/", include("accounts.api.v1.urls")),
    path("", include("warehouse.api.v1.urls")),
    path("", include("inventory.api.v1.urls")),
    path("", include("orders.api.v1.urls")),
    path("", include("operations.api.v1.urls")),
]
