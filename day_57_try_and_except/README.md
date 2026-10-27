# Python `try` and `except`: Exception Handling Across Software Systems

## Scope

This project studies Python `try` and `except` as part of a broader exception-handling model. The five implementations use a common repository-development scenario so that failures can be compared across programming languages and a relational database.

The central distinction is between normal control flow and exceptional control flow:

`try` identifies operations that may fail.

`except` handles selected failures.

`else` can be used for code that should execute only when the protected operation succeeds.

`finally` is appropriate for cleanup that must occur whether the operation succeeds or fails.

`raise` creates an exception deliberately when a domain rule is violated.

Exception chaining preserves the original failure while exposing a more meaningful application-level exception.

The implementations model repository operations such as repository lookup, Pull Request validation, review processing, status-check evaluation, and merge eligibility. The repository scenario provides realistic failure conditions without making exception handling itself dependent on an external service.

## Core Python Mechanism

The Python implementation uses a hierarchy of custom exceptions:

| Exception | Meaning |
|---|---|
| `RepositoryError` | Base class for repository workflow failures |
| `ValidationError` | Input or domain validation failed |
| `RepositoryNotFoundError` | Requested repository does not exist |
| `StorageError` | Persistent storage could not be read or written |

This hierarchy allows callers to catch a specific failure when they can recover from it and a broader domain exception when they only need a common failure boundary.

For example, repository storage catches low-level filesystem and JSON failures and converts them into `StorageError`. The original exception is retained with `raise ... from exc`. This separates implementation details from the public domain interface while preserving diagnostic information.

The script also demonstrates the difference between validation before an operation and handling a failure produced by the operation itself. `divide_review_work` validates its arguments before division, while JSON parsing catches a standard-library `JSONDecodeError` and converts it into a domain-specific `ValidationError`.

## `try`, `except`, and Exception Scope

A `try` block should cover the operation whose failure is expected and recoverable.

The Python implementation avoids a broad exception handler around the entire application logic. Individual operations have narrow exception boundaries:

- filesystem access is handled by the storage layer
- JSON parsing is handled where external data enters the application
- repository lookup distinguishes missing records from storage failures
- Pull Request evaluation converts validation failures into an explicit result
- the application entry point remains responsible for running the complete workflow

This structure prevents unrelated programming errors from being silently interpreted as ordinary business failures.

Catching `Exception` indiscriminately would make it difficult to distinguish a bad request from a programming defect. The implementation therefore prefers explicit exception types.

## Exception Hierarchy

The hierarchy supports increasingly broad handling:

`ValidationError`
→ `RepositoryError`
→ `Exception`

A caller that expects invalid user input can catch `ValidationError`.

A service boundary that treats all repository failures uniformly can catch `RepositoryError`.

A final process-level boundary can allow unexpected exceptions to terminate execution rather than hiding them.

This distinction is important because exception handling is also a policy decision. Handling an exception means the program has decided that the failure is understood at that point in the architecture.

## Exception Chaining

The Python implementation uses exception chaining when low-level failures are translated into domain failures.

Conceptually:

`JSONDecodeError`
→ `ValidationError`

The outer exception communicates the domain meaning. The chained exception preserves the technical cause.

This is preferable to discarding the original error because logs and debugging tools can still identify where the failure originated.

## Repository Workflow Model

The repository scenario is organized around the following conceptual flow:

`Repository`
→ `Branch`
→ `Commit`
→ `Pull Request`
→ `Review`
→ `Review Comment`
→ `Status Check`
→ `Merge Policy`
→ `Merge Eligibility`
→ `Merge`

Exception handling is applied at different points in that workflow.

A missing repository is a domain lookup failure.

Malformed JSON is an input failure.

An invalid branch name is a validation failure.

A failed status check is a workflow decision rather than a Python runtime exception.

A missing approval is also a policy result rather than necessarily an exceptional programming failure.

This distinction prevents normal negative business decisions from being represented as exceptions when a normal result is more appropriate.

## Pull Request Lifecycle

A Pull Request represents a proposed change from a source branch into a target branch.

Typical states represented by the implementations include:

| State | Meaning |
|---|---|
| Draft | Work is still being prepared |
| Open | Change is available for review |
| Blocked | One or more merge conditions are unsatisfied |
| Mergeable | Required conditions are satisfied |
| Merged | Changes have entered the target branch |
| Closed | Work was closed without merging |

The Python implementation evaluates a Pull Request using explicit conditions for source and target branches, approval counts, status checks, and resolved conversations.

The decision is returned as an `OperationResult` rather than throwing an exception for every policy failure.

## Code Review

Code review evaluates the quality and correctness of proposed changes.

The model distinguishes:

- reviewer identity
- review decision
- approval
- requested changes
- unresolved conversations
- review payload validation

An invalid review payload is an input failure and therefore produces a validation exception.

A valid review that requests changes is not malformed input. It is a legitimate review decision. The merge evaluation therefore treats that condition as a blocking policy result.

This distinction is important:

`invalid input` is a failure of data validity.

`changes requested` is a valid domain decision.

## Approvals

Approvals represent explicit reviewer decisions.

The implementations treat an approval as active only when the approval has not been dismissed. Required approval counts are evaluated separately from the existence of review records.

A Pull Request can therefore contain reviews without being mergeable.

For example:

`2 required approvals`
+
`1 active approval`
=
`not mergeable`

An approval can also cease to contribute to eligibility if it is dismissed or otherwise invalidated by repository policy.

## Branch Protection

Branch protection is repository-level enforcement.

The PostgreSQL implementation stores protection policy explicitly, including:

| Policy | Database representation |
|---|---|
| Required approvals | `required_approvals` |
| Required checks | `require_status_checks` |
| Resolved conversations | `require_resolved_conversations` |
| Direct-push restriction | `restrict_direct_push` |
| Force-push restriction | `restrict_force_push` |
| Branch deletion restriction | `restrict_deletion` |
| Linear history | `require_linear_history` |

These controls are different from reviews and approvals.

A review records an evaluation.

An approval records a decision.

Branch protection defines the conditions under which a repository permits a merge.

## JavaScript Implementation

The JavaScript implementation uses Node.js standard-library facilities and complements the Python design with asynchronous filesystem operations and event-driven workflow transitions.

`fs/promises` is used for asynchronous repository persistence.

`Error` subclasses represent domain-specific failures.

`cause` preserves the lower-level failure when a storage error wraps a filesystem error.

`EventEmitter` provides event-driven notification when workflow state changes.

The JavaScript implementation therefore illustrates an important practical difference from synchronous Python examples: exception handling also has to account for asynchronous operations.

Async failures are handled with `try` and `catch` around `await` expressions.

## JavaScript State Transitions

The JavaScript workflow explicitly defines allowed transitions.

For example:

`draft -> open`

`open -> mergeable`

`mergeable -> merged`

Invalid transitions raise `ValidationError`.

Terminal states such as `merged` and `closed` do not permit arbitrary transitions.

This is preferable to assigning state values without validation because invalid state transitions become detectable at the domain boundary.

## C++17 Governance Engine

The C++17 implementation models exception handling around a repository governance engine.

The main domain types are:

- `Review`
- `StatusCheck`
- `PullRequest`
- `Repository`
- `RepositoryGovernanceEngine`

C++ exception classes derive from `std::runtime_error`.

`ValidationError` identifies invalid domain data.

`MergePolicyError` identifies an attempted operation that violates merge policy.

The governance engine counts active approvals with STL algorithms and evaluates status checks using `std::all_of`.

The repository uses `std::map` for Pull Request lookup and `std::optional` for an explicit missing-record result.

This is a deliberate distinction from throwing an exception for every lookup miss. Absence can be represented normally when it is expected, while an invalid merge operation can remain exceptional.

## Java 17 Enterprise Model

The Java implementation uses records for immutable domain data and interfaces for policy abstraction.

The principal domain types are:

- `Review`
- `StatusCheck`
- `PullRequest`
- `MergePolicy`
- `ProtectedBranchPolicy`
- `PullRequestService`

The `MergePolicy` interface allows merge eligibility to be separated from the service that performs the merge.

The policy evaluates:

1. Pull Request state
2. active changes-requested reviews
3. active approvals
4. required status checks
5. unresolved review conversations

A failed policy evaluation produces a `MergePolicyException`, while invalid domain data produces a `ValidationException`.

