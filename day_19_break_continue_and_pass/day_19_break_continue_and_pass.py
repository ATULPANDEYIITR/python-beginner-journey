"""
break, continue, and pass in Python
===================================

A self-contained study program covering:
- The meaning and syntax of break, continue, and pass
- for and while loops
- Loop control flow
- Nested loops
- else clauses on loops
- Validation and sentinel loops
- Search and filtering patterns
- Exception handling
- Functions containing loop-control statements
- Classes and methods
- Generator-related considerations
- Common mistakes
- Performance and design considerations
- Practical simulations and algorithms
- Tests and demonstrations

Important terminology:
    break     -> terminates the nearest enclosing loop immediately.
    continue  -> skips the rest of the current iteration and starts the next one.
    pass      -> performs no operation; execution continues normally.

These are statements, not functions. They are commonly described informally as
"loop control statements" or "control-flow statements."
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator


# ---------------------------------------------------------------------------
# Utility functions used throughout the demonstrations
# ---------------------------------------------------------------------------

def section(title: str) -> None:
    """Print a visually separated study section."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def show_result(label: str, value: object) -> None:
    """Print a labeled result."""
    print(f"{label}: {value}")


# ---------------------------------------------------------------------------
# 1. FUNDAMENTALS
# ---------------------------------------------------------------------------

def demonstrate_basic_break() -> None:
    section("1. Basic break")

    print("Numbers before break:", end=" ")
    for number in range(1, 11):
        if number == 6:
            break
        print(number, end=" ")
    print()

    # When number becomes 6, break immediately terminates the for loop.
    # Values 6 through 10 are therefore never processed.


def demonstrate_basic_continue() -> None:
    section("2. Basic continue")

    print("Odd numbers:", end=" ")
    for number in range(1, 11):
        if number % 2 == 0:
            continue
        print(number, end=" ")
    print()

    # continue does not terminate the loop.
    # It skips the remaining statements in the current iteration.


def demonstrate_basic_pass() -> None:
    section("3. Basic pass")

    for number in range(1, 6):
        if number == 3:
            pass  # Intentionally do nothing.
        print(number, end=" ")
    print()

    # pass is different from continue.
    # With pass, execution continues with the next statement in the same
    # iteration. The print statement therefore still executes for number 3.


# ---------------------------------------------------------------------------
# 2. DIRECT COMPARISON
# ---------------------------------------------------------------------------

def demonstrate_comparison() -> None:
    section("4. break vs continue vs pass")

    print("break:")
    for number in range(1, 6):
        if number == 3:
            break
        print(f"  processed {number}")

    print("continue:")
    for number in range(1, 6):
        if number == 3:
            continue
        print(f"  processed {number}")

    print("pass:")
    for number in range(1, 6):
        if number == 3:
            pass
        print(f"  processed {number}")


# ---------------------------------------------------------------------------
# 3. FOR LOOPS
# ---------------------------------------------------------------------------

def demonstrate_for_loop_patterns() -> None:
    section("5. for-loop patterns")

    # Search for the first matching value.
    values = [14, 27, 35, 42, 51, 64]

    first_multiple_of_7 = None
    for value in values:
        if value % 7 == 0:
            first_multiple_of_7 = value
            break

    show_result("First multiple of 7", first_multiple_of_7)

    # Filter values using continue.
    positive_values = []
    mixed_values = [-4, 8, 0, 12, -7, 15]

    for value in mixed_values:
        if value <= 0:
            continue
        positive_values.append(value)

    show_result("Positive values", positive_values)

    # pass is useful while a branch is intentionally empty.
    for value in values:
        if value < 0:
            pass
        else:
            print(f"Non-negative value: {value}")


# ---------------------------------------------------------------------------
# 4. WHILE LOOPS
# ---------------------------------------------------------------------------

def demonstrate_while_loops() -> None:
    section("6. while-loop patterns")

    counter = 0
    while counter < 10:
        counter += 1

        if counter == 7:
            break

        print(counter, end=" ")
    print()

    counter = 0
    print("Skipping multiples of three:", end=" ")
    while counter < 10:
        counter += 1

        if counter % 3 == 0:
            continue

        print(counter, end=" ")
    print()

    # A pass statement does not change the loop condition.
    counter = 0
    while counter < 3:
        if counter == 1:
            pass
        print(f"counter={counter}")
        counter += 1


