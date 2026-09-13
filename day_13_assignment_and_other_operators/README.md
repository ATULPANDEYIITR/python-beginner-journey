# Assignment and Other Operators in Python

## Introduction

Operators are symbols or keywords that tell Python to perform an operation on one or more values. They form the foundation of calculations, comparisons, decision-making, data manipulation, object behavior, and many programming algorithms.

This study script provides a systematic treatment of Python assignment operators and other major operator categories. It begins with simple variable assignment and progresses through augmented assignment, unpacking, arithmetic, comparison, logical, identity, membership, bitwise, conditional, collection-specific, matrix multiplication, assignment expressions, and custom operator overloading.

The examples are executable and are organized so that individual concepts can be studied independently.

## Assignment operators

The basic assignment operator is `=`.

An assignment binds a name to an object:

    age = 25

The right-hand side is evaluated first. The resulting object is then associated with the name on the left-hand side.

Assignment is not mathematical equality. The following statement:

    x = 10

means that the name `x` is bound to the object representing `10`.

A comparison uses `==`:

    x == 10

This produces a Boolean result.

### Basic assignment

The script demonstrates assignments involving integers, strings, floating-point values, and Boolean values. A variable can be reassigned later:

    age = 25
    age = 26

The second statement changes the object to which `age` is bound.

Python variables are names rather than fixed storage containers with permanently declared types. A name can be rebound to an object of another type:

    value = 10
    value = "Python"

The same name can therefore refer to different object types at different points in a program.

## Multiple assignment

Python supports assigning several values in a single statement:

    first, second, third = 10, 20, 30

The values on the right are unpacked and assigned to the names on the left.

The number of targets normally has to match the number of supplied values. An incorrect number of values raises `ValueError`.

Multiple assignment is useful when initializing related variables and when working with structured data.

## Chained assignment

Python permits:

    x = y = z = 0

The same resulting object is assigned to all three names.

This is safe for immutable objects such as integers. Care is required with mutable objects:

    first = second = []

    first.append("value")

Both names refer to the same list, so both observe the modification.

If independent mutable objects are required, create them separately:

    first = []
    second = []

This distinction is important when using lists, dictionaries, sets, and other mutable objects.

## Unpacking assignment

Iterable objects can be unpacked into multiple variables:

    coordinates = (10, 20)
    x, y = coordinates

The elements are assigned from left to right.

Lists, tuples, strings, and many other iterable objects can participate in unpacking.

A mismatch between the number of values and targets normally produces `ValueError`.

## Extended iterable unpacking

The starred assignment target collects remaining values:

    first, *middle, last = [1, 2, 3, 4, 5]

The result is:

    first = 1
    middle = [2, 3, 4]
    last = 5

The starred target always receives a list.

It may also receive zero elements:

    first, *remaining = [99]

Here `remaining` becomes an empty list.

Extended unpacking is useful when the number of intermediate elements is variable.

## Swap assignment

Python provides a clear way to exchange two values:

    left, right = right, left

No explicit temporary variable is required.

This works because the right-hand side is evaluated before the assignments are performed.

The approach is generally clearer than implementing a manual temporary-variable or XOR-based swap.

## Augmented assignment

Augmented assignment combines an operation with assignment.

Common forms include:

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

For example:

    value = 10
    value += 5

is conceptually similar to:

    value = value + 5

The exact implementation behavior can depend on the object's special methods and mutability.

## Augmented assignment and mutable objects

A significant detail is that augmented assignment can use in-place operations when the object supports them.

For example:

    values = [1, 2]
    values += [3, 4]

Lists commonly modify themselves in place.

Immutable objects such as tuples cannot be modified in place. An expression such as:

    values = (1, 2)
    values += (3, 4)

results in a new tuple being created and bound to the name.

This difference matters when other variables reference the original object.

## Assignment expressions

Python provides the assignment expression operator:

    :=

It is commonly called the walrus operator.

Unlike normal assignment, an assignment expression both assigns a value and produces that value as part of a larger expression.

Example:

    if (length := len("Python")) > 5:
        print(length)

The calculated length is assigned to `length` and then used by the comparison.

Assignment expressions can reduce repeated calculations, particularly in conditions and loops.

They should be used when they improve clarity. Excessive use can make expressions difficult to read.

## Arithmetic operators

Arithmetic operators perform numerical operations.

The principal arithmetic operators demonstrated by the script are:

| Operator | Meaning |
|---|---|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | True division |
| `//` | Floor division |
| `%` | Modulo |
| `**` | Exponentiation |
| `@` | Matrix multiplication |

Unary operators include:

| Operator | Meaning |
|---|---|
| `+x` | Unary positive |
| `-x` | Unary negative |

### Addition

The `+` operator adds numeric values:

    10 + 5

It can also be overloaded by other data types. Strings use `+` for concatenation:

    "Py" + "thon"

Lists can also be concatenated:

    [1, 2] + [3, 4]

The meaning of an operator depends on the operand types.

### Subtraction

The `-` operator subtracts numeric values:

    10 - 5

For custom classes, subtraction can be implemented using `__sub__`.

### Multiplication

The `*` operator performs numerical multiplication:

    10 * 5

It also has sequence-specific behavior:

    "ha" * 3

produces repeated text.

Similarly:

    [1, 2] * 3

creates a repeated list.

Care is required with nested mutable objects because repetition copies references rather than recursively cloning mutable objects.

### True division

The `/` operator performs true division:

    10 / 4

The result is a floating-point value.

Division by zero raises `ZeroDivisionError`.

### Floor division

The `//` operator performs floor division.

For positive numbers:

    7 // 2

produces `3`.

Floor division is not simply truncation toward zero. It rounds toward negative infinity:

    -7 // 2

produces `-4`.

This distinction is important when working with negative values.

### Modulo

The `%` operator returns the remainder associated with floor division:

    7 % 2

produces `1`.

