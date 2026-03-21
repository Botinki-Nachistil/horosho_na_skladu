from __future__ import annotations

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction

from shared.seed_blueprint import build_seed_records


class Command(BaseCommand):
    help = "Seed warehouse demo data in an idempotent way."

    @transaction.atomic
    def handle(self, *args, **options):
        for record in build_seed_records():
            app_label, model_name = record["model"].split(".")
            model = apps.get_model(app_label, model_name)
            fields = dict(record["fields"])
            m2m_fields = {}

            for field_name in list(fields):
                if getattr(model._meta.get_field(field_name), "many_to_many", False):
                    m2m_fields[field_name] = fields.pop(field_name)

            obj = model.objects.filter(pk=record["pk"]).first() or model(pk=record["pk"])
            for field_name, value in fields.items():
                field = model._meta.get_field(field_name)
                if field.is_relation and value is not None:
                    related_model = field.remote_field.model
                    value = related_model.objects.get(pk=value)
                elif not field.is_relation:
                    value = field.to_python(value)
                setattr(obj, field_name, value)
            obj._skip_audit = True
            obj.save()

            for field_name, value in m2m_fields.items():
                getattr(obj, field_name).set(value)

        self.stdout.write(self.style.SUCCESS("Seed data loaded"))
