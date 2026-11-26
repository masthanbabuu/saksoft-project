-- sql/schema.sql: the ONE definition of the database (Playbook DB-03).
-- To change the schema, edit this file in place. Do not create separate ALTER files.
-- Docker runs this file when the database is first created (see docker-compose.yml).
--
-- Replace this example with the tables for your variant on day 7.

CREATE TABLE IF NOT EXISTS documents (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source      TEXT        NOT NULL,                       -- where the text came from (cited in answers)
    body        TEXT        NOT NULL,
    allowed_roles TEXT[]    NOT NULL DEFAULT '{}',          -- who may see it (filter BEFORE ranking, AI-08)
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()          -- always timestamptz in UTC (DB-08)
);

-- One reason per index (DB-04): this one speeds up "documents from one source".
CREATE INDEX IF NOT EXISTS idx_documents_source ON documents (source);

-- Day 16: Authentication and session management.

CREATE TABLE IF NOT EXISTS auth_users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'reader'
        CHECK (role IN ('reader', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    token_hash TEXT PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES auth_users(id)
        ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS auth_audit_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT REFERENCES auth_users(id),
    event_type TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS auth_login_attempts (
    identifier_hash TEXT PRIMARY KEY,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    locked_until TIMESTAMPTZ
);

-- Day 16: Parcel ownership.
ALTER TABLE parcels
ADD COLUMN IF NOT EXISTS owner_user_id BIGINT
REFERENCES auth_users(id);

CREATE INDEX IF NOT EXISTS idx_parcels_owner
ON parcels (owner_user_id);
