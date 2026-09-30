"""
Strings in Detail
A self-contained progression from fundamental string operations to
Unicode handling, parsing, searching, normalization, text analysis,
stream processing, and practical string-processing design.

Run:
    python strings_in_detail.py
"""

from __future__ import annotations

import csv
import io
import json
import re
import string
import sys
import textwrap
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def heading(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def fundamental_strings() -> None:
    heading("Fundamental String Operations")

    text = "Python makes text processing practical."
    print("Original:", text)
    print("Length:", len(text))
    print("First character:", text[0])
    print("Last character:", text[-1])
    print("Slice:", text[0:6])
    print("Every second character:", text[::2])
    print("Reversed:", text[::-1])

    # Strings are immutable. Operations create new string objects rather
    # than changing the existing string in place.
    upper_text = text.upper()
    replaced_text = text.replace("Python", "Modern Python")

    print("Uppercase:", upper_text)
    print("Replacement:", replaced_text)
    print("Original remains:", text)

    pieces = ["Python", "strings", "are", "immutable"]
    joined = " ".join(pieces)
    print("Joined:", joined)

    messy = "   production logs contain useful text   \n"
    print("Stripped:", repr(messy.strip()))

    sentence = "alpha,beta,gamma,delta"
    print("Split:", sentence.split(","))

    print("Contains 'text':", "text" in text)
    print("Starts with 'Python':", text.startswith("Python"))
    print("Ends with '.':", text.endswith("."))


def string_comparison_and_formatting() -> None:
    heading("Comparison, Formatting, and Escaping")

    left = "database"
    right = "database"
    print("Equality:", left == right)
    print("Case-sensitive equality:", "Admin" == "admin")
    print("Case-insensitive equality:", "Admin".casefold() == "admin".casefold())

    username = "atul"
    repository = "text-processing"
    issue_count = 7

    # f-strings make the relationship between values and generated text
    # explicit and are usually preferable to manual concatenation.
    message = f"{username} has {issue_count} issues in {repository}."
    print(message)

    price = 1499.5
    print(f"Price: ₹{price:,.2f}")

    multiline = """A string can span
multiple physical lines."""
    print(multiline)

    escaped = "A quote: \"strings\" and a path: C:\\data\\text"
    raw_path = r"C:\data\text"
    print(escaped)
    print(raw_path)


def validation_and_cleaning() -> None:
    heading("Validation and Cleaning")

    candidates = [
        "admin_user",
        "Admin User",
        "user@example.com",
        "",
        "a" * 80,
    ]

    username_pattern = re.compile(r"^[a-z][a-z0-9_]{2,31}$")

    for candidate in candidates:
        normalized = candidate.strip()
        valid = bool(username_pattern.fullmatch(normalized))
        print(f"{candidate!r:22} -> valid username: {valid}")

    # Validation should happen before downstream processing. Empty strings,
    # whitespace-only values, and unexpectedly large input can require
    # different handling in production systems.
    def validate_title(value: str, maximum: int = 120) -> str:
        if not isinstance(value, str):
            raise TypeError("title must be a string")

        cleaned = " ".join(value.split())

        if not cleaned:
            raise ValueError("title cannot be empty")

        if len(cleaned) > maximum:
            raise ValueError("title exceeds maximum length")

        return cleaned

    examples = ["  Quarterly   Revenue Report  ", "   ", "A useful title"]
    for value in examples:
        try:
            print(repr(value), "->", validate_title(value))
        except (TypeError, ValueError) as exc:
            print(repr(value), "-> rejected:", exc)


def searching_and_counting() -> None:
    heading("Searching, Counting, and Frequency Analysis")

    document = (
        "Strings support searching. Searching can use exact matches, "
        "prefixes, suffixes, regular expressions, or algorithms such as KMP."
    )

    print("Occurrences of 'search':", document.lower().count("search"))
    print("Position of 'KMP':", document.find("KMP"))
    print("Case-insensitive membership:", "strings" in document.lower())

    words = re.findall(r"[A-Za-z]+", document.lower())
    frequencies = Counter(words)

    print("Word frequencies:")
    for word, count in frequencies.most_common():
        print(f"  {word}: {count}")

    # Translate removes punctuation efficiently when the same punctuation
    # set needs to be stripped repeatedly.
    translator = str.maketrans("", "", string.punctuation)
    clean = document.translate(translator)
    print("Punctuation removed:", clean)


def regular_expression_processing() -> None:
    heading("Regular Expressions")

    log_text = """
    2026-09-30 INFO user=atul action=login
    2026-09-30 WARN user=admin action=failed-login
    2026-09-30 ERROR user=service action=timeout
    """

    record_pattern = re.compile(
        r"(?P<date>\d{4}-\d{2}-\d{2})\s+"
        r"(?P<level>[A-Z]+)\s+"
        r"user=(?P<user>[A-Za-z0-9_]+)\s+"
        r"action=(?P<action>[A-Za-z-]+)"
    )

    for match in record_pattern.finditer(log_text):
        print(match.groupdict())

    # Compiled patterns are reusable and make complex parsing easier to
    # inspect, test, and maintain.
    email_pattern = re.compile(
        r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
        r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
    )

    for email in ["person@example.com", "invalid@", "a@b"]:
        print(email, "->", bool(email_pattern.fullmatch(email)))


def unicode_and_normalization() -> None:
    heading("Unicode, Code Points, and Normalization")

    samples = ["café", "cafe\u0301", "東京", "नमस्ते", "😀"]

    for value in samples:
        print(
            repr(value),
            "characters:",
            len(value),
            "code points:",
            [f"U+{ord(char):04X}" for char in value],
        )

    composed = "café"
    decomposed = "cafe\u0301"

    print("Raw equality:", composed == decomposed)
    print(
        "NFC equality:",
        unicodedata.normalize("NFC", composed)
        == unicodedata.normalize("NFC", decomposed),
    )

    # Casefold is designed for caseless text comparison and handles more
    # Unicode cases than simple lowercasing.
    print("Casefold comparison:", "Straße".casefold() == "STRASSE".casefold())

    for char in "A9😀":
        print(
            char,
            "category=", unicodedata.category(char),
            "name=", unicodedata.name(char, "UNKNOWN"),
        )


def grapheme_like_analysis() -> None:
    heading("Characters, Code Points, and User-Visible Text")

    samples = [
        "hello",
        "café",
        "e\u0301",
        "👨‍💻",
        "🇮🇳",
    ]

    for value in samples:
        print(
            repr(value),
            "Python length=",
            len(value),
            "display-oriented note=",
            "may contain multiple code points",
        )

    print(
        "Python's len() counts Unicode code points, not necessarily "
        "user-perceived grapheme clusters."
    )


def tokenize_text() -> None:
    heading("Tokenization")

    text = "Release v2.10.4: API latency fell by 18.5% after caching."

    # This tokenizer preserves decimal numbers and words while treating
    # punctuation as separate tokens where useful for analysis.
    tokens = re.findall(
        r"\d+(?:\.\d+)*%?|[A-Za-z]+(?:[-'][A-Za-z]+)*|[^\w\s]",
        text,
    )

    for index, token in enumerate(tokens):
        print(index, repr(token))

    words = re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", text.lower())
    print("Word tokens:", words)


def palindrome_and_two_pointer() -> None:
    heading("Two-Pointer String Algorithm")

    def is_palindrome(value: str) -> bool:
        # Comparing inward from both ends avoids constructing a reversed
        # copy and uses O(n) time with O(1) auxiliary space.
        left, right = 0, len(value) - 1

        while left < right:
            if value[left] != value[right]:
                return False
            left += 1
            right -= 1

        return True

    for value in ["level", "radar", "python", "1221", ""]:
        print(repr(value), "->", is_palindrome(value))


def anagram_analysis() -> None:
    heading("Anagrams and Character Multisets")

    def are_anagrams(first: str, second: str) -> bool:
        normalized_first = "".join(first.casefold().split())
        normalized_second = "".join(second.casefold().split())
        return Counter(normalized_first) == Counter(normalized_second)

    pairs = [
        ("listen", "silent"),
        ("Debit Card", "Bad Credit"),
        ("python", "typhonx"),
    ]

    for first, second in pairs:
        print(first, "|", second, "->", are_anagrams(first, second))


def manual_substring_search() -> None:
    heading("Naive Substring Search")

    def find_substring(text: str, pattern: str) -> int:
        if pattern == "":
            return 0

        if len(pattern) > len(text):
            return -1

        for start in range(len(text) - len(pattern) + 1):
            for offset in range(len(pattern)):
                if text[start + offset] != pattern[offset]:
                    break
            else:
                return start

        return -1

    examples = [
        ("production deployment", "deploy"),
        ("aaaaab", "aaab"),
        ("database", "table"),
    ]

    for text, pattern in examples:
        print(repr(text), repr(pattern), "->", find_substring(text, pattern))


def kmp_search() -> None:
    heading("Knuth-Morris-Pratt String Search")

    def prefix_table(pattern: str) -> list[int]:
        table = [0] * len(pattern)
        matched = 0

        for index in range(1, len(pattern)):
            while matched > 0 and pattern[index] != pattern[matched]:
                matched = table[matched - 1]

            if pattern[index] == pattern[matched]:
                matched += 1

            table[index] = matched

        return table

    def kmp_find(text: str, pattern: str) -> int:
        if pattern == "":
            return 0

        table = prefix_table(pattern)
        text_index = 0
        pattern_index = 0

        while text_index < len(text):
            if text[text_index] == pattern[pattern_index]:
                text_index += 1
                pattern_index += 1

                if pattern_index == len(pattern):
                    return text_index - pattern_index
            elif pattern_index:
                pattern_index = table[pattern_index - 1]
            else:
                text_index += 1

        return -1

    text = "ababcabcabababd"
    pattern = "ababd"

    print("Text:", text)
    print("Pattern:", pattern)
    print("Prefix table:", prefix_table(pattern))
    print("Match index:", kmp_find(text, pattern))


def edit_distance() -> None:
    heading("Levenshtein Edit Distance")

    def levenshtein(first: str, second: str) -> int:
        # Keep only the previous and current rows. This reduces auxiliary
        # space from O(n*m) to O(min(n, m)).
        if len(first) < len(second):
            first, second = second, first

        previous = list(range(len(second) + 1))

        for i, char_first in enumerate(first, start=1):
            current = [i]

            for j, char_second in enumerate(second, start=1):
                insertion = current[j - 1] + 1
                deletion = previous[j] + 1
                substitution = previous[j - 1] + (char_first != char_second)

                current.append(min(insertion, deletion, substitution))

            previous = current

        return previous[-1]

    pairs = [
        ("kitten", "sitting"),
        ("database", "databse"),
        ("apple", "apple"),
    ]

    for first, second in pairs:
        print(first, "->", second, "distance:", levenshtein(first, second))


def rolling_hash_search() -> None:
    heading("Rolling Hash Search")

    def rolling_hash_find(text: str, pattern: str) -> int:
        if pattern == "":
            return 0
        if len(pattern) > len(text):
            return -1

        base = 257
        modulus = 1_000_000_007
        pattern_length = len(pattern)

        high_power = pow(base, pattern_length - 1, modulus)

        pattern_hash = 0
        window_hash = 0

        for index in range(pattern_length):
            pattern_hash = (
                pattern_hash * base + ord(pattern[index])
            ) % modulus
            window_hash = (
                window_hash * base + ord(text[index])
            ) % modulus

        for start in range(len(text) - pattern_length + 1):
            if window_hash == pattern_hash:
                # Hash collisions are possible, so equality must be verified.
                if text[start : start + pattern_length] == pattern:
                    return start

            if start < len(text) - pattern_length:
                outgoing = ord(text[start]) * high_power
                window_hash = (
                    (window_hash - outgoing) * base
                    + ord(text[start + pattern_length])
                ) % modulus

        return -1

    print(
        rolling_hash_find(
            "distributed systems require careful text processing",
            "careful",
        )
    )


@dataclass
class DocumentStats:
    characters: int
    words: int
    lines: int
    unique_words: int
    average_word_length: float


def analyze_document(text: str) -> DocumentStats:
    words = re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE)
    lengths = [len(word) for word in words]

    return DocumentStats(
        characters=len(text),
        words=len(words),
        lines=text.count("\n") + (1 if text else 0),
        unique_words=len({word.casefold() for word in words}),
        average_word_length=(
            sum(lengths) / len(lengths) if lengths else 0.0
        ),
    )


