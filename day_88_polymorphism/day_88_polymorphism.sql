/*
===============================================================
POLYMORPHISM IN POSTGRESQL
===============================================================

Domain:
Repository development and polymorphic notification delivery.

Database: PostgreSQL 14+

Demonstrates:
1. Relational domain modeling
2. Abstract notification channel types
3. Discriminator-based polymorphism
4. Table inheritance through foreign keys
5. Strategy selection through SQL functions
6. Repository and branch relationships
7. Pull Request lifecycle
8. Review and approval records
9. Status-check evaluation
10. Branch protection
11. Merge eligibility
12. Triggers and integrity enforcement
13. Reporting and aggregation
14. Transactions and failure handling

The SQL model separates:
- Branch state
- Proposed changes
- Review decisions
- Approval decisions
- Automated checks
- Repository enforcement
- Merge eligibility
===============================================================
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS polymorphism_lab;

SET search_path TO polymorphism_lab, public;


/* ============================================================
   1. ENUMERATED DOMAIN TYPES
   ============================================================ */

CREATE TYPE pull_request_state AS ENUM (
    'draft',
    'open',
    'closed',
    'merged'
);

CREATE TYPE review_state AS ENUM (
    'approved',
    'changes_requested',
    'commented',
    'dismissed'
);

CREATE TYPE check_state AS ENUM (
    'pending',
    'passed',
    'failed'
);

CREATE TYPE merge_strategy AS ENUM (
    'merge_commit',
    'squash',
    'rebase'
);

CREATE TYPE conversation_state AS ENUM (
    'open',
    'resolved'
);

CREATE TYPE notification_channel_type AS ENUM (
    'email',
    'sms',
    'webhook'
);


/* ============================================================
   2. REPOSITORIES
   ============================================================ */

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    repository_name VARCHAR(150) NOT NULL UNIQUE,

    owner_name VARCHAR(100) NOT NULL,

    default_branch VARCHAR(100) NOT NULL DEFAULT 'main',

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_repository_name
        CHECK (repository_name ~ '^[A-Za-z0-9_.-]+$')
);


/* ============================================================
   3. USERS AND REPOSITORY ROLES
   ============================================================ */

CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    username VARCHAR(100) NOT NULL UNIQUE,

    email VARCHAR(255) NOT NULL UNIQUE,

    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE repository_members (
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,

    user_id BIGINT NOT NULL
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    repository_role VARCHAR(30) NOT NULL,

    can_bypass_protection BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY (repository_id, user_id),

    CONSTRAINT valid_repository_role
        CHECK (
            repository_role IN (
                'administrator',
                'maintainer',
                'developer',
                'reviewer',
                'viewer'
            )
        )
);


/* ============================================================
   4. BRANCHES AND COMMITS
   ============================================================ */

CREATE TABLE branches (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,

    branch_name VARCHAR(150) NOT NULL,

    head_commit VARCHAR(64) NOT NULL,

    is_protected BOOLEAN NOT NULL DEFAULT FALSE,

    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (repository_id, branch_name),

    UNIQUE (repository_id, branch_id)
);

CREATE TABLE commits (
    commit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,

    commit_hash VARCHAR(64) NOT NULL,

    author_id BIGINT NOT NULL
        REFERENCES users(user_id),

    commit_message TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (repository_id, commit_hash),

    UNIQUE (repository_id, commit_id)
);

CREATE TABLE branch_commits (
    branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id)
        ON DELETE CASCADE,

    commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id)
        ON DELETE CASCADE,

    sequence_number INTEGER NOT NULL,

    PRIMARY KEY (branch_id, sequence_number),

    UNIQUE (branch_id, commit_id),

    CHECK (sequence_number > 0)
);


/* ============================================================
   5. PULL REQUESTS
   ============================================================ */

CREATE TABLE pull_requests (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    repository_id BIGINT NOT NULL,

    source_branch_id BIGINT NOT NULL,

    target_branch_id BIGINT NOT NULL,

    author_id BIGINT NOT NULL
        REFERENCES users(user_id),

    title VARCHAR(250) NOT NULL,

    description TEXT,

    base_commit VARCHAR(64) NOT NULL,

    head_commit VARCHAR(64) NOT NULL,

    state pull_request_state NOT NULL DEFAULT 'draft',

    is_draft BOOLEAN NOT NULL DEFAULT TRUE,

    merge_strategy merge_strategy,

    conversations_resolved BOOLEAN NOT NULL DEFAULT FALSE,

    merged_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    FOREIGN KEY (repository_id, source_branch_id)
        REFERENCES branches(repository_id, branch_id),

    FOREIGN KEY (repository_id, target_branch_id)
        REFERENCES branches(repository_id, branch_id),

    CHECK (source_branch_id <> target_branch_id),

    CHECK (length(trim(title)) > 0),

    CHECK (
        (state = 'merged' AND merged_at IS NOT NULL)
        OR
        (state <> 'merged' AND merged_at IS NULL)
    ),

    UNIQUE (repository_id, pull_request_id)
);


/* ============================================================
   6. PULL REQUEST COMMITS
   ============================================================ */

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,

    commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id),

    sequence_number INTEGER NOT NULL,

    PRIMARY KEY (pull_request_id, commit_id),

    UNIQUE (pull_request_id, sequence_number),

    CHECK (sequence_number > 0)
);


/* ============================================================
   7. REVIEWER ELIGIBILITY
   ============================================================ */

