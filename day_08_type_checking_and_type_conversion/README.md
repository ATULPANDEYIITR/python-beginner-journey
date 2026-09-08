# Type Checking and Type Conversion in Python

## Introduction

Python is dynamically typed, which means variables do not have permanently declared types. An object has a runtime type, and a variable can later refer to an object of another type.

Type checking and type conversion are therefore fundamental Python skills.

**Type checking** determines what type an object has or whether an object satisfies a particular type relationship.

**Type conversion** changes a value from one representation or type into another representation, such as converting `"42"` into `42`, a list into a tuple, text into UTF-8 bytes, or a decimal string into `Decimal`.

The accompanying Python script progresses from basic runtime type inspection to advanced topics such as type narrowing, protocols, generics, custom conversion protocols, static annotations, serialization, validation pipelines, security, performance, and production design.

---

## 1. Python's Object and Type Model

Everything used as a value in Python is an object. Objects include:

- integers
- floating-point numbers
- strings
- Boolean values
- lists
- tuples
- sets
- dictionaries
- functions
- classes
- instances of user-defined classes
- `None`

Every ordinary object has a runtime class.

For example:

- `42` is an instance of `int`
- `3.14` is an instance of `float`
- `"Python"` is an instance of `str`
- `[1, 2, 3]` is an instance of `list`
- `None` is an instance of `NoneType`

The script demonstrates this using `type()` and related introspection techniques.

---

## 2. `type()`

The built-in `type()` function returns the object's runtime class.

Conceptually:

    type(value)

For example:

    type(42)

returns the `int` class.

`type()` is useful when exact runtime information is required.

An important distinction is:

    type(value) is int

This checks whether the object's exact runtime class is `int`.

A subclass does not pass this exact comparison:

    class CustomInteger(int):
        pass

    value = CustomInteger(10)

Here:

    type(value) is int

is false because the exact class is `CustomInteger`.

---

## 3. `isinstance()`

`isinstance()` determines whether an object is an instance of a class or one of its subclasses.

Conceptually:

    isinstance(value, ExpectedType)

For example:

    isinstance(10, int)

returns `True`.

Unlike `type(value) is int`, `isinstance()` respects inheritance.

If `CustomInteger` inherits from `int`:

    isinstance(CustomInteger(10), int)

is `True`.

This makes `isinstance()` the preferred choice when subclasses should be accepted.

### Multiple accepted types

A tuple of classes can be supplied:

    isinstance(value, (int, float))

This means the value may be an `int` or a `float`, including compatible subclasses.

---

## 4. `type()` Versus `isinstance()`

The distinction is important:

| Expression | Meaning |
|---|---|
| `type(x)` | Returns the exact runtime class |
| `type(x) is T` | Requires exact runtime class `T` |
| `isinstance(x, T)` | Accepts `T` and subclasses |
| `issubclass(C, T)` | Checks whether class `C` derives from `T` |

A common design rule is to use `isinstance()` for behavioral or API compatibility and reserve exact `type()` comparisons for cases where exact runtime identity genuinely matters.

---

## 5. `issubclass()`

`issubclass()` works with classes rather than instances.

Conceptually:

    issubclass(SubClass, BaseClass)

For example:

    issubclass(Car, Vehicle)

returns `True` if `Car` derives from `Vehicle`.

The first argument must be a class. Passing an ordinary object produces `TypeError`.

---

## 6. Python's Core Built-in Types

The script demonstrates representative Python types including:

- `NoneType`
- `bool`
- `int`
- `float`
- `complex`
- `str`
- `list`
- `tuple`
- `set`
- `dict`
- `bytes`
- `bytearray`

These types have different behaviors and conversion rules.

For example, a string is an iterable of characters, while a dictionary is an iterable over its keys.

This has important consequences when using collection constructors.

---

## 7. Boolean Values and the `bool`/`int` Relationship

One of Python's most important type peculiarities is:

    bool

is a subclass of:

    int

Consequently:

    isinstance(True, int)

is `True`.

Also:

    int(True)

produces `1`, and:

    int(False)

produces `0`.

Boolean values can participate in arithmetic:

    True + True

produces `2`.

This behavior is valid Python, but it can cause validation bugs.

If an application requires an actual integer and wants to reject Boolean values, a robust check is:

    isinstance(value, int) and not isinstance(value, bool)

This distinction is demonstrated repeatedly in the script.

---

# Type Conversion

## 8. What Type Conversion Means

Type conversion is the process of obtaining a value in another type or representation.

Common conversion functions include:

- `int()`
- `float()`
- `complex()`
- `str()`
- `bool()`
- `bytes()`
- `bytearray()`
- `list()`
- `tuple()`
- `set()`
- `frozenset()`
- `dict()`

Conversion can either succeed, fail with an exception, or produce a result whose semantics are different from what a beginner might expect.

---

## 9. Integer Conversion

`int()` can convert compatible values to integers.

Examples include:

    int("42")
    int(42.9)
    int(True)

A particularly important rule is that:

    int(12.99)

does not round to `13`.

It produces `12`.

Likewise:

    int(-12.99)

produces `-12`.

Conversion from floating point to integer truncates toward zero.

This differs from mathematical floor:

    math.floor(-12.99)

produces `-13`.

---

## 10. Floating-Point Conversion

`float()` converts compatible numeric values or numeric strings into floating-point values.

