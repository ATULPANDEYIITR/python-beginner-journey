-- ============================================================
-- MULTIPLE INHERITANCE IN POSTGRESQL
--
-- PostgreSQL provides table inheritance, but table inheritance
-- is not equivalent to object-oriented multiple inheritance.
--
-- This implementation demonstrates:
-- 1. PostgreSQL table inheritance.
-- 2. Independent capability tables.
-- 3. Many-to-many capability composition.
-- 4. Interface-like behavior through relational design.
-- 5. Explicit conflict resolution.
-- 6. Diamond-shaped capability relationships.
-- 7. Constraint-based validation.
-- 8. Triggers and database functions.
-- 9. Transaction handling.
-- 10. Capability and permission evaluation.
--
-- PostgreSQL 15+
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS inheritance_lab;

SET search_path TO inheritance_lab, public;


-- ============================================================
-- 1. COMMON ENTITY TABLE
-- ============================================================

CREATE TABLE entity (
    entity_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_name VARCHAR(150) NOT NULL,
    entity_type VARCHAR(40) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT entity_name_not_empty
        CHECK (LENGTH(TRIM(entity_name)) > 0),

    CONSTRAINT entity_type_valid
        CHECK (
            entity_type IN (
                'DEVICE',
                'USER',
                'APPLICATION',
                'REPOSITORY'
            )
        )
);


-- ============================================================
-- 2. POSTGRESQL TABLE INHERITANCE
--
-- PostgreSQL child tables inherit columns and certain
-- constraints from their parent.
--
-- Parent primary-key and unique constraints are not
-- automatically enforced globally across inherited tables.
-- ============================================================

CREATE TABLE physical_device (
    manufacturer VARCHAR(100) NOT NULL,
    serial_number VARCHAR(100) NOT NULL
);

CREATE TABLE camera_device (
    camera_resolution VARCHAR(40) NOT NULL
) INHERITS (physical_device);

CREATE TABLE network_device (
    network_protocol VARCHAR(40) NOT NULL
) INHERITS (physical_device);

CREATE TABLE smart_camera (
    camera_resolution VARCHAR(40) NOT NULL,
    network_protocol VARCHAR(40) NOT NULL,
    manufacturer VARCHAR(100) NOT NULL,
    serial_number VARCHAR(100) NOT NULL,
    entity_id BIGINT NOT NULL REFERENCES entity(entity_id)
);


-- ============================================================
-- 3. CAPABILITY DEFINITIONS
-- ============================================================

CREATE TABLE capability (
    capability_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    capability_code VARCHAR(50) NOT NULL UNIQUE,
    capability_name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,

    CONSTRAINT capability_code_valid
        CHECK (capability_code ~ '^[A-Z][A-Z0-9_]*$')
);

INSERT INTO capability (
    capability_code,
    capability_name,
    description
)
VALUES
    (
        'LOGGING',
        'Logging',
        'Records application operations'
    ),
    (
        'VALIDATION',
        'Validation',
        'Validates input and business rules'
    ),
    (
        'READ',
        'Read',
        'Allows retrieval of records'
    ),
    (
        'WRITE',
        'Write',
        'Allows creation and modification of records'
    ),
    (
        'DELETE',
        'Delete',
        'Allows removal of records'
    ),
    (
        'AUTHENTICATION',
        'Authentication',
        'Verifies user identity'
    ),
    (
        'AUDIT',
        'Audit',
        'Maintains an audit history'
    ),
    (
        'EXPORT_CSV',
        'CSV Export',
        'Exports records in CSV format'
    ),
    (
        'EXPORT_JSON',
        'JSON Export',
        'Exports records in JSON format'
    );


-- ============================================================
-- 4. COMPOSABLE CAPABILITY RELATIONSHIPS
--
-- A class-like component may implement several capabilities.
-- The junction table models multiple inheritance of behavior.
-- ============================================================

CREATE TABLE application_component (
    component_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    component_name VARCHAR(120) NOT NULL UNIQUE,
    component_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    CONSTRAINT component_status_valid
        CHECK (
            component_status IN (
                'ACTIVE',
                'DISABLED',
                'DEPRECATED'
            )
        )
);

CREATE TABLE component_capability (
    component_id BIGINT NOT NULL
        REFERENCES application_component(component_id)
        ON DELETE CASCADE,

    capability_id BIGINT NOT NULL
        REFERENCES capability(capability_id),

    implementation_method VARCHAR(30) NOT NULL DEFAULT 'NATIVE',

    PRIMARY KEY (component_id, capability_id),

    CONSTRAINT implementation_method_valid
        CHECK (
            implementation_method IN (
                'NATIVE',
                'INHERITED',
                'DELEGATED'
            )
        )
);

