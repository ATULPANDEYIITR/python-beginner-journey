from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from heapq import heappop, heappush
from pathlib import Path
from typing import Any, Iterable
import json
import tempfile
import unittest


@dataclass
class WorkItem:
    item_id: str
    title: str
    category: str
    priority: int
    estimated_hours: float
    tags: set[str] = field(default_factory=set)
    dependencies: list[str] = field(default_factory=list)
    status: str = "pending"

    def __post_init__(self) -> None:
        if not self.item_id.strip() or not self.title.strip():
            raise ValueError("An item requires a non-empty ID and title.")
        if self.priority not in range(1, 6):
            raise ValueError("Priority must be between 1 and 5.")
        if self.estimated_hours < 0:
            raise ValueError("Estimated hours cannot be negative.")
        if self.status not in {"pending", "in_progress", "completed"}:
            raise ValueError(f"Unsupported status: {self.status}")


class WorkQueue:
    """Coordinate a list, dictionary, heap, set, and dependency graph."""

    def __init__(self) -> None:
        self.items: dict[str, WorkItem] = {}
        self.insertion_order: list[str] = []
        self.pending_heap: list[tuple[int, str]] = []
        self.completed_ids: set[str] = set()
        self.categories: defaultdict[str, set[str]] = defaultdict(set)
        self.dependencies: dict[str, set[str]] = {}
        self.activity: deque[str] = deque(maxlen=20)

    def add(self, item: WorkItem) -> None:
        if item.item_id in self.items:
            raise ValueError(f"Duplicate item ID: {item.item_id}")

        unknown = set(item.dependencies) - self.items.keys()
        if unknown:
            raise ValueError(f"Dependencies must exist first: {sorted(unknown)}")

        self.items[item.item_id] = item
        self.insertion_order.append(item.item_id)
        self.categories[item.category].add(item.item_id)
        self.dependencies[item.item_id] = set(item.dependencies)

        if item.status == "completed":
            self.completed_ids.add(item.item_id)
        elif item.status == "pending":
            heappush(self.pending_heap, (item.priority, item.item_id))

        self.activity.append(f"Added {item.item_id}")

    def ready_items(self) -> list[WorkItem]:
        """Return pending items whose dependencies are all completed."""
        return [
            self.items[item_id]
            for item_id in self.insertion_order
            if self.items[item_id].status == "pending"
            and self.dependencies[item_id] <= self.completed_ids
        ]

    def next_ready_item(self) -> WorkItem | None:
        """Use a min-heap while discarding stale entries lazily."""
        ready_ids = {item.item_id for item in self.ready_items()}

        while self.pending_heap:
            priority, item_id = heappop(self.pending_heap)
            item = self.items[item_id]

            if item.status != "pending" or priority != item.priority:
                continue

            if item_id not in ready_ids:
                heappush(self.pending_heap, (priority, item_id))
                return None

            return item

        return None

    def start(self, item_id: str) -> None:
        item = self._get(item_id)

        if item.status != "pending":
            raise ValueError(f"{item_id} is not pending.")

        if not self.dependencies[item_id] <= self.completed_ids:
            raise ValueError(f"Dependencies are incomplete for {item_id}.")

        item.status = "in_progress"
        self.activity.append(f"Started {item_id}")

    def complete(self, item_id: str) -> None:
        item = self._get(item_id)

        if item.status != "in_progress":
            raise ValueError(f"{item_id} must be in progress before completion.")

        item.status = "completed"
        self.completed_ids.add(item_id)
        self.activity.append(f"Completed {item_id}")

    def search_tags(self, required: set[str]) -> list[WorkItem]:
        """Set inclusion implements an AND search across tags."""
        return [
            item
            for item in self.items.values()
            if required <= item.tags
        ]

    def category_intersection(self, first: str, second: str) -> set[str]:
        return self.categories[first] & self.categories[second]

    def effort_by_category(self) -> dict[str, float]:
        totals: defaultdict[str, float] = defaultdict(float)
        for item in self.items.values():
            totals[item.category] += item.estimated_hours
        return dict(totals)

    def dependency_order(self) -> list[str]:
        """Kahn's algorithm detects cycles and produces a valid topological order."""
        indegree = {
            item_id: len(dependencies)
            for item_id, dependencies in self.dependencies.items()
        }
        dependents: defaultdict[str, list[str]] = defaultdict(list)

        for item_id, dependencies in self.dependencies.items():
            for dependency in dependencies:
                dependents[dependency].append(item_id)

        ready = deque(
            item_id for item_id in self.insertion_order
            if indegree[item_id] == 0
        )
        result: list[str] = []

        while ready:
            current = ready.popleft()
            result.append(current)

            for dependent in dependents[current]:
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    ready.append(dependent)

        if len(result) != len(self.items):
            raise ValueError("Dependency graph contains a cycle.")

        return result

    def snapshot(self) -> dict[str, Any]:
        """Convert sets and domain objects into JSON-compatible structures."""
        return {
            "items": [
                {
                    "item_id": item.item_id,
                    "title": item.title,
                    "category": item.category,
                    "priority": item.priority,
                    "estimated_hours": item.estimated_hours,
                    "tags": sorted(item.tags),
                    "dependencies": sorted(item.dependencies),
                    "status": item.status,
                }
                for item in (self.items[key] for key in self.insertion_order)
            ],
            "completed_ids": sorted(self.completed_ids),
            "categories": {
                category: sorted(ids)
                for category, ids in self.categories.items()
            },
            "activity": list(self.activity),
        }

    def export_json(self, path: Path) -> None:
        path.write_text(
            json.dumps(self.snapshot(), indent=2),
            encoding="utf-8",
        )

    def _get(self, item_id: str) -> WorkItem:
        try:
            return self.items[item_id]
        except KeyError as exc:
            raise KeyError(f"Unknown item: {item_id}") from exc