Examples include:

    float(10)
    float("10.25")
    float("1e3")

Floating-point values can also represent special values:

    float("nan")
    float("inf")
    float("-inf")

These values need special handling.

`math.isfinite()`, `math.isnan()`, and `math.isinf()` provide explicit tests.

---

## 11. Complex Conversion

`complex()` creates complex numbers.

Examples include:

    complex(5)
    complex("3+4j")

A complex number contains real and imaginary components.

Complex values are not ordered in the same way as ordinary real numbers, so operations such as `<` and `>` are not generally available between complex numbers.

---

## 12. String Conversion

`str()` creates a string representation of an object.

For example:

    str(42)

produces `"42"`.

String conversion is not necessarily a serialization format suitable for later reconstruction. A human-readable representation and a machine-readable serialization format are different concepts.

For structured data, formats such as JSON often provide more appropriate serialization semantics.

---

## 13. Boolean Conversion

`bool()` performs truth-value testing.

Common false-like values include:

- `False`
- `0`
- `0.0`
- `""`
- `[]`
- `()`
- `{}`
- `None`

Many other values are true-like.

A critical misconception is:

    bool("False")

This is `True`.

The reason is that `"False"` is a non-empty string.

Therefore `bool()` should not be used to parse textual Boolean values from forms, configuration files, APIs, or command-line arguments.

---

# Parsing Text

## 14. Converting Text to Numbers

User input and many external interfaces provide text.

For example:

    "25"

is a string rather than an integer.

It must be explicitly converted:

    int("25")

The same principle applies to floating-point values:

    float("25.5")

Conversion can fail when the text does not represent the required format.

For example:

    int("hello")

raises `ValueError`.

---

## 15. `ValueError` Versus `TypeError`

These exceptions often have different meanings.

`ValueError` generally means the type is acceptable but the value is inappropriate.

For example:

    int("hello")

The argument is a string, which `int()` can accept, but its contents do not represent an integer.

`TypeError` generally indicates that the supplied object is of an inappropriate type or that an operation is not supported between the given types.

For example, an operation expecting an integer-specific argument may reject a float or an arbitrary object.

Understanding this distinction makes validation and error handling clearer.

---

## 16. Integer Base Conversion

`int()` can parse strings using different number bases.

Examples:

    int("1010", 2)
    int("52", 8)
    int("2A", 16)

Python supports bases from `2` through `36`.

The reverse representation can be obtained with:

    bin(42)
    oct(42)
    hex(42)

These return strings representing the number in the corresponding base.

---

## 17. `int(..., 0)` and Prefix-Based Parsing

The base value `0` allows Python to infer the base from standard prefixes.

For example:

    int("0b1010", 0)
    int("0o52", 0)
    int("0x2A", 0)

This can be useful when accepting conventional Python-style integer representations.

---

# Characters and Binary Data

## 18. `ord()` and `chr()`

`ord()` converts a single character into its Unicode code point.

For example:

    ord("A")

produces `65`.

`chr()` performs the reverse conceptual operation:

    chr(65)

produces `"A"`.

These functions illustrate the distinction between a character's textual representation and its numeric Unicode code point.

---

## 19. Strings, Bytes, and Encoding

Python distinguishes text from binary data.

`str` represents text.

`bytes` represents immutable binary data.

`bytearray` represents mutable binary data.

Text can be encoded:

    text.encode("utf-8")

and bytes can be decoded:

    data.decode("utf-8")

Encoding converts Unicode text into a byte representation.

Decoding converts bytes back into text.

The encoding must match the data's actual encoding scheme.

UTF-8 is a common choice for interoperability.

---

## 20. `bytes()` Conversion

`bytes()` has several behaviors depending on its input.

For an integer:

    bytes(4)

creates four zero bytes.

For an iterable of integers:

    bytes([65, 66, 67])

creates bytes corresponding to those numeric byte values.

Each integer must be in the byte range `0` through `255`.

An invalid value such as `256` raises `ValueError`.

---

# Collection Conversion

## 21. List, Tuple, Set, and Frozenset Conversion

Collection constructors can consume iterables.

Examples:

    list("abc")

produces:

    ["a", "b", "c"]

Similarly:

    tuple("abc")

produces a tuple of characters.

A set removes duplicate values:

    set([1, 2, 2, 3])

produces a set containing unique values.

This means conversion can change more than the container's class.

A conversion to a set also changes the data's multiplicity semantics.

---

## 22. Set Conversion and Ordering

A set is not a sequence.

If an application requires:

- ordering
- duplicate preservation
- positional indexing

then converting a sequence to a set may destroy required semantics.

Therefore type conversion should be based on the required data model rather than simply the desired container name.

---

## 23. Dictionary Conversion

`dict()` can construct dictionaries from suitable iterable structures.

For example:

    dict([
        ("name", "Ada"),
        ("age", 36)
    ])

produces a dictionary.

The source must contain suitable key-value pairs.

Dictionary keys must be hashable.

Attempting to use an unhashable object such as a list as a dictionary key produces `TypeError`.

---

# Conversion Versus Casting

## 24. Runtime Conversion

A runtime conversion actually produces a value in another representation.

For example:

    integer_value = int("123")

The resulting object is an integer.

---

## 25. `typing.cast()`

`typing.cast()` has fundamentally different behavior.

