from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import InvalidStateError, NotFoundError, PermissionDeniedError
from models.sa_models import Location, Task, TaskStep
from schemas.mobile import ScanResponse, StepInfo


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


async def accept_task(db: AsyncSession, task_id: int, user_id: int) -> Task:
    task = await _get_task_or_404(db, task_id)
    if task.status != "pending":
        raise InvalidStateError(f"Task is '{task.status}', expected 'pending'")
    task.assignee_id = user_id
    task.status = "assigned"
    task.assigned_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(task)
    return task


async def start_task(db: AsyncSession, task_id: int, user_id: int) -> Task:
    task = await _get_task_or_404(db, task_id)
    _check_owner(task, user_id)
    if task.status != "assigned":
        raise InvalidStateError(f"Task is '{task.status}', expected 'assigned'")
    task.status = "in_progress"
    await db.commit()
    await db.refresh(task)
    return task


async def complete_task(db: AsyncSession, task_id: int, user_id: int) -> Task:
    task = await _get_task_or_404(db, task_id)
    _check_owner(task, user_id)
    if task.status == "done":
        return task
    if task.status != "in_progress":
        raise InvalidStateError(f"Task is '{task.status}', expected 'in_progress'")
    task.status = "done"
    task.completed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(task)
    return task


async def verify_scan(
    db: AsyncSession,
    task_id: int,
    step_seq: int,
    user_id: int,
    scanned_barcode: str,
    scanned_qty: Decimal,
) -> ScanResponse:
    task = await _get_task_or_404(db, task_id)
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

    if step.location_id is not None:
        loc_result = await db.execute(
            select(Location).where(Location.id == step.location_id)
        )
        location = loc_result.scalar_one_or_none()
        expected_barcode = location.barcode if location else step.expected_barcode
        mismatch_type = "wrong_location"
    else:
        expected_barcode = step.expected_barcode
        mismatch_type = "wrong_item"

    if scanned_barcode != expected_barcode:
        return ScanResponse(
            ok=False,
            step_completed=False,
            mismatch_reason=mismatch_type,
            next_step=None,
            task_completed=False,
        )

    if step.expected_qty != Decimal("0") and scanned_qty != step.expected_qty:
        return ScanResponse(
            ok=False,
            step_completed=False,
            mismatch_reason="wrong_qty",
            next_step=None,
            task_completed=False,
        )

    now = datetime.now(timezone.utc)
    step.actual_qty = scanned_qty
    step.completed_at = now

    remaining_result = await db.execute(
        select(TaskStep).where(
            TaskStep.task_id == task_id,
            TaskStep.completed_at.is_(None),
            TaskStep.sequence != step_seq,
        )
    )
    task_completed = remaining_result.scalar_one_or_none() is None

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

    return ScanResponse(
        ok=True,
        step_completed=True,
        next_step=next_step,
        task_completed=task_completed,
    )


async def _get_task_or_404(db: AsyncSession, task_id: int) -> Task:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise NotFoundError(f"Task {task_id} not found")
    return task


def _check_owner(task: Task, user_id: int) -> None:
    if task.assignee_id != user_id:
        raise PermissionDeniedError("This task belongs to another worker")
