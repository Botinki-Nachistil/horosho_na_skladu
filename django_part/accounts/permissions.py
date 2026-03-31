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