For example:

    cast(int, "123")

does not convert the string into an integer.

The runtime object remains a string.

`cast()` is a static typing instruction that tells a type checker to treat an expression as another type.

Therefore:

- `int("123")` is runtime conversion.
- `cast(int, "123")` is static type assertion.

Using `cast()` to perform runtime validation is a conceptual error.

---

# Implicit Coercion

## 26. Numeric Operations

Python supports certain numeric promotions.

For example:

    1 + 2.5

produces a floating-point result.

Python does not automatically interpret arbitrary strings as numbers.

For example:

    10 + "5"

raises `TypeError`.

Explicit conversion is required:

    10 + int("5")

The language therefore combines some well-defined numeric interoperability with strict separation between unrelated data representations.

---

# Truth-Value Testing

## 27. Truthiness

Python determines whether objects are true or false in Boolean contexts.

Examples include:

    if value:
        ...

An object's truth value can be determined by its Boolean protocol.

Empty collections are normally false-like.

Non-empty collections are normally true-like.

This is different from checking whether a value is literally the Boolean `True`.

For example:

    bool([0])

is `True` because the list is non-empty.

---

# Robust Boolean Parsing

## 28. Parsing Textual Booleans

Applications frequently receive values such as:

- `"true"`
- `"false"`
- `"yes"`
- `"no"`
- `"1"`
- `"0"`
- `"on"`
- `"off"`

These should be interpreted according to an explicit application-defined grammar.

The script implements a parser that:

1. verifies that the input is a string
2. removes surrounding whitespace
3. normalizes case
4. checks explicit accepted true values
5. checks explicit accepted false values
6. rejects unknown values

This is safer than using `bool(text)`.

---

# Numeric Precision

## 29. Floating-Point Representation

Floating-point numbers are stored using binary floating-point representation.

Many decimal fractions cannot be represented exactly in binary floating point.

Consequently:

    0.1 + 0.2

does not necessarily compare equal to:

    0.3

using exact equality.

This is a representation issue rather than a failure of arithmetic.

---

## 30. `Decimal`

The `decimal.Decimal` type provides decimal arithmetic suitable for cases where decimal representation and controlled precision matter.

A particularly important distinction is:

    Decimal("0.1")

versus:

    Decimal(0.1)

The first constructs a decimal from the textual decimal representation.

The second receives the already approximated binary floating-point value.

When decimal accuracy matters, constructing `Decimal` from appropriate textual or integer representations is generally preferable.

---

## 31. `Fraction`

`fractions.Fraction` represents rational numbers exactly.

For example:

    Fraction(3, 4)

represents exactly three-fourths.

It can be converted to a float when a floating-point approximation is acceptable.

Fraction conversion is useful when exact rational arithmetic is required.

---

# Rounding and Truncation

## 32. `int()`, `math.trunc()`, `floor()`, `ceil()`, and `round()`

These operations have distinct meanings.

| Operation | Purpose |
|---|---|
| `int(x)` | Converts to integer, truncating toward zero |
| `math.trunc(x)` | Truncates toward zero |
| `math.floor(x)` | Largest integer less than or equal to `x` |
| `math.ceil(x)` | Smallest integer greater than or equal to `x` |
| `round(x)` | Rounds according to Python's rounding semantics |

Negative values demonstrate the difference particularly clearly.

For example, truncating `-3.7` produces `-3`, while flooring it produces `-4`.

---

# Enums

## 33. `Enum`

Enumerations represent controlled sets of named values.

Example:

    class Status(Enum):
        PENDING = "pending"
        ACTIVE = "active"
        CLOSED = "closed"

An enum member has:

- a name
- a value
- its own enum type

Enum values can be reconstructed from their underlying value.

---

## 34. `IntEnum`

`IntEnum` combines enumeration semantics with integer behavior.

This means an `IntEnum` member is also an integer subclass.

This can be convenient for interoperability with APIs requiring integer constants, but it weakens the separation between the enumeration and ordinary integers.

---

# Custom Conversion Protocols

## 35. `__int__`

A class can define `__int__()` to support:

    int(instance)

The method should provide an appropriate integer representation.

---

## 36. `__float__`

A class can define `__float__()` to support:

    float(instance)

The implementation should provide a meaningful floating-point representation.

---

## 37. `__index__`

`__index__()` is more restrictive than `__int__()`.

It represents an exact integer suitable for operations that require an integer index.

Examples include sequence indexing and certain integer-oriented operations.

An object representing `12.8` should not normally claim to be a valid exact integer index.

The script demonstrates this distinction using a custom measurement class.

---

## 38. `__bool__`

Classes can define `__bool__()` to control truth-value testing.

This means:

    bool(instance)

can invoke application-defined logic.

Such behavior should be intuitive and predictable because Boolean contexts are common throughout Python programs.

---

# Static Type Hints

## 39. Type Annotations

Type annotations communicate intended types.

For example:

    def add_numbers(left: int, right: int) -> int:
        return left + right

Annotations improve:

- readability
- editor assistance
- static analysis
- API documentation
- maintainability
- refactoring safety

They do not normally enforce runtime types by themselves.

---

## 40. Annotations Are Not Automatic Runtime Validation

A function annotated with:

    def process(value: int) -> int:
        ...

does not automatically reject every non-integer at runtime.

Python normally does not insert runtime type validation merely because an annotation exists.

