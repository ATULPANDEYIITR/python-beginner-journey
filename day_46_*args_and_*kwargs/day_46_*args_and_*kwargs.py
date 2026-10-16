#!/usr/bin/env python3
"""Practical study of *args and **kwargs in repository automation.

The examples progress from argument packing and unpacking to decorators,
configuration merging, validation, event processing, and testing.
The program uses only the Python standard library.
"""

from __future__ import annotations

import functools
import inspect
import json
import logging
import time
import unittest
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar


F = TypeVar("F", bound=Callable[..., Any])

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def heading(title: str) -> None:
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


# A function with ordinary parameters establishes the baseline.
def calculate_review_capacity(reviewers: int, minutes_per_reviewer: int) -> int:
    if reviewers < 0 or minutes_per_reviewer < 0:
        raise ValueError("Review counts and time cannot be negative.")
    return reviewers * minutes_per_reviewer


# *args collects extra positional arguments into a tuple.
def summarize_commits(pull_request_id: int, *commit_messages: str) -> dict[str, Any]:
    if pull_request_id <= 0:
        raise ValueError("Pull request ID must be positive.")
    if any(not isinstance(message, str) or not message.strip()
           for message in commit_messages):
        raise ValueError("Commit messages must be non-empty strings.")

    return {
        "pull_request_id": pull_request_id,
        "commit_count": len(commit_messages),
        "messages": commit_messages,
    }


# **kwargs collects extra named arguments into a dictionary.
def create_pull_request(title: str, source_branch: str, target_branch: str,
                        **metadata: Any) -> dict[str, Any]:
    required = {"author", "repository"}
    missing = required - metadata.keys()
    if missing:
        raise ValueError(f"Missing metadata: {', '.join(sorted(missing))}")

    allowed = {"author", "repository", "draft", "labels", "reviewers"}
    unknown = metadata.keys() - allowed
    if unknown:
        raise ValueError(f"Unsupported metadata: {', '.join(sorted(unknown))}")

    if not title.strip() or not source_branch.strip() or not target_branch.strip():
        raise ValueError("Title and branch names must not be empty.")
    if source_branch == target_branch:
        raise ValueError("Source and target branches must differ.")

    return {
        "title": title,
        "source_branch": source_branch,
        "target_branch": target_branch,
        **metadata,
    }


def record_activity(action: str, *subjects: str, **details: Any) -> dict[str, Any]:
    """Combine positional subjects with flexible named event details."""
    if not action.strip():
        raise ValueError("Action must not be empty.")

    event = {
        "action": action,
        "subjects": list(subjects),
        "details": dict(details),
    }
    print(json.dumps(event, indent=2, sort_keys=True, default=str))
    return event


def demonstrate_unpacking() -> None:
    heading("Argument packing and unpacking")

    print("Review capacity:", calculate_review_capacity(3, 25))

    commit_messages = [
        "Validate incoming webhook signatures",
        "Add audit records for policy decisions",
        "Reject unauthorized merge requests",
    ]
    commit_summary = summarize_commits(42, *commit_messages)
    print("Commit summary:", commit_summary)

    metadata = {
        "author": "maya",
        "repository": "platform-api",
        "draft": False,
        "labels": ["security", "backend"],
        "reviewers": ["alex", "sam"],
    }
    request = create_pull_request(
        "Enforce signed webhook delivery",
        "feature/signed-webhooks",
        "main",
        **metadata,
    )
    print("Pull request:", json.dumps(request, indent=2))

    # The star operator unpacks an iterable; the double-star operator
    # unpacks a mapping whose keys must be valid keyword parameter names.
    first = [42, "maya"]
    second = {"repository": "platform-api", "draft": True}
    print("Unpacked event:")
    record_activity("pull_request.opened", *first, **second)


def demonstrate_argument_binding() -> None:
    heading("Parameter binding and common mistakes")

    def publish_review(repository: str, pull_request_id: int,
                       reviewer: str, approved: bool = False) -> None:
        print(
            f"{repository} PR #{pull_request_id}: "
            f"{reviewer} approved={approved}"
        )

    publish_review("platform-api", 42, reviewer="maya", approved=True)

    signature = inspect.signature(publish_review)
    print("Function signature:", signature)
    print(
        "Bound arguments:",
        signature.bind(
            "platform-api", 42, reviewer="maya", approved=True
        ).arguments,
    )

    invalid_calls = [
        lambda: publish_review("platform-api", pull_request_id=42,
                               reviewer="maya", unknown=True),
        lambda: publish_review("platform-api", 42, "maya", reviewer="sam"),
    ]

    for call in invalid_calls:
        try:
            call()
        except TypeError as exc:
            print("Rejected call:", exc)


