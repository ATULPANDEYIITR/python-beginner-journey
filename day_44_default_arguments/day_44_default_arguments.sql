-- PostgreSQL 15+
-- Repository governance: pull requests, code reviews, approvals,
-- status checks, and protected-branch enforcement.

BEGIN;

DROP VIEW IF EXISTS pull_request_merge_eligibility CASCADE;
DROP TABLE IF EXISTS merge_events CASCADE;
DROP TABLE IF EXISTS review_comments CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS status_check_runs CASCADE;
DROP TABLE IF EXISTS required_status_checks CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS pull_request_commits CASCADE;
DROP TABLE IF EXISTS pull_requests CASCADE;
DROP TABLE IF EXISTS branch_protection CASCADE;
DROP TABLE IF EXISTS branches CASCADE;
DROP TABLE IF EXISTS reviewers CASCADE;
DROP TABLE IF EXISTS repository_members CASCADE;
DROP TABLE IF EXISTS repositories CASCADE;
DROP TYPE IF EXISTS pull_request_state CASCADE;
DROP TYPE IF EXISTS review_state CASCADE;
DROP TYPE IF EXISTS check_state CASCADE;
DROP TYPE IF EXISTS merge_method CASCADE;
DROP TYPE IF EXISTS member_role CASCADE;

CREATE TYPE pull_request_state AS ENUM (
    'draft', 'open', 'closed', 'merged'
);

CREATE TYPE review_state AS ENUM (
    'commented', 'approved', 'changes_requested', 'dismissed'
);

CREATE TYPE check_state AS ENUM (
    'pending', 'success', 'failure', 'cancelled'
);

CREATE TYPE merge_method AS ENUM (
    'merge_commit', 'squash', 'rebase'
);

CREATE TYPE member_role AS ENUM (
    'read', 'write', 'maintain', 'admin'
);

CREATE TABLE repositories (
    repository_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    owner_name text NOT NULL,
    repository_name text NOT NULL,
    default_branch text NOT NULL DEFAULT 'main',
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (owner_name, repository_name),
    CHECK (length(trim(owner_name)) > 0),
    CHECK (length(trim(repository_name)) > 0),
    CHECK (length(trim(default_branch)) > 0)
);

CREATE TABLE repository_members (
    repository_id bigint NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    username text NOT NULL,
    role member_role NOT NULL DEFAULT 'read',
    active boolean NOT NULL DEFAULT true,
    PRIMARY KEY (repository_id, username),
    CHECK (length(trim(username)) > 0)
);

CREATE TABLE reviewers (
    repository_id bigint NOT NULL,
    username text NOT NULL,
    team_name text NOT NULL,
    can_approve boolean NOT NULL DEFAULT true,
    active boolean NOT NULL DEFAULT true,
    PRIMARY KEY (repository_id, username),
    FOREIGN KEY (repository_id, username)
        REFERENCES repository_members(repository_id, username)
        ON DELETE CASCADE,
    CHECK (length(trim(team_name)) > 0)
);

CREATE TABLE branches (
    branch_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id bigint NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    branch_name text NOT NULL,
    head_sha text NOT NULL,
    protected boolean NOT NULL DEFAULT false,
    deleted_at timestamptz,
    UNIQUE (repository_id, branch_name),
    UNIQUE (branch_id, repository_id),
    CHECK (length(trim(branch_name)) > 0),
    CHECK (length(trim(head_sha)) > 0)
);

CREATE TABLE branch_protection (
    protection_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id bigint NOT NULL UNIQUE REFERENCES branches(branch_id)
        ON DELETE CASCADE,
    required_approvals integer NOT NULL DEFAULT 2
        CHECK (required_approvals >= 0),
    dismiss_stale_approvals boolean NOT NULL DEFAULT true,
    require_code_owner_review boolean NOT NULL DEFAULT false,
    require_conversation_resolution boolean NOT NULL DEFAULT true,
    require_linear_history boolean NOT NULL DEFAULT false,
    prohibit_direct_push boolean NOT NULL DEFAULT true,
    prohibit_force_push boolean NOT NULL DEFAULT true,
    prohibit_deletion boolean NOT NULL DEFAULT true,
    require_ci boolean NOT NULL DEFAULT true,
    require_security_scan boolean NOT NULL DEFAULT true,
    allow_administrator_bypass boolean NOT NULL DEFAULT false,
    permitted_merge_methods merge_method[] NOT NULL
        DEFAULT ARRAY['squash', 'rebase']::merge_method[],
    CHECK (cardinality(permitted_merge_methods) > 0)
);

