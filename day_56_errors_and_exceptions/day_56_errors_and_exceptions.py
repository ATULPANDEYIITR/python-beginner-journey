from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set


class WorkflowError(Exception):
    """Base exception for repository workflow failures."""


class ValidationError(WorkflowError):
    pass


class StateTransitionError(WorkflowError):
    pass


class PolicyViolation(WorkflowError):
    pass


class MergeConflictError(WorkflowError):
    pass


class ReviewState(Enum):
    COMMENTED = "commented"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    DISMISSED = "dismissed"


class PullRequestState(Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


class CheckState(Enum):
    PASSING = "passing"
    FAILING = "failing"
    PENDING = "pending"


@dataclass
class Commit:
    sha: str
    message: str

    def __post_init__(self) -> None:
        if len(self.sha) < 7:
            raise ValidationError("Commit SHA must contain at least seven characters.")
        if not self.message.strip():
            raise ValidationError("Commit message cannot be empty.")


@dataclass
class Branch:
    name: str
    protected: bool = False
    commits: List[Commit] = field(default_factory=list)

    def add_commit(self, commit: Commit) -> None:
        self.commits.append(commit)


@dataclass
class ReviewComment:
    reviewer: str
    body: str
    resolved: bool = False

    def resolve(self) -> None:
        self.resolved = True


@dataclass
class Review:
    reviewer: str
    state: ReviewState
    comments: List[ReviewComment] = field(default_factory=list)
    commit_sha: str = ""

    def add_comment(self, body: str) -> None:
        if not body.strip():
            raise ValidationError("Review comment cannot be empty.")
        self.comments.append(ReviewComment(self.reviewer, body))


@dataclass
class StatusCheck:
    name: str
    state: CheckState

    def passed(self) -> bool:
        return self.state == CheckState.PASSING


@dataclass
class BranchProtection:
    required_reviews: int = 1
    required_checks: Set[str] = field(default_factory=set)
    dismiss_stale_reviews: bool = True
    require_conversations_resolved: bool = True
    allow_force_push: bool = False
    allow_deletion: bool = False
    require_linear_history: bool = True

    def __post_init__(self) -> None:
        if self.required_reviews < 0:
            raise ValidationError("Required review count cannot be negative.")


@dataclass
class PullRequest:
    number: int
    source: Branch
    target: Branch
    state: PullRequestState = PullRequestState.OPEN
    draft: bool = False
    commits: List[Commit] = field(default_factory=list)
    reviews: List[Review] = field(default_factory=list)
    checks: Dict[str, StatusCheck] = field(default_factory=dict)
    changed_files: Set[str] = field(default_factory=set)

    def add_commit(self, commit: Commit) -> None:
        if self.state != PullRequestState.OPEN:
            raise StateTransitionError("Commits can only be added to an open Pull Request.")
        self.commits.append(commit)

    def request_review(self, reviewer: str) -> None:
        if self.state != PullRequestState.OPEN:
            raise StateTransitionError("Reviews cannot be requested on a closed or merged Pull Request.")
        if not reviewer.strip():
            raise ValidationError("Reviewer name cannot be empty.")

    def add_review(self, review: Review) -> None:
        if self.state != PullRequestState.OPEN:
            raise StateTransitionError("Reviews require an open Pull Request.")
        self.reviews.append(review)

    def add_check(self, check: StatusCheck) -> None:
        self.checks[check.name] = check

    def synchronize_base(self, base_commit: Commit) -> None:
        if self.state != PullRequestState.OPEN:
            raise StateTransitionError("Only open Pull Requests can be synchronized.")
        self.commits.append(base_commit)

    def reopen(self) -> None:
        if self.state != PullRequestState.CLOSED:
            raise StateTransitionError("Only closed Pull Requests can be reopened.")
        self.state = PullRequestState.OPEN

    def close(self) -> None:
        if self.state == PullRequestState.MERGED:
            raise StateTransitionError("A merged Pull Request cannot be closed.")
        self.state = PullRequestState.CLOSED


class Repository:
    def __init__(self, name: str):
        if not name.strip():
            raise ValidationError("Repository name cannot be empty.")
        self.name = name
        self.branches: Dict[str, Branch] = {}
        self.protection: Dict[str, BranchProtection] = {}
        self.pull_requests: Dict[int, PullRequest] = {}

    def add_branch(self, branch: Branch) -> None:
        if branch.name in self.branches:
            raise ValidationError(f"Branch already exists: {branch.name}")
        self.branches[branch.name] = branch

    def protect(self, branch_name: str, policy: BranchProtection) -> None:
        if branch_name not in self.branches:
            raise ValidationError(f"Unknown branch: {branch_name}")
        self.branches[branch_name].protected = True
        self.protection[branch_name] = policy

    def create_pull_request(
        self,
        number: int,
        source_name: str,
        target_name: str,
        draft: bool = False,
    ) -> PullRequest:
        if number in self.pull_requests:
            raise ValidationError(f"Pull Request #{number} already exists.")
        if source_name not in self.branches or target_name not in self.branches:
            raise ValidationError("Source and target branches must exist.")
        if source_name == target_name:
            raise ValidationError("Source and target branches must differ.")

        pr = PullRequest(
            number=number,
            source=self.branches[source_name],
            target=self.branches[target_name],
            state=PullRequestState.DRAFT if draft else PullRequestState.OPEN,
            draft=draft,
        )
        self.pull_requests[number] = pr
        return pr


class MergeEngine:
    def __init__(self, repository: Repository):
        self.repository = repository

    @staticmethod
    def _active_approvals(pr: PullRequest) -> int:
        approved_reviewers = {
            review.reviewer
            for review in pr.reviews
            if review.state == ReviewState.APPROVED
        }
        return len(approved_reviewers)

    @staticmethod
    def _unresolved_comments(pr: PullRequest) -> int:
        return sum(
            1
            for review in pr.reviews
            for comment in review.comments
            if not comment.resolved
        )

    def validate_merge(self, pr: PullRequest) -> None:
        if pr.state != PullRequestState.OPEN:
            raise StateTransitionError("Only open Pull Requests can be merged.")

        if pr.draft:
            raise PolicyViolation("Draft Pull Requests cannot be merged.")

        if not pr.commits:
            raise ValidationError("Pull Request contains no commits.")

        if not pr.changed_files:
            raise ValidationError("Pull Request contains no changed files.")

        policy = self.repository.protection.get(pr.target.name)
        if policy is None:
            return

        if self._active_approvals(pr) < policy.required_reviews:
            raise PolicyViolation(
                f"Required approvals not satisfied: "
                f"{self._active_approvals(pr)}/{policy.required_reviews}"
            )

        for check_name in policy.required_checks:
            check = pr.checks.get(check_name)
            if check is None:
                raise PolicyViolation(f"Required status check is missing: {check_name}")
            if not check.passed():
                raise PolicyViolation(f"Required status check failed: {check_name}")

        if policy.require_conversations_resolved and self._unresolved_comments(pr):
            raise PolicyViolation("Unresolved review conversations remain.")

        if policy.require_linear_history and len(pr.commits) > 1:
            # This simplified model treats a multi-commit PR as linear when all
            # commits have valid identifiers. Real Git ancestry requires DAG analysis.
            if any(len(commit.sha) < 7 for commit in pr.commits):
                raise MergeConflictError("Invalid commit ancestry detected.")

    def merge(self, pr: PullRequest) -> str:
        self.validate_merge(pr)
        pr.state = PullRequestState.MERGED
        return f"Pull Request #{pr.number} merged into {pr.target.name}."


def demonstrate() -> None:
    repository = Repository("payments-service")

    main = Branch("main")
    feature = Branch("feature/payment-validation")

    main.add_commit(Commit("abcdef1234567", "Initial production commit"))
    feature.add_commit(Commit("123456789abcd", "Add payment validation"))

    repository.add_branch(main)
    repository.add_branch(feature)

    repository.protect(
        "main",
        BranchProtection(
            required_reviews=2,
            required_checks={"unit-tests", "security-scan"},
            dismiss_stale_reviews=True,
            require_conversations_resolved=True,
            allow_force_push=False,
            allow_deletion=False,
            require_linear_history=True,
        ),
    )

    pr = repository.create_pull_request(
        101,
        "feature/payment-validation",
        "main",
    )
    pr.changed_files.update({"payment.py", "test_payment.py"})
    pr.add_commit(feature.commits[0])

    pr.add_review(Review("alice", ReviewState.APPROVED, commit_sha="123456789abcd"))
    review = Review("bob", ReviewState.COMMENTED, commit_sha="123456789abcd")
    review.add_comment("Please validate currency boundaries.")
    pr.add_review(review)

    pr.add_check(StatusCheck("unit-tests", CheckState.PASSING))
    pr.add_check(StatusCheck("security-scan", CheckState.PASSING))

    engine = MergeEngine(repository)

    try:
        engine.merge(pr)
    except WorkflowError as exc:
        print(f"Expected merge rejection: {exc}")

    review.comments[0].resolve()
    review.state = ReviewState.APPROVED

    print(engine.merge(pr))

    closed_pr = repository.create_pull_request(
        102,
        "feature/payment-validation",
        "main",
    )
    closed_pr.close()

    try:
        closed_pr.add_review(Review("alice", ReviewState.APPROVED))
    except WorkflowError as exc:
        print(f"Expected state error: {exc}")

    closed_pr.reopen()
    print(f"Reopened Pull Request #{closed_pr.number}: {closed_pr.state.value}")


if __name__ == "__main__":
    demonstrate()
