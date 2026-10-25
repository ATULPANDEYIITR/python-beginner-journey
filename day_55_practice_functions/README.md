# Practice: Functions Through Repository Governance

## Purpose

This project practices functions through a realistic software-development workflow. Each implementation models how a proposed code change progresses through review, automated validation, approval, repository policy enforcement, and merging.

The four governance areas have separate responsibilities:

- **Pull Requests** provide the workflow for proposing changes between source and target branches.
- **Code Review** records reviewer feedback, inline discussions, and decisions about a changeset.
- **Approvals** determine whether eligible reviewers have accepted the current version of the changes.
- **Branch Protection** defines repository-level requirements that must be satisfied before merging.

A review is not automatically an approval. An approval does not guarantee that a merge is permitted. A pull request can have approved reviews and successful tests yet remain ineligible because its target branch has advanced or a discussion remains unresolved.

## Domain Model

The implementations use this relationship:

Repository → Branches → Commits → Pull Requests → Reviews → Review Comments

Pull Requests also connect to status checks and branch-protection policies. Those records contribute to a computed merge-eligibility decision, which is evaluated again before the merge operation.

The model distinguishes six important forms of state:

| State or record | Meaning |
|---|---|
| Proposed changes | Commits introduced by the source branch |
| Branch state | Current source and target commit identifiers |
| Review decisions | Comments, approvals, requested changes, and dismissals |
| Automated checks | Build, test, and security results associated with a commit |
| Repository policy | Rules governing reviews, history, and protected branches |
| Merge eligibility | The result of evaluating all applicable requirements |

## Pull Request Lifecycle

A pull request identifies a source branch and a target branch. The source contains the proposed changes; the target is the branch that would receive them.

The lifecycle represented by the programs includes:

- Opening a pull request and capturing its current source and target commit identifiers.
- Marking an open pull request as a draft when it is not ready for review.
- Marking a draft as ready for review.
- Requesting reviews from eligible reviewers.
- Recording status-check results against the proposed source commit.
- Synchronizing the pull request when its source or target branch advances.
- Closing an unmerged pull request or merging an eligible one.

A commit added to the source branch changes the proposed changeset. The previously recorded head identifier then becomes stale. Target-branch advancement also requires synchronization because the proposed change must be evaluated against the current target.

A stale head or base is a merge blocker. Synchronization updates the recorded identifiers, but it does not prove that the new changes are correct. Reviews and status checks must still be valid for the current changeset.

A merge strategy controls how the changes enter the target branch:

| Strategy | Behavior | Governance consideration |
|---|---|---|
| Merge commit | Preserves the branch relationship through a merge commit | Can violate a linear-history requirement |
| Squash | Combines the proposed changes into one target commit | Simplifies target history |
| Rebase | Replays changes onto the target history | Requires care when commit identifiers change |

The programs model the strategy and apply a linear-history rule where relevant. They do not reproduce all internal behavior of a production Git hosting platform.

Reopening is allowed only for a closed, unmerged pull request. A merged pull request is treated as a completed lifecycle transition rather than an ordinary closed request.

## Code Review

Code review evaluates the quality and correctness of the proposed changes. Reviewers inspect the changeset and provide feedback about correctness, security, maintainability, tests, and compatibility.

The implementations represent review decisions using explicit states:

| Review state | Meaning |
|---|---|
| `commented` | Feedback was submitted without approving or rejecting the changes |
| `approved` | The reviewer accepted the reviewed version |
| `changes_requested` | The reviewer identified changes that should be made |
| `dismissed` | A previous review decision no longer counts as active |

Comments can contain observations about a particular file or line. A discussion may remain unresolved after a review has been submitted. The sample workflow therefore treats review decisions and discussion resolution as separate concerns.

The implementations retain review history rather than replacing every prior review. The latest decision for each reviewer is used during eligibility evaluation. This prevents an earlier approval from overriding a later request for changes or dismissal.

Good review practice keeps comments specific, actionable, and tied to the actual changeset. Reviewers should check error handling, input validation, security boundaries, tests, and unintended behavior. A review should not be treated as a substitute for automated testing.

