from django.http import JsonResponse
from django.urls import path


def root(request):
    return JsonResponse({"status": "ok"})


def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("", root),
    path("health", health),
]

