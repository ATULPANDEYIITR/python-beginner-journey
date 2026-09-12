"""
Logical Operators in Python
===========================

A comprehensive, executable study file covering logical operators from
absolute beginner concepts through advanced usage.

Topics covered:
- Boolean values and truth values
- Boolean expressions
- and, or, not
- Truth tables
- Operator precedence and associativity
- Short-circuit evaluation
- Return-value behavior of and/or
- Comparisons combined with logical operators
- Chained comparisons
- Membership and identity tests
- Conditional expressions
- Validation patterns
- Nested logical expressions
- De Morgan's laws
- Boolean algebra
- Guard clauses
- Input validation
- Functions and logical conditions
- Classes and logical state
- Filtering and searching
- Algorithms using logical operators
- Edge cases
- Common mistakes
- Floating-point considerations
- None and truthiness
- Custom truth-value behavior
- Production-oriented patterns
- Performance and security considerations
- Testing logical expressions
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import Callable, Iterable, Optional


# ============================================================================
# SECTION 1: BASIC BOOLEAN CONCEPTS
# ============================================================================

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def show_result(description: str, value: object) -> None:
    """Print a labeled result."""
    print(f"{description}: {value!r}")


section("1. Boolean values")

# Python has exactly two built-in Boolean values:
# True  -> logical truth
# False -> logical falsehood
#
# bool is a subclass of int:
# True behaves numerically like 1.
# False behaves numerically like 0.

show_result("True", True)
show_result("False", False)
show_result("Type of True", type(True))
show_result("True converted to integer", int(True))
show_result("False converted to integer", int(False))

print("True + True =", True + True)
print("True + False =", True + False)
print("False + False =", False + False)


# ============================================================================
# SECTION 2: BOOLEAN EXPRESSIONS
# ============================================================================

section("2. Boolean expressions")

age = 25
has_identity_card = True
is_employed = False

show_result("age >= 18", age >= 18)
show_result("age < 18", age < 18)
show_result("has_identity_card", has_identity_card)
show_result("is_employed", is_employed)

# Comparisons produce Boolean values.
show_result("10 == 10", 10 == 10)
show_result("10 != 10", 10 != 10)
show_result("10 > 5", 10 > 5)
show_result("10 < 5", 10 < 5)
show_result("10 >= 10", 10 >= 10)
show_result("10 <= 9", 10 <= 9)


# ============================================================================
# SECTION 3: THE 'AND' OPERATOR
# ============================================================================

section("3. The and operator")

# 'and' means that all required conditions must be truthy.
#
# Boolean interpretation:
#
# True and True   -> True
# True and False  -> False
# False and True  -> False
# False and False -> False

print("True and True   =", True and True)
print("True and False  =", True and False)
print("False and True  =", False and True)
print("False and False =", False and False)

user_age = 28
has_ticket = True

can_enter = user_age >= 18 and has_ticket
show_result("Adult with a ticket can enter", can_enter)


# ============================================================================
# SECTION 4: THE 'OR' OPERATOR
# ============================================================================

section("4. The or operator")

# 'or' means that at least one condition must be truthy.
#
# True or True   -> True
# True or False  -> True
# False or True  -> True
# False or False -> False

print("True or True   =", True or True)
print("True or False  =", True or False)
print("False or True  =", False or True)
print("False or False =", False or False)

is_weekend = False
is_public_holiday = True

is_day_off = is_weekend or is_public_holiday
show_result("Is today a day off?", is_day_off)


# ============================================================================
# SECTION 5: THE 'NOT' OPERATOR
# ============================================================================

section("5. The not operator")

# 'not' reverses truth:
#
# not True  -> False
# not False -> True

print("not True  =", not True)
print("not False =", not False)

account_locked = False
can_login = not account_locked

show_result("Can login?", can_login)


# ============================================================================
# SECTION 6: TRUTH TABLES
# ============================================================================

section("6. Truth tables")

boolean_values = [False, True]

print("\nAND truth table")
print("A       B       A and B")
for a in boolean_values:
    for b in boolean_values:
        print(f"{a!s:<7} {b!s:<7} {a and b}")

print("\nOR truth table")
print("A       B       A or B")
for a in boolean_values:
    for b in boolean_values:
        print(f"{a!s:<7} {b!s:<7} {a or b}")

print("\nNOT truth table")
print("A       not A")
for a in boolean_values:
    print(f"{a!s:<7} {not a}")


# ============================================================================
# SECTION 7: COMBINING LOGICAL OPERATORS
# ============================================================================

section("7. Combining and, or, and not")

temperature = 24
raining = False
umbrella = True

comfortable = temperature >= 20 and temperature <= 30
safe_to_walk = not raining or umbrella
good_weather = comfortable and safe_to_walk

show_result("Comfortable temperature", comfortable)
show_result("Safe to walk", safe_to_walk)
show_result("Good weather", good_weather)


# ============================================================================
# SECTION 8: OPERATOR PRECEDENCE
# ============================================================================

section("8. Operator precedence")

# Logical precedence in Python is:
#
# 1. not
# 2. and
# 3. or
#
# Therefore:
#
# A or B and C
#
# means:
#
# A or (B and C)
#
# It does NOT mean:
#
# (A or B) and C

a = True
b = False
c = False

result_without_parentheses = a or b and c
result_with_parentheses = a or (b and c)

show_result("a or b and c", result_without_parentheses)
show_result("a or (b and c)", result_with_parentheses)

# Parentheses should be used when they make intent clearer.
result_explicit = (a or b) and c
show_result("(a or b) and c", result_explicit)


# ============================================================================
# SECTION 9: ASSOCIATIVITY
# ============================================================================

section("9. Associativity")

# Logical operators can be chained:
#
# A and B and C
# A or B or C
#
# Python evaluates these consistently according to their precedence
# and left-to-right evaluation rules.

values = [True, True, False]

print("True and True and False =", True and True and False)
print("False or False or True  =", False or False or True)

# 'not' is unary and applies to the expression immediately following it
# according to precedence.
show_result("not False and True", not False and True)
show_result("not (False and True)", not (False and True))


# ============================================================================
# SECTION 10: SHORT-CIRCUIT EVALUATION
# ============================================================================

section("10. Short-circuit evaluation")

# Python does not always evaluate every operand.
#
# With 'and':
# If the left operand is falsy, Python knows the whole logical expression
# cannot become truthy, so it stops.
#
# With 'or':
# If the left operand is truthy, Python knows the whole expression is
# already satisfied, so it stops.

def report(name: str, value: object) -> object:
    """Print when an expression is actually evaluated."""
    print(f"Evaluating {name}")
    return value


print("\nAND short-circuit:")
result = report("left side", False) and report("right side", True)
show_result("Result", result)

print("\nOR short-circuit:")
result = report("left side", True) or report("right side", False)
show_result("Result", result)


# ============================================================================
# SECTION 11: LOGICAL OPERATORS RETURN OPERANDS
# ============================================================================

section("11. and and or do not always return True or False")

# A critical Python-specific behavior:
#
# and and or return one of their operands.
#
# For 'and':
# - return the first falsy operand
# - otherwise return the final operand
#
# For 'or':
# - return the first truthy operand
# - otherwise return the final operand

show_result("False and 100", False and 100)
show_result("10 and 100", 10 and 100)
show_result("0 or 100", 0 or 100)
show_result("10 or 100", 10 or 100)

name = ""
display_name = name or "Anonymous"
show_result("Fallback name", display_name)

configured_timeout: Optional[int] = None
timeout = configured_timeout or 30
show_result("Timeout using or", timeout)


# ============================================================================
# SECTION 12: TRUTHINESS
# ============================================================================

section("12. Truthiness")

# Objects can be interpreted as true or false in Boolean contexts.
#
# Common falsy values:
# False
# None
# 0
# 0.0
# 0j
# ""
# []
# ()
# {}
# set()
#
# Most other objects are truthy.

truthiness_examples = [
    False,
    True,
    None,
    0,
    1,
    0.0,
    3.14,
    "",
    "Python",
    [],
    [1],
    (),
    (1,),
    {},
    {"key": "value"},
    set(),
    {1, 2},
]

for value in truthiness_examples:
    print(f"{value!r:<25} -> bool = {bool(value)}")


# ============================================================================
# SECTION 13: COMPARISONS WITH LOGICAL OPERATORS
# ============================================================================

section("13. Comparisons combined with logical operators")

marks = 82
attendance = 91

eligible = marks >= 40 and attendance >= 75
show_result("Eligible", eligible)

income = 65000
experience_years = 4

senior_candidate = income >= 50000 and experience_years >= 3
show_result("Senior candidate", senior_candidate)

# OR example
has_python = True
has_sql = False
has_excel = True

has_relevant_skill = has_python or has_sql or has_excel
show_result("Has at least one relevant skill", has_relevant_skill)

# NOT example
is_suspended = False
active_account = not is_suspended
show_result("Active account", active_account)


# ============================================================================
# SECTION 14: CHAINED COMPARISONS
# ============================================================================

section("14. Chained comparisons")

# Python allows:
#
# 18 <= age <= 60
#
# This is equivalent in logical meaning to:
#
# 18 <= age and age <= 60
#
# It is generally clearer than repeating the variable.

age = 35

show_result("18 <= age <= 60", 18 <= age <= 60)
show_result("18 <= age and age <= 60", 18 <= age and age <= 60)

score = 87
show_result("0 <= score <= 100", 0 <= score <= 100)


# ============================================================================
# SECTION 15: MEMBERSHIP AND IDENTITY
# ============================================================================

section("15. Membership and identity conditions")

skills = {"Python", "SQL", "Git"}

show_result("'Python' in skills", "Python" in skills)
show_result("'Java' in skills", "Java" in skills)

role = "developer"
show_result("role not in restricted_roles", role not in {"admin", "guest"})

value = None

# 'is' and 'is not' test object identity.
# They should normally be used for singleton objects such as None.
show_result("value is None", value is None)
show_result("value is not None", value is not None)


# ============================================================================
# SECTION 16: AND VS BITWISE &
# ============================================================================

section("16. Logical and versus bitwise &")

# 'and' is a logical operator.
# '&' is a bitwise operator.
#
# They are not interchangeable.

logical_result = True and False
bitwise_result = 6 & 3

show_result("True and False", logical_result)
show_result("6 & 3", bitwise_result)

# For Boolean operands, & can appear to resemble logical AND,
# but it has different semantics and does not provide logical short-circuiting.


# ============================================================================
# SECTION 17: OR VS BITWISE |
# ============================================================================

section("17. Logical or versus bitwise |")

logical_result = True or False
bitwise_result = 6 | 3

show_result("True or False", logical_result)
show_result("6 | 3", bitwise_result)


# ============================================================================
# SECTION 18: CONDITIONAL EXPRESSIONS
# ============================================================================

section("18. Logical expressions inside conditional expressions")

temperature = 31

weather_message = (
    "Comfortable"
    if 20 <= temperature <= 30
    else "Outside the comfortable range"
)

show_result("Weather message", weather_message)

age = 20
status = "Adult" if age >= 18 else "Minor"
show_result("Age status", status)


# ============================================================================
# SECTION 19: INPUT VALIDATION
# ============================================================================

section("19. Practical input validation")

def validate_username(username: str) -> bool:
    """
    Validate a username using logical conditions.

    Rules:
    - must not be empty
    - must contain between 3 and 20 characters
    - must not contain spaces
    """
    return (
        bool(username)
        and 3 <= len(username) <= 20
        and " " not in username
    )


usernames = ["atul", "", "ab", "user name", "valid_username"]

for username in usernames:
    print(f"{username!r:<20} -> valid = {validate_username(username)}")


def validate_password(password: str) -> bool:
    """
    Basic password validation.

    The password must:
    - contain at least 8 characters
    - contain at least one uppercase character
    - contain at least one lowercase character
    - contain at least one digit
    """
    return (
        len(password) >= 8
        and any(character.isupper() for character in password)
        and any(character.islower() for character in password)
        and any(character.isdigit() for character in password)
    )


passwords = [
    "password",
    "Password",
    "Password1",
    "P@ssword123",
]

for password in passwords:
    print(f"{password!r:<20} -> valid = {validate_password(password)}")


# ============================================================================
# SECTION 20: GUARD CLAUSES
# ============================================================================

section("20. Guard clauses")

# Logical conditions often make early validation possible.
# Guard clauses prevent deeply nested code.

def calculate_discount(price: float, customer_type: str) -> float:
    """
    Calculate a discount while validating inputs.

    Raises:
        ValueError: for invalid price or customer type.
    """
    if price < 0:
        raise ValueError("Price cannot be negative.")

    if customer_type not in {"regular", "premium"}:
        raise ValueError("Customer type must be regular or premium.")

    if price == 0:
        return 0.0

    if customer_type == "premium" and price >= 1000:
        return price * 0.20

    if customer_type == "premium":
        return price * 0.10

    return price * 0.05


for price, customer_type in [
    (500, "regular"),
    (500, "premium"),
    (1500, "premium"),
]:
    print(
        f"price={price}, customer_type={customer_type}, "
        f"discount={calculate_discount(price, customer_type):.2f}"
    )


# ============================================================================
# SECTION 21: DE MORGAN'S LAWS
# ============================================================================

section("21. De Morgan's laws")

# De Morgan's laws:
#
# not (A and B) == (not A) or (not B)
#
# not (A or B) == (not A) and (not B)
#
# These transformations are useful when simplifying complex conditions.

for a in boolean_values:
    for b in boolean_values:
        first_law_left = not (a and b)
        first_law_right = (not a) or (not b)

        second_law_left = not (a or b)
        second_law_right = (not a) and (not b)

        assert first_law_left == first_law_right
        assert second_law_left == second_law_right

print("De Morgan's first law verified for all Boolean combinations.")
print("De Morgan's second law verified for all Boolean combinations.")


# ============================================================================
# SECTION 22: SIMPLIFYING CONDITIONS
# ============================================================================

section("22. Logical simplification")

# A condition such as:
#
# if is_admin == True:
#
# can usually be written as:
#
# if is_admin:
#
# Similarly:
#
# if is_active == False:
#
# becomes:
#
# if not is_active:

is_admin = True
is_active = True

if is_admin:
    print("User has administrative privileges.")

if not is_active:
    print("This line is not executed because the account is active.")


# ============================================================================
# SECTION 23: COMPLEX BUSINESS RULE
# ============================================================================

section("23. Complex business rule")

@dataclass
class Customer:
    age: int
    annual_income: float
    credit_score: int
    has_existing_loan: bool
    is_employed: bool


def is_loan_eligible(customer: Customer) -> bool:
    """
    Determine loan eligibility using several logical rules.

    Basic policy:
    - age must be from 21 through 60
    - applicant must be employed
    - income must be at least 300,000
    - credit score must be at least 700
    - an existing loan is allowed only with a higher credit score
    """
    basic_requirements = (
        21 <= customer.age <= 60
        and customer.is_employed
        and customer.annual_income >= 300_000
        and customer.credit_score >= 700
    )

    existing_loan_exception = (
        customer.has_existing_loan
        and customer.credit_score >= 750
    )

    return basic_requirements and (
        not customer.has_existing_loan or existing_loan_exception
    )


customers = [
    Customer(30, 600_000, 780, False, True),
    Customer(30, 600_000, 720, True, True),
    Customer(30, 600_000, 760, True, True),
    Customer(19, 600_000, 800, False, True),
    Customer(30, 200_000, 800, False, True),
]

for index, customer in enumerate(customers, start=1):
    print(f"Customer {index}: eligible = {is_loan_eligible(customer)}")


# ============================================================================
# SECTION 24: SHORT-CIRCUIT AND EXPENSIVE OPERATIONS
# ============================================================================

section("24. Ordering conditions for short-circuiting")

# If one condition is inexpensive and highly likely to reject an input,
# placing it first can avoid expensive work.

def expensive_check() -> bool:
    """Simulate a costly validation."""
    print("Expensive check executed.")
    return True


valid_format = False

result = valid_format and expensive_check()
show_result("Result when format is invalid", result)

valid_format = True

result = valid_format and expensive_check()
show_result("Result when format is valid", result)


# ============================================================================
# SECTION 25: SAFE ATTRIBUTE ACCESS WITH SHORT-CIRCUIT LOGIC
# ============================================================================

section("25. Short-circuiting to protect attribute access")

@dataclass
class Profile:
    email: Optional[str]


profile: Optional[Profile] = None

# The second expression is never evaluated because profile is None.
has_email = profile is not None and bool(profile.email)

show_result("Profile has email", has_email)

profile = Profile(email="person@example.com")

has_email = profile is not None and bool(profile.email)
show_result("Profile has email after profile exists", has_email)


# ============================================================================
# SECTION 26: DEFAULT VALUES WITH OR
# ============================================================================

section("26. Default values and the or operator")

# A common pattern:
#
# value = user_value or default
#
# is concise, but it treats every falsy value as missing.
#
# This may be wrong when 0, False, or "" is a valid value.

requested_limit = 0
default_limit = 100

limit_using_or = requested_limit or default_limit

show_result("Limit using or", limit_using_or)

# If zero is a valid value, an explicit None check is safer.
limit_using_none_check = (
    default_limit if requested_limit is None else requested_limit
)

show_result("Limit using explicit None check", limit_using_none_check)


# ============================================================================
# SECTION 27: NONE VS FALSE
# ============================================================================

section("27. Distinguishing None from False")

values = [None, False, 0, "", [], "value"]

for value in values:
    print(
        f"value={value!r:<10} "
        f"bool(value)={bool(value)!s:<5} "
        f"value is None={value is None}"
    )


# ============================================================================
# SECTION 28: ANY AND ALL
# ============================================================================

section("28. any() and all() as logical tools")

# any(iterable) behaves like logical OR across its elements.
# all(iterable) behaves like logical AND across its elements.

conditions = [True, False, True]

show_result("any(conditions)", any(conditions))
show_result("all(conditions)", all(conditions))

marks = [72, 81, 90, 67]

all_passed = all(mark >= 40 for mark in marks)
any_distinction = any(mark >= 75 for mark in marks)

show_result("All students passed", all_passed)
show_result("At least one distinction", any_distinction)

# any() and all() also short-circuit while consuming iterables.


# ============================================================================
# SECTION 29: FILTERING DATA
# ============================================================================

section("29. Filtering records with logical operators")

employees = [
    {"name": "A", "age": 28, "salary": 65000, "active": True},
    {"name": "B", "age": 42, "salary": 90000, "active": True},
    {"name": "C", "age": 31, "salary": 45000, "active": False},
    {"name": "D", "age": 24, "salary": 55000, "active": True},
]

qualified_employees = [
    employee
    for employee in employees
    if employee["active"]
    and employee["salary"] >= 60000
    and 25 <= employee["age"] <= 45
]

for employee in qualified_employees:
    print(employee)


# ============================================================================
# SECTION 30: SEARCH WITH LOGICAL CONDITIONS
# ============================================================================

section("30. Searching with multiple conditions")

products = [
    {"name": "Laptop", "price": 70000, "stock": 5, "category": "electronics"},
    {"name": "Mouse", "price": 1200, "stock": 0, "category": "electronics"},
    {"name": "Chair", "price": 8000, "stock": 12, "category": "furniture"},
    {"name": "Monitor", "price": 18000, "stock": 7, "category": "electronics"},
]

available_electronics = [
    product
    for product in products
    if product["stock"] > 0
    and product["category"] == "electronics"
]

for product in available_electronics:
    print(product)


# ============================================================================
# SECTION 31: LOGICAL OPERATOR WITH FUNCTION CALLS
# ============================================================================

section("31. Function calls and short-circuit behavior")

def is_valid_age(age: int) -> bool:
    print("Checking age...")
    return 18 <= age <= 60


def has_required_documents(documents: set[str]) -> bool:
    print("Checking documents...")
    return {"identity", "address"}.issubset(documents)


age = 15
documents = {"identity", "address"}

# Because age validation is False, document validation is skipped.
eligible = is_valid_age(age) and has_required_documents(documents)

show_result("Eligible", eligible)


# ============================================================================
# SECTION 32: CUSTOM TRUTH VALUE
# ============================================================================

section("32. Custom truth-value behavior")

class Transaction:
    def __init__(self, amount: float, approved: bool) -> None:
        self.amount = amount
        self.approved = approved

    def __bool__(self) -> bool:
        # An object is considered truthy only when it is approved
        # and its transaction amount is positive.
        return self.approved and self.amount > 0

    def __repr__(self) -> str:
        return (
            f"Transaction(amount={self.amount}, "
            f"approved={self.approved})"
        )


transactions = [
    Transaction(500, True),
    Transaction(500, False),
    Transaction(0, True),
]

for transaction in transactions:
    print(f"{transaction!r} -> bool={bool(transaction)}")


# ============================================================================
# SECTION 33: BOOLEAN ALGEBRA IDENTITIES
# ============================================================================

section("33. Important Boolean algebra identities")

# Identity laws:
# A and True  == A
# A or False  == A
#
# Domination laws:
# A and False == False
# A or True   == True
#
# Idempotent laws:
# A and A == A
# A or A  == A
#
# Complement laws:
# A and not A == False
# A or not A  == True

for a in boolean_values:
    assert (a and True) == a
    assert (a or False) == a
    assert (a and False) is False
    assert (a or True) is True
    assert (a and a) == a
    assert (a or a) == a
    assert (a and not a) is False
    assert (a or not a) is True

print("Boolean algebra identities verified.")


# ============================================================================
# SECTION 34: LOGICAL EQUIVALENCE TESTING
# ============================================================================

section("34. Testing whether two logical expressions are equivalent")

def expressions_are_equivalent(
    expression_a: Callable[[bool, bool], bool],
    expression_b: Callable[[bool, bool], bool],
) -> bool:
    """Check equivalence for every possible Boolean input."""
    for a in boolean_values:
        for b in boolean_values:
            if expression_a(a, b) != expression_b(a, b):
                return False
    return True


equivalent = expressions_are_equivalent(
    lambda a, b: not (a and b),
    lambda a, b: (not a) or (not b),
)

show_result("De Morgan equivalence", equivalent)


# ============================================================================
# SECTION 35: XOR AS A LOGICAL PATTERN
# ============================================================================

section("35. XOR-style logic")

# Python does not have a keyword named 'xor'.
#
# For Boolean values:
#
# A XOR B means exactly one of A and B is true.
#
# A != B provides a clear Boolean XOR expression.

for a in boolean_values:
    for b in boolean_values:
        xor_result = a != b
        print(f"A={a}, B={b}, A XOR B={xor_result}")

# Bitwise XOR (^), while related for Boolean operands, is a bitwise operator.
show_result("True ^ False", True ^ False)
show_result("6 ^ 3", 6 ^ 3)


# ============================================================================
# SECTION 36: EXCLUSIVE CONDITIONS
# ============================================================================

section("36. Exactly-one condition")

def exactly_one(*conditions: bool) -> bool:
    """
    Return True only when exactly one condition is truthy.
    """
    return sum(bool(condition) for condition in conditions) == 1


show_result("exactly_one(True, False)", exactly_one(True, False))
show_result("exactly_one(True, True)", exactly_one(True, True))
show_result(
    "exactly_one(False, False, True)",
    exactly_one(False, False, True),
)


# ============================================================================
# SECTION 37: AT LEAST N CONDITIONS
# ============================================================================

section("37. Counting logical conditions")

def at_least_n_true(n: int, *conditions: bool) -> bool:
    """Return True when at least n supplied conditions are truthy."""
    if n < 0:
        raise ValueError("n cannot be negative.")

    return sum(bool(condition) for condition in conditions) >= n


show_result(
    "At least 2 of 3 conditions",
    at_least_n_true(2, True, True, False),
)

show_result(
    "At least 3 of 4 conditions",
    at_least_n_true(3, True, True, False, True),
)


# ============================================================================
# SECTION 38: COMPLEX AUTHORIZATION LOGIC
# ============================================================================

section("38. Authorization logic")

@dataclass
class User:
    role: str
    active: bool
    verified: bool
    owns_resource: bool


def can_edit_resource(user: User) -> bool:
    """
    Example authorization rule.

    A user can edit when:
    - the account is active
    - the account is verified
    - and either:
      * the user is an administrator
      * the user owns the resource
    """
    return (
        user.active
        and user.verified
        and (
            user.role == "admin"
            or user.owns_resource
        )
    )


users = [
    User("admin", True, True, False),
    User("user", True, True, True),
    User("user", True, True, False),
    User("user", False, True, True),
    User("user", True, False, True),
]

for user in users:
    print(f"{user!r} -> can_edit={can_edit_resource(user)}")


# ============================================================================
# SECTION 39: LOGICAL EXPRESSIONS AND EXCEPTIONS
# ============================================================================

section("39. Logical operators do not suppress exceptions when evaluation occurs")

def divide(a: float, b: float) -> float:
    """Divide two numbers."""
    return a / b


condition = False

# The division is not evaluated because the left side of 'and' is False.
safe_result = condition and divide(10, 0)
show_result("Short-circuited division", safe_result)

condition = True

try:
    # Now division is evaluated and raises ZeroDivisionError.
    unsafe_result = condition and divide(10, 0)
    show_result("Division result", unsafe_result)
except ZeroDivisionError as error:
    print("Caught expected exception:", error)


# ============================================================================
# SECTION 40: LOGICAL EXPRESSIONS AND SIDE EFFECTS
# ============================================================================

section("40. Side effects and logical expressions")

state = {"count": 0}


def increment_and_return_true() -> bool:
    state["count"] += 1
    print("Side effect executed.")
    return True


state["count"] = 0
result = False and increment_and_return_true()

show_result("Result", result)
show_result("Counter after False and expression", state["count"])

state["count"] = 0
result = True and increment_and_return_true()

show_result("Result", result)
show_result("Counter after True and expression", state["count"])

# Avoid hiding important side effects inside complicated Boolean expressions.
# Explicit statements are often easier to read and debug.


# ============================================================================
# SECTION 41: NESTED LOGICAL CONDITIONS
# ============================================================================

section("41. Nested conditions versus compound conditions")

balance = 15000
account_active = True
kyc_verified = True

compound_condition = (
    balance >= 10000
    and account_active
    and kyc_verified
)

show_result("Compound eligibility", compound_condition)

# Equivalent explicit structure:
if account_active:
    if kyc_verified:
        if balance >= 10000:
            print("Explicit nested structure: eligible.")


# ============================================================================
# SECTION 42: EDGE CASES
# ============================================================================

section("42. Important edge cases")

edge_cases = [
    ("empty string", ""),
    ("zero", 0),
    ("empty list", []),
    ("None", None),
    ("negative number", -1),
    ("non-empty string", "False"),
]

for name, value in edge_cases:
    print(f"{name:<20} value={value!r:<15} bool={bool(value)}")

# A string containing "False" is truthy because it is non-empty.
show_result("bool('False')", bool("False"))

# This is one reason user input should not automatically be treated
# as a Boolean value without explicit conversion rules.


# ============================================================================
# SECTION 43: STRING BOOLEAN INPUT
# ============================================================================

section("43. Safely interpreting textual Boolean input")

def parse_boolean(text: str) -> bool:
    """
    Parse common textual Boolean representations.

    Raises:
        ValueError: if the text is not recognized.
    """
    normalized = text.strip().lower()

    if normalized in {"true", "yes", "y", "1", "on"}:
        return True

    if normalized in {"false", "no", "n", "0", "off"}:
        return False

    raise ValueError(f"Unrecognized Boolean value: {text!r}")


for text in ["true", "YES", "0", "off", "False"]:
    print(f"{text!r} -> {parse_boolean(text)}")

try:
    parse_boolean("maybe")
except ValueError as error:
    print("Caught expected parsing error:", error)


# ============================================================================
# SECTION 44: FLOATING-POINT LOGICAL COMPARISONS
# ============================================================================

section("44. Floating-point comparisons")

# Floating-point calculations can contain small representation errors.
# Exact equality should therefore be used carefully.

calculated = 0.1 + 0.2

show_result("0.1 + 0.2", calculated)
show_result("0.1 + 0.2 == 0.3", calculated == 0.3)
show_result("isclose(0.1 + 0.2, 0.3)", isclose(calculated, 0.3))

# Logical conditions involving measured or calculated floating-point values
# often need tolerances rather than exact equality.


# ============================================================================
# SECTION 45: RANGE CONDITIONS
# ============================================================================

section("45. Range validation")

def is_valid_percentage(value: float) -> bool:
    """Check whether a value represents a percentage from 0 to 100."""
    return 0 <= value <= 100


percentages = [-1, 0, 50, 100, 101]

for percentage in percentages:
    print(
        f"percentage={percentage:>4} -> "
        f"valid={is_valid_percentage(percentage)}"
    )


# ============================================================================
# SECTION 46: MULTIPLE NEGATIONS
# ============================================================================

section("46. Multiple negations")

value = True

print("value:", value)
print("not value:", not value)
print("not not value:", not not value)

# Double negation returns the Boolean interpretation of the original value.
non_boolean = "Python"
show_result("not non_boolean", not non_boolean)
show_result("not not non_boolean", not not non_boolean)
show_result("bool(non_boolean)", bool(non_boolean))


# ============================================================================
# SECTION 47: LOGICAL OPERATOR PITFALL
# ============================================================================

section("47. A common comparison mistake")

x = 5

# Correct:
correct = x == 5 or x == 10

# Incorrect conceptual pattern:
#
# x == 5 or 10
#
# Python evaluates this as:
#
# (x == 5) or 10
#
# Since 10 is truthy, the expression can produce 10 rather than True.

incorrect_style = x == 5 or 10

show_result("Correct condition", correct)
show_result("x == 5 or 10", incorrect_style)

# The safe rule is to repeat the comparison:
# x == 5 or x == 10


# ============================================================================
# SECTION 48: ANOTHER COMMON COMPARISON PITFALL
# ============================================================================

section("48. Membership is often clearer than repeated OR")

status = "pending"

repeated_comparison = (
    status == "pending"
    or status == "approved"
    or status == "processing"
)

membership_test = status in {
    "pending",
    "approved",
    "processing",
}

show_result("Repeated comparisons", repeated_comparison)
show_result("Membership test", membership_test)


# ============================================================================
# SECTION 49: LOGICAL CONDITIONS IN LOOPS
# ============================================================================

section("49. Logical operators in loops")

numbers = list(range(1, 21))

selected_numbers = [
    number
    for number in numbers
    if number % 2 == 0 and number % 3 == 0
]

show_result("Numbers divisible by 2 and 3", selected_numbers)

selected_numbers = [
    number
    for number in numbers
    if number < 5 or number > 15
]

show_result("Numbers below 5 or above 15", selected_numbers)


# ============================================================================
# SECTION 50: LOGICAL CONDITIONS IN ALGORITHMS
# ============================================================================

section("50. Algorithmic example: interval overlap")

def intervals_overlap(
    start_a: float,
    end_a: float,
    start_b: float,
    end_b: float,
) -> bool:
    """
    Determine whether two closed intervals overlap.

    The intervals overlap when:
        start_a <= end_b
        AND
        start_b <= end_a
    """
    if start_a > end_a or start_b > end_b:
        raise ValueError("Interval start cannot exceed interval end.")

    return start_a <= end_b and start_b <= end_a


interval_tests = [
    (1, 5, 4, 8),
    (1, 3, 4, 8),
    (5, 10, 10, 12),
]

for interval in interval_tests:
    print(
        interval,
        "-> overlap =",
        intervals_overlap(*interval),
    )


# ============================================================================
# SECTION 51: LOGICAL CONDITIONS IN STATE MACHINES
# ============================================================================

section("51. Logical conditions in state validation")

allowed_transitions = {
    "draft": {"submitted"},
    "submitted": {"approved", "rejected"},
    "approved": set(),
    "rejected": {"draft"},
}


def can_transition(current: str, target: str) -> bool:
    """Check whether a state transition is allowed."""
    return (
        current in allowed_transitions
        and target in allowed_transitions[current]
    )


transitions = [
    ("draft", "submitted"),
    ("draft", "approved"),
    ("submitted", "approved"),
    ("rejected", "draft"),
]

for current, target in transitions:
    print(
        f"{current} -> {target}: "
        f"{can_transition(current, target)}"
    )


# ============================================================================
# SECTION 52: LOGICAL CONDITIONS IN DATA QUALITY
# ============================================================================

section("52. Data-quality validation")

@dataclass
class Record:
    identifier: str
    amount: float
    category: str
    active: bool


def is_valid_record(record: Record) -> bool:
    """Validate a record using several logical conditions."""
    return (
        bool(record.identifier.strip())
        and record.amount >= 0
        and record.category in {"A", "B", "C"}
        and isinstance(record.active, bool)
    )


records = [
    Record("R001", 1000, "A", True),
    Record("", 1000, "A", True),
    Record("R003", -10, "A", True),
    Record("R004", 500, "D", True),
]

for record in records:
    print(f"{record!r} -> valid={is_valid_record(record)}")


# ============================================================================
# SECTION 53: TESTING LOGICAL FUNCTIONS
# ============================================================================

section("53. Testing logical functions")

def is_adult(age: int) -> bool:
    """Return whether an age represents an adult."""
    return age >= 18


def test_is_adult() -> None:
    """Basic boundary tests."""
    assert is_adult(17) is False
    assert is_adult(18) is True
    assert is_adult(19) is True


def test_username_validation() -> None:
    """Test important username edge cases."""
    assert validate_username("abc") is True
    assert validate_username("ab") is False
    assert validate_username("") is False
    assert validate_username("user name") is False


def test_de_morgan() -> None:
    """Verify De Morgan's first law."""
    for a in boolean_values:
        for b in boolean_values:
            assert not (a and b) == ((not a) or (not b))


