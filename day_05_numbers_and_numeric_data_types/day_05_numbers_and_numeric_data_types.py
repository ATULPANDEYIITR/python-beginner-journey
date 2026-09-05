"""
NUMBERS AND NUMERIC DATA TYPES IN PYTHON
========================================

A comprehensive, self-contained study script covering Python numeric data
types from beginner fundamentals through advanced concepts.

Topics covered:
1. Numeric data types
2. Integers
3. Floating-point numbers
4. Complex numbers
5. Booleans as numeric values
6. Type conversion
7. Arithmetic operators
8. Comparison operators
9. Mathematical functions
10. Numeric precision
11. Floating-point limitations
12. Decimal arithmetic
13. Fraction arithmetic
14. Complex number operations
15. Bitwise operations
16. Binary, octal, and hexadecimal numbers
17. Numeric validation
18. Exceptions and error handling
19. Common mistakes
20. Performance considerations
21. Practical applications
22. Testing numeric code
23. Advanced numeric concepts
"""

from decimal import Decimal, getcontext, ROUND_HALF_UP, InvalidOperation
from fractions import Fraction
import math
import cmath
import random
import statistics
from typing import Union, Iterable


# ============================================================================
# 1. INTRODUCTION TO NUMERIC DATA TYPES
# ============================================================================

print("=" * 80)
print("1. PYTHON NUMERIC DATA TYPES")
print("=" * 80)

# Python provides several built-in numeric types.
integer_value = 42
floating_value = 3.14159
complex_value = 2 + 3j
boolean_value = True

print("Integer:", integer_value, "| Type:", type(integer_value))
print("Float:", floating_value, "| Type:", type(floating_value))
print("Complex:", complex_value, "| Type:", type(complex_value))
print("Boolean:", boolean_value, "| Type:", type(boolean_value))

# The most important built-in numeric types are:
#
# int      -> Whole numbers with arbitrary precision
# float    -> Floating-point numbers, usually IEEE 754 double precision
# complex  -> Numbers containing real and imaginary components
# bool     -> Logical values that behave numerically as 1 and 0


# ============================================================================
# 2. INTEGER DATA TYPE
# ============================================================================

print("\n" + "=" * 80)
print("2. INTEGER DATA TYPE")
print("=" * 80)

# Integers represent whole numbers.
positive_integer = 100
negative_integer = -25
zero = 0

print("Positive integer:", positive_integer)
print("Negative integer:", negative_integer)
print("Zero:", zero)

# Python integers have arbitrary precision.
# Unlike fixed-width integers in some languages, Python can store very large
# integer values limited primarily by available memory.
very_large_integer = 10 ** 100

print("Very large integer:", very_large_integer)
print("Number of digits:", len(str(very_large_integer)))

# Underscores can improve readability in large numeric literals.
population = 1_428_627_663
budget = 1_500_000_000

print("Population:", population)
print("Budget:", budget)

# Integer literals can also be written in different bases.
binary_integer = 0b1010
octal_integer = 0o12
hexadecimal_integer = 0xA

print("Binary 0b1010 =", binary_integer)
print("Octal 0o12 =", octal_integer)
print("Hexadecimal 0xA =", hexadecimal_integer)


# ============================================================================
# 3. FLOATING-POINT DATA TYPE
# ============================================================================

print("\n" + "=" * 80)
print("3. FLOATING-POINT DATA TYPE")
print("=" * 80)

# Floats represent real numbers with decimal components.
price = 99.99
temperature = -5.5
scientific_number = 1.2e3

print("Price:", price)
print("Temperature:", temperature)
print("Scientific notation 1.2e3:", scientific_number)

# Scientific notation can represent very large or very small values.
large_float = 5.67e20
small_float = 2.5e-8

print("Large float:", large_float)
print("Small float:", small_float)

# A float may represent an integer-looking value.
whole_number_float = 10.0
print("10.0 type:", type(whole_number_float))


# ============================================================================
# 4. COMPLEX NUMBERS
# ============================================================================

print("\n" + "=" * 80)
print("4. COMPLEX NUMBERS")
print("=" * 80)

# A complex number has the form:
#
#     a + bj
#
# where:
#     a = real part
#     b = imaginary part
#     j = square root of -1 in Python notation

z = 3 + 4j

print("Complex number:", z)
print("Real part:", z.real)
print("Imaginary part:", z.imag)
print("Complex conjugate:", z.conjugate())

# Magnitude is calculated using:
#
#     sqrt(real^2 + imaginary^2)

print("Magnitude using abs():", abs(z))

another_complex = 1 - 2j

