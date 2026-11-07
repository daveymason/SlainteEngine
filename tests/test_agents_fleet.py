"""Unit and integration tests for the unified SlainteTech 16-Agent Fleet."""
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
    ClinicOnboardingAgent,
    Nis2ComplianceAgent,
)
from agents.clinical import (
    MultimodalIngestAgent,
    PatientSummariserAgent,
    MedicationSafetyAgent,
    AcuityTriageAgent,
    AmbientScribeAgent,
    ClinicalCodingAgent,
    DischargeTransferAgent,
    EmsPrealertAgent,
    ChronicSurveillanceAgent,
)
from agents.runner import run_agent, health_check_all, run_all_governance_agents


def test_agents_catalog_integrity():
    assert len(AGENTS_CATALOG) == 16
    ids = [a['id'] for a in AGENTS_CATALOG]
    assert len(set(ids)) == 16
    numbers = [a['number'] for a in AGENTS_CATALOG]
    expected = [f"{i:02d}" for i in range(1, 17)]
    assert numbers == expected


def test_get_agent_by_id():
    for i in range(1, 17):
        num = f"{i:02d}"
        ag = get_agent_by_id(num)
        assert ag is not None
        assert ag['number'] == num
        assert get_agent_by_id(ag['id'])['id'] == ag['id']
        assert get_agent_by_id(ag['slug'])['id'] == ag['id']


def test_instantiate_all_16_agents():
    for ag_meta in AGENTS_CATALOG:
        instance = get_agent_instance(ag_meta['id'])
        assert instance is not None, f"Failed to instantiate agent {ag_meta['id']}"
        assert isinstance(instance, BaseAgent)
        assert instance.id == ag_meta['id']
        assert instance.number == ag_meta['number']
        assert instance.code == ag_meta['code']
        assert instance.health_check() in (True, False)


def test_runner_unified_interface():
    res = run_agent("clinic_onboarding")
    assert isinstance(res, AgentExecutionResult)
    assert res.agent_id == "clinic_onboarding"
    assert res.status == "pass"

    healths = health_check_all()
    assert len(healths) == 16

    unknown = run_agent("non_existent_agent")
    assert unknown.status == "fail"


def test_new_agents_execution():
    # 12 Onboarding
    onboard = ClinicOnboardingAgent()
    r12 = onboard.run()
    assert r12.agent_id == "clinic_onboarding"
    assert r12.status == "pass"

    # 13 Discharge
    discharge = DischargeTransferAgent()
    r13 = discharge.run({"vitals": {"sbp": 118, "hr": 70, "spo2": 99, "rr": 14, "temp": 36.6}})
    assert r13.agent_id == "discharge_transfer"
    assert r13.status == "pass"

    # 14 EMS Prealert
    ems = EmsPrealertAgent()
    r14 = ems.run({"vitals": {"sbp": 85, "hr": 130, "spo2": 88, "rr": 30, "temp": 39.5}})
    assert r14.agent_id == "ems_prealert"
    assert r14.status == "warning"

    # 15 Chronic Surveillance
    cdm = ChronicSurveillanceAgent()
    r15 = cdm.run()
    assert r15.agent_id == "chronic_surveillance"
    assert "care gap" in r15.summary.lower()

    # 16 NIS2 Compliance
    nis2 = Nis2ComplianceAgent()
    r16 = nis2.run()
    assert r16.agent_id == "nis2_compliance"
    assert r16.status == "pass"



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
