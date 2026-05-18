from __future__ import annotations

from decimal import Decimal
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from database import get_db
from dependencies import TokenPayload, get_current_user, get_redis
from main import app

WORKER = TokenPayload(user_id=7, role="worker", warehouse_id=1)


def _mock_redis() -> AsyncMock:
    r = AsyncMock()
    r.publish = AsyncMock()
    return r


def _override_db():
    mock_session = AsyncMock()

    async def _db():
        yield mock_session

    app.dependency_overrides[get_db] = _db
    return mock_session


def _override_auth():
    async def _user():
        return WORKER
    app.dependency_overrides[get_current_user] = _user


def _override_redis():
    redis = _mock_redis()
    app.dependency_overrides[get_redis] = lambda: redis
    return redis


@pytest_asyncio.fixture
async def client():
    _override_auth()
    _override_db()
    _override_redis()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_my_tasks(client: AsyncClient):
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.task_type = "picking"
    mock_task.status = "assigned"
    mock_task.priority = 5
    mock_task.source_location_id = None
    mock_task.target_location_id = None
    mock_task.quantity = Decimal("2.000")

    with patch(
        "routers.mobile.mobile_service.get_my_tasks", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = [mock_task]
        response = await client.get("/api/v1/mobile/my-tasks")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 1
    assert data[0]["status"] == "assigned"


@pytest.mark.asyncio
async def test_accept_task(client: AsyncClient):
    mock_task = MagicMock()
    mock_task.id = 5
    mock_task.task_type = "picking"
    mock_task.status = "assigned"
    mock_task.priority = 3
    mock_task.source_location_id = 1
    mock_task.target_location_id = 2
    mock_task.quantity = Decimal("1.000")

    with patch(
        "routers.mobile.mobile_service.accept_task", new_callable=AsyncMock
    ) as mock_accept:
        mock_accept.return_value = mock_task
        response = await client.post("/api/v1/mobile/tasks/5/accept")

    assert response.status_code == 200
    assert response.json()["status"] == "assigned"
    mock_accept.assert_awaited_once_with(ANY, 5, WORKER.user_id)


@pytest.mark.asyncio
async def test_accept_wrong_state(client: AsyncClient):
    from exceptions import InvalidStateError

    with patch(
        "routers.mobile.mobile_service.accept_task", new_callable=AsyncMock
    ) as mock_accept:
        mock_accept.side_effect = InvalidStateError("Task is 'assigned', expected 'pending'")
        response = await client.post("/api/v1/mobile/tasks/5/accept")

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_start_task(client: AsyncClient):
    mock_task = MagicMock()
    mock_task.id = 5
    mock_task.task_type = "picking"
    mock_task.status = "in_progress"
    mock_task.priority = 3
    mock_task.source_location_id = 1
    mock_task.target_location_id = 2
    mock_task.quantity = Decimal("1.000")

    with patch(
        "routers.mobile.mobile_service.start_task", new_callable=AsyncMock
    ) as mock_start:
        mock_start.return_value = mock_task
        response = await client.post("/api/v1/mobile/tasks/5/start")

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_complete_task(client: AsyncClient):
    from datetime import datetime, timezone

    mock_task = MagicMock()
    mock_task.id = 5
    mock_task.task_type = "picking"
    mock_task.status = "done"
    mock_task.priority = 3
    mock_task.source_location_id = 1
    mock_task.target_location_id = 2
    mock_task.quantity = Decimal("1.000")
    mock_task.completed_at = datetime.now(timezone.utc)

    with patch(
        "routers.mobile.mobile_service.complete_task", new_callable=AsyncMock
    ) as mock_complete:
        mock_complete.return_value = mock_task
        response = await client.post("/api/v1/mobile/tasks/5/complete")

    assert response.status_code == 200
    assert response.json()["status"] == "done"


@pytest.mark.asyncio
async def test_verify_scan_ok(client: AsyncClient):
    from schemas.mobile import ScanResponse, StepInfo

    scan_result = ScanResponse(
        ok=True,
        step_completed=True,
        next_step=StepInfo(sequence=2, action="confirm-target", expected_qty=Decimal("1.000")),
        task_completed=False,
    )

    with patch(
        "routers.mobile.mobile_service.verify_scan", new_callable=AsyncMock
    ) as mock_scan:
        mock_scan.return_value = scan_result
        response = await client.post(
            "/api/v1/mobile/tasks/5/steps/1/verify-scan",
            json={"scanned_barcode": "LOC-001", "scanned_qty": "1.000"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["step_completed"] is True
    assert data["next_step"]["sequence"] == 2


@pytest.mark.asyncio
async def test_verify_scan_mismatch(client: AsyncClient):
    from schemas.mobile import ScanResponse

    scan_result = ScanResponse(
        ok=False,
        step_completed=False,
        mismatch_reason="wrong_location",
        next_step=None,
        task_completed=False,
    )

    with patch(
        "routers.mobile.mobile_service.verify_scan", new_callable=AsyncMock
    ) as mock_scan:
        mock_scan.return_value = scan_result
        response = await client.post(
            "/api/v1/mobile/tasks/5/steps/1/verify-scan",
            json={"scanned_barcode": "WRONG-BARCODE", "scanned_qty": "1.000"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert data["mismatch_reason"] == "wrong_location"
