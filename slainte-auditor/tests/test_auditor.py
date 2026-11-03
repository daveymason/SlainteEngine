"""Unit and integration tests for the SlainteFHIR Red-Team & Semantic Verifier Agent."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

import httpx
import pytest

# Ensure slainte-auditor root is on sys.path
AUDITOR_ROOT = Path(__file__).resolve().parent.parent
if str(AUDITOR_ROOT) not in sys.path:
    sys.path.insert(0, str(AUDITOR_ROOT))

from src.conformance_filter import (
    SandboxSecurityViolation,
    filter_capability_statement,
    verify_sandbox_target,
)
from src.redteam_bola_agent import FhirRedTeamAgent, SharedAuditMemory
from src.sarif_reporter import build_sarif_report, save_sarif_report
from src.terminology_verifier import verify_bundle_terminology


def test_sandbox_guardrail_blocks_public_ips_and_allows_local():
    assert verify_sandbox_target("http://localhost:8082/fhir/r4") == "localhost"
    assert verify_sandbox_target("http://127.0.0.1:8082") == "127.0.0.1"
    assert verify_sandbox_target("http://slainte-fhir:8082") == "slainte-fhir"
    assert verify_sandbox_target("http://172.18.0.4:8082") == "172.18.0.4"

    with pytest.raises(SandboxSecurityViolation):
        verify_sandbox_target("https://8.8.8.8/fhir/r4")


def test_capability_statement_reachability_pruning():
    cap = {
        "resourceType": "CapabilityStatement",
        "fhirVersion": "4.0.1",
        "experimental": True,
        "rest": [
            {
                "mode": "server",
                "resource": [
                    {"type": "Patient", "interaction": [{"code": "read"}]},
                    {"type": "Observation", "interaction": [{"code": "read"}]},
                    {"type": "Binary", "interaction": [{"code": "read"}]},
                    {"type": "ValueSet", "interaction": [{"code": "read"}]},
                ],
            }
        ],
    }
    surface = filter_capability_statement(cap, "http://slainte-fhir:8082", require_experimental=True)
    assert "Patient" in surface.active_compartment_resources
    assert "Observation" in surface.active_compartment_resources
    assert "Binary" in surface.bridge_resources
    assert "ValueSet" in surface.pruned_resources
    assert surface.reduction_ratio > 0.6


def test_terminology_verifier_detects_oid_ucum_snomed_and_allergy_drift():
    sample_bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "pt-1",
                    "identifier": [
                        {
                            "system": "urn:oid:1.3.6.1.4.1.54392.5.2690.42.80",
                            "value": "99101-A",
                        }
                    ],
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "cond-1",
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "404684003",
                                "display": "Clinical finding: mysterious symptom",
                            }
                        ]
                    },
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "obs-bp",
                    "code": {
                        "coding": [{"system": "http://loinc.org", "code": "8480-6"}]
                    },
                    "valueQuantity": {"value": 130, "code": "mmHg"},
                }
            },
            {
                "resource": {
                    "resourceType": "AllergyIntolerance",
                    "id": "alg-1",
                    "code": {"text": "Severe Penicillin anaphylaxis", "coding": [{"code": "91936005"}]},
                }
            },
            {
                "resource": {
                    "resourceType": "MedicationRequest",
                    "id": "med-1",
                    "medicationCodeableConcept": {"text": "Co-Amoxiclav 625mg TDS"},
                }
            },
        ],
    }
    findings = verify_bundle_terminology(sample_bundle)
    rule_ids = {f.rule_id for f in findings}
    assert "FHIR-OID-DRIFT-002" in rule_ids
    assert "SNOMED-FALLBACK-002" in rule_ids
    assert "UCUM-UNIT-001" in rule_ids
    assert "CDS-CONTRAINDICATION-001" in rule_ids


def test_dual_phase_reflection_inter_reflection_pivot_after_three_403s():
    mem = SharedAuditMemory()
    assert not mem.is_hardened("VEC_1", "ID_PAT_A")
    mem.record("VEC_1", "ID_PAT_A", "GET", "/fhir/r4/Observation/1", 403, 4.2)
    mem.record("VEC_1", "ID_PAT_A", "GET", "/fhir/r4/Observation/2", 403, 3.8)
    e3 = mem.record("VEC_1", "ID_PAT_A", "GET", "/fhir/r4/Observation/3", 403, 3.5)
    assert mem.is_hardened("VEC_1", "ID_PAT_A")
    assert e3.reflection_action == "INTER_REFLECTION_PIVOT"


def test_redteam_agent_detects_bola_cors_and_validator_crash_with_sarif_export(tmp_path):
    def mock_fhir_handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        headers = {
            "access-control-allow-origin": request.headers.get("Origin", "*"),
            "access-control-allow-credentials": "true",
        }
        if path == "/fhir/r4/Patient" and request.method == "GET":
            return httpx.Response(
                200,
                headers=headers,
                json={
                    "resourceType": "Bundle",
                    "type": "searchset",
                    "total": 1,
                    "entry": [
                        {
                            "resource": {
                                "resourceType": "Patient",
                                "id": "patient-case-1",
                                "name": [{"family": "Murphy"}],
                            }
                        }
                    ],
                },
            )
        if path == "/fhir/r4/Patient/patient-case-1" and request.method == "GET":
            # Simulates unauthenticated / BOLA leak on SlainteFHIR
            return httpx.Response(
                200,
                headers=headers,
                json={"resourceType": "Patient", "id": "patient-case-1", "name": [{"family": "Murphy"}]},
            )
        if path == "/fhir/r4/Observation" and request.method == "GET":
            return httpx.Response(
                200,
                headers=headers,
                json={
                    "resourceType": "Bundle",
                    "type": "searchset",
                    "total": 1,
                    "entry": [{"resource": {"resourceType": "Observation", "id": "obs-1"}}],
                },
            )
        if path == "/fhir/r4/$validate" and request.method == "POST":
            # Simulates verification_engine.py KeyError on non-cohort patient ID
            return httpx.Response(
                422,
                headers=headers,
                json={
                    "resourceType": "OperationOutcome",
                    "issue": [
                        {
                            "severity": "error",
                            "code": "invalid",
                            "diagnostics": "'patient-redteam-999'",
                        }
                    ],
                },
            )
        return httpx.Response(404, headers=headers)

    transport = httpx.MockTransport(mock_fhir_handler)
    agent = FhirRedTeamAgent(base_url="http://slainte-fhir:8082", transport=transport)
    sec_findings = agent.run_campaign()

    rule_ids = {f.rule_id for f in sec_findings}
    assert "SLAINTE-BOLA-001" in rule_ids
    assert "SLAINTE-CORS-002" in rule_ids
    assert "SLAINTE-BOLA-003" in rule_ids
    assert "SLAINTE-VAL-CRASH-004" in rule_ids

    sarif = build_sarif_report(sec_findings, [])
    out_path = save_sarif_report(sarif, tmp_path / "slaintefhir-audit.sarif.json")
    assert out_path.exists()
    loaded = json.loads(out_path.read_text(encoding="utf-8"))
    assert loaded["version"] == "2.1.0"
    assert len(loaded["runs"][0]["results"]) == 4


def test_auditor_dashboard_ui_routes_render_stats_boxes_and_logs(tmp_path):
    """Verifies the SlainteDash UI routes (/fhir/Auditor, /fhir/auditor/run, /fhir/auditor/sarif)."""
    frontend_dir = AUDITOR_ROOT.parent / "frontend"
    if str(frontend_dir) not in sys.path:
        sys.path.insert(0, str(frontend_dir))

    import app as dashboard_app
    import auth
    import db as dashboard_db

    class TestConfig:
        TESTING = True
        DEBUG = True
        SECRET_KEY = "test-secret-key-for-auditor-ui"
        WTF_CSRF_ENABLED = False
        DATABASE_PATH = str(tmp_path / "test_ui.db")
        FHIR_SERVER_URL = "http://localhost:8082/fhir/r4"
        FHIR_STORE_PATH = str(AUDITOR_ROOT.parent / "data" / "fhir_store")
        RAW_DATA_PATH = str(tmp_path / "raw")
        FHIR_PAGE_SIZE = 10
        FHIR_TIMEOUT = 2.0
        LOG_LEVEL = "WARNING"
        LOG_JSON = False
        RATELIMIT_ENABLED = False
        RATELIMIT_AUTH = "100/minute"
        HEALTH_SHOW_BACKEND = True
        APPLIANCE_MODE = True

    flask_app = dashboard_app.create_app(TestConfig)
    with flask_app.app_context():
        dashboard_db.grant_admin("auditor_admin", auth.hash_password("ValidPass123!"))

    client = flask_app.test_client()
    login_resp = client.post(
        "/login",
        data={"username": "auditor_admin", "password": "ValidPass123!"},
        follow_redirects=True,
    )
    assert login_resp.status_code == 200

    # 1. GET /fhir/Auditor renders top KPI stat boxes and execution logs
    resp = client.get("/fhir/Auditor")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Slainte-Auditor: Autonomous FHIR R4 Verifier" in html
    assert "Surface Reduction" in html
    assert "FHIR Bundles Audited" in html
    assert "BOLA / Auth Findings" in html
    assert "Ontology &amp; UCUM Drift" in html
    assert "Reflection Memory" in html
    assert "Slainte-Auditor Live Execution Logs" in html

    # 2. POST /fhir/auditor/run triggers a live audit cycle and returns updated fragment
    run_resp = client.post("/fhir/auditor/run")
    assert run_resp.status_code == 200
    run_html = run_resp.get_data(as_text=True)
    assert "STAGE-1:GUARDRAIL" in run_html
    assert "STAGE-3:ORACLE" in run_html
    assert "SLAINTE-BOLA-001" in run_html

    # 3. GET /fhir/auditor/sarif returns valid OASIS SARIF v2.1.0 JSON
    sarif_resp = client.get("/fhir/auditor/sarif")
    assert sarif_resp.status_code == 200
    sarif_json = sarif_resp.get_json()
    assert sarif_json["version"] == "2.1.0"
    assert len(sarif_json["runs"][0]["results"]) > 0
