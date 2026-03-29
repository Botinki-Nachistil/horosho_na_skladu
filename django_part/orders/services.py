from __future__ import annotations

from django.db.models import F

from orders.models import Order
from shared.exceptions import InvalidStateError, ValidationError


def transition_order(order: Order, target: str | None) -> Order:
    if not target:
        raise ValidationError("status is required.")
    if not order.can_transition_to(target):
        raise InvalidStateError(f"Cannot transition from {order.status} to {target}.")
    if target == Order.Status.PACKED:
        if order.lines.filter(qty_picked__gt=F("qty_req")).exists():
            raise InvalidStateError("Cannot pack order: some lines have qty_picked exceeding qty_req.")
    order.status = target
    order.save(update_fields=["status", "updated_at"])
    return order
