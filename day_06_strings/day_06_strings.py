"""
STRINGS IN PYTHON
=================

A comprehensive, self-contained study script covering Python strings from
absolute beginner concepts through advanced usage, algorithms, Unicode,
performance, validation, security, testing, and production considerations.

The script uses only Python's standard library.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re
import string
import sys
import timeit
import unicodedata
from functools import lru_cache
from typing import Iterable


# ============================================================================
# 1. WHAT IS A STRING?
# ============================================================================

def section(title: str) -> None:
    """Print a visually distinct section heading."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


section("1. STRING FUNDAMENTALS")

# A string is an immutable sequence of Unicode characters.
name = "Python"
message = 'Strings can use single or double quotes.'

print(name)
print(message)

# Triple quotes are useful for multiline strings.
multiline = """This is
a multiline
string."""

print(multiline)

# An empty string contains zero characters.
empty = ""
print("Empty string:", repr(empty))
print("Length:", len(empty))

# Strings can contain spaces, punctuation, digits, and symbols.
mixed = "Python 3.13: strings @ work!"
print(mixed)

# repr() shows a representation useful for debugging.
print("repr:", repr(mixed))


# ============================================================================
# 2. STRING CREATION AND QUOTING
# ============================================================================

section("2. CREATING STRINGS")

single_quoted = 'Hello'
double_quoted = "Hello"
apostrophe_example = "Python's string"
escaped_apostrophe = 'Python\'s string'

print(single_quoted == double_quoted)
print(apostrophe_example == escaped_apostrophe)

# Escape sequences represent special characters.
escaped = "Line 1\nLine 2\tIndented"
print(escaped)

# Common escape sequences:
# \n newline
# \t tab
# \\ backslash
# \' single quote
# \" double quote
# \r carriage return
# \b backspace
# \f form feed

# Raw strings suppress most backslash escape processing.
windows_path = r"C:\Users\student\Documents\file.txt"
print(windows_path)

# Raw strings have a subtle limitation: they cannot end with an odd number
# of backslashes because the final backslash would escape the closing quote.
# Therefore, r"C:\" is invalid Python syntax.


# ============================================================================
# 3. STRING TYPE AND IMMUTABILITY
# ============================================================================

section("3. TYPE AND IMMUTABILITY")

text = "hello"
print(type(text))
print(isinstance(text, str))

# Strings are immutable. Operations create new strings rather than changing
# the original string object.
original = "hello"
upper_text = original.upper()

print("Original:", original)
print("New:", upper_text)

# The following would raise TypeError if uncommented:
# original[0] = "H"

# To change a string, construct a new string.
modified = "H" + original[1:]
print(modified)

# Identity and equality are different concepts.
a = "python"
b = "".join(["py", "thon"])

print("Equal values:", a == b)
print("Same object:", a is b)

# Use == for value comparison. Do not use is to compare string values.


# ============================================================================
# 4. INDEXING
# ============================================================================

section("4. STRING INDEXING")

text = "PYTHON"

print(text[0])
print(text[1])
print(text[5])

# Negative indexes count from the end.
print(text[-1])
print(text[-2])

# Indexing outside the valid range raises IndexError.
try:
    print(text[100])
except IndexError as error:
    print("Handled:", error)


# ============================================================================
# 5. SLICING
# ============================================================================

section("5. STRING SLICING")

text = "PYTHON"

print(text[0:2])
print(text[:2])
print(text[2:])
print(text[:])
print(text[-3:])
print(text[:-2])

# Slice syntax:
# sequence[start:stop:step]
print(text[::2])
print(text[1::2])

# Negative step reverses a string.
print(text[::-1])

# A slice outside the normal range is safe.
print(text[100:200])
print(text[-100:2])

# Step cannot be zero.
try:
    print(text[::0])
except ValueError as error:
    print("Handled:", error)


# ============================================================================
# 6. ITERATION
# ============================================================================

section("6. ITERATING OVER STRINGS")

word = "Python"

for character in word:
    print(character)

# enumerate() provides indexes and characters.
for index, character in enumerate(word):
    print(index, character)

# Membership testing.
print("P" in word)
print("z" not in word)


# ============================================================================
# 7. LENGTH AND BASIC OPERATORS
# ============================================================================

section("7. STRING OPERATORS")

first = "Hello"
second = "World"

print(first + " " + second)
print("ha" * 3)
print(len(first))

print("Hello" in first)
print("x" in first)

# Lexicographic comparison is based on Unicode code points.
print("apple" < "banana")
print("A" < "a")

# ord() returns a character's Unicode code point.
print(ord("A"))
print(ord("₹"))

# chr() converts a Unicode code point to a character.
print(chr(65))
print(chr(8377))


# ============================================================================
# 8. COMMON STRING METHODS
# ============================================================================

section("8. CASE CONVERSION")

text = "Python Programming"

print(text.lower())
print(text.upper())
print(text.title())
print(text.capitalize())
print(text.swapcase())

# casefold() is intended for aggressive, Unicode-aware case-insensitive
# comparisons.
print("Straße".lower())
print("Straße".casefold())
print("STRASSE".casefold() == "Straße".casefold())


section("9. SEARCHING")

text = "Python programming is powerful."

print(text.find("programming"))
print(text.find("Java"))  # -1 means not found.

print(text.index("programming"))

try:
    print(text.index("Java"))
except ValueError as error:
    print("index() error:", error)

print(text.rfind("o"))
print(text.count("o"))

print(text.startswith("Python"))
print(text.endswith("."))

print(text.startswith(("Java", "Python")))
print(text.endswith((".", "!")))


section("10. TRIMMING")

text = "   Python programming   "

print(repr(text.strip()))
print(repr(text.lstrip()))
print(repr(text.rstrip()))

# strip() removes characters from the ends, not an exact substring.
value = "---Python---"
print(value.strip("-"))

# To remove an exact prefix or suffix, use removeprefix() and removesuffix().
print(value.removeprefix("---"))
print(value.removesuffix("---"))


section("11. REPLACEMENT")

text = "I like Java. Java is popular."
print(text.replace("Java", "Python"))
print(text.replace("Java", "Python", 1))

# replace() creates a new string.
print(text)


section("12. SPLITTING AND JOINING")

sentence = "Python is easy to learn"
words = sentence.split()

print(words)

csv_line = "apple,banana,orange"
items = csv_line.split(",")
print(items)

# maxsplit limits the number of splits.
print("a:b:c:d".split(":", 2))

# partition() always returns exactly three components.
print("name=Atul".partition("="))
print("name".partition("="))

# join() combines strings using a separator.
print(", ".join(["Python", "SQL", "Excel"]))

# A common mistake is calling join() on a list containing non-strings.
try:
    print(", ".join(["Python", 123]))
except TypeError as error:
    print("Handled:", error)


# ============================================================================
# 9. STRING CLASSIFICATION METHODS
# ============================================================================

section("13. CHARACTER CLASSIFICATION")

samples = ["12345", "123.45", "abc", "ABC", "abc123", "   ", "Python_3"]

for sample in samples:
    print(
        repr(sample),
        "isalpha=", sample.isalpha(),
        "isdigit=", sample.isdigit(),
        "isdecimal=", sample.isdecimal(),
        "isnumeric=", sample.isnumeric(),
        "isalnum=", sample.isalnum(),
        "isspace=", sample.isspace(),
        "islower=", sample.islower(),
        "isupper=", sample.isupper(),
        "istitle=", sample.istitle(),
    )

