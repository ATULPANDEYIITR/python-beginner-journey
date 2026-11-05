# Working with JSON

## 1. Introduction

JSON (JavaScript Object Notation) is a text-based data interchange format used to represent structured information.

It is language-independent and commonly used for:

- REST API request and response bodies.
- Configuration files.
- Application settings.
- Event messages.
- Document-oriented storage.
- Data exchange between distributed services.
- Logging and monitoring.
- Structured application metadata.

JSON represents data using six fundamental value categories:

| JSON type | Description | Example |
|---|---|---|
| Object | Collection of key-value pairs | `{"name":"Atul"}` |
| Array | Ordered collection of values | `[10,20,30]` |
| String | Unicode text | `"India"` |
| Number | Integer or decimal number | `12500.50` |
| Boolean | Logical value | `true` |
| Null | Explicit absence of a value | `null` |

A JSON document can contain nested objects and arrays.

Example document:

    {
        "customer": {
            "id": 101,
            "name": "Atul Pandey",
            "address": {
                "city": "Lucknow",
                "country": "India"
            }
        },
        "active": true,
        "orders": [
            {
                "order_id": 5001,
                "amount": 66600
            }
        ]
    }

The structure represents a customer containing an address and multiple orders.

## 2. JSON Syntax and Data Rules

JSON syntax follows strict formatting rules.

### Objects

Objects use curly braces and contain key-value pairs.

- Keys must be strings enclosed in double quotation marks.
- A colon separates each key from its value.
- Commas separate individual properties.
- Duplicate keys should be rejected by strict application-level validation.

### Arrays

Arrays use square brackets.

They can contain different JSON types, including objects, strings, numbers, booleans, and null values.

Array positions are zero-indexed in Python, JavaScript, C++, and Java implementations.

### Strings

JSON strings use double quotation marks.

Special characters must be escaped.

| Character | JSON representation |
|---|---|
| Double quotation mark | `\"` |
| Backslash | `\\` |
| Newline | `\n` |
| Tab | `\t` |
| Carriage return | `\r` |
| Backspace | `\b` |
| Form feed | `\f` |

Unicode characters can be represented using `\uXXXX` escape sequences.

Surrogate pairs represent Unicode characters outside the Basic Multilingual Plane.

### Numbers

JSON supports integer and decimal number representations, including scientific notation.

Examples:

- `100`
- `-25`
- `12500.50`
- `2.5e3`

JSON does not define `NaN`, positive infinity, or negative infinity as valid numeric values.

Applications should account for numeric precision when processing financial information.

## 3. Serialization and Deserialization

These are the two fundamental JSON operations.

### Serialization

Serialization converts an in-memory data structure into a JSON string.

    Application Object
           |
           v
    JSON Serializer
           |
           v
       JSON Text
           |
           v
    File / API / Network

Examples:

| Language | Serialization |
|---|---|
| Python | `json.dumps()` |
| JavaScript | `JSON.stringify()` |
| C++ | `JSONSerializer::stringify()` |
| Java | `JSONSerializer.stringify()` |
| PostgreSQL | `jsonb_build_object()` |

Serialization is useful when transmitting application data or storing structured documents.

### Deserialization

Deserialization converts JSON text into an application data structure.

    JSON Text
        |
        v
    JSON Parser
        |
        v
    Application Object
        |
        v
    Validation
        |
        v
    Business Processing

Examples:

| Language | Deserialization |
|---|---|
| Python | `json.loads()` |
| JavaScript | `JSON.parse()` |
| C++ | `JSONParser::parse()` |
| Java | `JSONParser.parse()` |
| PostgreSQL | `::JSONB` conversion |

Parsing verifies syntax. It does not automatically establish that the document satisfies application business rules.

## 4. JSON Objects and Arrays

### Objects

Objects represent entities with named properties.

Example:

    {
        "customer_id": 101,
        "name": "Atul Pandey",
        "status": "active",
        "balance": 12500.50
    }

Python represents objects using dictionaries.

JavaScript represents them using objects.

C++ uses a map-based object representation.

Java uses maps in the implementation.

PostgreSQL provides JSON and JSONB document types.

### Arrays

Arrays represent ordered collections.

Example:

    [
        {
            "product": "Laptop",
            "price": 65000,
            "quantity": 1
        },
        {
            "product": "Mouse",
            "price": 800,
            "quantity": 2
        }
    ]

Arrays are useful for representing:

- Order items.
- Employee collections.
- Transaction records.
- API results.
- Event histories.

Array elements can be processed using loops, streams, array methods, and database expansion functions.

