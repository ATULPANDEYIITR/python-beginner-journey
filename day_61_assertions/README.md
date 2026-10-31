# Assertions

## Scope

This project treats assertions as executable correctness conditions rather than as a synonym for general input validation.

An assertion expresses a condition that the program or data model expects to be true. The implementations use assertions for internal assumptions, invariants, and postconditions while using explicit exceptions or database constraints for externally supplied data.

The central distinction is:

- **Precondition:** what must be true before an operation starts.
- **Postcondition:** what must be true after an operation completes.
- **Invariant:** what must remain true throughout the lifetime of an object or workflow.
- **Validation:** rejection of invalid external input.
- **Assertion:** an executable check that protects an expected correctness property.

The source files use the same conceptual model while giving each language a distinct engineering treatment.

## Domain Model

The repository-development scenario provides concrete state that can be checked.

    Repository
      |
      +-- Branches
      |     |
      |     +-- default branch
      |     +-- feature branch
      |
      +-- Commits
            |
            +-- Pull Request
                  |
                  +-- Reviews
                  |     |
                  |     +-- approvals
                  |     +-- unresolved comments
                  |
                  +-- Status Checks
                  |
                  +-- Merge Eligibility

Assertions operate at different boundaries in this model.

A repository must have a valid name and default branch. A pull request must have different source and target branches. A merged pull request must contain commits and must not remain a draft. These are domain invariants.

A duplicate commit ID or empty repository name is external or operationally supplied data and is therefore rejected explicitly rather than relying only on an assertion.

## Python Implementation

The Python file models repositories and pull requests with `dataclass` objects, enums, lists, and sets.

`require()` raises `ValidationError` for conditions that must be enforced regardless of interpreter optimization. This is important because Python's `assert` statement can be disabled when Python is executed with optimization.

`ensure()` represents a postcondition. The repository and pull-request classes use private invariant checks after state-changing operations.

The pull-request workflow is:

    create PR
       |
       v
    add commits
       |
       v
    draft
       |
       v
    mark ready
       |
       v
    merge

The implementation rejects invalid transitions such as adding a commit after merging.

The average-calculation function provides a smaller mathematical example. It validates non-empty input and then asserts that the calculated average lies between the minimum and maximum input values.

The test routine exercises successful operations, duplicate commits, invalid branches, empty collections, and mutation after merge.

### Python Assertion Design

The important design decision is separating assertions from validation.

Use assertions for internal assumptions such as:

- an object invariant was preserved
- a postcondition holds
- a collection remains internally consistent
- a mathematical result satisfies a known property

Use explicit exceptions for:

- user input
- configuration
- external data
- API requests
- database values
- conditions that must always be enforced in production

This distinction prevents a production correctness rule from disappearing merely because interpreter optimization is enabled.

## JavaScript Implementation

The JavaScript implementation uses Node.js standard-library modules.

`node:assert/strict` supplies assertion operations, while `EventEmitter` models state-related events.

The `Repository` class uses a `Set` for commit identity. The `PullRequest` class maintains explicit state and emits events when commits are added, a draft becomes ready, or a pull request is merged.

The event sequence is:

    commitAdded
         |
         v
       ready
         |
         v
       merged

This makes the implementation different from the Python version. The focus is not only object invariants but also event-driven state observation.

The asynchronous example uses a Promise-based state read and verifies the returned structure with strict assertions.

Explicit `ValidationError` handling remains separate from `assert`. This makes invalid external data a normal application error while keeping assertions focused on program correctness.

## C++17 Implementation

The C++ program implements a repository governance scenario with classes, enums, STL containers, and exception handling.

`Repository` stores commit identifiers in a `std::set`, providing efficient duplicate detection.

`PullRequest` uses:

- `std::vector` for ordered commits
- `std::vector` for reviews
- `enum class` for workflow state
- assertions for internal invariants
- exceptions for invalid operations

A pull request can merge only when:

1. it is open
2. it contains at least one commit
3. at least one review is approved
4. no review contains an unresolved discussion

This creates an explicit merge-eligibility calculation rather than treating approval as equivalent to merge permission.