If external data must be validated, explicit runtime checks are required.

This distinction is fundamental:

**Static type checking and runtime type checking are separate mechanisms.**

---

# Optional and Union Types

## 41. Optional Values

An optional integer can be expressed conceptually as:

    int | None

This means the value may be an integer or `None`.

`None` often represents:

- missing data
- no result
- absence of an optional value
- an intentionally empty state

Code should narrow the value before using it as an integer.

---

## 42. Union Types

A union allows several types:

    int | str

A function accepting such a value should determine which case it received before applying type-specific operations.

Runtime narrowing is commonly performed with `isinstance()`.

---

# Type Narrowing

## 43. Runtime Type Narrowing

Suppose a value has the conceptual type:

    int | str | None

The program can narrow it:

1. check `None`
2. check `int`
3. handle the remaining `str` case

Static type checkers can understand many such control-flow-based narrowing patterns.

This is one reason explicit checks are preferable to unchecked assumptions.

---

# `Any` Versus `object`

## 44. `Any`

`Any` tells static type analysis to permit essentially arbitrary operations.

It is useful at highly dynamic boundaries, but excessive use weakens the benefits of static typing.

If a value becomes `Any` too early, type errors can spread unnoticed through the program.

---

## 45. `object`

`object` means that a value can be any Python object, but operations on it are not automatically assumed to be valid.

The program must narrow the value before performing type-specific operations.

This makes `object` safer than indiscriminate use of `Any` when the exact runtime type is genuinely unknown.

---

# Type Aliases

## 46. Type Aliases

A type alias gives a meaningful name to a type expression.

For example:

    NumberLike = int | float | Decimal

This can improve readability when a type expression appears repeatedly.

Type aliases describe the type contract. They do not automatically convert values into the accepted types.

---

# Generics

## 47. Generic Types

Generics express relationships between types.

A generic container can conceptually be parameterized by its contained value type:

    Box[int]
    Box[str]

The script implements a simple generic `Box`.

Generics are especially useful for:

- reusable data structures
- APIs
- collections
- repositories
- utility functions
- libraries

Generic annotations primarily support static analysis and documentation.

They do not automatically perform runtime validation of the generic parameter.

---

# Protocols and Structural Typing

## 48. Protocols

A protocol describes expected behavior rather than requiring a particular inheritance relationship.

For example, a protocol can require:

    __len__()

A list, tuple, string, and dictionary already provide this behavior even though they do not inherit from a custom `SupportsLength` class.

This reflects structural typing:

> An object can satisfy an interface because it provides the required behavior.

---

## 49. `@runtime_checkable`

A protocol decorated with `@runtime_checkable` can participate in certain runtime `isinstance()` checks.

Runtime protocol checks are useful for simple capability checks, but they should not be confused with complete static type analysis.

Static protocol checking can express richer structural relationships than a simple runtime check.

---

# Duck Typing

## 50. Duck Typing

Python often emphasizes behavior rather than nominal class identity.

The common idea is that an object can be used when it provides the required operation.

For example, a function that needs a `write()` operation may work with multiple unrelated classes that implement `write()`.

The script demonstrates this using `Printer` and `Logger`.

Explicit `getattr()` plus `callable()` checks can be used when runtime validation is necessary.

---

# Custom Classes and Conversion

## 51. Domain-Specific Conversion

Not every conversion is a generic Python type conversion.

For example:

- Celsius to Fahrenheit
- Fahrenheit to Celsius
- meters to feet
- currencies between units
- database records to domain objects

are domain transformations.

They require business or mathematical rules rather than simply calling `int()` or `str()`.

The script separates domain conversion from generic Python type conversion.

---

# `__new__` and Custom Numeric Types

## 52. Validated Numeric Subclasses

An `int` subclass can override construction behavior to enforce domain constraints.

The script defines `PositiveInteger`, which accepts values that can be converted to integers and rejects non-positive values.

This demonstrates that a custom type can combine:

- conversion
- validation
- inheritance
- domain-specific invariants

---

# Collection Conversion and Generators

## 53. Iterable Consumption

Collection constructors such as:

    list()
    tuple()
    set()

consume iterables.

Generators are especially important because they are generally consumed as they are iterated.

For example:

    generator = (x * 2 for x in range(4))

After:

    list(generator)

the generator is exhausted.

Calling `list(generator)` again does not recreate the original data.

This is a behavioral consequence of conversion from a one-shot iterable.

---

# Shallow Conversion

## 54. Outer Container Versus Nested Objects

Consider:

    nested = [[1, 2], [3, 4]]
    converted = tuple(nested)

Only the outer container changes from `list` to `tuple`.

The inner lists remain the same objects.

Therefore:

    converted[0] is nested[0]

is `True`.

A tuple containing mutable objects is not recursively immutable.

---

# Copying Versus Conversion

## 55. Shallow and Deep Copy

Conversion and copying are different concepts.

`tuple(list_value)` changes the outer container representation.

`copy()` creates a shallow copy.

`deepcopy()` recursively duplicates supported nested objects.

The script demonstrates how mutations to nested objects can remain visible through a shallow copy but not through an appropriate deep copy.

---

# Validation

## 56. Conversion Is Not Validation

Successfully converting a value does not mean the value is valid for the application.

For example:

    int("200")

succeeds.

That does not mean `200` is a valid age.

