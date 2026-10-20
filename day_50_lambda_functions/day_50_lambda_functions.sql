DROP SCHEMA IF EXISTS lambda_demo CASCADE;
CREATE SCHEMA lambda_demo;
SET search_path TO lambda_demo;

-- A Lambda function is represented as independently deployable executable
-- behavior with a configured timeout and memory allocation.
CREATE TABLE lambda_functions (
    function_id BIGSERIAL PRIMARY KEY,
    function_name TEXT NOT NULL UNIQUE,
    runtime TEXT NOT NULL,
    memory_mb INTEGER NOT NULL DEFAULT 128,
    timeout_seconds INTEGER NOT NULL DEFAULT 3,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (btrim(function_name) <> ''),
    CHECK (memory_mb >= 128),
    CHECK (timeout_seconds BETWEEN 1 AND 900)
);

CREATE TABLE event_types (
    event_type_id BIGSERIAL PRIMARY KEY,
    event_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE lambda_routes (
    route_id BIGSERIAL PRIMARY KEY,
    function_id BIGINT NOT NULL REFERENCES lambda_functions(function_id),
    event_type_id BIGINT NOT NULL REFERENCES event_types(event_type_id),
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (function_id, event_type_id)
);

CREATE TABLE invocation_events (
    invocation_id UUID PRIMARY KEY,
    function_id BIGINT NOT NULL REFERENCES lambda_functions(function_id),
    event_type_id BIGINT NOT NULL REFERENCES event_types(event_type_id),
    idempotency_key TEXT,
    payload JSONB NOT NULL,
    status TEXT NOT NULL,
    result JSONB,
    error_message TEXT,
    duration_ms NUMERIC(12,3),
    invoked_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (status IN (
        'RECEIVED',
        'SUCCEEDED',
        'FAILED',
        'TIMED_OUT',
        'DUPLICATE'
    )),
    CHECK (duration_ms IS NULL OR duration_ms >= 0)
);

CREATE UNIQUE INDEX uq_successful_idempotency
ON invocation_events(function_id, idempotency_key)
WHERE idempotency_key IS NOT NULL
  AND status = 'SUCCEEDED';

CREATE INDEX idx_invocations_function_time
ON invocation_events(function_id, invoked_at DESC);

CREATE INDEX idx_invocations_status
ON invocation_events(status);

CREATE TABLE retry_policies (
    function_id BIGINT PRIMARY KEY
        REFERENCES lambda_functions(function_id)
        ON DELETE CASCADE,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    base_delay_ms INTEGER NOT NULL DEFAULT 100,
    CHECK (max_attempts BETWEEN 1 AND 10),
    CHECK (base_delay_ms >= 0)
);

CREATE TABLE dead_letter_events (
    dead_letter_id BIGSERIAL PRIMARY KEY,
    invocation_id UUID NOT NULL REFERENCES invocation_events(invocation_id),
    reason TEXT NOT NULL,
    stored_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION validate_invocation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status = 'SUCCEEDED' AND NEW.result IS NULL THEN
        RAISE EXCEPTION
            'Successful Lambda invocation must contain a result';
    END IF;

    IF NEW.status IN ('FAILED', 'TIMED_OUT')
       AND NULLIF(btrim(COALESCE(NEW.error_message, '')), '') IS NULL THEN
        RAISE EXCEPTION
            'Failed or timed-out invocation requires an error message';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_invocation
BEFORE INSERT OR UPDATE ON invocation_events
FOR EACH ROW
EXECUTE FUNCTION validate_invocation();

CREATE OR REPLACE FUNCTION record_invocation(
    p_function_name TEXT,
    p_event_name TEXT,
    p_invocation_id UUID,
    p_idempotency_key TEXT,
    p_payload JSONB,
    p_status TEXT,
    p_result JSONB DEFAULT NULL,
    p_error_message TEXT DEFAULT NULL,
    p_duration_ms NUMERIC DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_function_id BIGINT;
    v_event_type_id BIGINT;
BEGIN
    SELECT function_id
    INTO v_function_id
    FROM lambda_functions
    WHERE function_name = p_function_name
      AND enabled = TRUE;

    IF v_function_id IS NULL THEN
        RAISE EXCEPTION 'Enabled Lambda function not found: %',
            p_function_name;
    END IF;

    SELECT event_type_id
    INTO v_event_type_id
    FROM event_types
    WHERE event_name = p_event_name;

    IF v_event_type_id IS NULL THEN
        RAISE EXCEPTION 'Event type not found: %', p_event_name;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM lambda_routes
        WHERE function_id = v_function_id
          AND event_type_id = v_event_type_id
          AND enabled = TRUE
    ) THEN
        RAISE EXCEPTION
            'No enabled route from % to %',
            p_event_name,
            p_function_name;
    END IF;

    INSERT INTO invocation_events (
        invocation_id,
        function_id,
        event_type_id,
        idempotency_key,
        payload,
        status,
        result,
        error_message,
        duration_ms
    )
    VALUES (
        p_invocation_id,
        v_function_id,
        v_event_type_id,
        p_idempotency_key,
        p_payload,
        p_status,
        p_result,
        p_error_message,
        p_duration_ms
    );

    RETURN p_invocation_id;
END;
$$;

INSERT INTO lambda_functions (
    function_name,
    runtime,
    memory_mb,
    timeout_seconds
)
VALUES
    ('order-normalizer', 'python3.13', 256, 10),
    ('order-pricing', 'nodejs22.x', 256, 10),
    ('payment-processor', 'java17', 512, 15);

INSERT INTO event_types (event_name, description)
VALUES
    ('order.created', 'A new order has been submitted'),
    ('order.validated', 'An order has passed validation'),
    ('payment.requested', 'A payment should be processed');

INSERT INTO lambda_routes (function_id, event_type_id)
SELECT f.function_id, e.event_type_id
FROM lambda_functions f
CROSS JOIN event_types e
WHERE (f.function_name, e.event_name) IN (
    ('order-normalizer', 'order.created'),
    ('order-pricing', 'order.validated'),
    ('payment-processor', 'payment.requested')
);

INSERT INTO retry_policies (
    function_id,
    max_attempts,
    base_delay_ms
)
SELECT function_id, 3, 250
FROM lambda_functions;

-- Transactional event recording demonstrates that routing and invocation
-- metadata can be committed atomically.
BEGIN;

SELECT record_invocation(
    'order-normalizer',
    'order.created',
    '00000000-0000-0000-0000-000000000001',
    'ORDER-1001',
    '{"order_id":"ORD-1001","customer_id":"CUS-42","amount":7500,"currency":"INR"}',
    'SUCCEEDED',
    '{"order_id":"ORD-1001","validated":true}',
    NULL,
    18.420
);

COMMIT;

BEGIN;

SELECT record_invocation(
    'order-pricing',
    'order.validated',
    '00000000-0000-0000-0000-000000000002',
    'ORDER-1001-PRICING',
    '{"order_id":"ORD-1001","amount":7500,"currency":"INR"}',
    'SUCCEEDED',
    '{"order_id":"ORD-1001","discount":750,"payable":6750}',
    NULL,
    4.870
);

COMMIT;

BEGIN;

SELECT record_invocation(
    'payment-processor',
    'payment.requested',
    '00000000-0000-0000-0000-000000000003',
    'PAYMENT-1001',
    '{"order_id":"ORD-1001","amount":6750,"currency":"INR"}',
    'FAILED',
    NULL,
    'Downstream payment provider unavailable',
    120.500
);

INSERT INTO dead_letter_events (
    invocation_id,
    reason
)
VALUES (
    '00000000-0000-0000-0000-000000000003',
    'Transient payment-provider failure exceeded retry policy'
);

COMMIT;

-- A duplicate successful idempotency key is rejected by the partial
-- unique index. The failed invocation uses a different status and therefore
-- does not consume the successful idempotency key.
DO $$
BEGIN
    BEGIN
        PERFORM record_invocation(
            'order-normalizer',
            'order.created',
            '00000000-0000-0000-0000-000000000004',
            'ORDER-1001',
            '{"order_id":"ORD-1001","customer_id":"CUS-42","amount":7500}',
            'SUCCEEDED',
            '{"order_id":"ORD-1001","validated":true}',
            NULL,
            10.100
        );
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE
                'Duplicate successful idempotency key correctly rejected';
    END;
END;
$$;

-- Determine whether a function is configured to receive a particular event.
SELECT
    f.function_name,
    e.event_name,
    r.enabled AS route_enabled,
    f.enabled AS function_enabled
FROM lambda_routes r
JOIN lambda_functions f
    ON f.function_id = r.function_id
JOIN event_types e
    ON e.event_type_id = r.event_type_id
ORDER BY f.function_name, e.event_name;

-- Invocation reporting by function.
SELECT
    f.function_name,
    COUNT(*) AS invocations,
    COUNT(*) FILTER (WHERE i.status = 'SUCCEEDED') AS succeeded,
    COUNT(*) FILTER (WHERE i.status = 'FAILED') AS failed,
    COUNT(*) FILTER (WHERE i.status = 'TIMED_OUT') AS timed_out,
    ROUND(AVG(i.duration_ms), 3) AS average_duration_ms
FROM lambda_functions f
LEFT JOIN invocation_events i
    ON i.function_id = f.function_id
GROUP BY f.function_id, f.function_name
ORDER BY f.function_name;

-- CTE-based operational report identifies functions whose successful
-- invocation latency is high relative to their configured timeout.
WITH latency AS (
    SELECT
        f.function_name,
        f.timeout_seconds,
        AVG(i.duration_ms) AS average_ms,
        MAX(i.duration_ms) AS maximum_ms
    FROM lambda_functions f
    JOIN invocation_events i
        ON i.function_id = f.function_id
    WHERE i.status = 'SUCCEEDED'
    GROUP BY f.function_name, f.timeout_seconds
)
SELECT
    function_name,
    ROUND(average_ms, 3) AS average_ms,
    ROUND(maximum_ms, 3) AS maximum_ms,
    timeout_seconds * 1000 AS timeout_ms,
    ROUND(
        average_ms / (timeout_seconds * 1000) * 100,
        2
    ) AS average_timeout_utilization_percent
FROM latency
ORDER BY average_timeout_utilization_percent DESC;

-- Retry configuration is evaluated separately from invocation history.
SELECT
    f.function_name,
    rp.max_attempts,
    rp.base_delay_ms,
    POWER(2, rp.max_attempts - 1) * rp.base_delay_ms
        AS final_exponential_delay_ms
FROM retry_policies rp
JOIN lambda_functions f
    ON f.function_id = rp.function_id
ORDER BY f.function_name;

-- Identify failed events that may require dead-letter processing.
SELECT
    d.dead_letter_id,
    d.invocation_id,
    f.function_name,
    i.status,
    d.reason,
    d.stored_at
FROM dead_letter_events d
JOIN invocation_events i
    ON i.invocation_id = d.invocation_id
JOIN lambda_functions f
    ON f.function_id = i.function_id
ORDER BY d.stored_at DESC;
