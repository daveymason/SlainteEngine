"""Command-Line Interface for SlainteTech AI Security Labs Agents Fleet."""
import argparse
import json
import sys
from agents.registry import AGENTS_CATALOG, get_agent_by_id
from agents.runner import run_agent, health_check_all, run_all_governance_agents


def main():
    parser = argparse.ArgumentParser(description="Slainte-Engine Unified Agent Fleet CLI")
    subparsers = parser.add_subparsers(dest="command", help="Agent command to execute")

    # Command: list
    subparsers.add_parser("list", help="List all registered agents and their statuses")

    # Command: health
    subparsers.add_parser("health", help="Check prerequisite health across all agents")

    # Command: run <agent_id>
    run_parser = subparsers.add_parser("run", help="Run a specific agent by ID, code, or number")
    run_parser.add_argument("agent_id", help="Agent identifier (e.g. '01', 'bola_redteam', 'clinic_onboarding')")
    run_parser.add_argument("--context", help="Optional JSON string of input context", default=None)

    # Command: audit
    subparsers.add_parser("audit", help="Run full governance and security sweep")

    args = parser.parse_args()

    if args.command == "list":
        print(f"\n{'#':<4} {'ID':<22} {'CODE':<24} {'FLEET':<12} {'NAME'}")
        print("-" * 80)
        for a in AGENTS_CATALOG:
            print(f"{a['number']:<4} {a['id']:<22} {a['code']:<24} {a['fleet']:<12} {a['name']}")
        print(f"\nTotal Registered Agents: {len(AGENTS_CATALOG)}\n")

    elif args.command == "health":
        statuses = health_check_all()
        print(f"\n{'ID':<24} {'HEALTH'}")
        print("-" * 35)
        for aid, ok in statuses.items():
            print(f"{aid:<24} {'[OK]' if ok else '[DEGRADED]'}")
        print()

    elif args.command == "run":
        ctx = None
        if args.context:
            try:
                ctx = json.loads(args.context)
            except Exception as e:
                print(f"Error parsing context JSON: {e}", file=sys.stderr)
                sys.exit(1)
        res = run_agent(args.agent_id, context=ctx)
        print(f"\n[AGENT {res.agent_id.upper()} -> {res.status.upper()}]")
        print(f"Summary: {res.summary}")
        if res.findings:
            print("\nFindings:")
            for f in res.findings:
                print(f"  - {f}")
        print()

    elif args.command == "audit":
        print("\nExecuting comprehensive governance and security sweep...")
        results = run_all_governance_agents()
        for r in results:
            print(f"[{r.status.upper():<7}] {r.agent_id:<22} -> {r.summary}")
        print(f"\nCompleted audit sweep across {len(results)} governance agents.\n")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
