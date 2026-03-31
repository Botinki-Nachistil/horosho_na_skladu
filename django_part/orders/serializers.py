from __future__ import annotations

from rest_framework import serializers

from orders.models import Order, OrderLine


class OrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLine
        fields = ["id", "order", "item", "location", "qty_req", "qty_picked"]
        read_only_fields = ["id", "qty_picked"]


class OrderSerializer(serializers.ModelSerializer):
    lines = OrderLineSerializer(many=True, read_only=True)
    available_transitions = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "warehouse",
            "wave",
            "status",
            "priority",
            "customer",
            "deadline",
            "created_at",
            "updated_at",
            "lines",
            "available_transitions",
        ]
        read_only_fields = ["id", "status", "warehouse", "wave", "created_at", "updated_at", "lines", "available_transitions"]

    def get_available_transitions(self, obj: Order) -> list[str]:
        return [s for s in Order.Status.values if obj.can_transition_to(s)]


class OrderTransitionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.Status.choices)
