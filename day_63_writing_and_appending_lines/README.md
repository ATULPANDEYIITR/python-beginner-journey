# Writing and Appending Files

## Scope

This project implements reliable file creation, overwriting, appending, validation, auditing, and version-aware persistence across Python, JavaScript, C++17, Java 17, and PostgreSQL.

The central distinction is between two operations:

- **Writing** replaces the existing file contents or creates a new file.
- **Appending** preserves the existing contents and places new content at the end.

The implementations also address path validation, encoding, size limits, nested directories, missing files, operation auditing, transactional behavior, and failure handling.

## Core File Model

The implementations use a common conceptual model:

`Application → File Store → Safe Path → Write/Append Operation → Validation → Persistence → Audit`

A write operation follows:

`filename + content → validate → open in write mode → replace contents → audit`

An append operation follows:

`filename + content → validate → open in append mode → preserve contents → add content → audit`

The important semantic difference is the file-open mode. Write mode truncates an existing file, while append mode preserves the previous byte sequence.

## File Writing

Writing is appropriate when the resulting file should represent a complete new state.

For example:

`application.log`

can initially contain:

`Application started`

A subsequent write containing:

`Application restarted`

replaces the previous content.

This behavior is useful for generated reports, configuration snapshots, exported datasets, and regenerated state files.

The implementations do not silently confuse writing with appending. Each operation is represented explicitly by a write mode.

## File Appending

Appending is appropriate when previous records must remain intact.

A sequence such as:

`Application started`
`Configuration loaded`
`Database connection established`
`Worker process started`

can be constructed through multiple append operations.

Appending is useful for logs, audit trails, event records, incremental reports, and line-oriented output.

Appending has an important operational characteristic: repeated execution can create repeated records. Applications that require idempotency need an application-level record identifier or duplicate-detection policy. The file APIs themselves cannot determine whether two identical records represent legitimate repeated events.

## Python Implementation

The Python implementation uses a `FileManager` dataclass with a configured base directory, UTF-8 encoding, maximum content size, and an in-memory audit log.

### Path handling

The `_safe_path` method resolves the requested path and checks that the resulting location remains beneath the configured base directory.

This prevents inputs such as `../outside.txt` from escaping the storage directory.

The check is performed after path resolution rather than by inspecting only the original string. This is important because relative paths can contain combinations of directory components that change their final location.

### Writing and appending

The implementation maps:

- `WriteMode.WRITE` to Python file mode `w`
- `WriteMode.APPEND` to Python file mode `a`

The `write` and `append` methods share validation and persistence logic through `_save`.

### Line-oriented operations

`append_lines` normalizes each supplied line and ensures that each record ends with a newline.

This avoids inconsistent line endings when multiple records are appended programmatically.

### Validation and failures

The Python implementation rejects:

- empty or invalid filenames
- directory targets
- path traversal
- excessive content
- missing files during reads
- operating-system write failures
- non-string content

The example also contains assertions for successful content and file-size validation.

## JavaScript Implementation

The JavaScript implementation uses Node.js `fs/promises` rather than synchronous filesystem APIs.

This makes the example suitable for event-driven applications where blocking the main execution path would be undesirable.

### Asynchronous persistence

The `FileStore` methods return Promises and use `async` and `await`.

The flow is:

`validate → resolve path → create parent directory → asynchronous write → audit`

Both write and append operations use `fs.writeFile` with explicit flags.

The write operation uses `w`, while append uses `a`.

### Event-driven design

The implementation does not create a custom event emitter because asynchronous filesystem operations already integrate naturally with the Node.js event-driven execution model.

The audit records are collected after successful operations. Failed operations do not produce successful-operation audit records.

### Resource cleanup

The demonstration uses a temporary directory and removes it recursively after execution.

This keeps the example isolated from the user's permanent filesystem.

## C++17 Implementation

The C++ implementation models file persistence through a `FileStore` class and uses the C++17 `<filesystem>` library.

