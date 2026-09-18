# While loops

## Topic introduction

A `while` loop repeatedly executes a block of statements as long as a Boolean condition remains true. It is a condition-controlled loop, which makes it particularly useful when the number of iterations is not known in advance.

The central structure is:

`while condition:`

followed by an indented block in Python.

In JavaScript and C++, the equivalent structure is:

`while (condition) { ... }`

The essential sequence is:

1. Evaluate the condition.
2. If the condition is true, execute the loop body.
3. Update the state that controls the loop.
4. Evaluate the condition again.
5. Stop when the condition becomes false.

A `while` loop is therefore fundamentally a mechanism for repeatedly applying an operation while some state satisfies a condition.

The three implementations in this study use increasingly practical examples. Python focuses on language fundamentals and algorithms, JavaScript extends the concept into asynchronous and event-driven application patterns, and C++ develops an industry-style transaction-processing case study.

## Fundamental terminology

### Condition

The condition is an expression evaluated as a Boolean value.

For example, `counter < 10` asks whether `counter` is still below ten.

### Iteration

One execution of the loop body is an iteration.

If a loop body executes ten times, the loop has performed ten iterations.

### Loop body

The loop body is the block of statements controlled by the loop.

### Loop state

Loop state is the data whose value determines what the loop does or whether it continues.

A counter, queue, index, parser position, state-machine state, or timestamp can all act as loop state.

### Initialization

Initialization establishes the state before the first condition check.

For example:

`counter = 0`

### Update

The update changes the state after an iteration.

For example:

`counter += 1`

Without an appropriate update, a loop may never terminate.

### Termination condition

The termination condition describes the state under which the loop stops.

For a loop using `while counter < 10`, termination occurs when `counter < 10` becomes false.

### Sentinel

A sentinel is a special value that signals termination.

For example, a data-processing loop can continue until it encounters `-1`.

### Infinite loop

An infinite loop is a loop that does not terminate because its condition never becomes false or because control flow prevents the required state change.

Infinite loops are sometimes intentional in servers, event processors, and operating-system components, but production systems normally require a shutdown or cancellation mechanism.

## The basic execution model

Consider a counter starting at zero:

`counter = 0`

`while counter < 5:`

`    print(counter)`

`    counter += 1`

The initial condition is true because zero is less than five.

The body executes and changes the counter to one.

The condition is checked again.

This continues until the counter reaches five. At that point `counter < 5` is false and the loop terminates.

The Python implementation demonstrates this directly in `example_basic_while()`.

## Why state changes matter

A useful way to reason about every `while` loop is to identify:

- the initial state
- the continuation condition
- the state transition
- the termination state

A loop should normally have a visible relationship between its state transition and termination condition.

For example:

`remaining = 5`

`while remaining > 0:`

`    remaining -= 1`

The state moves from five toward zero.

A common mistake is:

`counter = 0`

`while counter < 5:`

`    print(counter)`

This does not change `counter`, so the condition remains true indefinitely.

The Python function `safe_progress_example()` demonstrates the safer pattern.

## Counter-controlled loops

A counter-controlled loop is appropriate when iteration depends on a known numeric boundary.

The Python implementation demonstrates:

- increasing counters
- decreasing counters
- custom increments
- explicit boundaries

JavaScript provides the same mechanisms through mutable `let` variables.

C++ commonly uses `size_t` or another integer type when traversing containers.

A counter loop has a predictable structure:

`initialize -> test -> execute -> update -> test`

## Condition-controlled loops

A condition-controlled loop is preferable when the termination event is more important than the number of iterations.

Examples include:

- process requests while work exists
- read records until a sentinel appears
- retry an operation until it succeeds or attempts are exhausted
- consume a queue until it becomes empty
- process pages until an API returns no records
- advance a state machine until a terminal state is reached

The C++ transaction processor demonstrates several of these patterns.

## Sentinel-controlled loops

A sentinel is a value with special meaning.

The Python function `sum_until_sentinel()` processes numbers until it encounters `-1`.

The value after the sentinel is deliberately ignored.

Sentinels are useful for streams and simple protocols, but they have a limitation: the sentinel must be distinguishable from valid data.

If `-1` is a legitimate business value, a separate termination mechanism is safer.

Modern APIs may instead use:

- explicit end-of-stream signals
- optional values
- exceptions such as iterator exhaustion
- status objects
- cancellation tokens
- message metadata

## Boolean flags

A Boolean flag can represent whether an event has occurred.

The Python example searches for an odd number while maintaining `found_odd`.

The general form is:

`while condition and not found:`

This can be useful when several conditions jointly determine termination.

Flags should be given meaningful names. `found_odd` communicates much more than a vague variable such as `flag`.

## `break`

`break` immediately terminates the nearest enclosing loop.

It is particularly useful when the desired result has already been found.

The search functions in all three implementations use early termination.

For example, an iterative search does not need to examine the remaining elements after finding its target.

A `break` statement should have a clear reason. Excessive use of multiple breaks can make control flow difficult to trace.

## `continue`

`continue` skips the remaining statements in the current iteration and begins the next iteration.

The Python and JavaScript examples use it to ignore unwanted values.

For example:

`if number % 2 == 0:`

`    continue`

This makes the main body operate only on odd numbers.

One important issue is that the state update must not accidentally be skipped.

For example, putting a counter increment after a `continue` can create an infinite loop if the `continue` is reached on every iteration.

## `while...else` in Python

Python has a special `while...else` construct.

The `else` block executes when the loop terminates normally because its condition becomes false.

It does not execute when the loop exits through `break`.

This makes `while...else` useful for search operations.

The Python function `search_with_break_else()` demonstrates the distinction.

JavaScript and C++ do not have a directly equivalent `while...else` construct.

## `do...while` in JavaScript

JavaScript provides both `while` and `do...while`.

A `while` loop checks its condition before entering the body.

A `do...while` loop executes the body first and checks the condition afterward.

Therefore, a `do...while` loop always executes at least once.

The JavaScript implementation demonstrates this difference.

This is useful for menu systems and workflows where an initial operation must occur before deciding whether another iteration is required.

## Nested while loops

A loop can contain another loop.

The outer loop may control rows while the inner loop controls columns.

The multiplication-table examples demonstrate this structure.

If the outer loop executes `n` times and the inner loop executes `n` times for every outer iteration, the total work is generally O(n²).

Nested loops are not automatically inefficient. Their cost depends on the amount of work performed and the input size.

## String processing

Strings can be processed character by character with an index.

The Python and JavaScript implementations use this technique to:

- reverse strings
- count characters

The basic model is:

`index = 0`

`while index < length:`

`    process character`

`    index += 1`

This approach is educational and gives explicit control over iteration.

Higher-level string operations can be clearer and faster for many production tasks, so an explicit `while` loop should be used when its control model provides value.

## Array and container processing

The Python, JavaScript, and C++ implementations all process collections using explicit loop state.

Typical state variables include:

- an index
- a queue position
- a batch boundary
- a pointer into a sorted range
- an iterator
- a timestamp window

A common performance consideration is how elements are removed.

In the JavaScript implementation, repeatedly calling `shift()` on a large array can require repeated element movement. An index-based approach avoids that pattern.

In C++, `std::queue` provides efficient front removal for queue-style processing.

## Iterators

A loop does not have to operate on an array index.

Python exposes iterators through `iter()` and `next()`. The iterator signals completion through `StopIteration`.

JavaScript exposes the iterator protocol through `Symbol.iterator` and iterator result objects containing `value` and `done`.

These examples demonstrate that looping is fundamentally about repeated state transitions. The state does not have to be an integer index.

## Algorithms implemented with while loops

### Factorial

The factorial of a non-negative integer is:

`n! = 1 × 2 × 3 × ... × n`

The iterative implementation begins with one and repeatedly multiplies by the next integer.

For `n`, this requires O(n) iterations.

The edge case `0! = 1` is explicitly supported.

### Greatest common divisor

The Euclidean algorithm repeatedly replaces two values with the second value and the remainder.

The core transition is:

`(a, b) -> (b, a mod b)`

The process ends when `b` becomes zero.

The algorithm has logarithmic behavior with respect to the smaller input for ordinary integer inputs.

All three implementations use this algorithm.

### Binary search

Binary search requires sorted data.

At every iteration, it examines the middle element and eliminates half of the remaining search space.

The search interval is represented by:

- `low`
- `high`

