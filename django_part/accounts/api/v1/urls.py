from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.api.v1.views import (
    AuditLogViewSet,
    ChangePasswordView,
    LoginView,
    MeView,
    PinLoginView,
    RefreshView,
    UserViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("audit", AuditLogViewSet, basename="audit")

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("login/pin/", PinLoginView.as_view(), name="pin-login"),
    path("token/refresh/", RefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("me/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("", include(router.urls)),
]