## 5. Nested JSON

Nested JSON represents hierarchical information.

For example:

    {
        "customer": {
            "profile": {
                "name": "Atul Pandey"
            },
            "address": {
                "city": "Lucknow"
            }
        }
    }

The city is located at:

`customer.address.city`

Nested access mechanisms differ between implementations.

| Language | Access mechanism |
|---|---|
| Python | Dictionary indexing |
| JavaScript | Object property access |
| C++ | `JSONValue::at()` |
| Java | Nested map access |
| PostgreSQL | `->`, `->>`, `#>`, `#>>` |

Applications should handle missing properties explicitly.

A missing property is different from a property whose value is JSON `null`.

## 6. JSON Validation

Validation determines whether a parsed document satisfies an expected structure and business rules.

Three validation levels are important.

### Syntax validation

Checks whether the document follows JSON grammar.

Examples of invalid syntax:

- Missing closing braces.
- Trailing commas.
- Unquoted property names.
- Invalid escape sequences.
- Invalid numeric representations.

### Structural validation

Checks whether required properties exist and have appropriate types.

Example customer requirements:

| Property | Required type | Rule |
|---|---|---|
| `customerId` | Integer | Positive |
| `name` | String | Non-empty |
| `email` | String | Valid email format |
| `status` | String | Allowed status |
| `balance` | Number | Non-negative |

### Business validation

Checks application-specific rules.

Examples:

- An order must contain at least one item.
- A quantity must be positive.
- A product price cannot be negative.
- A customer must be eligible to place an order.
- An order identifier must be unique.

The Python and Java implementations separate domain validation from JSON parsing.

The PostgreSQL implementation uses a validation function returning a JSON array of errors.

## 7. JSON Schema Concepts

JSON Schema is a specification for describing and validating JSON document structures.

Common schema keywords include:

| Keyword | Purpose |
|---|---|
| `type` | Specifies the expected data type |
| `properties` | Defines object properties |
| `required` | Identifies mandatory properties |
| `items` | Defines array element structure |
| `minimum` | Defines a numeric lower bound |
| `maximum` | Defines a numeric upper bound |
| `minLength` | Defines minimum string length |
| `maxLength` | Defines maximum string length |
| `enum` | Restricts values to an allowed set |
| `additionalProperties` | Controls unexpected properties |

The implementations use explicit application-level validation rather than depending on an external JSON Schema library.

This makes the examples self-contained, but does not implement the complete JSON Schema specification.

## 8. JSON File Handling

JSON is commonly used for configuration and persistent document storage.

A typical file workflow is:

    Application Data
          |
          v
      Serialization
          |
          v
      Temporary File
          |
          v
      File Replacement
          |
          v
       JSON File
          |
          v
        Reading
          |
          v
      Deserialization

The Python, JavaScript, and Java implementations demonstrate file persistence.

Important considerations include:

- UTF-8 encoding.
- File existence.
- File permissions.
- File size limits.
- Invalid document handling.
- Interrupted writes.
- Atomic replacement where supported.
- Temporary file cleanup.

Writing to a temporary file before replacing the destination reduces the risk of leaving a partially written document.

Atomic file replacement does not automatically provide concurrent-writer coordination or guaranteed durability after sudden hardware failure.

## 9. JSON Transformation

JSON transformation changes the structure or content of an existing document.

Typical operations include:

- Adding properties.
- Updating values.
- Removing properties.
- Filtering array elements.
- Combining objects.
- Extracting nested values.
- Converting relational records into JSON.

Example:

Original:

    {
        "order_id": 5001,
        "status": "pending"
    }

Updated:

    {
        "order_id": 5001,
        "status": "completed"
    }

The Python implementation uses nested dictionary updates.

The JavaScript implementation uses object transformation.

The PostgreSQL implementation demonstrates `jsonb_set`, the subtraction operator, and JSONB concatenation.

## 10. JSON Processing in Python

The Python implementation uses the standard-library `json` module.

### Main mechanisms

| Mechanism | Purpose |
|---|---|
| `json.dumps()` | Serialize Python values |
| `json.loads()` | Parse JSON text |
| `json.JSONDecodeError` | Handle syntax errors |
| `object_pairs_hook` | Inspect object key-value pairs |
| `parse_constant` | Control non-standard numeric constants |
| `Path.read_text()` | Read JSON files |
| `Path.write_text()` | Write JSON files |
| `dataclasses` | Represent structured application entities |
| `Enum` | Restrict status values |

### Custom parsing controls

The implementation rejects duplicate object keys.

It also rejects non-standard numerical constants and limits nesting depth.

