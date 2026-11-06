-- ============================================================
-- PRACTICE: FILES AND EXCEPTIONS
-- PostgreSQL file-import, validation, exception handling,
-- processing workflow, audit logging, and reporting.
--
-- PostgreSQL does not directly replace operating-system file
-- handling. This schema models the database side of a reliable
-- file ingestion workflow.
-- ============================================================

DROP SCHEMA IF EXISTS file_practice CASCADE;
CREATE SCHEMA file_practice;

SET search_path TO file_practice, public;

-- ------------------------------------------------------------
-- 1. Domain types
-- ------------------------------------------------------------

CREATE TYPE file_state AS ENUM (
    'RECEIVED',
    'VALIDATING',
    'VALIDATED',
    'PROCESSING',
    'COMPLETED',
    'PARTIALLY_FAILED',
    'FAILED'
);

CREATE TYPE record_state AS ENUM (
    'PENDING',
    'VALID',
    'PROCESSING',
    'COMPLETED',
    'REJECTED',
    'FAILED'
);

CREATE TYPE error_severity AS ENUM (
    'WARNING',
    'ERROR',
    'CRITICAL'
);

CREATE TYPE access_role AS ENUM (
    'ADMIN',
    'OPERATOR',
    'AUDITOR'
);

-- ------------------------------------------------------------
-- 2. Users and access control
-- ------------------------------------------------------------

