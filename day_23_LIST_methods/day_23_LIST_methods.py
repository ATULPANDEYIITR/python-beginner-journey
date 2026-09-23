"""
LIST METHODS
============

A comprehensive, executable study file covering Python list methods from
absolute beginner level through advanced practical usage.

A list is an ordered, mutable collection that can contain zero or more
objects. Python lists preserve insertion order, allow duplicate values,
support indexing and slicing, and can contain values of different types.

This file intentionally demonstrates the actual methods rather than merely
describing them. Run the file directly to execute all demonstrations.

Python list methods covered:
    append()
    extend()
    insert()
    remove()
    pop()
    clear()
    index()
    count()
    sort()
    reverse()
    copy()

Related list operations and advanced concepts:
    indexing
    negative indexing
    slicing
    membership
    concatenation
    repetition
    unpacking
    iteration
    nested lists
    list comprehensions
    shallow copies
    aliasing
    sorting with key functions
    stable sorting
    custom objects
    stack behavior
    queue considerations
    validation
    exception handling
    performance and complexity
    mutation and side effects
    practical case study
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Iterable, Iterator, Optional


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def section(title: str) -> None:
    """Print a visually separated section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def show(label: str, value) -> None:
    """Print a value with a descriptive label."""
    print(f"{label}: {value!r}")


# ---------------------------------------------------------------------------
# 1. Creating lists
# ---------------------------------------------------------------------------

section("1. Creating Lists")

empty_list = []
numbers = [10, 20, 30, 40]
mixed_list = ["Atul", 42, 3.14, True, None]
repeated = ["Python"] * 3

show("Empty list", empty_list)
show("Numbers", numbers)
show("Mixed list", mixed_list)
show("Repeated values", repeated)

# A list can contain another list. Such a structure is called a nested list.
nested = [[1, 2], [3, 4], [5, 6]]
show("Nested list", nested)


# ---------------------------------------------------------------------------
# 2. Indexing
# ---------------------------------------------------------------------------

section("2. Indexing")

languages = ["Python", "JavaScript", "C++", "Java"]

show("First element", languages[0])
show("Second element", languages[1])
show("Last element", languages[-1])
show("Second-last element", languages[-2])

# Invalid indexes raise IndexError.
try:
    print(languages[100])
except IndexError as error:
    print(f"Invalid index handled: {error}")


# ---------------------------------------------------------------------------
# 3. Slicing
# ---------------------------------------------------------------------------

section("3. Slicing")

values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

show("values[2:7]", values[2:7])
show("values[:5]", values[:5])
show("values[5:]", values[5:])
show("values[::2]", values[::2])
show("values[::-1]", values[::-1])

# Slice assignment changes the original list.
mutable_values = [1, 2, 3, 4, 5]
mutable_values[1:4] = [20, 30]
show("After slice assignment", mutable_values)


# ---------------------------------------------------------------------------
# 4. append()
# ---------------------------------------------------------------------------

section("4. append()")

items = ["Python", "JavaScript"]
result = items.append("C++")

show("After append", items)
show("Return value of append()", result)

# append() adds exactly one object.
items.append(["Java", "Go"])
show("append() with a list", items)

# The nested list remains one element.


# ---------------------------------------------------------------------------
# 5. extend()
# ---------------------------------------------------------------------------

section("5. extend()")

languages = ["Python", "JavaScript"]
result = languages.extend(["C++", "Java"])

show("After extend()", languages)
show("Return value of extend()", result)

# extend() consumes an iterable and adds each of its elements.
letters = ["A"]
letters.extend("BCD")
show("Extending with a string", letters)

# This distinction is fundamental:
# append(["C", "D"]) adds one list object.
# extend(["C", "D"]) adds C and D separately.


# ---------------------------------------------------------------------------
# 6. insert()
# ---------------------------------------------------------------------------

section("6. insert()")

numbers = [10, 20, 40]
numbers.insert(2, 30)
show("After inserting 30 at index 2", numbers)