These controls prevent ambiguous documents from silently entering the application.

### Domain modeling

The `Customer` and `Order` dataclasses represent business entities.

The `RecordStatus` enumeration restricts customer status values.

The validation function converts an untrusted dictionary into a validated customer instance.

### Security

Sensitive properties such as passwords, API keys, and tokens are removed recursively before external sharing.

The script also applies a file-size limit.

A checksum is calculated using SHA-256 over compact, sorted-key JSON.

This canonicalization is useful for repeatable hashing within the implementation, although it is not a complete implementation of a standardized canonical JSON format.

## 11. JSON Processing in JavaScript

JavaScript has native JSON support.

### Main mechanisms

| Mechanism | Purpose |
|---|---|
| `JSON.stringify()` | Convert objects into JSON |
| `JSON.parse()` | Parse JSON strings |
| `Object.hasOwn()` | Check own properties |
| `Object.entries()` | Iterate over properties |
| `Map` | Maintain indexed order records |
| `Set` | Maintain sensitive property names |
| `Promise` | Represent asynchronous operations |
| `async/await` | Coordinate asynchronous file operations |
| `EventEmitter` | Process application events |

### Event-driven JSON processing

The implementation uses an event processor for order creation.

    Order Request
         |
         v
    Event Publisher
         |
         v
    order.created
         |
         v
    Order Service
         |
         v
    Map Storage

This separates the publication of an event from the service responsible for processing the order.

### Asynchronous file operations

Node.js file operations use promises.

The repository writes serialized data to a temporary file and renames it after successful writing.

### API response processing

The API response handler checks:

- HTTP response status.
- Response content type.
- Response size.
- JSON syntax.
- Document nesting.

A syntactically valid response is not necessarily a valid business record.

The application must perform domain validation separately.

## 12. JSON Processing in C++17

C++ does not include a native JSON library in its standard library.

The implementation therefore provides a self-contained JSON value model and recursive-descent parser.

### JSON value representation

The `JSONValue` class uses `std::variant` to represent:

- Null.
- Boolean.
- Number.
- String.
- Array.
- Object.

The object representation uses `std::map`.

The array representation uses `std::vector`.

### Recursive-descent parsing

The parser processes JSON according to its grammar.

    JSON Input
        |
        v
    Token Inspection
        |
        v
    Value Parsing
        |
        +------ Object
        |
        +------ Array
        |
        +------ String
        |
        +------ Number
        |
        +------ Boolean
        |
        +------ Null

The parser uses separate methods for objects, arrays, strings, and numbers.

It rejects:

- Duplicate object keys.
- Invalid escape sequences.
- Invalid numeric formats.
- Unclosed strings.
- Trailing content.
- Excessive nesting.
- Non-finite numeric values.

Unicode escape sequences are converted into UTF-8.

### Serialization

The serializer recursively traverses the value model.

It escapes special characters and produces valid JSON text.

The object representation provides ordered keys through `std::map`.

### Engineering considerations

A custom parser gives control over parsing behavior but requires careful maintenance.

Production implementations should use a mature JSON library when complete Unicode validation, advanced interoperability, extensive testing, or high-performance parsing is required.

The demonstration parser does not implement a complete validation of raw UTF-8 byte sequences.

## 13. JSON Processing in Java 17

Java 17 does not provide a general-purpose JSON parser in its standard library.

The implementation includes a recursive-descent parser and serializer.

### Domain model

Java records provide immutable representations for:

- Customers.
- Products.
- Orders.

The compact constructors enforce validation at object creation.

The `CustomerStatus` enumeration restricts status values.

### Service layer

The `OrderService` manages order registration, duplicate detection, retrieval, and calculation.

The service uses a `HashMap` for efficient identifier-based lookup.

### Serialization

The serializer handles:

- Strings.
- Numbers.
- Booleans.
- Null.
- Maps.
- Collections.

Unsupported Java objects are rejected instead of being silently converted.

### Persistence

`JSONFileRepository` handles file storage.

It checks file size and uses a temporary file before replacing the destination.

The implementation also uses SHA-256 for hashing serialized documents.

### Enterprise considerations

The domain layer, validation layer, service layer, and persistence layer have separate responsibilities.

This structure reduces the coupling between document parsing and business operations.

The demonstration parser handles common JSON syntax but is not a replacement for a fully tested production JSON implementation.

## 14. JSON in PostgreSQL

PostgreSQL provides two important JSON data types.

### JSON

`JSON` stores JSON text and validates its syntax.

It preserves the original textual representation.

### JSONB

