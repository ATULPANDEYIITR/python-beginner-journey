# Comparison operators in Python

## Introduction

Comparison operators are used to determine the relationship between values. They are fundamental to decision-making in Python programs because they allow a program to determine whether values are equal, different, greater, smaller, within a range, or otherwise related.

The primary comparison operators are:

| Operator | Meaning | Example |
|---|---|---|
| `==` | Equal to | `a == b` |
| `!=` | Not equal to | `a != b` |
| `>` | Greater than | `a > b` |
| `<` | Less than | `a < b` |
| `>=` | Greater than or equal to | `a >= b` |
| `<=` | Less than or equal to | `a <= b` |

Python also provides related operators and mechanisms that are commonly used with comparison logic:

- `in`
- `not in`
- `is`
- `is not`
- logical operators such as `and`, `or`, and `not`
- chained comparisons
- rich comparison methods for custom classes

The accompanying Python script demonstrates comparison operators from basic expressions through validation, data processing, algorithms, custom objects, sorting, floating-point behavior, and domain-specific decision systems.

## What a comparison produces

A comparison normally produces a Boolean value:

- `True`
- `False`

For example, comparing `10` with `5` using the greater-than operator produces `True`.

A comparison expression can be:

- printed
- assigned to a variable
- used in an `if` statement
- used in a loop
- combined with other conditions
- used to filter data
- used by algorithms
- implemented by custom classes

A Boolean result can therefore become the basis for a larger program decision.

## Equality with `==`

The equality operator `==` checks whether two values compare as equal.

Examples include:

- two numbers having the same numeric value
- two strings containing the same text
- two lists containing equal elements
- two domain objects whose equality method defines them as equal

The equality operator is different from assignment.

Assignment uses:

`=`

Equality comparison uses:

`==`

For example, assigning `10` to a variable and checking whether a variable contains `10` are two different operations.

## Inequality with `!=`

The `!=` operator checks whether two values are not equal.

It is commonly used for:

- validation
- status checks
- filtering
- input processing
- detecting changes
- distinguishing different categories

For example, a status can be checked to determine whether it is different from `"inactive"`.

## Greater-than with `>`

The `>` operator returns `True` only when the left operand is strictly greater than the right operand.

For example:

`10 > 5`

is true, while:

`10 > 10`

is false.

The strict nature of the operator is important when designing boundary conditions.

## Less-than with `<`

The `<` operator returns `True` only when the left operand is strictly smaller than the right operand.

For example:

`5 < 10`

is true, while:

`10 < 10`

is false.

## Greater-than-or-equal with `>=`

The `>=` operator includes equality.

For example:

`10 >= 10`

is true.

This operator is particularly important when a requirement includes a boundary.

A rule such as "a person must be at least 18 years old" should use a condition equivalent to:

`age >= 18`

rather than:

`age > 18`

The difference occurs exactly at the boundary value.

## Less-than-or-equal with `<=`

The `<=` operator also includes equality.

For example:

`10 <= 10`

is true.

It is commonly used for maximum limits:

- amount must be no more than a limit
- age must be no more than a supported maximum
- response time must remain within an SLA
- inventory must not exceed a configured threshold

## Comparison table

For two values `a` and `b`:

| Expression | Question |
|---|---|
| `a == b` | Are they equal? |
| `a != b` | Are they different? |
| `a > b` | Is `a` strictly greater? |
| `a < b` | Is `a` strictly smaller? |
| `a >= b` | Is `a` greater or equal? |
| `a <= b` | Is `a` smaller or equal? |

Choosing the correct operator is a matter of accurately expressing the intended rule.

## Numeric comparisons

Python supports comparisons between compatible numeric types such as integers and floating-point values.

Examples include:

- positive numbers
- negative numbers
- zero
- very large integers
- floating-point values
- many combinations of numeric types

Python can compare an integer such as `1` and a floating-point value such as `1.0` as equal because they represent the same numeric value.

## Negative numbers

