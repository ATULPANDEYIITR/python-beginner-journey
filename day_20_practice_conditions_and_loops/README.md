# Practice: Conditions and Loops

## Topic introduction

Conditions and loops are fundamental control-flow mechanisms. They determine which instructions execute and how many times those instructions execute.

A program normally executes statements from top to bottom. Conditions introduce decisions into that sequence. Loops introduce repetition. Together, they allow a program to validate input, process collections, search data, calculate results, implement business rules, simulate events, and control larger application workflows.

The three implementations in this repository approach the subject from different technical perspectives:

- The Python implementation develops the concepts progressively and includes a broad collection of executable demonstrations.
- The JavaScript implementation emphasizes language-specific behavior, iterable processing, objects, collections, generators, and asynchronous loops.
- The C++ implementation develops an industry-style transaction-monitoring case study while demonstrating the same control-flow principles with static types, standard containers, exceptions, and explicit complexity considerations.

The examples are deliberately executable rather than purely descriptive. Running the programs allows the behavior of conditions and loops to be observed directly.

---

## Fundamental concepts

### Control flow

Control flow is the order in which program instructions are executed.

Without explicit control-flow statements, most simple programs follow a sequential pattern:

1. Execute the first statement.
2. Execute the second statement.
3. Execute the third statement.
4. Continue until the program finishes.

Conditions and loops modify this sequence.

A condition can cause a block to execute only when an expression is true. A loop can execute a block repeatedly until a collection is exhausted or a condition becomes false.

The major control-flow categories demonstrated in these implementations are:

- sequential execution
- conditional execution
- repeated execution
- early termination
- skipped iterations
- state-based processing
- asynchronous repetition

---

## Boolean values

A Boolean represents one of two logical states:

- `true`
- `false`

Python uses `True` and `False`.

JavaScript and C++ use `true` and `false`.

Conditions depend on Boolean expressions.

Examples include:

- a score being greater than a threshold
- a number being divisible by another number
- a collection containing an item
- a transaction exceeding a limit
- an authentication flag being enabled

A Boolean expression can contain comparison operators and logical operators.

---

## Comparison operators

Common comparison operations include:

| Meaning | Python | JavaScript | C++ |
|---|---|---|---|
| Equal | `==` | `===` | `==` |
| Not equal | `!=` | `!==` | `!=` |
| Less than | `<` | `<` | `<` |
| Less than or equal | `<=` | `<=` | `<=` |
| Greater than | `>` | `>` | `>` |
| Greater than or equal | `>=` | `>=` | `>=` |

JavaScript has an important distinction between strict and loose equality.

`5 === "5"` is false because the values have different types.

`5 == "5"` is true because loose equality performs type conversion.

For predictable application logic, strict equality is generally easier to reason about.

---

## Logical operators

Three fundamental logical operations are:

| Operation | Python | JavaScript | C++ |
|---|---|---|---|
| AND | `and` | `&&` | `&&` |
| OR | `or` | `||` | `||` |
| NOT | `not` | `!` | `!` |

### AND

AND requires both conditions to be true.

A typical expression is:

`age >= 18 and has_id`

The equivalent JavaScript and C++ forms use `&&`.

### OR

OR requires at least one condition to be true.

For example:

`is_student or is_senior`

### NOT

NOT reverses a Boolean value.

For example:

`not is_authenticated`

JavaScript uses `!` and C++ uses `!`.

---

## Short-circuit evaluation

Logical operators can stop evaluating as soon as the final result is known.

Consider:

`value is not None and value > 10`

If `value is not None` is false, Python does not evaluate `value > 10`.

This prevents unsafe operations in many situations.

JavaScript uses `&&` and `||` in a similar short-circuiting manner.

C++ also short-circuits `&&` and `||`.

Short-circuit evaluation can therefore be useful for both performance and safe conditional access.

---

## Python truthiness

Python allows many objects to be evaluated directly in conditions.

Examples of false-like values include:

- `False`
- `None`
- `0`
- `0.0`
- `""`
- `[]`
- `{}`
- `set()`

Non-empty collections and non-zero numbers are normally true-like.

This means a Python program can write:

`if not names:`

instead of explicitly checking:

`if len(names) == 0:`

The first form directly expresses the logical intent.

---

## JavaScript truthiness

