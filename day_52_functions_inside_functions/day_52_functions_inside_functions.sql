DROP SCHEMA IF EXISTS repository_governance CASCADE;
CREATE SCHEMA repository_governance;
SET search_path = repository_governance;

-- The relational model keeps Pull Requests, reviews, approvals,
-- and branch-protection policies distinct because they represent
-- different governance mechanisms.

CREATE TYPE pull_request_state AS ENUM (
    'draft',
    'open',
    'closed',
    'merged'
);

CREATE TYPE review_state AS ENUM (
    'commented',
    'changes_requested',
    'approved',
    'dismissed'
);

CREATE TABLE repositories (
    repository_id BIGSERIAL PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(repository_name)) >= 2),
    CHECK (length(trim(default_branch)) >= 1)
);

CREATE TABLE branches (
    branch_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    is_protected BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (repository_id, branch_name)
);

CREATE TABLE developers (
    developer_id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (username ~ '^[A-Za-z0-9_.-]{2,50}$')
);

CREATE TABLE pull_requests (
    pull_request_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    author_id BIGINT NOT NULL
        REFERENCES developers(developer_id),
    source_branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id),
    title TEXT NOT NULL,
    state pull_request_state NOT NULL DEFAULT 'draft',
    is_draft BOOLEAN NOT NULL DEFAULT TRUE,
    unresolved_conversations INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMPTZ,
    merged_at TIMESTAMPTZ,
    CHECK (length(trim(title)) >= 3),
    CHECK (unresolved_conversations >= 0),
    CHECK (
        (state = 'merged' AND merged_at IS NOT NULL)
        OR state <> 'merged'
    )
);

CREATE TABLE commits (
    commit_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    sha TEXT NOT NULL,
    commit_message TEXT NOT NULL,
    sequence_no INTEGER NOT NULL,
    UNIQUE (pull_request_id, sha),
    UNIQUE (pull_request_id, sequence_no),
    CHECK (length(sha) BETWEEN 7 AND 128),
    CHECK (length(trim(commit_message)) > 0),
    CHECK (sequence_no > 0)
);

CREATE TABLE reviewer_assignments (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL
        REFERENCES developers(developer_id),
    requested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pull_request_id, reviewer_id)
);

CREATE TABLE reviews (
    review_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL
        REFERENCES developers(developer_id),
    commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id)
        ON DELETE CASCADE,
    state review_state NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dismissed_at TIMESTAMPTZ,
    CHECK (
        (state = 'dismissed' AND dismissed_at IS NOT NULL)
        OR state <> 'dismissed'
    )
);

CREATE TABLE review_comments (
    comment_id BIGSERIAL PRIMARY KEY,
    review_id BIGINT NOT NULL
        REFERENCES reviews(review_id)
        ON DELETE CASCADE,
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(body)) > 0)
);

CREATE TABLE status_checks (
    status_check_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    completed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, check_name)
);

CREATE TABLE branch_protection_policies (
    policy_id BIGSERIAL PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE
        REFERENCES branches(branch_id)
        ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 0,
    require_conversation_resolution BOOLEAN NOT NULL DEFAULT FALSE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    allow_direct_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_branch_deletion BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (required_approvals >= 0)
);

CREATE TABLE required_status_checks (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    PRIMARY KEY (policy_id, check_name),
    CHECK (length(trim(check_name)) > 0)
);

CREATE INDEX idx_pr_target_state
    ON pull_requests(target_branch_id, state);

CREATE INDEX idx_reviews_pr_commit_state
    ON reviews(pull_request_id, commit_id, state);

CREATE INDEX idx_status_checks_pr_name
    ON status_checks(pull_request_id, check_name);

CREATE INDEX idx_review_comments_unresolved
    ON review_comments(review_id)
    WHERE resolved = FALSE;

INSERT INTO repositories(repository_name, default_branch)
VALUES ('secure-api', 'main');

INSERT INTO developers(username)
VALUES
    ('alice'),
    ('bob'),
    ('carol'),
    ('dave');