CREATE TABLE pull_requests (
    pull_request_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id bigint NOT NULL REFERENCES repositories(repository_id),
    number integer NOT NULL CHECK (number > 0),
    title text NOT NULL CHECK (length(trim(title)) > 0),
    author text NOT NULL,
    source_branch_id bigint NOT NULL,
    target_branch_id bigint NOT NULL,
    state pull_request_state NOT NULL DEFAULT 'draft',
    head_revision integer NOT NULL DEFAULT 0 CHECK (head_revision >= 0),
    base_revision integer NOT NULL DEFAULT 0 CHECK (base_revision >= 0),
    opened_at timestamptz NOT NULL DEFAULT now(),
    closed_at timestamptz,
    merged_at timestamptz,
    merged_by text,
    merge_commit_sha text,
    UNIQUE (repository_id, number),
    FOREIGN KEY (source_branch_id, repository_id)
        REFERENCES branches(branch_id, repository_id),
    FOREIGN KEY (target_branch_id, repository_id)
        REFERENCES branches(branch_id, repository_id),
    FOREIGN KEY (repository_id, author)
        REFERENCES repository_members(repository_id, username),
    CHECK (source_branch_id <> target_branch_id),
    CHECK (
        (state = 'merged' AND merged_at IS NOT NULL
            AND merged_by IS NOT NULL AND merge_commit_sha IS NOT NULL)
        OR
        (state <> 'merged' AND merged_at IS NULL
            AND merged_by IS NULL AND merge_commit_sha IS NULL)
    )
);

CREATE TABLE pull_request_commits (
    pull_request_id bigint NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    commit_sha text NOT NULL,
    commit_message text NOT NULL,
    changeset_revision integer NOT NULL CHECK (changeset_revision >= 0),
    committed_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (pull_request_id, commit_sha),
    CHECK (length(trim(commit_sha)) > 0),
    CHECK (length(trim(commit_message)) > 0)
);

CREATE TABLE reviews (
    review_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id bigint NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    reviewer text NOT NULL,
    state review_state NOT NULL,
    changeset_revision integer NOT NULL CHECK (changeset_revision >= 0),
    submitted_at timestamptz NOT NULL DEFAULT now(),
    dismissed_at timestamptz,
    summary text NOT NULL DEFAULT '',
    FOREIGN KEY (pull_request_id, reviewer)
        REFERENCES repository_members(repository_id, username)
        DEFERRABLE INITIALLY DEFERRED,
    CHECK (
        (state = 'dismissed' AND dismissed_at IS NOT NULL)
        OR
        (state <> 'dismissed' AND dismissed_at IS NULL)
    )
);

-- The reviewer identity is associated with the repository through a trigger,
-- because pull_request_id determines repository_id indirectly.
CREATE OR REPLACE FUNCTION validate_review_reviewer()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    pr_author text;
    pr_repository_id bigint;
    reviewer_active boolean;
    reviewer_can_approve boolean;
BEGIN
    SELECT author, repository_id
      INTO pr_author, pr_repository_id
      FROM pull_requests
     WHERE pull_request_id = NEW.pull_request_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Pull request % does not exist', NEW.pull_request_id;
    END IF;

    IF NEW.reviewer = pr_author THEN
        RAISE EXCEPTION 'Pull request authors cannot review their own changes';
    END IF;

    SELECT rm.active, COALESCE(rv.can_approve, false)
      INTO reviewer_active, reviewer_can_approve
      FROM repository_members rm
      LEFT JOIN reviewers rv
        ON rv.repository_id = rm.repository_id
       AND rv.username = rm.username
     WHERE rm.repository_id = pr_repository_id
       AND rm.username = NEW.reviewer;

    IF NOT FOUND OR NOT reviewer_active THEN
        RAISE EXCEPTION 'Reviewer is not an active repository member';
    END IF;

    IF NEW.state = 'approved' AND NOT reviewer_can_approve THEN
        RAISE EXCEPTION 'Reviewer % is not eligible to approve', NEW.reviewer;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER reviews_validate_reviewer
BEFORE INSERT OR UPDATE ON reviews
FOR EACH ROW EXECUTE FUNCTION validate_review_reviewer();