CREATE INDEX idx_component_capability_capability
    ON component_capability(capability_id, component_id);


-- ============================================================
-- 5. DIAMOND-SHAPED CAPABILITY MODEL
--
-- SmartDevice combines Camera and NetworkAdapter capabilities.
-- Both can depend on the same Device capability.
-- ============================================================

CREATE TABLE capability_dependency (
    parent_capability_id BIGINT NOT NULL
        REFERENCES capability(capability_id),

    required_capability_id BIGINT NOT NULL
        REFERENCES capability(capability_id),

    PRIMARY KEY (
        parent_capability_id,
        required_capability_id
    ),

    CONSTRAINT no_direct_self_dependency
        CHECK (parent_capability_id <> required_capability_id)
);


-- ============================================================
-- 6. METHOD AND IMPLEMENTATION REGISTRY
--
-- Conflicts are explicit rather than resolved by row order.
-- ============================================================

CREATE TABLE component_method (
    method_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    component_id BIGINT NOT NULL
        REFERENCES application_component(component_id)
        ON DELETE CASCADE,

    method_name VARCHAR(100) NOT NULL,
    implementation_name VARCHAR(120) NOT NULL,
    precedence INTEGER NOT NULL DEFAULT 100,

    is_selected BOOLEAN NOT NULL DEFAULT FALSE,

    UNIQUE (component_id, method_name, implementation_name)
);

CREATE UNIQUE INDEX uq_selected_component_method
    ON component_method(component_id, method_name)
    WHERE is_selected;


-- ============================================================
-- 7. USERS AND SECURITY PERMISSIONS
-- ============================================================

CREATE TABLE app_user (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    account_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    CONSTRAINT account_status_valid
        CHECK (
            account_status IN (
                'ACTIVE',
                'SUSPENDED',
                'DISABLED'
            )
        )
);

CREATE TABLE permission (
    permission_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    permission_code VARCHAR(40) NOT NULL UNIQUE
);

INSERT INTO permission (permission_code)
VALUES
    ('READ'),
    ('WRITE'),
    ('DELETE'),
    ('DEPLOY');

CREATE TABLE user_permission (
    user_id BIGINT NOT NULL
        REFERENCES app_user(user_id)
        ON DELETE CASCADE,

    permission_id BIGINT NOT NULL
        REFERENCES permission(permission_id),

    granted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, permission_id)
);

CREATE INDEX idx_user_permission_permission
    ON user_permission(permission_id, user_id);


-- ============================================================
-- 8. COMPONENT ACCESS POLICIES
-- ============================================================

CREATE TABLE component_access_policy (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    component_id BIGINT NOT NULL
        REFERENCES application_component(component_id)
        ON DELETE CASCADE,

    permission_id BIGINT NOT NULL
        REFERENCES permission(permission_id),

    minimum_account_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    UNIQUE (component_id, permission_id),

    CHECK (minimum_account_status = 'ACTIVE')
);


-- ============================================================
-- 9. AUDIT HISTORY
-- ============================================================

CREATE TABLE audit_log (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    component_id BIGINT
        REFERENCES application_component(component_id),

    user_id BIGINT
        REFERENCES app_user(user_id),

    operation VARCHAR(100) NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,

    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_component_time
    ON audit_log(component_id, occurred_at DESC);


-- ============================================================
-- 10. VALIDATION FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_component_capability()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM application_component
        WHERE component_id = NEW.component_id
          AND component_status = 'ACTIVE'
    ) THEN
        RAISE EXCEPTION
            'Capabilities can only be assigned to active components';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_component_capability
BEFORE INSERT OR UPDATE ON component_capability
FOR EACH ROW
EXECUTE FUNCTION validate_component_capability();


-- ============================================================
-- 11. AUDIT TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION audit_capability_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    target_component BIGINT;
    operation_name TEXT;
BEGIN
    IF TG_OP = 'DELETE' THEN
        target_component := OLD.component_id;
        operation_name := 'CAPABILITY_REMOVED';
    ELSE
        target_component := NEW.component_id;
        operation_name := 'CAPABILITY_ASSIGNED';
    END IF;

    INSERT INTO audit_log (
        component_id,
        operation,
        details
    )
    VALUES (
        target_component,
        operation_name,
        jsonb_build_object(
            'table_name', TG_TABLE_NAME,
            'operation', TG_OP
        )
    );

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_audit_capability_change
AFTER INSERT OR UPDATE OR DELETE ON component_capability
FOR EACH ROW
EXECUTE FUNCTION audit_capability_change();


