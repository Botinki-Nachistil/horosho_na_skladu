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
    scanned_qty: Decimal


class ScanResponse(BaseModel):
    ok: bool
    step_completed: bool
    mismatch_reason: str | None = None
    next_step: StepInfo | None = None
    task_completed: bool
