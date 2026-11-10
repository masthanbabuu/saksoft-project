DROP TABLE IF EXISTS scan_events CASCADE;
DROP TABLE IF EXISTS hubs CASCADE;
DROP TABLE IF EXISTS parcels CASCADE;

CREATE TABLE parcels (
    id BIGINT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    status VARCHAR(30) NOT NULL,
    category VARCHAR(50),
    created_at DATE NOT NULL
);

CREATE TABLE hubs (
    id BIGINT PRIMARY KEY,
    parent_id BIGINT NOT NULL REFERENCES parcels(id),
    label VARCHAR(50) NOT NULL,
    amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0)
);

CREATE TABLE scan_events (
    id BIGINT PRIMARY KEY,
    parent_id BIGINT NOT NULL REFERENCES hubs(id),
    event VARCHAR(100) NOT NULL,
    happened_at DATE NOT NULL
);

-- Indexes for common filtering and chronological sorting
CREATE INDEX idx_parcels_status_created
    ON parcels(status, created_at DESC);
CREATE INDEX idx_scan_events_parent_date
    ON scan_events(parent_id, happened_at DESC);
