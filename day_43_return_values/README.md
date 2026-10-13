# Return Values: A Technical Study Across Python, JavaScript, C++, Java, and PostgreSQL

## Introduction

A return value is the result a function, method, generator, or database routine communicates to its caller. It defines an important boundary between an operation and the code that depends on its outcome.

A return value can represent a computed quantity, a collection of records, a decision, an optional result, a successful operation, or a failure explanation. The type and structure of that value determine how callers can interpret it.

Return values are closely related to error handling, API contracts, data ownership, asynchronous execution, and program control flow. These relationships become especially important when a function participates in a larger workflow.

This study uses repository governance as a recurring domain. Pull Requests provide the workflow for proposing changes, code review evaluates the changes, approvals record reviewer decisions, and branch protection determines which conditions must be satisfied before a merge. These concepts supply realistic examples of return values that communicate decisions and operational outcomes.

## Core semantics

### Returning a value versus changing control flow

A return statement terminates the current function invocation and transfers a result to the caller. Statements after an executed return are not reached during that invocation.

Consider an approval-counting function. It may return the number of eligible approvals after examining review records. An early return can instead reject an invalid request before database access or expensive processing occurs.

Returning a result is different from printing a message. Printing writes information to an output stream. Returning makes a value available to the caller for comparison, storage, transformation, or further computation.

The distinction is equally important when a function returns no meaningful value. Python produces `None` when execution reaches the end of a function without an explicit return. JavaScript produces `undefined` in the equivalent situation. Neither value should be confused with an explicit result that communicates successful completion.

### Return values and exceptions

A function may communicate failure through an exception or through a value representing failure.

Exceptions are useful when an operation cannot continue under its contract, such as when a required identifier has an invalid type. A result object is useful when failure is an expected business outcome, such as a merge blocked by an unresolved review discussion.

These mechanisms express different contracts:

| Mechanism | Meaning | Appropriate use |
|---|---|---|
| Ordinary value | The operation produced a result | Invoice total, approval count, branch identifier |
| Optional value | A result may legitimately be absent | User lookup, missing configuration |
| Result object | Success or expected failure is represented explicitly | Merge decision, configuration validation |
| Exception | The operation could not satisfy its contract | Invalid input, forbidden state transition |
| Generator yield | An incremental item is available | Streaming batches of review records |
| Promise or future | An asynchronous result will become available | Build checks or remote repository operations |

A caller should not have to guess which interpretation applies. Function names, type declarations, documentation, and tests should agree on the return contract.

## Optional values and valid falsy results

An absent result is not the same as a valid result containing zero, false, or an empty string.

A discount lookup may legitimately return a discount rate of `0.0`. A successful operation may return an empty string. A boolean policy check may legitimately return `False`.

Treating all falsy values as failures loses this distinction.

Python's `is None` check explicitly distinguishes absence from numeric zero. JavaScript's `??` operator provides a nullish fallback for `null` and `undefined`, while `||` also replaces valid falsy values such as zero and the empty string.

In Java, `Optional<T>` expresses possible absence, while an operation-result type can distinguish failure from success. PostgreSQL uses `NULL` to represent unknown or absent values, and a query must account for its three-valued logic.

A robust interface defines what absence means rather than relying on truthiness.

## Structured return values

Returning multiple related facts as a tuple, record, object, or composite database result is often clearer than returning a single unstructured value.

An invoice calculation might return a subtotal, tax amount, and final total. A merge evaluator might return:

- An eligibility boolean.
- The number of effective approvals.
- A collection of blocking policy conditions.

A structured result preserves relationships among these values. It also allows a caller to distinguish the primary decision from its explanation.

The design should remain proportional to the problem. A short pair of related values may suit a tuple. A result consumed by several modules often benefits from a named class or record with explicit fields.

## Python implementation

The Python script progresses from ordinary functions to explicit result contracts and lazy computation.

### Basic functions and guard clauses

`calculate_total` validates its arguments and returns a numeric result. `stop_if_empty` uses an early return for the empty case, illustrating how control flow can produce either a meaningful value or `None`.

The expense-approval example uses guard clauses to reject invalid amounts and insufficient budgets before returning the final decision. This reduces nested conditions and makes each failure condition independently testable.

### Tuples, dictionaries, and dataclasses

`analyze_measurements` returns a tuple containing the minimum, maximum, and count. Tuple unpacking allows callers to assign meaningful local names to the individual values.

`inventory_report` returns a dictionary because its fields have descriptive names. `TemperatureReading` uses a frozen dataclass to group a location, measurement, and validity flag into a stable record.

These representations show that the return structure should reflect how the caller uses the result.

### `None` and sentinel objects

`find_discount` returns `None` when a code is absent but preserves a valid zero discount.

