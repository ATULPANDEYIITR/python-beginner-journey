# Conditional decision-making with `if`, `elif`, and `else`

## Topic introduction

Conditional statements allow a program to make decisions based on the current state of data. Python uses `if`, `elif`, and `else` to express alternative execution paths.

The same general idea appears in JavaScript and C++, although the syntax differs.

A conditional structure answers questions such as:

- Is a user old enough to enter?
- Is an account active?
- Which grade corresponds to a score?
- Is a transaction low, medium, or high risk?
- Should an order be approved, reviewed, or rejected?
- Does a user have permission to access a resource?
- Does input satisfy a required range?
- Which business rule should be applied?

The three primary Python keywords are:

- `if`: tests the first condition.
- `elif`: tests another condition when previous conditions were false.
- `else`: provides the fallback branch when none of the preceding conditions is true.

A typical Python structure is:

    if condition:
        statement
    elif another_condition:
        statement
    else:
        statement

Python identifies blocks through indentation. JavaScript and C++ use braces to define blocks.

---

## Fundamental concepts

### Boolean conditions

A condition produces a Boolean result: `True` or `False` in Python, and `true` or `false` in JavaScript and C++.

For example:

    age >= 18

The expression is true when `age` is at least 18.

Common comparison operators are:

| Operator | Meaning |
|---|---|
| `==` | equal |
| `!=` | not equal |
| `<` | less than |
| `<=` | less than or equal |
| `>` | greater than |
| `>=` | greater than or equal |

In JavaScript and C++, strict equality is normally written with `===` in JavaScript and `==` in C++.

Python uses `==` for equality.

### The `if` statement

An `if` statement executes a block only when its condition is true.

The Python implementation demonstrates this with an age check:

    if age >= 18:
        print("The person is an adult.")

When `age` is 20, the condition is true and the indented statement executes.

When `age` is 16, the statement does not execute.

### The `else` branch

`else` provides an alternative when the `if` condition is false.

    if age >= 18:
        status = "adult"
    else:
        status = "minor"

For an `if`/`else` pair, one of the two branches executes.

### The `elif` branch

`elif` means "else if". It allows several mutually exclusive alternatives.

The grade example follows this pattern:

    if marks >= 90:
        grade = "A+"
    elif marks >= 80:
        grade = "A"
    elif marks >= 70:
        grade = "B"
    else:
        grade = "F"

Python evaluates the conditions from top to bottom. Once one condition is true, its branch executes and the remaining branches in that chain are skipped.

---

## Ordering conditions correctly

Condition order can change the result.

Suppose the intended grading rules are:

- 90 or above: A+
- 80 to below 90: A
- 70 to below 80: B
- below 70: lower grade

The most restrictive high threshold should be checked first.

An incorrectly ordered chain could begin with:

    if marks >= 50:
        grade = "D"
    elif marks >= 90:
        grade = "A+"

A score of 95 satisfies `marks >= 50`, so Python would select `D` and never reach the `elif`.

This is one of the most important practical properties of an `if`/`elif` chain: **the first matching condition wins**.

---

## Boolean operators

Conditional expressions often combine multiple conditions.

### `and`

`and` requires both operands to be true.

    if age >= 18 and has_id:
        print("Entry permitted.")

### `or`

`or` requires at least one operand to be true.

    if temperature > 40 or raining:
        print("Take protection.")

### `not`

`not` reverses a Boolean value.

    if not account_locked:
        print("Account is available.")

JavaScript uses `&&`, `||`, and `!`.

C++ uses the same operators as JavaScript: `&&`, `||`, and `!`.

---

## Truthiness

Python conditions do not require the expression to literally produce `True` or `False`.

Python considers several values false-like, including:

- `False`
- `None`
- `0`
- empty strings
- empty lists
- empty dictionaries
- empty sets
- empty tuples

For example:

    names = []

    if names:
        print("Names exist.")
    else:
        print("No names exist.")

