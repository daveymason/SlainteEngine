FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    WORKSPACE_BASE=/workspace \
    PYTHONPATH=/workspace:/workspace/slainte-scan-mcp

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies for agent & MCP client
COPY openhands/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Create workspace dirs
RUN mkdir -p /workspace/data/raw \
             /workspace/data/fhir_store \
             /workspace/openhands/trajectories

COPY openhands/ /workspace/openhands/

EXPOSE 3000

CMD ["python3", "/workspace/openhands/agent_runner.py", "--interval", "5"]
