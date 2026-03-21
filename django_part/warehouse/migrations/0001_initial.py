from __future__ import annotations

from django.db import migrations, models

from shared.db import schema_table


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Warehouse",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                ("address", models.TextField(blank=True)),
                ("config", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": schema_table("warehouse", "warehouse_warehouse")},
        ),
        migrations.CreateModel(
            name="Zone",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                (
                    "zone_type",
                    models.CharField(
                        choices=[
                            ("picking", "Picking"),
                            ("storage", "Storage"),
                            ("shipping", "Shipping"),
                            ("receiving", "Receiving"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "warehouse",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="zones",
                        to="warehouse.warehouse",
                    ),
                ),
            ],
            options={"db_table": schema_table("warehouse", "warehouse_zone")},
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("barcode", models.CharField(max_length=64, unique=True)),
                (
                    "coords",
                    models.JSONField(
                        default=dict,
                        help_text='{"aisle": 3, "rack": 5, "level": 2}',
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "zone",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="locations",
                        to="warehouse.zone",
                    ),
                ),
            ],
            options={"db_table": schema_table("warehouse", "warehouse_location")},
        ),
        migrations.AddConstraint(
            model_name="zone",
            constraint=models.UniqueConstraint(
                fields=("warehouse", "name"),
                name="warehouse_zone_warehouse_name_uniq",
            ),
        ),
        migrations.AddIndex(
            model_name="location",
            index=models.Index(fields=["barcode"], name="warehouse_w_barcode_be23db_idx"),
        ),
    ]
