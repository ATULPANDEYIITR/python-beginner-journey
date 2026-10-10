"""
Practice: Python Data Structures

A self-contained practical exercise covering lists, tuples, dictionaries,
sets, stacks, queues, heaps, linked lists, trees, graphs, and hash-based
algorithms. Examples include validation, edge cases, complexity notes,
and executable assertions.

Run with:
    python practice_data_structures.py
"""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from heapq import heappush, heappop
from typing import Any, Iterable, Iterator, Optional


def print_heading(title: str) -> None:
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def demonstrate_lists() -> None:
    print_heading("Lists: ordered, mutable sequences")

    inventory = ["keyboard", "mouse", "monitor"]
    inventory.append("webcam")
    inventory.insert(1, "headset")
    inventory.remove("mouse")

    print("Inventory:", inventory)
    print("First two:", inventory[:2])
    print("Reversed:", inventory[::-1])

    # Comprehensions create a new list from a filtering and transformation rule.
    name_lengths = [len(item) for item in inventory if len(item) >= 6]
    print("Lengths of longer names:", name_lengths)

    # Sorting a copy preserves the original ordering.
    sorted_inventory = sorted(inventory, key=str.casefold)
    print("Sorted copy:", sorted_inventory)
    print("Original remains:", inventory)

    quantities = [12, 0, 7, 12, 3, 0]
    positive_quantities = [quantity for quantity in quantities if quantity > 0]
    print("Positive quantities:", positive_quantities)

    # Avoid removing items while iterating over the same list.
    remaining = [quantity for quantity in quantities if quantity != 0]
    assert remaining == [12, 7, 12, 3]

    # Assignment aliases a mutable list; slicing creates a shallow copy.
    original = [1, 2, 3]
    alias = original
    copied = original[:]
    alias.append(4)
    assert original == [1, 2, 3, 4]
    assert copied == [1, 2, 3]


def demonstrate_tuples() -> None:
    print_heading("Tuples: fixed-position records")

    employee = ("E104", "Operations Analyst", "Lucknow")
    employee_id, role, location = employee

    print(f"{employee_id}: {role}, {location}")

    # A trailing comma is necessary for a one-element tuple.
    single_value = ("approved",)
    assert isinstance(single_value, tuple)

    # Tuples are immutable, but can contain mutable objects.
    record = ("batch-17", ["pending", "pending"])
    record[1][0] = "processed"
    print("Tuple containing a mutable list:", record)

    # A tuple containing mutable, unhashable members cannot be used as a set key.
    try:
        hash(record)
    except TypeError:
        print("Expected behavior: tuple with a list is unhashable.")


def demonstrate_dictionaries() -> None:
    print_heading("Dictionaries: keyed records and aggregation")

    stock = {
        "LAPTOP": {"quantity": 14, "reorder_level": 5},
        "MOUSE": {"quantity": 3, "reorder_level": 10},
        "MONITOR": {"quantity": 8, "reorder_level": 4},
    }

    # get() avoids KeyError when a key may be absent.
    unknown = stock.get("TABLET")
    print("Unknown item:", unknown)

    # setdefault initializes a key only when it is missing.
    movements: dict[str, list[int]] = {}
    movements.setdefault("LAPTOP", []).extend([2, -1, 3])
    movements.setdefault("MOUSE", []).extend([-2, 1])

    print("Movements:", movements)

    reorder_items = {
        sku: details["quantity"]
        for sku, details in stock.items()
        if details["quantity"] < details["reorder_level"]
    }
    print("Items below reorder level:", reorder_items)

    # defaultdict handles repeated aggregation without explicit initialization.
    totals: defaultdict[str, int] = defaultdict(int)
    for sku, changes in movements.items():
        totals[sku] += sum(changes)

    print("Net movement:", dict(totals))

    # Dictionary union creates a merged dictionary in Python 3.9+.
    updated_stock = stock | {
        "TABLET": {"quantity": 6, "reorder_level": 2}
    }
    assert "TABLET" not in stock
    assert "TABLET" in updated_stock


