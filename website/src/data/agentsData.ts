export type AgentSquad = 'SlainteShield Security' | 'SlainteGov Governance' | 'SlainteClinical Care';

export interface AgentCapability {
  title: string;
  description: string;
  guardrailChip: string;
  iconKey:
    | 'security'
    | 'verified'
    | 'bug'
    | 'privacy'
    | 'factCheck'
    | 'sync'
    | 'summarize'
    | 'medication'
    | 'monitorHeart'
    | 'mic'
    | 'analytics';
}

export interface AgentSpecRow {
  parameter: string;
  deterministicMechanism: string;
  fhirBinding: string;
  standardAlignment: string;
}

export interface AgentRecord {
  slug: string; // SEO slug at /health-tech-agents/<slug>/
  name: string;
  codeName: string;
  squad: AgentSquad;
  squadColor: 'error' | 'warning' | 'primary';
  iconKey: AgentCapability['iconKey'];
  seoTitle: string;
  seoDescription: string;
  heroSummary: string;
  fastMcpBadges: string[];
  capabilities: [AgentCapability, AgentCapability, AgentCapability];
  verticalUseCase: {
    eyebrow: string;
    headline: string;
    scenario: string;
    outcomeMetric: string;
    verticalTitle: string;
    verticalHref: string;
  };
  technicalSpecs: AgentSpecRow[];
}

