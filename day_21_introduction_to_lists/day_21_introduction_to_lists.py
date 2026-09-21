"""
Introduction to Lists
======================

A comprehensive standalone study program for learning lists from absolute
beginner level through advanced practical usage.

This file uses Python's built-in list type to demonstrate:

1. What lists are and why they are useful
2. Creating lists
3. Indexing and negative indexing
4. Slicing
5. Updating elements
6. Adding elements
7. Removing elements
8. Searching
9. Membership testing
10. Iteration
11. enumerate()
12. zip()
13. List length
14. Nested lists
15. Lists containing different data types
16. Copying and aliasing
17. Shallow versus independent copies
18. List methods
19. Sorting and reversing
20. Key-based sorting
21. List comprehensions
22. Conditional comprehensions
23. Nested comprehensions
24. Aggregation
25. Filtering and transformation
26. Stack behavior
27. Queue behavior and its limitations
28. Two-dimensional data
29. Matrix operations
30. Deduplication while preserving order
31. Frequency counting
32. Grouping
33. Flattening
34. Chunking
35. Sliding windows
36. Rotation
37. Merging sorted lists
38. Binary search
39. Performance considerations
40. Common mistakes
41. Validation
42. Defensive programming
43. Testing
44. Practical data-processing examples
45. Advanced list-related techniques
46. A complete student-record case study

Run this file with Python 3.
"""

from __future__ import annotations

from dataclasses import dataclass
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict, deque
from copy import copy, deepcopy
from typing import Any, Iterable, Iterator, Sequence


# ---------------------------------------------------------------------------
# Utility functions used throughout the demonstrations
# ---------------------------------------------------------------------------

def section(title: str) -> None:
    """Print a visually distinct section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    """Print a smaller heading."""
    print("\n" + "-" * 60)
    print(title)
    print("-" * 60)


def show(label: str, value: Any) -> None:
    """Print a label and its value."""
    print(f"{label}: {value}")


# ---------------------------------------------------------------------------
# 1. What is a list?
# ---------------------------------------------------------------------------

section("1. What is a list?")

"""
A list is an ordered, mutable collection of objects.

Important properties of Python lists:

- Ordered: elements have a position.
- Mutable: elements can be changed after creation.
- Indexed: positions begin at 0.
- Dynamic: a list can grow or shrink.
- Allows duplicates.
- Can contain values of different types.
- Can contain other lists.
"""

numbers = [10, 20, 30, 40]
show("numbers", numbers)

mixed_values = [42, "Python", 3.14, True, None]
show("mixed_values", mixed_values)

duplicate_values = [5, 5, 7, 7, 7, 9]
show("duplicate_values", duplicate_values)


# ---------------------------------------------------------------------------
# 2. Creating lists
# ---------------------------------------------------------------------------

section("2. Creating lists")

empty_list = []
show("Empty list", empty_list)

scores = [85, 91, 76, 88]
show("Scores", scores)

words = ["Python", "JavaScript", "C++"]
show("Words", words)

# list() can create a list from an iterable.
characters = list("LIST")
show("Characters", characters)

number_range = list(range(1, 6))
show("Numbers generated from range", number_range)

# A list can also be created from a tuple.
tuple_data = (10, 20, 30)
converted_list = list(tuple_data)
show("Tuple converted to list", converted_list)


# ---------------------------------------------------------------------------
# 3. Indexing
# ---------------------------------------------------------------------------

section("3. Indexing")

languages = ["Python", "JavaScript", "C++", "Java", "Go"]

"""
Index positions:

Python       -> 0
JavaScript   -> 1
C++          -> 2
Java         -> 3
Go           -> 4
"""

show("First element", languages[0])
show("Second element", languages[1])
show("Last element", languages[4])

# Negative indexes count from the end.
show("Last element using -1", languages[-1])
show("Second-last element using -2", languages[-2])

"""
Attempting an index outside the valid range raises IndexError.
"""

try:
    print(languages[100])
except IndexError as error:
    print(f"Handled invalid index: {error}")


# ---------------------------------------------------------------------------
# 4. Updating list elements
# ---------------------------------------------------------------------------

section("4. Updating elements")

temperatures = [25, 27, 30, 29]
show("Before update", temperatures)

temperatures[2] = 31
show("After changing index 2", temperatures)

# Multiple positions can be changed using slice assignment.
temperatures[1:3] = [28, 32]
show("After slice assignment", temperatures)


# ---------------------------------------------------------------------------
# 5. Adding elements
# ---------------------------------------------------------------------------

section("5. Adding elements")

items = ["pen", "book"]
show("Initial", items)

# append() adds exactly one object to the end.
items.append("bag")
show("After append", items)

# extend() adds each element from an iterable.
items.extend(["pencil", "eraser"])
show("After extend", items)

# insert() places an element at a specified position.
items.insert(1, "notebook")
show("After insert", items)

"""
Important distinction:

