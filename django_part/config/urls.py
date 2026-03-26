from __future__ import annotations

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def healthcheck(_: object) -> JsonResponse:
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthcheck, name="healthcheck"),
    path("api/v1/", include("api.v1.urls")), 
]