# ---------------------------------------------------------------------------
# 5. LOOP ELSE
# ---------------------------------------------------------------------------

def demonstrate_loop_else() -> None:
    section("7. for/while else with break")

    numbers = [11, 15, 22, 31, 45]

    for number in numbers:
        if number % 2 == 0:
            print(f"Found an even number: {number}")
            break
    else:
        print("No even number was found.")

    # Because 22 is found, break executes and the loop's else clause does not.

    numbers_without_even = [11, 15, 31, 45]

    for number in numbers_without_even:
        if number % 2 == 0:
            print(f"Found an even number: {number}")
            break
    else:
        print("No even number was found.")

    # A loop else executes when the loop finishes normally.
    # It does not mean "else if the condition is false."
    # A break prevents the loop else from executing.


def is_prime(number: int) -> bool:
    """Return True if number is prime using for/else."""
    if number < 2:
        return False

    for divisor in range(2, int(number ** 0.5) + 1):
        if number % divisor == 0:
            break
    else:
        return True

    return False


# ---------------------------------------------------------------------------
# 6. NESTED LOOPS
# ---------------------------------------------------------------------------

def demonstrate_nested_break() -> None:
    section("8. Nested loops")

    print("Nested break:")
    for outer in range(1, 4):
        for inner in range(1, 5):
            if inner == 3:
                break
            print(f"outer={outer}, inner={inner}")

    # break affects only the nearest enclosing loop.
    # It does not automatically terminate every surrounding loop.

    print("Nested continue:")
    for outer in range(1, 3):
        for inner in range(1, 5):
            if inner == 2:
                continue
            print(f"outer={outer}, inner={inner}")

    print("Nested pass:")
    for outer in range(1, 3):
        for inner in range(1, 4):
            if inner == 2:
                pass
            print(f"outer={outer}, inner={inner}")


def find_coordinate(
    matrix: list[list[int]],
    target: int,
) -> tuple[int, int] | None:
    """Find target in a matrix using a flag to leave nested loops."""
    found_position: tuple[int, int] | None = None

    for row_index, row in enumerate(matrix):
        for column_index, value in enumerate(row):
            if value == target:
                found_position = (row_index, column_index)
                break

        if found_position is not None:
            break

    return found_position


# ---------------------------------------------------------------------------
# 7. PRACTICAL SEARCH
# ---------------------------------------------------------------------------

def linear_search_first(
    values: Iterable[int],
    target: int,
) -> int | None:
    """Return the first matching value or None."""
    for value in values:
        if value == target:
            break
    else:
        return None

    return value


def demonstrate_search() -> None:
    section("9. Search algorithms")

    data = [8, 19, 4, 27, 31, 42, 55]

    show_result("Search for 27", linear_search_first(data, 27))
    show_result("Search for 99", linear_search_first(data, 99))

    # Once the target is found, continuing to inspect values is unnecessary.
    # break therefore avoids unnecessary work.


# ---------------------------------------------------------------------------
# 8. FILTERING AND VALIDATION
# ---------------------------------------------------------------------------

def filter_valid_scores(scores: Iterable[object]) -> list[int]:
    """
    Keep valid integer scores from 0 through 100.

    Invalid values are skipped with continue.
    """
    valid_scores: list[int] = []

    for score in scores:
        if not isinstance(score, int) or isinstance(score, bool):
            continue

        if not 0 <= score <= 100:
            continue

        valid_scores.append(score)

    return valid_scores


def demonstrate_validation() -> None:
    section("10. Validation with continue")

    raw_scores: list[object] = [85, -3, 92, "90", 101, 77, None, 64]
    valid_scores = filter_valid_scores(raw_scores)

    show_result("Input scores", raw_scores)
    show_result("Valid scores", valid_scores)


# ---------------------------------------------------------------------------
# 9. SENTINEL-STYLE PROCESSING
# ---------------------------------------------------------------------------

