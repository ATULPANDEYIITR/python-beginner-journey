"""Mutable and Immutable Data: executable learning case study.

Run with:
    python mutable_immutable_data.py

The examples progress from object identity and mutation to immutable
structures, defensive copying, dataclass design, hashing, concurrency-safe
snapshots, and persistent-style state transitions.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from copy import deepcopy
from types import MappingProxyType
from typing import Any, Mapping


def heading(title: str) -> None:
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def demonstrate_scalar_immutability() -> None:
    heading("Scalar values and rebinding")

    value = 10
    original_id = id(value)

    # Integers are immutable. Adding one does not modify the integer object;
    # Python creates another integer and rebinds the variable name.
    value += 5

    print("value:", value)
    print("original integer object still existed:", original_id != id(value))

    text = "pull-request"
    text_id = id(text)
    text = text.upper()

    print("text:", text)
    print("string was replaced rather than modified:", text_id != id(text))


def demonstrate_mutable_aliasing() -> None:
    heading("Mutable objects and aliasing")

    labels = ["backend", "database"]
    another_reference = labels

    # Both names refer to the same list, so append mutates the shared object.
    another_reference.append("security")

    print("labels:", labels)
    print("same object:", labels is another_reference)

    copied_labels = labels.copy()
    copied_labels.append("testing")

    print("original after shallow copy mutation:", labels)
    print("copy after mutation:", copied_labels)


def demonstrate_nested_shallow_copy() -> None:
    heading("Nested data: shallow copy versus deep copy")

    review = {
        "title": "Improve validation",
        "files": ["validator.py", "tests/test_validator.py"],
        "metadata": {"priority": "high", "labels": ["review", "backend"]},
    }

    shallow = review.copy()
    deep = deepcopy(review)

    # The outer dictionaries differ, but nested mutable values are shared by
    # a shallow copy.
    shallow["metadata"]["labels"].append("security")
    shallow["files"].append("README.md")

    # deepcopy recursively creates independent nested objects.
    deep["metadata"]["labels"].append("documentation")

    print("original:", review)
    print("shallow copy:", shallow)
    print("deep copy:", deep)
    print(
        "nested metadata shared by shallow copy:",
        review["metadata"] is shallow["metadata"],
    )
    print(
        "nested metadata shared by deep copy:",
        review["metadata"] is deep["metadata"],
    )


def demonstrate_mutable_default_trap() -> None:
    heading("Avoiding shared mutable defaults")

    def add_label(labels: list[str] | None = None, label: str = "") -> list[str]:
        # None is used as the default marker so every call creates its own
        # mutable list rather than sharing one list between calls.
        if labels is None:
            labels = []
        labels.append(label)
        return labels

    first = add_label(label="backend")
    second = add_label(label="database")

    print("first:", first)
    print("second:", second)


@dataclass
class MutablePullRequest:
    title: str
    labels: list[str]
    changed_files: list[str]

    def add_label(self, label: str) -> None:
        if label not in self.labels:
            self.labels.append(label)

    def add_file(self, filename: str) -> None:
        if filename not in self.changed_files:
            self.changed_files.append(filename)


@dataclass(frozen=True)
class ImmutablePullRequest:
    title: str
    labels: tuple[str, ...]
    changed_files: tuple[str, ...]

    def with_label(self, label: str) -> "ImmutablePullRequest":
        if label in self.labels:
            return self
        return replace(self, labels=self.labels + (label,))

    def with_file(self, filename: str) -> "ImmutablePullRequest":
        if filename in self.changed_files:
            return self
        return replace(self, changed_files=self.changed_files + (filename,))


def demonstrate_dataclass_design() -> None:
    heading("Mutable and immutable domain objects")

    mutable_pr = MutablePullRequest(
        title="Improve validation",
        labels=["backend"],
        changed_files=["validator.py"],
    )
    mutable_pr.add_label("review")
    mutable_pr.add_file("tests/test_validator.py")

    print("mutable PR:", mutable_pr)

    immutable_pr = ImmutablePullRequest(
        title="Improve validation",
        labels=("backend",),
        changed_files=("validator.py",),
    )
    updated_pr = immutable_pr.with_label("review")
    updated_pr = updated_pr.with_file("tests/test_validator.py")

    print("original immutable PR:", immutable_pr)
    print("new immutable PR:", updated_pr)
    print("same object after non-changing update:", updated_pr.with_label("review") is updated_pr)


def demonstrate_read_only_views() -> None:
    heading("Read-only views are not the same as immutable ownership")

    configuration = {"required_reviewers": 2, "required_checks": ["tests", "lint"]}
    read_only = MappingProxyType(configuration)

    print("read-only configuration:", dict(read_only))

    try:
        read_only["required_reviewers"] = 3
    except TypeError as exc:
        print("direct mutation blocked:", exc)

    # MappingProxyType protects the view, but the original owner can still
    # mutate the underlying dictionary.
    configuration["required_reviewers"] = 3
    print("view reflects owner mutation:", dict(read_only))


def demonstrate_hashability() -> None:
    heading("Immutability and hashability")

    mutable_labels = ["backend", "review"]

    try:
        hash(mutable_labels)
    except TypeError as exc:
        print("list cannot be hashed:", exc)

    immutable_labels = ("backend", "review")
    print("tuple hash:", hash(immutable_labels))

    # Immutable values can safely participate in sets and dictionary keys when
    # every component is itself hashable.
    review_cache: dict[tuple[str, tuple[str, ...]], str] = {
        ("PR-1042", immutable_labels): "approved snapshot"
    }

    print("cache lookup:", review_cache[("PR-1042", immutable_labels)])


@dataclass(frozen=True)
class ReviewSnapshot:
    pull_request_id: str
    revision: int
    approvals: tuple[str, ...]
    checks: tuple[tuple[str, str], ...]

    def approve(self, reviewer: str) -> "ReviewSnapshot":
        if reviewer in self.approvals:
            return self
        return replace(self, approvals=self.approvals + (reviewer,))

    def set_check(self, name: str, status: str) -> "ReviewSnapshot":
        valid_statuses = {"pending", "passed", "failed"}
        if status not in valid_statuses:
            raise ValueError(f"unsupported check status: {status}")

        updated = dict(self.checks)
        updated[name] = status

        return replace(self, checks=tuple(sorted(updated.items())))

    def next_revision(self) -> "ReviewSnapshot":
        return replace(self, revision=self.revision + 1, approvals=())


def demonstrate_state_transitions() -> None:
    heading("Immutable state transitions")

    state = ReviewSnapshot(
        pull_request_id="PR-1042",
        revision=1,
        approvals=(),
        checks=(("lint", "pending"), ("tests", "pending")),
    )

    approved_state = state.approve("reviewer-a")
    approved_state = approved_state.set_check("lint", "passed")
    approved_state = approved_state.set_check("tests", "passed")

    print("initial state:", state)
    print("updated state:", approved_state)

    revised = approved_state.next_revision()

    print("after new revision:", revised)
    print("old approval remains in previous snapshot:", approved_state.approvals)
    print("new revision starts without old approvals:", revised.approvals)


def process_batch(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return transformed records without mutating caller-owned input."""

    result: list[dict[str, Any]] = []

    for record in records:
        if not isinstance(record.get("id"), str):
            raise ValueError("record id must be a string")

        transformed = deepcopy(record)
        transformed["processed"] = True
        transformed["labels"] = sorted(set(transformed.get("labels", [])))
        result.append(transformed)

    return result


