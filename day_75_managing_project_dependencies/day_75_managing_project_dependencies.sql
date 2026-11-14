-- ============================================================
-- PROJECT DEPENDENCY MANAGEMENT AND REPOSITORY GOVERNANCE
-- PostgreSQL 15+
--
-- Includes:
-- Dependency inventory and version constraints
-- Dependency relationships and resolution
-- Vulnerability and license assessment
-- Update proposals and changesets
-- Pull Requests, reviews and conversations
-- Approval policies and status checks
-- Branch protection and merge eligibility
-- Auditing and reporting
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS dependency_management;

SET search_path TO dependency_management, public;

-- ------------------------------------------------------------
-- 1. Domain types
-- ------------------------------------------------------------

CREATE TYPE branch_status AS ENUM (
    'active',
    'archived',
    'deleted'
);

CREATE TYPE pull_request_status AS ENUM (
    'draft',
    'open',
    'merged',
    'closed'
);

CREATE TYPE review_state AS ENUM (
    'approved',
    'changes_requested',
    'commented',
    'dismissed'
);

CREATE TYPE check_state AS ENUM (
    'pending',
    'passed',
    'failed'
);

CREATE TYPE merge_strategy AS ENUM (
    'merge',
    'squash',
    'rebase'
);

CREATE TYPE dependency_type AS ENUM (
    'runtime',
    'development',
    'optional',
    'peer'
);

CREATE TYPE severity_level AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

-- ------------------------------------------------------------
-- 2. Repositories and users
-- ------------------------------------------------------------

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name VARCHAR(150) NOT NULL UNIQUE,
    default_branch VARCHAR(100) NOT NULL DEFAULT 'main',
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (repository_name ~ '^[A-Za-z0-9_.-]+$')
);

CREATE TABLE repository_members (
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL,
    role VARCHAR(30) NOT NULL
        CHECK (role IN ('owner', 'maintainer', 'developer', 'reviewer')),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (repository_id, username)
);

CREATE TABLE branches (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    branch_name VARCHAR(150) NOT NULL,
    status branch_status NOT NULL DEFAULT 'active',
    head_commit VARCHAR(100) NOT NULL,
    base_branch_id BIGINT REFERENCES branches(branch_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (repository_id, branch_name),
    CHECK (branch_name <> '')
);

-- ------------------------------------------------------------
-- 3. Dependency inventory
-- ------------------------------------------------------------

CREATE TABLE dependencies (
    dependency_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    package_name VARCHAR(150) NOT NULL,
    current_version VARCHAR(50) NOT NULL,
    minimum_version VARCHAR(50) NOT NULL,
    maximum_version VARCHAR(50),
    package_type dependency_type NOT NULL DEFAULT 'runtime',
    direct_dependency BOOLEAN NOT NULL DEFAULT TRUE,
    license_identifier VARCHAR(100) NOT NULL,
    source_registry VARCHAR(300) NOT NULL,
    vulnerability_count INTEGER NOT NULL DEFAULT 0,
    last_audited_at TIMESTAMPTZ,
    UNIQUE (repository_id, package_name),
    CHECK (package_name ~ '^[A-Za-z0-9_.-]+$'),
    CHECK (vulnerability_count >= 0),
    CHECK (current_version ~ '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'),
    CHECK (minimum_version ~ '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'),
    CHECK (
        maximum_version IS NULL OR
        maximum_version ~ '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
    )
);

CREATE TABLE dependency_relationships (
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    dependency_id BIGINT NOT NULL
        REFERENCES dependencies(dependency_id) ON DELETE CASCADE,
    prerequisite_id BIGINT NOT NULL
        REFERENCES dependencies(dependency_id) ON DELETE CASCADE,
    PRIMARY KEY (dependency_id, prerequisite_id),
    CHECK (dependency_id <> prerequisite_id)
);

CREATE TABLE vulnerability_findings (
    finding_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dependency_id BIGINT NOT NULL
        REFERENCES dependencies(dependency_id) ON DELETE CASCADE,
    vulnerability_code VARCHAR(100) NOT NULL,
    severity severity_level NOT NULL,
    affected_version_range TEXT NOT NULL,
    remediation_version VARCHAR(50),
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    discovered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (dependency_id, vulnerability_code)
);

CREATE TABLE license_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    license_identifier VARCHAR(100) NOT NULL,
    allowed BOOLEAN NOT NULL,
    UNIQUE (repository_id, license_identifier)
);

-- ------------------------------------------------------------
-- 4. Commits and dependency lockfiles
-- ------------------------------------------------------------

CREATE TABLE commits (
    commit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    commit_hash VARCHAR(100) NOT NULL,
    parent_hash VARCHAR(100),
    commit_message TEXT NOT NULL,
    author_username VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (repository_id, commit_hash)
);

CREATE TABLE dependency_lockfiles (
    lockfile_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    lockfile_name VARCHAR(200) NOT NULL,
    content_hash VARCHAR(128) NOT NULL,
    dependency_count INTEGER NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (repository_id, branch_id, lockfile_name),
    CHECK (dependency_count >= 0)
);

-- ------------------------------------------------------------
-- 5. Dependency update proposals
-- ------------------------------------------------------------

