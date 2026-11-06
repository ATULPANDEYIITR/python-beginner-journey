# Practice: Files and Exceptions

## 1. Learning objectives

This project implements file operations and exception handling through five independent programming and database examples.

The practical focus is reliable data storage, structured file processing, input validation, failure recovery, and controlled execution of file workflows.

The implementations cover:

- Creating, reading, updating, and deleting files.
- Text, CSV, JSON, and line-oriented log processing.
- File paths and directory operations.
- File metadata and SHA-256 checksums.
- Structured exception handling.
- Custom exception classes.
- Resource management and cleanup.
- Atomic file replacement.
- Record-level validation.
- Partial failure handling.
- Audit logging.
- Transactional database processing.

## 2. File handling fundamentals

A file is a persistent collection of bytes stored under a filesystem path. Applications interpret those bytes according to a format, such as plain text, CSV, JSON, or binary data.

### File operation modes

| Operation | Purpose | Typical operation |
|---|---|---|
| Read | Retrieve existing content | `read` |
| Write | Create or replace content | `write` |
| Append | Add content without replacing existing content | `append` |
| Binary read | Retrieve raw bytes | `rb` |
| Binary write | Write raw bytes | `wb` |
| Exclusive creation | Create only if the file does not exist | `wx` or exclusive-create mode |

Write operations can destroy previous content when replacement is intended. Append operations preserve previous content but do not automatically provide transactional guarantees.

### Text and binary files

Text files contain character data interpreted using an encoding such as UTF-8.

Binary files contain arbitrary bytes. They should be processed without assuming that their content represents readable text.

The Python and Java implementations use explicit UTF-8 encoding. The C++ implementation uses stream-based file access.

An encoding error is different from a missing-file error. A file may exist and be readable at the operating-system level while still containing bytes that cannot be decoded using the selected encoding.

## 3. File paths and directories

A path identifies a file or directory.

Two common path forms are:

- Absolute path: identifies a location from the filesystem root.
- Relative path: identifies a location relative to the application's working directory.

The implementations use temporary directories for their demonstrations. This prevents test files from being mixed with unrelated application files.

Python uses `pathlib.Path`, Java uses `Path`, and C++ uses `std::filesystem`.

These interfaces support directory creation, path composition, existence checks, and file deletion.

### Directory processing

Directory traversal is useful for:

- Finding files with specific extensions.
- Building inventory reports.
- Processing batches of documents.
- Detecting missing or unexpected files.
- Calculating storage usage.

The Java implementation includes an extension-counting operation using recursive directory traversal.

For large directory trees, applications should avoid retaining unnecessary file metadata or file contents in memory.

## 4. Structured file formats

### CSV

CSV represents tabular records using rows and fields.

The Python implementation reads CSV records using `csv.DictReader`.

The Java implementation demonstrates a deliberately restricted CSV format with four unquoted columns:

- `id`
- `department`
- `employee`
- `amount`

The C++ implementation uses a custom escaped delimiter format for task persistence.

Real CSV files may contain quoted commas, escaped quotation marks, and embedded newlines. A simple string split is not a general CSV parser.

### JSON

JSON represents structured objects and arrays.

The Python implementation stores task records as a JSON array. The JavaScript implementation uses `JSON.stringify` and `JSON.parse`.

Example data structure:

- Task identifier
- Task title
- Priority
- Status
- Creation timestamp

JSON is useful when application records have named attributes and nested structures.

Validation must check both syntax and business rules. Successfully parsing JSON does not establish that its fields have correct types or acceptable values.

### JSON Lines

JSON Lines stores one JSON object per line.

The JavaScript implementation writes audit events in this format.

Each line represents an independent event, making the format suitable for append-oriented logs and streaming processing.

## 5. Exception handling

An exception represents an abnormal condition that interrupts normal execution.

It provides a structured alternative to silently ignoring failures or returning ambiguous values.

### Exception categories

| Exception category | Example | Appropriate response |
|---|---|---|
| File not found | Requested input is missing | Report or request the missing file |
| Permission failure | Application cannot access a file | Report the access failure |
| Encoding failure | Invalid UTF-8 content | Reject or process using an appropriate encoding |
| Format failure | Malformed JSON or CSV | Reject invalid input |
| Validation failure | Negative amount | Reject the affected record |
| Storage failure | Disk or filesystem error | Stop or retry according to policy |
| Unexpected failure | Unclassified runtime problem | Log diagnostic information and propagate |

