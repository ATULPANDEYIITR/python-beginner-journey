"""
COMPARISON OPERATORS IN PYTHON
==============================

A comprehensive, self-contained tutorial from absolute beginner to advanced level.

This script demonstrates:

1. What comparison operators are
2. The six primary comparison operators
3. Equality and inequality
4. Greater-than and less-than comparisons
5. Greater-than-or-equal and less-than-or-equal
6. Numeric comparisons
7. String comparisons
8. Boolean comparisons
9. Character and Unicode ordering
10. Variables and expressions
11. Comparisons inside if, elif, and else
12. Comparisons inside loops
13. Combining comparisons with logical operators
14. Chained comparisons
15. Membership comparisons using in and not in
16. Identity comparisons using is and is not
17. Equality versus identity
18. None comparisons
19. Floating-point comparison problems
20. Decimal comparison
21. Comparing different numeric types
22. Boolean and integer relationships
23. Complex numbers and comparison limitations
24. Lists, tuples, dictionaries, and sets
25. Lexicographical sequence comparison
26. Custom objects and rich comparison methods
27. dataclass ordering
28. Sorting with comparison keys
29. min(), max(), and comparison-based selection
30. Validation
31. Guard conditions
32. Edge cases
33. Common mistakes
34. Debugging comparison expressions
35. Performance considerations
36. Best practices
37. Practical examples
38. Automated assertions and tests
39. Advanced comparison design
40. A final integrated example

The script uses only Python's standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from functools import total_ordering
from math import isclose, nan
from typing import Any


# =============================================================================
# 1. BASIC IDEA OF COMPARISON OPERATORS
# =============================================================================

print("=" * 80)
print("1. BASIC IDEA OF COMPARISON OPERATORS")
print("=" * 80)

"""
A comparison operator compares two values and normally produces a Boolean result:

    True
    False

Python's six primary comparison operators are:

    ==    equal to
    !=    not equal to
    >     greater than
    <     less than
    >=    greater than or equal to
    <=    less than or equal to

A comparison is an expression.

For example:

    10 > 5

evaluates to:

    True
"""

a = 10
b = 5

print("a =", a)
print("b =", b)
print("a == b:", a == b)
print("a != b:", a != b)
print("a > b :", a > b)
print("a < b :", a < b)
print("a >= b:", a >= b)
print("a <= b:", a <= b)


# =============================================================================
# 2. EQUALITY OPERATOR ==
# =============================================================================

print("\n" + "=" * 80)
print("2. EQUALITY OPERATOR ==")
print("=" * 80)

"""
The == operator asks:

"Do these two values compare as equal?"

It does not mean assignment.

Assignment:

    x = 10

Comparison:

    x == 10

The first stores a value.
The second checks a relationship.
"""

x = 25

print("x == 25:", x == 25)
print("x == 20:", x == 20)

name = "Atul"

print("name == 'Atul':", name == "Atul")
print("name == 'atul':", name == "atul")


# =============================================================================
# 3. INEQUALITY OPERATOR !=
# =============================================================================

print("\n" + "=" * 80)
print("3. INEQUALITY OPERATOR !=")
print("=" * 80)

"""
The != operator asks:

"Are these two values different?"

Examples:
"""

age = 25

print("age != 18:", age != 18)
print("age != 25:", age != 25)

status = "active"

print("status != 'inactive':", status != "inactive")


# =============================================================================
# 4. GREATER-THAN >
# =============================================================================

print("\n" + "=" * 80)
print("4. GREATER-THAN OPERATOR >")
print("=" * 80)

"""
The > operator is True only when the left operand is strictly greater
than the right operand.
"""

score = 85

print("score > 50 :", score > 50)
print("score > 85 :", score > 85)
print("score > 100:", score > 100)


# =============================================================================
# 5. LESS-THAN <
# =============================================================================

print("\n" + "=" * 80)
print("5. LESS-THAN OPERATOR <")
print("=" * 80)

"""
The < operator is True only when the left operand is strictly less
than the right operand.
"""

temperature = 18

print("temperature < 25:", temperature < 25)
print("temperature < 18:", temperature < 18)
print("temperature < 10:", temperature < 10)


# =============================================================================
# 6. GREATER-THAN-OR-EQUAL >=
# =============================================================================

print("\n" + "=" * 80)
print("6. GREATER-THAN-OR-EQUAL OPERATOR >=")
print("=" * 80)

"""
The >= operator allows equality.

    10 >= 10  -> True
    11 >= 10  -> True
     9 >= 10  -> False
"""

marks = 40

print("marks >= 40:", marks >= 40)
print("marks >= 41:", marks >= 41)


# =============================================================================
# 7. LESS-THAN-OR-EQUAL <=
# =============================================================================

print("\n" + "=" * 80)
print("7. LESS-THAN-OR-EQUAL OPERATOR <=")
print("=" * 80)

"""
The <= operator also allows equality.

    10 <= 10  -> True
     9 <= 10  -> True
    11 <= 10  -> False
"""

limit = 100

print("limit <= 100:", limit <= 100)
print("limit <= 99 :", limit <= 99)


# =============================================================================
# 8. COMPLETE COMPARISON TABLE
# =============================================================================

print("\n" + "=" * 80)
print("8. COMPLETE COMPARISON TABLE")
print("=" * 80)

left = 10
right = 20

comparison_results = {
    "10 == 20": left == right,
    "10 != 20": left != right,
    "10 > 20": left > right,
    "10 < 20": left < right,
    "10 >= 20": left >= right,
    "10 <= 20": left <= right,
}

for expression, result in comparison_results.items():
    print(f"{expression:<10} -> {result}")


# =============================================================================
# 9. COMPARISONS PRODUCE BOOLEAN VALUES
# =============================================================================

print("\n" + "=" * 80)
print("9. COMPARISONS PRODUCE BOOLEAN VALUES")
print("=" * 80)

result = 100 > 50

print("result:", result)
print("type(result):", type(result).__name__)

"""
A comparison can be stored in a variable.
That Boolean variable can then be used elsewhere.
"""

is_adult = age >= 18
print("is_adult:", is_adult)


# =============================================================================
# 10. NUMERIC COMPARISONS
# =============================================================================

print("\n" + "=" * 80)
print("10. NUMERIC COMPARISONS")
print("=" * 80)

"""
Integers and floating-point numbers can be compared normally.
"""

print("10 == 10:", 10 == 10)
print("10 == 10.0:", 10 == 10.0)
print("10.5 > 10:", 10.5 > 10)
print("-5 < 0:", -5 < 0)
print("0 == -0:", 0 == -0)

large_number = 10**100
print("large_number > 10:", large_number > 10)


# =============================================================================
# 11. NEGATIVE NUMBERS
# =============================================================================

print("\n" + "=" * 80)
print("11. NEGATIVE NUMBER COMPARISONS")
print("=" * 80)

"""
Negative numbers follow the ordinary mathematical ordering:

    -10 < -5 < 0 < 5 < 10
"""

numbers = [-10, -5, 0, 5, 10]

for number in numbers:
    print(f"{number:>4} < 0 -> {number < 0}")


# =============================================================================
# 12. STRING COMPARISONS
# =============================================================================

print("\n" + "=" * 80)
print("12. STRING COMPARISONS")
print("=" * 80)

"""
Strings can be compared.

String comparison is lexicographical.
Python compares characters according to their Unicode code points.

This is not the same as natural-language dictionary ordering in every
language.
"""

print("'apple' == 'apple':", "apple" == "apple")
print("'apple' == 'Apple':", "apple" == "Apple")
print("'apple' != 'orange':", "apple" != "orange")
print("'apple' < 'banana':", "apple" < "banana")
print("'zebra' > 'apple':", "zebra" > "apple")


# =============================================================================
# 13. CASE SENSITIVITY IN STRINGS
# =============================================================================

print("\n" + "=" * 80)
print("13. CASE SENSITIVITY")
print("=" * 80)

"""
String comparisons are case-sensitive.

For case-insensitive comparison, normalize the values first.
"""

first_name = "ATUL"
second_name = "atul"

print("Direct equality:", first_name == second_name)
print("Lowercase equality:", first_name.lower() == second_name.lower())

"""
For user-facing comparisons, casefold() is generally more robust than lower()
for Unicode-aware case-insensitive matching.
"""

german_a = "straße"
german_b = "STRASSE"

print("lower() comparison:", german_a.lower() == german_b.lower())
print("casefold() comparison:", german_a.casefold() == german_b.casefold())


# =============================================================================
# 14. CHARACTER AND UNICODE COMPARISONS
# =============================================================================

print("\n" + "=" * 80)
print("14. CHARACTER AND UNICODE COMPARISONS")
print("=" * 80)

"""
Characters are strings of length one.
Their ordering follows Unicode code points.

ord() exposes the numeric code point.
"""

characters = ["A", "B", "a", "b"]

for character in characters:
    print(f"{character!r}: Unicode code point = {ord(character)}")

print("'A' < 'a':", "A" < "a")
print("'a' < 'b':", "a" < "b")


# =============================================================================
# 15. COMPARISON INSIDE IF
# =============================================================================

print("\n" + "=" * 80)
print("15. COMPARISON INSIDE IF")
print("=" * 80)

account_balance = 7500

if account_balance > 0:
    print("The account has a positive balance.")

if account_balance == 7500:
    print("The balance is exactly 7,500.")


# =============================================================================
# 16. IF, ELIF, ELSE WITH COMPARISONS
# =============================================================================

print("\n" + "=" * 80)
print("16. IF, ELIF, ELSE")
print("=" * 80)

marks = 82

if marks >= 90:
    grade = "A"
elif marks >= 80:
    grade = "B"
elif marks >= 70:
    grade = "C"
elif marks >= 60:
    grade = "D"
else:
    grade = "F"

print("Marks:", marks)
print("Grade:", grade)


# =============================================================================
# 17. COMPARISONS INSIDE LOOPS
# =============================================================================

print("\n" + "=" * 80)
print("17. COMPARISONS INSIDE LOOPS")
print("=" * 80)

for number in range(1, 11):
    if number % 2 == 0:
        print(number, "is even")
    else:
        print(number, "is odd")


# =============================================================================
# 18. COMPARISON WITH EXPRESSIONS
# =============================================================================

print("\n" + "=" * 80)
print("18. COMPARISONS WITH EXPRESSIONS")
print("=" * 80)

price = 100
quantity = 3
total = price * quantity

print("Total:", total)
print("total > 250:", total > 250)
print("total == 300:", total == 300)


# =============================================================================
# 19. COMBINING COMPARISONS WITH and
# =============================================================================

print("\n" + "=" * 80)
print("19. COMBINING COMPARISONS WITH and")
print("=" * 80)

"""
and requires both conditions to be truthy.
"""

user_age = 25
has_id = True

allowed = user_age >= 18 and has_id

print("Age >= 18:", user_age >= 18)
print("Has ID:", has_id)
print("Allowed:", allowed)


# =============================================================================
# 20. COMBINING COMPARISONS WITH or
# =============================================================================

print("\n" + "=" * 80)
print("20. COMBINING COMPARISONS WITH or")
print("=" * 80)

"""
or requires at least one condition to be truthy.
"""

is_weekend = False
is_holiday = True

can_rest = is_weekend or is_holiday

print("Weekend:", is_weekend)
print("Holiday:", is_holiday)
print("Can rest:", can_rest)


# =============================================================================
# 21. NOT WITH COMPARISONS
# =============================================================================

print("\n" + "=" * 80)
print("21. NOT WITH COMPARISONS")
print("=" * 80)

is_locked = False

print("is_locked:", is_locked)
print("not is_locked:", not is_locked)

if not is_locked:
    print("The system is currently unlocked.")


# =============================================================================
# 22. OPERATOR PRECEDENCE
# =============================================================================

print("\n" + "=" * 80)
print("22. OPERATOR PRECEDENCE")
print("=" * 80)

"""
Parentheses should be used when they make the intended logic clearer.

Comparison operators have higher precedence than not, and and/or have
their own precedence levels.

For complex conditions, explicit parentheses reduce ambiguity.
"""

age = 25
income = 50000
has_job = True

condition = (age >= 18 and income >= 30000) or has_job

print("condition:", condition)


# =============================================================================
# 23. CHAINED COMPARISONS
# =============================================================================

print("\n" + "=" * 80)
print("23. CHAINED COMPARISONS")
print("=" * 80)

"""
Python allows:

    10 < x < 20

This means:

    10 < x and x < 20

The chained form is often clearer.
"""

x = 15

print("10 < x < 20:", 10 < x < 20)
print("Equivalent expression:", 10 < x and x < 20)

temperature = 25
print("18 <= temperature <= 30:", 18 <= temperature <= 30)


# =============================================================================
# 24. CHAINED COMPARISONS WITH DIFFERENT OPERATORS
# =============================================================================

print("\n" + "=" * 80)
print("24. MIXED CHAINED COMPARISONS")
print("=" * 80)

value = 10

print("0 < value <= 10:", 0 < value <= 10)
print("value != 5 != 20:", value != 5 != 20)

"""
Chained comparisons should be used only when their meaning is obvious.
"""


# =============================================================================
# 25. IMPORTANT DIFFERENCE: CHAINING IS NOT NESTED LOGIC
# =============================================================================

print("\n" + "=" * 80)
print("25. CHAINING VERSUS NESTED LOGIC")
print("=" * 80)

a = 5
b = 10
c = 15

print("a < b < c:", a < b < c)
print("(a < b) < c:", (a < b) < c)

"""
The second expression compares the Boolean result of (a < b) with c.

