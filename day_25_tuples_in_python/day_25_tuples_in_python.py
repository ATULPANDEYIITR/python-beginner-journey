"""
TUPLES IN PYTHON
================

A comprehensive executable study of Python tuples, from fundamentals to
advanced usage.

Run:
    python tuples_complete.py

The examples are intentionally self-contained and use only the Python
standard library.
"""

from __future__ import annotations

from collections import namedtuple
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, NamedTuple, Optional
import sys
import timeit


# ============================================================================
# 1. FUNDAMENTALS
# ============================================================================

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    print(f"\n--- {title} ---")


def fundamentals() -> None:
    section("1. Tuple Fundamentals")

    # A tuple is an ordered collection of references to Python objects.
    # Parentheses are commonly used to display tuples, but commas are what
    # actually establish tuple packing.
    empty_tuple = ()
    coordinates = (10, 20)
    mixed_tuple = ("Atul", 30, 88.5, True)
    print("Empty tuple:", empty_tuple)
    print("Coordinates:", coordinates)
    print("Mixed tuple:", mixed_tuple)

    # Parentheses are optional in many tuple literals.
    packed = 1, 2, 3
    print("Packed tuple:", packed)
    print("Type:", type(packed).__name__)

    # A one-element tuple requires a trailing comma.
    not_a_tuple = (42)
    one_element_tuple = (42,)
    print("(42):", type(not_a_tuple).__name__)
    print("(42,):", type(one_element_tuple).__name__)

    # tuple() constructs a tuple from an iterable.
    from_list = tuple([1, 2, 3])
    from_string = tuple("ABC")
    from_range = tuple(range(4))
    print("From list:", from_list)
    print("From string:", from_string)
    print("From range:", from_range)

    # Strings are iterable, so tuple(string) creates one element per character.
    print("Tuple of 'Python':", tuple("Python"))

    # A tuple can contain another tuple.
    nested = ("user", (28, 80), ("Python", "SQL"))
    print("Nested tuple:", nested)


# ============================================================================
# 2. INDEXING AND SLICING
# ============================================================================

def indexing_and_slicing() -> None:
    section("2. Indexing and Slicing")

    values = ("zero", "one", "two", "three", "four", "five")

    print("Tuple:", values)
    print("First:", values[0])
    print("Second:", values[1])
    print("Last:", values[-1])
    print("Second-last:", values[-2])

    print("Slice [1:4]:", values[1:4])
    print("Slice [:3]:", values[:3])
    print("Slice [3:]:", values[3:])
    print("Every second item:", values[::2])
    print("Reversed:", values[::-1])

    # Out-of-range indexing raises IndexError.
    try:
        print(values[100])
    except IndexError as error:
        print("Handled invalid index:", error)

    # Slicing beyond the boundaries is safe.
    print("Oversized slice:", values[100:200])

    # Nested indexing.
    matrix = ((1, 2), (3, 4), (5, 6))
    print("matrix[1]:", matrix[1])
    print("matrix[1][0]:", matrix[1][0])


# ============================================================================
# 3. IMMUTABILITY
# ============================================================================

def immutability() -> None:
    section("3. Tuple Immutability")

    data = ("Python", 3, 2026)
    print("Original:", data)

    try:
        data[0] = "JavaScript"
    except TypeError as error:
        print("Direct modification rejected:", error)

    # Immutability applies to the tuple's references. It does not make every
    # object stored inside the tuple immutable.
    mutable_inside = ("configuration", {"debug": False})
    mutable_inside[1]["debug"] = True
    print("Tuple containing mutable object:", mutable_inside)

    # The tuple itself still cannot replace the dictionary reference.
    try:
        mutable_inside[1] = {}
    except TypeError as error:
        print("Reference replacement rejected:", error)

    # This distinction is important:
    # immutable container != recursively immutable object graph.

    immutable_nested = ("A", (1, 2), frozenset({3, 4}))
    print("Deeply immutable-style structure:", immutable_nested)