append([1, 2]) adds one list as one element.
extend([1, 2]) adds 1 and 2 as separate elements.
"""

append_example = [1, 2]
append_example.append([3, 4])

extend_example = [1, 2]
extend_example.extend([3, 4])

show("append([3, 4])", append_example)
show("extend([3, 4])", extend_example)


# ---------------------------------------------------------------------------
# 6. Removing elements
# ---------------------------------------------------------------------------

section("6. Removing elements")

shopping = ["milk", "bread", "eggs", "rice", "fruit"]

# remove() removes the first matching value.
shopping.remove("bread")
show("After remove('bread')", shopping)

# pop() removes and returns an element.
removed_item = shopping.pop()
show("Popped item", removed_item)
show("After pop()", shopping)

# pop(index) removes a particular position.
removed_item = shopping.pop(1)
show("Popped item at index 1", removed_item)
show("After pop(1)", shopping)

# del removes an element or slice.
del shopping[0]
show("After del shopping[0]", shopping)

shopping.clear()
show("After clear()", shopping)

# remove() raises ValueError if the value does not exist.
try:
    shopping.remove("does-not-exist")
except ValueError as error:
    print(f"Handled missing-value removal: {error}")


# ---------------------------------------------------------------------------
# 7. Length and membership
# ---------------------------------------------------------------------------

section("7. Length and membership")

numbers = [10, 20, 30, 40]

show("Length", len(numbers))
show("Is 20 present?", 20 in numbers)
show("Is 99 present?", 99 in numbers)

if 30 in numbers:
    print("30 exists in the list.")

if 50 not in numbers:
    print("50 does not exist in the list.")


# ---------------------------------------------------------------------------
# 8. Iterating over lists
# ---------------------------------------------------------------------------

section("8. Iterating over lists")

cities = ["Lucknow", "Delhi", "Mumbai", "Pune"]

for city in cities:
    print("City:", city)

subsection("Iterating with indexes")

for index in range(len(cities)):
    print(index, cities[index])

subsection("Preferred indexed iteration with enumerate()")

for index, city in enumerate(cities):
    print(index, city)

subsection("Starting enumerate() from another number")

for position, city in enumerate(cities, start=1):
    print(f"{position}. {city}")


# ---------------------------------------------------------------------------
# 9. zip() with multiple lists
# ---------------------------------------------------------------------------

section("9. Combining related lists with zip()")

names = ["Asha", "Ravi", "Neha"]
marks = [88, 76, 93]

for name, mark in zip(names, marks):
    print(f"{name}: {mark}")

"""
zip() stops when the shortest input iterable is exhausted.

This prevents automatic creation of meaningless unmatched pairs.
"""

short_list = [1, 2]
long_list = ["a", "b", "c"]

show("zip result", list(zip(short_list, long_list)))


# ---------------------------------------------------------------------------
# 10. Slicing
# ---------------------------------------------------------------------------

section("10. Slicing")

numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

show("Original", numbers)
show("numbers[2:6]", numbers[2:6])
show("numbers[:5]", numbers[:5])
show("numbers[5:]", numbers[5:])
show("numbers[:]", numbers[:])
show("numbers[::2]", numbers[::2])
show("numbers[1::2]", numbers[1::2])
show("numbers[::-1]", numbers[::-1])
show("numbers[8:2:-1]", numbers[8:2:-1])

"""
Slice syntax:

list[start:stop:step]

The start is included.
The stop is excluded.
"""

# Slice assignment can replace, insert, or remove ranges.
values = [1, 2, 3, 4, 5]
values[1:3] = [20, 30, 40]
show("Slice assignment with more values", values)

values[1:4] = [99]
show("Slice assignment with fewer values", values)

values[1:2] = [7, 8, 9]
show("Slice assignment used for insertion", values)

del values[1:3]
show("Slice deletion", values)


# ---------------------------------------------------------------------------
# 11. Important list methods
# ---------------------------------------------------------------------------

section("11. Important list methods")

method_demo = [4, 2, 7, 2, 9]

show("Original", method_demo)
show("count(2)", method_demo.count(2))
show("index(7)", method_demo.index(7))

method_demo.reverse()
show("After reverse()", method_demo)

method_demo.sort()
show("After sort()", method_demo)

method_demo.sort(reverse=True)
show("After sort(reverse=True)", method_demo)


# ---------------------------------------------------------------------------
# 12. sorted() versus list.sort()
# ---------------------------------------------------------------------------

section("12. sorted() versus list.sort()")

original = [5, 1, 4, 2, 3]

sorted_copy = sorted(original)
show("Original after sorted()", original)
show("Result from sorted()", sorted_copy)

original.sort()
show("Original after .sort()", original)

"""
sorted(iterable):
- Returns a new list.
- Works with many iterable types.

list.sort():
- Modifies the existing list.
- Returns None.
"""

result_of_sort = original.sort()
show("Return value of list.sort()", result_of_sort)


# ---------------------------------------------------------------------------
# 13. Sorting with key functions
# ---------------------------------------------------------------------------

section("13. Sorting with key functions")

students = [
    {"name": "Ravi", "marks": 82},
    {"name": "Asha", "marks": 95},
    {"name": "Neha", "marks": 88},
]

students_by_marks = sorted(students, key=lambda student: student["marks"])
show("Sorted by marks", students_by_marks)

students_by_marks_descending = sorted(
    students,
    key=lambda student: student["marks"],
    reverse=True,
)
show("Sorted by marks descending", students_by_marks_descending)

students_by_name = sorted(students, key=lambda student: student["name"])
show("Sorted by name", students_by_name)


# ---------------------------------------------------------------------------
# 14. List comprehensions
# ---------------------------------------------------------------------------

section("14. List comprehensions")

"""
A list comprehension creates a list using a compact expression.

General structure:

[result_expression for item in iterable]

