# Reading Text Files

## Scope

This learning artifact treats text-file reading as a complete data-processing workflow rather than a single file-open operation.

The implementations cover:

- Opening text files safely
- Explicit text encoding
- Reading complete files
- Streaming files line by line
- Searching text
- Counting lines, characters, and words
- Identifying non-empty lines
- Building word-frequency statistics
- Computing content fingerprints
- Validating paths and file sizes
- Handling missing files and read failures
- Preserving deterministic processing behavior
- Representing extracted text relationally in PostgreSQL

The five implementations use the same broad problem domain while applying different engineering approaches.

## Core Model

A text file contains ordered textual data. Reading it requires decisions about the file path, encoding, size, access method, error handling, and downstream processing.

A useful conceptual flow is:

    File Path
        |
        v
    Path Validation
        |
        v
    File Size / Access Validation
        |
        v
    Encoding Selection
        |
        v
    Text Reading
        |
        +------> Complete Content
        |
        +------> Lines
        |
        +------> Search Results
        |
        +------> Word Statistics
        |
        +------> Integrity Fingerprint

The distinction between complete reading and streaming is important. Complete reading is convenient when the content is known to be small enough to fit comfortably in memory. Streaming is preferable when processing can be performed incrementally.

## File Validation

The implementations validate file access before processing content.

The validation model checks:

| Condition | Handling |
|---|---|
| Missing path | Read operation fails |
| Directory instead of file | Read operation fails |
| Empty configuration value | Validation failure |
| File larger than configured limit | Read operation fails |
| Invalid text decoding | Read operation fails where the runtime exposes decoding errors |
| Empty search term | Search validation failure |
| Invalid result limit | Validation failure |
| I/O failure | Explicit processing error |

A size limit is a practical defensive control. It prevents an apparently simple text-processing operation from unexpectedly consuming excessive memory or processing an unsuitable input file.

The size limit used by the implementations is 5 MiB for demonstration purposes.

## Complete Reading Versus Streaming

Complete reading loads the entire text into a memory structure.

Conceptually:

    File
      |
      v
    Entire Content
      |
      +--> Search
      +--> Display
      +--> Analysis

This approach is straightforward and useful when the file is small.

Streaming changes the processing model:

    File
      |
      v
    Line 1 --> Process --> Discard
    Line 2 --> Process --> Discard
    Line 3 --> Process --> Discard
    ...
    
Only the currently processed portion needs to remain active for the main operation.

The Python implementation exposes `iter_lines()`. The JavaScript implementation uses Node.js streams and `readline`. The C++ implementation uses `std::getline`, while Java uses `BufferedReader`.

For large files, streaming reduces peak memory consumption. The database implementation represents individual lines as rows, allowing SQL queries to operate on the extracted structure.

## Python Implementation

The Python program uses `Path` for filesystem operations, a `dataclass` for immutable result structures, `Counter` for word frequencies, regular expressions for tokenization, and SHA-256 for a content fingerprint.

The main domain types are:

- `TextFileStats`
- `SearchResult`
- `TextFileReader`
- `TextFileError`
- `TextFileValidationError`
- `TextFileReadError`

`TextFileReader.iter_lines()` is the main streaming boundary. It opens the file with an explicit encoding and strict decoding behavior.

`read_text()` builds complete content from the stream. This keeps the actual file-opening policy centralized.

`search()` processes each line and records matching line numbers. Search is case-insensitive while preserving the original line for reporting.

`statistics()` processes the file once while calculating:

- Character count
- Line count
- Non-empty line count
- Word count
- Unique-word count
- SHA-256 digest

`top_words()` maintains a `Counter` rather than repeatedly scanning the complete text.

The demonstration creates a temporary file, exercises all operations, performs assertions, and removes the file in a `finally` block.

## JavaScript Implementation

The JavaScript implementation is designed around Node.js filesystem primitives.

It uses:

- `fs`
- `fs/promises`
- `readline`
- `crypto`
- `Map`
- Async iterators
- Promises
- Custom error classes

The `TextFileReader.lines()` method creates a readable stream and exposes its contents through an asynchronous iterator.

This makes the following processing pattern possible:

    Readable Stream
          |
          v
    readline Interface
          |
          v
    async iteration
          |
          v
    line-by-line processing

The implementation separates asynchronous file access from processing logic.

`read()` demonstrates complete UTF-8 reading.

`lines()` provides streaming access.

`search()` consumes the asynchronous line stream and returns matching records.

`statistics()` calculates counts and uses Node's cryptographic facilities to create a SHA-256 digest.

`topWords()` uses a `Map` as the mutable frequency index and sorts the final entries only when results must be returned.

The file-size check occurs before processing. The stream is explicitly cleaned up through `finally`, which is important when asynchronous processing terminates because of an exception.

## C++17 Implementation

The C++ implementation treats text-file processing as a small systems-oriented service.

The central class is `TextFileReader`.

