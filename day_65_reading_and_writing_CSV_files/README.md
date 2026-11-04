# Reading and Writing CSV Files

## 1. Introduction

Comma-Separated Values (CSV) is a text-based format for representing tabular data. Each record represents a row, and delimiters separate individual fields.

CSV is commonly used for:

- Data exchange between applications
- Database import and export
- Financial reporting
- Employee and customer records
- Transaction processing
- Data migration
- Batch processing
- Spreadsheet interoperability
- ETL (Extract, Transform, Load) pipelines

CSV is a data interchange format rather than a complete database format. It does not inherently enforce data types, primary keys, relationships, or business constraints.

A reliable CSV workflow must therefore handle parsing, schema validation, type conversion, data quality, error reporting, and safe output generation.

## 2. CSV File Structure

A typical CSV file contains a header followed by data records.

Example:

employee_id,name,department,salary,active
101,Alice Johnson,Engineering,85000.50,true
102,Bob Smith,Finance,72000.00,true
103,Charlie Brown,Engineering,91000.00,true

The first row identifies the columns.

Each subsequent row represents one record.

### Important terminology

| Term | Meaning |
|---|---|
| Record | A complete row of CSV data |
| Field | An individual value in a record |
| Header | Column names identifying fields |
| Delimiter | Character separating fields |
| Quote character | Character enclosing fields containing special characters |
| Escape sequence | Representation of special characters within a field |
| Schema | Expected columns, data types, and validation rules |
| Encoding | Character representation used by the file |
| Import | Reading external CSV data into an application |
| Export | Writing application data into a CSV file |
| Serialization | Converting structured values into CSV text |
| Deserialization | Converting CSV text into structured values |

## 3. CSV Formatting Rules

### 3.1 Delimiters

The comma is the most common delimiter.

Example:

employee_id,name,department
101,Alice,Engineering

Other delimiters include:

- Semicolon (`;`)
- Tab (`\t`)
- Pipe (`|`)

A file using tabs as separators is commonly called TSV.

A parser must use the delimiter specified by the file format rather than assuming that every text file uses commas.

### 3.2 Quoted fields

Fields containing commas, quotes, or line breaks need quoting.

Example:

employee_id,name,department
101,"Smith, Alice",Finance
102,"John ""Jack"" Brown",Engineering

The CSV convention represents an embedded quotation mark by doubling it.

The value:

John "Jack" Brown

is represented as:

"John ""Jack"" Brown"

### 3.3 Multiline fields

A CSV field can contain a line break when enclosed in quotes.

Example:

employee_id,description
101,"First line
Second line"

A physical line is not necessarily a complete CSV record.

This distinction matters when implementing streaming parsers. A parser must retain its quoted-field state until the record is complete.

### 3.4 Empty values

An empty field is represented by adjacent delimiters.

Example:

101,Alice,,85000

This is different from a missing column.

A reliable importer should distinguish:

- An explicitly empty value
- A missing field
- A missing record
- A field containing whitespace
- A database NULL value

CSV itself does not define a universal representation for NULL.

## 4. Reading CSV Files in Python

Python provides the standard-library `csv` module.

It supports structured parsing without requiring an external package.

### 4.1 csv.reader

`csv.reader` returns each record as a list of strings.

The implementation demonstrates:

- Reading a file with UTF-8 encoding
- Using `newline=""` for correct CSV newline handling
- Reading rows sequentially
- Preserving quoted values
- Handling delimiters and quotation marks

The returned values are strings. Numeric conversion and business validation remain application responsibilities.

### 4.2 csv.DictReader

`csv.DictReader` maps each record to a dictionary.

Example conceptual structure:

- employee_id → 101
- name → Alice Johnson
- department → Engineering
- salary → 85000.50
- active → true

This is useful when records contain named fields and application logic should not depend on numeric column positions.

The Python implementation validates headers before processing records.

It also checks for missing and extra fields.

### 4.3 csv.writer

`csv.writer` serializes lists into CSV records.

It automatically handles:

- Quoted values
- Commas inside fields
- Embedded quotation marks
- Record delimiters

The writer should be used instead of manually joining values with commas.

Manual joining fails when a field itself contains a comma.

### 4.4 csv.DictWriter

`csv.DictWriter` writes dictionary-based records using a defined field order.

Important options include:

| Option | Purpose |
|---|---|
| `fieldnames` | Defines the output columns |
| `writeheader()` | Writes the header record |
| `writerow()` | Writes one record |
| `writerows()` | Writes multiple records |
| `extrasaction` | Controls unexpected dictionary keys |

The Python implementation uses `DictWriter` for employee exports and department reports.

## 5. Reading and Writing CSV Files in JavaScript

Node.js provides file-system streams and asynchronous iteration.

The JavaScript implementation uses these capabilities to demonstrate a streaming-oriented approach.

### 5.1 File streams

`fs.createReadStream()` reads a file incrementally.

Unlike reading an entire file into memory, streaming allows processing records as input arrives.

This is particularly useful for large transaction exports.

### 5.2 Asynchronous iteration

The `readline` interface allows asynchronous consumption of physical lines.

The implementation tracks whether a quoted field is still open.

It combines physical lines when a quoted record spans multiple lines.

A production-grade parser must also support configurable delimiters, escaped quote characters, encoding policies, and malformed-record recovery.

### 5.3 JavaScript objects

The parser converts validated records into structured objects.

The transaction domain model contains:

| Property | Meaning |
|---|---|
| transactionId | Unique transaction identifier |
| customer | Customer name |
| region | Business region |
| amount | Transaction value |
| status | Transaction processing state |

`Set` provides efficient duplicate-ID detection.

`Map` groups completed transactions by region.

### 5.4 Transform streams

A Node.js `Transform` stream processes incoming data and emits transformed data.

It can be used for:

- Record validation
- Data normalization
- Filtering
- Type conversion
- Enrichment

Backpressure allows downstream processing speed to influence upstream data consumption.

This reduces uncontrolled memory growth in streaming workflows.

## 6. Reading and Writing CSV Files in C++17

C++17 does not provide a dedicated standard-library CSV parser.

The implementation uses standard file streams and STL containers.

### 6.1 File handling

`ifstream` reads CSV data.

`ofstream` writes CSV output.

The repository separates file operations from the business logic.

This provides a clearer boundary between storage and processing.

### 6.2 Parsing

The parser maintains a Boolean state indicating whether the current field is inside quotation marks.

When it encounters:

- A quotation mark, it changes the parsing state.
- Two consecutive quotation marks inside a quoted field, it interprets them as one literal quotation mark.
- A comma outside quotation marks, it completes the current field.
- A comma inside quotation marks, it preserves the comma as field content.

This is a state-machine approach to CSV parsing.

### 6.3 Domain modeling

The C++ implementation models sales orders using:

- `Order`
- `OrderStatus`
- `SalesSummary`
- `OrderRepository`
- `SalesAnalytics`

The `Order` structure stores the business data, while the repository handles file operations.

The analytics class calculates delivered revenue and product-level summaries.

### 6.4 STL usage

| C++ feature | Application |
|---|---|
| `vector` | Stores CSV fields and orders |
| `set` | Detects duplicate order identifiers |
| `map` | Groups sales by product |
| `ifstream` | Reads CSV files |
| `ofstream` | Writes CSV files |
| `stringstream` | Supports text conversion |
| `exception` | Represents processing failures |
| `rename` | Replaces completed output files |

The implementation uses `std::map` to produce ordered product reports.

## 7. Reading and Writing CSV Files in Java 17

The Java implementation models an enterprise invoice-import process.

Its design separates domain objects, parsing, policy evaluation, repository operations, and reporting.

### 7.1 Records

Java 17 records provide concise data carriers.

The `Invoice` record represents an immutable invoice.

Its compact constructor validates:

- Positive identifiers
- Required customer names
- Non-negative amounts
- Three-character currency codes
- Valid invoice statuses

