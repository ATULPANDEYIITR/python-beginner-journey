from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


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


class MergeError(Exception):
    """Raised when repository rules prevent a merge."""


@dataclass
class StatusCheck:
    name: str
    passed: bool
    required: bool = True


@dataclass
class Review:
    reviewer: str
    state: ReviewState
    commit_sha: str
    stale: bool = False


@dataclass
class BranchProtection:
    required_approvals: int = 2
    required_checks: set[str] = field(
        default_factory=lambda: {"tests", "security-scan"}
    )
    require_conversations_resolved: bool = True
    allow_force_push: bool = False
    allow_direct_push: bool = False
    require_linear_history: bool = True


@dataclass
class PullRequest:
    number: int
    source_branch: str
    target_branch: str
    commits: list[str]
    head_sha: str
    state: PullRequestState = PullRequestState.OPEN
    reviews: list[Review] = field(default_factory=list)
    checks: list[StatusCheck] = field(default_factory=list)
    unresolved_conversations: int = 0
    merge_strategy: str = "squash"
    synchronized_with_base: bool = True

    def add_review(self, review: Review) -> None:
        if self.state not in {PullRequestState.OPEN, PullRequestState.DRAFT}:
            raise ValueError("Reviews cannot be added to a closed or merged PR.")
        self.reviews.append(review)

    def approvals(self) -> int:
        return sum(
            1
            for review in self.reviews
            if review.state == ReviewState.APPROVED
            and not review.stale
        )


class Repository:
    def __init__(self, name: str, protection: BranchProtection):
        self.name = name
        self.protection = protection
        self.branches = {"main", "develop"}
        self.commits: set[str] = set()
        self.pull_requests: dict[int, PullRequest] = {}
        self.next_pr_number = 1
        self.audit_log: list[str] = []

    def create_commit(self, sha: str) -> None:
        if not sha or len(sha) < 7:
            raise ValueError("Commit SHA must contain at least seven characters.")
        if sha in self.commits:
            raise ValueError("Duplicate commit.")
        self.commits.add(sha)

    def create_pull_request(
        self,
        source_branch: str,
        target_branch: str,
        commits: list[str],
        draft: bool = False,
    ) -> PullRequest:
        if source_branch == target_branch:
            raise ValueError("Source and target branches must differ.")
        if source_branch not in self.branches:
            raise ValueError("Unknown source branch.")
        if target_branch not in self.branches:
            raise ValueError("Unknown target branch.")
        if not commits:
            raise ValueError("A pull request requires at least one commit.")
        if any(commit not in self.commits for commit in commits):
            raise ValueError("Pull request references an unknown commit.")

        pr = PullRequest(
            number=self.next_pr_number,
            source_branch=source_branch,
            target_branch=target_branch,
            commits=commits,
            head_sha=commits[-1],
            state=PullRequestState.DRAFT if draft else PullRequestState.OPEN,
        )
        self.pull_requests[pr.number] = pr
        self.next_pr_number += 1
        self.audit_log.append(f"PR-{pr.number} created")
        return pr

    def synchronize(self, pr: PullRequest) -> None:
        pr.synchronized_with_base = True
        for review in pr.reviews:
            review.stale = True
        self.audit_log.append(f"PR-{pr.number} synchronized; approvals became stale")

    def evaluate_merge(self, pr: PullRequest) -> tuple[bool, list[str]]:
        failures: list[str] = []

        if pr.state != PullRequestState.OPEN:
            failures.append("PR is not open.")

        if not pr.synchronized_with_base:
            failures.append("PR is not synchronized with the base branch.")

        required_approvals = self.protection.required_approvals
        if pr.approvals() < required_approvals:
            failures.append(
                f"Requires {required_approvals} non-stale approvals; "
                f"found {pr.approvals()}."
            )

        check_map = {check.name: check.passed for check in pr.checks}
        for required in self.protection.required_checks:
            if check_map.get(required) is not True:
                failures.append(f"Required status check failed or is missing: {required}")

        if (
            self.protection.require_conversations_resolved
            and pr.unresolved_conversations > 0
        ):
            failures.append("Unresolved review conversations remain.")

        if self.protection.require_linear_history and pr.merge_strategy == "merge":
            failures.append("Merge commit strategy violates linear-history policy.")

        return not failures, failures

    def merge(self, pr: PullRequest) -> bool:
        try:
            eligible, failures = self.evaluate_merge(pr)

            # else executes only when evaluation itself completed normally.
            if not eligible:
                raise MergeError("; ".join(failures))
            else:
                pr.state = PullRequestState.MERGED
                self.audit_log.append(f"PR-{pr.number} merged using {pr.merge_strategy}")
                return True
        except MergeError as exc:
            self.audit_log.append(f"PR-{pr.number} merge rejected: {exc}")
            return False
        finally:
            # finally runs for both successful and rejected merge attempts.
            self.audit_log.append(f"PR-{pr.number} merge attempt finalized")

    def close(self, pr: PullRequest) -> None:
        if pr.state == PullRequestState.MERGED:
            raise ValueError("A merged PR cannot be closed as an independent operation.")
        pr.state = PullRequestState.CLOSED
        self.audit_log.append(f"PR-{pr.number} closed")


