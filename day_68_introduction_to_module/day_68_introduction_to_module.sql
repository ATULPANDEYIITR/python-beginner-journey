/*
============================================================
INTRODUCTION TO MODULES - POSTGRESQL
============================================================

Demonstrates:
1. Database schemas as organizational modules.
2. Functions as reusable database components.
3. Module registration and versioning.
4. Module dependencies.
5. Module lifecycle and activation.
6. Dependency validation and circular dependency detection.
7. Role-based access control.
8. Execution auditing.
9. Transaction management.
10. Reporting and operational queries.

Compatible with PostgreSQL 15+.
*/

-- =========================================================
-- 1. CREATE DATABASE SCHEMA
-- =========================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS module_lab;

CREATE SCHEMA IF NOT EXISTS core_services;

CREATE SCHEMA IF NOT EXISTS analytics_services;

CREATE SCHEMA IF NOT EXISTS reporting_services;

COMMIT;

SET search_path TO module_lab, public;


-- =========================================================
-- 2. MODULE STATUS
-- =========================================================

CREATE TYPE module_lab.module_status AS ENUM (
    'registered',
    'active',
    'disabled',
    'failed'
);

CREATE TYPE module_lab.execution_status AS ENUM (
    'success',
    'failed'
);


-- =========================================================
-- 3. MODULE REGISTRY
-- =========================================================

CREATE TABLE module_lab.modules (
    module_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    module_name VARCHAR(100) NOT NULL UNIQUE,

    module_version VARCHAR(30) NOT NULL,

    description TEXT NOT NULL,

    owner_team VARCHAR(100) NOT NULL,

    status module_lab.module_status
        NOT NULL DEFAULT 'registered',

    created_at TIMESTAMPTZ
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_module_name
        CHECK (
            module_name ~ '^[a-zA-Z][a-zA-Z0-9_]*$'
        ),

    CONSTRAINT valid_module_version
        CHECK (
            module_version ~ '^[0-9]+\.[0-9]+\.[0-9]+$'
        ),

    CONSTRAINT valid_owner
        CHECK (length(trim(owner_team)) > 0)
);


-- =========================================================
-- 4. MODULE DEPENDENCIES
-- =========================================================

CREATE TABLE module_lab.module_dependencies (
    dependency_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    module_id BIGINT NOT NULL
        REFERENCES module_lab.modules(module_id)
        ON DELETE CASCADE,

    dependency_module_id BIGINT NOT NULL
        REFERENCES module_lab.modules(module_id)
        ON DELETE RESTRICT,

    created_at TIMESTAMPTZ
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_dependency
        UNIQUE (module_id, dependency_module_id),

    CONSTRAINT no_self_dependency
        CHECK (module_id <> dependency_module_id)
);

CREATE INDEX idx_dependencies_module
    ON module_lab.module_dependencies(module_id);

CREATE INDEX idx_dependencies_target
    ON module_lab.module_dependencies(dependency_module_id);


-- =========================================================
-- 5. MODULE EXECUTION AUDIT
-- =========================================================

CREATE TABLE module_lab.execution_logs (
    execution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    module_id BIGINT
        REFERENCES module_lab.modules(module_id)
        ON DELETE SET NULL,

    execution_status module_lab.execution_status NOT NULL,

    execution_message TEXT,

    execution_duration_ms NUMERIC(12, 3),

    executed_by TEXT NOT NULL DEFAULT session_user,

    executed_at TIMESTAMPTZ
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_execution_duration
        CHECK (
            execution_duration_ms IS NULL
            OR execution_duration_ms >= 0
        )
);

CREATE INDEX idx_execution_module_date
    ON module_lab.execution_logs(module_id, executed_at DESC);

CREATE INDEX idx_execution_status
    ON module_lab.execution_logs(execution_status);


-- =========================================================
-- 6. MODULE FUNCTION REGISTRY
-- =========================================================

CREATE TABLE module_lab.module_functions (
    function_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    module_id BIGINT NOT NULL
        REFERENCES module_lab.modules(module_id)
        ON DELETE CASCADE,

    function_name VARCHAR(100) NOT NULL,

    function_description TEXT NOT NULL,

    is_public BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_module_function
        UNIQUE (module_id, function_name),

    CONSTRAINT valid_function_name
        CHECK (
            function_name ~ '^[a-zA-Z][a-zA-Z0-9_]*$'
        )
);


-- =========================================================
-- 7. MODULE LIFECYCLE TRIGGER
-- =========================================================

CREATE OR REPLACE FUNCTION module_lab.update_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_module_timestamp
BEFORE UPDATE ON module_lab.modules
FOR EACH ROW
EXECUTE FUNCTION module_lab.update_timestamp();


