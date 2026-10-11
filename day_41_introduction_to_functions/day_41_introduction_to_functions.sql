-- Introduction to Functions: PostgreSQL relational model for repository governance.
-- The database separates request lifecycle, review decisions, approvals,
-- status checks, and branch-protection enforcement.

BEGIN;

DROP SCHEMA IF EXISTS function_learning CASCADE;
CREATE SCHEMA function_learning;
SET search_path TO function_learning, public;

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(repository_name)) > 0),
    CHECK (length(trim(default_branch)) > 0)
);

CREATE TABLE repository_members (
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id),
    username TEXT NOT NULL,
    member_role TEXT NOT NULL CHECK (
        member_role IN ('author', 'reviewer', 'maintainer', 'administrator', 'bot')
    ),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (repository_id, username),
    CHECK (length(trim(username)) > 0)
);

CREATE TABLE branches (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id),
    branch_name TEXT NOT NULL,
    head_sha TEXT,
    protected BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    UNIQUE (repository_id, branch_name),
    CHECK (length(trim(branch_name)) > 0),
    CHECK (head_sha IS NULL OR head_sha ~ '^[0-9a-fA-F]{7,40}$')
);

CREATE TABLE pull_requests (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id),
    author TEXT NOT NULL,
    source_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT 'draft' CHECK (
        state IN ('draft', 'open', 'closed', 'merged')
    ),
    base_synchronized BOOLEAN NOT NULL DEFAULT FALSE,
    has_conflicts BOOLEAN NOT NULL DEFAULT FALSE,
    linear_history_available BOOLEAN NOT NULL DEFAULT TRUE,
    unresolved_conversations INTEGER NOT NULL DEFAULT 0 CHECK (
        unresolved_conversations >= 0
    ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    merged_at TIMESTAMPTZ,
    CHECK (source_branch_id <> target_branch_id),
    CHECK (length(trim(title)) > 0),
    CHECK ((state = 'merged') = (merged_at IS NOT NULL))
);

CREATE TABLE commits (
    commit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    sha TEXT NOT NULL CHECK (sha ~ '^[0-9a-fA-F]{7,40}$'),
    message TEXT NOT NULL CHECK (length(trim(message)) > 0),
    committed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (pull_request_id, sha)
);

CREATE TABLE reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    reviewer TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (
        decision IN ('approved', 'changes_requested', 'commented')
    ),
    reviewed_commit_sha TEXT NOT NULL CHECK (
        reviewed_commit_sha ~ '^[0-9a-fA-F]{7,40}$'
    ),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dismissed_at TIMESTAMPTZ,
    dismissal_reason TEXT,
    CHECK (
        (dismissed_at IS NULL AND dismissal_reason IS NULL)
        OR
        (dismissed_at IS NOT NULL AND length(trim(dismissal_reason)) > 0)
    )
);

CREATE TABLE review_comments (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES reviews(review_id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER CHECK (line_number IS NULL OR line_number > 0),
    comment_body TEXT NOT NULL CHECK (length(trim(comment_body)) > 0),
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(file_path)) > 0)
);

CREATE TABLE status_checks (
    status_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    head_sha TEXT NOT NULL CHECK (head_sha ~ '^[0-9a-fA-F]{7,40}$'),
    status TEXT NOT NULL CHECK (status IN ('pending', 'success', 'failure')),
    completed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, check_name, head_sha),
    CHECK (
        (status = 'pending' AND completed_at IS NULL)
        OR
        (status IN ('success', 'failure') AND completed_at IS NOT NULL)
    ),
    CHECK (length(trim(check_name)) > 0)
);

CREATE TABLE branch_protection_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE REFERENCES branches(branch_id),
    required_approvals INTEGER NOT NULL DEFAULT 1 CHECK (required_approvals >= 1),
    require_code_owner_review BOOLEAN NOT NULL DEFAULT FALSE,
    require_conversation_resolution BOOLEAN NOT NULL DEFAULT TRUE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    restrict_direct_push BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_force_push BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_deletion BOOLEAN NOT NULL DEFAULT TRUE,
    enforce_for_administrators BOOLEAN NOT NULL DEFAULT TRUE,
    allow_bypass BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (NOT (enforce_for_administrators AND allow_bypass))
);

