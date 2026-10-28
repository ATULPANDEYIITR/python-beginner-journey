# `else` and `finally` Through Repository Governance

## Scope

This project studies `else` and `finally` through a concrete repository-governance workflow.

The central distinction is:

- `else` represents logic that should execute only when the guarded operation completed without raising an exception.
- `finally` represents cleanup or finalization that must execute after the guarded operation, regardless of whether it succeeded or failed.

The repository domain provides a useful stateful setting because a merge decision has a normal success path, explicit policy failures, unexpected failures, and mandatory audit or cleanup operations.

The project also keeps four repository concepts distinct:

| Area | Role |
|---|---|
| Pull Requests | Propose a changeset from a source branch toward a target branch |
| Code Review | Evaluates the proposed changes through reviews and discussions |
| Approvals | Records review decisions that may contribute to merge eligibility |
| Branch Protection | Enforces repository-level conditions before merging |

The relationship is:

`Repository → Branches → Commits → Pull Requests → Reviews → Comments/Conversations → Status Checks → Branch Protection → Approval Requirements → Merge Eligibility → Merge`

`else` and `finally` operate around decisions within this workflow rather than replacing these repository concepts.

## `else` Semantics

The important property of an `else` clause attached to exception handling is that it represents the successful, non-exceptional path.

In Python, the following conceptual structure is used by the project:

`try → exception? → except : otherwise → else : always → finally`

The `else` block is not a generic alternative to `if`. It executes only when the protected `try` block completes without raising an exception.

That distinction matters when an application needs to separate:

1. operations that can fail,
2. handling of the failure,
3. successful processing,
4. mandatory finalization.

The Python implementation uses this distinction while evaluating and merging a Pull Request.

A policy failure is converted into `MergeError`. The `except` branch records the rejection. The `else` branch performs the successful merge only after eligibility evaluation completes without a merge exception.

## `finally` Semantics

`finally` is used for operations whose execution should not depend on the result of the preceding operation.

Typical examples include:

- releasing resources,
- closing files,
- restoring state,
- recording an audit event,
- ending an operation marker,
- clearing temporary state.

The project uses finalization for merge attempts and status checks.

A merge attempt can:

- succeed,
- fail because of policy,
- encounter an unexpected error.

The audit finalization must occur for all three outcomes.

This is why the finalization operation belongs in `finally`, rather than being duplicated inside every success and failure branch.

## Pull Request Lifecycle

A Pull Request represents a proposed changeset.

The Python, JavaScript, C++17, Java 17, and PostgreSQL implementations model the following lifecycle:

`source branch → commits → Pull Request → review → checks → eligibility → merge`

A Pull Request contains a source branch and target branch. Its commits define the proposed changeset. The head commit identifies the revision against which review and automated checks are evaluated.

A Pull Request may be:

- draft,
- open,
- closed,
- merged.

A draft Pull Request represents work that is visible for early collaboration but is not yet treated as ready for normal merge processing.

A Pull Request can also become stale relative to its base branch. Synchronization can invalidate existing approvals because reviewers may have approved an earlier repository state.

## Code Review

Code Review evaluates the content of the proposed changes.

The project models review decisions using states such as:

- `commented`
- `changes_requested`
- `approved`
- `dismissed`

Review comments are associated with a particular review and identify a file, line, body, and resolution state.

A review is tied to a commit revision. This matters because an approval for an earlier revision should not automatically authorize a materially changed revision.

Review quality therefore depends on both the review state and the revision being reviewed.

The implementations treat unresolved review conversations separately from approval counts. A Pull Request can have sufficient approvals while still being blocked because required discussions remain unresolved.

This prevents approval and discussion resolution from becoming the same concept.

## Approvals

An approval is a review decision with specific semantics.

The project counts an approval as active only when relevant conditions are satisfied:

- the reviewer is active,
- the review state is `approved`,
- the review is not stale,
- the review corresponds to the current Pull Request head.

This is more precise than simply counting rows whose state equals `approved`.

### Stale approvals

A Pull Request can receive new commits or become synchronized with changes from its base branch.

When the reviewed revision changes, previous approvals may no longer represent the current code.

The implementations therefore model stale approvals explicitly.

The Python, JavaScript, and Java implementations invalidate approval state during synchronization. The PostgreSQL model stores `stale` directly in the `reviews` table and uses a trigger when relevant Pull Request state changes.

### Dismissed approvals

A dismissed review is not counted as an active approval.

Dismissal and staleness are distinct:

| Condition | Meaning |
|---|---|
| Approved | Reviewer approved the reviewed revision |
| Stale | Approval belongs to an older revision |
| Dismissed | Approval was explicitly invalidated |
| Changes requested | Reviewer requires modifications |

These states should not be collapsed into a single Boolean.

## Branch Protection