Negative numbers follow ordinary mathematical ordering.

For example:

`-10 < -5 < 0 < 5 < 10`

The sign of a number therefore directly affects the result of greater-than and less-than comparisons.

## String comparisons

Strings can be compared using equality, inequality, and ordering operators.

String ordering is lexicographical. Python compares characters according to their Unicode code points.

This means string comparison is not necessarily identical to natural-language dictionary ordering.

For example, uppercase and lowercase characters have different Unicode code points, so comparisons are case-sensitive.

## Case-sensitive comparison

The following values are different strings:

`"Python"`

and:

`"python"`

Therefore, direct equality between them is false.

When an application requires case-insensitive comparison, the values should be normalized before comparison.

`casefold()` is particularly useful for Unicode-aware case-insensitive matching.

## Unicode comparison

Python strings are Unicode strings.

The `ord()` function can be used to inspect the Unicode code point of a character.

Character ordering therefore depends on Unicode values rather than an abstract concept of alphabetical order.

For applications involving international text, direct string ordering should not automatically be interpreted as culturally correct sorting.

## Lexicographical comparison

Python compares sequences such as lists and tuples lexicographically.

The comparison proceeds from the first element toward later elements. Once Python finds the first pair of elements that differs, that difference determines the result.

For example, a sequence beginning with `1` is smaller than one beginning with `2`, regardless of later values.

This behavior is important for:

- tuples
- lists
- sorting
- ranking
- multi-field keys
- structured data comparisons

## Sequence length and comparison

If corresponding elements are equal until one sequence ends, the shorter sequence is considered smaller.

This is why a sequence such as `[1]` can compare as smaller than `[1, 0]`.

## Dictionary comparison

Dictionaries support equality comparison.

Two dictionaries can be equal even when their keys were inserted in different orders, because equality is based on their mappings.

Dictionaries do not support ordinary ordering comparisons using `<`, `>`, `<=`, or `>=`.

If dictionary records need to be ranked, a specific value should be selected as the comparison key.

For example, comparing two records by their `"score"` fields is meaningful even though comparing the dictionaries themselves with `>` is not.

## Set comparisons

Sets have specialized comparison semantics.

For sets:

- `==` checks equality
- `!=` checks inequality
- `<` checks proper subset
- `<=` checks subset
- `>` checks proper superset
- `>=` checks superset

For example, `{1, 2}` is a proper subset of `{1, 2, 3}`.

Set ordering is therefore not numerical or lexicographical. It represents set relationships.

Two sets can be incomparable under the subset relation. If neither set contains all elements of the other, both subset comparisons can be false.

## Boolean values and comparisons

`bool` is a subclass of `int` in Python.

Consequently:

- `True == 1` is true
- `False == 0` is true

This behavior is part of Python's type system, but code should not rely on it unnecessarily. Explicit Boolean conditions are normally clearer.

For example, if a variable already contains a Boolean value, writing the Boolean directly in a condition is clearer than comparing it with `True`.

## Equality versus identity

Equality and identity are different concepts.

Equality:

`a == b`

asks whether two objects have equal values according to their equality semantics.

Identity:

`a is b`

asks whether two references refer to the same object.

Two separately created lists can contain exactly the same elements while being different objects.

Therefore:

- equality can be true
- identity can be false

This distinction is one of the most important aspects of Python comparison logic.

## `is` and `is not`

The identity operators are:

- `is`
- `is not`

They should primarily be used when object identity is actually relevant.

The most common example is testing for `None`.

Preferred style:

`value is None`

and:

`value is not None`

Ordinary values should normally be compared with `==` rather than `is`.

## Why `is` should not replace `==`

Python implementations may reuse or cache certain objects. This can make identity results appear to work for some values even when identity is not semantically appropriate.

Code should not rely on implementation-specific object reuse for value comparisons.

Use:

`==`

for value equality.

Use:

`is`

when object identity is the intended question.

## `None` comparisons

`None` represents the absence of a value in many Python APIs.

