from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import AuditLog, User
from accounts.permissions import IsAdmin, IsSupervisor
from accounts.serializers import (
    AuditLogSerializer,
    ChangePasswordSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from accounts.services import (
    change_password,
    create_user,
    login_user,
    logout_user,
    pin_login,
    refresh_token,
    set_user_active,
    update_user,
)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response(login_user(
            request.data.get("username"),
            request.data.get("password"),
            request,
        ))


class PinLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response(pin_login(
            request.data.get("pin_code", ""),
            request.data.get("warehouse_id"),
        ))


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response(refresh_token(request.data.get("refresh")))


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logout_user(request.data.get("refresh"))
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            "id": u.id,
            "username": u.username,
            "full_name": u.get_full_name(),
            "role": u.role,
            "warehouse_id": u.warehouse_id,
            "shift": u.shift,
        })


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        change_password(
            user=request.user,
            old_password=serializer.validated_data["old_password"],
            new_password=serializer.validated_data["new_password"],
        )
        return Response({"message": "Password changed successfully."})


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSupervisor]
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ("update", "partial_update"):
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        qs = User.objects.select_related("warehouse").order_by("id")
        if user.role == User.Role.ADMIN:
            return qs
        if user.role == User.Role.MANAGER:
            return qs.filter(warehouse_id=user.warehouse_id).exclude(role=User.Role.ADMIN)
        if user.role == User.Role.SUPERVISOR:
            return qs.filter(warehouse_id=user.warehouse_id, role=User.Role.WORKER)
        return qs.none()

    def create(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        user = create_user(
            creator=request.user,
            username=d["username"],
            role=d["role"],
            warehouse_id=d["warehouse_id"],
            password=d["password"],
            first_name=d.get("first_name", ""),
            last_name=d.get("last_name", ""),
            pin=d.get("pin") or None,
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = UserUpdateSerializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = update_user(self.get_object(), **serializer.validated_data)
        return Response(UserSerializer(user).data)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="deactivate", permission_classes=[IsAdmin])
    def deactivate(self, request, pk=None):
        set_user_active(self.get_object(), False)
        return Response({"message": "User deactivated."})

    @action(detail=True, methods=["post"], url_path="activate", permission_classes=[IsAdmin])
    def activate(self, request, pk=None):
        set_user_active(self.get_object(), True)
        return Response({"message": "User activated."})


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = AuditLog.objects.select_related("user").order_by("-created_at")
        entity_type = self.request.query_params.get("entity_type")
        user_id = self.request.query_params.get("user_id")
        if entity_type:
            qs = qs.filter(entity_type=entity_type)
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs
