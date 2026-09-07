"""
BOOLEAN VALUES IN PYTHON
========================

A comprehensive, executable study file covering Boolean values from absolute
beginner concepts through advanced usage, implementation details, edge cases,
short-circuit evaluation, truthiness, comparisons, Boolean algebra, bitwise
operations, validation, testing, performance, and practical design.

Run this file directly:

    python boolean_values.py
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import reduce
from operator import and_, or_, xor
from typing import Any, Callable, Iterable, Optional


# =============================================================================
# 1. WHAT IS A BOOLEAN VALUE?
# =============================================================================

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


section("1. BOOLEAN VALUES: THE FUNDAMENTALS")

# A Boolean represents one of two logical states:
#   True  -> logical truth
#   False -> logical falsity
#
# Python uses the built-in bool type for Boolean values.

is_python_running = True
is_program_finished = False

print("True:", True)
print("False:", False)
print("Type of True:", type(True))
print("Type of False:", type(False))

assert isinstance(True, bool)
assert isinstance(False, bool)

# Python's Boolean literals are case-sensitive.
# Correct: True, False
# Incorrect: true, false
#
# The following would raise NameError if executed:
# true
# false

# Boolean values are useful for representing decisions and states.

logged_in = True
has_permission = False

print("Logged in:", logged_in)
print("Has permission:", has_permission)


# =============================================================================
# 2. BOOL IS A BUILT-IN TYPE
# =============================================================================

section("2. THE bool TYPE")

print("bool is:", bool)
print("bool's type:", type(bool))
print("True's class:", True.__class__)
print("False's class:", False.__class__)

# bool is a subclass of int in Python.
# This is an important Python-specific behavior.

print("issubclass(bool, int):", issubclass(bool, int))
print("isinstance(True, int):", isinstance(True, int))
print("isinstance(False, int):", isinstance(False, int))

# Boolean values have integer behavior:
# True behaves numerically like 1.
# False behaves numerically like 0.

print("True + True:", True + True)
print("True + False:", True + False)
print("False + False:", False + False)
print("True * 10:", True * 10)
print("False * 10:", False * 10)

assert True == 1
assert False == 0
assert True + True == 2

# Although this relationship is valid, using True and False as ordinary
# integers can reduce readability. Use explicit integers when the concept
# is numeric rather than logical.


# =============================================================================
# 3. CREATING BOOLEAN VALUES WITH bool()
# =============================================================================

section("3. CONVERTING VALUES TO BOOLEAN WITH bool()")

# bool(value) asks Python whether a value is truthy or falsy.

examples = [
    True,
    False,
    0,
    1,
    -1,
    0.0,
    3.14,
    "",
    "hello",
    [],
    [1],
    (),
    (1,),
    {},
    {"name": "Ada"},
    None,
]

for value in examples:
    print(f"{value!r:20} -> bool = {bool(value)}")

# Important:
# bool("False") is True because the string is non-empty.
# The contents of a string do not automatically determine its truth value.

print('bool("False"):', bool("False"))
print('bool("0"):', bool("0"))
print('bool("no"):', bool("no"))
print('bool(""):', bool(""))

# A common mistake is assuming that a non-empty textual representation of
# false is itself the Boolean value False.


# =============================================================================
# 4. TRUTHY AND FALSY VALUES
# =============================================================================

section("4. TRUTHINESS AND FALSINESS")

# Python does not require an expression to literally be True or False in
# conditional statements. Objects can have a truth value.

falsy_values = [
    False,
    None,
    0,
    0.0,
    0j,
    "",
    [],
    (),
    {},
    set(),
    range(0),
]

print("Falsy values:")
for value in falsy_values:
    print(f"  {value!r:20} -> {bool(value)}")

# Common truthy examples include non-zero numbers and non-empty containers.

truthy_values = [
    True,
    1,
    -1,
    0.5,
    "False",
    [0],
    {"x": None},
    {0},
    range(1),
]

print("\nTruthy values:")
for value in truthy_values:
    print(f"  {value!r:20} -> {bool(value)}")

# Important distinction:
#
# [] is falsy because it is empty.
# [False] is truthy because it is non-empty.
#
# The Boolean value of a container normally depends on whether it contains
# elements, not on whether the elements themselves are truthy.

print("bool([]):", bool([]))
print("bool([False]):", bool([False]))
print("bool([0]):", bool([0]))


# =============================================================================
# 5. if STATEMENTS AND BOOLEAN CONDITIONS
# =============================================================================

section("5. BOOLEAN VALUES IN CONDITIONS")

age = 25

if age >= 18:
    print("The person is an adult.")
else:
    print("The person is a minor.")

# The comparison age >= 18 produces a Boolean value.

adult = age >= 18
print("adult:", adult)
assert adult is True

# A Boolean variable can directly control a branch.

has_account = True

if has_account:
    print("Account exists.")
else:
    print("Account does not exist.")

# Explicit comparison with True is usually unnecessary:
#
# Preferred:
# if has_account:
#     ...
#
# Less idiomatic:
# if has_account == True:
#     ...
#
# The direct form communicates intent more clearly.


# =============================================================================
# 6. COMPARISON OPERATORS RETURN BOOLEAN VALUES
# =============================================================================

section("6. COMPARISON OPERATORS")

a = 10
b = 20

comparison_results = {
    "a == b": a == b,
    "a != b": a != b,
    "a < b": a < b,
    "a <= b": a <= b,
    "a > b": a > b,
    "a >= b": a >= b,
}

for expression, result in comparison_results.items():
    print(f"{expression:8} -> {result}")

# Equality compares values.
print("10 == 10:", 10 == 10)
print("10 == 10.0:", 10 == 10.0)
print("10 == True:", 10 == True)

# Identity is different from equality.
#
# == asks whether two objects compare equal.
# is asks whether two references point to the same object.

x = [1, 2, 3]
y = [1, 2, 3]
z = x

print("x == y:", x == y)
print("x is y:", x is y)
print("x is z:", x is z)

assert x == y
assert x is not y
assert x is z

# Use "is" primarily for identity checks such as:
#
# if value is None:
#     ...
#
# Do not generally replace == with is for value comparison.


# =============================================================================
# 7. THE LOGICAL NOT OPERATOR
# =============================================================================

section("7. THE not OPERATOR")

print("not True:", not True)
print("not False:", not False)

ready = False
print("ready:", ready)
print("not ready:", not ready)

# not converts an operand's truth value into its opposite.

print("not 0:", not 0)
print("not 1:", not 1)
print("not []:", not [])
print('not "Python":', not "Python")

assert (not True) is False
assert (not False) is True
assert (not 0) is True
assert (not 1) is False


# =============================================================================
# 8. THE and OPERATOR
# =============================================================================

section("8. THE and OPERATOR")

print("True and True:", True and True)
print("True and False:", True and False)
print("False and True:", False and True)
print("False and False:", False and False)

# Conceptually, and requires both operands to be truthy.
#
# Truth table:
#
# A      B       A and B
# False  False   False
# False  True    False
# True   False   False
# True   True    True

# But Python's "and" is not simply a Boolean-only operator.
# It returns one of its operands.

print("'hello' and 123:", "hello" and 123)
print("0 and 123:", 0 and 123)
print("[] and 123:", [] and 123)
print("[1] and 123:", [1] and 123)

# This behavior is extremely important.
#
# Python evaluates the first operand.
# If it is falsy, Python returns it immediately.
# Otherwise, Python evaluates and returns the second operand.

user_name = "Ada"
display_name = user_name and user_name.upper()
print("display_name:", display_name)

missing_name = ""
fallback_result = missing_name and missing_name.upper()
print("fallback_result:", fallback_result)


# =============================================================================
# 9. THE or OPERATOR
# =============================================================================

section("9. THE or OPERATOR")

print("True or True:", True or True)
print("True or False:", True or False)
print("False or True:", False or True)
print("False or False:", False or False)

# Like and, or returns operands rather than necessarily returning bool.

print("'hello' or 123:", "hello" or 123)
print("0 or 123:", 0 or 123)
print('"" or "fallback":', "" or "fallback")
print('"Ada" or "fallback":', "Ada" or "fallback")

# or returns the first truthy operand.
# If no operand is truthy, it returns the final operand.

name = ""
safe_name = name or "Anonymous"
print("safe_name:", safe_name)

# This is concise, but be careful:
# If an empty string is a valid value, "or" may incorrectly replace it.


# =============================================================================
# 10. SHORT-CIRCUIT EVALUATION
# =============================================================================

section("10. SHORT-CIRCUIT EVALUATION")

def report(label: str, value: Any) -> Any:
    """Show when an expression is actually evaluated."""
    print(f"Evaluating {label!r}")
    return value


print("Testing and:")
result = report("first", False) and report("second", True)
print("Result:", result)

print("\nTesting or:")
result = report("first", True) or report("second", False)
print("Result:", result)

# In:
#
# A and B
#
# B is not evaluated if A is falsy.
#
# In:
#
# A or B
#
# B is not evaluated if A is truthy.

# This is useful for guarding operations.

possibly_empty: list[int] = []

if possibly_empty and possibly_empty[0] > 10:
    print("First element is greater than 10.")
else:
    print("List is empty or first element is not greater than 10.")

# Because the list is empty, the second expression is never evaluated.
# This prevents IndexError.


# =============================================================================
# 11. BOOLEAN OPERATOR PRECEDENCE
# =============================================================================

section("11. BOOLEAN OPERATOR PRECEDENCE")

# Important precedence rules include:
#
# Comparisons have higher precedence than not.
# not has higher precedence than and.
# and has higher precedence than or.
#
# Therefore:
#
# not A and B or C
#
# is interpreted approximately as:
#
# ((not A) and B) or C

A = True
B = False
C = True

result_without_parentheses = not A and B or C
result_with_parentheses = ((not A) and B) or C

print("Without parentheses:", result_without_parentheses)
print("With explicit grouping:", result_with_parentheses)

# Parentheses improve readability when logical expressions become complex.

score = 75
attendance = 90

eligible = (score >= 60) and (attendance >= 75)
print("Eligible:", eligible)


# =============================================================================
# 12. CHAINED COMPARISONS
# =============================================================================

section("12. CHAINED COMPARISONS")

age = 30

print("18 <= age <= 65:", 18 <= age <= 65)
print("0 < age < 18:", 0 < age < 18)

# Chained comparisons are generally clearer than:
#
# age >= 18 and age <= 65

assert 18 <= age <= 65

# Python evaluates chained comparisons efficiently and does not unnecessarily
# evaluate the middle expression twice.

temperature = 22
comfortable = 18 <= temperature <= 26
print("Comfortable temperature:", comfortable)


# =============================================================================
# 13. BOOLEAN ALGEBRA
# =============================================================================

section("13. BOOLEAN ALGEBRA")

# Boolean algebra operates on truth values.
#
# Basic identities:
#
# NOT True  = False
# NOT False = True
#
# A AND True  = A
# A AND False = False
#
# A OR True   = True
# A OR False  = A
#
# A AND A = A
# A OR A  = A
#
# NOT NOT A = A

boolean_values = [False, True]

for value in boolean_values:
    print(
        f"A={value}: "
        f"A and True={value and True}, "
        f"A or False={value or False}, "
        f"not not A={not not value}"
    )

# De Morgan's laws:
#
# not (A and B) == (not A) or (not B)
# not (A or B)  == (not A) and (not B)

for left in boolean_values:
    for right in boolean_values:
        assert not (left and right) == ((not left) or (not right))
        assert not (left or right) == ((not left) and (not right))

print("De Morgan's laws verified for all Boolean combinations.")


# =============================================================================
# 14. BUILDING TRUTH TABLES
# =============================================================================

section("14. TRUTH TABLES")

def truth_table_binary(
    operation: Callable[[bool, bool], bool],
    name: str,
) -> None:
    """Print a truth table for a binary Boolean operation."""
    print(f"\n{name}")
    print("A      B      Result")
    print("-" * 22)

    for left in (False, True):
        for right in (False, True):
            result = operation(left, right)
            print(f"{str(left):5}  {str(right):5}  {result}")


truth_table_binary(lambda a, b: a and b, "AND")
truth_table_binary(lambda a, b: a or b, "OR")
truth_table_binary(lambda a, b: a != b, "XOR")


# =============================================================================
# 15. XOR WITH BOOLEANS
# =============================================================================

section("15. XOR: EXCLUSIVE OR")

# XOR is true when exactly one operand is true.

for left in boolean_values:
    for right in boolean_values:
        print(
            f"{left!s:5} XOR {right!s:5} = {left ^ right}"
        )

# With Boolean operands, ^ performs bitwise XOR and produces a Boolean result
# because bool is an integer subtype.

assert False ^ False is False
assert False ^ True is True
assert True ^ False is True
assert True ^ True is False

# XOR can also be expressed as:
#
# A != B
#
# for Boolean operands.

for left in boolean_values:
    for right in boolean_values:
        assert (left ^ right) == (left != right)


# =============================================================================
# 16. BOOLEAN OPERATORS VS BITWISE OPERATORS
# =============================================================================

section("16. LOGICAL OPERATORS VS BITWISE OPERATORS")

# Logical operators:
#   and
#   or
#   not
#
# Bitwise operators:
#   &
#   |
#   ^
#   ~
#
# For ordinary Boolean operands, bitwise operations can resemble Boolean
# algebra. With integers, they operate on individual binary bits.

print("True and False:", True and False)
print("True & False:", True & False)

print("True or False:", True or False)
print("True | False:", True | False)

print("True ^ False:", True ^ False)
print("not True:", not True)
print("~True:", ~True)

# ~True is -2, not False.
#
# Why?
# True is numerically 1.
# ~x is equivalent to -x - 1.
# ~1 == -2.

print("~True:", ~True)
assert ~True == -2

# Do not use ~ as a substitute for logical not.


# =============================================================================
# 17. BITWISE BOOLEAN OPERATIONS ON INTEGERS
# =============================================================================

section("17. BITWISE OPERATIONS ON INTEGERS")

x = 0b1100
y = 0b1010

print("x:", bin(x))
print("y:", bin(y))
print("x & y:", bin(x & y))
print("x | y:", bin(x | y))
print("x ^ y:", bin(x ^ y))
print("~x:", ~x)

# Bitwise AND:
#   1100
# & 1010
# = 1000
#
# Bitwise OR:
#   1100
# | 1010
# = 1110
#
# Bitwise XOR:
#   1100
# ^ 1010
# = 0110

assert x & y == 0b1000
assert x | y == 0b1110
assert x ^ y == 0b0110


# =============================================================================
# 18. BOOLEAN VALUES IN FUNCTIONS
# =============================================================================

section("18. FUNCTIONS THAT RETURN BOOLEAN VALUES")

def is_even(number: int) -> bool:
    """Return True when number is divisible by two."""
    return number % 2 == 0


def is_positive(number: float) -> bool:
    """Return True for positive numbers."""
    return number > 0


def has_items(items: Iterable[Any]) -> bool:
    """Return whether an iterable converted to a list contains items."""
    return bool(list(items))


for number in range(-3, 4):
    print(number, "is even:", is_even(number))

print("is_positive(10):", is_positive(10))
print("is_positive(-10):", is_positive(-10))
print("has_items([]):", has_items([]))
print("has_items([1, 2]):", has_items([1, 2]))

# Type annotations such as -> bool document that a function is intended to
# return a Boolean value. Python does not enforce the annotation at runtime.


# =============================================================================
# 19. RETURNING NON-BOOLEAN VALUES FROM PREDICATE-LIKE EXPRESSIONS
# =============================================================================

section("19. PREDICATES AND RETURN VALUES")

def find_first_positive(numbers: Iterable[int]) -> Optional[int]:
    """Return the first positive integer, or None if none exists."""
    for number in numbers:
        if number > 0:
            return number
    return None


numbers = [-5, -2, 7, 10]
result = find_first_positive(numbers)

print("First positive number:", result)
print("Found a positive number:", result is not None)

# A predicate is normally a function whose purpose is to answer a yes/no
# question and should therefore return bool.

def is_valid_score(score: float) -> bool:
    return 0 <= score <= 100


print("is_valid_score(85):", is_valid_score(85))
print("is_valid_score(150):", is_valid_score(150))


# =============================================================================
# 20. BOOLEAN INPUT VALIDATION
# =============================================================================

section("20. VALIDATING BOOLEAN INPUT")

def require_bool(value: Any) -> bool:
    """
    Accept only actual Boolean values.

    bool(value) would convert many unrelated values. That is not always
    appropriate when an API requires a strict Boolean.
    """
    if not isinstance(value, bool):
        raise TypeError(
            f"Expected bool, received {type(value).__name__}"
        )
    return value


for value in [True, False]:
    print("Valid:", require_bool(value))

for value in [0, 1, "true", "false", None]:
    try:
        require_bool(value)
    except TypeError as error:
        print("Rejected:", repr(value), "->", error)


# =============================================================================
# 21. STRICT BOOLEAN PARSING FROM TEXT
# =============================================================================

section("21. PARSING BOOLEAN TEXT")

def parse_boolean(text: str) -> bool:
    """
    Convert common textual Boolean representations into bool.

    This function is intentionally strict: unknown values raise ValueError.
    """
    normalized = text.strip().casefold()

    true_values = {"true", "1", "yes", "y", "on"}
    false_values = {"false", "0", "no", "n", "off"}

    if normalized in true_values:
        return True

    if normalized in false_values:
        return False

    raise ValueError(f"Invalid Boolean value: {text!r}")


for text in ["true", "TRUE", " yes ", "0", "off", "n"]:
    print(repr(text), "->", parse_boolean(text))

for text in ["maybe", "", "truth", "2"]:
    try:
        parse_boolean(text)
    except ValueError as error:
        print(repr(text), "-> rejected:", error)

# bool("false") would return True, which is why textual Boolean parsing should
# not normally be implemented simply as bool(text).


# =============================================================================
# 22. NONE VS FALSE
# =============================================================================

section("22. None IS NOT False")

print("False == None:", False == None)
print("False is None:", False is None)
print("bool(None):", bool(None))

# None commonly represents absence of a value.
# False represents a known logical false state.
#
# These are conceptually different even though both are falsy.

value: Optional[bool] = None

if value is None:
    print("Boolean value has not been supplied.")
elif value:
    print("Boolean value is True.")
else:
    print("Boolean value is False.")

# This distinction matters in APIs where:
#
# None  = unknown / omitted / not configured
# False = explicitly disabled
# True  = explicitly enabled


# =============================================================================
# 23. BOOLEAN DEFAULTS AND "OR"
# =============================================================================

section("23. DEFAULT VALUES AND A COMMON OR PITFALL")

def display_limit(limit: Optional[int]) -> int:
    """Use 100 only when limit is None."""
    if limit is None:
        return 100
    return limit


print("display_limit(None):", display_limit(None))
print("display_limit(0):", display_limit(0))

# This is preferable to:
#
# limit = limit or 100
#
# when zero is meaningful, because 0 is falsy.

def problematic_limit(limit: Optional[int]) -> int:
    return limit or 100


print("problematic_limit(None):", problematic_limit(None))
print("problematic_limit(0):", problematic_limit(0))

# The second function turns an explicitly supplied 0 into 100.
# Whether this is wrong depends on the application's semantics.


# =============================================================================
# 24. CUSTOM TRUTH VALUE WITH __bool__
# =============================================================================

section("24. CUSTOM OBJECT TRUTHINESS WITH __bool__")

class Account:
    def __init__(self, balance: float) -> None:
        self.balance = balance

    def __bool__(self) -> bool:
        # An account is considered truthy when it has a positive balance.
        return self.balance > 0


accounts = [
    Account(100.0),
    Account(0.0),
    Account(-10.0),
]

for account in accounts:
    print(
        "Balance:", account.balance,
        "Truth value:", bool(account)
    )

# __bool__ must return a Boolean.
#
# If an object does not define __bool__, Python can use __len__ to determine
# truthiness. If neither exists, instances are normally truthy.


# =============================================================================
# 25. CUSTOM TRUTH VALUE WITH __len__
# =============================================================================

section("25. CUSTOM TRUTHINESS WITH __len__")

class TaskQueue:
    def __init__(self, tasks: Iterable[str]) -> None:
        self.tasks = list(tasks)

    def __len__(self) -> int:
        return len(self.tasks)


empty_queue = TaskQueue([])
busy_queue = TaskQueue(["backup", "email"])

print("Empty queue:", bool(empty_queue))
print("Busy queue:", bool(busy_queue))

# Because TaskQueue has __len__ but no __bool__, Python uses the length.
#
# Length 0 -> falsy
# Length > 0 -> truthy


# =============================================================================
# 26. BOOLEAN EXPRESSIONS WITH FUNCTION CALLS
# =============================================================================

section("26. BOOLEAN EXPRESSIONS AND SIDE EFFECTS")

def authenticate(username: str, password: str) -> bool:
    """Simple educational authentication predicate."""
    return username == "admin" and password == "secret"


def has_admin_permission(role: str) -> bool:
    """Return whether a role has administrative permissions."""
    return role == "admin"


username = "admin"
password = "secret"
role = "admin"

authorized = authenticate(username, password) and has_admin_permission(role)
print("Authorized:", authorized)

# Short-circuiting can avoid unnecessary function calls.
#
# It can also make code harder to understand if the right side has side
# effects. Prefer explicit if statements when evaluation order has important
# business consequences.


# =============================================================================
# 27. BOOLEAN EXPRESSIONS AND EXCEPTIONS
# =============================================================================

section("27. GUARDING POTENTIALLY UNSAFE OPERATIONS")

data = [10, 20, 30]

if data and data[0] > 5:
    print("Safe access succeeded.")

# Without the first condition, accessing data[0] when data is empty would
# raise IndexError.

data = []

if data and data[0] > 5:
    print("This will not execute.")
else:
    print("Short-circuit prevented invalid indexing.")

# Another common pattern:

denominator = 0

if denominator != 0 and 100 / denominator > 2:
    print("Division is safe.")
else:
    print("Division was not attempted because denominator is zero.")


# =============================================================================
# 28. BOOLEAN VALUES IN LIST FILTERING
# =============================================================================

section("28. FILTERING WITH BOOLEAN CONDITIONS")

numbers = list(range(-5, 6))

positive_numbers = [number for number in numbers if number > 0]
even_numbers = [number for number in numbers if number % 2 == 0]
positive_even_numbers = [
    number for number in numbers
    if number > 0 and number % 2 == 0
]

print("Numbers:", numbers)
print("Positive:", positive_numbers)
print("Even:", even_numbers)
print("Positive and even:", positive_even_numbers)


# =============================================================================
# 29. all() AND any()
# =============================================================================

section("29. all() AND any()")

values = [2, 4, 6, 8]

print("All values are even:", all(value % 2 == 0 for value in values))
print("Any value is greater than 5:", any(value > 5 for value in values))

# all() returns True if every element is truthy.
# any() returns True if at least one element is truthy.
#
# Both functions short-circuit.

print("all([]):", all([]))
print("any([]):", any([]))

# These results are intentional:
#
# all([]) == True
# any([]) == False
#
# This follows the logic of universal and existential quantification:
# there is no counterexample to "all elements satisfy the condition", while
# there is no element satisfying "at least one".


# =============================================================================
# 30. all() AND any() WITH PREDICATES
# =============================================================================

section("30. PREDICATE-BASED VALIDATION")

scores = [75, 82, 91, 68]

all_valid = all(0 <= score <= 100 for score in scores)
any_excellent = any(score >= 90 for score in scores)

print("All scores valid:", all_valid)
print("At least one excellent score:", any_excellent)


# =============================================================================
# 31. BOOLEAN VALUES IN sorted(), min(), max(), and key FUNCTIONS
# =============================================================================

section("31. BOOLEAN KEY FUNCTIONS")

people = [
    {"name": "Alice", "active": True},
    {"name": "Bob", "active": False},
    {"name": "Charlie", "active": True},
]

# bool values can be used as sorting keys.
# False compares as 0 and True compares as 1.

people_by_activity = sorted(
    people,
    key=lambda person: person["active"],
    reverse=True,
)

print("Active people first:", people_by_activity)

# A more explicit key may improve readability:
people_by_activity = sorted(
    people,
    key=lambda person: not person["active"],
)

print("Active people first using not:", people_by_activity)


# =============================================================================
# 32. BOOLEAN VALUES AS DICTIONARY KEYS
# =============================================================================

section("32. BOOLEANS AS DICTIONARY KEYS")

boolean_dictionary = {
    True: "enabled",
    False: "disabled",
}

print(boolean_dictionary[True])
print(boolean_dictionary[False])

# Because True == 1 and False == 0, Boolean and integer keys can collide.

collision = {
    True: "boolean true",
    1: "integer one",
}

print("Collision dictionary:", collision)
print("Number of keys:", len(collision))

# True and 1 are equal keys.
# False and 0 are equal keys.
#
# This is an important edge case when designing dictionaries.


# =============================================================================
# 33. BOOLEAN VALUES IN SETS
# =============================================================================

section("33. BOOLEANS IN SETS")

values = {True, 1, False, 0, 2}
print("Set containing Boolean and integer equivalents:", values)

# True and 1 represent the same set key.
# False and 0 represent the same set key.

assert len({True, 1}) == 1
assert len({False, 0}) == 1


# =============================================================================
# 34. BOOLEAN COMPARISONS WITH NUMBERS
# =============================================================================

section("34. BOOLEAN-NUMERIC COMPARISONS")

print("True == 1:", True == 1)
print("False == 0:", False == 0)
print("True < 2:", True < 2)
print("False < 1:", False < 1)

# This follows from bool inheriting from int.
#
# Do not rely on this behavior when the domain distinction between logical
# state and numeric quantity matters.


# =============================================================================
# 35. BOOLEAN ARRAYS AND SUMMATION
# =============================================================================

section("35. COUNTING BOOLEAN CONDITIONS")

numbers = [1, 2, 3, 4, 5, 6]

even_flags = [number % 2 == 0 for number in numbers]

print("Even flags:", even_flags)
print("Number of even values:", sum(even_flags))

# True contributes 1 and False contributes 0.
#
# This is useful for simple counting, but explicit code can be clearer when
# the operation has complex business semantics.

assert sum(even_flags) == 3


# =============================================================================
# 36. BOOLEAN EXPRESSIONS AND TERNARY CONDITIONAL EXPRESSIONS
# =============================================================================

section("36. CONDITIONAL EXPRESSIONS")

age = 20
category = "adult" if age >= 18 else "minor"

print("Category:", category)

# Syntax:
#
# value_if_true if condition else value_if_false
#
# The condition itself produces a Boolean.

temperature = 35
message = "Hot" if temperature > 30 else "Comfortable"
print(message)


# =============================================================================
# 37. NESTED BOOLEAN CONDITIONS
# =============================================================================

section("37. COMPLEX BUSINESS RULE")

def can_purchase(
    age: int,
    has_valid_payment_method: bool,
    account_active: bool,
    product_in_stock: bool,
) -> bool:
    """
    Determine whether a purchase can proceed.

    Every required condition must be satisfied.
    """
    return (
        age >= 18
        and has_valid_payment_method
        and account_active
        and product_in_stock
    )


print(
    "Can purchase:",
    can_purchase(
        age=30,
        has_valid_payment_method=True,
        account_active=True,
        product_in_stock=True,
    ),
)

print(
    "Can purchase:",
    can_purchase(
        age=17,
        has_valid_payment_method=True,
        account_active=True,
        product_in_stock=True,
    ),
)


# =============================================================================
# 38. REFACTORING COMPLEX BOOLEAN EXPRESSIONS
# =============================================================================

section("38. MAKING COMPLEX CONDITIONS READABLE")

def is_eligible_for_discount(
    age: int,
    is_member: bool,
    purchase_amount: float,
) -> bool:
    """Return whether a customer qualifies for a discount."""
    adult = age >= 18
    sufficient_purchase = purchase_amount >= 100
    return adult and is_member and sufficient_purchase


print(
    "Discount eligible:",
    is_eligible_for_discount(30, True, 150),
)

# Named intermediate conditions can improve readability and debugging.
#
# Instead of one huge expression, isolate business concepts into meaningful
# Boolean variables or helper functions.


# =============================================================================
# 39. BOOLEAN LOGIC WITH ENUMERATED STATES
# =============================================================================

section("39. BOOLEAN VS MULTI-STATE MODELS")

class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DISABLED = "disabled"
    FAILED = "failed"


status = Status.ACTIVE

is_active = status is Status.ACTIVE
is_finished = status in {Status.DISABLED, Status.FAILED}

print("Status:", status)
print("Is active:", is_active)
print("Is finished:", is_finished)

# A Boolean is appropriate for a binary state.
#
# If a domain has three or more meaningful states, forcing it into multiple
# unrelated Boolean flags can create invalid combinations.
#
# An enum or another explicit state model may be better.


# =============================================================================
# 40. BOOLEAN FLAGS AND INVALID COMBINATIONS
# =============================================================================

section("40. MULTIPLE BOOLEAN FLAGS")

@dataclass
class ConnectionState:
    connected: bool
    reconnecting: bool


states = [
    ConnectionState(False, False),
    ConnectionState(True, False),
    ConnectionState(False, True),
    ConnectionState(True, True),
]

for state in states:
    print(state)

# The final state may be logically invalid if a connection cannot be both
# connected and reconnecting.
#
# Multiple Boolean fields create a Cartesian product of possible states.
# If the domain has mutually exclusive states, an Enum can encode the model
# more safely.


# =============================================================================
# 41. BOOLEAN FLAG DESIGN
# =============================================================================

section("41. GOOD BOOLEAN VARIABLE NAMES")

# Boolean names are clearer when they sound like predicates or states.

is_valid = True
has_permission = True
can_edit = False
should_retry = True
was_successful = True

print(is_valid, has_permission, can_edit, should_retry, was_successful)

# Weak names:
#
# valid = True
# permission = True
# retry = True
#
# These can be ambiguous depending on context.
#
# Strong names communicate that the value is Boolean.


# =============================================================================
# 42. DOUBLE NEGATIVES
# =============================================================================

section("42. AVOIDING DOUBLE NEGATIVES")

is_disabled = False

if not is_disabled:
    print("The feature is enabled.")

# Expressions such as:
#
# if not is_not_valid:
#
# require unnecessary mental processing.
#
# Prefer positive Boolean names where practical:
#
# is_valid
# is_enabled
# has_access


# =============================================================================
# 43. BOOLEAN COMPARISON STYLE
# =============================================================================

section("43. BOOLEAN COMPARISON BEST PRACTICES")

flag = True

# Preferred:
if flag:
    print("flag is truthy.")

# Usually unnecessary:
if flag == True:
    print("This works, but is less idiomatic.")

# For exact Boolean identity, "is" can be appropriate:
if flag is True:
    print("flag is exactly the singleton True.")

# In most application logic, simply using:
#
# if flag:
#
# is clearer and also handles truthy objects.
#
# If the API specifically requires an actual bool, validate it separately.


# =============================================================================
# 44. "is" VS "==" WITH BOOLEAN VALUES
# =============================================================================

section("44. is VS ==")

print("True == 1:", True == 1)
print("True is 1:", True is 1)

# "==" performs equality comparison.
# "is" performs identity comparison.
#
# A robust special-value check is:
#
# value is None
#
# For Boolean variables, direct truth testing is normally preferable.


# =============================================================================
# 45. BOOLEAN OPERATOR RETURN VALUES
# =============================================================================

section("45. AND/OR RETURN OPERANDS")

operands = [
    ("A and B", "A" and "B"),
    ("" + " and B", "" and "B"),
    ("A or B", "A" or "B"),
    ("" + " or B", "" or "B"),
]

for expression, result in operands:
    print(f"{expression!r:12} -> {result!r}")

# This distinction is crucial:
#
# bool(A and B)
#
# returns a Boolean.
#
# A and B
#
# may return A or B itself.

value = [] and [1]
print("[] and [1]:", value, type(value))

value = [1] and [2]
print("[1] and [2]:", value, type(value))

value = "" or "fallback"
print('"" or "fallback":', value, type(value))


# =============================================================================
# 46. FORCING A BOOLEAN RESULT
# =============================================================================

section("46. CONVERTING AN EXPRESSION TO bool")

expression_result = "hello" and 123

print("Expression result:", expression_result)
print("Boolean result:", bool(expression_result))

# If an API contract requires a bool, explicitly convert the expression:
is_available = bool("hello" and 123)

print("is_available:", is_available)
assert isinstance(is_available, bool)


# =============================================================================
# 47. BOOLEAN NEGATION OF TRUTHINESS
# =============================================================================

section("47. not AND TRUTHINESS")

objects = [None, 0, "", [], [1], 5, "Python"]

for object_value in objects:
    print(
        f"value={object_value!r:10} "
        f"bool={bool(object_value)!s:5} "
        f"not={not object_value}"
    )


# =============================================================================
# 48. OBJECTS WITH BOTH __bool__ AND __len__
# =============================================================================

section("48. __bool__ TAKES PRECEDENCE OVER __len__")

class PriorityExample:
    def __init__(self, length: int, truth: bool) -> None:
        self.length = length
        self.truth = truth

    def __bool__(self) -> bool:
        return self.truth

    def __len__(self) -> int:
        return self.length


example = PriorityExample(length=10, truth=False)
print("Length:", len(example))
print("Boolean value:", bool(example))

# When both methods exist, __bool__ determines truthiness.


# =============================================================================
# 49. INVALID __bool__ IMPLEMENTATION
# =============================================================================

section("49. __bool__ MUST RETURN bool")

class InvalidBoolean:
    def __bool__(self) -> int:
        # This violates Python's requirement that __bool__ return bool.
        return 1  # type: ignore[return-value]


try:
    bool(InvalidBoolean())
except TypeError as error:
    print("Invalid __bool__ rejected:", error)


# =============================================================================
# 50. BOOLEAN VALUES AND OBJECT IDENTITY
# =============================================================================

section("50. TRUE AND FALSE ARE SINGLETON BOOLEAN OBJECTS")

print("id(True):", id(True))
print("id(False):", id(False))

# True and False are singleton objects in Python.
# Their identity is stable during a process.
#
# Identity checks such as "value is True" are therefore technically meaningful
# for exact Boolean identity, though normal conditional checks are preferred.


# =============================================================================
# 51. BOOLEAN VALUES AND JSON-LIKE DATA
# =============================================================================

section("51. BOOLEAN DATA IN PYTHON")

# Python:
#   True
#   False
#   None
#
# JSON:
#   true
#   false
#   null
#
# The textual spelling differs even though Python's JSON serialization module
# handles the conversion automatically.

import json

payload = {
    "active": True,
    "verified": False,
    "name": "Ada",
}

encoded = json.dumps(payload)
decoded = json.loads(encoded)

print("Python object:", payload)
print("JSON text:", encoded)
print("Decoded object:", decoded)
print("Decoded active type:", type(decoded["active"]))

assert decoded == payload
assert isinstance(decoded["active"], bool)


# =============================================================================
# 52. BOOLEAN VALUES AND CONFIGURATION
# =============================================================================

section("52. BOOLEAN CONFIGURATION")

@dataclass
class FeatureConfig:
    caching_enabled: bool
    logging_enabled: bool
    debug_enabled: bool


config = FeatureConfig(
    caching_enabled=True,
    logging_enabled=True,
    debug_enabled=False,
)

print(config)

if config.caching_enabled:
    print("Caching is enabled.")

if config.debug_enabled:
    print("Debug mode is enabled.")
else:
    print("Debug mode is disabled.")


# =============================================================================
# 53. BOOLEAN DEFAULTS IN DATACLASSES
# =============================================================================

section("53. BOOLEAN DEFAULT VALUES")

@dataclass
class ServerConfig:
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    secure: bool = True


server_config = ServerConfig()
print(server_config)

# Boolean defaults should reflect the safest and most useful domain behavior.
# Security-sensitive features commonly benefit from secure-by-default design,
# although the correct default depends on the actual system.


# =============================================================================
# 54. BOOLEAN VALIDATION WITH ASSERT
# =============================================================================

section("54. ASSERTIONS AND BOOLEAN CONDITIONS")

value = 10

assert value > 0
assert isinstance(value > 0, bool)

# Assertions are useful for programmer assumptions and tests.
#
# They should not generally replace user-input validation because Python can
# disable assertions with optimization options.

print("Assertions passed.")


# =============================================================================
# 55. UNIT-STYLE TESTS FOR BOOLEAN LOGIC
# =============================================================================

section("55. TESTING BOOLEAN FUNCTIONS")

def is_adult(age: int) -> bool:
    return age >= 18


def run_boolean_tests() -> None:
    """Run deterministic tests for Boolean behavior."""
    assert is_adult(17) is False
    assert is_adult(18) is True
    assert is_adult(19) is True

    assert bool(0) is False
    assert bool(1) is True
    assert bool("") is False
    assert bool("x") is True
    assert bool([]) is False
    assert bool([0]) is True

    assert (True and True) is True
    assert (True and False) is False
    assert (False and True) is False
    assert (False and False) is False

    assert (True or True) is True
    assert (True or False) is True
    assert (False or True) is True
    assert (False or False) is False

    assert (not True) is False
    assert (not False) is True

    for a in (False, True):
        for b in (False, True):
            assert not (a and b) == ((not a) or (not b))
            assert not (a or b) == ((not a) and (not b))


run_boolean_tests()
print("Boolean unit tests passed.")


# =============================================================================
# 56. PROPERTY-STYLE TESTING OF BOOLEAN IDENTITIES
# =============================================================================

section("56. TESTING BOOLEAN IDENTITIES")

def verify_boolean_algebra() -> None:
    values = [False, True]

    for a in values:
        # Identity laws
        assert (a and True) == a
        assert (a or False) == a

        # Domination laws
        assert (a and False) is False
        assert (a or True) is True

        # Idempotent laws
        assert (a and a) == a
        assert (a or a) == a

        # Complement laws
        assert (a and not a) is False
        assert (a or not a) is True

        # Double negation
        assert not (not a) == a

    print("Boolean algebra identities verified.")


verify_boolean_algebra()


# =============================================================================
# 57. THREE-VALUED LOGIC WITH None
# =============================================================================

section("57. MODELING UNKNOWN VALUES")

# Python bool itself has two values, but applications sometimes need:
#
# True   = yes
# False  = no
# None   = unknown / not supplied
#
# This is not a third value of bool. It is a separate object participating in
# a larger application-level state model.

def approval_message(approved: Optional[bool]) -> str:
    if approved is None:
        return "Approval status is unknown."
    if approved:
        return "Approved."
    return "Rejected."


for approval in [True, False, None]:
    print(approval, "->", approval_message(approval))


# =============================================================================
# 58. EDGE CASE: EMPTY CONTAINERS
# =============================================================================

section("58. EMPTY VS NON-EMPTY CONTAINERS")

containers = [
    [],
    [False],
    [0],
    (),
    (False,),
    {},
    {"enabled": False},
    set(),
    {False},
]

for container in containers:
    print(f"{container!r:25} -> {bool(container)}")

# The container's own emptiness determines its truth value.
# The truthiness of its contents does not directly determine whether the
# container itself is truthy.


# =============================================================================
# 59. EDGE CASE: NAN
# =============================================================================

section("59. FLOAT NaN AND BOOLEAN LOGIC")

import math

nan = float("nan")

print("nan:", nan)
print("bool(nan):", bool(nan))
print("nan == nan:", nan == nan)
print("math.isnan(nan):", math.isnan(nan))

# NaN is a non-zero floating-point value, so it is truthy.
# Yet NaN is not equal to itself under IEEE floating-point semantics.

assert bool(nan) is True
assert math.isnan(nan)


# =============================================================================
# 60. EDGE CASE: NEGATIVE ZERO
# =============================================================================

section("60. NEGATIVE ZERO")

negative_zero = -0.0

print("negative_zero:", negative_zero)
print("bool(-0.0):", bool(negative_zero))
print("-0.0 == 0.0:", negative_zero == 0.0)

assert bool(negative_zero) is False
assert negative_zero == 0.0


# =============================================================================
# 61. EDGE CASE: COMPLEX NUMBERS
# =============================================================================

section("61. COMPLEX NUMBERS")

complex_zero = 0j
complex_nonzero = 1j

print("bool(0j):", bool(complex_zero))
print("bool(1j):", bool(complex_nonzero))

assert bool(0j) is False
assert bool(1j) is True


# =============================================================================
# 62. EDGE CASE: RANGE
# =============================================================================

section("62. RANGE TRUTHINESS")

print("bool(range(0)):", bool(range(0)))
print("bool(range(1)):", bool(range(1)))

# range(0) contains no values.
# range(1) contains one value: 0.

assert bool(range(0)) is False
assert bool(range(1)) is True


# =============================================================================
# 63. EDGE CASE: USER-DEFINED OBJECTS
# =============================================================================

section("63. DEFAULT TRUTHINESS OF OBJECTS")

class EmptyLookingObject:
    pass


object_instance = EmptyLookingObject()

print("bool(object_instance):", bool(object_instance))

# An ordinary user-defined object without __bool__ or __len__ is truthy.
#
# "Empty-looking" in a conceptual sense does not automatically mean falsy.


# =============================================================================
# 64. BOOLEAN LOGIC AND SIDE EFFECT ORDER
# =============================================================================

section("64. EVALUATION ORDER")

evaluation_log: list[str] = []


def record(name: str, result: bool) -> bool:
    evaluation_log.append(name)
    return result


evaluation_log.clear()
answer = record("A", False) and record("B", True)

print("and answer:", answer)
print("Evaluation order:", evaluation_log)

evaluation_log.clear()
answer = record("A", True) or record("B", False)

print("or answer:", answer)
print("Evaluation order:", evaluation_log)

# Python evaluates operands from left to right.
# Short-circuiting can prevent later operands from executing.


# =============================================================================
# 65. BOOLEAN EXPRESSIONS AND FUNCTION CALL COUNT
# =============================================================================

section("65. SHORT-CIRCUITING FOR EFFICIENCY")

call_count = 0


def expensive_check() -> bool:
    global call_count
    call_count += 1
    return True


false_condition = False

result = false_condition and expensive_check()

print("Result:", result)
print("expensive_check calls:", call_count)

assert call_count == 0

# Short-circuiting can improve performance by avoiding unnecessary work.
# It should first be used for correct logical guarding; performance is a
# secondary benefit.


# =============================================================================
# 66. COMMON MISTAKE: ASSIGNMENT VS COMPARISON
# =============================================================================

section("66. ASSIGNMENT VS COMPARISON")

# Python uses:
#
# =   assignment
# ==  equality comparison
#
# Example:
status = True
print("status:", status)

print("status == True:", status == True)

# Python does not allow assignment inside an ordinary expression in the same
# way some languages do. Assignment expressions use := and should be used
# carefully.

if (computed := 5) > 3:
    print("Computed value:", computed)

# The assignment expression stores a value and the comparison then produces
# a Boolean.


# =============================================================================
# 67. COMMON MISTAKE: bool() FOR TEXT PARSING
# =============================================================================

section("67. WHY bool(TEXT) IS NOT A BOOLEAN PARSER")

user_inputs = ["true", "false", "yes", "no", "0", "1", ""]

for text in user_inputs:
    print(f"bool({text!r}) -> {bool(text)}")

# Every non-empty string is truthy.
# Therefore:
#
# bool("false") -> True
#
# Use an explicit parser when text represents a Boolean configuration.


# =============================================================================
# 68. COMMON MISTAKE: USING is FOR VALUE COMPARISON
# =============================================================================

section("68. VALUE EQUALITY VS IDENTITY")

first = 1000
second = 1000

print("first == second:", first == second)
print("first is second:", first is second)

# Identity behavior for ordinary integers can vary due to implementation
# details such as object reuse. Never use "is" to test numeric equality.
#
# Always use == for value comparison.


# =============================================================================
# 69. COMMON MISTAKE: OVERLY COMPLEX CONDITIONS
# =============================================================================

section("69. SIMPLIFYING LOGICAL CONDITIONS")

# Harder to read:
complex_condition = (
    (age >= 18 and age <= 65)
    and (has_permission is True)
    and not (account_active is False)
)

print("Complex condition:", complex_condition)

# Clearer:
age_valid = 18 <= age <= 65
permission_granted = has_permission
account_is_active = account_active

clear_condition = age_valid and permission_granted and account_is_active

print("Clear condition:", clear_condition)


# =============================================================================
# 70. LOGICAL EQUIVALENCE
# =============================================================================

section("70. LOGICAL EQUIVALENCE")

def equivalent_expression(a: bool, b: bool) -> bool:
    """
    Demonstrate equivalence:
        A -> B
    is equivalent to:
        not A or B
    """
    implication = (not a) or b
    return implication


for a in boolean_values:
    for b in boolean_values:
        print(
            f"A={a}, B={b}, A->B={equivalent_expression(a, b)}"
        )


# =============================================================================
# 71. IMPLICATION AS A BUSINESS RULE
# =============================================================================

section("71. BOOLEAN IMPLICATION")

# Example rule:
#
# If a customer is a premium customer, they must have a verified account.
#
# Equivalent:
#
# not premium OR verified

def valid_customer_state(
    premium: bool,
    verified: bool,
) -> bool:
    return (not premium) or verified


print("Regular unverified:", valid_customer_state(False, False))
print("Premium verified:", valid_customer_state(True, True))
print("Premium unverified:", valid_customer_state(True, False))


# =============================================================================
# 72. BOOLEAN LOGIC WITH SET OPERATIONS
# =============================================================================

section("72. SET MEMBERSHIP RETURNS BOOLEAN")

roles = {"admin", "editor", "viewer"}

print('"admin" in roles:', "admin" in roles)
print('"guest" in roles:', "guest" in roles)

has_admin_role = "admin" in roles
has_guest_role = "guest" in roles

print(
    "Can manage:",
    has_admin_role or has_guest_role,
)

# Membership operators:
#   in
#   not in
#
# return Boolean values.

assert isinstance("admin" in roles, bool)
assert isinstance("guest" not in roles, bool)


# =============================================================================
# 73. IDENTITY CHECKS
# =============================================================================

section("73. IDENTITY EXPRESSIONS")

value = None

print("value is None:", value is None)
print("value is not None:", value is not None)

# Identity operators:
#   is
#   is not
#
# return Boolean values.


# =============================================================================
# 74. MEMBERSHIP CHECKS
# =============================================================================

section("74. MEMBERSHIP OPERATORS")

word = "Python"

print('"P" in word:', "P" in word)
print('"z" in word:', "z" in word)
print('"z" not in word:', "z" not in word)

numbers = {1, 2, 3}

print("2 in numbers:", 2 in numbers)
print("5 not in numbers:", 5 not in numbers)


# =============================================================================
# 75. BOOLEAN RETURN TYPES FROM OPERATORS
# =============================================================================

section("75. OPERATORS THAT PRODUCE BOOLEANS")

operations = {
    "10 == 10": 10 == 10,
    "10 != 5": 10 != 5,
    "10 < 20": 10 < 20,
    "10 <= 10": 10 <= 10,
    "20 > 10": 20 > 10,
    "20 >= 20": 20 >= 20,
    "'a' in 'cat'": "a" in "cat",
    "'x' not in 'cat'": "x" not in "cat",
    "None is None": None is None,
}

for expression, result in operations.items():
    print(expression, "->", result, type(result))


# =============================================================================
# 76. BOOLEAN LOGIC GATE CLASSES
# =============================================================================

section("76. LOGIC GATES")

class AndGate:
    @staticmethod
    def evaluate(a: bool, b: bool) -> bool:
        return a and b


class OrGate:
    @staticmethod
    def evaluate(a: bool, b: bool) -> bool:
        return a or b


class NotGate:
    @staticmethod
    def evaluate(a: bool) -> bool:
        return not a


class XorGate:
    @staticmethod
    def evaluate(a: bool, b: bool) -> bool:
        return a ^ b


for a in boolean_values:
    for b in boolean_values:
        print(
            f"A={a}, B={b}, "
            f"AND={AndGate.evaluate(a, b)}, "
            f"OR={OrGate.evaluate(a, b)}, "
            f"XOR={XorGate.evaluate(a, b)}"
        )

for a in boolean_values:
    print(f"NOT {a} = {NotGate.evaluate(a)}")


# =============================================================================
# 77. COMPOSING BOOLEAN LOGIC GATES
# =============================================================================

section("77. COMPOSITE LOGIC CIRCUIT")

def half_adder(a: bool, b: bool) -> tuple[bool, bool]:
    """
    A half adder produces:
        sum   = A XOR B
        carry = A AND B
    """
    return a ^ b, a and b


for a in boolean_values:
    for b in boolean_values:
        total, carry = half_adder(a, b)
        print(
            f"A={a}, B={b}, sum={total}, carry={carry}"
        )


# =============================================================================
# 78. BOOLEAN MASKING
# =============================================================================

section("78. BOOLEAN MASKING")

values = [10, 20, 30, 40, 50]
mask = [True, False, True, False, True]

selected = [
    value
    for value, include in zip(values, mask)
    if include
]

print("Values:", values)
print("Mask:", mask)
print("Selected:", selected)

# A Boolean mask represents a decision for each corresponding value.
# This idea appears in data processing, filtering, feature selection, and
# vectorized numerical systems.


# =============================================================================
# 79. BOOLEAN DECISION TABLE
# =============================================================================

section("79. DECISION TABLE")

def shipping_cost(
    order_total: float,
    is_member: bool,
    express: bool,
) -> float:
    """
    Educational decision table.

    Rules:
    - Express shipping costs 15.
    - Members with a standard order over 50 receive free shipping.
    - Everyone else pays 5.
    """
    if express:
        return 15.0

    if is_member and order_total >= 50:
        return 0.0

    return 5.0


test_orders = [
    (40, False, False),
    (60, False, False),
    (40, True, False),
    (60, True, False),
    (60, True, True),
]

for order_total, member, express in test_orders:
    print(
        order_total,
        member,
        express,
        "->",
        shipping_cost(order_total, member, express),
    )


# =============================================================================
# 80. BOOLEAN LOGIC AND SECURITY
# =============================================================================

section("80. BOOLEAN LOGIC IN SECURITY")

def authorize_request(
    authenticated: bool,
    account_active: bool,
    has_permission: bool,
) -> bool:
    """
    A request requires all three security conditions.

    This is only an educational Boolean model. Real authentication and
    authorization systems require secure identity verification, access
    control, auditing, and careful failure handling.
    """
    return authenticated and account_active and has_permission


print(
    "Authorized:",
    authorize_request(
        authenticated=True,
        account_active=True,
        has_permission=True,
    ),
)

print(
    "Authorized:",
    authorize_request(
        authenticated=True,
        account_active=False,
        has_permission=True,
    ),
)

# Security principle:
# Do not accidentally invert a security condition.
#
# For security-sensitive code, make conditions explicit and test both
# permitted and denied cases.


# =============================================================================
# 81. FAIL-CLOSED BOOLEAN DESIGN
# =============================================================================

section("81. FAIL-CLOSED DESIGN")

def access_allowed(
    authenticated: bool,
    permission_granted: bool,
) -> bool:
    """Access requires both authentication and permission."""
    return authenticated and permission_granted


print("Both true:", access_allowed(True, True))
print("Unauthenticated:", access_allowed(False, True))
print("No permission:", access_allowed(True, False))

# For access-control decisions, an explicit "all required conditions must be
# true" structure is easier to audit than a complicated mixture of positive
# and negative conditions.


# =============================================================================
# 82. BOOLEAN LOGIC AND ERROR HANDLING
# =============================================================================

section("82. BOOLEAN STATUS VS EXCEPTIONS")

def divide_safely(
    numerator: float,
    denominator: float,
) -> tuple[bool, Optional[float]]:
    """
    Return (success, result).

    This demonstrates one possible Boolean status pattern. In larger systems,
    exceptions or structured result types may communicate errors better.
    """
    if denominator == 0:
        return False, None

    return True, numerator / denominator


success, result = divide_safely(10, 2)
print("Success:", success, "Result:", result)

success, result = divide_safely(10, 0)
print("Success:", success, "Result:", result)


# =============================================================================
# 83. BOOLEAN RETURN VS EXCEPTION TRADE-OFF
# =============================================================================

section("83. BOOLEAN STATUS TRADE-OFF")

def validate_email_like(value: str) -> bool:
    """
    Simplified educational validation.

    Real email validation has more complicated requirements.
    """
    return "@" in value and "." in value.split("@")[-1]


for value in ["person@example.com", "invalid", "a@b"]:
    print(value, "->", validate_email_like(value))

# Returning bool works well when failure is an expected yes/no outcome.
#
# Raising an exception is often better when:
# - the input violates a programming contract,
# - the failure requires diagnostic information,
# - the caller cannot reasonably continue,
# - silently returning False could hide a programming error.


# =============================================================================
# 84. PERFORMANCE CONSIDERATIONS
# =============================================================================

section("84. PERFORMANCE OF BOOLEAN OPERATIONS")

# Boolean operations themselves are generally inexpensive.
# The important performance behavior is often short-circuiting.

large_data = list(range(100_000))

# any() stops as soon as it finds a truthy result.
contains_large_value = any(number > 99_990 for number in large_data)

print("Contains value greater than 99,990:", contains_large_value)

# all() stops as soon as it finds a falsy result.
all_positive = all(number >= 0 for number in large_data)

print("All values non-negative:", all_positive)

# Generator expressions avoid constructing an intermediate list.

# Less memory-efficient for very large sequences:
# any([condition(value) for value in data])
#
# More memory-efficient:
# any(condition(value) for value in data)


# =============================================================================
# 85. PERFORMANCE AND CONDITION ORDER
# =============================================================================

section("85. ORDERING SHORT-CIRCUITED CONDITIONS")

def cheap_check(value: int) -> bool:
    return value > 0


def expensive_check_for_demo(value: int) -> bool:
    # Simulate a non-trivial operation without external dependencies.
    total = 0
    for i in range(100):
        total += (value + i) % 7
    return total >= 0


value = -1

# The cheap condition fails, so the expensive condition is skipped.
result = cheap_check(value) and expensive_check_for_demo(value)

print("Condition result:", result)

# Put inexpensive and highly selective conditions early when doing so does not
# change the intended semantics.


# =============================================================================
# 86. BOOLEAN LOGIC AND DATABASE-STYLE CONDITIONS
# =============================================================================

section("86. COMBINING FILTER CONDITIONS")

records = [
    {"name": "A", "active": True, "score": 90},
    {"name": "B", "active": False, "score": 95},
    {"name": "C", "active": True, "score": 70},
    {"name": "D", "active": True, "score": 88},
]

selected_records = [
    record
    for record in records
    if record["active"] and record["score"] >= 80
]

print("Selected records:")
for record in selected_records:
    print(record)


# =============================================================================
# 87. BOOLEAN LOGIC AND VALIDATION RULES
# =============================================================================

section("87. MULTIPLE VALIDATION RULES")

@dataclass
class Registration:
    username: str
    password: str
    age: int


def validate_registration(registration: Registration) -> dict[str, bool]:
    """Return individual Boolean validation results."""
    username_valid = (
        bool(registration.username.strip())
        and len(registration.username) >= 3
    )

    password_valid = len(registration.password) >= 8
    age_valid = registration.age >= 18

    return {
        "username_valid": username_valid,
        "password_valid": password_valid,
        "age_valid": age_valid,
    }


registration = Registration("alice", "securepass", 25)
validation = validate_registration(registration)

print("Validation:", validation)
print("Registration valid:", all(validation.values()))


# =============================================================================
# 88. BOOLEAN AGGREGATION
# =============================================================================

section("88. AGGREGATING BOOLEAN RESULTS")

checks = [
    True,
    True,
    False,
    True,
]

print("All checks passed:", all(checks))
print("At least one check passed:", any(checks))
print("Passed count:", sum(checks))

# all(), any(), and sum() can express common aggregation operations cleanly.


# =============================================================================
# 89. BOOLEAN LOGIC WITH reduce
# =============================================================================

section("89. REDUCING BOOLEAN VALUES")

checks = [True, True, False, True]

all_using_reduce = reduce(and_, checks, True)
any_using_reduce = reduce(or_, checks, False)

print("All using reduce:", all_using_reduce)
print("Any using reduce:", any_using_reduce)

# Although reduce can express these operations, all() and any() are normally
# clearer and provide direct short-circuit semantics.


# =============================================================================
# 90. BOOLEAN XOR REDUCTION
# =============================================================================

section("90. XOR REDUCTION")

flags = [True, False, True, False, True]

xor_result = reduce(xor, flags, False)

print("Flags:", flags)
print("XOR reduction:", xor_result)

# XOR reduction can be useful when an odd/even number of True values matters.


# =============================================================================
# 91. BOOLEAN PARITY
# =============================================================================

section("91. BOOLEAN PARITY")

flags = [True, False, True, True]

true_count = sum(flags)
odd_parity = true_count % 2 == 1

print("True count:", true_count)
print("Odd parity:", odd_parity)

assert odd_parity == reduce(xor, flags, False)


# =============================================================================
# 92. BOOLEAN LOGIC AND BINARY REPRESENTATION
# =============================================================================

section("92. BOOLEAN VALUES AS BITS")

print("True as binary integer:", bin(True))
print("False as binary integer:", bin(False))

print("True as integer:", int(True))
print("False as integer:", int(False))

# bool -> int conversion is explicit and clear when numeric representation is
# actually intended.

assert int(True) == 1
assert int(False) == 0


# =============================================================================
# 93. EXPLICIT BOOLEAN CONVERSION
# =============================================================================

section("93. EXPLICIT CONVERSION")

values = [0, 1, "", "data", [], [1], None]

for value in values:
    boolean_value = bool(value)
    print(repr(value), "->", boolean_value)


# =============================================================================
# 94. BOOLEAN TYPE CHECKING
# =============================================================================

section("94. TYPE CHECKING")

values = [True, False, 1, 0, "True", None]

for value in values:
    print(
        repr(value),
        "is bool:",
        isinstance(value, bool),
    )

# isinstance(value, bool) distinguishes actual Boolean values from integers.
#
# Note:
# isinstance(True, int) is also True because bool subclasses int.


# =============================================================================
# 95. EXACT TYPE CHECKING
# =============================================================================

section("95. type(value) IS bool")

for value in [True, False, 1, 0]:
    print(
        repr(value),
        "type(value) is bool:",
        type(value) is bool,
    )

# type(value) is bool is stricter than isinstance(value, bool).
# Since bool is final as a practical built-in Boolean type, either can be
# useful depending on the API contract.


# =============================================================================
# 96. BOOLEAN API CONTRACTS
# =============================================================================

section("96. DESIGNING A BOOLEAN API")

def set_feature_enabled(enabled: bool) -> str:
    """
    Require a Boolean and return a descriptive result.

    Strict validation is appropriate when accepting external or loosely typed
    data that must conform to a Boolean contract.
    """
    if not isinstance(enabled, bool):
        raise TypeError("enabled must be a bool")

    return "Feature enabled." if enabled else "Feature disabled."


print(set_feature_enabled(True))
print(set_feature_enabled(False))

try:
    set_feature_enabled("true")  # type: ignore[arg-type]
except TypeError as error:
    print("Rejected:", error)


# =============================================================================
# 97. BOOLEAN FLAGS IN CLASS METHODS
# =============================================================================

section("97. BOOLEAN STATE TRANSITIONS")

class Lamp:
    def __init__(self) -> None:
        self.is_on = False

    def turn_on(self) -> None:
        self.is_on = True

    def turn_off(self) -> None:
        self.is_on = False

    def toggle(self) -> None:
        self.is_on = not self.is_on


lamp = Lamp()

print("Initially:", lamp.is_on)
lamp.turn_on()
print("After turn_on:", lamp.is_on)
lamp.toggle()
print("After toggle:", lamp.is_on)
lamp.turn_off()
print("After turn_off:", lamp.is_on)


# =============================================================================
# 98. BOOLEAN STATE MACHINES
# =============================================================================

section("98. BOOLEAN STATE MACHINE")

@dataclass
class Door:
    is_open: bool = False

    def open(self) -> None:
        self.is_open = True

    def close(self) -> None:
        self.is_open = False

    def can_enter(self) -> bool:
        return self.is_open


door = Door()

print("Can enter initially:", door.can_enter())
door.open()
print("Can enter after opening:", door.can_enter())
door.close()
print("Can enter after closing:", door.can_enter())


# =============================================================================
# 99. BOOLEAN CONDITIONS AND LOOP CONTROL
# =============================================================================

section("99. BOOLEAN CONDITIONS IN LOOPS")

numbers = [1, 2, 3, 4, 5]
index = 0

while index < len(numbers) and numbers[index] < 4:
    print("Processing:", numbers[index])
    index += 1

# The first condition protects the index access.
# The second condition controls the business rule.
#
# Short-circuiting makes this safe when index reaches len(numbers).


# =============================================================================
# 100. BOOLEAN FLAGS IN LOOPS
# =============================================================================

section("100. BOOLEAN LOOP FLAGS")

items = ["alpha", "beta", "target", "gamma"]
found = False

for item in items:
    if item == "target":
        found = True
        break

print("Found target:", found)

# In simple searches, next(), any(), or generator expressions can sometimes
# replace manual Boolean flags.

found_with_any = any(item == "target" for item in items)
print("Found with any():", found_with_any)


# =============================================================================
# 101. BOOLEAN LOGIC WITH DEFAULTS
# =============================================================================

section("101. DEFAULTING BOOLEAN VALUES")

def configure_logging(enabled: Optional[bool]) -> bool:
    """
    Preserve explicit True/False and use True only when the value is None.
    """
    if enabled is None:
        return True
    return enabled


for enabled in [True, False, None]:
    print(enabled, "->", configure_logging(enabled))


# =============================================================================
# 102. BOOLEAN LOGIC AND OPTIONAL VALUES
# =============================================================================

section("102. OPTIONAL BOOLEAN SEMANTICS")

def describe_feature(enabled: Optional[bool]) -> str:
    if enabled is True:
        return "Explicitly enabled."
    if enabled is False:
        return "Explicitly disabled."
    return "Not configured."


for enabled in [True, False, None]:
    print(enabled, "->", describe_feature(enabled))

# Comparing with "is True" and "is False" is useful here because the distinction
# between False and None is meaningful.


# =============================================================================
# 103. BOOLEAN LOGIC AND DATA QUALITY
# =============================================================================

section("103. DATA QUALITY CHECK")

dataset = [
    {"name": "Alice", "email": "alice@example.com", "active": True},
    {"name": "Bob", "email": "", "active": True},
    {"name": "Carol", "email": "carol@example.com", "active": False},
]

def record_is_valid(record: dict[str, Any]) -> bool:
    return (
        bool(record.get("name"))
        and bool(record.get("email"))
        and isinstance(record.get("active"), bool)
    )


for record in dataset:
    print(record, "->", record_is_valid(record))


# =============================================================================
# 104. SECURITY: NEVER CONFUSE TRUTHINESS WITH AUTHORIZATION
# =============================================================================

section("104. SECURITY DISTINCTION")

permission_value: Any = "false"

print("Raw permission value:", permission_value)
print("bool(permission_value):", bool(permission_value))

# This demonstrates why external authorization values must be validated and
# parsed correctly. A string such as "false" is truthy in Python.
#
# Never treat arbitrary external text as a Boolean merely by calling bool().


# =============================================================================
# 105. BOOLEAN LOGIC AND INPUT NORMALIZATION
# =============================================================================

section("105. NORMALIZATION BEFORE BOOLEAN INTERPRETATION")

def normalize_boolean_input(value: Any) -> bool:
    """
    Accept actual bools, integers 0/1, and common strings.

    Reject ambiguous values rather than guessing.
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, int) and value in (0, 1):
        return bool(value)

    if isinstance(value, str):
        return parse_boolean(value)

    raise TypeError(
        f"Unsupported Boolean input type: {type(value).__name__}"
    )


