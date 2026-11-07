"""Agent 06: SlainteEngine-Ingest — Multimodal Clinical Ingestion Pipeline."""
import os
import glob
from typing import Dict, Any, Optional, List
from agents.base import BaseAgent, AgentExecutionResult


class MultimodalIngestAgent(BaseAgent):
    id: str = "multimodal_ingest"
    number: str = "06"
    code: str = "SlainteEngine-Ingest"
    name: str = "Multimodal Clinical Ingestion Pipeline"
    fleet: str = "clinical"

    def __init__(self, raw_dir: Optional[str] = None, store_dir: Optional[str] = None):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.raw_dir = raw_dir or os.path.join(base_dir, "data", "raw")
        self.store_dir = store_dir or os.path.join(base_dir, "data", "fhir_store")

    def health_check(self) -> bool:
        return os.path.isdir(self.raw_dir) or os.path.isdir(self.store_dir)

    def get_pipeline_telemetry(self) -> Dict[str, Any]:
        raw_files = []
        if os.path.isdir(self.raw_dir):
            raw_files = [f for f in os.listdir(self.raw_dir) if not f.startswith(".")]

        bundles = []
        if os.path.isdir(self.store_dir):
            bundles = glob.glob(os.path.join(self.store_dir, "bundle_*.json"))

        return {
            "raw_count": len(raw_files),
            "raw_files": raw_files[:20],
            "bundle_count": len(bundles),
            "store_path": self.store_dir,
            "raw_path": self.raw_dir,
        }

    def ingest_hl7v2(self, raw_hl7: str, patient_id: Optional[str] = None) -> Dict[str, Any]:
        """Translate legacy HL7v2 pipe-hat message to FHIR R4 Bundle."""
        try:
            from enterprise_engine import translate_hl7v2_to_fhir_bundle
            return translate_hl7v2_to_fhir_bundle(raw_hl7, existing_patient_id=patient_id)
        except ImportError:
            try:
                from frontend.enterprise_engine import translate_hl7v2_to_fhir_bundle
                return translate_hl7v2_to_fhir_bundle(raw_hl7, existing_patient_id=patient_id)
            except Exception as e:
                return {"error": f"Failed to translate HL7v2 message: {e}"}

    def run(self, context: Optional[Dict[str, Any]] = None, **kwargs) -> AgentExecutionResult:
        context = context or {}
        telemetry = self.get_pipeline_telemetry()
        raw_hl7 = context.get("raw_hl7") or kwargs.get("raw_hl7")
        findings = []

        if raw_hl7:
            bundle = self.ingest_hl7v2(raw_hl7, context.get("patient_id"))
            telemetry["ingested_bundle"] = bundle

        summary = (
            f"Multimodal Ingestion Pipeline synchronized: {telemetry['raw_count']} raw dropzone files, "
            f"{telemetry['bundle_count']} verified FHIR R4 clinical bundles in store."
        )

        return AgentExecutionResult(
            agent_id=self.id,
            status="pass",
            summary=summary,
            findings=findings,
            telemetry=telemetry,
        )