def process_transactions(
    transactions: Iterable[dict[str, object]],
) -> tuple[float, int]:
    """
    Process transaction records.

    - Invalid records are skipped.
    - A transaction with type 'STOP' terminates processing.
    """
    total = 0.0
    processed_count = 0

    for transaction in transactions:
        transaction_type = transaction.get("type")

        if transaction_type == "STOP":
            break

        amount = transaction.get("amount")

        if transaction_type != "SALE":
            continue

        if not isinstance(amount, (int, float)):
            continue

        if amount < 0:
            continue

        total += float(amount)
        processed_count += 1

    return total, processed_count


def demonstrate_transactions() -> None:
    section("11. Transaction processing")

    transactions = [
        {"type": "SALE", "amount": 120.50},
        {"type": "REFUND", "amount": 20},
        {"type": "SALE", "amount": 75},
        {"type": "SALE", "amount": -10},
        {"type": "SALE", "amount": 200},
        {"type": "STOP"},
        {"type": "SALE", "amount": 9999},
    ]

    total, count = process_transactions(transactions)
    show_result("Processed sales", count)
    show_result("Sales total", total)


# ---------------------------------------------------------------------------
# 10. USER-INPUT STYLE VALIDATION WITHOUT ACTUAL INTERACTIVE INPUT
# ---------------------------------------------------------------------------

def validate_command(command: str) -> str:
    """
    Validate a command using continue-like logic represented through
    early iteration in a processing loop.
    """
    normalized = command.strip().lower()

    valid_commands = {"start", "stop", "status", "help"}

    if not normalized:
        return "empty"

    if normalized not in valid_commands:
        return "invalid"

    return normalized


def demonstrate_command_validation() -> None:
    section("12. Command validation")

    commands = ["", "launch", "status", " START ", "stop", "unknown"]

    for command in commands:
        result = validate_command(command)

        if result == "empty":
            continue

        if result == "invalid":
            print(f"Ignored invalid command: {command!r}")
            continue

        print(f"Accepted command: {result}")


# ---------------------------------------------------------------------------
# 11. EXCEPTIONS AND LOOP CONTROL
# ---------------------------------------------------------------------------

def parse_positive_integers(
    values: Iterable[str],
) -> list[int]:
    """Convert valid positive integer strings and skip invalid entries."""
    numbers: list[int] = []

    for text in values:
        try:
            number = int(text)
        except ValueError:
            continue

        if number <= 0:
            continue

        numbers.append(number)

    return numbers


def demonstrate_exceptions() -> None:
    section("13. Exception handling with continue")

    inputs = ["10", "abc", "25", "-7", "42", "3.14", "100"]
    parsed = parse_positive_integers(inputs)

    show_result("Input", inputs)
    show_result("Positive integers", parsed)


# ---------------------------------------------------------------------------
# 12. BREAK IN EXCEPTION-DRIVEN PROCESSING
# ---------------------------------------------------------------------------

def first_successful_conversion(values: Iterable[str]) -> int | None:
    """
    Return the first successfully converted positive integer.

    Invalid input is skipped.
    The first acceptable value causes break.
    """
    result: int | None = None

    for text in values:
        try:
            number = int(text)
        except ValueError:
            continue

        if number <= 0:
            continue

        result = number
        break

    return result


# ---------------------------------------------------------------------------
# 13. PASS AS A PLACEHOLDER
# ---------------------------------------------------------------------------

class ExperimentalFeature:
    """
    pass can temporarily define a class body.

    A class body cannot be completely empty. pass provides a valid statement
    while the class has no implementation.
    """

    pass


def demonstrate_pass_use_cases() -> None:
    section("14. Appropriate uses of pass")

    # Empty class.
    feature = ExperimentalFeature()
    show_result("Empty class instance", type(feature).__name__)

    # Empty exception branch.
    values = [1, 2, 3]
    for value in values:
        if value < 0:
            pass
        else:
            print(f"Accepted value: {value}")

    # pass is also useful during staged development, although production code
    # should replace intentional placeholders with meaningful implementation
    # when the behavior becomes known.