CREATE TABLE reviewer_assignments (
    repository_id BIGINT NOT NULL,

    pull_request_id BIGINT NOT NULL,

    reviewer_id BIGINT NOT NULL,

    is_eligible BOOLEAN NOT NULL DEFAULT TRUE,

    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (pull_request_id, reviewer_id),

    FOREIGN KEY (repository_id, pull_request_id)
        REFERENCES pull_requests(repository_id, pull_request_id)
        ON DELETE CASCADE,

    FOREIGN KEY (repository_id, reviewer_id)
        REFERENCES repository_members(repository_id, user_id)
        ON DELETE CASCADE
);


/* ============================================================
   8. CODE REVIEWS
   ============================================================ */

CREATE TABLE reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,

    reviewer_id BIGINT NOT NULL
        REFERENCES users(user_id),

    reviewed_commit VARCHAR(64) NOT NULL,

    review_status review_state NOT NULL,

    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    dismissed_at TIMESTAMPTZ,

    review_summary TEXT,

    CHECK (
        (review_status = 'dismissed' AND dismissed_at IS NOT NULL)
        OR
        (review_status <> 'dismissed' AND dismissed_at IS NULL)
    )
);

CREATE INDEX idx_reviews_pull_request
    ON reviews(pull_request_id, submitted_at DESC);

CREATE INDEX idx_reviews_current_approval
    ON reviews(pull_request_id, reviewed_commit, reviewer_id)
    WHERE review_status = 'approved';


/* ============================================================
   9. REVIEW COMMENTS AND CONVERSATIONS
   ============================================================ */

CREATE TABLE review_comments (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    review_id BIGINT NOT NULL
        REFERENCES reviews(review_id)
        ON DELETE CASCADE,

    file_path TEXT NOT NULL,

    line_number INTEGER,

    comment_body TEXT NOT NULL,

    conversation_status conversation_state
        NOT NULL DEFAULT 'open',

    resolved_by BIGINT REFERENCES users(user_id),

    resolved_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (line_number IS NULL OR line_number > 0),

    CHECK (length(trim(comment_body)) > 0),

    CHECK (
        (
            conversation_status = 'resolved'
            AND resolved_by IS NOT NULL
            AND resolved_at IS NOT NULL
        )
        OR
        (
            conversation_status = 'open'
            AND resolved_by IS NULL
            AND resolved_at IS NULL
        )
    )
);

CREATE INDEX idx_review_comments_open
    ON review_comments(review_id)
    WHERE conversation_status = 'open';


/* ============================================================
   10. AUTOMATED STATUS CHECKS
   ============================================================ */

CREATE TABLE status_checks (
    status_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,

    check_name VARCHAR(120) NOT NULL,

    tested_commit VARCHAR(64) NOT NULL,

    check_status check_state NOT NULL DEFAULT 'pending',

    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    completed_at TIMESTAMPTZ,

    execution_details JSONB NOT NULL DEFAULT '{}'::jsonb,

    UNIQUE (
        pull_request_id,
        check_name,
        tested_commit
    ),

    CHECK (
        (
            check_status = 'pending'
            AND completed_at IS NULL
        )
        OR
        (
            check_status IN ('passed', 'failed')
            AND completed_at IS NOT NULL
        )
    )
);

CREATE INDEX idx_status_checks_pr_commit
    ON status_checks(
        pull_request_id,
        tested_commit,
        check_status
    );


/* ============================================================
   11. BRANCH PROTECTION POLICIES
   ============================================================ */

CREATE TABLE branch_protection_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,

    branch_pattern VARCHAR(150) NOT NULL,

    required_reviews INTEGER NOT NULL DEFAULT 1,

    require_status_checks BOOLEAN NOT NULL DEFAULT TRUE,

    require_resolved_conversations BOOLEAN NOT NULL DEFAULT TRUE,

    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,

    prohibit_direct_push BOOLEAN NOT NULL DEFAULT TRUE,

    prohibit_force_push BOOLEAN NOT NULL DEFAULT TRUE,

    prohibit_branch_deletion BOOLEAN NOT NULL DEFAULT TRUE,

    require_administrator_approval BOOLEAN NOT NULL DEFAULT FALSE,

    allow_bypass BOOLEAN NOT NULL DEFAULT FALSE,

    enabled BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (repository_id, branch_pattern),

    CHECK (required_reviews >= 0)
);

CREATE TABLE required_status_checks (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id)
        ON DELETE CASCADE,

    check_name VARCHAR(120) NOT NULL,

    PRIMARY KEY (policy_id, check_name)
);


/* ============================================================
   12. MERGE ELIGIBILITY AUDIT
   ============================================================ */

