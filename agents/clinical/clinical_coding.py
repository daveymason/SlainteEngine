"""Agent 11: SlainteRev-Coding — HIPE / ICD-10-AM Clinical Coding & Revenue Audit Agent."""
from typing import Dict, Any, Optional, List
from agents.base import BaseAgent, AgentExecutionResult


class ClinicalCodingAgent(BaseAgent):
    id: str = "clinical_coding"
    number: str = "11"
    code: str = "SlainteRev-Coding"
    name: str = "HIPE / ICD-10-AM Clinical Coding & Revenue Audit"
    fleet: str = "clinical"

    def health_check(self) -> bool:
        return True

    def scan_coding_gaps(
        self,
        patient_id: str,
        patient_name: str,
        conditions: List[Dict[str, Any]],
        observations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Audit active conditions against laboratory and vital observations for uncoded DRG comorbidities."""
        try:
            from enterprise_engine import scan_patient_coding_gaps
            return scan_patient_coding_gaps(patient_id, patient_name, conditions, observations)
        except ImportError:
            try:
                from frontend.enterprise_engine import scan_patient_coding_gaps
                return scan_patient_coding_gaps(patient_id, patient_name, conditions, observations)
            except Exception as e:
                return {
                    "patient_id": patient_id,
                    "patient_name": patient_name,
                    "coding_gaps": [],
                    "total_uplift_eur": 0,
                    "error": str(e),
                }

    def run(self, context: Optional[Dict[str, Any]] = None, **kwargs) -> AgentExecutionResult:
        context = context or {}
        patient_id = context.get("patient_id") or kwargs.get("patient_id") or "P101"
        patient_name = context.get("patient_name") or kwargs.get("patient_name") or "Patient"
        conditions = context.get("conditions") or kwargs.get("conditions") or []
        observations = context.get("observations") or kwargs.get("observations") or []

        report = self.scan_coding_gaps(patient_id, patient_name, conditions, observations)
        gaps = report.get("coding_gaps", [])
        uplift = report.get("total_uplift_eur", 0)

        summary = (
            f"Agent 11 (SlainteRev-Coding) audited {patient_name} ({patient_id}): "
            f"{len(gaps)} uncoded ICD-10-AM comorbidity gap(s) identified with €{uplift:,} DRG uplift potential."
        )

        return AgentExecutionResult(
            agent_id=self.id,
            status="pass" if not gaps else "warning",
            summary=summary,
            findings=gaps,
            telemetry=report,
        )
