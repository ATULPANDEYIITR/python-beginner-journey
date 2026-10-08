-- Unpacking-oriented relational data model
-- PostgreSQL-compatible SQL
--
-- SQL has no Python-style tuple assignment unpacking. Its closest
-- relational counterpart is decomposing structured rows into named columns
-- through SELECT lists, row constructors, CTEs, JSON expansion, and
-- function outputs.
--
-- This model demonstrates how structured operational records can be stored,
-- validated, decomposed, aggregated, and transformed at the database layer.

DROP SCHEMA IF EXISTS unpacking_lab CASCADE;

CREATE SCHEMA unpacking_lab;

SET search_path TO unpacking_lab;

CREATE TABLE departments (
    department_id BIGSERIAL PRIMARY KEY,
    department_code TEXT NOT NULL UNIQUE,
    department_name TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (length(trim(department_code)) > 0),
    CHECK (length(trim(department_name)) > 0)
);

CREATE TABLE employees (
    employee_id BIGSERIAL PRIMARY KEY,
    employee_code TEXT NOT NULL UNIQUE,
    employee_name TEXT NOT NULL,
    department_id BIGINT NOT NULL
        REFERENCES departments(department_id),
    annual_salary NUMERIC(14, 2) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (length(trim(employee_code)) > 0),
    CHECK (length(trim(employee_name)) > 0),
    CHECK (annual_salary >= 0)
);

CREATE TABLE transactions (
    transaction_id BIGSERIAL PRIMARY KEY,
    transaction_code TEXT NOT NULL UNIQUE,
    employee_id BIGINT NOT NULL
        REFERENCES employees(employee_id),
    region TEXT NOT NULL,
    amount NUMERIC(14, 2) NOT NULL,
    transaction_status TEXT NOT NULL,
    tags TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (length(trim(transaction_code)) > 0),
    CHECK (length(trim(region)) > 0),
    CHECK (amount >= 0),
    CHECK (
        transaction_status IN (
            'completed',
            'pending',
            'cancelled'
        )
    )
);

CREATE INDEX idx_transactions_region_status
    ON transactions(region, transaction_status);

CREATE INDEX idx_transactions_employee
    ON transactions(employee_id);

CREATE INDEX idx_transactions_created_at
    ON transactions(created_at);

INSERT INTO departments (
    department_code,
    department_name
)
VALUES
    ('ENG', 'Engineering'),
    ('OPS', 'Operations'),
    ('FIN', 'Finance');

INSERT INTO employees (
    employee_code,
    employee_name,
    department_id,
    annual_salary
)
SELECT
    source.employee_code,
    source.employee_name,
    departments.department_id,
    source.annual_salary
FROM (
    VALUES
        ('E101', 'Atul', 'OPS', 87000.00),
        ('E102', 'Priya', 'ENG', 96000.00),
        ('E103', 'Rahul', 'FIN', 99000.00)
) AS source(
    employee_code,
    employee_name,
    department_code,
    annual_salary
)
JOIN departments
    ON departments.department_code =
       source.department_code;

INSERT INTO transactions (
    transaction_code,
    employee_id,
    region,
    amount,
    transaction_status,
    tags
)
SELECT
    source.transaction_code,
    employees.employee_id,
    source.region,
    source.amount,
    source.transaction_status,
    source.tags
FROM (
    VALUES
        (
            'TX001',
            'E101',
            'North',
            12500.00,
            'completed',
            ARRAY['approved', 'online']
        ),
        (
            'TX002',
            'E101',
            'North',
            3000.00,
            'pending',
            ARRAY['review']
        ),
        (
            'TX003',
            'E102',
            'South',
            8900.00,
            'completed',
            ARRAY['approved']
        ),
        (
            'TX004',
            'E101',
            'North',
            1500.00,
            'cancelled',
            ARRAY['cancelled']
        ),
        (
            'TX005',
            'E103',
            'South',
            2100.00,
            'completed',
            ARRAY['approved', 'priority']
        )
) AS source(
    transaction_code,
    employee_code,
    region,
    amount,
    transaction_status,
    tags
)
JOIN employees
    ON employees.employee_code =
       source.employee_code;

-- Row decomposition:
-- SELECT exposes individual fields from a relational row in named columns.
SELECT
    transaction_code,
    region,
    amount,
    transaction_status
FROM transactions
ORDER BY transaction_code;

-- A row constructor can create a structured value that can then be
-- decomposed with explicit column aliases.
SELECT
    row_data.transaction_code,
    row_data.region,
    row_data.amount
FROM (
    SELECT ROW(
        transaction_code,
        region,
        amount
    ) AS row_data
    FROM transactions
) AS source
CROSS JOIN LATERAL (
    SELECT
        (source.row_data).f1 AS transaction_code,
        (source.row_data).f2 AS region,
        (source.row_data).f3 AS amount
) AS row_data;

