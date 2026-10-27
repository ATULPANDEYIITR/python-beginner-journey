DROP SCHEMA IF EXISTS exception_workflow CASCADE;
CREATE SCHEMA exception_workflow;

SET search_path = exception_workflow, public;

CREATE TYPE repository_state AS ENUM (
    'active',
    'archived'
);

CREATE TYPE pull_request_state AS ENUM (
    'draft',
    'open',
    'blocked',
    'mergeable',
    'merged',
    'closed'
);

CREATE TYPE review_decision AS ENUM (
    'pending',
    'approved',
    'changes_requested',
    'rejected'
);

CREATE TYPE check_state AS ENUM (
    'pending',
    'passed',
    'failed'
);

CREATE TABLE repositories (
    repository_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    owner TEXT NOT NULL,
    state repository_state NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (owner, name),
    CHECK (length(trim(name)) > 0),
    CHECK (length(trim(owner)) > 0)
);

CREATE TABLE branches (
    branch_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    name TEXT NOT NULL,
    protected BOOLEAN NOT NULL DEFAULT FALSE,
    allows_direct_push BOOLEAN NOT NULL DEFAULT TRUE,
    allows_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (repository_id, name),
    CHECK (length(trim(name)) > 0),
    CHECK (
        allows_force_push = FALSE
        OR protected = FALSE
    )
);

CREATE TABLE commits (
    commit_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    commit_hash TEXT NOT NULL,
    author TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (repository_id, commit_hash),
    CHECK (length(trim(commit_hash)) >= 7),
    CHECK (length(trim(author)) > 0),
    CHECK (length(trim(message)) > 0)
);

CREATE TABLE pull_requests (
    pull_request_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    source_branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id),
    head_commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id),
    state pull_request_state NOT NULL DEFAULT 'draft',
    title TEXT NOT NULL,
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (source_branch_id <> target_branch_id),
    CHECK (length(trim(title)) > 0),
    CHECK (length(trim(created_by)) > 0)
);

CREATE TABLE reviewers (
    reviewer_id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (length(trim(username)) > 0)
);

CREATE TABLE pull_request_reviewers (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL
        REFERENCES reviewers(reviewer_id)
        ON DELETE RESTRICT,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pull_request_id, reviewer_id)
);

CREATE TABLE reviews (
    review_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL
        REFERENCES reviewers(reviewer_id)
        ON DELETE RESTRICT,
    decision review_decision NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dismissed BOOLEAN NOT NULL DEFAULT FALSE,
    body TEXT,
    UNIQUE (pull_request_id, reviewer_id, submitted_at)
);

CREATE TABLE review_comments (
    comment_id BIGSERIAL PRIMARY KEY,
    review_id BIGINT NOT NULL
        REFERENCES reviews(review_id)
        ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(file_path)) > 0),
    CHECK (line_number > 0),
    CHECK (length(trim(body)) > 0)
);

CREATE TABLE status_checks (
    status_check_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    state check_state NOT NULL DEFAULT 'pending',
    completed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, check_name),
    CHECK (length(trim(check_name)) > 0),
    CHECK (
        state = 'passed'
        OR completed_at IS NULL
        OR state = 'failed'
    )
);

CREATE TABLE branch_protection_policies (
    policy_id BIGSERIAL PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE
        REFERENCES branches(branch_id)
        ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 1,
    require_status_checks BOOLEAN NOT NULL DEFAULT TRUE,
    require_resolved_conversations BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_direct_push BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_force_push BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_deletion BOOLEAN NOT NULL DEFAULT TRUE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (required_approvals >= 0)
);

CREATE TABLE approval_requirements (
    requirement_id BIGSERIAL PRIMARY KEY,
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT
        REFERENCES reviewers(reviewer_id)
        ON DELETE RESTRICT,
    required BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (policy_id, reviewer_id)
);

CREATE INDEX idx_pr_repository_state
    ON pull_requests(repository_id, state);

