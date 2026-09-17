"""
for_loops.py

A comprehensive, executable study file for Python `for` loops.

The examples progress from absolute beginner concepts to advanced iteration
patterns, including:
- range()
- strings, lists, tuples, sets, and dictionaries
- enumerate()
- zip()
- nested loops
- comprehensions
- break, continue, and pass
- else clauses
- unpacking
- iterators and iterables
- custom iterators
- generators
- lazy iteration
- recursion comparisons
- algorithmic patterns
- validation and error handling
- edge cases
- performance measurements
- practical applications
- testing
- production-oriented patterns

Run with:
    python for_loops.py
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Iterable, Iterator, Sequence


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    """Print a smaller heading."""
    print(f"\n--- {title} ---")


# ---------------------------------------------------------------------------
# 1. The fundamental for loop
# ---------------------------------------------------------------------------

def basic_for_loop() -> None:
    section("1. Basic for loops")

    # A for loop repeats a block once for every item produced by an iterable.
    # The loop variable receives the current item on each iteration.
    for number in [1, 2, 3, 4, 5]:
        print(number)

    # A string is iterable, so a for loop can process one character at a time.
    for character in "Python":
        print(character)

    # A tuple is also iterable.
    coordinates = (10, 20, 30)
    for coordinate in coordinates:
        print("coordinate:", coordinate)


# ---------------------------------------------------------------------------
# 2. range()
# ---------------------------------------------------------------------------

def range_examples() -> None:
    section("2. range()")

    # range(stop) produces 0 through stop - 1.
    for number in range(5):
        print(number, end=" ")
    print()

    # range(start, stop) begins at start and excludes stop.
    for number in range(2, 7):
        print(number, end=" ")
    print()

    # range(start, stop, step) controls the increment.
    for number in range(0, 11, 2):
        print(number, end=" ")
    print()

    # A negative step iterates backwards.
    for number in range(10, 0, -2):
        print(number, end=" ")
    print()

    # If the direction and step disagree, the range is empty.
    print("range(1, 5, -1):", list(range(1, 5, -1)))

    # range objects are lazy integer sequences rather than materialized lists.
    numbers = range(1_000_000)
    print("range object type:", type(numbers).__name__)
    print("contains 999999:", 999_999 in numbers)


# ---------------------------------------------------------------------------
# 3. Iterating over common collections
# ---------------------------------------------------------------------------

def collection_iteration() -> None:
    section("3. Iterating over common collections")

    subsection("List")
    names = ["Atul", "Maya", "Ravi"]
    for name in names:
        print(name)

    subsection("Tuple")
    dimensions = (1920, 1080)
    for value in dimensions:
        print(value)

    subsection("Set")
    # Set iteration order should not be relied upon as a meaningful ordering.
    technologies = {"Python", "C++", "JavaScript"}
    for technology in technologies:
        print(technology)

    subsection("Dictionary keys")
    profile = {"name": "Atul", "role": "Developer", "experience": 3}
    for key in profile:
        print(key)

    subsection("Dictionary values")
    for value in profile.values():
        print(value)

    subsection("Dictionary key-value pairs")
    for key, value in profile.items():
        print(key, "=>", value)


# ---------------------------------------------------------------------------
# 4. enumerate()
# ---------------------------------------------------------------------------

def enumerate_examples() -> None:
    section("4. enumerate()")

    languages = ["Python", "JavaScript", "C++"]

    # enumerate() produces pairs: (index, item).
    for index, language in enumerate(languages):
        print(index, language)

    # The start parameter changes the initial index.
    for position, language in enumerate(languages, start=1):
        print(f"{position}. {language}")

    # This is preferable to manually maintaining a counter in most cases.
    for index, value in enumerate(["A", "B", "C"]):
        print(f"index={index}, value={value}")


# ---------------------------------------------------------------------------
# 5. zip()
# ---------------------------------------------------------------------------

def zip_examples() -> None:
    section("5. zip()")

    names = ["Alice", "Bob", "Charlie"]
    scores = [91, 84, 96]

    # zip() combines corresponding elements.
    for name, score in zip(names, scores):
        print(name, score)

    # zip() normally stops when the shortest iterable is exhausted.
    print(list(zip([1, 2, 3], ["a", "b"])))

    # Strict zip detects mismatched lengths and raises ValueError.
    try:
        for number, letter in zip([1, 2, 3], ["a", "b"], strict=True):
            print(number, letter)
    except ValueError as error:
        print("strict zip detected mismatch:", error)


# ---------------------------------------------------------------------------
# 6. Nested loops
# ---------------------------------------------------------------------------

def nested_loop_examples() -> None:
    section("6. Nested for loops")

    # A nested loop executes the inner loop for each outer-loop iteration.
    for row in range(3):
        for column in range(4):
            print(f"({row}, {column})", end=" ")
        print()

    subsection("Multiplication table")
    for number in range(1, 6):
        for multiplier in range(1, 6):
            print(f"{number * multiplier:2}", end=" ")
        print()

    subsection("Pattern")
    for row in range(1, 6):
        for _ in range(row):
            print("*", end="")
        print()


# ---------------------------------------------------------------------------
# 7. break
# ---------------------------------------------------------------------------

def break_examples() -> None:
    section("7. break")

    # break terminates the nearest enclosing loop immediately.
    for number in range(1, 11):
        if number == 6:
            break
        print(number)

    # Searching is a common practical use of break.
    target = 42
    numbers = [5, 17, 23, 42, 81]

    found_index = None
    for index, number in enumerate(numbers):
        if number == target:
            found_index = index
            break

    print("target index:", found_index)


# ---------------------------------------------------------------------------
# 8. continue
# ---------------------------------------------------------------------------

def continue_examples() -> None:
    section("8. continue")

    # continue skips the remaining statements in the current iteration.
    for number in range(1, 11):
        if number % 2 == 0:
            continue
        print(number)

    # Filtering data is a common application.
    values = [10, -2, 0, 8, -7, 4]
    positive_values = []

    for value in values:
        if value <= 0:
            continue
        positive_values.append(value)

    print("positive values:", positive_values)


# ---------------------------------------------------------------------------
# 9. pass
# ---------------------------------------------------------------------------

def pass_examples() -> None:
    section("9. pass")

    # pass does nothing. It is syntactically useful when a block must exist.
    for number in range(3):
        if number == 1:
            pass
        print(number)

    # pass is not equivalent to continue:
    # execution continues with the next statement in the current iteration.
    print("pass does not skip the rest of the loop body.")


# ---------------------------------------------------------------------------
# 10. for-else
# ---------------------------------------------------------------------------

def for_else_examples() -> None:
    section("10. for-else")

    # The else clause executes when the loop finishes normally.
    # It does not execute when the loop exits using break.
    target = 7
    numbers = [1, 3, 5, 9]

    for number in numbers:
        if number == target:
            print("found")
            break
    else:
        print("not found")

    subsection("Prime number test")

    def is_prime(candidate: int) -> bool:
        if candidate < 2:
            return False

        for divisor in range(2, int(candidate ** 0.5) + 1):
            if candidate % divisor == 0:
                break
        else:
            return True

        return False

    for candidate in [1, 2, 7, 9, 17, 25]:
        print(candidate, is_prime(candidate))


# ---------------------------------------------------------------------------
# 11. Looping with conditions
# ---------------------------------------------------------------------------

def conditional_iteration() -> None:
    section("11. Conditional processing")

    numbers = range(1, 11)

    for number in numbers:
        if number % 3 == 0:
            print(number, "is divisible by 3")
        elif number % 2 == 0:
            print(number, "is even")
        else:
            print(number, "is odd")


# ---------------------------------------------------------------------------
# 12. Accumulators
# ---------------------------------------------------------------------------

def accumulator_patterns() -> None:
    section("12. Accumulator patterns")

    values = [4, 8, 15, 16, 23, 42]

    total = 0
    for value in values:
        total += value
    print("sum:", total)

    product = 1
    for value in values:
        product *= value
    print("product:", product)

    maximum = values[0]
    for value in values[1:]:
        if value > maximum:
            maximum = value
    print("maximum:", maximum)

    minimum = values[0]
    for value in values[1:]:
        if value < minimum:
            minimum = value
    print("minimum:", minimum)


# ---------------------------------------------------------------------------
# 13. Counting and frequency analysis
# ---------------------------------------------------------------------------

def counting_examples() -> None:
    section("13. Counting and frequency analysis")

    values = [1, 2, 2, 3, 3, 3, 4]

    frequency: dict[int, int] = {}

    for value in values:
        frequency[value] = frequency.get(value, 0) + 1

    print("frequency:", frequency)

    text = "banana"
    character_frequency: dict[str, int] = {}

    for character in text:
        character_frequency[character] = (
            character_frequency.get(character, 0) + 1
        )

    print("character frequency:", character_frequency)


# ---------------------------------------------------------------------------
# 14. Building collections
# ---------------------------------------------------------------------------

def collection_building() -> None:
    section("14. Building collections with loops")

    squares = []
    for number in range(1, 11):
        squares.append(number * number)

    print("squares:", squares)

    even_squares = []
    for number in range(1, 11):
        if number % 2 == 0:
            even_squares.append(number * number)

    print("even squares:", even_squares)


# ---------------------------------------------------------------------------
# 15. Comprehensions
# ---------------------------------------------------------------------------

def comprehension_examples() -> None:
    section("15. Comprehensions")

    # A list comprehension expresses a simple loop-and-build operation.
    squares = [number * number for number in range(10)]
    print(squares)

    even_squares = [
        number * number
        for number in range(10)
        if number % 2 == 0
    ]
    print(even_squares)

    # Dictionary comprehension.
    square_map = {number: number * number for number in range(6)}
    print(square_map)

    # Set comprehension.
    remainders = {number % 3 for number in range(20)}
    print(remainders)

    # Generator expression is lazy.
    lazy_squares = (number * number for number in range(10))
    print("generator type:", type(lazy_squares).__name__)
    print("first three:", [next(lazy_squares) for _ in range(3)])


# ---------------------------------------------------------------------------
# 16. Unpacking inside loops
# ---------------------------------------------------------------------------

def unpacking_examples() -> None:
    section("16. Unpacking")

    points = [(10, 20), (30, 40), (50, 60)]

    for x, y in points:
        print(f"x={x}, y={y}")

    records = [
        ("Alice", 91, "A"),
        ("Bob", 84, "B"),
        ("Charlie", 96, "A+"),
    ]

    for name, score, grade in records:
        print(name, score, grade)

    # Starred unpacking can collect remaining values.
    values = [
        ("Python", "Programming", "Language"),
        ("PostgreSQL", "Database", "SQL"),
    ]

    for first, *remaining in values:
        print(first, remaining)


# ---------------------------------------------------------------------------
# 17. Iterators and iterables
# ---------------------------------------------------------------------------

def iterator_basics() -> None:
    section("17. Iterables and iterators")

    values = [10, 20, 30]

    # A list is iterable. iter() obtains an iterator from it.
    iterator = iter(values)

    print(next(iterator))
    print(next(iterator))
    print(next(iterator))

    try:
        print(next(iterator))
    except StopIteration:
        print("iterator is exhausted")

    # A for loop internally obtains an iterator and repeatedly calls next()
    # until StopIteration occurs.
    for value in values:
        print("for loop value:", value)


# ---------------------------------------------------------------------------
# 18. Custom iterator
# ---------------------------------------------------------------------------

class Countdown:
    """A simple custom iterator that counts down to zero."""

    def __init__(self, start: int):
        if start < 0:
            raise ValueError("start must be non-negative")
        self.current = start

    def __iter__(self) -> "Countdown":
        return self

    def __next__(self) -> int:
        if self.current < 0:
            raise StopIteration

        value = self.current
        self.current -= 1
        return value


def custom_iterator_example() -> None:
    section("18. Custom iterator")

    for number in Countdown(5):
        print(number)


# ---------------------------------------------------------------------------
# 19. Generators
# ---------------------------------------------------------------------------

def fibonacci_generator(limit: int) -> Iterator[int]:
    """Yield Fibonacci numbers without constructing the entire sequence."""
    first, second = 0, 1

    for _ in range(limit):
        yield first
        first, second = second, first + second


def generator_examples() -> None:
    section("19. Generators")

    for number in fibonacci_generator(10):
        print(number, end=" ")
    print()

    # Generators are useful when data is large because values are produced
    # incrementally instead of storing the entire sequence.
    generator = fibonacci_generator(1_000_000)
    print("first value:", next(generator))
    print("second value:", next(generator))


# ---------------------------------------------------------------------------
# 20. Iterating over files without loading everything
# ---------------------------------------------------------------------------

def file_iteration_example() -> None:
    section("20. File iteration")

    sample_text = "first line\nsecond line\nthird line\n"

    # Normally a file can be iterated line by line, which avoids loading a
    # potentially huge file into memory.
    with open("for_loop_sample.txt", "w", encoding="utf-8") as file:
        file.write(sample_text)

    try:
        with open("for_loop_sample.txt", "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                print(line_number, line.rstrip("\n"))
    finally:
        # Clean up the demonstration file.
        import os

        if os.path.exists("for_loop_sample.txt"):
            os.remove("for_loop_sample.txt")


# ---------------------------------------------------------------------------
# 21. Matrix processing
# ---------------------------------------------------------------------------

def matrix_processing() -> None:
    section("21. Matrix processing")

    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]

    total = 0
    for row in matrix:
        for value in row:
            total += value

    print("matrix sum:", total)

    diagonal = []
    for index in range(len(matrix)):
        diagonal.append(matrix[index][index])

    print("main diagonal:", diagonal)


# ---------------------------------------------------------------------------
# 22. Search algorithms
# ---------------------------------------------------------------------------

def linear_search(values: Sequence[int], target: int) -> int | None:
    """Return the first index containing target, or None."""
    for index, value in enumerate(values):
        if value == target:
            return index
    return None


def binary_search(values: Sequence[int], target: int) -> int | None:
    """
    Binary search requires sorted input.

    Complexity:
        Time: O(log n)
        Space: O(1)
    """
    left = 0
    right = len(values) - 1

    while left <= right:
        middle = (left + right) // 2

        if values[middle] == target:
            return middle

        if values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return None


def search_algorithm_examples() -> None:
    section("22. Search algorithms")

    values = [4, 8, 15, 16, 23, 42]

    print("linear search:", linear_search(values, 23))
    print("binary search:", binary_search(values, 23))
    print("missing:", binary_search(values, 99))


# ---------------------------------------------------------------------------
# 23. Sorting implemented with loops
# ---------------------------------------------------------------------------

def bubble_sort(values: list[int]) -> list[int]:
    """
    Demonstrate a classic nested-loop sorting algorithm.

    Bubble sort:
        Best case with early termination: O(n)
        Average/worst case: O(n^2)
        Extra space: O(1), excluding the copied input.
    """
    result = values.copy()

    for outer_index in range(len(result)):
        swapped = False

        for inner_index in range(0, len(result) - outer_index - 1):
            if result[inner_index] > result[inner_index + 1]:
                result[inner_index], result[inner_index + 1] = (
                    result[inner_index + 1],
                    result[inner_index],
                )
                swapped = True

        if not swapped:
            break

    return result


def sorting_example() -> None:
    section("23. Sorting with nested loops")

    values = [64, 34, 25, 12, 22, 11, 90]
    print("original:", values)
    print("sorted:", bubble_sort(values))


# ---------------------------------------------------------------------------
# 24. Input validation
# ---------------------------------------------------------------------------

def parse_positive_integer(text: str) -> int:
    """Convert text into a positive integer with explicit validation."""
    try:
        value = int(text)
    except ValueError as error:
        raise ValueError("input must be an integer") from error

    if value <= 0:
        raise ValueError("input must be positive")

    return value


def validation_example() -> None:
    section("24. Validation and error handling")

    for candidate in ["10", "0", "-3", "abc"]:
        try:
            value = parse_positive_integer(candidate)
            print(candidate, "=>", value)
        except ValueError as error:
            print(candidate, "=> error:", error)


# ---------------------------------------------------------------------------
# 25. Looping with exception handling
# ---------------------------------------------------------------------------

def safe_division_example() -> None:
    section("25. Exception handling inside loops")

    numerator_values = [10, 20, 30]
    denominator_values = [2, 0, 5]

    for numerator, denominator in zip(
        numerator_values,
        denominator_values,
        strict=True,
    ):
        try:
            result = numerator / denominator
        except ZeroDivisionError:
            print(f"{numerator} / {denominator} is invalid")
        else:
            print(f"{numerator} / {denominator} = {result}")


# ---------------------------------------------------------------------------
# 26. Real-world transaction processing
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    amount: float
    status: str


def process_transactions(transactions: Iterable[Transaction]) -> dict[str, float]:
    """Aggregate successful transaction amounts."""
    successful_total = 0.0
    failed_count = 0
    successful_count = 0

    for transaction in transactions:
        if transaction.amount < 0:
            raise ValueError(
                f"negative transaction amount: {transaction.transaction_id}"
            )

        if transaction.status == "success":
            successful_total += transaction.amount
            successful_count += 1
        elif transaction.status == "failed":
            failed_count += 1
        else:
            # Unknown states should be handled deliberately rather than
            # silently treated as successful.
            raise ValueError(
                f"unknown transaction status: {transaction.status}"
            )

    return {
        "successful_total": successful_total,
        "successful_count": float(successful_count),
        "failed_count": float(failed_count),
    }


def transaction_example() -> None:
    section("26. Real-world transaction processing")

    transactions = [
        Transaction("TX001", 1200.00, "success"),
        Transaction("TX002", 500.00, "failed"),
        Transaction("TX003", 850.00, "success"),
    ]

    print(process_transactions(transactions))


# ---------------------------------------------------------------------------
# 27. Batch processing
# ---------------------------------------------------------------------------

def chunked(values: Sequence[Any], chunk_size: int) -> Iterator[list[Any]]:
    """
    Yield a sequence in fixed-size batches.

    This pattern is useful for APIs, database writes, and batch jobs where
    processing everything at once may consume too much memory.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    for start in range(0, len(values), chunk_size):
        yield list(values[start:start + chunk_size])


