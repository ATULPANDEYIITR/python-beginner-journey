"""
LIST INDEXING AND SLICING
=========================

A comprehensive executable study program covering list indexing and slicing
from absolute beginner concepts through advanced Python techniques.

The examples are intentionally executable. Run this file with Python 3.10+
or a newer Python version.

Topics covered:
- Lists and sequence concepts
- Zero-based indexing
- Positive and negative indexes
- Index validation
- Reading, replacing, inserting, and deleting elements
- Nested-list indexing
- Slice syntax
- Positive and negative slicing
- Slice boundaries
- Slice steps
- Reverse slicing
- Slice assignment
- Slice deletion
- Extended slice assignment
- Copying and aliasing
- Shallow versus nested structures
- Built-in sequence behavior
- Strings, tuples, ranges, and list slicing
- Iterables versus sequences
- Performance and memory considerations
- Common errors and edge cases
- Practical data-processing examples
- Advanced patterns and helper functions
- Testing and validation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence


# ---------------------------------------------------------------------------
# SECTION 1: BASIC LIST CONCEPTS
# ---------------------------------------------------------------------------

def section(title: str) -> None:
    """Print a clear section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def show(label: str, value: Any) -> None:
    """Display a labeled value."""
    print(f"{label}: {value!r}")


section("1. Creating a List")

numbers = [10, 20, 30, 40, 50]
names = ["Asha", "Ravi", "Meera", "Kiran"]
mixed = [42, "Python", 3.14, True, None]

show("numbers", numbers)
show("names", names)
show("mixed", mixed)

# A list is an ordered, mutable sequence.
# "Ordered" means elements have positions.
# "Mutable" means elements can be changed after creation.

print("Length of numbers:", len(numbers))
print("Length of names:", len(names))


# ---------------------------------------------------------------------------
# SECTION 2: POSITIVE INDEXING
# ---------------------------------------------------------------------------

section("2. Positive Indexing")

numbers = [10, 20, 30, 40, 50]

# Python uses zero-based indexing:
# first element  -> index 0
# second element -> index 1
# third element  -> index 2
# ...
#
# The index is not the same thing as the human-oriented position.

for index in range(len(numbers)):
    print(f"index {index} -> value {numbers[index]}")

print("First element:", numbers[0])
print("Second element:", numbers[1])
print("Last element:", numbers[4])


# ---------------------------------------------------------------------------
# SECTION 3: NEGATIVE INDEXING
# ---------------------------------------------------------------------------

section("3. Negative Indexing")

# Negative indexes count from the end:
# -1 -> last element
# -2 -> second-last element
# -3 -> third-last element

for index in range(-1, -len(numbers) - 1, -1):
    print(f"index {index} -> value {numbers[index]}")

print("Last:", numbers[-1])
print("Second-last:", numbers[-2])
print("First using negative indexing:", numbers[-len(numbers)])


# ---------------------------------------------------------------------------
# SECTION 4: INDEX MATHEMATICS
# ---------------------------------------------------------------------------

section("4. Understanding Index Positions")

items = ["A", "B", "C", "D", "E"]

print("List:", items)
print("Positive indexes:  0   1   2   3   4")
print("Values:             A   B   C   D   E")
print("Negative indexes:  -5  -4  -3  -2  -1")

for index, value in enumerate(items):
    negative_index = index - len(items)
    print(
        f"value={value!r}, positive_index={index}, "
        f"equivalent_negative_index={negative_index}"
    )


# ---------------------------------------------------------------------------
# SECTION 5: INDEX ERRORS
# ---------------------------------------------------------------------------

section("5. Handling Invalid Indexes")

try:
    print(numbers[100])
except IndexError as error:
    print("IndexError caught:", error)

try:
    print(numbers[-100])
except IndexError as error:
    print("Negative IndexError caught:", error)

# An index must identify exactly one existing element.
# Unlike slicing, ordinary indexing does not silently clamp out-of-range
# positions.


# ---------------------------------------------------------------------------
# SECTION 6: CHANGING ELEMENTS
# ---------------------------------------------------------------------------

section("6. Updating Elements Through Indexing")

scores = [70, 82, 91, 64, 88]
print("Before:", scores)

scores[0] = 75
scores[-1] = 95

print("After:", scores)

# Indexing returns one element.
# Assignment through an index replaces that element.


# ---------------------------------------------------------------------------
# SECTION 7: INSERTING AND DELETING USING POSITIONS
# ---------------------------------------------------------------------------

section("7. Insertion and Deletion")

items = ["A", "B", "D", "E"]

items.insert(2, "C")
print("After insert:", items)

del items[1]
print("After del items[1]:", items)

removed = items.pop(1)
print("Popped value:", removed)
print("After pop:", items)

# remove(value) searches for a matching value, while del/pop operate
# directly with a position.

items = ["A", "B", "C", "B"]
items.remove("B")
print("After remove('B'):", items)


# ---------------------------------------------------------------------------
# SECTION 8: SLICING BASICS
# ---------------------------------------------------------------------------

section("8. Basic Slicing")

numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Basic slice syntax:
#
# sequence[start:stop]
#
# start is included.
# stop is excluded.

show("numbers", numbers)
show("numbers[2:6]", numbers[2:6])
show("numbers[0:4]", numbers[0:4])
show("numbers[5:9]", numbers[5:9])

# Therefore:
# [2:6] -> indexes 2, 3, 4, 5


# ---------------------------------------------------------------------------
# SECTION 9: OMITTING START OR STOP
# ---------------------------------------------------------------------------

section("9. Omitting Slice Boundaries")

show("numbers[:5]", numbers[:5])
show("numbers[5:]", numbers[5:])
show("numbers[:]", numbers[:])

# [:5] means from the beginning through index 4.
# [5:] means from index 5 through the end.
# [:] means the complete list.


# ---------------------------------------------------------------------------
# SECTION 10: NEGATIVE SLICE BOUNDARIES
# ---------------------------------------------------------------------------

section("10. Negative Slice Boundaries")

show("numbers[-5:]", numbers[-5:])
show("numbers[:-2]", numbers[:-2])
show("numbers[-7:-2]", numbers[-7:-2])
show("numbers[-4:-1]", numbers[-4:-1])

# Negative boundaries are converted conceptually relative to the end.
# The stop boundary remains exclusive.


# ---------------------------------------------------------------------------
# SECTION 11: SLICE STEP
# ---------------------------------------------------------------------------

section("11. Slice Steps")

numbers = list(range(20))

show("numbers", numbers)
show("numbers[::2]", numbers[::2])
show("numbers[1::2]", numbers[1::2])
show("numbers[::3]", numbers[::3])
show("numbers[2:15:4]", numbers[2:15:4])

