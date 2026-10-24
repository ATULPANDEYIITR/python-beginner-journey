DROP SCHEMA IF EXISTS reusable_functions CASCADE;

CREATE SCHEMA reusable_functions;

SET search_path TO reusable_functions, public;

CREATE TYPE function_status AS ENUM (
    'registered',
    'active',
    'disabled'
);

CREATE TYPE execution_status AS ENUM (
    'running',
    'succeeded',
    'failed'
);

CREATE TABLE reusable_function (
    function_id BIGSERIAL PRIMARY KEY,
    function_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    status function_status NOT NULL DEFAULT 'registered',
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT function_name_not_blank
        CHECK (length(btrim(function_name)) > 0),

    CONSTRAINT description_not_blank
        CHECK (length(btrim(description)) > 0),

    CONSTRAINT function_version_positive
        CHECK (version > 0)
);

CREATE TABLE function_parameter (
    parameter_id BIGSERIAL PRIMARY KEY,
    function_id BIGINT NOT NULL
        REFERENCES reusable_function(function_id)
        ON DELETE CASCADE,
    parameter_name TEXT NOT NULL,
    data_type TEXT NOT NULL,
    position INTEGER NOT NULL,
    required BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT parameter_name_not_blank
        CHECK (length(btrim(parameter_name)) > 0),

    CONSTRAINT parameter_type_not_blank
        CHECK (length(btrim(data_type)) > 0),

    CONSTRAINT parameter_position_positive
        CHECK (position > 0),

    CONSTRAINT unique_function_parameter_position
        UNIQUE (function_id, position),

    CONSTRAINT unique_function_parameter_name
        UNIQUE (function_id, parameter_name)
);

CREATE TABLE function_execution (
    execution_id BIGSERIAL PRIMARY KEY,
    function_id BIGINT NOT NULL
        REFERENCES reusable_function(function_id)
        ON DELETE RESTRICT,
    status execution_status NOT NULL DEFAULT 'running',
    input_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    output_data JSONB,
    error_message TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    completed_at TIMESTAMPTZ,

    CONSTRAINT execution_completion_consistency
        CHECK (
            (status = 'running'
             AND completed_at IS NULL)
            OR
            (status IN ('succeeded', 'failed')
             AND completed_at IS NOT NULL)
        ),

    CONSTRAINT successful_execution_has_output
        CHECK (
            status <> 'succeeded'
            OR output_data IS NOT NULL
        ),

    CONSTRAINT failed_execution_has_error
        CHECK (
            status <> 'failed'
            OR length(btrim(coalesce(error_message, ''))) > 0
        )
);

CREATE TABLE function_tag (
    function_id BIGINT NOT NULL
        REFERENCES reusable_function(function_id)
        ON DELETE CASCADE,
    tag TEXT NOT NULL,

    PRIMARY KEY (function_id, tag),

    CONSTRAINT tag_not_blank
        CHECK (length(btrim(tag)) > 0),

    CONSTRAINT tag_length
        CHECK (length(tag) <= 40)
);

CREATE INDEX idx_function_execution_function_time
    ON function_execution (function_id, started_at DESC);

CREATE INDEX idx_function_execution_status
    ON function_execution (status);

CREATE INDEX idx_function_tag_tag
    ON function_tag (tag);

CREATE OR REPLACE FUNCTION touch_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := clock_timestamp();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_touch_function
BEFORE UPDATE ON reusable_function
FOR EACH ROW
EXECUTE FUNCTION touch_updated_at();

CREATE OR REPLACE FUNCTION validate_execution_transition()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.status <> 'running' AND NEW.status <> OLD.status THEN
        RAISE EXCEPTION
            'Execution % cannot transition from % to %',
            OLD.execution_id,
            OLD.status,
            NEW.status;
    END IF;

    IF NEW.status = 'succeeded' THEN
        NEW.completed_at := COALESCE(
            NEW.completed_at,
            clock_timestamp()
        );
    END IF;

    IF NEW.status = 'failed' THEN
        NEW.completed_at := COALESCE(
            NEW.completed_at,
            clock_timestamp()
        );

        IF length(btrim(coalesce(NEW.error_message, ''))) = 0 THEN
            RAISE EXCEPTION
                'Failed execution requires an error message';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_execution_transition
BEFORE UPDATE ON function_execution
FOR EACH ROW
EXECUTE FUNCTION validate_execution_transition();

