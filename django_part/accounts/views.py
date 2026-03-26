from __future__ import annotations

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.exceptions import TokenValidationError, ValidationError
from accounts.models import AuditLog, User
from accounts.serializers import AuditLogSerializer, UserCreateSerializer, UserSerializer
from accounts.services import login_user, pin_login, refresh_token, set_user_active


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


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.select_related("warehouse").order_by("id")

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        set_user_active(self.get_object(), False)
        return Response({"message": "User deactivated."})

    @action(detail=True, methods=["post"], url_path="activate")
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