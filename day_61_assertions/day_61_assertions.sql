-- Assertions: PostgreSQL implementation.
-- The database uses CHECK constraints and triggers for durable data rules,
-- while assertion-style functions expose explicit validation behavior.
--
-- PostgreSQL does not implement the SQL-standard CREATE ASSERTION feature,
-- so cross-row invariants are represented with functions and triggers.

DROP SCHEMA IF EXISTS assertion_lab CASCADE;
CREATE SCHEMA assertion_lab;

SET search_path = assertion_lab, public;

CREATE TYPE repository_status AS ENUM ('ACTIVE', 'ARCHIVED');
CREATE TYPE pull_request_state AS ENUM ('DRAFT', 'OPEN', 'MERGED', 'CLOSED');
CREATE TYPE review_state AS ENUM ('PENDING', 'APPROVED', 'CHANGES_REQUESTED', 'COMMENTED');

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main',
    status repository_status NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT repository_name_nonempty
        CHECK (length(trim(name)) > 0),
    CONSTRAINT repository_branch_nonempty
        CHECK (length(trim(default_branch)) > 0)
);

CREATE TABLE branches (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    protected BOOLEAN NOT NULL DEFAULT FALSE,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT branch_name_nonempty
        CHECK (length(trim(branch_name)) > 0),
    CONSTRAINT unique_repository_branch
        UNIQUE (repository_id, branch_name)
);

CREATE TABLE commits (
    commit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    commit_hash TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT commit_hash_nonempty
        CHECK (length(trim(commit_hash)) > 0),
    CONSTRAINT commit_message_nonempty
        CHECK (length(trim(message)) > 0),
    CONSTRAINT unique_repository_commit
        UNIQUE (repository_id, commit_hash)
);

CREATE TABLE pull_requests (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    number INTEGER NOT NULL,
    source_branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id),
    state pull_request_state NOT NULL DEFAULT 'DRAFT',
    draft BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    merged_at TIMESTAMPTZ,
    CONSTRAINT positive_pr_number CHECK (number > 0),
    CONSTRAINT unique_repository_pr_number UNIQUE (repository_id, number),
    CONSTRAINT different_pr_branches
        CHECK (source_branch_id <> target_branch_id),
    CONSTRAINT merged_timestamp_consistency CHECK (
        (state = 'MERGED' AND merged_at IS NOT NULL)
        OR
        (state <> 'MERGED' AND merged_at IS NULL)
    ),
    CONSTRAINT merged_pr_not_draft CHECK (
        state <> 'MERGED' OR draft = FALSE
    )
);

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id) ON DELETE RESTRICT,
    PRIMARY KEY (pull_request_id, commit_id)
);

CREATE TABLE reviewers (
    reviewer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT reviewer_username_nonempty
        CHECK (length(trim(username)) > 0)
);

CREATE TABLE reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL
        REFERENCES reviewers(reviewer_id),
    state review_state NOT NULL,
    commit_id BIGINT
        REFERENCES commits(commit_id),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE review_comments (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL
        REFERENCES reviews(review_id) ON DELETE CASCADE,
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT comment_body_nonempty
        CHECK (length(trim(body)) > 0)
);

CREATE TABLE status_checks (
    status_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    completed_at TIMESTAMPTZ,
    CONSTRAINT unique_pr_status_check
        UNIQUE (pull_request_id, check_name)
);

CREATE TABLE branch_protection_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE
        REFERENCES branches(branch_id) ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 1,
    require_status_checks BOOLEAN NOT NULL DEFAULT TRUE,
    require_conversations_resolved BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_direct_push BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_force_push BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_branch_deletion BOOLEAN NOT NULL DEFAULT TRUE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT nonnegative_required_approvals
        CHECK (required_approvals >= 0)
);

CREATE INDEX idx_pr_repository_state
    ON pull_requests(repository_id, state);

CREATE INDEX idx_reviews_pr_state
    ON reviews(pull_request_id, state);

CREATE INDEX idx_comments_review_unresolved
    ON review_comments(review_id)
    WHERE resolved = FALSE;

CREATE INDEX idx_status_checks_pr_failed
    ON status_checks(pull_request_id)
    WHERE passed = FALSE;

CREATE OR REPLACE FUNCTION assert_pull_request_commit_repository()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    pr_repository BIGINT;
    commit_repository BIGINT;
