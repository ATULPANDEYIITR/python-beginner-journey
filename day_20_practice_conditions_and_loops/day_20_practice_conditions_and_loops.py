"""
Practice: Conditions and Loops
==============================

A comprehensive standalone study program covering Python conditions and loops
from absolute beginner concepts through advanced control-flow techniques.

The file is intentionally executable. Run it with Python 3.8+.

Topics demonstrated:
- Boolean values and expressions
- Comparison and logical operators
- if, elif, and else
- Nested conditions
- Conditional expressions
- Truthiness and falsiness
- Membership and identity tests
- Guard clauses
- Validation
- for loops
- while loops
- range()
- enumerate()
- zip()
- dictionary iteration
- nested loops
- break, continue, and pass
- loop else clauses
- comprehensions
- generator expressions
- state-based loops
- sentinel-controlled loops
- retry logic
- simulations
- searching and filtering
- aggregation
- performance considerations
- common mistakes and edge cases
"""

from __future__ import annotations

import math
import random
import time
from collections import Counter
from typing import Iterable, Iterator


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def section(title: str) -> None:
    """Print a consistent section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    """Print a smaller heading."""
    print(f"\n--- {title} ---")


def demonstrate(title: str, value) -> None:
    """Print a labeled result."""
    print(f"{title}: {value}")


# ---------------------------------------------------------------------------
# 1. Boolean values
# ---------------------------------------------------------------------------

def boolean_basics() -> None:
    section("1. Boolean values and expressions")

    # A condition eventually produces a Boolean result: True or False.
    is_python = True
    is_difficult = False

    demonstrate("is_python", is_python)
    demonstrate("is_difficult", is_difficult)
    demonstrate("True and False", True and False)
    demonstrate("True or False", True or False)
    demonstrate("not True", not True)

    age = 25
    demonstrate("age >= 18", age >= 18)
    demonstrate("age == 25", age == 25)
    demonstrate("age != 30", age != 30)
    demonstrate("age < 18", age < 18)
    demonstrate("age <= 25", age <= 25)
    demonstrate("age > 20", age > 20)


# ---------------------------------------------------------------------------
# 2. Comparison operators
# ---------------------------------------------------------------------------

def comparison_examples() -> None:
    section("2. Comparison operators")

    first = 10
    second = 20

    comparisons = {
        "10 == 20": first == second,
        "10 != 20": first != second,
        "10 < 20": first < second,
        "10 <= 20": first <= second,
        "10 > 20": first > second,
        "10 >= 20": first >= second,
    }

    for expression, result in comparisons.items():
        print(f"{expression:<12} -> {result}")

    # Python supports chained comparisons.
    temperature = 24
    demonstrate("18 <= temperature <= 30", 18 <= temperature <= 30)

    # This is equivalent to:
    equivalent = temperature >= 18 and temperature <= 30
    demonstrate("Equivalent expression", equivalent)


# ---------------------------------------------------------------------------
# 3. Logical operators
# ---------------------------------------------------------------------------

def logical_operator_examples() -> None:
    section("3. Logical operators")

    age = 30
    has_id = True
    is_student = False

    # AND requires both expressions to be truthy.
    can_enter = age >= 18 and has_id

    # OR requires at least one expression to be truthy.
    receives_discount = is_student or age >= 60

    # NOT reverses a Boolean result.
    needs_id = not has_id

    demonstrate("can_enter", can_enter)
    demonstrate("receives_discount", receives_discount)
    demonstrate("needs_id", needs_id)

    # Short-circuit evaluation matters:
    # the second expression is not evaluated when the first already
    # determines the result.
    value = None
    if value is not None and value > 10:
        print("Value is greater than 10.")
    else:
        print("Safe short-circuit evaluation prevented None > 10.")


# ---------------------------------------------------------------------------
# 4. if, elif, else
# ---------------------------------------------------------------------------

def grade_classifier(score: float) -> str:
    """Classify a score using mutually exclusive conditions."""
    if score < 0 or score > 100:
        return "Invalid score"
    elif score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def conditional_statements() -> None:
    section("4. if, elif, and else")

    scores = [95, 84, 72, 61, 43, -5, 101]

    for score in scores:
        print(f"Score {score:>3}: {grade_classifier(score)}")

    # Conditions can be nested, but excessive nesting often reduces clarity.
    age = 22
    has_ticket = True

    if age >= 18:
        if has_ticket:
            print("Nested condition: admission permitted.")
        else:
            print("Nested condition: ticket required.")
    else:
        print("Nested condition: visitor is under the required age.")


# ---------------------------------------------------------------------------
# 5. Truthiness
# ---------------------------------------------------------------------------

def truthiness_examples() -> None:
    section("5. Truthiness and falsiness")

    # These values are false in Boolean contexts:
    false_values = [False, None, 0, 0.0, "", [], {}, set()]

    for value in false_values:
        print(f"{value!r:<12} -> bool(value) = {bool(value)}")

    # Non-empty containers and non-zero numbers are normally truthy.
    true_values = [True, 1, -1, 3.14, "Python", [1], {"x": 1}]

    for value in true_values:
        print(f"{value!r:<12} -> bool(value) = {bool(value)}")

    names = []

    if not names:
        print("An empty list can be tested directly without len(names) == 0.")


# ---------------------------------------------------------------------------
# 6. Membership and identity
# ---------------------------------------------------------------------------

def membership_and_identity() -> None:
    section("6. Membership and identity")

    allowed_roles = {"admin", "manager", "analyst"}
    role = "analyst"

    if role in allowed_roles:
        print(f"{role!r} is an allowed role.")

    if "guest" not in allowed_roles:
        print("'guest' is not an allowed role.")

    # 'is' tests object identity, not ordinary value equality.
    value = None

    if value is None:
        print("Use 'is None' when checking specifically for None.")

    first_list = [1, 2, 3]
    second_list = [1, 2, 3]
    same_reference = first_list

    demonstrate("first_list == second_list", first_list == second_list)
    demonstrate("first_list is second_list", first_list is second_list)
    demonstrate("first_list is same_reference", first_list is same_reference)


# ---------------------------------------------------------------------------
# 7. Conditional expressions
# ---------------------------------------------------------------------------

def conditional_expression_examples() -> None:
    section("7. Conditional expressions")

    age = 20
    status = "adult" if age >= 18 else "minor"

    demonstrate("status", status)

    number = 7
    parity = "even" if number % 2 == 0 else "odd"

    demonstrate("parity", parity)

    # Conditional expressions are useful for simple decisions.
    # Large multi-branch decisions should normally use regular if/elif/else.
    score = 83
    category = (
        "excellent" if score >= 90
        else "good" if score >= 75
        else "needs improvement"
    )
    demonstrate("score category", category)


# ---------------------------------------------------------------------------
# 8. Functions with guard clauses
# ---------------------------------------------------------------------------

def calculate_discount(price: float, customer_type: str) -> float:
    """
    Calculate a discount while validating input early.

    Guard clauses reduce unnecessary nesting by returning immediately when
    an invalid condition is detected.
    """
    if price < 0:
        raise ValueError("Price cannot be negative.")

    if customer_type not in {"regular", "student", "premium"}:
        raise ValueError("Unknown customer type.")

    if customer_type == "premium":
        return price * 0.20

    if customer_type == "student":
        return price * 0.10

    return price * 0.05


def guard_clause_examples() -> None:
    section("8. Guard clauses and validation")

    for price, customer_type in [
        (1000, "regular"),
        (1000, "student"),
        (1000, "premium"),
    ]:
        discount = calculate_discount(price, customer_type)
        print(
            f"{customer_type:<8} price={price:.2f}, "
            f"discount={discount:.2f}, final={price - discount:.2f}"
        )

    for invalid_input in [(-100, "regular"), (100, "unknown")]:
        try:
            calculate_discount(*invalid_input)
        except ValueError as error:
            print(f"Validation error: {error}")


# ---------------------------------------------------------------------------
# 9. Basic for loops
# ---------------------------------------------------------------------------

def basic_for_loops() -> None:
    section("9. for loops")

    # A for loop processes each item in an iterable.
    languages = ["Python", "JavaScript", "C++"]

    for language in languages:
        print(f"Learning {language}")

    # Strings are iterable, so a loop can inspect each character.
    for character in "LOOP":
        print(character, end=" ")
    print()

    # range(start, stop, step) excludes stop.
    for number in range(1, 6):
        print(number, end=" ")
    print()

    for number in range(10, 0, -2):
        print(number, end=" ")
    print()


# ---------------------------------------------------------------------------
# 10. enumerate
# ---------------------------------------------------------------------------

def enumerate_examples() -> None:
    section("10. enumerate()")

    subjects = ["conditions", "loops", "functions", "classes"]

    # enumerate gives both the position and the value.
    for index, subject in enumerate(subjects, start=1):
        print(f"{index}. {subject}")

    # This is preferable to manually maintaining an index variable.
    # It avoids several common off-by-one errors.


# ---------------------------------------------------------------------------
# 11. zip
# ---------------------------------------------------------------------------

def zip_examples() -> None:
    section("11. zip()")

    names = ["Asha", "Ravi", "Mina"]
    scores = [92, 85, 78]

    for name, score in zip(names, scores):
        print(f"{name}: {score}")

    # zip stops when the shortest iterable is exhausted.
    short = [1, 2]
    long = ["a", "b", "c", "d"]

    print("Default zip:", list(zip(short, long)))

    # strict=True can detect accidental length mismatches.
    try:
        list(zip(short, long, strict=True))
    except ValueError as error:
        print(f"Strict zip detected mismatch: {error}")


# ---------------------------------------------------------------------------
# 12. Dictionary iteration
# ---------------------------------------------------------------------------

def dictionary_iteration() -> None:
    section("12. Iterating through dictionaries")

    inventory = {
        "laptop": 8,
        "keyboard": 15,
        "mouse": 22,
    }

    for product, quantity in inventory.items():
        print(f"{product:<10} -> {quantity}")

    print("Products:")
    for product in inventory:
        print(product)

    print("Quantities:")
    for quantity in inventory.values():
        print(quantity)


# ---------------------------------------------------------------------------
# 13. while loops
# ---------------------------------------------------------------------------

def basic_while_loops() -> None:
    section("13. while loops")

    counter = 1

    while counter <= 5:
        print(f"Counter = {counter}")
        counter += 1

    # A while loop is appropriate when the number of iterations depends on
    # changing state rather than a known collection.


def countdown(start: int) -> None:
    """Demonstrate a state-controlled loop."""
    if start < 0:
        raise ValueError("Countdown cannot start below zero.")

    while start > 0:
        print(start)
        start -= 1

    print("Go!")


# ---------------------------------------------------------------------------
# 14. break
# ---------------------------------------------------------------------------

def break_examples() -> None:
    section("14. break")

    numbers = [4, 7, 11, 15, 21, 30]
    target = 15

    for number in numbers:
        print(f"Checking {number}")
        if number == target:
            print("Target found; stopping early.")
            break

    # break can substantially reduce work when a result is found early.


# ---------------------------------------------------------------------------
# 15. continue
# ---------------------------------------------------------------------------

def continue_examples() -> None:
    section("15. continue")

    for number in range(1, 11):
        if number % 2 == 0:
            continue

        # Only odd numbers reach this point.
        print(number, end=" ")
    print()


# ---------------------------------------------------------------------------
# 16. pass
# ---------------------------------------------------------------------------

def pass_examples() -> None:
    section("16. pass")

    # pass does nothing. It is syntactically useful when an empty block
    # is temporarily or intentionally required.
    for number in range(3):
        if number == 1:
            pass
        print(f"Processed {number}")


# ---------------------------------------------------------------------------
# 17. Loop else
# ---------------------------------------------------------------------------

def loop_else_examples() -> None:
    section("17. for/while else")

    numbers = [2, 4, 6, 8, 10]
    target = 7

    for number in numbers:
        if number == target:
            print("Found target.")
            break
    else:
        # This else belongs to the loop, not to the if.
        # It executes when the loop completes without break.
        print("Target was not found.")

    attempts = 3

    while attempts > 0:
        print(f"Attempt remaining: {attempts}")
        attempts -= 1
    else:
        print("while loop completed normally.")


# ---------------------------------------------------------------------------
# 18. Nested loops
# ---------------------------------------------------------------------------

def nested_loop_examples() -> None:
    section("18. Nested loops")

    for row in range(1, 4):
        values = []
        for column in range(1, 5):
            values.append(row * column)
        print(values)

    # Nested loops often have multiplicative complexity.
    # If the outer loop runs n times and the inner loop runs m times,
    # the body can execute approximately n * m times.


# ---------------------------------------------------------------------------
# 19. Pattern generation
# ---------------------------------------------------------------------------

def pattern_generation() -> None:
    section("19. Pattern generation with nested loops")

    for row in range(1, 6):
        print("*" * row)

    print()

    for row in range(5, 0, -1):
        print("*" * row)


# ---------------------------------------------------------------------------
# 20. Searching
# ---------------------------------------------------------------------------

def linear_search(items: Iterable[int], target: int) -> int:
    """
    Return the first matching index, or -1.

    Linear search has O(n) worst-case time complexity.
    """
    for index, item in enumerate(items):
        if item == target:
            return index
    return -1


def searching_examples() -> None:
    section("20. Searching with conditions and loops")

    values = [12, 4, 19, 7, 31, 9]

    for target in [19, 100]:
        index = linear_search(values, target)
        print(f"Target {target}: index={index}")


# ---------------------------------------------------------------------------
# 21. Filtering and aggregation
# ---------------------------------------------------------------------------

def filtering_and_aggregation() -> None:
    section("21. Filtering and aggregation")

    transactions = [1200, -300, 450, -150, 800, -50]

    total_income = 0
    total_expenses = 0

    for amount in transactions:
        if amount >= 0:
            total_income += amount
        else:
            total_expenses += abs(amount)

    print(f"Income:   {total_income}")
    print(f"Expenses: {total_expenses}")
    print(f"Balance:  {total_income - total_expenses}")

    positive_transactions = [
        amount for amount in transactions if amount > 0
    ]
    print("Positive transactions:", positive_transactions)


# ---------------------------------------------------------------------------
# 22. Comprehensions
# ---------------------------------------------------------------------------

def comprehension_examples() -> None:
    section("22. List, set, and dictionary comprehensions")

    squares = [number * number for number in range(1, 11)]
    even_squares = [
        number * number
        for number in range(1, 11)
        if number % 2 == 0
    ]

    print("Squares:", squares)
    print("Even squares:", even_squares)

    unique_remainders = {
        number % 3
        for number in range(20)
    }

    print("Unique remainders:", unique_remainders)

    square_map = {
        number: number * number
        for number in range(1, 6)
    }

    print("Square map:", square_map)


# ---------------------------------------------------------------------------
# 23. Generator expressions
# ---------------------------------------------------------------------------

def generator_examples() -> None:
    section("23. Generator expressions")

    # A generator computes values lazily rather than constructing the entire
    # result list immediately.
    squares = (number * number for number in range(1, 6))

    print("Generator values:")
    for square in squares:
        print(square)

    # Generator expressions are useful for large streams of data.
    large_sum = sum(number * number for number in range(1_000_000))
    print("Sum of one million squares:", large_sum)


# ---------------------------------------------------------------------------
# 24. Nested data processing
# ---------------------------------------------------------------------------

def nested_data_processing() -> None:
    section("24. Nested data processing")

    students = [
        {"name": "Asha", "scores": [90, 88, 94]},
        {"name": "Ravi", "scores": [70, 82, 76]},
        {"name": "Mina", "scores": [98, 96, 99]},
    ]

    for student in students:
        scores = student["scores"]
        average = sum(scores) / len(scores)

        if average >= 90:
            performance = "excellent"
        elif average >= 75:
            performance = "good"
        else:
            performance = "needs improvement"

        print(
            f"{student['name']}: average={average:.2f}, "
            f"performance={performance}"
        )


# ---------------------------------------------------------------------------
# 25. Input validation without requiring user interaction
# ---------------------------------------------------------------------------

def validate_integer(value: str, minimum: int, maximum: int) -> int:
    """Convert and validate an integer represented as text."""
    try:
        number = int(value)
    except ValueError as error:
        raise ValueError("Input must be an integer.") from error

    if not minimum <= number <= maximum:
        raise ValueError(
            f"Input must be between {minimum} and {maximum}."
        )

    return number


def validation_examples() -> None:
    section("25. Validation with conditions and exceptions")

    test_inputs = ["42", "abc", "101", "-4", "75"]

    for raw_value in test_inputs:
        try:
            value = validate_integer(raw_value, 0, 100)
            print(f"{raw_value!r} -> accepted as {value}")
        except ValueError as error:
            print(f"{raw_value!r} -> rejected: {error}")


# ---------------------------------------------------------------------------
# 26. Sentinel-controlled loop
# ---------------------------------------------------------------------------

def process_until_sentinel(values: Iterable[int], sentinel: int = -1) -> int:
    """
    Process values until a sentinel appears.

    A sentinel is a special value that means "stop processing".
    """
    total = 0

    for value in values:
        if value == sentinel:
            break

        if value < 0:
            continue

        total += value

    return total


def sentinel_examples() -> None:
    section("26. Sentinel-controlled processing")

    values = [10, 20, -5, 30, 40, -1, 999]
    total = process_until_sentinel(values)

    print("Input:", values)
    print("Total before sentinel:", total)


# ---------------------------------------------------------------------------
# 27. Retry logic
# ---------------------------------------------------------------------------

def retry_operation(
    attempts: int,
    outcomes: list[bool],
) -> bool:
    """
    Demonstrate bounded retry logic.

    The function stops after the first successful attempt.
    """
    if attempts <= 0:
        raise ValueError("attempts must be positive")

    for attempt_number in range(1, attempts + 1):
        success = (
            outcomes[attempt_number - 1]
            if attempt_number - 1 < len(outcomes)
            else False
        )

        print(f"Attempt {attempt_number}: {'success' if success else 'failure'}")

        if success:
            return True

    return False


def retry_examples() -> None:
    section("27. Retry logic")

    success = retry_operation(4, [False, False, True])
    print("Final result:", success)

    success = retry_operation(3, [False, False, False])
    print("Final result:", success)


# ---------------------------------------------------------------------------
# 28. Menu-style state machine
# ---------------------------------------------------------------------------

def state_machine_example() -> None:
    section("28. State-machine style while loop")

    states = ["START", "AUTHENTICATE", "LOAD_DATA", "PROCESS", "END"]
    index = 0

    while index < len(states):
        state = states[index]

        if state == "START":
            print("System started.")
        elif state == "AUTHENTICATE":
            print("Authentication completed.")
        elif state == "LOAD_DATA":
            print("Data loaded.")
        elif state == "PROCESS":
            print("Data processed.")
        elif state == "END":
            print("System stopped.")

        index += 1


# ---------------------------------------------------------------------------
# 29. Prime number detection
# ---------------------------------------------------------------------------

def is_prime(number: int) -> bool:
    """
    Determine whether number is prime.

    Only divisors up to sqrt(number) need to be tested.
    This reduces the trial-division work from O(n) to O(sqrt(n)).
    """
    if number < 2:
        return False

    if number == 2:
        return True

    if number % 2 == 0:
        return False

    divisor = 3
    limit = math.isqrt(number)

    while divisor <= limit:
        if number % divisor == 0:
            return False
        divisor += 2

    return True


def prime_examples() -> None:
    section("29. Prime detection")

    for number in range(1, 31):
        if is_prime(number):
            print(number, end=" ")
    print()


# ---------------------------------------------------------------------------
# 30. Fibonacci sequence
# ---------------------------------------------------------------------------

def fibonacci_iterative(count: int) -> list[int]:
    """Generate Fibonacci numbers using an iterative loop."""
    if count < 0:
        raise ValueError("count cannot be negative")

    result: list[int] = []
    first, second = 0, 1

    for _ in range(count):
        result.append(first)
        first, second = second, first + second

    return result


def fibonacci_examples() -> None:
    section("30. Fibonacci with loops")

    print(fibonacci_iterative(15))


# ---------------------------------------------------------------------------
# 31. Frequency counting
# ---------------------------------------------------------------------------

def frequency_count(text: str) -> dict[str, int]:
    """Count alphabetic characters using a loop."""
    frequencies: dict[str, int] = {}

    for character in text.lower():
        if character.isalpha():
            frequencies[character] = frequencies.get(character, 0) + 1

    return frequencies


def frequency_examples() -> None:
    section("31. Frequency counting")

    text = "Conditions and loops"
    print(frequency_count(text))

    # Counter is a specialized standard-library implementation.
    print("Counter:", Counter(character for character in text.lower() if character.isalpha()))


# ---------------------------------------------------------------------------
# 32. Matrix traversal
# ---------------------------------------------------------------------------

def matrix_examples() -> None:
    section("32. Matrix traversal with nested loops")

    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]

    total = 0

    for row in matrix:
        for value in row:
            total += value

    print("Matrix:")
    for row in matrix:
        print(row)

    print("Matrix total:", total)


# ---------------------------------------------------------------------------
# 33. Early exit from nested loops
# ---------------------------------------------------------------------------

def find_pair_with_sum(numbers: list[int], target: int) -> tuple[int, int] | None:
    """
    Find the first pair whose sum equals target.

    The explicit return from the function exits both loops immediately.
    Worst-case complexity is O(n^2).
    """
    for first_index in range(len(numbers)):
        for second_index in range(first_index + 1, len(numbers)):
            if numbers[first_index] + numbers[second_index] == target:
                return numbers[first_index], numbers[second_index]

    return None


def nested_search_example() -> None:
    section("33. Exiting nested loops")

    numbers = [3, 8, 12, 17, 21]
    print("Pair:", find_pair_with_sum(numbers, 29))


# ---------------------------------------------------------------------------
# 34. Optimized pair search
# ---------------------------------------------------------------------------

def find_pair_with_sum_fast(
    numbers: Iterable[int],
    target: int,
) -> tuple[int, int] | None:
    """
    Find a pair using a set.

    Expected time complexity is O(n), with O(n) additional space.
    """
    seen: set[int] = set()

    for number in numbers:
        required = target - number

        if required in seen:
            return required, number

        seen.add(number)

    return None


def optimized_search_example() -> None:
    section("34. Trading space for speed")

    numbers = [3, 8, 12, 17, 21]
    print("Fast pair:", find_pair_with_sum_fast(numbers, 29))


# ---------------------------------------------------------------------------
# 35. Loop invariant example
# ---------------------------------------------------------------------------

def maximum_value(numbers: Iterable[int]) -> int:
    """
    Find the maximum value.

    Loop invariant:
    after processing each item, 'current_max' is the maximum of all
    items processed so far.
    """
    iterator = iter(numbers)

    try:
        current_max = next(iterator)
    except StopIteration as error:
        raise ValueError("At least one value is required.") from error

    for number in iterator:
        if number > current_max:
            current_max = number

    return current_max


def loop_invariant_example() -> None:
    section("35. Loop invariants")

    values = [14, 7, 31, 5, 22]
    print("Maximum:", maximum_value(values))

    try:
        maximum_value([])
    except ValueError as error:
        print("Empty-input edge case:", error)


# ---------------------------------------------------------------------------
# 36. Simulation
# ---------------------------------------------------------------------------

def dice_simulation(
    rolls: int,
    seed: int = 42,
) -> Counter[int]:
    """
    Simulate dice rolls.

    A deterministic seed makes the educational example reproducible.
    """
    if rolls < 0:
        raise ValueError("rolls cannot be negative")

    generator = random.Random(seed)
    frequencies: Counter[int] = Counter()

    for _ in range(rolls):
        outcome = generator.randint(1, 6)
        frequencies[outcome] += 1

    return frequencies


def simulation_example() -> None:
    section("36. Loop-based simulation")

    frequencies = dice_simulation(1000)
    print(dict(sorted(frequencies.items())))


# ---------------------------------------------------------------------------
# 37. Performance comparison
# ---------------------------------------------------------------------------

def loop_performance_demo(size: int = 100_000) -> None:
    section("37. Performance considerations")

    values = list(range(size))

    start = time.perf_counter()
    total_loop = 0

    for value in values:
        total_loop += value

    loop_time = time.perf_counter() - start

    start = time.perf_counter()
    total_builtin = sum(values)
    builtin_time = time.perf_counter() - start

    print("Loop total:", total_loop)
    print("sum() total:", total_builtin)
    print(f"Explicit loop time: {loop_time:.6f}s")
    print(f"sum() time:         {builtin_time:.6f}s")

    # Built-in operations are often implemented in optimized C and may be
    # faster than an equivalent Python-level loop. Correctness and clarity
    # still matter more than micro-optimizing tiny workloads.


# ---------------------------------------------------------------------------
# 38. Common off-by-one mistakes
# ---------------------------------------------------------------------------

def off_by_one_examples() -> None:
    section("38. Off-by-one errors")

    # range(5) produces 0, 1, 2, 3, 4, not 5.
    print("range(5):", list(range(5)))

    # To process exactly five positions starting at one:
    print("range(1, 6):", list(range(1, 6)))

    # Empty ranges are valid.
    print("range(5, 5):", list(range(5, 5)))


# ---------------------------------------------------------------------------
# 39. Infinite loop warning represented safely
# ---------------------------------------------------------------------------

def safe_state_loop() -> None:
    section("39. Avoiding accidental infinite loops")

    counter = 0

    while True:
        print(f"Iteration {counter}")

        if counter >= 2:
            break

        # A state-changing operation is essential in a bounded loop.
        counter += 1


# ---------------------------------------------------------------------------
# 40. Complex business rule engine
# ---------------------------------------------------------------------------

def calculate_shipping(
    weight_kg: float,
    distance_km: float,
    is_member: bool,
    fragile: bool,
) -> float:
    """
    Calculate shipping cost through multiple conditional rules.

    The function demonstrates how conditions can be combined while keeping
    each rule explicit.
    """
    if weight_kg <= 0:
        raise ValueError("Weight must be positive.")

    if distance_km < 0:
        raise ValueError("Distance cannot be negative.")

    base_cost = 50.0
    weight_cost = weight_kg * 20.0
    distance_cost = distance_km * 0.5

    cost = base_cost + weight_cost + distance_cost

    if fragile:
        cost += 100.0

    if is_member:
        cost *= 0.90

    if weight_kg > 20:
        cost += 200.0

    return round(cost, 2)


def business_rules_example() -> None:
    section("40. Multiple business rules")

    orders = [
        {"weight": 2, "distance": 10, "member": False, "fragile": False},
        {"weight": 5, "distance": 100, "member": True, "fragile": True},
        {"weight": 25, "distance": 50, "member": True, "fragile": False},
    ]

    for order in orders:
        cost = calculate_shipping(
            order["weight"],
            order["distance"],
            order["member"],
            order["fragile"],
        )
        print(order, "-> shipping =", cost)


# ---------------------------------------------------------------------------
# 41. Iterator protocol
# ---------------------------------------------------------------------------

class CountdownIterator:
    """
    Custom iterator showing how a for loop works conceptually.

    Python's for loop repeatedly requests the next item until StopIteration.
    """

    def __init__(self, start: int):
        self.current = start

    def __iter__(self) -> "CountdownIterator":
        return self

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration

        value = self.current
        self.current -= 1
        return value


def iterator_protocol_example() -> None:
    section("41. Iterator protocol")

    for value in CountdownIterator(5):
        print(value, end=" ")
    print()


# ---------------------------------------------------------------------------
# 42. Generator function
# ---------------------------------------------------------------------------

def fibonacci_generator(count: int) -> Iterator[int]:
    """Yield Fibonacci values one at a time."""
    if count < 0:
        raise ValueError("count cannot be negative")

    first, second = 0, 1

    for _ in range(count):
        yield first
        first, second = second, first + second


def generator_function_example() -> None:
    section("42. Generator functions")

    for value in fibonacci_generator(10):
        print(value, end=" ")
    print()


# ---------------------------------------------------------------------------
# 43. Practical transaction risk classifier
# ---------------------------------------------------------------------------

def classify_transaction(
    amount: float,
    country_match: bool,
    known_device: bool,
    transaction_count_last_hour: int,
) -> str:
    """
    Classify a transaction using deterministic rules.

    This is an educational rule engine, not a real fraud detector.
    """
    if amount <= 0:
        return "invalid"

    if transaction_count_last_hour < 0:
        return "invalid"

    if amount >= 100_000:
        return "manual_review"

    if not country_match and not known_device:
        return "high_risk"

    if transaction_count_last_hour > 20:
        return "high_risk"

    if not country_match or not known_device:
        return "review"

    return "normal"


def transaction_example() -> None:
    section("43. Practical rule-based classification")

    transactions = [
        (2500, True, True, 2),
        (15000, False, True, 4),
        (300000, True, True, 1),
        (5000, False, False, 2),
        (1000, True, True, 25),
    ]

    for transaction in transactions:
        print(transaction, "->", classify_transaction(*transaction))


# ---------------------------------------------------------------------------
# 44. Main execution
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Execute all demonstrations in a controlled order.

    Keeping execution inside main() prevents examples from running merely
    because another Python file imports this module.
    """
    boolean_basics()
    comparison_examples()
    logical_operator_examples()
    conditional_statements()
    truthiness_examples()
    membership_and_identity()
    conditional_expression_examples()
    guard_clause_examples()
    basic_for_loops()
    enumerate_examples()
    zip_examples()
    dictionary_iteration()
    basic_while_loops()
    countdown(3)
    break_examples()
    continue_examples()
    pass_examples()
    loop_else_examples()
    nested_loop_examples()
    pattern_generation()
    searching_examples()
    filtering_and_aggregation()
    comprehension_examples()
    generator_examples()
    nested_data_processing()
    validation_examples()
    sentinel_examples()
    retry_examples()
    state_machine_example()
    prime_examples()
    fibonacci_examples()
    frequency_examples()
    matrix_examples()
    nested_search_example()
    optimized_search_example()
    loop_invariant_example()
    simulation_example()
    loop_performance_demo()
    off_by_one_examples()
    safe_state_loop()
    business_rules_example()
    iterator_protocol_example()
    generator_function_example()
    transaction_example()

    section("Study checklist")
    checklist = [
        "Can you write a condition using ==, !=, <, <=, >, and >=?",
        "Can you combine conditions using and, or, and not?",
        "Can you explain the difference between == and is?",
        "Can you explain Python truthiness?",
        "Can you choose between if and a conditional expression?",
        "Can you use for with lists, strings, dictionaries, and range()?",
        "Can you explain when while is preferable to for?",
        "Can you use break and continue deliberately?",
        "Can you explain loop else?",
        "Can you avoid off-by-one errors?",
        "Can you analyze the cost of nested loops?",
        "Can you use a set to optimize repeated membership checks?",
        "Can you explain the difference between a list comprehension and generator?",
        "Can you validate loop inputs and handle failure cases?",
        "Can you identify and prevent accidental infinite loops?",
    ]

    for item in checklist:
        print(f"[ ] {item}")


if __name__ == "__main__":
    main()
