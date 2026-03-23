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
    NO_PROXY=${NO_PROXY} \
    FLASK_APP=src.main_flask:app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies from requirements (simple + predictable).
COPY requirements-flask.txt /requirements.txt
RUN pip install --no-cache-dir --retries 10 --timeout 120 -r /requirements.txt

FROM base AS development
EXPOSE 8002
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8002", "--debug"]

FROM base AS production
COPY . .
EXPOSE 8002
CMD ["gunicorn", "src.main_flask:app", \
     "--bind", "0.0.0.0:8002", \
     "--workers", "2"]
