from __future__ import annotations

from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import AuditLog, User
from accounts.serializers import AuditLogSerializer, UserCreateSerializer, UserSerializer


def _make_token_response(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    refresh["role"] = user.role
    refresh["warehouse_id"] = user.warehouse_id
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user_id": user.id,
        "role": user.role,
        "warehouse_id": user.warehouse_id,
    }


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": {"code": "MISSING_FIELDS", "message": "username and password are required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)

        if not user:
            return Response(
                {"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid username or password."}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"error": {"code": "ACCOUNT_DISABLED", "message": "Account is disabled."}},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(_make_token_response(user))


class PinLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        pin = request.data.get("pin_code", "")
        warehouse_id = request.data.get("warehouse_id")

        if not pin or not pin.isdigit() or not (4 <= len(pin) <= 6):
            return Response(
                {"error": {"code": "INVALID_PIN", "message": "PIN must be 4-6 digits."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = User.objects.filter(role=User.Role.WORKER, is_active=True)
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)

        matched = next((u for u in qs if u.check_pin(pin)), None)

        if not matched:
            return Response(
                {"error": {"code": "INVALID_PIN", "message": "Invalid PIN."}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(_make_token_response(matched))


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("refresh")

        if not token:
            return Response(
                {"error": {"code": "MISSING_FIELD", "message": "refresh token is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(token)
            return Response({"access": str(refresh.access_token)})
        except Exception:
            return Response(
                {"error": {"code": "INVALID_TOKEN", "message": "Token is invalid or expired."}},
                status=status.HTTP_401_UNAUTHORIZED,
            )


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
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response({"message": "User deactivated."})

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save(update_fields=["is_active"])
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