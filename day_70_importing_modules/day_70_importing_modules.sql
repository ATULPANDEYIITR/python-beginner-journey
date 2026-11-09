/*
IMPORTING MODULES IN POSTGRESQL

PostgreSQL does not use Python-style or Java-style import statements.

Database extensions provide reusable functionality that can be
installed into a database and exposed through schemas.

This script demonstrates:
- Extension installation and inspection
- Schema-qualified objects
- Extension dependency metadata
- Database module registration
- Module versions and compatibility
- Dependency validation
- Transaction-safe activation
- Module import auditing
- Failure handling
- Dependency-aware reporting
- Security-conscious execution

Run using a PostgreSQL 15+ database.

The pgcrypto extension is required and must be available
in the PostgreSQL server installation.
*/


-- =========================================================
-- 1. DATABASE MODULE SCHEMA
-- =========================================================

CREATE SCHEMA IF NOT EXISTS module_lab;

CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- =========================================================
-- 2. MODULE CATALOG
-- =========================================================

CREATE TABLE IF NOT EXISTS module_lab.modules (

    module_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    module_name VARCHAR(100) NOT NULL UNIQUE,

    module_version VARCHAR(30) NOT NULL,

    description TEXT NOT NULL,

    minimum_pg_version INTEGER NOT NULL DEFAULT 150000,

    enabled BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_module_name
        CHECK (module_name ~ '^[a-z][a-z0-9_]*$'),

    CONSTRAINT valid_module_version
        CHECK (
            module_version ~ '^[0-9]+\.[0-9]+\.[0-9]+$'
        ),

    CONSTRAINT valid_minimum_version
        CHECK (minimum_pg_version >= 100000)
);


-- =========================================================
-- 3. MODULE DEPENDENCIES
-- =========================================================

CREATE TABLE IF NOT EXISTS module_lab.module_dependencies (

    module_id BIGINT NOT NULL
        REFERENCES module_lab.modules(module_id)
        ON DELETE CASCADE,

    dependency_id BIGINT NOT NULL
        REFERENCES module_lab.modules(module_id)
        ON DELETE RESTRICT,

    required_version VARCHAR(30),

    PRIMARY KEY (module_id, dependency_id),

    CONSTRAINT no_self_dependency
        CHECK (module_id <> dependency_id),

    CONSTRAINT valid_required_version
        CHECK (
            required_version IS NULL
            OR required_version ~ '^[0-9]+\.[0-9]+\.[0-9]+$'
        )
);


CREATE INDEX IF NOT EXISTS idx_module_dependencies_dependency
ON module_lab.module_dependencies(dependency_id);


-- =========================================================
-- 4. MODULE IMPORT HISTORY
-- =========================================================

CREATE TABLE IF NOT EXISTS module_lab.module_imports (

    import_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    module_id BIGINT NOT NULL
        REFERENCES module_lab.modules(module_id),

    imported_by TEXT NOT NULL,

    import_status VARCHAR(20) NOT NULL,

    imported_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMPTZ,

    error_message TEXT,

    CONSTRAINT valid_import_status
        CHECK (
            import_status IN (
                'PENDING',
                'SUCCESS',
                'FAILED',
                'ROLLED_BACK'
            )
        ),

    CONSTRAINT valid_import_timestamps
        CHECK (
            completed_at IS NULL
            OR completed_at >= imported_at
        ),

    CONSTRAINT valid_import_error
        CHECK (
            import_status <> 'FAILED'
            OR error_message IS NOT NULL
        )
);


CREATE INDEX IF NOT EXISTS idx_module_imports_status_time
ON module_lab.module_imports(import_status, imported_at DESC);


-- =========================================================
-- 5. MODULE OBJECT REGISTRY
-- =========================================================