The record normalizes the monetary amount to two decimal places.

### 7.2 Enumerations

`InvoiceStatus` restricts invoice states to:

- DRAFT
- APPROVED
- PAID
- REJECTED

This prevents arbitrary status strings from spreading through business logic.

### 7.3 Import policies

`InvoiceImportPolicy` defines an interface for invoice acceptance.

`EnterpriseInvoicePolicy` implements a maximum-amount restriction and rejects invoices marked REJECTED.

Separating policy evaluation from parsing makes business rules easier to change and test.

### 7.4 Service architecture

| Component | Responsibility |
|---|---|
| CSVCodec | Parsing and serialization |
| Invoice | Immutable invoice domain model |
| InvoiceImportPolicy | Defines acceptance rules |
| EnterpriseInvoicePolicy | Implements enterprise restrictions |
| InvoiceImportService | Coordinates record validation and duplicate detection |
| InvoiceRepository | Reads and writes CSV files |
| InvoiceReportingService | Generates customer-level reports |

### 7.5 Import result states

The implementation distinguishes three outcomes:

| State | Meaning |
|---|---|
| ACCEPTED | Record passed validation and policy checks |
| INVALID | Record failed validation or business policy |
| DUPLICATE | Invoice identifier already exists in the import process |

This makes import outcomes explicit rather than treating every failure as an unstructured exception.

## 8. CSV Data Validation

CSV files contain text values, even when their fields represent numbers, dates, or Boolean values.

Type conversion must be performed before business operations.

### 8.1 Structural validation

Structural validation checks:

- Header existence
- Expected column names
- Column order where required
- Duplicate column names
- Correct field count
- Missing values
- Unexpected columns

For example, an employee import expecting five fields should reject a record containing four or six fields.

### 8.2 Type validation

Typical conversions include:

| Data type | Validation |
|---|---|
| Integer | Valid integer representation |
| Decimal | Valid finite numeric representation |
| Boolean | Accepted values such as true, false, 1, and 0 |
| Date | Valid date representation |
| Currency | Valid currency code |
| Identifier | Positive integer or approved identifier format |

Invalid conversion should produce a meaningful error.

### 8.3 Business validation

A structurally correct record may still violate business rules.

Examples:

- Negative salary
- Negative invoice amount
- Empty customer name
- Unsupported transaction status
- Duplicate identifier
- Amount exceeding an import threshold

The implementations separate structural validation from business validation.

### 8.4 Error isolation

A robust import should not necessarily terminate when one record is invalid.

The Python, JavaScript, C++, and Java examples process records independently and report rejected records.

This allows valid records to continue through the pipeline.

For critical financial imports, the business may instead require the entire batch to be rejected when any record fails validation.

The correct behavior depends on the import policy.

## 9. PostgreSQL CSV Import and Export

PostgreSQL provides native CSV functionality through `COPY`.

### 9.1 COPY

`COPY` transfers data between PostgreSQL tables and files.

A CSV export can specify:

- `FORMAT CSV`
- `HEADER TRUE`
- `DELIMITER`
- `QUOTE`
- `ESCAPE`
- `ENCODING`

Example command structure:

COPY table_name TO '/path/output.csv' WITH (FORMAT CSV, HEADER TRUE);

Server-side `COPY` accesses the database server's filesystem.

### 9.2 psql \copy

The psql client provides `\copy`.

It performs file access on the client machine and transfers data through the database connection.

This is useful when the database server does not have access to the local CSV file.

### 9.3 Staging tables

The SQL implementation uses a staging table before inserting records into the validated invoice table.

The staging table preserves raw values as text.

This design prevents invalid source values from immediately causing typed-column conversion failures.

The workflow is:

CSV file
→ Staging table
→ Structural validation
→ Data validation
→ Business policy evaluation
→ Duplicate detection
→ Validated invoice table
→ Reports and exports

### 9.4 Constraints

PostgreSQL constraints enforce data integrity.

