DROP SCHEMA IF EXISTS control_flow_governance CASCADE;
CREATE SCHEMA control_flow_governance;
SET search_path TO control_flow_governance;

-- The relational model uses repository governance as the concrete domain
-- in which else represents a successful non-exceptional decision path and
-- finally represents cleanup/audit work that must occur for every attempt.

CREATE TYPE pr_state AS ENUM (
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
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE branches (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    name TEXT NOT NULL,
    protected BOOLEAN NOT NULL DEFAULT FALSE,
    head_sha TEXT,
    UNIQUE (repository_id, name)
);

CREATE TABLE commits (
    commit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    sha TEXT NOT NULL,
    author TEXT NOT NULL,
    committed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (repository_id, sha),
    CHECK (length(sha) >= 7)
);

CREATE TABLE pull_requests (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    number INTEGER NOT NULL,
    source_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    state pr_state NOT NULL DEFAULT 'open',
    head_sha TEXT NOT NULL,
    merge_strategy TEXT NOT NULL DEFAULT 'squash',
    synchronized_with_base BOOLEAN NOT NULL DEFAULT TRUE,
    unresolved_conversations INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (repository_id, number),
    CHECK (source_branch_id <> target_branch_id),
    CHECK (unresolved_conversations >= 0),
    CHECK (merge_strategy IN ('merge', 'squash', 'rebase'))
);

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    commit_id BIGINT NOT NULL REFERENCES commits(commit_id),
    position INTEGER NOT NULL,
    PRIMARY KEY (pull_request_id, commit_id),
    UNIQUE (pull_request_id, position),
    CHECK (position > 0)
);

CREATE TABLE reviewers (
    reviewer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES reviewers(reviewer_id),
    state review_state NOT NULL,
    commit_sha TEXT NOT NULL,
    stale BOOLEAN NOT NULL DEFAULT FALSE,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE review_comments (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES reviews(review_id)
        ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (line_number > 0),
    CHECK (length(trim(body)) > 0)
);

CREATE TABLE status_checks (
    status_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (pull_request_id, check_name)
);

CREATE TABLE branch_protection_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL UNIQUE
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 0,
    require_resolved_conversations BOOLEAN NOT NULL DEFAULT TRUE,
    allow_direct_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    require_linear_history BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (required_approvals >= 0)
);

CREATE TABLE required_status_checks (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    PRIMARY KEY (policy_id, check_name)
);

CREATE TABLE merge_attempts (
    attempt_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    eligible BOOLEAN NOT NULL,
    failure_reason TEXT,
    finalized_at TIMESTAMPTZ
);

CREATE INDEX idx_reviews_pr_state
    ON reviews (pull_request_id, state, stale);

CREATE INDEX idx_status_checks_pr_name
    ON status_checks (pull_request_id, check_name);

CREATE INDEX idx_pr_repository_state
    ON pull_requests (repository_id, state);

CREATE INDEX idx_comments_review_resolution
    ON review_comments (review_id, resolved);

CREATE OR REPLACE FUNCTION validate_review_submission()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    current_head TEXT;
BEGIN
    SELECT head_sha
    INTO current_head
    FROM pull_requests
    WHERE pull_request_id = NEW.pull_request_id;

    IF current_head IS NULL THEN
        RAISE EXCEPTION 'Pull request does not exist';
    END IF;

    -- An approval against an old commit is immediately stale.
    IF NEW.state = 'approved' AND NEW.commit_sha <> current_head THEN
        NEW.stale := TRUE;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_review_submission
BEFORE INSERT OR UPDATE ON reviews
FOR EACH ROW
EXECUTE FUNCTION validate_review_submission();

CREATE OR REPLACE FUNCTION mark_approvals_stale_on_sync()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.head_sha IS DISTINCT FROM OLD.head_sha
       OR (
           OLD.synchronized_with_base = TRUE
           AND NEW.synchronized_with_base = FALSE
       ) THEN
        UPDATE reviews
        SET stale = TRUE
        WHERE pull_request_id = NEW.pull_request_id
          AND state = 'approved';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_mark_approvals_stale