-- =========================================================
-- 8. PREVENT INVALID DEPENDENCY CYCLES
-- =========================================================

CREATE OR REPLACE FUNCTION
module_lab.validate_dependency_cycle()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    cycle_found BOOLEAN;
BEGIN

    WITH RECURSIVE dependency_path AS (

        SELECT
            NEW.dependency_module_id AS current_id,
            ARRAY[
                NEW.module_id,
                NEW.dependency_module_id
            ]::BIGINT[] AS visited,
            (
                NEW.module_id = NEW.dependency_module_id
            ) AS cycle

        UNION ALL

        SELECT
            dependency.dependency_module_id,
            path.visited || dependency.dependency_module_id,
            dependency.dependency_module_id = NEW.module_id

        FROM dependency_path path

        JOIN module_lab.module_dependencies dependency
            ON dependency.module_id = path.current_id

        WHERE NOT path.cycle
          AND NOT (
              dependency.dependency_module_id = ANY(path.visited)
          )
    )

    SELECT EXISTS (
        SELECT 1
        FROM dependency_path
        WHERE cycle
    )
    INTO cycle_found;

    IF cycle_found THEN
        RAISE EXCEPTION
            'Circular dependency detected between module IDs % and %',
            NEW.module_id,
            NEW.dependency_module_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_dependency
BEFORE INSERT OR UPDATE
ON module_lab.module_dependencies
FOR EACH ROW
EXECUTE FUNCTION module_lab.validate_dependency_cycle();


-- =========================================================
-- 9. CHECK MODULE ACTIVATION ELIGIBILITY
-- =========================================================

CREATE OR REPLACE FUNCTION
module_lab.can_activate(p_module_id BIGINT)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT
        EXISTS (
            SELECT 1
            FROM module_lab.modules
            WHERE module_id = p_module_id
              AND status <> 'failed'
              AND status <> 'disabled'
        )
        AND NOT EXISTS (
            SELECT 1
            FROM module_lab.module_dependencies dependency

            JOIN module_lab.modules required_module
                ON required_module.module_id =
                   dependency.dependency_module_id

            WHERE dependency.module_id = p_module_id
              AND required_module.status <> 'active'
        );
$$;


-- =========================================================
-- 10. MODULE ACTIVATION PROCEDURE
-- =========================================================