The recommended tests are:

- `value is None`
- `value is not None`

This is especially important when a valid application value could be false, zero, an empty string, or an empty collection.

## Membership operators

The membership operators are:

- `in`
- `not in`

They test whether a value occurs within a container or supported object.

Examples include:

- checking whether an item exists in a list
- checking whether text contains a substring
- checking whether a dictionary contains a key
- checking whether an element belongs to a set

Membership semantics depend on the container type.

For dictionaries, `key in dictionary` checks keys rather than values.

## Logical operators with comparisons

Comparison expressions are frequently combined using:

- `and`
- `or`
- `not`

`and` requires all relevant conditions to be true.

`or` requires at least one relevant condition to be true.

`not` reverses a Boolean condition.

For example, a business rule might require:

- minimum age
- minimum income
- sufficient credit score
- acceptable debt

Such rules can be represented by combining comparisons with `and`.

## Short-circuit evaluation

Python evaluates `and` and `or` from left to right and can stop evaluating once the result is known.

For `and`, a false operand can make the entire expression false.

For `or`, a true operand can make the entire expression true.

Short-circuiting is useful for both correctness and performance.

For example, checking that a string is non-empty before accessing its first character prevents an invalid indexing operation.

## Chained comparisons

Python supports mathematical-style chained comparisons.

For example:

`10 < x < 20`

expresses that `x` is greater than `10` and less than `20`.

This is equivalent in meaning to:

`10 < x and x < 20`

when used as a normal chained comparison.

Chained comparisons are especially useful for ranges.

Examples include:

- `0 <= percentage <= 100`
- `18 <= age < 60`
- `9 <= hour < 18`

## Inclusive and exclusive boundaries

The distinction between strict and inclusive comparisons is critical.

Strict boundaries:

- `>`
- `<`

Inclusive boundaries:

- `>=`
- `<=`

For a range from 10 through 20 inclusive:

`10 <= value <= 20`

The values 10 and 20 are both accepted.

For an interval where 20 should be excluded:

`10 <= value < 20`

The choice should reflect the actual business or mathematical rule.

## Half-open intervals

Python frequently uses the half-open interval convention:

`[start, end)`

This means:

- start is included
- end is excluded

The built-in `range()` follows this model.

For example, `range(1, 5)` contains:

1, 2, 3, 4

but not 5.

This convention simplifies many indexing and algorithmic operations.

## Floating-point comparisons

Floating-point arithmetic requires special care.

Decimal fractions such as `0.1` and `0.2` cannot always be represented exactly using binary floating-point representation.

Consequently, an expression such as:

`0.1 + 0.2`

may not have exactly the same stored representation as:

`0.3`

Therefore, direct equality checks can produce surprising results.

## `math.isclose()`

For approximate floating-point comparisons, Python provides `math.isclose()`.

It supports:

- relative tolerance
- absolute tolerance

Relative tolerance is useful when values vary significantly in magnitude.

Absolute tolerance is especially important near zero.

Tolerance values should be selected according to the precision requirements of the application rather than copied blindly.

## Decimal comparisons

The `decimal.Decimal` type is useful when decimal arithmetic needs predictable decimal semantics.

It is particularly relevant to applications such as:

- financial calculations
- prices
- monetary balances
- accounting values

When constructing a `Decimal` from a decimal literal represented as text, using a string is preferable when exact decimal input is intended.

## NaN comparisons

`NaN` means "Not a Number" and has unusual IEEE floating-point comparison behavior.

A NaN value is not equal to itself.

Consequently:

- `nan == nan` is false
- `nan != nan` is true
- `nan < value` is false
- `nan > value` is false

NaN should be detected using appropriate numerical checks such as `math.isnan()` rather than ordinary equality.

## Complex numbers

Complex numbers support equality and inequality comparisons.

They do not support ordinary ordering comparisons such as:

- `<`
- `>`
- `<=`
- `>=`

Python does not define a natural total ordering for complex numbers.