# Negative indexes are accepted.
numbers.insert(-1, 35)
show("After insert(-1, 35)", numbers)

# An index larger than the list length inserts at the end.
numbers.insert(1000, 50)
show("After very large index", numbers)

# A sufficiently negative index inserts at the beginning.
numbers.insert(-1000, 5)
show("After very negative index", numbers)


# ---------------------------------------------------------------------------
# 7. remove()
# ---------------------------------------------------------------------------

section("7. remove()")

items = ["red", "blue", "green", "blue"]
items.remove("blue")

# remove() removes only the first matching value.
show("After removing first blue", items)

try:
    items.remove("purple")
except ValueError as error:
    print(f"remove() failure handled: {error}")


# ---------------------------------------------------------------------------
# 8. pop()
# ---------------------------------------------------------------------------

section("8. pop()")

stack = ["first", "second", "third"]

last_item = stack.pop()
show("Popped last item", last_item)
show("Stack after pop()", stack)

first_item = stack.pop(0)
show("Popped first item", first_item)
show("Remaining stack", stack)

try:
    stack.pop(100)
except IndexError as error:
    print(f"pop() failure handled: {error}")


# pop() returns the removed object, while remove() returns None.
# pop() is useful when the removed value itself is needed.


# ---------------------------------------------------------------------------
# 9. clear()
# ---------------------------------------------------------------------------

section("9. clear()")

items = [1, 2, 3, 4]
result = items.clear()

show("After clear()", items)
show("Return value of clear()", result)


# ---------------------------------------------------------------------------
# 10. index()
# ---------------------------------------------------------------------------

section("10. index()")

items = ["Python", "C++", "Python", "Java"]

first_python = items.index("Python")
second_python = items.index("Python", first_python + 1)

show("First Python index", first_python)
show("Second Python index", second_python)

try:
    items.index("Rust")
except ValueError as error:
    print(f"index() failure handled: {error}")

# index(value, start, stop) searches only within a range.
show("Python in range", items.index("Python", 1, 4))


# ---------------------------------------------------------------------------
# 11. count()
# ---------------------------------------------------------------------------

section("11. count()")

votes = ["yes", "no", "yes", "yes", "no"]
show("Number of yes values", votes.count("yes"))
show("Number of no values", votes.count("no"))
show("Number of abstain values", votes.count("abstain"))


# ---------------------------------------------------------------------------
# 12. sort()
# ---------------------------------------------------------------------------

section("12. sort()")

numbers = [5, 1, 9, 2, 7]
result = numbers.sort()

show("Sorted numbers", numbers)
show("Return value of sort()", result)

numbers.sort(reverse=True)
show("Descending order", numbers)

words = ["banana", "Apple", "cherry", "apricot"]
words.sort(key=str.lower)
show("Case-insensitive sort", words)

# sorted() is different from list.sort():
# list.sort() mutates the existing list.
# sorted() creates and returns a new list.
original = [3, 1, 2]
sorted_copy = sorted(original)

show("Original after sorted()", original)
show("Result from sorted()", sorted_copy)


# ---------------------------------------------------------------------------
# 13. reverse()
# ---------------------------------------------------------------------------

section("13. reverse()")

items = [1, 2, 3, 4]
result = items.reverse()

show("After reverse()", items)
show("Return value of reverse()", result)

# reversed() produces an iterator and does not mutate the list.
items = [1, 2, 3]
reversed_iterator = reversed(items)

show("Original after reversed()", items)
show("Materialized reversed iterator", list(reversed_iterator))


# ---------------------------------------------------------------------------
# 14. copy()
# ---------------------------------------------------------------------------

section("14. copy()")

original = [10, 20, 30]
copied = original.copy()

copied.append(40)

show("Original", original)
show("Copied", copied)

# Assignment does NOT create a copy.
original = [1, 2, 3]
alias = original
alias.append(4)