# Syntax:
#
# sequence[start:stop:step]
#
# A positive step moves forward.
# A negative step moves backward.
# A step of zero is invalid.


# ---------------------------------------------------------------------------
# SECTION 12: REVERSE SLICING
# ---------------------------------------------------------------------------

section("12. Reversing a List")

numbers = list(range(10))

print("Original:", numbers)
print("Reversed with [::-1]:", numbers[::-1])
print("Reverse from index 7 down to index 2:", numbers[7:1:-1])

# [::-1] is a common idiom for creating a reversed copy.


# ---------------------------------------------------------------------------
# SECTION 13: NEGATIVE STEP DETAILS
# ---------------------------------------------------------------------------

section("13. Negative Steps")

letters = list("ABCDEFGHIJ")

show("letters", letters)
show("letters[8:2:-1]", letters[8:2:-1])
show("letters[9:4:-2]", letters[9:4:-2])
show("letters[:3:-1]", letters[:3:-1])
show("letters[7::-1]", letters[7::-1])

try:
    print(letters[::0])
except ValueError as error:
    print("Zero-step error:", error)


# ---------------------------------------------------------------------------
# SECTION 14: SLICE OBJECTS
# ---------------------------------------------------------------------------

section("14. Explicit slice Objects")

numbers = list(range(20))

first_part = slice(2, 10)
every_third = slice(1, 18, 3)
reverse_part = slice(15, 4, -2)

print("Using slice(2, 10):", numbers[first_part])
print("Using slice(1, 18, 3):", numbers[every_third])
print("Using slice(15, 4, -2):", numbers[reverse_part])

# slice objects are useful when a slicing rule must be stored in a
# variable, passed into a function, or reused.


# ---------------------------------------------------------------------------
# SECTION 15: SLICE INDICES
# ---------------------------------------------------------------------------

section("15. Normalizing Slice Boundaries")

rules = [
    slice(None, None, None),
    slice(-100, 100, 1),
    slice(-5, None, 1),
    slice(None, None, -1),
]

for rule in rules:
    print(rule, "->", rule.indices(10))


# ---------------------------------------------------------------------------
# SECTION 16: SLICE ASSIGNMENT
# ---------------------------------------------------------------------------

section("16. Replacing a Portion of a List")

numbers = [0, 1, 2, 3, 4, 5]
print("Before:", numbers)

numbers[2:5] = [20, 30, 40]
print("Same-size replacement:", numbers)

numbers[1:3] = [100, 200, 300, 400]
print("Longer replacement:", numbers)

numbers[1:5] = ["X"]
print("Shorter replacement:", numbers)

# Slice assignment can change the length of the list.
# This is different from assigning through one ordinary index.


# ---------------------------------------------------------------------------
# SECTION 17: INSERTING WITH EMPTY SLICE
# ---------------------------------------------------------------------------

section("17. Insertion Through Slice Assignment")

items = ["A", "D"]

items[1:1] = ["B", "C"]
print("Inserted values:", items)

items[:0] = ["START"]
print("Inserted at beginning:", items)

items[len(items):] = ["END"]
print("Inserted at end:", items)


# ---------------------------------------------------------------------------
# SECTION 18: DELETING WITH SLICE ASSIGNMENT
# ---------------------------------------------------------------------------

section("18. Deleting Through Slice Assignment")

items = list("ABCDEFG")

items[2:5] = []
print("After deleting C-E:", items)

items[:] = []
print("After clearing the list:", items)

# del can also delete slices.

items = list("ABCDEFG")
del items[1:4]
print("After del items[1:4]:", items)


# ---------------------------------------------------------------------------
# SECTION 19: EXTENDED SLICE ASSIGNMENT
# ---------------------------------------------------------------------------

section("19. Extended Slice Assignment")

numbers = [0, 1, 2, 3, 4, 5, 6, 7]

numbers[::2] = [100, 200, 300, 400]
print("After replacing even positions:", numbers)

# With a non-unit step, the replacement iterable must have exactly the
# same number of elements as the selected positions.

try:
    numbers[::2] = [1, 2]
except ValueError as error:
    print("Extended slice assignment error:", error)


# ---------------------------------------------------------------------------
# SECTION 20: NESTED LIST INDEXING
# ---------------------------------------------------------------------------

section("20. Nested Lists")

matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

print("matrix:", matrix)
print("First row:", matrix[0])
print("Middle element:", matrix[1][1])
print("Bottom-right:", matrix[-1][-1])

matrix[1][1] = 50
print("After changing center:", matrix)


# ---------------------------------------------------------------------------
# SECTION 21: NESTED LIST SLICING
# ---------------------------------------------------------------------------

section("21. Nested List Slicing")

matrix = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
]

print("First two rows:", matrix[:2])
print("Last two rows:", matrix[-2:])
print("Columns 2 and 3 from each row:", [row[1:3] for row in matrix])


# ---------------------------------------------------------------------------
# SECTION 22: IMPORTANT DIFFERENCE BETWEEN LIST SLICING AND NUMPY-STYLE
# ---------------------------------------------------------------------------

section("22. Python Lists and Multi-Dimensional Indexing")

matrix = [[1, 2], [3, 4]]

# Python's built-in list does not support matrix[rows, columns].
try:
    print(matrix[0, 1])
except TypeError as error:
    print("Built-in list indexing limitation:", error)

# Instead, ordinary nested lists use matrix[row][column].
print("Correct nested-list access:", matrix[0][1])


# ---------------------------------------------------------------------------
# SECTION 23: LIST SLICES CREATE NEW LISTS
# ---------------------------------------------------------------------------

section("23. Slice Results Are New Lists")

original = [1, 2, 3, 4, 5]
copied = original[:]

copied[0] = 999

print("Original:", original)
print("Copied:", copied)
print("Different objects:", original is not copied)

# For a normal list, slicing creates a new outer list.


# ---------------------------------------------------------------------------
# SECTION 24: ALIASING
# ---------------------------------------------------------------------------

section("24. Aliasing Versus Copying")

original = [10, 20, 30]
alias = original
copy_using_slice = original[:]

alias[0] = 999

print("Original after alias modification:", original)
print("Alias:", alias)
print("Slice copy:", copy_using_slice)

print("original is alias:", original is alias)
print("original is copy:", original is copy_using_slice)


# ---------------------------------------------------------------------------
# SECTION 25: SHALLOW COPY WITH NESTED LISTS
# ---------------------------------------------------------------------------

section("25. Shallow Copy and Nested Lists")

original = [[1, 2], [3, 4]]
shallow = original[:]

shallow[0][0] = 999

print("Original:", original)
print("Shallow copy:", shallow)

# The outer list was copied, but its nested lists were not.
print("Outer objects differ:", original is not shallow)
print("Nested object shared:", original[0] is shallow[0])


