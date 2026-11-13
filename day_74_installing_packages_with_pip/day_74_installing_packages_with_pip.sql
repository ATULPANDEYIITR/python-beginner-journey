-- ============================================================
-- INSTALLING PYTHON PACKAGES WITH PIP
-- PostgreSQL package management and governance database
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS pip_governance;

SET search_path TO pip_governance, public;

-- ============================================================
-- 1. DOMAIN TYPES
-- ============================================================

CREATE TYPE package_status AS ENUM (
    'AVAILABLE',
    'VALIDATED',
    'APPROVED',
    'INSTALLING',
    'INSTALLED',
    'FAILED',
    'BLOCKED'
);

CREATE TYPE installation_status AS ENUM (
    'REQUESTED',
    'VALIDATING',
    'APPROVED',
    'INSTALLING',
    'SUCCEEDED',
    'FAILED',
    'REJECTED',
    'CANCELLED'
);

CREATE TYPE package_risk AS ENUM (
    'LOW',
    'MEDIUM',
    'HIGH',
    'CRITICAL'
);

CREATE TYPE operation_type AS ENUM (
    'INSTALL',
    'UPGRADE',
    'REMOVE'
);

-- ============================================================
-- 2. ORGANIZATIONS AND USERS
-- ============================================================

CREATE TABLE organizations (
    organization_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    organization_name VARCHAR(150) NOT NULL UNIQUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),

    username VARCHAR(100) NOT NULL,

    role VARCHAR(40) NOT NULL
        CHECK (
            role IN (
                'DEVELOPER',
                'BUILD_ENGINEER',
                'SECURITY_ADMIN',
                'RELEASE_MANAGER'
            )
        ),

    active BOOLEAN NOT NULL DEFAULT TRUE,

    UNIQUE (organization_id, username)
);

-- ============================================================
-- 3. PACKAGE INDEX REGISTRY
-- ============================================================

CREATE TABLE package_indexes (
    index_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    index_name VARCHAR(100) NOT NULL UNIQUE,

    index_url TEXT NOT NULL UNIQUE,

    trusted BOOLEAN NOT NULL DEFAULT FALSE,

    enabled BOOLEAN NOT NULL DEFAULT TRUE,

    CHECK (index_url LIKE 'https://%')
);

INSERT INTO package_indexes (
    index_name,
    index_url,
    trusted,
    enabled
)
VALUES
(
    'PyPI',
    'https://pypi.org/simple',
    TRUE,
    TRUE
),
(
    'Internal Python Repository',
    'https://packages.example.internal/simple',
    TRUE,
    TRUE
),
(
    'Unapproved External Repository',
    'https://untrusted.example.org/simple',
    FALSE,
    FALSE
);

-- ============================================================
-- 4. PACKAGE CATALOG
-- ============================================================

CREATE TABLE packages (
    package_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    package_name VARCHAR(200) NOT NULL,

    normalized_name VARCHAR(200) NOT NULL UNIQUE,

    description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (
        normalized_name ~ '^[a-z0-9]+([._-][a-z0-9]+)*$'
    )
);

CREATE TABLE package_versions (
    package_version_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    package_id BIGINT NOT NULL
        REFERENCES packages(package_id),

    version VARCHAR(100) NOT NULL,

    index_id BIGINT NOT NULL
        REFERENCES package_indexes(index_id),

    sha256 CHAR(64),

    risk package_risk NOT NULL DEFAULT 'LOW',

    status package_status NOT NULL DEFAULT 'AVAILABLE',

    published_at TIMESTAMPTZ,

    UNIQUE (package_id, version),

    CHECK (
        sha256 IS NULL OR sha256 ~ '^[a-fA-F0-9]{64}$'
    )
);

-- ============================================================
-- 5. PACKAGE DEPENDENCIES
-- ============================================================

