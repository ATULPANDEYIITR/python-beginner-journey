# Nested Conditions

## Topic introduction

Nested conditions are conditional statements placed inside other conditional statements. They allow a program to make a decision, then make another decision based on the result of the first decision.

A simple condition has one decision:

`if condition -> action`

A nested condition creates a decision hierarchy:

`if first condition -> if second condition -> action`

This structure is useful when later rules depend on earlier conditions. It appears in authentication, authorization, validation, pricing, eligibility systems, workflow engines, games, simulations, form processing, business rules, and many other software systems.

The three implementations in this repository demonstrate the concept from different programming perspectives:

- Python provides compact syntax and allows the decision logic to be expressed clearly with functions, classes, enumerations, dataclasses, assertions, and a general decision-tree structure.
- JavaScript demonstrates nested conditions in an application-oriented language, including truthiness, arrays, classes, asynchronous operations, promises, and `async`/`await`.
- C++ develops the topic into an industry-style case study using strongly typed structures, classes, enumerations, collections, exceptions, validation, a decision-tree data structure, and a loan decision engine.

The central idea is not simply to make conditions deeper. The important engineering problem is to express dependent decisions correctly, validate inputs, handle boundary cases, and keep decision logic understandable.

## Fundamental concepts

A condition is an expression that produces a Boolean result.

In Python and C++, Boolean values are represented by `True` and `False`, and `true` and `false`, respectively. JavaScript uses `true` and `false` but also has a broader truthiness system.

The basic structure is:

`if condition:`

followed by an indented block in Python.

In JavaScript and C++, braces define the block:

`if (condition) { ... }`

An `else` branch executes when the condition is false.

An `elif` in Python and an `else if` in JavaScript and C++ allow additional alternatives to be tested.

## Terminology

### Condition

A Boolean expression that determines which branch should execute.

Examples include:

- `age >= 18`
- `score >= 40`
- `account.active`
- `creditScore >= 750`

### Branch

A possible execution path controlled by a conditional statement.

### Nested condition

A conditional statement located inside another conditional branch.

### Decision tree

A collection of decisions arranged as a hierarchy. Each decision can lead to another decision or to a final result.

### Boolean operator

An operator used to combine or transform conditions.

Common operators include:

- Python: `and`, `or`, `not`
- JavaScript: `&&`, `||`, `!`
- C++: `&&`, `||`, `!`

### Guard clause

An early return used to reject an invalid or irrelevant case before reaching the main decision logic.

### Truthiness

A language feature in which values other than explicit Boolean values can be interpreted as true or false in a conditional context.

## The basic `if` statement

A basic condition checks one rule.

The Python implementation demonstrates:

`if age >= 18:`

The JavaScript implementation uses:

`if (age >= 18)`

The C++ implementation uses the same basic expression inside a strongly typed program.

For an age of 20, the adult branch executes. For an age of 17, the alternative branch executes.

The important principle is that the condition controls program flow. It does not merely calculate a value. It determines which statements execute.

## `if`, `elif`, and `else`

When several alternatives are mutually exclusive, an `if`/`elif`/`else` structure is often clearer than deeply nested conditions.

For example, a score can be mapped to a grade:

- 90 or above: A
- 80 to 89.99: B
- 70 to 79.99: C
- lower values: another category

The first matching branch executes.

The order of conditions matters. A condition such as `score >= 70` placed before `score >= 90` would capture scores that might otherwise belong to the higher category.

This illustrates an important rule:

> Conditional branches are evaluated in order.

## What makes a condition nested?

Consider the conceptual rule:

1. The person must be at least 18.
2. If they are at least 18, they must also provide identification.
3. Only when both requirements are satisfied is access granted.

The second decision is dependent on the first.

The implementations express this as:

`if age >= 18`

followed by a second condition checking identification.

The inner condition is not evaluated as an independent business decision. It belongs to the branch created by the outer condition.

This creates a hierarchy:

- age requirement
  - identity document present
    - grant access
    - deny access
  - deny access because of age

