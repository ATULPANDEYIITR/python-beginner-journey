-- ============================================================
-- PYTHON STANDARD LIBRARY: RELATIONAL OPERATIONS MODEL
-- PostgreSQL 14+
--
-- This database stores standard-library learning modules,
-- execution exercises, test results, and runtime telemetry.
--
-- Python standard-library modules are classified by purpose.
-- Database constraints protect the integrity of the catalog.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS stdlib_lab;

SET search_path TO stdlib_lab, public;

-- ------------------------------------------------------------
-- Enumerated domain types
-- ------------------------------------------------------------

CREATE TYPE module_category AS ENUM (
    'data_structures',
    'algorithms',
    'files',
    'serialization',
    'database',
    'networking',
    'concurrency',
    'security',
    'testing',
    'runtime'
);

CREATE TYPE exercise_status AS ENUM (
    'available',
    'running',
    'passed',
    'failed',
    'disabled'
);

CREATE TYPE execution_environment AS ENUM (
    'development',
    'testing',
    'production'
);

CREATE TYPE test_outcome AS ENUM (
    'passed',
    'failed',
    'skipped',
    'error'
);

-- ------------------------------------------------------------
-- Standard-library modules
-- ------------------------------------------------------------

CREATE TABLE modules (
    module_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    module_name VARCHAR(100) NOT NULL UNIQUE,
    category module_category NOT NULL,
    minimum_python_version VARCHAR(20) NOT NULL,
    is_external BOOLEAN NOT NULL DEFAULT FALSE,
    security_sensitive BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT module_name_nonempty
        CHECK (length(trim(module_name)) > 0),

    CONSTRAINT module_version_nonempty
        CHECK (length(trim(minimum_python_version)) > 0),

    CONSTRAINT stdlib_only
        CHECK (is_external = FALSE)
);

CREATE INDEX idx_modules_category
    ON modules(category);

CREATE INDEX idx_modules_security
    ON modules(security_sensitive)
    WHERE security_sensitive = TRUE;

-- ------------------------------------------------------------
-- Learning exercises
-- ------------------------------------------------------------

CREATE TABLE exercises (
    exercise_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    module_id BIGINT NOT NULL REFERENCES modules(module_id),
    exercise_name VARCHAR(150) NOT NULL,
    difficulty SMALLINT NOT NULL,
    status exercise_status NOT NULL DEFAULT 'available',
    timeout_seconds INTEGER NOT NULL DEFAULT 30,
    memory_limit_mb INTEGER NOT NULL DEFAULT 256,
    expected_behavior JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT exercise_name_nonempty
        CHECK (length(trim(exercise_name)) > 0),

    CONSTRAINT exercise_difficulty
        CHECK (difficulty BETWEEN 1 AND 5),

    CONSTRAINT exercise_timeout
        CHECK (timeout_seconds BETWEEN 1 AND 3600),

    CONSTRAINT exercise_memory
        CHECK (memory_limit_mb BETWEEN 16 AND 65536),

    CONSTRAINT expected_behavior_object
        CHECK (jsonb_typeof(expected_behavior) = 'object'),

    UNIQUE(module_id, exercise_name)
);

CREATE INDEX idx_exercises_module_status
    ON exercises(module_id, status);

CREATE INDEX idx_exercises_difficulty
    ON exercises(difficulty);

CREATE INDEX idx_exercises_expected_behavior
    ON exercises USING GIN(expected_behavior);

-- ------------------------------------------------------------
-- Execution environments
-- ------------------------------------------------------------

CREATE TABLE environments (
    environment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    environment_name VARCHAR(100) NOT NULL UNIQUE,
    environment_type execution_environment NOT NULL,
    python_version VARCHAR(20) NOT NULL,
    operating_system VARCHAR(100) NOT NULL,
    allowed_network_access BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (length(trim(python_version)) > 0),
    CHECK (length(trim(operating_system)) > 0)
);

-- ------------------------------------------------------------
-- Execution runs
-- ------------------------------------------------------------

