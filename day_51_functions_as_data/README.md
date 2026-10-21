# Functions as Data: Repository Governance and Merge Policies

This artifact set studies **functions as data** through a repository-development domain where behavior must be evaluated repeatedly against structured state.

The central idea is that a function can be treated as a value. It can be stored in a collection, passed into another function, selected by a policy registry, composed with other functions, and executed later. The repository domain provides a concrete setting in which this behavior is useful because Pull Requests, Code Review, Approvals, and Branch Protection require different kinds of decisions.

The four concepts have deliberately separate responsibilities:

| Area | Responsibility |
|---|---|
| Pull Requests | Propose and track a changeset from a source branch toward a target branch |
| Code Review | Evaluate the proposed changes and record comments or review decisions |
| Approvals | Represent qualified review decisions that contribute to merge eligibility |
| Branch Protection | Enforce repository-level conditions on the target branch |

A useful relationship is:

`Pull Request → Code Review → Approval Decisions → Branch Protection Evaluation → Merge Eligibility`

A function does not replace any of these concepts. Instead, functions provide a mechanism for expressing and reusing the rules that connect their state.

## Domain Model

A Pull Request contains a source branch, target branch, commits, lifecycle state, synchronization state, mergeability, reviews, status checks, and unresolved conversations.

Code Review is represented separately through review records. A review can contain inline comments and can have states such as `commented`, `approved`, `changes_requested`, or `dismissed`.

An approval is not simply the existence of a review. It is a particular review state that satisfies an approval policy. The implementations count distinct approved reviewers so that submitting multiple approvals under the same identity does not accidentally satisfy a requirement for independent reviewers.

Branch Protection describes requirements imposed on the target branch. Examples include:

- minimum number of required reviews
- required status checks
- required conversation resolution
- linear-history requirements
- restrictions on direct pushes
- restrictions on force pushes
- branch deletion restrictions
- administrator bypass policy

The distinction matters because a Pull Request can exist without being mergeable, a review can exist without being an approval, and an approval can exist without making a protected branch eligible for merging.

## Functions as Data

The Python implementation uses `Callable` values as governance rules. The `WorkflowEngine` stores rules in a dictionary:

`rule name → callable`

The engine can register a function, retrieve it by name, execute it, and determine which rules currently pass.

This allows rules such as:

- `is_mergeable`
- `has_required_reviews`
- `has_no_requested_changes`
- `required_checks_pass`
- `conversations_resolved`

to become values that can be manipulated by the application.

The `compose()` function creates another function from existing functions. The resulting callable represents a combined policy:

`all(rule₁, rule₂, rule₃, ...)`

This is a higher-order-function pattern. The policy itself becomes data that can later be executed against a Pull Request.

Python also uses functions for branch-name transformations. A list of transformations is applied sequentially, demonstrating that executable behavior can be stored alongside ordinary collection data.

The implementation intentionally does not serialize executable Python code. A production system should store trusted rule identifiers and configuration rather than accepting arbitrary source code and executing it.

## JavaScript Event and Asynchronous Model

The JavaScript implementation uses functions as first-class values in several different forms.

The `rules` object stores governance functions. The `all()` and `any()` functions are higher-order functions that return new predicate functions.

The repository also maintains event handlers. A function can be registered for an event such as `merged`, and the repository later invokes the stored handlers when the event occurs.

This is distinct from the Pull Request lifecycle itself. The event system is an execution mechanism for responding to state transitions.

Status checks demonstrate another useful property of JavaScript functions. The asynchronous `runStatusCheck()` function accepts an implementation function and executes it as a Promise-producing operation. `Promise.all()` then evaluates multiple status-check functions concurrently.

The flow is therefore:

`status-check functions → Promise results → Pull Request status data → governance predicates`

The JavaScript implementation also demonstrates function composition through `all()` and `any()`. The returned functions can be passed into other evaluators just like ordinary values.

## C++ Governance Engine

The C++ implementation treats `std::function` as the common representation for governance behavior.

The `GovernanceRule` type is:

`std::function<bool(const PullRequest&, const Repository&)>`

This permits several callable forms to participate in the same policy engine:

- ordinary functions
- lambda expressions
- other compatible function objects

The `GovernanceEngine` stores these rules in a map. Rule names identify trusted policy functions, while the function objects contain the actual executable behavior.

`allOf()` demonstrates higher-order policy construction. It accepts a collection of governance functions and returns another governance function that succeeds only when every component succeeds.

The C++ design also makes approval identity explicit with a `std::set`. This avoids counting two approvals from the same reviewer as two independent approvals.

The implementation is deliberately stricter than a simple boolean merge flag. A Pull Request must satisfy multiple independent conditions before `merge()` changes its state.

