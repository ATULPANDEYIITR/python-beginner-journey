-- ============================================================
-- CREATING YOUR OWN MODULES
-- PostgreSQL 16+
--
-- Models:
-- Module catalog
-- Module versions
-- Module dependencies
-- Module interfaces and permissions
-- Module registration
-- Configuration
-- Lifecycle transitions
-- Module executions
-- Execution auditing
-- Dependency validation
-- Activation eligibility
-- Failure tracking
--
-- Execute as a database owner in a dedicated database.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS module_platform;

SET search_path TO module_platform, public;

-- ------------------------------------------------------------
-- 1. ENUMERATIONS
-- ------------------------------------------------------------

CREATE TYPE module_state AS ENUM (
    'registered',
    'initialized',
    'active',
    'failed',
    'disabled'
);

CREATE TYPE module_visibility AS ENUM (
    'public',
    'internal',
    'private'
);

CREATE TYPE execution_status AS ENUM (
    'running',
    'completed',
    'failed'
);

-- ------------------------------------------------------------
-- 2. MODULE CATALOG
-- ------------------------------------------------------------

CREATE TABLE modules (
    module_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    module_name VARCHAR(100) NOT NULL UNIQUE,

    version_major INTEGER NOT NULL CHECK (version_major >= 0),
    version_minor INTEGER NOT NULL CHECK (version_minor >= 0),
    version_patch INTEGER NOT NULL CHECK (version_patch >= 0),

    description TEXT NOT NULL,

    owner_name VARCHAR(150) NOT NULL,

    visibility module_visibility NOT NULL DEFAULT 'internal',

    lifecycle_state module_state NOT NULL DEFAULT 'registered',

    enabled BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    last_error TEXT,

    CHECK (
        module_name ~ '^[a-z][a-z0-9_]*$'
    ),

    CHECK (length(trim(description)) > 0),

    CHECK (length(trim(owner_name)) > 0)
);

CREATE INDEX idx_modules_state
ON modules(lifecycle_state, enabled);

CREATE INDEX idx_modules_owner
ON modules(owner_name);

-- ------------------------------------------------------------
-- 3. MODULE INTERFACES
-- ------------------------------------------------------------

CREATE TABLE module_interfaces (
    interface_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    module_id BIGINT NOT NULL REFERENCES modules(module_id)
        ON DELETE CASCADE,

    interface_name VARCHAR(120) NOT NULL,

    interface_version VARCHAR(30) NOT NULL,

    interface_description TEXT NOT NULL,

    input_schema JSONB NOT NULL DEFAULT '{}'::jsonb,

    output_schema JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(module_id, interface_name),

    CHECK (length(trim(interface_name)) > 0),

    CHECK (
        interface_version ~ '^[0-9]+\.[0-9]+\.[0-9]+$'
    ),

    CHECK (jsonb_typeof(input_schema) = 'object'),

    CHECK (jsonb_typeof(output_schema) = 'object')
);

CREATE INDEX idx_interfaces_module
ON module_interfaces(module_id);

-- ------------------------------------------------------------
-- 4. PERMISSION CATALOG
-- ------------------------------------------------------------

CREATE TABLE permissions (
    permission_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    permission_code VARCHAR(80) NOT NULL UNIQUE,

    description TEXT NOT NULL,

    CHECK (
        permission_code ~ '^[a-z][a-z0-9_]*$'
    )
);

INSERT INTO permissions (
    permission_code,
    description
)
VALUES
    ('read_data', 'Read permitted application data'),
    ('write_data', 'Modify permitted application data'),
    ('calculate', 'Perform numerical calculations'),
    ('export_data', 'Export authorized reports'),
    ('manage_configuration', 'Manage module configuration')
ON CONFLICT (permission_code) DO NOTHING;

CREATE TABLE module_permissions (
    module_id BIGINT NOT NULL REFERENCES modules(module_id)
        ON DELETE CASCADE,

    permission_id BIGINT NOT NULL REFERENCES permissions(permission_id),

    granted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    granted_by VARCHAR(150) NOT NULL,

    PRIMARY KEY(module_id, permission_id)
);

-- ------------------------------------------------------------
-- 5. MODULE DEPENDENCIES
-- ------------------------------------------------------------