### Exception hierarchy

The implementations introduce custom exceptions to distinguish application-level failures.

Python uses subclasses of `Exception`.

JavaScript uses subclasses of `Error`.

C++ uses subclasses of `std::runtime_error`.

Java uses checked exception classes derived from `Exception`.

Custom exceptions preserve the original cause where supported. This makes it possible to report a meaningful application error without discarding the underlying technical failure.

### Exception propagation

An exception may be handled at the function where it occurs or propagated to a higher-level service.

A useful design separates:

1. Detection of a failure.
2. Classification of the failure.
3. Recovery or rejection.
4. Logging.
5. Reporting to the caller.

A low-level file-reading function should not silently convert every error into an empty file. Doing so can make a failed read appear to be a successful read of an empty file.

## 6. Resource management

Files consume operating-system resources.

An application must close file handles after completing an operation, including when an exception occurs.

| Language | Resource management |
|---|---|
| Python | `with` context manager |
| JavaScript | Promise-based filesystem operations and explicit cleanup |
| C++17 | RAII and stream destructors |
| Java 17 | Try-with-resources |

RAII means Resource Acquisition Is Initialization. C++ objects acquire resources during construction and release them during destruction.

Java try-with-resources automatically closes resources that implement `AutoCloseable`.

Python context managers provide similar deterministic cleanup.

JavaScript uses asynchronous operations and explicit cleanup where necessary.

These approaches reduce resource leaks and improve reliability during exceptional execution.

## 7. Atomic file operations

Writing directly to an existing file creates a risk of partial output.

For example, an application may overwrite half of a report before encountering a disk failure.

A safer replacement pattern is:

1. Create a temporary file in the destination directory.
2. Write the complete new content.
3. Flush the file where appropriate.
4. Close the temporary file.
5. Rename the temporary file to the destination.
6. Remove the temporary file if the operation fails.

The Python, JavaScript, C++, and Java examples implement temporary-file replacement.

A rename within the same filesystem is generally more suitable for atomic replacement than copying content directly over the destination.

Atomic replacement does not automatically guarantee durability after a sudden power failure. Production systems may need directory synchronization, storage-specific guarantees, and recovery procedures.

The C++ implementation includes a replacement fallback because filesystem rename behavior differs across operating systems.

## 8. File integrity and checksums

A checksum provides a digest of file content.

The examples use SHA-256.

The processing mechanism is:

- Read a file in chunks.
- Update the digest with each chunk.
- Finalize the digest.
- Represent the result as hexadecimal text.

Incremental processing avoids loading an entire large file into memory.

For a file containing \(n\) bytes, hashing requires \(O(n)\) time and approximately \(O(k)\) additional memory, where \(k\) is the chosen buffer size.

A checksum can help detect accidental corruption and identify duplicate content.

A checksum does not establish authenticity. An attacker who can modify both a file and its stored checksum can replace both values. Authenticity requires additional controls such as digital signatures or a trusted message authentication mechanism.

## 9. Python implementation

The Python script implements a task-management workflow using JSON persistence.

### Main components

| Component | Responsibility |
|---|---|
| `Task` | Represents a validated task |
| `TaskStatus` | Defines permitted task states |
| `TaskRepository` | Manages persistent task records |
| `FileOperationError` | Base application exception |
| `ValidationError` | Represents invalid business data |
| `FileFormatError` | Represents malformed structured data |
| `StorageError` | Represents filesystem failures |

### Workflow

Task creation follows this sequence:

`Input → Task Validation → Repository Read → Duplicate Check → JSON Serialization → Temporary File → Replacement`

The repository supports:

- Adding tasks.
- Reading all tasks.
- Updating task status.
- Deleting tasks.
- Detecting duplicate identifiers.
- Validating JSON records.
- Reading CSV records.
- Calculating file hashes.

The script also includes assertions that test persistence, status updates, deletion, and invalid input.

### Important design decision

The repository validates all records before writing them. This prevents invalid task objects from entering the persistent JSON file through the repository interface.

