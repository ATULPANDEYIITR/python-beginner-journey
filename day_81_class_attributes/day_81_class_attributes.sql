-- ============================================================
-- CLASS ATTRIBUTES: POSTGRESQL IMPLEMENTATION
-- PostgreSQL 15+
--
-- Models class definitions, shared class attributes,
-- inheritance, instance attributes, overrides, validation,
-- effective attribute resolution and audit history.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS class_attributes;

SET search_path TO class_attributes, public;

-- ------------------------------------------------------------
-- 1. Domain types
-- ------------------------------------------------------------

CREATE TYPE attribute_scope AS ENUM (
    'CLASS',
    'INSTANCE'
);

CREATE TYPE attribute_data_type AS ENUM (
    'TEXT',
    'INTEGER',
    'BOOLEAN',
    'NUMERIC'
);

CREATE TYPE object_state AS ENUM (
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

    parent_class_id BIGINT REFERENCES class_definition(class_id),

    description TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_class_name
        CHECK (class_name ~ '^[A-Za-z][A-Za-z0-9_]*$'),

    CONSTRAINT no_direct_self_inheritance
        CHECK (parent_class_id IS DISTINCT FROM class_id)
);

CREATE INDEX idx_class_parent
    ON class_definition(parent_class_id);

-- ------------------------------------------------------------
-- 3. Class attributes
--
-- One class attribute definition represents a shared
-- default value belonging to a class.
--
-- A child class may define an attribute with the same name.
-- This represents class-level attribute shadowing.
-- ------------------------------------------------------------

CREATE TABLE class_attribute (
    attribute_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    class_id BIGINT NOT NULL
        REFERENCES class_definition(class_id)
        ON DELETE CASCADE,

    attribute_name VARCHAR(100) NOT NULL,

    data_type attribute_data_type NOT NULL,

    text_value TEXT,

    integer_value BIGINT,

    boolean_value BOOLEAN,

    numeric_value NUMERIC(18,4),

    mutable BOOLEAN NOT NULL DEFAULT FALSE,

    description TEXT NOT NULL DEFAULT '',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_class_attribute
        UNIQUE (class_id, attribute_name),

    CONSTRAINT valid_attribute_name
        CHECK (attribute_name ~ '^[A-Za-z][A-Za-z0-9_]*$'),

    CONSTRAINT exactly_one_typed_value
        CHECK (
            num_nonnulls(
                text_value,
                integer_value,
                boolean_value,
                numeric_value
            ) = 1
        ),

    CONSTRAINT value_matches_data_type
        CHECK (
            (data_type = 'TEXT' AND text_value IS NOT NULL)
            OR
            (data_type = 'INTEGER' AND integer_value IS NOT NULL)
            OR
            (data_type = 'BOOLEAN' AND boolean_value IS NOT NULL)
            OR
            (data_type = 'NUMERIC' AND numeric_value IS NOT NULL)
        )
);

CREATE INDEX idx_class_attribute_name
    ON class_attribute(attribute_name);

-- ------------------------------------------------------------
-- 4. Instances
-- ------------------------------------------------------------

CREATE TABLE class_instance (
    instance_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    class_id BIGINT NOT NULL
        REFERENCES class_definition(class_id),

    instance_name VARCHAR(150) NOT NULL UNIQUE,

    owner_name VARCHAR(150) NOT NULL,

    state object_state NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_instance_name
        CHECK (length(trim(instance_name)) > 0),

    CONSTRAINT valid_owner_name
        CHECK (length(trim(owner_name)) > 0)
);

CREATE INDEX idx_instance_class
    ON class_instance(class_id);

CREATE INDEX idx_instance_state
    ON class_instance(state);

-- ------------------------------------------------------------
-- 5. Instance attribute overrides
--
-- An override is stored separately from the class attribute.
-- It does not change the shared class-level value.
-- ------------------------------------------------------------