CREATE TABLE module_dependencies (
    dependency_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    module_id BIGINT NOT NULL REFERENCES modules(module_id)
        ON DELETE CASCADE,

    depends_on_module_id BIGINT NOT NULL REFERENCES modules(module_id),

    minimum_major INTEGER NOT NULL DEFAULT 1 CHECK (minimum_major >= 0),

    minimum_minor INTEGER NOT NULL DEFAULT 0 CHECK (minimum_minor >= 0),

    minimum_patch INTEGER NOT NULL DEFAULT 0 CHECK (minimum_patch >= 0),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(module_id, depends_on_module_id),

    CHECK (module_id <> depends_on_module_id)
);

CREATE INDEX idx_dependencies_target
ON module_dependencies(depends_on_module_id);

-- ------------------------------------------------------------
-- 6. MODULE CONFIGURATION
-- ------------------------------------------------------------

CREATE TABLE module_configurations (
    configuration_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    module_id BIGINT NOT NULL REFERENCES modules(module_id)
        ON DELETE CASCADE,

    configuration_name VARCHAR(120) NOT NULL,

    configuration JSONB NOT NULL DEFAULT '{}'::jsonb,

    revision INTEGER NOT NULL DEFAULT 1 CHECK (revision > 0),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(module_id, configuration_name),

    CHECK (jsonb_typeof(configuration) = 'object')
);

CREATE INDEX idx_module_configuration
ON module_configurations(module_id);

-- ------------------------------------------------------------
-- 7. MODULE EXECUTION HISTORY
-- ------------------------------------------------------------

CREATE TABLE module_executions (
    execution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    module_id BIGINT NOT NULL REFERENCES modules(module_id),

    execution_uuid UUID NOT NULL UNIQUE,

    requested_by VARCHAR(150) NOT NULL,

    input_payload JSONB NOT NULL DEFAULT '{}'::jsonb,

    output_payload JSONB,

    execution_state execution_status NOT NULL DEFAULT 'running',

    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMPTZ,

    duration_ms NUMERIC(14, 3),

    error_message TEXT,

    CHECK (jsonb_typeof(input_payload) = 'object'),

    CHECK (
        output_payload IS NULL OR
        jsonb_typeof(output_payload) IN ('object', 'array')
    ),

    CHECK (
        duration_ms IS NULL OR duration_ms >= 0
    ),

    CHECK (
        (
            execution_state = 'running'
            AND completed_at IS NULL
        )
        OR
        (
            execution_state IN ('completed', 'failed')
            AND completed_at IS NOT NULL
        )
    )
);

CREATE INDEX idx_execution_module_date
ON module_executions(module_id, started_at DESC);

CREATE INDEX idx_execution_failures
ON module_executions(module_id, started_at DESC)
WHERE execution_state = 'failed';

-- ------------------------------------------------------------
-- 8. MODULE AUDIT LOG
-- ------------------------------------------------------------

CREATE TABLE module_audit_log (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    module_id BIGINT REFERENCES modules(module_id)
        ON DELETE SET NULL,

    action VARCHAR(80) NOT NULL,

    actor VARCHAR(150) NOT NULL,

    previous_state module_state,

    new_state module_state,

    details JSONB NOT NULL DEFAULT '{}'::jsonb,

    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (jsonb_typeof(details) = 'object')
);

CREATE INDEX idx_module_audit_date
ON module_audit_log(occurred_at DESC);

CREATE INDEX idx_module_audit_module
ON module_audit_log(module_id, occurred_at DESC);

-- ------------------------------------------------------------
-- 9. AUTOMATIC UPDATED_AT MANAGEMENT
-- ------------------------------------------------------------

CREATE FUNCTION update_modified_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_modules_updated
BEFORE UPDATE ON modules
FOR EACH ROW
EXECUTE FUNCTION update_modified_timestamp();

CREATE TRIGGER trg_config_updated
BEFORE UPDATE ON module_configurations
FOR EACH ROW
EXECUTE FUNCTION update_modified_timestamp();

-- ------------------------------------------------------------
-- 10. MODULE STATE TRANSITION ENFORCEMENT
-- ------------------------------------------------------------

