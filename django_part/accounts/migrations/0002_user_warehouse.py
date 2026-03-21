from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("warehouse", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="warehouse",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="users",
                to="warehouse.warehouse",
            ),
        ),
    ]
