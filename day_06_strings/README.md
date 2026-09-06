# Python Strings

## Introduction

A string in Python is an immutable sequence of Unicode characters. Strings are used to represent names, identifiers, sentences, configuration values, source text, serialized data, user input, file content, protocol data, and many other forms of textual information.

Python provides a rich string model that supports indexing, slicing, iteration, searching, replacement, splitting, joining, formatting, Unicode processing, regular expressions, parsing, validation, and transformation.

The accompanying Python script progresses from basic string operations to advanced topics such as Unicode normalization, text encoding, regular expressions, string algorithms, tries, edit distance, security considerations, performance, and production-oriented text processing.

## Fundamental String Concepts

### Creating strings

Strings can be created using single quotes, double quotes, or triple quotes.

Examples include:

    "Python"
    'Python'
    """A multiline string"""

Single and double quotes create the same fundamental type. The choice between them is primarily a matter of readability and the need to avoid unnecessary escaping.

Triple-quoted strings are commonly used for multiline text and documentation strings.

### Empty strings

An empty string is represented by:

    ""

Its length is zero, and it is false in a Boolean context.

    bool("")  # False

A non-empty string is true in a Boolean context.

### String type

The Python type for strings is `str`.

    value = "Python"
    type(value)

The result is:

    <class 'str'>

Strings are Unicode text rather than raw byte sequences.

## Immutability

Python strings are immutable. After a string object has been created, its individual characters cannot be modified.

An operation such as:

    text = "hello"
    text.upper()

does not modify `text`. It returns another string.

To produce a modified string, a new string must be constructed.

For example:

    text = "hello"
    text = "H" + text[1:]

Immutability provides important benefits. Strings can safely be used as dictionary keys and set members because their value cannot change after hashing.

It also means that repeated transformations may create new string objects, which matters when processing very large amounts of text.

## Indexing

A string is a sequence, so individual characters can be accessed by position.

For:

    text = "PYTHON"

the indexes are:

    P  Y  T  H  O  N
    0  1  2  3  4  5

Negative indexes count from the end:

    -6 -5 -4 -3 -2 -1
     P  Y  T  H  O  N

An index outside the valid range raises `IndexError`.

## Slicing

Slicing extracts a portion of a string.

The general syntax is:

    string[start:stop:step]

The `stop` position is exclusive.

Examples:

    text[0:2]
    text[:2]
    text[2:]
    text[::2]
    text[::-1]

A slice normally creates a new string. Unlike indexing, an out-of-range slice does not raise `IndexError`; Python simply returns the available portion.

A slice with a step of zero is invalid and raises `ValueError`.

## Iteration

Strings are iterable.

    for character in "Python":
        ...

Iteration processes one Unicode code point at a time.

`enumerate()` can be used when both the position and character are needed.

    for index, character in enumerate("Python"):
        ...

## Membership Testing

The `in` and `not in` operators test whether text occurs within another string.

    "Py" in "Python"
    "Java" not in "Python"

Substring membership is generally more useful than manually iterating through every character for ordinary containment tests.

## String Operators

Important operators include:

| Operation | Meaning |
|---|---|
| `+` | Concatenation |
| `*` | Repetition |
| `in` | Membership |
| `not in` | Negative membership |
| `[]` | Indexing |
| `[:]` | Slicing |

For example:

    "Hello" + " " + "World"
    "ha" * 3

## Length

`len()` returns the number of Unicode code points in a string.

    len("Python")

The value returned by `len()` is not necessarily the number of visible characters a person perceives. Some visible characters can consist of multiple Unicode code points.

This distinction becomes important with combining marks, emoji sequences, and grapheme clusters.

# Core String Methods

## Case Conversion

Python provides several case-related methods.

### `lower()`

Converts applicable characters to lowercase.

### `upper()`

Converts applicable characters to uppercase.

### `capitalize()`

Capitalizes the first character while applying lowercase behavior to the remainder according to Python's string semantics.

### `title()`

Produces title-style capitalization.

### `swapcase()`

Switches uppercase characters to lowercase and lowercase characters to uppercase.

### `casefold()`

`casefold()` is designed for Unicode-aware case-insensitive comparisons and is more aggressive than `lower()`.

For example, German `ß` demonstrates why simple lowercase conversion is not always sufficient for case-insensitive comparison.

A typical comparison strategy is:

    first.casefold() == second.casefold()

This should still be used according to the requirements of the application because case-insensitive comparison is a semantic decision.

## Searching

### `find()`

`find()` returns the position of the first occurrence of a substring.

If the substring does not exist, it returns `-1`.

### `index()`

`index()` also searches for a substring, but it raises `ValueError` when the substring does not exist.

This distinction is important:

| Method | Missing substring |
|---|---|
| `find()` | Returns `-1` |
| `index()` | Raises `ValueError` |

### `rfind()`

`rfind()` searches from the right and returns the highest matching position.

### `count()`

`count()` counts non-overlapping occurrences of a substring.

For example, counting `"aa"` in `"aaaa"` produces two because the occurrences do not overlap.

Overlapping substring counting requires a different algorithm.

## Prefix and Suffix Tests

`startswith()` tests whether a string begins with a specified prefix.

`endswith()` tests whether a string ends with a specified suffix.

Both support tuples of possible prefixes or suffixes.

These methods are preferable to manually slicing when the actual intention is to test a prefix or suffix.

## Trimming

The methods `strip()`, `lstrip()`, and `rstrip()` remove characters from the ends of strings.

    strip()
    lstrip()
    rstrip()

An important distinction is that `strip()` does not remove an exact substring. It treats its argument as a set of removable characters.

For exact prefix and suffix removal, Python provides:

    removeprefix()
    removesuffix()

This distinction prevents subtle bugs when processing identifiers, filenames, protocol fields, and other structured strings.

## Replacement

`replace()` creates a new string with occurrences of one substring replaced by another.

It can optionally receive a maximum replacement count.

    text.replace("old", "new")
    text.replace("old", "new", 1)

Because strings are immutable, the original string remains unchanged unless the result is assigned back to the same variable.

# Splitting and Joining

## `split()`

`split()` divides a string into a list.

    "Python is useful".split()

When no separator is supplied, Python treats runs of whitespace as separators and does not produce empty fields for repeated whitespace.

A specific separator can also be provided.

    "a,b,c".split(",")

The `maxsplit` argument limits the number of splits.

## `partition()`

`partition()` divides a string into exactly three components:

1. text before the separator,
2. the separator,
3. text after the separator.

For:

    "key=value".partition("=")

the conceptual result is:

    ("key", "=", "value")

If the separator is absent, the original string is returned as the first component, followed by two empty strings.

`partition()` is particularly useful when only the first separator matters.

## `join()`

`join()` combines an iterable of strings.

    ", ".join(["Python", "SQL", "Excel"])

The elements must be strings. Non-string elements cause `TypeError`.

When constructing a large string from many pieces, collecting the pieces and joining them is generally preferable to repeatedly constructing intermediate strings.

# Character Classification

Python provides methods for determining properties of characters and strings.

Important methods include:

- `isalpha()`
- `isalnum()`
- `isdigit()`
- `isdecimal()`
- `isnumeric()`
- `isspace()`
- `islower()`
- `isupper()`
- `istitle()`

These methods are Unicode-aware and should not automatically be interpreted as ASCII-only checks.

## `isdigit()`, `isdecimal()`, and `isnumeric()`

These methods have different definitions.

A character can be numeric without being a decimal digit. Superscript digits and Roman numeral characters illustrate why the methods should not be treated as interchangeable.

Use the method that matches the actual validation requirement.

# String Formatting

Python supports several generations of formatting techniques.

## Percent Formatting

The `%` operator supports older-style formatting.

    "Name: %s" % name

It remains valid but is generally less expressive than modern formatting approaches.

## `str.format()`

The `format()` method supports positional and named replacement fields.

    "Name: {}".format(name)

Named fields improve readability when a format contains many values.

## F-Strings

F-strings provide concise expression-based formatting.

    f"Name: {name}"

Expressions can be evaluated directly:

    f"Next year: {age + 1}"

F-strings support formatting specifications such as:

    f"{number:.2f}"
    f"{number:,.2f}"
    f"{value:^10}"

They also support debugging-oriented representations:

    f"{value!r}"

F-strings are usually the clearest choice for ordinary application-level string construction.

# Escape Sequences

Common escape sequences include:

| Escape | Meaning |
|---|---|
| `\n` | Newline |
| `\t` | Tab |
| `\\` | Backslash |
| `\'` | Single quote |
| `\"` | Double quote |
| `\r` | Carriage return |
| `\b` | Backspace |
| `\f` | Form feed |

Escape sequences are interpreted by Python string literals.

## Raw Strings

Raw string literals suppress most backslash escape processing.

    r"C:\Users\student\Documents"

Raw strings are especially convenient for Windows paths and regular expression patterns.

They still have syntactic restrictions. A raw string cannot end with an odd number of backslashes because the final backslash would interfere with the closing quote.

# Unicode

Python 3 strings are Unicode text.

A string can contain characters from many writing systems and symbol sets.

Examples include:

    "नमस्ते"
    "你好"
    "مرحبا"
    "😀"
    "₹"

`ord()` returns a character's Unicode code point.

`chr()` converts a code point back into a character.

Unicode makes Python suitable for multilingual text processing, but correct text handling requires understanding encoding, normalization, comparison, and display.

# Unicode Code Points and Grapheme Clusters

A Unicode string is not necessarily equivalent to a sequence of visually perceived characters.

For example, an accented character may be represented as:

- a single precomposed code point, or
- a base character followed by a combining mark.

Emoji sequences can also consist of multiple code points that render as one visible symbol.

Therefore:

    len(text)

counts Python string elements represented by Unicode code points, not necessarily user-perceived characters.

This distinction matters for:

- user interface character limits,
- cursor movement,
- text editing,
- internationalization,
- validation,
- display calculations.

# Unicode Normalization

Unicode provides normalization forms for dealing with equivalent or compatibility-related representations.

The Python `unicodedata` module provides:

- NFC
- NFD
- NFKC
- NFKD

NFC generally favors composed representations.

NFD decomposes characters where applicable.

NFKC and NFKD additionally apply compatibility transformations.

Normalization can be useful before comparisons or searches, but it should be applied deliberately. Compatibility normalization can change distinctions that matter to a particular application.

# Encoding and Decoding

A Python `str` represents text.

A `bytes` object represents a sequence of bytes.

Conversion from text to bytes is encoding:

    text.encode("utf-8")

Conversion from bytes to text is decoding:

    data.decode("utf-8")

UTF-8 is a widely used Unicode encoding and is commonly used at system boundaries.

The important conceptual model is:

    text -> encode -> bytes
    bytes -> decode -> text

Confusing these two levels is a common source of Unicode errors.

# Encoding Errors

When text contains characters that an encoding cannot represent, encoding may raise `UnicodeEncodeError`.

Similarly, decoding invalid byte sequences can raise `UnicodeDecodeError`.

Python provides error handling strategies such as:

- `strict`
- `ignore`
- `replace`

Ignoring invalid data can cause silent corruption, so error policies should be chosen according to the requirements of the system.

# Bytes Versus Strings

`str` and `bytes` are not interchangeable.

A string is text.

Bytes are binary data.

For example:

    "A"[0]

returns the string `"A"`.

But:

    b"A"[0]

returns the integer representing the byte value.

This distinction becomes important when handling:

- files,
- sockets,
- network protocols,
- encryption,
- compressed data,
- binary formats.

# String Translation

`str.maketrans()` and `translate()` support efficient character-level transformation.

They can:

- map characters,
- map Unicode code points,
- replace characters,
- delete characters.

For example, punctuation can be removed using a translation table.

This can be clearer and sometimes more efficient than repeatedly calling `replace()` for many individual characters.

# Regular Expressions

The `re` module provides regular expression support.

Regular expressions are useful when ordinary string methods are insufficient for pattern matching.

Important operations include:

- `re.search()`
- `re.match()`
- `re.fullmatch()`
- `re.findall()`
- `re.finditer()`
- `re.sub()`
- `re.split()`

## `search()`

Searches for a matching region anywhere in the text.

## `fullmatch()`

Requires the entire input to match the pattern.

This distinction is important for validation.

A pattern that merely searches for a valid-looking substring is not necessarily a valid input validator.

## Compiled Patterns

Patterns used repeatedly can be compiled:

    pattern = re.compile(...)

The compiled object can then be reused.

This improves organization and can avoid repeated pattern compilation.

# Regular Expression Groups

