# Input and Output in Python

## 1. Topic Introduction

Input and output, commonly abbreviated as I/O, describe how a Python program receives data and produces data.

Input can originate from:

- A user typing at a terminal
- Standard input streams
- Command-line arguments
- Environment variables
- Text files
- Binary files
- JSON documents
- CSV files
- Pipes
- Subprocesses
- Network or other file-like streams

Output can be directed to:

- The terminal
- Standard output
- Standard error
- Text files
- Binary files
- Structured data files
- Compressed archives
- Another process
- An in-memory stream

Python provides a consistent stream-oriented I/O model. Many operations work with file-like objects, which makes it possible to write code that operates on actual files, terminal streams, memory buffers, or other compatible objects.

The accompanying Python script progresses from basic `print()` and `input()` operations to file handling, serialization, streaming, validation, security, testing, subprocesses, and production-oriented design.

---

## 2. Fundamental Terminology

### Input

Input is information received by a program.

Examples include:

- `"Alice"` entered by a user
- `42` represented as text from a terminal
- A line read from a file
- JSON received from an external system
- An environment variable
- Bytes read from a binary stream

### Output

Output is information produced by a program.

Examples include:

- A message displayed using `print()`
- Data written to a file
- JSON emitted for another application
- Error diagnostics sent to `stderr`

### Stream

A stream is an abstraction representing a sequence of data that can be read from or written to.

Important standard streams are:

- `sys.stdin` for standard input
- `sys.stdout` for standard output
- `sys.stderr` for standard error

Files are also streams.

### Text I/O

Text I/O operates on Python `str` objects. Encoding and newline handling are relevant because text must eventually be represented as bytes.

### Binary I/O

Binary I/O operates on `bytes`. It is appropriate for data such as images, compressed files, executable files, and other non-text formats.

### Serialization

Serialization converts an in-memory object into a representation that can be stored or transmitted.

Deserialization reconstructs an in-memory representation from stored or transmitted data.

---

## 3. `print()` and Standard Output

The simplest output operation is:

    print("Hello, Python!")

`print()` accepts multiple positional arguments.

The default separator is a single space:

    print("Python", "Input", "Output")

The `sep` parameter changes the separator:

    print("2026", "09", "09", sep="-")

The `end` parameter controls what follows the final argument:

    print("Hello", end=" ")
    print("Python")

By default, `print()` ends with a newline.

### `file=`

`print()` can write to any compatible text stream:

    print("Message", file=sys.stdout)

This makes `print()` useful with files and in-memory buffers as well.

---

## 4. `sys.stdout` and `sys.stderr`

`sys.stdout` is the conventional destination for normal program output.

`sys.stderr` is conventionally used for diagnostic and error messages.

The script demonstrates:

- Writing with `sys.stdout.write()`
- Writing with `print(..., file=...)`
- Separating normal output from diagnostic output

This distinction is important in command-line applications because shells can redirect standard output and standard error independently.

For example, conceptually:

    python program.py > output.txt

redirects standard output, while:

    python program.py 2> errors.txt

redirects standard error.

A pipeline can connect one process's standard output to another process's standard input.

---

## 5. Escape Sequences

Common escape sequences include:

- `\n` for a newline
- `\t` for a tab
- `\\` for a backslash
- `\"` for a double quote
- `\0` for a null character

Raw strings reduce the need to escape backslashes:

    r"C:\Users\Student\Documents"

Raw strings are particularly useful when representing Windows paths and regular expressions, although they still have Python's syntactic restrictions around trailing backslashes and quotation marks.

---

## 6. String Formatting

Python provides several mechanisms for formatted output.

### Concatenation

Strings can be concatenated with `+`, but non-string values must be converted explicitly.

### `str.format()`

The `format()` method supports positional and named fields.

### F-strings

F-strings provide concise, expressive formatting:

    name = "Anita"
    score = 91.4567
    print(f"{name}: {score:.2f}")

Important formatting specifications demonstrated in the script include:

- Decimal precision
- Thousands separators
- Percentages
- Zero padding
- Left alignment
- Right alignment
- Center alignment

F-strings are generally the clearest choice for modern Python code when values need to be embedded in strings.

---

## 7. `input()`

The built-in `input()` function reads one line from standard input.

A critical rule is:

**`input()` always returns a string.**

For example, if the user types:

    42

then:

    value = input()

produces:

    "42"

not the integer:

    42

Conversion must be explicit:

    age = int(input("Age: "))

For decimal values:

    price = float(input("Price: "))

Direct conversion can raise `ValueError`, so external input should normally be validated.

---

## 8. Input Validation

External input should be treated as untrusted data until it has been validated.

The script implements reusable functions such as:

- `parse_integer()`
- `parse_float()`
- `parse_boolean()`
- `validate_age()`
- `validate_percentage()`
- `validate_username()`

Validation may involve:

1. Removing unwanted surrounding whitespace
2. Checking whether input is empty
3. Converting the value
4. Checking the numerical range
5. Checking allowed characters
6. Rejecting unsupported representations

A robust validation loop generally catches expected conversion errors and asks for input again.

The important principle is to validate according to the application's actual domain rather than simply checking whether conversion succeeded.

---

## 9. Boolean Input

A common mistake is:

    bool("False")

This evaluates to `True` because `"False"` is a non-empty string.

Boolean text therefore requires explicit interpretation.

The script's `parse_boolean()` function recognizes representations such as:

- `true`
- `false`
- `yes`
- `no`
- `1`
- `0`
- `on`
- `off`

The exact accepted values should be determined by the application's interface requirements.

---

## 10. Splitting Input

Input containing multiple values can be separated with `split()`.

For whitespace-separated values:

    parts = input_text.split()

For comma-separated values:

    parts = input_text.split(",")

Calling `split()` without an argument treats consecutive whitespace as a separator and avoids empty elements caused by repeated whitespace.

Calling `split(" ")` specifically splits on the literal space character and behaves differently when multiple spaces occur.

Whitespace normalization should therefore be deliberate.

---

## 11. Standard Input and `sys.stdin`

`input()` is convenient for interactive programs, but `sys.stdin` is useful when processing streams.

For example:

    for line in sys.stdin:
        process(line)

This pattern is especially important for programs that consume redirected files or pipelines.

Iterating over `sys.stdin` also naturally supports incremental processing instead of requiring the complete input to be loaded into memory.

---

## 12. File Paths with `pathlib`

The script uses `pathlib.Path` for filesystem operations.

Examples include:

- `path.exists()`
- `path.is_file()`
- `path.is_dir()`
- `path.read_text()`
- `path.write_text()`
- `path.read_bytes()`
- `path.write_bytes()`
- `path.mkdir()`
- `path.unlink()`
- `path.glob()`
- `path.rglob()`

`pathlib` provides a clearer and more portable interface than manually concatenating path strings.

A path should be treated as structured data rather than as a raw string whenever practical.

---

## 13. Opening Files

The general file-opening operation is:

    open(path, mode, encoding=...)

For text files, specifying the intended encoding is good practice when it is known. UTF-8 is a common choice.

The script primarily uses:

    encoding="utf-8"

The most important file modes are:

| Mode | Meaning |
|---|---|
| `r` | Read |
| `w` | Write and truncate |
| `a` | Append |
| `x` | Exclusive creation |
| `b` | Binary modifier |
| `t` | Text modifier |
| `+` | Reading and writing |

Modes can be combined, such as:

- `rb`
- `wb`
- `r+`
- `w+`

### Important distinction

Opening a file with `w` truncates an existing file.

For data that must not be accidentally overwritten, `x` can be appropriate.

---

## 14. Context Managers

The preferred pattern for ordinary file access is:

    with open(path, "r", encoding="utf-8") as file:
        content = file.read()

The context manager ensures that the file is closed when the block is exited, including when an exception occurs.

This is safer than relying on manually calling `close()`.

The script also implements a custom context manager to demonstrate the underlying `__enter__()` and `__exit__()` protocol.

---

## 15. Reading Files

Several reading methods are available.

### `read()`

Reads the requested content, or the remainder of the stream when no size is specified.

### `readline()`

Reads one line.

At end-of-file, `readline()` returns an empty string.

### `readlines()`

Reads lines into a list.

### Iteration

The following pattern is generally preferred for large text files:

    with open(path, encoding="utf-8") as file:
        for line in file:
            process(line)

It avoids loading the entire file into memory.

---

## 16. End-of-File

End-of-file is different from an empty line.

An empty line contains a newline:

    "\n"

End-of-file from `readline()` is represented by:

    ""

This distinction matters when manually implementing read loops.

---

## 17. `seek()` and `tell()`

`tell()` reports the current stream position.

`seek()` changes the stream position.

For example:

    position = file.tell()
    file.seek(0)

Binary streams make random access especially straightforward because offsets correspond directly to byte positions.

Text streams have additional encoding and newline considerations, so arbitrary position calculations should be handled carefully.

Not every stream is seekable. Pipes and some other streams may not support random access.

---

## 18. Text Versus Binary I/O

Text mode works with `str`.

Binary mode works with `bytes`.

Example:

    text = "hello"
    data = text.encode("utf-8")
    restored = data.decode("utf-8")

The conceptual flow is:

    str
      |
      | encode
      v
    bytes
      |
      | decode
      v
    str