JavaScript has its own truthiness rules. Values such as `false`, `0`, `""`, `null`, `undefined`, and `NaN` are falsy.

An important JavaScript distinction is that empty arrays and empty objects are truthy:

    if ([]) {
        // This executes.
    }

    if ({}) {
        // This also executes.
    }

C++ conditional expressions are normally based on Boolean values, although other scalar values can be contextually converted to `bool`.

---

## Equality and identity

Python distinguishes equality from identity.

Equality asks whether values are equivalent:

    if value == other_value:
        ...

Identity asks whether two references point to the same object:

    if value is None:
        ...

`is None` is the preferred Python pattern for checking `None`.

JavaScript has strict equality:

    value === otherValue

Strict equality avoids many implicit conversions associated with `==`.

The JavaScript implementation explicitly demonstrates:

    5 === "5"

and:

    5 == "5"

These expressions have different results because loose equality can perform type coercion.

---

## Membership conditions

Python provides the `in` operator:

    if role in {"admin", "manager"}:
        ...

This is useful for membership rules.

Instead of writing a long sequence of comparisons, a set can represent the accepted values.

The C++ case study uses `std::set` for supported country codes, while JavaScript uses `Set`.

This illustrates an important design principle: conditional logic does not always need to contain every value explicitly. A suitable data structure can represent the allowed set.

---

## Nested conditional statements

Conditions can be placed inside other conditions.

For example:

    if age >= 18:
        if has_ticket:
            if not is_banned:
                print("Entry approved.")

Nested conditions can model hierarchical rules, but excessive nesting makes code harder to read.

The implementations therefore also demonstrate guard clauses.

---

## Guard clauses

A guard clause handles an invalid or disallowed situation immediately.

Instead of:

    if age >= 18:
        if has_ticket:
            if not is_banned:
                return True

the logic can be written as:

    if age < 18:
        return False

    if not has_ticket:
        return False

    if is_banned:
        return False

    return True

This approach reduces nesting and makes rejection conditions explicit.

Guard clauses are particularly useful for validation, authorization, API handlers, transaction processing, and business-rule systems.

---

## Conditional expressions

Python has a conditional expression:

    status = "adult" if age >= 18 else "minor"

JavaScript uses the conditional or ternary operator:

    const status = age >= 18 ? "adult" : "minor";

C++ also supports the ternary operator:

    string status = age >= 18 ? "adult" : "minor";

These expressions are useful when the decision is short and the result is directly assigned.

They should not be used to hide complicated business logic. Multiple nested ternary expressions can reduce readability.

---

## Independent `if` statements versus `elif`

This distinction is fundamental.

Consider:

    if number % 2 == 0:
        print("even")

    if number > 0:
        print("positive")

Both conditions can execute.

An `elif` chain behaves differently:

    if number < 0:
        print("negative")
    elif number == 0:
        print("zero")
    else:
        print("positive")

Only one branch executes.

Use independent `if` statements when multiple conditions can legitimately apply.

Use `if`/`elif`/`else` when the alternatives are mutually exclusive.

---

## Input validation

Conditional statements are central to input validation.

The Python implementation converts a string to an integer and then validates its range:

    try:
        age = int(raw_age)
    except ValueError:
        ...
    
    if age < 0:
        ...
    elif age > 150:
        ...
    else:
        ...

The JavaScript implementation uses `Number`, `Number.isInteger`, and explicit range checks.

The C++ implementation uses `stoi` and verifies that the complete input was consumed.

A robust validation process generally has these stages:

1. Parse the input.
2. Detect conversion errors.
3. Check type requirements.
4. Check range constraints.
5. Check domain-specific rules.
6. Reject invalid values clearly.

Conditional statements should not be used as a substitute for parsing or exception handling. They work together with those mechanisms.

---

## Boundary conditions

Many conditional bugs occur at boundaries.