CREATE TABLE required_status_checks (
    policy_id BIGINT NOT NULL REFERENCES branch_protection_policies(policy_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    PRIMARY KEY (policy_id, check_name),
    CHECK (length(trim(check_name)) > 0)
);

CREATE INDEX idx_pull_requests_repository_state
    ON pull_requests(repository_id, state);

CREATE INDEX idx_commits_request_time
    ON commits(pull_request_id, committed_at DESC);

CREATE INDEX idx_reviews_request_reviewer_time
    ON reviews(pull_request_id, reviewer, submitted_at DESC);

CREATE INDEX idx_comments_unresolved
    ON review_comments(review_id)
    WHERE is_resolved = FALSE;

CREATE INDEX idx_status_checks_current_head
    ON status_checks(pull_request_id, check_name, head_sha, status);

-- Reject cross-repository branch pairs and authors who are not active members.
CREATE FUNCTION validate_pull_request_membership()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    source_repository BIGINT;
    target_repository BIGINT;
BEGIN
    SELECT repository_id INTO source_repository
    FROM branches WHERE branch_id = NEW.source_branch_id;

    SELECT repository_id INTO target_repository
    FROM branches WHERE branch_id = NEW.target_branch_id;

    IF source_repository IS NULL OR target_repository IS NULL THEN
        RAISE EXCEPTION 'Source and target branches must exist';
    END IF;

    IF source_repository <> NEW.repository_id
       OR target_repository <> NEW.repository_id THEN
        RAISE EXCEPTION 'Both branches must belong to the request repository';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM repository_members
        WHERE repository_id = NEW.repository_id
          AND username = NEW.author
          AND active = TRUE
    ) THEN
        RAISE EXCEPTION 'Pull request author must be an active repository member';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_pull_request_membership
BEFORE INSERT OR UPDATE OF repository_id, author, source_branch_id, target_branch_id
ON pull_requests
FOR EACH ROW
EXECUTE FUNCTION validate_pull_request_membership();

-- Reviewers must be active, eligible repository members and cannot approve
-- their own change. Review rows are retained to preserve the audit trail.
CREATE FUNCTION validate_review_submission()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    request_author TEXT;
    request_state TEXT;
    request_repository BIGINT;
    commit_exists BOOLEAN;
BEGIN
    SELECT author, state, repository_id
    INTO request_author, request_state, request_repository
    FROM pull_requests
    WHERE pull_request_id = NEW.pull_request_id;

    IF request_author IS NULL THEN
        RAISE EXCEPTION 'Pull request does not exist';
    END IF;

    IF request_state <> 'open' THEN
        RAISE EXCEPTION 'Reviews can be submitted only for open requests';
    END IF;

    IF NEW.reviewer = request_author THEN
        RAISE EXCEPTION 'Authors cannot review their own pull requests';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM repository_members
        WHERE repository_id = request_repository
          AND username = NEW.reviewer
          AND active = TRUE
          AND member_role IN ('reviewer', 'maintainer', 'administrator')
    ) THEN
        RAISE EXCEPTION 'Reviewer is not eligible or active';
    END IF;

    SELECT EXISTS (
        SELECT 1 FROM commits
        WHERE pull_request_id = NEW.pull_request_id
          AND lower(sha) = lower(NEW.reviewed_commit_sha)
    ) INTO commit_exists;

    IF NOT commit_exists THEN
        RAISE EXCEPTION 'Review must reference a commit in the request';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_review_submission
BEFORE INSERT ON reviews
FOR EACH ROW
EXECUTE FUNCTION validate_review_submission();