test_is_adult()
test_username_validation()
test_de_morgan()

print("All demonstration tests passed.")


# ============================================================================
# SECTION 54: LOGICAL EXPRESSION DEBUGGING
# ============================================================================

section("54. Debugging a complex logical expression")

age = 32
income = 75000
active = True
verified = False

condition = (
    21 <= age <= 60
    and income >= 50000
    and active
    and verified
)

show_result("Complete condition", condition)

# Break complex expressions into named intermediate conditions when debugging.
age_valid = 21 <= age <= 60
income_valid = income >= 50000
account_active = active
identity_verified = verified

print("age_valid:", age_valid)
print("income_valid:", income_valid)
print("account_active:", account_active)
print("identity_verified:", identity_verified)

debugged_condition = (
    age_valid
    and income_valid
    and account_active
    and identity_verified
)

show_result("Debugged condition", debugged_condition)


# ============================================================================
# SECTION 55: READABILITY OF COMPLEX LOGIC
# ============================================================================

section("55. Improving readability")

def is_priority_customer(
    account_active: bool,
    verified: bool,
    purchase_total: float,
    support_tier: str,
) -> bool:
    """
    Determine priority status.

    A customer must have an active verified account and either:
    - purchase at least 100,000
    - or belong to the premium support tier
    """
    return (
        account_active
        and verified
        and (
            purchase_total >= 100_000
            or support_tier == "premium"
        )
    )