CREATE TABLE instance_attribute (
    instance_attribute_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    instance_id BIGINT NOT NULL
        REFERENCES class_instance(instance_id)
        ON DELETE CASCADE,

    attribute_name VARCHAR(100) NOT NULL,

    data_type attribute_data_type NOT NULL,

    text_value TEXT,

    integer_value BIGINT,

    boolean_value BOOLEAN,

    numeric_value NUMERIC(18,4),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_instance_override
        UNIQUE (instance_id, attribute_name),

    CONSTRAINT exactly_one_instance_value
        CHECK (
            num_nonnulls(
                text_value,
                integer_value,
                boolean_value,
                numeric_value
            ) = 1
        ),

    CONSTRAINT instance_value_matches_type
        CHECK (
            (data_type = 'TEXT' AND text_value IS NOT NULL)
            OR
            (data_type = 'INTEGER' AND integer_value IS NOT NULL)
            OR
            (data_type = 'BOOLEAN' AND boolean_value IS NOT NULL)
            OR
            (data_type = 'NUMERIC' AND numeric_value IS NOT NULL)
        )
);

CREATE INDEX idx_instance_attribute_lookup
    ON instance_attribute(instance_id, attribute_name);

-- ------------------------------------------------------------
-- 6. Attribute audit
-- ------------------------------------------------------------

CREATE TABLE attribute_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    entity_type VARCHAR(20) NOT NULL,

    entity_id BIGINT NOT NULL,

    attribute_name VARCHAR(100) NOT NULL,

    operation VARCHAR(20) NOT NULL,

    previous_value JSONB,

    new_value JSONB,

    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    changed_by TEXT NOT NULL DEFAULT CURRENT_USER,

    CONSTRAINT valid_audit_entity
        CHECK (entity_type IN ('CLASS', 'INSTANCE')),

    CONSTRAINT valid_audit_operation
        CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE'))
);

CREATE INDEX idx_attribute_audit_time
    ON attribute_audit(changed_at DESC);

-- ------------------------------------------------------------
-- 7. Prevent inheritance cycles
--
-- A class cannot inherit from itself indirectly.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_class_inheritance()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    cycle_found BOOLEAN;
BEGIN
    IF NEW.parent_class_id IS NULL THEN
        RETURN NEW;
    END IF;

    WITH RECURSIVE ancestors(class_id) AS (
        SELECT NEW.parent_class_id

        UNION ALL

        SELECT cd.parent_class_id
        FROM class_definition cd
        JOIN ancestors a
          ON cd.class_id = a.class_id
        WHERE cd.parent_class_id IS NOT NULL
    )
    SELECT EXISTS (
        SELECT 1
        FROM ancestors
        WHERE class_id = NEW.class_id
    )
    INTO cycle_found;

    IF cycle_found THEN
        RAISE EXCEPTION
            'Circular class inheritance is not permitted.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_class_inheritance
BEFORE INSERT OR UPDATE OF parent_class_id
ON class_definition
FOR EACH ROW
EXECUTE FUNCTION validate_class_inheritance();

-- ------------------------------------------------------------
-- 8. Validate instance overrides against inherited definitions
--
-- Instance overrides must match the declared attribute type.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_instance_override()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    expected_type attribute_data_type;
    current_class_id BIGINT;
BEGIN
    SELECT class_id
    INTO current_class_id
    FROM class_instance
    WHERE instance_id = NEW.instance_id;

    IF current_class_id IS NULL THEN
        RAISE EXCEPTION 'Instance does not exist.';
    END IF;

    WITH RECURSIVE hierarchy(class_id, parent_class_id) AS (
        SELECT class_id, parent_class_id
        FROM class_definition
        WHERE class_id = current_class_id

        UNION ALL

        SELECT parent.class_id, parent.parent_class_id
        FROM class_definition parent
        JOIN hierarchy child
          ON child.parent_class_id = parent.class_id
    )
    SELECT ca.data_type
    INTO expected_type
    FROM hierarchy h
    JOIN class_attribute ca
      ON ca.class_id = h.class_id
    WHERE ca.attribute_name = NEW.attribute_name
    ORDER BY h.class_id = current_class_id DESC
    LIMIT 1;

    IF expected_type IS NULL THEN
        RAISE EXCEPTION
            'Attribute % is not defined in the class hierarchy.',
            NEW.attribute_name;
    END IF;

    IF expected_type <> NEW.data_type THEN
        RAISE EXCEPTION
            'Attribute type mismatch for %.',
            NEW.attribute_name;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_instance_override
