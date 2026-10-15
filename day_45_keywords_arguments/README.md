# Keyword Arguments: Explicit Configuration and Repository Governance

## Technical scope

Keyword arguments bind supplied values to named parameters in languages that support named argument calls. They make the relationship between a value and its intended meaning explicit, particularly when functions accept several optional settings of similar types.

This repository uses Pull Requests, Code Review, Approvals, and Branch Protection as a realistic setting for examining that idea. Repository governance frequently involves multiple boolean flags, policy thresholds, reviewer identities, status-check requirements, and merge strategies. Passing such values positionally can obscure their meaning or make call sites fragile.

The implementations distinguish three mechanisms:

- **Native keyword arguments:** Python binds values directly to named parameters.
- **Named configuration objects:** JavaScript, C++, and Java use objects or typed structures to represent named settings.
- **Relational configuration:** PostgreSQL stores policy values in constrained columns and validates structured JSONB options.

These mechanisms are related, but they are not interchangeable. A Python call such as `evaluate_merge_policy(pr, required_approvals=2)` uses language-level keyword binding. A JavaScript call such as `evaluateMergePolicy(pr, { requiredApprovals: 2 })` passes one ordinary object whose properties the function reads. C++ and Java similarly pass typed configuration objects rather than supporting Python-style named arguments.

## Python argument binding

The Python implementation starts with `create_pull_request`, which combines required positional-or-keyword parameters, a default target branch, and keyword-only settings.

The following call supplies the principal arguments by name:

    create_pull_request(
        title="Validate deployment settings",
        source_branch="feature/deployment-validation",
        target_branch="main",
        draft=True,
        reviewers=("Maya", "Daniel"),
    )

The function signature makes the binding rules explicit. `title` and `source_branch` are required. `target_branch` defaults to `main`. The asterisk before `draft` makes `draft` and `reviewers` keyword-only parameters. Attempting to pass the draft flag positionally raises `TypeError`.

Keyword-only settings are particularly useful when parameters have the same type but different meanings. Two consecutive boolean parameters can be easy to reverse accidentally. Requiring their names at the call site reduces this risk.

The program also demonstrates positional, keyword, and mixed calls. Python permits a positional-or-keyword parameter to be supplied positionally or by name, but the same parameter cannot be supplied twice. Invalid combinations are rejected during argument binding before the function body executes.

### Default values and mutable objects

`collect_checks` accepts an optional list and creates a new list when no value is supplied. It does not use a mutable list as a default argument. A mutable default would be created once when the function is defined and could be shared between calls.

The `BranchProtection` dataclass uses `default_factory` to create independent lists of required status checks for each policy instance. This prevents changes to one branch policy from silently affecting another.

Defaults are part of the function contract. A new optional parameter with a safe default can preserve existing call sites, while changing a default's meaning may change behavior without producing a syntax error.

### `**kwargs` and controlled extension

The functions `build_ci_configuration`, `configure_branch_protection`, `record_review`, and `validate_policy_payload` demonstrate collecting named arguments into dictionaries.

`**kwargs` is useful when a function accepts an extensible set of options. It also introduces risks: misspelled names can otherwise be silently accepted, and arbitrary settings can undermine validation.

The branch-protection configuration function therefore checks an allowlist of supported option names. It validates review thresholds, booleans, and the required-check collection before returning a policy. The review-recording function similarly limits accepted metadata fields.

Python type annotations document intended types but do not enforce those types at runtime. The examples explicitly reject booleans where a true integer is required because `bool` is a subclass of `int` in Python.

### Dictionary unpacking and wrappers

The Python program uses `**options` to expand a mapping into keyword arguments. It also combines mappings using dictionary unpacking. When duplicate keys occur in a dictionary expression, the later value takes precedence.

This is useful for combining organization-wide defaults with repository-specific overrides. The merged configuration should be validated after composition, since an override may introduce an invalid value.

