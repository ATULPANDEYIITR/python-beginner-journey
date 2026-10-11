# Introduction to Functions

## Purpose and scope

A function is a named unit of behavior that accepts inputs, performs an operation, and may return a result. Functions allow software to express a task once and reuse it across different inputs. They also establish boundaries for validation, error handling, testing, and changes to implementation details.

The five implementations approach functions from different technical perspectives:

- Python develops from basic calls and parameter handling to recursion, higher-order functions, closures, decorators, file operations, and testing.
- JavaScript emphasizes closures, callback functions, configuration objects, asynchronous execution, and event-driven domain behavior.
- C++ models repository governance through explicit data structures, policy evaluation, and controlled state transitions.
- Java uses immutable records, domain classes, collections, and a merge-eligibility service to represent enterprise review policies.
- PostgreSQL demonstrates database functions, triggers, constraints, and relational queries that evaluate repository governance rules.

The repository-governance examples illustrate a useful distinction: an ordinary function calculates a result, a domain operation changes application state, and a database function evaluates persisted records. Each has a different responsibility and different correctness requirements.

## Function anatomy

A function interface defines how callers interact with an operation. Its parameters establish the accepted inputs, while its return value defines the result available to the caller.

Consider a pricing operation with a unit price, quantity, and optional discount. The unit price and quantity are required inputs; the discount has a default value. Validation protects the calculation from invalid values, and the return value allows another operation to use the result without depending on printed output.

A function that returns a value is different from one that only prints information. Returning a subtotal permits a caller to apply discounts, calculate taxes, store the result, or test the calculation. Printing a subtotal only displays it. Well-designed business logic generally returns structured results and leaves presentation to its caller.

### Parameters and arguments

A parameter is a name declared in a function definition. An argument is the value supplied when the function is called.

Python distinguishes positional arguments, keyword arguments, default parameters, variable positional arguments through `*args`, and variable keyword arguments through `**kwargs`. Keyword-only parameters make important options explicit. JavaScript commonly accepts an options object and uses destructuring to extract named settings. C++ and Java can express parameter contracts through typed method signatures and domain-specific objects.

Defaults should represent safe, well-defined behavior. A default discount of zero is meaningful because omitting the discount does not unexpectedly reduce the price. Invalid values should be rejected rather than silently interpreted as legitimate inputs.

### Return values and side effects

A function can return a single value, a collection, or a structured object. Python supports tuples and dictionaries, JavaScript can return objects, and C++ and Java can return structures or records. These representations are useful when an operation calculates several related outputs.

Pure functions produce results from their inputs without changing external state. Price calculations and shipping estimates can often be pure. File-writing operations, repository state transitions, and database updates have side effects.

Keeping calculations separate from side effects improves testability. An invoice calculation can be tested without creating a file, while a separate serialization function handles persistence. The same separation allows a merge-eligibility calculation to be tested independently from the operation that marks a request as merged.

## Python implementation

The Python script uses functions as the primary unit of reusable behavior.

### Basic calls and validation

`greet` returns a formatted greeting, while `calculate_rectangle_area` validates dimensions before performing multiplication. `calculate_price` combines required parameters, a default discount, numeric validation, and explicit rounding. `calculate_total` uses `*args` to accept a variable number of amounts, and `build_profile` uses `**kwargs` to collect additional profile attributes.

The examples distinguish `TypeError`, which indicates an inappropriate input type, from `ValueError`, which indicates an invalid value of an otherwise acceptable type. The functions also reject non-finite numbers where those values would invalidate financial calculations.

`summarize_scores` converts an iterable into a list because it needs to inspect the values multiple times. It rejects an empty collection instead of attempting to calculate an undefined average.

### Recursion, iteration, and memoization

`factorial_recursive` demonstrates a recursive definition. It reaches a base case at zero or one and otherwise multiplies the current value by the factorial of the preceding integer.

