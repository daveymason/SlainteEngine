"""Agent 15: SlainteCare-CDM — Chronic Disease & Quality Care Surveillance Agent."""
from typing import Dict, Any, Optional, List
from agents.base import BaseAgent, AgentExecutionResult


class ChronicSurveillanceAgent(BaseAgent):
    id: str = "chronic_surveillance"
    number: str = "15"
    code: str = "SlainteCare-CDM"
    name: str = "Chronic Disease & Quality Care Surveillance Agent"
    fleet: str = "clinical"

    def health_check(self) -> bool:
        return True

    def scan_cdm_cohort(self, patients_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Audits chronic disease markers and flags guideline care gaps."""
        care_gaps = []
        monitored_conditions = ["Type 2 Diabetes", "Hypertension", "Chronic Kidney Disease", "COPD / Asthma"]

        sample_patients = patients_data or [
            {"id": "P101", "name": "Margaret O'Reilly", "condition": "Type 2 Diabetes", "last_hba1c_months": 14, "hba1c_value": 58, "bp": "148/88"},
            {"id": "P102", "name": "Sean Fitzpatrick", "condition": "Hypertension", "last_hba1c_months": 4, "hba1c_value": 38, "bp": "162/96"},
            {"id": "P103", "name": "Eileen Walsh", "condition": "Chronic Kidney Disease", "last_egfr_months": 9, "egfr": 42, "bp": "128/78"},
        ]

        for p in sample_patients:
            if p.get("last_hba1c_months", 0) > 12:
                care_gaps.append({
                    "patient_id": p["id"],
                    "name": p["name"],
                    "gap_type": "Overdue HbA1c Review",
                    "severity": "medium",
                    "guideline": "HSE CDM Contract: Annual HbA1c required.",
                })
            bp_sys = int(p.get("bp", "120/80").split("/")[0])
            if bp_sys >= 150:
                care_gaps.append({
                    "patient_id": p["id"],
                    "name": p["name"],
                    "gap_type": "Uncontrolled Systolic BP (>=150 mmHg)",
                    "severity": "high",
                    "guideline": "Target BP < 140/90 mmHg for chronic disease cohort.",
                })

        return {
            "cohort_size": len(sample_patients),
            "monitored_conditions": monitored_conditions,
            "care_gaps_count": len(care_gaps),
            "care_gaps": care_gaps,
        }

    def run(self, context: Optional[Dict[str, Any]] = None, **kwargs) -> AgentExecutionResult:
        context = context or {}
        cdm_res = self.scan_cdm_cohort(context.get("patients"))
        findings = []

        status = "pass" if cdm_res["care_gaps_count"] == 0 else "warning"

        for gap in cdm_res["care_gaps"]:
            findings.append({
                "patient": f"{gap['name']} ({gap['patient_id']})",
                "gap": gap["gap_type"],
                "severity": gap["severity"],
                "guideline": gap["guideline"],
            })

        summary = (
            f"Chronic Disease Surveillance Agent audited {cdm_res['cohort_size']} patient record(s): "
            f"{cdm_res['care_gaps_count']} clinical care gap(s) surfaced for proactive GP intervention."
        )

        return AgentExecutionResult(
            agent_id=self.id,
            status=status,
            summary=summary,
            findings=findings,
            telemetry=cdm_res,
        )