If complex values need to be sorted, an explicit metric can be supplied. For example, values can be ordered by their magnitude using `abs`.

This illustrates an important design principle: a program should use an explicit domain-specific ordering when a natural ordering does not exist.

## User input and comparisons

`input()` returns a string.

Therefore, numeric input normally needs conversion before numeric comparison.

A value read as `"100"` is text, not the integer `100`.

Comparing strings to numbers with ordering operators can produce a `TypeError`.

Input validation should therefore include:

1. reading the value
2. cleaning it when necessary
3. converting it to the intended type
4. validating its range
5. performing the comparison

## Validation with comparisons

Comparison operators are fundamental to input validation.

Typical validation rules include:

- age must be non-negative
- percentage must be between 0 and 100
- price must not be negative
- score must meet a minimum
- quantity must not exceed a limit
- temperature must remain within an accepted range

Chained comparisons make many range checks concise and readable.

## Comparison inside `if`, `elif`, and `else`

Conditional statements depend heavily on comparison operators.

A typical classification structure is:

- test the highest threshold
- test progressively lower thresholds
- use `else` for the remaining cases

Ordering of conditions matters.

For example, when assigning grades, testing a lower threshold before a higher threshold can make the higher branch unreachable for some values.

## Guard clauses

Guard clauses use comparisons early in a function to reject invalid conditions or handle exceptional cases.

For example:

- reject a negative price
- reject an invalid age
- reject a reversed interval
- reject missing required data

Guard clauses can make the main business logic easier to understand by removing invalid cases early.

## Truthiness versus explicit comparison

Python collections and strings have truth-value behavior.

An empty list is false in a Boolean context.

Therefore:

`if items:`

is generally clearer than:

`if items != []:`

Likewise:

`if not items:`

is commonly preferable when checking whether a collection is empty.

An explicit comparison is appropriate when the actual comparison itself matters.

## Comparing strings that represent numbers

String ordering is different from numeric ordering.

For example, the text `"9"` can compare as greater than `"10"` because string comparison examines characters rather than numeric magnitude.

When numeric meaning is intended, convert the strings to numbers before comparison.

The same principle applies to version strings, identifiers, dates represented as text, and other structured values.

## Version comparisons

Versions should not normally be compared as ordinary strings when their components have numeric meaning.

For example, string comparison can incorrectly treat:

`"10.0"`

as smaller than:

`"2.0"`

because the first character is compared first.

Parsing the version into numeric components creates a meaningful ordering.

## Date and time comparisons

Python's `date` and `datetime` types support meaningful comparison operations.

Dates can be compared chronologically.

This is useful for:

- deadlines
- expiration
- scheduling
- reporting periods
- date ranges
- SLA checks

The types being compared should be compatible and their timezone semantics should be understood when working with timezone-aware datetimes.

## Comparison in data filtering

Comparison operators are heavily used in data processing.

Examples include selecting:

- customers above a spending threshold
- transactions above a minimum amount
- employees with sufficient experience
- scores above a benchmark
- records matching a status
- inventory below a reorder level

List comprehensions provide a concise way to express many filtering operations.

## `any()` and `all()`

`any()` and `all()` combine comparison-based conditions over collections or generators.

`any()` returns true if at least one item satisfies the condition.

`all()` returns true if every item satisfies the condition.

They also short-circuit:

- `any()` stops at the first true result
- `all()` stops at the first false result

An important edge case is the empty iterable:

- `any([])` is `False`
- `all([])` is `True`

The behavior of `all()` follows its logical definition but can surprise programmers who assume that an empty collection must automatically fail a requirement.

## Comparison and algorithms

Comparison operators are central to many algorithms, including:

- searching
- sorting
- filtering
- ranking
- partitioning
- threshold detection
- interval processing
- decision systems

Algorithm correctness often depends on precise comparison conditions.

A single incorrect `<` instead of `<=` can change the behavior of an entire algorithm at a boundary.

## Binary search