Parentheses create capturing groups.

Named groups provide readable access to matched values.

A pattern can define:

    (?P<name>...)

The resulting match object can expose named groups through `group()` and `groupdict()`.

This is useful for parsing structured text.

# Greedy and Non-Greedy Matching

Regular expression quantifiers are generally greedy by default.

A greedy pattern attempts to consume as much text as possible while still allowing the overall pattern to match.

Adding `?` to an appropriate quantifier creates non-greedy behavior.

For example:

    .*

is greedy, while:

    .*?

is non-greedy.

The distinction is important when extracting repeated structures.

# Regular Expression Security

Regular expressions can consume significant computational resources, especially poorly designed patterns with ambiguous nested repetition.

Applications processing attacker-controlled input should avoid patterns susceptible to catastrophic backtracking.

Useful defensive principles include:

- keep patterns simple,
- constrain input lengths,
- avoid ambiguous nested quantifiers,
- prefer explicit character classes,
- use full matching for validation,
- benchmark suspicious patterns,
- consider timeouts or safer pattern engines when appropriate.

# Parsing Structured Text

Strings frequently represent structured information.

Examples include:

- key-value records,
- configuration files,
- logs,
- protocol messages,
- CSV,
- JSON,
- URLs.

Simple formats can sometimes be parsed with `split()` and `partition()`.

For standardized formats, specialized parsers are safer.

For example, CSV cannot reliably be parsed with:

    line.split(",")

because quoted fields may contain commas.

The Python `csv` module correctly handles many CSV-specific rules.

# JSON Strings

JSON is a structured data format commonly represented as text.

Python's `json` module provides:

- `json.dumps()` for serialization,
- `json.loads()` for deserialization.

Unicode handling can be controlled through options such as `ensure_ascii`.

Serialization and parsing should be performed with a real JSON parser rather than manually manipulating JSON strings.

# URL Encoding

URL components have their own encoding rules.

The `urllib.parse` module provides functions such as:

- `quote()`
- `urlencode()`

URL encoding should not be confused with:

- HTML escaping,
- SQL escaping,
- shell escaping,
- JSON serialization.

Escaping is context-dependent.

# Text Cleaning

A text-cleaning pipeline may involve:

1. Unicode normalization,
2. whitespace normalization,
3. case normalization,
4. punctuation handling,
5. application-specific validation.

For example:

    text = unicodedata.normalize("NFC", text)
    text = " ".join(text.split())
    text = text.casefold()

The exact sequence depends on the purpose of the text.

Aggressive normalization can destroy information, so cleaning should not be performed automatically without understanding the domain.

# String Algorithms

The Python script implements several algorithms that demonstrate practical string processing.

## Palindrome Detection

A palindrome reads the same forward and backward.

A simple implementation compares:

    text == text[::-1]

For phrases, normalization can remove spaces and punctuation before comparison.

## Anagram Detection

Two strings are anagrams when they contain the same character frequencies under the chosen normalization rules.

`collections.Counter` provides an efficient way to compare frequencies.

## Character Frequency

A `Counter` can count occurrences of individual characters.

This is useful for:

- frequency analysis,
- duplicate detection,
- anagram checking,
- text statistics.

## First Non-Repeating Character

Character counts can be computed first, followed by a second traversal that preserves original order.

This produces a time complexity proportional to the length of the input.

## Removing Duplicate Characters

A set can track characters already encountered while a list preserves their first-occurrence order.

The result can then be constructed with `join()`.

# Run-Length Encoding

Run-length encoding represents consecutive repeated characters using a character and count.

For example, a sequence conceptually resembling:

    aaabbcccc

can become:

    a3b2c4

The example implementation also provides decoding.

This demonstrates an important edge case: encoded counts must be parsed correctly, and malformed input should be rejected.

Run-length encoding is useful for demonstrating compression concepts but is not universally effective compression. Its usefulness depends on the structure of the data.

# ROT13

ROT13 rotates ASCII alphabetic characters by 13 positions.

Applying ROT13 twice returns the original text.

The implementation demonstrates:

- character classification,
- `ord()`,
- `chr()`,
- modular arithmetic.

ROT13 is not encryption and should never be treated as a security mechanism.

# Longest Common Prefix

The longest common prefix problem finds the longest initial sequence shared by multiple strings.

