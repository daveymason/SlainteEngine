"""SlainteTech AI Security Labs — Master 11-Agent Fleet Registry & Catalog."""
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

AVAILABLE_MODELS = [
    ('ollama/k9/lime:latest', 'Local: k9/lime:latest (Ollama)'),
    ('ollama/k9/lime-lite:latest', 'Local: k9/lime-lite:latest (Ollama)'),
    ('ollama/k9/Doggo:3b', 'Local: k9/Doggo:3b (Ollama)'),
    ('ollama/k9/chihuahua:latest', 'Local: k9/chihuahua:latest (Ollama)'),
    ('ollama/recordstore:latest', 'Local: recordstore:latest (Ollama)'),
    ('ollama/gemma3:1b', 'Local: gemma3:1b (Ollama)'),
    ('openai/gpt-6.1-luna', 'Cloud: openai/gpt-6.1-luna (.env Key)'),
]

AGENTS_CATALOG: List[Dict[str, Any]] = [
    {
        'id': 'bola_redteam',
        'slug': 'bola',
        'number': '01',
        'code': 'SlainteShield-BOLA',
        'name': 'BOLA & Role-Boundary Red-Team',
        'fleet': 'governance',
        'squad': 'shield',
        'squad_name': 'SlainteShield — Security & Adversarial Red-Team',
        'icon': 'fas fa-shield-alt',
        'color': 'primary',
        'summary': (
            'Probes cross-patient (CompartmentDefinition/Patient) and cross-vertical role '
            'boundaries using Dual-Phase Reflection (M) to detect OWASP API1:2023 / CWE-863 leaks.'
        ),
        'mcp_tools': ['CompartmentDefinition/Patient', 'Dual-Phase Reflection (M)', 'RFC 1918 Guardrail'],
        'embedded_in': ['Dedicated BOLA Dashboard (/agents/bola_redteam)'],
        'guardrail_label': 'Adversarial Probe Scope',
        'guardrail_options': ['RFC 1918 Private Subnet Only (Strict)', 'Patient + Vertical Role Boundaries', 'Read-Only Compartment Probe'],
        'default_guardrail': 'RFC 1918 Private Subnet Only (Strict)',
    },
    {
        'id': 'fhir_conformance',
        'slug': 'fhir',
        'number': '02',
        'code': 'SlainteShield-FHIR',
        'name': 'FHIR R4 Integrity & Terminology',
        'fleet': 'governance',
        'squad': 'shield',
        'squad_name': 'SlainteShield — Security & Adversarial Red-Team',
        'icon': 'fas fa-file-medical-alt',
        'color': 'primary',
        'summary': (
            'Audits every HL7 FHIR R4 bundle for unmapped SNOMED-CT/LOINC codes, invalid UCUM units, '
            'and missing Irish GMS OIDs, exporting OASIS SARIF v2.1.0 compliance reports.'
        ),
        'mcp_tools': ['validate_fhir_resource', 'resolve_terminology', 'SARIF v2.1.0 Exporter'],
        'embedded_in': ['Dedicated FHIR Integrity Page (/agents/fhir_conformance)'],
        'guardrail_label': 'Terminology & Profile Strictness',
        'guardrail_options': ['Strict Irish Core GMS OID + UCUM', 'Standard HL7 FHIR R4 $validate', 'Audit-Only (Non-Blocking)'],
        'default_guardrail': 'Strict Irish Core GMS OID + UCUM',
    },
    {
        'id': 'cve_vulnerability',
        'slug': 'cve',
        'number': '03',
        'code': 'SlainteShield-CVE',
        'name': 'Supply-Chain & App Vulnerability',
        'fleet': 'governance',
        'squad': 'shield',
        'squad_name': 'SlainteShield — Security & Adversarial Red-Team',
        'icon': 'fas fa-lock',
        'color': 'primary',
        'summary': (
            'Audits pinned Python dependencies (requirements.txt), verifies active Content-Security-Policy (CSP) '
            'and SRI sha384- hashes, and checks multi-worker SqliteStorage rate-limiting posture.'
        ),
        'mcp_tools': ['Dependency Pin Auditor', 'CSP & SRI sha384 Verifier', 'SqliteStorage Rate-Limit Probe'],
        'embedded_in': ['Dedicated CVE Posture Page (/agents/cve_vulnerability)', 'Security Settings'],
        'guardrail_label': 'Vulnerability Policy',
        'guardrail_options': ['Enforce Exact Version Pins + SRI + CSP', 'Warn on Unpinned Dependencies', 'Report-Only'],
        'default_guardrail': 'Enforce Exact Version Pins + SRI + CSP',
    },
    {
        'id': 'gdpr_privacy',
        'slug': 'gdpr',
        'number': '04',
        'code': 'SlainteGov-GDPR',
        'name': 'GDPR Art. 9 & Clinical Privacy Gate',
        'fleet': 'governance',
        'squad': 'gov',
        'squad_name': 'SlainteGov — Privacy, GDPR & Regulatory Governance',
        'icon': 'fas fa-user-shield',
        'color': 'primary',
        'summary': (
            'Enforces EU GDPR Art. 9 (Special Category Health Data) & Irish HIQA rules: verifies AI_DEIDENTIFY '
            'PII stripping, enforces the AI_ALLOW_REAL_PHI BAA gate, and checks salted SHA-256 log pseudonymisation.'
        ),
        'mcp_tools': ['AI_DEIDENTIFY Minimiser', 'AI_ALLOW_REAL_PHI Gate', 'LOG_HASH_SALT Verifier'],
        'embedded_in': ['Dedicated GDPR Page (/agents/gdpr_privacy)', 'AI Settings'],
        'guardrail_label': 'GDPR Art. 9 Data Minimisation',
        'guardrail_options': ['Strip Direct PII + Block Cloud PHI without BAA', 'Local Sovereign Air-Gap Only', 'Strict Safe-Harbor Redaction'],
        'default_guardrail': 'Strip Direct PII + Block Cloud PHI without BAA',
    },
    {
        'id': 'immutable_audit',
        'slug': 'audit',
        'number': '05',
        'code': 'SlainteGov-Audit',
        'name': 'Immutable Clinical & AI Audit Ledger',
        'fleet': 'governance',
        'squad': 'gov',
        'squad_name': 'SlainteGov — Privacy, GDPR & Regulatory Governance',
        'icon': 'fas fa-fingerprint',
        'color': 'primary',
        'summary': (
            'Verifies append-only SQLite triggers on audit_log and ai_exchange, inspects FHIR Provenance '
            'SHA-256 bundle signatures across all 8 verticals, and exports signed audit backup snapshots.'
        ),
        'mcp_tools': ['SQLite Append-Only Trigger Check', 'Provenance SHA-256 Verifier', 'Signed Audit Snapshot Exporter'],
        'embedded_in': ['Dedicated GovAudit Page (/agents/immutable_audit)', 'Patient Provenance Sign-Off'],
        'guardrail_label': 'Audit Retention & Trigger Enforcement',
        'guardrail_options': ['Immutable SQLite Triggers + SHA-256 Provenance', 'HIQA 7-Year Adult / 25-Year Pediatric Policy'],
        'default_guardrail': 'Immutable SQLite Triggers + SHA-256 Provenance',
    },
    {
        'id': 'multimodal_ingest',
        'slug': 'ingest',
        'number': '06',
        'code': 'SlainteEngine-Ingest',
        'name': 'Multimodal Clinical Ingestion Pipeline',
        'fleet': 'clinical',
        'squad': 'clinical',
        'squad_name': 'SlainteClinical — Bedside Intelligence & Ingestion Copilots',
        'icon': 'fas fa-file-import',
        'color': 'primary',
        'summary': (
            'Watches /data/raw, the Intake Modal, and legacy HL7v2 (ADT^A01 / ORU^R01 / RDE^O11) feeds, converting '
            'pipe-hat streams, CSVs, PDFs, and triage notes into GMS-deduplicated HL7 FHIR R4 bundles.'
        ),
        'mcp_tools': ['HL7v2 Pipe-Hat Translator', 'scan_clinical_schema', 'find_patient_id_by_gms'],
        'embedded_in': ['Dedicated Ingestion Pipeline Page (/agents/multimodal_ingest)', 'Intake Modal'],
        'guardrail_label': 'Ingestion Deduplication & Validation',
        'guardrail_options': ['Irish GMS OID Deduplication + FastMCP Gate', 'Strict Schema Rejection on Missing Vitals'],
        'default_guardrail': 'Irish GMS OID Deduplication + FastMCP Gate',
    },
    {
        'id': 'patient_summariser',
        'slug': 'scribe',
        'number': '07',
        'code': 'SlainteScribe-Brief',
        'name': 'Cited Patient Summariser & Handover',
        'fleet': 'clinical',
        'squad': 'clinical',
        'squad_name': 'SlainteClinical — Bedside Intelligence & Ingestion Copilots',
        'icon': 'fas fa-notes-medical',
        'color': 'primary',
        'summary': (
            'Generates a 3-bullet bedside clinical handover briefing on the Patient Details page and Scribe Console, '
            'citing exact [ResourceType/id] tags and logging every exchange to ai_exchange.'
        ),
        'mcp_tools': ['build_patient_context', '[ResourceType/id] Citation Engine', 'write_ai_exchange'],
        'embedded_in': ['Dedicated Scribe Page (/agents/patient_summariser)', 'Patient Details Page'],
        'guardrail_label': 'Citation & Context Policy',
        'guardrail_options': ['Mandatory [ResourceType/id] Citations + Never Drop Allergies', 'Concise 3-Bullet Handover Mode'],
        'default_guardrail': 'Mandatory [ResourceType/id] Citations + Never Drop Allergies',
    },
    {
        'id': 'medication_safety',
        'slug': 'rx',
        'number': '08',
        'code': 'SlainteRx-Guard',
        'name': 'Pharmacotherapy & Allergy Safety Gate',
        'fleet': 'clinical',
        'squad': 'clinical',
        'squad_name': 'SlainteClinical — Bedside Intelligence & Ingestion Copilots',
        'icon': 'fas fa-pills',
        'color': 'primary',
        'summary': (
            'Deterministically screens prescriptions across 3 tiers: (1) Allergy cross-reactivity, '
            '(2) ISMP High-Alert Drug-Drug Interactions, and (3) Patient lab eGFR renal dosing gates.'
        ),
        'mcp_tools': ['3-Tier Pharmacology Engine', 'ISMP High-Alert DDI Matrix', 'LOINC eGFR Renal Gate'],
        'embedded_in': ['Dedicated Rx-Guard Page (/agents/medication_safety)', 'Patient Details Page', 'Pharmacy Vertical'],
        'guardrail_label': 'Pharmacological Interception Mode',
        'guardrail_options': ['Hard Block on Anaphylaxis / Cross-Reactivity', 'Clinician Override with Provenance Sign-Off'],
        'default_guardrail': 'Hard Block on Anaphylaxis / Cross-Reactivity',
    },
    {
        'id': 'acuity_triage',
        'slug': 'triage',
        'number': '09',
        'code': 'SlainteDx-Triage',
        'name': 'Acuity Triage & NEWS2 Deterioration',
        'fleet': 'clinical',
        'squad': 'clinical',
        'squad_name': 'SlainteClinical — Bedside Intelligence & Ingestion Copilots',
        'icon': 'fas fa-heartbeat',
        'color': 'primary',
        'summary': (
            'Evaluates physiological vitals and presenting complaints to compute deterministic Manchester '
            'Triage (Cat 1–5) priority and 24-hour RCP NEWS2 physiological deterioration trajectories.'
        ),
        'mcp_tools': ['calculate_mts_category', 'calculate_news2_score', '24h Vital Sparkline Engine'],
        'embedded_in': ['Dedicated Dx-Triage Page (/agents/acuity_triage)', 'ED/EMS Live Triage Queue', 'Patient Details'],
        'guardrail_label': 'Deterioration Escalation Threshold',
        'guardrail_options': ['RCP NEWS2 Standard (>=5 Medium, >=7 High Risk)', 'Acute Sepsis High-Sensitivity (>=4 Alert)'],
        'default_guardrail': 'RCP NEWS2 Standard (>=5 Medium, >=7 High Risk)',
    },
    {
        'id': 'ambient_scribe',
        'slug': 'voice',
        'number': '10',
        'code': 'SlainteScribe-Voice',
        'name': 'Ambient Clinical Voice Scribe & Order Drafter',
        'fleet': 'clinical',
        'squad': 'clinical',
        'squad_name': 'SlainteClinical — Bedside Intelligence & Ingestion Copilots',
        'icon': 'fas fa-microphone-alt',
        'color': 'primary',
        'summary': (
            'Converts live consultation speech or uploaded audio into structured SOAP DocumentReference notes, '
            'SNOMED-CT Condition candidates, and 3-Tier SlainteRx-Guard pre-screened MedicationRequests.'
        ),
        'mcp_tools': ['Web Speech / Whisper ASR', 'SOAP Clinical Extractor', '3-Tier Rx-Guard Pre-Screen'],
        'embedded_in': ['Dedicated Voice Scribe Page (/agents/ambient_scribe)', 'Patient Details Page', 'GP Vertical'],
        'guardrail_label': 'Ambient Order Commit Policy',
        'guardrail_options': ['Clinician Co-Sign + Mandatory 3-Tier Rx-Guard Pre-Check', 'SOAP Note Draft Only (No Orders)'],
        'default_guardrail': 'Clinician Co-Sign + Mandatory 3-Tier Rx-Guard Pre-Check',
    },
    {
        'id': 'clinical_coding',
        'slug': 'coding',
        'number': '11',
        'code': 'SlainteRev-Coding',
        'name': 'HIPE / ICD-10-AM Clinical Coding & Revenue Audit',
        'fleet': 'clinical',
        'squad': 'gov',
        'squad_name': 'SlainteGov — Privacy, GDPR & Regulatory Governance',
        'icon': 'fas fa-coins',
        'color': 'primary',
        'summary': (
            'Audits FHIR lab & vital Observations (eGFR, HbA1c, Troponin, Lactate, SpO2, BP) against active Conditions '
            'to surface uncoded ICD-10-AM / SNOMED comorbidities and Irish HIPE DRG complexity uplift.'
        ),
        'mcp_tools': ['Lab-to-ICD10 Comorbidity Auditor', 'Irish HIPE DRG Estimator', 'Dual SNOMED+ICD10 Writer'],
        'embedded_in': ['Dedicated Rev-Coding Page (/agents/clinical_coding)', 'Patient Details Page'],
        'guardrail_label': 'Coding Evidence Standard',
        'guardrail_options': ['Require Objective LOINC Lab/Vital Citation ([Observation/id])', 'Advisory Audit Only'],
        'default_guardrail': 'Require Objective LOINC Lab/Vital Citation ([Observation/id])',
    },
    {
        'id': 'clinic_onboarding',
        'slug': 'onboard',
        'number': '12',
        'code': 'SlainteGov-Onboard',
        'name': 'Clinic Onboarding & Legacy Data Migration',
        'fleet': 'governance',
        'squad': 'gov',
        'squad_name': 'SlainteGov — Privacy, GDPR & Regulatory Governance',
        'icon': 'fas fa-hospital-user',
        'color': 'primary',
        'summary': (
            'Introspects raw practice exports (CSV, HL7v2, scanned PDF), maps clinical attributes to LOINC/SNOMED-CT, '
            'and compiles verified Irish Core FHIR R4 Bundles for seamless clinic onboarding.'
        ),
        'mcp_tools': ['scan_clinical_schema', 'resolve_terminology', 'validate_fhir_resource', 'generate_fhir_bundle'],
        'embedded_in': ['Dedicated Onboarding Page (/agents/clinic_onboarding)', 'Settings / Data'],
        'guardrail_label': 'Onboarding Conformance Strictness',
        'guardrail_options': ['Strict Zero-Defect Validation', 'Advisory Schema Discovery Only'],
        'default_guardrail': 'Strict Zero-Defect Validation',
    },
    {
        'id': 'discharge_transfer',
        'slug': 'discharge',
        'number': '13',
        'code': 'SlainteCare-Transfer',
        'name': 'Discharge & Clinical Handover Coordinator',
        'fleet': 'clinical',
        'squad': 'clinical',
        'squad_name': 'SlainteClinical — Bedside Intelligence & Ingestion Copilots',
        'icon': 'fas fa-door-open',
        'color': 'primary',
        'summary': (
            'Verifies patient physiological stability (NEWS2 <= 2), performs discharge medication reconciliation against documented '
            'allergies, and drafts structured electronic transfer letters for primary care continuity.'
        ),
        'mcp_tools': ['calculate_news2_score', 'check_drug_allergy_contraindications', 'Structured Transfer Drafter'],
        'embedded_in': ['Dedicated Discharge Page (/agents/discharge_transfer)', 'Patient Details Page', 'GP Vertical'],
        'guardrail_label': 'Discharge Physiological Stability Gate',
        'guardrail_options': ['Hard Hold on NEWS2 >= 3 or Unchecked Meds', 'Clinician Override with Sign-Off'],
        'default_guardrail': 'Hard Hold on NEWS2 >= 3 or Unchecked Meds',
    },
    {
        'id': 'ems_prealert',
        'slug': 'prealert',
        'number': '14',
        'code': 'SlainteEMS-Alert',
        'name': 'Emergency Pre-Hospital Pre-Alert Agent',
        'fleet': 'clinical',
        'squad': 'clinical',
        'squad_name': 'SlainteClinical — Bedside Intelligence & Ingestion Copilots',
        'icon': 'fas fa-ambulance',
        'color': 'primary',
        'summary': (
            'Evaluates pre-hospital vitals and chief complaints on ambulance tablets to determine Manchester Triage / NEWS2 '
            'urgency and beam structured pre-arrival clinical alerts with ETA to receiving Emergency Departments.'
        ),
        'mcp_tools': ['calculate_mts_category', 'calculate_news2_score', 'ED Pre-Alert Telemetry Beacon'],
        'embedded_in': ['Dedicated Pre-Alert Page (/agents/ems_prealert)', 'EMS Vertical Cockpit', 'ED Triage Queue'],
        'guardrail_label': 'Pre-Alert Auto-Dispatch Threshold',
        'guardrail_options': ['Automatic Dispatch on MTS Cat 1/2 or NEWS2 >= 7', 'Paramedic Manual Confirmation Required'],
        'default_guardrail': 'Automatic Dispatch on MTS Cat 1/2 or NEWS2 >= 7',
    },
    {
        'id': 'chronic_surveillance',
        'slug': 'surveillance',
        'number': '15',
        'code': 'SlainteCare-CDM',
        'name': 'Chronic Disease & Quality Care Surveillance',
        'fleet': 'clinical',
        'squad': 'clinical',
        'squad_name': 'SlainteClinical — Bedside Intelligence & Ingestion Copilots',
        'icon': 'fas fa-stethoscope',
        'color': 'primary',
        'summary': (
            'Continuously audits patient panels for diabetes, hypertension, and CKD to detect overdue surveillance markers '
            '(HbA1c > 12m, eGFR drop, uncontrolled SBP >= 150 mmHg) and surface proactive care-gap alerts.'
        ),
        'mcp_tools': ['CDM Quality Metric Auditor', 'eGFR Trend Evaluator', 'Care-Gap Flagging Engine'],
        'embedded_in': ['Dedicated Surveillance Page (/agents/chronic_surveillance)', 'GP Vertical', 'Patient Details'],
        'guardrail_label': 'Care Gap Escalation Policy',
        'guardrail_options': ['HSE CDM Contract Guidelines (Strict)', 'Advisory Quality Surveillance Only'],
        'default_guardrail': 'HSE CDM Contract Guidelines (Strict)',
    },
    {
        'id': 'nis2_compliance',
        'slug': 'nis2',
        'number': '16',
        'code': 'SlainteGov-NIS2',
        'name': 'EU NIS2 Directive & Continuous Compliance Auditor',
        'fleet': 'governance',
        'squad': 'gov',
        'squad_name': 'SlainteGov — Privacy, GDPR & Regulatory Governance',
        'icon': 'fas fa-clipboard-check',
        'color': 'primary',
        'summary': (
            'Audits hospital appliance operational controls against EU Directive 2022/2555 (NIS2) Article 21, verifying '
            'SIEM dispatch readiness, supply-chain pin integrity, and cryptographic Provenance sign-offs.'
        ),
        'mcp_tools': ['NIS2 Article 21 Control Auditor', 'SIEM Dispatch Verifier', 'Provenance Ledger Inspector'],
        'embedded_in': ['Dedicated NIS2 Page (/agents/nis2_compliance)', 'Security Settings', 'Compliance Certificate'],
        'guardrail_label': 'NIS2 Regulatory Posture',
        'guardrail_options': ['Continuous Automated Control Verification (Strict)', 'Weekly Attestation Snapshot Only'],
        'default_guardrail': 'Continuous Automated Control Verification (Strict)',
    },
]