def merge_settings(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    """Perform a shallow configuration merge without mutating either input."""
    return {**base, **overrides}


def configure_review_policy(**options: Any) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "required_approvals": 2,
        "dismiss_stale_approvals": True,
        "require_all_conversations_resolved": True,
        "allow_author_approval": False,
    }
    unknown = options.keys() - defaults.keys()
    if unknown:
        raise ValueError(f"Unknown policy options: {sorted(unknown)}")

    policy = {**defaults, **options}
    if (
        not isinstance(policy["required_approvals"], int)
        or isinstance(policy["required_approvals"], bool)
        or policy["required_approvals"] < 0
    ):
        raise ValueError("required_approvals must be a non-negative integer.")

    for key in (
        "dismiss_stale_approvals",
        "require_all_conversations_resolved",
        "allow_author_approval",
    ):
        if not isinstance(policy[key], bool):
            raise ValueError(f"{key} must be a boolean.")

    return policy


def demonstrate_configuration() -> None:
    heading("Keyword configuration and precedence")

    organization_defaults = {
        "required_approvals": 2,
        "require_status_checks": True,
        "allow_force_push": False,
    }
    repository_overrides = {
        "required_approvals": 3,
        "required_status_checks": ["tests", "security-scan"],
    }

    effective = merge_settings(organization_defaults, repository_overrides)
    print("Effective settings:", json.dumps(effective, indent=2))
    print("Validated review policy:", configure_review_policy(
        required_approvals=3,
        dismiss_stale_approvals=True,
    ))

    try:
        configure_review_policy(required_approvals=-1)
    except ValueError as exc:
        print("Invalid policy:", exc)