Because True behaves numerically like 1 in many contexts:

    (a < b) < c

becomes:

    True < 15

which is True.

This is syntactically valid but usually expresses a different idea.
"""


# =============================================================================
# 26. SHORT-CIRCUITING WITH and
# =============================================================================

print("\n" + "=" * 80)
print("26. SHORT-CIRCUITING WITH and")
print("=" * 80)

"""
Python evaluates and from left to right.

If the first operand is false, the second operand may not be evaluated.

This is useful for protecting operations from invalid input.
"""

text = ""

safe_condition = text != "" and text[0] == "A"

print("text:", repr(text))
print("safe_condition:", safe_condition)


# =============================================================================
# 27. SHORT-CIRCUITING WITH or
# =============================================================================

print("\n" + "=" * 80)
print("27. SHORT-CIRCUITING WITH or")
print("=" * 80)

"""
With or, if the first operand is truthy, Python can avoid evaluating the
second operand.
"""

username = ""

display_name = username or "Guest"

print("display_name:", display_name)


# =============================================================================
# 28. MEMBERSHIP COMPARISONS
# =============================================================================

print("\n" + "=" * 80)
print("28. MEMBERSHIP OPERATORS")
print("=" * 80)

"""
Membership operators are:

    in
    not in

They test whether an object contains another value.

Although they are not among the six ordering/equality comparison operators,
they are closely related to conditional comparison logic.
"""

languages = ["Python", "SQL", "Java", "C++"]

print("'Python' in languages:", "Python" in languages)
print("'Rust' in languages:", "Rust" in languages)
print("'Rust' not in languages:", "Rust" not in languages)


# =============================================================================
# 29. MEMBERSHIP IN STRINGS
# =============================================================================

print("\n" + "=" * 80)
print("29. MEMBERSHIP IN STRINGS")
print("=" * 80)

email = "student@example.com"

print("'@' in email:", "@" in email)
print("'.com' in email:", ".com" in email)
print("'gmail' in email:", "gmail" in email)


# =============================================================================
# 30. MEMBERSHIP IN DICTIONARIES
# =============================================================================

print("\n" + "=" * 80)
print("30. MEMBERSHIP IN DICTIONARIES")
print("=" * 80)

student = {
    "name": "Atul",
    "age": 25,
    "course": "Computer Science",
}

print("'name' in student:", "name" in student)
print("'Atul' in student:", "Atul" in student)

"""
For dictionaries, in normally checks keys, not values.
"""


# =============================================================================
# 31. IDENTITY OPERATORS
# =============================================================================

print("\n" + "=" * 80)
print("31. IDENTITY OPERATORS: is AND is not")
print("=" * 80)

"""
Identity operators are:

    is
    is not

They ask whether two references point to the same object.

Equality asks whether values compare equal.

Identity asks whether the objects themselves are the same object.
"""

list_a = [1, 2, 3]
list_b = [1, 2, 3]
list_c = list_a

print("list_a == list_b:", list_a == list_b)
print("list_a is list_b:", list_a is list_b)
print("list_a == list_c:", list_a == list_c)
print("list_a is list_c:", list_a is list_c)


# =============================================================================
# 32. EQUALITY VERSUS IDENTITY
# =============================================================================

print("\n" + "=" * 80)
print("32. EQUALITY VERSUS IDENTITY")
print("=" * 80)

"""
Use == when you care about value equality.

Use is when you care about object identity.

The classic example is None.
"""

value = None

print("value == None:", value == None)
print("value is None:", value is None)
print("value is not None:", value is not None)

"""
Best practice:

    if value is None:

rather than:

    if value == None:
"""


# =============================================================================
# 33. NONE AND SENTINEL VALUES
# =============================================================================

print("\n" + "=" * 80)
print("33. NONE AND SENTINEL VALUES")
print("=" * 80)

def find_user(users: list[dict[str, Any]], user_id: int) -> dict[str, Any] | None:
    for user in users:
        if user["id"] == user_id:
            return user
    return None


users = [
    {"id": 1, "name": "A"},
    {"id": 2, "name": "B"},
]

found_user = find_user(users, 99)

if found_user is None:
    print("User was not found.")
else:
    print("User:", found_user)


# =============================================================================
# 34. BOOLEAN VALUES AND COMPARISONS
# =============================================================================

print("\n" + "=" * 80)
print("34. BOOLEAN VALUES AND COMPARISONS")
print("=" * 80)

"""
bool is a subclass of int in Python.

Therefore:

    True == 1
    False == 0

are True.

This behavior is useful to understand, but relying on it for application
logic can make code less clear.
"""

print("True == 1:", True == 1)
print("False == 0:", False == 0)
print("True < 2:", True < 2)
print("False < 1:", False < 1)

print("type(True).__mro__:", [cls.__name__ for cls in type(True).__mro__])


# =============================================================================
# 35. NUMERIC TYPE COMPARISONS
# =============================================================================

print("\n" + "=" * 80)
print("35. COMPARING DIFFERENT NUMERIC TYPES")
print("=" * 80)

print("1 == 1.0:", 1 == 1.0)
print("1 == Decimal('1'):", 1 == Decimal("1"))
print("1.5 == Decimal('1.5'):", 1.5 == Decimal("1.5"))

"""
Python supports comparisons among many numeric types.

Precision and conversion behavior should still be considered carefully
when exact financial or decimal arithmetic matters.
"""


# =============================================================================
# 36. FLOATING-POINT COMPARISON PROBLEM
# =============================================================================

print("\n" + "=" * 80)
print("36. FLOATING-POINT COMPARISON")
print("=" * 80)

"""
Binary floating-point numbers cannot represent every decimal fraction
exactly.

For example:
"""

calculation = 0.1 + 0.2

print("0.1 + 0.2:", calculation)
print("(0.1 + 0.2) == 0.3:", calculation == 0.3)

"""
For approximate numerical work, use math.isclose().
"""

print("isclose(0.1 + 0.2, 0.3):", isclose(0.1 + 0.2, 0.3))


# =============================================================================
# 37. ABSOLUTE AND RELATIVE TOLERANCE
# =============================================================================

print("\n" + "=" * 80)
print("37. FLOATING-POINT TOLERANCE")
print("=" * 80)

measurement_a = 100.000001
measurement_b = 100.000002

print(
    "Default isclose:",
    isclose(measurement_a, measurement_b),
)

print(
    "Custom absolute tolerance:",
    isclose(measurement_a, measurement_b, abs_tol=0.00001),
)

"""
rel_tol is useful when the magnitude of values matters.
abs_tol is important when comparing values near zero.
"""


# =============================================================================
# 38. DECIMAL FOR EXACT DECIMAL ARITHMETIC
# =============================================================================

print("\n" + "=" * 80)
print("38. DECIMAL COMPARISON")
print("=" * 80)

"""
Decimal is appropriate for applications where decimal representation
and predictable decimal arithmetic matter, such as many financial
calculations.

Construct Decimal from strings when exact decimal input is intended.
"""

decimal_a = Decimal("0.1")
decimal_b = Decimal("0.2")
decimal_c = Decimal("0.3")

print("Decimal('0.1') + Decimal('0.2') == Decimal('0.3'):")
print(decimal_a + decimal_b == decimal_c)


# =============================================================================
# 39. NAN AND UNUSUAL FLOATING-POINT COMPARISONS
# =============================================================================

print("\n" + "=" * 80)
print("39. NaN COMPARISON")
print("=" * 80)

"""
NaN means "Not a Number".

IEEE floating-point NaN has unusual comparison behavior.

For a NaN value:

    nan == nan -> False
    nan < value -> False
    nan > value -> False

Use math.isnan() to detect NaN.
"""

not_a_number = nan

print("nan == nan:", not_a_number == not_a_number)
print("nan != nan:", not_a_number != not_a_number)
print("nan < 10:", not_a_number < 10)
print("nan > 10:", not_a_number > 10)
print("isnan(nan):", not_a_number != not_a_number)


# =============================================================================
# 40. COMPLEX NUMBERS
# =============================================================================

print("\n" + "=" * 80)
print("40. COMPLEX NUMBER COMPARISONS")
print("=" * 80)

"""
Complex numbers support equality and inequality comparisons:

    == 
    !=

They do not support ordinary ordering:

    <
    >
    <=
    >=

because complex numbers do not have a natural total ordering in Python.
"""

complex_a = 2 + 3j
complex_b = 2 + 3j

print("complex_a == complex_b:", complex_a == complex_b)
print("complex_a != complex_b:", complex_a != complex_b)

try:
    print(complex_a < complex_b)
except TypeError as error:
    print("Ordering complex numbers raises:", type(error).__name__)


# =============================================================================
# 41. LIST COMPARISONS
# =============================================================================

print("\n" + "=" * 80)
print("41. LIST COMPARISONS")
print("=" * 80)

"""
Lists support equality and lexicographical ordering.

Python compares corresponding elements from left to right.
"""

list_1 = [1, 2, 3]
list_2 = [1, 2, 3]
list_3 = [1, 2, 4]

print("list_1 == list_2:", list_1 == list_2)
print("list_1 < list_3:", list_1 < list_3)
print("list_3 > list_1:", list_3 > list_1)


# =============================================================================
# 42. LEXICOGRAPHICAL LIST COMPARISON
# =============================================================================

print("\n" + "=" * 80)
print("42. LEXICOGRAPHICAL SEQUENCE COMPARISON")
print("=" * 80)

"""
Comparison stops at the first pair of elements that differs.

For:

    [1, 100] < [2, 0]

Python compares 1 with 2 first.
Since 1 < 2, it does not need to compare 100 with 0.
"""

print("[1, 100] < [2, 0]:", [1, 100] < [2, 0])
print("[1, 100] > [1, 50]:", [1, 100] > [1, 50])
print("[1] < [1, 0]:", [1] < [1, 0])


# =============================================================================
# 43. TUPLE COMPARISONS
# =============================================================================

print("\n" + "=" * 80)
print("43. TUPLE COMPARISONS")
print("=" * 80)

"""
Tuples use lexicographical comparison as well.
"""

tuple_a = (2026, 9, 11)
tuple_b = (2026, 10, 1)

print("tuple_a < tuple_b:", tuple_a < tuple_b)


# =============================================================================
# 44. MIXED SEQUENCE ELEMENT TYPES
# =============================================================================

print("\n" + "=" * 80)
print("44. INCOMPARABLE SEQUENCE ELEMENTS")
print("=" * 80)

"""
If Python reaches elements that cannot be ordered against one another,
an ordering comparison can raise TypeError.

Equality is different and can still return False.
"""

mixed_a = [1, "two"]
mixed_b = [1, "three"]

print("mixed_a == mixed_b:", mixed_a == mixed_b)

try:
    print("mixed_a < mixed_b:", mixed_a < mixed_b)
except TypeError as error:
    print("Ordering error:", type(error).__name__)


# =============================================================================
# 45. DICTIONARY COMPARISONS
# =============================================================================

print("\n" + "=" * 80)
print("45. DICTIONARY COMPARISONS")
print("=" * 80)

"""
Dictionaries support equality comparison.

They do not support ordering comparisons such as < and >.
"""

dictionary_a = {"a": 1, "b": 2}
dictionary_b = {"b": 2, "a": 1}

print("dictionary_a == dictionary_b:", dictionary_a == dictionary_b)

try:
    print(dictionary_a < dictionary_b)
except TypeError as error:
    print("Dictionary ordering raises:", type(error).__name__)


# =============================================================================
# 46. SET COMPARISONS
# =============================================================================

print("\n" + "=" * 80)
print("46. SET COMPARISONS")
print("=" * 80)

"""
Sets have special comparison semantics.

    ==       equal sets
    !=       different sets
    <        proper subset
    <=       subset
    >        proper superset
    >=       superset
"""

set_a = {1, 2}
set_b = {1, 2, 3}

print("set_a == set_b:", set_a == set_b)
print("set_a < set_b :", set_a < set_b)
print("set_a <= set_b:", set_a <= set_b)
print("set_b > set_a :", set_b > set_a)
print("set_b >= set_a:", set_b >= set_a)


# =============================================================================
# 47. EMPTY SET AND SUBSET RELATIONSHIPS
# =============================================================================

print("\n" + "=" * 80)
print("47. EMPTY SET COMPARISON")
print("=" * 80)

empty_set = set()

print("empty_set <= {1, 2}:", empty_set <= {1, 2})
print("empty_set < {1, 2} :", empty_set < {1, 2})
print("empty_set == set():", empty_set == set())


# =============================================================================
# 48. USER INPUT AND COMPARISON
# =============================================================================

print("\n" + "=" * 80)
print("48. USER INPUT AND COMPARISON")
print("=" * 80)

"""
input() always returns a string.

Therefore numeric input must normally be converted before numeric comparison.

Example:

    raw_age = input(...)
    age = int(raw_age)

