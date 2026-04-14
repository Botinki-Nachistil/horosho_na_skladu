from __future__ import annotations

import re

from rest_framework import serializers

from accounts.models import AuditLog, RBACPermission, RefreshToken, User


class UserSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.SerializerMethodField()
    accessible_warehouses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "warehouse",
            "warehouse_name",
            "accessible_warehouses",
            "shift",
            "is_active",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "warehouse",
            "shift",
            "is_active",
            "date_joined",
        ]

    def get_warehouse_name(self, obj: User) -> str | None:
        return obj.warehouse.name if obj.warehouse_id else None

    def get_accessible_warehouses(self, obj: User) -> list[int]:
        return obj.accessible_warehouse_ids


class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    role = serializers.ChoiceField(choices=User.Role.choices)
    warehouse_id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=150, required=False, default="")
    last_name = serializers.CharField(max_length=150, required=False, default="")
    pin = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={"input_type": "password"},
    )

    def validate_pin(self, value: str) -> str:
        if value and not re.match(r"^\d{4,6}$", value):
            raise serializers.ValidationError("PIN must contain 4-6 digits.")
        return value


class UserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)
    shift = serializers.CharField(max_length=20, required=False, allow_blank=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    new_password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})


class RefreshTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefreshToken
        fields = ["id", "jti", "user", "exp", "revoked", "created_at"]
        read_only_fields = ["id", "jti", "created_at"]


class RBACPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RBACPermission
        fields = ["id", "role", "resource", "action"]
        read_only_fields = ["id"]


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ["id", "user", "action", "entity_type", "entity_id", "details", "ip_address", "created_at"]
        read_only_fields = ["id", "user", "action", "entity_type", "entity_id", "details", "ip_address", "created_at"]