-- ============================================================
-- 12. METHOD CONFLICT RESOLUTION
-- ============================================================

CREATE OR REPLACE FUNCTION select_component_method(
    p_component_id BIGINT,
    p_method_name VARCHAR,
    p_implementation_name VARCHAR
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    affected_rows INTEGER;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM component_method
        WHERE component_id = p_component_id
          AND method_name = p_method_name
          AND implementation_name = p_implementation_name
    ) THEN
        RAISE EXCEPTION
            'Requested implementation does not exist';
    END IF;

    UPDATE component_method
    SET is_selected = FALSE
    WHERE component_id = p_component_id
      AND method_name = p_method_name;

    UPDATE component_method
    SET is_selected = TRUE
    WHERE component_id = p_component_id
      AND method_name = p_method_name
      AND implementation_name = p_implementation_name;

    GET DIAGNOSTICS affected_rows = ROW_COUNT;

    IF affected_rows <> 1 THEN
        RAISE EXCEPTION
            'Method resolution failed';
    END IF;
END;
$$;


-- ============================================================
-- 13. AUTHORIZATION FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION authorize_component_operation(
    p_user_id BIGINT,
    p_component_id BIGINT,
    p_permission_code VARCHAR
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    authorized BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1
        FROM app_user u
        JOIN user_permission up
            ON up.user_id = u.user_id
        JOIN permission p
            ON p.permission_id = up.permission_id
        JOIN component_access_policy cap
            ON cap.permission_id = p.permission_id
           AND cap.component_id = p_component_id
        JOIN application_component ac
            ON ac.component_id = cap.component_id
        WHERE u.user_id = p_user_id
          AND u.account_status = 'ACTIVE'
          AND ac.component_status = 'ACTIVE'
          AND p.permission_code = p_permission_code
    )
    INTO authorized;

    RETURN authorized;
END;
$$;


-- ============================================================
-- 14. COMPONENT CAPABILITY VIEW
-- ============================================================

CREATE OR REPLACE VIEW component_capability_view AS
SELECT
    ac.component_id,
    ac.component_name,
    ac.component_status,
    c.capability_code,
    c.capability_name,
    cc.implementation_method
FROM application_component ac
JOIN component_capability cc
    ON cc.component_id = ac.component_id
JOIN capability c
    ON c.capability_id = cc.capability_id;


-- ============================================================
-- 15. METHOD RESOLUTION VIEW
-- ============================================================

CREATE OR REPLACE VIEW selected_method_view AS
SELECT
    cm.component_id,
    ac.component_name,
    cm.method_name,
    cm.implementation_name,
    cm.precedence
FROM component_method cm
JOIN application_component ac
    ON ac.component_id = cm.component_id
WHERE cm.is_selected = TRUE;


-- ============================================================
-- 16. SAMPLE COMPONENTS
-- ============================================================

INSERT INTO application_component (
    component_name
)
VALUES
    ('RepositoryService'),
    ('SmartCamera'),
    ('EnterpriseWorkflow'),
    ('DataExporter'),
    ('DisabledComponent');


UPDATE application_component
SET component_status = 'DISABLED'
WHERE component_name = 'DisabledComponent';


-- ============================================================
-- 17. ASSIGN CAPABILITIES
-- ============================================================

INSERT INTO component_capability (
    component_id,
    capability_id,
    implementation_method
)
SELECT
    ac.component_id,
    c.capability_id,
    'NATIVE'
FROM application_component ac
CROSS JOIN capability c
WHERE
    (
        ac.component_name = 'RepositoryService'
        AND c.capability_code IN (
            'LOGGING',
            'VALIDATION',
            'READ',
            'WRITE',
            'AUDIT'
        )
    )
    OR
    (
        ac.component_name = 'SmartCamera'
        AND c.capability_code IN (
            'LOGGING',
            'AUTHENTICATION'
        )
    )
    OR
    (
        ac.component_name = 'EnterpriseWorkflow'
        AND c.capability_code IN (
            'AUTHENTICATION',
            'AUDIT',
            'VALIDATION'
        )
    )
    OR
    (
        ac.component_name = 'DataExporter'
        AND c.capability_code IN (
            'EXPORT_CSV',
            'EXPORT_JSON',
            'VALIDATION'
        )
    );


