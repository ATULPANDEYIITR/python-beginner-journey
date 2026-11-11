-- ============================================================
-- PYTHON PACKAGE MANAGEMENT AND GOVERNANCE
-- PostgreSQL 15+
--
-- Models:
-- Package registry, releases, dependencies, environments,
-- installation records, security policies, license controls,
-- package audits, dependency resolution, and reporting.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS python_packages;

SET search_path TO python_packages, public;

-- ------------------------------------------------------------
-- 1. Domain types
-- ------------------------------------------------------------

CREATE TYPE package_status AS ENUM (
    'available',
    'blocked',
    'deprecated'
);

CREATE TYPE environment_status AS ENUM (
    'active',
    'archived',
    'disabled'
);

CREATE TYPE installation_status AS ENUM (
    'pending',
    'installed',
    'failed',
    'removed'
);

CREATE TYPE audit_result AS ENUM (
    'passed',
    'rejected',
    'warning'
);

-- ------------------------------------------------------------
-- 2. Package registry
-- ------------------------------------------------------------

CREATE TABLE packages (
    package_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    package_name VARCHAR(200) NOT NULL UNIQUE,

    normalized_name VARCHAR(200) NOT NULL UNIQUE,

    description TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_package_name CHECK (
        package_name ~ '^[A-Za-z0-9][A-Za-z0-9._-]*$'
        AND package_name NOT LIKE '%..%'
    ),

    CONSTRAINT nonempty_description CHECK (
        length(trim(description)) > 0
    )
);

CREATE TABLE package_releases (
    release_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    package_id BIGINT NOT NULL
        REFERENCES packages(package_id),

    version_major INTEGER NOT NULL,
    version_minor INTEGER NOT NULL,
    version_patch INTEGER NOT NULL,

    license VARCHAR(100) NOT NULL,

    source VARCHAR(100) NOT NULL DEFAULT 'pypi',

    checksum VARCHAR(128),

    status package_status NOT NULL DEFAULT 'available',

    published_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_package_version UNIQUE (
        package_id,
        version_major,
        version_minor,
        version_patch
    ),

    CONSTRAINT valid_version CHECK (
        version_major >= 0
        AND version_minor >= 0
        AND version_patch >= 0
    ),

    CONSTRAINT valid_license CHECK (
        length(trim(license)) > 0
    ),

    CONSTRAINT valid_checksum CHECK (
        checksum IS NULL OR checksum ~ '^[A-Fa-f0-9]{64}$'
    )
);

CREATE INDEX idx_release_version
ON package_releases (
    package_id,
    version_major DESC,
    version_minor DESC,
    version_patch DESC
);

CREATE INDEX idx_release_status
ON package_releases(status);

-- ------------------------------------------------------------
-- 3. Package dependencies
-- ------------------------------------------------------------

CREATE TABLE package_dependencies (
    dependency_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    release_id BIGINT NOT NULL
        REFERENCES package_releases(release_id)
        ON DELETE CASCADE,

    dependency_package_id BIGINT NOT NULL
        REFERENCES packages(package_id),

    version_constraint VARCHAR(100) NOT NULL DEFAULT '*',

    CONSTRAINT unique_release_dependency UNIQUE (
        release_id,
        dependency_package_id
    ),

    CONSTRAINT no_empty_constraint CHECK (
        length(trim(version_constraint)) > 0
    )
);

CREATE INDEX idx_dependency_target
ON package_dependencies(dependency_package_id);

-- Prevent direct self-dependencies.
CREATE FUNCTION prevent_self_dependency()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    source_package_id BIGINT;
BEGIN
    SELECT package_id
    INTO source_package_id
    FROM package_releases
    WHERE release_id = NEW.release_id;

    IF source_package_id = NEW.dependency_package_id THEN
        RAISE EXCEPTION
            'A package cannot depend on itself';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_self_dependency
BEFORE INSERT OR UPDATE
ON package_dependencies
FOR EACH ROW
EXECUTE FUNCTION prevent_self_dependency();

-- ------------------------------------------------------------
-- 4. Environments
-- ------------------------------------------------------------

