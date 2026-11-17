-- ============================================================
-- THE __init__() METHOD
-- PostgreSQL object initialization and relational workflows
--
-- PostgreSQL does not implement Python's __init__().
-- Equivalent initialization responsibilities can be modeled
-- using:
--   1. Column defaults
--   2. NOT NULL and CHECK constraints
--   3. BEFORE INSERT triggers
--   4. Database functions
--   5. Identity columns
--   6. Transactional initialization
--
-- This database models an enterprise asset-registration system.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS initialization_lab;

SET search_path TO initialization_lab, public;

-- ============================================================
-- 1. ENUM TYPES
-- ============================================================

CREATE TYPE asset_status AS ENUM (
    'created',
    'validated',
    'active',
    'suspended',
    'retired'
);

CREATE TYPE initialization_source AS ENUM (
    'manual',
    'api',
    'import'
);

CREATE TYPE initialization_event_type AS ENUM (
    'created',
    'validated',
    'activated',
    'suspended',
    'rejected'
);

-- ============================================================
-- 2. ORGANIZATIONS
-- ============================================================

CREATE TABLE organizations (
    organization_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    organization_name VARCHAR(150) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT organization_name_not_empty
        CHECK (length(trim(organization_name)) > 0),

    CONSTRAINT organization_name_unique
        UNIQUE (organization_name)
);

INSERT INTO organizations (organization_name)
VALUES
    ('Research Laboratory'),
    ('Enterprise Security Division');

-- ============================================================
-- 3. ASSET CATEGORIES
-- ============================================================

CREATE TABLE asset_categories (
    category_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    category_name VARCHAR(100) NOT NULL UNIQUE,

    CONSTRAINT category_name_not_empty
        CHECK (length(trim(category_name)) > 0)
);

INSERT INTO asset_categories (category_name)
VALUES
    ('Computing'),
    ('Networking'),
    ('Security Equipment'),
    ('Research Equipment');

-- ============================================================
-- 4. ASSET TABLE
-- Constructor-like initialization is represented by defaults,
-- constraints and a trigger.
-- ============================================================

CREATE TABLE assets (
    asset_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    asset_code VARCHAR(40) NOT NULL UNIQUE,

    asset_name VARCHAR(150) NOT NULL,

    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),

    category_id BIGINT NOT NULL
        REFERENCES asset_categories(category_id),

    purchase_cost NUMERIC(14, 2) NOT NULL DEFAULT 0,

    status asset_status NOT NULL DEFAULT 'created',

    source initialization_source NOT NULL DEFAULT 'manual',

    configuration JSONB NOT NULL DEFAULT '{}'::JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    validated_at TIMESTAMPTZ,

    CONSTRAINT asset_code_not_empty
        CHECK (length(trim(asset_code)) > 0),

    CONSTRAINT asset_name_not_empty
        CHECK (length(trim(asset_name)) > 0),

    CONSTRAINT valid_purchase_cost
        CHECK (purchase_cost >= 0),

    CONSTRAINT configuration_must_be_object
        CHECK (jsonb_typeof(configuration) = 'object'),

    CONSTRAINT validation_timestamp_consistency
        CHECK (
            (status IN ('created', 'suspended', 'retired'))
            OR validated_at IS NOT NULL
        )
);

-- ============================================================
-- 5. USERS AND REVIEWER ROLES
-- ============================================================

CREATE TABLE system_users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),

    username VARCHAR(100) NOT NULL UNIQUE,

    role VARCHAR(30) NOT NULL,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_user_role
        CHECK (
            role IN (
                'administrator',
                'asset_manager',
                'auditor',
                'operator'
            )
        ),

    CONSTRAINT username_not_empty
        CHECK (length(trim(username)) > 0)
);

INSERT INTO system_users (
    organization_id,
    username,
    role
)
SELECT organization_id, 'admin_lab', 'administrator'
FROM organizations
WHERE organization_name = 'Research Laboratory';