JavaScript also converts values to Boolean values when they appear in conditions, but its rules differ from Python.

Important falsy JavaScript values include:

- `false`
- `0`
- `-0`
- `0n`
- `""`
- `null`
- `undefined`
- `NaN`

An empty array is truthy:

`[]`

An empty object is also truthy:

`{}`

This distinction is important because developers coming from Python may incorrectly assume that an empty JavaScript array or object behaves like an empty Python list or dictionary in a condition.

---

## C++ Boolean conditions

C++ conditions can use the built-in `bool` type.

Integer expressions can also participate in conditions according to C++ conversion rules. Zero converts to false and non-zero values convert to true.

For readable production code, explicit Boolean expressions are usually preferable to relying on implicit integer-to-Boolean conversion when the intended meaning is not obvious.

---

## if statements

An `if` statement executes a block when its condition is true.

The basic conceptual structure is:

`if condition:`

in Python, while JavaScript and C++ use a form based on parentheses and braces.

An `if` statement is appropriate when there is a single decision.

Examples from the implementations include:

- checking whether a person is old enough
- checking whether a score is valid
- checking whether a transaction is positive
- checking whether a search found a target

---

## elif and else if

Python uses `elif` to represent another mutually exclusive condition.

JavaScript and C++ use `else if`.

The grade classifier demonstrates a sequence such as:

- 90 or above: A
- 80 or above: B
- 70 or above: C
- 60 or above: D
- otherwise: F

The order of conditions matters.

If a condition such as `score >= 60` appeared before `score >= 90`, a score of 95 would match the earlier condition and never reach the more specific condition.

This is a common logical error in rule-based programs.

---

## Nested conditions

A condition can contain another condition.

The examples use nested conditions to represent decisions such as:

1. Is the visitor an adult?
2. If yes, does the visitor have a ticket?

Nested conditions are valid, but excessive nesting can make code difficult to understand.

Guard clauses and logically separated functions can often reduce unnecessary nesting.

---

## Conditional expressions

Python has conditional expressions such as:

`"adult" if age >= 18 else "minor"`

JavaScript uses the ternary operator:

`age >= 18 ? "adult" : "minor"`

C++ also supports the ternary operator:

`age >= 18 ? "adult" : "minor"`

These expressions are appropriate for simple decisions that produce a value.

Large decision trees are usually easier to read as ordinary conditional statements.

---

## switch statements

JavaScript and C++ provide `switch`.

The C++ case study uses `switch` for arithmetic operation selection and for state transitions.

JavaScript uses `switch` for operation selection.

A switch statement is particularly useful when a single value must be compared against a collection of discrete cases.

A common mistake is forgetting `break` in languages where fall-through is possible.

Intentional fall-through can exist in some designs, but accidental fall-through is a frequent source of bugs.

Python does not use the traditional `switch` statement demonstrated by JavaScript and C++. Modern Python provides structural pattern matching with `match`, but the Python implementation focuses on ordinary conditionals because they are the primary concepts required for this exercise.

---

## for loops

A `for` loop is appropriate when a program needs to process items from an iterable or perform a known sequence of iterations.

Python examples process:

- lists
- strings
- ranges
- dictionaries
- generated values

JavaScript examples process:

- arrays
- strings
- generators
- custom iterables

C++ examples process:

- vectors
- ranges of integers
- collections of structures

The syntax differs, but the conceptual purpose is the same: execute a block repeatedly for a sequence of values.

---

## Python range()

Python's `range()` is particularly important.

`range(5)` produces:

`0, 1, 2, 3, 4`

The upper boundary is excluded.

`range(1, 6)` therefore produces:

`1, 2, 3, 4, 5`

This design is closely related to zero-based indexing and makes many calculations convenient.

Off-by-one errors often occur when developers misunderstand the excluded upper boundary.

---

## enumerate()

Python's `enumerate()` provides both an index and a value.

Instead of manually creating and updating an index variable, code can process:

`index, value`

at the same time.

The Python implementation uses `enumerate()` for searching and indexed output.

This is generally clearer than manually maintaining a counter.

---

## zip()

Python's `zip()` combines values from multiple iterables.

For example, names and scores can be processed together.

The ordinary form stops when the shortest iterable is exhausted.

Modern Python also supports `strict=True`, which can detect an unexpected length mismatch.

