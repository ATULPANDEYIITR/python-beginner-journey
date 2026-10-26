# Errors and Exceptions in Repository Governance Workflows

## Scope

This project models errors and exceptions through a repository-development workflow involving Pull Requests, Code Review, Approvals, and Branch Protection.

The four areas have distinct responsibilities:

| Area | Primary responsibility |
|---|---|
| Pull Request | Proposes a changeset from a source branch toward a target branch |
| Code Review | Evaluates the proposed changes through reviews and conversations |
| Approvals | Records whether eligible reviewers accept a specific revision |
| Branch Protection | Enforces repository-level conditions before the target branch can receive the merge |

The implementations deliberately treat invalid states, policy violations, stale approvals, unresolved conversations, missing checks, and merge failures as explicit failure conditions.

## Domain Model

The core relationship is:

`Repository → Branches → Commits → Pull Requests → Reviews → Review Comments`

Repository governance then evaluates:

`Pull Request + Reviews + Approvals + Status Checks + Branch Protection → Merge Eligibility → Merge`

A Pull Request represents the proposed change. Its source branch contains the development work, while its target branch identifies where the change is intended to land.

Code Review evaluates the contents of that proposal. Review comments identify issues or questions, and review states express the reviewer's current assessment.

Approvals are narrower than reviews. An approval is a decision that can contribute toward the target branch's required approval count. The approval is associated with a particular commit so that the system can identify stale decisions after the changeset changes.

Branch Protection operates at the target-branch level. It does not perform the review itself. Instead, it establishes conditions that must be satisfied before a Pull Request can be merged.

## Pull Request Lifecycle

A Pull Request moves through explicit states:

`DRAFT → OPEN → MERGED`

or:

`DRAFT → OPEN → CLOSED → OPEN`

A normal open Pull Request can also become:

`OPEN → CLOSED`

A merged Pull Request is terminal in the model.

The implementations enforce state-dependent operations. A closed Pull Request cannot receive new reviews or commits. A merged Pull Request cannot be reopened or modified. Reopening is explicitly supported for a closed Pull Request.

Draft Pull Requests represent proposed work that is not yet ready for merge evaluation. The governance engines reject them as merge candidates.

Base-branch synchronization is represented by adding the current target-branch revision to the Pull Request's working history. In a production Git implementation, synchronization requires actual commit-graph and conflict analysis.

Merge conflicts are treated as failure conditions rather than silently resolved. The C++ and Python models use explicit exceptions for unsafe or unsupported ancestry conditions.

## Changesets and Commits

A changeset consists of commits and changed files.

The models validate:

- non-empty commit identifiers
- meaningful commit messages
- at least one commit before merge
- at least one changed file
- valid source and target branches
- distinct source and target branches

A Pull Request's current commit is important for approval validity. An approval attached to an older commit can become stale when new changes are pushed.

The PostgreSQL implementation stores commit membership separately from Pull Requests through `pull_request_commits`. This preserves commit ordering without duplicating commit records.

## Code Review

Code Review is concerned with evaluating the proposed implementation.

The model supports:

- review submission
- inline-style review comments
- comments associated with reviewers
- review states
- requested changes
- approval decisions
- discussion resolution
- review validation against a specific commit

A review comment can remain unresolved even when the reviewer's overall state changes. This distinction is important because a repository can require all review conversations to be resolved before merge.

The review workflow is therefore:

`Review Submission → Comment or Decision → Discussion → Resolution → Updated Review Decision`

The system rejects merge when required conversations remain unresolved.

### Review Quality Controls

A review is useful only when its decision applies to the revision being merged.

The Java implementation explicitly compares the reviewed commit with the Pull Request's current commit. If an approval refers to an older commit, the implementation raises `StaleApprovalException`.

The PostgreSQL trigger performs the same protection at the database boundary for approvals.

This prevents application logic from accidentally treating an outdated approval as current.

## Approvals

Approval is a decision, not merely evidence that a reviewer opened or commented on a Pull Request.

The governance model distinguishes:

| Review state | Merge approval contribution |
|---|---:|
| `commented` | No |
| `changes_requested` | No |
| `approved` | Yes, when eligible and current |
| `dismissed` | No |

Approvals are counted by distinct reviewers rather than by raw review rows. This prevents repeated approvals by the same reviewer from artificially satisfying a required-review count.

An approval must also satisfy reviewer eligibility. The PostgreSQL model uses `reviewer_eligibility` to associate eligible reviewers with a branch-protection policy.

An approval can become stale when a new commit changes the Pull Request. The Java implementation detects stale approvals explicitly, while the PostgreSQL trigger prevents an approval from being inserted when it refers to an older current revision.

Dismissed approvals no longer contribute toward merge eligibility.

## Branch Protection

Branch Protection is repository governance rather than code review.

A protection policy can require:

- a minimum number of eligible approvals
- specific status checks
- resolved review conversations
- linear history
- restricted force pushes
- restricted branch deletion
- controlled administrator bypass

The policy is associated with the target branch.

For example:

`main`
`│`
`├── required approvals: 2`
`├── unit-tests: passing`
`├── security-scan: passing`
`├── conversations: resolved`
`├── force push: denied`
`└── deletion: denied`

The protection policy does not replace reviews. It evaluates whether the results of the review and automation process satisfy repository governance rules.

## Merge Eligibility

Merge eligibility is the final decision point.

A simplified evaluation is:

`Open PR`
`  ↓`
`Not a Draft`
`  ↓`
`Has Commits and Changes`
`  ↓`
`Required Eligible Approvals`
`  ↓`
`Required Status Checks Passing`
`  ↓`
`Required Conversations Resolved`
`  ↓`
`History Constraints Satisfied`
`  ↓`
`Merge Eligible`
`  ↓`
`Merge`

Failure at any required stage produces a domain-specific error.

Examples include:

- `ValidationError`
- `StateTransitionError`
- `PolicyViolation`
- `MergeConflictError`
- `StaleApprovalException`

This separation makes the failure cause distinguishable from a generic runtime error.

## Python Implementation

The Python implementation models repository workflow behavior using dataclasses, enums, dictionaries, lists, and sets.

Important components include:

| Component | Responsibility |
|---|---|
| `Repository` | Stores branches, Pull Requests, and protection policies |
| `Branch` | Represents source or target branch state |
| `Commit` | Represents a validated changeset unit |
| `PullRequest` | Controls lifecycle and review operations |
| `Review` | Represents reviewer decisions and comments |
| `StatusCheck` | Represents automated validation |
| `BranchProtection` | Defines target-branch requirements |
| `MergeEngine` | Evaluates merge eligibility |

Python exceptions are divided into workflow-level categories. This makes failures catchable at the correct abstraction level.

The example first fails because only one approval exists and a review conversation remains unresolved. It then resolves the conversation, adds the second approval, and performs the merge.

The example also attempts an illegal post-merge commit and demonstrates the resulting state-transition failure.

## JavaScript Implementation

The JavaScript implementation emphasizes event-driven behavior.

`EventBus` publishes events such as:

- `pull_request.state_changed`
- `pull_request.commit_added`
- `review.submitted`
- `check.updated`

The model uses `Map` for status checks and event handlers and `Set` for changed files and approval identities.

JavaScript's asynchronous capabilities are not required for this deterministic case study, so the implementation avoids artificial asynchronous operations. Event-driven state notifications provide the relevant JavaScript-specific design instead.

Domain errors carry both a message and an error code. This allows consumers to distinguish validation failures from policy failures without parsing error strings.

The governance engine separately evaluates:

1. Pull Request state
2. Draft status
3. Changeset completeness
4. Required approvals
5. Required status checks
6. Review conversations
7. Simplified history constraints

## C++17 Implementation

The C++17 implementation focuses on a repository governance engine with explicit object ownership through references and STL containers.

Key structures include:

- `Commit`
- `Review`
- `ReviewComment`
- `StatusCheck`
- `Branch`
- `BranchProtection`
- `PullRequest`

The exception hierarchy derives from `std::runtime_error`.

The governance engine uses:

- `std::set` for distinct approvers and required checks
- `std::map` for status checks
- `std::vector` for ordered commits and reviews
- explicit enum states for workflow transitions

The implementation intentionally does not pretend that commit count alone proves linear Git history. When the simplified model reaches a history that requires ancestry analysis, it raises `MergeConflictError`.

A production C++ implementation would inspect the Git commit DAG rather than infer ancestry from list structure.

## Java 17 Implementation

The Java implementation uses explicit enterprise-style domain types and policy objects.

Records represent immutable values such as:

- `Commit`
- `ReviewComment`

Interfaces represent independent merge rules:

`MergeRule`

Concrete policy rules include:

- `BasicMergeRule`
- `ApprovalRule`
- `StatusCheckRule`
- `ConversationRule`

`MergeEligibilityService` composes these rules and evaluates them in sequence.

This design keeps Pull Request state transitions separate from policy evaluation. A Pull Request knows whether it can transition from open to merged, while policy objects decide whether the transition is permitted.

Java-specific exception types distinguish stale approvals from ordinary policy violations. This is useful when an application needs to trigger a different remediation workflow for each failure class.

## PostgreSQL Implementation

The PostgreSQL implementation provides a relational representation of the entire workflow.

The principal entities are:

| Table | Purpose |
|---|---|
| `repositories` | Repository governance context |
| `users` | Reviewers and repository actors |
| `branches` | Source and target branches |
| `commits` | Repository commit records |
| `pull_requests` | Proposed changes and lifecycle state |
| `pull_request_commits` | Changeset membership |
| `pull_request_files` | Changed paths |
| `reviews` | Review decisions |
| `review_comments` | Review discussions |
| `status_checks` | Automated checks |
| `branch_protection_policies` | Target-branch governance |
| `required_status_checks` | Required automation |
| `reviewer_eligibility` | Eligible approval identities |

Database constraints reject malformed records before they reach workflow evaluation.

The `validate_review_commit` trigger protects approval freshness. An approval associated with an outdated current revision is rejected.

The `resolve_comment_timestamp` trigger maintains consistent resolution timestamps.

