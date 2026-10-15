# MISSION: BUILD AND DEPLOY "SLAINTE-ENGINE" (CLINICAL AI INTEROPERABILITY APPLIANCE)

You are the Principal Systems Architect and Lead Full-Stack HealthTech Engineer. Your task is to unify three components located in our current workspace into a single, production-grade, containerized clinical integration product.

## WORKSPACE CONTEXT & DIRECTORIES
The current workspace contains three core assets:
1. `./openhands/` — Sandboxed autonomous developer/agent environment.
2. `./slainte-scan-mcp/` — Python Model Context Protocol (MCP) server containing deterministic clinical tooling, Manchester Triage System (MTS) rules, terminology resolution (SNOMED-CT / LOINC), and FHIR R4 schema validation.
3. `./frontend/` (Patient-Dashboard-htmx-python-fhir) — Ultra-fast, lightweight clinical dashboard powered by Python, FastAPI/Flask, and HTMX that ingests and renders FHIR R4 bundles (triage queue, vitals, observations, patient timelines).

## PRODUCT DEFINITION: "SLAINTE-ENGINE"
An autonomous, zero-trust clinical ingestion appliance that allows healthcare teams, field clinics, and regional health trusts to ingest unstructured/messy clinical CSVs, legacy database dumps, or triage notes, convert them into mathematically verified FHIR R4 resources via an autonomous agent pipeline bound by deterministic MCP guardrails, and visualize them immediately on an HTMX dashboard.

---

### CORE ARCHITECTURAL REQUIREMENTS

#### 1. Pluggable AI Provider Configuration
The appliance MUST allow the operator to bring their own model via environment variables or a configuration file (`.env` or `config.toml`):
- Local Models: Ollama (e.g., `ollama/qwen2.5-coder:32b`, `ollama/deepseek-r1`, `ollama/llama3.3`) via local host networking (`http://host.docker.internal:11434` or local bridge).
- Frontier Cloud Providers: Google Gemini (`gemini-3.8-flash`, `gemini-1.5-pro`), Anthropic (`claude-3-7-sonnet`), and OpenAI (`o3-mini`, `gpt-4o`).
- LiteLLM / OpenHands native model routing must be configured cleanly so the agent loop respects user choice without requiring code edits.

#### 2. MCP Integration & Agent Binding
- Configure OpenHands (`config.toml` or runtime startup) to automatically register and expose `./slainte-scan-mcp` as an active tool server.
- The agent must be explicitly instructed on its system prompt loop:
  * Step A: Scan raw input directory (`/workspace/data/raw/`).
  * Step B: Call `slainte-scan-mcp` tools (`scan_clinical_schema`, `resolve_terminology`, `validate_fhir_resource`).
  * Step C: Write and execute deterministic Python conversion scripts in the sandbox.
  * Step D: Validate output FHIR bundles against the MCP schema validator. Never output hallucinated or unvalidated resources.
  * Step E: Output clean FHIR bundles to `/workspace/data/fhir_store/`.

#### 3. HTMX Dashboard Binding (`frontend`)
- Wire `./frontend` to continuously or dynamically read from `/workspace/data/fhir_store/` (or via an internal API endpoint).
- Ensure the HTMX interface displays:
  * Live Triage Queue (sorted by MTS priority / urgency).
  * Patient Detail Modal / View (Demographics, Conditions, Observations, Vital Signs trend graphs).
  * Pipeline Status Indicator (showing OpenHands ingestion runs and validation logs).

#### 4. Turnkey Docker Deployment
- Create a root `docker-compose.yml` and unified Docker configuration that spins up the entire appliance in one command: `docker compose up --build`.
- Ensure proper volume mounting:
  * Mount `/data/raw` for dropping messy clinical files.
  * Mount `/data/fhir_store` for persistent storage of validated FHIR JSON.
  * Configure networking so the OpenHands container, the MCP server, the HTMX dashboard, and the host machine (including local Ollama) can communicate seamlessly.

---

### EXECUTION ROADMAP: WHAT YOU MUST DELIVER RIGHT NOW

Please execute the following steps systematically, inspecting files, generating configuration files, and writing the glue code:

1. **Workspace Inspection & Verification:**
   - Inspect the schemas and entrypoints inside `./slainte-scan-mcp/` and `./frontend/`.
   - Identify any missing glue scripts, port conflicts, or dependency mismatches.

2. **OpenHands Configuration (`openhands_config.toml` & MCP Adapter):**
   - Provide the complete OpenHands configuration file connecting the agent runtime to `./slainte-scan-mcp`.
   - Provide the Agent Execution System Prompt that enforces zero-hallucination FHIR conversions.

3. **Dashboard Integration Layer:**
   - Ensure `./frontend/` has an endpoint or file-watcher to immediately load FHIR bundles produced by the agent. If an ingest endpoint or storage directory path needs adjusting, write the patch.

4. **Single-Command Orchestration (`docker-compose.yml` & `.env.example`):**
   - Write a complete `docker-compose.yml` coordinating:
     * `slainte-dashboard` (Port 8000 or 5000: HTMX Frontend)
     * `slainte-openhands` (Port 3000 / 8080: Agent Canvas / Execution engine)
     * Supporting volumes and health checks.
   - Provide a turnkey `.env.example` showing exact configurations for:
     * Mode A: Local Ollama (100% offline & private)
     * Mode B: Google Gemini API (Flash 3.8 / Pro)
     * Mode C: Anthropic Claude / OpenAI

5. **End-to-End Verification Test Script:**
   - Write a test runner script (`scripts/test_pipeline.sh` or `test_pipeline.py`) that:
     1. Drops a mock messy clinical CSV (with triage complaints, unstandardized vitals, and dates) into the raw folder.
     2. Triggers the agent loop.
     3. Asserts that valid FHIR R4 JSON is generated and validated.
     4. Asserts that the HTMX dashboard returns HTTP 200 and renders the patient card.

Proceed step-by-step with complete, production-ready code. No placeholders, no skipped steps.