BEGIN
    SELECT repository_id
    INTO pr_repository
    FROM pull_requests
    WHERE pull_request_id = NEW.pull_request_id;

    SELECT repository_id
    INTO commit_repository
    FROM commits
    WHERE commit_id = NEW.commit_id;

    IF pr_repository IS NULL OR commit_repository IS NULL THEN
        RAISE EXCEPTION 'PR and commit must reference existing repositories';
    END IF;

    IF pr_repository <> commit_repository THEN
        RAISE EXCEPTION
            'commit % belongs to repository %, but PR % belongs to repository %',
            NEW.commit_id,
            commit_repository,
            NEW.pull_request_id,
            pr_repository;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_assert_pr_commit_repository
BEFORE INSERT OR UPDATE ON pull_request_commits
FOR EACH ROW
EXECUTE FUNCTION assert_pull_request_commit_repository();

CREATE OR REPLACE FUNCTION assert_pr_branch_repository()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    pr_repository BIGINT;
    source_repository BIGINT;
    target_repository BIGINT;
BEGIN
    SELECT repository_id
    INTO pr_repository
    FROM pull_requests
    WHERE pull_request_id = NEW.pull_request_id;

    SELECT repository_id
    INTO source_repository
    FROM branches
    WHERE branch_id = (
        SELECT source_branch_id
        FROM pull_requests
        WHERE pull_request_id = NEW.pull_request_id
    );

    SELECT repository_id
    INTO target_repository
    FROM branches
    WHERE branch_id = (
        SELECT target_branch_id
        FROM pull_requests
        WHERE pull_request_id = NEW.pull_request_id
    );

    IF pr_repository <> source_repository
       OR pr_repository <> target_repository THEN
        RAISE EXCEPTION 'PR branches must belong to the same repository as the PR';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_assert_pr_branch_repository
AFTER INSERT OR UPDATE ON pull_requests
FOR EACH ROW
EXECUTE FUNCTION assert_pr_branch_repository();

CREATE OR REPLACE FUNCTION merge_pull_request(
    p_pull_request_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    pr_state pull_request_state;
    pr_draft BOOLEAN;
    required_approvals INTEGER;
    approval_count INTEGER;
    unresolved_count INTEGER;
    failed_checks INTEGER;
    commit_count INTEGER;
BEGIN
    SELECT
        pr.state,
        pr.draft,
        COALESCE(policy.required_approvals, 0)
    INTO
        pr_state,
        pr_draft,
        required_approvals
    FROM pull_requests pr
    JOIN branches target_branch
      ON target_branch.branch_id = pr.target_branch_id
    LEFT JOIN branch_protection_policies policy
      ON policy.branch_id = target_branch.branch_id
    WHERE pr.pull_request_id = p_pull_request_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'pull request % does not exist', p_pull_request_id;
    END IF;

    IF pr_state <> 'OPEN' OR pr_draft THEN
        RAISE EXCEPTION 'pull request must be open and non-draft';
    END IF;

    SELECT count(*)
    INTO commit_count
    FROM pull_request_commits
    WHERE pull_request_id = p_pull_request_id;

    IF commit_count = 0 THEN
        RAISE EXCEPTION 'pull request must contain at least one commit';
    END IF;

    SELECT count(DISTINCT reviewer_id)
    INTO approval_count
    FROM reviews
    WHERE pull_request_id = p_pull_request_id
      AND state = 'APPROVED';

    IF approval_count < required_approvals THEN
        RAISE EXCEPTION
            'approval requirement not met: % of %',
            approval_count,
            required_approvals;
    END IF;

    SELECT count(*)
    INTO unresolved_count
    FROM review_comments rc
    JOIN reviews r ON r.review_id = rc.review_id
    WHERE r.pull_request_id = p_pull_request_id
      AND rc.resolved = FALSE;

    IF unresolved_count > 0 THEN
        RAISE EXCEPTION 'unresolved review conversations remain';
    END IF;

    SELECT count(*)
    INTO failed_checks
    FROM status_checks
    WHERE pull_request_id = p_pull_request_id
      AND passed = FALSE;

    IF failed_checks > 0 THEN
        RAISE EXCEPTION 'required status checks are failing';
    END IF;

    UPDATE pull_requests
    SET state = 'MERGED',
        draft = FALSE,
        merged_at = CURRENT_TIMESTAMP
    WHERE pull_request_id = p_pull_request_id;

    RETURN TRUE;
END;
$$;

INSERT INTO repositories (name, default_branch)
VALUES ('assertion-lab', 'main');

INSERT INTO branches (repository_id, branch_name, protected)
SELECT repository_id, 'main', TRUE
FROM repositories
WHERE name = 'assertion-lab';

INSERT INTO branches (repository_id, branch_name)
SELECT repository_id, 'feature/assertions'
FROM repositories
WHERE name = 'assertion-lab';

INSERT INTO commits (repository_id, commit_hash, message)
SELECT repository_id, 'a1', 'Add assertion domain model'
FROM repositories
WHERE name = 'assertion-lab';

INSERT INTO commits (repository_id, commit_hash, message)
SELECT repository_id, 'a2', 'Add merge validation'
FROM repositories
WHERE name = 'assertion-lab';

INSERT INTO reviewers (username)
VALUES ('reviewer_a'), ('reviewer_b');

INSERT INTO branch_protection_policies (
    branch_id,
    required_approvals,
    require_status_checks,
    require_conversations_resolved,
    restrict_direct_push,
    restrict_force_push,
    restrict_branch_deletion,
    require_linear_history
)
SELECT branch_id, 2, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE
FROM branches
WHERE branch_name = 'main';

INSERT INTO pull_requests (
    repository_id,
    number,
    source_branch_id,
    target_branch_id,
    state,
    draft
)
SELECT
    r.repository_id,
    1,
    source.branch_id,
    target.branch_id,
    'OPEN',
    FALSE
FROM repositories r
JOIN branches source
  ON source.repository_id = r.repository_id
 AND source.branch_name = 'feature/assertions'
JOIN branches target
  ON target.repository_id = r.repository_id
 AND target.branch_name = 'main'
WHERE r.name = 'assertion-lab';

INSERT INTO pull_request_commits (pull_request_id, commit_id)
SELECT pr.pull_request_id, c.commit_id
FROM pull_requests pr
JOIN commits c
  ON c.commit_hash IN ('a1', 'a2')
WHERE pr.number = 1;

INSERT INTO reviews (pull_request_id, reviewer_id, state, commit_id)
SELECT pr.pull_request_id, reviewer.reviewer_id, 'APPROVED', c.commit_id
FROM pull_requests pr
JOIN reviewers reviewer ON reviewer.username = 'reviewer_a'
JOIN commits c ON c.commit_hash = 'a2'
WHERE pr.number = 1;

INSERT INTO reviews (pull_request_id, reviewer_id, state, commit_id)
SELECT pr.pull_request_id, reviewer.reviewer_id, 'APPROVED', c.commit_id
FROM pull_requests pr
JOIN reviewers reviewer ON reviewer.username = 'reviewer_b'
JOIN commits c ON c.commit_hash = 'a2'
WHERE pr.number = 1;

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    passed,
    completed_at
)
SELECT
    pull_request_id,
    'unit-tests',
    TRUE,
    CURRENT_TIMESTAMP