`configure_timeout` introduces a unique sentinel to distinguish an omitted argument from an explicit `None`. This is useful when omission means a default timeout but explicit `None` means that timeouts are disabled.

The distinction cannot be expressed reliably with a truthiness check alone.

### Mutable objects and ownership

Returning a list or dictionary exposes a reference to an object. If that object is shared, callers can change state that subsequent calls observe.

The script contrasts a shared cache with a copied settings dictionary. A copy provides isolation for the demonstrated flat dictionary, but a shallow copy does not isolate nested mutable objects. The JavaScript implementation uses a separate example to illustrate a frozen snapshot with a copied nested array.

The correct design depends on whether the returned object represents owned data, a read-only view, or intentional shared state.

### Generators and lazy return behavior

The `read_batches` generator uses `yield` to deliver batches incrementally. Its final `return` value becomes the value carried by `StopIteration` after the generator is exhausted.

This is different from a function that immediately returns a list. A generator can avoid allocating an entire result collection and can process larger inputs incrementally.

The example deliberately consumes the iterator with `next` so that its terminal value can be inspected. Ordinary iteration generally handles termination internally and does not expose that terminal value as part of the collection.

### Higher-order functions and recursion

`make_tax_calculator` returns a function that retains the configured tax rate. The returned function forms a closure over that rate.

`compose` combines transformations by passing the first function's return value into the second. The example demonstrates how explicit return contracts allow functions to form pipelines.

`factorial` shows how recursive calls return partial results to their callers. `fibonacci_cached` uses memoization to avoid repeatedly evaluating the same subproblems.

Caching is appropriate only when the function's result is determined by its arguments and cached values remain valid. Side effects and mutable external state can invalidate that assumption.

### Explicit operation results

`OperationResult` models success and failure as distinct states. Its constructor rejects contradictory states, such as a successful result that also contains an error message.

This is useful for operations where failure is expected and callers must inspect the outcome before proceeding. The file-reading example returns a successful string or a descriptive failure result instead of requiring every missing file to terminate the entire workflow.

`require_nonempty_text` demonstrates runtime validation of a return contract. Python type hints assist static analysis but do not enforce return types at runtime. Explicit checks remain necessary when untrusted or dynamically typed values cross a boundary.

## JavaScript implementation

The JavaScript file emphasizes asynchronous outcomes, event-driven behavior, and the difference between returned values and emitted values.

### Synchronous return contracts

`calculateInvoice` validates invoice lines and returns a structured object containing the subtotal, tax, and total. Invalid input produces a thrown error rather than a misleading partial calculation.

`parseDeploymentConfiguration` returns a discriminated result object. Its `success` field determines whether the caller should read a value or an error.

The object is frozen to prevent changes to its top-level result fields. Freezing is shallow, so nested objects require their own protection when immutability is important.

### Promises and `async` functions

`checkBuild` returns a Promise. Calling `resolve` supplies its fulfillment value, while calling `reject` communicates failure.

An `async` function returns a Promise even when its body appears to return an ordinary value. When `await` is applied to a fulfilled Promise, the fulfillment value becomes available. A rejection propagates as an exception unless it is handled.

`Promise.all` returns an array when every supplied Promise fulfills. If any input rejects, the aggregate Promise rejects. `Promise.allSettled` instead preserves each operation's fulfilled or rejected status, which is useful when build jobs should be reported independently.

### Generators

A JavaScript generator can both yield values and return a terminal value. Calling `next()` returns an object with `value` and `done` fields.

When `done` is false, `value` contains a yielded item. When `done` is true, `value` contains the generator's final return value.

Collection helpers such as `Array.from` collect yielded items and do not include the final return value. This matters when a generator uses its terminal return to communicate a final count or completion record.

### Event-driven workflows

`PullRequestWorkflow` models a small event-driven lifecycle. Its methods return updated request snapshots, while subscribers receive events describing changes.

The class keeps its request map and listener set private. Returned request objects and their check maps are frozen, so consumers cannot directly alter the stored request state through a returned snapshot.

The `subscribe` method returns an unsubscribe function. This is itself a meaningful return value: it gives the caller control over the lifetime of the subscription.

The workflow is a local simulation, not a replacement for a repository hosting service. It does not implement Git object storage, distributed synchronization, authentication, or a real merge operation.

### Policy evaluation

`evaluateMergePolicy` returns an eligibility decision and a list of blocking conditions. It does not perform the merge.

Keeping evaluation separate from execution allows a user interface to display blockers before attempting a state-changing operation. In a production service, the final merge operation must evaluate the current policy again because checks, reviews, or the target branch can change between an earlier evaluation and the attempted merge.

## C++ case study: Repository governance and merge eligibility

The C++ program models a repository governance engine for a protected `main` branch.

A developer proposes an audit-log change from a feature branch. The repository requires two effective approvals, passing unit tests and a security scan, resolved review conversations, linear-history compatibility, and a current code-owner approval.