show_result(
    "Priority customer",
    is_priority_customer(True, True, 25_000, "premium"),
)


# ============================================================================
# SECTION 56: LOGICAL OPERATORS WITH ITERATORS
# ============================================================================

section("56. Short-circuit behavior of any and all")

def checked_value(value: bool, label: str) -> bool:
    """Show which values are evaluated."""
    print(f"Evaluating {label}")
    return value


print("\nany() stops at the first truthy value:")
result = any(
    checked_value(value, f"value-{index}")
    for index, value in enumerate([False, False, True, True], start=1)
)
show_result("any result", result)

print("\nall() stops at the first falsy value:")
result = all(
    checked_value(value, f"value-{index}")
    for index, value in enumerate([True, True, False, True], start=1)
)
show_result("all result", result)


# ============================================================================
# SECTION 57: LOGICAL OPERATOR PERFORMANCE
# ============================================================================

section("57. Performance considerations")

# Short-circuiting can reduce unnecessary computation.
#
# A good ordering principle is:
# - Put inexpensive checks before expensive checks when appropriate.
# - Put checks likely to short-circuit early.
#
# Example:
#
# valid_input and expensive_database_check()
#
# If valid_input is False, the database check is skipped.

def cheap_check(value: int) -> bool:
    return value > 0


def expensive_check(value: int) -> bool:
    # This loop is only a demonstration of a more expensive operation.
    total = 0
    for number in range(10_000):
        total += number
    return value < total