# isdigit(), isdecimal(), and isnumeric() are not identical.
unicode_numbers = ["2", "²", "Ⅳ"]

for value in unicode_numbers:
    print(
        repr(value),
        "decimal:", value.isdecimal(),
        "digit:", value.isdigit(),
        "numeric:", value.isnumeric(),
    )


# ============================================================================
# 10. STRING FORMATTING
# ============================================================================

section("14. STRING FORMATTING")

name = "Atul"
age = 33

# Old-style formatting.
print("Name: %s, Age: %d" % (name, age))

# str.format().
print("Name: {}, Age: {}".format(name, age))
print("Name: {0}, Age: {1}".format(name, age))

# Named fields.
print("Name: {name}, Age: {age}".format(name=name, age=age))

# f-strings are generally the clearest modern approach.
print(f"Name: {name}, Age: {age}")

# Expressions can be evaluated inside f-strings.
print(f"Next year: {age + 1}")

# Formatting numbers.
price = 123456.789
print(f"{price:.2f}")
print(f"{price:,.2f}")
print(f"{0.875:.1%}")

# Alignment and width.
print(f"{'Python':>10}")
print(f"{'Python':<10}")
print(f"{'Python':^10}")
print(f"{42:05d}")

# repr-style conversion is useful for debugging.
value = "hello\nworld"
print(f"{value!r}")


# ============================================================================
# 11. STRING TRANSLATION
# ============================================================================

section("15. TRANSLATION TABLES")

translation_table = str.maketrans({
    "a": "@",
    "e": "3",
    "i": "1",
})

print("security".translate(translation_table))

# delete characters by mapping them to None.
delete_vowels = str.maketrans("", "", "aeiouAEIOU")
print("Python Programming".translate(delete_vowels))


# ============================================================================
# 12. STRING CONSTANTS
# ============================================================================

section("16. STRING CONSTANTS")

print(string.ascii_lowercase)
print(string.ascii_uppercase)
print(string.digits)
print(string.punctuation)
print(string.whitespace)


# ============================================================================
# 13. STRING COMPARISON AND NORMALIZATION
# ============================================================================

section("17. NORMALIZING TEXT FOR COMPARISON")

def normalize_basic(text: str) -> str:
    """Normalize ordinary user input for simple comparisons."""
    return " ".join(text.casefold().strip().split())


examples = [
    "  Python   Programming ",
    "PYTHON programming",
    "python PROGRAMMING",
]

for example in examples:
    print(repr(example), "=>", repr(normalize_basic(example)))

print(
    normalize_basic("Python   Programming")
    == normalize_basic(" python programming ")
)


# ============================================================================
# 14. UNICODE
# ============================================================================

section("18. UNICODE")

unicode_text = "Hello, नमस्ते, 你好, مرحبا, 😀, ₹"

print(unicode_text)
print("Characters:", len(unicode_text))

for character in "A₹😀":
    print(
        character,
        "code point:",
        ord(character),
        "name:",
        unicodedata.name(character, "UNKNOWN"),
    )

# Python strings represent Unicode text. Encoding converts text to bytes.
encoded = "नमस्ते".encode("utf-8")
print("UTF-8 bytes:", encoded)

decoded = encoded.decode("utf-8")
print("Decoded:", decoded)

# A decoding operation using the wrong encoding can fail.
try:
    print(encoded.decode("ascii"))
except UnicodeDecodeError as error:
    print("Handled:", error)


# ============================================================================
# 15. UNICODE NORMALIZATION
# ============================================================================

section("19. UNICODE NORMALIZATION FOR EQUIVALENCE")

# Some visually identical Unicode text can have different internal
# representations.
composed = "é"
decomposed = "e\u0301"

print(composed == decomposed)

normalized_composed = unicodedata.normalize("NFC", decomposed)
print(normalized_composed == composed)

normalized_decomposed = unicodedata.normalize("NFD", composed)
print(repr(normalized_decomposed))

# NFKC and NFKD apply compatibility normalization as well.
compatibility_example = "①"
print(unicodedata.normalize("NFKC", compatibility_example))


# ============================================================================
# 16. BYTES VS STR
# ============================================================================

section("20. STR VERSUS BYTES")

text = "Python"
data = b"Python"

print(type(text))
print(type(data))

print(text[0])
print(data[0])

# str represents text; bytes represents raw byte data.
# Converting text to bytes requires an encoding.
encoded_text = text.encode("utf-8")
decoded_text = encoded_text.decode("utf-8")

print(encoded_text)
print(decoded_text)


# ============================================================================
# 17. STRING ITERABLE BEHAVIOR
# ============================================================================

section("21. STRINGS AS ITERABLES")

word = "cat"

print(list(word))
print(tuple(word))
print(set(word))

# A one-character string is still a string.
print(type(word[0]))


# ============================================================================
# 18. LIST OF CHARACTERS AND MUTABILITY
# ============================================================================

section("22. MODIFYING A STRING INDIRECTLY")

text = "hello"

characters = list(text)
characters[0] = "H"

new_text = "".join(characters)

print(text)
print(new_text)

# For a small number of changes, slicing can be simpler.
new_text = "H" + text[1:]
print(new_text)


# ============================================================================
# 19. PERFORMANCE: CONCATENATION
# ============================================================================

section("23. STRING CONCATENATION AND PERFORMANCE")

pieces = ["Python", "is", "fast", "to", "learn"]

# Prefer join() when assembling many strings.
joined = " ".join(pieces)
print(joined)

# Repeated += in a loop can be less appropriate for large-scale text
# construction. A list followed by join() is explicit and efficient.
result_parts: list[str] = []

for piece in pieces:
    result_parts.append(piece)

print(" ".join(result_parts))

# A small benchmark illustrates relative behavior. Exact results depend on
# Python version, hardware, workload, and implementation details.
concat_time = timeit.timeit(
    "' '.join(['Python', 'is', 'efficient'])",
    number=100_000,
)

print("Example join benchmark:", concat_time)


# ============================================================================
# 20. MEMORY AND IMMUTABILITY
# ============================================================================

section("24. STRING MEMORY CONSIDERATIONS")

text = "Python"
print("Size in memory:", sys.getsizeof(text), "bytes")

# The exact size is implementation-dependent. Do not use getsizeof() as a
# universal measure of the total memory cost of an application's text data.


# ============================================================================
# 21. REGULAR EXPRESSIONS
# ============================================================================

section("25. REGULAR EXPRESSIONS")

email_pattern = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

emails = [
    "student@example.com",
    "invalid-email",
    "user@example",
]

for email in emails:
    print(email, bool(email_pattern.fullmatch(email)))

# Search finds a matching region.
text = "Order ID: 12345"
match = re.search(r"\d+", text)

if match:
    print("Found number:", match.group())

# findall() returns all matching strings.
print(re.findall(r"\d+", "A12 B345 C6"))

# sub() replaces matches.
print(re.sub(r"\s+", "-", "Python   is\tpowerful"))


# ============================================================================
# 22. REGEX GROUPS
# ============================================================================

section("26. REGULAR EXPRESSION GROUPS")

pattern = re.compile(r"(?P<name>[A-Za-z]+)-(?P<id>\d+)")

match = pattern.fullmatch("Atul-123")

if match:
    print(match.group("name"))
    print(match.group("id"))
    print(match.groupdict())


# ============================================================================
# 23. REGEX GREEDINESS
# ============================================================================