The implementation is intended for a single-process demonstration. It does not provide cross-process file locking or concurrent-write coordination.

## 10. JavaScript implementation

The JavaScript implementation demonstrates asynchronous file processing and event-driven execution.

### Main components

| Component | Responsibility |
|---|---|
| `Task` | Validates task input |
| `AsyncFileStore` | Provides asynchronous JSON persistence |
| `FileEventProcessor` | Coordinates task events |
| `EventEmitter` | Publishes successful and failed operations |
| `calculateHash` | Calculates an incremental SHA-256 digest |

### Asynchronous operations

Node.js filesystem APIs provide Promise-based methods.

An asynchronous operation can fail after execution has started. Its Promise rejects with an error.

The implementation uses `async` and `await` to make this behavior explicit.

`Promise.allSettled` is used when multiple task submissions should be evaluated independently. A failed submission does not erase the successful result of another submission.

### Event-driven processing

The event processor publishes:

- `task-added`
- `task-failed`

This separates task execution from event reporting.

The event listener receives the event after the corresponding operation has been attempted.

### Concurrency considerations

The store serializes writes within the running JavaScript instance using a queue.

This prevents concurrent operations in that instance from overwriting one another through interleaved read-modify-write sequences.

It does not coordinate multiple Node.js processes or external applications accessing the same file.

Production systems that require multi-process consistency should use an appropriate database or external locking mechanism.

## 11. C++17 implementation

The C++ program demonstrates typed file persistence using a custom delimiter-based format.

### Main components

| Component | Responsibility |
|---|---|
| `Task` | Models task data |
| `Status` | Defines task processing states |
| `TaskFileRepository` | Reads and writes task records |
| `ErrorReport` | Aggregates validation failures |
| `parseInput` | Converts raw input into validated tasks |

### Delimiter escaping

The persisted format uses the vertical bar as a field separator.

A literal vertical bar or backslash inside a title is escaped before storage.

This prevents ordinary delimiter characters from being interpreted as field boundaries.

The parser reverses the escaping mechanism when reading records.

### STL usage

The implementation uses:

- `std::vector` for task collections.
- `std::set` for duplicate identifier detection.
- `std::map` for error aggregation.
- `std::find_if` for task lookup.
- `std::count_if` for status aggregation.
- `std::sort` for priority ordering.
- `std::optional` for input that may be rejected.
- `std::filesystem` for directory and path operations.

### Complexity

For \(n\) stored tasks:

| Operation | Approximate complexity |
|---|---|
| Load all records | \(O(n)\) |
| Detect duplicate IDs using a set | \(O(n \log n)\) |
| Find a task | \(O(n)\) |
| Sort tasks | \(O(n \log n)\) |
| Count records by status | \(O(n)\) |

The repository reloads the file for each operation. This is appropriate for a small exercise but inefficient for large datasets.

The custom format is educational and does not replace a fully featured serialization format.

## 12. Java 17 implementation

The Java program models an enterprise expense-import process.

It distinguishes technical file failures from business-policy violations.

### Main components

| Component | Responsibility |
|---|---|
| `ImportRecord` | Immutable validated record |
| `RecordValidator` | Defines validation behavior |
| `ExpensePolicy` | Enforces department and amount restrictions |
| `CsvImportService` | Reads and processes CSV records |
| `AtomicFileWriter` | Replaces files through temporary storage |
| `AuditLogger` | Records workflow events |
| `DirectoryScanner` | Produces file-extension statistics |

### Records and immutability

Java records provide concise immutable data structures.

The `ImportRecord` constructor validates its fields, preventing invalid instances from being created through normal construction.

### Policy validation

The expense policy enforces two rules:

- The department must belong to the permitted department set.
- The amount must not exceed the configured maximum.

These are business validation rules rather than file-format rules.

A record can be syntactically valid while still violating an application policy.

### Partial failure handling

The CSV import service processes individual records independently.

A malformed or rejected record does not necessarily prevent subsequent records from being examined.

The service records the rejection result and continues processing.

A file-level failure, such as an unavailable file or invalid header, is handled separately.

This distinction is important in enterprise data-import systems because individual data-quality failures and infrastructure failures require different responses.