def batch_processing_example() -> None:
    section("27. Batch processing")

    records = list(range(1, 11))

    for batch in chunked(records, 3):
        print("processing batch:", batch)


# ---------------------------------------------------------------------------
# 28. Nested loops and Cartesian products
# ---------------------------------------------------------------------------

def cartesian_product_example() -> None:
    section("28. Cartesian products")

    colors = ["red", "blue"]
    sizes = ["S", "M", "L"]

    combinations = []

    for color in colors:
        for size in sizes:
            combinations.append((color, size))

    print(combinations)


# ---------------------------------------------------------------------------
# 29. Graph traversal
# ---------------------------------------------------------------------------

def breadth_first_search(
    graph: dict[str, list[str]],
    start: str,
) -> list[str]:
    """
    Breadth-first traversal.

    A for loop processes each neighbor of the current node. The queue
    guarantees that nodes are processed by increasing distance from start.
    """
    if start not in graph:
        raise KeyError(f"unknown start node: {start}")

    queue = [start]
    visited = {start}
    traversal = []
    position = 0

    while position < len(queue):
        current = queue[position]
        position += 1
        traversal.append(current)

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return traversal


def graph_example() -> None:
    section("29. Graph traversal")

    graph = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["E"],
        "D": [],
        "E": [],
    }

    print("BFS:", breadth_first_search(graph, "A"))