CREATE TABLE dependency_updates (
    update_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dependency_id BIGINT NOT NULL
        REFERENCES dependencies(dependency_id),
    old_version VARCHAR(50) NOT NULL,
    proposed_version VARCHAR(50) NOT NULL,
    update_type VARCHAR(20) NOT NULL
        CHECK (update_type IN ('patch', 'minor', 'major')),
    security_update BOOLEAN NOT NULL DEFAULT FALSE,
    compatibility_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (old_version <> proposed_version),
    CHECK (old_version ~ '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'),
    CHECK (proposed_version ~ '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$')
);

-- ------------------------------------------------------------
-- 6. Pull Requests
-- ------------------------------------------------------------

CREATE TABLE pull_requests (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    source_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    title VARCHAR(250) NOT NULL,
    description TEXT,
    author_username VARCHAR(100) NOT NULL,
    status pull_request_status NOT NULL DEFAULT 'open',
    is_draft BOOLEAN NOT NULL DEFAULT FALSE,
    source_commit_hash VARCHAR(100) NOT NULL,
    target_commit_hash VARCHAR(100) NOT NULL,
    base_synchronized BOOLEAN NOT NULL DEFAULT TRUE,
    has_merge_conflicts BOOLEAN NOT NULL DEFAULT FALSE,
    merged_commit_hash VARCHAR(100),
    selected_merge_strategy merge_strategy,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    merged_at TIMESTAMPTZ,
    CHECK (source_branch_id <> target_branch_id),
    CHECK (
        (status = 'merged' AND merged_at IS NOT NULL
         AND merged_commit_hash IS NOT NULL)
        OR
        (status <> 'merged' AND merged_at IS NULL)
    )
);

CREATE TABLE pull_request_changes (
    change_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    dependency_id BIGINT NOT NULL REFERENCES dependencies(dependency_id),
    previous_version VARCHAR(50) NOT NULL,
    proposed_version VARCHAR(50) NOT NULL,
    update_id BIGINT REFERENCES dependency_updates(update_id),
    UNIQUE (pull_request_id, dependency_id),
    CHECK (previous_version <> proposed_version)
);

-- ------------------------------------------------------------
-- 7. Code reviews and approvals
-- ------------------------------------------------------------

CREATE TABLE code_reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    reviewer_username VARCHAR(100) NOT NULL,
    state review_state NOT NULL,
    reviewed_commit_hash VARCHAR(100) NOT NULL,
    review_body TEXT,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (pull_request_id, reviewer_username, reviewed_commit_hash)
);