Binary search repeatedly compares a target with a middle element of a sorted collection.

If the target is greater than the middle value, the search continues in the upper half.

If the target is smaller, it continues in the lower half.

If the values are equal, the target has been found.

For a sorted collection, binary search has logarithmic time complexity:

`O(log n)`

The example implementation in the script is iterative and uses constant auxiliary space:

`O(1)`

The input must already be sorted according to the same ordering used by the search.

## Sorting and comparison keys

Python's `sorted()` and `list.sort()` use comparison-based ordering internally.

For application objects, a `key` function is often preferable to implementing a custom ordering.

A key function converts each object into a value representing the desired sorting criterion.

For example, employee records can be sorted by salary using the salary field as the key.

## Multiple sorting criteria

Tuples provide a convenient way to define multi-criteria ordering.

For example, records can be ordered by:

1. department
2. salary
3. name

Tuple comparison is lexicographical, so each field naturally becomes a tie-breaker for the preceding fields.

For different sort directions, a key can sometimes use transformations such as negative numeric values, or stable sorting can be applied in reverse priority order.

## Stable sorting

Python sorting is stable.

If two records have equal sorting keys, their original relative order is preserved.

Stable sorting is useful when applying multiple ordering operations and when preserving an existing order among equivalent records.

## Custom classes and rich comparisons

Python allows custom classes to define comparison behavior through rich comparison methods:

- `__eq__`
- `__ne__`
- `__lt__`
- `__le__`
- `__gt__`
- `__ge__`

A class can therefore define what equality or ordering means for its objects.

This is appropriate when a domain has a genuine comparison relationship.

## `NotImplemented`

Custom comparison methods should generally return `NotImplemented` when they do not know how to compare the supplied type.

This is different from returning `False`.

`NotImplemented` tells Python that the current implementation does not support that operand combination, allowing Python's comparison machinery to try the appropriate alternatives or raise a suitable `TypeError`.

This is an important detail when implementing reusable classes.

## `functools.total_ordering`

The `functools.total_ordering` decorator can generate missing ordering methods from a smaller set of comparison methods.

Typically, a class supplies:

- `__eq__`
- one ordering operation such as `__lt__`

and `total_ordering` supplies the other ordering methods.

It can reduce boilerplate, but explicitly implementing comparison operations may be preferable in performance-sensitive or highly specialized classes because generated logic can involve additional method calls.

## Dataclass ordering

The `dataclasses` module can generate comparison methods using:

`@dataclass(order=True)`

The generated ordering follows field declaration order.

This is convenient but requires careful field design.

If the first field is not actually the primary ordering criterion, automatic ordering may produce technically valid but semantically incorrect results for the application's purpose.

## Domain-specific comparison

An object can often be compared in multiple legitimate ways.

An employee might be compared by:

- salary
- seniority
- performance
- department
- name

There is no universally correct ordering without a domain rule.

For such cases, explicit methods or key functions are usually clearer than imposing one arbitrary global ordering.

## Partial ordering versus total ordering

A total ordering allows every pair of values to be meaningfully ordered.

A partial ordering does not necessarily provide a relationship for every pair.

Set subset relationships are an example.

Two sets can both fail the subset test against each other even though they are not equal.

Complex numbers are another example where ordinary ordering is not defined.

The appropriate comparison model depends on the mathematical structure of the data.

## Comparison contracts

A well-designed ordering should behave consistently.

Important properties include:

- equality should be self-consistent
- ordering should be transitive
- equivalent values should behave consistently
- comparison results should not contradict each other

For example, if `a < b` and `b < c`, a coherent ordering should also imply `a < c`.

Custom comparison methods do not automatically receive mathematical validation from Python. The class designer is responsible for defining coherent semantics.

## Equality and hashing

For hashable objects, equality and hashing must be compatible.

A fundamental requirement is:

If `a == b`, then `hash(a)` should equal `hash(b)`.

This matters when objects are stored in:

- dictionaries
- sets