show("Original after alias mutation", original)
show("Alias", alias)
print("original is alias:", original is alias)

# copy() creates a new outer list.
original = [1, 2, 3]
copied = original.copy()

print("original is copied:", original is copied)


# ---------------------------------------------------------------------------
# 15. Shallow-copy behavior
# ---------------------------------------------------------------------------

section("15. Shallow Copy and Nested Lists")

original = [[1, 2], [3, 4]]
copied = original.copy()

copied[0].append(99)

show("Original after nested mutation", original)
show("Copied after nested mutation", copied)

# The outer lists differ, but their nested elements are shared.
print("Outer identity:", original is copied)
print("Nested identity:", original[0] is copied[0])


# ---------------------------------------------------------------------------
# 16. Deep copying
# ---------------------------------------------------------------------------

section("16. Deep Copy")

import copy

original = [[1, 2], [3, 4]]
deep_copied = copy.deepcopy(original)

deep_copied[0].append(99)

show("Original", original)
show("Deep copy", deep_copied)
print("Nested identity:", original[0] is deep_copied[0])


# ---------------------------------------------------------------------------
# 17. Membership
# ---------------------------------------------------------------------------

section("17. Membership Testing")

permissions = ["read", "write", "execute"]

print("'read' in permissions:", "read" in permissions)
print("'delete' in permissions:", "delete" in permissions)


# ---------------------------------------------------------------------------
# 18. Concatenation and repetition
# ---------------------------------------------------------------------------

section("18. Concatenation and Repetition")

first = [1, 2]
second = [3, 4]

combined = first + second
repeated = first * 3

show("Concatenated", combined)
show("Repeated", repeated)

# + creates a new list.
# += generally mutates the existing list in place.
values = [1, 2]
values += [3, 4]
show("After +=", values)


# ---------------------------------------------------------------------------
# 19. Iteration
# ---------------------------------------------------------------------------

section("19. Iteration")

servers = ["web-01", "web-02", "database-01"]

for server in servers:
    print("Server:", server)

for index, server in enumerate(servers, start=1):
    print(f"{index}. {server}")


# ---------------------------------------------------------------------------
# 20. List comprehensions
# ---------------------------------------------------------------------------

section("20. List Comprehensions")

numbers = list(range(1, 11))

squares = [number * number for number in numbers]
even_numbers = [number for number in numbers if number % 2 == 0]
labels = [f"item-{number}" for number in numbers]

show("Squares", squares)
show("Even numbers", even_numbers)
show("Labels", labels)

# Nested comprehensions can flatten a matrix.
matrix = [[1, 2], [3, 4], [5, 6]]
flattened = [value for row in matrix for value in row]

show("Flattened matrix", flattened)


# ---------------------------------------------------------------------------
# 21. Sorting complex records
# ---------------------------------------------------------------------------

section("21. Sorting Complex Records")

employees = [
    {"name": "Asha", "salary": 85000},
    {"name": "Rahul", "salary": 65000},
    {"name": "Neha", "salary": 92000},
]

employees.sort(key=lambda employee: employee["salary"])

show("Employees sorted by salary", employees)

employees.sort(key=lambda employee: employee["salary"], reverse=True)

show("Employees sorted by salary descending", employees)


# ---------------------------------------------------------------------------
# 22. Stable sorting
# ---------------------------------------------------------------------------

section("22. Stable Sorting")

students = [
    ("Asha", "A"),
    ("Rahul", "B"),
    ("Neha", "A"),
    ("Vikram", "B"),
]

students.sort(key=lambda student: student[1])

# Python's sort is stable: students with the same key preserve their
# previous relative order.
show("Stable sort result", students)


# ---------------------------------------------------------------------------
# 23. Lists containing different data types
# ---------------------------------------------------------------------------

section("23. Mixed-Type Lists and Sorting Limitations")

mixed = [10, "20", 30]

try:
    mixed.sort()