### Filesystem model

`std::filesystem::path` is used for path construction and normalization.

The implementation compares the canonicalized target path with the canonicalized storage directory. A target that does not remain below the storage directory is rejected.

This protects the storage boundary against path traversal.

### Stream-based writing

`std::ofstream` is opened with either:

- `std::ios::trunc` for replacement
- `std::ios::app` for appending

The stream is flushed after the operation and checked for write failure.

### Structured auditing

Audit records are stored as C++ structures containing:

- operation type
- relative filename
- bytes written
- lines written

The program therefore separates file content from operational metadata.

### Resource management

The C++ stream object follows RAII semantics. Its lifetime is scoped to the operation, so the stream is closed automatically when the function returns.

The temporary demonstration directory is explicitly removed after validation.

## Java 17 Implementation

The Java implementation uses `Path`, `Files`, `StandardOpenOption`, records, interfaces, custom exceptions, and immutable audit-log exposure.

### Policy-based validation

`ContentPolicy` defines a validation contract.

`SizePolicy` implements that contract and limits the UTF-8 byte size of content.

This separates validation policy from file persistence. A production system can therefore introduce additional policies without changing the core write and append mechanics.

### Java file operations

Writing uses:

`CREATE + TRUNCATE_EXISTING + WRITE`

Appending uses:

`CREATE + APPEND + WRITE`

This makes the persistence semantics explicit.

### Domain modeling

The implementation uses records for immutable data structures:

- `WriteResult`
- `AuditRecord`

The `WriteMode` enum represents the permitted operation types.

`FileOperationException` provides a domain-specific failure type instead of exposing every low-level `IOException` directly to callers.

### Immutable audit exposure

The `auditLog()` method returns `List.copyOf`, preventing callers from modifying the internal audit collection.

This is useful when the file store owns the lifecycle of its operational metadata.

## PostgreSQL Implementation

The PostgreSQL implementation represents file-writing behavior as relational state rather than directly manipulating the operating system filesystem.

The database model contains:

- `stored_files`
- `file_operations`
- `file_snapshots`

The relationships are:

`stored_files`
`→ file_operations`

and

`stored_files`
`→ file_snapshots`

A stored file has one current metadata record, many operations, and many historical snapshots.

### `stored_files`

This table stores current file metadata:

- relative path
- status
- encoding
- byte size
- line count
- version number
- timestamps

The unique constraint on `relative_path` prevents duplicate logical files.

The size and version checks prevent invalid negative or zero-version states.

### `file_operations`

This table records every write or append action.

The stored content represents the input associated with the operation, while `bytes_written` and `lines_written` provide queryable operational metrics.

This is different from the filesystem implementations because the database retains operation history as structured relational data.

### `file_snapshots`

Snapshots represent complete file states at specific versions.

This makes it possible to inspect historical content without reconstructing it from every previous operation.

### Path protection

The database rejects path traversal patterns containing parent-directory components and rejects absolute paths.

The rule is enforced through both a table constraint and a trigger.

The application-level implementations and database-level model therefore apply the same storage-boundary principle at different layers.

## Transactional Behavior

The PostgreSQL operation function performs the logical update of:

1. file metadata
2. operation history
3. file snapshot

within the caller's transaction.

The demonstration commits a valid sequence and separately demonstrates a rollback.

The rollback example creates a temporary logical file inside a transaction and then issues `ROLLBACK`. The final query verifies that the record is absent.

This illustrates an important distinction between ordinary filesystem operations and database persistence. PostgreSQL can provide transactional atomicity across multiple related records, while ordinary filesystem writes require different durability and recovery mechanisms.

## Validation Model

The project applies validation at several layers.

| Layer | Validation |
|---|---|
| Python | Path containment, type checks, size limit, file existence |
| JavaScript | Path containment, content type, size limit, filesystem errors |
| C++17 | Canonical path containment, size limit, stream state |
| Java 17 | Path normalization, content policy, checked exceptions |
| PostgreSQL | Constraints, triggers, path rules, relational references |

