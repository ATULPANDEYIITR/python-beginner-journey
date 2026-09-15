"""
Comprehensive study of Python if, elif, and else.

This file progresses from absolute beginner concepts to advanced decision-making
patterns, validation, nested conditions, Boolean logic, conditional expressions,
guard clauses, structural alternatives, testing, debugging, performance, and
security-oriented validation.

Run with:
    python if_elif_else.py
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, Optional


# =============================================================================
# 1. FUNDAMENTALS
# =============================================================================

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def example_01_basic_if() -> None:
    section("1. Basic if statement")

    age = 20

    # The indented block executes only when the condition is truthy.
    if age >= 18:
        print("The person is an adult.")

    # If age were below 18, nothing would be printed by this if statement.


def example_02_if_else() -> None:
    section("2. if and else")

    age = 16

    if age >= 18:
        print("Adult")
    else:
        print("Minor")

    # Exactly one branch executes in an if/else structure.


def example_03_if_elif_else() -> None:
    section("3. if, elif, and else")

    marks = 76

    if marks >= 90:
        grade = "A+"
    elif marks >= 80:
        grade = "A"
    elif marks >= 70:
        grade = "B"
    elif marks >= 60:
        grade = "C"
    elif marks >= 50:
        grade = "D"
    else:
        grade = "F"

    print("Grade:", grade)

    # Conditions are evaluated from top to bottom.
    # Once one condition is true, the remaining elif/else branches are skipped.
    #
    # Order matters:
    #   if marks >= 50:
    #       ...
    #   elif marks >= 90:
    #       ...
    #
    # The second condition would never be reached for marks >= 90.


def example_04_comparison_operators() -> None:
    section("4. Comparison operators")

    a = 10
    b = 20

    print("a == b:", a == b)
    print("a != b:", a != b)
    print("a < b:", a < b)
    print("a <= b:", a <= b)
    print("a > b:", a > b)
    print("a >= b:", a >= b)

    if a < b:
        print("a is smaller than b")


def example_05_boolean_operators() -> None:
    section("5. Boolean operators: and, or, not")

    age = 25
    has_id = True

    # "and" requires both conditions to be true.
    if age >= 18 and has_id:
        print("Entry permitted.")

    temperature = 39
    raining = False

    # "or" requires at least one condition to be true.
    if temperature > 40 or raining:
        print("Carry appropriate protection.")

    # "not" reverses a Boolean value.
    account_locked = False

    if not account_locked:
        print("Account is available.")


def example_06_truthiness() -> None:
    section("6. Truthiness")

    values = [
        True,
        False,
        0,
        1,
        "",
        "Python",
        [],
        [1, 2],
        {},
        {"name": "Atul"},
        None,
    ]

    for value in values:
        if value:
            print(repr(value), "-> truthy")
        else:
            print(repr(value), "-> falsy")

    # Common falsy values include:
    # False, None, numeric zero, empty strings, empty lists, empty tuples,
    # empty sets, and empty dictionaries.


def example_07_membership_and_identity() -> None:
    section("7. Membership and identity")

    role = "admin"

    if role in {"admin", "manager"}:
        print("Privileged role.")

    username = None

    # Use "is None" rather than "== None" for None checks.
    if username is None:
        print("No username has been supplied.")


# =============================================================================
# 2. INPUT, VALIDATION, AND DECISION TABLES
# =============================================================================

def example_08_input_validation() -> None:
    section("8. Input validation")

    raw_age = "27"

    try:
        age = int(raw_age)
    except ValueError:
        print("Age must be an integer.")
        return

    if age < 0:
        print("Age cannot be negative.")
    elif age > 150:
        print("Age is outside the accepted range.")
    else:
        print("Valid age:", age)


def example_09_login_decision() -> None:
    section("9. Multi-condition login decision")

    username = "admin"
    password = "correct-password"
    account_active = True

    if not username:
        print("Username is required.")
    elif not password:
        print("Password is required.")
    elif not account_active:
        print("Account is inactive.")
    elif username == "admin" and password == "correct-password":
        print("Login successful.")
    else:
        print("Invalid credentials.")

    # In a real application, passwords must not be hard-coded or compared
    # this way. A secure system should use salted password hashing,
    # rate limiting, account lockout policies, and secret management.


def example_10_range_classification() -> None:
    section("10. Range classification")

    number = -4

    if number > 0:
        category = "positive"
    elif number < 0:
        category = "negative"
    else:
        category = "zero"

    print(number, "is", category)


# =============================================================================
# 3. NESTED CONDITIONS
# =============================================================================

def example_11_nested_if() -> None:
    section("11. Nested if statements")

    age = 25
    has_ticket = True
    is_banned = False

    if age >= 18:
        if has_ticket:
            if not is_banned:
                print("Entry approved.")
            else:
                print("Entry denied: banned.")
        else:
            print("Entry denied: ticket required.")
    else:
        print("Entry denied: minimum age not met.")

    # Deep nesting can become difficult to read.
    # Guard clauses often provide a clearer design.


def can_enter_event(age: int, has_ticket: bool, is_banned: bool) -> bool:
    """Return whether a person satisfies all entry requirements."""
    if age < 18:
        return False
    if not has_ticket:
        return False
    if is_banned:
        return False
    return True


def example_12_guard_clauses() -> None:
    section("12. Guard clauses")

    print(can_enter_event(25, True, False))
    print(can_enter_event(16, True, False))

    # Guard clauses reject invalid cases early and keep the successful path
    # less deeply nested.


# =============================================================================
# 4. CONDITIONAL EXPRESSIONS
# =============================================================================

def example_13_conditional_expression() -> None:
    section("13. Conditional expression")

    age = 21
    status = "adult" if age >= 18 else "minor"

    print(status)

    score = 85
    result = (
        "excellent"
        if score >= 90
        else "good"
        if score >= 70
        else "needs improvement"
    )

    print(result)

    # Conditional expressions are useful for short decisions.
    # Long nested expressions should normally be replaced with ordinary if/elif.


# =============================================================================
# 5. FUNCTIONS RETURNING DECISIONS
# =============================================================================

def classify_temperature(celsius: float) -> str:
    """Classify temperature using ordered mutually exclusive conditions."""
    if celsius < 0:
        return "freezing"
    elif celsius < 15:
        return "cold"
    elif celsius < 25:
        return "mild"
    elif celsius < 35:
        return "warm"
    else:
        return "hot"


def calculate_discount(customer_type: str, purchase_amount: float) -> float:
    """
    Return a discount amount.

    The checks deliberately separate customer classification from amount
    thresholds to demonstrate nested decision logic.
    """
    if purchase_amount < 0:
        raise ValueError("Purchase amount cannot be negative.")

    if customer_type == "premium":
        if purchase_amount >= 10000:
            rate = 0.20
        elif purchase_amount >= 5000:
            rate = 0.15
        else:
            rate = 0.10
    elif customer_type == "regular":
        if purchase_amount >= 10000:
            rate = 0.10
        elif purchase_amount >= 5000:
            rate = 0.05
        else:
            rate = 0.0
    else:
        rate = 0.0

    return purchase_amount * rate


def example_14_function_decisions() -> None:
    section("14. Decision-making inside functions")

    for temperature in [-10, 8, 20, 30, 40]:
        print(temperature, "->", classify_temperature(temperature))

    print("Premium discount:", calculate_discount("premium", 7000))
    print("Regular discount:", calculate_discount("regular", 7000))


# =============================================================================
# 6. EDGE CASES AND BOUNDARIES
# =============================================================================

def grade(marks: float) -> str:
    """Return a grade while validating boundaries."""
    if marks < 0 or marks > 100:
        raise ValueError("Marks must be between 0 and 100.")

    if marks >= 90:
        return "A+"
    elif marks >= 80:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 60:
        return "C"
    elif marks >= 50:
        return "D"
    else:
        return "F"


def example_15_boundary_testing() -> None:
    section("15. Boundary testing")

    test_marks = [0, 49.99, 50, 59.99, 60, 69.99, 70, 79.99, 80, 89.99, 90, 100]

    for marks in test_marks:
        print(f"{marks:6.2f} -> {grade(marks)}")

    for invalid_marks in [-1, 101]:
        try:
            print(grade(invalid_marks))
        except ValueError as error:
            print("Rejected:", error)


# =============================================================================
# 7. SHORT-CIRCUIT EVALUATION
# =============================================================================

def safe_division(numerator: float, denominator: float) -> Optional[float]:
    """Demonstrate guarding a potentially unsafe operation."""
    if denominator == 0:
        return None
    return numerator / denominator


def example_16_short_circuit() -> None:
    section("16. Short-circuit evaluation")

    username = ""
    is_admin = False

    # The second condition is evaluated only if the first condition is true.
    if username and is_admin:
        print("Admin access.")

    numbers = [10, 20, 30]

    # "and" prevents the index access when the list is empty.
    if numbers and numbers[0] > 5:
        print("First number is greater than five.")

    print("10 / 0 guarded:", safe_division(10, 0))


# =============================================================================
# 8. MATCHING MULTIPLE CONDITIONS
# =============================================================================

def classify_number(number: int) -> str:
    """Use independent if statements when multiple outcomes may apply."""
    labels = []

    if number % 2 == 0:
        labels.append("even")

    if number > 0:
        labels.append("positive")
    elif number < 0:
        labels.append("negative")
    else:
        labels.append("zero")

    return ", ".join(labels)


def example_17_independent_if_vs_elif() -> None:
    section("17. Independent if versus elif")

    number = 8

    # Both independent if statements can execute.
    if number % 2 == 0:
        print("The number is even.")

    if number > 0:
        print("The number is positive.")

    # elif means alternatives: only one branch in the chain can execute.
    if number < 0:
        print("Negative")
    elif number == 0:
        print("Zero")
    else:
        print("Positive")

    print("Combined classification:", classify_number(number))


# =============================================================================
# 9. DATA-DRIVEN DECISIONS
# =============================================================================

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def assess_transaction(amount: float, suspicious: bool, verified: bool) -> RiskLevel:
    """
    Demonstrate a realistic rule engine based on if/elif/else.

    Rules:
    - Invalid amounts are rejected before risk classification.
    - Suspicious transactions are high risk.
    - Large unverified transactions are high risk.
    - Medium amounts receive medium risk.
    - Small verified transactions receive low risk.
    """
    if amount <= 0:
        raise ValueError("Transaction amount must be positive.")

    if suspicious:
        return RiskLevel.HIGH
    elif amount >= 100000 and not verified:
        return RiskLevel.HIGH
    elif amount >= 10000:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW


def example_18_rule_engine() -> None:
    section("18. Rule-based decision system")

    transactions = [
        (500, False, True),
        (15000, False, True),
        (150000, False, False),
        (2000, True, True),
    ]

    for amount, suspicious, verified in transactions:
        risk = assess_transaction(amount, suspicious, verified)
        print(amount, suspicious, verified, "->", risk.value)


# =============================================================================
# 10. DATACLASSES AND OBJECT-ORIENTED DECISIONS
# =============================================================================

@dataclass
class Employee:
    name: str
    performance_score: float
    years_of_service: int
    disciplinary_action: bool = False


def determine_bonus(employee: Employee) -> float:
    """Determine a bonus using several business rules."""
    if employee.performance_score < 0 or employee.performance_score > 100:
        raise ValueError("Performance score must be between 0 and 100.")

    if employee.disciplinary_action:
        return 0.0

    if employee.performance_score >= 90:
        base_rate = 0.20
    elif employee.performance_score >= 75:
        base_rate = 0.12
    elif employee.performance_score >= 60:
        base_rate = 0.05
    else:
        base_rate = 0.0

    if employee.years_of_service >= 10:
        base_rate += 0.05
    elif employee.years_of_service >= 5:
        base_rate += 0.02

    return base_rate


def example_19_object_oriented_decision() -> None:
    section("19. Object-oriented decision logic")

    employees = [
        Employee("Asha", 94, 11),
        Employee("Ravi", 80, 6),
        Employee("Meera", 55, 3),
        Employee("Kabir", 95, 8, disciplinary_action=True),
    ]

    for employee in employees:
        bonus_rate = determine_bonus(employee)
        print(employee.name, "->", f"{bonus_rate:.0%} bonus")


# =============================================================================
# 11. BOOLEAN ALGEBRA AND PRECEDENCE
# =============================================================================

def example_20_precedence() -> None:
    section("20. Boolean precedence")

    a = True
    b = False
    c = False

    # Python evaluates "not" before "and", and "and" before "or".
    expression_one = a or b and c
    expression_two = (a or b) and c

    print("a or b and c:", expression_one)
    print("(a or b) and c:", expression_two)

    # Parentheses make complex business rules explicit.
    if (a and b) or (c and not b):
        print("Condition matched.")
    else:
        print("Condition did not match.")


# =============================================================================
# 12. ERROR HANDLING WITH CONDITIONS
# =============================================================================

def parse_positive_integer(value: str) -> int:
    """Convert and validate a positive integer."""
    try:
        number = int(value)
    except ValueError as error:
        raise ValueError("Value must contain a valid integer.") from error

    if number <= 0:
        raise ValueError("Value must be greater than zero.")

    return number


def example_21_error_handling() -> None:
    section("21. Validation and exceptions")

    inputs = ["42", "0", "-5", "hello"]

    for value in inputs:
        try:
            result = parse_positive_integer(value)
            print(value, "->", result)
        except ValueError as error:
            print(value, "-> rejected:", error)


# =============================================================================
# 13. ADVANCED CONDITIONAL PATTERNS
# =============================================================================

def example_22_assignment_expression() -> None:
    section("22. Assignment expression")

    text = "Python"

    # The walrus operator := assigns and tests a value in one expression.
    if (length := len(text)) > 5:
        print(f"'{text}' contains {length} characters.")

    # Use this only when it improves clarity. Ordinary assignment is often
    # easier to read.


def example_23_none_and_false_distinction() -> None:
    section("23. Distinguishing None from other falsy values")

    values = [None, 0, False, "", []]

    for value in values:
        if value is None:
            print(repr(value), "means missing/unknown.")
        elif not value:
            print(repr(value), "is present but falsy.")
        else:
            print(repr(value), "is truthy.")


def example_24_structural_pattern_matching() -> None:
    section("24. Structural pattern matching")

    command = ("move", 10, 20)

    # match/case is not a replacement for every if/elif chain.
    # It is useful when decisions depend on structure and patterns.
    match command:
        case ("move", x, y):
            print("Move to:", x, y)
        case ("stop",):
            print("Stop.")
        case _:
            print("Unknown command.")


# =============================================================================
# 14. ITERATIVE CONDITIONAL PROCESSING
# =============================================================================

def categorize_numbers(numbers: Iterable[int]) -> dict[str, list[int]]:
    """Classify numbers while preserving the original values."""
    result = {
        "negative": [],
        "zero": [],
        "positive_even": [],
        "positive_odd": [],
    }

    for number in numbers:
        if number < 0:
            result["negative"].append(number)
        elif number == 0:
            result["zero"].append(number)
        elif number % 2 == 0:
            result["positive_even"].append(number)
        else:
            result["positive_odd"].append(number)

    return result


def example_25_loop_and_condition() -> None:
    section("25. Conditions inside loops")

    numbers = [-3, -2, 0, 1, 2, 7, 8]
    categories = categorize_numbers(numbers)

    for category, values in categories.items():
        print(f"{category}: {values}")


# =============================================================================
# 15. PERFORMANCE
# =============================================================================

def linear_search_with_if(values: list[int], target: int) -> bool:
    """
    Search using an if condition.

    Complexity: O(n) in the worst case.
    """
    for value in values:
        if value == target:
            return True
    return False


def membership_search(values: list[int], target: int) -> bool:
    """
    Demonstrate Python's built-in membership operation.

    For a list, this is also O(n), but the implementation is optimized in C.
    """
    return target in values


def example_26_performance() -> None:
    section("26. Performance considerations")

    values = list(range(100_000))

    print(linear_search_with_if(values, 99_999))
    print(membership_search(values, 99_999))

    # Performance is influenced by:
    # 1. Number of conditions.
    # 2. Cost of expressions inside conditions.
    # 3. Frequency of each branch.
    # 4. Data structures used for membership tests.
    #
    # For repeated membership checks, a set can often reduce average lookup
    # complexity from O(n) to approximately O(1).
    value_set = set(values)

    if 99_999 in value_set:
        print("Fast set membership found the target.")


# =============================================================================
# 16. SECURITY-ORIENTED CONDITIONAL LOGIC
# =============================================================================

def authorize_request(
    authenticated: bool,
    role: str,
    resource_owner: bool,
    resource_public: bool,
) -> bool:
    """
    Illustrate authorization decisions.

    Authentication answers "Who are you?"
    Authorization answers "Are you allowed to perform this action?"
    """
    if not authenticated:
        return False

    if resource_public:
        return True

    if role == "admin":
        return True

    if role == "owner" and resource_owner:
        return True

    return False


def example_27_authorization() -> None:
    section("27. Security-oriented authorization")

    requests = [
        (False, "user", False, False),
        (True, "user", False, True),
        (True, "admin", False, False),
        (True, "owner", True, False),
        (True, "owner", False, False),
    ]

    for request in requests:
        print(request, "->", authorize_request(*request))

    # Security decisions should fail closed:
    # an unknown role or missing permission should normally result in denial.


# =============================================================================
# 17. COMMON MISTAKES
# =============================================================================

def example_28_common_mistakes() -> None:
    section("28. Common mistakes")

    # Mistake 1: using = instead of ==.
    #
    # Python correctly rejects:
    # if age = 18:
    #
    # Use:
    age = 18
    if age == 18:
        print("Correct equality comparison.")

    # Mistake 2: incorrect indentation.
    # Python uses indentation to define blocks.
    if age >= 18:
        print("Indented code belongs to the if block.")

    # Mistake 3: overly broad first condition.
    score = 95

    # Correct ordering from highest threshold to lowest threshold:
    if score >= 90:
        print("Excellent")
    elif score >= 70:
        print("Good")
    else:
        print("Needs improvement")

    # Mistake 4: confusing "and" with "or".
    account_age = 25
    verified = True

    if account_age >= 18 and verified:
        print("Both requirements are satisfied.")

    # Mistake 5: comparing against True unnecessarily.
    if verified:
        print("Prefer 'if verified:' to 'if verified == True:'.")


# =============================================================================
# 18. TESTING
# =============================================================================

def test_grade() -> None:
    assert grade(100) == "A+"
    assert grade(90) == "A+"
    assert grade(89.99) == "A"
    assert grade(80) == "A"
    assert grade(79.99) == "B"
    assert grade(70) == "B"
    assert grade(69.99) == "C"
    assert grade(60) == "C"
    assert grade(59.99) == "D"
    assert grade(50) == "D"
    assert grade(49.99) == "F"

    for invalid in (-1, 101):
        try:
            grade(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid marks were accepted.")


def test_authorization() -> None:
    assert authorize_request(False, "admin", False, False) is False
    assert authorize_request(True, "admin", False, False) is True
    assert authorize_request(True, "user", False, True) is True
    assert authorize_request(True, "owner", True, False) is True
    assert authorize_request(True, "owner", False, False) is False


def run_tests() -> None:
    section("29. Lightweight executable tests")

    test_grade()
    test_authorization()

    print("All tests passed.")


# =============================================================================
# 19. ADVANCED DECISION ENGINE
# =============================================================================

@dataclass
class Order:
    customer_type: str
    amount: float
    country: str
    verified: bool


def evaluate_order(order: Order) -> str:
    """
    A small industry-style decision engine.

    Decision priority:
    1. Reject invalid amount.
    2. Reject unsupported country.
    3. Require verification for high-value orders.
    4. Classify priority by amount and customer type.
    """
    if order.amount <= 0:
        return "REJECTED: invalid amount"

    supported_countries = {"IN", "US", "GB", "SG"}

    if order.country not in supported_countries:
        return "REJECTED: unsupported country"

    if order.amount >= 500000 and not order.verified:
        return "REJECTED: verification required"

    if order.customer_type == "enterprise":
        if order.amount >= 100000:
            return "APPROVED: enterprise-high-priority"
        elif order.amount >= 10000:
            return "APPROVED: enterprise-priority"
        else:
            return "APPROVED: enterprise-standard"

    elif order.customer_type == "premium":
        if order.amount >= 100000:
            return "APPROVED: premium-high-priority"
        else:
            return "APPROVED: premium-standard"

    elif order.customer_type == "regular":
        if order.amount >= 100000:
            return "APPROVED: regular-review"
        else:
            return "APPROVED: regular-standard"

    else:
        return "REJECTED: unknown customer type"


def example_30_complete_decision_engine() -> None:
    section("30. Complete decision engine")

    orders = [
        Order("enterprise", 250000, "IN", True),
        Order("premium", 15000, "US", True),
        Order("regular", 8000, "GB", True),
        Order("regular", 600000, "IN", False),
        Order("regular", 1000, "XX", True),
        Order("unknown", 1000, "IN", True),
        Order("regular", -50, "IN", True),
    ]

    for order in orders:
        print(order, "->", evaluate_order(order))


# =============================================================================
# 20. MAIN PROGRAM
# =============================================================================

def main() -> None:
    """
    Run all educational demonstrations in a controlled sequence.
    """
    examples: list[Callable[[], None]] = [
        example_01_basic_if,
        example_02_if_else,
        example_03_if_elif_else,
        example_04_comparison_operators,
        example_05_boolean_operators,
        example_06_truthiness,
        example_07_membership_and_identity,
        example_08_input_validation,
        example_09_login_decision,
        example_10_range_classification,
        example_11_nested_if,
        example_12_guard_clauses,
        example_13_conditional_expression,
        example_14_function_decisions,
        example_15_boundary_testing,
        example_16_short_circuit,
        example_17_independent_if_vs_elif,
        example_18_rule_engine,
        example_19_object_oriented_decision,
        example_20_precedence,
        example_21_error_handling,
        example_22_assignment_expression,
        example_23_none_and_false_distinction,
        example_24_structural_pattern_matching,
        example_25_loop_and_condition,
        example_26_performance,
        example_27_authorization,
        example_28_common_mistakes,
        run_tests,
        example_30_complete_decision_engine,
    ]

    for example in examples:
        example()


if __name__ == "__main__":
    main()