BEFORE INSERT OR UPDATE
ON instance_attribute
FOR EACH ROW
EXECUTE FUNCTION validate_instance_override();

-- ------------------------------------------------------------
-- 9. Audit trigger
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION record_attribute_audit()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    old_value JSONB;
    new_value JSONB;
    entity_identifier BIGINT;
    attribute_identifier TEXT;
    entity_identifier_type TEXT;
    action_name TEXT;
BEGIN
    IF TG_OP = 'INSERT' THEN
        new_value := to_jsonb(NEW);
        entity_identifier := NEW.instance_id;
        attribute_identifier := NEW.attribute_name;
        entity_identifier_type := 'INSTANCE';
        action_name := 'INSERT';

    ELSIF TG_OP = 'UPDATE' THEN
        old_value := to_jsonb(OLD);
        new_value := to_jsonb(NEW);
        entity_identifier := NEW.instance_id;
        attribute_identifier := NEW.attribute_name;
        entity_identifier_type := 'INSTANCE';
        action_name := 'UPDATE';

    ELSE
        old_value := to_jsonb(OLD);
        entity_identifier := OLD.instance_id;
        attribute_identifier := OLD.attribute_name;
        entity_identifier_type := 'INSTANCE';
        action_name := 'DELETE';
    END IF;

    INSERT INTO attribute_audit (
        entity_type,
        entity_id,
        attribute_name,
        operation,
        previous_value,
        new_value
    )
    VALUES (
        entity_identifier_type,
        entity_identifier,
        attribute_identifier,
        action_name,
        old_value,
        new_value
    );

    RETURN CASE
        WHEN TG_OP = 'DELETE' THEN OLD
        ELSE NEW
    END;
END;
$$;

CREATE TRIGGER trg_instance_attribute_audit
AFTER INSERT OR UPDATE OR DELETE
ON instance_attribute
FOR EACH ROW
EXECUTE FUNCTION record_attribute_audit();

-- ------------------------------------------------------------
-- 10. Effective attribute resolution
--
-- Resolution order:
-- 1. Instance override.
-- 2. Nearest class definition.
-- 3. Parent class definitions.
--
-- A child class definition shadows its parent definition.
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW effective_instance_attributes AS
WITH RECURSIVE hierarchy AS (
    SELECT
        ci.instance_id,
        ci.class_id AS current_class_id,
        ci.class_id AS definition_class_id,
        0 AS inheritance_depth
    FROM class_instance ci

    UNION ALL

    SELECT
        h.instance_id,
        h.current_class_id,
        parent.class_id,
        h.inheritance_depth + 1
    FROM hierarchy h
    JOIN class_definition current_class
      ON current_class.class_id = h.definition_class_id
    JOIN class_definition parent
      ON parent.class_id = current_class.parent_class_id
),
resolved_class_attributes AS (
    SELECT DISTINCT ON (
        h.instance_id,
        ca.attribute_name
    )
        h.instance_id,
        ca.attribute_name,
        ca.data_type,
        ca.text_value,
        ca.integer_value,
        ca.boolean_value,
        ca.numeric_value,
        h.inheritance_depth
    FROM hierarchy h
    JOIN class_attribute ca
      ON ca.class_id = h.definition_class_id
    ORDER BY
        h.instance_id,
        ca.attribute_name,
        h.inheritance_depth
)
SELECT
    ci.instance_id,
    ci.instance_name,
    ci.class_id,
    rca.attribute_name,
    COALESCE(ia.data_type, rca.data_type) AS data_type,

    COALESCE(ia.text_value, rca.text_value) AS text_value,

    COALESCE(ia.integer_value, rca.integer_value) AS integer_value,

    COALESCE(ia.boolean_value, rca.boolean_value) AS boolean_value,

    COALESCE(ia.numeric_value, rca.numeric_value) AS numeric_value,

    CASE
        WHEN ia.instance_attribute_id IS NOT NULL
            THEN 'INSTANCE_OVERRIDE'
        ELSE 'CLASS_DEFAULT'
    END AS attribute_source

