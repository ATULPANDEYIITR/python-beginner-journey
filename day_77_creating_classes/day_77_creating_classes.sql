-- ============================================================
-- CLASS CREATION AND OBJECT MODELING
-- PostgreSQL 15+
--
-- Relational representation of:
--   Class definitions
--   Inheritance
--   Attributes
--   Methods
--   Object instances
--   Attribute values
--   Object validation
--   Class-level constraints
--   Audit history
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS class_lab;

SET search_path TO class_lab, public;

-- ------------------------------------------------------------
-- 1. Enumerated domain types
-- ------------------------------------------------------------

CREATE TYPE attribute_data_type AS ENUM (
    'TEXT',
    'INTEGER',
    'DECIMAL',
    'BOOLEAN',
    'DATE'
);

CREATE TYPE instance_state AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'ARCHIVED'
);

-- ------------------------------------------------------------
-- 2. Class definitions
-- ------------------------------------------------------------

CREATE TABLE class_definition (
    class_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    class_name VARCHAR(100) NOT NULL UNIQUE,

    description TEXT NOT NULL,

    parent_class_id BIGINT
        REFERENCES class_definition(class_id)
        ON DELETE RESTRICT,

    is_abstract BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_class_name
        CHECK (class_name ~ '^[A-Za-z_][A-Za-z0-9_]*$'),

    CONSTRAINT no_direct_self_inheritance
        CHECK (parent_class_id IS DISTINCT FROM class_id)
);

CREATE INDEX idx_class_parent
    ON class_definition(parent_class_id);

-- ------------------------------------------------------------
-- 3. Class attributes
-- ------------------------------------------------------------

CREATE TABLE class_attribute (
    attribute_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    class_id BIGINT NOT NULL
        REFERENCES class_definition(class_id)
        ON DELETE CASCADE,

    attribute_name VARCHAR(100) NOT NULL,

    data_type attribute_data_type NOT NULL,

    is_required BOOLEAN NOT NULL DEFAULT TRUE,

    default_value TEXT,

    is_private BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT unique_class_attribute
        UNIQUE (class_id, attribute_name),

    CONSTRAINT valid_attribute_name
        CHECK (attribute_name ~ '^[A-Za-z_][A-Za-z0-9_]*$')
);

CREATE INDEX idx_attribute_class
    ON class_attribute(class_id);

-- ------------------------------------------------------------
-- 4. Class methods
-- ------------------------------------------------------------

CREATE TABLE class_method (
    method_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    class_id BIGINT NOT NULL
        REFERENCES class_definition(class_id)
        ON DELETE CASCADE,

    method_name VARCHAR(100) NOT NULL,

    return_type VARCHAR(50) NOT NULL DEFAULT 'VOID',

    is_static BOOLEAN NOT NULL DEFAULT FALSE,

    is_abstract BOOLEAN NOT NULL DEFAULT FALSE,

    access_modifier VARCHAR(10) NOT NULL DEFAULT 'PUBLIC',

    CONSTRAINT unique_class_method
        UNIQUE (class_id, method_name),

    CONSTRAINT valid_access_modifier
        CHECK (access_modifier IN (
            'PUBLIC',
            'PRIVATE',
            'PROTECTED'
        ))
);

CREATE INDEX idx_method_class
    ON class_method(class_id);

-- ------------------------------------------------------------
-- 5. Object instances
-- ------------------------------------------------------------

CREATE TABLE object_instance (
    object_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    class_id BIGINT NOT NULL
        REFERENCES class_definition(class_id)
        ON DELETE RESTRICT,

    object_name VARCHAR(150) NOT NULL,

    state instance_state NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    created_by VARCHAR(100) NOT NULL DEFAULT CURRENT_USER,

    CONSTRAINT unique_object_name_per_class
        UNIQUE (class_id, object_name),

    CONSTRAINT nonempty_object_name
        CHECK (length(trim(object_name)) > 0)
);

CREATE INDEX idx_object_class_state
    ON object_instance(class_id, state);

-- ------------------------------------------------------------
-- 6. Object attribute values
-- ------------------------------------------------------------

CREATE TABLE object_attribute_value (
    value_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    object_id BIGINT NOT NULL
        REFERENCES object_instance(object_id)
        ON DELETE CASCADE,

    attribute_id BIGINT NOT NULL
        REFERENCES class_attribute(attribute_id)
        ON DELETE RESTRICT,

    value_text TEXT,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_object_attribute
        UNIQUE (object_id, attribute_id)
);

