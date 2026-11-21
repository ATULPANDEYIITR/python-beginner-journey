-- ============================================================
-- CLASS METHODS: POSTGRESQL CLASS-LEVEL OPERATIONS
-- ============================================================
--
-- PostgreSQL does not implement object-oriented class methods
-- in the same way as Python, Java, or C++.
--
-- Database functions and procedures provide corresponding
-- class-level operations over relational entities.
--
-- This implementation models:
--   Product catalog
--   Product categories
--   Class-level configuration
--   Alternative construction
--   Shared registry operations
--   Aggregation
--   State transitions
--   Audit records
--   Validation
--   Transaction handling
--
-- PostgreSQL 15+
-- ============================================================

BEGIN;

DROP SCHEMA IF EXISTS class_methods_demo CASCADE;

CREATE SCHEMA class_methods_demo;

SET search_path TO class_methods_demo, public;

-- ============================================================
-- 1. DOMAIN TYPES
-- ============================================================

CREATE TYPE product_status AS ENUM (
    'ACTIVE',
    'DISCONTINUED'
);

CREATE TYPE product_category AS ENUM (
    'ELECTRONICS',
    'SOFTWARE',
    'FURNITURE'
);

-- ============================================================
-- 2. CLASS-LEVEL CONFIGURATION
-- ============================================================

CREATE TABLE catalog_configuration (
    configuration_id SMALLINT PRIMARY KEY
        CHECK (configuration_id = 1),

    minimum_price NUMERIC(12, 2) NOT NULL
        CHECK (minimum_price > 0),

    currency_code CHAR(3) NOT NULL DEFAULT 'INR',

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT single_configuration
        UNIQUE (configuration_id)
);

INSERT INTO catalog_configuration (
    configuration_id,
    minimum_price,
    currency_code
)
VALUES (1, 500.00, 'INR');

-- ============================================================
-- 3. PRODUCT REGISTRY
-- ============================================================

CREATE TABLE products (
    product_id VARCHAR(30) PRIMARY KEY,

    product_name VARCHAR(150) NOT NULL
        CHECK (length(trim(product_name)) > 0),

    category product_category NOT NULL,

    price NUMERIC(12, 2) NOT NULL
        CHECK (price > 0),

    status product_status NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_category_status
    ON products(category, status);

CREATE INDEX idx_products_created_at
    ON products(created_at DESC);

CREATE INDEX idx_products_active_price
    ON products(price)
    WHERE status = 'ACTIVE';

-- ============================================================
-- 4. SPECIALIZED PRODUCT INFORMATION
-- ============================================================

CREATE TABLE subscription_products (
    product_id VARCHAR(30) PRIMARY KEY
        REFERENCES products(product_id)
        ON DELETE CASCADE,

    duration_months INTEGER NOT NULL
        CHECK (duration_months BETWEEN 1 AND 60)
);

-- ============================================================
-- 5. AUDIT REGISTRY
-- ============================================================

CREATE TABLE product_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    product_id VARCHAR(30) NOT NULL,

    operation VARCHAR(30) NOT NULL,

    previous_state JSONB,

    current_state JSONB,

    performed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    performed_by TEXT NOT NULL DEFAULT current_user
);

CREATE INDEX idx_product_audit_product_time
    ON product_audit(product_id, performed_at DESC);

-- ============================================================
-- 6. VALIDATION FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_product_price()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    configured_minimum NUMERIC(12, 2);
BEGIN
    SELECT minimum_price
    INTO configured_minimum
    FROM catalog_configuration
    WHERE configuration_id = 1;

    IF configured_minimum IS NULL THEN
        RAISE EXCEPTION
            'Catalog configuration does not exist.';
    END IF;

    IF NEW.price < configured_minimum THEN
        RAISE EXCEPTION
            'Price % is below the configured minimum %.',
            NEW.price,
            configured_minimum;
    END IF;

    NEW.updated_at = CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_product_price
BEFORE INSERT OR UPDATE OF price
ON products
FOR EACH ROW
EXECUTE FUNCTION validate_product_price();

-- ============================================================
-- 7. AUDIT TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION audit_product_changes()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN

        INSERT INTO product_audit (
            product_id,
            operation,
            current_state
        )
        VALUES (
            NEW.product_id,
            'CREATE',
            to_jsonb(NEW)
        );

        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN

        INSERT INTO product_audit (
            product_id,
            operation,
            previous_state,
            current_state
        )
        VALUES (
            NEW.product_id,
            'UPDATE',
            to_jsonb(OLD),
            to_jsonb(NEW)
        );

        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN

        INSERT INTO product_audit (
            product_id,
            operation,
            previous_state
        )
        VALUES (
            OLD.product_id,
            'DELETE',
            to_jsonb(OLD)
        );

        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$;

CREATE TRIGGER trg_product_audit
AFTER INSERT OR UPDATE OR DELETE
ON products
FOR EACH ROW
EXECUTE FUNCTION audit_product_changes();

