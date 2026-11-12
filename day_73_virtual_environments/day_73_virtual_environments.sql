-- ============================================================
-- VIRTUAL ENVIRONMENT MANAGEMENT AND GOVERNANCE
-- PostgreSQL 15+
--
-- Models:
--   Projects
--   Runtime installations
--   Virtual environments
--   Environment lifecycle
--   Dependencies
--   Dependency lockfiles
--   Environment policies
--   Validation results
--   Audit history
--   Deployment eligibility
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS environment_management;

SET search_path TO environment_management, public;

-- ------------------------------------------------------------
-- ENUM TYPES
-- ------------------------------------------------------------

CREATE TYPE runtime_type AS ENUM (
    'PYTHON',
    'NODE',
    'JAVA'
);

CREATE TYPE isolation_level AS ENUM (
    'STRICT',
    'STANDARD',
    'SHARED'
);

CREATE TYPE environment_status AS ENUM (
    'CREATED',
    'CONFIGURING',
    'READY',
    'FAILED',
    'RETIRED'
);

CREATE TYPE dependency_scope AS ENUM (
    'PRODUCTION',
    'DEVELOPMENT',
    'TESTING'
);

CREATE TYPE validation_status AS ENUM (
    'PASSED',
    'FAILED',
    'WARNING'
);

-- ------------------------------------------------------------
-- PROJECTS
-- ------------------------------------------------------------

CREATE TABLE projects (
    project_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    project_name VARCHAR(100) NOT NULL UNIQUE,

    description TEXT,

    owner_name VARCHAR(100) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (LENGTH(TRIM(project_name)) > 0)
);

-- ------------------------------------------------------------
-- RUNTIME INSTALLATIONS
-- ------------------------------------------------------------

CREATE TABLE runtime_installations (
    runtime_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    runtime runtime_type NOT NULL,

    runtime_version VARCHAR(30) NOT NULL,

    executable_path TEXT NOT NULL,

    operating_system VARCHAR(50) NOT NULL,

    architecture VARCHAR(30) NOT NULL,

    is_approved BOOLEAN NOT NULL DEFAULT FALSE,

    installed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (
        runtime,
        runtime_version,
        operating_system,
        architecture
    ),

    CHECK (LENGTH(TRIM(executable_path)) > 0)
);

CREATE INDEX idx_runtime_approved
ON runtime_installations(runtime, is_approved);

-- ------------------------------------------------------------
-- ENVIRONMENT POLICIES
-- ------------------------------------------------------------

CREATE TABLE environment_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    policy_name VARCHAR(100) NOT NULL UNIQUE,

    minimum_disk_mb INTEGER NOT NULL DEFAULT 100,

    maximum_dependencies INTEGER NOT NULL DEFAULT 100,

    require_lockfile BOOLEAN NOT NULL DEFAULT TRUE,

    prohibit_system_packages BOOLEAN NOT NULL DEFAULT TRUE,

    require_strict_isolation BOOLEAN NOT NULL DEFAULT FALSE,

    allow_shared_environment BOOLEAN NOT NULL DEFAULT FALSE,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (minimum_disk_mb >= 0),

    CHECK (maximum_dependencies >= 0)
);

-- ------------------------------------------------------------
-- ALLOWED RUNTIMES PER POLICY
-- ------------------------------------------------------------

CREATE TABLE policy_allowed_runtimes (
    policy_id BIGINT NOT NULL
        REFERENCES environment_policies(policy_id)
        ON DELETE CASCADE,

    runtime runtime_type NOT NULL,

    PRIMARY KEY (policy_id, runtime)
);

-- ------------------------------------------------------------
-- VIRTUAL ENVIRONMENTS
-- ------------------------------------------------------------