For a grading rule:

    if marks >= 90:
        ...

the difference between `>= 90` and `> 90` is significant.

Important boundary values should be tested explicitly:

- 0
- 49.99
- 50
- 59.99
- 60
- 69.99
- 70
- 79.99
- 80
- 89.99
- 90
- 100

Invalid values such as `-1` and `101` should also be tested.

This technique is called boundary-value testing.

---

## Short-circuit evaluation

Boolean operators can avoid evaluating unnecessary expressions.

Python:

    if username and is_admin:
        ...

If `username` is falsy, Python does not need to evaluate `is_admin`.

JavaScript uses the same general short-circuit behavior with `&&` and `||`.

This is useful when the second condition depends on the first condition being valid.

For example:

    if numbers and numbers[0] > 5:
        ...

The first condition prevents access to `numbers[0]` when the collection is empty.

Short-circuiting can improve safety and performance, but expressions should remain understandable.

---

## Operator precedence

Complex Boolean expressions have precedence rules.

Python evaluates:

1. `not`
2. `and`
3. `or`

For example:

    a or b and c

is interpreted as:

    a or (b and c)

Parentheses make intent clearer:

    (a or b) and c

When a business rule is complicated, explicit parentheses are usually preferable even when they are not technically required.

---

## Functions and conditional logic

Conditional logic becomes easier to test and reuse when placed inside functions.

The Python implementation contains:

    def classify_temperature(celsius: float) -> str:

The function converts a numeric input into a meaningful category.

Functions provide several advantages:

- reusable decision rules
- isolated testing
- clearer interfaces
- reduced duplication
- easier maintenance
- better separation of concerns

A complex decision should generally have a named function whose name describes what the decision means.

---

## Object-oriented conditional logic

The Python implementation uses `Employee` as a dataclass.

The employee has:

- name
- performance score
- years of service
- disciplinary status

The bonus function uses conditional rules to determine a bonus rate.

The JavaScript implementation uses an `Employee` class.

The C++ case study uses structures and enumerations to represent domain data.

This illustrates a broader principle: conditional statements often operate on domain objects rather than isolated primitive variables.

---

## Rule-based systems

The transaction examples demonstrate a small rule engine.

The rules include:

1. Invalid transaction amounts are rejected.
2. Suspicious transactions are high risk.
3. Large unverified transactions are high risk.
4. Medium-sized transactions are medium risk.
5. Remaining valid transactions are low risk.

The order of these rules matters.

For example, a suspicious transaction should be classified as high risk before a general amount-based rule is allowed to classify it as low risk.

This is a common pattern in:

- payment processing
- fraud detection
- eligibility systems
- pricing engines
- insurance rules
- loan processing
- access control
- workflow management

---

## Security-oriented decisions

The implementations include authorization examples.

Authentication and authorization are different concepts.

Authentication asks:

> Who is the user?

Authorization asks:

> What is the user allowed to do?

The authorization implementation checks:

1. Whether the request is authenticated.
2. Whether the resource is public.
3. Whether the user has an administrator role.
4. Whether the user owns the protected resource.

The default result is denial.

This is called a fail-closed approach.

For security-sensitive code, unknown roles and missing permissions should generally not accidentally grant access.

Conditional logic should not be considered a complete security system by itself. Real systems also require secure identity management, session controls, logging, access policies, input validation, secret management, and appropriate server-side enforcement.

---

## JavaScript-specific conditional behavior

JavaScript has several mechanisms that interact closely with conditional statements.

### Strict equality

Prefer:

    if (value === expected) {
        ...
    }

over loose equality when type coercion is not intentionally required.

### Nullish coalescing

The `??` operator distinguishes nullish values from other falsy values.

For example:

    const configuredLimit = 0;
    const limit = configuredLimit ?? 100;

The result remains `0`.

A general truthiness fallback such as `configuredLimit || 100` would treat `0` as falsy and produce `100`.

