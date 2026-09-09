"""
INPUT AND OUTPUT IN PYTHON
==========================

A comprehensive, executable tutorial covering Python input/output from absolute
beginner concepts through advanced and production-oriented techniques.

The script uses only the Python standard library.

Run:
    python input_output_tutorial.py
"""

from __future__ import annotations

import csv
import io
import json
import os
import pickle
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path
from pprint import pprint
from typing import Any


# ============================================================================
# 1. BASIC OUTPUT: print()
# ============================================================================

def section(title: str) -> None:
    """Print a visible section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    """Print a subsection heading."""
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


section("1. BASIC OUTPUT WITH print()")

# print() sends text to standard output, normally the terminal.
print("Hello, Python!")

# Multiple positional arguments are separated by sep.
print("Python", "Input", "Output")

# sep controls the separator between arguments.
print("2026", "09", "09", sep="-")

# end controls what is printed after the final argument.
print("This stays on the same line", end=" ")
print("because end was changed.")

# The default is equivalent to:
# print("Hello\n", end="")
# More precisely, print() uses sep=" " and end="\n".
print("A", "B", "C", sep=" | ", end=".\n")

# print() can display different Python types.
print(42)
print(3.14159)
print(True)
print(None)
print([1, 2, 3])
print({"name": "Alice", "age": 30})


# ============================================================================
# 2. ESCAPE SEQUENCES
# ============================================================================

section("2. ESCAPE SEQUENCES AND FORMATTED OUTPUT")

print("Line one\nLine two")
print("Column1\tColumn2")
print("A quote: \"Python\"")
print("A backslash: \\")
print("A carriage return example: ABC\rXYZ")

# Raw strings suppress most escape-sequence processing.
print(r"C:\Users\Student\Documents")
print(r"Line\nis not split here.")

# Unicode characters can be printed directly.
print("Unicode:", "₹", "€", "π", "→")


# ============================================================================
# 3. STRING FORMATTING
# ============================================================================

section("3. STRING FORMATTING")

name = "Anita"
age = 25
score = 91.4567

# Concatenation is possible, but explicit conversion is required for
# non-string objects.
print("Name: " + name + ", Age: " + str(age))

# str.format()
print("Name: {}, Age: {}, Score: {:.2f}".format(name, age, score))

# Named format fields.
print("Name: {n}, Age: {a}, Score: {s:.2f}".format(
    n=name,
    a=age,
    s=score,
))

# F-strings are generally the clearest modern formatting technique.
print(f"Name: {name}, Age: {age}, Score: {score:.2f}")

# Useful formatting specifications.
amount = 1234567.891
print(f"Amount: ₹{amount:,.2f}")
print(f"Percentage: {0.87345:.2%}")
print(f"Integer padded with zeros: {42:06d}")
print(f"Left aligned:  {'Python':<15}")
print(f"Right aligned: {'Python':>15}")
print(f"Centered:       {'Python':^15}")


# ============================================================================
# 4. STANDARD OUTPUT STREAM: sys.stdout
# ============================================================================

section("4. STANDARD OUTPUT: sys.stdout")

# print() ultimately writes to a text output stream.
sys.stdout.write("sys.stdout.write() does not automatically add a newline.")
sys.stdout.write("\n")
sys.stdout.write("Explicit newline\n")

# print() can target another file-like object using file=.
buffer = io.StringIO()
print("First line", file=buffer)
print("Second line", file=buffer)
print("Captured content:")
print(buffer.getvalue(), end="")


# ============================================================================
# 5. STANDARD ERROR: sys.stderr
# ============================================================================

section("5. STANDARD ERROR: sys.stderr")

# stderr is conventionally used for diagnostic/error messages.
print("This is a normal message.", file=sys.stdout)
print("This is a diagnostic message.", file=sys.stderr)

# stdout and stderr are separate streams at the operating-system level.
# A shell can redirect them independently.


# ============================================================================
# 6. BASIC INPUT WITH input()
# ============================================================================

section("6. BASIC INPUT WITH input()")

# input() reads one line from standard input and returns a STRING.
#
# The following examples are shown as functions so that this tutorial can run
# non-interactively without waiting for user input.

def demonstrate_input_with_supplied_text(raw_text: str) -> None:
    """
    Demonstrate the operations normally performed after input().

    Real interactive version:
        user_text = input("Enter text: ")
    """
    user_text = raw_text
    print("Received:", user_text)
    print("Type:", type(user_text).__name__)


demonstrate_input_with_supplied_text("hello Python")

# Important:
# input() does NOT automatically convert numbers.
#
# Interactive equivalent:
# age_text = input("Enter your age: ")
# age = int(age_text)

sample_integer_input = "42"
sample_float_input = "19.75"

integer_value = int(sample_integer_input)
float_value = float(sample_float_input)

print("Converted integer:", integer_value, type(integer_value).__name__)
print("Converted float:", float_value, type(float_value).__name__)


# ============================================================================
# 7. SAFE INPUT CONVERSION
# ============================================================================

section("7. VALIDATING AND CONVERTING USER INPUT")

def parse_integer(text: str) -> int:
    """Convert text to an integer or raise ValueError with a clear message."""
    cleaned = text.strip()

    if not cleaned:
        raise ValueError("Input cannot be empty.")

    try:
        return int(cleaned)
    except ValueError as exc:
        raise ValueError(f"Expected an integer, received {text!r}.") from exc


def parse_float(text: str) -> float:
    """Convert text to a finite floating-point number."""
    cleaned = text.strip()

    if not cleaned:
        raise ValueError("Input cannot be empty.")

    try:
        value = float(cleaned)
    except ValueError as exc:
        raise ValueError(f"Expected a number, received {text!r}.") from exc

    if not __import__("math").isfinite(value):
        raise ValueError("The number must be finite.")

    return value


for raw_value in ["42", "  -17 ", "0", "+99"]:
    print(raw_value, "->", parse_integer(raw_value))

for raw_value in ["3.14", "  -2.5 ", "0.0"]:
    print(raw_value, "->", parse_float(raw_value))

for invalid in ["", "abc", "12.5"]:
    try:
        print("Trying:", invalid!r)
        print(parse_integer(invalid))
    except ValueError as error:
        print("Validation error:", error)


# ============================================================================
# 8. BOOLEAN INPUT
# ============================================================================

section("8. BOOLEAN INPUT")

def parse_boolean(text: str) -> bool:
    """
    Parse common textual boolean representations.

    bool("False") is True because any non-empty string is truthy.
    Therefore, directly calling bool() on user text is usually incorrect.
    """
    normalized = text.strip().casefold()

    if normalized in {"true", "t", "yes", "y", "1", "on"}:
        return True

    if normalized in {"false", "f", "no", "n", "0", "off"}:
        return False

    raise ValueError(f"Unrecognized boolean value: {text!r}")


for value in ["yes", "NO", "True", "false", "1", "0"]:
    print(value, "->", parse_boolean(value))

print('bool("False") ->', bool("False"))
print('parse_boolean("False") ->', parse_boolean("False"))


# ============================================================================
# 9. INPUT VALIDATION LOOPS
# ============================================================================

section("9. REUSABLE INPUT VALIDATION PATTERNS")

def validate_age(text: str) -> int:
    """Validate an age within a reasonable application-defined range."""
    age = parse_integer(text)

    if not 0 <= age <= 150:
        raise ValueError("Age must be between 0 and 150.")

    return age


def get_value_from_attempts(
    attempts: list[str],
    parser,
    default: Any = None,
) -> Any:
    """
    Simulate an interactive validation loop.

    A real application can replace attempts with repeated input().
    """
    for attempt in attempts:
        try:
            return parser(attempt)
        except ValueError as error:
            print(f"Invalid input {attempt!r}: {error}")

    print("All attempts failed.")
    return default


age = get_value_from_attempts(["abc", "-5", "33"], validate_age)
print("Accepted age:", age)

# A conventional interactive pattern is:
#
# while True:
#     try:
#         age = validate_age(input("Enter age: "))
#         break
#     except ValueError as error:
#         print(error)


# ============================================================================
# 10. MULTIPLE VALUES FROM ONE INPUT LINE
# ============================================================================

section("10. SPLITTING INPUT")

raw_line = "10 20 30 40"
parts = raw_line.split()
numbers = [int(part) for part in parts]

print("Parts:", parts)
print("Numbers:", numbers)

# Comma-separated input.
raw_csv_like = "Python,SQL,Excel,Statistics"
skills = [item.strip() for item in raw_csv_like.split(",")]
print("Skills:", skills)

# Multiple assignment.
first, second, third = ["A", "B", "C"]
print(first, second, third)

# Starred unpacking.
first, *middle, last = [10, 20, 30, 40, 50]
print("First:", first)
print("Middle:", middle)
print("Last:", last)


# ============================================================================
# 11. sys.stdin
# ============================================================================

section("11. STANDARD INPUT: sys.stdin")

# input() is convenient for one line at a time.
# sys.stdin is useful when processing streams of text, especially redirected
# files and command pipelines.

simulated_stdin = io.StringIO("apple\nbanana\ncherry\n")

for line in simulated_stdin:
    print("Read:", line.rstrip("\n"))

# In a real program:
#
# for line in sys.stdin:
#     process(line)
#
# This pattern is memory-efficient because it processes one line at a time.


# ============================================================================
# 12. FILE PATHS WITH pathlib
# ============================================================================

section("12. FILE PATHS WITH pathlib")

# pathlib provides an object-oriented interface for filesystem paths.
temporary_root = Path(tempfile.mkdtemp(prefix="python_io_tutorial_"))
print("Temporary directory:", temporary_root)

text_file = temporary_root / "notes.txt"
json_file = temporary_root / "data.json"
csv_file = temporary_root / "employees.csv"
binary_file = temporary_root / "binary.dat"
pickle_file = temporary_root / "object.pkl"


# ============================================================================
# 13. WRITING TEXT FILES
# ============================================================================

section("13. WRITING TEXT FILES")

content = "Python\nInput\nOutput\n"

# Path.write_text() is convenient for simple text files.
text_file.write_text(content, encoding="utf-8")

print("File exists:", text_file.exists())
print("File size:", text_file.stat().st_size, "bytes")


# ============================================================================
# 14. READING TEXT FILES
# ============================================================================

section("14. READING TEXT FILES")

# read_text() loads the entire file into memory.
loaded_content = text_file.read_text(encoding="utf-8")
print(loaded_content, end="")

# open() provides more control.
with open(text_file, "r", encoding="utf-8") as file:
    content_from_open = file.read()

print("Read using open():")
print(content_from_open, end="")


# ============================================================================
# 15. FILE MODES
# ============================================================================

section("15. FILE MODES")

# Common text/binary modes:
#
# r   read
# w   write, truncating an existing file
# a   append
# x   create exclusively, failing if the file exists
# b   binary mode modifier
# t   text mode modifier
# +   update mode: reading and writing
#
# Examples:
#   "r"
#   "w"
#   "a"
#   "x"
#   "rb"
#   "wb"
#   "r+"
#   "w+"
#
# Be careful with "w": opening an existing file with "w" truncates it.

append_file = temporary_root / "append.txt"
with open(append_file, "w", encoding="utf-8") as file:
    file.write("First\n")

with open(append_file, "a", encoding="utf-8") as file:
    file.write("Second\n")

print(append_file.read_text(encoding="utf-8"), end="")


# ============================================================================
# 16. CONTEXT MANAGERS
# ============================================================================

section("16. CONTEXT MANAGERS AND with")

with open(text_file, "r", encoding="utf-8") as file:
    first_line = file.readline().rstrip("\n")
    print("First line:", first_line)

# After the with block, the file is automatically closed.
print("File closed:", file.closed)

# This is safer than manually opening and closing:
#
# file = open(...)
# try:
#     ...
# finally:
#     file.close()


# ============================================================================
# 17. READ, READLINE, READLINES
# ============================================================================

section("17. read(), readline(), readlines()")

multi_line_file = temporary_root / "multi.txt"
multi_line_file.write_text("one\ntwo\nthree\n", encoding="utf-8")

with open(multi_line_file, "r", encoding="utf-8") as file:
    print("readline 1:", file.readline().rstrip())
    print("readline 2:", file.readline().rstrip())

with open(multi_line_file, "r", encoding="utf-8") as file:
    print("read():", repr(file.read()))

with open(multi_line_file, "r", encoding="utf-8") as file:
    print("readlines():", file.readlines())

# Iterating over the file is normally preferable for large files.
with open(multi_line_file, "r", encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        print(line_number, line.rstrip())


# ============================================================================
# 18. FILE POINTERS: tell() AND seek()
# ============================================================================

section("18. FILE POINTERS: tell() AND seek()")

with open(multi_line_file, "r", encoding="utf-8") as file:
    print("Initial position:", file.tell())
    print("Read:", file.read(3))
    print("Position after 3 characters:", file.tell())

    file.seek(0)
    print("Position after seek(0):", file.tell())
    print("First line again:", file.readline().rstrip())

    # seek() can reposition within a file, though character/byte semantics
    # depend on whether the stream is text or binary.


# ============================================================================
# 19. ENCODING AND NEWLINES
# ============================================================================

section("19. TEXT ENCODING AND NEWLINES")

unicode_file = temporary_root / "unicode.txt"
unicode_text = "भारत\nPython\nCafé\n"

unicode_file.write_text(unicode_text, encoding="utf-8")
print(unicode_file.read_text(encoding="utf-8"), end="")

# Always choose an explicit encoding for portable application code when the
# intended encoding is known. UTF-8 is the common choice.
#
# newline behavior can be controlled with open(..., newline=...).
#
# On reading, Python can perform universal newline translation.
# On writing, newline=None uses platform conventions.


# ============================================================================
# 20. TEXT VS BINARY I/O
# ============================================================================

section("20. TEXT VS BINARY I/O")

binary_data = bytes([0, 1, 2, 65, 66, 255])
binary_file.write_bytes(binary_data)

print("Binary bytes:", binary_file.read_bytes())

with open(binary_file, "rb") as file:
    raw_bytes = file.read()

print("Type from binary read:", type(raw_bytes).__name__)
print("Raw bytes:", raw_bytes)

# Text mode returns str.
# Binary mode returns bytes.
#
# str and bytes are different types:
text = "hello"
encoded = text.encode("utf-8")
decoded = encoded.decode("utf-8")

print("Text:", text, type(text).__name__)
print("Encoded:", encoded, type(encoded).__name__)
print("Decoded:", decoded, type(decoded).__name__)


# ============================================================================
# 21. ENCODING ERRORS
# ============================================================================

section("21. ENCODING AND DECODING ERRORS")

invalid_utf8 = b"\xff\xfe\xfd"

try:
    invalid_utf8.decode("utf-8")
except UnicodeDecodeError as error:
    print("Decode error:", error)

# Error strategies include:
#   strict  -> raise an exception
#   ignore  -> discard invalid data
#   replace -> replace invalid data with a replacement marker
#
print(invalid_utf8.decode("utf-8", errors="replace"))


# ============================================================================
# 22. JSON OUTPUT AND INPUT
# ============================================================================

section("22. JSON INPUT/OUTPUT")

person = {
    "name": "Rahul",
    "age": 29,
    "skills": ["Python", "SQL"],
    "active": True,
    "manager": None,
}

json_string = json.dumps(person, indent=2, ensure_ascii=False)
print(json_string)

json_file.write_text(json_string, encoding="utf-8")

loaded_person = json.loads(json_file.read_text(encoding="utf-8"))
print("Loaded JSON object:")
pprint(loaded_person)

# Direct file-based JSON APIs:
with open(json_file, "w", encoding="utf-8") as file:
    json.dump(person, file, indent=2, ensure_ascii=False)

with open(json_file, "r", encoding="utf-8") as file:
    person_from_file = json.load(file)

print("Name:", person_from_file["name"])


# ============================================================================
# 23. JSON TYPES AND LIMITATIONS
# ============================================================================

section("23. JSON TYPE MAPPING AND LIMITATIONS")

json_compatible = {
    "string": "text",
    "integer": 10,
    "float": 2.5,
    "boolean": True,
    "null": None,
    "array": [1, 2, 3],
    "object": {"key": "value"},
}

print(json.dumps(json_compatible, indent=2))

# Python-specific objects such as sets are not directly JSON serializable.
try:
    json.dumps({"numbers": {1, 2, 3}})
except TypeError as error:
    print("JSON serialization error:", error)

# A custom default serializer can define how selected objects are represented.
def json_default_serializer(value: Any) -> Any:
    if isinstance(value, set):
        return sorted(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


print(json.dumps(
    {"numbers": {3, 1, 2}},
    default=json_default_serializer,
))


# ============================================================================
# 24. CSV INPUT/OUTPUT
# ============================================================================

section("24. CSV INPUT/OUTPUT")

employees = [
    {"id": 1, "name": "Asha", "department": "Data", "salary": 65000},
    {"id": 2, "name": "Vikram", "department": "Engineering", "salary": 80000},
    {"id": 3, "name": "Neha", "department": "HR", "salary": 60000},
]

fieldnames = ["id", "name", "department", "salary"]

with open(csv_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(employees)

print(csv_file.read_text(encoding="utf-8"))

with open(csv_file, "r", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    rows = list(reader)

print("CSV rows:")
pprint(rows)

# CSV values are strings when read.
print("Type of CSV salary:", type(rows[0]["salary"]).__name__)
rows[0]["salary"] = int(rows[0]["salary"])
print("Converted salary:", rows[0]["salary"])


# ============================================================================
# 25. csv.reader AND csv.writer
# ============================================================================

section("25. csv.reader AND csv.writer")

simple_csv = temporary_root / "simple.csv"

with open(simple_csv, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Score"])
    writer.writerow(["Asha", 95])
    writer.writerow(["Vikram", 88])

with open(simple_csv, "r", newline="", encoding="utf-8") as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)


# ============================================================================
# 26. CSV QUOTING AND SPECIAL CHARACTERS
# ============================================================================

section("26. CSV QUOTING")

quoting_file = temporary_root / "quoting.csv"

data_with_commas = [
    ["Name", "Comment"],
    ["Alice", "Excellent, reliable employee"],
    ["Bob", 'Said "hello" during the meeting'],
]

with open(quoting_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(data_with_commas)

print(quoting_file.read_text(encoding="utf-8"))


# ============================================================================
# 27. IN-MEMORY FILES WITH io.StringIO
# ============================================================================

section("27. IN-MEMORY TEXT STREAMS")

text_stream = io.StringIO()

text_stream.write("First\n")
text_stream.write("Second\n")

print("Current stream position:", text_stream.tell())
print("Contents:", repr(text_stream.getvalue()))

text_stream.seek(0)
print("Read first line:", text_stream.readline().rstrip())

# StringIO behaves like a text file in many APIs.
# It is useful for testing and for constructing output without disk I/O.


# ============================================================================
# 28. IN-MEMORY BINARY STREAMS WITH io.BytesIO
# ============================================================================

section("28. IN-MEMORY BINARY STREAMS")

binary_stream = io.BytesIO()

binary_stream.write(b"Hello ")
binary_stream.write("Python".encode("utf-8"))

print("BytesIO content:", binary_stream.getvalue())

binary_stream.seek(0)
print("BytesIO read:", binary_stream.read())


# ============================================================================
# 29. FILE-LIKE OBJECTS
# ============================================================================

section("29. FILE-LIKE OBJECTS")

def write_report(output_stream: io.TextIOBase, title: str, values: list[int]) -> None:
    """
    Write to any compatible text stream.

    The function does not care whether output_stream is:
      - an actual disk file,
      - sys.stdout,
      - io.StringIO(),
      - another text stream.
    """
    output_stream.write(f"{title}\n")
    output_stream.write("=" * len(title) + "\n")
    for value in values:
        output_stream.write(f"- {value}\n")


memory_report = io.StringIO()
write_report(memory_report, "Scores", [91, 88, 95])
print(memory_report.getvalue(), end="")

# The same function can write directly to stdout.
write_report(sys.stdout, "Direct Report", [10, 20, 30])


# ============================================================================
# 30. TEMPORARY FILES
# ============================================================================

section("30. TEMPORARY FILES AND DIRECTORIES")

with tempfile.TemporaryDirectory(prefix="io_demo_") as temp_dir:
    temp_path = Path(temp_dir)
    temporary_file = temp_path / "temporary.txt"
    temporary_file.write_text("Temporary content", encoding="utf-8")

    print("Temporary file:", temporary_file)
    print("Content:", temporary_file.read_text(encoding="utf-8"))

# TemporaryDirectory is automatically cleaned up after the with block.


# ============================================================================
# 31. SAFE FILE WRITING AND ATOMIC REPLACEMENT
# ============================================================================

section("31. ATOMIC-STYLE FILE REPLACEMENT")

def atomic_write_text(
    destination: Path,
    content: str,
    encoding: str = "utf-8",
) -> None:
    """
    Write content through a temporary file and replace the destination.

    This reduces the risk of leaving a partially written destination when the
    process fails during the write. True durability guarantees also depend on
    the operating system and filesystem.
    """
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding=encoding,
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            file.write(content)
            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


atomic_file = temporary_root / "atomic.txt"
atomic_write_text(atomic_file, "Safely replaced content\n")
print(atomic_file.read_text(encoding="utf-8"), end="")


# ============================================================================
# 32. FILE METADATA AND DIRECTORY OPERATIONS
# ============================================================================

section("32. FILESYSTEM INPUT/OUTPUT")

nested_directory = temporary_root / "reports" / "2026"
nested_directory.mkdir(parents=True, exist_ok=True)

report_file = nested_directory / "report.txt"
report_file.write_text("Annual report", encoding="utf-8")

print("Exists:", report_file.exists())
print("Is file:", report_file.is_file())
print("Is directory:", report_file.is_dir())
print("Name:", report_file.name)
print("Suffix:", report_file.suffix)
print("Parent:", report_file.parent)

print("Directory contents:")
for path in temporary_root.rglob("*"):
    print(" ", path.relative_to(temporary_root))


# ============================================================================
# 33. COPYING, MOVING, AND DELETING
# ============================================================================

section("33. COPYING, MOVING, AND DELETING FILES")

source = temporary_root / "source.txt"
copy = temporary_root / "copy.txt"
moved = temporary_root / "moved.txt"

source.write_text("Source data", encoding="utf-8")
shutil.copy2(source, copy)
print("Copied:", copy.read_text(encoding="utf-8"))

shutil.move(copy, moved)
print("Moved exists:", moved.exists())

moved.unlink()
print("Deleted:", not moved.exists())


# ============================================================================
# 34. BINARY FILES AND BYTE PROCESSING
# ============================================================================

section("34. BINARY FILE PROCESSING")

raw = bytes(range(16))
binary_file.write_bytes(raw)

with open(binary_file, "rb") as file:
    first_four = file.read(4)
    remaining = file.read()

print("First four bytes:", first_four)
print("Remaining bytes:", remaining)

# Binary files are appropriate for images, compressed files, executables,
# network payloads, serialized data, and other non-text formats.


# ============================================================================
# 35. BUFFERING
# ============================================================================

section("35. BUFFERING")

# File objects may buffer reads and writes for efficiency.
buffered_file = temporary_root / "buffered.txt"

with open(buffered_file, "w", encoding="utf-8") as file:
    file.write("Buffered output\n")
    file.flush()
    # flush() transfers Python-level buffered data to the underlying stream.
    # It does not necessarily guarantee physical disk persistence.

print(buffered_file.read_text(encoding="utf-8"), end="")

# os.fsync(file.fileno()) can request that the operating system flush data to
# the storage device, but its exact durability behavior depends on the system.


# ============================================================================
# 36. PICKLE SERIALIZATION
# ============================================================================

section("36. PICKLE SERIALIZATION")

complex_object = {
    "numbers": {1, 2, 3},
    "tuple": (10, 20),
    "nested": {"enabled": True},
}

with open(pickle_file, "wb") as file:
    pickle.dump(complex_object, file)

with open(pickle_file, "rb") as file:
    restored_object = pickle.load(file)

print("Restored object:")
pprint(restored_object)

# SECURITY WARNING:
# Never unpickle untrusted data.
# pickle can execute arbitrary code during deserialization.
#
# JSON is usually preferable for untrusted or cross-language data exchange.


# ============================================================================
# 37. COMMAND-LINE ARGUMENTS
# ============================================================================

section("37. COMMAND-LINE INPUT")

print("sys.argv contains command-line arguments.")
print("Current sys.argv:", sys.argv)

# A real command might look like:
#
# python program.py input.txt --limit 10
#
# For production command-line interfaces, argparse is preferable to manually
# interpreting sys.argv.


# ============================================================================
# 38. ARGPARSE DEMONSTRATION
# ============================================================================

section("38. argparse FOR COMMAND-LINE INTERFACES")

import argparse

def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Demonstrate structured command-line input."
    )
    parser.add_argument(
        "--name",
        default="Student",
        help="Name to display.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of greetings.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )
    return parser


# parse_args() would normally process the actual command line.
# To keep this tutorial self-contained and safe to run with arbitrary command
# line arguments, parse a controlled example instead.
parser = build_argument_parser()
demo_arguments = parser.parse_args([
    "--name", "Asha",
    "--count", "2",
    "--verbose",
])

for _ in range(demo_arguments.count):
    print(f"Hello, {demo_arguments.name}!")

if demo_arguments.verbose:
    print("Verbose mode is enabled.")


# ============================================================================
# 39. ENVIRONMENT VARIABLES
# ============================================================================

section("39. ENVIRONMENT VARIABLES")

# Environment variables are another form of external input.
path_value = os.environ.get("PATH")
print("PATH is configured:", path_value is not None)

# get() allows a default.
application_mode = os.environ.get("APP_MODE", "development")
print("Application mode:", application_mode)

# Environment variables are strings.
# Convert and validate explicitly:
sample_port_text = "8080"
sample_port = parse_integer(sample_port_text)
print("Validated port:", sample_port)

# Never assume environment variables are trusted. Validate them just like
# command-line or interactive input.


# ============================================================================
# 40. REDIRECTION AND PIPELINE CONCEPTS
# ============================================================================

section("40. STANDARD STREAM REDIRECTION CONCEPTS")

print(
    "Typical shell redirection:",
    "python program.py > output.txt",
)

print(
    "Typical stderr redirection:",
    "python program.py 2> errors.txt",
)

print(
    "Typical pipeline:",
    "python program.py | another_program",
)

# The Python program itself can simply read sys.stdin and write sys.stdout.
# The operating system or shell connects those streams to files or processes.


# ============================================================================
# 41. LOGGING VS print()
# ============================================================================

section("41. logging VS print()")

import logging

logger = logging.getLogger("input_output_demo")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(levelname)s: %(message)s")
    )
    logger.addHandler(handler)

logger.info("This message is emitted through logging.")
logger.warning("Logging supports severity levels and configuration.")

# print() is suitable for simple user-facing output.
# logging is generally better for diagnostics in reusable applications because
# handlers, levels, formatting, destinations, and filtering can be configured.


# ============================================================================
# 42. CUSTOM OUTPUT CLASS
# ============================================================================

section("42. CUSTOM FILE-LIKE OUTPUT")

class PrefixWriter:
    """A minimal text writer that adds a prefix to each write."""

    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def write(self, text: str) -> int:
        prefixed_text = self.prefix + text
        return sys.stdout.write(prefixed_text)

    def flush(self) -> None:
        sys.stdout.flush()


prefix_writer = PrefixWriter("[CUSTOM] ")
print("Hello from a custom writer.", file=prefix_writer, end="\n")


# ============================================================================
# 43. VALIDATION WITH REGULAR EXPRESSIONS
# ============================================================================

section("43. STRUCTURED INPUT VALIDATION")

email_pattern = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)

sample_emails = [
    "student@example.com",
    "invalid-email",
]

for email in sample_emails:
    print(email, "->", bool(email_pattern.fullmatch(email)))

# Regular expressions are useful for structural validation, but an expression
# alone cannot prove that an address exists or that a user controls it.


# ============================================================================
# 44. RANGE AND SIZE VALIDATION
# ============================================================================

section("44. RANGE, LENGTH, AND DOMAIN VALIDATION")

def validate_percentage(text: str) -> float:
    percentage = parse_float(text)

    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100.")

    return percentage


def validate_username(text: str) -> str:
    username = text.strip()

    if not 3 <= len(username) <= 20:
        raise ValueError("Username must contain 3 to 20 characters.")

    if not re.fullmatch(r"[A-Za-z0-9_]+", username):
        raise ValueError(
            "Username may contain only letters, digits, and underscores."
        )

    return username


print("Percentage:", validate_percentage("87.5"))
print("Username:", validate_username("student_01"))


# ============================================================================
# 45. ERROR HANDLING
# ============================================================================

section("45. INPUT/OUTPUT ERROR HANDLING")

missing_file = temporary_root / "does_not_exist.txt"

try:
    missing_file.read_text(encoding="utf-8")
except FileNotFoundError as error:
    print("Missing file handled:", error)

try:
    with open(temporary_root, "not_a_file", encoding="utf-8"):
        pass
except (IsADirectoryError, PermissionError, OSError) as error:
    print("Filesystem error handled:", type(error).__name__)

try:
    parse_integer("not-an-integer")
except ValueError as error:
    print("Conversion error handled:", error)


# ============================================================================
# 46. EXCEPTIONS: SPECIFIC BEFORE GENERAL
# ============================================================================

section("46. EXCEPTION HANDLING ORDER")

def read_required_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print("The requested file does not exist.")
        raise
    except PermissionError:
        print("Permission denied.")
        raise
    except OSError:
        print("Another operating-system I/O error occurred.")
        raise


try:
    read_required_file(missing_file)
except FileNotFoundError:
    print("Caller received the specific exception.")

# Avoid:
#
# except Exception:
#     pass
#
# Such code can silently hide programming defects and operational failures.


# ============================================================================
# 47. EAFP AND LBYL
# ============================================================================

section("47. EAFP VS LBYL")

# Python commonly favors EAFP:
# "Easier to Ask Forgiveness than Permission."

def read_if_available_eafp(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


# LBYL:
# "Look Before You Leap."

def read_if_available_lbyl(path: Path) -> str | None:
    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8")
    return None


print("EAFP:", read_if_available_eafp(text_file))
print("LBYL:", read_if_available_lbyl(text_file))

# EAFP can be safer when filesystem state can change between the check and use.
# LBYL can be useful when a preliminary check itself is meaningful to the
# application. For filesystem access, exceptions remain important even after
# checks because the operation can still fail.


# ============================================================================
# 48. LARGE FILES AND STREAMING
# ============================================================================

section("48. STREAMING LARGE TEXT FILES")

large_file = temporary_root / "large.txt"

with open(large_file, "w", encoding="utf-8") as file:
    for number in range(1000):
        file.write(f"record-{number}\n")


def count_matching_lines(path: Path, keyword: str) -> int:
    """Process one line at a time rather than loading the whole file."""
    count = 0

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if keyword in line:
                count += 1

    return count


print("Matching records:", count_matching_lines(large_file, "record-99"))


# ============================================================================
# 49. CHUNKED BINARY I/O
# ============================================================================

section("49. CHUNKED BINARY I/O")

def copy_binary_stream(
    source_path: Path,
    destination_path: Path,
    chunk_size: int = 64 * 1024,
) -> int:
    """
    Copy a binary file incrementally.

    Returning the number of bytes copied makes the operation testable.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    total_bytes = 0

    with open(source_path, "rb") as source, open(destination_path, "wb") as destination:
        while True:
            chunk = source.read(chunk_size)
            if not chunk:
                break

            destination.write(chunk)
            total_bytes += len(chunk)

    return total_bytes


