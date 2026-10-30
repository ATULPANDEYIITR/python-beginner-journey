from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any
import json


# Custom exceptions carry stable error codes and structured context.
# Callers can handle a broad workflow failure or a specific failure type.
class WorkflowError(Exception):
    code = "WORKFLOW_ERROR"

    def __init__(
        self,
        message: str,
        *,
        context: dict[str, Any] | None = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.retryable = retryable

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": type(self).__name__,
            "code": self.code,
            "message": self.message,
            "context": self.context,
            "retryable": self.retryable,
        }


class ValidationError(WorkflowError):
    code = "VALIDATION_ERROR"


class NotFoundError(WorkflowError):
    code = "RESOURCE_NOT_FOUND"


class InvalidTransitionError(WorkflowError):
    code = "INVALID_STATE_TRANSITION"


class ReviewerEligibilityError(WorkflowError):
    code = "REVIEWER_NOT_ELIGIBLE"


class StaleApprovalError(WorkflowError):
    code = "STALE_APPROVAL"


class ProtectionViolationError(WorkflowError):
    code = "BRANCH_PROTECTION_VIOLATION"


class MergeConflictError(WorkflowError):
    code = "MERGE_CONFLICT"


class DiscussionResolutionError(WorkflowError):
    code = "UNRESOLVED_DISCUSSION"


class MergeEligibilityError(WorkflowError):
    code = "MERGE_NOT_ELIGIBLE"


class ConcurrencyConflictError(WorkflowError):
    code = "CONCURRENCY_CONFLICT"
    retryable = True