CREATE TABLE IF NOT EXISTS module_lab.module_objects (

    object_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    module_id BIGINT NOT NULL
        REFERENCES module_lab.modules(module_id)
        ON DELETE CASCADE,

    object_schema VARCHAR(63) NOT NULL,

    object_name VARCHAR(100) NOT NULL,

    object_type VARCHAR(30) NOT NULL,

    registered_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (
        module_id,
        object_schema,
        object_name
    ),

    CONSTRAINT valid_object_type
        CHECK (
            object_type IN (
                'TABLE',
                'VIEW',
                'FUNCTION',
                'PROCEDURE',
                'TYPE'
            )
        )
);


-- =========================================================
-- 6. MODULE ACTIVATION STATE
-- =========================================================

CREATE TABLE IF NOT EXISTS module_lab.module_state (

    module_id BIGINT PRIMARY KEY
        REFERENCES module_lab.modules(module_id),

    state VARCHAR(20) NOT NULL DEFAULT 'REGISTERED',

    activated_at TIMESTAMPTZ,

    last_import_id BIGINT
        REFERENCES module_lab.module_imports(import_id),

    CONSTRAINT valid_module_state
        CHECK (
            state IN (
                'REGISTERED',
                'IMPORTING',
                'ACTIVE',
                'FAILED',
                'DISABLED'
            )
        ),

    CONSTRAINT active_requires_timestamp
        CHECK (
            state <> 'ACTIVE'
            OR activated_at IS NOT NULL
        )
);


-- =========================================================
-- 7. MODULE DEPENDENCY VALIDATION
-- =========================================================

CREATE OR REPLACE FUNCTION module_lab.validate_dependency()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE

    dependency_enabled BOOLEAN;

BEGIN

    SELECT enabled
    INTO dependency_enabled
    FROM module_lab.modules
    WHERE module_id = NEW.dependency_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Referenced dependency does not exist';
    END IF;

    IF NOT dependency_enabled THEN
        RAISE EXCEPTION
            'Dependency module is disabled';
    END IF;

    RETURN NEW;

END;
$$;


DROP TRIGGER IF EXISTS trg_validate_dependency
ON module_lab.module_dependencies;

CREATE TRIGGER trg_validate_dependency

BEFORE INSERT OR UPDATE
ON module_lab.module_dependencies

FOR EACH ROW

EXECUTE FUNCTION module_lab.validate_dependency();


-- =========================================================
-- 8. AUTOMATIC STATE INITIALIZATION
-- =========================================================

CREATE OR REPLACE FUNCTION module_lab.initialize_module_state()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO module_lab.module_state (
        module_id,
        state
    )
    VALUES (
        NEW.module_id,
        CASE
            WHEN NEW.enabled THEN 'REGISTERED'
            ELSE 'DISABLED'
        END
    );

    RETURN NEW;

END;
$$;


DROP TRIGGER IF EXISTS trg_initialize_module_state
ON module_lab.modules;

CREATE TRIGGER trg_initialize_module_state

AFTER INSERT
ON module_lab.modules

FOR EACH ROW

EXECUTE FUNCTION module_lab.initialize_module_state();


-- =========================================================
-- 9. MODULE REGISTRATION FUNCTION
-- =========================================================