# ---------------------------------------------------------------------------
# 30. Dynamic programming example
# ---------------------------------------------------------------------------

def fibonacci_dynamic_programming(n: int) -> int:
    """Compute Fibonacci numbers iteratively in O(n) time and O(1) space."""
    if n < 0:
        raise ValueError("n must be non-negative")

    first, second = 0, 1

    for _ in range(n):
        first, second = second, first + second

    return first


def dynamic_programming_example() -> None:
    section("30. Iterative dynamic programming")

    for n in range(11):
        print(n, fibonacci_dynamic_programming(n))


# ---------------------------------------------------------------------------
# 31. Loop invariants
# ---------------------------------------------------------------------------

def loop_invariant_example(values: Sequence[int]) -> int:
    """
    Find the maximum value.

    Invariant:
    after processing the first k elements, `maximum` is the largest element
    among those k processed elements.
    """
    if not values:
        raise ValueError("values must not be empty")

    maximum = values[0]

    for value in values[1:]:
        if value > maximum:
            maximum = value

    return maximum


# ---------------------------------------------------------------------------
# 32. Avoiding modification during iteration
# ---------------------------------------------------------------------------

def safe_removal_example() -> None:
    section("32. Modifying collections during iteration")

    values = [1, 2, 3, 4, 5, 6]

    # Removing directly from a list while iterating can skip elements because
    # list positions shift. Iterating over a copy avoids that problem.
    for value in values.copy():
        if value % 2 == 0:
            values.remove(value)

    print("after safe removal:", values)

    # An even clearer approach is to build a new collection.
    original = [1, 2, 3, 4, 5, 6]
    filtered = []

    for value in original:
        if value % 2 != 0:
            filtered.append(value)

    print("filtered:", filtered)


