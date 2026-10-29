DROP SCHEMA IF EXISTS exception_demo CASCADE;
CREATE SCHEMA exception_demo;

SET search_path = exception_demo, public;

CREATE TYPE severity AS ENUM ('warning', 'error', 'critical');

CREATE TABLE users (
    user_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name text NOT NULL,
    email text NOT NULL UNIQUE,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT users_name_not_blank
        CHECK (length(btrim(full_name)) > 0),
    CONSTRAINT users_email_shape
        CHECK (position('@' IN email) > 1)
);

CREATE TABLE application_errors (
    error_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id bigint REFERENCES users(user_id),
    severity severity NOT NULL,
    error_code text NOT NULL,
    message text NOT NULL,
    original_message text,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT application_errors_code_not_blank
        CHECK (length(btrim(error_code)) > 0),
    CONSTRAINT application_errors_message_not_blank
        CHECK (length(btrim(message)) > 0)
);

CREATE TABLE user_operations (
    operation_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id bigint REFERENCES users(user_id),
    operation_name text NOT NULL,
    state text NOT NULL,
    started_at timestamptz NOT NULL DEFAULT now(),
    completed_at timestamptz,
    failure_error_id bigint REFERENCES application_errors(error_id),
    CONSTRAINT operation_name_not_blank
        CHECK (length(btrim(operation_name)) > 0),
    CONSTRAINT operation_state_valid
        CHECK (state IN ('started', 'succeeded', 'failed')),
    CONSTRAINT operation_completion_consistent
        CHECK (
            (state = 'started' AND completed_at IS NULL)
            OR
            (state IN ('succeeded', 'failed') AND completed_at IS NOT NULL)
        )
);

CREATE INDEX application_errors_created_at_idx
    ON application_errors (created_at);

CREATE INDEX application_errors_user_id_idx
    ON application_errors (user_id);

CREATE OR REPLACE FUNCTION validate_operation_transition()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.state = 'succeeded' AND NEW.state <> 'succeeded' THEN
        RAISE EXCEPTION
            USING
                ERRCODE = 'P0001',
                MESSAGE = 'A succeeded operation cannot be reopened';
    END IF;

    IF OLD.state = 'failed' AND NEW.state = 'started' THEN
        RAISE EXCEPTION
            USING
                ERRCODE = 'P0001',
                MESSAGE = 'A failed operation cannot return to started';
    END IF;

    IF NEW.state = 'failed' AND NEW.failure_error_id IS NULL THEN
        RAISE EXCEPTION
            USING
                ERRCODE = 'P0001',
                MESSAGE = 'Failed operations require failure_error_id';
    END IF;

    IF NEW.state = 'succeeded' AND NEW.failure_error_id IS NOT NULL THEN
        RAISE EXCEPTION
            USING
                ERRCODE = 'P0001',
                MESSAGE = 'Succeeded operations cannot contain a failure error';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER operation_transition_trigger
BEFORE UPDATE ON user_operations
FOR EACH ROW
EXECUTE FUNCTION validate_operation_transition();

CREATE OR REPLACE FUNCTION create_user(
    p_full_name text,
    p_email text
)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_id bigint;
BEGIN
    IF p_full_name IS NULL OR length(btrim(p_full_name)) = 0 THEN
        RAISE EXCEPTION
            USING
                ERRCODE = '22023',
                MESSAGE = 'Full name cannot be blank';
    END IF;

    IF p_email IS NULL OR position('@' IN p_email) <= 1 THEN
        RAISE EXCEPTION
            USING
                ERRCODE = '22023',
                MESSAGE = 'Email format is invalid';
    END IF;

    INSERT INTO users (full_name, email)
    VALUES (btrim(p_full_name), lower(btrim(p_email)))
    RETURNING user_id INTO v_user_id;

    RETURN v_user_id;
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION
            USING
                ERRCODE = '23505',
                MESSAGE = 'A user with this email already exists',
                DETAIL = p_email;
END;
$$;

CREATE OR REPLACE FUNCTION parse_positive_integer(
    p_value text
)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    v_value integer;
BEGIN
    BEGIN
        v_value := p_value::integer;
    EXCEPTION
        WHEN invalid_text_representation THEN
            RAISE EXCEPTION
                USING
                    ERRCODE = '22P02',
                    MESSAGE = 'Value is not a valid integer',
                    DETAIL = coalesce(p_value, '<null>');
    END;

    IF v_value <= 0 THEN
        RAISE EXCEPTION
            USING
                ERRCODE = '22023',
                MESSAGE = 'Integer must be greater than zero';
    END IF;

    RETURN v_value;
