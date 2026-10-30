# Creating Custom Exceptions in Repository Governance

## Purpose and scope

This project examines how to design, raise, propagate, catch, and report custom exceptions in software systems. Its working domain is repository governance: Pull Requests, code reviews, approval decisions, status checks, and protected branches.

The repository scenario makes exception design concrete. Operations can fail for different reasons, and those reasons require different responses. An invalid branch name requires input correction. A reviewer authorization failure requires a different reviewer. A stale approval requires a fresh review. A branch-protection violation requires the operation to use an authorized workflow. A concurrency conflict may permit a safe retry after the latest state has been retrieved.

A custom exception is a domain-specific failure type that communicates more than a generic runtime error. It identifies the failed condition, separates expected business failures from unexpected technical failures, and gives callers a stable way to select recovery behavior.

The implementations distinguish between the repository workflow and its failure model. Pull Requests provide the workflow for proposing changes. Code review evaluates the proposed changes. Approvals represent formal review decisions. Branch protection enforces repository-level conditions before a merge can modify a protected branch.

## Exception design principles

### Why custom exceptions are useful

A generic exception such as `RuntimeError`, `Error`, `std::exception`, or `SQLException` can indicate that an operation failed, but it does not necessarily identify the domain condition. Callers may be forced to inspect message text, infer the source of the failure, or treat unrelated failures identically.

A domain exception provides a stable contract:

| Exception property | Purpose |
|---|---|
| Type | Identifies the category of failure |
| Error code | Provides a stable machine-readable identifier |
| Message | Explains the failure to a developer or operator |
| Context | Identifies relevant entities, values, or state |
| Retryability | Indicates whether a retry may be reasonable |
| Cause | Preserves the underlying failure when wrapping another exception |

Messages should be informative, but application logic should normally depend on types and codes rather than exact message wording. Messages may be revised for clarity without changing the contract used by callers.

### Exception hierarchy

The implementations use a common workflow exception as the root of a domain-specific hierarchy.

| Exception type | Typical condition | Appropriate response |
|---|---|---|
| `ValidationError` | Missing title, invalid line number, malformed input | Correct the supplied data |
| `NotFoundError` | Branch or Pull Request does not exist | Retrieve a valid resource identifier |
| `InvalidTransitionError` | Attempt to merge a closed or draft Pull Request | Move the workflow into a valid state |
| `ReviewerEligibilityError` | Author attempts self-approval or an ineligible reviewer submits a review | Select an authorized reviewer |
| `ProtectionViolationError` | Unauthorized direct write or protected branch deletion | Use an authorized repository workflow |
| `MergeConflictError` | Base synchronization produces conflicting changes | Resolve conflicts before continuing |
| `MergeEligibilityError` | One or more merge requirements are unmet | Resolve each reported policy condition |
| `ConcurrencyConflictError` | The resource changes after a client reads it | Refresh state and retry only after revalidation |
| `StaleApprovalError` | A decision refers to an outdated changeset | Obtain a review of the current source commit |

The exception hierarchy avoids using one broad exception for every domain failure. A caller can catch the root type for common logging while catching a subtype for specific recovery behavior.

### Raising and catching exceptions

A well-designed custom exception is raised close to the operation that detects the invalid condition. The exception should identify the failure without silently modifying the domain state.

For example, a review-submission operation can detect that the reviewer is the Pull Request author and raise a reviewer-eligibility exception. The caller should not need to inspect the entire repository to discover why the review was rejected.

Catching should occur at a boundary that can make a meaningful decision. A command-line application may serialize the exception and return a non-zero exit status. An API layer may map it to an appropriate HTTP response. A database function may raise an application-specific SQLSTATE and allow the transaction manager to roll back the failed operation.

Unexpected programming errors should not be converted into misleading domain exceptions. Error wrapping is appropriate when an abstraction boundary needs to preserve the original cause while adding meaningful domain context.

## Repository workflow domain

The implementations use the following repository relationships:

Repository
  |
  +-- Branches
  |     |
  |     +-- Commits
  |
  +-- Pull Requests
        |
        +-- Proposed changes
        +-- Review decisions
        +-- Review comments and discussions
        +-- Automated status checks
        +-- Base-branch synchronization
        +-- Merge eligibility
        +-- Merge result