CREATE TABLE package_dependencies (
    dependency_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    package_version_id BIGINT NOT NULL
        REFERENCES package_versions(package_version_id)
        ON DELETE CASCADE,

    required_package_id BIGINT NOT NULL
        REFERENCES packages(package_id),

    minimum_version VARCHAR(100),

    maximum_version VARCHAR(100),

    UNIQUE (
        package_version_id,
        required_package_id
    ),

    CHECK (
        minimum_version IS NULL OR
        minimum_version <> ''
    ),

    CHECK (
        maximum_version IS NULL OR
        maximum_version <> ''
    )
);

CREATE INDEX idx_dependencies_parent
ON package_dependencies(package_version_id);

CREATE INDEX idx_dependencies_child
ON package_dependencies(required_package_id);

-- ============================================================
-- 6. COMPUTING ENVIRONMENTS
-- ============================================================

CREATE TABLE environments (
    environment_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),

    environment_name VARCHAR(150) NOT NULL,

    python_version VARCHAR(30) NOT NULL,

    operating_system VARCHAR(100) NOT NULL,

    environment_type VARCHAR(30) NOT NULL
        CHECK (
            environment_type IN (
                'DEVELOPMENT',
                'TEST',
                'STAGING',
                'PRODUCTION'
            )
        ),

    virtual_environment BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (
        organization_id,
        environment_name
    )
);

-- ============================================================
-- 7. ENVIRONMENT PACKAGE STATE
-- ============================================================

CREATE TABLE environment_packages (
    environment_package_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    environment_id BIGINT NOT NULL
        REFERENCES environments(environment_id),

    package_id BIGINT NOT NULL
        REFERENCES packages(package_id),

    package_version_id BIGINT NOT NULL
        REFERENCES package_versions(package_version_id),

    installed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    installed_by BIGINT
        REFERENCES users(user_id),

    UNIQUE (
        environment_id,
        package_id
    )
);

CREATE INDEX idx_environment_packages_environment
ON environment_packages(environment_id);

CREATE INDEX idx_environment_packages_version
ON environment_packages(package_version_id);

-- ============================================================
-- 8. INSTALLATION REQUESTS
-- ============================================================

CREATE TABLE installation_requests (
    request_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    environment_id BIGINT NOT NULL
        REFERENCES environments(environment_id),

    requested_by BIGINT NOT NULL
        REFERENCES users(user_id),

    operation operation_type NOT NULL,

    status installation_status NOT NULL DEFAULT 'REQUESTED',

    dry_run BOOLEAN NOT NULL DEFAULT TRUE,

    requirements_file TEXT,

    requested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMPTZ,

    error_message TEXT,

    CHECK (
        completed_at IS NULL OR completed_at >= requested_at
    )
);

CREATE INDEX idx_installation_requests_status
ON installation_requests(status, requested_at DESC);

CREATE INDEX idx_installation_requests_environment
ON installation_requests(environment_id, requested_at DESC);

CREATE TABLE installation_request_items (
    request_item_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    request_id BIGINT NOT NULL
        REFERENCES installation_requests(request_id)
        ON DELETE CASCADE,

    package_id BIGINT NOT NULL
        REFERENCES packages(package_id),

    requested_version VARCHAR(100),

    resolved_version_id BIGINT
        REFERENCES package_versions(package_version_id),

    UNIQUE(request_id, package_id)
);

-- ============================================================
-- 9. GOVERNANCE POLICIES
-- ============================================================

CREATE TABLE installation_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),

    policy_name VARCHAR(150) NOT NULL,

    require_pinned_version BOOLEAN NOT NULL DEFAULT TRUE,

    require_hash BOOLEAN NOT NULL DEFAULT FALSE,

    allow_upgrade BOOLEAN NOT NULL DEFAULT FALSE,

    allow_global_install BOOLEAN NOT NULL DEFAULT FALSE,

    maximum_risk package_risk NOT NULL DEFAULT 'MEDIUM',

    enabled BOOLEAN NOT NULL DEFAULT TRUE,

    UNIQUE (
        organization_id,
        policy_name
    )
);