This is important when two collections are expected to contain corresponding records.

Silently truncating mismatched data can otherwise hide data-quality problems.

---

## Dictionary iteration in Python

Python dictionaries can be traversed through:

- keys
- values
- key-value pairs

The Python implementation uses `.items()` when both the key and value are needed.

This is useful for processing inventories, configuration structures, frequency tables, and other mappings.

---

## JavaScript for...of

JavaScript's `for...of` iterates over values from an iterable.

It works naturally with:

- arrays
- strings
- Sets
- Maps
- generators
- custom iterable objects

It is usually appropriate when the actual values are the important part of the loop.

---

## JavaScript for...in

JavaScript's `for...in` enumerates property keys.

The JavaScript implementation demonstrates `for...in` with an object.

When processing an object's own properties, checking ownership is important when prototype properties may be present.

`Object.entries()` is often clearer when both keys and values are needed.

---

## while loops

A `while` loop continues while a condition remains true.

It is particularly useful when the number of iterations is determined by changing state.

Examples include:

- retrying an operation
- processing until a sentinel
- running a state machine
- waiting for a state transition
- repeatedly validating input

A `while` loop must eventually change the state relevant to its stopping condition.

Failure to do so can create an infinite loop.

---

## do-while loops

JavaScript and C++ provide `do...while`.

The body executes before the condition is checked.

Therefore, the body always executes at least once.

This differs from a normal `while` loop, whose body may execute zero times.

Python does not provide a dedicated `do...while` statement. Equivalent behavior can be implemented with `while True` and an explicit `break`.

---

## break

`break` terminates the nearest enclosing loop.

The implementations use it for:

- stopping a search when a target is found
- stopping processing at a sentinel
- ending retry attempts after success
- preventing a loop from continuing unnecessarily

Early termination can improve performance because work after the required result is not performed.

---

## continue

`continue` skips the remainder of the current iteration and moves to the next iteration.

The examples use it to ignore:

- even numbers when only odd numbers are required
- invalid negative transaction values
- unwanted characters during frequency counting

`continue` is useful, but excessive use can make complex loops harder to follow.

---

## pass in Python

Python requires a syntactically valid statement inside a block.

`pass` performs no operation.

It can be used where a block is intentionally empty.

It should not be confused with `continue` or `break`.

- `pass` does nothing and continues normally.
- `continue` skips the remainder of the current iteration.
- `break` exits the loop.

---

## Loop else in Python

Python has a distinctive `for...else` and `while...else` feature.

The loop's `else` block runs when the loop completes normally without encountering `break`.

This is useful for searching.

Conceptually:

- inspect each item
- `break` when the target is found
- execute the loop `else` when no target was found

The Python implementation demonstrates this behavior directly.

This feature is uncommon in many other mainstream languages and is worth understanding when reading Python code.

---

## Nested loops

A nested loop is a loop inside another loop.

The implementations use nested loops for:

- multiplication tables
- matrix traversal
- pair searching
- two-dimensional data processing

If an outer loop executes `n` times and an inner loop executes `m` times for every outer iteration, the inner body can execute approximately `n × m` times.

If both dimensions are `n`, the complexity is generally O(n²).

Nested loops are not inherently inefficient. They become problematic when their input sizes are large or when an algorithm with better complexity is available.

---

## Searching

The implementations demonstrate linear search.

Linear search examines values one by one until:

- the target is found, or
- all values have been examined

Its worst-case time complexity is O(n).

The search may terminate earlier when the target occurs near the beginning.

This is a practical example of why `break` can reduce actual work even when the theoretical worst-case complexity remains O(n).

---

## Trading space for time

The pair-sum examples demonstrate an important algorithmic trade-off.

A straightforward nested-loop solution checks many pairs and has O(n²) time complexity.

The optimized version stores previously seen values in a set.

For each number, it calculates the value required to reach the target and checks whether that value has already been seen.

This changes the basic approach from repeated pair comparison to membership lookup.

The Python implementation uses a set with expected O(1) membership behavior.

The JavaScript implementation uses `Set`.

The C++ implementation uses `std::set`, which provides ordered-tree lookup with O(log n) lookup and insertion. Consequently, the demonstrated C++ optimization has O(n log n) time rather than the expected O(n) behavior associated with a hash table.