CREATE TABLE app_users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    role access_role NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE departments (
    department_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    department_code VARCHAR(20) NOT NULL UNIQUE,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE import_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    policy_name VARCHAR(100) NOT NULL UNIQUE,
    maximum_amount NUMERIC(14, 2) NOT NULL
        CHECK (maximum_amount > 0),
    allowed_departments TEXT[] NOT NULL,
    maximum_records INTEGER NOT NULL DEFAULT 10000
        CHECK (maximum_records > 0),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 3. File registry
-- ------------------------------------------------------------

CREATE TABLE imported_files (
    file_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    original_filename VARCHAR(255) NOT NULL,
    storage_key VARCHAR(500) NOT NULL UNIQUE,
    sha256_hash VARCHAR(64) NOT NULL,
    file_size_bytes BIGINT NOT NULL
        CHECK (file_size_bytes >= 0),
    content_type VARCHAR(100) NOT NULL,
    uploaded_by BIGINT NOT NULL
        REFERENCES app_users(user_id),
    policy_id BIGINT NOT NULL
        REFERENCES import_policies(policy_id),
    state file_state NOT NULL DEFAULT 'RECEIVED',
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    CHECK (sha256_hash ~ '^[a-f0-9]{64}$'),
    CHECK (
        completed_at IS NULL
        OR completed_at >= uploaded_at
    )
);

CREATE INDEX idx_imported_files_state_time
    ON imported_files(state, uploaded_at DESC);

CREATE INDEX idx_imported_files_hash
    ON imported_files(sha256_hash);

-- ------------------------------------------------------------
-- 4. File records and record-level validation
-- ------------------------------------------------------------

CREATE TABLE imported_records (
    record_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    file_id BIGINT NOT NULL
        REFERENCES imported_files(file_id)
        ON DELETE CASCADE,
    source_row_number INTEGER NOT NULL
        CHECK (source_row_number > 0),
    employee_name VARCHAR(150),
    department_code VARCHAR(20),
    amount NUMERIC(14, 2),
    state record_state NOT NULL DEFAULT 'PENDING',
    processed_at TIMESTAMPTZ,
    UNIQUE(file_id, source_row_number),
    CHECK (amount IS NULL OR amount >= 0)
);

CREATE INDEX idx_records_file_state
    ON imported_records(file_id, state);

CREATE INDEX idx_records_department
    ON imported_records(department_code);

-- ------------------------------------------------------------
-- 5. Exception and audit records
-- ------------------------------------------------------------

CREATE TABLE processing_errors (
    error_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    file_id BIGINT NOT NULL
        REFERENCES imported_files(file_id)
        ON DELETE CASCADE,
    record_id BIGINT
        REFERENCES imported_records(record_id)
        ON DELETE CASCADE,
    error_code VARCHAR(60) NOT NULL,
    error_message TEXT NOT NULL,
    severity error_severity NOT NULL DEFAULT 'ERROR',
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_processing_errors_file_time
    ON processing_errors(file_id, occurred_at DESC);

CREATE TABLE audit_events (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    file_id BIGINT
        REFERENCES imported_files(file_id),
    actor_id BIGINT
        REFERENCES app_users(user_id),
    event_type VARCHAR(80) NOT NULL,
    event_details JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_events_file_time
    ON audit_events(file_id, occurred_at DESC);

-- ------------------------------------------------------------
-- 6. File state transition validation
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_file_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.state = NEW.state THEN
        RETURN NEW;
    END IF;

    IF OLD.state IN ('COMPLETED', 'PARTIALLY_FAILED', 'FAILED') THEN
        RAISE EXCEPTION
            'Terminal file state % cannot transition to %',
            OLD.state, NEW.state
            USING ERRCODE = '23514';
    END IF;

    IF NOT (
        (OLD.state = 'RECEIVED'
            AND NEW.state IN ('VALIDATING', 'FAILED'))
        OR
        (OLD.state = 'VALIDATING'
            AND NEW.state IN ('VALIDATED', 'FAILED'))
        OR
        (OLD.state = 'VALIDATED'
            AND NEW.state IN ('PROCESSING', 'FAILED'))
        OR
        (OLD.state = 'PROCESSING'
            AND NEW.state IN (
                'COMPLETED',
                'PARTIALLY_FAILED',
                'FAILED'
            ))
    ) THEN
        RAISE EXCEPTION
            'Invalid file transition: % -> %',
            OLD.state, NEW.state
            USING ERRCODE = '23514';
    END IF;

    IF NEW.state IN ('COMPLETED', 'PARTIALLY_FAILED', 'FAILED') THEN
        NEW.completed_at := COALESCE(NEW.completed_at, NOW());
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_file_transition
BEFORE UPDATE OF state ON imported_files
FOR EACH ROW
EXECUTE FUNCTION validate_file_transition();

-- ------------------------------------------------------------
-- 7. Record integrity and error logging
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_import_record()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.employee_name IS NOT NULL
       AND BTRIM(NEW.employee_name) = '' THEN
        RAISE EXCEPTION 'Employee name cannot be blank'
            USING ERRCODE = '23514';
    END IF;

    IF NEW.department_code IS NOT NULL
       AND BTRIM(NEW.department_code) = '' THEN
        RAISE EXCEPTION 'Department code cannot be blank'
            USING ERRCODE = '23514';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_import_record
BEFORE INSERT OR UPDATE ON imported_records
FOR EACH ROW
EXECUTE FUNCTION validate_import_record();

-- ------------------------------------------------------------
-- 8. Role-based authorization
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION assert_operator_access(
    p_user_id BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_role access_role;
    v_active BOOLEAN;
BEGIN
    SELECT role, active
    INTO v_role, v_active
    FROM app_users
    WHERE user_id = p_user_id;

    IF NOT FOUND OR NOT v_active THEN
        RAISE EXCEPTION 'User does not exist or is inactive'
            USING ERRCODE = '42501';
    END IF;

    IF v_role NOT IN ('ADMIN', 'OPERATOR') THEN
        RAISE EXCEPTION 'User lacks file processing permission'
            USING ERRCODE = '42501';
    END IF;
END;
$$;

-- ------------------------------------------------------------
-- 9. File registration
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION register_file(
    p_filename VARCHAR,
    p_storage_key VARCHAR,
    p_hash VARCHAR,
    p_size BIGINT,
    p_content_type VARCHAR,
    p_user_id BIGINT,
    p_policy_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_file_id BIGINT;
BEGIN
    PERFORM assert_operator_access(p_user_id);

    IF p_filename IS NULL OR BTRIM(p_filename) = '' THEN
        RAISE EXCEPTION 'Filename cannot be empty';
    END IF;

    IF p_storage_key IS NULL OR BTRIM(p_storage_key) = '' THEN
        RAISE EXCEPTION 'Storage key cannot be empty';
    END IF;

    IF p_hash !~ '^[a-f0-9]{64}$' THEN
        RAISE EXCEPTION 'Invalid SHA-256 hash';
    END IF;

    IF p_size < 0 THEN
        RAISE EXCEPTION 'File size cannot be negative';
    END IF;

    IF p_content_type NOT IN (
        'text/csv',
        'application/json'
    ) THEN
        RAISE EXCEPTION 'Unsupported file content type';
    END IF;

    INSERT INTO imported_files (
        original_filename,
        storage_key,
        sha256_hash,
        file_size_bytes,
        content_type,
        uploaded_by,
        policy_id
    )
    VALUES (
        p_filename,
        p_storage_key,
        p_hash,
        p_size,
        p_content_type,
        p_user_id,
        p_policy_id
    )
    RETURNING file_id INTO v_file_id;

    INSERT INTO audit_events (
        file_id,
        actor_id,
        event_type,
        event_details
    )
    VALUES (
        v_file_id,
        p_user_id,
        'FILE_REGISTERED',
        jsonb_build_object(
            'filename', p_filename,
            'size_bytes', p_size,
            'content_type', p_content_type
        )
    );

    RETURN v_file_id;

EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION
            'Duplicate storage key or file registration conflict';
END;
$$;

-- ------------------------------------------------------------
-- 10. Validate imported file records
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_file_records(
    p_file_id BIGINT,
    p_user_id BIGINT
)
RETURNS TABLE (
    total_records BIGINT,
    valid_records BIGINT,
    rejected_records BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_file imported_files%ROWTYPE;
    v_policy import_policies%ROWTYPE;
    v_total BIGINT;
BEGIN
    PERFORM assert_operator_access(p_user_id);

    SELECT *
    INTO v_file
    FROM imported_files
    WHERE file_id = p_file_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'File % not found', p_file_id;
    END IF;

    IF v_file.state <> 'RECEIVED' THEN
        RAISE EXCEPTION 'File must be in RECEIVED state';
    END IF;

    SELECT *
    INTO v_policy
    FROM import_policies
    WHERE policy_id = v_file.policy_id
      AND active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'No active import policy exists';
    END IF;

    UPDATE imported_files
    SET state = 'VALIDATING'
    WHERE file_id = p_file_id;

    SELECT COUNT(*)
    INTO v_total
    FROM imported_records
    WHERE file_id = p_file_id;

    IF v_total = 0 THEN
        INSERT INTO processing_errors (
            file_id,
            error_code,
            error_message,
            severity
        )
        VALUES (
            p_file_id,
            'EMPTY_FILE',
            'No data records were imported.',
            'ERROR'
        );

        UPDATE imported_files
        SET state = 'FAILED'
        WHERE file_id = p_file_id;

        RETURN QUERY
        SELECT 0::BIGINT, 0::BIGINT, 0::BIGINT;

        RETURN;
    END IF;

    IF v_total > v_policy.maximum_records THEN
        RAISE EXCEPTION
            'File exceeds maximum record count of %',
            v_policy.maximum_records;
    END IF;

    -- Record failures are isolated and stored for review.
    INSERT INTO processing_errors (
        file_id,
        record_id,
        error_code,
        error_message,
        severity
    )
    SELECT
        r.file_id,
        r.record_id,
        CASE
            WHEN r.employee_name IS NULL
                OR BTRIM(r.employee_name) = ''
                THEN 'INVALID_EMPLOYEE'
            WHEN r.department_code IS NULL
                OR NOT (
                    r.department_code =
                    ANY(v_policy.allowed_departments)
                )
                THEN 'INVALID_DEPARTMENT'
            WHEN r.amount IS NULL OR r.amount < 0
                THEN 'INVALID_AMOUNT'
            WHEN r.amount > v_policy.maximum_amount
                THEN 'AMOUNT_EXCEEDED'
            ELSE 'UNKNOWN'
        END,
        CASE
            WHEN r.employee_name IS NULL
                OR BTRIM(r.employee_name) = ''
                THEN 'Employee name is missing.'
            WHEN r.department_code IS NULL
                OR NOT (
                    r.department_code =
                    ANY(v_policy.allowed_departments)
                )
                THEN 'Department is not permitted.'
            WHEN r.amount IS NULL OR r.amount < 0
                THEN 'Amount is invalid.'
            WHEN r.amount > v_policy.maximum_amount
                THEN 'Amount exceeds policy limit.'
            ELSE 'Unclassified validation failure.'
        END,
        'ERROR'
    FROM imported_records r
    WHERE r.file_id = p_file_id
      AND (
          r.employee_name IS NULL
          OR BTRIM(r.employee_name) = ''
          OR r.department_code IS NULL
          OR NOT (
              r.department_code =
              ANY(v_policy.allowed_departments)
          )
          OR r.amount IS NULL
          OR r.amount < 0
          OR r.amount > v_policy.maximum_amount
      );

    UPDATE imported_records r
    SET state = CASE
        WHEN EXISTS (
            SELECT 1
            FROM processing_errors e
            WHERE e.record_id = r.record_id
              AND e.severity IN ('ERROR', 'CRITICAL')
        )
        THEN 'REJECTED'::record_state
        ELSE 'VALID'::record_state
    END
    WHERE r.file_id = p_file_id;

    UPDATE imported_files
    SET state = 'VALIDATED'
    WHERE file_id = p_file_id;

    INSERT INTO audit_events (
        file_id,
        actor_id,
        event_type,
        event_details
    )
    VALUES (
        p_file_id,
        p_user_id,
        'FILE_VALIDATED',
        jsonb_build_object('records', v_total)
    );

    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT,
        COUNT(*) FILTER (
            WHERE state = 'VALID'
        )::BIGINT,
        COUNT(*) FILTER (
            WHERE state = 'REJECTED'
        )::BIGINT
    FROM imported_records
    WHERE file_id = p_file_id;
END;
$$;

-- ------------------------------------------------------------
-- 11. Process eligible records
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE process_validated_file(
    p_file_id BIGINT,
    p_user_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_file_state file_state;
    v_valid BIGINT;
    v_rejected BIGINT;
BEGIN
    PERFORM assert_operator_access(p_user_id);

    SELECT state
    INTO v_file_state
    FROM imported_files
    WHERE file_id = p_file_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'File does not exist';
    END IF;

    IF v_file_state <> 'VALIDATED' THEN
        RAISE EXCEPTION
            'Only VALIDATED files can be processed';
    END IF;

    UPDATE imported_files
    SET state = 'PROCESSING'
    WHERE file_id = p_file_id;

    -- This represents a database-side business processing step.
    UPDATE imported_records
    SET
        state = 'COMPLETED',
        processed_at = NOW()
    WHERE file_id = p_file_id
      AND state = 'VALID';

    SELECT
        COUNT(*) FILTER (
            WHERE state = 'COMPLETED'
        ),
        COUNT(*) FILTER (
            WHERE state IN ('REJECTED', 'FAILED')
        )
    INTO v_valid, v_rejected
    FROM imported_records
    WHERE file_id = p_file_id;

    UPDATE imported_files
    SET state = CASE
        WHEN v_valid = 0 THEN 'FAILED'::file_state
        WHEN v_rejected > 0 THEN 'PARTIALLY_FAILED'::file_state
        ELSE 'COMPLETED'::file_state
    END
    WHERE file_id = p_file_id;

    INSERT INTO audit_events (
        file_id,
        actor_id,
        event_type,
        event_details
    )
    VALUES (
        p_file_id,
        p_user_id,
        'FILE_PROCESSED',
        jsonb_build_object(
            'completed_records', v_valid,
            'rejected_records', v_rejected
        )
    );

EXCEPTION
    WHEN OTHERS THEN
        -- Re-raise so the caller can roll back the transaction.
        RAISE;
END;
$$;

-- ------------------------------------------------------------
-- 12. Reporting views
-- ------------------------------------------------------------

CREATE VIEW file_processing_summary AS
SELECT
    f.file_id,
    f.original_filename,
    f.state,
    f.uploaded_at,
    f.completed_at,
    u.username AS uploaded_by,
    COUNT(r.record_id) AS total_records,
    COUNT(r.record_id) FILTER (
        WHERE r.state = 'COMPLETED'
    ) AS completed_records,
    COUNT(r.record_id) FILTER (
        WHERE r.state = 'REJECTED'
    ) AS rejected_records,
    COUNT(e.error_id) AS error_count
FROM imported_files f
JOIN app_users u
    ON u.user_id = f.uploaded_by
LEFT JOIN imported_records r
    ON r.file_id = f.file_id
LEFT JOIN processing_errors e
    ON e.file_id = f.file_id
GROUP BY
    f.file_id,
    f.original_filename,
    f.state,
    f.uploaded_at,
    f.completed_at,
    u.username;

CREATE VIEW department_import_report AS
SELECT
    r.department_code,
    COUNT(*) AS total_records,
    SUM(r.amount) AS total_amount,
    AVG(r.amount) AS average_amount,
    COUNT(*) FILTER (
        WHERE r.state = 'COMPLETED'
    ) AS completed_records,
    COUNT(*) FILTER (
        WHERE r.state = 'REJECTED'
    ) AS rejected_records
FROM imported_records r
GROUP BY r.department_code;

-- ------------------------------------------------------------
-- 13. Sample data
-- ------------------------------------------------------------

INSERT INTO app_users(username, role)
VALUES
    ('admin_user', 'ADMIN'),
    ('operator_user', 'OPERATOR'),
    ('audit_user', 'AUDITOR');

INSERT INTO departments(
    department_code,
    department_name
)
VALUES
    ('IT', 'Information Technology'),
    ('FINANCE', 'Finance'),
    ('HR', 'Human Resources');

INSERT INTO import_policies(
    policy_name,
    maximum_amount,
    allowed_departments,
    maximum_records
)
VALUES (
    'Standard Expense Import',
    10000,
    ARRAY['IT', 'FINANCE'],
    1000
);

-- ------------------------------------------------------------
-- 14. Register a file
-- ------------------------------------------------------------

DO $$
DECLARE
    v_file_id BIGINT;
BEGIN
    v_file_id := register_file(
        'monthly_expenses.csv',
        'imports/2026/monthly_expenses.csv',
        repeat('a', 64),
        2048,
        'text/csv',
        (
            SELECT user_id
            FROM app_users
            WHERE username = 'operator_user'
        ),
        (
            SELECT policy_id
            FROM import_policies
            WHERE policy_name = 'Standard Expense Import'
        )
    );

    INSERT INTO imported_records (
        file_id,
        source_row_number,
        employee_name,
        department_code,
        amount
    )
    VALUES
        (v_file_id, 2, 'Aarav Sharma', 'IT', 1200),
        (v_file_id, 3, 'Meera Singh', 'FINANCE', 4500),
        (v_file_id, 4, 'Rohan Verma', 'HR', 800),
        (v_file_id, 5, 'Anaya Gupta', 'IT', -50),
        (v_file_id, 6, 'Kabir Das', 'IT', 25000);

    RAISE NOTICE 'Registered file ID: %', v_file_id;
END;
$$;

-- ------------------------------------------------------------
-- 15. Transactional workflow execution
-- ------------------------------------------------------------

BEGIN;

DO $$
DECLARE
    v_file_id BIGINT;
    v_user_id BIGINT;
    v_total BIGINT;
    v_valid BIGINT;
    v_rejected BIGINT;
BEGIN
    SELECT file_id
    INTO v_file_id
    FROM imported_files
    WHERE original_filename = 'monthly_expenses.csv';

    SELECT user_id
    INTO v_user_id
    FROM app_users
    WHERE username = 'operator_user';

    SELECT total_records, valid_records, rejected_records
    INTO v_total, v_valid, v_rejected
    FROM validate_file_records(v_file_id, v_user_id);

    RAISE NOTICE
        'Validation: total %, valid %, rejected %',
        v_total, v_valid, v_rejected;

    CALL process_validated_file(v_file_id, v_user_id);
END;
$$;

COMMIT;

-- ------------------------------------------------------------
-- 16. Retrieval and evaluation queries
-- ------------------------------------------------------------

-- File state and processing results.
SELECT *
FROM file_processing_summary
ORDER BY uploaded_at DESC;

-- Record-level details.
SELECT
    record_id,
    source_row_number,
    employee_name,
    department_code,
    amount,
    state
FROM imported_records
ORDER BY source_row_number;

-- Detailed validation errors.
SELECT
    e.error_code,
    e.error_message,
    e.severity,
    r.source_row_number
FROM processing_errors e
LEFT JOIN imported_records r
    ON r.record_id = e.record_id
ORDER BY e.occurred_at;

-- Department-level aggregation.
SELECT *
FROM department_import_report
ORDER BY total_amount DESC NULLS LAST;

-- CTE-based file quality assessment.
WITH quality AS (
    SELECT
        file_id,
        COUNT(*) AS total,
        COUNT(*) FILTER (
            WHERE state = 'COMPLETED'
        ) AS completed,
        COUNT(*) FILTER (
            WHERE state = 'REJECTED'
        ) AS rejected
    FROM imported_records
    GROUP BY file_id
)
SELECT
    file_id,
    total,
    completed,
    rejected,
    ROUND(
        100.0 * completed / NULLIF(total, 0),
        2
    ) AS completion_percentage
FROM quality;

-- ------------------------------------------------------------
-- 17. Eligibility determination
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION file_is_eligible(
    p_file_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT
        EXISTS (
            SELECT 1
            FROM imported_files
            WHERE file_id = p_file_id
              AND state = 'VALIDATED'
        )
        AND EXISTS (
            SELECT 1
            FROM imported_records
            WHERE file_id = p_file_id
              AND state = 'VALID'
        );
$$;

SELECT
    file_id,
    original_filename,
    file_is_eligible(file_id) AS eligible_for_processing
FROM imported_files;

-- ------------------------------------------------------------
-- 18. Exception demonstration
-- ------------------------------------------------------------

DO $$
DECLARE
    v_file_id BIGINT;
BEGIN
    SELECT file_id
    INTO v_file_id
    FROM imported_files
    LIMIT 1;

    BEGIN
        -- An invalid state transition is rejected by the trigger.
        UPDATE imported_files
        SET state = 'RECEIVED'
        WHERE file_id = v_file_id;

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Invalid state transition rejected.';
        WHEN OTHERS THEN
            RAISE NOTICE
                'Expected workflow error: %',
                SQLERRM;
    END;
END;
$$;

-- ------------------------------------------------------------
-- 19. Operational reporting
-- ------------------------------------------------------------

SELECT
    state,
    COUNT(*) AS files,
    SUM(file_size_bytes) AS total_bytes
FROM imported_files
GROUP BY state
ORDER BY state;

SELECT
    severity,
    COUNT(*) AS error_count
FROM processing_errors
GROUP BY severity
ORDER BY severity;

SELECT
    event_type,
    COUNT(*) AS event_count
FROM audit_events
GROUP BY event_type
ORDER BY event_type;

-- ------------------------------------------------------------
-- 20. Security considerations
-- ------------------------------------------------------------
-- In production:
-- 1. Store files outside PostgreSQL or in controlled object storage.
-- 2. Validate file content and size before registering metadata.
-- 3. Never trust a user-provided storage path.
-- 4. Restrict EXECUTE privileges on processing functions.
-- 5. Apply row-level security where tenant isolation is required.
-- 6. Avoid logging passwords, tokens, or confidential file contents.
-- 7. Use separate database roles for upload, processing and audit.
-- 8. Coordinate external file operations with database transactions
--    through staging, checksums and retry-safe workflows.
-- 9. Use a durable job queue for long-running processing.
-- 10. A database transaction cannot roll back an external file write.

RESET search_path;
