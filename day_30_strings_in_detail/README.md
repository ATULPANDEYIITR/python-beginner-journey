# Strings in Detail

## Scope

Strings are sequences of textual data used throughout software systems for identifiers, configuration, logs, source code, network messages, user input, documents, search queries, and structured formats.

This repository presents strings from three complementary perspectives:

- Python provides a broad text-processing laboratory with executable examples for normalization, validation, tokenization, regular expressions, search algorithms, edit distance, files, streaming, redaction, and performance.
- JavaScript focuses on runtime-specific behavior, especially UTF-16 strings, Unicode iteration, event-driven processing, asynchronous text streams, regular expressions, and Node.js line processing.
- C++ implements a coherent text-search case study using an inverted index, tokenization, exact search, fuzzy matching, edit distance, validation, and sensitive-data redaction.

The central distinction is between treating a string as a simple sequence of characters and treating it as structured data whose encoding, normalization, parsing rules, ownership, performance, and security properties must be understood.

## Core String Model

A string can be viewed abstractly as an ordered sequence of textual units:

`S = s₀s₁s₂...sₙ₋₁`

The meaning of a string depends on what the program considers a unit.

That distinction matters because a byte, Unicode code point, UTF-16 code unit, and user-perceived character are not necessarily the same thing.

Python's `str` represents Unicode text and its indexing operates on Unicode code points. JavaScript strings use UTF-16 code units, so `length` does not necessarily equal the number of Unicode code points. C++ `std::string` is fundamentally a sequence of bytes, even though those bytes are often used to hold UTF-8 encoded text.

Consequently, code such as `length == number of visible characters` is not universally correct.

## Fundamental Operations

The Python implementation demonstrates indexing, slicing, reversing, membership tests, prefix and suffix checks, splitting, joining, replacement, trimming, and case conversion.

For example, `text[0]` accesses the first Python string element, while `text[::-1]` constructs a reversed string. Because Python strings are immutable, an operation such as `replace()` produces another string rather than changing the original object.

JavaScript provides similar operations through methods such as `slice()`, `substring()`, `includes()`, `startsWith()`, `endsWith()`, `replace()`, and `split()`. Template literals provide interpolation without requiring repeated concatenation.

C++ provides `std::string` and `std::string_view`. A `std::string` owns its character storage, while a `std::string_view` provides a non-owning view into existing character storage. A view must not outlive the storage to which it refers.

## Immutability and Construction

Strings are commonly immutable at the language level in Python and JavaScript. An expression that appears to modify a string generally creates another value.

This matters for large-scale processing. Repeatedly constructing larger strings can create many intermediate allocations.

The Python implementation demonstrates collecting fragments and using `join()`. The JavaScript implementation uses an array of fragments followed by `join()`. Both approaches make the intended assembly operation explicit.

The general pattern is:

`fragments -> collection -> single join operation`

For very large text, an application may instead process chunks incrementally rather than retaining the entire output in memory.

## Comparison and Case Handling

Exact string comparison is normally case-sensitive.

For example:

`"Admin" != "admin"`

Case-insensitive comparison requires an explicit policy. Python's `casefold()` is designed for Unicode-aware caseless comparison and is more appropriate than assuming that `lower()` handles every linguistic case.

Normalization and locale also matter. A comparison policy should specify whether text is normalized, whether case distinctions matter, and which locale rules apply.

A common engineering mistake is to use lowercasing as an implicit universal identity operation. Case transformation and identity comparison are different concerns.

## Whitespace and Cleaning

Whitespace processing should be defined rather than performed indiscriminately.

The Python program uses `strip()` to remove surrounding whitespace and `split()` followed by joining to collapse runs of whitespace in titles.

This is useful for controlled fields such as document titles, where repeated spaces have no semantic value.

The same approach would not necessarily be appropriate for source code, fixed-width records, passwords, cryptographic material, or text where whitespace itself carries meaning.

Cleaning should therefore be tied to the semantics of the input field.

## Validation

Validation determines whether text satisfies a required format.

The examples validate usernames using rules that specify:

- the first character must be lowercase alphabetic;
- subsequent characters may contain lowercase letters, digits, or underscores;
- the total length is bounded.

The title validator demonstrates a different validation problem. It accepts arbitrary text but rejects non-string values, empty content, and values exceeding a configured maximum.

These are different validation models. A username has a strict grammar, while a title has semantic constraints.

Production validation should also consider input size. Maximum lengths protect memory usage, reduce abuse opportunities, and make downstream behavior more predictable.

## Regular Expressions

Regular expressions describe patterns in text.

The Python implementation parses structured log lines into named fields such as date, level, user, and action. The JavaScript implementation performs the same type of parsing using JavaScript's named capture groups.

Regular expressions are particularly useful when the input has a stable lexical structure.