## Why nesting exists

Nested conditions are useful when later information only becomes relevant after an earlier requirement is satisfied.

For example:

- check whether an account exists
  - check whether it is active
    - check whether the user has a permission
      - allow
      - deny
  - deny because inactive
- user not found

This structure appears in the Python and JavaScript permission examples and the C++ collection example.

## Nested conditions versus compound conditions

The same logic can sometimes be expressed in two ways.

A nested form can look conceptually like:

`if adult -> if has ID -> if active -> allow`

A compound condition can express the requirements as one expression:

`adult AND has ID AND active`

The Python and JavaScript implementations deliberately demonstrate both forms.

These forms can be logically equivalent, but they communicate different things.

A compound condition is often concise when all requirements are independent and produce the same outcome.

Nested conditions can be useful when different failures need different messages.

For example:

- under 18
- missing identification
- inactive account

If every failure has the same result, a compound condition can be appropriate. If each failure has a different business meaning, nested branching may communicate the decision structure more directly.

## Boolean operators

### AND

AND requires all participating conditions to be true.

Python:

`age >= 18 and has_id`

JavaScript and C++:

`age >= 18 && hasId`

A typical use is:

`adult AND verified AND active`

### OR

OR succeeds when at least one condition is true.

Python:

`is_student or is_senior`

JavaScript and C++:

`isStudent || isSenior`

### NOT

NOT reverses a Boolean result.

Python:

`not active`

JavaScript and C++:

`!active`

## Short-circuit evaluation

Short-circuit evaluation prevents unnecessary evaluation of later expressions.

For AND:

`A and B`

If `A` is false, `B` does not need to be evaluated.

For OR:

`A or B`

If `A` is true, the result is already known.

This behavior is demonstrated in the Python program.

It can also protect operations that would otherwise fail.

For example, checking that an object exists before accessing a property can prevent an invalid access:

`user is not None and user.get("active") is True`

The first condition must succeed before the second expression is evaluated.

Short-circuit behavior is also useful for performance because expensive checks can be avoided when an earlier condition already determines the result.

## Deep nesting

The Python, JavaScript, and C++ implementations include exam classification logic with several levels:

- validate the score
  - check attendance
    - check misconduct
      - check score level
        - return the appropriate result

This is technically valid, but deep nesting has a cost.

As nesting depth increases:

- indentation increases
- branches become harder to trace
- testing becomes more difficult
- the number of possible execution paths grows
- maintenance becomes harder
- mistakes become easier to introduce

Deep nesting is therefore not automatically bad, but it should have a clear reason to exist.

## Guard clauses

A guard clause handles a condition immediately and returns.

Instead of:

`if valid:`

followed by several additional levels of nesting, a function can reject invalid states first.

The discount functions in all three implementations use this idea.

Conceptually:

- inactive customer -> return zero
- underage customer -> return zero
- invalid purchase -> return zero
- otherwise evaluate discount thresholds

This produces a flatter structure.

Guard clauses are particularly useful for validation, authorization, parsing, API handlers, and business rules.

## Validation before decision-making

Decision logic should not silently interpret invalid data as meaningful input.

The implementations validate:

- age
- scores
- attendance
- income
- debt
- credit scores
- requested amounts
- collection data

For example, a credit score outside its expected domain should not be treated as simply a low score.

There is a distinction between:

`invalid input`

and:

`valid input that does not satisfy a rule`

That distinction is important in production systems.

## Boundary values

Conditional programs frequently fail at boundaries.

Consider:

`score >= 40`

The values around the boundary are:

- 39.99
- 40
- 40.01

The correct branch should be explicitly tested for all meaningful boundaries.

The Python and C++ test suites include boundary tests for age, score, attendance, and discounts.

Boundary testing is especially important for:

- financial thresholds
- age restrictions
- quotas
- percentages
- dates
- numerical ranges
- access-control rules
- rate limits

## Truthiness in Python

Python treats several values as false in Boolean contexts.

Examples include:

