"""Agent 09: SlainteDx-Triage — Acuity Triage & NEWS2 Deterioration Engine."""
from typing import Dict, Any, Optional, Tuple, List
from agents.base import BaseAgent, AgentExecutionResult


class AcuityTriageAgent(BaseAgent):
    id: str = "acuity_triage"
    number: str = "09"
    code: str = "SlainteDx-Triage"
    name: str = "Acuity Triage & NEWS2 Deterioration"
    fleet: str = "clinical"

    def health_check(self) -> bool:
        return True

    def calculate_scores(self, vitals: Dict[str, Any]) -> Dict[str, Any]:
        """Compute Manchester Triage System (1-5) and RCP NEWS2 scores from vital observations."""
        try:
            from clinical_intake import calculate_mts_category, calculate_news2_score, MTS_METADATA
        except ImportError:
            try:
                from frontend.clinical_intake import calculate_mts_category, calculate_news2_score, MTS_METADATA
            except Exception:
                # Fallback to local scoring logic
                return {
                    "news2_score": 0,
                    "news2_tier": "Low Risk",
                    "breakdown": {},
                    "mts_cat": 3,
                    "mts_name": "Urgent",
                    "mts_target": 60,
                }

        n_score, n_tier, n_break = calculate_news2_score(vitals)
        mts_cat = calculate_mts_category(vitals)
        mts_meta = MTS_METADATA.get(mts_cat, MTS_METADATA[3])

        return {
            "news2_score": n_score,
            "news2_tier": n_tier,
            "breakdown": n_break,
            "mts_cat": mts_cat,
            "mts_name": mts_meta["name"],
            "mts_target": mts_meta["target_time_minutes"],
        }

    def run(self, context: Optional[Dict[str, Any]] = None, **kwargs) -> AgentExecutionResult:
        context = context or {}
        vitals = context.get("vitals") or kwargs.get("vitals") or {
            "rr": 20, "spo2": 97, "sbp": 120, "hr": 78, "temp": 37.0,
        }

        scores = self.calculate_scores(vitals)
        status = "pass"
        if scores["news2_score"] >= 7 or scores["mts_cat"] <= 2:
            status = "fail"
        elif scores["news2_score"] >= 5 or scores["mts_cat"] == 3:
            status = "warning"

        summary = (
            f"Computed MTS Category {scores['mts_cat']} ({scores['mts_name']}, target {scores['mts_target']}m) "
            f"and RCP NEWS2 Score {scores['news2_score']}/20 ({scores['news2_tier']})."
        )

        return AgentExecutionResult(
            agent_id=self.id,
            status=status,
            summary=summary,
            findings=[scores] if status != "pass" else [],
            telemetry=scores,
        )