## 13. PostgreSQL implementation

The PostgreSQL script models the database side of a file-ingestion workflow.

PostgreSQL stores file metadata, imported records, validation results, processing states, and audit information. Actual operating-system file access is handled by an application or external storage service.

### Relational model

The main relationships are:

`Users → Imported Files → Imported Records → Processing Errors`

Additional relationships include:

- Import policies assigned to files.
- Audit events associated with files and users.
- Departments used for business validation.

### Database objects

| Object | Purpose |
|---|---|
| `app_users` | Stores processing identities and roles |
| `departments` | Defines recognized departments |
| `import_policies` | Stores import limits |
| `imported_files` | Stores file metadata and lifecycle state |
| `imported_records` | Stores individual imported rows |
| `processing_errors` | Stores validation and processing failures |
| `audit_events` | Stores operational events |

### Constraints

The schema uses:

- Primary keys for record identification.
- Foreign keys for relational integrity.
- Unique constraints for usernames and storage keys.
- Check constraints for file sizes and amounts.
- Regular-expression validation for SHA-256 values.
- Enumerated types for controlled workflow states.

Indexes support common retrieval patterns, including file-state filtering, hash lookup, record-state retrieval, and chronological error reporting.

### File lifecycle

The permitted lifecycle is:

`RECEIVED → VALIDATING → VALIDATED → PROCESSING → COMPLETED`

Alternative terminal outcomes include:

- `PARTIALLY_FAILED`
- `FAILED`

The transition trigger rejects invalid state changes and prevents completed files from being reopened through ordinary updates.

### Validation function

`validate_file_records` evaluates imported rows against the active import policy.

It checks:

- Employee names.
- Permitted departments.
- Non-negative amounts.
- Maximum permitted amounts.
- Maximum record counts.

Invalid rows are marked as rejected and associated with error records.

Valid rows remain eligible for processing.

### Processing procedure

`process_validated_file` processes records that passed validation.

It changes eligible record states, determines the final file state, and writes an audit event.

The procedure requires an authorized operator or administrator.

### Exception handling

PL/pgSQL supports exception blocks using `EXCEPTION`.

The script demonstrates exception handling for database operations and uses `RAISE EXCEPTION` to reject invalid operations.

A database exception can cause the current transaction or subtransaction to roll back. The caller must understand the transaction boundary before attempting recovery.

### Reporting

The implementation provides:

- File processing summaries.
- Record-level retrieval.
- Error reports.
- Department-level aggregations.
- Completion percentages.
- File eligibility evaluation.
- Audit-event counts.

The CTE-based quality report calculates the percentage of completed records without dividing by zero.

## 14. Validation versus exception handling

Validation and exception handling serve different purposes.

Validation checks whether data or an operation satisfies predefined rules.

Exception handling controls what happens when an operation cannot proceed normally.

For example:

- A negative expense is a validation failure.
- A missing CSV file is a storage failure.
- Invalid JSON is a format failure.
- A duplicate task identifier is a business-rule failure.
- A disk write failure is an infrastructure failure.

The correct classification makes failures easier to diagnose and handle.

## 15. Partial processing and recovery

Batch file processing should distinguish between record-level failures and file-level failures.

Consider an import containing 100 records:

- 92 records pass validation.
- 5 records violate department restrictions.
- 3 records contain invalid amounts.

A record-oriented workflow can accept the 92 valid records while preserving the eight rejected records for correction.

An unreadable file is different. If the application cannot parse the file structure, it may be impossible to identify individual records reliably.

A practical recovery process should retain:

- Original file identity.
- File checksum.
- Import policy version.
- Record position.
- Error category.
- Processing timestamp.
- Retry status.

Retries should be designed to avoid duplicate business effects.

## 16. Security considerations

File processing introduces security risks beyond ordinary input validation.

| Risk | Control |
|---|---|
| Path traversal | Resolve and validate storage paths |
| Unauthorized access | Apply filesystem and application permissions |
| Malicious file content | Validate formats and enforce size limits |
| Duplicate imports | Use checksums and idempotency controls |
| Sensitive information exposure | Avoid logging file contents and credentials |
| Partial writes | Use temporary files and replacement |
| Concurrent updates | Use locking or transactional storage |
| Resource exhaustion | Limit file sizes, rows, and processing time |
| Data corruption | Use checksums and integrity validation |