Validation has at least two conceptual layers:

1. **Representation validation**
   - Can the value be parsed?
2. **Domain validation**
   - Is the resulting value acceptable?

The `convert_age()` function demonstrates this distinction.

---

# Validation Pipeline

## 57. Recommended Boundary Pipeline

A robust data-processing pipeline often follows this pattern:

    external input
        ↓
    type validation
        ↓
    syntax conversion
        ↓
    domain validation
        ↓
    trusted internal representation
        ↓
    business logic

For example, an order might arrive as:

    quantity = "3"
    price = "19.99"

The application can convert these into:

    quantity = 3
    price = Decimal("19.99")

and then validate that:

- quantity is positive
- price is non-negative
- both values are finite and structurally valid

The business logic can then operate on trusted representations.

---

# Exception Chaining

## 58. Preserving Conversion Causes

When converting external data, it is useful to translate low-level exceptions into domain-specific exceptions while preserving the original cause.

Conceptually:

    try:
        value = Decimal(text)
    except Exception as error:
        raise ValueError("Invalid decimal") from error

The `from error` clause preserves the original exception as the cause.

This improves debugging and diagnostic information.

---

# `None`

## 59. Testing for `None`

The preferred test is:

    value is None

rather than:

    value == None

`None` is a singleton sentinel representing absence.

Identity testing communicates the intended semantics clearly.

---

# Floating-Point Special Values

## 60. NaN

`NaN` means "Not a Number".

A significant property is:

    nan != nan

Therefore this is not a reliable NaN check:

    value == float("nan")

Use:

    math.isnan(value)

instead.

---

## 61. Infinity

Floating-point infinity can be positive or negative.

Use:

    math.isinf(value)

to test for infinity.

Use:

    math.isfinite(value)

when the application requires an ordinary finite number.

Validation should often reject non-finite values when processing financial, scientific, or domain-specific quantities that do not permit them.

---

# Runtime Validation of Collections

## 62. Generic Runtime Types

An annotation such as:

    list[int]

expresses that a list should contain integers.

But a simple runtime check such as:

    isinstance(value, list[int])

is not the normal mechanism for validating the element types.

Runtime validation generally requires:

1. checking the outer container
2. checking every element

For example:

    isinstance(value, list)

followed by element checks.

This is especially important for data loaded from external systems.

---

# Type Introspection

## 63. `typing.get_origin()` and `typing.get_args()`

Typing expressions can be inspected.

For:

    list[int]

the origin is conceptually the list type, while the argument is `int`.

For:

    int | str

the arguments are `int` and `str`.

This introspection is useful when building sophisticated runtime validation or framework infrastructure.

It should not be confused with automatic validation.

---

# Function Annotation Introspection

## 64. `get_type_hints()`

`typing.get_type_hints()` can retrieve resolved annotations from functions and classes.

This can be useful for:

- frameworks
- validation systems
- documentation systems
- dependency injection
- introspection tools

But obtaining an annotation is different from enforcing it.

---

# Overloads

## 65. `@overload`

`typing.overload` allows a function to describe multiple static call signatures.

For example, a function can accept:

    int

or:

    str

and return an integer in either case.

The actual implementation still executes at runtime and must handle the input safely.

Overloads are primarily for static analysis and API clarity.

---

# JSON Conversion

## 66. JSON and Python Types

JSON has a smaller conceptual type system than Python.

Typical mappings include:

| JSON concept | Python representation |
|---|---|
| object | `dict` |
| array | `list` |
| string | `str` |
| number | `int` or `float` |
| boolean | `bool` |
| null | `None` |

The script uses:

    json.dumps()

to serialize Python structures into JSON text.

It uses:

    json.loads()

to parse JSON text back into Python objects.

---

# Custom JSON Serialization

## 67. Python Types Not Directly Representable by JSON

Objects such as:

- `Decimal`
- `set`
- `bytes`
- custom classes

require explicit serialization rules.

The script demonstrates a `default` serializer that converts selected types into JSON-compatible values.

A particularly important financial design choice is whether a `Decimal` should become a JSON number or a JSON string.

Converting a precise decimal to a floating-point number can introduce unwanted precision loss. Representing it as a string can preserve its decimal representation.

The correct choice depends on the receiving system's contract.

---

# Date and Time Conversion

## 68. ISO Date and Time Parsing

The script demonstrates:

    date.fromisoformat()

and:

    datetime.fromisoformat()

These parse standard ISO-style date and datetime representations.

Date and datetime are separate concepts.

A datetime contains both date and time information.

A date contains only date information.

A timezone-aware datetime can be converted to another timezone using:

    astimezone()

Timezone handling is a domain where explicit representation is particularly important.

---

# Inheritance Versus Conversion

## 69. Subtyping Is Not Conversion

If:

    class Dog(Animal):
        ...

then a `Dog` object can be assigned to a variable conceptually representing an `Animal`.

This is subtyping and polymorphism.

It does not mean the object has been converted from `Dog` to `Animal`.

The same runtime object can be viewed through a base-class interface.

This distinction is important when designing class hierarchies.

---

# Type-Based Dispatch

## 70. Dispatching Based on Runtime Type

A function can use `isinstance()` checks to select behavior.

For example:

- Boolean values can receive Boolean-specific formatting.
- integers can receive integer-specific formatting.
- decimals can receive decimal-specific formatting.
- strings can receive string-specific formatting.

