# Managing Project Dependencies

## 1. Domain and Engineering Objectives

Project dependency management is the controlled identification, selection, resolution, installation, updating, validation, and governance of external software components used by a project.

A dependency can be a library, framework, runtime package, development utility, compiler component, or another software module required by an application.

Dependency management is not limited to downloading packages. It requires maintaining a consistent and reproducible software environment while controlling compatibility, security, licensing, availability, and operational risk.

The implementations model an enterprise repository containing:

- FastAPI
- HTTPX
- Pydantic
- Cryptography

The examples demonstrate how dependency changes move from an inventory through compatibility evaluation, automated checks, review, approval, repository enforcement, and controlled integration.

## 2. Dependency Concepts

### 2.1 Direct and transitive dependencies

A direct dependency is explicitly declared by the project.

A transitive dependency is required by another dependency.

For example:

    Enterprise Application
        |
        +-- FastAPI
        |     |
        |     +-- HTTPX
        |     |
        |     +-- Pydantic
        |
        +-- Cryptography

FastAPI is directly required by the application in this example. HTTPX and Pydantic are represented as its prerequisites.

The distinction matters because an application may not directly control the versions of all packages installed in its environment.

A change to one direct dependency can alter several transitive dependencies. Dependency resolution must therefore consider the complete dependency graph.

### 2.2 Semantic versioning

The implementations use three-component semantic versions:

`MAJOR.MINOR.PATCH`

| Component | Meaning | Typical compatibility implication |
|---|---|---|
| MAJOR | Major release | May introduce incompatible changes |
| MINOR | New functionality | Intended to preserve backward compatibility |
| PATCH | Bug or security fixes | Intended to preserve compatibility |

Examples:

- `2.8.2`
- `2.9.2`
- `3.0.0`

A version comparison must compare numeric components rather than treating version strings as ordinary text.

For example, `2.10.0` is newer than `2.9.0`, even though ordinary lexical string comparison can produce the wrong ordering.

The four-component and prerelease extensions of the full Semantic Versioning specification are outside the implemented version model.

### 2.3 Version constraints

A dependency declaration may specify:

- Current installed version.
- Minimum permitted version.
- Maximum permitted version.
- Exact version.
- Compatible version range.

The implementations maintain minimum and optional maximum boundaries.

A candidate update must be newer than the installed version and remain within the permitted range.

A real package manager must also interpret the dependency manifest's complete version-expression syntax, including prereleases and platform-specific markers.

### 2.4 Dependency resolution

Dependency resolution determines a compatible set of package versions satisfying all declared requirements.

The dependency graph is represented as a directed graph.

An edge from package A to package B means that A requires B.

The resolver must:

1. Identify all required packages.
2. Verify that every referenced package exists.
3. Detect circular relationships.
4. Establish prerequisite ordering.
5. Reject inconsistent dependency states.

The Python and Java implementations use depth-first traversal. JavaScript uses an event-driven repository model with depth-first graph validation. C++17 uses a recursive graph traversal.

The SQL implementation uses recursive common table expressions for dependency traversal.

### 2.5 Dependency cycles

Consider:

    Package A -> Package B
    Package B -> Package C
    Package C -> Package A

This graph contains a cycle.

A topological ordering cannot be produced because no valid prerequisite-first installation order exists.

Cycle detection prevents a dependency resolver from accepting an inconsistent graph.

### 2.6 Dependency conflicts

A conflict occurs when two or more packages impose incompatible requirements on the same dependency.

For example:

- Package A requires Library X version 2.x.
- Package B requires Library X version 3.x.
- The project requires both packages.

The resolver must determine whether a compatible combination exists.

The implementations enforce individual version boundaries and graph integrity. They do not implement a complete SAT-based or backtracking package solver.

A production resolver requires more advanced constraint-solving behavior.

## 3. Dependency Inventory and Governance

### 3.1 Inventory management

An inventory records the dependencies used by a repository.

The model includes:

| Attribute | Purpose |
|---|---|
| Package name | Identifies the component |
| Current version | Records the selected release |
| Minimum version | Defines the lower permitted boundary |
| Maximum version | Defines an optional upper boundary |
| Dependency type | Classifies runtime, development, optional, or peer dependencies |
| Direct dependency | Distinguishes declared from transitive packages |
| License | Identifies the distribution license |
| Registry | Records the package source |
| Vulnerability count | Records known security exposure |

The Python and JavaScript implementations store the inventory in dictionaries or maps.

C++17 uses ordered associative containers.