This demonstration uses fixed input so that the script remains
non-interactive and fully executable.
"""

raw_age = "25"
converted_age = int(raw_age)

print("raw_age type:", type(raw_age).__name__)
print("converted_age type:", type(converted_age).__name__)
print("converted_age >= 18:", converted_age >= 18)


# =============================================================================
# 49. VALIDATION USING COMPARISON OPERATORS
# =============================================================================

print("\n" + "=" * 80)
print("49. INPUT VALIDATION")
print("=" * 80)

def validate_percentage(value: float) -> bool:
    """Return True when value is within the inclusive 0-100 range."""
    return 0 <= value <= 100


test_percentages = [-5, 0, 50, 100, 105]

for percentage in test_percentages:
    print(
        f"{percentage:>4}: "
        f"valid={validate_percentage(percentage)}"
    )


# =============================================================================
# 50. RANGE VALIDATION
# =============================================================================

print("\n" + "=" * 80)
print("50. RANGE VALIDATION")
print("=" * 80)

def is_valid_age(age: int) -> bool:
    """Validate an age using an inclusive practical range."""
    return 0 <= age <= 120


for candidate_age in [-1, 0, 18, 120, 121]:
    print(
        f"age={candidate_age:>3}, "
        f"valid={is_valid_age(candidate_age)}"
    )


# =============================================================================
# 51. LOGIN-STYLE CONDITIONAL LOGIC
# =============================================================================

print("\n" + "=" * 80)
print("51. PRACTICAL LOGIN CONDITION")
print("=" * 80)

stored_username = "atul"
stored_password = "secret"

entered_username = "atul"
entered_password = "secret"

credentials_match = (
    entered_username == stored_username
    and entered_password == stored_password
)

print("Credentials match:", credentials_match)


# =============================================================================
# 52. PASSWORD VALIDATION
# =============================================================================

print("\n" + "=" * 80)
print("52. PASSWORD VALIDATION")
print("=" * 80)

def password_is_valid(password: str) -> bool:
    """
    Demonstrate basic comparison-based password rules.

    Real authentication systems should not store plaintext passwords.
    """
    return (
        len(password) >= 8
        and password != "password"
        and password != "12345678"
    )


password_candidates = [
    "short",
    "password",
    "12345678",
    "securePass9",
]

for password in password_candidates:
    print(
        f"{password!r:<18} -> "
        f"{password_is_valid(password)}"
    )


# =============================================================================
# 53. COMPARISON WITH CASE NORMALIZATION
# =============================================================================

print("\n" + "=" * 80)
print("53. NORMALIZED STRING COMPARISON")
print("=" * 80)

def same_username(first: str, second: str) -> bool:
    return first.casefold() == second.casefold()


print(same_username("Atul", "atul"))
print(same_username("USER", "user"))


# =============================================================================
# 54. COMPARING DATES
# =============================================================================

print("\n" + "=" * 80)
print("54. DATE COMPARISONS")
print("=" * 80)

from datetime import date, datetime, timedelta

today = date(2026, 9, 11)
deadline = date(2026, 9, 30)

print("today < deadline:", today < deadline)
print("today == deadline:", today == deadline)
print("today <= deadline:", today <= deadline)

if today <= deadline:
    print("The deadline has not passed.")


# =============================================================================
# 55. COMPARING DATETIME VALUES
# =============================================================================

print("\n" + "=" * 80)
print("55. DATETIME COMPARISONS")
print("=" * 80)

start_time = datetime(2026, 9, 11, 9, 0)
end_time = datetime(2026, 9, 11, 17, 0)

print("start_time < end_time:", start_time < end_time)

working_duration = end_time - start_time
print("working duration:", working_duration)


# =============================================================================
# 56. PRACTICAL BUSINESS METRIC COMPARISON
# =============================================================================

print("\n" + "=" * 80)
print("56. BUSINESS METRIC COMPARISON")
print("=" * 80)

revenue = 1_250_000
cost = 900_000
profit = revenue - cost
profit_margin = profit / revenue

print("Revenue:", revenue)
print("Cost:", cost)
print("Profit:", profit)
print("Profit margin:", profit_margin)

if profit > 0:
    print("The business is profitable.")

if profit_margin >= 0.20:
    print("Profit margin is at least 20%.")


# =============================================================================
# 57. COMPARING SCORES
# =============================================================================

print("\n" + "=" * 80)
print("57. SCORE COMPARISON")
print("=" * 80)

scores = {
    "Alice": 91,
    "Bob": 84,
    "Charlie": 91,
}

for name, score in scores.items():
    if score >= 90:
        print(name, "has an excellent score.")


# =============================================================================
# 58. min() AND max()
# =============================================================================

print("\n" + "=" * 80)
print("58. min() AND max()")
print("=" * 80)

values = [45, 12, 78, 23, 91]

print("Minimum:", min(values))
print("Maximum:", max(values))

"""
min() and max() use ordering relationships internally.
"""


# =============================================================================
# 59. COMPARING OBJECTS USING key=
# =============================================================================

print("\n" + "=" * 80)
print("59. SORTING WITH key=")
print("=" * 80)

employees = [
    {"name": "A", "salary": 70000},
    {"name": "B", "salary": 50000},
    {"name": "C", "salary": 90000},
]

sorted_by_salary = sorted(employees, key=lambda employee: employee["salary"])

for employee in sorted_by_salary:
    print(employee)


# =============================================================================
# 60. KEY FUNCTIONS VERSUS DIRECT OBJECT COMPARISON
# =============================================================================

print("\n" + "=" * 80)
print("60. KEY FUNCTIONS")
print("=" * 80)

"""
A key function transforms each object into a value that can be compared.

This is usually preferable to defining complicated comparison logic
when sorting based on one or more straightforward attributes.
"""

sorted_by_name = sorted(employees, key=lambda employee: employee["name"])

for employee in sorted_by_name:
    print(employee)


# =============================================================================
# 61. MULTIPLE SORTING CRITERIA
# =============================================================================

print("\n" + "=" * 80)
print("61. MULTIPLE SORTING CRITERIA")
print("=" * 80)

people = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 30},
]

sorted_people = sorted(
    people,
    key=lambda person: (person["age"], person["name"]),
)

for person in sorted_people:
    print(person)


# =============================================================================
# 62. CUSTOM CLASS WITH __eq__ AND __lt__
# =============================================================================

print("\n" + "=" * 80)
print("62. CUSTOM COMPARISON METHODS")
print("=" * 80)

@dataclass
class Product:
    name: str
    price: float

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Product):
            return NotImplemented
        return self.price == other.price

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Product):
            return NotImplemented
        return self.price < other.price


product_a = Product("Keyboard", 2500)
product_b = Product("Mouse", 1500)

print("product_a == product_b:", product_a == product_b)
print("product_a < product_b:", product_a < product_b)


# =============================================================================
# 63. WHY NOTIMPLEMENTED MATTERS
# =============================================================================

print("\n" + "=" * 80)
print("63. NotImplemented IN COMPARISON METHODS")
print("=" * 80)

"""
When a custom comparison method receives an unsupported operand type,
returning NotImplemented tells Python that this implementation does not
know how to perform that comparison.

It is generally preferable to returning False for every unsupported type,
because Python may then try the reflected operation or ultimately raise
an appropriate TypeError.
"""

try:
    print(product_a < 100)
except TypeError as error:
    print("Unsupported comparison:", type(error).__name__)


# =============================================================================
# 64. total_ordering
# =============================================================================

print("\n" + "=" * 80)
print("64. functools.total_ordering")
print("=" * 80)

@total_ordering
class Student:
    def __init__(self, name: str, score: float) -> None:
        self.name = name
        self.score = score

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Student):
            return NotImplemented
        return self.score == other.score

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Student):
            return NotImplemented
        return self.score < other.score

    def __repr__(self) -> str:
        return f"Student(name={self.name!r}, score={self.score!r})"


student_a = Student("Alice", 85)
student_b = Student("Bob", 90)

print("student_a < student_b:", student_a < student_b)
print("student_a <= student_b:", student_a <= student_b)
print("student_a > student_b:", student_a > student_b)
print("student_a >= student_b:", student_a >= student_b)


# =============================================================================
# 65. DATACLASS ORDERING
# =============================================================================

print("\n" + "=" * 80)
print("65. DATACLASS ORDERING")
print("=" * 80)

@dataclass(order=True)
class RankedPlayer:
    score: int
    name: str


player_a = RankedPlayer(90, "Alice")
player_b = RankedPlayer(80, "Bob")

print("player_a > player_b:", player_a > player_b)
print("player_a == player_b:", player_a == player_b)

"""
With order=True, dataclasses generate ordering methods based on fields
in their declared order.

This is convenient but requires deliberate field design because the
field order affects comparison semantics.
"""


# =============================================================================
# 66. CUSTOM COMPARISON WITH MULTIPLE ATTRIBUTES
# =============================================================================

print("\n" + "=" * 80)
print("66. MULTI-ATTRIBUTE COMPARISON")
print("=" * 80)

@dataclass
class Candidate:
    technical_score: int
    communication_score: int
    name: str

    def ranking_key(self) -> tuple[int, int, str]:
        return (
            self.technical_score,
            self.communication_score,
            self.name,
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Candidate):
            return NotImplemented
        return self.ranking_key() < other.ranking_key()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Candidate):
            return NotImplemented
        return self.ranking_key() == other.ranking_key()


candidate_a = Candidate(90, 80, "Alice")
candidate_b = Candidate(90, 75, "Bob")

print("candidate_a > candidate_b:", candidate_a > candidate_b)


# =============================================================================
# 67. CUSTOM COMPARISON SHOULD REFLECT DOMAIN MEANING
# =============================================================================

print("\n" + "=" * 80)
print("67. DOMAIN-SPECIFIC COMPARISON")
print("=" * 80)

@dataclass
class Transaction:
    amount: float
    status: str

    def is_high_value(self, threshold: float = 100000) -> bool:
        return self.amount >= threshold

    def is_completed(self) -> bool:
        return self.status == "completed"


transaction = Transaction(150000, "completed")

print("High value:", transaction.is_high_value())
print("Completed:", transaction.is_completed())


# =============================================================================
# 68. COMPARISON WITH TYPE VALIDATION
# =============================================================================

print("\n" + "=" * 80)
print("68. TYPE VALIDATION")
print("=" * 80)

def compare_numbers(a: float, b: float) -> str:
    if not isinstance(a, (int, float)) or isinstance(a, bool):
        raise TypeError("a must be a real numeric value")
    if not isinstance(b, (int, float)) or isinstance(b, bool):
        raise TypeError("b must be a real numeric value")

    if a > b:
        return "a is greater than b"
    if a < b:
        return "a is less than b"
    return "a and b are equal"


print(compare_numbers(10, 5))
print(compare_numbers(5, 10))
print(compare_numbers(10, 10))


# =============================================================================
# 69. COMPARISON OF OPTIONAL VALUES
# =============================================================================

print("\n" + "=" * 80)
print("69. OPTIONAL VALUES")
print("=" * 80)

optional_score: int | None = None

if optional_score is None:
    print("Score has not been provided.")
elif optional_score >= 50:
    print("Passing score.")
else:
    print("Failing score.")


# =============================================================================
# 70. GUARD CLAUSES
# =============================================================================

print("\n" + "=" * 80)
print("70. GUARD CLAUSES")
print("=" * 80)

def calculate_discount(price: float, customer_age: int) -> float:
    if price < 0:
        raise ValueError("Price cannot be negative")

    if customer_age < 0:
        raise ValueError("Age cannot be negative")

    if customer_age >= 60:
        return price * 0.90

    return price


print("Discounted price:", calculate_discount(1000, 65))
print("Regular price:", calculate_discount(1000, 30))


# =============================================================================
# 71. COMMON MISTAKE: = VERSUS ==
# =============================================================================

print("\n" + "=" * 80)
print("71. COMMON MISTAKE: = VERSUS ==")
print("=" * 80)

"""
The assignment operator is:

    =

The equality operator is:

    ==

This is invalid:

    if x = 10:

Python raises a SyntaxError.

Correct:

    if x == 10:
"""

value = 10

if value == 10:
    print("Correct equality comparison.")


# =============================================================================
# 72. COMMON MISTAKE: USING is FOR VALUE COMPARISON
# =============================================================================

print("\n" + "=" * 80)
print("72. COMMON MISTAKE: is VERSUS ==")
print("=" * 80)

first = [1, 2, 3]
second = [1, 2, 3]

print("Value equality:", first == second)
print("Object identity:", first is second)

"""
Do not rely on object interning or implementation-specific identity behavior
for ordinary value comparison.
"""


# =============================================================================
# 73. COMMON MISTAKE: FLOAT EQUALITY
# =============================================================================

print("\n" + "=" * 80)
print("73. COMMON MISTAKE: FLOAT EQUALITY")
print("=" * 80)

expected = 0.3
actual = 0.1 + 0.2

if isclose(actual, expected, rel_tol=1e-9, abs_tol=0.0):
    print("Values are approximately equal.")
else:
    print("Values are materially different.")


# =============================================================================
# 74. COMMON MISTAKE: COMPARING INPUT WITHOUT CONVERSION
# =============================================================================

print("\n" + "=" * 80)
print("74. INPUT CONVERSION")
print("=" * 80)

user_input = "100"

print("user_input == '100':", user_input == "100")

try:
    print(user_input > 50)
except TypeError as error:
    print("String versus integer ordering error:", type(error).__name__)

numeric_input = int(user_input)
print("numeric_input > 50:", numeric_input > 50)


# =============================================================================
# 75. COMMON MISTAKE: HARD-TO-READ CONDITIONS
# =============================================================================

print("\n" + "=" * 80)
print("75. READABLE CONDITIONAL LOGIC")
print("=" * 80)

age = 25
income = 60000
credit_score = 750

eligible = (
    age >= 18
    and income >= 30000
    and credit_score >= 700
)

print("Loan eligibility:", eligible)


# =============================================================================
# 76. COMPARISON AND TRUTHINESS
# =============================================================================

print("\n" + "=" * 80)
print("76. TRUTHINESS")
print("=" * 80)

"""
Conditions do not always need an explicit comparison.