The program also demonstrates the difference between validation and assertion. Constructor arguments and invalid operations produce exceptions. Internal state relationships are checked with `assert`.

The average function uses an assertion for a mathematical postcondition after validating the input.

## Java 17 Implementation

The Java implementation uses an enterprise-oriented domain model.

The `PullRequestState` enum represents explicit lifecycle states:

- `DRAFT`
- `OPEN`
- `MERGED`
- `CLOSED`

`Review` is a Java record representing immutable review information.

`AssertionPolicy<T>` demonstrates a generic policy abstraction. `RangePolicy` implements the interface for reusable numeric validation.

The pull-request object separates:

- state transitions
- review records
- approval evaluation
- merge eligibility
- invariant checking

The merge operation cannot execute unless the eligibility conditions are satisfied.

Streams are used for approval and unresolved-comment evaluation. This provides a declarative expression of collection-wide conditions while retaining explicit domain state.

The Java implementation also demonstrates why domain validation should not depend exclusively on Java's `assert`. Assertions are disabled unless the JVM is started with the appropriate assertion-enable option. Conditions that must always protect application state therefore use explicit exceptions.

## PostgreSQL Implementation

PostgreSQL represents assertions through database mechanisms because PostgreSQL does not provide the SQL-standard `CREATE ASSERTION` feature.

The schema uses:

- primary keys
- foreign keys
- unique constraints
- check constraints
- partial indexes
- triggers
- PL/pgSQL functions
- transactional merge logic
- CTE-based reporting

The principal entities are:

    repositories
        |
        +-- branches
        |
        +-- commits
        |
        +-- pull_requests
                 |
                 +-- pull_request_commits
                 |
                 +-- reviews
                 |      |
                 |      +-- review_comments
                 |
                 +-- status_checks
                 |
                 +-- branch_protection_policies

Column-level and row-level rules use `CHECK` constraints.

Examples include:

- repository names cannot be empty
- branch names cannot be empty
- commit hashes must be non-empty
- pull-request numbers must be positive
- source and target branches must differ
- merged pull requests must have a merge timestamp
- merged pull requests cannot remain drafts
- approval requirements cannot be negative

The trigger on `pull_request_commits` enforces a cross-table invariant: the commit and pull request must belong to the same repository.

The branch trigger checks that both pull-request branches belong to the repository associated with the pull request.

## Database Merge Assertions

The `merge_pull_request` function performs several cross-row checks before changing state.

The operation requires:

    OPEN state
        |
        +-- non-draft
        |
        +-- at least one commit
        |
        +-- required number of approvals
        |
        +-- no unresolved review comments
        |
        +-- no failed status checks
        |
        v
      MERGED

The function executes the validation and state transition inside a transaction.

The row is locked with `FOR UPDATE` before the final state transition. This reduces the risk of concurrent operations evaluating the same pull request against stale state.

## Assertions Versus Validation

The distinction is central to every implementation.

| Mechanism | Purpose | Example |
|---|---|---|
| Precondition | Required before an operation | A pull request must have a valid target branch |
| Postcondition | Expected after an operation | Adding a commit increases collection size |
| Invariant | Property that must remain true | Source and target branches differ |
| Assertion | Internal correctness check | Average lies between minimum and maximum |
| Validation exception | Reject invalid external input | Empty commit identifier |
| Database constraint | Persistently enforce data integrity | Unique repository and commit hash |
| Trigger | Enforce cross-row or cross-table rule | PR and commit belong to same repository |

An assertion should not be used merely because a condition is inconvenient to handle. The choice depends on whether the condition represents an internal correctness assumption or externally controlled data.

## Failure Handling

The implementations deliberately exercise failure cases.

Examples include:

- empty repository names
- empty branch names
- identical source and target branches
- duplicate commits
- empty collections
- invalid review identities
- mutation of merged pull requests
- missing approvals
- unresolved review conversations
- failed status checks
- inconsistent repository relationships

Failures are explicit and testable. Successful paths are also checked so that an assertion failure cannot be confused with expected validation behavior.

