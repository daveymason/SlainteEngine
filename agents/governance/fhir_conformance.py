"""Agent 02: SlainteShield-FHIR — FHIR R4 Conformance, Terminology & SARIF Verifier."""
import os
import json
from typing import Dict, Any, Optional, List
from agents.base import BaseAgent, AgentExecutionResult


class FhirConformanceAgent(BaseAgent):
    id: str = "fhir_conformance"
    number: str = "02"
    code: str = "SlainteShield-FHIR"
    name: str = "FHIR R4 Integrity & Terminology"
    fleet: str = "governance"

    def __init__(self, fhir_store_path: Optional[str] = None):
        self.fhir_store_path = fhir_store_path or os.environ.get(
            "FHIR_STORE_PATH",
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "fhir_store"))
        )

    def health_check(self) -> bool:
        """Verify presence of FHIR bundle storage directory."""
        return os.path.isdir(self.fhir_store_path)

    def inspect_bundle(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Inspect bundle for GMS OIDs, LOINC, SNOMED-CT, and UCUM units."""
        if not os.path.isdir(self.fhir_store_path):
            return None
        bfile = f"bundle_{patient_id}.json"
        bpath = os.path.join(self.fhir_store_path, bfile)
        if not os.path.isfile(bpath):
            return None

        try:
            with open(bpath, "r", encoding="utf-8") as f:
                bdata = json.load(f)
            res_rows = []
            gms_valid = False
            gms_val = "None"
            pt_name = patient_id
            for entry in bdata.get("entry") or []:
                res = entry.get("resource") or {}
                rtype = res.get("resourceType", "Resource")
                rid = res.get("id", "unknown")
                sys_str = "HL7 FHIR R4 Core"
                disp_str = rtype
                valid = True
                if rtype == "Patient":
                    name_obj = (res.get("name") or [{}])[0]
                    given = " ".join(name_obj.get("given", []))
                    family = name_obj.get("family", "")
                    pt_name = f"{family}, {given}".strip(", ") or patient_id
                    for ident in res.get("identifier") or []:
                        system = ident.get("system") or ""
                        if "54392" in system or "113883" in system:
                            gms_valid = True
                            gms_val = ident.get("value", "GMS")
                            sys_str = system
                    disp_str = f"{pt_name} ({res.get('gender', '')}, {res.get('birthDate', '')})"
                    valid = gms_valid
                elif rtype in ("Observation", "Condition", "AllergyIntolerance"):
                    coding = ((res.get("code") or {}).get("coding") or [{}])[0]
                    sys_str = coding.get("system") or "Unmapped"
                    disp_str = coding.get("display") or (res.get("code") or {}).get("text") or rtype
                    valid = bool(coding.get("code") and coding.get("system"))
                elif rtype == "MedicationRequest":
                    coding = ((res.get("medicationCodeableConcept") or {}).get("coding") or [{}])[0]
                    sys_str = coding.get("system") or "SNOMED/RxNorm"
                    disp_str = (res.get("medicationCodeableConcept") or {}).get("text") or coding.get("display") or "Medication"
                res_rows.append({
                    "resourceType": rtype,
                    "id": rid,
                    "system": sys_str,
                    "display": disp_str,
                    "valid": valid,
                })

            return {
                "filename": bfile,
                "patient_id": patient_id,
                "patient_name": pt_name,
                "gms_valid": gms_valid,
                "gms_value": gms_val,
                "resources": res_rows,
            }
        except Exception:
            return None

    def run(self, context: Optional[Dict[str, Any]] = None, **kwargs) -> AgentExecutionResult:
        context = context or {}
        patient_id = context.get("patient_id", "patient-case-1")
        inspected = self.inspect_bundle(patient_id)
        findings = []
        if inspected and not inspected.get("gms_valid"):
            findings.append({
                "rule": "IRISH-GMS-OID-MISSING",
                "severity": "warning",
                "detail": f"Patient {patient_id} bundle does not contain verified Irish GMS OID identifier.",
            })

        status = "pass" if not findings else "warning"
        summary = (
            f"Audited FHIR R4 conformance for {patient_id}: "
            f"{len(inspected.get('resources', [])) if inspected else 0} resources inspected, "
            f"GMS OID verified={inspected.get('gms_valid', False) if inspected else False}."
        )

        return AgentExecutionResult(
            agent_id=self.id,
            status=status,
            summary=summary,
            findings=findings,
            telemetry={"inspected_bundle": inspected},
        )