value = -1

performance_aware_result = cheap_check(value) and expensive_check(value)
show_result("Performance-aware condition", performance_aware_result)


# ============================================================================
# SECTION 58: SECURITY CONSIDERATIONS
# ============================================================================

section("58. Security considerations")

# Logical operators are not a security boundary by themselves.
#
# Authorization must be enforced on the server or trusted execution
# environment, not merely hidden in a user interface.
#
# This function demonstrates a server-side-style authorization rule.

def authorized_for_sensitive_action(
    authenticated: bool,
    active: bool,
    verified: bool,
    has_permission: bool,
) -> bool:
    """
    Return whether a sensitive action is authorized.

    All required security properties must be satisfied.
    """
    return (
        authenticated
        and active
        and verified
        and has_permission
    )


show_result(
    "Authorized",
    authorized_for_sensitive_action(
        authenticated=True,
        active=True,
        verified=True,
        has_permission=True,
    ),
)

# Never rely on a client-side Boolean such as:
#
# is_admin = True
#
# as proof of authorization. The trusted server must independently verify
# identity, permissions, session state, and relevant business rules.


# ============================================================================
# SECTION 59: PRODUCTION DESIGN CONSIDERATIONS
# ============================================================================

section("59. Production design considerations")

# Complex Boolean expressions become difficult to maintain when business
# rules change frequently.
#
# Naming intermediate conditions makes the rule auditable.