# ---------------------------------------------------------------------------
# SECTION 26: DEEP COPY
# ---------------------------------------------------------------------------

section("26. Deep Copy")

from copy import deepcopy

original = [[1, 2], [3, 4]]
deep = deepcopy(original)

deep[0][0] = 999

print("Original:", original)
print("Deep copy:", deep)
print("Nested object shared:", original[0] is deep[0])


# ---------------------------------------------------------------------------
# SECTION 27: SAFE INDEXING HELPERS
# ---------------------------------------------------------------------------

section("27. Safe Indexing")

def safe_get(sequence: Sequence[Any], index: int, default: Any = None) -> Any:
    """
    Return an element if the index is valid; otherwise return default.

    This function deliberately supports negative indexes because Python's
    sequence indexing rules define them as valid positions.
    """
    try:
        return sequence[index]
    except IndexError:
        return default
    except TypeError:
        return default


values = ["red", "green", "blue"]

print("Index 1:", safe_get(values, 1))
print("Index -1:", safe_get(values, -1))
print("Index 99:", safe_get(values, 99, "missing"))
print("Invalid index type:", safe_get(values, "1", "invalid"))


# ---------------------------------------------------------------------------
# SECTION 28: SAFE SLICING
# ---------------------------------------------------------------------------

section("28. A Reusable Slice Helper")

def take_slice(
    sequence: Sequence[Any],
    start: int | None = None,
    stop: int | None = None,
    step: int | None = None,
) -> list[Any]:
    """
    Return a list containing the requested slice.

    Converting the result to list makes the return type predictable for
    general Sequence implementations.
    """
    return list(sequence[slice(start, stop, step)])


values = list(range(10))

print("Middle:", take_slice(values, 2, 7))
print("Every second:", take_slice(values, None, None, 2))
print("Reverse:", take_slice(values, None, None, -1))


# ---------------------------------------------------------------------------
# SECTION 29: VALIDATING A USER-SUPPLIED INDEX
# ---------------------------------------------------------------------------

section("29. Input Validation")

def read_index(text: str, length: int) -> int:
    """
    Parse an integer index and validate it against Python's valid
    negative/positive index range.
    """
    try:
        index = int(text)
    except ValueError as error:
        raise ValueError("Index must be an integer.") from error

    if not -length <= index < length:
        raise IndexError(
            f"Index {index} is outside the valid range "
            f"{-length} through {length - 1}."
        )

    return index


for text in ["2", "-1", "100", "hello"]:
    try:
        print(text, "->", read_index(text, 5))
    except (ValueError, IndexError) as error:
        print(text, "->", error)


# ---------------------------------------------------------------------------
# SECTION 30: PRACTICAL DATA PROCESSING
# ---------------------------------------------------------------------------

section("30. Processing Recent Records")

temperatures = [31.2, 32.1, 30.8, 33.4, 34.0, 35.2, 33.8]

print("All temperatures:", temperatures)
print("Last three:", temperatures[-3:])
print("First three:", temperatures[:3])
print("Alternating samples:", temperatures[::2])
print("Reverse order:", temperatures[::-1])

recent = temperatures[-5:]
average_recent = sum(recent) / len(recent)

print("Recent five:", recent)
print("Average of recent five:", round(average_recent, 2))


# ---------------------------------------------------------------------------
# SECTION 31: PAGINATION
# ---------------------------------------------------------------------------

section("31. Pagination Using Slices")

records = [f"record-{number:02d}" for number in range(1, 26)]
page_size = 5

for page_number in range(1, 7):
    start = (page_number - 1) * page_size
    stop = start + page_size
    page = records[start:stop]
    print(f"Page {page_number}: {page}")


# ---------------------------------------------------------------------------
# SECTION 32: CHUNKING
# ---------------------------------------------------------------------------

section("32. Chunking a List")

def chunks(sequence: Sequence[Any], size: int) -> list[list[Any]]:
    """Split a sequence into consecutive chunks."""
    if size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    return [
        list(sequence[start:start + size])
        for start in range(0, len(sequence), size)
    ]


values = list(range(1, 14))
print("Chunks of four:", chunks(values, 4))

try:
    print(chunks(values, 0))
except ValueError as error:
    print("Chunking error:", error)


# ---------------------------------------------------------------------------
# SECTION 33: WINDOWING
# ---------------------------------------------------------------------------

section("33. Sliding Windows")

def sliding_windows(sequence: Sequence[Any], width: int) -> list[list[Any]]:
    """Return overlapping windows of a fixed width."""
    if width <= 0:
        raise ValueError("Window width must be positive.")
    if width > len(sequence):
        return []

    return [
        list(sequence[start:start + width])
        for start in range(len(sequence) - width + 1)
    ]


values = [10, 20, 30, 40, 50]
print("Width-3 windows:", sliding_windows(values, 3))
print("Width-1 windows:", sliding_windows(values, 1))
print("Too-wide windows:", sliding_windows(values, 10))


# ---------------------------------------------------------------------------
# SECTION 34: BATCHING AND PARTIAL FINAL BATCH
# ---------------------------------------------------------------------------

section("34. Batching")

transactions = [
    "T001", "T002", "T003", "T004", "T005",
    "T006", "T007", "T008", "T009",
]

for batch_number, batch in enumerate(chunks(transactions, 3), start=1):
    print(f"Batch {batch_number}: {batch}")


# ---------------------------------------------------------------------------
# SECTION 35: STRINGS ARE ALSO SEQUENCES
# ---------------------------------------------------------------------------

section("35. String Indexing and Slicing")

text = "PYTHON"

print("First character:", text[0])
print("Last character:", text[-1])
print("Middle:", text[1:5])
print("Reverse:", text[::-1])
print("Every second character:", text[::2])

# Strings support indexing and slicing, but strings are immutable.
try:
    text[0] = "J"
except TypeError as error:
    print("String mutation error:", error)


# ---------------------------------------------------------------------------
# SECTION 36: TUPLES
# ---------------------------------------------------------------------------

section("36. Tuple Indexing and Slicing")

point = (10, 20, 30, 40)

print("First:", point[0])
print("Last:", point[-1])
print("Middle:", point[1:3])

# A tuple is immutable, but it supports sequence indexing and slicing.


# ---------------------------------------------------------------------------
# SECTION 37: RANGE
# ---------------------------------------------------------------------------

section("37. Range Indexing and Slicing")

sequence = range(0, 20, 2)

print("range object:", sequence)
print("Index 3:", sequence[3])
print("Last:", sequence[-1])
print("Slice:", sequence[2:7])
print("Reversed range slice:", sequence[::-1])

# range slicing returns another range object rather than a list.


# ---------------------------------------------------------------------------
# SECTION 38: LIST COMPREHENSION WITH SLICES
# ---------------------------------------------------------------------------