CREATE OR REPLACE FUNCTION module_lab.register_module(
    p_name VARCHAR,
    p_version VARCHAR,
    p_description TEXT,
    p_minimum_pg_version INTEGER
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE

    new_module_id BIGINT;

BEGIN

    IF p_name !~ '^[a-z][a-z0-9_]*$' THEN
        RAISE EXCEPTION 'Invalid module name';
    END IF;

    IF p_version !~ '^[0-9]+\.[0-9]+\.[0-9]+$' THEN
        RAISE EXCEPTION 'Invalid module version';
    END IF;

    IF p_minimum_pg_version > current_setting(
        'server_version_num'
    )::INTEGER THEN

        RAISE EXCEPTION
            'Module requires a newer PostgreSQL version';
    END IF;

    INSERT INTO module_lab.modules (
        module_name,
        module_version,
        description,
        minimum_pg_version
    )
    VALUES (
        p_name,
        p_version,
        p_description,
        p_minimum_pg_version
    )
    RETURNING module_id INTO new_module_id;

    RETURN new_module_id;

END;
$$;


-- =========================================================
-- 10. DEPENDENCY-AWARE ACTIVATION
-- =========================================================

CREATE OR REPLACE FUNCTION module_lab.activate_module(
    p_module_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE

    target_module RECORD;

    dependency_record RECORD;

    dependency_state VARCHAR;

    current_import_id BIGINT;

    current_user_name TEXT := session_user;

BEGIN

    SELECT *
    INTO target_module
    FROM module_lab.modules
    WHERE module_id = p_module_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Module not found: %', p_module_id;
    END IF;

    IF NOT target_module.enabled THEN
        RAISE EXCEPTION
            'Module % is disabled',
            target_module.module_name;
    END IF;

    IF target_module.minimum_pg_version >
       current_setting('server_version_num')::INTEGER THEN

        RAISE EXCEPTION
            'PostgreSQL version is incompatible';
    END IF;

    INSERT INTO module_lab.module_imports (
        module_id,
        imported_by,
        import_status
    )
    VALUES (
        p_module_id,
        current_user_name,
        'PENDING'
    )
    RETURNING import_id INTO current_import_id;

    UPDATE module_lab.module_state
    SET
        state = 'IMPORTING',
        last_import_id = current_import_id
    WHERE module_id = p_module_id;

    FOR dependency_record IN

        SELECT
            d.dependency_id,
            m.module_name

        FROM module_lab.module_dependencies d

        JOIN module_lab.modules m
            ON m.module_id = d.dependency_id

        WHERE d.module_id = p_module_id

    LOOP

        SELECT state
        INTO dependency_state
        FROM module_lab.module_state
        WHERE module_id = dependency_record.dependency_id;

        IF dependency_state IS DISTINCT FROM 'ACTIVE' THEN

            RAISE EXCEPTION
                'Dependency % is not active',
                dependency_record.module_name;

        END IF;

    END LOOP;

    UPDATE module_lab.module_state
    SET
        state = 'ACTIVE',
        activated_at = CURRENT_TIMESTAMP,
        last_import_id = current_import_id
    WHERE module_id = p_module_id;

    UPDATE module_lab.module_imports
    SET
        import_status = 'SUCCESS',
        completed_at = CURRENT_TIMESTAMP
    WHERE import_id = current_import_id;

    RETURN current_import_id;

EXCEPTION
    WHEN OTHERS THEN

        IF current_import_id IS NOT NULL THEN

            UPDATE module_lab.module_imports
            SET
                import_status = 'FAILED',
                completed_at = CURRENT_TIMESTAMP,
                error_message = SQLERRM
            WHERE import_id = current_import_id;

            UPDATE module_lab.module_state
            SET
                state = 'FAILED',
                last_import_id = current_import_id
            WHERE module_id = p_module_id;

        END IF;

        RAISE;

END;
$$;


-- =========================================================
-- 11. SAFE ACTIVATION PROCEDURE
-- =========================================================

CREATE OR REPLACE PROCEDURE module_lab.import_module(
    p_module_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE

    generated_import_id BIGINT;

BEGIN

    generated_import_id :=
        module_lab.activate_module(p_module_id);

    RAISE NOTICE
        'Module activated. Import ID: %',
        generated_import_id;

END;
$$;


-- =========================================================
-- 12. SAMPLE MODULE REGISTRATION
-- =========================================================

INSERT INTO module_lab.modules (
    module_name,
    module_version,
    description,
    minimum_pg_version
)
VALUES
(
    'configuration',
    '1.0.0',
    'Application configuration management',
    150000
),
(
    'data_access',
    '2.0.0',
    'Database access and persistence',
    150000
),
(
    'analytics',
    '1.2.0',
    'Statistical processing and reporting',
    150000
),
(
    'reporting',
    '1.0.0',
    'Business reporting functionality',
    150000
),
(
    'experimental',
    '0.9.0',
    'Experimental functionality disabled for production',
    150000
);


UPDATE module_lab.modules
SET enabled = FALSE
WHERE module_name = 'experimental';


-- =========================================================
-- 13. SAMPLE DEPENDENCY REGISTRATION
-- =========================================================

INSERT INTO module_lab.module_dependencies (
    module_id,
    dependency_id,
    required_version
)
SELECT
    child.module_id,
    parent.module_id,
    CASE child.module_name
        WHEN 'data_access' THEN '1.0.0'
        WHEN 'analytics' THEN '2.0.0'
        WHEN 'reporting' THEN '1.2.0'
    END
FROM module_lab.modules child
JOIN module_lab.modules parent
    ON (
        (child.module_name = 'data_access'
         AND parent.module_name = 'configuration')

        OR

        (child.module_name = 'analytics'
         AND parent.module_name = 'data_access')

        OR

        (child.module_name = 'reporting'
         AND parent.module_name = 'analytics')
    );


-- =========================================================
-- 14. REGISTER MODULE OBJECTS
-- =========================================================

INSERT INTO module_lab.module_objects (
    module_id,
    object_schema,
    object_name,
    object_type
)
SELECT
    module_id,
    'public',
    object_name,
    object_type
FROM (
    VALUES
        ('configuration', 'application_settings', 'TABLE'),
        ('data_access', 'connection_status', 'VIEW'),
        ('analytics', 'calculate_metrics', 'FUNCTION'),
        ('reporting', 'generate_report', 'FUNCTION')
) AS objects(module_name, object_name, object_type)
JOIN module_lab.modules
    USING (module_name);


-- =========================================================
-- 15. ACTIVATE MODULES IN DEPENDENCY ORDER
-- =========================================================

DO $$
DECLARE

    current_module RECORD;

BEGIN

    FOR current_module IN

        SELECT
            module_id,
            module_name

        FROM module_lab.modules

        WHERE module_name IN (
            'configuration',
            'data_access',
            'analytics',
            'reporting'
        )

        ORDER BY CASE module_name
            WHEN 'configuration' THEN 1
            WHEN 'data_access' THEN 2
            WHEN 'analytics' THEN 3
            WHEN 'reporting' THEN 4
        END

    LOOP

        CALL module_lab.import_module(
            current_module.module_id
        );

    END LOOP;

END;
$$;


-- =========================================================
-- 16. EXPECTED FAILURE CASE
-- =========================================================

DO $$
DECLARE

    experimental_id BIGINT;

BEGIN

    SELECT module_id
    INTO experimental_id
    FROM module_lab.modules
    WHERE module_name = 'experimental';

    BEGIN

        PERFORM module_lab.activate_module(
            experimental_id
        );

    EXCEPTION
        WHEN OTHERS THEN

            RAISE NOTICE
                'Expected activation failure: %',
                SQLERRM;

    END;

END;
$$;


-- =========================================================
-- 17. MODULE INVENTORY VIEW
-- =========================================================

CREATE OR REPLACE VIEW module_lab.module_inventory AS

SELECT

    m.module_id,

    m.module_name,

    m.module_version,

    m.enabled,

    s.state,

    s.activated_at,

    COUNT(DISTINCT d.dependency_id) AS dependency_count,

    COUNT(DISTINCT o.object_id) AS registered_objects

FROM module_lab.modules m

LEFT JOIN module_lab.module_state s
    ON s.module_id = m.module_id

LEFT JOIN module_lab.module_dependencies d
    ON d.module_id = m.module_id

LEFT JOIN module_lab.module_objects o
    ON o.module_id = m.module_id

GROUP BY
    m.module_id,
    m.module_name,
    m.module_version,
    m.enabled,
    s.state,
    s.activated_at;


-- =========================================================
-- 18. DEPENDENCY VALIDATION REPORT
-- =========================================================

WITH dependency_report AS (

    SELECT

        m.module_name,

        dependency.module_name AS dependency_name,

        dependency_state.state AS dependency_state,

        dependency.enabled AS dependency_enabled

    FROM module_lab.module_dependencies d

    JOIN module_lab.modules m
        ON m.module_id = d.module_id

    JOIN module_lab.modules dependency
        ON dependency.module_id = d.dependency_id

    LEFT JOIN module_lab.module_state dependency_state
        ON dependency_state.module_id = dependency.module_id

)

SELECT

    module_name,

    dependency_name,

    dependency_state,

    dependency_enabled,

    CASE

        WHEN NOT dependency_enabled THEN 'DISABLED'

        WHEN dependency_state IS DISTINCT FROM 'ACTIVE'
            THEN 'NOT_ACTIVE'

        ELSE 'READY'

    END AS dependency_validation

FROM dependency_report

ORDER BY module_name, dependency_name;


-- =========================================================
-- 19. IMPORT HISTORY REPORT
-- =========================================================

SELECT

    m.module_name,

    i.import_id,

    i.imported_by,

    i.import_status,

    i.imported_at,

    i.completed_at,

    i.error_message

FROM module_lab.module_imports i

JOIN module_lab.modules m
    ON m.module_id = i.module_id

ORDER BY i.imported_at DESC;


-- =========================================================
-- 20. MODULE USAGE AGGREGATION
-- =========================================================

SELECT

    m.module_name,

    COUNT(i.import_id) AS total_import_attempts,

    COUNT(*) FILTER (
        WHERE i.import_status = 'SUCCESS'
    ) AS successful_imports,

    COUNT(*) FILTER (
        WHERE i.import_status = 'FAILED'
    ) AS failed_imports

FROM module_lab.modules m

LEFT JOIN module_lab.module_imports i
    ON i.module_id = m.module_id

GROUP BY m.module_id, m.module_name

ORDER BY total_import_attempts DESC;


-- =========================================================
-- 21. ELIGIBILITY DETERMINATION
-- =========================================================

SELECT

    m.module_name,

    m.enabled,

    s.state,

    CASE

        WHEN NOT m.enabled
            THEN 'INELIGIBLE_DISABLED'

        WHEN s.state = 'ACTIVE'
            THEN 'ELIGIBLE'

        WHEN EXISTS (

            SELECT 1

            FROM module_lab.module_dependencies d

            JOIN module_lab.module_state dependency_state
                ON dependency_state.module_id = d.dependency_id

            WHERE d.module_id = m.module_id

              AND dependency_state.state <> 'ACTIVE'

        )
            THEN 'BLOCKED_DEPENDENCY'

        ELSE 'PENDING_ACTIVATION'

    END AS eligibility

FROM module_lab.modules m

JOIN module_lab.module_state s
    ON s.module_id = m.module_id

ORDER BY m.module_name;


-- =========================================================
-- 22. TRANSACTIONAL REGISTRATION EXAMPLE
-- =========================================================

BEGIN;

DO $$
DECLARE

    new_module_id BIGINT;

BEGIN

    new_module_id := module_lab.register_module(
        'audit_tools',
        '1.0.0',
        'Database audit utilities',
        150000
    );

    RAISE NOTICE
        'Registered module ID: %',
        new_module_id;

END;
$$;

COMMIT;


-- =========================================================
-- 23. EXTENSION INVENTORY
-- =========================================================

SELECT

    e.extname AS extension_name,

    e.extversion AS installed_version,

    n.nspname AS extension_schema

FROM pg_extension e

JOIN pg_namespace n
    ON n.oid = e.extnamespace

ORDER BY e.extname;


-- =========================================================
-- 24. MODULE OBJECT LOOKUP
-- =========================================================

SELECT

    m.module_name,

    o.object_schema,

    o.object_name,

    o.object_type,

    o.registered_at

FROM module_lab.module_objects o

JOIN module_lab.modules m
    ON m.module_id = o.module_id

ORDER BY m.module_name, o.object_name;


-- =========================================================
-- 25. FINAL MODULE INVENTORY
-- =========================================================

SELECT *
FROM module_lab.module_inventory
ORDER BY module_name;