section("27. GREEDY AND NON-GREEDY MATCHING")

text = "<a>one</a><a>two</a>"

greedy = re.search(r"<a>.*</a>", text)
non_greedy = re.search(r"<a>.*?</a>", text)

print("Greedy:", greedy.group() if greedy else None)
print("Non-greedy:", non_greedy.group() if non_greedy else None)


# ============================================================================
# 24. VALIDATION
# ============================================================================

section("28. VALIDATING USER INPUT")

def validate_username(username: str) -> bool:
    """
    Validate a username using explicit rules.

    Rules:
    - 3 to 20 characters
    - starts with a letter
    - contains only letters, digits, and underscores
    """
    if not 3 <= len(username) <= 20:
        return False

    if not username[0].isalpha():
        return False

    return all(character.isalnum() or character == "_" for character in username)


usernames = ["Atul_123", "ab", "123abc", "valid_user", "invalid-user"]

for username in usernames:
    print(username, validate_username(username))


# ============================================================================
# 25. PARSING
# ============================================================================

section("29. STRING PARSING")

record = "name=Atul;role=student;country=India"

parsed: dict[str, str] = {}

for field in record.split(";"):
    key, separator, value = field.partition("=")

    if separator:
        parsed[key.strip()] = value.strip()

print(parsed)


# ============================================================================
# 26. SAFE PARSING CONSIDERATIONS
# ============================================================================

section("30. PARSING EDGE CASES")

def parse_key_value_record(record: str) -> dict[str, str]:
    """Parse semicolon-separated key=value fields safely."""
    result: dict[str, str] = {}

    for field in record.split(";"):
        field = field.strip()

        if not field:
            continue

        key, separator, value = field.partition("=")

        if not separator:
            raise ValueError(f"Invalid field: {field!r}")

        key = key.strip()
        value = value.strip()

        if not key:
            raise ValueError("Key cannot be empty")

        result[key] = value

    return result


for record in [
    "name=Atul;role=student",
    "name=Atul;;role=student;",
]:
    print(parse_key_value_record(record))

try:
    parse_key_value_record("name=Atul;invalid")
except ValueError as error:
    print("Handled:", error)


# ============================================================================
# 27. TEXT CLEANING PIPELINE
# ============================================================================

section("31. TEXT CLEANING PIPELINE")

def clean_text(text: str) -> str:
    """
    Clean ordinary natural-language input.

    This operation:
    1. strips leading/trailing whitespace,
    2. normalizes repeated whitespace,
    3. applies Unicode-aware case folding.
    """
    text = unicodedata.normalize("NFC", text)
    text = " ".join(text.split())
    return text.casefold()


raw_text = "  Python   PROGRAMMING \n\t"
print(repr(clean_text(raw_text)))


# ============================================================================
# 28. WORD FREQUENCY
# ============================================================================

section("32. WORD FREQUENCY ANALYSIS")

def word_frequency(text: str) -> Counter[str]:
    """Return case-insensitive word frequencies."""
    words = re.findall(r"\b[\w']+\b", text.casefold())
    return Counter(words)


sample_text = """
Python is powerful.
Python is readable.
Readable Python is useful.
"""

frequency = word_frequency(sample_text)

for word, count in frequency.most_common():
    print(word, count)


# ============================================================================
# 29. PALINDROMES
# ============================================================================

section("33. PALINDROME DETECTION")

def is_palindrome(text: str) -> bool:
    """Return True when the string reads identically forward and backward."""
    return text == text[::-1]


def is_phrase_palindrome(text: str) -> bool:
    """Ignore case and non-alphanumeric characters."""
    normalized = "".join(
        character.casefold()
        for character in text
        if character.isalnum()
    )
    return normalized == normalized[::-1]


print(is_palindrome("level"))
print(is_palindrome("python"))

print(is_phrase_palindrome("Madam, I'm Adam"))
print(is_phrase_palindrome("Python"))


# ============================================================================
# 30. ANAGRAMS
# ============================================================================

section("34. ANAGRAM DETECTION")

def are_anagrams(first: str, second: str) -> bool:
    """Compare normalized character frequencies."""
    normalize = lambda value: [
        character.casefold()
        for character in value
        if character.isalnum()
    ]

    return Counter(normalize(first)) == Counter(normalize(second))


print(are_anagrams("listen", "silent"))
print(are_anagrams("The eyes", "They see"))


# ============================================================================
# 31. CHARACTER FREQUENCY
# ============================================================================

section("35. CHARACTER FREQUENCY")

def character_frequency(text: str) -> Counter[str]:
    return Counter(text)


print(character_frequency("banana"))


# ============================================================================
# 32. FIRST NON-REPEATING CHARACTER
# ============================================================================

section("36. FIRST NON-REPEATING CHARACTER")

def first_non_repeating_character(text: str) -> str | None:
    counts = Counter(text)

    for character in text:
        if counts[character] == 1:
            return character

    return None


print(first_non_repeating_character("swiss"))
print(first_non_repeating_character("aabb"))


# ============================================================================
# 33. REMOVE DUPLICATE CHARACTERS
# ============================================================================

section("37. REMOVING DUPLICATE CHARACTERS")

def remove_duplicate_characters(text: str) -> str:
    """Preserve first occurrence order."""
    seen: set[str] = set()
    result: list[str] = []

    for character in text:
        if character not in seen:
            seen.add(character)
            result.append(character)

    return "".join(result)


print(remove_duplicate_characters("programming"))


# ============================================================================
# 34. REVERSE WORDS
# ============================================================================

section("38. REVERSING WORD ORDER")

def reverse_words(sentence: str) -> str:
    return " ".join(sentence.split()[::-1])


print(reverse_words("Python is easy to learn"))


# ============================================================================
# 35. RUN-LENGTH ENCODING
# ============================================================================

section("39. RUN-LENGTH ENCODING")

def run_length_encode(text: str) -> str:
    """Compress consecutive identical characters."""
    if not text:
        return ""

    result: list[str] = []
    count = 1

    for index in range(1, len(text)):
        if text[index] == text[index - 1]:
            count += 1
        else:
            result.append(f"{text[index - 1]}{count}")
            count = 1

    result.append(f"{text[-1]}{count}")
    return "".join(result)


def run_length_decode(encoded: str) -> str:
    """Decode output produced by run_length_encode()."""
    result: list[str] = []
    index = 0

    while index < len(encoded):
        character = encoded[index]
        index += 1

        start = index

        while index < len(encoded) and encoded[index].isdigit():
            index += 1

        if start == index:
            raise ValueError("Missing count in encoded string")

        count = int(encoded[start:index])

        if count < 1:
            raise ValueError("Count must be positive")

        result.append(character * count)

    return "".join(result)


encoded = run_length_encode("aaabbcccc")
print(encoded)
print(run_length_decode(encoded))


# ============================================================================
# 36. ROT13
# ============================================================================

section("40. CHARACTER TRANSFORMATION")

def rot13(text: str) -> str:
    """Apply ROT13 to ASCII letters while leaving other characters unchanged."""
    result: list[str] = []

    for character in text:
        if "a" <= character <= "z":
            result.append(chr((ord(character) - ord("a") + 13) % 26 + ord("a")))
        elif "A" <= character <= "Z":
            result.append(chr((ord(character) - ord("A") + 13) % 26 + ord("A")))
        else:
            result.append(character)

    return "".join(result)