Branch Protection is repository-level enforcement.

It determines which conditions must be satisfied before a Pull Request can be merged into a protected branch.

The project models policies such as:

- required approvals,
- required status checks,
- resolved conversations,
- linear history,
- direct-push restrictions,
- force-push restrictions.

Branch Protection is therefore not the same thing as review.

A reviewer may approve a Pull Request, while branch protection can still reject the merge because a required automated check failed.

Likewise, status checks may pass while the merge remains blocked because the required number of approvals has not been reached.

The final merge decision combines these independent conditions.

## Status Checks

Automated status checks represent machine-evaluated repository conditions.

The examples use checks such as:

- `tests`
- `security`

A status check is represented independently from human review.

A Pull Request is not merge-eligible merely because its tests pass. The final decision also considers approval requirements, synchronization, unresolved conversations, and branch-protection rules.

The JavaScript implementation uses asynchronous check execution and event emission. The Python implementation uses callable check functions. C++17 and Java model status checks as domain state. PostgreSQL persists them relationally.

## Python Implementation

The Python file models the workflow with dataclasses, enumerations, exceptions, collections, and explicit validation.

Important domain types include:

- `PullRequest`
- `Review`
- `StatusCheck`
- `BranchProtection`
- `Repository`

The `Repository.evaluate_merge()` method collects all failed policy conditions instead of stopping at the first failure.

The `merge()` method then uses exception handling to separate:

- eligibility evaluation,
- merge rejection,
- successful merge,
- mandatory finalization.

The `run_status_check()` function demonstrates another practical use of `finally`: status-check completion is reported even when the checker raises an exception.

Assertions at the end provide basic executable validation.

## JavaScript Implementation

The JavaScript implementation uses Node.js standard-library functionality and event-driven behavior.

`PullRequest` extends `EventEmitter` and emits events when:

- reviews are added,
- status checks change,
- synchronization occurs.

`Map` stores status checks efficiently by name, while `Set` represents protected branches and required checks.

JavaScript does not have Python-style `try/except/else` syntax. The implementation therefore expresses the successful non-exceptional path with an explicit `if` and `else` inside `try`.

The `finally` block remains native JavaScript exception-handling behavior.

Asynchronous status checks use Promises. A failed asynchronous check records a failed result and the `finally` section reports completion.

## C++17 Implementation

The C++ program treats repository governance as a domain engine.

The implementation uses:

- enums for state,
- structs for policy data,
- classes for domain objects,
- STL containers for repository state,
- exceptions for invalid operations,
- RAII for deterministic finalization.

C++17 does not provide a `finally` keyword.

The program therefore uses a scope guard implemented through RAII. Its destructor executes when the guard leaves scope, including during exception unwinding.

This provides the resource-finalization property normally associated with `finally`.

The C++ implementation also separates governance evaluation from mutation. `evaluate()` reports policy failures, while the merge operation changes Pull Request state only after the evaluation succeeds.

## Java 17 Implementation

The Java implementation uses an enterprise-oriented domain structure.

Records model immutable value objects such as:

- `Review`
- `StatusCheck`
- `BranchProtectionPolicy`

Enums represent domain states.

`MergeEligibilityService` owns policy evaluation, while `RepositoryService` owns repository-level workflow operations.

The merge operation uses `try`, `catch`, `else`-style explicit success branching, and `finally`.

Java has no native `else` clause attached to `try`, so the successful path is expressed explicitly after validation. Java does provide a native `finally` construct for mandatory finalization.

The design separates:

`domain state → policy evaluation → service workflow → audit finalization`

This is appropriate for enterprise systems where validation and policy decisions should not be buried inside presentation logic.

## PostgreSQL Implementation

The PostgreSQL implementation represents the workflow relationally.

Core tables include:

| Table | Responsibility |
|---|---|
| `repositories` | Repository identity and default branch |
| `branches` | Repository branches and protection state |
| `commits` | Repository commit identities |
| `pull_requests` | Proposed changes and lifecycle state |
| `pull_request_commits` | Changeset membership and ordering |
| `reviewers` | Reviewer identity and activity |
| `reviews` | Review decisions and stale status |
| `review_comments` | Inline review discussion |
| `status_checks` | Automated validation results |
| `branch_protection_policies` | Repository merge requirements |
| `required_status_checks` | Required automated checks |
| `merge_attempts` | Eligibility and finalization history |

The schema uses:

- primary keys,
- foreign keys,
- unique constraints,
- check constraints,
- indexes,
- enumerated types,
- triggers,
- functions,
- procedures,
- transactions.

The `merge_eligibility()` function evaluates repository policy and returns an explicit decision with a reason.

The `finalize_merge_attempt()` procedure records an attempt, evaluates eligibility, changes Pull Request state when appropriate, records failure information, and records finalization time.

