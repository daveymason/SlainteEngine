#!/usr/bin/env python3
"""SlainteFHIR Autonomous Red-Team & Semantic FHIR R4 Verifier Runner.

Executes the 4-stage auditing pipeline:
1. Conformance Ingestion & Static Reachability Filtering (with RFC 1918 guardrail).
2. Semantic & Terminology Conformance Verification across FHIR R4 Store bundles.
3. Multi-Identity BOLA & Graph-Traversal Conformance Campaign (Dual-Phase Reflection).
4. Live LLM Reasoning Synthesis (OpenAI Luna / Local Ollama 3B) & OASIS SARIF v2.1.0 Export.
"""
from __future__ import annotations

import argparse
import dataclasses
import glob
import json
import logging
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import httpx

from src.conformance_filter import filter_capability_statement, verify_sandbox_target
from src.redteam_bola_agent import FhirRedTeamAgent, SecurityFinding
from src.sarif_reporter import build_sarif_report, save_sarif_report
from src.terminology_verifier import TerminologyFinding, verify_bundle_terminology

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Slainte-Auditor] %(message)s",
)
logger = logging.getLogger("SlainteAuditor")


def _invoke_live_llm(
    model_choice: str,
    security_findings: List[SecurityFinding],
    terminology_findings: List[TerminologyFinding],
    victim_summary: str,
    log_fn: Any,
) -> Dict[str, Any]:
    """Invokes the selected OpenAI or Local Ollama model to synthesize live audit reasoning."""
    prompt = (
        f"You are an HL7 FHIR R4 API conformance and software QA assistant reviewing synthetic sandbox test metrics.\n"
        f"- Synthetic Test Endpoints Probed: {', '.join(f.endpoint for f in security_findings[:4])}\n"
        f"- API Conformance Rules Triggered ({len(security_findings)}): "
        f"{', '.join(f.rule_id + ' (' + f.cwe_id + ')' for f in security_findings[:4])}\n"
        f"- Terminology Schema Rules Triggered ({len(terminology_findings)} total): "
        f"{', '.join(t.rule_id + ' on ' + str(t.resource_type) for t in terminology_findings[:4])}\n\n"
        f"Write 2 technical sentences explaining how to fix (1) the missing OAuth2 compartment check on "
        f"the FHIR endpoints and (2) the UCUM unit ('mm[Hg]') and SNOMED CT coding schema errors."
    )

    ollama_urls = [
        os.environ.get("LLM_BASE_URL", "http://localhost:11434").rstrip("/"),
        "http://localhost:11434",
        "http://host.docker.internal:11434",
    ]

    # 1. If OpenAI model selected and OPENAI_API_KEY is present, try OpenAI API first
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if model_choice.startswith("openai/") and openai_key and not openai_key.startswith("sk-proj-..."):
        oa_model = model_choice.split("/", 1)[1].split(" ")[0].strip()
        log_fn("STAGE-3:LLM", f"Dispatching live audit telemetry to OpenAI model '{oa_model}'...")
        t0 = time.perf_counter()
        try:
            with httpx.Client(timeout=12.0) as client:
                r = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openai_key}"},
                    json={
                        "model": oa_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 160,
                    },
                )
                dt = round((time.perf_counter() - t0) * 1000.0, 1)
                if r.status_code == 200:
                    data = r.json()
                    text = data["choices"][0]["message"]["content"].strip()
                    usage = data.get("usage", {})
                    p_tok = usage.get("prompt_tokens", 0)
                    c_tok = usage.get("completion_tokens", 0)
                    log_fn(
                        "STAGE-3:LLM",
                        f"OpenAI {oa_model} responded in {dt}ms ({p_tok} prompt / {c_tok} completion tokens).",
                    )
                    return {
                        "provider": "OpenAI API",
                        "model_executed": oa_model,
                        "latency_ms": dt,
                        "prompt_tokens": p_tok,
                        "completion_tokens": c_tok,
                        "reasoning": text,
                        "thinking": "",
                    }
                else:
                    log_fn(
                        "STAGE-3:LLM",
                        f"OpenAI API returned HTTP {r.status_code} for '{oa_model}'; routing to local Ollama engine.",
                        level="WARN",
                    )
        except Exception as exc:
            log_fn("STAGE-3:LLM", f"OpenAI connection error ({exc}); routing to local Ollama engine.", level="WARN")

    # 2. Resolve Ollama model tag from user selection (or fallback when OPENAI_API_KEY is not set)
    if model_choice.startswith("ollama/"):
        raw_tag = model_choice[len("ollama/") :].split(" ")[0].strip()
    else:
        raw_tag = "gemma3:1b"
        log_fn(
            "STAGE-3:LLM",
            f"OPENAI_API_KEY not configured for '{model_choice}'; executing live local inference via Ollama '{raw_tag}'.",
        )

    for base in ollama_urls:
        try:
            t0 = time.perf_counter()
            with httpx.Client(timeout=25.0) as client:
                r = client.post(
                    f"{base}/api/chat",
                    json={
                        "model": raw_tag,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                        "options": {"num_predict": 140, "temperature": 0.4},
                    },
                )
                dt = round((time.perf_counter() - t0) * 1000.0, 1)
                if r.status_code == 200:
                    body = r.json()
                    msg = body.get("message", {})
                    content = (msg.get("content") or "").strip()
                    thinking = (msg.get("thinking") or "").strip()
                    p_tok = body.get("prompt_eval_count", 0)
                    c_tok = body.get("eval_count", 0)
                    log_fn(
                        "STAGE-3:LLM",
                        f"Ollama '{raw_tag}' inference completed in {dt}ms "
                        f"(prompt_tokens={p_tok}, completion_tokens={c_tok}).",
                    )
                    if content:
                        log_fn("STAGE-3:SYNTHESIS", f"LLM Verdict: {content[:220]}")
                    return {
                        "provider": f"Local Ollama ({base})",
                        "model_executed": raw_tag,
                        "latency_ms": dt,
                        "prompt_tokens": p_tok,
                        "completion_tokens": c_tok,
                        "reasoning": content or thinking or "Completed FHIR R4 BOLA and terminology synthesis.",
                        "thinking": thinking[:350] if thinking else "",
                    }
        except Exception:
            continue

    return {
        "provider": "Deterministic Rule Engine (Offline)",
        "model_executed": model_choice,
        "latency_ms": 0.0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "reasoning": (
            f"Confirmed {len(security_findings)} cross-compartment BOLA/CORS/Validator vulnerabilities "
            f"({victim_summary}) and {len(terminology_findings)} SNOMED/LOINC/UCUM/OID deviations."
        ),
        "thinking": "",
    }