binary_copy = temporary_root / "binary_copy.dat"
bytes_copied = copy_binary_stream(binary_file, binary_copy, chunk_size=4)

print("Bytes copied:", bytes_copied)
print("Copy correct:", binary_file.read_bytes() == binary_copy.read_bytes())


# ============================================================================
# 50. HASHING FILE CONTENT
# ============================================================================

section("50. STREAMING FILE HASH")

import hashlib

def sha256_file(path: Path, chunk_size: int = 64 * 1024) -> str:
    """Compute a SHA-256 digest without loading the entire file."""
    digest = hashlib.sha256()

    with open(path, "rb") as file:
        while chunk := file.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()


print("SHA-256:", sha256_file(binary_file))


# ============================================================================
# 51. COMPRESSION I/O
# ============================================================================

section("51. GZIP I/O")

import gzip

gzip_file = temporary_root / "data.txt.gz"

with gzip.open(gzip_file, "wt", encoding="utf-8") as file:
    file.write("Compressed text\n")
    file.write("Second line\n")

with gzip.open(gzip_file, "rt", encoding="utf-8") as file:
    compressed_content = file.read()

print(compressed_content, end="")


# ============================================================================
# 52. ZIP I/O
# ============================================================================

section("52. ZIP ARCHIVES")

import zipfile

