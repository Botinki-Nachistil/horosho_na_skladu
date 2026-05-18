from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import TokenPayload, get_redis, require_role
from schemas.mobile import ScanRequest, ScanResponse, TaskSummary
from services import mobile_service
from services.mobile_service import TaskCompletionEvent

router = APIRouter(prefix="/mobile", tags=["mobile"])

WorkerUser = Annotated[TokenPayload, Depends(require_role("worker"))]
DB = Annotated[AsyncSession, Depends(get_db)]
RedisClient = Annotated[Redis, Depends(get_redis)]


@router.get("/my-tasks", response_model=list[TaskSummary])
async def my_tasks(user: WorkerUser, db: DB) -> list[TaskSummary]:
    tasks = await mobile_service.get_my_tasks(db, user.user_id)
    return [TaskSummary.model_validate(t) for t in tasks]


@router.post("/tasks/{task_id}/accept", response_model=TaskSummary)
async def accept_task(task_id: int, user: WorkerUser, db: DB) -> TaskSummary:
    task = await mobile_service.accept_task(
        db, task_id, user.user_id, user.warehouse_id
    )
    return TaskSummary.model_validate(task)


@router.post("/tasks/{task_id}/start", response_model=TaskSummary)
async def start_task(task_id: int, user: WorkerUser, db: DB) -> TaskSummary:
    task = await mobile_service.start_task(db, task_id, user.user_id)
    return TaskSummary.model_validate(task)


@router.post("/tasks/{task_id}/complete", response_model=TaskSummary)
async def complete_task(
    task_id: int,
    user: WorkerUser,
    db: DB,
    redis: RedisClient,
    bg: BackgroundTasks,
) -> TaskSummary:
    task, completion_event = await mobile_service.complete_task(
        db, task_id, user.user_id
    )
    if completion_event is not None:
        bg.add_task(_publish_task_completed, redis, completion_event)
    return TaskSummary.model_validate(task)


@router.post(
    "/tasks/{task_id}/steps/{step_seq}/verify-scan",
    response_model=ScanResponse,
)
async def verify_scan(
    task_id: int,
    step_seq: int,
    body: ScanRequest,
    user: WorkerUser,
    db: DB,
    redis: RedisClient,
    bg: BackgroundTasks,
) -> ScanResponse:
    result, completion_event = await mobile_service.verify_scan(
        db, task_id, step_seq, user.user_id, body.scanned_barcode, body.actual_qty
    )
    if completion_event is not None:
        bg.add_task(_publish_task_completed, redis, completion_event)
    return result


async def _publish_task_completed(
    redis: Redis,
    event: TaskCompletionEvent,
) -> None:
    payload = json.dumps({
        "event_type": "task.completed",
        "task_id": event.task_id,
        "assignee_id": event.assignee_id,
        "warehouse_id": event.warehouse_id,
        "completed_at": event.completed_at.isoformat(),
    })
    await redis.publish(f"task_updates:{event.warehouse_id}", payload)