`factorial_iterative` calculates the same result using a loop. Iteration avoids Python's recursion-depth limitations and is more appropriate for large factorial inputs.

`fibonacci` uses `lru_cache` to retain results for previously evaluated inputs. Without caching, the straightforward recursive definition repeatedly evaluates the same subproblems. Memoization reduces repeated work, although the recursive implementation still has recursion-depth constraints and consumes memory for cached results.

The examples also distinguish algorithmic behavior from input validity. A mathematically correct recurrence still needs defined behavior for negative values, non-integer inputs, and excessive inputs.

### Higher-order functions and closures

`transform_all` accepts a callable and applies it to every input value. This separates the iteration mechanism from the operation being performed. A caller can supply a lambda, a named function, or another callable.

`make_multiplier` returns an inner function that retains access to the factor supplied when the multiplier was created. That retained reference is a closure. It allows the returned function to carry configuration without requiring a global variable.

`compose` combines two functions into a new function. The result of the first operation becomes the input of the second. Composition is useful when data processing can be represented as small transformations with clear interfaces.

### Decorators and timing

The `measured` decorator wraps a function to report execution time. `functools.wraps` preserves the wrapped function's metadata, including its name and documentation. The wrapper uses `try` and `finally`, so timing output is produced even when the wrapped operation raises an exception.

Timing results are observations rather than guarantees. Execution time depends on hardware, interpreter behavior, input size, and other running processes. Benchmarking decisions should use representative workloads rather than a single measurement.

### Invoice processing and serialization

The `OrderLine` dataclass represents an order line with a product name, unit price, and quantity. `validate_order_line` establishes the domain constraints before `line_subtotal` calculates the line amount.

`create_invoice` composes line calculations, subtotal aggregation, discount calculation, tax calculation, and total calculation. Keyword-only discount and tax parameters make policy choices explicit. The returned dictionary contains the component amounts so the final total can be inspected and independently tested.

`save_invoice` and `load_invoice` separate persistence from calculation. The file functions use UTF-8 JSON serialization and validate the loaded document's essential structure and total. A production billing system would also require durable storage, currency-aware decimal arithmetic, schema versioning, authorization, and controls against concurrent updates. Python's binary floating-point values are adequate for this educational example but are not the preferred representation for exact financial accounting.

### Testing

`FunctionTests` uses the standard `unittest` framework. The tests check normal calculations, defaults, validation errors, recursion-related behavior, function transformation, and invoice totals. Assertions establish expected outcomes rather than merely checking that a function executes without crashing.

Testing exceptional behavior is important because invalid inputs are part of a function's interface. A caller should be able to rely on documented exception behavior instead of discovering it unpredictably in production.

## JavaScript implementation

The JavaScript file emphasizes closures, callbacks, promises, and explicit domain-state changes.

### Options objects and function factories

`calculateSubscription` accepts a configuration object with a default discount. This pattern is useful when an operation has several optional settings because each argument is identified by name.

`createLogger` returns a function that retains its prefix. `createDiscountPolicy` returns a configured discount function after validating the rate. Both examples use closures to encapsulate configuration.

`createSequence` keeps its counter inside a closure and exposes only `next` and `current`. The returned interface prevents callers from directly replacing the internal counter. `Object.freeze` protects the exposed interface from ordinary property reassignment, although it does not make arbitrary closure state immutable.

### Callbacks and wrappers

`mapWithValidation` accepts a transformation callback. The callback defines what should happen to each item, while the higher-order function controls iteration.

`withTiming` wraps another function and reports the elapsed duration in a `finally` block. It preserves the wrapped function's return value and reports timing even if the wrapped operation throws. In a production implementation, timing metadata would normally be sent to a structured logging or telemetry system instead of printed directly.

### Asynchronous execution

`simulateStatusCheck` returns a promise representing a status check that completes later. `runChecksConcurrently` starts multiple checks and uses `Promise.allSettled` to preserve both successful and failed results.

