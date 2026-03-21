from __future__ import annotations

from django.contrib.auth.hashers import make_password

USER_PASSWORD = "ChangeMe123!"


def _location_count(zone_id: int) -> int:
    return 9 if zone_id in {5, 6} else 8


def build_seed_records() -> list[dict]:
    records: list[dict] = []

    warehouses = [
        {
            "model": "warehouse.warehouse",
            "pk": 1,
            "fields": {
                "name": "Склад А — Москва",
                "address": "г. Москва, ул. Складская, 1",
                "config": {"timezone": "Europe/Moscow"},
                "created_at": "2026-03-01T08:00:00+03:00",
            },
        },
        {
            "model": "warehouse.warehouse",
            "pk": 2,
            "fields": {
                "name": "Склад B — Санкт-Петербург",
                "address": "г. Санкт-Петербург, пр. Логистический, 7",
                "config": {"timezone": "Europe/Moscow"},
                "created_at": "2026-03-01T08:05:00+03:00",
            },
        },
    ]
    records.extend(warehouses)

    zones = [
        (1, 1, "A-Picking", "picking"),
        (2, 1, "A-Storage", "storage"),
        (3, 1, "A-Shipping", "shipping"),
        (4, 2, "B-Picking", "picking"),
        (5, 2, "B-Storage", "storage"),
        (6, 2, "B-Shipping", "shipping"),
    ]
    for pk, warehouse_id, name, zone_type in zones:
        records.append(
            {
                "model": "warehouse.zone",
                "pk": pk,
                "fields": {
                    "warehouse": warehouse_id,
                    "name": name,
                    "zone_type": zone_type,
                },
            }
        )

    location_pk = 1
    for zone_id, warehouse_id, name, zone_type in zones:
        for idx in range(1, _location_count(zone_id) + 1):
            records.append(
                {
                    "model": "warehouse.location",
                    "pk": location_pk,
                    "fields": {
                        "zone": zone_id,
                        "barcode": f"{name}-{idx:03d}",
                        "coords": {
                            "aisle": idx,
                            "rack": (idx % 4) + 1,
                            "level": (idx % 3) + 1,
                            "warehouse": warehouse_id,
                        },
                        "is_active": True,
                    },
                }
            )
            location_pk += 1

    for item_id in range(1, 21):
        records.append(
            {
                "model": "inventory.item",
                "pk": item_id,
                "fields": {
                    "sku": f"SKU-{item_id:03d}",
                    "name": f"Товар {item_id:03d}",
                    "barcode": f"46000000{item_id:04d}",
                    "unit": "pcs",
                    "weight": f"{1 + item_id / 10:.3f}",
                    "dimensions": {"l": 10 + item_id, "w": 5 + item_id, "h": 3 + item_id},
                    "is_active": True,
                },
            }
        )

    for inv_id in range(1, 21):
        records.append(
            {
                "model": "inventory.inventory",
                "pk": inv_id,
                "fields": {
                    "item": inv_id,
                    "location": inv_id,
                    "quantity": f"{100 + inv_id * 5:.3f}",
                    "reserved_qty": f"{inv_id % 7:.3f}",
                    "updated_at": "2026-03-02T09:00:00+03:00",
                },
            }
        )

    records.extend(
        [
            {
                "model": "operations.wave",
                "pk": 1,
                "fields": {
                    "warehouse": 1,
                    "code": "WAVE-001",
                    "status": "active",
                    "scheduled_at": "2026-03-03T09:00:00+03:00",
                    "created_at": "2026-03-03T08:50:00+03:00",
                },
            },
            {
                "model": "operations.wave",
                "pk": 2,
                "fields": {
                    "warehouse": 2,
                    "code": "WAVE-002",
                    "status": "planned",
                    "scheduled_at": "2026-03-03T11:00:00+03:00",
                    "created_at": "2026-03-03T10:50:00+03:00",
                },
            },
        ]
    )

    users = [
        (
            1,
            "admin",
            "admin@example.com",
            True,
            True,
            None,
            "A",
            "1111",
        ),
        (
            2,
            "manager",
            "manager@example.com",
            True,
            False,
            1,
            "A",
            "2222",
        ),
        (
            3,
            "supervisor",
            "supervisor@example.com",
            True,
            False,
            1,
            "B",
            "3333",
        ),
        (
            4,
            "worker",
            "worker@example.com",
            False,
            False,
            2,
            "B",
            "4444",
        ),
    ]
    for pk, role, email, is_staff, is_superuser, warehouse_id, shift, pin in users:
        records.append(
            {
                "model": "accounts.user",
                "pk": pk,
                "fields": {
                    "password": make_password(USER_PASSWORD, salt=f"seed-{pk}"),
                    "last_login": None,
                    "is_superuser": is_superuser,
                    "username": role,
                    "first_name": role.capitalize(),
                    "last_name": "Seed",
                    "email": email,
                    "is_staff": is_staff,
                    "is_active": True,
                    "date_joined": "2026-03-01T07:30:00+03:00",
                    "role": role,
                    "warehouse": warehouse_id,
                    "pin_code": pin,
                    "shift": shift,
                    "groups": [],
                    "user_permissions": [],
                },
            }
        )

    permission_pk = 1
    for role, resource, action in [
        ("admin", "order", "delete"),
        ("admin", "user", "write"),
        ("manager", "order", "write"),
        ("manager", "kpi", "read"),
        ("supervisor", "task", "write"),
        ("supervisor", "order", "read"),
        ("worker", "task", "read"),
        ("worker", "inventory", "read"),
    ]:
        records.append(
            {
                "model": "accounts.rbacpermission",
                "pk": permission_pk,
                "fields": {
                    "role": role,
                    "resource": resource,
                    "action": action,
                },
            }
        )
        permission_pk += 1

    orders = [
        (1, 1, None, "pending", 1, "ООО Альфа", "2026-03-03T18:00:00+03:00"),
        (2, 1, None, "processing", 3, "ООО Бета", "2026-03-03T19:00:00+03:00"),
        (3, 1, 1, "picking", 2, "ООО Гамма", "2026-03-03T17:00:00+03:00"),
        (4, 2, 2, "packed", 4, "ООО Дельта", "2026-03-04T09:00:00+03:00"),
        (5, 2, 2, "done", 5, "ООО Эпсилон", "2026-03-02T12:00:00+03:00"),
    ]
    for pk, warehouse_id, wave_id, status, priority, customer, deadline in orders:
        records.append(
            {
                "model": "orders.order",
                "pk": pk,
                "fields": {
                    "warehouse": warehouse_id,
                    "wave": wave_id,
                    "status": status,
                    "priority": priority,
                    "customer": customer,
                    "deadline": deadline,
                    "created_at": "2026-03-03T08:00:00+03:00",
                    "updated_at": "2026-03-03T08:30:00+03:00",
                },
            }
        )

    line_pk = 1
    line_specs = [
        (1, 1, 1, "4.000", "0.000"),
        (1, 2, 2, "3.000", "0.000"),
        (2, 3, 3, "5.000", "1.000"),
        (2, 4, 4, "6.000", "1.000"),
        (3, 5, 5, "2.000", "2.000"),
        (3, 6, 6, "1.000", "1.000"),
        (4, 7, 25, "7.000", "7.000"),
        (4, 8, 26, "2.000", "2.000"),
        (5, 9, 27, "9.000", "9.000"),
        (5, 10, 28, "4.000", "4.000"),
    ]
    for order_id, item_id, location_id, qty_req, qty_picked in line_specs:
        records.append(
            {
                "model": "orders.orderline",
                "pk": line_pk,
                "fields": {
                    "order": order_id,
                    "item": item_id,
                    "location": location_id,
                    "qty_req": qty_req,
                    "qty_picked": qty_picked,
                },
            }
        )
        line_pk += 1

    tasks = [
        (1, 1, 1, 4, "picking", "assigned", 1, 17, "4.000"),
        (2, 1, 1, 4, "picking", "in_progress", 2, 18, "3.000"),
        (3, 1, 1, 4, "move", "pending", 5, 19, "2.000"),
        (4, 2, 2, 4, "shipping", "assigned", 25, 42, "7.000"),
        (5, 2, 2, 4, "putaway", "done", 33, 34, "9.000"),
    ]
    for pk, warehouse_id, wave_id, assignee_id, task_type, status, source_id, target_id, qty in tasks:
        records.append(
            {
                "model": "operations.task",
                "pk": pk,
                "fields": {
                    "warehouse": warehouse_id,
                    "wave": wave_id,
                    "assignee": assignee_id,
                    "task_type": task_type,
                    "status": status,
                    "source_location": source_id,
                    "target_location": target_id,
                    "quantity": qty,
                    "priority": pk,
                    "created_at": "2026-03-03T09:00:00+03:00",
                    "assigned_at": "2026-03-03T09:05:00+03:00",
                    "completed_at": None if status != "done" else "2026-03-03T10:00:00+03:00",
                },
            }
        )

    step_pk = 1
    for task_id, source_id, target_id in [(1, 1, 17), (2, 2, 18), (3, 5, 19), (4, 25, 42), (5, 33, 34)]:
        for sequence, location_id, action in [
            (1, source_id, "scan-source"),
            (2, target_id, "confirm-target"),
        ]:
            records.append(
                {
                    "model": "operations.taskstep",
                    "pk": step_pk,
                    "fields": {
                        "task": task_id,
                        "sequence": sequence,
                        "action": action,
                        "location": location_id,
                        "expected_barcode": f"LOC-{location_id:03d}",
                        "expected_qty": "1.000",
                        "actual_qty": "1.000" if task_id == 5 else "0.000",
                        "completed_at": None,
                        "metadata": {"task_id": task_id},
                    },
                }
            )
            step_pk += 1

    records.extend(
        [
            {
                "model": "operations.route",
                "pk": 1,
                "fields": {
                    "wave": 1,
                    "task": 1,
                    "method": "nearest_neighbor",
                    "points": ["A-Picking-001", "A-Shipping-001"],
                    "distance_m": "124.50",
                    "eta_seconds": 320,
                    "diagnostics": {"iterations": 2},
                    "created_at": "2026-03-03T09:01:00+03:00",
                },
            },
            {
                "model": "operations.route",
                "pk": 2,
                "fields": {
                    "wave": 2,
                    "task": 4,
                    "method": "s_shape",
                    "points": ["B-Picking-001", "B-Shipping-001"],
                    "distance_m": "210.00",
                    "eta_seconds": 510,
                    "diagnostics": {"iterations": 1},
                    "created_at": "2026-03-03T11:01:00+03:00",
                },
            },
        ]
    )

    records.extend(
        [
            {
                "model": "operations.integrationconfig",
                "pk": 1,
                "fields": {
                    "warehouse": 1,
                    "name": "1C Sync A",
                    "channel_type": "rest",
                    "direction": "pull",
                    "endpoint": "https://example.local/api/1c/a",
                    "schedule": "*/15 * * * *",
                    "settings": {"timeout": 30},
                    "is_active": True,
                },
            },
            {
                "model": "operations.integrationconfig",
                "pk": 2,
                "fields": {
                    "warehouse": 2,
                    "name": "SAP Push B",
                    "channel_type": "csv",
                    "direction": "push",
                    "endpoint": "/exports/b.csv",
                    "schedule": "0 * * * *",
                    "settings": {"separator": ";"},
                    "is_active": True,
                },
            },
            {
                "model": "operations.integrationlog",
                "pk": 1,
                "fields": {
                    "config": 1,
                    "status": "success",
                    "attempt": 1,
                    "payload": {"batch": "sync-a-001"},
                    "response": {"status": 200},
                    "error_message": "",
                    "created_at": "2026-03-03T09:15:00+03:00",
                },
            },
            {
                "model": "operations.integrationlog",
                "pk": 2,
                "fields": {
                    "config": 2,
                    "status": "error",
                    "attempt": 2,
                    "payload": {"batch": "push-b-001"},
                    "response": {"status": 500},
                    "error_message": "Temporary upstream failure",
                    "created_at": "2026-03-03T10:15:00+03:00",
                },
            },
        ]
    )

    records.extend(
        [
            {
                "model": "operations.kpisnapshot",
                "pk": 1,
                "fields": {
                    "warehouse": 1,
                    "shift": "A",
                    "period_start": "2026-03-03T08:00:00+03:00",
                    "period_end": "2026-03-03T16:00:00+03:00",
                    "throughput_lines": 120,
                    "throughput_orders": 45,
                    "order_accuracy": "98.50",
                    "dock_to_stock_p95": "42.30",
                    "sla_on_time": 39,
                    "sla_overdue": 6,
                    "active_minutes": 360,
                    "idle_minutes": 45,
                    "created_at": "2026-03-03T16:10:00+03:00",
                },
            },
            {
                "model": "operations.kpisnapshot",
                "pk": 2,
                "fields": {
                    "warehouse": 2,
                    "shift": "B",
                    "period_start": "2026-03-03T08:00:00+03:00",
                    "period_end": "2026-03-03T16:00:00+03:00",
                    "throughput_lines": 98,
                    "throughput_orders": 34,
                    "order_accuracy": "97.10",
                    "dock_to_stock_p95": "55.00",
                    "sla_on_time": 30,
                    "sla_overdue": 4,
                    "active_minutes": 330,
                    "idle_minutes": 60,
                    "created_at": "2026-03-03T16:10:00+03:00",
                },
            },
        ]
    )

    for pk, warehouse_id, user_id, task_id, event_type in [
        (1, 1, 2, 1, "task_assigned"),
        (2, 1, 3, 2, "task_started"),
        (3, 1, 4, 3, "inventory_adjusted"),
        (4, 2, 4, 4, "task_reprioritized"),
        (5, 2, 4, 5, "task_completed"),
    ]:
        records.append(
            {
                "model": "operations.event",
                "pk": pk,
                "fields": {
                    "warehouse": warehouse_id,
                    "user": user_id,
                    "task": task_id,
                    "event_type": event_type,
                    "payload": {"task_id": task_id, "source": "seed"},
                    "created_at": "2026-03-03T10:00:00+03:00",
                },
            }
        )

    for pk, user_id, action, entity_type, entity_id in [
        (1, 2, "create", "order", 1),
        (2, 3, "assign", "task", 1),
        (3, 4, "adjust", "inventory", 1),
    ]:
        records.append(
            {
                "model": "accounts.auditlog",
                "pk": pk,
                "fields": {
                    "user": user_id,
                    "action": action,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "details": {"seed": True},
                    "ip_address": "127.0.0.1",
                    "created_at": "2026-03-03T10:30:00+03:00",
                },
            }
        )

    return records