def demonstrate_sets() -> None:
    print_heading("Sets: uniqueness and membership")

    completed = {"REQ-101", "REQ-102", "REQ-103", "REQ-103"}
    newly_submitted = {"REQ-103", "REQ-104", "REQ-105"}

    print("Unique completed requests:", completed)
    print("Intersection:", completed & newly_submitted)
    print("New requests:", newly_submitted - completed)
    print("All known requests:", completed | newly_submitted)
    print("Symmetric difference:", completed ^ newly_submitted)

    # Sets are appropriate for uniqueness and expected O(1) membership tests.
    assert "REQ-104" not in completed
    completed.add("REQ-104")
    assert "REQ-104" in completed

    # set() represents an empty set; {} represents an empty dictionary.
    assert isinstance(set(), set)
    assert isinstance({}, dict)


class Stack:
    """Last-in, first-out container implemented with a list."""

    def __init__(self) -> None:
        self._items: list[Any] = []

    def push(self, item: Any) -> None:
        self._items.append(item)

    def pop(self) -> Any:
        if not self._items:
            raise IndexError("Cannot pop from an empty stack")
        return self._items.pop()

    def peek(self) -> Any:
        if not self._items:
            raise IndexError("Cannot inspect an empty stack")
        return self._items[-1]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Any]:
        return iter(reversed(self._items))


class Queue:
    """First-in, first-out container implemented with deque."""

    def __init__(self) -> None:
        self._items: deque[Any] = deque()

    def enqueue(self, item: Any) -> None:
        self._items.append(item)

    def dequeue(self) -> Any:
        if not self._items:
            raise IndexError("Cannot dequeue from an empty queue")
        return self._items.popleft()

    def __len__(self) -> int:
        return len(self._items)


def demonstrate_stack_and_queue() -> None:
    print_heading("Stacks and queues")

    undo_stack = Stack()
    for action in ("create", "rename", "edit"):
        undo_stack.push(action)

    print("Undo order:", list(undo_stack))
    print("Next undo:", undo_stack.pop())

    jobs = Queue()
    for job in ("import.csv", "validate.csv", "report.csv"):
        jobs.enqueue(job)

    while len(jobs):
        print("Processing:", jobs.dequeue())

    try:
        jobs.dequeue()
    except IndexError as error:
        print("Expected queue error:", error)


def demonstrate_heap() -> None:
    print_heading("Heaps: priority scheduling")

    jobs = [
        (3, "Generate monthly report"),
        (1, "Resolve production incident"),
        (2, "Validate supplier records"),
    ]

    heap: list[tuple[int, str]] = []
    for priority, description in jobs:
        heappush(heap, (priority, description))

    while heap:
        priority, description = heappop(heap)
        print(f"Priority {priority}: {description}")

    # A min-heap exposes the smallest element, not a fully sorted list.
    assert heappop_or_none(heap) is None


def heappop_or_none(heap: list[Any]) -> Optional[Any]:
    return heappop(heap) if heap else None


@dataclass
class ListNode:
    value: Any
    next: Optional["ListNode"] = None


class SinglyLinkedList:
    """A singly linked list with O(1) append using a tail reference."""

    def __init__(self) -> None:
        self.head: Optional[ListNode] = None
        self.tail: Optional[ListNode] = None
        self.size = 0

    def append(self, value: Any) -> None:
        node = ListNode(value)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1

    def find(self, value: Any) -> Optional[ListNode]:
        current = self.head
        while current is not None:
            if current.value == value:
                return current
            current = current.next
        return None

    def delete_first(self, value: Any) -> bool:
        previous: Optional[ListNode] = None
        current = self.head

        while current is not None:
            if current.value == value:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next

                if current is self.tail:
                    self.tail = previous

                self.size -= 1
                return True

            previous, current = current, current.next

        return False

    def to_list(self) -> list[Any]:
        values: list[Any] = []
        current = self.head
        while current is not None:
            values.append(current.value)
            current = current.next
        return values


