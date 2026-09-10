# Arithmetic operators in Python

## Topic introduction

Arithmetic operators are symbols and operations used to perform numerical calculations in Python. They form one of the foundations of programming because calculations appear in finance, statistics, scientific computing, engineering, data analysis, business applications, simulations, algorithms, and everyday software.

The primary binary arithmetic operators are:

| Operator | Name | Example | Result |
|---|---|---|---:|
| `+` | Addition | `10 + 3` | `13` |
| `-` | Subtraction | `10 - 3` | `7` |
| `*` | Multiplication | `10 * 3` | `30` |
| `/` | True division | `10 / 3` | `3.333...` |
| `//` | Floor division | `10 // 3` | `3` |
| `%` | Modulo | `10 % 3` | `1` |
| `**` | Exponentiation | `10 ** 3` | `1000` |

Python also provides unary arithmetic operators:

- `+x` applies unary plus.
- `-x` applies unary minus.

The accompanying Python script demonstrates these operators progressively, beginning with basic calculations and extending to numerical precision, financial formulas, custom numeric objects, parsing, validation, testing, and security considerations.

## Numeric values used in arithmetic

Python provides several built-in numeric types.

### Integers

`int` represents whole numbers.

Examples include:

- `0`
- `10`
- `-25`
- `1000000`

Python integers support arbitrary precision. Unlike fixed-width integer systems, ordinary Python integers do not overflow simply because a calculation becomes larger than the typical machine word size. They grow as necessary, subject to available system resources.

### Floating-point numbers

`float` represents floating-point numbers.

Examples:

- `3.14`
- `0.5`
- `-12.75`

Floating-point arithmetic is efficient and is appropriate for many scientific and engineering calculations. It is not an exact representation of every decimal fraction.

### Complex numbers

`complex` represents numbers with real and imaginary components.

For example:

`3 + 4j`

Python uses `j` for the imaginary component.

Complex numbers support operations such as addition, subtraction, multiplication, division, and exponentiation. Some operations, such as floor division and modulo, are not defined for complex numbers.

### Boolean values

`bool` is related to integer arithmetic because `bool` is a subclass of `int`.

Python evaluates:

- `True` numerically as `1`
- `False` numerically as `0`

Therefore, expressions such as `True + 4` produce `5`.

This behavior can be useful in carefully designed expressions, but explicit conversion or clearer logic is usually preferable when numerical meaning matters.

## Addition

The addition operator is `+`.

For numerical operands:

`10 + 3`

produces `13`.

Addition works with integers, floating-point values, complex numbers, and other objects that implement compatible arithmetic behavior.

The meaning of `+` is not restricted to numbers. For example, lists can be concatenated with `+`, and strings can also be concatenated. The actual behavior is determined by the operand types.

## Subtraction

The subtraction operator is `-`.

For example:

`10 - 3`

produces `7`.

Subtraction can produce negative values:

`3 - 10`

produces `-7`.

The same symbol is also used as a unary operator. If `x` is `15`, then `-x` produces `-15`.

## Multiplication

The multiplication operator is `*`.

For numerical values:

`6 * 4`

produces `24`.

Multiplication also has type-specific behavior. For example, multiplying a string by an integer repeats the string:

`"abc" * 3`

produces three repetitions of the string.

This illustrates an important Python principle: operators are interpreted according to the types involved.

## True division

The `/` operator performs true division.

For example:

`7 / 2`

produces `3.5`.

Even when both operands are integers, `/` normally produces a floating-point result:

`10 / 2`

produces `5.0`.

Division by zero raises `ZeroDivisionError`.

This exception should be prevented or handled when the denominator can originate from variable or external input.

## Floor division

The `//` operator performs floor division.

For positive operands:

`10 // 3`

produces `3`.

The important distinction is that floor division rounds toward negative infinity rather than simply truncating toward zero.

For example:

`-7 // 2`

produces `-4`.

This differs from:

`int(-7 / 2)`

which produces `-3`.

The mathematical relationship is:

`a // b = floor(a / b)`

for the relevant numeric behavior.

Floor division is useful when a calculation requires complete groups, buckets, pages, units, or other quantities where the fractional remainder should be discarded according to floor semantics.

## Modulo

The `%` operator returns the remainder associated with division.

For example:

