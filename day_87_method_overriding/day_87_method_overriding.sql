-- ============================================================
-- METHOD OVERRIDING: RELATIONAL MODEL AND EXECUTION AUDIT
-- PostgreSQL 15+
--
-- Domain: Enterprise notification delivery.
--
-- The database models:
-- 1. Class definitions and inheritance relationships.
-- 2. Declared methods and overridden methods.
-- 3. Runtime dispatch decisions.
-- 4. Method contracts and compatibility validation.
-- 5. Invocation history and execution outcomes.
--
-- PostgreSQL table inheritance is not equivalent to Java,
-- C++ or Python class inheritance. This schema explicitly
-- models method overriding as application-level metadata.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS overriding_lab;

SET search_path TO overriding_lab, public;

-- ============================================================
-- 1. DOMAIN TYPES
-- ============================================================

CREATE TYPE method_kind AS ENUM (
    'INSTANCE',
    'STATIC',
    'CONSTRUCTOR'
);

CREATE TYPE invocation_status AS ENUM (
    'SUCCESS',
    'FAILED',
    'REJECTED'
);

CREATE TYPE access_level AS ENUM (
    'PUBLIC',
    'PROTECTED',
    'PRIVATE'
);

-- ============================================================
-- 2. CLASS DEFINITIONS
-- ============================================================

CREATE TABLE class_definitions (
    class_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    class_name VARCHAR(100) NOT NULL UNIQUE,

    parent_class_id BIGINT,

    is_abstract BOOLEAN NOT NULL DEFAULT FALSE,

    is_final BOOLEAN NOT NULL DEFAULT FALSE,

    description TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_parent_class
        FOREIGN KEY (parent_class_id)
        REFERENCES class_definitions(class_id),

    CONSTRAINT no_direct_self_inheritance
        CHECK (
            parent_class_id IS NULL
            OR parent_class_id <> class_id
        )
);

CREATE INDEX idx_class_parent
ON class_definitions(parent_class_id);

-- ============================================================
-- 3. METHOD DECLARATIONS
-- ============================================================

CREATE TABLE method_definitions (
    method_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    class_id BIGINT NOT NULL,

    method_name VARCHAR(120) NOT NULL,

    method_signature VARCHAR(300) NOT NULL,

    method_kind method_kind NOT NULL DEFAULT 'INSTANCE',

    return_type VARCHAR(100) NOT NULL,

    access access_level NOT NULL DEFAULT 'PUBLIC',

    is_abstract BOOLEAN NOT NULL DEFAULT FALSE,

    is_final BOOLEAN NOT NULL DEFAULT FALSE,

    is_static BOOLEAN NOT NULL DEFAULT FALSE,

    implementation_description TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_method_class
        FOREIGN KEY (class_id)
        REFERENCES class_definitions(class_id),

    CONSTRAINT unique_class_method
        UNIQUE (class_id, method_signature),

    CONSTRAINT static_method_consistency
        CHECK (
            NOT is_static
            OR method_kind = 'STATIC'
        ),

    CONSTRAINT no_abstract_final_method
        CHECK (
            NOT (is_abstract AND is_final)
        )
);

CREATE INDEX idx_method_name
ON method_definitions(method_name);

CREATE INDEX idx_method_class
ON method_definitions(class_id);

-- ============================================================
-- 4. OVERRIDE RELATIONSHIPS
-- ============================================================

CREATE TABLE method_overrides (
    override_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    parent_method_id BIGINT NOT NULL,

    overriding_method_id BIGINT NOT NULL UNIQUE,

    declared_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_parent_method
        FOREIGN KEY (parent_method_id)
        REFERENCES method_definitions(method_id),

    CONSTRAINT fk_overriding_method
        FOREIGN KEY (overriding_method_id)
        REFERENCES method_definitions(method_id),

    CONSTRAINT no_self_override
        CHECK (
            parent_method_id <> overriding_method_id
        )
);

CREATE INDEX idx_override_parent
ON method_overrides(parent_method_id);

-- ============================================================
-- 5. METHOD CONTRACTS
-- ============================================================

