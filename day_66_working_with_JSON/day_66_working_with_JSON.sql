-- ============================================================
-- WORKING WITH JSON IN POSTGRESQL
-- ============================================================
-- Demonstrates:
-- JSON and JSONB
-- Document validation
-- Nested property access
-- JSON operators
-- JSON aggregation
-- JSON transformation
-- JSON indexing
-- JSONPath queries
-- Relational and document integration
-- Transactions
-- Functions and triggers
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS json_lab;

SET search_path TO json_lab, public;

-- ------------------------------------------------------------
-- 1. Domain tables
-- ------------------------------------------------------------

CREATE TABLE customers (
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL
        CHECK (status IN ('active', 'inactive', 'pending')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name TEXT NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE orders (
    order_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
    order_status TEXT NOT NULL
        CHECK (order_status IN ('pending', 'completed', 'cancelled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE order_items (
    order_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(order_id)
        ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    UNIQUE (order_id, product_id)
);

-- ------------------------------------------------------------
-- 2. JSON document storage
-- ------------------------------------------------------------

CREATE TABLE json_documents (
    document_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_type TEXT NOT NULL,
    document_version INTEGER NOT NULL DEFAULT 1
        CHECK (document_version > 0),

    payload JSONB NOT NULL,

    document_status TEXT NOT NULL DEFAULT 'received'
        CHECK (
            document_status IN (
                'received',
                'validated',
                'rejected',
                'processed'
            )
        ),

    validation_errors JSONB NOT NULL DEFAULT '[]'::JSONB
        CHECK (jsonb_typeof(validation_errors) = 'array'),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_document_object
        CHECK (jsonb_typeof(payload) = 'object')
);

-- GIN supports efficient containment and JSONB existence queries.
CREATE INDEX idx_json_documents_payload
    ON json_documents USING GIN (payload jsonb_path_ops);

CREATE INDEX idx_json_documents_status
    ON json_documents (document_status, created_at DESC);

CREATE INDEX idx_orders_customer
    ON orders (customer_id, created_at DESC);

CREATE INDEX idx_order_items_order
    ON order_items (order_id);

-- ------------------------------------------------------------
-- 3. JSON document validation
-- ------------------------------------------------------------

CREATE FUNCTION validate_order_document(p_payload JSONB)
RETURNS JSONB
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    errors JSONB := '[]'::JSONB;
    item JSONB;
    item_count INTEGER := 0;
BEGIN
    IF jsonb_typeof(p_payload) <> 'object' THEN
        RETURN jsonb_build_array(
            'Document must be a JSON object'
        );
    END IF;

    IF NOT (p_payload ? 'order_id') THEN
        errors := errors || jsonb_build_array(
            'Missing order_id'
        );
    ELSIF jsonb_typeof(p_payload->'order_id') <> 'number'
       OR (p_payload->>'order_id') !~ '^[1-9][0-9]*$' THEN
        errors := errors || jsonb_build_array(
            'order_id must be a positive integer'
        );
    END IF;

    IF NOT (p_payload ? 'customer_id') THEN
        errors := errors || jsonb_build_array(
            'Missing customer_id'
        );
    ELSIF jsonb_typeof(p_payload->'customer_id') <> 'number'
       OR (p_payload->>'customer_id') !~ '^[1-9][0-9]*$' THEN
        errors := errors || jsonb_build_array(
            'customer_id must be a positive integer'
        );
    END IF;

    IF NOT (p_payload ? 'items') THEN
        errors := errors || jsonb_build_array(
            'Missing items'
        );

    ELSIF jsonb_typeof(p_payload->'items') <> 'array' THEN
        errors := errors || jsonb_build_array(
            'items must be an array'
        );

    ELSE
        item_count := jsonb_array_length(p_payload->'items');

        IF item_count = 0 THEN
            errors := errors || jsonb_build_array(
                'items cannot be empty'
            );
        END IF;

        FOR item IN
            SELECT value
            FROM jsonb_array_elements(p_payload->'items')
        LOOP
            IF jsonb_typeof(item) <> 'object' THEN
                errors := errors || jsonb_build_array(
                    'Each item must be an object'
                );
                CONTINUE;
            END IF;

            IF NOT (item ? 'product_id')
               OR jsonb_typeof(item->'product_id') <> 'number'
               OR (item->>'product_id') !~ '^[1-9][0-9]*$' THEN
                errors := errors || jsonb_build_array(
                    'Invalid product_id'
                );
            END IF;

            IF NOT (item ? 'quantity')
               OR jsonb_typeof(item->'quantity') <> 'number'
               OR (item->>'quantity') !~ '^[1-9][0-9]*$' THEN
                errors := errors || jsonb_build_array(
                    'Invalid item quantity'
                );
            END IF;

            IF NOT (item ? 'unit_price')
               OR jsonb_typeof(item->'unit_price') <> 'number'
               OR (item->>'unit_price')::NUMERIC < 0 THEN
                errors := errors || jsonb_build_array(
                    'Invalid unit price'
                );
            END IF;
        END LOOP;
    END IF;

    IF p_payload ? 'status'
       AND NOT (
           p_payload->>'status' IN (
               'pending',
               'completed',
               'cancelled'
           )
       ) THEN
        errors := errors || jsonb_build_array(
            'Invalid order status'
        );
    END IF;

    RETURN errors;
END;
$$;

-- ------------------------------------------------------------
-- 4. Automatically maintain document timestamps
-- ------------------------------------------------------------

CREATE FUNCTION update_document_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_document_timestamp
BEFORE UPDATE ON json_documents
FOR EACH ROW
EXECUTE FUNCTION update_document_timestamp();

-- ------------------------------------------------------------
-- 5. Sample relational records
-- ------------------------------------------------------------

INSERT INTO customers (full_name, email, status)
VALUES
    ('Atul Pandey', 'atul@example.com', 'active'),
    ('Ravi Sharma', 'ravi@example.com', 'active'),
    ('Neha Verma', 'neha@example.com', 'pending');

INSERT INTO products (product_name, unit_price)
VALUES
    ('Laptop', 65000.00),
    ('Mouse', 800.00),
    ('Keyboard', 1500.00);

INSERT INTO orders (customer_id, order_status)
VALUES
    (1, 'completed'),
    (1, 'pending'),
    (2, 'completed');

INSERT INTO order_items (
    order_id,
    product_id,
    quantity,
    unit_price
)
VALUES
    (1, 1, 1, 65000.00),
    (1, 2, 2, 800.00),
    (2, 3, 1, 1500.00),
    (3, 2, 1, 800.00);

-- ------------------------------------------------------------
-- 6. Store valid and invalid JSON documents
-- ------------------------------------------------------------

INSERT INTO json_documents (
    document_type,
    payload
)
VALUES
(
    'order',
    '{
        "order_id": 1001,
        "customer_id": 1,
        "status": "completed",
        "items": [
            {
                "product_id": 1,
                "quantity": 1,
                "unit_price": 65000
            },
            {
                "product_id": 2,
                "quantity": 2,
                "unit_price": 800
            }
        ],
        "metadata": {
            "source": "web",
            "currency": "INR"
        }
    }'::JSONB
),
(
    'order',
    '{
        "order_id": 1002,
        "customer_id": 2,
        "status": "pending",
        "items": [
            {
                "product_id": 3,
                "quantity": 2,
                "unit_price": 1500
            }
        ]
    }'::JSONB
),
(
    'order',
    '{
        "customer_id": 1,
        "items": [],
        "status": "unknown"
    }'::JSONB
);

-- ------------------------------------------------------------
-- 7. Validate stored documents
-- ------------------------------------------------------------

UPDATE json_documents
SET
    validation_errors = validate_order_document(payload),
    document_status = CASE
        WHEN jsonb_array_length(
            validate_order_document(payload)
        ) = 0
        THEN 'validated'
        ELSE 'rejected'
    END
WHERE document_type = 'order';

-- ------------------------------------------------------------
-- 8. JSON retrieval operators
-- ------------------------------------------------------------

-- -> returns a JSON value.
SELECT
    document_id,
    payload->'status' AS order_status
FROM json_documents;

-- ->> returns text.
SELECT
    document_id,
    payload->>'order_id' AS order_id
FROM json_documents;

-- #> accesses nested JSON values.
SELECT
    payload #> '{metadata,source}' AS source
FROM json_documents
WHERE payload ? 'metadata';

-- #>> returns nested values as text.
SELECT
    payload #>> '{metadata,currency}' AS currency
FROM json_documents
WHERE payload ? 'metadata';

-- ------------------------------------------------------------
-- 9. JSON containment and existence queries
-- ------------------------------------------------------------

SELECT document_id, payload
FROM json_documents
WHERE payload @> '{"status":"completed"}'::JSONB;

SELECT document_id
FROM json_documents
WHERE payload ? 'customer_id';

SELECT document_id
FROM json_documents
WHERE payload ?| ARRAY['metadata', 'items'];

-- ------------------------------------------------------------
-- 10. Extract JSON array elements
-- ------------------------------------------------------------

SELECT
    d.document_id,
    item->>'product_id' AS product_id,
    (item->>'quantity')::INTEGER AS quantity,
    (item->>'unit_price')::NUMERIC AS unit_price
FROM json_documents d
CROSS JOIN LATERAL
    jsonb_array_elements(d.payload->'items') AS item
WHERE d.document_status = 'validated';

-- ------------------------------------------------------------
-- 11. JSONPath queries
-- ------------------------------------------------------------

SELECT document_id, payload
FROM json_documents
WHERE jsonb_path_exists(
    payload,
    '$.items[*] ? (@.unit_price > 1000)'
);

-- ------------------------------------------------------------
-- 12. Convert relational data into JSON
-- ------------------------------------------------------------

CREATE VIEW order_json_view AS
SELECT
    o.order_id,
    o.customer_id,
    o.order_status,
    jsonb_build_object(
        'order_id', o.order_id,
        'customer_id', o.customer_id,
        'status', o.order_status,
        'created_at', o.created_at,
        'items',
        COALESCE(
            jsonb_agg(
                jsonb_build_object(
                    'product_id', oi.product_id,
                    'product_name', p.product_name,
                    'quantity', oi.quantity,
                    'unit_price', oi.unit_price,
                    'line_total', oi.quantity * oi.unit_price
                )
                ORDER BY oi.order_item_id
            ) FILTER (WHERE oi.order_item_id IS NOT NULL),
            '[]'::JSONB
        )
    ) AS order_document
FROM orders o
LEFT JOIN order_items oi
    ON oi.order_id = o.order_id
LEFT JOIN products p
    ON p.product_id = oi.product_id
GROUP BY
    o.order_id,
    o.customer_id,
    o.order_status,
    o.created_at;

SELECT *
FROM order_json_view
ORDER BY order_id;

-- ------------------------------------------------------------
-- 13. JSON reporting using CTEs
-- ------------------------------------------------------------

WITH expanded_orders AS (
    SELECT
        document_id,
        item
    FROM json_documents d
    CROSS JOIN LATERAL
        jsonb_array_elements(d.payload->'items') AS item
    WHERE d.document_status = 'validated'
),
order_totals AS (
    SELECT
        document_id,
        SUM(
            (item->>'quantity')::NUMERIC *
            (item->>'unit_price')::NUMERIC
        ) AS total_amount
    FROM expanded_orders
    GROUP BY document_id
)
SELECT
    document_id,
    total_amount,
    ROUND(total_amount * 0.18, 2) AS estimated_tax,
    ROUND(total_amount * 1.18, 2) AS estimated_total
FROM order_totals
ORDER BY document_id;

-- ------------------------------------------------------------
-- 14. JSON transformation
-- ------------------------------------------------------------

UPDATE json_documents
SET payload = jsonb_set(
    payload,
    '{metadata,source}',
    '"verified-api"'::JSONB,
    TRUE
)
WHERE document_id = 1
  AND payload ? 'metadata';

-- Remove a JSON property.
UPDATE json_documents
SET payload = payload - 'temporary_field'
WHERE document_id = 1;

-- Merge JSON objects.
UPDATE json_documents
SET payload = payload || '{"currency":"INR"}'::JSONB
WHERE document_id = 1;

-- ------------------------------------------------------------
-- 15. Processing and eligibility function
-- ------------------------------------------------------------

CREATE FUNCTION evaluate_document(p_document_id BIGINT)
RETURNS TABLE (
    id BIGINT,
    eligible BOOLEAN,
    errors JSONB,
    estimated_amount NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_payload JSONB;
    v_errors JSONB;
    v_amount NUMERIC := 0;
BEGIN
    SELECT payload
    INTO v_payload
    FROM json_documents
    WHERE document_id = p_document_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Document % does not exist', p_document_id;
    END IF;

    v_errors := validate_order_document(v_payload);

    IF jsonb_array_length(v_errors) = 0 THEN
        SELECT COALESCE(
            SUM(
                (item->>'quantity')::NUMERIC *
                (item->>'unit_price')::NUMERIC
            ),
            0
        )
        INTO v_amount
        FROM jsonb_array_elements(v_payload->'items') AS item;
    END IF;

    RETURN QUERY
    SELECT
        p_document_id,
        jsonb_array_length(v_errors) = 0,
        v_errors,
        v_amount;
END;
$$;

SELECT *
FROM evaluate_document(1);

SELECT *
FROM evaluate_document(3);

-- ------------------------------------------------------------
-- 16. Procedure for document processing
-- ------------------------------------------------------------

CREATE PROCEDURE process_document(p_document_id BIGINT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_errors JSONB;
BEGIN
    SELECT validate_order_document(payload)
    INTO v_errors
    FROM json_documents
    WHERE document_id = p_document_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Document not found';
    END IF;

    IF jsonb_array_length(v_errors) > 0 THEN
        UPDATE json_documents
        SET
            document_status = 'rejected',
            validation_errors = v_errors
        WHERE document_id = p_document_id;

        RETURN;
    END IF;

    UPDATE json_documents
    SET
        document_status = 'processed',
        validation_errors = '[]'::JSONB
    WHERE document_id = p_document_id
      AND document_status IN ('received', 'validated');
END;
$$;

-- ------------------------------------------------------------
-- 17. Transactional workflow
-- ------------------------------------------------------------

SAVEPOINT before_document_processing;

CALL process_document(1);

-- Verify the processing state.
SELECT
    document_id,
    document_status,
    validation_errors
FROM json_documents
WHERE document_id = 1;

RELEASE SAVEPOINT before_document_processing;

-- ------------------------------------------------------------
-- 18. Document status aggregation
-- ------------------------------------------------------------

SELECT
    document_status,
    COUNT(*) AS document_count,
    JSONB_AGG(
        jsonb_build_object(
            'document_id', document_id,
            'document_type', document_type,
            'created_at', created_at
        )
        ORDER BY document_id
    ) AS documents
FROM json_documents
GROUP BY document_status
ORDER BY document_status;

-- ------------------------------------------------------------
-- 19. Invalid document reporting
-- ------------------------------------------------------------

SELECT
    document_id,
    document_type,
    validation_errors
FROM json_documents
WHERE document_status = 'rejected';

-- ------------------------------------------------------------
-- 20. Relational versus JSON reporting
-- ------------------------------------------------------------

SELECT
    c.full_name,
    COUNT(DISTINCT o.order_id) AS order_count,
    COALESCE(
        SUM(oi.quantity * oi.unit_price),
        0
    ) AS relational_revenue
FROM customers c
LEFT JOIN orders o
    ON o.customer_id = c.customer_id
LEFT JOIN order_items oi
    ON oi.order_id = o.order_id
GROUP BY c.customer_id, c.full_name
ORDER BY relational_revenue DESC;

-- ------------------------------------------------------------
-- 21. JSON object inspection
-- ------------------------------------------------------------

SELECT
    document_id,
    jsonb_typeof(payload) AS root_type,
    jsonb_object_keys(payload) AS property_name
FROM json_documents
WHERE jsonb_typeof(payload) = 'object';

-- ------------------------------------------------------------
-- 22. JSON document version tracking
-- ------------------------------------------------------------

UPDATE json_documents
SET document_version = document_version + 1
WHERE document_id = 1;

SELECT
    document_id,
    document_version,
    updated_at
FROM json_documents;

COMMIT;

-- ------------------------------------------------------------
-- 23. Final verification
-- ------------------------------------------------------------

SELECT
    document_id,
    document_type,
    document_status,
    document_version,
    jsonb_array_length(validation_errors) AS error_count
FROM json_lab.json_documents
ORDER BY document_id;