`10 % 3`

produces `1`.

Modulo is commonly used for:

- checking divisibility
- determining even and odd numbers
- extracting digits
- cyclic calculations
- circular indexing
- clock arithmetic
- repeating patterns

A number is even when:

`number % 2 == 0`

The relationship between floor division and modulo can be expressed as:

`a == (a // b) * b + (a % b)`

For negative values, the sign behavior follows Python's floor-division rules, so it is important not to assume that modulo behaves like truncation-based remainder operations from every other programming language.

## Exponentiation

The `**` operator performs exponentiation.

Examples include:

`2 ** 3`

which produces `8`, and:

`5 ** 2`

which produces `25`.

An exponent of zero produces `1` for ordinary nonzero bases.

Negative exponents represent reciprocal powers:

`2 ** -1`

produces `0.5`.

Exponentiation can also be used for roots:

`9 ** 0.5`

calculates a square root.

For more specialized mathematical work, the `math` and `cmath` modules provide dedicated functions such as `math.sqrt()` and `cmath.sqrt()`.

## Unary arithmetic operators

Unary operators operate on one operand.

### Unary plus

`+x`

generally preserves the numerical value of `x`.

### Unary minus

`-x`

changes the sign of the value.

For example:

`-(-10)`

produces `10`.

Unary operators are important when expressions contain explicitly signed values or when a calculation needs to invert a value.

## Operator precedence

When multiple arithmetic operators appear in one expression, Python follows precedence rules.

For example:

`2 + 3 * 4`

produces `14`, not `20`, because multiplication has higher precedence than addition.

Parentheses override the default precedence:

`(2 + 3) * 4`

produces `20`.

A practical rule is to use parentheses when they make an expression easier to understand, especially in production code.

## Associativity

Associativity determines how operators with the same precedence are grouped.

Subtraction and division are normally evaluated from left to right.

For example:

`20 - 5 - 3`

is interpreted as:

`(20 - 5) - 3`

and produces `12`.

It is not equivalent to:

`20 - (5 - 3)`

Exponentiation is right-associative.

Therefore:

`2 ** 3 ** 2`

means:

`2 ** (3 ** 2)`

and produces `512`.

It is different from:

`(2 ** 3) ** 2`

which produces `64`.

## Augmented arithmetic assignment

Python provides augmented assignment operators that combine an arithmetic operation with assignment.

Examples include:

- `+=`
- `-=`
- `*=`
- `/=`
- `//=`
- `%=`
- `**=`

For example:

`value += 5`

is conceptually equivalent to updating `value` using addition.

Augmented assignment is useful when repeatedly updating a value such as a counter, accumulator, balance, or running total.

The exact implementation behavior can depend on the object's type because Python's data model allows types to customize these operations.

## Mixed numeric types

Python allows many arithmetic operations between compatible numeric types.

For example:

`10 + 2.5`

produces a floating-point result.

Complex values can also interact with real numeric values:

`(2 + 3j) + 5`

produces a complex number.

Not every combination is supported. Complex numbers, for example, do not define ordering in the same way as real numbers and do not support floor division or modulo.

Understanding the type of each operand is therefore important when designing calculations.

## Floating-point precision

Floating-point values use a binary representation. Many decimal fractions cannot be represented exactly in binary floating-point.

A classic example is:

`0.1 + 0.2`

which does not necessarily compare equal to:

`0.3`

using exact equality.

This does not mean Python is incorrectly performing arithmetic. It reflects the representation used by binary floating-point numbers.

For approximate comparisons, `math.isclose()` is usually more appropriate than direct equality.

For example, the script demonstrates comparison using:

`math.isclose(0.1 + 0.2, 0.3)`

The appropriate tolerance depends on the application and numerical scale.

## Decimal arithmetic

The `decimal.Decimal` type provides decimal arithmetic based on a decimal representation and configurable arithmetic context.

It is useful when decimal precision and predictable decimal rounding are important, particularly in applications such as financial calculations.

A good practice is to construct `Decimal` values from strings when the input represents an exact decimal quantity.

For example:

`Decimal("0.1")`

preserves the intended decimal value more directly than constructing a `Decimal` from a binary floating-point value.

The script demonstrates:

- Decimal addition
- Decimal multiplication
- percentage calculations
- tax calculations
- monetary totals
- explicit rounding with `quantize()`
- decimal precision context