except TypeError as error:
    print(f"Mixed-type sorting failure handled: {error}")

# A key function can provide a common comparison representation.
mixed = [10, "20", 30, "40"]
mixed.sort(key=str)

show("Mixed values sorted using str key", mixed)


# ---------------------------------------------------------------------------
# 24. Mutation during iteration
# ---------------------------------------------------------------------------

section("24. Avoiding Dangerous Mutation During Iteration")

numbers = [1, 2, 3, 4, 5, 6]

# Removing elements directly from the list being iterated can skip values.
# A safer approach is to build a new list.
even_numbers = [number for number in numbers if number % 2 == 0]

show("Original", numbers)
show("Filtered result", even_numbers)

# Another safe approach is iterating over a copy.
numbers = [1, 2, 3, 4, 5]
for number in numbers.copy():
    if number % 2 == 1:
        numbers.remove(number)

show("After controlled removal", numbers)


# ---------------------------------------------------------------------------
# 25. Functions that mutate lists
# ---------------------------------------------------------------------------

section("25. Functions and List Mutation")

def add_audit_event(events: list[str], event: str) -> None:
    """Mutate the supplied list by adding one event."""
    events.append(event)


audit_events = []
add_audit_event(audit_events, "login")
add_audit_event(audit_events, "file_access")

show("Audit events", audit_events)


def create_uppercase_copy(items: Iterable[str]) -> list[str]:
    """Return a new list without changing the input."""
    return [item.upper() for item in items]


source = ["python", "javascript", "cpp"]
result = create_uppercase_copy(source)

show("Source", source)
show("New result", result)


# ---------------------------------------------------------------------------
# 26. Stack implementation using list
# ---------------------------------------------------------------------------

section("26. List as a Stack")

stack: list[str] = []

stack.append("task-1")
stack.append("task-2")
stack.append("task-3")

show("Stack", stack)

while stack:
    task = stack.pop()
    print("Processing:", task)


# append() + pop() from the end gives efficient stack behavior.


# ---------------------------------------------------------------------------
# 27. Queue considerations
# ---------------------------------------------------------------------------

section("27. Queue Considerations")

# pop(0) requires shifting the remaining elements and can be expensive for
# large queues. collections.deque is normally preferable for queue behavior.
from collections import deque

queue = deque()
queue.append("request-1")
queue.append("request-2")
queue.append("request-3")

while queue:
    request = queue.popleft()
    print("Handling:", request)


# ---------------------------------------------------------------------------
# 28. Deduplication while preserving order
# ---------------------------------------------------------------------------

section("28. Deduplication")

values = ["python", "java", "python", "cpp", "java", "rust"]

# dict preserves insertion order in modern Python.
unique_values = list(dict.fromkeys(values))

show("Original", values)
show("Unique values", unique_values)


# ---------------------------------------------------------------------------
# 29. Filtering and validation
# ---------------------------------------------------------------------------

section("29. Validation")

raw_scores = [95, 87, -5, 101, 72, "unknown", 64]

valid_scores: list[int] = []

for score in raw_scores:
    if isinstance(score, int) and 0 <= score <= 100:
        valid_scores.append(score)

show("Valid scores", valid_scores)


# ---------------------------------------------------------------------------
# 30. Nested list processing
# ---------------------------------------------------------------------------

section("30. Nested Lists")

sales = [
    [1200, 1500, 1100],
    [900, 1800, 1700],
    [2100, 1900, 2200],
]

regional_totals = [sum(region) for region in sales]
total_sales = sum(regional_totals)

show("Regional totals", regional_totals)
show("Total sales", total_sales)


# ---------------------------------------------------------------------------
# 31. Matrix-style access
# ---------------------------------------------------------------------------

section("31. Matrix Access")

matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

for row in matrix:
    print(row)

show("Center value", matrix[1][1])


# ---------------------------------------------------------------------------
# 32. Common mistakes
# ---------------------------------------------------------------------------