The expression is evaluated once for every item.
"""

numbers = [1, 2, 3, 4, 5]

squares = [number * number for number in numbers]
show("Squares", squares)

doubled = [number * 2 for number in numbers]
show("Doubled", doubled)

upper_words = [word.upper() for word in ["python", "lists", "data"]]
show("Uppercase words", upper_words)


# ---------------------------------------------------------------------------
# 15. Conditional comprehensions
# ---------------------------------------------------------------------------

section("15. Conditional list comprehensions")

even_numbers = [number for number in range(1, 11) if number % 2 == 0]
show("Even numbers", even_numbers)

odd_numbers = [number for number in range(1, 11) if number % 2 != 0]
show("Odd numbers", odd_numbers)

positive_numbers = [number for number in [-3, 4, -1, 7, 0] if number > 0]
show("Positive numbers", positive_numbers)

"""
A conditional expression can also choose the produced value.

Syntax:

[value_if_true if condition else value_if_false for item in iterable]
"""

labels = [
    "even" if number % 2 == 0 else "odd"
    for number in range(1, 7)
]
show("Number labels", labels)


# ---------------------------------------------------------------------------
# 16. Nested list comprehensions
# ---------------------------------------------------------------------------

section("16. Nested list comprehensions")

matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

show("Matrix", matrix)

flattened = [value for row in matrix for value in row]
show("Flattened matrix", flattened)

squared_matrix = [
    [value * value for value in row]
    for row in matrix
]
show("Squared matrix", squared_matrix)


# ---------------------------------------------------------------------------
# 17. Aggregation
# ---------------------------------------------------------------------------

section("17. Aggregating list data")

scores = [72, 91, 84, 67, 95]

show("Minimum", min(scores))
show("Maximum", max(scores))
show("Sum", sum(scores))
show("Average", sum(scores) / len(scores))

"""
Guard against division by zero when calculating an average.
"""

empty_scores: list[int] = []

if empty_scores:
    print("Average:", sum(empty_scores) / len(empty_scores))
else:
    print("Cannot calculate an average for an empty list.")


# ---------------------------------------------------------------------------
# 18. any() and all()
# ---------------------------------------------------------------------------

section("18. any() and all()")

values = [2, 4, 6, 8]

show("Any value greater than 5", any(value > 5 for value in values))
show("All values are even", all(value % 2 == 0 for value in values))

"""
Important edge case:

all([]) is True.
any([]) is False.

These results follow the mathematical meaning of universal and existential
conditions over an empty collection.
"""

show("all([])", all([]))
show("any([])", any([]))


# ---------------------------------------------------------------------------
# 19. Copying and aliasing
# ---------------------------------------------------------------------------

section("19. Aliasing and copying")

original = [10, 20, 30]
alias = original

alias[0] = 999

show("Original after alias modification", original)
show("Alias", alias)

"""
alias and original refer to the same list object.

To create a new outer list, use copy(), slicing, or list().
"""

original = [10, 20, 30]

copy_one = original.copy()
copy_two = original[:]
copy_three = list(original)

copy_one[0] = 100
copy_two[1] = 200
copy_three[2] = 300

show("Original", original)
show("copy()", copy_one)
show("Slice copy", copy_two)
show("list() copy", copy_three)


# ---------------------------------------------------------------------------
# 20. Shallow copies and nested lists
# ---------------------------------------------------------------------------

section("20. Shallow copy versus deep copy")

nested = [[1, 2], [3, 4]]

shallow = copy(nested)
deep = deepcopy(nested)

nested[0][0] = 999

show("Nested original", nested)
show("Shallow copy", shallow)
show("Deep copy", deep)

"""
A shallow copy creates a new outer list but keeps references to the same
inner objects.

A deep copy recursively copies nested objects.

Deep copies are useful when independent nested structures are required, but
they can consume more memory and take more time.
"""


# ---------------------------------------------------------------------------
# 21. The mutable-default-argument mistake
# ---------------------------------------------------------------------------

section("21. Common mistake: mutable default arguments")

"""
Do not use [] as a default parameter when each function call is expected to
have an independent list.

Correct pattern:
"""

def add_item(item: Any, items: list[Any] | None = None) -> list[Any]:
    if items is None:
        items = []
    items.append(item)
    return items


show("First call", add_item("A"))
show("Second call", add_item("B"))


# ---------------------------------------------------------------------------
# 22. List references inside loops
# ---------------------------------------------------------------------------

section("22. Common mistake: repeated references to the same nested list")

wrong_matrix = [[0] * 3] * 3
wrong_matrix[0][0] = 1
show("Problematic repeated-reference matrix", wrong_matrix)

correct_matrix = [[0] * 3 for _ in range(3)]
correct_matrix[0][0] = 1
show("Independent-row matrix", correct_matrix)


# ---------------------------------------------------------------------------
# 23. Removing items while iterating
# ---------------------------------------------------------------------------

section("23. Removing items safely")

numbers = [1, 2, 3, 4, 5, 6]

"""
Removing elements directly while iterating over the same list can cause
elements to be skipped because indexes shift.