# ---------------------------------------------------------------------------
# 33. Common edge cases
# ---------------------------------------------------------------------------

def edge_case_examples() -> None:
    section("33. Edge cases")

    # Empty iterable: the loop body executes zero times.
    for value in []:
        print("never printed", value)

    print("empty loop completed")

    # range with equal start and stop is empty.
    print("range(5, 5):", list(range(5, 5)))

    # Step zero is invalid.
    try:
        list(range(1, 10, 0))
    except ValueError as error:
        print("zero step:", error)

    # A single string is one iterable. It is not automatically treated as
    # one atomic value by a for loop.
    for character in "42":
        print("character:", character)


# ---------------------------------------------------------------------------
# 34. Performance comparison
# ---------------------------------------------------------------------------

def performance_example() -> None:
    section("34. Performance considerations")

    values = list(range(100_000))

    start = perf_counter()
    total_loop = 0

    for value in values:
        total_loop += value

    loop_time = perf_counter() - start

    start = perf_counter()
    total_builtin = sum(values)
    builtin_time = perf_counter() - start

    print("loop result:", total_loop)
    print("sum result:", total_builtin)
    print(f"explicit loop: {loop_time:.6f} seconds")
    print(f"sum():         {builtin_time:.6f} seconds")

    # The point is not that every built-in is always faster. Built-ins often
    # implement operations in optimized C and also communicate intent clearly.
    # Measure real workloads before making performance decisions.


