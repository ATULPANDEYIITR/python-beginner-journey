-- PostgreSQL 15+
-- Custom exception handling is implemented through application-specific
-- SQLSTATE values, structured MESSAGE/DETAIL/HINT fields, and database rules.

DROP SCHEMA IF EXISTS repo_lab CASCADE;
CREATE SCHEMA repo_lab;
SET search_path TO repo_lab, public;

CREATE TABLE repository (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT repository_name_nonempty CHECK (length(trim(repository_name)) > 0)
);

CREATE TABLE repository_member (
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id)
        ON DELETE CASCADE,
    username TEXT NOT NULL,
    member_role TEXT NOT NULL CHECK (
        member_role IN ('DEVELOPER', 'REVIEWER', 'MAINTAINER', 'ADMIN')
    ),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (repository_id, username),
    CONSTRAINT username_nonempty CHECK (length(trim(username)) > 0)
);

CREATE TABLE commit_object (
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id)
        ON DELETE CASCADE,
    commit_sha TEXT NOT NULL,
    parent_sha TEXT,
    second_parent_sha TEXT,
    author_username TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (repository_id, commit_sha),
    FOREIGN KEY (repository_id, parent_sha)
        REFERENCES commit_object(repository_id, commit_sha),
    FOREIGN KEY (repository_id, second_parent_sha)
        REFERENCES commit_object(repository_id, commit_sha),
    CONSTRAINT commit_sha_nonempty CHECK (length(trim(commit_sha)) > 0),
    CONSTRAINT commit_message_nonempty CHECK (length(trim(message)) > 0),
    CONSTRAINT commit_parent_distinct CHECK (
        second_parent_sha IS NULL OR second_parent_sha <> parent_sha
    )
);

CREATE TABLE branch (
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id)
        ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    head_sha TEXT NOT NULL,
    is_protected BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (repository_id, branch_name),
    FOREIGN KEY (repository_id, head_sha)
        REFERENCES commit_object(repository_id, commit_sha),
    CONSTRAINT branch_name_nonempty CHECK (length(trim(branch_name)) > 0)
);

CREATE TABLE pull_request (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL,
    pull_request_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    source_branch TEXT NOT NULL,
    target_branch TEXT NOT NULL,
    author_username TEXT NOT NULL,
    state TEXT NOT NULL CHECK (
        state IN ('DRAFT', 'OPEN', 'CLOSED', 'MERGED')
    ),
    base_sha_seen TEXT NOT NULL,
    has_conflicts BOOLEAN NOT NULL DEFAULT FALSE,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    merged_sha TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    merged_at TIMESTAMPTZ,
    FOREIGN KEY (repository_id, source_branch)
        REFERENCES branch(repository_id, branch_name),
    FOREIGN KEY (repository_id, target_branch)
        REFERENCES branch(repository_id, branch_name),
    FOREIGN KEY (repository_id, author_username)
        REFERENCES repository_member(repository_id, username),
    FOREIGN KEY (repository_id, merged_sha)
        REFERENCES commit_object(repository_id, commit_sha),
    UNIQUE (repository_id, pull_request_number),
    CONSTRAINT different_branches CHECK (source_branch <> target_branch),
    CONSTRAINT pull_request_title_nonempty CHECK (length(trim(title)) > 0)
);