The implementation uses:

- `std::ifstream`
- `std::getline`
- `std::unordered_map`
- `std::vector`
- `std::sort`
- Enumerated file states
- Custom exceptions
- Explicit validation

`FileState` distinguishes:

- `Available`
- `Missing`
- `Invalid`
- `TooLarge`

This makes file validation an explicit state decision instead of mixing every failure into the read operation.

The program reads complete content through an `ostringstream`, while analysis uses line-by-line processing.

The word tokenizer is implemented without an external library. It constructs tokens from alphanumeric characters, underscores, and apostrophes.

The frequency index uses `std::unordered_map`, providing expected constant-time insertion and lookup for word counts.

The checksum uses the FNV-1a mechanism as a lightweight integrity fingerprint. It is intentionally different from a cryptographic digest and should not be interpreted as a cryptographic security control.

The program also checks search behavior and expected line counts before reporting successful validation.

## Java 17 Implementation

The Java implementation uses an enterprise-oriented service design.

The principal abstractions are:

- `TextFilePolicy`
- `SizePolicy`
- `TextFileService`
- `TextStatistics`
- `SearchResult`
- `TextFileException`

`TextFilePolicy` separates validation rules from file-processing operations. `SizePolicy` is one concrete policy implementation.

This design permits validation rules to be changed without embedding every rule directly inside the service.

`TextFileService.readAll()` performs complete reading through `BufferedReader`.

`search()` performs controlled line-by-line processing and returns immutable results through `List.copyOf()`.

`statistics()` maintains a word-frequency map while simultaneously calculating file statistics and a SHA-256 digest.

The Java implementation uses records for immutable result types:

- `SearchResult`
- `TextStatistics`

The top-word operation uses streams for ordering and limiting frequency results. The domain logic remains explicit rather than relying on a single large stream expression.

Custom checked exceptions distinguish expected file-processing failures from ordinary runtime errors.

## PostgreSQL Implementation

The PostgreSQL implementation models text-file processing relationally.

The schema contains:

| Table | Purpose |
|---|---|
| `text_documents` | Stores document metadata and text content |
| `document_lines` | Stores ordered lines extracted from documents |
| `document_words` | Stores normalized word frequencies |

The relationships are:

    text_documents
          |
          +---- document_lines
          |
          +---- document_words

`text_documents` stores the original text and metadata such as file name and encoding.

`document_lines` gives each line an explicit number. The `(document_id, line_number)` unique constraint prevents two different rows from claiming the same position within a document.

`document_words` provides a normalized word-frequency index. The composite primary key prevents duplicate word entries for the same document.

The database uses a 5 MiB check constraint to enforce the demonstration file-size policy at the database boundary.

## PostgreSQL Functions and Procedure

`validate_text_document()` performs database-level validation before insertion or update.

`populate_document_lines()` converts document content into ordered line rows.

`rebuild_word_index()` tokenizes the stored lines and constructs normalized word frequencies.

`ingest_document()` provides a transactional ingestion workflow. It:

1. Validates the file name and content.
2. Inserts the document.
3. Captures its generated identifier.
4. Extracts lines.
5. Rebuilds the word index.

The procedure allows these operations to be treated as one database workflow.

## Queries and Reporting

The SQL script demonstrates several different classes of query.

### Retrieval

Document metadata and original content can be retrieved directly from `text_documents`.

Individual lines are retrieved from `document_lines` and ordered by `line_number`.

### Search

Case-insensitive line search uses:

`lower(line_text) LIKE '%streaming%'`

The line remains associated with its source document and original position.

### Word Evaluation

The `document_words` table allows direct lookup of a normalized term and its occurrence count.

This avoids repeatedly tokenizing the original document for every word-frequency query.

### Aggregation

`document_report` combines document metadata with line and word information.

It reports:

- Byte size
- Total lines
- Non-empty lines
- Characters
- Words
- Unique words

### Ranking

A common table expression and window function rank words within each document.

The ranking query demonstrates how document-specific top-word analysis can be performed without procedural code.

### Validation

The line-continuity query compares stored line numbers with `row_number()` values. Any returned row indicates a structural inconsistency.

## Data Integrity

The relational implementation uses several database constraints.

Primary keys identify documents, lines, and document-word pairs.

Foreign keys ensure that lines and word statistics cannot exist without their source document.

The unique constraint on `(document_id, line_number)` preserves line ordering.

Check constraints validate:

- File names
- Encodings
- File size
- Positive line numbers
- Positive word counts

The trigger performs validation before a document is persisted.

These rules provide protection even when data is inserted through a client other than the application code.

## Error Handling

File reading can fail for reasons outside the application logic.

Relevant failure conditions include:

- The path does not exist.
- The path points to a directory.
- The process lacks permission.
- The file exceeds the configured size limit.
- The content cannot be decoded using the selected encoding.
- The filesystem becomes unavailable during processing.
- A database transaction fails during ingestion.

