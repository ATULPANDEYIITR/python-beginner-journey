#!/usr/bin/env python3
"""
Assertions: executable learning artifact.

Covers:
- assert statements and explicit AssertionError
- preconditions, postconditions, and invariants
- assertions versus input validation
- custom assertion helpers
- debugging information
- edge cases and failure handling
- production considerations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class AccountStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"


class ValidationError(ValueError):
    """Raised when externally supplied data is invalid."""


class InvariantViolation(RuntimeError):
    """Raised when an internal object invariant is broken."""


def require(condition: bool, message: str) -> None:
    """Enforce an input precondition that must remain enabled in production."""
    if not condition:
        raise ValidationError(message)


def ensure(condition: bool, message: str) -> None:
    """Enforce a postcondition explicitly."""
    if not condition:
        raise AssertionError(message)


def assert_non_negative(value: int, name: str) -> None:
    """Internal assertion helper for state that must never be negative."""
    assert value >= 0, f"{name} must be non-negative, got {value}"


@dataclass
class Repository:
    name: str
    default_branch: str = "main"
    commits: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        require(bool(self.name.strip()), "repository name cannot be empty")
        require(
            self.default_branch.isidentifier() or self.default_branch in {"main", "master"},
            "default branch must be a valid simple branch name",
        )
        self._check_invariants()

    def add_commit(self, commit_id: str) -> None:
        require(bool(commit_id.strip()), "commit ID cannot be empty")
        require(commit_id not in self.commits, "duplicate commit IDs are not allowed")

        before = len(self.commits)
        self.commits.append(commit_id)

        ensure(
            len(self.commits) == before + 1,
            "adding a commit must increase repository size by one",
        )
        self._check_invariants()

    def _check_invariants(self) -> None:
        assert self.name.strip(), "repository name invariant violated"
        assert self.default_branch.strip(), "default branch invariant violated"
        assert len(self.commits) == len(set(self.commits)), (
            "repository contains duplicate commit IDs"
        )


@dataclass
class PullRequest:
    number: int
    source_branch: str
    target_branch: str
    commits: list[str]
    draft: bool = False
    merged: bool = False

    def __post_init__(self) -> None:
        require(self.number > 0, "pull request number must be positive")
        require(
            self.source_branch.strip() and self.target_branch.strip(),
            "source and target branches are required",
        )
        require(
            self.source_branch != self.target_branch,
            "source and target branches must differ",
        )
        self._check_invariants()

    def add_commit(self, commit_id: str) -> None:
        require(bool(commit_id.strip()), "commit ID cannot be empty")
        require(not self.merged, "merged pull requests cannot receive commits")
        require(commit_id not in self.commits, "duplicate commit in pull request")

        self.commits.append(commit_id)
        self._check_invariants()

    def mark_ready(self) -> None:
        require(not self.merged, "merged pull request cannot become ready")
        self.draft = False
        self._check_invariants()

    def merge(self) -> None:
        require(not self.merged, "pull request is already merged")
        require(bool(self.commits), "pull request must contain at least one commit")
        self.merged = True
        self._check_invariants()

    def _check_invariants(self) -> None:
        assert self.number > 0, "pull request number invariant violated"
        assert self.source_branch != self.target_branch, (
            "pull request branch invariant violated"
        )
        assert len(self.commits) == len(set(self.commits)), (
            "pull request contains duplicate commits"
        )
        assert not self.merged or not self.draft, (
            "a merged pull request cannot remain a draft"
        )


def calculate_average(values: Iterable[float]) -> float:
    values = list(values)

    require(bool(values), "at least one value is required")
    require(
        all(isinstance(value, (int, float)) for value in values),
        "all values must be numeric",
    )

    result = sum(values) / len(values)

    ensure(min(values) <= result <= max(values), "average postcondition failed")
    return result


def demonstrate_python_assert_behavior() -> None:
    """
    Python's assert is intended for internal correctness checks.

    Running Python with -O removes assert statements. Therefore external
    input validation should use explicit exceptions instead of assert.
    """
    value = 10

    assert value > 0, "internal value must be positive"

    require(value <= 100, "external value must not exceed 100")


def run_tests() -> None:
    repo = Repository("assertion-lab")
    repo.add_commit("a1")
    repo.add_commit("a2")

    assert repo.commits == ["a1", "a2"]

    pull_request = PullRequest(
        number=42,
        source_branch="feature/assertions",
        target_branch="main",
        commits=["a1"],
        draft=True,
    )

    assert pull_request.draft is True
    pull_request.add_commit("a2")
    pull_request.mark_ready()
    pull_request.merge()

    assert pull_request.merged is True
    assert pull_request.draft is False

    assert calculate_average([10, 20, 30]) == 20

    try:
        calculate_average([])
    except ValidationError as exc:
        assert "at least one" in str(exc)
    else:
        raise AssertionError("empty input should have failed")

    try:
        PullRequest(
            number=1,
            source_branch="main",
            target_branch="main",
            commits=["a1"],
        )
    except ValidationError as exc:
        assert "must differ" in str(exc)
    else:
        raise AssertionError("identical branches should have failed")

    try:
        pull_request.add_commit("a3")
    except ValidationError as exc:
        assert "merged" in str(exc)
    else:
        raise AssertionError("merged PR mutation should have failed")

    try:
        repo.add_commit("a1")
    except ValidationError as exc:
        assert "duplicate" in str(exc)
    else:
        raise AssertionError("duplicate commit should have failed")

    demonstrate_python_assert_behavior()


def main() -> None:
    run_tests()
    print("All assertion demonstrations and tests passed.")


if __name__ == "__main__":
    main()