CREATE TABLE virtual_environments (
    environment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    project_id BIGINT NOT NULL
        REFERENCES projects(project_id),

    runtime_id BIGINT NOT NULL
        REFERENCES runtime_installations(runtime_id),

    policy_id BIGINT NOT NULL
        REFERENCES environment_policies(policy_id),

    environment_name VARCHAR(100) NOT NULL,

    environment_path TEXT NOT NULL,

    isolation isolation_level NOT NULL DEFAULT 'STRICT',

    status environment_status NOT NULL DEFAULT 'CREATED',

    disk_space_mb INTEGER NOT NULL,

    system_packages_enabled BOOLEAN NOT NULL DEFAULT FALSE,

    lockfile_present BOOLEAN NOT NULL DEFAULT FALSE,

    created_by VARCHAR(100) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (project_id, environment_name),

    UNIQUE (environment_path),

    CHECK (LENGTH(TRIM(environment_name)) > 0),

    CHECK (disk_space_mb >= 0),

    CHECK (LENGTH(TRIM(environment_path)) > 0)
);

CREATE INDEX idx_environment_project
ON virtual_environments(project_id);

CREATE INDEX idx_environment_status
ON virtual_environments(status);

CREATE INDEX idx_environment_runtime
ON virtual_environments(runtime_id);

CREATE INDEX idx_environment_policy
ON virtual_environments(policy_id);

-- ------------------------------------------------------------
-- DEPENDENCY CATALOG
-- ------------------------------------------------------------

CREATE TABLE dependency_catalog (
    dependency_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    package_name VARCHAR(150) NOT NULL,

    package_version VARCHAR(100) NOT NULL,

    runtime runtime_type NOT NULL,

    package_hash VARCHAR(128),

    source_registry TEXT,

    is_approved BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (
        package_name,
        package_version,
        runtime
    ),

    CHECK (LENGTH(TRIM(package_name)) > 0),

    CHECK (LENGTH(TRIM(package_version)) > 0)
);

CREATE INDEX idx_dependency_name
ON dependency_catalog(package_name);

CREATE INDEX idx_dependency_approval
ON dependency_catalog(is_approved);

-- ------------------------------------------------------------
-- ENVIRONMENT DEPENDENCIES
-- ------------------------------------------------------------

CREATE TABLE environment_dependencies (
    environment_id BIGINT NOT NULL
        REFERENCES virtual_environments(environment_id)
        ON DELETE CASCADE,

    dependency_id BIGINT NOT NULL
        REFERENCES dependency_catalog(dependency_id),

    scope dependency_scope NOT NULL DEFAULT 'PRODUCTION',

    is_direct BOOLEAN NOT NULL DEFAULT TRUE,

    installed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (
        environment_id,
        dependency_id
    )
);

CREATE INDEX idx_environment_dependency
ON environment_dependencies(dependency_id);

-- ------------------------------------------------------------
-- DEPENDENCY LOCKFILES
-- ------------------------------------------------------------

CREATE TABLE dependency_lockfiles (
    lockfile_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    environment_id BIGINT NOT NULL
        REFERENCES virtual_environments(environment_id)
        ON DELETE CASCADE,

    lockfile_format VARCHAR(50) NOT NULL,

    content_hash VARCHAR(128) NOT NULL,

    locked_content JSONB NOT NULL,

    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    generated_by VARCHAR(100) NOT NULL,

    UNIQUE(environment_id, content_hash),

    CHECK (jsonb_typeof(locked_content) = 'array')
);

CREATE INDEX idx_lockfile_environment
ON dependency_lockfiles(environment_id, generated_at DESC);

-- ------------------------------------------------------------
-- VALIDATION RESULTS
-- ------------------------------------------------------------

CREATE TABLE environment_validations (
    validation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    environment_id BIGINT NOT NULL
        REFERENCES virtual_environments(environment_id)
        ON DELETE CASCADE,

    validation_name VARCHAR(100) NOT NULL,

    status validation_status NOT NULL,

    details JSONB NOT NULL DEFAULT '{}'::JSONB,

    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    executed_by VARCHAR(100) NOT NULL,

    CHECK (jsonb_typeof(details) = 'object')
);

CREATE INDEX idx_validation_environment
ON environment_validations(environment_id, executed_at DESC);

CREATE INDEX idx_validation_status
ON environment_validations(status);