## Performance Considerations

The data structures match the operations being performed.

Python and JavaScript use sets for fast membership checks. Java uses a `HashSet` for repository commit identifiers. C++ uses `std::set`, providing ordered storage with logarithmic lookup and insertion.

The PostgreSQL schema adds indexes for frequently evaluated workflow conditions rather than indexing every column.

The partial indexes on unresolved comments and failed status checks limit index entries to records that can block merge eligibility.

For large repositories, cross-row assertions should be designed around indexed foreign keys and selective predicates. Expensive invariant checks on every write can become a transaction bottleneck.

## Security Considerations

Assertions are not an authorization mechanism.

A successful assertion does not prove that a caller is authorized to perform an operation.

Production systems should separately authenticate the actor and authorize operations such as:

- changing repository policy
- approving a pull request
- dismissing an approval
- merging protected branches
- bypassing repository controls

Assertions and validation protect correctness. Authorization protects access.

The database layer also avoids trusting application-side checks alone. Important relational integrity rules are enforced using constraints and triggers so that another database client cannot silently bypass the same rules.

## Production Behavior

A production design should distinguish checks that must remain active from checks intended primarily for debugging.

Python's `assert`, Java's `assert`, and C++'s `assert` can be disabled through runtime or compilation configuration.

Rules that must always execute should therefore use explicit exceptions, validation functions, constraints, or transactional database logic.

A useful production boundary is:

    External input
          |
          v
    Explicit validation
          |
          v
      Domain state
          |
          v
    Internal assertions
          |
          v
    Postcondition checks
          |
          v
    Persistent constraints

This layered approach prevents a disabled debugging assertion from becoming a data-integrity failure.

## Testing Strategy

The source files include executable checks rather than relying only on explanatory examples.

The tests cover both positive and negative paths:

| Test category | Expected behavior |
|---|---|
| Valid repository | Created successfully |
| Duplicate commit | Explicit validation failure |
| Valid pull request | State transitions succeed |
| Identical branches | Validation failure |
| Valid approval | Merge eligibility can become true |
| Unresolved comments | Merge blocked |
| Failed status check | Merge blocked |
| Merged pull request mutation | Operation rejected |
| Empty numeric input | Validation failure |
| Valid average | Postcondition holds |

The PostgreSQL script also performs a transactional merge after satisfying the database-level conditions and then retrieves the final workflow state.

## Limitations

Assertions cannot replace comprehensive tests.

An assertion generally checks one stated property at one execution point. It does not prove that all possible program states are correct.

Assertions also do not automatically establish:

- authorization
- concurrency safety
- complete business-rule coverage
- external system correctness
- data provenance
- availability
- recovery after infrastructure failure

Those concerns require their own mechanisms.

The PostgreSQL implementation approximates SQL-standard assertion semantics through constraints, triggers, and transactional functions. These mechanisms are practical but have different execution and maintenance characteristics from a hypothetical global `CREATE ASSERTION` facility.

## Cross-Language Comparison

| Language | Primary assertion mechanism | Domain technique |
|---|---|---|
| Python | `assert`, explicit `AssertionError` | Dataclasses and invariant methods |
| JavaScript | `node:assert/strict` | Event-driven state transitions |
| C++17 | `<cassert>` | Exception-backed validation and STL state |
| Java 17 | Java `assert` | Records, generics, policies, streams |
| PostgreSQL | Constraints, triggers, PL/pgSQL | Persistent relational invariants |

The common principle is consistent: assertions describe expected correctness, while durable validation mechanisms enforce conditions that cannot safely be disabled.

## Practical Rule Set

For application code, use assertions when a condition represents an internal assumption that indicates a programming defect if violated.

Use explicit validation when data comes from users, APIs, configuration, files, databases, or other external sources.

Use database constraints when the rule must hold for every client that can modify the database.

Use triggers or transactional functions when a rule depends on multiple rows or tables and cannot be expressed adequately with a simple constraint.

Use tests to verify both successful behavior and expected failures.

This separation keeps correctness checks meaningful without confusing debugging assertions with production validation or authorization.