The implementation progressively reduces a candidate prefix as each new string is compared.

This is a common interview-style algorithm that demonstrates indexing, slicing, iteration, and complexity reasoning.

# Levenshtein Distance

Levenshtein distance measures the minimum number of:

- insertions,
- deletions,
- substitutions

required to transform one string into another.

The implementation uses dynamic programming.

For strings of lengths `m` and `n`, the standard dynamic programming formulation requires:

- `O(mn)` time,
- `O(min(m,n))` additional space in the optimized implementation.

Applications include:

- spell correction,
- fuzzy matching,
- record linkage,
- approximate search,
- similarity analysis.

# Substring Search

The script demonstrates both a straightforward substring search and the Knuth-Morris-Pratt algorithm.

## Naive Search

The naive method checks possible starting positions directly.

Its worst-case behavior can be proportional to the product of text and pattern lengths.

It is simple and often adequate for small inputs.

## Knuth-Morris-Pratt

KMP preprocesses the pattern into a longest-prefix-suffix table.

The search phase can operate in linear time relative to the text and pattern after preprocessing.

The implementation demonstrates the important relationship between prefix structure and efficient pattern matching.

# Tries

A trie, or prefix tree, stores strings character by character.

It is useful for:

- autocomplete,
- prefix lookup,
- dictionary search,
- routing-like prefix structures.

The script implements insertion, exact lookup, and prefix lookup.

A trie can use substantial memory because each character can create nodes and dictionary entries.

# String Hashing

Python strings are hashable.

They can therefore be used as:

- dictionary keys,
- set elements,
- cache keys.

Python's built-in `hash()` should not be treated as a persistent or cross-process stable fingerprint. Python uses hash randomization, so the value can differ between processes.

For stable digests, a cryptographic hash such as SHA-256 can be produced using `hashlib`.

# Memoization

Strings can serve as keys for memoization because they are immutable and hashable.

The script demonstrates `functools.lru_cache`.

Memoization is useful when the same string inputs repeatedly produce the same computational result.

It should be applied carefully because caching large numbers of large strings can consume significant memory.

# Sorting Strings

By default, strings are sorted lexicographically according to Python's comparison semantics.

For case-insensitive sorting, a key such as:

    key=str.casefold

can be used.

Sorting according to human language rules is more complex than ordinary Unicode code-point ordering and may require locale-aware or specialized collation behavior.

# String-Based Stack Parsing

Balanced-bracket validation demonstrates how strings can be processed using a stack.

Opening brackets are pushed onto the stack.

Closing brackets must match the most recent opening bracket.

This technique illustrates a general parsing principle: nested structures are naturally handled with stack-based processing.

# Security Considerations

Strings are a major boundary between applications and external data, so string processing is closely connected with security.

## SQL Injection

Never construct SQL by concatenating untrusted strings.

Conceptually unsafe construction resembles:

    "SELECT ... WHERE username = '" + username + "'"

Use parameterized database queries instead.

## Shell Injection

Do not construct shell commands by concatenating untrusted strings.

When operating-system commands are genuinely required, prefer APIs such as `subprocess` with explicit argument lists and `shell=False`.

## HTML Injection and XSS

HTML output requires HTML-context escaping.

The `html.escape()` function can encode characters that have special meaning in HTML.

Escaping is context-specific. HTML escaping does not automatically make a string safe for JavaScript, SQL, shell commands, or other contexts.

## Passwords and Secrets

Passwords, API tokens, session tokens, and other secrets should not be printed in logs.

String length can be inspected for validation without exposing the actual secret.

Passwords should not be stored as plaintext merely because Python represents them as strings. Proper authentication systems use suitable password hashing mechanisms.

## Constant-Time Comparison

Sensitive token comparisons can be performed using `hmac.compare_digest()` when appropriate.

This is intended to reduce timing-related information leakage compared with ordinary equality checks in security-sensitive comparison scenarios.

It does not solve authentication design problems by itself.

## Log Injection

Untrusted strings containing newline or control characters can make logs misleading.

Using structured logging and appropriate escaping reduces the risk of log-forging problems.

## Unicode Confusables

Unicode permits visually similar characters from different scripts.

Two characters may look similar while being distinct code points.

This matters for:

- usernames,
- domain names,
- account identifiers,
- security-sensitive labels.

Security-sensitive systems may need restricted character sets, normalization, identifier policies, and specialized confusable-character analysis.

# Performance Considerations

String operations have different computational and memory characteristics.

Important principles include:

- indexing is generally constant-time in Python's string representation,
- slicing creates a new string,
- concatenation creates new string values,
- `join()` is generally appropriate for assembling many fragments,
- regular expressions can be computationally expensive,
- normalization adds processing cost,
- caching can improve repeated computation but consume memory.

For large text construction, a common pattern is:

    parts = []
    parts.append(...)
    parts.append(...)
    result = "".join(parts)

For truly large data, processing the entire text as one giant string may itself be inappropriate. Line-oriented or chunk-oriented processing can reduce peak memory consumption.

Performance assumptions should be validated using representative workloads rather than relying only on theoretical expectations.

# String Memory

`sys.getsizeof()` can provide information about the size of a Python string object, but it should not be treated as a universal measurement of total application memory consumption.

The actual memory cost of a text-processing system also depends on:

- temporary strings,
- containers,
- object references,
- caches,
- decoded representations,
- intermediate processing structures.

# Debugging Strings

`repr()` is particularly useful when debugging strings.

It makes characters such as:

- newline,
- tab,
- backslash,
- quotes

visible.

For example, comparing:

    print(value)

with:

    print(repr(value))

can reveal invisible whitespace and control characters.

This is useful when debugging parsing and validation failures.

# Common Mistakes

Several string-related mistakes occur frequently.

## Using `is` Instead of `==`

Use:

    first == second

for value comparison.

Do not use:

    first is second

to test whether two strings contain the same value.

`is` tests object identity, not value equality.

## Assuming Strings Are Mutable

Statements that attempt to assign to an individual string character fail because strings are immutable.

Construct a new string instead.

## Treating `strip()` as Exact Prefix Removal

`strip()` removes characters from the ends.

It does not remove an exact substring.

Use `removeprefix()` or `removesuffix()` for exact prefix or suffix removal.

## Using `split()` as a Complete Parser

Simple splitting is not a complete parser for formats such as CSV, JSON, or programming languages.

Use format-specific parsers for standardized data.

## Confusing `str` and `bytes`

Text and binary data are different abstraction levels.

Use explicit encoding and decoding at system boundaries.

## Assuming `lower()` Is Universal Case Normalization

Unicode case behavior can be more complex than simple lowercase conversion.

Use `casefold()` when an appropriate Unicode-aware case-insensitive comparison is required.

## Assuming `len()` Counts Visible Characters

`len()` counts Unicode code points, not necessarily grapheme clusters or visible glyphs.

## Interpolating Untrusted Data into Commands

String interpolation is convenient, but convenience does not make the resulting string safe for SQL, shell commands, HTML, or other execution contexts.

# Specialized Parsers

When a string represents a standardized data format, use the appropriate parser.

Examples include:

| Data | Appropriate Python facility |
|---|---|
| JSON | `json` |
| CSV | `csv` |
| URLs | `urllib.parse` |
| Regular expressions | `re` |
| HTML escaping | `html` |
| Cryptographic digests | `hashlib` |

The principle is to distinguish ordinary text manipulation from parsing a formal language.

# Domain-Specific Validation

String validation should reflect business rules.

A username validator in the script demonstrates explicit constraints:

- minimum length,
- maximum length,
- first-character rule,
- allowed character set.

Validation should be separated from formatting and presentation.

For complex applications, domain-specific string types can make invalid states harder to represent.

The script demonstrates this using immutable data classes such as a validated `Username` and `ProductCode`.

# String-Like Domain Objects

A raw string may represent a domain concept such as:

- username,
- product code,
- email address,
- account identifier,
- currency code,
- postal code.

Wrapping such values in a dedicated type allows validation and normalization to occur at the boundary.

This can make application code more explicit than passing unrestricted strings everywhere.

# String Representation

Python distinguishes between `str()` and `repr()`.

`str()` generally aims to provide a human-oriented representation.

`repr()` aims to provide an unambiguous or debugging-oriented representation.

Classes can customize these behaviors with:

    __str__()
    __repr__()

This distinction is especially valuable in logs, debugging, and diagnostic output.