`Promise.all` is appropriate when any failure should reject the combined operation. `Promise.allSettled` is useful for diagnostic workflows that need to know which individual operations succeeded. The example records failed checks as failures rather than treating an exception as successful completion.

### Pull Request lifecycle model

The `PullRequest` class represents a request with a source branch, target branch, commits, reviews, status checks, and lifecycle events. The transition map defines permitted state changes. For example, a draft can become ready, and a merged request cannot be reopened through an ordinary transition.

The `submitReview` method validates reviewer identity, review decision, lifecycle state, and commit reference. The `mergeEligibility` method evaluates current approvals and required checks. The `merge` method performs the transition only when the evaluation permits it.

The example deliberately associates approvals with a commit SHA. When a later commit changes the request's head, previous approvals no longer count in this simplified policy. A real repository platform can have additional rules governing stale reviews, dismissal, code-owner approval, and administrator bypass.

The model is educational rather than a complete GitHub API implementation. Its transition map and in-memory collections illustrate application-level policy checks; they do not replace server-side permissions or repository protection settings.

## C++ case study

The C++ program models a payment-platform repository whose protected `main` branch requires eligible approvals, successful automated checks, synchronization with the base branch, and resolved discussions.

### Domain representation

`RequestState`, `ReviewDecision`, and `CheckState` are enumerations. They restrict the represented states to explicitly defined values rather than arbitrary strings.

`Commit`, `Review`, `GovernancePolicy`, `PullRequest`, and `Eligibility` represent different parts of the workflow. The request stores its commits and review history, while the policy stores required checks and eligible reviewers. The eligibility result contains both a Boolean decision and human-readable blockers.

The use of `std::vector` preserves commit and review history. `std::map` represents named status checks, and `std::set` represents policy requirements and reviewer eligibility. These structures make the policy evaluation straightforward and avoid repeatedly searching unordered collections for every required check.

### Governance service

`RepositoryGovernance` owns the evaluation rules. `openRequest` validates branch identifiers and requires at least one commit. `submitReview` rejects author self-approval and ineligible reviewers. `updateCheck` records the latest state for a named check.

`evaluate` gathers all reasons that prevent merging rather than stopping after the first failure. It checks lifecycle state, commit availability, branch synchronization, merge conflicts, linear-history requirements, unresolved conversations, approvals, blocking review decisions, and required status checks.

The evaluator considers the latest active review per reviewer and counts only approvals that refer to the current head commit. A new commit therefore makes earlier approvals stale for this model. Dismissal retains the review record while excluding it from active decisions, supporting an auditable history.

### State transitions and failure handling

The `merge` operation evaluates the complete policy before changing the request state. A rejected merge raises an exception and leaves the request unmerged. The demonstration first exposes an incomplete check and unresolved conversation, then updates those conditions and performs the merge.

A second request illustrates stale approvals after a new commit is added. A third scenario demonstrates rejection when an empty request is opened.

The policy fields for direct pushes, force pushes, and branch deletion represent governance settings, but the in-memory evaluator does not itself implement Git server authorization. Enforcing those restrictions requires integration with the repository hosting platform or a server-side authorization layer.

For a request containing \(C\) commits, \(R\) reviews, and \(S\) required checks, the current implementation scans the review history and required checks, giving a practical evaluation cost of approximately \(O(R + S)\), excluding ordered-map operations. Repository-scale systems may need indexed review state, cached check results, and careful synchronization to handle concurrent updates.

## Java enterprise model

The Java program uses explicit domain types and a service boundary to separate repository state from merge-policy evaluation.

### Records and immutable policy

The `Commit`, `Review`, `ReviewPolicy`, and `MergeEvaluation` records model values with validation at construction time. A commit cannot be constructed with an invalid identifier or an empty message. The policy copies its reviewer and check sets using `Set.copyOf`, preventing callers from mutating those collections through their original references.

The `PullRequest` class owns mutable lifecycle state and collections. Its methods define permitted operations, while `MergeEligibilityService` evaluates whether the request satisfies the policy.

