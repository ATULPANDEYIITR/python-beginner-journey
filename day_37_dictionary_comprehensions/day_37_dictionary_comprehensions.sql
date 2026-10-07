-- Dictionary Comprehensions: relational representation of dictionary-style
-- transformations.
--
-- PostgreSQL is used because it provides strong JSONB support alongside
-- ordinary relational operations. SQL has no Python-style dictionary
-- comprehension syntax. The closest relational model is:
-- source rows -> filtering -> derived key/value expressions -> materialized
-- result relation or JSONB object.
--
-- This script demonstrates that distinction using an operational metrics
-- domain where key/value transformations are useful.

DROP SCHEMA IF EXISTS dictionary_comprehension_lab CASCADE;
CREATE SCHEMA dictionary_comprehension_lab;

SET search_path TO dictionary_comprehension_lab;

-- --------------------------------------------------------------------------
-- Source data
-- --------------------------------------------------------------------------

CREATE TABLE employees (
    employee_id integer PRIMARY KEY,
    employee_name text NOT NULL,
    department text NOT NULL,
    salary integer NOT NULL CHECK (salary >= 0),
    active boolean NOT NULL DEFAULT true
);

CREATE TABLE orders (
    order_id bigint PRIMARY KEY,
    customer_name text NOT NULL,
    amount numeric(12, 2) NOT NULL CHECK (amount >= 0),
    status text NOT NULL
        CHECK (status IN ('pending', 'completed', 'cancelled', 'refunded'))
);

CREATE INDEX idx_orders_customer
    ON orders (customer_name);

CREATE INDEX idx_orders_status
    ON orders (status);

INSERT INTO employees
    (employee_id, employee_name, department, salary, active)
VALUES
    (101, 'Asha', 'Engineering', 95000, true),
    (102, 'Rahul', 'Finance', 72000, true),
    (103, 'Meera', 'Engineering', 105000, false),
    (104, 'Vikram', 'Operations', 68000, true),
    (105, 'Neha', 'Engineering', 115000, true);

INSERT INTO orders
    (order_id, customer_name, amount, status)
VALUES
    (1001, 'Asha', 1200.00, 'completed'),
    (1002, 'Rahul', 800.00, 'completed'),
    (1003, 'Asha', 700.00, 'completed'),
    (1004, 'Meera', 2500.00, 'completed'),
    (1005, 'Rahul', 500.00, 'completed'),
    (1006, 'Vikram', 100.00, 'cancelled');

-- --------------------------------------------------------------------------
-- Basic dictionary-style transformation
-- --------------------------------------------------------------------------
--
-- Python:
-- {employee_id: salary * 2 for employee_id, salary in source.items()}
--
-- SQL expresses the same operation as a relation with one derived key
-- column and one derived value column.

SELECT
    employee_id AS dictionary_key,
    salary * 2 AS dictionary_value
FROM employees
ORDER BY employee_id;

-- --------------------------------------------------------------------------
-- Filtering before materialization
-- --------------------------------------------------------------------------
--
-- This corresponds to a comprehension with an if clause.

SELECT
    employee_id AS dictionary_key,
    salary AS dictionary_value
FROM employees
WHERE active
  AND salary >= 90000
ORDER BY employee_id;

-- --------------------------------------------------------------------------
-- Conditional values
-- --------------------------------------------------------------------------

SELECT
    employee_name AS dictionary_key,
    CASE
        WHEN salary >= 100000 THEN 'senior'
        WHEN salary >= 75000 THEN 'mid'
        ELSE 'entry'
    END AS dictionary_value
FROM employees
ORDER BY employee_name;

-- --------------------------------------------------------------------------
-- JSONB object construction
-- --------------------------------------------------------------------------
--
-- jsonb_object_agg is useful when the desired final representation is
-- actually a JSON object with dynamic keys. The key must be unique within
-- the intended business domain or the aggregation semantics must be known.

SELECT jsonb_object_agg(
    employee_id::text,
    salary
    ORDER BY employee_id
) AS salary_dictionary
FROM employees;

-- --------------------------------------------------------------------------
-- Filtered JSONB dictionary
-- --------------------------------------------------------------------------

SELECT jsonb_object_agg(
    employee_name,
    salary
    ORDER BY employee_name
) AS senior_salary_dictionary
FROM employees
WHERE active
  AND salary >= 90000;

-- --------------------------------------------------------------------------
-- Key transformation
-- --------------------------------------------------------------------------

SELECT jsonb_object_agg(
    upper(employee_name),
    department
    ORDER BY employee_name
) AS employee_department_dictionary
FROM employees
WHERE active;

-- --------------------------------------------------------------------------
-- Duplicate-key issue
-- --------------------------------------------------------------------------
--
-- A relational query may contain multiple rows with the same prospective
-- dictionary key. A comprehension using a normal dict would apply
-- last-write-wins behavior. PostgreSQL's jsonb_object_agg also resolves
-- duplicate keys to the later aggregated value, so applications should
-- establish uniqueness explicitly when correctness depends on it.

SELECT
    customer_name,
    count(*) AS order_count,
    sum(amount) AS total_amount
FROM orders
GROUP BY customer_name
ORDER BY customer_name;

-- --------------------------------------------------------------------------
-- One-to-many grouping
-- --------------------------------------------------------------------------
--
-- Instead of forcing duplicate dictionary keys into scalar values,
-- aggregate them into arrays. This corresponds to a Python pattern such as:
-- {department: [employee1, employee2] for department ...}