They become difficult to maintain when used as a substitute for a full parser for deeply nested or recursive formats.

A production regular expression should be reviewed for:

- correct anchoring;
- unexpected matches;
- invalid input;
- excessive backtracking where the engine permits it;
- Unicode behavior;
- maximum input size;
- whether the expression is actually the right parsing mechanism.

## Tokenization

Tokenization converts a continuous text stream into meaningful units.

The Python and JavaScript implementations recognize words, numbers, versions, percentages, and punctuation with patterns appropriate to the examples.

The C++ case study takes a simpler indexing-oriented approach. It treats alphanumeric runs as searchable terms and normalizes them to lowercase.

Tokenization is domain-specific.

A search engine, compiler, programming-language parser, natural-language system, log processor, and CSV parser require different tokenization rules.

There is no universal tokenizer that is correct for every text-processing problem.

## Unicode

Unicode assigns abstract code points to characters and symbols. Encoding determines how those code points are represented in memory or transmitted.

UTF-8 represents Unicode code points using one to four bytes. UTF-16 uses one or two 16-bit code units for a Unicode scalar value. UTF-32 uses fixed-width 32-bit code units for scalar values.

The number of bytes, code units, code points, and user-visible characters can therefore differ.

For example, an emoji such as `😀` requires two UTF-16 code units in JavaScript but represents one Unicode code point.

The JavaScript implementation explicitly compares:

`value.length`

with:

`[...value].length`

The first measures UTF-16 code units. The second iterates Unicode code points.

This distinction prevents incorrect assumptions about string length.

## Unicode Normalization

Visually equivalent text can have different internal representations.

The word `café` can contain a precomposed `é`, or it can contain `e` followed by a combining acute accent.

Consequently, two visually equivalent strings may fail direct equality.

Unicode normalization transforms equivalent sequences into defined canonical forms.

The examples use NFC normalization before comparison.

Normalization is especially relevant to:

- usernames;
- search indexes;
- document comparison;
- identifiers;
- deduplication;
- storage;
- security-sensitive comparisons.

Normalization should be applied according to an explicit application policy rather than automatically to every text field.

## User-Perceived Characters

A Unicode code point is not always the same as a user-perceived character.

Sequences involving combining marks, variation selectors, regional indicators, and zero-width joiners can form a single displayed unit while containing multiple code points.

For example, a family or profession emoji may contain several code points connected by zero-width joiners.

Therefore, displaying a substring based solely on code-point count can split a user-visible grapheme cluster.

Applications requiring accurate cursor movement, truncation, or character limits based on what users perceive may need grapheme-cluster-aware processing.

## Search Algorithms

The Python and JavaScript implementations include both naive substring search and Knuth-Morris-Pratt search.

Naive search compares the pattern against each possible starting position. Its worst-case running time is approximately `O(nm)` for text length `n` and pattern length `m`.

KMP preprocesses the pattern into a prefix table. When a mismatch occurs, it uses previously computed prefix information rather than restarting the comparison from scratch.

Its search phase is `O(n)` after `O(m)` preprocessing, giving `O(n + m)` total time.

The prefix table records the length of the longest proper prefix of the pattern that is also a suffix at each position.

The important algorithmic distinction is that KMP uses information about the pattern's internal structure to avoid redundant comparisons.

## Rolling Hash

The Python implementation also demonstrates a rolling-hash substring search.

Instead of comparing every candidate substring immediately, it computes a numeric hash for the pattern and for each text window.

When the window moves, the outgoing character is removed mathematically and the incoming character is incorporated.

A matching hash is not sufficient proof of equality because different strings can produce the same hash. The implementation therefore verifies the actual substring after a hash match.

This illustrates a general rule:

`hash equality -> candidate match`

not:

`hash equality -> guaranteed string equality`

## Edit Distance

Levenshtein distance measures the minimum number of single-character insertions, deletions, and substitutions required to transform one string into another.

The Python, JavaScript, and C++ implementations use dynamic programming.

The recurrence compares the cost of:

- inserting a character;
- deleting a character;
- substituting one character for another.

A complete matrix requires `O(nm)` space. The implementations optimize auxiliary space by retaining only the previous and current rows, reducing additional space to `O(min(n,m))`.

Edit distance is useful for:

- typo-tolerant search;
- spelling correction;
- duplicate detection;
- approximate matching;
- record reconciliation.

It can become expensive for very large strings or very large candidate sets, so production search systems commonly reduce the candidate set before calculating detailed distances.

## Python Implementation

The Python program is a broad executable laboratory for string processing.

Its progression includes fundamental operations, validation, search, regular expressions, Unicode normalization, tokenization, palindrome detection, anagrams, naive substring search, KMP, rolling hashes, edit distance, document statistics, CSV parsing, temporary text-file processing, streaming-style line processing, memoized recursive string computation, and redaction.