A repository contains branches. Each branch points to a commit. A Pull Request identifies a source branch and a target branch, making the proposed changes available for review and validation.

The source branch represents the proposed changeset. The target branch represents the destination. Their current commit identifiers matter because approvals and automated checks refer to particular source states. A review of an earlier commit must not automatically authorize a later, materially different changeset when the repository policy dismisses stale approvals.

### Pull Requests

The workflow model distinguishes four states:

| State | Meaning |
|---|---|
| `DRAFT` | The proposal is being prepared and is not ready for merge |
| `OPEN` | The proposal is available for review and validation |
| `CLOSED` | The proposal was closed without merging |
| `MERGED` | The proposal was integrated into its target branch |

A draft Pull Request can become open through a ready-for-review transition. An open or draft Pull Request can be closed. A closed, unmerged Pull Request can be reopened. A merged Pull Request cannot be reopened as though its changes had never been integrated.

Source and target branches must differ. A valid proposal must contain changes relative to its target. The model prevents duplicate active Pull Requests for the same branch pair.

Commits advance branch heads. When new commits are added to a source branch, earlier review decisions and status checks remain historical records, but they do not automatically apply to the new commit identifier.

Base synchronization records the target branch state against which the proposal has been updated. If synchronization produces conflicts, the proposal retains a conflict state and cannot be merged until those conflicts are resolved.

### Code review

Code review is the technical evaluation of the changeset. It is distinct from the formal approval requirement.

Reviewers inspect the proposed changes and may submit a review, add an inline comment, or participate in a discussion. The implementations represent review decisions using:

- `COMMENTED`: feedback was submitted without a formal approval or rejection.
- `APPROVED`: the reviewer accepts the reviewed changeset.
- `CHANGES_REQUESTED`: the reviewer identifies issues that should be addressed.
- `DISMISSED`: the review is no longer an active decision.

Inline comments identify a file and line. Review discussions can remain unresolved until the relevant concern has been addressed. Conversation resolution is a separate condition from the existence of an approval.

Reviewer eligibility is checked before a review is accepted. The author cannot approve their own proposal. Repository membership and reviewer role determine whether a person can participate in formal review.

A useful review process also considers scope and quality. A review should relate to the actual proposed changes, identify meaningful defects or risks, and avoid treating unrelated files as part of the same approval decision.

### Approvals

An approval is a formal review decision associated with a particular source commit and reviewer. It is not the same as a general comment, a successful status check, or permission to modify the repository.

The approval evaluation counts distinct reviewers rather than counting every historical approval. The latest decision by a reviewer supersedes that reviewer's earlier decision. Dismissed reviews do not satisfy the approval requirement.

When stale-review dismissal is enabled, an approval applies only when its recorded source commit matches the current source branch head. A new commit can therefore make an earlier approval ineffective. The proposal must receive a fresh approval for the current changeset.

The implementations support a configurable minimum approval count. The SQL model also supports role-specific approval requirements, such as requiring at least one maintainer approval. This separates the number of approvals from the organizational role expected to provide them.

A `CHANGES_REQUESTED` decision is treated as a blocking review condition while it remains the latest applicable review decision. A later review can replace the earlier decision after the changes have been addressed.

### Branch protection

Branch protection is a repository-level enforcement mechanism. It does not perform code review and does not itself create approval decisions. It determines whether repository conditions are satisfied before a protected branch can be changed.

The policy model covers:

| Protection control | Governance effect |
|---|---|
| Required approvals | Enforces a minimum number of valid approvals |
| Required status checks | Requires automated checks to succeed against the current source commit |
| Direct-push restriction | Prevents ordinary direct updates to a protected branch |
| Force-push restriction | Prevents history-rewriting updates |
| Deletion restriction | Prevents deletion of protected branches |
| Conversation resolution | Blocks merging while review threads remain unresolved |
| Linear history | Prevents merge strategies that introduce non-linear history |
| Merge strategy restrictions | Limits the permitted merge operations |
| Administrator enforcement | Determines whether administrators remain subject to policy |
| Bypass policy | Allows explicitly authorized exceptions where repository policy permits them |

