from django.test import TestCase

from accounts.models import User
from warehouse.models import Warehouse


class TestUserModel(TestCase):
    def test_user_has_warehouse_fk(self):
        warehouse = Warehouse.objects.create(name="Test WH")
        user = User.objects.create_user(
            username="worker1",
            password="pass",
            role=User.Role.WORKER,
            warehouse=warehouse,
        )
        self.assertEqual(user.warehouse, warehouse)