- `False`
- `None`
- numeric zero
- empty strings
- empty collections

Non-empty collections and non-empty strings are generally truthy.

The Python program demonstrates explicit Boolean logic as well as truthiness.

A good practice is to avoid relying on implicit truthiness when the distinction between values is important.

For example, `if value:` is not equivalent to `if value is not None:`.

The first checks truthiness. The second specifically checks whether the object is not `None`.

## Truthiness in JavaScript

JavaScript has its own truthiness rules.

Common falsy values include:

- `false`
- `0`
- `-0`
- `""`
- `null`
- `undefined`
- `NaN`

An important JavaScript peculiarity is that empty arrays and empty objects are truthy.

Therefore:

`if ([])`

is true.

And:

`if ({})`

is also true.

This differs from Python, where empty lists and empty dictionaries are falsy.

Understanding language-specific truthiness rules prevents subtle conditional bugs.

## Conditional expressions

Python has conditional expressions such as:

`value_if_true if condition else value_if_false`

JavaScript and C++ provide the conditional operator:

`condition ? valueIfTrue : valueIfFalse`

These are useful for short decisions.

They become difficult to read when many conditional expressions are nested.

The Python and JavaScript programs deliberately include nested conditional expressions to illustrate this trade-off.

A useful rule is to favor readability over compactness.

## `match` and `switch`

Nested `if` statements are not the only way to represent branching.

Python's `match`/`case` is useful for pattern and categorical matching.

JavaScript and C++ provide `switch`.

A `switch` is particularly suitable when one value is being compared against several discrete alternatives.

For example:

- HTTP 200
- HTTP 201
- HTTP 400
- HTTP 404

Range-based conditions are often more naturally expressed with `if` statements.

The Python implementation also demonstrates a guarded `case` for a range of server error status codes.

## Nested conditions with collections

A realistic application often combines a collection lookup with nested conditions.

The example permission logic follows this hierarchy:

- find the user
  - if the user is active
    - if permissions are correctly represented
      - if the required permission exists
        - grant access
      - otherwise deny
    - invalid permission data
  - inactive account
- user not found

This demonstrates why nested conditions can represent a business workflow rather than simply a syntax exercise.

## Object-oriented decision logic

The Python implementation introduces:

- `Account`
- `AccountDecisionEngine`
- `LoanApplication`
- `LoanDecisionEngine`

The JavaScript implementation introduces corresponding classes.

The C++ implementation uses structures and classes with strong typing.

Moving decision logic into a class can provide:

- encapsulation
- reusable rules
- testable methods
- separation of data from processing
- clearer ownership of business logic

The objective is not to use classes merely because they exist. Classes are useful when a collection of data and related behavior forms a coherent responsibility.

## Enumerations

The Python implementation uses `Enum`.

The C++ implementation uses `enum class`.

Enumerations represent a fixed set of categories more safely than arbitrary strings.

For example:

`GUEST`

`USER`

`ADMIN`

This makes invalid categories harder to express accidentally and makes the domain model clearer.

JavaScript does not have the same built-in enumeration mechanism as Python or C++, so the implementation uses ordinary strings for role values.

## Decision trees

A deeply nested collection of conditions can be viewed as a decision tree.

For example:

- four wheels?
  - yes -> powered?
    - yes -> passenger focused?
      - yes -> car
      - no -> utility vehicle
    - no -> non-powered four-wheel vehicle
  - no -> two wheels?
    - yes -> two-wheel vehicle
    - no -> other vehicle

The three implementations model this idea explicitly.

Python uses a `DecisionNode` dataclass.

JavaScript uses a `DecisionNode` class.

C++ stores nodes in a vector and connects them using indices.

This is an important conceptual transition:

A conditional structure can be represented as code, but a decision process can also be represented as data.

Once represented as data, a system can potentially load, modify, validate, or inspect rules without rewriting the entire traversal algorithm.

## Recursive versus iterative decision processing

The Python decision-tree implementation uses iterative traversal.