Instead of:

    if items != []:

prefer:

    if items:

Likewise:

    if not items:

for an empty collection.
"""

items = [1, 2, 3]

if items:
    print("The collection is non-empty.")

if items != []:
    print("The collection is also non-empty.")


# =============================================================================
# 77. EXPLICIT BOOLEAN COMPARISON
# =============================================================================

print("\n" + "=" * 80)
print("77. BOOLEAN COMPARISON STYLE")
print("=" * 80)

is_active = True

if is_active:
    print("Preferred style: direct Boolean condition.")

if is_active == True:
    print("Explicit comparison also works, but is usually unnecessary.")


# =============================================================================
# 78. COMPARING ENUM VALUES
# =============================================================================

print("\n" + "=" * 80)
print("78. ENUM COMPARISON")
print("=" * 80)

from enum import Enum


class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


order_status = OrderStatus.COMPLETED

print("order_status == OrderStatus.COMPLETED:",
      order_status == OrderStatus.COMPLETED)

if order_status is OrderStatus.COMPLETED:
    print("Order is completed.")

"""
Enum members are singleton-like named members, so identity checks between
members are appropriate. Equality is also meaningful.
"""


# =============================================================================
# 79. COMPARISON OF VERSION-LIKE STRINGS
# =============================================================================

print("\n" + "=" * 80)
print("79. VERSION-LIKE STRING COMPARISON")
print("=" * 80)

"""
A common trap:

    "10.0" < "2.0"

String comparison sees "1" before "2", so this can produce a result that
does not represent numeric version ordering.

For structured versions, parse components first.
"""

print("'10.0' < '2.0':", "10.0" < "2.0")

version_a = tuple(map(int, "10.0".split(".")))
version_b = tuple(map(int, "2.0".split(".")))

print("Parsed version comparison:", version_a > version_b)


# =============================================================================
# 80. COMPARING PHONE-LIKE OR IDENTIFIER STRINGS
# =============================================================================

print("\n" + "=" * 80)
print("80. NORMALIZING IDENTIFIERS")
print("=" * 80)

identifier_a = " ABC-123 "
identifier_b = "abc-123"

normalized_a = identifier_a.strip().casefold()
normalized_b = identifier_b.strip().casefold()

print("Identifiers equal after normalization:",
      normalized_a == normalized_b)


# =============================================================================
# 81. COMPARISON FUNCTIONS
# =============================================================================

print("\n" + "=" * 80)
print("81. REUSABLE COMPARISON FUNCTIONS")
print("=" * 80)

def compare_scores(score_a: float, score_b: float) -> int:
    """
    Return:
        1  if score_a is greater
        0  if equal
       -1  if score_a is smaller
    """
    if score_a > score_b:
        return 1
    if score_a < score_b:
        return -1
    return 0


print(compare_scores(90, 80))
print(compare_scores(80, 90))
print(compare_scores(80, 80))


# =============================================================================
# 82. THREE-WAY COMPARISON
# =============================================================================

print("\n" + "=" * 80)
print("82. THREE-WAY COMPARISON")
print("=" * 80)

def three_way_compare(a: Any, b: Any) -> int:
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


for pair in [(1, 2), (2, 1), (5, 5)]:
    print(pair, "->", three_way_compare(*pair))


# =============================================================================
# 83. COMPARISON AND FILTERING
# =============================================================================

print("\n" + "=" * 80)
print("83. FILTERING WITH COMPARISONS")
print("=" * 80)

sales = [12000, 45000, 18000, 76000, 32000]

high_value_sales = [
    sale for sale in sales
    if sale >= 30000
]

print("Sales:", sales)
print("Sales >= 30,000:", high_value_sales)


# =============================================================================
# 84. MULTIPLE COMPARISONS IN LIST COMPREHENSIONS
# =============================================================================

print("\n" + "=" * 80)
print("84. MULTIPLE CONDITIONS")
print("=" * 80)

numbers = list(range(1, 21))

selected = [
    number
    for number in numbers
    if number >= 5 and number <= 15 and number % 2 == 0
]

print("Selected:", selected)


# =============================================================================
# 85. FILTERING DICTIONARY RECORDS
# =============================================================================

print("\n" + "=" * 80)
print("85. FILTERING RECORDS")
print("=" * 80)

customers = [
    {"name": "A", "age": 22, "spend": 5000},
    {"name": "B", "age": 35, "spend": 25000},
    {"name": "C", "age": 42, "spend": 40000},
]

qualified_customers = [
    customer
    for customer in customers
    if customer["age"] >= 30
    and customer["spend"] >= 20000
]

for customer in qualified_customers:
    print(customer)


# =============================================================================
# 86. COMPARISON WITH CONDITIONAL EXPRESSIONS
# =============================================================================

print("\n" + "=" * 80)
print("86. CONDITIONAL EXPRESSIONS")
print("=" * 80)

score = 75

result = "Pass" if score >= 40 else "Fail"

print("Result:", result)


# =============================================================================
# 87. EDGE CASE: EQUAL BOUNDARIES
# =============================================================================

print("\n" + "=" * 80)
print("87. BOUNDARY CONDITIONS")
print("=" * 80)

minimum = 10
maximum = 20

for value in [9, 10, 11, 19, 20, 21]:
    print(
        f"value={value:>2}: "
        f"inside={minimum <= value <= maximum}"
    )


# =============================================================================
# 88. INCLUSIVE VERSUS EXCLUSIVE BOUNDS
# =============================================================================

print("\n" + "=" * 80)
print("88. INCLUSIVE VERSUS EXCLUSIVE BOUNDS")
print("=" * 80)

value = 10

print("Inclusive lower bound:", value >= 10)
print("Exclusive lower bound:", value > 10)

"""
Carefully choose:

    >= and <=

when boundaries should be included, and:

    > and <

when boundaries should be excluded.
"""


# =============================================================================
# 89. EXCEPTION HANDLING AROUND COMPARISONS
# =============================================================================

print("\n" + "=" * 80)
print("89. ERROR HANDLING")
print("=" * 80)

def safe_numeric_comparison(left: Any, right: Any) -> bool | None:
    try:
        return left > right
    except TypeError:
        return None


print("10 > 5:", safe_numeric_comparison(10, 5))
print("'10' > 5:", safe_numeric_comparison("10", 5))


# =============================================================================
# 90. DEBUGGING COMPARISON EXPRESSIONS
# =============================================================================

print("\n" + "=" * 80)
print("90. DEBUGGING COMPARISONS")
print("=" * 80)

left_value = "100"
right_value = 100

print("left_value:", repr(left_value))
print("right_value:", repr(right_value))
print("left type:", type(left_value).__name__)
print("right type:", type(right_value).__name__)

print("Equality:", left_value == right_value)

"""
When a comparison produces an unexpected result, inspect:

1. The values
2. Their types
3. Whitespace
4. Case
5. Numeric precision
6. None values
7. Object identity
8. Conversion or normalization
9. Custom comparison methods
"""


# =============================================================================
# 91. ASSERTIONS FOR COMPARISON LOGIC
# =============================================================================

print("\n" + "=" * 80)
print("91. ASSERTIONS")
print("=" * 80)

assert 10 == 10
assert 10 != 20
assert 20 > 10
assert 10 < 20
assert 20 >= 20
assert 10 <= 20

assert 0 <= 50 <= 100

print("Basic comparison assertions passed.")


# =============================================================================
# 92. TESTING A VALIDATION FUNCTION
# =============================================================================

print("\n" + "=" * 80)
print("92. TESTING VALIDATION")
print("=" * 80)

def is_valid_discount(discount: float) -> bool:
    return 0 <= discount <= 100


validation_cases = {
    -1: False,
    0: True,
    10: True,
    100: True,
    101: False,
}

for input_value, expected in validation_cases.items():
    actual = is_valid_discount(input_value)
    assert actual == expected
    print(
        f"discount={input_value:>3}: "
        f"actual={actual}, expected={expected}"
    )


# =============================================================================
# 93. PERFORMANCE: SHORT-CIRCUITING
# =============================================================================

print("\n" + "=" * 80)
print("93. PERFORMANCE AND SHORT-CIRCUITING")
print("=" * 80)

"""
Comparison operations are generally inexpensive.

For compound conditions, order can matter because and/or short-circuit.

Put inexpensive and highly selective checks early when that improves
clarity and avoids unnecessary work.

The following function avoids indexing when the string is empty.
"""

def starts_with_a(text: str) -> bool:
    return bool(text) and text[0].lower() == "a"


for text in ["Atul", "", "Python"]:
    print(repr(text), "->", starts_with_a(text))


# =============================================================================
# 94. PERFORMANCE: EXPENSIVE FUNCTION CALLS
# =============================================================================

print("\n" + "=" * 80)
print("94. AVOIDING UNNECESSARY WORK")
print("=" * 80)

def expensive_check() -> bool:
    print("expensive_check() executed")
    return True


print("Case 1:")
result = False and expensive_check()
print("Result:", result)

print("\nCase 2:")
result = True or expensive_check()
print("Result:", result)


# =============================================================================
# 95. COMPARISON SORTING COMPLEXITY
# =============================================================================

print("\n" + "=" * 80)
print("95. COMPARISON-BASED SORTING")
print("=" * 80)

"""
Python's sorted() and list.sort() use Timsort.

The exact number of comparisons depends on the data.

For ordinary use, rely on Python's optimized sorting implementation
rather than implementing a sorting algorithm unnecessarily.
"""

unsorted_values = [9, 3, 7, 1, 5]

print("Before:", unsorted_values)
print("After :", sorted(unsorted_values))


# =============================================================================
# 96. STABLE SORTING AND COMPARISON KEYS
# =============================================================================

print("\n" + "=" * 80)
print("96. STABLE SORTING")
print("=" * 80)

records = [
    ("A", 80),
    ("B", 90),
    ("C", 80),
    ("D", 90),
]

sorted_records = sorted(records, key=lambda record: record[1])

print("Sorted records:", sorted_records)

"""
Python sorting is stable.

Records with equal keys preserve their original relative order.
"""


# =============================================================================
# 97. REVERSE ORDER
# =============================================================================

print("\n" + "=" * 80)
print("97. REVERSE COMPARISON ORDER")
print("=" * 80)

numbers = [5, 1, 9, 3]

print("Ascending :", sorted(numbers))
print("Descending:", sorted(numbers, reverse=True))


# =============================================================================
# 98. COMPARISON OF CUSTOM OBJECTS USING KEY
# =============================================================================

print("\n" + "=" * 80)
print("98. OBJECT SORTING WITH KEY")
print("=" * 80)

students = [
    Student("Alice", 85),
    Student("Bob", 95),
    Student("Charlie", 75),
]

sorted_students = sorted(students, key=lambda student: student.score)

for student in sorted_students:
    print(student)


# =============================================================================
# 99. COMPARISON CONTRACTS
# =============================================================================

print("\n" + "=" * 80)
print("99. COMPARISON CONTRACTS")
print("=" * 80)

"""
A well-designed ordering should be consistent.

Important mathematical-style properties include:

Reflexivity for equality:
    a == a

Antisymmetry for a partial/order relation:
    if a <= b and b <= a, then a == b

Transitivity:
    if a < b and b < c, then a < c

A custom class with inconsistent comparison methods can cause surprising
sorting and ordering behavior.

Python does not automatically prove that a custom comparison implementation
satisfies these properties.
"""

assert 5 == 5
assert 5 < 10 and 10 < 20 and 5 < 20

print("Basic comparison consistency examples passed.")


# =============================================================================
# 100. PARTIAL ORDERING VERSUS TOTAL ORDERING
# =============================================================================

print("\n" + "=" * 80)
print("100. PARTIAL VERSUS TOTAL ORDERING")
print("=" * 80)

"""
A total ordering allows every pair of values to be meaningfully ordered.

Some domains have only partial ordering.

Examples include:
    - sets under subset relations
    - complex numbers, which do not support ordinary < and >
    - domain objects where some records are incomparable

A comparison design should match the mathematical and business meaning
of the domain.
"""

set_x = {1, 2}
set_y = {3, 4}

print("set_x <= set_y:", set_x <= set_y)
print("set_y <= set_x:", set_y <= set_x)

"""
Both are False.

This does not mean one set is "less valuable" than the other.
It means neither set is a subset of the other.
"""


# =============================================================================
# 101. COMPARISON AND SECURITY
# =============================================================================

print("\n" + "=" * 80)
print("101. SECURITY CONSIDERATIONS")
print("=" * 80)

"""
Comparison logic can affect security-sensitive decisions.

Examples:

    - authorization checks
    - access thresholds
    - expiration checks
    - transaction limits
    - input validation
    - password policy validation
    - feature access

For secrets such as passwords or cryptographic signatures, ordinary == may
leak information through timing differences in some contexts.

