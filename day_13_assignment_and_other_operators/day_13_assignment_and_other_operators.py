"""
Assignment and Other Operators in Python
=========================================

A comprehensive standalone study script covering Python assignment operators
and other major operator categories from beginner to advanced level.

The script is intentionally executable. Run it directly with Python 3.9+
to observe the examples and demonstrations.

Topics covered:
- Assignment operator
- Multiple assignment
- Chained assignment
- Unpacking assignment
- Extended iterable unpacking
- Swap assignment
- Augmented assignment operators
- Assignment expressions (walrus operator)
- Arithmetic operators
- Comparison operators
- Logical operators
- Identity operators
- Membership operators
- Bitwise operators
- Conditional expressions
- Operator precedence and associativity
- Short-circuit evaluation
- Comparison chaining
- Floating-point considerations
- Integer division and modulo
- Boolean behavior
- Operator overloading
- Special methods such as __add__, __eq__, __lt__, __contains__
- Matrix multiplication operator
- Custom operator implementations
- Practical validation examples
- Edge cases
- Common mistakes
- Performance considerations
- Debugging and testing
"""

from __future__ import annotations

import math
import operator
from dataclasses import dataclass
from decimal import Decimal
from functools import reduce
from typing import Any, Iterable


# ============================================================================
# 1. BASIC ASSIGNMENT
# ============================================================================

def demonstrate_basic_assignment() -> None:
    """
    Assignment stores or binds a value to a variable name.

    The = symbol is an assignment operator, not a mathematical equality sign.
    """

    print("\n" + "=" * 80)
    print("1. BASIC ASSIGNMENT")
    print("=" * 80)

    age = 25
    name = "Atul"
    height = 1.75
    is_student = True

    print("age =", age)
    print("name =", name)
    print("height =", height)
    print("is_student =", is_student)

    # Assignment can replace an earlier value.
    age = 26
    print("Updated age =", age)

    # Python variables are names bound to objects.
    number = 100
    another_number = number

    print("number =", number)
    print("another_number =", another_number)

    # The two names currently refer to the same immutable integer object.
    print("number is another_number:", number is another_number)


# ============================================================================
# 2. MULTIPLE ASSIGNMENT
# ============================================================================

def demonstrate_multiple_assignment() -> None:
    """
    Python permits several assignment forms that make code concise.
    """

    print("\n" + "=" * 80)
    print("2. MULTIPLE ASSIGNMENT")
    print("=" * 80)

    # Multiple variables can receive multiple values.
    first, second, third = 10, 20, 30

    print(first, second, third)

    # The number of variables must normally match the number of values.
    # The following would raise ValueError:
    #
    # first, second = 10, 20, 30

    # Multiple assignment is useful when initializing related variables.
    width, height = 1920, 1080
    print("Resolution:", width, "x", height)

    # Variables can also be initialized to the same value.
    x = y = z = 0

    print("x =", x)
    print("y =", y)
    print("z =", z)


# ============================================================================
# 3. CHAINED ASSIGNMENT
# ============================================================================

def demonstrate_chained_assignment() -> None:
    """
    Chained assignment binds multiple names to the same resulting object.

    Be careful with mutable objects: all names can refer to the same object.
    """

    print("\n" + "=" * 80)
    print("3. CHAINED ASSIGNMENT")
    print("=" * 80)

    a = b = c = 50

    print("a =", a)
    print("b =", b)
    print("c =", c)

    # Mutable-object example.
    first_list = second_list = []

    first_list.append("shared")

    print("first_list =", first_list)
    print("second_list =", second_list)
    print("first_list is second_list:", first_list is second_list)

    # To create separate lists, use separate expressions.
    independent_first = []
    independent_second = []

    independent_first.append("only first")

    print("independent_first =", independent_first)
    print("independent_second =", independent_second)


# ============================================================================
# 4. UNPACKING ASSIGNMENT
# ============================================================================

def demonstrate_unpacking_assignment() -> None:
    """
    Unpacking extracts elements from an iterable into separate variables.
    """

    print("\n" + "=" * 80)
    print("4. UNPACKING ASSIGNMENT")
    print("=" * 80)

    coordinates = (10, 20)

    x, y = coordinates

    print("x =", x)
    print("y =", y)

    # Strings are iterable, so their characters can also be unpacked.
    first, second, third = "ABC"

    print(first, second, third)

    # Lists and tuples can both be unpacked.
    values = [100, 200, 300]
    first_value, second_value, third_value = values

    print(first_value, second_value, third_value)


# ============================================================================
# 5. EXTENDED UNPACKING
# ============================================================================

def demonstrate_extended_unpacking() -> None:
    """
    The * operator captures zero or more remaining elements.
    """

    print("\n" + "=" * 80)
    print("5. EXTENDED UNPACKING")
    print("=" * 80)

    numbers = [1, 2, 3, 4, 5]

    first, *middle, last = numbers

    print("first =", first)
    print("middle =", middle)
    print("last =", last)

    first, *remaining = numbers

    print("first =", first)
    print("remaining =", remaining)

    *beginning, last = numbers

    print("beginning =", beginning)
    print("last =", last)

    # The starred target receives a list.
    values = (10, 20, 30)
    first_value, *rest = values

    print("Type of rest:", type(rest).__name__)
    print("rest =", rest)

    # A starred target may legally receive zero elements.
    first_only, *empty_rest = [99]

    print("first_only =", first_only)
    print("empty_rest =", empty_rest)


# ============================================================================
# 6. SWAP ASSIGNMENT
# ============================================================================

def demonstrate_swap_assignment() -> None:
    """
    Python can swap variables without a temporary variable.
    """

    print("\n" + "=" * 80)
    print("6. SWAP ASSIGNMENT")
    print("=" * 80)

    left = 10
    right = 20

    print("Before:", left, right)

    left, right = right, left

    print("After:", left, right)

    # This is safer and clearer than manually creating a temporary variable
    # for ordinary Python object references.


# ============================================================================
# 7. AUGMENTED ASSIGNMENT
# ============================================================================

