"""
List Comprehensions: from fundamental expressions to advanced data-processing patterns.

This executable script focuses on Python list comprehensions and closely related
comprehension constructs. Every demonstration produces observable output and
includes validation, edge cases, performance considerations, and practical
data-processing examples.
"""

from __future__ import annotations

from dataclasses import dataclass
from timeit import timeit
from typing import Iterable, Iterator


def heading(title: str) -> None:
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def demonstrate_basic_comprehensions() -> None:
    heading("Basic list comprehensions")

    numbers = [1, 2, 3, 4, 5]

    squares = [number * number for number in numbers]
    print("Squares:", squares)

    doubled = [number * 2 for number in numbers]
    print("Doubled:", doubled)

    labels = [f"item-{number}" for number in numbers]
    print("Labels:", labels)

    # A comprehension evaluates the expression once for every input element.
    upper_names = [name.upper() for name in ["alice", "bob", "carol"]]
    print("Upper-case names:", upper_names)


def demonstrate_filtering() -> None:
    heading("Filtering with an if clause")

    numbers = list(range(1, 16))

    even_numbers = [number for number in numbers if number % 2 == 0]
    print("Even numbers:", even_numbers)

    odd_numbers = [number for number in numbers if number % 2 != 0]
    print("Odd numbers:", odd_numbers)

    positive_values = [value for value in [-4, 3, 0, 8, -1, 6] if value > 0]
    print("Positive values:", positive_values)

    # The condition determines whether the input element contributes
    # an output element. It does not transform the element itself.
    long_words = [
        word for word in ["database", "API", "repository", "SQL", "architecture"]
        if len(word) >= 6
    ]
    print("Words with at least six characters:", long_words)


def demonstrate_transformation_and_filtering() -> None:
    heading("Transformation combined with filtering")

    raw_values = ["  python ", "", "javascript", "  ", "C++", "java"]

    cleaned = [value.strip().lower() for value in raw_values if value.strip()]
    print("Cleaned non-empty values:", cleaned)

    even_squares = [number * number for number in range(20) if number % 2 == 0]
    print("Squares of even numbers:", even_squares)

    # The expression can be more complex than the condition.
    score_labels = [
        f"{score}:pass" if score >= 50 else f"{score}:fail"
        for score in [35, 50, 72, 91, 48]
    ]
    print("Score labels:", score_labels)


def demonstrate_nested_loops() -> None:
    heading("Nested loops inside a comprehension")

    coordinates = [
        (x, y)
        for x in range(3)
        for y in range(3)
    ]
    print("Coordinate pairs:", coordinates)

    multiplication_pairs = [
        (left, right, left * right)
        for left in range(1, 4)
        for right in range(1, 4)
    ]
    print("Multiplication pairs:", multiplication_pairs)

    # Multiple for clauses correspond to nested loops.
    flattened = [
        item
        for group in [[1, 2], [3, 4], [5, 6]]
        for item in group
    ]
    print("Flattened:", flattened)


def demonstrate_matrix_processing() -> None:
    heading("Matrix processing")

    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]

    flattened = [value for row in matrix for value in row]
    print("Flattened matrix:", flattened)

    transposed = [
        [matrix[row][column] for row in range(len(matrix))]
        for column in range(len(matrix[0]))
    ]
    print("Transposed matrix:", transposed)

    doubled_matrix = [
        [value * 2 for value in row]
        for row in matrix
    ]
    print("Doubled matrix:", doubled_matrix)


def demonstrate_conditional_expression() -> None:
    heading("Conditional expressions inside comprehensions")

    numbers = range(-3, 4)

    signs = [
        "positive" if number > 0 else
        "negative" if number < 0 else
        "zero"
        for number in numbers
    ]
    print("Signs:", signs)

    normalized = [
        value if value >= 0 else 0
        for value in [-5, 4, -1, 7, 0]
    ]
    print("Negative values replaced with zero:", normalized)


def demonstrate_strings() -> None:
    heading("String processing")

    text = "List comprehensions make Python data processing concise"

    words = text.split()
    lengths = [len(word) for word in words]
    print("Word lengths:", lengths)

    vowels = [character for character in text.lower() if character in "aeiou"]
    print("Vowels:", vowels)

    unique_letters = sorted({
        character.lower()
        for character in text
        if character.isalpha()
    })
    print("Unique alphabetic characters:", unique_letters)