A node is selected, an answer determines the next node, and the process continues until a result is reached.

A decision tree could also be traversed recursively.

Recursive traversal can be elegant for tree-shaped data because a subtree is itself a smaller tree.

Iterative traversal has the advantage of making the execution stack explicit and can avoid recursion-depth issues for very deep trees.

## Error handling

Conditional logic should distinguish expected business outcomes from programming failures.

Examples:

`Rejected: insufficient balance`

and:

`Invalid input`

are normal application outcomes.

An unexpected exception may represent a programming error, infrastructure failure, or corrupted state.

Python uses `try`/`except`.

JavaScript uses `try`/`catch`.

C++ uses exceptions such as `std::runtime_error` and `std::out_of_range`.

The C++ main function catches unexpected standard exceptions so the program can terminate in a controlled manner.

## Authentication and authorization

The authorization examples demonstrate an important conceptual distinction.

Authentication asks:

"Who is the user?"

Authorization asks:

"What is this authenticated user allowed to access?"

The sample decision process checks:

- authentication
- role
- resource type
- resource ownership

The implementation is intentionally simplified. It is a demonstration of conditional structure rather than a production identity system.

Real systems should not rely solely on client-side checks or simple strings to protect sensitive resources. Authorization should be enforced on the trusted server side, with appropriate identity verification, access-control rules, auditing, and secure handling of credentials.

## Performance considerations

Most ordinary conditional checks are constant-time operations.

A simple chain such as:

- check A
- check B
- check C

is approximately O(1) when the number of conditions is fixed.

A loop containing nested conditions may become O(n), where `n` is the number of records.

The user-permission examples search through a vector/list of users. In the worst case, a linear scan is O(n).

The C++ permission example uses an `unordered_set` for permissions. Average membership lookup is approximately O(1), although worst-case behavior can be different.

The programs also demonstrate ordering cheap checks before expensive checks.

If an inexpensive condition can reject the request, performing it before an expensive calculation avoids unnecessary work.

## Complexity of decision trees

For a single path through a decision tree, evaluation visits one node per decision.

If a tree has depth `d`, evaluating one input is O(d).

The total number of possible Boolean paths can grow exponentially with depth. A full binary tree of depth `d` can have up to 2^d leaves.

This is why testing becomes more difficult as conditional systems grow.

The problem is not necessarily runtime performance. It is also the number of logical paths that must be reasoned about and tested.

## Testing nested conditions

Nested conditions should be tested by branch and boundary.

Important test categories include:

- outer condition true
- outer condition false
- inner condition true
- inner condition false
- multiple nested conditions true
- multiple nested conditions false
- invalid input
- minimum boundary
- maximum boundary
- just below a boundary
- exactly at a boundary
- just above a boundary
- missing data
- unexpected categories

The Python implementation uses assertions.

The JavaScript implementation includes a small assertion helper.

The C++ implementation includes explicit test functions that throw exceptions when an expectation fails.

## Common mistakes

### Incorrect branch ordering

A broad condition can prevent a more specific condition from being reached.

For example, checking:

`score >= 70`

before:

`score >= 90`

would classify a score of 95 as the lower category.

Specific thresholds should be ordered appropriately.

### Excessive nesting

Deep indentation can make code difficult to read.

When independent rejection conditions exist, guard clauses can reduce unnecessary nesting.

### Confusing validation with business logic

Invalid data should not automatically be treated as a legitimate negative decision.

For example, a credit score of 1200 should be rejected as invalid rather than classified as simply "low" or "high".

### Relying on implicit truthiness

A value being truthy does not necessarily mean it represents the intended business state.

For example, an empty collection, zero, or `None` can have different meanings depending on the application.

### Forgetting boundary values

A rule such as `age >= 18` has a critical boundary at 18.

Testing only age 25 does not prove that the boundary is implemented correctly.

### Mixing unrelated responsibilities

A single conditional function that validates input, authenticates a user, calculates pricing, writes to a database, and sends notifications becomes difficult to test.