FROM pull_requests
WHERE number = 1;

-- Retrieval.
SELECT
    pr.number,
    pr.state,
    source.branch_name AS source_branch,
    target.branch_name AS target_branch
FROM pull_requests pr
JOIN branches source ON source.branch_id = pr.source_branch_id
JOIN branches target ON target.branch_id = pr.target_branch_id
ORDER BY pr.number;

-- Assertion-style validation report.
WITH approval_counts AS (
    SELECT
        pull_request_id,
        count(DISTINCT reviewer_id) FILTER (
            WHERE state = 'APPROVED'
        ) AS approvals
    FROM reviews
    GROUP BY pull_request_id
),
check_counts AS (
    SELECT
        pull_request_id,
        count(*) FILTER (WHERE passed = FALSE) AS failed_checks
    FROM status_checks
    GROUP BY pull_request_id
)
SELECT
    pr.number,
    COALESCE(ac.approvals, 0) AS approvals,
    policy.required_approvals,
    COALESCE(cc.failed_checks, 0) AS failed_checks,
    CASE
        WHEN COALESCE(ac.approvals, 0) >= policy.required_approvals
         AND COALESCE(cc.failed_checks, 0) = 0
        THEN 'ELIGIBLE'
        ELSE 'BLOCKED'
    END AS merge_status
FROM pull_requests pr
JOIN branches target
  ON target.branch_id = pr.target_branch_id
JOIN branch_protection_policies policy
  ON policy.branch_id = target.branch_id
LEFT JOIN approval_counts ac
  ON ac.pull_request_id = pr.pull_request_id
LEFT JOIN check_counts cc
  ON cc.pull_request_id = pr.pull_request_id
ORDER BY pr.number;

-- Transactional workflow: merge only after all assertions pass.
BEGIN;
SELECT merge_pull_request(
    (SELECT pull_request_id FROM pull_requests WHERE number = 1)
);
COMMIT;

-- Final workflow state.
SELECT
    number,
    state,
    draft,
    merged_at
FROM pull_requests
WHERE number = 1;
