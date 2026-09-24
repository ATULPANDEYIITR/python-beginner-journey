"""
Working with Lists
===================

A comprehensive standalone study program covering Python lists from absolute
beginner concepts through advanced techniques, algorithms, performance,
mutability, copying, nested lists, sorting, searching, comprehensions,
iterators, and practical data-processing patterns.

Run:
    python working_with_lists.py
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from functools import reduce
from time import perf_counter
from typing import Any, Iterable, Iterator, Sequence


# ---------------------------------------------------------------------------
# Utility functions used throughout the demonstrations
# ---------------------------------------------------------------------------

def section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def show(label: str, value: Any) -> None:
    print(f"{label}: {value}")


# ---------------------------------------------------------------------------
# 1. What a list is
# ---------------------------------------------------------------------------

def demonstrate_list_fundamentals() -> None:
    section("1. List fundamentals")

    # A list is an ordered, mutable collection.
    empty_list = []
    numbers = [10, 20, 30, 40]
    names = ["Atul", "Riya", "Sam"]
    mixed = [42, "Python", 3.14, True, None]

    show("Empty list", empty_list)
    show("Numbers", numbers)
    show("Names", names)
    show("Mixed values", mixed)

    # Lists preserve insertion order and may contain duplicate values.
    repeated = ["red", "blue", "red", "green", "blue"]
    show("Duplicates are allowed", repeated)

    # Lists can contain lists, producing nested structures.
    nested = [[1, 2], [3, 4], [5, 6]]
    show("Nested list", nested)

    # A list can contain objects of different types, although homogeneous
    # lists are usually easier to reason about in production code.
    show("Type of numbers", type(numbers).__name__)
    show("Length", len(numbers))


# ---------------------------------------------------------------------------
# 2. Indexing
# ---------------------------------------------------------------------------

def demonstrate_indexing() -> None:
    section("2. Indexing")

    values = ["zero", "one", "two", "three", "four"]

    # Python uses zero-based indexing.
    show("First element", values[0])
    show("Second element", values[1])
    show("Last element", values[-1])
    show("Second-last element", values[-2])

    # Accessing an invalid index raises IndexError.
    try:
        print(values[100])
    except IndexError as error:
        show("Invalid index", f"{type(error).__name__}: {error}")

    # A useful defensive pattern is to validate the index before access.
    index = 3
    if 0 <= index < len(values):
        show("Validated access", values[index])


# ---------------------------------------------------------------------------
# 3. Slicing
# ---------------------------------------------------------------------------

def demonstrate_slicing() -> None:
    section("3. Slicing")

    values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    # Syntax: sequence[start:stop:step]
    # The stop position is excluded.
    show("values[2:6]", values[2:6])
    show("values[:4]", values[:4])
    show("values[5:]", values[5:])
    show("values[:]", values[:])
    show("Every second item", values[::2])
    show("Reverse", values[::-1])
    show("Reverse from index 7", values[7:1:-1])

    # Slicing produces a new list for a normal list.
    copied = values[:]
    copied[0] = 999
    show("Original after slice copy", values)
    show("Modified slice copy", copied)


# ---------------------------------------------------------------------------
# 4. Mutability and assignment
# ---------------------------------------------------------------------------

def demonstrate_mutability() -> None:
    section("4. Mutability")

    values = [10, 20, 30]

    # Individual elements can be replaced.
    values[1] = 200
    show("After element replacement", values)

    # A slice can replace multiple elements.
    values[0:2] = [100, 200, 300]
    show("After slice assignment", values)

    # Deleting an element changes the list in place.
    del values[1]
    show("After del", values)

    # clear() removes all elements in place.
    values.clear()
    show("After clear()", values)


# ---------------------------------------------------------------------------
# 5. Adding elements
# ---------------------------------------------------------------------------

def demonstrate_adding_elements() -> None:
    section("5. Adding elements")

    values = [1, 2]

    # append adds exactly one object to the end.
    values.append(3)
    show("After append", values)

    # extend adds each element from an iterable.
    values.extend([4, 5, 6])
    show("After extend", values)

    # insert places an object before the specified position.
    values.insert(0, 0)
    show("After insert", values)

    # A common mistake is confusing append and extend.
    append_example = [1, 2]
    append_example.append([3, 4])

    extend_example = [1, 2]
    extend_example.extend([3, 4])

    show("append([3, 4])", append_example)
    show("extend([3, 4])", extend_example)


# ---------------------------------------------------------------------------
# 6. Removing elements
# ---------------------------------------------------------------------------

def demonstrate_removing_elements() -> None:
    section("6. Removing elements")

    values = ["a", "b", "c", "b", "d"]

    # remove deletes the first matching value.
    values.remove("b")
    show("After remove('b')", values)

    # pop removes and returns an element.
    removed_last = values.pop()
    show("Popped last value", removed_last)
    show("List after pop()", values)

    removed_first = values.pop(0)
    show("Popped first value", removed_first)
    show("List after pop(0)", values)

    # Removing an absent value raises ValueError.
    try:
        values.remove("missing")
    except ValueError as error:
        show("Removing missing value", f"{type(error).__name__}: {error}")

    # del removes by index but does not return the removed item.
    if values:
        del values[0]
    show("After del values[0]", values)


# ---------------------------------------------------------------------------
# 7. Searching and membership
# ---------------------------------------------------------------------------

def demonstrate_searching() -> None:
    section("7. Searching and membership")

    values = [12, 7, 25, 7, 42, 19]

    show("25 in values", 25 in values)
    show("100 in values", 100 in values)
    show("25 not in values", 25 not in values)

    # index returns the first matching position.
    show("Index of 7", values.index(7))

    # count returns the number of occurrences.
    show("Count of 7", values.count(7))

    try:
        values.index(100)
    except ValueError as error:
        show("Searching for absent value", f"{type(error).__name__}: {error}")


# ---------------------------------------------------------------------------
# 8. Iteration
# ---------------------------------------------------------------------------

def demonstrate_iteration() -> None:
    section("8. Iteration")

    names = ["Alice", "Bob", "Charlie"]

    print("Direct iteration:")
    for name in names:
        print(f"  {name}")

    print("Iteration with index:")
    for index, name in enumerate(names):
        print(f"  index={index}, value={name}")

    # Iterating over a snapshot is useful when the original list might change.
    values = [1, 2, 3, 4]
    for value in values[:]:
        if value % 2 == 0:
            values.remove(value)

    show("After safe removal through a slice snapshot", values)

    # Mutating the same list while iterating over it directly can skip values.
    unsafe_example = [1, 2, 3, 4, 5, 6]
    for value in unsafe_example:
        if value % 2 == 0:
            unsafe_example.remove(value)

    show("Potentially surprising direct-mutation result", unsafe_example)


# ---------------------------------------------------------------------------
# 9. List comprehensions
# ---------------------------------------------------------------------------

def demonstrate_comprehensions() -> None:
    section("9. List comprehensions")

    numbers = list(range(1, 11))

    squares = [number * number for number in numbers]
    show("Squares", squares)

    even_squares = [number * number for number in numbers if number % 2 == 0]
    show("Even squares", even_squares)

    labels = [
        "even" if number % 2 == 0 else "odd"
        for number in numbers
    ]
    show("Conditional labels", labels)

    # Nested loops can be expressed in a comprehension.
    coordinates = [
        (x, y)
        for x in range(3)
        for y in range(2)
    ]
    show("Coordinate pairs", coordinates)

    # A comprehension should remain readable. A traditional loop is preferable
    # when a comprehension would contain complicated branching or side effects.


# ---------------------------------------------------------------------------
# 10. Built-in functions
# ---------------------------------------------------------------------------

def demonstrate_builtins() -> None:
    section("10. Useful built-in functions")

    values = [8, 3, 12, 5, 10]

    show("len", len(values))
    show("min", min(values))
    show("max", max(values))
    show("sum", sum(values))
    show("sorted", sorted(values))
    show("reversed converted to list", list(reversed(values)))
    show("any", any(value > 10 for value in values))
    show("all", all(value > 0 for value in values))

    # sorted() returns a new list.
    # list.sort() modifies the existing list.
    original = [3, 1, 2]
    new_list = sorted(original)
    show("original after sorted()", original)
    show("new list", new_list)

    original.sort()
    show("original after sort()", original)


# ---------------------------------------------------------------------------
# 11. Sorting
# ---------------------------------------------------------------------------

def demonstrate_sorting() -> None:
    section("11. Sorting")

    numbers = [40, 10, 30, 20]
    numbers.sort()
    show("Ascending", numbers)

    numbers.sort(reverse=True)
    show("Descending", numbers)

    words = ["pear", "apple", "banana", "fig"]
    words.sort(key=len)
    show("Sorted by length", words)

    people = [
        {"name": "Alice", "age": 31},
        {"name": "Bob", "age": 24},
        {"name": "Charlie", "age": 29},
    ]

    people.sort(key=lambda person: person["age"])
    show("People sorted by age", people)

    # Python's sort is stable: equal-key records retain their relative order.
    records = [
        ("A", 2),
        ("B", 1),
        ("C", 2),
        ("D", 1),
    ]
    records.sort(key=lambda record: record[1])
    show("Stable sort", records)


# ---------------------------------------------------------------------------
# 12. Aliasing versus copying
# ---------------------------------------------------------------------------

def demonstrate_aliasing_and_copying() -> None:
    section("12. Aliasing and copying")

    original = [1, 2, 3]

    # Assignment does not copy the list. Both variables refer to the same object.
    alias = original
    alias.append(4)

    show("Original after alias mutation", original)
    show("Alias", alias)
    show("Same object", original is alias)

    # A shallow copy creates a different outer list.
    shallow_copy = original.copy()
    shallow_copy.append(5)

    show("Original after shallow copy mutation", original)
    show("Shallow copy", shallow_copy)
    show("Different outer object", original is not shallow_copy)

    # For nested lists, a shallow copy still shares inner lists.
    nested = [[1, 2], [3, 4]]
    nested_copy = nested.copy()
    nested_copy[0].append(99)

    show("Nested original after inner mutation", nested)
    show("Nested shallow copy", nested_copy)

    # A recursive deep copy creates independent nested objects.
    from copy import deepcopy

    deep_copy = deepcopy(nested)
    deep_copy[0].append(1000)

    show("Nested original after deep-copy mutation", nested)
    show("Deep copy", deep_copy)


# ---------------------------------------------------------------------------
# 13. Nested lists and matrices
# ---------------------------------------------------------------------------

def demonstrate_nested_lists() -> None:
    section("13. Nested lists")

    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]

    show("Matrix", matrix)
    show("Middle value", matrix[1][1])

    print("Rows:")
    for row in matrix:
        print(" ", row)

    # Correct way to create independent rows.
    correct_matrix = [[0] * 3 for _ in range(3)]
    correct_matrix[0][0] = 99
    show("Independent rows", correct_matrix)

    # A common mistake:
    incorrect_matrix = [[0] * 3] * 3
    incorrect_matrix[0][0] = 99
    show("Shared-row problem", incorrect_matrix)

    # Matrix transpose using zip.
    transposed = [list(column) for column in zip(*matrix)]
    show("Transpose", transposed)


# ---------------------------------------------------------------------------
# 14. Aggregation and transformation
# ---------------------------------------------------------------------------

def demonstrate_transform_filter_reduce() -> None:
    section("14. Transform, filter, and reduce")

    values = [1, 2, 3, 4, 5]

    doubled = list(map(lambda value: value * 2, values))
    show("map", doubled)

    even_values = list(filter(lambda value: value % 2 == 0, values))
    show("filter", even_values)

    total = reduce(lambda left, right: left + right, values, 0)
    show("reduce", total)

    # Generator expressions avoid constructing an intermediate list when only
    # aggregation is required.
    generator_total = sum(value * value for value in values)
    show("Generator expression total", generator_total)


# ---------------------------------------------------------------------------
# 15. Advanced iteration
# ---------------------------------------------------------------------------

def demonstrate_iterators() -> None:
    section("15. Iterators and generators")

    values = ["A", "B", "C"]
    iterator = iter(values)

    print("Manual iterator consumption:")
    while True:
        try:
            print(" ", next(iterator))
        except StopIteration:
            break

    def squares(limit: int) -> Iterator[int]:
        for number in range(limit):
            yield number * number

    show("Generator output", list(squares(6)))

    # Generators calculate values lazily and can represent very large streams
    # without storing all values in a list at once.
    lazy_values = squares(1_000_000)
    show("First lazy value", next(lazy_values))
    show("Second lazy value", next(lazy_values))


# ---------------------------------------------------------------------------
# 16. Stack and queue patterns
# ---------------------------------------------------------------------------

def demonstrate_stack_and_queue() -> None:
    section("16. Lists as stacks and queues")

    # append/pop() are efficient stack operations.
    stack: list[str] = []
    stack.append("task A")
    stack.append("task B")
    stack.append("task C")

    show("Stack", stack)
    show("Popped stack item", stack.pop())
    show("Stack after pop", stack)

    # Removing from index zero of a large list is O(n), because remaining
    # elements have to shift. deque is preferred for FIFO queues.
    queue: deque[str] = deque()
    queue.append("customer 1")
    queue.append("customer 2")
    queue.append("customer 3")

    show("Queue", list(queue))
    show("Dequeued item", queue.popleft())
    show("Queue after popleft", list(queue))


# ---------------------------------------------------------------------------
# 17. Frequency analysis
# ---------------------------------------------------------------------------

def demonstrate_frequency_analysis() -> None:
    section("17. Frequency analysis")

    values = ["apple", "banana", "apple", "orange", "banana", "apple"]

    frequencies = Counter(values)
    show("Frequency table", frequencies)
    show("Most common values", frequencies.most_common())

    # Manual implementation demonstrates the underlying dictionary pattern.
    manual: dict[str, int] = {}
    for value in values:
        manual[value] = manual.get(value, 0) + 1

    show("Manual frequency table", manual)


# ---------------------------------------------------------------------------
# 18. Removing duplicates
# ---------------------------------------------------------------------------

def demonstrate_duplicate_removal() -> None:
    section("18. Removing duplicates")

    values = [4, 2, 4, 1, 2, 3, 1]

    # set() is concise but does not express an ordered-list requirement in
    # older Python versions. dict.fromkeys preserves insertion order.
    unique_ordered = list(dict.fromkeys(values))

    show("Original", values)
    show("Unique while preserving first occurrence", unique_ordered)
    show("Unique values as set", set(values))


# ---------------------------------------------------------------------------
# 19. Flattening nested lists
# ---------------------------------------------------------------------------

def demonstrate_flattening() -> None:
    section("19. Flattening")

    nested = [[1, 2], [3, 4, 5], [], [6]]

    flat = [item for group in nested for item in group]
    show("Flattened list", flat)

    # A recursive implementation handles arbitrarily nested list structures.
    def flatten(value: Any) -> list[Any]:
        result: list[Any] = []

        if isinstance(value, list):
            for item in value:
                result.extend(flatten(item))
        else:
            result.append(value)

        return result

    deeply_nested = [1, [2, [3, 4], []], [5, [6, [7]]]]
    show("Deep flatten", flatten(deeply_nested))


# ---------------------------------------------------------------------------
# 20. Partitioning
# ---------------------------------------------------------------------------

def demonstrate_partitioning() -> None:
    section("20. Partitioning")

    values = [1, 8, 3, 12, 5, 20, 7]

    below_ten = [value for value in values if value < 10]
    ten_or_more = [value for value in values if value >= 10]

    show("Below ten", below_ten)
    show("Ten or more", ten_or_more)

    # A single pass can partition the values while preserving order.
    small: list[int] = []
    large: list[int] = []

    for value in values:
        (small if value < 10 else large).append(value)

    show("Single-pass small partition", small)
    show("Single-pass large partition", large)


# ---------------------------------------------------------------------------
# 21. Binary search
# ---------------------------------------------------------------------------

def binary_search(values: Sequence[int], target: int) -> int:
    """
    Return the target index in a sorted sequence, or -1 if absent.

    Binary search requires sorted input and runs in O(log n) time.
    """
    left = 0
    right = len(values) - 1

    while left <= right:
        middle = left + (right - left) // 2

        if values[middle] == target:
            return middle
        if values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


def demonstrate_binary_search() -> None:
    section("21. Binary search")

    sorted_values = [3, 7, 12, 18, 24, 31, 42]

    show("Search for 18", binary_search(sorted_values, 18))
    show("Search for 100", binary_search(sorted_values, 100))

    # bisect provides production-ready binary-search helpers.
    import bisect

    position = bisect.bisect_left(sorted_values, 24)
    show("bisect_left position for 24", position)

    insertion_position = bisect.bisect_left(sorted_values, 20)
    show("Insertion position for 20", insertion_position)


# ---------------------------------------------------------------------------
# 22. Two-pointer technique
# ---------------------------------------------------------------------------

def find_pair_with_sum(sorted_values: Sequence[int], target: int) -> tuple[int, int] | None:
    """Find one pair whose values add to target using two pointers."""
    left = 0
    right = len(sorted_values) - 1

    while left < right:
        current = sorted_values[left] + sorted_values[right]

        if current == target:
            return sorted_values[left], sorted_values[right]
        if current < target:
            left += 1
        else:
            right -= 1

    return None


def demonstrate_two_pointer_algorithm() -> None:
    section("22. Two-pointer list algorithm")

    values = [1, 3, 4, 6, 8, 11, 15]
    show("Pair summing to 14", find_pair_with_sum(values, 14))
    show("Pair summing to 100", find_pair_with_sum(values, 100))


# ---------------------------------------------------------------------------
# 23. List-based insertion and deletion complexity
# ---------------------------------------------------------------------------

def demonstrate_complexity() -> None:
    section("23. Complexity considerations")

    operations = {
        "Index access": "O(1) average",
        "Append at end": "O(1) amortized",
        "Pop at end": "O(1)",
        "Search with in": "O(n)",
        "index(value)": "O(n)",
        "remove(value)": "O(n)",
        "Insert at front": "O(n)",
        "Delete from front": "O(n)",
        "Sorting": "O(n log n) worst-case",
        "Copying a list": "O(n)",
    }

    for operation, complexity in operations.items():
        print(f"{operation:28} {complexity}")

    print(
        "\nThe exact cost can depend on input characteristics and the operation's "
        "implementation details. Python lists are dynamic arrays rather than "
        "linked lists."
    )


# ---------------------------------------------------------------------------
# 24. Custom records and sorting
# ---------------------------------------------------------------------------

@dataclass
class Student:
    name: str
    score: float
    attendance: float


def demonstrate_custom_objects() -> None:
    section("24. Lists of custom objects")

    students = [
        Student("Alice", 91.5, 96.0),
        Student("Bob", 84.0, 91.0),
        Student("Charlie", 91.5, 88.0),
    ]

    for student in students:
        print(student)

    # Multiple sorting criteria can be expressed using tuple keys.
    students.sort(key=lambda student: (-student.score, -student.attendance))

    show("Sorted students", students)


# ---------------------------------------------------------------------------
# 25. Validation and defensive list processing
# ---------------------------------------------------------------------------

def average_positive_numbers(values: Iterable[Any]) -> float:
    """
    Calculate an average after validating that every supplied value is numeric.

    bool is rejected deliberately because bool is a subclass of int in Python
    but usually does not represent a measurement.
    """
    validated: list[float] = []

    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"Expected numeric value, received {value!r}")

        if value <= 0:
            raise ValueError(f"Expected positive value, received {value!r}")

        validated.append(float(value))

    if not validated:
        raise ValueError("At least one positive number is required")

    return sum(validated) / len(validated)


def demonstrate_validation() -> None:
    section("25. Validation and error handling")

    valid_values = [10, 20, 30]
    show("Average", average_positive_numbers(valid_values))

    invalid_examples = [
        [],
        [10, -5, 20],
        [10, "twenty", 30],
    ]

    for example in invalid_examples:
        try:
            average_positive_numbers(example)
        except (TypeError, ValueError) as error:
            print(f"Input {example!r} -> {type(error).__name__}: {error}")


# ---------------------------------------------------------------------------
# 26. Functional patterns without unnecessary complexity
# ---------------------------------------------------------------------------

def demonstrate_practical_pipeline() -> None:
    section("26. Practical data-processing pipeline")

    raw_scores = [
        "82",
        "91",
        "invalid",
        "76",
        "",
        "88",
        "105",
        "-4",
    ]

    valid_scores: list[int] = []

    for raw_score in raw_scores:
        try:
            score = int(raw_score)
        except ValueError:
            continue

        if 0 <= score <= 100:
            valid_scores.append(score)

    normalized = [score / 100 for score in valid_scores]
    average = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

    show("Valid scores", valid_scores)
    show("Normalized scores", normalized)
    show("Average valid score", average)


# ---------------------------------------------------------------------------
# 27. List equality, identity, and membership
# ---------------------------------------------------------------------------

def demonstrate_equality_identity() -> None:
    section("27. Equality versus identity")

    first = [1, 2, 3]
    second = [1, 2, 3]
    third = first

    show("first == second", first == second)
    show("first is second", first is second)
    show("first is third", first is third)

    # Equality compares values. Identity asks whether two references point to
    # the exact same object.
    print("Value equality and object identity are different concepts.")


# ---------------------------------------------------------------------------
# 28. Packing and unpacking
# ---------------------------------------------------------------------------

def demonstrate_unpacking() -> None:
    section("28. Packing and unpacking")

    values = [10, 20, 30]

    first, second, third = values
    show("first", first)
    show("second", second)
    show("third", third)

    # Starred unpacking captures an arbitrary number of middle elements.
    first, *middle, last = [1, 2, 3, 4, 5]
    show("First", first)
    show("Middle", middle)
    show("Last", last)

    # Function calls can unpack list values into positional arguments.
    def add_three(a: int, b: int, c: int) -> int:
        return a + b + c

    show("Unpacked function arguments", add_three(*values))


# ---------------------------------------------------------------------------
# 29. Nested comprehensions and matrix operations
# ---------------------------------------------------------------------------

def demonstrate_matrix_operations() -> None:
    section("29. Matrix operations")

    matrix = [
        [1, 2, 3],
        [4, 5, 6],
    ]

    doubled = [
        [value * 2 for value in row]
        for row in matrix
    ]

    row_sums = [sum(row) for row in matrix]
    column_sums = [
        sum(matrix[row][column] for row in range(len(matrix)))
        for column in range(len(matrix[0]))
    ]

    show("Doubled matrix", doubled)
    show("Row sums", row_sums)
    show("Column sums", column_sums)


# ---------------------------------------------------------------------------
# 30. Sorting with rich keys
# ---------------------------------------------------------------------------

def demonstrate_advanced_sorting() -> None:
    section("30. Advanced sorting")

    products = [
        {"name": "Laptop", "price": 900, "rating": 4.5},
        {"name": "Phone", "price": 700, "rating": 4.7},
        {"name": "Tablet", "price": 500, "rating": 4.7},
        {"name": "Monitor", "price": 300, "rating": 4.2},
    ]

    # Sort by rating descending, then price ascending.
    products.sort(key=lambda product: (-product["rating"], product["price"]))

    for product in products:
        print(product)


# ---------------------------------------------------------------------------
# 31. Performance measurement
# ---------------------------------------------------------------------------

def demonstrate_performance() -> None:
    section("31. Basic performance measurement")

    size = 200_000

    start = perf_counter()
    values = []
    for number in range(size):
        values.append(number)
    append_time = perf_counter() - start

    start = perf_counter()
    squares = [number * number for number in range(size)]
    comprehension_time = perf_counter() - start

    show("Append loop seconds", round(append_time, 6))
    show("Comprehension seconds", round(comprehension_time, 6))
    show("Generated sizes", (len(values), len(squares)))

    print(
        "Timing varies by Python version, hardware, operating system, and "
        "background activity. Microbenchmarks should be interpreted carefully."
    )


# ---------------------------------------------------------------------------
# 32. Memory and references
# ---------------------------------------------------------------------------

def demonstrate_references() -> None:
    section("32. References and object behavior")

    values = [1, 2, 3]
    references = [values, values]

    references[0].append(4)

    show("Shared object through two references", references)
    show("references[0] is references[1]", references[0] is references[1])

    independent = [values.copy(), values.copy()]
    independent[0].append(5)

    show("Independent outer lists", independent)


# ---------------------------------------------------------------------------
# 33. Common mistakes
# ---------------------------------------------------------------------------

def demonstrate_common_mistakes() -> None:
    section("33. Common mistakes")

    # Mistake 1: assigning a reference when a copy was intended.
    original = [1, 2, 3]
    wrong_copy = original
    wrong_copy.append(4)
    show("Reference assignment affects original", original)

    # Mistake 2: using remove when an index is intended.
    values = ["a", "b", "c"]
    del values[1]
    show("Delete by index", values)

    # Mistake 3: assuming sort() returns the sorted list.
    values = [3, 1, 2]
    result = values.sort()
    show("sort() return value", result)
    show("List itself after sort()", values)

    # Mistake 4: using a list for frequent front removals.
    print(
        "For frequent FIFO operations, collections.deque is normally more "
        "appropriate than repeatedly calling list.pop(0)."
    )


# ---------------------------------------------------------------------------
# 34. Practical inventory system
# ---------------------------------------------------------------------------

@dataclass
class InventoryItem:
    sku: str
    name: str
    quantity: int
    price: float


def inventory_total(items: Sequence[InventoryItem]) -> float:
    return sum(item.quantity * item.price for item in items)


def find_inventory_item(
    items: Sequence[InventoryItem],
    sku: str,
) -> InventoryItem | None:
    for item in items:
        if item.sku == sku:
            return item
    return None


def demonstrate_inventory_case_study() -> None:
    section("34. Practical inventory case study")

    inventory = [
        InventoryItem("LAP-001", "Laptop", 8, 75000.0),
        InventoryItem("PHN-002", "Phone", 15, 42000.0),
        InventoryItem("MON-003", "Monitor", 12, 18000.0),
    ]

    show("Inventory value", inventory_total(inventory))

    requested_sku = "PHN-002"
    item = find_inventory_item(inventory, requested_sku)

    if item is not None:
        show("Found item", item)
    else:
        show("Missing SKU", requested_sku)

    # Apply a stock adjustment safely.
    adjustment = -3
    if item is not None:
        if item.quantity + adjustment < 0:
            print("Stock adjustment rejected: quantity cannot become negative.")
        else:
            item.quantity += adjustment

    show("Inventory after adjustment", inventory)

    # Sort a copied view rather than changing the operational order.
    expensive_first = sorted(
        inventory,
        key=lambda inventory_item: inventory_item.price,
        reverse=True,
    )
    show("Expensive-first view", expensive_first)


# ---------------------------------------------------------------------------
# 35. Testing list-related functions
# ---------------------------------------------------------------------------

def demonstrate_testing() -> None:
    section("35. Lightweight testing")

    def unique_preserving_order(values: Iterable[Any]) -> list[Any]:
        seen: set[Any] = set()
        result: list[Any] = []

        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)

        return result

    test_cases = [
        ([], []),
        ([1], [1]),
        ([1, 2, 1, 3], [1, 2, 3]),
        (["a", "a", "b"], ["a", "b"]),
    ]

    for input_values, expected in test_cases:
        actual = unique_preserving_order(input_values)
        assert actual == expected, (
            f"Expected {expected!r}, received {actual!r}"
        )

    print(f"Passed {len(test_cases)} list-processing tests.")


# ---------------------------------------------------------------------------
# 36. Advanced list algorithm: merge two sorted lists
# ---------------------------------------------------------------------------

def merge_sorted_lists(
    left: Sequence[int],
    right: Sequence[int],
) -> list[int]:
    """
    Merge two already-sorted sequences in O(n + m) time.
    """
    result: list[int] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1

    result.extend(left[left_index:])
    result.extend(right[right_index:])

    return result


def demonstrate_merge() -> None:
    section("36. Merging sorted lists")

    left = [1, 4, 7, 10]
    right = [2, 3, 8, 11]

    show("Left", left)
    show("Right", right)
    show("Merged", merge_sorted_lists(left, right))


# ---------------------------------------------------------------------------
# 37. Advanced algorithm: rotate a list
# ---------------------------------------------------------------------------

def rotate_list(values: Sequence[Any], positions: int) -> list[Any]:
    """
    Rotate a sequence to the right.

    Modulo handles rotations larger than the list length.
    """
    if not values:
        return []

    positions %= len(values)

    if positions == 0:
        return list(values)

    return list(values[-positions:]) + list(values[:-positions])


def demonstrate_rotation() -> None:
    section("37. List rotation")

    values = [1, 2, 3, 4, 5]

    show("Rotate right by 2", rotate_list(values, 2))
    show("Rotate right by 7", rotate_list(values, 7))
    show("Rotate empty list", rotate_list([], 4))


# ---------------------------------------------------------------------------
# 38. Advanced algorithm: chunking
# ---------------------------------------------------------------------------

def chunked(values: Sequence[Any], chunk_size: int) -> list[list[Any]]:
    """Split a sequence into chunks of a requested positive size."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    return [
        list(values[index:index + chunk_size])
        for index in range(0, len(values), chunk_size)
    ]


