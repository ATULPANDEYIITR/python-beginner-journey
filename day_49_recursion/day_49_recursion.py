from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable
import json
import math
import tempfile


def factorial_recursive(n: int) -> int:
    """Compute n! using the mathematical recursive definition."""
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("factorial requires an integer")
    if n < 0:
        raise ValueError("factorial is undefined for negative integers")
    if n in (0, 1):
        return 1
    return n * factorial_recursive(n - 1)


def factorial_iterative(n: int) -> int:
    """Equivalent iterative implementation for comparison."""
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("factorial requires an integer")
    if n < 0:
        raise ValueError("factorial is undefined for negative integers")

    result = 1
    for value in range(2, n + 1):
        result *= value
    return result


def fibonacci_recursive(n: int) -> int:
    """
    Naive recursive Fibonacci.

    This mirrors F(n) = F(n-1) + F(n-2), but repeats subproblems
    extensively, giving exponential time complexity.
    """
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


def fibonacci_memoized(n: int, cache: dict[int, int] | None = None) -> int:
    """Top-down dynamic programming: recursion plus cached subproblems."""
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")

    if cache is None:
        cache = {0: 0, 1: 1}

    if n not in cache:
        cache[n] = fibonacci_memoized(n - 1, cache) + fibonacci_memoized(n - 2, cache)
    return cache[n]