section("38. Slices Combined with List Comprehensions")

numbers = list(range(1, 21))

even_position_values = [value * 10 for value in numbers[::2]]
middle_squared = [value ** 2 for value in numbers[5:15]]

print("Values at even positions multiplied by ten:", even_position_values)
print("Squared middle section:", middle_squared)


# ---------------------------------------------------------------------------
# SECTION 39: FILTERING AFTER SLICING
# ---------------------------------------------------------------------------

section("39. Filtering a Selected Region")

scores = [45, 72, 81, 39, 90, 66, 54, 88]

selected = scores[2:7]
passing = [score for score in selected if score >= 60]

print("Selected region:", selected)
print("Passing scores:", passing)


# ---------------------------------------------------------------------------
# SECTION 40: SORTING AND SLICING
# ---------------------------------------------------------------------------

section("40. Top-N Pattern")

scores = [72, 91, 88, 64, 97, 83, 79, 95]

top_scores = sorted(scores, reverse=True)[:3]

print("Original scores:", scores)
print("Top three:", top_scores)

# sorted() creates a new list. The original list remains unchanged.


# ---------------------------------------------------------------------------
# SECTION 41: COPY BEFORE SORTING
# ---------------------------------------------------------------------------

section("41. Preserving Original Order")

scores = [72, 91, 88, 64]

ordered = scores[:]
ordered.sort()

print("Original:", scores)
print("Sorted copy:", ordered)


# ---------------------------------------------------------------------------
# SECTION 42: EDGE CASES
# ---------------------------------------------------------------------------

section("42. Slice Edge Cases")

values = [1, 2, 3, 4, 5]

edge_cases = {
    "too-large-start": values[100:],
    "too-large-stop": values[:100],
    "negative-too-small-start": values[-100:],
    "negative-too-small-stop": values[:-100],
    "empty-forward": values[4:2],
    "empty-forward-step": values[4:2:1],
    "empty-reverse": values[1:4:-1],
    "full-copy": values[:],
}

for name, result in edge_cases.items():
    print(f"{name}: {result}")


# ---------------------------------------------------------------------------
# SECTION 43: INDEXING VERSUS SLICING
# ---------------------------------------------------------------------------

section("43. Indexing Versus Slicing")

values = [10, 20, 30, 40, 50]

print("Indexing values[2]:", values[2], type(values[2]))
print("Slicing values[2:3]:", values[2:3], type(values[2:3]))

# Indexing returns one element.
# Slicing returns a sequence of the same general sequence family.


# ---------------------------------------------------------------------------
# SECTION 44: EMPTY SLICES
# ---------------------------------------------------------------------------

section("44. Empty Slices")

values = [1, 2, 3]

empty_one = values[2:2]
empty_two = values[5:2]
empty_three = values[-1:-1]

print(empty_one)
print(empty_two)
print(empty_three)

print("All are empty:", empty_one == empty_two == empty_three == [])


# ---------------------------------------------------------------------------
# SECTION 45: SLICE ASSIGNMENT AS A STRUCTURAL OPERATION
# ---------------------------------------------------------------------------

section("45. Structural List Editing")

letters = list("ABCDEFG")

letters[2:2] = ["X", "Y"]
print("Insertion:", letters)

letters[1:4] = ["M"]
print("Replacement:", letters)

letters[-2:] = []
print("Deletion:", letters)


# ---------------------------------------------------------------------------
# SECTION 46: REPLACING EVERY OTHER ELEMENT
# ---------------------------------------------------------------------------

section("46. Extended Slice Replacement")

values = list(range(10))
replacement = [100, 101, 102, 103, 104]

values[::2] = replacement

print("Replaced positions 0,2,4,6,8:", values)


# ---------------------------------------------------------------------------
# SECTION 47: REVERSE EXTENDED SLICE ASSIGNMENT
# ---------------------------------------------------------------------------

section("47. Reverse Extended Slice Assignment")

values = list("ABCDEFGH")
values[7:1:-2] = ["X", "Y", "Z"]

print("After reverse-step replacement:", values)


# ---------------------------------------------------------------------------
# SECTION 48: ASSIGNMENT TYPE REQUIREMENTS
# ---------------------------------------------------------------------------

section("48. Slice Assignment Requires an Iterable")

values = [1, 2, 3, 4]

try:
    values[1:3] = 99
except TypeError as error:
    print("Slice assignment type error:", error)

# A slice assignment requires an iterable on the right-hand side.


# ---------------------------------------------------------------------------
# SECTION 49: SLICE ASSIGNMENT WITH GENERATORS
# ---------------------------------------------------------------------------

section("49. Slice Assignment from an Iterable")

values = [1, 2, 3, 4, 5]
values[1:3] = (number * 10 for number in range(2))

print("After generator-based assignment:", values)


# ---------------------------------------------------------------------------
# SECTION 50: SEQUENCE PROTOCOL
# ---------------------------------------------------------------------------

section("50. A Custom Sequence-Like Class")

class SimpleSequence:
    """
    A small sequence-like class demonstrating that __getitem__ receives
    either an integer index or a slice object.
    """

    def __init__(self, values: Iterable[Any]) -> None:
        self._values = list(values)

    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, key: int | slice) -> Any:
        if isinstance(key, slice):
            # Returning another SimpleSequence preserves the abstraction.
            return SimpleSequence(self._values[key])

        return self._values[key]

    def __repr__(self) -> str:
        return f"SimpleSequence({self._values!r})"


custom = SimpleSequence([10, 20, 30, 40, 50])

print("Custom sequence:", custom)
print("Index 2:", custom[2])
print("Slice 1:4:", custom[1:4])
print("Reverse:", custom[::-1])


# ---------------------------------------------------------------------------
# SECTION 51: CUSTOM SLICE LOGIC
# ---------------------------------------------------------------------------

section("51. Inspecting Slice Components")

def describe_key(key: int | slice) -> None:
    if isinstance(key, slice):
        print(
            "slice -> "
            f"start={key.start!r}, "
            f"stop={key.stop!r}, "
            f"step={key.step!r}"
        )
    else:
        print(f"integer index -> {key!r}")


for key in [2, slice(1, 8, 2), slice(None, None, -1)]:
    describe_key(key)


# ---------------------------------------------------------------------------
# SECTION 52: PERFORMANCE DISCUSSION THROUGH MEASUREMENT
# ---------------------------------------------------------------------------

section("52. Basic Performance Measurement")

import timeit

large_values = list(range(100_000))

slice_time = timeit.timeit(
    "values[10_000:90_000]",
    globals={"values": large_values},
    number=100,
)

index_time = timeit.timeit(
    "values[50_000]",
    globals={"values": large_values},
    number=100_000,
)

print("100 list slices:", round(slice_time, 6), "seconds")
print("100,000 index operations:", round(index_time, 6), "seconds")