def demonstrate_linked_list() -> None:
    print_heading("Singly linked lists")

    history = SinglyLinkedList()
    for version in ("v1", "v2", "v3"):
        history.append(version)

    print("Versions:", history.to_list())
    print("Find v2:", history.find("v2").value)
    print("Delete v1:", history.delete_first("v1"))
    print("After deletion:", history.to_list())
    print("Delete missing version:", history.delete_first("v9"))


@dataclass
class TreeNode:
    key: int
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None


def bst_insert(root: Optional[TreeNode], key: int) -> TreeNode:
    """Insert unique integer keys into a binary search tree."""
    if root is None:
        return TreeNode(key)
    if key < root.key:
        root.left = bst_insert(root.left, key)
    elif key > root.key:
        root.right = bst_insert(root.right, key)
    return root


def bst_contains(root: Optional[TreeNode], key: int) -> bool:
    current = root
    while current is not None:
        if key == current.key:
            return True
        current = current.left if key < current.key else current.right
    return False


def inorder(root: Optional[TreeNode]) -> list[int]:
    if root is None:
        return []
    return inorder(root.left) + [root.key] + inorder(root.right)


def demonstrate_tree() -> None:
    print_heading("Binary search trees")

    root: Optional[TreeNode] = None
    for key in (50, 30, 70, 20, 40, 60, 80, 40):
        root = bst_insert(root, key)

    print("In-order traversal:", inorder(root))
    print("Contains 60:", bst_contains(root, 60))
    print("Contains 99:", bst_contains(root, 99))

    # An unbalanced BST can degrade to O(n) operations.
    # Self-balancing trees are preferable for adversarial or sorted input.


@dataclass
class WeightedGraph:
    adjacency: dict[str, dict[str, float]] = field(
        default_factory=lambda: defaultdict(dict)
    )

    def add_edge(
        self, source: str, destination: str, weight: float, bidirectional: bool = True
    ) -> None:
        if not source or not destination:
            raise ValueError("Vertex names cannot be empty")
        if weight < 0:
            raise ValueError("Dijkstra's algorithm requires non-negative weights")

        self.adjacency.setdefault(source, {})
        self.adjacency.setdefault(destination, {})
        self.adjacency[source][destination] = weight

        if bidirectional:
            self.adjacency[destination][source] = weight

    def shortest_path(
        self, start: str, target: str
    ) -> tuple[float, list[str]]:
        if start not in self.adjacency or target not in self.adjacency:
            return float("inf"), []

        distances = {start: 0.0}
        previous: dict[str, str] = {}
        frontier: list[tuple[float, str]] = [(0.0, start)]

        while frontier:
            distance, vertex = heappop(frontier)

            # Ignore stale heap entries after a better path is discovered.
            if distance != distances.get(vertex, float("inf")):
                continue

            if vertex == target:
                path = [target]
                while path[-1] != start:
                    path.append(previous[path[-1]])
                path.reverse()
                return distance, path

            for neighbor, weight in self.adjacency[vertex].items():
                candidate = distance + weight
                if candidate < distances.get(neighbor, float("inf")):
                    distances[neighbor] = candidate
                    previous[neighbor] = vertex
                    heappush(frontier, (candidate, neighbor))

        return float("inf"), []


def demonstrate_graph() -> None:
    print_heading("Graphs and shortest paths")

    graph = WeightedGraph()
    graph.add_edge("Warehouse", "Hub", 5)
    graph.add_edge("Warehouse", "Store-A", 12)
    graph.add_edge("Hub", "Store-A", 4)
    graph.add_edge("Hub", "Store-B", 7)
    graph.add_edge("Store-A", "Store-B", 2)

    distance, path = graph.shortest_path("Warehouse", "Store-B")
    print("Shortest route:", " -> ".join(path))
    print("Total travel cost:", distance)

    unreachable_cost, unreachable_path = graph.shortest_path(
        "Warehouse", "Unknown"
    )
    assert unreachable_cost == float("inf")
    assert unreachable_path == []