Validation is intentionally distributed rather than relying on a single layer.

Filesystem boundaries should be checked before opening a path. Database invariants should be enforced by the database itself when they must remain valid regardless of the calling application.

## Encoding and Byte Size

The examples use UTF-8.

Character count and byte count are not always equivalent. A non-ASCII character can occupy multiple bytes in UTF-8.

The Python, JavaScript, Java, and PostgreSQL implementations therefore use byte-oriented measurements where file-size limits or storage statistics are relevant.

This distinction matters when enforcing maximum file sizes.

## Failure Conditions

The implementations explicitly handle common failures:

- invalid paths
- directory targets
- missing files
- excessive content
- invalid content types
- inaccessible directories
- failed streams
- filesystem permission failures
- database constraint violations
- transaction rollback

Errors are converted into domain-specific failures where practical so callers can distinguish expected file-operation problems from unrelated application failures.

## Performance Considerations

Appending small records is generally inexpensive, but repeatedly opening a file can create unnecessary filesystem overhead for very high-volume workloads.

For high-throughput logging, a buffered writer, dedicated logging subsystem, or batched append strategy may be preferable.

Large files should not be loaded completely into memory when only a small portion is required. The demonstration reads complete files because the examples are intentionally small and validation-oriented.

The PostgreSQL snapshot model provides convenient historical retrieval but duplicates content across versions. For very large files, storing every complete snapshot can consume substantial storage. A production design could store immutable chunks, content-addressed objects, or operation deltas depending on recovery requirements.

## Security Considerations

The main filesystem security control is path containment.

An application that accepts filenames from users must not concatenate untrusted input directly with a trusted directory and assume the resulting path is safe.

The implementations therefore resolve and validate the resulting path.

Other important controls include:

- restrict the writable directory
- avoid running the process with unnecessary filesystem privileges
- enforce content-size limits
- validate encoding assumptions
- avoid accepting arbitrary absolute paths
- avoid exposing internal filesystem paths in public error responses
- separate user-controlled filenames from executable commands
- audit successful write and append operations

Writing files should never be implemented by passing untrusted filenames through a shell command.

## Relationship Between Writing and Appending

Writing and appending are related but have different state semantics.

`WRITE`

`old content → replaced by new content`

`APPEND`

`old content → old content + new content`

A write operation is appropriate when the file represents a replaceable snapshot.

An append operation is appropriate when the file represents a chronological or cumulative record stream.

Confusing these operations can cause either accidental data loss or uncontrolled file growth.

## Edge Cases

The implementations explicitly consider:

- empty content
- content without a final newline
- multiple newline characters
- nested directories
- repeated append operations
- missing files
- existing files
- directory targets
- path traversal
- oversized content
- failed writes
- invalid input types
- temporary test directories
- database transaction rollback

An empty append is valid in the implementations because it does not alter file content. An empty write creates or replaces the file with zero bytes.

## Source File Responsibilities

| Source | Primary perspective |
|---|---|
| Python | Object-oriented file manager with validation and audit records |
| JavaScript | Asynchronous Node.js filesystem workflow |
| C++17 | RAII-oriented filesystem service using streams and `std::filesystem` |
| Java 17 | Policy-driven enterprise-style file service with explicit domain types |
| PostgreSQL | Transactional relational model for file state, operations, and snapshots |

The five implementations intentionally use different mechanisms instead of being direct line-by-line translations.

## Execution Model

The Python, JavaScript, C++17, and Java 17 demonstrations create temporary storage, perform write and append operations, validate the resulting content, test path protection, display audit information, and clean up temporary data.

The PostgreSQL script creates a dedicated schema, defines relational structures and database functions, inserts realistic file operations, executes reporting queries, validates current metadata against snapshots, and demonstrates transaction rollback.

The result is a consistent technical model of writing and appending files while preserving the distinct strengths of each implementation environment.
