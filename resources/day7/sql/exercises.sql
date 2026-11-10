-- 1. First 10 active parcels, newest first
SELECT *
FROM parcels
WHERE status = 'active'
ORDER BY created_at DESC
LIMIT 10;

-- 2. Count parcels per status
SELECT status, COUNT(*)
FROM parcels
GROUP BY status
ORDER BY status;

-- 3. Hubs with their parent parcel name
SELECT h.id, h.parent_id, p.name AS parcel_name, h.label, h.amount
FROM hubs h
JOIN parcels p ON p.id = h.parent_id
ORDER BY h.id;

-- 4. Parcels having more than two hubs
SELECT p.id, p.name, COUNT(h.id) AS hub_count
FROM parcels p
JOIN hubs h ON h.parent_id = p.id
GROUP BY p.id, p.name
HAVING COUNT(h.id) > 2;

-- 5. Parcels with no hubs
SELECT p.*
FROM parcels p
LEFT JOIN hubs h ON h.parent_id = p.id
WHERE h.id IS NULL;

-- 6. Total amount per hub label, above 1000
SELECT label, SUM(amount) AS total_amount
FROM hubs
GROUP BY label
HAVING SUM(amount) > 1000
ORDER BY total_amount DESC;

-- 7. Rank hubs by amount within each parcel
SELECT id, parent_id, label, amount,
       RANK() OVER (
           PARTITION BY parent_id ORDER BY amount DESC
       ) AS amount_rank
FROM hubs;

-- 8. Latest scan event for every hub
WITH ranked_events AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY parent_id
               ORDER BY happened_at DESC, id DESC
           ) AS rn
    FROM scan_events
)
SELECT h.id AS hub_id, h.label, e.event, e.happened_at
FROM hubs h
LEFT JOIN ranked_events e
    ON e.parent_id = h.id AND e.rn = 1
ORDER BY h.id;
