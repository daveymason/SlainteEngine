"""SlainteTech AI Security Labs — Autonomous 11-Agent Fleet Package."""
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

__all__ = [
    "BaseAgent",
    "AgentExecutionResult",
    "AGENTS_CATALOG",
    "get_agent_by_id",
    "get_all_agents_with_settings",
    "save_agent_settings",
    "get_agent_instance",
    "BolaRedTeamAgent",
    "FhirConformanceAgent",
    "CveVulnerabilityAgent",
    "run_cve_vulnerability_scan",
    "GdprPrivacyAgent",
    "run_gdpr_privacy_scan",
    "ImmutableAuditAgent",
    "run_immutable_audit_scan",
    "verify_sqlite_immutability_live",
    "build_signed_audit_snapshot",
    "MultimodalIngestAgent",
    "PatientSummariserAgent",
    "MedicationSafetyAgent",
    "AcuityTriageAgent",
    "AmbientScribeAgent",
    "ClinicalCodingAgent",
]
