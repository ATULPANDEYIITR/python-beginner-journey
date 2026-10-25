#!/usr/bin/env python3
"""Practice: Functions through a simulated pull-request governance workflow."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable


class PullRequestState(Enum):
    DRAFT = "draft"
    OPEN = "open"
    MERGED = "merged"
    CLOSED = "closed"


class ReviewState(Enum):
    COMMENTED = "commented"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    DISMISSED = "dismissed"


@dataclass(frozen=True)
class Commit:
    sha: str
    message: str


@dataclass
class Branch:
    name: str
    commits: list[Commit] = field(default_factory=list)

    def add_commit(self, commit: Commit) -> None:
        if any(existing.sha == commit.sha for existing in self.commits):
            raise ValueError(f"Duplicate commit: {commit.sha}")
        self.commits.append(commit)


@dataclass
class Review:
    reviewer: str
    state: ReviewState
    head_sha: str
    comments: list[str] = field(default_factory=list)
    submitted_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class BranchProtection:
    required_approvals: int = 2
    required_checks: tuple[str, ...] = ("build", "tests", "security")
    require_conversation_resolution: bool = True
    require_linear_history: bool = True
    restrict_direct_push: bool = True
    allow_force_push: bool = False
    allow_deletion: bool = False
    allow_admin_bypass: bool = False


@dataclass
class PullRequest:
    number: int
    source: Branch
    target: Branch
    author: str
    reviewers: set[str]
    state: PullRequestState = PullRequestState.OPEN
    head_sha: str = ""
    base_sha: str = ""
    reviews: list[Review] = field(default_factory=list)
    checks: dict[str, bool] = field(default_factory=dict)
    unresolved_comments: int = 0
    merged_commit: str | None = None
    merge_strategy: str = "squash"
    events: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.number <= 0:
            raise ValueError("Pull request number must be positive")
        if not self.author.strip():
            raise ValueError("Author is required")
        if self.author in self.reviewers:
            raise ValueError("Author cannot review their own pull request")
        if not self.source.name or not self.target.name:
            raise ValueError("Source and target branches are required")
        self.head_sha = self.current_head()
        self.base_sha = self.current_base()
        self.events.append("Pull request opened")

    def current_head(self) -> str:
        return self.source.commits[-1].sha if self.source.commits else ""

    def current_base(self) -> str:
        return self.target.commits[-1].sha if self.target.commits else ""

    def sync_branches(self) -> None:
        self.head_sha = self.current_head()
        self.base_sha = self.current_base()
        self.events.append("Branch state synchronized")

    def mark_draft(self) -> None:
        self._require_open()
        self.state = PullRequestState.DRAFT
        self.events.append("Converted to draft")

    def ready_for_review(self) -> None:
        if self.state != PullRequestState.DRAFT:
            raise ValueError("Only draft pull requests can become ready")
        self.state = PullRequestState.OPEN
        self.events.append("Marked ready for review")

    def submit_review(
        self,
        reviewer: str,
        state: ReviewState,
        comments: list[str] | None = None,
    ) -> None:
        self._require_open()
        if reviewer not in self.reviewers:
            raise PermissionError("Reviewer is not eligible")
        if state == ReviewState.DISMISSED:
            raise ValueError("Submit a decision, not a dismissal")
        if not self.head_sha:
            raise ValueError("Cannot review an empty changeset")

        review = Review(
            reviewer=reviewer,
            state=state,
            head_sha=self.head_sha,
            comments=list(comments or []),
        )
        self.reviews.append(review)
        self.events.append(f"{reviewer} submitted {state.value}")

    def dismiss_review(self, reviewer: str) -> None:
        self._require_open()
        for review in reversed(self.reviews):
            if review.reviewer == reviewer and review.state in (
                ReviewState.APPROVED,
                ReviewState.CHANGES_REQUESTED,
            ):
                review.state = ReviewState.DISMISSED
                self.events.append(f"Review by {reviewer} dismissed")
                return
        raise ValueError("No active decision exists for this reviewer")

    def set_check(self, name: str, passed: bool) -> None:
        self._require_open()
        if not name.strip():
            raise ValueError("Check name is required")
        self.checks[name] = passed
        self.events.append(
            f"Check {name}: {'passed' if passed else 'failed'}"
        )

    def resolve_conversation(self) -> None:
        self._require_open()
        if self.unresolved_comments > 0:
            self.unresolved_comments -= 1
            self.events.append("Review conversation resolved")

    def eligible_approvals(self) -> set[str]:
        # Only each reviewer's latest decision on the current head counts.
        latest: dict[str, Review] = {}
        for review in self.reviews:
            if review.head_sha == self.head_sha:
                latest[review.reviewer] = review

        return {
            reviewer
            for reviewer, review in latest.items()
            if review.state == ReviewState.APPROVED
        }

    def merge_eligibility(
        self, policy: BranchProtection
    ) -> tuple[bool, list[str]]:
        reasons: list[str] = []

        if self.state != PullRequestState.OPEN:
            reasons.append("Pull request is not open")
            return False, reasons

        if not self.head_sha or not self.source.commits:
            reasons.append("Source branch has no commits")

        if self.head_sha != self.current_head():
            reasons.append("Source branch changed; synchronize state")

        if self.base_sha != self.current_base():
            reasons.append("Target branch changed; synchronize state")

        approvals = self.eligible_approvals()
        if len(approvals) < policy.required_approvals:
            reasons.append(
                f"Requires {policy.required_approvals} current approvals; "
                f"found {len(approvals)}"
            )

        for check in policy.required_checks:
            if self.checks.get(check) is not True:
                reasons.append(f"Required check not passing: {check}")

        if policy.require_conversation_resolution and self.unresolved_comments:
            reasons.append(
                f"{self.unresolved_comments} unresolved conversation(s)"
            )

        if policy.require_linear_history and self.merge_strategy == "merge":
            reasons.append("Merge commits are prohibited by linear-history policy")

        if self.merge_strategy not in ("merge", "squash", "rebase"):
            reasons.append("Unsupported merge strategy")

        return not reasons, reasons

    def merge(self, policy: BranchProtection) -> str:
        eligible, reasons = self.merge_eligibility(policy)
        if not eligible:
            raise RuntimeError("Merge blocked: " + "; ".join(reasons))

        self.state = PullRequestState.MERGED
        self.merged_commit = f"merge-pr-{self.number}-{self.head_sha[:8]}"
        self.target.add_commit(
            Commit(self.merged_commit, f"Merge pull request #{self.number}")
        )
        self.events.append(f"Merged using {self.merge_strategy}")
        return self.merged_commit

    def close(self) -> None:
        self._require_open()
        self.state = PullRequestState.CLOSED
        self.events.append("Pull request closed without merging")

    def reopen(self) -> None:
        if self.state != PullRequestState.CLOSED:
            raise ValueError("Only closed, unmerged pull requests can reopen")
        self.state = PullRequestState.OPEN
        self.sync_branches()
        self.events.append("Pull request reopened")

    def _require_open(self) -> None:
        if self.state != PullRequestState.OPEN:
            raise RuntimeError("Operation requires an open pull request")


def run_checks(
    checks: dict[str, Callable[[], bool]]
) -> dict[str, bool]:
    """Run independent validation functions and retain individual failures."""
    results: dict[str, bool] = {}
    for name, check in checks.items():
        try:
            results[name] = bool(check())
        except Exception as exc:
            results[name] = False
            print(f"Check {name} failed: {type(exc).__name__}: {exc}")
    return results


def build_example() -> tuple[PullRequest, BranchProtection]:
    main = Branch("main", [Commit("base001", "Initial release")])
    feature = Branch("feature/payment-validation")
    feature.add_commit(Commit("feat001", "Validate payment requests"))

    policy = BranchProtection(required_approvals=2)
    pr = PullRequest(
        number=42,
        source=feature,
        target=main,
        author="developer",
        reviewers={"reviewer-alex", "reviewer-sam", "reviewer-jordan"},
    )
    pr.unresolved_comments = 1

    pr.checks.update(
        run_checks(
            {
                "build": lambda: True,
                "tests": lambda: 120 >= 120,
                "security": lambda: True,
            }
        )
    )
    return pr, policy


def main() -> None:
    pr, policy = build_example()

    pr.submit_review(
        "reviewer-alex",
        ReviewState.APPROVED,
        ["Validation covers missing payment identifiers."],
    )
    pr.submit_review(
        "reviewer-sam",
        ReviewState.CHANGES_REQUESTED,
        ["Add a test for duplicate transaction identifiers."],
    )

    eligible, reasons = pr.merge_eligibility(policy)
    print(f"Initial merge eligibility: {eligible}")
    for reason in reasons:
        print(f"  BLOCKED: {reason}")

    pr.submit_review("reviewer-sam", ReviewState.APPROVED)
    pr.resolve_conversation()
    eligible, reasons = pr.merge_eligibility(policy)
    assert eligible, reasons

    merged_sha = pr.merge(policy)
    print(f"Merged commit: {merged_sha}")
    print(f"Final state: {pr.state.value}")

    # A merged pull request cannot be reopened as an ordinary closed PR.
    try:
        pr.reopen()
    except ValueError as exc:
        print(f"Expected lifecycle restriction: {exc}")

    # Invalid approval policy is rejected by eligibility logic in real systems;
    # this simulation validates it explicitly at the policy boundary.
    try:
        BranchProtection(required_approvals=-1)
        validate_policy(-1)
    except ValueError as exc:
        print(f"Expected policy validation: {exc}")


def validate_policy(required_approvals: int) -> None:
    if required_approvals < 0:
        raise ValueError("Required approvals cannot be negative")


if __name__ == "__main__":
    main()