The implementations avoid silently converting such failures into empty results.

A missing file is not the same as an empty file.

An empty file is valid input with zero content.

A file containing empty lines is different from an empty file because it has line structure despite containing little or no visible text.

## Encoding

Text-file reading is an encoding-sensitive operation.

The Python implementation explicitly uses UTF-8.

The JavaScript implementation requests UTF-8 from Node.js filesystem APIs.

The Java implementation uses `StandardCharsets.UTF_8`.

The PostgreSQL model stores an `encoding_name` field as metadata while storing decoded text in the `TEXT` column.

The C++ implementation deliberately keeps its example focused on byte-oriented stream handling rather than claiming that arbitrary external encodings are automatically decoded correctly. Production systems processing multilingual legacy files should establish an explicit encoding policy before interpreting bytes as characters.

## Performance

For a file with `n` characters and `w` extracted words, the basic scanning operations are approximately linear in the amount of input.

A single streaming pass has an expected time complexity of `O(n)`.

Frequency maps require additional memory proportional to the number of distinct words, approximately `O(u)`, where `u` is the number of unique tokens.

Complete reading requires memory proportional to the file size.

Streaming processing can reduce the file-content memory requirement to approximately the size of the active buffer and current record, though result collections can still consume memory if the application stores every match.

The JavaScript implementation uses stream-based reading to support asynchronous incremental processing.

The Python, C++, and Java implementations also provide line-oriented processing paths.

The PostgreSQL design trades storage space for queryability by storing extracted lines and word frequencies separately from the original content.

## Security Considerations

Text-file processing should not assume that an input path is trustworthy.

Relevant controls include:

- Validate that the path refers to a regular file.
- Enforce a maximum input size.
- Avoid executing file contents as commands.
- Treat text as data.
- Use explicit encodings.
- Avoid logging sensitive file contents unnecessarily.
- Restrict filesystem permissions at the operating-system level.
- Avoid constructing shell commands from file names.
- Use parameterized SQL when application code supplies document values.
- Keep database transactions atomic during ingestion.

A content hash can help detect changes, but a hash alone does not establish that a file came from a trusted source.

## Edge Cases

The implementations explicitly account for several boundary conditions.

### Empty File

An empty file should produce zero lines or an empty-content result according to the chosen line-reading API semantics.

### Empty Lines

A document can contain multiple empty lines while still having meaningful line positions.

The PostgreSQL implementation records these lines explicitly through `document_lines`.

### Repeated Words

Repeated words are counted rather than deduplicated.

The unique-word count and total-word count therefore represent different measurements.

### Case Differences

Search is case-insensitive.

Word-frequency processing normalizes tokens to lowercase so that `Reading` and `reading` contribute to the same frequency entry.

### Large Files

The examples impose a file-size limit and provide streaming processing.

A production system may replace a fixed limit with configurable limits based on workload and infrastructure.

### Missing Files

Missing files produce explicit errors instead of returning an empty string.

This prevents an absent input from being confused with valid empty content.

### Invalid Search Input

Empty search terms are rejected because accepting them would cause every line to match.

## Relationship Between the Five Implementations

The implementations are deliberately different.

| Implementation | Primary Perspective | Main Technique |
|---|---|---|
| Python | Data-processing utility | `Path`, iterators, dataclasses, `Counter` |
| JavaScript | Event-driven processing | Streams, async iterators, `Map`, Promises |
| C++17 | Systems-oriented processing | STL, explicit states, streams, hash maps |
| Java 17 | Enterprise service model | Policies, records, services, checked exceptions |
| PostgreSQL | Relational text-processing model | Tables, constraints, functions, procedures, CTEs |

The same domain is therefore represented at different abstraction levels rather than through mechanical translations.

## Practical Workflow

A robust text-reading workflow can be represented as:

    Input Path
        |
        v
    Validate Path
        |
        v
    Validate File Type
        |
        v
    Validate Size
        |
        v
    Select Encoding
        |
        v
    Open Safely
        |
        v
    Read
        |
        +--> Search
        |
        +--> Statistics
        |
        +--> Word Frequency
        |
        +--> Integrity Check
        |
        v
    Close / Release Resources

The central engineering decision is to keep input validation, resource management, processing, and reporting separate enough that a failure in one stage does not silently corrupt the meaning of another stage.

## Educational Coverage

The artifact develops the following concepts through executable implementations:

- File paths and file metadata
- Text encoding
- Complete versus streaming reads
- Line-oriented processing
- Tokenization
- Frequency analysis
- Case normalization
- Exception handling
- Resource cleanup
- Hashing and integrity fingerprints
- Immutable result structures
- Asynchronous iteration
- STL-based processing
- Policy-based validation
- Relational normalization
- Database constraints
- Triggers
- Stored functions
- Stored procedures
- Transactions
- CTEs
- Window functions
- Indexed retrieval
- Database-level validation