zip_file = temporary_root / "archive.zip"

with zipfile.ZipFile(zip_file, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    archive.write(text_file, arcname="notes.txt")
    archive.write(json_file, arcname="data.json")

with zipfile.ZipFile(zip_file, "r") as archive:
    print("Archive members:", archive.namelist())
    extracted_json = archive.read("data.json").decode("utf-8")
    print("JSON from archive:")
    print(extracted_json)


# ============================================================================
# 53. PATH TRAVERSAL SECURITY
# ============================================================================

section("53. PATH TRAVERSAL SECURITY")

def safe_child_path(base_directory: Path, user_supplied_name: str) -> Path:
    """
    Resolve a user-supplied path and ensure it remains inside base_directory.

    This protects applications that accept filenames from untrusted users.
    """
    base = base_directory.resolve()
    candidate = (base / user_supplied_name).resolve()

    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise ValueError("Path escapes the permitted directory.") from exc

    return candidate


print("Safe path:", safe_child_path(temporary_root, "reports/output.txt"))

for unsafe_name in ["../outside.txt", "../../secret.txt"]:
    try:
        print(safe_child_path(temporary_root, unsafe_name))
    except ValueError as error:
        print("Blocked unsafe path:", error)


# ============================================================================
# 54. SAFE FILE EXTENSIONS ARE NOT SECURITY
# ============================================================================

section("54. FILE EXTENSIONS ARE NOT TRUST BOUNDARIES")

# A filename such as "image.jpg" does not prove that the contents are an image.
# Security-sensitive applications should inspect and validate file contents
# according to the actual format, enforce size limits, and avoid unsafe
# processing of untrusted data.

fake_image = temporary_root / "photo.jpg"
fake_image.write_text("This is not actually an image.", encoding="utf-8")

print("Filename suffix:", fake_image.suffix)
print("Content begins with:", fake_image.read_text(encoding="utf-8")[:20])

# The suffix alone is not proof of file type.


# ============================================================================
# 55. RESOURCE LIMITS
# ============================================================================

section("55. INPUT SIZE LIMITS")

MAX_INPUT_LENGTH = 100

def validate_text_length(text: str, maximum: int = MAX_INPUT_LENGTH) -> str:
    if len(text) > maximum:
        raise ValueError(
            f"Input exceeds the maximum allowed length of {maximum}."
        )
    return text


print(validate_text_length("short text"))

try:
    validate_text_length("x" * 101)
except ValueError as error:
    print("Length limit enforced:", error)


# ============================================================================
# 56. COMMAND INJECTION CONSIDERATIONS
# ============================================================================

section("56. SHELL COMMAND SECURITY")

# User input should NOT normally be interpolated directly into shell commands.
#
# Unsafe conceptual pattern:
#     os.system("some_command " + user_input)
#
# If a subprocess is genuinely needed, prefer an argument list and avoid
# shell=True unless shell interpretation is deliberately required.

import subprocess

completed = subprocess.run(
    [sys.executable, "-c", "print('subprocess output')"],
    capture_output=True,
    text=True,
    check=True,
)

print("stdout:", completed.stdout.strip())
print("stderr:", completed.stderr.strip())

# capture_output=True captures both stdout and stderr.
# text=True decodes output into str rather than bytes.
# check=True raises CalledProcessError when the command exits unsuccessfully.


# ============================================================================
# 57. SUBPROCESS INPUT
# ============================================================================

section("57. SUBPROCESS INPUT AND OUTPUT")

echo_program = (
    "import sys; "
    "data = sys.stdin.read(); "
    "print(data.upper(), end='')"
)

result = subprocess.run(
    [sys.executable, "-c", echo_program],
    input="hello from stdin\n",
    capture_output=True,
    text=True,
    check=True,
)

print("Subprocess transformed output:", result.stdout.rstrip())


# ============================================================================
# 58. STDOUT AND STDERR CAPTURE
# ============================================================================

section("58. CAPTURING OUTPUT IN TESTS")

def generate_message(name: str, output_stream: io.TextIOBase) -> None:
    output_stream.write(f"Hello, {name}!\n")


captured = io.StringIO()
generate_message("Tester", captured)

expected = "Hello, Tester!\n"
actual = captured.getvalue()

print("Expected:", repr(expected))
print("Actual:  ", repr(actual))
print("Match:", actual == expected)


# ============================================================================
# 59. UNIT TESTING I/O
# ============================================================================

section("59. TESTING INPUT/OUTPUT CODE")

import unittest
from unittest.mock import patch

def interactive_greeting() -> None:
    name = input("Name: ")
    print(f"Hello, {name}!")


class InputOutputTests(unittest.TestCase):
    def test_output_function(self) -> None:
        stream = io.StringIO()

        generate_message("Asha", stream)

        self.assertEqual(stream.getvalue(), "Hello, Asha!\n")

    def test_input_function(self) -> None:
        with patch("builtins.input", return_value="Vikram"):
            captured_output = io.StringIO()

            with patch("sys.stdout", new=captured_output):
                interactive_greeting()

            self.assertEqual(
                captured_output.getvalue(),
                "Hello, Vikram!\n",
            )


test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(InputOutputTests)
test_result = unittest.TextTestRunner(
    stream=io.StringIO(),
    verbosity=0,
).run(test_suite)

print("Tests run:", test_result.testsRun)
print("Failures:", len(test_result.failures))
print("Errors:", len(test_result.errors))


# ============================================================================
# 60. JSON ROUND-TRIP TEST
# ============================================================================

section("60. SERIALIZATION ROUND-TRIP")

original = {
    "name": "Meera",
    "age": 31,
    "scores": [91, 87, 95],
    "active": True,
    "manager": None,
}

serialized = json.dumps(original)
restored = json.loads(serialized)

print("Round-trip successful:", original == restored)


# ============================================================================
# 61. CUSTOM JSON ENCODER
# ============================================================================

section("61. CUSTOM JSON ENCODER")

from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone

@dataclass
class Employee:
    employee_id: int
    name: str
    salary: float


employee = Employee(101, "Riya", 75000.50)

# dataclasses can be converted into dictionaries.
employee_dictionary = asdict(employee)
print(employee_dictionary)

# datetime and date require an explicit JSON representation.
timestamp = datetime.now(timezone.utc)
today = date.today()

datetime_payload = {
    "timestamp": timestamp.isoformat(),
    "date": today.isoformat(),
}

print(json.dumps(datetime_payload, indent=2))


# ============================================================================
# 62. MEMORY-EFFICIENT JSON LINE PROCESSING
# ============================================================================

section("62. JSON LINES / NDJSON STYLE PROCESSING")

jsonl_file = temporary_root / "events.jsonl"

events = [
    {"id": 1, "event": "login", "user": "alice"},
    {"id": 2, "event": "purchase", "user": "bob"},
    {"id": 3, "event": "logout", "user": "alice"},
]

with open(jsonl_file, "w", encoding="utf-8") as file:
    for event in events:
        file.write(json.dumps(event) + "\n")

# JSON Lines stores one JSON value per line, making streaming practical.
with open(jsonl_file, "r", encoding="utf-8") as file:
    for line in file:
        event = json.loads(line)
        print(event)


# ============================================================================
# 63. STRUCTURED TEXT PARSING
# ============================================================================

section("63. PARSING STRUCTURED INPUT")

def parse_key_value_pairs(text: str) -> dict[str, str]:
    """
    Parse a simple format:
        key=value,key2=value2

    This deliberately handles malformed fields rather than silently accepting
    them.
    """
    result: dict[str, str] = {}

    if not text.strip():
        return result

    for field in text.split(","):
        if "=" not in field:
            raise ValueError(f"Missing '=' in field: {field!r}")

        key, value = field.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            raise ValueError("Keys cannot be empty.")

        result[key] = value

    return result


print(parse_key_value_pairs("name=Alice,role=Analyst,city=Lucknow"))

try:
    parse_key_value_pairs("name=Alice,broken")
except ValueError as error:
    print("Parsing error:", error)


# ============================================================================
# 64. DELIMITERS AND NEWLINE EDGE CASES
# ============================================================================

section("64. INPUT EDGE CASES")

edge_cases = [
    "",
    " ",
    "\n",
    "  hello  ",
    "hello world",
    "10,20,30",
]

for value in edge_cases:
    print(repr(value), "strip ->", repr(value.strip()))

# split() without an argument handles repeated whitespace:
print("Whitespace split:", "  one   two\tthree\n".split())

# split(" ") behaves differently because it treats exactly the literal space
# as the delimiter and can produce empty strings:
print("Literal-space split:", "  one   two ".split(" "))


# ============================================================================
# 65. NEWLINE HANDLING
# ============================================================================

section("65. NEWLINE HANDLING")

newline_file = temporary_root / "newlines.txt"

with open(newline_file, "w", encoding="utf-8", newline="\n") as file:
    file.write("one\n")
    file.write("two\n")

print(repr(newline_file.read_text(encoding="utf-8")))

# rstrip("\n") removes newline characters only.
# rstrip() removes all trailing whitespace, which may accidentally remove
# meaningful spaces or tabs.
line = "hello \n"
print("rstrip newline:", repr(line.rstrip("\n")))
print("rstrip whitespace:", repr(line.rstrip()))


# ============================================================================
# 66. FLUSHING INTERACTIVE OUTPUT
# ============================================================================

section("66. FLUSHING OUTPUT")

# In interactive applications, flush=True can make output visible immediately.
print("Immediate-style output", flush=True)

# Example:
#
# print("Progress: 50%", end="\r", flush=True)
#
# flush=True is useful when output should not wait in a buffer.


# ============================================================================
# 67. PROGRESS OUTPUT
# ============================================================================

section("67. SIMPLE PROGRESS OUTPUT")

for progress in range(0, 101, 25):
    print(f"\rProgress: {progress:3d}%", end="", flush=True)
    time.sleep(0.01)

print()


# ============================================================================
# 68. PERFORMANCE: BUFFERED VS UNBUFFERED PATTERNS
# ============================================================================

section("68. PERFORMANCE CONSIDERATIONS")

# Avoid repeatedly opening and closing a file for every small record.
# Prefer one open operation and multiple writes.

performance_file = temporary_root / "performance.txt"

with open(performance_file, "w", encoding="utf-8") as file:
    for number in range(100):
        file.write(f"{number}\n")

# For large data:
#   - stream records rather than loading everything into memory
#   - use appropriate buffering
#   - choose an efficient serialization format
#   - batch writes where appropriate
#   - avoid unnecessary conversions and copies
#   - use binary mode for binary data
#   - profile before making complicated optimizations


# ============================================================================
# 69. ATOMIC APPEND LIMITATIONS
# ============================================================================

section("69. CONCURRENT I/O CONSIDERATIONS")

concurrent_file = temporary_root / "concurrent.txt"
concurrent_file.write_text("", encoding="utf-8")

# Multiple processes or threads writing the same file introduce coordination
# concerns. A single Python function is not automatically a complete concurrency
# solution.

# Depending on requirements, applications may need:
#   - file locks
#   - process synchronization
#   - a database
#   - an append-only logging system
#   - transactional storage
#
# Atomicity of individual operations and durability of data are separate
# concerns.


# ============================================================================
# 70. FILE PERMISSIONS
# ============================================================================

section("70. FILE PERMISSIONS")

permission_file = temporary_root / "permissions.txt"
permission_file.write_text("Sensitive application data\n", encoding="utf-8")

try:
    current_mode = permission_file.stat().st_mode
    print("Permission bits:", oct(current_mode & 0o777))
except OSError as error:
    print("Could not inspect permissions:", error)

# chmod behavior and permission semantics differ by operating system.
# Applications handling sensitive data should use least-privilege principles
# and avoid assuming that a filename or directory is inherently protected.


# ============================================================================
# 71. SYMLINK CONSIDERATIONS
# ============================================================================

section("71. SYMLINK AND PATH SECURITY")

real_directory = temporary_root / "real"
real_directory.mkdir()

real_file = real_directory / "data.txt"
real_file.write_text("real content", encoding="utf-8")

# is_symlink() distinguishes a symbolic link from an ordinary path.
print("Real file is symlink:", real_file.is_symlink())

# Security-sensitive code may need to account for symlinks because resolving a
# path can lead outside an intended directory.


# ============================================================================
# 72. DIRECTORY INPUT/OUTPUT
# ============================================================================

section("72. DIRECTORY OPERATIONS")

directory = temporary_root / "directory_demo"
directory.mkdir(exist_ok=True)

for filename in ["a.txt", "b.txt", "c.log"]:
    (directory / filename).write_text(filename, encoding="utf-8")

print("iterdir():")
for path in directory.iterdir():
    print(path.name)

print("Only .txt files:")
for path in directory.glob("*.txt"):
    print(path.name)


# ============================================================================
# 73. COPY DIRECTORY
# ============================================================================

section("73. DIRECTORY COPYING")

source_directory = temporary_root / "source_directory"
source_directory.mkdir()

(source_directory / "one.txt").write_text("one", encoding="utf-8")
(source_directory / "two.txt").write_text("two", encoding="utf-8")

destination_directory = temporary_root / "destination_directory"

shutil.copytree(source_directory, destination_directory)

print("Copied directory files:")
for path in destination_directory.iterdir():
    print(path.name)


# ============================================================================
# 74. FILE SIZE LIMITS
# ============================================================================

section("74. CHECKING FILE SIZE")

def ensure_file_size(
    path: Path,
    maximum_bytes: int,
) -> None:
    """Reject files larger than the application's allowed limit."""
    size = path.stat().st_size

    if size > maximum_bytes:
        raise ValueError(
            f"File size {size} exceeds limit {maximum_bytes}."
        )


ensure_file_size(text_file, maximum_bytes=10_000)
print("File size is within the configured limit.")


# ============================================================================
# 75. ENCODING ROUND-TRIP
# ============================================================================

section("75. ENCODING ROUND-TRIP")

original_text = "Python → डेटा → café → résumé"
encoded_text = original_text.encode("utf-8")
decoded_text = encoded_text.decode("utf-8")

print("Original:", original_text)
print("Byte length:", len(encoded_text))
print("Round-trip:", decoded_text == original_text)


# ============================================================================
# 76. DIFFERENCE BETWEEN CHARACTERS AND BYTES
# ============================================================================

section("76. CHARACTERS VS BYTES")

ascii_text = "ABC"
unicode_text = "भारत"

print("ASCII characters:", len(ascii_text))
print("ASCII UTF-8 bytes:", len(ascii_text.encode("utf-8")))

print("Unicode characters:", len(unicode_text))
print("Unicode UTF-8 bytes:", len(unicode_text.encode("utf-8")))

# len(str) counts Unicode code points, while len(bytes) counts bytes.
# A visible character can occupy multiple bytes in UTF-8.


# ============================================================================
# 77. SEEK/TELL IN BINARY MODE
# ============================================================================

section("77. BINARY seek() AND tell()")

with open(binary_file, "rb") as file:
    print("Position:", file.tell())
    print("First byte:", file.read(1))
    print("Position:", file.tell())

    file.seek(5)
    print("Byte at position 5:", file.read(1))

    file.seek(-2, os.SEEK_END)
    print("Last two bytes:", file.read())


# ============================================================================
# 78. RANDOM ACCESS
# ============================================================================

section("78. RANDOM ACCESS")

records_file = temporary_root / "fixed_records.dat"

# Fixed-size records make direct offsets easy to calculate.
records = [b"AAAA", b"BBBB", b"CCCC", b"DDDD"]

with open(records_file, "wb") as file:
    for record in records:
        file.write(record)

record_size = 4
record_index = 2

with open(records_file, "rb") as file:
    file.seek(record_index * record_size)
    record = file.read(record_size)

print("Record at index 2:", record)


# ============================================================================
# 79. SEEKABLE VS NON-SEEKABLE STREAMS
# ============================================================================

section("79. SEEKABLE AND NON-SEEKABLE STREAMS")

with open(text_file, "r", encoding="utf-8") as file:
    print("Regular file seekable:", file.seekable())

print("StringIO seekable:", io.StringIO().seekable())

# Some pipes, sockets, and streams are not seekable.
# Code that requires random access should not assume every stream supports
# seek().


# ============================================================================
# 80. INPUT/OUTPUT ABSTRACTION
# ============================================================================

section("80. SEPARATING INPUT, PROCESSING, AND OUTPUT")

def calculate_average(values: list[float]) -> float:
    if not values:
        raise ValueError("At least one value is required.")
    return sum(values) / len(values)


def process_scores(input_stream: io.TextIOBase, output_stream: io.TextIOBase) -> None:
    """
    Read numeric scores from a text stream and write a result to another.

    Separating streams from business logic makes code easier to test.
    """
    scores: list[float] = []

    for line in input_stream:
        stripped = line.strip()

        if not stripped:
            continue

        try:
            scores.append(float(stripped))
        except ValueError:
            output_stream.write(f"Invalid score: {stripped!r}\n")

    if scores:
        average = calculate_average(scores)
        output_stream.write(f"Average: {average:.2f}\n")
    else:
        output_stream.write("No valid scores.\n")


score_input = io.StringIO("90\n85.5\nbad\n94\n")
score_output = io.StringIO()

process_scores(score_input, score_output)

print(score_output.getvalue(), end="")


# ============================================================================
# 81. DEPENDENCY INJECTION FOR I/O
# ============================================================================

section("81. DEPENDENCY INJECTION FOR TESTABLE I/O")

def write_status(
    output_stream: io.TextIOBase,
    status: str,
) -> None:
    output_stream.write(f"STATUS={status}\n")


status_buffer = io.StringIO()
write_status(status_buffer, "READY")

print("Injected output:")
print(status_buffer.getvalue(), end="")

# The function can write to sys.stdout, a file, or a test buffer without
# changing its internal logic.


# ============================================================================
# 82. CONFIGURATION FILE I/O
# ============================================================================

section("82. CONFIGURATION THROUGH JSON")

config = {
    "host": "127.0.0.1",
    "port": 8000,
    "debug": False,
}

config_file = temporary_root / "config.json"
atomic_write_text(
    config_file,
    json.dumps(config, indent=2),
)

loaded_config = json.loads(config_file.read_text(encoding="utf-8"))

print("Loaded host:", loaded_config["host"])
print("Loaded port:", loaded_config["port"])


# ============================================================================
# 83. DATA VALIDATION AFTER DESERIALIZATION
# ============================================================================

section("83. VALIDATE DATA AFTER DESERIALIZATION")

def validate_config(config_data: dict[str, Any]) -> dict[str, Any]:
    required_keys = {"host", "port", "debug"}

    missing = required_keys - config_data.keys()
    if missing:
        raise ValueError(f"Missing configuration keys: {sorted(missing)}")

    if not isinstance(config_data["host"], str):
        raise ValueError("host must be a string.")

    if not isinstance(config_data["port"], int):
        raise ValueError("port must be an integer.")

    if not 1 <= config_data["port"] <= 65535:
        raise ValueError("port must be between 1 and 65535.")

    if not isinstance(config_data["debug"], bool):
        raise ValueError("debug must be boolean.")

    return config_data


print("Validated configuration:", validate_config(loaded_config))


# ============================================================================
# 84. OUTPUT FORMATTING TABLE
# ============================================================================

section("84. FORMATTED TABULAR OUTPUT")

records = [
    ("Alice", 95, "A"),
    ("Bob", 87, "B"),
    ("Charlie", 91, "A"),
]

print(f"{'Name':<12}{'Score':>8}{'Grade':>8}")
print("-" * 28)

for student_name, student_score, grade in records:
    print(f"{student_name:<12}{student_score:>8}{grade:>8}")


# ============================================================================
# 85. pprint FOR COMPLEX OUTPUT
# ============================================================================

section("85. pprint FOR READABLE DEBUG OUTPUT")

complex_data = {
    "employees": employees,
    "settings": config,
    "metadata": {
        "created": "2026-09-09",
        "tags": ["python", "io", "tutorial"],
    },
}

pprint(complex_data, sort_dicts=False)


# ============================================================================
# 86. OUTPUT AS JSON FOR MACHINES
# ============================================================================

section("86. HUMAN-READABLE VS MACHINE-READABLE OUTPUT")

human_output = f"Employee {employee.name} earns {employee.salary:.2f}."
machine_output = json.dumps(employee_dictionary)

print("Human output:", human_output)
print("Machine output:", machine_output)

# Human-readable output prioritizes clarity.
# Machine-readable output prioritizes predictable structure and parsing.


# ============================================================================
# 87. NULL BYTE AND SPECIAL DATA
# ============================================================================

section("87. SPECIAL CHARACTERS IN TEXT")

special_file = temporary_root / "special.txt"
special_content = "A\0B\tC\nD"

special_file.write_text(special_content, encoding="utf-8")

loaded_special = special_file.read_text(encoding="utf-8")
print("Representation:", repr(loaded_special))
print("Contains null byte:", "\0" in loaded_special)


# ============================================================================
# 88. EOF CONCEPT
# ============================================================================

section("88. END OF FILE")

with open(multi_line_file, "r", encoding="utf-8") as file:
    while True:
        line = file.readline()

        if line == "":
            # Empty string from readline() indicates EOF.
            break

        print("Record:", line.rstrip())

# Important distinction:
# An empty line is "\n".
# End-of-file from readline() is "".


# ============================================================================
# 89. PARTIAL READS
# ============================================================================

section("89. PARTIAL READS")

partial_file = temporary_root / "partial.txt"
partial_file.write_text("ABCDEFGHIJ", encoding="utf-8")

with open(partial_file, "r", encoding="utf-8") as file:
    while chunk := file.read(3):
        print("Chunk:", chunk)


# ============================================================================
# 90. I/O AND DATA INTEGRITY
# ============================================================================

section("90. DATA INTEGRITY CHECK")

integrity_file = temporary_root / "integrity.txt"
integrity_file.write_text("Important content\n", encoding="utf-8")

first_hash = sha256_file(integrity_file)

# Reading the same data should produce the same digest.
second_hash = sha256_file(integrity_file)

print("Hashes equal:", first_hash == second_hash)
print("Digest:", first_hash)


# ============================================================================
# 91. HANDLING MALFORMED JSON
# ============================================================================

section("91. MALFORMED JSON")

malformed_json = '{"name": "Alice", "age": }'

try:
    json.loads(malformed_json)
except json.JSONDecodeError as error:
    print("JSON error:", error)


# ============================================================================
# 92. HANDLING MALFORMED CSV DATA
# ============================================================================

section("92. CSV VALIDATION")

def read_employee_csv(path: Path) -> list[dict[str, Any]]:
    """Read and validate required CSV fields."""
    required = {"id", "name", "department", "salary"}
    result: list[dict[str, Any]] = []

    with open(path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV has no header.")

        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing columns: {sorted(missing)}")

        for row_number, row in enumerate(reader, start=2):
            try:
                row["id"] = int(row["id"])
                row["salary"] = float(row["salary"])
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Invalid numeric value on CSV row {row_number}."
                ) from error

            result.append(row)

    return result


validated_employees = read_employee_csv(csv_file)
pprint(validated_employees)


# ============================================================================
# 93. BUFFER PROTOCOL BASICS
# ============================================================================

section("93. STREAM PROTOCOL BASICS")

# Many I/O APIs work through a file-like protocol rather than requiring a
# specific concrete class.
#
# Text streams generally expose methods such as:
#   read(), readline(), write(), seek(), tell(), flush(), close()
#
# Binary streams similarly expose byte-oriented operations.

protocol_buffer = io.StringIO()
print("Protocol-compatible output", file=protocol_buffer)
print("Works with print():", protocol_buffer.getvalue().strip())


# ============================================================================
# 94. CUSTOM CONTEXT MANAGER
# ============================================================================

section("94. CUSTOM CONTEXT MANAGER")

class ManagedTextFile:
    """A small example of manually implementing context-manager behavior."""

    def __init__(self, path: Path, mode: str = "r") -> None:
        self.path = path
        self.mode = mode
        self.file = None

    def __enter__(self):
        self.file = open(self.path, self.mode, encoding="utf-8")
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file is not None:
            self.file.close()

        # Returning False means exceptions are not suppressed.
        return False


with ManagedTextFile(text_file, "r") as file:
    print("Managed file:", file.readline().rstrip())


# ============================================================================
# 95. DATETIME OUTPUT
# ============================================================================

section("95. MACHINE-FRIENDLY TIME OUTPUT")

timestamp_file = temporary_root / "timestamp.txt"
current_timestamp = datetime.now(timezone.utc).isoformat()

timestamp_file.write_text(current_timestamp, encoding="utf-8")

print("UTC timestamp:", timestamp_file.read_text(encoding="utf-8"))


# ============================================================================
# 96. SERIALIZATION TRADE-OFFS
# ============================================================================

section("96. SERIALIZATION TRADE-OFFS")

serialization_examples = {
    "JSON": {
        "strengths": [
            "human-readable",
            "widely supported",
            "cross-language",
        ],
        "limitations": [
            "limited native type system",
            "larger than many binary formats",
        ],
    },
    "CSV": {
        "strengths": [
            "simple tabular interchange",
            "widely supported by spreadsheet tools",
        ],
        "limitations": [
            "weak type information",
            "poor representation of nested structures",
        ],
    },
    "pickle": {
        "strengths": [
            "supports many Python objects",
            "convenient for Python-specific persistence",
        ],
        "limitations": [
            "Python-specific",
            "unsafe with untrusted input",
        ],
    },
}

pprint(serialization_examples, sort_dicts=False)


# ============================================================================
# 97. ERROR TAXONOMY
# ============================================================================

section("97. COMMON I/O EXCEPTIONS")

common_exceptions = {
    "FileNotFoundError": "Requested file or directory does not exist.",
    "PermissionError": "Operation is not permitted by the operating system.",
    "IsADirectoryError": "A file operation was attempted on a directory.",
    "NotADirectoryError": "A directory operation encountered a non-directory.",
    "FileExistsError": "Exclusive creation found an existing path.",
    "UnicodeDecodeError": "Bytes could not be decoded using the chosen encoding.",
    "UnicodeEncodeError": "Text could not be encoded using the chosen encoding.",
    "json.JSONDecodeError": "JSON input is malformed.",
    "csv.Error": "CSV parsing encountered an error.",
    "OSError": "General operating-system I/O error.",
}

for exception_name, description in common_exceptions.items():
    print(f"{exception_name}: {description}")


# ============================================================================
# 98. PRODUCTION-STYLE FILE PROCESSOR
# ============================================================================

section("98. PRODUCTION-STYLE STREAMING PROCESSOR")

def transform_text_file(
    source: Path,
    destination: Path,
) -> int:
    """
    Stream a text file, normalize whitespace, and write transformed lines.

    Returns the number of processed records.
    """
    processed = 0

    destination.parent.mkdir(parents=True, exist_ok=True)

    with (
        open(source, "r", encoding="utf-8") as source_file,
        open(destination, "w", encoding="utf-8") as destination_file,
    ):
        for line in source_file:
            normalized = " ".join(line.split())

            if normalized:
                destination_file.write(normalized + "\n")

            processed += 1

    return processed


source_data = temporary_root / "raw.txt"
clean_data = temporary_root / "clean.txt"

source_data.write_text(
    "  Python   input output  \n"
    "\n"
    "  file handling   \n"
    "JSON and CSV\n",
    encoding="utf-8",
)

processed_records = transform_text_file(source_data, clean_data)

print("Processed records:", processed_records)
print(clean_data.read_text(encoding="utf-8"), end="")


# ============================================================================
# 99. PRODUCTION-STYLE JSON STORE
# ============================================================================

section("99. PRODUCTION-STYLE JSON STORAGE")

class JsonFileStore:
    """
    Small JSON file abstraction.

    The class demonstrates separation between serialization and application
    code, validation of paths, and atomic writes.
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def save(self, data: Any) -> None:
        serialized = json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        atomic_write_text(self.path, serialized)

    def load(self) -> Any:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            raise
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid JSON in {self.path}"
            ) from error


store_file = temporary_root / "store.json"
store = JsonFileStore(store_file)

store.save({"users": [{"id": 1, "name": "Asha"}]})
print("Stored data:")
pprint(store.load())


# ============================================================================
# 100. I/O BEST-PRACTICES CHECKLIST
# ============================================================================

section("100. I/O BEST-PRACTICES CHECKLIST")

best_practices = [
    "Use input() for simple interactive line input.",
    "Remember that input() returns str.",
    "Validate and convert external input explicitly.",
    "Use pathlib for filesystem paths.",
    "Use with when working with files.",
    "Specify UTF-8 when the intended text encoding is known.",
    "Use binary mode for binary data.",
    "Stream large files instead of loading them entirely.",
    "Use JSON for structured, cross-language data when appropriate.",
    "Use csv for tabular data exchange.",
    "Never unpickle untrusted data.",
    "Do not trust filenames or file extensions as security boundaries.",
    "Validate file sizes and input lengths.",
    "Protect against path traversal when filenames are untrusted.",
    "Avoid shell=True with untrusted subprocess input.",
    "Use logging for application diagnostics.",
    "Test I/O using StringIO, BytesIO, and mocked input where practical.",
    "Consider atomic replacement for important file updates.",
    "Distinguish flushing from durable persistence.",
    "Account for concurrency when multiple actors access the same file.",
]

for number, practice in enumerate(best_practices, start=1):
    print(f"{number:02d}. {practice}")


# ============================================================================
# 101. INTEGRATED MINI APPLICATION
# ============================================================================

section("101. INTEGRATED MINI APPLICATION")

def calculate_grade(score: float) -> str:
    if not 0 <= score <= 100:
        raise ValueError("Score must be between 0 and 100.")

    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def process_student_records(
    input_stream: io.TextIOBase,
    output_stream: io.TextIOBase,
) -> None:
    """
    Read CSV-like student records:

        name,score

    Validate each record and produce formatted output.
    """
    reader = csv.DictReader(input_stream)

    if reader.fieldnames != ["name", "score"]:
        raise ValueError("Expected CSV columns: name,score")

    output_stream.write(
        f"{'Name':<15}{'Score':>8}{'Grade':>8}\n"
    )
    output_stream.write("-" * 31 + "\n")

    for row_number, row in enumerate(reader, start=2):
        name = (row.get("name") or "").strip()

        if not name:
            output_stream.write(
                f"Row {row_number}: invalid empty name\n"
            )
            continue

        try:
            score = float(row["score"])
            grade = calculate_grade(score)
        except (TypeError, ValueError) as error:
            output_stream.write(
                f"Row {row_number}: invalid score ({error})\n"
            )
            continue

        output_stream.write(
            f"{name:<15}{score:>8.2f}{grade:>8}\n"
        )


student_input = io.StringIO(
    "name,score\n"
    "Alice,95\n"
    "Bob,81.5\n"
    "Charlie,invalid\n"
    ",88\n"
    "Diana,72\n"
)

student_output = io.StringIO()

process_student_records(student_input, student_output)

print(student_output.getvalue(), end="")


# ============================================================================
# 102. CLEANUP
# ============================================================================

section("102. CLEANUP")

# The tutorial created a temporary directory rather than modifying arbitrary
# user files. Removing it at the end demonstrates controlled cleanup.
shutil.rmtree(temporary_root, ignore_errors=True)

print("Temporary tutorial data removed.")
print("\nInput and Output tutorial completed successfully.")
