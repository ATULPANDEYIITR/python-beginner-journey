BEGIN;

DROP VIEW IF EXISTS ready_work_items;
DROP VIEW IF EXISTS category_effort;
DROP TABLE IF EXISTS work_activity CASCADE;
DROP TABLE IF EXISTS work_dependencies CASCADE;
DROP TABLE IF EXISTS work_tags CASCADE;
DROP TABLE IF EXISTS work_items CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

CREATE TABLE departments (
    department_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    department_name TEXT NOT NULL UNIQUE
);

CREATE TABLE work_items (
    work_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    department_id BIGINT NOT NULL REFERENCES departments(department_id),
    priority SMALLINT NOT NULL CHECK (priority BETWEEN 1 AND 5),
    estimated_hours NUMERIC(10, 2) NOT NULL CHECK (estimated_hours >= 0),
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'in_progress', 'completed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    CHECK (
        (status = 'completed' AND completed_at IS NOT NULL)
        OR
        (status <> 'completed' AND completed_at IS NULL)
    )
);

CREATE TABLE work_tags (
    work_item_id BIGINT NOT NULL
        REFERENCES work_items(work_item_id) ON DELETE CASCADE,
    tag TEXT NOT NULL CHECK (length(trim(tag)) > 0),
    PRIMARY KEY (work_item_id, tag)
);

CREATE TABLE work_dependencies (
    work_item_id BIGINT NOT NULL
        REFERENCES work_items(work_item_id) ON DELETE CASCADE,
    prerequisite_id BIGINT NOT NULL
        REFERENCES work_items(work_item_id) ON DELETE RESTRICT,
    PRIMARY KEY (work_item_id, prerequisite_id),
    CHECK (work_item_id <> prerequisite_id)
);