The service catches unexpected runtime failures and wraps them in a repository-level exception with the original cause preserved.

## PostgreSQL Relational Model

The PostgreSQL implementation represents exception-related workflow behavior through relational constraints, functions, triggers, and transactional operations.

The core relationships are:

`repositories`
→ `branches`
→ `commits`

and:

`repositories`
→ `pull_requests`
→ `reviews`
→ `review_comments`

with:

`pull_requests`
→ `status_checks`

and:

`branches`
→ `branch_protection_policies`
→ `approval_requirements`

The database uses PostgreSQL enum types for controlled workflow states.

Foreign keys enforce entity relationships.

Check constraints reject invalid values.

Unique constraints prevent duplicate repository and branch identities.

Partial indexes accelerate active review and unresolved-comment queries.

## Database-Level Validation

The `validate_pull_request_branches` trigger verifies that Pull Request branches belong to the same repository and that source and target branches differ.

This is important because application-level validation alone cannot guarantee correctness when multiple applications or direct SQL clients can modify the database.

The database therefore provides a second enforcement boundary.

The merge-eligibility function evaluates the current database state rather than trusting a cached application decision.

## Merge Eligibility

The PostgreSQL function `pull_request_merge_eligibility` evaluates:

- Pull Request existence
- workflow state
- active changes-requested reviews
- required approvals
- unresolved review conversations
- status-check results
- branch protection policy

It returns both a Boolean eligibility result and a human-readable reason.

This is useful for reporting because a blocked Pull Request needs an explanation, not only a false value.

Examples include:

`Required approvals are missing.`

`Unresolved review conversations remain.`

`Required status checks have not all passed.`

`An active changes-requested review exists.`

## Transactional Merge

The `merge_pull_request` function locks the Pull Request row with `FOR UPDATE`, evaluates the current policy, and changes the state to `merged` only when the policy succeeds.

The operation is executed inside a transaction.

This prevents a merge decision from being separated from the state update by another concurrent transaction.

The transactional boundary is especially important for workflow systems because merge eligibility can change while a user is reviewing a Pull Request.

## Failure Handling Across the Five Implementations

| Failure | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Missing repository | Custom exception | Custom error | Optional / validation | Domain exception | Query result |
| Invalid input | `ValidationError` | `ValidationError` | `ValidationError` | `ValidationException` | Constraints |
| Malformed JSON | Chained exception | `SyntaxError` wrapped as storage error | Not applicable | Parsing exception example | Not applicable |
| Failed checks | Policy result | Policy result | Boolean policy result | Policy result | Eligibility result |
| Missing approvals | Policy result | Policy result | Policy result | Policy result | Eligibility result |
| Invalid transition | Validation exception | Validation error | State/policy error | Domain exception | State constraints/functions |
| Storage failure | `StorageError` | `StorageError` | In-memory model | Domain service boundary | Transaction/database error |

The table demonstrates a key design principle: not every negative result should be an exception.

## Error Handling Rules

A robust exception-handling boundary should answer three questions:

1. What failure can occur here?
2. Can this layer recover from it?
3. If the error is translated, is the original cause preserved?

The implementations use narrow exception handling because broad handlers can hide defects.

Good handling:

`try` a specific operation.

`except` a known recoverable failure.

Translate it only when the receiving layer needs a different domain abstraction.

Preserve the original cause when useful.

Allow unexpected failures to remain visible.

Avoid:

`except Exception: pass`

or equivalent patterns that silently discard failures.

## `finally` and Cleanup

The Python implementation uses `TemporaryDirectory`, which provides deterministic cleanup through a context manager rather than manually duplicating cleanup in every failure branch.

The same principle applies to `finally`: cleanup should be placed in a mechanism that executes regardless of success or failure.

Resource cleanup is separate from error classification.

The failure handler determines what happened.

The cleanup mechanism ensures resources are released.

## Performance Considerations

Exception handling should not replace ordinary branching for frequent expected decisions.

The merge-policy implementations use ordinary Boolean decisions for conditions such as:

- insufficient approvals
- failed status checks
- unresolved conversations
- active change requests

Exceptions are used for invalid operations, malformed inputs, unavailable storage, and domain failures where exceptional control flow is appropriate.

