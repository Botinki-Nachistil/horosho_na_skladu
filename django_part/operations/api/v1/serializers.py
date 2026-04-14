from __future__ import annotations

from rest_framework import serializers

from operations.models import (
    Event,
    IntegrationConfig,
    IntegrationLog,
    KpiSnapshot,
    Route,
    Task,
    TaskStep,
    Wave,
)


class TaskStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStep
        fields = [
            "id",
            "task",
            "sequence",
            "action",
            "location",
            "expected_barcode",
            "expected_qty",
            "actual_qty",
            "completed_at",
            "metadata",
        ]
        read_only_fields = ["id"]


class TaskSerializer(serializers.ModelSerializer):
    steps = TaskStepSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "warehouse",
            "wave",
            "assignee",
            "task_type",
            "status",
            "source_location",
            "target_location",
            "quantity",
            "priority",
            "created_at",
            "assigned_at",
            "completed_at",
            "steps",
        ]
        read_only_fields = ["id", "status", "assignee", "assigned_at", "completed_at", "created_at", "steps"]


class TaskWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "warehouse",
            "wave",
            "task_type",
            "source_location",
            "target_location",
            "quantity",
            "priority",
        ]


class TaskAssignSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


class WaveSerializer(serializers.ModelSerializer):
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Wave
        fields = ["id", "warehouse", "code", "status", "scheduled_at", "created_at", "tasks_count"]
        read_only_fields = ["id", "status", "created_at"]

    def get_tasks_count(self, instance: Wave) -> int:
        return instance.tasks.count()


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = [
            "id",
            "wave",
            "task",
            "method",
            "points",
            "distance_m",
            "eta_seconds",
            "diagnostics",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "warehouse", "user", "task", "event_type", "payload", "created_at"]
        read_only_fields = ["id", "created_at"]


class IntegrationConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationConfig
        fields = [
            "id",
            "warehouse",
            "name",
            "channel_type",
            "direction",
            "endpoint",
            "schedule",
            "settings",
            "is_active",
        ]
        read_only_fields = ["id"]


class IntegrationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationLog
        fields = ["id", "config", "status", "attempt", "payload", "response", "error_message", "created_at"]
        read_only_fields = ["id", "created_at"]


class KpiSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = KpiSnapshot
        fields = [
            "id",
            "warehouse",
            "shift",
            "period_start",
            "period_end",
            "throughput_lines",
            "throughput_orders",
            "order_accuracy",
            "dock_to_stock_p95",
            "sla_on_time",
            "sla_overdue",
            "active_minutes",
            "idle_minutes",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "warehouse",
            "shift",
            "period_start",
            "period_end",
            "throughput_lines",
            "throughput_orders",
            "order_accuracy",
            "dock_to_stock_p95",
            "sla_on_time",
            "sla_overdue",
            "active_minutes",
            "idle_minutes",
            "created_at",
        ]