The algorithm runs in O(log n) time and O(1) additional space in the iterative implementation.

The most important precondition is that the input must be sorted according to the same ordering used by the search.

### Prime testing

The implementations test possible divisors only up to the square root of the candidate.

If a composite number has a factor greater than its square root, it must also have a corresponding factor smaller than the square root.

The loop therefore stops at the mathematical boundary required by the algorithm.

### Fibonacci sequence

The iterative Fibonacci implementation maintains two pieces of state.

Instead of repeatedly recalculating earlier terms recursively, it updates the pair after each iteration.

This provides O(n) time for generating `n` terms and O(n) space for storing the resulting sequence.

The underlying rolling state itself requires only O(1) working memory.

## Floating-point termination

Floating-point arithmetic requires special care.

A condition such as:

`while value != 1.0`

can be unsafe when `value` is repeatedly modified by decimal floating-point operations.

Many decimal fractions cannot be represented exactly in binary floating-point.

A safer pattern is often:

`while abs(value - target) > tolerance:`

Another option is a maximum iteration count.

The Python, JavaScript, and C++ materials emphasize bounded or tolerance-based termination for numerical algorithms.

## Input validation

A loop that processes external input should not assume that every value is valid.

The Python and JavaScript examples validate positive integers before accepting them.

Production applications should consider:

- malformed input
- missing input
- unexpected ranges
- encoding issues
- resource limits
- excessively large values
- repeated invalid attempts

Validation should occur before unsafe or expensive processing.

## Retry loops

Retry loops are common in distributed applications because network and service operations can fail temporarily.

An unsafe retry loop can continue forever.

The implementations therefore use a maximum number of attempts.

A production retry policy may also include:

- exponential backoff
- jitter
- timeout limits
- cancellation
- idempotency controls
- error classification
- circuit breakers

Not every failure should be retried. Authentication failures, malformed requests, and deterministic validation errors generally require different handling from transient network failures.

The code examples keep the retry mechanism deterministic so its loop behavior can be studied without external services.

## Asynchronous while loops in JavaScript

JavaScript can combine `while` loops with `async` and `await`.

The JavaScript implementation demonstrates:

- asynchronous retries
- simulated paginated retrieval
- chunked processing

An asynchronous loop can wait for a Promise between iterations.

This is especially relevant to:

- API clients
- browser applications
- server-side JavaScript
- queue workers
- database operations

An important distinction is that `await` does not make a CPU-heavy synchronous loop automatically non-blocking.

A loop that performs millions of synchronous calculations can still monopolize the JavaScript event loop.

The chunked-processing example explicitly yields between batches.

## Pagination

APIs frequently return data in pages.

A typical pagination loop is conceptually:

`page = 1`

`while more data exists:`

`    request page`

`    process records`

`    page += 1`

The JavaScript example models this without making a network request.

Real implementations should account for:

- empty pages
- repeated pages
- maximum page limits
- server errors
- rate limits
- authentication expiry
- cancellation
- duplicate records

A production loop should not blindly continue forever because a server unexpectedly keeps returning data.

## State machines

A state machine represents a system as a set of states and valid transitions.

The Python traffic-light example and C++ transaction workflow demonstrate this concept.

The C++ case study uses:

`Pending -> Validated -> Approved -> Completed`

or a transition to:

`Rejected`

A state-machine loop is useful when the termination condition is a terminal state rather than a numeric boundary.

State machines appear in:

- payment processing
- order management
- authentication workflows
- network protocols
- manufacturing systems
- device controllers
- deployment pipelines

Explicit state transitions are easier to validate than arbitrary changes to unrelated Boolean flags.

## C++ case study: transaction processing service

The C++ program models a simplified transaction-processing service.

The system accepts transaction records containing:

- transaction ID
- customer identifier
- amount
- status

The case study then develops the processing pipeline in stages.

### Validation layer

`isValidTransaction()` rejects records with:

- non-positive IDs
- empty customer identifiers
- negative amounts
- non-finite numeric amounts

The validation loop demonstrates how every input record can be examined without assuming that all records are trustworthy.

### Transaction processor

`TransactionProcessor` separates accepted and rejected transactions.

Its internal loops demonstrate explicit traversal and controlled state progression.

The class also provides a total-value calculation for accepted records.

### Batch processing