CREATE INDEX idx_object_attribute_lookup
    ON object_attribute_value(object_id, attribute_id);

-- ------------------------------------------------------------
-- 7. Audit log
-- ------------------------------------------------------------

CREATE TABLE object_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    object_id BIGINT
        REFERENCES object_instance(object_id)
        ON DELETE SET NULL,

    operation VARCHAR(30) NOT NULL,

    details JSONB NOT NULL DEFAULT '{}'::jsonb,

    changed_by TEXT NOT NULL DEFAULT CURRENT_USER,

    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_object_time
    ON object_audit(object_id, changed_at DESC);

-- ------------------------------------------------------------
-- 8. Inheritance cycle prevention
--
-- Prevents indirect inheritance loops such as:
-- A -> B -> C -> A.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION prevent_inheritance_cycle()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    cycle_found BOOLEAN;
BEGIN
    IF NEW.parent_class_id IS NULL THEN
        RETURN NEW;
    END IF;

    WITH RECURSIVE ancestors(class_id, parent_class_id) AS (
        SELECT class_id, parent_class_id
        FROM class_definition
        WHERE class_id = NEW.parent_class_id

        UNION

        SELECT c.class_id, c.parent_class_id
        FROM class_definition c
        JOIN ancestors a
          ON c.class_id = a.parent_class_id
    )
    SELECT EXISTS (
        SELECT 1
        FROM ancestors
        WHERE class_id = NEW.class_id
    )
    INTO cycle_found;

    IF cycle_found THEN
        RAISE EXCEPTION
            'Inheritance cycle detected for class %',
            NEW.class_name;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_inheritance_cycle
BEFORE INSERT OR UPDATE OF parent_class_id
ON class_definition
FOR EACH ROW
EXECUTE FUNCTION prevent_inheritance_cycle();

-- ------------------------------------------------------------
-- 9. Ensure attributes belong to the object's class hierarchy
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_object_attribute()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    object_class BIGINT;
    attribute_class BIGINT;
    compatible BOOLEAN;
BEGIN
    SELECT class_id
    INTO object_class
    FROM object_instance
    WHERE object_id = NEW.object_id;

    SELECT class_id
    INTO attribute_class
    FROM class_attribute
    WHERE attribute_id = NEW.attribute_id;

    IF object_class IS NULL OR attribute_class IS NULL THEN
        RAISE EXCEPTION 'Object or attribute does not exist.';
    END IF;

    WITH RECURSIVE hierarchy(class_id, parent_class_id) AS (
        SELECT class_id, parent_class_id
        FROM class_definition
        WHERE class_id = object_class

        UNION ALL

        SELECT parent.class_id, parent.parent_class_id
        FROM class_definition parent
        JOIN hierarchy child
          ON child.parent_class_id = parent.class_id
    )
    SELECT EXISTS (
        SELECT 1
        FROM hierarchy
        WHERE class_id = attribute_class
    )
    INTO compatible;

    IF NOT compatible THEN
        RAISE EXCEPTION
            'Attribute % does not belong to object class hierarchy.',
            NEW.attribute_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_object_attribute
BEFORE INSERT OR UPDATE
ON object_attribute_value
FOR EACH ROW
EXECUTE FUNCTION validate_object_attribute();

-- ------------------------------------------------------------
-- 10. Attribute type validation
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_attribute_value()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    expected_type attribute_data_type;
    required_attribute BOOLEAN;
    value_valid BOOLEAN := FALSE;
BEGIN
    SELECT data_type, is_required
    INTO expected_type, required_attribute
    FROM class_attribute
    WHERE attribute_id = NEW.attribute_id;

    IF NEW.value_text IS NULL THEN
        IF required_attribute THEN
            RAISE EXCEPTION 'Required attribute cannot be NULL.';
        END IF;

        RETURN NEW;
    END IF;

    CASE expected_type
        WHEN 'TEXT' THEN
            value_valid := TRUE;

        WHEN 'INTEGER' THEN
            value_valid := NEW.value_text ~ '^-?[0-9]+$';

        WHEN 'DECIMAL' THEN
            value_valid := NEW.value_text ~
                '^-?[0-9]+([.][0-9]+)?$';

        WHEN 'BOOLEAN' THEN
            value_valid := lower(NEW.value_text) IN (
                'true', 'false'
            );

        WHEN 'DATE' THEN
            BEGIN
                PERFORM NEW.value_text::DATE;
                value_valid := TRUE;
            EXCEPTION
                WHEN invalid_datetime_format
                    OR datetime_field_overflow THEN
                    value_valid := FALSE;
            END;
    END CASE;

    IF NOT value_valid THEN
        RAISE EXCEPTION
            'Invalid value for attribute %. Expected type: %',
            NEW.attribute_id,
            expected_type;
    END IF;

    NEW.updated_at := CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_attribute_value