The order of checks matters when types have inheritance relationships.

Because `bool` is a subclass of `int`, a Boolean check should occur before an integer check if Boolean behavior is supposed to be distinct.

---

# Default Conversion

## 71. Controlled Defaults

Sometimes applications intentionally provide fallback values.

For example:

    to_int_or_default("invalid", default=-1)

can return `-1`.

This should be done deliberately.

Silently replacing invalid data with a default can hide data-quality problems.

A default is appropriate when the application semantics explicitly define what missing or invalid input means.

---

# Type Checking External Data

## 72. Dataclasses Do Not Automatically Validate Types

A dataclass declaration such as:

    @dataclass
    class Person:
        name: str
        age: int

documents the intended fields and their types.

It does not automatically guarantee that every constructor call receives the correct runtime types.

For example, external data should still be validated before being converted into a trusted internal model.

The script demonstrates explicit validation before constructing a dataclass.

---

# Structural Typing

## 73. Behavior-Based Interfaces

Structural typing focuses on required attributes or methods rather than inheritance.

A type can satisfy a structural interface without explicitly inheriting from a base class.

This is particularly useful in Python because many APIs are behavior-oriented.

Examples include objects that:

- can be measured with `len()`
- can be written to
- can be iterated
- expose a particular attribute

---

# Security Considerations

## 74. Never Use `eval()` as a General Conversion Mechanism

A dangerous pattern is interpreting untrusted input as executable Python code.

`eval()` executes expressions.

It is not an ordinary conversion function.

For external input, use narrowly defined parsers such as:

- `int()`
- `float()`
- `Decimal()`
- `json.loads()`
- explicit Boolean parsers
- application-specific validation

The principle is:

**Parse data as data rather than interpreting untrusted data as executable code.**

---

## 75. Resource Limits

Type conversion can consume computational resources.

Extremely large:

- integers
- strings
- collections
- nested structures

can increase memory or CPU usage.

Applications processing untrusted input should apply reasonable size limits before expensive operations.

The script demonstrates a basic input-size validation pattern.

---

# Performance Considerations

## 76. Cost of Type Checks and Conversion

Operations such as:

    isinstance()
    type()
    int()

are generally efficient, but they still have a cost.

The script uses `timeit` to measure representative operations.

The measurements are machine-dependent and should not be treated as universal benchmarks.

Performance optimization should be based on profiling real workloads.

---

## 77. Avoiding Unnecessary Conversion

Repeated conversion can be wasteful.

If a value is already an integer, there is generally no need to repeatedly parse its string representation.

A good architecture normalizes data at the boundary and uses the normalized representation internally.

For example:

    external string
        ↓
    one conversion
        ↓
    internal integer

is generally preferable to repeatedly converting the same external representation throughout the business logic.

---

# Common Mistakes

## 78. Comparing Text to Numbers

This is incorrect when numeric comparison is intended:

    age = "25"
    age > 18

The string must first be parsed:

    age = int(age)
    age > 18

---

## 79. Using `bool()` to Parse `"false"`

This produces `True`:

    bool("false")

because the string is non-empty.

Explicit textual parsing is required.

---

## 80. Assuming Type Hints Enforce Runtime Types

Annotations communicate intended types but do not automatically enforce runtime contracts.

External input requires explicit validation.

---

## 81. Confusing `cast()` With Conversion

This:

    cast(int, "123")

does not produce an integer.

This:

    int("123")

does.

---

## 82. Forgetting the `bool`/`int` Relationship

This:

    isinstance(True, int)

is `True`.

If Boolean values should be rejected, test for them explicitly.

---

## 83. Assuming `int(float)` Rounds

This:

    int(9.99)

produces `9`, not `10`.

Use `round()` when rounding is the intended operation.

---

# Edge Cases

## 84. Important Conversion Edge Cases

The script demonstrates cases including:

- `int(True)`
- `int(False)`
- leading and trailing whitespace
- explicit plus signs
- negative numbers
- scientific notation
- `NaN`
- positive infinity
- negative infinity
- invalid numeric strings
- invalid Unicode code points
- invalid byte values
- empty strings
- `None`
- Boolean values treated as integers
- generator exhaustion
- nested mutable objects
- very large integers

These cases are important because seemingly simple conversion functions can have non-obvious behavior.

---

# Large Integers

## 85. Python Integer Precision

Python integers use arbitrary precision rather than a fixed-width machine integer representation.

This allows values much larger than typical 32-bit or 64-bit integer ranges.

The practical limit is constrained by available memory and computation.

Converting extremely large integers to floating point can fail because floating-point representations have a limited range.

---

# Conversion of Untrusted Data

## 86. Trust Boundaries

Data can enter an application through:

- HTTP requests
- forms
- command-line arguments
- environment variables
- configuration files
- databases
- message queues
- JSON payloads
- CSV files
- user input

External data should be considered untrusted until validated.

A robust system converts it into an internal representation that satisfies explicit invariants.

The integrated customer-record example demonstrates this pattern.

---

# Production Design

## 87. Boundary Normalization

A strong architectural principle is:

**Convert and validate external data at system boundaries.**

For example:

    API request
        ↓
    raw strings / JSON values
        ↓
    validation
        ↓
    conversion
        ↓
    domain model
        ↓
    business logic