def demonstrate_frequency_algorithms() -> None:
    print_heading("Frequency counting and efficient lookups")

    events = [
        "login", "search", "login", "purchase",
        "search", "login", "logout", "purchase",
    ]

    frequency = Counter(events)
    print("Event frequencies:", frequency.most_common())
    print("Most frequent event:", frequency.most_common(1))

    def first_repeated(values: Iterable[Any]) -> Optional[Any]:
        seen: set[Any] = set()
        for value in values:
            if value in seen:
                return value
            seen.add(value)
        return None

    print("First repeated event:", first_repeated(events))
    assert first_repeated([1, 2, 3, 2, 1]) == 2
    assert first_repeated([]) is None


def demonstrate_data_validation() -> None:
    print_heading("Validating structured records")

    def normalize_employee(record: dict[str, Any]) -> dict[str, Any]:
        required = {"employee_id", "name", "hours"}
        missing = required - record.keys()
        if missing:
            raise ValueError(f"Missing fields: {sorted(missing)}")

        employee_id = record["employee_id"]
        name = record["name"]
        hours = record["hours"]

        if not isinstance(employee_id, str) or not employee_id.strip():
            raise ValueError("employee_id must be a non-empty string")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        if isinstance(hours, bool) or not isinstance(hours, (int, float)):
            raise ValueError("hours must be numeric")
        if not 0 <= hours <= 168:
            raise ValueError("hours must be between 0 and 168")

        return {
            "employee_id": employee_id.strip().upper(),
            "name": name.strip(),
            "hours": float(hours),
        }

    valid = normalize_employee({
        "employee_id": " e104 ",
        "name": "Asha Verma",
        "hours": 40,
    })
    print("Normalized record:", valid)

    try:
        normalize_employee({
            "employee_id": "E105",
            "name": "Ravi",
            "hours": 200,
        })
    except ValueError as error:
        print("Rejected record:", error)


def demonstrate_copying_and_complexity() -> None:
    print_heading("Copying, mutation, and performance")

    nested = {"teams": [{"name": "Data", "members": ["Asha"]}]}

    # A shallow copy duplicates only the outer dictionary.
    shallow = nested.copy()
    shallow["teams"][0]["members"].append("Ravi")
    assert "Ravi" in nested["teams"][0]["members"]

    # deepcopy recursively copies nested mutable objects.
    from copy import deepcopy

    independent = deepcopy(nested)
    independent["teams"][0]["members"].append("Meera")
    assert "Meera" not in nested["teams"][0]["members"]

    print("Original after shallow mutation:", nested)
    print("Independent deep copy:", independent)

    print(
        "Typical complexity: list append O(1) amortized; list membership O(n); "
        "dictionary/set lookup O(1) average; deque append/popleft O(1); "
        "heap push/pop O(log n); linked-list search O(n)."
    )


def run_assertions() -> None:
    # These checks act as lightweight regression tests for the examples.
    assert Counter("banana").most_common(1)[0] == ("a", 3)

    stack = Stack()
    stack.push("first")
    stack.push("second")
    assert stack.pop() == "second"
    assert stack.pop() == "first"

    linked = SinglyLinkedList()
    linked.append(10)
    linked.append(20)
    assert linked.delete_first(10)
    assert linked.to_list() == [20]
    assert linked.delete_first(20)
    assert linked.head is None and linked.tail is None and linked.size == 0

    graph = WeightedGraph()
    graph.add_edge("A", "B", 2)
    graph.add_edge("B", "C", 3)
    graph.add_edge("A", "C", 9)
    cost, path = graph.shortest_path("A", "C")
    assert cost == 5 and path == ["A", "B", "C"]

    try:
        graph.add_edge("A", "D", -1)
    except ValueError:
        pass
    else:
        raise AssertionError("Negative graph weights must be rejected")


def main() -> None:
    demonstrate_lists()
    demonstrate_tuples()
    demonstrate_dictionaries()
    demonstrate_sets()
    demonstrate_stack_and_queue()
    demonstrate_heap()
    demonstrate_linked_list()
    demonstrate_tree()
    demonstrate_graph()
    demonstrate_frequency_algorithms()
    demonstrate_data_validation()
    demonstrate_copying_and_complexity()
    run_assertions()
    print_heading("All data-structure checks passed")


if __name__ == "__main__":
    main()