-- ============================================================
-- 18. CAPABILITY DEPENDENCIES
-- ============================================================

INSERT INTO capability_dependency (
    parent_capability_id,
    required_capability_id
)
SELECT
    parent.capability_id,
    required.capability_id
FROM capability parent
CROSS JOIN capability required
WHERE
    (
        parent.capability_code = 'WRITE'
        AND required.capability_code = 'VALIDATION'
    )
    OR
    (
        parent.capability_code = 'DELETE'
        AND required.capability_code = 'AUDIT'
    )
    OR
    (
        parent.capability_code = 'DEPLOY'
        AND required.capability_code = 'AUTHENTICATION'
    );


-- ============================================================
-- 19. REGISTER CONFLICTING METHODS
-- ============================================================

INSERT INTO component_method (
    component_id,
    method_name,
    implementation_name,
    precedence
)
SELECT
    ac.component_id,
    'export',
    implementation,
    priority
FROM application_component ac
CROSS JOIN (
    VALUES
        ('CSVExporter', 10),
        ('JSONExporter', 20)
) AS implementations(implementation, priority)
WHERE ac.component_name = 'DataExporter';


SELECT select_component_method(
    component_id,
    'export',
    'CSVExporter'
)
FROM application_component
WHERE component_name = 'DataExporter';


-- ============================================================
-- 20. USERS AND PERMISSIONS
-- ============================================================

INSERT INTO app_user (username, account_status)
VALUES
    ('release_admin', 'ACTIVE'),
    ('developer', 'ACTIVE'),
    ('suspended_user', 'SUSPENDED');

INSERT INTO user_permission (user_id, permission_id)
SELECT
    u.user_id,
    p.permission_id
FROM app_user u
CROSS JOIN permission p
WHERE
    (
        u.username = 'release_admin'
        AND p.permission_code IN (
            'READ',
            'WRITE',
            'DELETE',
            'DEPLOY'
        )
    )
    OR
    (
        u.username = 'developer'
        AND p.permission_code IN (
            'READ',
            'WRITE'
        )
    )
    OR
    (
        u.username = 'suspended_user'
        AND p.permission_code = 'READ'
    );


-- ============================================================
-- 21. ACCESS POLICY RECORDS
-- ============================================================

INSERT INTO component_access_policy (
    component_id,
    permission_id
)
SELECT
    ac.component_id,
    p.permission_id
FROM application_component ac
CROSS JOIN permission p
WHERE
    ac.component_name IN (
        'RepositoryService',
        'EnterpriseWorkflow'
    )
    AND p.permission_code IN ('READ', 'WRITE', 'DEPLOY');


-- ============================================================
-- 22. RECURSIVE CAPABILITY DEPENDENCY EVALUATION
-- ============================================================

WITH RECURSIVE capability_tree AS (
    SELECT
        capability_id AS root_capability,
        capability_id,
        0 AS depth,
        ARRAY[capability_id] AS path
    FROM capability

    UNION ALL

    SELECT
        ct.root_capability,
        cd.required_capability_id,
        ct.depth + 1,
        ct.path || cd.required_capability_id
    FROM capability_tree ct
    JOIN capability_dependency cd
        ON cd.parent_capability_id = ct.capability_id
    WHERE NOT cd.required_capability_id = ANY(ct.path)
)
SELECT
    root.capability_code AS root_capability,
    dependency.capability_code AS required_capability,
    ct.depth
FROM capability_tree ct
JOIN capability root
    ON root.capability_id = ct.root_capability
JOIN capability dependency
    ON dependency.capability_id = ct.capability_id
WHERE ct.depth > 0
ORDER BY root.capability_code, ct.depth;


-- ============================================================
-- 23. RETRIEVE ALL COMPONENT CAPABILITIES
-- ============================================================

SELECT
    component_name,
    capability_name,
    implementation_method
FROM component_capability_view
ORDER BY component_name, capability_name;


-- ============================================================
-- 24. METHOD CONFLICT REPORT
-- ============================================================

SELECT
    component_name,
    method_name,
    COUNT(*) AS implementation_count,
    ARRAY_AGG(implementation_name ORDER BY precedence)
        AS available_implementations
FROM component_method
GROUP BY component_id, component_name, method_name
HAVING COUNT(*) > 1;


-- ============================================================
-- 25. METHOD RESOLUTION REPORT
-- ============================================================

SELECT *
FROM selected_method_view;


-- ============================================================
-- 26. VALIDATION REPORT
-- ============================================================