The `audit_call` decorator forwards `*args` and `**kwargs` to the wrapped function. `functools.wraps` preserves metadata and supports signature inspection. `inspect.signature` and `Signature.bind` demonstrate how Python frameworks can inspect a function's declared parameters and validate a proposed call without executing the function.

The merge-decision function validates the Pull Request identifier, actor, and strategy. The wrapper logs argument counts rather than logging potentially sensitive argument values.

## JavaScript: named options and lifecycle events

JavaScript does not support Python-style keyword arguments. It commonly achieves similar readability with an options object and destructuring:

    createPullRequest({
        title: "Enforce token audience validation",
        sourceBranch: "feature/token-audience",
        reviewers: ["Maya", "Daniel"],
        draft: true,
    });

The function's destructured parameter provides defaults for `targetBranch`, `draft`, and `reviewers`. It validates each field because JavaScript does not enforce the intended types automatically.

The program distinguishes rest parameters from named configuration. `...comments` collects additional positional arguments into an array; it does not capture arbitrary named arguments. `submitReview` uses a separate options object for the review state, commit SHA, and dismissal behavior.

Object spread combines policy defaults with repository-specific overrides. Later properties replace earlier properties with the same name. `configureProtection` validates override keys and types, removes duplicate required checks, and freezes the resulting top-level policy object. Freezing is shallow, so nested objects and arrays require their own immutability strategy if the configuration must be deeply immutable.

### Event-driven Pull Request model

`PullRequestWorkflow` represents the lifecycle of an actual proposed repository change. It records commits, reviews, status checks, review conversations, and merge decisions.

The workflow emits events when important state changes occur. Subscribers receive a timestamped event object, allowing logging or notification code to observe changes without controlling the lifecycle implementation.

The model rejects invalid transitions, including adding commits to a merged Pull Request and reviewing a commit that is not part of the current change. When a new commit arrives, approvals against older commits become dismissed when the policy requires stale-review dismissal.

The eligibility evaluation counts only current, non-dismissed reviews from requested reviewers. It separately checks the approval threshold, required CI results, unresolved conversations, and Pull Request state. The merge operation refuses to proceed while any requirement fails.

The asynchronous example uses `Promise.all` to collect independent check results. A rejected promise indicates that the evaluation itself failed. It must not be treated as a successful status check merely because the remaining checks passed.

## C++: repository governance case study

The C++ program models a payments-platform repository protecting its `main` branch. It uses enums for lifecycle states, reviews, checks, and merge strategies; structures for commits and policy configuration; and a repository class that controls state changes.

`BranchProtection` provides validated setter methods for named policy configuration. Fluent calls make each setting readable while retaining the static types and compile-time checking provided by C++.

The `Repository` class stores Pull Requests in an `unordered_map`, keeps required checks in a `set`, and records reviews and commits in vectors. It validates source branch naming, target branch identity, unique Pull Request identifiers, commit SHA formatting, relative file paths, requested reviewer eligibility, and current-commit review requirements.

The merge-eligibility algorithm determines the latest commit and ignores dismissed or outdated reviews. It also rejects a Pull Request with a current change request, insufficient approvals, missing or failed required checks, or unresolved discussions.

With \(R\) reviews and \(C\) required checks, the straightforward review scan is \(O(R)\) and the required-check lookup is approximately \(O(C \log S)\) for an ordered map containing \(S\) observed checks. The implementation favors clarity and deterministic policy behavior over optimizing a small demonstration dataset.

The case study also shows that merge eligibility and branch access are separate concerns. A qualifying Pull Request may merge only after the review and check requirements pass, while direct pushes, force pushes, and branch deletion remain subject to their own protected-branch rules.

## Java: enterprise policy and domain modeling

The Java implementation uses records for immutable values such as `Commit`, `Review`, `Conversation`, `BranchProtection`, and `MergeEvaluation`. Enums constrain lifecycle and review states to known values. Constructors validate inputs so invalid objects are rejected at the domain boundary.

`BranchProtection.Builder` provides named configuration through descriptive methods. For example, `requiredApprovals(2)` states the policy intent directly without depending on parameter position. The built record copies its required-check collection into an immutable set, preventing later modifications to the caller's original collection from changing the policy.

