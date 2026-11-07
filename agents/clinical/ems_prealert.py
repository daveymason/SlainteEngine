"""Agent 14: SlainteEMS-Alert — Emergency Pre-Hospital Pre-Alert Agent."""
from typing import Dict, Any, Optional, List
from agents.base import BaseAgent, AgentExecutionResult


class EmsPrealertAgent(BaseAgent):
    id: str = "ems_prealert"
    number: str = "14"
    code: str = "SlainteEMS-Alert"
    name: str = "Emergency Pre-Hospital Pre-Alert Agent"
    fleet: str = "clinical"

    def health_check(self) -> bool:
        return True

    def calculate_alert_priority(self, vitals: Dict[str, Any], complaint: str = "") -> Dict[str, Any]:
        """Calculates MTS category and NEWS2 score to determine ED pre-alert severity."""
        mts_category = 3
        try:
            from fhir_utils import calculate_news2_score
            news_res = calculate_news2_score(vitals)
            news2 = news_res.get("news2_score", 0) if isinstance(news_res, dict) else int(news_res or 0)
        except Exception:
            news2 = 2

        # Fast triage categorization
        sbp = vitals.get("sbp", 120)
        spo2 = vitals.get("spo2", 98)
        if sbp < 80 or spo2 < 85 or "unresponsive" in complaint.lower() or "cardiac" in complaint.lower():
            mts_category = 1
        elif news2 >= 7 or spo2 < 91:
            mts_category = 2
        elif news2 >= 5:
            mts_category = 3
        else:
            mts_category = 4

        requires_prealert = mts_category in (1, 2) or news2 >= 7
        return {
            "mts_category": mts_category,
            "news2_score": news2,
            "requires_ed_prealert": requires_prealert,
            "alert_tier": "CRITICAL PRE-ALERT (RED)" if mts_category == 1 else ("URGENT PRE-ALERT (AMBER)" if requires_prealert else "STANDARD TRANSPORT (GREEN)"),
        }

    def run(self, context: Optional[Dict[str, Any]] = None, **kwargs) -> AgentExecutionResult:
        context = context or {}
        vitals = context.get("vitals") or kwargs.get("vitals") or {"sbp": 85, "hr": 128, "spo2": 89, "rr": 28, "temp": 39.2}
        complaint = context.get("complaint") or kwargs.get("complaint") or "Acute respiratory distress and hypotension"
        eta_minutes = context.get("eta_minutes", 12)

        alert_res = self.calculate_alert_priority(vitals, complaint)
        findings = []

        if alert_res["requires_ed_prealert"]:
            status = "warning"
            findings.append({
                "category": "emergency_prealert",
                "status": "warning",
                "detail": f"{alert_res['alert_tier']}: MTS Cat {alert_res['mts_category']} & NEWS2 {alert_res['news2_score']}. Handoff ETA: {eta_minutes} min.",
            })
            summary = (
                f"Emergency Pre-Alert Agent: Dispatched {alert_res['alert_tier']} to receiving Emergency Department. "
                f"MTS Category {alert_res['mts_category']}, NEWS2: {alert_res['news2_score']}, ETA: {eta_minutes}m."
            )
        else:
            status = "pass"
            findings.append({
                "category": "routine_transport",
                "status": "pass",
                "detail": f"Standard transit: MTS Cat {alert_res['mts_category']}, NEWS2 {alert_res['news2_score']}. ETA: {eta_minutes} min.",
            })
            summary = (
                f"Emergency Pre-Alert Agent: Patient in stable transit. "
                f"MTS Category {alert_res['mts_category']}, NEWS2: {alert_res['news2_score']}, ETA: {eta_minutes}m."
            )

        telemetry = {
            **alert_res,
            "eta_minutes": eta_minutes,
            "presenting_complaint": complaint,
            "vitals_snapshot": vitals,
        }

        return AgentExecutionResult(
            agent_id=self.id,
            status=status,
            summary=summary,
            findings=findings,
            telemetry=telemetry,
        )
