from __future__ import annotations

import re

from rest_framework import serializers

from accounts.models import AuditLog, RBACPermission, RefreshToken, User


class UserSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={"input_type": "password"},
    )
    warehouse = serializers.PrimaryKeyRelatedField(read_only=True)

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
            "shift",
            "is_active",
            "date_joined",
            "pin",
        ]
        read_only_fields = ["id", "date_joined"]
        extra_kwargs = {"password": {"write_only": True, "required": False}}

    def validate_pin(self, value: str) -> str:
        if value and not re.match(r"^\d{4,6}$", value):
            raise serializers.ValidationError("PIN must contain 4-6 digits.")
        return value

    def update(self, instance: User, validated_data: dict) -> User:
        pin = validated_data.pop("pin", None)
        instance = super().update(instance, validated_data)
        if pin:
            instance.set_pin(pin)
            instance.save(update_fields=["pin_code"])
        return instance


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
