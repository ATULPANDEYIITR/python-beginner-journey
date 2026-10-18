-- PostgreSQL demonstration of local variables, session variables,
-- routine variables, and shared persistent configuration.
-- PostgreSQL does not have ordinary application-style global variables.
-- GUC settings, tables, and routine variables have different scopes.

BEGIN;

CREATE SCHEMA IF NOT EXISTS scope_lab;

DROP TABLE IF EXISTS scope_lab.inventory_audit;
DROP TABLE IF EXISTS scope_lab.warehouse_stock;
DROP TABLE IF EXISTS scope_lab.application_config;

CREATE TABLE scope_lab.application_config (
    config_key TEXT PRIMARY KEY,
    config_value TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scope_lab.warehouse_stock (
    warehouse_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    warehouse_name TEXT NOT NULL UNIQUE,
    capacity INTEGER NOT NULL CHECK (capacity >= 0),
    stock INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT stock_within_capacity CHECK (stock >= 0 AND stock <= capacity)
);

CREATE TABLE scope_lab.inventory_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    warehouse_id BIGINT NOT NULL
        REFERENCES scope_lab.warehouse_stock(warehouse_id),
    operation TEXT NOT NULL CHECK (operation IN ('RECEIVE', 'DISPATCH')),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    stock_after INTEGER NOT NULL CHECK (stock_after >= 0),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX inventory_audit_warehouse_time_idx
    ON scope_lab.inventory_audit (warehouse_id, recorded_at DESC);

INSERT INTO scope_lab.application_config (config_key, config_value)
VALUES
    ('application_name', 'Inventory Control'),
    ('currency', 'INR'),
    ('tax_rate', '0.18');

INSERT INTO scope_lab.warehouse_stock (warehouse_name, capacity, stock)
VALUES
    ('Lucknow Hub', 400, 100),
    ('Kanpur Hub', 250, 60);

COMMIT;

-- A custom PostgreSQL configuration parameter can act as session-local
-- state. It is not a durable, cross-session global variable.
SET scope_lab.current_region = 'Uttar Pradesh';

SELECT current_setting('scope_lab.current_region') AS session_region;

-- SET LOCAL lasts only until the current transaction ends.
BEGIN;
SET LOCAL scope_lab.current_region = 'Delhi';
SELECT current_setting('scope_lab.current_region') AS transaction_region;
COMMIT;

SELECT current_setting('scope_lab.current_region') AS region_after_commit;

-- PL/pgSQL DECLARE variables are local to each routine invocation.
CREATE OR REPLACE FUNCTION scope_lab.calculate_invoice(
    p_unit_price NUMERIC,
    p_quantity INTEGER
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_subtotal NUMERIC(12, 2);
    v_tax_rate NUMERIC(6, 4);
    v_tax_amount NUMERIC(12, 2);
    v_total NUMERIC(12, 2);
BEGIN
    IF p_unit_price IS NULL OR p_unit_price < 0 THEN
        RAISE EXCEPTION 'Unit price must be non-negative';
    END IF;

    IF p_quantity IS NULL OR p_quantity < 0 THEN
        RAISE EXCEPTION 'Quantity must be non-negative';
    END IF;

    -- Configuration is shared through a table, not through a PL/pgSQL local.
    SELECT config_value::NUMERIC
    INTO v_tax_rate
    FROM scope_lab.application_config
    WHERE config_key = 'tax_rate';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tax rate configuration is missing';
    END IF;

    v_subtotal := p_unit_price * p_quantity;
    v_tax_amount := ROUND(v_subtotal * v_tax_rate, 2);
    v_total := v_subtotal + v_tax_amount;

    RETURN v_total;
END;
$$;

-- The function's variables disappear after each call.
SELECT scope_lab.calculate_invoice(1250.00, 3) AS invoice_total;

-- A routine demonstrates how local variables can support a transactional
-- update while the table remains the persistent source of truth.
CREATE OR REPLACE FUNCTION scope_lab.receive_stock(
    p_warehouse_id BIGINT,
    p_quantity INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_current_stock INTEGER;
    v_capacity INTEGER;
    v_new_stock INTEGER;
BEGIN
    IF p_quantity IS NULL OR p_quantity <= 0 THEN
        RAISE EXCEPTION 'Quantity must be positive';
    END IF;

    -- Lock the row to prevent concurrent updates from overshooting capacity.
    SELECT stock, capacity
    INTO v_current_stock, v_capacity
    FROM scope_lab.warehouse_stock
    WHERE warehouse_id = p_warehouse_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Warehouse % does not exist', p_warehouse_id;
    END IF;

    v_new_stock := v_current_stock + p_quantity;

    IF v_new_stock > v_capacity THEN
        RAISE EXCEPTION 'Warehouse capacity exceeded';
    END IF;

    UPDATE scope_lab.warehouse_stock
    SET stock = v_new_stock
    WHERE warehouse_id = p_warehouse_id;

    INSERT INTO scope_lab.inventory_audit
        (warehouse_id, operation, quantity, stock_after)
    VALUES
        (p_warehouse_id, 'RECEIVE', p_quantity, v_new_stock);

    RETURN v_new_stock;
END;
$$;

-- Run the successful update in a transaction.
BEGIN;
SELECT scope_lab.receive_stock(1, 25) AS stock_after_receipt;
COMMIT;

-- Each query has its own aliases and intermediate expressions; they do not
-- create persistent variables.
SELECT
    warehouse_name,
    stock,
    capacity,
    capacity - stock AS remaining_capacity
FROM scope_lab.warehouse_stock
ORDER BY warehouse_name;

SELECT
    w.warehouse_name,
    COUNT(a.audit_id) AS operation_count,
    COALESCE(SUM(a.quantity), 0) AS total_units_moved
FROM scope_lab.warehouse_stock AS w
LEFT JOIN scope_lab.inventory_audit AS a
    ON a.warehouse_id = w.warehouse_id
GROUP BY w.warehouse_id, w.warehouse_name
ORDER BY w.warehouse_name;

-- A failed statement raises an exception. Execute this separately if
-- testing interactively, since the client may stop at the first error.
-- SELECT scope_lab.receive_stock(1, 10000);

-- Shared configuration persists across sessions because it is stored in
-- a table. Session settings and routine-local variables are not substitutes
-- for transactionally managed business data.
SELECT config_key, config_value, updated_at
FROM scope_lab.application_config
ORDER BY config_key;
