-- PostgreSQL 15+
-- Keyword-argument concepts represented as explicit named configuration,
-- JSONB option payloads with validation, and relational governance constraints.
--
-- The schema separates Pull Request lifecycle, code review decisions,
-- approval eligibility, status checks, review discussions, and branch policy.
-- A database function evaluates current merge prerequisites.

BEGIN;

CREATE SCHEMA IF NOT EXISTS repository_governance;
SET search_path TO repository_governance, public;

CREATE TYPE pull_request_state AS ENUM (
    'draft',
    'open',
    'closed',
    'merged'
);

CREATE TYPE review_state AS ENUM (
    'approved',
    'changes_requested',
    'commented'
);

CREATE TYPE check_state AS ENUM (
    'pending',
    'success',
    'failure'
);

CREATE TYPE merge_strategy AS ENUM (
    'merge_commit',
    'squash',
    'rebase'
);

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (repository_name ~ '^[a-zA-Z0-9._-]+$'),
    CHECK (length(default_branch) > 0)
);

CREATE TABLE repository_members (
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    username TEXT NOT NULL,
    role TEXT NOT NULL CHECK (
        role IN ('read', 'write', 'maintain', 'admin')
    ),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (repository_id, username)
);

CREATE TABLE branches (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    head_sha TEXT NOT NULL,
    protected BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    UNIQUE (repository_id, branch_name),
    CHECK (length(branch_name) > 0),
    CHECK (head_sha ~ '^[0-9a-f]{7,40}$')
);

CREATE TABLE commits (
    commit_sha TEXT PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    author_username TEXT NOT NULL,
    committed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    message TEXT NOT NULL,
    CHECK (commit_sha ~ '^[0-9a-f]{7,40}$'),
    CHECK (length(message) > 0)
);

CREATE TABLE commit_files (
    commit_sha TEXT NOT NULL
        REFERENCES commits(commit_sha) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    change_kind TEXT NOT NULL CHECK (
        change_kind IN ('added', 'modified', 'deleted', 'renamed')
    ),
    PRIMARY KEY (commit_sha, file_path),
    CHECK (length(file_path) > 0),
    CHECK (left(file_path, 1) <> '/')
);

CREATE TABLE pull_requests (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    source_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    author_username TEXT NOT NULL,
    state pull_request_state NOT NULL DEFAULT 'draft',
    is_draft BOOLEAN NOT NULL DEFAULT TRUE,
    head_sha TEXT,
    base_sha TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMPTZ,
    merged_at TIMESTAMPTZ,
    merge_actor TEXT,
    merge_strategy merge_strategy,
    UNIQUE (pull_request_id, repository_id),
    CHECK (length(trim(title)) > 0),
    CHECK (source_branch_id <> target_branch_id),
    CHECK (
        (state = 'draft' AND is_draft)
        OR state <> 'draft'
    ),
    CHECK (
        (state = 'merged' AND merged_at IS NOT NULL
            AND merge_actor IS NOT NULL AND merge_strategy IS NOT NULL)
        OR state <> 'merged'
    ),
    CHECK (
        (state = 'closed' AND closed_at IS NOT NULL)
        OR state <> 'closed'
    ),
    CHECK (
        head_sha IS NULL OR head_sha ~ '^[0-9a-f]{7,40}$'
    ),
    CHECK (
        base_sha IS NULL OR base_sha ~ '^[0-9a-f]{7,40}$'
    )
);

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    commit_sha TEXT NOT NULL REFERENCES commits(commit_sha),
    sequence_number INTEGER NOT NULL CHECK (sequence_number > 0),
    PRIMARY KEY (pull_request_id, commit_sha),
    UNIQUE (pull_request_id, sequence_number)
);

CREATE TABLE review_requests (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    reviewer_username TEXT NOT NULL,
    requested_by TEXT NOT NULL,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fulfilled_at TIMESTAMPTZ,
    PRIMARY KEY (pull_request_id, reviewer_username)
);

CREATE TABLE reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    reviewer_username TEXT NOT NULL,
    reviewed_commit_sha TEXT NOT NULL REFERENCES commits(commit_sha),
    state review_state NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dismissed_at TIMESTAMPTZ,
    dismissal_reason TEXT,
    eligible BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (review_id, pull_request_id),
    CHECK (
        (dismissed_at IS NULL AND dismissal_reason IS NULL)
        OR (dismissed_at IS NOT NULL AND dismissal_reason IS NOT NULL)
    )
);

