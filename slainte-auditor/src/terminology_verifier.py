"""Stage 2: Semantic & Terminology Conformance Verifier (SNOMED CT, LOINC, UCUM, Irish OIDs).

Audits FHIR R4 Bundles and resources for:
1. Cross-service OID drift (Irish GMS OID vs HL7/IHI OIDs).
2. Strict UCUM unit conformance (e.g., 'mm[Hg]' vs 'mmHg', '/min' vs 'bpm').
3. LOINC code consistency (e.g., SpO2 '59408-5' vs '2708-6') and physiological bounds.
4. Silent SNOMED CT fallback masking ('404684003' generic Clinical Finding).
5. Semantic contradictions between free-text notes/allergies and coded prescriptions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

STRICT_LOINC_UCUM_RULES: Dict[str, Dict[str, Any]] = {
    "8480-6": {"display": "Systolic blood pressure", "ucum": "mm[Hg]", "min": 40.0, "max": 280.0},
    "8462-4": {"display": "Diastolic blood pressure", "ucum": "mm[Hg]", "min": 20.0, "max": 180.0},
    "8867-4": {"display": "Heart rate", "ucum": "/min", "min": 20.0, "max": 250.0},
    "9279-1": {"display": "Respiratory rate", "ucum": "/min", "min": 4.0, "max": 60.0},
    "2708-6": {"display": "Oxygen saturation in Arterial blood", "ucum": "%", "min": 50.0, "max": 100.0},
    "59408-5": {"display": "Oxygen saturation in Arterial blood by Pulse oximetry", "ucum": "%", "min": 50.0, "max": 100.0},
    "8310-5": {"display": "Body temperature", "ucum": "Cel", "min": 28.0, "max": 43.0},
    "9269-2": {"display": "Glasgow coma score total", "ucum": "{score}", "min": 3.0, "max": 15.0},
    "72514-3": {"display": "Pain severity - 0-10 verbal numeric rating [Score] - Reported", "ucum": "{score}", "min": 0.0, "max": 10.0},
}

APPROVED_PATIENT_IDENTIFIER_SYSTEMS = {
    "urn:oid:1.3.6.1.4.1.54392.5.2690.42.80": "Irish GMS OID (SlainteScan)",
    "urn:oid:2.16.840.1.113883.2.17.1.1": "Irish Health OID (SlainteFHIR)",
    "http://health.gov.ie/ihi": "Irish Individual Health Identifier (IHI)",
    "https://fhir.nhs.uk/Id/nhs-number": "NHS Number",
}

PENICILLIN_ALLERGY_MARKERS = {"penicillin", "amoxicillin", "beta-lactam", "91936005", "764146007"}
BETA_LACTAM_MED_MARKERS = {"co-amoxiclav", "augmentin", "amoxicillin", "ampicillin", "piperacillin", "617296", "372687004"}


@dataclass
class TerminologyFinding:
    rule_id: str
    severity: str  # "error" | "warning"
    resource_id: str
    resource_type: str
    message: str
    cwe_id: str = "CWE-20"
    owasp_category: str = "FHIR-Semantic-Conformance"


def verify_bundle_terminology(bundle: Dict[str, Any]) -> List[TerminologyFinding]:
    """
    Audits a FHIR R4 Bundle for terminology, UCUM unit, OID drift, and clinical safety errors.
    """
    findings: List[TerminologyFinding] = []
    if bundle.get("resourceType") != "Bundle":
        findings.append(
            TerminologyFinding(
                rule_id="FHIR-STRUCT-001",
                severity="error",
                resource_id=str(bundle.get("id", "root")),
                resource_type=str(bundle.get("resourceType", "Unknown")),
                message="Root resourceType must be 'Bundle'.",
            )
        )
        return findings

    entries = bundle.get("entry", [])
    documented_penicillin_allergy = False
    proposed_beta_lactam_meds: List[str] = []

    for idx, entry in enumerate(entries):
        res = entry.get("resource", {}) if isinstance(entry, dict) else {}
        rtype = res.get("resourceType", "Unknown")
        rid = res.get("id", f"entry-{idx}")

        if rtype == "Patient":
            for ident in res.get("identifier", []):
                sys_uri = ident.get("system", "")
                if sys_uri not in APPROVED_PATIENT_IDENTIFIER_SYSTEMS:
                    findings.append(
                        TerminologyFinding(
                            rule_id="FHIR-OID-001",
                            severity="error",
                            resource_id=rid,
                            resource_type="Patient",
                            message=f"Unrecognized Patient.identifier.system '{sys_uri}'.",
                        )
                    )
                elif sys_uri == "urn:oid:1.3.6.1.4.1.54392.5.2690.42.80":
                    findings.append(
                        TerminologyFinding(
                            rule_id="FHIR-OID-DRIFT-002",
                            severity="warning",
                            resource_id=rid,
                            resource_type="Patient",
                            message=(
                                "Cross-service OID drift detected: bundle uses SlainteScan GMS OID "
                                "'urn:oid:1.3.6.1.4.1.54392.5.2690.42.80' which SlainteFHIR "
                                "verification_engine rejects (expects 'urn:oid:2.16.840.1.113883.2.17.1.1')."
                            ),
                        )
                    )

        elif rtype == "Condition":
            codings = res.get("code", {}).get("coding", [])
            for c in codings:
                sys_uri = c.get("system", "")
                code_val = str(c.get("code", ""))
                if sys_uri != "http://snomed.info/sct":
                    findings.append(
                        TerminologyFinding(
                            rule_id="SNOMED-SYS-001",
                            severity="error",
                            resource_id=rid,
                            resource_type="Condition",
                            message=f"Condition coding system must be 'http://snomed.info/sct', got '{sys_uri}'.",
                        )
                    )
                if code_val == "404684003":
                    findings.append(
                        TerminologyFinding(
                            rule_id="SNOMED-FALLBACK-002",
                            severity="warning",
                            resource_id=rid,
                            resource_type="Condition",
                            message=(
                                f"Condition/{rid} uses generic fallback SNOMED CT code '404684003' "
                                f"('{c.get('display', '')}'), indicating an unmapped clinical complaint."
                            ),
                        )
                    )

        elif rtype == "Observation":
            codings = res.get("code", {}).get("coding", [])
            vq = res.get("valueQuantity", {})
            for c in codings:
                if c.get("system") == "http://loinc.org":
                    l_code = str(c.get("code", ""))
                    if l_code == "59408-5":
                        findings.append(
                            TerminologyFinding(
                                rule_id="LOINC-DRIFT-001",
                                severity="warning",
                                resource_id=rid,
                                resource_type="Observation",
                                message=(
                                    f"Observation/{rid} uses pulse-oximetry SpO2 LOINC '59408-5', "
                                    "which conflicts with SlainteFHIR's strict '2708-6' validator map."
                                ),
                            )
                        )
                    if l_code in STRICT_LOINC_UCUM_RULES and vq:
                        expected_ucum = STRICT_LOINC_UCUM_RULES[l_code]["ucum"]
                        actual_ucum = vq.get("code") or vq.get("unit") or ""
                        if actual_ucum != expected_ucum:
                            findings.append(
                                TerminologyFinding(
                                    rule_id="UCUM-UNIT-001",
                                    severity="error",
                                    resource_id=rid,
                                    resource_type="Observation",
                                    message=(
                                        f"Non-compliant UCUM unit on Observation/{rid} (LOINC {l_code}): "
                                        f"expected strict UCUM '{expected_ucum}', got '{actual_ucum}'."
                                    ),
                                )
                            )
                        try:
                            val = float(vq.get("value", 0.0))
                            lo, hi = STRICT_LOINC_UCUM_RULES[l_code]["min"], STRICT_LOINC_UCUM_RULES[l_code]["max"]
                            if not (lo <= val <= hi):
                                findings.append(
                                    TerminologyFinding(
                                        rule_id="PHYSIO-BOUNDS-001",
                                        severity="error",
                                        resource_id=rid,
                                        resource_type="Observation",
                                        message=(
                                            f"Physiologically implausible value {val} {actual_ucum} "
                                            f"on Observation/{rid} (valid range: {lo}..{hi})."
                                        ),
                                    )
                                )
                        except (TypeError, ValueError):
                            pass

        elif rtype == "AllergyIntolerance":
            text_blob = str(res.get("code", {})).lower()
            if any(m in text_blob for m in PENICILLIN_ALLERGY_MARKERS):
                documented_penicillin_allergy = True

        elif rtype == "MedicationRequest":
            med_blob = str(res.get("medicationCodeableConcept", {})).lower()
            if any(m in med_blob for m in BETA_LACTAM_MED_MARKERS):
                proposed_beta_lactam_meds.append(rid)

    if documented_penicillin_allergy and proposed_beta_lactam_meds:
        findings.append(
            TerminologyFinding(
                rule_id="CDS-CONTRAINDICATION-001",
                severity="error",
                resource_id=",".join(proposed_beta_lactam_meds),
                resource_type="MedicationRequest",
                message=(
                    "Semantic Clinical Safety Violation: Beta-lactam MedicationRequest "
                    f"({', '.join(proposed_beta_lactam_meds)}) prescribed alongside documented "
                    "Penicillin AllergyIntolerance."
                ),
            )
        )

    return findings
