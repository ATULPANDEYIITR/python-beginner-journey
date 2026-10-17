# Variable Scope: Lexical Bindings, Closures, and State Isolation

## Scope and technical motivation

Variable scope defines where a name can be accessed and which binding an expression refers to. It is a fundamental part of program correctness because functions, nested blocks, callbacks, and services frequently operate on names that share spelling but refer to different values.

The implementations use repository development as a practical setting. A pull request has its own review state, reviewers have individual decisions, and repository policies govern whether a change may be merged. These values must remain distinguishable even when several functions process the same request.

The examples distinguish variable scope from repository governance itself. Scope determines how a program accesses its state. Pull request workflows, code review decisions, approvals, and branch protection provide the domain in which that state is represented and evaluated.

## Lexical scope and name resolution

Lexical scope is determined by the structure of the source code. A name introduced inside a function is generally accessible only within that function and its nested functions. Nested functions can usually read bindings in enclosing scopes.

A typical lookup proceeds through the relevant local scope, enclosing function scopes, the module or global scope, and the language's built-in namespace where applicable. The exact rules differ between languages.

### Local bindings and shadowing

Shadowing occurs when an inner scope introduces a name already used by an outer scope. References inside the inner scope resolve to the inner binding, while references outside it continue to resolve to the outer binding.

This is useful when a function needs a temporary policy value or a review-specific decision. It can also make code difficult to understand when unrelated meanings share a name. Descriptive names such as `repositoryPolicy`, `reviewDecision`, and `currentCommit` reduce that risk.

Scope is not the same as object identity. Two bindings may refer to the same mutable object. Mutating the object through one binding can be visible through another binding even when neither binding is reassigned.

## Python implementation

The Python program demonstrates module-level names, function-local assignments, shadowing, `global`, `nonlocal`, closures, comprehension scope, exception-target cleanup, and the distinction between mutation and rebinding.

Python determines local variables by examining assignments within a function. An assignment to a name normally makes that name local throughout the function unless a `global` or `nonlocal` declaration changes the rule. Consequently, reading the name before its local assignment can raise `UnboundLocalError`.

The nested function in `closure_counter` retains a reference to an enclosing binding after the outer function returns. Its `nonlocal` declaration allows it to rebind that enclosing variable instead of creating a new local binding.

The two loop-closure examples expose a common error. Functions created with a loop variable can all observe the final value when they execute later. A default argument captures the value at function creation and avoids that particular late-binding behavior.

The repository-policy closure retains a settings object and checks a branch against the protected branch name. The merge evaluator uses local collections to identify missing checks, failed checks, insufficient distinct approvals, and unresolved review conversations. Each invocation creates its own failure list, preventing one evaluation's findings from leaking into another.

Python dictionaries and lists are mutable objects. Assigning a new list to a local variable does not replace the caller's binding, while appending to a shared list changes the object visible through every reference to it.

The example is a teaching model rather than a complete Git hosting implementation. Its approval evaluator uses supplied reviewer identities and check results; it does not contact a repository provider or independently verify commit ancestry.

## JavaScript implementation

JavaScript uses lexical environments and distinguishes `var`, `let`, and `const`.

- `var` is function-scoped, or global-scoped in certain script contexts. It is not confined to the block in which it appears.
- `let` introduces a block-scoped binding that can be reassigned.
- `const` introduces a block-scoped binding that cannot be reassigned after initialization. If the value is an object, its properties may still be mutable.

A `let` or `const` binding cannot be accessed before initialization. The temporal dead zone is the period between entering the binding's scope and executing its initialization. This differs from the behavior of a hoisted `var` binding, which initially evaluates to `undefined`.

The closure examples compare `var` and `let` in loops. With `var`, callbacks share one function-scoped binding. With `let`, each loop iteration has its own binding, allowing callbacks to retain the expected iteration value.

`createCounter` and `createReviewSession` demonstrate encapsulation through closures. Internal state is accessible only through returned methods. The review session validates state transitions and inline comment data before modifying its private variables.

The policy evaluator creates a local failure collection and a `Set` of distinct reviewers. It excludes the pull request author, checks required status results, detects stale approvals, and enforces conversation-resolution requirements. Its immutable policy object prevents accidental replacement of policy properties, although `Object.freeze` is shallow unless nested objects are frozen separately.

The asynchronous evidence loader uses `async` and `await`. The local `evidence` binding remains available in the calling function after the awaited operation completes. A rejected operation is converted into a structured error result, illustrating how asynchronous failures can be handled without introducing shared global error state.

## C++ case study: Repository governance engine

