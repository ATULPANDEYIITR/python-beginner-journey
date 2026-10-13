-- Return Values: PostgreSQL implementation of repository governance.
--
-- Return values are represented through function results, returned rows,
-- composite records, SQLSTATE exceptions, and transaction outcomes.
-- This schema also demonstrates how Pull Requests, reviews, approvals,
-- status checks, and branch protection remain distinct concerns.

BEGIN;

CREATE SCHEMA IF NOT EXISTS repository_governance;
SET search_path TO repository_governance, public;

CREATE TYPE pull_request_state AS ENUM (
    'draft', 'open', 'closed', 'merged'
);

CREATE TYPE review_state AS ENUM (
    'commented', 'changes_requested', 'approved', 'dismissed'
);

CREATE TYPE check_state AS ENUM (
    'pending', 'passed', 'failed'
);

CREATE TYPE merge_strategy AS ENUM (
    'merge_commit', 'squash', 'rebase'
);

CREATE TABLE repository (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    owner_name TEXT NOT NULL,
    repository_name TEXT NOT NULL,
    default_branch TEXT NOT NULL DEFAULT 'main',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (owner_name, repository_name),
    CHECK (length(trim(owner_name)) > 0),
    CHECK (length(trim(repository_name)) > 0)
);

CREATE TABLE repository_user (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (length(trim(username)) > 0)
);

CREATE TABLE repository_branch (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id),
    branch_name TEXT NOT NULL,
    head_commit TEXT NOT NULL,
    protected BOOLEAN NOT NULL DEFAULT FALSE,
    linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    UNIQUE (repository_id, branch_name),
    CHECK (length(trim(branch_name)) > 0),
    CHECK (length(trim(head_commit)) > 0)
);

CREATE TABLE branch_protection_policy (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id),
    branch_pattern TEXT NOT NULL,
    required_approvals INTEGER NOT NULL DEFAULT 1
        CHECK (required_approvals >= 0),
    require_resolved_conversations BOOLEAN NOT NULL DEFAULT TRUE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    prohibit_direct_pushes BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_force_pushes BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_deletion BOOLEAN NOT NULL DEFAULT TRUE,
    dismiss_stale_approvals BOOLEAN NOT NULL DEFAULT TRUE,
    require_code_owner_approval BOOLEAN NOT NULL DEFAULT FALSE,
    restrict_merge_actors BOOLEAN NOT NULL DEFAULT FALSE,
    administrator_must_follow_policy BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, branch_pattern),
    CHECK (length(trim(branch_pattern)) > 0)
);

