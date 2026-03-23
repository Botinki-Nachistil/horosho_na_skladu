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

# Some [uvicorn] extras may require compilation (e.g. uvloop/httptools).
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies from requirements (simple + predictable).
COPY requirements-fastapi.txt /requirements.txt
RUN pip install --no-cache-dir --retries 10 --timeout 120 -r /requirements.txt

FROM base AS development
EXPOSE 8001
CMD ["uvicorn", "src.main_fastapi:app", "--host", "0.0.0.0", "--port", "8001"]

FROM base AS production
COPY . .
EXPOSE 8001
CMD ["uvicorn", "src.main_fastapi:app", "--host", "0.0.0.0", "--port", "8001"]