## Java Enterprise Domain Model

The Java implementation uses a dedicated `GovernanceRule` functional interface extending `BiPredicate<PullRequest, Repository>`.

This provides a strongly typed domain-level representation of a function as data.

Java records are used for immutable values such as:

- `Commit`
- `Review`
- `BranchProtection`

The mutable `PullRequest` object owns lifecycle state and provides explicit operations for submitting reviews, changing status checks, closing, reopening, synchronizing, and merging.

The `GovernancePolicy` class acts as a trusted function registry. Named rules can be registered and evaluated without exposing the individual implementations to callers.

The `all()` method constructs a composite governance function from a list of existing functions. Java's `Function<String, String>` is also used for branch-name transformations, showing that function values are useful outside boolean policy evaluation.

The enterprise-oriented design keeps policy behavior separate from domain state. This makes policy rules easier to replace, test, audit, and compose.

## Pull Request Lifecycle

The Pull Request model represents a lifecycle rather than merely a collection of commits.

A typical state flow is:

`DRAFT → OPEN → CLOSED`

or:

`DRAFT → OPEN → MERGED`

An open Pull Request can receive reviews and status checks. A closed Pull Request can be reopened. A merged Pull Request is treated as a completed state and cannot simply be converted back into an ordinary open Pull Request.

Base-branch synchronization is separate from the existence of commits. A Pull Request may contain valid commits but still be marked as requiring synchronization with the target branch.

A merge conflict therefore affects merge eligibility rather than changing the meaning of the review itself.

## Changesets and Commits

Commits describe the changeset proposed by a Pull Request.

The implementations keep commits distinct from reviews. This prevents an approval from being interpreted as a property of an individual commit and prevents a commit from implicitly becoming approved.

The SQL model uses `pull_request_commit` as a many-to-many association. This permits a repository commit to be associated with a Pull Request without embedding commit information directly inside the Pull Request record.

The Pull Request can therefore evolve as its source branch receives new commits.

## Code Review

Code Review evaluates the proposed changes.

The review model distinguishes:

- general comments
- approvals
- requested changes
- dismissed reviews

Inline comments are separate records in the SQL model and can refer to a specific commit, file path, and line number.

This allows a review discussion to be resolved independently of the review's existence.

A review with comments is not automatically an approval. A reviewer can comment without approving, or explicitly request changes.

Review quality therefore depends on the reviewer's evaluation and the scope of the review, while merge eligibility depends on the repository's formal policy.

## Approval Semantics

Approvals are represented as review decisions rather than as independent Pull Request flags.

The implementations use distinct reviewer identities when counting approvals.

For example, if a protected branch requires two approvals:

`bob → approved`

`bob → approved`

does not produce two independent approvals.

Instead:

`distinct approved reviewers = {bob}`

and the requirement remains unsatisfied.

This distinction prevents duplicate review records from artificially satisfying a governance requirement.

## Stale and Dismissed Approvals

The model recognizes that review state can become separated from the current changeset.

When a Pull Request receives new commits after a review, a production implementation may need a policy for whether previous approvals remain valid. This artifact models synchronization explicitly but does not pretend that every hosting platform has identical stale-review semantics.

Dismissal is also represented as a distinct review state. A dismissed review is not treated as an active approval.

The SQL schema records dismissal metadata so an audit trail can preserve why a review ceased to participate in the active review state.

A production policy should define exactly when approvals become stale, which changes trigger dismissal, and who can dismiss them.

## Review Discussions

Review comments and conversations are different from approval decisions.

A review comment may be resolved while the review remains part of the review history.

Branch Protection can impose a separate requirement that all conversations be resolved before merging.

This produces an important distinction:

`review decision ≠ conversation state`

A Pull Request can therefore have sufficient approvals while still being blocked by an unresolved conversation.

The governance functions evaluate these conditions independently.

## Status Checks

Status checks are another independent merge condition.

A protected branch may require:

- unit tests
- security scanning
- integration tests
- static analysis

The SQL implementation stores required checks in `protected_status_check` and actual Pull Request results in `status_check`.

The `status_checks_satisfied()` function compares the required set against the actual results.

A missing check is treated as failing. This is safer than interpreting absence as success.

## Branch Protection

Branch Protection is repository governance rather than review behavior.

The SQL `branch_protection` table contains repository-level restrictions, while `protected_status_check` stores required checks.

The model can express policies such as:

- no direct pushes
- no force pushes
- no branch deletion
- required reviews
- required conversations to be resolved
- linear-history requirements
- administrator bypass configuration

The examples do not silently treat administrator privileges as an automatic bypass. A bypass is a separate policy decision that should be explicit and auditable.