The PostgreSQL implementation adds indexes for queries that repeatedly filter Pull Requests, active reviews, unresolved comments, and status checks.

The Java and C++ implementations use in-memory collections and linear scans suitable for the small case-study data volume. A larger repository service would require persistent indexing and careful query planning.

## Security Considerations

Exception messages should not expose secrets, credentials, access tokens, or sensitive repository data.

The examples return controlled domain messages instead of dumping raw filesystem or database internals to users.

Exception chaining remains useful for server-side diagnostics, but production systems should separate internal diagnostic logs from externally visible messages.

Database constraints provide defense against invalid state even when application validation is bypassed.

Protected branches reject direct modification through explicit policy representation.

Force-push restrictions and merge requirements are represented as repository governance controls rather than being treated as review comments.

## Edge Cases

The implementations cover several failure boundaries:

- empty repository names
- empty branch names
- identical source and target branches
- negative approval counts
- zero reviewers for division
- malformed JSON
- missing JSON fields
- missing repositories
- invalid workflow transitions
- failed status checks
- insufficient approvals
- unresolved review conversations
- active changes-requested reviews
- dismissed approvals
- malformed stored records
- missing database relationships
- protected-branch merge failures

These cases demonstrate why exception handling must be designed around domain boundaries rather than inserted mechanically around every statement.

## Relationship Between the Four Repository Concepts

The repository concepts remain distinct:

`Pull Request`
provides the workflow for proposing a change.

`Code Review`
evaluates the proposed change through reviews, comments, and reviewer decisions.

`Approvals`
represent explicit review decisions that may contribute to merge eligibility.

`Branch Protection`
enforces repository-level conditions before a merge is permitted.

Their relationship is:

`Pull Request`
→ `Code Review`
→ `Approval`
→ `Branch Protection`
→ `Merge Eligibility`
→ `Merge`

A Pull Request can exist without approval.

A review can exist without being an approval.

An approval can exist without making a Pull Request mergeable.

A branch can require conditions that go beyond the review state.

## Practical Design Decisions

The implementations deliberately distinguish three categories:

### Exceptional failures

Examples include malformed external data, unavailable storage, invalid domain input, and illegal state transitions.

### Valid negative decisions

Examples include a failed status check or insufficient approvals.

These are legitimate workflow outcomes and can normally be represented by Boolean or result values.

### Enforcement failures

Examples include an attempted merge that violates branch protection.

These may be represented as a domain-specific exception at a service boundary because the requested operation cannot be completed.

This classification keeps exception handling meaningful and prevents ordinary workflow states from becoming indistinguishable from programming errors.

## File Responsibilities

| File | Responsibility |
|---|---|
| Python | JSON-backed repository workflow, custom exception hierarchy, validation, exception chaining, and controlled failure results |
| JavaScript | Asynchronous persistence, error causes, merge-policy evaluation, and event-driven state transitions |
| C++17 | Repository governance engine using STL algorithms, `optional`, custom exceptions, and explicit merge policy |
| Java 17 | Enterprise-style immutable domain model, policy interface, service boundary, records, streams, and custom exceptions |
| PostgreSQL | Relational workflow, constraints, trigger validation, policy functions, indexes, reporting, and transactional merge |

## Limitations

The examples are intentionally self-contained.

They do not implement a network API, authentication provider, distributed locking service, remote Git server, or production repository hosting platform.

The exception-handling mechanisms are real, but the repository workflow is a controlled technical model.

The PostgreSQL model does not attempt to reproduce every feature of a commercial Git hosting platform. Its purpose is to show how repository workflow state and enforcement rules can be represented relationally and evaluated transactionally.

The Python filesystem store is suitable for a small executable case study, not concurrent production persistence.

The JavaScript asynchronous store is similarly designed for local execution rather than multi-process coordination.

## Execution

The Python file can be executed directly with Python 3.

The JavaScript file can be executed with a current Node.js runtime.

The C++ source requires a compiler supporting C++17.

The Java source requires Java 17 or later.

The SQL script requires PostgreSQL with support for schemas, enums, PL/pgSQL, triggers, and transactional SQL.

The five implementations are intentionally independent. Each one can be examined separately while using the same domain vocabulary for comparison.