CREATE FUNCTION validate_module_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.lifecycle_state = OLD.lifecycle_state THEN
        RETURN NEW;
    END IF;

    IF NOT (
        (OLD.lifecycle_state = 'registered'
            AND NEW.lifecycle_state IN ('initialized', 'failed', 'disabled'))

        OR

        (OLD.lifecycle_state = 'initialized'
            AND NEW.lifecycle_state IN ('active', 'failed', 'disabled'))

        OR

        (OLD.lifecycle_state = 'active'
            AND NEW.lifecycle_state IN ('failed', 'disabled'))

        OR

        (OLD.lifecycle_state = 'failed'
            AND NEW.lifecycle_state IN ('registered', 'disabled'))

        OR

        (OLD.lifecycle_state = 'disabled'
            AND NEW.lifecycle_state = 'registered')
    ) THEN
        RAISE EXCEPTION
            'Invalid module state transition: % -> %',
            OLD.lifecycle_state,
            NEW.lifecycle_state;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_module_transition
BEFORE UPDATE OF lifecycle_state ON modules
FOR EACH ROW
EXECUTE FUNCTION validate_module_transition();

-- ------------------------------------------------------------
-- 11. DEPENDENCY CYCLE DETECTION
-- ------------------------------------------------------------

CREATE FUNCTION prevent_dependency_cycle()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    cycle_found BOOLEAN;
BEGIN
    WITH RECURSIVE dependency_path(module_id) AS (
        SELECT NEW.depends_on_module_id

        UNION

        SELECT dependency.depends_on_module_id
        FROM module_dependencies dependency
        INNER JOIN dependency_path path
            ON dependency.module_id = path.module_id
    )
    SELECT EXISTS (
        SELECT 1
        FROM dependency_path
        WHERE module_id = NEW.module_id
    )
    INTO cycle_found;

    IF cycle_found THEN
        RAISE EXCEPTION
            'Circular module dependency detected.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_dependency_cycle
BEFORE INSERT OR UPDATE ON module_dependencies
FOR EACH ROW
EXECUTE FUNCTION prevent_dependency_cycle();

-- ------------------------------------------------------------
-- 12. DEPENDENCY AND VERSION VALIDATION
-- ------------------------------------------------------------