def production_eligibility(
    age: int,
    income: float,
    credit_score: int,
    account_active: bool,
) -> bool:
    age_requirement = 21 <= age <= 65
    income_requirement = income >= 300_000
    credit_requirement = credit_score >= 700
    account_requirement = account_active

    return (
        age_requirement
        and income_requirement
        and credit_requirement
        and account_requirement
    )


show_result(
    "Production eligibility",
    production_eligibility(35, 800_000, 760, True),
)


# ============================================================================
# SECTION 60: OPERATOR PRECEDENCE REFERENCE
# ============================================================================

section("60. Practical precedence reference")

# A simplified ordering relevant to logical expressions:
#
# Parentheses
# Comparisons: ==, !=, <, <=, >, >=, in, not in, is, is not
# not
# and
# or
#
# Example:
#
# age >= 18 and country == "India" or is_admin
#
# is interpreted as:
#
# (age >= 18 and country == "India") or is_admin

age = 20
country = "India"
is_admin = False

result = (
    age >= 18
    and country == "India"
    or is_admin
)

show_result("Precedence example", result)

# Parentheses make the intended grouping explicit:
result = (
    (age >= 18 and country == "India")
    or is_admin
)

show_result("Explicitly grouped expression", result)


# ============================================================================
# SECTION 61: LOGICAL EXPRESSIONS WITH COLLECTIONS
# ============================================================================