# ============================================================================
# 4. PACKING AND UNPACKING
# ============================================================================

def packing_and_unpacking() -> None:
    section("4. Packing and Unpacking")

    # Packing.
    person = ("Atul", 30, "India")
    print("Packed:", person)

    # Basic unpacking requires the number of targets to match.
    name, age, country = person
    print(name, age, country)

    try:
        a, b = person
    except ValueError as error:
        print("Wrong unpacking count:", error)

    # Starred unpacking collects zero or more remaining values into a list.
    first, *middle, last = (10, 20, 30, 40, 50)
    print("first:", first)
    print("middle:", middle)
    print("last:", last)

    first, *rest = (10,)
    print("Single-item starred unpack:", first, rest)

    # Starred targets cannot be used more than once in one assignment.
    try:
        compile("a, *b, *c = (1, 2, 3)", "<example>", "exec")
    except SyntaxError as error:
        print("Multiple starred targets rejected:", error.msg)

    # Nested unpacking.
    employee = ("E101", ("Atul", "Pandey"), ("Engineering", "Python"))
    employee_id, (first_name, last_name), (department, skill) = employee
    print(employee_id, first_name, last_name, department, skill)

    # Swap variables without a temporary variable.
    left, right = 10, 20
    left, right = right, left
    print("Swapped:", left, right)


# ============================================================================
# 5. TUPLE OPERATORS
# ============================================================================

def tuple_operations() -> None:
    section("5. Tuple Operators and Operations")

    first = (1, 2, 3)
    second = (4, 5)

    print("Concatenation:", first + second)
    print("Repetition:", ("A", "B") * 3)

    values = (10, 20, 30, 20)
    print("Contains 20:", 20 in values)
    print("Contains 99:", 99 in values)

    print("Length:", len(values))
    print("Minimum:", min(values))
    print("Maximum:", max(values))
    print("Sum:", sum(values))

    # Equality is element-by-element and order-sensitive.
    print("(1, 2) == (1, 2):", (1, 2) == (1, 2))
    print("(1, 2) == (2, 1):", (1, 2) == (2, 1))

    # Lexicographical comparison.
    print("(1, 2) < (1, 3):", (1, 2) < (1, 3))
    print("(2,) > (1, 1000):", (2,) > (1, 1000))

    # Comparisons require compatible element ordering.
    try:
        print((1, "two") < (2, "three"))
    except TypeError as error:
        print("Incompatible comparison:", error)


# ============================================================================
# 6. TUPLE METHODS
# ============================================================================

def tuple_methods() -> None:
    section("6. Tuple Methods")

    values = ("Python", "SQL", "Python", "C++", "Python")

    print("count('Python'):", values.count("Python"))
    print("index('C++'):", values.index("C++"))

    try:
        values.index("Rust")
    except ValueError as error:
        print("Missing index handled:", error)

    # Tuple has only two public data-oriented methods:
    # count() and index().
    print("Tuple methods demonstrated: count(), index()")


# ============================================================================
# 7. ITERATION
# ============================================================================

def iteration() -> None:
    section("7. Iterating Over Tuples")

    languages = ("Python", "JavaScript", "C++")

    for language in languages:
        print("Language:", language)

    for position, language in enumerate(languages, start=1):
        print(position, language)

    # Multiple sequences can be traversed together with zip().
    versions = (3.13, 2026, 17)
    for language, version in zip(languages, versions):
        print(f"{language}: {version}")

    # Tuple iteration works with any iterable-consuming mechanism.
    iterator = iter(languages)
    while True:
        try:
            print("next():", next(iterator))
        except StopIteration:
            break


# ============================================================================
# 8. TUPLES AND FUNCTIONS
# ============================================================================

def calculate_statistics(numbers: Iterable[float]) -> tuple[float, float, float]:
    """Return minimum, maximum, and arithmetic mean."""
    values = tuple(numbers)
    if not values:
        raise ValueError("At least one number is required")
    return min(values), max(values), sum(values) / len(values)


