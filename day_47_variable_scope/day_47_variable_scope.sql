-- PostgreSQL 15+ repository governance and variable-scope learning model.
-- Scope here means lexical scope in application programs; PostgreSQL PL/pgSQL
-- also has block-local variables and nested blocks with shadowing.

BEGIN;

DROP SCHEMA IF EXISTS scope_governance CASCADE;
CREATE SCHEMA scope_governance;
SET search_path TO scope_governance, public;

CREATE TYPE pull_request_state AS ENUM
    ('draft', 'open', 'closed', 'merged');

CREATE TYPE review_state AS ENUM
    ('pending', 'approved', 'changes_requested', 'dismissed');

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL
);

CREATE TABLE branches (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id),
    branch_name TEXT NOT NULL,
    head_commit TEXT NOT NULL,
    protected BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (repository_id, branch_name)
);

CREATE TABLE pull_requests (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id),
    author TEXT NOT NULL,
    source_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    title TEXT NOT NULL,
    state pull_request_state NOT NULL DEFAULT 'open',
    head_commit TEXT NOT NULL,
    base_commit TEXT NOT NULL,
    draft BOOLEAN NOT NULL DEFAULT FALSE,
    merged_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (source_branch_id <> target_branch_id),
    CHECK ((state = 'merged') = (merged_at IS NOT NULL)),
    CHECK (NOT draft OR state = 'draft')
);

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    commit_id TEXT NOT NULL,
    position INTEGER NOT NULL CHECK (position > 0),
    commit_message TEXT NOT NULL,
    PRIMARY KEY (pull_request_id, commit_id),
    UNIQUE (pull_request_id, position)
);

CREATE TABLE reviewers (
    reviewer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    can_approve BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES reviewers(reviewer_id),
    reviewed_commit TEXT NOT NULL,
    state review_state NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Latest review state per reviewer is derived from timestamp ordering.
CREATE INDEX reviews_latest_idx
    ON reviews (pull_request_id, reviewer_id, submitted_at DESC);

CREATE TABLE review_comments (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES reviews(review_id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL CHECK (line_number > 0),
    body TEXT NOT NULL CHECK (length(trim(body)) > 0),
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE status_checks (
    check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    commit_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'success', 'failure')),
    completed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, check_name, commit_id)
);