AFTER UPDATE ON pull_requests
FOR EACH ROW
EXECUTE FUNCTION mark_approvals_stale_on_sync();

CREATE OR REPLACE FUNCTION merge_eligibility(
    p_pull_request_id BIGINT
)
RETURNS TABLE (
    eligible BOOLEAN,
    reason TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    required_approvals INTEGER;
    actual_approvals INTEGER;
    unresolved INTEGER;
    synchronized BOOLEAN;
    required_check TEXT;
    check_passed BOOLEAN;
    linear_history_required BOOLEAN;
    merge_method TEXT;
BEGIN
    SELECT
        bp.required_approvals,
        bp.require_linear_history
    INTO
        required_approvals,
        linear_history_required
    FROM pull_requests pr
    JOIN branch_protection_policies bp
      ON bp.repository_id = pr.repository_id
    WHERE pr.pull_request_id = p_pull_request_id;

    IF NOT FOUND THEN
        RETURN QUERY
        SELECT FALSE, 'No branch-protection policy exists.';
        RETURN;
    END IF;

    SELECT
        pr.unresolved_conversations,
        pr.synchronized_with_base,
        pr.merge_strategy
    INTO
        unresolved,
        synchronized,
        merge_method
    FROM pull_requests pr
    WHERE pr.pull_request_id = p_pull_request_id
      AND pr.state = 'open';

    IF NOT FOUND THEN
        RETURN QUERY
        SELECT FALSE, 'Pull request is not open.';
        RETURN;
    END IF;

    SELECT count(*)
    INTO actual_approvals
    FROM reviews r
    JOIN reviewers rv
      ON rv.reviewer_id = r.reviewer_id
    JOIN pull_requests pr
      ON pr.pull_request_id = r.pull_request_id
    WHERE r.pull_request_id = p_pull_request_id
      AND r.state = 'approved'
      AND r.stale = FALSE
      AND rv.active = TRUE
      AND r.commit_sha = pr.head_sha;

    IF actual_approvals < required_approvals THEN
        RETURN QUERY
        SELECT FALSE,
               format(
                   'Required approvals: %s; current approvals: %s.',
                   required_approvals,
                   actual_approvals
               );
        RETURN;
    ELSE
        -- The ELSE path is reached only after the approval condition
        -- has been evaluated successfully.
        NULL;
    END IF;

    IF NOT synchronized THEN
        RETURN QUERY
        SELECT FALSE, 'Pull request is not synchronized with base.';
        RETURN;
    END IF;

    IF unresolved > 0 THEN
        RETURN QUERY
        SELECT FALSE, 'Review conversations remain unresolved.';
        RETURN;
    END IF;

    IF linear_history_required AND merge_method = 'merge' THEN
        RETURN QUERY
        SELECT FALSE,
               'Merge strategy violates the linear-history requirement.';
        RETURN;
    END IF;

    FOR required_check IN
        SELECT rsc.check_name
        FROM branch_protection_policies bp
        JOIN required_status_checks rsc
          ON rsc.policy_id = bp.policy_id
        JOIN pull_requests pr
          ON pr.repository_id = bp.repository_id
        WHERE pr.pull_request_id = p_pull_request_id
    LOOP
        SELECT sc.passed
        INTO check_passed
        FROM status_checks sc
        WHERE sc.pull_request_id = p_pull_request_id
          AND sc.check_name = required_check;

        IF check_passed IS DISTINCT FROM TRUE THEN
            RETURN QUERY
            SELECT FALSE,
                   'Required status check failed or is missing: '
                   || required_check;
            RETURN;
        END IF;
    END LOOP;

    RETURN QUERY
    SELECT TRUE,
           'All merge conditions are satisfied.';
END;
$$;

CREATE OR REPLACE PROCEDURE finalize_merge_attempt(
    p_pull_request_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    result_row RECORD;
    attempt_id_value BIGINT;
BEGIN
    INSERT INTO merge_attempts (
        pull_request_id,
        eligible
    )
    VALUES (
        p_pull_request_id,
        FALSE
    )
    RETURNING attempt_id INTO attempt_id_value;

    BEGIN
        SELECT *
        INTO result_row
        FROM merge_eligibility(p_pull_request_id)
        LIMIT 1;

        IF result_row.eligible THEN
            UPDATE pull_requests
            SET state = 'merged'
            WHERE pull_request_id = p_pull_request_id;

            UPDATE merge_attempts
            SET eligible = TRUE,
                failure_reason = NULL
            WHERE attempt_id = attempt_id_value;
        ELSE
            UPDATE merge_attempts
            SET eligible = FALSE,
                failure_reason = result_row.reason
            WHERE attempt_id = attempt_id_value;
        END IF;

    EXCEPTION
        WHEN OTHERS THEN
            UPDATE merge_attempts
            SET eligible = FALSE,
                failure_reason = SQLERRM
            WHERE attempt_id = attempt_id_value;
            RAISE;
    END;

    -- PostgreSQL has no native FINALLY clause. This update is the
    -- deterministic finalization operation executed after the decision
    -- block completes normally.
    UPDATE merge_attempts
    SET finalized_at = CURRENT_TIMESTAMP
    WHERE attempt_id = attempt_id_value;
END;
$$;

INSERT INTO repositories (name)
VALUES ('secure-platform');

INSERT INTO branches (
    repository_id,
    name,
    protected,
    head_sha
)
SELECT repository_id, 'main', TRUE, 'abcdef2'
FROM repositories
WHERE name = 'secure-platform';

INSERT INTO branches (
    repository_id,
    name,
    protected,
    head_sha
)
SELECT repository_id, 'develop', FALSE, 'abcdef2'
FROM repositories
WHERE name = 'secure-platform';

INSERT INTO commits (repository_id, sha, author)
SELECT repository_id, 'abcdef1', 'alice'
FROM repositories
WHERE name = 'secure-platform';

INSERT INTO commits (repository_id, sha, author)
SELECT repository_id, 'abcdef2', 'bob'
FROM repositories
WHERE name = 'secure-platform';

INSERT INTO pull_requests (
    repository_id,
    number,
    source_branch_id,
    target_branch_id,
    state,
    head_sha,
    merge_strategy,
    synchronized_with_base,
    unresolved_conversations
)
SELECT
    r.repository_id,
    1,
    source.branch_id,
    target.branch_id,
    'open',
    'abcdef2',
    'squash',
    TRUE,
    0
FROM repositories r
JOIN branches source
  ON source.repository_id = r.repository_id
 AND source.name = 'develop'
JOIN branches target
  ON target.repository_id = r.repository_id
 AND target.name = 'main'
WHERE r.name = 'secure-platform';

INSERT INTO pull_request_commits (
    pull_request_id,
    commit_id,
    position
)
SELECT pr.pull_request_id, c.commit_id, 1
FROM pull_requests pr
JOIN commits c
  ON c.sha = 'abcdef1'
WHERE pr.number = 1;

INSERT INTO pull_request_commits (
    pull_request_id,
    commit_id,
    position
)
SELECT pr.pull_request_id, c.commit_id, 2
FROM pull_requests pr
JOIN commits c
  ON c.sha = 'abcdef2'
WHERE pr.number = 1;

INSERT INTO reviewers (username)
VALUES ('alice'), ('bob'), ('carol');

INSERT INTO branch_protection_policies (
    repository_id,
    required_approvals,
    require_resolved_conversations,
    allow_direct_push,
    allow_force_push,
    require_linear_history
)
SELECT repository_id, 2, TRUE, FALSE, FALSE, TRUE
FROM repositories
WHERE name = 'secure-platform';

INSERT INTO required_status_checks (policy_id, check_name)
SELECT policy_id, 'tests'
FROM branch_protection_policies;

INSERT INTO required_status_checks (policy_id, check_name)
SELECT policy_id, 'security'
FROM branch_protection_policies;

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    state,
    commit_sha
)
SELECT
    pr.pull_request_id,
    rv.reviewer_id,
    'approved',
    pr.head_sha
FROM pull_requests pr
JOIN reviewers rv
  ON rv.username = 'alice'
WHERE pr.number = 1;

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    state,
    commit_sha
)
SELECT
    pr.pull_request_id,
    rv.reviewer_id,
    'approved',
    pr.head_sha