Java uses an encapsulated repository service.

PostgreSQL stores the inventory in the `dependencies` relation.

### 3.2 Dependency sources

A package may originate from:

- A public package registry.
- A private enterprise registry.
- An internal artifact repository.
- A version-controlled source repository.

The source must be controlled because package-name similarity does not establish package authenticity.

A production deployment should verify package provenance, registry configuration, signatures where supported, and artifact integrity.

### 3.3 Lockfiles

A lockfile records resolved dependency versions.

Its purpose is reproducibility.

A manifest expresses dependency requirements, while a lockfile records the selected dependency graph.

These are different responsibilities.

| Manifest | Lockfile |
|---|---|
| Declares dependency requirements | Records resolved versions |
| Expresses version constraints | Records selected versions |
| Supports dependency maintenance | Supports reproducible installation |
| Usually maintained directly | Usually generated by a package manager |

The Python implementation generates a JSON lockfile with an integrity digest.

The JavaScript implementation generates an equivalent structured document and supports atomic file replacement.

The SQL implementation stores lockfile metadata, including the content hash and dependency count.

The C++17 implementation concentrates on graph resolution and governance rather than filesystem lockfile serialization.

The Java implementation concentrates on enterprise domain modeling and repository state transitions.

A digest detects accidental changes to the serialized content. It does not establish artifact authenticity or provide a cryptographic signature over a trusted release.

## 4. Dependency Security and License Compliance

### 4.1 Vulnerability management

A dependency can introduce security weaknesses even when the application code is correct.

A dependency audit should consider:

- Known vulnerabilities.
- Severity.
- Affected versions.
- Available remediation versions.
- Exploitability.
- Exposure in the deployed application.
- Whether the dependency is actually reachable at runtime.

The SQL model includes a `vulnerability_findings` table containing vulnerability identifiers, severity, affected version information, remediation versions, and verification status.

The governance services enforce a configurable vulnerability threshold.

The demonstration policy rejects packages with vulnerabilities above the permitted threshold.

A production security process should use an authoritative vulnerability database and verify whether a finding applies to the installed package version.

### 4.2 License compliance

Open-source licenses impose different conditions on redistribution, modification, attribution, and distribution.

The implementations use an allowlist containing:

- MIT
- Apache-2.0
- BSD-3-Clause

A license allowlist is a simplified policy mechanism.

Production license governance must consider the exact license text, dependency distribution model, transitive obligations, exceptions, and organizational legal requirements.

### 4.3 Supply-chain controls

A reliable dependency supply chain should enforce:

- Trusted package registries.
- Version pinning where appropriate.
- Lockfile verification.
- Artifact integrity checks.
- Vulnerability scanning.
- License scanning.
- Dependency provenance.
- Controlled update permissions.
- Auditable changes.

A package update should not automatically be considered safe merely because its version is newer.

## 5. Dependency Update Lifecycle

A dependency update is a controlled repository change.

The workflow implemented in the source files is:

    Inventory
       |
       v
    Discover Available Versions
       |
       v
    Validate Version Constraints
       |
       v
    Generate Update Plan
       |
       v
    Create Source Branch
       |
       v
    Open Pull Request
       |
       v
    Execute Automated Checks
       |
       v
    Code Review
       |
       v
    Approval Decisions
       |
       v
    Branch Protection Evaluation
       |
       v
    Merge Eligibility
       |
       v
    Merge and Update Inventory
       |
       v
    Regenerate Lockfile

The update plan identifies packages that can be upgraded without violating the modeled version constraints.

An update may be rejected when:

- The package does not exist in the inventory.
- The proposed version is not newer.
- The proposed version exceeds the maximum permitted version.
- A dependency is missing.
- The dependency graph contains a cycle.
- A license violates policy.
- A vulnerability threshold is exceeded.

## 6. Pull Request Management

A Pull Request is a repository workflow for proposing changes from a source branch into a target branch.

For dependency management, the changeset represents proposed package-version changes.

### 6.1 Pull Request mechanics

The repository workflow uses:

| Element | Responsibility |
|---|---|
| Source branch | Holds proposed dependency changes |
| Target branch | Contains the existing repository state |
| Changeset | Describes proposed package modifications |
| Commits | Record changes made to the source branch |
| Review requests | Assign reviewers |
| Status checks | Record automated validation results |
| Merge strategy | Determines how changes enter the target branch |

The source branch is not the target branch.

A proposed dependency update does not modify the target branch merely because a Pull Request has been opened.

The target branch changes only after a permitted merge.

