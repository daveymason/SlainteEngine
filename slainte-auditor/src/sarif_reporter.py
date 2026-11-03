"""Stage 4: Multi-Identity Differential Ground-Truth Oracle & SARIF v2.1.0 Exporter."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from .redteam_bola_agent import SecurityFinding
from .terminology_verifier import TerminologyFinding


def build_sarif_report(
    security_findings: List[SecurityFinding],
    terminology_findings: List[TerminologyFinding],
    target_url: str = "http://slainte-fhir:8082",
) -> Dict[str, Any]:
    """
    Compiles confirmed security (BOLA/CORS/Validator) and semantic terminology findings
    into a standard SARIF v2.1.0 JSON report for CI/CD and dashboard ingestion.
    """
    rules_map: Dict[str, Dict[str, Any]] = {}
    results: List[Dict[str, Any]] = []

    for sf in security_findings:
        if sf.rule_id not in rules_map:
            rules_map[sf.rule_id] = {
                "id": sf.rule_id,
                "name": sf.vector_id,
                "shortDescription": {"text": f"{sf.owasp_id} / {sf.cwe_id}: {sf.rule_id}"},
                "fullDescription": {"text": sf.description},
                "properties": {
                    "tags": ["security", "fhir-r4", sf.cwe_id, sf.owasp_id],
                    "security-severity": "9.1" if sf.severity == "critical" else "7.5",
                },
            }
        results.append(
            {
                "ruleId": sf.rule_id,
                "level": "error" if sf.severity in ("critical", "high") else "warning",
                "message": {
                    "text": (
                        f"[{sf.severity.upper()}] {sf.description} "
                        f"(Reproduce: `{sf.reproduction_curl}`)"
                    )
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": f"{target_url}{sf.endpoint}"}
                        }
                    }
                ],
                "properties": {
                    "attacker_identity": sf.attacker_identity,
                    "victim_resource": sf.victim_resource_id,
                    "cwe": sf.cwe_id,
                    "owasp": sf.owasp_id,
                },
            }
        )

    for tf in terminology_findings:
        if tf.rule_id not in rules_map:
            rules_map[tf.rule_id] = {
                "id": tf.rule_id,
                "name": tf.owasp_category,
                "shortDescription": {"text": f"FHIR R4 Semantic & Ontology Rule {tf.rule_id}"},
                "fullDescription": {"text": tf.message},
                "properties": {
                    "tags": ["clinical-interoperability", "snomed-ct", "loinc", "ucum", tf.cwe_id]
                },
            }
        results.append(
            {
                "ruleId": tf.rule_id,
                "level": "error" if tf.severity == "error" else "warning",
                "message": {"text": tf.message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": f"{tf.resource_type}/{tf.resource_id}"}
                        }
                    }
                ],
                "properties": {
                    "resource_type": tf.resource_type,
                    "resource_id": tf.resource_id,
                },
            }
        )

    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "SlainteFHIR-Auditor",
                        "version": "1.0.0",
                        "informationUri": "https://hl7.org/fhir/R4/security.html",
                        "rules": list(rules_map.values()),
                    }
                },
                "invocations": [
                    {
                        "executionSuccessful": True,
                        "endTimeUtc": datetime.now(timezone.utc).isoformat(),
                    }
                ],
                "results": results,
            }
        ],
    }


def save_sarif_report(report: Dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return output_path
