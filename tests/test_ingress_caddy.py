"""Ingress Reverse Proxy and TLS Verification Tests."""
import os
import subprocess
import pytest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CADDYFILE_PATH = os.path.join(REPO_ROOT, "deploy", "Caddyfile")
COMPOSE_PATH = os.path.join(REPO_ROOT, "docker-compose.yml")


def test_caddyfile_exists_and_contains_required_ingress_routes():
    """Verify Caddyfile defines reverse proxy routes for FHIR and dashboard."""
    assert os.path.exists(CADDYFILE_PATH), f"Caddyfile not found at {CADDYFILE_PATH}"
    with open(CADDYFILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Route definitions
    assert ":80" in content, "Missing HTTP :80 block"
    assert ":443" in content, "Missing HTTPS :443 block"
    assert "handle /fhir/r4*" in content, "Missing /fhir/r4 route handler"
    assert "slainte-fhir:8082" in content, "Missing reverse_proxy to slainte-fhir:8082"
    assert "slainte-dashboard:8000" in content, "Missing reverse_proxy to slainte-dashboard:8000"

    # Security headers
    assert "Strict-Transport-Security" in content, "Missing HSTS security header"
    assert "X-Content-Type-Options" in content, "Missing X-Content-Type-Options"
    assert "X-Frame-Options" in content, "Missing X-Frame-Options"


def test_docker_compose_ingress_service():
    """Verify docker-compose.yml configures slainte-ingress with ports 80/443 and correct volumes."""
    assert os.path.exists(COMPOSE_PATH), f"docker-compose.yml not found at {COMPOSE_PATH}"
    with open(COMPOSE_PATH, "r", encoding="utf-8") as f:
        compose_cfg = yaml.safe_load(f)

    services = compose_cfg.get("services", {})
    assert "slainte-ingress" in services, "slainte-ingress service missing from docker-compose.yml"
    ingress = services["slainte-ingress"]

    assert "ports" in ingress, "slainte-ingress must expose ports"
    ports = [str(p) for p in ingress["ports"]]
    assert any("80:80" in p for p in ports), f"Port 80 not exposed in {ports}"
    assert any("443:443" in p for p in ports), f"Port 443 not exposed in {ports}"

    volumes = ingress.get("volumes", [])
    vol_str = " ".join(volumes)
    assert "Caddyfile" in vol_str, "Caddyfile not mounted in slainte-ingress"


def test_caddy_syntax_validation():
    """Verify Caddy syntax using caddy validate in container if docker is available."""
    docker_check = subprocess.run(["which", "docker"], capture_output=True, text=True)
    if docker_check.returncode != 0:
        pytest.skip("Docker not installed in environment")

    cmd = [
        "docker", "run", "--rm",
        "-v", f"{CADDYFILE_PATH}:/etc/caddy/Caddyfile:ro",
        "caddy:2-alpine",
        "caddy", "validate", "--config", "/etc/caddy/Caddyfile"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"Caddyfile validation failed: {res.stderr}\n{res.stdout}"
    assert "Valid configuration" in res.stdout or "Valid configuration" in res.stderr