def document_analysis() -> None:
    heading("Document Analysis")

    document = textwrap.dedent(
        """
        Reliable text processing begins with clearly defined input rules.
        Production systems must account for Unicode, malformed input,
        normalization, repeated processing, and measurable performance.
        """
    ).strip()

    stats = analyze_document(document)
    print(stats)

    words = re.findall(r"\b[\w'-]+\b", document.casefold())
    frequencies = Counter(words)

    print("Most common words:")
    for word, count in frequencies.most_common(5):
        print(f"  {word}: {count}")


def structured_text_parsing() -> None:
    heading("Structured Text Parsing")

    csv_text = """service,environment,status
api,production,healthy
worker,production,degraded
web,staging,healthy
"""

    reader = csv.DictReader(io.StringIO(csv_text))
    records = list(reader)

    for record in records:
        print(record)

    healthy_production = [
        record
        for record in records
        if record["environment"] == "production"
        and record["status"] == "healthy"
    ]

    print("Healthy production services:", healthy_production)


def safe_text_file_processing() -> None:
    heading("Text File Processing")

    sample_path = Path("strings_detail_sample.txt")
    sample_content = (
        "alpha beta gamma\n"
        "beta gamma gamma\n"
        "delta alpha\n"
    )

    try:
        # UTF-8 is explicitly selected instead of relying on the platform's
        # default encoding, which can differ between machines.
        sample_path.write_text(sample_content, encoding="utf-8")

        content = sample_path.read_text(encoding="utf-8")
        words = re.findall(r"\b[A-Za-z]+\b", content.lower())

        print("Words:", words)
        print("Frequency:", Counter(words))
    finally:
        # Temporary files should not silently accumulate in a project.
        if sample_path.exists():
            sample_path.unlink()