encoded = rot13("Hello, Python!")
print(encoded)
print(rot13(encoded))


# ============================================================================
# 37. LONGEST COMMON PREFIX
# ============================================================================

section("41. LONGEST COMMON PREFIX")

def longest_common_prefix(strings: Iterable[str]) -> str:
    values = list(strings)

    if not values:
        return ""

    prefix = values[0]

    for value in values[1:]:
        common_length = 0

        for left, right in zip(prefix, value):
            if left != right:
                break
            common_length += 1

        prefix = prefix[:common_length]

        if not prefix:
            break

    return prefix


print(longest_common_prefix(["flower", "flow", "flight"]))
print(longest_common_prefix(["dog", "racecar", "car"]))
print(longest_common_prefix([]))


# ============================================================================
# 38. LEVENSHTEIN DISTANCE
# ============================================================================

section("42. EDIT DISTANCE")

def levenshtein_distance(first: str, second: str) -> int:
    """
    Calculate the minimum number of insertions, deletions, and substitutions
    required to transform one string into another.

    Time complexity: O(m*n)
    Space complexity: O(min(m,n))
    """
    if len(first) < len(second):
        first, second = second, first

    previous = list(range(len(second) + 1))

    for i, left in enumerate(first, start=1):
        current = [i]

        for j, right in enumerate(second, start=1):
            insertion = current[j - 1] + 1
            deletion = previous[j] + 1
            substitution = previous[j - 1] + (left != right)

            current.append(min(insertion, deletion, substitution))

        previous = current

    return previous[-1]


print(levenshtein_distance("kitten", "sitting"))
print(levenshtein_distance("", "abc"))


# ============================================================================
# 39. NAIVE SUBSTRING SEARCH
# ============================================================================

section("43. SUBSTRING SEARCH ALGORITHM")

def naive_find(text: str, pattern: str) -> int:
    """
    Find pattern using direct character-by-character comparison.

    Returns the first index or -1.
    """
    if pattern == "":
        return 0

    if len(pattern) > len(text):
        return -1

    for start in range(len(text) - len(pattern) + 1):
        if text[start:start + len(pattern)] == pattern:
            return start

    return -1


print(naive_find("hello world", "world"))
print(naive_find("hello world", "Python"))
print(naive_find("abc", ""))


# ============================================================================
# 40. KMP STRING SEARCH
# ============================================================================

section("44. KNUTH-MORRIS-PRATT SEARCH")

def build_lps(pattern: str) -> list[int]:
    """
    Build the Longest Prefix Suffix table used by KMP.
    """
    lps = [0] * len(pattern)
    length = 0
    index = 1

    while index < len(pattern):
        if pattern[index] == pattern[length]:
            length += 1
            lps[index] = length
            index += 1
        elif length:
            length = lps[length - 1]
        else:
            lps[index] = 0
            index += 1

    return lps


def kmp_find(text: str, pattern: str) -> int:
    """
    Find pattern using the KMP algorithm.

    Preprocessing: O(m)
    Search: O(n)
    """
    if pattern == "":
        return 0

    lps = build_lps(pattern)

    text_index = 0
    pattern_index = 0

    while text_index < len(text):
        if text[text_index] == pattern[pattern_index]:
            text_index += 1
            pattern_index += 1

            if pattern_index == len(pattern):
                return text_index - pattern_index

        elif pattern_index:
            pattern_index = lps[pattern_index - 1]
        else:
            text_index += 1

    return -1


print(build_lps("ababaca"))
print(kmp_find("ababcabcabababd", "ababd"))
print(kmp_find("hello", "xyz"))


# ============================================================================
# 41. STRING ROTATION
# ============================================================================

section("45. STRING ROTATION")

def is_rotation(first: str, second: str) -> bool:
    """
    Two strings are rotations if they have equal length and second occurs
    inside first + first.
    """
    return len(first) == len(second) and second in (first + first)


print(is_rotation("waterbottle", "erbottlewat"))
print(is_rotation("abc", "acb"))


# ============================================================================
# 42. CUSTOM TOKENIZER
# ============================================================================

section("46. SIMPLE TOKENIZATION")

def tokenize(text: str) -> list[str]:
    """
    Tokenize words and punctuation separately.
    """
    return re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)


print(tokenize("Hello, Python! Version 3."))


# ============================================================================
# 43. MASKING SENSITIVE TEXT
# ============================================================================

section("47. MASKING SENSITIVE STRINGS")

def mask_email(email: str) -> str:
    """
    Mask part of an email address for display.

    This is a presentation utility, not a security mechanism.
    """
    local, separator, domain = email.partition("@")

    if not separator:
        raise ValueError("Invalid email format")

    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]

    return masked_local + "@" + domain


print(mask_email("atul@example.com"))


# ============================================================================
# 44. PASSWORD HANDLING
# ============================================================================

section("48. PASSWORD STRING SECURITY")

password = "ExamplePassword123!"

# Do not print passwords in real applications.
print("Password length:", len(password))

# Password validation should focus on policy requirements without logging
# the actual secret.
def password_meets_basic_policy(password: str) -> bool:
    if len(password) < 12:
        return False

    has_upper = any(character.isupper() for character in password)
    has_lower = any(character.islower() for character in password)
    has_digit = any(character.isdigit() for character in password)
    has_special = any(character in string.punctuation for character in password)

    return has_upper and has_lower and has_digit and has_special


print(password_meets_basic_policy(password))

# Never store plaintext passwords merely because they are strings.
# Password storage should use a dedicated password hashing algorithm and a
# suitable authentication architecture.


# ============================================================================
# 45. CONSTANT-TIME COMPARISON
# ============================================================================

section("49. SECURE STRING COMPARISON")

import hmac

expected_token = "secret-token"
provided_token = "secret-token"

# compare_digest() is designed to reduce timing leakage during comparisons.
print(hmac.compare_digest(expected_token, provided_token))


# ============================================================================
# 46. SQL INJECTION AWARENESS
# ============================================================================

section("50. STRING SECURITY AND SQL")

username = "alice"

unsafe_query = "SELECT * FROM users WHERE username = '" + username + "'"
print("Illustrative query:", unsafe_query)

# Building SQL statements by concatenating untrusted strings can allow SQL
# injection. Real database code should use parameterized queries supplied by
# the database driver rather than interpolating user input into SQL.


# ============================================================================
# 47. HTML ESCAPING
# ============================================================================

section("51. HTML ESCAPING")

from html import escape

untrusted_text = '<script>alert("x")</script>'
safe_html_text = escape(untrusted_text)

print(safe_html_text)

# Escaping is context-dependent. HTML escaping is not automatically correct
# for JavaScript, SQL, shell commands, URLs, or other output contexts.


# ============================================================================
# 48. SHELL COMMAND SECURITY
# ============================================================================

section("52. SHELL COMMAND SECURITY")

filename = "report.txt"

# This is safe as an illustrative string because it is not executed.
command = f"cat {filename}"
print(command)

# Do not pass untrusted strings into shell commands through string
# concatenation. Prefer subprocess APIs with argument lists and shell=False.


# ============================================================================
# 49. STRING TEMPLATES
# ============================================================================

section("53. STRING TEMPLATES")

from string import Template

template = Template("Hello, $name. Your role is $role.")
print(template.substitute(name="Atul", role="student"))

# safe_substitute() leaves missing placeholders rather than raising KeyError.
print(Template("Hello, $name, $unknown").safe_substitute(name="Atul"))


