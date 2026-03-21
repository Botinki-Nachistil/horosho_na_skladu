FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

COPY . .
RUN chmod +x docker-entrypoint.sh

CMD ["./docker-entrypoint.sh", "python", "manage.py", "runserver", "0.0.0.0:8001"]