# ---------------------------------------------------------------------------
# 35. Time complexity examples
# ---------------------------------------------------------------------------

def complexity_examples() -> None:
    section("35. Complexity")

    # One loop over n elements is generally O(n).
    values = list(range(10))

    operations = 0
    for _ in values:
        operations += 1

    print("single-loop operations:", operations)

    # Two independent loops are O(n + n), which simplifies to O(n).
    operations = 0
    for _ in values:
        operations += 1

    for _ in values:
        operations += 1

    print("two independent loops:", operations)

    # Nested loops over the same n-sized collection are generally O(n^2).
    operations = 0
    for _ in values:
        for _ in values:
            operations += 1

    print("nested-loop operations:", operations)


# ---------------------------------------------------------------------------
# 36. Reusable iteration functions
# ---------------------------------------------------------------------------

def transform_values(
    values: Iterable[int],
    multiplier: int,
) -> Iterator[int]:
    """Yield transformed values lazily."""
    for value in values:
        yield value * multiplier


def reusable_iteration_example() -> None:
    section("36. Reusable lazy processing")

    source = range(1, 6)
    transformed = transform_values(source, 10)

    for value in transformed:
        print(value)


# ---------------------------------------------------------------------------
# 37. Pipeline processing
# ---------------------------------------------------------------------------