### Domain architecture

`Branch` represents source and target branches, including their commit histories and branch characteristics.

`PullRequest` owns the request lifecycle, requested reviewers, reviews, review conversations, status checks, synchronization state, and applicable policy.

`ProtectionPolicy` stores the governance rules that the merge evaluator must enforce. `MergeDecision` represents the result of evaluating those rules.

The design keeps policy evaluation separate from the final merge operation. That separation permits the program to report blockers without modifying the target branch.

### Result type and failure handling

The generic `Result<T>` class stores either a successful value or an error message in `std::variant`.

`ok()` reports which alternative is active. `value()` rejects access to a failed result, and `error()` rejects access to a successful result.

This contract distinguishes a successful empty string from a failed operation. An empty string can be a valid payload, so using an empty string as the sole failure indicator would be ambiguous.

The implementation uses exceptions for malformed construction and illegal state transitions, while `Result<T>` represents expected failures such as an unauthorized or ineligible merge.

### Review decisions and approvals

Review submission validates that the reviewer was requested and is not the author. The current review for a reviewer replaces that reviewer's previous review, preventing a historical approval from automatically counting as another independent vote.

An approval records the source commit that was reviewed. When stale approvals are disallowed, a later source commit invalidates those approvals for merge eligibility until reviewers submit current decisions.

Dismissal is a separate administrative operation. It changes the state of an existing approval rather than treating dismissal as a new ordinary review.

### Review discussions and status checks

Inline comments carry a file path, line number, and body. The program validates these fields at construction.

Review conversations are tracked independently from review states. An approval does not automatically resolve a conversation, because a reviewer may approve the general change while a particular discussion remains unresolved.

Status checks are stored by name. The evaluator verifies every required check and rejects a missing or failing result.

### Synchronization and merge strategies

The target branch's head is recorded when the request is created. If the target branch changes, the request is marked as requiring synchronization.

The case study does not implement Git's content-level merge algorithm. It models the governance consequence of a target-head change and requires explicit confirmation of synchronization or conflict resolution. This distinction avoids claiming that comparing commit identifiers is sufficient to detect real textual conflicts.

The merge method models merge-commit, squash, and rebase choices as different recorded operations. A production implementation must verify that the selected strategy is permitted by the hosting platform and branch policy.

The example demonstrates an initially blocked request, resolution of a review conversation, approval staleness after a source update, and a final attempt to merge after new approvals.

## Java implementation: Enterprise governance model

The Java program applies explicit domain types to repository policy evaluation.

### Records and domain objects

Java records represent commits, review comments, reviews, merge decisions, and operation results. Their compact constructors enforce invariants at the point of construction.

`Branch` encapsulates branch state and returns an immutable copy of its commit list. `PullRequest` manages review requests, current reviewer decisions, status checks, discussion state, and lifecycle transitions.

`BranchProtectionPolicy` is immutable after construction. Its required checks, code owners, and bypass actors are copied into immutable sets. This prevents a caller from changing policy by mutating a collection supplied to the constructor.

### Explicit lifecycle transitions

The request starts in either `DRAFT` or `OPEN`. Publishing a draft transitions it to `OPEN`; closing an active request transitions it to `CLOSED`; reopening is permitted only from `CLOSED`; and a successful merge transitions it to `MERGED`.

Invalid transitions raise `IllegalStateException` rather than returning a misleading success value.

This approach places lifecycle rules inside domain methods rather than relying on each caller to implement the same conditions.

### Review and approval semantics

The program stores the latest review for each reviewer in a map. A new review replaces the previous decision, so an old approval cannot remain effective after a reviewer changes their decision to `CHANGES_REQUESTED` or `COMMENTED`.

The merge evaluator filters approvals by the reviewed commit when stale approvals must be dismissed. It also excludes the author and verifies the presence of a required code-owner approval.

This is a simplified enterprise policy model. Actual hosting platforms may implement more detailed rules for reviewer teams, review dismissal, code-owner matching, and permissions.

### Result objects and Java-specific trade-offs

`OperationResult<T>` distinguishes success from failure and validates its internal state. `Optional<T>` provides a representation for a possibly absent payload.

The distinction between `Optional.empty()` and a failed operation remains important. An optional value represents absence, whereas an operation result represents whether the operation succeeded.

Java's static type system makes domain contracts easier to inspect and refactor. It does not remove the need for runtime validation at application boundaries or authorization checks at service boundaries.

## PostgreSQL data model and return behavior

The SQL script models repository governance as relational data.

### Relational entities