### 6.2 Pull Request states

The implementations model:

| State | Meaning |
|---|---|
| Draft | Proposal is not ready for normal review or merging |
| Open | Proposal is active |
| Merged | Changes have entered the target branch |
| Closed | Proposal was closed without merging |

A closed unmerged Pull Request can be reopened when repository workflow permits it.

A merged Pull Request should not be treated as an unmerged proposal.

### 6.3 Synchronizing the base branch

A source branch can become outdated while development continues on the target branch.

Synchronization brings the source branch up to date with the target branch.

A repository may require the source branch to be synchronized before merging.

The implementations represent synchronization through an explicit state field.

### 6.4 Merge conflicts

A merge conflict occurs when changes cannot be combined automatically.

Dependency conflicts may occur when:

- Another update modifies the same package.
- The manifest is modified concurrently.
- The lockfile changes independently.
- Two branches introduce incompatible version requirements.

A conflicting Pull Request must be reconciled before merge eligibility is granted.

### 6.5 Merge strategies

| Strategy | Behavior |
|---|---|
| Merge commit | Preserves branch history and creates a merge commit |
| Squash | Combines proposed changes into one commit |
| Rebase | Replays commits onto the updated target history |

The Python, JavaScript, C++17, and Java implementations model the selected strategy as part of the merge operation.

The PostgreSQL model records the selected strategy and resulting merge identifier.

The examples do not implement Git's underlying object database or actual branch-ref manipulation.

## 7. Code Review

Code Review evaluates the technical quality and risk of proposed dependency changes.

It is distinct from the Pull Request itself.

A Pull Request provides the proposal workflow. Code Review provides the human evaluation of the proposed changes.

### 7.1 Review criteria

Dependency updates should be examined for:

- Version compatibility.
- Breaking changes.
- Deprecated APIs.
- Runtime behavior changes.
- Security improvements.
- New transitive dependencies.
- License changes.
- Performance effects.
- Configuration changes.
- Migration requirements.
- Test coverage.
- Lockfile consistency.

A reviewer should examine the actual dependency changes rather than approve a version increase solely because automated checks passed.

### 7.2 Review states

| Review state | Meaning |
|---|---|
| Approved | Reviewer accepts the reviewed changes |
| Changes requested | Reviewer identifies issues requiring correction |
| Commented | Reviewer provides observations without approving |
| Dismissed | A previous review decision is no longer active |

### 7.3 Inline comments and discussions

An inline comment refers to a particular file or line.

Examples include:

- Questioning an unexpected version upgrade.
- Identifying a compatibility issue.
- Requesting a migration test.
- Identifying a new transitive package.

Review conversations can remain open until the issue has been addressed.

The Python and JavaScript implementations maintain conversation-resolution state.

The Java and C++ implementations model review decisions and review-related eligibility conditions.

The PostgreSQL implementation stores individual comments and discussion records separately.

### 7.4 Review failure modes

Common failures include:

- Reviewing an outdated commit.
- Approving without inspecting the dependency changeset.
- Ignoring transitive dependency changes.
- Treating a comment as an approval.
- Leaving important discussions unresolved.
- Reviewing without the necessary repository role.

A review decision must be associated with the commit that was examined.

## 8. Approval Management

An approval is a formal review decision.

It indicates that an eligible reviewer accepts the reviewed changes according to the repository's review process.

Approval is not the same as merge permission.

### 8.1 Reviewer eligibility

A repository can restrict approval privileges to authorized members.

The Java implementation models reviewer eligibility through repository roles and an enterprise review service.

The PostgreSQL implementation uses repository membership records and a trigger to reject reviews from inactive or ineligible members.

### 8.2 Required approvals

A repository can require a minimum number of distinct approvals.

The demonstration policy requires two approvals.

Approvals from the same reviewer must not be counted multiple times toward the requirement.

The implementations use distinct reviewer identities when calculating approval counts.

### 8.3 Stale approvals

An approval may become stale when additional commits change the proposed changeset.

For example:

1. A reviewer approves version 2.8.2.
2. A developer changes the proposed version to 2.9.2.
3. The original reviewer has not inspected the new changes.
4. The previous approval is dismissed or excluded from the current approval count.

The Python, JavaScript, and Java implementations demonstrate stale approval handling.

The SQL implementation associates reviews with the reviewed commit hash and counts only approvals associated with the current source commit.

### 8.4 Approval and merge eligibility

Approval establishes a review decision.

It does not establish that:

- Security checks passed.
- License requirements were satisfied.
- Required conversations were resolved.
- The source branch is synchronized.
- The lockfile exists.
- The target branch's protection rules are satisfied.

These conditions are evaluated separately.

## 9. Branch Protection

Branch Protection is the repository-level enforcement mechanism that controls changes entering important branches.

It is distinct from Pull Request workflow, Code Review, and approval decisions.

### 9.1 Protected branches

A branch such as `main` may be protected because it represents a stable integration point.

The repository can require that all changes pass defined governance conditions.

### 9.2 Required status checks

Status checks are automated results associated with a particular commit.

The demonstration includes:

| Check | Purpose |
|---|---|
| Unit tests | Detect functional regressions |
| Security scan | Identify dependency vulnerabilities |
| License audit | Identify licensing violations |
| Dependency resolution | Verify dependency graph consistency |

Possible states are:

- Pending
- Passed
- Failed

A successful result for an older commit must not automatically validate a newer commit.

This is why the implementations associate check results with commit identifiers.

### 9.3 Direct-push restrictions

Direct-push restrictions prevent ordinary users from modifying protected branches without following the prescribed integration workflow.

The repository model represents this as a policy setting.

### 9.4 Force-push restrictions

A force push can rewrite branch history.

Protected repositories commonly restrict this operation to prevent accidental loss of commits or disruption of shared development history.

### 9.5 Branch deletion restrictions

Deletion restrictions prevent important repository branches from being removed without authorization.

### 9.6 Conversation requirements

A repository may require all review discussions to be resolved before merging.

A resolved conversation means the discussion has been addressed according to the review workflow. It does not independently prove that the proposed code is correct.

### 9.7 Linear history

Linear-history requirements restrict merge operations that introduce non-linear commit histories.

A repository can configure permitted merge strategies according to its history policy.

### 9.8 Administrator behavior and bypass

Some repository platforms permit administrators or designated roles to bypass selected protection conditions.

Bypass must be explicitly governed.

The implementations model an administrator-bypass policy attribute but do not implement a complete identity-based bypass authorization service.

A production system must record the bypass actor, justification, affected policy, and resulting repository state.

## 10. Merge Eligibility

Merge eligibility is the combined result of repository and proposal validation.

The model distinguishes:

| Concern | Meaning |
|---|---|
| Proposed changes | Requested dependency modifications |
| Branch state | Actual source and target branch positions |
| Review decisions | Human evaluation results |
| Approvals | Formal reviewer decisions |
| Status checks | Automated validation results |
| Protection policy | Repository-level enforcement requirements |
| Merge eligibility | Whether all required conditions are satisfied |

The eligibility evaluation uses the following logical conditions:

    PR is open
        AND PR is not draft
        AND no merge conflicts
        AND source branch synchronized
        AND required conversations resolved
        AND required status checks passed
        AND sufficient eligible approvals
        AND dependency policy satisfied
        AND lockfile requirement satisfied

A failure in any required condition blocks merging.

This separation is important because a Pull Request can be technically valid while still being prohibited by repository policy.

## 11. Implementation Architecture

### 11.1 Python

The Python implementation provides a repository workflow simulator.

Core structures:

| Structure | Responsibility |
|---|---|
| `Version` | Semantic version parsing and comparison |
| `Dependency` | Dependency metadata and validation |
| `Policy` | Configurable governance requirements |
| `PullRequest` | Proposed changes and workflow state |
| `Review` | Reviewer decision and commit association |
| `DependencyManager` | Repository operations and eligibility evaluation |

The implementation uses:

- Dataclasses for domain objects.
- Enums for workflow states.
- Dictionaries for dependency and repository indexes.
- Sets for license and approval policies.
- Deques for dependency ordering.
- SHA-256 for deterministic demonstration identifiers and lockfile integrity.
- Atomic replacement for lockfile output.

The topological ordering algorithm has time complexity of:

`O(V + E)`

where V represents dependency nodes and E represents dependency relationships, excluding sorting overhead.

### 11.2 JavaScript

The JavaScript implementation emphasizes asynchronous validation and event-driven repository operations.

Core structures:

| Structure | Responsibility |
|---|---|
| `Dependency` | Validated package representation |
| `Repository` | Repository state and workflow operations |
| `Map` | Dependency, review, and status indexes |
| `Set` | Policy and merge-strategy membership |
| `EventEmitter` | Repository workflow notifications |
| `Promise.all` | Concurrent automated status checks |

The implementation supports:

- Asynchronous status checks.
- Event notifications.
- Dependency graph traversal.
- Pull Request lifecycle operations.
- Approval validation.
- Stale approval handling.
- Atomic lockfile replacement.
- Merge eligibility evaluation.

Concurrent checks are independent operations, so they can execute using promises.

The implementation converts check exceptions into failed check states rather than silently treating them as successful results.

### 11.3 C++17

The C++ implementation emphasizes explicit domain modeling and deterministic governance evaluation.

Core structures:

- `Version`
- `Dependency`
- `Review`
- `PullRequest`
- `ProtectionPolicy`
- `GovernanceEngine`

It uses:

- `std::map` for ordered repository state.
- `std::set` for license and approval validation.
- `std::vector` for dependency relationships and evaluation results.
- `std::function` for recursive graph traversal.
- Enumerations for review, status, and merge states.
- Exceptions for invalid state transitions.

The implementation validates the complete merge conditions before modifying the dependency inventory.

This reduces the risk of partially applying an invalid dependency update.

### 11.4 Java 17

The Java implementation emphasizes enterprise service boundaries and immutable domain data.

Core components:

| Component | Responsibility |
|---|---|
| `Version` record | Immutable version representation |
| `Dependency` record | Validated dependency data |
| `ReviewPolicy` | Approval and conversation requirements |
| `ProtectionPolicy` | Repository enforcement configuration |
| `DependencyRepository` | Encapsulated inventory management |
| `DependencyResolver` | Dependency graph validation |
| `GovernanceScanner` | License and vulnerability assessment |
| `DependencyGovernanceService` | Workflow and merge orchestration |

Records provide immutable value-oriented structures.

The repository service centralizes dependency updates.

The governance service coordinates independent policy components.

The `apply` operation validates all proposed dependency changes before updating the inventory.

This design reduces direct state manipulation across the enterprise domain.

### 11.5 PostgreSQL

The database implementation represents dependency governance as a relational workflow.

Important relations include:

| Table | Purpose |
|---|---|
| `repositories` | Repository metadata |
| `repository_members` | User roles and eligibility |
| `branches` | Source and target branch state |
| `dependencies` | Package inventory |
| `dependency_relationships` | Direct graph edges |
| `vulnerability_findings` | Security findings |
| `license_policies` | Allowed and prohibited licenses |
| `dependency_updates` | Proposed package upgrades |
| `pull_requests` | Proposed repository changes |
| `pull_request_changes` | Dependency changesets |
| `code_reviews` | Review decisions |
| `review_comments` | Individual review observations |
| `review_conversations` | Discussion resolution |
| `status_checks` | Automated validation results |
| `branch_protection_policies` | Repository enforcement |
| `required_status_checks` | Required automated checks |
| `dependency_lockfiles` | Lockfile metadata |
| `merge_evaluations` | Eligibility audit history |
| `repository_audit_log` | Repository operations |

The schema uses foreign keys, uniqueness constraints, check constraints, indexes, triggers, views, recursive CTEs, and a transactional merge procedure.

The merge procedure locks the Pull Request and affected dependency records before updating repository state.

It verifies that the current dependency versions still match the versions recorded when the changeset was created.

This prevents a concurrent update from silently overwriting a newer dependency state.

The procedure also records the merge decision and repository audit event.

## 12. Database Integrity and Performance

### 12.1 Referential integrity

Foreign keys ensure that reviews, changesets, status checks, and dependencies reference existing records.

Unique constraints prevent duplicate repository names, package declarations, and duplicate reviewer decisions for the same commit.

Check constraints enforce valid states and nonnegative numeric values.

### 12.2 Trigger-based validation

The dependency version trigger checks minimum and maximum version boundaries.

The review-membership trigger validates reviewer eligibility.

The conversation trigger maintains consistent resolution timestamps.

These mechanisms prevent invalid records from being accepted through ordinary database writes.

### 12.3 Recursive queries

Recursive CTEs traverse dependency relationships.

They are useful for identifying prerequisite packages and examining transitive dependency structures.

Graph traversal can become expensive when a repository contains many dependencies or highly connected relationships.

Indexes on relationship identifiers and repository identifiers support efficient joins.

### 12.4 Transaction handling

Dependency updates must be applied atomically.

The database procedure performs the merge within the calling transaction.

If a required condition fails, the operation raises an exception and the transaction must not be committed as a successful merge.

The application should treat database transaction failures as rejected repository operations.

### 12.5 Concurrent modifications

Two Pull Requests can independently propose updates to the same package.

The database procedure locks affected dependency rows and verifies the recorded previous version before applying the proposed version.