# ============================================================================
# 50. DATACLASS USING STRINGS
# ============================================================================

section("54. STRINGS IN DATA MODELS")

@dataclass(frozen=True)
class User:
    username: str
    email: str
    role: str


user = User(
    username="atul",
    email="atul@example.com",
    role="student",
)

print(user)


# ============================================================================
# 51. VALIDATED STRING VALUE OBJECT
# ============================================================================

section("55. VALIDATED STRING DOMAIN OBJECT")

@dataclass(frozen=True)
class Username:
    value: str

    def __post_init__(self) -> None:
        if not validate_username(self.value):
            raise ValueError("Invalid username")

    def __str__(self) -> str:
        return self.value


valid_username = Username("atul_123")
print(str(valid_username))

try:
    Username("12")
except ValueError as error:
    print("Handled:", error)


# ============================================================================
# 52. STRING INTERPOLATION EDGE CASES
# ============================================================================

section("56. F-STRING EDGE CASES")

value = "Python"

print(f"{value=}")
print(f"{len(value)=}")
print(f"{value!r}")

# Braces can be escaped by doubling them.
print(f"{{value}} = {value}")


# ============================================================================
# 53. FORMAT SPEC MINI-LANGUAGE
# ============================================================================

section("57. FORMAT SPECIFICATION")

number = 1234.56789

formats = [
    f"{number:.2f}",
    f"{number:,.2f}",
    f"{number:10.2f}",
    f"{number:010.2f}",
]

for formatted in formats:
    print(formatted)


# ============================================================================
# 54. PREFIX/SUFFIX EDGE CASES
# ============================================================================

section("58. PREFIX AND SUFFIX EDGE CASES")

value = "filename.txt"

print(value.removeprefix("file"))
print(value.removesuffix(".txt"))
print(value.removeprefix("missing"))

# removeprefix() and removesuffix() require exact string matching.


# ============================================================================
# 55. PARTITION VERSUS SPLIT
# ============================================================================

section("59. PARTITION VERSUS SPLIT")

value = "key=value=another"

print(value.split("="))
print(value.partition("="))

# split() can return many components.
# partition() separates around only the first occurrence.


# ============================================================================
# 56. STRING TRANSLATION ADVANCED
# ============================================================================

section("60. TRANSLATION FOR CHARACTER MAPPING")

source = "abcdef"
mapping = str.maketrans("abc", "123")

print(source.translate(mapping))

# The mapping can also use Unicode ordinals.
mapping = {
    ord("a"): "α",
    ord("b"): "β",
}

print("abc".translate(mapping))


# ============================================================================
# 57. TEXT WRAPPING
# ============================================================================

section("61. TEXT WRAPPING")

import textwrap

long_text = (
    "Python strings are immutable Unicode sequences that support indexing, "
    "slicing, searching, formatting, parsing, and transformation."
)

print(textwrap.fill(long_text, width=50))


# ============================================================================
# 58. STRING DIFFERENCES
# ============================================================================

section("62. DIFFERENCES BETWEEN IMPORTANT OPERATIONS")

comparison_examples = {
    "find": "returns -1 when absent",
    "index": "raises ValueError when absent",
    "split": "returns a list of pieces",
    "partition": "returns exactly three pieces",
    "strip": "removes matching characters from ends",
    "removeprefix": "removes one exact prefix",
    "replace": "replaces occurrences",
    "casefold": "strong Unicode-aware case normalization",
}

for operation, description in comparison_examples.items():
    print(f"{operation:15} {description}")


# ============================================================================
# 59. EDGE CASES
# ============================================================================

section("63. IMPORTANT STRING EDGE CASES")

edge_cases = [
    "",
    " ",
    "\n",
    "0",
    "é",
    "e\u0301",
    "😀",
    "   Python   ",
]

for value in edge_cases:
    print(
        repr(value),
        "length=", len(value),
        "empty=", value == "",
        "truthy=", bool(value),
    )

# Empty strings are false in Boolean contexts.
if not "":
    print("An empty string is falsy.")

if "Python":
    print("A non-empty string is truthy.")


# ============================================================================
# 60. STRING SORTING
# ============================================================================

section("64. SORTING STRINGS")

names = ["bob", "Alice", "charlie", "alice"]

print(sorted(names))
print(sorted(names, key=str.casefold))

# Sorting is lexicographic by default.
# Locale-aware sorting can require locale-specific facilities and domain
# knowledge; Unicode code-point ordering is not the same as human collation.


# ============================================================================
# 61. CUSTOM SORTING
# ============================================================================

section("65. SORTING BY STRING PROPERTY")

words = ["pear", "watermelon", "fig", "banana"]

print(sorted(words, key=len))
print(sorted(words, key=lambda word: (len(word), word)))


# ============================================================================
# 62. STRING STACK / PARSING EXAMPLE
# ============================================================================

section("66. BALANCED BRACKET VALIDATION")

def balanced_brackets(text: str) -> bool:
    """Validate (), [], and {} using a stack."""
    opening = {"(", "[", "{"}
    closing_to_opening = {
        ")": "(",
        "]": "[",
        "}": "{",
    }

    stack: list[str] = []

    for character in text:
        if character in opening:
            stack.append(character)

        elif character in closing_to_opening:
            if not stack or stack.pop() != closing_to_opening[character]:
                return False

    return not stack


for expression in [
    "(a + b)",
    "[a + (b * c)]",
    "(]",
    "([)]",
    "{hello}",
]:
    print(expression, balanced_brackets(expression))


# ============================================================================
# 63. SIMPLE QUOTED STRING PARSER
# ============================================================================

section("67. QUOTED STRING PARSING")

def split_quoted_fields(text: str, separator: str = ",") -> list[str]:
    """
    Split a simple CSV-like line while respecting double-quoted separators.

    This is educational and intentionally does not attempt to implement the
    complete CSV specification.
    """
    fields: list[str] = []
    current: list[str] = []
    inside_quotes = False

    for character in text:
        if character == '"':
            inside_quotes = not inside_quotes
            current.append(character)
        elif character == separator and not inside_quotes:
            fields.append("".join(current).strip())
            current = []
        else:
            current.append(character)

    if inside_quotes:
        raise ValueError("Unclosed quoted field")

    fields.append("".join(current).strip())
    return fields


print(split_quoted_fields('Atul,"Python, SQL",India'))

try:
    print(split_quoted_fields('"unclosed,field'))
except ValueError as error:
    print("Handled:", error)


# ============================================================================
# 64. RECURSION AND STRING PROCESSING
# ============================================================================

section("68. RECURSIVE STRING EXAMPLE")

def reverse_recursive(text: str) -> str:
    """Educational recursive reversal. Not recommended for huge strings."""
    if len(text) <= 1:
        return text

    return reverse_recursive(text[1:]) + text[0]


print(reverse_recursive("Python"))

# Recursive string slicing can create many temporary strings and may hit the
# recursion limit. Iterative or slicing-based reversal is normally preferable.


# ============================================================================
# 65. MEMOIZATION WITH STRING INPUT
# ============================================================================

section("69. MEMOIZATION")

@lru_cache(maxsize=None)
def count_a(text: str) -> int:
    """Count occurrences of 'a'; caching demonstrates hashable string keys."""
    return text.count("a")


print(count_a("banana"))
print(count_a.cache_info())


# ============================================================================
# 66. HASHING AND DICTIONARY KEYS
# ============================================================================