`JSONB` stores JSON in a decomposed binary representation.

It supports indexing and efficient document-oriented operations.

| Feature | JSON | JSONB |
|---|---|---|
| Syntax validation | Yes | Yes |
| Original whitespace preservation | Yes | No |
| Original object key order | Preserved in text | Not preserved |
| Duplicate keys | Retained in input text | Reduced to the last value |
| GIN indexing | No native JSON indexing | Supported |
| Containment operations | Limited | Supported |
| JSONPath operations | Supported through relevant functions | Supported |

JSONB is suitable for workloads involving frequent querying, containment checks, and indexing.

It should not be treated as a replacement for every relational table.

## 15. PostgreSQL JSON Operators

The SQL implementation demonstrates the principal JSONB operators.

| Operator | Function |
|---|---|
| `->` | Retrieve an object property as JSON |
| `->>` | Retrieve an object property as text |
| `#>` | Retrieve a nested value as JSON |
| `#>>` | Retrieve a nested value as text |
| `?` | Check whether an object contains a key |
| `?|` | Check whether any specified keys exist |
| `?&` | Check whether all specified keys exist |
| `@>` | Check JSONB containment |
| `<@` | Check contained-by relationship |
| `||` | Combine JSONB objects or arrays |
| `-` | Remove a property or array element |
| `#-` | Remove a nested property |

Example nested retrieval:

`payload #>> '{metadata,currency}'`

This extracts the currency property as text.

## 16. JSON Aggregation and Transformation in PostgreSQL

PostgreSQL can construct JSON directly from relational data.

Important functions include:

| Function | Purpose |
|---|---|
| `jsonb_build_object()` | Build a JSON object |
| `jsonb_build_array()` | Build a JSON array |
| `jsonb_agg()` | Aggregate values into a JSON array |
| `jsonb_object_agg()` | Aggregate key-value pairs |
| `jsonb_array_elements()` | Expand a JSON array |
| `jsonb_each()` | Expand object properties |
| `jsonb_typeof()` | Identify a JSON value type |
| `jsonb_set()` | Update a nested value |
| `jsonb_path_exists()` | Evaluate a JSONPath condition |

The SQL implementation combines relational order information into JSON documents using a view.

This demonstrates a useful integration pattern:

    Relational Tables
          |
          v
      SQL JOIN
          |
          v
    JSON Aggregation
          |
          v
     JSONB Document
          |
          v
     API / Reporting

The CTE example expands order items and calculates document-level totals.

## 17. JSONPath

JSONPath provides a standardized way to query structured JSON data using path expressions.

It supports nested navigation, filtering, and matching.

Example:

`$.items[*] ? (@.unit_price > 1000)`

This expression searches the items array for objects whose unit price exceeds 1000.

PostgreSQL supports JSONPath through functions such as:

- `jsonb_path_exists()`
- `jsonb_path_match()`
- `jsonb_path_query()`
- `jsonb_path_query_array()`

JSONPath is useful when nested conditions become more complicated than simple property access.

## 18. JSON and Relational Database Design

JSON and relational tables solve different data-modeling problems.

### Relational data

Relational tables are appropriate for:

- Customer identifiers.
- Product catalogs.
- Financial transactions.
- Inventory.
- Foreign-key relationships.
- Uniqueness requirements.
- Frequently joined business entities.

### JSON documents

JSON is appropriate for:

- Variable metadata.
- External API payloads.
- Event attributes.
- Flexible configuration.
- Optional properties.
- Heterogeneous document structures.

### Hybrid approach

The PostgreSQL implementation uses relational tables for customers, products, orders, and order items.

JSONB stores incoming order documents.

This provides relational integrity while supporting flexible document ingestion.

A document containing a numeric customer identifier does not automatically create a foreign-key relationship with the customer table.

Cross-document referential integrity must be enforced explicitly when required.

## 19. Error Handling and Failure Conditions

JSON processing can fail at multiple stages.

| Failure | Example | Handling |
|---|---|---|
| Syntax error | Missing closing brace | Reject during parsing |
| Type error | String supplied for numeric field | Reject during validation |
| Missing property | No customer identifier | Report validation error |
| Duplicate key | Repeated object property | Reject ambiguous input |
| Excessive nesting | Deeply nested document | Enforce depth limit |
| Excessive size | Oversized API response | Reject before processing |
| Invalid number | `NaN` | Reject |
| File error | Missing or inaccessible file | Handle I/O exception |
| Business error | Negative order quantity | Reject during domain validation |
| Duplicate record | Existing order identifier | Reject during service processing |