Decimal arithmetic still requires careful control of precision and rounding rules.

## Fraction arithmetic

The `fractions.Fraction` class provides exact rational arithmetic.

For example:

`Fraction(1, 3) + Fraction(1, 6)`

produces the exact rational value `1/2`.

Fractions are particularly useful when exact rational results matter.

The script demonstrates:

- addition
- subtraction
- multiplication
- division
- automatic fraction reduction
- conversion from exact decimal strings

Fractions may require more computational and memory resources than primitive floating-point arithmetic, so they should be selected when exact rational representation provides a meaningful benefit.

## Complex arithmetic

Complex numbers contain:

- a real component
- an imaginary component

For example:

`2 + 3j`

The script demonstrates:

- addition
- subtraction
- multiplication
- division
- exponentiation
- magnitude
- complex square roots

The `cmath` module is appropriate for mathematical functions involving complex values.

Complex arithmetic is relevant to electrical engineering, signal processing, control systems, physics, numerical methods, and other technical fields.

## Numeric conversion

Python provides explicit numeric conversion functions such as:

- `int()`
- `float()`
- `complex()`

Conversion is not the same as arithmetic.

For example:

`int(7.9)`

produces `7`.

For negative values:

`int(-7.9)`

produces `-7`.

This is truncation toward zero rather than mathematical floor.

Therefore:

`int(-3.9)`

is different from:

`math.floor(-3.9)`

which produces `-4`.

Understanding the distinction prevents subtle errors in calculations involving negative quantities.

## Common arithmetic patterns

Arithmetic operators appear in many basic algorithms.

### Even and odd detection

Modulo can determine parity:

`number % 2 == 0`

indicates an even number.

### Digit extraction

For an integer:

`number % 10`

extracts its final decimal digit.

`number // 10`

removes the final decimal digit.

These operations are useful in digit-processing algorithms.

### Time conversion

Seconds can be converted into hours, minutes, and seconds using floor division and modulo.

For example:

- hours use `// 3600`
- remaining seconds use `% 3600`
- minutes use `// 60`
- remaining seconds use `% 60`

### Percentages

A percentage can be calculated as:

`obtained / maximum * 100`

The denominator must be checked to prevent division by zero.

## Practical mathematical formulas

Arithmetic operators form the computational basis of many formulas.

The script implements examples including:

- simple interest
- compound interest
- rectangle area
- circle area
- BMI
- percentage change
- geometric distance
- statistical averages

The important programming principle is to translate a mathematical formula into small, clearly named expressions rather than hiding complex calculations in unnecessarily dense code.

## Financial calculations

Arithmetic is central to financial software.

### Simple interest

The script uses:

`principal * rate * time`

where the percentage rate is converted into decimal form.

### Compound interest

Compound growth follows a power-based formula:

`P * (1 + r / n) ** (n * t)`

where:

- `P` is principal
- `r` is annual rate as a decimal
- `n` is the number of compounding periods per year
- `t` is time

### EMI

The script implements a standard fixed-rate loan EMI calculation.

The monthly payment is based on:

`P * r * (1 + r)^n / ((1 + r)^n - 1)`

where:

- `P` is the principal
- `r` is the monthly interest rate
- `n` is the number of monthly payments

Special handling is required when the interest rate is zero because the standard formula contains a division by an expression that becomes zero.

Financial calculations also require careful decisions about rounding, currency representation, compounding conventions, and regulatory or business rules.

## Statistical arithmetic

Arithmetic operators support statistical calculations.

The script demonstrates:

- sum
- count
- arithmetic mean
- weighted average

The arithmetic mean is:

`sum(values) / count`

A weighted average is:

`sum(value * weight) / sum(weights)`

Input validation is important because an empty dataset or zero total weight makes these formulas undefined.

## Compound calculations

Real applications frequently combine several arithmetic operations.

For example, a commercial calculation may:

1. start with an original price
2. calculate a discount
3. subtract the discount
4. calculate tax on the discounted price
5. add the tax
6. round the final amount

The script uses `Decimal` for this type of decimal-sensitive calculation.

Breaking the calculation into intermediate variables improves readability, debugging, and auditing.

## Geometry and arithmetic

