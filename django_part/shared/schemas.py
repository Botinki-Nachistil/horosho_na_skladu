from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class WarehouseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str


class InventorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sku: str
    location_barcode: str
    quantity: Decimal
    reserved_qty: Decimal
    available_qty: Decimal


class TaskSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_type: str
    status: str
    priority: int
    created_at: datetime