Binary mode should be used for binary formats.

Reading binary data as text without knowing its encoding can cause decoding errors or data corruption.

---

## 19. Characters Versus Bytes

A Unicode character does not necessarily correspond to one byte.

For example, the script compares:

- The number of characters in English text
- The number of UTF-8 bytes used by the same text
- The number of characters in non-ASCII text
- The corresponding UTF-8 byte count

This distinction matters when calculating:

- Network payload sizes
- Storage requirements
- File limits
- Protocol lengths
- Buffer sizes

`len(str)` measures Unicode code points, while `len(bytes)` measures bytes.

---

## 20. Encoding and Decoding

Encoding converts text into bytes:

    text.encode("utf-8")

Decoding converts bytes into text:

    data.decode("utf-8")

A decoding operation can fail with `UnicodeDecodeError` when the bytes do not represent valid data in the selected encoding.

Possible error strategies include:

- `strict`
- `ignore`
- `replace`

The `strict` behavior is generally preferable when silently losing or altering information would be unacceptable.

Using `ignore` can discard data, while `replace` changes invalid sequences into replacement characters.

---

## 21. Newline Handling

Newline behavior varies across operating systems and file formats.

Python provides newline handling through the `newline` parameter of `open()`.

The script demonstrates explicit newline writing and shows why these operations differ:

    line.rstrip("\n")

and:

    line.rstrip()

The first removes newline characters specifically.

The second removes all trailing whitespace and can unintentionally remove meaningful spaces or tabs.

---

## 22. `StringIO`

`io.StringIO` provides an in-memory text stream.

It behaves similarly to a text file for many operations:

- `write()`
- `read()`
- `readline()`
- `seek()`
- `tell()`
- `getvalue()`

It is particularly useful for:

- Testing output
- Constructing text
- Passing file-like objects to functions
- Avoiding temporary disk files

The script uses `StringIO` to test functions that produce output.

---

## 23. `BytesIO`

`io.BytesIO` provides an in-memory binary stream.

It is useful when APIs expect a binary file-like object but data should remain in memory.

The script demonstrates writing bytes, retrieving them with `getvalue()`, repositioning the stream, and reading the bytes.

---

## 24. File-Like Objects

A major design principle in Python I/O is programming against a stream interface rather than a specific file implementation.

A function can accept an output stream and use:

    output_stream.write(...)

The caller can then provide:

- A real file
- `sys.stdout`
- `StringIO`
- Another compatible stream

This approach improves reuse and testability.

---

## 25. JSON Input and Output

JSON is a text-based structured data format widely used for configuration and data exchange.

Python provides:

- `json.dumps()` to serialize an object to a string
- `json.loads()` to deserialize a string
- `json.dump()` to write JSON to a file-like object
- `json.load()` to read JSON from a file-like object

The script demonstrates all four operations.

A typical JSON-compatible value can contain:

- Strings
- Numbers
- Booleans
- `None`
- Lists
- Dictionaries

Python-specific objects such as sets require custom handling.

---

## 26. JSON Type Limitations

JSON does not have a direct representation for every Python type.

For example, a Python `set` is not directly JSON serializable.

The script demonstrates a custom `default` serializer that converts sets into sorted lists.

When designing JSON schemas, the representation should be explicit and stable. Custom conversion should not accidentally produce ambiguous or incompatible structures.

---

## 27. JSON Validation

Successfully parsing JSON does not mean the data is valid for an application.

For example, valid JSON can still have:

- Missing required fields
- Incorrect types
- Invalid numerical ranges
- Unexpected structures

The script demonstrates a configuration validation function that checks:

- Required keys
- Host type
- Port type
- Port range
- Boolean configuration values

Deserialization and domain validation are separate operations.

---

## 28. JSON Lines

JSON Lines, commonly represented as one JSON object per line, is useful for streaming structured records.

Instead of loading a massive JSON array into memory, a program can process each line independently.

The script writes and reads one JSON record per line.

This pattern is useful for:

- Logs
- Event streams
- Large datasets
- Incremental processing

Each line must still contain valid JSON according to the chosen format contract.

---

## 29. CSV Input and Output

CSV stands for Comma-Separated Values.

Python's `csv` module provides:

- `csv.reader`
- `csv.writer`
- `csv.DictReader`
- `csv.DictWriter`

`DictReader` and `DictWriter` are particularly convenient when columns have meaningful names.

The script writes employee records with:

- ID
- Name
- Department
- Salary

It then reads and validates the records.

---

## 30. CSV Type Conversion

CSV data is text-oriented.

When reading:

    65000

the resulting field is normally a string:

    "65000"

Applications must convert fields explicitly:

    salary = int(row["salary"])

or:

    salary = float(row["salary"])