`BatchService` divides the input into batches.

The outer `while` controls the current batch.

The inner `while` controls records inside that batch.

This provides a useful example of nested condition-controlled loops in a realistic system.

The final batch may contain fewer records than the configured batch size. The implementation handles this through `min()` when calculating the batch boundary.

### Retry behavior

Transaction ID 3 deliberately fails its first two simulated attempts and succeeds on the third.

The `RetryPolicy` uses a bounded `while` loop.

This illustrates why a retry loop should have an explicit upper bound.

Without such a bound, a persistent failure could consume resources indefinitely.

### Queue processing

`BatchQueue` uses `std::queue<Transaction>`.

The processing loop continues while the queue is not empty.

This maps directly to the operational rule:

`while work remains, process work`

The queue is preferable to repeatedly removing the first element of a vector because its interface is designed for queue semantics.

### Transaction state machine

`TransactionWorkflow` models a transaction's lifecycle.

A valid and approved transaction progresses to completion.

An invalid or unapproved transaction transitions to rejection.

The loop terminates when a terminal state is reached.

This is an example of a `while` loop whose termination condition is domain state rather than an integer counter.

### Rate limiting

`SlidingWindowLimiter` models a simple request-rate control mechanism.

A queue stores timestamps.

Old timestamps are removed while they are outside the active window.

The current request is then accepted only if the number of active timestamps is below the configured limit.

Each timestamp enters and leaves the queue once, producing amortized linear behavior across a sequence of requests.

### Analytical processing

The C++ program also performs:

- threshold filtering
- statistics
- customer aggregation
- binary search
- greatest common divisor calculation
- primality testing

These examples show that a `while` loop is not a specific algorithm. It is a control-flow mechanism that can implement many different algorithms.

## Complexity considerations

Loop syntax does not determine algorithmic complexity by itself.

The operations performed inside the loop are what determine the cost.

Examples:

| Operation | Typical complexity |
|---|---:|
| Linear traversal | O(n) |
| Factorial calculation | O(n) |
| Character counting | O(n) |
| GCD using Euclid's algorithm | O(log n) |
| Binary search | O(log n) |
| Nested n by n traversal | O(n²) |
| Prime test by trial division | O(sqrt(n)) |
| Queue processing of n elements | O(n) |
| Sliding-window timestamp processing | O(n) amortized |

An O(n) loop can still be slow if every iteration performs an expensive operation.

Likewise, a loop with many iterations can be efficient when each iteration performs constant-time work.

## Performance considerations

### Avoid unnecessary work

Move invariant calculations outside the loop when possible.

For example, if a value does not change between iterations, calculating it once is usually preferable to recalculating it repeatedly.

### Choose appropriate data structures

A loop over a suitable data structure can be much more efficient than the same logical loop over an unsuitable one.

The C++ case study uses `std::queue` for queue semantics.

The JavaScript examples use indexes instead of repeated front-removal operations.

### Reduce repeated allocations

Repeatedly creating temporary objects or strings inside very large loops can increase allocation and garbage-collection costs.

The correct optimization depends on the runtime and workload, so readability should not be sacrificed without evidence of a performance problem.

### Consider built-in operations

The Python implementation includes both an explicit `while`-based sum and Python's built-in `sum()`.

The explicit loop is useful for learning and custom processing. The built-in operation is normally preferable for a straightforward sum because it is implemented efficiently by the Python runtime.

### Avoid premature optimization

A clear O(n) implementation is often preferable to a complicated optimization that provides no measurable benefit.

Profiling should guide performance work in production applications.

## Infinite loops

Common causes include:

- forgetting the state update
- updating the wrong variable
- using the wrong comparison operator
- creating an unreachable termination condition
- relying on exact floating-point equality
- repeatedly receiving data without a stop condition
- swallowing errors that should terminate processing

An intentionally infinite loop can be appropriate for a long-running service, but such a loop normally needs:

- cancellation
- shutdown signals
- error handling
- resource cleanup
- health monitoring
- backoff
- logging
- bounded resource consumption

## Common mistakes

### Forgetting to update the counter

A loop such as `while counter < 10` needs a mechanism that eventually changes `counter`.

### Off-by-one errors

Compare:

`while index < length`

with:

`while index <= length`