A list comprehension is often clearer.
"""

numbers = [number for number in numbers if number % 2 == 0]
show("Only even numbers", numbers)


# ---------------------------------------------------------------------------
# 24. Filtering and transforming data
# ---------------------------------------------------------------------------

section("24. Filtering and transforming data")

prices = [100, 250, 75, 500, 120]

expensive_prices = [price for price in prices if price >= 200]
show("Prices >= 200", expensive_prices)

discounted_prices = [round(price * 0.90, 2) for price in prices]
show("10% discounted prices", discounted_prices)

taxed_prices = [round(price * 1.18, 2) for price in prices]
show("Prices with 18% tax", taxed_prices)


# ---------------------------------------------------------------------------
# 25. Deduplication while preserving order
# ---------------------------------------------------------------------------

section("25. Removing duplicates while preserving order")

values = [4, 2, 4, 7, 2, 9, 7, 1]

unique_values = list(dict.fromkeys(values))
show("Original", values)
show("Unique values in original order", unique_values)

"""
A set is excellent for membership testing but does not represent the same
purpose as an ordered list. dict.fromkeys() is a convenient way to preserve
the first occurrence of each value.
"""


# ---------------------------------------------------------------------------
# 26. Frequency counting
# ---------------------------------------------------------------------------

section("26. Counting frequencies")

votes = ["A", "B", "A", "C", "B", "A"]

frequency = Counter(votes)
show("Frequency table", frequency)
show("Most common values", frequency.most_common())

"""
Counter is not itself a list, but it is useful when processing list data.
"""

numbers = [1, 1, 2, 3, 3, 3]
frequency_numbers = Counter(numbers)
show("Number frequencies", frequency_numbers)


# ---------------------------------------------------------------------------
# 27. Grouping list data
# ---------------------------------------------------------------------------

section("27. Grouping list records")

employees = [
    {"name": "Asha", "department": "IT"},
    {"name": "Ravi", "department": "Finance"},
    {"name": "Neha", "department": "IT"},
    {"name": "Arjun", "department": "HR"},
]

employees_by_department: defaultdict[str, list[dict[str, str]]] = defaultdict(list)

for employee in employees:
    employees_by_department[employee["department"]].append(employee)

for department, members in employees_by_department.items():
    print(department, "->", members)


# ---------------------------------------------------------------------------
# 28. Flattening nested lists
# ---------------------------------------------------------------------------

section("28. Flattening nested lists")

nested_values = [
    [1, 2],
    [3, 4],
    [5, 6],
]

flattened_values = []

for group in nested_values:
    for value in group:
        flattened_values.append(value)

show("Flattened using loops", flattened_values)

flattened_values_comp = [
    value
    for group in nested_values
    for value in group
]
show("Flattened using comprehension", flattened_values_comp)


# ---------------------------------------------------------------------------
# 29. A reusable flatten function
# ---------------------------------------------------------------------------

section("29. Recursive flattening")

def flatten_nested(value: Any) -> list[Any]:
    """
    Recursively flatten lists and tuples.

    Strings and bytes are treated as atomic values rather than iterated
    character by character.
    """
    if isinstance(value, (list, tuple)):
        result: list[Any] = []
        for item in value:
            result.extend(flatten_nested(item))
        return result

    return [value]


nested_data = [1, [2, [3, 4]], [[5], 6], "ABC"]
show("Original nested data", nested_data)
show("Recursively flattened", flatten_nested(nested_data))


# ---------------------------------------------------------------------------
# 30. Chunking
# ---------------------------------------------------------------------------

section("30. Splitting a list into chunks")

def chunk_list(values: Sequence[Any], size: int) -> list[list[Any]]:
    """Split values into consecutive chunks of at most size elements."""
    if size <= 0:
        raise ValueError("Chunk size must be positive.")

    return [
        list(values[start:start + size])
        for start in range(0, len(values), size)
    ]


data = list(range(1, 11))

show("Chunks of size 3", chunk_list(data, 3))

try:
    chunk_list(data, 0)
except ValueError as error:
    print(f"Handled invalid chunk size: {error}")


# ---------------------------------------------------------------------------
# 31. Sliding windows
# ---------------------------------------------------------------------------

section("31. Sliding windows")

def sliding_windows(values: Sequence[Any], window_size: int) -> list[list[Any]]:
    """Return every consecutive window of a requested size."""
    if window_size <= 0:
        raise ValueError("Window size must be positive.")

    if window_size > len(values):
        return []

    return [
        list(values[index:index + window_size])
        for index in range(len(values) - window_size + 1)
    ]


temperatures = [20, 22, 24, 23, 25]
show("Three-value windows", sliding_windows(temperatures, 3))


# ---------------------------------------------------------------------------
# 32. Rotating lists
# ---------------------------------------------------------------------------

section("32. Rotating lists")

def rotate_right(values: Sequence[Any], positions: int) -> list[Any]:
    """Return a new list rotated to the right."""
    if not values:
        return []

    positions %= len(values)
    if positions == 0:
        return list(values)

    return list(values[-positions:]) + list(values[:-positions])


rotation_data = [1, 2, 3, 4, 5]

show("Original", rotation_data)
show("Rotate right by 2", rotate_right(rotation_data, 2))
show("Rotate right by 7", rotate_right(rotation_data, 7))
show("Rotate right by -1", rotate_right(rotation_data, -1))


# ---------------------------------------------------------------------------
# 33. Merging two sorted lists
# ---------------------------------------------------------------------------

section("33. Merging sorted lists")

def merge_sorted_lists(first: Sequence[int], second: Sequence[int]) -> list[int]:
    """
    Merge two already-sorted sequences in linear time.

    Complexity:
        Time: O(n + m)
        Extra output space: O(n + m)
    """
    result: list[int] = []
    first_index = 0
    second_index = 0

    while first_index < len(first) and second_index < len(second):
        if first[first_index] <= second[second_index]:
            result.append(first[first_index])
            first_index += 1
        else:
            result.append(second[second_index])
            second_index += 1

    result.extend(first[first_index:])
    result.extend(second[second_index:])

    return result


first_sorted = [1, 4, 7, 10]
second_sorted = [2, 3, 8, 9]

show(
    "Merged result",
    merge_sorted_lists(first_sorted, second_sorted),
)


# ---------------------------------------------------------------------------
# 34. Binary search
# ---------------------------------------------------------------------------

section("34. Binary search on sorted lists")

def binary_search(values: Sequence[int], target: int) -> int:
    """
    Find target in a sorted sequence.

    Returns:
        Index of target if found.
        -1 otherwise.

    Complexity:
        Time: O(log n)
        Space: O(1)
    """
    left = 0
    right = len(values) - 1

    while left <= right:
        middle = (left + right) // 2

        if values[middle] == target:
            return middle

        if values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


sorted_numbers = [10, 20, 30, 40, 50, 60]

show("Index of 40", binary_search(sorted_numbers, 40))
show("Index of 99", binary_search(sorted_numbers, 99))

"""
Binary search requires sorted data.