def demonstrate_chunking() -> None:
    section("38. Chunking")

    values = list(range(1, 11))

    show("Chunks of three", chunked(values, 3))

    try:
        chunked(values, 0)
    except ValueError as error:
        show("Invalid chunk size", f"{type(error).__name__}: {error}")


# ---------------------------------------------------------------------------
# 39. Main demonstration runner
# ---------------------------------------------------------------------------

def main() -> None:
    demonstrate_list_fundamentals()
    demonstrate_indexing()
    demonstrate_slicing()
    demonstrate_mutability()
    demonstrate_adding_elements()
    demonstrate_removing_elements()
    demonstrate_searching()
    demonstrate_iteration()
    demonstrate_comprehensions()
    demonstrate_builtins()
    demonstrate_sorting()
    demonstrate_aliasing_and_copying()
    demonstrate_nested_lists()
    demonstrate_transform_filter_reduce()
    demonstrate_iterators()
    demonstrate_stack_and_queue()
    demonstrate_frequency_analysis()
    demonstrate_duplicate_removal()
    demonstrate_flattening()
    demonstrate_partitioning()
    demonstrate_binary_search()
    demonstrate_two_pointer_algorithm()
    demonstrate_complexity()
    demonstrate_custom_objects()
    demonstrate_validation()
    demonstrate_practical_pipeline()
    demonstrate_equality_identity()
    demonstrate_unpacking()
    demonstrate_matrix_operations()
    demonstrate_advanced_sorting()
    demonstrate_performance()
    demonstrate_references()
    demonstrate_common_mistakes()
    demonstrate_inventory_case_study()
    demonstrate_testing()
    demonstrate_merge()
    demonstrate_rotation()
    demonstrate_chunking()

    section("Study program completed")
    print("All list demonstrations completed successfully.")


if __name__ == "__main__":
    main()
