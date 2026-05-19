FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
RUN uv pip install --system --no-cache -r pyproject.toml

COPY . .

EXPOSE 8002

CMD ["flask", "--app", "wsgi:app", "run", "--host=0.0.0.0", "--port=8002"]