END;
$$;

CREATE OR REPLACE PROCEDURE record_failure(
    p_operation_id bigint,
    p_error_code text,
    p_message text,
    p_original_message text DEFAULT NULL,
    p_severity severity DEFAULT 'error'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_error_id bigint;
BEGIN
    INSERT INTO application_errors (
        user_id,
        severity,
        error_code,
        message,
        original_message
    )
    SELECT
        user_id,
        p_severity,
        p_error_code,
        p_message,
        p_original_message
    FROM user_operations
    WHERE operation_id = p_operation_id
    RETURNING error_id INTO v_error_id;

    IF v_error_id IS NULL THEN
        RAISE EXCEPTION
            USING
                ERRCODE = 'P0002',
                MESSAGE = 'Operation does not exist';
    END IF;

    UPDATE user_operations
    SET
        state = 'failed',
        completed_at = now(),
        failure_error_id = v_error_id
    WHERE operation_id = p_operation_id;
END;
$$;

CREATE VIEW operation_failure_report AS
SELECT
    o.operation_id,
    o.operation_name,
    o.state,
    u.full_name,
    u.email,
    e.severity,
    e.error_code,
    e.message,
    e.original_message,
    o.started_at,
    o.completed_at
FROM user_operations o
LEFT JOIN users u
    ON u.user_id = o.user_id
LEFT JOIN application_errors e
    ON e.error_id = o.failure_error_id;

INSERT INTO users (full_name, email)
VALUES
    ('Ada Lovelace', 'ada@example.com'),
    ('Grace Hopper', 'grace@example.com'),
    ('Katherine Johnson', 'katherine@example.com');

INSERT INTO application_errors (
    user_id,
    severity,
    error_code,
    message,
    original_message
)
VALUES
    (
        1,
        'error',
        'VALIDATION_ERROR',
        'User input failed validation',
        'email domain was missing'
    ),
    (
        2,
        'critical',
        'STORAGE_ERROR',
        'Persistent storage was unavailable',
        'permission denied'
    ),
    (
        3,
        'warning',
        'CONFIGURATION_ERROR',
        'Optional configuration was missing',
        NULL
    );

INSERT INTO user_operations (
    user_id,
    operation_name,
    state,
    started_at,
    completed_at,
    failure_error_id
)
VALUES
    (
        1,
        'profile_validation',
        'failed',
        now() - interval '30 minutes',
        now() - interval '29 minutes',
        1
    ),
    (
        2,
        'profile_persistence',
        'failed',
        now() - interval '20 minutes',
        now() - interval '19 minutes',
        2
    ),
    (
        3,
        'configuration_check',
        'succeeded',
        now() - interval '10 minutes',
        now() - interval '9 minutes',
        NULL
    );

-- RAISE EXCEPTION aborts the current statement or transaction unless handled.
DO $$
BEGIN
    BEGIN
        PERFORM parse_positive_integer('-5');
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Handled exception [%]: %',
                SQLSTATE,
                SQLERRM;
    END;
END;
$$;

DO $$
DECLARE
    v_operation_id bigint;
BEGIN
    INSERT INTO user_operations (
        user_id,
        operation_name,
        state
    )
    VALUES (
        1,
        'demonstrate_failure',
        'started'
    )
    RETURNING operation_id INTO v_operation_id;

    CALL record_failure(
        v_operation_id,
        'VALIDATION_ERROR',
        'Demonstration operation failed',
        'invalid business input',
        'error'
    );
END;
$$;

-- This transaction demonstrates atomic rollback.
BEGIN;

INSERT INTO users (full_name, email)
VALUES ('Transactional User', 'transaction@example.com');

-- The constraint deliberately rejects this invalid operation.
DO $$
BEGIN
    RAISE EXCEPTION
        USING
            ERRCODE = 'P0001',
            MESSAGE = 'Demonstration rollback';
END;
$$;

ROLLBACK;

SELECT
    user_id,
    full_name,
    email
FROM users
ORDER BY user_id;

SELECT
    severity,
    error_code,
    count(*) AS error_count
FROM application_errors
GROUP BY severity, error_code
ORDER BY severity, error_code;

SELECT
    operation_id,
    operation_name,
    state,
    full_name,
    severity,
    error_code,
    message
FROM operation_failure_report
ORDER BY operation_id;

SELECT
    state,
    count(*) AS operation_count
FROM user_operations
GROUP BY state
ORDER BY state;

SELECT
    user_id,
    count(*) AS failure_count
FROM application_errors
WHERE user_id IS NOT NULL
GROUP BY user_id
HAVING count(*) > 0
ORDER BY failure_count DESC;
