"""Unified Agent Execution Engine for SlainteTech AI Security Labs.

Provides a single canonical entrypoint for running any agent:
- Synchronously from web handlers / copilots
- Interactively via CLI (`python -m agents.cli run <agent_id>`)
- Asynchronously via background worker loop
"""
import sys
import logging
from typing import Dict, Any, Optional, List
from agents.base import BaseAgent, AgentExecutionResult
from agents.registry import AGENTS_CATALOG, get_agent_by_id, get_agent_instance

logger = logging.getLogger("SlainteAgentsRunner")


def run_agent(agent_id: str, context: Optional[Dict[str, Any]] = None, **kwargs) -> AgentExecutionResult:
    """Execute any registered agent through the unified BaseAgent interface."""
    agent = get_agent_instance(agent_id)
    if not agent:
        return AgentExecutionResult(
            agent_id=agent_id,
            status="fail",
            summary=f"Unknown agent identifier: '{agent_id}'",
            findings=[{"error": f"Agent '{agent_id}' not found in registry"}],
            telemetry={"registered_agents": [a["id"] for a in AGENTS_CATALOG]},
        )
    return agent.run(context=context, **kwargs)


def health_check_all() -> Dict[str, bool]:
    """Run health checks across all registered agents."""
    results = {}
    for meta in AGENTS_CATALOG:
        ag = get_agent_instance(meta["id"])
        results[meta["id"]] = ag.health_check() if ag else False
    return results


def run_all_governance_agents() -> List[AgentExecutionResult]:
    """Execute a complete audit & security sweep across all governance agents."""
    gov_agents = [a["id"] for a in AGENTS_CATALOG if a.get("fleet") == "governance"]
    results = []
    for aid in gov_agents:
        results.append(run_agent(aid))
    return results


def run_all_clinical_agents(patient_context: Optional[Dict[str, Any]] = None) -> List[AgentExecutionResult]:
    """Execute a complete evaluation sweep across clinical copilot agents."""
    clin_agents = [a["id"] for a in AGENTS_CATALOG if a.get("fleet") == "clinical"]
    results = []
    for aid in clin_agents:
        results.append(run_agent(aid, context=patient_context))
    return results