Python's bisect module provides optimized insertion-point operations.
"""

position = bisect_left(sorted_numbers, 35)
show("Insertion position for 35", position)

position = bisect_right(sorted_numbers, 40)
show("Position after existing 40", position)


# ---------------------------------------------------------------------------
# 35. Stack behavior
# ---------------------------------------------------------------------------

section("35. Lists as stacks")

"""
A stack follows LIFO:

Last In, First Out.

append() pushes an item.
pop() removes the most recently added item.
"""

stack: list[str] = []

stack.append("first")
stack.append("second")
stack.append("third")

show("Stack", stack)

while stack:
    print("Popped:", stack.pop())


# ---------------------------------------------------------------------------
# 36. Queue behavior
# ---------------------------------------------------------------------------

section("36. Lists versus queues")

"""
A queue follows FIFO:

First In, First Out.

Removing from the beginning of a Python list using pop(0) is O(n), because
remaining elements need to be shifted.

For frequent queue operations, collections.deque is generally preferable.
"""

queue = deque()

queue.append("customer-1")
queue.append("customer-2")
queue.append("customer-3")

while queue:
    print("Serving:", queue.popleft())


# ---------------------------------------------------------------------------
# 37. List as a two-dimensional data structure
# ---------------------------------------------------------------------------

section("37. Two-dimensional lists")

matrix = [
    [10, 20, 30],
    [40, 50, 60],
    [70, 80, 90],
]

for row in matrix:
    print(row)

show("Element at row 1, column 2", matrix[1][2])

subsection("Traversing every matrix element")

for row in matrix:
    for value in row:
        print(value, end=" ")
    print()


# ---------------------------------------------------------------------------
# 38. Matrix transpose
# ---------------------------------------------------------------------------

section("38. Matrix transpose")

matrix = [
    [1, 2, 3],
    [4, 5, 6],
]

transpose = [list(column) for column in zip(*matrix)]

show("Original matrix", matrix)
show("Transpose", transpose)


# ---------------------------------------------------------------------------
# 39. Matrix validation
# ---------------------------------------------------------------------------

section("39. Validating rectangular matrices")

def is_rectangular_matrix(matrix: Sequence[Sequence[Any]]) -> bool:
    """Return True when every row has the same length."""
    if not matrix:
        return True

    expected_length = len(matrix[0])

    return all(len(row) == expected_length for row in matrix)


valid_matrix = [[1, 2], [3, 4]]
invalid_matrix = [[1, 2], [3]]

show("Valid matrix?", is_rectangular_matrix(valid_matrix))
show("Invalid matrix?", is_rectangular_matrix(invalid_matrix))


# ---------------------------------------------------------------------------
# 40. Lists of objects
# ---------------------------------------------------------------------------

section("40. Lists of objects")

@dataclass
class Product:
    name: str
    price: float
    quantity: int

    @property
    def inventory_value(self) -> float:
        return self.price * self.quantity


products = [
    Product("Laptop", 65000, 3),
    Product("Mouse", 1200, 15),
    Product("Keyboard", 2500, 8),
]

for product in products:
    print(
        product.name,
        product.price,
        product.quantity,
        product.inventory_value,
    )

most_expensive = max(products, key=lambda product: product.price)
show("Most expensive product", most_expensive.name)


# ---------------------------------------------------------------------------
# 41. Lists and functions
# ---------------------------------------------------------------------------

section("41. Passing lists to functions")

def calculate_total(values: Sequence[float]) -> float:
    """Return the total of numeric values."""
    return sum(values)


def calculate_average(values: Sequence[float]) -> float:
    """Return the average or raise ValueError for an empty sequence."""
    if not values:
        raise ValueError("Cannot calculate an average of an empty sequence.")

    return sum(values) / len(values)


sales = [1000.0, 2500.0, 1750.0]

show("Sales total", calculate_total(sales))
show("Sales average", calculate_average(sales))


# ---------------------------------------------------------------------------
# 42. Type validation
# ---------------------------------------------------------------------------

section("42. Validation before list processing")

def calculate_average_checked(values: Sequence[Any]) -> float:
    """
    Validate that all values are numbers before calculating an average.

    bool is intentionally excluded because bool is a subclass of int in
    Python but usually should not be treated as a numeric measurement.
    """
    if not values:
        raise ValueError("At least one value is required.")

    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(
                f"Invalid value {value!r}; expected int or float."
            )

    return sum(values) / len(values)


show(
    "Checked average",
    calculate_average_checked([10, 20, 30]),
)

try:
    calculate_average_checked([10, "20", 30])
except (TypeError, ValueError) as error:
    print(f"Validation error: {error}")


# ---------------------------------------------------------------------------
# 43. Sorting stability
# ---------------------------------------------------------------------------

section("43. Stable sorting")

records = [
    ("Asha", "IT", 90),
    ("Ravi", "Finance", 90),
    ("Neha", "IT", 80),
    ("Arjun", "Finance", 90),
]

"""
Python's sort is stable. When two elements have equal keys, their original
relative order is preserved.