The choice of data structure therefore affects algorithmic complexity.

---

## Filtering and aggregation

Conditions and loops frequently work together.

A loop can:

1. inspect each record
2. classify it
3. update one or more totals

The financial transaction examples separate positive values from negative values and calculate income, expenses, and balance.

This pattern appears throughout real applications:

- accounting
- analytics
- inventory management
- monitoring
- reporting
- statistics
- billing
- telemetry processing

---

## Comprehensions in Python

Python comprehensions provide compact collection construction.

The Python implementation demonstrates:

- list comprehensions
- set comprehensions
- dictionary comprehensions

A list comprehension can combine transformation and filtering.

For example, it can construct the squares of only even numbers.

Comprehensions are concise, but they should remain readable. Extremely complicated comprehensions can be less maintainable than ordinary loops.

---

## Generator expressions

A generator expression produces values lazily.

Instead of constructing an entire collection immediately, values are generated when requested.

This can reduce memory usage for large sequences.

The Python implementation demonstrates summing a large range through a generator expression.

The JavaScript implementation demonstrates generator functions using `yield`.

Generators are especially useful for streams, large sequences, pipelines, and incremental processing.

---

## Generator functions

A generator function yields one value at a time.

The Fibonacci examples demonstrate this behavior.

A normal function may return a complete list:

`[0, 1, 1, 2, 3, ...]`

A generator can produce each value as the consumer requests it.

This changes the memory and execution model.

The generator does not need to materialize every result before iteration begins.

---

## Iterator protocols

The Python implementation defines a custom iterator using:

- `__iter__()`
- `__next__()`

The JavaScript implementation defines a custom iterable through `Symbol.iterator`.

These examples show that a language-level `for` loop is not merely syntactic repetition. It depends on an iteration protocol.

The protocol allows different data structures to define how their values are produced.

---

## Sentinel-controlled loops

A sentinel is a special value that means processing should stop.

The examples process values until `-1` appears.

The important rule is that the sentinel is a control value, not ordinary application data.

If the sentinel could also be a legitimate data value, another termination mechanism may be required.

---

## Retry loops

Retry logic is a practical use of loops.

A retry mechanism normally needs:

- a maximum number of attempts
- a success condition
- failure handling
- a stopping rule

An unbounded retry loop can create serious production problems.

It can repeatedly consume CPU, overload an external service, or prevent an application from recovering.

Production retry systems may also use:

- delays
- exponential backoff
- jitter
- retryable-error classification
- cancellation
- global time limits

The provided examples deliberately keep retry behavior deterministic and simple.

---

## State-machine loops

A state machine represents a process as a collection of states and transitions.

The Python implementation demonstrates explicit state progression.

The C++ case study uses:

- START
- VALIDATE
- CLASSIFY
- STORE
- FINISH

A loop repeatedly evaluates the current state and determines the next state.

This approach is useful when application behavior depends on the current phase of processing.

State machines appear in:

- workflow systems
- network protocols
- authentication flows
- user interfaces
- payment processing
- manufacturing systems
- embedded systems

---

## Validation

Validation should occur before operations that depend on valid input.

The examples validate:

- numeric ranges
- transaction amounts
- retry counts
- collection dimensions
- transaction frequencies
- division denominators

Validation is particularly important around loops because invalid state can cause:

- incorrect results
- infinite loops
- exceptions
- resource exhaustion
- corrupted application state

A loop should have clear assumptions about the data it processes.

---

## Exception handling

Python uses `try` and `except`.

JavaScript uses `try` and `catch`.

C++ uses `try` and `catch`.

Exceptions are appropriate for failures that should interrupt the normal local control flow.

They should not be used as a replacement for every ordinary condition.

For example, checking whether a number is negative before processing it is generally clearer than deliberately causing an exception and catching it.

---

## Edge cases

Important edge cases demonstrated by the implementations include:

- empty collections
- invalid scores
- negative values
- zero denominators
- missing search targets
- mismatched collection lengths
- invalid retry counts
- large input sizes
- duplicate values
- sentinel values
- unusually large transactions
- unknown operations
- invalid transaction records

Edge cases are important because control-flow logic often appears correct for ordinary data while failing at boundaries.

---

## Off-by-one errors

