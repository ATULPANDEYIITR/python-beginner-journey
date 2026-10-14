# Default Arguments: Practical Programming and Repository Governance

## Technical scope

Default arguments allow a function or method to supply a predefined value when a caller omits an optional parameter. They reduce repetitive configuration while preserving explicit control over behavior.

This repository applies the concept to a software-development workflow involving pull requests, code review, approvals, and branch protection. These areas interact, but they solve different problems:

- **Pull Requests** provide the lifecycle for proposing changes between a source branch and a target branch.
- **Code Review** evaluates the proposed changes through review decisions, inline comments, discussions, and follow-up changes.
- **Approvals** record reviewer decisions and determine whether the configured review threshold has been satisfied.
- **Branch Protection** establishes repository-level rules that restrict when changes can enter a protected branch.

Default arguments make these mechanisms configurable. They do not replace authorization, validation, or enforcement.

## Understanding default arguments

Consider a Python function that creates a pull request:

`def create_pull_request(title, source_branch, target_branch="main", draft=False):`

A caller that omits `target_branch` uses `main`. A caller that explicitly supplies `target_branch="release"` targets the release branch instead.

Defaults are particularly useful when an operation has a stable conventional behavior, such as selecting the repository's default branch or requiring two independent approvals. They are less appropriate when an omitted value must be distinguished from a legitimate value such as `None`.

### Parameter rules

In Python, required positional parameters must precede optional positional parameters. Keyword-only parameters, introduced by `*`, are useful for policy settings because they make calls explicit and reduce mistakes when several Boolean options exist.

For example, `evaluate_merge_policy(checks, approvals, required_approvals=2, require_ci=True)` communicates policy choices more clearly than a function that accepts multiple unexplained positional flags.

JavaScript supports default parameter values and destructured configuration objects. C++ supports default arguments in function declarations. Java does not support general default parameter values, so the Java implementation models configuration with immutable policy records and factory methods. SQL expresses defaults through column declarations and uses constraints and queries to enforce database-level rules.

## Python implementation

The Python script begins with functions whose optional arguments control target branches, draft status, review decisions, and merge-policy settings.

`create_pull_request()` validates branch names and prevents a pull request from targeting its own source branch. `summarize_review()` supplies a default review decision and summary while rejecting unsupported review states.

### Mutable defaults and object identity

Python evaluates default expressions when a function is defined, not each time it is called. This behavior makes mutable defaults dangerous.

A function declared as `def collect_labels(label, labels=[]):` reuses the same list across calls when the caller omits `labels`. Appending a label in one call can therefore affect another call.

The safe implementation uses `labels=None` and creates a new list inside the function. The same principle applies to dictionaries, sets, and other mutable objects.

The `PullRequest` dataclass uses `field(default_factory=list)` and `field(default_factory=set)` so each instance owns independent collections. A new pull request cannot accidentally inherit another pull request's labels or reviewers.

### Definition-time binding

A default such as `limit=DEFAULT_REVIEW_LIMIT` captures the current value when the function is defined. Reassigning the global variable later does not change the captured default.

This distinction matters for configuration that may change while a program is running. If the current configuration must be consulted on every invocation, use a sentinel such as `None` and resolve the effective value inside the function.

### Keyword-only configuration

`evaluate_merge_policy()` separates required inputs from optional policy settings. Its keyword-only parameters configure the approval threshold and required CI and security checks.

The advanced `assess_pull_request()` function also evaluates draft state, unresolved discussions, stale approvals, and named required checks. It returns structured failures rather than a single unexplained Boolean.

The audit-log example uses `occurred_at=None` and `metadata=None` to resolve optional values at call time. It writes JSON Lines records, validates timezone-aware timestamps, and reads records back with error reporting for malformed JSON.

The script includes assertions for expected behavior, invalid configurations, successful merge eligibility, and stale approvals.

## JavaScript implementation

The JavaScript file models repository workflow behavior through objects, Maps, asynchronous checks, and explicit lifecycle operations.

### Configuration through destructured parameters

`createPullRequest()` accepts a configuration object. Its default target branch is `main`, while `draft` defaults to `true`. The function validates the identifier, title, branches, and label collection before creating the object.

Using a configuration object is valuable when an operation has many optional settings. Callers can supply only the relevant fields without relying on positional argument order.

The function copies the labels array rather than retaining the caller's original array. This prevents later external mutations from silently changing the initial pull-request state.

### Lifecycle and review events

The workflow models commits, requested reviewers, review submissions, status checks, conversations, base-branch synchronization, closure, reopening, and merging.

`addCommit()` increments the changeset revision and marks existing approvals as stale. The review history remains available, but the merge evaluator does not count an approval tied to an outdated revision when stale-approval dismissal is enabled.

`submitReview()` supports `APPROVED`, `CHANGES_REQUESTED`, and `COMMENTED`. Inline comments can include a file and line number. Authors cannot review their own pull requests.

### Asynchronous status checks

`runChecksAsynchronously()` executes independent check functions using `Promise.allSettled()`. Unlike `Promise.all()`, this method allows the program to report all completed or failed checks instead of abandoning the entire result when one promise rejects.