CREATE TABLE review (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_request(pull_request_id)
        ON DELETE CASCADE,
    reviewer_username TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (
        decision IN ('COMMENTED', 'APPROVED', 'CHANGES_REQUESTED', 'DISMISSED')
    ),
    reviewed_commit_sha TEXT NOT NULL,
    reviewed_base_sha TEXT NOT NULL,
    review_body TEXT NOT NULL DEFAULT '',
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE review_comment (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_request(pull_request_id)
        ON DELETE CASCADE,
    review_id BIGINT REFERENCES review(review_id)
        ON DELETE SET NULL,
    reviewer_username TEXT NOT NULL,
    comment_type TEXT NOT NULL CHECK (
        comment_type IN ('INLINE', 'GENERAL', 'REVIEW_THREAD')
    ),
    file_path TEXT,
    line_number INTEGER,
    body TEXT NOT NULL,
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT comment_body_nonempty CHECK (length(trim(body)) > 0),
    CONSTRAINT inline_location_valid CHECK (
        comment_type <> 'INLINE'
        OR (
            file_path IS NOT NULL
            AND length(trim(file_path)) > 0
            AND line_number IS NOT NULL
            AND line_number > 0
        )
    )
);

CREATE TABLE status_check (
    status_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_request(pull_request_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    tested_commit_sha TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('PENDING', 'SUCCESS', 'FAILURE')),
    details TEXT NOT NULL DEFAULT '',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (pull_request_id, check_name, tested_commit_sha),
    CONSTRAINT check_name_nonempty CHECK (length(trim(check_name)) > 0)
);

CREATE TABLE branch_protection (
    repository_id BIGINT NOT NULL,
    branch_name TEXT NOT NULL,
    required_approvals INTEGER NOT NULL DEFAULT 1
        CHECK (required_approvals >= 0),
    require_conversation_resolution BOOLEAN NOT NULL DEFAULT TRUE,
    require_linear_history BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_direct_push BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_force_push BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_deletion BOOLEAN NOT NULL DEFAULT TRUE,
    dismiss_stale_reviews BOOLEAN NOT NULL DEFAULT TRUE,
    enforce_administrators BOOLEAN NOT NULL DEFAULT TRUE,
    allow_bypass BOOLEAN NOT NULL DEFAULT FALSE,
    allowed_merge_strategies TEXT[] NOT NULL
        DEFAULT ARRAY['SQUASH', 'REBASE']::TEXT[],
    PRIMARY KEY (repository_id, branch_name),
    FOREIGN KEY (repository_id, branch_name)
        REFERENCES branch(repository_id, branch_name)
        ON DELETE CASCADE,
    CONSTRAINT allowed_strategy_values CHECK (
        allowed_merge_strategies <@ ARRAY['MERGE', 'SQUASH', 'REBASE']::TEXT[]
    )
);

CREATE TABLE required_status_check (
    repository_id BIGINT NOT NULL,
    branch_name TEXT NOT NULL,
    check_name TEXT NOT NULL,
    PRIMARY KEY (repository_id, branch_name, check_name),
    FOREIGN KEY (repository_id, branch_name)
        REFERENCES branch_protection(repository_id, branch_name)
        ON DELETE CASCADE,
    CONSTRAINT required_check_name_nonempty CHECK (length(trim(check_name)) > 0)
);

-- Role-specific approval requirements allow a policy to require, for example,
-- at least one maintainer approval as well as a general approval count.
CREATE TABLE approval_requirement (
    repository_id BIGINT NOT NULL,
    branch_name TEXT NOT NULL,
    required_role TEXT NOT NULL CHECK (
        required_role IN ('REVIEWER', 'MAINTAINER', 'ADMIN')
    ),
    minimum_count INTEGER NOT NULL CHECK (minimum_count >= 0),
    PRIMARY KEY (repository_id, branch_name, required_role),
    FOREIGN KEY (repository_id, branch_name)
        REFERENCES branch_protection(repository_id, branch_name)
        ON DELETE CASCADE
);

CREATE INDEX idx_pull_request_repository_state
    ON pull_request(repository_id, state);

CREATE INDEX idx_review_pr_time
    ON review(pull_request_id, reviewer_username, submitted_at DESC, review_id DESC);

CREATE INDEX idx_review_comment_unresolved
    ON review_comment(pull_request_id)
    WHERE is_resolved = FALSE;

CREATE INDEX idx_status_check_pr_name_sha
    ON status_check(pull_request_id, check_name, tested_commit_sha);

-- ---------------------------------------------------------------------------
-- Custom database exception conventions
--
-- P2001: invalid input or domain validation
-- P2002: missing repository resource
-- P2003: invalid workflow state transition
-- P2004: reviewer is not eligible
-- P2005: branch protection violation
-- P2006: merge eligibility failure
-- P2007: merge conflict
-- P2008: stale or concurrent workflow state
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION guard_protected_branch_update()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_restricted BOOLEAN;
    v_internal_merge TEXT;
BEGIN
    IF NEW.head_sha IS DISTINCT FROM OLD.head_sha THEN
        v_internal_merge := current_setting(
            'repo_lab.internal_merge',
            TRUE
        );

        IF v_internal_merge IS DISTINCT FROM 'on' THEN
            SELECT restrict_direct_push
            INTO v_restricted
            FROM branch_protection
            WHERE repository_id = OLD.repository_id
              AND branch_name = OLD.branch_name;

            IF COALESCE(v_restricted, FALSE) THEN
                RAISE EXCEPTION USING
                    ERRCODE = 'P2005',
                    MESSAGE = 'Direct update of a protected branch is prohibited',
                    DETAIL = format(
                        'repository_id=%s, branch=%s',
                        OLD.repository_id,
                        OLD.branch_name
                    ),
                    HINT = 'Submit a Pull Request and use the governed merge function.';
            END IF;
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_guard_protected_branch_update
BEFORE UPDATE OF head_sha ON branch
FOR EACH ROW
EXECUTE FUNCTION guard_protected_branch_update();

CREATE OR REPLACE FUNCTION guard_protected_branch_delete()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_restricted BOOLEAN;
BEGIN
    SELECT restrict_deletion
    INTO v_restricted
    FROM branch_protection
    WHERE repository_id = OLD.repository_id
      AND branch_name = OLD.branch_name;

    IF COALESCE(v_restricted, FALSE) THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2005',
            MESSAGE = 'Deletion of a protected branch is prohibited',
            DETAIL = format('branch=%s', OLD.branch_name),
            HINT = 'Remove the protection policy through an authorized governance process first.';
    END IF;

    RETURN OLD;
END;
$$;

CREATE TRIGGER trg_guard_protected_branch_delete
BEFORE DELETE ON branch
FOR EACH ROW
EXECUTE FUNCTION guard_protected_branch_delete();

CREATE OR REPLACE FUNCTION validate_pull_request_insert()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_source_sha TEXT;
    v_target_sha TEXT;
BEGIN
    IF NEW.source_branch = NEW.target_branch THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2001',
            MESSAGE = 'Source and target branches must differ';
    END IF;

    SELECT head_sha INTO v_source_sha
    FROM branch
    WHERE repository_id = NEW.repository_id
      AND branch_name = NEW.source_branch
      AND deleted_at IS NULL;

    IF NOT FOUND THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2002',
            MESSAGE = 'Source branch does not exist or is deleted';
    END IF;

    SELECT head_sha INTO v_target_sha
    FROM branch
    WHERE repository_id = NEW.repository_id
      AND branch_name = NEW.target_branch
      AND deleted_at IS NULL;

    IF NOT FOUND THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2002',
            MESSAGE = 'Target branch does not exist or is deleted';
    END IF;

    IF v_source_sha = v_target_sha THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2001',
            MESSAGE = 'Source branch contains no changes relative to target';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM repository_member
        WHERE repository_id = NEW.repository_id
          AND username = NEW.author_username
          AND active
    ) THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2004',
            MESSAGE = 'Pull Request author is not an active repository member';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_pull_request_insert