The `DocumentStats` dataclass demonstrates how textual measurements can be represented as structured data rather than printed as unrelated values.

The document analyzer extracts words with a Unicode-aware regular expression and calculates total words, unique words, lines, characters, and average word length.

The file-processing demonstration explicitly uses UTF-8 rather than relying on the host operating system's default encoding.

The streaming demonstration processes input line by line. This models how a production log processor can avoid loading an entire log into memory.

The security section illustrates why strings representing filenames, SQL values, and HTML content require context-specific validation or escaping.

## JavaScript Implementation

The JavaScript program emphasizes runtime-specific string behavior.

Its Unicode section demonstrates that JavaScript string indexing and `length` operate on UTF-16 code units. Spread iteration uses the string iterator and therefore works at Unicode code-point boundaries.

The program also uses regular expressions with Unicode property escapes such as `\p{L}` and `\p{N}`.

The `TextPipeline` class demonstrates an event-driven architecture. It normalizes input, emits a `normalized` event, tokenizes the resulting text, emits `tokenized`, constructs frequency information, and emits `analyzed`.

This design separates processing stages and illustrates how text transformations can become events in a Node.js application.

The asynchronous generator demonstrates chunk-oriented processing using `for await...of`. The example simulates delayed chunks, which is representative of the interface used by asynchronous streams.

The `readline` example demonstrates line-oriented processing without manually splitting a complete input string into an array of lines.

## C++ Case Study

The C++ program models a small document search engine.

A `Document` contains an identifier, title, and body.

`TextEngine` owns the document collection and an inverted index:

`unordered_map<string, unordered_map<int, size_t>>`

The outer map associates a normalized term with a posting map. The inner map associates each document identifier with the number of occurrences of that term.

For example, a term such as `string` can map to document identifiers and occurrence counts.

This structure changes exact term lookup from scanning every document's full body to an average constant-time hash lookup for the term, followed by processing of the matching posting list.

The engine validates document identifiers, titles, body size, and duplicate identifiers before indexing the document.

Tokenization occurs while adding a document. Terms are normalized to lowercase and punctuation is excluded from the searchable token.

Exact search retrieves matching postings and sorts results by occurrence count and then document identifier.

Fuzzy search compares the query against indexed terms using Levenshtein distance. This creates a realistic relationship between exact indexing and more expensive approximate matching.

The program also redacts email addresses before sensitive text is displayed.

## Ownership and Views in C++

The C++ case study uses `std::string_view` for functions that only need temporary read access.

For example, the edit-distance function does not need to take ownership of either input, so `string_view` avoids unnecessary copying.

This is safe only while the referenced strings remain alive and unchanged in ways that invalidate the view.

A `string_view` should not be stored beyond the lifetime of the source object unless the lifetime relationship is explicitly guaranteed.

This is a significant distinction from an owning `std::string`.

## Structured Text

Some textual formats should not be processed as arbitrary strings.

CSV has quoting, escaping, and delimiter rules. JSON has nested structure. Programming languages have lexical and syntactic grammars.

The Python example parses a simple CSV representation with `csv.DictReader`, rather than manually interpreting commas.

The JavaScript example intentionally uses a constrained CSV format to illustrate field extraction. It should not be treated as a complete RFC-compliant CSV parser because quoted commas and escaped quotes require additional grammar handling.

The design principle is to choose a parser appropriate to the format instead of assuming `split()` is universally correct.

## File Processing

Text files require explicit encoding decisions.

The Python program writes and reads UTF-8 explicitly.

This prevents behavior from changing merely because the program runs on a machine with a different default encoding.

Large files should normally be processed incrementally when possible.

A program that performs:

`entire_file = file.read()`

may be straightforward, but its memory consumption grows with the input size.

Line-oriented or chunk-oriented processing can keep memory usage bounded.

## String Security

Strings are a major boundary between trusted program state and untrusted external data.

A string must not be considered safe merely because it has been stored in a variable.

### SQL

User-provided strings should be supplied through parameterized database APIs.

String concatenation such as constructing SQL by directly inserting user input can turn ordinary text into executable SQL syntax.

The Python, JavaScript, and C++ examples describe or demonstrate the boundary without constructing unsafe SQL.

### HTML

Untrusted text must be escaped or safely rendered according to the output context.

A string intended to be displayed as text is different from a string intentionally interpreted as HTML.

In browser code, assigning untrusted content directly to `innerHTML` can create script-injection risks.

### Filesystem Paths

A filename field is not automatically equivalent to a safe filesystem path.

The Python example validates a simple filename grammar and rejects a traversal-style value such as `../../etc/passwd`.

Applications that genuinely accept paths require a different design involving canonicalization, allowed roots, authorization, and operating-system-specific rules.

### Regular Expressions