A rejected check is recorded as a failure. This prevents a transient exception from being mistaken for a successful CI or security result.

### Merge eligibility

`evaluateMergeEligibility()` accepts optional configuration for required approvals, required checks, discussion resolution, linear history, draft merging, stale approvals, and merge strategy.

The evaluator distinguishes workflow state from review decisions and repository policy. A pull request may contain approvals yet remain ineligible because checks are pending, discussions are unresolved, or the current changeset has not been reviewed.

The implementation is an educational in-memory model. It does not provide distributed locking, durable event storage, or authoritative enforcement against concurrent repository changes.

## C++ case study: Repository governance engine

The C++ program models a protected deployment-service repository using domain-specific structures and a `PullRequest` class.

### Domain model

The implementation defines separate enumerations for pull-request state, review decision, status-check state, and merge method. This prevents unrelated concepts from being represented by ambiguous strings throughout the program.

`ProtectionPolicy` holds governance settings such as required approvals, mandatory CI and security checks, discussion resolution, linear history, permitted merge methods, and administrator bypass.

The `PullRequest` class owns its commits, reviews, status checks, requested reviewers, and conversations. Its methods enforce lifecycle constraints before changing state.

### Changeset-aware approvals

Each review records the revision it evaluated. Adding a commit advances the revision, so previously recorded approvals no longer count when the policy requires current approvals.

The evaluator retains the review history but considers the latest decision from each reviewer. A subsequent request for changes supersedes that reviewer's earlier approval. Dismissed approvals are excluded.

This design separates historical evidence from current merge eligibility.

### Branch policy and merge methods

The case study prohibits merge commits when linear history is required and rejects merge methods absent from the permitted-method set. It checks CI and security status independently and requires unresolved discussions to be addressed.

Direct-push, force-push, and deletion restrictions are represented as governance policy concepts. The in-memory program does not control actual Git transport or hosting-platform permissions, so those restrictions must be enforced by the real repository service.

### Failure handling and complexity

Invalid transitions and malformed input produce exceptions. For example, a merged pull request cannot be merged again, and a closed pull request cannot be merged without being reopened.

Review evaluation uses ordered maps and vectors. Finding the latest review involves a traversal of the review history, followed by policy checks. The principal review-processing cost is linear in the number of stored reviews, while ordered-map operations introduce logarithmic lookup costs.

The demonstration includes an unresolved discussion, a changeset update that invalidates approvals, renewed reviews, successful merge eligibility, and rejection of a closed pull request.

## Java implementation: Enterprise policy model

The Java program models the same governance domain through immutable records, a policy record, explicit state transitions, and a merge-eligibility service implemented by the `PullRequest` domain object.

### Immutable domain values

`Commit`, `Reviewer`, `Review`, `Conversation`, `Policy`, and `Eligibility` are records. Their constructors validate data at creation time, and collection-valued policy fields are defensively copied.

Java has no general method-parameter defaults comparable to Python's default arguments. The `Policy.standard()` factory method provides a reusable default configuration instead. Callers can construct another `Policy` when a repository needs a different approval threshold or check set.

This approach makes policy configuration explicit and prevents a shared mutable configuration object from being modified unexpectedly.

### Review requests and approval state

The program requires reviewers to be explicitly requested before they submit a review. Reviewers cannot approve their own changes, and review submissions cannot directly manufacture a dismissal state.

`Review` records the changeset revision and submission timestamp. The eligibility evaluator selects the latest review per reviewer, counts eligible approvals, checks current status results, and verifies that required conversations are resolved.

The model distinguishes review history from current approval status. A newly added commit changes the revision, making earlier approvals stale under the standard policy.

### Policy evaluation and lifecycle

The `Policy` record defines the required approval count, required checks, permitted merge methods, discussion-resolution rule, linear-history rule, stale-approval behavior, and administrator-bypass setting.

`Eligibility` returns both a Boolean decision and the list of reasons that explain rejection. `merge()` changes the pull-request state only when evaluation succeeds.

The program demonstrates a pull request that initially fails because a conversation is unresolved. After the discussion is resolved, another commit makes previous approvals stale. Fresh reviews and successful checks restore eligibility.

The implementation is an in-memory reference model. Production systems also require authenticated identities, durable audit records, transaction-safe state changes, and synchronization with the repository hosting platform.

## SQL data model: Relational repository governance

The PostgreSQL script stores repository configuration and workflow history in related tables. Its schema separates branches, pull requests, commits, reviews, comments, conversations, status-check runs, and branch-protection rules.

### Relational structure

- `repositories` identifies repositories and their default branches.
- `repository_members` records membership, activity, and repository roles.
- `reviewers` records reviewer teams and approval eligibility.
- `branches` identifies source and target branches and records protected status.
- `branch_protection` stores review thresholds, required checks, merge restrictions, and bypass settings.
- `pull_requests` records the source branch, target branch, author, lifecycle state, and changeset revision.
- `pull_request_commits` preserves the commits associated with a pull request.
- `reviews` records review decisions and the changeset revision they evaluated.
- `review_comments` stores file-specific comments and their resolution state.
- `conversations` tracks discussion threads independently of individual inline comments.
- `required_status_checks` identifies checks mandated by a protection policy.
- `status_check_runs` preserves results for individual changeset revisions.
- `merge_events` records successful merge operations.

