-- PostgreSQL 14+
-- Demonstrates function parameters, function arguments, overloads,
-- defaults, named notation, variadic functions, INOUT parameters,
-- validation, and transaction-safe business calculations.

BEGIN;

DROP SCHEMA IF EXISTS parameter_lab CASCADE;
CREATE SCHEMA parameter_lab;
SET search_path TO parameter_lab, public;

CREATE TABLE pricing_policy (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    policy_name TEXT NOT NULL UNIQUE,
    tax_rate NUMERIC(7, 6) NOT NULL CHECK (tax_rate BETWEEN 0 AND 1),
    maximum_discount NUMERIC(7, 6) NOT NULL
        CHECK (maximum_discount BETWEEN 0 AND 1),
    shipping_rate NUMERIC(7, 6) NOT NULL CHECK (shipping_rate >= 0)
);

CREATE TABLE purchase_order (
    order_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_reference TEXT NOT NULL UNIQUE,
    policy_id BIGINT NOT NULL REFERENCES pricing_policy(policy_id),
    discount_rate NUMERIC(7, 6) NOT NULL DEFAULT 0
        CHECK (discount_rate BETWEEN 0 AND 1),
    shipping_override NUMERIC(12, 2)
        CHECK (shipping_override IS NULL OR shipping_override >= 0),
    status TEXT NOT NULL DEFAULT 'DRAFT'
        CHECK (status IN ('DRAFT', 'VALIDATED', 'REJECTED', 'PRICED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE purchase_line (
    line_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES purchase_order(order_id)
        ON DELETE CASCADE,
    item_code TEXT NOT NULL,
    description TEXT NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    UNIQUE (order_id, item_code)
);

CREATE TABLE pricing_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES purchase_order(order_id),
    event_name TEXT NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX purchase_line_order_idx ON purchase_line(order_id);
CREATE INDEX purchase_order_status_created_idx
    ON purchase_order(status, created_at DESC);

INSERT INTO pricing_policy (
    policy_name, tax_rate, maximum_discount, shipping_rate
) VALUES
    ('Domestic equipment', 0.180000, 0.150000, 0.025000),
    ('Export equipment', 0.120000, 0.100000, 0.040000);

INSERT INTO purchase_order (
    order_reference, policy_id, discount_rate, shipping_override
)
SELECT 'PO-IND-1001', policy_id, 0.100000, NULL
FROM pricing_policy
WHERE policy_name = 'Domestic equipment';

INSERT INTO purchase_order (
    order_reference, policy_id, discount_rate, shipping_override
)
SELECT 'PO-IND-1002', policy_id, 0.000000, 250.00
FROM pricing_policy
WHERE policy_name = 'Domestic equipment';

INSERT INTO purchase_line (
    order_id, item_code, description, unit_price, quantity
)
SELECT o.order_id, data.item_code, data.description,
       data.unit_price, data.quantity
FROM purchase_order AS o
CROSS JOIN (
    VALUES
        ('SNS-100', 'Industrial sensor', 2450.00::numeric, 4),
        ('CAL-200', 'Calibration kit', 1800.00::numeric, 2),
        ('CBL-300', 'Shielded cable', 350.00::numeric, 10)
) AS data(item_code, description, unit_price, quantity)
WHERE o.order_reference = 'PO-IND-1001';

INSERT INTO purchase_line (
    order_id, item_code, description, unit_price, quantity
)
SELECT o.order_id, 'PMP-400', 'Hydraulic pump', 12500.00, 2
FROM purchase_order AS o
WHERE o.order_reference = 'PO-IND-1002';

-- IN parameters receive argument values. Defaults permit callers to omit
-- trailing arguments, while validation rejects unsupported discount rates.
CREATE FUNCTION calculate_line_total(
    p_unit_price NUMERIC,
    p_quantity INTEGER DEFAULT 1
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_unit_price < 0 THEN
        RAISE EXCEPTION 'Unit price cannot be negative';
    END IF;

    IF p_quantity < 0 THEN
        RAISE EXCEPTION 'Quantity cannot be negative';
    END IF;

    RETURN ROUND(p_unit_price * p_quantity, 2);
END;
$$;

-- PostgreSQL resolves overloads using argument types and function signatures.
-- The second function accepts three required arguments and one optional
-- argument; it is deliberately distinct from the two-argument function.
CREATE FUNCTION calculate_line_total(
    p_unit_price NUMERIC,
    p_quantity INTEGER,
    p_discount_rate NUMERIC,
    p_tax_rate NUMERIC DEFAULT 0
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_unit_price < 0 OR p_quantity < 0 THEN
        RAISE EXCEPTION 'Price and quantity must be non-negative';
    END IF;

    IF p_discount_rate < 0 OR p_discount_rate > 1 THEN
        RAISE EXCEPTION 'Discount must be between zero and one';
    END IF;

    IF p_tax_rate < 0 OR p_tax_rate > 1 THEN
        RAISE EXCEPTION 'Tax rate must be between zero and one';
    END IF;

    RETURN ROUND(
        p_unit_price * p_quantity * (1 - p_discount_rate) * (1 + p_tax_rate),
        2
    );
END;
$$;

-- VARIADIC NUMERIC[] receives any number of trailing numeric arguments.
-- An empty variadic array is rejected to avoid a meaningless average.
CREATE FUNCTION average_amounts(VARIADIC p_amounts NUMERIC[])
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_count INTEGER;
    v_total NUMERIC := 0;
    v_amount NUMERIC;
BEGIN
    v_count := COALESCE(array_length(p_amounts, 1), 0);

    IF v_count = 0 THEN
        RAISE EXCEPTION 'At least one amount is required';
    END IF;

    FOREACH v_amount IN ARRAY p_amounts LOOP
        IF v_amount IS NULL THEN
            RAISE EXCEPTION 'Amounts cannot contain NULL';
        END IF;
        v_total := v_total + v_amount;
    END LOOP;

    RETURN v_total / v_count;
END;
$$;

-- INOUT parameters both receive an input and return an updated value.
CREATE PROCEDURE normalize_reference(
    INOUT p_reference TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_reference IS NULL OR BTRIM(p_reference) = '' THEN
        RAISE EXCEPTION 'Reference must not be blank';
    END IF;

    p_reference := UPPER(REGEXP_REPLACE(BTRIM(p_reference), '\s+', '-', 'g'));
END;
$$;

-- Named notation makes calls with optional settings unambiguous.
-- The function returns a detailed pricing record and does not mutate data.
CREATE FUNCTION price_order(
    p_order_id BIGINT,
    p_discount_override NUMERIC DEFAULT NULL,
    p_shipping_override NUMERIC DEFAULT NULL
)
RETURNS TABLE (
    order_reference TEXT,
    subtotal NUMERIC,
    discount NUMERIC,
    taxable_amount NUMERIC,
    tax NUMERIC,
    shipping NUMERIC,
    total NUMERIC
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_policy pricing_policy%ROWTYPE;
    v_order purchase_order%ROWTYPE;
    v_subtotal NUMERIC;
    v_discount_rate NUMERIC;
    v_shipping NUMERIC;
    v_discount NUMERIC;
    v_taxable NUMERIC;
    v_tax NUMERIC;
BEGIN
    SELECT * INTO v_order
    FROM purchase_order
    WHERE order_id = p_order_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Purchase order % does not exist', p_order_id;
    END IF;

    SELECT * INTO v_policy
    FROM pricing_policy
    WHERE policy_id = v_order.policy_id;

    SELECT COALESCE(SUM(calculate_line_total(unit_price, quantity)), 0)
    INTO v_subtotal
    FROM purchase_line
    WHERE order_id = p_order_id;

    IF v_subtotal <= 0 THEN
        RAISE EXCEPTION 'Purchase order % has no positive subtotal', p_order_id;
    END IF;

    v_discount_rate := COALESCE(
        p_discount_override,
        v_order.discount_rate
    );

    IF v_discount_rate < 0 OR
       v_discount_rate > v_policy.maximum_discount THEN
        RAISE EXCEPTION
            'Discount % exceeds policy maximum %',
            v_discount_rate,
            v_policy.maximum_discount;
    END IF;

    IF p_shipping_override IS NOT NULL AND p_shipping_override < 0 THEN
        RAISE EXCEPTION 'Shipping override cannot be negative';
    END IF;

    v_discount := ROUND(v_subtotal * v_discount_rate, 2);
    v_taxable := v_subtotal - v_discount;
    v_tax := ROUND(v_taxable * v_policy.tax_rate, 2);

    v_shipping := COALESCE(
        p_shipping_override,
        v_order.shipping_override,
        ROUND(v_taxable * v_policy.shipping_rate, 2)
    );

    order_reference := v_order.order_reference;
    subtotal := v_subtotal;
    discount := v_discount;
    taxable_amount := v_taxable;
    tax := v_tax;
    shipping := v_shipping;
    total := v_taxable + v_tax + v_shipping;

    RETURN NEXT;
END;
$$;

-- A trigger centralizes the rule that a line cannot be edited on a priced
-- order. The trigger uses NEW and OLD records rather than caller parameters.
CREATE FUNCTION guard_priced_order_lines()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_order_id BIGINT;
    v_status TEXT;
BEGIN
    v_order_id := COALESCE(NEW.order_id, OLD.order_id);

    SELECT status INTO v_status
    FROM purchase_order
    WHERE order_id = v_order_id
    FOR UPDATE;

    IF v_status = 'PRICED' THEN
        RAISE EXCEPTION 'Cannot change lines for a priced order';
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$;

CREATE TRIGGER purchase_line_priced_guard
BEFORE INSERT OR UPDATE OR DELETE ON purchase_line
FOR EACH ROW EXECUTE FUNCTION guard_priced_order_lines();

-- Named argument notation identifies values by parameter name instead of
-- relying on positional order.
SELECT calculate_line_total(
    p_unit_price => 2450.00,
    p_quantity => 4
) AS named_argument_total;

SELECT calculate_line_total(100.00) AS default_quantity_total;

SELECT calculate_line_total(
    p_unit_price => 100.00,
    p_quantity => 3,
    p_discount_rate => 0.10,
    p_tax_rate => 0.18
) AS discounted_taxed_total;

SELECT average_amounts(10.00, 20.00, 30.00, 40.00) AS average_amount;

CALL normalize_reference('  po ind 1009  ');

-- The derived line total is computed using a function argument supplied by
-- each row; the function itself does not need to know the table structure.
SELECT
    o.order_reference,
    l.item_code,
    l.quantity,
    l.unit_price,
    calculate_line_total(l.unit_price, l.quantity) AS line_total
FROM purchase_order AS o
JOIN purchase_line AS l USING (order_id)
ORDER BY o.order_reference, l.item_code;

-- A function's default values do not replace explicit NULL values unless
-- COALESCE is used in its implementation.
SELECT *
FROM price_order(
    p_order_id => (
        SELECT order_id FROM purchase_order
        WHERE order_reference = 'PO-IND-1001'
    ),
    p_discount_override => NULL,
    p_shipping_override => NULL
);

-- Demonstrate validation and transactional state changes. The exception
-- block rolls back its subtransaction without stopping the entire script.
DO $$
DECLARE
    v_order_id BIGINT;
    v_total NUMERIC;
BEGIN
    SELECT order_id INTO v_order_id
    FROM purchase_order
    WHERE order_reference = 'PO-IND-1001';

    SELECT p.total INTO v_total
    FROM price_order(v_order_id, 0.10, NULL) AS p;

    UPDATE purchase_order
    SET status = 'PRICED'
    WHERE order_id = v_order_id;

    INSERT INTO pricing_audit(order_id, event_name, details)
    VALUES (
        v_order_id,
        'ORDER_PRICED',
        jsonb_build_object('total', v_total, 'currency', 'INR')
    );

    RAISE NOTICE 'Order priced at %', v_total;
END;
$$;

DO $$
DECLARE
    v_order_id BIGINT;
BEGIN
    SELECT order_id INTO v_order_id
    FROM purchase_order
    WHERE order_reference = 'PO-IND-1001';

    BEGIN
        INSERT INTO purchase_line(
            order_id, item_code, description, unit_price, quantity
        ) VALUES (
            v_order_id, 'LATE-ITEM', 'Late change', 100.00, 1
        );
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Expected line guard: %', SQLERRM;
    END;
END;
$$;

-- The order summary joins normalized entities rather than storing duplicate
-- totals that could become inconsistent with their underlying line items.
CREATE VIEW order_line_summary AS
SELECT
    o.order_reference,
    o.status,
    COUNT(l.line_id) AS line_count,
    COALESCE(SUM(calculate_line_total(l.unit_price, l.quantity)), 0)
        AS subtotal
FROM purchase_order AS o
LEFT JOIN purchase_line AS l USING (order_id)
GROUP BY o.order_id, o.order_reference, o.status;

SELECT * FROM order_line_summary ORDER BY order_reference;

SELECT
    a.event_name,
    a.details,
    a.recorded_at
FROM pricing_audit AS a
ORDER BY a.recorded_at DESC;

-- Invalid calls are caught in an exception block so the complete script
-- remains executable while still demonstrating argument validation.
DO $$
BEGIN
    BEGIN
        PERFORM calculate_line_total(-1.00, 2);
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Invalid price rejected: %', SQLERRM;
    END;

    BEGIN
        PERFORM average_amounts(VARIADIC ARRAY[]::NUMERIC[]);
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Empty variadic arguments rejected: %', SQLERRM;
    END;

    BEGIN
        PERFORM price_order(
            p_order_id => -999,
            p_discount_override => 0.05,
            p_shipping_override => NULL
        );
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Invalid order argument rejected: %', SQLERRM;
    END;
END;
$$;

COMMIT;