print("Addition:", z + another_complex)
print("Subtraction:", z - another_complex)
print("Multiplication:", z * another_complex)
print("Division:", z / another_complex)

# cmath provides mathematical functions designed for complex numbers.
complex_square_root = cmath.sqrt(-9)
print("Square root of -9:", complex_square_root)


# ============================================================================
# 5. BOOLEAN AS A NUMERIC TYPE
# ============================================================================

print("\n" + "=" * 80)
print("5. BOOLEAN AS A NUMERIC TYPE")
print("=" * 80)

# bool is a subclass of int.
print("Is bool a subclass of int?", issubclass(bool, int))

print("True as integer:", int(True))
print("False as integer:", int(False))

print("True + True =", True + True)
print("True + False =", True + False)
print("False * 100 =", False * 100)

# This behavior can be useful when counting conditions.
scores = [85, 40, 70, 25, 95]
passing_count = sum(score >= 50 for score in scores)

print("Passing scores:", passing_count)


# ============================================================================
# 6. TYPE CONVERSION
# ============================================================================

print("\n" + "=" * 80)
print("6. NUMERIC TYPE CONVERSION")
print("=" * 80)

# int() converts compatible values to integers.
print("int(10.9):", int(10.9))
print("int(-10.9):", int(-10.9))

# Important behavior:
# int() truncates toward zero. It does not round.
print("int(3.99):", int(3.99))
print("int(-3.99):", int(-3.99))

# float() converts compatible values to floating-point numbers.
print("float(10):", float(10))
print("float('3.14'):", float("3.14"))

# complex() creates complex numbers.
print("complex(5):", complex(5))
print("complex(2, 3):", complex(2, 3))

# bool() converts values according to truth-value rules.
print("bool(0):", bool(0))
print("bool(1):", bool(1))
print("bool(-5):", bool(-5))
print("bool(0.0):", bool(0.0))

# String conversion can fail.
try:
    invalid_number = int("hello")
except ValueError as error:
    print("Conversion error:", error)


# ============================================================================
# 7. BASIC ARITHMETIC OPERATORS
# ============================================================================

print("\n" + "=" * 80)
print("7. ARITHMETIC OPERATORS")
print("=" * 80)

a = 17
b = 5

print("a =", a)
print("b =", b)