# ---------------------------------------------------------------------------
# 14. PASS VS CONTINUE
# ---------------------------------------------------------------------------

def demonstrate_pass_vs_continue() -> None:
    section("15. pass versus continue")

    print("Using pass:")
    for number in range(1, 5):
        if number == 2:
            pass
        print(f"  after conditional: {number}")

    print("Using continue:")
    for number in range(1, 5):
        if number == 2:
            continue
        print(f"  after conditional: {number}")

    # With pass:
    #   condition -> pass -> following statement executes.
    #
    # With continue:
    #   condition -> current iteration ends -> next iteration begins.


# ---------------------------------------------------------------------------
# 15. PASS VS BREAK
# ---------------------------------------------------------------------------

def demonstrate_pass_vs_break() -> None:
    section("16. pass versus break")

    print("pass:")
    for number in range(1, 5):
        if number == 2:
            pass
        print(number, end=" ")
    print()

    print("break:")
    for number in range(1, 5):
        if number == 2:
            break
        print(number, end=" ")
    print()


# ---------------------------------------------------------------------------
# 16. CONTROL FLOW VISUALIZATION
# ---------------------------------------------------------------------------

def control_flow_demo() -> None:
    section("17. Control-flow trace")

    events: list[str] = []

    for number in range(1, 6):
        events.append(f"start:{number}")

        if number == 2:
            events.append("continue")
            continue

        if number == 4:
            events.append("break")
            break

        events.append(f"end:{number}")

    for event in events:
        print(event)

    # The trace demonstrates:
    # 1 -> start and end
    # 2 -> start and continue, so end is skipped
    # 3 -> start and end
    # 4 -> start and break, so end is skipped and the loop terminates
    # 5 -> never reached


# ---------------------------------------------------------------------------
# 17. LOOP CONTROL INSIDE FUNCTIONS
# ---------------------------------------------------------------------------

def find_first_negative(values: Iterable[int]) -> int | None:
    for value in values:
        if value < 0:
            return value
    return None


def skip_negative_values(values: Iterable[int]) -> list[int]:
    result: list[int] = []

    for value in values:
        if value < 0:
            continue
        result.append(value)

    return result


def demonstrate_functions() -> None:
    section("18. Functions containing loop-control statements")

    values = [5, 8, 11, -4, 20]

    show_result("First negative", find_first_negative(values))
    show_result("Non-negative values", skip_negative_values(values))

    # A return exits the entire function.
    # A break exits only the nearest loop.
    # A continue exits only the current loop iteration.


# ---------------------------------------------------------------------------
# 18. SEARCHING A MATRIX
# ---------------------------------------------------------------------------

def demonstrate_matrix_search() -> None:
    section("19. Matrix search")

    matrix = [
        [4, 8, 12],
        [16, 20, 24],
        [28, 32, 36],
    ]

    show_result("Position of 24", find_coordinate(matrix, 24))
    show_result("Position of 99", find_coordinate(matrix, 99))


# ---------------------------------------------------------------------------
# 19. MULTIPLE CONDITIONS
# ---------------------------------------------------------------------------

def classify_numbers(values: Iterable[int]) -> dict[str, list[int]]:
    """
    Demonstrate careful ordering of continue conditions.

    Multiples of ten are placed in a separate category.
    Negative values are ignored.
    Even and odd positive values are categorized.
    """
    result = {
        "multiples_of_ten": [],
        "even": [],
        "odd": [],
    }

    for value in values:
        if value < 0:
            continue

        if value % 10 == 0:
            result["multiples_of_ten"].append(value)
            continue

        if value % 2 == 0:
            result["even"].append(value)
            continue

        result["odd"].append(value)

    return result


# ---------------------------------------------------------------------------
# 20. REAL-WORLD RECORD PROCESSING
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Employee:
    name: str
    department: str
    salary: float
    active: bool


def calculate_department_payroll(
    employees: Iterable[Employee],
    department: str,
) -> float:
    """Calculate payroll for active employees in one department."""
    payroll = 0.0

    for employee in employees:
        if not employee.active:
            continue

        if employee.department != department:
            continue

        if employee.salary < 0:
            continue

        payroll += employee.salary

    return payroll