inputs: list[Any] = [
    True,
    False,
    1,
    0,
    "true",
    "false",
    "YES",
    "off",
]

for value in inputs:
    print(repr(value), "->", normalize_boolean_input(value))

for value in [2, -1, "maybe", None, [], 1.0]:
    try:
        normalize_boolean_input(value)
    except (TypeError, ValueError) as error:
        print(repr(value), "-> rejected:", error)


# =============================================================================
# 106. BOOLEAN LOGIC AND TYPE COERCION
# =============================================================================

section("106. TYPE COERCION CONSIDERATIONS")

print("bool(1.0):", bool(1.0))
print("bool(1):", bool(1))
print("bool(1 + 0j):", bool(1 + 0j))

# bool() checks truthiness, not whether the input is semantically Boolean.
#
# For domain validation, distinguish:
#
# conversion:
#     bool(value)
#
# validation:
#     isinstance(value, bool)


# =============================================================================
# 107. BOOLEAN EXPRESSIONS AND OPERATOR OVERLOADING
# =============================================================================

section("107. BOOLEAN OPERATORS VS CUSTOM OBJECTS")

# Python's "and", "or", and "not" are language-level operations based on
# truthiness and short-circuiting. They should not be confused with ordinary
# overloadable arithmetic operators.
#
# Custom classes can control truthiness through __bool__ or __len__.