INSERT INTO system_users (
    organization_id,
    username,
    role
)
SELECT organization_id, 'asset_operator', 'operator'
FROM organizations
WHERE organization_name = 'Research Laboratory';

INSERT INTO system_users (
    organization_id,
    username,
    role
)
SELECT organization_id, 'security_auditor', 'auditor'
FROM organizations
WHERE organization_name = 'Enterprise Security Division';

-- ============================================================
-- 6. INITIALIZATION AUDIT
-- Every successful asset insertion is recorded.
-- ============================================================

CREATE TABLE initialization_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    asset_id BIGINT NOT NULL
        REFERENCES assets(asset_id),

    event_type initialization_event_type NOT NULL,

    performed_by BIGINT
        REFERENCES system_users(user_id),

    details JSONB NOT NULL DEFAULT '{}'::JSONB,

    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT audit_details_object
        CHECK (jsonb_typeof(details) = 'object')
);

-- ============================================================
-- 7. INITIALIZATION TRIGGER
--
-- A BEFORE INSERT trigger applies initialization rules.
-- It also normalizes strings and maintains timestamps.
-- ============================================================

CREATE OR REPLACE FUNCTION initialize_asset()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.asset_code := upper(trim(NEW.asset_code));
    NEW.asset_name := trim(NEW.asset_name);

    IF NEW.asset_code = '' OR NEW.asset_name = '' THEN
        RAISE EXCEPTION
            'Asset code and name are required.';
    END IF;

    IF NEW.purchase_cost < 0 THEN
        RAISE EXCEPTION
            'Purchase cost cannot be negative.';
    END IF;

    IF NEW.configuration IS NULL THEN
        NEW.configuration := '{}'::JSONB;
    END IF;

    NEW.created_at := COALESCE(
        NEW.created_at,
        CURRENT_TIMESTAMP
    );

    NEW.updated_at := CURRENT_TIMESTAMP;

    IF NEW.status = 'active' AND NEW.validated_at IS NULL THEN
        RAISE EXCEPTION
            'An asset must be validated before activation.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER before_asset_initialization
BEFORE INSERT ON assets
FOR EACH ROW
EXECUTE FUNCTION initialize_asset();

-- ============================================================
-- 8. AUDIT TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION audit_asset_initialization()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO initialization_audit (
        asset_id,
        event_type,
        details
    )
    VALUES (
        NEW.asset_id,
        'created',
        jsonb_build_object(
            'asset_code', NEW.asset_code,
            'source', NEW.source,
            'status', NEW.status
        )
    );

    RETURN NEW;
END;
$$;

CREATE TRIGGER after_asset_initialization
AFTER INSERT ON assets
FOR EACH ROW
EXECUTE FUNCTION audit_asset_initialization();

-- ============================================================
-- 9. ASSET CREATION FUNCTION
--
-- Centralized factory-like database function.
-- The function delegates final integrity enforcement to
-- constraints and triggers.
-- ============================================================

