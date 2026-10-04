#!/usr/bin/env python3
"""
Copying Data: shallow copies, deep copies, mutable aliases, recursive copying,
copy-on-write style techniques, and safe copying of structured application data.

The examples use realistic application data rather than isolated syntax exercises.
Everything uses the Python standard library and can be executed directly.
"""

from __future__ import annotations

from copy import copy, deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import json
import sys


def heading(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def show_identity(label: str, left: Any, right: Any) -> None:
    print(f"{label}: same object={left is right}, equal value={left == right}")


def demonstrate_assignment_aliasing() -> None:
    heading("Assignment creates an alias, not a copy")

    source = {
        "repository": "analytics-platform",
        "settings": {"retention_days": 30},
        "tags": ["python", "data"],
    }

    alias = source
    alias["settings"]["retention_days"] = 90
    alias["tags"].append("production")

    print("Source after changing alias:")
    print(json.dumps(source, indent=2))

    show_identity("source and alias", source, alias)
    print(
        "Both names refer to the same dictionary, so a mutation through either "
        "name changes the same object."
    )


def demonstrate_shallow_copy() -> None:
    heading("Shallow copy: independent outer container, shared nested objects")

    source = {
        "service": "billing",
        "limits": {"requests_per_minute": 500},
        "owners": ["platform", "finance"],
    }

    cloned = source.copy()

    cloned["service"] = "billing-canary"
    cloned["limits"]["requests_per_minute"] = 1000
    cloned["owners"].append("security")

    print("Original:")
    print(json.dumps(source, indent=2))
    print("\nShallow copy:")
    print(json.dumps(cloned, indent=2))

    show_identity("outer dictionaries", source, cloned)
    show_identity("nested limits dictionaries", source["limits"], cloned["limits"])
    show_identity("nested owner lists", source["owners"], cloned["owners"])

    print(
        "\nThe top-level dictionary was copied, but references stored inside it "
        "were copied rather than the nested objects themselves."
    )


def demonstrate_deep_copy() -> None:
    heading("Deep copy: recursively independent mutable structure")

    source = {
        "service": "checkout",
        "deployment": {
            "regions": ["ap-south-1", "eu-west-1"],
            "environment": {"name": "production", "replicas": 4},
        },
    }

    cloned = deepcopy(source)
    cloned["deployment"]["regions"].append("us-east-1")
    cloned["deployment"]["environment"]["replicas"] = 8

    print("Original:")
    print(json.dumps(source, indent=2))
    print("\nDeep copy after mutation:")
    print(json.dumps(cloned, indent=2))

    show_identity(
        "deployment dictionaries",
        source["deployment"],
        cloned["deployment"],
    )
    show_identity(
        "region lists",
        source["deployment"]["regions"],
        cloned["deployment"]["regions"],
    )


@dataclass
class UserPreferences:
    theme: str
    notification_channels: list[str] = field(default_factory=list)


@dataclass
class Account:
    account_id: str
    owner: str
    preferences: UserPreferences
    feature_flags: dict[str, bool]
    audit_metadata: dict[str, Any] = field(default_factory=dict)


def demonstrate_object_copying() -> None:
    heading("Copying custom objects")

    account = Account(
        account_id="ACC-2048",
        owner="operations",
        preferences=UserPreferences(
            theme="dark",
            notification_channels=["email", "pager"],
        ),
        feature_flags={"new_dashboard": True, "risk_engine": False},
        audit_metadata={"created_by": "admin", "revision": 7},
    )

    shallow = copy(account)
    deep = deepcopy(account)

    shallow.preferences.notification_channels.append("sms")
    shallow.feature_flags["risk_engine"] = True

    deep.preferences.theme = "light"
    deep.audit_metadata["revision"] = 8

    print("Original account:")
    print(account)

    print("\nAfter changing shallow copy:")
    print(shallow)

    print("\nAfter changing deep copy:")
    print(deep)

    show_identity("account/preferences", account.preferences, shallow.preferences)
    show_identity("account/preferences", account.preferences, deep.preferences)
    show_identity("account/feature_flags", account.feature_flags, shallow.feature_flags)
    show_identity("account/feature_flags", account.feature_flags, deep.feature_flags)


def demonstrate_nested_collections() -> None:
    heading("Copying nested collections safely")

    records = [
        {"id": 101, "labels": ["verified", "priority"], "metrics": {"score": 91}},
        {"id": 102, "labels": ["pending"], "metrics": {"score": 76}},
    ]

    shallow = list(records)
    deep = deepcopy(records)

    shallow[0]["labels"].append("reviewed")
    deep[1]["metrics"]["score"] = 88

    print("Original records:")
    print(json.dumps(records, indent=2))

    print("\nShallow copy:")
    print(json.dumps(shallow, indent=2))

    print("\nDeep copy:")
    print(json.dumps(deep, indent=2))


def demonstrate_tuple_and_immutable_values() -> None:
    heading("Immutable values inside copied structures")

    source = {
        "name": "cache-policy",
        "version": 3,
        "enabled": True,
        "coordinates": (28.6139, 77.2090),
    }

    cloned = deepcopy(source)

    print("source:", source)
    print("cloned:", cloned)
    print(
        "Integers, booleans, strings, and tuples containing immutable values do "
        "not require independent mutable state in the same way lists and dicts do."
    )


def demonstrate_copying_with_cycles() -> None:
    heading("Deep copy of cyclic structures")

    node: dict[str, Any] = {"name": "root"}
    node["children"] = []
    node["parent"] = node

    cloned = deepcopy(node)

    print("Original has self-reference:", node["parent"] is node)
    print("Clone has self-reference:", cloned["parent"] is cloned)
    print("Clone is independent:", cloned is not node)


def validate_snapshot(snapshot: dict[str, Any]) -> None:
    required = {"version", "service", "configuration"}
    missing = required - snapshot.keys()

    if missing:
        raise ValueError(f"Snapshot is missing required fields: {sorted(missing)}")

    if not isinstance(snapshot["version"], int) or snapshot["version"] < 1:
        raise ValueError("Snapshot version must be a positive integer.")

    if not isinstance(snapshot["configuration"], dict):
        raise TypeError("Snapshot configuration must be a dictionary.")


def create_configuration_snapshot(
    live_configuration: dict[str, Any],
) -> dict[str, Any]:
    """
    A snapshot is intended to remain stable even when the live configuration
    changes. A deep copy prevents later mutations from changing the snapshot.
    """
    snapshot = {
        "version": live_configuration["version"],
        "service": live_configuration["service"],
        "configuration": deepcopy(live_configuration["configuration"]),
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }

    validate_snapshot(snapshot)
    return snapshot


def demonstrate_snapshot_pattern() -> None:
    heading("Production-style configuration snapshot")

    live_configuration = {
        "version": 12,
        "service": "payment-api",
        "configuration": {
            "timeouts": {"connect": 2, "read": 10},
            "features": {
                "fraud_detection": True,
                "async_settlement": False,
            },
            "regions": ["ap-south-1", "eu-central-1"],
        },
    }

    snapshot = create_configuration_snapshot(live_configuration)

    live_configuration["configuration"]["timeouts"]["read"] = 30
    live_configuration["configuration"]["regions"].append("us-east-1")
    live_configuration["configuration"]["features"]["async_settlement"] = True

    print("Live configuration:")
    print(json.dumps(live_configuration, indent=2))

    print("\nStable snapshot:")
    print(json.dumps(snapshot, indent=2))


def demonstrate_selective_copying() -> None:
    heading("Selective copying when a full deep copy is unnecessary")

    source = {
        "service": "search-api",
        "immutable_schema": ("query", "filters", "sort"),
        "runtime": {
            "workers": 8,
            "timeouts": {"request": 5},
        },
        "metadata": {
            "owner": "search-team",
            "documentation": "internal",
        },
    }

    selective = source.copy()
    selective["runtime"] = source["runtime"].copy()
    selective["runtime"]["timeouts"] = source["runtime"]["timeouts"].copy()

    selective["runtime"]["workers"] = 16
    selective["runtime"]["timeouts"]["request"] = 10

    print("Original:")
    print(json.dumps(source, indent=2))

    print("\nSelectively copied structure:")
    print(json.dumps(selective, indent=2))

    print(
        "\nSelective copying can be useful when the data model is known and only "
        "specific mutable layers need isolation. It requires stronger knowledge "
        "of the object graph than deepcopy()."
    )


class CopyPolicyError(ValueError):
    """Raised when a requested copying strategy is incompatible with policy."""


class ConfigurationStore:
    """
    Maintains live configuration and immutable-style snapshots.

    The store deliberately copies data at its public boundaries. This prevents
    callers from accidentally mutating internal state through retained aliases.
    """

    def __init__(self, initial: dict[str, Any]) -> None:
        self._state = deepcopy(initial)
        self._validate(self._state)
        self._history: list[dict[str, Any]] = []

    @staticmethod
    def _validate(state: dict[str, Any]) -> None:
        if not isinstance(state, dict):
            raise TypeError("State must be a dictionary.")
        if not isinstance(state.get("features"), dict):
            raise TypeError("State must contain a feature dictionary.")
        if not isinstance(state.get("limits"), dict):
            raise TypeError("State must contain a limits dictionary.")

    def read(self) -> dict[str, Any]:
        return deepcopy(self._state)

    def update_feature(self, name: str, enabled: bool) -> None:
        if not name.strip():
            raise ValueError("Feature name cannot be empty.")
        if not isinstance(enabled, bool):
            raise TypeError("Feature state must be boolean.")

        previous = deepcopy(self._state)
        self._state["features"][name] = enabled
        self._history.append(previous)

    def update_limit(self, name: str, value: int) -> None:
        if value < 0:
            raise ValueError("A limit cannot be negative.")

        previous = deepcopy(self._state)
        self._state["limits"][name] = value
        self._history.append(previous)

    def rollback(self) -> None:
        if not self._history:
            raise CopyPolicyError("There is no previous state to restore.")

        self._state = self._history.pop()

    def history_depth(self) -> int:
        return len(self._history)


def demonstrate_copy_boundary_design() -> None:
    heading("Copying at API boundaries")

    store = ConfigurationStore(
        {
            "features": {"audit_logging": True},
            "limits": {"requests_per_minute": 1000},
        }
    )

    external_view = store.read()
    external_view["features"]["audit_logging"] = False
    external_view["limits"]["requests_per_minute"] = 1

    print("Mutated caller-owned copy:")
    print(json.dumps(external_view, indent=2))

    print("\nInternal store remains protected:")
    print(json.dumps(store.read(), indent=2))

    store.update_feature("risk_scoring", True)
    store.update_limit("requests_per_minute", 2000)

    print("\nUpdated store:")
    print(json.dumps(store.read(), indent=2))
    print("History entries:", store.history_depth())

    store.rollback()
    print("\nAfter one rollback:")
    print(json.dumps(store.read(), indent=2))


def demonstrate_serialization_as_copy_boundary() -> None:
    heading("Serialization as a deliberate data-transfer boundary")

    original = {
        "job": "nightly-report",
        "parameters": {
            "regions": ["IN", "EU"],
            "include_failed": False,
        },
    }

    wire_payload = json.dumps(original)
    received = json.loads(wire_payload)

    received["parameters"]["regions"].append("US")

    print("Original:")
    print(json.dumps(original, indent=2))

    print("\nDeserialized copy:")
    print(json.dumps(received, indent=2))

    show_identity(
        "nested parameters after JSON round trip",
        original["parameters"],
        received["parameters"],
    )

    print(
        "\nSerialization is not a universal replacement for deepcopy. It changes "
        "the representation and can lose Python-specific types, identity, "
        "object references, precision, or custom behavior."
    )


def demonstrate_common_failure_modes() -> None:
    heading("Common copying failure modes")

    rows = [["A", "B"], ["C", "D"]]
    wrong = list(rows)
    correct = deepcopy(rows)

    wrong[0][0] = "X"
    correct[1][1] = "Y"

    print("Original after shallow mutation:")
    print(rows)

    print("Independent deep copy:")
    print(correct)

    print(
        "\nA frequent bug occurs when a developer assumes list(source) or "
        "source.copy() recursively duplicates nested mutable elements."
    )


def demonstrate_memory_and_performance() -> None:
    heading("Performance and memory considerations")

    large_records = [
        {
            "id": index,
            "attributes": {
                "active": True,
                "score": index % 100,
            },
        }
        for index in range(10_000)
    ]

    shallow = large_records.copy()
    deep = deepcopy(large_records)

    print("Records:", len(large_records))
    print("Top-level copy created:", len(shallow))
    print("Deep copy created:", len(deep))
    print(
        "Nested identity shared by shallow copy:",
        large_records[0]["attributes"] is shallow[0]["attributes"],
    )
    print(
        "Nested identity shared by deep copy:",
        large_records[0]["attributes"] is deep[0]["attributes"],
    )

    print(
        "\nDeep copying can consume substantially more memory and CPU because it "
        "traverses the object graph. Copy only the state that needs isolation "
        "when performance and ownership semantics permit it."
    )


def demonstrate_testing_copy_semantics() -> None:
    heading("Testing copy semantics")

    original = {
        "policy": {"max_retries": 3},
        "servers": ["api-1", "api-2"],
    }

    shallow = copy(original)
    deep = deepcopy(original)

    assert original is not shallow
    assert original is not deep
    assert original["policy"] is shallow["policy"]
    assert original["policy"] is not deep["policy"]

    shallow["policy"]["max_retries"] = 5
    assert original["policy"]["max_retries"] == 5

    deep["policy"]["max_retries"] = 7
    assert original["policy"]["max_retries"] == 5

    print("Copy identity and mutation-isolation assertions passed.")


def demonstrate_security_and_ownership() -> None:
    heading("Security and ownership considerations")

    credentials = {
        "service": "database",
        "connection": {
            "username": "service_account",
            "password": "example-only",
        },
    }

    copied_credentials = deepcopy(credentials)

    print(
        "A copy does not erase the original secret and does not encrypt the copy."
    )
    print(
        "Applications should avoid unnecessary duplication of secrets because "
        "each copy can increase the number of memory locations containing "
        "sensitive material."
    )

    copied_credentials["connection"]["password"] = "<rotated>"
    print("Original password unchanged:", credentials["connection"]["password"])
    print("Copied password:", copied_credentials["connection"]["password"])


def demonstrate_decision_rules() -> None:
    heading("Choosing a copying strategy")

    decisions = [
        (
            "Need another name for the same live state",
            "assignment",
            "An alias is intentional.",
        ),
        (
            "Need a new outer list/dict but shared nested objects are acceptable",
            "shallow copy",
            "Avoid unnecessary recursive copying.",
        ),
        (
            "Need an independently mutable nested structure",
            "deep copy",
            "Recursive mutable state must be isolated.",
        ),
        (
            "Only selected nested layers require isolation",
            "selective copy",
            "Explicitly copy the ownership boundaries.",
        ),
        (
            "Crossing a process or API boundary",
            "serialization",
            "Transfer a defined data representation.",
        ),
    ]

    for situation, strategy, reason in decisions:
        print(f"{situation}\n  Strategy: {strategy}\n  Reason: {reason}\n")


def main() -> None:
    print("COPYING DATA IN PYTHON")
    print(f"Python {sys.version.split()[0]}")

    demonstrate_assignment_aliasing()
    demonstrate_shallow_copy()
    demonstrate_deep_copy()
    demonstrate_object_copying()
    demonstrate_nested_collections()
    demonstrate_tuple_and_immutable_values()
    demonstrate_copying_with_cycles()
    demonstrate_snapshot_pattern()
    demonstrate_selective_copying()
    demonstrate_copy_boundary_design()
    demonstrate_serialization_as_copy_boundary()
    demonstrate_common_failure_modes()
    demonstrate_memory_and_performance()
    demonstrate_testing_copy_semantics()
    demonstrate_security_and_ownership()
    demonstrate_decision_rules()

    print("\nAll copying demonstrations completed successfully.")


if __name__ == "__main__":
    main()