CREATE TABLE review_comments (
    comment_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id bigint NOT NULL REFERENCES reviews(review_id)
        ON DELETE CASCADE,
    file_path text NOT NULL,
    line_number integer,
    body text NOT NULL CHECK (length(trim(body)) > 0),
    created_at timestamptz NOT NULL DEFAULT now(),
    resolved boolean NOT NULL DEFAULT false,
    CHECK (length(trim(file_path)) > 0),
    CHECK (line_number IS NULL OR line_number > 0)
);

CREATE TABLE conversations (
    conversation_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id bigint NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    thread_key text NOT NULL,
    body text NOT NULL CHECK (length(trim(body)) > 0),
    created_by text NOT NULL,
    resolved boolean NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT now(),
    resolved_at timestamptz,
    UNIQUE (pull_request_id, thread_key),
    CHECK (
        (resolved = true AND resolved_at IS NOT NULL)
        OR
        (resolved = false AND resolved_at IS NULL)
    )
);

CREATE TABLE required_status_checks (
    protection_id bigint NOT NULL REFERENCES branch_protection(protection_id)
        ON DELETE CASCADE,
    check_name text NOT NULL,
    PRIMARY KEY (protection_id, check_name),
    CHECK (length(trim(check_name)) > 0)
);

CREATE TABLE status_check_runs (
    check_run_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id bigint NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    check_name text NOT NULL,
    changeset_revision integer NOT NULL CHECK (changeset_revision >= 0),
    state check_state NOT NULL DEFAULT 'pending',
    started_at timestamptz NOT NULL DEFAULT now(),
    completed_at timestamptz,
    CHECK (
        (state = 'pending' AND completed_at IS NULL)
        OR
        (state <> 'pending' AND completed_at IS NOT NULL)
    )
);

CREATE TABLE merge_events (
    merge_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id bigint NOT NULL REFERENCES pull_requests(pull_request_id),
    actor text NOT NULL,
    method merge_method NOT NULL,
    result_sha text NOT NULL,
    merged_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (pull_request_id),
    CHECK (length(trim(actor)) > 0),
    CHECK (length(trim(result_sha)) > 0)
);

CREATE INDEX pull_requests_target_state_idx
    ON pull_requests(target_branch_id, state);

CREATE INDEX reviews_pr_revision_state_idx
    ON reviews(pull_request_id, changeset_revision, state, submitted_at DESC);

CREATE INDEX status_checks_current_idx
    ON status_check_runs(pull_request_id, check_name, changeset_revision, started_at DESC);

CREATE INDEX unresolved_conversations_idx
    ON conversations(pull_request_id)
    WHERE resolved = false;

CREATE INDEX review_comments_unresolved_idx
    ON review_comments(review_id)
    WHERE resolved = false;

-- A new changeset revision invalidates previously successful check results.
CREATE OR REPLACE FUNCTION prevent_invalid_pr_transition()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.state = 'merged' AND NEW.state <> 'merged' THEN
        RAISE EXCEPTION 'Merged pull requests cannot be reopened or changed';
    END IF;

    IF OLD.state = 'closed' AND NEW.state = 'merged' THEN
        RAISE EXCEPTION 'A closed pull request must be reopened before merging';
    END IF;

    IF OLD.state = 'merged' AND
       (NEW.merged_at, NEW.merged_by, NEW.merge_commit_sha)
       IS DISTINCT FROM
       (OLD.merged_at, OLD.merged_by, OLD.merge_commit_sha) THEN
        RAISE EXCEPTION 'Merge audit fields are immutable';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER pull_requests_state_guard
BEFORE UPDATE ON pull_requests
FOR EACH ROW EXECUTE FUNCTION prevent_invalid_pr_transition();