CREATE TABLE merge_evaluations (
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,

    evaluated_by BIGINT NOT NULL
        REFERENCES users(user_id),

    is_eligible BOOLEAN NOT NULL,

    violations JSONB NOT NULL DEFAULT '[]'::jsonb,

    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_merge_evaluations_pr
    ON merge_evaluations(pull_request_id, evaluated_at DESC);


/* ============================================================
   13. POLYMORPHIC NOTIFICATION MODEL
   ============================================================ */

/*
A single notification table identifies the abstract channel.
Channel-specific tables provide subtype details.

The discriminator controls which implementation is selected.
*/

CREATE TABLE notification_channels (
    channel_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    channel_type notification_channel_type NOT NULL,

    channel_name VARCHAR(100) NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    UNIQUE (channel_name, channel_type),

    UNIQUE (channel_id, channel_type)
);

CREATE TABLE email_channels (
    channel_id BIGINT PRIMARY KEY,

    channel_type notification_channel_type
        NOT NULL DEFAULT 'email',

    sender_address VARCHAR(255) NOT NULL,

    FOREIGN KEY (channel_id, channel_type)
        REFERENCES notification_channels(channel_id, channel_type)
        ON DELETE CASCADE,

    CHECK (channel_type = 'email')
);

CREATE TABLE sms_channels (
    channel_id BIGINT PRIMARY KEY,

    channel_type notification_channel_type
        NOT NULL DEFAULT 'sms',

    sender_number VARCHAR(20) NOT NULL,

    FOREIGN KEY (channel_id, channel_type)
        REFERENCES notification_channels(channel_id, channel_type)
        ON DELETE CASCADE,

    CHECK (channel_type = 'sms')
);

CREATE TABLE webhook_channels (
    channel_id BIGINT PRIMARY KEY,

    channel_type notification_channel_type
        NOT NULL DEFAULT 'webhook',

    endpoint_url TEXT NOT NULL,

    FOREIGN KEY (channel_id, channel_type)
        REFERENCES notification_channels(channel_id, channel_type)
        ON DELETE CASCADE,

    CHECK (channel_type = 'webhook'),

    CHECK (
        endpoint_url ~ '^https://'
    )
);

CREATE TABLE notification_events (
    notification_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    channel_id BIGINT NOT NULL
        REFERENCES notification_channels(channel_id),

    recipient TEXT NOT NULL,

    message TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    delivery_attempts INTEGER NOT NULL DEFAULT 0,

    delivered BOOLEAN NOT NULL DEFAULT FALSE,

    CHECK (length(trim(recipient)) > 0),

    CHECK (length(trim(message)) > 0),

    CHECK (delivery_attempts >= 0)
);


/* ============================================================
   14. POLYMORPHIC NOTIFICATION DISPATCH
   ============================================================ */

CREATE OR REPLACE FUNCTION dispatch_notification(
    p_notification_id BIGINT
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_type notification_channel_type;
    v_active BOOLEAN;
    v_recipient TEXT;
    v_message TEXT;
    v_valid BOOLEAN := FALSE;
    v_attempts INTEGER;
BEGIN

    SELECT
        nc.channel_type,
        nc.is_active,
        ne.recipient,
        ne.message,
        ne.delivery_attempts
    INTO
        v_type,
        v_active,
        v_recipient,
        v_message,
        v_attempts
    FROM notification_events ne
    JOIN notification_channels nc
        ON nc.channel_id = ne.channel_id
    WHERE ne.notification_id = p_notification_id
    FOR UPDATE OF ne;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Notification % does not exist',
            p_notification_id;
    END IF;

    IF NOT v_active THEN
        RAISE EXCEPTION 'Notification channel is inactive';
    END IF;

    IF v_attempts >= 5 THEN
        RAISE EXCEPTION 'Maximum delivery attempts exceeded';
    END IF;

    /*
    Each channel type has its own validation and dispatch rule.
    A real integration would hand the event to a secured worker.
    */

    CASE v_type

        WHEN 'email' THEN

            IF v_recipient ~
                '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
            THEN
                v_valid := EXISTS (
                    SELECT 1
                    FROM email_channels
                    WHERE channel_id = (
                        SELECT channel_id
                        FROM notification_events
                        WHERE notification_id = p_notification_id
                    )
                );
            END IF;

        WHEN 'sms' THEN

            IF v_recipient ~ '^\+?[1-9][0-9]{7,14}$'
            THEN
                v_valid := EXISTS (
                    SELECT 1
                    FROM sms_channels
                    WHERE channel_id = (
                        SELECT channel_id
                        FROM notification_events
                        WHERE notification_id = p_notification_id
                    )
                );
            END IF;

        WHEN 'webhook' THEN

            IF v_recipient ~ '^https://'
            THEN
                v_valid := EXISTS (
                    SELECT 1
                    FROM webhook_channels
                    WHERE channel_id = (
                        SELECT channel_id
                        FROM notification_events
                        WHERE notification_id = p_notification_id
                    )
                );
            END IF;

    END CASE;

    IF NOT v_valid THEN
        UPDATE notification_events
        SET delivery_attempts = delivery_attempts + 1
        WHERE notification_id = p_notification_id;

        RETURN 'VALIDATION_FAILED';
    END IF;

    UPDATE notification_events
    SET
        delivery_attempts = delivery_attempts + 1,
        delivered = TRUE
    WHERE notification_id = p_notification_id;

    RETURN 'DELIVERED';

END;
$$;


/* ============================================================
   15. PULL REQUEST APPROVAL EVALUATION
   ============================================================ */

CREATE OR REPLACE FUNCTION count_current_approvals(
    p_pull_request_id BIGINT
)
RETURNS INTEGER
LANGUAGE sql
STABLE
AS $$
    SELECT COUNT(DISTINCT r.reviewer_id)::INTEGER
    FROM reviews r
    JOIN pull_requests pr
        ON pr.pull_request_id = r.pull_request_id
    JOIN reviewer_assignments ra
        ON ra.pull_request_id = r.pull_request_id
       AND ra.reviewer_id = r.reviewer_id
    JOIN repository_members rm
        ON rm.repository_id = ra.repository_id
       AND rm.user_id = r.reviewer_id
    WHERE r.pull_request_id = p_pull_request_id
      AND r.review_status = 'approved'
      AND r.reviewed_commit = pr.head_commit
      AND ra.is_eligible = TRUE
      AND rm.repository_role IN (
          'reviewer',
          'maintainer',
          'administrator'
      )
      AND rm.user_id <> pr.author_id
      AND rm.repository_id = pr.repository_id
      AND rm.can_bypass_protection = FALSE;
$$;


/* ============================================================
   16. BRANCH PROTECTION POLICY MATCHING
   ============================================================ */

CREATE OR REPLACE FUNCTION matching_protection_policy(
    p_repository_id BIGINT,
    p_branch_name TEXT
)
RETURNS BIGINT
LANGUAGE sql
STABLE
AS $$
    SELECT policy_id
    FROM branch_protection_policies
    WHERE repository_id = p_repository_id
      AND enabled = TRUE
      AND (
          branch_pattern = p_branch_name
          OR
          branch_pattern = '*'
      )
    ORDER BY
        CASE
            WHEN branch_pattern = p_branch_name THEN 0
            ELSE 1
        END
    LIMIT 1;
$$;


/* ============================================================
   17. MERGE ELIGIBILITY FUNCTION
   ============================================================ */

CREATE OR REPLACE FUNCTION evaluate_merge_eligibility(
    p_pull_request_id BIGINT
)
RETURNS JSONB
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_pr pull_requests%ROWTYPE;
    v_target branches%ROWTYPE;
    v_policy_id BIGINT;
    v_required_reviews INTEGER;
    v_actual_reviews INTEGER;
    v_violations JSONB := '[]'::jsonb;
    v_policy branch_protection_policies%ROWTYPE;
    v_missing_checks TEXT[];
    v_unresolved_count INTEGER;
    v_result JSONB;
BEGIN

    SELECT *
    INTO v_pr
    FROM pull_requests
    WHERE pull_request_id = p_pull_request_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Pull Request % not found',
            p_pull_request_id;
    END IF;

    SELECT *
    INTO v_target
    FROM branches
    WHERE branch_id = v_pr.target_branch_id
      AND repository_id = v_pr.repository_id;

    IF NOT FOUND OR v_target.is_deleted THEN
        RAISE EXCEPTION 'Target branch is unavailable';
    END IF;

    IF v_pr.state <> 'open' THEN
        v_violations := v_violations ||
            jsonb_build_array('Pull Request is not open');
    END IF;

    IF v_pr.is_draft THEN
        v_violations := v_violations ||
            jsonb_build_array('Draft Pull Request cannot be merged');
    END IF;

    IF v_pr.head_commit = v_pr.base_commit THEN
        v_violations := v_violations ||
            jsonb_build_array('Pull Request contains no distinct changes');
    END IF;

    IF v_target.head_commit <> v_pr.base_commit THEN
        v_violations := v_violations ||
            jsonb_build_array('Target branch has changed; synchronize first');
    END IF;

    v_policy_id := matching_protection_policy(
        v_pr.repository_id,
        v_target.branch_name
    );

    IF v_policy_id IS NOT NULL THEN

        SELECT *
        INTO v_policy
        FROM branch_protection_policies
        WHERE policy_id = v_policy_id;

        v_required_reviews := v_policy.required_reviews;

        v_actual_reviews := count_current_approvals(
            p_pull_request_id
        );

        IF v_actual_reviews < v_required_reviews THEN
            v_violations := v_violations ||
                jsonb_build_array(
                    'Insufficient eligible current approvals'
                );
        END IF;

        IF v_policy.require_status_checks THEN

            SELECT ARRAY_AGG(required.check_name)
            INTO v_missing_checks
            FROM required_status_checks required
            WHERE required.policy_id = v_policy_id
              AND NOT EXISTS (
                  SELECT 1
                  FROM status_checks sc
                  WHERE sc.pull_request_id = p_pull_request_id
                    AND sc.check_name = required.check_name
                    AND sc.tested_commit = v_pr.head_commit
                    AND sc.check_status = 'passed'
              );

            IF COALESCE(array_length(v_missing_checks, 1), 0) > 0 THEN
                v_violations := v_violations ||
                    jsonb_build_array(
                        'Required status checks missing or failed'
                    );
            END IF;

        END IF;

        IF v_policy.require_resolved_conversations THEN

            SELECT COUNT(*)
            INTO v_unresolved_count
            FROM review_comments rc
            JOIN reviews r
                ON r.review_id = rc.review_id
            WHERE r.pull_request_id = p_pull_request_id
              AND rc.conversation_status = 'open';

            IF v_unresolved_count > 0
               OR NOT v_pr.conversations_resolved
            THEN
                v_violations := v_violations ||
                    jsonb_build_array(
                        'Unresolved review conversations'
                    );
            END IF;

        END IF;

        IF v_policy.require_linear_history
           AND v_pr.merge_strategy = 'merge_commit'
        THEN
            v_violations := v_violations ||
                jsonb_build_array(
                    'Merge strategy violates linear-history policy'
                );
        END IF;

    END IF;

    v_result := jsonb_build_object(
        'pull_request_id', p_pull_request_id,
        'eligible', jsonb_array_length(v_violations) = 0,
        'violations', v_violations,
        'current_approvals',
            count_current_approvals(p_pull_request_id),
        'policy_id', v_policy_id,
        'evaluated_at', NOW()
    );

    RETURN v_result;

END;
$$;


/* ============================================================
   18. REVIEW COMMENT RESOLUTION TRIGGER
   ============================================================ */

CREATE OR REPLACE FUNCTION validate_comment_resolution()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF NEW.conversation_status = 'resolved' THEN

        IF NEW.resolved_by IS NULL OR NEW.resolved_at IS NULL THEN
            RAISE EXCEPTION
                'Resolved conversations require resolver and timestamp';
        END IF;

    ELSE

        NEW.resolved_by := NULL;
        NEW.resolved_at := NULL;

    END IF;

    RETURN NEW;

END;
$$;

CREATE TRIGGER trg_validate_comment_resolution
BEFORE INSERT OR UPDATE ON review_comments
FOR EACH ROW
EXECUTE FUNCTION validate_comment_resolution();


/* ============================================================
   19. PULL REQUEST STATE VALIDATION TRIGGER
   ============================================================ */

CREATE OR REPLACE FUNCTION validate_pull_request_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF TG_OP = 'UPDATE' THEN

        IF OLD.state = 'merged' THEN
            RAISE EXCEPTION
                'Merged Pull Requests are immutable';
        END IF;

        IF NEW.state = 'merged' THEN

            IF OLD.state <> 'open' THEN
                RAISE EXCEPTION
                    'Only open Pull Requests can be merged';
            END IF;

            NEW.merged_at := NOW();

        ELSIF NEW.state <> 'merged' THEN

            NEW.merged_at := NULL;

        END IF;

        NEW.updated_at := NOW();

    END IF;

    RETURN NEW;

END;
$$;

CREATE TRIGGER trg_validate_pull_request_transition
BEFORE UPDATE ON pull_requests
FOR EACH ROW
EXECUTE FUNCTION validate_pull_request_transition();


/* ============================================================
   20. MERGE PROCESSING PROCEDURE
   ============================================================ */

CREATE OR REPLACE PROCEDURE merge_pull_request(
    p_pull_request_id BIGINT,
    p_actor_id BIGINT,
    p_strategy merge_strategy
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_pr pull_requests%ROWTYPE;
    v_target branches%ROWTYPE;
    v_evaluation JSONB;
    v_new_commit TEXT;
BEGIN

    SELECT *
    INTO v_pr
    FROM pull_requests
    WHERE pull_request_id = p_pull_request_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Pull Request not found';
    END IF;

    SELECT *
    INTO v_target
    FROM branches
    WHERE branch_id = v_pr.target_branch_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Target branch not found';
    END IF;

    /*
    Eligibility is recalculated immediately before merge.
    A previous successful evaluation is not sufficient because
    approvals, checks, and branch state may have changed.
    */

    UPDATE pull_requests
    SET merge_strategy = p_strategy
    WHERE pull_request_id = p_pull_request_id;

    SELECT evaluate_merge_eligibility(p_pull_request_id)
    INTO v_evaluation;

    IF NOT (v_evaluation ->> 'eligible')::BOOLEAN THEN
        RAISE EXCEPTION
            'Merge rejected: %',
            v_evaluation -> 'violations';
    END IF;

    IF v_target.is_protected THEN

        IF NOT EXISTS (
            SELECT 1
            FROM repository_members
            WHERE repository_id = v_pr.repository_id
              AND user_id = p_actor_id
              AND repository_role IN (
                  'administrator',
                  'maintainer'
              )
        ) THEN
            RAISE EXCEPTION
                'Actor lacks merge permission';
        END IF;

    END IF;

    v_new_commit :=
        'merged-' || p_pull_request_id || '-' ||
        substring(v_pr.head_commit FROM 1 FOR 12);

    UPDATE branches
    SET
        head_commit = v_new_commit,
        updated_at = NOW()
    WHERE branch_id = v_pr.target_branch_id
      AND head_commit = v_pr.base_commit;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Concurrent branch update detected';
    END IF;

    UPDATE pull_requests
    SET
        state = 'merged',
        is_draft = FALSE,
        merged_at = NOW(),
        merge_strategy = p_strategy
    WHERE pull_request_id = p_pull_request_id;

    INSERT INTO merge_evaluations (
        pull_request_id,
        evaluated_by,
        is_eligible,
        violations
    )
    VALUES (
        p_pull_request_id,
        p_actor_id,
        TRUE,
        '[]'::jsonb
    );

END;
$$;


/* ============================================================
   21. REPORTING VIEW
   ============================================================ */

CREATE VIEW pull_request_governance_report AS
SELECT
    pr.pull_request_id,
    repo.repository_name,
    pr.title,
    pr.state,
    pr.is_draft,
    source.branch_name AS source_branch,
    target.branch_name AS target_branch,
    pr.base_commit,
    pr.head_commit,

    COUNT(DISTINCT r.review_id) FILTER (
        WHERE r.review_status = 'approved'
          AND r.reviewed_commit = pr.head_commit
    ) AS current_approval_records,

    COUNT(DISTINCT sc.status_check_id) FILTER (
        WHERE sc.check_status = 'passed'
          AND sc.tested_commit = pr.head_commit
    ) AS passed_current_checks,

    COUNT(DISTINCT rc.comment_id) FILTER (
        WHERE rc.conversation_status = 'open'
    ) AS unresolved_conversations,

    target.is_protected

FROM pull_requests pr

JOIN repositories repo
    ON repo.repository_id = pr.repository_id

JOIN branches source
    ON source.branch_id = pr.source_branch_id

JOIN branches target
    ON target.branch_id = pr.target_branch_id

LEFT JOIN reviews r
    ON r.pull_request_id = pr.pull_request_id

LEFT JOIN status_checks sc
    ON sc.pull_request_id = pr.pull_request_id

LEFT JOIN review_comments rc
    ON rc.review_id = r.review_id

GROUP BY
    pr.pull_request_id,
    repo.repository_name,
    source.branch_name,
    target.branch_name,
    target.is_protected;


/* ============================================================
   22. SAMPLE DATA
   ============================================================ */

INSERT INTO repositories (
    repository_name,
    owner_name,
    default_branch
)
VALUES (
    'secure-inventory',
    'engineering',
    'main'
);

INSERT INTO users (
    username,
    email
)
VALUES
    ('developer1', 'developer1@example.com'),
    ('reviewer1', 'reviewer1@example.com'),
    ('reviewer2', 'reviewer2@example.com'),
    ('administrator1', 'admin@example.com');

INSERT INTO repository_members (
    repository_id,
    user_id,
    repository_role,
    can_bypass_protection
)
SELECT
    r.repository_id,
    u.user_id,
    CASE u.username
        WHEN 'developer1' THEN 'developer'
        WHEN 'reviewer1' THEN 'reviewer'
        WHEN 'reviewer2' THEN 'maintainer'
        ELSE 'administrator'
    END,
    FALSE
FROM repositories r
CROSS JOIN users u
WHERE r.repository_name = 'secure-inventory';


INSERT INTO branches (
    repository_id,
    branch_name,
    head_commit,
    is_protected
)
SELECT
    repository_id,
    'main',
    'commit-100',
    TRUE
FROM repositories
WHERE repository_name = 'secure-inventory';

INSERT INTO branches (
    repository_id,
    branch_name,
    head_commit,
    is_protected
)
SELECT
    repository_id,
    'feature/inventory',
    'commit-105',
    FALSE
FROM repositories
WHERE repository_name = 'secure-inventory';


INSERT INTO commits (
    repository_id,
    commit_hash,
    author_id,
    commit_message
)
SELECT
    r.repository_id,
    v.hash,
    u.user_id,
    v.message
FROM repositories r
CROSS JOIN users u
CROSS JOIN (
    VALUES
        ('commit-100', 'Initial repository setup'),
        ('commit-104', 'Add inventory service'),
        ('commit-105', 'Add input validation'),
        ('commit-200', 'Experimental security change')
) AS v(hash, message)
WHERE r.repository_name = 'secure-inventory'
  AND u.username = 'developer1';


INSERT INTO branch_commits (
    branch_id,
    commit_id,
    sequence_number
)
SELECT
    b.branch_id,
    c.commit_id,
    1
FROM branches b
JOIN commits c
    ON c.repository_id = b.repository_id
WHERE b.branch_name = 'main'
  AND c.commit_hash = 'commit-100';


INSERT INTO branch_commits (
    branch_id,
    commit_id,
    sequence_number
)
SELECT
    b.branch_id,
    c.commit_id,
    CASE c.commit_hash
        WHEN 'commit-104' THEN 1
        WHEN 'commit-105' THEN 2
    END
FROM branches b
JOIN commits c
    ON c.repository_id = b.repository_id
WHERE b.branch_name = 'feature/inventory'
  AND c.commit_hash IN ('commit-104', 'commit-105');


/* ============================================================
   23. CREATE VALID AND FAILURE-STATE PULL REQUESTS
   ============================================================ */

INSERT INTO pull_requests (
    repository_id,
    source_branch_id,
    target_branch_id,
    author_id,
    title,
    description,
    base_commit,
    head_commit,
    state,
    is_draft,
    conversations_resolved
)
SELECT
    r.repository_id,
    source.branch_id,
    target.branch_id,
    author.user_id,
    'Add secure inventory processing',
    'Introduce inventory validation and repository safeguards.',
    'commit-100',
    'commit-105',
    'open',
    FALSE,
    TRUE
FROM repositories r
JOIN branches source
    ON source.repository_id = r.repository_id
   AND source.branch_name = 'feature/inventory'
JOIN branches target
    ON target.repository_id = r.repository_id
   AND target.branch_name = 'main'
JOIN users author
    ON author.username = 'developer1'
WHERE r.repository_name = 'secure-inventory';


INSERT INTO pull_requests (
    repository_id,
    source_branch_id,
    target_branch_id,
    author_id,
    title,
    base_commit,
    head_commit,
    state,
    is_draft,
    conversations_resolved
)
SELECT
    r.repository_id,
    source.branch_id,
    target.branch_id,
    author.user_id,
    'Experimental security modification',
    'commit-100',
    'commit-200',
    'open',
    FALSE,
    FALSE
FROM repositories r
JOIN branches source
    ON source.repository_id = r.repository_id
   AND source.branch_name = 'feature/inventory'
JOIN branches target
    ON target.repository_id = r.repository_id
   AND target.branch_name = 'main'
JOIN users author
    ON author.username = 'developer1'
WHERE r.repository_name = 'secure-inventory';


/* ============================================================
   24. REVIEWER ASSIGNMENTS
   ============================================================ */

INSERT INTO reviewer_assignments (
    repository_id,
    pull_request_id,
    reviewer_id
)
SELECT
    pr.repository_id,
    pr.pull_request_id,
    u.user_id
FROM pull_requests pr
JOIN users u
    ON u.username IN ('reviewer1', 'reviewer2');


/* ============================================================
   25. REVIEW DECISIONS
   ============================================================ */

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    reviewed_commit,
    review_status,
    review_summary
)
SELECT
    pr.pull_request_id,
    u.user_id,
    'commit-105',
    'approved',
    'Implementation and validation reviewed.'
FROM pull_requests pr
CROSS JOIN users u
WHERE pr.title = 'Add secure inventory processing'
  AND u.username IN ('reviewer1', 'reviewer2');


INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    reviewed_commit,
    review_status,
    review_summary
)
SELECT
    pr.pull_request_id,
    u.user_id,
    'commit-105',
    'changes_requested',
    'Additional input validation is required.'
FROM pull_requests pr
JOIN users u
    ON u.username = 'reviewer1'
WHERE pr.title = 'Experimental security modification';


/* ============================================================
   26. INLINE REVIEW COMMENTS
   ============================================================ */

INSERT INTO review_comments (
    review_id,
    file_path,
    line_number,
    comment_body,
    conversation_status
)
SELECT
    review_id,
    'src/inventory.py',
    42,
    'Validate external inventory values.',
    'resolved'
FROM reviews
WHERE review_summary = 'Implementation and validation reviewed.'
LIMIT 1;

UPDATE review_comments
SET
    resolved_by = (
        SELECT user_id
        FROM users
        WHERE username = 'reviewer1'
    ),
    resolved_at = NOW()
WHERE comment_body = 'Validate external inventory values.';


/* ============================================================
   27. STATUS CHECK RECORDS
   ============================================================ */

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    tested_commit,
    check_status,
    completed_at,
    execution_details
)
SELECT
    pr.pull_request_id,
    check_name,
    'commit-105',
    'passed',
    NOW(),
    jsonb_build_object(
        'runner', 'ci-runner-01',
        'duration_seconds', 18
    )
