# SlainteFHIR Auditor: Autonomous Red-Team & Semantic FHIR R4 Verifier

`slainte-auditor` is the autonomous security and clinical interoperability verification deliverable for the **Slainte-Engine** stack. Built for OpenHands (`CodeActAgent`) and Model Context Protocol (`FastMCP`), it continuously audits HL7 FHIR R4 servers (`slainte-fhir:8082`) across two dimensions:

1. **Semantic & Terminology Conformance Verification:**
   - Audits ingested FHIR R4 Bundles against **SNOMED CT**, **LOINC**, strict **UCUM** units (`mm[Hg]`, `/min`, `Cel`), and Irish **GMS / IHI** identifier systems.
   - Detects cross-service schema drift (e.g., OID mismatches between `slainte-scan-mcp` and `slainte-fhir`), silent fallback codes (`404684003`), and clinical contradictions between free-text triage notes, NEWS2/MTS scores, and `AllergyIntolerance` / `MedicationRequest` pairs.

2. **Autonomous Multi-Identity BOLA & Graph-Traversal Red-Teaming:**
   - **Stage 1 (`src/conformance_filter.py`):** Enforces RFC-1918 / loopback sandbox pinning and `CapabilityStatement` reachability pruning against `CompartmentDefinition/Patient`.
   - **Stage 2 (`src/terminology_verifier.py`):** Deterministic + LLM-assisted clinical coding and ontology verifier.
   - **Stage 3 (`src/redteam_bola_agent.py`):** Stateful multi-identity BOLA penetration tester with **Dual-Phase Reflection** (*Intra-Reflection* for `400/422 OperationOutcome` syntax repair; *Inter-Reflection* after $K=3$ consecutive `403 Forbidden` blocks) probing 6 FHIR R4 attack vectors.
   - **Stage 4 (`src/sarif_reporter.py`):** Multi-Identity Differential Ground-Truth Oracle exporting findings to **SARIF v2.1.0** (`data/audit_reports/slaintefhir-audit.sarif.json`) and HL7 FHIR `OperationOutcome` resources.

## Quickstart

```bash
# Run standalone audit suite against local SlainteFHIR (:8082) or offline fixtures
python3 slainte-auditor/auditor_runner.py --once

# Run unit & integration tests
pytest slainte-auditor/tests/
```