print("Addition:", a + b)
print("Subtraction:", a - b)
print("Multiplication:", a * b)
print("Division:", a / b)
print("Floor division:", a // b)
print("Remainder:", a % b)
print("Exponentiation:", a ** b)

# Division always produces a float in Python 3.
print("10 / 2 =", 10 / 2, "| Type:", type(10 / 2))

# Floor division rounds downward toward negative infinity.
print("17 // 5 =", 17 // 5)
print("-17 // 5 =", -17 // 5)
print("-17 / 5 =", -17 / 5)

# Modulo results follow an important mathematical relationship:
#
#     a == (a // b) * b + (a % b)

for dividend, divisor in [(17, 5), (-17, 5), (17, -5), (-17, -5)]:
    quotient = dividend // divisor
    remainder = dividend % divisor
    reconstructed = quotient * divisor + remainder

    print(
        f"{dividend} = ({quotient} * {divisor}) + {remainder} "
        f"-> {reconstructed == dividend}"
    )


# ============================================================================
# 8. OPERATOR PRECEDENCE
# ============================================================================

print("\n" + "=" * 80)
print("8. OPERATOR PRECEDENCE")
print("=" * 80)

# Multiplication occurs before addition.
expression_1 = 2 + 3 * 4

# Parentheses change evaluation order.
expression_2 = (2 + 3) * 4

print("2 + 3 * 4 =", expression_1)
print("(2 + 3) * 4 =", expression_2)

# Exponentiation has higher precedence than multiplication.
print("2 + 3 ** 2 =", 2 + 3 ** 2)

# Exponentiation associates from right to left.
print("2 ** 3 ** 2 =", 2 ** 3 ** 2)
print("(2 ** 3) ** 2 =", (2 ** 3) ** 2)


# ============================================================================
# 9. COMPARISON OPERATORS
# ============================================================================

print("\n" + "=" * 80)
print("9. COMPARISON OPERATORS")
print("=" * 80)

x = 10
y = 20

print("x == y:", x == y)
print("x != y:", x != y)
print("x < y:", x < y)
print("x > y:", x > y)
print("x <= y:", x <= y)
print("x >= y:", x >= y)

# Comparisons return boolean values.
result = x < y
print("Comparison type:", type(result))

# Python supports chained comparisons.
age = 25
print("18 <= age <= 60:", 18 <= age <= 60)


# ============================================================================
# 10. AUGMENTED ASSIGNMENT
# ============================================================================

print("\n" + "=" * 80)
print("10. AUGMENTED ASSIGNMENT")
print("=" * 80)

balance = 100

balance += 50
print("After += 50:", balance)

balance -= 20
print("After -= 20:", balance)

balance *= 2
print("After *= 2:", balance)

balance /= 5
print("After /= 5:", balance)

# Notice that /= changes an integer into a float.
print("Current type:", type(balance))


# ============================================================================
# 11. BUILT-IN NUMERIC FUNCTIONS
# ============================================================================

print("\n" + "=" * 80)
print("11. BUILT-IN NUMERIC FUNCTIONS")
print("=" * 80)

numbers = [-10, 4, 8, -3, 15]

print("Numbers:", numbers)
print("Absolute value:", abs(-42))
print("Minimum:", min(numbers))
print("Maximum:", max(numbers))
print("Sum:", sum(numbers))
print("Power:", pow(2, 10))
print("Power with modulo:", pow(2, 10, 1000))
print("Rounded:", round(3.14159, 2))

# divmod returns quotient and remainder together.
quotient, remainder = divmod(17, 5)

print("divmod(17, 5):", (quotient, remainder))

# all() and any() can work with numeric truth values.
print("all([1, 2, 3]):", all([1, 2, 3]))
print("all([1, 0, 3]):", all([1, 0, 3]))
print("any([0, 0, 3]):", any([0, 0, 3]))
print("any([0, 0, 0]):", any([0, 0, 0]))


# ============================================================================
# 12. ROUNDING
# ============================================================================

print("\n" + "=" * 80)
print("12. ROUNDING")
print("=" * 80)

print("round(3.14159, 2):", round(3.14159, 2))
print("round(3.5):", round(3.5))
print("round(4.5):", round(4.5))

# Python uses banker's rounding for exact halfway cases.
# It rounds to the nearest even number.
print("round(2.5):", round(2.5))
print("round(3.5):", round(3.5))

# math.floor rounds downward.
print("math.floor(3.9):", math.floor(3.9))
print("math.floor(-3.1):", math.floor(-3.1))

# math.ceil rounds upward.
print("math.ceil(3.1):", math.ceil(3.1))
print("math.ceil(-3.9):", math.ceil(-3.9))

# math.trunc removes the fractional component toward zero.
print("math.trunc(3.9):", math.trunc(3.9))
print("math.trunc(-3.9):", math.trunc(-3.9))


# ============================================================================
# 13. FLOATING-POINT PRECISION
# ============================================================================

print("\n" + "=" * 80)
print("13. FLOATING-POINT PRECISION")
print("=" * 80)

# Decimal fractions cannot always be represented exactly in binary floating-point.
precision_problem = 0.1 + 0.2

print("0.1 + 0.2 =", precision_problem)
print("0.1 + 0.2 == 0.3:", precision_problem == 0.3)

# Avoid direct equality comparisons when floating-point calculations are involved.
print(
    "math.isclose(0.1 + 0.2, 0.3):",
    math.isclose(0.1 + 0.2, 0.3)
)

# Absolute and relative tolerances can be specified.
calculated = 1.000000001
expected = 1.0

print(
    "Close with tolerance:",
    math.isclose(calculated, expected, rel_tol=1e-8)
)


# ============================================================================
# 14. SPECIAL FLOAT VALUES
# ============================================================================

print("\n" + "=" * 80)
print("14. SPECIAL FLOAT VALUES")
print("=" * 80)

positive_infinity = float("inf")
negative_infinity = float("-inf")
not_a_number = float("nan")

print("Positive infinity:", positive_infinity)
print("Negative infinity:", negative_infinity)
print("NaN:", not_a_number)

print("math.isinf(infinity):", math.isinf(positive_infinity))
print("math.isnan(NaN):", math.isnan(not_a_number))

# NaN has unusual comparison behavior.
print("NaN == NaN:", not_a_number == not_a_number)
print("NaN != NaN:", not_a_number != not_a_number)

# Use math.isnan() instead of equality for NaN detection.
print("Correct NaN detection:", math.isnan(not_a_number))


# ============================================================================
# 15. DECIMAL FOR EXACT DECIMAL ARITHMETIC
# ============================================================================

print("\n" + "=" * 80)
print("15. DECIMAL ARITHMETIC")
print("=" * 80)

# Decimal is useful when exact base-10 arithmetic is required,
# particularly for financial calculations.

decimal_result = Decimal("0.1") + Decimal("0.2")

print("Decimal('0.1') + Decimal('0.2') =", decimal_result)
print("Exact comparison:", decimal_result == Decimal("0.3"))

# Construct Decimal values from strings when precision matters.
# Decimal(0.1) inherits the already approximate binary float representation.
from_float = Decimal(0.1)
from_string = Decimal("0.1")

print("Decimal from float:", from_float)
print("Decimal from string:", from_string)

# Decimal precision can be configured.
getcontext().prec = 28

large_decimal_calculation = Decimal(1) / Decimal(7)
print("1 / 7 with Decimal precision:", large_decimal_calculation)

# Financial rounding example.
price = Decimal("19.995")
rounded_price = price.quantize(
    Decimal("0.01"),
    rounding=ROUND_HALF_UP
)

print("Rounded financial price:", rounded_price)


# ============================================================================
# 16. FRACTION FOR EXACT RATIONAL NUMBERS
# ============================================================================

print("\n" + "=" * 80)
print("16. FRACTION ARITHMETIC")
print("=" * 80)

# Fraction represents rational numbers exactly.
one_third = Fraction(1, 3)
one_sixth = Fraction(1, 6)

print("1/3:", one_third)
print("1/6:", one_sixth)
print("1/3 + 1/6:", one_third + one_sixth)

# Fractions are automatically simplified.
simplified = Fraction(10, 20)
print("Fraction(10, 20):", simplified)

# Fractions can be constructed from strings.
fraction_from_string = Fraction("3/7")
print("Fraction('3/7'):", fraction_from_string)

# Fraction.from_float can approximate a float.
approximation = Fraction(0.1).limit_denominator()
print("Fraction approximation of 0.1:", approximation)


# ============================================================================
# 17. MATHEMATICAL FUNCTIONS
# ============================================================================

print("\n" + "=" * 80)
print("17. MATHEMATICAL FUNCTIONS")
print("=" * 80)

value = 16

print("Square root:", math.sqrt(value))
print("Factorial of 5:", math.factorial(5))
print("GCD of 48 and 18:", math.gcd(48, 18))
print("LCM of 12 and 18:", math.lcm(12, 18))

# Constants.
print("Pi:", math.pi)
print("Euler's number:", math.e)
print("Tau:", math.tau)

# Trigonometric functions use radians.
angle_degrees = 90
angle_radians = math.radians(angle_degrees)

print("90 degrees in radians:", angle_radians)
print("sin(90 degrees):", math.sin(angle_radians))

# Logarithms.
print("Natural logarithm of e:", math.log(math.e))
print("Base-10 logarithm of 1000:", math.log10(1000))
print("Base-2 logarithm of 8:", math.log2(8))


# ============================================================================
# 18. NUMBER BASES AND CONVERSION
# ============================================================================

print("\n" + "=" * 80)
print("18. NUMBER BASES AND CONVERSION")
print("=" * 80)

number = 255

print("Decimal:", number)
print("Binary:", bin(number))
print("Octal:", oct(number))
print("Hexadecimal:", hex(number))

# Convert strings in different bases to integers.
binary_string = "11111111"
hex_string = "FF"

print("Binary string to integer:", int(binary_string, 2))
print("Hexadecimal string to integer:", int(hex_string, 16))

# Format without prefixes.
print("Binary without prefix:", format(number, "b"))
print("Octal without prefix:", format(number, "o"))
print("Hexadecimal without prefix:", format(number, "X"))


# ============================================================================
# 19. BITWISE OPERATIONS
# ============================================================================

print("\n" + "=" * 80)
print("19. BITWISE OPERATIONS")
print("=" * 80)

left = 12   # 1100
right = 10  # 1010

print("left:", left, bin(left))
print("right:", right, bin(right))

print("AND:", left & right, bin(left & right))
print("OR:", left | right, bin(left | right))
print("XOR:", left ^ right, bin(left ^ right))
print("NOT left:", ~left)
print("Left shift:", left << 1)
print("Right shift:", left >> 1)

# Bit masks are useful for compact flag storage.
READ_PERMISSION = 0b001
WRITE_PERMISSION = 0b010
EXECUTE_PERMISSION = 0b100

permissions = READ_PERMISSION | WRITE_PERMISSION

print("Permissions:", bin(permissions))
print(
    "Can read?",
    bool(permissions & READ_PERMISSION)
)
print(
    "Can execute?",
    bool(permissions & EXECUTE_PERMISSION)
)


# ============================================================================
# 20. NUMERIC INPUT VALIDATION
# ============================================================================

print("\n" + "=" * 80)
print("20. NUMERIC INPUT VALIDATION")
print("=" * 80)


def parse_positive_integer(value: str) -> int:
    """
    Convert a string to a strictly positive integer.

    Raises:
        ValueError: If the input is not an integer or is not positive.
    """

    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError("Input must contain a valid integer.")

    if number <= 0:
        raise ValueError("Input must be greater than zero.")

    return number


test_inputs = ["25", "0", "-5", "3.14", "hello"]

for test_input in test_inputs:
    try:
        parsed = parse_positive_integer(test_input)
        print(f"{test_input!r} -> {parsed}")
    except ValueError as error:
        print(f"{test_input!r} -> Error: {error}")


# ============================================================================
# 21. SAFE DIVISION
# ============================================================================

print("\n" + "=" * 80)
print("21. SAFE DIVISION")
print("=" * 80)


def safe_divide(
    numerator: Union[int, float],
    denominator: Union[int, float]
) -> float:
    """
    Divide two numeric values safely.

    Raises:
        TypeError: If values are not numeric.
        ZeroDivisionError: If denominator is zero.
    """

    if not isinstance(numerator, (int, float)):
        raise TypeError("Numerator must be numeric.")

    if not isinstance(denominator, (int, float)):
        raise TypeError("Denominator must be numeric.")

    if denominator == 0:
        raise ZeroDivisionError("Cannot divide by zero.")

    return numerator / denominator


division_cases = [(10, 2), (5, 0), (10, 4)]

for numerator, denominator in division_cases:
    try:
        print(
            f"{numerator} / {denominator} =",
            safe_divide(numerator, denominator)
        )
    except (TypeError, ZeroDivisionError) as error:
        print(
            f"{numerator} / {denominator} -> Error:",
            error
        )


# ============================================================================
# 22. AVERAGE AND BASIC STATISTICS
# ============================================================================

print("\n" + "=" * 80)
print("22. NUMERIC DATA AND STATISTICS")
print("=" * 80)


def calculate_average(values: Iterable[Union[int, float]]) -> float:
    """
    Calculate the arithmetic mean.

    Raises:
        ValueError: If no values are provided.
    """

    values = list(values)

    if not values:
        raise ValueError("Cannot calculate average of an empty collection.")

    return sum(values) / len(values)


dataset = [72, 85, 91, 68, 88, 95]

print("Dataset:", dataset)
print("Mean:", calculate_average(dataset))
print("Median:", statistics.median(dataset))
print("Minimum:", min(dataset))
print("Maximum:", max(dataset))
print("Range:", max(dataset) - min(dataset))

# Population variance and standard deviation.
print("Population variance:", statistics.pvariance(dataset))
print("Population standard deviation:", statistics.pstdev(dataset))


# ============================================================================
# 23. NUMERIC ALGORITHMS: PRIME NUMBER CHECKING
# ============================================================================

print("\n" + "=" * 80)
print("23. NUMERIC ALGORITHM: PRIME NUMBER CHECKING")
print("=" * 80)


def is_prime(number: int) -> bool:
    """
    Return True if number is prime.

    Performance consideration:
    Testing divisors only up to sqrt(number) is much faster than testing all
    values up to number - 1.
    """

    if number <= 1:
        return False

    if number <= 3:
        return True

    if number % 2 == 0 or number % 3 == 0:
        return False

    candidate = 5

    while candidate * candidate <= number:
        if number % candidate == 0:
            return False

        if number % (candidate + 2) == 0:
            return False

        candidate += 6

    return True


prime_test_values = [1, 2, 3, 4, 5, 17, 25, 97, 100]

for value in prime_test_values:
    print(f"{value} is prime:", is_prime(value))


# ============================================================================
# 24. NUMERIC ALGORITHMS: GREATEST COMMON DIVISOR
# ============================================================================

print("\n" + "=" * 80)
print("24. NUMERIC ALGORITHM: EUCLIDEAN GCD")
print("=" * 80)


def euclidean_gcd(first: int, second: int) -> int:
    """
    Calculate the greatest common divisor using the Euclidean algorithm.
    """

    first = abs(first)
    second = abs(second)

    while second != 0:
        first, second = second, first % second

    return first


print("GCD(48, 18):", euclidean_gcd(48, 18))
print("GCD(270, 192):", euclidean_gcd(270, 192))
print("GCD(-48, 18):", euclidean_gcd(-48, 18))


# ============================================================================
# 25. NUMERIC ALGORITHMS: FACTORIAL
# ============================================================================

print("\n" + "=" * 80)
print("25. NUMERIC ALGORITHM: FACTORIAL")
print("=" * 80)


def factorial_iterative(number: int) -> int:
    """
    Calculate factorial iteratively.

    Factorial definition:
        n! = n * (n - 1) * ... * 1

    Special case:
        0! = 1
    """

    if not isinstance(number, int):
        raise TypeError("Factorial requires an integer.")

    if number < 0:
        raise ValueError("Factorial is not defined for negative integers.")

    result = 1

    for current in range(2, number + 1):
        result *= current

    return result


for value in range(6):
    print(f"{value}! =", factorial_iterative(value))


# ============================================================================
# 26. NUMERIC SIMULATION: COMPOUND INTEREST
# ============================================================================

print("\n" + "=" * 80)
print("26. PRACTICAL APPLICATION: COMPOUND INTEREST")
print("=" * 80)


def compound_interest(
    principal: float,
    annual_rate: float,
    years: float,
    compounds_per_year: int = 1
) -> float:
    """
    Calculate compound interest.

    Formula:
        A = P * (1 + r / n) ** (n * t)

    P = principal
    r = annual interest rate as a decimal
    n = number of compounding periods per year
    t = number of years
    """

    if principal < 0:
        raise ValueError("Principal cannot be negative.")

    if compounds_per_year <= 0:
        raise ValueError("Compounds per year must be positive.")

    amount = principal * (
        1 + annual_rate / compounds_per_year
    ) ** (compounds_per_year * years)

    return amount


principal = 100_000
annual_rate = 0.08
years = 5

final_amount = compound_interest(
    principal,
    annual_rate,
    years,
    compounds_per_year=12
)

print("Principal:", principal)
print("Annual rate:", annual_rate)
print("Years:", years)
print("Final amount:", round(final_amount, 2))
print("Interest earned:", round(final_amount - principal, 2))


# ============================================================================
# 27. PRACTICAL APPLICATION: PERCENTAGES
# ============================================================================

print("\n" + "=" * 80)
print("27. PRACTICAL APPLICATION: PERCENTAGES")
print("=" * 80)


def percentage(part: float, whole: float) -> float:
    """
    Calculate what percentage 'part' represents of 'whole'.
    """

    if whole == 0:
        raise ZeroDivisionError("Whole cannot be zero.")

    return (part / whole) * 100


sales = 750
target = 1000

print(
    "Percentage of target achieved:",
    percentage(sales, target)
)

original_price = 2000
discount_percent = 15

discount = original_price * discount_percent / 100
final_price = original_price - discount

print("Original price:", original_price)
print("Discount:", discount)
print("Final price:", final_price)


# ============================================================================
# 28. PRACTICAL APPLICATION: UNIT CONVERSION
# ============================================================================

print("\n" + "=" * 80)
print("28. PRACTICAL APPLICATION: UNIT CONVERSION")
print("=" * 80)


def celsius_to_fahrenheit(celsius: float) -> float:
    return (celsius * 9 / 5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) * 5 / 9


temperature_celsius = 25

temperature_fahrenheit = celsius_to_fahrenheit(
    temperature_celsius
)

print(
    f"{temperature_celsius}°C = "
    f"{temperature_fahrenheit}°F"
)

print(
    f"{temperature_fahrenheit}°F = "
    f"{fahrenheit_to_celsius(temperature_fahrenheit)}°C"
)


# ============================================================================
# 29. RANDOM NUMBERS
# ============================================================================

print("\n" + "=" * 80)
print("29. RANDOM NUMBERS")
print("=" * 80)

# random.randint includes both endpoints.
random_integer = random.randint(1, 10)

# random.random returns a float in [0.0, 1.0).
random_float = random.random()

print("Random integer:", random_integer)
print("Random float:", random_float)

# random.uniform returns a random float between specified bounds.
random_temperature = random.uniform(20.0, 35.0)

print("Random temperature:", random_temperature)

# Important security note:
# The random module is not suitable for security-sensitive values such as
# passwords, authentication tokens, or cryptographic keys.


# ============================================================================
# 30. MONTE CARLO SIMULATION
# ============================================================================

print("\n" + "=" * 80)
print("30. ADVANCED APPLICATION: MONTE CARLO ESTIMATION OF PI")
print("=" * 80)


def estimate_pi(samples: int) -> float:
    """
    Estimate pi using random points.

    A square with side length 2 contains a circle with radius 1.

    Probability that a random point lies inside the circle:
        circle area / square area
        pi / 4

    Therefore:
        pi approximately equals 4 * points_inside / total_points
    """

    if samples <= 0:
        raise ValueError("Samples must be positive.")

    inside_circle = 0

    for _ in range(samples):
        x_coordinate = random.uniform(-1, 1)
        y_coordinate = random.uniform(-1, 1)

        if (
            x_coordinate ** 2
            + y_coordinate ** 2
            <= 1
        ):
            inside_circle += 1

    return 4 * inside_circle / samples


pi_estimate = estimate_pi(10_000)

print("Estimated pi:", pi_estimate)
print("Actual pi:", math.pi)
print("Absolute error:", abs(pi_estimate - math.pi))


# ============================================================================
# 31. OVERFLOW, UNDERFLOW, AND LARGE NUMBERS
# ============================================================================

print("\n" + "=" * 80)
print("31. LARGE NUMBERS AND NUMERIC LIMITATIONS")
print("=" * 80)

# Python integers can grow to very large sizes.
huge_integer = 2 ** 1000

print("Digits in 2 ** 1000:", len(str(huge_integer)))

# Floats have finite precision and range.
very_large_float = 1e308

print("Large float:", very_large_float)

# Integer arithmetic is exact, but extremely large integer calculations
# require additional memory and CPU time.


# ============================================================================
# 32. MIXING NUMERIC TYPES
# ============================================================================

print("\n" + "=" * 80)
print("32. MIXING NUMERIC TYPES")
print("=" * 80)

integer = 10
floating = 2.5
fraction = Fraction(1, 2)

print("int + float:", integer + floating)
print("int + Fraction:", integer + fraction)

# Decimal and float should generally not be mixed directly.
money = Decimal("10.50")

try:
    invalid_mixed_operation = money + 0.25
except TypeError as error:
    print("Decimal + float error:", error)

# Use compatible types.
correct_operation = money + Decimal("0.25")
print("Decimal + Decimal:", correct_operation)


# ============================================================================
# 33. COMMON NUMERIC MISTAKES
# ============================================================================

print("\n" + "=" * 80)
print("33. COMMON NUMERIC MISTAKES")
print("=" * 80)

# Mistake 1: Assuming / performs integer division.
print("5 / 2 =", 5 / 2)
print("5 // 2 =", 5 // 2)

# Mistake 2: Comparing floating-point values directly.
print("0.1 + 0.2 == 0.3:", 0.1 + 0.2 == 0.3)

# Correct approach.
print(
    "Using isclose:",
    math.isclose(0.1 + 0.2, 0.3)
)

# Mistake 3: Forgetting that int() truncates.
print("int(9.9):", int(9.9))
print("round(9.9):", round(9.9))

# Mistake 4: Division by zero.
try:
    value = 10 / 0
except ZeroDivisionError:
    print("Division by zero must be handled.")

# Mistake 5: Incorrect percentage conversion.
percent = 25

incorrect = 1000 * percent
correct = 1000 * (percent / 100)

print("Incorrect percentage calculation:", incorrect)
print("Correct percentage calculation:", correct)


# ============================================================================
# 34. PERFORMANCE COMPARISON: FLOAT VS DECIMAL
# ============================================================================

print("\n" + "=" * 80)
print("34. PERFORMANCE AND TYPE TRADE-OFFS")
print("=" * 80)

# Conceptual comparison:
#
# int:
#   Exact whole-number arithmetic.
#   Can handle arbitrarily large integers.
#
# float:
#   Fast and widely supported.
#   Subject to binary precision limitations.
#
# Decimal:
#   Exact decimal representation.
#   Often slower than float.
#   Appropriate for many financial calculations.
#
# Fraction:
#   Exact rational arithmetic.
#   Numerators and denominators can become very large.
#
# complex:
#   Supports calculations involving imaginary components.


# ============================================================================
# 35. ADVANCED: NUMERIC CLASS WITH VALIDATION
# ============================================================================

print("\n" + "=" * 80)
print("35. ADVANCED IMPLEMENTATION: BANK ACCOUNT BALANCE")
print("=" * 80)


class BankAccount:
    """
    A small example showing why Decimal is useful for financial values.

    The class prevents floating-point precision problems by storing balances
    as Decimal values.
    """

    def __init__(self, initial_balance: str = "0.00"):
        self.balance = Decimal(initial_balance)

        if self.balance < 0:
            raise ValueError("Initial balance cannot be negative.")

    def deposit(self, amount: str) -> None:
        amount_decimal = Decimal(amount)

        if amount_decimal <= 0:
            raise ValueError("Deposit amount must be positive.")

        self.balance += amount_decimal

    def withdraw(self, amount: str) -> None:
        amount_decimal = Decimal(amount)

        if amount_decimal <= 0:
            raise ValueError("Withdrawal amount must be positive.")

        if amount_decimal > self.balance:
            raise ValueError("Insufficient balance.")

        self.balance -= amount_decimal

    def formatted_balance(self) -> Decimal:
        return self.balance.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )


account = BankAccount("100.00")

account.deposit("25.50")
account.withdraw("40.25")

print("Account balance:", account.formatted_balance())


# ============================================================================
# 36. ADVANCED: NUMERIC TESTING
# ============================================================================

print("\n" + "=" * 80)
print("36. TESTING NUMERIC CODE")
print("=" * 80)


def square(number: Union[int, float]) -> Union[int, float]:
    return number * number


# Exact values can use direct equality.
assert square(5) == 25
assert square(-3) == 9

# Floating-point calculations should often use math.isclose().
assert math.isclose(
    square(0.1),
    0.01,
    rel_tol=1e-9,
    abs_tol=1e-12
)

# Test edge cases.
assert factorial_iterative(0) == 1
assert euclidean_gcd(0, 5) == 5
assert is_prime(1) is False
assert is_prime(2) is True

print("Numeric tests completed successfully.")


# ============================================================================
# 37. ADVANCED: NUMERIC DATA CLEANING
# ============================================================================

print("\n" + "=" * 80)
print("37. NUMERIC DATA CLEANING")
print("=" * 80)


def clean_numeric_values(
    values: Iterable[object]
) -> list[float]:
    """
    Convert valid numeric values to floats.

    Invalid values, None, NaN, and infinity are excluded.
    """

    cleaned_values = []

    for value in values:
        try:
            numeric_value = float(value)

            if not math.isfinite(numeric_value):
                continue

            cleaned_values.append(numeric_value)

        except (TypeError, ValueError):
            continue

    return cleaned_values


raw_values = [
    10,
    "25.5",
    None,
    "invalid",
    float("nan"),
    float("inf"),
    -3
]

cleaned = clean_numeric_values(raw_values)

print("Raw values:", raw_values)
print("Cleaned numeric values:", cleaned)
print("Average:", calculate_average(cleaned))


# ============================================================================
# 38. ADVANCED: LINEAR INTERPOLATION
# ============================================================================

print("\n" + "=" * 80)
print("38. ADVANCED NUMERIC APPLICATION: LINEAR INTERPOLATION")
print("=" * 80)


def linear_interpolation(
    x: float,
    x0: float,
    y0: float,
    x1: float,
    y1: float
) -> float:
    """
    Estimate y for x between two known points.

    Formula:
        y = y0 + (x - x0) * (y1 - y0) / (x1 - x0)
    """

    if x0 == x1:
        raise ValueError(
            "Interpolation requires two different x coordinates."
        )

    return y0 + (
        (x - x0)
        * (y1 - y0)
        / (x1 - x0)
    )


interpolated_value = linear_interpolation(
    x=5,
    x0=0,
    y0=0,
    x1=10,
    y1=100
)

print("Interpolated value:", interpolated_value)


# ============================================================================
# 39. ADVANCED: NUMERICAL DERIVATIVE
# ============================================================================

print("\n" + "=" * 80)
print("39. ADVANCED NUMERIC APPLICATION: NUMERICAL DERIVATIVE")
print("=" * 80)


def numerical_derivative(
    function,
    x: float,
    step: float = 1e-6
) -> float:
    """
    Approximate a derivative using the central difference formula:

        f'(x) approximately equals
        (f(x + h) - f(x - h)) / (2h)

    Smaller step sizes may improve approximation initially, but extremely small
    values can increase floating-point rounding errors.
    """

    if step <= 0:
        raise ValueError("Step must be positive.")

    return (
        function(x + step)
        - function(x - step)
    ) / (2 * step)


def quadratic(value: float) -> float:
    return value ** 2


derivative_at_5 = numerical_derivative(
    quadratic,
    5
)

print("Approximate derivative of x^2 at x=5:", derivative_at_5)
print("Expected derivative:", 10)


# ============================================================================
# 40. FINAL NUMERIC TYPE COMPARISON
# ============================================================================

print("\n" + "=" * 80)
print("40. NUMERIC TYPE COMPARISON")
print("=" * 80)

numeric_examples = [
    42,
    3.14,
    2 + 3j,
    True,
    Decimal("10.25"),
    Fraction(3, 4)
]

for numeric_example in numeric_examples:
    print(
        f"Value: {numeric_example!r:>25} | "
        f"Type: {type(numeric_example).__name__}"
    )

print("\nStudy script completed.")