def streaming_line_processing() -> None:
    heading("Streaming Text Processing")

    data = io.StringIO(
        "INFO request=100 latency=24ms\n"
        "ERROR request=101 latency=timeout\n"
        "INFO request=102 latency=31ms\n"
    )

    error_count = 0
    request_ids: list[int] = []

    # Streaming line processing avoids loading an arbitrarily large log
    # into memory when the source is a real file or network stream.
    for line in data:
        if line.startswith("ERROR"):
            error_count += 1

        match = re.search(r"request=(\d+)", line)
        if match:
            request_ids.append(int(match.group(1)))

    print("Errors:", error_count)
    print("Request IDs:", request_ids)


def string_interning_and_memory() -> None:
    heading("Memory and Performance Considerations")

    values = ["status_ok"] * 1000
    unique_values = set(values)

    print("Number of list elements:", len(values))
    print("Number of unique values:", len(unique_values))

    print(
        "Repeated concatenation can repeatedly allocate strings. "
        "For many fragments, collecting them and using ''.join(...) "
        "is usually more efficient."
    )

    fragments = [f"record-{index}" for index in range(1000)]
    combined = "|".join(fragments)
    print("Combined length:", len(combined))


def cached_recursive_processing() -> None:
    heading("Memoization with String Problems")

    @lru_cache(maxsize=None)
    def count_decodings(value: str) -> int:
        # This is a small dynamic-programming example in which substrings
        # become states. Invalid numeric encodings return zero.
        if not value:
            return 1

        if value[0] == "0":
            return 0

        total = count_decodings(value[1:])

        if len(value) >= 2 and 10 <= int(value[:2]) <= 26:
            total += count_decodings(value[2:])

        return total

    for value in ["12", "226", "06", "11106"]:
        count_decodings.cache_clear()
        print(value, "->", count_decodings(value))