FROM pull_requests pr
CROSS JOIN (
    VALUES
        ('unit-tests'),
        ('security-scan'),
        ('build')
) AS checks(check_name)
WHERE pr.title = 'Add secure inventory processing';


INSERT INTO status_checks (
    pull_request_id,
    check_name,
    tested_commit,
    check_status,
    completed_at
)
SELECT
    pr.pull_request_id,
    'unit-tests',
    'commit-200',
    'failed',
    NOW()
FROM pull_requests pr
WHERE pr.title = 'Experimental security modification';


/* ============================================================
   28. PROTECTION POLICY CONFIGURATION
   ============================================================ */

INSERT INTO branch_protection_policies (
    repository_id,
    branch_pattern,
    required_reviews,
    require_status_checks,
    require_resolved_conversations,
    require_linear_history,
    prohibit_direct_push,
    prohibit_force_push,
    prohibit_branch_deletion,
    allow_bypass
)
SELECT
    repository_id,
    'main',
    2,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    FALSE
FROM repositories
WHERE repository_name = 'secure-inventory';


INSERT INTO required_status_checks (
    policy_id,
    check_name
)
SELECT
    policy_id,
    check_name
FROM branch_protection_policies
CROSS JOIN (
    VALUES
        ('unit-tests'),
        ('security-scan'),
        ('build')
) AS required(check_name)
WHERE branch_pattern = 'main';


