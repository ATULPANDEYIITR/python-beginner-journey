"""
Arithmetic Operators in Python
==============================

A comprehensive standalone study script covering arithmetic operators from
absolute beginner level through advanced practical usage.

Topics covered:
- Numeric types
- Addition, subtraction, multiplication
- True division and floor division
- Modulo
- Exponentiation
- Unary plus and unary minus
- Operator precedence and associativity
- Parentheses
- Integer and floating-point arithmetic
- Complex numbers
- Decimal arithmetic
- Fractions
- Numeric conversions
- Negative numbers and floor division
- Modulo with negative operands
- Floating-point precision
- Large integers
- Overflow and domain errors
- Arithmetic with booleans
- Arithmetic with numeric-like objects
- The __add__, __sub__, __mul__, __truediv__, __floordiv__,
  __mod__, and __pow__ protocols
- Reflected arithmetic methods
- Type interactions
- Practical calculations
- Compound calculations
- Validation
- Error handling
- Testing
- Performance considerations
- Numerical best practices
- Real-world applications

Run this file directly:

    python arithmetic_operators.py
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, getcontext
from fractions import Fraction
import cmath
import math
import operator
import sys
import timeit
from typing import Callable, Iterable


# ---------------------------------------------------------------------------
# 1. Basic numeric values
# ---------------------------------------------------------------------------

def demonstrate_numeric_values() -> None:
    """Show the main built-in numeric types used with arithmetic operators."""

    print("\n" + "=" * 80)
    print("1. NUMERIC VALUES AND TYPES")
    print("=" * 80)

    integer_value = 20
    floating_value = 7.5
    complex_value = 3 + 4j
    boolean_value = True

    print("integer:", integer_value, type(integer_value))
    print("float:", floating_value, type(floating_value))
    print("complex:", complex_value, type(complex_value))
    print("bool:", boolean_value, type(boolean_value))

    # bool is a subclass of int in Python.
    print("True behaves numerically as:", int(True))
    print("False behaves numerically as:", int(False))


# ---------------------------------------------------------------------------
# 2. Addition
# ---------------------------------------------------------------------------

def demonstrate_addition() -> None:
    """Demonstrate the + operator."""

    print("\n" + "=" * 80)
    print("2. ADDITION (+)")
    print("=" * 80)

    a = 10
    b = 3

    print("10 + 3 =", a + b)
    print("10.5 + 2.5 =", 10.5 + 2.5)
    print("(-10) + 3 =", (-10) + 3)

    # Addition is also defined for some non-numeric objects.
    # This script focuses on arithmetic, but the same operator is overloaded
    # by sequences for concatenation.
    print("[1, 2] + [3, 4] =", [1, 2] + [3, 4])

    # Strings use + for concatenation, not numerical addition.
    print('"Python" + "3" =', "Python" + "3")


# ---------------------------------------------------------------------------
# 3. Subtraction
# ---------------------------------------------------------------------------

def demonstrate_subtraction() -> None:
    """Demonstrate the - operator."""

    print("\n" + "=" * 80)
    print("3. SUBTRACTION (-)")
    print("=" * 80)

    a = 10
    b = 3

    print("10 - 3 =", a - b)
    print("3 - 10 =", b - a)
    print("10.5 - 2.25 =", 10.5 - 2.25)

    # Unary minus changes the sign of a value.
    value = 15
    print("Unary -15 =", -value)


# ---------------------------------------------------------------------------
# 4. Multiplication
# ---------------------------------------------------------------------------

def demonstrate_multiplication() -> None:
    """Demonstrate the * operator."""

    print("\n" + "=" * 80)
    print("4. MULTIPLICATION (*)")
    print("=" * 80)

    print("6 * 4 =", 6 * 4)
    print("2.5 * 4 =", 2.5 * 4)
    print("(-5) * (-2) =", (-5) * (-2))
    print("(-5) * 2 =", (-5) * 2)

    # Multiplication also has defined behavior for sequences.
    print('"abc" * 3 =', "abc" * 3)
    print("[1, 2] * 3 =", [1, 2] * 3)


# ---------------------------------------------------------------------------
# 5. True division
# ---------------------------------------------------------------------------

def demonstrate_true_division() -> None:
    """Demonstrate /, Python's true division operator."""

    print("\n" + "=" * 80)
    print("5. TRUE DIVISION (/)")
    print("=" * 80)

    print("10 / 2 =", 10 / 2)
    print("7 / 2 =", 7 / 2)
    print("1 / 4 =", 1 / 4)

    # Even when both operands are integers, / returns a float.
    result = 10 / 2
    print("Type of 10 / 2:", type(result).__name__)

    try:
        print("10 / 0 =", 10 / 0)
    except ZeroDivisionError as error:
        print("10 / 0 raises:", type(error).__name__, "-", error)


# ---------------------------------------------------------------------------
# 6. Floor division
# ---------------------------------------------------------------------------

