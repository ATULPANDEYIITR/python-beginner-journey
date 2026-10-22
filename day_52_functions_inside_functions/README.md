# Functions Inside Functions: Repository Governance

## Scope

This project studies **functions inside functions** through a concrete repository-development scenario involving Pull Requests, Code Review, Approvals, and Branch Protection.

The four concepts have separate responsibilities:

| Area | Responsibility |
|---|---|
| Pull Request | Provides the workflow for proposing a changeset from a source branch toward a target branch |
| Code Review | Evaluates the technical changes through reviews, comments, discussions, and requested changes |
| Approvals | Records review decisions that can satisfy an approval requirement when the reviewer and commit are eligible |
| Branch Protection | Enforces repository-level conditions that must be satisfied before a protected branch can receive a merge |

The central programming concept is that an outer function can define an inner function and return it, call it, or use it as a specialized operation. The inner function can retain access to variables from the enclosing function. This behavior is particularly useful when a repository policy must be configured once and evaluated repeatedly.

The implementations deliberately keep repository workflow behavior separate from review decisions and from branch-level enforcement.

## Core Concept: Functions Inside Functions

A nested function is a function whose definition occurs inside another function.

The relationship can be represented as:

`outer function → local state → inner function → retained state → specialized behavior`

For example, a policy factory can receive a protected branch and its rules, then return a validator specialized for those rules.

The important property is **lexical scoping**. The inner function can access variables defined in its enclosing scope even after the outer function has returned. Such retained state is commonly described as a **closure**.

In this project, the pattern is used for repository governance rather than as an isolated language feature.

A policy-producing function can retain:

- the protected branch name
- the required approval count
- required status checks
- conversation-resolution requirements
- history requirements

The resulting validator can then evaluate many Pull Requests against the same policy.

## Pull Request Workflow

A Pull Request connects a source branch with a target branch.

The implementation models the important lifecycle states:

`draft → open → closed`

or:

`draft → open → merged`

A Pull Request contains a changeset represented by commits. Reviewers can be requested, status checks can report their results, and discussions can remain unresolved.

Base-branch synchronization matters because review decisions can become invalid when the Pull Request receives a new commit. The implementations therefore associate approval decisions with a specific commit rather than treating an approval as permanently valid.

A simplified workflow is:

`source branch`
→ `commits`
→ `Pull Request`
→ `review`
→ `status checks`
→ `approval`
→ `branch-policy evaluation`
→ `merge`

A Pull Request can also be reopened after closure. The Python implementation explicitly models reopening, while the other implementations concentrate on merge eligibility and policy evaluation.

## Code Review

Code Review is concerned with evaluating the changes, not with defining repository-wide merge restrictions.

The review model distinguishes:

- comments
- requested changes
- approvals
- dismissed reviews
- review discussions
- the commit to which a review applies

The implementations use a review state rather than treating every reviewer interaction as an approval.

A reviewer who identifies a problem can request changes. A reviewer who finds the changes acceptable can approve. A dismissed approval is not treated as a valid approval for merge eligibility.

Review scope also matters. A review is associated with a particular Pull Request and commit. This prevents an approval on an earlier changeset from silently authorizing a later, unreviewed changeset.

## Approvals

An approval is a review decision with a specific governance meaning.

The project does not count every review as an approval. A valid approval must satisfy the applicable rules.

The C++ and Java implementations require the reviewer to be eligible and the approval to apply to the latest commit.

The Python implementation expresses the same rule through a nested helper function:

`count_valid_approvals(pr)`

That helper reads the latest commit and counts unique eligible reviewers whose approval applies to that commit.

This distinction is important because two approvals on commit `A` do not automatically represent two approvals for commit `B`.

A simplified state transition is:

`commit A → two approvals → new commit B → approvals stale → fresh reviews → merge eligible`

This behavior models a common review-policy principle: a material changeset update can invalidate previous review decisions.

## Branch Protection

Branch Protection operates at repository governance level.

A protected branch can require:

- a minimum number of approvals
- successful status checks
- resolved conversations
- linear history
- restrictions against direct pushes
- restrictions against force pushes
- restrictions against branch deletion

Branch Protection does not itself perform the technical review. It establishes conditions that must be satisfied before a merge is accepted.

The relationship is therefore:

`Pull Request proposes`

`Code Review evaluates`

`Approval records a decision`

`Branch Protection enforces merge conditions`