# List indexing is normally O(1).
# A slice that selects k elements normally requires O(k) time and creates
# storage for those selected references.
#
# These measurements depend on the machine and Python implementation.


# ---------------------------------------------------------------------------
# SECTION 53: MEMORY CONSIDERATIONS
# ---------------------------------------------------------------------------

section("53. Slice Copy Versus Shared Reference")

import sys

values = list(range(10_000))
copy_of_values = values[:]

print("Original list object size:", sys.getsizeof(values))
print("Slice copy object size:", sys.getsizeof(copy_of_values))

# sys.getsizeof reports the container's own memory footprint, not the total
# recursive memory footprint of every object referenced by the list.


# ---------------------------------------------------------------------------
# SECTION 54: ITERATION VERSUS SLICING
# ---------------------------------------------------------------------------

section("54. Avoiding Unnecessary Large Copies")

values = list(range(20))

# Slicing creates a new list.
selected = values[5:15]

# An index-based loop can avoid creating a temporary slice.
selected_without_copy = [
    values[index]
    for index in range(5, 15)
]

print("Slice result:", selected)
print("Index-based result:", selected_without_copy)

# For ordinary lists, both produce a new output list here.
# In larger systems, direct iteration or itertools can be preferable when
# no materialized list is required.


# ---------------------------------------------------------------------------
# SECTION 55: ITERTOOLS ISlice
# ---------------------------------------------------------------------------

section("55. Lazy Selection with itertools.islice")

from itertools import islice

values = range(1_000_000)

lazy_section = islice(values, 100, 110)

print("Lazy values:", list(lazy_section))

# islice can select a region from an iterable without first constructing a
# full list of the selected region. It is especially useful with streams
# and generators.


# ---------------------------------------------------------------------------
# SECTION 56: GENERATORS AND SLICING LIMITATION
# ---------------------------------------------------------------------------

section("56. Generators Are Not Directly Sliceable")

def number_generator():
    for number in range(10):
        yield number

generator = number_generator()

try:
    print(generator[2:5])
except TypeError as error:
    print("Generator slicing error:", error)

# Convert when a reusable random-access sequence is required.
generator = number_generator()
print("Converted generator slice:", list(generator)[2:5])

# For large streams, itertools.islice is generally preferable to converting
# the entire generator into a list.


# ---------------------------------------------------------------------------
# SECTION 57: PRACTICAL LOG PROCESSING
# ---------------------------------------------------------------------------

section("57. Log Record Analysis")

logs = [
    "INFO startup",
    "INFO database connected",
    "WARNING cache miss",
    "ERROR authentication failed",
    "ERROR database timeout",
    "INFO retry started",
    "INFO recovery complete",
]

recent_logs = logs[-4:]
error_logs = [entry for entry in recent_logs if entry.startswith("ERROR")]

print("Recent logs:", recent_logs)
print("Recent errors:", error_logs)


# ---------------------------------------------------------------------------
# SECTION 58: TIME-SERIES ANALYSIS
# ---------------------------------------------------------------------------

section("58. Time-Series Window")

daily_sales = [120, 135, 128, 142, 155, 161, 149, 170, 181, 176]

last_seven_days = daily_sales[-7:]
previous_three = daily_sales[-10:-7]

print("Last seven days:", last_seven_days)
print("Previous three:", previous_three)

last_seven_average = sum(last_seven_days) / len(last_seven_days)
print("Seven-day average:", round(last_seven_average, 2))


# ---------------------------------------------------------------------------
# SECTION 59: DATA VALIDATION WITH SLICES
# ---------------------------------------------------------------------------

section("59. Batch Validation")

records = [
    "USR001",
    "USR002",
    "",
    "USR004",
    "USR005",
]

batch = records[:4]
invalid = [record for record in batch if not record]

print("Batch:", batch)
print("Invalid entries:", invalid)


# ---------------------------------------------------------------------------
# SECTION 60: FIXED-WIDTH DATA
# ---------------------------------------------------------------------------

section("60. Fixed-Width Text Fields")

raw_record = "INDIA     2026   ACTIVE  "

country = raw_record[0:10].strip()
year = raw_record[10:18].strip()
status = raw_record[18:].strip()

print("Country:", country)
print("Year:", year)
print("Status:", status)


# ---------------------------------------------------------------------------
# SECTION 61: COMMON MISTAKE: STOP IS EXCLUSIVE
# ---------------------------------------------------------------------------

section("61. Stop Boundary Is Exclusive")

values = list(range(10))

print("values[2:5]:", values[2:5])
print("Indexes selected:", list(range(2, 5)))

# If a programmer wants positions 2, 3, 4, index 5 is the correct stop.


# ---------------------------------------------------------------------------
# SECTION 62: COMMON MISTAKE: OFF-BY-ONE
# ---------------------------------------------------------------------------

section("62. Avoiding Off-by-One Errors")

def first_n(sequence: Sequence[Any], count: int) -> list[Any]:
    if count < 0:
        raise ValueError("count cannot be negative")
    return list(sequence[:count])


values = list("ABCDEFGHIJ")

for count in [0, 1, 3, 10, 20]:
    print(f"first_n({count}):", first_n(values, count))


# ---------------------------------------------------------------------------
# SECTION 63: COMMON MISTAKE: CONFUSING POSITION AND VALUE
# ---------------------------------------------------------------------------

section("63. Position Versus Value")

values = [10, 20, 30, 40]

print("The value at index 2 is:", values[2])

# values.index(30) performs a search for the value 30 and returns its
# first matching position.
print("The position of value 30 is:", values.index(30))


# ---------------------------------------------------------------------------
# SECTION 64: DUPLICATE VALUES
# ---------------------------------------------------------------------------

section("64. Duplicate Values")

values = ["A", "B", "A", "C", "A"]

print("First A:", values.index("A"))
print("Slice containing first three:", values[:3])

# index() returns the first matching position.
# Slicing selects based on positions, not value identity.


# ---------------------------------------------------------------------------
# SECTION 65: REVERSING WITHOUT MUTATING
# ---------------------------------------------------------------------------

section("65. Reverse Copy Versus reverse()")

values = [1, 2, 3, 4]

reversed_copy = values[::-1]
print("Original:", values)
print("Reverse copy:", reversed_copy)

values.reverse()
print("After in-place reverse:", values)


# ---------------------------------------------------------------------------
# SECTION 66: SORTED SLICE RESULTS
# ---------------------------------------------------------------------------

section("66. Sorting a Selected Segment")

values = [8, 3, 7, 2, 9, 1, 6]

middle_sorted = sorted(values[1:6])

print("Original:", values)
print("Selected segment:", values[1:6])
print("Sorted selected segment:", middle_sorted)


