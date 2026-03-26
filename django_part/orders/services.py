from __future__ import annotations

from orders.models import Order
from shared.exceptions import InvalidStateError, ValidationError


def transition_order(order: Order, target: str | None) -> Order:
    if not target:
        raise ValidationError("status is required.")
    if not order.can_transition_to(target):
        raise InvalidStateError(f"Cannot transition from {order.status} to {target}.")
    order.status = target
    order.save(update_fields=["status", "updated_at"])
    return order