Security-sensitive secret comparison should use an appropriate constant-time
comparison function, such as hmac.compare_digest(), rather than assuming
ordinary equality is suitable.
"""

import hmac

provided_token = "abc123"
expected_token = "abc123"

print(
    "Constant-time-style token comparison:",
    hmac.compare_digest(provided_token, expected_token),
)


# =============================================================================
# 102. COMPARISON AND AUTHORIZATION
# =============================================================================

print("\n" + "=" * 80)
print("102. AUTHORIZATION THRESHOLD")
print("=" * 80)

user_role = "admin"

if user_role == "admin":
    print("Administrative operation allowed.")
else:
    print("Administrative operation denied.")


# =============================================================================
# 103. COMPARISON AND RATE LIMITING
# =============================================================================

print("\n" + "=" * 80)
print("103. LIMIT CHECK")
print("=" * 80)

request_count = 95
request_limit = 100

if request_count >= request_limit:
    print("Rate limit reached.")
else:
    print("Request permitted.")


# =============================================================================
# 104. COMPARISON AND FINANCE
# =============================================================================

print("\n" + "=" * 80)
print("104. FINANCIAL THRESHOLD")
print("=" * 80)

investment = 500000
minimum_investment = 250000

if investment >= minimum_investment:
    print("Investment meets the minimum requirement.")


# =============================================================================
# 105. COMPARISON AND STATISTICS
# =============================================================================

print("\n" + "=" * 80)
print("105. STATISTICAL THRESHOLD")
print("=" * 80)

scores = [40, 55, 70, 85, 90]
threshold = 60

above_threshold = [
    score for score in scores
    if score >= threshold
]

print("Scores:", scores)
print("Scores >= threshold:", above_threshold)


# =============================================================================
# 106. COMPARISON AND MACHINE LEARNING METRICS
# =============================================================================

print("\n" + "=" * 80)
print("106. MACHINE LEARNING METRIC THRESHOLD")
print("=" * 80)

accuracy = 0.94
minimum_accuracy = 0.90

if accuracy >= minimum_accuracy:
    print("Model meets the minimum accuracy requirement.")
else:
    print("Model does not meet the minimum accuracy requirement.")


# =============================================================================
# 107. COMPARISON AND TEMPERATURE CLASSIFICATION
# =============================================================================

print("\n" + "=" * 80)
print("107. TEMPERATURE CLASSIFICATION")
print("=" * 80)

def classify_temperature(celsius: float) -> str:
    if celsius < 0:
        return "freezing"
    if celsius < 15:
        return "cold"
    if celsius < 30:
        return "moderate"
    return "hot"


for temperature in [-5, 0, 10, 20, 30, 40]:
    print(temperature, "->", classify_temperature(temperature))


# =============================================================================
# 108. COMPARISON AND AGE CLASSIFICATION
# =============================================================================

print("\n" + "=" * 80)
print("108. AGE CLASSIFICATION")
print("=" * 80)

def classify_age(age: int) -> str:
    if age < 0:
        return "invalid"
    if age < 13:
        return "child"
    if age < 18:
        return "teenager"
    if age < 60:
        return "adult"
    return "senior"


for candidate_age in [-1, 5, 15, 30, 60, 80]:
    print(candidate_age, "->", classify_age(candidate_age))


# =============================================================================
# 109. COMPARISON AND PASSWORD LENGTH
# =============================================================================

print("\n" + "=" * 80)
print("109. PASSWORD LENGTH THRESHOLD")
print("=" * 80)

password = "ExamplePassword"

print("Length:", len(password))
print("Length >= 8:", len(password) >= 8)
print("Length >= 12:", len(password) >= 12)


# =============================================================================
# 110. COMPARISON OF PATH OBJECTS
# =============================================================================

print("\n" + "=" * 80)
print("110. PATH COMPARISON")
print("=" * 80)

from pathlib import Path

path_a = Path("data/file.txt")
path_b = Path("data/file.txt")

print("path_a == path_b:", path_a == path_b)

"""
Path equality compares the represented path values.

Do not confuse path equality with whether two paths refer to the same
physical filesystem object. For that question, filesystem-aware methods
such as Path.samefile() may be appropriate when the paths exist.
"""


# =============================================================================
# 111. COMPARISON WITH OBJECTS THAT RETURN NOTIMPLEMENTED
# =============================================================================

print("\n" + "=" * 80)
print("111. RICH COMPARISON PROTOCOL")
print("=" * 80)

"""
Python's rich comparison methods include:

    __eq__
    __ne__
    __lt__
    __le__
    __gt__
    __ge__

For a < b, Python uses the appropriate rich comparison machinery.

Custom classes should implement only the semantics they actually support.
"""


# =============================================================================
# 112. DIRECT RICH COMPARISON METHODS
# =============================================================================

print("\n" + "=" * 80)
print("112. DIRECT RICH COMPARISON METHODS")
print("=" * 80)

@dataclass
class Temperature:
    celsius: float

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius < other.celsius

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius == other.celsius


cold = Temperature(10)
warm = Temperature(25)

print("cold < warm:", cold < warm)
print("cold == warm:", cold == warm)


# =============================================================================
# 113. COMPARISON WITH None
# =============================================================================

print("\n" + "=" * 80)
print("113. SAFE NONE COMPARISON")
print("=" * 80)

result = None

if result is not None:
    print("Result exists:", result)
else:
    print("Result is None.")


# =============================================================================
# 114. DEFAULT VALUES AND COMPARISON
# =============================================================================

print("\n" + "=" * 80)
print("114. DEFAULT VALUE LOGIC")
print("=" * 80)

provided_limit: int | None = None

limit = provided_limit if provided_limit is not None else 100

print("Effective limit:", limit)


# =============================================================================
# 115. COMPARISON OF BOOLEAN CONDITIONS
# =============================================================================

print("\n" + "=" * 80)
print("115. COMBINED BUSINESS RULE")
print("=" * 80)

age = 30
income = 80000
credit_score = 720
existing_debt = 10000

loan_eligible = (
    age >= 21
    and income >= 50000
    and credit_score >= 700
    and existing_debt <= 20000
)

print("Loan eligible:", loan_eligible)


# =============================================================================
# 116. DECOMPOSING COMPLEX COMPARISONS
# =============================================================================

print("\n" + "=" * 80)
print("116. READABLE COMPLEX CONDITIONS")
print("=" * 80)

age_ok = age >= 21
income_ok = income >= 50000
credit_ok = credit_score >= 700
debt_ok = existing_debt <= 20000

loan_eligible = age_ok and income_ok and credit_ok and debt_ok

print("age_ok:", age_ok)
print("income_ok:", income_ok)
print("credit_ok:", credit_ok)
print("debt_ok:", debt_ok)
print("loan_eligible:", loan_eligible)


# =============================================================================
# 117. COMPARISON OF TWO DATES FOR EXPIRATION
# =============================================================================

print("\n" + "=" * 80)
print("117. EXPIRATION CHECK")
print("=" * 80)

expiry_date = date(2026, 12, 31)

if today > expiry_date:
    print("Expired.")
else:
    print("Not expired.")


# =============================================================================
# 118. COMPARISON WITH TIME WINDOWS
# =============================================================================

print("\n" + "=" * 80)
print("118. TIME WINDOW")
print("=" * 80)

current_hour = 14

business_hours = 9 <= current_hour < 18

print("Within business hours:", business_hours)


# =============================================================================
# 119. COMPARISON WITH GRADES
# =============================================================================

print("\n" + "=" * 80)
print("119. GRADE BOUNDARIES")
print("=" * 80)

def grade_from_percentage(percentage: float) -> str:
    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100.")

    if percentage >= 90:
        return "A"
    if percentage >= 80:
        return "B"
    if percentage >= 70:
        return "C"
    if percentage >= 60:
        return "D"
    return "F"


for percentage in [0, 59.99, 60, 69.99, 70, 79.99, 80, 89.99, 90, 100]:
    print(f"{percentage:>6} -> {grade_from_percentage(percentage)}")


# =============================================================================
# 120. EDGE CASES WITH EMPTY STRINGS
# =============================================================================

print("\n" + "=" * 80)
print("120. EMPTY STRING COMPARISONS")
print("=" * 80)

empty = ""
non_empty = "Python"

print("empty == '':", empty == "")
print("empty < 'Python':", empty < non_empty)
print("bool(empty):", bool(empty))


# =============================================================================
# 121. EDGE CASES WITH EMPTY COLLECTIONS
# =============================================================================

print("\n" + "=" * 80)
print("121. EMPTY COLLECTIONS")
print("=" * 80)

empty_list: list[int] = []
empty_tuple: tuple[int, ...] = ()
empty_dict: dict[str, int] = {}
empty_set: set[int] = set()

print("empty_list == []:", empty_list == [])
print("empty_tuple == ():", empty_tuple == ())
print("empty_dict == {}:", empty_dict == {})
print("empty_set == set():", empty_set == set())


# =============================================================================
# 122. COMPARISON OF DIFFERENT TYPES
# =============================================================================

print("\n" + "=" * 80)
print("122. DIFFERENT TYPE COMPARISONS")
print("=" * 80)

print("1 == 1.0:", 1 == 1.0)
print("'1' == 1:", "1" == 1)

try:
    print("'1' < 1:", "1" < 1)
except TypeError as error:
    print("'1' < 1 raises:", type(error).__name__)

"""
Equality between unrelated types often returns False.

Ordering unrelated types commonly raises TypeError in Python 3.
"""


# =============================================================================
# 123. COMPARISON OF BYTES AND STRINGS
# =============================================================================

print("\n" + "=" * 80)
print("123. BYTES VERSUS STRING")
print("=" * 80)

byte_value = b"hello"
text_value = "hello"

print("byte_value == text_value:", byte_value == text_value)

try:
    print(byte_value < text_value)
except TypeError as error:
    print("bytes/string ordering raises:", type(error).__name__)


# =============================================================================
# 124. COMPARISON AND DATA QUALITY
# =============================================================================

print("\n" + "=" * 80)
print("124. DATA QUALITY CHECK")
print("=" * 80)

dataset = [
    {"name": "A", "score": 95},
    {"name": "B", "score": None},
    {"name": "C", "score": 75},
]

for record in dataset:
    score = record["score"]

    if score is None:
        print(record["name"], "has a missing score.")
    elif score >= 80:
        print(record["name"], "has a high score.")
    else:
        print(record["name"], "has a lower score.")


# =============================================================================
# 125. SORTING WITH MISSING VALUES
# =============================================================================

print("\n" + "=" * 80)
print("125. SORTING DATA WITH NONE")
print("=" * 80)

"""
None cannot generally be ordered directly with numbers.

A key function can map missing values to a separate sorting category.
"""

scores_with_missing = [95, None, 75, 88, None]

sorted_scores = sorted(
    scores_with_missing,
    key=lambda value: (value is None, value if value is not None else 0),
)

print("Original:", scores_with_missing)
print("Sorted with None last:", sorted_scores)


# =============================================================================
# 126. CUSTOM COMPARISON FOR A DOMAIN OBJECT
# =============================================================================

print("\n" + "=" * 80)
print("126. DOMAIN OBJECT COMPARISON")
print("=" * 80)

@total_ordering
class Invoice:
    def __init__(self, invoice_id: str, amount: Decimal) -> None:
        self.invoice_id = invoice_id
        self.amount = amount

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Invoice):
            return NotImplemented
        return self.amount == other.amount

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Invoice):
            return NotImplemented
        return self.amount < other.amount

    def __repr__(self) -> str:
        return f"Invoice({self.invoice_id!r}, {self.amount!r})"


invoice_a = Invoice("INV-001", Decimal("25000.00"))
invoice_b = Invoice("INV-002", Decimal("30000.00"))

print("invoice_a < invoice_b:", invoice_a < invoice_b)
print("invoice_a <= invoice_b:", invoice_a <= invoice_b)


# =============================================================================
# 127. COMPARISON AND BUSINESS RULES
# =============================================================================

print("\n" + "=" * 80)
print("127. BUSINESS RULE ENGINE")
print("=" * 80)

def transaction_allowed(
    amount: Decimal,
    daily_limit: Decimal,
    current_total: Decimal,
) -> bool:
    """
    Allow a transaction only when the amount is positive and the resulting
    daily total does not exceed the configured limit.
    """
    if amount <= Decimal("0"):
        return False

    projected_total = current_total + amount

    return projected_total <= daily_limit


daily_limit = Decimal("100000")
current_total = Decimal("75000")
transaction_amount = Decimal("20000")

print(
    "Transaction allowed:",
    transaction_allowed(
        transaction_amount,
        daily_limit,
        current_total,
    ),
)


# =============================================================================
# 128. COMPARISON AND ERROR MESSAGES
# =============================================================================

print("\n" + "=" * 80)
print("128. EXPLICIT VALIDATION ERRORS")
print("=" * 80)

def validate_age_for_registration(age: int) -> None:
    if age < 0:
        raise ValueError("Age cannot be negative.")
    if age > 120:
        raise ValueError("Age exceeds the supported range.")
    if age < 18:
        raise ValueError("Registration requires age 18 or above.")


for candidate in [-1, 15, 18, 121]:
    try:
        validate_age_for_registration(candidate)
        print(candidate, "accepted")
    except ValueError as error:
        print(candidate, "rejected:", error)


# =============================================================================
# 129. COMPARISON AND SORTED ORDER
# =============================================================================

print("\n" + "=" * 80)
print("129. ORDERING CUSTOM VALUES")
print("=" * 80)

prices = [
    Decimal("199.99"),
    Decimal("49.99"),
    Decimal("999.00"),
    Decimal("149.50"),
]

for price in sorted(prices):
    print(price)


# =============================================================================
# 130. COMPARISON AND SEARCH
# =============================================================================

print("\n" + "=" * 80)
print("130. SEARCH WITH COMPARISON")
print("=" * 80)

def first_above_threshold(values: list[int], threshold: int) -> int | None:
    for value in values:
        if value > threshold:
            return value
    return None


values = [5, 12, 8, 20, 4]

print("First value > 10:", first_above_threshold(values, 10))
print("First value > 25:", first_above_threshold(values, 25))


# =============================================================================
# 131. COMPARISON AND BINARY SEARCH
# =============================================================================

print("\n" + "=" * 80)
print("131. BINARY SEARCH")
print("=" * 80)

def binary_search(sorted_values: list[int], target: int) -> int:
    """
    Return the index of target or -1 when target is absent.

    The input must already be sorted in ascending order.

    Binary search repeatedly compares the target with the middle element,
    reducing the search interval roughly by half each time.

    Time complexity:
        O(log n)

    Space complexity:
        O(1) for this iterative implementation.
    """
    low = 0
    high = len(sorted_values) - 1

    while low <= high:
        middle = (low + high) // 2
        middle_value = sorted_values[middle]

        if middle_value == target:
            return middle
        if middle_value < target:
            low = middle + 1
        else:
            high = middle - 1

    return -1


sorted_numbers = [2, 4, 6, 8, 10, 12, 14]

print("Index of 10:", binary_search(sorted_numbers, 10))
print("Index of 11:", binary_search(sorted_numbers, 11))


# =============================================================================
# 132. COMPARISON AND ALGORITHM DESIGN
# =============================================================================

print("\n" + "=" * 80)
print("132. COMPARISON IN ALGORITHMS")
print("=" * 80)

"""
Comparison operators are fundamental to algorithms such as:

    - searching
    - sorting
    - filtering
    - partitioning
    - threshold detection
    - interval processing
    - decision trees
    - validation
    - scheduling
    - ranking

