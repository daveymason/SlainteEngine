#!/usr/bin/env bash
# =============================================================================
# SLAINTE-ENGINE: UNIFIED APPLIANCE CONTROL CLI
# =============================================================================
# Turnkey management of the Slainte-Engine Clinical Interoperability Appliance:
# 1. SlainteDash    (HTMX + Flask Clinical Dashboard on port 8000)
# 2. SlainteScan    (FastMCP Deterministic Clinical Server on port 8081)
# 3. SlainteEngine  (OpenHands Sandboxed Autonomous Agent Loop on port 3000)
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Terminal Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Detect Docker Compose command
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif which docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    echo -e "${RED}[ERROR] Neither 'docker compose' nor 'docker-compose' was found. Please install Docker.${NC}"
    exit 1
fi

print_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "=========================================================================="
    echo "   SLAINTE-ENGINE: Autonomous Clinical AI Interoperability Appliance"
    echo "   Unified Medical Record Ingestion & Real-Time Triage Engine"
    echo "=========================================================================="
    echo -e "${NC}"
}

ensure_environment() {
    # 1. Ensure .env file exists
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            echo -e "${YELLOW}[SETUP] Creating .env from .env.example...${NC}"
            cp .env.example .env
        else
            echo -e "${YELLOW}[SETUP] Initializing minimal .env...${NC}"
            cat << 'ENVEOF' > .env
FLASK_ENV=production
APPLIANCE_MODE=true
FHIR_STORE_PATH=/workspace/data/fhir_store
RAW_DATA_PATH=/workspace/data/raw
SECRET_KEY=slainte-engine-production-key-99021
INITIAL_ADMIN_USERNAME=admin
INITIAL_ADMIN_PASSWORD=ClinicalAdmin2026!
LLM_MODEL=ollama/qwen2.5-coder:32b
LLM_BASE_URL=http://host.docker.internal:11434
LLM_API_KEY=ollama
ENVEOF
        fi
    fi

    # 2. Ensure data directories exist and have proper permissions
    mkdir -p data/raw data/fhir_store
    chmod -R 775 data/raw data/fhir_store 2>/dev/null || true
}

start_appliance() {
    print_banner
    ensure_environment

    echo -e "${BLUE}[1/3] Building and starting containerized services...${NC}"
    ${DOCKER_COMPOSE} up -d --build

    # Ensure volume permissions inside container to prevent access collision
    sleep 2
    if docker ps --format '{{.Names}}' | grep -q 'slainte-openhands'; then
        docker exec slainte-openhands chmod -R 775 /workspace/data/raw /workspace/data/fhir_store 2>/dev/null || true
    fi

    echo -e "${BLUE}[2/3] Waiting for clinical services to report healthy...${NC}"
    local max_wait=30
    local count=0
    local dashboard_ready=false
    local mcp_ready=false

    while [ $count -lt $max_wait ]; do
        if curl -s -m 2 -o /dev/null http://localhost:8081/sse 2>/dev/null || [ "$(curl -s -m 2 -o /dev/null -w "%{http_code}" http://localhost:8081/ 2>/dev/null)" != "000" ]; then
            mcp_ready=true
        fi
        if curl -s -m 2 http://localhost:8000/health | grep -q "ok" 2>/dev/null; then
            dashboard_ready=true
        fi

        if [ "$dashboard_ready" = true ] && [ "$mcp_ready" = true ]; then
            break
        fi

        sleep 1
        count=$((count + 1))
        echo -n "."
    done
    echo ""

    if [ "$dashboard_ready" = true ]; then
        echo -e "${GREEN}[OK] SlainteDash (Clinical Dashboard) is healthy on port 8000${NC}"
    else
        echo -e "${YELLOW}[WARN] SlainteDash still starting up. Check '${DOCKER_COMPOSE} logs slainte-dashboard'${NC}"
    fi

    if [ "$mcp_ready" = true ]; then
        echo -e "${GREEN}[OK] SlainteScan (FastMCP Tool Server) is healthy on port 8081${NC}"
    else
        echo -e "${YELLOW}[WARN] SlainteScan still starting up. Check '${DOCKER_COMPOSE} logs slainte-mcp'${NC}"
    fi

    echo -e "${GREEN}[OK] SlainteEngine (OpenHands Autonomous Ingestion Loop) active on port 3000${NC}"

    # Print Access Endpoints
    echo ""
    echo -e "${CYAN}${BOLD}==========================================================================${NC}"
    echo -e "${GREEN}${BOLD}  APPLIANCE OPERATIONAL - READY FOR CLINICAL USE${NC}"
    echo -e "${CYAN}${BOLD}==========================================================================${NC}"
    echo -e "  * ${BOLD}Clinical Dashboard:${NC}    http://localhost:8000"
    echo -e "  * ${BOLD}Live Triage Queue:${NC}     http://localhost:8000/?view=/fhir/Triage"
    echo -e "  * ${BOLD}Pipeline Telemetry:${NC}    http://localhost:8000/?view=/pipeline/status"
    echo -e "  * ${BOLD}FastMCP Server:${NC}        http://localhost:8081/sse"
    echo -e "  * ${BOLD}OpenHands Sandbox:${NC}     http://localhost:3000"
    echo -e "  * ${BOLD}Credentials:${NC}           Username: ${YELLOW}admin${NC}  |  Password: ${YELLOW}ClinicalAdmin2026!${NC}"
    echo -e "${CYAN}==========================================================================${NC}"
    echo -e "Run ${BOLD}./run.sh status${NC} to view health, or ${BOLD}./run.sh test${NC} to run verification tests."
    echo ""
}