CREATE TABLE package_environments (
    environment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    environment_name VARCHAR(150) NOT NULL UNIQUE,

    python_version VARCHAR(20) NOT NULL,

    operating_system VARCHAR(100) NOT NULL,

    status environment_status NOT NULL DEFAULT 'active',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_environment_name CHECK (
        length(trim(environment_name)) > 0
    ),

    CONSTRAINT valid_python_version CHECK (
        python_version ~ '^[0-9]+\.[0-9]+(\.[0-9]+)?$'
    )
);

-- ------------------------------------------------------------
-- 5. Installation history
-- ------------------------------------------------------------

CREATE TABLE package_installations (
    installation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    environment_id BIGINT NOT NULL
        REFERENCES package_environments(environment_id),

    release_id BIGINT NOT NULL
        REFERENCES package_releases(release_id),

    status installation_status NOT NULL DEFAULT 'pending',

    installed_at TIMESTAMPTZ,

    failure_reason TEXT,

    CONSTRAINT unique_environment_release UNIQUE (
        environment_id,
        release_id
    ),

    CONSTRAINT installation_state_consistency CHECK (
        (
            status = 'installed'
            AND installed_at IS NOT NULL
            AND failure_reason IS NULL
        )
        OR
        (
            status = 'failed'
            AND failure_reason IS NOT NULL
        )
        OR
        (
            status IN ('pending', 'removed')
        )
    )
);

CREATE INDEX idx_installation_environment
ON package_installations(environment_id, status);

-- ------------------------------------------------------------
-- 6. Repository security policies
-- ------------------------------------------------------------

CREATE TABLE package_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    policy_name VARCHAR(150) NOT NULL UNIQUE,

    minimum_approvals INTEGER NOT NULL DEFAULT 0,

    block_deprecated BOOLEAN NOT NULL DEFAULT TRUE,

    require_checksum BOOLEAN NOT NULL DEFAULT FALSE,

    allowed_sources TEXT[] NOT NULL DEFAULT ARRAY['pypi'],

    allowed_licenses TEXT[] NOT NULL DEFAULT
        ARRAY['MIT', 'Apache-2.0', 'BSD-3-Clause', 'ISC'],

    active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT valid_approval_count CHECK (
        minimum_approvals >= 0
    ),

    CONSTRAINT nonempty_sources CHECK (
        cardinality(allowed_sources) > 0
    ),

    CONSTRAINT nonempty_licenses CHECK (
        cardinality(allowed_licenses) > 0
    )
);

CREATE TABLE package_audits (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    environment_id BIGINT NOT NULL
        REFERENCES package_environments(environment_id),

    release_id BIGINT NOT NULL
        REFERENCES package_releases(release_id),

    policy_id BIGINT NOT NULL
        REFERENCES package_policies(policy_id),

    result audit_result NOT NULL,

    findings JSONB NOT NULL DEFAULT '[]'::JSONB,

    audited_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT findings_array CHECK (
        jsonb_typeof(findings) = 'array'
    )
);

CREATE INDEX idx_audit_environment_date
ON package_audits(environment_id, audited_at DESC);

-- ------------------------------------------------------------
-- 7. Policy evaluation function
-- ------------------------------------------------------------