This separation prevents the four concepts from being treated as synonyms.

## Python Implementation

The Python program models a repository workflow with `dataclass` domain objects and enumerations.

The principal objects are:

- `Commit`
- `Review`
- `PullRequest`
- `BranchProtection`

The most important nested-function mechanism occurs in `create_validator()`.

The outer function receives:

- `protected_branch`
- `BranchProtection`

It then defines `validate()` internally.

`validate()` accesses the outer function's `protected_branch` and `protection` variables. When `create_validator()` returns `validate`, the returned function retains those values through a closure.

This creates a specialized operation:

`create_validator("main", protection) → validator`

The caller can subsequently execute the validator without passing the branch-policy configuration on every call.

The Python implementation also uses a nested `count_valid_approvals()` helper. This isolates approval semantics from the broader Pull Request validation logic.

Other mechanisms demonstrated include:

- immutable `dataclass` configuration
- enumerated workflow states
- sets for reviewer eligibility
- dictionaries for status checks
- exceptions through input validation
- reopening a closed Pull Request
- stale-approval detection
- audit logging
- linear-history validation

The implementation is intentionally standard-library based.

## JavaScript Implementation

The JavaScript program uses an event-driven governance model.

`GovernanceEngine` stores:

- repository configuration
- branch-protection policy
- event listeners
- audit events

The `createPolicyEvaluator()` method creates a function that closes over the repository policy.

Inside that evaluator, `countApprovals()` is itself a nested function. It calculates current approvals using:

- the latest commit
- reviewer eligibility
- approval state
- dismissal status

This structure demonstrates two layers of function nesting:

`createPolicyEvaluator()`
→ returned evaluator
→ `countApprovals()`

The event system provides a complementary perspective. Successful merges and rejected merges emit events, and registered handlers append audit entries.

This is useful for repository automation because policy evaluation and event handling are separate concerns.

The JavaScript implementation also validates:

- Pull Request numbers
- titles
- branch names
- reviewers
- commit identifiers
- status checks
- direct modifications of protected branches

No external npm dependency is required.

## C++ Implementation

The C++ program treats merge eligibility as a governance engine.

`MergeEligibilityEngine` owns a `BranchProtection` object and exposes an evaluation operation.

The nested-function mechanism appears in `createApprovalCounter()`.

The method creates a lambda that captures the policy by value. The lambda then calculates the unique reviewers whose approvals apply to the latest commit.

The C++ implementation emphasizes explicit data structures:

- `std::vector` for ordered commits and reviews
- `std::set` for eligible reviewers and unique approvals
- `std::map` for status checks
- enumerations for Pull Request and review states

The merge engine evaluates multiple independent conditions:

`target branch`
→ `Pull Request state`
→ `commit existence`
→ `status checks`
→ `conversation resolution`
→ `current approvals`
→ `linear history`

Only when all required conditions pass is the Pull Request transitioned to `Merged`.

The set-based approval calculation prevents the same reviewer from satisfying multiple approval requirements.

## Java Implementation

The Java program models repository governance as an enterprise-style domain service.

It uses:

- records for immutable value objects
- enums for workflow states
- interfaces for policy checks
- collections for reviewers, commits, and reviews
- streams for approval filtering
- explicit domain validation
- a dedicated `MergeEligibilityService`

The `PolicyCheck` functional interface represents one independent governance rule.

The service creates policy functions through nested methods such as:

`createBranchPolicy()`

`createStatusPolicy()`

`createApprovalPolicy()`

`createConversationPolicy()`

`createHistoryPolicy()`

The service then evaluates those policies as a collection.

This architecture makes each rule independently testable while allowing the enclosing service to retain the branch-protection configuration.

The approval policy is deliberately different from the branch policy. Approval evaluates reviewer decisions against the latest commit. Branch policy determines whether the Pull Request targets the protected branch and whether the workflow state permits evaluation.

## PostgreSQL Implementation

The SQL implementation models the same governance domain relationally.

Core relationships include:

`repositories → branches → branch_protection_policies`

and:

`pull_requests → commits`

`pull_requests → reviewer_assignments`

`pull_requests → reviews`

`reviews → review_comments`

`pull_requests → status_checks`

The schema uses PostgreSQL-specific enumerated types for Pull Request and review states.

Constraints enforce basic integrity at the database layer.

Examples include:

- unique repository names
- unique branch names per repository
- unique commit SHAs within a Pull Request
- unique reviewer assignments
- non-negative unresolved conversation counts
- valid approval counts
- valid dismissed-review timestamps

The `evaluate_merge_eligibility()` function performs policy evaluation inside PostgreSQL.

Its approval calculation is based on the latest commit. This means an approval attached to an earlier commit does not satisfy the current approval requirement.

The function also evaluates:

- Pull Request state
- draft status
- direct-push restrictions
- conversation resolution
- required approvals
- required status checks

The `pull_request_governance_report` view provides a reporting-oriented representation of current approval state.

The transaction example demonstrates that eligibility evaluation and state transition can occur within a transactional boundary.

## Nested Functions Across the Implementations

The four implementations use different mechanisms for the same conceptual purpose.

| Language | Nested-function mechanism | Governance use |
|---|---|---|
| Python | Nested `def` with closure | Creates a branch-specific validator |
| JavaScript | Inner functions and closures | Creates policy evaluators and approval counters |
| C++17 | Lambdas capturing policy state | Builds an approval-counting policy operation |
| Java 17 | Functional-interface implementations returned by methods | Builds independent governance policy checks |
| PostgreSQL | Functions with local variables and query logic | Performs database-side merge eligibility evaluation |

The language mechanisms are not identical.

Python and JavaScript make lexical closures particularly direct. C++ uses lambdas with captures. Java commonly expresses similar behavior with lambdas, functional interfaces, and methods that produce policy functions. PostgreSQL functions encapsulate database-side behavior and state local variables within a function invocation rather than providing general-purpose nested closures in the same style.

## Review and Approval Failure Modes

Several failure conditions are deliberately represented.

### Stale approvals

An approval is associated with a commit.

When a new commit becomes the latest commit, earlier approvals no longer satisfy the current-commit approval rule.

### Dismissed reviews

A dismissed review is not counted as an active approval.

### Ineligible reviewers

A reviewer's approval is counted only when the reviewer is assigned or otherwise eligible under the modeled policy.

### Missing status checks

A required check that is absent or unsuccessful prevents merge eligibility.

### Unresolved discussions

A protected branch can require review conversations to be resolved before merging.

### Draft Pull Requests

A draft Pull Request remains unsuitable for merge under the modeled policy.

### Direct protected-branch changes

The branch policy can prohibit direct modification of the protected branch.

### Invalid history

The examples treat duplicate commit identifiers as a failure of the simplified linear-history model.

## Performance Considerations

The in-memory implementations use sets for reviewer membership and unique approval tracking.

This makes membership checks approximately constant time on average:

`O(1)`

For a Pull Request containing `n` reviews, approval evaluation is approximately:

`O(n)`

For `n` commits, the simplified linear-history validation is approximately:

`O(n)`

The SQL implementation creates indexes around access patterns used for governance evaluation, particularly:

- target branch and Pull Request state
- Pull Request, commit, and review state
- Pull Request status checks
- unresolved comments

The database model can therefore evaluate governance conditions without scanning unrelated repository records in common cases.

## Security and Governance Considerations

Nested functions can encapsulate policy configuration, but closure state is not automatically a security boundary.

Authorization must still be enforced by the surrounding application and repository platform.

The database implementation strengthens integrity by storing governance rules relationally and evaluating eligibility within PostgreSQL.

Important controls include:

- preventing unauthorized direct pushes
- distinguishing eligible reviewers
- ignoring dismissed approvals
- associating reviews with commits
- enforcing required status checks
- requiring resolved conversations
- preventing invalid state transitions
- protecting branch-level governance records

A production system would also need authenticated identities, authorization checks, immutable audit records, concurrency controls, webhook or event validation, and explicit administrative bypass policies.

## Relationship Between the Four Governance Areas

The project deliberately keeps the concepts separate:

| Mechanism | Question it answers |
|---|---|
| Pull Request | What change is being proposed, from which branch, toward which branch? |
| Code Review | What did reviewers find in the proposed changes? |
| Approval | Has an eligible reviewer formally accepted the applicable changeset? |
| Branch Protection | Are repository-level conditions satisfied for the protected branch? |

A Pull Request can exist without approval.

A review can exist without approval.

An approval can exist without making a Pull Request mergeable.

A branch-protection policy can require approvals and status checks, but it does not replace the review process.

This separation is the key governance relationship represented throughout the implementations.