# `None` Versus an Empty String

`None` and `""` have different meanings.

An empty string represents text containing zero characters.

`None` represents the absence of a value.

They should not be treated as interchangeable.

This distinction is important in:

- database values,
- optional fields,
- APIs,
- configuration,
- validation.

# String Constants

The `string` module provides useful constants such as:

- `ascii_lowercase`
- `ascii_uppercase`
- `digits`
- `punctuation`
- `whitespace`

These are useful when implementing character-level rules without manually reproducing character sets.

# Text Wrapping

The `textwrap` module can format long text for terminal output, reports, and fixed-width displays.

This is different from changing the underlying semantic content.

# Large Text Processing

Large text should not always be loaded into memory at once.

The script demonstrates generators that process chunks or lines.

A generator can yield one piece at a time, allowing downstream code to process data incrementally.

This pattern can reduce memory pressure when working with large files or streams.

# Production Considerations

Production text processing should account for:

- encoding boundaries,
- Unicode behavior,
- normalization rules,
- input validation,
- output escaping,
- secret handling,
- performance,
- memory consumption,
- parser correctness,
- logging safety,
- error handling,
- domain-specific semantics.

A robust implementation should make assumptions explicit.

For example, an identifier may intentionally be case-sensitive. Automatically applying `casefold()` could then create incorrect behavior.

Similarly, removing accents may improve search behavior in one application while destroying meaningful distinctions in another.

# Important Comparisons

| Concept | Important distinction |
|---|---|
| `==` vs `is` | Value equality vs object identity |
| `find()` vs `index()` | `-1` vs `ValueError` when absent |
| `split()` vs `partition()` | Multiple pieces vs exactly three pieces |
| `strip()` vs `removeprefix()` | Character-set trimming vs exact prefix removal |
| `lower()` vs `casefold()` | Basic lowercase vs stronger Unicode-aware comparison |
| `str` vs `bytes` | Text vs byte data |
| `encode()` vs `decode()` | Text to bytes vs bytes to text |
| `str()` vs `repr()` | Human-oriented vs diagnostic representation |
| `hash()` vs SHA-256 | Runtime hash-table value vs stable cryptographic digest |
| `split(",")` vs CSV parser | Simple delimiter splitting vs format-aware parsing |

# Algorithms Covered

The Python script includes complete implementations of:

- palindrome detection,
- phrase palindrome detection,
- anagram detection,
- character frequency,
- first non-repeating character,
- duplicate-character removal,
- word reversal,
- run-length encoding,
- run-length decoding,
- ROT13,
- longest common prefix,
- Levenshtein distance,
- naive substring search,
- Knuth-Morris-Pratt search,
- string rotation,
- bracket balancing,
- text tokenization,
- word-frequency analysis,
- prefix-tree insertion and lookup.

These examples demonstrate how fundamental string operations can be combined to solve larger problems.

# Testing

The script includes assertions for important functions and edge cases.

Testing string-processing code should include:

- empty strings,
- single-character strings,
- repeated characters,
- Unicode text,
- missing delimiters,
- invalid formats,
- very short inputs,
- very long inputs,
- unusual whitespace,
- malformed encoded data,
- case differences,
- normalization differences.

String bugs frequently occur at boundaries rather than in ordinary examples.

# Edge Cases

Important edge cases demonstrated by the script include:

- empty strings,
- whitespace-only strings,
- out-of-range indexing,
- out-of-range slicing,
- empty search patterns,
- missing separators,
- repeated separators,
- Unicode characters,
- combining characters,
- malformed run-length data,
- unmatched brackets,
- unclosed quoted fields,
- `None` values,
- extremely large rotation values,
- overlapping substring occurrences.

Handling these cases explicitly makes text-processing code more predictable.

# Practical Applications

String processing is central to many software systems.

Typical applications include:

- form validation,
- command-line interfaces,
- configuration processing,
- log analysis,
- search,
- autocomplete,
- natural-language preprocessing,
- data cleaning,
- ETL pipelines,
- API payload handling,
- document processing,
- text analytics,
- identifier validation,
- report generation,
- serialization,
- protocol parsing,
- security filtering.

String knowledge is therefore not limited to simple text manipulation. It connects directly to algorithms, data structures, software security, internationalization, and system design.