The `PullRequest` class owns lifecycle state and its related collections. It enforces legal state transitions, validates review eligibility, requires reviews to reference the latest commit, and records dismissal of stale reviews. Collections are exposed as copies rather than as mutable internal state.

`MergeEligibilityService` evaluates the current state independently of the entity's storage and mutation responsibilities. It identifies the most recent active decision by each reviewer and applies the protected branch's approval, check, and discussion requirements.

The `RepositoryGovernance` service ensures that a Pull Request targets the protected branch and delegates eligibility and merge operations to the policy service. It also models direct-push, force-push, and deletion restrictions.

This separation is useful in enterprise systems because a review decision, a policy definition, and an authorization decision have different responsibilities. The service can be tested independently, while the domain objects protect their own invariants.

## PostgreSQL: relational enforcement

The SQL implementation represents repository governance through normalized relational tables.

| Table | Responsibility |
|---|---|
| `repositories` | Identifies repositories and their default branches. |
| `repository_members` | Stores membership, role, and active status. |
| `branches` | Represents source and target branches and their current heads. |
| `commits` and `commit_files` | Store commit identities and changed paths. |
| `pull_requests` | Stores proposal metadata and lifecycle state. |
| `pull_request_commits` | Associates a Pull Request with its ordered commits. |
| `review_requests` | Records requested reviewers. |
| `reviews` | Stores review decisions, eligibility, and dismissal information. |
| `review_comments` | Records inline discussion and resolution status. |
| `status_checks` | Associates check results with a specific commit. |
| `branch_protection_policies` | Stores branch-level enforcement settings. |
| `required_status_checks` | Defines the checks required by a policy. |
| `policy_audit_events` | Preserves changes to branch policy configuration. |

Primary keys, foreign keys, unique constraints, checks, and triggers enforce different aspects of integrity. A foreign key ensures that a referenced record exists. A check constraint validates a value within a row. A trigger validates relationships that span multiple rows, such as whether a reviewer belongs to the repository and was requested for the relevant Pull Request.

The `validate_policy_options` function accepts a JSONB object and validates recognized option names and types. It rejects misspelled settings instead of silently ignoring them. This resembles a validated keyword-argument interface, while the actual stored policy remains represented by relational columns.

The `pull_request_merge_eligibility` view combines the current commit, review decisions, required checks, and unresolved discussions into a diagnostic eligibility result. Its result is an evaluation, not a substitute for an atomic merge operation. A production system must prevent concurrent changes from invalidating the conditions between evaluation and merge.

The script demonstrates transaction boundaries when the Pull Request advances to a new commit. Older reviews are dismissed when configured, and new required checks are created for the new revision. Status checks and approvals for the previous head cannot automatically qualify the new head.

The SQL example also records policy changes in an audit table. Such records support accountability when a repository's approval threshold, bypass permissions, or required checks change.

## The four governance concepts

### Pull Requests

A Pull Request proposes a change from a source branch to a target branch. Its lifecycle includes draft creation, readiness for review, commit updates, review activity, status-check execution, merging, closing, and possible reopening.

A changeset is the set of changes being evaluated. New commits can alter that changeset and make previous approvals or status checks stale. Merge strategies such as merge commit, squash, and rebase determine how accepted changes are integrated. The examples model merge strategy selection, although they do not implement Git's underlying object graph or conflict-resolution algorithm.

A merge conflict must be resolved against the relevant target-branch state. In a production workflow, synchronizing with the base branch can change the effective changeset and trigger additional checks or review requirements.

### Code Review

Code Review evaluates whether the proposed changes satisfy correctness, security, maintainability, and testing expectations. Inline comments identify concerns in particular files or lines, while review-level comments can discuss the broader design.

The code models review decisions separately from comment resolution. A reviewer can leave comments without approving the change. A request for changes is a distinct state that blocks merging under the demonstrated policy. Resolving a discussion records that the conversation is addressed; it does not automatically constitute approval.