def demonstrate_defensive_copying() -> None:
    heading("Defensive copying at API boundaries")

    incoming = [
        {"id": "PR-1042", "labels": ["review", "review"], "metadata": {"team": "platform"}}
    ]

    processed = process_batch(incoming)
    processed[0]["metadata"]["team"] = "security"

    print("caller-owned input:", incoming)
    print("independent processed data:", processed)


class ImmutableEventLog:
    """Persistent-style event history using tuples.

    Each append creates a new history value. Existing histories remain valid
    snapshots, which makes the structure useful for auditing and replay.
    """

    def __init__(self, events: tuple[tuple[str, str], ...] = ()) -> None:
        self._events = events

    @property
    def events(self) -> tuple[tuple[str, str], ...]:
        return self._events

    def append(self, event_type: str, value: str) -> "ImmutableEventLog":
        if not event_type or not value:
            raise ValueError("event type and value must be non-empty")
        return ImmutableEventLog(self._events + ((event_type, value),))


def demonstrate_snapshot_history() -> None:
    heading("Persistent-style immutable history")

    history = ImmutableEventLog()
    created = history.append("created", "PR-1042")
    reviewed = created.append("approved", "reviewer-a")
    merged = reviewed.append("merged", "squash")

    print("empty history:", history.events)
    print("created snapshot:", created.events)
    print("reviewed snapshot:", reviewed.events)
    print("merged snapshot:", merged.events)


