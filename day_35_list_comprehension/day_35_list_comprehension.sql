-- PostgreSQL-compatible SQL model for studying list-comprehension concepts
-- through relational projection, filtering, nested relationships, and
-- materialized query results.
--
-- SQL does not have list-comprehension syntax. SELECT projects values,
-- WHERE filters rows, and JOIN/UNNEST handle relationships that resemble
-- nested iteration.

DROP SCHEMA IF EXISTS comprehension_lab CASCADE;

CREATE SCHEMA comprehension_lab;

SET search_path TO comprehension_lab;

CREATE TABLE products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    price NUMERIC(12, 2) NOT NULL CHECK (price > 0),
    stock INTEGER NOT NULL CHECK (stock >= 0),
    category TEXT NOT NULL CHECK (btrim(category) <> ''),
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE tags (
    tag_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (btrim(name) <> '')
);

CREATE TABLE product_tags (
    product_id BIGINT NOT NULL REFERENCES products(product_id)
        ON DELETE CASCADE,
    tag_id BIGINT NOT NULL REFERENCES tags(tag_id)
        ON DELETE CASCADE,
    PRIMARY KEY (product_id, tag_id)
);

CREATE INDEX idx_products_category_stock
    ON products(category, stock)
    WHERE active = TRUE;

CREATE INDEX idx_product_tags_tag
    ON product_tags(tag_id);

INSERT INTO products (name, price, stock, category, active)
VALUES
    ('Keyboard', 79.99, 12, 'hardware', TRUE),
    ('Mouse', 29.99, 0, 'hardware', TRUE),
    ('Monitor', 249.50, 7, 'hardware', TRUE),
    ('Notebook', 8.50, 25, 'stationery', TRUE),
    ('Cable', 12.75, 18, 'hardware', TRUE),
    ('Legacy Adapter', 19.99, 6, 'hardware', FALSE);

INSERT INTO tags (name)
VALUES
    ('input'),
    ('display'),
    ('network'),
    ('office'),
    ('peripheral');

INSERT INTO product_tags (product_id, tag_id)
SELECT p.product_id, t.tag_id
FROM products AS p
JOIN tags AS t
  ON (p.name = 'Keyboard' AND t.name IN ('input', 'peripheral'))
  OR (p.name = 'Mouse' AND t.name IN ('input', 'peripheral'))
  OR (p.name = 'Monitor' AND t.name = 'display')
  OR (p.name = 'Notebook' AND t.name = 'office')
  OR (p.name = 'Cable' AND t.name = 'network');

-- Projection corresponds to the transformation part of a comprehension.
SELECT
    product_id,
    name,
    price,
    price * stock AS inventory_value
FROM products
ORDER BY product_id;

-- WHERE corresponds to filtering the source collection before projection.
SELECT
    name,
    price
FROM products
WHERE active
  AND stock > 0
  AND category = 'hardware'
ORDER BY price DESC;

-- Transformation plus filtering can be expressed directly in one query.
SELECT
    name,
    ROUND(price * stock, 2) AS inventory_value
FROM products
WHERE active
  AND stock > 0
  AND price >= 50
ORDER BY inventory_value DESC;

-- Conditional projection is SQL's CASE expression.
SELECT
    name,
    stock,
    CASE
        WHEN stock = 0 THEN 'out-of-stock'
        WHEN stock < 10 THEN 'low-stock'
        ELSE 'available'
    END AS stock_status
FROM products
ORDER BY product_id;

-- A relational equivalent of nested iteration uses JOIN.
SELECT
    p.name AS product,
    t.name AS tag
FROM products AS p
JOIN product_tags AS pt
  ON pt.product_id = p.product_id
JOIN tags AS t
  ON t.tag_id = pt.tag_id
ORDER BY p.name, t.name;

-- Aggregate transformed values by category.
SELECT
    category,
    COUNT(*) AS product_count,
    SUM(stock) AS total_units,
    ROUND(SUM(price * stock), 2) AS inventory_value
FROM products
WHERE active
GROUP BY category
ORDER BY category;

-- A CTE separates the filtering stage from the projection stage.
WITH eligible_products AS (
    SELECT
        product_id,
        name,
        price,
        stock
    FROM products
    WHERE active
      AND stock > 0
)
SELECT
    product_id,
    name,
    ROUND(price * stock, 2) AS inventory_value
FROM eligible_products
ORDER BY inventory_value DESC;

-- PostgreSQL arrays can be expanded with UNNEST when a single row contains
-- a collection. Each element becomes a relational row.
WITH source AS (
    SELECT ARRAY[1, 2, 3, 4, 5, 6]::INTEGER[] AS values
)
SELECT
    value,
    value * value AS square
FROM source
CROSS JOIN LATERAL unnest(values) AS expanded(value)
WHERE value % 2 = 0
ORDER BY value;

-- The following query demonstrates a transformed array result rather than
-- creating one row per output value.
WITH source AS (
    SELECT ARRAY[1, 2, 3, 4, 5, 6]::INTEGER[] AS values
)
SELECT
    ARRAY(
        SELECT value * value
        FROM unnest(values) AS expanded(value)
        WHERE value % 2 = 0
        ORDER BY value
    ) AS even_squares
FROM source;

-- JSON arrays provide another realistic nested-data case.
WITH source AS (
    SELECT
        '[
            {"name":"Alice","active":true,"score":91},
            {"name":"Bob","active":false,"score":42},
            {"name":"Carol","active":true,"score":77}
        ]'::jsonb AS records
)
SELECT
    record ->> 'name' AS name,
    (record ->> 'score')::INTEGER AS score
FROM source
CROSS JOIN LATERAL jsonb_array_elements(records) AS expanded(record)
WHERE (record ->> 'active')::BOOLEAN
  AND (record ->> 'score')::INTEGER >= 50
ORDER BY score DESC;

-- Database constraints reject invalid values instead of relying solely on
-- application-side validation.
DO $$
BEGIN
    BEGIN
        INSERT INTO products (name, price, stock, category)
        VALUES ('Invalid Product', -5.00, 4, 'hardware');
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Rejected invalid product price as expected';
    END;
END;
$$;

-- Transactional processing ensures a group of related changes either all
-- succeeds or none of it is committed.
BEGIN;

INSERT INTO products (name, price, stock, category)
VALUES ('Transaction Test Cable', 14.50, 20, 'hardware');

SAVEPOINT before_invalid_update;

UPDATE products
SET stock = -1
WHERE name = 'Transaction Test Cable';

-- The CHECK constraint causes the update to fail, so a real client would
-- roll back to the savepoint or abort the transaction. This script instead
-- demonstrates the intended safe transaction boundary with a valid update.
ROLLBACK TO SAVEPOINT before_invalid_update;

UPDATE products
SET stock = 21
WHERE name = 'Transaction Test Cable';

COMMIT;

-- A view provides a reusable relational projection for consumers that need
-- the same comprehension-like filtering and transformation repeatedly.
CREATE OR REPLACE VIEW available_hardware_inventory AS
SELECT
    product_id,
    name,
    price,
    stock,
    ROUND(price * stock, 2) AS inventory_value
FROM products
WHERE active
  AND stock > 0
  AND category = 'hardware';

SELECT *
FROM available_hardware_inventory
ORDER BY inventory_value DESC;

-- Explain verifies whether the filtering index can support the workload.
EXPLAIN
SELECT
    name,
    price
FROM products
WHERE active
  AND category = 'hardware'
  AND stock > 0;