### Review decisions and freshness

A review stores the commit identifier it evaluated. The service selects the latest non-dismissed review per reviewer and compares the review's commit reference with the current head. It counts eligible approvals and detects a current request for changes.

Dismissal marks a review as dismissed rather than erasing its history. This supports auditability and makes the difference between a recorded review and an active review explicit.

The service also checks branch synchronization, merge conflicts, linear history, unresolved conversations, and required status checks. Missing or unsuccessful checks produce specific blockers. The merge operation refuses to transition a request unless the complete evaluation succeeds.

### Lifecycle enforcement

The `open`, `transitionToDraft`, and `close` methods validate state transitions. A request cannot be opened without commits or changed after it has been merged. Review submission is restricted to open requests and eligible reviewers.

This model uses Java's type system and encapsulation to reduce invalid states. It does not eliminate every concurrency problem: an actual multi-user service would need transactional persistence and a way to prevent the request's head or review state from changing between eligibility evaluation and merge execution.

The sample demonstrates enterprise domain modeling, not a direct integration with a repository hosting provider.

## PostgreSQL relational model

The SQL script persists repository governance data in related tables and uses database-level validation to protect data integrity.

### Entities and relationships

| Table | Responsibility |
|---|---|
| `repositories` | Identifies repositories and their default branches. |
| `repository_members` | Stores membership, role, and active status. |
| `branches` | Associates branch names and protection status with repositories. |
| `pull_requests` | Stores source and target branches, author, lifecycle state, and synchronization conditions. |
| `commits` | Records the changeset history associated with each request. |
| `reviews` | Stores reviewer decisions, the reviewed commit, and dismissal information. |
| `review_comments` | Records file-specific comments, optional line references, and resolution state. |
| `status_checks` | Records check results against particular commit identifiers. |
| `branch_protection_policies` | Defines required approvals and branch-level merge restrictions. |
| `required_status_checks` | Identifies the automated checks required by each policy. |

Foreign keys enforce relationships between requests, branches, commits, reviews, comments, and status checks. Unique constraints prevent duplicate branch names within a repository and duplicate check results for the same request, check name, and head commit.

Check constraints enforce valid lifecycle states, review decisions, check statuses, non-negative discussion counts, and valid commit-identifier formats. These constraints prevent many invalid records even when an application submits malformed input.

### Triggers and database functions

`validate_pull_request_membership` ensures that source and target branches belong to the request's repository and that the author is an active member.

`validate_review_submission` ensures that a review targets an open request, that the reviewer is active and eligible, that the author is not reviewing their own request, and that the reviewed commit belongs to the request.

`evaluate_merge_eligibility` is a SQL table-valued function. Its common table expressions isolate request context, policy settings, current reviewer decisions, approval counts, required-check failures, and blockers. It evaluates approvals against the latest commit rather than accepting an old approval as current.

The function returns the reasons a merge is blocked. If no blockers exist, it returns an eligible result with a null blocker. This allows callers to inspect the complete decision rather than interpreting a single Boolean without context.

### Indexes and query behavior

The indexes support repository-state filtering, chronological commit retrieval, reviewer history, unresolved comment lookups, and status-check evaluation. The unresolved-comment index is partial because only unresolved discussions need that access path for many workflows.

The `merge_eligibility` view exposes the result of the evaluation function for requests in the database. The demonstration query first reveals a pending security check, then updates that check and reevaluates eligibility.

### Transactions and limitations

The script uses a transaction to group schema creation, sample data insertion, policy evaluation, and the successful merge transition. The final update to a merged state occurs only after eligibility has been evaluated.

A production merge operation must address concurrency. A request's head, reviews, or check results could change between evaluation and state transition. A robust implementation would evaluate and update within a carefully designed transaction, use suitable row locks or optimistic concurrency controls, and integrate with the actual repository hosting system.