### Asynchronous decisions

The JavaScript implementation includes an asynchronous user-status operation.

The program waits for the result and then applies conditional logic:

    if (!user.authenticated) {
        ...
    } else if (!user.active) {
        ...
    } else if (user.role === "admin") {
        ...
    }

This pattern is common in web applications because information used for a decision often comes from asynchronous operations.

### Browser environment detection

The JavaScript implementation checks:

    typeof window !== "undefined"

and:

    typeof document !== "undefined"

This demonstrates how conditions can adapt program behavior to different runtime environments.

---

## Python-specific conditional behavior

Python conditions can operate directly on objects through truth-value testing.

Important examples include:

    if collection:
        ...

    if value is None:
        ...

Python also supports assignment expressions:

    if (length := len(text)) > 5:
        ...

The assignment expression can be useful when the assigned value is needed immediately inside the condition, but ordinary assignment may be clearer for complicated logic.

Python also provides structural pattern matching with `match` and `case`. Pattern matching can be preferable when the decision depends on the structure of data rather than only numerical or Boolean comparisons.

`if`/`elif` remains appropriate for ordinary threshold and Boolean rules.

---

## C++ case study

The C++ program models a financial order-processing service.

Each order contains:

- order ID
- customer type
- amount
- country
- verification status

The customer type is represented with an enumeration:

    enum class CustomerType {
        Regular,
        Premium,
        Enterprise,
        Unknown
    };

The order evaluation function applies several levels of conditional logic.

### Validation stage

The program first checks:

- positive order ID
- positive amount
- non-empty country

Invalid orders are rejected before business rules are evaluated.

### Geographic stage

The system checks whether the country is supported.

A `std::set` contains the supported country codes.

This is preferable to an unnecessarily long chain such as:

    if (country == "IN") ...
    else if (country == "US") ...
    else if (country == "GB") ...

when the problem is fundamentally a membership test.

### Verification stage

Orders worth at least 500,000 require verification.

The rule is represented as a compound condition:

    if (order.amount >= 500000.0 && !order.verified)

This demonstrates how Boolean operators extend `if` statements beyond simple comparisons.

### Customer classification

The program then distinguishes:

- enterprise
- premium
- regular
- unknown

Each customer category has its own amount thresholds.

Unknown customer types are rejected.

### Decision object

The C++ program returns a structured `Decision` containing:

- status
- reason
- priority

This is more useful than returning only a Boolean because real systems often need to explain what decision was made.

---

## C++ case-study architecture

The program separates responsibilities into functions and data structures.

### Domain model

`Order` represents an order.

`CustomerType` represents customer classification.

`DecisionStatus` represents the result.

`Decision` contains the decision result and its explanation.

### Validation

`validateOrder()` checks structural validity.

### Membership

`isSupportedCountry()` checks supported geographic regions.

### Decision engine

`evaluateOrder()` applies ordered business rules.

### Reporting

`printOrderDecision()` converts the structured result into human-readable output.

### Aggregation

`calculateStatistics()` processes multiple orders and counts:

- approved orders
- review orders
- rejected orders
- total approved value

This demonstrates how simple conditional statements can become part of a larger application architecture.

---

## Complexity considerations

The cost of an `if` statement itself is normally constant time, O(1).

A simple chain such as:

    if x == 1:
        ...
    elif x == 2:
        ...
    elif x == 3:
        ...

has a number of comparisons proportional to the number of branches in the worst case.

When a decision consists of a large membership list, a data structure may be more appropriate.

For example:

- list search: generally O(n)
- set membership: approximately O(1) average case for hash-based sets
- balanced tree sets: generally O(log n)

The exact performance characteristics depend on the language and data structure.

For small numbers of conditions, readability usually matters more than micro-optimization.

---

## Performance considerations

Conditional performance can be influenced by:

- number of conditions
- cost of expressions
- expensive function calls inside conditions
- repeated membership checks
- data structure selection
- frequency of each branch
- compiler optimizations
- CPU branch prediction in low-level performance-sensitive code

Avoid unnecessary work inside a condition.

For example, this can be inefficient:

    if expensive_function() and another_expensive_function():
        ...

when an inexpensive condition could reject most cases first.

A better ordering can be:

    if not basic_validation:
        return False

    if expensive_function():
        ...

This is both a performance and readability consideration.

---

## Common mistakes

### Using assignment instead of comparison

In Python:

    if age = 18:

is invalid syntax.

The equality comparison is:

    if age == 18:

In JavaScript, accidental assignment inside a condition can produce incorrect behavior.

Use `===` for strict equality.

### Incorrect branch ordering

A broad condition placed before a specific condition can prevent the specific branch from ever executing.

### Confusing `if` and `elif`

Use `elif` when only one outcome should be selected.

Use independent `if` statements when multiple properties may simultaneously apply.

### Excessive nesting

Deep nesting can make logic difficult to understand.

Guard clauses often simplify the structure.

### Complex Boolean expressions

Long expressions with several `and`/`or` operations can become ambiguous.

Use parentheses or split the decision into named variables or functions.

### Incorrect boundary operators

Confusing `>` with `>=` can create errors at exact threshold values.

### Assuming all languages have identical truthiness rules

Python, JavaScript, and C++ do not have identical condition semantics.

Language-specific behavior must be understood before porting conditional code.

---

## Exceptions and failure handling

Conditional statements can detect expected invalid states, but they do not replace exception handling.

For example, converting malformed text to an integer may fail before a range condition can be evaluated.

Python uses `try`/`except`.

JavaScript uses `try`/`catch`.

C++ can use exceptions such as `std::invalid_argument` and `std::out_of_range`.

A robust program separates:

- parsing failure
- validation failure
- business-rule rejection
- unexpected system errors

This distinction makes error handling easier to understand.

---

## Testing conditional logic

Conditional code should be tested across all meaningful branches.

For a grade function, tests should include:

- values below every threshold
- values exactly at every threshold
- values just above or below every threshold
- minimum valid values
- maximum valid values
- invalid values

The three implementations contain executable tests for major decision functions.

This is particularly important because conditional bugs often occur not in the normal case but at boundaries or unusual combinations of conditions.

---

## Edge cases

Important edge cases for conditional logic include:

- empty input
- missing values
- `None` in Python
- `null` or `undefined` in JavaScript
- zero
- negative values
- values exactly equal to thresholds
- values slightly below thresholds
- values slightly above thresholds
- invalid numeric input
- unknown categories
- unsupported countries
- inactive accounts
- missing permissions
- conflicting business rules

The correct behavior should be defined explicitly rather than left to accidental control flow.

---

## Decision tables

For complicated business rules, a decision table can make requirements easier to reason about.

For the order-processing case:

| Condition | Result |
|---|---|
| Invalid amount | Reject |
| Unsupported country | Reject |
| High value and unverified | Reject |
| Enterprise and high amount | High-priority approval |
| Enterprise and medium amount | Priority approval |
| Premium and high amount | High-priority approval |
| Regular and high amount | Manual review |
| Regular and normal amount | Standard approval |
| Unknown customer type | Reject |

The order of evaluation determines which rule takes precedence when several conditions could apply.

---

## Important distinctions

### `if` versus `elif`

`if` starts a conditional chain.

`elif` adds another mutually exclusive branch.

### `elif` versus `else`

`elif` has a condition.

`else` has no condition and executes when every preceding condition is false.

### Independent `if` versus an `if`/`elif` chain

Independent `if` statements can execute multiple branches.

An `if`/`elif`/`else` chain selects at most one branch.

### Conditional logic versus data-driven lookup

A small number of rules may be easiest to express with `if`/`elif`.