Applications should not trust a filename, extension, or MIME type supplied by a user.

A filename ending in `.csv` does not establish that its contents are valid CSV.

Similarly, a file checksum does not establish that the file is safe to process.

## 17. Atomicity and transaction boundaries

Filesystem operations and database transactions are separate mechanisms.

A database transaction can roll back changes to database tables, but it cannot automatically reverse an external filesystem write.

For a production import workflow, a useful sequence is:

1. Receive the uploaded file.
2. Store it in a controlled staging location.
3. Calculate and verify its checksum.
4. Register its metadata in the database.
5. Validate its content.
6. Process eligible records.
7. Record the final outcome.
8. Move or retain the file according to the retention policy.

If a database operation fails after the file has been stored, the application needs a reconciliation or cleanup mechanism.

The PostgreSQL implementation deliberately models metadata and processing rather than pretending that a database transaction controls external file storage.

## 18. Performance considerations

| Operation | Performance consideration |
|---|---|
| Reading large files | Process in chunks or streams |
| CSV imports | Avoid unnecessary intermediate copies |
| JSON persistence | Full serialization can become expensive |
| Hash calculation | Use incremental buffers |
| Directory scanning | Avoid unnecessary recursive traversal |
| Repeated file updates | Reduce repeated full-file rewrites |
| Database reporting | Use indexes that match filtering and joining patterns |
| Error aggregation | Store structured error categories |
| Concurrent processing | Use bounded workers and controlled locking |

For large imports, a database staging table and bulk-loading approach may be more efficient than inserting every row through an individual application request.

Indexes improve retrieval but add storage requirements and write overhead. They should support actual query patterns.

## 19. Practical test cases

The following cases are represented across the implementations.

| Test case | Expected behavior |
|---|---|
| Missing file | Return or raise a clear missing-file error |
| Empty file | Reject when records are required |
| Invalid JSON | Raise a format exception |
| Invalid CSV header | Reject the file |
| Invalid numeric value | Reject the affected record |
| Duplicate identifier | Prevent duplicate insertion |
| Blank title | Reject task creation |
| Negative amount | Reject the expense record |
| Excessive amount | Reject under the import policy |
| Unauthorized department | Reject under the import policy |
| Missing task | Return a not-found result |
| Failed file replacement | Clean up the temporary file |
| Multiple concurrent submissions | Preserve serialized writes within the supported process |
| Invalid state transition | Reject the operation |
| Corrupt content | Report a format or integrity failure |

## 20. Execution

### Python

Requires Python 3.10 or later.

Run using:

`python file_exception_practice.py`

Only standard-library modules are required.

### JavaScript

Requires Node.js 18 or later.

Run using:

`node file_exception_practice.js`

Only Node.js built-in modules are required.

### C++17

Compile using:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic file_exception_practice.cpp -o file_exception_practice`

Run using:

`./file_exception_practice`

On Windows, run the generated executable as `file_exception_practice.exe`.

### Java 17

Compile using:

`javac FileExceptionPractice.java`

Run using:

`java FileExceptionPractice`

The program uses Java 17 language features, including records and text blocks.

### PostgreSQL

Execute the SQL script using a PostgreSQL 15 or later database session.

The script creates the `file_practice` schema, its database objects, sample data, processing functions, and reporting queries.

It drops and recreates the exercise schema. Do not execute it in a database containing important data under that schema.

## 21. Technical limitations

These implementations are educational models with deliberately bounded responsibilities.

- Python JSON persistence rewrites the complete task collection.
- JavaScript serialization protects writes only within one process.
- C++ uses a custom delimiter format rather than a general serialization library.
- Java's demonstration CSV parser does not support quoted fields containing commas or newlines.
- The Java audit logger demonstrates append operations but does not provide a tamper-proof audit system.
- The PostgreSQL schema does not access external files directly.
- Database transactions do not automatically coordinate with filesystem transactions.
- SHA-256 checksums detect content changes but do not authenticate file origin.
- Atomic rename guarantees and durability depend on filesystem and operating-system behavior.

These boundaries distinguish a working learning implementation from a production file-processing platform.