-- Calculate eligibility from current reviews and checks, not from historical
-- approvals alone. A production merge operation must lock and revalidate the
-- PR, branch policy, and current target head inside one transaction.
CREATE VIEW pull_request_merge_eligibility AS
WITH latest_reviews AS (
    SELECT DISTINCT ON (r.pull_request_id, r.reviewer)
        r.pull_request_id,
        r.reviewer,
        r.state,
        r.changeset_revision,
        r.dismissed_at
    FROM reviews r
    ORDER BY
        r.pull_request_id,
        r.reviewer,
        r.submitted_at DESC,
        r.review_id DESC
),
approval_counts AS (
    SELECT
        pr.pull_request_id,
        COUNT(lr.reviewer) FILTER (
            WHERE lr.state = 'approved'
              AND lr.dismissed_at IS NULL
              AND (
                  NOT COALESCE(bp.dismiss_stale_approvals, true)
                  OR lr.changeset_revision = pr.head_revision
              )
        ) AS current_approvals
    FROM pull_requests pr
    LEFT JOIN latest_reviews lr
      ON lr.pull_request_id = pr.pull_request_id
    LEFT JOIN branch_protection bp
      ON bp.branch_id = pr.target_branch_id
    GROUP BY pr.pull_request_id
),
current_checks AS (
    SELECT DISTINCT ON (scr.pull_request_id, scr.check_name)
        scr.pull_request_id,
        scr.check_name,
        scr.state,
        scr.changeset_revision
    FROM status_check_runs scr
    ORDER BY
        scr.pull_request_id,
        scr.check_name,
        scr.changeset_revision DESC,
        scr.started_at DESC,
        scr.check_run_id DESC
),
check_failures AS (
    SELECT
        pr.pull_request_id,
        COUNT(*) FILTER (
            WHERE required.check_name IS NOT NULL
              AND (
                  current_check.state IS DISTINCT FROM 'success'::check_state
                  OR current_check.changeset_revision <> pr.head_revision
              )
        ) AS missing_required_checks
    FROM pull_requests pr
    LEFT JOIN branch_protection bp
      ON bp.branch_id = pr.target_branch_id
    LEFT JOIN required_status_checks required
      ON required.protection_id = bp.protection_id
    LEFT JOIN current_checks current_check
      ON current_check.pull_request_id = pr.pull_request_id
     AND current_check.check_name = required.check_name
    GROUP BY pr.pull_request_id
),
unresolved_counts AS (
    SELECT
        pr.pull_request_id,
        COUNT(c.conversation_id) FILTER (
            WHERE c.resolved = false
        ) AS unresolved_threads
    FROM pull_requests pr
    LEFT JOIN conversations c
      ON c.pull_request_id = pr.pull_request_id
    GROUP BY pr.pull_request_id
)
SELECT
    pr.pull_request_id,
    pr.repository_id,
    pr.number,
    pr.title,
    pr.state,
    pr.head_revision,
    pr.target_branch_id,
    COALESCE(ac.current_approvals, 0) AS current_approvals,
    COALESCE(bp.required_approvals, 2) AS required_approvals,
    COALESCE(cf.missing_required_checks, 0) AS missing_required_checks,
    COALESCE(uc.unresolved_threads, 0) AS unresolved_threads,
    (
        pr.state = 'open'
        AND COALESCE(ac.current_approvals, 0)
            >= COALESCE(bp.required_approvals, 2)
        AND COALESCE(cf.missing_required_checks, 0) = 0
        AND (
            NOT COALESCE(bp.require_conversation_resolution, true)
            OR COALESCE(uc.unresolved_threads, 0) = 0
        )
    ) AS eligible_under_viewed_rules
FROM pull_requests pr
LEFT JOIN branch_protection bp
  ON bp.branch_id = pr.target_branch_id
LEFT JOIN approval_counts ac
  ON ac.pull_request_id = pr.pull_request_id
LEFT JOIN check_failures cf
  ON cf.pull_request_id = pr.pull_request_id
LEFT JOIN unresolved_counts uc
  ON uc.pull_request_id = pr.pull_request_id;

-- Sample repository and governance policy.
INSERT INTO repositories (owner_name, repository_name)
VALUES ('platform-team', 'deployment-service');

INSERT INTO repository_members (repository_id, username, role)
VALUES
    (1, 'developer-lee', 'write'),
    (1, 'reviewer-alex', 'maintain'),
    (1, 'reviewer-sam', 'maintain'),
    (1, 'release-admin', 'admin');

INSERT INTO reviewers (repository_id, username, team_name, can_approve)
VALUES
    (1, 'reviewer-alex', 'platform', true),
    (1, 'reviewer-sam', 'security', true),
    (1, 'release-admin', 'release-engineering', true);

INSERT INTO branches (
    repository_id, branch_name, head_sha, protected
)
VALUES
    (1, 'main', 'base-0087', true),
    (1, 'feature/deployment-auth', 'commit-b52d7f1', false);

