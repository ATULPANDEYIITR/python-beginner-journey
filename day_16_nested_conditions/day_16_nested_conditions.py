"""
Nested Conditions: A complete beginner-to-advanced study program.

This standalone program demonstrates nested conditional logic in Python:
    - Boolean expressions
    - if / elif / else
    - nested if statements
    - multi-level decision trees
    - validation
    - guard clauses
    - conditional expressions
    - combining conditions with and/or/not
    - membership and identity checks
    - truthiness
    - match/case comparison
    - decision-table thinking
    - edge cases
    - error handling
    - testing
    - performance considerations
    - maintainability and security considerations

Run:
    python nested_conditions.py
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, Optional


# ---------------------------------------------------------------------------
# 1. FUNDAMENTALS
# ---------------------------------------------------------------------------

def demonstrate_basic_condition() -> None:
    """Show the fundamental structure of a conditional."""
    age = 20

    if age >= 18:
        print("Basic condition: adult")
    else:
        print("Basic condition: minor")


def demonstrate_if_elif_else() -> None:
    """Show mutually exclusive branches."""
    score = 82

    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"

    print(f"if/elif/else: score={score}, grade={grade}")


def demonstrate_boolean_operators() -> None:
    """Demonstrate and, or, and not."""
    age = 25
    has_id = True
    is_student = False

    if age >= 18 and has_id:
        print("and: access requirement satisfied")

    if is_student or age >= 60:
        print("or: discount condition satisfied")
    else:
        print("or: regular pricing applies")

    if not is_student:
        print("not: the person is not a student")


# ---------------------------------------------------------------------------
# 2. NESTED CONDITIONS
# ---------------------------------------------------------------------------

def classify_access(age: int, has_identity_document: bool) -> str:
    """
    Demonstrate a simple nested condition.

    The second decision is evaluated only after the first decision succeeds.
    """
    if age >= 18:
        if has_identity_document:
            return "Access granted"
        else:
            return "Access denied: identity document required"
    else:
        return "Access denied: minimum age requirement not met"


def demonstrate_nested_conditions() -> None:
    examples = [
        (25, True),
        (25, False),
        (16, True),
        (16, False),
    ]

    for age, has_id in examples:
        result = classify_access(age, has_id)
        print(f"Nested condition: age={age}, has_id={has_id} -> {result}")


# ---------------------------------------------------------------------------
# 3. DEEPER NESTING
# ---------------------------------------------------------------------------

def classify_exam_result(score: float, attendance: float, misconduct: bool) -> str:
    """
    A three-level decision tree.

    Rules:
        1. Score must be valid.
        2. A score of at least 40 is required to pass.
        3. Attendance must be at least 75%.
        4. Misconduct prevents a normal pass classification.
        5. High score + high attendance can produce distinction.
    """
    if 0 <= score <= 100:
        if attendance >= 75:
            if misconduct:
                return "Review required: misconduct record"
            else:
                if score >= 75:
                    return "Distinction"
                else:
                    if score >= 40:
                        return "Pass"
                    else:
                        return "Fail"
        else:
            return "Fail: attendance requirement not met"
    else:
        return "Invalid score"


def demonstrate_deep_nesting() -> None:
    cases = [
        (92, 95, False),
        (62, 80, False),
        (32, 90, False),
        (88, 90, True),
        (75, 60, False),
        (105, 90, False),
    ]

    for score, attendance, misconduct in cases:
        print(
            f"Exam: score={score}, attendance={attendance}, "
            f"misconduct={misconduct} -> "
            f"{classify_exam_result(score, attendance, misconduct)}"
        )


# ---------------------------------------------------------------------------
# 4. VALIDATION BEFORE NESTED DECISIONS
# ---------------------------------------------------------------------------

def validate_age(age: object) -> tuple[bool, str]:
    """
    Validate input before making business decisions.

    bool is rejected because bool is a subclass of int in Python and accepting
    True as age 1 would be an unintended behavior.
    """
    if isinstance(age, bool):
        return False, "Age must be an integer, not a boolean."

    if not isinstance(age, int):
        return False, "Age must be an integer."

    if age < 0 or age > 150:
        return False, "Age must be between 0 and 150."

    return True, ""


def eligibility_decision(age: object, employed: bool, income: float) -> str:
    """Validate first, then apply nested eligibility rules."""
    valid, message = validate_age(age)

    if not valid:
        return f"Invalid input: {message}"

    if age >= 18:
        if employed:
            if income >= 30000:
                return "Eligible: employed adult with sufficient income"
            else:
                return "Condition not met: income is below the threshold"
        else:
            return "Condition not met: applicant is unemployed"
    else:
        return "Condition not met: applicant is under 18"


# ---------------------------------------------------------------------------
# 5. EDGE CASES
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    """Show boundary values and unusual but valid values."""
    ages = [0, 17, 18, 19, 150]

    for age in ages:
        print(f"Age boundary {age}: {classify_access(age, True)}")

    for value in [0, "", [], [1], "Python", None, False, True]:
        if value:
            print(f"Truthiness: {value!r} is truthy")
        else:
            print(f"Truthiness: {value!r} is falsy")


# ---------------------------------------------------------------------------
# 6. COMPOUND CONDITIONS VERSUS NESTED CONDITIONS
# ---------------------------------------------------------------------------

def access_compound(age: int, has_id: bool, active_account: bool) -> bool:
    """Several requirements expressed in one boolean expression."""
    return age >= 18 and has_id and active_account


def access_nested(age: int, has_id: bool, active_account: bool) -> bool:
    """The same logical requirements expressed as nested decisions."""
    if age >= 18:
        if has_id:
            if active_account:
                return True

    return False


def demonstrate_equivalent_logic() -> None:
    cases = [
        (20, True, True),
        (20, True, False),
        (20, False, True),
        (17, True, True),
    ]

    for case in cases:
        compound = access_compound(*case)
        nested = access_nested(*case)
        print(f"Equivalent logic: {case} -> compound={compound}, nested={nested}")


# ---------------------------------------------------------------------------
# 7. NESTING WITH COLLECTIONS
# ---------------------------------------------------------------------------

def find_user_permission(
    users: list[dict[str, object]],
    username: str,
    required_permission: str,
) -> str:
    """
    Nested conditions over a collection.

    The structure illustrates:
        collection -> matching user -> active status -> permission.
    """
    for user in users:
        if user.get("username") == username:
            if user.get("active"):
                permissions = user.get("permissions", [])

                if isinstance(permissions, list):
                    if required_permission in permissions:
                        return "Permission granted"
                    else:
                        return "Permission denied: missing permission"
                else:
                    return "Invalid permission data"
            else:
                return "Permission denied: inactive account"

    return "User not found"


def demonstrate_collection_nesting() -> None:
    users = [
        {
            "username": "alice",
            "active": True,
            "permissions": ["read", "write"],
        },
        {
            "username": "bob",
            "active": False,
            "permissions": ["read"],
        },
    ]

    for username in ["alice", "bob", "charlie"]:
        print(
            username,
            "->",
            find_user_permission(users, username, "write"),
        )


# ---------------------------------------------------------------------------
# 8. CONDITIONAL EXPRESSIONS
# ---------------------------------------------------------------------------

def demonstrate_conditional_expression() -> None:
    age = 21
    status = "adult" if age >= 18 else "minor"

    print(f"Conditional expression: {status}")

    # Conditional expressions can be nested, but this is usually harder to
    # read than ordinary if/else statements.
    score = 85
    grade = (
        "A"
        if score >= 90
        else "B"
        if score >= 80
        else "C"
        if score >= 70
        else "F"
    )

    print(f"Nested conditional expression: {grade}")


# ---------------------------------------------------------------------------
# 9. GUARD CLAUSES
# ---------------------------------------------------------------------------

def calculate_discount(
    customer_active: bool,
    age: int,
    purchase_amount: float,
) -> float:
    """
    Guard clauses reduce unnecessary nesting.

    Instead of:
        if active:
            if adult:
                if amount:
                    ...

    invalid cases are returned early.
    """
    if not customer_active:
        return 0.0

    if age < 18:
        return 0.0

    if purchase_amount <= 0:
        return 0.0

    if purchase_amount >= 10000:
        return 0.20

    if purchase_amount >= 5000:
        return 0.10

    return 0.05


# ---------------------------------------------------------------------------
# 10. DECISION TABLE
# ---------------------------------------------------------------------------

def calculate_shipping(
    destination: str,
    weight_kg: float,
    express: bool,
) -> float:
    """
    Nested conditions represent a small decision table.

    Invalid input is rejected before pricing logic.
    """
    if destination not in {"domestic", "international"}:
        raise ValueError("Unknown destination.")

    if weight_kg <= 0:
        raise ValueError("Weight must be positive.")

    if destination == "domestic":
        if weight_kg <= 1:
            base = 60
        elif weight_kg <= 5:
            base = 120
        else:
            base = 250

        if express:
            return base * 1.75

        return base

    if weight_kg <= 1:
        base = 1000
    elif weight_kg <= 5:
        base = 2500
    else:
        base = 5000

    if express:
        return base * 1.50

    return base


# ---------------------------------------------------------------------------
# 11. ENUMS AND NESTED DECISIONS
# ---------------------------------------------------------------------------

class UserRole(Enum):
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"


def determine_feature_access(
    role: UserRole,
    verified: bool,
    feature_enabled: bool,
) -> str:
    """
    Enum values make categorical conditions clearer than arbitrary strings.
    """
    if not feature_enabled:
        return "Feature disabled"

    if role == UserRole.GUEST:
        if verified:
            return "Guest verified: limited access"
        return "Guest access only"

    if role == UserRole.USER:
        if verified:
            return "Verified user: standard access"
        return "User must verify account"

    if role == UserRole.ADMIN:
        if verified:
            return "Administrator: administrative access"
        return "Administrator must verify account"

    return "Unknown role"


# ---------------------------------------------------------------------------
# 12. OBJECT-ORIENTED DECISION MODEL
# ---------------------------------------------------------------------------

@dataclass
class Account:
    username: str
    age: int
    active: bool
    verified: bool
    role: UserRole
    balance: float


class AccountDecisionEngine:
    """Encapsulate related nested decision rules."""

    MINIMUM_BALANCE_FOR_TRANSFER = 100.0

    def evaluate_transfer(
        self,
        sender: Account,
        recipient: Account,
        amount: float,
    ) -> str:
        if amount <= 0:
            return "Rejected: transfer amount must be positive"

        if not sender.active:
            return "Rejected: sender account is inactive"

        if not recipient.active:
            return "Rejected: recipient account is inactive"

        if not sender.verified:
            return "Rejected: sender is not verified"

        if not recipient.verified:
            return "Rejected: recipient is not verified"

        if sender.age < 18:
            return "Rejected: sender must be an adult"

        if sender.balance < amount:
            return "Rejected: insufficient balance"

        if sender.balance - amount < self.MINIMUM_BALANCE_FOR_TRANSFER:
            return "Rejected: minimum retained balance would be violated"

        return "Transfer approved"


# ---------------------------------------------------------------------------
# 13. ERROR HANDLING INSIDE CONDITIONAL LOGIC
# ---------------------------------------------------------------------------

def safe_integer_decision(raw_value: str) -> str:
    """Convert text to an integer and then make a nested decision."""
    try:
        number = int(raw_value.strip())
    except (AttributeError, ValueError):
        return "Invalid integer input"

    if number >= 0:
        if number % 2 == 0:
            return "Non-negative even integer"
        else:
            return "Non-negative odd integer"
    else:
        if number % 2 == 0:
            return "Negative even integer"
        else:
            return "Negative odd integer"


# ---------------------------------------------------------------------------
# 14. SHORT-CIRCUIT EVALUATION
# ---------------------------------------------------------------------------

def demonstrate_short_circuit() -> None:
    """
    Python may avoid evaluating later conditions when the result is already
    known. This is useful for safe access to potentially unavailable data.
    """
    user: Optional[dict[str, object]] = None

    if user is not None and user.get("active") is True:
        print("Short circuit: active user")
    else:
        print("Short circuit: user unavailable or inactive")

    values = [10, 20, 30]

    if values and values[0] == 10:
        print("Short circuit: list is non-empty and first value is 10")


# ---------------------------------------------------------------------------
# 15. MATCH/CASE AS AN ALTERNATIVE
# ---------------------------------------------------------------------------

def classify_http_status(status_code: int) -> str:
    """
    Python's match/case can express categorical branching.

    Nested if statements remain useful when conditions involve ranges,
    multiple independent properties, or complex boolean expressions.
    """
    match status_code:
        case 200:
            return "Success"
        case 201:
            return "Created"
        case 400:
            return "Bad request"
        case 401 | 403:
            return "Authentication or authorization failure"
        case 404:
            return "Not found"
        case code if 500 <= code <= 599:
            return "Server error"
        case _:
            return "Other status"


# ---------------------------------------------------------------------------
# 16. RECURSIVE NESTED DECISION TREE
# ---------------------------------------------------------------------------

@dataclass
class DecisionNode:
    question: str
    yes: Optional["DecisionNode"] = None
    no: Optional["DecisionNode"] = None
    result: Optional[str] = None


def evaluate_decision_tree(
    node: DecisionNode,
    answers: Iterable[bool],
) -> str:
    """
    Traverse a binary decision tree.

    This generalizes nested if statements into a data structure.
    """
    current = node
    answer_iterator = iter(answers)

    while current.result is None:
        try:
            answer = next(answer_iterator)
        except StopIteration:
            return "Insufficient answers"

        if answer:
            if current.yes is None:
                return "Invalid tree: missing yes branch"
            current = current.yes
        else:
            if current.no is None:
                return "Invalid tree: missing no branch"
            current = current.no

    return current.result


def build_vehicle_decision_tree() -> DecisionNode:
    return DecisionNode(
        question="Does the vehicle have four wheels?",
        yes=DecisionNode(
            question="Is it powered by an engine?",
            yes=DecisionNode(
                question="Is it intended mainly for passenger transport?",
                yes=DecisionNode(result="Car"),
                no=DecisionNode(result="Utility vehicle"),
            ),
            no=DecisionNode(result="Non-powered four-wheel vehicle"),
        ),
        no=DecisionNode(
            question="Does it have two wheels?",
            yes=DecisionNode(result="Two-wheel vehicle"),
            no=DecisionNode(result="Other vehicle"),
        ),
    )


# ---------------------------------------------------------------------------
# 17. NESTED CONDITIONS WITH SECURITY-RELEVANT VALIDATION
# ---------------------------------------------------------------------------

def authorization_check(
    authenticated: bool,
    role: str,
    requested_resource: str,
    resource_owner: str,
    current_user: str,
) -> str:
    """
    A simplified authorization example.

    Security principle:
        authentication and authorization are distinct.

    This is only a local demonstration, not a production authentication
    system.
    """
    if not authenticated:
        return "Denied: authentication required"

    normalized_role = role.strip().lower()

    if normalized_role == "admin":
        return "Allowed: administrator access"

    if normalized_role == "user":
        if requested_resource == "profile":
            if resource_owner == current_user:
                return "Allowed: own profile"
            return "Denied: profile belongs to another user"

        if requested_resource == "public":
            return "Allowed: public resource"

        return "Denied: insufficient permission"

    return "Denied: unknown role"


# ---------------------------------------------------------------------------
# 18. PERFORMANCE: ORDER CHEAP TESTS BEFORE EXPENSIVE TESTS WHEN SAFE
# ---------------------------------------------------------------------------

def expensive_check() -> bool:
    """
    Placeholder-free simulation of an expensive operation.

    The function performs real computation rather than pretending that an
    operation exists.
    """
    total = 0
    for number in range(1, 10_001):
        total += number * number

    return total > 0


def performance_aware_decision(age: int, active: bool) -> bool:
    """
    Cheap conditions are evaluated before the expensive computation.

    This matters when the expensive operation is unnecessary for rejected
    inputs.
    """
    if age < 18:
        return False

    if not active:
        return False

    if expensive_check():
        return True

    return False


# ---------------------------------------------------------------------------
# 19. TESTABLE RULE FUNCTIONS
# ---------------------------------------------------------------------------

def temperature_category(celsius: float) -> str:
    """Nested boundary classification."""
    if celsius < 0:
        return "freezing"
    else:
        if celsius < 10:
            return "cold"
        else:
            if celsius < 25:
                return "mild"
            else:
                if celsius < 35:
                    return "warm"
                else:
                    return "hot"


def run_assertions() -> None:
    """Executable tests for important boundaries and failure conditions."""
    assert classify_access(18, True) == "Access granted"
    assert classify_access(18, False) == "Access denied: identity document required"
    assert classify_access(17, True) == "Access denied: minimum age requirement not met"

    assert temperature_category(-1) == "freezing"
    assert temperature_category(0) == "cold"
    assert temperature_category(9.99) == "cold"
    assert temperature_category(10) == "mild"
    assert temperature_category(24.99) == "mild"
    assert temperature_category(25) == "warm"
    assert temperature_category(34.99) == "warm"
    assert temperature_category(35) == "hot"

    assert access_compound(20, True, True) == access_nested(20, True, True)
    assert access_compound(20, False, True) == access_nested(20, False, True)

    assert safe_integer_decision("10") == "Non-negative even integer"
    assert safe_integer_decision("-3") == "Negative odd integer"
    assert safe_integer_decision("abc") == "Invalid integer input"

    assert classify_http_status(200) == "Success"
    assert classify_http_status(503) == "Server error"


# ---------------------------------------------------------------------------
# 20. PRACTICAL INDUSTRY-STYLE CASE STUDY
# ---------------------------------------------------------------------------

@dataclass
class LoanApplication:
    applicant_name: str
    age: int
    monthly_income: float
    monthly_debt: float
    credit_score: int
    employment_years: float
    verified_identity: bool
    requested_amount: float


class LoanDecisionEngine:
    """
    Demonstration loan decision engine.

    The thresholds are educational examples, not financial advice or a real
    lender's underwriting policy.
    """

    def evaluate(self, application: LoanApplication) -> str:
        if application.age < 18:
            return "Rejected: applicant is under 18"

        if not application.verified_identity:
            return "Rejected: identity verification failed"

        if application.monthly_income <= 0:
            return "Rejected: income must be positive"

        if application.monthly_debt < 0:
            return "Rejected: debt cannot be negative"

        if application.credit_score < 300 or application.credit_score > 900:
            return "Rejected: invalid credit score"

        if application.requested_amount <= 0:
            return "Rejected: requested amount must be positive"

        debt_to_income = (
            application.monthly_debt / application.monthly_income
        )

        if application.credit_score >= 750:
            if debt_to_income <= 0.35:
                if application.employment_years >= 2:
                    return "Eligible: standard review"
                else:
                    return "Manual review: limited employment history"
            else:
                return "Manual review: elevated debt-to-income ratio"

        if application.credit_score >= 650:
            if debt_to_income <= 0.30:
                if application.employment_years >= 3:
                    return "Manual review: moderate credit profile"
                else:
                    return "Manual review: employment history insufficient"
            else:
                return "Rejected: debt-to-income ratio too high"

        return "Rejected: credit score below example threshold"


def demonstrate_loan_case_study() -> None:
    applications = [
        LoanApplication(
            "Asha",
            30,
            100000,
            20000,
            780,
            5,
            True,
            500000,
        ),
        LoanApplication(
            "Bharat",
            28,
            80000,
            30000,
            680,
            4,
            True,
            300000,
        ),
        LoanApplication(
            "Chirag",
            22,
            50000,
            20000,
            620,
            1,
            True,
            200000,
        ),
        LoanApplication(
            "Divya",
            35,
            90000,
            10000,
            760,
            7,
            False,
            400000,
        ),
    ]

    engine = LoanDecisionEngine()

    for application in applications:
        result = engine.evaluate(application)
        print(f"Loan decision for {application.applicant_name}: {result}")


# ---------------------------------------------------------------------------
# 21. COMMON MISTAKES
# ---------------------------------------------------------------------------

def demonstrate_common_mistakes() -> None:
    """
    These examples show safe alternatives to common conditional mistakes.
    """

    # Mistake: confusing assignment with comparison.
    # Python prevents the classic C-style accidental assignment in if.
    status = "active"

    if status == "active":
        print("Correct comparison with ==")

    # Mistake: writing conditions whose precedence is unclear.
    age = 25
    has_id = True
    active = True

    # Parentheses make intent explicit.
    if (age >= 18) and has_id and active:
        print("Explicit boolean grouping")

    # Mistake: checking equality when membership expresses the requirement.
    role = "admin"

    if role in {"admin", "manager"}:
        print("Membership condition matched")


# ---------------------------------------------------------------------------
# 22. INTERACTIVE DEMONSTRATION
# ---------------------------------------------------------------------------

def interactive_age_classifier() -> None:
    """
    Optional interactive example.

    It is isolated from the rest of the program so the main demonstration
    remains automatically executable without requiring user input.
    """
    raw_age = input("Enter an age, or press Enter to skip: ").strip()

    if not raw_age:
        print("Interactive example skipped.")
        return

    try:
        age = int(raw_age)
    except ValueError:
        print("Invalid age: enter a whole number.")
        return

    valid, message = validate_age(age)

    if not valid:
        print(message)
        return

    if age < 13:
        print("Child")
    else:
        if age < 18:
            print("Teenager")
        else:
            if age < 65:
                print("Adult")
            else:
                print("Senior adult")


# ---------------------------------------------------------------------------
# 23. MAIN PROGRAM
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 72)
    print("NESTED CONDITIONS: PYTHON STUDY PROGRAM")
    print("=" * 72)

    print("\n1. Basic condition")
    demonstrate_basic_condition()

    print("\n2. if / elif / else")
    demonstrate_if_elif_else()

    print("\n3. Boolean operators")
    demonstrate_boolean_operators()

    print("\n4. Nested conditions")
    demonstrate_nested_conditions()

    print("\n5. Deeper nesting")
    demonstrate_deep_nesting()

    print("\n6. Validation before decisions")
    print(eligibility_decision(25, True, 50000))
    print(eligibility_decision(17, True, 50000))
    print(eligibility_decision(-2, True, 50000))
    print(eligibility_decision(True, True, 50000))

    print("\n7. Edge cases")
    demonstrate_edge_cases()

    print("\n8. Compound versus nested logic")
    demonstrate_equivalent_logic()

    print("\n9. Collection nesting")
    demonstrate_collection_nesting()

    print("\n10. Conditional expressions")
    demonstrate_conditional_expression()

    print("\n11. Guard clauses")
    for amount in [0, 3000, 7000, 12000]:
        print(
            f"Purchase={amount}: "
            f"discount={calculate_discount(True, 30, amount):.0%}"
        )

    print("\n12. Shipping decision table")
    for destination, weight, express in [
        ("domestic", 0.5, False),
        ("domestic", 3, True),
        ("international", 2, False),
        ("international", 8, True),
    ]:
        print(
            destination,
            weight,
            express,
            "->",
            calculate_shipping(destination, weight, express),
        )

    print("\n13. Enum-based decisions")
    print(
        determine_feature_access(
            UserRole.USER,
            verified=True,
            feature_enabled=True,
        )
    )

    print("\n14. Object-oriented decision engine")
    sender = Account(
        "sender",
        30,
        True,
        True,
        UserRole.USER,
        5000,
    )
    recipient = Account(
        "recipient",
        30,
        True,
        True,
        UserRole.USER,
        1000,
    )
    account_engine = AccountDecisionEngine()
    print(account_engine.evaluate_transfer(sender, recipient, 1000))

    print("\n15. Error handling")
    for raw_value in ["42", "-7", "11", "hello", ""]:
        print(f"{raw_value!r}: {safe_integer_decision(raw_value)}")

    print("\n16. Short-circuit evaluation")
    demonstrate_short_circuit()

    print("\n17. match/case")
    for code in [200, 201, 404, 401, 503, 418]:
        print(code, "->", classify_http_status(code))

    print("\n18. Decision tree")
    tree = build_vehicle_decision_tree()
    print(evaluate_decision_tree(tree, [True, True, True]))
    print(evaluate_decision_tree(tree, [False, True]))
    print(evaluate_decision_tree(tree, [True, True, False]))

    print("\n19. Authorization")
    print(
        authorization_check(
            True,
            "user",
            "profile",
            "alice",
            "alice",
        )
    )
    print(
        authorization_check(
            True,
            "user",
            "profile",
            "bob",
            "alice",
        )
    )

    print("\n20. Performance-aware decision")
    print(performance_aware_decision(25, True))
    print(performance_aware_decision(16, True))

    print("\n21. Automated tests")
    run_assertions()
    print("All assertions passed.")

    print("\n22. Loan case study")
    demonstrate_loan_case_study()

    print("\n23. Common mistakes and safer patterns")
    demonstrate_common_mistakes()

    print("\nThe interactive example is available through:")
    print("interactive_age_classifier()")


if __name__ == "__main__":
    main()