Off-by-one errors occur when a loop executes one time too many or one time too few.

Typical causes include:

- misunderstanding whether an upper boundary is inclusive
- mixing zero-based and one-based indexing
- using `<=` where `<` is intended
- starting a counter at the wrong value
- using an incorrect loop termination condition

Python's `range()` is a frequent source of confusion for beginners because its stop value is excluded.

JavaScript and C++ loops also require careful attention to boundary conditions.

---

## Infinite loops

An infinite loop is a loop that never reaches its termination condition.

A typical mistake is:

`while counter < 10`

without changing `counter`.

A safe loop needs a state transition that moves it toward termination.

Infinite loops can be intentional in servers, event processors, and long-running applications, but intentional infinite loops require explicit lifecycle controls such as:

- shutdown signals
- cancellation
- timeouts
- resource limits
- exception handling

An accidental infinite loop is a defect.

---

## Python implementation

The Python program is organized as a progressive study file.

It demonstrates:

- Boolean expressions
- comparisons
- logical operators
- conditionals
- truthiness
- membership
- identity
- conditional expressions
- guard clauses
- `for`
- `while`
- `range`
- `enumerate`
- `zip`
- dictionary iteration
- `break`
- `continue`
- `pass`
- loop `else`
- nested loops
- comprehensions
- generators
- searching
- filtering
- aggregation
- validation
- simulations
- state processing
- custom iterators
- business rules
- performance measurement

The functions are separated so that each concept can be studied independently.

The `main()` function executes the demonstrations in a logical sequence.

The Python implementation also demonstrates that loops are closely connected to other language features rather than being isolated syntax.

---

## JavaScript implementation

The JavaScript program emphasizes behavior that is particularly relevant to JavaScript development.

It demonstrates:

- strict and loose equality
- JavaScript truthiness
- `if`
- ternary expressions
- `switch`
- `for`
- `for...of`
- `for...in`
- `while`
- `do...while`
- `break`
- `continue`
- arrays
- objects
- `Map`
- `Set`
- generators
- custom iterables
- validation
- asynchronous loops
- `Promise.all`
- performance timing

The asynchronous section is especially important because JavaScript applications frequently process operations that do not complete immediately.

A `for...of` loop with `await` processes asynchronous tasks sequentially.

`Promise.all()` can run independent asynchronous operations concurrently.

These approaches have different behavior and should not be treated as interchangeable.

---

## C++ case study

### Problem being modeled

The C++ implementation models a simplified transaction-monitoring system.

Each transaction contains:

- transaction ID
- customer
- amount
- country-match status
- known-device status
- transaction count during the previous hour

The system validates each transaction and assigns a classification.

Possible classifications are:

- normal
- review
- high risk
- manual review
- invalid

The rules are intentionally deterministic so that control-flow behavior can be studied without depending on external systems.

This is an educational rule engine, not a real fraud-detection system.

---

## C++ architecture

The case study separates responsibilities into several components.

### Transaction

The `Transaction` structure represents input data.

### TransactionResult

The `TransactionResult` structure represents processed output.

### TransactionStatus

The enumeration represents the finite set of classifications.

### Validation

`isValidTransaction()` checks basic input validity.

### Classification

`classifyTransaction()` applies the decision rules.

### State processing

`processTransaction()` models a state-driven workflow.

### Batch processing

`processTransactions()` applies the processing logic to an entire collection.

### Reporting

`printReport()` produces a structured report and counts classifications.

This separation prevents all logic from being placed inside one large function.

---

## C++ state machine

The transaction workflow moves through:

`START`

then:

`VALIDATE`

then:

`CLASSIFY`

then:

`STORE`

then:

`FINISH`

A `while` loop controls state progression.

A `switch` determines what happens in each state.

This combination demonstrates how conditions and loops can form the control structure of a larger application rather than merely supporting small examples.

---

## Transaction rules

The case study uses rules such as:

- non-positive amounts are invalid
- negative transaction counts are invalid
- transactions at or above the large-amount threshold require manual review
- a transaction with both an unfamiliar country and unfamiliar device is high risk
- excessive transaction frequency is high risk
- a single unfamiliar characteristic causes review
- otherwise the transaction is normal

The exact rules are intentionally simple and deterministic.

Real financial systems require considerably more controls, data quality mechanisms, authorization, auditing, model governance, privacy protections, and operational safeguards.

