from __future__ import annotations

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import IsAdmin, IsManager, IsSupervisor
from operations.models import (
    Event,
    IntegrationConfig,
    IntegrationLog,
    KpiSnapshot,
    Route,
    Task,
    Wave,
)
from operations.serializers import (
    EventSerializer,
    IntegrationConfigSerializer,
    IntegrationLogSerializer,
    KpiSnapshotSerializer,
    RouteSerializer,
    TaskAssignSerializer,
    TaskSerializer,
    TaskWriteSerializer,
    WaveSerializer,
)
from operations.services import (
    activate_wave,
    assign_task,
    cancel_task,
    complete_task,
    start_task,
)


class WaveViewSet(viewsets.ModelViewSet):
    serializer_class = WaveSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsManager()]
        if self.action == "activate":
            return [IsSupervisor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Wave.objects.select_related("warehouse").prefetch_related("tasks")
        if user.role != User.Role.ADMIN:
            qs = qs.filter(warehouse_id__in=user.accessible_warehouse_ids)
        warehouse_id = self.request.query_params.get("warehouse")
        status_param = self.request.query_params.get("status")
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        wave = activate_wave(self.get_object())
        return Response(WaveSerializer(wave).data)


class TaskViewSet(viewsets.ModelViewSet):

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "assign", "cancel"):
            return [IsSupervisor()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return TaskWriteSerializer
        return TaskSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.select_related(
            "warehouse", "wave", "assignee",
            "source_location", "target_location",
        ).prefetch_related("steps")

        if user.role == User.Role.WORKER:
            qs = qs.filter(assignee=user)
        elif user.role != User.Role.ADMIN:
            qs = qs.filter(warehouse_id__in=user.accessible_warehouse_ids)

        status_param = self.request.query_params.get("status")
        task_type = self.request.query_params.get("task_type")
        wave_id = self.request.query_params.get("wave")
        warehouse_id = self.request.query_params.get("warehouse")

        if status_param:
            qs = qs.filter(status=status_param)
        if task_type:
            qs = qs.filter(task_type=task_type)
        if wave_id:
            qs = qs.filter(wave_id=wave_id)
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)

        return qs.order_by("priority", "created_at")

    @action(detail=True, methods=["post"], url_path="assign")
    def assign(self, request, pk=None):
        serializer = TaskAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = assign_task(self.get_object(), serializer.validated_data["user_id"])
        return Response(TaskSerializer(task).data)

    @action(detail=True, methods=["post"], url_path="start")
    def start(self, request, pk=None):
        task = start_task(self.get_object())
        return Response(TaskSerializer(task).data)

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        task = complete_task(self.get_object())
        return Response(TaskSerializer(task).data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        task = cancel_task(self.get_object())
        return Response(TaskSerializer(task).data)


class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Route.objects.select_related("wave", "task")
        if user.role == User.Role.WORKER:
            qs = qs.filter(task__assignee=user)
        elif user.role != User.Role.ADMIN:
            qs = qs.filter(task__warehouse_id__in=user.accessible_warehouse_ids)
        task_id = self.request.query_params.get("task")
        wave_id = self.request.query_params.get("wave")
        if task_id:
            qs = qs.filter(task_id=task_id)
        if wave_id:
            qs = qs.filter(wave_id=wave_id)
        return qs


class IntegrationConfigViewSet(viewsets.ModelViewSet):
    serializer_class = IntegrationConfigSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return IntegrationConfig.objects.select_related("warehouse")


class IntegrationLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IntegrationLogSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = IntegrationLog.objects.select_related("config").order_by("-created_at")
        config_id = self.request.query_params.get("config")
        if config_id:
            qs = qs.filter(config_id=config_id)
        return qs


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Event.objects.select_related("warehouse", "user", "task").order_by("-created_at")
        if user.role == User.Role.WORKER:
            qs = qs.filter(user=user)
        elif user.role != User.Role.ADMIN:
            qs = qs.filter(warehouse_id__in=user.accessible_warehouse_ids)
        event_type = self.request.query_params.get("event_type")
        task_id = self.request.query_params.get("task")
        if event_type:
            qs = qs.filter(event_type=event_type)
        if task_id:
            qs = qs.filter(task_id=task_id)
        return qs


class KpiSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = KpiSnapshotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = KpiSnapshot.objects.select_related("warehouse").order_by("-period_start")
        if user.role != User.Role.ADMIN:
            qs = qs.filter(warehouse_id__in=user.accessible_warehouse_ids)
        warehouse_id = self.request.query_params.get("warehouse")
        shift = self.request.query_params.get("shift")
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        if shift:
            qs = qs.filter(shift=shift)
        return qs