A robust CSV importer should validate both the presence of required columns and the types of individual values.

---

## 31. CSV Quoting

CSV is more subtle than simply splitting strings on commas.

Values can contain:

- Commas
- Quotes
- Newlines

The `csv` module handles these cases according to CSV conventions.

Manually implementing:

    line.split(",")

is therefore unsafe for general CSV processing.

The script demonstrates values containing commas and quotation marks.

---

## 32. Temporary Files and Directories

The `tempfile` module provides safer mechanisms for temporary resources.

The script uses:

- `TemporaryDirectory`
- `NamedTemporaryFile`

Temporary resources are useful for:

- Intermediate processing
- Testing
- Atomic writes
- Temporary exports

A temporary resource should have a controlled lifetime and should not be used as a substitute for deliberate persistent storage.

---

## 33. Atomic-Style File Replacement

Important files can be damaged if a process writes directly to a destination and fails partway through.

The script demonstrates a safer pattern:

1. Create a temporary file in the destination directory.
2. Write the complete content.
3. Flush it.
4. Request synchronization with `os.fsync()`.
5. Replace the destination with `os.replace()`.

This reduces the risk of exposing partially written content.

Atomic replacement and durable storage are separate concepts. Filesystem guarantees vary, so applications with strict durability requirements must account for their operating environment.

---

## 34. Filesystem Operations

The script demonstrates:

- Creating directories
- Reading directory contents
- Recursive searching
- Copying files
- Moving files
- Deleting files
- Copying directories
- Inspecting file metadata

`shutil` provides higher-level filesystem operations such as copying and moving.

`Path` provides convenient path-oriented operations.

---

## 35. File Metadata

A `Path` can provide information such as:

- Name
- Suffix
- Parent directory
- Existence
- Whether it is a file
- Whether it is a directory
- File size
- Permission bits

Filesystem metadata is platform-dependent, so code should not assume that every operating system exposes identical behavior.

---

## 36. Binary File Processing

Binary files should be opened using modes such as:

    "rb"

and:

    "wb"

Reading binary data produces `bytes`.

The script demonstrates partial reads and chunked copying.

Binary I/O is important for:

- Images
- Audio
- Video
- Archives
- Executables
- Database files
- Protocol payloads

Treating arbitrary binary data as text can corrupt it.

---

## 37. Buffering

Python and the operating system may buffer I/O operations for performance.

`flush()` pushes Python-level buffered data toward the underlying stream.

It does not necessarily mean that the data has physically reached persistent storage.

`os.fsync()` can request stronger synchronization from the operating system, but exact durability depends on the platform and storage system.

Buffering improves performance by reducing the number of expensive low-level operations.

---

## 38. Streaming Large Files

A common mistake is:

    content = file.read()

for very large files.

This can consume substantial memory.

A better approach is:

    for line in file:
        process(line)

For binary data, fixed-size chunks are appropriate:

    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            break
        process(chunk)

The script demonstrates both approaches.

---

## 39. Chunk Size

Chunk size represents the amount of binary data processed during one iteration.

Very small chunks can increase overhead.

Very large chunks can increase memory consumption and may not provide meaningful performance improvements.

There is no universally optimal chunk size. A value such as 64 KiB is a reasonable general-purpose starting point, but production systems should measure actual workloads.

---

## 40. File Hashing

The script computes SHA-256 hashes incrementally.

The data is read in chunks and supplied to:

    hashlib.sha256()

This avoids loading the complete file into memory.

Hashes can help with:

- Integrity verification
- Change detection
- Content identification

A cryptographic hash does not automatically prove authenticity. If an attacker can modify both the file and the hash, a plain hash does not establish trust.

---

## 41. Compression I/O

The standard library includes support for compressed streams.

The script demonstrates gzip:

    gzip.open(..., "wt", encoding="utf-8")

and:

    gzip.open(..., "rt", encoding="utf-8")

Compressed streams can reduce storage and transfer size at the cost of CPU processing.

Compression is particularly useful when I/O bandwidth or storage is more constrained than CPU capacity.

---

## 42. ZIP Archives

The `zipfile` module supports ZIP archives.

The script demonstrates:

- Creating an archive
- Adding files
- Listing archive members
- Reading an archived file

ZIP archives can contain multiple files and directories.

Applications handling untrusted ZIP files must also consider archive extraction security, including malicious paths and decompression resource consumption.

---

## 43. Pickle

`pickle` is Python's native object serialization mechanism.

It can represent many Python-specific structures that JSON cannot directly represent.

The critical security rule is:

**Never unpickle untrusted data.**

Deserializing a malicious pickle can execute arbitrary code.

Pickle is therefore unsuitable as a general-purpose secure interchange format.

