from django.test import TestCase

from inventory.models import Inventory, Item
from warehouse.models import Location, Warehouse, Zone


class TestInventory(TestCase):
    def setUp(self):
        warehouse = Warehouse.objects.create(name="Test WH")
        zone = Zone.objects.create(
            warehouse=warehouse,
            name="Picking",
            zone_type=Zone.ZoneType.PICKING,
        )
        self.location = Location.objects.create(barcode="A-01-01", zone=zone)
        self.item = Item.objects.create(sku="SKU-001", name="Test Item", barcode="1000001")

    def test_available_qty_computed(self):
        inventory = Inventory.objects.create(
            item=self.item,
            location=self.location,
            quantity=100,
            reserved_qty=30,
        )
        inventory.refresh_from_db()
        self.assertEqual(inventory.available_qty, 70)