Separating responsibilities makes the decision logic easier to understand.

### Duplicating rules

If the same nested rule appears in many places, changing the rule requires changing many locations.

Centralizing business rules reduces inconsistency.

### Unclear Boolean precedence

Expressions containing several `and`/`or` operations can be difficult to interpret.

Parentheses can make the intended grouping explicit.

## Edge cases

Important edge cases for conditional systems include:

- zero
- negative values
- empty strings
- empty collections
- null-like values
- missing properties
- invalid numeric values
- exact threshold values
- values immediately outside thresholds
- maximum accepted values
- minimum accepted values
- unknown categories
- inactive accounts
- missing permissions
- insufficient answers in a decision tree

The supplied implementations deliberately exercise several of these cases.

## Python-specific considerations

Python uses indentation to define conditional blocks.

This makes structure visually obvious but means indentation is syntactically significant.

Python supports:

- `if`
- `elif`
- `else`
- conditional expressions
- `match`/`case`
- Boolean operators `and`, `or`, `not`

Python also provides convenient data modeling with `dataclass` and `Enum`, both used in the implementation.

Python's `match` statement is useful for structural and categorical branching, while ordinary `if` statements remain appropriate for ranges and complex Boolean expressions.

## JavaScript-specific considerations

JavaScript uses braces to define conditional blocks.

It also has a broad truthiness system, so developers must understand the difference between:

- strict Boolean conditions
- truthy values
- falsy values

The JavaScript implementation uses strict equality such as `===`.

Strict equality avoids many type-conversion surprises associated with loose equality.

JavaScript also supports asynchronous execution through promises and `async`/`await`.

The asynchronous example demonstrates that nested conditional logic still applies when information arrives asynchronously.

The program first waits for the account status and then makes decisions based on the returned data.

## C++-specific considerations

C++ provides strong static typing and compile-time checking.

The C++ case study uses:

- `struct`
- `class`
- `enum class`
- `std::vector`
- `std::unordered_set`
- `std::optional`
- exceptions
- structured bindings
- standard library algorithms and types

The type system helps make the domain model explicit.

For example, `enum class DecisionStatus` restricts decision states to known categories.

C++ also allows developers to reason closely about performance and memory behavior, which becomes useful when nested decision logic operates over large collections or high-throughput systems.

## Python, JavaScript, and C++ comparison

| Aspect | Python | JavaScript | C++ |
|---|---|---|---|
| Conditional syntax | `if`, `elif`, `else` | `if`, `else if`, `else` | `if`, `else if`, `else` |
| Boolean AND | `and` | `&&` | `&&` |
| Boolean OR | `or` | `||` | `||` |
| Boolean NOT | `not` | `!` | `!` |
| Conditional expression | `x if c else y` | `c ? x : y` | `c ? x : y` |
| Pattern/categorical branching | `match` | `switch` | `switch` |
| Main block delimiter | Indentation | Braces | Braces |
| Truthiness | Built in | Extensive coercion rules | Mostly explicit Boolean conversion |
| Strong static typing | No | No | Yes |
| Enumeration support | `Enum` | Usually modeled manually | `enum class` |
| Exception handling | `try`/`except` | `try`/`catch` | `try`/`catch` |
| Asynchronous model | Available through libraries/runtime | Core application feature | Available through libraries and concurrency facilities |
| Decision-tree example | Dataclass nodes | Class-based nodes | Strongly typed indexed nodes |

## C++ case study

### Problem being modeled

The C++ program models a simplified loan application decision engine.

An application contains:

- applicant name
- age
- monthly income
- monthly debt
- credit score
- employment history
- identity verification state
- requested amount
- employment type

The program first validates the application.

It then evaluates nested business rules.

The thresholds are explicitly educational examples and do not represent an actual financial institution's underwriting policy.

### Validation layer

The engine checks:

- applicant name
- age range
- positive income
- non-negative debt
- credit score range
- non-negative employment history
- positive requested amount

This prevents invalid data from entering the business decision stage.

