"""
OPERATOR PRECEDENCE IN PYTHON
=============================

A comprehensive, executable study file covering Python operator precedence
from absolute beginner concepts through advanced expression behavior.

The examples use only Python's standard library.

Run this file directly:

    python operator_precedence.py

The script is intentionally organized from simple expressions to advanced
topics such as chained comparisons, boolean short-circuiting, conditional
expressions, assignment expressions, unpacking, lambda expressions, matrix
multiplication, custom operator overloading, and bytecode inspection.
"""

from __future__ import annotations

import ast
import dis
import math
import operator
from dataclasses import dataclass
from typing import Callable


# =============================================================================
# 1. BASIC IDEA: WHAT IS OPERATOR PRECEDENCE?
# =============================================================================

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    """Print a readable subsection heading."""
    print("\n" + "-" * 70)
    print(title)
    print("-" * 70)


def show(description: str, value) -> None:
    """Display an expression description and its resulting value."""
    print(f"{description:<58} -> {value!r}")


section("1. OPERATOR PRECEDENCE: THE BASIC IDEA")

print(
    """
Operator precedence determines which operators are evaluated before others
when an expression contains multiple operators.

For example:

    2 + 3 * 4

Multiplication has higher precedence than addition, so Python evaluates the
expression conceptually as:

    2 + (3 * 4)

The result is 14, not 20.

Precedence answers the question:
    "Which operator gets priority?"

Associativity answers a different question:
    "When operators have the same precedence, in what direction are they
     grouped?"

Parentheses can explicitly control grouping:

    (2 + 3) * 4

which produces 20.

Important distinction:
    precedence is about priority between different operators;
    associativity is about grouping operators at the same precedence level.
"""
)

show("2 + 3 * 4", 2 + 3 * 4)
show("(2 + 3) * 4", (2 + 3) * 4)
show("2 * 3 + 4", 2 * 3 + 4)
show("2 * (3 + 4)", 2 * (3 + 4))


# =============================================================================
# 2. WHY PRECEDENCE MATTERS
# =============================================================================

section("2. WHY PRECEDENCE MATTERS")

subsection("Arithmetic example")

a = 10
b = 5
c = 2

show("a + b * c", a + b * c)
show("(a + b) * c", (a + b) * c)
show("a * b - c", a * b - c)
show("a * (b - c)", a * (b - c))

print(
    """
Without understanding precedence, a programmer may read an expression in
ordinary left-to-right order and obtain the wrong mental result.

Python does not simply evaluate every expression from left to right.

For:

    10 + 5 * 2

the multiplication is performed before the addition.

For:

    10 - 5 + 2

both subtraction and addition have the same precedence, so grouping proceeds
from left to right:

    (10 - 5) + 2
"""
)

show("10 + 5 * 2", 10 + 5 * 2)
show("(10 + 5) * 2", (10 + 5) * 2)
show("10 - 5 + 2", 10 - 5 + 2)
show("(10 - 5) + 2", (10 - 5) + 2)


# =============================================================================
# 3. PYTHON OPERATOR PRECEDENCE TABLE
# =============================================================================

section("3. PYTHON OPERATOR PRECEDENCE TABLE")

print(
    """
From highest precedence to lowest precedence, Python's major expression
operators can be organized approximately as follows.

Higher
  |
  |  Parenthesized expressions, displays, calls, subscriptions
  |  Await expression
  |  **
  |  +x, -x, ~x
  |  *, @, /, //, %
  |  +, -
  |  <<, >>
  |  &
  |  ^
  |  |
  |  in, not in, is, is not, <, <=, >, >=, ==, !=
  |  not
  |  and
  |  or
  |  if ... else
  |  lambda
  |  :=
  |
Lower

Important qualifications:

1. Parentheses explicitly control grouping.
2. Function calls, indexing, and attribute access bind very strongly.
3. Exponentiation has unusual interaction with unary operators.
4. Comparisons can be chained.
5. Boolean operators use short-circuit evaluation.
6. Conditional expressions have lower precedence than most operators.
7. Assignment expressions have very low precedence and sometimes require
   parentheses depending on context.
8. The complete language grammar is more precise than a simple table.

The table is best understood together with actual examples.
"""
)


# =============================================================================
# 4. PARENTHESES
# =============================================================================

section("4. PARENTHESES HAVE THE HIGHEST PRACTICAL PRIORITY")

subsection("Changing grouping")

expressions = {
    "2 + 3 * 4": 2 + 3 * 4,
    "(2 + 3) * 4": (2 + 3) * 4,
    "2 * 3 + 4": 2 * 3 + 4,
    "2 * (3 + 4)": 2 * (3 + 4),
    "100 / 10 + 5": 100 / 10 + 5,
    "100 / (10 + 5)": 100 / (10 + 5),
}

for expression, result in expressions.items():
    show(expression, result)

print(
    """
Parentheses should be used when they improve correctness or readability.

Good:

    total = subtotal + (tax_rate * subtotal)

Good:

    result = (income - expenses) * tax_rate

Unnecessary but legal parentheses can make an expression harder to read if
they are used everywhere without purpose.

The practical rule is:
    rely on precedence when it is obvious and conventional;
    use parentheses when grouping is important to meaning.
"""
)


# =============================================================================
# 5. FUNCTION CALLS, INDEXING, AND ATTRIBUTE ACCESS
# =============================================================================

section("5. CALLS, INDEXING, AND ATTRIBUTE ACCESS")

subsection("Function calls")

def double(value: int) -> int:
    return value * 2


show("double(3) + 4", double(3) + 4)
show("double(3 + 4)", double(3 + 4))

subsection("Indexing")

numbers = [10, 20, 30, 40]

show("numbers[1] + 5", numbers[1] + 5)
show("numbers[1 + 1]", numbers[1 + 1])

subsection("Attribute access")

text = "python"

show("text.upper()", text.upper())
show("text.upper()[0]", text.upper()[0])
show("len(text) + 1", len(text) + 1)

print(
    """
Calls, subscriptions, and attribute access bind very tightly.

For example:

    numbers[1] + 5

means:

    (numbers[1]) + 5

not:

    numbers[(1 + 5)]

Likewise:

    object.method()

accesses the method before the call happens.
"""
)


# =============================================================================
# 6. EXPONENTIATION
# =============================================================================

section("6. EXPONENTIATION (**)")


show("2 ** 3", 2 ** 3)
show("2 ** 3 * 4", 2 ** 3 * 4)
show("2 * 3 ** 4", 2 * 3 ** 4)
show("(2 ** 3) * 4", (2 ** 3) * 4)

print(
    """
Exponentiation has higher precedence than multiplication.

Therefore:

    2 * 3 ** 4

means:

    2 * (3 ** 4)

not:

    (2 * 3) ** 4
"""
)


# =============================================================================
# 7. EXPONENTIATION ASSOCIATIVITY
# =============================================================================

section("7. EXPONENTIATION IS RIGHT-ASSOCIATIVE")

show("2 ** 3 ** 2", 2 ** 3 ** 2)
show("2 ** (3 ** 2)", 2 ** (3 ** 2))
show("(2 ** 3) ** 2", (2 ** 3) ** 2)

print(
    """
Most binary arithmetic operators group from left to right.

Exponentiation is an important exception: it groups from right to left.

Thus:

    2 ** 3 ** 2

is interpreted as:

    2 ** (3 ** 2)

which is:

    2 ** 9

which is:

    512

This is one of the most important exceptions to remember.
"""
)


# =============================================================================
# 8. UNARY OPERATORS AND POWER
# =============================================================================

section("8. UNARY OPERATORS AND EXPONENTIATION")

show("-2 ** 2", -2 ** 2)
show("(-2) ** 2", (-2) ** 2)
show("+2 ** 2", +2 ** 2)
show("(+2) ** 2", (+2) ** 2)

print(
    """
A subtle Python rule concerns unary + and - around exponentiation.

The expression:

    -2 ** 2

is interpreted as:

    -(2 ** 2)

so the result is -4.

The expression:

    (-2) ** 2

explicitly makes -2 the base, producing 4.

This distinction is mathematically important and frequently causes mistakes.

For negative bases with powers, parentheses are usually the clearest choice.
"""
)


# =============================================================================
# 9. MULTIPLICATIVE OPERATORS
# =============================================================================

section("9. MULTIPLICATIVE OPERATORS")