Regular expressions applied to untrusted, very large inputs can become a performance concern when the pattern causes excessive backtracking.

Input limits, carefully designed patterns, and appropriate parsing strategies reduce this risk.

## Redaction

Redaction is a transformation rather than a validation operation.

The examples replace email addresses with `[EMAIL]` and ticket identifiers with `[TICKET]`.

Redaction should occur before sensitive information reaches logs, analytics systems, telemetry, or user interfaces when those destinations are not authorized to receive the original data.

A redaction expression should be tested against realistic variations and known failure cases.

It should not be assumed to detect every possible representation of sensitive information.

## Common Failure Modes

### Confusing Bytes with Characters

UTF-8 text can use multiple bytes for a single Unicode code point. Byte length is therefore not a reliable user-facing character count.

### Assuming `length` Means Visible Characters

Python and JavaScript expose different string models, and neither simple length operation should automatically be interpreted as the number of grapheme clusters visible to a user.

### Using `split()` as a Universal Parser

Delimiters inside quoted fields, escaped characters, nesting, and multiline records can make simple splitting incorrect.

### Using Lowercasing as Universal Normalization

Case transformation, Unicode normalization, locale-sensitive comparison, and identifier policy are separate concerns.

### Building SQL with Concatenation

String interpolation does not turn untrusted data into safe database parameters.

### Treating Hashes as Proof of Equality

A hash collision is possible. Hash-based candidate matching must verify actual equality when correctness requires it.

### Ignoring Input Size

Regular expressions, edit-distance algorithms, repeated concatenation, and complete-file reads can all become expensive when input size is uncontrolled.

### Keeping Non-Owning String Views Too Long

A C++ `string_view` can refer to invalid memory if the original string is destroyed or its storage is invalidated.

## Performance Characteristics

| Operation | Typical complexity | Important consideration |
|---|---:|---|
| Direct equality | `O(n)` | Can stop early on mismatch |
| Prefix/suffix test | `O(n)` | Implementation-dependent constants |
| Naive substring search | `O(nm)` worst case | Simple and often adequate for small inputs |
| KMP search | `O(n + m)` | Requires `O(m)` prefix information |
| Rolling hash search | Approximately `O(n + m)` expected | Hash collisions require verification |
| Character frequency | `O(n)` | Memory depends on distinct symbols |
| Levenshtein distance | `O(nm)` | Can use reduced auxiliary space |
| Joining fragments | Approximately `O(total output)` | Avoids repeated intermediate concatenation |
| Inverted-index lookup | Average `O(1)` term lookup | Posting-list processing remains necessary |

The practical choice depends on input size, query frequency, alphabet, memory limits, latency requirements, and correctness requirements.

## Testing Strategy

String systems require tests that exercise both ordinary and adversarial inputs.

Important cases include:

- empty strings;
- one-character strings;
- strings containing only whitespace;
- leading and trailing whitespace;
- repeated whitespace;
- Unicode characters;
- combining marks;
- emoji sequences;
- malformed encodings at input boundaries;
- very long input;
- strings containing punctuation;
- repeated substrings;
- patterns longer than the searched text;
- empty search patterns;
- exact matches at the beginning or end;
- overlapping matches;
- edit-distance substitutions, insertions, and deletions;
- malformed structured records;
- sensitive values requiring redaction.

Algorithm tests should also compare optimized implementations against simpler reference implementations on generated inputs.

## Design Relationships

The three implementations use different levels of abstraction.

The Python program treats strings as a broad computational subject. It demonstrates individual mechanisms and connects them into progressively more advanced processing tasks.

The JavaScript program focuses on how string behavior interacts with a runtime. UTF-16 semantics, Unicode iteration, event-driven processing, asynchronous generators, and Node.js line handling become central design concerns.

The C++ program treats string processing as a system component. Documents enter through validation, text becomes tokens, tokens become index entries, queries use the index, approximate matching adds a dynamic-programming cost, and sensitive output is redacted before presentation.

These perspectives illustrate that string processing is not simply a collection of methods. It involves representation, semantics, algorithms, ownership, resource management, parsing rules, and security boundaries.

## Practical Architecture

A production text-processing pipeline can be conceptualized as:

`Input -> Validation -> Encoding Handling -> Normalization -> Tokenization -> Processing -> Storage/Index -> Query/Output`

Each stage has a distinct responsibility.

Validation determines whether the input is acceptable.

Encoding handling establishes what bytes represent.

Normalization establishes a canonical representation when the domain requires one.

Tokenization identifies meaningful units.

Processing performs operations such as search, classification, transformation, or statistics.

Storage or indexing determines how processed information can be retrieved efficiently.

Output handling determines how text is safely serialized, displayed, logged, or transmitted.

Keeping these responsibilities distinct prevents a single string-cleaning function from silently becoming a parser, validator, security filter, and normalization system at the same time.