CREATE TABLE review_comments (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES reviews(review_id) ON DELETE CASCADE,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    file_path TEXT,
    line_number INTEGER,
    body TEXT NOT NULL,
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ,
    CHECK (length(trim(body)) > 0),
    CHECK (line_number IS NULL OR line_number > 0),
    CHECK (
        (is_resolved AND resolved_at IS NOT NULL)
        OR (NOT is_resolved AND resolved_at IS NULL)
    )
);

CREATE TABLE status_checks (
    status_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    commit_sha TEXT NOT NULL REFERENCES commits(commit_sha),
    check_name TEXT NOT NULL,
    state check_state NOT NULL DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    details TEXT NOT NULL DEFAULT '',
    UNIQUE (pull_request_id, commit_sha, check_name),
    CHECK (length(trim(check_name)) > 0),
    CHECK (
        completed_at IS NULL OR
        (started_at IS NOT NULL AND completed_at >= started_at)
    )
);

CREATE TABLE branch_protection_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE
        REFERENCES branches(branch_id) ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 2
        CHECK (required_approvals >= 0),
    dismiss_stale_reviews BOOLEAN NOT NULL DEFAULT TRUE,
    require_conversation_resolution BOOLEAN NOT NULL DEFAULT TRUE,
    require_linear_history BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_direct_pushes BOOLEAN NOT NULL DEFAULT TRUE,
    allow_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_deletion BOOLEAN NOT NULL DEFAULT FALSE,
    enforce_for_administrators BOOLEAN NOT NULL DEFAULT TRUE,
    allow_bypass BOOLEAN NOT NULL DEFAULT FALSE,
    require_signed_commits BOOLEAN NOT NULL DEFAULT FALSE,
    merge_strategies merge_strategy[] NOT NULL
        DEFAULT ARRAY['squash']::merge_strategy[],
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (cardinality(merge_strategies) > 0)
);

CREATE TABLE required_status_checks (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    PRIMARY KEY (policy_id, check_name),
    CHECK (length(trim(check_name)) > 0)
);

CREATE TABLE policy_audit_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id) ON DELETE CASCADE,
    actor_username TEXT NOT NULL,
    action TEXT NOT NULL,
    old_configuration JSONB,
    new_configuration JSONB NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pull_requests_repository_state
    ON pull_requests(repository_id, state, updated_at DESC);

CREATE INDEX idx_reviews_pr_commit_state
    ON reviews(pull_request_id, reviewed_commit_sha, state)
    WHERE dismissed_at IS NULL AND eligible;

CREATE INDEX idx_comments_unresolved
    ON review_comments(pull_request_id, comment_id)
    WHERE NOT is_resolved;

CREATE INDEX idx_status_checks_required_lookup
    ON status_checks(pull_request_id, commit_sha, check_name, state);

CREATE INDEX idx_pull_request_commits_latest
    ON pull_request_commits(pull_request_id, sequence_number DESC);

CREATE INDEX idx_policy_audit_events_recent
    ON policy_audit_events(policy_id, occurred_at DESC);

-- These triggers keep a Pull Request's repository consistent with both
-- referenced branches and ensure review requests use active repository members.
CREATE FUNCTION validate_pull_request_branches()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    source_repository BIGINT;
    target_repository BIGINT;
BEGIN
    SELECT repository_id
    INTO source_repository
    FROM branches
    WHERE branch_id = NEW.source_branch_id
      AND deleted_at IS NULL;

    SELECT repository_id
    INTO target_repository
    FROM branches
    WHERE branch_id = NEW.target_branch_id
      AND deleted_at IS NULL;

    IF source_repository IS NULL OR target_repository IS NULL THEN
        RAISE EXCEPTION 'Pull Request branches must exist and be active';
    END IF;

    IF source_repository <> NEW.repository_id
       OR target_repository <> NEW.repository_id THEN
        RAISE EXCEPTION
            'Source branch, target branch, and Pull Request must share a repository';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM repository_members
        WHERE repository_id = NEW.repository_id
          AND username = NEW.author_username
          AND active
          AND role IN ('write', 'maintain', 'admin')
    ) THEN
        RAISE EXCEPTION 'Pull Request author lacks write permission';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_pull_request_branches