CREATE TABLE method_contracts (
    contract_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    method_id BIGINT NOT NULL UNIQUE,

    parameter_count INTEGER NOT NULL DEFAULT 0,

    parameter_signature TEXT NOT NULL DEFAULT '',

    return_type VARCHAR(100) NOT NULL,

    contract_description TEXT NOT NULL,

    CONSTRAINT fk_contract_method
        FOREIGN KEY (method_id)
        REFERENCES method_definitions(method_id),

    CONSTRAINT valid_parameter_count
        CHECK (parameter_count >= 0)
);

-- ============================================================
-- 6. RUNTIME OBJECT INSTANCES
-- ============================================================

CREATE TABLE object_instances (
    object_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    object_name VARCHAR(120) NOT NULL UNIQUE,

    class_id BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_object_class
        FOREIGN KEY (class_id)
        REFERENCES class_definitions(class_id)
);

CREATE INDEX idx_object_class
ON object_instances(class_id);

-- ============================================================
-- 7. METHOD INVOCATION AUDIT
-- ============================================================

CREATE TABLE method_invocations (
    invocation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    object_id BIGINT NOT NULL,

    requested_method_id BIGINT NOT NULL,

    resolved_method_id BIGINT NOT NULL,

    invocation_status invocation_status NOT NULL,

    execution_result JSONB,

    error_message TEXT,

    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_invocation_object
        FOREIGN KEY (object_id)
        REFERENCES object_instances(object_id),

    CONSTRAINT fk_requested_method
        FOREIGN KEY (requested_method_id)
        REFERENCES method_definitions(method_id),

    CONSTRAINT fk_resolved_method
        FOREIGN KEY (resolved_method_id)
        REFERENCES method_definitions(method_id),

    CONSTRAINT valid_error_state
        CHECK (
            invocation_status <> 'FAILED'
            OR error_message IS NOT NULL
        )
);

CREATE INDEX idx_invocation_object_time
ON method_invocations(object_id, executed_at DESC);

CREATE INDEX idx_invocation_resolved_method
ON method_invocations(resolved_method_id);

CREATE INDEX idx_invocation_status
ON method_invocations(invocation_status);

-- ============================================================
-- 8. CLASS HIERARCHY VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_class_hierarchy()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    current_parent BIGINT;
    visited BIGINT[];
BEGIN
    IF NEW.parent_class_id IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT is_final
    INTO STRICT NEW.is_final
    FROM class_definitions
    WHERE class_id = NEW.parent_class_id;

    IF NEW.class_id IS NOT NULL
       AND NEW.parent_class_id = NEW.class_id THEN
        RAISE EXCEPTION
            'A class cannot inherit from itself';
    END IF;

    current_parent := NEW.parent_class_id;
    visited := ARRAY[NEW.parent_class_id];

    LOOP
        SELECT parent_class_id
        INTO current_parent
        FROM class_definitions
        WHERE class_id = current_parent;

        EXIT WHEN current_parent IS NULL;

        IF current_parent = NEW.class_id THEN
            RAISE EXCEPTION
                'Circular class inheritance detected';
        END IF;

        IF current_parent = ANY(visited) THEN
            RAISE EXCEPTION
                'Existing circular hierarchy detected';
        END IF;

        visited := array_append(visited, current_parent);
    END LOOP;

    RETURN NEW;
END;
$$;

-- The trigger is installed on class insertion and parent changes.
CREATE TRIGGER trg_validate_class_hierarchy
BEFORE INSERT OR UPDATE OF parent_class_id
ON class_definitions
FOR EACH ROW
EXECUTE FUNCTION validate_class_hierarchy();

-- ============================================================
-- 9. METHOD OVERRIDE VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_method_override()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    parent_method RECORD;
    child_method RECORD;
    current_class BIGINT;
    parent_class BIGINT;
    hierarchy_valid BOOLEAN := FALSE;