# ---------------------------------------------------------------------------
# SECTION 67: ASSIGNING A SORTED SLICE BACK
# ---------------------------------------------------------------------------

section("67. Sorting a Segment In Place")

values = [8, 3, 7, 2, 9, 1, 6]

values[1:6] = sorted(values[1:6])

print("Result:", values)


# ---------------------------------------------------------------------------
# SECTION 68: ROTATION WITH SLICES
# ---------------------------------------------------------------------------

section("68. Rotating a List")

def rotate_left(values: Sequence[Any], positions: int) -> list[Any]:
    """Return a new list rotated left by positions."""
    data = list(values)

    if not data:
        return []

    positions %= len(data)
    return data[positions:] + data[:positions]


def rotate_right(values: Sequence[Any], positions: int) -> list[Any]:
    """Return a new list rotated right by positions."""
    data = list(values)

    if not data:
        return []

    positions %= len(data)
    if positions == 0:
        return data[:]

    return data[-positions:] + data[:-positions]


values = [1, 2, 3, 4, 5]

print("Left 2:", rotate_left(values, 2))
print("Right 2:", rotate_right(values, 2))
print("Left 7:", rotate_left(values, 7))
print("Right 7:", rotate_right(values, 7))


# ---------------------------------------------------------------------------
# SECTION 69: PARTITIONING
# ---------------------------------------------------------------------------

section("69. Partitioning Data")

def partition_at(values: Sequence[Any], position: int) -> tuple[list[Any], list[Any]]:
    """Split a sequence into two lists at a slice boundary."""
    return list(values[:position]), list(values[position:])


left, right = partition_at(list(range(10)), 6)

print("Left:", left)
print("Right:", right)


# ---------------------------------------------------------------------------
# SECTION 70: REUSABLE PAGE FUNCTION
# ---------------------------------------------------------------------------

section("70. Reusable Pagination Function")

def get_page(
    sequence: Sequence[Any],
    page_number: int,
    page_size: int,
) -> list[Any]:
    """
    Return one page of data.

    Page numbers are one-based for human-friendly API behavior.
    """
    if page_number < 1:
        raise ValueError("page_number must be at least 1")
    if page_size <= 0:
        raise ValueError("page_size must be positive")

    start = (page_number - 1) * page_size
    return list(sequence[start:start + page_size])


data = list(range(1, 24))

for page in range(1, 6):
    print(page, "->", get_page(data, page, 5))


# ---------------------------------------------------------------------------
# SECTION 71: SAFE LAST-N
# ---------------------------------------------------------------------------

section("71. Last-N Utility")

def last_n(sequence: Sequence[Any], count: int) -> list[Any]:
    """Return the last count elements without failing for oversized counts."""
    if count < 0:
        raise ValueError("count cannot be negative")
    if count == 0:
        return []
    return list(sequence[-count:])


values = [10, 20, 30]

for count in [0, 1, 2, 3, 10]:
    print(f"last_n({count}):", last_n(values, count))


# ---------------------------------------------------------------------------
# SECTION 72: PREFIX AND SUFFIX
# ---------------------------------------------------------------------------

section("72. Prefix and Suffix Checks")

values = [1, 2, 3, 4, 5]

print("Prefix [1,2]:", values[:2])
print("Suffix [4,5]:", values[-2:])

print("Starts with [1,2]:", values[:2] == [1, 2])
print("Ends with [4,5]:", values[-2:] == [4, 5])


# ---------------------------------------------------------------------------
# SECTION 73: STRIDE-BASED SAMPLING
# ---------------------------------------------------------------------------

section("73. Stride-Based Sampling")

sensor_values = list(range(0, 100, 5))

print("All sensor values:", sensor_values)
print("Every second measurement:", sensor_values[::2])
print("Every third measurement:", sensor_values[::3])


# ---------------------------------------------------------------------------
# SECTION 74: INTERLEAVED DATA
# ---------------------------------------------------------------------------

section("74. Separating Interleaved Data")

interleaved = [
    "temperature", 31,
    "humidity", 65,
    "pressure", 1012,
]

keys = interleaved[::2]
values = interleaved[1::2]

print("Keys:", keys)
print("Values:", values)


# ---------------------------------------------------------------------------
# SECTION 75: PRACTICAL FEATURE EXTRACTION
# ---------------------------------------------------------------------------

section("75. Selecting Feature Columns from Rows")

rows = [
    ["A001", "India", 91, "active"],
    ["A002", "India", 87, "active"],
    ["A003", "Nepal", 76, "inactive"],
]

# The built-in list type does not support selecting arbitrary columns with
# one slice. A comprehension applies the same slice/index rule to rows.

scores = [row[2] for row in rows]
status = [row[-1] for row in rows]

print("Scores:", scores)
print("Status:", status)


# ---------------------------------------------------------------------------
# SECTION 76: MULTI-LEVEL INDEXING
# ---------------------------------------------------------------------------

section("76. Deeply Nested Data")

organization = [
    [
        ["employee-001", "Engineering"],
        ["employee-002", "Security"],
    ],
    [
        ["employee-003", "Finance"],
        ["employee-004", "Operations"],
    ],
]

print("First department:", organization[0])
print("Second employee in first department:", organization[0][1])
print("Name of that employee:", organization[0][1][0])


# ---------------------------------------------------------------------------
# SECTION 77: MUTABLE NESTED DATA
# ---------------------------------------------------------------------------

section("77. Nested Mutation Through Indexing")

organization[0][1][1] = "Cybersecurity"

print("Updated organization:", organization)


# ---------------------------------------------------------------------------
# SECTION 78: COPYING NESTED DATA CAREFULLY
# ---------------------------------------------------------------------------

section("78. Nested Copying Decision")

shallow = organization[:]
deep = deepcopy(organization)

shallow[0][0][0] = "changed-through-shallow"
deep[0][0][0] = "changed-only-in-deep"

print("Original after shallow modification:", organization)
print("Deep copy:", deep)


# ---------------------------------------------------------------------------
# SECTION 79: TESTING INDEXING AND SLICING
# ---------------------------------------------------------------------------

section("79. Automated Assertions")

values = [0, 1, 2, 3, 4]

assert values[0] == 0
assert values[-1] == 4
assert values[1:4] == [1, 2, 3]
assert values[:2] == [0, 1]
assert values[-2:] == [3, 4]
assert values[::-1] == [4, 3, 2, 1, 0]

print("All indexing and slicing assertions passed.")


# ---------------------------------------------------------------------------
# SECTION 80: TESTING EDGE CONDITIONS
# ---------------------------------------------------------------------------

section("80. Edge-Condition Tests")

empty: list[int] = []

assert empty[:] == []
assert empty[0:10] == []
assert empty[-10:] == []
assert empty[::-1] == []

try:
    empty[0]