Geometric formulas are composed of arithmetic operations.

The script calculates Euclidean distance between two points using:

`sqrt((x2 - x1)^2 + (y2 - y1)^2)`

This demonstrates the relationship between:

- subtraction
- exponentiation
- addition
- square roots

Arithmetic expressions therefore frequently form larger mathematical algorithms.

## Modulo in cyclic systems

Modulo is especially useful when values wrap around.

For a 24-hour clock:

`(current_hour + hours_later) % 24`

keeps the result inside the range from `0` through `23`.

Modulo can also implement circular array indexing.

For an array of length `n`, an index can be wrapped using:

`index % n`

This technique appears in scheduling, simulations, ring buffers, circular queues, and repeating patterns.

## Powers and roots

Roots can be expressed using fractional exponents.

A square root can be represented as:

`x ** 0.5`

A dedicated function such as:

`math.sqrt(x)`

is generally clearer when specifically calculating a square root.

For exact integer square-root calculations, `math.isqrt()` is useful because it returns the integer floor of the square root without converting the value to floating point.

## Rounding

Rounding is separate from basic arithmetic but is important when arithmetic results must be represented at a particular precision.

Python's `round()` operates according to Python's rounding behavior and the underlying numeric representation.

Floating-point representation can make decimal-looking values behave unexpectedly.

For decimal-sensitive applications, `Decimal.quantize()` provides explicit decimal rounding control.

The rounding strategy should be selected according to the application's numerical requirements rather than applied automatically to every intermediate result.

## Operator module

Python's `operator` module exposes arithmetic operations as functions.

Examples include:

- `operator.add`
- `operator.sub`
- `operator.mul`
- `operator.truediv`
- `operator.floordiv`
- `operator.mod`
- `operator.pow`

This is useful when an operation needs to be stored in a variable, passed into a function, selected dynamically, or used in a dispatch table.

The script demonstrates a dictionary mapping operator symbols to functions.

This approach is generally safer than dynamically executing arbitrary source code.

## Operator overloading

Python allows classes to define how arithmetic operators behave.

Important special methods include:

| Operator | Special method |
|---|---|
| `+` | `__add__()` |
| `-` | `__sub__()` |
| `*` | `__mul__()` |
| `/` | `__truediv__()` |
| `//` | `__floordiv__()` |
| `%` | `__mod__()` |
| `**` | `__pow__()` |

The script defines a `Measurement` class that implements selected arithmetic operations.

This allows expressions such as adding two compatible `Measurement` objects.

Operator overloading should represent a natural mathematical relationship. Overloading `+` with an unrelated meaning can make code difficult to understand.

## Reflected arithmetic methods

Python also supports reflected arithmetic methods.

Examples include:

- `__radd__()`
- `__rsub__()`
- `__rmul__()`
- `__rtruediv__()`

These methods help custom objects participate in expressions where the custom object appears on the right-hand side.

For example:

`3 * measurement`

may invoke a reflected multiplication method when the left operand cannot directly perform the operation with the custom object.

Returning `NotImplemented` from an unsupported arithmetic method is an important part of Python's operator protocol because it allows Python to attempt an appropriate alternative operation.

## Error handling

Arithmetic can fail for several reasons.

### Division by zero

Operations such as:

`10 / 0`

raise `ZeroDivisionError`.

The same general issue applies to floor division and modulo with zero divisors.

### Invalid types

An expression involving incompatible types can raise `TypeError`.

For example, attempting numerical addition between a string and an integer is not a valid arithmetic operation.

### Invalid numeric input

User-provided text must be validated before it is used in arithmetic.

The script demonstrates conversion through controlled parsing and rejects non-finite values when finite numbers are required.

## Edge cases

Important arithmetic edge cases include:

- division by zero
- modulo by zero
- negative operands
- zero powers
- negative powers
- very large integers
- floating-point rounding
- infinity
- NaN
- incompatible operand types
- complex-number restrictions

Edge cases should be tested explicitly because arithmetic that works for ordinary positive values may behave differently around zero or negative numbers.

## Infinity and NaN

Floating-point arithmetic supports special values including:

- positive infinity
- negative infinity
- NaN, meaning "not a number"

Infinity participates in many arithmetic operations according to IEEE-style floating-point behavior.

NaN has unusual comparison semantics. In particular, a NaN value is not equal to itself.

