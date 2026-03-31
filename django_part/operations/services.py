from __future__ import annotations

from django.utils import timezone

from accounts.models import User
from operations.models import Task, Wave
from shared.exceptions import InvalidStateError, NotFoundError, ValidationError


def activate_wave(wave: Wave) -> Wave:
    if wave.status != Wave.Status.PLANNED:
        raise InvalidStateError(f"Cannot activate wave with status {wave.status}.")
    if not wave.tasks.exists():
        raise InvalidStateError("Cannot activate a wave with no tasks.")
    wave.status = Wave.Status.ACTIVE
    wave.save(update_fields=["status"])
    return wave


def assign_task(task: Task, user_id: int) -> Task:
    if task.status not in (Task.Status.PENDING, Task.Status.ASSIGNED):
        raise InvalidStateError(f"Cannot assign task with status {task.status}.")
    try:
        worker = User.objects.get(pk=user_id, role=User.Role.WORKER, is_active=True)
    except User.DoesNotExist:
        raise NotFoundError("Active worker not found.")
    if task.warehouse_id not in worker.accessible_warehouse_ids:
        raise ValidationError("Worker does not have access to the task's warehouse.")
    task.assignee = worker
    task.status = Task.Status.ASSIGNED
    task.assigned_at = timezone.now()
    task.save(update_fields=["assignee", "status", "assigned_at"])
    return task


def start_task(task: Task) -> Task:
    if task.status != Task.Status.ASSIGNED:
        raise InvalidStateError(f"Cannot start task with status {task.status}.")
    task.status = Task.Status.IN_PROGRESS
    task.save(update_fields=["status"])
    return task


def complete_task(task: Task) -> Task:
    if task.status != Task.Status.IN_PROGRESS:
        raise InvalidStateError(f"Cannot complete task with status {task.status}.")
    task.status = Task.Status.DONE
    task.completed_at = timezone.now()
    task.save(update_fields=["status", "completed_at"])
    _try_complete_wave(task)
    return task


def _try_complete_wave(task: Task) -> None:
    if not task.wave_id:
        return
    wave = task.wave
    if wave.status != Wave.Status.ACTIVE:
        return
    has_incomplete = wave.tasks.exclude(
        status__in=(Task.Status.DONE, Task.Status.CANCELLED)
    ).exists()
    if not has_incomplete:
        wave.status = Wave.Status.DONE
        wave.save(update_fields=["status"])


def cancel_task(task: Task) -> Task:
    if task.status == Task.Status.DONE:
        raise InvalidStateError("Cannot cancel completed task.")
    task.status = Task.Status.CANCELLED
    task.save(update_fields=["status"])
    _try_complete_wave(task)
    return task