-- Merge eligibility is calculated from the current request head, the latest
-- non-dismissed decision per reviewer, current status checks, and branch policy.
CREATE FUNCTION evaluate_merge_eligibility(request_id BIGINT)
RETURNS TABLE (
    eligible BOOLEAN,
    blocker TEXT
)
LANGUAGE sql
STABLE
AS $$
    WITH request_context AS (
        SELECT
            pr.pull_request_id,
            pr.repository_id,
            pr.author,
            pr.state,
            pr.base_synchronized,
            pr.has_conflicts,
            pr.linear_history_available,
            pr.unresolved_conversations,
            pr.source_branch_id,
            pr.target_branch_id,
            (
                SELECT c.sha
                FROM commits c
                WHERE c.pull_request_id = pr.pull_request_id
                ORDER BY c.committed_at DESC, c.commit_id DESC
                LIMIT 1
            ) AS head_sha
        FROM pull_requests pr
        WHERE pr.pull_request_id = request_id
    ),
    policy_context AS (
        SELECT
            rc.*,
            bp.required_approvals,
            bp.require_conversation_resolution,
            bp.require_linear_history,
            bp.allow_bypass,
            bp.enforce_for_administrators
        FROM request_context rc
        JOIN branches target ON target.branch_id = rc.target_branch_id
        LEFT JOIN branch_protection_policies bp
            ON bp.branch_id = target.branch_id
    ),
    latest_reviews AS (
        SELECT DISTINCT ON (r.reviewer)
            r.reviewer,
            r.decision,
            r.reviewed_commit_sha,
            r.pull_request_id
        FROM reviews r
        WHERE r.pull_request_id = request_id
          AND r.dismissed_at IS NULL
        ORDER BY r.reviewer, r.submitted_at DESC, r.review_id DESC
    ),
    approval_count AS (
        SELECT COUNT(*) AS approvals
        FROM latest_reviews lr
        JOIN policy_context pc ON pc.pull_request_id = lr.pull_request_id
        JOIN repository_members rm
          ON rm.repository_id = pc.repository_id
         AND rm.username = lr.reviewer
         AND rm.active = TRUE
         AND rm.member_role IN ('reviewer', 'maintainer', 'administrator')
        WHERE lr.decision = 'approved'
          AND lower(lr.reviewed_commit_sha) = lower(pc.head_sha)
          AND lr.reviewer <> pc.author
    ),
    check_failures AS (
        SELECT rsc.check_name
        FROM policy_context pc
        JOIN branch_protection_policies bp
          ON bp.branch_id = pc.target_branch_id
        JOIN required_status_checks rsc ON rsc.policy_id = bp.policy_id
        LEFT JOIN status_checks sc
          ON sc.pull_request_id = pc.pull_request_id
         AND sc.check_name = rsc.check_name
         AND lower(sc.head_sha) = lower(pc.head_sha)
        WHERE sc.status IS DISTINCT FROM 'success'
    ),
    blockers AS (
        SELECT 'Request is not open' AS reason
        FROM policy_context WHERE state <> 'open'

        UNION ALL
        SELECT 'Request has no commits'
        FROM policy_context WHERE head_sha IS NULL

        UNION ALL
        SELECT 'Source branch is not synchronized with base'
        FROM policy_context WHERE NOT base_synchronized

        UNION ALL
        SELECT 'Source branch has merge conflicts'
        FROM policy_context WHERE has_conflicts

        UNION ALL
        SELECT 'Linear history is required'
        FROM policy_context
        WHERE require_linear_history AND NOT linear_history_available

        UNION ALL
        SELECT 'Review conversations remain unresolved'
        FROM policy_context
        WHERE require_conversation_resolution AND unresolved_conversations > 0

        UNION ALL
        SELECT 'Insufficient eligible current approvals'
        FROM policy_context pc
        CROSS JOIN approval_count ac
        WHERE ac.approvals < COALESCE(pc.required_approvals, 1)

        UNION ALL
        SELECT 'A current review requests changes'
        FROM latest_reviews lr
        JOIN policy_context pc ON pc.pull_request_id = lr.pull_request_id
        WHERE lr.decision = 'changes_requested'
          AND lower(lr.reviewed_commit_sha) = lower(pc.head_sha)

        UNION ALL
        SELECT 'Required status check is not successful: ' || cf.check_name
        FROM check_failures cf
    )
    SELECT NOT EXISTS (SELECT 1 FROM blockers) AS eligible, reason AS blocker
    FROM blockers

    UNION ALL

    SELECT TRUE, NULL::TEXT
    WHERE NOT EXISTS (SELECT 1 FROM blockers);
$$;

-- Sample repository and governance actors.
INSERT INTO repositories (repository_name, default_branch)
VALUES ('payment-platform', 'main');

INSERT INTO repository_members (repository_id, username, member_role)
SELECT repository_id, username, member_role
FROM repositories
CROSS JOIN (
    VALUES
        ('developer', 'author'),
        ('alex', 'reviewer'),
        ('priya', 'reviewer'),
        ('sam', 'maintainer'),
        ('release-admin', 'administrator')
) AS members(username, member_role)
WHERE repository_name = 'payment-platform';

INSERT INTO branches (repository_id, branch_name, head_sha, protected)
SELECT repository_id, branch_name, head_sha, protected
FROM repositories
CROSS JOIN (
    VALUES
        ('main', 'aaaaaaa', TRUE),
        ('feature/payment-validation', 'bbbbbbb', FALSE),
        ('feature/audit-logging', 'ccccccc', FALSE)
) AS branch_data(branch_name, head_sha, protected)
WHERE repository_name = 'payment-platform';

INSERT INTO branch_protection_policies (
    branch_id,
    required_approvals,
    require_conversation_resolution,
    require_linear_history,
    restrict_direct_push,
    prohibit_force_push,
    prohibit_deletion,
    enforce_for_administrators
)
SELECT branch_id, 2, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE
FROM branches
WHERE branch_name = 'main';

