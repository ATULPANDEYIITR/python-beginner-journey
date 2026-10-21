DROP SCHEMA IF EXISTS functions_as_data_governance CASCADE;
CREATE SCHEMA functions_as_data_governance;
SET search_path TO functions_as_data_governance;

-- The relational model keeps Pull Requests, Code Review, Approvals, and
-- Branch Protection separate. PostgreSQL stores policy attributes as data;
-- executable policy functions evaluate that data.

CREATE TYPE pull_request_state AS ENUM (
    'draft',
    'open',
    'closed',
    'merged'
);

CREATE TYPE review_state AS ENUM (
    'commented',
    'approved',
    'changes_requested',
    'dismissed'
);

CREATE TYPE merge_strategy AS ENUM (
    'merge_commit',
    'squash',
    'rebase'
);

CREATE TABLE repository (
    repository_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CHECK (btrim(name) <> ''),
    CHECK (btrim(default_branch) <> '')
);

CREATE TABLE repository_member (
    repository_id BIGINT NOT NULL
        REFERENCES repository(repository_id)
        ON DELETE CASCADE,
    username TEXT NOT NULL,
    is_administrator BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (repository_id, username),
    CHECK (btrim(username) <> '')
);

CREATE TABLE branch (
    branch_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repository(repository_id)
        ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (repository_id, branch_name),
    CHECK (btrim(branch_name) <> '')
);

CREATE TABLE branch_protection (
    protection_id BIGSERIAL PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE
        REFERENCES branch(branch_id)
        ON DELETE CASCADE,
    required_reviews INTEGER NOT NULL DEFAULT 0,
    require_conversation_resolution BOOLEAN NOT NULL DEFAULT FALSE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    allow_direct_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_deletion BOOLEAN NOT NULL DEFAULT FALSE,
    allow_admin_bypass BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (required_reviews >= 0)
);