BEGIN
    SELECT *
    INTO STRICT parent_method
    FROM method_definitions
    WHERE method_id = NEW.parent_method_id;

    SELECT *
    INTO STRICT child_method
    FROM method_definitions
    WHERE method_id = NEW.overriding_method_id;

    IF parent_method.method_name <> child_method.method_name THEN
        RAISE EXCEPTION
            'Overriding method names must match';
    END IF;

    IF parent_method.method_signature <>
       child_method.method_signature THEN
        RAISE EXCEPTION
            'Method signatures are incompatible';
    END IF;

    IF parent_method.return_type <> child_method.return_type THEN
        RAISE EXCEPTION
            'Return types are incompatible in this model';
    END IF;

    IF parent_method.is_static OR child_method.is_static THEN
        RAISE EXCEPTION
            'Static methods cannot participate in instance overriding';
    END IF;

    IF parent_method.method_kind <> 'INSTANCE'
       OR child_method.method_kind <> 'INSTANCE' THEN
        RAISE EXCEPTION
            'Only instance methods can be overridden';
    END IF;

    IF parent_method.is_final THEN
        RAISE EXCEPTION
            'A final method cannot be overridden';
    END IF;

    IF parent_method.access = 'PRIVATE' THEN
        RAISE EXCEPTION
            'Private methods are not inherited for overriding';
    END IF;

    IF child_method.access = 'PRIVATE' THEN
        RAISE EXCEPTION
            'Overriding method cannot reduce accessibility';
    END IF;

    IF parent_method.access = 'PUBLIC'
       AND child_method.access <> 'PUBLIC' THEN
        RAISE EXCEPTION
            'Public method accessibility cannot be reduced';
    END IF;

    IF parent_method.access = 'PROTECTED'
       AND child_method.access = 'PRIVATE' THEN
        RAISE EXCEPTION
            'Protected method accessibility cannot be reduced';
    END IF;

    SELECT parent_class_id
    INTO parent_class
    FROM class_definitions
    WHERE class_id = parent_method.class_id;

    current_class := child_method.class_id;

    WHILE current_class IS NOT NULL LOOP

        IF current_class = parent_method.class_id THEN
            hierarchy_valid := TRUE;
            EXIT;
        END IF;

        SELECT parent_class_id
        INTO current_class
        FROM class_definitions
        WHERE class_id = current_class;

    END LOOP;

    IF NOT hierarchy_valid THEN
        RAISE EXCEPTION
            'Overriding class must inherit from the declaring class';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_method_override
BEFORE INSERT OR UPDATE
ON method_overrides
FOR EACH ROW
EXECUTE FUNCTION validate_method_override();

-- ============================================================
-- 10. CONTRACT COMPATIBILITY
-- ============================================================

CREATE OR REPLACE FUNCTION validate_override_contract()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    parent_contract RECORD;
    child_contract RECORD;
BEGIN
    SELECT *
    INTO STRICT parent_contract
    FROM method_contracts
    WHERE method_id = NEW.parent_method_id;

    SELECT *
    INTO STRICT child_contract
    FROM method_contracts
    WHERE method_id = NEW.overriding_method_id;

    IF parent_contract.parameter_count <>
       child_contract.parameter_count THEN
        RAISE EXCEPTION
            'Override parameter count differs from parent';
    END IF;

    IF parent_contract.parameter_signature <>
       child_contract.parameter_signature THEN
        RAISE EXCEPTION
            'Override parameter signature differs from parent';
    END IF;

    IF parent_contract.return_type <>
       child_contract.return_type THEN
        RAISE EXCEPTION
            'Override return contract differs from parent';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_override_contract
BEFORE INSERT
ON method_overrides
FOR EACH ROW
EXECUTE FUNCTION validate_override_contract();

-- ============================================================
-- 11. RUNTIME METHOD RESOLUTION
-- ============================================================