CREATE TABLE policy_allowed_indexes (
    policy_id BIGINT NOT NULL
        REFERENCES installation_policies(policy_id)
        ON DELETE CASCADE,

    index_id BIGINT NOT NULL
        REFERENCES package_indexes(index_id),

    PRIMARY KEY(policy_id, index_id)
);

CREATE TABLE policy_denied_packages (
    policy_id BIGINT NOT NULL
        REFERENCES installation_policies(policy_id)
        ON DELETE CASCADE,

    package_id BIGINT NOT NULL
        REFERENCES packages(package_id),

    PRIMARY KEY(policy_id, package_id)
);

CREATE TABLE policy_approvers (
    policy_id BIGINT NOT NULL
        REFERENCES installation_policies(policy_id)
        ON DELETE CASCADE,

    user_id BIGINT NOT NULL
        REFERENCES users(user_id),

    PRIMARY KEY(policy_id, user_id)
);

-- ============================================================
-- 10. INSTALLATION APPROVALS
-- ============================================================

CREATE TABLE installation_approvals (
    approval_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    request_id BIGINT NOT NULL
        REFERENCES installation_requests(request_id),

    reviewer_id BIGINT NOT NULL
        REFERENCES users(user_id),

    decision VARCHAR(20) NOT NULL
        CHECK (
            decision IN ('APPROVED', 'REJECTED')
        ),

    comments TEXT,

    decided_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(request_id, reviewer_id)
);

-- ============================================================
-- 11. INSTALLATION EXECUTION LOG
-- ============================================================