section("61. Collections and logical conditions")

shopping_cart = [
    {"name": "Laptop", "price": 70000},
    {"name": "Mouse", "price": 1200},
    {"name": "Keyboard", "price": 3000},
]

cart_not_empty = bool(shopping_cart)
has_expensive_item = any(item["price"] > 50000 for item in shopping_cart)
all_prices_valid = all(item["price"] > 0 for item in shopping_cart)

show_result("Cart not empty", cart_not_empty)
show_result("Has expensive item", has_expensive_item)
show_result("All prices valid", all_prices_valid)

cart_is_valid = (
    cart_not_empty
    and all_prices_valid
)

show_result("Cart is valid", cart_is_valid)


# ============================================================================
# SECTION 62: LOGICAL CONDITIONS AND EXCEPTION HANDLING
# ============================================================================

section("62. Validation before processing")

def process_payment(amount: float, account_active: bool) -> str:
    """
    Demonstrate validation before a payment operation.
    """
    if not account_active:
        raise PermissionError("Account is inactive.")

    if not amount > 0:
        raise ValueError("Payment amount must be positive.")

    return f"Payment of {amount:.2f} accepted."


payment_cases = [
    (1000, True),
    (0, True),
    (500, False),
]

for amount, active in payment_cases:
    try:
        print(process_payment(amount, active))
    except (ValueError, PermissionError) as error:
        print("Payment rejected:", error)