class ValidationResult:
    def __init__(self, valid: bool, message: str) -> None:
        self.valid = valid
        self.message = message

    def __bool__(self) -> bool:
        return self.valid


validation_result = ValidationResult(True, "Valid input.")

if validation_result:
    print(validation_result.message)


# =============================================================================
# 108. BOOLEAN LOGIC AND RESULT OBJECTS
# =============================================================================

section("108. BOOLEAN-COERCIBLE RESULT OBJECT")

invalid_result = ValidationResult(False, "Input is invalid.")

print("bool(invalid_result):", bool(invalid_result))

if not invalid_result:
    print(invalid_result.message)

# This can create expressive APIs, but excessive custom truthiness may hide
# important state. Use it when the object's natural Boolean interpretation is
# obvious.


# =============================================================================
# 109. BOOLEAN LOGIC AND THREAD-SAFETY CONSIDERATIONS
# =============================================================================

section("109. BOOLEAN STATE AND CONCURRENCY")

# A Boolean assignment such as:
#
# self.running = True
#
# is simple, but correctness in concurrent programs depends on the entire
# state transition, not merely on the Boolean type.
#
# Example of a simple state model:

@dataclass
class WorkerState:
    running: bool = False
    stopped: bool = False


worker_state = WorkerState()

worker_state.running = True
worker_state.stopped = False