BEFORE INSERT ON pull_request
FOR EACH ROW
EXECUTE FUNCTION validate_pull_request_insert();

CREATE OR REPLACE FUNCTION validate_review_insert()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_author TEXT;
    v_repository_id BIGINT;
    v_state TEXT;
    v_source_branch TEXT;
    v_current_head TEXT;
    v_role TEXT;
BEGIN
    SELECT author_username, repository_id, state, source_branch
    INTO v_author, v_repository_id, v_state, v_source_branch
    FROM pull_request
    WHERE pull_request_id = NEW.pull_request_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2002',
            MESSAGE = 'Pull Request does not exist';
    END IF;

    IF v_state <> 'OPEN' THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2003',
            MESSAGE = 'Reviews can only be submitted on an open Pull Request',
            DETAIL = format('current_state=%s', v_state);
    END IF;

    IF NEW.reviewer_username = v_author THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2004',
            MESSAGE = 'A Pull Request author cannot review their own change';
    END IF;

    SELECT member_role INTO v_role
    FROM repository_member
    WHERE repository_id = v_repository_id
      AND username = NEW.reviewer_username
      AND active;

    IF v_role IS NULL OR v_role NOT IN ('REVIEWER', 'MAINTAINER', 'ADMIN') THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2004',
            MESSAGE = 'Reviewer does not have an eligible repository role',
            DETAIL = format('reviewer=%s', NEW.reviewer_username);
    END IF;

    SELECT head_sha INTO v_current_head
    FROM branch
    WHERE repository_id = v_repository_id
      AND branch_name = v_source_branch;

    IF NEW.reviewed_commit_sha <> v_current_head THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2008',
            MESSAGE = 'Review targets a stale source commit',
            DETAIL = format(
                'reviewed_sha=%s, current_sha=%s',
                NEW.reviewed_commit_sha,
                v_current_head
            ),
            HINT = 'Refresh the Pull Request and review the current changeset.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_review_insert
BEFORE INSERT ON review
FOR EACH ROW
EXECUTE FUNCTION validate_review_insert();