/* ============================================================
   29. RETRIEVAL QUERIES
   ============================================================ */

-- All Pull Requests and their branch relationships.

SELECT
    pull_request_id,
    title,
    source_branch,
    target_branch,
    state
FROM pull_request_governance_report
ORDER BY pull_request_id;


-- Review decisions and their commit references.

SELECT
    pr.pull_request_id,
    u.username,
    r.review_status,
    r.reviewed_commit,
    pr.head_commit
FROM reviews r
JOIN pull_requests pr
    ON pr.pull_request_id = r.pull_request_id
JOIN users u
    ON u.user_id = r.reviewer_id
ORDER BY r.review_id;


-- Open review conversations.

SELECT
    rc.comment_id,
    rc.file_path,
    rc.line_number,
    rc.comment_body,
    rc.conversation_status
FROM review_comments rc
WHERE rc.conversation_status = 'open';


/* ============================================================
   30. VALIDATION AND ELIGIBILITY QUERIES
   ============================================================ */

SELECT
    pull_request_id,
    count_current_approvals(pull_request_id)
        AS current_eligible_approvals
FROM pull_requests;


SELECT
    pr.pull_request_id,
    evaluate_merge_eligibility(
        pr.pull_request_id
    ) AS eligibility
FROM pull_requests pr;


