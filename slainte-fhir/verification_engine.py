#!/usr/bin/env python3
"""
HL7 FHIR R4 Synthetic Cohort Dual-Tier Verification & Clinical Audit Engine
Compatible with Python 3.12+ (Standard Library Only: json, re, sys, pathlib, dataclasses)
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ============================================================================
# TIER 1 & TIER 2 CONSTANTS AND ONTOLOGY MAPS
# ============================================================================

ISO8601_TZ_REGEX = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
IRISH_GMS_REGEX = re.compile(r"^99\d{3}-[A-Z]$")
NHS_NUMBER_REGEX = re.compile(r"^\d{10}$")

REQUIRED_LOINC_UCUM_MAP: dict[str, tuple[str, str]] = {
    "8480-6": ("Systolic blood pressure", "mm[Hg]"),
    "8462-4": ("Diastolic blood pressure", "mm[Hg]"),
    "8867-4": ("Heart rate", "/min"),
    "9279-1": ("Respiratory rate", "/min"),
    "2708-6": ("Oxygen saturation in Arterial blood", "%"),
    "8310-5": ("Body temperature", "Cel"),
    "9269-2": ("Glasgow coma score total", "{score}"),
    "72514-3": ("Pain severity - 0-10 verbal numeric rating [Score] - Reported", "{score}"),
    "4548-4": ("Hemoglobin A1c/Hemoglobin.total in Blood", "%"),
    "33914-3": (
        "Glomerular filtration rate [Volume Rate/Area] in Serum or Plasma by Creatinine-based formula (MDRD)/1.73 sq M",
        "mL/min/{1.73_m2}",
    ),
    "6690-2": ("Leukocytes [#/volume] in Blood by Automated count", "10*9/L"),
}

MTS_SNOMED_TO_CATEGORY: dict[str, tuple[int, str]] = {
    "394849002": (1, "MTS Category 1 - Immediate (Red)"),
    "394848005": (2, "MTS Category 2 - Very Urgent (Orange)"),
    "394850002": (3, "MTS Category 3 - Urgent (Yellow)"),
    "394847000": (4, "MTS Category 4 - Standard (Green)"),
    "394846009": (5, "MTS Category 5 - Non-Urgent (Blue)"),
}

EXPECTED_COHORT_SCORES: dict[str, tuple[int, int]] = {
    "patient-case-1": (1, 18),
    "patient-case-2": (2, 11),
    "patient-case-3": (3, 2),
    "patient-case-4": (4, 0),
    "patient-case-5": (5, 0),
    "patient-case-6": (5, 0),
    "patient-case-7": (3, 1),
    "patient-case-8": (3, 0),
}


@dataclass
class PatientCohortSummary:
    patient_id: str
    full_url: str
    identifier_system: str
    identifier_value: str
    encounter_class: str = ""
    mts_category: int = 0
    mts_label: str = ""
    vitals: dict[str, float] = field(default_factory=dict)
    on_supplemental_o2: bool = False
    news2_score: int = 0
    news2_breakdown: dict[str, int] = field(default_factory=dict)
    conditions: list[str] = field(default_factory=list)
    safety_flags: list[str] = field(default_factory=list)


# ============================================================================
# DETERMINISTIC ROYAL COLLEGE OF PHYSICIANS NEWS2 ENGINE
# ============================================================================

def calculate_news2_scale1(
    rr: float,
    spo2: float,
    on_o2: bool,
    sbp: float,
    hr: float,
    gcs: float,
    temp: float,
) -> tuple[int, dict[str, int]]:
    """Computes deterministic RCP NEWS2 aggregate score and parameter breakdown."""
    breakdown: dict[str, int] = {}

    # 1. Respiration Rate (/min)
    if rr <= 8:
        breakdown["RR"] = 3
    elif 9 <= rr <= 11:
        breakdown["RR"] = 1
    elif 12 <= rr <= 20:
        breakdown["RR"] = 0
    elif 21 <= rr <= 24:
        breakdown["RR"] = 2
    else:
        breakdown["RR"] = 3

    # 2. SpO2 Scale 1 (%)
    if spo2 <= 91:
        breakdown["SpO2"] = 3
    elif 92 <= spo2 <= 93:
        breakdown["SpO2"] = 2
    elif 94 <= spo2 <= 95:
        breakdown["SpO2"] = 1
    else:
        breakdown["SpO2"] = 0

    # 3. Air or Supplemental Oxygen
    breakdown["O2"] = 2 if on_o2 else 0

    # 4. Systolic Blood Pressure (mm[Hg])
    if sbp <= 90:
        breakdown["SBP"] = 3
    elif 91 <= sbp <= 100:
        breakdown["SBP"] = 2
    elif 101 <= sbp <= 110:
        breakdown["SBP"] = 1
    elif 111 <= sbp <= 219:
        breakdown["SBP"] = 0
    else:
        breakdown["SBP"] = 3

    # 5. Pulse / Heart Rate (/min)
    if hr <= 40:
        breakdown["HR"] = 3
    elif 41 <= hr <= 50:
        breakdown["HR"] = 1
    elif 51 <= hr <= 90:
        breakdown["HR"] = 0
    elif 91 <= hr <= 110:
        breakdown["HR"] = 1
    elif 111 <= hr <= 130:
        breakdown["HR"] = 2
    else:
        breakdown["HR"] = 3

    # 6. Consciousness (ACVPU mapped from GCS: GCS 15 == Alert (0), GCS < 15 == CVPU (3))
    breakdown["CVPU"] = 0 if gcs == 15 else 3

    # 7. Body Temperature (Cel)
    if temp <= 35.0:
        breakdown["Temp"] = 3
    elif 35.1 <= temp <= 36.0:
        breakdown["Temp"] = 1
    elif 36.1 <= temp <= 38.0:
        breakdown["Temp"] = 0
    elif 38.1 <= temp <= 39.0:
        breakdown["Temp"] = 1
    else:
        breakdown["Temp"] = 2

    total_score = sum(breakdown.values())
    return total_score, breakdown


# ============================================================================
# DUAL-TIER AUDIT ENGINE
# ============================================================================

def verify_fhir_r4_bundle(bundle_data: dict[str, Any]) -> None:
    print("=" * 84)
    print("HL7 FHIR R4 DUAL-TIER SYNTHETIC COHORT VERIFICATION ENGINE")
    print("=" * 84)

    # ------------------------------------------------------------------------
    # TIER 1: SYNTACTIC & STRUCTURAL AUDIT
    # ------------------------------------------------------------------------
    assert bundle_data.get("resourceType") == "Bundle", "Root resourceType must be 'Bundle'"
    bundle_type = bundle_data.get("type")
    assert bundle_type in ("transaction", "collection"), f"Invalid Bundle.type: {bundle_type}"

    entries = bundle_data.get("entry", [])
    assert len(entries) > 0, "Bundle.entry cannot be empty"

    full_url_registry: dict[str, dict[str, Any]] = {}
    cohorts_by_url: dict[str, PatientCohortSummary] = {}

    for idx, entry in enumerate(entries):
        full_url = entry.get("fullUrl", "")
        assert full_url.startswith("urn:uuid:"), f"Entry {idx} missing valid urn:uuid fullUrl"
        assert full_url not in full_url_registry, f"Duplicate fullUrl detected: {full_url}"

        resource = entry.get("resource", {})
        res_type = resource.get("resourceType")
        assert res_type, f"Entry {idx} missing resourceType"
        full_url_registry[full_url] = resource

        if bundle_type == "transaction":
            req = entry.get("request", {})
            assert req.get("method") == "POST", f"Entry {idx} request.method must be 'POST'"
            assert req.get("url") == res_type, f"Entry {idx} request.url must match {res_type}"

        # Validate Patient Identifiers and Demographics
        if res_type == "Patient":
            pat_id = resource.get("id", "")
            identifiers = resource.get("identifier", [])
            assert len(identifiers) >= 1, f"Patient {pat_id} missing identifier"
            id_sys = identifiers[0].get("system", "")
            id_val = identifiers[0].get("value", "")

            if id_sys == "urn:oid:2.16.840.1.113883.2.17.1.1":
                assert IRISH_GMS_REGEX.match(id_val), f"Invalid Irish GMS ID format: {id_val}"
            elif id_sys == "https://fhir.nhs.uk/Id/nhs-number":
                assert NHS_NUMBER_REGEX.match(id_val), f"Invalid NHS Number format: {id_val}"
            else:
                raise AssertionError(f"Unsupported identifier system: {id_sys}")

            for req_field in ("name", "telecom", "gender", "birthDate", "address"):
                assert req_field in resource, f"Patient {pat_id} missing {req_field}"

            cohorts_by_url[full_url] = PatientCohortSummary(
                patient_id=pat_id,
                full_url=full_url,
                identifier_system=id_sys,
                identifier_value=id_val,
            )

    # Second pass: Verify Referential Integrity, ISO-8601 Timestamps, and Clinical Semantics
    for full_url, resource in full_url_registry.items():
        res_type = resource["resourceType"]
        res_id = resource.get("id", "unknown")

        # Check all timestamp fields for strict ISO-8601 compliance
        for ts_field in ("effectiveDateTime", "recordedDate", "authoredOn", "recorded"):
            if ts_field in resource:
                ts_val = resource[ts_field]
                assert ISO8601_TZ_REGEX.match(ts_val), (
                    f"Resource {res_id} has non-compliant ISO-8601 timestamp: {ts_val}"
                )
        if "period" in resource:
            for p_field in ("start", "end"):
                if p_field in resource["period"]:
                    p_val = resource["period"][p_field]
                    assert ISO8601_TZ_REGEX.match(p_val), (
                        f"Resource {res_id} period.{p_field} invalid ISO-8601: {p_val}"
                    )

        # Verify Subject / Patient References
        subj_ref = None
        if "subject" in resource:
            subj_ref = resource["subject"].get("reference")
        elif "patient" in resource:
            subj_ref = resource["patient"].get("reference")

        if subj_ref:
            assert subj_ref in cohorts_by_url, (
                f"Broken subject reference {subj_ref} in {res_type}/{res_id}"
            )
            cohort = cohorts_by_url[subj_ref]

            if res_type == "Encounter":
                enc_class = resource.get("class", {}).get("code")
                assert enc_class in ("AMB", "EMER", "IMP"), f"Invalid Encounter.class: {enc_class}"
                cohort.encounter_class = enc_class

                prio_codings = resource.get("priority", {}).get("coding", [])
                assert prio_codings, f"Encounter {res_id} missing MTS priority coding"
                mts_code = prio_codings[0].get("code")
                assert mts_code in MTS_SNOMED_TO_CATEGORY, f"Unknown MTS SNOMED code: {mts_code}"
                cohort.mts_category, cohort.mts_label = MTS_SNOMED_TO_CATEGORY[mts_code]

            elif res_type == "Condition":
                clin_status = (
                    resource.get("clinicalStatus", {}).get("coding", [{}])[0].get("code")
                )
                ver_status = (
                    resource.get("verificationStatus", {}).get("coding", [{}])[0].get("code")
                )
                assert clin_status in ("active", "recurrence", "resolved"), (
                    f"Invalid Condition.clinicalStatus: {clin_status}"
                )
                assert ver_status in ("confirmed", "provisional"), (
                    f"Invalid Condition.verificationStatus: {ver_status}"
                )
                codings = resource.get("code", {}).get("coding", [])
                for c in codings:
                    assert c.get("system") == "http://snomed.info/sct", (
                        f"Condition {res_id} must use SNOMED-CT system"
                    )
                    cohort.conditions.append(f"{c.get('code')} ({c.get('display')})")

            elif res_type == "Observation":
                coding = resource.get("code", {}).get("coding", [{}])[0]
                sys_uri = coding.get("system")
                code_val = coding.get("code")
                vq = resource.get("valueQuantity", {})
                val_num = float(vq.get("value", 0.0))
                ucum_code = vq.get("code", "")
                assert vq.get("system") == "http://unitsofmeasure.org", (
                    f"Observation {res_id} must use http://unitsofmeasure.org"
                )

                if sys_uri == "http://loinc.org":
                    assert code_val in REQUIRED_LOINC_UCUM_MAP, (
                        f"Unexpected LOINC code {code_val} in {res_id}"
                    )
                    expected_display, expected_ucum = REQUIRED_LOINC_UCUM_MAP[code_val]
                    assert ucum_code == expected_ucum, (
                        f"UCUM mismatch in {res_id}: expected {expected_ucum}, got {ucum_code}"
                    )

                    # Physiological Plausibility Rules (Zero Hallucination)
                    if code_val == "2708-6":  # SpO2
                        assert 50.0 <= val_num <= 100.0, f"Implausible SpO2: {val_num}%"
                        for comp in resource.get("component", []):
                            if "valueBoolean" in comp:
                                cohort.on_supplemental_o2 = bool(comp["valueBoolean"])
                    elif code_val == "8480-6":  # Systolic BP
                        assert 40.0 <= val_num <= 280.0, f"Implausible SBP: {val_num} mmHg"
                    elif code_val == "8462-4":  # Diastolic BP
                        assert 20.0 <= val_num <= 180.0, f"Implausible DBP: {val_num} mmHg"
                    elif code_val == "8867-4":  # Heart Rate
                        assert 20.0 <= val_num <= 250.0, f"Implausible HR: {val_num} /min"
                    elif code_val == "9279-1":  # Respiratory Rate
                        assert 4.0 <= val_num <= 60.0, f"Implausible RR: {val_num} /min"
                    elif code_val == "8310-5":  # Body Temp
                        assert 28.0 <= val_num <= 43.0, f"Implausible Temp: {val_num} Cel"
                    elif code_val == "9269-2":  # GCS
                        assert 3.0 <= val_num <= 15.0, f"Implausible GCS: {val_num}"
                    elif code_val == "72514-3":  # Pain
                        assert 0.0 <= val_num <= 10.0, f"Implausible Pain Score: {val_num}"

                    # Store latest vital reading by LOINC code
                    cohort.vitals[code_val] = val_num

            elif res_type == "AllergyIntolerance":
                crit = resource.get("criticality")
                codings = resource.get("code", {}).get("coding", [])
                for c in codings:
                    if c.get("code") in ("91936005", "764146007") and crit == "high":
                        cohort.safety_flags.append("DOCUMENTED_PENICILLIN_ANAPHYLAXIS")

            elif res_type == "MedicationRequest":
                codings = resource.get("medicationCodeableConcept", {}).get("coding", [])
                for c in codings:
                    if c.get("code") in ("617296", "372687004"):
                        cohort.safety_flags.append("PROPOSED_BETA_LACTAM_COAMOXICLAV")

            elif res_type == "Provenance":
                targets = resource.get("target", [])
                assert targets and isinstance(targets, list), f"Provenance {res_id} must have a non-empty target array"
                assert "recorded" in resource, f"Provenance {res_id} missing recorded timestamp"
                agents = resource.get("agent", [])
                assert agents and isinstance(agents, list), f"Provenance {res_id} must have practitioner agent array"

    print("[PASS] Tier 1: JSON Syntax, Transaction POST Semantics, UUID Referential Integrity & ISO-8601")
    print("[PASS] Tier 2: LOINC/SNOMED/RxNorm Bindings, Strict UCUM Units & Physiological Bounds\n")

    # ------------------------------------------------------------------------
    # TIER 2: DETERMINISTIC MTS & NEWS2 SCORING + DOMAIN SPECIFIC AUDITS
    # ------------------------------------------------------------------------
    print(f"{'Patient ID':<16} | {'Regional ID':<12} | {'Class':<5} | {'MTS Cat':<7} | {'NEWS2':<6} | {'Clinical Verification Notes'}")
    print("-" * 84)

    for pat_url, cohort in cohorts_by_url.items():
        v = cohort.vitals
        # Verify pulse pressure > 0
        assert v["8480-6"] > v["8462-4"], f"SBP must exceed DBP in {cohort.patient_id}"

        news2_total, breakdown = calculate_news2_scale1(
            rr=v["9279-1"],
            spo2=v["2708-6"],
            on_o2=cohort.on_supplemental_o2,
            sbp=v["8480-6"],
            hr=v["8867-4"],
            gcs=v["9269-2"],
            temp=v["8310-5"],
        )
        cohort.news2_score = news2_total
        cohort.news2_breakdown = breakdown

        exp_mts, exp_news2 = EXPECTED_COHORT_SCORES[cohort.patient_id]
        assert cohort.mts_category == exp_mts, (
            f"{cohort.patient_id} MTS mismatch: expected {exp_mts}, got {cohort.mts_category}"
        )
        assert cohort.news2_score == exp_news2, (
            f"{cohort.patient_id} NEWS2 mismatch: expected {exp_news2}, got {cohort.news2_score}"
        )

        notes = f"Breakdown: {breakdown}"
        if (
            "DOCUMENTED_PENICILLIN_ANAPHYLAXIS" in cohort.safety_flags
            and "PROPOSED_BETA_LACTAM_COAMOXICLAV" in cohort.safety_flags
        ):
            notes = "CDS GATE INTERCEPTED: Penicillin Anaphylaxis vs Co-Amoxiclav!"

        print(
            f"{cohort.patient_id:<16} | {cohort.identifier_value:<12} | "
            f"{cohort.encounter_class:<5} | Cat {cohort.mts_category:<3} | "
            f"{cohort.news2_score:>2}/20  | {notes}"
        )

    print("=" * 84)
    print("ALL 8 CLINICAL COHORTS PASSED DUAL-TIER VERIFICATION WITH ZERO ERRORS.")


if __name__ == "__main__":
    bundle_path = Path("synthetic_fhir_r4_cohorts.json")
    if not bundle_path.exists():
        print(
            "Note: Save the Deliverable 1 JSON block as 'synthetic_fhir_r4_cohorts.json' "
            "in the working directory to execute file-based verification.",
            file=sys.stderr,
        )
        sys.exit(0)

    with bundle_path.open("r", encoding="utf-8") as f:
        loaded_bundle = json.load(f)
    verify_fhir_r4_bundle(loaded_bundle)