Defining a custom `__eq__` can affect whether an object is hashable and how it behaves in hash-based collections.

Frozen dataclasses can be useful when immutable value objects need reliable equality and hashing semantics.

## Comparison and data cleaning

Real-world data often contains:

- leading whitespace
- inconsistent capitalization
- missing values
- numeric values stored as strings
- malformed values
- different Unicode representations

Comparison logic should operate on normalized values when appropriate.

For identifiers, trimming whitespace and applying case normalization can prevent false mismatches.

For Unicode text, normalization using the `unicodedata` module can be necessary when visually equivalent strings may have different internal representations.

## Missing data

Missing values should be handled explicitly.

For example, a numerical score may be:

- a number
- `None`

Trying to order `None` with a number is generally invalid.

A robust program should first test whether the value is missing:

`score is None`

and only perform numeric comparison when a real score exists.

## Comparison and business rules

Comparison operators translate business requirements into executable logic.

Examples include:

- minimum age
- minimum income
- maximum debt
- minimum score
- spending thresholds
- inventory limits
- SLA requirements
- access levels
- transaction limits

The comparison operator must exactly match the requirement.

"At least" means `>=`.

"Greater than" means `>`.

"At most" means `<=`.

"Less than" means `<`.

"Exactly" means `==`.

"Different from" means `!=`.

## Comparison and authorization

Comparison logic can determine whether a user has sufficient permissions.

A common design is to map roles to numeric levels and compare those levels.

For example:

- guest = 0
- user = 1
- manager = 2
- admin = 3

The current user's level can then be compared with the minimum required level.

This approach is useful when permissions form a clear hierarchy.

## Comparison and security

Comparison logic can appear in security-sensitive code, including:

- authorization
- token verification
- access thresholds
- password policies
- rate limiting
- transaction limits

Ordinary equality should not automatically be assumed appropriate for comparing secrets.

For security-sensitive secret values, timing-resistant comparison functions such as `hmac.compare_digest()` can be appropriate.

The broader principle is that security-sensitive comparisons require consideration of both logical correctness and side-channel behavior.

## Comparison and performance

Simple comparisons are generally inexpensive.

Performance becomes more relevant when:

- comparisons are executed millions of times
- comparison functions perform expensive calculations
- custom objects perform complex work
- sorting involves expensive transformations
- data is repeatedly normalized during comparisons

Short-circuit evaluation can prevent unnecessary work.

When sorting, key functions are often preferable to repeatedly recalculating a complex comparison criterion.

## Comparison key design

A good comparison key should:

- represent the intended domain rule
- be deterministic
- be inexpensive when possible
- handle missing values deliberately
- make tie-breaking explicit
- avoid unintended type combinations

For example, a candidate-ranking key can contain:

- technical score
- communication score
- name

This creates a predictable tie-breaking structure.

## Common mistakes

### Using `=` instead of `==`

`=` performs assignment.

`==` performs equality comparison.

Confusing them leads to syntax errors or incorrect code.

### Using `is` instead of `==`

`is` checks object identity.

`==` checks value equality.

Use `is` primarily for cases such as `None` and deliberately shared sentinel objects.

### Comparing floating-point values with exact equality

Binary floating-point representation can cause mathematically expected decimal values to differ at the representation level.

Use an appropriate tolerance when approximate equality is intended.

### Forgetting input conversion

`input()` returns strings.

A numeric string must generally be converted before numeric ordering is performed.

### Using the wrong boundary operator

A requirement such as "at least 18" requires `>= 18`.

Using `> 18` incorrectly excludes exactly 18.

### Using `or` when `and` is required

Changing `and` to `or` can fundamentally change a business rule.

Conditions should be written according to the actual requirement rather than the desired output for one test case.

### Comparing dictionaries directly for ordering

Dictionaries support equality but do not provide ordinary numerical ordering.

Select the specific field that represents the intended comparison.

### Assuming all objects have a natural ordering

Some objects cannot or should not be ordered directly.