except IndexError:
    print("Correctly caught indexing into an empty list.")

print("Empty-list slice tests passed.")


# ---------------------------------------------------------------------------
# SECTION 81: COMPARING SLICE NOTATION
# ---------------------------------------------------------------------------

section("81. Equivalent Slice Forms")

values = list(range(10))

equivalent_a = values[:5]
equivalent_b = values[0:5]

print(equivalent_a)
print(equivalent_b)
print("Equivalent:", equivalent_a == equivalent_b)

reverse_a = values[::-1]
reverse_b = values[9::-1]

print("Full reverse:", reverse_a)
print("Explicit reverse from last:", reverse_b)


# ---------------------------------------------------------------------------
# SECTION 82: ADVANCED SLICE NORMALIZATION
# ---------------------------------------------------------------------------

section("82. Slice Normalization with slice.indices")

def normalized_slice(
    length: int,
    start: int | None,
    stop: int | None,
    step: int | None,
) -> tuple[int, int, int]:
    """Convert a slice into concrete bounds for a sequence of given length."""
    return slice(start, stop, step).indices(length)


tests = [
    (10, None, None, None),
    (10, 2, 8, 2),
    (10, -3, None, None),
    (10, None, None, -1),
]

for length, start, stop, step in tests:
    print(
        f"length={length}, start={start}, stop={stop}, step={step}"
        f" -> {normalized_slice(length, start, stop, step)}"
    )


# ---------------------------------------------------------------------------
# SECTION 83: IMPLEMENTING SLICE SELECTION MANUALLY
# ---------------------------------------------------------------------------

section("83. Manual Slice Reasoning")

def manual_slice(
    sequence: Sequence[Any],
    start: int | None = None,
    stop: int | None = None,
    step: int | None = None,
) -> list[Any]:
    """
    Demonstrate the conceptual mechanics of slicing by normalizing the
    slice and iterating over the resulting indexes.

    This is educational, not a replacement for Python's optimized slicing.
    """
    normalized_start, normalized_stop, normalized_step = slice(
        start, stop, step
    ).indices(len(sequence))

    return [
        sequence[index]
        for index in range(
            normalized_start,
            normalized_stop,
            normalized_step,
        )
    ]


values = list("ABCDEFGHIJ")

examples = [
    (None, None, None),
    (2, 7, None),
    (1, 9, 2),
    (8, 2, -1),
    (None, None, -1),
]

for start, stop, step in examples:
    native = values[slice(start, stop, step)]
    manual = manual_slice(values, start, stop, step)
    print(
        f"{start}:{stop}:{step} -> native={native}, manual={manual}, "
        f"equal={native == manual}"
    )


# ---------------------------------------------------------------------------
# SECTION 84: PRODUCTION-STYLE DATA WINDOW
# ---------------------------------------------------------------------------

section("84. Production-Style Rolling Analysis")

@dataclass(frozen=True)
class Measurement:
    timestamp: str
    value: float


measurements = [
    Measurement("09:00", 10.5),
    Measurement("10:00", 11.0),
    Measurement("11:00", 10.8),
    Measurement("12:00", 12.2),
    Measurement("13:00", 12.8),
    Measurement("14:00", 13.1),
]

window_size = 3

for index in range(window_size, len(measurements) + 1):
    window = measurements[index - window_size:index]
    average = sum(item.value for item in window) / len(window)

    print(
        f"{window[-1].timestamp}: "
        f"window={[item.value for item in window]}, "
        f"average={average:.2f}"
    )


# ---------------------------------------------------------------------------
# SECTION 85: ERROR-HANDLING STRATEGY
# ---------------------------------------------------------------------------

section("85. Distinguishing Index Errors from Type Errors")

values = [1, 2, 3]

cases = [1, -1, 10, "1", 1.5, None]

for index in cases:
    try:
        print(f"{index!r} -> {values[index]}")
    except IndexError:
        print(f"{index!r} -> valid type, invalid position")
    except TypeError:
        print(f"{index!r} -> invalid index type")


# ---------------------------------------------------------------------------
# SECTION 86: IMMUTABLE SEQUENCE BEHAVIOR
# ---------------------------------------------------------------------------

section("86. Immutable Sequence Examples")

for sequence in [
    "abcdef",
    (10, 20, 30, 40),
    range(10),
]:
    print("Sequence:", sequence)
    print("First:", sequence[0])
    print("Slice:", sequence[1:4])
    print("Reverse:", sequence[::-1])


# ---------------------------------------------------------------------------
# SECTION 87: COMPARING LIST COPY METHODS
# ---------------------------------------------------------------------------

section("87. Common List Copy Methods")

values = [1, 2, 3]

copy_slice = values[:]
copy_constructor = list(values)
copy_method = values.copy()

print("Slice:", copy_slice)
print("list():", copy_constructor)
print("copy():", copy_method)

print(
    "All distinct outer objects:",
    values is not copy_slice
    and values is not copy_constructor
    and values is not copy_method,
)


# ---------------------------------------------------------------------------
# SECTION 88: SLICE-BASED CLEARING
# ---------------------------------------------------------------------------

section("88. Clearing While Preserving the List Object")

values = [1, 2, 3]
reference = values

values[:] = []

print("values:", values)
print("reference:", reference)
print("Same object:", values is reference)

# This differs from:
#
# values = []
#
# because reassignment would bind values to a new list while existing
# references continue to point to the original list.


# ---------------------------------------------------------------------------
# SECTION 89: REPLACING CONTENT WHILE PRESERVING IDENTITY
# ---------------------------------------------------------------------------

section("89. In-Place Full Replacement")

values = [1, 2, 3]
object_id = id(values)

values[:] = [10, 20, 30, 40]

print("Values:", values)
print("Identity preserved:", id(values) == object_id)


# ---------------------------------------------------------------------------
# SECTION 90: API-STYLE WINDOW EXTRACTION
# ---------------------------------------------------------------------------

section("90. API-Style Record Window")

@dataclass(frozen=True)
class Record:
    record_id: int
    status: str


records = [
    Record(1, "new"),
    Record(2, "processed"),
    Record(3, "processed"),
    Record(4, "failed"),
    Record(5, "new"),
    Record(6, "processed"),
]

offset = 2
limit = 3

window = records[offset:offset + limit]

print("Offset:", offset)
print("Limit:", limit)
print("Returned records:", window)


# ---------------------------------------------------------------------------
# SECTION 91: LIMIT AND OFFSET VALIDATION
# ---------------------------------------------------------------------------

section("91. Robust Offset/Limit Validation")

def window(
    sequence: Sequence[Any],
    offset: int = 0,
    limit: int = 10,
) -> list[Any]:
    """
    Return a bounded window using offset/limit semantics.
    """
    if offset < 0:
        raise ValueError("offset cannot be negative")
    if limit < 0:
        raise ValueError("limit cannot be negative")

    return list(sequence[offset:offset + limit])