CREATE TABLE work_activity (
    activity_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    work_item_id BIGINT NOT NULL
        REFERENCES work_items(work_item_id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    previous_status TEXT,
    new_status TEXT,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- These indexes support ready-work filtering, category aggregation, and
-- dependency traversal without duplicating the primary-key indexes.
CREATE INDEX idx_work_items_status_priority
    ON work_items(status, priority, item_code);

CREATE INDEX idx_work_items_department
    ON work_items(department_id);

CREATE INDEX idx_work_dependencies_prerequisite
    ON work_dependencies(prerequisite_id);

CREATE INDEX idx_work_tags_tag_item
    ON work_tags(tag, work_item_id);

CREATE INDEX idx_work_activity_item_time
    ON work_activity(work_item_id, occurred_at DESC);

CREATE OR REPLACE FUNCTION enforce_work_item_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status IS DISTINCT FROM OLD.status THEN
        IF NOT (
            (OLD.status = 'pending' AND NEW.status = 'in_progress')
            OR
            (OLD.status = 'in_progress' AND NEW.status = 'completed')
        ) THEN
            RAISE EXCEPTION
                'Invalid work-item transition: % -> %',
                OLD.status, NEW.status;
        END IF;

        IF NEW.status = 'in_progress' AND EXISTS (
            SELECT 1
            FROM work_dependencies dependency
            JOIN work_items prerequisite
              ON prerequisite.work_item_id = dependency.prerequisite_id
            WHERE dependency.work_item_id = OLD.work_item_id
              AND prerequisite.status <> 'completed'
        ) THEN
            RAISE EXCEPTION
                'Cannot start work item % while prerequisites remain incomplete',
                OLD.item_code;
        END IF;

        IF NEW.status = 'completed' THEN
            NEW.completed_at := CURRENT_TIMESTAMP;
        ELSE
            NEW.completed_at := NULL;
        END IF;

        INSERT INTO work_activity (
            work_item_id,
            event_type,
            previous_status,
            new_status
        )
        VALUES (
            OLD.work_item_id,
            'status_transition',
            OLD.status,
            NEW.status
        );
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_enforce_work_item_transition
BEFORE UPDATE OF status ON work_items
FOR EACH ROW
EXECUTE FUNCTION enforce_work_item_transition();

CREATE OR REPLACE FUNCTION prevent_dependency_cycles()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Recursive reachability detects whether the new edge would close a cycle.
    IF EXISTS (
        WITH RECURSIVE reachable(item_id) AS (
            SELECT NEW.prerequisite_id

            UNION

            SELECT dependency.prerequisite_id
            FROM work_dependencies dependency
            JOIN reachable current_node
              ON dependency.work_item_id = current_node.item_id
        )
        SELECT 1
        FROM reachable
        WHERE item_id = NEW.work_item_id
    ) THEN
        RAISE EXCEPTION
            'Dependency would create a cycle between work items % and %',
            NEW.work_item_id, NEW.prerequisite_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_dependency_cycles
BEFORE INSERT OR UPDATE ON work_dependencies
FOR EACH ROW
EXECUTE FUNCTION prevent_dependency_cycles();

CREATE VIEW ready_work_items AS
SELECT
    item.work_item_id,
    item.item_code,
    item.title,
    department.department_name,
    item.priority,
    item.estimated_hours
FROM work_items item
JOIN departments department
  ON department.department_id = item.department_id
WHERE item.status = 'pending'
  AND NOT EXISTS (
      SELECT 1
      FROM work_dependencies dependency
      JOIN work_items prerequisite
        ON prerequisite.work_item_id = dependency.prerequisite_id
      WHERE dependency.work_item_id = item.work_item_id
        AND prerequisite.status <> 'completed'
  );

CREATE VIEW category_effort AS
SELECT
    department.department_name,
    COUNT(*) AS item_count,
    SUM(item.estimated_hours) AS total_estimated_hours,
    COUNT(*) FILTER (WHERE item.status = 'completed') AS completed_count
FROM work_items item
JOIN departments department
  ON department.department_id = item.department_id
GROUP BY department.department_name;

INSERT INTO departments (department_name)
VALUES
    ('Data Operations'),
    ('Warehouse'),
    ('Analytics'),
    ('Procurement');

INSERT INTO work_items (
    item_code, title, department_id, priority, estimated_hours
)
VALUES
    (
        'OPS-401',
        'Validate supplier delivery records',
        (SELECT department_id FROM departments
         WHERE department_name = 'Data Operations'),
        1,
        2.50
    ),
    (
        'OPS-402',
        'Reconcile warehouse inventory',
        (SELECT department_id FROM departments
         WHERE department_name = 'Warehouse'),
        2,
        4.00
    ),
    (
        'OPS-403',
        'Publish procurement dashboard',
        (SELECT department_id FROM departments
         WHERE department_name = 'Analytics'),
        1,
        3.50
    ),
    (
        'OPS-404',
        'Archive validation evidence',
        (SELECT department_id FROM departments
         WHERE department_name = 'Data Operations'),
        3,
        1.00
    );

INSERT INTO work_tags (work_item_id, tag)
SELECT item.work_item_id, tags.tag
FROM (
    VALUES
        ('OPS-401', 'validation'),
        ('OPS-401', 'quality'),
        ('OPS-402', 'reconciliation'),
        ('OPS-402', 'quality'),
        ('OPS-403', 'reporting'),
        ('OPS-403', 'quality'),
        ('OPS-404', 'validation'),
        ('OPS-404', 'audit')
) AS tags(item_code, tag)
JOIN work_items item ON item.item_code = tags.item_code;

INSERT INTO work_dependencies (work_item_id, prerequisite_id)
SELECT child.work_item_id, parent.work_item_id
FROM (
    VALUES
        ('OPS-402', 'OPS-401'),
        ('OPS-403', 'OPS-402'),
        ('OPS-404', 'OPS-401')
) AS relationships(child_code, parent_code)
JOIN work_items child ON child.item_code = relationships.child_code
JOIN work_items parent ON parent.item_code = relationships.parent_code;

-- The view excludes work blocked by incomplete prerequisites.
SELECT * FROM ready_work_items ORDER BY priority, item_code;

-- Relational division: every requested tag must be present.
SELECT item.item_code, item.title
FROM work_items item
WHERE NOT EXISTS (
    SELECT required.tag
    FROM (VALUES ('validation'), ('quality')) AS required(tag)
    WHERE NOT EXISTS (
        SELECT 1
        FROM work_tags assigned
        WHERE assigned.work_item_id = item.work_item_id
          AND assigned.tag = required.tag
    )
)
ORDER BY item.item_code;

SELECT * FROM category_effort ORDER BY department_name;

-- Complete the prerequisite inside a transaction. The trigger records the
-- transition and allows downstream work to become eligible.
SAVEPOINT before_completion;

UPDATE work_items
SET status = 'in_progress'
WHERE item_code = 'OPS-401';

UPDATE work_items
SET status = 'completed'
WHERE item_code = 'OPS-401';

SELECT * FROM ready_work_items ORDER BY priority, item_code;

-- Roll back only this demonstration's state change so rerunning the workflow
-- starts with the original sample statuses.
ROLLBACK TO SAVEPOINT before_completion;

-- This query reports dependency depth and order for the acyclic sample graph.
WITH RECURSIVE dependency_depth AS (
    SELECT
        item.work_item_id,
        item.item_code,
        item.title,
        0 AS depth
    FROM work_items item
    WHERE NOT EXISTS (
        SELECT 1
        FROM work_dependencies dependency
        WHERE dependency.work_item_id = item.work_item_id
    )

    UNION ALL

    SELECT
        child.work_item_id,
        child.item_code,
        child.title,
        parent.depth + 1
    FROM dependency_depth parent
    JOIN work_dependencies dependency
      ON dependency.prerequisite_id = parent.work_item_id
    JOIN work_items child
      ON child.work_item_id = dependency.work_item_id
)
SELECT item_code, title, MAX(depth) AS dependency_depth
FROM dependency_depth
GROUP BY item_code, title
ORDER BY dependency_depth, item_code;

COMMIT;