print(worker_state)

# In real concurrent systems, synchronization primitives such as locks,
# events, or atomic mechanisms may be needed. A Boolean field alone does not
# guarantee thread-safe coordination.


# =============================================================================
# 110. BOOLEAN LOGIC AND API SERIALIZATION
# =============================================================================

section("110. SERIALIZATION ROUND TRIP")

settings = {
    "dark_mode": True,
    "notifications": False,
}

serialized = json.dumps(settings)
restored = json.loads(serialized)

print("Serialized:", serialized)
print("Restored:", restored)

assert type(restored["dark_mode"]) is bool
assert type(restored["notifications"]) is bool


# =============================================================================
# 111. BOOLEAN LOGIC AND ENVIRONMENT VARIABLES
# =============================================================================

section("111. ENVIRONMENT VARIABLES ARE STRINGS")

import os

# Environment variables are textual values.
# This means:
#
# os.environ.get("DEBUG") == "false"
#
# is a string comparison, not a Boolean.

os.environ["DEMO_DEBUG"] = "false"

raw_debug = os.environ["DEMO_DEBUG"]

print("Raw environment value:", raw_debug)
print("bool(raw_debug):", bool(raw_debug))
print("Parsed environment value:", parse_boolean(raw_debug))

del os.environ["DEMO_DEBUG"]


