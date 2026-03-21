from django.contrib import admin

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


@admin.register(Wave)
class WaveAdmin(admin.ModelAdmin):
    list_display = ("code", "warehouse", "status", "scheduled_at")
    list_filter = ("status", "warehouse")
    search_fields = ("code",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "task_type", "status", "priority", "warehouse", "assignee")
    list_filter = ("task_type", "status", "warehouse")
    search_fields = ("id", "assignee__username")


@admin.register(TaskStep)
class TaskStepAdmin(admin.ModelAdmin):
    list_display = ("task", "sequence", "action", "location", "completed_at")
    list_filter = ("action",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("id", "method", "distance_m", "eta_seconds", "created_at")
    search_fields = ("method",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "warehouse", "user", "task", "created_at")
    list_filter = ("event_type", "warehouse")


@admin.register(IntegrationConfig)
class IntegrationConfigAdmin(admin.ModelAdmin):
    list_display = ("name", "channel_type", "direction", "warehouse", "is_active")
    list_filter = ("channel_type", "direction", "is_active")


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ("config", "status", "attempt", "created_at")
    list_filter = ("status", "config")


@admin.register(KpiSnapshot)
class KpiSnapshotAdmin(admin.ModelAdmin):
    list_display = ("warehouse", "shift", "period_start", "period_end", "throughput_orders")
    list_filter = ("warehouse", "shift")