def demonstrate_augmented_assignment() -> None:
    """
    Augmented assignment combines an operation with assignment.

    Common forms:
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
        <<=
        >>=
    """

    print("\n" + "=" * 80)
    print("7. AUGMENTED ASSIGNMENT")
    print("=" * 80)

    value = 10

    value += 5
    print("After += :", value)

    value -= 3
    print("After -= :", value)

    value *= 2
    print("After *= :", value)

    value /= 4
    print("After /= :", value)

    value //= 2
    print("After //= :", value)

    value %= 3
    print("After %= :", value)

    value **= 3
    print("After **= :", value)

    bit_value = 12

    bit_value &= 10
    print("After &= :", bit_value)

    bit_value |= 8
    print("After |= :", bit_value)

    bit_value ^= 3
    print("After ^= :", bit_value)

    bit_value <<= 1
    print("After <<= :", bit_value)

    bit_value >>= 2
    print("After >>= :", bit_value)


# ============================================================================
# 8. AUGMENTED ASSIGNMENT WITH MUTABLE OBJECTS
# ============================================================================

def demonstrate_mutable_augmented_assignment() -> None:
    """
    Augmented assignment can behave differently depending on whether a type
    supports in-place operations.

    Lists commonly mutate in place for +=.
    """

    print("\n" + "=" * 80)
    print("8. AUGMENTED ASSIGNMENT AND MUTABILITY")
    print("=" * 80)

    values = [1, 2]

    original_id = id(values)

    values += [3, 4]

    print("values =", values)
    print("Same list object:", id(values) == original_id)

    tuple_values = (1, 2)
    tuple_original_id = id(tuple_values)

    tuple_values += (3, 4)

    print("tuple_values =", tuple_values)
    print(
        "Same tuple object:",
        id(tuple_values) == tuple_original_id,
    )

    # A tuple is immutable, so += creates a new tuple.


# ============================================================================
# 9. ASSIGNMENT EXPRESSIONS
# ============================================================================

def demonstrate_assignment_expression() -> None:
    """
    The walrus operator := assigns a value while producing that value as
    an expression.

    It is useful when a calculated value is needed immediately in a condition
    or loop.
    """

    print("\n" + "=" * 80)
    print("9. ASSIGNMENT EXPRESSIONS")
    print("=" * 80)

    if (length := len("Python")) > 5:
        print("Length =", length)

    numbers = [2, 4, 6, 8]

    while (count := len(numbers)) > 0:
        print("Remaining elements:", count)
        numbers.pop()

    # Assignment expressions should improve clarity rather than make code
    # unnecessarily compact.

    text = "hello"

    if (upper_text := text.upper()) == "HELLO":
        print("Computed value:", upper_text)


# ============================================================================
# 10. ARITHMETIC OPERATORS
# ============================================================================