# =============================================================================
# 112. BOOLEAN CONFIGURATION BEST PRACTICE
# =============================================================================

section("112. SAFE BOOLEAN CONFIGURATION")

def read_boolean_environment(
    environment: dict[str, str],
    key: str,
    default: bool,
) -> bool:
    raw_value = environment.get(key)

    if raw_value is None:
        return default

    try:
        return parse_boolean(raw_value)
    except ValueError as error:
        raise ValueError(
            f"Invalid Boolean configuration for {key!r}: {raw_value!r}"
        ) from error


environment = {
    "DEBUG": "false",
    "CACHE": "on",
}

print(read_boolean_environment(environment, "DEBUG", True))
print(read_boolean_environment(environment, "CACHE", False))
print(read_boolean_environment(environment, "MISSING", False))


# =============================================================================
# 113. BOOLEAN DECISION LOGGING
# =============================================================================

section("113. EXPLAINABLE BOOLEAN DECISIONS")

def access_decision(
    authenticated: bool,
    active: bool,
    permitted: bool,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []

    if not authenticated:
        reasons.append("User is not authenticated.")

    if not active:
        reasons.append("Account is inactive.")

    if not permitted:
        reasons.append("Required permission is missing.")

    return len(reasons) == 0, reasons


allowed, reasons = access_decision(True, False, True)

print("Allowed:", allowed)
print("Reasons:", reasons)

# A single Boolean can answer the final decision, while structured reasons can
# explain why the decision was False.


# =============================================================================
# 114. BOOLEAN CONDITIONS AND DEBUGGING
# =============================================================================

section("114. DEBUGGING COMPLEX CONDITIONS")

def order_eligible(
    amount: float,
    customer_active: bool,
    inventory_available: bool,
) -> bool:
    amount_valid = amount > 0
    return amount_valid and customer_active and inventory_available


amount = 100
customer_active = True
inventory_available = False

print("amount_valid:", amount > 0)
print("customer_active:", customer_active)
print("inventory_available:", inventory_available)
print(
    "order_eligible:",
    order_eligible(
        amount,
        customer_active,
        inventory_available,
    ),
)

# Breaking a condition into named Boolean components makes debugging easier.


# =============================================================================
# 115. BOOLEAN LOGIC AND DE MORGAN REFACTORING
# =============================================================================

section("115. DE MORGAN REFACTORING")

def original_rule(a: bool, b: bool) -> bool:
    return not (a and b)


def equivalent_rule(a: bool, b: bool) -> bool:
    return (not a) or (not b)


for a in boolean_values:
    for b in boolean_values:
        print(
            a,
            b,
            original_rule(a, b),
            equivalent_rule(a, b),
        )
        assert original_rule(a, b) == equivalent_rule(a, b)


# =============================================================================
# 116. BOOLEAN LOGIC AND DISTRIBUTION
# =============================================================================

section("116. DISTRIBUTIVE LAWS")

for a in boolean_values:
    for b in boolean_values:
        for c in boolean_values:
            assert a and (b or c) == ((a and b) or (a and c))
            assert a or (b and c) == ((a or b) and (a or c))

print("Distributive Boolean laws verified.")


# =============================================================================
# 117. BOOLEAN LOGIC AND ABSORPTION
# =============================================================================

section("117. ABSORPTION LAWS")

for a in boolean_values:
    for b in boolean_values:
        assert a or (a and b) == a
        assert a and (a or b) == a

print("Absorption laws verified.")


# =============================================================================
# 118. BOOLEAN LOGIC AND EXCLUSIVE CONDITIONS
# =============================================================================

section("118. EXACTLY-ONE CONDITION")

def exactly_one(a: bool, b: bool) -> bool:
    return a ^ b


for a in boolean_values:
    for b in boolean_values:
        print(a, b, "-> exactly one:", exactly_one(a, b))

# Exactly one of two conditions can be expressed with XOR.
#
# For more than two conditions, count the True values when the requirement is
# exactly one:

def exactly_one_true(flags: Iterable[bool]) -> bool:
    return sum(flags) == 1


print(exactly_one_true([False, True, False]))
print(exactly_one_true([True, True, False]))


# =============================================================================
# 119. AT LEAST ONE, ALL, EXACTLY ONE
# =============================================================================

section("119. COMMON BOOLEAN CARDINALITY RULES")

def at_least_one(flags: Iterable[bool]) -> bool:
    return any(flags)


def all_true(flags: Iterable[bool]) -> bool:
    return all(flags)


def exactly_one_true_count(flags: Iterable[bool]) -> bool:
    return sum(flags) == 1


flags = [False, True, False]

print("At least one:", at_least_one(flags))
print("All true:", all_true(flags))
print("Exactly one:", exactly_one_true_count(flags))


# =============================================================================
# 120. BOOLEAN LOGIC AND BUSINESS CARDINALITY
# =============================================================================

section("120. CARDINALITY-BASED BUSINESS RULE")

def meets_verification_requirement(
    email_verified: bool,
    phone_verified: bool,
    identity_verified: bool,
) -> bool:
    """
    Require at least two verification methods.
    """
    return sum(
        [email_verified, phone_verified, identity_verified]
    ) >= 2


cases = [
    (False, False, False),
    (True, False, False),
    (True, True, False),
    (True, True, True),
]

for case in cases:
    print(case, "->", meets_verification_requirement(*case))


# =============================================================================
# 121. BOOLEAN FLAGS AND COUPLING
# =============================================================================

section("121. TOO MANY BOOLEAN FLAGS")

@dataclass
class ApplicationFlags:
    debug: bool
    verbose: bool
    dry_run: bool
    test_mode: bool


flags = ApplicationFlags(
    debug=True,
    verbose=True,
    dry_run=False,
    test_mode=False,
)

print(flags)

# Many Boolean flags can create many combinations.
# Four independent flags already allow 2^4 = 16 combinations.
#
# As the number of independent Boolean dimensions grows, explicit modes,
# states, or configuration objects may be easier to reason about.


# =============================================================================
# 122. CALCULATING BOOLEAN STATE SPACE
# =============================================================================

section("122. BOOLEAN STATE SPACE")

def number_of_boolean_combinations(number_of_flags: int) -> int:
    if number_of_flags < 0:
        raise ValueError("number_of_flags cannot be negative")
    return 2 ** number_of_flags


for count in range(0, 7):
    print(
        f"{count} Boolean flags -> "
        f"{number_of_boolean_combinations(count)} combinations"
    )


# =============================================================================
# 123. BOOLEAN LOGIC AND TEST COVERAGE
# =============================================================================

section("123. TESTING BOOLEAN BRANCHES")

def shipping_discount(
    member: bool,
    amount: float,
) -> float:
    if member and amount >= 100:
        return 10.0
    return 0.0


test_cases = [
    (False, 50),
    (False, 100),
    (True, 50),
    (True, 100),
]

for member, amount in test_cases:
    result = shipping_discount(member, amount)
    print(member, amount, "->", result)

# When a condition contains multiple Boolean factors, test combinations that
# exercise each logical branch. For more complicated rules, decision tables
# can make the required test cases explicit.


# =============================================================================
# 124. BOOLEAN LOGIC AND EDGE-CASE TESTING
# =============================================================================

section("124. BOUNDARY TESTING")

ages = [17, 18, 19, 64, 65, 66]

for age in ages:
    print(age, "->", 18 <= age <= 65)

# Boundary values are particularly important for Boolean predicates involving
# >=, <=, >, and <.


# =============================================================================
# 125. COMMON BOOLEAN MISTAKES CHECKLIST IN CODE
# =============================================================================

section("125. COMMON MISTAKES DEMONSTRATED")

mistakes = {
    "bool('false') is True": bool("false") is True,
    "bool('0') is True": bool("0") is True,
    "bool([]) is False": bool([]) is False,
    "bool([False]) is True": bool([False]) is True,
    "True == 1": True == 1,
    "False == 0": False == 0,
}

for description, result in mistakes.items():
    print(description, "->", result)


# =============================================================================
# 126. ADVANCED: BOOLEAN LOGIC AS CALLABLE PREDICATES
# =============================================================================

section("126. COMPOSABLE PREDICATES")

Predicate = Callable[[Any], bool]


def and_predicates(
    first: Predicate,
    second: Predicate,
) -> Predicate:
    """Combine two predicates using logical AND."""
    return lambda value: first(value) and second(value)


def or_predicates(
    first: Predicate,
    second: Predicate,
) -> Predicate:
    """Combine two predicates using logical OR."""
    return lambda value: first(value) or second(value)


def not_predicate(
    predicate: Predicate,
) -> Predicate:
    """Negate a predicate."""
    return lambda value: not predicate(value)


is_positive_predicate = lambda value: value > 0
is_even_predicate = lambda value: value % 2 == 0

is_positive_even = and_predicates(
    is_positive_predicate,
    is_even_predicate,
)

is_not_positive = not_predicate(is_positive_predicate)

for number in range(-3, 5):
    print(
        number,
        "positive_even:",
        is_positive_even(number),
        "not_positive:",
        is_not_positive(number),
    )


# =============================================================================
# 127. ADVANCED: BOOLEAN RULE ENGINE
# =============================================================================

section("127. SIMPLE BOOLEAN RULE ENGINE")

@dataclass
class Rule:
    name: str
    predicate: Predicate


class RuleEngine:
    def __init__(self, rules: Iterable[Rule]) -> None:
        self.rules = list(rules)

    def evaluate(self, value: Any) -> dict[str, bool]:
        return {
            rule.name: bool(rule.predicate(value))
            for rule in self.rules
        }

    def passes_all(self, value: Any) -> bool:
        return all(
            rule.predicate(value)
            for rule in self.rules
        )


engine = RuleEngine(
    [
        Rule("positive", lambda value: value > 0),
        Rule("even", lambda value: value % 2 == 0),
        Rule("less_than_100", lambda value: value < 100),
    ]
)

for value in [2, 3, 102, -2]:
    print(value, "->", engine.evaluate(value))
    print("Passes all:", engine.passes_all(value))


# =============================================================================
# 128. ADVANCED: BOOLEAN EXPRESSION TREE
# =============================================================================

section("128. BOOLEAN EXPRESSION TREE")

class BooleanExpression:
    def evaluate(self) -> bool:
        raise NotImplementedError


@dataclass
class BooleanLiteral(BooleanExpression):
    value: bool

    def evaluate(self) -> bool:
        return self.value


@dataclass
class AndExpression(BooleanExpression):
    left: BooleanExpression
    right: BooleanExpression

    def evaluate(self) -> bool:
        return self.left.evaluate() and self.right.evaluate()


@dataclass
class OrExpression(BooleanExpression):
    left: BooleanExpression
    right: BooleanExpression

    def evaluate(self) -> bool:
        return self.left.evaluate() or self.right.evaluate()


@dataclass
class NotExpression(BooleanExpression):
    expression: BooleanExpression

    def evaluate(self) -> bool:
        return not self.expression.evaluate()


expression_tree = OrExpression(
    AndExpression(
        BooleanLiteral(True),
        BooleanLiteral(False),
    ),
    NotExpression(BooleanLiteral(False)),
)

print("Expression tree result:", expression_tree.evaluate())
assert expression_tree.evaluate() is True


# =============================================================================
# 129. ADVANCED: LAZY BOOLEAN EXPRESSION EVALUATION
# =============================================================================

section("129. LAZY EXPRESSION EVALUATION")

class LazyAnd:
    def __init__(
        self,
        left: Callable[[], bool],
        right: Callable[[], bool],
    ) -> None:
        self.left = left
        self.right = right

    def evaluate(self) -> bool:
        left_result = self.left()

        if not left_result:
            return False

        return self.right()


calls: list[str] = []


def first_condition() -> bool:
    calls.append("first")
    return False


def second_condition() -> bool:
    calls.append("second")
    return True


lazy_expression = LazyAnd(first_condition, second_condition)

print("Lazy result:", lazy_expression.evaluate())
print("Calls:", calls)

assert calls == ["first"]


# =============================================================================
# 130. ADVANCED: THREE-VALUED APPLICATION LOGIC
# =============================================================================

section("130. EXPLICIT UNKNOWN STATE")

class TriState(Enum):
    TRUE = True
    FALSE = False
    UNKNOWN = None


def tristate_not(value: TriState) -> TriState:
    if value is TriState.TRUE:
        return TriState.FALSE
    if value is TriState.FALSE:
        return TriState.TRUE
    return TriState.UNKNOWN


for state in TriState:
    print(state, "NOT ->", tristate_not(state))

# This is an application-level three-state model.
# It is not the same as Python's bool type.


# =============================================================================
# 131. ADVANCED: BOOLEAN ALGEBRA IMPLEMENTATION
# =============================================================================

section("131. BOOLEAN ALGEBRA HELPERS")

def boolean_and(*values: bool) -> bool:
    return all(values)


def boolean_or(*values: bool) -> bool:
    return any(values)


def boolean_not(value: bool) -> bool:
    return not value


print("boolean_and(True, True):", boolean_and(True, True))
print("boolean_and(True, False):", boolean_and(True, False))
print("boolean_or(False, True):", boolean_or(False, True))
print("boolean_or(False, False):", boolean_or(False, False))
print("boolean_not(True):", boolean_not(True))

# all() and any() naturally generalize AND and OR to arbitrary-length
# collections.


# =============================================================================
# 132. ADVANCED: TRUTHINESS PROTOCOL
# =============================================================================

section("132. PYTHON TRUTHINESS PROTOCOL")

# Python determines an object's truth value approximately as follows:
#
# 1. If __bool__ exists, call it.
# 2. Otherwise, if __len__ exists, use whether length is non-zero.
# 3. Otherwise, the object is truthy.
#
# The protocol is central to if, while, not, and, or, any(), all(), and bool().

class TruthinessDemo:
    def __init__(self, value: bool) -> None:
        self.value = value

    def __bool__(self) -> bool:
        return self.value


for value in [False, True]:
    demo = TruthinessDemo(value)
    print(value, "->", bool(demo))


# =============================================================================
# 133. ADVANCED: AMBIGUOUS TRUTHINESS
# =============================================================================

section("133. AVOID AMBIGUOUS TRUTHINESS")

class ExplicitState:
    def __init__(self, configured: bool, enabled: bool) -> None:
        self.configured = configured
        self.enabled = enabled

    def is_enabled(self) -> bool:
        return self.configured and self.enabled


states = [
    ExplicitState(False, False),
    ExplicitState(True, False),
    ExplicitState(True, True),
]

for state in states:
    print(
        "configured=", state.configured,
        "enabled=", state.enabled,
        "is_enabled=", state.is_enabled(),
    )

# An object can have multiple meaningful states. Defining __bool__ too
# aggressively may hide those distinctions. A named method can sometimes be
# clearer.


# =============================================================================
# 134. ADVANCED: BOOLEAN LOGIC AND IMMUTABILITY
# =============================================================================

section("134. BOOLEAN IMMUTABILITY")

flag = True
original_id = id(flag)

flag = False

print("Original True id:", original_id)
print("Current False id:", id(flag))

# Boolean objects themselves are immutable. Reassigning a variable changes
# which object the variable references; it does not mutate True into False.


# =============================================================================
# 135. ADVANCED: BOOLEAN MEMORY REPRESENTATION CONCEPT
# =============================================================================

section("135. BOOLEAN STORAGE CONCEPT")

# In Python's object model, True and False are full Python objects.
# Applications that store millions of Boolean values may use specialized
# representations such as packed bits or Boolean arrays to reduce memory.
#
# This script uses ordinary Python lists for educational clarity.

million_flags = [True] * 10_000
print("Number of flags:", len(million_flags))
print("First flag:", million_flags[0])


# =============================================================================
# 136. BOOLEAN PERFORMANCE: LIST VS GENERATOR
# =============================================================================

section("136. GENERATOR SHORT-CIRCUITING")

def positive(value: int) -> bool:
    return value > 0


values = [-10, -5, -1, 0, 1, 2]

list_result = any([positive(value) for value in values])
generator_result = any(positive(value) for value in values)

print("List result:", list_result)
print("Generator result:", generator_result)

# The generator version allows any() to stop without constructing the entire
# list. This can reduce memory usage and work for large or infinite iterables.


# =============================================================================
# 137. BOOLEAN LOGIC AND INFINITE ITERABLES
# =============================================================================

section("137. SHORT-CIRCUITING WITH POTENTIALLY LARGE ITERABLES")

def infinite_numbers():
    number = 0
    while True:
        yield number
        number += 1


# any() stops when the first number satisfying the condition is found.
first_large_exists = any(
    number >= 10
    for number in infinite_numbers()
)

print("An infinite sequence contains a number >= 10:", first_large_exists)

# Without short-circuiting, consuming an infinite iterable would never finish.


# =============================================================================
# 138. BOOLEAN LOGIC AND EXCEPTIONS IN GENERATORS
# =============================================================================

section("138. EXCEPTION-AWARE BOOLEAN CHECKS")

def safe_positive(value: Any) -> bool:
    try:
        return value > 0
    except TypeError:
        return False


mixed_values: list[Any] = [10, -2, "text", 5]

print([
    safe_positive(value)
    for value in mixed_values
])

# Exception handling can be appropriate when heterogeneous input is expected.
# If the input contract should guarantee numeric values, silently converting
# errors into False may hide data-quality problems.


# =============================================================================
# 139. BOOLEAN LOGIC AND DESIGN TRADE-OFFS
# =============================================================================

section("139. BOOLEAN DESIGN TRADE-OFFS")

trade_offs = {
    "Boolean flag": "Simple binary state; can become ambiguous when many flags interact.",
    "Enum": "Better for mutually exclusive multi-state conditions.",
    "None + bool": "Useful when explicit False differs from unknown/unconfigured.",
    "Predicate function": "Encapsulates reusable business rules.",
    "Exception": "Better for invalid program states than ordinary false outcomes.",
}

for concept, explanation in trade_offs.items():
    print(f"{concept}: {explanation}")


# =============================================================================
# 140. FINAL INTEGRATED EXAMPLE
# =============================================================================

section("140. INTEGRATED BOOLEAN-DRIVEN APPLICATION EXAMPLE")

@dataclass
class User:
    name: str
    age: int
    authenticated: bool
    active: bool
    email_verified: bool
    is_admin: bool


@dataclass
class Resource:
    name: str
    public: bool
    requires_admin: bool


def can_access(user: User, resource: Resource) -> bool:
    """
    Access policy:
    1. User must be authenticated.
    2. User must have an active account.
    3. Public resources can be accessed after authentication and activation.
    4. Private resources require email verification.
    5. Admin-only resources additionally require admin status.
    """
    authenticated_and_active = (
        user.authenticated and user.active
    )

    if not authenticated_and_active:
        return False

    if resource.requires_admin and not user.is_admin:
        return False

    if resource.public:
        return True

    return user.email_verified


users = [
    User(
        name="Alice",
        age=30,
        authenticated=True,
        active=True,
        email_verified=True,
        is_admin=False,
    ),
    User(
        name="Bob",
        age=25,
        authenticated=True,
        active=True,
        email_verified=False,
        is_admin=False,
    ),
    User(
        name="Carol",
        age=40,
        authenticated=True,
        active=True,
        email_verified=True,
        is_admin=True,
    ),
    User(
        name="Dave",
        age=22,
        authenticated=False,
        active=True,
        email_verified=True,
        is_admin=False,
    ),
]

resources = [
    Resource(
        name="Public Article",
        public=True,
        requires_admin=False,
    ),
    Resource(
        name="Private Report",
        public=False,
        requires_admin=False,
    ),
    Resource(
        name="Admin Console",
        public=False,
        requires_admin=True,
    ),
]

for user in users:
    for resource in resources:
        print(
            f"{user.name:5} -> {resource.name:15}: "
            f"{can_access(user, resource)}"
        )


# =============================================================================
# 141. FINAL BOOLEAN KNOWLEDGE CHECK
# =============================================================================

section("141. BOOLEAN KNOWLEDGE CHECK")

knowledge_checks = {
    "True is a bool": isinstance(True, bool),
    "False is a bool": isinstance(False, bool),
    "0 is falsy": not bool(0),
    "1 is truthy": bool(1),
    "empty string is falsy": not bool(""),
    "non-empty string is truthy": bool("x"),
    "empty list is falsy": not bool([]),
    "non-empty list is truthy": bool([False]),
    "not True is False": (not True) is False,
    "True and False is False": (True and False) is False,
    "True or False is True": (True or False) is True,
    "True XOR True is False": (True ^ True) is False,
    "True == 1": True == 1,
    "False == 0": False == 0,
    "None is not False": None is not False,
}

for concept, verified in knowledge_checks.items():
    print(f"{concept:40} -> {verified}")

assert all(knowledge_checks.values())


# =============================================================================
# 142. CONCISE REFERENCE
# =============================================================================

section("142. BOOLEAN QUICK REFERENCE")

quick_reference = {
    "Boolean literals": "True, False",
    "Boolean type": "bool",
    "Conversion": "bool(value)",
    "Negation": "not value",
    "Logical AND": "a and b",
    "Logical OR": "a or b",
    "Boolean XOR": "a ^ b",
    "Equality": "a == b",
    "Inequality": "a != b",
    "Less than": "a < b",
    "Less/equal": "a <= b",
    "Greater than": "a > b",
    "Greater/equal": "a >= b",
    "Identity": "a is b",
    "Non-identity": "a is not b",
    "Membership": "a in b",
    "Non-membership": "a not in b",
    "All conditions": "all(iterable)",
    "Any condition": "any(iterable)",
    "Custom truthiness": "__bool__() or __len__()",
}

for concept, syntax in quick_reference.items():
    print(f"{concept:25}: {syntax}")


# =============================================================================
# 143. FINAL VALIDATION
# =============================================================================

section("143. FINAL SELF-TEST")

def final_self_test() -> None:
    # Fundamentals
    assert True is True
    assert False is False
    assert isinstance(True, bool)
    assert isinstance(False, bool)

    # Truthiness
    assert bool(0) is False
    assert bool(1) is True
    assert bool("") is False
    assert bool("False") is True
    assert bool([]) is False
    assert bool([False]) is True
    assert bool(None) is False

    # Logical operations
    assert (True and True) is True
    assert (True and False) is False
    assert (False and True) is False
    assert (False and False) is False

    assert (True or True) is True
    assert (True or False) is True
    assert (False or True) is True
    assert (False or False) is False

    assert (not True) is False
    assert (not False) is True

    # Boolean/integer relationship
    assert True == 1
    assert False == 0

    # Comparison operators
    assert 5 > 2
    assert 5 >= 5
    assert 2 < 5
    assert 2 <= 2
    assert 5 != 4
    assert 5 == 5

    # Membership
    assert "a" in "cat"
    assert "z" not in "cat"

    # Identity
    none_value = None
    assert none_value is None

    # all/any
    assert all([True, True])
    assert not all([True, False])
    assert any([False, True])
    assert not any([False, False])

    # De Morgan
    for a in boolean_values:
        for b in boolean_values:
            assert not (a and b) == ((not a) or (not b))
            assert not (a or b) == ((not a) and (not b))

    # Chained comparison
    assert 18 <= 30 <= 65

    # Strict parser
    assert parse_boolean("true") is True
    assert parse_boolean("FALSE") is False

    # Custom truthiness
    assert bool(Account(10))
    assert not bool(Account(0))

    print("All final Boolean self-tests passed successfully.")


final_self_test()


# =============================================================================
# END OF STUDY SCRIPT
# =============================================================================

print("\nBoolean study script completed successfully.")