def demonstrate_dictionaries_and_records() -> None:
    heading("Processing structured records")

    users = [
        {"name": "Alice", "active": True, "score": 92},
        {"name": "Bob", "active": False, "score": 61},
        {"name": "Carol", "active": True, "score": 84},
        {"name": "David", "active": True, "score": 47},
    ]

    active_names = [
        user["name"]
        for user in users
        if user["active"]
    ]
    print("Active users:", active_names)

    passing_active_users = [
        user["name"]
        for user in users
        if user["active"] and user["score"] >= 50
    ]
    print("Passing active users:", passing_active_users)

    score_map = {
        user["name"]: user["score"]
        for user in users
    }
    print("Score map created with dictionary comprehension:", score_map)


def demonstrate_set_and_generator_comprehensions() -> None:
    heading("Related comprehension forms")

    values = [1, 2, 2, 3, 3, 3, 4]

    unique_squares = {
        value * value
        for value in values
    }
    print("Set comprehension:", unique_squares)

    # A generator expression is lazy. It does not immediately construct
    # the complete result list in memory.
    lazy_squares = (
        value * value
        for value in values
    )
    print("Generator type:", type(lazy_squares).__name__)
    print("Generator values:", list(lazy_squares))


def demonstrate_functional_comprehensions() -> None:
    heading("Functions and comprehensions")

    def is_valid_score(score: int) -> bool:
        return 0 <= score <= 100

    scores = [88, 101, -3, 76, 45, 100]

    valid_scores = [
        score
        for score in scores
        if is_valid_score(score)
    ]
    print("Valid scores:", valid_scores)

    average = (
        sum(valid_scores) / len(valid_scores)
        if valid_scores
        else 0.0
    )
    print("Average valid score:", average)


@dataclass(frozen=True)
class Product:
    name: str
    price: float
    stock: int
    category: str


def demonstrate_domain_processing() -> None:
    heading("Practical domain example")

    products = [
        Product("Keyboard", 79.99, 12, "hardware"),
        Product("Mouse", 29.99, 0, "hardware"),
        Product("Monitor", 249.50, 7, "hardware"),
        Product("Notebook", 8.50, 25, "stationery"),
        Product("Cable", 12.75, 18, "hardware"),
    ]

    available_hardware = [
        product.name
        for product in products
        if product.category == "hardware" and product.stock > 0
    ]
    print("Available hardware:", available_hardware)

    inventory_values = {
        product.name: round(product.price * product.stock, 2)
        for product in products
    }
    print("Inventory values:", inventory_values)

    premium_products = [
        product.name
        for product in products
        if product.price >= 100 and product.stock > 0
    ]
    print("In-stock products costing at least 100:", premium_products)


def demonstrate_validation() -> None:
    heading("Validation and failure conditions")

    records = [
        {"name": "Alice", "age": 31},
        {"name": "Bob", "age": 17},
        {"name": "", "age": 28},
        {"name": "Carol", "age": 42},
        {"name": "Invalid", "age": -2},
    ]

    valid_names = [
        record["name"]
        for record in records
        if isinstance(record.get("name"), str)
        and bool(record["name"].strip())
        and isinstance(record.get("age"), int)
        and 0 <= record["age"] <= 130
    ]
    print("Names from valid records:", valid_names)

    # A common mistake is accessing a missing dictionary key directly.
    incomplete = {"name": "Eve"}

    try:
        ages = [
            record["age"]
            for record in [incomplete]
        ]
        print(ages)
    except KeyError as exc:
        print("Expected validation failure:", exc)

    safe_ages = [
        record.get("age")
        for record in [incomplete]
        if isinstance(record.get("age"), int)
    ]
    print("Safely extracted ages:", safe_ages)


def demonstrate_file_processing() -> None:
    heading("File-oriented processing without external packages")

    log_lines = [
        "INFO request accepted",
        "ERROR database unavailable",
        "INFO retry started",
        "WARNING retry limit approaching",
        "ERROR timeout",
    ]

    error_messages = [
        line
        for line in log_lines
        if line.startswith("ERROR")
    ]
    print("Error log entries:", error_messages)

    # This is equivalent to:
    # result = []
    # for line in log_lines:
    #     if "ERROR" in line:
    #         result.append(line)
    #
    # The comprehension expresses the same data-selection operation directly.
    error_count = sum(
        1
        for line in log_lines
        if "ERROR" in line
    )
    print("Number of errors:", error_count)


