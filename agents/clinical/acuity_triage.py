"""Agent 09: SlainteDx-Triage — Acuity Triage & NEWS2 Deterioration Engine."""
import os
import json
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
                # Deterministic calculation fallback
                rr = float(vitals.get("rr") or 18)
                spo2 = float(vitals.get("spo2") or 98)
                sbp = float(vitals.get("sbp") or 120)
                hr = float(vitals.get("hr") or 72)
                temp = float(vitals.get("temp") or 36.8)

                n_score = 0
                if rr <= 8 or rr >= 25: n_score += 3
                elif rr >= 21: n_score += 2
                elif rr <= 11: n_score += 1

                if spo2 <= 91: n_score += 3
                elif spo2 <= 93: n_score += 2
                elif spo2 <= 95: n_score += 1

                if sbp <= 90: n_score += 3
                elif sbp <= 100: n_score += 2
                elif sbp <= 110: n_score += 1

                if hr <= 40 or hr >= 131: n_score += 3
                elif hr >= 111: n_score += 2
                elif hr <= 50 or hr >= 91: n_score += 1

                if temp <= 35.0: n_score += 3
                elif temp >= 39.1: n_score += 2
                elif (temp <= 36.0 or temp >= 38.1): n_score += 1

                if n_score >= 7: n_tier = "High Risk (Critical)"
                elif n_score >= 5: n_tier = "Medium Risk (Urgent)"
                else: n_tier = "Low Risk (Standard)"

                mts_cat = 1 if n_score >= 9 else (2 if n_score >= 7 else (3 if n_score >= 4 else (4 if n_score >= 2 else 5)))
                mts_names = {1: "Immediate / Resuscitation", 2: "Very Urgent", 3: "Urgent", 4: "Standard", 5: "Non-Urgent"}
                mts_targets = {1: 0, 2: 10, 3: 60, 4: 120, 5: 240}

                return {
                    "news2_score": n_score,
                    "news2_tier": n_tier,
                    "breakdown": {"rr": rr, "spo2": spo2, "sbp": sbp, "hr": hr, "temp": temp},
                    "mts_cat": mts_cat,
                    "mts_name": mts_names.get(mts_cat, "Urgent"),
                    "mts_target": mts_targets.get(mts_cat, 60),
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
        patient_id = context.get("patient_id") or kwargs.get("patient_id")
        fhir = context.get("fhir") or kwargs.get("fhir")
        fhir_store_path = context.get("fhir_store_path") or kwargs.get("fhir_store_path") or os.environ.get("FHIR_STORE_PATH")
        vitals = context.get("vitals") or kwargs.get("vitals")

        if not vitals and patient_id:
            vitals = {}
            if fhir:
                try:
                    obs_res = fhir.get("Observation", params={"patient": patient_id, "_count": 50})
                    if obs_res.ok:
                        for o in obs_res.entries:
                            cd = o.get("code", {})
                            codes = [c.get("code") for c in cd.get("coding", [])]
                            val = o.get("valueQuantity", {}).get("value")
                            if val is not None:
                                if "8480-6" in codes and "sbp" not in vitals:
                                    vitals["sbp"] = val
                                elif "8867-4" in codes and "hr" not in vitals:
                                    vitals["hr"] = val
                                elif "9279-1" in codes and "rr" not in vitals:
                                    vitals["rr"] = val
                                elif ("2708-6" in codes or "59408-5" in codes) and "spo2" not in vitals:
                                    vitals["spo2"] = val
                                elif "8310-5" in codes and "temp" not in vitals:
                                    vitals["temp"] = val
                except Exception:
                    pass

            if not vitals and fhir_store_path and os.path.isdir(fhir_store_path):
                bpath = os.path.join(fhir_store_path, f"bundle_{patient_id}.json")
                if os.path.isfile(bpath):
                    try:
                        with open(bpath, "r", encoding="utf-8") as f:
                            bdata = json.load(f)
                            for entry in bdata.get("entry", []):
                                res = entry.get("resource", {})
                                if res.get("resourceType") == "Observation":
                                    cd = res.get("code", {})
                                    codes = [c.get("code") for c in cd.get("coding", [])]
                                    val = res.get("valueQuantity", {}).get("value")
                                    if val is not None:
                                        if "8480-6" in codes and "sbp" not in vitals:
                                            vitals["sbp"] = val
                                        elif "8867-4" in codes and "hr" not in vitals:
                                            vitals["hr"] = val
                                        elif "9279-1" in codes and "rr" not in vitals:
                                            vitals["rr"] = val
                                        elif ("2708-6" in codes or "59408-5" in codes) and "spo2" not in vitals:
                                            vitals["spo2"] = val
                                        elif "8310-5" in codes and "temp" not in vitals:
                                            vitals["temp"] = val
                    except Exception:
                        pass

        if not vitals:
            vitals = {"rr": 18, "spo2": 98, "sbp": 120, "hr": 72, "temp": 36.8}

        scores = self.calculate_scores(vitals)
        scores["vitals_analyzed"] = vitals
        scores["patient_id"] = patient_id or "General Cohort"

        status = "pass"
        if scores["news2_score"] >= 7 or scores["mts_cat"] <= 2:
            status = "fail"
        elif scores["news2_score"] >= 5 or scores["mts_cat"] == 3:
            status = "warning"

        summary = (
            f"Computed MTS Category {scores['mts_cat']} ({scores['mts_name']}, target {scores['mts_target']}m) "
            f"and RCP NEWS2 Score {scores['news2_score']}/20 ({scores['news2_tier']}) "
            f"for {scores['patient_id']}."
        )

        return AgentExecutionResult(
            agent_id=self.id,
            status=status,
            summary=summary,
            findings=[scores] if status != "pass" else [],
            telemetry=scores,
        )