CREATE TABLE execution_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    exercise_id BIGINT NOT NULL REFERENCES exercises(exercise_id),
    environment_id BIGINT NOT NULL REFERENCES environments(environment_id),
    status exercise_status NOT NULL DEFAULT 'running',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_ms BIGINT,
    memory_used_mb INTEGER,
    error_message TEXT,
    output_digest CHAR(64),

    CONSTRAINT run_duration_nonnegative
        CHECK (duration_ms IS NULL OR duration_ms >= 0),

    CONSTRAINT run_memory_nonnegative
        CHECK (memory_used_mb IS NULL OR memory_used_mb >= 0),

    CONSTRAINT run_completion_order
        CHECK (
            completed_at IS NULL OR completed_at >= started_at
        ),

    CONSTRAINT run_status_completion
        CHECK (
            status IN ('running', 'passed', 'failed', 'disabled')
        ),

    CONSTRAINT run_digest_format
        CHECK (
            output_digest IS NULL OR
            output_digest ~ '^[0-9a-f]{64}$'
        )
);

CREATE INDEX idx_runs_exercise_started
    ON execution_runs(exercise_id, started_at DESC);

CREATE INDEX idx_runs_status
    ON execution_runs(status);

CREATE INDEX idx_runs_environment
    ON execution_runs(environment_id, started_at DESC);

-- ------------------------------------------------------------
-- Individual test results
-- ------------------------------------------------------------

CREATE TABLE test_results (
    test_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES execution_runs(run_id)
        ON DELETE CASCADE,
    test_name VARCHAR(150) NOT NULL,
    outcome test_outcome NOT NULL,
    execution_time_ms BIGINT NOT NULL DEFAULT 0,
    diagnostic JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (length(trim(test_name)) > 0),
    CHECK (execution_time_ms >= 0),
    CHECK (jsonb_typeof(diagnostic) = 'object'),

    UNIQUE(run_id, test_name)
);

CREATE INDEX idx_test_results_run_outcome
    ON test_results(run_id, outcome);

-- ------------------------------------------------------------
-- Execution audit trail
-- ------------------------------------------------------------

CREATE TABLE execution_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES execution_runs(run_id),
    event_type VARCHAR(80) NOT NULL,
    event_details JSONB NOT NULL DEFAULT '{}',
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (length(trim(event_type)) > 0),
    CHECK (jsonb_typeof(event_details) = 'object')
);

CREATE INDEX idx_audit_run_time
    ON execution_audit(run_id, recorded_at DESC);

-- ------------------------------------------------------------
-- Validate run state transitions
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_run_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        IF OLD.status IN ('passed', 'failed', 'disabled')
           AND NEW.status <> OLD.status THEN
            RAISE EXCEPTION
                'Terminal execution state cannot be changed';
        END IF;

        IF OLD.status = 'running'
           AND NEW.status = 'available' THEN
            RAISE EXCEPTION
                'Running execution cannot become available';
        END IF;

        IF NEW.completed_at IS NOT NULL
           AND NEW.status = 'running' THEN
            RAISE EXCEPTION
                'Running execution cannot have completion time';
        END IF;

        IF NEW.status IN ('passed', 'failed', 'disabled')
           AND NEW.completed_at IS NULL THEN
            RAISE EXCEPTION
                'Terminal execution requires completion time';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_run_transition
BEFORE UPDATE ON execution_runs
FOR EACH ROW
EXECUTE FUNCTION validate_run_transition();

-- ------------------------------------------------------------
-- Audit test-result insertion
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION audit_test_result()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO execution_audit (
        run_id,
        event_type,
        event_details
    )
    VALUES (
        NEW.run_id,
        'TEST_RESULT_RECORDED',
        jsonb_build_object(
            'test_name', NEW.test_name,
            'outcome', NEW.outcome,
            'execution_time_ms', NEW.execution_time_ms
        )
    );

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_audit_test_result
AFTER INSERT ON test_results
FOR EACH ROW
EXECUTE FUNCTION audit_test_result();

-- ------------------------------------------------------------
-- Catalog registration
-- ------------------------------------------------------------