def demonstrate_basic_structures() -> None:
    print("\n--- Lists, tuples, dictionaries, sets, and deques ---")

    deployment_stages = ["build", "test", "stage", "deploy"]
    immutable_coordinates = (28.6139, 77.2090)
    build_metadata = {
        "version": "2.4.0",
        "environment": "staging",
        "passed": True,
    }
    required_permissions = {"read", "review", "merge"}
    recent_events = deque(
        ["branch_created", "pull_request_opened"],
        maxlen=3,
    )

    deployment_stages.append("verify")
    required_permissions.add("audit")
    recent_events.append("review_requested")

    print("Stages:", deployment_stages)
    print("Coordinates:", immutable_coordinates)
    print("Metadata:", build_metadata)
    print("Permissions:", sorted(required_permissions))
    print("Recent events:", list(recent_events))


def demonstrate_work_queue() -> WorkQueue:
    print("\n--- Coordinated work-management data structures ---")

    queue = WorkQueue()

    queue.add(WorkItem(
        "TASK-100",
        "Validate incoming records",
        "data",
        1,
        2.5,
        {"validation", "quality"},
    ))
    queue.add(WorkItem(
        "TASK-101",
        "Create normalized storage",
        "database",
        2,
        4.0,
        {"storage", "quality"},
        ["TASK-100"],
    ))
    queue.add(WorkItem(
        "TASK-102",
        "Build operational dashboard",
        "analytics",
        1,
        5.0,
        {"dashboard", "reporting"},
        ["TASK-101"],
    ))
    queue.add(WorkItem(
        "TASK-103",
        "Document validation outcomes",
        "documentation",
        3,
        1.0,
        {"validation", "reporting"},
        ["TASK-100"],
    ))

    print("Dependency order:", queue.dependency_order())
    print("Initially ready:", [item.item_id for item in queue.ready_items()])
    print(
        "Items with validation and quality tags:",
        [item.item_id for item in queue.search_tags({"validation", "quality"})],
    )
    print("Effort totals:", queue.effort_by_category())

    selected = queue.next_ready_item()
    if selected is not None:
        print("Selected priority item:", selected.item_id)
        queue.start(selected.item_id)
        queue.complete(selected.item_id)

    print("Ready after completion:", [
        item.item_id for item in queue.ready_items()
    ])

    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "work_items.json"
        queue.export_json(output)
        loaded = json.loads(output.read_text(encoding="utf-8"))
        print("Exported item count:", len(loaded["items"]))

    return queue