# ============================================================================
# SECTION 63: LOGICAL CONDITIONS WITH DEFAULT CONFIGURATION
# ============================================================================

section("63. Configuration validation")

@dataclass
class Configuration:
    host: str
    port: int
    debug: bool


def is_valid_configuration(config: Configuration) -> bool:
    """Validate a simple application configuration."""
    return (
        bool(config.host.strip())
        and 1 <= config.port <= 65_535
        and isinstance(config.debug, bool)
    )


configurations = [
    Configuration("localhost", 8000, True),
    Configuration("", 8000, True),
    Configuration("localhost", 70_000, True),
]

for config in configurations:
    print(f"{config!r} -> valid={is_valid_configuration(config)}")


# ============================================================================
# SECTION 64: LOGICAL EXPRESSIONS AND NAMED PREDICATES
# ============================================================================

section("64. Named predicates")

def is_adult_person(age: int) -> bool:
    return age >= 18


def has_valid_income(income: float) -> bool:
    return income >= 300_000


def has_good_credit(score: int) -> bool:
    return score >= 700


def qualifies_for_offer(age: int, income: float, score: int) -> bool:
    return (
        is_adult_person(age)
        and has_valid_income(income)
        and has_good_credit(score)
    )


show_result(
    "Qualifies for offer",
    qualifies_for_offer(35, 800_000, 750),
)


