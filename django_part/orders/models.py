from __future__ import annotations

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from shared.db import schema_table


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        PICKING = "picking", "Picking"
        PACKED = "packed", "Packed"
        DONE = "done", "Done"

    warehouse = models.ForeignKey(
        "warehouse.Warehouse",
        on_delete=models.PROTECT,
        related_name="orders",
    )
    wave = models.ForeignKey(
        "operations.Wave",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    priority = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(9)],
        help_text="1 = highest, 9 = lowest",
    )
    customer = models.CharField(max_length=256, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = schema_table("warehouse", "orders_order")
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["warehouse", "status"]),
        ]

    def can_transition_to(self, target_status: str) -> bool:
        transitions = {
            self.Status.PENDING: {self.Status.PROCESSING},
            self.Status.PROCESSING: {self.Status.PICKING},
            self.Status.PICKING: {self.Status.PACKED},
            self.Status.PACKED: {self.Status.DONE},
            self.Status.DONE: set(),
        }
        return target_status in transitions[self.status]


class OrderLine(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="lines")
    item = models.ForeignKey("inventory.Item", on_delete=models.PROTECT)
    location = models.ForeignKey(
        "warehouse.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Assigned pick location",
    )
    qty_req = models.DecimalField(max_digits=12, decimal_places=3)
    qty_picked = models.DecimalField(max_digits=12, decimal_places=3, default=0)

    class Meta:
        db_table = schema_table("warehouse", "orders_orderline")
        indexes = [models.Index(fields=["order", "item"])]