CREATE INDEX idx_reviews_pull_request_decision
    ON reviews(pull_request_id, decision)
    WHERE dismissed = FALSE;

CREATE INDEX idx_comments_unresolved
    ON review_comments(review_id)
    WHERE resolved = FALSE;

CREATE INDEX idx_checks_pull_request_state
    ON status_checks(pull_request_id, state);

INSERT INTO repositories (name, owner)
VALUES
    ('secure-platform', 'engineering'),
    ('data-pipeline', 'analytics');

INSERT INTO branches (
    repository_id,
    name,
    protected,
    allows_direct_push,
    allows_force_push
)
SELECT
    repository_id,
    'main',
    TRUE,
    FALSE,
    FALSE
FROM repositories
WHERE name = 'secure-platform'
  AND owner = 'engineering';

INSERT INTO branches (
    repository_id,
    name,
    protected,
    allows_direct_push,
    allows_force_push
)
SELECT
    repository_id,
    'feature/reliable-exceptions',
    FALSE,
    TRUE,
    TRUE
FROM repositories
WHERE name = 'secure-platform'
  AND owner = 'engineering';

INSERT INTO branches (
    repository_id,
    name,
    protected,
    allows_direct_push,
    allows_force_push
)
SELECT
    repository_id,
    'feature/broken-check',
    FALSE,
    TRUE,
    TRUE
FROM repositories
WHERE name = 'secure-platform'
  AND owner = 'engineering';

INSERT INTO commits (
    repository_id,
    commit_hash,
    author,
    message
)
SELECT
    repository_id,
    'abcdef1234567',
    'alice',
    'Add controlled exception handling'
FROM repositories
WHERE name = 'secure-platform'
  AND owner = 'engineering';

INSERT INTO commits (
    repository_id,
    commit_hash,
    author,
    message
)
SELECT
    repository_id,
    '1234567abcdef',
    'bob',
    'Introduce validation failure test'
FROM repositories
WHERE name = 'secure-platform'
  AND owner = 'engineering';

INSERT INTO pull_requests (
    repository_id,
    source_branch_id,
    target_branch_id,
    head_commit_id,
    state,
    title,
    created_by
)
SELECT
    r.repository_id,
    source.branch_id,
    target.branch_id,
    c.commit_id,
    'open',
    'Implement reliable exception handling',
    'alice'
FROM repositories r
JOIN branches source
    ON source.repository_id = r.repository_id
   AND source.name = 'feature/reliable-exceptions'
JOIN branches target
    ON target.repository_id = r.repository_id
   AND target.name = 'main'
JOIN commits c
    ON c.repository_id = r.repository_id
   AND c.commit_hash = 'abcdef1234567'
WHERE r.name = 'secure-platform'
  AND r.owner = 'engineering';

INSERT INTO pull_requests (
    repository_id,
    source_branch_id,
    target_branch_id,
    head_commit_id,
    state,
    title,
    created_by
)
SELECT
    r.repository_id,
    source.branch_id,
    target.branch_id,
    c.commit_id,
    'open',
    'Introduce an intentionally failing workflow',
    'bob'
FROM repositories r
JOIN branches source
    ON source.repository_id = r.repository_id
   AND source.name = 'feature/broken-check'
JOIN branches target
    ON target.repository_id = r.repository_id
   AND target.name = 'main'
JOIN commits c
    ON c.repository_id = r.repository_id
   AND c.commit_hash = '1234567abcdef'
WHERE r.name = 'secure-platform'
  AND r.owner = 'engineering';

INSERT INTO reviewers (username)
VALUES
    ('alice'),
    ('bob'),
    ('carol');

INSERT INTO branch_protection_policies (
    branch_id,
    required_approvals,
    require_status_checks,
    require_resolved_conversations,
    restrict_direct_push,
    restrict_force_push,
    restrict_deletion,
    require_linear_history
)
SELECT
    branch_id,
    2,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE
FROM branches
WHERE name = 'main';

