from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import JSON, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Warehouse(db.Model):
    __tablename__ = "warehouse_warehouse"
    __table_args__ = {"schema": "warehouse"}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    address: Mapped[str] = mapped_column(Text, default="")
    config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Zone(db.Model):
    __tablename__ = "warehouse_zone"
    __table_args__ = {"schema": "warehouse"}

    id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouse.warehouse_warehouse.id"))
    name: Mapped[str] = mapped_column(String(64))
    zone_type: Mapped[str] = mapped_column(String(20))


class Location(db.Model):
    __tablename__ = "warehouse_location"
    __table_args__ = {"schema": "warehouse"}

    id: Mapped[int] = mapped_column(primary_key=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("warehouse.warehouse_zone.id"))
    barcode: Mapped[str] = mapped_column(String(64), unique=True)
    coords: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(default=True)


class Item(db.Model):
    __tablename__ = "inventory_item"
    __table_args__ = {"schema": "warehouse"}

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(256))
    barcode: Mapped[str] = mapped_column(String(64), unique=True)
    unit: Mapped[str] = mapped_column(String(20), default="pcs")
    is_active: Mapped[bool] = mapped_column(default=True)


class Order(db.Model):
    __tablename__ = "orders_order"
    __table_args__ = {"schema": "warehouse"}

    id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouse.warehouse_warehouse.id"))
    wave_id: Mapped[int | None] = mapped_column(ForeignKey("operations.operations_wave.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20))
    priority: Mapped[int] = mapped_column(default=5)
    customer: Mapped[str] = mapped_column(String(256), default="")
    deadline: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    lines: Mapped[list[OrderLine]] = relationship("OrderLine", back_populates="order", lazy="select")


class OrderLine(db.Model):
    __tablename__ = "orders_orderline"
    __table_args__ = {"schema": "warehouse"}

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("warehouse.orders_order.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("warehouse.inventory_item.id"))
    location_id: Mapped[int | None] = mapped_column(ForeignKey("warehouse.warehouse_location.id"), nullable=True)
    qty_req: Mapped[Decimal] = mapped_column(Numeric(12, 3))
    qty_picked: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0)

    order: Mapped[Order] = relationship("Order", back_populates="lines", lazy="select")
    item: Mapped[Item] = relationship("Item", lazy="select")


class Wave(db.Model):
    __tablename__ = "operations_wave"
    __table_args__ = {"schema": "operations"}

    id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouse.warehouse_warehouse.id"))
    code: Mapped[str] = mapped_column(String(64), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="planned")
    scheduled_at: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Task(db.Model):
    __tablename__ = "operations_task"
    __table_args__ = {"schema": "operations"}

    id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouse.warehouse_warehouse.id"))
    wave_id: Mapped[int | None] = mapped_column(ForeignKey("operations.operations_wave.id"), nullable=True)
    assignee_id: Mapped[int | None] = mapped_column(nullable=True)
    task_type: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    source_location_id: Mapped[int | None] = mapped_column(ForeignKey("warehouse.warehouse_location.id"), nullable=True)
    target_location_id: Mapped[int | None] = mapped_column(ForeignKey("warehouse.warehouse_location.id"), nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0)
    priority: Mapped[int] = mapped_column(default=5)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    assigned_at: Mapped[datetime | None]
    completed_at: Mapped[datetime | None]


class TaskStep(db.Model):
    __tablename__ = "operations_taskstep"
    __table_args__ = {"schema": "operations"}

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("operations.operations_task.id"))
    sequence: Mapped[int]
    action: Mapped[str] = mapped_column(String(64))
    location_id: Mapped[int | None] = mapped_column(ForeignKey("warehouse.warehouse_location.id"), nullable=True)
    expected_barcode: Mapped[str] = mapped_column(String(64), default="")
    expected_qty: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0)
    actual_qty: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0)
    completed_at: Mapped[datetime | None]
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)


class Route(db.Model):
    __tablename__ = "operations_route"
    __table_args__ = {"schema": "operations"}

    id: Mapped[int] = mapped_column(primary_key=True)
    wave_id: Mapped[int | None] = mapped_column(ForeignKey("operations.operations_wave.id"), nullable=True)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("operations.operations_task.id"), nullable=True)
    method: Mapped[str] = mapped_column(String(64), default="nearest_neighbor")
    points: Mapped[list[Any]] = mapped_column(JSON, default=list)
    distance_m: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    eta_seconds: Mapped[int] = mapped_column(default=0)
    diagnostics: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class IntegrationConfig(db.Model):
    __tablename__ = "operations_integrationconfig"
    __table_args__ = {"schema": "operations"}

    id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_id: Mapped[int | None] = mapped_column(ForeignKey("warehouse.warehouse_warehouse.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(128))
    channel_type: Mapped[str] = mapped_column(String(20))
    direction: Mapped[str] = mapped_column(String(20))
    endpoint: Mapped[str] = mapped_column(String(256), default="")
    schedule: Mapped[str] = mapped_column(String(64), default="")
    settings: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(default=True)

    logs: Mapped[list[IntegrationLog]] = relationship("IntegrationLog", back_populates="config", lazy="select")


class IntegrationLog(db.Model):
    __tablename__ = "operations_integrationlog"
    __table_args__ = {"schema": "operations"}

    id: Mapped[int] = mapped_column(primary_key=True)
    config_id: Mapped[int] = mapped_column(ForeignKey("operations.operations_integrationconfig.id"))
    status: Mapped[str] = mapped_column(String(20))
    attempt: Mapped[int] = mapped_column(default=1)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    response: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    error_message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    config: Mapped[IntegrationConfig] = relationship("IntegrationConfig", back_populates="logs", lazy="select")


class KpiSnapshot(db.Model):
    __tablename__ = "operations_kpisnapshot"
    __table_args__ = {"schema": "operations"}

    id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouse.warehouse_warehouse.id"))
    shift: Mapped[str] = mapped_column(String(20), default="")
    period_start: Mapped[datetime]
    period_end: Mapped[datetime]
    throughput_lines: Mapped[int] = mapped_column(default=0)
    throughput_orders: Mapped[int] = mapped_column(default=0)
    order_accuracy: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    dock_to_stock_p95: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=0)
    sla_on_time: Mapped[int] = mapped_column(default=0)
    sla_overdue: Mapped[int] = mapped_column(default=0)
    active_minutes: Mapped[int] = mapped_column(default=0)
    idle_minutes: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