BEFORE INSERT OR UPDATE OF repository_id, source_branch_id,
    target_branch_id, author_username
ON pull_requests
FOR EACH ROW
EXECUTE FUNCTION validate_pull_request_branches();

CREATE FUNCTION validate_review_reviewer()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    current_repository BIGINT;
BEGIN
    SELECT repository_id
    INTO current_repository
    FROM pull_requests
    WHERE pull_request_id = NEW.pull_request_id;

    IF NOT EXISTS (
        SELECT 1
        FROM repository_members
        WHERE repository_id = current_repository
          AND username = NEW.reviewer_username
          AND active
          AND role IN ('write', 'maintain', 'admin')
    ) THEN
        RAISE EXCEPTION 'Reviewer is not an active eligible repository member';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM review_requests
        WHERE pull_request_id = NEW.pull_request_id
          AND reviewer_username = NEW.reviewer_username
    ) THEN
        RAISE EXCEPTION 'Reviewer has not been requested for this Pull Request';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pull_request_commits
        WHERE pull_request_id = NEW.pull_request_id
          AND commit_sha = NEW.reviewed_commit_sha
    ) THEN
        RAISE EXCEPTION 'Reviewed commit is not part of this Pull Request';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_review_reviewer
BEFORE INSERT OR UPDATE OF pull_request_id, reviewer_username,
    reviewed_commit_sha
ON reviews
FOR EACH ROW
EXECUTE FUNCTION validate_review_reviewer();

CREATE FUNCTION validate_review_comment_relationship()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    review_pr_id BIGINT;
BEGIN
    SELECT pull_request_id
    INTO review_pr_id
    FROM reviews
    WHERE review_id = NEW.review_id;

    IF review_pr_id IS DISTINCT FROM NEW.pull_request_id THEN
        RAISE EXCEPTION
            'Review comment and review must reference the same Pull Request';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_review_comment_relationship
BEFORE INSERT OR UPDATE OF review_id, pull_request_id
ON review_comments
FOR EACH ROW
EXECUTE FUNCTION validate_review_comment_relationship();

CREATE FUNCTION audit_branch_policy()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    current_policy_id BIGINT;
BEGIN
    current_policy_id := COALESCE(NEW.policy_id, OLD.policy_id);

    INSERT INTO policy_audit_events (
        policy_id,
        actor_username,
        action,
        old_configuration,
        new_configuration
    )
    VALUES (
        current_policy_id,
        current_user,
        TG_OP,
        CASE WHEN TG_OP = 'INSERT' THEN NULL
             ELSE to_jsonb(OLD) END,
        CASE WHEN TG_OP = 'DELETE' THEN '{}'::jsonb
             ELSE to_jsonb(NEW) END
    );

    RETURN COALESCE(NEW, OLD);
END;
$$;

CREATE TRIGGER trg_audit_branch_policy
AFTER INSERT OR UPDATE OR DELETE
ON branch_protection_policies
FOR EACH ROW
EXECUTE FUNCTION audit_branch_policy();

-- Named settings are represented in a JSONB configuration object. This
-- function rejects unknown keys and wrong JSON types instead of silently
-- accepting misspelled settings, similar to a validated keyword API.
CREATE FUNCTION validate_policy_options(options JSONB)
RETURNS JSONB
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    item RECORD;
    allowed_keys TEXT[] := ARRAY[
        'required_approvals',
        'dismiss_stale_reviews',
        'require_conversation_resolution',
        'require_linear_history',
        'restrict_direct_pushes',
        'allow_force_push',
        'allow_deletion',
        'enforce_for_administrators',
        'allow_bypass',
        'require_signed_commits'
    ];
