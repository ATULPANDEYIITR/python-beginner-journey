#!/usr/bin/env python3
"""Default arguments: practical Python implementations from fundamentals to advanced patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import wraps
from inspect import signature
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable, Iterable, TypeVar
import json


def print_section(title: str) -> None:
    print(f"\n{'=' * 12} {title} {'=' * 12}")


# A default is used only when the caller omits the corresponding argument.
def create_pull_request(
    title: str,
    source_branch: str,
    target_branch: str = "main",
    draft: bool = False,
) -> dict[str, object]:
    if not title.strip():
        raise ValueError("Pull request title cannot be empty.")
    if not source_branch.strip() or not target_branch.strip():
        raise ValueError("Branch names cannot be empty.")
    if source_branch == target_branch:
        raise ValueError("Source and target branches must differ.")

    return {
        "title": title,
        "source_branch": source_branch,
        "target_branch": target_branch,
        "draft": draft,
    }


# Positional defaults must follow required positional parameters.
# A caller may override any default using a keyword argument.
def summarize_review(
    reviewer: str,
    decision: str = "COMMENTED",
    summary: str = "No blocking observations.",
) -> str:
    allowed = {"APPROVED", "CHANGES_REQUESTED", "COMMENTED"}
    if decision not in allowed:
        raise ValueError(f"Unsupported review decision: {decision}")
    if not reviewer.strip():
        raise ValueError("Reviewer identity is required.")
    return f"{reviewer}: {decision} - {summary}"


def show_fundamentals() -> None:
    print_section("Function defaults")

    print(create_pull_request("Add audit logging", "feature/audit"))
    print(create_pull_request(
        "Repair authorization checks",
        "fix/authorization",
        target_branch="release",
        draft=True,
    ))
    print(summarize_review("reviewer-alex"))
    print(summarize_review(
        "reviewer-sam",
        "CHANGES_REQUESTED",
        "Reject unauthenticated role changes.",
    ))

    try:
        create_pull_request("Invalid branch", "main", "main")
    except ValueError as error:
        print(f"Validation caught: {error}")


# Mutable defaults are evaluated once when the function is defined.
# Reusing a list default can accidentally leak state between calls.
def unsafe_collect_labels(label: str, labels: list[str] = []) -> list[str]:
    labels.append(label)
    return labels


# None is an explicit sentinel meaning that a fresh list should be created.
def collect_labels(
    label: str,
    labels: list[str] | None = None,
) -> list[str]:
    if labels is None:
        labels = []
    labels.append(label)
    return labels


def demonstrate_mutable_defaults() -> None:
    print_section("Mutable default pitfalls")

    first = unsafe_collect_labels("security")
    second = unsafe_collect_labels("database")
    print(f"Shared default: first={first}, second={second}")

    first_safe = collect_labels("security")
    second_safe = collect_labels("database")
    print(f"Fresh defaults: first={first_safe}, second={second_safe}")

    existing = ["performance"]
    updated = collect_labels("security", existing)
    print(f"Explicit list: {updated}; original object preserved: {updated is existing}")


# Default values are captured when the def statement executes, not on every call.
DEFAULT_REVIEW_LIMIT = 3


def get_review_queue(limit: int = DEFAULT_REVIEW_LIMIT) -> list[str]:
    if limit < 0:
        raise ValueError("Limit cannot be negative.")
    return ["PR-104", "PR-103", "PR-102", "PR-101"][:limit]


def demonstrate_definition_time_defaults() -> None:
    print_section("Definition-time binding")

    global DEFAULT_REVIEW_LIMIT
    print(get_review_queue())
    DEFAULT_REVIEW_LIMIT = 1
    print(f"Changing the global does not change the captured default: {get_review_queue()}")
    print(f"Explicit argument: {get_review_queue(DEFAULT_REVIEW_LIMIT)}")


# Keyword-only parameters make configuration easier to read and extend.
def evaluate_merge_policy(
    checks: dict[str, str],
    approvals: int,
    *,
    required_approvals: int = 2,
    require_ci: bool = True,
    require_security_scan: bool = True,
) -> tuple[bool, list[str]]:
    if approvals < 0 or required_approvals < 0:
        raise ValueError("Approval counts cannot be negative.")

    failures: list[str] = []

    if approvals < required_approvals:
        failures.append(
            f"Requires {required_approvals} approvals; received {approvals}."
        )

    if require_ci and checks.get("ci") != "success":
        failures.append("Continuous integration has not succeeded.")

    if require_security_scan and checks.get("security") != "success":
        failures.append("Security scan has not succeeded.")

    return not failures, failures


def demonstrate_policy() -> None:
    print_section("Keyword-only policy defaults")

    checks = {"ci": "success", "security": "success"}
    print(evaluate_merge_policy(checks, approvals=2))
    print(evaluate_merge_policy(
        {"ci": "success", "security": "failure"},
        approvals=1,
        required_approvals=1,
    ))
    print(evaluate_merge_policy(
        {"ci": "success"},
        approvals=1,
        required_approvals=1,
        require_security_scan=False,
    ))


@dataclass
class PullRequest:
    """A small domain object with independent mutable state per instance."""

    number: int
    title: str
    source_branch: str
    target_branch: str = "main"
    labels: list[str] = field(default_factory=list)
    reviewers: set[str] = field(default_factory=set)
    draft: bool = True

    def add_reviewer(self, reviewer: str) -> None:
        if not reviewer.strip():
            raise ValueError("Reviewer cannot be empty.")
        self.reviewers.add(reviewer)

    def add_label(self, label: str) -> None:
        normalized = label.strip().lower()
        if not normalized:
            raise ValueError("Label cannot be empty.")
        if normalized not in self.labels:
            self.labels.append(normalized)

    def mark_ready(self) -> None:
        self.draft = False


def demonstrate_dataclass_defaults() -> None:
    print_section("Dataclass factories")

    first = PullRequest(104, "Add audit logging", "feature/audit")
    second = PullRequest(
        105,
        "Repair access control",
        "fix/access-control",
        target_branch="release",
    )

    first.add_label("Security")
    first.add_reviewer("reviewer-alex")
    first.mark_ready()

    print(first)
    print(second)
    print(f"Independent labels: {first.labels is not second.labels}")
    print(f"Independent reviewers: {first.reviewers is not second.reviewers}")


# functools.wraps preserves the original function's metadata.
F = TypeVar("F", bound=Callable[..., object])


def trace_calls(function: F) -> F:
    @wraps(function)
    def wrapper(*args: object, **kwargs: object) -> object:
        print(f"Calling {function.__name__}: args={args}, kwargs={kwargs}")
        result = function(*args, **kwargs)
        print(f"Returned: {result}")
        return result

    return wrapper  # type: ignore[return-value]


@trace_calls
def format_commit_message(
    summary: str,
    *,
    scope: str = "general",
    ticket: str | None = None,
) -> str:
    clean_summary = summary.strip()
    if not clean_summary:
        raise ValueError("Commit summary cannot be empty.")

    prefix = f"{scope}: "
    suffix = f" ({ticket})" if ticket else ""
    return f"{prefix}{clean_summary}{suffix}"


def demonstrate_introspection() -> None:
    print_section("Inspection and instrumentation")

    print(signature(create_pull_request))
    print(signature(evaluate_merge_policy))
    print(format_commit_message(
        "Enforce branch protection",
        scope="governance",
        ticket="SEC-42",
    ))


# Configuration defaults can be represented explicitly when None is valid data.
@dataclass(frozen=True)
class ReviewConfiguration:
    required_approvals: int = 2
    required_checks: tuple[str, ...] = ("ci", "security")
    dismiss_stale_approvals: bool = True

    def __post_init__(self) -> None:
        if self.required_approvals < 0:
            raise ValueError("Required approvals cannot be negative.")
        if len(set(self.required_checks)) != len(self.required_checks):
            raise ValueError("Required checks must be unique.")
        if any(not check.strip() for check in self.required_checks):
            raise ValueError("Check names cannot be empty.")


def assess_pull_request(
    checks: dict[str, str],
    approvals: int,
    *,
    configuration: ReviewConfiguration | None = None,
    is_draft: bool = False,
    unresolved_threads: int = 0,
    approval_is_stale: bool = False,
) -> dict[str, object]:
    # Configuration is created per invocation when the caller omits it.
    policy = configuration if configuration is not None else ReviewConfiguration()

    if approvals < 0 or unresolved_threads < 0:
        raise ValueError("Counts cannot be negative.")

    failures: list[str] = []

    if is_draft:
        failures.append("Draft pull requests cannot be merged.")

    if unresolved_threads:
        failures.append(f"{unresolved_threads} review discussion(s) remain unresolved.")

    effective_approvals = approvals
    if approval_is_stale and policy.dismiss_stale_approvals:
        effective_approvals = 0
        failures.append("Stale approvals are not counted.")

    if effective_approvals < policy.required_approvals:
        failures.append(
            f"Approval requirement not met: "
            f"{effective_approvals}/{policy.required_approvals}."
        )

    for check_name in policy.required_checks:
        if checks.get(check_name) != "success":
            failures.append(f"Required check '{check_name}' is not successful.")

    return {
        "eligible": not failures,
        "failures": failures,
        "effective_approvals": effective_approvals,
        "required_checks": policy.required_checks,
    }


def demonstrate_advanced_policy() -> None:
    print_section("Governance evaluation")

    configuration = ReviewConfiguration(
        required_approvals=2,
        required_checks=("ci", "security", "integration"),
    )

    checks = {
        "ci": "success",
        "security": "success",
        "integration": "success",
    }

    print(json.dumps(
        assess_pull_request(checks, 2, configuration=configuration),
        indent=2,
    ))

    print(json.dumps(
        assess_pull_request(
            checks,
            2,
            configuration=configuration,
            approval_is_stale=True,
        ),
        indent=2,
    ))

    print(json.dumps(
        assess_pull_request(
            {"ci": "success", "security": "failure"},
            1,
            configuration=configuration,
            is_draft=True,
            unresolved_threads=2,
        ),
        indent=2,
    ))


def write_audit_record(
    event: str,
    *,
    actor: str = "system",
    occurred_at: datetime | None = None,
    metadata: dict[str, object] | None = None,
    destination: Path,
) -> None:
    # Resolve optional values at call time and copy metadata to avoid retaining
    # a caller-owned mutable mapping inside the serialized record.
    timestamp = occurred_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("Audit timestamps must include a timezone.")
    if not event.strip() or not actor.strip():
        raise ValueError("Event and actor are required.")

    record = {
        "event": event,
        "actor": actor,
        "occurred_at": timestamp.isoformat(),
        "metadata": dict(metadata) if metadata is not None else {},
    }

    # Append one complete JSON object per line for audit-log processing.
    with destination.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")


def read_audit_records(destination: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []

    if not destination.exists():
        return records

    with destination.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Malformed audit record on line {line_number}"
                ) from error

            if not isinstance(value, dict):
                raise ValueError(f"Audit record on line {line_number} is not an object.")

            records.append(value)

    return records


def demonstrate_file_workflow() -> None:
    print_section("File handling and optional arguments")

    with TemporaryDirectory(prefix="review-audit-") as directory:
        path = Path(directory) / "audit.jsonl"

        write_audit_record(
            "pull_request.opened",
            actor="developer-lee",
            metadata={"number": 104, "target": "main"},
            destination=path,
        )
        write_audit_record(
            "review.approved",
            actor="reviewer-alex",
            metadata={"number": 104, "decision": "APPROVED"},
            destination=path,
        )

        print(json.dumps(read_audit_records(path), indent=2))

    print("A missing audit file produces an empty record list.")
    print(read_audit_records(Path("nonexistent-review-audit.jsonl")))


def run_assertions() -> None:
    assert create_pull_request("Add tests", "feature/tests")["target_branch"] == "main"
    assert create_pull_request(
        "Patch release", "fix/patch", target_branch="release"
    )["target_branch"] == "release"

    assert collect_labels("security") == ["security"]
    assert collect_labels("database") == ["database"]

    eligible, failures = evaluate_merge_policy(
        {"ci": "success", "security": "success"},
        approvals=2,
    )
    assert eligible and not failures

    rejected, failures = evaluate_merge_policy(
        {"ci": "failure", "security": "success"},
        approvals=2,
    )
    assert not rejected and any("integration" not in failure for failure in failures)

    result = assess_pull_request(
        {"ci": "success", "security": "success"},
        2,
    )
    assert result["eligible"] is True

    stale_result = assess_pull_request(
        {"ci": "success", "security": "success"},
        2,
        approval_is_stale=True,
    )
    assert stale_result["eligible"] is False

    try:
        ReviewConfiguration(required_approvals=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("Negative approval requirement should fail.")

    print_section("Assertions")
    print("All assertions passed.")


def main() -> None:
    show_fundamentals()
    demonstrate_mutable_defaults()
    demonstrate_definition_time_defaults()
    demonstrate_policy()
    demonstrate_dataclass_defaults()
    demonstrate_introspection()
    demonstrate_advanced_policy()
    demonstrate_file_workflow()
    run_assertions()


if __name__ == "__main__":
    main()