def demonstrate_floor_division() -> None:
    """Demonstrate // and the important negative-number behavior."""

    print("\n" + "=" * 80)
    print("6. FLOOR DIVISION (//)")
    print("=" * 80)

    print("10 // 3 =", 10 // 3)
    print("10.0 // 3 =", 10.0 // 3)

    # Floor division means floor(a / b), not truncation toward zero.
    print("7 // 2 =", 7 // 2)
    print("-7 // 2 =", -7 // 2)
    print("7 // -2 =", 7 // -2)
    print("-7 // -2 =", -7 // -2)

    print("math.floor(-7 / 2) =", math.floor(-7 / 2))
    print("int(-7 / 2) =", int(-7 / 2))

    print("\nImportant distinction:")
    print("floor(-3.5) =", math.floor(-3.5))
    print("int(-3.5) =", int(-3.5))


# ---------------------------------------------------------------------------
# 7. Modulo
# ---------------------------------------------------------------------------

def demonstrate_modulo() -> None:
    """Demonstrate the % operator and its relationship with //."""

    print("\n" + "=" * 80)
    print("7. MODULO (%)")
    print("=" * 80)

    print("10 % 3 =", 10 % 3)
    print("10 % 2 =", 10 % 2)
    print("17 % 5 =", 17 % 5)

    # Modulo is useful for checking divisibility.
    number = 42
    print("42 divisible by 7:", number % 7 == 0)
    print("42 divisible by 5:", number % 5 == 0)

    # Python satisfies:
    # a == (a // b) * b + (a % b)
    a = -7
    b = 3
    quotient = a // b
    remainder = a % b

    print("\nFor a =", a, "and b =", b)
    print("a // b =", quotient)
    print("a % b =", remainder)
    print("(a // b) * b + (a % b) =", quotient * b + remainder)


# ---------------------------------------------------------------------------
# 8. Exponentiation
# ---------------------------------------------------------------------------

def demonstrate_exponentiation() -> None:
    """Demonstrate the ** operator."""

    print("\n" + "=" * 80)
    print("8. EXPONENTIATION (**)")
    print("=" * 80)

    print("2 ** 3 =", 2 ** 3)
    print("5 ** 2 =", 5 ** 2)
    print("10 ** 0 =", 10 ** 0)
    print("9 ** 0.5 =", 9 ** 0.5)

    # Negative exponents represent reciprocals for nonzero bases.
    print("2 ** -1 =", 2 ** -1)
    print("2 ** -3 =", 2 ** -3)

    # Python supports arbitrary-size integers.
    print("2 ** 100 =", 2 ** 100)

    # A negative base with a fractional exponent can produce a complex result.
    print("(-8) ** (1 / 3) =", (-8) ** (1 / 3))

    # math.pow converts its arguments to float, so behavior differs.
    print("math.pow(2, 3) =", math.pow(2, 3))


# ---------------------------------------------------------------------------
# 9. Unary operators
# ---------------------------------------------------------------------------

def demonstrate_unary_operators() -> None:
    """Demonstrate unary + and unary -."""

    print("\n" + "=" * 80)
    print("9. UNARY PLUS AND UNARY MINUS")
    print("=" * 80)

    value = 25

    print("+value =", +value)
    print("-value =", -value)
    print("-(-value) =", -(-value))

    # Unary plus generally leaves the numerical value unchanged.
    # It can still invoke a type's __pos__ implementation.
    print("+3.5 =", +3.5)


# ---------------------------------------------------------------------------
# 10. Operator precedence
# ---------------------------------------------------------------------------

def demonstrate_precedence() -> None:
    """Demonstrate the order in which arithmetic operations are evaluated."""

    print("\n" + "=" * 80)
    print("10. OPERATOR PRECEDENCE")
    print("=" * 80)

    print("2 + 3 * 4 =", 2 + 3 * 4)
    print("(2 + 3) * 4 =", (2 + 3) * 4)

    print("2 ** 3 * 4 =", 2 ** 3 * 4)
    print("2 * 3 ** 4 =", 2 * 3 ** 4)

    # Parentheses explicitly control evaluation.
    expression_without_parentheses = 10 + 5 * 2
    expression_with_parentheses = (10 + 5) * 2

    print("10 + 5 * 2 =", expression_without_parentheses)
    print("(10 + 5) * 2 =", expression_with_parentheses)


# ---------------------------------------------------------------------------
# 11. Associativity
# ---------------------------------------------------------------------------

def demonstrate_associativity() -> None:
    """Demonstrate left and right associativity of arithmetic operators."""

    print("\n" + "=" * 80)
    print("11. ASSOCIATIVITY")
    print("=" * 80)

    # Most binary arithmetic operators are evaluated left-to-right when they
    # have equal precedence.
    print("20 - 5 - 3 =", 20 - 5 - 3)
    print("(20 - 5) - 3 =", (20 - 5) - 3)
    print("20 - (5 - 3) =", 20 - (5 - 3))

    print("20 / 5 / 2 =", 20 / 5 / 2)
    print("(20 / 5) / 2 =", (20 / 5) / 2)
    print("20 / (5 / 2) =", 20 / (5 / 2))

    # Exponentiation is right-associative.
    print("2 ** 3 ** 2 =", 2 ** 3 ** 2)
    print("2 ** (3 ** 2) =", 2 ** (3 ** 2))
    print("(2 ** 3) ** 2 =", (2 ** 3) ** 2)


# ---------------------------------------------------------------------------
# 12. Mixed numeric types
# ---------------------------------------------------------------------------

def demonstrate_mixed_numeric_types() -> None:
    """Show common interactions among int, float, complex, and bool."""

    print("\n" + "=" * 80)
    print("12. MIXED NUMERIC TYPES")
    print("=" * 80)

    integer_value = 10
    float_value = 2.5

    result = integer_value + float_value

    print("10 + 2.5 =", result)
    print("Type:", type(result).__name__)

    print("True + 4 =", True + 4)
    print("False * 100 =", False * 100)

    complex_value = 2 + 3j
    print("(2 + 3j) + 5 =", complex_value + 5)
    print("(2 + 3j) * 2 =", complex_value * 2)

    try:
        print("(2 + 3j) // 2 =", complex_value // 2)
    except TypeError as error:
        print("Complex floor division raises:", type(error).__name__, "-", error)

    try:
        print("(2 + 3j) % 2 =", complex_value % 2)
    except TypeError as error:
        print("Complex modulo raises:", type(error).__name__, "-", error)


# ---------------------------------------------------------------------------
# 13. Floating-point precision
# ---------------------------------------------------------------------------

def demonstrate_float_precision() -> None:
    """Demonstrate why binary floating-point can produce surprising results."""

    print("\n" + "=" * 80)
    print("13. FLOATING-POINT PRECISION")
    print("=" * 80)

    result = 0.1 + 0.2

    print("0.1 + 0.2 =", result)
    print("0.1 + 0.2 == 0.3:", result == 0.3)

    # Use math.isclose for approximate numerical comparison.
    print(
        "math.isclose(0.1 + 0.2, 0.3):",
        math.isclose(0.1 + 0.2, 0.3),
    )

    # Binary floating-point cannot exactly represent many decimal fractions.
    # repr() exposes a useful representation of the stored floating value.
    print("repr(0.1) =", repr(0.1))


# ---------------------------------------------------------------------------
# 14. Decimal arithmetic
# ---------------------------------------------------------------------------

def demonstrate_decimal() -> None:
    """Demonstrate decimal arithmetic for decimal-sensitive calculations."""

    print("\n" + "=" * 80)
    print("14. DECIMAL ARITHMETIC")
    print("=" * 80)

    # Construct Decimal from strings when exact decimal input is required.
    decimal_a = Decimal("0.1")
    decimal_b = Decimal("0.2")

    print("Decimal('0.1') + Decimal('0.2') =", decimal_a + decimal_b)
    print("Equals Decimal('0.3'):", decimal_a + decimal_b == Decimal("0.3"))

    # Decimal can also represent monetary values precisely according to its
    # decimal arithmetic rules, subject to context and rounding.
    price = Decimal("199.99")
    quantity = Decimal("3")
    subtotal = price * quantity

    print("Price:", price)
    print("Quantity:", quantity)
    print("Subtotal:", subtotal)

    tax_rate = Decimal("0.18")
    tax = subtotal * tax_rate
    total = subtotal + tax

    print("Tax:", tax)
    print("Total:", total)

    rounded_total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    print("Rounded total:", rounded_total)

    # Decimal arithmetic is controlled by a decimal context.
    print("Current Decimal precision:", getcontext().prec)


# ---------------------------------------------------------------------------
# 15. Fractions
# ---------------------------------------------------------------------------

def demonstrate_fractions() -> None:
    """Demonstrate exact rational arithmetic using Fraction."""

    print("\n" + "=" * 80)
    print("15. FRACTION ARITHMETIC")
    print("=" * 80)

    first = Fraction(1, 3)
    second = Fraction(1, 6)

    print("1/3 + 1/6 =", first + second)
    print("1/3 - 1/6 =", first - second)
    print("1/3 * 1/6 =", first * second)
    print("1/3 / 1/6 =", first / second)

    # Fraction automatically reduces rational numbers.
    print("Fraction(6, 8) =", Fraction(6, 8))

    # Conversion from a float captures the exact binary floating-point value,
    # not necessarily the intended decimal fraction.
    print("Fraction(0.5) =", Fraction(0.5))
    print("Fraction('0.1') =", Fraction("0.1"))


# ---------------------------------------------------------------------------
# 16. Complex arithmetic
# ---------------------------------------------------------------------------

def demonstrate_complex_arithmetic() -> None:
    """Demonstrate arithmetic with complex numbers."""

    print("\n" + "=" * 80)
    print("16. COMPLEX NUMBER ARITHMETIC")
    print("=" * 80)

    z1 = 2 + 3j
    z2 = 1 - 4j

    print("z1 =", z1)
    print("z2 =", z2)
    print("z1 + z2 =", z1 + z2)
    print("z1 - z2 =", z1 - z2)
    print("z1 * z2 =", z1 * z2)
    print("z1 / z2 =", z1 / z2)
    print("z1 ** 2 =", z1 ** 2)
    print("|z1| =", abs(z1))

    # cmath supports mathematical functions for complex numbers.
    print("sqrt(-1) using cmath =", cmath.sqrt(-1))


# ---------------------------------------------------------------------------
# 17. Numeric conversion
# ---------------------------------------------------------------------------

def demonstrate_conversions() -> None:
    """Demonstrate explicit conversions relevant to arithmetic."""

    print("\n" + "=" * 80)
    print("17. NUMERIC CONVERSIONS")
    print("=" * 80)

    print("int(7.9) =", int(7.9))
    print("int(-7.9) =", int(-7.9))
    print("float(10) =", float(10))
    print("complex(5) =", complex(5))

    # int() truncates toward zero for finite floating-point values.
    print("int(3.999) =", int(3.999))
    print("int(-3.999) =", int(-3.999))

    # Round is different from int because it performs rounding.
    print("round(3.999) =", round(3.999))
    print("round(3.14159, 2) =", round(3.14159, 2))


# ---------------------------------------------------------------------------
# 18. Useful arithmetic patterns
# ---------------------------------------------------------------------------

def demonstrate_common_patterns() -> None:
    """Demonstrate common arithmetic programming patterns."""

    print("\n" + "=" * 80)
    print("18. COMMON ARITHMETIC PATTERNS")
    print("=" * 80)

    # Even/odd detection.
    for number in range(1, 6):
        parity = "even" if number % 2 == 0 else "odd"
        print(number, "is", parity)

    # Extracting digits.
    number = 5837
    last_digit = number % 10
    remaining_digits = number // 10

    print("\nNumber:", number)
    print("Last digit:", last_digit)
    print("Remaining digits:", remaining_digits)

    # Convert seconds into hours, minutes, and seconds.
    total_seconds = 7384

    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60

    print("\n7384 seconds =", hours, "hours,", minutes, "minutes,", seconds, "seconds")

    # Percentage calculation.
    obtained_marks = 438
    maximum_marks = 500
    percentage = obtained_marks / maximum_marks * 100

    print("Percentage:", percentage)


# ---------------------------------------------------------------------------
# 19. Practical mathematical formulas
# ---------------------------------------------------------------------------

def calculate_simple_interest(
    principal: float,
    annual_rate_percent: float,
    years: float,
) -> float:
    """Return simple interest."""

    return principal * (annual_rate_percent / 100) * years


def calculate_compound_amount(
    principal: float,
    annual_rate_percent: float,
    years: float,
    compounds_per_year: int,
) -> float:
    """Return compound amount using the standard compounding formula."""

    if compounds_per_year <= 0:
        raise ValueError("compounds_per_year must be positive")

    rate = annual_rate_percent / 100
    return principal * (1 + rate / compounds_per_year) ** (
        compounds_per_year * years
    )


def calculate_rectangle_area(length: float, width: float) -> float:
    """Return rectangle area."""

    if length < 0 or width < 0:
        raise ValueError("length and width must be non-negative")

    return length * width


def calculate_circle_area(radius: float) -> float:
    """Return circle area."""

    if radius < 0:
        raise ValueError("radius must be non-negative")

    return math.pi * radius ** 2


def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Return BMI as weight divided by height squared."""

    if weight_kg <= 0:
        raise ValueError("weight must be positive")

    if height_m <= 0:
        raise ValueError("height must be positive")

    return weight_kg / height_m ** 2


def demonstrate_practical_formulas() -> None:
    """Demonstrate arithmetic operators in common formulas."""

    print("\n" + "=" * 80)
    print("19. PRACTICAL MATHEMATICAL FORMULAS")
    print("=" * 80)

    print(
        "Simple interest:",
        calculate_simple_interest(10000, 8, 2),
    )

    print(
        "Compound amount:",
        calculate_compound_amount(10000, 8, 2, 12),
    )

    print(
        "Rectangle area:",
        calculate_rectangle_area(12.5, 4),
    )

    print(
        "Circle area:",
        calculate_circle_area(7),
    )

    print(
        "BMI:",
        calculate_bmi(70, 1.75),
    )


# ---------------------------------------------------------------------------
# 20. EMI calculation
# ---------------------------------------------------------------------------

def calculate_emi(
    principal: float,
    annual_interest_rate_percent: float,
    years: int,
) -> float:
    """
    Calculate monthly EMI.

    Formula:
        EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)

    P = principal
    r = monthly interest rate as a decimal
    n = number of monthly payments
    """

    if principal <= 0:
        raise ValueError("principal must be positive")

    if annual_interest_rate_percent < 0:
        raise ValueError("interest rate cannot be negative")

    if years <= 0:
        raise ValueError("years must be positive")

    monthly_rate = annual_interest_rate_percent / 100 / 12
    number_of_payments = years * 12

    if monthly_rate == 0:
        return principal / number_of_payments

    growth_factor = (1 + monthly_rate) ** number_of_payments

    return (
        principal
        * monthly_rate
        * growth_factor
        / (growth_factor - 1)
    )


def demonstrate_emi() -> None:
    """Demonstrate EMI arithmetic."""

    print("\n" + "=" * 80)
    print("20. EMI CALCULATION")
    print("=" * 80)

    principal = 1_000_000
    annual_rate = 8.5
    years = 20

    emi = calculate_emi(principal, annual_rate, years)
    total_payment = emi * years * 12
    total_interest = total_payment - principal

    print("Principal:", principal)
    print("Annual rate:", annual_rate, "%")
    print("Loan term:", years, "years")
    print("Monthly EMI:", round(emi, 2))
    print("Total payment:", round(total_payment, 2))
    print("Total interest:", round(total_interest, 2))


# ---------------------------------------------------------------------------
# 21. Arithmetic using the operator module
# ---------------------------------------------------------------------------

def demonstrate_operator_module() -> None:
    """Show named functions corresponding to arithmetic operators."""

    print("\n" + "=" * 80)
    print("21. OPERATOR MODULE")
    print("=" * 80)

    print("operator.add(10, 5) =", operator.add(10, 5))
    print("operator.sub(10, 5) =", operator.sub(10, 5))
    print("operator.mul(10, 5) =", operator.mul(10, 5))
    print("operator.truediv(10, 5) =", operator.truediv(10, 5))
    print("operator.floordiv(10, 3) =", operator.floordiv(10, 3))
    print("operator.mod(10, 3) =", operator.mod(10, 3))
    print("operator.pow(2, 5) =", operator.pow(2, 5))

    # This is useful when an operation must be passed around as a function.
    operations: dict[str, Callable[[float, float], float]] = {
        "add": operator.add,
        "subtract": operator.sub,
        "multiply": operator.mul,
        "divide": operator.truediv,
    }

    a = 12
    b = 4

    for name, operation in operations.items():
        print(f"{name:>8}: {operation(a, b)}")


# ---------------------------------------------------------------------------
# 22. Arithmetic method protocols
# ---------------------------------------------------------------------------

class Measurement:
    """
    A small numeric-like class demonstrating arithmetic operator overloading.

    The value represents a measurement in a single conceptual unit.
    """

    def __init__(self, value: float) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"Measurement({self.value!r})"

    def __add__(self, other: Measurement | float) -> Measurement:
        if isinstance(other, Measurement):
            return Measurement(self.value + other.value)

        if isinstance(other, (int, float)):
            return Measurement(self.value + other)

        return NotImplemented

    def __sub__(self, other: Measurement | float) -> Measurement:
        if isinstance(other, Measurement):
            return Measurement(self.value - other.value)

        if isinstance(other, (int, float)):
            return Measurement(self.value - other)

        return NotImplemented

    def __mul__(self, other: float) -> Measurement:
        if isinstance(other, (int, float)):
            return Measurement(self.value * other)

        return NotImplemented

    def __rmul__(self, other: float) -> Measurement:
        # Reflected multiplication supports:
        # number * Measurement
        return self.__mul__(other)

    def __truediv__(self, other: float) -> Measurement:
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("cannot divide Measurement by zero")

            return Measurement(self.value / other)

        return NotImplemented


def demonstrate_operator_overloading() -> None:
    """Demonstrate arithmetic methods used by Python's operator machinery."""

    print("\n" + "=" * 80)
    print("22. OPERATOR OVERLOADING")
    print("=" * 80)

    first = Measurement(10)
    second = Measurement(4)

    print("first:", first)
    print("second:", second)
    print("first + second:", first + second)
    print("first - second:", first - second)
    print("first * 3:", first * 3)
    print("3 * first:", 3 * first)
    print("first / 2:", first / 2)

    print("\nImportant special methods:")
    print("__add__       -> +")
    print("__sub__       -> -")
    print("__mul__       -> *")
    print("__truediv__   -> /")
    print("__floordiv__  -> //")
    print("__mod__       -> %")
    print("__pow__       -> **")
    print("__radd__      -> reflected +")
    print("__rmul__      -> reflected *")


# ---------------------------------------------------------------------------
# 23. Reflected arithmetic operations
# ---------------------------------------------------------------------------

class NumberWrapper:
    """Demonstrate reflected addition with a custom type."""

    def __init__(self, value: int) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"NumberWrapper({self.value})"

    def __add__(self, other: int) -> NumberWrapper:
        if isinstance(other, int):
            return NumberWrapper(self.value + other)

        return NotImplemented

    def __radd__(self, other: int) -> NumberWrapper:
        if isinstance(other, int):
            return NumberWrapper(other + self.value)

        return NotImplemented


def demonstrate_reflected_operations() -> None:
    """Explain the role of reflected arithmetic methods."""

    print("\n" + "=" * 80)
    print("23. REFLECTED OPERATIONS")
    print("=" * 80)

    wrapped = NumberWrapper(10)

    print("wrapped + 5 =", wrapped + 5)
    print("5 + wrapped =", 5 + wrapped)

    print(
        "\nThe second expression can use __radd__ when the left operand "
        "cannot directly perform the operation with the right operand."
    )


# ---------------------------------------------------------------------------
# 24. Error handling
# ---------------------------------------------------------------------------

def safe_divide(
    numerator: float,
    denominator: float,
) -> float | None:
    """Perform division while converting expected arithmetic errors to None."""

    try:
        return numerator / denominator
    except ZeroDivisionError:
        return None


def demonstrate_error_handling() -> None:
    """Demonstrate important arithmetic exceptions."""

    print("\n" + "=" * 80)
    print("24. ERROR HANDLING")
    print("=" * 80)

    print("safe_divide(10, 2) =", safe_divide(10, 2))
    print("safe_divide(10, 0) =", safe_divide(10, 0))

    try:
        result = 10 / 0
        print(result)
    except ZeroDivisionError as error:
        print("Caught ZeroDivisionError:", error)

    try:
        result = "10" + 5
        print(result)
    except TypeError as error:
        print("Caught TypeError:", error)

    try:
        result = Decimal("not-a-number")
        print(result)
    except InvalidOperation as error:
        print("Caught Decimal InvalidOperation:", type(error).__name__)


# ---------------------------------------------------------------------------
# 25. Arithmetic edge cases
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    """Demonstrate less obvious arithmetic behaviors."""

    print("\n" + "=" * 80)
    print("25. EDGE CASES")
    print("=" * 80)

    print("0 ** 0 =", 0 ** 0)
    print("0.0 ** 0 =", 0.0 ** 0)

    try:
        print("0.0 ** -1 =", 0.0 ** -1)
    except ZeroDivisionError as error:
        print("0.0 ** -1 raises:", type(error).__name__, "-", error)

    try:
        print("10 / 0 =", 10 / 0)
    except ZeroDivisionError as error:
        print("10 / 0 raises:", type(error).__name__, "-", error)

    print("(-7) % 3 =", (-7) % 3)
    print("7 % (-3) =", 7 % (-3))
    print("(-7) % (-3) =", (-7) % (-3))

    # Python integers do not overflow merely because they become large.
    huge_integer = 10 ** 100
    print("Number of digits in 10 ** 100:", len(str(huge_integer)))


# ---------------------------------------------------------------------------
# 26. Infinity and NaN
# ---------------------------------------------------------------------------

def demonstrate_special_float_values() -> None:
    """Demonstrate infinity and NaN behavior."""

    print("\n" + "=" * 80)
    print("26. INFINITY AND NaN")
    print("=" * 80)

    positive_infinity = float("inf")
    negative_infinity = float("-inf")
    not_a_number = float("nan")

    print("positive infinity:", positive_infinity)
    print("negative infinity:", negative_infinity)
    print("NaN:", not_a_number)

    print("inf + 100 =", positive_infinity + 100)
    print("inf * 2 =", positive_infinity * 2)
    print("inf > 1_000_000:", positive_infinity > 1_000_000)

    # NaN has unusual comparison behavior.
    print("NaN == NaN:", not_a_number == not_a_number)
    print("math.isnan(NaN):", math.isnan(not_a_number))


# ---------------------------------------------------------------------------
# 27. Arithmetic with functions
# ---------------------------------------------------------------------------

def average(numbers: Iterable[float]) -> float:
    """Calculate an arithmetic mean."""

    values = list(numbers)

    if not values:
        raise ValueError("at least one number is required")

    return sum(values) / len(values)


def weighted_average(
    values: Iterable[float],
    weights: Iterable[float],
) -> float:
    """Calculate a weighted average."""

    value_list = list(values)
    weight_list = list(weights)

    if len(value_list) != len(weight_list):
        raise ValueError("values and weights must have the same length")

    total_weight = sum(weight_list)

    if total_weight == 0:
        raise ValueError("total weight must not be zero")

    weighted_sum = sum(
        value * weight
        for value, weight in zip(value_list, weight_list)
    )

    return weighted_sum / total_weight


def demonstrate_statistical_arithmetic() -> None:
    """Demonstrate arithmetic used in simple statistics."""

    print("\n" + "=" * 80)
    print("27. STATISTICAL ARITHMETIC")
    print("=" * 80)

    data = [10, 20, 30, 40, 50]

    print("Data:", data)
    print("Sum:", sum(data))
    print("Count:", len(data))
    print("Average:", average(data))

    values = [80, 90, 70]
    weights = [0.2, 0.5, 0.3]

    print("Weighted average:", weighted_average(values, weights))


# ---------------------------------------------------------------------------
# 28. Compound calculations
# ---------------------------------------------------------------------------

def calculate_net_price(
    price: Decimal,
    discount_percent: Decimal,
    tax_percent: Decimal,
) -> Decimal:
    """
    Calculate a final price after discount and tax.

    Discount is applied first.
    Tax is then applied to the discounted amount.
    """

    if not 0 <= discount_percent <= 100:
        raise ValueError("discount must be between 0 and 100")

    if tax_percent < 0:
        raise ValueError("tax cannot be negative")

    discount_multiplier = Decimal("1") - discount_percent / Decimal("100")
    discounted_price = price * discount_multiplier

    tax_multiplier = Decimal("1") + tax_percent / Decimal("100")
    final_price = discounted_price * tax_multiplier

    return final_price


def demonstrate_compound_calculation() -> None:
    """Demonstrate a multi-stage commercial calculation."""

    print("\n" + "=" * 80)
    print("28. COMPOUND CALCULATIONS")
    print("=" * 80)

    price = Decimal("2500")
    discount = Decimal("10")
    tax = Decimal("18")

    final_price = calculate_net_price(price, discount, tax)

    print("Original price:", price)
    print("Discount:", discount, "%")
    print("Tax:", tax, "%")
    print("Final price:", final_price)


# ---------------------------------------------------------------------------
# 29. Order of operations in a larger expression
# ---------------------------------------------------------------------------

def demonstrate_complex_expression() -> None:
    """Break down a larger arithmetic expression for clarity."""

    print("\n" + "=" * 80)
    print("29. BREAKING DOWN COMPLEX EXPRESSIONS")
    print("=" * 80)

    # Original mathematical expression:
    #
    # ((a + b) * c - d ** 2) / e
    #
    # Breaking it into named steps makes the calculation easier to inspect.
    a = 10
    b = 5
    c = 3
    d = 4
    e = 2

    addition = a + b
    multiplication = addition * c
    power = d ** 2
    subtraction = multiplication - power
    result = subtraction / e

    print("a + b =", addition)
    print("(a + b) * c =", multiplication)
    print("d ** 2 =", power)
    print("((a + b) * c) - d ** 2 =", subtraction)
    print("Final result =", result)

    direct_result = ((a + b) * c - d ** 2) / e
    print("Direct expression result =", direct_result)


# ---------------------------------------------------------------------------
# 30. Arithmetic and assignment
# ---------------------------------------------------------------------------

def demonstrate_augmented_assignment() -> None:
    """Demonstrate arithmetic assignment operators."""

    print("\n" + "=" * 80)
    print("30. AUGMENTED ASSIGNMENT")
    print("=" * 80)

    value = 10

    value += 5
    print("After += 5:", value)

    value -= 3
    print("After -= 3:", value)

    value *= 2
    print("After *= 2:", value)

    value /= 4
    print("After /= 4:", value)

    value //= 2
    print("After //= 2:", value)

    value %= 3
    print("After %= 3:", value)

    value **= 4
    print("After **= 4:", value)


# ---------------------------------------------------------------------------
# 31. Arithmetic and comparison
# ---------------------------------------------------------------------------

def demonstrate_arithmetic_with_comparisons() -> None:
    """Show arithmetic expressions used inside conditions."""

    print("\n" + "=" * 80)
    print("31. ARITHMETIC WITH CONDITIONS")
    print("=" * 80)

    income = 85000
    expenses = 62000
    profit = income - expenses

    print("Income:", income)
    print("Expenses:", expenses)
    print("Profit:", profit)
    print("Profitable:", profit > 0)

    score = 87
    passing_score = 40

    print("Score:", score)
    print("Passed:", score >= passing_score)
    print("Difference from passing score:", score - passing_score)


# ---------------------------------------------------------------------------
# 32. Modulo applications
# ---------------------------------------------------------------------------

def demonstrate_modulo_applications() -> None:
    """Demonstrate practical uses of modulo."""

    print("\n" + "=" * 80)
    print("32. PRACTICAL USES OF MODULO")
    print("=" * 80)

    # Clock arithmetic.
    current_hour = 22
    hours_later = 7
    future_hour = (current_hour + hours_later) % 24

    print("22:00 + 7 hours ->", future_hour, ":00")

    # Circular indexing.
    items = ["A", "B", "C", "D"]
    index = 7
    circular_item = items[index % len(items)]

    print("Circular index 7 in four items ->", circular_item)

    # Alternating behavior.
    for position in range(8):
        state = "even-position" if position % 2 == 0 else "odd-position"
        print(position, state)


# ---------------------------------------------------------------------------
# 33. Power and roots
# ---------------------------------------------------------------------------

def demonstrate_powers_and_roots() -> None:
    """Demonstrate common ways to calculate roots."""

    print("\n" + "=" * 80)
    print("33. POWERS AND ROOTS")
    print("=" * 80)

    number = 64

    print("64 ** 2 =", number ** 2)
    print("Square root using ** 0.5:", number ** 0.5)
    print("Square root using math.sqrt:", math.sqrt(number))
    print("Cube root using ** (1/3):", number ** (1 / 3))

    # For exact integer roots, integer arithmetic can be preferable.
    print("isqrt(64):", math.isqrt(64))
    print("isqrt(65):", math.isqrt(65))

    # math.isqrt returns the floor of the square root for non-perfect squares.
    print("isqrt(65) ** 2:", math.isqrt(65) ** 2)


# ---------------------------------------------------------------------------
# 34. Distance formula
# ---------------------------------------------------------------------------

def calculate_distance(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> float:
    """Calculate Euclidean distance between two points."""

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def demonstrate_geometry_arithmetic() -> None:
    """Demonstrate arithmetic operators in geometry."""

    print("\n" + "=" * 80)
    print("34. GEOMETRY AND ARITHMETIC")
    print("=" * 80)

    point_a = (2, 3)
    point_b = (8, 11)

    distance = calculate_distance(
        point_a[0],
        point_a[1],
        point_b[0],
        point_b[1],
    )

    print("Point A:", point_a)
    print("Point B:", point_b)
    print("Distance:", distance)


# ---------------------------------------------------------------------------
# 35. Percentage change
# ---------------------------------------------------------------------------

def percentage_change(old_value: float, new_value: float) -> float:
    """Return percentage change from old_value to new_value."""

    if old_value == 0:
        raise ValueError("old_value cannot be zero")

    return (new_value - old_value) / old_value * 100


def demonstrate_percentage_change() -> None:
    """Demonstrate percentage change calculations."""

    print("\n" + "=" * 80)
    print("35. PERCENTAGE CHANGE")
    print("=" * 80)

    old_price = 100
    new_price = 125

    change = percentage_change(old_price, new_price)

    print("Old value:", old_price)
    print("New value:", new_price)
    print("Percentage change:", change, "%")

    decrease = percentage_change(200, 150)
    print("Decrease from 200 to 150:", decrease, "%")


# ---------------------------------------------------------------------------
# 36. Rounding and arithmetic
# ---------------------------------------------------------------------------

def demonstrate_rounding() -> None:
    """Demonstrate rounding and its interaction with numerical results."""

    print("\n" + "=" * 80)
    print("36. ROUNDING")
    print("=" * 80)

    values = [2.675, 2.685, 3.1415926535]

    for value in values:
        print(
            "value =",
            value,
            "| round(value, 2) =",
            round(value, 2),
        )

    # Rounding binary floats can surprise users because the stored value may
    # differ slightly from the decimal value written in source code.
    print("\nFor exact decimal rounding, Decimal can be preferable:")

    decimal_value = Decimal("2.675")
    print(
        "Decimal('2.675').quantize(Decimal('0.01')) =",
        decimal_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
    )


# ---------------------------------------------------------------------------
# 37. Arithmetic performance
# ---------------------------------------------------------------------------

def demonstrate_performance() -> None:
    """Provide a small performance demonstration."""

    print("\n" + "=" * 80)
    print("37. PERFORMANCE CONSIDERATIONS")
    print("=" * 80)

    integer_time = timeit.timeit(
        "10_000 * 20_000",
        number=1_000_000,
    )

    floating_time = timeit.timeit(
        "10_000.0 * 20_000.0",
        number=1_000_000,
    )

    print("Repeated integer multiplication time:", integer_time)
    print("Repeated float multiplication time:", floating_time)

    # Timing varies by machine, Python implementation, and system load.
    print(
        "\nPerformance measurements are environment-dependent. "
        "Arithmetic choice should normally be driven by correctness first."
    )


# ---------------------------------------------------------------------------
# 38. Large integer arithmetic
# ---------------------------------------------------------------------------

def demonstrate_large_integers() -> None:
    """Demonstrate Python's arbitrary-precision integer arithmetic."""

    print("\n" + "=" * 80)
    print("38. LARGE INTEGER ARITHMETIC")
    print("=" * 80)

    huge = 2 ** 1000

    print("2 ** 1000 calculated successfully.")
    print("Number of decimal digits:", len(str(huge)))
    print("Last 20 digits:", str(huge)[-20:])

    # Python integers grow as needed, limited by available memory and
    # implementation/resource constraints rather than fixed machine overflow.
    print("Python integer type:", type(huge).__name__)


# ---------------------------------------------------------------------------
# 39. Input validation
# ---------------------------------------------------------------------------

def parse_number(text: str) -> float:
    """Convert user text into a finite floating-point number."""

    try:
        value = float(text)
    except ValueError as error:
        raise ValueError(f"Invalid numeric input: {text!r}") from error

    if not math.isfinite(value):
        raise ValueError("Only finite numbers are accepted")

    return value


def calculate_from_inputs(
    first_text: str,
    operator_symbol: str,
    second_text: str,
) -> float:
    """Perform a validated arithmetic calculation from text inputs."""

    first = parse_number(first_text)
    second = parse_number(second_text)

    if operator_symbol == "+":
        return first + second
    if operator_symbol == "-":
        return first - second
    if operator_symbol == "*":
        return first * second
    if operator_symbol == "/":
        if second == 0:
            raise ZeroDivisionError("division by zero")
        return first / second
    if operator_symbol == "//":
        if second == 0:
            raise ZeroDivisionError("floor division by zero")
        return first // second
    if operator_symbol == "%":
        if second == 0:
            raise ZeroDivisionError("modulo by zero")
        return first % second
    if operator_symbol == "**":
        return first ** second

    raise ValueError(f"Unsupported operator: {operator_symbol!r}")


def demonstrate_validation() -> None:
    """Demonstrate safe handling of textual arithmetic input."""

    print("\n" + "=" * 80)
    print("39. INPUT VALIDATION")
    print("=" * 80)

    examples = [
        ("10", "+", "5"),
        ("10", "-", "5"),
        ("10", "*", "5"),
        ("10", "/", "5"),
        ("10", "//", "3"),
        ("10", "%", "3"),
        ("2", "**", "8"),
        ("10", "/", "0"),
        ("abc", "+", "5"),
    ]

    for first, symbol, second in examples:
        try:
            result = calculate_from_inputs(first, symbol, second)
            print(f"{first} {symbol} {second} = {result}")
        except (ValueError, ZeroDivisionError) as error:
            print(
                f"{first} {symbol} {second} -> "
                f"{type(error).__name__}: {error}"
            )


# ---------------------------------------------------------------------------
# 40. Why eval should not be used casually for user arithmetic
# ---------------------------------------------------------------------------

def demonstrate_expression_safety() -> None:
    """
    Explain why unrestricted eval is inappropriate for untrusted input.

    The function intentionally does not execute user-provided expressions.
    """

    print("\n" + "=" * 80)
    print("40. SECURITY CONSIDERATION: EXPRESSION EVALUATION")
    print("=" * 80)

    print(
        "Unrestricted eval() can execute arbitrary Python expressions and "
        "should not be used to evaluate untrusted arithmetic input."
    )

    print(
        "A production calculator should tokenize and parse permitted "
        "operators and operands instead of executing arbitrary source code."
    )

    # The safe arithmetic function above only accepts a predefined operator
    # set and converts input through controlled numeric parsing.
    print("10 + 5 through controlled parsing:", calculate_from_inputs("10", "+", "5"))


# ---------------------------------------------------------------------------
# 41. Arithmetic expression parser
# ---------------------------------------------------------------------------

class ArithmeticExpressionParser:
    """
    A small safe arithmetic parser supporting:

    - numeric literals
    - +, -, *, /, //, %, **
    - parentheses
    - unary + and -
    
    It does not execute arbitrary Python code.

    This implementation is intended as an educational demonstration of how
    arithmetic syntax can be parsed rather than passed to eval().
    """

    def __init__(self, expression: str) -> None:
        self.expression = expression
        self.position = 0

    def parse(self) -> float:
        """Parse the entire expression."""

        result = self._parse_expression()
        self._skip_spaces()

        if self.position != len(self.expression):
            raise ValueError(
                f"Unexpected character at position {self.position}: "
                f"{self.expression[self.position]!r}"
            )

        return result

    def _skip_spaces(self) -> None:
        while (
            self.position < len(self.expression)
            and self.expression[self.position].isspace()
        ):
            self.position += 1

    def _match(self, text: str) -> bool:
        self._skip_spaces()

        if self.expression.startswith(text, self.position):
            self.position += len(text)
            return True

        return False

    def _parse_expression(self) -> float:
        """Parse addition and subtraction."""

        value = self._parse_term()

        while True:
            if self._match("+"):
                value += self._parse_term()
            elif self._match("-"):
                value -= self._parse_term()
            else:
                return value

    def _parse_term(self) -> float:
        """Parse multiplication, division, floor division, and modulo."""

        value = self._parse_power()

        while True:
            if self._match("*"):
                # "**" belongs to exponentiation and must be checked first.
                if self._match("*"):
                    self.position -= 2
                    return value
                value *= self._parse_power()

            elif self._match("//"):
                divisor = self._parse_power()
                if divisor == 0:
                    raise ZeroDivisionError("floor division by zero")
                value //= divisor

            elif self._match("/"):
                divisor = self._parse_power()
                if divisor == 0:
                    raise ZeroDivisionError("division by zero")
                value /= divisor

            elif self._match("%"):
                divisor = self._parse_power()
                if divisor == 0:
                    raise ZeroDivisionError("modulo by zero")
                value %= divisor

            else:
                return value

    def _parse_power(self) -> float:
        """
        Parse exponentiation.

        Exponentiation is right-associative, so:
            2 ** 3 ** 2
        means:
            2 ** (3 ** 2)
        """

        value = self._parse_unary()

        self._skip_spaces()

        if self.expression.startswith("**", self.position):
            self.position += 2
            exponent = self._parse_power()
            value = value ** exponent

        return value

    def _parse_unary(self) -> float:
        """Parse unary plus and minus."""

        self._skip_spaces()

        if self._match("+"):
            return +self._parse_unary()

        if self._match("-"):
            return -self._parse_unary()

        return self._parse_primary()

    def _parse_primary(self) -> float:
        """Parse a number or parenthesized expression."""

        self._skip_spaces()

        if self._match("("):
            value = self._parse_expression()

            if not self._match(")"):
                raise ValueError("Missing closing parenthesis")

            return value

        start = self.position

        digits_seen = False
        decimal_point_seen = False

        while self.position < len(self.expression):
            character = self.expression[self.position]

            if character.isdigit():
                digits_seen = True
                self.position += 1

            elif character == "." and not decimal_point_seen:
                decimal_point_seen = True
                self.position += 1

            else:
                break

        if not digits_seen:
            raise ValueError(
                f"Expected a number at position {start}"
            )

        number_text = self.expression[start:self.position]

        try:
            return float(number_text)
        except ValueError as error:
            raise ValueError(
                f"Invalid number: {number_text!r}"
            ) from error


def demonstrate_safe_expression_parser() -> None:
    """Demonstrate the educational arithmetic parser."""

    print("\n" + "=" * 80)
    print("41. SAFE ARITHMETIC EXPRESSION PARSER")
    print("=" * 80)

    expressions = [
        "2 + 3 * 4",
        "(2 + 3) * 4",
        "10 / 2 + 5",
        "10 // 3",
        "17 % 5",
        "2 ** 3 ** 2",
        "-5 + 2 * 3",
        "2 ** (3 + 1)",
    ]

    for expression in expressions:
        try:
            result = ArithmeticExpressionParser(expression).parse()
            print(f"{expression} = {result}")
        except (ValueError, ZeroDivisionError) as error:
            print(f"{expression} -> {type(error).__name__}: {error}")


# ---------------------------------------------------------------------------
# 42. Parser edge cases
# ---------------------------------------------------------------------------

def demonstrate_parser_edge_cases() -> None:
    """Demonstrate malformed expression handling."""

    print("\n" + "=" * 80)
    print("42. PARSER EDGE CASES")
    print("=" * 80)

    invalid_expressions = [
        "10 / 0",
        "(10 + 5",
        "10 +",
        "abc + 5",
        "10 **",
        "10 @ 5",
    ]

    for expression in invalid_expressions:
        try:
            result = ArithmeticExpressionParser(expression).parse()
            print(f"{expression} = {result}")
        except (ValueError, ZeroDivisionError) as error:
            print(
                f"{expression!r} -> "
                f"{type(error).__name__}: {error}"
            )


# ---------------------------------------------------------------------------
# 43. Testing arithmetic functions
# ---------------------------------------------------------------------------

def assert_equal(actual: object, expected: object, description: str) -> None:
    """Simple educational assertion helper."""

    if actual != expected:
        raise AssertionError(
            f"{description}: expected {expected!r}, got {actual!r}"
        )


def assert_close(
    actual: float,
    expected: float,
    description: str,
    tolerance: float = 1e-9,
) -> None:
    """Assert approximate equality for floating-point values."""

    if not math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance):
        raise AssertionError(
            f"{description}: expected approximately {expected!r}, "
            f"got {actual!r}"
        )


def run_arithmetic_tests() -> None:
    """Run a compact set of correctness tests."""

    print("\n" + "=" * 80)
    print("43. TESTING")
    print("=" * 80)

    assert_equal(10 + 5, 15, "addition")
    assert_equal(10 - 5, 5, "subtraction")
    assert_equal(10 * 5, 50, "multiplication")
    assert_equal(10 // 3, 3, "floor division")
    assert_equal(10 % 3, 1, "modulo")
    assert_equal(2 ** 5, 32, "power")

    assert_close(10 / 4, 2.5, "true division")
    assert_close(calculate_circle_area(1), math.pi, "circle area")

    assert_equal(Fraction(1, 3) + Fraction(1, 6), Fraction(1, 2), "fractions")
    assert_equal(Decimal("0.1") + Decimal("0.2"), Decimal("0.3"), "decimal")

    assert_equal(
        ArithmeticExpressionParser("2 + 3 * 4").parse(),
        14.0,
        "parser precedence",
    )

    assert_equal(
        ArithmeticExpressionParser("2 ** 3 ** 2").parse(),
        512.0,
        "parser exponent associativity",
    )

    print("All arithmetic tests passed.")


# ---------------------------------------------------------------------------
# 44. Common mistakes
# ---------------------------------------------------------------------------

def demonstrate_common_mistakes() -> None:
    """Demonstrate common arithmetic mistakes and their corrections."""

    print("\n" + "=" * 80)
    print("44. COMMON MISTAKES")
    print("=" * 80)

    print("Mistake: using / when integer floor division is required.")
    print("10 / 3  =", 10 / 3)
    print("10 // 3 =", 10 // 3)

    print("\nMistake: assuming // truncates toward zero.")
    print("-7 // 2 =", -7 // 2)
    print("int(-7 / 2) =", int(-7 / 2))

    print("\nMistake: using == for approximate floating-point comparison.")
    print("0.1 + 0.2 == 0.3:", 0.1 + 0.2 == 0.3)
    print("math.isclose(...):", math.isclose(0.1 + 0.2, 0.3))

    print("\nMistake: forgetting operator precedence.")
    print("2 + 3 * 4 =", 2 + 3 * 4)
    print("(2 + 3) * 4 =", (2 + 3) * 4)

    print("\nMistake: dividing by zero.")
    try:
        _ = 100 / 0
    except ZeroDivisionError:
        print("Division by zero must be handled or prevented.")


# ---------------------------------------------------------------------------
# 45. Arithmetic design best practices
# ---------------------------------------------------------------------------

def demonstrate_best_practices() -> None:
    """Print concise design rules demonstrated by the preceding code."""

    print("\n" + "=" * 80)
    print("45. BEST PRACTICES")
    print("=" * 80)

    practices = [
        "Use parentheses when they make evaluation order clearer.",
        "Use / for true division and // when floor division is intended.",
        "Remember that // floors toward negative infinity.",
        "Use % for remainders, divisibility, and cyclic calculations.",
        "Use ** for exponentiation.",
        "Use math.isclose for approximate floating-point comparisons.",
        "Use Decimal when exact decimal arithmetic is important.",
        "Use Fraction when exact rational arithmetic is required.",
        "Validate denominators before division or modulo.",
        "Keep complex expressions readable by naming intermediate results.",
        "Do not use unrestricted eval() on untrusted arithmetic input.",
        "Test edge cases such as zero, negative values, and empty inputs.",
        "Choose numeric types based on correctness requirements, not habit.",
    ]

    for number, practice in enumerate(practices, start=1):
        print(f"{number:2}. {practice}")


# ---------------------------------------------------------------------------
# 46. Comparison table
# ---------------------------------------------------------------------------

def demonstrate_operator_comparison() -> None:
    """Compare the fundamental arithmetic operators."""

    print("\n" + "=" * 80)
    print("46. OPERATOR COMPARISON")
    print("=" * 80)

    rows = [
        ("+", "Addition", "10 + 3", 10 + 3),
        ("-", "Subtraction", "10 - 3", 10 - 3),
        ("*", "Multiplication", "10 * 3", 10 * 3),
        ("/", "True division", "10 / 3", 10 / 3),
        ("//", "Floor division", "10 // 3", 10 // 3),
        ("%", "Modulo", "10 % 3", 10 % 3),
        ("**", "Exponentiation", "10 ** 3", 10 ** 3),
    ]

    print(f"{'Operator':<10}{'Meaning':<20}{'Expression':<15}Result")
    print("-" * 65)

    for symbol, meaning, expression, result in rows:
        print(f"{symbol:<10}{meaning:<20}{expression:<15}{result}")


# ---------------------------------------------------------------------------
# 47. Mini calculator
# ---------------------------------------------------------------------------

def calculator(
    first: float,
    symbol: str,
    second: float,
) -> float:
    """
    A small reusable calculator based on explicit operator dispatch.

    This intentionally avoids eval() so that the supported arithmetic
    operations remain explicit and controlled.
    """

    operation_map: dict[str, Callable[[float, float], float]] = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "//": operator.floordiv,
        "%": operator.mod,
        "**": operator.pow,
    }

    if symbol not in operation_map:
        raise ValueError(f"Unsupported operator: {symbol}")

    if symbol in {"/", "//", "%"} and second == 0:
        raise ZeroDivisionError(
            f"cannot apply {symbol} with zero as the second operand"
        )

    return operation_map[symbol](first, second)


def demonstrate_calculator() -> None:
    """Demonstrate the reusable calculator function."""

    print("\n" + "=" * 80)
    print("47. MINI CALCULATOR")
    print("=" * 80)

    calculations = [
        (12, "+", 8),
        (12, "-", 8),
        (12, "*", 8),
        (12, "/", 8),
        (12, "//", 8),
        (12, "%", 8),
        (2, "**", 8),
    ]

    for first, symbol, second in calculations:
        print(
            f"{first} {symbol} {second} =",
            calculator(first, symbol, second),
        )


# ---------------------------------------------------------------------------
# 48. Main execution
# ---------------------------------------------------------------------------

def main() -> None:
    """Run all educational demonstrations in logical order."""

    print("=" * 80)
    print("ARITHMETIC OPERATORS IN PYTHON")
    print("=" * 80)
    print(
        "This standalone program demonstrates arithmetic from basic "
        "operators to numerical design and implementation."
    )

    demonstrate_numeric_values()
    demonstrate_addition()
    demonstrate_subtraction()
    demonstrate_multiplication()
    demonstrate_true_division()
    demonstrate_floor_division()
    demonstrate_modulo()
    demonstrate_exponentiation()
    demonstrate_unary_operators()
    demonstrate_precedence()
    demonstrate_associativity()
    demonstrate_mixed_numeric_types()
    demonstrate_float_precision()
    demonstrate_decimal()
    demonstrate_fractions()
    demonstrate_complex_arithmetic()
    demonstrate_conversions()
    demonstrate_common_patterns()
    demonstrate_practical_formulas()
    demonstrate_emi()
    demonstrate_operator_module()
    demonstrate_operator_overloading()
    demonstrate_reflected_operations()
    demonstrate_error_handling()
    demonstrate_edge_cases()
    demonstrate_special_float_values()
    demonstrate_statistical_arithmetic()
    demonstrate_compound_calculation()
    demonstrate_complex_expression()
    demonstrate_augmented_assignment()
    demonstrate_arithmetic_with_comparisons()
    demonstrate_modulo_applications()
    demonstrate_powers_and_roots()
    demonstrate_geometry_arithmetic()
    demonstrate_percentage_change()
    demonstrate_rounding()
    demonstrate_performance()
    demonstrate_large_integers()
    demonstrate_validation()
    demonstrate_expression_safety()
    demonstrate_safe_expression_parser()
    demonstrate_parser_edge_cases()
    run_arithmetic_tests()
    demonstrate_common_mistakes()
    demonstrate_best_practices()
    demonstrate_operator_comparison()
    demonstrate_calculator()

    print("\n" + "=" * 80)
    print("END OF ARITHMETIC OPERATORS STUDY SCRIPT")
    print("=" * 80)

    # sys.version provides useful context when comparing behavior across
    # Python versions.
    print("Python version:", sys.version.split()[0])


if __name__ == "__main__":
    main()