CREATE TABLE policy_required_check (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policy(policy_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    PRIMARY KEY (policy_id, check_name),
    CHECK (length(trim(check_name)) > 0)
);

CREATE TABLE policy_code_owner (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policy(policy_id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES repository_user(user_id),
    PRIMARY KEY (policy_id, user_id)
);

CREATE TABLE policy_bypass_actor (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policy(policy_id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES repository_user(user_id),
    reason TEXT NOT NULL,
    PRIMARY KEY (policy_id, user_id),
    CHECK (length(trim(reason)) > 0)
);

CREATE TABLE pull_request (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id),
    author_id BIGINT NOT NULL REFERENCES repository_user(user_id),
    source_branch_id BIGINT NOT NULL REFERENCES repository_branch(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES repository_branch(branch_id),
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    state pull_request_state NOT NULL DEFAULT 'open',
    is_draft BOOLEAN NOT NULL DEFAULT FALSE,
    source_head_commit TEXT NOT NULL,
    target_head_at_sync TEXT NOT NULL,
    base_synchronized BOOLEAN NOT NULL DEFAULT TRUE,
    merge_strategy merge_strategy,
    merged_by BIGINT REFERENCES repository_user(user_id),
    merged_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (source_branch_id <> target_branch_id),
    CHECK (length(trim(title)) > 0),
    CHECK (
        (state = 'merged' AND merged_at IS NOT NULL
            AND merged_by IS NOT NULL AND merge_strategy IS NOT NULL)
        OR
        (state <> 'merged' AND merged_at IS NULL
            AND merged_by IS NULL AND merge_strategy IS NULL)
    ),
    CHECK (NOT (is_draft AND state = 'merged'))
);

CREATE TABLE pull_request_commit (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_request(pull_request_id) ON DELETE CASCADE,
    commit_id TEXT NOT NULL,
    commit_message TEXT NOT NULL,
    ordinal INTEGER NOT NULL CHECK (ordinal >= 1),
    added_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (pull_request_id, commit_id),
    UNIQUE (pull_request_id, ordinal),
    CHECK (length(trim(commit_id)) > 0),
    CHECK (length(trim(commit_message)) > 0)
);

CREATE TABLE review_request (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_request(pull_request_id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES repository_user(user_id),
    requested_by BIGINT NOT NULL REFERENCES repository_user(user_id),
    requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (pull_request_id, reviewer_id)
);

CREATE TABLE pull_request_review (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_request(pull_request_id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES repository_user(user_id),
    state review_state NOT NULL,
    reviewed_commit_id TEXT NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    dismissed_at TIMESTAMPTZ,
    dismissal_reason TEXT,
    CHECK (
        (state = 'dismissed' AND dismissed_at IS NOT NULL
            AND dismissal_reason IS NOT NULL)
        OR
        (state <> 'dismissed' AND dismissed_at IS NULL
            AND dismissal_reason IS NULL)
    )
);

-- Historical reviews are retained, but only the latest review per reviewer
-- is treated as current by the merge-eligibility query.
CREATE INDEX pull_request_review_latest_idx
    ON pull_request_review (
        pull_request_id, reviewer_id, submitted_at DESC, review_id DESC
    );

CREATE TABLE review_comment (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL
        REFERENCES pull_request_review(review_id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL CHECK (line_number >= 1),
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (length(trim(file_path)) > 0),
    CHECK (length(trim(body)) > 0)
);

CREATE TABLE review_conversation (
    conversation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_request(pull_request_id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ,
    CHECK (length(trim(topic)) > 0),
    CHECK (
        (resolved AND resolved_at IS NOT NULL)
        OR
        (NOT resolved AND resolved_at IS NULL)
    )
);

CREATE TABLE pull_request_status_check (
    status_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_request(pull_request_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    state check_state NOT NULL DEFAULT 'pending',
    checked_commit_id TEXT NOT NULL,
    completed_at TIMESTAMPTZ,
    details TEXT NOT NULL DEFAULT '',
    UNIQUE (pull_request_id, check_name),
    CHECK (length(trim(check_name)) > 0),
    CHECK (
        (state = 'pending' AND completed_at IS NULL)
        OR
        (state <> 'pending' AND completed_at IS NOT NULL)
    )
);

CREATE INDEX pull_request_repository_state_idx
    ON pull_request(repository_id, state, created_at DESC);

CREATE INDEX unresolved_conversations_idx
    ON review_conversation(pull_request_id)
    WHERE resolved = FALSE;

CREATE INDEX status_check_state_idx
    ON pull_request_status_check(pull_request_id, check_name, state);

-- Function return values are explicit: callers receive a boolean or a
-- table of blockers rather than interpreting printed output.
CREATE FUNCTION is_current_approval(
    p_review_id BIGINT,
    p_dismiss_stale BOOLEAN,
    p_source_head TEXT,
    p_author_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM pull_request_review r
        WHERE r.review_id = p_review_id
          AND r.state = 'approved'
          AND r.reviewer_id <> p_author_id
          AND (
              NOT p_dismiss_stale
              OR r.reviewed_commit_id = p_source_head
          )
          AND NOT EXISTS (
              SELECT 1
              FROM pull_request_review newer
              WHERE newer.pull_request_id = r.pull_request_id
                AND newer.reviewer_id = r.reviewer_id
                AND (newer.submitted_at, newer.review_id)
                    > (r.submitted_at, r.review_id)
          )
    );
$$;

CREATE FUNCTION merge_blockers(p_pull_request_id BIGINT)
RETURNS TABLE (
    blocker_code TEXT,
    blocker_detail TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    pr pull_request%ROWTYPE;
    target_branch repository_branch%ROWTYPE;
    source_branch repository_branch%ROWTYPE;
    policy branch_protection_policy%ROWTYPE;
    approval_count INTEGER;
    owner_approval_count INTEGER;
BEGIN
    SELECT *
    INTO pr
    FROM pull_request
    WHERE pull_request_id = p_pull_request_id;

    IF NOT FOUND THEN
        RETURN QUERY SELECT
            'NOT_FOUND'::TEXT,
            'Pull Request does not exist.'::TEXT;
        RETURN;
    END IF;

    SELECT * INTO source_branch
    FROM repository_branch
    WHERE branch_id = pr.source_branch_id;

    SELECT * INTO target_branch
    FROM repository_branch
    WHERE branch_id = pr.target_branch_id;

    SELECT bp.* INTO policy
    FROM branch_protection_policy bp
    WHERE bp.repository_id = pr.repository_id
      AND (
          bp.branch_pattern = target_branch.branch_name
          OR bp.branch_pattern = '*'
      )
    ORDER BY
        CASE WHEN bp.branch_pattern = target_branch.branch_name
             THEN 0 ELSE 1 END
    LIMIT 1;

    IF pr.state <> 'open' OR pr.is_draft THEN
        RETURN QUERY SELECT
            'PULL_REQUEST_STATE',
            'Request must be open and not a draft.';
    END IF;

    IF target_branch.deleted_at IS NOT NULL
       OR source_branch.deleted_at IS NOT NULL THEN
        RETURN QUERY SELECT
            'BRANCH_DELETED',
            'Source or target branch has been deleted.';
    END IF;

    IF NOT pr.base_synchronized
       OR pr.target_head_at_sync <> target_branch.head_commit THEN
        RETURN QUERY SELECT
            'BASE_OUTDATED',
            'Target branch changed; synchronization is required.';
    END IF;

    IF NOT FOUND THEN
        -- FOUND here refers to the preceding SELECT INTO policy.
        -- The absence of a policy is allowed for an unprotected target.
        IF target_branch.protected THEN
            RETURN QUERY SELECT
                'POLICY_MISSING',
                'Protected branch has no matching policy.';
        END IF;
    END IF;

    IF policy.policy_id IS NOT NULL THEN
        IF policy.require_resolved_conversations AND EXISTS (
            SELECT 1
            FROM review_conversation c
            WHERE c.pull_request_id = pr.pull_request_id
              AND NOT c.resolved
        ) THEN
            RETURN QUERY SELECT
                'UNRESOLVED_CONVERSATIONS',
                'Review conversations remain unresolved.';
        END IF;

        IF policy.require_linear_history AND
           NOT target_branch.linear_history THEN
            RETURN QUERY SELECT
                'LINEAR_HISTORY',
                'Target branch requires linear history.';
        END IF;

        IF EXISTS (
            SELECT 1
            FROM policy_required_check required
            LEFT JOIN pull_request_status_check actual
              ON actual.pull_request_id = pr.pull_request_id
             AND actual.check_name = required.check_name
             AND actual.checked_commit_id = pr.source_head_commit
            WHERE required.policy_id = policy.policy_id
              AND (actual.status_check_id IS NULL OR actual.state <> 'passed')
        ) THEN
            RETURN QUERY SELECT
                'REQUIRED_CHECK',
                'At least one required check is missing, stale, or failing.';
        END IF;

        SELECT count(*)
        INTO approval_count
        FROM pull_request_review r
        WHERE r.pull_request_id = pr.pull_request_id
          AND r.state = 'approved'
          AND r.reviewer_id <> pr.author_id
          AND (
              NOT policy.dismiss_stale_approvals
              OR r.reviewed_commit_id = pr.source_head_commit
          )
          AND NOT EXISTS (
              SELECT 1
              FROM pull_request_review newer
              WHERE newer.pull_request_id = r.pull_request_id
                AND newer.reviewer_id = r.reviewer_id
                AND (newer.submitted_at, newer.review_id)
                    > (r.submitted_at, r.review_id)
          );

        IF approval_count < policy.required_approvals THEN
            RETURN QUERY SELECT
                'APPROVAL_COUNT',
                format(
                    'Requires %s effective approvals; found %s.',
                    policy.required_approvals,
                    approval_count
                );
        END IF;

        IF policy.require_code_owner_approval THEN
            SELECT count(*)
            INTO owner_approval_count
            FROM pull_request_review r
            JOIN policy_code_owner owner
              ON owner.user_id = r.reviewer_id
             AND owner.policy_id = policy.policy_id
            WHERE r.pull_request_id = pr.pull_request_id
              AND r.state = 'approved'
              AND r.reviewer_id <> pr.author_id
              AND (
                  NOT policy.dismiss_stale_approvals
                  OR r.reviewed_commit_id = pr.source_head_commit
              )
              AND NOT EXISTS (
                  SELECT 1
                  FROM pull_request_review newer
                  WHERE newer.pull_request_id = r.pull_request_id
                    AND newer.reviewer_id = r.reviewer_id
                    AND (newer.submitted_at, newer.review_id)
                        > (r.submitted_at, r.review_id)
              );

            IF owner_approval_count = 0 THEN
                RETURN QUERY SELECT
                    'CODE_OWNER_APPROVAL',
                    'A current code-owner approval is required.';
            END IF;
        END IF;
    END IF;

    RETURN;
END;
$$;

CREATE FUNCTION evaluate_pull_request(p_pull_request_id BIGINT)
RETURNS TABLE (
    eligible BOOLEAN,
    blocker_count BIGINT,
    blockers TEXT
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        count(b.blocker_code) = 0,
        count(b.blocker_code),
        COALESCE(
            string_agg(
                b.blocker_code || ': ' || b.blocker_detail,
                '; ' ORDER BY b.blocker_code
            ),
            'No blockers'
        )
    FROM merge_blockers(p_pull_request_id) b;
$$;

-- Sample repository and identities.
INSERT INTO repository (owner_name, repository_name)
VALUES ('engineering', 'audit-service');

INSERT INTO repository_user (username)
VALUES
    ('developer-1'),
    ('reviewer-2'),
    ('security-reviewer'),
    ('release-manager'),
    ('release-admin');

INSERT INTO repository_branch (
    repository_id, branch_name, head_commit, protected, linear_history
)
SELECT repository_id, 'main', 'c-700', TRUE, TRUE
FROM repository
WHERE owner_name = 'engineering'
  AND repository_name = 'audit-service';

INSERT INTO repository_branch (
    repository_id, branch_name, head_commit, protected, linear_history
)
SELECT repository_id, 'feature/audit-log', 'c-701', FALSE, TRUE
FROM repository
WHERE owner_name = 'engineering'
  AND repository_name = 'audit-service';

INSERT INTO branch_protection_policy (
    repository_id,
    branch_pattern,
    required_approvals,
    require_resolved_conversations,
    require_linear_history,
    prohibit_direct_pushes,
    prohibit_force_pushes,
    prohibit_deletion,
    dismiss_stale_approvals,
    require_code_owner_approval
)
SELECT repository_id, 'main', 2, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE
FROM repository
WHERE owner_name = 'engineering'
  AND repository_name = 'audit-service';

INSERT INTO policy_required_check (policy_id, check_name)
SELECT policy_id, 'unit-tests'
FROM branch_protection_policy
WHERE branch_pattern = 'main';

INSERT INTO policy_required_check (policy_id, check_name)
SELECT policy_id, 'security-scan'
FROM branch_protection_policy
WHERE branch_pattern = 'main';

INSERT INTO policy_code_owner (policy_id, user_id)
SELECT bp.policy_id, u.user_id
FROM branch_protection_policy bp
JOIN repository r ON r.repository_id = bp.repository_id
JOIN repository_user u ON u.username = 'security-reviewer'
WHERE r.repository_name = 'audit-service';

INSERT INTO pull_request (
    repository_id,
    author_id,
    source_branch_id,
    target_branch_id,
    title,
    state,
    is_draft,
    source_head_commit,
    target_head_at_sync
)
SELECT
    r.repository_id,
    author.user_id,
    source.branch_id,
    target.branch_id,
    'Preserve actor identity in audit events',
    'open',
    FALSE,
    source.head_commit,
    target.head_commit
FROM repository r
JOIN repository_user author ON author.username = 'developer-1'
JOIN repository_branch source
  ON source.repository_id = r.repository_id
 AND source.branch_name = 'feature/audit-log'
JOIN repository_branch target
  ON target.repository_id = r.repository_id
 AND target.branch_name = 'main'
WHERE r.repository_name = 'audit-service';

INSERT INTO pull_request_commit (
    pull_request_id, commit_id, commit_message, ordinal
)
SELECT pull_request_id, 'c-701',
       'Add audit event model', 1
FROM pull_request
WHERE title = 'Preserve actor identity in audit events';

INSERT INTO review_request (pull_request_id, reviewer_id, requested_by)
SELECT pr.pull_request_id, u.user_id, pr.author_id
FROM pull_request pr
JOIN repository_user u
  ON u.username IN ('reviewer-2', 'security-reviewer');

INSERT INTO pull_request_review (
    pull_request_id, reviewer_id, state, reviewed_commit_id
)
SELECT pr.pull_request_id, u.user_id, 'approved', pr.source_head_commit
FROM pull_request pr
JOIN repository_user u
  ON u.username IN ('reviewer-2', 'security-reviewer');

INSERT INTO review_comment (
    review_id, file_path, line_number, body, resolved
)
SELECT r.review_id, 'src/audit.cpp', 42,
       'Confirm actor identity is retained on authorization failures.',
       TRUE
FROM pull_request_review r
JOIN repository_user u ON u.user_id = r.reviewer_id
WHERE u.username = 'security-reviewer';

INSERT INTO review_conversation (
    pull_request_id, topic, resolved, resolved_at
)
SELECT pull_request_id,
       'Confirm actor identity on failed authorization events.',
       TRUE,
       now()
FROM pull_request
WHERE title = 'Preserve actor identity in audit events';

INSERT INTO pull_request_status_check (
    pull_request_id, check_name, state, checked_commit_id, completed_at
)
SELECT pull_request_id, 'unit-tests', 'passed', source_head_commit, now()
FROM pull_request
WHERE title = 'Preserve actor identity in audit events';

INSERT INTO pull_request_status_check (
    pull_request_id, check_name, state, checked_commit_id, completed_at
)
SELECT pull_request_id, 'security-scan', 'passed', source_head_commit, now()
FROM pull_request
WHERE title = 'Preserve actor identity in audit events';

-- Read the effective approval count without treating historical approvals
-- as independent votes.
WITH latest_reviews AS (
    SELECT DISTINCT ON (r.pull_request_id, r.reviewer_id)
        r.pull_request_id,
        r.reviewer_id,
        r.state,
        r.reviewed_commit_id
    FROM pull_request_review r
    ORDER BY r.pull_request_id, r.reviewer_id,
             r.submitted_at DESC, r.review_id DESC
)
SELECT
    pr.title,
    count(*) FILTER (
        WHERE lr.state = 'approved'
          AND lr.reviewer_id <> pr.author_id
          AND (
              NOT bp.dismiss_stale_approvals
              OR lr.reviewed_commit_id = pr.source_head_commit
          )
    ) AS effective_approvals
FROM pull_request pr
JOIN branch_protection_policy bp
  ON bp.repository_id = pr.repository_id
 AND bp.branch_pattern = 'main'
LEFT JOIN latest_reviews lr
  ON lr.pull_request_id = pr.pull_request_id
GROUP BY pr.title;

-- The function returns one row containing eligibility, blocker count, and
-- an explanation suitable for a merge interface or deployment audit log.
SELECT *
FROM evaluate_pull_request(
    (SELECT pull_request_id
     FROM pull_request
     WHERE title = 'Preserve actor identity in audit events')
);

-- A missing required check must prevent eligibility. The check is added
-- as a pending run on the current commit to demonstrate this distinction.
INSERT INTO pull_request_status_check (
    pull_request_id, check_name, state, checked_commit_id
)
SELECT pull_request_id, 'dependency-review', 'pending', source_head_commit
FROM pull_request
WHERE title = 'Preserve actor identity in audit events'
ON CONFLICT (pull_request_id, check_name)
DO UPDATE SET
    state = EXCLUDED.state,
    checked_commit_id = EXCLUDED.checked_commit_id,
    completed_at = NULL;

SELECT *
FROM evaluate_pull_request(
    (SELECT pull_request_id
     FROM pull_request
     WHERE title = 'Preserve actor identity in audit events')
);

-- Return values and database errors are different contracts. This block
-- catches a constraint violation so the demonstration can continue.
DO $$
BEGIN
    BEGIN
        INSERT INTO branch_protection_policy (
            repository_id, branch_pattern, required_approvals
        )
        SELECT repository_id, 'main', -1
        FROM repository
        WHERE repository_name = 'audit-service';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'Invalid approval requirement rejected by CHECK constraint.';
    END;
END;
$$;

-- A direct-push guard is database-level defense in depth. Application and
-- hosting-provider permissions must still enforce the actual Git operation.
CREATE FUNCTION reject_protected_branch_mutation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.protected AND NEW.head_commit <> OLD.head_commit THEN
        RAISE EXCEPTION
            'Direct head updates are prohibited for protected branch %',
            OLD.branch_name
            USING ERRCODE = '42501';
    END IF;

    IF OLD.protected AND OLD.deleted_at IS NULL
       AND NEW.deleted_at IS NOT NULL THEN
        IF EXISTS (
            SELECT 1
            FROM branch_protection_policy p
            WHERE p.repository_id = OLD.repository_id
              AND (
                  p.branch_pattern = OLD.branch_name
                  OR p.branch_pattern = '*'
              )
              AND p.prohibit_deletion
        ) THEN
            RAISE EXCEPTION
                'Deletion is prohibited for protected branch %',
                OLD.branch_name
                USING ERRCODE = '42501';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER protect_branch_head
BEFORE UPDATE OF head_commit, deleted_at ON repository_branch
FOR EACH ROW
EXECUTE FUNCTION reject_protected_branch_mutation();

-- Keep the demonstration transaction isolated from the caller's schema
-- and data. Replace ROLLBACK with COMMIT to retain the sample records.
ROLLBACK;
