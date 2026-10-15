#!/usr/bin/env python3
"""Comprehensive keyword-argument study through repository governance workflows.

Run with Python 3.10 or later:
    python keyword_arguments.py

The examples demonstrate positional arguments, keyword arguments, defaults,
keyword-only parameters, **kwargs, argument validation, callback forwarding,
configuration merging, decorators, dataclasses, and API compatibility.
"""

from __future__ import annotations

import inspect
import json
import logging
import re
from dataclasses import asdict, dataclass, field
from functools import wraps
from typing import Any, Callable, TypeVar


logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def heading(title: str) -> None:
    print(f"\n{'=' * 12} {title} {'=' * 12}")


# Keyword arguments bind supplied values to parameter names. Positional
# arguments bind by position, so combining both styles requires care.
def create_pull_request(
    title: str,
    source_branch: str,
    target_branch: str = "main",
    *,
    draft: bool = False,
    reviewers: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Build a validated Pull Request proposal."""
    if not title.strip():
        raise ValueError("Pull Request title cannot be empty.")

    if not source_branch.startswith("feature/"):
        raise ValueError("Source branch must start with 'feature/'.")

    if source_branch == target_branch:
        raise ValueError("Source and target branches must differ.")

    if not target_branch.strip():
        raise ValueError("Target branch cannot be empty.")

    if any(not reviewer.strip() for reviewer in reviewers):
        raise ValueError("Reviewer names cannot be empty.")

    return {
        "title": title.strip(),
        "source_branch": source_branch,
        "target_branch": target_branch,
        "draft": draft,
        "reviewers": list(dict.fromkeys(reviewers)),
        "state": "draft" if draft else "open",
    }


def demonstrate_binding() -> None:
    heading("Argument binding")

    positional = create_pull_request(
        "Validate deployment settings",
        "feature/deployment-validation",
        "main",
    )

    keyword_based = create_pull_request(
        title="Validate deployment settings",
        source_branch="feature/deployment-validation",
        target_branch="main",
        draft=True,
        reviewers=("Maya", "Daniel"),
    )

    mixed = create_pull_request(
        "Improve branch policy",
        "feature/branch-policy",
        reviewers=("Aisha",),
    )

    print("Positional call:", positional)
    print("Keyword-based call:", keyword_based)
    print("Mixed call:", mixed)

    try:
        create_pull_request(
            title="",
            source_branch="feature/invalid",
        )
    except ValueError as error:
        print("Validation correctly rejected invalid input:", error)


# Keyword-only parameters follow * in a function signature. This is useful
# when boolean flags or policy settings should be explicitly named.
def evaluate_merge_policy(
    pull_request: dict[str, Any],
    *,
    required_approvals: int = 2,
    require_ci: bool = True,
    require_resolved_comments: bool = True,
    allow_drafts: bool = False,
) -> dict[str, Any]:
    """Evaluate repository-level merge prerequisites."""
    if required_approvals < 0:
        raise ValueError("required_approvals cannot be negative.")

    if not isinstance(required_approvals, int) or isinstance(
        required_approvals, bool
    ):
        raise TypeError("required_approvals must be an integer.")

    if pull_request["state"] == "draft" and not allow_drafts:
        return {"eligible": False, "reasons": ["Draft Pull Requests cannot merge."]}

    reasons: list[str] = []

    if pull_request.get("approvals", 0) < required_approvals:
        reasons.append(
            f"Requires {required_approvals} approvals; "
            f"received {pull_request.get('approvals', 0)}."
        )

    if require_ci and pull_request.get("ci_status") != "success":
        reasons.append("Required CI checks have not passed.")

    if (
        require_resolved_comments
        and pull_request.get("unresolved_comments", 0) > 0
    ):
        reasons.append("Review discussions remain unresolved.")

    return {"eligible": not reasons, "reasons": reasons}


def demonstrate_keyword_only_parameters() -> None:
    heading("Keyword-only policy settings")

    pull_request = {
        "state": "open",
        "approvals": 2,
        "ci_status": "success",
        "unresolved_comments": 0,
    }

    strict_result = evaluate_merge_policy(
        pull_request,
        required_approvals=2,
        require_ci=True,
        require_resolved_comments=True,
    )

    relaxed_ci_result = evaluate_merge_policy(
        pull_request,
        required_approvals=2,
        require_ci=False,
        require_resolved_comments=True,
    )

    print("Strict policy:", strict_result)
    print("Policy with CI enforcement disabled:", relaxed_ci_result)

    try:
        evaluate_merge_policy(pull_request, 2)
    except TypeError as error:
        print("Keyword-only enforcement:", error)


# A mutable default is shared between calls. Use None or a factory instead.
def collect_checks(
    required_checks: list[str] | None = None,
) -> list[str]:
    checks = list(required_checks) if required_checks is not None else []
    checks.append("unit-tests")
    return checks


def demonstrate_defaults() -> None:
    heading("Default values and mutable-default safety")

    print(collect_checks())
    print(collect_checks())
    print(collect_checks(["lint"]))

    @dataclass
    class BranchProtection:
        branch: str
        required_checks: list[str] = field(
            default_factory=lambda: ["unit-tests", "lint"]
        )
        required_approvals: int = 2
        allow_force_push: bool = False
        allow_deletion: bool = False

    main_policy = BranchProtection(branch="main")
    release_policy = BranchProtection(
        branch="release",
        required_checks=["integration-tests", "security-scan"],
        required_approvals=3,
    )

    main_policy.required_checks.append("dependency-audit")

    print("Main policy:", asdict(main_policy))
    print("Release policy:", asdict(release_policy))


# **kwargs captures extra keyword arguments in a dictionary. Explicit
# parameters remain preferable for settings with known meanings.
def build_ci_configuration(
    project: str,
    *,
    python_version: str = "3.12",
    timeout_seconds: int = 600,
    **custom_settings: Any,
) -> dict[str, Any]:
    if not project.strip():
        raise ValueError("Project name is required.")

    if timeout_seconds <= 0:
        raise ValueError("Timeout must be positive.")

    reserved = {"project", "python_version", "timeout_seconds"}
    collisions = reserved.intersection(custom_settings)

    if collisions:
        raise ValueError(f"Reserved settings supplied: {sorted(collisions)}")

    return {
        "project": project,
        "python_version": python_version,
        "timeout_seconds": timeout_seconds,
        "custom_settings": dict(custom_settings),
    }


def demonstrate_kwargs() -> None:
    heading("Arbitrary keyword arguments")

    configuration = build_ci_configuration(
        "payment-service",
        python_version="3.13",
        timeout_seconds=900,
        cache_dependencies=True,
        runner="linux-x64",
        artifact_retention_days=14,
    )

    print(json.dumps(configuration, indent=2))

    try:
        build_ci_configuration("payment-service", timeout_seconds=0)
    except ValueError as error:
        print("Configuration rejected:", error)


# A function receiving **options can accept extension fields, but it should
# validate names rather than silently accepting misspelled security settings.
def configure_branch_protection(
    branch: str,
    **options: Any,
) -> dict[str, Any]:
    allowed = {
        "required_reviews",
        "required_status_checks",
        "dismiss_stale_reviews",
        "require_linear_history",
        "restrict_pushes",
        "allow_force_push",
        "allow_deletion",
        "require_conversation_resolution",
        "enforce_for_administrators",
        "allow_bypass",
    }

    unknown = set(options) - allowed
    if unknown:
        raise TypeError(f"Unknown branch protection options: {sorted(unknown)}")

    policy = {
        "branch": branch,
        "required_reviews": 2,
        "required_status_checks": ["unit-tests", "lint"],
        "dismiss_stale_reviews": True,
        "require_linear_history": True,
        "restrict_pushes": True,
        "allow_force_push": False,
        "allow_deletion": False,
        "require_conversation_resolution": True,
        "enforce_for_administrators": True,
        "allow_bypass": False,
    }
    policy.update(options)

    if not branch.strip():
        raise ValueError("Branch name cannot be empty.")

    if not isinstance(policy["required_reviews"], int) or isinstance(
        policy["required_reviews"], bool
    ):
        raise TypeError("required_reviews must be an integer.")

    if policy["required_reviews"] < 0:
        raise ValueError("required_reviews cannot be negative.")

    for name in (
        "dismiss_stale_reviews",
        "require_linear_history",
        "restrict_pushes",
        "allow_force_push",
        "allow_deletion",
        "require_conversation_resolution",
        "enforce_for_administrators",
        "allow_bypass",
    ):
        if not isinstance(policy[name], bool):
            raise TypeError(f"{name} must be a boolean.")

    if not isinstance(policy["required_status_checks"], list):
        raise TypeError("required_status_checks must be a list.")

    return policy


def demonstrate_policy_configuration() -> None:
    heading("Validated branch protection configuration")

    policy = configure_branch_protection(
        "main",
        required_reviews=3,
        required_status_checks=["unit-tests", "integration-tests", "lint"],
        enforce_for_administrators=True,
    )

    print(json.dumps(policy, indent=2))

    try:
        configure_branch_protection("main", require_linera_history=True)
    except TypeError as error:
        print("Misspelled option rejected:", error)


# Dictionary unpacking expands mappings into named arguments. The order of
# explicit arguments and **mapping expansion matters when keys collide.
def open_review_request(
    title: str,
    *,
    reviewers: tuple[str, ...],
    labels: tuple[str, ...] = (),
    draft: bool = False,
) -> dict[str, Any]:
    return {
        "title": title,
        "reviewers": list(reviewers),
        "labels": list(labels),
        "draft": draft,
    }


def demonstrate_unpacking() -> None:
    heading("Dictionary unpacking")

    options = {
        "reviewers": ("Maya", "Chen"),
        "labels": ("security", "backend"),
        "draft": False,
    }

    request = open_review_request(
        "Harden token validation",
        **options,
    )

    print("Expanded options:", request)

    base_options = {"labels": ("backend",), "draft": True}
    override_options = {"draft": False, "reviewers": ("Aisha",)}

    merged_options = {**base_options, **override_options}
    print("Merged options:", merged_options)

    # A later dictionary value replaces an earlier value with the same key.
    print(
        "Constructed request:",
        open_review_request(
            "Fix authorization policy",
            reviewers=merged_options["reviewers"],
            labels=merged_options["labels"],
            draft=merged_options["draft"],
        ),
    )


# Callbacks can forward keyword arguments with **kwargs. functools.wraps
# preserves the wrapped function's metadata and inspectable signature.
def audit_call(function: F) -> F:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info(
            "Calling %s with %d positional and %d keyword arguments",
            function.__name__,
            len(args),
            len(kwargs),
        )
        return function(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


@audit_call
def publish_merge_decision(
    pull_request_id: int,
    *,
    merged_by: str,
    strategy: str = "squash",
) -> dict[str, Any]:
    if pull_request_id <= 0:
        raise ValueError("Pull Request ID must be positive.")

    if strategy not in {"merge", "squash", "rebase"}:
        raise ValueError("Unsupported merge strategy.")

    if not merged_by.strip():
        raise ValueError("A responsible merger must be identified.")

    return {
        "pull_request_id": pull_request_id,
        "merged_by": merged_by,
        "strategy": strategy,
        "state": "merged",
    }


def demonstrate_decorators_and_signatures() -> None:
    heading("Decorators and function signatures")

    decision = publish_merge_decision(
        418,
        merged_by="repository-maintainer",
        strategy="squash",
    )

    print("Merge decision:", decision)
    print("Signature preserved:", inspect.signature(publish_merge_decision))

    try:
        publish_merge_decision(418, merged_by="maintainer", strategy="octopus")
    except ValueError as error:
        print("Invalid strategy rejected:", error)


# **kwargs also supports a controlled extension mechanism for review metadata.
# Explicitly reject unsupported values instead of allowing arbitrary payloads.
def record_review(
    pull_request_id: int,
    reviewer: str,
    *,
    state: str,
    commit_sha: str,
    **metadata: Any,
) -> dict[str, Any]:
    allowed_metadata = {"review_summary", "reviewer_team", "review_round"}
    unknown = set(metadata) - allowed_metadata

    if unknown:
        raise TypeError(f"Unsupported review metadata: {sorted(unknown)}")

    if pull_request_id <= 0:
        raise ValueError("Pull Request ID must be positive.")

    if not reviewer.strip():
        raise ValueError("Reviewer identity is required.")

    if state not in {"approved", "changes_requested", "commented"}:
        raise ValueError("Unsupported review state.")

    if not re.fullmatch(r"[0-9a-f]{7,40}", commit_sha):
        raise ValueError("Commit SHA must contain 7 to 40 lowercase hex digits.")

    return {
        "pull_request_id": pull_request_id,
        "reviewer": reviewer,
        "state": state,
        "commit_sha": commit_sha,
        "metadata": metadata,
    }


def demonstrate_review_metadata() -> None:
    heading("Review recording and stale approval detection")

    reviewed_commit = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
    current_commit = "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1"

    review = record_review(
        418,
        "Maya",
        state="approved",
        commit_sha=reviewed_commit,
        reviewer_team="platform",
        review_round=1,
        review_summary="Authorization checks are correctly enforced.",
    )

    review["is_stale"] = review["commit_sha"] != current_commit
    print(json.dumps(review, indent=2))
    print("Approval applies to current commit:", not review["is_stale"])


# Parameterized validation prevents accidental acceptance of misspelled names.
# It also demonstrates why Python's type hints alone do not enforce runtime types.
def validate_policy_payload(**payload: Any) -> dict[str, Any]:
    expected_types = {
        "required_approvals": int,
        "require_ci": bool,
        "require_linear_history": bool,
    }

    unknown = set(payload) - set(expected_types)
    if unknown:
        raise TypeError(f"Unexpected policy fields: {sorted(unknown)}")

    for key, expected_type in expected_types.items():
        if key not in payload:
            continue

        value = payload[key]

        if expected_type is int:
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{key} must be an integer.")
        elif not isinstance(value, expected_type):
            raise TypeError(f"{key} must be a boolean.")

    if payload.get("required_approvals", 0) < 0:
        raise ValueError("required_approvals cannot be negative.")

    return dict(payload)


def demonstrate_validation() -> None:
    heading("Runtime keyword validation")

    print(
        validate_policy_payload(
            required_approvals=2,
            require_ci=True,
            require_linear_history=True,
        )
    )

    invalid_payloads = [
        {"required_approvals": True},
        {"require_ci": "yes"},
        {"require_linear_history": False, "require_lineer_history": True},
        {"required_approvals": -1},
    ]

    for payload in invalid_payloads:
        try:
            validate_policy_payload(**payload)
        except (TypeError, ValueError) as error:
            print(f"Rejected {payload}: {error}")


def demonstrate_signature_inspection() -> None:
    heading("Signature inspection and binding")

    signature = inspect.signature(create_pull_request)

    supplied = {
        "title": "Fix protected branch enforcement",
        "source_branch": "feature/protection-enforcement",
        "draft": False,
        "reviewers": ("Maya", "Daniel"),
    }

    # bind() applies Python's actual argument-binding rules without executing
    # the function, making it useful for wrappers and validation frameworks.
    bound = signature.bind(**supplied)
    bound.apply_defaults()

    print("Signature:", signature)
    print("Bound arguments:", dict(bound.arguments))

    for invalid_call in (
        lambda: create_pull_request(
            "Bad source",
            "bugfix/source-name",
        ),
        lambda: create_pull_request(
            "Duplicate arguments",
            "feature/example",
            title="Second title",
        ),
    ):
        try:
            invalid_call()
        except (ValueError, TypeError) as error:
            print("Invalid invocation:", error)


def demonstrate_compatibility() -> None:
    heading("Backward-compatible keyword APIs")

    # Adding a new optional keyword-only parameter preserves existing calls.
    def notify_reviewer(
        reviewer: str,
        pull_request_id: int,
        *,
        channel: str = "email",
        include_diff_link: bool = True,
    ) -> dict[str, Any]:
        if channel not in {"email", "chat", "webhook"}:
            raise ValueError("Unsupported notification channel.")

        return {
            "reviewer": reviewer,
            "pull_request_id": pull_request_id,
            "channel": channel,
            "include_diff_link": include_diff_link,
        }

    old_call = notify_reviewer("Maya", 418)
    new_call = notify_reviewer(
        "Daniel",
        418,
        channel="chat",
        include_diff_link=False,
    )

    print("Existing call:", old_call)
    print("Extended call:", new_call)


def main() -> None:
    demonstrate_binding()
    demonstrate_keyword_only_parameters()
    demonstrate_defaults()
    demonstrate_kwargs()
    demonstrate_policy_configuration()
    demonstrate_unpacking()
    demonstrate_decorators_and_signatures()
    demonstrate_review_metadata()
    demonstrate_validation()
    demonstrate_signature_inspection()
    demonstrate_compatibility()

    heading("Execution completed")
    print("All keyword-argument demonstrations finished.")


if __name__ == "__main__":
    main()