This is useful for multi-stage sorting.
"""

records_by_marks = sorted(records, key=lambda record: record[2])
show("Records sorted by marks", records_by_marks)


# ---------------------------------------------------------------------------
# 44. Performance characteristics
# ---------------------------------------------------------------------------

section("44. List operation complexity")

"""
Typical Python list complexity:

Operation                  Typical complexity
------------------------------------------------
Index access               O(1)
Index assignment           O(1)
append()                   Amortized O(1)
pop()                      O(1)
insert(0, value)           O(n)
pop(0)                     O(n)
Search using 'in'          O(n)
remove(value)              O(n)
sort()                     O(n log n)
Reverse                    O(n)
Copy                       O(n)
Slicing                    O(k)

The exact implementation details depend on the operation and Python
implementation, but these are the standard practical complexity models.
"""

large_demo = list(range(100))

show("First value", large_demo[0])
show("Last value", large_demo[-1])


# ---------------------------------------------------------------------------
# 45. Memory considerations
# ---------------------------------------------------------------------------

section("45. Memory considerations")

"""
A Python list stores references to Python objects.

Therefore:

[1, 2, 3]

does not mean that the list itself directly stores the full representation
of each integer in the same way a fixed-width C array would.

This contributes to Python's flexibility but also means Python lists can
consume substantially more memory than tightly packed numeric arrays.

For ordinary application-level collections, list is often the natural
choice. For specialized numeric workloads, other data structures may be
more memory efficient.
"""

memory_example = [100, 200, 300]
show("Memory example", memory_example)


# ---------------------------------------------------------------------------
# 46. List versus tuple versus set
# ---------------------------------------------------------------------------

section("46. List versus tuple versus set")

"""
List:
- Ordered
- Mutable
- Allows duplicates
- Indexed

Tuple:
- Ordered
- Immutable
- Allows duplicates
- Indexed

Set:
- Designed for unique elements
- Supports fast average-case membership testing
- Does not provide list-style positional indexing
"""

comparison_list = [1, 2, 2, 3]
comparison_tuple = (1, 2, 2, 3)
comparison_set = {1, 2, 2, 3}

show("List", comparison_list)
show("Tuple", comparison_tuple)
show("Set", comparison_set)


# ---------------------------------------------------------------------------
# 47. List versus array-like structures
# ---------------------------------------------------------------------------

section("47. Choosing a list appropriately")

"""
Use a Python list when:

- You need an ordered collection.
- Values may need to be changed.
- Values can be heterogeneous.
- You need convenient indexing and slicing.
- You frequently append items.

Consider another structure when:

- You need uniqueness as the primary requirement -> set.
- You need immutable ordered data -> tuple.
- You need key-value lookup -> dict.
- You need efficient FIFO queue operations -> deque.
- You need compact homogeneous numeric storage -> specialized array tools.
"""


# ---------------------------------------------------------------------------
# 48. Generator versus list
# ---------------------------------------------------------------------------

section("48. List versus generator")

def generate_squares(limit: int) -> Iterator[int]:
    for number in range(limit):
        yield number * number


generator = generate_squares(5)

show("Generator object", generator)
show("Generator converted to list", list(generator))

"""
A list materializes all values immediately.

A generator produces values lazily.

For very large sequences, lazy processing can significantly reduce memory
usage, but a generator does not provide normal random indexing.
"""


# ---------------------------------------------------------------------------
# 49. Practical data-cleaning pipeline
# ---------------------------------------------------------------------------

section("49. Practical list data-cleaning pipeline")

raw_values = [
    " 100 ",
    "250",
    "",
    "invalid",
    " 300",
    "150 ",
]

cleaned_values: list[float] = []

for raw_value in raw_values:
    value = raw_value.strip()

    if not value:
        continue

    try:
        cleaned_values.append(float(value))
    except ValueError:
        print(f"Skipped invalid value: {raw_value!r}")

show("Clean numeric values", cleaned_values)
show("Total", sum(cleaned_values))


# ---------------------------------------------------------------------------
# 50. Practical sales analysis
# ---------------------------------------------------------------------------

section("50. Practical sales analysis")

sales_records = [
    {"product": "Laptop", "quantity": 2, "price": 65000},
    {"product": "Mouse", "quantity": 10, "price": 1200},
    {"product": "Keyboard", "quantity": 5, "price": 2500},
    {"product": "Monitor", "quantity": 3, "price": 18000},
]

line_totals = [
    record["quantity"] * record["price"]
    for record in sales_records
]

show("Line totals", line_totals)
show("Total sales", sum(line_totals))
show("Highest line total", max(line_totals))


# ---------------------------------------------------------------------------
# 51. Practical ranking
# ---------------------------------------------------------------------------

section("51. Ranking records")

candidates = [
    {"name": "Asha", "score": 91},
    {"name": "Ravi", "score": 84},
    {"name": "Neha", "score": 96},
    {"name": "Arjun", "score": 88},
]

ranking = sorted(
    candidates,
    key=lambda candidate: candidate["score"],
    reverse=True,
)

for rank, candidate in enumerate(ranking, start=1):
    print(
        f"{rank}. {candidate['name']} - {candidate['score']}"
    )


# ---------------------------------------------------------------------------
# 52. Stable ranking with a secondary key
# ---------------------------------------------------------------------------

section("52. Multi-key sorting")

employees = [
    {"name": "Asha", "department": "IT", "salary": 90000},
    {"name": "Ravi", "department": "Finance", "salary": 85000},
    {"name": "Neha", "department": "IT", "salary": 95000},
    {"name": "Arjun", "department": "Finance", "salary": 88000},
]

department_salary_order = sorted(
    employees,
    key=lambda employee: (employee["department"], -employee["salary"]),
)

for employee in department_salary_order:
    print(employee)


# ---------------------------------------------------------------------------
# 53. In-place versus out-of-place transformations
# ---------------------------------------------------------------------------

section("53. In-place versus out-of-place operations")

values = [3, 1, 2]

new_values = sorted(values)

show("Original after sorted()", values)
show("New sorted list", new_values)

values.sort()

show("Original after sort()", values)

"""
An in-place operation can be useful when ownership of the original list is
clear. A new list is safer when other parts of a program need the original
ordering.
"""


# ---------------------------------------------------------------------------
# 54. List equality and identity
# ---------------------------------------------------------------------------

section("54. Equality versus identity")

first = [1, 2, 3]
second = [1, 2, 3]
third = first

show("first == second", first == second)
show("first is second", first is second)
show("first is third", first is third)

"""
== compares values.

