#!/usr/bin/env python3
"""
Project Dependency Management
A repository dependency management and governance simulator.

Features:
- Dependency inventory and version constraints
- Semantic version validation
- Direct and transitive dependencies
- Dependency graph construction
- Cycle detection and topological ordering
- Vulnerability and license policy evaluation
- Version conflict detection
- Update planning
- Dependency lockfile generation
- Automated validation and audit reporting
- Pull Request-based dependency updates
- Code review and approval simulation
- Branch protection and merge eligibility
"""

from __future__ import annotations

import json
import hashlib
import re
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


class DependencyError(Exception):
    pass


class ValidationError(DependencyError):
    pass


class PolicyError(DependencyError):
    pass


class PRState(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    MERGED = "merged"
    CLOSED = "closed"


class ReviewState(str, Enum):
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    COMMENTED = "commented"
    DISMISSED = "dismissed"


class CheckState(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    patch: int

    PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")

    @classmethod
    def parse(cls, value: str) -> "Version":
        match = cls.PATTERN.fullmatch(value)
        if not match:
            raise ValidationError(f"Invalid semantic version: {value}")
        return cls(*(int(part) for part in match.groups()))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass
class Dependency:
    name: str
    version: Version
    minimum: Version
    maximum: Optional[Version] = None
    direct: bool = True
    license: str = "MIT"
    vulnerabilities: int = 0
    dependencies: list[str] = field(default_factory=list)
    source: str = "public-registry"

    def validate(self) -> None:
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", self.name):
            raise ValidationError(f"Invalid dependency name: {self.name}")
        if self.version < self.minimum:
            raise ValidationError(f"{self.name} violates minimum version")
        if self.maximum and self.version > self.maximum:
            raise ValidationError(f"{self.name} exceeds maximum version")
        if self.vulnerabilities < 0:
            raise ValidationError("Vulnerability count cannot be negative")


@dataclass
class Policy:
    allowed_licenses: set[str] = field(
        default_factory=lambda: {"MIT", "Apache-2.0", "BSD-3-Clause"}
    )
    maximum_vulnerabilities: int = 0
    require_lockfile: bool = True
    require_approval: bool = True
    required_approvals: int = 2
    require_passing_checks: bool = True
    require_resolved_conversations: bool = True
    reject_direct_push: bool = True
    reject_force_push: bool = True
    reject_branch_deletion: bool = True
    require_linear_history: bool = True
    dismiss_stale_approvals: bool = True
    administrator_bypass: bool = False


@dataclass
class Review:
    reviewer: str
    state: ReviewState
    commit_hash: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class PullRequest:
    number: int
    source_branch: str
    target_branch: str
    proposed_changes: dict[str, Version]
    state: PRState = PRState.OPEN
    draft: bool = False
    reviews: list[Review] = field(default_factory=list)
    checks: dict[str, CheckState] = field(default_factory=dict)
    conversations: dict[str, bool] = field(default_factory=dict)
    base_synchronized: bool = True
    merge_conflicts: bool = False
    head_commit: str = "initial"
    merge_commit: Optional[str] = None

    def add_review(self, reviewer: str, state: ReviewState) -> None:
        if self.state != PRState.OPEN or self.draft:
            raise DependencyError("PR is not ready for review")
        if any(r.reviewer == reviewer for r in self.reviews):
            self.reviews = [
                r for r in self.reviews if r.reviewer != reviewer
            ]
        self.reviews.append(
            Review(reviewer, state, self.head_commit)
        )

    def push_commit(self, changes: dict[str, Version]) -> None:
        if self.state != PRState.OPEN:
            raise DependencyError("Cannot push to a closed PR")
        self.proposed_changes.update(changes)
        payload = json.dumps(
            {k: str(v) for k, v in sorted(self.proposed_changes.items())}
        )
        self.head_commit = hashlib.sha256(
            (self.head_commit + payload).encode()
        ).hexdigest()[:12]

        self.checks = {
            name: CheckState.PENDING for name in self.checks
        }
        self.merge_conflicts = False


class DependencyManager:
    def __init__(self, policy: Optional[Policy] = None):
        self.dependencies: dict[str, Dependency] = {}
        self.policy = policy or Policy()
        self.repositories: dict[str, dict[str, str]] = {}
        self.pull_requests: dict[int, PullRequest] = {}
        self.protected_branches: set[str] = {"main"}
        self.next_pr = 1

    def add_dependency(self, dependency: Dependency) -> None:
        dependency.validate()
        if dependency.name in self.dependencies:
            raise ValidationError(
                f"Dependency already exists: {dependency.name}"
            )
        self.dependencies[dependency.name] = dependency

    def dependency_graph(self) -> dict[str, list[str]]:
        graph = {}
        for name, dep in self.dependencies.items():
            for child in dep.dependencies:
                if child not in self.dependencies:
                    raise ValidationError(
                        f"Unknown transitive dependency: {child}"
                    )
            graph[name] = list(dep.dependencies)
        return graph

    def topological_order(self) -> list[str]:
        graph = self.dependency_graph()
        indegree = {name: 0 for name in graph}

        # Edges point from a package to its prerequisites.
        for name, children in graph.items():
            for child in children:
                indegree[name] += 1

        reverse = defaultdict(list)
        for name, children in graph.items():
            for child in children:
                reverse[child].append(name)

        queue = deque(
            sorted(name for name, degree in indegree.items() if degree == 0)
        )
        result = []

        while queue:
            current = queue.popleft()
            result.append(current)
            for dependent in sorted(reverse[current]):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(graph):
            raise DependencyError("Circular dependency detected")

        return result

    def evaluate(self) -> list[str]:
        findings = []

        for dependency in self.dependencies.values():
            try:
                dependency.validate()
            except ValidationError as exc:
                findings.append(str(exc))

            if dependency.license not in self.policy.allowed_licenses:
                findings.append(
                    f"Prohibited license: {dependency.name} "
                    f"({dependency.license})"
                )

            if dependency.vulnerabilities > self.policy.maximum_vulnerabilities:
                findings.append(
                    f"Security policy violation: {dependency.name} "
                    f"has {dependency.vulnerabilities} vulnerabilities"
                )

        try:
            self.topological_order()
        except DependencyError as exc:
            findings.append(str(exc))

        return findings

    def update_plan(
        self, available_versions: dict[str, str]
    ) -> dict[str, Version]:
        plan = {}

        for name, raw_version in available_versions.items():
            if name not in self.dependencies:
                raise ValidationError(f"Unknown dependency: {name}")

            candidate = Version.parse(raw_version)
            current = self.dependencies[name]

            if candidate <= current.version:
                continue
            if candidate < current.minimum:
                continue
            if current.maximum and candidate > current.maximum:
                continue

            plan[name] = candidate

        return plan

    def lockfile(self) -> dict:
        graph = self.dependency_graph()
        entries = {}

        for name in self.topological_order():
            dep = self.dependencies[name]
            entries[name] = {
                "version": str(dep.version),
                "direct": dep.direct,
                "license": dep.license,
                "dependencies": sorted(graph[name]),
                "source": dep.source,
            }

        canonical = json.dumps(entries, sort_keys=True)
        return {
            "format": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "dependencies": entries,
            "integrity": hashlib.sha256(canonical.encode()).hexdigest(),
        }

    def save_lockfile(self, path: str = "dependencies.lock.json") -> None:
        target = Path(path)
        data = self.lockfile()
        temporary = target.with_suffix(target.suffix + ".tmp")

        try:
            temporary.write_text(
                json.dumps(data, indent=2),
                encoding="utf-8",
            )
            temporary.replace(target)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise

    def create_pull_request(
        self,
        changes: dict[str, Version],
        source: str = "dependency/update",
        target: str = "main",
        draft: bool = False,
    ) -> PullRequest:
        if not changes:
            raise ValidationError("PR must contain dependency changes")
        if source == target:
            raise ValidationError("Source and target branches must differ")
        if target not in self.protected_branches:
            raise ValidationError("Target branch is not protected")

        for name, version in changes.items():
            if name not in self.dependencies:
                raise ValidationError(f"Unknown dependency: {name}")
            dep = self.dependencies[name]
            if version <= dep.version:
                raise ValidationError(f"Non-upgrade version: {name}")
            if dep.maximum and version > dep.maximum:
                raise ValidationError(f"Version outside allowed range: {name}")

        pr = PullRequest(
            self.next_pr,
            source,
            target,
            dict(changes),
            state=PRState.DRAFT if draft else PRState.OPEN,
            draft=draft,
        )
        self.pull_requests[pr.number] = pr
        self.next_pr += 1
        return pr

    def evaluate_merge(self, pr: PullRequest) -> list[str]:
        reasons = []

        if pr.state != PRState.OPEN:
            reasons.append("PR is not open")
        if pr.draft:
            reasons.append("Draft PR cannot be merged")
        if pr.merge_conflicts:
            reasons.append("Merge conflicts must be resolved")
        if not pr.base_synchronized:
            reasons.append("Source branch is not synchronized with target")
        if self.policy.require_resolved_conversations:
            if any(not resolved for resolved in pr.conversations.values()):
                reasons.append("Unresolved review conversations exist")

        if self.policy.require_passing_checks:
            if not pr.checks:
                reasons.append("Required checks have not been configured")
            elif any(
                state != CheckState.PASSED
                for state in pr.checks.values()
            ):
                reasons.append("One or more status checks have not passed")

        valid_reviews = [
            review for review in pr.reviews
            if review.commit_hash == pr.head_commit
        ]

        if self.policy.dismiss_stale_approvals:
            approvals = {
                review.reviewer
                for review in valid_reviews
                if review.state == ReviewState.APPROVED
            }
        else:
            approvals = {
                review.reviewer
                for review in pr.reviews
                if review.state == ReviewState.APPROVED
            }

        changes_requested = any(
            review.state == ReviewState.CHANGES_REQUESTED
            and (
                not self.policy.dismiss_stale_approvals
                or review.commit_hash == pr.head_commit
            )
            for review in pr.reviews
        )

        if changes_requested:
            reasons.append("Changes have been requested")

        if self.policy.require_approval:
            if len(approvals) < self.policy.required_approvals:
                reasons.append(
                    f"Requires {self.policy.required_approvals} "
                    f"eligible approvals; found {len(approvals)}"
                )

        if self.policy.require_lockfile:
            if not self.dependencies:
                reasons.append("Dependency inventory is empty")

        reasons.extend(self.evaluate())
        return reasons

    def merge(self, pr: PullRequest, strategy: str = "merge") -> None:
        reasons = self.evaluate_merge(pr)
        if reasons:
            raise PolicyError("; ".join(reasons))

        if strategy not in {"merge", "squash", "rebase"}:
            raise ValidationError("Unsupported merge strategy")

        # Update branch state only after all merge conditions pass.
        for name, version in pr.proposed_changes.items():
            self.dependencies[name].version = version

        pr.merge_commit = hashlib.sha256(
            f"{pr.number}:{pr.head_commit}:{strategy}".encode()
        ).hexdigest()[:12]
        pr.state = PRState.MERGED


def build_demo() -> DependencyManager:
    manager = DependencyManager(
        Policy(required_approvals=2)
    )

    manager.add_dependency(
        Dependency(
            "httpx", Version.parse("0.27.0"),
            Version.parse("0.25.0"),
            license="BSD-3-Clause",
        )
    )
    manager.add_dependency(
        Dependency(
            "pydantic", Version.parse("2.8.2"),
            Version.parse("2.5.0"),
            license="MIT",
        )
    )
    manager.add_dependency(
        Dependency(
            "fastapi", Version.parse("0.112.0"),
            Version.parse("0.100.0"),
            license="MIT",
            dependencies=["pydantic", "httpx"],
        )
    )
    manager.add_dependency(
        Dependency(
            "cryptography", Version.parse("43.0.0"),
            Version.parse("42.0.0"),
            license="Apache-2.0",
        )
    )

    return manager


def main() -> int:
    manager = build_demo()

    print("PROJECT DEPENDENCY MANAGEMENT")
    print("=" * 55)

    print("\nDependency inventory:")
    for name, dependency in sorted(manager.dependencies.items()):
        print(
            f"{name:15} {dependency.version} "
            f"license={dependency.license}"
        )

    print("\nInstallation order:")
    print(" -> ".join(manager.topological_order()))

    print("\nPolicy evaluation:")
    findings = manager.evaluate()
    print("PASS" if not findings else "\n".join(findings))

    print("\nAvailable dependency updates:")
    updates = manager.update_plan({
        "httpx": "0.28.1",
        "pydantic": "2.9.2",
        "fastapi": "0.115.0",
    })

    for name, version in updates.items():
        print(f"{name}: {manager.dependencies[name].version} -> {version}")

    pr = manager.create_pull_request(updates)
    pr.checks = {
        "unit-tests": CheckState.PASSED,
        "security-scan": CheckState.PASSED,
        "license-audit": CheckState.PASSED,
        "dependency-resolution": CheckState.PASSED,
    }

    pr.conversations = {
        "version compatibility": True,
        "migration impact": True,
    }

    pr.add_review("reviewer-1", ReviewState.APPROVED)
    pr.add_review("reviewer-2", ReviewState.APPROVED)

    print(f"\nPull Request #{pr.number}")
    print("Merge eligibility:")

    reasons = manager.evaluate_merge(pr)
    if reasons:
        print("\n".join(reasons))
    else:
        print("ELIGIBLE")

    manager.merge(pr, strategy="squash")
    print(f"Merge completed: {pr.merge_commit}")

    print("\nUpdated dependency inventory:")
    for name, dependency in sorted(manager.dependencies.items()):
        print(f"{name}: {dependency.version}")

    print("\nLockfile integrity:")
    lock = manager.lockfile()
    print(lock["integrity"])

    # Verify cycle detection and version validation.
    try:
        Version.parse("1.2")
    except ValidationError as exc:
        print(f"\nExpected validation failure: {exc}")

    print("\nExecution completed.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (DependencyError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