/* ============================================================
   31. AGGREGATION AND REPORTING
   ============================================================ */

SELECT
    state,
    COUNT(*) AS total_pull_requests,
    COUNT(*) FILTER (
        WHERE is_draft
    ) AS draft_count
FROM pull_requests
GROUP BY state
ORDER BY state;


SELECT
    r.repository_name,
    COUNT(pr.pull_request_id) AS total_requests,
    COUNT(pr.pull_request_id) FILTER (
        WHERE pr.state = 'merged'
    ) AS merged_requests,
    COUNT(pr.pull_request_id) FILTER (
        WHERE pr.state = 'open'
    ) AS open_requests
FROM repositories r
LEFT JOIN pull_requests pr
    ON pr.repository_id = r.repository_id
GROUP BY r.repository_name;


/* ============================================================
   32. CTE-BASED REVIEW QUALITY ANALYSIS
   ============================================================ */

WITH latest_reviews AS (
    SELECT DISTINCT ON (
        pull_request_id,
        reviewer_id
    )
        pull_request_id,
        reviewer_id,
        review_status,
        reviewed_commit
    FROM reviews
    ORDER BY
        pull_request_id,
        reviewer_id,
        submitted_at DESC,
        review_id DESC
)
SELECT
    pr.pull_request_id,
    pr.title,
    COUNT(*) FILTER (
        WHERE lr.review_status = 'approved'
          AND lr.reviewed_commit = pr.head_commit
    ) AS latest_current_approvals,
    COUNT(*) FILTER (
        WHERE lr.review_status = 'changes_requested'
    ) AS latest_change_requests