section("70. STRINGS AS HASHABLE OBJECTS")

dictionary = {
    "name": "Atul",
    "language": "Python",
}

print(dictionary["name"])

# Strings are immutable and hashable, making them valid dictionary keys and
# set members.
unique_values = {"python", "sql", "python"}
print(unique_values)


# ============================================================================
# 67. STRING INTERNS
# ============================================================================

section("71. STRING INTERNING")

import sys as _sys

first = _sys.intern("interned-example")
second = _sys.intern("interned-example")

print(first == second)
print(first is second)

# Interning can reduce duplicate storage for selected strings, but should not
# be used indiscriminately. Python implementations may already intern some
# strings automatically.


# ============================================================================
# 68. NEWLINE HANDLING
# ============================================================================

section("72. NEWLINES")

multiline_text = "line one\nline two\nline three"

print(multiline_text.splitlines())

# splitlines() handles several newline conventions more appropriately than
# simply calling split("\n") for general text processing.


# ============================================================================
# 69. ENCODING ERROR HANDLING
# ============================================================================

section("73. ENCODING ERROR STRATEGIES")

text = "café"

encoded = text.encode("ascii", errors="ignore")
print(encoded)

encoded = text.encode("ascii", errors="replace")
print(encoded)

# Error strategies should be selected deliberately. Silently ignoring data
# can corrupt information.


# ============================================================================
# 70. STRING NORMALIZATION PIPELINE FOR SEARCH
# ============================================================================

section("74. SEARCH NORMALIZATION")

def search_key(text: str) -> str:
    """
    Build a basic normalized search key.

    NFKC is useful when compatibility equivalents should compare similarly.
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.casefold()
    text = " ".join(text.split())
    return text


search_values = [
    " Python ",
    "PYTHON",
    "python",
]

for value in search_values:
    print(repr(search_key(value)))


# ============================================================================
# 71. SECURITY: CONTROL CHARACTERS
# ============================================================================

section("75. CONTROL CHARACTER AWARENESS")

dangerous_display = "username\nadmin"
print(repr(dangerous_display))

# Logging untrusted strings without considering control characters can make
# logs confusing or vulnerable to log-forging techniques. Structured logging
# and appropriate escaping are preferable in production systems.


# ============================================================================
# 72. SECURITY: UNICODE CONFUSABLES
# ============================================================================

section("76. UNICODE CONFUSABLES")

latin_a = "a"
cyrillic_a = "а"

print(latin_a == cyrillic_a)
print([unicodedata.name(character) for character in latin_a])
print([unicodedata.name(character) for character in cyrillic_a])

# Visually similar Unicode characters can represent different code points.
# Security-sensitive identifiers may require normalization, allowlists,
# restricted character sets, or specialized confusable detection.


# ============================================================================
# 73. STRING ALGORITHMS: CHARACTER UNIQUE TEST
# ============================================================================

section("77. UNIQUE CHARACTER TEST")

def all_characters_unique(text: str) -> bool:
    return len(set(text)) == len(text)


print(all_characters_unique("abcde"))
print(all_characters_unique("hello"))


# ============================================================================
# 74. STRING ALGORITHMS: VOWEL COUNT
# ============================================================================

section("78. VOWEL COUNT")

def count_vowels(text: str) -> int:
    vowels = set("aeiou")
    return sum(character.casefold() in vowels for character in text)


print(count_vowels("Programming"))


# ============================================================================
# 75. STRING ALGORITHMS: CHARACTER REMOVAL
# ============================================================================

section("79. CHARACTER FILTERING")

def remove_vowels(text: str) -> str:
    vowels = set("aeiouAEIOU")
    return "".join(character for character in text if character not in vowels)


print(remove_vowels("Python Programming"))


# ============================================================================
# 76. STRING ALGORITHMS: WORD LENGTH
# ============================================================================

section("80. LONGEST WORD")

def longest_word(sentence: str) -> str:
    words = sentence.split()

    if not words:
        return ""

    return max(words, key=len)


print(longest_word("Python makes text processing practical"))


# ============================================================================
# 77. STRING ALGORITHMS: FREQUENT WORD
# ============================================================================

section("81. MOST FREQUENT WORD")

def most_frequent_word(text: str) -> tuple[str | None, int]:
    frequency = word_frequency(text)

    if not frequency:
        return None, 0

    word, count = frequency.most_common(1)[0]
    return word, count


print(most_frequent_word("python python sql python sql"))


# ============================================================================
# 78. STRING ALGORITHMS: ROTATE
# ============================================================================

section("82. STRING ROTATION")

def rotate_left(text: str, positions: int) -> str:
    if not text:
        return ""

    positions %= len(text)
    return text[positions:] + text[:positions]


def rotate_right(text: str, positions: int) -> str:
    if not text:
        return ""

    positions %= len(text)
    return text[-positions:] + text[:-positions] if positions else text


print(rotate_left("abcdef", 2))
print(rotate_right("abcdef", 2))
print(rotate_left("abcdef", 100))


# ============================================================================
# 79. STRING ALGORITHMS: COMPRESS SPACES
# ============================================================================

section("83. SPACE NORMALIZATION")

def compress_spaces(text: str) -> str:
    return " ".join(text.split())


print(compress_spaces("Python    is   very\tuseful"))


# ============================================================================
# 80. STRING ALGORITHMS: COUNT SUBSTRING
# ============================================================================

section("84. NON-OVERLAPPING SUBSTRING COUNT")

text = "aaaa"
print(text.count("aa"))

# str.count() counts non-overlapping occurrences.
# Overlapping occurrences require a different algorithm.


def count_overlapping(text: str, pattern: str) -> int:
    if pattern == "":
        return 0

    count = 0

    for index in range(len(text) - len(pattern) + 1):
        if text.startswith(pattern, index):
            count += 1

    return count


print(count_overlapping("aaaa", "aa"))


# ============================================================================
# 81. STRING ALGORITHMS: PREFIX FUNCTION
# ============================================================================

section("85. PREFIX FUNCTION")

pattern = "ababaca"
print(build_lps(pattern))


# ============================================================================
# 82. TESTING
# ============================================================================

section("86. ASSERTION-BASED TESTING")

assert normalize_basic("  PYTHON   programming ") == "python programming"
assert is_palindrome("level")
assert not is_palindrome("python")
assert are_anagrams("listen", "silent")
assert naive_find("hello", "ell") == 1
assert kmp_find("hello", "ell") == 1
assert levenshtein_distance("kitten", "sitting") == 3
assert run_length_decode(run_length_encode("aaabb")) == "aaabb"
assert balanced_brackets("{[()]}")

print("Core assertions passed.")


# ============================================================================
# 83. EXCEPTION TESTING
# ============================================================================

section("87. TESTING ERROR CONDITIONS")

try:
    parse_key_value_record("invalid-field")
except ValueError:
    print("Invalid key-value input correctly rejected.")

try:
    run_length_decode("a")
except ValueError:
    print("Invalid run-length data correctly rejected.")


# ============================================================================
# 84. CUSTOM STRING-LIKE CLASS
# ============================================================================

section("88. STRING-LIKE DOMAIN CLASS")

@dataclass(frozen=True)
class ProductCode:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().upper()

        if not re.fullmatch(r"[A-Z]{3}-\d{4}", normalized):
            raise ValueError("Product code must look like ABC-1234")

        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


code = ProductCode(" abc-1234 ")
print(code)


# ============================================================================
# 85. MULTILINE STRING PROCESSING
# ============================================================================

section("89. MULTILINE PROCESSING")

document = """
Python
SQL