The examples use simple conversation-resolution records. They do not implement threaded replies, GitHub's full review-submission semantics, or every possible discussion lifecycle.

## Approvals

Approvals are review decisions used to satisfy a repository's acceptance requirements. The approval count is not the total number of review records. It is the number of distinct eligible reviewers whose latest applicable decision is an approval of the current pull request head.

The evaluation follows these rules:

1. The reviewer must be eligible and must not be the pull request author.
2. Only the latest decision by that reviewer is considered.
3. The decision must apply to the current source commit.
4. Dismissed approvals do not count.
5. The number of qualifying reviewers must meet the target branch's required approval count.

A new source commit makes previous head-specific approvals stale in these models. A dismissed approval also stops contributing to eligibility. A later valid approval can replace an earlier request for changes.

The required approval count is configurable. A policy requiring two approvals cannot be satisfied by two approval events from the same reviewer. It requires two distinct eligible reviewers.

Production hosting systems may offer more detailed policies for code-owner approval, stale-approval dismissal, reviewer permissions, approval of the latest push, and administrative exceptions. Those rules must be configured and enforced explicitly in a real repository.

## Branch Protection

Branch protection governs changes to a target branch. It does not perform the review itself; it defines which conditions must be met before a proposed change can be merged.

The policy model includes:

| Rule | Effect |
|---|---|
| Required approvals | Enforces a minimum number of current eligible approvals |
| Required status checks | Requires specified checks to pass on the current source commit |
| Conversation resolution | Blocks merging while required review discussions remain unresolved |
| Linear history | Rejects merge-commit strategy when linear history is required |
| Direct-push restriction | Records the policy against bypassing the pull-request workflow |
| Force-push restriction | Records whether rewriting protected history is permitted |
| Branch-deletion restriction | Records whether protected branches may be deleted |
| Administrator bypass | Represents whether privileged users may bypass configured rules |

The sample programs evaluate approval, check, conversation, and linear-history rules. They model the other restrictions as policy attributes rather than fully implementing a hosting service's authorization system.

A real repository must enforce direct-push, force-push, deletion, and bypass restrictions at the hosting or server layer. A local eligibility function cannot prevent an external client from modifying a branch unless all write paths are controlled.

Administrator privileges should not be interpreted as an automatic exemption. Where bypass is enabled, it should be explicit, authorized, and auditable. The example merge services require an authorized merge actor and re-evaluate policy before changing the target branch.

## Functions and Validation

Functions make the governance rules reusable. Instead of repeating approval and check logic throughout the lifecycle, each implementation centralizes the decision in an eligibility operation.

The main function responsibilities are:

- Validate identifiers, branch relationships, reviewer eligibility, and policy values.
- Record review decisions and check results.
- Resolve current review decisions from review history.
- Compare the recorded branch state with the actual branch heads.
- Collect all merge blockers rather than stopping at the first failure.
- Apply the merge only when the eligibility result permits it.

Collecting blockers is useful during development because a contributor can see every currently unmet requirement. It also makes automated tests more precise.

### Python

The Python file uses dataclasses to model commits, branches, reviews, policies, and pull requests. Enums constrain lifecycle and review states. Methods group related behavior, while `merge_eligibility()` returns both a Boolean decision and a list of reasons.

The `run_checks()` function accepts callable checks, executes each independently, and converts exceptions into failed results. This prevents one failed check from hiding the outcomes of unrelated checks.

The example verifies that a pull request is initially blocked and becomes eligible after the required approvals and conversation resolution are recorded. Assertions verify the expected transition. The implementation is a simulation and does not connect to a remote repository.

### JavaScript

The JavaScript file uses Node.js standard-library facilities, including `EventEmitter`, Promises, and the `crypto` module. Events record important lifecycle actions, allowing consumers to react to submitted reviews and successful merges without coupling event listeners to the policy engine.

The check runner uses `Promise.all()` to execute independent checks concurrently. Each check records its own success or failure. The `Map` collections store checks and conversations, while `Set` collections represent reviewer eligibility and qualifying approvals.

The evaluator associates check results and reviews with a specific source head. This prevents a successful result for an earlier commit from being accepted as proof for a newer changeset.

### C++17

