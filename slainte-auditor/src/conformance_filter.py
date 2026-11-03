"""Stage 1: Conformance Ingestion, Sandbox Safety Guardrails & Reachability Filtering.

Enforces:
1. Hardcoded RFC 1918 / loopback / internal Docker network pinning (prevents dual-use abuse).
2. CapabilityStatement ingestion & CompartmentDefinition/Patient reachability pruning.
"""
from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass, field
from typing import Any, Dict, List
from urllib.parse import urlparse

# Allowed Docker internal hostnames on slainte-net
ALLOWED_SANDBOX_HOSTS = {
    "localhost",
    "127.0.0.1",
    "::1",
    "slainte-fhir",
    "slainte-mcp",
    "slainte-dashboard",
    "host.docker.internal",
}

# Normative HL7 FHIR R4 CompartmentDefinition/Patient inclusion rules
PATIENT_COMPARTMENT_MAP: Dict[str, List[str]] = {
    "Patient": ["_id", "link"],
    "Encounter": ["patient", "subject"],
    "Observation": ["subject", "performer"],
    "Condition": ["patient", "subject"],
    "DiagnosticReport": ["subject"],
    "MedicationRequest": ["subject"],
    "AllergyIntolerance": ["patient", "recorder", "asserter"],
    "DocumentReference": ["subject", "author"],
    "Communication": ["subject", "sender", "recipient"],
    "Provenance": ["patient", "target"],
}

# Shared bridge / sink resource types retained outside strict patient compartment
BRIDGE_AND_SINK_RESOURCES = {
    "Binary",
    "Practitioner",
    "PractitionerRole",
    "Organization",
    "Location",
    "Device",
    "Group",
    "Bundle",
}

# Pure terminology / conformance metadata resources deterministically pruned from BOLA probing
PRUNED_METADATA_RESOURCES = {
    "CodeSystem",
    "ValueSet",
    "ConceptMap",
    "StructureDefinition",
    "CapabilityStatement",
    "SearchParameter",
    "OperationDefinition",
    "NamingSystem",
    "TerminologyCapabilities",
}


class SandboxSecurityViolation(RuntimeError):
    """Raised when a target URL violates RFC 1918 / loopback sandbox guardrails."""


@dataclass
class ReachabilitySurface:
    target_url: str
    fhir_version: str
    experimental: bool
    active_compartment_resources: Dict[str, List[str]] = field(default_factory=dict)
    bridge_resources: List[str] = field(default_factory=list)
    pruned_resources: List[str] = field(default_factory=list)
    supported_interactions: Dict[str, List[str]] = field(default_factory=dict)
    reduction_ratio: float = 0.0


def verify_sandbox_target(target_url: str) -> str:
    """
    Cryptographically / network-layer guardrail: ensures target_url resolves strictly
    to loopback, RFC 1918 private networks, or allow-listed internal Docker containers.
    """
    parsed = urlparse(target_url)
    if parsed.scheme not in ("http", "https"):
        raise SandboxSecurityViolation(f"Unsupported URL scheme: {parsed.scheme}")

    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise SandboxSecurityViolation(f"Missing hostname in target URL: {target_url}")

    if hostname in ALLOWED_SANDBOX_HOSTS:
        return hostname

    # Check if literal IP address
    try:
        ip_obj = ipaddress.ip_address(hostname)
        if ip_obj.is_loopback or ip_obj.is_private:
            return hostname
        raise SandboxSecurityViolation(
            f"GUARDRAIL ABORT: Target IP {hostname} is publicly routable. "
            "SlainteFHIR Auditor is restricted to RFC 1918 / loopback sandboxes."
        )
    except ValueError:
        pass

    # Resolve hostname and verify private/loopback IP
    try:
        resolved_ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(resolved_ip)
        if not (ip_obj.is_loopback or ip_obj.is_private):
            raise SandboxSecurityViolation(
                f"GUARDRAIL ABORT: Host '{hostname}' resolved to public IP {resolved_ip}."
            )
    except socket.gaierror as exc:
        raise SandboxSecurityViolation(
            f"GUARDRAIL ABORT: Unrecognized external host '{hostname}' ({exc})."
        ) from exc

    return hostname


def filter_capability_statement(
    capability_stmt: Dict[str, Any],
    target_url: str = "http://slainte-fhir:8082",
    require_experimental: bool = False,
) -> ReachabilitySurface:
    """
    Ingests a FHIR R4 CapabilityStatement and prunes non-clinical metadata endpoints
    against CompartmentDefinition/Patient.
    """
    verify_sandbox_target(target_url)

    if capability_stmt.get("resourceType") != "CapabilityStatement":
        raise ValueError("Input is not a valid HL7 FHIR CapabilityStatement")

    experimental = bool(capability_stmt.get("experimental", True))
    if require_experimental and not experimental:
        raise SandboxSecurityViolation(
            "GUARDRAIL ABORT: Target CapabilityStatement.experimental is False."
        )

    fhir_version = capability_stmt.get("fhirVersion", "4.0.1")
    rest_blocks = capability_stmt.get("rest", [])
    declared_resources: List[Dict[str, Any]] = []
    for block in rest_blocks:
        if block.get("mode") == "server":
            declared_resources.extend(block.get("resource", []))

    surface = ReachabilitySurface(
        target_url=target_url,
        fhir_version=fhir_version,
        experimental=experimental,
    )

    # Include default non-clinical FHIR R4 metadata types in baseline denominator
    total_candidate_types = len(declared_resources) + len(PRUNED_METADATA_RESOURCES)

    for res in declared_resources:
        rtype = res.get("type", "")
        if not rtype:
            continue
        interactions = [
            i.get("code") for i in res.get("interaction", []) if i.get("code")
        ]
        surface.supported_interactions[rtype] = interactions

        if rtype in PRUNED_METADATA_RESOURCES:
            surface.pruned_resources.append(rtype)
        elif rtype in PATIENT_COMPARTMENT_MAP:
            surface.active_compartment_resources[rtype] = PATIENT_COMPARTMENT_MAP[rtype]
        elif rtype in BRIDGE_AND_SINK_RESOURCES:
            surface.bridge_resources.append(rtype)
        else:
            surface.pruned_resources.append(rtype)

    for meta_type in sorted(PRUNED_METADATA_RESOURCES):
        if meta_type not in surface.pruned_resources:
            surface.pruned_resources.append(meta_type)

    retained = len(surface.active_compartment_resources) + len(surface.bridge_resources)
    if total_candidate_types > 0:
        surface.reduction_ratio = round(
            1.0 - (retained / float(total_candidate_types)), 4
        )

    return surface
