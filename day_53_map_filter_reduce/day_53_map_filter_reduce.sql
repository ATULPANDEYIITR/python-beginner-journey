DROP SCHEMA IF EXISTS functional_collection_demo CASCADE;
CREATE SCHEMA functional_collection_demo;
SET search_path TO functional_collection_demo;

-- The relational model represents a collection-processing pipeline.
-- map-like behavior is represented by derived expressions,
-- filter-like behavior by WHERE clauses,
-- and reduce-like behavior by aggregate functions.

CREATE TYPE order_status AS ENUM ('paid', 'pending', 'cancelled');

CREATE TABLE department (
    department_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    department_name TEXT NOT NULL UNIQUE,
    CONSTRAINT department_name_not_blank
        CHECK (btrim(department_name) <> '')
);

CREATE TABLE customer (
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_name TEXT NOT NULL,
    CONSTRAINT customer_name_not_blank
        CHECK (btrim(customer_name) <> '')
);

CREATE TABLE sales_order (
    order_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customer(customer_id),
    department_id BIGINT NOT NULL REFERENCES department(department_id),
    amount NUMERIC(14, 2) NOT NULL,
    status order_status NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT amount_non_negative CHECK (amount >= 0)
);

CREATE INDEX sales_order_status_amount_idx
    ON sales_order (status, amount);

CREATE INDEX sales_order_department_idx
    ON sales_order (department_id);

-- This view is a map-like projection. Each row is transformed into
-- a reporting representation without changing the underlying data.
CREATE VIEW order_projection AS
SELECT
    o.order_id,
    c.customer_name,
    d.department_name,
    o.amount,
    round(o.amount * 0.015, 2) AS service_fee,
    round(o.amount * 1.015, 2) AS amount_with_fee,
    o.status
FROM sales_order AS o
JOIN customer AS c
    ON c.customer_id = o.customer_id
JOIN department AS d
    ON d.department_id = o.department_id;

INSERT INTO department (department_name)
VALUES
    ('Engineering'),
    ('Finance'),
    ('Operations');

INSERT INTO customer (customer_name)
VALUES
    ('Asha'),
    ('Rahul'),
    ('Meera'),
    ('Kabir'),
    ('Nisha');

INSERT INTO sales_order
    (customer_id, department_id, amount, status)
VALUES
    (1, 1, 12000.00, 'paid'),
    (2, 2, 4700.00, 'paid'),
    (3, 1, 18500.00, 'paid'),
    (4, 3, 9100.00, 'pending'),
    (5, 2, 7300.00, 'paid'),
    (1, 1, 2100.00, 'cancelled');

-- FILTER:
-- Select only paid orders meeting the revenue threshold.
SELECT
    order_id,
    customer_name,
    department_name,
    amount
FROM order_projection
WHERE status = 'paid'
  AND amount >= 5000
ORDER BY amount DESC;

-- MAP:
-- Transform each eligible amount into a derived value.
SELECT
    order_id,
    customer_name,
    amount,
    round(amount * 1.08, 2) AS projected_amount
FROM order_projection
WHERE status = 'paid'
  AND amount >= 5000
ORDER BY order_id;

-- REDUCE:
-- SUM reduces multiple eligible rows to one scalar.
SELECT
    COALESCE(SUM(amount), 0.00) AS total_eligible_revenue
FROM sales_order
WHERE status = 'paid'
  AND amount >= 5000;

-- The CTE makes the filter stage explicit before aggregation.
WITH eligible_orders AS (
    SELECT
        order_id,
        department_id,
        amount
    FROM sales_order
    WHERE status = 'paid'
      AND amount >= 5000
)
SELECT
    d.department_name,
    COUNT(e.order_id) AS order_count,
    COALESCE(SUM(e.amount), 0.00) AS revenue
FROM department AS d
LEFT JOIN eligible_orders AS e
    ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
ORDER BY revenue DESC, d.department_name;

-- A map/filter/reduce style query:
-- 1. eligible_orders filters rows,
-- 2. projected_orders derives a value,
-- 3. the final SELECT aggregates the derived values.
WITH eligible_orders AS (
    SELECT
        order_id,
        amount
    FROM sales_order
    WHERE status = 'paid'
      AND amount >= 5000
),
projected_orders AS (
    SELECT
        order_id,
        round(amount * 1.08, 2) AS projected_amount
    FROM eligible_orders
)
SELECT
    COUNT(*) AS eligible_count,
    COALESCE(SUM(projected_amount), 0.00) AS projected_total,
    COALESCE(AVG(projected_amount), 0.00) AS projected_average
FROM projected_orders;

-- A reusable function exposes the reduction as a database operation.
CREATE OR REPLACE FUNCTION eligible_revenue()
RETURNS NUMERIC(14, 2)
LANGUAGE SQL
STABLE
AS $$
    SELECT COALESCE(SUM(amount), 0.00)::NUMERIC(14, 2)
    FROM sales_order
    WHERE status = 'paid'
      AND amount >= 5000;
$$;

SELECT eligible_revenue();

-- Transactional behavior: an invalid amount violates the CHECK constraint.
-- The savepoint allows the transaction to continue after the expected failure.
BEGIN;

SAVEPOINT before_invalid_order;

DO $$
BEGIN
    BEGIN
        INSERT INTO sales_order
            (customer_id, department_id, amount, status)
        VALUES
            (1, 1, -100.00, 'paid');
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Rejected invalid negative order amount';
    END;
END
$$;

ROLLBACK TO SAVEPOINT before_invalid_order;

COMMIT;

-- Window functions preserve row-level results while calculating
-- aggregate context, which is useful when a reduction alone would lose
-- the identity of individual rows.
SELECT
    order_id,
    department_name,
    amount,
    round(
        SUM(amount) OVER (PARTITION BY department_name),
        2
    ) AS department_total
FROM order_projection
WHERE status = 'paid'
ORDER BY department_name, order_id;

-- Empty reductions use COALESCE so the result has a defined identity value.
SELECT
    COALESCE(
        SUM(amount) FILTER (
            WHERE status = 'paid' AND amount >= 1000000
        ),
        0.00
    ) AS empty_safe_reduction
FROM sales_order;