SELECT
    department,
    array_agg(employee_name ORDER BY employee_name) AS employees
FROM employees
GROUP BY department
ORDER BY department;

-- --------------------------------------------------------------------------
-- Aggregation followed by filtering
-- --------------------------------------------------------------------------
--
-- This is the SQL equivalent of:
-- totals = aggregate(...)
-- high_value = {customer: total for customer, total in totals.items()
--               if total >= 1500}

WITH customer_totals AS (
    SELECT
        customer_name,
        sum(amount) AS total_amount
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_name
)
SELECT
    customer_name AS dictionary_key,
    total_amount AS dictionary_value
FROM customer_totals
WHERE total_amount >= 1500
ORDER BY customer_name;

-- --------------------------------------------------------------------------
-- Materialized JSON dictionary for the operational report
-- --------------------------------------------------------------------------

WITH metrics AS (
    SELECT
        count(*) FILTER (WHERE status = 'completed') AS completed_orders,
        count(*) FILTER (WHERE status = 'cancelled') AS cancelled_orders,
        count(*) FILTER (WHERE status = 'refunded') AS refunded_orders,
        count(*) AS total_orders
    FROM orders
),
rates AS (
    SELECT
        round(
            cancelled_orders::numeric / NULLIF(total_orders, 0) * 100,
            2
        ) AS cancelled_rate,
        round(
            refunded_orders::numeric / NULLIF(total_orders, 0) * 100,
            2
        ) AS refunded_rate,
        completed_orders,
        total_orders
    FROM metrics
)
SELECT jsonb_build_object(
    'completed_orders', completed_orders,
    'total_orders', total_orders,
    'cancelled_rate', cancelled_rate,
    'refunded_rate', refunded_rate
) AS operational_dictionary
FROM rates;

-- --------------------------------------------------------------------------
-- Indexing for dictionary-like lookup
-- --------------------------------------------------------------------------
--
-- A dictionary is often used because lookup by key is important.
-- Relational systems use indexes for the analogous access pattern.

EXPLAIN
SELECT
    employee_id,
    employee_name,
    salary
FROM employees
WHERE employee_id = 103;

EXPLAIN
SELECT
    order_id,
    customer_name,
    amount
FROM orders
WHERE customer_name = 'Asha';

-- --------------------------------------------------------------------------
-- JSONB transformation with a common table expression
-- --------------------------------------------------------------------------

WITH active_employees AS (
    SELECT
        employee_name,
        department,
        salary
    FROM employees
    WHERE active
),
salary_bands AS (
    SELECT
        employee_name,
        CASE
            WHEN salary >= 100000 THEN 'senior'
            WHEN salary >= 75000 THEN 'mid'
            ELSE 'entry'
        END AS band
    FROM active_employees
)
SELECT jsonb_object_agg(
    employee_name,
    band
    ORDER BY employee_name
) AS employee_salary_bands
FROM salary_bands;

-- --------------------------------------------------------------------------
-- Transactional validation
-- --------------------------------------------------------------------------
--
-- Database constraints prevent invalid amounts regardless of whether data
-- originated from Python, JavaScript, Java, C++, or another client.
-- The transaction demonstrates explicit commit/rollback semantics.

BEGIN;

INSERT INTO orders
    (order_id, customer_name, amount, status)
VALUES
    (1007, 'Neha', 3200.00, 'completed');

COMMIT;

-- This statement would fail because the CHECK constraint rejects negatives.
-- It is deliberately kept commented so the complete script remains
-- executable without an intentional transaction failure.
--
-- BEGIN;
-- INSERT INTO orders
--     (order_id, customer_name, amount, status)
-- VALUES
--     (1008, 'Invalid Customer', -1.00, 'completed');
-- ROLLBACK;

-- --------------------------------------------------------------------------
-- A reusable SQL view
-- --------------------------------------------------------------------------

CREATE OR REPLACE VIEW active_employee_dictionary AS
SELECT
    employee_id AS dictionary_key,
    jsonb_build_object(
        'name', employee_name,
        'department', department,
        'salary', salary
    ) AS dictionary_value
FROM employees
WHERE active;

SELECT *
FROM active_employee_dictionary
ORDER BY dictionary_key;

-- --------------------------------------------------------------------------
-- Nested JSON dictionary
-- --------------------------------------------------------------------------
--
-- The relational rows represent the source. JSON aggregation provides a
-- nested dictionary-like representation while SQL keeps relational integrity.

SELECT jsonb_object_agg(
    department,
    employees
    ORDER BY department
) AS department_dictionary
FROM (
    SELECT
        department,
        jsonb_agg(
            jsonb_build_object(
                'employee_id', employee_id,
                'name', employee_name,
                'salary', salary
            )
            ORDER BY employee_name
        ) AS employees
    FROM employees
    WHERE active
    GROUP BY department
) grouped_departments;

-- --------------------------------------------------------------------------
-- Final query: dictionary-style operational index
-- --------------------------------------------------------------------------

WITH customer_totals AS (
    SELECT
        customer_name,
        sum(amount) AS total_amount
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_name
),
classified AS (
    SELECT
        customer_name,
        total_amount,
        CASE
            WHEN total_amount >= 50000 THEN 'high'
            WHEN total_amount >= 10000 THEN 'medium'
            ELSE 'low'
        END AS category
    FROM customer_totals
)
SELECT jsonb_object_agg(
    customer_name,
    jsonb_build_object(
        'total_amount', total_amount,
        'category', category
    )
    ORDER BY customer_name
) AS customer_dictionary
FROM classified;