INSERT INTO approval_requirements (
    policy_id,
    reviewer_id,
    required
)
SELECT
    p.policy_id,
    r.reviewer_id,
    TRUE
FROM branch_protection_policies p
CROSS JOIN reviewers r
WHERE r.username IN ('alice', 'bob')
  AND p.branch_id = (
      SELECT branch_id
      FROM branches
      WHERE name = 'main'
      LIMIT 1
  );

INSERT INTO pull_request_reviewers (
    pull_request_id,
    reviewer_id
)
SELECT
    pr.pull_request_id,
    r.reviewer_id
FROM pull_requests pr
CROSS JOIN reviewers r
WHERE pr.title = 'Implement reliable exception handling'
  AND r.username IN ('alice', 'bob');

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    decision,
    body
)
SELECT
    pr.pull_request_id,
    r.reviewer_id,
    'approved',
    'Validation and failure paths are correctly separated.'
FROM pull_requests pr
JOIN reviewers r
    ON r.username = 'alice'
WHERE pr.title = 'Implement reliable exception handling';

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    decision,
    body
)
SELECT
    pr.pull_request_id,
    r.reviewer_id,
    'approved',
    'Exception boundaries preserve domain context.'
FROM pull_requests pr
JOIN reviewers r
    ON r.username = 'bob'
WHERE pr.title = 'Implement reliable exception handling';

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    decision,
    body
)
SELECT
    pr.pull_request_id,
    r.reviewer_id,
    'changes_requested',
    'The failure path requires additional handling.'
FROM pull_requests pr
JOIN reviewers r
    ON r.username = 'carol'
WHERE pr.title = 'Introduce an intentionally failing workflow';

INSERT INTO review_comments (
    review_id,
    file_path,
    line_number,
    body,
    resolved
)
SELECT
    review_id,
    'workflow.py',
    87,
    'Handle malformed external input explicitly.',
    FALSE
FROM reviews
WHERE decision = 'changes_requested';

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    state,
    completed_at
)
SELECT
    pull_request_id,
    'unit-tests',
    'passed',
    CURRENT_TIMESTAMP
FROM pull_requests
WHERE title = 'Implement reliable exception handling';

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    state,
    completed_at
)
SELECT
    pull_request_id,
    'security-scan',
    'passed',
    CURRENT_TIMESTAMP
FROM pull_requests
WHERE title = 'Implement reliable exception handling';

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    state,
    completed_at
)
SELECT
    pull_request_id,
    'unit-tests',
    'passed',
    CURRENT_TIMESTAMP
FROM pull_requests
WHERE title = 'Introduce an intentionally failing workflow';

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    state,
    completed_at
)
SELECT
    pull_request_id,
    'security-scan',
    'failed',
    CURRENT_TIMESTAMP
FROM pull_requests
WHERE title = 'Introduce an intentionally failing workflow';

CREATE OR REPLACE FUNCTION validate_pull_request_branches()
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
    WHERE branch_id = NEW.source_branch_id;

    SELECT repository_id
    INTO target_repository
    FROM branches
    WHERE branch_id = NEW.target_branch_id;

    IF source_repository IS NULL OR target_repository IS NULL THEN
        RAISE EXCEPTION
            USING
                ERRCODE = '23503',
                MESSAGE = 'Pull Request references a missing branch.';
    END IF;

    IF source_repository <> NEW.repository_id
       OR target_repository <> NEW.repository_id THEN
        RAISE EXCEPTION
            USING
                ERRCODE = '23514',
                MESSAGE = 'Pull Request branches must belong to its repository.';
    END IF;

    IF NEW.source_branch_id = NEW.target_branch_id THEN
        RAISE EXCEPTION
            USING
                ERRCODE = '23514',
                MESSAGE = 'Source and target branches must differ.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_pull_request_branches
BEFORE INSERT OR UPDATE
ON pull_requests
FOR EACH ROW
EXECUTE FUNCTION validate_pull_request_branches();

