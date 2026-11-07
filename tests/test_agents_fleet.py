"""Unit and integration tests for the unified SlainteTech 11-Agent Fleet."""
import pytest
from agents.base import BaseAgent, AgentExecutionResult
from agents.registry import (
    AGENTS_CATALOG,
    get_agent_by_id,
    get_all_agents_with_settings,
    save_agent_settings,
    get_agent_instance,
)
from agents.governance import (
    BolaRedTeamAgent,
    FhirConformanceAgent,
    CveVulnerabilityAgent,
    run_cve_vulnerability_scan,
    GdprPrivacyAgent,
    run_gdpr_privacy_scan,
    ImmutableAuditAgent,
    run_immutable_audit_scan,
    verify_sqlite_immutability_live,
    build_signed_audit_snapshot,
)
from agents.clinical import (
    MultimodalIngestAgent,
    PatientSummariserAgent,
    MedicationSafetyAgent,
    AcuityTriageAgent,
    AmbientScribeAgent,
    ClinicalCodingAgent,
)


def test_agents_catalog_integrity():
    assert len(AGENTS_CATALOG) == 11
    ids = [a['id'] for a in AGENTS_CATALOG]
    assert len(set(ids)) == 11
    numbers = [a['number'] for a in AGENTS_CATALOG]
    assert numbers == ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11']


def test_get_agent_by_id():
    for num in ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11'):
        ag = get_agent_by_id(num)
        assert ag is not None
        assert ag['number'] == num
        # Test lookup by id and slug
        assert get_agent_by_id(ag['id'])['id'] == ag['id']
        assert get_agent_by_id(ag['slug'])['id'] == ag['id']


def test_instantiate_all_11_agents():
    for ag_meta in AGENTS_CATALOG:
        instance = get_agent_instance(ag_meta['id'])
        assert instance is not None, f"Failed to instantiate agent {ag_meta['id']}"
        assert isinstance(instance, BaseAgent)
        assert instance.id == ag_meta['id']
        assert instance.number == ag_meta['number']
        assert instance.code == ag_meta['code']
        assert instance.health_check() in (True, False)


def test_cve_vulnerability_agent():
    agent = CveVulnerabilityAgent()
    res = agent.run({"app_config": {}})
    assert isinstance(res, AgentExecutionResult)
    assert res.agent_id == "cve_vulnerability"
    assert res.status in ("pass", "warning", "fail")
    assert "checks" in res.telemetry


def test_gdpr_privacy_agent():
    class DummyDB:
        def read_ai_exchange(self, limit=20):
            return [{"id": 1, "deidentified": 1}]
        def read_break_glass_grants(self, limit=20):
            return []

    agent = GdprPrivacyAgent()
    res = agent.run({"app_config": {"AI_DEIDENTIFY": "always"}, "db": DummyDB()})
    assert isinstance(res, AgentExecutionResult)
    assert res.agent_id == "gdpr_privacy"
    assert res.status in ("pass", "warning")


def test_immutable_audit_agent():
    class DummyDB:
        def get_connection(self):
            class DummyConn:
                def execute(self, q, *args):
                    class DummyCursor:
                        def fetchall(self):
                            return [{"name": "audit_log_no_update"}, {"name": "audit_log_no_delete"}, {"name": "ai_exchange_no_update"}, {"name": "ai_exchange_no_delete"}]
                        def fetchone(self):
                            return None
                    return DummyCursor()
            return DummyConn()
        def read_audit(self, limit=30):
            return []
        def read_ai_exchange(self, limit=30):
            return []
        def read_break_glass_grants(self, limit=20):
            return []

    agent = ImmutableAuditAgent()
    res = agent.run({"db": DummyDB()})
    assert isinstance(res, AgentExecutionResult)
    assert res.agent_id == "immutable_audit"
    assert res.status == "pass"


def test_clinical_agents_execution():
    # 06 Ingest
    ingest = MultimodalIngestAgent()
    r6 = ingest.run()
    assert r6.agent_id == "multimodal_ingest"

    # 07 Summariser
    summariser = PatientSummariserAgent()
    r7 = summariser.run({"patient": {"id": "P101", "name": "Mary Higgins", "age": 62, "gender": "Female"}})
    assert r7.agent_id == "patient_summariser"
    assert "Mary Higgins" in r7.summary or "P101" in r7.summary

    # 08 Rx Guard
    rx = MedicationSafetyAgent()
    r8 = rx.run({"allergies": ["Penicillin"], "medications": ["Amoxicillin"]})
    assert r8.agent_id == "medication_safety"

    # 09 Acuity Triage
    triage = AcuityTriageAgent()
    r9 = triage.run({"vitals": {"rr": 18, "spo2": 98, "sbp": 120, "hr": 72, "temp": 36.8}})
    assert r9.agent_id == "acuity_triage"

    # 10 Ambient Scribe
    scribe = AmbientScribeAgent()
    r10 = scribe.run({"transcript": "Patient complains of chest tightness and mild dyspnea for 2 days."})
    assert r10.agent_id == "ambient_scribe"

    # 11 Rev Coding
    coding = ClinicalCodingAgent()
    r11 = coding.run({"patient_id": "P101", "conditions": [], "observations": []})
    assert r11.agent_id == "clinical_coding"