def compare_update_costs() -> None:
    heading("Performance implications")

    mutable = list(range(10_000))
    immutable = tuple(range(10_000))

    mutable.append(10_000)
    immutable = immutable + (10_000,)

    print("mutable list length:", len(mutable))
    print("immutable tuple length:", len(immutable))
    print(
        "important distinction:",
        "list append changes one existing object; tuple concatenation creates a new tuple",
    )

    print(
        "For very large immutable state, repeated copying can be expensive; "
        "persistent data structures or carefully scoped immutable snapshots may "
        "be preferable when structural sharing is required."
    )


def validate_immutable_configuration(config: Mapping[str, Any]) -> tuple[tuple[str, Any], ...]:
    required = {"repository", "protected_branch", "required_approvals"}

    missing = required - config.keys()
    if missing:
        raise ValueError(f"missing configuration fields: {sorted(missing)}")

    approvals = config["required_approvals"]
    if not isinstance(approvals, int) or approvals < 0:
        raise ValueError("required_approvals must be a non-negative integer")

    # Tuples make the returned configuration resistant to accidental
    # modification by consumers of this function.
    return tuple(sorted(config.items(), key=lambda item: item[0]))


def demonstrate_validation() -> None:
    heading("Validation before freezing data")

    raw = {
        "repository": "platform-service",
        "protected_branch": "main",
        "required_approvals": 2,
    }

    frozen_configuration = validate_immutable_configuration(raw)
    print("validated immutable representation:", frozen_configuration)

    try:
        validate_immutable_configuration(
            {
                "repository": "platform-service",
                "protected_branch": "main",
                "required_approvals": -1,
            }
        )
    except ValueError as exc:
        print("invalid configuration rejected:", exc)


def demonstrate_common_boundary_rule() -> None:
    heading("A practical rule for mutable and immutable boundaries")

    internal_state = {
        "labels": ["backend"],
        "files": ["service.py"],
    }

    def snapshot(state: Mapping[str, Any]) -> tuple[tuple[str, tuple[str, ...]], ...]:
        return tuple(
            (key, tuple(value))
            for key, value in sorted(state.items())
        )

    stable_snapshot = snapshot(internal_state)
    internal_state["labels"].append("security")

    print("mutable internal state:", internal_state)
    print("previous immutable snapshot:", stable_snapshot)


def run() -> None:
    demonstrate_scalar_immutability()
    demonstrate_mutable_aliasing()
    demonstrate_nested_shallow_copy()
    demonstrate_mutable_default_trap()
    demonstrate_dataclass_design()
    demonstrate_read_only_views()
    demonstrate_hashability()
    demonstrate_state_transitions()
    demonstrate_defensive_copying()
    demonstrate_snapshot_history()
    compare_update_costs()
    demonstrate_validation()
    demonstrate_common_boundary_rule()

    heading("Completed")
    print("The demonstrations finished without requiring external packages.")


if __name__ == "__main__":
    run()
