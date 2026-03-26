from __future__ import annotations

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import Order
from orders.serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "priority", "deadline"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Order.objects.select_related("warehouse", "wave").prefetch_related(
            "lines__item",
        )
        status_param = self.request.query_params.get("status")
        priority = self.request.query_params.get("priority")
        warehouse_id = self.request.query_params.get("warehouse")
        if status_param:
            qs = qs.filter(status=status_param)
        if priority:
            qs = qs.filter(priority=priority)
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        return qs

    @action(detail=True, methods=["post"], url_path="transition")
    def transition(self, request, pk=None):
        order = self.get_object()
        target = request.data.get("status")

        if not target:
            return Response(
                {"error": {"code": "MISSING_FIELD", "message": "status is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not order.can_transition_to(target):
            return Response(
                {"error": {
                    "code": "INVALID_TRANSITION",
                    "message": f"Cannot transition from {order.status} to {target}.",
                }},
                status=status.HTTP_409_CONFLICT,
            )

        order.status = target
        order.save(update_fields=["status", "updated_at"])
        return Response(OrderSerializer(order).data)