INSERT INTO modules (
    module_name,
    category,
    minimum_python_version,
    security_sensitive,
    description
)
VALUES
(
    'collections',
    'data_structures',
    '3.10',
    FALSE,
    'Specialized containers including Counter, deque and defaultdict.'
),
(
    'itertools',
    'algorithms',
    '3.10',
    FALSE,
    'Memory-efficient iterator building blocks.'
),
(
    'functools',
    'algorithms',
    '3.10',
    FALSE,
    'Higher-order functions, decorators and memoization.'
),
(
    'pathlib',
    'files',
    '3.10',
    FALSE,
    'Object-oriented filesystem paths.'
),
(
    'csv',
    'serialization',
    '3.10',
    FALSE,
    'Delimited tabular data processing.'
),
(
    'json',
    'serialization',
    '3.10',
    FALSE,
    'JSON serialization and deserialization.'
),
(
    'sqlite3',
    'database',
    '3.10',
    TRUE,
    'Embedded relational database access and parameterized SQL.'
),
(
    'urllib',
    'networking',
    '3.10',
    TRUE,
    'URL parsing and HTTP communication.'
),
(
    'asyncio',
    'concurrency',
    '3.10',
    FALSE,
    'Asynchronous I/O and cooperative task scheduling.'
),
(
    'concurrent.futures',
    'concurrency',
    '3.10',
    FALSE,
    'Thread and process executor abstractions.'
),
(
    'hashlib',
    'security',
    '3.10',
    TRUE,
    'Cryptographic hash and message digest functions.'
),
(
    'secrets',
    'security',
    '3.10',
    TRUE,
    'Cryptographically secure random values.'
),
(
    'unittest',
    'testing',
    '3.10',
    FALSE,
    'Built-in unit testing framework.'
),
(
    'logging',
    'runtime',
    '3.10',
    TRUE,
    'Configurable application logging.'
)
ON CONFLICT(module_name) DO NOTHING;

-- ------------------------------------------------------------
-- Exercise registration
-- ------------------------------------------------------------

INSERT INTO exercises (
    module_id,
    exercise_name,
    difficulty,
    timeout_seconds,
    memory_limit_mb,
    expected_behavior
)
SELECT
    module_id,
    exercise_name,
    difficulty,
    30,
    256,
    expected_behavior::jsonb
FROM (
    VALUES
    (
        'collections',
        'Frequency analysis',
        1,
        '{"expected":"Counter output"}'
    ),
    (
        'itertools',
        'Combinatorial generation',
        3,
        '{"expected":"Lazy iterator"}'
    ),
    (
        'functools',
        'Memoized computation',
        3,
        '{"expected":"Cached result"}'
    ),
    (
        'pathlib',
        'Directory traversal',
        2,
        '{"expected":"Path objects"}'
    ),
    (
        'csv',
        'Structured CSV export',
        2,
        '{"expected":"Valid CSV records"}'
    ),
    (
        'json',
        'JSON serialization',
        2,
        '{"expected":"Valid JSON"}'
    ),
    (
        'sqlite3',
        'Transactional persistence',
        4,
        '{"expected":"Committed transaction"}'
    ),
    (
        'urllib',
        'Bounded HTTPS request',
        4,
        '{"expected":"Validated response"}'
    ),
    (
        'asyncio',
        'Concurrent asynchronous tasks',
        4,
        '{"expected":"Completed coroutines"}'
    ),
    (
        'concurrent.futures',
        'Parallel computation',
        5,
        '{"expected":"Ordered results"}'
    ),
    (
        'hashlib',
        'SHA-256 digest',
        2,
        '{"expected":"64-character digest"}'
    ),
    (
        'unittest',
        'Automated assertions',
        2,
        '{"expected":"All tests pass"}'
    )
) AS source(
    module_name,
    exercise_name,
    difficulty,
    expected_behavior
)
JOIN modules USING(module_name)
ON CONFLICT(module_id, exercise_name) DO NOTHING;

-- ------------------------------------------------------------
-- Execution environment registration
-- ------------------------------------------------------------

INSERT INTO environments (
    environment_name,
    environment_type,
    python_version,
    operating_system,
    allowed_network_access
)
VALUES
(
    'Developer workstation',
    'development',
    '3.13',
    'Windows 11',
    FALSE
),
(
    'Automated test runner',
    'testing',
    '3.13',
    'Linux',
    FALSE
),
(
    'Controlled production worker',
    'production',
    '3.13',
    'Linux',
    FALSE
)
ON CONFLICT(environment_name) DO NOTHING;

-- ------------------------------------------------------------
-- Reporting views
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW module_catalog AS
SELECT
    m.module_id,
    m.module_name,
    m.category,
    m.minimum_python_version,
    m.security_sensitive,
    COUNT(e.exercise_id) AS exercise_count,
    COUNT(e.exercise_id) FILTER (
        WHERE e.status = 'available'
    ) AS available_exercises
FROM modules m
LEFT JOIN exercises e
    ON e.module_id = m.module_id
GROUP BY
    m.module_id,
    m.module_name,
    m.category,
    m.minimum_python_version,
    m.security_sensitive;

