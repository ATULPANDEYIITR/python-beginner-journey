DROP SCHEMA IF EXISTS repository_governance CASCADE;
CREATE SCHEMA repository_governance;

SET search_path TO repository_governance, public;

CREATE TYPE pr_state AS ENUM ('draft', 'open', 'closed', 'merged');
CREATE TYPE review_state AS ENUM (
    'commented',
    'approved',
    'changes_requested',
    'dismissed'
);
CREATE TYPE check_state AS ENUM ('passing', 'failing', 'pending');
CREATE TYPE merge_strategy AS ENUM ('merge_commit', 'squash', 'rebase');

CREATE TABLE repositories (
    repository_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    administrator_bypass_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(name)) > 0)
);

CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (length(trim(username)) > 0)
);

CREATE TABLE branches (
    branch_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id),
    name TEXT NOT NULL,
    protected BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (repository_id, name),
    CHECK (length(trim(name)) > 0)
);

CREATE TABLE commits (
    commit_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id),
    sha TEXT NOT NULL UNIQUE,
    message TEXT NOT NULL,
    parent_commit_id BIGINT REFERENCES commits(commit_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(sha) >= 7),
    CHECK (length(trim(message)) > 0)
);

CREATE TABLE pull_requests (
    pull_request_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id),
    number INTEGER NOT NULL,
    source_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    state pr_state NOT NULL DEFAULT 'open',
    is_draft BOOLEAN NOT NULL DEFAULT FALSE,
    current_commit_id BIGINT REFERENCES commits(commit_id),
    merge_strategy merge_strategy,
    created_by BIGINT NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMPTZ,
    merged_at TIMESTAMPTZ,
    UNIQUE (repository_id, number),
    CHECK (source_branch_id <> target_branch_id),
    CHECK (
        (state = 'merged' AND merged_at IS NOT NULL)
        OR state <> 'merged'
    ),
    CHECK (
        (state = 'closed' AND closed_at IS NOT NULL)
        OR state <> 'closed'
    )
);

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id),
    commit_order INTEGER NOT NULL,
    PRIMARY KEY (pull_request_id, commit_id),
    UNIQUE (pull_request_id, commit_order),
    CHECK (commit_order > 0)
);

CREATE TABLE pull_request_files (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    path TEXT NOT NULL,
    PRIMARY KEY (pull_request_id, path),
    CHECK (length(trim(path)) > 0)
);

CREATE TABLE reviews (
    review_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES users(user_id),
    state review_state NOT NULL,
    commit_id BIGINT NOT NULL REFERENCES commits(commit_id),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE review_comments (
    comment_id BIGSERIAL PRIMARY KEY,
    review_id BIGINT NOT NULL
        REFERENCES reviews(review_id) ON DELETE CASCADE,
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ,
    CHECK (length(trim(body)) > 0),
    CHECK (
        (resolved = TRUE AND resolved_at IS NOT NULL)
        OR resolved = FALSE
    )
);

CREATE TABLE status_checks (
    status_check_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    state check_state NOT NULL,
    completed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, check_name),
    CHECK (
        (state = 'passing' AND completed_at IS NOT NULL)
        OR state <> 'passing'
    )
);

CREATE TABLE branch_protection_policies (
    policy_id BIGSERIAL PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE
        REFERENCES branches(branch_id) ON DELETE CASCADE,
    required_reviews INTEGER NOT NULL DEFAULT 0,
    require_resolved_conversations BOOLEAN NOT NULL DEFAULT TRUE,
    dismiss_stale_reviews BOOLEAN NOT NULL DEFAULT TRUE,
    allow_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_deletion BOOLEAN NOT NULL DEFAULT FALSE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    allow_administrator_bypass BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (required_reviews >= 0)
);

CREATE TABLE required_status_checks (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    PRIMARY KEY (policy_id, check_name),
    CHECK (length(trim(check_name)) > 0)
);

CREATE TABLE reviewer_eligibility (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    PRIMARY KEY (policy_id, user_id)
);

CREATE INDEX idx_pr_target_state
    ON pull_requests(target_branch_id, state);

CREATE INDEX idx_reviews_pr_state
    ON reviews(pull_request_id, state);

CREATE INDEX idx_checks_pr_state
    ON status_checks(pull_request_id, state);

CREATE INDEX idx_comments_unresolved
    ON review_comments(review_id)
    WHERE resolved = FALSE;