def demonstrate_employee_processing() -> None:
    section("20. Real-world employee processing")

    employees = [
        Employee("Asha", "Engineering", 90000, True),
        Employee("Rahul", "Sales", 70000, True),
        Employee("Mira", "Engineering", 95000, False),
        Employee("Vikram", "Engineering", 110000, True),
        Employee("Neha", "HR", 60000, True),
    ]

    payroll = calculate_department_payroll(employees, "Engineering")
    show_result("Active Engineering payroll", payroll)


# ---------------------------------------------------------------------------
# 21. BREAK AND ALGORITHM COMPLEXITY
# ---------------------------------------------------------------------------

def contains_duplicate(values: list[int]) -> bool:
    """
    Return True at the first duplicate.

    Worst-case time: O(n^2) for this educational implementation.
    Space: O(1) beyond the input list.

    A set-based implementation is usually preferable for large datasets.
    """
    for first_index in range(len(values)):
        for second_index in range(first_index + 1, len(values)):
            if values[first_index] == values[second_index]:
                return True

    return False


def contains_duplicate_with_break(values: list[int]) -> bool:
    """Equivalent nested-loop demonstration using break."""
    duplicate_found = False

    for first_index in range(len(values)):
        for second_index in range(first_index + 1, len(values)):
            if values[first_index] == values[second_index]:
                duplicate_found = True
                break

        if duplicate_found:
            break

    return duplicate_found


def contains_duplicate_fast(values: Iterable[int]) -> bool:
    """
    Average O(n) time and O(n) auxiliary space using a set.
    """
    seen: set[int] = set()

    for value in values:
        if value in seen:
            return True
        seen.add(value)

    return False


# ---------------------------------------------------------------------------
# 22. PERFORMANCE CONSIDERATIONS
# ---------------------------------------------------------------------------

def benchmark_style_examples() -> None:
    section("21. Performance considerations")

    values = list(range(10_000))

    # This returns as soon as the target is found.
    result = linear_search_first(values, 1)
    show_result("Early search result", result)

    # Searching for a value near the end requires more iterations.
    result = linear_search_first(values, 9_999)
    show_result("Late search result", result)

    # break is not itself a performance optimization in every program.
    # It is useful when further work is unnecessary.
    #
    # continue can reduce work within an iteration by skipping the remaining
    # statements for records that are known to be irrelevant.


# ---------------------------------------------------------------------------
# 23. COMMON MISTAKE: INFINITE WHILE LOOPS
# ---------------------------------------------------------------------------

def demonstrate_safe_while() -> None:
    section("22. Safe while-loop control")

    attempts = 0
    maximum_attempts = 5

    while True:
        attempts += 1

        if attempts >= maximum_attempts:
            break

    show_result("Attempts", attempts)

    # The loop has a clear termination condition.
    # A while True loop should normally contain a reachable break or another
    # explicit termination mechanism.


# ---------------------------------------------------------------------------
# 24. COMMON MISTAKE: CONTINUE BEFORE STATE UPDATE
# ---------------------------------------------------------------------------

def demonstrate_continue_state_update() -> None:
    section("23. continue and state updates")

    counter = 0

    while counter < 5:
        counter += 1

        if counter == 3:
            continue

        print(f"Processed {counter}")

    # The counter is updated before continue.
    # If the update occurred only after continue, the loop could become
    # infinite when counter reached 3.


# ---------------------------------------------------------------------------
# 25. MULTI-LEVEL EXIT PATTERNS
# ---------------------------------------------------------------------------

def find_value_in_matrix(
    matrix: list[list[int]],
    target: int,
) -> tuple[int, int] | None:
    """
    A practical two-level break pattern.

    A flag is used because break only exits the nearest loop.
    """
    result: tuple[int, int] | None = None

    for row_index, row in enumerate(matrix):
        for column_index, value in enumerate(row):
            if value == target:
                result = (row_index, column_index)
                break

        if result is not None:
            break

    return result


