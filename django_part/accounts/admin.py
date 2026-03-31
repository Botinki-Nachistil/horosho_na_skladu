from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import AuditLog, RBACPermission, RefreshToken, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "role", "warehouse", "is_active")
    list_filter = ("role", "warehouse", "is_active")
    search_fields = ("username", "email")
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Warehouse Access",
            {"fields": ("role", "warehouse", "warehouses", "shift")},
        ),
    )
    filter_horizontal = ("warehouses",)


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ("jti", "user", "exp", "revoked", "created_at")
    list_filter = ("revoked",)
    search_fields = ("user__username",)


@admin.register(RBACPermission)
class RBACPermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "resource", "action")
    list_filter = ("role", "resource", "action")
    search_fields = ("resource", "action")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "entity_type", "entity_id", "user", "created_at")
    list_filter = ("action", "entity_type", "created_at")
    search_fields = ("entity_type", "user__username")
    readonly_fields = ("created_at",)