class PRState(str, Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    MERGED = "MERGED"


class ReviewDecision(str, Enum):
    COMMENTED = "COMMENTED"
    APPROVED = "APPROVED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    DISMISSED = "DISMISSED"


class CheckState(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class MergeStrategy(str, Enum):
    MERGE = "MERGE"
    SQUASH = "SQUASH"
    REBASE = "REBASE"


@dataclass(frozen=True)
class Commit:
    sha: str
    message: str
    parent_sha: str | None
    author: str


@dataclass
class Branch:
    name: str
    head_sha: str
    protected: bool = False
    deleted: bool = False


@dataclass(frozen=True)
class Review:
    reviewer: str
    decision: ReviewDecision
    commit_sha: str
    base_sha: str
    dismissed: bool = False


@dataclass
class ReviewComment:
    comment_id: int
    reviewer: str
    path: str
    line: int
    body: str
    resolved: bool = False


@dataclass(frozen=True)
class StatusCheck:
    name: str
    commit_sha: str
    state: CheckState
    details: str = ""


@dataclass
class BranchProtection:
    required_reviews: int = 1
    required_checks: set[str] = field(
        default_factory=lambda: {"unit-tests", "security-scan"}
    )
    require_conversation_resolution: bool = True
    require_linear_history: bool = True
    restrict_direct_push: bool = True
    restrict_force_push: bool = True
    restrict_deletion: bool = True
    dismiss_stale_reviews: bool = True
    enforce_admins: bool = True
    allow_bypass: bool = False
    bypass_users: set[str] = field(default_factory=set)
    allowed_merge_strategies: set[MergeStrategy] = field(
        default_factory=lambda: {
            MergeStrategy.SQUASH,
            MergeStrategy.REBASE,
        }
    )


@dataclass
class PullRequest:
    number: int
    title: str
    author: str
    source_branch: str
    target_branch: str
    state: PRState
    base_sha_seen: str
    version: int = 1
    requested_reviewers: set[str] = field(default_factory=set)
    reviews: list[Review] = field(default_factory=list)
    comments: list[ReviewComment] = field(default_factory=list)
    checks: dict[tuple[str, str], StatusCheck] = field(default_factory=dict)
    has_conflicts: bool = False
    merged_sha: str | None = None


class Repository:
    """In-memory repository with explicit workflow and policy enforcement."""

    def __init__(
        self,
        name: str,
        *,
        eligible_reviewers: set[str],
        protection: BranchProtection | None = None,
    ) -> None:
        self.name = self._validate_name(name)
        self.eligible_reviewers = set(eligible_reviewers)
        self.protection = protection or BranchProtection()
        self.branches: dict[str, Branch] = {}
        self.commits: dict[str, Commit] = {}
        self.pull_requests: dict[int, PullRequest] = {}
        self._commit_counter = 0
        self._comment_counter = 0
        self._pr_counter = 0

        root = self._new_commit("Initial repository state", None, "system")
        self.branches["main"] = Branch("main", root.sha, protected=True)

    @staticmethod
    def _validate_name(value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Repository name must be a non-empty string.")
        return value.strip()

    @staticmethod
    def _validate_text(value: str, field_name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(
                f"{field_name} must be a non-empty string.",
                context={"field": field_name},
            )
        return value.strip()

    def _new_commit(
        self,
        message: str,
        parent_sha: str | None,
        author: str,
    ) -> Commit:
        self._commit_counter += 1
        sha = f"{self._commit_counter:040x}"
        commit = Commit(sha, message, parent_sha, author)
        self.commits[sha] = commit
        return commit

    def _branch(self, name: str) -> Branch:
        branch = self.branches.get(name)
        if branch is None or branch.deleted:
            raise NotFoundError(
                f"Branch '{name}' does not exist.",
                context={"branch": name},
            )
        return branch

    def _pr(self, number: int) -> PullRequest:
        pr = self.pull_requests.get(number)
        if pr is None:
            raise NotFoundError(
                f"Pull Request #{number} does not exist.",
                context={"pull_request": number},
            )
        return pr

    def create_branch(self, name: str, from_branch: str = "main") -> Branch:
        name = self._validate_text(name, "branch name")
        source = self._branch(from_branch)

        if name in self.branches and not self.branches[name].deleted:
            raise ValidationError(
                f"Branch '{name}' already exists.",
                context={"branch": name},
            )

        branch = Branch(name=name, head_sha=source.head_sha)
        self.branches[name] = branch
        return branch

    def push_commit(
        self,
        branch_name: str,
        message: str,
        author: str,
        *,
        force: bool = False,
        parent_sha: str | None = None,
    ) -> Commit:
        """Apply branch-level push rules before advancing a branch."""
        branch = self._branch(branch_name)
        message = self._validate_text(message, "commit message")
        author = self._validate_text(author, "commit author")

        if branch.protected:
            is_bypass = (
                self.protection.allow_bypass
                and not self.protection.enforce_admins
                and author in self.protection.bypass_users
            )
            if self.protection.restrict_direct_push and not is_bypass:
                raise ProtectionViolationError(
                    f"Direct pushes to protected branch '{branch_name}' are prohibited.",
                    context={"branch": branch_name, "actor": author},
                )
            if force and self.protection.restrict_force_push and not is_bypass:
                raise ProtectionViolationError(
                    f"Force pushes to protected branch '{branch_name}' are prohibited.",
                    context={"branch": branch_name, "actor": author},
                )

        expected_parent = branch.head_sha
        if parent_sha is not None and parent_sha != expected_parent:
            raise ConcurrencyConflictError(
                "The branch head changed before the commit was applied.",
                context={
                    "branch": branch_name,
                    "expected_parent": expected_parent,
                    "provided_parent": parent_sha,
                },
            )

        commit = self._new_commit(message, expected_parent, author)
        branch.head_sha = commit.sha

        # Source changes increment the affected PR version. Existing reviews
        # and checks remain recorded but no longer apply to the new head SHA.
        for pr in self.pull_requests.values():
            if pr.source_branch == branch_name and pr.state in {
                PRState.OPEN,
                PRState.DRAFT,
            }:
                pr.version += 1

        return commit

    def delete_branch(self, branch_name: str, actor: str) -> None:
        branch = self._branch(branch_name)
        if branch.protected and self.protection.restrict_deletion:
            is_bypass = (
                self.protection.allow_bypass
                and not self.protection.enforce_admins
                and actor in self.protection.bypass_users
            )
            if not is_bypass:
                raise ProtectionViolationError(
                    f"Deletion of protected branch '{branch_name}' is prohibited.",
                    context={"branch": branch_name, "actor": actor},
                )
        branch.deleted = True

    def create_pull_request(
        self,
        title: str,
        source_branch: str,
        target_branch: str,
        author: str,
        *,
        draft: bool = False,
    ) -> PullRequest:
        title = self._validate_text(title, "Pull Request title")
        source = self._branch(source_branch)
        target = self._branch(target_branch)

        if source_branch == target_branch:
            raise ValidationError("Source and target branches must differ.")

        if source.head_sha == target.head_sha:
            raise ValidationError(
                "The source branch has no changes relative to the target.",
                context={"source_branch": source_branch},
            )

        for existing in self.pull_requests.values():
            if (
                existing.source_branch == source_branch
                and existing.target_branch == target_branch
                and existing.state in {PRState.OPEN, PRState.DRAFT}
            ):
                raise ValidationError(
                    "An active Pull Request already exists for this branch pair.",
                    context={"existing_pull_request": existing.number},
                )

        self._pr_counter += 1
        pr = PullRequest(
            number=self._pr_counter,
            title=title,
            author=self._validate_text(author, "Pull Request author"),
            source_branch=source_branch,
            target_branch=target_branch,
            state=PRState.DRAFT if draft else PRState.OPEN,
            base_sha_seen=target.head_sha,
        )
        self.pull_requests[pr.number] = pr
        return pr

    def ready_for_review(self, number: int) -> None:
        pr = self._pr(number)
        if pr.state != PRState.DRAFT:
            raise InvalidTransitionError(
                "Only a draft Pull Request can be marked ready for review.",
                context={"pull_request": number, "state": pr.state.value},
            )
        pr.state = PRState.OPEN
        pr.version += 1

    def request_review(self, number: int, reviewer: str) -> None:
        pr = self._pr(number)
        if pr.state != PRState.OPEN:
            raise InvalidTransitionError(
                "Reviews can only be requested on an open Pull Request."
            )
        if reviewer == pr.author or reviewer not in self.eligible_reviewers:
            raise ReviewerEligibilityError(
                f"'{reviewer}' is not eligible to review this Pull Request.",
                context={"reviewer": reviewer, "pull_request": number},
            )
        pr.requested_reviewers.add(reviewer)
        pr.version += 1

    def submit_review(
        self,
        number: int,
        reviewer: str,
        decision: ReviewDecision,
    ) -> Review:
        pr = self._pr(number)
        if pr.state != PRState.OPEN:
            raise InvalidTransitionError(
                "A review can only be submitted on an open Pull Request.",
                context={"state": pr.state.value},
            )
        if reviewer == pr.author or reviewer not in self.eligible_reviewers:
            raise ReviewerEligibilityError(
                f"'{reviewer}' cannot review their own work or lacks reviewer eligibility.",
                context={"reviewer": reviewer, "author": pr.author},
            )
        if not isinstance(decision, ReviewDecision):
            raise ValidationError("The review decision is not recognized.")

        review = Review(
            reviewer=reviewer,
            decision=decision,
            commit_sha=self._branch(pr.source_branch).head_sha,
            base_sha=self._branch(pr.target_branch).head_sha,
        )
        pr.reviews.append(review)
        pr.requested_reviewers.discard(reviewer)
        pr.version += 1
        return review

    def dismiss_review(self, number: int, reviewer: str) -> None:
        pr = self._pr(number)
        matching = [
            index
            for index, review in enumerate(pr.reviews)
            if review.reviewer == reviewer and not review.dismissed
        ]
        if not matching:
            raise NotFoundError(
                "No active review by the specified reviewer exists.",
                context={"reviewer": reviewer, "pull_request": number},
            )

        index = matching[-1]
        old = pr.reviews[index]
        pr.reviews[index] = Review(
            reviewer=old.reviewer,
            decision=ReviewDecision.DISMISSED,
            commit_sha=old.commit_sha,
            base_sha=old.base_sha,
            dismissed=True,
        )
        pr.version += 1

    def add_inline_comment(
        self,
        number: int,
        reviewer: str,
        path: str,
        line: int,
        body: str,
    ) -> ReviewComment:
        pr = self._pr(number)
        if pr.state != PRState.OPEN:
            raise InvalidTransitionError(
                "Inline comments require an open Pull Request."
            )
        if reviewer == pr.author or reviewer not in self.eligible_reviewers:
            raise ReviewerEligibilityError(
                "The commenter is not an eligible reviewer.",
                context={"reviewer": reviewer},
            )
        if line < 1:
            raise ValidationError("Comment line numbers must be positive.")

        path = self._validate_text(path, "file path")
        body = self._validate_text(body, "comment body")
        self._comment_counter += 1
        comment = ReviewComment(
            comment_id=self._comment_counter,
            reviewer=reviewer,
            path=path,
            line=line,
            body=body,
        )
        pr.comments.append(comment)
        pr.version += 1
        return comment

    def resolve_comment(self, number: int, comment_id: int) -> None:
        pr = self._pr(number)
        for comment in pr.comments:
            if comment.comment_id == comment_id:
                comment.resolved = True
                pr.version += 1
                return
        raise NotFoundError(
            f"Review comment {comment_id} does not exist.",
            context={"pull_request": number, "comment_id": comment_id},
        )

    def set_status_check(
        self,
        number: int,
        check_name: str,
        state: CheckState,
        details: str = "",
        *,
        commit_sha: str | None = None,
    ) -> StatusCheck:
        pr = self._pr(number)
        if pr.state != PRState.OPEN:
            raise InvalidTransitionError(
                "Status checks can only be updated for open Pull Requests."
            )

        current_head = self._branch(pr.source_branch).head_sha
        tested_sha = commit_sha or current_head
        if tested_sha != current_head:
            raise StaleApprovalError(
                "A status check must refer to the current source commit.",
                context={
                    "check": check_name,
                    "tested_sha": tested_sha,
                    "current_sha": current_head,
                },
            )

        check_name = self._validate_text(check_name, "status check name")
        check = StatusCheck(check_name, tested_sha, state, details)
        pr.checks[(check_name, tested_sha)] = check
        pr.version += 1
        return check

    def synchronize_base(self, number: int, *, conflict: bool = False) -> None:
        pr = self._pr(number)
        if pr.state != PRState.OPEN:
            raise InvalidTransitionError(
                "Only an open Pull Request can synchronize its base branch."
            )

        if conflict:
            pr.has_conflicts = True
            pr.version += 1
            raise MergeConflictError(
                "Base synchronization produced merge conflicts.",
                context={"pull_request": number},
            )

        pr.base_sha_seen = self._branch(pr.target_branch).head_sha
        pr.has_conflicts = False
        pr.version += 1

    def set_conflict_state(self, number: int, has_conflicts: bool) -> None:
        pr = self._pr(number)
        pr.has_conflicts = has_conflicts
        pr.version += 1

    @staticmethod
    def _latest_reviews(pr: PullRequest) -> dict[str, Review]:
        latest: dict[str, Review] = {}
        for review in pr.reviews:
            latest[review.reviewer] = review
        return latest

    def evaluate_merge_eligibility(
        self,
        number: int,
        strategy: MergeStrategy,
        actor: str,
    ) -> dict[str, Any]:
        pr = self._pr(number)
        source = self._branch(pr.source_branch)
        target = self._branch(pr.target_branch)
        policy = self.protection
        reasons: list[str] = []

        bypass = (
            policy.allow_bypass
            and not policy.enforce_admins
            and actor in policy.bypass_users
        )

        if pr.state != PRState.OPEN:
            reasons.append(f"Pull Request state is {pr.state.value}, not OPEN.")
        if pr.state == PRState.DRAFT:
            reasons.append("Draft Pull Requests cannot be merged.")
        if pr.base_sha_seen != target.head_sha:
            reasons.append("Base branch has advanced; synchronize before merging.")
        if pr.has_conflicts:
            reasons.append("Merge conflicts must be resolved.")
        if strategy not in policy.allowed_merge_strategies:
            reasons.append(f"Merge strategy {strategy.value} is not allowed.")
        if policy.require_linear_history and strategy == MergeStrategy.MERGE:
            reasons.append("The selected strategy does not preserve linear history.")

        latest = self._latest_reviews(pr)
        current_reviews = [
            review
            for review in latest.values()
            if not review.dismissed and review.commit_sha == source.head_sha
        ]

        if policy.dismiss_stale_reviews:
            approvals = sum(
                review.decision == ReviewDecision.APPROVED
                for review in current_reviews
            )
            changes_requested = any(
                review.decision == ReviewDecision.CHANGES_REQUESTED
                for review in current_reviews
            )
        else:
            approvals = sum(
                review.decision == ReviewDecision.APPROVED
                and not review.dismissed
                for review in latest.values()
            )
            changes_requested = any(
                review.decision == ReviewDecision.CHANGES_REQUESTED
                and not review.dismissed
                for review in latest.values()
            )

        if not bypass:
            if approvals < policy.required_reviews:
                reasons.append(
                    f"Requires {policy.required_reviews} approval(s); "
                    f"only {approvals} valid approval(s) exist."
                )
            if changes_requested:
                reasons.append("An active reviewer has requested changes.")

            missing_checks = []
            for required_name in sorted(policy.required_checks):
                check = pr.checks.get((required_name, source.head_sha))
                if check is None or check.state != CheckState.SUCCESS:
                    missing_checks.append(required_name)
            if missing_checks:
                reasons.append(
                    "Required checks are missing or unsuccessful: "
                    + ", ".join(missing_checks)
                )

            if policy.require_conversation_resolution:
                unresolved = [
                    comment.comment_id
                    for comment in pr.comments
                    if not comment.resolved
                ]
                if unresolved:
                    reasons.append(
                        f"{len(unresolved)} review conversation(s) remain unresolved."
                    )

        return {
            "eligible": not reasons,
            "pull_request": number,
            "source_head": source.head_sha,
            "target_head": target.head_sha,
            "approvals": approvals,
            "required_approvals": policy.required_reviews,
            "bypass_applied": bypass,
            "strategy": strategy.value,
            "reasons": reasons,
            "version": pr.version,
        }

    def merge(
        self,
        number: int,
        strategy: MergeStrategy,
        actor: str,
        *,
        expected_version: int | None = None,
    ) -> Commit:
        pr = self._pr(number)

        # Optimistic concurrency prevents a client from merging a state
        # different from the one it inspected.
        if expected_version is not None and expected_version != pr.version:
            raise ConcurrencyConflictError(
                "Pull Request changed after eligibility was inspected.",
                context={
                    "expected_version": expected_version,
                    "current_version": pr.version,
                },
            )

        report = self.evaluate_merge_eligibility(number, strategy, actor)
        if not report["eligible"]:
            raise MergeEligibilityError(
                "The Pull Request does not satisfy merge requirements.",
                context={"reasons": report["reasons"]},
            )

        target = self._branch(pr.target_branch)
        source = self._branch(pr.source_branch)
        parent = target.head_sha

        if strategy == MergeStrategy.MERGE:
            commit = self._new_commit(
                f"Merge Pull Request #{number}: {pr.title}",
                parent,
                actor,
            )
        elif strategy == MergeStrategy.SQUASH:
            commit = self._new_commit(
                f"Squash Pull Request #{number}: {pr.title}",
                parent,
                actor,
            )
        else:
            commit = self._new_commit(
                f"Rebase Pull Request #{number}: {pr.title}",
                parent,
                actor,
            )

        # The protected branch changes only through this policy-checked
        # merge path, not through the public direct-push method.
        target.head_sha = commit.sha
        pr.merged_sha = commit.sha
        pr.state = PRState.MERGED
        pr.version += 1

        # Keep the source branch object available for audit and reopen rules.
        _ = source
        return commit

    def close_pull_request(self, number: int) -> None:
        pr = self._pr(number)
        if pr.state not in {PRState.OPEN, PRState.DRAFT}:
            raise InvalidTransitionError(
                "Only an open or draft Pull Request can be closed.",
                context={"state": pr.state.value},
            )
        pr.state = PRState.CLOSED
        pr.version += 1

    def reopen_pull_request(self, number: int) -> None:
        pr = self._pr(number)
        if pr.state != PRState.CLOSED:
            raise InvalidTransitionError(
                "Only a closed, unmerged Pull Request can be reopened.",
                context={"state": pr.state.value},
            )
        pr.state = PRState.OPEN
        pr.version += 1


def demonstrate_custom_exceptions() -> None:
    """Run a complete repository workflow and exercise failure handling."""
    repository = Repository(
        "acme/payments",
        eligible_reviewers={"bob", "carol", "dave"},
        protection=BranchProtection(
            required_reviews=1,
            required_checks={"unit-tests", "security-scan"},
            require_conversation_resolution=True,
            require_linear_history=True,
        ),
    )

    repository.create_branch("feature/refund-validation")
    repository.push_commit(
        "feature/refund-validation",
        "Validate refund request amounts",
        "alice",
    )

    pr = repository.create_pull_request(
        "Add refund validation",
        "feature/refund-validation",
        "main",
        "alice",
        draft=True,
    )
    repository.ready_for_review(pr.number)
    repository.request_review(pr.number, "bob")

    comment = repository.add_inline_comment(
        pr.number,
        "bob",
        "payments/refunds.py",
        42,
        "Reject negative refund values before processing.",
    )
    repository.resolve_comment(pr.number, comment.comment_id)

    repository.set_status_check(
        pr.number, "unit-tests", CheckState.SUCCESS, "148 tests passed"
    )
    repository.set_status_check(
        pr.number, "security-scan", CheckState.SUCCESS, "No critical findings"
    )
    repository.submit_review(pr.number, "bob", ReviewDecision.APPROVED)

    report = repository.evaluate_merge_eligibility(
        pr.number, MergeStrategy.SQUASH, "alice"
    )
    print("Eligibility report:")
    print(json.dumps(report, indent=2))

    merged_commit = repository.merge(
        pr.number,
        MergeStrategy.SQUASH,
        "alice",
        expected_version=pr.version,
    )
    print(f"\nMerged Pull Request #{pr.number} as {merged_commit.sha[:12]}.")

    # Direct writes to protected branches produce a specific exception.
    try:
        repository.push_commit("main", "Bypass review", "alice")
    except ProtectionViolationError as error:
        print("\nProtected branch rejection:")
        print(json.dumps(error.to_dict(), indent=2))

    # Self-review is a different failure with a different recovery path.
    repository.create_branch("feature/second-change")
    repository.push_commit(
        "feature/second-change",
        "Add a second payment validation rule",
        "alice",
    )
    second_pr = repository.create_pull_request(
        "Add payment validation rule",
        "feature/second-change",
        "main",
        "alice",
    )
    try:
        repository.submit_review(
            second_pr.number, "alice", ReviewDecision.APPROVED
        )
    except ReviewerEligibilityError as error:
        print("\nReviewer eligibility rejection:")
        print(json.dumps(error.to_dict(), indent=2))

    # A stale approval cannot satisfy a policy requiring current-head review.
    repository.request_review(second_pr.number, "bob")
    repository.submit_review(
        second_pr.number, "bob", ReviewDecision.APPROVED
    )
    repository.push_commit(
        "feature/second-change",
        "Correct the validation edge case",
        "alice",
    )
    for check_name in repository.protection.required_checks:
        repository.set_status_check(
            second_pr.number, check_name, CheckState.SUCCESS
        )

    stale_report = repository.evaluate_merge_eligibility(
        second_pr.number, MergeStrategy.SQUASH, "alice"
    )
    print("\nEligibility after a new source commit:")
    print(json.dumps(stale_report, indent=2))

    try:
        repository.merge(second_pr.number, MergeStrategy.SQUASH, "alice")
    except MergeEligibilityError as error:
        print("\nMerge rejection:")
        print(json.dumps(error.to_dict(), indent=2))


if __name__ == "__main__":
    try:
        demonstrate_custom_exceptions()
    except WorkflowError as error:
        print(json.dumps(error.to_dict(), indent=2))
        raise SystemExit(1)