CREATE OR REPLACE FUNCTION validate_review_commit()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    latest_commit BIGINT;
BEGIN
    SELECT current_commit_id
    INTO latest_commit
    FROM pull_requests
    WHERE pull_request_id = NEW.pull_request_id;

    IF latest_commit IS NOT NULL
       AND NEW.commit_id <> latest_commit
       AND NEW.state = 'approved' THEN
        RAISE EXCEPTION
            'Approval is stale: review commit % differs from current PR commit %',
            NEW.commit_id,
            latest_commit;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_review_commit
BEFORE INSERT OR UPDATE ON reviews
FOR EACH ROW
EXECUTE FUNCTION validate_review_commit();

CREATE OR REPLACE FUNCTION resolve_comment_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.resolved AND NOT OLD.resolved THEN
        NEW.resolved_at := CURRENT_TIMESTAMP;
    ELSIF NOT NEW.resolved THEN
        NEW.resolved_at := NULL;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_resolve_comment_timestamp
BEFORE UPDATE ON review_comments
FOR EACH ROW
EXECUTE FUNCTION resolve_comment_timestamp();

CREATE OR REPLACE FUNCTION merge_eligibility(
    p_pull_request_id BIGINT
)
RETURNS TABLE (
    eligible BOOLEAN,
    reason TEXT,
    approvals BIGINT,
    required_approvals INTEGER,
    failed_checks BIGINT,
    unresolved_conversations BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    target_branch BIGINT;
    policy_id_value BIGINT;
    required_reviews_value INTEGER;
    required_conversations BOOLEAN;
BEGIN
    SELECT target_branch_id
    INTO target_branch
    FROM pull_requests
    WHERE pull_request_id = p_pull_request_id
      AND state = 'open';

    IF target_branch IS NULL THEN
        RETURN QUERY
        SELECT FALSE, 'Pull Request does not exist or is not open.',
               0::BIGINT, 0, 0::BIGINT, 0::BIGINT;
        RETURN;
    END IF;

    SELECT bpp.policy_id,
           bpp.required_reviews,
           bpp.require_resolved_conversations
    INTO policy_id_value, required_reviews_value, required_conversations
    FROM branch_protection_policies bpp
    WHERE bpp.branch_id = target_branch;

    IF policy_id_value IS NULL THEN
        RETURN QUERY
        SELECT TRUE, 'Target branch has no protection policy.',
               0::BIGINT, 0, 0::BIGINT, 0::BIGINT;
        RETURN;
    END IF;

    RETURN QUERY
    WITH eligible_reviewers AS (
        SELECT DISTINCT r.reviewer_id
        FROM reviews r
        JOIN pull_requests p
          ON p.pull_request_id = r.pull_request_id
        JOIN reviewer_eligibility re
          ON re.policy_id = policy_id_value
         AND re.user_id = r.reviewer_id
        WHERE r.pull_request_id = p_pull_request_id
          AND r.state = 'approved'
          AND r.commit_id = p.current_commit_id
    ),
    failed AS (
        SELECT COUNT(*)::BIGINT AS count
        FROM required_status_checks rsc
        LEFT JOIN status_checks sc
          ON sc.pull_request_id = p_pull_request_id
         AND sc.check_name = rsc.check_name
        WHERE rsc.policy_id = policy_id_value
          AND sc.state IS DISTINCT FROM 'passing'
    ),
    unresolved AS (
        SELECT COUNT(*)::BIGINT AS count
        FROM review_comments rc
        JOIN reviews r ON r.review_id = rc.review_id
        WHERE r.pull_request_id = p_pull_request_id
          AND rc.resolved = FALSE
    )
    SELECT
        (
            (SELECT COUNT(*) FROM eligible_reviewers)
                >= required_reviews_value
            AND (SELECT count FROM failed) = 0
            AND (
                NOT required_conversations
                OR (SELECT count FROM unresolved) = 0
            )
        ),
        CASE
            WHEN (SELECT COUNT(*) FROM eligible_reviewers)
                    < required_reviews_value
                THEN 'Required approvals are missing.'
            WHEN (SELECT count FROM failed) > 0
                THEN 'Required status checks are not passing.'
            WHEN required_conversations
                 AND (SELECT count FROM unresolved) > 0
                THEN 'Review conversations remain unresolved.'
            ELSE 'Merge conditions satisfied.'
        END,
        (SELECT COUNT(*) FROM eligible_reviewers),
        required_reviews_value,
        (SELECT count FROM failed),
        (SELECT count FROM unresolved);
END;
$$;

CREATE VIEW pull_request_governance_report AS
SELECT
    p.pull_request_id,
    r.name AS repository,
    p.number,
    p.state,
    sb.name AS source_branch,
    tb.name AS target_branch,
    p.is_draft,
    COUNT(DISTINCT rv.review_id) AS review_count,
    COUNT(DISTINCT rv.reviewer_id)
        FILTER (WHERE rv.state = 'approved') AS raw_approval_count,
    COUNT(DISTINCT sc.status_check_id)
        FILTER (WHERE sc.state = 'passing') AS passing_checks,
    COUNT(DISTINCT rc.comment_id)
        FILTER (WHERE rc.resolved = FALSE) AS unresolved_comments
FROM pull_requests p
JOIN repositories r ON r.repository_id = p.repository_id
JOIN branches sb ON sb.branch_id = p.source_branch_id
JOIN branches tb ON tb.branch_id = p.target_branch_id
LEFT JOIN reviews rv ON rv.pull_request_id = p.pull_request_id
LEFT JOIN status_checks sc ON sc.pull_request_id = p.pull_request_id
LEFT JOIN review_comments rc ON rc.review_id = rv.review_id
GROUP BY
    p.pull_request_id,
    r.name,
    p.number,
    p.state,
    sb.name,
    tb.name,
    p.is_draft;

INSERT INTO repositories (name, administrator_bypass_enabled)
VALUES ('payments-service', TRUE);

INSERT INTO users (username) VALUES
    ('alice'),
    ('bob'),
    ('carol'),
    ('release-admin');

INSERT INTO branches (repository_id, name, protected)
SELECT repository_id, 'main', TRUE
FROM repositories
WHERE name = 'payments-service';

INSERT INTO branches (repository_id, name, protected)
SELECT repository_id, 'feature/payment-validation', FALSE
FROM repositories
WHERE name = 'payments-service';

INSERT INTO commits (repository_id, sha, message)
SELECT repository_id, 'abcdef1234567', 'Initial production state'
FROM repositories
WHERE name = 'payments-service';

INSERT INTO commits (repository_id, sha, message, parent_commit_id)
SELECT
    r.repository_id,
    '123456789abcd',
    'Implement payment validation',
    c.commit_id
FROM repositories r
JOIN commits c
  ON c.sha = 'abcdef1234567'
WHERE r.name = 'payments-service';

INSERT INTO branch_protection_policies (
    branch_id,
    required_reviews,
    require_resolved_conversations,
    dismiss_stale_reviews,
    allow_force_push,
    allow_deletion,
    require_linear_history,
    allow_administrator_bypass
)
SELECT
    branch_id,
    2,
    TRUE,
    TRUE,
    FALSE,
    FALSE,
    TRUE,
    FALSE
FROM branches
WHERE name = 'main';

INSERT INTO required_status_checks (policy_id, check_name)
SELECT policy_id, 'unit-tests'
FROM branch_protection_policies
WHERE branch_id = (
    SELECT branch_id FROM branches WHERE name = 'main'
);

INSERT INTO required_status_checks (policy_id, check_name)
SELECT policy_id, 'security-scan'
FROM branch_protection_policies
WHERE branch_id = (
    SELECT branch_id FROM branches WHERE name = 'main'
);

INSERT INTO reviewer_eligibility (policy_id, user_id)
SELECT bpp.policy_id, u.user_id
FROM branch_protection_policies bpp
JOIN branches b ON b.branch_id = bpp.branch_id
JOIN users u ON u.username IN ('alice', 'bob')
WHERE b.name = 'main';

INSERT INTO pull_requests (
    repository_id,
    number,
    source_branch_id,
    target_branch_id,
    state,
    is_draft,
    current_commit_id,
    created_by
)
SELECT
    r.repository_id,
    101,
    sb.branch_id,
    tb.branch_id,
    'open',
    FALSE,
    c.commit_id,
    u.user_id
FROM repositories r
JOIN branches sb
  ON sb.repository_id = r.repository_id
 AND sb.name = 'feature/payment-validation'
JOIN branches tb
  ON tb.repository_id = r.repository_id
 AND tb.name = 'main'
JOIN commits c
  ON c.sha = '123456789abcd'
JOIN users u
  ON u.username = 'alice'
WHERE r.name = 'payments-service';

INSERT INTO pull_request_commits (
    pull_request_id,
    commit_id,
    commit_order
)
SELECT p.pull_request_id, c.commit_id, 1
FROM pull_requests p
JOIN commits c ON c.sha = '123456789abcd'
WHERE p.number = 101;

INSERT INTO pull_request_files (pull_request_id, path)
SELECT pull_request_id, path
FROM pull_requests
CROSS JOIN (VALUES
    ('payment_validation.py'),
    ('test_payment_validation.py')
) AS files(path)
WHERE number = 101;

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    state,
    commit_id
)
SELECT p.pull_request_id, u.user_id, 'approved', c.commit_id
FROM pull_requests p
JOIN users u ON u.username = 'alice'
JOIN commits c ON c.sha = '123456789abcd'
WHERE p.number = 101;

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    state,
    commit_id
)
SELECT p.pull_request_id, u.user_id, 'commented', c.commit_id
FROM pull_requests p
JOIN users u ON u.username = 'bob'
JOIN commits c ON c.sha = '123456789abcd'
WHERE p.number = 101;