def secure_text_handling() -> None:
    heading("Security-Relevant String Handling")

    user_supplied_filename = "../../etc/passwd"

    # Validation should reject path traversal when a string is intended to
    # represent a simple filename rather than an arbitrary filesystem path.
    filename_pattern = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")

    print(
        "Filename accepted:",
        bool(filename_pattern.fullmatch(user_supplied_filename)),
    )

    query = "admin' OR '1'='1"
    print("Raw user input:", query)
    print(
        "SQL guidance: never construct SQL by interpolating this string; "
        "use parameterized database APIs."
    )

    html_fragment = "<script>alert('x')</script>"
    print("Potential HTML input:", html_fragment)
    print(
        "Web guidance: HTML output requires context-appropriate escaping "
        "or a safe templating mechanism."
    )


def text_redaction() -> None:
    heading("Practical Text Redaction")

    message = (
        "Contact alice@example.com or bob@example.org. "
        "Reference ticket SEC-48291."
    )

    email_pattern = re.compile(
        r"\b[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
        r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+\b"
    )
    ticket_pattern = re.compile(r"\b[A-Z]{2,8}-\d{3,8}\b")

    redacted = email_pattern.sub("[EMAIL]", message)
    redacted = ticket_pattern.sub("[TICKET]", redacted)

    print(redacted)


def comparison_table() -> None:
    heading("Algorithmic Characteristics")

    rows = [
        ("Direct equality", "Compare full strings", "O(n)", "O(1) typical"),
        ("Naive search", "Find substring", "O(n*m)", "O(1)"),
        ("KMP", "Find substring", "O(n+m)", "O(m)"),
        ("Levenshtein", "Edit distance", "O(n*m)", "O(min(n,m)) here"),
        ("Counter", "Frequency analysis", "O(n)", "O(k)"),
    ]

    for name, purpose, time, space in rows:
        print(f"{name:20} {purpose:25} {time:10} {space}")


def run_all_demos() -> None:
    fundamental_strings()
    string_comparison_and_formatting()
    validation_and_cleaning()
    searching_and_counting()
    regular_expression_processing()
    unicode_and_normalization()
    grapheme_like_analysis()
    tokenize_text()
    palindrome_and_two_pointer()
    anagram_analysis()
    manual_substring_search()
    kmp_search()
    edit_distance()
    rolling_hash_search()
    document_analysis()
    structured_text_parsing()
    safe_text_file_processing()
    streaming_line_processing()
    string_interning_and_memory()
    cached_recursive_processing()
    secure_text_handling()
    text_redaction()
    comparison_table()


if __name__ == "__main__":
    try:
        run_all_demos()
    except BrokenPipeError:
        # This makes command-line piping behave cleanly when a downstream
        # process closes its input before all output is produced.
        sys.exit(0)