### Identity requirement

After basic validation, identity verification is checked.

If identity verification fails, the application is rejected before further business rules are evaluated.

This demonstrates dependent decision flow.

### Debt-to-income calculation

The program calculates:

`debtToIncome = monthlyDebt / monthlyIncome`

Because positive income has already been validated, division by zero is avoided.

### Credit-score branch

The engine creates a primary decision based on credit score.

For a high example score, the engine evaluates the debt-to-income ratio.

If that condition passes, employment history becomes relevant.

This is a nested dependency:

`credit score -> debt-to-income -> employment history`

For a moderate score, a different debt-to-income threshold and employment-history requirement are applied.

Lower scores reach a rejection branch.

### Decision result

The engine returns a `DecisionResult` containing:

- decision status
- reason

The status is represented with `enum class`.

Possible states are:

- `Approved`
- `ManualReview`
- `Rejected`

This is clearer than returning unrelated Boolean values.

A Boolean such as `true` or `false` would not distinguish approval from manual review.

## Decision tables and nested conditions

Nested conditions can be understood as executable decision tables.

For example:

| Credit profile | DTI condition | Employment condition | Result |
|---|---|---|---|
| High | Within standard threshold | Sufficient | Approved |
| High | Within standard threshold | Insufficient | Manual review |
| High | Above standard threshold | Any | Manual review |
| Moderate | Within moderate threshold | Sufficient | Manual review |
| Moderate | Within moderate threshold | Insufficient | Manual review |
| Moderate | Above moderate threshold | Any | Rejected |
| Low | Not applicable | Not applicable | Rejected |

The nested program is one way to encode this table.

For larger systems, a decision table or rule engine can sometimes be easier to maintain than deeply nested source code.

## When nested conditions are appropriate

Nested conditions are appropriate when:

- later decisions depend on earlier decisions
- different branches require different follow-up checks
- the hierarchy reflects the actual business process
- each branch remains understandable
- the number of conditions is manageable

Examples include:

- authentication followed by authorization
- input validation followed by processing
- order existence followed by order state
- customer status followed by pricing rules
- transaction validation followed by fraud checks
- device type followed by capability checks

## When nesting should be reduced

Nesting should be reconsidered when:

- indentation becomes excessive
- many branches perform the same operation
- the same rule appears repeatedly
- conditions are difficult to name
- testing becomes complicated
- business rules change frequently
- a decision table would be clearer
- a strategy or rule-object design would better represent the domain

Reducing nesting does not mean eliminating all nested conditions. It means choosing a structure that matches the complexity of the decision system.

## Alternative design patterns

### Guard clauses

Use early returns for invalid states.

This is effective when rejection conditions are independent.

### Boolean helper functions

Instead of embedding a complex expression directly in a large function, create a named function.

For example:

`isEligibleForTransfer()`

can communicate intent better than a long Boolean expression.

### Decision tables

Decision tables make combinations of conditions explicit.

They are useful when many combinations of inputs determine a small number of outcomes.

### Rule objects

A large rule system can represent each business rule as an object or function.

This can make rules independently testable.

### State machines

If decisions depend strongly on the current state of an entity, a state-machine model may be more suitable than deeply nested conditions.

Examples include:

- order lifecycle
- payment lifecycle
- support ticket workflow
- deployment lifecycle

### Decision trees

Decision trees are suitable when each answer naturally leads to another question.

The supplied implementations demonstrate how the tree can be represented as data rather than hard-coded indentation.

## Security considerations

Nested conditions frequently appear in security-sensitive code.

Typical security decisions include:

- whether a user is authenticated
- whether an account is active
- whether a user has a role
- whether a resource belongs to the current user
- whether a requested operation is permitted

Security decisions should be implemented carefully.

A client-side condition such as:

`if (userIsAdmin)`

does not itself provide security.

An attacker can manipulate client-side code or requests.

Authorization must be enforced by the trusted server or security boundary.

Security-sensitive conditions should also avoid relying on unvalidated user input.