The quality of comparison logic directly affects algorithm correctness.
"""


# =============================================================================
# 133. INTERVAL OVERLAP
# =============================================================================

print("\n" + "=" * 80)
print("133. INTERVAL COMPARISON")
print("=" * 80)

def intervals_overlap(
    start_a: int,
    end_a: int,
    start_b: int,
    end_b: int,
) -> bool:
    """
    Determine whether two closed intervals overlap.

    Assumption:
        start <= end for each interval.

    Closed intervals consider touching endpoints as overlapping.
    """
    if start_a > end_a or start_b > end_b:
        raise ValueError("Interval start cannot exceed interval end.")

    return start_a <= end_b and start_b <= end_a


print("Intervals [1, 5] and [4, 8]:",
      intervals_overlap(1, 5, 4, 8))

print("Intervals [1, 5] and [6, 8]:",
      intervals_overlap(1, 5, 6, 8))

print("Intervals [1, 5] and [5, 8]:",
      intervals_overlap(1, 5, 5, 8))


# =============================================================================
# 134. HALF-OPEN INTERVALS
# =============================================================================

print("\n" + "=" * 80)
print("134. HALF-OPEN INTERVALS")
print("=" * 80)

"""
A half-open interval is:

    [start, end)

It includes start but excludes end.

Python's range() follows this convention.
"""

print("Values in range(1, 5):", list(range(1, 5)))
print("5 in range(1, 5):", 5 in range(1, 5))
print("4 in range(1, 5):", 4 in range(1, 5))


# =============================================================================
# 135. COMPARISON AND RANGE OBJECTS
# =============================================================================

print("\n" + "=" * 80)
print("135. RANGE MEMBERSHIP")
print("=" * 80)

age = 25

print("18 <= age < 60:", 18 <= age < 60)
print("age in range(18, 60):", age in range(18, 60))


# =============================================================================
# 136. COMPARISON OF SET RELATIONSHIPS
# =============================================================================

print("\n" + "=" * 80)
print("136. SET RELATIONSHIP CHECKS")
print("=" * 80)

required_permissions = {"read", "write"}
user_permissions = {"read", "write", "delete"}

print(
    "Required permissions are a subset:",
    required_permissions <= user_permissions,
)

print(
    "User has additional permissions:",
    user_permissions > required_permissions,
)


# =============================================================================
# 137. COMPARISON AND FEATURE FLAGS
# =============================================================================

print("\n" + "=" * 80)
print("137. FEATURE FLAG CONDITIONS")
print("=" * 80)

user_plan = "premium"
minimum_plan = "premium"

feature_enabled = user_plan == minimum_plan

print("Feature enabled:", feature_enabled)


# =============================================================================
# 138. COMPARISON AND DATA FILTERING PIPELINE
# =============================================================================

print("\n" + "=" * 80)
print("138. DATA FILTERING PIPELINE")
print("=" * 80)

transactions = [
    {"id": 1, "amount": 5000, "status": "completed"},
    {"id": 2, "amount": 25000, "status": "pending"},
    {"id": 3, "amount": 50000, "status": "completed"},
    {"id": 4, "amount": 1000, "status": "completed"},
]

large_completed = [
    transaction
    for transaction in transactions
    if transaction["amount"] >= 10000
    and transaction["status"] == "completed"
]

for transaction in large_completed:
    print(transaction)


# =============================================================================
# 139. COMPARISON AND CONDITIONAL AGGREGATION
# =============================================================================

print("\n" + "=" * 80)
print("139. CONDITIONAL AGGREGATION")
print("=" * 80)

completed_amount = sum(
    transaction["amount"]
    for transaction in transactions
    if transaction["status"] == "completed"
)

print("Completed transaction amount:", completed_amount)


# =============================================================================
# 140. COMPARISON AND ANY / ALL
# =============================================================================

print("\n" + "=" * 80)
print("140. any() AND all()")
print("=" * 80)

scores = [80, 85, 90, 95]

all_passing = all(score >= 40 for score in scores)
any_excellent = any(score >= 90 for score in scores)

print("All passing:", all_passing)
print("Any excellent:", any_excellent)


# =============================================================================
# 141. EMPTY ITERABLE EDGE CASE WITH all() AND any()
# =============================================================================

print("\n" + "=" * 80)
print("141. any() / all() EMPTY CASE")
print("=" * 80)

empty_values: list[int] = []

print("any(empty_values):", any(empty_values))
print("all(empty_values):", all(empty_values))

"""
This is an important logical behavior:

    any([]) -> False
    all([]) -> True

Do not assume all() means "there must be at least one item."
"""


# =============================================================================
# 142. COMPARISON AND GENERATOR EXPRESSIONS
# =============================================================================

print("\n" + "=" * 80)
print("142. GENERATOR-BASED COMPARISON")
print("=" * 80)

large_number_exists = any(
    number > 100
    for number in range(1, 200)
)

print("Any number > 100:", large_number_exists)


# =============================================================================
# 143. COMPARISON AND PERFORMANCE OF any()
# =============================================================================

print("\n" + "=" * 80)
print("143. SHORT-CIRCUITING any()")
print("=" * 80)

def is_large(number: int) -> bool:
    print("Checking:", number)
    return number > 3


result = any(is_large(number) for number in [1, 2, 3, 4, 5])

print("Result:", result)

"""
any() stops once it finds a truthy result.
"""


# =============================================================================
# 144. COMPARISON AND PERFORMANCE OF all()
# =============================================================================

print("\n" + "=" * 80)
print("144. SHORT-CIRCUITING all()")
print("=" * 80)

def is_positive(number: int) -> bool:
    print("Checking:", number)
    return number > 0


result = all(is_positive(number) for number in [1, 2, -1, 4])

print("Result:", result)

"""
all() stops once it finds a false result.
"""


# =============================================================================
# 145. ADVANCED: SORTING WITH MULTIPLE DIRECTIONS
# =============================================================================

print("\n" + "=" * 80)
print("145. MULTI-DIRECTION SORTING")
print("=" * 80)

products = [
    {"name": "A", "rating": 4, "price": 100},
    {"name": "B", "rating": 5, "price": 200},
    {"name": "C", "rating": 5, "price": 150},
]

"""
A tuple key naturally sorts all fields in the same direction.

When different fields require different directions, it can be cleaner
to perform stable sorts in reverse priority order or use a carefully
designed key transformation.
"""

sorted_products = sorted(
    products,
    key=lambda product: (-product["rating"], product["price"]),
)

for product in sorted_products:
    print(product)


# =============================================================================
# 146. ADVANCED: COMPARISON KEY DESIGN
# =============================================================================

print("\n" + "=" * 80)
print("146. COMPARISON KEY DESIGN")
print("=" * 80)

@dataclass
class Employee:
    name: str
    department: str
    salary: int

    def sort_key(self) -> tuple[str, int, str]:
        return (
            self.department,
            -self.salary,
            self.name,
        )


employee_list = [
    Employee("A", "Engineering", 100000),
    Employee("B", "Engineering", 120000),
    Employee("C", "Finance", 90000),
    Employee("D", "Finance", 110000),
]

for employee in sorted(employee_list, key=Employee.sort_key):
    print(employee)


# =============================================================================
# 147. ADVANCED: COMPARISON OF CASE-INSENSITIVE NAMES
# =============================================================================

print("\n" + "=" * 80)
print("147. CASE-INSENSITIVE SORTING")
print("=" * 80)

names = ["atul", "Bob", "alice", "CHARLIE"]

print(
    sorted(names, key=str.casefold)
)


# =============================================================================
# 148. ADVANCED: COMPARISON OF DECIMAL VALUES
# =============================================================================

print("\n" + "=" * 80)
print("148. DECIMAL ORDERING")
print("=" * 80)

decimal_values = [
    Decimal("10.10"),
    Decimal("10.01"),
    Decimal("9.99"),
]

for value in sorted(decimal_values):
    print(value)


# =============================================================================
# 149. ADVANCED: COMPARISON OF CUSTOM PRIORITIES
# =============================================================================

print("\n" + "=" * 80)
print("149. CUSTOM PRIORITY ORDER")
print("=" * 80)

priority_order = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

tasks = [
    {"name": "Task A", "priority": "low"},
    {"name": "Task B", "priority": "critical"},
    {"name": "Task C", "priority": "high"},
]

ordered_tasks = sorted(
    tasks,
    key=lambda task: priority_order[task["priority"]],
)

for task in ordered_tasks:
    print(task)


# =============================================================================
# 150. EDGE CASE: UNKNOWN PRIORITY
# =============================================================================

print("\n" + "=" * 80)
print("150. HANDLING UNKNOWN VALUES")
print("=" * 80)

tasks_with_unknown = [
    {"name": "Task A", "priority": "low"},
    {"name": "Task B", "priority": "unknown"},
]

def priority_key(task: dict[str, str]) -> int:
    return priority_order.get(task["priority"], 999)


for task in sorted(tasks_with_unknown, key=priority_key):
    print(task)


# =============================================================================
# 151. COMPARISON AND OBJECT IDENTITY
# =============================================================================

print("\n" + "=" * 80)
print("151. OBJECT IDENTITY")
print("=" * 80)

object_a = []
object_b = object_a
object_c = []

print("object_a == object_b:", object_a == object_b)
print("object_a is object_b:", object_a is object_b)
print("object_a == object_c:", object_a == object_c)
print("object_a is object_c:", object_a is object_c)

print("id(object_a) == id(object_b):", id(object_a) == id(object_b))


# =============================================================================
# 152. IDENTITY SHOULD BE USED SPARINGLY
# =============================================================================

print("\n" + "=" * 80)
print("152. IDENTITY BEST PRACTICE")
print("=" * 80)

"""
Use identity primarily for singleton/sentinel checks, especially None.

Prefer:

    value is None

Avoid using:

    value is 100

as a value comparison.

Object interning and caching can vary by implementation and context.
"""

number_a = 1000
number_b = 1000

print("number_a == number_b:", number_a == number_b)
print("number_a is number_b:", number_a is number_b)


# =============================================================================
# 153. COMPARISON AND HASHABILITY
# =============================================================================

print("\n" + "=" * 80)
print("153. EQUALITY AND HASHING")
print("=" * 80)

"""
Objects used as dictionary keys or set members need compatible hashing
and equality semantics.

A fundamental expectation is:

    if a == b:
        hash(a) == hash(b)

for hashable objects.

Defining custom __eq__ can affect hashability.
"""

text_a = "Python"
text_b = "Python"

print("text_a == text_b:", text_a == text_b)
print("hash(text_a) == hash(text_b):", hash(text_a) == hash(text_b))


# =============================================================================
# 154. DATACLASS EQUALITY AND HASHING CONSIDERATIONS
# =============================================================================

print("\n" + "=" * 80)
print("154. DATACLASS SEMANTICS")
print("=" * 80)

@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int


coordinate_a = Coordinate(10, 20)
coordinate_b = Coordinate(10, 20)

print("coordinate_a == coordinate_b:", coordinate_a == coordinate_b)
print("hashes equal:", hash(coordinate_a) == hash(coordinate_b))


# =============================================================================
# 155. COMPARISON OF COORDINATES
# =============================================================================

print("\n" + "=" * 80)
print("155. COORDINATE ORDERING")
print("=" * 80)

@dataclass(order=True, frozen=True)
class OrderedCoordinate:
    x: int
    y: int


coordinate_c = OrderedCoordinate(1, 5)
coordinate_d = OrderedCoordinate(2, 0)

print("coordinate_c < coordinate_d:", coordinate_c < coordinate_d)

"""
The generated ordering is lexicographical by field declaration:

    x first
    y second