FROM pull_requests pr
LEFT JOIN latest_reviews lr
    ON lr.pull_request_id = pr.pull_request_id
GROUP BY
    pr.pull_request_id,
    pr.title;


/* ============================================================
   33. POLYMORPHIC NOTIFICATION SAMPLE DATA
   ============================================================ */

INSERT INTO notification_channels (
    channel_type,
    channel_name
)
VALUES
    ('email', 'Engineering Email'),
    ('sms', 'Operations SMS'),
    ('webhook', 'Security Webhook');


INSERT INTO email_channels (
    channel_id,
    sender_address
)
SELECT
    channel_id,
    'noreply@example.com'
FROM notification_channels
WHERE channel_name = 'Engineering Email';


INSERT INTO sms_channels (
    channel_id,
    sender_number
)
SELECT
    channel_id,
    '+911234567890'
FROM notification_channels
WHERE channel_name = 'Operations SMS';


INSERT INTO webhook_channels (
    channel_id,
    endpoint_url
)
SELECT
    channel_id,
    'https://hooks.example.com/security'
FROM notification_channels
WHERE channel_name = 'Security Webhook';


INSERT INTO notification_events (
    channel_id,
    recipient,
    message
)
SELECT
    channel_id,
    CASE channel_type
        WHEN 'email' THEN 'engineering@example.com'
        WHEN 'sms' THEN '+919876543210'
        WHEN 'webhook' THEN 'https://hooks.example.com/events'
    END,
    'Repository governance event.'
