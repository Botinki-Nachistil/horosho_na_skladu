FROM python:3.12-slim AS base
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-django.txt /requirements.txt
RUN pip install --no-cache-dir --retries 10 --timeout 120 -r /requirements.txt

#Dev
FROM base AS development
EXPOSE 8001
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]

#Prod
FROM base AS production
COPY . .
EXPOSE 8001
RUN python manage.py collectstatic --noinput --settings=config.settings || true
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8001", \
     "--workers", "4", \
     "--timeout", "30", \
     "--access-logfile", "-"]