def demonstrate_arithmetic_operators() -> None:
    """
    Arithmetic operators perform numerical calculations.

    +   addition
    -   subtraction
    *   multiplication
    /   true division
    //  floor division
    %   modulo
    **  exponentiation
    @   matrix multiplication
    """

    print("\n" + "=" * 80)
    print("10. ARITHMETIC OPERATORS")
    print("=" * 80)

    a = 17
    b = 5

    print("a + b  =", a + b)
    print("a - b  =", a - b)
    print("a * b  =", a * b)
    print("a / b  =", a / b)
    print("a // b =", a // b)
    print("a % b  =", a % b)
    print("a ** b =", a ** b)

    # Unary operators.
    print("+a =", +a)
    print("-a =", -a)

    # Parentheses change evaluation order.
    print("a + b * 2 =", a + b * 2)
    print("(a + b) * 2 =", (a + b) * 2)


# ============================================================================
# 11. FLOOR DIVISION AND NEGATIVE NUMBERS
# ============================================================================

def demonstrate_floor_division_edge_cases() -> None:
    """
    // means floor division, not simply truncation toward zero.

    Floor means rounding toward negative infinity.
    """

    print("\n" + "=" * 80)
    print("11. FLOOR DIVISION EDGE CASES")
    print("=" * 80)

    print("7 // 2 =", 7 // 2)
    print("-7 // 2 =", -7 // 2)

    print("7 % 2 =", 7 % 2)
    print("-7 % 2 =", -7 % 2)

    # Python maintains the relationship:
    #
    # a == (a // b) * b + (a % b)
    #
    # whenever b is not zero.

    a = -7
    b = 2

    print(
        "Verification:",
        a == (a // b) * b + (a % b),
    )


# ============================================================================
# 12. DIVISION BY ZERO
# ============================================================================

def demonstrate_division_errors() -> None:
    """
    Division, modulo, and floor division by zero raise ZeroDivisionError.
    """

    print("\n" + "=" * 80)
    print("12. DIVISION BY ZERO")
    print("=" * 80)

    operations = [
        ("division", lambda: 10 / 0),
        ("floor division", lambda: 10 // 0),
        ("modulo", lambda: 10 % 0),
    ]

    for operation_name, operation_function in operations:
        try:
            operation_function()
        except ZeroDivisionError as error:
            print(f"{operation_name}: {type(error).__name__}: {error}")


# ============================================================================
# 13. COMPARISON OPERATORS
# ============================================================================

def demonstrate_comparison_operators() -> None:
    """
    Comparison operators return Boolean values.

    ==  equal
    !=  not equal
    <   less than
    <=  less than or equal
    >   greater than
    >=  greater than or equal
    """

    print("\n" + "=" * 80)
    print("13. COMPARISON OPERATORS")
    print("=" * 80)

    x = 10
    y = 20

    print("x == y:", x == y)
    print("x != y:", x != y)
    print("x < y :", x < y)
    print("x <= y:", x <= y)
    print("x > y :", x > y)
    print("x >= y:", x >= y)

    # Comparison results are bool values.
    result = x < y
    print("Type of result:", type(result).__name__)


# ============================================================================
# 14. COMPARISON CHAINING
# ============================================================================

def demonstrate_comparison_chaining() -> None:
    """
    Python supports chained comparisons.

    a < b < c

    is conceptually equivalent to:

    a < b and b < c

    with the middle expression evaluated only once.
    """

    print("\n" + "=" * 80)
    print("14. COMPARISON CHAINING")
    print("=" * 80)

    age = 25

    print("18 <= age < 60:", 18 <= age < 60)

    score = 85

    if 0 <= score <= 100:
        print("Score is within the valid range.")

    # Chained comparisons are often clearer than repeating a variable.


# ============================================================================
# 15. LOGICAL OPERATORS
# ============================================================================

def demonstrate_logical_operators() -> None:
    """
    Logical operators:

    and
    or
    not
    """

    print("\n" + "=" * 80)
    print("15. LOGICAL OPERATORS")
    print("=" * 80)

    is_logged_in = True
    is_admin = False

    print("logged in AND admin:", is_logged_in and is_admin)
    print("logged in OR admin:", is_logged_in or is_admin)
    print("NOT admin:", not is_admin)

    age = 30
    has_permission = True

    can_enter = age >= 18 and has_permission

    print("Can enter:", can_enter)


# ============================================================================
# 16. SHORT-CIRCUIT EVALUATION
# ============================================================================

def demonstrate_short_circuiting() -> None:
    """
    and/or use short-circuit evaluation.

    For:
        A and B

    B is evaluated only if A is truthy.

    For:
        A or B

    B is evaluated only if A is falsy.
    """

    print("\n" + "=" * 80)
    print("16. SHORT-CIRCUIT EVALUATION")
    print("=" * 80)

    def announce(name: str, value: Any) -> Any:
        print("Evaluating:", name)
        return value

    result = announce("first", False) and announce("second", True)

    print("AND result:", result)

    result = announce("first", True) or announce("second", False)

    print("OR result:", result)

    # This behavior is useful for safe access patterns.
    denominator = 0

    if denominator != 0 and 100 / denominator > 1:
        print("Safe calculation.")

    # The division is never evaluated because denominator != 0 is False.


# ============================================================================
# 17. AND/OR RETURN OPERANDS, NOT NECESSARILY BOOL
# ============================================================================

def demonstrate_truthy_operand_return() -> None:
    """
    and and or return one of their operands rather than forcing a bool.

    This is an important distinction between logical operators and comparisons.
    """

    print("\n" + "=" * 80)
    print("17. LOGICAL OPERATORS RETURN OPERANDS")
    print("=" * 80)

    print("'Python' and 100 =", "Python" and 100)
    print("'' and 100 =", "" and 100)

    print("'Python' or 100 =", "Python" or 100)
    print("'' or 100 =", "" or 100)

    # Common default-value pattern:
    user_name = ""

    display_name = user_name or "Guest"

    print("display_name =", display_name)


# ============================================================================
# 18. IDENTITY OPERATORS
# ============================================================================

def demonstrate_identity_operators() -> None:
    """
    Identity operators:

    is
    is not

    They test object identity, not value equality.
    """

    print("\n" + "=" * 80)
    print("18. IDENTITY OPERATORS")
    print("=" * 80)

    first_list = [1, 2, 3]
    second_list = [1, 2, 3]
    same_reference = first_list

    print("first_list == second_list:", first_list == second_list)
    print("first_list is second_list:", first_list is second_list)

    print(
        "first_list is same_reference:",
        first_list is same_reference,
    )

    # is is appropriate for singleton objects such as None.
    value = None

    print("value is None:", value is None)

    # Do not use "is" as a general replacement for ==.


# ============================================================================
# 19. MEMBERSHIP OPERATORS
# ============================================================================

def demonstrate_membership_operators() -> None:
    """
    Membership operators:

    in
    not in

    They test whether an item belongs to a container or iterable.
    """

    print("\n" + "=" * 80)
    print("19. MEMBERSHIP OPERATORS")
    print("=" * 80)

    numbers = [10, 20, 30]

    print("20 in numbers:", 20 in numbers)
    print("99 in numbers:", 99 in numbers)
    print("99 not in numbers:", 99 not in numbers)

    text = "Python programming"

    print("'Python' in text:", "Python" in text)
    print("'Java' in text:", "Java" in text)

    dictionary = {"name": "Atul", "age": 30}

    # Membership in a dictionary checks keys by default.
    print("'name' in dictionary:", "name" in dictionary)
    print("'Atul' in dictionary:", "Atul" in dictionary)


# ============================================================================
# 20. BITWISE OPERATORS
# ============================================================================

def demonstrate_bitwise_operators() -> None:
    """
    Bitwise operators work on integer binary representations.

    &   AND
    |   OR
    ^   XOR
    ~   NOT
    <<  left shift
    >>  right shift
    """

    print("\n" + "=" * 80)
    print("20. BITWISE OPERATORS")
    print("=" * 80)

    a = 12
    b = 10

    print("a =", a, "binary =", bin(a))
    print("b =", b, "binary =", bin(b))

    print("a & b =", a & b)
    print("a | b =", a | b)
    print("a ^ b =", a ^ b)
    print("~a =", ~a)
    print("a << 1 =", a << 1)
    print("a >> 1 =", a >> 1)

    # For positive integers, left shift by one position corresponds to
    # multiplication by 2 when overflow is not a concern.
    print("12 << 2 =", 12 << 2)

    # Right shift performs floor division by powers of two for integers.
    print("12 >> 2 =", 12 >> 2)


# ============================================================================
# 21. BIT MASK APPLICATION
# ============================================================================

def demonstrate_bit_masks() -> None:
    """
    Bitwise operators are useful for compact flags and permission masks.
    """

    print("\n" + "=" * 80)
    print("21. BIT MASKS")
    print("=" * 80)

    READ = 1 << 0
    WRITE = 1 << 1
    EXECUTE = 1 << 2

    permissions = READ | WRITE

    print("READ:", READ)
    print("WRITE:", WRITE)
    print("EXECUTE:", EXECUTE)
    print("permissions:", permissions)

    has_read = bool(permissions & READ)
    has_write = bool(permissions & WRITE)
    has_execute = bool(permissions & EXECUTE)

    print("Has read:", has_read)
    print("Has write:", has_write)
    print("Has execute:", has_execute)

    # Add a permission using OR.
    permissions |= EXECUTE

    print("Updated permissions:", permissions)

    # Remove a permission using AND with the complemented mask.
    permissions &= ~WRITE

    print("After removing WRITE:", permissions)


# ============================================================================
# 22. CONDITIONAL EXPRESSION
# ============================================================================

def demonstrate_conditional_expression() -> None:
    """
    Conditional expression:

        value_if_true if condition else value_if_false

    It is an expression, so it produces a value.
    """

    print("\n" + "=" * 80)
    print("22. CONDITIONAL EXPRESSIONS")
    print("=" * 80)

    age = 21

    category = "adult" if age >= 18 else "minor"

    print("category =", category)

    temperature = 35

    message = "Hot" if temperature > 30 else "Moderate"

    print("message =", message)


# ============================================================================
# 23. OPERATOR PRECEDENCE
# ============================================================================

def demonstrate_operator_precedence() -> None:
    """
    Operators have precedence rules.

    A simplified hierarchy from higher to lower precedence includes:

    - Parentheses
    - Exponentiation
    - Unary +, -, ~
    - *, /, //, %
    - +, -
    - Shifts
    - &
    - ^
    - |
    - Comparisons, membership, identity
    - not
    - and
    - or
    - Conditional expression
    - Assignment expressions

    Assignment itself is a statement and does not behave like ordinary
    arithmetic operators.
    """

    print("\n" + "=" * 80)
    print("23. OPERATOR PRECEDENCE")
    print("=" * 80)

    expression_one = 2 + 3 * 4
    expression_two = (2 + 3) * 4

    print("2 + 3 * 4 =", expression_one)
    print("(2 + 3) * 4 =", expression_two)

    expression_three = 2 ** 3 * 4
    print("2 ** 3 * 4 =", expression_three)

    # Parentheses are recommended when they improve readability, even if
    # precedence rules already produce the intended result.


# ============================================================================
# 24. ASSOCIATIVITY
# ============================================================================

def demonstrate_associativity() -> None:
    """
    Associativity determines how operators of the same precedence group.

    Most arithmetic operators associate left-to-right.

    Exponentiation is right-associative:
        2 ** 3 ** 2
    means:
        2 ** (3 ** 2)
    """

    print("\n" + "=" * 80)
    print("24. ASSOCIATIVITY")
    print("=" * 80)

    print("100 / 10 / 2 =", 100 / 10 / 2)
    print("Equivalent grouping:", (100 / 10) / 2)

    print("2 ** 3 ** 2 =", 2 ** 3 ** 2)
    print("Equivalent grouping:", 2 ** (3 ** 2))


# ============================================================================
# 25. BOOLEAN VALUES AND OPERATORS
# ============================================================================

def demonstrate_boolean_arithmetic() -> None:
    """
    bool is a subclass of int in Python.

    True behaves numerically like 1.
    False behaves numerically like 0.

    This behavior is valid Python but should be used deliberately.
    """

    print("\n" + "=" * 80)
    print("25. BOOLEAN VALUES AND ARITHMETIC")
    print("=" * 80)

    print("True + True =", True + True)
    print("True * 10 =", True * 10)
    print("False * 10 =", False * 10)

    print("isinstance(True, int):", isinstance(True, int))

    values = [True, False, True, True]

    print("Number of True values:", sum(values))


# ============================================================================
# 26. FLOATING-POINT OPERATOR EDGE CASES
# ============================================================================

def demonstrate_floating_point_precision() -> None:
    """
    Binary floating-point numbers cannot represent every decimal fraction
    exactly.

    This can produce results that look surprising.
    """

    print("\n" + "=" * 80)
    print("26. FLOATING-POINT PRECISION")
    print("=" * 80)

    result = 0.1 + 0.2

    print("0.1 + 0.2 =", result)
    print("0.1 + 0.2 == 0.3:", result == 0.3)

    print(
        "math.isclose(0.1 + 0.2, 0.3):",
        math.isclose(result, 0.3),
    )

    # Decimal can represent decimal arithmetic more appropriately for
    # financial calculations when configured and used correctly.
    decimal_result = Decimal("0.1") + Decimal("0.2")

    print("Decimal('0.1') + Decimal('0.2') =", decimal_result)


# ============================================================================
# 27. OPERATOR FUNCTIONS FROM THE OPERATOR MODULE
# ============================================================================

def demonstrate_operator_module() -> None:
    """
    Python's operator module exposes functions corresponding to many
    operators.

    This is useful when an operation must be passed as a callable.
    """

    print("\n" + "=" * 80)
    print("27. OPERATOR MODULE")
    print("=" * 80)

    print("operator.add(10, 5) =", operator.add(10, 5))
    print("operator.sub(10, 5) =", operator.sub(10, 5))
    print("operator.mul(10, 5) =", operator.mul(10, 5))
    print("operator.truediv(10, 5) =", operator.truediv(10, 5))
    print("operator.eq(10, 10) =", operator.eq(10, 10))
    print("operator.lt(10, 20) =", operator.lt(10, 20))

    numbers = [1, 2, 3, 4]

    total = reduce(operator.add, numbers)

    print("reduce(operator.add, numbers) =", total)


# ============================================================================
# 28. MATRIX MULTIPLICATION
# ============================================================================

def demonstrate_matrix_multiplication() -> None:
    """
    Python's @ operator represents matrix multiplication.

    Built-in lists do not implement matrix multiplication themselves, so
    a small custom matrix class is used here.
    """

    print("\n" + "=" * 80)
    print("28. MATRIX MULTIPLICATION OPERATOR")
    print("=" * 80)

    class Matrix:
        """Minimal educational matrix implementation supporting @."""

        def __init__(self, rows: list[list[float]]) -> None:
            if not rows or not rows[0]:
                raise ValueError("Matrix cannot be empty.")

            width = len(rows[0])

            if any(len(row) != width for row in rows):
                raise ValueError("All rows must have equal length.")

            self.rows = [list(row) for row in rows]

        def __matmul__(self, other: "Matrix") -> "Matrix":
            if len(self.rows[0]) != len(other.rows):
                raise ValueError(
                    "Matrix dimensions are incompatible for multiplication."
                )

            result = []

            for row in self.rows:
                result_row = []

                for column_index in range(len(other.rows[0])):
                    value = sum(
                        row[k] * other.rows[k][column_index]
                        for k in range(len(other.rows))
                    )
                    result_row.append(value)

                result.append(result_row)

            return Matrix(result)

        def __repr__(self) -> str:
            return f"Matrix({self.rows!r})"

    matrix_a = Matrix([[1, 2], [3, 4]])
    matrix_b = Matrix([[5, 6], [7, 8]])

    matrix_c = matrix_a @ matrix_b

    print("A =", matrix_a)
    print("B =", matrix_b)
    print("A @ B =", matrix_c)


# ============================================================================
# 29. OPERATOR OVERLOADING
# ============================================================================

@dataclass
class Money:
    """
    Example of operator overloading.

    A class can define special methods that determine how operators work
    with instances of that class.
    """

    amount: float
    currency: str = "INR"

    def _check_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(
                "Cannot combine different currencies directly."
            )

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented

        self._check_currency(other)

        return Money(
            self.amount + other.amount,
            self.currency,
        )

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented

        self._check_currency(other)

        return Money(
            self.amount - other.amount,
            self.currency,
        )

    def __mul__(self, multiplier: float) -> "Money":
        if not isinstance(multiplier, (int, float)):
            return NotImplemented

        return Money(
            self.amount * multiplier,
            self.currency,
        )

    def __rmul__(self, multiplier: float) -> "Money":
        return self.__mul__(multiplier)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented

        return (
            self.amount == other.amount
            and self.currency == other.currency
        )

    def __lt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented

        self._check_currency(other)

        return self.amount < other.amount

    def __repr__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"


def demonstrate_operator_overloading() -> None:
    """
    Operators can be customized through special methods.
    """

    print("\n" + "=" * 80)
    print("29. OPERATOR OVERLOADING")
    print("=" * 80)

    salary = Money(50000)
    bonus = Money(10000)

    total = salary + bonus
    difference = salary - bonus
    increased = salary * 1.10

    print("salary =", salary)
    print("bonus =", bonus)
    print("salary + bonus =", total)
    print("salary - bonus =", difference)
    print("salary * 1.10 =", increased)

    print("salary == Money(50000):", salary == Money(50000))
    print("bonus < salary:", bonus < salary)
    print("2 * bonus:", 2 * bonus)

    try:
        print(salary + Money(100, "USD"))
    except ValueError as error:
        print("Currency error:", error)


# ============================================================================
# 30. SPECIAL METHODS FOR COMPARISONS
# ============================================================================

@dataclass
class StudentScore:
    """Object supporting rich comparisons based on score."""

    name: str
    score: float

    def __lt__(self, other: "StudentScore") -> bool:
        if not isinstance(other, StudentScore):
            return NotImplemented
        return self.score < other.score

    def __le__(self, other: "StudentScore") -> bool:
        if not isinstance(other, StudentScore):
            return NotImplemented
        return self.score <= other.score

    def __gt__(self, other: "StudentScore") -> bool:
        if not isinstance(other, StudentScore):
            return NotImplemented
        return self.score > other.score

    def __ge__(self, other: "StudentScore") -> bool:
        if not isinstance(other, StudentScore):
            return NotImplemented
        return self.score >= other.score

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StudentScore):
            return NotImplemented
        return self.score == other.score


def demonstrate_custom_comparisons() -> None:
    """
    Custom comparison operators allow domain objects to participate naturally
    in sorting and comparison logic.
    """

    print("\n" + "=" * 80)
    print("30. CUSTOM COMPARISONS")
    print("=" * 80)

    student_a = StudentScore("A", 85)
    student_b = StudentScore("B", 92)

    print("A < B:", student_a < student_b)
    print("A <= B:", student_a <= student_b)
    print("B > A:", student_b > student_a)
    print("B >= A:", student_b >= student_a)

    students = [
        StudentScore("A", 85),
        StudentScore("B", 92),
        StudentScore("C", 78),
    ]

    print("Sorted students:", sorted(students, key=lambda student: student.score))


# ============================================================================
# 31. CONTAINER MEMBERSHIP AND __contains__
# ============================================================================

class ProductCatalog:
    """Custom container demonstrating the membership operator."""

    def __init__(self, products: Iterable[str]) -> None:
        self.products = set(products)

    def __contains__(self, product_name: str) -> bool:
        return product_name.lower() in {
            product.lower() for product in self.products
        }


def demonstrate_custom_membership() -> None:
    """
    The in operator can invoke __contains__ for custom objects.
    """

    print("\n" + "=" * 80)
    print("31. CUSTOM MEMBERSHIP")
    print("=" * 80)

    catalog = ProductCatalog(
        ["Laptop", "Keyboard", "Mouse"]
    )

    print("'Laptop' in catalog:", "Laptop" in catalog)
    print("'laptop' in catalog:", "laptop" in catalog)
    print("'Monitor' in catalog:", "Monitor" in catalog)


# ============================================================================
# 32. BITWISE XOR APPLICATION
# ============================================================================

def demonstrate_xor_properties() -> None:
    """
    XOR has useful mathematical properties:

    x ^ 0 = x
    x ^ x = 0

    XOR is also commutative and associative.

    The classic XOR swap exists mathematically, but normal Python tuple
    assignment is clearer and should be preferred for ordinary swapping.
    """

    print("\n" + "=" * 80)
    print("32. XOR PROPERTIES")
    print("=" * 80)

    value = 42

    print("value ^ 0 =", value ^ 0)
    print("value ^ value =", value ^ value)

    a = 12
    b = 5

    print("a ^ b =", a ^ b)
    print("b ^ a =", b ^ a)
    print("(a ^ b) == (b ^ a):", (a ^ b) == (b ^ a))


# ============================================================================
# 33. PRACTICAL VALIDATION USING OPERATORS
# ============================================================================

def validate_user_input(
    age: int,
    username: str,
    roles: set[str],
) -> bool:
    """
    Combine comparison, logical, membership, and identity operators.

    The validation rule is:
    - age must be between 18 and 100
    - username must not be empty
    - role must contain either admin or analyst
    """

    if age is None:
        return False

    valid_age = 18 <= age <= 100
    valid_username = username.strip() != ""
    valid_role = "admin" in roles or "analyst" in roles

    return valid_age and valid_username and valid_role


def demonstrate_practical_validation() -> None:
    """
    Real-world validation often combines several operator categories.
    """

    print("\n" + "=" * 80)
    print("33. PRACTICAL VALIDATION")
    print("=" * 80)

    cases = [
        (30, "atul", {"analyst"}),
        (16, "atul", {"analyst"}),
        (30, "", {"analyst"}),
        (30, "atul", {"viewer"}),
    ]

    for age, username, roles in cases:
        result = validate_user_input(age, username, roles)

        print(
            f"age={age}, username={username!r}, roles={roles}"
            f" -> valid={result}"
        )


# ============================================================================
# 34. SAFE CALCULATOR
# ============================================================================

def calculate(
    left: float,
    right: float,
    operation: str,
) -> float:
    """
    Execute a selected arithmetic operation with explicit validation.

    This example demonstrates why dynamic operator selection should be
    controlled rather than using eval() on arbitrary user input.
    """

    operations = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "//": operator.floordiv,
        "%": operator.mod,
        "**": operator.pow,
    }

    if operation not in operations:
        raise ValueError(f"Unsupported operation: {operation!r}")

    if operation in {"/", "//", "%"} and right == 0:
        raise ZeroDivisionError("Cannot divide or take modulo by zero.")

    return operations[operation](left, right)


def demonstrate_safe_calculator() -> None:
    """
    A controlled operator mapping is safer than eval() for a calculator.
    """

    print("\n" + "=" * 80)
    print("34. SAFE CALCULATOR")
    print("=" * 80)

    examples = [
        (10, 5, "+"),
        (10, 5, "-"),
        (10, 5, "*"),
        (10, 5, "/"),
        (10, 3, "//"),
        (10, 3, "%"),
        (2, 5, "**"),
    ]

    for left, right, operation in examples:
        print(
            f"{left} {operation} {right} = "
            f"{calculate(left, right, operation)}"
        )

    try:
        calculate(10, 0, "/")
    except ZeroDivisionError as error:
        print("Handled error:", error)

    try:
        calculate(10, 5, "unknown")
    except ValueError as error:
        print("Handled error:", error)


# ============================================================================
# 35. ASSIGNMENT AND OBJECT REFERENCES
# ============================================================================

def demonstrate_reference_behavior() -> None:
    """
    Assignment does not copy an object automatically.

    It binds another name to the same object.
    """

    print("\n" + "=" * 80)
    print("35. ASSIGNMENT AND OBJECT REFERENCES")
    print("=" * 80)

    original = [1, 2, 3]
    alias = original

    alias.append(4)

    print("original =", original)
    print("alias =", alias)
    print("original is alias:", original is alias)

    # A shallow copy creates a new outer list.
    copied = original.copy()

    copied.append(5)

    print("original after copy modification:", original)
    print("copied:", copied)
    print("original is copied:", original is copied)


# ============================================================================
# 36. ASSIGNMENT IN LOOP CONDITIONS
# ============================================================================

def demonstrate_walrus_with_search() -> None:
    """
    Assignment expressions can avoid repeating an expensive or lengthy
    calculation in a condition.
    """

    print("\n" + "=" * 80)
    print("36. WALRUS OPERATOR IN PRACTICAL CODE")
    print("=" * 80)

    data = ["apple", "banana", "cherry"]

    if (found := next(
        (item for item in data if item.startswith("b")),
        None,
    )) is not None:
        print("Found:", found)
    else:
        print("Not found")


# ============================================================================
# 37. OPERATOR PRECEDENCE PRACTICE
# ============================================================================

def demonstrate_precedence_practice() -> None:
    """
    Several expressions are evaluated to make precedence behavior explicit.
    """

    print("\n" + "=" * 80)
    print("37. PRECEDENCE PRACTICE")
    print("=" * 80)

    expressions = {
        "2 + 3 * 4": 2 + 3 * 4,
        "(2 + 3) * 4": (2 + 3) * 4,
        "10 > 5 and 3 < 4": 10 > 5 and 3 < 4,
        "not False and True": not False and True,
        "True or False and False": True or False and False,
    }

    for expression, result in expressions.items():
        print(f"{expression} = {result}")

    # When an expression becomes difficult to read, add parentheses instead
    # of relying on the reader to remember precedence rules.


# ============================================================================
# 38. COMPARISON EDGE CASES
# ============================================================================

def demonstrate_comparison_edge_cases() -> None:
    """
    Demonstrates comparisons involving different types and special values.
    """

    print("\n" + "=" * 80)
    print("38. COMPARISON EDGE CASES")
    print("=" * 80)

    print("1 == True:", 1 == True)
    print("0 == False:", 0 == False)

    # Different types can sometimes compare, but relying on implicit
    # cross-type behavior is often poor design.
    print("1.0 == 1:", 1.0 == 1)

    nan = float("nan")

    print("nan == nan:", nan == nan)
    print("nan != nan:", nan != nan)

    positive_infinity = float("inf")

    print("inf > 1_000_000:", positive_infinity > 1_000_000)


# ============================================================================
# 39. SET OPERATIONS AS OPERATOR APPLICATIONS
# ============================================================================

def demonstrate_set_operators() -> None:
    """
    Sets use operators for mathematical set operations.

    | union
    & intersection
    - difference
    ^ symmetric difference
    """

    print("\n" + "=" * 80)
    print("39. SET OPERATORS")
    print("=" * 80)

    developers = {"Python", "SQL", "Git"}
    analysts = {"Python", "Excel", "SQL"}

    print("Union:", developers | analysts)
    print("Intersection:", developers & analysts)
    print("Difference:", developers - analysts)
    print("Symmetric difference:", developers ^ analysts)

    print(
        "developers <= analysts:",
        developers <= analysts,
    )


# ============================================================================
# 40. DICTIONARY MERGE OPERATORS
# ============================================================================

def demonstrate_dictionary_merge_operators() -> None:
    """
    Python 3.9 introduced dictionary merge operators:

    |   merge
    |=  update in place
    """

    print("\n" + "=" * 80)
    print("40. DICTIONARY MERGE OPERATORS")
    print("=" * 80)

    defaults = {
        "theme": "light",
        "language": "English",
    }

    user_settings = {
        "theme": "dark",
        "font_size": 14,
    }

    merged = defaults | user_settings

    print("defaults:", defaults)
    print("user_settings:", user_settings)
    print("merged:", merged)

    settings = defaults.copy()
    settings |= user_settings

    print("settings after |= :", settings)


# ============================================================================
# 41. SEQUENCE CONCATENATION AND REPETITION
# ============================================================================

def demonstrate_sequence_operators() -> None:
    """
    Some sequence types overload + and *.

    + concatenates compatible sequences.
    * repeats sequences.
    """

    print("\n" + "=" * 80)
    print("41. SEQUENCE OPERATORS")
    print("=" * 80)

    print("[1, 2] + [3, 4] =", [1, 2] + [3, 4])
    print("[1, 2] * 3 =", [1, 2] * 3)

    print("'Py' + 'thon' =", "Py" + "thon")
    print("'ha' * 3 =", "ha" * 3)

    # Important mutable-object edge case:
    nested = [[]] * 3

    nested[0].append("shared")

    print("nested =", nested)
    print(
        "All inner lists are the same object:",
        nested[0] is nested[1] is nested[2],
    )


# ============================================================================
# 42. OPERATOR PRECEDENCE WITH WALRUS
# ============================================================================

def demonstrate_walrus_parentheses() -> None:
    """
    Assignment expressions have restrictions in some contexts and often
    benefit from explicit parentheses.

    Explicit grouping improves readability and avoids syntax ambiguity.
    """

    print("\n" + "=" * 80)
    print("42. WALRUS AND PARENTHESES")
    print("=" * 80)

    values = [10, 20, 30]

    if (count := len(values)) > 2:
        print("The collection contains", count, "items.")

    # Clear grouping is preferable when combining := with other operators.


# ============================================================================
# 43. PRACTICAL FINANCIAL CALCULATION
# ============================================================================

def demonstrate_financial_operators() -> None:
    """
    Operators are the basic building blocks of business and financial
    calculations.

    This example calculates simple interest and final amount.
    """

    print("\n" + "=" * 80)
    print("43. PRACTICAL FINANCIAL CALCULATION")
    print("=" * 80)

    principal = 100_000
    annual_rate = 0.08
    years = 3

    simple_interest = principal * annual_rate * years
    final_amount = principal + simple_interest

    print("Principal:", principal)
    print("Annual rate:", annual_rate)
    print("Years:", years)
    print("Simple interest:", simple_interest)
    print("Final amount:", final_amount)

    # Decimal is preferable when exact decimal representation is important.
    principal_decimal = Decimal("100000")
    rate_decimal = Decimal("0.08")
    years_decimal = Decimal("3")

    interest_decimal = (
        principal_decimal
        * rate_decimal
        * years_decimal
    )

    print("Decimal interest:", interest_decimal)


# ============================================================================
# 44. PERFORMANCE CONSIDERATIONS
# ============================================================================

def demonstrate_performance_considerations() -> None:
    """
    Operator syntax is usually highly optimized, but the underlying operation
    still determines computational cost.

    Examples:
    - list membership is generally O(n)
    - set membership is generally O(1) average-case
    - dictionary key membership is generally O(1) average-case
    """

    print("\n" + "=" * 80)
    print("44. PERFORMANCE CONSIDERATIONS")
    print("=" * 80)

    large_list = list(range(100_000))
    large_set = set(large_list)

    target = 99_999

    print("Target in list:", target in large_list)
    print("Target in set:", target in large_set)

    print(
        "For repeated membership tests, a set can be much more efficient "
        "than a list."
    )


# ============================================================================
# 45. SECURITY CONSIDERATIONS
# ============================================================================

def demonstrate_security_principles() -> None:
    """
    Operators themselves are not generally security vulnerabilities.

    The danger often appears when expressions are built from untrusted input.

    Never use eval() to execute arbitrary user-provided expressions unless
    there is a carefully designed, restricted execution environment.

    A whitelist of allowed operations is safer for simple calculators.
    """

    print("\n" + "=" * 80)
    print("45. SECURITY CONSIDERATIONS")
    print("=" * 80)

    allowed_operations = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
    }

    user_operation = "+"

    if user_operation in allowed_operations:
        result = allowed_operations[user_operation](10, 5)
        print("Controlled operation result:", result)

    print(
        "Use explicit operation mappings instead of executing arbitrary "
        "expressions from untrusted input."
    )


# ============================================================================
# 46. COMMON MISTAKES
# ============================================================================

def demonstrate_common_mistakes() -> None:
    """
    Demonstrates common operator-related mistakes and safer alternatives.
    """

    print("\n" + "=" * 80)
    print("46. COMMON MISTAKES")
    print("=" * 80)

    # Mistake 1: confusing assignment and equality.
    #
    # if x = 10:
    #     ...
    #
    # is invalid syntax.
    #
    # Correct:
    x = 10

    if x == 10:
        print("Correct use of == for comparison.")

    # Mistake 2: using is for value comparison.
    first = [1, 2]
    second = [1, 2]

    print("Correct value comparison:", first == second)
    print("Identity comparison:", first is second)

    # Mistake 3: using integer division when decimal division is required.
    print("10 / 4 =", 10 / 4)
    print("10 // 4 =", 10 // 4)

    # Mistake 4: forgetting operator precedence.
    print("Correctly grouped:", 10 + 2 * 3)
    print("Explicit grouping:", (10 + 2) * 3)

    # Mistake 5: assuming floating-point equality is always exact.
    print(
        "Use math.isclose:",
        math.isclose(0.1 + 0.2, 0.3),
    )


# ============================================================================
# 47. MINI EXPRESSION EVALUATOR WITHOUT EVAL
# ============================================================================

class SimpleExpressionEvaluator:
    """
    A deliberately small evaluator for expressions represented as:

        (left, operator, right)

    It does not parse arbitrary strings and therefore avoids the risks of
    passing untrusted input to eval().
    """

    OPERATIONS = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "//": operator.floordiv,
        "%": operator.mod,
        "**": operator.pow,
    }

    def evaluate(
        self,
        left: float,
        operation: str,
        right: float,
    ) -> float:
        if operation not in self.OPERATIONS:
            raise ValueError(
                f"Unsupported operator: {operation}"
            )

        if operation in {"/", "//", "%"} and right == 0:
            raise ZeroDivisionError(
                "Right operand cannot be zero."
            )

        return self.OPERATIONS[operation](left, right)


def demonstrate_expression_evaluator() -> None:
    """
    Demonstrates a controlled operator dispatch design.
    """

    print("\n" + "=" * 80)
    print("47. MINI EXPRESSION EVALUATOR")
    print("=" * 80)

    evaluator = SimpleExpressionEvaluator()

    expressions = [
        (20, "+", 5),
        (20, "-", 5),
        (20, "*", 5),
        (20, "/", 5),
        (20, "//", 3),
        (20, "%", 3),
        (2, "**", 5),
    ]

    for left, operation_name, right in expressions:
        result = evaluator.evaluate(
            left,
            operation_name,
            right,
        )

        print(
            f"{left} {operation_name} {right} = {result}"
        )


# ============================================================================
# 48. OPERATOR CATEGORY REFERENCE
# ============================================================================

def demonstrate_operator_reference() -> None:
    """
    Prints a compact reference of major Python operator categories.
    """

    print("\n" + "=" * 80)
    print("48. OPERATOR CATEGORY REFERENCE")
    print("=" * 80)

    categories = {
        "Assignment": [
            "=",
            "+=",
            "-=",
            "*=",
            "/=",
            "//=",
            "%=",
            "**=",
            "&=",
            "|=",
            "^=",
            "<<=",
            ">>=",
            "@=",
        ],
        "Arithmetic": [
            "+",
            "-",
            "*",
            "/",
            "//",
            "%",
            "**",
            "@",
        ],
        "Comparison": [
            "==",
            "!=",
            "<",
            "<=",
            ">",
            ">=",
        ],
        "Logical": [
            "and",
            "or",
            "not",
        ],
        "Identity": [
            "is",
            "is not",
        ],
        "Membership": [
            "in",
            "not in",
        ],
        "Bitwise": [
            "&",
            "|",
            "^",
            "~",
            "<<",
            ">>",
        ],
        "Conditional": [
            "x if condition else y",
        ],
        "Assignment expression": [
            ":=",
        ],
        "Collection-specific": [
            "|",
            "&",
            "-",
            "^",
            "@" ,
        ],
    }

    for category, operators in categories.items():
        print(f"{category}:")
        print("  " + ", ".join(operators))


# ============================================================================
# 49. SELF-TESTS
# ============================================================================

def run_tests() -> None:
    """
    Basic assertions verify important operator behavior.

    Assertions are intentionally small and deterministic so this script can
    function as both a tutorial and a basic study reference.
    """

    print("\n" + "=" * 80)
    print("49. SELF-TESTS")
    print("=" * 80)

    assert 10 + 5 == 15
    assert 10 - 5 == 5
    assert 10 * 5 == 50
    assert 10 / 5 == 2
    assert 10 // 3 == 3
    assert 10 % 3 == 1
    assert 2 ** 5 == 32

    assert 10 > 5
    assert 10 >= 10
    assert 10 != 20
    assert 10 == 10

    assert True and True
    assert True or False
    assert not False

    assert "Python" in "Python programming"
    assert "Java" not in "Python programming"

    first = []
    second = first

    assert first is second

    values = [1, 2]
    alias = values
    alias += [3]

    assert values == [1, 2, 3]

    assert 18 <= 25 <= 60

    evaluator = SimpleExpressionEvaluator()

    assert evaluator.evaluate(10, "+", 5) == 15
    assert evaluator.evaluate(10, "*", 5) == 50

    print("All self-tests passed.")


# ============================================================================
# 50. MAIN PROGRAM
# ============================================================================

def main() -> None:
    """
    Run the complete educational demonstration.
    """

    print("=" * 80)
    print("ASSIGNMENT AND OTHER OPERATORS IN PYTHON")
    print("=" * 80)
    print(
        "This program demonstrates assignment, arithmetic, comparison, "
        "logical, identity, membership, bitwise, conditional, matrix, "
        "collection, and custom operators."
    )

    demonstrate_basic_assignment()
    demonstrate_multiple_assignment()
    demonstrate_chained_assignment()
    demonstrate_unpacking_assignment()
    demonstrate_extended_unpacking()
    demonstrate_swap_assignment()
    demonstrate_augmented_assignment()
    demonstrate_mutable_augmented_assignment()
    demonstrate_assignment_expression()

    demonstrate_arithmetic_operators()
    demonstrate_floor_division_edge_cases()
    demonstrate_division_errors()

    demonstrate_comparison_operators()
    demonstrate_comparison_chaining()

    demonstrate_logical_operators()
    demonstrate_short_circuiting()
    demonstrate_truthy_operand_return()

    demonstrate_identity_operators()
    demonstrate_membership_operators()

    demonstrate_bitwise_operators()
    demonstrate_bit_masks()

    demonstrate_conditional_expression()
    demonstrate_operator_precedence()
    demonstrate_associativity()

    demonstrate_boolean_arithmetic()
    demonstrate_floating_point_precision()
    demonstrate_operator_module()

    demonstrate_matrix_multiplication()
    demonstrate_operator_overloading()
    demonstrate_custom_comparisons()
    demonstrate_custom_membership()
    demonstrate_xor_properties()

    demonstrate_practical_validation()
    demonstrate_safe_calculator()
    demonstrate_reference_behavior()
    demonstrate_walrus_with_search()
    demonstrate_precedence_practice()
    demonstrate_comparison_edge_cases()

    demonstrate_set_operators()
    demonstrate_dictionary_merge_operators()
    demonstrate_sequence_operators()
    demonstrate_walrus_parentheses()

    demonstrate_financial_operators()
    demonstrate_performance_considerations()
    demonstrate_security_principles()
    demonstrate_common_mistakes()

    demonstrate_expression_evaluator()
    demonstrate_operator_reference()

    run_tests()

    print("\n" + "=" * 80)
    print("END OF OPERATOR STUDY SCRIPT")
    print("=" * 80)


if __name__ == "__main__":
    main()