For many cross-language or untrusted-data scenarios, JSON is a safer and more interoperable representation.

---

## 44. Command-Line Arguments

Python exposes command-line arguments through:

    sys.argv

For example, a conceptual command can be:

    python program.py input.txt --limit 10

For non-trivial command-line applications, `argparse` is preferable to manually interpreting `sys.argv`.

The script demonstrates:

- Named options
- Default values
- Integer conversion
- Boolean flags
- Help descriptions

Command-line input should be validated just like interactive input.

---

## 45. Environment Variables

Environment variables are another external input mechanism.

Python provides:

    os.environ.get("NAME")

Environment variables are strings.

Therefore:

    PORT = os.environ.get("PORT")

does not automatically produce an integer.

The application should explicitly convert and validate values.

Environment variables are often useful for deployment configuration, but they should not automatically be considered trusted.

---

## 46. Subprocess Input and Output

The `subprocess` module allows Python programs to interact with external processes.

The script demonstrates:

- Capturing standard output
- Capturing standard error
- Supplying standard input
- Using `text=True`
- Checking command success

A typical secure pattern is an argument list:

    subprocess.run(
        [program, argument1, argument2],
        check=True,
    )

rather than constructing shell commands through string concatenation.

---

## 47. Shell Injection

Untrusted input should not be interpolated directly into shell commands.

A dangerous design conceptually resembles:

    os.system("command " + user_input)

The problem is that shell syntax may interpret attacker-controlled characters as commands or operators.

Using a list of arguments with `subprocess.run()` avoids shell parsing in the normal case.

`shell=True` should only be used when shell behavior is intentionally required and inputs are appropriately controlled.

---

## 48. Path Traversal

Applications that accept filenames from users must consider path traversal.

A malicious value such as:

    ../secret.txt

may attempt to escape an intended directory.

The script's `safe_child_path()` function:

1. Resolves the base directory.
2. Resolves the candidate path.
3. Checks whether the candidate remains relative to the permitted base.

Filesystem security can also involve symlinks, race conditions, permissions, mount points, and platform-specific behavior.

A simple filename suffix is not a security boundary.

---

## 49. File Extensions Are Not File Types

A file called:

    photo.jpg

does not necessarily contain JPEG data.

Attackers can rename arbitrary content to have a trusted extension.

Security-sensitive applications should validate actual content and apply appropriate size, format, and processing restrictions.

---

## 50. Input Size Limits

Unbounded input can cause resource exhaustion.

Applications should consider limits on:

- User-entered strings
- Uploaded files
- Request bodies
- Lines
- JSON documents
- CSV records
- Archive sizes
- Decompressed content

The script demonstrates a basic maximum text-length validator and a file-size validator.

Limits should be based on application requirements rather than arbitrary assumptions.

---

## 51. Exception Handling

Important I/O-related exceptions include:

- `FileNotFoundError`
- `PermissionError`
- `IsADirectoryError`
- `NotADirectoryError`
- `FileExistsError`
- `UnicodeDecodeError`
- `UnicodeEncodeError`
- `json.JSONDecodeError`
- `csv.Error`
- `OSError`

Specific exceptions should generally be handled before broader exception classes.

Catching `Exception` indiscriminately can hide programming errors and operational failures.

A useful pattern is to catch an expected exception, provide meaningful context, and either recover or propagate the failure appropriately.

---

## 52. EAFP and LBYL

Python frequently favors EAFP:

**Easier to Ask Forgiveness than Permission.**

Example:

    try:
        data = path.read_text()
    except FileNotFoundError:
        ...

The alternative is LBYL:

**Look Before You Leap.**

Example:

    if path.exists():
        ...

For filesystem operations, a preliminary check does not guarantee that the later operation will succeed. A file may disappear, permissions may change, or another process may modify the filesystem between the check and the operation.

Therefore, exception handling remains necessary even when checks are performed.

---

## 53. Logging Versus `print()`

`print()` is appropriate for simple user-facing output.

`logging` is generally more suitable for application diagnostics because it supports:

- Severity levels
- Configurable handlers
- Structured formatting
- Multiple destinations
- Filtering
- Operational configuration

Common logging levels include:

- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL

Production applications should avoid relying exclusively on ad hoc `print()` statements for diagnostics.

---

## 54. Human-Readable Versus Machine-Readable Output

Human-oriented output may prioritize readability:

    Employee Alice earns 75000.50.

Machine-oriented output may prioritize structure:

    {"employee": "Alice", "salary": 75000.5}

Machine-readable formats should have stable schemas and predictable types.

JSON is often useful for machine-to-machine exchange because it is widely supported.

---

## 55. Input/Processing/Output Separation

A strong design separates:

1. Input acquisition
2. Validation
3. Business logic
4. Output generation

