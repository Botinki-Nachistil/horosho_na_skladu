from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import (
    DomainValidationError,
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
)
from models.sa_models import Task, TaskStep
from schemas.mobile import ScanResponse, StepInfo

LOCATION_ACTIONS = {
    "scan_location",
    "pick_location",
    "put_location",
    "scan-source",
    "confirm-target",
}


@dataclass(frozen=True)
class TaskCompletionEvent:
    task_id: int
    assignee_id: int | None
    warehouse_id: int
    completed_at: datetime


async def get_my_tasks(db: AsyncSession, user_id: int) -> list[Task]:
    result = await db.execute(
        select(Task)
        .where(
            Task.assignee_id == user_id,
            Task.status.in_(["assigned", "in_progress"]),
        )
        .order_by(Task.priority.desc())
    )
    return list(result.scalars().all())


async def accept_task(
    db: AsyncSession,
    task_id: int,
    user_id: int,
    warehouse_id: int | None,
) -> Task:
    task = await _get_task_or_404(db, task_id, for_update=True)
    _check_warehouse(task, warehouse_id)
    if task.status != "pending":
        raise InvalidStateError(f"Task is '{task.status}', expected 'pending'")
    task.assignee_id = user_id
    task.status = "assigned"
    task.assigned_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(task)
    return task


async def start_task(db: AsyncSession, task_id: int, user_id: int) -> Task:
    task = await _get_task_or_404(db, task_id, for_update=True)
    _check_owner(task, user_id)
    if task.status != "assigned":
        raise InvalidStateError(f"Task is '{task.status}', expected 'assigned'")
    task.status = "in_progress"
    await db.commit()
    await db.refresh(task)
    return task


async def complete_task(
    db: AsyncSession,
    task_id: int,
    user_id: int,
) -> tuple[Task, TaskCompletionEvent | None]:
    task = await _get_task_or_404(db, task_id, for_update=True)
    _check_owner(task, user_id)
    if task.status == "done":
        return task, None
    if task.status != "in_progress":
        raise InvalidStateError(f"Task is '{task.status}', expected 'in_progress'")
    task.status = "done"
    task.completed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(task)
    return task, _completion_event(task)


async def verify_scan(
    db: AsyncSession,
    task_id: int,
    step_seq: int,
    user_id: int,
    scanned_barcode: str,
    actual_qty: Decimal,
) -> tuple[ScanResponse, TaskCompletionEvent | None]:
    task = await _get_task_or_404(db, task_id, for_update=True)
    _check_owner(task, user_id)
    if task.status != "in_progress":
        raise InvalidStateError("Task must be in_progress to verify scans")

    step_result = await db.execute(
        select(TaskStep)
        .where(TaskStep.task_id == task_id, TaskStep.sequence == step_seq)
        .with_for_update()
    )
    step = step_result.scalar_one_or_none()
    if step is None:
        raise NotFoundError(f"Step {step_seq} not found for task {task_id}")
    if step.completed_at is not None:
        raise InvalidStateError("Step already completed")

    if scanned_barcode != step.expected_barcode:
        return (
            ScanResponse(
                valid=False,
                next_step=None,
                mismatch_reason=_mismatch_reason_for_step(step),
            ),
            None,
        )

    if step.expected_qty != Decimal("0") and actual_qty != step.expected_qty:
        return (
            ScanResponse(
                valid=False,
                next_step=None,
                mismatch_reason="wrong_qty",
            ),
            None,
        )

    now = datetime.now(timezone.utc)
    step.actual_qty = actual_qty
    step.completed_at = now

    await db.flush()

    remaining_result = await db.execute(
        select(TaskStep.id).where(
            TaskStep.task_id == task_id,
            TaskStep.completed_at.is_(None),
            TaskStep.sequence != step_seq,
        ).limit(1)
    )
    task_completed = remaining_result.first() is None

    if task_completed:
        task.status = "done"
        task.completed_at = now

    await db.commit()

    next_step: StepInfo | None = None
    if not task_completed:
        next_result = await db.execute(
            select(TaskStep)
            .where(
                TaskStep.task_id == task_id,
                TaskStep.sequence > step_seq,
                TaskStep.completed_at.is_(None),
            )
            .order_by(TaskStep.sequence.asc())
            .limit(1)
        )
        ns = next_result.scalar_one_or_none()
        if ns:
            next_step = StepInfo(
                sequence=ns.sequence,
                action=ns.action,
                expected_qty=ns.expected_qty,
            )

    response = ScanResponse(
        valid=True,
        next_step=next_step,
        mismatch_reason=None,
    )
    return response, _completion_event(task) if task_completed else None


async def _get_task_or_404(
    db: AsyncSession,
    task_id: int,
    *,
    for_update: bool = False,
) -> Task:
    stmt = select(Task).where(Task.id == task_id)
    if for_update:
        stmt = stmt.with_for_update()
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if task is None:
        raise NotFoundError(f"Task {task_id} not found")
    return task


def _check_owner(task: Task, user_id: int) -> None:
    if task.assignee_id != user_id:
        raise PermissionDeniedError("This task belongs to another worker")


def _check_warehouse(task: Task, warehouse_id: int | None) -> None:
    if warehouse_id is None or task.warehouse_id != warehouse_id:
        raise PermissionDeniedError("This task belongs to another warehouse")


def _completion_event(task: Task) -> TaskCompletionEvent:
    if task.completed_at is None:
        raise DomainValidationError("Completed task has no completed_at timestamp")
    return TaskCompletionEvent(
        task_id=task.id,
        assignee_id=task.assignee_id,
        warehouse_id=task.warehouse_id,
        completed_at=task.completed_at,
    )


def _mismatch_reason_for_step(step: TaskStep) -> str:
    if step.action in LOCATION_ACTIONS or step.location_id is not None:
        return "wrong_location"
    return "wrong_item"