CREATE OR REPLACE FUNCTION register_function(
    p_name TEXT,
    p_description TEXT,
    p_version INTEGER DEFAULT 1
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    new_function_id BIGINT;
BEGIN
    IF length(btrim(p_name)) = 0 THEN
        RAISE EXCEPTION 'Function name cannot be blank';
    END IF;

    IF length(btrim(p_description)) = 0 THEN
        RAISE EXCEPTION 'Function description cannot be blank';
    END IF;

    IF p_version <= 0 THEN
        RAISE EXCEPTION 'Function version must be positive';
    END IF;

    INSERT INTO reusable_function (
        function_name,
        description,
        version
    )
    VALUES (
        btrim(p_name),
        btrim(p_description),
        p_version
    )
    RETURNING function_id
    INTO new_function_id;

    RETURN new_function_id;
END;
$$;

CREATE OR REPLACE FUNCTION start_execution(
    p_function_id BIGINT,
    p_input JSONB DEFAULT '{}'::jsonb
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    new_execution_id BIGINT;
    current_status function_status;
BEGIN
    SELECT status
    INTO current_status
    FROM reusable_function
    WHERE function_id = p_function_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Function % does not exist',
            p_function_id;
    END IF;

    IF current_status <> 'active' THEN
        RAISE EXCEPTION
            'Function % is not active',
            p_function_id;
    END IF;

    INSERT INTO function_execution (
        function_id,
        input_data
    )
    VALUES (
        p_function_id,
        COALESCE(p_input, '{}'::jsonb)
    )
    RETURNING execution_id
    INTO new_execution_id;

    RETURN new_execution_id;
END;
$$;

CREATE OR REPLACE FUNCTION complete_execution(
    p_execution_id BIGINT,
    p_output JSONB
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE function_execution
    SET
        status = 'succeeded',
        output_data = p_output
    WHERE execution_id = p_execution_id
      AND status = 'running';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Running execution % does not exist',
            p_execution_id;
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION fail_execution(
    p_execution_id BIGINT,
    p_error TEXT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    IF length(btrim(p_error)) = 0 THEN
        RAISE EXCEPTION
            'Failure reason cannot be blank';
    END IF;

    UPDATE function_execution
    SET
        status = 'failed',
        error_message = p_error
    WHERE execution_id = p_execution_id
      AND status = 'running';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Running execution % does not exist',
            p_execution_id;
    END IF;
END;
$$;

CREATE OR REPLACE VIEW function_execution_report AS
SELECT
    rf.function_id,
    rf.function_name,
    rf.version,
    rf.status AS function_status,
    COUNT(fe.execution_id) AS total_executions,
    COUNT(*) FILTER (
        WHERE fe.status = 'succeeded'
    ) AS successful_executions,
    COUNT(*) FILTER (
        WHERE fe.status = 'failed'
    ) AS failed_executions,
    ROUND(
        100.0
        * COUNT(*) FILTER (
            WHERE fe.status = 'succeeded'
        )
        / NULLIF(COUNT(fe.execution_id), 0),
        2
    ) AS success_rate
FROM reusable_function rf
LEFT JOIN function_execution fe
    ON fe.function_id = rf.function_id
GROUP BY
    rf.function_id,
    rf.function_name,
    rf.version,
    rf.status;

INSERT INTO reusable_function (
    function_name,
    description,
    status,
    version
)
VALUES
(
    'normalize_tags',
    'Normalizes, validates, deduplicates, and sorts textual tags.',
    'active',
    1
),
(
    'calculate_statistics',
    'Calculates count, minimum, maximum, mean, and population standard deviation.',
    'active',
    2
),
(
    'validate_text',
    'Validates that a text value is non-null and non-empty after trimming.',
    'active',
    1
),
(
    'legacy_formatter',
    'Historical formatter retained for compatibility but not available for new execution.',
    'disabled',
    1
);

INSERT INTO function_parameter (
    function_id,
    parameter_name,
    data_type,
    position,
    required
)
SELECT
    function_id,
    'tags',
    'text[]',
    1,
    TRUE
FROM reusable_function
WHERE function_name = 'normalize_tags';

INSERT INTO function_parameter (
    function_id,
    parameter_name,
    data_type,
    position,
    required
)
SELECT
    function_id,
    'values',
    'numeric[]',
    1,
    TRUE
FROM reusable_function
WHERE function_name = 'calculate_statistics';

INSERT INTO function_parameter (
    function_id,
    parameter_name,
    data_type,
    position,
    required
)
SELECT
    function_id,
    'value',
    'text',
    1,
    TRUE
FROM reusable_function
WHERE function_name = 'validate_text';

INSERT INTO function_tag (function_id, tag)
SELECT function_id, tag
FROM reusable_function,
LATERAL unnest(
    CASE function_name
        WHEN 'normalize_tags'
            THEN ARRAY['validation', 'collections', 'text-processing']
        WHEN 'calculate_statistics'
            THEN ARRAY['statistics', 'validation', 'numeric-processing']
        WHEN 'validate_text'
            THEN ARRAY['validation', 'contracts']
        ELSE ARRAY['legacy']
    END
) AS tags(tag);

UPDATE reusable_function
SET status = 'active'
WHERE function_name IN (
    'normalize_tags',
    'calculate_statistics',
    'validate_text'
);

BEGIN;

WITH selected_function AS (
    SELECT function_id
    FROM reusable_function
    WHERE function_name = 'normalize_tags'
      AND status = 'active'
)
INSERT INTO function_execution (
    function_id,
    status,
    input_data,
    output_data,
    completed_at
)
SELECT
    function_id,
    'succeeded',
    '{"tags":["API","api","database"]}'::jsonb,
    '{"tags":["api","database"]}'::jsonb,
    clock_timestamp()
FROM selected_function;

COMMIT;

BEGIN;

WITH selected_function AS (
    SELECT function_id
    FROM reusable_function
    WHERE function_name = 'calculate_statistics'
      AND status = 'active'
)
INSERT INTO function_execution (
    function_id,
    status,
    input_data,
    error_message,
    completed_at
)
SELECT
    function_id,
    'failed',
    '{"values":[]}'::jsonb,
    'At least one numeric value is required.',
    clock_timestamp()
FROM selected_function;

COMMIT;

SELECT
    function_name,
    description,
    version,
    status
FROM reusable_function
ORDER BY function_name;

SELECT
    rf.function_name,
    fp.parameter_name,
    fp.data_type,
    fp.position,
    fp.required
FROM reusable_function rf
JOIN function_parameter fp
    ON fp.function_id = rf.function_id
ORDER BY
    rf.function_name,
    fp.position;

SELECT
    rf.function_name,
    ft.tag
FROM reusable_function rf
JOIN function_tag ft
    ON ft.function_id = rf.function_id
ORDER BY
    rf.function_name,
    ft.tag;

SELECT *
FROM function_execution_report
ORDER BY function_name;

SELECT
    rf.function_name,
    fe.status,
    fe.input_data,
    fe.output_data,
    fe.error_message,
    fe.started_at,
    fe.completed_at
FROM function_execution fe
JOIN reusable_function rf
    ON rf.function_id = fe.function_id
ORDER BY fe.started_at DESC;

SELECT
    rf.function_name,
    COUNT(fe.execution_id) AS executions,
    COUNT(*) FILTER (
        WHERE fe.status = 'failed'
    ) AS failures
FROM reusable_function rf
LEFT JOIN function_execution fe
    ON fe.function_id = rf.function_id
GROUP BY rf.function_name
HAVING COUNT(*) FILTER (
    WHERE fe.status = 'failed'
) > 0
ORDER BY failures DESC;

SELECT
    rf.function_name,
    jsonb_agg(
        jsonb_build_object(
            'parameter', fp.parameter_name,
            'type', fp.data_type,
            'required', fp.required
        )
        ORDER BY fp.position
    ) AS signature
FROM reusable_function rf
JOIN function_parameter fp
    ON fp.function_id = rf.function_id
GROUP BY rf.function_name
ORDER BY rf.function_name;

DO $$
DECLARE
    function_id_value BIGINT;
    execution_id_value BIGINT;
BEGIN
    function_id_value := register_function(
        'transactional_example',
        'Function used to demonstrate transactional execution tracking.',
        1
    );

    UPDATE reusable_function
    SET status = 'active'
    WHERE function_id = function_id_value;

    execution_id_value := start_execution(
        function_id_value,
        '{"request":"sample"}'::jsonb
    );

    PERFORM complete_execution(
        execution_id_value,
        '{"result":"accepted"}'::jsonb
    );

    RAISE NOTICE
        'Created function %, completed execution %',
        function_id_value,
        execution_id_value;
END;
$$;

SELECT *
FROM function_execution_report
WHERE function_name = 'transactional_example';

DO $$
BEGIN
    BEGIN
        PERFORM start_execution(
            (
                SELECT function_id
                FROM reusable_function
                WHERE function_name = 'legacy_formatter'
            ),
            '{}'::jsonb
        );
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Expected disabled-function failure: %',
                SQLERRM;
    END;
END;
$$;