| Constraint | Purpose |
|---|---|
| PRIMARY KEY | Uniquely identifies records |
| FOREIGN KEY | Enforces relationships |
| UNIQUE | Prevents duplicate combinations |
| NOT NULL | Requires a value |
| CHECK | Enforces valid conditions |

The invoice table enforces positive identifiers, valid amounts, currency formats, and supported statuses.

### 9.5 Transactions

The SQL implementation uses a transaction around batch creation, staging, processing, and reporting.

Transactions provide atomicity.

If an unhandled database error occurs before COMMIT, PostgreSQL can roll back the transaction.

A failed record that is deliberately recorded in `import_error` does not automatically invalidate the entire transaction.

## 10. Data Cleaning and Transformation

CSV data frequently requires transformation before storage or reporting.

Common operations include:

- Trimming whitespace
- Normalizing status values
- Converting numeric strings
- Standardizing currency codes
- Removing duplicate records
- Rejecting malformed records
- Applying business policies
- Normalizing field names

The Python employee workflow converts strings into an immutable `Employee` dataclass.

The JavaScript workflow converts transaction records into validated objects.

The C++ workflow converts raw fields into typed `Order` structures.

The Java workflow creates immutable `Invoice` records.

PostgreSQL uses validation functions and typed columns to enforce equivalent rules at the database boundary.

## 11. Duplicate Detection

Duplicate records can occur because of:

- Repeated exports
- Replayed imports
- Network retries
- Incorrect source-system identifiers
- Merged datasets

The implementations use different data structures for duplicate detection.

| Implementation | Mechanism |
|---|---|
| Python | `set` |
| JavaScript | `Set` |
| C++17 | `set` |
| Java 17 | `HashSet` |
| PostgreSQL | Primary key and indexed existence checks |

Hash-based duplicate detection generally offers expected O(1) lookup per record.

Tree-based sets generally offer O(log n) lookup.

Database uniqueness constraints remain essential because application-level duplicate checks alone cannot guarantee integrity under concurrent imports.

## 12. Aggregation and Reporting

CSV data can be transformed into reports without changing the source file.

The implementations provide three reporting scenarios.

### 12.1 Department salary report

The Python implementation groups active employees by department.

It calculates:

- Employee count
- Total salary
- Average salary

### 12.2 Regional transaction report

The JavaScript implementation groups completed transactions by region.

It calculates:

- Completed transaction count
- Completed transaction amount
- Average completed transaction amount

### 12.3 Product sales report

The C++ implementation groups delivered orders by product.

It calculates:

- Delivered order count
- Revenue
- Average order value

### 12.4 Customer invoice report

The Java implementation groups paid invoices by customer.

It calculates:

- Invoice count
- Total paid amount

### 12.5 Database reporting

The PostgreSQL implementation provides:

- Invoice status aggregation
- Customer payment reports
- Batch acceptance statistics
- Rejected record analysis
- Import audit retrieval
- Payment eligibility evaluation

SQL aggregation is particularly useful when the source data has already been validated and stored in relational tables.

## 13. Large CSV Files and Streaming

Reading an entire CSV file into memory can become expensive.

Suppose a file contains one million records.

If the application stores every parsed row, its memory consumption depends on:

- Number of rows
- Number of columns
- String lengths
- Object overhead
- Temporary transformation objects

Streaming reduces the number of records held simultaneously.

### 13.1 Streaming workflow

Read one record
→ Validate the record
→ Convert data types
→ Apply business rules
→ Write or store the accepted record
→ Continue

### 13.2 Memory considerations

| Approach | Memory behavior |
|---|---|
| Read entire file | Proportional to total file size |
| Process records sequentially | Proportional to current record and processing state |
| Streaming with aggregation | Proportional to current record and aggregate state |
| Database staging | Uses database storage and transaction resources |

Duplicate detection can still require O(n) memory when all previously seen identifiers must be retained.

For extremely large imports, database uniqueness constraints or external partitioning may be preferable.

## 14. Atomic File Writing

Directly overwriting an important CSV file can leave incomplete output if a process fails during writing.

A safer workflow is:

1. Create a temporary file in the destination directory.
2. Write the complete CSV output.
3. Flush buffered data.
4. Close the file.
5. Replace the destination file.

The Python implementation uses `os.replace()`.

The JavaScript implementation writes to a unique temporary file and renames it.

The C++ implementation uses a temporary output file followed by `rename()`.

The Java implementation uses `Files.move()` with `ATOMIC_MOVE` when supported and a replacement fallback otherwise.

Atomic replacement behavior depends on the operating system and filesystem. A fallback move is not guaranteed to be atomic.

For highly critical applications, durability, directory synchronization, file permissions, and recovery procedures must also be considered.

## 15. CSV Security

CSV files should be treated as untrusted input.

### 15.1 Formula injection

Spreadsheet applications may interpret fields beginning with certain characters as formulas.

Potentially dangerous prefixes include:

- `=`
- `+`
- `-`
- `@`

An attacker could supply a field such as:

=HYPERLINK("https://example.invalid","Open")

If the exported file is opened in a spreadsheet application, the value may be interpreted as a formula.

The implementations demonstrate prefixing potentially dangerous values with an apostrophe.

This is a mitigation, not a universal security guarantee. Spreadsheet applications differ in how they interpret CSV values.

### 15.2 Input validation

Applications should validate:

- Field length
- Numeric ranges
- Required values
- Allowed characters where appropriate
- Identifiers
- Status values
- Record counts

### 15.3 File access

CSV processing should avoid:

- Trusting arbitrary file paths
- Overwriting unrelated files
- Reading untrusted symbolic links without policy checks
- Exposing sensitive temporary files
- Using excessive filesystem permissions

### 15.4 Sensitive data

CSV files may contain personal or financial information.

Production systems should consider:

- Access control
- Encryption at rest
- Secure file transfer
- Retention periods
- Audit logs
- Restricted output columns
- Secure temporary storage

### 15.5 Encoding

UTF-8 is a practical default for interoperable CSV files.

The Python implementation also uses `utf-8-sig` when reading to tolerate a UTF-8 byte-order mark.

Encoding assumptions should be documented and enforced at system boundaries.

## 16. Performance Analysis

| Operation | Typical complexity |
|---|---|
| Reading n records | O(n) |
| Writing n records | O(n) |
| Validating one record | O(k), where k is the number of fields |
| Hash-based duplicate detection | Expected O(n) total |
| Tree-based duplicate detection | O(n log n) total |
| Grouping by category | Expected O(n) with hash maps |
| Sorting report categories | O(g log g) |
| Database indexed identifier lookup | Approximately O(log n) |
| Sequential streaming memory | O(r + s) |

Here:

- `n` represents the number of records.
- `k` represents the number of fields per record.
- `g` represents the number of distinct groups.
- `r` represents the current record size.
- `s` represents retained processing state, such as duplicate identifiers or aggregate values.

Actual performance depends on file size, encoding, hardware, database indexes, and implementation details.

## 17. Common CSV Failure Modes

| Failure | Cause | Handling |
|---|---|---|
| Incorrect column count | Malformed source record | Reject record |
| Missing header | Invalid input structure | Reject file |
| Duplicate header | Ambiguous field mapping | Reject file |
| Invalid integer | Incorrect identifier | Record validation error |
| Invalid decimal | Malformed numeric value | Reject record |
| Unclosed quote | Malformed CSV syntax | Reject record or file |
| Duplicate identifier | Repeated source record | Reject duplicate |
| Encoding error | Incorrect file encoding | Report decoding failure |
| Missing file | Incorrect path or unavailable source | Report file error |
| Permission error | Insufficient filesystem access | Report I/O failure |
| Disk full | Insufficient storage | Preserve original output |
| Formula injection | Untrusted spreadsheet value | Sanitize exported text |
| Large file | Excessive memory consumption | Use streaming |
| Concurrent import | Simultaneous processing | Enforce database uniqueness |

## 18. Implementation Comparison

