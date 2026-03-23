FROM python:3.12-slim AS base
WORKDIR /app

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HTTP_PROXY=${HTTP_PROXY} \
    HTTPS_PROXY=${HTTPS_PROXY} \
    NO_PROXY=${NO_PROXY}

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies from requirements (simple + predictable).
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