def demonstrate_multilevel_exit() -> None:
    section("24. Exiting nested loops")

    matrix = [
        [10, 20, 30],
        [40, 50, 60],
        [70, 80, 90],
    ]

    show_result("Target position", find_value_in_matrix(matrix, 80))

    # Alternatives to a flag include:
    # - return from a function
    # - raising a deliberately designed exception in specialized situations
    # - restructuring the algorithm
    #
    # A flag is often simple and explicit for a small nested search.


# ---------------------------------------------------------------------------
# 26. GENERATORS
# ---------------------------------------------------------------------------

def positive_values(values: Iterable[int]) -> Iterator[int]:
    """
    Generator using continue.

    yield pauses the generator; continue skips to the next iteration.
    """
    for value in values:
        if value <= 0:
            continue
        yield value


def first_large_value(values: Iterable[int], minimum: int) -> int | None:
    """
    Demonstrate break while consuming an iterable lazily.
    """
    for value in values:
        if value < minimum:
            continue

        return value

    return None


def demonstrate_generators() -> None:
    section("25. Generators")

    generator = positive_values([-5, 2, 0, 8, -1, 12])
    show_result("Generated positives", list(generator))

    show_result(
        "First value >= 10",
        first_large_value(range(20), 10),
    )

    # Lazy iteration means values do not have to be stored in a list first.
    # A break/return can stop consumption before the entire iterable is read.


# ---------------------------------------------------------------------------
# 27. ASYNC CONTEXT
# ---------------------------------------------------------------------------

async def asynchronous_processing_example() -> list[int]:
    """
    This function intentionally avoids external dependencies.

    The loop-control semantics of break and continue do not fundamentally
    change in an async for loop. The source of values may simply be asynchronous.
    """
    values = [1, 2, 3, 4, 5]
    accepted: list[int] = []

    for value in values:
        if value == 2:
            continue

        if value == 5:
            break

        accepted.append(value)

    return accepted


# ---------------------------------------------------------------------------
# 28. PASS IN EXCEPTION AND ABSTRACT DESIGN CONTEXTS
# ---------------------------------------------------------------------------

class Parser:
    """A concrete placeholder class for demonstration purposes."""

    def parse(self, text: str) -> str:
        if not text.strip():
            pass  # Explicitly choose not to reject empty input here.
        return text.strip()


def demonstrate_parser() -> None:
    section("26. pass in a class method")

    parser = Parser()
    show_result("Parsed text", parser.parse("  example  "))


# ---------------------------------------------------------------------------
# 29. WHEN NOT TO USE PASS
# ---------------------------------------------------------------------------

def demonstrate_unnecessary_pass() -> None:
    section("27. Avoiding unnecessary pass")

    # Unnecessary:
    for number in range(3):
        if number >= 0:
            pass
        print(number)

    # Cleaner:
    for number in range(3):
        print(number)

    # pass should communicate intentional inactivity, not be inserted merely
    # because the author is uncertain about the syntax.


# ---------------------------------------------------------------------------
# 30. CONTROL-FLOW TESTS
# ---------------------------------------------------------------------------

def test_break() -> None:
    result: list[int] = []

    for number in range(5):
        if number == 3:
            break
        result.append(number)

    assert result == [0, 1, 2]


def test_continue() -> None:
    result: list[int] = []

    for number in range(5):
        if number == 3:
            continue
        result.append(number)

    assert result == [0, 1, 2, 4]


def test_pass() -> None:
    result: list[int] = []

    for number in range(3):
        if number == 1:
            pass
        result.append(number)

    assert result == [0, 1, 2]


def test_loop_else_with_break() -> None:
    found = False

    for number in range(5):
        if number == 2:
            found = True
            break

    assert found is True


def run_tests() -> None:
    section("28. Assertions and tests")

    test_break()
    test_continue()
    test_pass()
    test_loop_else_with_break()

    print("All control-flow assertions passed.")


# ---------------------------------------------------------------------------
# 31. ADVANCED CASE STUDY: LOG PROCESSING
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LogRecord:
    level: str
    service: str
    message: str