| Language | Primary CSV mechanism | Main design perspective |
|---|---|---|
| Python | `csv` module | Structured data processing |
| JavaScript | Node.js streams and custom parser | Asynchronous event-driven processing |
| C++17 | File streams and STL | Explicit parsing and domain modeling |
| Java 17 | Records, services, and interfaces | Enterprise import architecture |
| PostgreSQL | `COPY`, staging, functions, and constraints | Transactional data management |

Each implementation addresses the same general problem using different language capabilities.

The Python version emphasizes standard-library CSV processing.

The JavaScript version emphasizes asynchronous file handling and streaming.

The C++ version emphasizes explicit parser state and domain-oriented processing.

The Java version emphasizes immutable domain objects and enterprise policy separation.

The PostgreSQL version emphasizes relational integrity, staging, transactional processing, and database-side reporting.

## 19. Practical CSV Processing Architecture

A production-oriented CSV workflow can be represented as:

Source CSV
    |
    v
File Access and Encoding Validation
    |
    v
CSV Parsing
    |
    v
Header and Schema Validation
    |
    v
Field Conversion
    |
    v
Data Quality Validation
    |
    v
Duplicate Detection
    |
    v
Business Rule Evaluation
    |
    +------ Invalid Records ------> Error Log
    |
    v
Validated Records
    |
    v
Database or Application Storage
    |
    v
Aggregation and Reporting
    |
    v
CSV Export
    |
    v
Output Validation and Delivery

The architecture separates file-format concerns from business rules and storage operations.

This separation makes it easier to replace the source system, change validation policies, or move from local file processing to database-backed imports.

## 20. Execution Requirements

| Deliverable | Runtime | External dependencies |
|---|---|---|
| Python | Python 3.10+ | None |
| JavaScript | Node.js 18+ | None |
| C++17 | C++17 compiler | None |
| Java | Java 17 | None |
| PostgreSQL | PostgreSQL 14+ and psql | None |

### Python

Run the script using Python 3.

The program creates a `csv_data` directory containing the source employee CSV, processed employee CSV, and department report.

### JavaScript

Run the file using Node.js.

The program creates a `csv_data` directory containing transaction input, processed transaction data, and regional reporting output.

### C++17

Compile using a C++17-compatible compiler.

The executable generates order input, processed order output, and product reporting files in its working directory.

### Java 17

Compile and run the `Main` class using Java 17.

The program generates an enterprise invoice dataset, accepted invoice export, and customer payment report.

### PostgreSQL

Execute the SQL script using `psql`.

The script creates the `csv_lab` schema and its associated tables, functions, views, indexes, sample records, and reporting queries.

The PostgreSQL example uses psql variable substitution for the generated batch identifier. The script is intended to be executed as a psql script rather than pasted directly into a generic SQL editor.

## 21. Technical Limitations

The examples implement the core CSV mechanisms needed to understand reliable import and export workflows. Some production requirements need additional infrastructure.

- The JavaScript, C++17, and Java examples use compact parsers for instructional purposes. Their line-oriented input implementations do not fully support multiline quoted records.
- The Python implementation uses the standard CSV parser, which provides more complete CSV record handling.
- The C++ implementation does not implement a configurable character encoding layer.
- The examples use in-memory duplicate tracking, which may require significant memory for extremely large files.
- Floating-point arithmetic is used in the JavaScript and C++ financial examples. Financial production systems should prefer integer minor units or decimal arithmetic.
- CSV does not preserve database types, constraints, relationships, or transaction boundaries.
- Spreadsheet formula sanitization requires testing against the target spreadsheet applications.
- Atomic replacement depends on filesystem capabilities and does not automatically guarantee crash durability.
- The SQL example uses PostgreSQL-specific functionality and psql commands.
- The JavaScript and Java examples process physical lines and should be replaced with a fully compliant CSV parser when multiline quoted records are expected.
- A production import pipeline should also define batch retry behavior, idempotency, concurrency control, retention, and operational monitoring.

The central engineering distinction is between parsing a CSV file successfully and accepting its records as valid business data. Reliable processing requires both.
