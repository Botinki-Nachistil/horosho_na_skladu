from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import JSON, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Warehouse(Base):
    __tablename__ = "warehouse_warehouse"
    __table_args__ = {"schema": "warehouse"}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    address: Mapped[str] = mapped_column(Text, default="")
    config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Zone(Base):
    __tablename__ = "warehouse_zone"
    __table_args__ = {"schema": "warehouse"}

    id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouse.warehouse_warehouse.id"))
    name: Mapped[str] = mapped_column(String(64))
    zone_type: Mapped[str] = mapped_column(String(20))


class Location(Base):
    __tablename__ = "warehouse_location"
    __table_args__ = {"schema": "warehouse"}

    id: Mapped[int] = mapped_column(primary_key=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("warehouse.warehouse_zone.id"))
    barcode: Mapped[str] = mapped_column(String(64), unique=True)
    coords: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(default=True)


class Item(Base):
    __tablename__ = "inventory_item"
    __table_args__ = {"schema": "warehouse"}

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(256))
    barcode: Mapped[str] = mapped_column(String(64), unique=True)
    unit: Mapped[str] = mapped_column(String(20), default="pcs")
    is_active: Mapped[bool] = mapped_column(default=True)


class Order(Base):
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

    lines: Mapped[list[OrderLine]] = relationship(
        "OrderLine", back_populates="order", lazy="selectin"
    )


class OrderLine(Base):
    __tablename__ = "orders_orderline"
    __table_args__ = {"schema": "warehouse"}

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("warehouse.orders_order.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("warehouse.inventory_item.id"))
    location_id: Mapped[int | None] = mapped_column(ForeignKey("warehouse.warehouse_location.id"), nullable=True)
    qty_req: Mapped[Decimal] = mapped_column(Numeric(12, 3))
    qty_picked: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0)

    order: Mapped[Order] = relationship("Order", back_populates="lines", lazy="noload")
    item: Mapped[Item] = relationship("Item", lazy="noload")
    location: Mapped[Location | None] = relationship("Location", lazy="noload")


class Wave(Base):
    __tablename__ = "operations_wave"
    __table_args__ = {"schema": "operations"}

    id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouse.warehouse_warehouse.id"))
    code: Mapped[str] = mapped_column(String(64), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="planned")
    scheduled_at: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    tasks: Mapped[list[Task]] = relationship(
        "Task", back_populates="wave", lazy="noload"
    )


class Task(Base):
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

    wave: Mapped[Wave | None] = relationship("Wave", back_populates="tasks", lazy="noload")
    steps: Mapped[list[TaskStep]] = relationship(
        "TaskStep", back_populates="task", lazy="noload"
    )


class TaskStep(Base):
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

    task: Mapped[Task] = relationship("Task", back_populates="steps", lazy="noload")


class Route(Base):
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