The latter can access an invalid position when the valid indexes end at `length - 1`.

### Incorrect initialization

An initial value that already violates the intended invariant can cause the loop to execute zero times.

This is sometimes correct and sometimes a bug.

### Updating too early

Changing the index before processing the current item can accidentally skip data.

### Updating too late

Updating state after a conditionally executed `continue` can prevent progress.

### Modifying a collection unexpectedly

Changing the collection being traversed can make loop behavior difficult to reason about.

### Unbounded retries

Retrying forever can hide persistent failures and consume resources.

### Trusting input

External data should be validated before it becomes loop state or enters an algorithm.

### Floating-point equality

Exact equality should not normally control numerical convergence.

## Exceptions and error handling

Loops often encounter errors in the middle of processing.

The implementations demonstrate several strategies:

- validate before entering the main processing path
- raise exceptions for invalid function parameters
- catch expected retry failures
- use bounded retry counts
- propagate fatal errors to the program-level handler

Error handling should not accidentally create a loop that repeatedly retries an error that can never succeed.

## Security considerations

Loops can create security problems when their execution is controlled by untrusted input.

Examples include:

- an attacker providing an extremely large iteration count
- a request causing an expensive algorithm to execute repeatedly
- an unbounded retry mechanism consuming resources
- an API returning unlimited pages
- a queue growing faster than workers can process it
- malformed input causing repeated validation attempts

Security-conscious loop design should therefore consider:

- maximum input sizes
- maximum iteration counts
- request timeouts
- rate limits
- memory limits
- cancellation
- authentication attempt limits
- resource quotas

The JavaScript and Python examples include bounded retry patterns. The C++ case study includes a sliding-window limiter.

## Authentication attempt limits

The Python implementation includes a bounded authentication example.

It intentionally models the loop only and does not represent a production password-storage implementation.

Real authentication systems should use secure password hashing, protected credential storage, rate limiting, account protection mechanisms, and appropriate session controls.

The relevant loop principle is that authentication attempts should have explicit limits or other abuse-prevention controls.

## Debugging while loops

When debugging a loop, inspect four things first:

1. Initial state
2. Condition
3. State update
4. Termination state

A useful debugging table can contain:

| Iteration | State before | Condition | Action | State after |
|---|---:|---|---|---:|
| 1 | 0 | true | process | 1 |
| 2 | 1 | true | process | 2 |
| 3 | 2 | true | process | 3 |
| 4 | 3 | false | stop | 3 |

For complex loops, logging the state transition is often more informative than logging every statement.

In production, excessive loop logging can itself become a performance and storage problem, so structured and rate-limited logging is preferable.

## Python implementation

The Python implementation provides the broadest instructional coverage.

It demonstrates:

- basic `while`
- counters
- decreasing counters
- custom steps
- input validation
- sentinel loops
- Boolean flags
- `break`
- `continue`
- `while...else`
- nested loops
- string processing
- list processing
- iterators
- factorial
- Euclidean GCD
- binary search
- Newton's method
- prime testing
- Fibonacci generation
- state machines
- compound-interest simulation
- queue-style processing
- retry logic
- sliding-window processing
- command processing
- performance comparison
- assertions and tests

The code is intentionally explicit so the relationship between state and termination remains visible.

## JavaScript implementation

The JavaScript implementation focuses on application behavior.

It demonstrates:

- standard `while`
- `do...while`
- JavaScript type validation
- arrays and strings
- iterators
- classes
- state machines
- retries
- asynchronous loops
- Promises
- simulated pagination
- chunked processing
- event-loop yielding
- numeric precision considerations

The asynchronous examples show why JavaScript's execution model can make loop design different from a purely synchronous implementation.

An asynchronous loop can await an external operation while allowing the runtime to handle other work between asynchronous operations.

## C++ implementation

The C++ program develops the topic as a transaction-processing case study.

Its major components are:

- `Transaction`
- validation logic
- `TransactionProcessor`
- `RetryPolicy`
- `BatchQueue`
- `TransactionWorkflow`
- `SlidingWindowLimiter`
- `BatchService`
- statistical processing
- aggregation
- search algorithms
- test functions

The case study demonstrates how a simple language construct becomes part of larger system architecture.

C++ also introduces explicit types, standard-library containers, exception handling, object-oriented design, and performance-oriented data structures.

