FROM python:3.12-slim

WORKDIR /workspace/slainte-auditor

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV TARGET_FHIR_URL=http://slainte-fhir:8082
ENV MCP_SERVER_URL=http://slainte-mcp:8081
ENV REPORT_OUTPUT_DIR=/workspace/data/audit_reports

CMD ["python3", "auditor_runner.py", "--interval", "30"]
