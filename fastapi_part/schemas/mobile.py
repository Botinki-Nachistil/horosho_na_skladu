from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class TaskSummary(BaseModel):
    id: int
    task_type: str
    status: str
    priority: int
    source_location_id: int | None
    target_location_id: int | None
    quantity: Decimal

    model_config = {"from_attributes": True}


class StepInfo(BaseModel):
    sequence: int
    action: str
    expected_qty: Decimal


class ScanRequest(BaseModel):
    scanned_barcode: str
    actual_qty: Decimal


class ScanResponse(BaseModel):
    valid: bool
    next_step: StepInfo | None = None
    mismatch_reason: str | None = None