CREATE OR REPLACE FUNCTION unresolved_conversation_count(
    requested_pull_request_id BIGINT
)
RETURNS INTEGER
LANGUAGE SQL
STABLE
AS $$
    SELECT COUNT(*)::INTEGER
    FROM review_comments rc
    JOIN reviews r
      ON r.review_id = rc.review_id
    WHERE r.pull_request_id = requested_pull_request_id
      AND rc.resolved = FALSE;
$$;

CREATE OR REPLACE FUNCTION active_approval_count(
    requested_pull_request_id BIGINT
)
RETURNS INTEGER
LANGUAGE SQL
STABLE
AS $$
    SELECT COUNT(*)::INTEGER
    FROM reviews
    WHERE pull_request_id = requested_pull_request_id
      AND decision = 'approved'
      AND dismissed = FALSE;
$$;

CREATE OR REPLACE FUNCTION has_active_change_request(
    requested_pull_request_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM reviews
        WHERE pull_request_id = requested_pull_request_id
          AND decision = 'changes_requested'
          AND dismissed = FALSE
    );
$$;

CREATE OR REPLACE FUNCTION all_required_checks_passed(
    requested_pull_request_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
AS $$
    SELECT
        COUNT(*) > 0
        AND COUNT(*) FILTER (
            WHERE state <> 'passed'
        ) = 0
    FROM status_checks
    WHERE pull_request_id = requested_pull_request_id;
$$;

CREATE OR REPLACE FUNCTION pull_request_merge_eligibility(
    requested_pull_request_id BIGINT
)
RETURNS TABLE (
    eligible BOOLEAN,
    reason TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    target_branch BIGINT;
    required_approvals INTEGER;
    require_checks BOOLEAN;
    require_conversations BOOLEAN;
BEGIN
    SELECT target_branch_id
    INTO target_branch
    FROM pull_requests
    WHERE pull_request_id = requested_pull_request_id;

    IF target_branch IS NULL THEN
        RETURN QUERY
        SELECT FALSE, 'Pull Request does not exist.';
        RETURN;
    END IF;

    SELECT
        bpp.required_approvals,
        bpp.require_status_checks,
        bpp.require_resolved_conversations
    INTO
        required_approvals,
        require_checks,
        require_conversations
    FROM branch_protection_policies bpp
    WHERE bpp.branch_id = target_branch;

    IF NOT FOUND THEN
        RETURN QUERY
        SELECT TRUE, 'Target branch has no protection policy.';
        RETURN;
    END IF;

    IF (SELECT state
        FROM pull_requests
        WHERE pull_request_id = requested_pull_request_id)
        NOT IN ('open', 'blocked', 'mergeable') THEN
        RETURN QUERY
        SELECT FALSE, 'Pull Request is not in a mergeable workflow state.';
        RETURN;
    END IF;

    IF has_active_change_request(requested_pull_request_id) THEN
        RETURN QUERY
        SELECT FALSE, 'An active changes-requested review exists.';
        RETURN;
    END IF;

    IF active_approval_count(requested_pull_request_id)
       < required_approvals THEN
        RETURN QUERY
        SELECT FALSE, 'Required approvals are missing.';
        RETURN;
    END IF;

    IF require_conversations
       AND unresolved_conversation_count(requested_pull_request_id) > 0 THEN
        RETURN QUERY
        SELECT FALSE, 'Unresolved review conversations remain.';
        RETURN;
    END IF;

    IF require_checks
       AND NOT all_required_checks_passed(requested_pull_request_id) THEN
        RETURN QUERY
        SELECT FALSE, 'Required status checks have not all passed.';
        RETURN;
    END IF;

    RETURN QUERY
    SELECT TRUE, 'Pull Request satisfies the configured merge policy.';
END;
$$;

CREATE OR REPLACE FUNCTION merge_pull_request(
    requested_pull_request_id BIGINT
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    eligibility RECORD;
    current_state pull_request_state;
BEGIN
    SELECT state
    INTO current_state
    FROM pull_requests
    WHERE pull_request_id = requested_pull_request_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            USING
                ERRCODE = 'P0002',
                MESSAGE = 'Pull Request does not exist.';
    END IF;

    SELECT *
    INTO eligibility
    FROM pull_request_merge_eligibility(
        requested_pull_request_id
    );

    IF NOT eligibility.eligible THEN
        RAISE EXCEPTION
            USING
                ERRCODE = 'P0001',
                MESSAGE = eligibility.reason;
    END IF;

    UPDATE pull_requests
    SET
        state = 'merged',
        updated_at = CURRENT_TIMESTAMP
    WHERE pull_request_id = requested_pull_request_id;

    RETURN 'Pull Request merged successfully.';
END;
$$;

-- Retrieval: Pull Requests and their branch state.
SELECT
    pr.pull_request_id,
    pr.title,
    pr.state,
    source.name AS source_branch,
    target.name AS target_branch
FROM pull_requests pr
JOIN branches source
  ON source.branch_id = pr.source_branch_id
JOIN branches target
  ON target.branch_id = pr.target_branch_id
ORDER BY pr.pull_request_id;

-- Validation: show review counts, unresolved comments, and check failures.
SELECT
    pr.pull_request_id,
    pr.title,
    active_approval_count(pr.pull_request_id) AS approvals,
    unresolved_conversation_count(pr.pull_request_id) AS unresolved_comments,
    COUNT(sc.status_check_id) FILTER (
        WHERE sc.state = 'failed'
    ) AS failed_checks
FROM pull_requests pr
LEFT JOIN status_checks sc
  ON sc.pull_request_id = pr.pull_request_id
GROUP BY
    pr.pull_request_id,
    pr.title
ORDER BY pr.pull_request_id;

-- Evaluation: determine merge eligibility without changing data.
SELECT
    pr.pull_request_id,
    pr.title,
    eligibility.eligible,
    eligibility.reason
FROM pull_requests pr
CROSS JOIN LATERAL pull_request_merge_eligibility(
    pr.pull_request_id
) AS eligibility
ORDER BY pr.pull_request_id;

-- Aggregation: repository-level workflow state counts.
SELECT
    r.owner,
    r.name,
    pr.state,
    COUNT(*) AS pull_request_count
FROM repositories r
LEFT JOIN pull_requests pr
  ON pr.repository_id = r.repository_id
GROUP BY
    r.owner,
    r.name,
    pr.state
ORDER BY
    r.owner,
    r.name,
    pr.state;

-- Reporting: active reviewers and their review decisions.
SELECT
    rv.username,
    COUNT(rev.review_id) AS review_count,
    COUNT(*) FILTER (
        WHERE rev.decision = 'approved'
          AND NOT rev.dismissed
    ) AS active_approvals,
    COUNT(*) FILTER (
        WHERE rev.decision = 'changes_requested'
          AND NOT rev.dismissed
    ) AS active_change_requests
FROM reviewers rv
LEFT JOIN reviews rev
  ON rev.reviewer_id = rv.reviewer_id
WHERE rv.active
GROUP BY rv.username
ORDER BY rv.username;

-- Transactional merge attempt.
BEGIN;

SELECT merge_pull_request(
    (
        SELECT pull_request_id
        FROM pull_requests
        WHERE title = 'Implement reliable exception handling'
    )
);

COMMIT;

-- Failure-case evaluation is intentionally read-only.
SELECT
    pr.pull_request_id,
    pr.title,
    eligibility.eligible,
    eligibility.reason
FROM pull_requests pr
CROSS JOIN LATERAL pull_request_merge_eligibility(
    pr.pull_request_id
) AS eligibility
WHERE pr.title = 'Introduce an intentionally failing workflow';

-- A protected merge cannot be performed until its failed check,
-- unresolved conversations, and missing approvals are corrected.