INSERT INTO review_comments (review_id, body)
SELECT review_id, 'Validate currency and amount boundaries.'
FROM reviews
WHERE pull_request_id = (
    SELECT pull_request_id FROM pull_requests WHERE number = 101
)
AND reviewer_id = (
    SELECT user_id FROM users WHERE username = 'bob'
);

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    state,
    completed_at
)
SELECT pull_request_id, 'unit-tests', 'passing', CURRENT_TIMESTAMP
FROM pull_requests
WHERE number = 101;

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    state,
    completed_at
)
SELECT pull_request_id, 'security-scan', 'passing', CURRENT_TIMESTAMP
FROM pull_requests
WHERE number = 101;

-- First evaluation intentionally fails because one approval and one
-- unresolved conversation remain.
SELECT *
FROM merge_eligibility(
    (SELECT pull_request_id FROM pull_requests WHERE number = 101)
);

-- Resolve the review conversation.
UPDATE review_comments
SET resolved = TRUE
WHERE review_id = (
    SELECT rv.review_id
    FROM reviews rv
    JOIN users u ON u.user_id = rv.reviewer_id
    WHERE rv.pull_request_id = (
        SELECT pull_request_id FROM pull_requests WHERE number = 101
    )
    AND u.username = 'bob'
);

-- Convert Bob's review to an approval.
UPDATE reviews
SET state = 'approved'
WHERE pull_request_id = (
    SELECT pull_request_id FROM pull_requests WHERE number = 101
)
AND reviewer_id = (
    SELECT user_id FROM users WHERE username = 'bob'
);