FROM class_instance ci

JOIN resolved_class_attributes rca
  ON rca.instance_id = ci.instance_id

LEFT JOIN instance_attribute ia
  ON ia.instance_id = ci.instance_id
 AND ia.attribute_name = rca.attribute_name;

-- ------------------------------------------------------------
-- 11. Attribute lookup function
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION get_effective_attribute(
    p_instance_id BIGINT,
    p_attribute_name VARCHAR
)
RETURNS TABLE (
    attribute_name VARCHAR,
    data_type attribute_data_type,
    text_value TEXT,
    integer_value BIGINT,
    boolean_value BOOLEAN,
    numeric_value NUMERIC,
    attribute_source TEXT
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        e.attribute_name,
        e.data_type,
        e.text_value,
        e.integer_value,
        e.boolean_value,
        e.numeric_value,
        e.attribute_source
    FROM effective_instance_attributes e
    WHERE e.instance_id = p_instance_id
      AND e.attribute_name = p_attribute_name;
$$;

-- ------------------------------------------------------------
-- 12. Class attribute update procedure
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE update_class_text_attribute(
    p_class_id BIGINT,
    p_attribute_name VARCHAR,
    p_new_value TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_new_value IS NULL THEN
        RAISE EXCEPTION 'Class attribute cannot be NULL.';
    END IF;

    UPDATE class_attribute
    SET text_value = p_new_value
    WHERE class_id = p_class_id
      AND attribute_name = p_attribute_name
      AND data_type = 'TEXT';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Text class attribute was not found.';
    END IF;
END;
$$;

-- ------------------------------------------------------------
-- 13. Sample class hierarchy
-- ------------------------------------------------------------

INSERT INTO class_definition (
    class_name,
    parent_class_id,
    description
)
VALUES (
    'BaseRepository',
    NULL,
    'Common repository class'
);

INSERT INTO class_definition (
    class_name,
    parent_class_id,
    description
)
SELECT
    'EnterpriseRepository',
    class_id,
    'Enterprise repository specialization'
FROM class_definition
WHERE class_name = 'BaseRepository';

INSERT INTO class_definition (
    class_name,
    parent_class_id,
    description
)
VALUES (
    'StandaloneRepository',
    NULL,
    'Independent repository class'
);

-- ------------------------------------------------------------
-- 14. Shared class attribute definitions
-- ------------------------------------------------------------

INSERT INTO class_attribute (
    class_id,
    attribute_name,
    data_type,
    text_value,
    description
)
SELECT
    class_id,
    'organization',
    'TEXT',
    'OpenSystems',
    'Default organization name'
FROM class_definition
WHERE class_name = 'BaseRepository';

INSERT INTO class_attribute (
    class_id,
    attribute_name,
    data_type,
    integer_value,
    description
)
SELECT
    class_id,
    'maximum_repositories',
    'INTEGER',
    100,
    'Maximum repository capacity'
FROM class_definition
WHERE class_name = 'BaseRepository';

INSERT INTO class_attribute (
    class_id,
    attribute_name,
    data_type,
    boolean_value,
    description
)
SELECT
    class_id,
    'audit_enabled',
    'BOOLEAN',
    FALSE,
    'Default audit configuration'
FROM class_definition
WHERE class_name = 'BaseRepository';

-- Child class shadows inherited organization and capacity.
INSERT INTO class_attribute (
    class_id,
    attribute_name,
    data_type,
    text_value,
    description
)
SELECT
    class_id,
    'organization',
    'TEXT',
    'EnterpriseSystems',
    'Enterprise organization override'
FROM class_definition
WHERE class_name = 'EnterpriseRepository';

INSERT INTO class_attribute (
    class_id,
    attribute_name,
    data_type,
    integer_value,
    description
)
SELECT
    class_id,
    'maximum_repositories',
    'INTEGER',
    50,
    'Enterprise repository capacity'
FROM class_definition
WHERE class_name = 'EnterpriseRepository';

INSERT INTO class_attribute (
    class_id,
    attribute_name,
    data_type,
    boolean_value,
    description
)
SELECT
    class_id,
    'audit_enabled',
    'BOOLEAN',
    TRUE,
    'Enterprise auditing requirement'
FROM class_definition
WHERE class_name = 'EnterpriseRepository';

INSERT INTO class_attribute (
    class_id,
    attribute_name,
    data_type,
    text_value,
    description
)
SELECT
    class_id,
    'organization',
    'TEXT',
    'StandaloneSystems',
    'Standalone organization'
FROM class_definition
WHERE class_name = 'StandaloneRepository';

-- ------------------------------------------------------------
-- 15. Create class instances
-- ------------------------------------------------------------

INSERT INTO class_instance (
    class_id,
    instance_name,
    owner_name
)
SELECT
    class_id,
    'payments-platform',
    'finance-team'
FROM class_definition
WHERE class_name = 'BaseRepository';

INSERT INTO class_instance (
    class_id,
    instance_name,
    owner_name
)
SELECT
    class_id,
    'secure-infrastructure',
    'security-team'
FROM class_definition
WHERE class_name = 'EnterpriseRepository';

INSERT INTO class_instance (
    class_id,
    instance_name,
    owner_name
)
SELECT
    class_id,
    'analytics-platform',
    'data-team'
FROM class_definition
WHERE class_name = 'BaseRepository';

-- ------------------------------------------------------------
-- 16. Instance-level overrides
-- ------------------------------------------------------------

INSERT INTO instance_attribute (
    instance_id,
    attribute_name,
    data_type,
    text_value
)
SELECT
    instance_id,
    'organization',
    'TEXT',
    'CustomFinanceSystems'
FROM class_instance
WHERE instance_name = 'payments-platform';

INSERT INTO instance_attribute (
    instance_id,
    attribute_name,
    data_type,
    boolean_value
)
SELECT
    instance_id,
    'audit_enabled',
    'BOOLEAN',
    TRUE
FROM class_instance
WHERE instance_name = 'payments-platform';

-- ------------------------------------------------------------
-- 17. Retrieval queries
-- ------------------------------------------------------------

SELECT
    class_name,
    parent_class_id,
    description
FROM class_definition
ORDER BY class_id;

SELECT
    cd.class_name,
    ca.attribute_name,
    ca.data_type,
    ca.text_value,
    ca.integer_value,
    ca.boolean_value
FROM class_attribute ca
JOIN class_definition cd
  ON cd.class_id = ca.class_id
ORDER BY cd.class_name, ca.attribute_name;

-- ------------------------------------------------------------
-- 18. Effective attribute reporting
-- ------------------------------------------------------------

SELECT
    instance_name,
    attribute_name,
    data_type,
    text_value,
    integer_value,
    boolean_value,
    attribute_source
FROM effective_instance_attributes
ORDER BY instance_name, attribute_name;

-- ------------------------------------------------------------
-- 19. Direct effective attribute lookup
-- ------------------------------------------------------------

SELECT *
FROM get_effective_attribute(
    (
        SELECT instance_id
        FROM class_instance
        WHERE instance_name = 'payments-platform'
    ),
    'organization'
);

-- ------------------------------------------------------------
-- 20. Aggregation and evaluation
-- ------------------------------------------------------------

SELECT
    cd.class_name,
    COUNT(ci.instance_id) AS instance_count,
    COUNT(*) FILTER (
        WHERE ci.state = 'ACTIVE'
    ) AS active_instances
FROM class_definition cd
LEFT JOIN class_instance ci
  ON ci.class_id = cd.class_id
GROUP BY cd.class_id, cd.class_name
ORDER BY cd.class_name;

SELECT
    instance_name,
    COUNT(*) AS resolved_attribute_count,
    COUNT(*) FILTER (
        WHERE attribute_source = 'INSTANCE_OVERRIDE'
    ) AS override_count,
    COUNT(*) FILTER (
        WHERE attribute_source = 'CLASS_DEFAULT'
    ) AS inherited_or_class_default_count
FROM effective_instance_attributes
GROUP BY instance_id, instance_name
ORDER BY instance_name;

-- ------------------------------------------------------------
-- 21. Workflow: transactional class attribute update
-- ------------------------------------------------------------

SAVEPOINT before_class_update;

CALL update_class_text_attribute(
    (
        SELECT class_id
        FROM class_definition
        WHERE class_name = 'BaseRepository'
    ),
    'organization',
    'UpdatedOpenSystems'
);

-- Existing instances without overrides resolve the new value.
SELECT
    instance_name,
    text_value,
    attribute_source
FROM effective_instance_attributes
WHERE attribute_name = 'organization'
ORDER BY instance_name;

-- ------------------------------------------------------------
-- 22. Validation reporting
-- ------------------------------------------------------------

SELECT
    ci.instance_name,
    ia.attribute_name,
    ia.data_type AS override_type,
    ca.data_type AS class_definition_type
FROM instance_attribute ia
JOIN class_instance ci
  ON ci.instance_id = ia.instance_id
JOIN class_definition cd
  ON cd.class_id = ci.class_id
JOIN class_attribute ca
  ON ca.class_id = cd.class_id
 AND ca.attribute_name = ia.attribute_name
WHERE ia.data_type <> ca.data_type;

-- No rows should be returned for valid overrides.

-- ------------------------------------------------------------
-- 23. Audit retrieval
-- ------------------------------------------------------------

SELECT
    audit_id,
    entity_type,
    entity_id,
    attribute_name,
    operation,
    previous_value,
    new_value,
    changed_at
FROM attribute_audit
ORDER BY changed_at DESC, audit_id DESC;

-- ------------------------------------------------------------
-- 24. Inheritance hierarchy report
-- ------------------------------------------------------------

WITH RECURSIVE hierarchy AS (
    SELECT
        class_id,
        class_name,
        parent_class_id,
        0 AS depth,
        class_name::TEXT AS hierarchy_path
    FROM class_definition
    WHERE parent_class_id IS NULL

    UNION ALL

    SELECT
        child.class_id,
        child.class_name,
        child.parent_class_id,
        parent.depth + 1,
        parent.hierarchy_path || ' -> ' || child.class_name
    FROM class_definition child
    JOIN hierarchy parent
      ON child.parent_class_id = parent.class_id
)
SELECT
    class_name,
    depth,
    hierarchy_path
FROM hierarchy
ORDER BY hierarchy_path;

-- ------------------------------------------------------------
-- 25. Demonstrate a rejected override transaction
-- ------------------------------------------------------------

SAVEPOINT before_invalid_override;

DO $$
DECLARE
    target_instance BIGINT;
BEGIN
    SELECT instance_id
    INTO target_instance
    FROM class_instance
    WHERE instance_name = 'analytics-platform';

    BEGIN
        INSERT INTO instance_attribute (
            instance_id,
            attribute_name,
            data_type,
            integer_value
        )
        VALUES (
            target_instance,
            'organization',
            'INTEGER',
            500
        );

    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Expected validation failure: %', SQLERRM;
    END;
END;
$$;

-- ------------------------------------------------------------
-- 26. Reporting: class versus instance attribute scope
-- ------------------------------------------------------------

SELECT
    cd.class_name,
    ca.attribute_name,
    'CLASS' AS attribute_scope,
    COUNT(ci.instance_id) AS affected_instances
FROM class_attribute ca
JOIN class_definition cd
  ON cd.class_id = ca.class_id
LEFT JOIN class_instance ci
  ON ci.class_id = ca.class_id
GROUP BY cd.class_id, cd.class_name, ca.attribute_name

UNION ALL

SELECT
    cd.class_name,
    ia.attribute_name,
    'INSTANCE' AS attribute_scope,
    COUNT(DISTINCT ci.instance_id) AS affected_instances
FROM instance_attribute ia
JOIN class_instance ci
  ON ci.instance_id = ia.instance_id
JOIN class_definition cd
  ON cd.class_id = ci.class_id
GROUP BY cd.class_name, ia.attribute_name

ORDER BY class_name, attribute_name, attribute_scope;

-- ------------------------------------------------------------
-- 27. Transaction completion
-- ------------------------------------------------------------

COMMIT;