INSERT INTO branches(repository_id, branch_name, is_protected)
SELECT repository_id, branch_name, branch_name = 'main'
FROM repositories
CROSS JOIN (
    VALUES
        ('main'),
        ('feature/authentication'),
        ('feature/deployment')
) AS b(branch_name);

INSERT INTO branch_protection_policies(
    branch_id,
    required_approvals,
    require_conversation_resolution,
    require_linear_history,
    allow_direct_push,
    allow_force_push,
    allow_branch_deletion
)
SELECT
    branch_id,
    2,
    TRUE,
    TRUE,
    FALSE,
    FALSE,
    FALSE
FROM branches
WHERE branch_name = 'main';

INSERT INTO required_status_checks(policy_id, check_name)
SELECT policy_id, check_name
FROM branch_protection_policies
CROSS JOIN (
    VALUES ('tests'), ('security-scan')
) AS checks(check_name);

INSERT INTO pull_requests(
    repository_id,
    author_id,
    source_branch_id,
    target_branch_id,
    title,
    state,
    is_draft,
    unresolved_conversations
)
SELECT
    r.repository_id,
    author.developer_id,
    source.branch_id,
    target.branch_id,
    'Harden authentication policy',
    'open',
    FALSE,
    0
FROM repositories r
JOIN developers author
    ON author.username = 'carol'
JOIN branches source
    ON source.repository_id = r.repository_id
    AND source.branch_name = 'feature/authentication'
JOIN branches target
    ON target.repository_id = r.repository_id
    AND target.branch_name = 'main';

INSERT INTO commits(
    pull_request_id,
    sha,
    commit_message,
    sequence_no
)
SELECT
    pull_request_id,
    'a100001',
    'authentication policy',
    1
FROM pull_requests
WHERE title = 'Harden authentication policy';

INSERT INTO commits(
    pull_request_id,
    sha,
    commit_message,
    sequence_no
)
SELECT
    pull_request_id,
    'b200002',
    'security validation',
    2
FROM pull_requests
WHERE title = 'Harden authentication policy';

INSERT INTO reviewer_assignments(pull_request_id, reviewer_id)
SELECT pr.pull_request_id, d.developer_id
FROM pull_requests pr
JOIN developers d
    ON d.username IN ('alice', 'bob')
WHERE pr.title = 'Harden authentication policy';

INSERT INTO reviews(
    pull_request_id,
    reviewer_id,
    commit_id,
    state
)
SELECT
    pr.pull_request_id,
    d.developer_id,
    c.commit_id,
    'approved'
FROM pull_requests pr
JOIN developers d
    ON d.username IN ('alice', 'bob')
JOIN commits c
    ON c.pull_request_id = pr.pull_request_id
    AND c.sha = 'b200002'
WHERE pr.title = 'Harden authentication policy';

INSERT INTO status_checks(
    pull_request_id,
    check_name,
    passed,
    completed_at
)
SELECT
    pull_request_id,
    check_name,
    TRUE,
    CURRENT_TIMESTAMP
FROM pull_requests
CROSS JOIN (
    VALUES ('tests'), ('security-scan')
) AS checks(check_name)
WHERE title = 'Harden authentication policy';

INSERT INTO pull_requests(
    repository_id,
    author_id,
    source_branch_id,
    target_branch_id,
    title,
    state,
    is_draft,
    unresolved_conversations
)
SELECT
    r.repository_id,
    author.developer_id,
    source.branch_id,
    target.branch_id,
    'Deployment policy update',
    'open',
    FALSE,
    1
FROM repositories r
JOIN developers author
    ON author.username = 'dave'
JOIN branches source
    ON source.repository_id = r.repository_id
    AND source.branch_name = 'feature/deployment'
JOIN branches target
    ON target.repository_id = r.repository_id
    AND target.branch_name = 'main';

INSERT INTO commits(
    pull_request_id,
    sha,
    commit_message,
    sequence_no
)
SELECT
    pull_request_id,
    'c300003',
    'initial deployment policy',
    1