def analyze_logs(
    records: Iterable[LogRecord],
) -> dict[str, int]:
    """
    Analyze log records.

    Rules:
    - DEBUG records are ignored.
    - Empty messages are ignored.
    - ERROR records are counted.
    - CRITICAL terminates processing because the example models an emergency
      shutdown boundary.
    """
    counts = {
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
        "CRITICAL": 0,
    }

    for record in records:
        level = record.level.upper()

        if level == "CRITICAL":
            counts["CRITICAL"] += 1
            break

        if level == "DEBUG":
            continue

        if not record.message.strip():
            continue

        if level not in counts:
            continue

        counts[level] += 1

    return counts


def demonstrate_log_analysis() -> None:
    section("29. Log-processing case study")

    records = [
        LogRecord("INFO", "api", "Request received"),
        LogRecord("DEBUG", "api", "Internal value"),
        LogRecord("WARNING", "api", "High latency"),
        LogRecord("ERROR", "database", "Connection failed"),
        LogRecord("INFO", "worker", ""),
        LogRecord("CRITICAL", "database", "Database unavailable"),
        LogRecord("ERROR", "api", "This record is after the boundary"),
    ]

    show_result("Log counts", analyze_logs(records))


# ---------------------------------------------------------------------------
# 32. EDGE CASES
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    section("30. Edge cases")

    # break inside an empty loop body is syntactically valid only if the body
    # contains a statement. pass can supply that statement.
    for _ in []:
        pass

    # continue in a loop that never iterates simply never executes.
    for _ in []:
        continue

    # A break at the first iteration terminates immediately.
    for number in range(5):
        if number == 0:
            break

    # A continue at every iteration results in no body output.
    for number in range(3):
        if number >= 0:
            continue
        print(number)

    print("Edge cases completed.")


# ---------------------------------------------------------------------------
# 33. SYNTAX AND SEMANTIC RULES
# ---------------------------------------------------------------------------

def demonstrate_rules() -> None:
    section("31. Important language rules")

    print("Rule: break requires an enclosing loop.")
    print("Rule: continue requires an enclosing loop.")
    print("Rule: pass does not require a loop.")

    # The following examples are intentionally NOT executed because they would
    # cause SyntaxError at compile time:
    #
    # break
    # continue
    #
    # Both are only valid inside loops.

    # pass is legal anywhere a statement is syntactically required:
    if True:
        pass

    def intentionally_empty_function() -> None:
        pass

    intentionally_empty_function()


# ---------------------------------------------------------------------------
# 34. RELATED CONTROL-FLOW OPERATIONS
# ---------------------------------------------------------------------------

def compare_return_raise_break_continue() -> None:
    section("32. Related control-flow operations")

    def example_return() -> str:
        for number in range(5):
            if number == 2:
                return "return exits the function"
        return "loop completed"

    show_result("return", example_return())

    def example_break() -> str:
        for number in range(5):
            if number == 2:
                break
        return "function continues after the loop"

    show_result("break", example_break())

    def example_continue() -> list[int]:
        values = []
        for number in range(5):
            if number == 2:
                continue
            values.append(number)
        return values

    show_result("continue", example_continue())

    def example_raise() -> None:
        try:
            raise ValueError("demonstration")
        except ValueError:
            print("raise transfers control to exception handling")


    example_raise()


# ---------------------------------------------------------------------------
# 35. BEST-PRACTICE DEMONSTRATIONS
# ---------------------------------------------------------------------------

def best_practice_examples() -> None:
    section("33. Best-practice patterns")

    # Prefer direct conditions over deeply nested branches.
    values = [4, -2, 8, -1, 10]

    positive_even = []
    for value in values:
        if value <= 0:
            continue
        if value % 2 != 0:
            continue
        positive_even.append(value)

    show_result("Positive even values", positive_even)

    # Use break when the algorithm genuinely has a stopping condition.
    target = 8
    found = False

    for value in values:
        if value == target:
            found = True
            break

    show_result("Target found", found)

    # Use pass only when intentionally doing nothing.
    class Configuration:
        pass

    show_result("Configuration class", Configuration.__name__)


# ---------------------------------------------------------------------------
# 36. COMPLETE PRACTICAL PIPELINE
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SensorReading:
    sensor_id: str
    temperature: float | None
    active: bool