FROM pull_requests pr
JOIN reviewers rv
  ON rv.username = 'bob'
WHERE pr.number = 1;

INSERT INTO review_comments (
    review_id,
    file_path,
    line_number,
    body,
    resolved
)
SELECT
    review_id,
    'src/payment_service.py',
    42,
    'Validation is required before the state transition.',
    TRUE
FROM reviews
WHERE reviewer_id = (
    SELECT reviewer_id
    FROM reviewers
    WHERE username = 'alice'
)
LIMIT 1;

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    passed
)
SELECT pull_request_id, 'tests', TRUE
FROM pull_requests
WHERE number = 1;

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    passed
)
SELECT pull_request_id, 'security', TRUE
FROM pull_requests
WHERE number = 1;

-- Basic repository and branch retrieval.
SELECT
    r.name AS repository,
    b.name AS branch,
    b.protected,
    b.head_sha
FROM repositories r
JOIN branches b
  ON b.repository_id = r.repository_id
ORDER BY r.name, b.name;

-- Review decision reporting.
SELECT
    pr.number,
    rv.username,
    re.state,
    re.stale,
    re.commit_sha
FROM pull_requests pr
JOIN reviews re
  ON re.pull_request_id = pr.pull_request_id
JOIN reviewers rv
  ON rv.reviewer_id = re.reviewer_id