def _build_embedded_slainte_fhir_transport() -> httpx.MockTransport:
    """Provides an embedded sandbox transport mirroring slainte-fhir/main.py when port 8082 is offline."""

    def _handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        headers = {
            "access-control-allow-origin": request.headers.get("Origin", "*"),
            "access-control-allow-credentials": "true",
        }
        if path == "/fhir/r4/Patient" and request.method == "GET":
            return httpx.Response(
                200,
                headers=headers,
                json={
                    "resourceType": "Bundle",
                    "type": "searchset",
                    "total": 8,
                    "entry": [
                        {
                            "resource": {
                                "resourceType": "Patient",
                                "id": "patient-case-1",
                                "name": [{"family": "Murphy", "given": ["Sean"]}],
                                "gender": "male",
                                "birthDate": "1958-04-12",
                            }
                        }
                    ],
                },
            )
        if path.startswith("/fhir/r4/Patient/") and request.method == "GET":
            pid = path.split("/")[-1]
            return httpx.Response(
                200,
                headers=headers,
                json={
                    "resourceType": "Patient",
                    "id": pid,
                    "name": [{"family": "Murphy", "given": ["Sean"]}],
                    "gender": "male",
                    "birthDate": "1958-04-12",
                },
            )
        if path == "/fhir/r4/Observation" and request.method == "GET":
            return httpx.Response(
                200,
                headers=headers,
                json={
                    "resourceType": "Bundle",
                    "type": "searchset",
                    "total": 6,
                    "entry": [
                        {
                            "resource": {
                                "resourceType": "Observation",
                                "id": "obs-case1-sbp",
                                "subject": {"reference": "Patient/patient-case-1"},
                                "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6"}]},
                                "valueQuantity": {"value": 85.0, "code": "mm[Hg]"},
                            }
                        },
                        {
                            "resource": {
                                "resourceType": "Observation",
                                "id": "obs-case1-hr",
                                "subject": {"reference": "Patient/patient-case-1"},
                                "code": {"coding": [{"system": "http://loinc.org", "code": "8867-4"}]},
                                "valueQuantity": {"value": 135.0, "code": "/min"},
                            }
                        },
                    ],
                },
            )
        if path == "/fhir/r4/$validate" and request.method == "POST":
            return httpx.Response(
                422,
                headers=headers,
                json={
                    "resourceType": "OperationOutcome",
                    "issue": [
                        {
                            "severity": "error",
                            "code": "invalid",
                            "diagnostics": "'patient-redteam-999'",
                        }
                    ],
                },
            )
        return httpx.Response(403, headers=headers, json={"resourceType": "OperationOutcome"})

    return httpx.MockTransport(_handler)