Use a domain-specific key when an ordering criterion is needed.

## Debugging comparison problems

When a comparison produces an unexpected result, inspect:

1. The actual values.
2. The types of the values.
3. Leading or trailing whitespace.
4. String capitalization.
5. Numeric conversion.
6. Floating-point precision.
7. `None` values.
8. Object identity.
9. Custom comparison methods.
10. Boundary conditions.
11. Logical operators.
12. Chained comparison structure.

Using `repr()` is useful when invisible characters may be involved.

Printing `type(value).__name__` is useful when values look correct but behave differently.

## Testing comparison logic

Comparison-heavy code should be tested around boundaries.

For a range from 10 through 20, useful test values include:

- 9
- 10
- 11
- 19
- 20
- 21

These tests verify:

- below the lower boundary
- exactly at the lower boundary
- inside the range
- exactly at the upper boundary
- above the upper boundary

Assertions are useful for executable correctness checks.

## Edge cases covered

The script demonstrates several important edge cases:

- negative numbers
- zero
- equal boundary values
- empty strings
- empty collections
- `None`
- NaN
- floating-point precision
- complex numbers
- incompatible types
- mixed sequence values
- missing data
- unknown categories
- empty iterables with `any()` and `all()`
- custom objects
- Unicode normalization
- identity versus equality

These cases are important because comparison logic that works for ordinary values can fail or behave unexpectedly at the boundaries.

## Practical applications

Comparison operators are used throughout software development.

### Data validation

Examples:

- percentage between 0 and 100
- age within a supported range
- amount greater than zero
- quantity below a maximum

### Finance

Examples:

- transaction amount against a limit
- debt against income
- investment against a minimum
- profit against zero
- profit margin against a target

### Business analytics

Examples:

- filtering high-value customers
- identifying large transactions
- selecting records above a threshold
- comparing performance against targets

### Machine learning

Examples:

- classification thresholds
- minimum accuracy requirements
- error tolerances
- outlier detection

### Web applications

Examples:

- authorization
- feature access
- account status
- input validation
- request limits

### Algorithms

Examples:

- binary search
- sorting
- filtering
- ranking
- interval overlap
- partitioning

### Scheduling

Examples:

- checking whether a time is inside business hours
- comparing deadlines
- detecting expired records
- checking overlapping intervals

## Implementation considerations

When implementing comparison logic:

- choose the operator that precisely matches the requirement
- handle boundary values explicitly
- normalize data when semantic equality requires it
- convert values to the correct types
- use `is None` for `None`
- use `==` for normal value equality
- use `is` for identity
- use `isclose()` for approximate floating-point equality
- use `Decimal` when decimal arithmetic semantics are required
- define custom comparison methods only when domain semantics justify them
- return `NotImplemented` for unsupported custom comparison types
- use key functions for most custom sorting requirements
- test edge cases around boundaries

## Production considerations

In production systems, comparison logic often represents important business rules.

A comparison should therefore be:

- explicit
- deterministic
- testable
- documented when non-obvious
- consistent with the domain model
- resistant to malformed input
- careful about numerical precision
- appropriate for the data types involved

Security-sensitive comparisons require additional care because logical equality and secure secret comparison are different concerns.

Comparison code should also be isolated into testable functions when rules become sufficiently complex.

## Relationship between comparison operators and control flow

Comparison operators provide the conditions used by control-flow structures.

The general relationship is:

comparison → Boolean result → condition → program decision

For example:

`score >= 40`

produces a Boolean result.

That result can then determine whether a student passes.

Larger systems build many such comparisons into validation rules, algorithms, and decision engines.

## Relationship between comparisons and data structures

Different Python data structures define different comparison semantics.

| Type | Equality | Ordering |
|---|---|---|
| `int` | Yes | Yes |
| `float` | Yes | Yes, with NaN considerations |
| `Decimal` | Yes | Yes |
| `str` | Yes | Lexicographical |
| `list` | Yes | Lexicographical |
| `tuple` | Yes | Lexicographical |
| `set` | Yes | Subset/superset semantics |
| `dict` | Yes | No ordinary ordering |
| `complex` | Equality/inequality | No ordinary ordering |
| Custom class | Defined by class | Defined by class |