The model uses squash and rebase strategies under a linear-history policy. A traditional merge commit is rejected when linear history is mandatory.

Bypass is explicit. A bypass actor must be authorized by the policy, and the configuration must permit bypass. When administrator enforcement is enabled, administrator status alone does not remove the requirements.

## Python implementation

The Python script is an in-memory repository workflow simulator.

### Domain structures

The implementation uses dataclasses for commits, branches, Pull Requests, reviews, comments, status checks, and branch protection policies. Enums represent workflow states, review decisions, check results, and merge strategies.

The `Repository` class owns the repository state and provides methods for creating branches, committing changes, opening Pull Requests, requesting reviews, submitting review decisions, recording comments, resolving discussions, updating status checks, synchronizing the target branch, and merging.

The `PullRequest` object stores its source and target branch names, base commit observed during synchronization, current state, version, reviews, comments, and checks.

Status checks are indexed by both check name and commit identifier. This prevents a successful check on an earlier commit from satisfying the requirement for a later source head.

### Exception mechanisms

`WorkflowError` is the root exception. It stores a stable code, a message, structured context, and a retryability flag. Its `to_dict()` method converts the error into a serialization-friendly structure.

Specific subclasses identify validation failures, missing resources, invalid state transitions, reviewer authorization failures, branch-protection violations, conflicts, unresolved merge eligibility, stale approvals, and concurrency conflicts.

The exception context allows the application to record relevant identifiers without parsing the message. For example, a concurrency error carries the expected and actual Pull Request versions.

The demonstration catches exceptions at the operation boundary. A direct write to the protected `main` branch produces a protection-specific exception. A self-review attempt produces a reviewer-eligibility exception. A merge attempt after a new source commit produces a merge-eligibility exception because the previous approval is no longer current.

### Concurrency and validation

The optional `expected_version` parameter in the merge operation implements optimistic concurrency control. The caller can provide the version it previously inspected. A mismatch indicates that the Pull Request changed before the merge was attempted.

This is an in-memory model rather than a distributed locking implementation. A production service would also need transactional persistence and an atomic compare-and-update operation.

The script uses only the Python standard library. Its assertions are represented through explicit domain checks and exceptions, making failure conditions visible to the caller.

## JavaScript implementation

The JavaScript file complements the Python simulator through event-driven behavior and asynchronous status-check execution.

### Event-driven workflow

The `Repository` class extends Node.js `EventEmitter`. It emits events when branches are created or deleted, commits are pushed, reviews are requested or submitted, discussions are created or resolved, checks are updated, and Pull Requests are closed or merged.

Event emission separates workflow state changes from audit consumers. A logging component can listen to events without becoming part of the core repository decision logic.

The implementation uses `Map` for branches and Pull Requests, `Set` for eligible reviewers and policy requirements, and immutable objects for individual commit and review records.

### Asynchronous status checks

The `runChecks()` method runs independent check functions concurrently through `Promise.allSettled()`. It records each result even when another check fails.

A fulfilled check is translated into a successful or failed status according to its result. A rejected promise is recorded as a failed check with its error detail. The caller receives the outcomes separately, allowing a reporting layer to distinguish test failures from execution failures.

Each recorded check is tied to the source commit identifier captured when the check run began. This is important because an asynchronous check must not accidentally certify a later commit that it did not test.

### Exception propagation

Custom error classes extend the common `WorkflowError` class. Each error supplies a stable code and structured context. The `toJSON()` method supports consistent logging and API response construction.

The main function catches domain exceptions separately from unexpected errors. Domain errors are serialized with their codes and context. Unexpected failures are reported through a separate path rather than being disguised as normal workflow rejections.

The model includes event notifications, asynchronous check execution, current-head review validation, base synchronization, merge policy evaluation, and optimistic version checks.

## C++17 implementation

The C++ program presents repository governance as a strongly typed merge-eligibility engine.

### Typed domain representation

Enums represent Pull Request state, review decision, check state, and merge strategy. Structs represent commits, branches, reviews, status checks, discussions, protection policy, Pull Requests, and eligibility results.

The engine uses STL containers:

| Container | Use |
|---|---|
| `std::map` | Branches, Pull Requests, and check records |
| `std::set` | Eligible reviewers, required checks, and allowed strategies |
| `std::vector` | Reviews, discussions, and eligibility reasons |
| `std::pair` | Composite check keys containing a name and commit identifier |

The `RepositoryGovernanceEngine` centralizes state access and validation. Private lookup methods raise a resource-not-found exception rather than returning an invalid reference or requiring callers to interpret an empty result.

### Exception hierarchy

`WorkflowError` derives from `std::runtime_error` and provides a stable error code and retryability flag. Domain-specific subclasses preserve the type information needed for targeted exception handling.

`MergeEligibilityError` carries a vector of policy reasons. The caller can report each blocking condition without parsing a combined message.

The main function demonstrates nested exception handling. A protection failure is handled separately from reviewer eligibility and merge eligibility failures. A final catch for `WorkflowError` handles other expected domain failures, while `std::exception` provides a fallback for unexpected standard-library failures.

### Governance evaluation

The `evaluate()` method inspects the current source and target branch heads, Pull Request state, merge strategy, review decisions, current approvals, status checks, conflict state, and unresolved discussions.

The latest review from each reviewer supersedes earlier decisions. Stale approvals are ignored when the protection policy requires current-head reviews.

The merge operation evaluates policy before advancing the target branch. It also accepts an optional expected Pull Request version to detect stale client state.

The implementation does not use an external repository hosting service. Its commit identifiers are local identifiers created by the program. A production system would use persistent commit objects and transactionally update the branch reference.

## Java 17 implementation

The Java program emphasizes enterprise domain modeling, immutable policy configuration, explicit state transitions, and separation between workflow aggregates and policy evaluation.

### Domain types

The implementation uses Java records for `CommitRef`, `ReviewRecord`, `StatusCheck`, `ReviewDiscussion`, `BranchProtectionPolicy`, and `EligibilityResult`.

Records reduce mutable state in domain values. For example, a review record captures the reviewer, decision, source commit, target commit, and review body at submission time. It does not silently change when a branch advances.

`PullRequestAggregate` owns mutable workflow state. It enforces valid transitions such as marking a draft ready, closing an open proposal, and reopening a closed proposal.

The aggregate returns immutable copies of its review, discussion, and check collections. External callers cannot directly modify the internal lists and maps.

### Policy objects and services

The `MergePolicy` interface defines a policy evaluation contract. `StandardMergePolicy` implements the required approval, check, synchronization, conversation, conflict, and history rules.

`GovernanceService` coordinates branch access, Pull Request creation, review authorization, check recording, discussion resolution, and merge execution.

This separation means that a different policy implementation can be supplied without rewriting the Pull Request aggregate. The aggregate controls state transitions; the policy object evaluates whether a proposed merge is permitted.

### Exception and state management

The Java exception hierarchy extends `RuntimeException` through `WorkflowException`. It stores an error code, retryability flag, and immutable context map.

The implementation distinguishes exceptions for validation, missing resources, invalid transitions, reviewer eligibility, protected branches, conflicts, merge eligibility, and concurrent modification.

The policy is immutable. A policy change requires constructing a replacement policy object rather than mutating its requirements through an exposed collection.

The version check in the service detects stale client state before merge execution. In a persistent application, this check should be paired with a database transaction or an atomic update condition to eliminate the gap between validation and commit.

## PostgreSQL implementation

The PostgreSQL script implements a relational repository-governance model and uses PostgreSQL custom SQLSTATE values to represent domain exceptions.

### Relational model

The `repo_lab` schema contains the following principal tables:

| Table | Responsibility |
|---|---|
| `repository` | Repository identity and creation metadata |
| `repository_member` | Membership and governance roles |
| `commit_object` | Commit identities and parent relationships |
| `branch` | Branch heads and deletion state |
| `pull_request` | Proposed source-to-target changes |
| `review` | Reviewer decisions tied to commit identifiers |
| `review_comment` | Inline comments and review conversations |
| `status_check` | Automated check outcomes for specific commits |
| `branch_protection` | Target-branch governance configuration |
| `required_status_check` | Checks required by a protected branch |
| `approval_requirement` | Role-specific approval requirements |