---

## C++ data structures

The case study uses:

- `vector` for ordered collections of transactions
- `map` for status counts and deterministic frequency tables
- `set` for membership-based pair searching
- `optional` for a result that may not exist
- `struct` for records
- `enum class` for controlled status values

Choosing an appropriate data structure directly affects performance and clarity.

A vector provides efficient sequential access.

A set provides ordered lookup.

A map associates keys with values.

An optional explicitly represents the possibility of no result.

---

## Complexity considerations

### Linear search

Linear search examines elements sequentially.

Worst-case complexity:

O(n)

Additional space:

O(1)

### Nested pair search

A basic pair search can compare every pair.

Time complexity:

O(n²)

Additional space:

O(1)

apart from the input collection.

### Set-based pair search

The C++ implementation uses `std::set`.

Each lookup and insertion is O(log n).

Processing n values therefore produces approximately:

O(n log n)

time complexity.

Additional space:

O(n)

The Python and JavaScript versions use hash-based set structures for the analogous optimized search, which typically provide expected O(1) membership operations.

This illustrates that the same high-level algorithm can have different complexity characteristics depending on the underlying data structure.

### Matrix traversal

A matrix with `r` rows and `c` columns requires:

O(r × c)

time to inspect every element.

For a square n × n matrix this becomes:

O(n²)

---

## Performance considerations

Loop performance depends on more than the number of loop statements.

Important factors include:

- algorithmic complexity
- number of iterations
- data structure selection
- memory access patterns
- allocation behavior
- function-call overhead
- language runtime
- compiler optimization
- I/O operations
- asynchronous scheduling

Replacing an O(n²) algorithm with an O(n) or O(n log n) algorithm can have a much larger effect than micro-optimizing the syntax of the loop.

The Python and JavaScript programs include simple timing demonstrations.

Those measurements are machine-dependent and should not be treated as universal benchmarks.

The C++ implementation includes operation-count analysis to make complexity visible without depending on machine-specific timing.

---

## Conditions and data structures

Conditions often determine how a data structure is processed.

Examples include:

- if a key exists, update it
- if an item is valid, include it
- if a target is found, stop searching
- if a threshold is exceeded, classify the record differently
- if a state changes, transition to another processing stage

This interaction between data and control flow is central to practical programming.

---

## Conditions and algorithms

Many algorithms are essentially carefully organized combinations of conditions and loops.

Examples include:

- linear search
- binary search
- sorting
- graph traversal
- matrix traversal
- dynamic programming
- parsing
- simulation
- frequency counting
- validation
- scheduling

The condition determines what should happen to each value.

The loop determines how the algorithm moves through the input.

---

## Conditions and validation

A reliable program should define valid input states explicitly.

For numeric data, this can involve:

- minimum values
- maximum values
- finite values
- integer requirements
- non-zero requirements

For collections, validation can involve:

- empty input
- expected size
- matching lengths
- duplicate handling
- valid element types

For workflows, validation can involve:

- legal state transitions
- valid operation names
- permitted status values
- retry limits

Conditions provide the mechanism for expressing these rules.

---

## Common mistakes

### Using assignment instead of comparison

A comparison asks whether values meet a relationship.

An assignment changes a variable.

The exact syntax differs between languages, so the mistake appears differently in each language.

### Incorrect condition order

Broad conditions placed before specific conditions can prevent later branches from executing.

### Forgetting to update a while-loop state

This can produce an infinite loop.

### Incorrect range boundaries

An excluded upper boundary is easy to overlook.

### Incorrect indexing

Zero-based indexing must be distinguished from human-oriented one-based numbering.

### Overusing nested conditions

Deep nesting can make logic difficult to trace.

### Overusing nested loops

Nested loops may create unacceptable O(n²), O(n³), or worse behavior for large inputs.

### Forgetting break in switch

JavaScript and C++ switch statements can fall through between cases when `break` is absent.

### Confusing equality and identity

Python `==` compares values while `is` tests object identity.

### Confusing JavaScript equality operators

`===` and `==` do not have the same conversion behavior.

### Assuming empty JavaScript arrays are falsy

They are truthy.

### Using exceptions for normal branching

Ordinary expected decisions are generally clearer when represented by conditions.

---