def pipeline_example() -> None:
    section("37. Iterator pipeline")

    raw_values = range(1, 21)

    # Each generator expression processes values lazily. The complete data
    # set does not need to be materialized between every stage.
    positive_values = (value for value in raw_values if value > 0)
    even_values = (value for value in positive_values if value % 2 == 0)
    squared_values = (value * value for value in even_values)

    for value in squared_values:
        print(value)


# ---------------------------------------------------------------------------
# 38. Sentinel-style searching
# ---------------------------------------------------------------------------

def first_matching(
    values: Iterable[Any],
    predicate,
) -> Any | None:
    """Return the first item satisfying predicate."""
    for value in values:
        if predicate(value):
            return value
    return None


def predicate_example() -> None:
    section("38. Predicate-based iteration")

    values = [3, 7, 11, 14, 19]

    result = first_matching(values, lambda value: value % 2 == 0)
    print("first even value:", result)


# ---------------------------------------------------------------------------
# 39. Multi-dimensional traversal
# ---------------------------------------------------------------------------

def transpose(matrix: list[list[Any]]) -> list[list[Any]]:
    """Transpose a rectangular matrix using nested loops."""
    if not matrix:
        return []

    column_count = len(matrix[0])

    if any(len(row) != column_count for row in matrix):
        raise ValueError("matrix must be rectangular")

    result: list[list[Any]] = []

    for column in range(column_count):
        new_row = []

        for row in range(len(matrix)):
            new_row.append(matrix[row][column])

        result.append(new_row)

    return result


def transpose_example() -> None:
    section("39. Matrix transpose")

    matrix = [
        [1, 2, 3],
        [4, 5, 6],
    ]

    print("original:", matrix)
    print("transpose:", transpose(matrix))


# ---------------------------------------------------------------------------
# 40. Production-style record validation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class UserRecord:
    user_id: int
    email: str
    active: bool