CREATE TABLE review_comments (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL
        REFERENCES code_reviews(review_id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER,
    comment_body TEXT NOT NULL,
    is_inline BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (line_number IS NULL OR line_number > 0)
);

CREATE TABLE review_conversations (
    conversation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    discussion_topic VARCHAR(250) NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (
        (resolved = TRUE AND resolved_at IS NOT NULL)
        OR
        (resolved = FALSE AND resolved_at IS NULL)
    )
);

-- ------------------------------------------------------------
-- 8. Status checks
-- ------------------------------------------------------------

CREATE TABLE status_checks (
    check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    check_name VARCHAR(150) NOT NULL,
    state check_state NOT NULL DEFAULT 'pending',
    commit_hash VARCHAR(100) NOT NULL,
    details TEXT,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (pull_request_id, check_name, commit_hash)
);

-- ------------------------------------------------------------
-- 9. Branch protection
-- ------------------------------------------------------------

CREATE TABLE branch_protection_policies (
    protection_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    required_approvals INTEGER NOT NULL DEFAULT 2,
    require_status_checks BOOLEAN NOT NULL DEFAULT TRUE,
    require_resolved_conversations BOOLEAN NOT NULL DEFAULT TRUE,
    require_lockfile BOOLEAN NOT NULL DEFAULT TRUE,
    allow_direct_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_branch_deletion BOOLEAN NOT NULL DEFAULT FALSE,
    require_linear_history BOOLEAN NOT NULL DEFAULT TRUE,
    dismiss_stale_approvals BOOLEAN NOT NULL DEFAULT TRUE,
    administrator_bypass BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (repository_id, branch_id),
    CHECK (required_approvals >= 0)
);

CREATE TABLE required_status_checks (
    protection_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(protection_id)
        ON DELETE CASCADE,
    check_name VARCHAR(150) NOT NULL,
    PRIMARY KEY (protection_id, check_name)
);

-- ------------------------------------------------------------
-- 10. Merge eligibility audit
-- ------------------------------------------------------------

CREATE TABLE merge_evaluations (
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    eligible BOOLEAN NOT NULL,
    evaluated_by VARCHAR(100) NOT NULL,
    evaluation_details JSONB NOT NULL DEFAULT '[]'::jsonb,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE repository_audit_log (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    actor VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id BIGINT,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 11. Performance indexes
-- ------------------------------------------------------------

CREATE INDEX idx_dependencies_repository
    ON dependencies(repository_id, package_name);

CREATE INDEX idx_dependency_vulnerabilities
    ON vulnerability_findings(severity, verified);

CREATE INDEX idx_pr_repository_status
    ON pull_requests(repository_id, status, created_at DESC);

CREATE INDEX idx_pr_target
    ON pull_requests(target_branch_id, status);

CREATE INDEX idx_reviews_pr_commit
    ON code_reviews(pull_request_id, reviewed_commit_hash, state);

CREATE INDEX idx_status_checks_pr_commit
    ON status_checks(pull_request_id, commit_hash, state);

CREATE INDEX idx_open_conversations
    ON review_conversations(pull_request_id)
    WHERE resolved = FALSE;

CREATE INDEX idx_audit_repository_time
    ON repository_audit_log(repository_id, created_at DESC);

CREATE INDEX idx_merge_evaluations
    ON merge_evaluations(pull_request_id, evaluated_at DESC);

-- ------------------------------------------------------------
-- 12. Version comparison
-- ------------------------------------------------------------

CREATE FUNCTION version_compare(
    p_left TEXT,
    p_right TEXT
)
RETURNS INTEGER
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    left_parts INTEGER[];
    right_parts INTEGER[];
    i INTEGER;
BEGIN
    IF p_left !~ '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
       OR
       p_right !~ '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
    THEN
        RAISE EXCEPTION 'Invalid semantic version';
    END IF;

    left_parts := string_to_array(p_left, '.')::INTEGER[];
    right_parts := string_to_array(p_right, '.')::INTEGER[];

    FOR i IN 1..3 LOOP
        IF left_parts[i] < right_parts[i] THEN
            RETURN -1;
        ELSIF left_parts[i] > right_parts[i] THEN
            RETURN 1;
        END IF;
    END LOOP;

    RETURN 0;
END;
$$;

-- ------------------------------------------------------------
-- 13. Dependency integrity trigger
-- ------------------------------------------------------------

CREATE FUNCTION validate_dependency_version()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF version_compare(
        NEW.current_version,
        NEW.minimum_version
    ) < 0 THEN
        RAISE EXCEPTION
            'Current version is below minimum for %',
            NEW.package_name;
    END IF;

    IF NEW.maximum_version IS NOT NULL
       AND version_compare(
           NEW.current_version,
           NEW.maximum_version
       ) > 0 THEN
        RAISE EXCEPTION
            'Current version exceeds maximum for %',
            NEW.package_name;
    END IF;

    NEW.last_audited_at := NOW();

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_dependency_version
BEFORE INSERT OR UPDATE OF
    current_version, minimum_version, maximum_version
ON dependencies
FOR EACH ROW
EXECUTE FUNCTION validate_dependency_version();

-- ------------------------------------------------------------
-- 14. Review membership validation
-- ------------------------------------------------------------

CREATE FUNCTION validate_review_membership()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_repository_id BIGINT;
    v_active BOOLEAN;
    v_role VARCHAR(30);
    v_pr_status pull_request_status;
    v_draft BOOLEAN;
BEGIN
    SELECT repository_id, status, is_draft
    INTO v_repository_id, v_pr_status, v_draft
    FROM pull_requests
    WHERE pull_request_id = NEW.pull_request_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Pull Request does not exist';
    END IF;

    SELECT active, role
    INTO v_active, v_role
    FROM repository_members
    WHERE repository_id = v_repository_id
      AND username = NEW.reviewer_username;

    IF NOT FOUND OR NOT v_active THEN
        RAISE EXCEPTION 'Reviewer is not an active repository member';
    END IF;

    IF v_role NOT IN ('owner', 'maintainer', 'reviewer') THEN
        RAISE EXCEPTION 'Reviewer role is not eligible';
    END IF;

    IF v_pr_status <> 'open' OR v_draft THEN
        RAISE EXCEPTION 'Pull Request is not reviewable';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_review_membership
BEFORE INSERT OR UPDATE ON code_reviews
FOR EACH ROW
EXECUTE FUNCTION validate_review_membership();

-- ------------------------------------------------------------
-- 15. Conversation resolution consistency
-- ------------------------------------------------------------

CREATE FUNCTION validate_conversation_resolution()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.resolved AND NEW.resolved_at IS NULL THEN
        NEW.resolved_at := NOW();
    END IF;

    IF NOT NEW.resolved THEN
        NEW.resolved_at := NULL;
        NEW.resolved_by := NULL;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_conversation_resolution
BEFORE INSERT OR UPDATE ON review_conversations
FOR EACH ROW
EXECUTE FUNCTION validate_conversation_resolution();

-- ------------------------------------------------------------
-- 16. Dependency graph validation
-- ------------------------------------------------------------

CREATE FUNCTION validate_dependency_graph(
    p_repository_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_total BIGINT;
    v_reachable BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_total
    FROM dependencies
    WHERE repository_id = p_repository_id;

    IF EXISTS (
        SELECT 1
        FROM dependency_relationships r
        JOIN dependencies d
          ON d.dependency_id = r.dependency_id
        JOIN dependencies p
          ON p.dependency_id = r.prerequisite_id
        WHERE d.repository_id <> p_repository_id
           OR p.repository_id <> p_repository_id
    ) THEN
        RETURN FALSE;
    END IF;

    WITH RECURSIVE traversal(node, path, cycle) AS (
        SELECT
            dependency_id,
            ARRAY[dependency_id],
            FALSE
        FROM dependencies
        WHERE repository_id = p_repository_id

        UNION ALL

        SELECT
            r.prerequisite_id,
            t.path || r.prerequisite_id,
            r.prerequisite_id = ANY(t.path)
        FROM traversal t
        JOIN dependency_relationships r
          ON r.dependency_id = t.node
        JOIN dependencies d
          ON d.dependency_id = r.prerequisite_id
        WHERE d.repository_id = p_repository_id
          AND NOT t.cycle
    )
    SELECT NOT EXISTS (
        SELECT 1 FROM traversal WHERE cycle
    )
    INTO v_total;

    RETURN v_total::BOOLEAN;
END;
$$;

-- ------------------------------------------------------------
-- 17. Dependency policy evaluation
-- ------------------------------------------------------------

CREATE FUNCTION dependency_policy_violations(
    p_repository_id BIGINT
)
RETURNS TABLE (
    dependency_name VARCHAR,
    violation TEXT
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        d.package_name::VARCHAR,
        'Disallowed license: ' || d.license_identifier
    FROM dependencies d
    LEFT JOIN license_policies lp
      ON lp.repository_id = d.repository_id
     AND lp.license_identifier = d.license_identifier
    WHERE d.repository_id = p_repository_id
      AND (
          (lp.policy_id IS NOT NULL AND NOT lp.allowed)
          OR
          (
              NOT EXISTS (
                  SELECT 1
                  FROM license_policies x
                  WHERE x.repository_id = p_repository_id
              )
              AND d.license_identifier NOT IN (
                  'MIT', 'Apache-2.0', 'BSD-3-Clause'
              )
          )
      )

    UNION ALL

    SELECT
        d.package_name::VARCHAR,
        'Unresolved security vulnerability'
    FROM dependencies d
    JOIN vulnerability_findings vf
      ON vf.dependency_id = d.dependency_id
    WHERE d.repository_id = p_repository_id
      AND vf.verified
      AND vf.severity IN ('high', 'critical');
$$;

-- ------------------------------------------------------------
-- 18. Merge eligibility evaluation
-- ------------------------------------------------------------

CREATE FUNCTION evaluate_merge_eligibility(
    p_pull_request_id BIGINT
)
RETURNS TABLE (
    eligible BOOLEAN,
    reasons JSONB
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_pr pull_requests%ROWTYPE;
    v_policy branch_protection_policies%ROWTYPE;
    v_approvals INTEGER;
    v_pending_checks INTEGER;
    v_failed_checks INTEGER;
    v_missing_checks INTEGER;
    v_unresolved INTEGER;
    v_lockfiles INTEGER;
    v_dependency_violations INTEGER;
    v_reasons JSONB := '[]'::jsonb;
BEGIN
    SELECT *
    INTO v_pr
    FROM pull_requests
    WHERE pull_request_id = p_pull_request_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Pull Request not found';
    END IF;

    SELECT *
    INTO v_policy
    FROM branch_protection_policies
    WHERE repository_id = v_pr.repository_id
      AND branch_id = v_pr.target_branch_id;

    IF NOT FOUND THEN
        v_reasons := v_reasons ||
            jsonb_build_array('No branch protection policy');
    END IF;

    IF v_pr.status <> 'open' THEN
        v_reasons := v_reasons ||
            jsonb_build_array('Pull Request is not open');
    END IF;

    IF v_pr.is_draft THEN
        v_reasons := v_reasons ||
            jsonb_build_array('Draft Pull Request cannot merge');
    END IF;

    IF v_pr.has_merge_conflicts THEN
        v_reasons := v_reasons ||
            jsonb_build_array('Merge conflicts exist');
    END IF;

    IF NOT v_pr.base_synchronized THEN
        v_reasons := v_reasons ||
            jsonb_build_array('Base branch is outdated');
    END IF;

    IF FOUND AND v_policy.require_resolved_conversations THEN
        SELECT COUNT(*)
        INTO v_unresolved
        FROM review_conversations
        WHERE pull_request_id = p_pull_request_id
          AND NOT resolved;

        IF v_unresolved > 0 THEN
            v_reasons := v_reasons ||
                jsonb_build_array('Unresolved review conversations');
        END IF;
    END IF;

    IF FOUND AND v_policy.require_status_checks THEN
        SELECT COUNT(*)
        INTO v_missing_checks
        FROM required_status_checks required
        WHERE required.protection_id = v_policy.protection_id
          AND NOT EXISTS (
              SELECT 1
              FROM status_checks actual
              WHERE actual.pull_request_id = p_pull_request_id
                AND actual.check_name = required.check_name
                AND actual.commit_hash = v_pr.source_commit_hash
                AND actual.state = 'passed'
          );

        IF v_missing_checks > 0 THEN
            v_reasons := v_reasons ||
                jsonb_build_array('Required status checks missing or failing');
        END IF;
    END IF;

    IF FOUND THEN
        SELECT COUNT(DISTINCT cr.reviewer_username)
        INTO v_approvals
        FROM code_reviews cr
        JOIN repository_members rm
          ON rm.repository_id = v_pr.repository_id
         AND rm.username = cr.reviewer_username
        WHERE cr.pull_request_id = p_pull_request_id
          AND cr.state = 'approved'
          AND cr.reviewed_commit_hash = v_pr.source_commit_hash
          AND rm.active
          AND rm.role IN ('owner', 'maintainer', 'reviewer');

        IF v_approvals < v_policy.required_approvals THEN
            v_reasons := v_reasons ||
                jsonb_build_array(
                    'Insufficient eligible current approvals'
                );
        END IF;

        IF v_policy.require_lockfile THEN
            SELECT COUNT(*)
            INTO v_lockfiles
            FROM dependency_lockfiles
            WHERE repository_id = v_pr.repository_id
              AND branch_id = v_pr.source_branch_id;

            IF v_lockfiles = 0 THEN
                v_reasons := v_reasons ||
                    jsonb_build_array('Dependency lockfile missing');
            END IF;
        END IF;
    END IF;

    SELECT COUNT(*)
    INTO v_dependency_violations
    FROM dependency_policy_violations(v_pr.repository_id);

    IF v_dependency_violations > 0 THEN
        v_reasons := v_reasons ||
            jsonb_build_array('Dependency policy violations exist');
    END IF;

    RETURN QUERY
    SELECT
        jsonb_array_length(v_reasons) = 0,
        v_reasons;
END;
$$;

-- ------------------------------------------------------------
-- 19. Transactional merge procedure
-- ------------------------------------------------------------

CREATE PROCEDURE merge_pull_request(
    p_pull_request_id BIGINT,
    p_strategy merge_strategy,
    p_actor VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_pr pull_requests%ROWTYPE;
    v_eligible BOOLEAN;
    v_reasons JSONB;
    v_new_commit VARCHAR(100);
    v_change RECORD;
BEGIN
    SELECT *
    INTO v_pr
    FROM pull_requests
    WHERE pull_request_id = p_pull_request_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Pull Request not found';
    END IF;

    IF v_pr.status <> 'open' OR v_pr.is_draft THEN
        RAISE EXCEPTION 'Pull Request is not mergeable';
    END IF;

    SELECT e.eligible, e.reasons
    INTO v_eligible, v_reasons
    FROM evaluate_merge_eligibility(p_pull_request_id) e;

    INSERT INTO merge_evaluations (
        pull_request_id,
        eligible,
        evaluated_by,
        evaluation_details
    )
    VALUES (
        p_pull_request_id,
        v_eligible,
        p_actor,
        v_reasons
    );

    IF NOT v_eligible THEN
        RAISE EXCEPTION 'Merge denied: %', v_reasons;
    END IF;

    -- Lock dependency rows to prevent concurrent update races.
    FOR v_change IN
        SELECT pc.dependency_id,
               pc.previous_version,
               pc.proposed_version
        FROM pull_request_changes pc
        WHERE pc.pull_request_id = p_pull_request_id
        ORDER BY pc.dependency_id
    LOOP
        PERFORM 1
        FROM dependencies
        WHERE dependency_id = v_change.dependency_id
        FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Dependency disappeared during merge';
        END IF;

        IF version_compare(
            (
                SELECT current_version
                FROM dependencies
                WHERE dependency_id = v_change.dependency_id
            ),
            v_change.previous_version
        ) <> 0 THEN
            RAISE EXCEPTION
                'Dependency changed since PR creation';
        END IF;

        UPDATE dependencies
        SET current_version = v_change.proposed_version
        WHERE dependency_id = v_change.dependency_id;
    END LOOP;

    v_new_commit := md5(
        v_pr.source_commit_hash ||
        v_pr.target_commit_hash ||
        p_pull_request_id::TEXT ||
        p_strategy::TEXT
    );

    UPDATE pull_requests
    SET status = 'merged',
        selected_merge_strategy = p_strategy,
        merged_commit_hash = v_new_commit,
        merged_at = NOW()
    WHERE pull_request_id = p_pull_request_id;

    UPDATE branches
    SET head_commit = v_new_commit
    WHERE branch_id = v_pr.target_branch_id;

    INSERT INTO repository_audit_log (
        repository_id,
        actor,
        action,
        entity_type,
        entity_id,
        details
    )
    VALUES (
        v_pr.repository_id,
        p_actor,
        'pull_request_merged',
        'pull_request',
        p_pull_request_id,
        jsonb_build_object(
            'strategy', p_strategy,
            'commit', v_new_commit
        )
    );
END;
$$;

-- ------------------------------------------------------------
-- 20. Reporting views
-- ------------------------------------------------------------

CREATE VIEW dependency_inventory_report AS
SELECT
    r.repository_name,
    d.package_name,
    d.current_version,
    d.minimum_version,
    d.maximum_version,
    d.package_type,
    d.direct_dependency,
    d.license_identifier,
    d.vulnerability_count,
    d.last_audited_at
FROM dependencies d
JOIN repositories r
  ON r.repository_id = d.repository_id;

CREATE VIEW pull_request_governance_report AS
SELECT
    pr.pull_request_id,
    r.repository_name,
    pr.title,
    pr.status,
    pr.is_draft,
    pr.author_username,
    pr.source_commit_hash,
    pr.target_commit_hash,
    COUNT(DISTINCT cr.review_id)
        FILTER (WHERE cr.state = 'approved') AS approval_records,
    COUNT(DISTINCT sc.check_id)
        FILTER (WHERE sc.state = 'passed') AS passed_checks,
    COUNT(DISTINCT rc.conversation_id)
        FILTER (WHERE NOT rc.resolved) AS unresolved_conversations
FROM pull_requests pr
JOIN repositories r
  ON r.repository_id = pr.repository_id
LEFT JOIN code_reviews cr
  ON cr.pull_request_id = pr.pull_request_id
 AND cr.reviewed_commit_hash = pr.source_commit_hash
LEFT JOIN status_checks sc
  ON sc.pull_request_id = pr.pull_request_id
 AND sc.commit_hash = pr.source_commit_hash
LEFT JOIN review_conversations rc
  ON rc.pull_request_id = pr.pull_request_id
GROUP BY
    pr.pull_request_id,
    r.repository_name;

-- ------------------------------------------------------------
-- 21. Sample repository
-- ------------------------------------------------------------

INSERT INTO repositories (
    repository_name,
    description
)
VALUES (
    'enterprise-platform',
    'Enterprise application dependency governance demonstration'
);

INSERT INTO repository_members (
    repository_id, username, role
)
SELECT repository_id, member.username, member.role
FROM repositories
CROSS JOIN (
    VALUES
        ('project-owner', 'owner'),
        ('platform-reviewer', 'reviewer'),
        ('security-reviewer', 'maintainer'),
        ('developer-one', 'developer')
) AS member(username, role)
WHERE repository_name = 'enterprise-platform';

INSERT INTO branches (
    repository_id,
    branch_name,
    head_commit
)
SELECT repository_id, 'main', 'base-commit-001'
FROM repositories
WHERE repository_name = 'enterprise-platform';

INSERT INTO branches (
    repository_id,
    branch_name,
    head_commit,
    base_branch_id
)
SELECT
    repository_id,
    'dependency/quarterly-update',
    'dependency-commit-001',
    branch_id
FROM repositories r
JOIN branches b USING (repository_id)
WHERE r.repository_name = 'enterprise-platform'
  AND b.branch_name = 'main';

INSERT INTO dependencies (
    repository_id,
    package_name,
    current_version,
    minimum_version,
    package_type,
    direct_dependency,
    license_identifier,
    source_registry
)
SELECT
    repository_id,
    package_name,
    current_version,
    minimum_version,
    package_type::dependency_type,
    TRUE,
    license_identifier,
    'https://registry.example/packages'
FROM repositories
CROSS JOIN (
    VALUES
        ('httpx', '0.27.0', '0.25.0', 'runtime', 'BSD-3-Clause'),
        ('pydantic', '2.8.2', '2.5.0', 'runtime', 'MIT'),
        ('fastapi', '0.112.0', '0.100.0', 'runtime', 'MIT'),
        ('cryptography', '43.0.0', '42.0.0', 'runtime', 'Apache-2.0')
) AS packages(
    package_name,
    current_version,
    minimum_version,
    package_type,
    license_identifier
)
WHERE repository_name = 'enterprise-platform';

-- fastapi requires httpx and pydantic.
INSERT INTO dependency_relationships (
    repository_id,
    dependency_id,
    prerequisite_id
)
SELECT
    d.repository_id,
    d.dependency_id,
    p.dependency_id
FROM dependencies d
JOIN dependencies p
  ON p.repository_id = d.repository_id
WHERE d.package_name = 'fastapi'
  AND p.package_name IN ('httpx', 'pydantic');

INSERT INTO license_policies (
    repository_id,
    license_identifier,
    allowed
)
SELECT repository_id, license_identifier, TRUE
FROM repositories
CROSS JOIN (
    VALUES ('MIT'), ('Apache-2.0'), ('BSD-3-Clause')
) AS licenses(license_identifier)
WHERE repository_name = 'enterprise-platform';

INSERT INTO branch_protection_policies (
    repository_id,
    branch_id,
    required_approvals,
    require_status_checks,
    require_resolved_conversations,
    require_lockfile,
    allow_direct_push,
    allow_force_push,
    allow_branch_deletion,
    require_linear_history,
    dismiss_stale_approvals
)
SELECT
    b.repository_id,
    b.branch_id,
    2,
    TRUE,
    TRUE,
    TRUE,
    FALSE,
    FALSE,
    FALSE,
    TRUE,
    TRUE
FROM branches b
JOIN repositories r USING (repository_id)
WHERE r.repository_name = 'enterprise-platform'
  AND b.branch_name = 'main';

INSERT INTO required_status_checks (
    protection_id,
    check_name
)
SELECT
    protection_id,
    check_name
FROM branch_protection_policies
CROSS JOIN (
    VALUES
        ('unit-tests'),
        ('security-scan'),
        ('license-audit')
) AS checks(check_name);

-- A valid lockfile for the proposed source branch.
INSERT INTO dependency_lockfiles (
    repository_id,
    branch_id,
    lockfile_name,
    content_hash,
    dependency_count
)
SELECT
    repository_id,
    branch_id,
    'dependencies.lock',
    md5('dependency-lock-v1'),
    4
FROM branches
WHERE branch_name = 'dependency/quarterly-update';

-- ------------------------------------------------------------
-- 22. Create dependency update records
-- ------------------------------------------------------------

INSERT INTO dependency_updates (
    dependency_id,
    old_version,
    proposed_version,
    update_type,
    security_update,
    compatibility_verified
)
SELECT
    dependency_id,
    current_version,
    proposed_version,
    update_type,
    FALSE,
    TRUE
FROM dependencies
JOIN (
    VALUES
        ('httpx', '0.28.1', 'minor'),
        ('pydantic', '2.9.2', 'minor'),
        ('fastapi', '0.115.0', 'minor')
) AS updates(package_name, proposed_version, update_type)
USING (package_name)
WHERE dependencies.package_name = updates.package_name;

-- ------------------------------------------------------------
-- 23. Open a dependency-update Pull Request
-- ------------------------------------------------------------

INSERT INTO pull_requests (
    repository_id,
    source_branch_id,
    target_branch_id,
    title,
    description,
    author_username,
    status,
    is_draft,
    source_commit_hash,
    target_commit_hash
)
SELECT
    r.repository_id,
    source.branch_id,
    target.branch_id,
    'Quarterly dependency updates',
    'Version upgrades with compatibility and security checks.',
    'developer-one',
    'open',
    FALSE,
    'dependency-commit-001',
    'base-commit-001'
FROM repositories r
JOIN branches source
  ON source.repository_id = r.repository_id
 AND source.branch_name = 'dependency/quarterly-update'
JOIN branches target
  ON target.repository_id = r.repository_id
 AND target.branch_name = 'main'
WHERE r.repository_name = 'enterprise-platform';

INSERT INTO pull_request_changes (
    pull_request_id,
    dependency_id,
    previous_version,
    proposed_version,
    update_id
)
SELECT
    pr.pull_request_id,
    d.dependency_id,
    u.old_version,
    u.proposed_version,
    u.update_id
FROM pull_requests pr
JOIN repositories r USING (repository_id)
JOIN dependency_updates u ON TRUE
JOIN dependencies d
  ON d.dependency_id = u.dependency_id
WHERE r.repository_name = 'enterprise-platform'
  AND pr.title = 'Quarterly dependency updates'
  AND pr.status = 'open';

-- ------------------------------------------------------------
-- 24. Status checks for the proposed commit
-- ------------------------------------------------------------

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    state,
    commit_hash,
    details
)
SELECT
    pr.pull_request_id,
    check_name,
    'passed',
    pr.source_commit_hash,
    'Automated validation completed successfully'
FROM pull_requests pr
CROSS JOIN (
    VALUES
        ('unit-tests'),
        ('security-scan'),
        ('license-audit')
) AS checks(check_name)
WHERE pr.title = 'Quarterly dependency updates';

-- ------------------------------------------------------------
-- 25. Eligible review decisions
-- ------------------------------------------------------------

INSERT INTO code_reviews (
    pull_request_id,
    reviewer_username,
    state,
    reviewed_commit_hash,
    review_body
)
SELECT
    pr.pull_request_id,
    reviewer.username,
    'approved',
    pr.source_commit_hash,
    reviewer.review_body
FROM pull_requests pr
CROSS JOIN (
    VALUES
        ('security-reviewer', 'Security and license checks reviewed'),
        ('platform-reviewer', 'Compatibility and version changes reviewed')
) AS reviewer(username, review_body)
WHERE pr.title = 'Quarterly dependency updates';

INSERT INTO review_comments (
    review_id,
    file_path,
    line_number,
    comment_body,
    is_inline
)
SELECT
    cr.review_id,
    'requirements.txt',
    12,
    'The selected version is compatible with the application constraints.',
    TRUE
FROM code_reviews cr
JOIN pull_requests pr USING (pull_request_id)
WHERE pr.title = 'Quarterly dependency updates'
  AND cr.reviewer_username = 'platform-reviewer';

INSERT INTO review_conversations (
    pull_request_id,
    discussion_topic,
    resolved,
    resolved_by,
    resolved_at
)
SELECT
    pull_request_id,
    'Dependency compatibility analysis',
    TRUE,
    'platform-reviewer',
    NOW()
FROM pull_requests
WHERE title = 'Quarterly dependency updates';

-- ------------------------------------------------------------
-- 26. A separate failure scenario
-- ------------------------------------------------------------

INSERT INTO pull_requests (
    repository_id,
    source_branch_id,
    target_branch_id,
    title,
    author_username,
    status,
    is_draft,
    source_commit_hash,
    target_commit_hash
)
SELECT
    r.repository_id,
    source.branch_id,
    target.branch_id,
    'Experimental dependency update',
    'developer-one',
    'open',
    FALSE,
    'experimental-commit-001',
    'base-commit-001'
FROM repositories r
JOIN branches source
  ON source.repository_id = r.repository_id
 AND source.branch_name = 'dependency/quarterly-update'
JOIN branches target
  ON target.repository_id = r.repository_id
 AND target.branch_name = 'main'
WHERE r.repository_name = 'enterprise-platform';

INSERT INTO review_conversations (
    pull_request_id,
    discussion_topic,
    resolved
)
SELECT
    pull_request_id,
    'Unresolved compatibility concern',
    FALSE
FROM pull_requests
WHERE title = 'Experimental dependency update';

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    state,
    commit_hash
)
SELECT
    pull_request_id,
    'security-scan',
    'failed',
    source_commit_hash
FROM pull_requests
WHERE title = 'Experimental dependency update';

-- ------------------------------------------------------------
-- 27. Retrieval: dependency inventory
-- ------------------------------------------------------------

SELECT *
FROM dependency_inventory_report
ORDER BY repository_name, package_name;

-- ------------------------------------------------------------
-- 28. Retrieval: dependency installation order
-- ------------------------------------------------------------

WITH RECURSIVE resolution AS (
    SELECT
        d.dependency_id,
        d.package_name,
        0 AS depth,
        ARRAY[d.dependency_id] AS path
    FROM dependencies d
    WHERE d.direct_dependency

    UNION ALL

    SELECT
        prerequisite.dependency_id,
        prerequisite.package_name,
        r.depth + 1,
        r.path || prerequisite.dependency_id
    FROM resolution r
    JOIN dependency_relationships rel
      ON rel.dependency_id = r.dependency_id
    JOIN dependencies prerequisite
      ON prerequisite.dependency_id = rel.prerequisite_id
    WHERE NOT prerequisite.dependency_id = ANY(r.path)
)
SELECT
    package_name,
    MAX(depth) AS maximum_dependency_depth
FROM resolution
GROUP BY package_name
ORDER BY maximum_dependency_depth, package_name;

-- ------------------------------------------------------------
-- 29. Validation: dependency version constraints
-- ------------------------------------------------------------

SELECT
    package_name,
    current_version,
    minimum_version,
    maximum_version,
    CASE
        WHEN version_compare(
            current_version, minimum_version
        ) < 0 THEN 'BELOW_MINIMUM'
        WHEN maximum_version IS NOT NULL
         AND version_compare(
            current_version, maximum_version
         ) > 0 THEN 'ABOVE_MAXIMUM'
        ELSE 'VALID'
    END AS validation_result
FROM dependencies;

-- ------------------------------------------------------------
-- 30. Aggregation: repository dependency statistics
-- ------------------------------------------------------------

SELECT
    r.repository_name,
    COUNT(d.dependency_id) AS total_dependencies,
    COUNT(*) FILTER (
        WHERE d.direct_dependency
    ) AS direct_dependencies,
    COUNT(*) FILTER (
        WHERE NOT d.direct_dependency
    ) AS transitive_dependencies,
    SUM(d.vulnerability_count) AS reported_vulnerabilities,
    COUNT(DISTINCT d.license_identifier) AS distinct_licenses
FROM repositories r
LEFT JOIN dependencies d
  ON d.repository_id = r.repository_id
GROUP BY r.repository_id, r.repository_name;

-- ------------------------------------------------------------
-- 31. Evaluation: policy violations
-- ------------------------------------------------------------

SELECT *
FROM dependency_policy_violations(
    (
        SELECT repository_id
        FROM repositories
        WHERE repository_name = 'enterprise-platform'
    )
);

-- ------------------------------------------------------------
-- 32. Evaluation: Pull Request eligibility
-- ------------------------------------------------------------

SELECT
    pr.pull_request_id,
    pr.title,
    result.eligible,
    result.reasons
FROM pull_requests pr
CROSS JOIN LATERAL evaluate_merge_eligibility(
    pr.pull_request_id
) result
ORDER BY pr.pull_request_id;

-- ------------------------------------------------------------
-- 33. Reporting: review and status-check activity
-- ------------------------------------------------------------

SELECT *
FROM pull_request_governance_report
ORDER BY pull_request_id;

-- ------------------------------------------------------------
-- 34. Transactional merge
--
-- The valid dependency-update PR is merged only if every
-- governance condition passes.
-- ------------------------------------------------------------

DO $$
DECLARE
    v_pr_id BIGINT;
BEGIN
    SELECT pull_request_id
    INTO v_pr_id
    FROM pull_requests
    WHERE title = 'Quarterly dependency updates';

    CALL merge_pull_request(
        v_pr_id,
        'squash',
        'project-owner'
    );

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Merge was rejected: %', SQLERRM;
END;
$$;

-- ------------------------------------------------------------
-- 35. Final repository state
-- ------------------------------------------------------------

SELECT
    repository_name,
    package_name,
    current_version,
    license_identifier
FROM dependency_inventory_report
ORDER BY package_name;

SELECT
    pull_request_id,
    title,
    status,
    selected_merge_strategy,
    merged_at
FROM pull_requests
ORDER BY pull_request_id;

SELECT
    actor,
    action,
    entity_type,
    entity_id,
    created_at
FROM repository_audit_log
ORDER BY audit_id;

COMMIT;