-- ============================================================
-- 8. CLASS-LEVEL FACTORY FUNCTION
-- ============================================================
--
-- Equivalent to a static factory method.
-- The function creates and returns a database entity.
-- The transaction guarantees atomic insertion.

CREATE OR REPLACE FUNCTION create_product(
    p_id VARCHAR(30),
    p_name VARCHAR(150),
    p_category product_category,
    p_price NUMERIC(12, 2)
)
RETURNS products
LANGUAGE plpgsql
AS $$
DECLARE
    created_product products%ROWTYPE;
BEGIN
    IF p_id IS NULL OR length(trim(p_id)) = 0 THEN
        RAISE EXCEPTION 'Product ID is required.';
    END IF;

    IF p_name IS NULL OR length(trim(p_name)) = 0 THEN
        RAISE EXCEPTION 'Product name is required.';
    END IF;

    IF p_price IS NULL OR p_price <= 0 THEN
        RAISE EXCEPTION 'Price must be positive.';
    END IF;

    INSERT INTO products (
        product_id,
        product_name,
        category,
        price
    )
    VALUES (
        trim(p_id),
        trim(p_name),
        p_category,
        p_price
    )
    RETURNING * INTO created_product;

    RETURN created_product;
END;
$$;

-- ============================================================
-- 9. ALTERNATIVE CONSTRUCTOR FUNCTION
-- ============================================================
--
-- Accepts JSON input rather than individual arguments.

CREATE OR REPLACE FUNCTION create_product_from_json(
    p_data JSONB
)
RETURNS products
LANGUAGE plpgsql
AS $$
DECLARE
    result products%ROWTYPE;
BEGIN
    IF p_data IS NULL OR jsonb_typeof(p_data) <> 'object' THEN
        RAISE EXCEPTION 'Expected a JSON object.';
    END IF;

    IF NOT (
        p_data ?& ARRAY[
            'id',
            'name',
            'category',
            'price'
        ]
    ) THEN
        RAISE EXCEPTION 'Required JSON properties are missing.';
    END IF;

    result := create_product(
        p_data ->> 'id',
        p_data ->> 'name',
        (p_data ->> 'category')::product_category,
        (p_data ->> 'price')::NUMERIC
    );

    RETURN result;
END;
$$;

-- ============================================================
-- 10. CLASS-LEVEL REGISTRY LOOKUP
-- ============================================================

CREATE OR REPLACE FUNCTION find_product(
    p_id VARCHAR(30)
)
RETURNS SETOF products
LANGUAGE SQL
STABLE
AS $$
    SELECT *
    FROM products
    WHERE product_id = p_id;
$$;

-- ============================================================
-- 11. CLASS-LEVEL AGGREGATION
-- ============================================================