def function_usage() -> None:
    section("8. Tuples with Functions")

    result = calculate_statistics([10, 20, 30, 40])
    print("Returned tuple:", result)

    minimum, maximum, average = result
    print("Minimum:", minimum)
    print("Maximum:", maximum)
    print("Average:", average)

    # Returning multiple values in Python is implemented through tuple packing.
    def divide_with_remainder(dividend: int, divisor: int) -> tuple[int, int]:
        if divisor == 0:
            raise ZeroDivisionError("divisor cannot be zero")
        return dividend // divisor, dividend % divisor

    quotient, remainder = divide_with_remainder(17, 5)
    print("Quotient:", quotient)
    print("Remainder:", remainder)


# ============================================================================
# 9. TUPLES AS DICTIONARY KEYS
# ============================================================================

def dictionary_keys() -> None:
    section("9. Tuples as Dictionary Keys")

    # Hashable tuples can be used as dictionary keys.
    population = {
        ("India", "Lucknow"): 3_500_000,
        ("India", "Delhi"): 32_000_000,
    }

    print("Lucknow:", population[("India", "Lucknow")])

    # A tuple is hashable only when all of its elements are hashable.
    valid_key = (1, "Python", frozenset({"A", "B"}))
    print("Hashable tuple:", hash(valid_key))

    try:
        hash((1, []))
    except TypeError as error:
        print("Unhashable tuple:", error)

    try:
        invalid_dictionary = {(1, []): "value"}
        print(invalid_dictionary)
    except TypeError as error:
        print("Cannot use tuple containing list as key:", error)


# ============================================================================
# 10. TUPLES AND SETS
# ============================================================================

def sets_and_tuples() -> None:
    section("10. Tuples and Sets")

    coordinates = {(0, 0), (1, 2), (0, 0), (3, 4)}
    print("Unique coordinate tuples:", coordinates)

    # Set elements must be hashable.
    try:
        bad_set = {[1, 2]}
        print(bad_set)
    except TypeError as error:
        print("Lists cannot be set elements:", error)

    # Converting lists to tuples can make structured data hashable.
    matrix_rows = [[1, 2], [3, 4], [1, 2]]
    unique_rows = {tuple(row) for row in matrix_rows}
    print("Unique rows:", unique_rows)


# ============================================================================
# 11. SORTING TUPLES
# ============================================================================

def sorting_tuples() -> None:
    section("11. Sorting Tuples")

    records = (
        ("Atul", 88),
        ("Riya", 95),
        ("Aman", 88),
        ("Zoya", 72),
    )

    print("Sorted naturally:", sorted(records))
    print("Sorted by score:", sorted(records, key=lambda record: record[1]))
    print(
        "Sorted by score descending:",
        sorted(records, key=lambda record: record[1], reverse=True),
    )

    # Multiple-key sorting.
    print(
        "Score descending, name ascending:",
        sorted(records, key=lambda record: (-record[1], record[0])),
    )


# ============================================================================
# 12. NESTED TUPLES AND STRUCTURED DATA
# ============================================================================

def nested_data() -> None:
    section("12. Nested Tuples")

    company = (
        ("Engineering", ("Python", "C++", "JavaScript")),
        ("Analytics", ("SQL", "Statistics")),
        ("Security", ("Cryptography", "Networking")),
    )

    for department, skills in company:
        print(department, "->", ", ".join(skills))

    # Nested tuples are useful when the structure is fixed and compact.
    graph_edges = (
        ("A", "B", 4),
        ("A", "C", 2),
        ("B", "D", 7),
    )

    for source, destination, weight in graph_edges:
        print(f"{source} -> {destination}, weight={weight}")


# ============================================================================
# 13. TUPLES VS LISTS
# ============================================================================