is checks whether two references point to the same object.

Do not use is when you mean ordinary value equality.
"""


# ---------------------------------------------------------------------------
# 55. Truthiness
# ---------------------------------------------------------------------------

section("55. Empty and non-empty lists")

empty = []
non_empty = [1]

if not empty:
    print("An empty list is falsey.")

if non_empty:
    print("A non-empty list is truthy.")


# ---------------------------------------------------------------------------
# 56. Safe first-element access
# ---------------------------------------------------------------------------

section("56. Handling empty lists")

def first_or_default(values: Sequence[Any], default: Any = None) -> Any:
    """Return the first item or a supplied default."""
    return values[0] if values else default


show("First item", first_or_default([10, 20]))
show("First item from empty list", first_or_default([]))
show("Custom default", first_or_default([], "N/A"))


# ---------------------------------------------------------------------------
# 57. Finding all matching indexes
# ---------------------------------------------------------------------------

section("57. Finding all matching positions")

def find_all_indexes(values: Sequence[Any], target: Any) -> list[int]:
    return [
        index
        for index, value in enumerate(values)
        if value == target
    ]


values = ["A", "B", "A", "C", "A"]

show("Indexes containing A", find_all_indexes(values, "A"))


# ---------------------------------------------------------------------------
# 58. Partitioning values
# ---------------------------------------------------------------------------

section("58. Partitioning a list")

def partition_even_odd(values: Iterable[int]) -> tuple[list[int], list[int]]:
    even: list[int] = []
    odd: list[int] = []

    for value in values:
        if value % 2 == 0:
            even.append(value)
        else:
            odd.append(value)

    return even, odd


even_values, odd_values = partition_even_odd(range(1, 11))

show("Even values", even_values)
show("Odd values", odd_values)


# ---------------------------------------------------------------------------
# 59. Safe deletion by index
# ---------------------------------------------------------------------------

section("59. Safe deletion by index")

def remove_at(values: list[Any], index: int) -> Any:
    """
    Remove and return an item by index with explicit bounds validation.
    """
    if not -len(values) <= index < len(values):
        raise IndexError(
            f"Index {index} is outside the valid range for this list."
        )

    return values.pop(index)


values = ["a", "b", "c"]

show("Removed", remove_at(values, 1))
show("Remaining", values)

try:
    remove_at(values, 99)
except IndexError as error:
    print(f"Handled deletion error: {error}")


# ---------------------------------------------------------------------------
# 60. Defensive processing of nested data
# ---------------------------------------------------------------------------

section("60. Defensive processing of nested records")

orders = [
    {"customer": "Asha", "items": ["Laptop", "Mouse"]},
    {"customer": "Ravi", "items": ["Keyboard"]},
    {"customer": "Neha", "items": []},
]

for order in orders:
    items = order.get("items", [])
    if not isinstance(items, list):
        print(f"Invalid items for {order.get('customer')}")
        continue

    print(
        order.get("customer"),
        "has",
        len(items),
        "item(s).",
    )


# ---------------------------------------------------------------------------
# 61. Iterator behavior
# ---------------------------------------------------------------------------

section("61. Iterators over lists")

values = [10, 20, 30]

iterator = iter(values)

show("First next()", next(iterator))
show("Second next()", next(iterator))
show("Third next()", next(iterator))

try:
    next(iterator)
except StopIteration:
    print("Iterator is exhausted.")


# ---------------------------------------------------------------------------
# 62. Enumerating transformed data
# ---------------------------------------------------------------------------

section("62. enumerate() with comprehensions")

names = ["asha", "ravi", "neha"]

formatted_names = [
    f"{index}: {name.title()}"
    for index, name in enumerate(names, start=1)
]

for line in formatted_names:
    print(line)


# ---------------------------------------------------------------------------
# 63. Filtering using functions
# ---------------------------------------------------------------------------

section("63. Functional filtering")

numbers = list(range(1, 11))

greater_than_five = list(filter(lambda value: value > 5, numbers))
squared_numbers = list(map(lambda value: value * value, numbers))

show("filter result", greater_than_five)
show("map result", squared_numbers)

"""
List comprehensions are often preferred in Python when they make the
transformation clearer.
"""

greater_than_five_comp = [value for value in numbers if value > 5]
squared_numbers_comp = [value * value for value in numbers]

show("Comprehension filter", greater_than_five_comp)
show("Comprehension map", squared_numbers_comp)


# ---------------------------------------------------------------------------
# 64. Practical mini-project: student analysis
# ---------------------------------------------------------------------------

section("64. Mini-project: student analysis")

@dataclass
class Student:
    name: str
    marks: list[float]

    @property
    def total(self) -> float:
        return sum(self.marks)

    @property
    def average(self) -> float:
        if not self.marks:
            return 0.0
        return self.total / len(self.marks)

    @property
    def passed(self) -> bool:
        return bool(self.marks) and all(mark >= 40 for mark in self.marks)


students = [
    Student("Asha", [88, 91, 84]),
    Student("Ravi", [72, 68, 75]),
    Student("Neha", [95, 93, 97]),
    Student("Arjun", [35, 74, 61]),
]

for student in students:
    print(
        student.name,
        "Total:", student.total,
        "Average:", round(student.average, 2),
        "Passed:", student.passed,
    )

top_student = max(students, key=lambda student: student.average)
show("Highest average", top_student.name)


# ---------------------------------------------------------------------------
# 65. Mini-project: inventory analysis
# ---------------------------------------------------------------------------

section("65. Mini-project: inventory analysis")

inventory = [
    Product("Laptop", 65000, 3),
    Product("Mouse", 1200, 0),
    Product("Keyboard", 2500, 8),
    Product("Monitor", 18000, 2),
]

out_of_stock = [
    product
    for product in inventory
    if product.quantity == 0
]

inventory_value = sum(
    product.inventory_value
    for product in inventory
)

show(
    "Out-of-stock products",
    [product.name for product in out_of_stock],
)

show("Total inventory value", inventory_value)


# ---------------------------------------------------------------------------
# 66. Testing list functions
# ---------------------------------------------------------------------------

section("66. Testing list-processing functions")

def run_assertion_tests() -> None:
    assert chunk_list([1, 2, 3, 4, 5], 2) == [
        [1, 2],
        [3, 4],
        [5],
    ]

    assert rotate_right([1, 2, 3], 1) == [3, 1, 2]
    assert rotate_right([1, 2, 3], 3) == [1, 2, 3]

    assert binary_search([10, 20, 30], 20) == 1
    assert binary_search([10, 20, 30], 99) == -1

    assert flatten_nested([1, [2, [3]]]) == [1, 2, 3]

    assert find_all_indexes(["x", "y", "x"], "x") == [0, 2]

    assert is_rectangular_matrix([[1, 2], [3, 4]])
    assert not is_rectangular_matrix([[1, 2], [3]])

    assert first_or_default([]) is None
    assert first_or_default([], 99) == 99

    print("All assertions passed.")


run_assertion_tests()


# ---------------------------------------------------------------------------
# 67. Edge cases
# ---------------------------------------------------------------------------

section("67. Important edge cases")

edge_cases = [
    [],
    [1],
    [None],
    [0],
    [""],
    [False],
    [1, 1, 1],
]

for case in edge_cases:
    print(
        "Value:", case,
        "| Length:", len(case),
        "| Truthy:", bool(case),
    )


# ---------------------------------------------------------------------------
# 68. Practical checklist
# ---------------------------------------------------------------------------

section("68. List best-practice checklist")

best_practices = [
    "Use meaningful variable names.",
    "Use enumerate() instead of manually tracking indexes.",
    "Use list comprehensions when they remain readable.",
    "Use append() for one item and extend() for multiple items.",
    "Do not confuse append() with extend().",
    "Avoid modifying a list while directly iterating over it.",
    "Use deque for frequent FIFO queue operations.",
    "Remember that list membership testing is linear in the general case.",
    "Use sorted() when the original order should remain unchanged.",
    "Use list.sort() when in-place sorting is intended.",
    "Be careful with shallow copies of nested lists.",
    "Validate indexes and input data at system boundaries.",
    "Handle empty lists before operations such as average calculations.",
    "Choose sets, dictionaries, tuples, or specialized structures when they fit the problem better.",
]

for number, practice in enumerate(best_practices, start=1):
    print(f"{number}. {practice}")


# ---------------------------------------------------------------------------
# 69. Final integrated example
# ---------------------------------------------------------------------------

section("69. Integrated list-processing example")

transactions = [
    {"id": 101, "category": "food", "amount": 450.0},
    {"id": 102, "category": "travel", "amount": 2500.0},
    {"id": 103, "category": "food", "amount": 700.0},
    {"id": 104, "category": "technology", "amount": 15000.0},
    {"id": 105, "category": "travel", "amount": 1200.0},
]

valid_transactions = [
    transaction
    for transaction in transactions
    if transaction["amount"] >= 0
]

total_spending = sum(
    transaction["amount"]
    for transaction in valid_transactions
)

largest_transaction = max(
    valid_transactions,
    key=lambda transaction: transaction["amount"],
)

category_totals: defaultdict[str, float] = defaultdict(float)

for transaction in valid_transactions:
    category_totals[transaction["category"]] += transaction["amount"]

print("Valid transactions:", len(valid_transactions))
print("Total spending:", total_spending)
print("Largest transaction:", largest_transaction)

print("Category totals:")
for category, amount in sorted(category_totals.items()):
    print(f"  {category}: {amount}")


# ---------------------------------------------------------------------------
# 70. Completion
# ---------------------------------------------------------------------------

section("Study file completed")

print(
    "The examples above demonstrate Python lists from basic creation and "
    "indexing through nested structures, algorithms, data processing, "
    "performance considerations, validation, testing, and practical "
    "applications."
)