The script demonstrates this through functions that accept explicit input and output streams.

For example, a processing function can receive a `StringIO` object during testing and a real file or `sys.stdout` in production.

This avoids tightly coupling application logic to `input()` and `print()`.

---

## 56. Dependency Injection for I/O

Passing a stream into a function is a simple form of dependency injection.

Instead of:

    def report():
        print("...")

a more reusable design is:

    def report(output_stream):
        output_stream.write("...")

The caller controls the destination.

This improves:

- Testability
- Reusability
- Separation of concerns
- Integration with other systems

---

## 57. Testing Input and Output

I/O code should be testable without requiring a human to type input or inspect terminal output manually.

The script demonstrates:

- `io.StringIO`
- `unittest`
- `unittest.mock.patch`
- Mocked `input()`
- Captured `stdout`

This makes expected input and output deterministic.

A useful test compares exact output when formatting is part of the interface contract.

---

## 58. Testing Serialization

Serialization should often be tested through a round trip:

1. Start with an object.
2. Serialize it.
3. Deserialize it.
4. Compare the resulting data with the original.

For JSON-compatible data:

    restored = json.loads(json.dumps(original))

The test should account for intentional type transformations if the serialization format does not preserve every Python-specific type.

---

## 59. Configuration Files

Configuration files are a practical application of input/output.

The script uses JSON to store configuration such as:

- Host
- Port
- Debug mode

Loading configuration should be followed by validation.

A syntactically valid configuration file can still be semantically invalid.

---

## 60. Production-Style JSON Storage

The `JsonFileStore` class demonstrates a small abstraction around JSON persistence.

It separates:

- Serialization
- File writing
- File reading
- Error translation

The save operation uses atomic-style replacement.

The load operation distinguishes a missing file from malformed JSON.

This separation makes filesystem behavior easier to test and maintain.

---

## 61. Structured Input Parsing

Input often follows an application-specific format.

The script implements a simple parser for:

    key=value,key2=value2

The parser explicitly rejects malformed fields.

This illustrates a general rule:

**A parser should not silently accept malformed input when correctness matters.**

The exact validation rules should be defined by the data format.

---

## 62. Output Tables

Formatted strings can produce readable terminal tables.

The script uses width specifications such as:

    f"{name:<15}{score:>8.2f}"

This demonstrates how formatting can control:

- Field width
- Alignment
- Decimal precision

For complex applications, dedicated structured output formats may be preferable to manually formatted tables.

---

## 63. Performance Considerations

I/O is often substantially slower than in-memory operations.

Performance considerations include:

### Avoid excessive file opening

Opening a file repeatedly for every small record can add overhead.

Prefer opening once when the workflow allows it.

### Stream large files

Do not load very large files entirely into memory unless necessary.

### Batch writes

Writing larger groups of data can reduce overhead.

### Use suitable chunk sizes

Binary transfers should generally use reasonably sized chunks.

### Avoid unnecessary conversions

Repeated encoding, decoding, serialization, and copying can increase CPU and memory usage.

### Measure before optimizing

I/O performance depends on:

- Operating system
- Filesystem
- Storage device
- Network
- File size
- Buffering
- Application architecture

Optimization should be based on measurement.

---

## 64. Concurrency Considerations

Multiple threads or processes accessing the same file can introduce race conditions.

Potential problems include:

- Interleaved writes
- Lost updates
- Partial records
- Inconsistent reads
- Concurrent truncation
- File replacement races

Possible architectural solutions include:

- File locks
- Synchronization primitives
- Append-only designs
- Databases
- Transactional storage
- Dedicated logging systems

A single `write()` call in one Python process does not automatically solve every concurrent-access problem.

---

## 65. Atomicity and Durability

Two different concepts must be distinguished.

### Atomicity

An operation appears to happen as one indivisible transition from one state to another.

### Durability

Data remains persisted after failures such as process termination or power loss.

Atomic replacement can reduce exposure to partial files, but it does not automatically guarantee all durability properties.

Durability depends on the filesystem, operating system, storage hardware, synchronization operations, and application architecture.

---

## 66. File Permissions

Filesystem permissions control who can access or modify files.

Applications should follow least-privilege principles.

Sensitive data should not be placed in locations with unnecessarily broad permissions.

Permission behavior differs across operating systems, so portable applications should avoid assuming identical permission models everywhere.

---

## 67. Symbolic Links

Symbolic links can redirect a path to another location.

This matters for security-sensitive filesystem operations because a path that appears to be inside a permitted directory may resolve elsewhere.

Applications that process untrusted filenames should consider:

- Symbolic links
- Canonical paths
- Race conditions
- Filesystem boundaries
- Permission changes

