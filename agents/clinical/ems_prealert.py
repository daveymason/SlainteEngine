"""Agent 14: SlainteEMS-Alert — Emergency Pre-Hospital Pre-Alert Agent."""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
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
        sbp = float(vitals.get("sbp") or vitals.get("systolic_bp") or 120)
        dbp = float(vitals.get("dbp") or vitals.get("diastolic_bp") or 80)
        hr = float(vitals.get("hr") or vitals.get("heart_rate") or 75)
        spo2 = float(vitals.get("spo2") or 98)
        rr = float(vitals.get("rr") or vitals.get("respiratory_rate") or 16)
        temp = float(vitals.get("temp") or vitals.get("temperature") or 36.8)

        norm_vitals = {
            "systolic_bp": sbp,
            "diastolic_bp": dbp,
            "heart_rate": hr,
            "spo2": spo2,
            "respiratory_rate": rr,
            "temperature": temp,
        }

        try:
            from fhir_utils import calculate_news2_score
            news_res = calculate_news2_score(norm_vitals)
            if isinstance(news_res, tuple):
                news2 = int(news_res[0] or 0)
            elif isinstance(news_res, dict):
                news2 = int(news_res.get("news2_score", 0))
            else:
                news2 = int(news_res or 0)
        except Exception:
            news2 = 0

        complaint_lower = (complaint or "").lower()
        if (
            sbp < 80
            or spo2 < 85
            or rr >= 35
            or rr < 8
            or "unresponsive" in complaint_lower
            or "cardiac arrest" in complaint_lower
            or "active hemorrhage" in complaint_lower
            or "anaphylaxis" in complaint_lower
        ):
            mts_category = 1
            mts_name = "Red / Immediate Resuscitation"
            alert_tier = "CRITICAL PRE-ALERT (RED)"
            target_mins = 0
            resus_action = "Immediate Resuscitation Bay 1 Activation • Trauma / Cardiac Team Standby"
        elif (
            news2 >= 7
            or spo2 < 91
            or sbp < 90
            or rr >= 30
            or hr >= 130
            or "stemi" in complaint_lower
            or "stroke" in complaint_lower
            or "sepsis" in complaint_lower
        ):
            mts_category = 2
            mts_name = "Amber / Very Urgent"
            alert_tier = "URGENT PRE-ALERT (AMBER)"
            target_mins = 10
            resus_action = "Acute Resus / High-Dependency Cubicle Prepared • Senior Clinician Assigned"
        elif news2 >= 5 or spo2 <= 93 or sbp <= 100 or rr >= 25 or hr >= 110:
            mts_category = 3
            mts_name = "Yellow / Urgent"
            alert_tier = "PRIORITY TRANSPORT (YELLOW)"
            target_mins = 60
            resus_action = "ED Majors Cubicle Assigned • Immediate Nursing Assessment"
        elif news2 >= 1:
            mts_category = 4
            mts_name = "Green / Standard"
            alert_tier = "STANDARD TRANSPORT (GREEN)"
            target_mins = 120
            resus_action = "Routine ED Triage Stream • Ambulatory / Minors Assessment"
        else:
            mts_category = 5
            mts_name = "Blue / Non-Urgent"
            alert_tier = "NON-URGENT TRANSPORT (BLUE)"
            target_mins = 240
            resus_action = "ED Primary Care Stream / Minor Injuries Unit"

        requires_prealert = mts_category in (1, 2) or news2 >= 7

        return {
            "mts_category": mts_category,
            "mts_name": mts_name,
            "news2_score": news2,
            "requires_ed_prealert": requires_prealert,
            "alert_tier": alert_tier,
            "target_mins": target_mins,
            "resus_action": resus_action,
            "norm_vitals": norm_vitals,
        }

    def run(self, context: Optional[Dict[str, Any]] = None, **kwargs) -> AgentExecutionResult:
        context = context or {}
        vitals = context.get("vitals") or kwargs.get("vitals") or {"sbp": 85, "hr": 128, "spo2": 89, "rr": 28, "temp": 39.2}
        complaint = context.get("chief_complaint") or context.get("complaint") or kwargs.get("complaint") or "Acute respiratory distress and hypotension"
        eta_minutes = int(context.get("eta_minutes", 12))
        patient_id = context.get("patient_id") or "Unidentified-PreHospital-1"
        patient_name = context.get("patient_name") or "Pre-Hospital Casualty"
        receiving_ed = context.get("receiving_ed") or "Mater Misericordiae University Hospital ED"

        alert_res = self.calculate_alert_priority(vitals, complaint)
        norm_vitals = alert_res["norm_vitals"]

        findings = [
            {
                "category": "cardiovascular",
                "parameter": "Heart Rate",
                "field_value": f"{int(norm_vitals['heart_rate'])} bpm",
                "triage_assessment": "Tachycardia (High Risk)" if norm_vitals['heart_rate'] >= 110 else ("Bradycardia" if norm_vitals['heart_rate'] < 50 else "Normal Range"),
                "receiving_action": "Continuous 12-Lead ECG & Defibrillator Standby" if norm_vitals['heart_rate'] >= 110 else "Routine Cardiac Monitoring",
                "status": "warning" if norm_vitals['heart_rate'] >= 110 or norm_vitals['heart_rate'] < 50 else "pass",
            },
            {
                "category": "hemodynamics",
                "parameter": "Blood Pressure",
                "field_value": f"{int(norm_vitals['systolic_bp'])}/{int(norm_vitals['diastolic_bp'])} mmHg",
                "triage_assessment": "Severe Hypotension (NEWS2 +3)" if norm_vitals['systolic_bp'] < 90 else ("Borderline Low (NEWS2 +1)" if norm_vitals['systolic_bp'] < 100 else "Hemodynamically Stable"),
                "receiving_action": "Large-Bore IV Access (16G) & 500mL Warm Saline Bolus Staged" if norm_vitals['systolic_bp'] < 90 else "Standard IV Cannulation",
                "status": "warning" if norm_vitals['systolic_bp'] < 90 else "pass",
            },
            {
                "category": "respiratory",
                "parameter": "Oxygen Saturation (SpO2)",
                "field_value": f"{int(norm_vitals['spo2'])}% (Field Air)",
                "triage_assessment": "Critical Hypoxemia (NEWS2 +3)" if norm_vitals['spo2'] < 92 else ("Mild Hypoxia (NEWS2 +1)" if norm_vitals['spo2'] < 95 else "Adequate Oxygenation"),
                "receiving_action": "High-Flow Non-Rebreather Mask (15 L/min) / CPAP Prepared" if norm_vitals['spo2'] < 92 else "Nasal Cannula 2 L/min PRN",
                "status": "warning" if norm_vitals['spo2'] < 92 else "pass",
            },
            {
                "category": "ventilation",
                "parameter": "Respiratory Rate",
                "field_value": f"{int(norm_vitals['respiratory_rate'])} breaths/min",
                "triage_assessment": "Severe Tachypnea (NEWS2 +3)" if norm_vitals['respiratory_rate'] >= 25 else ("Tachypnea (NEWS2 +1)" if norm_vitals['respiratory_rate'] >= 21 else "Eupneic"),
                "receiving_action": "Emergency Airway Equipment & Bag-Valve-Mask Ready" if norm_vitals['respiratory_rate'] >= 25 else "Continuous Respiratory Rate Tracking",
                "status": "warning" if norm_vitals['respiratory_rate'] >= 25 else "pass",
            },
            {
                "category": "thermoregulation",
                "parameter": "Body Temperature",
                "field_value": f"{norm_vitals['temperature']:.1f} °C",
                "triage_assessment": "Pyrexia / Sepsis Flag" if norm_vitals['temperature'] >= 38.0 else ("Hypothermia" if norm_vitals['temperature'] < 36.0 else "Normothermic"),
                "receiving_action": "Blood Cultures & Sepsis Pathway Staged" if norm_vitals['temperature'] >= 38.0 else "Thermal Blanket Comfort",
                "status": "warning" if norm_vitals['temperature'] >= 38.0 or norm_vitals['temperature'] < 36.0 else "pass",
            },
            {
                "category": "clinical_acuity",
                "parameter": "Presenting Chief Complaint",
                "field_value": str(complaint),
                "triage_assessment": f"Manchester Triage: {alert_res['mts_name']} (Target: {alert_res['target_mins']} min)",
                "receiving_action": str(alert_res['resus_action']),
                "status": "warning" if alert_res["requires_ed_prealert"] else "pass",
            },
        ]

        if alert_res["requires_ed_prealert"]:
            status = "warning"
            summary = (
                f"Emergency Pre-Alert Agent: Dispatched {alert_res['alert_tier']} to {receiving_ed} for {patient_name} ({patient_id}). "
                f"MTS Category {alert_res['mts_category']} ({alert_res['mts_name']}), NEWS2: {alert_res['news2_score']}/20, ETA: {eta_minutes}m."
            )
        else:
            status = "pass"
            summary = (
                f"Emergency Pre-Alert Agent: {patient_name} ({patient_id}) in stable transit (ROUTINE GREEN) to {receiving_ed}. "
                f"MTS Category {alert_res['mts_category']}, NEWS2: {alert_res['news2_score']}/20, ETA: {eta_minutes}m."
            )

        telemetry = {
            **alert_res,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "receiving_ed": receiving_ed,
            "eta_minutes": eta_minutes,
            "presenting_complaint": complaint,
            "vitals_snapshot": norm_vitals,
            "dispatch_timestamp": datetime.now(timezone.utc).isoformat(),
            "egress_mode": "Local Sovereign Gateway (Air-Gapped Simulation • Zero External Leakage)",
            "fhir_resource_type": "Encounter",
            "fhir_class": "EMER",
        }

        return AgentExecutionResult(
            agent_id=self.id,
            status=status,
            summary=summary,
            findings=findings,
            telemetry=telemetry,
        )