## Comparison of Python, JavaScript, and C++

| Aspect | Python | JavaScript | C++ |
|---|---|---|---|
| Basic syntax | `while condition:` | `while (condition)` | `while (condition)` |
| Main strength in this study | Algorithmic clarity | Application and asynchronous behavior | Systems-oriented case study |
| Dynamic typing | Yes | Yes | No |
| Explicit memory management | Automatic | Automatic | Automatic plus deterministic resource-management facilities |
| Async loop support | Available through async features | Central application pattern | Available through standard/library mechanisms |
| Iterator protocol | `iter()` and `next()` | `Symbol.iterator` | STL iterators and ranges |
| `while...else` | Yes | No | No |
| `do...while` | No direct equivalent | Yes | Yes |
| Queue example | List/index model | Array/index model | `std::queue` |
| Typical performance profile | High productivity | Strong application/runtime integration | High control and performance potential |

The important point is not that one language's `while` loop is inherently superior. The control structure is conceptually the same, while the surrounding language and runtime determine how it integrates into a larger program.

## `while` versus `for`

A `for` loop is often preferable when iteration has a clear counter or traversal structure.

A `while` loop is often preferable when the termination event depends on changing state.

Examples naturally suited to `while` include:

- process until queue exhaustion
- retry until success or attempt limit
- read until sentinel
- continue until a state becomes terminal
- process pages until an empty page
- converge until an error is below tolerance

Examples naturally suited to `for` include:

- visit every element exactly once
- repeat a known number of times
- iterate through a collection
- traverse a numeric range

The distinction is about expressing intent, not merely about technical capability.

## `while` versus `do...while`

A normal `while` loop may execute zero times.

A `do...while` loop executes at least once.

Use `while` when the condition must be checked before any work.

Use `do...while` when the first execution is required before deciding whether to continue.

## Loop invariants

A loop invariant is a property that remains true before and after each iteration.

For a binary search, an important invariant is that if the target exists, it remains within the active search interval.

For a queue processor, an invariant may be that every item before the current queue position has already been processed.

Loop invariants are valuable when proving correctness of algorithms.

## Termination reasoning

A useful formal approach is to identify a quantity that moves toward a terminating boundary.

For example:

`remaining = 10`

Each iteration performs:

`remaining -= 1`

The value decreases toward zero.

For binary search, the search interval becomes smaller.

For queue processing, the number of pending elements decreases.

For a state machine, the state moves toward a terminal state.

This is a practical way to reason about whether a loop will terminate.

## Production design considerations

A production loop should have an explicit operational purpose.

Important questions include:

- What state changes each iteration?
- What causes termination?
- Can the loop receive malformed input?
- What happens if an operation fails?
- Can the loop run for unexpectedly long periods?
- Is cancellation required?
- Is resource usage bounded?
- Is progress observable?
- What happens if external data stops changing?
- Is the selected data structure appropriate?
- What is the time and space complexity?
- Are numeric calculations stable?
- Can the loop be safely restarted?

These questions are particularly important for network services, background workers, batch processors, and data pipelines.

## Practical applications

`while` loops appear in many real systems:

- command interpreters
- interactive menus
- network clients
- API pagination
- queue consumers
- retry systems
- schedulers
- parsers
- numerical algorithms
- simulations
- rate limiters
- state machines
- monitoring processes
- streaming systems
- transaction processing
- validation workflows
- resource-management logic

The common property is that the number of iterations is often determined by changing runtime state rather than a fixed count.

## Important design distinction

A loop is not an algorithm by itself.

`while` only specifies a control-flow mechanism.

The algorithm's behavior comes from:

- the state representation
- the condition
- the transition
- the operations performed
- the data structure
- the termination rule

The same `while` syntax can implement an O(n) traversal, an O(log n) binary search, a state machine, a retry mechanism, or a potentially unbounded service loop.

## Key implementation principles

A well-designed `while` loop generally has:

- clear initialization
- a meaningful condition
- explicit state progression
- predictable termination
- appropriate error handling
- bounded resource use when required
- suitable data structures
- documented assumptions
- tests for boundary cases

The most important habit is to reason about the state transition before writing the loop body. A loop becomes much easier to implement and debug when its termination behavior is understood first.