def analyze_sensor_readings(
    readings: Iterable[SensorReading],
    warning_threshold: float,
    critical_threshold: float,
) -> dict[str, object]:
    """
    Analyze sensor readings.

    continue:
        - ignores inactive sensors
        - ignores missing measurements

    break:
        - stops processing when a critical temperature is detected

    pass:
        - demonstrates an intentional no-op branch for an ordinary reading.
    """
    valid_readings: list[float] = []
    critical_sensor: str | None = None

    for reading in readings:
        if not reading.active:
            continue

        if reading.temperature is None:
            continue

        temperature = reading.temperature
        valid_readings.append(temperature)

        if temperature >= critical_threshold:
            critical_sensor = reading.sensor_id
            break

        if temperature >= warning_threshold:
            print(
                f"Warning: {reading.sensor_id} temperature "
                f"{temperature:.1f}"
            )
            continue

        # Ordinary readings need no special action.
        pass

    return {
        "processed_readings": len(valid_readings),
        "critical_sensor": critical_sensor,
        "maximum_temperature": (
            max(valid_readings) if valid_readings else None
        ),
    }


def demonstrate_sensor_pipeline() -> None:
    section("34. Practical sensor pipeline")

    readings = [
        SensorReading("S-01", 21.5, True),
        SensorReading("S-02", None, True),
        SensorReading("S-03", 29.0, False),
        SensorReading("S-04", 35.0, True),
        SensorReading("S-05", 90.0, True),
    ]

    result = analyze_sensor_readings(
        readings,
        warning_threshold=30.0,
        critical_threshold=80.0,
    )

    show_result("Sensor analysis", result)


# ---------------------------------------------------------------------------
# 37. STUDY TABLE
# ---------------------------------------------------------------------------

def print_concept_table() -> None:
    section("35. Concept table")

    rows = [
        ("break", "Exit nearest loop", "Stop searching after target is found"),
        (
            "continue",
            "Skip current iteration",
            "Ignore invalid or irrelevant records",
        ),
        (
            "pass",
            "Do nothing",
            "Create an intentional empty block",
        ),
    ]

    for keyword, action, example in rows:
        print(f"{keyword:10} | {action:22} | {example}")


# ---------------------------------------------------------------------------
# 38. MAIN PROGRAM
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the complete study program."""
    demonstrate_basic_break()
    demonstrate_basic_continue()
    demonstrate_basic_pass()
    demonstrate_comparison()
    demonstrate_for_loop_patterns()
    demonstrate_while_loops()
    demonstrate_loop_else()
    demonstrate_nested_break()
    demonstrate_search()
    demonstrate_validation()
    demonstrate_transactions()
    demonstrate_command_validation()
    demonstrate_exceptions()

    show_result(
        "First successful positive conversion",
        first_successful_conversion(["x", "-4", "0", "19", "27"]),
    )

    demonstrate_pass_use_cases()
    demonstrate_pass_vs_continue()
    demonstrate_pass_vs_break()
    control_flow_demo()
    demonstrate_functions()
    demonstrate_matrix_search()

    show_result(
        "Number classification",
        classify_numbers([-4, 5, 8, 10, 11, 20]),
    )

    demonstrate_employee_processing()

    show_result(
        "Duplicate exists",
        contains_duplicate([1, 2, 3, 2]),
    )
    show_result(
        "Duplicate with break",
        contains_duplicate_with_break([1, 2, 3, 4]),
    )
    show_result(
        "Fast duplicate detection",
        contains_duplicate_fast([1, 7, 3, 9, 7]),
    )

    benchmark_style_examples()
    demonstrate_safe_while()
    demonstrate_continue_state_update()
    demonstrate_multilevel_exit()
    demonstrate_generators()
    demonstrate_parser()
    demonstrate_unnecessary_pass()
    demonstrate_log_analysis()
    demonstrate_edge_cases()
    demonstrate_rules()
    compare_return_raise_break_continue()
    best_practice_examples()
    demonstrate_sensor_pipeline()
    print_concept_table()
    run_tests()

    section("36. End of study program")
    print("All demonstrations completed successfully.")


if __name__ == "__main__":
    main()