The C++ program models branches using STL vectors and uses maps and sets for check results, reviewer decisions, and approval counting. Enums represent the allowed lifecycle and decision states.

Branch insertion validates commit-parent relationships. The eligibility engine gathers blockers, and the merge operation advances the target branch only when the policy is satisfied.

The C++ implementation emphasizes explicit domain structures, deterministic policy evaluation, and exception-based failure handling. It does not use external libraries or require access to a remote Git server.

### Java 17

The Java implementation uses records for immutable data such as commits, review comments, status-check results, policies, and eligibility results. Mutable domain classes represent branches, reviews, and pull requests whose states change during the workflow.

The policy record validates its approval count and required-check names. The service-like methods separate review submission, check updates, lifecycle transitions, and merge evaluation. Streams and collections select each reviewer's latest decision and identify current approvals.

The model is suitable for practicing enterprise-style domain boundaries and validation. A production service would also need persistent storage, authentication, transaction management, concurrency controls, and an integration layer for a repository-hosting API.

### PostgreSQL

The SQL script creates a dedicated `repo_practice` schema and a relational model for repositories, members, branches, commits, pull requests, review requests, reviews, comments, status checks, protection policies, required checks, and eligibility audit records.

Primary keys, foreign keys, unique constraints, and check constraints enforce structural rules. Triggers validate pull-request branch relationships, reviewer eligibility, and the association between checks and the current source head.

The `evaluate_merge_eligibility()` function returns a decision and its blockers. It selects each reviewer's latest decision before counting approvals and checks whether required automated checks target the current head.

The `merge_pull_request()` function performs the final evaluation and updates the target branch and pull-request state in one transaction. Row locking helps prevent concurrent operations from silently applying a merge to an outdated target state. Production systems may require broader locking and serialization across reviews, checks, branch updates, and policy changes.

The sample transaction creates a repository, two branches, a protected target, an open pull request, review records, comments, and check results. It then resolves a conversation, records a new approval, evaluates eligibility, and attempts the merge.

## Automated Checks and Failure Handling

Status checks are separate from human review decisions. The example checks are named `build`, `tests`, and `security`, but each is an independent validation result.

A required check must exist, report success, and correspond to the current source head. Missing checks, pending results, failures, and stale results all block merging.

The source files demonstrate several other failure conditions:

- Invalid or missing identifiers.
- Duplicate commits.
- Self-review attempts.
- Unauthorized reviewer submissions.
- Invalid lifecycle transitions.
- Stale source or target branch state.
- Insufficient approvals.
- Unresolved conversations.
- Unsupported merge strategies.
- Invalid approval-policy values.

The SQL constraints and triggers enforce important invariants close to the data. Application-level checks remain necessary because not every business rule can be expressed safely as a simple constraint.

## Running the Examples

| File | Runtime | Execution |
|---|---|---|
| Python | Python 3.10 or later | Run the script directly |
| JavaScript | Node.js 18 or later | Run the file with Node.js |
| C++17 | C++17-compatible compiler | Compile and run the program |
| Java | Java 17 or later | Compile `RepositoryGovernance.java` and run `RepositoryGovernance` |
| PostgreSQL | PostgreSQL with PL/pgSQL | Execute the SQL script in a database where the executing role can create schemas, tables, functions, and triggers |

The Python, JavaScript, C++, and Java programs run independently. The SQL script is intended for a PostgreSQL database and creates its own schema. Run it in a disposable practice database if you do not want the sample records to remain.

## Design Limitations

These examples are educational domain models, not replacements for a production repository-hosting platform.

The language implementations use in-memory state, simplified commit identifiers, and limited lifecycle rules. They do not fetch real Git history, calculate merge conflicts, execute CI pipelines, authenticate users, or prevent external branch modifications.

The SQL implementation stores a relational representation of repository state. Its sample merge workflow provides transaction boundaries and locking for the pull-request and target-branch rows, but a production design must also coordinate concurrent review changes, status-check updates, policy modifications, and external Git operations.

The most important design principle is that eligibility is a decision derived from current state, not a permanent property of a pull request. Branch changes, new review decisions, dismissed approvals, check failures, and unresolved conversations can change whether a merge is permitted.