Path validation is an important security layer but may need to be combined with stronger filesystem controls for high-security applications.

---

## 68. Temporary Resources

Temporary directories and files are useful for intermediate work.

`TemporaryDirectory` provides automatic cleanup when its context ends.

Temporary resources should be:

- Scoped appropriately
- Cleaned up
- Protected from unintended access
- Used with predictable lifetime semantics

They are particularly useful in tests because they avoid modifying permanent application data.

---

## 69. Data Integrity

Hashing can detect whether content has changed.

The script uses SHA-256 and processes the file in chunks.

The same content should produce the same digest.

Hashing is useful for integrity checking but should not be confused with authentication. A hash by itself does not establish who created or approved the data.

---

## 70. Common Mistakes

### Mistake 1: Assuming `input()` returns a number

It returns `str`.

### Mistake 2: Using `bool()` on textual booleans

`bool("False")` is `True`.

### Mistake 3: Opening an existing file with `w` unintentionally

`w` truncates the file.

### Mistake 4: Forgetting to close files

Use a context manager.

### Mistake 5: Omitting the intended encoding

Explicitly specify encoding when the application knows which encoding should be used.

### Mistake 6: Reading huge files with `read()`

Stream them where practical.

### Mistake 7: Splitting CSV with `str.split(",")`

Use the `csv` module.

### Mistake 8: Assuming CSV fields have correct types

Convert and validate them.

### Mistake 9: Unpickling untrusted data

Never do this.

### Mistake 10: Trusting file extensions

A filename does not prove its content type.

### Mistake 11: Building shell commands from untrusted strings

Use argument lists with `subprocess`.

### Mistake 12: Silently catching every exception

Broad exception handling can hide serious defects.

### Mistake 13: Treating `flush()` as guaranteed disk persistence

Flushing and durability are different concerns.

### Mistake 14: Assuming every stream supports `seek()`

Pipes and other streams may not be seekable.

---

## 71. Limitations and Trade-Offs

### JSON

Strengths:

- Human-readable
- Widely supported
- Cross-language
- Good for hierarchical data

Limitations:

- Limited type system
- No native Python set
- No native Python tuple distinction
- Potentially larger than specialized binary formats

### CSV

Strengths:

- Simple
- Excellent for tabular data
- Widely supported

Limitations:

- Weak type information
- Poor support for nested structures
- Quoting rules must be respected

### Pickle

Strengths:

- Supports many Python objects
- Convenient for Python-specific persistence

Limitations:

- Python-specific
- Unsafe for untrusted input
- Not appropriate as a general cross-language interchange format

### Plain Text

Strengths:

- Simple
- Human-readable
- Easy to inspect

Limitations:

- Structure must be defined by the application
- Type information is usually absent
- Parsing rules can become complex

---

## 72. Security Considerations

Input/output operations often form a security boundary.

Important considerations include:

- Validate all external input.
- Enforce input size limits.
- Validate file sizes.
- Protect against path traversal.
- Consider symbolic-link attacks.
- Do not trust file extensions.
- Do not unpickle untrusted data.
- Avoid unsafe shell command construction.
- Avoid unnecessary privileges.
- Validate structured data after deserialization.
- Treat environment variables as external configuration rather than inherently trusted values.
- Carefully process untrusted archives.
- Avoid silently ignoring malformed data.
- Protect sensitive output and files with appropriate filesystem permissions.

Security validation should be based on the actual threat model and deployment environment.

---

## 73. Implementation Considerations

A robust I/O implementation should answer several questions:

1. What is the source of the input?
2. Is the input text or binary?
3. What encoding is expected?
4. What is the maximum acceptable input size?
5. What constitutes valid input?
6. How should malformed input be handled?
7. Does the operation need random access?
8. Can the data be streamed?
9. Where should output be sent?
10. Does output need to be human-readable or machine-readable?
11. Can multiple processes access the data concurrently?
12. Does partial failure need to be prevented?
13. Is durability important?
14. Is the data trusted?
15. Does serialization preserve the required types?
16. What tests prove correct behavior?

These decisions are more important than choosing an I/O function in isolation.

---

## 74. Real-World Applications

Python input/output techniques appear in:

- Command-line utilities
- Data-processing pipelines
- ETL systems
- Configuration management
- Log processing
- Report generation
- CSV imports and exports
- JSON APIs
- Batch processing
- File synchronization
- Data validation
- Backup systems
- Test harnesses
- Automation scripts
- Archive processing
- Application diagnostics

A production application often combines several I/O mechanisms. For example, a command-line tool may receive arguments, read a configuration file, process a large CSV stream, write structured JSON, and report diagnostics through logging.

---

## 75. Conceptual Architecture