Review quality depends on inspecting the relevant changeset, understanding its intended behavior, checking failure paths, and confirming that security-sensitive behavior is tested. The examples model review states and discussion resolution but do not attempt to automate the intellectual judgment required for a high-quality review.

### Approvals

An approval is a reviewer decision. Its eligibility depends on reviewer identity, repository membership, the requested-review relationship, the reviewed commit, and whether the decision has been dismissed.

The examples require approvals against the latest commit and count no more than one active decision per reviewer. A new commit can invalidate an earlier approval when stale-review dismissal is enabled. A dismissed approval remains part of the review history but no longer contributes to merge eligibility.

Approval requirements are policy thresholds. Two approvals are not inherently equivalent to two independent security checks, and a high approval count cannot compensate for a failed required check. The approval threshold and the other merge prerequisites are evaluated independently.

### Branch Protection

Branch Protection defines repository-level restrictions on how a target branch can change. The examples model required reviews, required status checks, stale-review dismissal, conversation resolution, linear history, direct-push restrictions, force-push restrictions, deletion restrictions, administrator enforcement, and bypass permissions.

These settings govern merge eligibility and access to the protected branch. The code evaluates a subset of Git hosting platform behavior, rather than claiming to implement every provider's policy semantics. Linear-history enforcement, signed-commit verification, and administrator bypass behavior require actual hosting-platform or Git-level enforcement in a production system.

A bypass permission is a deliberate exception to normal governance. It should be restricted to explicitly authorized actors and audited. An administrator should not automatically be treated as exempt from every policy unless the configured rules explicitly permit it.

## Keyword arguments and named configuration compared

| Mechanism | What it provides | Main limitation |
|---|---|---|
| Python keyword arguments | Direct binding from parameter names to supplied values. | Unknown keywords normally raise `TypeError` unless captured by `**kwargs`. |
| Python `**kwargs` | An extensible dictionary of extra named values. | Requires explicit validation to prevent unknown or misspelled options. |
| JavaScript options object | Named properties, destructuring defaults, and object composition. | No native named-argument binding; property names and runtime types require validation. |
| C++ policy structure | Typed configuration, explicit setters, and compile-time type checking. | Does not provide native named arguments at function call sites. |
| Java record and builder | Immutable policy snapshots, domain validation, and readable configuration. | Builder methods must be maintained as the policy contract evolves. |
| PostgreSQL JSONB options | Flexible structured configuration with server-side validation. | Flexible input does not replace normalized policy storage or database constraints. |

## Failure conditions and production boundaries

Several distinctions are essential when applying these implementations to a real repository platform:

- A successful local evaluation does not guarantee that a remote merge remains eligible. The source branch, target branch, review state, or status checks can change concurrently.
- A reviewer's approval must be associated with a particular revision. Counting every historical approval can incorrectly allow an outdated changeset to merge.
- A passing status check for an older commit does not prove that the current commit passes the same check.
- A resolved comment is not the same as an approval. Review discussions and review decisions must be stored and evaluated separately.
- Keyword configuration should reject unknown keys, invalid types, negative thresholds, and unsupported enum values. Silently ignoring a misspelled security setting can produce a policy weaker than intended.
- A successful application-level check must be followed by an atomic or concurrency-safe merge operation. Production implementations need transactions, locking or equivalent concurrency controls, and revalidation of the latest branch state.
- Branch protection must be enforced by the authoritative repository service. A standalone program or SQL view can model and diagnose the rules but cannot, by itself, prevent remote Git operations.
- Audit logs should preserve who changed policy, what changed, when the change occurred, and whether a privileged bypass was used. Sensitive credentials and access tokens must not be placed in general-purpose keyword dictionaries, logs, or review metadata.

The central design distinction is that named configuration improves the clarity of a call, while validation and enforcement determine whether that call can safely change repository state. A readable argument name reduces ambiguity; it does not replace a policy invariant, authorization check, transaction, or protected-branch rule.