This ordering may be technically valid but not necessarily meaningful
for every geometric application.
"""


# =============================================================================
# 156. COMPARISON AND DOMAIN SEMANTICS
# =============================================================================

print("\n" + "=" * 80)
print("156. DOMAIN SEMANTICS MATTER")
print("=" * 80)

"""
Two objects can have several legitimate comparison dimensions.

For example, an employee can be compared by:

    - salary
    - seniority
    - performance
    - department
    - name

There is no universally correct ordering without a domain rule.

Use explicit key functions or named methods when multiple interpretations
exist.
"""

employee = Employee("Atul", "Engineering", 100000)

print("Salary:", employee.salary)
print("Salary >= 100000:", employee.salary >= 100000)
print("Department == Engineering:", employee.department == "Engineering")


# =============================================================================
# 157. ADVANCED: APPROXIMATE DOMAIN COMPARISON
# =============================================================================

print("\n" + "=" * 80)
print("157. APPROXIMATE DOMAIN COMPARISON")
print("=" * 80)

def approximately_equal(
    a: float,
    b: float,
    tolerance: float = 1e-9,
) -> bool:
    return isclose(a, b, rel_tol=tolerance, abs_tol=tolerance)


print(
    "approximately_equal(100.0000001, 100.0000002):",
    approximately_equal(100.0000001, 100.0000002),
)


# =============================================================================
# 158. APPROXIMATE RANGE CHECK
# =============================================================================

print("\n" + "=" * 80)
print("158. APPROXIMATE RANGE CHECK")
print("=" * 80)

measurement = 9.999999999
target = 10.0

within_tolerance = isclose(measurement, target, abs_tol=1e-8)

print("Within tolerance:", within_tolerance)


# =============================================================================
# 159. COMMON MISTAKE: WRONG LOGICAL OPERATOR
# =============================================================================

print("\n" + "=" * 80)
print("159. and VERSUS or")
print("=" * 80)

age = 25
has_permission = False

correct_requirement = age >= 18 and has_permission
alternative_requirement = age >= 18 or has_permission

print("AND condition:", correct_requirement)
print("OR condition:", alternative_requirement)

"""
Changing and to or can dramatically change business logic.

The correct operator must reflect the requirement rather than the desired
Boolean result.
"""


# =============================================================================
# 160. COMMON MISTAKE: WRONG BOUNDARY
# =============================================================================

print("\n" + "=" * 80)
print("160. BOUNDARY MISTAKE")
print("=" * 80)

age = 18

print("age > 18 :", age > 18)
print("age >= 18:", age >= 18)

"""
If the rule says "18 or older", >= is required.
"""


# =============================================================================
# 161. COMMON MISTAKE: STRING NUMBERS
# =============================================================================

print("\n" + "=" * 80)
print("161. STRING NUMBER ORDERING")
print("=" * 80)

print("'9' > '10':", "9" > "10")
print("9 > 10:", 9 > 10)

"""
The first comparison is lexical string ordering.
The second is numeric ordering.

Data should be converted to the intended semantic type before comparison.
"""


# =============================================================================
# 162. COMMON MISTAKE: ASSUMING DICTIONARIES ARE ORDERABLE
# =============================================================================

print("\n" + "=" * 80)
print("162. DICTIONARY ORDERING LIMITATION")
print("=" * 80)

record_a = {"score": 90}
record_b = {"score": 80}

try:
    print(record_a > record_b)
except TypeError as error:
    print("Direct dictionary ordering:", type(error).__name__)

print(
    "Compare values instead:",
    record_a["score"] > record_b["score"],
)


# =============================================================================
# 163. COMMON MISTAKE: ASSUMING ALL OBJECTS HAVE NATURAL ORDER
# =============================================================================

print("\n" + "=" * 80)
print("163. NATURAL ORDER LIMITATION")
print("=" * 80)

"""
Some objects have equality but no natural ordering.

A good program should not invent an arbitrary ordering merely because
an algorithm expects one.

Instead, define a domain-specific key or ordering rule.
"""

complex_numbers = [1 + 2j, 2 + 3j]

try:
    print(sorted(complex_numbers))
except TypeError as error:
    print("Cannot sort complex numbers directly:", type(error).__name__)

print(
    "Sort complex numbers by magnitude:",
    sorted(complex_numbers, key=abs),
)


# =============================================================================
# 164. COMPARISON AND ABSOLUTE VALUE
# =============================================================================

print("\n" + "=" * 80)
print("164. COMPARING BY MAGNITUDE")
print("=" * 80)

values = [-100, 20, -5, 30]

largest_magnitude = max(values, key=abs)

print("Values:", values)
print("Largest absolute magnitude:", largest_magnitude)


# =============================================================================
# 165. COMPARISON AND CUSTOM METRIC
# =============================================================================

print("\n" + "=" * 80)
print("165. CUSTOM METRIC")
print("=" * 80)

points = [(1, 2), (5, 5), (2, 1), (10, 0)]

def squared_distance_from_origin(point: tuple[int, int]) -> int:
    x, y = point
    return x * x + y * y


farthest = max(points, key=squared_distance_from_origin)

print("Points:", points)
print("Farthest by squared distance:", farthest)


# =============================================================================
# 166. COMPARISON AND NEGATION
# =============================================================================

print("\n" + "=" * 80)
print("166. NEGATING COMPARISON RESULTS")
print("=" * 80)

x = 10

print("not (x == 10):", not (x == 10))
print("x != 10:", x != 10)

"""
For equality and inequality, != directly expresses the intended relationship
and is generally clearer than negating ==.
"""


# =============================================================================
# 167. COMPARISON AND DE MORGAN'S LAWS
# =============================================================================

print("\n" + "=" * 80)
print("167. DE MORGAN'S LAWS")
print("=" * 80)

a = True
b = False

left_expression = not (a and b)
right_expression = (not a) or (not b)

print("not (a and b):", left_expression)
print("(not a) or (not b):", right_expression)

left_expression = not (a or b)
right_expression = (not a) and (not b)

print("not (a or b):", left_expression)
print("(not a) and (not b):", right_expression)


# =============================================================================
# 168. COMPARISON AND CONDITIONAL PRIORITY
# =============================================================================

print("\n" + "=" * 80)
print("168. CONDITIONAL PRIORITY")
print("=" * 80)

score = 88
attendance = 92

eligible = (
    score >= 50
    and attendance >= 75
)

print("Eligible:", eligible)


# =============================================================================
# 169. COMPARISON AND ERROR BOUNDARIES
# =============================================================================

print("\n" + "=" * 80)
print("169. ERROR BOUNDARY")
print("=" * 80)

observed = 102
expected = 100
maximum_error = 5

error = abs(observed - expected)

print("Error:", error)
print("Within allowed error:", error <= maximum_error)


# =============================================================================
# 170. COMPARISON AND SLA
# =============================================================================

print("\n" + "=" * 80)
print("170. SERVICE LEVEL AGREEMENT CHECK")
print("=" * 80)

response_time_ms = 180
sla_limit_ms = 200

sla_met = response_time_ms <= sla_limit_ms

print("SLA met:", sla_met)


# =============================================================================
# 171. COMPARISON AND INVENTORY
# =============================================================================

print("\n" + "=" * 80)
print("171. INVENTORY REORDER")
print("=" * 80)

stock = 12
reorder_level = 20

if stock <= reorder_level:
    print("Reorder required.")
else:
    print("Stock level is sufficient.")


# =============================================================================
# 172. COMPARISON AND CONSTRUCTION LIMITS
# =============================================================================

print("\n" + "=" * 80)
print("172. CONSTRUCTION LIMIT")
print("=" * 80)

load = 850
safe_load_limit = 1000

if load <= safe_load_limit:
    print("Load is within the safe limit.")
else:
    print("Load exceeds the safe limit.")


# =============================================================================
# 173. COMPARISON AND REAL ESTATE
# =============================================================================

print("\n" + "=" * 80)
print("173. REAL ESTATE FILTER")
print("=" * 80)

properties = [
    {"name": "A", "price": 5000000, "area": 1200},
    {"name": "B", "price": 8000000, "area": 1800},
    {"name": "C", "price": 6000000, "area": 1000},
]

budget = 7000000
minimum_area = 1100

matches = [
    property_data
    for property_data in properties
    if property_data["price"] <= budget
    and property_data["area"] >= minimum_area
]

for property_data in matches:
    print(property_data)


# =============================================================================
# 174. COMPARISON AND STATISTICAL OUTLIERS
# =============================================================================

print("\n" + "=" * 80)
print("174. OUTLIER THRESHOLD")
print("=" * 80)

measurements = [10, 11, 9, 10, 50, 12]
outlier_threshold = 30

outliers = [
    measurement
    for measurement in measurements
    if measurement > outlier_threshold
]

print("Outliers:", outliers)


# =============================================================================
# 175. COMPARISON AND ACCESS CONTROL LEVELS
# =============================================================================

print("\n" + "=" * 80)
print("175. ACCESS LEVEL COMPARISON")
print("=" * 80)

access_levels = {
    "guest": 0,
    "user": 1,
    "manager": 2,
    "admin": 3,
}

current_role = "manager"
required_role = "user"

has_access = (
    access_levels[current_role]
    >= access_levels[required_role]
)

print("Has access:", has_access)


# =============================================================================
# 176. COMPARISON AND STATUS PRIORITY
# =============================================================================

print("\n" + "=" * 80)
print("176. STATUS PRIORITY")
print("=" * 80)

status_priority = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}

status_a = "critical"
status_b = "high"

print(
    "status_a has higher priority:",
    status_priority[status_a] > status_priority[status_b],
)


# =============================================================================
# 177. ADVANCED: CUSTOM COMPARATOR ADAPTER
# =============================================================================

print("\n" + "=" * 80)
print("177. COMPARATOR ADAPTER")
print("=" * 80)

from typing import Callable

Comparator = Callable[[Any, Any], int]


def compare_by_key(
    first: Any,
    second: Any,
    key: Callable[[Any], Any],
) -> int:
    first_key = key(first)
    second_key = key(second)

    if first_key < second_key:
        return -1
    if first_key > second_key:
        return 1
    return 0


print(
    compare_by_key(
        {"score": 90},
        {"score": 80},
        key=lambda item: item["score"],
    )
)


# =============================================================================
# 178. ADVANCED: LEGACY COMPARATOR WITH cmp_to_key
# =============================================================================

print("\n" + "=" * 80)
print("178. cmp_to_key")
print("=" * 80)

from functools import cmp_to_key

def descending_numeric_comparator(a: int, b: int) -> int:
    if a > b:
        return -1
    if a < b:
        return 1
    return 0


numbers = [5, 2, 9, 1]

print(
    sorted(
        numbers,
        key=cmp_to_key(descending_numeric_comparator),
    )
)

"""
Modern Python generally prefers key functions because they are clearer
and can be more efficient for sorting.

cmp_to_key is useful when adapting an existing comparator-style algorithm.
"""


# =============================================================================
# 179. ADVANCED: COMPARISON AND CACHING KEYS
# =============================================================================

print("\n" + "=" * 80)
print("179. COMPARISON KEY COMPUTATION")
print("=" * 80)

"""
When sorting, Python's key-based sorting computes the key for each item
and uses those keys during sorting.

This is generally preferable to repeatedly computing an expensive
comparison transformation.
"""

records = [
    {"name": "alice"},
    {"name": "Bob"},
    {"name": "charlie"},
]

sorted_records = sorted(
    records,
    key=lambda record: record["name"].casefold(),
)

print(sorted_records)


# =============================================================================
# 180. ADVANCED: COMPARISON AND NORMALIZATION
# =============================================================================

print("\n" + "=" * 80)
print("180. NORMALIZATION BEFORE COMPARISON")
print("=" * 80)

def normalize_identifier(value: str) -> str:
    return value.strip().casefold()


raw_a = "  Python  "
raw_b = "PYTHON"

print(
    normalize_identifier(raw_a)
    == normalize_identifier(raw_b)
)


# =============================================================================
# 181. COMPARISON AND INTERNATIONAL TEXT
# =============================================================================

print("\n" + "=" * 80)
print("181. UNICODE TEXT CONSIDERATIONS")
print("=" * 80)

"""
Unicode strings can contain visually similar text represented in different
ways. Normalization may be necessary for robust equality comparisons.