Primary keys, foreign keys, uniqueness rules, enumerated types, and check constraints protect data integrity.

### Database defaults and integrity

Defaults such as `state = 'draft'`, `required_approvals = 2`, and `prohibit_force_push = true` establish initial values for omitted columns. These database defaults are distinct from application-level function defaults.

Check constraints prevent negative approval thresholds, invalid revision numbers, blank identifiers, and inconsistent merge metadata. Foreign keys prevent references to nonexistent repository members, branches, and pull requests.

The review-validation trigger rejects self-reviews and approvals from inactive or ineligible reviewers. The lifecycle trigger prevents merged pull requests from returning to an earlier state and rejects attempts to merge a closed pull request without reopening it.

### Current revisions and stale approvals

The `pull_request_merge_eligibility` view uses common table expressions to calculate current approvals, current required-check results, and unresolved discussions.

The latest-review query uses PostgreSQL's `DISTINCT ON` to select the most recent decision for each reviewer. The status-check query selects the latest check run for each check name. A check must succeed on the current changeset revision, not merely on an earlier revision.

The sample workflow begins with two approvals and successful checks. It then advances the pull request revision, demonstrating that old approvals and checks remain in the audit history but no longer satisfy current-revision requirements.

The final inserts record fresh approvals and check runs for the new revision.

### Indexes and transactional limits

The indexes support queries for pull requests targeting a branch, review history by revision and state, current status-check runs, and unresolved conversations.

The script runs inside a transaction so schema creation and sample-data operations can be rolled back together if an error occurs. A production merge service must also lock the relevant pull request and protection policy, verify the target branch head, re-evaluate eligibility, and record the merge atomically.

The view reports eligibility under the rules it explicitly evaluates. It is not a substitute for a complete merge-enforcement service: merge-method restrictions, authorization, direct-push prevention, force-push restrictions, deletion rules, and administrative exceptions must also be enforced at the trusted application or repository-hosting layer.

## Distinguishing the four governance concepts

| Concept | Primary responsibility | How defaults contribute |
|---|---|---|
| Pull Requests | Manage proposed changes, source and target branches, commits, synchronization, conflicts, and lifecycle transitions. | Supply conventional target branches and initial draft behavior. |
| Code Review | Evaluate changes through review decisions, inline comments, conversations, and revision-specific feedback. | Supply a default review state or review-summary text. |
| Approvals | Determine whether eligible reviewers have approved the current changeset and whether those approvals remain valid. | Supply a configurable minimum approval count and stale-approval policy. |
| Branch Protection | Enforce repository-level restrictions and merge prerequisites. | Supply default required checks, merge restrictions, and protected-branch settings. |

A default is a starting value, not proof that a rule has been satisfied. A configured requirement of two approvals does not establish that two eligible people have approved the current changeset. A default successful-check configuration must not be confused with actual CI execution. A protected-branch policy must be enforced by an authoritative service rather than merely displayed by an application.

## Common implementation failures

### Confusing omission with an explicit value

A caller may intentionally pass `None`, `null`, an empty string, or an empty collection. These values should not automatically be treated as omitted arguments unless that behavior is part of the contract. Sentinel values and explicit validation make the distinction clear.

### Reusing mutable objects

Python functions and JavaScript destructuring defaults can produce unexpected state leakage when defaults refer to shared mutable objects. Create fresh collections where independent state is required, or defensively copy caller-owned values.

### Treating historical approvals as current

A review decision describes a particular revision of a changeset. New commits, base-branch synchronization, dismissal, or later review decisions may change merge eligibility. Historical approval records should remain available for audit while current eligibility is recalculated.

### Using permissive defaults for security policy

A default should not silently weaken access controls. Required checks, eligible reviewers, administrator bypass, force-push restrictions, and merge methods should be explicit policy decisions. The absence of a check result must not be interpreted as success.

### Confusing state validation with authorization

A function can reject a closed pull request, but that alone does not establish who is authorized to merge it. Authentication, reviewer eligibility, permission checks, policy evaluation, and atomic state changes are separate responsibilities.

## Performance and production considerations

Default arguments reduce repetitive caller configuration, but they do not remove the cost of validating the resulting operation. Merge eligibility must still be evaluated against the current changeset, review history, status-check results, and branch-protection rules.

For large repositories, indexes should support the actual query patterns used by review dashboards and merge services. Repeated full-history scans may become expensive as review and check records accumulate. Current-state projections can improve response time, provided they remain consistent with the authoritative audit history.

Concurrent updates require particular care. A pull request might be approved while CI is running, receive another commit before merge, or target a branch whose head has changed. The final merge operation must revalidate the relevant conditions within a transaction or an equivalent atomic repository-hosting operation.

Default configuration is most reliable when it is explicit, validated, independently testable, and subordinate to the repository's authoritative security and governance rules.