The appropriate way to detect NaN is:

`math.isnan(value)`

Applications that process external numerical data should consider how non-finite values are handled before calculations are performed.

## Large integer arithmetic

Python's `int` supports arbitrary-precision integer arithmetic.

For example:

`2 ** 1000`

can be calculated without ordinary fixed-width integer overflow.

The practical limits are determined by computational resources and implementation constraints.

Very large integer calculations can still consume substantial CPU time and memory. Arbitrary precision removes many overflow concerns but does not make extremely large calculations computationally free.

## Expression parsing

A calculator that accepts expressions such as:

`2 + 3 * 4`

must understand numerical tokens, operators, precedence, associativity, and parentheses.

The script includes an educational arithmetic parser that supports:

- numbers
- parentheses
- unary plus
- unary minus
- addition
- subtraction
- multiplication
- division
- floor division
- modulo
- exponentiation

The parser processes the expression according to arithmetic precedence rather than passing the expression directly to Python's `eval()`.

This demonstrates the conceptual structure behind a basic arithmetic expression evaluator.

## Security considerations

Unrestricted `eval()` should not be used to evaluate untrusted user input.

An arithmetic expression entered by a user is still text that could contain constructs unrelated to arithmetic. Passing arbitrary input to an execution mechanism can therefore create a code-execution vulnerability.

A safer design is to:

- tokenize input
- explicitly recognize permitted operators
- validate numeric literals
- construct an expression representation
- evaluate only supported operations
- reject unsupported syntax
- impose appropriate limits on expression size and computational complexity

The script's parser demonstrates the core idea of restricting evaluation to an explicitly defined arithmetic grammar.

## Input validation

Arithmetic functions should validate their assumptions.

Examples include:

- checking that a denominator is not zero
- checking that a radius is not negative
- checking that a loan principal is positive
- checking that a time period is valid
- checking that weights have the expected length
- checking that total weight is not zero
- checking that percentage values are within valid ranges

Validation should occur close to the boundary where untrusted or uncertain input enters the system.

## Complex expressions and readability

A mathematically valid expression can still be difficult to maintain if it is excessively dense.

For example, a large expression can be divided into named intermediate values.

This provides several benefits:

- easier debugging
- easier testing
- clearer intent
- easier review
- easier modification
- better error isolation

The script demonstrates both direct expressions and equivalent calculations broken into intermediate steps.

## Testing arithmetic

Arithmetic functions should be tested using normal cases and edge cases.

The script includes assertions for:

- addition
- subtraction
- multiplication
- division
- floor division
- modulo
- exponentiation
- floating-point results
- circle area
- fractions
- decimals
- expression precedence
- exponentiation associativity

Floating-point results are tested using approximate comparison rather than requiring exact binary equality.

A robust test suite should also test:

- zero
- negative values
- very large values
- invalid input
- division by zero
- boundary values
- unexpected operand types

## Performance considerations

Primitive arithmetic on Python numeric types is generally efficient, but the cost of arithmetic depends on the numeric type and the size of the values.

Typical considerations include:

- integers grow in size as their magnitude increases
- floating-point operations use fixed-size representations
- `Decimal` provides decimal arithmetic but can have different performance characteristics
- `Fraction` maintains exact rational values and can involve larger numerator and denominator values
- complex arithmetic requires operations on both real and imaginary components

The script includes a small `timeit` demonstration comparing representative integer and floating-point multiplication.

Microbenchmark results depend on the machine, Python implementation, interpreter state, and system load. Correctness and appropriate numerical representation should normally take priority over small arithmetic performance differences.

## Important distinctions

### `/` versus `//`

`/` performs true division.

`//` performs floor division.

For positive numbers they can appear similar when the result is an integer, but their result types and behavior for fractional results differ.

Negative values make the distinction especially important.

### `//` versus `int(a / b)`

`//` uses floor semantics.

`int()` truncates toward zero when converting a floating-point result to an integer.

Therefore:

`-7 // 2`

and:

`int(-7 / 2)`

produce different results.

### `%` versus percentage notation

Python's `%` is the modulo operator. It does not directly mean "percent."

A percentage calculation generally uses arithmetic such as:

`value / total * 100`

The same `%` symbol is therefore not a percentage operator in Python.