| Table | Responsibility |
|---|---|
| `repository` | Identifies a repository and its default branch |
| `repository_user` | Stores reviewer and contributor identities |
| `repository_branch` | Stores branch heads and protection characteristics |
| `branch_protection_policy` | Defines merge governance rules |
| `policy_required_check` | Stores the checks required by a policy |
| `policy_code_owner` | Identifies eligible code owners |
| `policy_bypass_actor` | Records authorized policy bypass actors and their reasons |
| `pull_request` | Stores request lifecycle and synchronization information |
| `pull_request_commit` | Records commits associated with a request |
| `review_request` | Records requested reviewers |
| `pull_request_review` | Stores review decisions and reviewed revisions |
| `review_comment` | Stores inline comments and resolution state |
| `review_conversation` | Tracks discussion resolution separately from approvals |
| `pull_request_status_check` | Records named check outcomes and the commits they evaluated |

Primary keys identify records. Foreign keys preserve relationships between repositories, branches, users, policies, requests, and reviews. Unique constraints prevent duplicate repository identities and repeated check names within one request.

Check constraints reject invalid approval counts, empty identifiers, invalid comment line numbers, and inconsistent merge metadata.

### PostgreSQL return mechanisms

PostgreSQL provides several ways for a routine to communicate a result.

A scalar function can return a boolean, number, or text value. A table-returning function can return multiple rows. A composite return type can represent a structured record. PL/pgSQL routines can raise exceptions when a caller violates an operation's contract.

The script defines `is_current_approval` as a boolean function and `merge_blockers` as a table-returning function. `evaluate_pull_request` aggregates the blockers into an eligibility result, count, and explanation.

The blocker function reports missing or failing checks, insufficient approvals, stale synchronization, unresolved conversations, and missing code-owner approval.

### Approval counting and review history

Historical reviews should not be counted as independent votes. The merge-eligibility query selects the latest review for each reviewer using `DISTINCT ON` and an ordering that includes the review identifier to break timestamp ties.

The query then counts only current approvals, excludes the author, and optionally checks whether each approval refers to the current source revision.

This approach preserves review history while computing an effective approval state. It also makes approval policy changes auditable because previous decisions are not silently overwritten.

### Database-level policy enforcement

The schema includes indexes for repository-state searches, status-check lookups, review-history ordering, and unresolved discussions.

The branch trigger rejects protected-branch head updates and enforces deletion restrictions represented in policy records. It serves as defense in depth, not as a substitute for Git hosting permissions, server-side receive hooks, or application authorization.

The demonstration uses a transaction and ends with `ROLLBACK`, leaving the example data uncommitted. A deployment that needs to retain the records can change the transaction ending after reviewing the statements.

The SQL examples show why a returned eligibility decision is not equivalent to a guaranteed merge. The underlying records can change after evaluation. A production merge transaction should lock or otherwise coordinate relevant records, recheck policy, and perform the state change atomically.

## Distinctions that matter in production

### A successful result is not a successful side effect

An eligibility function may correctly return `true`, but that does not prove that a merge subsequently completed. The branch could change, a permission could be revoked, or a required check could be invalidated between evaluation and execution.

The final operation must verify the relevant conditions at the point where it changes state.

### Return values and mutable state

Returning a reference to mutable data exposes that data to callers. A function should make its ownership contract clear.

Immutable records, copied collections, and explicit result types reduce accidental changes. They do not replace authorization, concurrency control, or validation of external inputs.

### Errors and business decisions

A rejected merge is often an ordinary policy outcome rather than a programming defect. Returning a structured decision with specific blockers allows a caller to display a useful explanation and take corrective action.

An invalid request state or corrupted invariant is different. It may justify an exception because the operation cannot satisfy its expected contract.

### Asynchronous results

A Promise, future, or asynchronous task represents a result that may not be immediately available. Its contract includes both eventual success and failure.

Callers must handle rejection paths, timeouts, cancellation where supported, and partial failure when multiple independent tasks execute together.

### Performance and allocation

Returning a small scalar is generally inexpensive. Returning large collections can incur allocation and copying costs. Generators and streaming interfaces can reduce memory usage when a caller can process results incrementally.

The choice should reflect the workload. A streaming interface is useful for large review histories, while a structured object is usually clearer for a small merge decision.

## Testing return contracts

Return-value tests should verify the observable contract rather than only checking that a function executes.

Useful assertions include:

- A valid invoice returns the correct subtotal, tax, and total.
- A missing lookup is distinguishable from a valid zero value.
- A failed operation does not expose a successful payload.
- A stale approval does not satisfy the current approval requirement.
- A missing status check produces a merge blocker.
- A resolved discussion does not automatically create an approval.
- A rejected merge does not change the target branch.
- A generator's final return is distinguishable from the items it yields.
- An asynchronous rejection is handled rather than silently ignored.

Tests should also verify invalid transitions, malformed inputs, duplicate identities, and state changes between evaluation and execution.

The most reliable return-value design is one in which callers can determine what happened, what data is available, and which conditions remain unsatisfied without guessing from incidental output or ambiguous sentinel values.