## Merge Eligibility

Merge eligibility is a composite decision.

The implementations evaluate conditions such as:

`open + not draft + mergeable + synchronized + required approvals + passing checks + resolved conversations + no requested changes`

Each condition remains a separate function.

This is preferable to a single large boolean expression when policies need to be inspected, reused, tested, or changed independently.

The C++ and Java implementations construct composite policies from individual function values. Python does the same with `compose()`, while JavaScript uses `all()` and `any()`.

## SQL Representation

PostgreSQL provides a relational representation of the same domain.

The principal relationships are:

`repository → branch → branch_protection`

`repository → pull_request → review`

`pull_request → pull_request_commit → commit`

`review → review_comment`

`pull_request → status_check`

`branch_protection → protected_status_check`

This separates durable data from executable policy.

PostgreSQL functions then evaluate that data:

- `required_reviews_satisfied()`
- `status_checks_satisfied()`
- `conversations_satisfied()`
- `no_requested_changes()`
- `pull_request_merge_eligible()`

The final function acts as a database-level composite policy.

## Transactional Merge

The SQL script uses a serializable transaction for the merge example.

The Pull Request is locked with `FOR UPDATE`, eligibility is checked, a merge event is recorded, and the Pull Request is transitioned to `merged`.

The trigger prevents the Pull Request from entering the merged state unless the corresponding merge event already exists.

This creates a database-level integrity boundary rather than depending entirely on application code.

The ordering is intentional:

`lock → evaluate → record merge event → change state → commit`

A production implementation would also need to consider concurrent status-check updates, review changes, branch updates, and retry behavior.

## Functions Versus Function Configuration

There is an important distinction between storing functions and storing configuration.

A function is executable behavior.

Configuration describes parameters used by that behavior.

For example:

`required_reviews = 2`

is configuration.

`required_reviews_satisfied(pr, repository)`

is executable behavior.

A robust governance system generally stores policy configuration as durable data while keeping executable functions inside a trusted code or database-function registry.

The artifact set follows this principle. Functions can be selected by trusted names, while arbitrary user-provided source code is never converted into executable logic.

## Failure Conditions

The examples intentionally include several failure cases:

| Failure | Result |
|---|---|
| Missing required approval | Merge blocked |
| Duplicate approval by one reviewer | Does not satisfy independent-review requirement |
| Requested changes remain active | Merge blocked |
| Required status check missing or failed | Merge blocked |
| Unresolved required conversation | Merge blocked |
| Pull Request not synchronized | Merge blocked |
| Merge conflict | Merge blocked |
| Merged Pull Request submitted for another transition | Rejected |
| Unknown policy function | Rejected |
| Invalid reviewer or branch information | Validation failure |

These failures illustrate why functions are useful as independently testable policy units.

## Performance Considerations

Function-as-data designs introduce a small amount of indirection because execution is selected through callable values rather than hard-coded control flow.

The larger performance concern in the SQL implementation is relational evaluation.

Indexes are therefore provided for common governance access patterns:

- Pull Requests by target branch and state
- reviews by Pull Request, state, and reviewer
- status checks by Pull Request and check name
- unresolved review comments

Approval counting uses distinct reviewer identities. This is necessary for correctness even though distinct aggregation can be more expensive than a simple row count.

In a high-volume repository system, cached policy evaluation or materialized governance state could be considered, provided cache invalidation remains correct.

## Security and Governance Boundaries

Functions as data can become dangerous if arbitrary executable content is accepted from untrusted users.

The implementations avoid dynamic source-code execution.

Trusted policy registries are preferable:

`policy name → trusted function`

rather than:

`user text → executable code`

Branch protection also represents a security boundary. Direct pushes, force pushes, deletion, and administrative bypass should be explicit policy decisions rather than accidental consequences of application behavior.

Audit records should preserve who performed a merge, which strategy was used, which policy was evaluated, and which approvals and checks were active at the time.

## Relationship Between the Four Governance Areas

The four areas can be understood without collapsing their responsibilities:

| Mechanism | Primary question |
|---|---|
| Pull Request | What change is being proposed, from where, and toward which branch? |
| Code Review | What did reviewers determine about the proposed change? |
| Approval | Which eligible review decisions satisfy the required approval policy? |
| Branch Protection | What repository-level conditions must hold before the target branch accepts the merge? |

Functions connect these questions without making them the same thing.

A Pull Request supplies state to review functions.

Review functions produce decisions.

Approval predicates interpret eligible review decisions.

Branch-protection predicates combine those decisions with repository-level restrictions.

The final merge decision is therefore a composition of independently meaningful functions rather than an overloaded representation of any single governance concept.