The unicodedata module provides Unicode normalization forms.
"""

import unicodedata

composed = "é"
decomposed = "e\u0301"

print("Direct equality:", composed == decomposed)

normalized_composed = unicodedata.normalize("NFC", composed)
normalized_decomposed = unicodedata.normalize("NFC", decomposed)

print(
    "NFC-normalized equality:",
    normalized_composed == normalized_decomposed,
)


# =============================================================================
# 182. COMPARISON AND DECISION TABLE
# =============================================================================

print("\n" + "=" * 80)
print("182. DECISION TABLE")
print("=" * 80)

def admission_decision(
    percentage: float,
    attendance: float,
) -> str:
    if percentage >= 60 and attendance >= 75:
        return "eligible"
    if percentage >= 60 and attendance < 75:
        return "attendance shortfall"
    return "academic shortfall"


cases = [
    (80, 80),
    (80, 70),
    (50, 90),
]

for percentage, attendance in cases:
    print(
        percentage,
        attendance,
        "->",
        admission_decision(percentage, attendance),
    )


# =============================================================================
# 183. ADVANCED: MULTI-CRITERIA ELIGIBILITY
# =============================================================================

print("\n" + "=" * 80)
print("183. MULTI-CRITERIA ELIGIBILITY")
print("=" * 80)

def is_candidate_eligible(candidate: dict[str, Any]) -> bool:
    return (
        candidate["age"] >= 18
        and candidate["experience"] >= 2
        and candidate["score"] >= 70
        and candidate["status"] == "active"
    )


candidate_records = [
    {
        "name": "A",
        "age": 25,
        "experience": 3,
        "score": 80,
        "status": "active",
    },
    {
        "name": "B",
        "age": 17,
        "experience": 3,
        "score": 90,
        "status": "active",
    },
]

for candidate in candidate_records:
    print(
        candidate["name"],
        "->",
        is_candidate_eligible(candidate),
    )


# =============================================================================
# 184. COMPARISON AND FAIL-FAST VALIDATION
# =============================================================================

print("\n" + "=" * 80)
print("184. FAIL-FAST VALIDATION")
print("=" * 80)

def validate_order(start: int, end: int) -> None:
    if start > end:
        raise ValueError(
            f"Invalid interval: start={start} is greater than end={end}"
        )


validate_order(1, 10)

try:
    validate_order(10, 1)
except ValueError as error:
    print("Validation error:", error)


# =============================================================================
# 185. COMPARISON AND INVARIANTS
# =============================================================================

print("\n" + "=" * 80)
print("185. INVARIANTS")
print("=" * 80)

def calculate_average(values: list[float]) -> float:
    if not values:
        raise ValueError("At least one value is required.")

    total = sum(values)
    average = total / len(values)

    assert min(values) <= average <= max(values)

    return average


sample_values = [10, 20, 30]

print("Average:", calculate_average(sample_values))


# =============================================================================
# 186. COMPARISON AND TEST-DRIVEN THINKING
# =============================================================================

print("\n" + "=" * 80)
print("186. EDGE-CASE TESTING")
print("=" * 80)

def is_between(value: float, lower: float, upper: float) -> bool:
    if lower > upper:
        raise ValueError("lower cannot exceed upper")
    return lower <= value <= upper


edge_cases = [
    (10, 10, 20, True),
    (20, 10, 20, True),
    (9.99, 10, 20, False),
    (20.01, 10, 20, False),
]

for value, lower, upper, expected in edge_cases:
    actual = is_between(value, lower, upper)
    assert actual == expected

print("All interval edge-case tests passed.")


# =============================================================================
# 187. ADVANCED: COMPARISON OF RECORDS
# =============================================================================

print("\n" + "=" * 80)
print("187. RECORD COMPARISON")
print("=" * 80)

record_a = {
    "name": "Alice",
    "score": 95,
    "experience": 4,
}

record_b = {
    "name": "Bob",
    "score": 90,
    "experience": 6,
}

record_comparison = (
    record_a["score"],
    record_a["experience"],
) > (
    record_b["score"],
    record_b["experience"],
)

print("Record A ranks higher:", record_comparison)


# =============================================================================
# 188. COMPARISON AND TIE-BREAKING
# =============================================================================

print("\n" + "=" * 80)
print("188. TIE-BREAKING")
print("=" * 80)

ranked_candidates = [
    {"name": "Alice", "score": 90, "experience": 3},
    {"name": "Bob", "score": 90, "experience": 5},
    {"name": "Charlie", "score": 85, "experience": 7},
]

ranked = sorted(
    ranked_candidates,
    key=lambda candidate: (
        -candidate["score"],
        -candidate["experience"],
        candidate["name"],
    ),
)

for candidate in ranked:
    print(candidate)


# =============================================================================
# 189. ADVANCED: COMPARISON OF ENUM PRIORITIES
# =============================================================================

print("\n" + "=" * 80)
print("189. ENUM VALUES AND PRIORITY")
print("=" * 80)

class Severity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


current_severity = Severity.HIGH

print(
    "At least medium:",
    current_severity.value >= Severity.MEDIUM.value,
)

print(
    "Critical:",
    current_severity is Severity.CRITICAL,
)


# =============================================================================
# 190. COMPARISON OF ENUMS DIRECTLY
# =============================================================================

print("\n" + "=" * 80)
print("190. ENUM ORDERING LIMITATION")
print("=" * 80)

"""
Ordinary Enum members do not automatically support ordering.

If ordering is required, IntEnum or explicit .value comparison can be used.
"""

from enum import IntEnum


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


print("Priority.HIGH > Priority.LOW:", Priority.HIGH > Priority.LOW)


# =============================================================================
# 191. COMPARISON AND TYPE-SPECIFIC DESIGN
# =============================================================================

print("\n" + "=" * 80)
print("191. TYPE-SPECIFIC DESIGN")
print("=" * 80)

"""
When a comparison has domain-specific semantics, encode the semantics
explicitly instead of depending on accidental Python ordering.
"""

def priority_at_least(
    current: Priority,
    required: Priority,
) -> bool:
    return current >= required


print(
    "HIGH at least MEDIUM:",
    priority_at_least(Priority.HIGH, Priority.MEDIUM),
)


# =============================================================================
# 192. ADVANCED: COMPARISON WITH SENTINELS
# =============================================================================

print("\n" + "=" * 80)
print("192. SENTINEL OBJECT")
print("=" * 80)

MISSING = object()

data_value: Any = MISSING

if data_value is MISSING:
    print("Value is missing.")

"""
A unique object can act as a private sentinel when None is a valid
application value.
"""


# =============================================================================
# 193. COMPARISON AND API DESIGN
# =============================================================================

print("\n" + "=" * 80)
print("193. API DESIGN")
print("=" * 80)

def get_score(record: dict[str, Any]) -> int | None:
    score = record.get("score")

    if score is None:
        return None

    return int(score)


record = {"score": 85}

score = get_score(record)

if score is not None and score >= 80:
    print("High score.")


# =============================================================================
# 194. COMPARISON AND DATABASE-LIKE FILTERING
# =============================================================================

print("\n" + "=" * 80)
print("194. DATABASE-LIKE FILTERING")
print("=" * 80)

orders = [
    {"id": 1, "amount": 500, "status": "paid"},
    {"id": 2, "amount": 1500, "status": "paid"},
    {"id": 3, "amount": 2500, "status": "pending"},
]

filtered_orders = [
    order
    for order in orders
    if order["amount"] >= 1000
    and order["status"] == "paid"
]

for order in filtered_orders:
    print(order)


# =============================================================================
# 195. COMPARISON AND NULL-LIKE DATA
# =============================================================================

print("\n" + "=" * 80)
print("195. MISSING DATA")
print("=" * 80)

data_points = [10, None, 20, None, 30]

known_points = [
    point for point in data_points
    if point is not None
]

print("Known points:", known_points)


# =============================================================================
# 196. COMPARISON AND DATA CLEANING
# =============================================================================

print("\n" + "=" * 80)
print("196. DATA CLEANING")
print("=" * 80)

raw_values = ["10", " 20 ", "", "30", "invalid"]

clean_values: list[int] = []

for raw_value in raw_values:
    cleaned = raw_value.strip()

    if cleaned == "":
        continue

    if cleaned.isdigit():
        clean_values.append(int(cleaned))

print("Clean numeric values:", clean_values)


# =============================================================================
# 197. COMPARISON AND VALIDATION OF RANGES
# =============================================================================

print("\n" + "=" * 80)
print("197. RANGE VALIDATION WITH EXCEPTIONS")
print("=" * 80)

def validate_temperature(
    temperature: float,
    minimum: float = -50,
    maximum: float = 60,
) -> None:
    if not minimum <= temperature <= maximum:
        raise ValueError(
            f"Temperature must be between {minimum} and {maximum}."
        )


for temperature in [-60, -50, 25, 60, 70]:
    try:
        validate_temperature(temperature)
        print(temperature, "accepted")
    except ValueError as error:
        print(temperature, "rejected:", error)


# =============================================================================
# 198. COMPARISON AND TESTABLE RULES
# =============================================================================

print("\n" + "=" * 80)
print("198. TESTABLE BUSINESS RULES")
print("=" * 80)

def qualifies_for_discount(
    order_value: Decimal,
    customer_age: int,
) -> bool:
    return (
        order_value >= Decimal("10000")
        or customer_age >= 60
    )


assert qualifies_for_discount(Decimal("10000"), 30)
assert qualifies_for_discount(Decimal("5000"), 60)
assert not qualifies_for_discount(Decimal("5000"), 30)

print("Discount rule tests passed.")


# =============================================================================
# 199. COMPARISON OPERATOR REFERENCE
# =============================================================================

print("\n" + "=" * 80)
print("199. QUICK REFERENCE")
print("=" * 80)

reference = [
    ("==", "equal to", "a == b"),
    ("!=", "not equal to", "a != b"),
    (">", "greater than", "a > b"),
    ("<", "less than", "a < b"),
    (">=", "greater than or equal to", "a >= b"),
    ("<=", "less than or equal to", "a <= b"),
    ("in", "membership", "a in b"),
    ("not in", "non-membership", "a not in b"),
    ("is", "object identity", "a is b"),
    ("is not", "object non-identity", "a is not b"),
]

for operator, meaning, example in reference:
    print(f"{operator:<7} | {meaning:<30} | {example}")


# =============================================================================
# 200. INTEGRATED PRACTICAL EXAMPLE
# =============================================================================

print("\n" + "=" * 80)
print("200. INTEGRATED PRACTICAL EXAMPLE")
print("=" * 80)

@dataclass
class LoanApplication:
    applicant_name: str
    age: int
    monthly_income: Decimal
    credit_score: int
    existing_debt: Decimal
    requested_amount: Decimal


def evaluate_loan_application(application: LoanApplication) -> str:
    """
    Demonstrate comparison operators in a realistic decision system.

    Rules:
        - Applicant must be at least 21.
        - Monthly income must be at least 50,000.
        - Credit score must be at least 700.
        - Existing debt must be no more than 50% of annualized income.
        - Requested loan amount must not exceed 10 times monthly income.

    These are educational rules, not financial advice or a real lending model.
    """
    if application.age < 21:
        return "Rejected: age requirement not met."

    if application.monthly_income < Decimal("50000"):
        return "Rejected: income requirement not met."

    if application.credit_score < 700:
        return "Rejected: credit score requirement not met."

    annual_income = application.monthly_income * Decimal("12")
    maximum_debt = annual_income * Decimal("0.50")

    if application.existing_debt > maximum_debt:
        return "Rejected: existing debt is too high."

    maximum_requested_amount = application.monthly_income * Decimal("10")

    if application.requested_amount > maximum_requested_amount:
        return "Rejected: requested amount is too high."

    return "Approved for preliminary educational screening."


applications = [
    LoanApplication(
        applicant_name="Applicant A",
        age=30,
        monthly_income=Decimal("80000"),
        credit_score=760,
        existing_debt=Decimal("200000"),
        requested_amount=Decimal("500000"),
    ),
    LoanApplication(
        applicant_name="Applicant B",
        age=19,
        monthly_income=Decimal("80000"),
        credit_score=760,
        existing_debt=Decimal("100000"),
        requested_amount=Decimal("300000"),
    ),
    LoanApplication(
        applicant_name="Applicant C",
        age=35,
        monthly_income=Decimal("40000"),
        credit_score=760,
        existing_debt=Decimal("100000"),
        requested_amount=Decimal("300000"),
    ),
    LoanApplication(
        applicant_name="Applicant D",
        age=40,
        monthly_income=Decimal("100000"),
        credit_score=650,
        existing_debt=Decimal("100000"),
        requested_amount=Decimal("500000"),
    ),
]

for application in applications:
    print(
        application.applicant_name,
        "->",
        evaluate_loan_application(application),
    )


# =============================================================================
# FINAL AUTOMATED CHECKS
# =============================================================================

print("\n" + "=" * 80)
print("FINAL AUTOMATED CHECKS")
print("=" * 80)

# Basic operators.
assert 5 == 5
assert 5 != 6
assert 6 > 5
assert 5 < 6
assert 5 >= 5
assert 5 <= 5

# Chained comparisons.
assert 0 <= 50 <= 100

# Membership.
assert "Python" in ["Python", "SQL"]
assert "JavaScript" not in ["Python", "SQL"]

# Identity.
none_value = None
assert none_value is None

# Floating-point approximation.
assert isclose(0.1 + 0.2, 0.3)

# Set relationships.
assert {1, 2} < {1, 2, 3}

# Sequence ordering.
assert [1, 2] < [1, 3]

# Validation.
assert is_valid_age(18)
assert not is_valid_age(121)

# Algorithm.
assert binary_search([1, 2, 3, 4, 5], 3) == 2
assert binary_search([1, 2, 3, 4, 5], 8) == -1

# Domain comparison.
assert Product("A", 100) < Product("B", 200)

print("All automated comparison checks passed.")
print("\nComparison operator tutorial completed successfully.")