This prevents conversion logic from being scattered throughout the application.

---

## 88. Keep Business Logic Typed

Once data has been validated, internal functions should ideally operate on meaningful types.

For example:

    def calculate_total(
        quantity: int,
        price: Decimal,
    ) -> Decimal:
        ...

This is clearer than having every business function repeatedly accept arbitrary strings and convert them.

---

# Testing

## 89. What Conversion Tests Should Cover

Conversion functions should test:

### Valid values

Examples:

- `"42"`
- `" 42 "`
- `"3.14"`
- `"true"`

### Invalid values

Examples:

- `"abc"`
- `""`
- malformed numeric strings
- unsupported runtime objects

### Boundary values

Examples:

- zero
- negative numbers
- maximum permitted domain values
- values immediately outside the domain

### Type edge cases

Examples:

- `None`
- `True`
- `False`
- subclasses
- unexpected collection types

The script includes self-tests using Python assertions.

---

# Conversion and Validation Comparison

## 90. Conversion Versus Validation

| Concept | Question |
|---|---|
| Type checking | What kind of object is this? |
| Parsing | Can this representation be interpreted? |
| Conversion | Can this value be represented in another type? |
| Domain validation | Is this value allowed by the application? |
| Type annotation | What type is intended? |
| Static checking | Does source code satisfy declared type relationships? |
| Runtime validation | Does the actual object satisfy the required contract? |
| Serialization | How is an object represented externally? |
| Deserialization | How is an external representation reconstructed? |

These concepts are related but should not be conflated.

---

# `Any`, `object`, and Explicit Validation

## 91. Choosing Between Dynamic and Explicit Types

`Any` is appropriate when dynamic behavior is unavoidable, but excessive use removes useful static guarantees.

`object` communicates that the value is unknown without permitting arbitrary operations.

Explicit runtime checks provide the strongest control when data comes from an untrusted boundary.

A practical pattern is:

    value: object

followed by:

    if isinstance(value, int):
        ...

This creates a controlled narrowing process.

---

# Type Checking Decision Guide

## 92. Which Mechanism Should Be Used?

| Requirement | Appropriate mechanism |
|---|---|
| Know exact runtime type | `type(value)` |
| Require exact class | `type(value) is T` |
| Accept subclasses | `isinstance(value, T)` |
| Check several types | `isinstance(value, (A, B))` |
| Check class inheritance | `issubclass()` |
| Perform runtime conversion | `int()`, `float()`, `str()`, etc. |
| Communicate intended type | Type annotations |
| Static assertion | `cast()` |
| Behavior-based interface | Protocol or duck typing |
| Validate external values | Explicit runtime validation |
| Parse JSON | `json.loads()` |
| Serialize JSON | `json.dumps()` |
| Exact decimal arithmetic | `Decimal` |
| Exact rational arithmetic | `Fraction` |

---

# Important Implementation Principles

## 93. Principle 1: Do Not Confuse Representation With Meaning

The string:

    "100"

is not automatically an integer.

It is textual data representing a possible integer.

Conversion gives it numeric meaning.

---

## 94. Principle 2: Conversion Does Not Guarantee Validity

A successful conversion only proves that the representation was acceptable to the converter.

Domain validation is still necessary.

---

## 95. Principle 3: Type Annotations and Runtime Validation Have Different Roles

Annotations primarily communicate intended structure and support static analysis.

Runtime validation protects the program when actual data may violate those expectations.

Production applications often need both.

---

## 96. Principle 4: Explicit Conversion Is Safer Than Assumption

When data crosses a system boundary, explicitly convert it into the representation required by internal code.

This reduces ambiguity and prevents repeated parsing.

---

## 97. Principle 5: Preserve Precision When Required

Use an appropriate numeric representation.

For decimal business values, `Decimal` may be preferable to `float`.

For exact rational quantities, `Fraction` may be preferable.

The correct type depends on the mathematical and business requirements.

---

# Real-World Applications

## 98. Web Applications

HTTP parameters are commonly received as strings.

Examples:

- page numbers
- quantities
- IDs
- filters
- Boolean options

These values require parsing and validation before business logic uses them.

---

## 99. APIs

JSON data must be transformed into appropriate internal Python types.

A robust API implementation validates:

- field presence
- field type
- permitted values
- numeric ranges
- textual formats
- nested structures

---

## 100. Databases

Database drivers may return different Python types depending on the column type and driver configuration.

Applications may normalize these into domain-specific representations.

Examples include converting:

- database numeric values to `Decimal`
- timestamps to timezone-aware `datetime`
- status codes to enums
- records to dataclasses or domain objects

---

## 101. Configuration

Environment variables are textual.

For example, an environment variable representing a timeout may contain:

    "30"

The application must convert it:

    int("30")

Boolean configuration values also require explicit parsing because:

    bool("false")

does not mean false.

---

## 102. Data Engineering

Large datasets often require conversion between:

- strings
- numbers
- dates
- lists
- dictionaries
- binary formats

Incorrect conversion can produce data corruption, precision loss, or silent inconsistencies.

Validation and normalization should therefore be explicit parts of ingestion pipelines.

---

## 103. Financial Systems

Financial applications often require decimal semantics.

Binary floating-point values can introduce representation differences for decimal fractions.

`Decimal` can provide more suitable arithmetic and controlled rounding behavior.

Financial systems should also define:

