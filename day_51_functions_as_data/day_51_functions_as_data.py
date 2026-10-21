from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Iterable, Optional, TypeAlias
import hashlib
import json
import time


Function: TypeAlias = Callable[..., object]


class PullRequestState(Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


class ReviewState(Enum):
    COMMENTED = "commented"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    DISMISSED = "dismissed"


class MergeStrategy(Enum):
    MERGE_COMMIT = "merge_commit"
    SQUASH = "squash"
    REBASE = "rebase"


@dataclass(frozen=True)
class Commit:
    sha: str
    message: str
    author: str


@dataclass
class Review:
    reviewer: str
    state: ReviewState
    comments: list[str] = field(default_factory=list)
    submitted_at: float = field(default_factory=time.time)


@dataclass
class PullRequest:
    number: int
    source_branch: str
    target_branch: str
    commits: list[Commit]
    state: PullRequestState = PullRequestState.OPEN
    draft: bool = False
    reviews: list[Review] = field(default_factory=list)
    status_checks: dict[str, bool] = field(default_factory=dict)
    conversations_open: int = 0
    mergeable: bool = True
    synchronized_with_base: bool = True

    def add_review(self, review: Review) -> None:
        if self.state != PullRequestState.OPEN:
            raise ValueError("Reviews can only be submitted to an open Pull Request.")
        if not review.reviewer.strip():
            raise ValueError("Reviewer identity cannot be empty.")
        self.reviews.append(review)

    def request_changes(self, reviewer: str, comment: str) -> None:
        self.add_review(
            Review(
                reviewer=reviewer,
                state=ReviewState.CHANGES_REQUESTED,
                comments=[comment],
            )
        )

    def reopen(self) -> None:
        if self.state != PullRequestState.CLOSED:
            raise ValueError("Only a closed Pull Request can be reopened.")
        self.state = PullRequestState.OPEN

    def close(self) -> None:
        if self.state == PullRequestState.MERGED:
            raise ValueError("A merged Pull Request cannot be closed.")
        self.state = PullRequestState.CLOSED

    def synchronize(self, new_commits: Iterable[Commit]) -> None:
        if self.state != PullRequestState.OPEN:
            raise ValueError("Only an open Pull Request can be synchronized.")
        self.commits.extend(new_commits)
        self.synchronized_with_base = True
        self.mergeable = True

    def mark_conflicted(self) -> None:
        self.mergeable = False
        self.synchronized_with_base = False


@dataclass(frozen=True)
class BranchProtection:
    branch_name: str
    required_reviews: int
    required_status_checks: tuple[str, ...]
    require_conversation_resolution: bool = True
    require_linear_history: bool = False
    allow_direct_push: bool = False
    allow_force_push: bool = False
    allow_deletion: bool = False
    allow_admin_bypass: bool = False


@dataclass(frozen=True)
class Repository:
    name: str
    default_branch: str
    protected_branches: dict[str, BranchProtection]


class WorkflowEngine:
    """
    Demonstrates functions as data.

    Functions are stored in dictionaries, passed to evaluators, composed,
    filtered, and executed as policy rules. The functions themselves become
    data describing repository governance behavior.
    """

    def __init__(self) -> None:
        self.rules: dict[str, Function] = {}

    def register_rule(self, name: str, rule: Function) -> None:
        if not callable(rule):
            raise TypeError("A governance rule must be callable.")
        self.rules[name] = rule

    def evaluate(self, name: str, *args: object) -> bool:
        if name not in self.rules:
            raise KeyError(f"Unknown rule: {name}")
        result = self.rules[name](*args)
        if not isinstance(result, bool):
            raise TypeError(f"Rule '{name}' must return bool.")
        return result

    def matching_rules(
        self, context: PullRequest, repository: Repository
    ) -> list[str]:
        return [
            name
            for name, rule in self.rules.items()
            if rule(context, repository)
        ]


def has_required_reviews(pr: PullRequest, repository: Repository) -> bool:
    protection = repository.protected_branches[pr.target_branch]
    eligible_approvals = {
        review.reviewer
        for review in pr.reviews
        if review.state == ReviewState.APPROVED
    }
    return len(eligible_approvals) >= protection.required_reviews


def has_no_requested_changes(pr: PullRequest, _: Repository) -> bool:
    return not any(
        review.state == ReviewState.CHANGES_REQUESTED
        for review in pr.reviews
    )


def required_checks_pass(pr: PullRequest, repository: Repository) -> bool:
    protection = repository.protected_branches[pr.target_branch]
    return all(
        pr.status_checks.get(check_name, False)
        for check_name in protection.required_status_checks
    )


def conversations_resolved(pr: PullRequest, repository: Repository) -> bool:
    protection = repository.protected_branches[pr.target_branch]
    return (
        not protection.require_conversation_resolution
        or pr.conversations_open == 0
    )


def is_mergeable(pr: PullRequest, _: Repository) -> bool:
    return (
        pr.state == PullRequestState.OPEN
        and not pr.draft
        and pr.mergeable
        and pr.synchronized_with_base
    )


def compose(*rules: Function) -> Function:
    if not rules:
        raise ValueError("At least one rule is required.")

    def composed(*args: object) -> bool:
        return all(bool(rule(*args)) for rule in rules)

    return composed


def merge_function(
    pr: PullRequest,
    repository: Repository,
    strategy: MergeStrategy,
) -> str:
    policy = compose(
        is_mergeable,
        has_required_reviews,
        has_no_requested_changes,
        required_checks_pass,
        conversations_resolved,
    )

    if not policy(pr, repository):
        raise RuntimeError("Pull Request is not eligible for merging.")

    if strategy == MergeStrategy.SQUASH:
        result = f"PR #{pr.number} squashed into {pr.target_branch}"
    elif strategy == MergeStrategy.REBASE:
        result = f"PR #{pr.number} rebased into {pr.target_branch}"
    else:
        result = f"PR #{pr.number} merged with a merge commit"

    pr.state = PullRequestState.MERGED
    return result


def demonstrate_functional_data() -> None:
    repository = Repository(
        name="payments-service",
        default_branch="main",
        protected_branches={
            "main": BranchProtection(
                branch_name="main",
                required_reviews=2,
                required_status_checks=("unit-tests", "security-scan"),
                require_conversation_resolution=True,
                require_linear_history=True,
                allow_direct_push=False,
                allow_force_push=False,
            )
        },
    )

    commits = [
        Commit("a1b2c3d", "Implement payment validation", "alice"),
        Commit("d4e5f6a", "Add validation tests", "alice"),
    ]

    pr = PullRequest(
        number=42,
        source_branch="feature/payment-validation",
        target_branch="main",
        commits=commits,
    )

    pr.status_checks.update(
        {
            "unit-tests": True,
            "security-scan": True,
        }
    )

    pr.add_review(Review("bob", ReviewState.APPROVED))
    pr.add_review(Review("carol", ReviewState.APPROVED))

    engine = WorkflowEngine()
    engine.register_rule("mergeable", is_mergeable)
    engine.register_rule("reviews", has_required_reviews)
    engine.register_rule("no_requested_changes", has_no_requested_changes)
    engine.register_rule("status_checks", required_checks_pass)
    engine.register_rule("conversations", conversations_resolved)

    matched = engine.matching_rules(pr, repository)

    print("Registered policy functions:", list(engine.rules))
    print("Passing policy functions:", matched)

    print(
        "Required reviews:",
        engine.evaluate("reviews", pr, repository),
    )

    print(
        "Merge result:",
        merge_function(pr, repository, MergeStrategy.SQUASH),
    )

    # Functions can also be selected as ordinary data.
    transformations: list[Function] = [
        lambda value: str(value).strip(),
        lambda value: value.lower(),
        lambda value: value.replace(" ", "-"),
    ]

    branch_name = "  Feature Payment Validation  "
    for transform in transformations:
        branch_name = transform(branch_name)

    print("Transformed branch:", branch_name)

    # Functions can be serialized indirectly by storing stable names and
    # parameters rather than attempting to serialize executable code.
    policy_manifest = {
        "repository": repository.name,
        "rules": list(engine.rules.keys()),
        "merge_strategy": MergeStrategy.SQUASH.value,
    }

    print(json.dumps(policy_manifest, indent=2))

    digest = hashlib.sha256(
        json.dumps(policy_manifest, sort_keys=True).encode()
    ).hexdigest()

    print("Policy manifest SHA-256:", digest)


def demonstrate_failure_conditions() -> None:
    repository = Repository(
        name="analytics-service",
        default_branch="main",
        protected_branches={
            "main": BranchProtection(
                branch_name="main",
                required_reviews=2,
                required_status_checks=("tests",),
            )
        },
    )

    pr = PullRequest(
        number=7,
        source_branch="feature/report",
        target_branch="main",
        commits=[],
    )

    pr.status_checks["tests"] = True
    pr.add_review(Review("reviewer-a", ReviewState.APPROVED))

    try:
        merge_function(pr, repository, MergeStrategy.MERGE_COMMIT)
    except RuntimeError as exc:
        print("Expected merge failure:", exc)

    try:
        pr.add_review(Review("", ReviewState.APPROVED))
    except ValueError as exc:
        print("Expected validation failure:", exc)


if __name__ == "__main__":
    demonstrate_functional_data()
    demonstrate_failure_conditions()