CREATE TABLE protected_status_check (
    protection_id BIGINT NOT NULL
        REFERENCES branch_protection(protection_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    PRIMARY KEY (protection_id, check_name),
    CHECK (btrim(check_name) <> '')
);

CREATE TABLE pull_request (
    pull_request_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repository(repository_id)
        ON DELETE CASCADE,
    number INTEGER NOT NULL,
    source_branch_id BIGINT NOT NULL
        REFERENCES branch(branch_id),
    target_branch_id BIGINT NOT NULL
        REFERENCES branch(branch_id),
    title TEXT NOT NULL,
    state pull_request_state NOT NULL DEFAULT 'open',
    draft BOOLEAN NOT NULL DEFAULT FALSE,
    mergeable BOOLEAN NOT NULL DEFAULT TRUE,
    synchronized_with_base BOOLEAN NOT NULL DEFAULT TRUE,
    open_conversations INTEGER NOT NULL DEFAULT 0,
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    closed_at TIMESTAMPTZ,
    merged_at TIMESTAMPTZ,
    UNIQUE (repository_id, number),
    CHECK (number > 0),
    CHECK (source_branch_id <> target_branch_id),
    CHECK (open_conversations >= 0),
    CHECK (btrim(title) <> ''),
    CHECK (btrim(created_by) <> ''),
    CHECK (
        (state = 'merged' AND merged_at IS NOT NULL)
        OR state <> 'merged'
    )
);

CREATE TABLE commit (
    commit_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repository(repository_id)
        ON DELETE CASCADE,
    sha CHAR(40) NOT NULL,
    message TEXT NOT NULL,
    author TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (repository_id, sha),
    CHECK (sha ~ '^[0-9a-fA-F]{40}$'),
    CHECK (btrim(message) <> ''),
    CHECK (btrim(author) <> '')
);

CREATE TABLE pull_request_commit (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_request(pull_request_id)
        ON DELETE CASCADE,
    commit_id BIGINT NOT NULL
        REFERENCES commit(commit_id)
        ON DELETE RESTRICT,
    position INTEGER NOT NULL,
    PRIMARY KEY (pull_request_id, commit_id),
    UNIQUE (pull_request_id, position),
    CHECK (position > 0)
);

CREATE TABLE review (
    review_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_request(pull_request_id)
        ON DELETE CASCADE,
    reviewer TEXT NOT NULL,
    state review_state NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    dismissed_at TIMESTAMPTZ,
    dismissal_reason TEXT,
    CHECK (btrim(reviewer) <> ''),
    CHECK (
        state <> 'dismissed'
        OR dismissed_at IS NOT NULL
    )
);

CREATE TABLE review_comment (
    comment_id BIGSERIAL PRIMARY KEY,
    review_id BIGINT NOT NULL
        REFERENCES review(review_id)
        ON DELETE CASCADE,
    commit_id BIGINT
        REFERENCES commit(commit_id)
        ON DELETE RESTRICT,
    file_path TEXT,
    line_number INTEGER,
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CHECK (btrim(body) <> ''),
    CHECK (line_number IS NULL OR line_number > 0)
);

CREATE TABLE status_check (
    status_check_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_request(pull_request_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (pull_request_id, check_name),
    CHECK (btrim(check_name) <> '')
);

CREATE TABLE review_request (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_request(pull_request_id)
        ON DELETE CASCADE,
    reviewer TEXT NOT NULL,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (pull_request_id, reviewer),
    CHECK (btrim(reviewer) <> '')
);

CREATE TABLE merge_event (
    merge_event_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL UNIQUE
        REFERENCES pull_request(pull_request_id)
        ON DELETE RESTRICT,
    strategy merge_strategy NOT NULL,
    merged_by TEXT NOT NULL,
    merged_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CHECK (btrim(merged_by) <> '')
);

CREATE INDEX idx_pull_request_target_state
    ON pull_request (target_branch_id, state);

CREATE INDEX idx_review_pr_state_reviewer
    ON review (pull_request_id, state, reviewer);

CREATE INDEX idx_status_check_pr_name
    ON status_check (pull_request_id, check_name);

CREATE INDEX idx_review_comment_unresolved
    ON review_comment (review_id)
    WHERE resolved = FALSE;

-- The trigger prevents a Pull Request from claiming merged state without a
-- merge event. This makes merge state transition an integrity rule rather
-- than an application-only convention.
CREATE OR REPLACE FUNCTION enforce_merged_state()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.state = 'merged' AND OLD.state <> 'merged' THEN
        IF NOT EXISTS (
            SELECT 1
            FROM merge_event
            WHERE pull_request_id = NEW.pull_request_id
        ) THEN
            RAISE EXCEPTION
                'Pull Request % cannot become merged without merge event',
                NEW.number;
        END IF;

        NEW.merged_at := COALESCE(NEW.merged_at, clock_timestamp());
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_enforce_merged_state
BEFORE UPDATE OF state ON pull_request
FOR EACH ROW
EXECUTE FUNCTION enforce_merged_state();

-- Functions are stored in PostgreSQL as executable policy values in the
-- database catalog. This function is a stable governance predicate over
-- relational policy data.
CREATE OR REPLACE FUNCTION required_reviews_satisfied(
    p_pull_request_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT
        COUNT(DISTINCT r.reviewer) >= COALESCE(bp.required_reviews, 0)
    FROM pull_request pr
    JOIN branch_protection bp
        ON bp.branch_id = pr.target_branch_id
    LEFT JOIN review r
        ON r.pull_request_id = pr.pull_request_id
       AND r.state = 'approved'
    WHERE pr.pull_request_id = p_pull_request_id
    GROUP BY bp.required_reviews;
$$;

CREATE OR REPLACE FUNCTION status_checks_satisfied(
    p_pull_request_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT NOT EXISTS (
        SELECT 1
        FROM branch_protection bp
        JOIN protected_status_check required
            ON required.protection_id = bp.protection_id
        JOIN pull_request pr
            ON pr.target_branch_id = bp.branch_id
        LEFT JOIN status_check actual
            ON actual.pull_request_id = pr.pull_request_id
           AND actual.check_name = required.check_name
        WHERE pr.pull_request_id = p_pull_request_id
          AND COALESCE(actual.passed, FALSE) = FALSE
    );
$$;

CREATE OR REPLACE FUNCTION conversations_satisfied(
    p_pull_request_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT
        NOT bp.require_conversation_resolution
        OR pr.open_conversations = 0
    FROM pull_request pr
    JOIN branch_protection bp
        ON bp.branch_id = pr.target_branch_id
    WHERE pr.pull_request_id = p_pull_request_id;
$$;

CREATE OR REPLACE FUNCTION no_requested_changes(
    p_pull_request_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT NOT EXISTS (
        SELECT 1
        FROM review
        WHERE pull_request_id = p_pull_request_id
          AND state = 'changes_requested'
    );
$$;

CREATE OR REPLACE FUNCTION pull_request_merge_eligible(
    p_pull_request_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_result BOOLEAN;
BEGIN
    SELECT
        pr.state = 'open'
        AND NOT pr.draft
        AND pr.mergeable
        AND pr.synchronized_with_base
        AND required_reviews_satisfied(pr.pull_request_id)
        AND status_checks_satisfied(pr.pull_request_id)
        AND conversations_satisfied(pr.pull_request_id)
        AND no_requested_changes(pr.pull_request_id)
    INTO v_result
    FROM pull_request pr
    WHERE pr.pull_request_id = p_pull_request_id;

    RETURN COALESCE(v_result, FALSE);
END;
$$;

-- This view exposes each policy function as data-like evaluation output.
CREATE VIEW pull_request_governance AS
SELECT
    pr.pull_request_id,
    pr.repository_id,
    pr.number,
    pr.source_branch_id,
    pr.target_branch_id,
    pr.state,
    pr.draft,
    pr.mergeable,
    pr.synchronized_with_base,
    required_reviews_satisfied(pr.pull_request_id)
        AS approvals_satisfied,
    status_checks_satisfied(pr.pull_request_id)
        AS status_checks_satisfied,
    conversations_satisfied(pr.pull_request_id)
        AS conversations_satisfied,
    no_requested_changes(pr.pull_request_id)
        AS no_requested_changes,
    pull_request_merge_eligible(pr.pull_request_id)
        AS merge_eligible
FROM pull_request pr;

-- Sample repository and actors.
INSERT INTO repository (name, default_branch)
VALUES ('payments-platform', 'main');

INSERT INTO repository_member (
    repository_id,
    username,
    is_administrator
)
SELECT repository_id, username, administrator
FROM (
    VALUES
        (1, 'alice', FALSE),
        (1, 'bob', FALSE),
        (1, 'carol', FALSE),
        (1, 'admin', TRUE)
) AS members(repository_id, username, administrator);

INSERT INTO branch (
    repository_id,
    branch_name
)
VALUES
    (1, 'main'),
    (1, 'feature/payment-validation'),
    (1, 'feature/reporting');

INSERT INTO branch_protection (
    branch_id,
    required_reviews,
    require_conversation_resolution,
    require_linear_history,
    allow_direct_push,
    allow_force_push,
    allow_deletion,
    allow_admin_bypass
)
SELECT
    branch_id,
    2,
    TRUE,
    TRUE,
    FALSE,
    FALSE,
    FALSE,
    FALSE
FROM branch
WHERE repository_id = 1
  AND branch_name = 'main';

INSERT INTO protected_status_check (
    protection_id,
    check_name
)
SELECT protection_id, 'unit-tests'
FROM branch_protection
WHERE protection_id = 1;

INSERT INTO protected_status_check (
    protection_id,
    check_name
)
SELECT protection_id, 'security-scan'
FROM branch_protection
WHERE protection_id = 1;

-- Commits represent the Pull Request changeset independently of review.
INSERT INTO commit (
    repository_id,
    sha,
    message,
    author
)
VALUES
(
    1,
    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'Implement payment validation',
    'alice'
),
(
    1,
    'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
    'Add validation tests',
    'alice'
),
(
    1,
    'cccccccccccccccccccccccccccccccccccccccc',
    'Add reporting endpoint',
    'dave'
);

INSERT INTO pull_request (
    repository_id,
    number,
    source_branch_id,
    target_branch_id,
    title,
    state,
    draft,
    mergeable,
    synchronized_with_base,
    open_conversations,
    created_by
)
VALUES
(
    1,
    101,
    (SELECT branch_id FROM branch
     WHERE branch_name = 'feature/payment-validation'),
    (SELECT branch_id FROM branch
     WHERE branch_name = 'main'),
    'Validate payment requests',
    'open',
    FALSE,
    TRUE,
    TRUE,
    0,
    'alice'
),
(
    1,
    102,
    (SELECT branch_id FROM branch
     WHERE branch_name = 'feature/reporting'),
    (SELECT branch_id FROM branch
     WHERE branch_name = 'main'),
    'Add reporting endpoint',
    'open',
    FALSE,
    TRUE,
    TRUE,
    0,
    'dave'
);

INSERT INTO pull_request_commit (
    pull_request_id,
    commit_id,
    position
)
SELECT 101, commit_id, position
FROM (
    VALUES
        (
            (SELECT commit_id FROM commit
             WHERE sha = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'),
            1
        ),
        (
            (SELECT commit_id FROM commit
             WHERE sha = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'),
            2
        )
) AS commits(commit_id, position);

INSERT INTO pull_request_commit (
    pull_request_id,
    commit_id,
    position
)
SELECT
    102,
    commit_id,
    1
FROM commit
WHERE sha = 'cccccccccccccccccccccccccccccccccccccccc';

-- Review decisions are distinct from Pull Request mechanics.
INSERT INTO review (
    pull_request_id,
    reviewer,
    state
)
VALUES
    (101, 'bob', 'approved'),
    (101, 'carol', 'approved'),
    (102, 'bob', 'approved');

INSERT INTO review_comment (
    review_id,
    commit_id,
    file_path,
    line_number,
    body,
    resolved
)
VALUES
(
    1,
    (SELECT commit_id FROM commit
     WHERE sha = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'),
    'src/payment.py',
    42,
    'Validate the currency before calculating the total.',
    TRUE
),
(
    2,
    (SELECT commit_id FROM commit
     WHERE sha = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'),
    'tests/test_payment.py',
    18,
    'Add a boundary case for zero-value payments.',
    TRUE
);

INSERT INTO status_check (
    pull_request_id,
    check_name,
    passed
)
VALUES
    (101, 'unit-tests', TRUE),
    (101, 'security-scan', TRUE),
    (102, 'unit-tests', TRUE),
    (102, 'security-scan', TRUE);

INSERT INTO review_request (
    pull_request_id,
    reviewer
)
VALUES
    (101, 'bob'),
    (101, 'carol'),
    (102, 'carol');

-- Pull Request 101 is merge-eligible.
SELECT
    number,
    approvals_satisfied,
    status_checks_satisfied,
    conversations_satisfied,
    no_requested_changes,
    merge_eligible
FROM pull_request_governance
WHERE number = 101;

-- Pull Request 102 has only one distinct approval.
SELECT
    number,
    approvals_satisfied,
    merge_eligible
FROM pull_request_governance
WHERE number = 102;

-- CTE showing review workload separately from approval semantics.
WITH review_metrics AS (
    SELECT
        pr.pull_request_id,
        pr.number,
        COUNT(r.review_id) AS total_reviews,
        COUNT(*) FILTER (
            WHERE r.state = 'approved'
        ) AS approvals,
        COUNT(*) FILTER (
            WHERE r.state = 'changes_requested'
        ) AS change_requests,
        COUNT(DISTINCT r.reviewer) FILTER (
            WHERE r.state = 'approved'
        ) AS distinct_approvers
    FROM pull_request pr
    LEFT JOIN review r
        ON r.pull_request_id = pr.pull_request_id
    GROUP BY pr.pull_request_id, pr.number
)
SELECT *
FROM review_metrics
ORDER BY number;

-- Review comments expose unresolved discussion state without changing the
-- approval calculation itself.
SELECT
    pr.number,
    COUNT(rc.comment_id) AS comments,
    COUNT(*) FILTER (
        WHERE rc.resolved = FALSE
    ) AS unresolved_comments
FROM pull_request pr
LEFT JOIN review r
    ON r.pull_request_id = pr.pull_request_id
LEFT JOIN review_comment rc
    ON rc.review_id = r.review_id
GROUP BY pr.number
ORDER BY pr.number;

-- Transactional merge workflow. The merge event is inserted first because
-- the trigger requires an event before a Pull Request can enter merged state.
BEGIN;

SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

SELECT pull_request_id
FROM pull_request
WHERE pull_request_id = 101
FOR UPDATE;

DO $$
BEGIN
    IF NOT pull_request_merge_eligible(101) THEN
        RAISE EXCEPTION
            'Pull Request 101 is not merge-eligible';
    END IF;
END;
$$;

INSERT INTO merge_event (
    pull_request_id,
    strategy,
    merged_by
)
VALUES (
    101,
    'squash',
    'admin'
);

UPDATE pull_request
SET
    state = 'merged',
    closed_at = clock_timestamp(),
    merged_at = clock_timestamp()
WHERE pull_request_id = 101;

COMMIT;

-- The merged Pull Request now fails the normal open-state eligibility rule.
SELECT
    number,
    state,
    merge_eligible
FROM pull_request_governance
WHERE number = 101;

-- Failure scenario: a requested-change review blocks merging even when
-- status checks and approval counts otherwise look healthy.
INSERT INTO review (
    pull_request_id,
    reviewer,
    state
)
VALUES
    (102, 'carol', 'changes_requested');

SELECT
    number,
    approvals_satisfied,
    no_requested_changes,
    merge_eligible
FROM pull_request_governance
WHERE number = 102;

-- Base-branch synchronization is a separate merge condition.
UPDATE pull_request
SET synchronized_with_base = FALSE
WHERE number = 102;

SELECT
    number,
    synchronized_with_base,
    merge_eligible
FROM pull_request_governance
WHERE number = 102;

-- Functions as data are visible here as named PostgreSQL routines. The
-- application can select a policy function by name from a trusted registry,
-- while executable code remains controlled by the database definition.
SELECT
    routine_schema,
    routine_name,
    routine_type
FROM information_schema.routines
WHERE routine_schema = 'functions_as_data_governance'
  AND routine_name IN (
      'required_reviews_satisfied',
      'status_checks_satisfied',
      'conversations_satisfied',
      'no_requested_changes',
      'pull_request_merge_eligible'
  )
ORDER BY routine_name;