def tuples_vs_lists() -> None:
    section("13. Tuples Versus Lists")

    values_as_tuple = (1, 2, 3)
    values_as_list = [1, 2, 3]

    values_as_list.append(4)

    print("Tuple:", values_as_tuple)
    print("List after append:", values_as_list)

    print(
        "Tuple memory size:",
        sys.getsizeof(values_as_tuple),
        "bytes",
    )
    print(
        "List memory size:",
        sys.getsizeof(values_as_list),
        "bytes",
    )

    # Neither container is universally "better".
    # Tuples communicate fixed structure and prevent direct item reassignment.
    # Lists communicate mutable collections.
    print("Tuple supports append:", hasattr(values_as_tuple, "append"))
    print("List supports append:", hasattr(values_as_list, "append"))


# ============================================================================
# 14. PERFORMANCE
# ============================================================================

def performance() -> None:
    section("14. Performance Considerations")

    tuple_literal = "(1, 2, 3, 4, 5)"
    list_literal = "[1, 2, 3, 4, 5]"

    tuple_time = timeit.timeit(
        tuple_literal,
        number=500_000,
    )
    list_time = timeit.timeit(
        list_literal,
        number=500_000,
    )

    print(f"Creating tuple: {tuple_time:.6f} seconds")
    print(f"Creating list:  {list_time:.6f} seconds")

    # These measurements depend on Python version and hardware. They are
    # demonstrations, not universal benchmarks.
    print("Benchmark results are environment-dependent.")


# ============================================================================
# 15. NAMED TUPLES
# ============================================================================

class Student(NamedTuple):
    """Typed, immutable record represented as a tuple."""

    name: str
    age: int
    score: float


def named_tuple_examples() -> None:
    section("15. Named Tuples")

    student = Student("Atul", 30, 91.5)

    print("Student:", student)
    print("By index:", student[0])
    print("By name:", student.name)
    print("Fields:", Student._fields)

    # NamedTuple instances remain tuple subclasses.
    print("Is tuple:", isinstance(student, tuple))

    # collections.namedtuple is another standard-library option.
    Point = namedtuple("Point", ["x", "y"])
    point = Point(10, 20)

    print("Point:", point)
    print("point.x:", point.x)
    print("point.y:", point.y)


# ============================================================================
# 16. DATACLASSES VS TUPLES
# ============================================================================

@dataclass(frozen=True)
class ImmutableUser:
    """Immutable record using a dataclass rather than a tuple."""

    name: str
    age: int


def dataclass_comparison() -> None:
    section("16. Tuple Records Versus Dataclasses")

    tuple_user = ("Atul", 30)
    dataclass_user = ImmutableUser("Atul", 30)

    print("Tuple record:", tuple_user)
    print("Dataclass record:", dataclass_user)

    # A tuple is generally compact and positional.
    # A dataclass provides explicit named fields and richer behavior.
    print("Tuple field access:", tuple_user[0])
    print("Dataclass field access:", dataclass_user.name)

    try:
        dataclass_user.age = 31
    except Exception as error:
        print("Frozen dataclass rejects assignment:", type(error).__name__)


# ============================================================================
# 17. GENERATOR EXPRESSIONS AND TUPLES
# ============================================================================

def generator_examples() -> None:
    section("17. Generators and Tuple Materialization")

    generator = (number * number for number in range(5))
    print("Generator object:", generator)

    materialized = tuple(generator)
    print("Materialized tuple:", materialized)

    # Once consumed, a generator is exhausted.
    print("Generator after consumption:", tuple(generator))

    # This is useful when the source is lazy and the final result should be
    # an immutable snapshot.
    squares = tuple(number**2 for number in range(1, 6))
    print("Squares:", squares)


# ============================================================================
# 18. CONVERSION
# ============================================================================

def conversions() -> None:
    section("18. Conversions")

    original_tuple = (1, 2, 3)

    as_list = list(original_tuple)
    as_set = set(original_tuple)
    as_string = str(original_tuple)

    print("Tuple:", original_tuple)
    print("List:", as_list)
    print("Set:", as_set)
    print("String representation:", as_string)

    # Convert back after mutation.
    as_list.append(4)
    reconstructed = tuple(as_list)
    print("Reconstructed tuple:", reconstructed)