- precision
- scale
- rounding policy
- validation rules
- acceptable ranges
- serialization format

rather than relying on implicit conversion.

---

# Security Considerations

## 104. Secure Conversion Practices

Secure conversion should follow these principles:

1. Treat external input as untrusted.
2. Use narrow parsers.
3. Reject malformed input.
4. Apply domain constraints.
5. Apply reasonable input-size limits.
6. Avoid executable interpretation.
7. Avoid silently accepting unexpected formats.
8. Preserve error causes for diagnostics.
9. Normalize data before business processing.
10. Test malicious and pathological input cases.

---

# Performance Considerations

## 105. Performance Rules

Type checking and conversion are usually not major bottlenecks in ordinary programs.

Performance problems become more relevant when:

- millions of values are converted repeatedly
- very large inputs are processed
- conversions occur inside hot loops
- serialization is frequent
- expensive validation is duplicated

The preferred optimization strategy is:

1. design clean conversion boundaries
2. avoid redundant conversions
3. profile real workloads
4. optimize only demonstrated bottlenecks

Micro-optimizing `type()` versus `isinstance()` without profiling is rarely an appropriate application-level optimization.

---

# Testing Strategy

## 106. Recommended Test Categories

A production conversion function should normally test:

- valid input
- invalid input
- empty input
- whitespace
- boundary values
- negative values
- very large values
- `None`
- Boolean values
- subclass behavior
- malformed external representations
- special numeric values
- unexpected collection types

The script includes self-tests for Boolean parsing, age validation, numeric normalization, and order parsing.

---

# Core Terminology

## 107. Glossary

### Runtime Type

The actual class of an object during program execution.

### Type Checking

Determining whether an object has a particular type or satisfies a type relationship.

### Type Conversion

Producing a value in another representation or type.

### Parsing

Interpreting a textual or external representation according to a defined syntax.

### Coercion

Changing one value into another representation, often as part of an operation or conversion process.

### Type Annotation

Metadata expressing the intended type of a variable, parameter, return value, or attribute.

### Static Type Checking

Analyzing source code and type annotations without executing the program.

### Runtime Type Checking

Checking actual objects while the program executes.

### Type Narrowing

Reducing a union or broad type to a more specific type based on runtime or control-flow information.

### Subtyping

A relationship where one type can be used where another compatible base type is expected.

### Duck Typing

Behavior-oriented typing in which an object is used according to the operations it supports.

### Protocol

A structural interface describing required attributes or methods.

### Serialization

Converting an object or data structure into an external representation.

### Deserialization

Reconstructing a Python representation from serialized data.

### Validation

Determining whether a value satisfies the rules required by an application.

---

# Integrated Example

## 108. Customer Record Pipeline

The final integrated example combines the major concepts.

Raw data contains:

- customer ID
- name
- age
- active status
- balance

The parser performs:

1. runtime type checks
2. Boolean rejection where necessary
3. textual decimal conversion
4. finite-value validation
5. range validation
6. whitespace normalization
7. creation of an immutable domain representation

The result is a `CustomerRecord` object containing trusted, typed data.

This represents a practical pattern for converting external data into internal domain models.

---

# Script Structure

## 109. Main Areas Covered by the Python Script

The script demonstrates:

1. Python's runtime type model
2. basic built-in types
3. `type()`
4. `isinstance()`
5. `issubclass()`
6. inheritance
7. numeric conversion
8. string parsing
9. numeric bases
10. Boolean conversion
11. truthiness
12. Boolean text parsing
13. character and Unicode conversion
14. bytes and encoding
15. collection conversion
16. shallow conversion
17. copying
18. Decimal
19. Fraction
20. rounding and truncation
21. Enum and IntEnum
22. custom conversion protocols
23. `__bool__`
24. type annotations
25. `Optional`
26. union types
27. type narrowing
28. `Any`
29. `object`
30. type aliases
31. generics
32. protocols
33. overloads
34. type introspection
35. dataclass validation
36. runtime collection validation
37. JSON serialization
38. date and time conversion
39. duck typing
40. domain-specific conversion
41. exception handling
42. exception chaining
43. NaN and infinity
44. large integer behavior
45. performance measurement
46. security considerations
47. resource limits
48. common mistakes
49. edge cases
50. production validation pipelines
51. testing
52. real-world data normalization

---

# Practical Rules to Retain

## 110. Core Rules

1. `type(x)` tells you the exact runtime class.
2. `type(x) is T` requires exact class identity.
3. `isinstance(x, T)` normally works with subclasses.
4. `issubclass(C, T)` checks class inheritance.
5. `int()` performs actual integer conversion.
6. `cast()` does not perform runtime conversion.
7. `bool("false")` is `True`.
8. `bool` is a subclass of `int`.
9. `int(float_value)` truncates toward zero.
10. `Decimal` is useful for decimal arithmetic requiring appropriate precision semantics.
11. `Fraction` provides exact rational representation.
12. Type annotations do not automatically enforce runtime types.
13. External data should be validated.
14. Parsing and domain validation are separate stages.
15. `None` should normally be checked with `is None`.
16. `NaN` should be checked with `math.isnan()`.
17. `eval()` should not be used to parse untrusted data.
18. Collection conversion can change data semantics.
19. Generator conversion consumes the generator.
20. Static typing and runtime validation solve related but different problems.