## Edge-case design

Good control-flow design explicitly considers boundaries.

Examples include:

- zero
- negative numbers
- maximum permitted values
- empty input
- one-item input
- duplicate input
- missing target
- invalid type
- invalid state
- division by zero
- retry exhaustion
- sentinel appearing immediately
- sentinel never appearing
- mismatched collection sizes

A program that works only for ordinary input is not robust.

---

## Security considerations

Conditions and loops can contribute to security when they control validation, access decisions, resource consumption, and input processing.

Important considerations include:

### Input validation

Never assume external input is valid.

Validate:

- type
- range
- format
- size
- allowed values

### Resource exhaustion

Unbounded loops can consume CPU and memory.

Large collections should be processed with appropriate limits when the input is externally controlled.

### Retry abuse

Unlimited retries can cause denial-of-service conditions against dependent systems.

Production systems should use bounded retries and appropriate backoff.

### Authorization

A condition such as `isAdmin` should never be treated as trustworthy merely because it came from client-controlled data.

Authorization decisions must be based on trusted server-side state.

### Financial decisions

The C++ transaction example is a deterministic educational rule engine. Production financial decision systems require strong authentication, authorization, auditing, data integrity, privacy controls, and careful governance.

### Integer and numeric boundaries

C++ numeric types have finite ranges.

Overflow can produce incorrect results if not considered.

The Fibonacci implementation therefore demonstrates a type-boundary consideration: even when the loop itself is correct, the numeric representation eventually becomes insufficient for mathematical values.

---

## Implementation considerations

### Readability

A loop should make its stopping condition understandable.

### Small functions

Separating validation, calculation, classification, and reporting reduces complexity.

### Meaningful names

Names such as `transactionCountLastHour` communicate intent better than names such as `x`.

### Explicit failure handling

Invalid states should produce predictable behavior.

### Early termination

Use `break` or return from a function when further processing cannot affect the required result.

### Appropriate data structures

Choosing a set or map can avoid unnecessary nested loops.

### Avoid unnecessary work

If an operation can stop after finding a result, do not continue processing the remaining data.

### Measure before optimizing

Performance assumptions should be validated with appropriate measurements.

---

## Conditions and loops in real applications

These constructs are used in almost every software system.

### Web applications

Conditions determine:

- authentication status
- permissions
- validation results
- page states
- feature availability

Loops process:

- database results
- API responses
- lists
- search results
- user interface data

### Data analysis

Conditions filter records.

Loops aggregate or transform values.

### Financial software

Conditions enforce:

- eligibility rules
- transaction thresholds
- validation rules
- risk classifications

Loops process:

- transactions
- portfolios
- accounts
- market records

### Networking

Loops can process:

- incoming messages
- connection states
- retry attempts
- protocol events

Conditions determine:

- packet validity
- connection state
- timeout behavior
- protocol transitions

### Systems programming

Loops and conditions control:

- memory processing
- device states
- event queues
- scheduling
- resource management

### Embedded systems

Long-running loops often monitor hardware state.

Conditions determine whether a device should:

- activate
- sleep
- retry
- report an error
- transition to another state

---

## Python, JavaScript, and C++ comparison

| Concept | Python | JavaScript | C++ |
|---|---|---|---|
| Boolean | `True`, `False` | `true`, `false` | `true`, `false` |
| Conditional | `if`, `elif`, `else` | `if`, `else if`, `else` | `if`, `else if`, `else` |
| Traditional switch | Not used here | `switch` | `switch` |
| For iteration | `for item in` | `for...of` | range-based `for` |
| Numeric loop | `range()` | traditional `for` | traditional `for` |
| While | `while` | `while` | `while` |
| Do-while | No dedicated statement | `do...while` | `do...while` |
| Continue | `continue` | `continue` | `continue` |
| Break | `break` | `break` | `break` |
| Empty statement | `pass` | empty block / statement | empty statement / block |
| Generator | `yield` | `yield` | not directly equivalent |
| Main mapping | `dict` | `Map` / object | `map` |
| Set | `set` | `Set` | `set` |
| Optional result | `None` or typing | `null` / `undefined` | `std::optional` |
| Exceptions | `try/except` | `try/catch` | `try/catch` |

The syntax differs, but the underlying control-flow ideas transfer across languages.

---