def fibonacci_tail_style(n: int, a: int = 0, b: int = 1) -> int:
    """
    Tail-position recursive formulation.

    CPython does not perform tail-call optimization, so this remains
    subject to Python's recursion-depth limit.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return a
    return fibonacci_tail_style(n - 1, b, a + b)


def recursive_sum(values: list[int], index: int = 0) -> int:
    """Sum a sequence by recursively consuming one element per call."""
    if index == len(values):
        return 0
    return values[index] + recursive_sum(values, index + 1)


def recursive_max(values: list[int], index: int = 0) -> int:
    """Find a maximum without slicing the list at every recursive call."""
    if not values:
        raise ValueError("cannot find a maximum in an empty list")

    if index == len(values) - 1:
        return values[index]

    remaining_max = recursive_max(values, index + 1)
    return values[index] if values[index] > remaining_max else remaining_max


def reverse_recursive(text: str) -> str:
    """Reverse a string by recursively removing its first character."""
    if len(text) <= 1:
        return text
    return reverse_recursive(text[1:]) + text[0]


def is_palindrome_recursive(text: str) -> bool:
    """Check a normalized string using two recursive boundaries."""
    normalized = "".join(character.casefold() for character in text if character.isalnum())

    def check(left: int, right: int) -> bool:
        if left >= right:
            return True
        if normalized[left] != normalized[right]:
            return False
        return check(left + 1, right - 1)

    return check(0, len(normalized) - 1)


def binary_search_recursive(
    values: list[int],
    target: int,
    low: int = 0,
    high: int | None = None,
) -> int:
    """Binary search using recursive interval reduction."""
    if high is None:
        high = len(values) - 1

    if low > high:
        return -1

    middle = low + (high - low) // 2

    if values[middle] == target:
        return middle
    if target < values[middle]:
        return binary_search_recursive(values, target, low, middle - 1)
    return binary_search_recursive(values, target, middle + 1, high)


def merge_sort_recursive(values: list[int]) -> list[int]:
    """
    Recursive divide-and-conquer sorting.

    The list is divided until single-element lists are reached, then
    sorted halves are merged. The recurrence is T(n)=2T(n/2)+O(n).
    """
    if len(values) <= 1:
        return values.copy()

    middle = len(values) // 2
    left = merge_sort_recursive(values[:middle])
    right = merge_sort_recursive(values[middle:])

    merged: list[int] = []
    left_index = right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return merged


def quick_sort_recursive(values: list[int]) -> list[int]:
    """
    Recursive quicksort using a three-way partition.

    Three-way partitioning handles duplicate values efficiently.
    Worst-case depth can still become O(n), so an adversarial input
    can exhaust Python's recursion limit.
    """
    if len(values) <= 1:
        return values.copy()

    pivot = values[len(values) // 2]
    smaller = [value for value in values if value < pivot]
    equal = [value for value in values if value == pivot]
    larger = [value for value in values if value > pivot]

    return quick_sort_recursive(smaller) + equal + quick_sort_recursive(larger)


@dataclass
class TreeNode:
    value: int
    left: TreeNode | None = None
    right: TreeNode | None = None


def insert_bst(root: TreeNode | None, value: int) -> TreeNode:
    """Recursively insert a value into a binary search tree."""
    if root is None:
        return TreeNode(value)

    if value < root.value:
        root.left = insert_bst(root.left, value)
    elif value > root.value:
        root.right = insert_bst(root.right, value)

    return root


def inorder(root: TreeNode | None) -> list[int]:
    """Visit left subtree, node, then right subtree."""
    if root is None:
        return []
    return inorder(root.left) + [root.value] + inorder(root.right)


def preorder(root: TreeNode | None) -> list[int]:
    """Visit node before its child subtrees."""
    if root is None:
        return []
    return [root.value] + preorder(root.left) + preorder(root.right)


def postorder(root: TreeNode | None) -> list[int]:
    """Visit both child subtrees before visiting the node."""
    if root is None:
        return []
    return postorder(root.left) + postorder(root.right) + [root.value]


def tree_height(root: TreeNode | None) -> int:
    """Return the number of nodes on the longest root-to-leaf path."""
    if root is None:
        return 0
    return 1 + max(tree_height(root.left), tree_height(root.right))


def tree_contains(root: TreeNode | None, target: int) -> bool:
    """Use the BST ordering property to eliminate one subtree per call."""
    if root is None:
        return False
    if root.value == target:
        return True
    if target < root.value:
        return tree_contains(root.left, target)
    return tree_contains(root.right, target)


@dataclass
class FileNode:
    name: str
    is_directory: bool
    children: list[FileNode] = field(default_factory=list)


def calculate_directory_size(node: FileNode) -> int:
    """
    Recursively aggregate sizes in a hierarchical structure.

    Directory nodes have no direct file size here; file names encode
    their example size as a suffix such as report_120.
    """
    if not node.is_directory:
        try:
            return int(node.name.rsplit("_", 1)[1])
        except (IndexError, ValueError) as exc:
            raise ValueError(f"file {node.name!r} has no numeric size suffix") from exc

    return sum(calculate_directory_size(child) for child in node.children)


def walk_tree(node: FileNode, prefix: str = "") -> list[str]:
    """Recursively produce paths for every node in a directory tree."""
    current_path = f"{prefix}/{node.name}" if prefix else node.name
    result = [current_path]

    for child in node.children:
        result.extend(walk_tree(child, current_path))

    return result


def nested_depth(value: object) -> int:
    """Measure nesting depth of dictionaries and lists recursively."""
    if isinstance(value, dict):
        if not value:
            return 1
        return 1 + max(nested_depth(item) for item in value.values())

    if isinstance(value, list):
        if not value:
            return 1
        return 1 + max(nested_depth(item) for item in value)

    return 0


def flatten_nested(value: object) -> list[object]:
    """Flatten arbitrarily nested lists without using explicit loops."""
    if not isinstance(value, list):
        return [value]

    flattened: list[object] = []
    for item in value:
        flattened.extend(flatten_nested(item))
    return flattened


def gcd_recursive(a: int, b: int) -> int:
    """Euclid's algorithm: gcd(a,b)=gcd(b,a mod b)."""
    a, b = abs(a), abs(b)
    if b == 0:
        return a
    return gcd_recursive(b, a % b)