show("10 * 3", 10 * 3)
show("10 / 3", 10 / 3)
show("10 // 3", 10 // 3)
show("10 % 3", 10 % 3)

print(
    """
Multiplication, matrix multiplication, division, floor division, and modulo
share the same precedence level.

When operators share the same level, normal left-to-right grouping applies
for these binary operators.

For example:

    100 / 10 * 2

is:

    (100 / 10) * 2

not:

    100 / (10 * 2)
"""
)

show("100 / 10 * 2", 100 / 10 * 2)
show("(100 / 10) * 2", (100 / 10) * 2)
show("100 / (10 * 2)", 100 / (10 * 2))

print(
    """
Modulo and floor division have important semantic details.

For negative operands:

    // performs floor division, meaning the mathematical floor is used.
    % produces a remainder consistent with the floor-division relationship.

Examples:
"""
)

show("7 // 3", 7 // 3)
show("7 % 3", 7 % 3)
show("-7 // 3", -7 // 3)
show("-7 % 3", -7 % 3)


# =============================================================================
# 10. ADDITIVE OPERATORS
# =============================================================================

section("10. ADDITION AND SUBTRACTION")

show("10 + 5 - 2", 10 + 5 - 2)
show("(10 + 5) - 2", (10 + 5) - 2)
show("10 + (5 - 2)", 10 + (5 - 2))

print(
    """
Addition and subtraction have the same precedence and normally associate
from left to right.

Therefore:

    10 - 5 - 2

means:

    (10 - 5) - 2

not:

    10 - (5 - 2)
"""
)

show("10 - 5 - 2", 10 - 5 - 2)
show("(10 - 5) - 2", (10 - 5) - 2)
show("10 - (5 - 2)", 10 - (5 - 2))


# =============================================================================
# 11. SHIFT OPERATORS
# =============================================================================

section("11. BITWISE SHIFT OPERATORS")

show("8 << 2", 8 << 2)
show("32 >> 2", 32 >> 2)

print(
    """
Shift operators have lower precedence than addition and subtraction.

Therefore:

    1 + 2 << 3

is grouped as:

    (1 + 2) << 3
"""
)

show("1 + 2 << 3", 1 + 2 << 3)
show("(1 + 2) << 3", (1 + 2) << 3)
show("1 + (2 << 3)", 1 + (2 << 3))


# =============================================================================
# 12. BITWISE OPERATORS
# =============================================================================

section("12. BITWISE OPERATORS")

x = 12  # binary 1100
y = 10  # binary 1010

show("x & y", x & y)
show("x ^ y", x ^ y)
show("x | y", x | y)

print(
    """
The bitwise precedence hierarchy is:

    &
    ^
    |

So bitwise AND binds more strongly than XOR, which binds more strongly than
OR.

For example:

    12 | 10 & 3

is interpreted as:

    12 | (10 & 3)
"""
)

show("12 | 10 & 3", 12 | 10 & 3)
show("12 | (10 & 3)", 12 | (10 & 3))
show("(12 | 10) & 3", (12 | 10) & 3)


# =============================================================================
# 13. COMPARISON OPERATORS
# =============================================================================

section("13. COMPARISON OPERATORS")

show("5 > 3", 5 > 3)
show("5 == 5", 5 == 5)
show("5 != 3", 5 != 3)
show("5 <= 5", 5 <= 5)

print(
    """
Comparison operators include:

    <
    <=
    >
    >=
    ==
    !=
    in
    not in
    is
    is not

Comparisons produce Boolean results.

Comparison operators have lower precedence than arithmetic and bitwise
operators, so:

    5 + 2 > 6

means:

    (5 + 2) > 6
"""
)

show("5 + 2 > 6", 5 + 2 > 6)
show("(5 + 2) > 6", (5 + 2) > 6)
show("5 + (2 > 6)", 5 + (2 > 6))


# =============================================================================
# 14. CHAINED COMPARISONS
# =============================================================================

section("14. CHAINED COMPARISONS")

show("1 < 2 < 3", 1 < 2 < 3)
show("1 < 2 > 0", 1 < 2 > 0)
show("1 == 1 == True", 1 == 1 == True)

print(
    """
Python supports chained comparisons.

The expression:

    1 < 2 < 3

is conceptually similar to:

    (1 < 2) and (2 < 3)

but it is not merely textual substitution. Python evaluates the middle
operand only once.

For example:

    a < b < c

means that b must satisfy both comparisons.

This is useful for range checks:

    0 <= score <= 100

It is usually clearer than:

    score >= 0 and score <= 100
"""
)

score = 87
show("0 <= score <= 100", 0 <= score <= 100)
show("score >= 0 and score <= 100", score >= 0 and score <= 100)


# =============================================================================
# 15. COMPARISONS WITH DIFFERENT OPERATORS
# =============================================================================

section("15. COMPARISON CHAINS CAN MIX OPERATORS")

value = 50

show("0 < value <= 100", 0 < value <= 100)
show("value == 50 != 60", value == 50 != 60)
show("10 < value == 50", 10 < value == 50)

print(
    """
A comparison chain does not mean that the Boolean result of one comparison
is compared with the next operand.

For example:

    1 < 2 < 3

does not mean:

    (1 < 2) < 3

Instead, it represents:

    1 < 2 and 2 < 3

This distinction becomes important when operands are Boolean or when custom
comparison methods are involved.
"""
)


# =============================================================================
# 16. MEMBERSHIP AND IDENTITY
# =============================================================================

section("16. MEMBERSHIP AND IDENTITY")

items = ["apple", "banana", "orange"]

show('"banana" in items', "banana" in items)
show('"pear" not in items', "pear" not in items)

first = items
second = items
third = list(items)

show("first is second", first is second)
show("first is third", first is third)
show("first == third", first == third)

print(
    """
The operators == and is are not interchangeable.

    == tests value equality.
    is tests object identity.

Use is and is not primarily for identity checks, especially with None:

    value is None
    value is not None

Do not rely on object interning or implementation-specific identity behavior
for ordinary numeric or string equality.
"""
)


# =============================================================================
# 17. NOT
# =============================================================================

section("17. BOOLEAN NOT")

show("not True", not True)
show("not False", not False)
show("not 0", not 0)
show("not 10", not 10)
show("not []", not [])

print(
    """
not has lower precedence than comparisons.

Therefore:

    not 5 == 5

is interpreted as:

    not (5 == 5)

not:

    (not 5) == 5

This is why Boolean conditions can naturally be written as:

    not value == expected

although:

    value != expected

is usually clearer.
"""
)

show("not 5 == 5", not 5 == 5)
show("not (5 == 5)", not (5 == 5))
show("5 != 5", 5 != 5)


# =============================================================================
# 18. AND
# =============================================================================

section("18. BOOLEAN AND")

show("True and True", True and True)
show("True and False", True and False)
show("False and True", False and True)

print(
    """
and has lower precedence than comparisons and higher precedence than or.

An important fact:
    and does not necessarily return a Boolean object.

It returns one of its operands.

If the left operand is falsy, Python returns it immediately.

Otherwise, Python evaluates and returns the right operand.
"""
)

show("'hello' and 123", "hello" and 123)
show("'' and 123", "" and 123)
show("0 and 999", 0 and 999)
show("42 and 999", 42 and 999)


# =============================================================================
# 19. OR
# =============================================================================

section("19. BOOLEAN OR")

show("True or False", True or False)
show("False or True", False or True)

print(
    """
or also returns an operand rather than forcing the result to True or False.

If the left operand is truthy, Python returns it immediately.

Otherwise, Python evaluates and returns the right operand.
"""
)

show("'value' or 'fallback'", "value" or "fallback")
show("'' or 'fallback'", "" or "fallback")
show("0 or 42", 0 or 42)
show("42 or 99", 42 or 99)


# =============================================================================
# 20. AND HAS HIGHER PRECEDENCE THAN OR
# =============================================================================

section("20. AND BEFORE OR")

show("True or False and False", True or False and False)
show("True or (False and False)", True or (False and False))
show("(True or False) and False", (True or False) and False)

print(
    """
Because and has higher precedence than or:

    A or B and C

means:

    A or (B and C)

not:

    (A or B) and C
"""
)


# =============================================================================
# 21. SHORT-CIRCUIT EVALUATION
# =============================================================================

section("21. SHORT-CIRCUIT EVALUATION")

def announce(name: str, value: bool) -> bool:
    """Print when an operand is actually evaluated."""
    print(f"Evaluating {name!r}")
    return value


print("Example 1: False and ...")
result = announce("left", False) and announce("right", True)
show("result", result)

print("\nExample 2: True or ...")
result = announce("left", True) or announce("right", False)
show("result", result)

print(
    """
Short-circuiting is related to precedence but is a separate evaluation rule.

For:

    A and B

B is not evaluated when A is falsy.

For:

    A or B

B is not evaluated when A is truthy.

This affects correctness, performance, and safety.

A common pattern is:

    value is not None and value.process()

The method call is protected because it occurs only if the first condition
is true.
"""
)


# =============================================================================
# 22. GUARDING OPERATIONS WITH AND
# =============================================================================

section("22. USING AND AS A GUARD")

user_data = {"name": "Atul"}

show("user_data and user_data['name']", user_data and user_data["name"])

empty_data = {}

show("empty_data and empty_data['name']", empty_data and empty_data.get("name"))

print(
    """
Short-circuiting can protect an operation from being evaluated.

But readability matters. For complex conditions, explicit if statements are
often clearer than deeply nested Boolean expressions.
"""
)


# =============================================================================
# 23. CONDITIONAL EXPRESSIONS
# =============================================================================

section("23. CONDITIONAL EXPRESSIONS")

age = 25

show("'adult' if age >= 18 else 'minor'", "adult" if age >= 18 else "minor")
show("'yes' if age >= 18 else 'no'", "yes" if age >= 18 else "no")

print(
    """
Python's conditional expression has the form:

    value_if_true if condition else value_if_false

The condition is evaluated first.

Only the selected branch expression is evaluated.

This makes conditional expressions useful for compact value selection, but
complex nested conditional expressions can reduce readability.
"""
)


# =============================================================================
# 24. CONDITIONAL EXPRESSION PRECEDENCE
# =============================================================================

section("24. CONDITIONAL EXPRESSION PRECEDENCE")

result_a = 10 + 5 if True else 20
result_b = (10 + 5) if True else 20

show("10 + 5 if True else 20", result_a)
show("(10 + 5) if True else 20", result_b)

print(
    """
Most arithmetic and comparison expressions bind more strongly than the
conditional expression.

Thus:

    10 + 5 if condition else 20

selects between:

    10 + 5

and:

    20
"""
)


# =============================================================================
# 25. LAMBDA EXPRESSIONS
# =============================================================================

section("25. LAMBDA AND PRECEDENCE")

subsection("Basic lambda")

square = lambda x: x * x
show("square(5)", square(5))

print(
    """
A lambda expression creates a function:

    lambda parameters: expression

The body of the lambda is an expression.

Lambda has very low precedence. When passing a lambda to another construct,
parentheses may be necessary to make the intended structure explicit.
"""
)

functions = [
    lambda x: x + 1,
    lambda x: x * 2,
    lambda x: x ** 2,
]

for function in functions:
    show(f"lambda result for 4", function(4))


# =============================================================================
# 26. ASSIGNMENT EXPRESSIONS
# =============================================================================

section("26. ASSIGNMENT EXPRESSIONS (:=)")

print(
    """
The assignment expression operator := is commonly called the walrus operator.

It both assigns a value to a variable and produces that value as an
expression.

Example:

    if (length := len("Python")) > 3:
        ...

Parentheses are frequently used because assignment expressions have low
precedence and because many syntactic contexts require explicit grouping.
"""
)

if (length := len("Python")) > 3:
    show("length assigned by := ", length)

numbers_for_sum = [1, 2, 3, 4]
if (total := sum(numbers_for_sum)) > 5:
    show("total assigned by := ", total)


# =============================================================================
# 27. ASSIGNMENT EXPRESSIONS IN WHILE LOOPS
# =============================================================================

section("27. ASSIGNMENT EXPRESSIONS IN CONTROL FLOW")

values = iter([3, 2, 1, 0])

while (current := next(values)) != 0:
    print(f"Current value: {current}")

print("Loop stopped when the assigned value became 0.")

print(
    """
The assignment expression returns the assigned value, so it can participate
in a larger expression.

Its low precedence is deliberate. Parentheses often make the intended
condition much easier to understand.
"""
)


# =============================================================================
# 28. ASSIGNMENT IS NOT AN ORDINARY EXPRESSION
# =============================================================================

section("28. ASSIGNMENT STATEMENTS VS ASSIGNMENT EXPRESSIONS")

print(
    """
An ordinary assignment statement such as:

    x = 10

is not simply another arithmetic operator with ordinary expression
precedence.

The assignment expression:

    (x := 10)

is different. It is an expression and therefore can appear in expression
contexts where assignment statements cannot.

This distinction explains why:

    x = 10

and:

    (x := 10)

should not be treated as identical syntax.
"""
)


# =============================================================================
# 29. UNARY OPERATORS
# =============================================================================

section("29. UNARY OPERATORS")

value = 5

show("+value", +value)
show("-value", -value)
show("~value", ~value)

print(
    """
Unary operators include:

    +x
    -x
    ~x

They operate on one operand.

The bitwise inversion operator ~ has the integer relationship:

    ~x == -(x + 1)

for Python integers.
"""
)

for value in range(-3, 4):
    show(f"~{value}", ~value)


# =============================================================================
# 30. OPERATOR PRECEDENCE WITH MIXED ARITHMETIC
# =============================================================================

section("30. MIXED ARITHMETIC EXPRESSIONS")

examples = {
    "2 + 3 * 4 ** 2": 2 + 3 * 4 ** 2,
    "(2 + 3) * 4 ** 2": (2 + 3) * 4 ** 2,
    "20 // 3 + 4 * 2": 20 // 3 + 4 * 2,
    "20 / 3 + 4 ** 2": 20 / 3 + 4 ** 2,
    "2 ** 3 ** 2 + 1": 2 ** 3 ** 2 + 1,
}

for expression, result in examples.items():
    show(expression, result)

print(
    """
A reliable manual method is:

1. Identify parentheses.
2. Identify function calls, indexing, and attribute access.
3. Identify exponentiation.
4. Identify unary operators.
5. Process multiplication-family operators.
6. Process addition/subtraction.
7. Process shifts.
8. Process bitwise operators.
9. Process comparisons.
10. Process not.
11. Process and.
12. Process or.
13. Process conditional expressions.
14. Consider lambda and assignment-expression syntax where relevant.

The exact grammar should be consulted for unusual syntax.
"""
)


# =============================================================================
# 31. A BOOLEAN EXPRESSION WITH MANY PRECEDENCE LEVELS
# =============================================================================

section("31. COMPLEX BOOLEAN EXPRESSION")

score = 85
attendance = 92
is_registered = True
has_hold = False

condition = (
    score >= 50
    and attendance >= 75
    and is_registered
    and not has_hold
)

show("complex eligibility condition", condition)

equivalent_grouped = (
    (score >= 50)
    and (attendance >= 75)
    and is_registered
    and (not has_hold)
)

show("explicitly grouped condition", equivalent_grouped)

print(
    """
Explicit grouping can make a business rule easier to audit.

Even when parentheses are technically unnecessary, they can document the
intended logical structure.
"""
)


# =============================================================================
# 32. PRECEDENCE DOES NOT OVERRIDE EVALUATION RULES
# =============================================================================

section("32. PRECEDENCE VS EVALUATION ORDER")

print(
    """
Operator precedence determines how an expression is grouped.

It does not mean that every subexpression is blindly evaluated in a simple
top-to-bottom list.

Short-circuit operators can prevent evaluation of later operands.

Function-call arguments and other expression components also have their own
evaluation-order rules.

Therefore two questions should always be separated:

    1. How is the expression grouped?
    2. Which grouped parts are actually evaluated?
"""
)


# =============================================================================
# 33. FUNCTION ARGUMENTS AND PRECEDENCE
# =============================================================================

section("33. FUNCTION ARGUMENTS")

def report(*values):
    """Return arguments as a tuple so evaluation is easy to inspect."""
    return values


show("report(2 + 3, 4 * 5)", report(2 + 3, 4 * 5))
show("report((2 + 3) * 4)", report((2 + 3) * 4))

print(
    """
Commas separate function arguments. Arithmetic precedence operates inside
each argument expression.

For:

    report(2 + 3, 4 * 5)

the arguments are:

    2 + 3
    4 * 5

which become:

    5
    20
"""
)


# =============================================================================
# 34. COMPARISONS AND BOOLEAN OPERATORS
# =============================================================================

section("34. COMPARISON + BOOLEAN PRECEDENCE")

a = 10
b = 20
c = 30

show("a < b and b < c", a < b and b < c)
show("a < b or b > c", a < b or b > c)
show("not a < b", not a < b)
show("not (a < b)", not (a < b))

print(
    """
The standard structure is:

    comparisons
        ↓
    not
        ↓
    and
        ↓
    or

Therefore:

    not a < b and b < c or c == 30

is grouped roughly as:

    ((not (a < b)) and (b < c)) or (c == 30)

When a condition matters to program correctness, explicit parentheses can
make this structure much easier to verify.
"""
)


# =============================================================================
# 35. COMMON MISTAKE: AND/OR
# =============================================================================

section("35. COMMON MISTAKE: AND/OR GROUPING")

a = True
b = False
c = False

show("a or b and c", a or b and c)
show("a or (b and c)", a or (b and c))
show("(a or b) and c", (a or b) and c)

print(
    """
The first two expressions are identical because and has higher precedence.

The third expression is different because parentheses force a different
grouping.
"""
)


# =============================================================================
# 36. COMMON MISTAKE: EQUALITY VS ASSIGNMENT
# =============================================================================

section("36. COMMON MISTAKE: = VS ==")

print(
    """
The symbols have different purposes:

    =   assignment statement
    ==  equality comparison
    :=  assignment expression

Example:

    name = "Atul"

assigns a value.

Example:

    name == "Atul"

tests equality.

Example:

    if (name := get_name()) == "Atul":
        ...

assigns a value and then compares it.

Confusing = with == is a syntax or logic error depending on context.
"""
)


# =============================================================================
# 37. COMMON MISTAKE: IS VS ==
# =============================================================================

section("37. COMMON MISTAKE: IS VS ==")

value_a = [1, 2, 3]
value_b = [1, 2, 3]

show("value_a == value_b", value_a == value_b)
show("value_a is value_b", value_a is value_b)

print(
    """
Two separate list objects can contain equal values.

Therefore:

    value_a == value_b

can be True while:

    value_a is value_b

is False.

Use == for value comparison and is for identity.
"""
)


# =============================================================================
# 38. COMMON MISTAKE: NEGATIVE POWERS
# =============================================================================

section("38. COMMON MISTAKE: NEGATIVE BASES")

show("-3 ** 2", -3 ** 2)
show("(-3) ** 2", (-3) ** 2)
show("-3 ** 3", -3 ** 3)
show("(-3) ** 3", (-3) ** 3)

print(
    """
The difference is not cosmetic.

    -3 ** 2
        means
    -(3 ** 2)

while:

    (-3) ** 2
        means
    (-3) raised to the power 2
"""
)


# =============================================================================
# 39. COMMON MISTAKE: DIVISION AND MULTIPLICATION
# =============================================================================

section("39. COMMON MISTAKE: / AND *")

show("100 / 10 * 5", 100 / 10 * 5)
show("100 / (10 * 5)", 100 / (10 * 5))

print(
    """
Multiplication and division have the same precedence.

They do not mean "do all multiplication before all division."

Instead:

    100 / 10 * 5

is:

    (100 / 10) * 5
"""
)


# =============================================================================
# 40. COMMON MISTAKE: MIXED ADDITION AND SUBTRACTION
# =============================================================================

section("40. COMMON MISTAKE: + AND -")

show("20 - 5 + 2", 20 - 5 + 2)
show("(20 - 5) + 2", (20 - 5) + 2)
show("20 - (5 + 2)", 20 - (5 + 2))

print(
    """
Addition and subtraction share precedence and associate from left to right.

The same principle applies to multiplication and division.
"""
)


# =============================================================================
# 41. STRING CONCATENATION AND PRECEDENCE
# =============================================================================

section("41. STRINGS AND +")

show('"Hello " + "World"', "Hello " + "World")
show('"Value: " + str(10 + 5)', "Value: " + str(10 + 5))

print(
    """
The + operator can be overloaded by types.

For integers it performs numeric addition.

For strings it performs concatenation.

For lists it can concatenate lists.

Operator precedence remains a syntactic property, while the meaning of an
operator can depend on the operand types.
"""
)

show("[1, 2] + [3, 4]", [1, 2] + [3, 4])


# =============================================================================
# 42. TYPE-DEPENDENT OPERATOR MEANING
# =============================================================================

section("42. SAME PRECEDENCE, DIFFERENT OPERATION")

show("5 + 3", 5 + 3)
show('"5" + "3"', "5" + "3")
show("[5] + [3]", [5] + [3])

print(
    """
Precedence answers "which operation is grouped first."

It does not answer "what does the operator mean for these types?"

Python resolves operator behavior using the objects' type protocols and
special methods.
"""
)


# =============================================================================
# 43. OPERATOR OVERLOADING
# =============================================================================

section("43. CUSTOM OPERATOR OVERLOADING")

@dataclass
class NumberBox:
    """A small class demonstrating how Python operators can be overloaded."""

    value: int

    def __add__(self, other: "NumberBox") -> "NumberBox":
        return NumberBox(self.value + other.value)

    def __mul__(self, other: "NumberBox") -> "NumberBox":
        return NumberBox(self.value * other.value)

    def __pow__(self, other: int) -> "NumberBox":
        return NumberBox(self.value ** other)

    def __repr__(self) -> str:
        return f"NumberBox({self.value})"


left = NumberBox(2)
right = NumberBox(3)

show("left + right", left + right)
show("left * right", left * right)
show("left + right * left", left + right * left)
show("(left + right) * left", (left + right) * left)
show("left ** 3", left ** 3)

print(
    """
Operator precedence is determined by Python's grammar, not by the custom
class.

The class determines what an operator does after Python has already parsed
the expression.

For:

    left + right * left

Python first groups it as:

    left + (right * left)

and then invokes the appropriate special methods.
"""
)


# =============================================================================
# 44. PRECEDENCE IS DIFFERENT FROM OPERATOR IMPLEMENTATION
# =============================================================================

section("44. PRECEDENCE VS OPERATOR OVERLOADING")

print(
    """
There are two separate layers:

Syntax layer:
    Python's grammar decides that * binds more strongly than +.

Object protocol layer:
    Python invokes __mul__ and __add__ for the corresponding operations.

A custom __add__ method cannot change the precedence of +.

This is a critical distinction when designing domain-specific classes.
"""
)


# =============================================================================
# 45. MATRIX MULTIPLICATION
# =============================================================================

section("45. MATRIX MULTIPLICATION OPERATOR @")

print(
    """
Python provides @ for matrix multiplication.

Its precedence belongs to the multiplicative operator group, alongside:

    *
    /
    //
    %

A custom matrix-like object can implement __matmul__.
"""
)


@dataclass
class MatrixValue:
    """Tiny scalar-like demonstration object for the @ operator."""

    value: int

    def __matmul__(self, other: "MatrixValue") -> "MatrixValue":
        return MatrixValue(self.value * other.value)

    def __add__(self, other: "MatrixValue") -> "MatrixValue":
        return MatrixValue(self.value + other.value)

    def __repr__(self) -> str:
        return f"MatrixValue({self.value})"


m1 = MatrixValue(2)
m2 = MatrixValue(3)
m3 = MatrixValue(4)

show("m1 + m2 @ m3", m1 + m2 @ m3)
show("(m1 + m2) @ m3", (m1 + m2) @ m3)


# =============================================================================
# 46. OPERATOR PRECEDENCE WITH COLLECTIONS
# =============================================================================

section("46. COLLECTION EXPRESSIONS")

numbers = [1, 2, 3, 4, 5]

show("numbers[1 + 1]", numbers[1 + 1])
show("numbers[2] * 10", numbers[2] * 10)

squares = [number ** 2 for number in numbers]
show("[number ** 2 for number in numbers]", squares)

filtered = [number for number in numbers if number % 2 == 0]
show("[number for number in numbers if number % 2 == 0]", filtered)

print(
    """
Comprehensions contain their own syntax and expression structure.

Inside:

    number ** 2

exponentiation applies to number and 2.

Inside:

    number % 2 == 0

modulo has higher precedence than equality comparison.
"""
)


# =============================================================================
# 47. CONDITIONAL EXPRESSIONS INSIDE COMPREHENSIONS
# =============================================================================

section("47. CONDITIONAL EXPRESSIONS AND COMPREHENSIONS")

numbers = list(range(1, 7))

labels = [
    "even" if number % 2 == 0 else "odd"
    for number in numbers
]

show("conditional expression in comprehension", labels)

print(
    """
The conditional expression:

    "even" if number % 2 == 0 else "odd"

is the element expression.

The comprehension's filtering clause, when present, is a separate syntactic
component.

These structures should not be confused.
"""
)


# =============================================================================
# 48. GENERATOR EXPRESSIONS
# =============================================================================

section("48. GENERATOR EXPRESSIONS")

numbers = range(1, 6)

generator = (number ** 2 for number in numbers)

show("list(generator)", list(generator))

print(
    """
Generator expressions use expression precedence in the same way as other
expressions, while changing evaluation strategy.

The values are generated lazily rather than all being materialized immediately.
"""
)


# =============================================================================
# 49. F-STRINGS AND EXPRESSION PRECEDENCE
# =============================================================================

section("49. EXPRESSIONS INSIDE F-STRINGS")

name = "Python"
x = 5
y = 3

show('f"{x + y}"', f"{x + y}")
show('f"{x * y}"', f"{x * y}")
show('f"{x ** y}"', f"{x ** y}")

formatted = f"{name}: {x + y * 2}"
show('f"{name}: {x + y * 2}"', formatted)

print(
    """
Expressions inside f-string replacement fields follow ordinary Python
expression rules.

The surrounding string syntax does not change operator precedence inside
the expression.
"""
)


# =============================================================================
# 50. OPERATOR PRECEDENCE AND FUNCTION RETURN VALUES
# =============================================================================

section("50. RETURN VALUES IN EXPRESSIONS")

def get_base() -> int:
    print("get_base() called")
    return 2


def get_exponent() -> int:
    print("get_exponent() called")
    return 3


result = get_base() ** get_exponent() + 1
show("get_base() ** get_exponent() + 1", result)

print(
    """
Function calls bind tightly.

The calls produce values, and those values then participate in the larger
expression according to operator precedence.
"""
)


# =============================================================================
# 51. EXPLICITLY REWRITING AN EXPRESSION
# =============================================================================

section("51. MANUAL PARENTHESIZATION")

original = 3 + 4 * 2 ** 3 - 5
explicit = 3 + (4 * (2 ** 3)) - 5

show("3 + 4 * 2 ** 3 - 5", original)
show("3 + (4 * (2 ** 3)) - 5", explicit)

print(
    """
Adding parentheses to show the precedence structure is a useful learning
technique.

The expression:

    3 + 4 * 2 ** 3 - 5

can be made structurally explicit as:

    3 + (4 * (2 ** 3)) - 5

The result remains the same because the parentheses document the grouping
already chosen by Python.
"""
)


# =============================================================================
# 52. AST INSPECTION
# =============================================================================

section("52. ABSTRACT SYNTAX TREE (AST)")

expression = "3 + 4 * 2 ** 3 - 5"

tree = ast.parse(expression, mode="eval")

print(f"Expression: {expression}")
print("AST:")
print(ast.dump(tree, indent=4))

print(
    """
The AST is a useful way to inspect how Python parsed an expression.

The tree structure reveals nested operations.

For example, multiplication appears beneath the addition/subtraction structure,
and exponentiation appears beneath multiplication.

This demonstrates that precedence is reflected in the parsed structure.
"""
)


# =============================================================================
# 53. AST FOR BOOLEAN PRECEDENCE
# =============================================================================

section("53. AST FOR BOOLEAN PRECEDENCE")

boolean_expression = "a or b and not c"
boolean_tree = ast.parse(boolean_expression, mode="eval")

print(f"Expression: {boolean_expression}")
print(ast.dump(boolean_tree, indent=4))

print(
    """
The AST shows that:

    not c

is grouped before:

    b and not c

which is grouped before:

    a or ...

This corresponds to:

    a or (b and (not c))
"""
)


# =============================================================================
# 54. AST FOR COMPARISON CHAINS
# =============================================================================

section("54. AST FOR CHAINED COMPARISONS")

comparison_expression = "1 < x < 10"
comparison_tree = ast.parse(comparison_expression, mode="eval")

print(f"Expression: {comparison_expression}")
print(ast.dump(comparison_tree, indent=4))

print(
    """
A chained comparison is represented as one comparison node containing
multiple operators and comparands.

This is another reason not to think of:

    1 < x < 10

as ordinary left-to-right binary operations.
"""
)


# =============================================================================
# 55. AST FOR ASSIGNMENT EXPRESSIONS
# =============================================================================

section("55. AST FOR ASSIGNMENT EXPRESSIONS")

walrus_expression = "(n := 10) + 5"
walrus_tree = ast.parse(walrus_expression, mode="eval")

print(f"Expression: {walrus_expression}")
print(ast.dump(walrus_tree, indent=4))


# =============================================================================
# 56. BYTECODE INSPECTION
# =============================================================================

section("56. BYTECODE AND EXPRESSION EVALUATION")

def precedence_demo() -> int:
    return 3 + 4 * 2 ** 3


print("Disassembly of precedence_demo:")
dis.dis(precedence_demo)

print(
    """
The dis module exposes CPython bytecode.

Bytecode is an implementation-level detail, not the definition of Python
syntax itself. Different Python implementations or compiler versions can
change bytecode.

The AST and language grammar are more appropriate for reasoning about
precedence.

Bytecode can still be useful when investigating actual CPython execution.
"""
)


# =============================================================================
# 57. CONSTANT FOLDING
# =============================================================================

section("57. CONSTANT FOLDING")

def constant_expression() -> int:
    return 3 + 4 * 2


show("constant_expression()", constant_expression())

print("Disassembly:")
dis.dis(constant_expression)

print(
    """
CPython may evaluate constant expressions during compilation.

For example:

    3 + 4 * 2

contains only constants, so the compiler can often replace the computation
with the resulting constant.

This is called constant folding.

Do not confuse compiler optimization with operator precedence. Precedence
determines the expression's meaning before optimization.
"""
)


# =============================================================================
# 58. PRECEDENCE AND SIDE EFFECTS
# =============================================================================

section("58. PRECEDENCE AND SIDE EFFECTS")

events: list[str] = []


def record(name: str, value: int) -> int:
    events.append(name)
    return value


events.clear()
result = record("A", 1) + record("B", 2) * record("C", 3)

show("result", result)
show("evaluation events", events)

print(
    """
Precedence determines that multiplication belongs inside the addition:

    A + (B * C)

The function calls still have observable evaluation behavior.

When expressions contain side effects, excessive complexity can make code
hard to reason about. Splitting a complicated expression into named steps
is often safer.
"""
)


# =============================================================================
# 59. SIDE EFFECTS AND SHORT-CIRCUITING
# =============================================================================

section("59. SIDE EFFECTS WITH SHORT-CIRCUITING")

events.clear()

result = record("left", 0) and record("right", 100)

show("result", result)
show("evaluation events", events)

events.clear()

result = record("left", 1) or record("right", 100)

show("result", result)
show("evaluation events", events)

print(
    """
The right side is skipped in both examples because of short-circuiting.

This can be useful, but side effects hidden inside Boolean expressions can
make behavior surprising.

Prefer simple, explicit control flow when evaluation has important side
effects.
"""
)


# =============================================================================
# 60. OPERATOR PRECEDENCE VS MATHEMATICAL CONVENTION
# =============================================================================

section("60. PYTHON PRECEDENCE VS MATHEMATICAL NOTATION")

print(
    """
Python follows many familiar mathematical conventions:

    exponentiation before multiplication
    multiplication before addition
    comparisons after arithmetic

But Python is a programming language, not a mathematical notation system.

Examples of language-specific behavior include:

    and / or returning operands
    is testing identity
    chained comparisons
    assignment expressions
    overloaded operators
    floor division
    string/list concatenation with +
    short-circuit evaluation

Therefore mathematical intuition is useful but not sufficient.
"""
)


# =============================================================================
# 61. BOOLEAN VALUES ARE INTEGERS
# =============================================================================

section("61. BOOL AND INTEGER RELATIONSHIP")

show("True == 1", True == 1)
show("False == 0", False == 0)
show("True + True", True + True)
show("False * 100", False * 100)

print(
    """
bool is a subclass of int in Python.

Therefore:

    True behaves numerically like 1
    False behaves numerically like 0

This does not mean Boolean logic should be replaced with arithmetic in every
case. Clear Boolean expressions are usually preferable for conditions.
"""
)


# =============================================================================
# 62. COMPARISON RESULT VS AND/OR OPERAND RESULT
# =============================================================================

section("62. BOOLEAN OPERATORS DO NOT ALWAYS RETURN BOOL")

show("1 < 2", 1 < 2)
show("1 and 2", 1 and 2)
show("0 and 2", 0 and 2)
show("0 or 2", 0 or 2)
show("5 or 2", 5 or 2)

print(
    """
Comparisons normally produce bool objects.

and and or return one of their operands.

This difference is important when using Boolean expressions for fallback
values:

    value = user_value or default_value

The expression returns user_value when it is truthy; otherwise it returns
default_value.

This pattern has an important edge case: legitimate falsy values such as 0,
False, or an empty string will also trigger the fallback.
"""
)


# =============================================================================
# 63. FALLBACK VALUE EDGE CASE
# =============================================================================

section("63. EDGE CASE: OR FALLBACKS")

user_value = 0
default_value = 100

show("user_value or default_value", user_value or default_value)

print(
    """
If 0 is a valid value and should not trigger a fallback, use an explicit
None check instead:

    value = user_value if user_value is not None else default_value
"""
)

show(
    "explicit None-style fallback",
    user_value if user_value is not None else default_value,
)


# =============================================================================
# 64. COMPARISON WITH NONE
# =============================================================================

section("64. CORRECT NONE CHECKS")

possibly_missing = None

show("possibly_missing is None", possibly_missing is None)
show("possibly_missing is not None", possibly_missing is not None)

print(
    """
The preferred idiom for None is:

    value is None
    value is not None

rather than:

    value == None
    value != None

Identity is the appropriate semantic test for the singleton None object.
"""
)


# =============================================================================
# 65. OPERATOR PRECEDENCE IN VALIDATION
# =============================================================================

section("65. PRACTICAL VALIDATION EXAMPLE")

def valid_percentage(value: float) -> bool:
    """Validate that a percentage lies in the inclusive range 0 to 100."""
    return 0 <= value <= 100


for percentage in [-1, 0, 50, 100, 101]:
    show(f"valid_percentage({percentage})", valid_percentage(percentage))

print(
    """
Chained comparisons make inclusive range validation concise and readable:

    0 <= value <= 100

The equivalent expanded form is:

    0 <= value and value <= 100

The chained version is generally easier to read.
"""
)


# =============================================================================
# 66. PRACTICAL FINANCE-STYLE EXAMPLE
# =============================================================================

section("66. PRACTICAL FINANCIAL CALCULATION")

principal = 100_000
annual_rate = 0.08
years = 5

future_value = principal * (1 + annual_rate) ** years

show("future value", future_value)

print(
    """
The expression:

    principal * (1 + annual_rate) ** years

relies on precedence:

    1 + annual_rate
        happens inside parentheses

    (...) ** years
        happens next

    principal * (...)
        happens last

Parentheses around the rate adjustment are essential to the intended formula.
"""
)


# =============================================================================
# 67. PRACTICAL DISCOUNT EXAMPLE
# =============================================================================

section("67. PRACTICAL DISCOUNT CALCULATION")

price = 2_500
discount = 0.20
tax = 0.18

discounted_price = price * (1 - discount)
final_price = discounted_price * (1 + tax)

show("discounted_price", discounted_price)
show("final_price", final_price)

print(
    """
Breaking a financial calculation into named stages is often safer than
writing a single complicated expression.

It makes assumptions and precedence visible.
"""
)


# =============================================================================
# 68. PRACTICAL CONDITIONAL LOGIC
# =============================================================================

section("68. PRACTICAL CONDITIONAL LOGIC")

income = 800_000
age = 35
resident = True

eligible = (
    income > 500_000
    and age >= 18
    and resident
)

show("eligible", eligible)

print(
    """
Named Boolean variables can make precedence easier to understand than one
very long expression.

When a business rule becomes complex, decompose it into meaningful predicates.
"""
)


# =============================================================================
# 69. NESTED BOOLEAN EXPRESSIONS
# =============================================================================

section("69. COMPLEX BOOLEAN PRECEDENCE")

has_account = True
is_verified = True
is_admin = False
is_owner = True

access = (
    has_account
    and is_verified
    and (is_admin or is_owner)
)

show("access", access)

print(
    """
The parentheses around:

    is_admin or is_owner

make the intended rule explicit:

    a verified account is required
    and the user must be either an administrator or owner
"""
)


# =============================================================================
# 70. PRECEDENCE AND READABILITY
# =============================================================================

section("70. READABILITY PRINCIPLES")

print(
    """
Correct precedence is not the only consideration.

Consider:

    if age >= 18 and country == "IN" or is_special_case:

Python has a valid interpretation, but a reader may not immediately know
whether the intended rule was:

    (age >= 18 and country == "IN") or is_special_case

or:

    age >= 18 and (country == "IN" or is_special_case)

If the distinction matters, write the parentheses.

Good code makes the intended logic visible rather than forcing the reader
to reconstruct precedence mentally.
"""
)


# =============================================================================
# 71. PRECEDENCE AND PERFORMANCE
# =============================================================================

section("71. PERFORMANCE CONSIDERATIONS")

print(
    """
Operator precedence itself generally has negligible runtime cost.

Performance differences usually come from:

    short-circuiting
    repeated function calls
    expensive operands
    temporary objects
    overloaded operator implementations
    algorithmic complexity

For example:

    cheap_condition and expensive_operation()

can avoid the expensive operation when cheap_condition is false.

This is a consequence of short-circuit evaluation, not a special speed
property of the precedence table.
"""
)


# =============================================================================
# 72. PERFORMANCE EXAMPLE WITH SHORT-CIRCUITING
# =============================================================================

section("72. PERFORMANCE-RELEVANT SHORT-CIRCUITING")

def expensive_check() -> bool:
    print("expensive_check() executed")
    return True


condition = False and expensive_check()
show("False and expensive_check()", condition)

condition = True or expensive_check()
show("True or expensive_check()", condition)

print(
    """
Neither expensive_check() call executes because the left side already
determines the result.

This can reduce unnecessary work, but the condition should still be logically
correct. Short-circuiting should not be used merely as a cryptic optimization.
"""
)


# =============================================================================
# 73. SECURITY CONSIDERATIONS
# =============================================================================

section("73. SECURITY CONSIDERATIONS")

print(
    """
Operator precedence is not itself a security boundary.

A dangerous pattern is dynamically constructing and evaluating arbitrary
Python expressions from untrusted input using mechanisms such as eval().

For example, an application should not assume that restricting visible
operators makes arbitrary eval() safe.

Safer designs parse input into a controlled grammar or use explicit mappings
from allowed operations to functions.

Precedence still matters when implementing a safe expression parser because
the parser must reproduce the intended grammar and grouping rules.
"""
)


# =============================================================================
# 74. SAFE OPERATOR DISPATCH
# =============================================================================

section("74. SAFE OPERATOR DISPATCH")

allowed_operations: dict[str, Callable[[float, float], float]] = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "//": operator.floordiv,
    "%": operator.mod,
    "**": operator.pow,
}

left_value = 10
right_value = 3

for symbol in ["+", "-", "*", "/", "//", "%", "**"]:
    function = allowed_operations[symbol]
    result = function(left_value, right_value)
    show(f"10 {symbol} 3", result)

print(
    """
The operator module provides function equivalents for many Python operators.

This is useful when an application needs a controlled set of operations
without dynamically executing arbitrary source code.

A full expression parser still requires grammar handling for precedence,
parentheses, associativity, names, literals, and other syntax.
"""
)


# =============================================================================
# 75. WRITING A SIMPLE PRECEDENCE-AWARE CALCULATOR
# =============================================================================

section("75. SIMPLE PRECEDENCE-AWARE CALCULATOR")

print(
    """
A calculator that supports multiple operators cannot correctly evaluate
arbitrary expressions by simply splitting on operators.

For example:

    2 + 3 * 4

requires multiplication to be recognized before addition.

A real expression parser normally has:

    lexical analysis
    parsing
    precedence handling
    evaluation

Python itself performs these stages for Python expressions.
"""
)


# =============================================================================
# 76. SHUNTING-YARD CONCEPT
# =============================================================================

section("76. SHUNTING-YARD PARSING CONCEPT")

print(
    """
One classical approach for expression parsing is the shunting-yard algorithm.

The parser maintains:

    output queue
    operator stack

Each operator receives metadata such as:

    precedence
    associativity
    arity

For example, a simplified table might be:

    **    high       right
    *     medium     left
    /     medium     left
    +     low        left
    -     low        left

The algorithm uses this information to transform infix expressions into
postfix notation or another representation suitable for evaluation.

Python's parser is considerably more sophisticated because Python syntax
contains many constructs beyond arithmetic.
"""
)


# =============================================================================
# 77. MINI PRECEDENCE TABLE IMPLEMENTATION
# =============================================================================

section("77. A SMALL PRECEDENCE TABLE")

operator_info = {
    "**": {"precedence": 4, "associativity": "right"},
    "*": {"precedence": 3, "associativity": "left"},
    "/": {"precedence": 3, "associativity": "left"},
    "+": {"precedence": 2, "associativity": "left"},
    "-": {"precedence": 2, "associativity": "left"},
}

for symbol, metadata in operator_info.items():
    print(
        f"{symbol:>2} | precedence={metadata['precedence']} "
        f"| associativity={metadata['associativity']}"
    )

print(
    """
This miniature table is not Python's complete grammar. It is an educational
representation of the concepts needed by a basic arithmetic parser.
"""
)


# =============================================================================
# 78. ASSOCIATIVITY EXAMPLES
# =============================================================================

section("78. ASSOCIATIVITY")

show("100 / 10 / 2", 100 / 10 / 2)
show("(100 / 10) / 2", (100 / 10) / 2)
show("100 / (10 / 2)", 100 / (10 / 2))

show("2 ** 3 ** 2", 2 ** 3 ** 2)
show("2 ** (3 ** 2)", 2 ** (3 ** 2))
show("(2 ** 3) ** 2", (2 ** 3) ** 2)

print(
    """
Associativity becomes important when operators of the same precedence occur
without parentheses.

For ordinary arithmetic multiplication and division, grouping is left to
right.

For exponentiation, grouping is right to left.
"""
)


# =============================================================================
# 79. OPERATOR PRECEDENCE DOES NOT MEAN LEFT OPERAND FIRST FOR EVERYTHING
# =============================================================================

section("79. PRECEDENCE AND ASSOCIATIVITY ARE DIFFERENT")

print(
    """
Consider:

    2 ** 3 ** 2

Precedence tells us that exponentiation is the relevant operation.

Associativity tells us that the grouping is:

    2 ** (3 ** 2)

If you only memorize "high precedence" without understanding associativity,
you can still evaluate this expression incorrectly.
"""
)


# =============================================================================
# 80. COMPARISON CHAINS AND SIDE EFFECTS
# =============================================================================

section("80. CHAINED COMPARISONS EVALUATE MIDDLE OPERANDS ONCE")

class Counter:
    """Object used to show observable evaluation in a comparison chain."""

    def __init__(self, value: int, name: str):
        self.value = value
        self.name = name

    def __lt__(self, other):
        print(f"{self.name} < {getattr(other, 'name', other)}")
        other_value = getattr(other, "value", other)
        return self.value < other_value

    def __repr__(self):
        return self.name


left = Counter(1, "left")
middle = Counter(2, "middle")
right = Counter(3, "right")

result = left < middle < right
show("left < middle < right", result)

print(
    """
The middle operand participates in both comparisons but is evaluated only
once.

This is one of the semantic advantages of Python's chained-comparison syntax.
"""
)


# =============================================================================
# 81. COMPARISON OPERATORS CAN BE OVERLOADED
# =============================================================================

section("81. CUSTOM COMPARISON OPERATORS")

@dataclass
class ComparableValue:
    value: int
    name: str

    def __lt__(self, other: "ComparableValue") -> bool:
        print(f"Comparing {self.name} < {other.name}")
        return self.value < other.value


first = ComparableValue(1, "first")
second = ComparableValue(2, "second")
third = ComparableValue(3, "third")

show("first < second < third", first < second < third)


# =============================================================================
# 82. OPERATOR PRECEDENCE WITH NOT AND COMPARISONS
# =============================================================================

section("82. NOT BINDS LESS TIGHTLY THAN COMPARISONS")

numbers = [1, 2, 3]

show("not 2 in numbers", not 2 in numbers)
show("not (2 in numbers)", not (2 in numbers))
show("2 not in numbers", 2 not in numbers)

print(
    """
Membership operators participate in the comparison precedence level.

Therefore:

    not 2 in numbers

means:

    not (2 in numbers)

The dedicated form:

    2 not in numbers

is generally clearer.
"""
)


# =============================================================================
# 83. PRECEDENCE WITH IS
# =============================================================================

section("83. NOT AND IS")

value = None

show("not value is None", not value is None)
show("not (value is None)", not (value is None))
show("value is not None", value is not None)

print(
    """
The grammar makes:

    not value is None

equivalent in grouping to:

    not (value is None)

The idiomatic form for a positive None check is simply:

    value is None
"""
)


# =============================================================================
# 84. PRECEDENCE WITH MEMBERSHIP
# =============================================================================

section("84. MEMBERSHIP + BOOLEAN OPERATORS")

allowed = {"admin", "editor"}
role = "editor"
active = True

show("role in allowed and active", role in allowed and active)
show("(role in allowed) and active", (role in allowed) and active)

print(
    """
Membership comparisons bind more strongly than and.

Therefore:

    role in allowed and active

means:

    (role in allowed) and active
"""
)


# =============================================================================
# 85. PRECEDENCE WITH BITWISE AND COMPARISON
# =============================================================================

section("85. BITWISE OPERATORS VS COMPARISONS")

value = 6

show("value & 2 == 2", value & 2 == 2)
show("(value & 2) == 2", (value & 2) == 2)
show("value & (2 == 2)", value & (2 == 2))

print(
    """
Bitwise AND has higher precedence than comparison.

Therefore:

    value & 2 == 2

is grouped as:

    (value & 2) == 2

Parentheses are recommended when mixing bitwise logic and comparisons because
the intended operation is easier to read.
"""
)


# =============================================================================
# 86. PRECEDENCE WITH SHIFTS AND ADDITION
# =============================================================================

section("86. SHIFTS VS ADDITION")

show("1 << 2 + 1", 1 << 2 + 1)
show("1 << (2 + 1)", 1 << (2 + 1))
show("(1 << 2) + 1", (1 << 2) + 1)

print(
    """
Addition has higher precedence than shifts.

Thus:

    1 << 2 + 1

means:

    1 << (2 + 1)
"""
)


# =============================================================================
# 87. PRECEDENCE WITH BITWISE OPERATORS
# =============================================================================

section("87. BITWISE PRECEDENCE HIERARCHY")

show("1 | 2 ^ 3 & 4", 1 | 2 ^ 3 & 4)
show("1 | (2 ^ (3 & 4))", 1 | (2 ^ (3 & 4)))
show("(1 | 2) ^ 3 & 4", (1 | 2) ^ 3 & 4)

print(
    """
Bitwise precedence is:

    &   highest among these
    ^
    |   lowest among these

This differs from Boolean precedence and should not be assumed to be
interchangeable with and, xor-like logic, or.
"""
)


# =============================================================================
# 88. BOOLEAN AND BITWISE OPERATORS ARE DIFFERENT
# =============================================================================

section("88. AND VS BITWISE AND")

show("True and False", True and False)
show("1 & 0", 1 & 0)
show("True & False", True & False)

print(
    """
and is a Boolean short-circuit operator that returns an operand.

& is a bitwise operator that invokes the bitwise AND protocol.

For custom objects, their behavior can be very different.

Do not substitute one for the other simply because both can appear to
represent "AND" in informal discussion.
"""
)


# =============================================================================
# 89. OPERATOR FUNCTIONS
# =============================================================================

section("89. THE OPERATOR MODULE")

operator_examples = [
    ("operator.add", operator.add, 4, 5),
    ("operator.sub", operator.sub, 4, 5),
    ("operator.mul", operator.mul, 4, 5),
    ("operator.pow", operator.pow, 4, 2),
    ("operator.lt", operator.lt, 4, 5),
    ("operator.eq", operator.eq, 4, 4),
]

for name, function, left, right in operator_examples:
    show(name, function(left, right))

print(
    """
The operator module exposes function forms of many operators.

This is particularly useful with:

    map()
    sorted()
    key functions
    dispatch tables
    higher-order functions

It does not change the precedence of operators in source expressions.
"""
)


# =============================================================================
# 90. SORTING WITH OPERATOR FUNCTIONS
# =============================================================================

section("90. OPERATOR FUNCTIONS IN PRACTICAL CODE")

records = [
    {"name": "A", "score": 82},
    {"name": "B", "score": 95},
    {"name": "C", "score": 71},
]

sorted_records = sorted(records, key=operator.itemgetter("score"), reverse=True)

show("records sorted by score", sorted_records)

print(
    """
Here itemgetter("score") creates a callable that retrieves the score field.

No expression precedence issue is involved in the key function itself, but
operator functions provide a clean way to represent operations as objects.
"""
)


# =============================================================================
# 91. ADVANCED: PARENTHESIS AS A DESIGN TOOL
# =============================================================================

section("91. PARENTHESES AS A DESIGN TOOL")

print(
    """
Parentheses serve several purposes:

1. Change the result by changing grouping.
2. Document an intended grouping.
3. Satisfy grammar requirements in some contexts.
4. Make maintenance safer.
5. Reduce ambiguity in mixed logical or arithmetic expressions.

Example:

    result = base * (1 + rate) ** periods

is much easier to verify than an expression relying on a reader to infer
every precedence level.
"""
)


# =============================================================================
# 92. WHEN PARENTHESES ARE ESSENTIAL
# =============================================================================

section("92. WHEN PARENTHESES ARE ESSENTIAL")

base = -2
exponent = 4

show("base ** exponent", base ** exponent)
show("(-2) ** exponent", (-2) ** exponent)
show("-(2 ** exponent)", -(2 ** exponent))

print(
    """
When a negative number is intended to be the base of an exponent, parentheses
are essential for the usual mathematical interpretation.
"""
)


# =============================================================================
# 93. WHEN PARENTHESES IMPROVE CLARITY
# =============================================================================

section("93. WHEN PARENTHESES IMPROVE CLARITY")

temperature = 25
minimum = 0
maximum = 40

condition = minimum <= temperature <= maximum
explicit_condition = (minimum <= temperature) and (temperature <= maximum)

show("minimum <= temperature <= maximum", condition)
show("explicit comparison grouping", explicit_condition)

print(
    """
Both forms express the same range test.

For chained comparisons, Python already provides a clear syntax, so additional
parentheses may not be necessary.

For complex combinations of and/or, parentheses are often more valuable.
"""
)


# =============================================================================
# 94. EDGE CASE: FLOATING-POINT COMPARISONS
# =============================================================================

section("94. EDGE CASE: FLOATING-POINT EQUALITY")

value = 0.1 + 0.2

show("0.1 + 0.2", value)
show("0.1 + 0.2 == 0.3", value == 0.3)
show("math.isclose(0.1 + 0.2, 0.3)", math.isclose(value, 0.3))

print(
    """
Operator precedence cannot solve numerical representation issues.

The expression:

    0.1 + 0.2 == 0.3

is syntactically straightforward but may be False because binary floating
point cannot represent many decimal fractions exactly.

For approximate numerical comparison, math.isclose() can be appropriate.
"""
)


# =============================================================================
# 95. EDGE CASE: DIVISION BY ZERO
# =============================================================================

section("95. EDGE CASE: EXCEPTIONS")

def safe_divide(left: float, right: float) -> float | None:
    """Return None instead of allowing division by zero to escape."""
    try:
        return left / right
    except ZeroDivisionError:
        return None


show("safe_divide(10, 2)", safe_divide(10, 2))
show("safe_divide(10, 0)", safe_divide(10, 0))

print(
    """
Correct precedence does not guarantee that an expression is valid at runtime.

Expressions can raise exceptions such as:

    ZeroDivisionError
    TypeError
    OverflowError
    ValueError

depending on the operators and operand types.
"""
)


# =============================================================================
# 96. EDGE CASE: MIXED TYPES
# =============================================================================

section("96. EDGE CASE: MIXED OPERAND TYPES")

try:
    result = "10" + 5
except TypeError as error:
    print(f'"10" + 5 -> TypeError: {error}')

try:
    result = 10 + None
except TypeError as error:
    print(f"10 + None -> TypeError: {error}")

print(
    """
Precedence determines grouping, but Python still requires compatible
operations between operand types.

For example:

    "10" + 5

is grouped unambiguously but is invalid because string concatenation and
integer addition are not automatically combined.
"""
)


# =============================================================================
# 97. EDGE CASE: CUSTOM TYPES
# =============================================================================

section("97. EDGE CASE: CUSTOM TYPE SEMANTICS")

print(
    """
Custom classes can define special methods such as:

    __add__
    __sub__
    __mul__
    __truediv__
    __pow__
    __lt__
    __eq__
    __and__
    __or__
    __xor__
    __matmul__

The grammar still determines precedence.

The custom type determines the runtime behavior of the selected operation.
"""
)


# =============================================================================
# 98. EDGE CASE: NAN COMPARISONS
# =============================================================================

section("98. EDGE CASE: NaN")

nan = float("nan")

show("nan == nan", nan == nan)
show("nan < 1", nan < 1)
show("nan > 1", nan > 1)
show("nan != nan", nan != nan)

print(
    """
Special floating-point values can make ordinary comparison intuition fail.

NaN is not equal to itself.

This is a numerical semantics issue, not a precedence issue.
"""
)


# =============================================================================
# 99. PRECEDENCE IN REAL-WORLD CODE REVIEW
# =============================================================================

section("99. CODE REVIEW CHECKLIST")

print(
    """
When reviewing a complex expression, ask:

1. Are parentheses changing the intended grouping?
2. Are exponentiation and unary operators behaving as intended?
3. Are operators of equal precedence grouped correctly?
4. Is exponentiation's right associativity relevant?
5. Are comparison chains intentional?
6. Is not applied to the intended comparison?
7. Is and applied before or after the intended or?
8. Are and/or return-value semantics being relied upon?
9. Could short-circuiting skip a required side effect?
10. Are is and == being used correctly?
11. Are bitwise and Boolean operators being distinguished?
12. Could a falsy value unexpectedly trigger an or fallback?
13. Would named intermediate variables improve readability?
14. Could an exception occur in any operand?
15. Are overloaded operators changing the meaning of the operations?
"""
)


# =============================================================================
# 100. REFACTORING A COMPLEX EXPRESSION
# =============================================================================

section("100. REFACTORING COMPLEX EXPRESSIONS")

age = 30
income = 900_000
verified = True
country = "IN"

compact = age >= 18 and income > 500_000 and verified and (
    country == "IN" or country == "US"
)

is_adult = age >= 18
meets_income = income > 500_000
is_verified = verified
is_supported_country = country in {"IN", "US"}

readable = (
    is_adult
    and meets_income
    and is_verified
    and is_supported_country
)

show("compact condition", compact)
show("refactored condition", readable)

print(
    """
The refactored version exposes the business concepts.

This can be preferable when a condition is likely to be modified, reviewed,
tested, or audited.
"""
)


# =============================================================================
# 101. PRECEDENCE AND TESTING
# =============================================================================

section("101. TESTING EXPRESSION BEHAVIOR")

def eligibility(age: int, verified: bool, country: str) -> bool:
    return age >= 18 and verified and country in {"IN", "US"}


test_cases = [
    (18, True, "IN"),
    (17, True, "IN"),
    (18, False, "IN"),
    (18, True, "UK"),
    (30, True, "US"),
]

for test_case in test_cases:
    show(f"eligibility{test_case}", eligibility(*test_case))

print(
    """
For precedence-sensitive logic, tests should cover boundaries and combinations,
not only the most obvious successful case.

Useful test categories include:

    true/true
    true/false
    false/true
    false/false
    boundary values
    empty values
    None
    unexpected types
    exceptional values

The exact categories depend on the expression's purpose.
"""
)


# =============================================================================
# 102. ASSERTIONS FOR CORE PRECEDENCE FACTS
# =============================================================================

section("102. EXECUTABLE PRECEDENCE ASSERTIONS")

assert 2 + 3 * 4 == 14
assert (2 + 3) * 4 == 20

assert 2 ** 3 ** 2 == 512
assert (2 ** 3) ** 2 == 64

assert -2 ** 2 == -4
assert (-2) ** 2 == 4

assert 100 / 10 * 2 == 20
assert 100 / (10 * 2) == 5

assert 1 < 2 < 3
assert not (1 > 2)

assert True or False and False is True

print("All core precedence assertions passed.")


# =============================================================================
# 103. PRECEDENCE QUIZ WITH ANSWERS
# =============================================================================

section("103. PRECEDENCE PRACTICE")

practice_questions = [
    ("2 + 3 * 4", 14),
    ("2 * 3 + 4", 10),
    ("2 ** 3 ** 2", 512),
    ("-2 ** 2", -4),
    ("(-2) ** 2", 4),
    ("10 - 3 - 2", 5),
    ("10 / 2 * 5", 25),
    ("True or False and False", True),
    ("not 2 == 3", True),
    ("1 < 2 < 3", True),
]

for expression, expected in practice_questions:
    actual = eval(expression)
    status = "PASS" if actual == expected else "FAIL"
    print(f"{status:<5} {expression:<30} expected={expected!r}, actual={actual!r}")

print(
    """
The practice section uses eval() only with hard-coded, trusted expressions
inside this educational script.

Never pass untrusted user input to eval().
"""
)


# =============================================================================
# 104. WHY eval() IS NOT A SAFE GENERAL CALCULATOR
# =============================================================================

section("104. WHY UNTRUSTED EVAL IS DANGEROUS")

print(
    """
eval() parses and executes Python expressions.

It is therefore not a safe general-purpose mechanism for evaluating arbitrary
user input.

A production calculator that accepts user expressions should define exactly
what syntax is allowed and parse it using a restricted grammar or another
safe evaluation strategy.

Operator precedence is one part of such a grammar.
"""
)


# =============================================================================
# 105. ADVANCED: BUILDING A SIMPLE PRECEDENCE-AWARE EVALUATOR
# =============================================================================

section("105. ADVANCED: SIMPLE PRECEDENCE-AWARE EVALUATOR")

print(
    """
The following educational evaluator supports only:

    non-negative integers
    +
    -
    *
    /
    parentheses

It does not execute arbitrary Python.

Its grammar is:

    expression := term ((+ | -) term)*
    term       := factor ((* | /) factor)*
    factor     := integer | '(' expression ')'

Because expression calls term and term calls factor, multiplication/division
naturally receive higher precedence than addition/subtraction.
"""
)


class SimpleArithmeticParser:
    """
    Small recursive-descent parser demonstrating precedence through grammar.

    Grammar:

        expression := term ((+ | -) term)*
        term       := factor ((* | /) factor)*
        factor     := integer | '(' expression ')'

    This is intentionally limited and educational.
    """

    def __init__(self, source: str):
        self.source = source
        self.position = 0

    def parse(self) -> float:
        value = self.parse_expression()
        self.skip_spaces()

        if self.position != len(self.source):
            raise ValueError(
                f"Unexpected character at position {self.position}: "
                f"{self.source[self.position]!r}"
            )

        return value

    def skip_spaces(self) -> None:
        while self.position < len(self.source) and self.source[self.position].isspace():
            self.position += 1

    def parse_expression(self) -> float:
        value = self.parse_term()

        while True:
            self.skip_spaces()

            if self.match("+"):
                value += self.parse_term()
            elif self.match("-"):
                value -= self.parse_term()
            else:
                return value

    def parse_term(self) -> float:
        value = self.parse_factor()

        while True:
            self.skip_spaces()

            if self.match("*"):
                value *= self.parse_factor()
            elif self.match("/"):
                divisor = self.parse_factor()

                if divisor == 0:
                    raise ZeroDivisionError("division by zero")

                value /= divisor
            else:
                return value

    def parse_factor(self) -> float:
        self.skip_spaces()

        if self.match("("):
            value = self.parse_expression()

            self.skip_spaces()

            if not self.match(")"):
                raise ValueError("Missing closing parenthesis")

            return value

        return self.parse_number()

    def parse_number(self) -> float:
        self.skip_spaces()

        start = self.position

        while self.position < len(self.source) and self.source[self.position].isdigit():
            self.position += 1

        if start == self.position:
            raise ValueError(
                f"Expected integer at position {self.position}"
            )

        return float(self.source[start:self.position])

    def match(self, character: str) -> bool:
        self.skip_spaces()

        if self.position < len(self.source) and self.source[self.position] == character:
            self.position += 1
            return True

        return False


calculator_examples = [
    "2 + 3 * 4",
    "(2 + 3) * 4",
    "20 / 2 + 3",
    "20 / (2 + 3)",
    "100 - 10 * 5 + 2",
]

for expression in calculator_examples:
    result = SimpleArithmeticParser(expression).parse()
    show(expression, result)


# =============================================================================
# 106. PARSER PRECEDENCE EXPLAINED
# =============================================================================

section("106. HOW THE MINI PARSER IMPLEMENTS PRECEDENCE")

print(
    """
The parser does not need a separate numeric precedence value for this small
grammar.

Instead, precedence is encoded structurally:

    parse_expression()
        calls parse_term()

    parse_term()
        calls parse_factor()

Therefore multiplication and division are handled inside a term before the
term is combined by addition or subtraction.

This is a fundamental parser-design technique.
"""
)


# =============================================================================
# 107. EXTENDING THE MINI PARSER WITH EXPONENTIATION
# =============================================================================

section("107. EXTENDING A PARSER WITH EXPONENTIATION")

print(
    """
Exponentiation introduces an important additional requirement.

Because Python-style exponentiation is right-associative:

    2 ** 3 ** 2

must become:

    2 ** (3 ** 2)

A recursive-descent grammar can encode this by making the exponent parser
recurse on the right side.

Conceptually:

    power := unary | unary '**' power

rather than a loop that naturally produces left association.

The exact Python grammar also has subtle interactions between power and
unary operators.
"""
)


# =============================================================================
# 108. PRECEDENCE AND GRAMMAR DESIGN
# =============================================================================

section("108. PRECEDENCE AS A GRAMMAR PROPERTY")

print(
    """
A language grammar can encode precedence through:

    layered grammar rules
    precedence declarations
    parse-expression functions
    Pratt parsing
    precedence-climbing algorithms
    shunting-yard algorithms

For a compiler or interpreter, precedence is not merely documentation.

It directly affects the parse tree and therefore program meaning.
"""
)


# =============================================================================
# 109. PRATT PARSING CONCEPT
# =============================================================================

section("109. PRATT PARSING CONCEPT")

print(
    """
Pratt parsing is another technique for parsing expressions.

Each token can have binding-power information.

A token with stronger binding power captures a larger part of the surrounding
expression.

This approach can elegantly handle:

    prefix operators
    infix operators
    postfix operators
    different precedence levels
    associativity

For example:

    ** can receive high right-binding behavior
    * can receive medium binding behavior
    + can receive lower binding behavior

Pratt parsers are useful when designing expression-rich languages.
"""
)


# =============================================================================
# 110. PRECEDENCE-CLIMBING CONCEPT
# =============================================================================

section("110. PRECEDENCE-CLIMBING PARSING")

print(
    """
Precedence climbing is an expression-parsing technique that uses precedence
levels to decide when recursive parsing should stop or continue.

A simplified conceptual rule is:

    parse the left operand
    inspect the next operator
    if its precedence is high enough:
        consume it
        parse the right operand
        combine both sides

Associativity changes the threshold used when parsing the right operand.

This provides a compact way to implement arithmetic expression grammars.
"""
)


# =============================================================================
# 111. OPERATOR PRECEDENCE AND DOMAIN-SPECIFIC LANGUAGES
# =============================================================================

section("111. DOMAIN-SPECIFIC LANGUAGES")

print(
    """
If a program defines its own expression language, operator precedence becomes
a design decision.

A DSL might define:

    + and -
    * and /
    comparisons
    logical operators
    custom operators

The designer must specify:

    precedence
    associativity
    arity
    valid operand types
    evaluation semantics
    error behavior

Ambiguous precedence rules create difficult-to-debug programs.
"""
)


# =============================================================================
# 112. OPERATOR PRECEDENCE AND API DESIGN
# =============================================================================

section("112. OPERATOR OVERLOADING AND API DESIGN")

print(
    """
Operator overloading can make mathematical or domain-specific objects
expressive.

For example:

    price * quantity

may be natural for a custom numeric object.

But overloading should preserve intuitive semantics where possible.

An overloaded operator should not surprise readers by performing an unrelated
action merely because the syntax happens to be available.

Precedence is fixed by Python, so API designers should understand how their
operators combine with existing operators.
"""
)


# =============================================================================
# 113. ADVANCED EDGE CASE: REFLECTED OPERATORS
# =============================================================================

section("113. REFLECTED OPERATOR METHODS")

print(
    """
Binary operators can involve reflected methods.

For example:

    a + b

normally relates to:

    a.__add__(b)

and, depending on the types and return behavior, Python may consider:

    b.__radd__(a)

The same general idea exists for several binary operators.

This is part of Python's data model.

It affects operator implementation, not the source-level precedence of +.
"""
)


# =============================================================================
# 114. ADVANCED EDGE CASE: IN-PLACE OPERATORS
# =============================================================================

section("114. IN-PLACE OPERATORS")

values = [1, 2]

values += [3]
show("values after += ", values)

number = 10
number *= 2
show("number after *= ", number)

print(
    """
Operators such as:

    +=
    -=
    *=
    /=
    //=
    %=
    **=
    @=
    &= 
    |=
    ^=

are assignment statements with augmented-operation semantics.

They should not be treated as ordinary binary operators that merely return
a value.

For mutable objects, an in-place operation may mutate the existing object.
For immutable objects, a new object may be produced.
"""
)


# =============================================================================
# 115. PRECEDENCE OF AUGMENTED ASSIGNMENT
# =============================================================================

section("115. AUGMENTED ASSIGNMENT AND EXPRESSION STRUCTURE")

print(
    """
Consider:

    x *= 2 + 3

The right-hand expression is:

    2 + 3

so the operation effectively uses the computed value 5.

Augmented assignment itself is a statement-level construct, not simply a
low-precedence binary expression.
"""
)

x = 10
x *= 2 + 3
show("x after x *= 2 + 3", x)


# =============================================================================
# 116. PRECEDENCE AND UNPACKING
# =============================================================================

section("116. UNPACKING AND EXPRESSIONS")

values = [1, 2, 3]

a, b, c = values
show("a", a)
show("b", b)
show("c", c)

print(
    """
Unpacking assignment has its own statement syntax.

Expressions used to produce the iterable are evaluated according to normal
expression rules before assignment occurs.

For example:

    a, b = 1 + 2, 3 * 4

contains two independent expressions on the right-hand side.
"""
)

a, b = 1 + 2, 3 * 4
show("a from 1 + 2", a)
show("b from 3 * 4", b)


# =============================================================================
# 117. PRECEDENCE AND TUPLE CONSTRUCTION
# =============================================================================

section("117. COMMA VS OPERATOR PRECEDENCE")

pair = 1 + 2, 3 * 4
show("1 + 2, 3 * 4", pair)

print(
    """
The comma constructs a tuple in many expression contexts.

The arithmetic expressions on each side are evaluated according to their
normal precedence.

Thus:

    1 + 2, 3 * 4

produces:

    (3, 12)

The comma is syntactic structure, not simply another arithmetic operator.
"""
)


# =============================================================================
# 118. PRECEDENCE AND STARRED EXPRESSIONS
# =============================================================================

section("118. STARRED EXPRESSIONS")

values = [1, 2, 3]
combined = [0, *values, 4]

show("[0, *values, 4]", combined)

print(
    """
The * in unpacking syntax is not the same operation as multiplication.

Its meaning depends on syntactic context.

This is a broader lesson:
    identical symbols can participate in different grammar constructs.

Precedence tables should therefore not be treated as a universal list of
every possible use of a symbol.
"""
)


# =============================================================================
# 119. PRECEDENCE AND DICTIONARY UNPACKING
# =============================================================================

section("119. DICTIONARY UNPACKING")

base_config = {"timeout": 10}
override_config = {"timeout": 30, "retries": 3}

merged = {**base_config, **override_config}

show("merged configuration", merged)

print(
    """
Dictionary unpacking with ** is syntax for mapping expansion in a dictionary
display.

It is not exponentiation in this context.

Again, syntactic context determines the meaning of the symbol.
"""
)


# =============================================================================
# 120. OPERATOR PRECEDENCE AND PEP-STYLE READABILITY
# =============================================================================

section("120. PRACTICAL STYLE GUIDANCE")

print(
    """
Good practices:

1. Use parentheses when they communicate intent.
2. Keep Boolean conditions readable.
3. Prefer named intermediate variables for complex business rules.
4. Avoid relying on obscure precedence facts when readability suffers.
5. Be especially careful with ** and unary -.
6. Remember that and/or return operands.
7. Distinguish is from ==.
8. Use chained comparisons when they naturally express a range.
9. Do not mix bitwise and Boolean operators casually.
10. Avoid side effects inside complicated expressions.
11. Do not use eval() for untrusted expressions.
12. Test boundary cases for precedence-sensitive logic.
13. Understand overloaded operators in custom classes.
14. Keep custom operator semantics intuitive.
"""
)


# =============================================================================
# 121. PERFORMANCE BENCHMARKING PRINCIPLE
# =============================================================================

section("121. PERFORMANCE MEASUREMENT")

print(
    """
Do not assume that a particular parenthesization is faster merely because it
looks simpler.

Precedence usually changes grouping and therefore semantics.

Performance should be measured with representative workloads.

When performance matters, investigate:

    algorithmic complexity
    repeated computation
    object allocation
    function-call overhead
    short-circuit opportunities
    I/O
    numerical libraries
    compiler/runtime behavior

Correctness and clarity come before micro-optimizing expression syntax.
"""
)


# =============================================================================
# 122. DEBUGGING PRECEDENCE ERRORS
# =============================================================================

section("122. DEBUGGING PRECEDENCE ERRORS")

print(
    """
A practical debugging method is:

1. Copy the original expression.
2. Identify each operator.
3. Mark each operator's precedence.
4. Mark associativity where operators share a level.
5. Add parentheses to represent the expected grouping.
6. Print intermediate values.
7. Compare with the actual result.
8. Convert complex conditions into named Boolean variables.
9. Test edge cases.
10. Inspect the AST when parsing behavior is unclear.

The ast module is particularly useful when the question is:
    "How did Python parse this?"
"""
)


# =============================================================================
# 123. DEBUGGING WITH INTERMEDIATE VALUES
# =============================================================================

section("123. DEBUGGING BY DECOMPOSITION")

a = 4
b = 2
c = 3

step_one = c ** 2
step_two = b * step_one
step_three = a + step_two

show("step_one = c ** 2", step_one)
show("step_two = b * step_one", step_two)
show("step_three = a + step_two", step_three)

direct_result = a + b * c ** 2

show("direct expression", direct_result)

assert step_three == direct_result

print(
    """
Breaking an expression into intermediate variables is a powerful way to
debug precedence and identify incorrect assumptions.
"""
)


# =============================================================================
# 124. PRECEDENCE QUICK REFERENCE
# =============================================================================

section("124. QUICK REFERENCE")

precedence_reference = [
    ("Highest", "Parentheses, calls, indexing, attribute access"),
    ("", "await"),
    ("", "**"),
    ("", "+x, -x, ~x"),
    ("", "*, @, /, //, %"),
    ("", "+, -"),
    ("", "<<, >>"),
    ("", "&"),
    ("", "^"),
    ("", "|"),
    ("", "comparisons, in, not in, is, is not"),
    ("", "not"),
    ("", "and"),
    ("", "or"),
    ("", "if ... else"),
    ("", "lambda"),
    ("Lowest", ":="),
]

for level, operators in precedence_reference:
    print(f"{level:<8} {operators}")


# =============================================================================
# 125. FINAL EXECUTABLE KNOWLEDGE CHECK
# =============================================================================

section("125. FINAL KNOWLEDGE CHECK")

knowledge_checks = {
    "Multiplication before addition": 2 + 3 * 4 == 14,
    "Parentheses override precedence": (2 + 3) * 4 == 20,
    "Power is right-associative": 2 ** 3 ** 2 == 512,
    "Unary minus and power": -2 ** 2 == -4,
    "Parenthesized negative base": (-2) ** 2 == 4,
    "Division/multiplication are left-associative": 100 / 10 * 2 == 20,
    "Comparison chain": 1 < 2 < 3,
    "not after comparison precedence": not (5 == 4),
    "and before or": True or False and False,
    "Boolean and returns operands": (10 and 20) == 20,
    "Boolean or returns operands": (0 or 20) == 20,
    "Range comparison": 0 <= 50 <= 100,
    "Identity check": (None is None),
}

passed = 0

for description, result in knowledge_checks.items():
    status = "PASS" if result else "FAIL"
    print(f"{status:<5} {description}")
    passed += bool(result)

print(f"\nKnowledge checks passed: {passed}/{len(knowledge_checks)}")

assert passed == len(knowledge_checks)


# =============================================================================
# 126. KEY TAKEAWAYS AS EXECUTABLE DATA
# =============================================================================

section("126. CORE RULES")

core_rules = [
    "Parentheses explicitly control grouping.",
    "Calls, indexing, and attribute access bind very strongly.",
    "Exponentiation has high precedence and is right-associative.",
    "Unary +, -, and ~ have their own precedence relationship with power.",
    "Multiplicative operators bind more strongly than additive operators.",
    "Shifts bind less strongly than addition/subtraction.",
    "Bitwise precedence is &: ^: | from higher to lower.",
    "Comparisons have lower precedence than arithmetic and bitwise operations.",
    "Python supports chained comparisons.",
    "not binds more tightly than and.",
    "and binds more tightly than or.",
    "and/or short-circuit and return operands.",
    "Conditional expressions have low precedence.",
    "lambda has very low precedence.",
    "Assignment expressions have very low precedence.",
    "Precedence determines grouping, not the runtime meaning of overloaded operators.",
    "Short-circuiting determines whether some operands are evaluated.",
    "Readability can justify explicit parentheses even when they are unnecessary.",
    "eval() must not be treated as a safe evaluator for untrusted input.",
]

for index, rule in enumerate(core_rules, start=1):
    print(f"{index:02d}. {rule}")


# =============================================================================
# 127. SCRIPT COMPLETION
# =============================================================================

section("127. COMPLETION")

print(
    """
This script has demonstrated operator precedence from basic arithmetic
through parsing, AST inspection, short-circuit evaluation, chained
comparisons, assignment expressions, custom operators, parser design,
performance, debugging, security, and production-oriented readability.

The central principle is:

    precedence determines grouping,
    associativity determines grouping direction for equal-precedence
    operators,
    and evaluation rules determine which grouped expressions actually run.

When an expression is difficult to reason about, make the grouping explicit
with parentheses or decompose the expression into named intermediate values.
"""
)
