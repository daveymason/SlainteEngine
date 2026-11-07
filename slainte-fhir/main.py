"""
SlainteFHIR: Autonomous Lightweight HL7 FHIR R4 Micro-EHR Server.
Provides:
- Standard FHIR R4 REST endpoints (/Patient, /Observation, /Condition, /Encounter, /Bundle)
- Smart Gatekeeper zero-hallucination validation via verification_engine
- Real-time Server-Sent Events (SSE) push updates
- High-concurrency SQLite WAL storage with JSON1 indexing
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Query, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

import db
import verification_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SlainteFHIR")

# Subscribers for Server-Sent Events
subscribers: List[asyncio.Queue] = []

async def publish_event(event_type: str, payload: Dict[str, Any]):
    """Broadcast an event to all connected dashboard SSE subscribers."""
    message = json.dumps({"event": event_type, "data": payload})
    for queue in subscribers:
        await queue.put(message)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Boot SQLite WAL store and seed with initial cohort if empty
    seed_path = os.getenv("SEED_FILE", "data.json")
    await db.init_db(seed_path)
    logger.info("SlainteFHIR database ready in WAL mode.")
    yield
    logger.info("SlainteFHIR shutting down.")

app = FastAPI(
    title="SlainteFHIR Micro-EHR",
    description="Autonomous, Zero-Hallucination HL7 FHIR R4 Clinical API Server",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_bundle_searchset(resources: List[Dict[str, Any]], total: Optional[int] = None) -> Dict[str, Any]:
    """Wraps resources in a valid FHIR R4 Bundle of type 'searchset'."""
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": total if total is not None else len(resources),
        "entry": [{"fullUrl": f"urn:uuid:{r.get('id')}", "resource": r} for r in resources]
    }

def create_operation_outcome(severity: str, code: str, message: str) -> Dict[str, Any]:
    """Creates a standard HL7 FHIR R4 OperationOutcome."""
    return {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": severity,
                "code": code,
                "diagnostics": message
            }
        ]
    }

# =============================================================================
# 1. CORE SYSTEM & CAPABILITY ENDPOINTS
# =============================================================================

@app.get("/health")
async def health_check():
    counts = await db.count_resources()
    total = sum(counts.values())
    return {
        "status": "ok",
        "service": "SlainteFHIR",
        "engine": "FastAPI + SQLite WAL",
        "total_resources": total,
        "resource_breakdown": counts
    }

@app.get("/.well-known/smart-configuration")
@app.get("/fhir/r4/.well-known/smart-configuration")
async def smart_configuration(request: Request):
    """HL7 SMART App Launch v2.0 Discovery Document (.well-known/smart-configuration)."""
    public_dash = os.getenv("SLAINTE_DASH_PUBLIC_URL", "http://localhost:8000").rstrip("/")
    issuer = str(request.base_url).rstrip("/") + "/fhir/r4"
    return {
        "issuer": issuer,
        "jwks_uri": f"{public_dash}/smart/.well-known/jwks.json",
        "authorization_endpoint": f"{public_dash}/smart/authorize",
        "token_endpoint": f"{public_dash}/smart/token",
        "introspection_endpoint": f"{public_dash}/smart/introspect",
        "management_endpoint": f"{public_dash}/settings/smart",
        "grant_types_supported": ["authorization_code", "client_credentials"],
        "response_types_supported": ["code"],
        "scopes_supported": [
            "openid",
            "fhirUser",
            "profile",
            "launch",
            "launch/patient",
            "launch/encounter",
            "patient/*.cruds",
            "patient/*.rs",
            "user/*.cruds",
            "system/*.rs",
            "offline_access",
        ],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": [
            "none",
            "client_secret_basic",
            "private_key_jwt",
        ],
        "capabilities": [
            "launch-ehr",
            "launch-standalone",
            "authorize-post",
            "client-public",
            "client-confidential-symmetric",
            "client-confidential-asymmetric",
            "sso-openid-connect",
            "context-banner",
            "context-style",
            "context-ehr-patient",
            "context-ehr-encounter",
            "context-standalone-patient",
            "permission-offline",
            "permission-patient",
            "permission-user",
            "permission-v1",
            "permission-v2",
        ],
    }


@app.get("/metadata")
@app.get("/fhir/r4/metadata")
async def capability_statement():
    """HL7 FHIR R4 CapabilityStatement declaring server features & SMART-on-FHIR v2 security."""
    public_dash = os.getenv("SLAINTE_DASH_PUBLIC_URL", "http://localhost:8000").rstrip("/")
    return {
        "resourceType": "CapabilityStatement",
        "status": "active",
        "date": "2026-11-07T00:00:00Z",
        "publisher": "SlainteTech AI Security Labs",
        "kind": "instance",
        "software": {
            "name": "SlainteFHIR",
            "version": "1.2.0"
        },
        "fhirVersion": "4.0.1",
        "format": ["json"],
        "rest": [
            {
                "mode": "server",
                "security": {
                    "cors": True,
                    "service": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/restful-security-service",
                                    "code": "SMART-on-FHIR",
                                    "display": "SMART-on-FHIR v2.0 OAuth2 / OIDC"
                                }
                            ],
                            "text": "HL7 SMART App Launch v2.0 + OIDC PKCE"
                        }
                    ],
                    "extension": [
                        {
                            "url": "http://fhir-registry.smarthealthit.org/StructureDefinition/oauth-uris",
                            "extension": [
                                {"url": "authorize", "valueUri": f"{public_dash}/smart/authorize"},
                                {"url": "token", "valueUri": f"{public_dash}/smart/token"}
                            ]
                        }
                    ]
                },
                "resource": [
                    {"type": "Patient", "interaction": [{"code": "read"}, {"code": "search-type"}, {"code": "create"}, {"code": "update"}]},
                    {"type": "Observation", "interaction": [{"code": "read"}, {"code": "search-type"}, {"code": "create"}, {"code": "update"}]},
                    {"type": "Condition", "interaction": [{"code": "read"}, {"code": "search-type"}, {"code": "create"}, {"code": "update"}]},
                    {"type": "Encounter", "interaction": [{"code": "read"}, {"code": "search-type"}, {"code": "create"}, {"code": "update"}]},
                    {"type": "MedicationRequest", "interaction": [{"code": "read"}, {"code": "search-type"}, {"code": "create"}, {"code": "update"}]},
                    {"type": "AllergyIntolerance", "interaction": [{"code": "read"}, {"code": "search-type"}, {"code": "create"}, {"code": "update"}]},
                    {"type": "DocumentReference", "interaction": [{"code": "read"}, {"code": "search-type"}, {"code": "create"}, {"code": "update"}]},
                    {"type": "Provenance", "interaction": [{"code": "read"}, {"code": "search-type"}, {"code": "create"}]},
                    {"type": "Bundle", "interaction": [{"code": "create"}]}
                ]
            }
        ]
    }

# =============================================================================
# 2. PATIENT ENDPOINTS
# =============================================================================

@app.get("/fhir/r4/Patient")
async def search_patients(
    request: Request,
    _id: Optional[str] = Query(None),
    identifier: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    _count: Optional[int] = Query(None),
    limit: int = Query(50, le=200)
):
    patients = await db.query_resources("Patient", limit=200)
    if _id:
        patients = [p for p in patients if p.get("id") == _id]
    if identifier:
        patients = [
            p for p in patients 
            if any(identifier.lower() in str(i.get("value", "")).lower() for i in p.get("identifier", []))
        ]
    name_query = name or request.query_params.get("name:contains")
    if name_query:
        name_lower = name_query.lower()
        patients = [
            p for p in patients
            if any(
                name_lower in (n.get("text", "") + " " + " ".join(n.get("given", []) + [n.get("family", "")])).lower()
                for n in p.get("name", [])
            )
        ]
    effective_limit = _count if _count is not None else limit
    return create_bundle_searchset(patients[:effective_limit], total=len(patients))

@app.get("/fhir/r4/Patient/{patient_id}")
async def get_patient(patient_id: str):
    patient = await db.get_resource("Patient", patient_id)
    if not patient:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_operation_outcome("error", "not-found", f"Patient/{patient_id} not found")
        )
    return patient

# =============================================================================
# 3. OBSERVATION & CLINICAL ENDPOINTS
# =============================================================================

@app.get("/fhir/r4/Observation")
async def search_observations(
    patient: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    code: Optional[str] = Query(None),
    _count: Optional[int] = Query(None),
    limit: int = Query(100, le=500)
):
    patient_ref = patient or subject
    obs_list = await db.query_resources("Observation", patient_ref=patient_ref, limit=500)

    if category:
        cat_target = category.lower().split("|")[-1].strip()
        vital_loincs = {
            "8480-6", "8462-4", "85354-9", "55284-4", "8867-4",
            "59408-5", "2708-6", "9279-1", "8310-5", "72514-3", "9269-2"
        }
        filtered_by_cat = []
        for o in obs_list:
            cats = o.get("category", [])
            cat_codes = [
                cd.get("code", "").lower()
                for c in cats if isinstance(c, dict)
                for cd in c.get("coding", []) if isinstance(cd, dict) and cd.get("code")
            ]
            obs_loincs = {
                c.get("code")
                for c in o.get("code", {}).get("coding", [])
                if isinstance(c, dict) and c.get("code")
            }
            is_vital = bool(obs_loincs & vital_loincs)
            if cat_target in cat_codes:
                filtered_by_cat.append(o)
            elif not cat_codes:
                if cat_target == "vital-signs" and is_vital:
                    filtered_by_cat.append(o)
                elif cat_target == "laboratory" and not is_vital and "75540-5" not in obs_loincs:
                    filtered_by_cat.append(o)
        obs_list = filtered_by_cat

    if code:
        raw_codes = [c.strip() for c in code.split(",") if c.strip()]
        codes_to_match = set()
        for rc in raw_codes:
            codes_to_match.add(rc)
            if "|" in rc:
                codes_to_match.add(rc.split("|")[-1])
        if "59408-5" in codes_to_match or "2708-6" in codes_to_match:
            codes_to_match.update({"59408-5", "2708-6"})
        if "85354-9" in codes_to_match or "55284-4" in codes_to_match:
            codes_to_match.update({"85354-9", "55284-4"})
        obs_list = [
            o for o in obs_list
            if o.get("code", {}).get("text") in codes_to_match
            or any(
                c.get("code") in codes_to_match
                for c in o.get("code", {}).get("coding", [])
                if isinstance(c, dict)
            )
        ]

    effective_limit = _count if _count is not None else limit
    return create_bundle_searchset(obs_list[:effective_limit], total=len(obs_list))

@app.get("/fhir/r4/Condition")
async def search_conditions(
    patient: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    _count: Optional[int] = Query(None),
    limit: int = Query(100, le=500)
):
    patient_ref = patient or subject
    effective_limit = _count if _count is not None else limit
    conditions = await db.query_resources("Condition", patient_ref=patient_ref, limit=effective_limit)
    return create_bundle_searchset(conditions)

@app.get("/fhir/r4/MedicationRequest")
async def search_medication_requests(
    patient: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    _count: Optional[int] = Query(None),
    limit: int = Query(100, le=500)
):
    patient_ref = patient or subject
    effective_limit = _count if _count is not None else limit
    meds = await db.query_resources("MedicationRequest", patient_ref=patient_ref, limit=effective_limit)
    return create_bundle_searchset(meds)

@app.get("/fhir/r4/MedicationRequest/{med_id}")
async def get_medication_request(med_id: str):
    med = await db.get_resource("MedicationRequest", med_id)
    if not med:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_operation_outcome("error", "not-found", f"MedicationRequest/{med_id} not found")
        )
    return med

@app.get("/fhir/r4/AllergyIntolerance")
async def search_allergy_intolerances(
    patient: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    _count: Optional[int] = Query(None),
    limit: int = Query(100, le=500)
):
    patient_ref = patient or subject
    effective_limit = _count if _count is not None else limit
    allergies = await db.query_resources("AllergyIntolerance", patient_ref=patient_ref, limit=effective_limit)
    return create_bundle_searchset(allergies)

@app.get("/fhir/r4/AllergyIntolerance/{allergy_id}")
async def get_allergy_intolerance(allergy_id: str):
    alg = await db.get_resource("AllergyIntolerance", allergy_id)
    if not alg:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_operation_outcome("error", "not-found", f"AllergyIntolerance/{allergy_id} not found")
        )
    return alg

@app.get("/fhir/r4/Encounter")
async def search_encounters(
    patient: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    limit: int = Query(50, le=200)
):
    patient_ref = patient or subject
    encounters = await db.query_resources("Encounter", patient_ref=patient_ref, limit=limit)
    return create_bundle_searchset(encounters)

@app.get("/fhir/r4/Provenance")
async def search_provenance(
    patient: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    target: Optional[str] = Query(None),
    limit: int = Query(50, le=200)
):
    patient_ref = patient or subject
    provenances = await db.query_resources("Provenance", patient_ref=patient_ref, limit=limit)
    if target:
        provenances = [
            p for p in provenances
            if any(target in t.get("reference", "") for t in p.get("target", []))
        ]
    return create_bundle_searchset(provenances)

@app.get("/fhir/r4/Provenance/{provenance_id}")
async def get_provenance(provenance_id: str):
    prov = await db.get_resource("Provenance", provenance_id)
    if not prov:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_operation_outcome("error", "not-found", f"Provenance/{provenance_id} not found")
        )
    return prov

@app.get("/fhir/r4/DocumentReference")
async def search_document_references(
    patient: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    _count: Optional[int] = Query(None),
    limit: int = Query(100, le=500)
):
    patient_ref = patient or subject
    effective_limit = _count if _count is not None else limit
    docs = await db.query_resources("DocumentReference", patient_ref=patient_ref, limit=effective_limit)
    return create_bundle_searchset(docs)

@app.get("/fhir/r4/DocumentReference/{doc_id}")
async def get_document_reference(doc_id: str):
    doc = await db.get_resource("DocumentReference", doc_id)
    if not doc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_operation_outcome("error", "not-found", f"DocumentReference/{doc_id} not found")
        )
    return doc

@app.get("/fhir/r4/Condition/{cond_id}")
async def get_condition(cond_id: str):
    cond = await db.get_resource("Condition", cond_id)
    if not cond:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_operation_outcome("error", "not-found", f"Condition/{cond_id} not found")
        )
    return cond

@app.get("/fhir/r4/Observation/{obs_id}")
async def get_observation(obs_id: str):
    obs = await db.get_resource("Observation", obs_id)
    if not obs:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_operation_outcome("error", "not-found", f"Observation/{obs_id} not found")
        )
    return obs

SUPPORTED_MUTABLE_RESOURCES = {
    "Patient", "Encounter", "Condition", "Observation",
    "MedicationRequest", "AllergyIntolerance", "DocumentReference", "Provenance"
}

@app.post("/fhir/r4/{resource_type}", status_code=status.HTTP_201_CREATED)
async def create_fhir_resource(resource_type: str, payload: Dict[str, Any]):
    """Create an individual HL7 FHIR R4 clinical resource."""
    if resource_type == "$validate":
        return await validate_fhir(payload)
    if resource_type == "Bundle":
        return await ingest_bundle(payload)
    if resource_type not in SUPPORTED_MUTABLE_RESOURCES:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=create_operation_outcome("error", "not-supported", f"Unsupported resourceType: {resource_type}")
        )
    if payload.get("resourceType") and payload.get("resourceType") != resource_type:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=create_operation_outcome("error", "invalid", f"resourceType mismatch: expected {resource_type}")
        )
    payload = dict(payload)
    payload["resourceType"] = resource_type
    saved = await db.save_resource(payload)
    await publish_event("resource-created", {"resourceType": resource_type, "id": saved.get("id")})
    return saved

@app.put("/fhir/r4/{resource_type}/{resource_id}")
async def update_fhir_resource(resource_type: str, resource_id: str, payload: Dict[str, Any]):
    """Update an existing HL7 FHIR R4 clinical resource by ID."""
    if resource_type not in SUPPORTED_MUTABLE_RESOURCES:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=create_operation_outcome("error", "not-supported", f"Unsupported resourceType: {resource_type}")
        )
    payload = dict(payload)
    payload["resourceType"] = resource_type
    payload["id"] = resource_id
    saved = await db.save_resource(payload)
    await publish_event("resource-updated", {"resourceType": resource_type, "id": resource_id})
    return saved


# =============================================================================
# 4. INGESTION, VALIDATION & SMART GATEKEEPER
# =============================================================================

@app.post("/fhir/r4/$validate")
async def validate_fhir(bundle: Dict[str, Any]):
    """Dynamic validation endpoint without persistence."""
    try:
        verification_engine.verify_fhir_r4_bundle(bundle)
        return create_operation_outcome("information", "informational", "Bundle passed all FHIR R4 and clinical verification gates.")
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=create_operation_outcome("error", "invalid", str(e))
        )

@app.post("/fhir/r4/Bundle", status_code=status.HTTP_201_CREATED)
async def ingest_bundle(bundle: Dict[str, Any]):
    """
    Ingests and validates an HL7 FHIR R4 Bundle.
    Rejects bundles with unmapped terms or clinical errors via OperationOutcome.
    Saves to SQLite WAL and broadcasts real-time SSE notification.
    """
    if bundle.get("resourceType") != "Bundle":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=create_operation_outcome("error", "invalid", "Payload must be an HL7 FHIR R4 Bundle.")
        )

    # 1. Verification Gate
    try:
        verification_engine.verify_fhir_r4_bundle(bundle)
    except Exception as e:
        logger.warning(f"Bundle rejected by verification engine: {e}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=create_operation_outcome("error", "invalid", f"Clinical Gatekeeper Rejection: {e}")
        )

    # 2. Persist to SQLite WAL store
    count = await db.save_bundle(bundle)

    # 3. Broadcast real-time SSE event to SlainteDash
    await publish_event("patient-triaged", {
        "bundle_id": bundle.get("id"),
        "entries_ingested": count,
        "type": bundle.get("type")
    })

    return {
        "resourceType": "Bundle",
        "type": "transaction-response",
        "id": bundle.get("id"),
        "total_entries_stored": count,
        "status": "success"
    }

# =============================================================================
# 5. REAL-TIME EVENT STREAM (SSE)
# =============================================================================

@app.get("/events/stream")
async def sse_event_stream(request: Request):
    """Server-Sent Events stream for zero-polling HTMX dashboard updates."""
    queue = asyncio.Queue()
    subscribers.append(queue)

    async def event_generator():
        try:
            # Send initial keepalive ping
            yield {"event": "ping", "data": "connected"}
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield {"event": "message", "data": data}
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "keepalive"}
        finally:
            if queue in subscribers:
                subscribers.remove(queue)

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8082, reload=False)
