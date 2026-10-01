"""
String Methods: comprehensive executable learning laboratory.

This program demonstrates Python string methods from fundamental operations
through validation, parsing, normalization, transformation, structured text
processing, and a realistic log-processing workflow.

All demonstrations use the Python standard library.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
import tempfile
import textwrap


def heading(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def show(label: str, value: object) -> None:
    print(f"{label:<38} {value!r}")


# ---------------------------------------------------------------------------
# Fundamentals: methods that inspect or transform individual strings.
# ---------------------------------------------------------------------------

def demonstrate_fundamentals() -> None:
    heading("Fundamental String Methods")

    text = "  Python String Methods  "

    show("Original", text)
    show("strip()", text.strip())
    show("lstrip()", text.lstrip())
    show("rstrip()", text.rstrip())
    show("lower()", text.lower())
    show("upper()", text.upper())
    show("casefold()", "Straße".casefold())
    show("title()", "python string methods".title())
    show("capitalize()", "python string methods".capitalize())
    show("swapcase()", "PyThOn".swapcase())

    # String methods return new strings. They do not mutate the original
    # string because Python strings are immutable.
    normalized = text.strip()
    show("Original after strip()", text)
    show("Returned string", normalized)

    sample = "Python makes text processing practical"

    show("len()", len(sample))
    show("count('t')", sample.count("t"))
    show("find('text')", sample.find("text"))
    show("find('missing')", sample.find("missing"))
    show("rfind('t')", sample.rfind("t"))
    show("index('text')", sample.index("text"))
    show("startswith('Python')", sample.startswith("Python"))
    show("endswith('practical')", sample.endswith("practical"))

    # index() raises ValueError when the substring is absent, whereas find()
    # returns -1. This distinction matters when failure must be handled.
    try:
        sample.index("database")
    except ValueError as exc:
        show("index() missing substring", type(exc).__name__)


# ---------------------------------------------------------------------------
# Splitting, joining, replacement, and partitioning.
# ---------------------------------------------------------------------------

def demonstrate_structure_methods() -> None:
    heading("Splitting, Joining, Replacement, and Partitioning")

    csv_line = "ATUL,Python,Advanced,120"
    fields = csv_line.split(",")
    show("split(',')", fields)
    show("split(',', 2)", csv_line.split(",", 2))

    sentence = "Python   JavaScript    C++"
    # split() without an explicit separator treats runs of whitespace as one
    # separator and avoids empty fields.
    show("split() whitespace", sentence.split())

    words = ["String", "methods", "support", "text", "processing"]
    show("' '.join(words)", " ".join(words))
    show("','.join(words)", ",".join(words))

    url = "https://example.com/products?id=42"
    show("partition('://')", url.partition("://"))
    show("rpartition('/')", url.rpartition("/"))

    message = "ERROR: connection failed; ERROR: retrying"
    show("replace()", message.replace("ERROR", "WARNING"))
    show("replace(..., 1)", message.replace("ERROR", "WARNING", 1))

    # removeprefix() and removesuffix() are safer than broad replace() when
    # only a known boundary marker should be removed.
    filename = "report.final.csv"
    show("removeprefix()", "report_" + filename.removeprefix("report."))
    show("removesuffix()", filename.removesuffix(".csv"))

    path = "archive/2026/reports"
    show("split('/')", path.split("/"))
    show("rsplit('/', 1)", path.rsplit("/", 1))


# ---------------------------------------------------------------------------
# Character classification and validation.
# ---------------------------------------------------------------------------

def validate_identifier(value: str) -> tuple[bool, str]:
    """Validate a simple application identifier using string methods."""

    if not value:
        return False, "identifier cannot be empty"

    if not value.isidentifier():
        return False, "identifier is not a valid Python-style identifier"

    if value in {"class", "def", "return", "import"}:
        return False, "identifier conflicts with a reserved keyword"

    return True, "valid identifier"


def demonstrate_validation() -> None:
    heading("Character Classification and Validation")

    samples = [
        "",
        "12345",
        "ABC123",
        "hello_world",
        "hello-world",
        "  ",
        "42.50",
        "Ⅻ",
        "abc@example.com",
    ]

    for value in samples:
        print(f"\nValue: {value!r}")
        show("isalpha()", value.isalpha())
        show("isdigit()", value.isdigit())
        show("isdecimal()", value.isdecimal())
        show("isnumeric()", value.isnumeric())
        show("isalnum()", value.isalnum())
        show("isspace()", value.isspace())
        show("islower()", value.islower())
        show("isupper()", value.isupper())
        show("istitle()", value.istitle())
        show("isprintable()", value.isprintable())
        show("isidentifier()", value.isidentifier())

    for identifier in ["customer_id", "2026_report", "order-id", "class"]:
        valid, reason = validate_identifier(identifier)
        print(f"{identifier!r}: {valid} ({reason})")


# ---------------------------------------------------------------------------
# Formatting methods.
# ---------------------------------------------------------------------------

def demonstrate_formatting() -> None:
    heading("Formatting Methods")

    product = "Quantum Laptop"
    quantity = 3
    price = 74999.50

    # format() and f-strings are useful for constructing human-readable
    # output, while alignment methods control fixed-width text.
    invoice = "Product: {} | Quantity: {} | Unit Price: ₹{:,.2f}".format(
        product, quantity, price
    )
    show("format()", invoice)

    show("center()", product.center(30, "-"))
    show("ljust()", product.ljust(30, "."))
    show("rjust()", product.rjust(30, "."))
    show("zfill()", "4287".zfill(8))

    # format_map() can resolve named fields from a dictionary.
    template = "{name} submitted {count} files"
    values = {"name": "Atul", "count": 18}
    show("format_map()", template.format_map(values))


# ---------------------------------------------------------------------------
# Translation and character-level transformations.
# ---------------------------------------------------------------------------

def demonstrate_translation() -> None:
    heading("Character Translation")

    text = "Use 2026-10-01 for the deployment window."
    translation_table = str.maketrans({"-": "/", ".": "!"})
    show("translate()", text.translate(translation_table))

    # maketrans() can map individual characters to replacement strings.
    # translate() performs the complete character mapping in one pass.
    digit_translation = str.maketrans("0123456789", "abcdefghij")
    show("digit translation", "Account 5027".translate(digit_translation))

    # None in a translation table deletes characters.
    punctuation_table = str.maketrans("", "", ".,!?")
    show(
        "translate() deleting punctuation",
        "Hello, world! Are you ready?".translate(punctuation_table),
    )


# ---------------------------------------------------------------------------
# Text normalization pipeline.
# ---------------------------------------------------------------------------

def normalize_name(value: str) -> str:
    """
    Normalize user-entered names without attempting unsafe transliteration.

    strip() removes boundary whitespace, while casefold() gives a stronger
    Unicode-aware comparison form than lower() for case-insensitive matching.
    """
    cleaned = " ".join(value.strip().split())
    return cleaned.title()


def canonical_email(value: str) -> str:
    """Create a simple canonical form for application-level comparisons."""

    return value.strip().casefold()


def demonstrate_normalization() -> None:
    heading("Normalization Pipelines")

    names = [
        "  atul   pandey ",
        "ATUL PANDEY",
        " Atul\tPandey ",
        "maria   fernández",
    ]

    for name in names:
        show("raw name", name)
        show("normalized name", normalize_name(name))

    emails = [
        "  ATUL.PANDEY@EXAMPLE.COM ",
        "atul.pandey@example.com",
        "User@Example.com",
    ]

    for email in emails:
        show("raw email", email)
        show("canonical email", canonical_email(email))


# ---------------------------------------------------------------------------
# Search and extraction using methods plus regular expressions.
# ---------------------------------------------------------------------------

def extract_key_value(line: str) -> dict[str, str]:
    """Parse a semicolon-separated key=value record."""

    result: dict[str, str] = {}

    for component in line.split(";"):
        key, separator, value = component.partition("=")

        if not separator:
            raise ValueError(f"Malformed component: {component!r}")

        key = key.strip()
        value = value.strip()

        if not key:
            raise ValueError("Empty key is not allowed")

        result[key] = value

    return result


def demonstrate_parsing() -> None:
    heading("Parsing Structured Text")

    record = "user=atul;action=login;status=success;region=IN-NORTH"
    parsed = extract_key_value(record)
    show("Parsed record", parsed)

    malformed = "user=atul;action;status=success"

    try:
        extract_key_value(malformed)
    except ValueError as exc:
        show("Malformed record error", str(exc))

    # String methods perform predictable structural parsing; regular
    # expressions are useful when the text pattern itself is more complex.
    log_line = (
        "2026-10-01 07:30:42 [ERROR] service=payments "
        "request_id=req-42 latency=187ms"
    )

    pattern = re.compile(
        r"^(?P<date>\S+)\s+"
        r"(?P<time>\S+)\s+"
        r"\[(?P<level>[A-Z]+)\]\s+"
        r"service=(?P<service>\S+)\s+"
        r"request_id=(?P<request_id>\S+)\s+"
        r"latency=(?P<latency>\d+)ms$"
    )

    match = pattern.match(log_line)

    if match:
        show("Parsed log fields", match.groupdict())


# ---------------------------------------------------------------------------
# Realistic application: log analyzer.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LogRecord:
    timestamp: str
    level: str
    service: str
    message: str


class LogAnalyzer:
    """
    Analyze application logs using string methods.

    The parser deliberately accepts a simple documented format:
    ISO_TIMESTAMP|LEVEL|SERVICE|MESSAGE
    """

    VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    def __init__(self) -> None:
        self.records: list[LogRecord] = []

    def parse_line(self, line: str) -> LogRecord:
        line = line.strip()

        if not line:
            raise ValueError("blank log line")

        parts = line.split("|", 3)

        if len(parts) != 4:
            raise ValueError("expected four pipe-separated fields")

        timestamp, level, service, message = (
            part.strip() for part in parts
        )

        if not timestamp:
            raise ValueError("timestamp cannot be empty")

        level = level.upper()

        if level not in self.VALID_LEVELS:
            raise ValueError(f"unsupported log level: {level!r}")

        if not service.isidentifier():
            raise ValueError(
                f"service name must be identifier-like: {service!r}"
            )

        if not message:
            raise ValueError("message cannot be empty")

        return LogRecord(timestamp, level, service, message)

    def ingest(self, lines: list[str]) -> tuple[int, list[str]]:
        errors: list[str] = []

        for line_number, line in enumerate(lines, start=1):
            try:
                self.records.append(self.parse_line(line))
            except ValueError as exc:
                errors.append(f"line {line_number}: {exc}")

        return len(self.records), errors

    def count_by_level(self) -> Counter[str]:
        return Counter(record.level for record in self.records)

    def count_by_service(self) -> Counter[str]:
        return Counter(record.service for record in self.records)

    def find_messages(self, term: str) -> list[LogRecord]:
        """
        Perform case-insensitive message matching.

        casefold() is preferred over lower() for robust Unicode-aware
        case-insensitive comparisons.
        """
        normalized_term = term.casefold()

        if not normalized_term:
            return []

        return [
            record
            for record in self.records
            if normalized_term in record.message.casefold()
        ]

    def error_summary(self) -> list[str]:
        return [
            f"{record.timestamp} {record.service}: {record.message}"
            for record in self.records
            if record.level in {"ERROR", "CRITICAL"}
        ]


def demonstrate_log_analyzer() -> None:
    heading("Realistic Log Analyzer")

    lines = [
        "2026-10-01T07:20:01|INFO|gateway|Request accepted",
        "2026-10-01T07:20:02|INFO|auth|User authentication succeeded",
        "2026-10-01T07:20:03|WARNING|gateway|Request latency exceeded threshold",
        "2026-10-01T07:20:04|ERROR|payments|Database connection failed",
        "2026-10-01T07:20:05|ERROR|payments|Database connection retry succeeded",
        "2026-10-01T07:20:06|CRITICAL|gateway|Upstream service unavailable",
        "bad|record",
        "2026-10-01T07:20:07|TRACE|gateway|Unsupported severity",
    ]

    analyzer = LogAnalyzer()
    accepted, errors = analyzer.ingest(lines)

    show("Accepted records", accepted)
    show("Rejected records", len(errors))

    for error in errors:
        print(f"  {error}")

    show("Count by level", dict(analyzer.count_by_level()))
    show("Count by service", dict(analyzer.count_by_service()))

    print("\nMessages containing 'database':")
    for record in analyzer.find_messages("DATABASE"):
        print(f"  {record.timestamp} [{record.level}] {record.message}")

    print("\nError and critical records:")
    for message in analyzer.error_summary():
        print(f"  {message}")


# ---------------------------------------------------------------------------
# File handling with string methods.
# ---------------------------------------------------------------------------

def demonstrate_file_processing() -> None:
    heading("File Processing")

    content = textwrap.dedent(
        """
        # Deployment configuration
        APP_NAME = Market Prism
        ENVIRONMENT = production
        DEBUG = false

        # This line is intentionally ignored
        LOG_LEVEL = warning
        """
    ).strip()

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "config.txt"
        path.write_text(content, encoding="utf-8")

        settings: dict[str, str] = {}

        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            key, separator, value = line.partition("=")

            if not separator:
                raise ValueError(f"Invalid configuration line: {raw_line!r}")

            key = key.strip()
            value = value.strip()

            if not key.isupper():
                raise ValueError(f"Configuration key must be uppercase: {key}")

            settings[key] = value

        show("Loaded settings", settings)
        show("Application name", settings["APP_NAME"])
        show("Environment", settings["ENVIRONMENT"])


# ---------------------------------------------------------------------------
# Security-focused string handling.
# ---------------------------------------------------------------------------

def safe_display_username(username: str) -> str:
    """
    Validate and normalize a display username.

    This is not authentication. String validation alone must never be treated
    as proof that a user owns an account.
    """
    candidate = username.strip()

    if not candidate:
        raise ValueError("username cannot be empty")

    if len(candidate) > 32:
        raise ValueError("username is too long")

    if not candidate.isascii():
        raise ValueError("username must contain ASCII characters")

    if not candidate.replace("_", "").replace("-", "").isalnum():
        raise ValueError("username contains unsupported characters")

    return candidate.casefold()


def demonstrate_security_and_edge_cases() -> None:
    heading("Validation, Security, and Edge Cases")

    usernames = [
        " Atul_Pandey ",
        "admin-user",
        "",
        "user@example.com",
        "normal_user",
    ]

    for username in usernames:
        try:
            show(f"safe username {username!r}", safe_display_username(username))
        except ValueError as exc:
            show(f"rejected username {username!r}", str(exc))

    # strip() does not remove arbitrary internal whitespace. Blindly applying
    # it to security-sensitive structured data can therefore produce a false
    # assumption that the complete value has been normalized.
    suspicious = "admin user"
    show("Internal whitespace remains", suspicious.strip())

    # String equality is exact. For case-insensitive comparison, normalize
    # both operands explicitly instead of relying on visual similarity.
    left = "ADMIN"
    right = "admin"
    show("Exact equality", left == right)
    show("Casefold equality", left.casefold() == right.casefold())

    # Empty separators have different meanings in split().
    show("'a,,b'.split(',')", "a,,b".split(","))
    show("'a,,b'.split()", "a,,b".split())

    # replace() is literal and does not interpret a pattern as a regular
    # expression. This prevents accidental regex semantics.
    show("Literal replace()", "file[1].txt".replace("[1]", "[2]"))


# ---------------------------------------------------------------------------
# Testing the actual topic-specific behavior.
# ---------------------------------------------------------------------------

def run_assertions() -> None:
    heading("Executable Checks")

    assert "  Python  ".strip() == "Python"
    assert "PYTHON".lower() == "python"
    assert "Straße".casefold() == "strasse"
    assert "a,b,c".split(",") == ["a", "b", "c"]
    assert "-".join(["2026", "10", "01"]) == "2026-10-01"
    assert "warning".startswith("warn")
    assert "report.csv".endswith(".csv")
    assert "abc123".isalnum()
    assert not "abc-123".isalnum()
    assert "42".isdigit()
    assert "hello".replace("l", "L") == "heLLo"
    assert "prefix-data".removeprefix("prefix-") == "data"
    assert "data.json".removesuffix(".json") == "data"

    parsed = extract_key_value("a=1;b=2")
    assert parsed == {"a": "1", "b": "2"}

    assert normalize_name("  atul   pandey ") == "Atul Pandey"
    assert canonical_email(" ATUL@EXAMPLE.COM ") == "atul@example.com"

    print("All string-method assertions passed.")


def main() -> None:
    print("STRING METHODS LABORATORY")
    print("Python standard-library implementation")

    demonstrate_fundamentals()
    demonstrate_structure_methods()
    demonstrate_validation()
    demonstrate_formatting()
    demonstrate_translation()
    demonstrate_normalization()
    demonstrate_parsing()
    demonstrate_log_analyzer()
    demonstrate_file_processing()
    demonstrate_security_and_edge_cases()
    run_assertions()


if __name__ == "__main__":
    main()
