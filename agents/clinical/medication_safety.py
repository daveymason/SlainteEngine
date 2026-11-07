"""Agent 08: SlainteRx-Guard — Pharmacotherapy, Allergy & Multi-Tier Renal Safety Gate."""
from typing import Dict, Any, Optional, List
from agents.base import BaseAgent, AgentExecutionResult


class MedicationSafetyAgent(BaseAgent):
    id: str = "medication_safety"
    number: str = "08"
    code: str = "SlainteRx-Guard"
    name: str = "Pharmacotherapy & Allergy Safety Gate"
    fleet: str = "clinical"

    def health_check(self) -> bool:
        return True

    def evaluate_safety(
        self,
        allergies: List[str],
        medications: List[str],
        observations: Optional[List[Dict[str, Any]]] = None,
        candidate_drug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Perform 3-tier safety screening: Allergies, DDI interactions, and eGFR renal gates."""
        try:
            from enterprise_engine import evaluate_clinical_pharmacology_3tier
            return evaluate_clinical_pharmacology_3tier(
                allergies=allergies,
                active_medications=medications,
                lab_observations=observations or [],
                candidate_drug=candidate_drug,
            )
        except ImportError:
            try:
                from frontend.enterprise_engine import evaluate_clinical_pharmacology_3tier
                return evaluate_clinical_pharmacology_3tier(
                    allergies=allergies,
                    active_medications=medications,
                    lab_observations=observations or [],
                    candidate_drug=candidate_drug,
                )
            except Exception as e:
                return {
                    "alerts": [{"tier": "ERROR", "severity": "error", "message": str(e)}],
                    "tier_counts": {"tier1": 0, "tier2": 0, "tier3": 0},
                    "egfr": None,
                }

    def run(self, context: Optional[Dict[str, Any]] = None, **kwargs) -> AgentExecutionResult:
        context = context or {}
        allergies = context.get("allergies") or kwargs.get("allergies") or []
        medications = context.get("medications") or kwargs.get("medications") or []
        candidate_drug = context.get("candidate_drug") or kwargs.get("candidate_drug")
        observations = context.get("observations") or kwargs.get("observations") or []

        eval_result = self.evaluate_safety(allergies, medications, observations, candidate_drug)
        alerts = eval_result.get("alerts", [])
        hard_stops = [a for a in alerts if a.get("tier") == "TIER_1_ALLERGY_HARD_STOP" or a.get("severity") == "error"]

        status = "fail" if hard_stops else ("warning" if alerts else "pass")
        summary = (
            f"3-Tier Rx-Guard evaluated {len(medications) + (1 if candidate_drug else 0)} medication(s): "
            f"{len(alerts)} alert(s) identified ({len(hard_stops)} Tier-1 Hard Stops, eGFR={eval_result.get('egfr')})."
        )

        return AgentExecutionResult(
            agent_id=self.id,
            status=status,
            summary=summary,
            findings=alerts,
            telemetry=eval_result,
        )