The example's branch-protection schema records direct-push, force-push, deletion, administrator, and bypass policies. The eligibility function focuses on merge conditions and does not implement repository-server authorization. Those settings must be enforced by the hosting platform or an integrated authorization service.

## Distinctions among the implementations

Functions serve different roles according to the environment in which they execute.

| Function role | Example | Responsibility |
|---|---|---|
| Calculation | Python `calculate_price` | Validates inputs and returns a computed value. |
| Transformation | Python `transform_all` | Applies caller-supplied behavior to a collection. |
| Closure | JavaScript `createDiscountPolicy` | Retains configuration inside a returned function. |
| Asynchronous operation | JavaScript `simulateStatusCheck` | Represents work that completes later and may fail. |
| Domain operation | C++ `RepositoryGovernance.merge` | Validates a policy before changing application state. |
| Service method | Java `MergeEligibilityService.evaluate` | Applies enterprise rules to explicit domain objects. |
| Database function | PostgreSQL `evaluate_merge_eligibility` | Evaluates persisted records through relational queries. |
| Trigger function | PostgreSQL validation functions | Rejects invalid writes before they are stored. |

These roles should not be treated as interchangeable. A pure calculation does not need database access. A domain operation must preserve state invariants. A database trigger protects persisted integrity but cannot replace all application authorization. A merge-policy evaluator provides a decision, while the merge operation performs the state transition.

## Function design and common failure modes

### Ambiguous contracts

A function with unclear input requirements forces callers to guess what constitutes valid input. Explicit parameter types, validation, meaningful exceptions, and structured return values reduce this ambiguity.

### Excessive responsibilities

A single function that validates an order, calculates taxes, writes a file, sends notifications, and changes repository state becomes difficult to test. Separating calculations, persistence, and state transitions gives each operation a clearer contract.

### Hidden state and side effects

Global mutable variables and closures with poorly defined state can make behavior depend on previous calls. Closures are useful when retained state is intentional, as in a sequence generator, but the interface should control how that state changes.

### Recursion without suitable limits

Recursive functions need a correct base case and progress toward it. Missing base cases can cause unbounded recursion. Even a correct recursive algorithm can exceed the language's call-stack limit, which is why the iterative factorial implementation is included alongside the recursive version.

### Incorrect caching

Memoization is useful when repeated inputs produce reusable results. It is unsuitable when results depend on changing external state unless the cache accounts for that state. Cached results also consume memory, so an unbounded cache is not automatically appropriate for long-running services.

### Incomplete asynchronous error handling

Starting asynchronous operations does not guarantee their success. Promise rejection, timeouts, and partial failure must be handled explicitly. `Promise.allSettled` is useful when every outcome is needed for diagnostics, while a strict all-or-nothing operation may prefer `Promise.all`.

### Stale review decisions

A review decision applies to a particular changeset. When new commits are added, earlier approval may no longer represent the code being merged. Repository governance must define how stale reviews are handled and must evaluate approvals against the correct head revision.

### Validation at only one layer

Application validation improves error messages, but concurrent callers and direct database writes can bypass application-level checks. Database constraints and triggers protect persisted invariants, while repository hosting permissions enforce branch operations that the database cannot independently control.

## Performance and production considerations

Function calls have overhead, but architectural clarity and correctness usually matter more than eliminating small call costs. Performance work should focus on measured bottlenecks such as repeated scans, expensive recursion, redundant database queries, and unnecessary serialization.

Pure functions are easy to test and often straightforward to cache. Stateful functions need explicit transition rules. Asynchronous functions require clear completion and failure behavior. Database functions need appropriate indexes and query plans. Enterprise service methods need transactional guarantees when evaluation and mutation must be atomic.

For repository governance, the critical production requirement is that the merge decision and the actual merge cannot diverge. The system must validate the current request head, eligible reviews, required checks, conflict status, branch policy, and authorization at the point of merging. A previously successful evaluation is not a permanent permission to merge if the underlying state has changed.