-- CTE decomposition makes a complex relational transformation easier to
-- reason about without duplicating expressions.
WITH transaction_parts AS (
    SELECT
        transaction_id,
        transaction_code,
        region,
        amount,
        transaction_status
    FROM transactions
)
SELECT
    transaction_code,
    region,
    amount
FROM transaction_parts
WHERE transaction_status = 'completed'
ORDER BY amount DESC;

-- Aggregate structured records after selecting their relevant fields.
WITH completed_transactions AS (
    SELECT
        transaction_code,
        region,
        amount
    FROM transactions
    WHERE transaction_status = 'completed'
)
SELECT
    region,
    COUNT(*) AS completed_count,
    SUM(amount) AS completed_amount,
    AVG(amount) AS average_amount
FROM completed_transactions
GROUP BY region
ORDER BY region;

-- Array expansion demonstrates decomposition of one structured attribute
-- into multiple relational rows.
SELECT
    transaction_code,
    tag
FROM transactions
CROSS JOIN LATERAL unnest(tags) AS tag
ORDER BY transaction_code, tag;

-- JSON decomposition is useful when external systems send structured
-- payloads whose fields must be extracted before normalization.
WITH raw_payload AS (
    SELECT
        '{
            "id": "TX900",
            "region": "West",
            "amount": 7200.50,
            "status": "completed",
            "metadata": {
                "source": "api",
                "priority": true
            }
        }'::jsonb AS payload
)
SELECT
    payload ->> 'id' AS transaction_code,
    payload ->> 'region' AS region,
    (payload ->> 'amount')::numeric AS amount,
    payload ->> 'status' AS transaction_status,
    payload #>> '{metadata,source}' AS source,
    (payload #>> '{metadata,priority}')::boolean AS priority
FROM raw_payload;

-- A domain-specific view provides a stable decomposed representation for
-- reporting consumers.
CREATE VIEW transaction_details AS
SELECT
    t.transaction_code,
    e.employee_code,
    e.employee_name,
    d.department_code,
    d.department_name,
    t.region,
    t.amount,
    t.transaction_status,
    t.created_at
FROM transactions AS t
JOIN employees AS e
    ON e.employee_id = t.employee_id
JOIN departments AS d
    ON d.department_id = e.department_id;

SELECT *
FROM transaction_details
ORDER BY transaction_code;

-- Database constraints reject invalid states before application-level
-- unpacking or processing can occur.
DO $$
BEGIN
    BEGIN
        INSERT INTO transactions (
            transaction_code,
            employee_id,
            region,
            amount,
            transaction_status
        )
        VALUES (
            'INVALID-NEGATIVE',
            (SELECT employee_id FROM employees WHERE employee_code = 'E101'),
            'West',
            -10.00,
            'completed'
        );
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'Negative amount correctly rejected by CHECK constraint';
    END;

    BEGIN
        INSERT INTO transactions (
            transaction_code,
            employee_id,
            region,
            amount,
            transaction_status
        )
        VALUES (
            'INVALID-STATUS',
            (SELECT employee_id FROM employees WHERE employee_code = 'E101'),
            'West',
            100.00,
            'unknown'
        );
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'Unsupported status correctly rejected by CHECK constraint';
    END;
END;
$$;

-- A transactional update demonstrates decomposition of values into local
-- variables before applying a controlled state change.
BEGIN;

DO $$
DECLARE
    selected_transaction RECORD;
    selected_amount NUMERIC(14, 2);
    selected_region TEXT;
BEGIN
    SELECT
        amount,
        region
    INTO
        selected_amount,
        selected_region
    FROM transactions
    WHERE transaction_code = 'TX002'
    FOR UPDATE;

    IF selected_amount IS NULL THEN
        RAISE EXCEPTION
            'Transaction TX002 does not exist';
    END IF;

    RAISE NOTICE
        'Selected region=% amount=%',
        selected_region,
        selected_amount;
END;
$$;

UPDATE transactions
SET
    transaction_status = 'completed',
    tags = array_append(tags, 'approved')
WHERE transaction_code = 'TX002'
  AND transaction_status = 'pending';

COMMIT;

-- Verify the state transition after the transaction.
SELECT
    transaction_code,
    region,
    amount,
    transaction_status,
    tags
FROM transactions
WHERE transaction_code = 'TX002';

-- A final reporting query exposes the decomposed business dimensions
-- needed by an operational dashboard.
SELECT
    department_name,
    region,
    transaction_status,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount
FROM transaction_details
GROUP BY
    department_name,
    region,
    transaction_status
ORDER BY
    department_name,
    region,
    transaction_status;
