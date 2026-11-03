FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PORT=8082 \
    DB_PATH=/app/data/fhir_store/fhir_store.db \
    SEED_FILE=/app/data.json

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data/fhir_store

EXPOSE 8082

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://127.0.0.1:8082/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8082"]