The C++ program models a repository where changes targeting `main` require independent approvals, successful checks, resolved conversations, and verified linear history.

### Domain model

`PullRequest` stores its author, source and target branches, commits, reviews, status-check results, and lifecycle flags. `Review` associates a reviewer and review decision with the commit that was examined. `BranchProtection` contains the repository-level merge requirements.

The implementation uses `vector` for ordered review and commit data, `set` for distinct reviewer identities and required checks, and `map` for named status-check results. These data structures express different domain properties instead of using a single undifferentiated collection.

### Merge eligibility

`GovernanceEngine::evaluate` collects failure reasons without mutating the request. It rejects closed or merged requests, drafts, missing metadata, incorrect target branches, insufficient approvals, failed or missing checks, unresolved conversations, and unverified linear history.

Approvals are counted by distinct eligible reviewer identity. The author cannot supply an independent approval. A later review decision by the same reviewer replaces the earlier decision for the purpose of this simplified model. Stale approvals invalidate the current approval set when the configured policy requires dismissal.

The merge operation evaluates the request immediately before changing its state. This demonstrates the separation between deciding whether a transition is permitted and performing the transition.

### Protected operations and limitations

The engine separately evaluates direct pushes, force pushes, and branch deletion. These are repository-level controls, not review decisions. An administrator bypass is available only when the policy explicitly allows it.

The case study uses a Boolean status result for linear history rather than implementing a full commit graph. It also does not provide synchronization, persistent storage, authenticated identities, or atomic operations across multiple processes. A production service would need concurrency control and a trusted source for review and check evidence.

For a set of \(V\) reviewers and \(C\) required checks, this evaluator performs work proportional to the number of reviews and checks, excluding the cost of string operations and container details. Ordered or hashed structures may be chosen according to repository size and lookup patterns.

## Java implementation: Enterprise domain model

The Java program models pull request lifecycle state, review state, commit evidence, branch protection, and merge eligibility using explicit domain types.

`PullRequestState` separates draft, open, closed, and merged requests. `ReviewState` expresses the reviewer's decision independently of the request lifecycle. A review can be approved while the pull request still cannot be merged.

The `Review` class validates reviewer identity and inline comment fields. Its transition method rejects unsupported transitions rather than silently overwriting state. Comment collections are exposed as immutable copies, preventing callers from changing internal storage without validation.

The `PullRequest` class validates identifying fields, stores commits and checks, and tracks stale approvals. Adding a commit marks approvals stale because the previously reviewed changeset may no longer match the current request. Closing and reopening are explicit state transitions.

`BranchProtection` represents repository-level rules as an immutable record. Its required-check set is copied at construction, avoiding accidental mutation through a caller-owned set.

`MergeEligibilityService` evaluates the current request state, target branch, commit presence, distinct approvals, required status checks, stale approval policy, resolved conversations, and linear-history evidence. It returns a `MergeDecision` containing both the result and its blocking reasons. The merge method throws an exception if the request is ineligible.

The program also demonstrates the difference between request-level restrictions and repository permissions. Direct pushes, force pushes, and deletion are evaluated separately, with administrator bypass controlled by policy.

The model deliberately makes the relevant state transitions explicit. A production implementation would also verify that each approval references the current head commit, authenticate reviewer permissions, handle dismissed reviews and team membership, persist state transactionally, and protect against concurrent changes between eligibility evaluation and merge.

## PostgreSQL data model

The SQL implementation represents repository governance as related tables rather than embedding every property in one record.

| Table | Purpose |
|---|---|
| `repositories` | Identifies repositories and their default branches. |
| `branches` | Associates branch names and commit heads with repositories. |
| `pull_requests` | Stores request ownership, source and target branches, lifecycle state, and commit references. |
| `pull_request_commits` | Records the ordered commits associated with a request. |
| `reviewers` | Stores reviewer identities and eligibility flags. |
| `reviews` | Preserves review decisions and the commit each decision examined. |
| `review_comments` | Stores inline discussions and their resolution status. |
| `status_checks` | Records named check outcomes for particular commits. |
| `branch_protection` | Stores protected-branch governance requirements. |
| `required_status_checks` | Associates a protection policy with its required check names. |
| `pull_request_metadata` | Tracks stale approvals, conversation status, and linear-history verification. |

Foreign keys preserve relationships between requests, branches, reviewers, reviews, and comments. Check constraints reject invalid line numbers, unsupported check states, negative approval thresholds, and inconsistent merged-state metadata. Unique constraints prevent duplicate branch names within a repository and duplicate positions within a request's commit sequence.