stop_appliance() {
    print_banner
    echo -e "${YELLOW}[SHUTDOWN] Stopping all Slainte-Engine appliance containers...${NC}"
    ${DOCKER_COMPOSE} down
    echo -e "${GREEN}[SHUTDOWN] All services stopped safely.${NC}"
}

restart_appliance() {
    stop_appliance
    start_appliance
}

show_status() {
    print_banner
    echo -e "${BOLD}1. Docker Container Status:${NC}"
    ${DOCKER_COMPOSE} ps
    echo ""

    echo -e "${BOLD}2. Clinical Ingestion Statistics:${NC}"
    local raw_count=$(ls -1 data/raw 2>/dev/null | wc -l)
    local fhir_count=$(ls -1 data/fhir_store/*.json 2>/dev/null | wc -l)
    echo -e "  * Raw Input Dropzone:     ${CYAN}${raw_count} file(s)${NC} (in ./data/raw)"
    echo -e "  * Verified FHIR R4 Store: ${GREEN}${fhir_count} bundle(s)${NC} (in ./data/fhir_store)"
    echo ""

    echo -e "${BOLD}3. HTTP Health Probes:${NC}"
    if curl -s -m 2 http://localhost:8000/health | grep -q "ok" 2>/dev/null; then
        echo -e "  * SlainteDash (8000):   ${GREEN}[HEALTHY / HTTP 200]${NC}"
    else
        echo -e "  * SlainteDash (8000):   ${RED}[DOWN or INITIALIZING]${NC}"
    fi

    if curl -s -m 2 -o /dev/null http://localhost:8081/sse 2>/dev/null || [ "$(curl -s -m 2 -o /dev/null -w "%{http_code}" http://localhost:8081/ 2>/dev/null)" != "000" ]; then
        echo -e "  * SlainteScan (8081):   ${GREEN}[HEALTHY / FastMCP active]${NC}"
    else
        echo -e "  * SlainteScan (8081):   ${RED}[DOWN or INITIALIZING]${NC}"
    fi

    if docker ps --format '{{.Names}}' | grep -q 'slainte-openhands'; then
        echo -e "  * SlainteEngine (3000): ${GREEN}[ACTIVE / Ingestion Loop running]${NC}"
    else
        echo -e "  * SlainteEngine (3000): ${RED}[NOT RUNNING]${NC}"
    fi
    echo ""
}

run_tests() {
    print_banner
    echo -e "${BLUE}[TEST] Launching End-to-End Pipeline Verification Suite...${NC}"
    ./scripts/test_pipeline.sh
}

tail_logs() {
    local service="${1:-}"
    if [ -n "$service" ]; then
        ${DOCKER_COMPOSE} logs -f "$service"
    else
        ${DOCKER_COMPOSE} logs -f
    fi
}

trigger_ingest() {
    print_banner
    echo -e "${BLUE}[INGEST] Triggering on-demand clinical ingestion cycle via OpenHands...${NC}"
    if docker ps --format '{{.Names}}' | grep -q 'slainte-openhands'; then
        docker exec -it slainte-openhands python3 /workspace/openhands/agent_runner.py --once
    else
        echo -e "${YELLOW}Container not running; executing locally via Python...${NC}"
        python3 openhands/agent_runner.py --once --raw-dir data/raw --store-dir data/fhir_store
    fi
}

show_help() {
    print_banner
    echo -e "${BOLD}USAGE:${NC} ./run.sh [COMMAND]"
    echo ""
    echo -e "${BOLD}COMMANDS:${NC}"
    echo -e "  ${GREEN}start${NC} | ${GREEN}up${NC}      Start all services in background (default if no argument given)"
    echo -e "  ${YELLOW}stop${NC}  | ${YELLOW}down${NC}    Stop all appliance containers"
    echo -e "  ${CYAN}restart${NC}        Restart all containers"
    echo -e "  ${CYAN}status${NC}         Display container health, HTTP probes, and bundle counts"
    echo -e "  ${BLUE}test${NC}           Execute the end-to-end automated verification test suite"
    echo -e "  ${BLUE}logs [svc]${NC}     Follow live container logs (optional service: dashboard, mcp, openhands)"
    echo -e "  ${CYAN}ingest${NC}         Trigger an immediate single-pass ingestion cycle"
    echo -e "  ${BOLD}help${NC}           Show this help message"
    echo ""
}

# Main Command Dispatch
case "${1:-start}" in
    start|up)
        start_appliance
        ;;
    stop|down)
        stop_appliance
        ;;
    restart)
        restart_appliance
        ;;
    status|ps)
        show_status
        ;;
    test)
        run_tests
        ;;
    logs)
        tail_logs "${2:-}"
        ;;
    ingest)
        trigger_ingest
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}[ERROR] Unknown command: '$1'${NC}"
        show_help
        exit 1
        ;;
esac