def validate_records(
    records: Iterable[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Separate valid records from invalid records without losing error details."""
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for position, record in enumerate(records):
        errors: list[str] = []
        record_id = record.get("id")
        amount = record.get("amount")

        if not isinstance(record_id, str) or not record_id.strip():
            errors.append("id must be a non-empty string")
        elif record_id in seen_ids:
            errors.append("id must be unique")

        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            errors.append("amount must be numeric")
        elif amount < 0:
            errors.append("amount cannot be negative")

        if errors:
            rejected.append({
                "position": position,
                "record": record,
                "errors": errors,
            })
            continue

        seen_ids.add(record_id)
        accepted.append({
            "id": record_id,
            "amount": float(amount),
        })

    return accepted, rejected


def demonstrate_data_processing() -> None:
    print("\n--- Validation and aggregation across structures ---")

    incoming = [
        {"id": "R-1", "amount": 150.0},
        {"id": "R-2", "amount": 220},
        {"id": "R-1", "amount": 75},
        {"id": "R-4", "amount": -10},
        {"id": "", "amount": 45},
        {"id": "R-5", "amount": True},
    ]

    accepted, rejected = validate_records(incoming)
    amount_by_id = {row["id"]: row["amount"] for row in accepted}
    amount_buckets = Counter(
        "high" if amount >= 200 else "standard"
        for amount in amount_by_id.values()
    )

    print("Accepted records:", amount_by_id)
    print("Amount buckets:", dict(amount_buckets))
    print("Rejected count:", len(rejected))

    for error in rejected:
        print(f"Rejected position {error['position']}: {error['errors']}")


def demonstrate_heap_scheduling() -> None:
    print("\n--- Heap-based scheduling ---")

    jobs = [
        (3, "refresh-index"),
        (1, "repair-records"),
        (2, "rebuild-summary"),
        (1, "verify-integrity"),
    ]

    heap: list[tuple[int, str]] = []
    for job in jobs:
        heappush(heap, job)

    while heap:
        priority, name = heappop(heap)
        print(f"Priority {priority}: {name}")


class DataStructureTests(unittest.TestCase):
    def test_duplicate_ids_are_rejected(self) -> None:
        queue = WorkQueue()
        item = WorkItem("A", "First task", "data", 1, 1)
        queue.add(item)

        with self.assertRaises(ValueError):
            queue.add(WorkItem("A", "Duplicate task", "data", 2, 1))

    def test_dependency_blocks_start(self) -> None:
        queue = WorkQueue()
        queue.add(WorkItem("A", "Parent", "data", 1, 1))
        queue.add(WorkItem("B", "Child", "data", 2, 1, dependencies=["A"]))

        with self.assertRaises(ValueError):
            queue.start("B")

    def test_completed_dependency_unlocks_child(self) -> None:
        queue = WorkQueue()
        queue.add(WorkItem("A", "Parent", "data", 1, 1))
        queue.add(WorkItem("B", "Child", "data", 2, 1, dependencies=["A"]))

        queue.start("A")
        queue.complete("A")

        self.assertIn("B", [item.item_id for item in queue.ready_items()])

    def test_dependency_order_detects_cycle(self) -> None:
        queue = WorkQueue()
        queue.add(WorkItem("A", "First", "data", 1, 1))
        queue.add(WorkItem("B", "Second", "data", 1, 1, dependencies=["A"]))

        queue.dependencies["A"].add("B")

        with self.assertRaises(ValueError):
            queue.dependency_order()

    def test_boolean_is_not_accepted_as_amount(self) -> None:
        accepted, rejected = validate_records([{"id": "X", "amount": True}])
        self.assertEqual(accepted, [])
        self.assertEqual(len(rejected), 1)


def main() -> None:
    demonstrate_basic_structures()
    demonstrate_work_queue()
    demonstrate_data_processing()
    demonstrate_heap_scheduling()

    print("\n--- Automated verification ---")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DataStructureTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