INSERT INTO branch_protection (
    branch_id,
    required_approvals,
    dismiss_stale_approvals,
    require_conversation_resolution,
    require_linear_history,
    prohibit_direct_push,
    prohibit_force_push,
    prohibit_deletion,
    require_ci,
    require_security_scan,
    allow_administrator_bypass,
    permitted_merge_methods
)
VALUES (
    1,
    2,
    true,
    true,
    true,
    true,
    true,
    true,
    true,
    true,
    false,
    ARRAY['squash', 'rebase']::merge_method[]
);

INSERT INTO required_status_checks (protection_id, check_name)
VALUES
    (1, 'ci'),
    (1, 'security'),
    (1, 'integration');

INSERT INTO pull_requests (
    repository_id,
    number,
    title,
    author,
    source_branch_id,
    target_branch_id,
    state,
    head_revision,
    base_revision
)
VALUES (
    1,
    104,
    'Enforce deployment authorization',
    'developer-lee',
    2,
    1,
    'open',
    2,
    87
);

INSERT INTO pull_request_commits (
    pull_request_id, commit_sha, commit_message, changeset_revision
)
VALUES
    (1, 'a91c3e0', 'Add deployment authorization middleware', 1),
    (1, 'b52d7f1', 'Test denied deployment requests', 2);

INSERT INTO reviews (
    pull_request_id, reviewer, state, changeset_revision, summary
)
VALUES
    (1, 'reviewer-alex', 'approved', 2, 'Authorization boundary verified'),
    (1, 'reviewer-sam', 'approved', 2, 'Security tests reviewed');

INSERT INTO review_comments (
    review_id, file_path, line_number, body, resolved
)
VALUES
    (1, 'src/deployment_service.py', 88,
     'Confirm that denied requests emit an audit event.', true);

INSERT INTO conversations (
    pull_request_id, thread_key, body, created_by, resolved, resolved_at
)
VALUES
    (1, 'audit-event', 'Verify audit coverage for denied deployments.',
     'reviewer-sam', true, now());

INSERT INTO status_check_runs (
    pull_request_id, check_name, changeset_revision, state, completed_at
)
VALUES
    (1, 'ci', 2, 'success', now()),
    (1, 'security', 2, 'success', now()),
    (1, 'integration', 2, 'success', now());

-- The current PR satisfies the required approvals, checks, and conversations.
SELECT
    number,
    title,
    current_approvals,
    required_approvals,
    missing_required_checks,
    unresolved_threads,
    eligible_under_viewed_rules
FROM pull_request_merge_eligibility
ORDER BY number;

-- A newer commit makes prior approval and check records stale.
UPDATE pull_requests
SET head_revision = head_revision + 1
WHERE pull_request_id = 1;

INSERT INTO pull_request_commits (
    pull_request_id, commit_sha, commit_message, changeset_revision
)
VALUES (
    1, 'c63e8a2', 'Handle malformed deployment identities', 3
);

-- Historical successes and approvals remain stored for audit purposes.
-- They do not satisfy current-revision requirements.
SELECT
    number,
    current_approvals,
    missing_required_checks,
    eligible_under_viewed_rules
FROM pull_request_merge_eligibility
WHERE pull_request_id = 1;

-- New approvals and status-check runs restore current eligibility.
INSERT INTO reviews (
    pull_request_id, reviewer, state, changeset_revision, summary
)
VALUES
    (1, 'reviewer-alex', 'approved', 3, 'Updated changes reviewed'),
    (1, 'reviewer-sam', 'approved', 3, 'Updated security behavior verified');

INSERT INTO status_check_runs (
    pull_request_id, check_name, changeset_revision, state, completed_at
)
VALUES
    (1, 'ci', 3, 'success', now()),
    (1, 'security', 3, 'success', now()),
    (1, 'integration', 3, 'success', now());

SELECT
    number,
    current_approvals,
    missing_required_checks,
    unresolved_threads,
    eligible_under_viewed_rules
FROM pull_request_merge_eligibility
WHERE pull_request_id = 1;

-- Direct-push, force-push, branch-deletion, bypass, and merge-method
-- restrictions are policy data. Enforcement of those operations must occur
-- in the trusted repository service or hosting platform; SQL constraints
-- alone cannot intercept external Git transport operations.

COMMIT;
