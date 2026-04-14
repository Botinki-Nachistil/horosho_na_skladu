from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from operations.api.v1.views import (
    EventViewSet,
    IntegrationConfigViewSet,
    IntegrationLogViewSet,
    KpiSnapshotViewSet,
    RouteViewSet,
    TaskViewSet,
    WaveViewSet,
)

router = DefaultRouter()
router.register("waves", WaveViewSet, basename="wave")
router.register("tasks", TaskViewSet, basename="task")
router.register("routes", RouteViewSet, basename="route")
router.register("integrations", IntegrationConfigViewSet, basename="integration-config")
router.register("integration-logs", IntegrationLogViewSet, basename="integration-log")
router.register("kpi", KpiSnapshotViewSet, basename="kpi")
router.register("events", EventViewSet, basename="event")

urlpatterns = [
    path("", include(router.urls)),
]