PostgreSQL
Excel
"""

non_empty_lines = [
    line.strip()
    for line in document.splitlines()
    if line.strip()
]

print(non_empty_lines)


# ============================================================================
# 86. STRING PREFIX TREE
# ============================================================================

section("90. TRIE: PREFIX-BASED STRING DATA STRUCTURE")

class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.is_word = False


class Trie:
    """A prefix tree supporting insertion, lookup, and prefix queries."""

    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root

        for character in word:
            node = node.children.setdefault(character, TrieNode())

        node.is_word = True

    def contains(self, word: str) -> bool:
        node = self.root

        for character in word:
            if character not in node.children:
                return False
            node = node.children[character]

        return node.is_word

    def starts_with(self, prefix: str) -> bool:
        node = self.root

        for character in prefix:
            if character not in node.children:
                return False
            node = node.children[character]

        return True


trie = Trie()

for word in ["python", "py", "pandas", "sql"]:
    trie.insert(word)

print(trie.contains("python"))
print(trie.contains("java"))
print(trie.starts_with("pan"))
print(trie.starts_with("py"))


# ============================================================================
# 87. STRING HASHING
# ============================================================================

section("91. STRING HASHING")

text = "Python"
print(hash(text))

# Hash values are useful for hash tables, sets, and dictionaries.
# Python's string hashing is randomized between processes for security.
# Therefore, hash("Python") should not be treated as a persistent identifier
# or stable cross-process checksum.


# ============================================================================
# 88. STABLE DIGESTS
# ============================================================================

section("92. STABLE TEXT DIGEST")

import hashlib

text = "Python"

digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

print(digest)

# A cryptographic digest is deterministic for the same bytes, unlike Python's
# built-in hash() value, which is not intended for persistent fingerprints.


# ============================================================================
# 89. STRING SERIALIZATION
# ============================================================================

section("93. JSON STRING SERIALIZATION")

import json

data = {
    "name": "Atul",
    "language": "Python",
    "skills": ["strings", "SQL"],
}

serialized = json.dumps(data, ensure_ascii=False)
print(serialized)

restored = json.loads(serialized)
print(restored)


# ============================================================================
# 90. CSV STRING PROCESSING
# ============================================================================

section("94. CSV AND WHY SPECIALIZED PARSERS MATTER")

import csv
from io import StringIO

csv_text = 'Atul,"Python, SQL",India\n'

reader = csv.reader(StringIO(csv_text))

for row in reader:
    print(row)

# Simple split(",") is not a complete CSV parser because quoted fields may
# contain commas, quotes, and embedded line breaks.


# ============================================================================
# 91. URL-STYLE ENCODING
# ============================================================================

section("95. URL QUERY ENCODING")

from urllib.parse import quote, urlencode

value = "Python strings & Unicode"

print(quote(value))
print(urlencode({"q": value, "page": 1}))

# URL encoding is context-specific. Do not substitute HTML escaping or SQL
# escaping for URL encoding.


# ============================================================================
# 92. STRING CLEANING WITH TRANSLATION
# ============================================================================

section("96. FAST CHARACTER FILTERING")

punctuation_table = str.maketrans("", "", string.punctuation)

text = "Hello, Python! Strings are useful."
print(text.translate(punctuation_table))


# ============================================================================
# 93. PERFORMANCE CONSIDERATIONS
# ============================================================================

section("97. PERFORMANCE PRINCIPLES")

# General principles:
# - String indexing is O(1) in typical Python implementations.
# - Slicing creates a new string and is proportional to slice size.
# - Searching can vary depending on operation and implementation.
# - join() is preferred for assembling many pieces.
# - Regular expressions can be expensive for complex patterns.
# - Reusing a compiled regular expression can be beneficial for repeated use.
# - Unicode normalization adds processing cost and should be applied according
#   to the application's actual text semantics.

large_parts = [str(number) for number in range(10_000)]

joined = ",".join(large_parts)
print("Joined characters:", len(joined))


# ============================================================================
# 94. REGEX PERFORMANCE AND REUSE
# ============================================================================

section("98. COMPILED REGEX REUSE")

number_pattern = re.compile(r"\d+")

text = "A12 B345 C6789"

for match in number_pattern.finditer(text):
    print(match.group(), match.span())


# ============================================================================
# 95. REGEX SECURITY
# ============================================================================

section("99. REGULAR EXPRESSION SECURITY")

# Complex patterns can suffer from catastrophic backtracking in some regex
# engines and pattern structures. Avoid ambiguous nested quantifiers when
# processing attacker-controlled input.

safe_pattern = re.compile(r"^[A-Za-z0-9_]{1,20}$")

print(bool(safe_pattern.fullmatch("safe_username_123")))


# ============================================================================
# 96. LOGGING-SAFE REPRESENTATION
# ============================================================================

section("100. DEBUGGING STRING VALUES")

user_input = "hello\nworld\t!"

print("Raw value:", user_input)
print("Debug representation:", repr(user_input))

# repr() makes invisible characters visible, which is useful when diagnosing
# whitespace, newline, escape, and encoding-related problems.


# ============================================================================
# 97. COMMON MISTAKES
# ============================================================================

section("101. COMMON STRING MISTAKES")

mistakes = [
    "Using is instead of == for value comparison",
    "Assuming strings are mutable",
    "Using split(',') as a complete CSV parser",
    "Building large strings through inefficient repeated operations",
    "Ignoring Unicode normalization when semantic equivalence matters",
    "Treating bytes and str as interchangeable",
    "Using lower() for every Unicode case-insensitive comparison",
    "Concatenating untrusted input into SQL or shell commands",
    "Printing secrets such as passwords or authentication tokens",
    "Assuming len() measures visual grapheme clusters",
]

for mistake in mistakes:
    print("-", mistake)


# ============================================================================
# 98. GRAPHEME CLUSTER CAVEAT
# ============================================================================

section("102. VISUAL CHARACTERS VERSUS CODE POINTS")

family_emoji = "👨‍👩‍👧‍👦"

print("String:", family_emoji)
print("Python length:", len(family_emoji))
print("Code points:", [hex(ord(character)) for character in family_emoji])

# len(str) counts Unicode code points, not necessarily user-perceived
# characters, grapheme clusters, or rendered glyphs.


# ============================================================================
# 99. NORMALIZATION AND DIACRITIC REMOVAL
# ============================================================================

section("103. DIACRITIC HANDLING")

def remove_diacritics(text: str) -> str:
    """
    Remove combining marks after NFD decomposition.

    This is useful for selected search scenarios, but it changes information
    and is not universally appropriate for linguistic comparison.
    """
    decomposed = unicodedata.normalize("NFD", text)

    return "".join(
        character
        for character in decomposed
        if unicodedata.category(character) != "Mn"
    )


print(remove_diacritics("café résumé naïve"))


# ============================================================================
# 100. STRING API DISCOVERY
# ============================================================================

section("104. STRING METHODS")

public_string_methods = [
    method
    for method in dir(str)
    if not method.startswith("_")
]

print(", ".join(public_string_methods))


# ============================================================================
# 101. TYPE ANNOTATIONS
# ============================================================================

section("105. TYPE ANNOTATIONS WITH STRINGS")

def greeting(name: str) -> str:
    return f"Hello, {name}!"


print(greeting("Atul"))


# ============================================================================
# 102. GENERATOR FOR STRING CHUNKS
# ============================================================================

section("106. PROCESSING LARGE TEXT IN CHUNKS")

def chunks(text: str, size: int) -> Iterable[str]:
    """Yield fixed-size string chunks."""
    if size <= 0:
        raise ValueError("Chunk size must be positive")

    for start in range(0, len(text), size):
        yield text[start:start + size]


for chunk in chunks("abcdefghijklmnopqrstuvwxyz", 5):
    print(chunk)


# ============================================================================
# 103. STREAMING-LIKE LINE PROCESSING
# ============================================================================

section("107. LINE-ORIENTED TEXT PROCESSING")

def non_empty_lines(lines: Iterable[str]) -> Iterable[str]:
    """Yield stripped non-empty lines without creating an unnecessary list."""
    for line in lines:
        stripped = line.strip()

        if stripped:
            yield stripped


source_lines = [
    "  Python  ",
    "",
    " SQL ",
    "   ",
    " PostgreSQL ",
]

print(list(non_empty_lines(source_lines)))


# ============================================================================
# 104. TEXT COMPARISON
# ============================================================================

section("108. EXACT VERSUS NORMALIZED COMPARISON")

left = " Python "
right = "python"

print("Exact:", left == right)
print("Normalized:", normalize_basic(left) == normalize_basic(right))

# The correct comparison strategy depends on the domain. Normalizing too
# aggressively can incorrectly treat distinct values as equivalent.


# ============================================================================
# 105. DOMAIN-SPECIFIC IDENTIFIERS
# ============================================================================

section("109. CASE SENSITIVITY")

case_sensitive_ids = {"ABC", "abc"}
print(case_sensitive_ids)

case_insensitive_ids = {value.casefold() for value in ["ABC", "abc"]}
print(case_insensitive_ids)

# Whether identifiers are case-sensitive is a domain rule, not a universal
# property of strings.


# ============================================================================
# 106. STRING FORMATTING WITH CUSTOM OBJECTS
# ============================================================================

section("110. CUSTOM STRING REPRESENTATION")

@dataclass
class Employee:
    name: str
    department: str

    def __str__(self) -> str:
        return f"{self.name} ({self.department})"

    def __repr__(self) -> str:
        return (
            f"Employee(name={self.name!r}, "
            f"department={self.department!r})"
        )


employee = Employee("Atul", "Technology")

print(str(employee))
print(repr(employee))


# ============================================================================
# 107. EDGE CASE: NONE IS NOT A STRING
# ============================================================================

section("111. NONE VERSUS EMPTY STRING")

value: str | None = None

print(value is None)
print("" == value)

# Calling string methods on None raises AttributeError.
try:
    print(value.strip())  # type: ignore[union-attr]
except AttributeError as error:
    print("Handled:", error)


# ============================================================================
# 108. SAFE STRING CONVERSION
# ============================================================================

section("112. STR() VERSUS REPR()")

values = [None, 123, 45.6, True, "hello\nworld"]

for value in values:
    print("str :", str(value))
    print("repr:", repr(value))


# ============================================================================
# 109. STRING REPRESENTATION OF COLLECTIONS
# ============================================================================

section("113. COLLECTIONS CONTAINING STRINGS")

items = ["Python", "SQL", "FastAPI"]

print(items)
print(tuple(items))
print({item: len(item) for item in items})


# ============================================================================
# 110. SIMPLE TEXT REPORT
# ============================================================================

section("114. BUILDING A TEXT REPORT")

report_rows = [
    ("Name", "Atul"),
    ("Language", "Python"),
    ("Topic", "Strings"),
]

report = "\n".join(
    f"{key:<12}: {value}"
    for key, value in report_rows
)

print(report)


# ============================================================================
# 111. STRING-BASED CONFIGURATION PARSING
# ============================================================================

section("115. CONFIGURATION PARSING")

configuration = """
host=localhost
port=5432
database=training
"""

config: dict[str, str] = {}

for line in configuration.splitlines():
    line = line.strip()

    if not line or line.startswith("#"):
        continue

    key, separator, value = line.partition("=")

    if not separator:
        raise ValueError(f"Invalid configuration line: {line!r}")

    config[key.strip()] = value.strip()

print(config)


# ============================================================================
# 112. PRODUCTION CONSIDERATIONS
# ============================================================================

section("116. PRODUCTION-ORIENTED STRING PRACTICES")

production_principles = [
    "Define text normalization rules explicitly.",
    "Keep text and binary data conceptually separate.",
    "Use explicit encodings at system boundaries.",
    "Prefer UTF-8 for interoperable text when appropriate.",
    "Validate external input according to business rules.",
    "Escape output according to its destination context.",
    "Use parameterized database queries.",
    "Avoid shell command construction from untrusted strings.",
    "Do not log secrets.",
    "Use structured logging when handling untrusted input.",
    "Benchmark real workloads before making performance assumptions.",
    "Use specialized parsers for standardized formats.",
    "Consider Unicode normalization when equality has semantic implications.",
    "Do not assume len() equals the number of visible characters.",
]

for principle in production_principles:
    print("-", principle)


# ============================================================================
# 113. FINAL INTEGRATED EXAMPLE
# ============================================================================

section("117. INTEGRATED TEXT PROCESSING EXAMPLE")

@dataclass(frozen=True)
class TextStatistics:
    characters: int
    words: int
    lines: int
    unique_words: int
    most_common_word: str | None


def analyze_text(text: str) -> TextStatistics:
    normalized = unicodedata.normalize("NFC", text)

    words = re.findall(r"\b[\w']+\b", normalized.casefold())
    counts = Counter(words)

    most_common = counts.most_common(1)

    return TextStatistics(
        characters=len(normalized),
        words=len(words),
        lines=len(normalized.splitlines()),
        unique_words=len(counts),
        most_common_word=most_common[0][0] if most_common else None,
    )


document = """
Python strings are Unicode text.
Strings are immutable.
String methods support searching, formatting, and transformation.
Python strings are useful for parsing and data processing.
"""

statistics = analyze_text(document)

print(statistics)


# ============================================================================
# 114. FINAL VALIDATION
# ============================================================================

section("118. FINAL VALIDATION")

assert isinstance("Python", str)
assert "Python"[0] == "P"
assert "Python"[-1] == "n"
assert "Python"[::-1] == "nohtyP"
assert "PYTHON".lower() == "python"
assert "python".upper() == "PYTHON"
assert "  python  ".strip() == "python"
assert "a,b,c".split(",") == ["a", "b", "c"]
assert "-".join(["a", "b", "c"]) == "a-b-c"
assert "Python".startswith("Py")
assert "Python".endswith("on")
assert "th" in "Python"
assert "Java" not in "Python"
assert are_anagrams("listen", "silent")
assert is_phrase_palindrome("A man, a plan, a canal: Panama")
assert levenshtein_distance("abc", "abc") == 0
assert kmp_find("abcdef", "cde") == 2
assert rotate_left("abcdef", 2) == "cdefab"
assert rotate_right("abcdef", 2) == "efabcd"
assert balanced_brackets("({[]})")
assert not balanced_brackets("({[})")
assert run_length_decode(run_length_encode("aaabbbcccc")) == "aaabbbcccc"
assert search_key("  PYTHON  ") == "python"

print("All final validations passed.")
print("\nString study script completed successfully.")