Understanding the type-specific behavior prevents incorrect assumptions.

## Relationship between comparisons and sorting

Sorting depends on ordering relationships.

For simple values, Python already knows how to compare them.

For structured data, a key function is usually the clearest way to specify the desired ordering.

For domain objects that genuinely have a natural order, rich comparison methods can provide reusable semantics.

The choice between these approaches depends on whether the ordering is:

- local to one operation
- reusable across the application
- inherent to the domain object
- dependent on multiple criteria

## Relationship between comparisons and validation

Validation is fundamentally a comparison problem in many applications.

A validation rule can often be expressed as a Boolean statement:

- value must be positive
- value must be within a range
- status must equal a required value
- field must not be empty
- score must meet a threshold

Clear comparison expressions make validation easier to test and maintain.

## Relationship between comparisons and algorithms

Many algorithms repeatedly ask questions such as:

- Is the target equal to the current value?
- Is the target greater than the current value?
- Is this boundary reached?
- Is this element smaller?
- Are these intervals overlapping?
- Does this value satisfy the threshold?

Comparison operators are therefore not merely syntax for conditional statements. They are core primitives for computational reasoning.

## Performance considerations for comparison-heavy code

For ordinary application code, readability should generally take priority over micro-optimizing comparisons.

Performance becomes important when:

- processing very large datasets
- performing repeated searches
- sorting large collections
- evaluating expensive custom comparison methods
- repeatedly normalizing text
- calling expensive functions inside compound conditions

Useful principles include:

- take advantage of short-circuiting
- compute expensive keys once when appropriate
- use efficient built-in operations
- use binary search for suitable sorted data
- avoid unnecessary repeated conversions
- use key-based sorting rather than complex comparator functions when possible

## Important distinctions

### `==` versus `is`

`==` asks:

"Do these values compare equal?"

`is` asks:

"Are these references to the same object?"

### `>` versus `>=`

`>` excludes equality.

`>=` includes equality.

### `<` versus `<=`

`<` excludes equality.

`<=` includes equality.

### `and` versus `or`

`and` requires all conditions to succeed.

`or` requires at least one condition to succeed.

### exact float equality versus approximate equality

Exact equality checks representation-level equality.

Approximate comparison checks whether values are sufficiently close according to a tolerance.

## Complete operator reference

| Category | Operator | Purpose |
|---|---|---|
| Equality | `==` | Value equality |
| Inequality | `!=` | Value inequality |
| Ordering | `>` | Strictly greater |
| Ordering | `<` | Strictly smaller |
| Ordering | `>=` | Greater or equal |
| Ordering | `<=` | Smaller or equal |
| Membership | `in` | Membership test |
| Membership | `not in` | Non-membership test |
| Identity | `is` | Same object |
| Identity | `is not` | Different objects |

## Script coverage

The Python script progresses from basic comparison expressions through:

- Boolean comparison results
- numeric comparisons
- negative numbers
- string and Unicode comparisons
- conditional statements
- loops
- logical operators
- chained comparisons
- membership
- identity
- `None`
- floating-point precision
- `Decimal`
- NaN
- complex numbers
- lists
- tuples
- dictionaries
- sets
- input validation
- date and time comparisons
- sorting
- filtering
- `min()` and `max()`
- custom comparison methods
- `NotImplemented`
- `total_ordering`
- dataclass ordering
- comparison keys
- business rules
- security-sensitive comparisons
- binary search
- interval logic
- `any()` and `all()`
- Unicode normalization
- missing data
- testing
- assertions
- performance considerations
- domain-specific comparison design
- an integrated loan-screening example

The examples are intentionally executable so that comparison behavior can be observed directly rather than treated only as abstract syntax.
