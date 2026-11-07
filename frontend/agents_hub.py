"""Autonomous 11-Agent Hub Registry, Per-Agent Settings & Dedicated Agent Dashboards.

Bridges to the unified root `agents` monorepo package.
Unifies SlainteTech AI Security Labs' three agent squads:
- Squad A (SlainteShield): Security, Red-Team & Vulnerability Agents (01 BOLA, 02 FHIR, 03 CVE)
- Squad B (SlainteGov): Governance, GDPR Privacy, Immutable Audit & HIPE Revenue Agents (04 GDPR, 05 Audit, 11 Rev-Coding)
- Squad C (SlainteClinical): Clinical Intelligence, Voice Scribe & Ingestion Agents (06 Ingest, 07 Summariser, 08 Rx-Guard, 09 Triage, 10 Voice-Scribe)
"""
import os
import sys

# Ensure repository root is on sys.path so 'agents' can be imported anywhere
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from agents.registry import (
    AVAILABLE_MODELS,
    AGENTS_CATALOG,
    get_agent_by_id,
    get_all_agents_with_settings,
    save_agent_settings,
    get_agent_instance,
)
from agents.governance.cve_vulnerability import run_cve_vulnerability_scan
from agents.governance.gdpr_privacy import run_gdpr_privacy_scan
from agents.governance.immutable_audit import (
    run_immutable_audit_scan,
    verify_sqlite_immutability_live,
    build_signed_audit_snapshot,
)

__all__ = [
    'AVAILABLE_MODELS',
    'AGENTS_CATALOG',
    'get_agent_by_id',
    'get_all_agents_with_settings',
    'save_agent_settings',
    'get_agent_instance',
    'run_cve_vulnerability_scan',
    'run_gdpr_privacy_scan',
    'run_immutable_audit_scan',
    'verify_sqlite_immutability_live',
    'build_signed_audit_snapshot',
]
