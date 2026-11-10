-- Before adding the hubs parent_id index
EXPLAIN ANALYZE
SELECT h.id, p.name
FROM hubs h
JOIN parcels p ON p.id = h.parent_id;

EXPLAIN ANALYZE
SELECT p.id, p.name, COUNT(h.id)
FROM parcels p
JOIN hubs h ON h.parent_id = p.id
GROUP BY p.id, p.name
HAVING COUNT(h.id) > 2;

-- Add index
CREATE INDEX IF NOT EXISTS idx_hubs_parent_id ON hubs(parent_id);
ANALYZE hubs;

-- After adding the index
EXPLAIN ANALYZE
SELECT h.id, p.name
FROM hubs h
JOIN parcels p ON p.id = h.parent_id;

EXPLAIN ANALYZE
SELECT p.id, p.name, COUNT(h.id)
FROM parcels p
JOIN hubs h ON h.parent_id = p.id
GROUP BY p.id, p.name
HAVING COUNT(h.id) > 2;