This is an optimistic state-validation check combined with transactional row locking.

It prevents a stale changeset from overwriting a concurrent dependency update.

## 13. Edge Cases and Failure Handling

| Failure | Expected handling |
|---|---|
| Invalid semantic version | Reject input |
| Duplicate dependency | Reject inventory insertion |
| Missing transitive dependency | Reject graph resolution |
| Circular dependency | Reject dependency graph |
| Version outside permitted range | Reject update |
| Prohibited license | Block governance evaluation |
| Excessive vulnerabilities | Block governance evaluation |
| Empty changeset | Reject Pull Request |
| Draft Pull Request | Prevent merge |
| Unresolved conversation | Block merge |
| Missing status check | Block merge |
| Failed status check | Block merge |
| Insufficient approvals | Block merge |
| Stale approval | Exclude from current approval count |
| Merge conflict | Require conflict resolution |
| Outdated source branch | Require synchronization |
| Concurrent dependency update | Reject stale changeset |
| Invalid merge strategy | Reject merge request |

Failure handling must preserve repository consistency.

A failed eligibility evaluation must not partially update dependency versions.

## 14. Security and Production Considerations

The implementations provide an educational governance model rather than a complete package-management platform.

A production dependency-management service requires further controls.

### Identity and authorization

- Authenticate repository users.
- Enforce role-based permissions.
- Separate review privileges from merge privileges.
- Restrict administrative bypass.
- Protect credentials and registry tokens.

### Supply-chain security

- Verify package provenance.
- Pin and verify dependency artifacts.
- Restrict untrusted package registries.
- Validate package signatures where supported.
- Monitor dependency namespace confusion.
- Detect malicious package updates.

### Security scanning

- Use vulnerability data with update timestamps.
- Evaluate affected-version ranges.
- Distinguish verified and unverified findings.
- Track remediation status.
- Reassess dependencies when new advisories appear.

### Reproducibility

- Preserve package-manager-native lockfiles.
- Record registry and artifact identities.
- Verify integrity during installation.
- Use controlled build environments.
- Maintain reproducible deployment artifacts.

### Auditability

- Record who requested an update.
- Record who reviewed and approved it.
- Preserve the reviewed commit identifier.
- Store status-check results.
- Record merge strategy.
- Record policy evaluation results.
- Preserve administrative bypass events.

### Operational reliability

- Handle registry outages.
- Retry transient network failures safely.
- Prevent duplicate update jobs.
- Avoid concurrent lockfile overwrites.
- Cache immutable package metadata.
- Monitor dependency-resolution performance.

## 15. Limitations of the Demonstration

The implementations deliberately model repository and dependency governance without attempting to reproduce the full behavior of a commercial package manager or hosted source-control platform.

Important boundaries include:

- Version handling covers stable three-component semantic versions.
- Complete package-manager constraint languages are not implemented.
- Dependency conflict resolution does not use SAT solving.
- The examples do not download or install actual packages.
- Vulnerability findings are modeled rather than retrieved from a live advisory service.
- License classification is based on configured policy identifiers.
- The lockfile formats are demonstration formats rather than package-manager-native formats.
- The C++ implementation does not implement persistent lockfile serialization.
- The JavaScript and Python examples use local repository state.
- The SQL model does not implement Git object storage.
- Branch synchronization and merge strategies are represented as governance states and operations.
- Administrator bypass is represented as policy configuration, not a complete authorization mechanism.

These boundaries separate the modeled management workflow from the implementation details of actual package registries, build systems, and source-control servers.

## 16. Practical Engineering Distinctions

The following mechanisms have separate responsibilities and should not be treated as interchangeable.

| Mechanism | Primary responsibility |
|---|---|
| Dependency manifest | Declares required packages and constraints |
| Dependency resolver | Finds compatible package versions |
| Dependency graph | Represents package relationships |
| Lockfile | Records resolved dependency state |
| Dependency scanner | Identifies security and license risks |
| Pull Request | Provides the workflow for proposing changes |
| Code Review | Evaluates the proposed changes |
| Approval | Records a formal review decision |
| Status checks | Record automated validation results |
| Branch Protection | Enforces repository-level conditions |
| Merge eligibility | Determines whether integration is permitted |
| Merge operation | Applies the accepted changes to the target branch |

The key architectural distinction is that dependency correctness, review quality, approval decisions, and repository merge enforcement are separate concerns.

A dependency update should enter the stable repository only when its proposed state has been validated and the repository's governance requirements have been satisfied.