Indexes support common retrieval patterns. The partial index on open pull requests avoids indexing closed and merged requests for the active-request query. The latest-review index supports retrieval of recent reviewer decisions. The partial unresolved-comment index focuses on unresolved discussions.

### Merge eligibility view

The `merge_eligibility` view derives current approval counts and check failures from stored evidence.

A `DISTINCT ON` query selects the most recent review for each reviewer and request. Approval counting excludes the author, inactive reviewers, reviewers without approval permission, and reviews tied to a different head commit. This avoids treating multiple historical approvals from one reviewer as multiple independent approvals.

The check evaluation requires a successful result for the current head commit. A successful result from an older commit does not establish that the current changeset passed. The view also evaluates the protection policy's stale-approval, conversation-resolution, and linear-history requirements.

A view provides a consistent query interface, but it does not by itself make a later merge atomic. A production merge transaction must lock or otherwise protect the relevant request, branch head, policy, reviews, and check records so that the state cannot change between validation and the merge.

The transaction at the end of the script groups schema creation, sample data, and demonstrations into one database transaction. The constraint demonstration catches an invalid comment insertion inside a nested exception block, allowing the remaining script to proceed.

## How the concepts relate without being interchangeable

Variable scope, pull request workflow, code review, approvals, and branch protection operate at different levels.

**Variable scope** determines which program binding a name refers to. It prevents review state, policy state, and temporary evaluation results from being confused by accidental shadowing or shared mutable variables.

**Pull requests** represent proposed changes from a source branch to a target branch. Their lifecycle includes drafting, opening, synchronization with the base branch, handling conflicts, closing, reopening, and merging. A request's changeset can change as new commits arrive.

**Code review** evaluates the actual changeset. Reviewers may leave inline comments, discuss design decisions, request changes, or submit a review state. Resolving a discussion is distinct from granting approval.

**Approvals** are review decisions with specific eligibility and freshness requirements. A policy may require multiple distinct reviewers, prohibit self-approval, or invalidate approvals when new commits make the previous review stale.

**Branch protection** enforces repository-level conditions. It can require reviews and status checks, prohibit direct pushes, restrict force pushes and deletion, require resolved conversations, and enforce linear history. Administrator bypass behavior depends on the repository's configured rules and platform semantics.

A pull request can therefore have completed review discussions and still lack enough approvals. It can have enough approvals and still fail a required security check. Both conditions can be satisfied while a stale approval or unresolved discussion continues to block the merge.

## Edge cases and correctness considerations

- **Shadowing:** A local name can hide an outer binding. In complex policy code, use distinct names for request state, repository policy, and individual review decisions.
- **Mutable shared state:** A closure can retain a mutable object. Encapsulation and defensive copies reduce accidental modifications by unrelated callers.
- **Late-bound callbacks:** JavaScript callbacks and Python closures may observe a variable's later value rather than the value expected when the callback was created.
- **Stale review evidence:** An approval applies to the changeset that was reviewed. New commits may require renewed review and fresh status checks.
- **Reviewer identity:** Multiple reviews by one person must not satisfy a requirement for multiple distinct reviewers. Self-approval must be excluded when the policy prohibits it.
- **Missing status checks:** A required check that has not run is not equivalent to a successful check.
- **Invalid state transitions:** Closing a merged request or approving a dismissed review without a valid workflow transition should be rejected.
- **Concurrent updates:** A request can change after eligibility is evaluated. Validation and merging must be coordinated atomically in a real repository service.
- **Privilege bypass:** Administrator privileges should not be treated as an implicit universal exception. Bypass behavior must be explicit, auditable, and consistent with repository policy.

## Performance and production considerations

Local lexical lookups are generally inexpensive, but closure design affects object lifetime and memory retention. A closure that retains a large object graph can keep data alive longer than intended. Capturing only the state a function needs can reduce accidental retention.

Repository governance evaluation is dominated by the number of reviews, required checks, and discussion records examined. Indexed lookup by request, reviewer, check name, and commit identifier reduces unnecessary scanning. Database queries should use the current head commit as part of the check and review validation.

Policy evaluation must distinguish an absent value from an explicit negative result. A missing status check is different from a failed check, and an absent approval is different from a dismissed approval. Explicit states and structured failure reasons make these differences observable.

Persistent repository services should use authenticated identities, transactional updates, immutable audit events, and server-side permission checks. Client-side or in-memory eligibility calculations can explain a decision but cannot independently enforce repository security.

The examples provide executable models of these mechanisms. They intentionally omit provider-specific API behavior, distributed locking, signed commit verification, full merge-conflict resolution, and production authentication because those mechanisms require infrastructure beyond lexical scope and the local governance models.