CREATE FUNCTION validate_module_dependencies(
    p_module_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    dependency RECORD;
BEGIN
    FOR dependency IN
        SELECT
            required.module_id,
            required.module_name,
            required.version_major,
            required.version_minor,
            required.version_patch,
            required.enabled,
            required.lifecycle_state,
            requirement.minimum_major,
            requirement.minimum_minor,
            requirement.minimum_patch
        FROM module_dependencies requirement
        INNER JOIN modules required
            ON required.module_id =
               requirement.depends_on_module_id
        WHERE requirement.module_id = p_module_id
    LOOP

        IF NOT dependency.enabled THEN
            RAISE EXCEPTION
                'Dependency % is disabled.',
                dependency.module_name;
        END IF;

        IF dependency.lifecycle_state NOT IN (
            'initialized',
            'active'
        ) THEN
            RAISE EXCEPTION
                'Dependency % is not initialized.',
                dependency.module_name;
        END IF;

        IF ROW(
            dependency.version_major,
            dependency.version_minor,
            dependency.version_patch
        ) < ROW(
            dependency.minimum_major,
            dependency.minimum_minor,
            dependency.minimum_patch
        ) THEN
            RAISE EXCEPTION
                'Dependency % does not meet minimum version.',
                dependency.module_name;
        END IF;

    END LOOP;

    RETURN TRUE;
END;
$$;

-- ------------------------------------------------------------
-- 13. MODULE ACTIVATION
-- ------------------------------------------------------------

CREATE PROCEDURE activate_module(
    p_module_id BIGINT,
    p_actor VARCHAR(150)
)
LANGUAGE plpgsql
AS $$
DECLARE
    target RECORD;
BEGIN
    SELECT *
    INTO target
    FROM modules
    WHERE module_id = p_module_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Module not found.';
    END IF;

    IF NOT target.enabled THEN
        RAISE EXCEPTION 'Module is disabled.';
    END IF;

    IF target.lifecycle_state = 'active' THEN
        RETURN;
    END IF;

    IF target.lifecycle_state NOT IN (
        'registered',
        'initialized'
    ) THEN
        RAISE EXCEPTION
            'Module cannot be activated from state %.',
            target.lifecycle_state;
    END IF;

    PERFORM validate_module_dependencies(p_module_id);

    IF target.lifecycle_state = 'registered' THEN
        UPDATE modules
        SET lifecycle_state = 'initialized'
        WHERE module_id = p_module_id;
    END IF;

    UPDATE modules
    SET lifecycle_state = 'active',
        last_error = NULL
    WHERE module_id = p_module_id;

    INSERT INTO module_audit_log (
        module_id,
        action,
        actor,
        previous_state,
        new_state
    )
    VALUES (
        p_module_id,
        'MODULE_ACTIVATED',
        p_actor,
        target.lifecycle_state,
        'active'
    );
END;
$$;

-- ------------------------------------------------------------
-- 14. MODULE REGISTRATION PROCEDURE
-- ------------------------------------------------------------

CREATE PROCEDURE register_module(
    p_name VARCHAR(100),
    p_major INTEGER,
    p_minor INTEGER,
    p_patch INTEGER,
    p_description TEXT,
    p_owner VARCHAR(150),
    p_actor VARCHAR(150),
    INOUT p_module_id BIGINT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO modules (
        module_name,
        version_major,
        version_minor,
        version_patch,
        description,
        owner_name
    )
    VALUES (
        p_name,
        p_major,
        p_minor,
        p_patch,
        p_description,
        p_owner
    )
    RETURNING module_id INTO p_module_id;

    INSERT INTO module_audit_log (
        module_id,
        action,
        actor,
        new_state
    )
    VALUES (
        p_module_id,
        'MODULE_REGISTERED',
        p_actor,
        'registered'
    );
END;
$$;

-- ------------------------------------------------------------
-- 15. EXECUTION COMPLETION
-- ------------------------------------------------------------

CREATE FUNCTION complete_module_execution(
    p_execution_id BIGINT,
    p_output JSONB
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    execution_record RECORD;
BEGIN
    IF jsonb_typeof(p_output) NOT IN ('object', 'array') THEN
        RAISE EXCEPTION 'Output must be a JSON object or array.';
    END IF;

    SELECT *
    INTO execution_record
    FROM module_executions
    WHERE execution_id = p_execution_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Execution not found.';
    END IF;

    IF execution_record.execution_state <> 'running' THEN
        RAISE EXCEPTION 'Execution is already finalized.';
    END IF;

    UPDATE module_executions
    SET output_payload = p_output,
        execution_state = 'completed',
        completed_at = CURRENT_TIMESTAMP,
        duration_ms = EXTRACT(
            EPOCH FROM (
                CURRENT_TIMESTAMP - started_at
            )
        ) * 1000
    WHERE execution_id = p_execution_id;
END;
$$;

CREATE FUNCTION fail_module_execution(
    p_execution_id BIGINT,
    p_error TEXT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_error IS NULL OR length(trim(p_error)) = 0 THEN
        RAISE EXCEPTION 'Failure reason is required.';
    END IF;

    UPDATE module_executions
    SET execution_state = 'failed',
        error_message = p_error,
        completed_at = CURRENT_TIMESTAMP,
        duration_ms = EXTRACT(
            EPOCH FROM (
                CURRENT_TIMESTAMP - started_at
            )
        ) * 1000
    WHERE execution_id = p_execution_id
      AND execution_state = 'running';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Running execution not found or already finalized.';
    END IF;
END;
$$;

-- ------------------------------------------------------------
-- 16. SAMPLE MODULES
-- ------------------------------------------------------------

INSERT INTO modules (
    module_name,
    version_major,
    version_minor,
    version_patch,
    description,
    owner_name
)
VALUES
(
    'analytics',
    2,
    1,
    0,
    'Reusable numerical analytics functionality',
    'Data Engineering'
),
(
    'reporting',
    1,
    0,
    0,
    'Structured reporting functionality',
    'Business Intelligence'
),
(
    'notification',
    1,
    2,
    0,
    'Application notification functionality',
    'Platform Engineering'
),
(
    'experimental',
    0,
    1,
    0,
    'Experimental module for development testing',
    'Research Engineering'
);

-- ------------------------------------------------------------
-- 17. SAMPLE INTERFACES
-- ------------------------------------------------------------

INSERT INTO module_interfaces (
    module_id,
    interface_name,
    interface_version,
    interface_description,
    input_schema,
    output_schema
)
SELECT
    module_id,
    'calculate',
    '1.0.0',
    'Calculate aggregate numerical values',
    '{"operation":"string","values":"number[]"}',
    '{"result":"number","input_count":"integer"}'
FROM modules
WHERE module_name = 'analytics';

INSERT INTO module_interfaces (
    module_id,
    interface_name,
    interface_version,
    interface_description,
    input_schema,
    output_schema
)
SELECT
    module_id,
    'generate_report',
    '1.0.0',
    'Generate structured reports',
    '{"records":"array"}',
    '{"report":"object"}'
FROM modules
WHERE module_name = 'reporting';

-- ------------------------------------------------------------
-- 18. PERMISSION ASSIGNMENTS
-- ------------------------------------------------------------

INSERT INTO module_permissions (
    module_id,
    permission_id,
    granted_by
)
SELECT
    module.module_id,
    permission.permission_id,
    'platform_admin'
FROM modules module
CROSS JOIN permissions permission
WHERE
    (
        module.module_name = 'analytics'
        AND permission.permission_code = 'calculate'
    )
    OR
    (
        module.module_name = 'reporting'
        AND permission.permission_code IN (
            'read_data',
            'export_data'
        )
    )
    OR
    (
        module.module_name = 'notification'
        AND permission.permission_code IN (
            'read_data',
            'write_data'
        )
    );

-- ------------------------------------------------------------
-- 19. MODULE DEPENDENCIES
-- ------------------------------------------------------------

INSERT INTO module_dependencies (
    module_id,
    depends_on_module_id,
    minimum_major,
    minimum_minor,
    minimum_patch
)
SELECT
    reporting.module_id,
    analytics.module_id,
    2,
    0,
    0
FROM modules reporting
CROSS JOIN modules analytics
WHERE reporting.module_name = 'reporting'
  AND analytics.module_name = 'analytics';

INSERT INTO module_dependencies (
    module_id,
    depends_on_module_id,
    minimum_major,
    minimum_minor,
    minimum_patch
)
SELECT
    notification.module_id,
    analytics.module_id,
    2,
    0,
    0
FROM modules notification
CROSS JOIN modules analytics
WHERE notification.module_name = 'notification'
  AND analytics.module_name = 'analytics';

-- ------------------------------------------------------------
-- 20. MODULE CONFIGURATION
-- ------------------------------------------------------------

INSERT INTO module_configurations (
    module_id,
    configuration_name,
    configuration
)
SELECT
    module_id,
    'default',
    '{"precision":3,"maximum_records":10000}'
FROM modules
WHERE module_name = 'analytics';

INSERT INTO module_configurations (
    module_id,
    configuration_name,
    configuration
)
SELECT
    module_id,
    'default',
    '{"report_title":"Quarterly Analytics","format":"json"}'
FROM modules
WHERE module_name = 'reporting';

-- ------------------------------------------------------------
-- 21. ACTIVATE DEPENDENCIES FIRST
-- ------------------------------------------------------------

CALL activate_module(
    (SELECT module_id FROM modules WHERE module_name = 'analytics'),
    'platform_admin'
);

CALL activate_module(
    (SELECT module_id FROM modules WHERE module_name = 'reporting'),
    'platform_admin'
);

CALL activate_module(
    (SELECT module_id FROM modules WHERE module_name = 'notification'),
    'platform_admin'
);

-- ------------------------------------------------------------
-- 22. SAMPLE EXECUTIONS
-- ------------------------------------------------------------

INSERT INTO module_executions (
    module_id,
    execution_uuid,
    requested_by,
    input_payload
)
SELECT
    module_id,
    gen_random_uuid(),
    'analytics_service',
    '{"operation":"average","values":[100,150,200,250]}'
FROM modules
WHERE module_name = 'analytics'
RETURNING execution_id;

-- Complete a known running execution using its UUID.
WITH selected_execution AS (
    SELECT execution_id
    FROM module_executions execution
    INNER JOIN modules module
        ON module.module_id = execution.module_id
    WHERE module.module_name = 'analytics'
    ORDER BY execution_id DESC
    LIMIT 1
)
SELECT complete_module_execution(
    execution_id,
    '{"operation":"average","result":175,"input_count":4}'
)
FROM selected_execution;

-- Create a deliberately failed execution.
INSERT INTO module_executions (
    module_id,
    execution_uuid,
    requested_by,
    input_payload
)
SELECT
    module_id,
    gen_random_uuid(),
    'test_runner',
    '{"operation":"unknown","values":[1,2]}'
FROM modules
WHERE module_name = 'analytics'
RETURNING execution_id;

WITH failed_execution AS (
    SELECT execution_id
    FROM module_executions execution
    INNER JOIN modules module
        ON module.module_id = execution.module_id
    WHERE module.module_name = 'analytics'
      AND execution.execution_state = 'running'
      AND execution.requested_by = 'test_runner'
    ORDER BY execution_id DESC
    LIMIT 1
)
SELECT fail_module_execution(
    execution_id,
    'Unsupported operation requested.'
)
FROM failed_execution;

-- ------------------------------------------------------------
-- 23. MODULE DISCOVERY
-- ------------------------------------------------------------

CREATE VIEW module_catalog AS
SELECT
    module.module_id,
    module.module_name,
    module.version_major || '.' ||
        module.version_minor || '.' ||
        module.version_patch AS version,
    module.description,
    module.owner_name,
    module.visibility,
    module.lifecycle_state,
    module.enabled,
    COUNT(DISTINCT interface.interface_id) AS interface_count,
    COUNT(DISTINCT dependency.dependency_id) AS dependency_count
FROM modules module
LEFT JOIN module_interfaces interface
    ON interface.module_id = module.module_id
LEFT JOIN module_dependencies dependency
    ON dependency.module_id = module.module_id
GROUP BY module.module_id;

-- ------------------------------------------------------------
-- 24. DEPENDENCY REPORT
-- ------------------------------------------------------------

CREATE VIEW module_dependency_report AS
SELECT
    source.module_name AS module_name,
    source.version_major || '.' ||
        source.version_minor || '.' ||
        source.version_patch AS module_version,
    target.module_name AS dependency_name,
    target.version_major || '.' ||
        target.version_minor || '.' ||
        target.version_patch AS dependency_version,
    dependency.minimum_major || '.' ||
        dependency.minimum_minor || '.' ||
        dependency.minimum_patch AS minimum_required_version,
    target.lifecycle_state AS dependency_state
FROM module_dependencies dependency
INNER JOIN modules source
    ON source.module_id = dependency.module_id
INNER JOIN modules target
    ON target.module_id = dependency.depends_on_module_id;

-- ------------------------------------------------------------
-- 25. ACTIVATION ELIGIBILITY
-- ------------------------------------------------------------

CREATE VIEW module_activation_eligibility AS
SELECT
    module.module_id,
    module.module_name,
    module.lifecycle_state,
    module.enabled,
    NOT EXISTS (
        SELECT 1
        FROM module_dependencies dependency
        INNER JOIN modules required
            ON required.module_id =
               dependency.depends_on_module_id
        WHERE dependency.module_id = module.module_id
          AND (
              required.enabled = FALSE
              OR required.lifecycle_state NOT IN (
                  'initialized',
                  'active'
              )
              OR ROW(
                  required.version_major,
                  required.version_minor,
                  required.version_patch
              ) < ROW(
                  dependency.minimum_major,
                  dependency.minimum_minor,
                  dependency.minimum_patch
              )
          )
    ) AS dependencies_satisfied
FROM modules module;

-- ------------------------------------------------------------
-- 26. MODULE EXECUTION AGGREGATION
-- ------------------------------------------------------------

CREATE VIEW module_execution_summary AS
SELECT
    module.module_name,
    COUNT(execution.execution_id) AS total_executions,
    COUNT(*) FILTER (
        WHERE execution.execution_state = 'completed'
    ) AS successful_executions,
    COUNT(*) FILTER (
        WHERE execution.execution_state = 'failed'
    ) AS failed_executions,
    ROUND(
        AVG(execution.duration_ms),
        3
    ) AS average_duration_ms,
    MAX(execution.started_at) AS latest_execution
FROM modules module
LEFT JOIN module_executions execution
    ON execution.module_id = module.module_id
GROUP BY module.module_id, module.module_name;

-- ------------------------------------------------------------
-- 27. REPORTING QUERIES
-- ------------------------------------------------------------

-- Query A: All registered modules.
SELECT *
FROM module_catalog
ORDER BY module_name;

-- Query B: Interfaces and their contracts.
SELECT
    module.module_name,
    interface.interface_name,
    interface.interface_version,
    interface.input_schema,
    interface.output_schema
FROM module_interfaces interface
INNER JOIN modules module
    ON module.module_id = interface.module_id
ORDER BY module.module_name;

-- Query C: Dependencies and version requirements.
SELECT *
FROM module_dependency_report
ORDER BY module_name;

-- Query D: Activation eligibility.
SELECT *
FROM module_activation_eligibility
ORDER BY module_name;

-- Query E: Module execution performance.
SELECT *
FROM module_execution_summary
ORDER BY total_executions DESC;

-- Query F: Execution failure analysis.
SELECT
    module.module_name,
    execution.error_message,
    execution.started_at
FROM module_executions execution
INNER JOIN modules module
    ON module.module_id = execution.module_id
WHERE execution.execution_state = 'failed'
ORDER BY execution.started_at DESC;

-- Query G: Permission assignments.
SELECT
    module.module_name,
    permission.permission_code,
    assignment.granted_by
FROM module_permissions assignment
INNER JOIN modules module
    ON module.module_id = assignment.module_id
INNER JOIN permissions permission
    ON permission.permission_id = assignment.permission_id
ORDER BY module.module_name, permission.permission_code;

-- Query H: Recursive dependency hierarchy.
WITH RECURSIVE dependency_tree AS (
    SELECT
        module_id,
        depends_on_module_id,
        1 AS depth,
        ARRAY[module_id, depends_on_module_id] AS path
    FROM module_dependencies

    UNION ALL

    SELECT
        tree.module_id,
        dependency.depends_on_module_id,
        tree.depth + 1,
        tree.path || dependency.depends_on_module_id
    FROM dependency_tree tree
    INNER JOIN module_dependencies dependency
        ON dependency.module_id = tree.depends_on_module_id
    WHERE NOT dependency.depends_on_module_id = ANY(tree.path)
)
SELECT
    source.module_name,
    target.module_name AS dependency_name,
    tree.depth
FROM dependency_tree tree
INNER JOIN modules source
    ON source.module_id = tree.module_id
INNER JOIN modules target
    ON target.module_id = tree.depends_on_module_id
ORDER BY source.module_name, tree.depth;

-- Query I: Latest execution per module.
SELECT DISTINCT ON (module_id)
    module_id,
    execution_uuid,
    execution_state,
    started_at,
    completed_at,
    error_message
FROM module_executions
ORDER BY module_id, started_at DESC;

-- Query J: Configuration revision inventory.
SELECT
    module.module_name,
    configuration.configuration_name,
    configuration.revision,
    configuration.configuration
FROM module_configurations configuration
INNER JOIN modules module
    ON module.module_id = configuration.module_id;

-- ------------------------------------------------------------
-- 28. TRANSACTIONAL FAILURE DEMONSTRATION
-- ------------------------------------------------------------

-- The invalid operation is rolled back automatically.
-- It does not alter an existing module.

DO $$
DECLARE
    target_id BIGINT;
BEGIN
    SELECT module_id
    INTO target_id
    FROM modules
    WHERE module_name = 'analytics';

    BEGIN
        UPDATE modules
        SET lifecycle_state = 'disabled'
        WHERE module_id = target_id;

        -- The transition is permitted, so the nested block
        -- is rolled back deliberately.
        RAISE EXCEPTION 'Demonstration rollback.';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Transactional demonstration: %',
                SQLERRM;
    END;
END;
$$;

-- ------------------------------------------------------------
-- 29. AUDIT REPORT
-- ------------------------------------------------------------

SELECT
    audit.action,
    audit.actor,
    module.module_name,
    audit.previous_state,
    audit.new_state,
    audit.occurred_at
FROM module_audit_log audit
LEFT JOIN modules module
    ON module.module_id = audit.module_id
ORDER BY audit.occurred_at DESC;

COMMIT;