CREATE OR REPLACE FUNCTION get_catalog_statistics()
RETURNS TABLE (
    category product_category,
    product_count BIGINT,
    total_value NUMERIC,
    average_price NUMERIC
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        p.category,
        COUNT(*) AS product_count,
        SUM(p.price) AS total_value,
        ROUND(AVG(p.price), 2) AS average_price
    FROM products p
    WHERE p.status = 'ACTIVE'
    GROUP BY p.category;
$$;

-- ============================================================
-- 12. CLASS-LEVEL CONFIGURATION UPDATE
-- ============================================================

CREATE OR REPLACE PROCEDURE update_minimum_price(
    p_amount NUMERIC(12, 2)
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_amount IS NULL OR p_amount <= 0 THEN
        RAISE EXCEPTION 'Minimum price must be positive.';
    END IF;

    UPDATE catalog_configuration
    SET
        minimum_price = p_amount,
        updated_at = CURRENT_TIMESTAMP
    WHERE configuration_id = 1;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Configuration record is missing.';
    END IF;
END;
$$;

-- ============================================================
-- 13. INSTANCE-LIKE PRODUCT OPERATION
-- ============================================================

CREATE OR REPLACE FUNCTION apply_product_discount(
    p_id VARCHAR(30),
    p_percentage NUMERIC
)
RETURNS products
LANGUAGE plpgsql
AS $$
DECLARE
    result products%ROWTYPE;
BEGIN
    IF p_percentage IS NULL OR
       p_percentage < 0 OR
       p_percentage > 50 THEN

        RAISE EXCEPTION
            'Discount must be between 0 and 50.';
    END IF;

    UPDATE products
    SET price = ROUND(
        price * (1 - p_percentage / 100),
        2
    )
    WHERE product_id = p_id
      AND status = 'ACTIVE'
    RETURNING * INTO result;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Product does not exist or is not active: %',
            p_id;
    END IF;

    RETURN result;
END;
$$;

-- ============================================================
-- 14. STATE TRANSITION
-- ============================================================

CREATE OR REPLACE FUNCTION discontinue_product(
    p_id VARCHAR(30)
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    affected_rows INTEGER;
BEGIN
    UPDATE products
    SET status = 'DISCONTINUED'
    WHERE product_id = p_id
      AND status = 'ACTIVE';

    GET DIAGNOSTICS affected_rows = ROW_COUNT;

    RETURN affected_rows = 1;
END;
$$;

-- ============================================================
-- 15. VIEWS
-- ============================================================

CREATE OR REPLACE VIEW active_product_catalog AS
SELECT
    product_id,
    product_name,
    category,
    price,
    created_at
FROM products
WHERE status = 'ACTIVE';

CREATE OR REPLACE VIEW product_audit_history AS
SELECT
    audit_id,
    product_id,
    operation,
    previous_state,
    current_state,
    performed_at,
    performed_by
FROM product_audit;

-- ============================================================
-- 16. SAMPLE DATA
-- ============================================================

SELECT create_product(
    'P101',
    'Business Laptop',
    'ELECTRONICS',
    75000
);

SELECT create_product(
    'P102',
    'Office Chair',
    'FURNITURE',
    12500
);

SELECT create_product_from_json(
    '{
        "id": "P103",
        "name": "Security Platform",
        "category": "SOFTWARE",
        "price": 25000
    }'::JSONB
);

SELECT create_product(
    'P104',
    'Network Switch',
    'ELECTRONICS',
    18000
);

INSERT INTO subscription_products (
    product_id,
    duration_months
)
VALUES ('P103', 12);

-- ============================================================
-- 17. RETRIEVAL
-- ============================================================

SELECT *
FROM find_product('P101');

SELECT *
FROM active_product_catalog
ORDER BY price DESC;

-- ============================================================
-- 18. VALIDATION
-- ============================================================

DO $$
BEGIN
    BEGIN
        PERFORM create_product(
            'P105',
            'Invalid Product',
            'ELECTRONICS',
            -500
        );
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Validation rejected invalid product: %',
            SQLERRM;
    END;

    BEGIN
        PERFORM create_product(
            'P106',
            'Below Minimum',
            'FURNITURE',
            100
        );
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Minimum price rejected: %', SQLERRM;
    END;
END;
$$;

-- ============================================================
-- 19. CLASS-LEVEL REPORTING
-- ============================================================

SELECT *
FROM get_catalog_statistics()
ORDER BY category;

-- ============================================================
-- 20. WINDOW-BASED ANALYTICS
-- ============================================================

WITH ranked_products AS (
    SELECT
        product_id,
        product_name,
        category,
        price,
        RANK() OVER (
            PARTITION BY category
            ORDER BY price DESC
        ) AS category_rank
    FROM products
    WHERE status = 'ACTIVE'
)
SELECT *
FROM ranked_products
ORDER BY category, category_rank;

-- ============================================================
-- 21. TRANSACTIONAL BUSINESS OPERATIONS
-- ============================================================

SAVEPOINT before_discount;

SELECT (
    apply_product_discount('P101', 10)
).*;

-- Demonstration of transaction recovery.
ROLLBACK TO SAVEPOINT before_discount;

-- Apply the final approved discount.
SELECT (
    apply_product_discount('P101', 5)
).*;

-- ============================================================
-- 22. STATE TRANSITION
-- ============================================================

SELECT discontinue_product('P102') AS discontinued;

-- ============================================================
-- 23. AUDIT REPORT
-- ============================================================

SELECT
    product_id,
    operation,
    performed_at,
    performed_by
FROM product_audit
ORDER BY audit_id;

-- ============================================================
-- 24. REGISTRY STATISTICS
-- ============================================================

SELECT
    COUNT(*) AS registered_products,
    COUNT(*) FILTER (
        WHERE status = 'ACTIVE'
    ) AS active_products,
    COUNT(*) FILTER (
        WHERE status = 'DISCONTINUED'
    ) AS discontinued_products,
    SUM(price) FILTER (
        WHERE status = 'ACTIVE'
    ) AS active_inventory_value
FROM products;

-- ============================================================
-- 25. ELIGIBILITY DETERMINATION
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    p.status,
    p.price,
    c.minimum_price,
    (
        p.status = 'ACTIVE'
        AND p.price >= c.minimum_price
    ) AS eligible_for_sale
FROM products p
CROSS JOIN catalog_configuration c;

-- ============================================================
-- 26. CTE-BASED OPERATIONAL REPORT
-- ============================================================

WITH category_totals AS (
    SELECT
        category,
        COUNT(*) AS total_products,
        SUM(price) AS category_value
    FROM products
    GROUP BY category
),
catalog_total AS (
    SELECT SUM(price) AS total_value
    FROM products
    WHERE status = 'ACTIVE'
)
SELECT
    ct.category,
    ct.total_products,
    ct.category_value,
    ROUND(
        100.0 * ct.category_value /
        NULLIF(c.total_value, 0),
        2
    ) AS percentage_of_catalog_value
FROM category_totals ct
CROSS JOIN catalog_total c
ORDER BY ct.category;

-- ============================================================
-- 27. FINAL STATE
-- ============================================================

SELECT
    product_id,
    product_name,
    category,
    price,
    status,
    created_at,
    updated_at
FROM products
ORDER BY product_id;

COMMIT;