SELECT *
FROM merge_eligibility(
    (SELECT pull_request_id FROM pull_requests WHERE number = 101)
);

-- Transactional merge: eligibility is checked before the state transition.
BEGIN;

DO $$
DECLARE
    pr_id BIGINT;
    can_merge BOOLEAN;
BEGIN
    SELECT pull_request_id
    INTO pr_id
    FROM pull_requests
    WHERE number = 101
    FOR UPDATE;

    SELECT eligible
    INTO can_merge
    FROM merge_eligibility(pr_id);

    IF NOT can_merge THEN
        RAISE EXCEPTION 'Pull Request #101 is not merge eligible.';
    END IF;

    UPDATE pull_requests
    SET state = 'merged',
        merge_strategy = 'squash',
        merged_at = CURRENT_TIMESTAMP
    WHERE pull_request_id = pr_id;
END;
$$;

COMMIT;

SELECT *
FROM pull_request_governance_report
WHERE number = 101;

-- Demonstrate a closed Pull Request and explicit reopening workflow.
INSERT INTO pull_requests (
    repository_id,
    number,
    source_branch_id,
    target_branch_id,
    state,
    is_draft,
    created_by,
    closed_at
)
SELECT
    r.repository_id,
    102,
    sb.branch_id,
    tb.branch_id,
    'closed',
    FALSE,
    u.user_id,
    CURRENT_TIMESTAMP
FROM repositories r
JOIN branches sb
  ON sb.repository_id = r.repository_id
 AND sb.name = 'feature/payment-validation'
JOIN branches tb
  ON tb.repository_id = r.repository_id
 AND tb.name = 'main'
JOIN users u ON u.username = 'alice'
WHERE r.name = 'payments-service';

UPDATE pull_requests
SET state = 'open',
    closed_at = NULL
WHERE number = 102
  AND state = 'closed';

SELECT number, state
FROM pull_requests
WHERE number IN (101, 102)
ORDER BY number;