FROM notification_channels;


/* ============================================================
   34. POLYMORPHIC DISPATCH QUERIES
   ============================================================ */

SELECT
    ne.notification_id,
    nc.channel_type,
    dispatch_notification(ne.notification_id) AS dispatch_result
FROM notification_events ne
JOIN notification_channels nc
    ON nc.channel_id = ne.channel_id
ORDER BY ne.notification_id;


/* ============================================================
   35. NOTIFICATION AGGREGATION
   ============================================================ */

SELECT
    nc.channel_type,
    COUNT(ne.notification_id) AS total_notifications,
    COUNT(ne.notification_id) FILTER (
        WHERE ne.delivered
    ) AS delivered_notifications,
    SUM(ne.delivery_attempts) AS total_attempts
FROM notification_channels nc
LEFT JOIN notification_events ne
    ON ne.channel_id = nc.channel_id
GROUP BY nc.channel_type
ORDER BY nc.channel_type;


/* ============================================================
   36. TRANSACTIONAL MERGE DEMONSTRATION
   ============================================================ */

/*
The first Pull Request has:
- Two eligible reviewers.
- All required checks passed.
- Resolved review conversations.
- An unchanged target branch.
- An authorized maintainer executing the merge.

The procedure locks the Pull Request and target branch.
Any failure raises an exception and the transaction rolls back.
*/

DO $$
DECLARE
    v_pr_id BIGINT;
    v_actor BIGINT;
BEGIN

    SELECT pull_request_id
    INTO v_pr_id
    FROM pull_requests
    WHERE title = 'Add secure inventory processing';

    SELECT user_id
    INTO v_actor
    FROM users
    WHERE username = 'reviewer2';

    IF v_pr_id IS NULL OR v_actor IS NULL THEN
        RAISE EXCEPTION 'Required sample records are missing';
    END IF;

    CALL merge_pull_request(
        v_pr_id,
        v_actor,
        'squash'
    );

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE
            'Merge transaction failed: %',
            SQLERRM;
END;
$$;


/* ============================================================
   37. POST-MERGE STATE VERIFICATION
   ============================================================ */

SELECT
    pr.pull_request_id,
    pr.state,
    pr.merge_strategy,
    pr.merged_at,
    target.branch_name,
    target.head_commit
FROM pull_requests pr
JOIN branches target
    ON target.branch_id = pr.target_branch_id
WHERE pr.title = 'Add secure inventory processing';


/* ============================================================
   38. EXPLICIT FAILURE SCENARIO
   ============================================================ */

/*
The experimental Pull Request has:
- Insufficient approvals.
- A failed status check.
- An unresolved conversation.
- A stale base reference after the first merge.

Its merge eligibility must remain false.
*/

SELECT
    pull_request_id,
    evaluate_merge_eligibility(
        pull_request_id
    ) AS rejection_details
FROM pull_requests
WHERE title = 'Experimental security modification';


/* ============================================================
   39. PERFORMANCE AND GOVERNANCE DIAGNOSTICS
   ============================================================ */

EXPLAIN
SELECT
    pull_request_id,
    review_status,
    reviewed_commit
FROM reviews
WHERE pull_request_id = 1
  AND review_status = 'approved';


EXPLAIN
SELECT
    pull_request_id,
    check_name,
    check_status
FROM status_checks
WHERE pull_request_id = 1
  AND tested_commit = 'commit-105';


/*
Important production considerations:

1. Approval records should be immutable audit events.
2. Approval freshness must be checked against the current head commit.
3. Repository membership must be checked at evaluation time.
4. Bypass permissions require separate authorization and auditing.
5. SQL transaction locks prevent common merge races.
6. Branch synchronization requires actual commit ancestry validation.
7. This schema stores a simplified merge representation.
8. A production system must verify commit graphs and conflicts.
9. Webhook delivery must be performed by an isolated worker.
10. External network requests must not run inside database functions.
*/

COMMIT;