INSERT INTO required_status_checks (policy_id, check_name)
SELECT policy_id, check_name
FROM branch_protection_policies
CROSS JOIN (VALUES ('unit-tests'), ('security-scan')) AS checks(check_name);

INSERT INTO pull_requests (
    repository_id, author, source_branch_id, target_branch_id,
    title, description, state, base_synchronized,
    has_conflicts, linear_history_available, unresolved_conversations
)
SELECT
    repo.repository_id,
    'developer',
    source.branch_id,
    target.branch_id,
    'Validate payment boundaries',
    'Reject invalid amounts before processing a payment.',
    'open',
    TRUE,
    FALSE,
    TRUE,
    0
FROM repositories repo
JOIN branches source
  ON source.repository_id = repo.repository_id
 AND source.branch_name = 'feature/payment-validation'
JOIN branches target
  ON target.repository_id = repo.repository_id
 AND target.branch_name = 'main'
WHERE repo.repository_name = 'payment-platform';

INSERT INTO commits (pull_request_id, sha, message)
SELECT pull_request_id, 'd111111', 'Validate payment amount boundaries'
FROM pull_requests
WHERE title = 'Validate payment boundaries';

INSERT INTO reviews (
    pull_request_id, reviewer, decision, reviewed_commit_sha
)
SELECT pr.pull_request_id, review_data.reviewer,
       review_data.decision, 'd111111'
FROM pull_requests pr
CROSS JOIN (
    VALUES
        ('alex', 'approved'),
        ('priya', 'approved')
) AS review_data(reviewer, decision)
WHERE pr.title = 'Validate payment boundaries';

INSERT INTO review_comments (
    review_id, file_path, line_number, comment_body, is_resolved
)
SELECT review_id, 'payments/validator.py', 42,
       'Boundary behavior is covered by the updated tests.', TRUE
FROM reviews
WHERE reviewer = 'alex'
  AND pull_request_id = (
      SELECT pull_request_id
      FROM pull_requests
      WHERE title = 'Validate payment boundaries'
  );

INSERT INTO status_checks (
    pull_request_id, check_name, head_sha, status, completed_at
)
SELECT pr.pull_request_id, checks.check_name, 'd111111',
       checks.status,
       CASE WHEN checks.status = 'pending' THEN NULL ELSE CURRENT_TIMESTAMP END
FROM pull_requests pr
CROSS JOIN (
    VALUES
        ('unit-tests', 'success'),
        ('security-scan', 'pending')
) AS checks(check_name, status)
WHERE pr.title = 'Validate payment boundaries';

-- This view exposes each required condition as a merge-evaluation result.
CREATE VIEW merge_eligibility AS
SELECT
    pr.pull_request_id,
    pr.title,
    pr.state,
    evaluation.eligible,
    evaluation.blocker
FROM pull_requests pr
CROSS JOIN LATERAL evaluate_merge_eligibility(pr.pull_request_id) evaluation;

-- Inspect blockers. The pending security scan prevents merging.
SELECT * FROM merge_eligibility ORDER BY pull_request_id;

-- Complete the pending check against the current head.
UPDATE status_checks
SET status = 'success',
    completed_at = CURRENT_TIMESTAMP
WHERE check_name = 'security-scan'
  AND pull_request_id = (
      SELECT pull_request_id FROM pull_requests
      WHERE title = 'Validate payment boundaries'
  );

SELECT * FROM merge_eligibility ORDER BY pull_request_id;

-- A merge transition is allowed only when the evaluation reports eligibility.
DO $$
DECLARE
    target_request BIGINT;
    allowed BOOLEAN;
BEGIN
    SELECT pull_request_id INTO target_request
    FROM pull_requests
    WHERE title = 'Validate payment boundaries';

    SELECT e.eligible INTO allowed
    FROM evaluate_merge_eligibility(target_request) e
    LIMIT 1;

    IF NOT COALESCE(allowed, FALSE) THEN
        RAISE EXCEPTION 'Merge rejected by repository policy';
    END IF;

    UPDATE pull_requests
    SET state = 'merged', merged_at = CURRENT_TIMESTAMP
    WHERE pull_request_id = target_request;
END;
$$;

SELECT pull_request_id, title, state, merged_at
FROM pull_requests
ORDER BY pull_request_id;

-- A database CHECK constraint prevents negative unresolved conversation counts.
-- Run this statement separately to observe the constraint failure:
-- UPDATE pull_requests SET unresolved_conversations = -1 WHERE pull_request_id = 1;

COMMIT;
