# Python Packages and Dependency Management

## 1. Technical Scope

Python packages provide reusable functionality that can be imported into applications. They are distributed through package repositories and installed into Python environments.

The Python package ecosystem includes:

- Package creation and distribution.
- Package repositories and indexes.
- Package installation and removal.
- Dependency declaration and resolution.
- Version constraints and compatibility.
- Virtual environments.
- Package metadata.
- Dependency lock files.
- Security and license auditing.
- Reproducible application environments.

The implementations model a package-management system with repository validation, dependency resolution, installation controls, and governance.

## 2. Python Package Fundamentals

A Python module is an individual Python file containing reusable code.

A package is a collection of related modules organized into a directory structure. Packages commonly provide an `__init__.py` file, although Python also supports namespace packages.

A typical package structure is:

    analytics_project/
        pyproject.toml
        README.md
        src/
            analytics_project/
                __init__.py
                processing.py
                validation.py
        tests/
            test_processing.py

### Modules and packages

| Concept | Description |
|---|---|
| Module | A Python source file |
| Package | A collection of related modules |
| Subpackage | A package inside another package |
| Namespace package | A package whose portions may exist across multiple directories |
| Distribution | An installable package artifact |
| Wheel | A built distribution in `.whl` format |
| Source distribution | An archive containing source files |
| Dependency | Another distribution required by a package |

Import names and distribution names are not always identical. A distribution may provide several importable modules, and multiple distributions may use similar import names.

## 3. Python Package Ecosystem

The package ecosystem contains several distinct components.

| Component | Purpose |
|---|---|
| PyPI | Public Python package index |
| pip | Python package installer |
| venv | Standard-library virtual environment creation |
| ensurepip | Bootstraps pip where available |
| pyproject.toml | Project configuration and build metadata |
| setuptools | Package build backend |
| Hatchling | Package build backend |
| Poetry | Dependency and project management |
| uv | Python package and project management |
| wheel | Built distribution format |
| build | Frontend for building distributions |

These components have different responsibilities. PyPI stores package distributions and metadata, while pip installs distributions into a Python environment.

## 4. Package Installation

The standard package installer is pip.

Common operations include:

| Command | Operation |
|---|---|
| `python -m pip --version` | Display pip version |
| `python -m pip install numpy` | Install a package |
| `python -m pip install pandas` | Install a data analysis package |
| `python -m pip uninstall numpy` | Remove a package |
| `python -m pip list` | List installed distributions |
| `python -m pip show pandas` | Display package metadata |
| `python -m pip freeze` | Display installed distribution versions |
| `python -m pip check` | Check installed dependency compatibility |
| `python -m pip install --upgrade requests` | Upgrade a package |
| `python -m pip install -r requirements.txt` | Install declared requirements |

Using `python -m pip` associates pip with the selected Python interpreter. This reduces confusion when multiple Python installations exist.

## 5. Virtual Environments

A virtual environment provides an isolated installation location for Python packages.

Without isolation, projects may interfere with each other by requiring different package versions.

Example environment structure:

    project/
        .venv/
        requirements.txt
        pyproject.toml
        src/

Creation:

`python -m venv .venv`

Windows PowerShell activation:

`.\.venv\Scripts\Activate.ps1`

Windows Command Prompt activation:

`.venv\Scripts\activate.bat`

Linux and macOS activation:

`source .venv/bin/activate`

Verification:

`python -m pip list`

Deactivation:

`deactivate`

A virtual environment isolates installed Python packages. It does not completely isolate the operating system, native libraries, environment variables, or all external system dependencies.

## 6. Package Metadata and pyproject.toml

Modern Python projects commonly use `pyproject.toml` for project metadata and build configuration.

Important metadata includes:

- Project name.
- Project version.
- Description.
- Python version requirements.
- Runtime dependencies.
- Optional dependencies.
- Build-system requirements.
- Build backend.
- Entry points.
- License information.

The distinction between runtime dependencies and build-system requirements is important.

Runtime dependencies are needed by the installed application. Build-system requirements are needed to produce a distribution.

PEP 517 defines a standardized build-backend interface. PEP 518 defines the build-system requirements declaration.

PEP 621 defines standardized project metadata in `pyproject.toml`.

## 7. Package Versioning

Python distributions commonly use versions following the rules defined by PEP 440.

A simple version contains:

`MAJOR.MINOR.PATCH`

For example:

- `1.0.0`
- `1.2.0`
- `2.1.4`

Version components communicate different release changes.

| Component | Common interpretation |
|---|---|
| Major | Significant compatibility changes |
| Minor | New functionality |
| Patch | Bug fixes |

This table describes a common release convention. PEP 440 defines Python version syntax and comparison behavior, rather than requiring every project to follow this release convention.

Version constraints control which releases are acceptable.

| Constraint | Meaning |
|---|---|
| `==2.1.0` | Exact version |
| `!=2.1.0` | Exclude a version |
| `>=2.0.0` | Minimum version |
| `<=2.5.0` | Maximum version |
| `>2.0.0` | Greater than a version |
| `<3.0.0` | Lower than a version |
| `~=2.1` | Compatible release constraint |

The executable examples implement a deliberately restricted three-component version model. They do not implement the complete PEP 440 specification, including pre-releases, post-releases, development releases, epochs, and local versions.

## 8. Dependency Management

A dependency is a package required by another package.

Consider this dependency graph:

    analytics-toolkit
        |
        +---- pandas
        |       |
        |       +---- numpy
        |
        +---- requests

The installation order must respect dependencies:

1. numpy
2. pandas
3. requests
4. analytics-toolkit

A dependency resolver identifies compatible package releases and constructs an installation order.

### Dependency resolution mechanisms

The Python implementation uses depth-first traversal.

It maintains:

- A visited set to avoid repeated processing.
- An active set to detect circular dependencies.
- An ordered list to preserve dependency-first installation order.

A cycle such as:

    package-a -> package-b
         ^          |
         |__________|

must be rejected.

The resolver demonstrates basic graph traversal. It does not implement a complete production dependency solver.

Real package resolution must consider the combined constraints of all dependency paths, environment markers, platform compatibility, extras, pre-releases, and transitive version conflicts.

## 9. Requirements Files and Lock Files

A requirements file commonly declares package installation requirements.

`requirements.txt` is widely used for dependency installation.

A lock file records selected dependency versions for repeatable environment reconstruction.

| Requirements file | Lock file |
|---|---|
| Declares installation requirements | Records resolved package selections |
| May contain version ranges | Usually records exact versions |
| Can be maintained manually | Commonly generated by a dependency-management tool |
| Expresses requested dependencies | Records a resolution result |

The Python and JavaScript implementations generate a simplified JSON lock file.

The lock-file model records:

- Package name.
- Selected version.
- Direct dependency declarations.
- Lock-file format version.

A production lock file should also capture distribution hashes, environment markers, platform-specific selections, and relevant repository information.

A lock file improves reproducibility but does not guarantee identical behavior across different operating systems, Python interpreters, native libraries, or hardware.

## 10. Package Security

Package installation introduces supply-chain risks.

Important security concerns include:

- Malicious packages.
- Typosquatting.
- Dependency confusion.
- Compromised maintainers.
- Vulnerable package versions.
- Untrusted package indexes.
- Malicious installation scripts.
- Unverified distribution artifacts.
- License incompatibility.
- Dependency takeover.

### Security controls implemented

The examples implement a basic package security policy.

| Control | Purpose |
|---|---|
| Package blocklist | Reject prohibited package names |
| License allowlist | Restrict unacceptable licenses |
| Source validation | Reject untrusted repositories |
| Package status | Reject blocked or unavailable releases |
| Checksum metadata | Support distribution integrity verification |
| Installation validation | Prevent policy violations before state changes |

The checksum field in the examples represents package metadata. The implementations do not download distribution files or independently verify their cryptographic hashes.

A production implementation should verify the actual downloaded artifact against a trusted digest, use secure transport, restrict repository configuration, and maintain an auditable package inventory.

## 11. Python Implementation

The Python script implements a package-management simulation.

### Core components

| Component | Responsibility |
|---|---|
| `Version` | Validates and compares versions |
| `Dependency` | Represents package requirements |
| `Package` | Stores package metadata |
| `PackageRepository` | Maintains available releases |
| `DependencyResolver` | Resolves dependency relationships |
| `SecurityAuditor` | Evaluates package security rules |
| `Environment` | Tracks installed distributions |
| `save_lock_file` | Writes dependency information |
| `load_lock_file` | Validates lock-file contents |

### Important implementation decisions

Dataclasses provide structured package metadata.