## Important distinctions

### for versus while

Use `for` when the program naturally processes an iterable or has a clearly defined iteration sequence.

Use `while` when continuation depends primarily on changing state.

### break versus continue

`break` ends the loop.

`continue` skips the current iteration.

### condition versus loop

A condition answers:

"Should this branch execute?"

A loop answers:

"Should this operation execute again?"

### equality versus identity

Equality asks whether two values are equivalent.

Identity asks whether two references point to the same object.

This distinction is particularly important in Python.

### sequential versus concurrent asynchronous processing

The JavaScript asynchronous example demonstrates that awaiting inside a loop processes tasks sequentially.

`Promise.all()` can process independent operations concurrently.

Concurrency changes system behavior and must be selected according to dependency, rate limits, resource capacity, and failure-handling requirements.

---

## Practical design pattern: guard clauses

A guard clause checks an invalid or exceptional condition early and exits the current function.

This can transform deeply nested code into a sequence of explicit checks.

The Python discount calculation and JavaScript validation functions demonstrate this pattern.

Guard clauses are especially useful when:

- invalid input should stop processing
- a required object is missing
- a security check fails
- a precondition is not satisfied

---

## Practical design pattern: early search termination

Search algorithms frequently benefit from early termination.

Once the required value has been found, continuing to inspect the remaining collection provides no benefit.

`break` is one mechanism for this behavior.

Returning from the containing function can also terminate multiple levels of nested processing.

---

## Practical design pattern: bounded retries

A retry loop should have a known upper bound.

The implementations model this through a maximum number of attempts.

Production systems often expand the pattern with:

- exponential backoff
- randomized jitter
- retryable-error classification
- cancellation
- timeouts

The control-flow principle remains the same: repeat while the operation is retryable and the retry budget has not been exhausted.

---

## Practical design pattern: state transition

A state-based loop maintains an explicit current state.

Each iteration:

1. examines the current state
2. performs the appropriate action
3. determines the next state
4. continues until a terminal state is reached

This pattern is useful when workflow complexity exceeds what a simple sequence of statements can express clearly.

---

## Practical design pattern: filter and aggregate

A common data-processing loop performs both selection and aggregation.

For each record:

1. determine whether it qualifies
2. choose the appropriate category
3. update a counter or total

This pattern appears in the transaction reports, financial calculations, and frequency counters.

---

## Production considerations

Production-quality control flow should consider:

- correctness
- boundary conditions
- input validation
- error handling
- observability
- resource limits
- performance
- maintainability
- security
- cancellation
- concurrency
- testability

A loop that is logically correct for ten records may still be inappropriate for ten million records.

An algorithm that works locally may behave differently when network latency, database latency, external failures, or concurrency are introduced.

Control flow therefore needs to be designed in the context of the complete system.

---

## Testing conditions and loops

Useful tests should include both normal and boundary cases.

For a score classifier:

- 100
- 90
- 89
- 80
- 79
- 70
- 69
- 60
- 59
- 0
- negative values
- values above 100

For a search algorithm:

- target at the beginning
- target in the middle
- target at the end
- target missing
- empty collection
- duplicate target

For retry logic:

- immediate success
- success after several failures
- complete failure
- zero attempts
- negative attempt count

For a loop-controlled workflow:

- normal transition
- invalid state
- terminal state
- repeated state
- missing termination condition

Boundary testing is particularly important for control flow because a single comparison operator can change program behavior.

---

## Relationship between correctness and complexity

A correct algorithm is not necessarily an efficient algorithm.

For example, a nested loop can correctly find a pair of numbers, but it may become slow as input grows.

Replacing repeated pair comparisons with a set can reduce the amount of work.

This leads to an important programming principle:

The choice of control flow and data structures should reflect the size and characteristics of the expected input.

---

## Source implementation structure

The Python file is primarily a comprehensive teaching program. Each section is implemented as a separate function and executed from `main()`.

The JavaScript file follows a similar educational progression while incorporating JavaScript-specific iteration and asynchronous behavior.

The C++ file uses a transaction-monitoring case study to connect control flow with:

- typed data models
- enumerations
- standard containers
- state machines
- validation
- exception handling
- reporting
- algorithmic analysis

The three implementations therefore demonstrate both language-independent principles and language-specific mechanisms.