# ============================================================================
# SECTION 65: LOGICAL OPERATOR EXERCISES AS EXECUTABLE ASSERTIONS
# ============================================================================

section("65. Executable logical exercises")

# These assertions reinforce core concepts while also acting as tests.

assert True and True is True
assert True and False is False
assert False and True is False
assert True or False is True
assert False or False is False
assert not True is False
assert not False is True

assert (18 <= 25 <= 60) is True
assert ("Python" in {"Python", "SQL"}) is True
assert (None is None) is True

assert any([False, False, True]) is True
assert all([True, True, True]) is True
assert all([True, False, True]) is False

print("Core logical assertions passed.")


# ============================================================================
# SECTION 66: FINAL INTEGRATED EXAMPLE
# ============================================================================

section("66. Integrated example")

@dataclass
class Application:
    age: int
    income: float
    credit_score: int
    employment_status: str
    account_verified: bool
    country: str
    requested_amount: float


def evaluate_application(application: Application) -> dict[str, object]:
    """
    Evaluate an application with clearly separated Boolean rules.

    Rules:
    - applicant must be between 21 and 65
    - income must be positive
    - requested amount must be positive
    - applicant must be employed or self-employed
    - verification must be complete
    - credit score must be at least 650
    - country must be one of the supported countries
    """
    age_valid = 21 <= application.age <= 65
    income_valid = application.income > 0
    requested_amount_valid = application.requested_amount > 0

    employment_valid = application.employment_status in {
        "employed",
        "self-employed",
    }

    supported_country = application.country in {
        "India",
        "United States",
        "United Kingdom",
    }

    credit_valid = application.credit_score >= 650
    verification_valid = application.account_verified

    eligible = (
        age_valid
        and income_valid
        and requested_amount_valid
        and employment_valid
        and verification_valid
        and credit_valid
        and supported_country
    )

    return {
        "age_valid": age_valid,
        "income_valid": income_valid,
        "requested_amount_valid": requested_amount_valid,
        "employment_valid": employment_valid,
        "verification_valid": verification_valid,
        "credit_valid": credit_valid,
        "supported_country": supported_country,
        "eligible": eligible,
    }


application = Application(
    age=32,
    income=900_000,
    credit_score=735,
    employment_status="employed",
    account_verified=True,
    country="India",
    requested_amount=500_000,
)

evaluation = evaluate_application(application)

for rule, result in evaluation.items():
    print(f"{rule:<25} -> {result}")


# ============================================================================
# SECTION 67: CONCEPTUAL REFERENCE PRINTED BY THE SCRIPT
# ============================================================================

section("67. Logical operator reference")

reference = {
    "and": "True when the required operands are all truthy; short-circuits on a falsy operand.",
    "or": "True when at least one operand is truthy; short-circuits on a truthy operand.",
    "not": "Reverses the truth value of an expression.",
    "in": "Tests membership in a container.",
    "not in": "Tests that a value is not a member.",
    "is": "Tests object identity.",
    "is not": "Tests that two references are not the same object.",
    "any": "Returns True when at least one item in an iterable is truthy.",
    "all": "Returns True when every item in an iterable is truthy.",
}

for operator, description in reference.items():
    print(f"{operator:<10} -> {description}")


# ============================================================================
# END OF STUDY SCRIPT
# ============================================================================

print("\n" + "=" * 78)
print("Logical operators study script completed successfully.")
print("=" * 78)