section("32. Common Mistakes")

# Mistake 1: expecting append() to return the modified list.
items = [1, 2]
result = items.append(3)

print("append() result is None:", result is None)

# Mistake 2: assigning one list to another and expecting independence.
a = [1, 2]
b = a
b.append(3)

show("a after modifying b", a)

# Correct approach:
a = [1, 2]
b = a.copy()
b.append(3)

show("Independent a", a)
show("Independent b", b)

# Mistake 3: using remove() when an index is intended.
items = ["a", "b", "c"]
removed = items.pop(1)

show("Value removed by index", removed)
show("Remaining items", items)


# ---------------------------------------------------------------------------
# 33. Method comparison
# ---------------------------------------------------------------------------

section("33. Method Comparison")

print("append(value) -> adds one object")
print("extend(iterable) -> adds each element from an iterable")
print("insert(index, value) -> inserts one object at a position")
print("remove(value) -> removes the first matching value")
print("pop(index) -> removes and returns an item")
print("clear() -> removes all items")
print("index(value) -> returns the first matching index")
print("count(value) -> counts matching values")
print("sort() -> sorts the list in place")
print("reverse() -> reverses the list in place")
print("copy() -> creates a shallow copy")


# ---------------------------------------------------------------------------
# 34. Complexity considerations
# ---------------------------------------------------------------------------

section("34. Typical Complexity Considerations")

complexity = {
    "indexing": "O(1) average",
    "append at end": "O(1) amortized",
    "pop at end": "O(1)",
    "insert at beginning": "O(n)",
    "pop at beginning": "O(n)",
    "remove by value": "O(n)",
    "index search": "O(n)",
    "count": "O(n)",
    "membership test": "O(n)",
    "sort": "O(n log n) typical",
    "reverse": "O(n)",
    "copy": "O(n)",
}

for operation, cost in complexity.items():
    print(f"{operation:25} {cost}")


# ---------------------------------------------------------------------------
# 35. Dataclass objects and list methods
# ---------------------------------------------------------------------------

section("35. Lists of Objects")

@dataclass
class Product:
    name: str
    price: float
    quantity: int

    @property
    def inventory_value(self) -> float:
        return self.price * self.quantity


products = [
    Product("Keyboard", 2500, 4),
    Product("Mouse", 1200, 8),
    Product("Monitor", 18000, 3),
]

products.sort(key=lambda product: product.inventory_value, reverse=True)

for product in products:
    print(
        product.name,
        "inventory value =",
        product.inventory_value,
    )


# ---------------------------------------------------------------------------
# 36. Practical inventory example
# ---------------------------------------------------------------------------

section("36. Practical Inventory Processing")

inventory = [
    {"sku": "KB001", "name": "Keyboard", "stock": 12, "price": 2500},
    {"sku": "MS001", "name": "Mouse", "stock": 4, "price": 1200},
    {"sku": "MN001", "name": "Monitor", "stock": 0, "price": 18000},
    {"sku": "HD001", "name": "Hard Drive", "stock": 7, "price": 6500},
]

low_stock = [
    item
    for item in inventory
    if 0 < item["stock"] <= 5
]

out_of_stock = [
    item
    for item in inventory
    if item["stock"] == 0
]

inventory.sort(key=lambda item: item["price"], reverse=True)

show("Low-stock products", low_stock)
show("Out-of-stock products", out_of_stock)
show("Inventory sorted by price", inventory)


# ---------------------------------------------------------------------------
# 37. Safe removal helper
# ---------------------------------------------------------------------------

section("37. Safe Removal Helper")

def remove_first_if_present(items: list[str], value: str) -> bool:
    """
    Remove the first occurrence of value if present.

    Returns:
        True when an element was removed.
        False when the value did not exist.
    """
    if value in items:
        items.remove(value)
        return True
    return False


colors = ["red", "green", "blue"]