BEFORE INSERT OR UPDATE
ON object_attribute_value
FOR EACH ROW
EXECUTE FUNCTION validate_attribute_value();

-- ------------------------------------------------------------
-- 11. Abstract-class and required-attribute enforcement
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_object_creation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    abstract_class BOOLEAN;
BEGIN
    SELECT is_abstract
    INTO abstract_class
    FROM class_definition
    WHERE class_id = NEW.class_id;

    IF abstract_class THEN
        RAISE EXCEPTION
            'Cannot instantiate abstract class %',
            NEW.class_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_object_creation
BEFORE INSERT
ON object_instance
FOR EACH ROW
EXECUTE FUNCTION validate_object_creation();

CREATE OR REPLACE FUNCTION check_required_attributes()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    missing_attribute TEXT;
BEGIN
    SELECT ca.attribute_name
    INTO missing_attribute
    FROM class_attribute ca
    WHERE ca.is_required = TRUE
      AND ca.default_value IS NULL
      AND ca.class_id IN (
          WITH RECURSIVE hierarchy(class_id, parent_class_id) AS (
              SELECT class_id, parent_class_id
              FROM class_definition
              WHERE class_id = NEW.class_id

              UNION ALL

              SELECT parent.class_id, parent.parent_class_id
              FROM class_definition parent
              JOIN hierarchy child
                ON child.parent_class_id = parent.class_id
          )
          SELECT class_id FROM hierarchy
      )
      AND NOT EXISTS (
          SELECT 1
          FROM object_attribute_value v
          WHERE v.object_id = NEW.object_id
            AND v.attribute_id = ca.attribute_id
      )
    LIMIT 1;

    IF missing_attribute IS NOT NULL THEN
        RAISE EXCEPTION
            'Required attribute % has not been assigned.',
            missing_attribute;
    END IF;

    RETURN NULL;
END;
$$;

CREATE CONSTRAINT TRIGGER trg_check_required_attributes
AFTER INSERT
ON object_attribute_value
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION check_required_attributes();