The `merge_eligibility` function evaluates:

- Pull Request state
- eligible approvals
- current commit association
- required status checks
- unresolved conversations

The `pull_request_governance_report` view provides a reporting-oriented representation of review and check state.

The merge example uses a transaction and locks the Pull Request row before evaluating and changing its state. This reduces the risk of concurrent operations observing and modifying the same workflow state inconsistently.

## Error and Exception Taxonomy

The four workflow areas produce different classes of failure.

| Failure | Meaning |
|---|---|
| Validation failure | Input or domain data is malformed |
| State transition failure | An operation is incompatible with the current Pull Request state |
| Review failure | A review or conversation requirement is incomplete |
| Stale approval | An approval applies to an older revision |
| Policy violation | Branch-level governance requirements are not satisfied |
| Status-check failure | Required automation is missing, pending, or failing |
| Merge conflict | The changes cannot safely satisfy the modeled merge constraints |

This taxonomy is more useful than treating every failure as an undifferentiated exception because different failures require different corrective actions.

## Failure Scenarios

### Draft Pull Request

A draft Pull Request is valid repository state but is not a valid merge candidate.

The correct response is a policy rejection rather than a data-validation failure.

### Missing Approval

A Pull Request can contain extensive review discussion and still fail because the required number of eligible approvals has not been reached.

### Stale Approval

A reviewer can approve commit `A`, after which commit `B` is added. The approval for `A` should not automatically certify `B` when the policy requires current-revision approval.

### Unresolved Conversation

A Pull Request can have enough approvals but still fail because a required review conversation remains unresolved.

### Failing Status Check

Review approval does not override an automated status check required by branch protection.

### Invalid State Transition

A merged Pull Request cannot accept a new commit in these models. The failure is a state-transition error, not a review failure.

### Closed Pull Request

A closed Pull Request can be reopened. This is different from creating a new Pull Request because the existing proposal retains its identity and history.

## Security Considerations

Repository governance is a security boundary.

The implementations enforce several controls:

- eligible reviewers are explicitly modeled
- approvals are associated with specific commits
- dismissed approvals do not count
- unresolved conversations can block merges
- protected branches reject unsafe operations
- force-push permission is modeled separately
- branch deletion permission is modeled separately
- administrator bypass is represented explicitly
- merge operations validate policy before changing state

The database model also places important validation close to persistent data. Application-level validation alone is insufficient when multiple services can write to the same database.

A production system would also authenticate actors, authorize every state-changing operation, record audit events, and protect repository credentials and signing keys.

## Performance Considerations

The models use sets and maps where membership and lookup operations matter.

Python uses dictionaries and sets for repositories, policies, checks, changed files, and approval identities.

JavaScript uses `Map` and `Set` for the same categories of high-value lookup.

C++ uses ordered STL containers where deterministic traversal is useful.

Java uses `HashMap`, `HashSet`, and immutable collections where appropriate.

PostgreSQL indexes are concentrated on workflow queries:

- target branch plus Pull Request state
- Pull Request plus review state
- Pull Request plus status-check state
- unresolved review comments

The database model avoids indiscriminate indexing because every index adds storage and write-maintenance cost.

For a large repository platform, merge eligibility would need efficient caching, event-driven check updates, reviewer-policy lookup, and commit-graph operations rather than repeatedly scanning complete histories.

## Important Distinctions

The implementation preserves these distinctions:

**Pull Request**

Represents the proposed changeset and its lifecycle.

**Code Review**

Represents human evaluation of the proposed implementation and its discussions.

**Approval**

Represents a qualifying reviewer decision that may satisfy a merge requirement.

**Branch Protection**

Represents repository-level rules that determine whether the target branch accepts the merge.

A review can exist without being an approval. An approval can exist without being sufficient. A sufficient approval set can still fail branch protection because of status checks or unresolved conversations.

## Practical Workflow

A realistic repository change proceeds through:

`Developer`
`   │`
`   ├── creates source branch`
`   │`
`   ├── creates commits`
`   │`
`   └── opens Pull Request`
`          │`
`          ├── automated status checks`
`          │`
`          ├── reviewer evaluation`
`          │      ├── comments`
`          │      ├── requested changes`
`          │      └── approvals`
`          │`
`          └── branch protection evaluation`
`                 │`
`                 ├── reject with explicit failure`
`                 │`
`                 └── permit merge`
`                         │`
`                         └── target branch updated`

The central design principle is that each stage owns a different kind of decision. Errors and exceptions communicate when a transition cannot safely proceed.

## Limitations

These implementations are deliberately self-contained models rather than complete Git hosting systems.

They do not implement:

- actual Git object storage
- real commit-DAG traversal
- network authentication
- signed commits
- webhook delivery
- distributed locking
- repository-scale permission inheritance
- actual merge conflict resolution
- hosted Pull Request APIs

The PostgreSQL implementation provides persistent relational enforcement, while the language implementations focus on executable domain behavior.

The simplified linear-history checks should not be interpreted as equivalent to Git's actual ancestry analysis. Real merge eligibility requires examining the repository's commit graph and the exact merge strategy being applied.