def get_agent_by_id(agent_id: str) -> Optional[Dict[str, Any]]:
    if not agent_id:
        return None
    norm = agent_id.strip().lower()
    alias_map = {
        'discharge_readiness': 'discharge_transfer',
        'discharge': 'discharge_transfer',
        'ems': 'ems_prealert',
        'ems_alert': 'ems_prealert',
        'cve': 'cve_vulnerability',
        'vuln': 'cve_vulnerability',
        'gdpr': 'gdpr_privacy',
        'privacy': 'gdpr_privacy',
        'audit': 'immutable_audit',
        'immutability': 'immutable_audit',
        'triage': 'acuity_triage',
        'news2': 'acuity_triage',
        'fhir': 'fhir_conformance',
        'conformance': 'fhir_conformance',
        'summariser': 'patient_summariser',
        'summary': 'patient_summariser',
        'scribe': 'ambient_scribe',
        'ambient': 'ambient_scribe',
        'rxguard': 'medication_safety',
        'rx_guard': 'medication_safety',
    }
    norm = alias_map.get(norm, norm)
    for agent in AGENTS_CATALOG:
        if agent['id'] == norm or agent['slug'] == norm or agent['number'] == norm:
            return agent
    return None


def get_all_agents_with_settings(db_module, default_model: str = 'ollama/k9/lime:latest') -> List[Dict[str, Any]]:
    """Return all 11 agents enriched with their persisted per-agent settings from SQLite."""
    enriched = []
    for agent in AGENTS_CATALOG:
        raw = ''
        try:
            raw = db_module.get_system_setting(f"agent_cfg:{agent['id']}", '')
        except Exception:
            raw = ''
        cfg = {}
        if raw:
            try:
                cfg = json.loads(raw)
            except Exception:
                cfg = {}
        item = dict(agent)
        item['enabled'] = cfg.get('enabled', True)
        item['assigned_model'] = cfg.get('model') or default_model
        item['active_guardrail'] = cfg.get('guardrail') or agent['default_guardrail']
        item['updated_at'] = cfg.get('updated_at', 'Default Policy')
        enriched.append(item)
    return enriched