FROM pull_requests
WHERE title = 'Deployment policy update';

INSERT INTO reviewer_assignments(pull_request_id, reviewer_id)
SELECT pr.pull_request_id, d.developer_id
FROM pull_requests pr
JOIN developers d
    ON d.username IN ('alice', 'bob')
WHERE pr.title = 'Deployment policy update';

INSERT INTO status_checks(
    pull_request_id,
    check_name,
    passed,
    completed_at
)
SELECT
    pull_request_id,
    check_name,
    TRUE,
    CURRENT_TIMESTAMP
FROM pull_requests
CROSS JOIN (
    VALUES ('tests'), ('security-scan')
) AS checks(check_name)
WHERE title = 'Deployment policy update';

INSERT INTO review_comments(review_id, body, resolved)
SELECT
    review_id,
    'Please document the deployment rollback rule.',
    FALSE
FROM reviews
WHERE FALSE;

-- The following function evaluates the governance rules without granting
-- the application permission to bypass the database model.
CREATE OR REPLACE FUNCTION evaluate_merge_eligibility(
    p_pull_request_id BIGINT
)
RETURNS TABLE (
    eligible BOOLEAN,
    reason TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    pr RECORD;
    policy RECORD;
    latest_commit BIGINT;
    approval_count INTEGER;
    required_check_count INTEGER;
    passing_check_count INTEGER;
BEGIN
    SELECT *
    INTO pr
    FROM pull_requests
    WHERE pull_request_id = p_pull_request_id;

    IF NOT FOUND THEN
        RETURN QUERY
        SELECT FALSE, 'Pull Request does not exist';
        RETURN;
    END IF;

    SELECT bpp.*
    INTO policy
    FROM branch_protection_policies bpp
    WHERE bpp.branch_id = pr.target_branch_id;

    IF NOT FOUND THEN
        RETURN QUERY
        SELECT TRUE, 'No branch-protection policy is configured';
        RETURN;
    END IF;

    IF pr.state <> 'open' THEN
        RETURN QUERY
        SELECT FALSE, 'Pull Request is not open';
        RETURN;
    END IF;

    IF pr.is_draft THEN
        RETURN QUERY
        SELECT FALSE, 'Draft Pull Request cannot be merged';
        RETURN;
    END IF;

    IF pr.source_branch_id = pr.target_branch_id
       AND NOT policy.allow_direct_push THEN
        RETURN QUERY
        SELECT FALSE, 'Direct push to protected branch is prohibited';
        RETURN;
    END IF;

    IF policy.require_conversation_resolution
       AND pr.unresolved_conversations > 0 THEN
        RETURN QUERY
        SELECT FALSE, 'Unresolved review conversations remain';
        RETURN;
    END IF;

    SELECT c.commit_id
    INTO latest_commit
    FROM commits c
    WHERE c.pull_request_id = p_pull_request_id
    ORDER BY c.sequence_no DESC
    LIMIT 1;

    IF latest_commit IS NULL THEN
        RETURN QUERY
        SELECT FALSE, 'Pull Request has no commits';
        RETURN;
    END IF;

    SELECT COUNT(DISTINCT r.reviewer_id)
    INTO approval_count
    FROM reviews r
    JOIN reviewer_assignments ra
        ON ra.pull_request_id = r.pull_request_id
        AND ra.reviewer_id = r.reviewer_id
    WHERE r.pull_request_id = p_pull_request_id
      AND r.commit_id = latest_commit
      AND r.state = 'approved'
      AND r.dismissed_at IS NULL;

    IF approval_count < policy.required_approvals THEN
        RETURN QUERY
        SELECT FALSE,
               format(
                   'Only %s current approval(s); %s required',
                   approval_count,
                   policy.required_approvals
               );
        RETURN;
    END IF;

    SELECT COUNT(*)
    INTO required_check_count
    FROM required_status_checks
    WHERE policy_id = policy.policy_id;

    SELECT COUNT(*)
    INTO passing_check_count
    FROM required_status_checks required
    JOIN status_checks actual
        ON actual.pull_request_id = p_pull_request_id
        AND actual.check_name = required.check_name
        AND actual.passed = TRUE
    WHERE required.policy_id = policy.policy_id;

    IF passing_check_count < required_check_count THEN
        RETURN QUERY
        SELECT FALSE, 'Required status checks are not all passing';
        RETURN;
    END IF;

    RETURN QUERY
    SELECT TRUE, 'All merge conditions are satisfied';
END;
$$;

CREATE OR REPLACE VIEW pull_request_governance_report AS
WITH latest_commit AS (
    SELECT DISTINCT ON (pull_request_id)
        pull_request_id,
        commit_id,
        sha,
        sequence_no
    FROM commits
    ORDER BY pull_request_id, sequence_no DESC
),
approval_counts AS (
    SELECT
        r.pull_request_id,
        COUNT(DISTINCT r.reviewer_id) AS approvals
    FROM reviews r
    JOIN latest_commit lc
        ON lc.pull_request_id = r.pull_request_id
        AND lc.commit_id = r.commit_id
    JOIN reviewer_assignments ra
        ON ra.pull_request_id = r.pull_request_id
        AND ra.reviewer_id = r.reviewer_id
    WHERE r.state = 'approved'
      AND r.dismissed_at IS NULL
    GROUP BY r.pull_request_id
)
SELECT
    pr.pull_request_id,
    repo.repository_name,
    pr.title,
    pr.state,
    source.branch_name AS source_branch,
    target.branch_name AS target_branch,
    COALESCE(ac.approvals, 0) AS current_approvals,
    COALESCE(policy.required_approvals, 0) AS required_approvals,
    pr.unresolved_conversations,
    COALESCE(lc.sha, 'NO-COMMIT') AS latest_commit
FROM pull_requests pr
JOIN repositories repo
    ON repo.repository_id = pr.repository_id
JOIN branches source
    ON source.branch_id = pr.source_branch_id
JOIN branches target
    ON target.branch_id = pr.target_branch_id
LEFT JOIN latest_commit lc
    ON lc.pull_request_id = pr.pull_request_id
LEFT JOIN approval_counts ac
    ON ac.pull_request_id = pr.pull_request_id
LEFT JOIN branch_protection_policies policy
    ON policy.branch_id = pr.target_branch_id;

-- A successful merge is performed transactionally.
BEGIN;

SELECT *
FROM evaluate_merge_eligibility(
    (
        SELECT pull_request_id
        FROM pull_requests
        WHERE title = 'Harden authentication policy'
    )
);

UPDATE pull_requests
SET
    state = 'merged',
    is_draft = FALSE,
    merged_at = CURRENT_TIMESTAMP
WHERE title = 'Harden authentication policy'
  AND EXISTS (
      SELECT 1
      FROM evaluate_merge_eligibility(pull_request_id)
      WHERE eligible = TRUE
  );

COMMIT;

-- Reporting query: current approval state is based on the latest commit,
-- so approvals attached to older commits do not satisfy the current policy.
SELECT *
FROM pull_request_governance_report
ORDER BY pull_request_id;

-- Demonstrates an invalid governance operation without changing data.
BEGIN;

SELECT *
FROM evaluate_merge_eligibility(
    (
        SELECT pull_request_id
        FROM pull_requests
        WHERE title = 'Deployment policy update'
    )
);

ROLLBACK;

-- Aggregated reviewer activity remains distinct from approval eligibility.
SELECT
    d.username,
    COUNT(r.review_id) AS review_count,
    COUNT(*) FILTER (
        WHERE r.state = 'approved'
    ) AS approvals,
    COUNT(*) FILTER (
        WHERE r.state = 'changes_requested'
    ) AS requested_changes
FROM developers d
LEFT JOIN reviews r
    ON r.reviewer_id = d.developer_id
GROUP BY d.developer_id, d.username
ORDER BY review_count DESC, d.username;