CREATE TABLE branch_protection (
    protection_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE REFERENCES branches(branch_id),
    required_approvals INTEGER NOT NULL DEFAULT 1 CHECK (required_approvals >= 0),
    restrict_direct_pushes BOOLEAN NOT NULL DEFAULT TRUE,
    block_force_pushes BOOLEAN NOT NULL DEFAULT TRUE,
    block_deletion BOOLEAN NOT NULL DEFAULT TRUE,
    require_resolved_conversations BOOLEAN NOT NULL DEFAULT TRUE,
    require_linear_history BOOLEAN NOT NULL DEFAULT TRUE,
    dismiss_stale_approvals BOOLEAN NOT NULL DEFAULT TRUE,
    allow_admin_bypass BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE required_status_checks (
    protection_id BIGINT NOT NULL
        REFERENCES branch_protection(protection_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    PRIMARY KEY (protection_id, check_name)
);

CREATE TABLE pull_request_metadata (
    pull_request_id BIGINT PRIMARY KEY
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    approvals_stale BOOLEAN NOT NULL DEFAULT FALSE,
    conversations_resolved BOOLEAN NOT NULL DEFAULT TRUE,
    linear_history_verified BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX open_pull_requests_idx
    ON pull_requests (target_branch_id, created_at DESC)
    WHERE state IN ('open', 'draft');

CREATE INDEX unresolved_comments_idx
    ON review_comments (review_id)
    WHERE resolved = FALSE;

-- PL/pgSQL demonstrates block-local variables and lexical shadowing.
CREATE OR REPLACE FUNCTION scope_binding_demo()
RETURNS TABLE (binding_scope TEXT, binding_value TEXT)
LANGUAGE plpgsql
AS $$
DECLARE
    policy_name TEXT := 'repository-policy';
BEGIN
    binding_scope := 'outer';
    binding_value := policy_name;
    RETURN NEXT;

    DECLARE
        policy_name TEXT := 'pull-request-policy';
    BEGIN
        binding_scope := 'inner';
        binding_value := policy_name;
        RETURN NEXT;
    END;

    binding_scope := 'outer-after-inner';
    binding_value := policy_name;
    RETURN NEXT;
END;
$$;

-- The database uses constraints for integrity and a view for a consistent
-- read of merge blockers. A production merge operation should lock the PR,
-- branch head, policy, and relevant review/check rows in one transaction.
CREATE OR REPLACE VIEW merge_eligibility AS
WITH latest_reviews AS (
    SELECT DISTINCT ON (r.pull_request_id, r.reviewer_id)
        r.pull_request_id,
        r.reviewer_id,
        r.state,
        r.reviewed_commit,
        rv.username,
        rv.active,
        rv.can_approve,
        pr.author,
        pr.head_commit,
        pr.target_branch_id,
        pr.state AS pr_state
    FROM reviews r
    JOIN reviewers rv ON rv.reviewer_id = r.reviewer_id
    JOIN pull_requests pr ON pr.pull_request_id = r.pull_request_id
    ORDER BY r.pull_request_id, r.reviewer_id, r.submitted_at DESC, r.review_id DESC
),
approval_counts AS (
    SELECT
        lr.pull_request_id,
        COUNT(*) FILTER (
            WHERE lr.state = 'approved'
              AND lr.active
              AND lr.can_approve
              AND lr.username <> lr.author
              AND lr.reviewed_commit = lr.head_commit
        ) AS current_approval_count
    FROM latest_reviews lr
    GROUP BY lr.pull_request_id
),
check_evaluation AS (
    SELECT
        pr.pull_request_id,
        COUNT(*) FILTER (
            WHERE required.check_name IS NOT NULL
              AND (
                  sc.status IS DISTINCT FROM 'success'
                  OR sc.commit_id IS DISTINCT FROM pr.head_commit
              )
        ) AS blocking_check_count
    FROM pull_requests pr
    LEFT JOIN branch_protection bp
        ON bp.branch_id = pr.target_branch_id
    LEFT JOIN required_status_checks required
        ON required.protection_id = bp.protection_id
    LEFT JOIN status_checks sc
        ON sc.pull_request_id = pr.pull_request_id
       AND sc.check_name = required.check_name
       AND sc.commit_id = pr.head_commit
    GROUP BY pr.pull_request_id
),
conversation_evaluation AS (
    SELECT
        pr.pull_request_id,
        COUNT(rc.comment_id) FILTER (WHERE NOT rc.resolved) AS unresolved_count
    FROM pull_requests pr
    LEFT JOIN reviews r ON r.pull_request_id = pr.pull_request_id
    LEFT JOIN review_comments rc ON rc.review_id = r.review_id
    GROUP BY pr.pull_request_id
)
SELECT
    pr.pull_request_id,
    pr.title,
    pr.state,
    pr.head_commit,
    pr.target_branch_id,
    COALESCE(ac.current_approval_count, 0) AS current_approval_count,
    bp.required_approvals,
    COALESCE(ce.blocking_check_count, 0) AS blocking_check_count,
    COALESCE(conversations.unresolved_count, 0) AS unresolved_count,
    COALESCE(meta.approvals_stale, FALSE) AS approvals_stale,
    COALESCE(meta.linear_history_verified, FALSE) AS linear_history_verified,
    (
        pr.state = 'open'
        AND NOT pr.draft
        AND bp.protection_id IS NOT NULL
        AND COALESCE(ac.current_approval_count, 0) >= bp.required_approvals
        AND COALESCE(ce.blocking_check_count, 0) = 0
        AND (
            NOT bp.require_resolved_conversations
            OR (
                COALESCE(conversations.unresolved_count, 0) = 0
                AND COALESCE(meta.conversations_resolved, TRUE)
            )
        )
        AND (
            NOT bp.dismiss_stale_approvals
            OR NOT COALESCE(meta.approvals_stale, FALSE)
        )
        AND (
            NOT bp.require_linear_history
            OR COALESCE(meta.linear_history_verified, FALSE)
        )
    ) AS eligible
FROM pull_requests pr
LEFT JOIN branch_protection bp ON bp.branch_id = pr.target_branch_id
LEFT JOIN approval_counts ac ON ac.pull_request_id = pr.pull_request_id
LEFT JOIN check_evaluation ce ON ce.pull_request_id = pr.pull_request_id
LEFT JOIN conversation_evaluation conversations
    ON conversations.pull_request_id = pr.pull_request_id
LEFT JOIN pull_request_metadata meta
    ON meta.pull_request_id = pr.pull_request_id;

INSERT INTO repositories (repository_name, default_branch)
VALUES ('payments-service', 'main');

INSERT INTO branches (repository_id, branch_name, head_commit, protected)
SELECT repository_id, 'main', 'base-900', TRUE
FROM repositories WHERE repository_name = 'payments-service';

INSERT INTO branches (repository_id, branch_name, head_commit)
SELECT repository_id, 'feature/currency-validation', 'commit-102'
FROM repositories WHERE repository_name = 'payments-service';

INSERT INTO reviewers (username, active, can_approve)
VALUES
    ('reviewer-ada', TRUE, TRUE),
    ('reviewer-lin', TRUE, TRUE),
    ('developer-kim', TRUE, TRUE),
    ('reviewer-disabled', FALSE, TRUE);

INSERT INTO branch_protection (
    branch_id, required_approvals, restrict_direct_pushes,
    block_force_pushes, block_deletion, require_resolved_conversations,
    require_linear_history, dismiss_stale_approvals, allow_admin_bypass
)
SELECT branch_id, 2, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, FALSE
FROM branches
WHERE branch_name = 'main';

INSERT INTO required_status_checks (protection_id, check_name)
SELECT protection_id, check_name
FROM branch_protection
CROSS JOIN (VALUES ('unit-tests'), ('security-scan')) AS required(check_name);

INSERT INTO pull_requests (
    repository_id, author, source_branch_id, target_branch_id,
    title, state, head_commit, base_commit, draft
)
SELECT
    repo.repository_id,
    'developer-kim',
    source.branch_id,
    target.branch_id,
    'Validate currency before charging',
    'open',
    'commit-102',
    'base-900',
    FALSE
FROM repositories repo
JOIN branches source ON source.repository_id = repo.repository_id
    AND source.branch_name = 'feature/currency-validation'
JOIN branches target ON target.repository_id = repo.repository_id
    AND target.branch_name = 'main'
WHERE repo.repository_name = 'payments-service';

INSERT INTO pull_request_commits (pull_request_id, commit_id, position, commit_message)
SELECT pull_request_id, 'commit-101', 1, 'Add currency validation'
FROM pull_requests
UNION ALL
SELECT pull_request_id, 'commit-102', 2, 'Reject unsupported currency'
FROM pull_requests;

INSERT INTO pull_request_metadata (
    pull_request_id, approvals_stale, conversations_resolved, linear_history_verified
)
SELECT pull_request_id, FALSE, TRUE, TRUE
FROM pull_requests;

INSERT INTO reviews (pull_request_id, reviewer_id, reviewed_commit, state)
SELECT pr.pull_request_id, rv.reviewer_id, 'commit-102', 'approved'
FROM pull_requests pr
JOIN reviewers rv ON rv.username IN ('reviewer-ada', 'reviewer-lin');

INSERT INTO reviews (pull_request_id, reviewer_id, reviewed_commit, state)
SELECT pr.pull_request_id, rv.reviewer_id, 'commit-102', 'approved'
FROM pull_requests pr
JOIN reviewers rv ON rv.username = 'developer-kim';

INSERT INTO review_comments (review_id, file_path, line_number, body, resolved)
SELECT
    review_id,
    'src/payment.py',
    42,
    'Reject unsupported currency before modifying the ledger.',
    TRUE
FROM reviews
WHERE reviewer_id = (SELECT reviewer_id FROM reviewers WHERE username = 'reviewer-ada');

INSERT INTO status_checks (pull_request_id, check_name, commit_id, status, completed_at)
SELECT pr.pull_request_id, checks.check_name, 'commit-102', 'success', CURRENT_TIMESTAMP
FROM pull_requests pr
CROSS JOIN (VALUES ('unit-tests'), ('security-scan')) AS checks(check_name);

-- Demonstrate nested lexical bindings.
SELECT * FROM scope_binding_demo();

-- Distinct eligible approvals exclude the author and stale reviewed commits.
SELECT pull_request_id, current_approval_count, required_approvals, eligible
FROM merge_eligibility
ORDER BY pull_request_id;

-- Inline review discussions are evaluated independently of approval counts.
SELECT
    pr.pull_request_id,
    rc.file_path,
    rc.line_number,
    rc.resolved,
    rc.body
FROM pull_requests pr
JOIN reviews r ON r.pull_request_id = pr.pull_request_id
JOIN review_comments rc ON rc.review_id = r.review_id
WHERE NOT rc.resolved;

-- Simulate a new commit changing the head. Old approvals and check results
-- no longer match the current changeset and cannot authorize a merge.
UPDATE pull_requests
SET head_commit = 'commit-103'
WHERE title = 'Validate currency before charging';

UPDATE pull_request_metadata
SET approvals_stale = TRUE
WHERE pull_request_id = (
    SELECT pull_request_id
    FROM pull_requests
    WHERE title = 'Validate currency before charging'
);

SELECT pull_request_id, current_approval_count, blocking_check_count,
       approvals_stale, eligible
FROM merge_eligibility;

-- A failed status check is valid stored evidence but blocks the merge.
INSERT INTO status_checks (pull_request_id, check_name, commit_id, status, completed_at)
SELECT pull_request_id, 'unit-tests', 'commit-103', 'failure', CURRENT_TIMESTAMP
FROM pull_requests
WHERE title = 'Validate currency before charging';

SELECT pull_request_id, blocking_check_count, eligible
FROM merge_eligibility;

-- Constraints prevent a comment from referring to a nonexistent review and
-- prevent negative line numbers. Such failures abort the statement.
DO $$
BEGIN
    BEGIN
        INSERT INTO review_comments (review_id, file_path, line_number, body)
        VALUES (-1, 'src/payment.py', 0, 'Invalid reference and line');
    EXCEPTION
        WHEN foreign_key_violation OR check_violation THEN
            RAISE NOTICE 'Invalid review comment rejected by database constraints';
    END;
END;
$$;

COMMIT;