-- ------------------------------------------------------------
-- 12. Object creation procedure
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE create_object(
    p_class_name VARCHAR,
    p_object_name VARCHAR,
    p_attributes JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    selected_class_id BIGINT;
    attribute_record RECORD;
    attribute_value TEXT;
    inserted_object_id BIGINT;
BEGIN
    IF p_attributes IS NULL OR jsonb_typeof(p_attributes) <> 'object' THEN
        RAISE EXCEPTION 'Attributes must be a JSON object.';
    END IF;

    SELECT class_id
    INTO selected_class_id
    FROM class_definition
    WHERE class_name = p_class_name;

    IF selected_class_id IS NULL THEN
        RAISE EXCEPTION 'Class % does not exist.', p_class_name;
    END IF;

    INSERT INTO object_instance(
        class_id,
        object_name
    )
    VALUES (
        selected_class_id,
        p_object_name
    )
    RETURNING object_id INTO inserted_object_id;

    FOR attribute_record IN
        SELECT ca.attribute_id, ca.attribute_name, ca.default_value
        FROM class_attribute ca
        WHERE ca.class_id IN (
            WITH RECURSIVE hierarchy(class_id, parent_class_id) AS (
                SELECT class_id, parent_class_id
                FROM class_definition
                WHERE class_id = selected_class_id

                UNION ALL

                SELECT parent.class_id, parent.parent_class_id
                FROM class_definition parent
                JOIN hierarchy child
                  ON child.parent_class_id = parent.class_id
            )
            SELECT class_id FROM hierarchy
        )
    LOOP
        IF p_attributes ? attribute_record.attribute_name THEN
            attribute_value :=
                p_attributes ->> attribute_record.attribute_name;
        ELSE
            attribute_value := attribute_record.default_value;
        END IF;

        IF attribute_value IS NOT NULL THEN
            INSERT INTO object_attribute_value(
                object_id,
                attribute_id,
                value_text
            )
            VALUES (
                inserted_object_id,
                attribute_record.attribute_id,
                attribute_value
            );
        END IF;
    END LOOP;

    INSERT INTO object_audit(
        object_id,
        operation,
        details
    )
    VALUES (
        inserted_object_id,
        'CREATE',
        jsonb_build_object(
            'class', p_class_name,
            'object', p_object_name
        )
    );
END;
$$;

-- ------------------------------------------------------------
-- 13. Class hierarchy reporting view
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW class_hierarchy AS
WITH RECURSIVE hierarchy AS (
    SELECT
        class_id,
        class_name,
        parent_class_id,
        class_name::TEXT AS full_path,
        0 AS depth
    FROM class_definition
    WHERE parent_class_id IS NULL

    UNION ALL

    SELECT
        child.class_id,
        child.class_name,
        child.parent_class_id,
        parent.full_path || ' -> ' || child.class_name,
        parent.depth + 1
    FROM class_definition child
    JOIN hierarchy parent
      ON child.parent_class_id = parent.class_id
)
SELECT *
FROM hierarchy;

-- ------------------------------------------------------------
-- 14. Class instance reporting view
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW object_details AS
SELECT
    o.object_id,
    c.class_name,
    o.object_name,
    o.state,
    jsonb_object_agg(
        ca.attribute_name,
        v.value_text
    ) FILTER (
        WHERE ca.attribute_name IS NOT NULL
    ) AS attributes
FROM object_instance o
JOIN class_definition c
  ON c.class_id = o.class_id
LEFT JOIN object_attribute_value v
  ON v.object_id = o.object_id
LEFT JOIN class_attribute ca
  ON ca.attribute_id = v.attribute_id
GROUP BY
    o.object_id,
    c.class_name,
    o.object_name,
    o.state;

-- ------------------------------------------------------------
-- 15. Sample class definitions
-- ------------------------------------------------------------

INSERT INTO class_definition(
    class_name,
    description,
    parent_class_id,
    is_abstract
)
VALUES
    ('Entity', 'Base entity class', NULL, TRUE),
    ('Employee', 'Employee domain class', 1, FALSE),
    ('Manager', 'Manager specialization', 2, FALSE),
    ('Developer', 'Developer specialization', 2, FALSE);

-- ------------------------------------------------------------
-- 16. Sample class attributes
-- ------------------------------------------------------------

INSERT INTO class_attribute(
    class_id,
    attribute_name,
    data_type,
    is_required,
    default_value,
    is_private
)
VALUES
    (1, 'entity_code', 'TEXT', TRUE, NULL, FALSE),
    (2, 'employee_name', 'TEXT', TRUE, NULL, FALSE),
    (2, 'salary', 'DECIMAL', TRUE, NULL, TRUE),
    (2, 'joining_date', 'DATE', FALSE, NULL, FALSE),
    (3, 'team_size', 'INTEGER', TRUE, '1', FALSE),
    (4, 'programming_language', 'TEXT', TRUE, 'Python', FALSE);

-- ------------------------------------------------------------
-- 17. Sample methods
-- ------------------------------------------------------------

INSERT INTO class_method(
    class_id,
    method_name,
    return_type,
    is_static,
    is_abstract,
    access_modifier
)
VALUES
    (1, 'validate', 'BOOLEAN', FALSE, TRUE, 'PUBLIC'),
    (2, 'calculate_salary', 'DECIMAL', FALSE, FALSE, 'PUBLIC'),
    (3, 'assign_team', 'VOID', FALSE, FALSE, 'PUBLIC'),
    (4, 'compile_code', 'BOOLEAN', FALSE, FALSE, 'PUBLIC');

-- ------------------------------------------------------------
-- 18. Create objects transactionally
-- ------------------------------------------------------------

CALL create_object(
    'Manager',
    'Manager_Aarav',
    '{
        "entity_code": "ENT-001",
        "employee_name": "Aarav Sharma",
        "salary": "95000",
        "joining_date": "2025-01-15",
        "team_size": "8"
    }'::jsonb
);

CALL create_object(
    'Developer',
    'Developer_Meera',
    '{
        "entity_code": "ENT-002",
        "employee_name": "Meera Verma",
        "salary": "75000",
        "joining_date": "2025-03-10",
        "programming_language": "Java"
    }'::jsonb
);

COMMIT;