export const HEALTH_TECH_AGENTS: AgentRecord[] = [
  {
    slug: 'bola-authorization-red-team-agent',
    name: 'BOLA & Role-Boundary Red-Team Agent',
    codeName: 'SlainteShield-BOLA',
    squad: 'SlainteShield Security',
    squadColor: 'error',
    iconKey: 'security',
    seoTitle: 'BOLA & Role-Boundary Healthcare API Red-Team Agent | SlainteTech',
    seoDescription:
      'Autonomous OWASP API1:2023 Broken Object Level Authorization (BOLA) red-team verifier for HL7 FHIR R4 patient compartments and clinical role boundaries.',
    heroSummary:
      'Continuously probes HL7 FHIR R4 endpoints across victim/attacker patient pairs and clinical role boundaries to detect OWASP API1:2023 Broken Object Level Authorization leaks before external attackers do.',
    fastMcpBadges: ['OWASP API1:2023', 'CompartmentDefinition/Patient', 'RFC 1918 Sandbox Guard'],
    capabilities: [
      {
        title: 'CompartmentDefinition Surface Pruning',
        description:
          'Reads live /fhir/r4/metadata CapabilityStatements and prunes non-patient metadata endpoints, concentrating probes strictly on clinical compartment resources.',
        guardrailChip: '58.1% Surface Reduction',
        iconKey: 'security',
      },
      {
        title: 'Dual-Phase Reflection Probing',
        description:
          'Samples isolated Victim and Attacker compartments, records HTTP status/digest pairs in SharedAuditMemory, and verifies zero unauthorized PHI cross-reads.',
        guardrailChip: 'Deterministic AuthZ Diff',
        iconKey: 'verified',
      },
      {
        title: 'RFC 1918 Loopback & Sandbox Lock',
        description:
          'Hardcoded network guardrail refuses execution against non-RFC-1918 public clinical endpoints unless explicitly allowlisted in air-gapped staging.',
        guardrailChip: 'Zero Production Disruption',
        iconKey: 'factCheck',
      },
    ],
    verticalUseCase: {
      eyebrow: 'Verified Vertical Use Case — Elite Sports Medicine',
      headline: 'Preventing Cross-Roster Medical Chart Leaks in Professional Clubs',
      scenario:
        'When physiotherapy, coaching, and club doctors share an athlete readiness platform, SlainteShield-BOLA continuously verifies that squad role tokens cannot query restricted psychiatric, cardiac, or TUE FHIR compartments belonging to other athletes.',
      outcomeMetric: '0 Cross-Patient Compartment Leaks Across 8 Clinical Resource Types',
      verticalTitle: 'For Elite Sports Clubs & Federations',
      verticalHref: '/verticals/sports-medicine/',
    },
    technicalSpecs: [
      {
        parameter: 'Target Surface',
        deterministicMechanism: 'CapabilityStatement parser + CompartmentDefinition/Patient filter',
        fhirBinding: 'Patient, Observation, Condition, MedicationRequest, AllergyIntolerance, DocumentReference',
        standardAlignment: 'OWASP API Security Top 10 (API1:2023)',
      },
      {
        parameter: 'Safety Boundary',
        deterministicMechanism: 'RFC 1918 / localhost IP validation prior to socket dispatch',
        fhirBinding: 'GET /fhir/r4/metadata',
        standardAlignment: 'EU NIS2 Directive Art. 21 Security Testing',
      },
      {
        parameter: 'Audit Output',
        deterministicMechanism: 'Structured telemetry JSON + CISO Compliance Certificate digest',
        fhirBinding: 'AuditEvent & SharedAuditMemory',
        standardAlignment: 'CWE-639 / CWE-863 Verification',
      },
    ],
  },
  {
    slug: 'fhir-r4-conformance-terminology-agent',
    name: 'FHIR R4 Conformance & Terminology Agent',
    codeName: 'SlainteShield-FHIR',
    squad: 'SlainteShield Security',
    squadColor: 'error',
    iconKey: 'verified',
    seoTitle: 'HL7 FHIR R4 Conformance, SNOMED, LOINC & UCUM Agent | SlainteTech',
    seoDescription:
      'Deterministic HL7 FHIR R4 schema, SNOMED-CT, LOINC, UCUM unit, and Irish GMS OID conformance verifier with OASIS SARIF v2.1.0 reporting.',
    heroSummary:
      'Audits clinical bundles and micro-EHR stores for unmapped SNOMED-CT diagnoses, missing LOINC observation codes, non-standard UCUM dosage units, and Irish GMS identifier OID drift.',
    fastMcpBadges: ['HL7 FHIR R4 $validate', 'SNOMED-CT / LOINC / UCUM', 'OASIS SARIF v2.1.0'],
    capabilities: [
      {
        title: 'Terminology & UCUM Unit Verification',
        description:
          'Validates that every vital sign, laboratory result, and prescription carries canonical LOINC/SNOMED URIs and machine-safe UCUM units (mg, mL, mmol/L).',
        guardrailChip: 'Strict UCUM Gate',
        iconKey: 'verified',
      },
      {
        title: 'Irish GMS & National Identifier Binding',
        description:
          'Checks Patient.identifier systems against the Irish GMS OID (urn:oid:1.3.6.1.4.1.54392.5.2690.42.80) to prevent orphaned reimbursement records.',
        guardrailChip: 'HSE HIQA Interop Ready',
        iconKey: 'factCheck',
      },
      {
        title: 'CI/CD OASIS SARIF v2.1.0 Export',
        description:
          'Serializes every schema or terminology defect into standard OASIS SARIF v2.1.0 reports consumable directly by GitHub Code Scanning and hospital QA pipelines.',
        guardrailChip: 'SARIF v2.1.0 Native',
        iconKey: 'analytics',
      },
    ],
    verticalUseCase: {
      eyebrow: 'Verified Vertical Use Case — Clinical & Community Pharmacies',
      headline: 'Eliminating Ambiguous Dosage Units & Unverified GMS Identifiers Before Dispensing',
      scenario:
        'Before prescriptions enter the pharmacist verification queue or monthly HSE PCRS claim batch, SlainteShield-FHIR flags non-UCUM free-text dose strings and missing GMS identifier systems.',
      outcomeMetric: '100% Schema & Identifier Validation Prior to HSE PCRS Batch Export',
      verticalTitle: 'For Clinical & Community Pharmacies',
      verticalHref: '/verticals/pharmacy/',
    },
    technicalSpecs: [
      {
        parameter: 'Code System Checks',
        deterministicMechanism: 'Deterministic URI & code-presence ruleset in terminology_verifier.py',
        fhirBinding: 'Observation.code, Condition.code, MedicationRequest.medicationCodeableConcept',
        standardAlignment: 'HL7 FHIR R4.0.1 & HIQA eHealth Standards',
      },
      {
        parameter: 'Unit Integrity',
        deterministicMechanism: 'UCUM system URI (http://unitsofmeasure.org) & unit token verifier',
        fhirBinding: 'Observation.valueQuantity, Dosage.doseAndRate',
        standardAlignment: 'ISO 11240 / UCUM Clinical Safety',
      },
      {
        parameter: 'Machine Report',
        deterministicMechanism: 'Deterministic SARIF v2.1.0 generator (sarif_reporter.py)',
        fhirBinding: 'OperationOutcome / Bundle.$validate',
        standardAlignment: 'OASIS SARIF v2.1.0',
      },
    ],
  },
  {
    slug: 'healthcare-cve-vulnerability-agent',
    name: 'Healthcare Supply-Chain & CVE Vulnerability Agent',
    codeName: 'SlainteShield-CVE',
    squad: 'SlainteShield Security',
    squadColor: 'error',
    iconKey: 'bug',
    seoTitle: 'Healthcare Software Supply-Chain, CSP & CVE Audit Agent | SlainteTech',
    seoDescription:
      'Continuous dependency pinning, Subresource Integrity (SRI sha384), Content-Security-Policy, and rate-limiter posture auditing for clinical web platforms.',
    heroSummary:
      'Continuously inspects Python package pins, Subresource Integrity (SRI sha384) cryptographic hashes on browser assets, Content-Security-Policy headers, and SQLite multi-worker rate-limiting.',
    fastMcpBadges: ['Exact == Dependency Pins', 'SRI sha384 Verified', 'CSP & SameSite=Lax'],
    capabilities: [
      {
        title: 'Deterministic Dependency Pin Audit',
        description:
          'Parses production manifests to verify exact version pinning (==), preventing unreviewed transitive package drift across clinical container builds.',
        guardrailChip: 'Zero Unpinned Packages',
        iconKey: 'bug',
      },
      {
        title: 'Cryptographic SRI & Browser Hardening',
        description:
          'Verifies sha384 Subresource Integrity hashes on external scripts/stylesheets alongside Content-Security-Policy, X-Frame-Options, and HttpOnly session flags.',
        guardrailChip: 'SRI sha384 Enforced',
        iconKey: 'security',
      },
      {
        title: 'Brute-Force & Rate-Limit Storage Check',
        description:
          'Confirms multi-worker SQLite rate-limit storage and progressive 15-minute account lockouts after 5 failed authentication attempts.',
        guardrailChip: 'Shared Worker Lockout',
        iconKey: 'verified',
      },
    ],
    verticalUseCase: {
      eyebrow: 'Verified Vertical Use Case — Astronaut & Aerospace Medicine',
      headline: 'Guaranteeing Zero Supply-Chain Drift in Air-Gapped Orbital Medical Bays',
      scenario:
        'Before sealing an offline spacecraft or submarine medical appliance running local 3B models, SlainteShield-CVE verifies that every Python dependency is deterministically pinned and every UI asset matches its cryptographic hash.',
      outcomeMetric: '100% Deterministic Build & Cryptographic Asset Integrity Offline',
      verticalTitle: 'For Astronaut & Aerospace Medicine',
      verticalHref: '/verticals/astronaut-health/',
    },
    technicalSpecs: [
      {
        parameter: 'Supply-Chain Check',
        deterministicMechanism: 'Manifest parser auditing exact == version specifiers',
        fhirBinding: 'Appliance Container Runtime',
        standardAlignment: 'EU NIS2 Supply-Chain Security (Art. 21(2)(d))',
      },
      {
        parameter: 'Transport & DOM Defense',
        deterministicMechanism: 'CSP header + HTML template sha384 integrity attribute scanner',
        fhirBinding: 'SMART-on-FHIR & Clinical UI Shell',
        standardAlignment: 'OWASP ASVS v4.0 Level 2',
      },
      {
        parameter: 'Auth Abuse Control',
        deterministicMechanism: 'Centralized SQLite rate-limit backend + 5-strike lockout verifier',
        fhirBinding: '/login, /smart/token, /auth/oidc/callback',
        standardAlignment: 'ISO/IEC 27001:2022 A.8.9',
      },
    ],
  },
  {
    slug: 'gdpr-clinical-privacy-deidentification-agent',
    name: 'GDPR Art. 9 Clinical Privacy & De-Identification Agent',
    codeName: 'SlainteGov-GDPR',
    squad: 'SlainteGov Governance',
    squadColor: 'warning',
    iconKey: 'privacy',
    seoTitle: 'GDPR Art. 9 Healthcare Privacy, PII Redaction & Break-the-Glass Agent | SlainteTech',
    seoDescription:
      'Enforces EU GDPR Article 9 data minimisation, strips patient PII prior to LLM inference, pseudonymises logs with salted SHA-256, and audits Break-the-Glass access.',
    heroSummary:
      'Enforces EU GDPR Article 9 special-category health data minimisation by stripping direct identifiers before cloud AI calls, salting log subject IDs, and governing 60-minute Break-the-Glass emergency overrides.',
    fastMcpBadges: ['EU GDPR Art. 9 & 32', 'Live PII Redaction Gate', '60m Break-the-Glass'],
    capabilities: [
      {
        title: 'Pre-Inference FHIR PII Stripping',
        description:
          'Removes names, street addresses, telecom numbers, GMS identifiers, and reduces birth dates to birth year before assembling external LLM prompts.',
        guardrailChip: 'AI_DEIDENTIFY Gate',
        iconKey: 'privacy',
      },
      {
        title: 'Salted SHA-256 Subject Pseudonymisation',
        description:
          'Replaces raw patient identifiers in application and AI exchange logs with salted cryptographic digests verified against LOG_HASH_SALT.',
        guardrailChip: 'Zero Raw PHI in Logs',
        iconKey: 'security',
      },
      {
        title: 'Audited Break-the-Glass Vital-Interest Grants',
        description:
          'Provides time-boxed 60-minute GDPR Art. 9(2)(c) emergency access overrides backed by append-only SQLite triggers and instant HMAC-SHA256 SIEM alerts.',
        guardrailChip: 'Immutable Override Ledger',
        iconKey: 'factCheck',
      },
    ],
    verticalUseCase: {
      eyebrow: 'Verified Vertical Use Case — Psychiatry & Mental Health',
      headline: 'Protecting Highly Sensitive Psychiatric Notes While Supporting Crisis Care',
      scenario:
        'Community mental health records carry extreme confidentiality sensitivity. SlainteGov-GDPR strips all direct patient identifiers before consultation summarisation and requires a justified, SIEM-alerted Break-the-Glass grant for out-of-hours crisis access.',
      outcomeMetric: '100% Direct-Identifier Redaction on External AI Contexts',
      verticalTitle: 'For Psychiatrists & Mental Health',
      verticalHref: '/verticals/psychiatry/',
    },
    technicalSpecs: [
      {
        parameter: 'Context Redaction',
        deterministicMechanism: 'Deterministic field scrubber in ai/context.py prior to provider dispatch',
        fhirBinding: 'Patient.name, Patient.address, Patient.telecom, Patient.identifier, Patient.birthDate',
        standardAlignment: 'EU GDPR Art. 5(1)(c) & Art. 9',
      },
      {
        parameter: 'Cloud BAA Gate',
        deterministicMechanism: 'Blocks non-local PHI transmission unless AI_ALLOW_REAL_PHI=true',
        fhirBinding: 'All LLM Prompt Payloads',
        standardAlignment: 'EU GDPR Art. 28 Processor Governance',
      },
      {
        parameter: 'Emergency Override',
        deterministicMechanism: 'Append-only break_glass_grants SQLite table + SIEM webhook',
        fhirBinding: 'Patient Compartment Emergency Access',
        standardAlignment: 'GDPR Art. 9(2)(c) Vital Interests',
      },
    ],
  },
  {
    slug: 'immutable-clinical-ai-audit-agent',
    name: 'Immutable Clinical & AI Audit Ledger Agent',
    codeName: 'SlainteGov-Audit',
    squad: 'SlainteGov Governance',
    squadColor: 'warning',
    iconKey: 'factCheck',
    seoTitle: 'Immutable Healthcare & EU AI Act Audit Trail Agent | SlainteTech',
    seoDescription:
      'Tamper-evident SQLite kernel triggers, SHA-256 FHIR Provenance sign-off, HMAC SIEM webhooks, and printable NIS2 / EU AI Act compliance certificates.',
    heroSummary:
      'Guarantees non-repudiation across every clinical write and AI prompt exchange using database-level BEFORE UPDATE/DELETE rejection triggers, SHA-256 FHIR Provenance hashes, and signed compliance snapshots.',
    fastMcpBadges: ['Append-Only SQL Triggers', 'SHA-256 FHIR Provenance', 'EU AI Act Art. 12'],
    capabilities: [
      {
        title: 'Live Tamper-Rejection Savepoint Verification',
        description:
          'Executes non-destructive SQLite savepoint probes attempting UPDATE and DELETE mutations against audit_log and ai_exchange to prove kernel triggers reject tampering.',
        guardrailChip: 'SQLITE_ABORT Verified',
        iconKey: 'factCheck',
      },
      {
        title: 'Cryptographic Clinician Provenance Sign-Off',
        description:
          'Binds IMC/PSI/NMBI practitioner registration IDs and SHA-256 bundle hashes into HL7 FHIR R4 Provenance resources on clinical sign-off.',
        guardrailChip: 'SHA-256 Bundle Hash',
        iconKey: 'verified',
      },
      {
        title: 'SIEM Webhooks & Executive Attestation',
        description:
          'Dispatches HMAC-SHA256 signed security events to hospital SOCs and generates printable NIS2, EU AI Act, GDPR, and ISO 27001 attestation certificates.',
        guardrailChip: 'X-Slainte-Signature HMAC',
        iconKey: 'analytics',
      },
    ],
    verticalUseCase: {
      eyebrow: 'Verified Vertical Use Case — Emergency Departments',
      headline: 'Defensible Medico-Legal Handover & AI Traceability in High-Acuity Resuscitation',
      scenario:
        'During rapid shift changes in overcrowded Emergency Departments, every triage score, medication override, bedside AI summary, and consultant Provenance signature is locked into an append-only ledger.',
      outcomeMetric: 'Zero Mutable Audit Rows Across Clinical & AI Exchange Tables',
      verticalTitle: 'For Emergency Departments',
      verticalHref: '/verticals/emergency-departments/',
    },
    technicalSpecs: [
      {
        parameter: 'Immutability Mechanism',
        deterministicMechanism: 'SQLite BEFORE UPDATE / BEFORE DELETE RAISE(ABORT) triggers on 3 audit tables',
        fhirBinding: 'audit_log, ai_exchange, break_glass_grants',
        standardAlignment: 'EU AI Act Art. 12 Record-Keeping',
      },
      {
        parameter: 'Clinical Non-Repudiation',
        deterministicMechanism: 'Canonical JSON SHA-256 digest stored in Provenance.signature',
        fhirBinding: 'HL7 FHIR R4 Provenance',
        standardAlignment: 'HIQA Information Management Standards',
      },
      {
        parameter: 'SOC Integration',
        deterministicMechanism: 'HMAC-SHA256 webhook dispatcher + signed JSON snapshot export',
        fhirBinding: 'GET /agents/audit/snapshot & /agents/compliance-certificate',
        standardAlignment: 'EU NIS2 Art. 23 Incident Reporting',
      },
    ],
  },
  {
    slug: 'multimodal-hl7v2-fhir-ingestion-agent',
    name: 'Multimodal & HL7v2-to-FHIR R4 Ingestion Agent',
    codeName: 'SlainteEngine-Ingest',
    squad: 'SlainteClinical Care',
    squadColor: 'primary',
    iconKey: 'sync',
    seoTitle: 'HL7v2 ADT/ORU & Multimodal OCR to FHIR R4 Ingestion Agent | SlainteTech',
    seoDescription:
      'Converts legacy hospital HL7v2 pipe-hat messages (ADT, ORU, RDE), CSV cohorts, PDFs, and handwritten triage notes into validated HL7 FHIR R4 bundles.',
    heroSummary:
      'Bridges legacy hospital PAS/LIS interfaces and paper workflows by translating HL7v2 pipe-hat streams (ADT^A01, ORU^R01, RDE^O11), CSV batches, PDFs, and clinical images into deduplicated HL7 FHIR R4 bundles.',
    fastMcpBadges: ['HL7v2 MSH|PID|OBX|RXE', 'PDF & Image OCR Gate', 'Irish GMS Deduplication'],
    capabilities: [
      {
        title: 'Deterministic HL7v2 Pipe-Hat Translator',
        description:
          'Parses MSH, PID, PV1, AL1, DG1, OBR, OBX, and RXE segments directly into FHIR R4 Patient, Condition, AllergyIntolerance, Observation, and MedicationRequest resources.',
        guardrailChip: 'Zero Interface Engine Tax',
        iconKey: 'sync',
      },
      {
        title: 'Multimodal CSV, PDF & Field Note Intake',
        description:
          'Extracts vitals, presenting complaints, and allergies from structured CSVs, referral PDFs, and photographed triage sheets with FastMCP validation.',
        guardrailChip: '5-Stage Harmonization',
        iconKey: 'factCheck',
      },
      {
        title: 'GMS Identifier Deduplication',
        description:
          'Matches incoming Irish GMS identifiers against existing Patient records via find_patient_id_by_gms so repeat admissions update the longitudinal chart rather than duplicating it.',
        guardrailChip: 'Single Longitudinal Record',
        iconKey: 'verified',
      },
    ],
    verticalUseCase: {
      eyebrow: 'Verified Vertical Use Case — Ambulance & Paramedic Services',
      headline: 'Turning Roadside Paramedic Notes & Legacy Hospital Feeds into Live FHIR Charts',
      scenario:
        'Paramedics transmitting rapid pre-hospital ePCR observations or hospitals streaming legacy HL7v2 ADT/ORU messages land in SlainteFHIR within milliseconds, pre-scored for Manchester Triage and deduplicated by GMS ID.',
      outcomeMetric: '<50ms Deterministic HL7v2-to-FHIR R4 Bundle Translation',
      verticalTitle: 'For Ambulance & Paramedic Services',
      verticalHref: '/verticals/ambulance-ems/',
    },
    technicalSpecs: [
      {
        parameter: 'Legacy Hospital Feeds',
        deterministicMechanism: 'Native Python HL7v2 v2.3–v2.5 segment parser (/enterprise/hl7v2/ingest)',
        fhirBinding: 'Bundle (transaction/collection) -> Patient, Encounter, Observation, AllergyIntolerance',
        standardAlignment: 'HL7 v2.x to HL7 FHIR R4 Mapping',
      },
      {
        parameter: 'Multimodal Intake',
        deterministicMechanism: 'CSV/PDF/Image parser + deterministic SNOMED complaint resolver',
        fhirBinding: 'POST /fhir/intake/manual & /fhir/intake/upload',
        standardAlignment: 'LOINC Vital Signs & SNOMED-CT',
      },
      {
        parameter: 'Identity Resolution',
        deterministicMechanism: 'Exact GMS OID lookup before Patient resource creation',
        fhirBinding: 'Patient.identifier (urn:oid:1.3.6.1.4.1.54392.5.2690.42.80)',
        standardAlignment: 'HIQA National Health Identifier Guidance',
      },
    ],
  },
  {
    slug: 'cited-patient-handover-summariser-agent',
    name: 'Cited Clinical Handover Summariser Agent',
    codeName: 'SlainteScribe-Brief',
    squad: 'SlainteClinical Care',
    squadColor: 'primary',
    iconKey: 'summarize',
    seoTitle: 'Cited HL7 FHIR R4 Clinical Handover Summariser Agent | SlainteTech',
    seoDescription:
      'Generates 4-bullet bedside shift-handover briefings citing exact HL7 FHIR R4 resource IDs and grounded in deterministic NEWS2 and drug-allergy checks.',
    heroSummary:
      'Synthesizes longitudinal patient charts into concise 4-bullet clinical shift handovers where every statement is anchored to explicit FHIR R4 resource types, deterministic NEWS2 scores, and verified allergy records.',
    fastMcpBadges: ['Mandatory [ResourceType] Citations', 'Allergies-First Context', 'Audit Logged'],
    capabilities: [
      {
        title: 'Allergies-First Token Curation',
        description:
          'Deterministic context curator guarantees AllergyIntolerance and active MedicationRequests survive even tight token ceilings before trimming older observations.',
        guardrailChip: 'Safety-Priority Curation',
        iconKey: 'summarize',
      },
      {
        title: 'Failure-Is-Never-Emptiness Guardrail',
        description:
          'If a FHIR search endpoint times out, the prompt explicitly marks that clinical section as unreadable rather than letting the model assume "none recorded".',
        guardrailChip: 'Anti-Hallucination Prompting',
        iconKey: 'verified',
      },
      {
        title: 'Deterministic Fallback & AI Exchange Logging',
        description:
          'Produces a structured 4-bullet clinical briefing even when offline and records prompt hashes, token counts, and model IDs in ai_exchange.',
        guardrailChip: '100% Uptime Handover',
        iconKey: 'factCheck',
      },
    ],
    verticalUseCase: {
      eyebrow: 'Verified Vertical Use Case — Emergency Departments',
      headline: 'Zero-Omission Consultant & Nursing Shift Handovers Under Time Pressure',
      scenario:
        'At 08:00 resuscitation handover, clinicians trigger SlainteScribe-Brief directly from the patient roster or chart to review presentation, 24h NEWS2 acuity, abnormal labs, and active drug-allergy alerts in 4 cited bullets.',
      outcomeMetric: '4-Bullet Cited Briefing Grounded in Live FHIR R4 Compartments',
      verticalTitle: 'For Emergency Departments',
      verticalHref: '/verticals/emergency-departments/',
    },
    technicalSpecs: [
      {
        parameter: 'Context Assembly',
        deterministicMechanism: 'Priority-ordered FHIR compartment curator (ai/context.py)',
        fhirBinding: 'Patient/$everything or parallel Observation/Condition/Allergy/Medication queries',
        standardAlignment: 'ISBAR / Clinical Handover Safety',
      },
      {
        parameter: 'Safety Grounding',
        deterministicMechanism: 'Pre-computed RCP NEWS2 + check_drug_allergy_contraindications injected verbatim',
        fhirBinding: '[Patient/id], [Condition], [Observation/vital-signs], [AllergyIntolerance]',
        standardAlignment: 'DCB0129 Clinical Risk Control',
      },
      {
        parameter: 'Sovereign Model Choice',
        deterministicMechanism: 'Switchable between local Ollama 3B models and BAA-gated frontier APIs',
        fhirBinding: '/settings/ai & POST /ai/summarise/<patient_id>',
        standardAlignment: 'EU AI Act Transparency & Traceability',
      },
    ],
  },
  {
    slug: 'pharmacotherapy-allergy-renal-safety-agent',
    name: '3-Tier Pharmacotherapy, Allergy & Renal Safety Agent',
    codeName: 'SlainteRx-Guard',
    squad: 'SlainteClinical Care',
    squadColor: 'primary',
    iconKey: 'medication',
    seoTitle: '3-Tier Drug-Allergy, High-Alert DDI & Renal eGFR Safety Agent | SlainteTech',
    seoDescription:
      '100% deterministic 3-tier clinical pharmacology safety gate screening drug-allergy cross-reactivity, ISMP high-alert drug interactions, and LOINC eGFR renal dosing.',
    heroSummary:
      'Intercepts unsafe prescriptions before FHIR persistence using a zero-hallucination 3-tier Python pharmacology engine covering Beta-Lactam/NSAID/Sulfa cross-reactivity, ISMP high-alert DDIs, and patient LOINC eGFR & Potassium labs.',
    fastMcpBadges: ['Tier 1: Allergy Cross-Reactivity', 'Tier 2: ISMP High-Alert DDI', 'Tier 3: Lab eGFR & K+ Gate'],
    capabilities: [
      {
        title: 'Tier 1: Cross-Reactivity Matrix',
        description:
          'Detects Penicillin-to-Amoxicillin/Cephalosporin, Aspirin/NSAID, and Sulfonamide cross-reactivity directly against active AllergyIntolerance records.',
        guardrailChip: 'Anaphylaxis Hard-Stop',
        iconKey: 'medication',
      },
      {
        title: 'Tier 2: ISMP High-Alert Drug-Drug Interactions',
        description:
          'Screens active regimens for life-threatening pairs including Clarithromycin + Statin (rhabdomyolysis), Warfarin + NSAID/Metronidazole, Opioid + Benzodiazepine, and ACEi + Spironolactone.',
        guardrailChip: 'High-Alert DDI Matrix',
        iconKey: 'security',
      },
      {
        title: 'Tier 3: Lab-Guided Renal eGFR & Potassium Gate',
        description:
          'Queries latest LOINC eGFR (33914-3) and Potassium (2823-3) Observations to block Metformin in severe renal impairment (eGFR < 30) and nephrotoxic NSAIDs when eGFR < 60.',
        guardrailChip: 'Live Lab-Aware Dosing',
        iconKey: 'verified',
      },
    ],
    verticalUseCase: {
      eyebrow: 'Verified Vertical Use Case — Dental Surgeons & DSOs',
      headline: 'Blocking Penicillin Anaphylaxis & Anticoagulant Bleeding Risks Chairside',
      scenario:
        'Before prescribing post-extraction Amoxicillin or Ibuprofen on the dental surgery chart, SlainteRx-Guard cross-checks the patient’s Penicillin allergy, Warfarin/Apixaban regimen, and baseline renal eGFR in under 5 milliseconds.',
      outcomeMetric: '3 Simultaneous Pharmacology Tiers Checked on Every Prescription & Voice Order',
      verticalTitle: 'For Dental Surgeons & DSOs',
      verticalHref: '/verticals/dentistry/',
    },
    technicalSpecs: [
      {
        parameter: 'Execution Engine',
        deterministicMechanism: '100% deterministic Python rule matrix (evaluate_clinical_pharmacology_3tier)',
        fhirBinding: 'AllergyIntolerance, MedicationRequest, Observation (LOINC 33914-3, 2823-3)',
        standardAlignment: 'ISMP High-Alert Medications & NICE CKD Guidance',
      },
      {
        parameter: 'Clinical Override Governance',
        deterministicMechanism: 'Blocks HTTP write unless prescriber RBAC role documents clinical justification',
        fhirBinding: 'POST /fhir/Medications/<id>/add & SIEM Webhook on High-Risk Override',
        standardAlignment: 'HIQA Medication Safety & DCB0160',
      },
      {
        parameter: 'Embedded Surfaces',
        deterministicMechanism: 'Runs inline on Patient Prescribing, Ambient Voice Scribe drafts, and Pharmacy Queue',
        fhirBinding: 'MedicationRequest.note & AuditEvent',
        standardAlignment: 'Zero-LLM-Math Safety Principle',
      },
    ],
  },
  {
    slug: 'manchester-triage-news2-acuity-agent',
    name: 'Manchester Triage & RCP NEWS2 Acuity Agent',
    codeName: 'SlainteDx-Triage',
    squad: 'SlainteClinical Care',
    squadColor: 'primary',
    iconKey: 'monitorHeart',
    seoTitle: 'Deterministic Manchester Triage (MTS) & RCP NEWS2 Agent | SlainteTech',
    seoDescription:
      'Zero-hallucination Manchester Triage System (Cat 1–5) priority assignment and Royal College of Physicians NEWS2 (0–20) physiological deterioration tracking.',
    heroSummary:
      'Computes deterministic Manchester Triage System categories (Cat 1 Immediate to Cat 5 Non-Urgent) and Royal College of Physicians NEWS2 scores (0–20) from LOINC vital signs — never delegating clinical arithmetic to LLM weights.',
    fastMcpBadges: ['MTS Cat 1–5 (0m–240m)', 'RCP NEWS2 (0–20)', '24h SVG Vital Sparklines'],
    capabilities: [
      {
        title: 'Royal College of Physicians NEWS2 Engine',
        description:
          'Scores respiratory rate, SpO2, systolic BP, heart rate, temperature, and consciousness/GCS against exact RCP physiological thresholds with automatic sepsis escalation at NEWS2 >= 7.',
        guardrailChip: 'Exact RCP Thresholds',
        iconKey: 'monitorHeart',
      },
      {
        title: 'Manchester Triage System (Cat 1–5) Queueing',
        description:
          'Combines vital-sign discriminators and high-risk presenting complaints to classify arrivals from Category 1 (0 min Immediate) to Category 5 (240 min).',
        guardrailChip: 'Sub-10ms Triage Math',
        iconKey: 'verified',
      },
      {
        title: '24-Hour Trajectory Sparklines & Live Refresh',
        description:
          'Generates bedside 24-hour physiological trend sparklines and triggers real-time HTMX NEWS2 card updates whenever fresh vitals are recorded.',
        guardrailChip: 'HX-Trigger Live Sync',
        iconKey: 'analytics',
      },
    ],
    verticalUseCase: {
      eyebrow: 'Verified Vertical Use Case — Ambulance & Paramedic Services',
      headline: 'Instant Pre-Hospital Acuity Pre-Alerts From Ruggedised Ambulance Tablets',
      scenario:
        'An Advanced Paramedic enters roadside BP 84/52, HR 135, SpO2 87%, and RR 30 on a tablet; SlainteDx-Triage immediately flags MTS Category 1 (0m Immediate) and NEWS2 High Clinical Risk before the ambulance reaches the ED bay.',
      outcomeMetric: '<10ms Deterministic MTS + NEWS2 Calculation With Zero Cloud Latency',
      verticalTitle: 'For Ambulance & Paramedic Services',
      verticalHref: '/verticals/ambulance-ems/',
    },
    technicalSpecs: [
      {
        parameter: 'Vital Sign Inputs',
        deterministicMechanism: 'LOINC-keyed Python physiological scorer (calculate_news2_score & calculate_mts_category)',
        fhirBinding: 'Observation (8480-6 SBP, 8867-4 HR, 9279-1 RR, 2708-6/59408-5 SpO2, 8310-5 Temp, 9269-2 GCS)',
        standardAlignment: 'Royal College of Physicians NEWS2 (2017/2023)',
      },
      {
        parameter: 'Escalation Tiers',
        deterministicMechanism: 'Low (0–4), Single-Parameter Red (3), Medium (5–6), High Sepsis/ICU Review (>=7)',
        fhirBinding: 'Encounter.priority & Observation',
        standardAlignment: 'HSE National Early Warning System (INEWS)',
      },
      {
        parameter: 'Field & Bedside UX',
        deterministicMechanism: 'Collapsible urgent-focus MTS accordions + coarse-pointer 44px touch controls',
        fhirBinding: 'GET /fhir/Triage & POST /fhir/VitalSigns/<id>/add',
        standardAlignment: 'WCAG 2.2 AA & Emergency Human Factors',
      },
    ],
  },
  {
    slug: 'ambient-clinical-voice-scribe-agent',
    name: 'Ambient Clinical Voice Scribe & Order Drafter Agent',
    codeName: 'SlainteScribe-Voice',
    squad: 'SlainteClinical Care',
    squadColor: 'primary',
    iconKey: 'mic',
    seoTitle: 'Ambient Clinical Voice Scribe & Safe FHIR R4 Order Drafter | SlainteTech',
    seoDescription:
      'Turns live clinician-patient consultations into structured SOAP DocumentReference notes, SNOMED conditions, and 3-Tier Rx-Guard pre-screened FHIR draft orders.',
    heroSummary:
      'Eliminates after-hours documentation by converting live consultation speech or uploaded audio into structured SOAP notes, SNOMED-CT/ICD-10-AM diagnoses, and draft prescriptions pre-screened by 3-Tier SlainteRx-Guard before clinician co-sign.',
    fastMcpBadges: ['Web Speech & Whisper ASR', 'Structured SOAP Note', 'Pre-Screened FHIR Orders'],
    capabilities: [
      {
        title: 'Structured SOAP & Vital Extraction',
        description:
          'Transforms consultation dialogue into Subjective, Objective, Assessment, and Plan sections while extracting mentioned BP, HR, SpO2, RR, and temperature readings into LOINC Observations.',
        guardrailChip: 'LOINC Vitals Extracted',
        iconKey: 'mic',
      },
      {
        title: 'Mandatory 3-Tier Rx-Guard Pre-Screening',
        description:
          'Every medication mentioned during dictation is automatically passed through SlainteRx-Guard so allergies, high-alert DDIs, and eGFR renal blocks surface before a single order is committed.',
        guardrailChip: 'Zero Unscreened Voice Orders',
        iconKey: 'medication',
      },
      {
        title: 'Human-in-the-Loop Co-Sign & Commit',
        description:
          'Ambient drafts never auto-mutate the legal medical record; a licensed prescriber reviews checkboxes and commits approved resources in one click.',
        guardrailChip: 'Mandatory Clinician Co-Sign',
        iconKey: 'verified',
      },
    ],
    verticalUseCase: {
      eyebrow: 'Verified Vertical Use Case — General Practitioners & Community Nursing',
      headline: 'Reclaiming 60% of Consultation Documentation Time in GP Clinics & Home Visits',
      scenario:
        'Whether consulting in a busy GP surgery or visiting a housebound chronic-disease patient on a tablet, SlainteScribe-Voice drafts the SOAP note, maps SNOMED/ICD-10 diagnoses, and flags Penicillin or renal dosing conflicts prior to sign-off.',
      outcomeMetric: '1-Click Commit of SOAP DocumentReference, SNOMED Conditions & Safe Rx',
      verticalTitle: 'For General Practitioners & Community Nursing',
      verticalHref: '/verticals/general-practice/',
    },
    technicalSpecs: [
      {
        parameter: 'Speech & Text Pipeline',
        deterministicMechanism: 'Browser Web Speech API (en-IE) / OpenAI Whisper ASR + structured clinical parser',
        fhirBinding: 'POST /enterprise/scribe/process',
        standardAlignment: 'EU GDPR Art. 9 & Local-First Option',
      },
      {
        parameter: 'Pre-Commit Safety Gate',
        deterministicMechanism: 'Inline invocation of evaluate_clinical_pharmacology_3tier on all draft orders',
        fhirBinding: 'Draft MedicationRequest + AllergyIntolerance + Observation (eGFR)',
        standardAlignment: 'EU AI Act Art. 14 Human Oversight',
      },
      {
        parameter: 'FHIR R4 Persistence',
        deterministicMechanism: 'Atomic commit of approved SOAP, Conditions, Vitals, and non-blocked Rx',
        fhirBinding: 'DocumentReference (11506-3), Condition, Observation, MedicationRequest',
        standardAlignment: 'HL7 FHIR R4 Clinical Document Architecture',
      },
    ],
  },
  {
    slug: 'autonomous-icd10-drg-clinical-coding-agent',
    name: 'Autonomous HIPE, ICD-10-AM & DRG Clinical Coding Agent',
    codeName: 'SlainteRev-Coding',
    squad: 'SlainteGov Governance',
    squadColor: 'warning',
    iconKey: 'analytics',
    seoTitle: 'Autonomous HIPE, ICD-10-AM & SNOMED DRG Clinical Coding Agent | SlainteTech',
    seoDescription:
      'Audits objective LOINC laboratory and vital observations against active FHIR Conditions to detect uncoded comorbidities and recover hospital DRG complexity reimbursement.',
    heroSummary:
      'Cross-examines objective laboratory biomarkers and vital signs (eGFR, HbA1c, Troponin, Lactate, SpO2, BP) against recorded diagnoses to surface uncoded ICD-10-AM / SNOMED-CT comorbidities with full LOINC observation citations.',
    fastMcpBadges: ['Irish HIPE / ABF Ready', 'Dual SNOMED + ICD-10-AM', 'Objective Lab Evidence'],
    capabilities: [
      {
        title: 'Objective Biomarker-to-Diagnosis Audit',
        description:
          'Evaluates LOINC labs and vitals (eGFR < 60 CKD, HbA1c >= 48 T2DM, Troponin > 50 myocardial injury, Lactate >= 2.0 hyperlactataemia, SpO2 <= 91% hypoxaemia) against active Conditions.',
        guardrailChip: 'Zero Upcoding Hallucination',
        iconKey: 'analytics',
      },
      {
        title: 'Irish HIPE DRG Complexity Uplift Estimation',
        description:
          'Quantifies estimated Activity-Based Funding (ABF) / HIPE DRG complexity reimbursement impact across uncoded secondary comorbidities for hospital finance review.',
        guardrailChip: 'Transparent CFO ROI',
        iconKey: 'factCheck',
      },
      {
        title: '1-Click Dual-Coded FHIR Condition Capture',
        description:
          'Writes clinician-approved Condition resources carrying both SNOMED-CT clinical codes and ICD-10-AM classification bindings alongside the citing Observation reference.',
        guardrailChip: 'SNOMED + ICD-10-AM Bound',
        iconKey: 'verified',
      },
    ],
    verticalUseCase: {
      eyebrow: 'Verified Vertical Use Case — Hospital & Chronic Disease Medicine',
      headline: 'Recovering Unbilled Secondary Comorbidities With Provable Laboratory Citations',
      scenario:
        'When an inpatient or CDM patient has an eGFR of 38 mL/min and HbA1c of 56 mmol/mol in laboratory Observations without corresponding CKD Stage 3 or Type 2 Diabetes codes on the problem list, SlainteRev-Coding surfaces the exact gap for 1-click capture.',
      outcomeMetric: 'Every Suggested ICD-10-AM Code Cites Its Exact LOINC Observation Evidence',
      verticalTitle: 'For General Practitioners & Primary Care',
      verticalHref: '/verticals/general-practice/',
    },
    technicalSpecs: [
      {
        parameter: 'Evidence Ruleset',
        deterministicMechanism: 'Deterministic LOINC threshold scanner (scan_patient_coding_gaps)',
        fhirBinding: 'Observation (33914-3 eGFR, 4548-4 HbA1c, 6598-7 Troponin, 2524-7 Lactate) vs. Condition',
        standardAlignment: 'Irish HPO HIPE & ICD-10-AM / ACHI Standards',
      },
      {
        parameter: 'Dual Coding Output',
        deterministicMechanism: 'Creates Condition with simultaneous http://snomed.info/sct & ICD-10-AM codings',
        fhirBinding: 'POST /enterprise/coding/apply/<patient_id>',
        standardAlignment: 'HIQA SNOMED-CT National Release & ABF Audit',
      },
      {
        parameter: 'Anti-Fraud Guardrail',
        deterministicMechanism: 'Never proposes a diagnosis code without a verifiable abnormal LOINC Observation',
        fhirBinding: 'Condition.note citing [Observation/id] value & timestamp',
        standardAlignment: 'Hospital Billing Audit Defensibility',
      },
    ],
  },
];

export function getAgentBySlug(slug: string): AgentRecord | undefined {
  return HEALTH_TECH_AGENTS.find((a) => a.slug === slug);
}