A maintainable I/O-heavy application often follows this structure:

    External Input
          |
          v
    Parsing
          |
          v
    Validation
          |
          v
    Business Logic
          |
          v
    Serialization / Formatting
          |
          v
    Output Stream

Keeping these stages separate makes the system easier to test, replace, and maintain.

For example, the same business logic can receive data from:

- A terminal
- A file
- JSON
- CSV
- A test buffer

without changing the core processing logic.

---

## 76. Important Distinctions

| Concept | Meaning |
|---|---|
| `str` | Unicode text in Python |
| `bytes` | Raw byte sequence |
| Encoding | Converts text to bytes |
| Decoding | Converts bytes to text |
| `stdin` | Standard input stream |
| `stdout` | Standard output stream |
| `stderr` | Standard error stream |
| `read()` | Reads stream content |
| `readline()` | Reads one line |
| `write()` | Writes data |
| `seek()` | Changes stream position |
| `tell()` | Reports stream position |
| `flush()` | Flushes buffered stream data |
| `fsync()` | Requests OS-level synchronization |
| Serialization | Object to external representation |
| Deserialization | External representation to object |
| Streaming | Processing incrementally |
| Buffering | Temporarily collecting I/O data for efficiency |

---

## 77. Advanced Design Principles

### Prefer explicit boundaries

External data should enter the application through clearly defined interfaces.

### Separate parsing from validation

Parsing determines what the input structurally represents.

Validation determines whether that representation is acceptable.

### Separate I/O from business logic

Business logic should not depend unnecessarily on terminal or filesystem behavior.

### Prefer streaming for unbounded data

Large or potentially unbounded data should normally be processed incrementally.

### Treat external data as untrusted

Files, arguments, environment variables, and serialized documents can all contain malformed or malicious values.

### Use appropriate serialization

Choose JSON, CSV, plain text, binary formats, or other representations according to the required data model and trust boundary.

### Design for failure

Files can disappear, permissions can change, storage can fill, encodings can be wrong, and data can be malformed.

Production code should make these failure modes explicit.

---

## 78. What the Python Script Demonstrates

The accompanying script implements a progression through:

1. Basic `print()`
2. Escape sequences
3. String formatting
4. `sys.stdout`
5. `sys.stderr`
6. `input()` concepts
7. Integer and floating-point conversion
8. Boolean parsing
9. Validation loops
10. Input splitting
11. `sys.stdin`
12. `pathlib`
13. Text file writing
14. Text file reading
15. File modes
16. Context managers
17. `read()`, `readline()`, and `readlines()`
18. `seek()` and `tell()`
19. Encoding and newline behavior
20. Text and binary I/O
21. Encoding errors
22. JSON serialization
23. JSON limitations
24. CSV processing
25. CSV readers and writers
26. CSV quoting
27. `StringIO`
28. `BytesIO`
29. File-like interfaces
30. Temporary resources
31. Atomic-style replacement
32. Filesystem operations
33. Copying and moving
34. Binary processing
35. Buffering
36. Pickle
37. Command-line arguments
38. `argparse`
39. Environment variables
40. Stream redirection concepts
41. Logging
42. Custom output streams
43. Regular-expression validation
44. Range and domain validation
45. I/O exceptions
46. Specific exception handling
47. EAFP and LBYL
48. Large-file streaming
49. Chunked binary I/O
50. File hashing
51. gzip
52. ZIP archives
53. Path traversal protection
54. File-type trust boundaries
55. Input limits
56. Shell-command security
57. Subprocess input/output
58. Output capture
59. Unit testing
60. Serialization round trips
61. Custom JSON serialization
62. JSON Lines
63. Structured parsing
64. Input edge cases
65. Newline handling
66. Output flushing
67. Progress output
68. Performance considerations
69. Concurrent I/O considerations
70. File permissions
71. Symbolic links
72. Directory operations
73. Directory copying
74. File-size validation
75. Encoding round trips
76. Character and byte differences
77. Binary random access
78. Fixed-size record access
79. Seekable versus non-seekable streams
80. Input/processing/output separation
81. Dependency injection
82. JSON configuration
83. Configuration validation
84. Formatted tables
85. Pretty-printing
86. Machine-readable output
87. Special characters
88. End-of-file behavior
89. Partial reads
90. Data integrity
91. Malformed JSON handling
92. CSV validation
93. File-like protocols
94. Custom context managers
95. Timestamp output
96. Serialization trade-offs
97. I/O exception taxonomy
98. Streaming file transformation
99. JSON file storage
100. I/O best practices
101. An integrated CSV-based application
102. Controlled temporary-resource cleanup

The examples are deliberately connected so that basic terminal I/O leads naturally into files, structured data, streaming, security, testing, and production-oriented design.