def run_status_check(
    pr: PullRequest,
    check_name: str,
    checker: Callable[[PullRequest], bool],
) -> None:
    try:
        passed = bool(checker(pr))
        pr.checks = [c for c in pr.checks if c.name != check_name]
        pr.checks.append(StatusCheck(check_name, passed))
    except Exception as exc:
        pr.checks = [c for c in pr.checks if c.name != check_name]
        pr.checks.append(StatusCheck(check_name, False))
        print(f"Status check '{check_name}' failed with error: {exc}")
    finally:
        print(f"Status check '{check_name}' completed.")


def demonstrate_else_and_finally() -> None:
    repository = Repository(
        "secure-platform",
        BranchProtection(
            required_approvals=2,
            required_checks={"tests", "security-scan"},
            require_conversations_resolved=True,
            require_linear_history=True,
        ),
    )

    for sha in ("a1b2c3d4", "b2c3d4e5", "c3d4e5f6"):
        repository.create_commit(sha)

    pr = repository.create_pull_request(
        "develop",
        "main",
        ["a1b2c3d4", "b2c3d4e5"],
        draft=False,
    )

    pr.add_review(Review("reviewer-alice", ReviewState.APPROVED, pr.head_sha))
    pr.add_review(Review("reviewer-bob", ReviewState.APPROVED, pr.head_sha))

    run_status_check(pr, "tests", lambda current: len(current.commits) <= 10)
    run_status_check(pr, "security-scan", lambda current: current.head_sha != "")

    eligible, reasons = repository.evaluate_merge(pr)

    if eligible:
        print("PR is merge-eligible.")
    else:
        print("PR is not merge-eligible:")
        for reason in reasons:
            print(f"  - {reason}")

    merged = repository.merge(pr)
    print(f"Merge result: {merged}")
    print(f"Final PR state: {pr.state.value}")

    # Synchronizing after new base changes invalidates prior approvals.
    if merged:
        print("The PR is already merged; no synchronization is attempted.")
    else:
        repository.synchronize(pr)

    print("\nAudit log:")
    for event in repository.audit_log:
        print(f"  {event}")


def demonstrate_failure_path() -> None:
    repository = Repository(
        "governed-api",
        BranchProtection(
            required_approvals=2,
            required_checks={"tests"},
        ),
    )
    repository.create_commit("deadbee1")

    pr = repository.create_pull_request("develop", "main", ["deadbee1"])

    pr.add_review(Review("reviewer-one", ReviewState.APPROVED, pr.head_sha))
    pr.checks.append(StatusCheck("tests", True))

    # try/except/else/finally is useful when success and cleanup have
    # materially different responsibilities.
    try:
        eligible, failures = repository.evaluate_merge(pr)
        if not eligible:
            raise MergeError(", ".join(failures))
    except MergeError as exc:
        print(f"Expected failure: {exc}")
    else:
        print("Unexpectedly eligible.")
    finally:
        print("Eligibility evaluation completed regardless of outcome.")


def main() -> None:
    print("=== Successful governance workflow ===")
    demonstrate_else_and_finally()

    print("\n=== Failure workflow ===")
    demonstrate_failure_path()

    # Assertions provide executable checks for important edge conditions.
    assert PullRequestState.MERGED.value == "merged"
    assert ReviewState.APPROVED.value == "approved"

    print("\nValidation complete.")


if __name__ == "__main__":
    main()