Primary keys, foreign keys, unique constraints, and check constraints enforce data integrity. The indexes support common access patterns, particularly Pull Request state retrieval, latest review lookup, unresolved conversation filtering, and status-check lookup by commit.

The schema records reviews and status checks historically. It does not overwrite an earlier review when a reviewer submits a new decision. The eligibility function selects each reviewer's latest decision.

### Custom SQL exceptions

PostgreSQL does not provide application-defined exception classes in the same way as Python, JavaScript, C++, or Java. Instead, PL/pgSQL functions can raise exceptions with application-specific five-character SQLSTATE codes.

The script uses the following convention:

| SQLSTATE | Domain meaning |
|---|---|
| `P2001` | Validation failure |
| `P2002` | Resource not found |
| `P2003` | Invalid workflow transition |
| `P2004` | Reviewer authorization failure |
| `P2005` | Branch-protection violation |
| `P2006` | Merge eligibility failure |
| `P2007` | Merge conflict |
| `P2008` | Stale or concurrent workflow state |

The `RAISE EXCEPTION USING` form supports a message, detail, and hint. This gives database callers structured diagnostic information while retaining PostgreSQL transaction behavior.

Applications can inspect the returned SQLSTATE rather than matching exception messages. The database exception can then be mapped to the corresponding application exception type.

### Triggers and functions

The branch-update trigger rejects direct changes to protected branch heads. The governed merge function sets a transaction-local control flag before updating the target branch. This makes the approved merge path distinct from an ordinary branch update.

The review trigger prevents authors from reviewing their own Pull Requests. It also validates reviewer role and rejects a review that refers to a stale source commit.

The main functions implement Pull Request creation, review submission, status-check recording, base synchronization, eligibility evaluation, merging, closing, and reopening.

`evaluate_merge_eligibility()` returns an eligibility result, a collection of reasons, and the number of valid approvals. It evaluates the current source commit rather than treating historical approvals and checks as automatically valid.

`merge_pull_request()` locks the Pull Request and target branch, evaluates policy, creates a merge commit record, advances the protected branch through the controlled trigger path, and marks the Pull Request as merged. A raised exception causes the current transaction to roll back.

### Transactional behavior

The sample workflow uses PL/pgSQL exception blocks to catch expected domain failures without terminating the complete script.

A caught exception inside a nested block rolls back the failed block's database changes while allowing the outer transaction to continue. This is useful for testing expected failure paths, but production applications should define transaction boundaries deliberately.

The SQL functions use row locks during important workflow operations. Pull Request number allocation uses a transaction-level advisory lock for the repository. These mechanisms reduce races between concurrent operations.

## Error handling across the implementations

The same domain failure is represented differently according to the capabilities of each language.

| Concern | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Root failure type | `WorkflowError` | `WorkflowError` | `WorkflowError` | `WorkflowException` | SQLSTATE convention |
| Specialized failures | Subclasses | Subclasses | Derived exception classes | Derived exception classes | Application-specific SQLSTATE |
| Structured context | Dictionary | Object | Typed fields and reason collections | Immutable map | `DETAIL` and `HINT` |
| Async failure handling | Not required by simulator | Promises and `allSettled` | Synchronous | Synchronous | Transaction and exception blocks |
| Retry indication | Boolean property | Boolean property | Boolean property | Boolean property | Application mapping |
| State protection | Repository methods | Repository methods | Governance engine | Aggregate and service | Constraints and triggers |
| Policy evaluation | Repository method | Repository method | Eligibility engine | Policy interface | PL/pgSQL function |

The language implementations share domain terminology but use different mechanisms. Python emphasizes dataclasses and an inspectable exception hierarchy. JavaScript emphasizes asynchronous execution and events. C++ uses explicit types and standard exception inheritance. Java uses immutable records, aggregate boundaries, and policy interfaces. PostgreSQL uses SQLSTATE values, constraints, triggers, row locks, and transactional functions.

## Failure scenarios and recovery behavior

### Invalid input

An empty Pull Request title or invalid comment location should be rejected before the operation changes repository state. The caller should correct the input rather than retry the same request.