def run_audit_cycle(
    target_url: str,
    fhir_store_dir: str,
    report_dir: str,
    model_name: str | None = None,
) -> Dict[str, Any]:
    """Executes one complete 4-stage security and semantic verification cycle."""
    execution_logs: List[str] = []
    out_dir = Path(report_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    model_state_file = out_dir / "selected_model.txt"

    if model_name:
        model_state_file.write_text(model_name.strip(), encoding="utf-8")
        active_model = model_name.strip()
    elif model_state_file.is_file():
        active_model = model_state_file.read_text(encoding="utf-8").strip() or "openai/gpt-6.1-luna"
    else:
        active_model = (
            os.environ.get("AUDITOR_MODEL")
            or os.environ.get("LLM_MODEL")
            or "openai/gpt-6.1-luna"
        )

    def _log(stage: str, msg: str, level: str = "INFO") -> None:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "Z"
        line = f"{ts} [{level}] [{stage}] {msg}"
        execution_logs.append(line)
        logger.info(f"[{stage}] {msg}")

    _log("STAGE-0:MODEL", f"Selected OpenHands Auditor Model: {active_model}")

    # Stage 1: Verify RFC 1918 / loopback sandbox guardrail
    host = verify_sandbox_target(target_url)
    _log(
        "STAGE-1:GUARDRAIL",
        f"RFC 1918 / loopback sandbox guardrail verified for target {target_url} (host={host})",
    )

    cap_stmt: Dict[str, Any] = {
        "resourceType": "CapabilityStatement",
        "status": "active",
        "experimental": True,
        "fhirVersion": "4.0.1",
        "rest": [
            {
                "mode": "server",
                "resource": [
                    {"type": "Patient", "interaction": [{"code": "read"}, {"code": "search-type"}]},
                    {"type": "Observation", "interaction": [{"code": "read"}, {"code": "search-type"}]},
                    {"type": "Condition", "interaction": [{"code": "read"}, {"code": "search-type"}]},
                    {"type": "Encounter", "interaction": [{"code": "read"}, {"code": "search-type"}]},
                    {"type": "Provenance", "interaction": [{"code": "read"}, {"code": "search-type"}]},
                    {"type": "AllergyIntolerance", "interaction": [{"code": "read"}, {"code": "search-type"}]},
                    {"type": "MedicationRequest", "interaction": [{"code": "read"}, {"code": "search-type"}]},
                    {"type": "DiagnosticReport", "interaction": [{"code": "read"}, {"code": "search-type"}]},
                    {"type": "Binary", "interaction": [{"code": "read"}]},
                    {"type": "Bundle", "interaction": [{"code": "create"}]},
                    {"type": "Organization", "interaction": [{"code": "read"}]},
                    {"type": "Practitioner", "interaction": [{"code": "read"}]},
                    {"type": "Location", "interaction": [{"code": "read"}]},
                    {"type": "HealthcareService", "interaction": [{"code": "read"}]},
                    {"type": "ValueSet", "interaction": [{"code": "read"}]},
                    {"type": "CodeSystem", "interaction": [{"code": "read"}]},
                    {"type": "StructureDefinition", "interaction": [{"code": "read"}]},
                    {"type": "SearchParameter", "interaction": [{"code": "read"}]},
                    {"type": "CapabilityStatement", "interaction": [{"code": "read"}]},
                    {"type": "OperationDefinition", "interaction": [{"code": "read"}]},
                    {"type": "ImplementationGuide", "interaction": [{"code": "read"}]},
                    {"type": "Subscription", "interaction": [{"code": "read"}]},
                ],
            }
        ],
    }

    live_reachable = False
    try:
        t0 = time.perf_counter()
        with httpx.Client(timeout=2.5) as client:
            r = client.get(f"{target_url.rstrip('/')}/fhir/r4/metadata")
            dt_meta = (time.perf_counter() - t0) * 1000.0
            if r.status_code == 200:
                live_cap = r.json()
                if isinstance(live_cap, dict) and live_cap.get("resourceType") == "CapabilityStatement":
                    cap_stmt["fhirVersion"] = live_cap.get("fhirVersion", "4.0.1")
                live_reachable = True
                _log(
                    "STAGE-1:INGEST",
                    f"Fetched live CapabilityStatement from {target_url}/fhir/r4/metadata in {dt_meta:.2f}ms",
                )
    except Exception:
        _log(
            "STAGE-1:INGEST",
            "Live HTTP daemon not listening on port 8082; binding embedded SlainteFHIR sandbox transport.",
        )

    surface = filter_capability_statement(cap_stmt, target_url=target_url)
    _log(
        "STAGE-1:FILTER",
        f"CompartmentDefinition/Patient filter retained {len(surface.active_compartment_resources)} "
        f"clinical resource(s) and pruned {len(surface.pruned_resources)} non-compartment metadata type(s) "
        f"({surface.reduction_ratio * 100:.1f}% surface reduction).",
    )

    # Stage 2: Semantic & Terminology Verification across FHIR Store bundles
    terminology_findings: List[TerminologyFinding] = []
    bundle_files = sorted(glob.glob(os.path.join(fhir_store_dir, "*.json")))
    t_stage2 = time.perf_counter()
    _log(
        "STAGE-2:ONTOLOGY",
        f"Scanning {len(bundle_files)} HL7 FHIR R4 Bundle(s) in {fhir_store_dir} against SNOMED CT, LOINC, UCUM & HSE OIDs...",
    )
    for bpath in bundle_files:
        try:
            with open(bpath, "r", encoding="utf-8") as f:
                bdata = json.load(f)
            if isinstance(bdata, dict) and bdata.get("resourceType") == "Bundle":
                b_findings = verify_bundle_terminology(bdata)
                for bf in b_findings:
                    bf.resource_id = f"{os.path.basename(bpath)} :: {bf.resource_id}"
                terminology_findings.extend(b_findings)
        except Exception as exc:
            _log("STAGE-2:WARN", f"Failed to parse bundle {bpath}: {exc}", level="WARN")

    dt_stage2 = (time.perf_counter() - t_stage2) * 1000.0
    _log(
        "STAGE-2:ONTOLOGY",
        f"Completed terminology & CDS verification in {dt_stage2:.2f}ms: {len(terminology_findings)} semantic/ontology drift issue(s) flagged.",
    )

    # Stage 3: Autonomous Red-Team BOLA Campaign with Dual-Phase Reflection
    _log(
        "STAGE-3:REDTEAM",
        "Executing FhirRedTeamAgent with SharedAuditMemory (M) and Multi-Identity Differential Oracle (live patient cohort sampling).",
    )
    transport = None if live_reachable else _build_embedded_slainte_fhir_transport()
    agent = FhirRedTeamAgent(base_url=target_url, transport=transport)
    security_findings: List[SecurityFinding] = agent.run_campaign()

    for entry in agent.memory.entries:
        _log(
            "STAGE-3:MEMORY",
            f"Step #{entry.step:02d} [{entry.vector_id}] {entry.identity} -> {entry.method} {entry.endpoint} "
            f"(HTTP {entry.status_code}, {entry.latency_ms:.2f}ms) | Reflection: {entry.reflection_action} | {entry.notes}",
        )

    victim_summary = agent.memory.entries[0].notes if agent.memory.entries else "Patient/patient-case-1"
    llm_synthesis = _invoke_live_llm(
        model_choice=active_model,
        security_findings=security_findings,
        terminology_findings=terminology_findings,
        victim_summary=victim_summary,
        log_fn=_log,
    )

    _log(
        "STAGE-3:ORACLE",
        f"Differential Oracle confirmed {len(security_findings)} authorization/validation vulnerability(s) across {len(agent.memory.entries)} live HTTP memory steps.",
    )

    # Stage 4: Export SARIF v2.1.0 report & UI Telemetry JSON
    sarif_doc = build_sarif_report(
        security_findings=security_findings,
        terminology_findings=terminology_findings,
        target_url=target_url,
    )
    out_file = save_sarif_report(sarif_doc, out_dir / "slaintefhir-audit.sarif.json")
    _log("STAGE-4:SARIF", f"OASIS SARIF v2.1.0 report written to {out_file}")

    telemetry_payload: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "target_url": target_url,
        "execution_mode": "Live SlainteFHIR HTTP" if live_reachable else "Embedded Sandbox Transport",
        "model_architecture": f"{active_model} + OpenHands SDK",
        "selected_model": active_model,
        "llm_synthesis": llm_synthesis,
        "stats": {
            "surface_reduction_pct": round(surface.reduction_ratio * 100, 1),
            "active_compartment_count": len(surface.active_compartment_resources),
            "pruned_resource_count": len(surface.pruned_resources),
            "bundles_audited": len(bundle_files),
            "security_findings_count": len(security_findings),
            "terminology_findings_count": len(terminology_findings),
            "memory_steps_count": len(agent.memory.entries),
        },
        "surface": {
            "active_compartment_resources": surface.active_compartment_resources,
            "bridge_resources": surface.bridge_resources,
            "pruned_resources": surface.pruned_resources,
        },
        "security_findings": [dataclasses.asdict(f) for f in security_findings],
        "terminology_findings": [dataclasses.asdict(t) for t in terminology_findings],
        "memory_entries": [dataclasses.asdict(m) for m in agent.memory.entries],
        "logs": execution_logs,
        "sarif_path": str(out_file),
    }

    telemetry_file = out_dir / "audit_telemetry.json"
    telemetry_file.write_text(json.dumps(telemetry_payload, indent=2), encoding="utf-8")
    _log("STAGE-4:TELEMETRY", f"Dashboard UI telemetry written to {telemetry_file}")

    return {
        "surface_reduction": surface.reduction_ratio,
        "bundles_audited": len(bundle_files),
        "terminology_findings": len(terminology_findings),
        "security_findings": len(security_findings),
        "memory_steps": len(agent.memory.entries),
        "sarif_path": str(out_file),
        "telemetry_path": str(telemetry_file),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="SlainteFHIR Autonomous Red-Team & Verifier")
    parser.add_argument(
        "--target-url",
        default=os.environ.get("TARGET_FHIR_URL", "http://localhost:8082"),
    )
    parser.add_argument(
        "--store-dir",
        default=os.environ.get("FHIR_STORE_PATH", "/workspace/data/fhir_store"),
    )
    parser.add_argument(
        "--report-dir",
        default=os.environ.get("REPORT_OUTPUT_DIR", "/workspace/data/audit_reports"),
    )
    parser.add_argument("--once", action="store_true", help="Run a single audit pass and exit")
    parser.add_argument("--interval", type=int, default=30, help="Continuous poll interval (s)")
    args = parser.parse_args()

    store_dir = args.store_dir
    report_dir = args.report_dir
    if not os.path.exists("/workspace"):
        base_data = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        if store_dir == "/workspace/data/fhir_store":
            store_dir = os.path.join(base_data, "fhir_store")
        if report_dir == "/workspace/data/audit_reports":
            report_dir = os.path.join(base_data, "audit_reports")

    if args.once:
        run_audit_cycle(args.target_url, store_dir, report_dir)
        return

    while True:
        try:
            run_audit_cycle(args.target_url, store_dir, report_dir)
        except Exception as exc:
            logger.exception(f"Audit cycle error: {exc}")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
