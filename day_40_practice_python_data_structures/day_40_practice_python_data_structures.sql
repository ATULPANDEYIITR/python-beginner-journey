-- Practice: Python Data Structures
-- PostgreSQL case study: a relational model for operational data collections.
--
-- This script demonstrates relational representations of keyed records,
-- unique collections, ordered event histories, queue-like work items,
-- hierarchical relationships, and graph edges. SQL rows are not substitutes
-- for in-memory lists or sets in every situation; constraints and indexes
-- provide durable integrity and efficient relational access.

BEGIN;

DROP SCHEMA IF EXISTS data_structures_practice CASCADE;
CREATE SCHEMA data_structures_practice;
SET search_path TO data_structures_practice, public;

CREATE TABLE employees (
    employee_id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL CHECK (length(trim(full_name)) > 0),
    department TEXT NOT NULL CHECK (length(trim(department)) > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory_items (
    sku TEXT PRIMARY KEY,
    description TEXT NOT NULL CHECK (length(trim(description)) > 0),
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    reorder_level INTEGER NOT NULL CHECK (reorder_level >= 0),
    unit_cost NUMERIC(12, 2) NOT NULL CHECK (unit_cost >= 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory_movements (
    movement_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku TEXT NOT NULL REFERENCES inventory_items(sku),
    quantity_delta INTEGER NOT NULL CHECK (quantity_delta <> 0),
    reason TEXT NOT NULL CHECK (
        reason IN ('RECEIPT', 'ISSUE', 'RETURN', 'ADJUSTMENT')
    ),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX inventory_movements_sku_time_idx
    ON inventory_movements (sku, occurred_at DESC);

CREATE TABLE operational_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_key TEXT NOT NULL UNIQUE,
    event_type TEXT NOT NULL CHECK (length(trim(event_type)) > 0),
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX operational_events_type_time_idx
    ON operational_events (event_type, occurred_at DESC);

CREATE TABLE work_items (
    work_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    priority SMALLINT NOT NULL CHECK (priority BETWEEN 1 AND 5),
    status TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    claimed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    CHECK (completed_at IS NULL OR status = 'COMPLETED'),
    CHECK (claimed_at IS NULL OR claimed_at >= created_at)
);

-- Supports retrieval of pending work by urgency and arrival time.
CREATE INDEX work_items_pending_priority_idx
    ON work_items (priority, created_at, work_item_id)
    WHERE status = 'PENDING';

CREATE TABLE categories (
    category_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE,
    parent_category_id BIGINT REFERENCES categories(category_id)
        ON DELETE RESTRICT,
    CHECK (parent_category_id IS NULL OR parent_category_id <> category_id)
);

CREATE TABLE facilities (
    facility_id TEXT PRIMARY KEY,
    facility_name TEXT NOT NULL
);

CREATE TABLE routes (
    source_facility_id TEXT NOT NULL REFERENCES facilities(facility_id),
    destination_facility_id TEXT NOT NULL REFERENCES facilities(facility_id),
    distance_km NUMERIC(10, 2) NOT NULL CHECK (distance_km >= 0),
    PRIMARY KEY (source_facility_id, destination_facility_id),
    CHECK (source_facility_id <> destination_facility_id)
);

CREATE TABLE employee_skill_tags (
    employee_id TEXT NOT NULL REFERENCES employees(employee_id)
        ON DELETE CASCADE,
    skill_tag TEXT NOT NULL CHECK (length(trim(skill_tag)) > 0),
    PRIMARY KEY (employee_id, skill_tag)
);

INSERT INTO employees (employee_id, full_name, department) VALUES
    ('E-101', 'Asha Verma', 'Operations'),
    ('E-102', 'Ravi Kumar', 'Finance'),
    ('E-103', 'Mira Shah', 'Operations');

INSERT INTO inventory_items
    (sku, description, quantity, reorder_level, unit_cost)
VALUES
    ('CPU-01', 'Server processor', 2, 8, 240.00),
    ('RAM-16', 'Memory module', 14, 10, 68.50),
    ('SSD-02', 'Enterprise SSD', 1, 6, 115.00),
    ('NET-10', 'Network adapter', 4, 5, 39.99);

INSERT INTO inventory_movements (sku, quantity_delta, reason) VALUES
    ('CPU-01', 5, 'RECEIPT'),
    ('CPU-01', -3, 'ISSUE'),
    ('RAM-16', -2, 'ISSUE'),
    ('SSD-02', 2, 'RETURN');

INSERT INTO operational_events (event_key, event_type, payload) VALUES
    ('EV-001', 'login', '{"employee_id":"E-101"}'),
    ('EV-002', 'purchase', '{"sku":"CPU-01","quantity":2}'),
    ('EV-003', 'login', '{"employee_id":"E-102"}'),
    ('EV-004', 'search', '{"query":"network adapter"}'),
    ('EV-005', 'purchase', '{"sku":"SSD-02","quantity":1}');

INSERT INTO work_items (title, priority, status) VALUES
    ('Investigate low processor stock', 1, 'PENDING'),
    ('Reconcile memory-module movement', 3, 'PENDING'),
    ('Prepare weekly inventory report', 4, 'PENDING'),
    ('Validate supplier receipt', 2, 'COMPLETED');

INSERT INTO categories (category_name, parent_category_id)
VALUES ('Hardware', NULL);

INSERT INTO categories (category_name, parent_category_id)
SELECT 'Computing', category_id
FROM categories
WHERE category_name = 'Hardware';

INSERT INTO categories (category_name, parent_category_id)
SELECT 'Networking', category_id
FROM categories
WHERE category_name = 'Hardware';

INSERT INTO facilities (facility_id, facility_name) VALUES
    ('WH', 'Central Warehouse'),
    ('NH', 'North Hub'),
    ('SH', 'South Hub'),
    ('CS', 'City Store');

INSERT INTO routes
    (source_facility_id, destination_facility_id, distance_km)
VALUES
    ('WH', 'NH', 4.50),
    ('WH', 'SH', 6.00),
    ('NH', 'CS', 3.00),
    ('SH', 'CS', 2.00),
    ('NH', 'SH', 1.50);

INSERT INTO employee_skill_tags (employee_id, skill_tag) VALUES
    ('E-101', 'inventory-control'),
    ('E-101', 'data-quality'),
    ('E-102', 'financial-audit'),
    ('E-103', 'data-quality');

-- A dictionary-like keyed lookup is represented by the inventory_items primary key.
SELECT sku, description, quantity, reorder_level
FROM inventory_items
WHERE sku = 'CPU-01';

-- Filtering a relational collection identifies stock below its reorder threshold.
SELECT sku, description, quantity, reorder_level,
       reorder_level - quantity AS suggested_replenishment
FROM inventory_items
WHERE quantity < reorder_level
ORDER BY suggested_replenishment DESC, sku;

-- Aggregation over a sequence of movements resembles frequency and sum processing.
SELECT sku,
       COUNT(*) AS movement_count,
       SUM(quantity_delta) AS net_movement
FROM inventory_movements
GROUP BY sku
ORDER BY sku;

-- JSONB preserves event-specific attributes while event_key prevents duplicate ingestion.
SELECT event_type,
       COUNT(*) AS event_count,
       jsonb_agg(event_key ORDER BY occurred_at, event_id) AS event_keys
FROM operational_events
GROUP BY event_type
ORDER BY event_type;

-- A priority queue can be approximated by ordered selection.
-- FOR UPDATE SKIP LOCKED lets concurrent workers claim different pending rows.
WITH next_work AS (
    SELECT work_item_id
    FROM work_items
    WHERE status = 'PENDING'
    ORDER BY priority, created_at, work_item_id
    FOR UPDATE SKIP LOCKED
    LIMIT 1
)
UPDATE work_items AS work
SET status = 'PROCESSING',
    claimed_at = CURRENT_TIMESTAMP
FROM next_work
WHERE work.work_item_id = next_work.work_item_id
RETURNING work.work_item_id, work.title, work.priority, work.status;

-- Recursive traversal represents a hierarchy without storing a duplicated path.
WITH RECURSIVE category_tree AS (
    SELECT category_id, category_name, parent_category_id, 0 AS depth
    FROM categories
    WHERE parent_category_id IS NULL

    UNION ALL

    SELECT child.category_id,
           child.category_name,
           child.parent_category_id,
           parent.depth + 1
    FROM categories AS child
    JOIN category_tree AS parent
      ON child.parent_category_id = parent.category_id
)
SELECT category_id, category_name, depth
FROM category_tree
ORDER BY depth, category_name;

-- Recursive path expansion demonstrates graph traversal for this small,
-- non-negative, undirected route network. The visited path prevents cycles.
WITH RECURSIVE route_walk AS (
    SELECT
        'WH'::TEXT AS current_facility,
        ARRAY['WH'::TEXT] AS path,
        0::NUMERIC AS total_distance
    UNION ALL
    SELECT
        route.destination_facility_id,
        walk.path || route.destination_facility_id,
        walk.total_distance + route.distance_km
    FROM route_walk AS walk
    JOIN routes AS route
      ON route.source_facility_id = walk.current_facility
    WHERE NOT route.destination_facility_id = ANY(walk.path)
      AND cardinality(walk.path) < 10
)
SELECT path, total_distance
FROM route_walk
WHERE current_facility = 'CS'
ORDER BY total_distance, path
LIMIT 1;

-- Unique skill tags enforce set semantics for each employee.
SELECT employee_id, array_agg(skill_tag ORDER BY skill_tag) AS skill_tags
FROM employee_skill_tags
GROUP BY employee_id
ORDER BY employee_id;

-- Validate work completion and retain a durable event history in one transaction.
-- The row update is conditional, so repeated completion attempts cannot silently
-- complete a record that is no longer processing.
WITH completed AS (
    UPDATE work_items
    SET status = 'COMPLETED',
        completed_at = CURRENT_TIMESTAMP
    WHERE work_item_id = (
        SELECT work_item_id
        FROM work_items
        WHERE status = 'PROCESSING'
        ORDER BY claimed_at, work_item_id
        LIMIT 1
        FOR UPDATE
    )
      AND status = 'PROCESSING'
    RETURNING work_item_id, title
)
SELECT * FROM completed;

-- Database integrity failures should be tested separately by attempting invalid
-- inserts in a controlled test transaction. The following checks demonstrate
-- existing constraint metadata without deliberately aborting this main script.
SELECT
    conrelid::regclass AS table_name,
    conname AS constraint_name,
    contype AS constraint_type
FROM pg_constraint
WHERE connamespace = 'data_structures_practice'::regnamespace
ORDER BY table_name::TEXT, constraint_name;

COMMIT;
