"""
TYPE CHECKING AND TYPE CONVERSION IN PYTHON
===========================================

A self-contained study and demonstration script covering Python's type system,
runtime type checking, explicit and implicit conversion, parsing, validation,
custom types, static type hints, protocols, generics, numeric conversions,
collection conversions, serialization-related conversions, edge cases,
error handling, testing, performance, and production-oriented practices.

Run:
    python type_checking_and_type_conversion.py

The script uses only Python's standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from numbers import Number, Integral, Real
from typing import (
    Any,
    Generic,
    Iterable,
    Optional,
    Protocol,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
    overload,
    runtime_checkable,
)
import math
import timeit


# =============================================================================
# 1. FUNDAMENTAL CONCEPTS
# =============================================================================

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    """Print a readable subsection heading."""
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def demonstrate_basic_types() -> None:
    section("1. BASIC PYTHON TYPES")

    # Every ordinary Python object has a runtime type.
    values = [
        None,
        True,
        42,
        3.14,
        2 + 3j,
        "Python",
        [1, 2, 3],
        (1, 2, 3),
        {1, 2, 3},
        {"language": "Python"},
        b"Python",
        bytearray(b"Python"),
    ]

    for value in values:
        print(
            f"value={value!r:<25} "
            f"type={type(value).__name__:<12} "
            f"id={id(value)}"
        )

    # bool is a subclass of int.
    print("\nImportant inheritance relationship:")
    print("isinstance(True, int):", isinstance(True, int))
    print("type(True) is int:", type(True) is int)

    # The two expressions are intentionally different:
    # isinstance() respects inheritance; type(x) is T requires an exact type.
    print("isinstance(42, int):", isinstance(42, int))
    print("type(42) is int:", type(42) is int)


# =============================================================================
# 2. TYPE() AND ISINSTANCE()
# =============================================================================

class CustomInteger(int):
    """An int subclass used to demonstrate inheritance-aware checks."""


def demonstrate_type_and_isinstance() -> None:
    section("2. type() VERSUS isinstance()")

    number = CustomInteger(10)

    print("type(number):", type(number))
    print("type(number) is int:", type(number) is int)
    print("isinstance(number, int):", isinstance(number, int))

    # Use type(x) is T when exact runtime identity matters.
    # Use isinstance(x, T) when subclasses should also be accepted.
    #
    # In application code, isinstance() is usually the more flexible choice.

    examples = [
        10,
        True,
        10.5,
        "10",
        [10],
    ]

    for value in examples:
        print(
            f"{value!r:>10} -> "
            f"isinstance(value, int)={isinstance(value, int)!s:<5}, "
            f"type(value) is int={type(value) is int}"
        )


# =============================================================================
# 3. TYPE INFORMATION
# =============================================================================

def describe_runtime_type(value: Any) -> str:
    """
    Return useful runtime type information.

    __class__ and type(value) normally identify the same runtime class.
    """
    return (
        f"repr={value!r}, "
        f"type={type(value).__name__}, "
        f"module={type(value).__module__}"
    )


def demonstrate_type_information() -> None:
    section("3. RUNTIME TYPE INFORMATION")

    values = [10, "hello", [1, 2], None]

    for value in values:
        print(describe_runtime_type(value))

    print("\nObject/class relationships:")
    print("10.__class__:", (10).__class__)
    print("10.__class__ is type(10):", (10).__class__ is type(10))


# =============================================================================
# 4. BUILT-IN TYPE CONVERSION
# =============================================================================

def demonstrate_numeric_conversion() -> None:
    section("4. NUMERIC TYPE CONVERSION")

    # int() performs explicit conversion.
    print("int(12.9):", int(12.9))
    print("int(-12.9):", int(-12.9))

    # int(float) truncates toward zero. It does NOT round.
    print("int(12.99):", int(12.99))
    print("int(-12.99):", int(-12.99))

    # round() follows Python's rounding behavior, including ties-to-even
    # for ordinary binary floating-point cases.
    print("round(12.99):", round(12.99))
    print("round(12.5):", round(12.5))
    print("round(13.5):", round(13.5))

    # float() accepts numeric values and numeric strings.
    print("float(10):", float(10))
    print('float("10.25"):', float("10.25"))

    # complex() can create complex numbers from compatible values.
    print("complex(5):", complex(5))
    print('complex("3+4j"):', complex("3+4j"))

    # bool() uses truth-value testing rather than numeric parsing.
    print("bool(0):", bool(0))
    print("bool(1):", bool(1))
    print("bool(-5):", bool(-5))
    print('bool(""):', bool(""))
    print('bool("False"):', bool("False"))


# =============================================================================
# 5. STRING TO NUMBER CONVERSION
# =============================================================================

def demonstrate_string_parsing() -> None:
    section("5. STRING TO NUMBER CONVERSION")

    integer_strings = [
        "42",
        "-42",
        "+42",
        " 42 ",
        "0",
        "0b1010",
        "0o52",
        "0x2A",
    ]

    for text in integer_strings:
        try:
            if text.strip().lower().startswith(("0b", "0o", "0x")):
                value = int(text, 0)
            else:
                value = int(text)
            print(f"int({text!r}) -> {value}")
        except ValueError as error:
            print(f"int({text!r}) -> ValueError: {error}")

    floating_strings = [
        "3.14",
        "-0.25",
        "1e3",
        "  99.5  ",
        "nan",
        "inf",
        "-inf",
    ]

    for text in floating_strings:
        try:
            value = float(text)
            print(f"float({text!r}) -> {value!r}")
        except ValueError as error:
            print(f"float({text!r}) -> ValueError: {error}")


# =============================================================================
# 6. BASE CONVERSION
# =============================================================================

def demonstrate_integer_bases() -> None:
    section("6. INTEGER BASE CONVERSION")

    number = 42

    print("Decimal:", number)
    print("Binary:", bin(number))
    print("Octal:", oct(number))
    print("Hexadecimal:", hex(number))

    print('\nint("101010", 2):', int("101010", 2))
    print('int("52", 8):', int("52", 8))
    print('int("2A", 16):', int("2A", 16))

    # int(text, base) accepts bases from 2 through 36.
    print('int("Z", 36):', int("Z", 36))

    # The base argument controls interpretation of the string.
    # int("10", 2) is two in decimal, not ten.
    print('int("10", 2):', int("10", 2))
    print('int("10", 10):', int("10", 10))
    print('int("10", 16):', int("10", 16))


# =============================================================================
# 7. CHARACTER AND BYTE CONVERSION
# =============================================================================

def demonstrate_character_and_bytes_conversion() -> None:
    section("7. CHARACTER, STRING, BYTES, AND BYTEARRAY CONVERSION")

    # ord() converts one Unicode character to its code point.
    print("ord('A'):", ord("A"))
    print("ord('€'):", ord("€"))

    # chr() converts an integer Unicode code point to a character.
    print("chr(65):", chr(65))
    print("chr(8364):", chr(8364))

    text = "café"
    encoded = text.encode("utf-8")
    decoded = encoded.decode("utf-8")

    print("Original:", text)
    print("UTF-8 bytes:", encoded)
    print("Decoded:", decoded)

    mutable_bytes = bytearray(encoded)
    print("bytearray:", mutable_bytes)

    # bytes(integer) creates that many zero bytes.
    print("bytes(4):", bytes(4))

    # bytes(iterable_of_ints) converts integers in the range 0..255.
    print("bytes([65, 66, 67]):", bytes([65, 66, 67]))

    try:
        bytes([256])
    except ValueError as error:
        print("bytes([256]) -> ValueError:", error)


# =============================================================================
# 8. COLLECTION TYPE CONVERSION
# =============================================================================

def demonstrate_collection_conversion() -> None:
    section("8. COLLECTION TYPE CONVERSION")

    original = [1, 2, 2, 3, 1]

    print("Original list:", original)
    print("tuple(original):", tuple(original))
    print("set(original):", set(original))
    print("frozenset(original):", frozenset(original))

    # Converting to a set removes duplicates and loses sequence ordering
    # semantics. Do not use set() merely to "change the type" when ordering
    # or multiplicity is meaningful.
    print("list(set(original)):", list(set(original)))

    mapping = [("name", "Ada"), ("age", 36)]
    print("dict(mapping):", dict(mapping))

    # dict keys must be hashable.
    try:
        dict([[["unhashable"], "value"]])
    except TypeError as error:
        print("Invalid dict construction -> TypeError:", error)

    # Strings are iterable, so list("abc") produces characters.
    print('list("abc"):', list("abc"))
    print('tuple("abc"):', tuple("abc"))
    print('set("banana"):', set("banana"))


# =============================================================================
# 9. CONVERSION VERSUS CASTING
# =============================================================================

def demonstrate_conversion_vs_casting() -> None:
    section("9. TYPE CONVERSION VERSUS TYPE CASTING")

    # Runtime conversion actually creates or returns a value of another type.
    text_number = "123"
    integer_number = int(text_number)

    print("text_number:", text_number, type(text_number).__name__)
    print("integer_number:", integer_number, type(integer_number).__name__)

    # typing.cast() does not convert the runtime object.
    # It only tells static type checkers to treat the expression as another
    # type. At runtime, the original object remains unchanged.
    alleged_integer = cast(int, text_number)

    print("cast(int, '123'):", alleged_integer)
    print("Runtime type after cast:", type(alleged_integer).__name__)

    # This is a central distinction:
    # int("123") -> runtime conversion
    # cast(int, "123") -> static typing assertion with no conversion


# =============================================================================
# 10. IMPLICIT COERCION AND OPERATOR BEHAVIOR
# =============================================================================

def demonstrate_numeric_operations() -> None:
    section("10. NUMERIC COERCION AND OPERATOR BEHAVIOR")

    print("1 + 2:", 1 + 2)
    print("1 + 2.5:", 1 + 2.5)
    print("5 / 2:", 5 / 2)
    print("5 // 2:", 5 // 2)
    print("5 ** 2:", 5 ** 2)

    # Python does not generally coerce arbitrary unrelated types.
    # For example, strings do not become numbers automatically for +.
    try:
        print("10 + '5':", 10 + "5")
    except TypeError as error:
        print("10 + '5' -> TypeError:", error)

    # + has a different meaning for strings.
    print('"10" + "5":', "10" + "5")

    # Multiplication by an integer repeats sequences.
    print('"ab" * 3:', "ab" * 3)
    print("[1, 2] * 2:", [1, 2] * 2)


# =============================================================================
# 11. TRUTH-VALUE TESTING
# =============================================================================

def demonstrate_truthiness() -> None:
    section("11. TRUTH-VALUE TESTING")

    values = [
        False,
        True,
        0,
        1,
        0.0,
        "",
        "False",
        [],
        [0],
        (),
        (0,),
        {},
        {"x": 0},
        None,
    ]

    for value in values:
        print(f"{value!r:<15} -> bool={bool(value)}")

    # A non-empty string is truthy even when it spells "False".
    # This is why bool(user_input) is not a safe parser for textual booleans.


# =============================================================================
# 12. SAFE BOOLEAN PARSING
# =============================================================================

TRUE_TEXT = {"true", "t", "yes", "y", "1", "on"}
FALSE_TEXT = {"false", "f", "no", "n", "0", "off"}


def parse_bool(text: str) -> bool:
    """
    Parse common textual boolean representations.

    Raises:
        TypeError: if the input is not a string.
        ValueError: if the text is not recognized.
    """
    if not isinstance(text, str):
        raise TypeError("parse_bool() expects a string")

    normalized = text.strip().lower()

    if normalized in TRUE_TEXT:
        return True

    if normalized in FALSE_TEXT:
        return False

    raise ValueError(f"Unrecognized boolean value: {text!r}")


def demonstrate_boolean_parsing() -> None:
    section("13. ROBUST BOOLEAN STRING PARSING")

    samples = ["true", "FALSE", " yes ", "0", "on", "maybe", ""]

    for sample in samples:
        try:
            print(f"parse_bool({sample!r}) -> {parse_bool(sample)}")
        except (TypeError, ValueError) as error:
            print(f"parse_bool({sample!r}) -> {type(error).__name__}: {error}")


# =============================================================================
# 13. EXCEPTIONS DURING CONVERSION
# =============================================================================

def demonstrate_conversion_errors() -> None:
    section("14. CONVERSION ERRORS")

    invalid_conversions = [
        ("int('hello')", lambda: int("hello")),
        ("float('hello')", lambda: float("hello")),
        ("int(3.14, 10)", lambda: int(3.14, 10)),
        ("chr(-1)", lambda: chr(-1)),
        ("bytes([300])", lambda: bytes([300])),
    ]

    for description, operation in invalid_conversions:
        try:
            result = operation()
            print(description, "->", result)
        except Exception as error:
            print(
                description,
                "->",
                type(error).__name__,
                ":",
                error,
            )


# =============================================================================
# 14. VALIDATION BEFORE CONVERSION
# =============================================================================

def convert_age(text: str) -> int:
    """
    Convert an age string into an integer while applying domain validation.

    Conversion and validation are different:
    - int("200") succeeds syntactically.
    - 200 may still be invalid for the application's domain.
    """
    if not isinstance(text, str):
        raise TypeError("Age must be supplied as text")

    normalized = text.strip()

    if not normalized:
        raise ValueError("Age cannot be empty")

    try:
        age = int(normalized)
    except ValueError as error:
        raise ValueError("Age must contain a valid integer") from error

    if not 0 <= age <= 150:
        raise ValueError("Age must be between 0 and 150")

    return age


def demonstrate_validation() -> None:
    section("15. VALIDATION AFTER TYPE CONVERSION")

    samples = ["33", " 42 ", "", "abc", "-5", "200"]

    for sample in samples:
        try:
            print(f"convert_age({sample!r}) -> {convert_age(sample)}")
        except (TypeError, ValueError) as error:
            print(f"convert_age({sample!r}) -> {type(error).__name__}: {error}")


# =============================================================================
# 15. USER INPUT IS ALWAYS TEXT
# =============================================================================

def demonstrate_input_concept() -> None:
    section("16. INPUT AND TYPE CONVERSION")

    # input() always returns str when it succeeds.
    # Interactive input is not used here so the script remains non-interactive.
    simulated_input = "25"

    print("Simulated input:", simulated_input)
    print("Runtime type:", type(simulated_input).__name__)
    print("Converted age:", int(simulated_input))
    print("Converted type:", type(int(simulated_input)).__name__)

    # Common mistake:
    # age = input("Age: ")
    # if age > 18:
    #     ...
    #
    # This fails because age is a string.
    #
    # Correct:
    # age = int(input("Age: "))


# =============================================================================
# 16. FLOATING-POINT CONVERSION AND PRECISION
# =============================================================================

def demonstrate_float_precision() -> None:
    section("17. FLOAT CONVERSION AND PRECISION")

    print("float('0.1'):", float("0.1"))
    print("0.1 + 0.2:", 0.1 + 0.2)
    print("0.1 + 0.2 == 0.3:", 0.1 + 0.2 == 0.3)

    # Binary floating point cannot represent many decimal fractions exactly.
    # Decimal is preferable when exact decimal arithmetic is required.
    decimal_sum = Decimal("0.1") + Decimal("0.2")

    print("Decimal('0.1') + Decimal('0.2'):", decimal_sum)
    print(
        "Decimal('0.1') + Decimal('0.2') == Decimal('0.3'):",
        decimal_sum == Decimal("0.3"),
    )

    # Constructing Decimal from a float preserves the float's existing
    # approximation, while constructing from a string represents the intended
    # decimal value exactly.
    print("Decimal(0.1):", Decimal(0.1))
    print("Decimal('0.1'):", Decimal("0.1"))


# =============================================================================
# 17. ROUNDING, FLOOR, CEILING, TRUNCATION
# =============================================================================

def demonstrate_rounding() -> None:
    section("18. ROUNDING, FLOOR, CEILING, AND TRUNCATION")

    values = [3.7, 3.2, -3.2, -3.7]

    for value in values:
        print(
            f"{value:>5}: "
            f"int={int(value):>3}, "
            f"trunc={math.trunc(value):>3}, "
            f"floor={math.floor(value):>3}, "
            f"ceil={math.ceil(value):>3}, "
            f"round={round(value):>3}"
        )

    print("round(2.675, 2):", round(2.675, 2))

    # The result illustrates why decimal representation and binary
    # floating-point representation must not be treated as interchangeable.


# =============================================================================
# 18. DECIMAL AND FRACTION CONVERSIONS
# =============================================================================

def demonstrate_decimal_and_fraction() -> None:
    section("19. DECIMAL AND FRACTION CONVERSION")

    decimal_value = Decimal("10.50")
    float_value = float(decimal_value)
    int_value = int(decimal_value)

    print("Decimal:", decimal_value)
    print("float(Decimal):", float_value)
    print("int(Decimal):", int_value)

    fraction = Fraction(3, 4)

    print("Fraction:", fraction)
    print("float(Fraction):", float(fraction))
    print("int(Fraction):", int(fraction))
    print("Fraction(0.75):", Fraction(0.75))
    print("Fraction('0.75'):", Fraction("0.75"))

    # Fraction(0.75) captures the exact binary floating-point value of 0.75,
    # which happens to be exactly representable. Other decimal fractions may
    # expose floating-point approximation when converted this way.
    print("Fraction(0.1):", Fraction(0.1))


# =============================================================================
# 19. ENUMERATION TYPES
# =============================================================================

from enum import Enum, IntEnum


class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    CLOSED = "closed"


class NumericStatus(IntEnum):
    PENDING = 1
    ACTIVE = 2
    CLOSED = 3


def demonstrate_enums() -> None:
    section("20. ENUMS AND TYPE-SAFE CATEGORICAL VALUES")

    status = Status.ACTIVE

    print("status:", status)
    print("status.name:", status.name)
    print("status.value:", status.value)
    print("Status('active'):", Status("active"))

    print("NumericStatus.ACTIVE == 2:", NumericStatus.ACTIVE == 2)
    print("isinstance(NumericStatus.ACTIVE, int):",
          isinstance(NumericStatus.ACTIVE, int))

    # Enum and IntEnum have different semantics. IntEnum participates in
    # integer operations and comparisons, which can be useful but may reduce
    # strict separation from ordinary integers.


# =============================================================================
# 20. CUSTOM CONVERSION WITH __int__, __float__, __index__
# =============================================================================

class Measurement:
    """A simple object demonstrating conversion protocols."""

    def __init__(self, value: float) -> None:
        self.value = value

    def __int__(self) -> int:
        # int(obj) calls __int__ when available.
        return int(self.value)

    def __float__(self) -> float:
        # float(obj) calls __float__ when available.
        return float(self.value)

    def __index__(self) -> int:
        # __index__ means the object can represent an exact integer index.
        # Python uses this protocol for operations requiring an integer index,
        # such as sequence indexing and some binary/bitwise operations.
        if not self.value.is_integer():
            raise TypeError("Measurement is not an exact integer")
        return int(self.value)


def demonstrate_custom_conversion_protocols() -> None:
    section("21. CUSTOM CONVERSION PROTOCOLS")

    measurement = Measurement(12.8)

    print("int(measurement):", int(measurement))
    print("float(measurement):", float(measurement))

    exact_measurement = Measurement(3.0)

    print("hex(exact_measurement):", hex(exact_measurement))
    print("[10, 20, 30, 40][exact_measurement]:",
          [10, 20, 30, 40][exact_measurement])

    try:
        print("[10, 20, 30][measurement]:",
              [10, 20, 30][measurement])
    except TypeError as error:
        print("Non-integral __index__ usage -> TypeError:", error)


# =============================================================================
# 21. __bool__ AND TRUTH-VALUE PROTOCOL
# =============================================================================

class Temperature:
    """Demonstrates custom truth-value behavior."""

    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    def __bool__(self) -> bool:
        # A custom type can define what "truthy" means.
        return self.celsius > 0


def demonstrate_bool_protocol() -> None:
    section("22. CUSTOM BOOLEAN CONVERSION")

    temperatures = [Temperature(-5), Temperature(0), Temperature(20)]

    for temperature in temperatures:
        print(
            f"{temperature.celsius:>3}°C -> "
            f"bool={bool(temperature)}"
        )


# =============================================================================
# 22. TYPE HINTS
# =============================================================================

def add_numbers(left: int, right: int) -> int:
    """A type-annotated function."""
    return left + right


def format_name(name: str, age: int) -> str:
    """Return a formatted description using annotated parameters."""
    return f"{name} is {age} years old."


def demonstrate_type_hints() -> None:
    section("23. TYPE HINTS")

    print("add_numbers(2, 3):", add_numbers(2, 3))
    print("format_name('Ada', 36):", format_name("Ada", 36))

    print("Annotations for add_numbers:")
    print(get_type_hints(add_numbers))

    # Type hints normally do not enforce runtime types.
    #
    # The following is accepted by Python at runtime because annotations are
    # metadata unless explicit runtime validation is added:
    #
    # add_numbers("2", "3")
    #
    # It would fail inside the function with a TypeError because string + string
    # is valid and would actually produce "23". This illustrates why type hints
    # and runtime validation solve different problems.

    print("add_numbers('2', '3'):", add_numbers("2", "3"))


# =============================================================================
# 23. OPTIONAL AND UNION TYPES
# =============================================================================

def parse_optional_integer(value: Optional[str]) -> Optional[int]:
    """Convert a string to int while allowing None."""
    if value is None:
        return None
    return int(value)


def parse_identifier(identifier: int | str) -> int:
    """
    Accept an integer directly or parse an integer string.

    This is a Python 3.10+ union annotation.
    """
    if isinstance(identifier, int):
        return identifier

    if isinstance(identifier, str):
        return int(identifier.strip())

    raise TypeError("identifier must be int or str")


def demonstrate_union_types() -> None:
    section("24. OPTIONAL AND UNION TYPES")

    print("parse_optional_integer(None):",
          parse_optional_integer(None))
    print("parse_optional_integer('123'):",
          parse_optional_integer("123"))

    print("parse_identifier(123):", parse_identifier(123))
    print("parse_identifier('123'):", parse_identifier("123"))

    try:
        parse_identifier(12.5)
    except TypeError as error:
        print("parse_identifier(12.5) -> TypeError:", error)


# =============================================================================
# 24. TYPE CHECKING WITH ANY
# =============================================================================

def unsafe_sum(value: Any) -> Any:
    """
    Any disables useful static checking for the value.

    This function is intentionally permissive to demonstrate the trade-off.
    """
    return value + 10


def safe_sum(value: object) -> int:
    """
    object means "some object", so runtime narrowing is required.

    Unlike Any, object does not tell the type checker that arbitrary operations
    are valid.
    """
    if not isinstance(value, int):
        raise TypeError("value must be an integer")
    return value + 10


def demonstrate_any_and_object() -> None:
    section("25. ANY VERSUS OBJECT")

    print("unsafe_sum(5):", unsafe_sum(5))
    print("safe_sum(5):", safe_sum(5))

    try:
        print("safe_sum('5'):", safe_sum("5"))
    except TypeError as error:
        print("safe_sum('5') -> TypeError:", error)

    # Any is useful at dynamic boundaries but should not spread unnecessarily
    # through an application's internal type model.


# =============================================================================
# 25. TYPE NARROWING
# =============================================================================

def describe_value(value: int | str | None) -> str:
    """
    Runtime checks narrow a union into a more specific branch.
    """
    if value is None:
        return "value is None"

    if isinstance(value, int):
        return f"integer: {value}"

    # At this point the remaining union member is str.
    return f"string: {value}"


def demonstrate_type_narrowing() -> None:
    section("26. TYPE NARROWING")

    for value in [None, 10, "Python"]:
        print(describe_value(value))


# =============================================================================
# 26. TYPE ALIASES
# =============================================================================

UserIdentifier = int | str
NumberLike = int | float | Decimal


def normalize_number(value: NumberLike) -> Decimal:
    """
    Convert supported numeric inputs into Decimal.

    Strings are deliberately excluded from this function's type contract.
    """
    if isinstance(value, Decimal):
        return value

    if isinstance(value, int):
        return Decimal(value)

    if isinstance(value, float):
        # Converting float directly preserves its binary approximation.
        # In applications needing decimal semantics, receiving text and then
        # constructing Decimal from the text is usually preferable.
        return Decimal(str(value))

    raise TypeError(f"Unsupported number type: {type(value).__name__}")


def demonstrate_type_aliases() -> None:
    section("27. TYPE ALIASES")

    values: list[NumberLike] = [10, 2.5, Decimal("3.75")]

    for value in values:
        print(
            repr(value),
            "->",
            normalize_number(value),
            type(normalize_number(value)).__name__,
        )


# =============================================================================
# 27. GENERIC TYPES
# =============================================================================

T = TypeVar("T")


class Box(Generic[T]):
    """A simple generic container."""

    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value


def demonstrate_generics() -> None:
    section("28. GENERIC TYPES")

    integer_box = Box(100)
    string_box = Box("Python")

    print("integer_box.get():", integer_box.get())
    print("string_box.get():", string_box.get())

    # Generic annotations describe relationships between inputs and outputs.
    # Runtime objects generally do not retain full generic parameter information
    # in a way that isinstance() can directly enforce.


# =============================================================================
# 28. RUNTIME CHECKABLE PROTOCOL
# =============================================================================

@runtime_checkable
class SupportsLength(Protocol):
    def __len__(self) -> int:
        ...


def demonstrate_protocols() -> None:
    section("29. PROTOCOLS AND STRUCTURAL TYPE CHECKING")

    values = ["abc", [1, 2, 3], {"a": 1}, 42]

    for value in values:
        print(
            repr(value),
            "supports __len__:",
            isinstance(value, SupportsLength),
        )

    # A protocol describes required behavior rather than requiring inheritance.
    # @runtime_checkable allows certain isinstance() checks at runtime.
    #
    # Runtime protocol checks are useful for simple structural checks, but static
    # type checkers provide much richer protocol analysis.


# =============================================================================
# 29. CLASS CHECKING
# =============================================================================

class Vehicle:
    pass


class Car(Vehicle):
    pass


class Motorcycle(Vehicle):
    pass


def demonstrate_class_hierarchy() -> None:
    section("30. TYPE CHECKING CLASS HIERARCHIES")

    car = Car()

    print("type(car) is Car:", type(car) is Car)
    print("isinstance(car, Car):", isinstance(car, Car))
    print("isinstance(car, Vehicle):", isinstance(car, Vehicle))
    print("issubclass(Car, Vehicle):", issubclass(Car, Vehicle))
    print("issubclass(Motorcycle, Vehicle):", issubclass(Motorcycle, Vehicle))

    try:
        print("issubclass(car, Vehicle):", issubclass(car, Vehicle))
    except TypeError as error:
        print("issubclass(instance, class) -> TypeError:", error)


# =============================================================================
# 30. CHECKING MULTIPLE TYPES
# =============================================================================

def is_number(value: object) -> bool:
    """
    Demonstrate a tuple of classes in isinstance().

    bool is technically an int subclass, so this function treats bool as numeric.
    """
    return isinstance(value, (int, float, complex, Decimal, Fraction))


def is_non_boolean_integer(value: object) -> bool:
    """
    Treat bool separately when business logic requires actual integers.
    """
    return isinstance(value, int) and not isinstance(value, bool)


def demonstrate_multiple_type_checks() -> None:
    section("31. MULTIPLE TYPES AND BOOL AS AN INT SUBCLASS")

    values = [True, False, 0, 1, 2.5, 2 + 0j, Decimal("3")]

    for value in values:
        print(
            f"{value!r:<12} "
            f"is_number={is_number(value)!s:<5} "
            f"is_non_boolean_integer={is_non_boolean_integer(value)}"
        )


# =============================================================================
# 31. CONVERSION OF NUMERIC BOOLEANS
# =============================================================================

def demonstrate_bool_integer_relationship() -> None:
    section("32. BOOL AND INTEGER CONVERSION")

    print("int(True):", int(True))
    print("int(False):", int(False))
    print("bool(0):", bool(0))
    print("bool(1):", bool(1))
    print("True + True:", True + True)
    print("True == 1:", True == 1)

    # This relationship is legitimate Python behavior but can cause subtle bugs
    # in validation code if bool should not count as an integer.


# =============================================================================
# 32. CONVERSION OF DICTIONARIES AND ITERABLES
# =============================================================================

def demonstrate_iterable_requirements() -> None:
    section("33. ITERABLE-BASED CONVERSION")

    # list(), tuple(), set(), and frozenset() consume iterables.
    generator = (number * 2 for number in range(4))

    print("list(generator):", list(generator))

    # The generator is exhausted after consumption.
    print("list(generator) again:", list(generator))

    # Conversion from a generator can therefore have side effects in the sense
    # that consuming it changes what remains available.


# =============================================================================
# 33. SHALLOW CONVERSION AND NESTED DATA
# =============================================================================

def demonstrate_shallow_conversion() -> None:
    section("34. SHALLOW CONVERSION")

    nested_list = [[1, 2], [3, 4]]
    tuple_copy = tuple(nested_list)

    print("nested_list:", nested_list)
    print("tuple_copy:", tuple_copy)

    # tuple(nested_list) changes the outer container only.
    # The inner lists are the same objects.
    print("tuple_copy[0] is nested_list[0]:",
          tuple_copy[0] is nested_list[0])

    nested_list[0].append(99)

    print("After mutating nested_list[0]:")
    print("nested_list:", nested_list)
    print("tuple_copy:", tuple_copy)


# =============================================================================
# 34. DEEP COPY VERSUS CONVERSION
# =============================================================================

from copy import copy, deepcopy


def demonstrate_copying() -> None:
    section("35. CONVERSION VERSUS COPYING")

    original = [[1, 2], [3, 4]]
    shallow = copy(original)
    deep = deepcopy(original)

    original[0].append(99)

    print("original:", original)
    print("shallow copy:", shallow)
    print("deep copy:", deep)

    # Conversion, copying, and serialization are distinct operations.
    # tuple(list_value) changes the outer container type.
    # copy() duplicates the container structure shallowly.
    # deepcopy() recursively duplicates supported nested objects.


# =============================================================================
# 35. DATACLASS TYPE CHECKING
# =============================================================================

@dataclass
class Person:
    name: str
    age: int


def create_person(data: dict[str, object]) -> Person:
    """
    Validate and convert untrusted dictionary data into a typed object.

    This illustrates a production-relevant pattern: do not assume that a type
    annotation automatically validates external data.
    """
    name = data.get("name")
    age = data.get("age")

    if not isinstance(name, str):
        raise TypeError("name must be a string")

    if isinstance(age, bool) or not isinstance(age, int):
        raise TypeError("age must be a non-boolean integer")

    if age < 0:
        raise ValueError("age cannot be negative")

    return Person(name=name, age=age)


def demonstrate_dataclass_validation() -> None:
    section("36. VALIDATING EXTERNAL DATA INTO A DATACLASS")

    valid_data: dict[str, object] = {
        "name": "Ada",
        "age": 36,
    }

    print("create_person(valid_data):", create_person(valid_data))

    invalid_data: dict[str, object] = {
        "name": "Ada",
        "age": "36",
    }

    try:
        create_person(invalid_data)
    except (TypeError, ValueError) as error:
        print(
            "create_person(invalid_data) ->",
            type(error).__name__,
            ":",
            error,
        )


# =============================================================================
# 36. STRUCTURAL TYPE CHECKING WITH ATTRIBUTES
# =============================================================================

@runtime_checkable
class Named(Protocol):
    name: str


@dataclass
class Employee:
    name: str
    employee_id: int


@dataclass
class Product:
    name: str
    price: Decimal


def demonstrate_structural_typing() -> None:
    section("37. STRUCTURAL TYPING")

    objects = [
        Employee("Ada", 101),
        Product("Keyboard", Decimal("49.99")),
        {"name": "Dictionary object"},
    ]

    for value in objects:
        # Runtime protocol checks for data attributes have limitations and should
        # not be confused with complete static structural validation.
        try:
            result = isinstance(value, Named)
        except TypeError:
            result = False

        print(repr(value), "is Named:", result)


# =============================================================================
# 37. OVERLOADS
# =============================================================================

@overload
def normalize_identifier(value: int) -> int:
    ...


@overload
def normalize_identifier(value: str) -> int:
    ...


def normalize_identifier(value: int | str) -> int:
    """
    Overloads describe multiple accepted static call signatures.

    Runtime implementation still needs ordinary validation.
    """
    if isinstance(value, bool):
        raise TypeError("bool is not a valid identifier")

    if isinstance(value, int):
        return value

    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            raise ValueError("identifier cannot be empty")
        return int(normalized)

    raise TypeError("identifier must be int or str")


def demonstrate_overloads() -> None:
    section("38. OVERLOADS")

    print("normalize_identifier(42):", normalize_identifier(42))
    print("normalize_identifier('42'):", normalize_identifier("42"))

    try:
        normalize_identifier(True)
    except (TypeError, ValueError) as error:
        print("normalize_identifier(True) ->", type(error).__name__, ":", error)


# =============================================================================
# 38. TYPE OBJECTS AND META-TYPES
# =============================================================================

def demonstrate_type_objects() -> None:
    section("39. TYPE OBJECTS AND METATYPES")

    print("type(10):", type(10))
    print("type(int):", type(int))
    print("type(str):", type(str))
    print("type(type):", type(type))

    # Classes are objects too, and their type is normally a metaclass.
    print("isinstance(int, type):", isinstance(int, type))
    print("isinstance(str, type):", isinstance(str, type))
    print("isinstance(10, type):", isinstance(10, type))


# =============================================================================
# 39. TYPE-BASED DISPATCH
# =============================================================================

def convert_for_display(value: object) -> str:
    """
    Use explicit type narrowing to select behavior.
    """
    if isinstance(value, bool):
        return f"boolean:{value}"

    if isinstance(value, int):
        return f"integer:{value}"

    if isinstance(value, float):
        return f"float:{value:.2f}"

    if isinstance(value, Decimal):
        return f"decimal:{value}"

    if isinstance(value, str):
        return f"string:{value}"

    if value is None:
        return "none"

    return f"other:{type(value).__name__}"


def demonstrate_type_dispatch() -> None:
    section("40. TYPE-BASED DISPATCH")

    values = [True, 10, 3.14159, Decimal("9.99"), "Python", None, [1, 2]]

    for value in values:
        print(convert_for_display(value))


# =============================================================================
# 40. CONVERSION WITH DEFAULTS
# =============================================================================

def to_int_or_default(value: object, default: int = 0) -> int:
    """
    Convert a value when possible; otherwise return a controlled default.

    The function intentionally distinguishes None from invalid text.
    """
    if value is None:
        return default

    if isinstance(value, bool):
        raise TypeError("Boolean is not accepted as an integer")

    if isinstance(value, int):
        return value

    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return default

    raise TypeError(f"Unsupported value type: {type(value).__name__}")


def demonstrate_default_conversion() -> None:
    section("41. CONVERSION WITH DEFAULT VALUES")

    samples: list[object] = ["123", "abc", None, 42]

    for sample in samples:
        try:
            print(
                repr(sample),
                "->",
                to_int_or_default(sample, default=-1),
            )
        except TypeError as error:
            print(repr(sample), "-> TypeError:", error)


# =============================================================================
# 41. VALIDATION PIPELINE
# =============================================================================

@dataclass(frozen=True)
class Order:
    quantity: int
    unit_price: Decimal


def parse_order(quantity_text: str, price_text: str) -> Order:
    """
    A multi-stage conversion and validation pipeline.

    Stage 1: type validation
    Stage 2: syntax conversion
    Stage 3: domain validation
    Stage 4: construction of a trusted internal representation
    """
    if not isinstance(quantity_text, str):
        raise TypeError("quantity_text must be a string")

    if not isinstance(price_text, str):
        raise TypeError("price_text must be a string")

    try:
        quantity = int(quantity_text.strip())
    except ValueError as error:
        raise ValueError("quantity must be an integer") from error

    try:
        unit_price = Decimal(price_text.strip())
    except Exception as error:
        raise ValueError("unit price must be a valid decimal") from error

    if quantity <= 0:
        raise ValueError("quantity must be positive")

    if unit_price < 0:
        raise ValueError("unit price cannot be negative")

    return Order(quantity=quantity, unit_price=unit_price)


def demonstrate_validation_pipeline() -> None:
    section("42. CONVERSION AND VALIDATION PIPELINE")

    samples = [
        ("3", "19.99"),
        ("0", "19.99"),
        ("three", "19.99"),
        ("3", "-2.00"),
        ("3", "not-a-price"),
    ]

    for quantity, price in samples:
        try:
            order = parse_order(quantity, price)
            print(f"{quantity!r}, {price!r} -> {order}")
        except (TypeError, ValueError) as error:
            print(
                f"{quantity!r}, {price!r} -> "
                f"{type(error).__name__}: {error}"
            )


# =============================================================================
# 42. EXCEPTIONS AND CHAINING
# =============================================================================

def parse_percentage(text: str) -> Decimal:
    """Convert a textual percentage into a validated Decimal."""
    try:
        value = Decimal(text.strip())
    except Exception as error:
        raise ValueError(f"Invalid percentage: {text!r}") from error

    if not value.is_finite():
        raise ValueError("Percentage must be finite")

    if not Decimal("0") <= value <= Decimal("100"):
        raise ValueError("Percentage must be between 0 and 100")

    return value


def demonstrate_exception_chaining() -> None:
    section("43. EXCEPTION CHAINING")

    for sample in ["25.5", "abc", "150"]:
        try:
            print(sample, "->", parse_percentage(sample))
        except ValueError as error:
            print(sample, "-> ValueError:", error)


# =============================================================================
# 43. NAN AND INFINITY
# =============================================================================

def demonstrate_special_float_values() -> None:
    section("44. NaN AND INFINITY")

    values = [
        float("nan"),
        float("inf"),
        float("-inf"),
    ]

    for value in values:
        print(
            f"value={value!r}, "
            f"isfinite={math.isfinite(value)}, "
            f"isnan={math.isnan(value)}, "
            f"isinf={math.isinf(value)}"
        )

    nan = float("nan")

    print("nan == nan:", nan == nan)
    print("nan != nan:", nan != nan)

    # Never rely on x == float("nan") to detect NaN.
    # Use math.isnan() or equivalent numeric-library facilities.


# =============================================================================
# 44. NONE AND TYPE CHECKING
# =============================================================================

def demonstrate_none() -> None:
    section("45. NONE AND OPTIONAL VALUES")

    value: Optional[int] = None

    print("value is None:", value is None)
    print("type(value):", type(value).__name__)
    print("isinstance(value, type(None)):", isinstance(value, type(None)))

    # "is None" is preferred to "== None" because None is a singleton sentinel
    # and identity expresses the intended semantic check.


# =============================================================================
# 45. TYPE CHECKING GENERIC COLLECTIONS AT RUNTIME
# =============================================================================

def all_integers(values: object) -> bool:
    """
    Validate that a value is a list whose elements are non-boolean integers.

    Python's isinstance() cannot directly express list[int] as a runtime class
    check, so the container and each element must be checked separately.
    """
    if not isinstance(values, list):
        return False

    return all(
        isinstance(value, int) and not isinstance(value, bool)
        for value in values
    )


def demonstrate_runtime_generic_validation() -> None:
    section("46. RUNTIME VALIDATION OF GENERIC COLLECTIONS")

    samples: list[object] = [
        [1, 2, 3],
        [1, True, 3],
        ["1", "2"],
        [],
        (1, 2, 3),
    ]

    for sample in samples:
        print(repr(sample), "->", all_integers(sample))


# =============================================================================
# 46. LIST[int] AND TYPE INTROSPECTION
# =============================================================================

def demonstrate_typing_introspection() -> None:
    section("47. TYPE ANNOTATION INTROSPECTION")

    annotation = list[int]

    print("annotation:", annotation)
    print("get_origin(annotation):", get_origin(annotation))
    print("get_args(annotation):", get_args(annotation))

    union_annotation = int | str

    print("union annotation:", union_annotation)
    print("union origin:", get_origin(union_annotation))
    print("union arguments:", get_args(union_annotation))

    # This introspection describes typing expressions. It is not equivalent to
    # validating arbitrary runtime data against every possible type annotation.


# =============================================================================
# 47. TYPE CHECKING FUNCTIONS
# =============================================================================

def validate_function_arguments(
    name: str,
    age: int,
    active: bool,
) -> None:
    """
    Manually enforce a runtime contract corresponding to annotations.
    """
    expected = {
        "name": str,
        "age": int,
        "active": bool,
    }

    values = {
        "name": name,
        "age": age,
        "active": active,
    }

    for field_name, expected_type in expected.items():
        value = values[field_name]

        if not isinstance(value, expected_type):
            raise TypeError(
                f"{field_name} must be {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )


def demonstrate_runtime_annotation_validation() -> None:
    section("48. MANUAL RUNTIME VALIDATION OF ANNOTATIONS")

    validate_function_arguments("Ada", 36, True)
    print("Valid arguments accepted.")

    try:
        validate_function_arguments("Ada", "36", True)  # type: ignore[arg-type]
    except TypeError as error:
        print("Invalid arguments -> TypeError:", error)


# =============================================================================
# 48. CONVERSION OF JSON-LIKE DATA
# =============================================================================

import json


def demonstrate_json_conversion() -> None:
    section("49. JSON AND PYTHON TYPE CONVERSION")

    data = {
        "name": "Ada",
        "age": 36,
        "active": True,
        "skills": ["math", "programming"],
        "metadata": None,
    }

    serialized = json.dumps(data)
    restored = json.loads(serialized)

    print("Python object:", data)
    print("JSON text:", serialized)
    print("Restored Python object:", restored)

    print("Top-level restored type:", type(restored).__name__)
    print("Restored age type:", type(restored["age"]).__name__)
    print("Restored active type:", type(restored["active"]).__name__)

    # JSON has a smaller type system than Python. Python-specific objects such
    # as Decimal, set, bytes, or custom classes need explicit serialization rules.


# =============================================================================
# 49. CUSTOM JSON SERIALIZATION
# =============================================================================

def json_default(value: object) -> object:
    """
    Convert selected Python-specific values into JSON-compatible values.
    """
    if isinstance(value, Decimal):
        # String preserves decimal representation and avoids silently losing
        # precision through float conversion.
        return str(value)

    if isinstance(value, set):
        return sorted(value)

    if isinstance(value, bytes):
        return value.decode("utf-8")

    raise TypeError(
        f"Object of type {type(value).__name__} is not JSON serializable"
    )


def demonstrate_custom_json_serialization() -> None:
    section("50. CUSTOM JSON CONVERSION")

    data = {
        "price": Decimal("19.99"),
        "tags": {"python", "types"},
        "payload": b"hello",
    }

    serialized = json.dumps(data, default=json_default)

    print("Original:", data)
    print("Serialized:", serialized)


# =============================================================================
# 50. CSV-LIKE STRING CONVERSION
# =============================================================================

def parse_integer_csv(text: str) -> list[int]:
    """
    Convert comma-separated integer text into a list of integers.

    Whitespace around each field is ignored.
    Empty fields are rejected rather than silently converted.
    """
    if not isinstance(text, str):
        raise TypeError("CSV input must be a string")

    parts = text.split(",")

    result: list[int] = []

    for part in parts:
        normalized = part.strip()

        if not normalized:
            raise ValueError("CSV contains an empty field")

        try:
            result.append(int(normalized))
        except ValueError as error:
            raise ValueError(
                f"Invalid integer field: {normalized!r}"
            ) from error

    return result


def demonstrate_csv_conversion() -> None:
    section("51. STRING LIST PARSING")

    for text in ["1,2,3", " 10, 20, 30 ", "1,,3", "1,two,3"]:
        try:
            print(text!r, "->", parse_integer_csv(text))
        except (TypeError, ValueError) as error:
            print(text!r, "->", type(error).__name__, ":", error)


# =============================================================================
# 51. DATE AND TIME CONVERSION
# =============================================================================

from datetime import date, datetime, time, timezone


def demonstrate_datetime_conversion() -> None:
    section("52. DATE AND TIME CONVERSION")

    date_text = "2026-09-08"
    parsed_date = date.fromisoformat(date_text)

    print("date.fromisoformat:", parsed_date)
    print("type:", type(parsed_date).__name__)

    datetime_text = "2026-09-08T11:30:00+05:30"
    parsed_datetime = datetime.fromisoformat(datetime_text)

    print("datetime.fromisoformat:", parsed_datetime)
    print("tzinfo:", parsed_datetime.tzinfo)

    current_date = date.today()
    print("date.today():", current_date)

    # datetime and date are distinct types. Explicit conversion should be used
    # when changing between representations.
    print("datetime.date():", parsed_datetime.date())
    print("datetime.time():", parsed_datetime.time())

    utc_datetime = parsed_datetime.astimezone(timezone.utc)
    print("Converted to UTC:", utc_datetime)


# =============================================================================
# 52. TYPE CONVERSION AND INHERITANCE
# =============================================================================

class Animal:
    def speak(self) -> str:
        return "sound"


class Dog(Animal):
    def speak(self) -> str:
        return "woof"


def demonstrate_subclass_conversion_concept() -> None:
    section("53. SUBTYPING IS NOT THE SAME AS CONVERSION")

    dog = Dog()

    print("type(dog):", type(dog).__name__)
    print("isinstance(dog, Dog):", isinstance(dog, Dog))
    print("isinstance(dog, Animal):", isinstance(dog, Animal))

    # A Dog object does not need to be converted into Animal to be usable where
    # Animal behavior is expected. This is polymorphism, not type conversion.
    animal: Animal = dog
    print("animal.speak():", animal.speak())


# =============================================================================
# 53. DUCK TYPING
# =============================================================================

class Printer:
    def write(self, text: str) -> None:
        print(f"Printer: {text}")


class Logger:
    def write(self, text: str) -> None:
        print(f"Logger: {text}")


def send_message(writer: object, message: str) -> None:
    """
    Demonstrate duck typing with explicit runtime capability checking.
    """
    write_method = getattr(writer, "write", None)

    if not callable(write_method):
        raise TypeError("writer must provide a callable write() method")

    write_method(message)


def demonstrate_duck_typing() -> None:
    section("54. DUCK TYPING AND TYPE CHECKING")

    send_message(Printer(), "hello")
    send_message(Logger(), "hello")

    try:
        send_message(object(), "hello")
    except TypeError as error:
        print("Invalid writer -> TypeError:", error)


# =============================================================================
# 54. TYPE CHECKING WITH ATTRIBUTES
# =============================================================================

def get_name(value: object) -> str:
    """
    Runtime-safe extraction of a string name attribute.
    """
    name = getattr(value, "name", None)

    if not isinstance(name, str):
        raise TypeError("Object must have a string 'name' attribute")

    return name


def demonstrate_getattr_validation() -> None:
    section("55. ATTRIBUTE TYPE VALIDATION")

    people = [
        Employee("Ada", 101),
        Product("Keyboard", Decimal("49.99")),
    ]

    for person in people:
        print("get_name:", get_name(person))


# =============================================================================
# 55. TYPE CONVERSION USING __new__ AND __init__
# =============================================================================

class PositiveInteger(int):
    """
    An int subclass that validates its value during construction.

    This illustrates that subclass construction can implement domain-specific
    validation while retaining integer behavior.
    """

    def __new__(cls, value: int | str) -> PositiveInteger:
        integer_value = int(value)

        if integer_value <= 0:
            raise ValueError("PositiveInteger must be greater than zero")

        return super().__new__(cls, integer_value)


def demonstrate_custom_numeric_type() -> None:
    section("56. CUSTOM NUMERIC TYPE")

    value = PositiveInteger("25")

    print("value:", value)
    print("type:", type(value).__name__)
    print("isinstance(value, int):", isinstance(value, int))
    print("value + 5:", value + 5)

    try:
        PositiveInteger("-1")
    except ValueError as error:
        print("PositiveInteger('-1') -> ValueError:", error)


# =============================================================================
# 56. CONVERSION OF CLASS INSTANCES
# =============================================================================

@dataclass
class Celsius:
    value: float

    def to_fahrenheit(self) -> float:
        return self.value * 9 / 5 + 32


@dataclass
class Fahrenheit:
    value: float

    def to_celsius(self) -> float:
        return (self.value - 32) * 5 / 9


def demonstrate_domain_conversion() -> None:
    section("57. DOMAIN-SPECIFIC CONVERSION")

    celsius = Celsius(100)
    fahrenheit = celsius.to_fahrenheit()

    print("100°C -> °F:", fahrenheit)

    converted_back = Fahrenheit(fahrenheit).to_celsius()

    print(f"{fahrenheit}°F -> °C:", converted_back)

    # Domain conversion is not the same thing as Python's generic type()
    # conversion. It changes the representation according to domain rules.


# =============================================================================
# 57. INTEGER OVERFLOW AND ARBITRARY PRECISION
# =============================================================================

def demonstrate_integer_precision() -> None:
    section("58. INTEGER PRECISION")

    huge = 10**100

    print("Huge integer digits:", len(str(huge)))
    print("Huge integer type:", type(huge).__name__)
    print("Huge integer squared digits:", len(str(huge * huge)))

    # Python integers have arbitrary precision, subject to available memory.
    # Converting a huge integer to float may overflow.
    try:
        print("float(10**1000):", float(10**1000))
    except OverflowError as error:
        print("float(10**1000) -> OverflowError:", error)


# =============================================================================
# 58. PERFORMANCE OF TYPE CHECKS AND CONVERSIONS
# =============================================================================

def demonstrate_performance() -> None:
    section("59. PERFORMANCE CONSIDERATIONS")

    type_check_time = timeit.timeit(
        "isinstance(value, int)",
        setup="value = 123",
        number=1_000_000,
    )

    exact_type_time = timeit.timeit(
        "type(value) is int",
        setup="value = 123",
        number=1_000_000,
    )

    conversion_time = timeit.timeit(
        "int('123')",
        number=1_000_000,
    )

    print(f"isinstance() for 1,000,000 checks: {type_check_time:.6f}s")
    print(f"type() is for 1,000,000 checks: {exact_type_time:.6f}s")
    print(f"int('123') for 1,000,000 conversions: {conversion_time:.6f}s")

    # These timings are machine-dependent. They are useful for understanding
    # relative cost, not for establishing universal benchmark numbers.
    #
    # In production, correctness and clarity usually matter more than optimizing
    # isolated type checks unless profiling identifies a real bottleneck.


# =============================================================================
# 59. PERFORMANCE: REPEATED CONVERSION
# =============================================================================

def inefficient_sum(text_values: Iterable[str]) -> int:
    """
    Convert repeatedly during the aggregation.
    """
    total = 0

    for text in text_values:
        total += int(text)

    return total


def efficient_sum(text_values: Iterable[str]) -> int:
    """
    The conversion is still performed once per element, but the generator
    expression makes the pipeline explicit and avoids an unnecessary list.
    """
    return sum(int(text) for text in text_values)


def demonstrate_conversion_performance_pattern() -> None:
    section("60. CONVERSION IN DATA PROCESSING")

    values = ["10", "20", "30", "40"]

    print("inefficient_sum:", inefficient_sum(values))
    print("efficient_sum:", efficient_sum(values))

    # The function names illustrate a conceptual comparison rather than a claim
    # that the first implementation is always materially slower. Measure actual
    # workloads before optimizing.


# =============================================================================
# 60. SECURITY: NEVER USE EVAL FOR CONVERSION
# =============================================================================

def demonstrate_safe_parsing() -> None:
    section("61. SECURITY: SAFE PARSING VERSUS eval()")

    user_supplied_text = "123"

    print("int(user_supplied_text):", int(user_supplied_text))

    # NEVER use eval(user_supplied_text) as a general-purpose converter.
    #
    # eval() executes Python expressions and therefore creates a code-execution
    # risk when its input is attacker-controlled.
    #
    # Use narrowly defined parsers such as int(), float(), Decimal(), JSON
    # parsing, or explicit validation instead.

    print("Safe conversion avoids executable interpretation.")


# =============================================================================
# 61. SECURITY: LIMIT RESOURCE-INTENSIVE CONVERSIONS
# =============================================================================

def demonstrate_resource_limits() -> None:
    section("62. SECURITY: RESOURCE CONSIDERATIONS")

    # Python versions can impose limits on conversion of extremely long decimal
    # strings to integers to reduce denial-of-service risks.
    normal_text = "9" * 20

    print("Normal integer conversion succeeds:", int(normal_text))

    # Application-level input limits remain valuable even when the interpreter
    # provides protections. Reject excessively large input before expensive
    # processing when domain constraints allow it.
    maximum_digits = 1000
    attacker_like_input = "9" * 500

    if len(attacker_like_input) > maximum_digits:
        raise ValueError("Input exceeds application limit")

    print("Input length accepted:", len(attacker_like_input))


# =============================================================================
# 62. COMMON MISTAKES
# =============================================================================

def demonstrate_common_mistakes() -> None:
    section("63. COMMON MISTAKES")

    subsection("Mistake 1: Comparing a string with an integer")
    user_age = "25"

    try:
        print(user_age > 18)
    except TypeError as error:
        print("TypeError:", error)

    print("Correct:", int(user_age) > 18)

    subsection("Mistake 2: Using bool() to parse text")
    print('bool("false"):', bool("false"))
    print("Correct parser:", parse_bool("false"))

    subsection("Mistake 3: Assuming annotations enforce runtime types")
    print("Annotations:", get_type_hints(add_numbers))
    print("Annotations are metadata unless runtime validation is implemented.")

    subsection("Mistake 4: Treating cast() as conversion")
    text = "123"
    fake_int = cast(int, text)

    print("cast(int, text):", fake_int)
    print("Runtime type:", type(fake_int).__name__)

    subsection("Mistake 5: Using type() when isinstance() is intended")
    class MyInt(int):
        pass

    value = MyInt(5)

    print("type(value) is int:", type(value) is int)
    print("isinstance(value, int):", isinstance(value, int))

    subsection("Mistake 6: Ignoring bool being an int subclass")
    print("isinstance(True, int):", isinstance(True, int))

    subsection("Mistake 7: Assuming int(float) rounds")
    print("int(9.99):", int(9.99))
    print("round(9.99):", round(9.99))


# =============================================================================
# 63. EDGE CASES
# =============================================================================

def demonstrate_edge_cases() -> None:
    section("64. IMPORTANT EDGE CASES")

    edge_cases = [
        ("int(True)", lambda: int(True)),
        ("int(False)", lambda: int(False)),
        ("float('nan')", lambda: float("nan")),
        ("float('inf')", lambda: float("inf")),
        ("int('  42  ')", lambda: int("  42  ")),
        ("int('+42')", lambda: int("+42")),
        ("int('-42')", lambda: int("-42")),
        ("float('1e3')", lambda: float("1e3")),
        ("bool('0')", lambda: bool("0")),
    ]

    for description, operation in edge_cases:
        try:
            result = operation()
            print(f"{description:<25} -> {result!r}")
        except Exception as error:
            print(
                f"{description:<25} -> "
                f"{type(error).__name__}: {error}"
            )


# =============================================================================
# 64. TYPE CHECKING BEFORE CONVERSION
# =============================================================================

def normalize_numeric_input(value: object) -> Decimal:
    """
    Normalize supported numeric input while avoiding surprising bool behavior.
    """
    if isinstance(value, bool):
        raise TypeError("Boolean values are not accepted as numeric input")

    if isinstance(value, Decimal):
        return value

    if isinstance(value, int):
        return Decimal(value)

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Float must be finite")
        return Decimal(str(value))

    if isinstance(value, str):
        text = value.strip()

        if not text:
            raise ValueError("Numeric text cannot be empty")

        try:
            result = Decimal(text)
        except Exception as error:
            raise ValueError("Invalid numeric text") from error

        if not result.is_finite():
            raise ValueError("Numeric text must represent a finite value")

        return result

    raise TypeError(
        f"Unsupported numeric input type: {type(value).__name__}"
    )


def demonstrate_normalization() -> None:
    section("65. ROBUST INPUT NORMALIZATION")

    samples: list[object] = [
        10,
        10.5,
        Decimal("10.50"),
        " 10.75 ",
        True,
        "abc",
        None,
    ]

    for sample in samples:
        try:
            print(repr(sample), "->", normalize_numeric_input(sample))
        except (TypeError, ValueError) as error:
            print(
                repr(sample),
                "->",
                type(error).__name__,
                ":",
                error,
            )


# =============================================================================
# 65. TYPE CONVERSION TABLE DEMONSTRATION
# =============================================================================

def demonstrate_conversion_matrix() -> None:
    section("66. CONVERSION MATRIX")

    source_values: list[object] = [
        42,
        3.14,
        True,
        "42",
    ]

    converters = [
        ("int", int),
        ("float", float),
        ("str", str),
        ("bool", bool),
    ]

    for value in source_values:
        print(f"\nSource: {value!r} ({type(value).__name__})")

        for converter_name, converter in converters:
            try:
                converted = converter(value)
                print(
                    f"  {converter_name:<5} -> "
                    f"{converted!r} ({type(converted).__name__})"
                )
            except (TypeError, ValueError) as error:
                print(
                    f"  {converter_name:<5} -> "
                    f"{type(error).__name__}: {error}"
                )


# =============================================================================
# 66. EXPLICIT VERSUS IMPLICIT DESIGN
# =============================================================================

def calculate_total(quantity: int, price: Decimal) -> Decimal:
    """
    Strongly typed internal calculation.

    External conversion should normally happen at system boundaries so the
    internal business logic works with trusted representations.
    """
    return Decimal(quantity) * price


def demonstrate_boundary_design() -> None:
    section("67. SYSTEM BOUNDARIES AND TYPE NORMALIZATION")

    raw_quantity = "3"
    raw_price = "19.99"

    quantity = int(raw_quantity)
    price = Decimal(raw_price)

    total = calculate_total(quantity, price)

    print("Raw quantity:", raw_quantity, type(raw_quantity).__name__)
    print("Normalized quantity:", quantity, type(quantity).__name__)
    print("Raw price:", raw_price, type(raw_price).__name__)
    print("Normalized price:", price, type(price).__name__)
    print("Total:", total, type(total).__name__)

    # A useful architecture is:
    #
    # external input -> validation -> conversion -> typed internal model
    # -> business logic -> typed output -> serialization


# =============================================================================
# 67. TESTING TYPE CONVERSION FUNCTIONS
# =============================================================================

def test_parse_bool() -> None:
    assert parse_bool("true") is True
    assert parse_bool("FALSE") is False
    assert parse_bool(" yes ") is True

    try:
        parse_bool("unknown")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for unknown boolean text")


def test_convert_age() -> None:
    assert convert_age("33") == 33
    assert convert_age(" 42 ") == 42

    for invalid in ["", "abc", "-1", "151"]:
        try:
            convert_age(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"Expected ValueError for {invalid!r}"
            )


def test_normalize_numeric_input() -> None:
    assert normalize_numeric_input("10") == Decimal("10")
    assert normalize_numeric_input(10) == Decimal("10")
    assert normalize_numeric_input(10.5) == Decimal("10.5")

    try:
        normalize_numeric_input(True)
    except TypeError:
        pass
    else:
        raise AssertionError("Boolean should be rejected")


def test_parse_order() -> None:
    order = parse_order("2", "9.99")

    assert order.quantity == 2
    assert order.unit_price == Decimal("9.99")


def run_tests() -> None:
    section("68. SELF-TESTS")

    tests = [
        test_parse_bool,
        test_convert_age,
        test_normalize_numeric_input,
        test_parse_order,
    ]

    passed = 0

    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except AssertionError as error:
            print(f"FAIL: {test.__name__}: {error}")

    print(f"\n{passed}/{len(tests)} tests passed.")


# =============================================================================
# 68. TYPE CHECKING DECISION GUIDE
# =============================================================================

def type_checking_decision_guide() -> None:
    section("69. TYPE CHECKING DECISION GUIDE")

    decisions = [
        (
            "Need exact runtime class identity",
            "type(value) is ExpectedType",
        ),
        (
            "Accept subclasses",
            "isinstance(value, ExpectedType)",
        ),
        (
            "Accept several runtime classes",
            "isinstance(value, (TypeA, TypeB))",
        ),
        (
            "Check whether a class inherits another",
            "issubclass(SubType, BaseType)",
        ),
        (
            "Need static type information",
            "Use type annotations and a static type checker",
        ),
        (
            "Need runtime validation of annotations",
            "Implement explicit validation or use a validation framework",
        ),
        (
            "Need actual runtime conversion",
            "Use int(), float(), str(), Decimal(), list(), etc.",
        ),
        (
            "Need only a static assertion",
            "typing.cast()",
        ),
        (
            "Need capability rather than inheritance",
            "Use duck typing or Protocol",
        ),
    ]

    for situation, technique in decisions:
        print(f"{situation}:")
        print(f"  {technique}")


# =============================================================================
# 69. COMPARISON OF COMMON OPERATIONS
# =============================================================================

def demonstrate_comparison() -> None:
    section("70. IMPORTANT DISTINCTIONS")

    comparisons = [
        (
            "type(value)",
            "Reports the exact runtime class object.",
        ),
        (
            "type(value) is T",
            "Requires exact runtime class T.",
        ),
        (
            "isinstance(value, T)",
            "Accepts T and compatible subclasses.",
        ),
        (
            "issubclass(C, T)",
            "Checks class inheritance.",
        ),
        (
            "int(value)",
            "Performs runtime integer conversion.",
        ),
        (
            "cast(int, value)",
            "Changes static interpretation only; does not convert.",
        ),
        (
            "bool(value)",
            "Performs truth-value testing, not textual boolean parsing.",
        ),
        (
            "str(value)",
            "Produces a string representation.",
        ),
        (
            "encode/decode",
            "Converts between text and byte representations.",
        ),
        (
            "list(value)",
            "Consumes an iterable into a list.",
        ),
        (
            "set(value)",
            "Consumes an iterable and removes duplicates.",
        ),
    ]

    for operation, meaning in comparisons:
        print(f"{operation:<25} -> {meaning}")


# =============================================================================
# 70. PRODUCTION BEST PRACTICES
# =============================================================================

def production_best_practices() -> None:
    section("71. PRODUCTION BEST PRACTICES")

    practices = [
        "Validate untrusted input at system boundaries.",
        "Convert external representations into stable internal types early.",
        "Do not assume annotations enforce runtime types.",
        "Use isinstance() when subclasses should be accepted.",
        "Use type(x) is T only when exact runtime type identity is required.",
        "Treat bool carefully because bool is a subclass of int.",
        "Do not use eval() to parse untrusted values.",
        "Use Decimal for exact decimal business calculations where appropriate.",
        "Use explicit boolean parsing for textual true/false values.",
        "Distinguish syntax errors from domain validation errors.",
        "Preserve useful exception causes with exception chaining.",
        "Keep conversion and business validation conceptually separate.",
        "Use static annotations to communicate contracts.",
        "Use runtime validation where data crosses a trust boundary.",
        "Avoid excessive use of Any because it weakens static guarantees.",
        "Use object plus runtime narrowing when a value is intentionally unknown.",
        "Measure performance before optimizing type checks or conversions.",
        "Apply input-size limits when conversion can consume substantial resources.",
        "Prefer explicit conversion over surprising implicit assumptions.",
        "Test valid values, invalid values, boundary values, and type edge cases.",
    ]

    for index, practice in enumerate(practices, start=1):
        print(f"{index:>2}. {practice}")


# =============================================================================
# 71. INTEGRATED REAL-WORLD EXAMPLE
# =============================================================================

@dataclass(frozen=True)
class CustomerRecord:
    customer_id: int
    name: str
    age: int
    active: bool
    balance: Decimal


def parse_customer_record(raw: dict[str, object]) -> CustomerRecord:
    """
    Convert a dictionary representing external data into a validated model.

    The function intentionally performs explicit type checks because dictionaries
    loaded from files, APIs, forms, databases, or message queues may contain
    unexpected runtime types.
    """
    customer_id = raw.get("customer_id")
    name = raw.get("name")
    age = raw.get("age")
    active = raw.get("active")
    balance = raw.get("balance")

    if isinstance(customer_id, bool) or not isinstance(customer_id, int):
        raise TypeError("customer_id must be a non-boolean integer")

    if not isinstance(name, str):
        raise TypeError("name must be a string")

    if isinstance(age, bool) or not isinstance(age, int):
        raise TypeError("age must be a non-boolean integer")

    if not isinstance(active, bool):
        raise TypeError("active must be a boolean")

    if isinstance(balance, Decimal):
        decimal_balance = balance
    elif isinstance(balance, str):
        try:
            decimal_balance = Decimal(balance.strip())
        except Exception as error:
            raise ValueError("balance must be a valid decimal") from error
    else:
        raise TypeError("balance must be Decimal or decimal text")

    if customer_id <= 0:
        raise ValueError("customer_id must be positive")

    if not 0 <= age <= 150:
        raise ValueError("age must be between 0 and 150")

    if not decimal_balance.is_finite():
        raise ValueError("balance must be finite")

    return CustomerRecord(
        customer_id=customer_id,
        name=name.strip(),
        age=age,
        active=active,
        balance=decimal_balance,
    )


def demonstrate_real_world_pipeline() -> None:
    section("72. INTEGRATED REAL-WORLD VALIDATION AND CONVERSION")

    raw_records: list[dict[str, object]] = [
        {
            "customer_id": 101,
            "name": "Ada",
            "age": 36,
            "active": True,
            "balance": "1250.50",
        },
        {
            "customer_id": 102,
            "name": "Grace",
            "age": "40",
            "active": True,
            "balance": "500.25",
        },
        {
            "customer_id": 103,
            "name": "Alan",
            "age": 42,
            "active": "yes",
            "balance": Decimal("100.00"),
        },
    ]

    for raw in raw_records:
        try:
            record = parse_customer_record(raw)
            print("VALID:", record)
        except (TypeError, ValueError) as error:
            print("INVALID:", raw)
            print("  Reason:", type(error).__name__, error)


# =============================================================================
# 72. FINAL CONCEPT MAP
# =============================================================================

def concept_map() -> None:
    section("73. CONCEPT MAP")

    concepts = {
        "Runtime type inspection": [
            "type()",
            "isinstance()",
            "issubclass()",
            "type objects",
            "inheritance",
        ],
        "Runtime conversion": [
            "int()",
            "float()",
            "complex()",
            "str()",
            "bool()",
            "bytes()",
            "list()",
            "tuple()",
            "set()",
            "dict()",
        ],
        "Numeric conversion": [
            "int",
            "float",
            "Decimal",
            "Fraction",
            "rounding",
            "truncation",
            "floor",
            "ceiling",
        ],
        "Text and binary conversion": [
            "encode()",
            "decode()",
            "ord()",
            "chr()",
            "Unicode",
            "UTF-8",
        ],
        "Static typing": [
            "annotations",
            "Union",
            "Optional",
            "TypeVar",
            "Generic",
            "Protocol",
            "overload",
            "cast",
        ],
        "Runtime validation": [
            "input validation",
            "type narrowing",
            "domain constraints",
            "exception handling",
            "trusted internal models",
        ],
        "Production concerns": [
            "security",
            "resource limits",
            "precision",
            "performance",
            "testing",
            "API boundaries",
            "serialization",
        ],
    }

    for category, items in concepts.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  - {item}")


# =============================================================================
# 73. MAIN
# =============================================================================

def main() -> None:
    """
    Execute all educational demonstrations in a deliberate beginner-to-advanced
    order.
    """
    demonstrate_basic_types()
    demonstrate_type_and_isinstance()
    demonstrate_type_information()
    demonstrate_numeric_conversion()
    demonstrate_string_parsing()
    demonstrate_integer_bases()
    demonstrate_character_and_bytes_conversion()
    demonstrate_collection_conversion()
    demonstrate_conversion_vs_casting()
    demonstrate_numeric_operations()
    demonstrate_truthiness()
    demonstrate_boolean_parsing()
    demonstrate_conversion_errors()
    demonstrate_validation()
    demonstrate_input_concept()
    demonstrate_float_precision()
    demonstrate_rounding()
    demonstrate_decimal_and_fraction()
    demonstrate_enums()
    demonstrate_custom_conversion_protocols()
    demonstrate_bool_protocol()
    demonstrate_type_hints()
    demonstrate_union_types()
    demonstrate_any_and_object()
    demonstrate_type_narrowing()
    demonstrate_type_aliases()
    demonstrate_generics()
    demonstrate_protocols()
    demonstrate_class_hierarchy()
    demonstrate_multiple_type_checks()
    demonstrate_bool_integer_relationship()
    demonstrate_iterable_requirements()
    demonstrate_shallow_conversion()
    demonstrate_copying()
    demonstrate_dataclass_validation()
    demonstrate_structural_typing()
    demonstrate_overloads()
    demonstrate_type_objects()
    demonstrate_type_dispatch()
    demonstrate_default_conversion()
    demonstrate_validation_pipeline()
    demonstrate_exception_chaining()
    demonstrate_special_float_values()
    demonstrate_none()
    demonstrate_runtime_generic_validation()
    demonstrate_typing_introspection()
    demonstrate_runtime_annotation_validation()
    demonstrate_json_conversion()
    demonstrate_custom_json_serialization()
    demonstrate_csv_conversion()
    demonstrate_datetime_conversion()
    demonstrate_subclass_conversion_concept()
    demonstrate_duck_typing()
    demonstrate_getattr_validation()
    demonstrate_custom_numeric_type()
    demonstrate_domain_conversion()
    demonstrate_integer_precision()
    demonstrate_performance()
    demonstrate_conversion_performance_pattern()
    demonstrate_safe_parsing()
    demonstrate_resource_limits()
    demonstrate_common_mistakes()
    demonstrate_edge_cases()
    demonstrate_normalization()
    demonstrate_conversion_matrix()
    demonstrate_boundary_design()
    run_tests()
    type_checking_decision_guide()
    demonstrate_comparison()
    production_best_practices()
    demonstrate_real_world_pipeline()
    concept_map()

    section("74. SCRIPT COMPLETED")
    print("All demonstrations and self-tests have finished.")


if __name__ == "__main__":
    main()