def validate_users(records: Iterable[dict[str, Any]]) -> list[UserRecord]:
    """
    Validate external-style records.

    The loop deliberately validates every field rather than trusting input.
    """
    valid_records: list[UserRecord] = []

    for record_number, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise TypeError(f"record {record_number} must be a dictionary")

        user_id = record.get("user_id")
        email = record.get("email")
        active = record.get("active")

        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError(f"record {record_number}: invalid user_id")

        if not isinstance(email, str) or "@" not in email:
            raise ValueError(f"record {record_number}: invalid email")

        if not isinstance(active, bool):
            raise ValueError(f"record {record_number}: invalid active flag")

        valid_records.append(UserRecord(user_id, email, active))

    return valid_records


def validation_pipeline_example() -> None:
    section("40. Production-style validation")

    records = [
        {"user_id": 1, "email": "alice@example.com", "active": True},
        {"user_id": 2, "email": "bob@example.com", "active": False},
    ]

    print(validate_users(records))


# ---------------------------------------------------------------------------
# 41. Testing loop-driven algorithms
# ---------------------------------------------------------------------------

def run_tests() -> None:
    section("41. Basic tests")

    assert linear_search([10, 20, 30], 20) == 1
    assert linear_search([10, 20, 30], 99) is None

    assert binary_search([10, 20, 30], 20) == 1
    assert binary_search([10, 20, 30], 99) is None

    assert bubble_sort([]) == []
    assert bubble_sort([3, 1, 2]) == [1, 2, 3]
    assert bubble_sort([5, 5, 5]) == [5, 5, 5]

    assert fibonacci_dynamic_programming(0) == 0
    assert fibonacci_dynamic_programming(1) == 1
    assert fibonacci_dynamic_programming(10) == 55

    assert transpose([[1, 2], [3, 4]]) == [[1, 3], [2, 4]]

    print("all assertions passed")


# ---------------------------------------------------------------------------
# 42. Practical reporting
# ---------------------------------------------------------------------------

def reporting_example() -> None:
    section("42. Practical reporting")

    sales = [
        {"product": "Laptop", "quantity": 3, "price": 70000},
        {"product": "Monitor", "quantity": 5, "price": 15000},
        {"product": "Keyboard", "quantity": 10, "price": 2500},
    ]

    grand_total = 0

    for sale in sales:
        revenue = sale["quantity"] * sale["price"]
        grand_total += revenue
        print(
            f"{sale['product']}: "
            f"quantity={sale['quantity']}, "
            f"revenue={revenue}"
        )

    print("grand total:", grand_total)


# ---------------------------------------------------------------------------
# 43. Advanced topic: asynchronous for
# ---------------------------------------------------------------------------

async def async_number_stream(limit: int) -> Any:
    """
    Demonstrate the conceptual relationship between `for` and `async for`.

    This function is intentionally implemented as an asynchronous generator.
    """
    import asyncio

    for number in range(limit):
        await asyncio.sleep(0)
        yield number


async def async_iteration_example() -> None:
    section("43. Asynchronous iteration")

    async for number in async_number_stream(5):
        print(number)


# ---------------------------------------------------------------------------
# 44. Main execution
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the complete learning sequence."""

    basic_for_loop()
    range_examples()
    collection_iteration()
    enumerate_examples()
    zip_examples()
    nested_loop_examples()
    break_examples()
    continue_examples()
    pass_examples()
    for_else_examples()
    conditional_iteration()
    accumulator_patterns()
    counting_examples()
    collection_building()
    comprehension_examples()
    unpacking_examples()
    iterator_basics()
    custom_iterator_example()
    generator_examples()
    file_iteration_example()
    matrix_processing()
    search_algorithm_examples()
    sorting_example()
    validation_example()
    safe_division_example()
    transaction_example()
    batch_processing_example()
    cartesian_product_example()
    graph_example()
    dynamic_programming_example()

    section("31. Loop invariant example")
    print(loop_invariant_example([8, 3, 21, 5, 13]))

    safe_removal_example()
    edge_case_examples()
    performance_example()
    complexity_examples()
    reusable_iteration_example()
    pipeline_example()
    predicate_example()
    transpose_example()
    validation_pipeline_example()
    reporting_example()
    run_tests()

    # asyncio.run() is kept separate so the synchronous examples remain easy
    # to understand.
    import asyncio

    asyncio.run(async_iteration_example())


if __name__ == "__main__":
    main()