Enums restrict package status values.

Sets detect repeated dependencies and circular dependency chains.

Dictionaries provide efficient package lookup.

Exceptions distinguish package validation, dependency, security, and installation failures.

The installation process checks the complete package collection before modifying environment state.

The lock-file writer uses a temporary file followed by replacement to reduce the risk of leaving partially written lock files.

### Execution

`python packages.py`

Generate:

`package-lock.json`

Validate an existing lock file:

`python packages.py --lock package-lock.json`

The implementation uses the standard library and does not require pip installation of additional dependencies.

## 12. JavaScript Implementation

The JavaScript implementation provides an event-driven package-management model using Node.js.

### Core components

| Component | Responsibility |
|---|---|
| `PackageRecord` | Package metadata |
| `Registry` | Release lookup and selection |
| `Resolver` | Dependency graph traversal |
| `SecurityPolicy` | Package policy evaluation |
| `PackageEnvironment` | Installation state |
| `EventEmitter` | Installation lifecycle events |
| `createLockFile` | Asynchronous lock-file creation |

The implementation uses:

- Maps for package registry and installed state.
- Sets for policy evaluation and graph traversal.
- Promises and asynchronous file operations.
- Private class fields for internal state.
- Event-driven installation notifications.
- Copy-on-write state replacement.

### Event lifecycle

    installation:started
             |
             v
      Policy evaluation
             |
        +----+----+
        |         |
      Passed    Failed
        |         |
        v         v
     Commit    Error event
        |
        v
    installation:completed

The installation operation reports success only after its state transition completes.

### Execution

Save the file as `packages.js`.

`node packages.js`

The implementation requires Node.js 18 or later and uses no third-party npm packages.

## 13. C++17 Implementation

The C++ program implements a package-governance engine.

### Core components

| Component | Responsibility |
|---|---|
| `Version` | Version comparison |
| `Dependency` | Dependency declaration |
| `Package` | Package domain model |
| `PackageRegistry` | Release management |
| `DependencyResolver` | Dependency ordering |
| `SecurityPolicy` | Package eligibility |
| `PackageEnvironment` | Installation state |

The implementation uses STL maps, sets, vectors, sorting algorithms, and exceptions.

### Transactional installation

The environment copies its existing installation state into a candidate map.

It validates all packages and version conflicts against the candidate.

Only after successful validation does it replace the existing state.

This prevents partial in-memory installation when validation fails.

### Complexity

Let:

- V represent the number of package releases.
- E represent the number of dependency relationships.

Dependency traversal is approximately O(V + E) for a fixed release selection.

Sorting dependency lists adds sorting overhead.

Registry version lookup is efficient when package names are indexed, although the simplified implementation scans candidate releases for compatibility.