CREATE TABLE installation_logs (
    log_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    request_id BIGINT NOT NULL
        REFERENCES installation_requests(request_id),

    package_id BIGINT
        REFERENCES packages(package_id),

    previous_status installation_status,

    new_status installation_status NOT NULL,

    details TEXT,

    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_installation_logs_request
ON installation_logs(request_id, recorded_at);

-- ============================================================
-- 12. AUDIT TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION audit_installation_status()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN

        INSERT INTO installation_logs (
            request_id,
            previous_status,
            new_status,
            details
        )
        VALUES (
            NEW.request_id,
            OLD.status,
            NEW.status,
            'Installation request state changed.'
        );

    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_installation_status_audit
AFTER UPDATE OF status
ON installation_requests
FOR EACH ROW
EXECUTE FUNCTION audit_installation_status();

-- ============================================================
-- 13. SAMPLE ORGANIZATION AND USERS
-- ============================================================

INSERT INTO organizations(organization_name)
VALUES ('Enterprise Engineering');

INSERT INTO users(
    organization_id,
    username,
    role
)
SELECT
    organization_id,
    'developer01',
    'DEVELOPER'
FROM organizations
WHERE organization_name = 'Enterprise Engineering';

INSERT INTO users(
    organization_id,
    username,
    role
)
SELECT
    organization_id,
    'build-engineer',
    'BUILD_ENGINEER'
FROM organizations
WHERE organization_name = 'Enterprise Engineering';

INSERT INTO users(
    organization_id,
    username,
    role
)
SELECT
    organization_id,
    'security-admin',
    'SECURITY_ADMIN'
FROM organizations
WHERE organization_name = 'Enterprise Engineering';

INSERT INTO users(
    organization_id,
    username,
    role
)
SELECT
    organization_id,
    'release-manager',
    'RELEASE_MANAGER'
FROM organizations
WHERE organization_name = 'Enterprise Engineering';

-- ============================================================
-- 14. SAMPLE PACKAGE RECORDS
-- ============================================================

INSERT INTO packages(
    package_name,
    normalized_name,
    description
)
VALUES
(
    'requests',
    'requests',
    'HTTP client library.'
),
(
    'urllib3',
    'urllib3',
    'HTTP client library.'
),
(
    'certifi',
    'certifi',
    'Certificate authority bundle.'
),
(
    'idna',
    'idna',
    'Internationalized domain names.'
),
(
    'charset-normalizer',
    'charset-normalizer',
    'Character encoding detection.'
),
(
    'unsafe-library',
    'unsafe-library',
    'Restricted demonstration package.'
);

INSERT INTO package_versions(
    package_id,
    version,
    index_id,
    risk,
    status
)
SELECT
    p.package_id,
    v.version,
    i.index_id,
    v.risk::package_risk,
    'AVAILABLE'
FROM (
    VALUES
        ('requests', '2.32.3', 'LOW'),
        ('urllib3', '2.2.3', 'LOW'),
        ('certifi', '2024.8.30', 'LOW'),
        ('idna', '3.10', 'LOW'),
        ('charset-normalizer', '3.4.0', 'LOW'),
        ('unsafe-library', '1.0.0', 'CRITICAL')
) AS v(package_name, version, risk)
JOIN packages p
    ON p.normalized_name = v.package_name
JOIN package_indexes i
    ON i.index_name = 'PyPI';

-- ============================================================
-- 15. DEPENDENCY RELATIONSHIPS
-- ============================================================

INSERT INTO package_dependencies(
    package_version_id,
    required_package_id,
    minimum_version
)
SELECT
    parent.package_version_id,
    child.package_id,
    dependency.minimum_version
FROM (
    VALUES
        ('requests', 'urllib3', '1.21.1'),
        ('requests', 'certifi', '2017.4.17'),
        ('requests', 'idna', '2.5'),
        ('requests', 'charset-normalizer', '2.0.0')
) AS dependency(
    parent_name,
    child_name,
    minimum_version
)
JOIN packages parent_package
    ON parent_package.normalized_name = dependency.parent_name
JOIN package_versions parent
    ON parent.package_id = parent_package.package_id
JOIN packages child
    ON child.normalized_name = dependency.child_name;

-- ============================================================
-- 16. ENVIRONMENT RECORDS
-- ============================================================

INSERT INTO environments(
    organization_id,
    environment_name,
    python_version,
    operating_system,
    environment_type,
    virtual_environment
)
SELECT
    organization_id,
    'development-env',
    '3.13',
    'Windows 11',
    'DEVELOPMENT',
    TRUE
FROM organizations
WHERE organization_name = 'Enterprise Engineering';

INSERT INTO environments(
    organization_id,
    environment_name,
    python_version,
    operating_system,
    environment_type,
    virtual_environment
)
SELECT
    organization_id,
    'production-env',
    '3.12',
    'Ubuntu Linux',
    'PRODUCTION',
    TRUE
FROM organizations
WHERE organization_name = 'Enterprise Engineering';

-- ============================================================
-- 17. INSTALLATION POLICIES
-- ============================================================

INSERT INTO installation_policies(
    organization_id,
    policy_name,
    require_pinned_version,
    require_hash,
    allow_upgrade,
    allow_global_install,
    maximum_risk
)
SELECT
    organization_id,
    'Production Security Policy',
    TRUE,
    TRUE,
    FALSE,
    FALSE,
    'MEDIUM'
FROM organizations
WHERE organization_name = 'Enterprise Engineering';

INSERT INTO policy_allowed_indexes(
    policy_id,
    index_id
)
SELECT
    p.policy_id,
    i.index_id
FROM installation_policies p
JOIN package_indexes i
    ON i.index_name = 'PyPI'
WHERE p.policy_name = 'Production Security Policy';

INSERT INTO policy_denied_packages(
    policy_id,
    package_id
)
SELECT
    p.policy_id,
    pkg.package_id
FROM installation_policies p
JOIN packages pkg
    ON pkg.normalized_name = 'unsafe-library'
WHERE p.policy_name = 'Production Security Policy';

INSERT INTO policy_approvers(
    policy_id,
    user_id
)
SELECT
    p.policy_id,
    u.user_id
FROM installation_policies p
JOIN users u
    ON u.username IN (
        'security-admin',
        'release-manager'
    )
WHERE p.policy_name = 'Production Security Policy';

-- ============================================================
-- 18. INSTALLATION REQUESTS
-- ============================================================

INSERT INTO installation_requests(
    environment_id,
    requested_by,
    operation,
    status,
    dry_run
)
SELECT
    e.environment_id,
    u.user_id,
    'INSTALL',
    'REQUESTED',
    TRUE
FROM environments e
JOIN users u
    ON u.username = 'developer01'
WHERE e.environment_name = 'development-env';

INSERT INTO installation_request_items(
    request_id,
    package_id,
    requested_version
)
SELECT
    r.request_id,
    p.package_id,
    '2.32.3'
FROM installation_requests r
JOIN packages p
    ON p.normalized_name = 'requests'
WHERE r.status = 'REQUESTED';

-- Invalid governance scenario: unpinned package request.
INSERT INTO installation_requests(
    environment_id,
    requested_by,
    operation,
    status,
    dry_run
)
SELECT
    e.environment_id,
    u.user_id,
    'INSTALL',
    'REQUESTED',
    TRUE
FROM environments e
JOIN users u
    ON u.username = 'developer01'
WHERE e.environment_name = 'production-env';

INSERT INTO installation_request_items(
    request_id,
    package_id,
    requested_version
)
SELECT
    r.request_id,
    p.package_id,
    NULL
FROM installation_requests r
JOIN packages p
    ON p.normalized_name = 'unsafe-library'
WHERE r.request_id = (
    SELECT MAX(request_id)
    FROM installation_requests
);

-- ============================================================
-- 19. REQUEST VALIDATION FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_installation_request(
    p_request_id BIGINT,
    p_policy_id BIGINT
)
RETURNS TABLE (
    package_name VARCHAR,
    approved BOOLEAN,
    reason TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_request installation_requests%ROWTYPE;
    v_policy installation_policies%ROWTYPE;
BEGIN
    SELECT *
    INTO v_request
    FROM installation_requests
    WHERE request_id = p_request_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Installation request % not found',
            p_request_id;
    END IF;

    SELECT *
    INTO v_policy
    FROM installation_policies
    WHERE policy_id = p_policy_id
      AND enabled = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Active policy % not found',
            p_policy_id;
    END IF;

    RETURN QUERY
    SELECT
        p.package_name::VARCHAR,

        (
            (
                NOT v_policy.require_pinned_version
                OR item.requested_version IS NOT NULL
            )
            AND
            (
                NOT v_policy.require_hash
                OR pv.sha256 IS NOT NULL
            )
            AND
            pv.risk <= v_policy.maximum_risk
            AND
            EXISTS (
                SELECT 1
                FROM policy_allowed_indexes pai
                JOIN package_indexes pi
                    ON pi.index_id = pai.index_id
                WHERE pai.policy_id = p_policy_id
                  AND pi.index_id = pv.index_id
                  AND pi.trusted = TRUE
                  AND pi.enabled = TRUE
            )
            AND
            NOT EXISTS (
                SELECT 1
                FROM policy_denied_packages pdp
                WHERE pdp.policy_id = p_policy_id
                  AND pdp.package_id = p.package_id
            )
            AND
            (
                v_request.operation <> 'UPGRADE'
                OR v_policy.allow_upgrade
            )
        ) AS approved,

        CASE
            WHEN v_policy.require_pinned_version
                 AND item.requested_version IS NULL
                THEN 'Version must be pinned.'

            WHEN v_policy.require_hash
                 AND pv.sha256 IS NULL
                THEN 'SHA-256 hash is required.'

            WHEN pv.risk > v_policy.maximum_risk
                THEN 'Package exceeds permitted risk.'

            WHEN NOT EXISTS (
                SELECT 1
                FROM policy_allowed_indexes pai
                JOIN package_indexes pi
                    ON pi.index_id = pai.index_id
                WHERE pai.policy_id = p_policy_id
                  AND pi.index_id = pv.index_id
                  AND pi.trusted = TRUE
                  AND pi.enabled = TRUE
            )
                THEN 'Package source is not trusted.'

            WHEN EXISTS (
                SELECT 1
                FROM policy_denied_packages pdp
                WHERE pdp.policy_id = p_policy_id
                  AND pdp.package_id = p.package_id
            )
                THEN 'Package explicitly denied.'

            WHEN v_request.operation = 'UPGRADE'
                 AND NOT v_policy.allow_upgrade
                THEN 'Upgrade prohibited.'

            ELSE 'Approved.'
        END::TEXT AS reason

    FROM installation_request_items item
    JOIN packages p
        ON p.package_id = item.package_id
    LEFT JOIN package_versions pv
        ON pv.package_id = p.package_id
       AND (
            item.requested_version IS NULL
            OR pv.version = item.requested_version
       )
    WHERE item.request_id = p_request_id;
END;
$$;

-- ============================================================
-- 20. APPROVAL AND WORKFLOW PROCEDURE
-- ============================================================

CREATE OR REPLACE PROCEDURE process_installation_request(
    p_request_id BIGINT,
    p_policy_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_invalid_count INTEGER;
    v_item RECORD;
BEGIN
    -- Lock the request to avoid simultaneous processing.
    SELECT request_id
    FROM installation_requests
    WHERE request_id = p_request_id
      AND status = 'REQUESTED'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Request is missing or not in REQUESTED state.';
    END IF;

    UPDATE installation_requests
    SET status = 'VALIDATING'
    WHERE request_id = p_request_id;

    SELECT COUNT(*)
    INTO v_invalid_count
    FROM validate_installation_request(
        p_request_id,
        p_policy_id
    )
    WHERE approved = FALSE;

    IF v_invalid_count > 0 THEN

        UPDATE installation_requests
        SET
            status = 'REJECTED',
            completed_at = CURRENT_TIMESTAMP,
            error_message = 'One or more packages failed policy validation.'
        WHERE request_id = p_request_id;

        RETURN;
    END IF;

    -- A successful policy evaluation does not mean the package
    -- has already been downloaded or installed.
    UPDATE installation_requests
    SET status = 'APPROVED'
    WHERE request_id = p_request_id;

    FOR v_item IN
        SELECT
            item.request_item_id,
            item.package_id,
            pv.package_version_id
        FROM installation_request_items item
        JOIN packages p
            ON p.package_id = item.package_id
        JOIN package_versions pv
            ON pv.package_id = item.package_id
           AND pv.version = item.requested_version
        WHERE item.request_id = p_request_id
    LOOP
        UPDATE installation_request_items
        SET resolved_version_id = v_item.package_version_id
        WHERE request_item_id = v_item.request_item_id;
    END LOOP;

    UPDATE installation_requests
    SET status = 'INSTALLING'
    WHERE request_id = p_request_id;

    -- A dry run records a successful plan, not a real installation.
    UPDATE installation_requests
    SET
        status = CASE
            WHEN dry_run THEN 'SUCCEEDED'::installation_status
            ELSE 'APPROVED'::installation_status
        END,
        completed_at = CASE
            WHEN dry_run THEN CURRENT_TIMESTAMP
            ELSE NULL
        END
    WHERE request_id = p_request_id;

END;
$$;

-- ============================================================
-- 21. INSTALLATION REQUEST VIEWS
-- ============================================================

CREATE OR REPLACE VIEW package_inventory AS
SELECT
    p.package_id,
    p.package_name,
    pv.version,
    pi.index_name,
    pi.trusted,
    pv.risk,
    pv.status
FROM packages p
JOIN package_versions pv
    ON pv.package_id = p.package_id
JOIN package_indexes pi
    ON pi.index_id = pv.index_id;

CREATE OR REPLACE VIEW installation_request_report AS
SELECT
    r.request_id,
    e.environment_name,
    u.username AS requested_by,
    r.operation,
    r.status,
    r.dry_run,
    COUNT(item.request_item_id) AS package_count,
    r.requested_at,
    r.completed_at
FROM installation_requests r
JOIN environments e
    ON e.environment_id = r.environment_id
JOIN users u
    ON u.user_id = r.requested_by
LEFT JOIN installation_request_items item
    ON item.request_id = r.request_id
GROUP BY
    r.request_id,
    e.environment_name,
    u.username;

-- ============================================================
-- 22. DEPENDENCY RECURSION QUERY
-- ============================================================

WITH RECURSIVE dependency_tree AS (
    SELECT
        pv.package_version_id,
        p.package_name,
        0 AS dependency_level,
        ARRAY[p.package_id] AS visited
    FROM packages p
    JOIN package_versions pv
        ON pv.package_id = p.package_id
    WHERE p.normalized_name = 'requests'
      AND pv.version = '2.32.3'

    UNION ALL

    SELECT
        child_version.package_version_id,
        child.package_name,
        tree.dependency_level + 1,
        tree.visited || child.package_id
    FROM dependency_tree tree
    JOIN package_dependencies dependency
        ON dependency.package_version_id = tree.package_version_id
    JOIN packages child
        ON child.package_id = dependency.required_package_id
    JOIN package_versions child_version
        ON child_version.package_id = child.package_id
    WHERE child.package_id <> ALL(tree.visited)
)
SELECT
    package_name,
    dependency_level,
    package_version_id
FROM dependency_tree
ORDER BY dependency_level, package_name;

-- ============================================================
-- 23. VALIDATION REPORT
-- ============================================================

SELECT
    r.request_id,
    validation.package_name,
    validation.approved,
    validation.reason
FROM installation_requests r
CROSS JOIN LATERAL validate_installation_request(
    r.request_id,
    (
        SELECT policy_id
        FROM installation_policies
        WHERE policy_name = 'Production Security Policy'
        LIMIT 1
    )
) validation
ORDER BY r.request_id, validation.package_name;

-- ============================================================
-- 24. PROCESS VALID REQUEST
-- ============================================================

DO $$
DECLARE
    v_request_id BIGINT;
    v_policy_id BIGINT;
BEGIN
    SELECT policy_id
    INTO v_policy_id
    FROM installation_policies
    WHERE policy_name = 'Production Security Policy';

    SELECT request_id
    INTO v_request_id
    FROM installation_requests
    WHERE status = 'REQUESTED'
    ORDER BY request_id
    LIMIT 1;

    IF v_request_id IS NOT NULL THEN
        CALL process_installation_request(
            v_request_id,
            v_policy_id
        );
    END IF;
END;
$$;

-- ============================================================
-- 25. REPORTING AND AGGREGATION
-- ============================================================

SELECT *
FROM package_inventory
ORDER BY package_name, version;

SELECT *
FROM installation_request_report
ORDER BY request_id;

SELECT
    status,
    COUNT(*) AS total_requests,
    COUNT(*) FILTER (
        WHERE dry_run = TRUE
    ) AS dry_run_requests,
    COUNT(*) FILTER (
        WHERE dry_run = FALSE
    ) AS execution_requests
FROM installation_requests
GROUP BY status
ORDER BY status;

SELECT
    p.package_name,
    COUNT(*) AS request_frequency
FROM installation_request_items item
JOIN packages p
    ON p.package_id = item.package_id
GROUP BY p.package_name
ORDER BY request_frequency DESC, p.package_name;

-- ============================================================
-- 26. INSTALLATION AUDIT RETRIEVAL
-- ============================================================

SELECT
    l.log_id,
    l.request_id,
    l.previous_status,
    l.new_status,
    l.details,
    l.recorded_at
FROM installation_logs l
ORDER BY l.recorded_at DESC;

-- ============================================================
-- 27. ENVIRONMENT PACKAGE RETRIEVAL
-- ============================================================

SELECT
    e.environment_name,
    e.python_version,
    e.environment_type,
    p.package_name,
    pv.version,
    ep.installed_at
FROM environment_packages ep
JOIN environments e
    ON e.environment_id = ep.environment_id
JOIN packages p
    ON p.package_id = ep.package_id
JOIN package_versions pv
    ON pv.package_version_id = ep.package_version_id
ORDER BY e.environment_name, p.package_name;

-- ============================================================
-- 28. TRANSACTION COMPLETION
-- ============================================================

COMMIT;

-- ============================================================
-- END OF PIP PACKAGE GOVERNANCE DATABASE
-- ============================================================
