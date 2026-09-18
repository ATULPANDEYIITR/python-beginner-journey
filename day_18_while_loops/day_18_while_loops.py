"""
WHILE LOOPS: BEGINNER TO ADVANCED
=================================

A comprehensive executable study file covering while loops in Python:
fundamentals, syntax, conditions, counters, sentinels, validation, nested
loops, break, continue, else, infinite loops, iteration patterns, state
machines, simulations, algorithms, performance, debugging, and practical
design.

Run:
    python while_loops.py
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isqrt
from typing import Callable, Iterable


# ---------------------------------------------------------------------------
# 1. FUNDAMENTALS
# ---------------------------------------------------------------------------

def example_basic_while() -> None:
    """A while loop repeats while its condition remains True."""
    print("\n1. Basic while loop")

    number = 1
    while number <= 5:
        print(number, end=" ")
        number += 1

    print()


def example_countdown() -> None:
    """The loop condition is checked before every iteration."""
    print("\n2. Countdown")

    remaining = 5
    while remaining > 0:
        print(remaining, end=" ")
        remaining -= 1

    print("Blast off!")


def example_condition_changes() -> None:
    """A while loop normally needs state that eventually changes."""
    print("\n3. Changing loop state")

    balance = 100
    withdrawal = 30

    while balance >= withdrawal:
        balance -= withdrawal
        print(f"Withdrawal accepted. Remaining balance: {balance}")

    print(f"Final balance: {balance}")


# ---------------------------------------------------------------------------
# 2. COUNTER-CONTROLLED LOOPS
# ---------------------------------------------------------------------------

def example_counter_patterns() -> None:
    print("\n4. Counter patterns")

    # Increasing counter.
    i = 0
    while i < 5:
        print(f"increasing: {i}")
        i += 1

    # Decreasing counter.
    i = 5
    while i > 0:
        print(f"decreasing: {i}")
        i -= 1

    # Custom step.
    i = 0
    while i <= 20:
        if i % 4 == 0:
            print(f"multiple of four: {i}")
        i += 1


# ---------------------------------------------------------------------------
# 3. USER-INPUT STYLE VALIDATION
# ---------------------------------------------------------------------------

def validate_positive_integer(value: str) -> int:
    """Convert text to a positive integer or raise ValueError."""
    try:
        number = int(value)
    except ValueError as exc:
        raise ValueError("Input must be an integer.") from exc

    if number <= 0:
        raise ValueError("Input must be greater than zero.")

    return number


def example_input_validation(values: list[str]) -> int | None:
    """
    Simulate repeated input validation without requiring interactive input.

    A real program could replace the list with input().
    """
    print("\n5. Repeated validation")

    index = 0

    while index < len(values):
        raw_value = values[index]
        index += 1

        try:
            number = validate_positive_integer(raw_value)
        except ValueError as exc:
            print(f"Rejected {raw_value!r}: {exc}")
            continue

        print(f"Accepted: {number}")
        return number

    print("No valid value was supplied.")
    return None


# ---------------------------------------------------------------------------
# 4. SENTINEL-CONTROLLED LOOPS
# ---------------------------------------------------------------------------

def sum_until_sentinel(numbers: Iterable[int], sentinel: int = -1) -> int:
    """
    Consume values until a sentinel appears.

    The sentinel terminates the process but is not included in the sum.
    """
    values = iter(numbers)
    total = 0

    while True:
        try:
            value = next(values)
        except StopIteration:
            break

        if value == sentinel:
            break

        total += value

    return total


def example_sentinel_loop() -> None:
    print("\n6. Sentinel-controlled loop")

    data = [10, 20, 30, 40, -1, 999]
    result = sum_until_sentinel(data)
    print(f"Sum before sentinel: {result}")


# ---------------------------------------------------------------------------
# 5. BOOLEAN FLAGS
# ---------------------------------------------------------------------------

def example_boolean_flag() -> None:
    print("\n7. Boolean flag")

    values = [4, 8, 12, 15, 20]
    index = 0
    found_odd = False

    while index < len(values) and not found_odd:
        if values[index] % 2 == 1:
            found_odd = True
        index += 1

    print(f"Odd value found: {found_odd}")


# ---------------------------------------------------------------------------
# 6. BREAK
# ---------------------------------------------------------------------------

def find_first(values: list[int], target: int) -> int:
    """Return the first matching index, or -1."""
    index = 0

    while index < len(values):
        if values[index] == target:
            break
        index += 1

    return index if index < len(values) else -1


def example_break() -> None:
    print("\n8. break")

    values = [11, 23, 35, 47, 59]
    print("Index of 35:", find_first(values, 35))
    print("Index of 99:", find_first(values, 99))


# ---------------------------------------------------------------------------
# 7. CONTINUE
# ---------------------------------------------------------------------------

def example_continue() -> None:
    print("\n9. continue")

    number = 0
    while number < 10:
        number += 1

        # Skip even numbers.
        if number % 2 == 0:
            continue

        print(number, end=" ")

    print()


# ---------------------------------------------------------------------------
# 8. WHILE...ELSE
# ---------------------------------------------------------------------------

def contains_value(values: list[int], target: int) -> bool:
    """
    The else block executes when the while condition becomes false normally.
    It does not execute when break terminates the loop.
    """
    index = 0

    while index < len(values):
        if values[index] == target:
            return True
        index += 1
    else:
        return False


def search_with_break_else(values: list[int], target: int) -> None:
    index = 0

    while index < len(values):
        if values[index] == target:
            print(f"Found {target} at index {index}.")
            break
        index += 1
    else:
        print(f"{target} was not found.")


# ---------------------------------------------------------------------------
# 9. NESTED WHILE LOOPS
# ---------------------------------------------------------------------------

def multiplication_table(size: int) -> None:
    print("\n10. Nested while loops")

    row = 1
    while row <= size:
        column = 1

        while column <= size:
            print(f"{row * column:3}", end=" ")
            column += 1

        print()
        row += 1


# ---------------------------------------------------------------------------
# 10. STRING PROCESSING
# ---------------------------------------------------------------------------

def reverse_string_with_while(text: str) -> str:
    index = len(text) - 1
    result: list[str] = []

    while index >= 0:
        result.append(text[index])
        index -= 1

    return "".join(result)


def count_characters(text: str, target: str) -> int:
    count = 0
    index = 0

    while index < len(text):
        if text[index] == target:
            count += 1
        index += 1

    return count


def example_string_processing() -> None:
    print("\n11. String processing")
    text = "while loops"
    print("Original:", text)
    print("Reversed:", reverse_string_with_while(text))
    print("Number of l characters:", count_characters(text, "l"))


# ---------------------------------------------------------------------------
# 11. LIST PROCESSING
# ---------------------------------------------------------------------------

def filter_positive(values: list[int]) -> list[int]:
    result: list[int] = []
    index = 0

    while index < len(values):
        if values[index] > 0:
            result.append(values[index])
        index += 1

    return result


def calculate_statistics(values: list[float]) -> dict[str, float]:
    """Calculate basic statistics without a for loop."""
    if not values:
        raise ValueError("At least one value is required.")

    index = 0
    total = 0.0
    minimum = values[0]
    maximum = values[0]

    while index < len(values):
        value = values[index]
        total += value

        if value < minimum:
            minimum = value

        if value > maximum:
            maximum = value

        index += 1

    return {
        "count": float(len(values)),
        "sum": total,
        "minimum": minimum,
        "maximum": maximum,
        "mean": total / len(values),
    }


# ---------------------------------------------------------------------------
# 12. ITERATORS AND WHILE
# ---------------------------------------------------------------------------

def consume_iterator(iterator: Iterable[int]) -> list[int]:
    """
    while can work directly with an iterator through next().

    StopIteration is the iterator protocol's signal that no values remain.
    """
    iterator_object = iter(iterator)
    result: list[int] = []

    while True:
        try:
            result.append(next(iterator_object))
        except StopIteration:
            break

    return result


# ---------------------------------------------------------------------------
# 13. FACTORIAL
# ---------------------------------------------------------------------------

def factorial(number: int) -> int:
    if number < 0:
        raise ValueError("Factorial is undefined for negative integers.")

    result = 1
    current = 2

    while current <= number:
        result *= current
        current += 1

    return result


# ---------------------------------------------------------------------------
# 14. EUCLIDEAN ALGORITHM
# ---------------------------------------------------------------------------

def greatest_common_divisor(a: int, b: int) -> int:
    """
    Euclid's algorithm repeatedly replaces (a, b) with (b, a % b).

    Time complexity: O(log(min(a, b))) for non-negative integer inputs.
    """
    a = abs(a)
    b = abs(b)

    while b != 0:
        a, b = b, a % b

    return a


# ---------------------------------------------------------------------------
# 15. BINARY SEARCH
# ---------------------------------------------------------------------------

def binary_search(sorted_values: list[int], target: int) -> int:
    """
    Iterative binary search.

    Requires ascending sorted input.
    Time complexity: O(log n).
    Space complexity: O(1), excluding the input.
    """
    low = 0
    high = len(sorted_values) - 1

    while low <= high:
        middle = low + (high - low) // 2
        candidate = sorted_values[middle]

        if candidate == target:
            return middle

        if candidate < target:
            low = middle + 1
        else:
            high = middle - 1

    return -1


# ---------------------------------------------------------------------------
# 16. NEWTON'S METHOD
# ---------------------------------------------------------------------------

def square_root_newton(
    value: float,
    tolerance: float = 1e-12,
    maximum_iterations: int = 100,
) -> float:
    """
    Approximate sqrt(value) using Newton-Raphson iteration.

    x_(n+1) = 0.5 * (x_n + value / x_n)
    """
    if value < 0:
        raise ValueError("Square root requires a non-negative value.")

    if value == 0:
        return 0.0

    estimate = value if value >= 1 else 1.0
    iteration = 0

    while iteration < maximum_iterations:
        next_estimate = 0.5 * (estimate + value / estimate)

        if abs(next_estimate - estimate) <= tolerance:
            return next_estimate

        estimate = next_estimate
        iteration += 1

    raise RuntimeError("Newton iteration did not converge.")


# ---------------------------------------------------------------------------
# 17. PRIME TESTING
# ---------------------------------------------------------------------------

def is_prime(number: int) -> bool:
    """Test primality using trial division up to sqrt(number)."""
    if number < 2:
        return False

    if number == 2:
        return True

    if number % 2 == 0:
        return False

    divisor = 3
    limit = isqrt(number)

    while divisor <= limit:
        if number % divisor == 0:
            return False
        divisor += 2

    return True


def primes_up_to(limit: int) -> list[int]:
    result: list[int] = []
    candidate = 2

    while candidate <= limit:
        if is_prime(candidate):
            result.append(candidate)
        candidate += 1

    return result


# ---------------------------------------------------------------------------
# 18. FIBONACCI
# ---------------------------------------------------------------------------

def fibonacci_terms(count: int) -> list[int]:
    if count < 0:
        raise ValueError("Count cannot be negative.")

    result: list[int] = []
    first, second = 0, 1
    index = 0

    while index < count:
        result.append(first)
        first, second = second, first + second
        index += 1

    return result


# ---------------------------------------------------------------------------
# 19. STATE MACHINE
# ---------------------------------------------------------------------------

@dataclass
class TrafficLight:
    state: str = "RED"
    cycles: int = 0

    TRANSITIONS = {
        "RED": "GREEN",
        "GREEN": "YELLOW",
        "YELLOW": "RED",
    }

    def advance(self) -> None:
        if self.state not in self.TRANSITIONS:
            raise ValueError(f"Unknown traffic state: {self.state}")

        self.state = self.TRANSITIONS[self.state]
        self.cycles += 1


def simulate_traffic_light(cycles: int) -> list[str]:
    if cycles < 0:
        raise ValueError("Cycles cannot be negative.")

    light = TrafficLight()
    states = [light.state]
    completed = 0

    while completed < cycles:
        light.advance()
        states.append(light.state)
        completed += 1

    return states


# ---------------------------------------------------------------------------
# 20. SIMULATION WITH A TERMINATION CONDITION
# ---------------------------------------------------------------------------

def compound_until_target(
    principal: float,
    annual_rate: float,
    target: float,
    periods_per_year: int = 12,
) -> tuple[int, float]:
    """
    Compound interest until a target balance is reached.

    Returns (number_of_periods, resulting_balance).
    """
    if principal <= 0:
        raise ValueError("Principal must be positive.")
    if annual_rate < 0:
        raise ValueError("Rate cannot be negative.")
    if target < principal:
        return 0, principal
    if periods_per_year <= 0:
        raise ValueError("Periods per year must be positive.")

    rate_per_period = annual_rate / periods_per_year
    balance = principal
    periods = 0

    while balance < target:
        previous_balance = balance
        balance *= 1 + rate_per_period
        periods += 1

        # A zero rate cannot reach a larger target.
        if balance == previous_balance:
            raise ValueError("Target cannot be reached at the supplied rate.")

    return periods, balance


# ---------------------------------------------------------------------------
# 21. QUEUE PROCESSING
# ---------------------------------------------------------------------------

def process_queue(tasks: list[str], processor: Callable[[str], str]) -> list[str]:
    """
    Model a queue using an index.

    Removing the first list element repeatedly with pop(0) is O(n) per
    removal. An index avoids that repeated shifting and keeps processing
    linear for this simple queue representation.
    """
    results: list[str] = []
    position = 0

    while position < len(tasks):
        task = tasks[position]
        results.append(processor(task))
        position += 1

    return results


# ---------------------------------------------------------------------------
# 22. RETRY LOGIC
# ---------------------------------------------------------------------------

def retry_operation(
    operation: Callable[[], bool],
    maximum_attempts: int,
) -> bool:
    """
    Retry a boolean operation up to maximum_attempts times.

    This demonstrates a common production pattern: bounded retries.
    """
    if maximum_attempts <= 0:
        raise ValueError("maximum_attempts must be positive.")

    attempt = 1

    while attempt <= maximum_attempts:
        try:
            if operation():
                return True
        except Exception as exc:
            print(f"Attempt {attempt} raised {type(exc).__name__}: {exc}")

        attempt += 1

    return False


# ---------------------------------------------------------------------------
# 23. EDGE CASES
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    print("\n12. Edge cases")

    print("Empty binary search:", binary_search([], 10))
    print("Zero factorial:", factorial(0))
    print("GCD(0, 24):", greatest_common_divisor(0, 24))
    print("GCD(24, 0):", greatest_common_divisor(24, 0))
    print("Fibonacci(0):", fibonacci_terms(0))
    print("Prime test for 1:", is_prime(1))
    print("Prime test for 2:", is_prime(2))
    print("Prime test for 97:", is_prime(97))


# ---------------------------------------------------------------------------
# 24. COMMON INFINITE-LOOP BUGS
# ---------------------------------------------------------------------------

def safe_progress_example(limit: int) -> int:
    """
    A safe loop because progress toward the termination condition is explicit.
    """
    counter = 0

    while counter < limit:
        counter += 1

    return counter


def explain_infinite_loop_risks() -> None:
    print("\n13. Infinite-loop risks")
    print("A while loop can become infinite if its condition never becomes false.")
    print("Typical causes:")
    print("  - forgetting to update a counter")
    print("  - changing the wrong variable")
    print("  - using a condition that can never become false")
    print("  - floating-point progress that never reaches an exact value")
    print("  - external state that never changes")
    print("Safe result:", safe_progress_example(5))


# ---------------------------------------------------------------------------
# 25. FLOATING-POINT TERMINATION
# ---------------------------------------------------------------------------

def floating_point_loop_demo() -> None:
    print("\n14. Floating-point termination")

    value = 0.0
    iterations = 0

    # Do not depend on value == 1.0 as the termination condition.
    # Use a bounded loop or tolerance when working with floating point.
    while value < 1.0 and iterations < 20:
        value += 0.1
        iterations += 1

    print(f"value={value!r}, iterations={iterations}")


# ---------------------------------------------------------------------------
# 26. INPUT PROCESSING WITHOUT TRUSTING INPUT
# ---------------------------------------------------------------------------

def parse_integer_sequence(text: str) -> list[int]:
    """
    Parse comma-separated integers using a while loop.

    Example:
        "10, 20, -5" -> [10, 20, -5]
    """
    pieces = text.split(",")
    numbers: list[int] = []
    index = 0

    while index < len(pieces):
        piece = pieces[index].strip()

        if not piece:
            raise ValueError("Empty value found.")

        try:
            numbers.append(int(piece))
        except ValueError as exc:
            raise ValueError(f"Invalid integer: {piece!r}") from exc

        index += 1

    return numbers


# ---------------------------------------------------------------------------
# 27. PASSWORD-STYLE ATTEMPT CONTROL
# ---------------------------------------------------------------------------

def authenticate(
    supplied_passwords: list[str],
    expected_password: str,
    maximum_attempts: int = 3,
) -> bool:
    """
    Demonstrate bounded authentication attempts.

    Real authentication systems should never store plaintext passwords and
    should use established password hashing and account protection controls.
    """
    if maximum_attempts <= 0:
        return False

    attempt = 0

    while attempt < maximum_attempts and attempt < len(supplied_passwords):
        password = supplied_passwords[attempt]
        attempt += 1

        if password == expected_password:
            return True

    return False


# ---------------------------------------------------------------------------
# 28. RATE-LIMITING STYLE WINDOW
# ---------------------------------------------------------------------------

def allow_requests(
    request_times: list[int],
    window_size: int,
    maximum_requests: int,
) -> list[bool]:
    """
    Simple sliding-window demonstration.

    request_times must be sorted in ascending order.
    """
    if window_size <= 0 or maximum_requests <= 0:
        raise ValueError("Window size and request limit must be positive.")

    decisions: list[bool] = []
    left = 0
    index = 0

    while index < len(request_times):
        current_time = request_times[index]

        while (
            left < index
            and request_times[left] <= current_time - window_size
        ):
            left += 1

        requests_in_window = index - left + 1
        decisions.append(requests_in_window <= maximum_requests)
        index += 1

    return decisions


# ---------------------------------------------------------------------------
# 29. MENU-STYLE STATE CONTROL
# ---------------------------------------------------------------------------

def command_processor(commands: list[str]) -> list[str]:
    """
    Model a command loop without interactive input.

    The command "quit" terminates the loop.
    """
    output: list[str] = []
    position = 0

    while position < len(commands):
        command = commands[position].strip().lower()
        position += 1

        if command == "help":
            output.append("Available: help, status, quit")
            continue

        if command == "status":
            output.append("System status: operational")
            continue

        if command == "quit":
            output.append("Command loop terminated.")
            break

        output.append(f"Unknown command: {command}")

    return output


# ---------------------------------------------------------------------------
# 30. PERFORMANCE COMPARISON
# ---------------------------------------------------------------------------

def sum_with_while(values: list[int]) -> int:
    total = 0
    index = 0

    while index < len(values):
        total += values[index]
        index += 1

    return total


def sum_with_builtin(values: list[int]) -> int:
    return sum(values)


def performance_notes() -> None:
    print("\n15. Performance considerations")
    values = list(range(10_000))
    print("while sum:", sum_with_while(values))
    print("built-in sum:", sum_with_builtin(values))
    print("Both process O(n) data, but Python's built-in sum is implemented in")
    print("optimized interpreter/runtime code and is normally preferable.")


# ---------------------------------------------------------------------------
# 31. TESTING
# ---------------------------------------------------------------------------

def run_tests() -> None:
    """Small assertion-based test suite for the examples."""
    assert factorial(0) == 1
    assert factorial(5) == 120

    assert greatest_common_divisor(48, 18) == 6
    assert greatest_common_divisor(-48, 18) == 6

    assert binary_search([1, 3, 5, 7, 9], 7) == 3
    assert binary_search([1, 3, 5, 7, 9], 8) == -1

    assert fibonacci_terms(6) == [0, 1, 1, 2, 3, 5]

    assert is_prime(2)
    assert is_prime(97)
    assert not is_prime(1)
    assert not is_prime(100)

    assert reverse_string_with_while("abc") == "cba"
    assert count_characters("banana", "a") == 3

    assert parse_integer_sequence("1, 2, -3") == [1, 2, -3]

    assert contains_value([1, 2, 3], 2)
    assert not contains_value([1, 2, 3], 9)

    assert process_queue(["a", "b"], str.upper) == ["A", "B"]

    assert authenticate(["bad", "secret"], "secret", 3)

    print("\nAll assertions passed.")


# ---------------------------------------------------------------------------
# 32. PRACTICAL DEMONSTRATION
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 72)
    print("WHILE LOOPS IN PYTHON: COMPLETE STUDY PROGRAM")
    print("=" * 72)

    example_basic_while()
    example_countdown()
    example_condition_changes()
    example_counter_patterns()

    example_input_validation(["hello", "-5", "42"])
    example_sentinel_loop()
    example_boolean_flag()
    example_break()
    example_continue()

    print("\nwhile...else examples")
    search_with_break_else([10, 20, 30], 20)
    search_with_break_else([10, 20, 30], 99)

    multiplication_table(4)
    example_string_processing()

    print("\n16. Data processing")
    numbers = [-5, 0, 3, 8, -2, 10]
    print("Positive values:", filter_positive(numbers))
    print("Statistics:", calculate_statistics([10, 20, 30, 40]))

    print("\n17. Iterator processing")
    print("Iterator result:", consume_iterator([2, 4, 6, 8]))

    print("\n18. Algorithms")
    print("5! =", factorial(5))
    print("GCD(84, 30) =", greatest_common_divisor(84, 30))
    print("Binary search index:", binary_search([2, 4, 6, 8, 10, 12], 8))
    print("sqrt(2) approximation:", square_root_newton(2))
    print("Primes through 30:", primes_up_to(30))
    print("First 10 Fibonacci terms:", fibonacci_terms(10))

    print("\n19. State machine")
    print("Traffic states:", simulate_traffic_light(6))

    print("\n20. Compound simulation")
    periods, balance = compound_until_target(1000, 0.12, 1500)
    print(f"Reached target after {periods} monthly periods: {balance:.2f}")

    print("\n21. Queue processing")
    print(process_queue(["compile", "test", "package"], str.upper))

    print("\n22. Retry logic")
    attempts = {"count": 0}

    def simulated_operation() -> bool:
        attempts["count"] += 1
        return attempts["count"] >= 3

    print("Retry result:", retry_operation(simulated_operation, 5))

    demonstrate_edge_cases()
    explain_infinite_loop_risks()
    floating_point_loop_demo()

    print("\n23. Parsing")
    print(parse_integer_sequence("10, 20, -5, 40"))

    print("\n24. Bounded authentication")
    print(
        "Authentication:",
        authenticate(["incorrect", "wrong", "correct"], "correct", 3),
    )

    print("\n25. Sliding-window decisions")
    request_times = [0, 1, 2, 3, 7, 8]
    print(allow_requests(request_times, window_size=5, maximum_requests=3))

    print("\n26. Command processor")
    for message in command_processor(["help", "status", "unknown", "quit", "status"]):
        print(message)

    performance_notes()
    run_tests()

    print("\nStudy principles:")
    print("1. A while loop repeats while its condition evaluates to True.")
    print("2. The condition is evaluated before each iteration.")
    print("3. Loop state should move deliberately toward termination.")
    print("4. break exits the nearest loop immediately.")
    print("5. continue skips the remainder of the current iteration.")
    print("6. while...else executes else only after normal loop termination.")
    print("7. Bounded loops are easier to reason about than uncontrolled loops.")
    print("8. Use tolerance or iteration bounds for floating-point algorithms.")
    print("9. Validate external input before using it as loop state.")
    print("10. Choose while when termination depends naturally on changing state.")


if __name__ == "__main__":
    main()