# ============================================================================
# 19. EDGE CASES
# ============================================================================

def edge_cases() -> None:
    section("19. Important Edge Cases")

    # Empty tuple.
    empty = ()
    print("Empty tuple length:", len(empty))

    # One-element tuple.
    one = 100,
    print("One-element tuple:", one)

    # Tuple containing None.
    nullable = (None, "value")
    print("None-containing tuple:", nullable)

    # Tuple containing booleans and integers.
    # True and 1 compare equal in Python.
    print("(True,) == (1,):", (True,) == (1,))
    print("Hash equality:", hash((True,)) == hash((1,)))

    # Tuple multiplication with zero and negative values.
    print("(1, 2) * 0:", (1, 2) * 0)
    print("(1, 2) * -1:", (1, 2) * -1)

    # Concatenating with a non-tuple raises TypeError.
    try:
        print((1, 2) + [3, 4])
    except TypeError as error:
        print("Invalid concatenation:", error)

    # A tuple can contain itself only through a mutable indirection; direct
    # recursive construction is not possible in a simple tuple literal.
    recursive_list: list[Any] = []
    recursive_tuple = (recursive_list,)
    recursive_list.append(recursive_tuple)
    print("Indirect recursive structure:", recursive_tuple)


# ============================================================================
# 20. COPYING
# ============================================================================

def copying_behavior() -> None:
    section("20. Copying Tuples")

    original = (1, 2, 3)
    copied = tuple(original)

    # CPython may return the same tuple object because tuples are immutable.
    print("Original is copied:", original is copied)

    nested = (["A", "B"],)
    shallow = tuple(nested)

    nested[0].append("C")

    print("Nested original:", nested)
    print("Nested shallow copy:", shallow)

    # The tuple container was not changed, but its referenced list was.
    print("Same inner list:", nested[0] is shallow[0])


# ============================================================================
# 21. PATTERN MATCHING
# ============================================================================

def structural_pattern_matching() -> None:
    section("21. Structural Pattern Matching")

    coordinate = (10, 20)

    match coordinate:
        case (0, 0):
            print("Origin")
        case (x, y):
            print(f"Coordinate x={x}, y={y}")

    command = ("move", 10, 20)

    match command:
        case ("move", x, y):
            print(f"Move to ({x}, {y})")
        case ("stop",):
            print("Stop")
        case _:
            print("Unknown command")

    # Sequence patterns can include a starred component.
    values = (1, 2, 3, 4, 5)

    match values:
        case (first, *middle, last):
            print("First:", first, "Middle:", middle, "Last:", last)


# ============================================================================
# 22. TYPE ANNOTATIONS
# ============================================================================

def typing_examples() -> None:
    section("22. Tuple Type Annotations")

    point: tuple[int, int] = (10, 20)
    rgb: tuple[int, int, int] = (255, 128, 0)

    # A variable-length tuple of one type:
    numbers: tuple[float, ...] = (1.0, 2.5, 3.75)

    print("Point:", point)
    print("RGB:", rgb)
    print("Numbers:", numbers)

    def get_user() -> tuple[str, int]:
        return "Atul", 30

    user_name, user_age = get_user()
    print(user_name, user_age)


# ============================================================================
# 23. TUPLES IN ALGORITHMS
# ============================================================================

def algorithm_examples() -> None:
    section("23. Tuples in Algorithms")

    # Priority queues commonly store tuples such as (priority, item).
    import heapq

    queue: list[tuple[int, str]] = []

    heapq.heappush(queue, (2, "Write report"))
    heapq.heappush(queue, (1, "Fix production bug"))
    heapq.heappush(queue, (3, "Review documentation"))

    while queue:
        priority, task = heapq.heappop(queue)
        print(f"priority={priority}: {task}")

    # Graph edge representation.
    edges = [
        ("A", "B", 4),
        ("A", "C", 2),
        ("C", "D", 1),
        ("B", "D", 5),
    ]

    adjacency: dict[str, list[tuple[str, int]]] = {}

    for source, destination, weight in edges:
        adjacency.setdefault(source, []).append((destination, weight))

    print("Adjacency list:", adjacency)


