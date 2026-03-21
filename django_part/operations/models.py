from __future__ import annotations

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from shared.db import schema_table


class Wave(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        ACTIVE = "active", "Active"
        DONE = "done", "Done"

    warehouse = models.ForeignKey(
        "warehouse.Warehouse",
        on_delete=models.CASCADE,
        related_name="waves",
    )
    code = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = schema_table("operations", "operations_wave")
        indexes = [models.Index(fields=["warehouse", "status"])]


class Task(models.Model):
    class TaskType(models.TextChoices):
        PICKING = "picking", "Picking"
        PUTAWAY = "putaway", "Putaway"
        MOVE = "move", "Move"
        SHIPPING = "shipping", "Shipping"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ASSIGNED = "assigned", "Assigned"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"
        CANCELLED = "cancelled", "Cancelled"

    warehouse = models.ForeignKey(
        "warehouse.Warehouse",
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    wave = models.ForeignKey(
        Wave,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    assignee = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    task_type = models.CharField(max_length=20, choices=TaskType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    source_location = models.ForeignKey(
        "warehouse.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_tasks",
    )
    target_location = models.ForeignKey(
        "warehouse.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="target_tasks",
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    priority = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(9)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = schema_table("operations", "operations_task")
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["warehouse", "status"]),
        ]


class TaskStep(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="steps")
    sequence = models.PositiveIntegerField()
    action = models.CharField(max_length=64)
    location = models.ForeignKey(
        "warehouse.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_steps",
    )
    expected_barcode = models.CharField(max_length=64, blank=True)
    expected_qty = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    actual_qty = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = schema_table("operations", "operations_taskstep")
        constraints = [
            models.UniqueConstraint(
                fields=["task", "sequence"],
                name="operations_taskstep_task_sequence_uniq",
            )
        ]


class Route(models.Model):
    wave = models.ForeignKey(
        Wave,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="routes",
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="routes",
    )
    method = models.CharField(max_length=64, default="nearest_neighbor")
    points = models.JSONField(default=list)
    distance_m = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    eta_seconds = models.PositiveIntegerField(default=0)
    diagnostics = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = schema_table("operations", "operations_route")


class Event(models.Model):
    warehouse = models.ForeignKey(
        "warehouse.Warehouse",
        on_delete=models.CASCADE,
        related_name="events",
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    event_type = models.CharField(max_length=64)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = schema_table("operations", "operations_event")
        indexes = [models.Index(fields=["event_type", "created_at"])]


class IntegrationConfig(models.Model):
    class ChannelType(models.TextChoices):
        REST = "rest", "REST"
        CSV = "csv", "CSV"
        XML = "xml", "XML"
        SFTP = "sftp", "SFTP"

    class Direction(models.TextChoices):
        PULL = "pull", "Pull"
        PUSH = "push", "Push"

    warehouse = models.ForeignKey(
        "warehouse.Warehouse",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="integration_configs",
    )
    name = models.CharField(max_length=128)
    channel_type = models.CharField(max_length=20, choices=ChannelType.choices)
    direction = models.CharField(max_length=20, choices=Direction.choices)
    endpoint = models.CharField(max_length=256, blank=True)
    schedule = models.CharField(max_length=64, blank=True)
    settings = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = schema_table("operations", "operations_integrationconfig")


class IntegrationLog(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"

    config = models.ForeignKey(
        IntegrationConfig,
        on_delete=models.CASCADE,
        related_name="logs",
    )
    status = models.CharField(max_length=20, choices=Status.choices)
    attempt = models.PositiveIntegerField(default=1)
    payload = models.JSONField(default=dict)
    response = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = schema_table("operations", "operations_integrationlog")
        indexes = [models.Index(fields=["config", "created_at"])]


class KpiSnapshot(models.Model):
    warehouse = models.ForeignKey(
        "warehouse.Warehouse",
        on_delete=models.CASCADE,
        related_name="kpi_snapshots",
    )
    shift = models.CharField(max_length=20, blank=True)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    throughput_lines = models.PositiveIntegerField(default=0)
    throughput_orders = models.PositiveIntegerField(default=0)
    order_accuracy = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    dock_to_stock_p95 = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    sla_on_time = models.PositiveIntegerField(default=0)
    sla_overdue = models.PositiveIntegerField(default=0)
    active_minutes = models.PositiveIntegerField(default=0)
    idle_minutes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = schema_table("operations", "operations_kpisnapshot")
        indexes = [models.Index(fields=["warehouse", "period_start"])]