CREATE OR REPLACE FUNCTION resolve_method(
    p_object_id BIGINT,
    p_requested_method_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    current_class BIGINT;
    requested_class BIGINT;
    requested_signature VARCHAR(300);
    requested_kind method_kind;
    resolved_method BIGINT;
BEGIN
    SELECT oi.class_id
    INTO STRICT current_class
    FROM object_instances oi
    WHERE oi.object_id = p_object_id;

    SELECT md.class_id,
           md.method_signature,
           md.method_kind
    INTO STRICT requested_class,
                requested_signature,
                requested_kind
    FROM method_definitions md
    WHERE md.method_id = p_requested_method_id;

    IF requested_kind <> 'INSTANCE' THEN
        RAISE EXCEPTION
            'Runtime overriding resolution requires an instance method';
    END IF;

    -- Verify that the requested method belongs to the object's
    -- inheritance hierarchy.
    LOOP
        EXIT WHEN current_class = requested_class;

        SELECT parent_class_id
        INTO current_class
        FROM class_definitions
        WHERE class_id = current_class;

        IF current_class IS NULL THEN
            RAISE EXCEPTION
                'Requested method is outside the object hierarchy';
        END IF;
    END LOOP;

    -- Search from the runtime class towards its ancestors.
    SELECT md.method_id
    INTO resolved_method
    FROM class_definitions cd
    JOIN method_definitions md
      ON md.class_id = cd.class_id
    WHERE cd.class_id IN (
        WITH RECURSIVE ancestors(class_id, parent_class_id, depth) AS (
            SELECT class_id, parent_class_id, 0
            FROM class_definitions
            WHERE class_id = (
                SELECT class_id
                FROM object_instances
                WHERE object_id = p_object_id
            )

            UNION ALL

            SELECT parent.class_id,
                   parent.parent_class_id,
                   child.depth + 1
            FROM ancestors child
            JOIN class_definitions parent
              ON parent.class_id = child.parent_class_id
        )
        SELECT class_id
        FROM ancestors
    )
      AND md.method_signature = requested_signature
      AND md.method_kind = 'INSTANCE'
    ORDER BY (
        WITH RECURSIVE ancestors(class_id, parent_class_id, depth) AS (
            SELECT class_id, parent_class_id, 0
            FROM class_definitions
            WHERE class_id = (
                SELECT class_id
                FROM object_instances
                WHERE object_id = p_object_id
            )

            UNION ALL

            SELECT parent.class_id,
                   parent.parent_class_id,
                   child.depth + 1
            FROM ancestors child
            JOIN class_definitions parent
              ON parent.class_id = child.parent_class_id
        )
        SELECT depth
        FROM ancestors
        WHERE ancestors.class_id = cd.class_id
    )
    LIMIT 1;

    IF resolved_method IS NULL THEN
        RAISE EXCEPTION
            'No compatible method implementation found';
    END IF;

    RETURN resolved_method;
END;
$$;

-- ============================================================
-- 12. INVOCATION RECORDING
-- ============================================================

CREATE OR REPLACE FUNCTION record_method_invocation(
    p_object_id BIGINT,
    p_requested_method_id BIGINT,
    p_result JSONB
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    resolved_id BIGINT;
    invocation_id BIGINT;
BEGIN
    resolved_id := resolve_method(
        p_object_id,
        p_requested_method_id
    );

    INSERT INTO method_invocations (
        object_id,
        requested_method_id,
        resolved_method_id,
        invocation_status,
        execution_result
    )
    VALUES (
        p_object_id,
        p_requested_method_id,
        resolved_id,
        'SUCCESS',
        p_result
    )
    RETURNING method_invocations.invocation_id
    INTO invocation_id;

    RETURN invocation_id;
END;
$$;

-- ============================================================
-- 13. REPORTING VIEW
-- ============================================================

CREATE OR REPLACE VIEW override_execution_report AS
SELECT
    mi.invocation_id,
    oi.object_name,
    runtime_class.class_name AS runtime_class,
    requested_class.class_name AS requested_method_class,
    requested_method.method_name,
    resolved_class.class_name AS resolved_method_class,
    resolved_method.method_signature,
    mi.invocation_status,
    mi.execution_result,
    mi.error_message,
    mi.executed_at
FROM method_invocations mi
JOIN object_instances oi
  ON oi.object_id = mi.object_id
JOIN class_definitions runtime_class
  ON runtime_class.class_id = oi.class_id
JOIN method_definitions requested_method
  ON requested_method.method_id = mi.requested_method_id
JOIN class_definitions requested_class
  ON requested_class.class_id = requested_method.class_id
JOIN method_definitions resolved_method
  ON resolved_method.method_id = mi.resolved_method_id
JOIN class_definitions resolved_class
  ON resolved_class.class_id = resolved_method.class_id;

-- ============================================================
-- 14. SAMPLE CLASS HIERARCHY
-- ============================================================

INSERT INTO class_definitions (
    class_name,
    parent_class_id,
    is_abstract,
    is_final,
    description
)
VALUES (
    'NotificationService',
    NULL,
    TRUE,
    FALSE,
    'Abstract notification service contract'
);

INSERT INTO class_definitions (
    class_name,
    parent_class_id,
    is_abstract,
    is_final,
    description
)
SELECT
    'EmailService',
    class_id,
    FALSE,
    FALSE,
    'Standard email delivery implementation'
FROM class_definitions
WHERE class_name = 'NotificationService';

INSERT INTO class_definitions (
    class_name,
    parent_class_id,
    is_abstract,
    is_final,
    description
)
SELECT
    'SmsService',
    class_id,
    FALSE,
    FALSE,
    'SMS delivery implementation'
FROM class_definitions
WHERE class_name = 'NotificationService';

INSERT INTO class_definitions (
    class_name,
    parent_class_id,
    is_abstract,
    is_final,
    description
)
SELECT
    'PriorityEmailService',
    class_id,
    FALSE,
    FALSE,
    'Priority email implementation extending EmailService'
FROM class_definitions
WHERE class_name = 'EmailService';

-- ============================================================
-- 15. SAMPLE METHOD DECLARATIONS
-- ============================================================

INSERT INTO method_definitions (
    class_id,
    method_name,
    method_signature,
    method_kind,
    return_type,
    access,
    is_abstract,
    implementation_description
)
SELECT
    class_id,
    'send',
    'send(NotificationRequest)',
    'INSTANCE',
    'DeliveryReceipt',
    'PUBLIC',
    TRUE,
    'Base notification delivery contract'
FROM class_definitions
WHERE class_name = 'NotificationService';

INSERT INTO method_definitions (
    class_id,
    method_name,
    method_signature,
    method_kind,
    return_type,
    access,
    implementation_description
)
SELECT
    class_id,
    'send',
    'send(NotificationRequest)',
    'INSTANCE',
    'DeliveryReceipt',
    'PUBLIC',
    'Deliver a standard email notification'
FROM class_definitions
WHERE class_name = 'EmailService';

INSERT INTO method_definitions (
    class_id,
    method_name,
    method_signature,
    method_kind,
    return_type,
    access,
    implementation_description
)
SELECT
    class_id,
    'send',
    'send(NotificationRequest)',
    'INSTANCE',
    'DeliveryReceipt',
    'PUBLIC',
    'Deliver an SMS notification'
FROM class_definitions
WHERE class_name = 'SmsService';

INSERT INTO method_definitions (
    class_id,
    method_name,
    method_signature,
    method_kind,
    return_type,
    access,
    implementation_description
)
SELECT
    class_id,
    'send',
    'send(NotificationRequest)',
    'INSTANCE',
    'DeliveryReceipt',
    'PUBLIC',
    'Deliver a priority email notification'
FROM class_definitions
WHERE class_name = 'PriorityEmailService';

-- ============================================================
-- 16. CONTRACT RECORDS
-- ============================================================

INSERT INTO method_contracts (
    method_id,
    parameter_count,
    parameter_signature,
    return_type,
    contract_description
)
SELECT
    method_id,
    1,
    'NotificationRequest',
    'DeliveryReceipt',
    'Accept one notification request and return a delivery receipt'
FROM method_definitions;

-- ============================================================
-- 17. OVERRIDE RELATIONSHIPS
-- ============================================================

INSERT INTO method_overrides (
    parent_method_id,
    overriding_method_id
)
SELECT
    parent_method.method_id,
    child_method.method_id
FROM method_definitions parent_method
JOIN class_definitions parent_class
  ON parent_class.class_id = parent_method.class_id
JOIN class_definitions child_class
  ON child_class.parent_class_id = parent_class.class_id
JOIN method_definitions child_method
  ON child_method.class_id = child_class.class_id
WHERE parent_class.class_name = 'NotificationService'
  AND parent_method.method_name = 'send'
  AND child_method.method_name = 'send';

-- PriorityEmailService overrides EmailService's implementation.
INSERT INTO method_overrides (
    parent_method_id,
    overriding_method_id
)
SELECT
    parent_method.method_id,
    child_method.method_id
FROM method_definitions parent_method
JOIN class_definitions parent_class
  ON parent_class.class_id = parent_method.class_id
JOIN class_definitions child_class
  ON child_class.parent_class_id = parent_class.class_id
JOIN method_definitions child_method
  ON child_method.class_id = child_class.class_id
WHERE parent_class.class_name = 'EmailService'
  AND parent_method.method_name = 'send'
  AND child_method.method_name = 'send';

-- ============================================================
-- 18. RUNTIME OBJECTS
-- ============================================================

INSERT INTO object_instances (
    object_name,
    class_id
)
SELECT
    'standard_email_instance',
    class_id
FROM class_definitions
WHERE class_name = 'EmailService';

INSERT INTO object_instances (
    object_name,
    class_id
)
SELECT
    'priority_email_instance',
    class_id
FROM class_definitions
WHERE class_name = 'PriorityEmailService';

INSERT INTO object_instances (
    object_name,
    class_id
)
SELECT
    'sms_instance',
    class_id
FROM class_definitions
WHERE class_name = 'SmsService';

-- ============================================================
-- 19. RUNTIME DISPATCH EXAMPLES
-- ============================================================

-- A reference to NotificationService.send is resolved against
-- the actual runtime object's class.

SELECT record_method_invocation(
    (
        SELECT object_id
        FROM object_instances
        WHERE object_name = 'standard_email_instance'
    ),
    (
        SELECT md.method_id
        FROM method_definitions md
        JOIN class_definitions cd
          ON cd.class_id = md.class_id
        WHERE cd.class_name = 'NotificationService'
          AND md.method_name = 'send'
    ),
    '{"recipient":"customer@example.com","status":"SENT"}'::JSONB
);

SELECT record_method_invocation(
    (
        SELECT object_id
        FROM object_instances
        WHERE object_name = 'priority_email_instance'
    ),
    (
        SELECT md.method_id
        FROM method_definitions md
        JOIN class_definitions cd
          ON cd.class_id = md.class_id
        WHERE cd.class_name = 'NotificationService'
          AND md.method_name = 'send'
    ),
    '{"recipient":"admin@example.com","priority":true}'::JSONB
);

SELECT record_method_invocation(
    (
        SELECT object_id
        FROM object_instances
        WHERE object_name = 'sms_instance'
    ),
    (
        SELECT md.method_id
        FROM method_definitions md
        JOIN class_definitions cd
          ON cd.class_id = md.class_id
        WHERE cd.class_name = 'NotificationService'
          AND md.method_name = 'send'
    ),
    '{"recipient":"+919876543210","status":"SENT"}'::JSONB
);

-- ============================================================
-- 20. RETRIEVAL: CLASS HIERARCHY
-- ============================================================

WITH RECURSIVE class_tree AS (
    SELECT
        class_id,
        class_name,
        parent_class_id,
        0 AS depth,
        class_name::TEXT AS hierarchy_path
    FROM class_definitions
    WHERE parent_class_id IS NULL

    UNION ALL

    SELECT
        child.class_id,
        child.class_name,
        child.parent_class_id,
        parent.depth + 1,
        parent.hierarchy_path || ' -> ' || child.class_name
    FROM class_definitions child
    JOIN class_tree parent
      ON child.parent_class_id = parent.class_id
)
SELECT *
FROM class_tree
ORDER BY hierarchy_path;

-- ============================================================
-- 21. RETRIEVAL: OVERRIDDEN METHODS
-- ============================================================

SELECT
    parent_class.class_name AS parent_class,
    parent_method.method_name,
    parent_method.method_signature,
    child_class.class_name AS overriding_class,
    child_method.return_type
FROM method_overrides mo
JOIN method_definitions parent_method
  ON parent_method.method_id = mo.parent_method_id
JOIN method_definitions child_method
  ON child_method.method_id = mo.overriding_method_id
JOIN class_definitions parent_class
  ON parent_class.class_id = parent_method.class_id
JOIN class_definitions child_class
  ON child_class.class_id = child_method.class_id
ORDER BY parent_class.class_name, child_class.class_name;

-- ============================================================
-- 22. EVALUATION: RUNTIME DISPATCH
-- ============================================================

SELECT
    object_name,
    runtime_class,
    requested_method_class,
    resolved_method_class,
    method_name,
    invocation_status
FROM override_execution_report
ORDER BY executed_at;

-- ============================================================
-- 23. AGGREGATION: INVOCATION COUNTS
-- ============================================================

SELECT
    resolved_method_class,
    method_signature,
    COUNT(*) AS invocation_count,
    COUNT(*) FILTER (
        WHERE invocation_status = 'SUCCESS'
    ) AS successful_invocations,
    COUNT(*) FILTER (
        WHERE invocation_status = 'FAILED'
    ) AS failed_invocations
FROM override_execution_report
GROUP BY
    resolved_method_class,
    method_signature
ORDER BY invocation_count DESC;

-- ============================================================
-- 24. VALIDATION: CONTRACT COMPATIBILITY
-- ============================================================

SELECT
    parent_method.method_name,
    parent_class.class_name AS parent_class,
    child_class.class_name AS child_class,
    parent_contract.parameter_signature AS parent_parameters,
    child_contract.parameter_signature AS child_parameters,
    parent_contract.return_type AS parent_return_type,
    child_contract.return_type AS child_return_type,
    (
        parent_contract.parameter_signature =
        child_contract.parameter_signature
        AND
        parent_contract.return_type =
        child_contract.return_type
    ) AS compatible
FROM method_overrides mo
JOIN method_definitions parent_method
  ON parent_method.method_id = mo.parent_method_id
JOIN method_definitions child_method
  ON child_method.method_id = mo.overriding_method_id
JOIN class_definitions parent_class
  ON parent_class.class_id = parent_method.class_id
JOIN class_definitions child_class
  ON child_class.class_id = child_method.class_id
JOIN method_contracts parent_contract
  ON parent_contract.method_id = parent_method.method_id
JOIN method_contracts child_contract
  ON child_contract.method_id = child_method.method_id;

-- ============================================================
-- 25. WORKFLOW: FAILED INVOCATION AUDIT
-- ============================================================

SELECT
    invocation_id,
    object_id,
    resolved_method_id,
    error_message,
    executed_at
FROM method_invocations
WHERE invocation_status IN ('FAILED', 'REJECTED')
ORDER BY executed_at DESC;

-- ============================================================
-- 26. REPORTING: OVERRIDE DEPTH
-- ============================================================

WITH RECURSIVE hierarchy AS (
    SELECT
        class_id,
        class_name,
        parent_class_id,
        0 AS depth
    FROM class_definitions
    WHERE parent_class_id IS NULL

    UNION ALL

    SELECT
        child.class_id,
        child.class_name,
        child.parent_class_id,
        parent.depth + 1
    FROM class_definitions child
    JOIN hierarchy parent
      ON child.parent_class_id = parent.class_id
)
SELECT
    class_name,
    depth,
    CASE
        WHEN depth = 0 THEN 'BASE CLASS'
        WHEN depth = 1 THEN 'DIRECT SUBCLASS'
        ELSE 'MULTILEVEL SUBCLASS'
    END AS inheritance_category
FROM hierarchy
ORDER BY depth, class_name;

-- ============================================================
-- 27. TRANSACTION AND ROLLBACK DEMONSTRATION
-- ============================================================

SAVEPOINT before_validation_example;

-- A deliberately invalid override is rejected by the trigger.
-- The nested block catches the expected exception so the
-- demonstration does not abort the complete script.

DO $$
DECLARE
    parent_id BIGINT;
    child_id BIGINT;
BEGIN
    SELECT method_id
    INTO parent_id
    FROM method_definitions
    WHERE method_signature = 'send(NotificationRequest)'
      AND class_id = (
          SELECT class_id
          FROM class_definitions
          WHERE class_name = 'NotificationService'
      );

    SELECT method_id
    INTO child_id
    FROM method_definitions
    WHERE method_signature = 'send(NotificationRequest)'
      AND class_id = (
          SELECT class_id
          FROM class_definitions
          WHERE class_name = 'SmsService'
      );

    BEGIN
        INSERT INTO method_overrides (
            parent_method_id,
            overriding_method_id
        )
        VALUES (
            child_id,
            parent_id
        );

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Invalid override rejected: %',
                SQLERRM;
    END;
END;
$$;

RELEASE SAVEPOINT before_validation_example;

-- ============================================================
-- 28. SECURITY AND OPERATIONAL CONSIDERATIONS
-- ============================================================

-- In production:
-- 1. Restrict writes to class and method metadata.
-- 2. Restrict invocation audit modification.
-- 3. Use database roles and least privilege.
-- 4. Avoid storing credentials or sensitive message contents
--    in execution_result.
-- 5. Use immutable audit records where required.
-- 6. Validate method contracts in the application runtime.
-- 7. Use concurrency controls when registering new metadata.
-- 8. Treat this registry as descriptive metadata, not as a
--    replacement for a programming language's virtual dispatch.

COMMIT;
