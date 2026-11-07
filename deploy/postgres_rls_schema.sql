-- =============================================================================
-- SlainteTech AI Security Labs — Production Multi-Tenant PostgreSQL 16 Schema
-- Phase 11.5: JSONB + GIN Path Indexing + Row-Level Security (RLS) Isolation
-- =============================================================================
-- Purpose:
--   Provides turn-key migration from zero-config single-node SQLite WAL to a
--   multi-hospital / multi-CHO (HSE Community Healthcare Organisation) cluster
--   with kernel-enforced PostgreSQL Row-Level Security (RLS) and append-only
--   audit & Break-the-Glass triggers.
--
-- Usage:
--   psql "$DATABASE_URL" -f deploy/postgres_rls_schema.sql
--   -- Inside each application request transaction:
--   SET LOCAL app.current_tenant_id = 'hospital-mater-dublin';
-- =============================================================================

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Tenants (Hospitals, GP Networks, Dental Groups, EMS Regions)
CREATE TABLE IF NOT EXISTS tenants (
    tenant_id      TEXT PRIMARY KEY,
    display_name   TEXT NOT NULL,
    country_code   CHAR(2) NOT NULL DEFAULT 'IE',
    hiqa_facility  TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    active         BOOLEAN NOT NULL DEFAULT TRUE
);

INSERT INTO tenants (tenant_id, display_name, hiqa_facility)
VALUES ('default-ie-hse', 'Slainte Default Clinical Tenant (HSE Ireland)', 'HIQA-IE-0001')
ON CONFLICT (tenant_id) DO NOTHING;

-- 2. HL7 FHIR R4 Resource Store (JSONB + GIN Indexed + Tenant RLS)
CREATE TABLE IF NOT EXISTS fhir_resources (
    tenant_id      TEXT NOT NULL REFERENCES tenants(tenant_id),
    resource_type  TEXT NOT NULL,
    resource_id    TEXT NOT NULL,
    patient_ref    TEXT,
    version_id     INTEGER NOT NULL DEFAULT 1,
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload        JSONB NOT NULL,
    PRIMARY KEY (tenant_id, resource_type, resource_id)
);

CREATE INDEX IF NOT EXISTS idx_fhir_tenant_patient
    ON fhir_resources (tenant_id, resource_type, patient_ref);

CREATE INDEX IF NOT EXISTS idx_fhir_payload_gin
    ON fhir_resources USING GIN (payload jsonb_path_ops);

ALTER TABLE fhir_resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE fhir_resources FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS fhir_tenant_isolation ON fhir_resources;
CREATE POLICY fhir_tenant_isolation ON fhir_resources
    USING (tenant_id = current_setting('app.current_tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true));

-- 3. Clinical Users & Granular Separation-of-Duties RBAC
CREATE TABLE IF NOT EXISTS users (
    tenant_id              TEXT NOT NULL REFERENCES tenants(tenant_id),
    username               TEXT NOT NULL,
    password_hash          TEXT NOT NULL,
    display_name           TEXT,
    role                   TEXT NOT NULL DEFAULT 'viewer',
    clinical_role          TEXT NOT NULL DEFAULT 'general_clinician',
    registration_id        TEXT NOT NULL DEFAULT '',
    status                 TEXT NOT NULL DEFAULT 'pending',
    created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at          TIMESTAMPTZ,
    failed_login_attempts  INTEGER NOT NULL DEFAULT 0,
    locked_until           TIMESTAMPTZ,
    PRIMARY KEY (tenant_id, username)
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE users FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS users_tenant_isolation ON users;
CREATE POLICY users_tenant_isolation ON users
    USING (tenant_id = current_setting('app.current_tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true));

-- 4. Immutable Clinical & Auth Audit Ledger (Append-Only Triggers + RLS)
CREATE TABLE IF NOT EXISTS audit_log (
    id            BIGSERIAL PRIMARY KEY,
    tenant_id     TEXT NOT NULL REFERENCES tenants(tenant_id),
    occurred_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor         TEXT,
    action        TEXT NOT NULL,
    resource_type TEXT,
    resource_id   TEXT,
    outcome       TEXT NOT NULL,
    remote_addr   TEXT,
    user_agent    TEXT,
    detail        JSONB
);

CREATE INDEX IF NOT EXISTS idx_pg_audit_occurred ON audit_log (tenant_id, occurred_at DESC);
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS audit_tenant_isolation ON audit_log;
CREATE POLICY audit_tenant_isolation ON audit_log
    USING (tenant_id = current_setting('app.current_tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true));

-- 5. Immutable AI Exchange Ledger (EU AI Act Art. 12 Logging + RLS)
CREATE TABLE IF NOT EXISTS ai_exchange (
    id             BIGSERIAL PRIMARY KEY,
    tenant_id      TEXT NOT NULL REFERENCES tenants(tenant_id),
    occurred_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor          TEXT NOT NULL,
    patient_ref    TEXT NOT NULL,
    feature        TEXT NOT NULL,
    model          TEXT NOT NULL,
    prompt_hash    TEXT NOT NULL,
    prompt_version TEXT,
    deidentified   BOOLEAN NOT NULL DEFAULT TRUE,
    input_tokens   INTEGER,
    output_tokens  INTEGER,
    response       TEXT NOT NULL
);

ALTER TABLE ai_exchange ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_exchange FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS ai_exchange_tenant_isolation ON ai_exchange;
CREATE POLICY ai_exchange_tenant_isolation ON ai_exchange
    USING (tenant_id = current_setting('app.current_tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true));

-- 6. Immutable Break-the-Glass Emergency Access Grants (GDPR Art. 9(2)(c) Vital Interests)
CREATE TABLE IF NOT EXISTS break_glass_grants (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       TEXT NOT NULL REFERENCES tenants(tenant_id),
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ NOT NULL,
    actor           TEXT NOT NULL,
    clinical_role   TEXT NOT NULL,
    patient_id      TEXT NOT NULL,
    emergency_type  TEXT NOT NULL,
    justification   TEXT NOT NULL,
    remote_addr     TEXT,
    siem_dispatched BOOLEAN NOT NULL DEFAULT FALSE
);

ALTER TABLE break_glass_grants ENABLE ROW LEVEL SECURITY;
ALTER TABLE break_glass_grants FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS break_glass_tenant_isolation ON break_glass_grants;
CREATE POLICY break_glass_tenant_isolation ON break_glass_grants
    USING (tenant_id = current_setting('app.current_tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true));

-- 7. Kernel-Level Append-Only Immutability Enforcement Function & Triggers
CREATE OR REPLACE FUNCTION slainte_prevent_ledger_mutation()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'Security Policy Violation: Table % is strictly append-only (HIQA / EU AI Act / ISO 27001)', TG_TABLE_NAME;
END;
$$;

DROP TRIGGER IF EXISTS trg_audit_log_immutable ON audit_log;
CREATE TRIGGER trg_audit_log_immutable
    BEFORE UPDATE OR DELETE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION slainte_prevent_ledger_mutation();

DROP TRIGGER IF EXISTS trg_ai_exchange_immutable ON ai_exchange;
CREATE TRIGGER trg_ai_exchange_immutable
    BEFORE UPDATE OR DELETE ON ai_exchange
    FOR EACH ROW EXECUTE FUNCTION slainte_prevent_ledger_mutation();

DROP TRIGGER IF EXISTS trg_break_glass_immutable ON break_glass_grants;
CREATE TRIGGER trg_break_glass_immutable
    BEFORE UPDATE OR DELETE ON break_glass_grants
    FOR EACH ROW EXECUTE FUNCTION slainte_prevent_ledger_mutation();

COMMIT;