CREATE OR REPLACE VIEW exercise_performance AS
SELECT
    e.exercise_id,
    e.exercise_name,
    m.module_name,
    COUNT(DISTINCT r.run_id) AS total_runs,
    COUNT(DISTINCT r.run_id) FILTER (
        WHERE r.status = 'passed'
    ) AS successful_runs,
    COUNT(DISTINCT r.run_id) FILTER (
        WHERE r.status = 'failed'
    ) AS failed_runs,
    ROUND(
        AVG(r.duration_ms)::numeric,
        2
    ) AS average_duration_ms,
    MAX(r.started_at) AS last_execution
FROM exercises e
JOIN modules m
    ON m.module_id = e.module_id
LEFT JOIN execution_runs r
    ON r.exercise_id = e.exercise_id
GROUP BY
    e.exercise_id,
    e.exercise_name,
    m.module_name;

-- ------------------------------------------------------------
-- Execution eligibility function
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION is_execution_eligible(
    p_exercise_id BIGINT,
    p_environment_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    exercise_record RECORD;
    environment_record RECORD;
BEGIN
    SELECT
        e.status,
        e.timeout_seconds,
        e.memory_limit_mb,
        m.security_sensitive
    INTO exercise_record
    FROM exercises e
    JOIN modules m USING(module_id)
    WHERE e.exercise_id = p_exercise_id;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    SELECT
        environment_type,
        allowed_network_access
    INTO environment_record
    FROM environments
    WHERE environment_id = p_environment_id;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    IF exercise_record.status <> 'available' THEN
        RETURN FALSE;
    END IF;

    IF environment_record.environment_type = 'production'
       AND exercise_record.security_sensitive
       AND environment_record.allowed_network_access THEN
        RETURN FALSE;
    END IF;

    RETURN TRUE;
END;
$$;

-- ------------------------------------------------------------
-- Execution procedure
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE start_exercise(
    p_exercise_id BIGINT,
    p_environment_id BIGINT,
    INOUT p_run_id BIGINT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT is_execution_eligible(
        p_exercise_id,
        p_environment_id
    ) THEN
        RAISE EXCEPTION
            'Exercise is not eligible for execution';
    END IF;

    INSERT INTO execution_runs (
        exercise_id,
        environment_id,
        status
    )
    VALUES (
        p_exercise_id,
        p_environment_id,
        'running'
    )
    RETURNING run_id INTO p_run_id;

    INSERT INTO execution_audit (
        run_id,
        event_type,
        event_details
    )
    VALUES (
        p_run_id,
        'EXECUTION_STARTED',
        jsonb_build_object(
            'exercise_id', p_exercise_id,
            'environment_id', p_environment_id
        )
    );
END;
$$;

-- ------------------------------------------------------------
-- Record execution completion
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE complete_exercise(
    p_run_id BIGINT,
    p_status exercise_status,
    p_duration_ms BIGINT,
    p_memory_used_mb INTEGER,
    p_error_message TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_status NOT IN ('passed', 'failed', 'disabled') THEN
        RAISE EXCEPTION 'Invalid terminal status';
    END IF;

    IF p_duration_ms < 0 OR p_memory_used_mb < 0 THEN
        RAISE EXCEPTION 'Invalid execution measurements';
    END IF;

    UPDATE execution_runs
    SET
        status = p_status,
        completed_at = NOW(),
        duration_ms = p_duration_ms,
        memory_used_mb = p_memory_used_mb,
        error_message = p_error_message
    WHERE run_id = p_run_id
      AND status = 'running';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Run does not exist or is not running';
    END IF;

    INSERT INTO execution_audit (
        run_id,
        event_type,
        event_details
    )
    VALUES (
        p_run_id,
        'EXECUTION_COMPLETED',
        jsonb_build_object(
            'status', p_status,
            'duration_ms', p_duration_ms,
            'memory_used_mb', p_memory_used_mb
        )
    );
END;
$$;

COMMIT;

-- ============================================================
-- OPERATIONAL EXAMPLES
-- ============================================================

-- 1. Retrieve the standard-library catalog.

SELECT *
FROM stdlib_lab.module_catalog
ORDER BY category, module_name;

-- 2. Retrieve exercises by category and difficulty.

SELECT
    m.module_name,
    e.exercise_name,
    e.difficulty,
    e.timeout_seconds
FROM stdlib_lab.exercises e
JOIN stdlib_lab.modules m USING(module_id)
WHERE m.category = 'concurrency'
  AND e.difficulty >= 3
ORDER BY e.difficulty DESC;

-- 3. Identify security-sensitive modules.

SELECT module_name, category, description
FROM stdlib_lab.modules
WHERE security_sensitive = TRUE;

-- 4. Determine execution eligibility.

SELECT
    e.exercise_name,
    env.environment_name,
    stdlib_lab.is_execution_eligible(
        e.exercise_id,
        env.environment_id
    ) AS eligible
FROM stdlib_lab.exercises e
CROSS JOIN stdlib_lab.environments env
ORDER BY e.exercise_id, env.environment_id;

-- 5. Start a transactionally recorded execution.

DO $$
DECLARE
    selected_exercise BIGINT;
    selected_environment BIGINT;
    generated_run BIGINT;
BEGIN
    SELECT exercise_id
    INTO selected_exercise
    FROM stdlib_lab.exercises
    WHERE exercise_name = 'Memoized computation';

    SELECT environment_id
    INTO selected_environment
    FROM stdlib_lab.environments
    WHERE environment_name = 'Automated test runner';

    CALL stdlib_lab.start_exercise(
        selected_exercise,
        selected_environment,
        generated_run
    );

    RAISE NOTICE 'Created execution run: %', generated_run;

    CALL stdlib_lab.complete_exercise(
        generated_run,
        'passed',
        125,
        32,
        NULL
    );
END;
$$;

-- 6. Record test results for the most recent execution.

INSERT INTO stdlib_lab.test_results (
    run_id,
    test_name,
    outcome,
    execution_time_ms,
    diagnostic
)
SELECT
    run_id,
    'memoization_result',
    'passed',
    15,
    '{"expected":55,"actual":55}'::jsonb
FROM stdlib_lab.execution_runs
ORDER BY run_id DESC
LIMIT 1
ON CONFLICT(run_id, test_name) DO NOTHING;

-- 7. Execution aggregation.

SELECT
    status,
    COUNT(*) AS total_runs,
    ROUND(AVG(duration_ms)::numeric, 2) AS mean_duration_ms,
    MAX(memory_used_mb) AS maximum_memory_mb
FROM stdlib_lab.execution_runs
GROUP BY status
ORDER BY status;

-- 8. Exercise performance reporting.

SELECT *
FROM stdlib_lab.exercise_performance
ORDER BY total_runs DESC, exercise_name;

-- 9. Test outcome reporting.

SELECT
    tr.outcome,
    COUNT(*) AS test_count,
    ROUND(AVG(tr.execution_time_ms)::numeric, 2)
        AS average_test_duration_ms
FROM stdlib_lab.test_results tr
GROUP BY tr.outcome
ORDER BY tr.outcome;

-- 10. Audit history.

SELECT
    run_id,
    event_type,
    event_details,
    recorded_at
FROM stdlib_lab.execution_audit
ORDER BY recorded_at DESC;

-- 11. Find failed executions.

SELECT
    r.run_id,
    m.module_name,
    e.exercise_name,
    r.error_message,
    r.started_at
FROM stdlib_lab.execution_runs r
JOIN stdlib_lab.exercises e USING(exercise_id)
JOIN stdlib_lab.modules m USING(module_id)
WHERE r.status = 'failed'
ORDER BY r.started_at DESC;

-- 12. JSONB diagnostic query.

SELECT
    test_name,
    diagnostic
FROM stdlib_lab.test_results
WHERE diagnostic @> '{"expected":55}'::jsonb;

-- 13. Constraint validation example.
-- The nested exception block rolls back this invalid statement
-- without interrupting the remainder of the script.

DO $$
BEGIN
    BEGIN
        INSERT INTO stdlib_lab.modules (
            module_name,
            category,
            minimum_python_version,
            is_external,
            security_sensitive,
            description
        )
        VALUES (
            'third_party_example',
            'runtime',
            '3.10',
            TRUE,
            FALSE,
            'Intentionally invalid external module'
        );

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'Expected validation failure: external module rejected';
    END;
END;
$$;

-- 14. Final catalog health report.

SELECT
    (SELECT COUNT(*) FROM stdlib_lab.modules)
        AS registered_modules,
    (SELECT COUNT(*) FROM stdlib_lab.exercises)
        AS registered_exercises,
    (SELECT COUNT(*) FROM stdlib_lab.execution_runs)
        AS execution_runs,
    (SELECT COUNT(*) FROM stdlib_lab.test_results)
        AS recorded_tests,
    (SELECT COUNT(*) FROM stdlib_lab.execution_audit)
        AS audit_events;