A large set of simple value mappings may be better represented with a dictionary, map, set, or other data structure.

### Validation versus authorization

Validation determines whether input is acceptable.

Authorization determines whether an actor is permitted to perform an operation.

These concerns should not be accidentally combined into one unclear condition.

---

## Best practices

Use conditions that are easy to read and test.

Prefer meaningful names:

    if account_is_active:
        ...

rather than cryptic expressions involving unrelated variables.

Keep related rules together.

Validate inputs before applying complex business rules.

Use guard clauses when they reduce nesting.

Order mutually exclusive threshold rules carefully.

Use explicit parentheses for complicated Boolean expressions.

Use strict equality in JavaScript unless type coercion is intentionally required.

Use `is None` for Python `None` checks.

Use appropriate collections for large membership rules.

Keep security decisions fail-closed where appropriate.

Write tests for every branch and important boundary.

Extract complicated decisions into named functions.

Avoid duplicating the same condition across many parts of an application.

---

## Limitations of large `if`/`elif` chains

Conditional statements are fundamental, but a very large chain can become difficult to maintain.

For example, hundreds of branches may indicate that the problem is better represented by:

- a lookup table
- a dictionary
- a set
- a class hierarchy
- a strategy pattern
- a rule engine
- structural pattern matching
- configuration-driven rules

The appropriate alternative depends on whether the problem is value lookup, type dispatch, structured matching, business rules, or algorithmic processing.

The goal is not to eliminate `if` statements. The goal is to use the representation that best matches the problem.

---

## Practical applications

Conditional statements are used throughout software systems.

### Web applications

- authentication
- authorization
- request validation
- HTTP status selection
- feature flags
- form validation

### Financial systems

- transaction validation
- fraud classification
- risk scoring
- loan eligibility
- pricing
- portfolio rules

### Data processing

- missing-value handling
- classification
- filtering
- data quality checks
- anomaly detection

### Automation

- selecting actions
- retry decisions
- error handling
- workflow routing

### Games

- player state
- collision handling
- scoring
- level progression
- enemy behavior

### Embedded and systems software

- sensor thresholds
- device states
- error states
- safety checks
- hardware control logic

---

## Implementation comparison

| Concept | Python | JavaScript | C++ |
|---|---|---|---|
| First branch | `if` | `if` | `if` |
| Additional branch | `elif` | `else if` | `else if` |
| Fallback | `else` | `else` | `else` |
| AND | `and` | `&&` | `&&` |
| OR | `or` | `||` | `||` |
| NOT | `not` | `!` | `!` |
| Equality | `==` | `===` normally preferred | `==` |
| Conditional expression | `x if c else y` | `c ? x : y` | `c ? x : y` |
| Null-like value | `None` | `null`, `undefined` | commonly `nullptr` for pointers |
| Block syntax | indentation | `{}` | `{}` |
| Membership | `in` | `Set.has()` or other structures | containers such as `std::set` |

The core decision-making principle remains the same across the three languages, while the syntax and type semantics differ.

---

## Python implementation

The Python script is designed as a complete study file.

It demonstrates:

- basic `if`
- `if`/`else`
- `if`/`elif`/`else`
- comparison operators
- Boolean operators
- truthiness
- membership
- identity checks
- input validation
- nested conditions
- guard clauses
- conditional expressions
- functions containing decision rules
- boundary testing
- short-circuit evaluation
- independent `if` statements
- rule engines
- dataclasses
- exception handling
- assignment expressions
- `None` handling
- structural pattern matching
- loops containing conditions
- performance-related membership decisions
- authorization
- lightweight tests
- a complete order-processing decision engine

The Python implementation emphasizes the semantics of Python's conditional expressions and truth-value testing.

---

## JavaScript implementation

The JavaScript file complements the Python implementation with JavaScript-specific behavior.

It demonstrates:

- `if`
- `else if`
- `else`
- strict equality
- JavaScript truthiness
- empty arrays and objects as truthy values
- Boolean operators
- validation
- guard clauses
- the conditional operator
- object-oriented decision logic
- `Set` membership
- nullish coalescing
- asynchronous decision-making
- browser environment checks
- authorization
- performance considerations
- executable assertions
- a complete order decision engine

The asynchronous example is particularly relevant to JavaScript applications because conditional decisions frequently depend on data returned by asynchronous operations.

---

## C++ implementation

The C++ program presents an industry-style financial order-processing case study.

The system models:

- customer types
- orders
- decision statuses
- validation results
- authorization requests
- order priorities
- supported countries
- aggregate order statistics

The decision engine applies a sequence of ordered rules.

The implementation demonstrates how `if`, `else if`, and `else` participate in a larger architecture rather than existing only as isolated syntax examples.

It also uses:

- `enum class`
- structures
- functions
- `std::set`
- `std::optional`
- exception handling
- input parsing
- validation
- reporting
- assertions
- aggregation
- complexity-aware data structures

The default-deny authorization behavior illustrates a security-oriented use of conditional logic.

---

## Conceptual flow of the case study

The C++ order engine follows this sequence:

1. Validate the order ID.
2. Validate the amount.
3. Validate the country field.
4. Check whether the country is supported.
5. Require verification for sufficiently large orders.
6. Determine the customer category.
7. Apply customer-specific amount thresholds.
8. Return approval, review, or rejection.
9. Attach a reason and priority.
10. Aggregate decisions for reporting.

This is a realistic example of why condition order matters. A high-value unverified order must be rejected before a later customer-specific rule can approve it.

---

## Production considerations

In production systems, conditional logic should be designed around explicit requirements.

Business rules should be documented before implementation.

Security-sensitive conditions should be tested against both allowed and denied cases.

Input should be validated at system boundaries.

Authorization should be enforced on the server side when the resource is protected.

Complex business rules should be isolated into testable components.

Large rule sets should be reviewed periodically because rule precedence can change system behavior.

Logs should capture important decisions without exposing sensitive information.

Performance optimization should be based on measurement rather than assumptions.

Conditional code should remain deterministic where possible, particularly for financial and compliance-related decisions.

---

## Relationship to broader programming concepts

Conditional statements are connected to several fundamental programming ideas.

### Control flow

`if`, `elif`, and `else` determine which instructions execute.

### Boolean algebra

Complex decisions are constructed from logical operators.

### Functions

Functions encapsulate decision rules.

### Data structures

Sets, dictionaries, maps, and other collections can replace repetitive conditional comparisons.

### Object-oriented programming

Methods can make decisions based on object state.

### Error handling

Conditions detect expected invalid states while exceptions handle failures that cannot be represented as ordinary successful control flow.

### Testing

Each branch represents behavior that can be tested independently.

### Security

Authorization and validation rely heavily on correct conditional ordering.

### Performance

The number and cost of conditions can influence execution time, especially when decisions occur inside large loops.

---

## Core principles demonstrated

The implementations establish several important principles:

1. A condition determines whether a branch executes.
2. Conditions are evaluated according to language-specific semantics.
3. An `elif`/`else if` chain selects the first matching branch.
4. `else` is the fallback when no earlier branch matches.
5. Branch ordering can change program behavior.
6. Independent `if` statements can all execute.
7. Boolean operators allow multiple conditions to be combined.
8. Short-circuit evaluation can prevent unnecessary or unsafe operations.
9. Boundary values require explicit testing.
10. Guard clauses can reduce nesting.
11. Complex rules should be isolated into reusable functions.
12. Data structures can replace unnecessarily large conditional chains.
13. Security decisions should normally fail closed.
14. Performance should be considered in frequently executed decision paths.
15. Conditional behavior should be tested across normal, boundary, and invalid cases.

These principles apply from small scripts to larger software systems.