# ============================================================================
# 24. TUPLES IN DATA PROCESSING
# ============================================================================

def data_processing() -> None:
    section("24. Data Processing with Tuples")

    sales = (
        ("Laptop", 3, 75_000),
        ("Phone", 5, 30_000),
        ("Tablet", 2, 25_000),
    )

    totals = tuple(
        (product, quantity, quantity * unit_price)
        for product, quantity, unit_price in sales
    )

    for product, quantity, total in totals:
        print(f"{product}: quantity={quantity}, total={total}")

    total_revenue = sum(total for _, _, total in totals)
    print("Total revenue:", total_revenue)

    # Tuples are useful for fixed records, but dictionaries/dataclasses may be
    # clearer when records contain many fields.


# ============================================================================
# 25. VALIDATION
# ============================================================================

def validate_coordinate(value: Any) -> tuple[float, float]:
    """Validate and normalize a two-dimensional coordinate."""
    if not isinstance(value, tuple):
        raise TypeError("coordinate must be a tuple")

    if len(value) != 2:
        raise ValueError("coordinate must contain exactly two values")

    x, y = value

    if not isinstance(x, (int, float)) or isinstance(x, bool):
        raise TypeError("x must be numeric")

    if not isinstance(y, (int, float)) or isinstance(y, bool):
        raise TypeError("y must be numeric")

    return float(x), float(y)


def validation_examples() -> None:
    section("25. Validation")

    valid_values = [
        (10, 20),
        (-5.5, 4),
        (0, 0),
    ]

    for value in valid_values:
        print(value, "->", validate_coordinate(value))

    invalid_values = [
        [10, 20],
        (10,),
        ("10", 20),
        (True, 20),
    ]

    for value in invalid_values:
        try:
            validate_coordinate(value)
        except (TypeError, ValueError) as error:
            print(repr(value), "-> rejected:", error)


# ============================================================================
# 26. CUSTOM TUPLE SUBCLASS
# ============================================================================