print("Removed green:", remove_first_if_present(colors, "green"))
print("Removed purple:", remove_first_if_present(colors, "purple"))
show("Colors", colors)


# ---------------------------------------------------------------------------
# 38. Binary-search-related distinction
# ---------------------------------------------------------------------------

section("38. Linear Search vs Binary Search")

import bisect

sorted_numbers = [10, 20, 30, 40, 50]

# list.index() performs a linear search.
print("Linear search index:", sorted_numbers.index(30))

# bisect can locate an insertion point in a sorted list efficiently.
position = bisect.bisect_left(sorted_numbers, 30)

print("Binary-search insertion position:", position)

# bisect does not replace list.index() for arbitrary unsorted lists.
# The list must remain sorted for meaningful binary-search behavior.


# ---------------------------------------------------------------------------
# 39. Performance experiment
# ---------------------------------------------------------------------------

section("39. Small Performance Experiment")

large_list = list(range(200_000))

start = perf_counter()
large_list.append(200_000)
append_duration = perf_counter() - start

start = perf_counter()
_ = 200_000 in large_list
membership_duration = perf_counter() - start

print(f"append() measurement: {append_duration:.8f} seconds")
print(f"membership measurement: {membership_duration:.8f} seconds")
print(
    "Timing varies by machine, Python implementation, system load, "
    "and hardware."
)


# ---------------------------------------------------------------------------
# 40. Advanced sorting with multiple keys
# ---------------------------------------------------------------------------

section("40. Multiple Sorting Keys")

records = [
    {"department": "IT", "name": "Ravi", "salary": 90000},
    {"department": "HR", "name": "Asha", "salary": 90000},
    {"department": "IT", "name": "Neha", "salary": 75000},
    {"department": "HR", "name": "Vikram", "salary": 70000},
]

records.sort(
    key=lambda record: (
        record["department"],
        -record["salary"],
        record["name"],
    )
)

for record in records:
    print(record)


# ---------------------------------------------------------------------------
# 41. Custom iterable with extend()
# ---------------------------------------------------------------------------

section("41. Custom Iterable")

class NumberGenerator:
    """A simple iterable that yields a sequence of numbers."""

    def __init__(self, start: int, stop: int):
        self.start = start
        self.stop = stop

    def __iter__(self) -> Iterator[int]:
        return iter(range(self.start, self.stop))


values = [100]
values.extend(NumberGenerator(1, 5))

show("After extending from custom iterable", values)


# ---------------------------------------------------------------------------
# 42. Defensive handling of user input
# ---------------------------------------------------------------------------

section("42. Input Validation Pattern")

def parse_positive_integers(text: str) -> list[int]:
    """
    Convert comma-separated input into positive integers.

    Invalid entries are rejected with ValueError.
    """
    if not text.strip():
        raise ValueError("Input cannot be empty.")

    parts = text.split(",")
    numbers: list[int] = []

    for part in parts:
        cleaned = part.strip()

        if not cleaned:
            raise ValueError("Empty item found.")

        try:
            number = int(cleaned)
        except ValueError as error:
            raise ValueError(
                f"Invalid integer: {cleaned!r}"
            ) from error

        if number <= 0:
            raise ValueError(
                f"Expected a positive integer, got {number}."
            )

        numbers.append(number)

    return numbers


for sample in ("10, 20, 30", "5, 0, 8", "10, abc, 20"):
    try:
        print(sample, "->", parse_positive_integers(sample))
    except ValueError as error:
        print(sample, "-> validation error:", error)


# ---------------------------------------------------------------------------
# 43. Testing list behavior
# ---------------------------------------------------------------------------

section("43. Assertions as Simple Tests")

def add_unique(items: list[str], value: str) -> bool:
    """Add value only when it does not already exist."""
    if value in items:
        return False

    items.append(value)
    return True


test_items: list[str] = []

assert add_unique(test_items, "Python") is True
assert add_unique(test_items, "Python") is False
assert test_items == ["Python"]

print("All basic assertions passed.")