### `**` versus multiplication

`x * x` multiplies two copies of `x`.

`x ** 2` expresses exponentiation.

Both can calculate a square, but exponentiation generalizes naturally to other powers.

### `float` versus `Decimal`

`float` is generally appropriate for many numerical calculations where binary floating-point precision is acceptable.

`Decimal` is more appropriate when exact decimal representation and controlled decimal rounding are important.

### `float` versus `Fraction`

`float` is compact and efficient for many numerical workloads.

`Fraction` provides exact rational arithmetic but may grow substantially in complexity for repeated calculations.

## Common mistakes

### Forgetting precedence

An expression such as:

`2 + 3 * 4`

does not mean:

`(2 + 3) * 4`

Parentheses should be used when the intended evaluation order differs from the standard precedence rules.

### Assuming floor division truncates

For negative values, `//` does not simply discard the fractional portion toward zero.

### Comparing floats with exact equality

Expressions involving floating-point calculations should generally be compared using an appropriate tolerance when exact representation is not guaranteed.

### Ignoring zero denominators

Division, floor division, and modulo require nonzero divisors.

### Using the wrong numeric type

Using `float` for every problem can introduce precision issues. Using `Fraction` or `Decimal` unnecessarily can increase computational cost or complexity.

### Writing unreadable expressions

A mathematically correct expression can still be poor production code if its purpose is difficult to understand.

Intermediate variables can make important calculations clearer.

### Using unrestricted expression evaluation

Passing arbitrary user input to `eval()` creates a security risk. A calculator should explicitly define and validate its supported syntax.

## Best practices

1. Choose the numeric type according to the precision requirements.
2. Use parentheses when they improve clarity.
3. Validate denominators before division and modulo.
4. Handle expected arithmetic exceptions explicitly.
5. Use `math.isclose()` for appropriate floating-point comparisons.
6. Use `Decimal` for decimal-sensitive calculations where its semantics are appropriate.
7. Use `Fraction` when exact rational arithmetic is required.
8. Break complicated formulas into meaningful intermediate values.
9. Test zero, negative, boundary, and invalid inputs.
10. Avoid unrestricted `eval()` for untrusted expressions.
11. Use named functions for reusable calculations.
12. Keep arithmetic logic separate from input and presentation logic.
13. Document unusual mathematical assumptions.
14. Apply rounding at the appropriate business or presentation boundary rather than prematurely rounding every intermediate result.
15. Consider computational cost when working with extremely large integers or exact numerical types.

## Implementation considerations

A production arithmetic component should normally separate several responsibilities:

- input validation
- parsing
- numerical computation
- error handling
- formatting
- persistence or external integration

For example, a financial calculation should not combine raw user-input parsing, currency formatting, database access, and mathematical formulas into one large function.

Separating these concerns makes the arithmetic easier to test and audit.

## Real-world relevance

Arithmetic operators are fundamental to:

- financial applications
- banking systems
- accounting software
- statistical analysis
- data analytics
- scientific computing
- engineering calculations
- physics simulations
- graphics
- game development
- business metrics
- inventory systems
- billing systems
- loan calculators
- tax calculations
- scheduling systems
- numerical algorithms
- machine learning computations
- computer simulations
- measurement systems

Even sophisticated software systems ultimately depend on reliable numerical operations for many of their calculations.

## Script structure

The Python study script progresses through:

- numeric values and types
- addition
- subtraction
- multiplication
- true division
- floor division
- modulo
- exponentiation
- unary operators
- precedence
- associativity
- mixed numeric types
- floating-point precision
- decimal arithmetic
- fraction arithmetic
- complex arithmetic
- numeric conversions
- common arithmetic patterns
- practical mathematical formulas
- EMI calculations
- the `operator` module
- operator overloading
- reflected operations
- error handling
- edge cases
- infinity and NaN
- statistical arithmetic
- compound calculations
- complex expressions
- augmented assignment
- arithmetic with conditions
- modulo applications
- powers and roots
- geometry
- percentage change
- rounding
- performance
- large integers
- input validation
- expression safety
- expression parsing
- parser edge cases
- testing
- common mistakes
- best practices
- operator comparison
- a reusable mini calculator

Each section contains executable examples so that the arithmetic concepts can be observed directly through Python behavior.