def traced(function: F) -> F:
    """A decorator that preserves the wrapped function's metadata."""
    @functools.wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(
            f"Calling {function.__name__}: "
            f"positional={len(args)}, keyword={sorted(kwargs)}"
        )
        return function(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


@traced
def evaluate_merge(
    pull_request_id: int,
    *,
    approvals: int,
    required_approvals: int,
    checks_passed: bool,
    conversations_resolved: bool,
) -> dict[str, Any]:
    """Keyword-only policy inputs make security decisions explicit."""
    if pull_request_id <= 0:
        raise ValueError("Pull request ID must be positive.")
    if required_approvals < 0 or approvals < 0:
        raise ValueError("Approval counts cannot be negative.")

    blockers: list[str] = []
    if approvals < required_approvals:
        blockers.append("insufficient approvals")
    if not checks_passed:
        blockers.append("required checks have failed or are pending")
    if not conversations_resolved:
        blockers.append("unresolved review conversations")

    return {
        "pull_request_id": pull_request_id,
        "mergeable": not blockers,
        "blockers": blockers,
    }


def retry_on_temporary_failure(
    attempts: int = 3,
    delay_seconds: float = 0.0,
) -> Callable[[F], F]:
    """A configurable decorator factory that forwards arbitrary call arguments."""
    if attempts < 1:
        raise ValueError("At least one attempt is required.")
    if delay_seconds < 0:
        raise ValueError("Delay cannot be negative.")

    def decorate(function: F) -> F:
        @functools.wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(attempts):
                try:
                    return function(*args, **kwargs)
                except (TimeoutError, ConnectionError):
                    if attempt == attempts - 1:
                        raise
                    if delay_seconds:
                        time.sleep(delay_seconds)
            raise RuntimeError("Unreachable retry state.")

        return wrapper  # type: ignore[return-value]

    return decorate


def demonstrate_decorators() -> None:
    heading("Decorators and explicit policy decisions")

    result = evaluate_merge(
        42,
        approvals=2,
        required_approvals=2,
        checks_passed=True,
        conversations_resolved=False,
    )
    print("Merge evaluation:", result)

    attempts = Counter()

    @retry_on_temporary_failure(attempts=3)
    def fetch_check_result(check_name: str, *, run_id: int) -> str:
        attempts[check_name] += 1
        if attempts[check_name] < 2:
            raise ConnectionError("Status service temporarily unavailable")
        return f"{check_name}: run {run_id} passed"

    print(fetch_check_result("unit-tests", run_id=981))
    print("Attempts:", attempts["unit-tests"])


@dataclass(frozen=True)
class Review:
    reviewer: str
    state: str
    commit_sha: str
    is_author: bool = False


@dataclass
class PullRequest:
    number: int
    title: str
    author: str
    source_branch: str
    target_branch: str
    head_sha: str
    base_sha: str
    draft: bool = True
    state: str = "open"
    reviews: list[Review] = field(default_factory=list)
    checks: dict[str, str] = field(default_factory=dict)
    unresolved_conversations: int = 0

    def add_review(self, review: Review) -> None:
        if self.state != "open":
            raise ValueError("Reviews can only be added to open pull requests.")
        if review.commit_sha != self.head_sha:
            raise ValueError("Review must apply to the current source commit.")
        if review.reviewer == self.author or review.is_author:
            raise ValueError("Pull request authors cannot review their own changes.")
        if review.state not in {"approved", "changes_requested", "commented"}:
            raise ValueError("Unsupported review state.")
        self.reviews.append(review)

    def synchronize(self, new_head_sha: str) -> None:
        if self.state != "open":
            raise ValueError("Only open pull requests can be synchronized.")
        if not new_head_sha.strip():
            raise ValueError("Commit SHA cannot be empty.")
        self.head_sha = new_head_sha
        # Existing reviews remain in the history but no longer approve this head.
        self.checks.clear()

    def current_approval_count(self) -> int:
        latest_by_reviewer: dict[str, Review] = {}
        for review in self.reviews:
            if review.commit_sha == self.head_sha:
                latest_by_reviewer[review.reviewer] = review
        return sum(
            review.state == "approved"
            for review in latest_by_reviewer.values()
        )


def demonstrate_lifecycle() -> None:
    heading("Pull request state and review freshness")

    pr = PullRequest(
        number=42,
        title="Enforce review governance",
        author="maya",
        source_branch="feature/governance",
        target_branch="main",
        head_sha="a91c2ef",
        base_sha="70bd119",
        draft=False,
        checks={"unit-tests": "passed", "security-scan": "passed"},
        unresolved_conversations=0,
    )

    pr.add_review(Review("alex", "approved", "a91c2ef"))
    pr.add_review(Review("sam", "approved", "a91c2ef"))
    print("Approvals before update:", pr.current_approval_count())

    pr.synchronize("c814d02")
    print("Approvals after update:", pr.current_approval_count())
    print("Checks after update:", pr.checks)

    pr.add_review(Review("alex", "approved", "c814d02"))
    print("Current approvals after re-review:", pr.current_approval_count())


class WorkflowTests(unittest.TestCase):
    def test_positional_packing(self) -> None:
        summary = summarize_commits(7, "Add tests", "Fix policy")
        self.assertEqual(summary["commit_count"], 2)

    def test_unknown_pull_request_metadata_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            create_pull_request(
                "Secure merge",
                "feature/security",
                "main",
                author="maya",
                repository="platform-api",
                admin_override=True,
            )

    def test_merge_blockers(self) -> None:
        result = evaluate_merge(
            9,
            approvals=1,
            required_approvals=2,
            checks_passed=True,
            conversations_resolved=True,
        )
        self.assertFalse(result["mergeable"])

    def test_stale_approvals_do_not_count(self) -> None:
        pr = PullRequest(
            10, "Policy update", "maya", "feature/policy", "main",
            "new-sha", "base-sha",
        )
        pr.reviews.append(Review("alex", "approved", "old-sha"))
        self.assertEqual(pr.current_approval_count(), 0)

    def test_retry_configuration_rejects_zero_attempts(self) -> None:
        with self.assertRaises(ValueError):
            retry_on_temporary_failure(attempts=0)


def main() -> None:
    demonstrate_unpacking()
    demonstrate_argument_binding()
    demonstrate_configuration()
    demonstrate_decorators()
    demonstrate_lifecycle()

    heading("Executable verification")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(WorkflowTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