Applications should distinguish parsing errors from validation errors and business-processing errors.

This separation improves debugging and makes error reporting more precise.

## 20. JSON Security

JSON is a data format, not a security boundary.

A valid JSON document can still contain malicious or unauthorized information.

Important security controls include:

### Input limits

Apply limits to:

- Document size.
- Nesting depth.
- Array length.
- String length.
- Numeric ranges.
- Processing time.

### Sensitive information

Avoid exposing:

- Passwords.
- Access tokens.
- API keys.
- Session identifiers.
- Confidential customer information.

The Python, JavaScript, and Java examples recursively remove selected sensitive properties before sharing data.

This filtering is a demonstration, not a complete data-loss prevention system.

### SQL injection

Use parameterized SQL statements when JSON values originate from application input.

Never construct SQL commands by concatenating untrusted JSON strings.

### Access control

Validate whether the requesting user is authorized to access the customer, order, or document.

Successful JSON parsing does not establish authorization.

### Database protection

Use database permissions, appropriate indexes, constraints, and transaction boundaries.

Avoid exposing internal database documents directly without checking which properties are safe to return.

## 21. Performance Considerations

JSON processing performance depends on document size, nesting, query patterns, and transformation requirements.

| Operation | Main consideration |
|---|---|
| Parsing | Linear traversal of input in typical parsers |
| Serialization | Traversal of the complete data structure |
| Nested property access | Depends on the object representation |
| Array filtering | Usually linear in array length |
| File processing | Memory and disk I/O |
| JSONB containment | Benefits from appropriate GIN indexes |
| JSON aggregation | Depends on row count and aggregation size |
| Repeated document updates | Can increase storage and write costs |

### Memory considerations

The Python, JavaScript, C++, and Java examples load complete documents into memory.

This is appropriate for bounded documents.

Very large datasets may require streaming parsers or incremental processing.

### PostgreSQL indexing

The SQL implementation creates a GIN index using `jsonb_path_ops`.

This supports relevant JSONB containment queries.

The operator class has a narrower set of supported operators than the default JSONB GIN operator class.

Index selection should follow actual query patterns.

Indexes also increase storage requirements and write overhead.

## 22. Implementation Comparison

| Feature | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| JSON parsing | Standard library | Native support | Custom parser | Custom parser | Native |
| Serialization | Standard library | Native support | Custom serializer | Custom serializer | Native |
| Nested access | Dictionaries | Objects | JSONValue | Maps | JSONB operators |
| Validation | Functions and dataclasses | Validation classes | Domain classes | Records and services | PL/pgSQL |
| Arrays | Lists | Arrays | Vectors | Collections | JSONB arrays |
| File operations | pathlib | Node.js fs | Not implemented | NIO | Database storage |
| Error handling | Exceptions | Exceptions | Exceptions | Custom exceptions | SQL exceptions |
| Document querying | Python functions | Object navigation | Object access | Map access | JSONPath and operators |
| Security filtering | Recursive transformation | Recursive transformation | Domain validation | Recursive transformation | Constraints and validation |

## 23. Practical JSON Workflow

A reliable application workflow separates data ingestion, validation, transformation, and persistence.

    External Data Source
            |
            v
       Receive JSON
            |
            v
       Size Checking
            |
            v
       JSON Parsing
            |
            v
      Syntax Validation
            |
            v
    Structural Validation
            |
            v
     Business Validation
            |
            v
       Transformation
            |
            v
      Authorization
            |
            v
      Persistence
            |
            v
      Reporting / API

Each stage has a different responsibility.

Parsing establishes whether the input is valid JSON.

Structural validation checks the expected document shape.

Business validation checks domain rules.

Authorization checks access rights.

Persistence records the validated information.

This separation makes JSON processing easier to maintain, test, and debug.

## 24. Executable Deliverables

| File | Main implementation | Runtime |
|---|---|---|
| Python | JSON serialization, validation, file handling, sanitization | Python 3 |
| JavaScript | Event-driven order processing and asynchronous persistence | Node.js 18+ |
| C++ | Recursive-descent JSON parser and serializer | C++17 |
| Java | Enterprise domain model, custom parser, and persistence service | Java 17 |
| PostgreSQL | JSONB storage, validation, indexing, transformation, and reporting | PostgreSQL |

The five implementations demonstrate different approaches to processing the same underlying JSON data model.

The custom C++ and Java parsers intentionally cover common JSON structures and syntax rather than implementing every feature of a production-grade JSON library. Unicode normalization, complete raw UTF-8 validation, streaming parsing, and standardized JSON Schema validation require additional dedicated implementations.