def power_recursive(base: float, exponent: int) -> float:
    """
    Exponentiation by squaring.

    Instead of multiplying base exponent times, halve the exponent
    recursively, reducing the number of multiplications to O(log n).
    """
    if exponent == 0:
        return 1.0
    if exponent < 0:
        if base == 0:
            raise ZeroDivisionError("zero cannot be raised to a negative exponent")
        return 1.0 / power_recursive(base, -exponent)

    half = power_recursive(base, exponent // 2)
    result = half * half

    if exponent % 2:
        result *= base

    return result


def recursive_permutations(items: list[str]) -> list[list[str]]:
    """Generate permutations by recursively choosing each possible first item."""
    if len(items) <= 1:
        return [items.copy()]

    permutations: list[list[str]] = []

    for index, item in enumerate(items):
        remaining = items[:index] + items[index + 1:]
        for suffix in recursive_permutations(remaining):
            permutations.append([item] + suffix)

    return permutations


def recursive_subset_sum(
    values: list[int],
    target: int,
    index: int = 0,
    chosen: tuple[int, ...] = (),
) -> tuple[int, ...] | None:
    """
    Backtracking recursion for finding one subset whose sum equals target.

    Each value creates two branches: include it or exclude it.
    This exponential search is useful for demonstrating recursion trees
    and pruning, but it is not appropriate for large input sets.
    """
    if target == 0:
        return chosen

    if index == len(values):
        return None

    if values[index] <= target:
        included = recursive_subset_sum(
            values,
            target - values[index],
            index + 1,
            chosen + (values[index],),
        )
        if included is not None:
            return included

    return recursive_subset_sum(values, target, index + 1, chosen)


def safe_recursive_depth(depth: int) -> int:
    """Demonstrate controlled recursion while rejecting unreasonable depth."""
    if depth < 0:
        raise ValueError("depth cannot be negative")
    if depth > 1000:
        raise ValueError("requested depth is intentionally limited for safety")
    if depth == 0:
        return 0
    return 1 + safe_recursive_depth(depth - 1)


def serialize_tree(root: TreeNode | None) -> dict | None:
    """Convert a recursive tree structure into JSON-compatible data."""
    if root is None:
        return None
    return {
        "value": root.value,
        "left": serialize_tree(root.left),
        "right": serialize_tree(root.right),
    }


def deserialize_tree(data: dict | None) -> TreeNode | None:
    """Reconstruct a tree recursively from serialized nested dictionaries."""
    if data is None:
        return None
    if not isinstance(data, dict) or "value" not in data:
        raise ValueError("invalid serialized tree node")

    return TreeNode(
        int(data["value"]),
        deserialize_tree(data.get("left")),
        deserialize_tree(data.get("right")),
    )


def recursive_json_size(value: object) -> int:
    """Count JSON-like scalar leaves recursively."""
    if isinstance(value, dict):
        return sum(recursive_json_size(item) for item in value.values())
    if isinstance(value, list):
        return sum(recursive_json_size(item) for item in value)
    return 1


def run_case(name: str, operation: Callable[[], object]) -> None:
    """Execute a demonstration while keeping failures visible and contained."""
    try:
        print(f"{name}: {operation()}")
    except (TypeError, ValueError, ZeroDivisionError, RecursionError) as exc:
        print(f"{name}: {type(exc).__name__}: {exc}")


def main() -> None:
    print("=== Fundamental recursive definitions ===")
    run_case("5!", lambda: factorial_recursive(5))
    run_case("0!", lambda: factorial_recursive(0))
    run_case("factorial(-1)", lambda: factorial_recursive(-1))
    run_case("factorial(6) iterative comparison", lambda: factorial_iterative(6))

    print("\n=== Recursive sequences and memoization ===")
    run_case("F(10) naive recursion", lambda: fibonacci_recursive(10))
    run_case("F(35) memoized recursion", lambda: fibonacci_memoized(35))
    run_case("F(20) tail-style recursion", lambda: fibonacci_tail_style(20))

    print("\n=== Recursive collection processing ===")
    values = [14, 7, 29, 3, 18, 11]
    run_case("recursive sum", lambda: recursive_sum(values))
    run_case("recursive maximum", lambda: recursive_max(values))
    run_case("recursive reverse", lambda: reverse_recursive("recursion"))
    run_case(
        "recursive palindrome",
        lambda: is_palindrome_recursive("A man, a plan, a canal: Panama"),
    )

    print("\n=== Divide-and-conquer algorithms ===")
    ordered = [3, 7, 11, 14, 18, 29]
    run_case("binary search for 18", lambda: binary_search_recursive(ordered, 18))
    run_case("binary search for 20", lambda: binary_search_recursive(ordered, 20))
    run_case("merge sort", lambda: merge_sort_recursive(values))
    run_case("three-way quicksort", lambda: quick_sort_recursive([5, 2, 5, 1, 9, 5, 2]))

    print("\n=== Recursive tree algorithms ===")
    root: TreeNode | None = None
    for value in [50, 30, 70, 20, 40, 60, 80, 65]:
        root = insert_bst(root, value)

    run_case("inorder traversal", lambda: inorder(root))
    run_case("preorder traversal", lambda: preorder(root))
    run_case("postorder traversal", lambda: postorder(root))
    run_case("tree height", lambda: tree_height(root))
    run_case("tree contains 65", lambda: tree_contains(root, 65))
    run_case("tree contains 99", lambda: tree_contains(root, 99))

    print("\n=== Recursive hierarchical data ===")
    file_tree = FileNode(
        "project",
        True,
        [
            FileNode(
                "src",
                True,
                [FileNode("app_1200", False), FileNode("parser_850", False)],
            ),
            FileNode(
                "tests",
                True,
                [FileNode("test_app_600", False), FileNode("test_parser_450", False)],
            ),
            FileNode("README_300", False),
        ],
    )
    run_case("directory size", lambda: calculate_directory_size(file_tree))
    run_case("tree walk", lambda: walk_tree(file_tree))

    print("\n=== Nested structures ===")
    nested = [1, [2, [3, 4]], {"status": ["ok", {"attempts": 3}]}]
    run_case("list flattening", lambda: flatten_nested(nested[:2]))
    run_case("JSON-like depth", lambda: nested_depth(nested))
    run_case("JSON-like scalar count", lambda: recursive_json_size(nested))

    print("\n=== Mathematical recursion ===")
    run_case("gcd(252, 105)", lambda: gcd_recursive(252, 105))
    run_case("3^13 by exponentiation by squaring", lambda: power_recursive(3, 13))
    run_case("2^-4", lambda: power_recursive(2, -4))

    print("\n=== Backtracking recursion ===")
    run_case(
        "permutations of ABC",
        lambda: recursive_permutations(["A", "B", "C"]),
    )
    run_case(
        "subset sum target 15",
        lambda: recursive_subset_sum([4, 7, 9, 11], 15),
    )
    run_case(
        "subset sum impossible target 100",
        lambda: recursive_subset_sum([4, 7, 9, 11], 100),
    )

    print("\n=== Recursive persistence ===")
    serialized = serialize_tree(root)
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "tree.json"
        path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")
        restored = deserialize_tree(json.loads(path.read_text(encoding="utf-8")))
        print(f"serialized tree file: {path.name}")
        print(f"restored inorder traversal: {inorder(restored)}")

    print("\n=== Failure and depth behavior ===")
    run_case("negative recursive depth", lambda: safe_recursive_depth(-1))
    run_case("controlled depth", lambda: safe_recursive_depth(25))

    print("\n=== Complexity observations ===")
    print("Factorial recursion: O(n) time and O(n) call-stack space.")
    print("Naive Fibonacci: exponential time because subproblems are recomputed.")
    print("Memoized Fibonacci: O(n) time and O(n) auxiliary storage.")
    print("Binary search recursion: O(log n) time on sorted data and O(log n) stack depth.")
    print("Merge sort: O(n log n) time with O(n) auxiliary merge storage.")
    print("Balanced BST traversal: O(n) time; search is O(log n) when balanced.")
    print("Backtracking subset search: worst-case O(2^n), illustrating why recursion can be powerful but expensive.")
    print("Python does not perform tail-call optimization, so deep recursion can raise RecursionError.")


if __name__ == "__main__":
    main()
