import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import aiosqlite

logger = logging.getLogger("SlainteFHIR.db")

DB_PATH = os.getenv("DB_PATH", "fhir_store.db")

async def get_connection() -> aiosqlite.Connection:
    conn = await aiosqlite.connect(DB_PATH)
    await conn.execute("PRAGMA journal_mode = WAL;")
    await conn.execute("PRAGMA busy_timeout = 5000;")
    await conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

async def init_db(seed_file: Optional[str] = "data.json"):
    """Initialize SQLite database in WAL mode and seed if empty."""
    conn = await get_connection()
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS fhir_resources (
                id TEXT PRIMARY KEY,
                resource_type TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                patient_ref TEXT,
                raw_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_res_type ON fhir_resources(resource_type);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_res_id ON fhir_resources(resource_id);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_pat_ref ON fhir_resources(patient_ref);")

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS fhir_bundles (
                bundle_id TEXT PRIMARY KEY,
                bundle_type TEXT NOT NULL,
                raw_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await conn.commit()

        # Check if database needs initial or updated seeding
        cursor = await conn.execute("SELECT COUNT(*) FROM fhir_resources;")
        count = (await cursor.fetchone())[0]
        if count < 100 and seed_file and Path(seed_file).exists():
            logger.info(f"Seeding SlainteFHIR database from {seed_file} (current count: {count})...")
            with open(seed_file, "r", encoding="utf-8") as f:
                seed_data = json.load(f)
            await save_bundle_conn(conn, seed_data)
            await conn.commit()
            logger.info("Seeding completed successfully.")
    finally:
        await conn.close()

async def save_bundle_conn(conn: aiosqlite.Connection, bundle: Dict[str, Any]) -> int:
    """Save bundle and split out its individual entries with normalized references."""
    bundle_id = bundle.get("id", f"bundle-{os.urandom(4).hex()}")
    bundle_type = bundle.get("type", "collection")
    raw_bundle = json.dumps(bundle)

    await conn.execute(
        "INSERT OR REPLACE INTO fhir_bundles (bundle_id, bundle_type, raw_json) VALUES (?, ?, ?);",
        (bundle_id, bundle_type, raw_bundle)
    )

    entries = bundle.get("entry", [])
    
    # Map fullUrls to canonical IDs
    url_to_canonical = {}
    for entry in entries:
        full_url = entry.get("fullUrl")
        resource = entry.get("resource")
        if full_url and resource:
            res_type = resource.get("resourceType")
            res_id = resource.get("id")
            if res_type and res_id:
                canonical = f"{res_type}/{res_id}"
                url_to_canonical[full_url] = canonical
                url_to_canonical[full_url.replace("urn:uuid:", "")] = canonical

    inserted = 0
    for entry in entries:
        resource = entry.get("resource")
        if not resource:
            continue
        res_type = resource.get("resourceType")
        res_id = resource.get("id")
        if not res_type or not res_id:
            continue

        full_id = f"{res_type}/{res_id}"
        
        # Extract and canonicalize patient reference
        patient_ref = None
        if res_type == "Patient":
            patient_ref = full_id
        elif "subject" in resource and "reference" in resource["subject"]:
            raw_ref = resource["subject"]["reference"]
            patient_ref = url_to_canonical.get(raw_ref, raw_ref)
        elif "patient" in resource and "reference" in resource["patient"]:
            raw_ref = resource["patient"]["reference"]
            patient_ref = url_to_canonical.get(raw_ref, raw_ref)
        elif res_type == "Provenance":
            for t in resource.get("target", []):
                t_ref = t.get("reference", "")
                canon = url_to_canonical.get(t_ref, t_ref)
                if "Patient/" in canon:
                    patient_ref = canon[canon.find("Patient/"):]
                    break
            if not patient_ref and "entity" in resource:
                for ent in resource.get("entity", []):
                    w_ref = ent.get("what", {}).get("reference", "")
                    canon = url_to_canonical.get(w_ref, w_ref)
                    if "Patient/" in canon:
                        patient_ref = canon[canon.find("Patient/"):]
                        break


        await conn.execute(
            """
            INSERT OR REPLACE INTO fhir_resources (id, resource_type, resource_id, patient_ref, raw_json, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
            """,
            (full_id, res_type, res_id, patient_ref, json.dumps(resource))
        )
        inserted += 1

    return inserted

async def save_bundle(bundle: Dict[str, Any]) -> int:
    conn = await get_connection()
    try:
        count = await save_bundle_conn(conn, bundle)
        await conn.commit()
        return count
    finally:
        await conn.close()

async def get_resource(res_type: str, res_id: str) -> Optional[Dict[str, Any]]:
    full_id = f"{res_type}/{res_id}"
    conn = await get_connection()
    try:
        cursor = await conn.execute("SELECT raw_json FROM fhir_resources WHERE id = ?;", (full_id,))
        row = await cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None
    finally:
        await conn.close()

async def query_resources(res_type: str, patient_ref: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    conn = await get_connection()
    try:
        if patient_ref:
            clean_id = patient_ref.replace("Patient/", "")
            patterns = [patient_ref, f"Patient/{clean_id}", clean_id]
            placeholders = ",".join(["?"] * len(patterns))
            cursor = await conn.execute(
                f"SELECT raw_json FROM fhir_resources WHERE resource_type = ? AND patient_ref IN ({placeholders}) LIMIT ?;",
                (res_type, *patterns, limit)
            )
        else:
            cursor = await conn.execute(
                "SELECT raw_json FROM fhir_resources WHERE resource_type = ? LIMIT ?;",
                (res_type, limit)
            )
        rows = await cursor.fetchall()
        return [json.loads(r[0]) for r in rows]
    finally:
        await conn.close()

async def count_resources() -> Dict[str, int]:
    conn = await get_connection()
    try:
        cursor = await conn.execute("SELECT resource_type, COUNT(*) FROM fhir_resources GROUP BY resource_type;")
        rows = await cursor.fetchall()
        return {r[0]: r[1] for r in rows}
    finally:
        await conn.close()