def save_agent_settings(db_module, agent_id: str, enabled: bool, model: str, guardrail: str) -> Dict[str, Any]:
    agent = get_agent_by_id(agent_id)
    canonical_id = agent['id'] if agent else agent_id
    payload = {
        'enabled': bool(enabled),
        'model': (model or '').strip(),
        'guardrail': (guardrail or '').strip(),
        'updated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
    }
    db_module.set_system_setting(f"agent_cfg:{canonical_id}", json.dumps(payload))
    return payload


def get_agent_instance(agent_id: str):
    """Instantiate the concrete agent class for a given agent identifier."""
    ag = get_agent_by_id(agent_id)
    if not ag:
        return None
    cid = ag['id']
    if cid == 'bola_redteam':
        from agents.governance.bola_redteam import BolaRedTeamAgent
        return BolaRedTeamAgent()
    elif cid == 'fhir_conformance':
        from agents.governance.fhir_conformance import FhirConformanceAgent
        return FhirConformanceAgent()
    elif cid == 'cve_vulnerability':
        from agents.governance.cve_vulnerability import CveVulnerabilityAgent
        return CveVulnerabilityAgent()
    elif cid == 'gdpr_privacy':
        from agents.governance.gdpr_privacy import GdprPrivacyAgent
        return GdprPrivacyAgent()
    elif cid == 'immutable_audit':
        from agents.governance.immutable_audit import ImmutableAuditAgent
        return ImmutableAuditAgent()
    elif cid == 'multimodal_ingest':
        from agents.clinical.multimodal_ingest import MultimodalIngestAgent
        return MultimodalIngestAgent()
    elif cid == 'patient_summariser':
        from agents.clinical.patient_summariser import PatientSummariserAgent
        return PatientSummariserAgent()
    elif cid == 'medication_safety':
        from agents.clinical.medication_safety import MedicationSafetyAgent
        return MedicationSafetyAgent()
    elif cid == 'acuity_triage':
        from agents.clinical.acuity_triage import AcuityTriageAgent
        return AcuityTriageAgent()
    elif cid == 'ambient_scribe':
        from agents.clinical.ambient_scribe import AmbientScribeAgent
        return AmbientScribeAgent()
    elif cid == 'clinical_coding':
        from agents.clinical.clinical_coding import ClinicalCodingAgent
        return ClinicalCodingAgent()
    elif cid == 'clinic_onboarding':
        from agents.governance.onboarding import ClinicOnboardingAgent
        return ClinicOnboardingAgent()
    elif cid == 'discharge_transfer':
        from agents.clinical.discharge_transfer import DischargeTransferAgent
        return DischargeTransferAgent()
    elif cid == 'ems_prealert':
        from agents.clinical.ems_prealert import EmsPrealertAgent
        return EmsPrealertAgent()
    elif cid == 'chronic_surveillance':
        from agents.clinical.chronic_surveillance import ChronicSurveillanceAgent
        return ChronicSurveillanceAgent()
    elif cid == 'nis2_compliance':
        from agents.governance.nis2_compliance import Nis2ComplianceAgent
        return Nis2ComplianceAgent()
    return None