CREATE OR REPLACE FUNCTION create_asset(
    p_asset_code VARCHAR,
    p_asset_name VARCHAR,
    p_organization_id BIGINT,
    p_category_id BIGINT,
    p_purchase_cost NUMERIC DEFAULT 0,
    p_source initialization_source DEFAULT 'manual',
    p_configuration JSONB DEFAULT '{}'::JSONB
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_asset_id BIGINT;
BEGIN
    IF p_asset_code IS NULL OR trim(p_asset_code) = '' THEN
        RAISE EXCEPTION 'Asset code is required.';
    END IF;

    IF p_asset_name IS NULL OR trim(p_asset_name) = '' THEN
        RAISE EXCEPTION 'Asset name is required.';
    END IF;

    IF p_purchase_cost IS NULL OR p_purchase_cost < 0 THEN
        RAISE EXCEPTION 'Invalid purchase cost.';
    END IF;

    IF p_configuration IS NULL
       OR jsonb_typeof(p_configuration) <> 'object' THEN
        RAISE EXCEPTION 'Configuration must be a JSON object.';
    END IF;

    INSERT INTO assets (
        asset_code,
        asset_name,
        organization_id,
        category_id,
        purchase_cost,
        source,
        configuration
    )
    VALUES (
        p_asset_code,
        p_asset_name,
        p_organization_id,
        p_category_id,
        p_purchase_cost,
        p_source,
        p_configuration
    )
    RETURNING asset_id INTO v_asset_id;

    RETURN v_asset_id;
END;
$$;

-- ============================================================
-- 10. ASSET VALIDATION FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_asset(
    p_asset_id BIGINT,
    p_user_id BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_role VARCHAR(30);
    v_user_org BIGINT;
    v_asset_org BIGINT;
    v_status asset_status;
BEGIN
    SELECT role, organization_id
    INTO v_role, v_user_org
    FROM system_users
    WHERE user_id = p_user_id
      AND active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Active user not found.';
    END IF;

    IF v_role NOT IN ('administrator', 'asset_manager') THEN
        RAISE EXCEPTION 'User is not authorized to validate assets.';
    END IF;

    SELECT organization_id, status
    INTO v_asset_org, v_status
    FROM assets
    WHERE asset_id = p_asset_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Asset not found.';
    END IF;

    IF v_asset_org <> v_user_org THEN
        RAISE EXCEPTION 'Cross-organization validation is prohibited.';
    END IF;

    IF v_status <> 'created' THEN
        RAISE EXCEPTION 'Only newly created assets can be validated.';
    END IF;

    UPDATE assets
    SET
        status = 'validated',
        validated_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE asset_id = p_asset_id;

    INSERT INTO initialization_audit (
        asset_id,
        event_type,
        performed_by,
        details
    )
    VALUES (
        p_asset_id,
        'validated',
        p_user_id,
        '{"validation":"passed"}'::JSONB
    );
END;
$$;

-- ============================================================
-- 11. ACTIVATION PROCEDURE
-- ============================================================

CREATE OR REPLACE PROCEDURE activate_asset(
    p_asset_id BIGINT,
    p_user_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_asset_org BIGINT;
    v_user_org BIGINT;
    v_role VARCHAR(30);
    v_status asset_status;
BEGIN
    SELECT organization_id, status
    INTO v_asset_org, v_status
    FROM assets
    WHERE asset_id = p_asset_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Asset not found.';
    END IF;

    SELECT organization_id, role
    INTO v_user_org, v_role
    FROM system_users
    WHERE user_id = p_user_id
      AND active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Active user not found.';
    END IF;

    IF v_asset_org <> v_user_org THEN
        RAISE EXCEPTION 'Organization mismatch.';
    END IF;

    IF v_role NOT IN ('administrator', 'asset_manager') THEN
        RAISE EXCEPTION 'Insufficient activation privileges.';
    END IF;

    IF v_status <> 'validated' THEN
        RAISE EXCEPTION 'Asset must be validated before activation.';
    END IF;

    UPDATE assets
    SET
        status = 'active',
        updated_at = CURRENT_TIMESTAMP
    WHERE asset_id = p_asset_id;

    INSERT INTO initialization_audit (
        asset_id,
        event_type,
        performed_by,
        details
    )
    VALUES (
        p_asset_id,
        'activated',
        p_user_id,
        '{"activation":"successful"}'::JSONB
    );
END;
$$;

-- ============================================================
-- 12. PERFORMANCE INDEXES
-- ============================================================

CREATE INDEX idx_assets_organization_status
    ON assets (organization_id, status);

CREATE INDEX idx_assets_category
    ON assets (category_id);

CREATE INDEX idx_assets_created_at
    ON assets (created_at DESC);

CREATE INDEX idx_assets_configuration
    ON assets USING GIN (configuration);

CREATE INDEX idx_initialization_audit_asset_time
    ON initialization_audit (asset_id, occurred_at DESC);

CREATE INDEX idx_system_users_organization_role
    ON system_users (organization_id, role)
    WHERE active = TRUE;

-- ============================================================
-- 13. SAMPLE ASSET INITIALIZATION
-- ============================================================

SELECT create_asset(
    'asset-001',
    'Research Workstation',
    (
        SELECT organization_id
        FROM organizations
        WHERE organization_name = 'Research Laboratory'
    ),
    (
        SELECT category_id
        FROM asset_categories
        WHERE category_name = 'Computing'
    ),
    85000.00,
    'manual',
    '{"processor":"64-core","memory_gb":128}'::JSONB
);

SELECT create_asset(
    'asset-002',
    'Network Firewall',
    (
        SELECT organization_id
        FROM organizations
        WHERE organization_name = 'Research Laboratory'
    ),
    (
        SELECT category_id
        FROM asset_categories
        WHERE category_name = 'Networking'
    ),
    120000.00,
    'api',
    '{"vendor":"Enterprise","encrypted":true}'::JSONB
);

SELECT create_asset(
    'asset-003',
    'Security Monitoring Sensor',
    (
        SELECT organization_id
        FROM organizations
        WHERE organization_name = 'Enterprise Security Division'
    ),
    (
        SELECT category_id
        FROM asset_categories
        WHERE category_name = 'Security Equipment'
    ),
    45000.00,
    'import',
    '{"network_enabled":true,"monitoring":true}'::JSONB
);

-- ============================================================
-- 14. VALIDATION AND ACTIVATION WORKFLOW
-- ============================================================

DO $$
DECLARE
    v_asset_id BIGINT;
    v_user_id BIGINT;
BEGIN
    SELECT asset_id
    INTO v_asset_id
    FROM assets
    WHERE asset_code = 'ASSET-001';

    SELECT user_id
    INTO v_user_id
    FROM system_users
    WHERE username = 'admin_lab';

    PERFORM validate_asset(v_asset_id, v_user_id);

    CALL activate_asset(v_asset_id, v_user_id);
END;
$$;

-- ============================================================
-- 15. TRANSACTIONAL FAILURE HANDLING
-- An invalid operation is isolated by a savepoint.
-- ============================================================

SAVEPOINT invalid_initialization_test;

DO $$
BEGIN
    BEGIN
        PERFORM create_asset(
            'asset-invalid',
            'Invalid Asset',
            1,
            1,
            -500,
            'manual',
            '{}'::JSONB
        );

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Initialization rejected: %', SQLERRM;
    END;
END;
$$;

RELEASE SAVEPOINT invalid_initialization_test;

-- ============================================================
-- 16. RETRIEVAL VIEW
-- ============================================================

CREATE OR REPLACE VIEW asset_initialization_report AS
SELECT
    a.asset_id,
    a.asset_code,
    a.asset_name,
    o.organization_name,
    c.category_name,
    a.purchase_cost,
    a.status,
    a.source,
    a.created_at,
    a.validated_at,
    a.configuration
FROM assets a
JOIN organizations o
    ON o.organization_id = a.organization_id
JOIN asset_categories c
    ON c.category_id = a.category_id;

-- ============================================================
-- 17. INITIALIZATION ELIGIBILITY VIEW
-- ============================================================

CREATE OR REPLACE VIEW asset_eligibility_report AS
SELECT
    asset_id,
    asset_code,
    asset_name,
    status,
    CASE
        WHEN status = 'created'
            THEN 'Eligible for validation'
        WHEN status = 'validated'
            THEN 'Eligible for activation'
        WHEN status = 'active'
            THEN 'Already active'
        WHEN status = 'suspended'
            THEN 'Suspended'
        ELSE 'Retired'
    END AS eligibility
FROM assets;

-- ============================================================
-- 18. RETRIEVAL
-- ============================================================

SELECT *
FROM asset_initialization_report
ORDER BY asset_id;

-- ============================================================
-- 19. VALIDATION REPORT
-- ============================================================

SELECT
    asset_code,
    asset_name,
    purchase_cost,
    status,
    validated_at,
    CASE
        WHEN purchase_cost < 0 THEN 'Invalid cost'
        WHEN status = 'active' AND validated_at IS NULL
            THEN 'Missing validation'
        ELSE 'Valid'
    END AS validation_result
FROM assets;

-- ============================================================
-- 20. AGGREGATION
-- ============================================================

SELECT
    o.organization_name,
    a.status,
    COUNT(*) AS asset_count,
    SUM(a.purchase_cost) AS total_purchase_cost,
    AVG(a.purchase_cost) AS average_purchase_cost
FROM assets a
JOIN organizations o
    ON o.organization_id = a.organization_id
GROUP BY
    o.organization_name,
    a.status
ORDER BY
    o.organization_name,
    a.status;

-- ============================================================
-- 21. WORKFLOW HISTORY
-- ============================================================

SELECT
    a.asset_code,
    h.event_type,
    u.username,
    h.occurred_at,
    h.details
FROM initialization_audit h
JOIN assets a
    ON a.asset_id = h.asset_id
LEFT JOIN system_users u
    ON u.user_id = h.performed_by
ORDER BY h.occurred_at, h.audit_id;

-- ============================================================
-- 22. CTE: INITIALIZATION PERFORMANCE ANALYSIS
-- ============================================================

WITH initialization_metrics AS (
    SELECT
        organization_id,
        COUNT(*) AS total_assets,
        COUNT(*) FILTER (
            WHERE status = 'active'
        ) AS active_assets,
        COUNT(*) FILTER (
            WHERE status = 'created'
        ) AS pending_assets,
        AVG(
            EXTRACT(EPOCH FROM (updated_at - created_at))
        ) AS average_elapsed_seconds
    FROM assets
    GROUP BY organization_id
)
SELECT
    o.organization_name,
    m.total_assets,
    m.active_assets,
    m.pending_assets,
    ROUND(m.average_elapsed_seconds::NUMERIC, 2)
        AS average_elapsed_seconds
FROM initialization_metrics m
JOIN organizations o
    ON o.organization_id = m.organization_id;

-- ============================================================
-- 23. CONFIGURATION SEARCH
-- ============================================================

SELECT
    asset_code,
    configuration
FROM assets
WHERE configuration @> '{"encrypted":true}'::JSONB;

-- ============================================================
-- 24. DATABASE INTEGRITY CHECK
-- ============================================================

SELECT
    COUNT(*) AS total_assets,
    COUNT(*) FILTER (
        WHERE asset_code IS NULL OR asset_name IS NULL
    ) AS incomplete_assets,
    COUNT(*) FILTER (
        WHERE purchase_cost < 0
    ) AS invalid_cost_assets,
    COUNT(*) FILTER (
        WHERE status = 'active' AND validated_at IS NULL
    ) AS invalid_active_assets
FROM assets;

-- ============================================================
-- 25. EXPLICIT TRANSACTION DEMONSTRATION
-- ============================================================

SAVEPOINT transaction_demo;

UPDATE assets
SET
    configuration = configuration ||
        '{"initialization_checked":true}'::JSONB,
    updated_at = CURRENT_TIMESTAMP
WHERE asset_code = 'ASSET-001';

-- Retain the valid configuration update.
RELEASE SAVEPOINT transaction_demo;

COMMIT;

-- ============================================================
-- 26. FINAL VERIFICATION
-- ============================================================

SELECT
    asset_code,
    status,
    configuration
FROM assets
ORDER BY asset_code;

SELECT
    event_type,
    COUNT(*) AS event_count
FROM initialization_audit
GROUP BY event_type
ORDER BY event_type;