ORDER BY pr.number, rv.username;

-- Evaluate the complete merge policy.
SELECT *
FROM merge_eligibility(
    (SELECT pull_request_id
     FROM pull_requests
     WHERE number = 1)
);

-- Transactionally attempt the merge and record finalization.
BEGIN;

CALL finalize_merge_attempt(
    (SELECT pull_request_id
     FROM pull_requests
     WHERE number = 1)
);

COMMIT;

-- Merge workflow and finalization reporting.
SELECT
    ma.attempt_id,
    pr.number,
    ma.eligible,
    ma.failure_reason,
    ma.attempted_at,
    ma.finalized_at
FROM merge_attempts ma
JOIN pull_requests pr
  ON pr.pull_request_id = ma.pull_request_id
ORDER BY ma.attempt_id;

-- Demonstrate a failing policy state without modifying the successful PR.
BEGIN;

INSERT INTO pull_requests (
    repository_id,
    number,
    source_branch_id,
    target_branch_id,
    state,
    head_sha,
    merge_strategy,
    synchronized_with_base,
    unresolved_conversations
)
SELECT
    r.repository_id,
    2,
    source.branch_id,
    target.branch_id,
    'open',
    'abcdef2',
    'squash',
    FALSE,
    1
FROM repositories r
JOIN branches source
  ON source.repository_id = r.repository_id
 AND source.name = 'develop'
JOIN branches target
  ON target.repository_id = r.repository_id
 AND target.name = 'main'
WHERE r.name = 'secure-platform';

SELECT *
FROM merge_eligibility(
    (SELECT pull_request_id
     FROM pull_requests
     WHERE number = 2)
);

ROLLBACK;

-- Aggregation of review and status-check state.
SELECT
    pr.number,
    COUNT(DISTINCT re.review_id) AS review_count,
    COUNT(DISTINCT CASE
        WHEN re.state = 'approved'
         AND re.stale = FALSE
        THEN re.review_id
    END) AS active_approval_count,
    COUNT(DISTINCT sc.status_check_id) AS status_check_count,
    COUNT(DISTINCT CASE
        WHEN sc.passed THEN sc.status_check_id
    END) AS passing_check_count
FROM pull_requests pr
LEFT JOIN reviews re
  ON re.pull_request_id = pr.pull_request_id
LEFT JOIN status_checks sc
  ON sc.pull_request_id = pr.pull_request_id
GROUP BY pr.number
ORDER BY pr.number;