-- ------------------------------------------------------------
-- ENVIRONMENT AUDIT LOG
-- ------------------------------------------------------------

CREATE TABLE environment_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    environment_id BIGINT
        REFERENCES virtual_environments(environment_id)
        ON DELETE SET NULL,

    action VARCHAR(100) NOT NULL,

    previous_status environment_status,

    new_status environment_status,

    actor VARCHAR(100) NOT NULL,

    details JSONB NOT NULL DEFAULT '{}'::JSONB,

    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_environment_time
ON environment_audit(environment_id, occurred_at DESC);

-- ------------------------------------------------------------
-- STATE TRANSITION VALIDATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_environment_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF TG_OP = 'INSERT' THEN

        IF NEW.status <> 'CREATED' THEN
            RAISE EXCEPTION
                'New environments must start in CREATED state';
        END IF;

        RETURN NEW;
    END IF;

    IF NEW.status = OLD.status THEN
        RETURN NEW;
    END IF;

    IF NOT (
        (OLD.status = 'CREATED'
            AND NEW.status IN ('CONFIGURING', 'RETIRED'))

        OR

        (OLD.status = 'CONFIGURING'
            AND NEW.status IN ('READY', 'FAILED', 'RETIRED'))

        OR

        (OLD.status = 'READY'
            AND NEW.status IN ('CONFIGURING', 'FAILED', 'RETIRED'))

        OR

        (OLD.status = 'FAILED'
            AND NEW.status IN ('CONFIGURING', 'RETIRED'))
    ) THEN

        RAISE EXCEPTION
            'Invalid environment transition: % -> %',
            OLD.status,
            NEW.status;

    END IF;

    NEW.updated_at := NOW();

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_environment_transition
BEFORE INSERT OR UPDATE OF status
ON virtual_environments
FOR EACH ROW
EXECUTE FUNCTION validate_environment_transition();

-- ------------------------------------------------------------
-- AUDIT STATUS CHANGES
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION audit_environment_changes()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF TG_OP = 'INSERT' THEN

        INSERT INTO environment_audit (
            environment_id,
            action,
            previous_status,
            new_status,
            actor,
            details
        )
        VALUES (
            NEW.environment_id,
            'ENVIRONMENT_CREATED',
            NULL,
            NEW.status,
            NEW.created_by,
            jsonb_build_object(
                'environment_name', NEW.environment_name,
                'isolation', NEW.isolation
            )
        );

    ELSIF OLD.status IS DISTINCT FROM NEW.status THEN

        INSERT INTO environment_audit (
            environment_id,
            action,
            previous_status,
            new_status,
            actor,
            details
        )
        VALUES (
            NEW.environment_id,
            'STATUS_CHANGED',
            OLD.status,
            NEW.status,
            NEW.created_by,
            jsonb_build_object(
                'environment_name', NEW.environment_name
            )
        );

    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_environment_audit
AFTER INSERT OR UPDATE OF status
ON virtual_environments
FOR EACH ROW
EXECUTE FUNCTION audit_environment_changes();