The supplied authorization examples demonstrate the structure of security decisions but are not production authentication systems.

## Data validation and security

Validation helps prevent malformed data from reaching business logic.

Important principles include:

- validate types
- validate ranges
- reject impossible values
- distinguish missing data from false values
- use allowlists for categorical inputs where appropriate
- avoid trusting client-side state
- perform authorization on the trusted side
- avoid exposing unnecessary internal decision details

A production application may require additional protections depending on the domain.

## Maintainability

Conditional logic is easier to maintain when:

- conditions have meaningful names
- branches have one clear responsibility
- repeated logic is extracted
- validation is separated from processing
- business rules are documented
- tests cover boundaries
- functions remain reasonably small
- decision structures match the domain

The three implementations intentionally use descriptive names such as:

`classifyExamResult`

`findUserPermission`

`calculateDiscount`

`evaluateTransfer`

`evaluate`

These names communicate the purpose of the decision logic without requiring the reader to inspect every branch first.

## Debugging nested conditions

When debugging a nested conditional, identify the exact branch that was expected and compare it with the branch actually executed.

A practical debugging process is:

- inspect the input values
- evaluate the outer condition
- evaluate each inner condition in order
- check boundary comparisons
- check Boolean operator grouping
- check whether earlier branches capture the input
- verify that invalid inputs are rejected correctly
- reproduce the issue with a minimal test case

Logging can help in production systems, but sensitive information should not be written to logs unnecessarily.

## Testing strategy

A robust test suite should not only test successful outcomes.

For a nested decision tree, tests should cover every meaningful branch.

For the loan example, this includes:

- invalid age
- invalid income
- invalid debt
- invalid credit score
- invalid requested amount
- unverified identity
- high credit score with acceptable DTI
- high credit score with excessive DTI
- high credit score with insufficient employment history
- moderate credit score with acceptable DTI
- moderate credit score with excessive DTI
- low credit score

Boundary testing should include exact threshold values and values immediately above and below them.

## Implementation considerations

The Python implementation emphasizes readability and rapid experimentation.

The JavaScript implementation demonstrates how nested conditions work in application and asynchronous environments.

The C++ implementation emphasizes strong types, explicit data structures, predictable memory behavior, and an industry-style architecture.

The underlying logical principles remain the same:

1. evaluate a condition
2. select a branch
3. evaluate dependent conditions when necessary
4. continue until a final result is reached

The language changes the syntax and available abstractions, but not the fundamental control-flow concept.

## Practical applications

Nested conditional logic appears in many systems.

### Authentication

`authenticated -> account active -> verification state`

### Authorization

`authenticated -> role -> resource -> ownership -> permission`

### E-commerce

`product exists -> inventory available -> customer eligible -> discount -> shipping`

### Banking

`account active -> identity verified -> balance sufficient -> transaction allowed`

### Education

`score valid -> attendance valid -> exam result -> classification`

### Healthcare software

`patient exists -> data available -> rule satisfied -> workflow branch`

Actual healthcare decisions require domain-specific validation, governance, and safety controls.

### Cloud systems

`service available -> deployment valid -> environment permitted -> deployment action`

### Cybersecurity

`request received -> identity verified -> policy matched -> resource allowed`

### Games

`player exists -> state active -> action permitted -> outcome calculated`

### Data processing

`record valid -> required fields present -> category identified -> transformation applied`

## Important distinctions

### Nested condition versus sequential conditions

Two conditions written one after another are not necessarily nested.

Nested conditions mean the second condition is located inside a branch of the first condition.

This distinction matters because nesting expresses dependency.

### Nested condition versus compound condition

A compound condition combines several Boolean expressions into one logical expression.

A nested condition creates a hierarchy of decisions.

They may produce the same Boolean result but can communicate different business semantics.

### Validation versus rejection

Validation determines whether data is structurally acceptable.

Rejection is a business outcome after valid data has been evaluated.

Keeping these concepts distinct improves system design.

### Authentication versus authorization

Authentication establishes identity.