SELECT
    ac.component_name,
    c.capability_code,
    CASE
        WHEN ac.component_status <> 'ACTIVE'
            THEN 'COMPONENT_INACTIVE'
        WHEN cc.component_id IS NULL
            THEN 'CAPABILITY_MISSING'
        ELSE 'VALID'
    END AS validation_result
FROM application_component ac
CROSS JOIN capability c
LEFT JOIN component_capability cc
    ON cc.component_id = ac.component_id
   AND cc.capability_id = c.capability_id
ORDER BY ac.component_name, c.capability_code;


-- ============================================================
-- 27. AUTHORIZATION EVALUATION
-- ============================================================

SELECT
    u.username,
    ac.component_name,
    p.permission_code,
    authorize_component_operation(
        u.user_id,
        ac.component_id,
        p.permission_code
    ) AS authorized
FROM app_user u
CROSS JOIN application_component ac
CROSS JOIN permission p
WHERE u.username IN (
    'release_admin',
    'developer',
    'suspended_user'
)
AND ac.component_name IN (
    'RepositoryService',
    'EnterpriseWorkflow'
)
AND p.permission_code IN ('READ', 'WRITE', 'DEPLOY')
ORDER BY u.username, ac.component_name, p.permission_code;


-- ============================================================
-- 28. AGGREGATION AND GOVERNANCE REPORT
-- ============================================================

SELECT
    ac.component_name,
    COUNT(cc.capability_id) AS capability_count,
    COUNT(DISTINCT cap.permission_id) AS policy_count,
    ac.component_status
FROM application_component ac
LEFT JOIN component_capability cc
    ON cc.component_id = ac.component_id
LEFT JOIN component_access_policy cap
    ON cap.component_id = ac.component_id
GROUP BY
    ac.component_id,
    ac.component_name,
    ac.component_status
ORDER BY ac.component_name;


-- ============================================================
-- 29. FAILURE CASE: DISABLED COMPONENT
--
-- Expected to raise an exception.
-- Run separately when testing the trigger.
-- ============================================================

-- INSERT INTO component_capability (
--     component_id,
--     capability_id
-- )
-- SELECT
--     ac.component_id,
--     c.capability_id
-- FROM application_component ac
-- CROSS JOIN capability c
-- WHERE ac.component_name = 'DisabledComponent'
--   AND c.capability_code = 'READ';


-- ============================================================
-- 30. FAILURE CASE: MISSING METHOD IMPLEMENTATION
--
-- Expected to raise an exception.
-- Run separately when testing the function.
-- ============================================================

-- SELECT select_component_method(
--     (
--         SELECT component_id
--         FROM application_component
--         WHERE component_name = 'DataExporter'
--     ),
--     'export',
--     'XMLExporter'
-- );


-- ============================================================
-- 31. TRANSACTIONAL METHOD RESOLUTION
-- ============================================================

SAVEPOINT before_method_change;

SELECT select_component_method(
    (
        SELECT component_id
        FROM application_component
        WHERE component_name = 'DataExporter'
    ),
    'export',
    'JSONExporter'
);

-- Verify the selected implementation within the transaction.
SELECT *
FROM selected_method_view
WHERE component_name = 'DataExporter';

-- Restore the original selection for the demonstration.
ROLLBACK TO SAVEPOINT before_method_change;


-- ============================================================
-- 32. AUDIT REPORT
-- ============================================================

SELECT
    al.audit_id,
    ac.component_name,
    al.operation,
    al.details,
    al.occurred_at
FROM audit_log al
LEFT JOIN application_component ac
    ON ac.component_id = al.component_id
ORDER BY al.occurred_at DESC, al.audit_id DESC;


-- ============================================================
-- 33. QUERY PERFORMANCE
-- ============================================================

ANALYZE entity;
ANALYZE capability;
ANALYZE application_component;
ANALYZE component_capability;
ANALYZE component_method;
ANALYZE app_user;
ANALYZE user_permission;
ANALYZE component_access_policy;
ANALYZE audit_log;

-- Example query for execution-plan inspection:
EXPLAIN
SELECT
    ac.component_name,
    c.capability_code
FROM application_component ac
JOIN component_capability cc
    ON cc.component_id = ac.component_id
JOIN capability c
    ON c.capability_id = cc.capability_id
WHERE ac.component_name = 'RepositoryService';


COMMIT;

-- ============================================================
-- END OF MULTIPLE INHERITANCE DATABASE MODEL
-- ============================================================