CREATE OR REPLACE PROCEDURE
module_lab.activate_module(
    p_module_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    current_status module_lab.module_status;
BEGIN

    SELECT status
    INTO current_status
    FROM module_lab.modules
    WHERE module_id = p_module_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Module % does not exist', p_module_id;
    END IF;

    IF current_status = 'disabled'
       OR current_status = 'failed' THEN

        RAISE EXCEPTION
            'Module cannot be activated from state %',
            current_status;
    END IF;

    IF NOT module_lab.can_activate(p_module_id) THEN

        RAISE EXCEPTION
            'Module dependencies are not active';
    END IF;

    UPDATE module_lab.modules
    SET status = 'active'
    WHERE module_id = p_module_id;

    INSERT INTO module_lab.execution_logs (
        module_id,
        execution_status,
        execution_message
    )
    VALUES (
        p_module_id,
        'success',
        'Module activated'
    );

END;
$$;


-- =========================================================
-- 11. REUSABLE DATABASE FUNCTIONS
-- =========================================================

CREATE OR REPLACE FUNCTION
core_services.calculate_total(
    p_values NUMERIC[]
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN

    IF cardinality(p_values) = 0 THEN
        RAISE EXCEPTION 'Input array cannot be empty';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM unnest(p_values) AS value
        WHERE value IS NULL
    ) THEN
        RAISE EXCEPTION 'Input contains NULL values';
    END IF;

    RETURN (
        SELECT SUM(value)
        FROM unnest(p_values) AS value
    );

END;
$$;


CREATE OR REPLACE FUNCTION
core_services.calculate_average(
    p_values NUMERIC[]
)
RETURNS NUMERIC
LANGUAGE sql
IMMUTABLE
STRICT
AS $$
    SELECT
        SUM(value) / COUNT(*)
    FROM unnest(p_values) AS value;
$$;


-- =========================================================
-- 12. ANALYTICS MODULE
-- =========================================================

CREATE TABLE analytics_services.sales_records (
    record_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    category VARCHAR(100) NOT NULL,

    amount NUMERIC(14, 2) NOT NULL,

    recorded_at TIMESTAMPTZ
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_category
        CHECK (length(trim(category)) > 0),

    CONSTRAINT non_negative_amount
        CHECK (amount >= 0)
);

CREATE INDEX idx_sales_category_date
    ON analytics_services.sales_records(category, recorded_at DESC);


CREATE OR REPLACE FUNCTION
analytics_services.category_report()
RETURNS TABLE (
    category VARCHAR,
    record_count BIGINT,
    total_amount NUMERIC,
    average_amount NUMERIC
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        sales.category::VARCHAR,
        COUNT(*),
        SUM(sales.amount),
        AVG(sales.amount)
    FROM analytics_services.sales_records sales
    GROUP BY sales.category
    ORDER BY sales.category;
$$;


-- =========================================================
-- 13. SAMPLE MODULE REGISTRATION
-- =========================================================

INSERT INTO module_lab.modules (
    module_name,
    module_version,
    description,
    owner_team
)
VALUES
(
    'core',
    '1.0.0',
    'Core reusable database services',
    'Platform Engineering'
),
(
    'database',
    '1.2.0',
    'Database access and persistence services',
    'Data Engineering'
),
(
    'analytics',
    '2.0.0',
    'Business analytics and aggregation',
    'Analytics Engineering'
),
(
    'reporting',
    '1.0.0',
    'Business reporting services',
    'Reporting Team'
),
(
    'experimental',
    '0.1.0',
    'Experimental module not yet activated',
    'Research Team'
);


-- =========================================================
-- 14. REGISTER DEPENDENCIES
-- =========================================================

INSERT INTO module_lab.module_dependencies (
    module_id,
    dependency_module_id
)
SELECT
    module.module_id,
    dependency.module_id
FROM (
    VALUES
        ('database', 'core'),
        ('analytics', 'core'),
        ('analytics', 'database'),
        ('reporting', 'analytics')
) AS dependency_map(module_name, dependency_name)

JOIN module_lab.modules module
    ON module.module_name = dependency_map.module_name

JOIN module_lab.modules dependency
    ON dependency.module_name = dependency_map.dependency_name;


-- =========================================================
-- 15. REGISTER FUNCTIONS
-- =========================================================

INSERT INTO module_lab.module_functions (
    module_id,
    function_name,
    function_description,
    is_public
)
SELECT
    module.module_id,
    function_info.function_name,
    function_info.description,
    function_info.is_public
FROM (
    VALUES
        ('core', 'calculate_total',
         'Calculates the sum of numeric values', TRUE),
        ('core', 'calculate_average',
         'Calculates the arithmetic mean', TRUE),
        ('analytics', 'category_report',
         'Generates category-level reports', TRUE)
) AS function_info(
    module_name,
    function_name,
    description,
    is_public
)
JOIN module_lab.modules module
    ON module.module_name = function_info.module_name;


-- =========================================================
-- 16. SAMPLE BUSINESS RECORDS
-- =========================================================

INSERT INTO analytics_services.sales_records (
    category,
    amount
)
VALUES
('Technology', 120000),
('Technology', 150000),
('Technology', 175000),
('Consulting', 80000),
('Consulting', 95000),
('Research', 45000),
('Research', 60000);


-- =========================================================
-- 17. ACTIVATE MODULES IN DEPENDENCY ORDER
-- =========================================================

DO $$
DECLARE
    module_record RECORD;
BEGIN

    FOR module_record IN

        SELECT module_name, module_id
        FROM module_lab.modules
        WHERE module_name IN (
            'core',
            'database',
            'analytics',
            'reporting'
        )
        ORDER BY CASE module_name
            WHEN 'core' THEN 1
            WHEN 'database' THEN 2
            WHEN 'analytics' THEN 3
            WHEN 'reporting' THEN 4
        END

    LOOP

        CALL module_lab.activate_module(
            module_record.module_id
        );

    END LOOP;

END;
$$;


-- =========================================================
-- 18. MODULE INFORMATION VIEW
-- =========================================================

CREATE OR REPLACE VIEW module_lab.module_overview AS

SELECT
    module.module_id,
    module.module_name,
    module.module_version,
    module.owner_team,
    module.status,

    COUNT(DISTINCT dependency.dependency_module_id)
        AS dependency_count,

    COUNT(DISTINCT function_info.function_id)
        AS registered_function_count

FROM module_lab.modules module

LEFT JOIN module_lab.module_dependencies dependency
    ON dependency.module_id = module.module_id

LEFT JOIN module_lab.module_functions function_info
    ON function_info.module_id = module.module_id

GROUP BY
    module.module_id,
    module.module_name,
    module.module_version,
    module.owner_team,
    module.status;


-- =========================================================
-- 19. DEPENDENCY REPORT
-- =========================================================

CREATE OR REPLACE VIEW module_lab.dependency_report AS

SELECT
    module.module_name AS module_name,
    required.module_name AS dependency_name,
    required.status AS dependency_status

FROM module_lab.module_dependencies dependency

JOIN module_lab.modules module
    ON module.module_id = dependency.module_id

JOIN module_lab.modules required
    ON required.module_id = dependency.dependency_module_id;


-- =========================================================
-- 20. QUERY: MODULE RETRIEVAL
-- =========================================================

SELECT *
FROM module_lab.module_overview
ORDER BY module_name;


-- =========================================================
-- 21. QUERY: DEPENDENCY VALIDATION
-- =========================================================

SELECT
    module.module_name,
    module.status,
    module_lab.can_activate(module.module_id)
        AS activation_eligible

FROM module_lab.modules module
ORDER BY module.module_name;


-- =========================================================
-- 22. QUERY: DEPENDENCY DETAILS
-- =========================================================

SELECT *
FROM module_lab.dependency_report
ORDER BY module_name, dependency_name;


-- =========================================================
-- 23. QUERY: AGGREGATION
-- =========================================================

SELECT
    category,
    COUNT(*) AS records,
    SUM(amount) AS total_sales,
    AVG(amount) AS average_sales

FROM analytics_services.sales_records

GROUP BY category
ORDER BY total_sales DESC;


-- =========================================================
-- 24. QUERY: REUSABLE FUNCTION EXECUTION
-- =========================================================

SELECT
    core_services.calculate_total(
        ARRAY[100, 200, 300, 400]::NUMERIC[]
    ) AS calculated_total;


SELECT
    core_services.calculate_average(
        ARRAY[100, 200, 300, 400]::NUMERIC[]
    ) AS calculated_average;


-- =========================================================
-- 25. QUERY: MODULE REPORTING
-- =========================================================

SELECT *
FROM analytics_services.category_report();


-- =========================================================
-- 26. QUERY: EXECUTION HISTORY
-- =========================================================

SELECT
    module.module_name,
    logs.execution_status,
    logs.execution_message,
    logs.executed_by,
    logs.executed_at

FROM module_lab.execution_logs logs

LEFT JOIN module_lab.modules module
    ON module.module_id = logs.module_id

ORDER BY logs.executed_at DESC;


-- =========================================================
-- 27. DEMONSTRATE TRANSACTION ROLLBACK
-- =========================================================

BEGIN;

UPDATE module_lab.modules
SET status = 'disabled'
WHERE module_name = 'experimental';

-- The change is deliberately rolled back.
ROLLBACK;


-- =========================================================
-- 28. DEMONSTRATE CIRCULAR DEPENDENCY PROTECTION
-- =========================================================

DO $$
DECLARE
    reporting_id BIGINT;
    core_id BIGINT;
BEGIN

    SELECT module_id INTO reporting_id
    FROM module_lab.modules
    WHERE module_name = 'reporting';

    SELECT module_id INTO core_id
    FROM module_lab.modules
    WHERE module_name = 'core';

    BEGIN

        -- reporting already depends indirectly on core.
        -- This attempted reverse dependency creates a cycle.
        INSERT INTO module_lab.module_dependencies (
            module_id,
            dependency_module_id
        )
        VALUES (
            core_id,
            reporting_id
        );

    EXCEPTION
        WHEN raise_exception THEN
            RAISE NOTICE
                'Circular dependency correctly rejected: %',
                SQLERRM;
    END;

END;
$$;


-- =========================================================
-- 29. SECURITY AND ACCESS CONTROL
-- =========================================================

-- Create a restricted application role if it does not exist.
DO $$
BEGIN

    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'module_reader'
    ) THEN

        CREATE ROLE module_reader NOLOGIN;

    END IF;

END;
$$;

GRANT USAGE ON SCHEMA module_lab TO module_reader;

GRANT SELECT
ON module_lab.modules,
   module_lab.module_overview,
   module_lab.dependency_report
TO module_reader;

GRANT EXECUTE
ON FUNCTION module_lab.can_activate(BIGINT)
TO module_reader;

-- Readers cannot modify module registration or dependency records.
REVOKE INSERT, UPDATE, DELETE
ON module_lab.modules,
   module_lab.module_dependencies
FROM module_reader;


-- =========================================================
-- 30. FINAL VALIDATION REPORT
-- =========================================================

SELECT
    module_name,
    module_version,
    status,
    owner_team
FROM module_lab.modules
ORDER BY module_name;

SELECT
    COUNT(*) AS registered_modules,
    COUNT(*) FILTER (
        WHERE status = 'active'
    ) AS active_modules,
    COUNT(*) FILTER (
        WHERE status = 'disabled'
    ) AS disabled_modules,
    COUNT(*) FILTER (
        WHERE status = 'failed'
    ) AS failed_modules
FROM module_lab.modules;

SELECT
    'Module demonstration completed' AS execution_message;