Authorization determines permitted actions.

A program can authenticate a user successfully while still denying access to a particular resource.

### Conditional code versus decision data

Simple conditions can be expressed directly in source code.

Large rule systems may be better represented as decision tables, trees, rule objects, or state machines.

## Limitations of nested conditions

Nested conditions are not a universal solution.

Large nested structures can become:

- difficult to read
- difficult to test
- difficult to modify
- difficult to document
- vulnerable to branch-order mistakes
- difficult to represent when rules change frequently

The appropriate design depends on the number of rules, rate of change, domain complexity, and need for dynamic configuration.

## Best practices

Use clear variable names.

Validate inputs before applying business rules.

Keep related conditions together.

Use guard clauses when they reduce unnecessary indentation.

Use parentheses when Boolean grouping is not immediately obvious.

Test boundary values.

Test both successful and unsuccessful branches.

Avoid duplicated conditions.

Prefer strict comparisons where appropriate.

Keep security checks on the trusted side of an application.

Separate authentication from authorization.

Do not allow client-side conditions to serve as the only security boundary.

Use enums or constrained categories when a domain has a fixed set of states.

Consider decision tables or rule structures when conditional logic becomes too large.

Order cheap, safe checks before expensive operations when the ordering does not change semantics.

Document non-obvious business rules.

Use automated tests to prevent changes in one branch from breaking another branch.

## Relationship between nested conditions and control flow

Nested conditions are one part of structured control flow.

Other important control-flow mechanisms include:

- loops
- function calls
- exceptions
- pattern matching
- state transitions
- asynchronous callbacks
- event handlers

Conditional statements determine which path is executed.

Loops determine repetition.

Functions organize reusable behavior.

Exceptions represent exceptional control transfer.

Decision trees and state machines provide higher-level representations for particular classes of control-flow problems.

## Code organization in this repository

The Python file is organized into progressively more advanced sections:

- basic conditions
- Boolean operators
- nested conditions
- deeper nesting
- validation
- edge cases
- compound versus nested logic
- collection processing
- conditional expressions
- guard clauses
- decision tables
- enumerations
- object-oriented decisions
- error handling
- short-circuit evaluation
- `match`/`case`
- decision trees
- authorization
- performance-aware evaluation
- automated tests
- an industry-style loan case study

The JavaScript file follows a parallel educational progression while adding JavaScript-specific behavior:

- truthiness
- strict comparisons
- classes
- arrays
- `switch`
- promises
- `async`/`await`
- JavaScript error handling

The C++ file develops a more structured technical case study:

- typed data models
- enums
- classes
- collections
- `unordered_set`
- optional decision-tree branches
- exception handling
- validation
- a loan decision engine
- assertions
- interactive input handling

## Running the implementations

### Python

Run the Python program with a Python 3 installation:

`python nested_conditions.py`

The program executes its demonstrations automatically.

The interactive age classifier is provided as a separate function so the main demonstration remains deterministic.

### JavaScript

Run the JavaScript program with a modern Node.js runtime:

`node nested-conditions.js`

The asynchronous example executes as part of the main program.

### C++

Compile the C++ program using C++17 or later:

`g++ -std=c++17 -Wall -Wextra -pedantic nested_conditions.cpp -o nested_conditions`

Then run the resulting executable.

The C++ implementation uses only the standard library.

## Educational progression represented by the code

The implementations move through several levels of abstraction.

At the first level, a condition directly controls an output.

At the second level, one condition controls another condition.

At the third level, multiple nested decisions represent a business rule.

At the fourth level, validation and guard clauses improve reliability and readability.

At the fifth level, classes encapsulate decision rules.

At the sixth level, a decision tree represents conditional logic as data.

At the seventh level, the C++ loan engine combines validation, domain modeling, nested rules, calculated metrics, explicit result states, and automated tests into a complete technical case study.

This progression demonstrates that nested conditions are not merely a beginner syntax feature. They are a basic building block from which more sophisticated decision systems can be constructed.