def demonstrate_edge_cases() -> None:
    heading("Edge cases")

    empty_result = [value * 2 for value in []]
    print("Empty input produces:", empty_result)

    nested_empty = [
        value
        for group in [[], [1, 2], []]
        for value in group
    ]
    print("Nested empty groups produce:", nested_empty)

    no_matches = [
        value
        for value in range(5)
        if value > 100
    ]
    print("No matching elements produce:", no_matches)

    # A condition involving zero must be written carefully when division
    # or indexing depends on the selected value.
    safe_reciprocals = [
        round(1 / value, 3)
        for value in [-2, -1, 0, 1, 2]
        if value != 0
    ]
    print("Safe reciprocals:", safe_reciprocals)


def demonstrate_readability_limits() -> None:
    heading("Readability boundaries")

    values = range(1, 11)

    readable = [
        number * number
        for number in values
        if number % 2 == 0
    ]
    print("Readable comprehension:", readable)

    # A deeply nested comprehension can become harder to review and debug.
    # When the transformation requires several business rules, explicit
    # functions or loops can be clearer than compressing everything into one line.
    complex_values = [
        (number, number ** 2)
        for number in values
        if number % 2 == 0
        and number ** 2 < 80
    ]
    print("Still-readable multi-condition example:", complex_values)


def demonstrate_performance() -> None:
    heading("Performance characteristics")

    data = list(range(100_000))

    def comprehension() -> list[int]:
        return [number * 2 for number in data]

    def explicit_loop() -> list[int]:
        result: list[int] = []
        for number in data:
            result.append(number * 2)
        return result

    comprehension_time = timeit(comprehension, number=20)
    loop_time = timeit(explicit_loop, number=20)

    print(f"List comprehension time: {comprehension_time:.6f}s")
    print(f"Explicit loop time:      {loop_time:.6f}s")

    # Both approaches materialize the complete list, so their result memory
    # requirement is broadly similar. For large streams, a generator expression
    # can avoid materializing every result simultaneously.
    generator = (number * 2 for number in data)
    first_five = [next(generator) for _ in range(5)]
    print("First five lazily generated values:", first_five)


def demonstrate_iterator_interaction() -> None:
    heading("Comprehensions with iterables")

    def values() -> Iterator[int]:
        yield 10
        yield 20
        yield 30
        yield 40

    result = [value + 5 for value in values()]
    print("Comprehension over a generator:", result)

    def positive(values: Iterable[int]) -> list[int]:
        return [value for value in values if value > 0]

    print("Reusable function:", positive([-3, 0, 4, 8, -1]))


def demonstrate_common_mistakes() -> None:
    heading("Common mistakes represented directly")

    values = [1, 2, 3, 4]

    # Filtering uses the trailing if clause.
    filtered = [value for value in values if value > 2]
    print("Correct filtering:", filtered)

    # Conditional output uses an if/else expression before the for clause.
    categorized = [
        "large" if value > 2 else "small"
        for value in values
    ]
    print("Conditional transformation:", categorized)

    # Nested loops can multiply the number of produced elements.
    pairs = [
        (left, right)
        for left in [1, 2]
        for right in [10, 20, 30]
    ]
    print("Nested-loop result count:", len(pairs))
    print("Nested-loop results:", pairs)


def main() -> None:
    demonstrate_basic_comprehensions()
    demonstrate_filtering()
    demonstrate_transformation_and_filtering()
    demonstrate_nested_loops()
    demonstrate_matrix_processing()
    demonstrate_conditional_expression()
    demonstrate_strings()
    demonstrate_dictionaries_and_records()
    demonstrate_set_and_generator_comprehensions()
    demonstrate_functional_comprehensions()
    demonstrate_domain_processing()
    demonstrate_validation()
    demonstrate_file_processing()
    demonstrate_edge_cases()
    demonstrate_readability_limits()
    demonstrate_performance()
    demonstrate_iterator_interaction()
    demonstrate_common_mistakes()


if __name__ == "__main__":
    main()