PostgreSQL has no native `finally` statement. The procedure therefore uses explicit finalization SQL after the controlled exception block. The exception handler records the failure before the error is re-raised.

## Domain State Separation

The implementation deliberately separates several kinds of state.

### Proposed changes

Commits and Pull Requests describe what is being proposed.

They do not themselves constitute approval.

### Branch state

Branches have names, heads, and protection status.

Branch state determines where a Pull Request originates and where it is intended to merge.

### Review state

Reviews represent human evaluation.

Review comments provide more detailed discussion and resolution information.

### Approval state

Approval is a review decision that may satisfy a policy requirement.

Approval can become stale or dismissed.

### Automated state

Status checks represent automated validation.

They are independent from human approvals.

### Repository enforcement

Branch Protection expresses repository-level requirements.

It determines whether the Pull Request can satisfy the repository's merge rules.

### Final merge eligibility

Eligibility combines all relevant conditions.

A simplified decision model is:

`Eligibility = Open + Current Reviews + Required Approvals + Passing Checks + Resolved Conversations + Branch Policy`

`else` applies to successful processing of that decision.

`finally` applies to operations that must be finalized after the decision.

## Failure Handling

The implementations distinguish expected policy failures from unexpected programming or infrastructure failures.

Examples of expected failures include:

- source and target branches are identical,
- Pull Request is closed,
- required approval is missing,
- approval is stale,
- status check is missing,
- status check failed,
- unresolved conversations remain,
- Pull Request is not synchronized,
- merge strategy violates linear-history requirements.

These are domain failures and can be reported as policy results.

Unexpected failures are handled separately so that programming defects are not silently converted into ordinary governance decisions.

## Edge Cases

Important edge cases covered by the implementations include:

- empty changesets,
- duplicate commits,
- unknown branches,
- unknown commits,
- invalid reviewers,
- closed Pull Requests,
- stale approvals,
- missing required checks,
- failed required checks,
- unresolved review conversations,
- merge commits under a linear-history policy,
- synchronization after review,
- merge attempts that are already completed,
- malformed commit identifiers.

The database layer adds constraints so that invalid states can be rejected close to the data boundary.

## Performance Considerations

The workflow is primarily a policy-evaluation problem.

In the in-memory implementations:

- sets provide efficient branch and commit membership checks,
- maps provide direct status-check lookup,
- review scanning is proportional to the number of reviews,
- policy evaluation is proportional to the number of configured required checks and reviews.

The PostgreSQL schema indexes the columns used for common policy lookups, especially Pull Request state, review state, status-check names, and review resolution.

Indexes are not applied indiscriminately because each index adds storage and write-maintenance cost.

## Security Considerations

Repository governance is a security control as well as a development workflow.

Important controls include:

- preventing direct pushes to protected branches,
- preventing unauthorized force pushes,
- requiring independent approvals,
- invalidating stale approvals,
- requiring security checks,
- requiring resolved discussions,
- preserving audit history,
- validating repository relationships with foreign keys,
- rejecting malformed identifiers,
- avoiding trust in client-provided merge eligibility.

The merge decision should be calculated from authoritative repository state rather than from a client assertion that a Pull Request is ready.

## Practical Distinction Between `else` and `finally`

The two constructs solve different problems.

| Construct | Question it answers |
|---|---|
| `else` | Did the guarded operation complete without an exception? |
| `finally` | What must happen after the operation regardless of outcome? |

For a merge attempt:

`try: evaluate policy`

`except: record rejection`

`else: perform successful merge`

`finally: finalize audit state`

The successful merge should not occur in `finally`, because `finally` also executes after failure.

Likewise, mandatory finalization should not be placed only in `else`, because `else` is skipped when an exception occurs.

## Cross-Language Comparison

| Language | `else` after exception handling | `finally` | Project-specific mechanism |
|---|---|---|---|
| Python | Native `try/except/else` | Native | Repository workflow and status checks |
| JavaScript | No native `try/else` | Native | Explicit success branch inside `try` |
| C++17 | No native `try/else` | No native keyword | Explicit success branch and RAII scope guard |
| Java 17 | No native `try/else` | Native | Service-layer policy evaluation |
| PostgreSQL | Procedural conditional logic | No native `finally` statement | Explicit finalization after exception handling |

The implementations are deliberately not mechanical translations. Each language uses its own control-flow and state-management strengths.

## Design Principle

The main engineering principle is to assign each operation to the correct part of the control-flow structure.

Use the exception-handling block for operations that may fail.

Use the failure branch for handling exceptional conditions.

Use the successful branch for work that should occur only after normal completion.

Use finalization for state that must be recorded or cleaned up regardless of success or failure.

In repository governance, this separation prevents an important class of workflow errors: treating successful processing, policy rejection, and mandatory cleanup as if they were the same event.
