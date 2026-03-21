#!/bin/sh
set -eu

python manage.py migrate --noinput

if python manage.py shell -c "from warehouse.models import Warehouse; raise SystemExit(0 if Warehouse.objects.exists() else 1)"; then
  echo "Seed data already present"
else
  python manage.py loaddata fixtures/initial_data.json
fi

exec "$@"