### Compilation

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic packages.cpp -o packages`

Execution:

`.\packages.exe`

The program uses no external libraries.

## 14. Java 17 Implementation

The Java implementation models enterprise-oriented package governance.

### Domain architecture

| Component | Responsibility |
|---|---|
| `Version` | Immutable version representation |
| `Dependency` | Dependency metadata |
| `PackageRecord` | Immutable package information |
| `PackageRepository` | Repository interface |
| `InMemoryRepository` | Repository implementation |
| `DependencyResolver` | Dependency resolution |
| `ReviewPolicy` | Enterprise policy evaluation |
| `InstallationService` | Controlled installation |

Java records provide immutable version and dependency values.

Interfaces separate repository behavior from its implementation.

Collections support registry indexing, policy evaluation, and installation management.

Streams provide filtering, sorting, and reporting operations.

The installation service uses synchronized methods and copy-on-write state preparation.

### Enterprise considerations

A production package-management service would require:

- User authentication.
- Role-based authorization.
- Repository access controls.
- Audit logging.
- Transactional persistent storage.
- Concurrent installation coordination.
- Artifact verification.
- Policy versioning.
- Environment-specific compatibility rules.

The provided Java program models the domain and its business rules without connecting to an external package repository.

### Compilation

`javac Main.java`

Execution:

`java Main`

The program requires Java 17 and uses no third-party dependencies.

## 15. PostgreSQL Implementation

The SQL implementation models package management using relational database structures.

### Database entities

| Table | Purpose |
|---|---|
| `packages` | Package identity and metadata |
| `package_releases` | Published package versions |
| `package_dependencies` | Dependency relationships |
| `package_environments` | Isolated application environments |
| `package_installations` | Installation history |
| `package_policies` | Security and licensing rules |
| `package_audits` | Package policy evaluation records |

### Relational structure

    packages
       |
       +---- package_releases
                  |
                  +---- package_dependencies
                  |
                  +---- package_installations
                  |
                  +---- package_audits

    package_environments
       |
       +---- package_installations
       |
       +---- package_audits

    package_policies
       |
       +---- package_audits

### Integrity controls

Primary keys identify records.

Foreign keys preserve relationships between packages, releases, environments, and dependencies.

Unique constraints prevent duplicate package releases and repeated dependencies.

Check constraints validate package names, version components, checksums, and installation-state consistency.

Triggers prevent direct self-dependencies and invalid installation transitions.

Indexes support release lookup, dependency retrieval, installation reporting, and audit history queries.

### Recursive dependency queries

A recursive common table expression retrieves transitive dependencies.

The query maintains a visited identifier array to prevent revisiting packages within the same traversal path.

The example demonstrates recursive dependency discovery. It does not perform complete version-constraint resolution or guarantee a globally consistent dependency solution.

### Transaction handling

The `install_package` procedure:

1. Locks the target environment.
2. Evaluates the selected package against an active policy.
3. Records the audit result.
4. Rejects packages that violate policy.
5. Creates an installation record when approved.

The example uses transactional SQL execution to preserve database consistency.

### Execution

Save the SQL as `packages.sql`.

Run:

`psql -U postgres -d package_management -f packages.sql`

The script creates its schema, tables, constraints, functions, triggers, procedures, indexes, views, and sample records.

## 16. Installation and Resolution Failure Conditions

| Failure | Expected handling |
|---|---|
| Invalid package name | Reject package metadata |
| Invalid version | Reject version declaration |
| Missing package | Stop dependency resolution |
| Incompatible version | Reject dependency selection |
| Circular dependency | Stop graph traversal |
| Blocked package | Reject installation |
| Unapproved license | Reject installation |
| Untrusted source | Reject installation |
| Conflicting installed version | Reject state modification |
| Dependency still required | Prevent package removal |
| Corrupted lock file | Reject lock-file loading |
| Failed database policy | Roll back installation transaction |

## 17. Performance and Scalability

Package management can become expensive when applications contain large dependency graphs.

Important performance considerations include:

- Indexing package names.
- Indexing package versions.
- Caching repository metadata.
- Avoiding repeated dependency traversal.
- Deduplicating package releases.
- Reusing verified artifact metadata.
- Separating package downloads from dependency resolution.
- Limiting recursive graph depth.
- Using transaction boundaries appropriately.
- Avoiding unnecessary installation-state updates.

A production dependency solver may need constraint propagation, backtracking, conflict analysis, and platform-specific dependency selection.

The implementations deliberately use simpler algorithms to make the core package-management mechanisms explicit.

## 18. Implementation Comparison

| Dimension | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Package metadata | Dataclasses | Classes | Structs | Records and classes | Tables |
| Repository | Dictionary | Map | Map | HashMap | Relational tables |
| Dependencies | Lists | Arrays | Vectors | Lists | Foreign keys |
| Version validation | Custom parser | Custom parser | Comparator | Comparable | Check constraints |
| Resolution | DFS | DFS | DFS | DFS | Recursive CTE |
| Security | Auditor | Policy | Policy engine | Review policy | Policy function |
| Installation | Environment | Event-driven service | Transactional state | Installation service | Stored procedure |
| Persistence | JSON | JSON | In-memory | In-memory | PostgreSQL |

The implementations share a common domain but use different programming models and engineering approaches.

## 19. Limitations

These examples implement a controlled package-management simulation rather than a replacement for pip, PyPI, uv, Poetry, or a production dependency solver.

They do not implement:

- Complete PEP 440 version parsing.
- Full dependency constraint solving.
- Package artifact downloads.
- Wheel extraction.
- Native extension compilation.
- Python interpreter compatibility evaluation.
- Operating-system environment markers.
- Editable installations.
- Package signature verification.
- Complete vulnerability database integration.
- Actual virtual environment creation.
- Complete PEP 517 build workflows.

The simplified version comparators and lock-file formats are educational domain models. Production systems should use established Python packaging standards and trusted package-management tooling.