class Coordinate(tuple):
    """A tuple subclass with named coordinate properties and validation."""

    __slots__ = ()

    def __new__(cls, x: float, y: float) -> "Coordinate":
        if not isinstance(x, (int, float)) or isinstance(x, bool):
            raise TypeError("x must be numeric")
        if not isinstance(y, (int, float)) or isinstance(y, bool):
            raise TypeError("y must be numeric")
        return super().__new__(cls, (x, y))

    @property
    def x(self) -> float:
        return self[0]

    @property
    def y(self) -> float:
        return self[1]

    def distance_from_origin(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5


def tuple_subclass_example() -> None:
    section("26. Tuple Subclass")

    point = Coordinate(3, 4)

    print("Point:", point)
    print("x:", point.x)
    print("y:", point.y)
    print("Distance:", point.distance_from_origin())
    print("Is tuple:", isinstance(point, tuple))

    try:
        point[0] = 99
    except TypeError as error:
        print("Still immutable:", error)


# ============================================================================
# 27. PRODUCTION-STYLE EXAMPLE
# ============================================================================

@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    account_id: str
    amount: float
    currency: str


def transaction_pipeline() -> None:
    section("27. Production-Style Tuple Usage")

    transactions = (
        ("TX001", "ACC100", 1500.00, "INR"),
        ("TX002", "ACC101", -250.00, "INR"),
        ("TX003", "ACC100", 750.00, "INR"),
    )

    # Tuple unpacking makes a fixed-format row easy to process.
    normalized: tuple[Transaction, ...] = tuple(
        Transaction(
            transaction_id=transaction_id,
            account_id=account_id,
            amount=amount,
            currency=currency,
        )
        for transaction_id, account_id, amount, currency in transactions
    )

    for transaction in normalized:
        print(transaction)

    account_totals: dict[str, float] = {}

    for transaction in normalized:
        account_totals[transaction.account_id] = (
            account_totals.get(transaction.account_id, 0.0)
            + transaction.amount
        )

    print("Account totals:", account_totals)


# ============================================================================
# 28. COMMON MISTAKES
# ============================================================================

def common_mistakes() -> None:
    section("28. Common Mistakes")

    # Mistake 1: forgetting the comma in a one-item tuple.
    value = ("Python")
    correct = ("Python",)

    print("Without comma:", type(value).__name__)
    print("With comma:", type(correct).__name__)

    # Mistake 2: expecting tuple methods such as append().
    values = (1, 2, 3)

    try:
        values.append(4)  # type: ignore[attr-defined]
    except AttributeError as error:
        print("No append():", error)

    # Mistake 3: assuming nested objects are automatically immutable.
    nested = (["A"],)
    nested[0].append("B")
    print("Mutable nested value:", nested)

    # Mistake 4: using an unhashable element in a key.
    try:
        dictionary = {(1, [2, 3]): "invalid"}
        print(dictionary)
    except TypeError as error:
        print("Invalid dictionary key:", error)


# ============================================================================
# 29. TESTING
# ============================================================================

def run_tests() -> None:
    section("29. Self-Tests")

    assert (1, 2, 3)[1] == 2
    assert (1,) == tuple([1])
    assert len(()) == 0
    assert (1, 2) + (3, 4) == (1, 2, 3, 4)
    assert (1, 2) * 2 == (1, 2, 1, 2)
    assert (1, 2, 1).count(1) == 2
    assert (10, 20, 30).index(20) == 1
    assert tuple(range(3)) == (0, 1, 2)

    minimum, maximum, average = calculate_statistics([10, 20, 30])
    assert minimum == 10
    assert maximum == 30
    assert average == 20

    assert validate_coordinate((1, 2)) == (1.0, 2.0)

    try:
        validate_coordinate((1,))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")

    point = Coordinate(3, 4)
    assert point.x == 3
    assert point.y == 4
    assert point.distance_from_origin() == 5

    print("All self-tests passed.")


# ============================================================================
# 30. FINAL STUDY DEMONSTRATION
# ============================================================================

def final_reference_demo() -> None:
    section("30. Compact Tuple Reference")

    examples = {
        "empty": (),
        "single": (42,),
        "multiple": (1, 2, 3),
        "packed": 1, 2, 3,
        "nested": ((1, 2), (3, 4)),
        "constructed": tuple([5, 6, 7]),
        "slice": (0, 1, 2, 3, 4)[1:4],
        "unpacked": None,
    }

    a, b, c = (10, 20, 30)
    examples["unpacked"] = (a, b, c)

    for name, value in examples.items():
        print(f"{name:12}: {value!r}")

    print("\nKey properties:")
    print("- ordered")
    print("- indexed")
    print("- iterable")
    print("- immutable at the container level")
    print("- can contain heterogeneous objects")
    print("- hashable when every contained object is hashable")
    print("- useful for fixed-format records and multiple return values")


def main() -> None:
    fundamentals()
    indexing_and_slicing()
    immutability()
    packing_and_unpacking()
    tuple_operations()
    tuple_methods()
    iteration()
    function_usage()
    dictionary_keys()
    sets_and_tuples()
    sorting_tuples()
    nested_data()
    tuples_vs_lists()
    performance()
    named_tuple_examples()
    dataclass_comparison()
    generator_examples()
    conversions()
    edge_cases()
    copying_behavior()
    structural_pattern_matching()
    typing_examples()
    algorithm_examples()
    data_processing()
    validation_examples()
    tuple_subclass_example()
    transaction_pipeline()
    common_mistakes()
    run_tests()
    final_reference_demo()


if __name__ == "__main__":
    main()
