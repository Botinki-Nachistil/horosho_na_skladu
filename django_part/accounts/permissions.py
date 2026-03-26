from __future__ import annotations

from rest_framework.permissions import BasePermission


class RolePermission(BasePermission):
    required_roles: list[str] = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in self.required_roles


class IsAdmin(RolePermission):
    required_roles = ["admin"]


class IsManager(RolePermission):
    required_roles = ["admin", "manager"]


class IsSupervisor(RolePermission):
    required_roles = ["admin", "manager", "supervisor"]


class IsWorker(RolePermission):
    required_roles = ["admin", "manager", "supervisor", "worker"]


class WarehouseScopedPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role in ("admin",):
            return True

        warehouse_id = getattr(obj, "warehouse_id", None)
        if warehouse_id is None:
            warehouse = getattr(obj, "warehouse", None)
            warehouse_id = getattr(warehouse, "id", None)

        return warehouse_id == user.warehouse_id