CREATE FUNCTION evaluate_package_policy(
    p_release_id BIGINT,
    p_policy_id BIGINT
)
RETURNS TABLE (
    accepted BOOLEAN,
    findings JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    release_record RECORD;
    policy_record RECORD;
    issues JSONB := '[]'::JSONB;
BEGIN
    SELECT
        r.*,
        p.package_name
    INTO release_record
    FROM package_releases r
    JOIN packages p
      ON p.package_id = r.package_id
    WHERE r.release_id = p_release_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Release % not found', p_release_id;
    END IF;

    SELECT *
    INTO policy_record
    FROM package_policies
    WHERE policy_id = p_policy_id
      AND active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Active policy not found';
    END IF;

    IF release_record.status = 'blocked' THEN
        issues := issues || jsonb_build_array(
            'Package is blocked'
        );
    END IF;

    IF policy_record.block_deprecated
       AND release_record.status = 'deprecated' THEN
        issues := issues || jsonb_build_array(
            'Package is deprecated'
        );
    END IF;

    IF NOT (
        release_record.license =
        ANY(policy_record.allowed_licenses)
    ) THEN
        issues := issues || jsonb_build_array(
            'License is not approved'
        );
    END IF;

    IF NOT (
        release_record.source =
        ANY(policy_record.allowed_sources)
    ) THEN
        issues := issues || jsonb_build_array(
            'Package source is not approved'
        );
    END IF;

    IF policy_record.require_checksum
       AND release_record.checksum IS NULL THEN
        issues := issues || jsonb_build_array(
            'Package checksum is required'
        );
    END IF;

    RETURN QUERY
    SELECT
        jsonb_array_length(issues) = 0,
        issues;
END;
$$;

-- ------------------------------------------------------------
-- 8. Installation state transition trigger
-- ------------------------------------------------------------

CREATE FUNCTION validate_installation_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN

        IF OLD.status IN ('removed', 'failed')
           AND NEW.status = 'installed' THEN
            RAISE EXCEPTION
                'Create a new installation record instead of reopening history';
        END IF;

        IF OLD.status = 'installed'
           AND NEW.status = 'pending' THEN
            RAISE EXCEPTION
                'Installed package cannot return to pending';
        END IF;

    END IF;

    IF NEW.status = 'installed' THEN
        NEW.installed_at := CURRENT_TIMESTAMP;
        NEW.failure_reason := NULL;
    END IF;

    IF NEW.status = 'failed'
       AND NEW.failure_reason IS NULL THEN
        RAISE EXCEPTION
            'Failure reason is required';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_installation_transition
BEFORE INSERT OR UPDATE
ON package_installations
FOR EACH ROW
EXECUTE FUNCTION validate_installation_transition();

-- ------------------------------------------------------------
-- 9. Transactional installation procedure
-- ------------------------------------------------------------

CREATE PROCEDURE install_package(
    p_environment_id BIGINT,
    p_release_id BIGINT,
    p_policy_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    policy_result RECORD;
BEGIN
    -- Lock the environment row to serialize installation requests.
    PERFORM 1
    FROM package_environments
    WHERE environment_id = p_environment_id
      AND status = 'active'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Active environment not found';
    END IF;

    SELECT *
    INTO policy_result
    FROM evaluate_package_policy(
        p_release_id,
        p_policy_id
    );

    INSERT INTO package_audits (
        environment_id,
        release_id,
        policy_id,
        result,
        findings
    )
    VALUES (
        p_environment_id,
        p_release_id,
        p_policy_id,
        CASE
            WHEN policy_result.accepted
                THEN 'passed'::audit_result
            ELSE 'rejected'::audit_result
        END,
        policy_result.findings
    );

    IF NOT policy_result.accepted THEN
        RAISE EXCEPTION
            'Package rejected: %',
            policy_result.findings;
    END IF;

    INSERT INTO package_installations (
        environment_id,
        release_id,
        status
    )
    VALUES (
        p_environment_id,
        p_release_id,
        'installed'
    )
    ON CONFLICT (environment_id, release_id)
    DO NOTHING;

END;
$$;

-- ------------------------------------------------------------
-- 10. Package registry reporting view
-- ------------------------------------------------------------

CREATE VIEW package_registry_report AS
SELECT
    p.package_id,
    p.package_name,
    r.release_id,
    concat(
        r.version_major, '.',
        r.version_minor, '.',
        r.version_patch
    ) AS version,
    r.license,
    r.source,
    r.status,
    r.published_at,
    COUNT(DISTINCT d.dependency_id) AS dependency_count
FROM packages p
JOIN package_releases r
    ON r.package_id = p.package_id
LEFT JOIN package_dependencies d
    ON d.release_id = r.release_id
GROUP BY
    p.package_id,
    p.package_name,
    r.release_id;

-- ------------------------------------------------------------
-- 11. Sample registry data
-- ------------------------------------------------------------

INSERT INTO packages (
    package_name,
    normalized_name,
    description
)
VALUES
(
    'numpy',
    'numpy',
    'Numerical computing library.'
),
(
    'pandas',
    'pandas',
    'Data analysis library.'
),
(
    'requests',
    'requests',
    'HTTP client library.'
),
(
    'analytics-toolkit',
    'analytics-toolkit',
    'Analytics application dependency package.'
),
(
    'legacy-package',
    'legacy-package',
    'Deprecated package.'
);

INSERT INTO package_releases (
    package_id,
    version_major,
    version_minor,
    version_patch,
    license,
    source,
    checksum,
    status
)
SELECT
    package_id,
    2,
    1,
    0,
    'BSD-3-Clause',
    'pypi',
    repeat('a', 64),
    'available'
FROM packages
WHERE normalized_name = 'numpy';

INSERT INTO package_releases (
    package_id,
    version_major,
    version_minor,
    version_patch,
    license,
    source,
    checksum,
    status
)
SELECT
    package_id,
    2,
    2,
    0,
    'BSD-3-Clause',
    'pypi',
    repeat('b', 64),
    'available'
FROM packages
WHERE normalized_name = 'pandas';

INSERT INTO package_releases (
    package_id,
    version_major,
    version_minor,
    version_patch,
    license,
    source,
    checksum,
    status
)
SELECT
    package_id,
    2,
    32,
    0,
    'Apache-2.0',
    'pypi',
    repeat('c', 64),
    'available'
FROM packages
WHERE normalized_name = 'requests';

INSERT INTO package_releases (
    package_id,
    version_major,
    version_minor,
    version_patch,
    license,
    source,
    checksum,
    status
)
SELECT
    package_id,
    1,
    0,
    0,
    'MIT',
    'pypi',
    repeat('d', 64),
    'available'
FROM packages
WHERE normalized_name = 'analytics-toolkit';

INSERT INTO package_releases (
    package_id,
    version_major,
    version_minor,
    version_patch,
    license,
    source,
    status
)
SELECT
    package_id,
    1,
    0,
    0,
    'GPL-3.0',
    'unknown-index',
    'blocked'
FROM packages
WHERE normalized_name = 'legacy-package';

-- ------------------------------------------------------------
-- 12. Sample dependency relationships
-- ------------------------------------------------------------

INSERT INTO package_dependencies (
    release_id,
    dependency_package_id,
    version_constraint
)
SELECT
    parent.release_id,
    child.package_id,
    '>=2.0.0'
FROM package_releases parent
JOIN packages parent_package
    ON parent_package.package_id = parent.package_id
JOIN packages child
    ON child.normalized_name = 'numpy'
WHERE parent_package.normalized_name = 'pandas';

INSERT INTO package_dependencies (
    release_id,
    dependency_package_id,
    version_constraint
)
SELECT
    parent.release_id,
    child.package_id,
    '>=2.2.0'
FROM package_releases parent
JOIN packages parent_package
    ON parent_package.package_id = parent.package_id
JOIN packages child
    ON child.normalized_name = 'pandas'
WHERE parent_package.normalized_name = 'analytics-toolkit';

INSERT INTO package_dependencies (
    release_id,
    dependency_package_id,
    version_constraint
)
SELECT
    parent.release_id,
    child.package_id,
    '>=2.30.0'
FROM package_releases parent
JOIN packages parent_package
    ON parent_package.package_id = parent.package_id
JOIN packages child
    ON child.normalized_name = 'requests'
WHERE parent_package.normalized_name = 'analytics-toolkit';

-- ------------------------------------------------------------
-- 13. Environment and governance configuration
-- ------------------------------------------------------------

INSERT INTO package_environments (
    environment_name,
    python_version,
    operating_system
)
VALUES
(
    'analytics-development',
    '3.13.0',
    'Windows'
),
(
    'analytics-production',
    '3.12.0',
    'Linux'
);

INSERT INTO package_policies (
    policy_name,
    minimum_approvals,
    block_deprecated,
    require_checksum,
    allowed_sources,
    allowed_licenses
)
VALUES
(
    'enterprise-default',
    0,
    TRUE,
    TRUE,
    ARRAY['pypi'],
    ARRAY[
        'MIT',
        'Apache-2.0',
        'BSD-3-Clause',
        'ISC'
    ]
);

-- ------------------------------------------------------------
-- 14. Package retrieval
-- ------------------------------------------------------------

SELECT *
FROM package_registry_report
ORDER BY package_name, version DESC;

-- ------------------------------------------------------------
-- 15. Dependency retrieval
-- ------------------------------------------------------------

SELECT
    parent.package_name AS package,
    child.package_name AS dependency,
    dependency.version_constraint
FROM package_dependencies dependency
JOIN package_releases release
    ON release.release_id = dependency.release_id
JOIN packages parent
    ON parent.package_id = release.package_id
JOIN packages child
    ON child.package_id = dependency.dependency_package_id
ORDER BY parent.package_name, child.package_name;

-- ------------------------------------------------------------
-- 16. Dependency traversal using recursive CTE
-- ------------------------------------------------------------

WITH RECURSIVE dependency_tree AS (
    SELECT
        p.package_id,
        p.package_name,
        r.release_id,
        0 AS depth,
        ARRAY[p.package_id] AS visited
    FROM packages p
    JOIN package_releases r
        ON r.package_id = p.package_id
    WHERE p.normalized_name = 'analytics-toolkit'
      AND r.status = 'available'
      AND r.version_major = 1
      AND r.version_minor = 0
      AND r.version_patch = 0

    UNION ALL

    SELECT
        child.package_id,
        child.package_name,
        child_release.release_id,
        tree.depth + 1,
        tree.visited || child.package_id
    FROM dependency_tree tree
    JOIN package_dependencies dependency
        ON dependency.release_id = tree.release_id
    JOIN packages child
        ON child.package_id = dependency.dependency_package_id
    JOIN LATERAL (
        SELECT release_id
        FROM package_releases
        WHERE package_id = child.package_id
          AND status = 'available'
        ORDER BY
            version_major DESC,
            version_minor DESC,
            version_patch DESC
        LIMIT 1
    ) child_release ON TRUE
    WHERE NOT child.package_id = ANY(tree.visited)
)
SELECT
    package_name,
    depth
FROM dependency_tree
ORDER BY depth, package_name;

-- ------------------------------------------------------------
-- 17. Version eligibility validation
-- ------------------------------------------------------------

SELECT
    p.package_name,
    concat(
        r.version_major, '.',
        r.version_minor, '.',
        r.version_patch
    ) AS version,
    CASE
        WHEN r.version_major >= 2 THEN 'eligible'
        ELSE 'requires review'
    END AS version_eligibility
FROM packages p
JOIN package_releases r
    ON r.package_id = p.package_id
WHERE r.status = 'available';

-- ------------------------------------------------------------
-- 18. Install a package transactionally
-- ------------------------------------------------------------

DO $$
DECLARE
    environment_key BIGINT;
    release_key BIGINT;
    policy_key BIGINT;
BEGIN
    SELECT environment_id
    INTO environment_key
    FROM package_environments
    WHERE environment_name = 'analytics-development';

    SELECT r.release_id
    INTO release_key
    FROM package_releases r
    JOIN packages p
        ON p.package_id = r.package_id
    WHERE p.normalized_name = 'numpy'
      AND r.version_major = 2
      AND r.version_minor = 1
      AND r.version_patch = 0;

    SELECT policy_id
    INTO policy_key
    FROM package_policies
    WHERE policy_name = 'enterprise-default';

    CALL install_package(
        environment_key,
        release_key,
        policy_key
    );
END;
$$;

-- ------------------------------------------------------------
-- 19. Installation report
-- ------------------------------------------------------------

SELECT
    environment.environment_name,
    package.package_name,
    concat(
        release.version_major, '.',
        release.version_minor, '.',
        release.version_patch
    ) AS installed_version,
    installation.status,
    installation.installed_at
FROM package_installations installation
JOIN package_environments environment
    ON environment.environment_id = installation.environment_id
JOIN package_releases release
    ON release.release_id = installation.release_id
JOIN packages package
    ON package.package_id = release.package_id
ORDER BY environment.environment_name, package.package_name;

-- ------------------------------------------------------------
-- 20. Security audit report
-- ------------------------------------------------------------

SELECT
    audit.audit_id,
    environment.environment_name,
    package.package_name,
    audit.result,
    audit.findings,
    audit.audited_at
FROM package_audits audit
JOIN package_environments environment
    ON environment.environment_id = audit.environment_id
JOIN package_releases release
    ON release.release_id = audit.release_id
JOIN packages package
    ON package.package_id = release.package_id
ORDER BY audit.audited_at DESC;

-- ------------------------------------------------------------
-- 21. Package installation aggregation
-- ------------------------------------------------------------

SELECT
    package.package_name,
    COUNT(*) FILTER (
        WHERE installation.status = 'installed'
    ) AS active_installations,
    COUNT(*) FILTER (
        WHERE installation.status = 'failed'
    ) AS failed_installations
FROM packages package
LEFT JOIN package_releases release
    ON release.package_id = package.package_id
LEFT JOIN package_installations installation
    ON installation.release_id = release.release_id
GROUP BY package.package_id, package.package_name
ORDER BY active_installations DESC, package.package_name;

COMMIT;