# ---------------------------------------------------------------------------
# 44. Practical data pipeline
# ---------------------------------------------------------------------------

section("44. Practical Data Pipeline")

raw_transactions = [
    {"id": "T001", "amount": "1200", "status": "paid"},
    {"id": "T002", "amount": "invalid", "status": "paid"},
    {"id": "T003", "amount": "800", "status": "cancelled"},
    {"id": "T004", "amount": "2500", "status": "paid"},
]

valid_paid_transactions = []

for transaction in raw_transactions:
    if transaction["status"] != "paid":
        continue

    try:
        amount = float(transaction["amount"])
    except ValueError:
        continue

    if amount < 0:
        continue

    valid_paid_transactions.append(
        {
            "id": transaction["id"],
            "amount": amount,
        }
    )

valid_paid_transactions.sort(
    key=lambda transaction: transaction["amount"],
    reverse=True,
)

show("Processed transactions", valid_paid_transactions)


# ---------------------------------------------------------------------------
# 45. Edge cases
# ---------------------------------------------------------------------------

section("45. Important Edge Cases")

empty: list[int] = []

show("Empty list", empty)
show("Empty list slice", empty[:])
show("Count on empty list", empty.count(10))
show("Membership in empty list", 10 in empty)

try:
    empty.pop()
except IndexError as error:
    print("pop() on empty list:", error)

try:
    empty.remove(10)
except ValueError as error:
    print("remove() on empty list:", error)

try:
    empty.index(10)
except ValueError as error:
    print("index() on empty list:", error)


# ---------------------------------------------------------------------------
# 46. List methods versus built-in functions
# ---------------------------------------------------------------------------

section("46. List Methods vs Built-in Functions")

values = [5, 2, 9, 1]

# Method: modifies in place.
method_values = values.copy()
method_values.sort()

# Built-in: returns a new sorted list.
function_values = sorted(values)

show("Method result", method_values)
show("Built-in result", function_values)

print("sum(values):", sum(values))
print("min(values):", min(values))
print("max(values):", max(values))
print("len(values):", len(values))


# ---------------------------------------------------------------------------
# 47. Practical rules
# ---------------------------------------------------------------------------

section("47. Practical Rules")

rules = [
    "Use append() when adding one object.",
    "Use extend() when adding multiple elements from an iterable.",
    "Use insert() when position matters.",
    "Use remove() when you know the value to remove.",
    "Use pop() when you need to remove by position and receive the value.",
    "Use clear() when the entire list should be emptied.",
    "Use index() when you need the first matching position.",
    "Use count() when you need the number of occurrences.",
    "Use sort() when in-place sorting is desired.",
    "Use sorted() when the original sequence should remain unchanged.",
    "Use reverse() for in-place reversal.",
    "Use reversed() when an iterator is preferable.",
    "Use copy() to create a shallow outer-list copy.",
    "Use copy.deepcopy() when independent nested structures are required.",
    "Prefer deque for efficient queue operations.",
]

for number, rule in enumerate(rules, start=1):
    print(f"{number:02}. {rule}")


# ---------------------------------------------------------------------------
# 48. Final integrated demonstration
# ---------------------------------------------------------------------------

section("48. Integrated List-Methods Demonstration")

tasks = [
    "Design database schema",
    "Implement API",
    "Write tests",
]

tasks.append("Deploy application")
tasks.extend(["Monitor service", "Review logs"])
tasks.insert(1, "Create technical specification")
tasks.remove("Write tests")

show("Tasks after modifications", tasks)

completed_task = tasks.pop()
show("Completed task removed", completed_task)

tasks.sort()
show("Tasks alphabetically sorted", tasks)

tasks.reverse()
show("Tasks reversed", tasks)

copied_tasks = tasks.copy()
copied_tasks.append("Archive project")

show("Original tasks", tasks)
show("Copied tasks", copied_tasks)

print("\nStudy file execution completed successfully.")