BEGIN
    IF jsonb_typeof(options) <> 'object' THEN
        RAISE EXCEPTION 'Policy options must be a JSON object';
    END IF;

    FOR item IN SELECT key, value FROM jsonb_each(options)
    LOOP
        IF NOT item.key = ANY (allowed_keys) THEN
            RAISE EXCEPTION 'Unknown policy option: %', item.key;
        END IF;

        IF item.key = 'required_approvals' THEN
            IF jsonb_typeof(item.value) <> 'number' THEN
                RAISE EXCEPTION 'required_approvals must be numeric';
            END IF;

            IF (item.value #>> '{}')::NUMERIC < 0
               OR (item.value #>> '{}')::NUMERIC <>
                  trunc((item.value #>> '{}')::NUMERIC) THEN
                RAISE EXCEPTION
                    'required_approvals must be a non-negative integer';
            END IF;
        ELSE
            IF jsonb_typeof(item.value) <> 'boolean' THEN
                RAISE EXCEPTION '% must be boolean', item.key;
            END IF;
        END IF;
    END LOOP;

    RETURN options;
END;
$$;

-- A view provides a diagnostic evaluation rather than silently merging data.
-- Only approvals on the current PR head count when stale reviews are dismissed.
CREATE VIEW pull_request_merge_eligibility AS
WITH latest_commits AS (
    SELECT DISTINCT ON (pull_request_id)
        pull_request_id,
        commit_sha AS latest_sha
    FROM pull_request_commits
    ORDER BY pull_request_id, sequence_number DESC
),
active_reviews AS (
    SELECT
        r.pull_request_id,
        r.reviewer_username,
        r.state,
        r.reviewed_commit_sha,
        row_number() OVER (
            PARTITION BY r.pull_request_id, r.reviewer_username
            ORDER BY r.submitted_at DESC, r.review_id DESC
        ) AS reviewer_review_order
    FROM reviews r
    JOIN latest_commits lc
      ON lc.pull_request_id = r.pull_request_id
     AND lc.latest_sha = r.reviewed_commit_sha
    WHERE r.dismissed_at IS NULL
      AND r.eligible
),
review_totals AS (
    SELECT
        pull_request_id,
        count(*) FILTER (
            WHERE state = 'approved'
        ) AS approvals,
        bool_or(state = 'changes_requested') AS changes_requested
    FROM active_reviews
    WHERE reviewer_review_order = 1
    GROUP BY pull_request_id
),
check_totals AS (
    SELECT
        pr.pull_request_id,
        count(rsc.check_name) FILTER (
            WHERE sc.state = 'success'
              AND sc.commit_sha = lc.latest_sha
        ) AS successful_required_checks,
        count(rsc.check_name) AS total_required_checks
    FROM pull_requests pr
    LEFT JOIN latest_commits lc
      ON lc.pull_request_id = pr.pull_request_id
    LEFT JOIN branches b
      ON b.branch_id = pr.target_branch_id
    LEFT JOIN branch_protection_policies bp
      ON bp.branch_id = b.branch_id
    LEFT JOIN required_status_checks rsc
      ON rsc.policy_id = bp.policy_id
    LEFT JOIN status_checks sc
      ON sc.pull_request_id = pr.pull_request_id
     AND sc.check_name = rsc.check_name
    GROUP BY pr.pull_request_id
),
comment_totals AS (
    SELECT
        pr.pull_request_id,
        count(rc.comment_id) FILTER (
            WHERE NOT rc.is_resolved
        ) AS unresolved_comments
    FROM pull_requests pr
    LEFT JOIN review_comments rc
      ON rc.pull_request_id = pr.pull_request_id
    GROUP BY pr.pull_request_id
)
SELECT
    pr.pull_request_id,
    repo.repository_name,
    pr.title,
    pr.state,
    pr.is_draft,
    b.branch_name AS protected_target,
    COALESCE(rt.approvals, 0) AS current_approvals,
    bp.required_approvals,
    COALESCE(rt.changes_requested, FALSE) AS changes_requested,
    COALESCE(ct.successful_required_checks, 0) AS successful_required_checks,
    COALESCE(ct.total_required_checks, 0) AS total_required_checks,
    COALESCE(cmt.unresolved_comments, 0) AS unresolved_comments,
    (
        pr.state = 'open'
        AND NOT pr.is_draft
        AND COALESCE(rt.approvals, 0) >= bp.required_approvals
        AND NOT COALESCE(rt.changes_requested, FALSE)
        AND COALESCE(ct.successful_required_checks, 0)
            = COALESCE(ct.total_required_checks, 0)
        AND (
            NOT bp.require_conversation_resolution
            OR COALESCE(cmt.unresolved_comments, 0) = 0
        )
    ) AS merge_eligible
FROM pull_requests pr
JOIN repositories repo ON repo.repository_id = pr.repository_id
JOIN branches b ON b.branch_id = pr.target_branch_id
LEFT JOIN branch_protection_policies bp ON bp.branch_id = b.branch_id
LEFT JOIN review_totals rt ON rt.pull_request_id = pr.pull_request_id
LEFT JOIN check_totals ct ON ct.pull_request_id = pr.pull_request_id
LEFT JOIN comment_totals cmt ON cmt.pull_request_id = pr.pull_request_id;

-- Seed repository identities and permissions.
INSERT INTO repositories (repository_name, default_branch)
VALUES ('payments-platform', 'main');

INSERT INTO repository_members (repository_id, username, role)
SELECT repository_id, username, role
FROM repositories
CROSS JOIN (
    VALUES
        ('release-maintainer', 'maintain'),
        ('Maya', 'write'),
        ('Daniel', 'write'),
        ('Aisha', 'write'),
        ('developer-lee', 'write')
) AS members(username, role)
WHERE repository_name = 'payments-platform';

INSERT INTO branches (
    repository_id, branch_name, head_sha, protected
)
SELECT repository_id, branch_name, head_sha, protected
FROM repositories
CROSS JOIN (
    VALUES
        ('main', '1111111', TRUE),
        ('feature/signed-artifacts', 'a1b2c3d', FALSE),
        ('feature/pending-policy', 'c1d2e3f', FALSE)
) AS branch_data(branch_name, head_sha, protected)
WHERE repository_name = 'payments-platform';

INSERT INTO branch_protection_policies (
    branch_id,
    required_approvals,
    dismiss_stale_reviews,
    require_conversation_resolution,
    require_linear_history,
    restrict_direct_pushes,
    allow_force_push,
    allow_deletion,
    enforce_for_administrators,
    allow_bypass,
    require_signed_commits,
    merge_strategies
)
SELECT
    branch_id,
    2,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    FALSE,
    FALSE,
    TRUE,
    FALSE,
    TRUE,
    ARRAY['squash', 'rebase']::merge_strategy[]
FROM branches
WHERE branch_name = 'main';

INSERT INTO required_status_checks (policy_id, check_name)
SELECT policy_id, check_name
FROM branch_protection_policies
CROSS JOIN (
    VALUES ('unit-tests'), ('security-scan'), ('lint')
) AS required(check_name);

INSERT INTO commits (
    commit_sha, repository_id, author_username, message
)
SELECT sha, repository_id, author, message
FROM repositories
CROSS JOIN (
    VALUES
        (
            'a1b2c3d',
            'developer-lee',
            'Enforce signed artifact verification'
        ),
        (
            'b2c3d4e',
            'developer-lee',
            'Handle artifact verification edge cases'
        ),
        (
            'c1d2e3f',
            'developer-lee',
            'Prepare policy configuration validation'
        )
) AS commit_data(sha, author, message)
WHERE repository_name = 'payments-platform';

INSERT INTO commit_files (commit_sha, file_path, change_kind)
VALUES
    ('a1b2c3d', 'src/signature.py', 'modified'),
    ('a1b2c3d', 'tests/test_signature.py', 'added'),
    ('b2c3d4e', 'src/signature.py', 'modified'),
    ('c1d2e3f', 'src/policy.py', 'added');

INSERT INTO pull_requests (
    repository_id,
    title,
    description,
    source_branch_id,
    target_branch_id,
    author_username,
    state,
    is_draft,
    head_sha,
    base_sha
)
SELECT
    repo.repository_id,
    pr_data.title,
    pr_data.description,
    source.branch_id,
    target.branch_id,
    'developer-lee',
    pr_data.state::pull_request_state,
    pr_data.is_draft,
    pr_data.head_sha,
    '1111111'
FROM repositories repo
CROSS JOIN (
    VALUES
        (
            'Enforce signed deployment artifacts',
            'Verify signatures before accepting deployment artifacts.',
            'open',
            FALSE,
            'a1b2c3d',
            'feature/signed-artifacts'
        ),
        (
            'Prepare branch policy validation',
            'Draft change for typed policy configuration.',
            'draft',
            TRUE,
            'c1d2e3f',
            'feature/pending-policy'
        )
) AS pr_data(
    title, description, state, is_draft, head_sha, source_branch
)
JOIN branches source
  ON source.repository_id = repo.repository_id
 AND source.branch_name = pr_data.source_branch
JOIN branches target
  ON target.repository_id = repo.repository_id
 AND target.branch_name = 'main'
WHERE repo.repository_name = 'payments-platform';

INSERT INTO pull_request_commits (
    pull_request_id, commit_sha, sequence_number
)
SELECT pr.pull_request_id, commit.commit_sha, commit.sequence_number
FROM pull_requests pr
CROSS JOIN (
    VALUES
        ('Enforce signed deployment artifacts', 'a1b2c3d', 1),
        ('Prepare branch policy validation', 'c1d2e3f', 1)
) AS commit(commit_title, commit_sha, sequence_number)
WHERE pr.title = commit.commit_title;

INSERT INTO review_requests (
    pull_request_id, reviewer_username, requested_by
)
SELECT pr.pull_request_id, reviewers.username, 'developer-lee'
FROM pull_requests pr
CROSS JOIN (
    VALUES ('Maya'), ('Daniel')
) AS reviewers(username)
WHERE pr.title = 'Enforce signed deployment artifacts';

INSERT INTO reviews (
    pull_request_id,
    reviewer_username,
    reviewed_commit_sha,
    state,
    eligible
)
SELECT
    pr.pull_request_id,
    review_data.username,
    'a1b2c3d',
    review_data.state::review_state,
    TRUE
FROM pull_requests pr
CROSS JOIN (
    VALUES
        ('Maya', 'approved'),
        ('Daniel', 'approved')
) AS review_data(username, state)
WHERE pr.title = 'Enforce signed deployment artifacts';

INSERT INTO review_comments (
    review_id,
    pull_request_id,
    file_path,
    line_number,
    body,
    is_resolved,
    resolved_at
)
SELECT
    r.review_id,
    r.pull_request_id,
    'src/signature.py',
    42,
    'Confirm rejection of unsigned deployment artifacts.',
    FALSE,
    NULL
FROM reviews r
JOIN pull_requests pr
  ON pr.pull_request_id = r.pull_request_id
WHERE pr.title = 'Enforce signed deployment artifacts'
  AND r.reviewer_username = 'Maya';

INSERT INTO status_checks (
    pull_request_id,
    commit_sha,
    check_name,
    state,
    started_at,
    completed_at,
    details
)
SELECT
    pr.pull_request_id,
    'a1b2c3d',
    check_data.check_name,
    check_data.state::check_state,
    CURRENT_TIMESTAMP - INTERVAL '2 minutes',
    CURRENT_TIMESTAMP,
    check_data.details
FROM pull_requests pr
CROSS JOIN (
    VALUES
        ('unit-tests', 'success', 'All tests passed'),
        ('security-scan', 'success', 'No blocking findings'),
        ('lint', 'success', 'Static checks passed')
) AS check_data(check_name, state, details)
WHERE pr.title = 'Enforce signed deployment artifacts';

-- Demonstrate configuration validation. A misspelled keyword-style setting
-- must fail instead of being silently ignored.
SELECT validate_policy_options(
    '{
        "required_approvals": 2,
        "dismiss_stale_reviews": true,
        "require_linear_history": true,
        "allow_force_push": false
    }'::jsonb
) AS validated_named_options;

-- Current merge eligibility, including unresolved review conversations.
SELECT *
FROM pull_request_merge_eligibility
ORDER BY pull_request_id;

-- The policy is relational rather than embedded entirely in application code.
SELECT
    repo.repository_name,
    branch.branch_name,
    policy.required_approvals,
    policy.dismiss_stale_reviews,
    policy.require_conversation_resolution,
    policy.require_linear_history,
    policy.restrict_direct_pushes,
    policy.allow_force_push,
    policy.allow_deletion,
    policy.enforce_for_administrators,
    policy.allow_bypass,
    policy.require_signed_commits,
    policy.merge_strategies,
    array_agg(required.check_name ORDER BY required.check_name)
        AS required_checks
FROM branch_protection_policies policy
JOIN branches branch ON branch.branch_id = policy.branch_id
JOIN repositories repo ON repo.repository_id = branch.repository_id
LEFT JOIN required_status_checks required
    ON required.policy_id = policy.policy_id
GROUP BY repo.repository_name, branch.branch_name, policy.policy_id;

-- Unresolved inline discussions remain a separate review-quality condition.
SELECT
    pr.pull_request_id,
    pr.title,
    comment.comment_id,
    comment.file_path,
    comment.line_number,
    comment.body
FROM review_comments comment
JOIN pull_requests pr
  ON pr.pull_request_id = comment.pull_request_id
WHERE NOT comment.is_resolved
ORDER BY pr.pull_request_id, comment.comment_id;

-- Demonstrate transactional dismissal of stale reviews when a new commit
-- becomes the Pull Request head. In production, head updates and review
-- invalidation must be performed atomically by the application or a trigger.
BEGIN;

WITH selected_pr AS (
    SELECT pull_request_id
    FROM pull_requests
    WHERE title = 'Enforce signed deployment artifacts'
    FOR UPDATE
),
new_head AS (
    SELECT commit_sha
    FROM commits
    WHERE commit_sha = 'b2c3d4e'
)
INSERT INTO pull_request_commits (
    pull_request_id, commit_sha, sequence_number
)
SELECT
    selected_pr.pull_request_id,
    new_head.commit_sha,
    COALESCE(
        (
            SELECT max(sequence_number) + 1
            FROM pull_request_commits existing
            WHERE existing.pull_request_id = selected_pr.pull_request_id
        ),
        1
    )
FROM selected_pr
CROSS JOIN new_head
ON CONFLICT (pull_request_id, commit_sha) DO NOTHING;

UPDATE pull_requests pr
SET head_sha = 'b2c3d4e',
    updated_at = CURRENT_TIMESTAMP
FROM selected_pr
WHERE pr.pull_request_id = selected_pr.pull_request_id;

UPDATE reviews r
SET dismissed_at = CURRENT_TIMESTAMP,
    dismissal_reason = 'Source branch advanced after review'
FROM selected_pr
WHERE r.pull_request_id = selected_pr.pull_request_id
  AND r.reviewed_commit_sha <> 'b2c3d4e'
  AND r.dismissed_at IS NULL
  AND EXISTS (
      SELECT 1
      FROM branch_protection_policies bp
      JOIN branches b ON b.branch_id = bp.branch_id
      WHERE b.branch_id = (
          SELECT target_branch_id
          FROM pull_requests
          WHERE pull_request_id = r.pull_request_id
      )
      AND bp.dismiss_stale_reviews
  );

COMMIT;

-- New checks are required for the latest revision, even when older checks passed.
INSERT INTO status_checks (
    pull_request_id,
    commit_sha,
    check_name,
    state,
    started_at,
    completed_at,
    details
)
SELECT
    pr.pull_request_id,
    'b2c3d4e',
    required.check_name,
    'pending',
    CURRENT_TIMESTAMP,
    NULL,
    'Re-run required checks for the new head'
FROM pull_requests pr
JOIN branches b ON b.branch_id = pr.target_branch_id
JOIN branch_protection_policies bp ON bp.branch_id = b.branch_id
JOIN required_status_checks required ON required.policy_id = bp.policy_id
WHERE pr.title = 'Enforce signed deployment artifacts'
ON CONFLICT (pull_request_id, commit_sha, check_name) DO NOTHING;

-- Example integrity failures, deliberately rolled back.
-- The DO blocks make the script executable while showing that the database
-- rejects invalid values. Unexpected acceptance raises a visible exception.
DO $$
BEGIN
    BEGIN
        PERFORM validate_policy_options(
            '{"required_approvals": true}'::jsonb
        );
        RAISE EXCEPTION 'Expected type validation to reject boolean approvals';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM =
                'Expected type validation to reject boolean approvals' THEN
                RAISE;
            END IF;
            RAISE NOTICE 'Invalid approval type rejected: %', SQLERRM;
    END;

    BEGIN
        PERFORM validate_policy_options(
            '{"require_linera_history": true}'::jsonb
        );
        RAISE EXCEPTION 'Expected validation to reject misspelled option';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM =
                'Expected validation to reject misspelled option' THEN
                RAISE;
            END IF;
            RAISE NOTICE 'Unknown policy option rejected: %', SQLERRM;
    END;
END;
$$;

-- Current revision now requires fresh approvals and successful new checks.
SELECT
    pull_request_id,
    title,
    state,
    current_approvals,
    required_approvals,
    successful_required_checks,
    total_required_checks,
    unresolved_comments,
    merge_eligible
FROM pull_request_merge_eligibility
ORDER BY pull_request_id;

-- The sample transaction establishes the schema and initial demonstration data.
-- Commit all setup and workflow records so the script is immediately inspectable.
COMMIT;
