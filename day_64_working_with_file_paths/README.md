# Working with File Paths

## Scope

This project models filesystem paths as structured data rather than treating them as arbitrary strings. The five implementations demonstrate path construction, normalization, inspection, directory traversal, file operations, extension analysis, validation, security controls, and persistence of path metadata.

The implementations use:

| File | Perspective |
|---|---|
| Python | Object-oriented filesystem workflow using `pathlib` |
| JavaScript | Asynchronous Node.js filesystem operations |
| C++17 | Native filesystem and strongly typed path-management service |
| Java 17 | Enterprise-style service with explicit path policy objects |
| PostgreSQL | Relational model for repositories, filesystem nodes, policies, and operations |

The examples deliberately use temporary or managed roots so that destructive operations remain isolated from unrelated files.

## Core Path Concepts

A filesystem path identifies the location of a file or directory.

A path can contain several meaningful components:

| Component | Example |
|---|---|
| Root | `/` or `C:\` |
| Parent | `reports/2026` |
| Name | `report.csv` |
| Stem | `report` |
| Extension | `.csv` |
| Relative path | `reports/2026/report.csv` |
| Absolute path | `/srv/app/reports/2026/report.csv` |

A relative path is interpreted in relation to a current or explicitly selected root. An absolute path identifies a location independently of the caller's current directory.

The implementations prefer explicit managed roots because filesystem operations become easier to validate and audit when the allowed boundary is known.

## Joining Paths

Paths should be constructed with filesystem-aware operations rather than manually concatenating separators.

Python uses `pathlib.Path`:

`Path("reports") / "2026" / "report.csv"`

JavaScript uses Node's `path` module:

`path.join("reports", "2026", "report.csv")`

C++17 uses `std::filesystem::path`:

`fs::path("reports") / "2026" / "report.csv"`

Java uses `Paths.get`:

`Paths.get("reports", "2026", "report.csv")`

These mechanisms account for platform-specific separators and make the intent of path construction explicit.

## Normalization

Normalization removes syntactic path components that do not change the intended location, such as redundant separators or `.` components.

For example:

`reports/2026/./november/report.csv`

can normalize to:

`reports/2026/november/report.csv`

Normalization must not be confused with security validation. A path such as:

`reports/../../outside.txt`

may normalize to a location outside the permitted root.

The implementations therefore normalize a candidate path and then verify that the resulting location remains inside the managed root.

## Relative and Absolute Paths

Relative paths are useful when an application controls a known directory hierarchy.

For example:

`reports/2026/report.csv`

can be resolved against:

`/srv/application-data`

to produce:

`/srv/application-data/reports/2026/report.csv`

Absolute paths are useful when a precise operating-system location is required, but accepting arbitrary absolute paths from untrusted input can give an application access to files outside its intended storage area.

The Python, JavaScript, C++, and Java implementations therefore use a managed root and reject paths that escape it.

## Path Traversal

Path traversal occurs when an input path uses parent-directory components to move outside an intended directory.

A dangerous example is:

`../../etc/passwd`

A web application, archive extractor, file-processing service, or API that accepts arbitrary paths must not assume that the path remains inside the intended directory simply because it began with an expected prefix.

The safe workflow is:

`untrusted path`
        |
        v
`reject invalid characters`
        |
        v
`resolve / normalize`
        |
        v
`compare against managed root`
        |
        v
`perform filesystem operation`

The examples reject traversal before file operations are performed.

## Symbolic Links and Canonicalization

A lexical check can be insufficient when symbolic links are involved.

For example, a directory inside an approved root could contain a symbolic link pointing somewhere outside that root.

Applications with strong security requirements should distinguish between:

- lexical normalization
- absolute resolution
- canonical resolution
- filesystem authorization
- operating-system permissions

The C++ example uses `weakly_canonical` for its managed path resolution. Production systems should also consider symbolic-link policy explicitly, especially when an attacker can create or modify filesystem entries.

## Python Implementation

The Python implementation uses `pathlib`, which provides a high-level interface for filesystem paths.

`FilePathManager` provides:

- managed-root creation
- safe path resolution
- directory creation
- text-file creation
- file and directory inspection
- recursive file discovery
- extension aggregation
- relative-path reporting
- controlled file copying

The `PathInfo` dataclass provides a structured representation of an inspected path.

`PathKind` separates files, directories, and missing paths.

`PathSecurityError` distinguishes invalid or unauthorized paths from ordinary filesystem failures.

The implementation also demonstrates `PurePosixPath` and `PureWindowsPath`. These classes are useful when manipulating path syntax for a particular platform without actually accessing that filesystem.

## JavaScript Implementation

The JavaScript implementation uses Node.js standard-library modules:

- `node:fs/promises`
- `node:path`
- `node:os`

Filesystem operations are asynchronous and return promises.

The `FilePathManager` validates paths before performing asynchronous operations. Recursive discovery uses directory-entry metadata rather than reading every file into memory.

A `Map` is used for extension aggregation before converting the result to an ordinary object.

The implementation demonstrates a distinct Node.js design:

`main()`
→ asynchronous filesystem workflow
→ promise-based operations
→ structured error handling
→ temporary-directory cleanup

This model is appropriate for services where filesystem operations should not block the event loop.

## C++17 Implementation

The C++ implementation uses `std::filesystem`, introduced as a standard filesystem facility in C++17.

The service uses:

- `std::filesystem::path`
- `recursive_directory_iterator`
- `weakly_canonical`
- `copy_file`
- `create_directories`
- `std::map`
- `std::vector`
- structured exception handling

The filesystem API is strongly integrated with C++ types, which avoids many of the string-only operations common in lower-level path manipulation.

The extension report uses a sorted associative container, providing deterministic output.

The managed-root check compares path components rather than performing a simple textual prefix test. A textual test can produce incorrect results when paths share a string prefix but represent different directory trees.

## Java 17 Implementation

The Java implementation uses an enterprise-style service structure.

`PathPolicy` defines a validation contract.

`ManagedPathPolicy` implements the security rule that a normalized path must remain underneath the configured root.

`RepositoryFileService` separates filesystem operations from path-policy decisions.

The service demonstrates:

- records for immutable inspection results
- interfaces for policy abstraction
- `Path` and `Files`
- streams for recursive discovery
- collections for reporting
- custom exceptions
- UTF-8 text handling
- explicit cleanup

This separation makes it possible to replace the path policy without rewriting the filesystem service.

## PostgreSQL Model

The PostgreSQL implementation represents filesystem metadata and path operations relationally.

The main entities are:

`repositories`
→ identifies managed filesystem roots

`filesystem_nodes`
→ represents files and directories

`path_access_policies`
→ represents allowed path prefixes and operation permissions

`path_operations`
→ records requested and completed filesystem operations

The database does not replace the operating system filesystem. It provides a metadata, governance, audit, and policy layer around filesystem-oriented workflows.

## Relational Integrity

The schema uses primary keys and foreign keys to maintain relationships.

A filesystem node belongs to a repository.

A child node can reference a parent node.

A parent must belong to the same repository as its child.

A parent must represent a directory.

Unique constraints prevent duplicate relative paths within one repository.

Check constraints reject:

- empty names
- NUL characters
- invalid relative paths
- negative file sizes
- inconsistent file and directory size states

The trigger `prevent_invalid_parent` performs cross-row validation that cannot be expressed adequately with an ordinary row-level check constraint.

## PostgreSQL Path Validation

The `validate_relative_path` function rejects:

- null paths
- empty paths
- NUL characters
- absolute POSIX paths
- Windows-style drive-root paths
- parent-directory traversal

The function is marked `IMMUTABLE` because its result depends only on its input.

It is used by a table constraint so invalid relative paths cannot be stored.

Database validation should complement, not replace, application-layer filesystem security.

## File Extensions

The implementations extract file extensions for reporting.

The PostgreSQL function `path_extension` handles files with and without extensions.

Examples include:

| Path | Extension |
|---|---|
| `report.csv` | `.csv` |
| `report.txt` | `.txt` |
| `README` | `[no extension]` |

The extension is metadata and should not be treated as proof of file content. A file named `document.pdf` can contain arbitrary bytes.

Applications that need content validation should inspect file signatures, MIME information, or application-specific parsing rules.

## Directory Traversal

Recursive traversal is useful for:

- inventory generation
- backup preparation
- extension analysis
- migration
- auditing
- storage reporting

The examples return files in sorted order where practical, which makes output deterministic.

Large directory trees introduce scalability concerns. Recursive traversal may consume significant time and metadata I/O. Production systems may need:

- bounded traversal
- pagination
- exclusion rules
- concurrency controls
- cancellation
- incremental indexing
- filesystem event integration

## File Copying

The implementations demonstrate controlled file copying.

A copy operation should validate both:

1. the source path
2. the destination path

Validating only the destination is insufficient because an attacker could attempt to use a source path outside the managed storage boundary.

Destination parent directories are created before copying.

Existing destinations are handled differently by each standard-library API, so production applications should explicitly define overwrite behavior.

## Error Handling

Filesystem operations can fail for reasons unrelated to path syntax.

Typical failures include:

- missing files
- missing parent directories
- insufficient permissions
- invalid filenames
- filesystem read-only state
- concurrent deletion
- unavailable network filesystems
- storage exhaustion
- symbolic-link complications

The examples distinguish validation errors from operational failures where appropriate.

A production service should preserve the underlying error context for diagnostics while exposing only safe information to external users.

## Security Considerations

Important controls for path-processing systems include:

| Control | Purpose |
|---|---|
| Managed root | Limits filesystem scope |
| Normalization | Resolves syntactic path ambiguity |
| Root containment check | Blocks traversal |
| NUL rejection | Prevents ambiguous path handling |
| Absolute-path rejection | Prevents bypass of a relative-path policy |
| Symlink policy | Controls filesystem redirection |
| Least-privilege OS account | Limits damage from application compromise |
| Operation auditing | Records sensitive filesystem actions |
| Input validation | Rejects malformed requests |
| Explicit overwrite policy | Prevents accidental replacement |

Path validation should be performed before opening or modifying a file.

## Performance Considerations

Path operations are generally inexpensive compared with file content processing, but large directory trees can make metadata traversal expensive.

A recursive scan has approximately linear work relative to the number of filesystem entries visited:

`O(n)`

where `n` is the number of entries traversed.

Extension aggregation uses maps or dictionaries and is approximately `O(n)` expected time for hash-based structures.

Sorting file results adds approximately:

`O(n log n)`

time.

Database indexes on repository and relative-path fields reduce lookup cost for metadata queries.

For very large repositories, storing every filesystem object in a relational database may create synchronization and write-volume costs. An application should define whether the database is authoritative metadata, a cache, or an audit ledger.

## Edge Cases

The implementations account for several important cases:

- missing files
- directories mistaken for files
- files without extensions
- nested directories
- traversal attempts
- absolute paths
- NUL characters
- invalid parents
- duplicate relative paths
- copy failures
- empty paths
- platform-specific separators
- cleanup failures

Additional production cases can include symbolic links, mount points, permissions changes, concurrent writers, case-sensitive versus case-insensitive filesystems, Unicode normalization, reserved Windows names, path-length limits, and network filesystem behavior.

## Platform Differences

Filesystem semantics differ across operating systems.

Unix-like systems commonly use `/` as the separator and have a root such as `/`.

Windows commonly uses drive-qualified paths such as `C:\data\report.csv`, while APIs may also accept `/` separators.

Case sensitivity is another important distinction. Many Unix filesystems are case-sensitive, while common Windows configurations are case-insensitive.

Applications that need portability should avoid assumptions about:

- separator characters
- case sensitivity
- reserved filenames
- maximum path lengths
- filesystem permissions
- symbolic links
- filename encoding

Standard path libraries should be preferred over manual string manipulation.

## Practical Workflow

A robust path-processing workflow can be represented as:

`Input`
→ `Syntax validation`
→ `Path construction`
→ `Normalization`
→ `Root containment validation`
→ `Filesystem operation`
→ `Result validation`
→ `Audit / reporting`

For security-sensitive operations, authorization should occur before the filesystem operation and should be based on the normalized path and requested operation type.

## Database Workflow

The PostgreSQL model represents:

`Repository`
→ `Filesystem Nodes`
→ `Path Policies`
→ `Path Operations`

An operation can then be evaluated against the applicable policy.

For example:

`reports/2026/report.csv`
→ repository = `operations`
→ policy prefix = `reports`
→ operation = `read`
→ read permission = allowed
→ operation can proceed

A traversal path such as:

`../outside.txt`

fails validation before it becomes an accepted relative path.

## Design Boundaries

The source programs operate on real filesystem paths, while PostgreSQL stores metadata and policy information.

The database cannot guarantee that an external filesystem has not changed unless a synchronization mechanism exists.

Similarly, application-level validation cannot replace operating-system access controls.

A secure design therefore uses multiple layers:

`Application validation`
+
`Authorization`
+
`Filesystem permissions`
+
`Database integrity`
+
`Audit logging`

No single layer should be treated as sufficient for a hostile environment.

## Educational Focus

The implementations emphasize the difference between a path string and a filesystem object.

A path is a representation of a location.

A file or directory is an object maintained by the operating system.

Operations such as `resolve`, `normalize`, `stat`, `walk`, `copy`, and `delete` operate at different abstraction levels.

Understanding that distinction helps prevent incorrect assumptions such as treating a normalized path as automatically authorized or treating a filename extension as proof of file type.

The project therefore connects basic path manipulation with practical filesystem engineering, validation, security, portability, database modeling, and operational auditing.