CREATE OR REPLACE FUNCTION create_pull_request(
    p_repository_id BIGINT,
    p_title TEXT,
    p_source_branch TEXT,
    p_target_branch TEXT,
    p_author TEXT,
    p_draft BOOLEAN DEFAULT FALSE
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_number INTEGER;
    v_target_sha TEXT;
    v_pr_id BIGINT;
BEGIN
    IF p_title IS NULL OR length(trim(p_title)) = 0 THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2001',
            MESSAGE = 'Pull Request title cannot be empty';
    END IF;

    -- Serialize number allocation for this repository.
    PERFORM pg_advisory_xact_lock(p_repository_id);

    IF EXISTS (
        SELECT 1
        FROM pull_request
        WHERE repository_id = p_repository_id
          AND source_branch = p_source_branch
          AND target_branch = p_target_branch
          AND state IN ('DRAFT', 'OPEN')
    ) THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2001',
            MESSAGE = 'An active Pull Request already exists for this branch pair';
    END IF;

    SELECT head_sha INTO v_target_sha
    FROM branch
    WHERE repository_id = p_repository_id
      AND branch_name = p_target_branch
      AND deleted_at IS NULL;

    IF NOT FOUND THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2002',
            MESSAGE = 'Target branch does not exist';
    END IF;

    SELECT COALESCE(MAX(pull_request_number), 0) + 1
    INTO v_number
    FROM pull_request
    WHERE repository_id = p_repository_id;

    INSERT INTO pull_request (
        repository_id,
        pull_request_number,
        title,
        source_branch,
        target_branch,
        author_username,
        state,
        base_sha_seen
    )
    VALUES (
        p_repository_id,
        v_number,
        trim(p_title),
        p_source_branch,
        p_target_branch,
        p_author,
        CASE WHEN p_draft THEN 'DRAFT' ELSE 'OPEN' END,
        v_target_sha
    )
    RETURNING pull_request_id INTO v_pr_id;

    RETURN v_pr_id;
END;
$$;

CREATE OR REPLACE FUNCTION submit_review(
    p_pull_request_id BIGINT,
    p_reviewer TEXT,
    p_decision TEXT,
    p_body TEXT DEFAULT ''
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_repository_id BIGINT;
    v_source_branch TEXT;
    v_target_branch TEXT;
    v_head_sha TEXT;
    v_base_sha TEXT;
    v_review_id BIGINT;
BEGIN
    IF p_decision NOT IN (
        'COMMENTED', 'APPROVED', 'CHANGES_REQUESTED', 'DISMISSED'
    ) THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2001',
            MESSAGE = 'Unknown review decision';
    END IF;

    SELECT repository_id, source_branch, target_branch
    INTO v_repository_id, v_source_branch, v_target_branch
    FROM pull_request
    WHERE pull_request_id = p_pull_request_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2002',
            MESSAGE = 'Pull Request does not exist';
    END IF;

    SELECT head_sha INTO v_head_sha
    FROM branch
    WHERE repository_id = v_repository_id
      AND branch_name = v_source_branch;

    SELECT head_sha INTO v_base_sha
    FROM branch
    WHERE repository_id = v_repository_id
      AND branch_name = v_target_branch;

    INSERT INTO review (
        pull_request_id,
        reviewer_username,
        decision,
        reviewed_commit_sha,
        reviewed_base_sha,
        review_body
    )
    VALUES (
        p_pull_request_id,
        p_reviewer,
        p_decision,
        v_head_sha,
        v_base_sha,
        COALESCE(p_body, '')
    )
    RETURNING review_id INTO v_review_id;

    RETURN v_review_id;
END;
$$;

CREATE OR REPLACE FUNCTION record_status_check(
    p_pull_request_id BIGINT,
    p_check_name TEXT,
    p_state TEXT,
    p_details TEXT DEFAULT ''
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_repository_id BIGINT;
    v_source_branch TEXT;
    v_head_sha TEXT;
    v_check_id BIGINT;
BEGIN
    IF p_state NOT IN ('PENDING', 'SUCCESS', 'FAILURE') THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2001',
            MESSAGE = 'Unknown status-check state';
    END IF;

    IF p_check_name IS NULL OR length(trim(p_check_name)) = 0 THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2001',
            MESSAGE = 'Status-check name cannot be empty';
    END IF;

    SELECT repository_id, source_branch
    INTO v_repository_id, v_source_branch
    FROM pull_request
    WHERE pull_request_id = p_pull_request_id
      AND state = 'OPEN'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2003',
            MESSAGE = 'Status checks require an open Pull Request';
    END IF;

    SELECT head_sha INTO v_head_sha
    FROM branch
    WHERE repository_id = v_repository_id
      AND branch_name = v_source_branch;

    INSERT INTO status_check (
        pull_request_id,
        check_name,
        tested_commit_sha,
        state,
        details
    )
    VALUES (
        p_pull_request_id,
        trim(p_check_name),
        v_head_sha,
        p_state,
        COALESCE(p_details, '')
    )
    ON CONFLICT (pull_request_id, check_name, tested_commit_sha)
    DO UPDATE SET
        state = EXCLUDED.state,
        details = EXCLUDED.details,
        updated_at = CURRENT_TIMESTAMP
    RETURNING status_check_id INTO v_check_id;

    RETURN v_check_id;
END;
$$;

CREATE OR REPLACE FUNCTION synchronize_pull_request_base(
    p_pull_request_id BIGINT,
    p_has_conflicts BOOLEAN DEFAULT FALSE
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_repository_id BIGINT;
    v_target_branch TEXT;
    v_target_sha TEXT;
BEGIN
    SELECT repository_id, target_branch
    INTO v_repository_id, v_target_branch
    FROM pull_request
    WHERE pull_request_id = p_pull_request_id
      AND state = 'OPEN'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2003',
            MESSAGE = 'Only an open Pull Request can synchronize its base';
    END IF;

    SELECT head_sha INTO v_target_sha
    FROM branch
    WHERE repository_id = v_repository_id
      AND branch_name = v_target_branch;

    UPDATE pull_request
    SET base_sha_seen = v_target_sha,
        has_conflicts = p_has_conflicts,
        version = version + 1
    WHERE pull_request_id = p_pull_request_id;

    IF p_has_conflicts THEN
        RAISE NOTICE
            'Pull Request % synchronized with conflicts requiring resolution',
            p_pull_request_id;
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION evaluate_merge_eligibility(
    p_pull_request_id BIGINT,
    p_strategy TEXT,
    p_actor TEXT
)
RETURNS TABLE (
    eligible BOOLEAN,
    reasons TEXT[],
    valid_approvals INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_pr pull_request%ROWTYPE;
    v_source_sha TEXT;
    v_target_sha TEXT;
    v_required_approvals INTEGER;
    v_require_conversations BOOLEAN;
    v_require_linear BOOLEAN;
    v_dismiss_stale BOOLEAN;
    v_allow_bypass BOOLEAN;
    v_enforce_admins BOOLEAN;
    v_allowed_strategies TEXT[];
    v_role TEXT;
    v_bypass BOOLEAN := FALSE;
    v_reasons TEXT[] := ARRAY[]::TEXT[];
    v_approvals INTEGER := 0;
    v_changes_requested BOOLEAN := FALSE;
    v_missing_checks TEXT[];
    v_unresolved_count INTEGER;
    v_requirement RECORD;
    v_role_approvals INTEGER;
BEGIN
    SELECT * INTO v_pr
    FROM pull_request
    WHERE pull_request_id = p_pull_request_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2002',
            MESSAGE = 'Pull Request does not exist',
            DETAIL = format('pull_request_id=%s', p_pull_request_id);
    END IF;

    SELECT head_sha INTO v_source_sha
    FROM branch
    WHERE repository_id = v_pr.repository_id
      AND branch_name = v_pr.source_branch;

    SELECT head_sha INTO v_target_sha
    FROM branch
    WHERE repository_id = v_pr.repository_id
      AND branch_name = v_pr.target_branch;

    SELECT
        required_approvals,
        require_conversation_resolution,
        require_linear_history,
        dismiss_stale_reviews,
        allow_bypass,
        enforce_administrators,
        allowed_merge_strategies
    INTO
        v_required_approvals,
        v_require_conversations,
        v_require_linear,
        v_dismiss_stale,
        v_allow_bypass,
        v_enforce_admins,
        v_allowed_strategies
    FROM branch_protection
    WHERE repository_id = v_pr.repository_id
      AND branch_name = v_pr.target_branch;

    IF NOT FOUND THEN
        v_required_approvals := 0;
        v_require_conversations := FALSE;
        v_require_linear := FALSE;
        v_dismiss_stale := TRUE;
        v_allow_bypass := FALSE;
        v_enforce_admins := TRUE;
        v_allowed_strategies := ARRAY['MERGE', 'SQUASH', 'REBASE']::TEXT[];
    END IF;

    SELECT member_role INTO v_role
    FROM repository_member
    WHERE repository_id = v_pr.repository_id
      AND username = p_actor
      AND active;

    v_bypass := (
        v_allow_bypass
        AND NOT v_enforce_admins
        AND v_role = 'ADMIN'
    );

    IF v_pr.state <> 'OPEN' THEN
        v_reasons := array_append(
            v_reasons,
            format('Pull Request state is %s, not OPEN', v_pr.state)
        );
    END IF;

    IF v_pr.base_sha_seen <> v_target_sha THEN
        v_reasons := array_append(
            v_reasons,
            'Base branch has advanced and requires synchronization'
        );
    END IF;

    IF v_pr.has_conflicts THEN
        v_reasons := array_append(
            v_reasons,
            'Merge conflicts remain unresolved'
        );
    END IF;

    IF NOT (p_strategy = ANY(v_allowed_strategies)) THEN
        v_reasons := array_append(
            v_reasons,
            format('Merge strategy %s is not allowed', p_strategy)
        );
    END IF;

    IF v_require_linear AND p_strategy = 'MERGE' THEN
        v_reasons := array_append(
            v_reasons,
            'Merge strategy violates the linear-history requirement'
        );
    END IF;

    -- The latest decision from each reviewer supersedes earlier decisions.
    WITH latest_reviews AS (
        SELECT DISTINCT ON (reviewer_username)
            reviewer_username,
            decision,
            reviewed_commit_sha,
            submitted_at,
            review_id
        FROM review
        WHERE pull_request_id = p_pull_request_id
        ORDER BY reviewer_username, submitted_at DESC, review_id DESC
    )
    SELECT
        COUNT(*) FILTER (
            WHERE decision = 'APPROVED'
              AND (
                  NOT v_dismiss_stale
                  OR reviewed_commit_sha = v_source_sha
              )
        )::INTEGER,
        COALESCE(
            BOOL_OR(
                decision = 'CHANGES_REQUESTED'
                AND (
                    NOT v_dismiss_stale
                    OR reviewed_commit_sha = v_source_sha
                )
            ),
            FALSE
        )
    INTO v_approvals, v_changes_requested
    FROM latest_reviews
    WHERE decision <> 'DISMISSED';

    IF NOT v_bypass THEN
        IF v_approvals < v_required_approvals THEN
            v_reasons := array_append(
                v_reasons,
                format(
                    'Requires %s approval(s), but only %s are valid',
                    v_required_approvals,
                    v_approvals
                )
            );
        END IF;

        IF v_changes_requested THEN
            v_reasons := array_append(
                v_reasons,
                'An active review has requested changes'
            );
        END IF;

        -- Role-specific approvals are checked independently of the general count.
        FOR v_requirement IN
            SELECT required_role, minimum_count
            FROM approval_requirement
            WHERE repository_id = v_pr.repository_id
              AND branch_name = v_pr.target_branch
        LOOP
            WITH latest_role_reviews AS (
                SELECT DISTINCT ON (r.reviewer_username)
                    r.reviewer_username,
                    r.decision,
                    r.reviewed_commit_sha
                FROM review r
                WHERE r.pull_request_id = p_pull_request_id
                ORDER BY
                    r.reviewer_username,
                    r.submitted_at DESC,
                    r.review_id DESC
            )
            SELECT COUNT(*)::INTEGER
            INTO v_role_approvals
            FROM latest_role_reviews lr
            JOIN repository_member rm
              ON rm.repository_id = v_pr.repository_id
             AND rm.username = lr.reviewer_username
            WHERE rm.member_role = v_requirement.required_role
              AND rm.active
              AND lr.decision = 'APPROVED'
              AND (
                  NOT v_dismiss_stale
                  OR lr.reviewed_commit_sha = v_source_sha
              );

            IF v_role_approvals < v_requirement.minimum_count THEN
                v_reasons := array_append(
                    v_reasons,
                    format(
                        'Requires %s approval(s) from role %s; found %s',
                        v_requirement.minimum_count,
                        v_requirement.required_role,
                        v_role_approvals
                    )
                );
            END IF;
        END LOOP;

        SELECT array_agg(required.check_name ORDER BY required.check_name)
        INTO v_missing_checks
        FROM required_status_check required
        WHERE required.repository_id = v_pr.repository_id
          AND required.branch_name = v_pr.target_branch
          AND NOT EXISTS (
              SELECT 1
              FROM status_check check_result
              WHERE check_result.pull_request_id = p_pull_request_id
                AND check_result.check_name = required.check_name
                AND check_result.tested_commit_sha = v_source_sha
                AND check_result.state = 'SUCCESS'
          );

        IF v_missing_checks IS NOT NULL THEN
            v_reasons := array_append(
                v_reasons,
                'Missing or unsuccessful checks: ' ||
                array_to_string(v_missing_checks, ', ')
            );
        END IF;

        IF v_require_conversations THEN
            SELECT COUNT(*) INTO v_unresolved_count
            FROM review_comment
            WHERE pull_request_id = p_pull_request_id
              AND comment_type = 'REVIEW_THREAD'
              AND NOT is_resolved;

            IF v_unresolved_count > 0 THEN
                v_reasons := array_append(
                    v_reasons,
                    format(
                        '%s review conversation(s) remain unresolved',
                        v_unresolved_count
                    )
                );
            END IF;
        END IF;
    END IF;

    RETURN QUERY
    SELECT
        cardinality(v_reasons) = 0,
        v_reasons,
        v_approvals;
END;
$$;

CREATE OR REPLACE FUNCTION merge_pull_request(
    p_pull_request_id BIGINT,
    p_strategy TEXT,
    p_actor TEXT
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_pr pull_request%ROWTYPE;
    v_source_sha TEXT;
    v_target_sha TEXT;
    v_new_sha TEXT;
    v_eligible BOOLEAN;
    v_reasons TEXT[];
    v_actor_role TEXT;
BEGIN
    SELECT * INTO v_pr
    FROM pull_request
    WHERE pull_request_id = p_pull_request_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2002',
            MESSAGE = 'Pull Request does not exist';
    END IF;

    SELECT head_sha INTO v_source_sha
    FROM branch
    WHERE repository_id = v_pr.repository_id
      AND branch_name = v_pr.source_branch;

    SELECT head_sha INTO v_target_sha
    FROM branch
    WHERE repository_id = v_pr.repository_id
      AND branch_name = v_pr.target_branch
    FOR UPDATE;

    SELECT eligible, reasons
    INTO v_eligible, v_reasons
    FROM evaluate_merge_eligibility(
        p_pull_request_id,
        p_strategy,
        p_actor
    );

    IF NOT v_eligible THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2006',
            MESSAGE = 'Pull Request is not eligible for merging',
            DETAIL = array_to_string(v_reasons, '; '),
            HINT = 'Resolve every reported condition and reevaluate eligibility.';
    END IF;

    IF p_strategy NOT IN ('MERGE', 'SQUASH', 'REBASE') THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2001',
            MESSAGE = 'Unknown merge strategy';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM repository_member
        WHERE repository_id = v_pr.repository_id
          AND username = p_actor
          AND active
    ) THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2004',
            MESSAGE = 'Merge actor is not an active repository member';
    END IF;

    v_new_sha := md5(
        p_pull_request_id::TEXT
        || clock_timestamp()::TEXT
        || random()::TEXT
        || p_actor
    );

    INSERT INTO commit_object (
        repository_id,
        commit_sha,
        parent_sha,
        second_parent_sha,
        author_username,
        message
    )
    VALUES (
        v_pr.repository_id,
        v_new_sha,
        v_target_sha,
        CASE
            WHEN p_strategy = 'MERGE' THEN v_source_sha
            ELSE NULL
        END,
        p_actor,
        format(
            '%s Pull Request #%s: %s',
            p_strategy,
            v_pr.pull_request_number,
            v_pr.title
        )
    );

    -- This transaction-local flag allows only this governed merge function
    -- to advance a protected branch through the update trigger.
    PERFORM set_config('repo_lab.internal_merge', 'on', TRUE);

    UPDATE branch
    SET head_sha = v_new_sha
    WHERE repository_id = v_pr.repository_id
      AND branch_name = v_pr.target_branch;

    UPDATE pull_request
    SET state = 'MERGED',
        merged_sha = v_new_sha,
        merged_at = CURRENT_TIMESTAMP,
        version = version + 1
    WHERE pull_request_id = p_pull_request_id;

    PERFORM set_config('repo_lab.internal_merge', 'off', TRUE);

    RETURN v_new_sha;
END;
$$;

CREATE OR REPLACE FUNCTION close_pull_request(
    p_pull_request_id BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_state TEXT;
BEGIN
    SELECT state INTO v_state
    FROM pull_request
    WHERE pull_request_id = p_pull_request_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2002',
            MESSAGE = 'Pull Request does not exist';
    END IF;

    IF v_state NOT IN ('OPEN', 'DRAFT') THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2003',
            MESSAGE = 'Only open or draft Pull Requests can be closed',
            DETAIL = format('current_state=%s', v_state);
    END IF;

    UPDATE pull_request
    SET state = 'CLOSED',
        version = version + 1
    WHERE pull_request_id = p_pull_request_id;
END;
$$;

CREATE OR REPLACE FUNCTION reopen_pull_request(
    p_pull_request_id BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_state TEXT;
BEGIN
    SELECT state INTO v_state
    FROM pull_request
    WHERE pull_request_id = p_pull_request_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2002',
            MESSAGE = 'Pull Request does not exist';
    END IF;

    IF v_state <> 'CLOSED' THEN
        RAISE EXCEPTION USING
            ERRCODE = 'P2003',
            MESSAGE = 'Only closed Pull Requests can be reopened',
            DETAIL = format('current_state=%s', v_state);
    END IF;

    UPDATE pull_request
    SET state = 'OPEN',
        version = version + 1
    WHERE pull_request_id = p_pull_request_id;
END;
$$;

CREATE VIEW pull_request_dashboard AS
SELECT
    pr.pull_request_id,
    pr.repository_id,
    pr.pull_request_number,
    pr.title,
    pr.author_username,
    pr.source_branch,
    source.head_sha AS source_head_sha,
    pr.target_branch,
    target.head_sha AS target_head_sha,
    pr.state,
    pr.base_sha_seen,
    pr.version,
    pr.has_conflicts,
    COUNT(DISTINCT review.review_id) AS submitted_review_count,
    COUNT(DISTINCT comment.comment_id)
        FILTER (
            WHERE comment.comment_type = 'REVIEW_THREAD'
              AND NOT comment.is_resolved
        ) AS unresolved_conversation_count
FROM pull_request pr
JOIN branch source
  ON source.repository_id = pr.repository_id
 AND source.branch_name = pr.source_branch
JOIN branch target
  ON target.repository_id = pr.repository_id
 AND target.branch_name = pr.target_branch
LEFT JOIN review
  ON review.pull_request_id = pr.pull_request_id
LEFT JOIN review_comment comment
  ON comment.pull_request_id = pr.pull_request_id
GROUP BY
    pr.pull_request_id,
    source.head_sha,
    target.head_sha;

CREATE VIEW merge_eligibility_report AS
SELECT
    pr.pull_request_id,
    pr.pull_request_number,
    pr.title,
    pr.state,
    result.eligible,
    result.valid_approvals,
    result.reasons
FROM pull_request pr
CROSS JOIN LATERAL evaluate_merge_eligibility(
    pr.pull_request_id,
    'SQUASH',
    pr.author_username
) AS result;

-- ---------------------------------------------------------------------------
-- Realistic repository and workflow records
-- ---------------------------------------------------------------------------

INSERT INTO repository (repository_name)
VALUES ('acme/payments');

INSERT INTO repository_member (
    repository_id,
    username,
    member_role
)
VALUES
    (1, 'alice', 'DEVELOPER'),
    (1, 'bob', 'MAINTAINER'),
    (1, 'carol', 'REVIEWER'),
    (1, 'dave', 'ADMIN');

INSERT INTO commit_object (
    repository_id,
    commit_sha,
    parent_sha,
    author_username,
    message
)
VALUES
    (1, 'root-0001', NULL, 'system', 'Initial repository state');

INSERT INTO branch (
    repository_id,
    branch_name,
    head_sha,
    is_protected
)
VALUES
    (1, 'main', 'root-0001', TRUE),
    (1, 'feature/refund-validation', 'root-0001', FALSE),
    (1, 'feature/legacy-cleanup', 'root-0001', FALSE);

INSERT INTO commit_object (
    repository_id,
    commit_sha,
    parent_sha,
    author_username,
    message
)
VALUES
    (
        1,
        'feature-0001',
        'root-0001',
        'alice',
        'Validate refund request amounts'
    ),
    (
        1,
        'legacy-0001',
        'root-0001',
        'alice',
        'Prepare legacy payment cleanup'
    );

UPDATE branch
SET head_sha = 'feature-0001'
WHERE repository_id = 1
  AND branch_name = 'feature/refund-validation';

UPDATE branch
SET head_sha = 'legacy-0001'
WHERE repository_id = 1
  AND branch_name = 'feature/legacy-cleanup';

INSERT INTO branch_protection (
    repository_id,
    branch_name,
    required_approvals,
    require_conversation_resolution,
    require_linear_history,
    restrict_direct_push,
    restrict_force_push,
    restrict_deletion,
    dismiss_stale_reviews,
    enforce_administrators,
    allow_bypass,
    allowed_merge_strategies
)
VALUES (
    1,
    'main',
    1,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    FALSE,
    ARRAY['SQUASH', 'REBASE']::TEXT[]
);

INSERT INTO required_status_check (
    repository_id,
    branch_name,
    check_name
)
VALUES
    (1, 'main', 'unit-tests'),
    (1, 'main', 'security-scan');

INSERT INTO approval_requirement (
    repository_id,
    branch_name,
    required_role,
    minimum_count
)
VALUES
    (1, 'main', 'MAINTAINER', 1);

DO $$
DECLARE
    v_pr BIGINT;
    v_second_pr BIGINT;
    v_review_id BIGINT;
    v_comment_id BIGINT;
BEGIN
    -- PR 1: complete workflow with an approval, successful checks, and
    -- a resolved review conversation.
    v_pr := create_pull_request(
        1,
        'Add refund validation',
        'feature/refund-validation',
        'main',
        'alice',
        FALSE
    );

    v_review_id := submit_review(
        v_pr,
        'bob',
        'APPROVED',
        'The boundary validation is correct.'
    );

    INSERT INTO review_comment (
        pull_request_id,
        review_id,
        reviewer_username,
        comment_type,
        file_path,
        line_number,
        body,
        is_resolved
    )
    VALUES (
        v_pr,
        v_review_id,
        'bob',
        'INLINE',
        'payments/refunds.py',
        42,
        'Check the lower amount boundary before creating a refund.',
        TRUE
    )
    RETURNING comment_id INTO v_comment_id;

    INSERT INTO review_comment (
        pull_request_id,
        review_id,
        reviewer_username,
        comment_type,
        body,
        is_resolved
    )
    VALUES (
        v_pr,
        v_review_id,
        'bob',
        'REVIEW_THREAD',
        'The validation condition has been reviewed.',
        TRUE
    );

    PERFORM record_status_check(
        v_pr,
        'unit-tests',
        'SUCCESS',
        '148 tests passed'
    );

    PERFORM record_status_check(
        v_pr,
        'security-scan',
        'SUCCESS',
        'No critical findings'
    );

    RAISE NOTICE 'PR 1 eligibility: %',
        (
            SELECT eligible
            FROM evaluate_merge_eligibility(v_pr, 'SQUASH', 'alice')
        );

    RAISE NOTICE 'PR 1 merge commit: %',
        merge_pull_request(v_pr, 'SQUASH', 'alice');

    -- PR 2: draft Pull Request illustrates an invalid merge state.
    v_second_pr := create_pull_request(
        1,
        'Clean up legacy payment processing',
        'feature/legacy-cleanup',
        'main',
        'alice',
        TRUE
    );

    BEGIN
        PERFORM merge_pull_request(
            v_second_pr,
            'SQUASH',
            'alice'
        );
    EXCEPTION
        WHEN SQLSTATE 'P2006' THEN
            RAISE NOTICE
                'Expected merge rejection for draft PR: %',
                SQLERRM;
            RAISE NOTICE 'Policy detail: %', PG_EXCEPTION_DETAIL;
    END;

    -- An author cannot approve their own Pull Request.
    BEGIN
        PERFORM submit_review(
            v_second_pr,
            'alice',
            'APPROVED',
            'Attempted self-approval'
        );
    EXCEPTION
        WHEN SQLSTATE 'P2004' THEN
            RAISE NOTICE
                'Expected reviewer eligibility rejection: %',
                SQLERRM;
    END;

    -- A direct protected-branch update must be rejected by the trigger.
    BEGIN
        UPDATE branch
        SET head_sha = 'unauthorized-sha'
        WHERE repository_id = 1
          AND branch_name = 'main';
    EXCEPTION
        WHEN SQLSTATE 'P2005' THEN
            RAISE NOTICE
                'Expected protected branch rejection: %',
                SQLERRM;
            RAISE NOTICE 'Guidance: %', PG_EXCEPTION_HINT;
    END;
END;
$$;

-- ---------------------------------------------------------------------------
-- Retrieval, validation, workflow, aggregation, and policy reporting
-- ---------------------------------------------------------------------------

-- Pull Request details and current branch heads.
SELECT *
FROM pull_request_dashboard
ORDER BY pull_request_number;

-- Review decisions and their associated source commits.
SELECT
    pr.pull_request_number,
    review.reviewer_username,
    review.decision,
    review.reviewed_commit_sha,
    review.submitted_at
FROM review
JOIN pull_request pr USING (pull_request_id)
ORDER BY pr.pull_request_number, review.submitted_at;

-- Required automated checks and their result for the current source head.
SELECT
    pr.pull_request_number,
    required.check_name,
    COALESCE(check_result.state, 'MISSING') AS current_state
FROM pull_request pr
JOIN branch source
  ON source.repository_id = pr.repository_id
 AND source.branch_name = pr.source_branch
JOIN required_status_check required
  ON required.repository_id = pr.repository_id
 AND required.branch_name = pr.target_branch
LEFT JOIN status_check check_result
  ON check_result.pull_request_id = pr.pull_request_id
 AND check_result.check_name = required.check_name
 AND check_result.tested_commit_sha = source.head_sha
ORDER BY pr.pull_request_number, required.check_name;

-- The latest review by each reviewer, with stale approvals excluded.
WITH latest_reviews AS (
    SELECT DISTINCT ON (
        review.pull_request_id,
        review.reviewer_username
    )
        review.pull_request_id,
        review.reviewer_username,
        review.decision,
        review.reviewed_commit_sha,
        review.submitted_at
    FROM review
    ORDER BY
        review.pull_request_id,
        review.reviewer_username,
        review.submitted_at DESC,
        review.review_id DESC
)
SELECT
    pr.pull_request_number,
    latest.reviewer_username,
    latest.decision,
    latest.reviewed_commit_sha = source.head_sha AS reviews_current_head
FROM latest_reviews latest
JOIN pull_request pr USING (pull_request_id)
JOIN branch source
  ON source.repository_id = pr.repository_id
 AND source.branch_name = pr.source_branch
ORDER BY pr.pull_request_number, latest.reviewer_username;

-- Policy-based eligibility reporting.
SELECT *
FROM merge_eligibility_report
ORDER BY pull_request_number;

-- Aggregate review and workflow metrics by repository.
SELECT
    repository.repository_name,
    COUNT(DISTINCT pr.pull_request_id) AS pull_request_count,
    COUNT(DISTINCT pr.pull_request_id)
        FILTER (WHERE pr.state = 'MERGED') AS merged_count,
    COUNT(DISTINCT pr.pull_request_id)
        FILTER (WHERE pr.state = 'DRAFT') AS draft_count,
    COUNT(DISTINCT review.review_id) AS review_count,
    COUNT(DISTINCT comment.comment_id)
        FILTER (
            WHERE comment.comment_type = 'REVIEW_THREAD'
              AND NOT comment.is_resolved
        ) AS unresolved_conversations
FROM repository
LEFT JOIN pull_request pr
  ON pr.repository_id = repository.repository_id
LEFT JOIN review
  ON review.pull_request_id = pr.pull_request_id
LEFT JOIN review_comment comment
  ON comment.pull_request_id = pr.pull_request_id
GROUP BY repository.repository_id, repository.repository_name;

-- Demonstrate a caught domain validation error without aborting the script.
DO $$
BEGIN
    PERFORM create_pull_request(
        1,
        '',
        'feature/legacy-cleanup',
        'main',
        'alice',
        FALSE
    );
EXCEPTION
    WHEN SQLSTATE 'P2001' THEN
        RAISE NOTICE 'Expected title validation error: %', SQLERRM;
END;
$$;

-- Transactional integrity: an invalid merge rolls back all of its writes.
-- The exception is caught outside the failed subtransaction.
DO $$
BEGIN
    BEGIN
        PERFORM merge_pull_request(
            2,
            'MERGE',
            'alice'
        );
    EXCEPTION
        WHEN SQLSTATE 'P2006' THEN
            RAISE NOTICE
                'Merge transaction rolled back after policy rejection: %',
                SQLERRM;
    END;
END;
$$;
