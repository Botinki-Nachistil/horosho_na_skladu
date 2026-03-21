from django.test import TestCase

from inventory.models import Item
from orders.models import Order, OrderLine
from warehouse.models import Location, Warehouse, Zone


class TestOrderCascade(TestCase):
    def test_delete_order_removes_lines(self):
        warehouse = Warehouse.objects.create(name="Test WH")
        zone = Zone.objects.create(
            warehouse=warehouse,
            name="Picking",
            zone_type=Zone.ZoneType.PICKING,
        )
        location = Location.objects.create(barcode="A-01-01", zone=zone)
        item = Item.objects.create(sku="SKU-001", name="Test Item", barcode="1000001")
        order = Order.objects.create(warehouse=warehouse, priority=1)
        OrderLine.objects.create(order=order, item=item, location=location, qty_req=1)

        order.delete()

        self.assertEqual(OrderLine.objects.count(), 0)