-- ------------------------------------------------------------
-- POLICY EVALUATION FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION evaluate_environment(
    p_environment_id BIGINT
)
RETURNS TABLE (
    eligible BOOLEAN,
    violation_count INTEGER,
    violations JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE

    v_environment virtual_environments%ROWTYPE;

    v_runtime runtime_type;

    v_policy environment_policies%ROWTYPE;

    v_dependency_count INTEGER;

    v_violations JSONB := '[]'::JSONB;

BEGIN

    SELECT *
    INTO v_environment
    FROM virtual_environments
    WHERE environment_id = p_environment_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Environment % does not exist',
            p_environment_id;
    END IF;

    SELECT *
    INTO v_policy
    FROM environment_policies
    WHERE policy_id = v_environment.policy_id
      AND is_active = TRUE;

    IF NOT FOUND THEN
        v_violations := v_violations ||
            jsonb_build_array('No active environment policy');
    END IF;

    SELECT runtime
    INTO v_runtime
    FROM runtime_installations
    WHERE runtime_id = v_environment.runtime_id
      AND is_approved = TRUE;

    IF NOT FOUND THEN
        v_violations := v_violations ||
            jsonb_build_array('Runtime is not approved');
    END IF;

    IF FOUND AND v_policy.policy_id IS NOT NULL THEN

        IF NOT EXISTS (
            SELECT 1
            FROM policy_allowed_runtimes
            WHERE policy_id = v_policy.policy_id
              AND runtime = v_runtime
        ) THEN

            v_violations := v_violations ||
                jsonb_build_array('Runtime not allowed by policy');

        END IF;

    END IF;

    IF v_policy.policy_id IS NOT NULL THEN

        IF v_environment.disk_space_mb <
           v_policy.minimum_disk_mb THEN

            v_violations := v_violations ||
                jsonb_build_array('Insufficient disk space');

        END IF;

        IF
            v_policy.require_lockfile
            AND NOT v_environment.lockfile_present
        THEN

            v_violations := v_violations ||
                jsonb_build_array('Lockfile required');

        END IF;

        IF
            v_policy.prohibit_system_packages
            AND v_environment.system_packages_enabled
        THEN

            v_violations := v_violations ||
                jsonb_build_array('System packages prohibited');

        END IF;

        IF
            v_policy.require_strict_isolation
            AND v_environment.isolation <> 'STRICT'
        THEN

            v_violations := v_violations ||
                jsonb_build_array('Strict isolation required');

        END IF;

        IF
            v_environment.isolation = 'SHARED'
            AND NOT v_policy.allow_shared_environment
        THEN

            v_violations := v_violations ||
                jsonb_build_array('Shared environment prohibited');

        END IF;

    END IF;

    SELECT COUNT(*)
    INTO v_dependency_count
    FROM environment_dependencies
    WHERE environment_id = p_environment_id;

    IF
        v_policy.policy_id IS NOT NULL
        AND v_dependency_count > v_policy.maximum_dependencies
    THEN

        v_violations := v_violations ||
            jsonb_build_array('Dependency limit exceeded');

    END IF;

    IF EXISTS (
        SELECT 1
        FROM environment_dependencies ed
        JOIN dependency_catalog dc
          ON dc.dependency_id = ed.dependency_id
        WHERE ed.environment_id = p_environment_id
          AND dc.is_approved = FALSE
    ) THEN

        v_violations := v_violations ||
            jsonb_build_array('Unapproved dependency detected');

    END IF;

    RETURN QUERY
    SELECT
        jsonb_array_length(v_violations) = 0,
        jsonb_array_length(v_violations),
        v_violations;

END;
$$;

-- ------------------------------------------------------------
-- DEPENDENCY INSERTION PROCEDURE
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE add_environment_dependency(
    p_environment_id BIGINT,
    p_dependency_id BIGINT,
    p_scope dependency_scope,
    p_is_direct BOOLEAN
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_status environment_status;
BEGIN

    SELECT status
    INTO v_status
    FROM virtual_environments
    WHERE environment_id = p_environment_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Environment not found';
    END IF;

    IF v_status = 'RETIRED' THEN
        RAISE EXCEPTION
            'Cannot modify retired environment';
    END IF;

    INSERT INTO environment_dependencies (
        environment_id,
        dependency_id,
        scope,
        is_direct
    )
    VALUES (
        p_environment_id,
        p_dependency_id,
        p_scope,
        p_is_direct
    );

    INSERT INTO environment_audit (
        environment_id,
        action,
        actor,
        details
    )
    VALUES (
        p_environment_id,
        'DEPENDENCY_ADDED',
        CURRENT_USER,
        jsonb_build_object(
            'dependency_id', p_dependency_id,
            'scope', p_scope
        )
    );

END;
$$;

-- ------------------------------------------------------------
-- DEPLOYMENT ELIGIBILITY VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW environment_deployment_eligibility AS

SELECT
    ve.environment_id,
    ve.environment_name,
    p.project_name,
    ri.runtime,
    ri.runtime_version,
    ve.isolation,
    ve.status,
    ve.disk_space_mb,
    ve.lockfile_present,
    COUNT(DISTINCT ed.dependency_id) AS dependency_count,

    COALESCE(
        BOOL_AND(dc.is_approved),
        TRUE
    ) AS dependencies_approved,

    (
        ve.status = 'READY'
        AND ve.lockfile_present
        AND ve.isolation = 'STRICT'
        AND ri.is_approved
        AND BOOL_AND(dc.is_approved) IS DISTINCT FROM FALSE
    ) AS preliminary_eligibility

FROM virtual_environments ve

JOIN projects p
    ON p.project_id = ve.project_id

JOIN runtime_installations ri
    ON ri.runtime_id = ve.runtime_id

LEFT JOIN environment_dependencies ed
    ON ed.environment_id = ve.environment_id

LEFT JOIN dependency_catalog dc
    ON dc.dependency_id = ed.dependency_id

GROUP BY
    ve.environment_id,
    ve.environment_name,
    p.project_name,
    ri.runtime,
    ri.runtime_version,
    ve.isolation,
    ve.status,
    ve.disk_space_mb,
    ve.lockfile_present,
    ri.is_approved;

-- ------------------------------------------------------------
-- REPORTING VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW environment_inventory AS

SELECT
    ve.environment_id,
    ve.environment_name,
    p.project_name,
    ri.runtime,
    ri.runtime_version,
    ve.status,
    ve.isolation,
    ve.disk_space_mb,
    COUNT(ed.dependency_id) AS dependency_count,
    ve.created_at,
    ve.updated_at

FROM virtual_environments ve

JOIN projects p
    ON p.project_id = ve.project_id

JOIN runtime_installations ri
    ON ri.runtime_id = ve.runtime_id

LEFT JOIN environment_dependencies ed
    ON ed.environment_id = ve.environment_id

GROUP BY
    ve.environment_id,
    p.project_name,
    ri.runtime,
    ri.runtime_version;

-- ------------------------------------------------------------
-- SAMPLE DATA
-- ------------------------------------------------------------

INSERT INTO projects (
    project_name,
    description,
    owner_name
)
VALUES
(
    'analytics-platform',
    'Data analytics and reporting platform',
    'Engineering Team'
),
(
    'web-platform',
    'Enterprise web application',
    'Application Team'
);

INSERT INTO runtime_installations (
    runtime,
    runtime_version,
    executable_path,
    operating_system,
    architecture,
    is_approved
)
VALUES
(
    'PYTHON',
    '3.13',
    '/usr/bin/python3.13',
    'Linux',
    'x86_64',
    TRUE
),
(
    'NODE',
    '22',
    '/usr/bin/node',
    'Linux',
    'x86_64',
    TRUE
),
(
    'JAVA',
    '17',
    '/usr/bin/java',
    'Linux',
    'x86_64',
    TRUE
),
(
    'PYTHON',
    '3.9',
    '/usr/bin/python3.9',
    'Linux',
    'x86_64',
    FALSE
);

INSERT INTO environment_policies (
    policy_name,
    minimum_disk_mb,
    maximum_dependencies,
    require_lockfile,
    prohibit_system_packages,
    require_strict_isolation,
    allow_shared_environment
)
VALUES
(
    'STRICT_ENTERPRISE',
    100,
    50,
    TRUE,
    TRUE,
    TRUE,
    FALSE
),
(
    'DEVELOPMENT_STANDARD',
    50,
    100,
    TRUE,
    FALSE,
    FALSE,
    FALSE
);

INSERT INTO policy_allowed_runtimes (
    policy_id,
    runtime
)
SELECT policy_id, 'PYTHON'
FROM environment_policies
WHERE policy_name = 'STRICT_ENTERPRISE';

INSERT INTO policy_allowed_runtimes (
    policy_id,
    runtime
)
SELECT policy_id, 'NODE'
FROM environment_policies
WHERE policy_name = 'STRICT_ENTERPRISE';

INSERT INTO policy_allowed_runtimes (
    policy_id,
    runtime
)
SELECT policy_id, 'JAVA'
FROM environment_policies
WHERE policy_name = 'STRICT_ENTERPRISE';

INSERT INTO policy_allowed_runtimes (
    policy_id,
    runtime
)
SELECT policy_id, 'PYTHON'
FROM environment_policies
WHERE policy_name = 'DEVELOPMENT_STANDARD';

INSERT INTO policy_allowed_runtimes (
    policy_id,
    runtime
)
SELECT policy_id, 'NODE'
FROM environment_policies
WHERE policy_name = 'DEVELOPMENT_STANDARD';

INSERT INTO dependency_catalog (
    package_name,
    package_version,
    runtime,
    package_hash,
    source_registry,
    is_approved
)
VALUES
(
    'numpy',
    '2.3.0',
    'PYTHON',
    'sha256:numpy-example-hash',
    'https://pypi.org/simple',
    TRUE
),
(
    'pandas',
    '2.3.0',
    'PYTHON',
    'sha256:pandas-example-hash',
    'https://pypi.org/simple',
    TRUE
),
(
    'pytest',
    '8.4.0',
    'PYTHON',
    'sha256:pytest-example-hash',
    'https://pypi.org/simple',
    TRUE
),
(
    'unverified-package',
    '1.0.0',
    'PYTHON',
    NULL,
    'https://example.invalid/simple',
    FALSE
),
(
    'express',
    '5.1.0',
    'NODE',
    'sha256:express-example-hash',
    'https://registry.npmjs.org',
    TRUE
);

-- ------------------------------------------------------------
-- CREATE ENVIRONMENTS
-- ------------------------------------------------------------

INSERT INTO virtual_environments (
    project_id,
    runtime_id,
    policy_id,
    environment_name,
    environment_path,
    isolation,
    status,
    disk_space_mb,
    system_packages_enabled,
    lockfile_present,
    created_by
)
SELECT
    p.project_id,
    r.runtime_id,
    ep.policy_id,
    'analytics-dev',
    '/srv/environments/analytics-dev',
    'STRICT',
    'CREATED',
    2048,
    FALSE,
    TRUE,
    'engineering-admin'

FROM projects p
CROSS JOIN runtime_installations r
CROSS JOIN environment_policies ep

WHERE p.project_name = 'analytics-platform'
  AND r.runtime = 'PYTHON'
  AND r.runtime_version = '3.13'
  AND r.is_approved = TRUE
  AND ep.policy_name = 'STRICT_ENTERPRISE';

INSERT INTO virtual_environments (
    project_id,
    runtime_id,
    policy_id,
    environment_name,
    environment_path,
    isolation,
    status,
    disk_space_mb,
    system_packages_enabled,
    lockfile_present,
    created_by
)
SELECT
    p.project_id,
    r.runtime_id,
    ep.policy_id,
    'analytics-test',
    '/srv/environments/analytics-test',
    'STRICT',
    'CREATED',
    1024,
    FALSE,
    TRUE,
    'engineering-admin'

FROM projects p
CROSS JOIN runtime_installations r
CROSS JOIN environment_policies ep

WHERE p.project_name = 'analytics-platform'
  AND r.runtime = 'PYTHON'
  AND r.runtime_version = '3.13'
  AND r.is_approved = TRUE
  AND ep.policy_name = 'STRICT_ENTERPRISE';

-- ------------------------------------------------------------
-- ATTACH APPROVED DEPENDENCIES
-- ------------------------------------------------------------

INSERT INTO environment_dependencies (
    environment_id,
    dependency_id,
    scope,
    is_direct
)
SELECT
    ve.environment_id,
    dc.dependency_id,
    CASE
        WHEN dc.package_name = 'pytest'
            THEN 'TESTING'::dependency_scope
        ELSE 'PRODUCTION'::dependency_scope
    END,
    TRUE

FROM virtual_environments ve

JOIN dependency_catalog dc
    ON dc.package_name IN ('numpy', 'pandas', 'pytest')

WHERE ve.environment_name = 'analytics-dev';

-- ------------------------------------------------------------
-- ADD LOCKFILE
-- ------------------------------------------------------------

INSERT INTO dependency_lockfiles (
    environment_id,
    lockfile_format,
    content_hash,
    locked_content,
    generated_by
)
SELECT
    environment_id,
    'JSON',
    'sha256:analytics-lockfile-001',
    '[
        {"name":"numpy","version":"2.3.0"},
        {"name":"pandas","version":"2.3.0"},
        {"name":"pytest","version":"8.4.0"}
    ]'::JSONB,
    'engineering-admin'

FROM virtual_environments

WHERE environment_name = 'analytics-dev';

-- ------------------------------------------------------------
-- UPDATE LIFECYCLE STATES
-- ------------------------------------------------------------

UPDATE virtual_environments
SET status = 'CONFIGURING'
WHERE environment_name = 'analytics-dev';

UPDATE virtual_environments
SET status = 'READY'
WHERE environment_name = 'analytics-dev';

UPDATE virtual_environments
SET status = 'CONFIGURING'
WHERE environment_name = 'analytics-test';

UPDATE virtual_environments
SET status = 'FAILED'
WHERE environment_name = 'analytics-test';

-- ------------------------------------------------------------
-- RECORD VALIDATION RESULTS
-- ------------------------------------------------------------

INSERT INTO environment_validations (
    environment_id,
    validation_name,
    status,
    details,
    executed_by
)
SELECT
    environment_id,
    'DEPENDENCY_ISOLATION_CHECK',
    'PASSED',
    jsonb_build_object(
        'isolation', isolation,
        'lockfile_present', lockfile_present
    ),
    'validation-service'

FROM virtual_environments

WHERE environment_name = 'analytics-dev';

INSERT INTO environment_validations (
    environment_id,
    validation_name,
    status,
    details,
    executed_by
)
SELECT
    environment_id,
    'DEPLOYMENT_READINESS_CHECK',
    'FAILED',
    jsonb_build_object(
        'reason', 'Environment configuration failed'
    ),
    'validation-service'

FROM virtual_environments

WHERE environment_name = 'analytics-test';

COMMIT;

-- ============================================================
-- RETRIEVAL QUERIES
-- ============================================================

-- 1. List all environments.

SELECT *
FROM environment_inventory
ORDER BY project_name, environment_name;

-- 2. Retrieve an environment and its runtime.

SELECT
    ve.environment_name,
    p.project_name,
    ri.runtime,
    ri.runtime_version,
    ve.status,
    ve.isolation
FROM virtual_environments ve
JOIN projects p
    ON p.project_id = ve.project_id
JOIN runtime_installations ri
    ON ri.runtime_id = ve.runtime_id
ORDER BY ve.environment_name;

-- 3. Retrieve installed dependencies.

SELECT
    ve.environment_name,
    dc.package_name,
    dc.package_version,
    ed.scope,
    dc.is_approved
FROM environment_dependencies ed
JOIN virtual_environments ve
    ON ve.environment_id = ed.environment_id
JOIN dependency_catalog dc
    ON dc.dependency_id = ed.dependency_id
ORDER BY ve.environment_name, dc.package_name;

-- ============================================================
-- POLICY VALIDATION
-- ============================================================

-- 4. Evaluate every environment.

SELECT
    ve.environment_name,
    result.eligible,
    result.violation_count,
    result.violations
FROM virtual_environments ve
CROSS JOIN LATERAL evaluate_environment(
    ve.environment_id
) AS result
ORDER BY ve.environment_name;

-- 5. Identify unapproved dependencies.

SELECT
    ve.environment_name,
    dc.package_name,
    dc.package_version
FROM environment_dependencies ed
JOIN virtual_environments ve
    ON ve.environment_id = ed.environment_id
JOIN dependency_catalog dc
    ON dc.dependency_id = ed.dependency_id
WHERE dc.is_approved = FALSE;

-- 6. Find environments without lockfiles.

SELECT
    environment_name,
    status
FROM virtual_environments
WHERE lockfile_present = FALSE;

-- ============================================================
-- AGGREGATION AND REPORTING
-- ============================================================

-- 7. Count environments by lifecycle state.

SELECT
    status,
    COUNT(*) AS environment_count
FROM virtual_environments
GROUP BY status
ORDER BY status;

-- 8. Count environments by runtime.

SELECT
    ri.runtime,
    COUNT(*) AS environment_count
FROM virtual_environments ve
JOIN runtime_installations ri
    ON ri.runtime_id = ve.runtime_id
GROUP BY ri.runtime
ORDER BY ri.runtime;

-- 9. Dependency count by project.

SELECT
    p.project_name,
    COUNT(ed.dependency_id) AS total_dependencies,
    COUNT(DISTINCT ve.environment_id) AS environments
FROM projects p
LEFT JOIN virtual_environments ve
    ON ve.project_id = p.project_id
LEFT JOIN environment_dependencies ed
    ON ed.environment_id = ve.environment_id
GROUP BY p.project_id, p.project_name
ORDER BY p.project_name;

-- ============================================================
-- CTE-BASED EVALUATION
-- ============================================================

-- 10. Deployment eligibility report.

WITH evaluation AS (

    SELECT
        ve.environment_id,
        ve.environment_name,
        ve.status,
        ve.isolation,
        result.eligible,
        result.violations

    FROM virtual_environments ve

    CROSS JOIN LATERAL evaluate_environment(
        ve.environment_id
    ) AS result

)

SELECT
    environment_id,
    environment_name,
    status,
    isolation,
    eligible,
    violations
FROM evaluation
ORDER BY eligible DESC, environment_name;

-- ============================================================
-- WORKFLOW PROCESSING
-- ============================================================

-- 11. Record a new validation.

INSERT INTO environment_validations (
    environment_id,
    validation_name,
    status,
    details,
    executed_by
)
SELECT
    environment_id,
    'POST_INSTALL_IMPORT_TEST',
    'PASSED',
    '{"test":"package import validation"}'::JSONB,
    'ci-service'
FROM virtual_environments
WHERE environment_name = 'analytics-dev';

-- 12. Add a dependency using the stored procedure.

-- This transaction is rolled back to keep sample data unchanged.

BEGIN;

CALL add_environment_dependency(
    (
        SELECT environment_id
        FROM virtual_environments
        WHERE environment_name = 'analytics-dev'
    ),
    (
        SELECT dependency_id
        FROM dependency_catalog
        WHERE package_name = 'unverified-package'
    ),
    'DEVELOPMENT',
    TRUE
);

ROLLBACK;

-- 13. Read environment audit history.

SELECT
    audit_id,
    action,
    previous_status,
    new_status,
    actor,
    details,
    occurred_at
FROM environment_audit
ORDER BY occurred_at DESC;

-- ============================================================
-- ELIGIBILITY DETERMINATION
-- ============================================================

-- 14. Identify environments that are eligible for deployment.

SELECT
    ve.environment_id,
    ve.environment_name,
    ve.status,
    evaluation.eligible,
    evaluation.violations
FROM virtual_environments ve
CROSS JOIN LATERAL evaluate_environment(
    ve.environment_id
) AS evaluation
WHERE ve.status = 'READY'
  AND evaluation.eligible = TRUE;

-- 15. Identify failed environments.

SELECT
    ve.environment_name,
    p.project_name,
    ev.validation_name,
    ev.status,
    ev.details
FROM virtual_environments ve
JOIN projects p
    ON p.project_id = ve.project_id
LEFT JOIN environment_validations ev
    ON ev.environment_id = ve.environment_id
WHERE ve.status = 'FAILED'
ORDER BY ev.executed_at DESC;

-- ============================================================
-- ADDITIONAL PERFORMANCE ANALYSIS
-- ============================================================

EXPLAIN
SELECT *
FROM virtual_environments
WHERE status = 'READY';

EXPLAIN
SELECT *
FROM environment_dependencies
WHERE dependency_id = 1;

-- The database stores environment metadata and governance.
-- Actual filesystem isolation and package installation must
-- be enforced by the environment-management application.