Python maintains the relationship:

    a == (a // b) * b + (a % b)

when the divisor is nonzero.

Modulo is commonly used for divisibility tests, cyclic calculations, indexing patterns, and periodic logic.

### Exponentiation

The `**` operator performs exponentiation:

    2 ** 5

produces `32`.

Exponentiation is right-associative:

    2 ** 3 ** 2

is interpreted as:

    2 ** (3 ** 2)

not:

    (2 ** 3) ** 2

## Comparison operators

Comparison operators produce Boolean results.

| Operator | Meaning |
|---|---|
| `==` | Equal |
| `!=` | Not equal |
| `<` | Less than |
| `<=` | Less than or equal |
| `>` | Greater than |
| `>=` | Greater than or equal |

For example:

    score >= 50

produces either `True` or `False`.

Comparisons are fundamental to validation, filtering, branching, sorting, and algorithmic decisions.

## Comparison chaining

Python supports chained comparisons:

    18 <= age < 60

This is equivalent in meaning to:

    18 <= age and age < 60

The chained form is concise and usually easier to read.

Chained comparisons can also express ranges naturally:

    0 <= score <= 100

This is useful for validation.

## Logical operators

Python provides three logical operators:

| Operator | Meaning |
|---|---|
| `and` | Logical conjunction |
| `or` | Logical disjunction |
| `not` | Logical negation |

For example:

    is_logged_in and has_permission

requires both operands to be truthy.

The `or` operator is commonly used when a fallback value is needed:

    display_name = user_name or "Guest"

The behavior is based on truthiness.

## Short-circuit evaluation

Python evaluates `and` and `or` using short-circuit rules.

For:

    A and B

if `A` is falsy, Python does not evaluate `B`.

For:

    A or B

if `A` is truthy, Python does not evaluate `B`.

This has practical consequences.

For example:

    denominator != 0 and 100 / denominator > 1

is safe because the division is not evaluated when `denominator` is zero.

Short-circuit evaluation is useful for efficient conditions and safe access patterns.

## Logical operators return operands

A subtle but important property is that `and` and `or` do not necessarily return `True` or `False`.

For example:

    "Python" and 100

returns `100`.

Similarly:

    "" or "Guest"

returns `"Guest"`.

The operators return one of their operands according to truthiness rules.

This behavior is frequently used for default values, although explicit conditional logic may be clearer when the requirement is complex.

## Truthiness

Python objects have truth values.

Common falsy values include:

- `False`
- `None`
- `0`
- `0.0`
- `""`
- empty lists
- empty tuples
- empty dictionaries
- empty sets

Most other objects are truthy unless their type defines different behavior.

The `bool()` function can explicitly convert an object to a Boolean value.

## Identity operators

Python has two identity operators:

    is
    is not

They test whether two references point to the same object.

They do not test whether two objects merely have equal values.

For example:

    first = [1, 2]
    second = [1, 2]

The expressions:

    first == second

and:

    first is second

have different meanings.

The first compares values. The second compares object identity.

`is` is particularly appropriate for singleton checks such as:

    value is None

The common mistake of writing:

    value == None

should generally be replaced with:

    value is None

## Equality versus identity

Equality asks whether two objects should be considered equivalent according to their equality behavior.

Identity asks whether they are literally the same object.

This distinction becomes especially important with mutable data structures and custom classes.

Use:

    ==

for value comparison.

Use:

    is

for identity checks, especially singleton checks such as `None`.

## Membership operators

Membership operators are:

    in
    not in

They test whether a value is contained in a collection or supported iterable.

Examples include:

    20 in [10, 20, 30]

and:

    "Python" in "Python programming"

For dictionaries, membership normally checks keys:

    "name" in user

does not search dictionary values.

For repeated membership tests, the choice of container matters significantly. Lists generally require a linear search, while sets and dictionaries provide average constant-time membership operations.

## Bitwise operators

Bitwise operators operate on the binary representation of integers.

| Operator | Meaning |
|---|---|
| `&` | Bitwise AND |
| `|` | Bitwise OR |
| `^` | Bitwise XOR |
| `~` | Bitwise NOT |
| `<<` | Left shift |
| `>>` | Right shift |

For example:

    12 & 10

performs a bit-by-bit AND operation.

The script uses `bin()` to display binary representations so that the operations can be understood at the bit level.

## Bitwise AND

The `&` operator sets a bit in the result only when the corresponding bit is set in both operands.

It is frequently used for:

- bit masks
- permissions
- feature flags
- binary protocols
- low-level data processing

## Bitwise OR

The `|` operator sets a result bit when either corresponding operand has that bit set.

A common application is combining flags:

    permissions = READ | WRITE

## Bitwise XOR

The `^` operator sets a bit when the corresponding bits differ.

Important properties include:

    x ^ 0 == x

and:

    x ^ x == 0

XOR is useful in checksums, bit manipulation, flags, and some algorithmic techniques.

Although XOR can theoretically be used for swapping variables, ordinary Python tuple assignment is clearer and safer.

## Bitwise NOT

The `~` operator complements the integer's bits.

Python integers use signed arbitrary-precision representation, so expressions involving `~` can produce results that may look different from fixed-width unsigned integer systems.

For example:

    ~12

produces `-13`.

The mathematical relationship for Python integers is:

    ~x == -x - 1

## Bit shifts

The left-shift operator moves bits toward higher positions:

    x << n

The right-shift operator moves bits toward lower positions:

    x >> n

For positive integers, a left shift by one position corresponds to multiplication by two, while a right shift by one position corresponds to floor division by two.

Bit shifts are useful in low-level programming, encoding, masks, and performance-sensitive integer operations.

## Conditional expressions

Python supports a conditional expression:

    value_if_true if condition else value_if_false

Example:

    category = "adult" if age >= 18 else "minor"

It is useful for short expressions where a complete `if` statement would be unnecessarily verbose.

Nested conditional expressions should be used cautiously because excessive nesting can reduce readability.

## Operator precedence

When several operators occur in the same expression, Python follows precedence rules.

A simplified ordering from higher to lower precedence is:

1. Parentheses
2. Exponentiation
3. Unary operators
4. Multiplication, division, floor division, modulo
5. Addition and subtraction
6. Shifts
7. Bitwise AND
8. Bitwise XOR
9. Bitwise OR
10. Comparisons, membership, identity
11. `not`
12. `and`
13. `or`
14. Conditional expressions
15. Assignment expressions

Normal assignment using `=` is not an ordinary arithmetic expression operator.

For example:

    2 + 3 * 4

is evaluated as:

    2 + (3 * 4)

so the result is `14`.

Parentheses can explicitly communicate intended grouping:

    (2 + 3) * 4

which produces `20`.

Even when the precedence rules are known, parentheses are often appropriate when they make business logic or mathematical intent clearer.

## Associativity

Associativity determines how operators of the same precedence are grouped.

Many arithmetic operations associate from left to right.

For example:

    100 / 10 / 2

is interpreted as:

    (100 / 10) / 2

Exponentiation is an important exception because it associates from right to left:

    2 ** 3 ** 2

means:

    2 ** (3 ** 2)

Understanding associativity prevents subtle expression errors.

## Boolean values and numbers

Python's `bool` type is a subclass of `int`.

Consequently:

    True == 1

and:

    False == 0

are true comparisons.

Boolean values can participate in arithmetic:

    True + True

produces `2`.

This can be useful for counting Boolean conditions:

    sum([True, False, True])

produces `2`.

Although valid, this behavior should be used deliberately so that the code remains understandable.

## Floating-point precision

Floating-point arithmetic can produce surprising results because many decimal fractions cannot be represented exactly in binary floating-point format.

For example:

    0.1 + 0.2

does not necessarily produce a binary representation exactly equal to `0.3`.

Therefore:

    0.1 + 0.2 == 0.3

may be `False`.

For approximate numerical comparisons, `math.isclose()` is often more appropriate.

For exact decimal financial calculations, `Decimal` can be preferable:

    Decimal("0.1") + Decimal("0.2")

The use of strings when constructing `Decimal` values avoids first introducing binary floating-point approximation.

## Division by zero

The following operations raise `ZeroDivisionError` when the divisor is zero:

- `/`
- `//`
- `%`

Production programs should validate inputs or explicitly handle the exception where zero is a valid possibility.

The script demonstrates exception handling around these operations.

## Operator functions

The `operator` module provides callable equivalents of many operators.

Examples include:

    operator.add
    operator.sub
    operator.mul
    operator.truediv
    operator.eq
    operator.lt

This is useful when an operation needs to be passed as a function.

For example, an operation table can map symbols to callable functions:

    {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul
    }

This approach is useful for calculators, dispatch systems, transformation pipelines, and configurable algorithms.

## Operator overloading

Python allows classes to define how operators behave for their objects.

Special methods control operator behavior.

Examples include:

| Special method | Common operator |
|---|---|
| `__add__` | `+` |
| `__sub__` | `-` |
| `__mul__` | `*` |
| `__truediv__` | `/` |
| `__floordiv__` | `//` |
| `__mod__` | `%` |
| `__pow__` | `**` |
| `__eq__` | `==` |
| `__lt__` | `<` |
| `__le__` | `<=` |
| `__gt__` | `>` |
| `__ge__` | `>=` |
| `__contains__` | `in` |
| `__matmul__` | `@` |

The `Money` class in the script demonstrates custom addition, subtraction, multiplication, equality, and comparison.

This allows domain-specific objects to behave naturally.

## Returning `NotImplemented`

Custom operator methods often return `NotImplemented` when they do not support the operand type.

This is preferable to blindly assuming that the other object has the expected structure.

Returning `NotImplemented` allows Python's operator dispatch mechanism to attempt an appropriate reflected operation or eventually raise a suitable exception.

## Reflected operators

Some operations have reflected special methods.

For example:

    __mul__
    __rmul__

The `Money` example implements `__rmul__` so that:

    2 * money

can work naturally.

This is important when designing custom numeric-like classes.

## Custom comparisons

Classes can implement comparison methods such as:

    __lt__
    __le__
    __gt__
    __ge__
    __eq__

The `StudentScore` class uses these methods to compare students based on their scores.

Custom comparison behavior is useful for:

- sorting domain objects
- ranking
- threshold checks
- prioritization
- business rules

The comparison should represent a consistent and logically meaningful relationship.

## Custom membership

The `in` operator can be customized through `__contains__`.

The `ProductCatalog` example implements:

    def __contains__(self, product_name):
        ...

This allows expressions such as:

    "Laptop" in catalog

to work with a user-defined object.

## Matrix multiplication

The `@` operator represents matrix multiplication.

It was introduced specifically for matrix-like numerical operations.

The script defines a small educational `Matrix` class and implements:

    __matmul__

so that:

    matrix_a @ matrix_b

performs matrix multiplication.

The operator does not automatically make ordinary Python lists into matrices. Appropriate numerical or custom matrix types must implement the operation.

## Set operators

Sets provide mathematical operators.

| Operator | Meaning |
|---|---|
| `|` | Union |
| `&` | Intersection |
| `-` | Difference |
| `^` | Symmetric difference |

For two sets `A` and `B`:

    A | B

contains elements from either set.

    A & B

contains elements common to both.

    A - B

contains elements present in `A` but not `B`.

    A ^ B

contains elements present in exactly one of the two sets.

These operators are useful for data analysis, access control, feature comparison, and filtering.

## Dictionary merge operators

Python 3.9 introduced dictionary merge operators.

The `|` operator creates a merged dictionary:

    merged = defaults | user_settings

When the same key appears in both dictionaries, the value from the right-hand dictionary takes precedence.

The `|=` operator updates an existing dictionary:

    settings |= user_settings

These operators provide concise alternatives to some older dictionary-merging patterns.

## Sequence operators

Several sequence types overload operators.

For example:

    [1, 2] + [3, 4]

concatenates lists.

Similarly:

    [1, 2] * 3

repeats a list.

Strings support equivalent operations:

    "Py" + "thon"
    "ha" * 3

Sequence repetition has an important limitation with mutable nested objects. Repetition copies references to existing objects rather than creating independent recursive copies.

Therefore:

    nested = [[]] * 3

creates three references to the same inner list.

Modifying one inner list modifies what all three references observe.

## Assignment and object references

Assignment does not automatically copy an object.

For example:

    original = [1, 2, 3]
    alias = original

Both names refer to the same list.

Changing the list through either name changes the same object.

A shallow copy can create a new outer list:

    copied = original.copy()

The copied list and original list are different outer objects.

For nested structures, shallow copying does not recursively copy all nested objects. Deeper copying requires appropriate copying strategies when independent nested structures are necessary.

## Practical validation

Operators frequently work together in validation logic.

The script's validation example combines:

- comparison operators
- logical operators
- membership operators
- identity checks
- string operations

A validation rule can be expressed as:

    valid_age = 18 <= age <= 100
    valid_username = username.strip() != ""
    valid_role = "admin" in roles or "analyst" in roles

The final result combines these conditions with `and`.

This pattern occurs frequently in authentication, authorization, form validation, API input validation, and business-rule processing.

## Controlled expression evaluation

A calculator should not normally execute arbitrary user input with `eval()`.

A safer architecture for a limited calculator is to define an explicit set of permitted operations:

    {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul
    }

The script implements this design in both `calculate()` and `SimpleExpressionEvaluator`.

The approach provides explicit control over which operations can execute.

For more complex expression languages, a dedicated parser and restricted grammar are preferable to executing arbitrary Python source code.

## Security considerations

Operators themselves are ordinary language features, but unsafe expression evaluation can become a security problem.

The most important concern is executing untrusted text as Python code.

Using `eval()` or `exec()` on arbitrary user input can allow unintended code execution.

A safer design uses:

- explicit operation whitelists
- input validation
- type validation
- bounded input sizes
- controlled parsing
- explicit error handling

The script demonstrates a whitelist-based calculator instead of dynamic source-code execution.

## Performance considerations

Different operators can have very different performance characteristics because the underlying data structure determines the cost.

Membership testing illustrates this clearly.

For a list:

    target in large_list

usually requires a linear scan, making the average complexity O(n).

For a set:

    target in large_set

membership is generally O(1) on average because sets use hash-based lookup.

For dictionaries, key membership is also generally O(1) on average.

This means that changing the data structure can have a much greater performance impact than changing the surface syntax of an operator.

## Operator overloading design considerations

Operator overloading should represent an intuitive relationship.

For example, adding two `Money` objects with the same currency is meaningful.

Adding incompatible currencies directly is not automatically meaningful, so the example explicitly rejects that operation.

Good operator implementations should:

- preserve clear semantics
- validate incompatible operands
- avoid surprising side effects
- return `NotImplemented` for unsupported operand types where appropriate
- maintain consistent equality and ordering behavior
- document unusual behavior
- avoid overloading operators merely to make syntax shorter

Operator overloading is most effective when the domain meaning closely matches the normal meaning of the operator.

## Common mistakes

### Confusing `=` and `==`

Incorrect:

    if x = 10:

Correct:

    x = 10

and:

    if x == 10:

Assignment binds a value. Equality compares values.

### Confusing `==` and `is`

Use `==` for value equality.

Use `is` for identity, especially:

    value is None

### Confusing `/` and `//`

`/` performs true division.

`//` performs floor division.

For example:

    10 / 4

produces `2.5`, while:

    10 // 4

produces `2`.

### Ignoring negative floor division

Because floor division rounds toward negative infinity:

    -7 // 2

is `-4`, not `-3`.

### Assuming floating-point values are exact

Do not assume that every decimal calculation can be represented exactly by binary floating-point numbers.

Use approximate comparisons where appropriate and decimal arithmetic where exact decimal semantics are required.

### Forgetting short-circuit behavior

Short-circuiting can be useful, but complicated expressions can become difficult to understand.

Prefer clear conditions over clever expressions.

### Misusing `and` and `or`

Because these operators return operands, not necessarily Boolean values, code can behave differently from what beginners expect.

Explicit conditional expressions may be clearer when a true Boolean result is required.

### Accidentally sharing mutable objects

This can happen with chained assignment and sequence repetition.

For example:

    a = b = []

and:

    nested = [[]] * 3

can produce multiple references to the same mutable object.

## Edge cases

Important operator edge cases covered by the script include:

- division by zero
- modulo by zero
- negative floor division
- floating-point precision
- NaN comparisons
- infinity comparisons
- Boolean values participating in arithmetic
- mutable-object aliasing
- extended unpacking with zero remaining elements
- incompatible custom operands
- different dictionary values for the same key
- set-specific operator behavior
- unsupported custom operators
- matrix dimension mismatches

Understanding these cases is important because operator behavior is not always identical to elementary mathematical notation.

## `NaN` behavior

A floating-point NaN has unusual comparison semantics.

For example:

    nan == nan

is `False`.

Also:

    nan != nan

is `True`.

This behavior follows IEEE floating-point semantics and should be considered when processing scientific, statistical, or financial numerical data.

## Infinity

Python floating-point values can represent positive and negative infinity:

    float("inf")

Infinity participates in many comparisons as expected:

    float("inf") > 1_000_000

is `True`.

Programs performing numerical analysis should still consider whether infinite values are valid domain values.

## Error handling

Operator-related errors should be handled at the appropriate boundary.

Typical exceptions include:

- `ZeroDivisionError`
- `TypeError`
- `ValueError`
- `OverflowError` in relevant numerical situations

The script demonstrates explicit exception handling for division by zero and invalid calculator operations.

Input validation should normally happen before an operation when invalid input can be detected early.

## Testing operator-based code

The script contains a self-test section using assertions.

The tests verify:

- arithmetic behavior
- comparisons
- logical operations
- membership
- identity
- augmented assignment
- comparison chaining
- custom calculator operations

Assertions are useful for detecting unexpected behavior during development.

Production applications generally require a broader testing strategy, including unit tests, integration tests, boundary tests, and domain-specific validation.

## Implementation considerations

When implementing operator-heavy logic:

- choose operators that clearly express the intended meaning
- use parentheses when they improve readability
- validate operands before performing sensitive calculations
- handle division by zero explicitly where appropriate
- use `Decimal` for suitable exact-decimal financial calculations
- use `math.isclose()` for appropriate floating-point comparisons
- choose sets or dictionaries when repeated membership checks justify them
- avoid unsafe evaluation of arbitrary expressions
- use custom operator overloading only when the semantics are intuitive
- preserve consistent comparison behavior
- consider mutability when using assignment and augmented assignment
- test boundary conditions and unusual numerical values

## Operator category reference

The principal categories demonstrated in the script are:

| Category | Operators or forms |
|---|---|
| Assignment | `=` |
| Augmented assignment | `+=`, `-=`, `*=`, `/=`, `//=`, `%=`, `**=`, `@=`, `&=`, `|=`, `^=`, `<<=`, `>>=` |
| Assignment expression | `:=` |
| Arithmetic | `+`, `-`, `*`, `/`, `//`, `%`, `**`, `@` |
| Comparison | `==`, `!=`, `<`, `<=`, `>`, `>=` |
| Logical | `and`, `or`, `not` |
| Identity | `is`, `is not` |
| Membership | `in`, `not in` |
| Bitwise | `&`, `|`, `^`, `~`, `<<`, `>>` |
| Conditional | `x if condition else y` |
| Set operations | `|`, `&`, `-`, `^` |
| Dictionary merge | `|`, `|=` |
| Sequence operations | `+`, `*` |
| Matrix multiplication | `@` |

## Real-world relevance

Assignment and other operators appear throughout Python software.

Assignment operators are used for:

- state management
- variable initialization
- configuration
- counters
- accumulators
- object references

Arithmetic operators support:

- financial calculations
- statistics
- engineering formulas
- pricing
- measurements
- simulations

Comparison and logical operators support:

- validation
- authorization
- filtering
- business rules
- conditional workflows
- algorithmic decisions

Membership operators are important for:

- search
- validation
- access control
- collection processing

Bitwise operators are relevant to:

- permissions
- binary protocols
- flags
- systems programming
- compact state representations

Operator overloading supports domain-specific abstractions such as:

- matrices
- vectors
- monetary values
- dates and times
- scientific quantities
- custom collections

A strong understanding of operators therefore provides a foundation for both basic Python programming and advanced software design.
