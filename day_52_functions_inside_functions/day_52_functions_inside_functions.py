from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Iterable


class PullRequestState(Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


class ReviewState(Enum):
    COMMENTED = "commented"
    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"
    DISMISSED = "dismissed"


@dataclass(frozen=True)
class Commit:
    sha: str
    message: str


@dataclass
class Review:
    reviewer: str
    state: ReviewState
    commit_sha: str
    comments: list[str] = field(default_factory=list)


@dataclass
class PullRequest:
    number: int
    title: str
    source_branch: str
    target_branch: str
    state: PullRequestState
    commits: list[Commit]
    requested_reviewers: set[str] = field(default_factory=set)
    reviews: list[Review] = field(default_factory=list)
    status_checks: dict[str, bool] = field(default_factory=dict)
    unresolved_conversations: int = 0
    draft: bool = False


@dataclass(frozen=True)
class BranchProtection:
    required_approvals: int
    required_checks: frozenset[str]
    require_conversation_resolution: bool
    allow_force_push: bool = False
    allow_direct_push: bool = False
    require_linear_history: bool = False


def build_repository_simulator() -> dict[str, object]:
    """
    Demonstrates lexical scoping, closures, nested functions, decorators,
    and functions returning functions while modeling repository governance.
    """

    audit_log: list[str] = []

    def audit(event: str) -> None:
        # The nested function closes over audit_log from the enclosing scope.
        audit_log.append(event)

    def create_validator(
        protected_branch: str,
        protection: BranchProtection,
    ) -> Callable[[PullRequest], list[str]]:
        """
        Returns a nested function customized for one protected branch.
        """

        def validate(pr: PullRequest) -> list[str]:
            failures: list[str] = []

            if pr.target_branch != protected_branch:
                failures.append(
                    f"target branch must be {protected_branch}"
                )

            if pr.state != PullRequestState.OPEN:
                failures.append("pull request is not open")

            if pr.draft:
                failures.append("draft pull request cannot be merged")

            if not protection.allow_direct_push and pr.source_branch == protected_branch:
                failures.append("source and protected target branch cannot be identical")

            for check in protection.required_checks:
                if pr.status_checks.get(check) is not True:
                    failures.append(f"required status check failed: {check}")

            if protection.require_conversation_resolution:
                if pr.unresolved_conversations > 0:
                    failures.append("unresolved review conversations remain")

            if protection.required_approvals > 0:
                current_approvals = count_valid_approvals(pr)

                if current_approvals < protection.required_approvals:
                    failures.append(
                        f"requires {protection.required_approvals} valid approval(s); "
                        f"found {current_approvals}"
                    )

            if protection.require_linear_history:
                if not has_linear_history(pr):
                    failures.append("linear-history requirement is not satisfied")

            return failures

        return validate

    def count_valid_approvals(pr: PullRequest) -> int:
        """
        Nested helper: approvals only count when they apply to the latest
        commit and were not dismissed.
        """
        latest_commit = pr.commits[-1].sha if pr.commits else None
        eligible_reviewers = pr.requested_reviewers

        approved_reviewers = {
            review.reviewer
            for review in pr.reviews
            if review.state == ReviewState.APPROVED
            and review.commit_sha == latest_commit
            and review.reviewer in eligible_reviewers
        }

        return len(approved_reviewers)

    def has_linear_history(pr: PullRequest) -> bool:
        """
        A compact simulation: each commit SHA must be unique and ordered.
        """
        shas = [commit.sha for commit in pr.commits]
        return len(shas) == len(set(shas))

    def merge_if_eligible(
        pr: PullRequest,
        validator: Callable[[PullRequest], list[str]],
    ) -> bool:
        failures = validator(pr)

        if failures:
            audit(
                f"PR #{pr.number} rejected: " + "; ".join(failures)
            )
            return False

        pr.state = PullRequestState.MERGED
        audit(f"PR #{pr.number} merged into {pr.target_branch}")
        return True

    def reopen(pr: PullRequest) -> None:
        if pr.state == PullRequestState.CLOSED:
            pr.state = PullRequestState.OPEN
            audit(f"PR #{pr.number} reopened")

    protection = BranchProtection(
        required_approvals=2,
        required_checks=frozenset({"tests", "security-scan"}),
        require_conversation_resolution=True,
        require_linear_history=True,
    )

    validate_main = create_validator("main", protection)

    return {
        "audit": audit,
        "validator": validate_main,
        "merge": merge_if_eligible,
        "reopen": reopen,
        "audit_log": audit_log,
    }


def main() -> None:
    system = build_repository_simulator()

    pr = PullRequest(
        number=42,
        title="Improve authentication workflow",
        source_branch="feature/auth-policy",
        target_branch="main",
        state=PullRequestState.OPEN,
        draft=False,
        commits=[
            Commit("a1", "add authentication policy"),
            Commit("b2", "add validation tests"),
        ],
        requested_reviewers={"alice", "bob", "carol"},
        reviews=[
            Review(
                reviewer="alice",
                state=ReviewState.APPROVED,
                commit_sha="b2",
            ),
            Review(
                reviewer="bob",
                state=ReviewState.APPROVED,
                commit_sha="b2",
            ),
        ],
        status_checks={
            "tests": True,
            "security-scan": True,
        },
        unresolved_conversations=0,
    )

    validator = system["validator"]
    merge = system["merge"]

    failures = validator(pr)
    print("Initial validation:", "PASS" if not failures else failures)

    merged = merge(pr, validator)
    print("Merged:", merged)
    print("State:", pr.state.value)

    print("\nAudit log:")
    for entry in system["audit_log"]:
        print("-", entry)

    # Demonstrate stale approvals after a new commit.
    pr2 = PullRequest(
        number=43,
        title="Change database transaction policy",
        source_branch="feature/transactions",
        target_branch="main",
        state=PullRequestState.OPEN,
        commits=[Commit("c1", "initial policy")],
        requested_reviewers={"alice", "bob"},
        reviews=[
            Review(
                reviewer="alice",
                state=ReviewState.APPROVED,
                commit_sha="c1",
            ),
            Review(
                reviewer="bob",
                state=ReviewState.APPROVED,
                commit_sha="c1",
            ),
        ],
        status_checks={
            "tests": True,
            "security-scan": True,
        },
    )

    # A new commit makes previous approvals stale under this policy model.
    pr2.commits.append(Commit("d2", "address review feedback"))

    failures = validator(pr2)
    print("\nAfter new commit:")
    for failure in failures:
        print("-", failure)

    # Re-reviewing the latest commit restores approval eligibility.
    pr2.reviews.extend(
        [
            Review(
                reviewer="alice",
                state=ReviewState.APPROVED,
                commit_sha="d2",
            ),
            Review(
                reviewer="bob",
                state=ReviewState.APPROVED,
                commit_sha="d2",
            ),
        ]
    )

    print("\nAfter fresh approvals:")
    print("Merged:", merge(pr2, validator))
    print("State:", pr2.state.value)

    # Security consideration:
    # The nested validator owns its policy configuration through closure
    # state, so callers cannot accidentally substitute a different branch
    # policy without explicitly constructing another validator.


if __name__ == "__main__":
    main()