### Invalid workflow transition

A draft Pull Request must be marked ready before it can be merged. A merged Pull Request cannot be reopened through the closed-Pull-Request transition. The caller must select an operation valid for the current state.

### Reviewer authorization failure

An author cannot approve their own changes. An inactive member or an ineligible repository role cannot submit a formal review. The operation should be rejected without creating an approval record.

### Stale review

A review records the source commit that the reviewer inspected. If the source branch advances, the old approval may no longer satisfy the policy. A fresh review is required when stale-review dismissal is enabled.

### Failed status check

A required check must succeed against the current source commit. A successful test run tied to an older commit does not certify the newest changeset.

### Unresolved discussion

A formal approval does not automatically resolve every inline discussion. When conversation resolution is mandatory, each review thread must be resolved independently.

### Branch-protection violation

A direct write to a protected branch must not bypass the repository's merge process. A controlled merge operation evaluates the applicable requirements before advancing the target branch.

### Merge conflict

A source branch may no longer apply cleanly after the target branch advances. The conflict state must be resolved before merge eligibility can become true.

### Concurrent modification

A client may inspect a Pull Request and attempt to merge it after another operation has changed its version. The merge operation should detect the mismatch and request a fresh evaluation.

Retryability is not a guarantee that repeating an operation will succeed. A retry is appropriate only after the caller has refreshed the resource and verified that the requested operation remains valid.

## Security and operational considerations

Custom exceptions are part of the application's security and reliability boundary. Error messages should communicate enough information to diagnose a failure without exposing secrets, access tokens, private repository content, or sensitive configuration.

Structured context should contain only information needed for diagnosis. API clients should not receive internal stack traces or database details by default.

Repository authorization and branch protection must be enforced at the server or database boundary. A client-side interface that hides an unauthorized operation is not a security control.

The examples use in-memory repository state in the programming-language implementations. They demonstrate workflow and exception behavior, but they do not provide distributed persistence, multi-process locking, or authentication. The PostgreSQL implementation provides persistent relational structures and transaction-based enforcement, but a production deployment would also require database roles, least-privilege grants, controlled function execution, audit retention, and secure connection configuration.

The exception taxonomy should remain stable enough for callers to depend on its codes and types. Error messages can evolve, but changing an error code or its meaning can break API clients, monitoring rules, and automated recovery logic.

## Execution and expected behavior

| Deliverable | Runtime | Execution |
|---|---|---|
| Python | Python 3.10 or later | Run the script directly |
| JavaScript | Node.js 18 or later | Run as a Node.js file |
| C++17 | C++ compiler with C++17 support | Compile and run the program |
| Java 17 | Java 17 or later | Compile `Main.java` and run `Main` |
| PostgreSQL | PostgreSQL 15 or later | Execute the SQL script in a database session |

The programming-language examples create a repository, prepare a feature branch, open a Pull Request, collect review decisions, resolve a discussion, record successful checks, evaluate merge eligibility, and perform a squash merge.

They then exercise expected failures, including direct writes to a protected branch, self-review, and a stale approval after a source commit changes.

The PostgreSQL script creates a separate `repo_lab` schema, builds the relational model, inserts sample repository data, creates a valid Pull Request workflow, merges an eligible proposal, and catches expected validation and policy exceptions. It begins by dropping an existing `repo_lab` schema, so it should be executed only in a database where replacing that schema is acceptable.

## Technical limitations

The programming-language implementations are educational in-memory models. They do not implement a distributed Git server, real Git object storage, network authentication, webhook delivery, or a complete repository-hosting API.

The SQL model stores commit references and parent relationships but does not implement Git tree objects, blob storage, content-based merge algorithms, or actual source-code conflict detection. Conflict state is represented explicitly so the governance workflow can enforce it.

The examples also simplify reviewer teams and authorization. Real organizations may apply team ownership, path-based review requirements, multiple approval groups, CODEOWNERS rules, signed commits, deployment gates, policy versioning, and organization-wide restrictions.

These limitations do not change the central exception-design principles: detect failures at the correct boundary, represent domain conditions with specific types or codes, preserve useful context, prevent invalid state transitions, and make recovery behavior explicit.```