values = list(range(20))

for offset, limit in [(0, 5), (5, 5), (18, 5), (20, 5), (5, 0)]:
    print(
        f"offset={offset}, limit={limit} -> "
        f"{window(values, offset, limit)}"
    )


# ---------------------------------------------------------------------------
# SECTION 92: PRACTICAL TOP-N WITH TIES
# ---------------------------------------------------------------------------

section("92. Selecting a Score Region")

players = [
    ("A", 91),
    ("B", 87),
    ("C", 99),
    ("D", 94),
    ("E", 88),
]

sorted_players = sorted(players, key=lambda item: item[1], reverse=True)
top_three = sorted_players[:3]

print("Sorted:", sorted_players)
print("Top three:", top_three)


# ---------------------------------------------------------------------------
# SECTION 93: SLICING DOES NOT FILTER BY VALUE
# ---------------------------------------------------------------------------

section("93. Position Selection Versus Condition Selection")

values = [10, 90, 20, 80, 30, 70]

print("Positional selection:", values[1:5])
print("Conditional selection:", [value for value in values if value >= 70])


# ---------------------------------------------------------------------------
# SECTION 94: SLICE ASSIGNMENT AND LENGTH
# ---------------------------------------------------------------------------

section("94. Length Changes Through Slice Assignment")

values = [1, 2, 3, 4, 5]

for replacement in [
    [],
    [100],
    [100, 200],
    [100, 200, 300, 400],
]:
    current = values[:]
    current[1:4] = replacement
    print(
        f"replacement={replacement!r}, "
        f"result={current!r}, "
        f"length={len(current)}"
    )


# ---------------------------------------------------------------------------
# SECTION 95: ADVANCED EXTENDED SLICE RULE
# ---------------------------------------------------------------------------

section("95. Extended Slice Length Rule")

values = list(range(12))
selected_indexes = list(range(*slice(None, None, 3).indices(len(values))))

print("Selected indexes:", selected_indexes)
print("Selected values:", values[::3])
print("Required replacement length:", len(selected_indexes))


# ---------------------------------------------------------------------------
# SECTION 96: CUSTOM TABLE EXAMPLE
# ---------------------------------------------------------------------------

section("96. Table Row and Column Operations")

table = [
    ["ID", "Name", "Score", "Status"],
    [1, "Asha", 91, "Pass"],
    [2, "Ravi", 84, "Pass"],
    [3, "Meera", 52, "Fail"],
    [4, "Kiran", 96, "Pass"],
]

header = table[0]
data_rows = table[1:]

print("Header:", header)
print("First two data rows:", data_rows[:2])
print("Last two data rows:", data_rows[-2:])
print("Names:", [row[1] for row in data_rows])
print("Scores:", [row[2] for row in data_rows])


# ---------------------------------------------------------------------------
# SECTION 97: DATA CLEANING
# ---------------------------------------------------------------------------

section("97. Data Cleaning Through Slices")

raw_values = [
    None,
    10,
    20,
    None,
    30,
    40,
    None,
]

middle = raw_values[1:-1]
clean_middle = [value for value in middle if value is not None]

print("Raw:", raw_values)
print("Middle:", middle)
print("Clean middle:", clean_middle)


# ---------------------------------------------------------------------------
# SECTION 98: EDGE CASE: EMPTY AND SINGLE-ELEMENT LISTS
# ---------------------------------------------------------------------------

section("98. Empty and Single-Element Lists")

for values in [[], [42]]:
    print("Values:", values)
    print("Full slice:", values[:])
    print("Reverse:", values[::-1])
    print("First three:", values[:3])
    print("Last three:", values[-3:])


# ---------------------------------------------------------------------------
# SECTION 99: EDGE CASE: VERY LARGE BOUNDARIES
# ---------------------------------------------------------------------------

section("99. Very Large Slice Boundaries")

values = [1, 2, 3]

print(values[-10_000:10_000])
print(values[10_000:-10_000])

# Slices clamp out-of-range boundaries rather than raising IndexError.


# ---------------------------------------------------------------------------
# SECTION 100: FINAL INTEGRATED CASE STUDY
# ---------------------------------------------------------------------------

section("100. Integrated Case Study: Sales Dashboard")

@dataclass(frozen=True)
class Sale:
    transaction_id: str
    amount: float
    region: str


sales = [
    Sale("S001", 1200.00, "North"),
    Sale("S002", 850.00, "South"),
    Sale("S003", 2100.00, "North"),
    Sale("S004", 1750.00, "West"),
    Sale("S005", 950.00, "East"),
    Sale("S006", 3200.00, "North"),
    Sale("S007", 1100.00, "South"),
    Sale("S008", 2800.00, "West"),
    Sale("S009", 1600.00, "East"),
    Sale("S010", 4000.00, "North"),
]

# 1. Most recent five transactions.
recent_sales = sales[-5:]

# 2. Highest-value three transactions.
top_sales = sorted(sales, key=lambda sale: sale.amount, reverse=True)[:3]

# 3. Every second transaction for a sampling operation.
sampled_sales = sales[::2]

# 4. Paginated data.
page_two = sales[5:10]

print("Recent five:")
for sale in recent_sales:
    print(sale)

print("\nTop three:")
for sale in top_sales:
    print(sale)

print("\nSampled:")
for sale in sampled_sales:
    print(sale)

print("\nPage two:")
for sale in page_two:
    print(sale)


# ---------------------------------------------------------------------------
# SECTION 101: FINAL PRINCIPLES
# ---------------------------------------------------------------------------

section("101. Core Rules Demonstrated")

principles = [
    "Python sequence indexes are zero-based.",
    "Negative indexes count from the end.",
    "Ordinary indexing returns one element.",
    "An invalid ordinary index raises IndexError.",
    "A slice uses start:stop:step.",
    "The start boundary is inclusive.",
    "The stop boundary is exclusive.",
    "Slice boundaries may be omitted.",
    "Negative slice boundaries are valid.",
    "A negative step moves backward.",
    "A step of zero raises ValueError.",
    "Out-of-range slice boundaries are generally clamped.",
    "A normal list slice creates a new outer list.",
    "Slice assignment can replace, insert, or delete elements.",
    "Extended slice assignment requires matching lengths.",
    "Nested lists require multiple indexing operations.",
    "List slicing is positional, not conditional.",
    "Generators are not directly sliceable.",
    "itertools.islice provides lazy selection for iterables.",
    "Indexing is generally O(1) for Python lists.",
    "Slicing generally costs O(k) for k selected elements.",
]

for number, principle in enumerate(principles, start=1):
    print(f"{number:02d}. {principle}")


print("\nStudy program completed successfully.")