-- ------------------------------------------------------------
-- 19. Retrieval queries
-- ------------------------------------------------------------

SELECT *
FROM class_definition
ORDER BY class_id;

SELECT *
FROM class_hierarchy
ORDER BY depth, class_id;

SELECT *
FROM class_attribute
ORDER BY class_id, attribute_id;

SELECT *
FROM class_method
ORDER BY class_id, method_id;

SELECT *
FROM object_details
ORDER BY object_id;

-- ------------------------------------------------------------
-- 20. Validation and inheritance evaluation
-- ------------------------------------------------------------

SELECT
    c.class_name,
    c.is_abstract,
    COUNT(DISTINCT a.attribute_id) AS attribute_count,
    COUNT(DISTINCT m.method_id) AS method_count
FROM class_definition c
LEFT JOIN class_attribute a
    ON a.class_id = c.class_id
LEFT JOIN class_method m
    ON m.class_id = c.class_id
GROUP BY c.class_id, c.class_name, c.is_abstract
ORDER BY c.class_id;

-- ------------------------------------------------------------
-- 21. Aggregation and reporting
-- ------------------------------------------------------------

SELECT
    c.class_name,
    COUNT(o.object_id) AS object_count,
    COUNT(*) FILTER (
        WHERE o.state = 'ACTIVE'
    ) AS active_objects
FROM class_definition c
LEFT JOIN object_instance o
    ON o.class_id = c.class_id
GROUP BY c.class_name
ORDER BY object_count DESC;

SELECT
    operation,
    COUNT(*) AS operations,
    MAX(changed_at) AS latest_operation
FROM object_audit
GROUP BY operation;

-- ------------------------------------------------------------
-- 22. Demonstrate a failed operation safely
-- ------------------------------------------------------------

DO $$
BEGIN
    BEGIN
        CALL create_object(
            'Entity',
            'Invalid_Abstract_Instance',
            '{"entity_code":"INVALID"}'::jsonb
        );

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Expected failure: %', SQLERRM;
    END;
END;
$$;

-- ------------------------------------------------------------
-- 23. Demonstrate attribute retrieval
-- ------------------------------------------------------------

SELECT
    o.object_name,
    c.class_name,
    ca.attribute_name,
    v.value_text,
    ca.data_type
FROM object_instance o
JOIN class_definition c
    ON c.class_id = o.class_id
JOIN object_attribute_value v
    ON v.object_id = o.object_id
JOIN class_attribute ca
    ON ca.attribute_id = v.attribute_id
ORDER BY o.object_id, ca.attribute_name;

-- ------------------------------------------------------------
-- 24. Inheritance-aware attribute reporting
-- ------------------------------------------------------------

WITH RECURSIVE class_tree AS (
    SELECT
        class_id,
        class_name,
        parent_class_id,
        0 AS depth
    FROM class_definition
    WHERE parent_class_id IS NULL

    UNION ALL

    SELECT
        child.class_id,
        child.class_name,
        child.parent_class_id,
        parent.depth + 1
    FROM class_definition child
    JOIN class_tree parent
        ON child.parent_class_id = parent.class_id
)
SELECT
    class_tree.class_name,
    class_tree.depth,
    COUNT(class_attribute.attribute_id) AS declared_attributes
FROM class_tree
LEFT JOIN class_attribute
    ON class_attribute.class_id = class_tree.class_id
GROUP BY
    class_tree.class_id,
    class_tree.class_name,
    class_tree.depth
ORDER BY class_tree.depth, class_tree.class_name;

-- ------------------------------------------------------------
-- 25. Operational integrity checks
-- ------------------------------------------------------------

SELECT
    o.object_id,
    o.object_name,
    ca.attribute_name
FROM object_instance o
JOIN class_attribute ca
    ON ca.class_id = o.class_id
LEFT JOIN object_attribute_value v
    ON v.object_id = o.object_id
   AND v.attribute_id = ca.attribute_id
WHERE ca.is_required = TRUE
  AND ca.default_value IS NULL
  AND v.value_id IS NULL;

-- The result should be empty for valid sample objects.

SELECT
    COUNT(*) AS total_classes
FROM class_definition;

SELECT
    COUNT(*) AS total_objects
FROM object_instance;

SELECT
    COUNT(*) AS total_attribute_values
FROM object_attribute_value;

-- ============================================================
-- End of class creation and object modeling demonstration.
-- ============================================================
