"""
DICTIONARIES IN PYTHON
======================

A comprehensive executable study file covering Python dictionaries from
absolute beginner concepts through advanced implementation techniques.

Run:
    python dictionaries.py
"""

from __future__ import annotations

from collections import Counter, defaultdict, OrderedDict, ChainMap, UserDict
from dataclasses import dataclass
from functools import lru_cache
from timeit import timeit
from typing import Any, Hashable, Iterable


# ============================================================================
# 1. FUNDAMENTALS
# ============================================================================

def section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    print("\n--- " + title + " ---")


section("1. DICTIONARY FUNDAMENTALS")

# A dictionary stores key-value pairs.
# Keys identify values. Keys must be hashable; values can be almost anything.
student = {
    "name": "Atul",
    "age": 25,
    "course": "Computer Science",
}

print("Dictionary:", student)
print("Type:", type(student))
print("Name:", student["name"])

# Dictionary keys are unique. Assigning an existing key replaces its value.
student["age"] = 26
student["city"] = "Prayagraj"

print("After update:", student)

# Different key types can be used when they are hashable.
mixed_keys = {
    "text": "value",
    42: "integer key",
    (1, 2): "tuple key",
    True: "boolean key",
}
print("Mixed keys:", mixed_keys)

# bool and int have the same hash/equality relationship.
# Therefore True and 1 refer to the same dictionary key.
boolean_integer_collision = {True: "first", 1: "second"}
print("True/1 key collision:", boolean_integer_collision)


# ============================================================================
# 2. CREATING DICTIONARIES
# ============================================================================

section("2. CREATING DICTIONARIES")

empty_a = {}
empty_b = dict()

print("Empty dictionaries:", empty_a, empty_b)

person = dict(name="Atul", age=25, active=True)
print("dict() with keyword arguments:", person)

pairs = [
    ("name", "Atul"),
    ("age", 25),
    ("active", True),
]
from_pairs = dict(pairs)
print("dict() from pairs:", from_pairs)

# fromkeys() creates a dictionary using the same initial value.
subjects = ["Python", "JavaScript", "C++"]
marks = dict.fromkeys(subjects, 0)
print("fromkeys:", marks)

# Be careful with mutable values in fromkeys().
shared_lists = dict.fromkeys(["a", "b"], [])
shared_lists["a"].append(10)
print("Shared mutable value:", shared_lists)
print("Both keys reference the same list:", shared_lists["a"] is shared_lists["b"])

# Safer construction when every key needs its own list.
independent_lists = {key: [] for key in ["a", "b"]}
independent_lists["a"].append(10)
print("Independent lists:", independent_lists)


# ============================================================================
# 3. ACCESSING VALUES
# ============================================================================

section("3. ACCESSING VALUES")

profile = {
    "name": "Atul",
    "age": 25,
    "skills": ["Python", "SQL", "Git"],
}

print("Bracket access:", profile["name"])

# Accessing a missing key with [] raises KeyError.
try:
    print(profile["country"])
except KeyError as error:
    print("Missing key with []:", error)

# get() avoids KeyError and returns None or a supplied default.
print("get() missing key:", profile.get("country"))
print("get() with default:", profile.get("country", "India"))


# ============================================================================
# 4. ADDING, UPDATING, AND REMOVING
# ============================================================================

section("4. MODIFYING DICTIONARIES")

account = {
    "name": "Atul",
    "balance": 1000,
}

account["currency"] = "INR"
account["balance"] += 500

print("After direct modifications:", account)

account.update({"balance": 2000, "status": "active"})
print("After update():", account)

# | merges dictionaries and creates a new dictionary.
limits = {"daily": 10000, "monthly": 100000}
preferences = {"currency": "INR", "language": "English"}
combined = limits | preferences
print("Merged dictionary:", combined)

# |= updates an existing dictionary in place.
preferences |= {"theme": "dark"}
print("In-place merge:", preferences)

removed_value = account.pop("status")
print("pop() removed:", removed_value)
print("After pop():", account)

default_removed = account.pop("missing", "not found")
print("pop() missing key with default:", default_removed)

last_item = account.popitem()
print("popitem() removed:", last_item)
print("Account:", account)

account.clear()
print("After clear():", account)

# del removes a key. A missing key raises KeyError.
example = {"a": 1, "b": 2}
del example["a"]
print("After del:", example)


# ============================================================================
# 5. MEMBERSHIP AND LENGTH
# ============================================================================

section("5. MEMBERSHIP, LENGTH, AND TRUTHINESS")

data = {"name": "Atul", "age": 25}

print("'name' in data:", "name" in data)
print("'Atul' in data:", "Atul" in data)
print("'Atul' in data.values():", "Atul" in data.values())
print("Length:", len(data))
print("Empty dictionary is false:", bool({}))
print("Non-empty dictionary is true:", bool(data))


# ============================================================================
# 6. KEYS, VALUES, AND ITEMS
# ============================================================================

section("6. KEYS, VALUES, AND ITEMS")

inventory = {
    "laptop": 5,
    "keyboard": 12,
    "mouse": 20,
}

print("Keys:", inventory.keys())
print("Values:", inventory.values())
print("Items:", inventory.items())

# These are dynamic view objects.
keys_view = inventory.keys()
inventory["monitor"] = 7
print("Dynamic keys view:", list(keys_view))

for key in inventory:
    print("Key:", key)

for value in inventory.values():
    print("Value:", value)

for key, value in inventory.items():
    print(f"{key} -> {value}")


# ============================================================================
# 7. DICTIONARY ITERATION
# ============================================================================

section("7. ITERATION PATTERNS")

scores = {
    "Alice": 85,
    "Bob": 92,
    "Carol": 78,
    "David": 95,
}

print("Students scoring >= 90:")
for name, score in scores.items():
    if score >= 90:
        print(name, score)

print("Upper-case names:")
for name in scores:
    print(name.upper())

# Modifying dictionary size during iteration is unsafe.
# Build a list of keys first when deletion is necessary.
scores_copy = scores.copy()
for name in list(scores_copy):
    if scores_copy[name] < 80:
        del scores_copy[name]

print("After safe deletion:", scores_copy)


# ============================================================================
# 8. DICTIONARY COMPREHENSIONS
# ============================================================================

section("8. DICTIONARY COMPREHENSIONS")

squares = {number: number * number for number in range(1, 6)}
print("Squares:", squares)

even_squares = {
    number: number * number
    for number in range(1, 11)
    if number % 2 == 0
}
print("Even squares:", even_squares)

names = ["alice", "bob", "carol"]
name_lengths = {name: len(name) for name in names}
print("Name lengths:", name_lengths)

# Transform an existing dictionary.
prices = {"apple": 100, "banana": 40, "orange": 80}
discounted = {
    product: price * 0.9
    for product, price in prices.items()
}
print("Discounted prices:", discounted)


# ============================================================================
# 9. HASHABILITY AND VALID KEYS
# ============================================================================

section("9. HASHABILITY AND DICTIONARY KEYS")

# Hashable immutable objects can normally be dictionary keys.
valid_key_examples = {
    "string": "yes",
    10: "yes",
    3.14: "yes",
    (1, 2): "yes",
    frozenset({1, 2}): "yes",
}
print("Hashable keys:", valid_key_examples)

# Lists are mutable and therefore unhashable.
try:
    invalid = {[1, 2]: "value"}
except TypeError as error:
    print("Unhashable list key:", error)

# A tuple is hashable only when all of its elements are hashable.
try:
    invalid_tuple = {(1, [2]): "value"}
except TypeError as error:
    print("Tuple containing list:", error)

# Custom objects can be keys if they have suitable hash/equality behavior.
class UserKey:
    def __init__(self, user_id: int):
        self.user_id = user_id

    def __hash__(self) -> int:
        return hash(self.user_id)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, UserKey) and self.user_id == other.user_id


user_dictionary = {UserKey(101): "Administrator"}
print("Custom object lookup:", user_dictionary[UserKey(101)])


# ============================================================================
# 10. NESTED DICTIONARIES
# ============================================================================

section("10. NESTED DICTIONARIES")

employees = {
    101: {
        "name": "Alice",
        "department": "Engineering",
        "salary": 90000,
    },
    102: {
        "name": "Bob",
        "department": "Security",
        "salary": 95000,
    },
}

print("Nested access:", employees[101]["department"])

for employee_id, details in employees.items():
    print(employee_id, details["name"], details["salary"])

# Safe nested access with get().
country = employees.get(999, {}).get("country", "Unknown")
print("Safe nested lookup:", country)


# ============================================================================
# 11. COPYING AND ALIASING
# ============================================================================

section("11. COPYING AND ALIASING")

original = {
    "name": "Atul",
    "skills": ["Python", "SQL"],
}

alias = original
alias["name"] = "Changed"

print("Original after alias modification:", original)

shallow = original.copy()
shallow["name"] = "Shallow Copy"
print("Original after scalar shallow-copy change:", original)
print("Shallow:", shallow)

# A shallow copy does not recursively copy nested mutable objects.
shallow["skills"].append("Git")
print("Original nested list:", original["skills"])

import copy

deep = copy.deepcopy(original)
deep["skills"].append("Docker")
print("Original after deep copy:", original)
print("Deep copy:", deep)


# ============================================================================
# 12. SORTING
# ============================================================================

section("12. SORTING DICTIONARIES")

scores = {
    "Alice": 85,
    "Bob": 92,
    "Carol": 78,
    "David": 95,
}

by_name = dict(sorted(scores.items()))
by_score = dict(sorted(scores.items(), key=lambda item: item[1]))
by_score_descending = dict(
    sorted(scores.items(), key=lambda item: item[1], reverse=True)
)

print("By name:", by_name)
print("By score:", by_score)
print("By descending score:", by_score_descending)


# ============================================================================
# 13. FREQUENCY COUNTING
# ============================================================================

section("13. FREQUENCY COUNTING")

text = "dictionary data structures are useful data structures"
words = text.lower().split()

frequency: dict[str, int] = {}
for word in words:
    frequency[word] = frequency.get(word, 0) + 1

print("Manual frequency:", frequency)

counter = Counter(words)
print("Counter:", counter)
print("Most common:", counter.most_common(3))


# ============================================================================
# 14. GROUPING WITH defaultdict
# ============================================================================

section("14. defaultdict")

students_by_department: defaultdict[str, list[str]] = defaultdict(list)

records = [
    ("Engineering", "Alice"),
    ("Security", "Bob"),
    ("Engineering", "Carol"),
    ("Security", "David"),
]

for department, student_name in records:
    students_by_department[department].append(student_name)

print("Grouped students:", dict(students_by_department))

# defaultdict automatically creates the missing value.
word_lengths: defaultdict[int, list[str]] = defaultdict(list)
for word in ["cat", "dog", "python", "sql"]:
    word_lengths[len(word)].append(word)

print("Grouped by length:", dict(word_lengths))


# ============================================================================
# 15. SETDEFAULT
# ============================================================================

section("15. setdefault()")

groups: dict[str, list[str]] = {}

for department, student_name in records:
    groups.setdefault(department, []).append(student_name)

print("Grouping with setdefault:", groups)


# ============================================================================
# 16. DEFAULTDICT VS SETDEFAULT
# ============================================================================

section("16. GROUPING DESIGN COMPARISON")

print(
    "defaultdict is convenient when repeated missing-key initialization is a "
    "central part of the algorithm."
)
print(
    "setdefault is useful when only occasional initialization is required."
)


# ============================================================================
# 17. ORDERED DICTIONARIES
# ============================================================================

section("17. ORDERED DICTIONARY")

# Regular dict preserves insertion order in modern Python.
regular = {"a": 1, "b": 2, "c": 3}
print("Regular dict order:", list(regular))

ordered = OrderedDict([("a", 1), ("b", 2), ("c", 3)])
ordered.move_to_end("a")
print("OrderedDict after move_to_end:", ordered)

# OrderedDict still provides specialized operations useful in some designs.


# ============================================================================
# 18. CHAINMAP
# ============================================================================

section("18. ChainMap")

defaults = {"theme": "dark", "language": "English", "timeout": 30}
environment = {"timeout": 60}
command_line = {"theme": "light"}

configuration = ChainMap(command_line, environment, defaults)

print("Theme:", configuration["theme"])
print("Timeout:", configuration["timeout"])
print("Language:", configuration["language"])

# Lookup searches maps from left to right.


# ============================================================================
# 19. USERDICT
# ============================================================================

section("19. CUSTOM DICTIONARY BEHAVIOR")

class CaseInsensitiveDictionary(UserDict):
    """Dictionary that treats string keys without regard to case."""

    @staticmethod
    def normalize(key: Hashable) -> Hashable:
        return key.lower() if isinstance(key, str) else key

    def __setitem__(self, key: Hashable, value: Any) -> None:
        super().__setitem__(self.normalize(key), value)

    def __getitem__(self, key: Hashable) -> Any:
        return super().__getitem__(self.normalize(key))

    def __contains__(self, key: object) -> bool:
        normalized = self.normalize(key)  # type: ignore[arg-type]
        return super().__contains__(normalized)


case_insensitive = CaseInsensitiveDictionary()
case_insensitive["Name"] = "Atul"
print("Case-insensitive lookup:", case_insensitive["name"])
print("Membership:", "NAME" in case_insensitive)


# ============================================================================
# 20. DICTIONARY MERGING
# ============================================================================

section("20. MERGING AND CONFLICTS")

left = {"a": 1, "b": 2}
right = {"b": 20, "c": 3}

merged = left | right
print("Merged:", merged)

# The right-hand value wins on duplicate keys.
print("Conflict result for b:", merged["b"])

left |= right
print("Left after |=:", left)

# Older Python versions commonly used {**left, **right}.
legacy_style_merge = {**{"a": 1}, **{"a": 2, "b": 3}}
print("Unpacking merge:", legacy_style_merge)


# ============================================================================
# 21. UNPACKING
# ============================================================================

section("21. DICTIONARY UNPACKING")

base = {"name": "Atul", "role": "developer"}
extra = {"location": "India"}

combined = {**base, **extra}
print("Combined:", combined)

def show_profile(name: str, role: str) -> None:
    print(f"Profile: {name} / {role}")

show_profile(**base)


# ============================================================================
# 22. DICTIONARY AS A LOOKUP TABLE
# ============================================================================

section("22. LOOKUP TABLES")

operations = {
    "add": lambda a, b: a + b,
    "subtract": lambda a, b: a - b,
    "multiply": lambda a, b: a * b,
    "divide": lambda a, b: a / b if b != 0 else None,
}

for operation_name in operations:
    print(operation_name, operations[operation_name](10, 2))

# A dictionary can replace a long if/elif chain when operations are keyed.


# ============================================================================
# 23. VALIDATION
# ============================================================================

section("23. VALIDATING DICTIONARY DATA")

required_fields = {"name", "email", "age"}

candidate = {
    "name": "Alice",
    "email": "alice@example.com",
    "age": 30,
}

missing_fields = required_fields - candidate.keys()
unexpected_fields = candidate.keys() - required_fields

print("Missing fields:", missing_fields)
print("Unexpected fields:", unexpected_fields)

if not missing_fields and not unexpected_fields:
    print("Schema keys are valid.")


def validate_user(data: dict[str, Any]) -> list[str]:
    """Validate a simple user record and return all detected problems."""
    errors: list[str] = []

    required = {"name", "email", "age"}
    missing = required - data.keys()
    unexpected = data.keys() - required

    if missing:
        errors.append(f"Missing fields: {sorted(missing)}")
    if unexpected:
        errors.append(f"Unexpected fields: {sorted(unexpected)}")

    if "name" in data and not isinstance(data["name"], str):
        errors.append("name must be a string")

    if "email" in data and (
        not isinstance(data["email"], str) or "@" not in data["email"]
    ):
        errors.append("email must contain @")

    if "age" in data and (
        not isinstance(data["age"], int) or isinstance(data["age"], bool)
    ):
        errors.append("age must be an integer")

    return errors


print("Valid record:", validate_user(candidate))
print(
    "Invalid record:",
    validate_user({"name": 10, "email": "wrong", "extra": True}),
)


# ============================================================================
# 24. DICTIONARY OF OBJECTS
# ============================================================================

section("24. DICTIONARY OF OBJECTS")

@dataclass
class Product:
    product_id: int
    name: str
    price: float
    stock: int

    def available(self) -> bool:
        return self.stock > 0


products = {
    101: Product(101, "Laptop", 75000, 5),
    102: Product(102, "Keyboard", 2500, 0),
}

for product_id, product in products.items():
    print(product_id, product.name, product.available())


# ============================================================================
# 25. DICTIONARY OF DICTIONARIES AS AN IN-MEMORY DATABASE
# ============================================================================

section("25. IN-MEMORY DATABASE")

database: dict[int, dict[str, Any]] = {
    1: {"name": "Alice", "department": "Engineering", "salary": 90000},
    2: {"name": "Bob", "department": "Security", "salary": 95000},
}

def find_employees(
    records: dict[int, dict[str, Any]],
    department: str,
) -> dict[int, dict[str, Any]]:
    return {
        employee_id: employee
        for employee_id, employee in records.items()
        if employee.get("department") == department
    }


print("Engineering employees:", find_employees(database, "Engineering"))


# ============================================================================
# 26. RECURSIVE DICTIONARY TRAVERSAL
# ============================================================================

section("26. RECURSIVE NESTED DICTIONARIES")

nested_data: dict[str, Any] = {
    "application": {
        "database": {
            "host": "localhost",
            "port": 5432,
        },
        "logging": {
            "level": "INFO",
        },
    }
}


def flatten_dictionary(
    data: dict[str, Any],
    prefix: str = "",
) -> dict[str, Any]:
    """Flatten nested dictionaries using dot-separated paths."""
    result: dict[str, Any] = {}

    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else str(key)

        if isinstance(value, dict):
            result.update(flatten_dictionary(value, path))
        else:
            result[path] = value

    return result


flat = flatten_dictionary(nested_data)
print("Flattened:", flat)


def unflatten_dictionary(flat_data: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct nested dictionaries from dotted paths."""
    result: dict[str, Any] = {}

    for path, value in flat_data.items():
        current = result
        parts = path.split(".")

        for part in parts[:-1]:
            existing = current.get(part)
            if existing is None:
                current[part] = {}
            elif not isinstance(existing, dict):
                raise ValueError(
                    f"Path conflict at {part!r} while processing {path!r}"
                )
            current = current[part]

        final_key = parts[-1]
        if final_key in current and isinstance(current[final_key], dict):
            raise ValueError(f"Leaf/path conflict at {path!r}")

        current[final_key] = value

    return result


print("Unflattened:", unflatten_dictionary(flat))


# ============================================================================
# 27. RECURSIVE SEARCH
# ============================================================================

section("27. SEARCHING NESTED DICTIONARIES")

def find_key_recursive(
    value: Any,
    target_key: str,
    path: tuple[str, ...] = (),
) -> list[tuple[str, ...]]:
    """Return all paths where target_key occurs in nested dict structures."""
    found: list[tuple[str, ...]] = []

    if isinstance(value, dict):
        for key, child in value.items():
            current_path = path + (str(key),)

            if key == target_key:
                found.append(current_path)

            found.extend(find_key_recursive(child, target_key, current_path))

    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(
                find_key_recursive(child, target_key, path + (str(index),))
            )

    return found


search_data = {
    "user": {"name": "Alice", "address": {"city": "Delhi"}},
    "admin": {"name": "Bob", "address": {"city": "Mumbai"}},
}

print("Paths containing 'city':", find_key_recursive(search_data, "city"))


# ============================================================================
# 28. JSON-LIKE STRUCTURES
# ============================================================================

section("28. DICTIONARIES AND JSON")

import json

configuration = {
    "application": "DictionaryLab",
    "version": 1,
    "features": ["lookup", "validation", "analytics"],
    "database": {
        "host": "localhost",
        "port": 5432,
    },
}

json_text = json.dumps(configuration, indent=2)
print("Serialized JSON:")
print(json_text)

decoded = json.loads(json_text)
print("Decoded type:", type(decoded))
print("Decoded application:", decoded["application"])


# ============================================================================
# 29. SERIALIZATION EDGE CASES
# ============================================================================

section("29. SERIALIZATION EDGE CASES")

non_json_value = {
    "created": __import__("datetime").datetime.now(),
}

try:
    json.dumps(non_json_value)
except TypeError as error:
    print("Datetime JSON error:", error)

# default=str is convenient but converts values to strings, which may lose
# type information. Production systems should use an explicit serialization
# policy when type preservation matters.
print(
    "Explicit fallback serialization:",
    json.dumps(non_json_value, default=str),
)


# ============================================================================
# 30. IMMUTABILITY AND DICTIONARY VIEWS
# ============================================================================

section("30. READ-ONLY MAPPING VIEWS")

from types import MappingProxyType

mutable_settings = {"timeout": 30, "retries": 3}
read_only_settings = MappingProxyType(mutable_settings)

print("Read-only view:", dict(read_only_settings))

try:
    read_only_settings["timeout"] = 60
except TypeError as error:
    print("Cannot modify MappingProxyType:", error)

# The view reflects changes to the underlying dictionary.
mutable_settings["timeout"] = 60
print("Updated read-only view:", read_only_settings["timeout"])


# ============================================================================
# 31. CUSTOM MAPPING USING PROTOCOL
# ============================================================================

section("31. CUSTOM MAPPING")

from collections.abc import Iterator, Mapping


class EnvironmentMapping(Mapping[str, str]):
    """Read-only mapping backed by a selected environment snapshot."""

    def __init__(self, source: dict[str, str]):
        self._source = dict(source)

    def __getitem__(self, key: str) -> str:
        return self._source[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._source)

    def __len__(self) -> int:
        return len(self._source)


environment_mapping = EnvironmentMapping(
    {"APP_ENV": "production", "LOG_LEVEL": "INFO"}
)

print("Custom mapping:", dict(environment_mapping))
print("LOG_LEVEL:", environment_mapping["LOG_LEVEL"])


# ============================================================================
# 32. LRU CACHE USING A DICTIONARY
# ============================================================================

section("32. DICTIONARY-BASED CACHE")

class SimpleLRUCache:
    """
    Small LRU cache.

    dict preserves insertion order. Moving a key to the end makes it the
    most recently used item. Evicting the first key removes the least
    recently used item.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._data: dict[Hashable, Any] = {}

    def get(self, key: Hashable) -> Any | None:
        if key not in self._data:
            return None

        value = self._data.pop(key)
        self._data[key] = value
        return value

    def put(self, key: Hashable, value: Any) -> None:
        if key in self._data:
            self._data.pop(key)

        self._data[key] = value

        if len(self._data) > self.capacity:
            oldest_key = next(iter(self._data))
            del self._data[oldest_key]

    def __repr__(self) -> str:
        return repr(self._data)


cache = SimpleLRUCache(2)
cache.put("A", 100)
cache.put("B", 200)
print("Initial cache:", cache)
print("Read A:", cache.get("A"))
cache.put("C", 300)
print("After inserting C:", cache)


# ============================================================================
# 33. MEMOIZATION
# ============================================================================

section("33. MEMOIZATION")

def fibonacci_plain(number: int) -> int:
    if number < 0:
        raise ValueError("number must not be negative")
    if number <= 1:
        return number
    return fibonacci_plain(number - 1) + fibonacci_plain(number - 2)


memo: dict[int, int] = {0: 0, 1: 1}


def fibonacci_memoized(number: int) -> int:
    if number < 0:
        raise ValueError("number must not be negative")

    if number not in memo:
        memo[number] = (
            fibonacci_memoized(number - 1)
            + fibonacci_memoized(number - 2)
        )

    return memo[number]


print("Memoized Fibonacci:", fibonacci_memoized(30))

# functools.lru_cache internally provides memoization semantics.
@lru_cache(maxsize=None)
def fibonacci_cached(number: int) -> int:
    if number <= 1:
        return number
    return fibonacci_cached(number - 1) + fibonacci_cached(number - 2)


print("lru_cache Fibonacci:", fibonacci_cached(30))


# ============================================================================
# 34. GRAPH REPRESENTATION
# ============================================================================

section("34. DICTIONARIES FOR GRAPHS")

graph: dict[str, list[str]] = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C"],
}

print("Graph adjacency list:", graph)


def breadth_first_search(
    graph_data: dict[str, list[str]],
    start: str,
) -> list[str]:
    if start not in graph_data:
        raise KeyError(f"Unknown start node: {start}")

    queue = [start]
    visited = {start}
    result: list[str] = []

    while queue:
        current = queue.pop(0)
        result.append(current)

        for neighbor in graph_data.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return result


print("BFS:", breadth_first_search(graph, "A"))


# ============================================================================
# 35. WEIGHTED GRAPH AND DIJKSTRA
# ============================================================================

section("35. DICTIONARY-BASED DIJKSTRA")

weighted_graph: dict[str, dict[str, int]] = {
    "A": {"B": 4, "C": 2},
    "B": {"C": 1, "D": 5},
    "C": {"B": 1, "D": 8, "E": 10},
    "D": {"E": 2},
    "E": {},
}


def dijkstra(
    graph_data: dict[str, dict[str, int]],
    source: str,
) -> dict[str, float]:
    if source not in graph_data:
        raise KeyError(source)

    distances = {node: float("inf") for node in graph_data}
    distances[source] = 0

    unvisited = set(graph_data)

    while unvisited:
        current = min(unvisited, key=distances.get)
        unvisited.remove(current)

        if distances[current] == float("inf"):
            break

        for neighbor, weight in graph_data[current].items():
            if weight < 0:
                raise ValueError("Dijkstra requires non-negative edge weights")

            new_distance = distances[current] + weight

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance

    return distances


print("Shortest distances:", dijkstra(weighted_graph, "A"))


# ============================================================================
# 36. DICTIONARY-BASED INDEX
# ============================================================================

section("36. INVERTED INDEX")

documents = {
    1: "python dictionaries are efficient",
    2: "python supports many data structures",
    3: "dictionaries support fast lookup",
}


def build_inverted_index(
    document_store: dict[int, str],
) -> dict[str, set[int]]:
    index: defaultdict[str, set[int]] = defaultdict(set)

    for document_id, content in document_store.items():
        for word in content.lower().split():
            index[word].add(document_id)

    return dict(index)


inverted_index = build_inverted_index(documents)
print("Documents containing 'python':", inverted_index.get("python", set()))
print("Documents containing 'lookup':", inverted_index.get("lookup", set()))


# ============================================================================
# 37. EDGE CASES
# ============================================================================

section("37. IMPORTANT EDGE CASES")

edge_cases = {
    "empty": {},
    "zero": 0,
    "none": None,
    "false": False,
    "empty_string": "",
}

print("Dictionary values may be None:", edge_cases["none"])
print("Zero is a valid value:", edge_cases["zero"])

# Use `key in dictionary` to distinguish a missing key from a key whose value
# happens to be None.
data_with_none = {"result": None}

if "result" in data_with_none:
    print("Key exists even though value is None.")

print("get() cannot distinguish these without a sentinel:")
print({"result": None}.get("result"))
print({}.get("result"))

sentinel = object()
value = {}.get("result", sentinel)

if value is sentinel:
    print("The key is genuinely absent.")


# ============================================================================
# 38. MUTATION DURING ITERATION
# ============================================================================

section("38. MUTATION DURING ITERATION")

unsafe = {"a": 1, "b": 2, "c": 3}

try:
    for key in unsafe:
        if key == "b":
            del unsafe[key]
except RuntimeError as error:
    print("Mutation error:", error)

safe = {"a": 1, "b": 2, "c": 3}
for key in list(safe):
    if key == "b":
        del safe[key]

print("Safe mutation:", safe)


# ============================================================================
# 39. DICTIONARY INVARIANTS
# ============================================================================

section("39. DICTIONARY INVARIANTS")

# A dictionary cannot contain two distinct equal keys simultaneously.
duplicate_keys = {"x": 1, "x": 2}
print("Duplicate literal key result:", duplicate_keys)

# Equality and hashing must agree for dictionary keys:
# if a == b, hash(a) must equal hash(b).
print("hash('abc'):", hash("abc"))

# Hash values should not be persisted as permanent identifiers because Python
# intentionally randomizes some hashes between processes.


# ============================================================================
# 40. PERFORMANCE
# ============================================================================

section("40. PERFORMANCE CONSIDERATIONS")

large_dictionary = {number: number for number in range(100_000)}
large_list = list(range(100_000))
target = 99_999

dictionary_lookup_time = timeit(
    lambda: large_dictionary[target],
    number=100_000,
)

list_membership_time = timeit(
    lambda: target in large_list,
    number=100,
)

print(f"100,000 dictionary lookups: {dictionary_lookup_time:.6f} seconds")
print(f"100 list membership scans: {list_membership_time:.6f} seconds")

print(
    "Average dictionary lookup is designed for O(1) behavior, while a "
    "linear list membership scan is O(n)."
)


# ============================================================================
# 41. COLLISIONS AND HASH TABLE CONCEPTS
# ============================================================================

section("41. HASH TABLE CONCEPTS")

print(
    "Python dictionaries are hash-table-based mappings. A key is hashed to "
    "help locate its storage position."
)
print(
    "Hash collisions are possible: different keys can produce the same "
    "hash-related placement. The implementation resolves collisions."
)
print(
    "The exact internal layout is an implementation detail and should not "
    "be relied upon by application code."
)


# ============================================================================
# 42. SECURITY CONSIDERATIONS
# ============================================================================

section("42. SECURITY CONSIDERATIONS")

print(
    "Dictionary keys can come from untrusted input, so applications should "
    "validate expected keys and value types."
)
print(
    "Avoid blindly merging untrusted dictionaries into security-sensitive "
    "configuration, because an attacker-controlled key can override a "
    "trusted setting."
)

trusted_configuration = {
    "debug": False,
    "authentication_required": True,
}

untrusted_configuration = {
    "debug": True,
}

# Explicit allow-listing prevents arbitrary configuration overrides.
allowed_configuration_keys = {"language"}

safe_updates = {
    key: value
    for key, value in untrusted_configuration.items()
    if key in allowed_configuration_keys
}

trusted_configuration.update(safe_updates)
print("Protected configuration:", trusted_configuration)


# ============================================================================
# 43. CONFIGURATION PRECEDENCE
# ============================================================================

section("43. CONFIGURATION PRECEDENCE")

defaults = {
    "host": "localhost",
    "port": 8000,
    "debug": False,
}

file_config = {
    "port": 8080,
}

runtime_config = {
    "debug": True,
}

final_config = defaults | file_config | runtime_config

print("Defaults:", defaults)
print("File config:", file_config)
print("Runtime config:", runtime_config)
print("Final configuration:", final_config)


# ============================================================================
# 44. TRANSACTION-LIKE UPDATE
# ============================================================================

section("44. ATOMIC-STYLE APPLICATION UPDATE")

account = {
    "balance": 10_000,
    "status": "active",
}


def apply_balance_change(
    account_data: dict[str, Any],
    amount: float,
) -> dict[str, Any]:
    """
    Validate changes before mutating the original dictionary.

    The function returns a new dictionary, which makes it easier for callers
    to reject invalid changes without partially modifying the source.
    """
    proposed = account_data.copy()
    new_balance = proposed["balance"] + amount

    if new_balance < 0:
        raise ValueError("Insufficient funds")

    proposed["balance"] = new_balance
    return proposed


try:
    account = apply_balance_change(account, -2000)
    print("Successful account update:", account)
except ValueError as error:
    print("Rejected update:", error)

try:
    account = apply_balance_change(account, -20_000)
except ValueError as error:
    print("Rejected overdraft:", error)


# ============================================================================
# 45. TESTING DICTIONARY LOGIC
# ============================================================================

section("45. ASSERTION-BASED TESTS")

def word_frequency(words: Iterable[str]) -> dict[str, int]:
    result: dict[str, int] = {}

    for word in words:
        normalized = word.lower()
        result[normalized] = result.get(normalized, 0) + 1

    return result


assert word_frequency(["Python", "python"]) == {"python": 2}
assert word_frequency([]) == {}
assert word_frequency(["a", "b", "a"]) == {"a": 2, "b": 1}

print("Dictionary function assertions passed.")


# ============================================================================
# 46. DICTIONARY COMPARISON
# ============================================================================

section("46. COMPARISON")

first = {"a": 1, "b": 2}
second = {"b": 2, "a": 1}
third = {"a": 1, "b": 3}

print("first == second:", first == second)
print("first == third:", first == third)

# Dictionary equality does not depend on insertion order.
# Ordering is relevant when iterating, but not for ordinary equality.


# ============================================================================
# 47. SHALLOW VS DEEP STRUCTURAL COMPARISON
# ============================================================================

section("47. STRUCTURAL NESTING")

nested_a = {"config": {"timeout": 30}}
nested_b = {"config": {"timeout": 30}}

print("Nested dictionaries equal:", nested_a == nested_b)
print("Same outer object:", nested_a is nested_b)
print("Same inner object:", nested_a["config"] is nested_b["config"])


# ============================================================================
# 48. PRODUCTION DESIGN GUIDELINES
# ============================================================================

section("48. PRODUCTION DESIGN GUIDELINES")

guidelines = {
    "key_design": "Choose stable, meaningful, hashable keys.",
    "validation": "Validate external dictionary data before use.",
    "mutation": "Prefer controlled mutation and clear ownership.",
    "performance": "Use dictionaries when key-based lookup is the natural operation.",
    "security": "Do not blindly trust configuration keys from external input.",
    "testing": "Test missing keys, empty input, duplicate keys, and invalid values.",
    "typing": "Use type annotations for complex dictionary structures.",
}

for topic, rule in guidelines.items():
    print(f"{topic}: {rule}")


# ============================================================================
# 49. ADVANCED TYPE ANNOTATIONS
# ============================================================================

section("49. TYPE ANNOTATIONS")

from typing import TypedDict, NotRequired


class UserRecord(TypedDict):
    name: str
    email: str
    age: int
    phone: NotRequired[str]


typed_user: UserRecord = {
    "name": "Alice",
    "email": "alice@example.com",
    "age": 30,
}

print("TypedDict runtime object:", typed_user)

# TypedDict primarily helps static type checkers. It does not automatically
# enforce the schema at runtime.


# ============================================================================
# 50. DICTIONARY WITH GENERIC FUNCTIONS
# ============================================================================

section("50. GENERIC DICTIONARY UTILITIES")

K = Any
V = Any


def invert_mapping(mapping: dict[K, V]) -> dict[V, K]:
    """
    Reverse keys and values.

    This is safe only when values are unique and hashable.
    """
    inverted: dict[V, K] = {}

    for key, value in mapping.items():
        if not isinstance(value, Hashable):
            raise TypeError(f"Value {value!r} is not hashable")
        if value in inverted:
            raise ValueError(f"Duplicate value cannot be inverted: {value!r}")
        inverted[value] = key

    return inverted


print("Inverted:", invert_mapping({"a": 1, "b": 2}))

try:
    print(invert_mapping({"a": 1, "b": 1}))
except ValueError as error:
    print("Invert error:", error)


# ============================================================================
# 51. TOP-K FREQUENCIES
# ============================================================================

section("51. TOP-K ANALYTICS")

def top_k_frequencies(
    values: Iterable[Hashable],
    k: int,
) -> list[tuple[Hashable, int]]:
    if k < 0:
        raise ValueError("k must not be negative")

    counter = Counter(values)
    return counter.most_common(k)


print(
    "Top frequencies:",
    top_k_frequencies(["a", "b", "a", "c", "a", "b"], 2),
)


# ============================================================================
# 52. DICTIONARY-BASED STATE MACHINE
# ============================================================================

section("52. STATE MACHINE")

transitions: dict[str, dict[str, str]] = {
    "locked": {
        "unlock": "unlocked",
    },
    "unlocked": {
        "lock": "locked",
        "open": "open",
    },
    "open": {
        "close": "unlocked",
    },
}


def transition_state(
    state: str,
    event: str,
) -> str:
    try:
        return transitions[state][event]
    except KeyError:
        raise ValueError(
            f"Invalid transition: state={state!r}, event={event!r}"
        ) from None


state = "locked"

for event in ["unlock", "open", "close", "lock"]:
    state = transition_state(state, event)
    print(event, "->", state)


# ============================================================================
# 53. DICTIONARY-BASED DISPATCH WITH VALIDATION
# ============================================================================

section("53. DISPATCH TABLE")

def safe_divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b


math_dispatch = {
    "add": lambda a, b: a + b,
    "subtract": lambda a, b: a - b,
    "multiply": lambda a, b: a * b,
    "divide": safe_divide,
}


def execute_operation(
    operation: str,
    a: float,
    b: float,
) -> float:
    function = math_dispatch.get(operation)

    if function is None:
        raise ValueError(f"Unsupported operation: {operation}")

    return function(a, b)


print("Dispatch result:", execute_operation("multiply", 6, 7))

try:
    execute_operation("divide", 10, 0)
except ZeroDivisionError as error:
    print("Dispatch error:", error)


# ============================================================================
# 54. MEMORY AND DESIGN TRADE-OFFS
# ============================================================================

section("54. MEMORY AND DESIGN TRADE-OFFS")

print(
    "Dictionaries provide fast average-case key lookup but generally use "
    "more memory than compact sequential structures."
)
print(
    "If the problem is naturally positional, a list may be more appropriate."
)
print(
    "If only unique membership is required without associated values, a set "
    "may communicate the design more clearly."
)


# ============================================================================
# 55. DICTIONARY VS LIST VS SET
# ============================================================================

section("55. DATA STRUCTURE COMPARISON")

comparison = {
    "dictionary": {
        "primary_operation": "key -> value lookup",
        "duplicates": "keys unique",
        "typical_lookup": "O(1) average",
    },
    "list": {
        "primary_operation": "ordered positional storage",
        "duplicates": "allowed",
        "membership": "O(n) typical",
    },
    "set": {
        "primary_operation": "unique membership",
        "duplicates": "not stored",
        "membership": "O(1) average",
    },
}

for structure, properties in comparison.items():
    print(structure, properties)


# ============================================================================
# 56. PRACTICAL MINI PROJECT: SALES ANALYTICS
# ============================================================================

section("56. MINI PROJECT: SALES ANALYTICS")

sales = [
    {"product": "Laptop", "category": "Electronics", "quantity": 2, "price": 75000},
    {"product": "Mouse", "category": "Electronics", "quantity": 5, "price": 1200},
    {"product": "Chair", "category": "Furniture", "quantity": 3, "price": 8000},
    {"product": "Laptop", "category": "Electronics", "quantity": 1, "price": 75000},
]


def sales_analytics(
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    product_revenue: defaultdict[str, float] = defaultdict(float)
    category_revenue: defaultdict[str, float] = defaultdict(float)
    product_quantity: defaultdict[str, int] = defaultdict(int)

    for record in records:
        quantity = record["quantity"]
        price = record["price"]
        revenue = quantity * price

        product = record["product"]
        category = record["category"]

        product_revenue[product] += revenue
        category_revenue[category] += revenue
        product_quantity[product] += quantity

    return {
        "product_revenue": dict(product_revenue),
        "category_revenue": dict(category_revenue),
        "product_quantity": dict(product_quantity),
    }


analytics = sales_analytics(sales)

print("Product revenue:", analytics["product_revenue"])
print("Category revenue:", analytics["category_revenue"])
print("Product quantities:", analytics["product_quantity"])


# ============================================================================
# 57. PRACTICAL MINI PROJECT: ROLE-BASED ACCESS
# ============================================================================

section("57. MINI PROJECT: ROLE-BASED ACCESS")

permissions = {
    "admin": {"read", "write", "delete"},
    "editor": {"read", "write"},
    "viewer": {"read"},
}


def is_authorized(
    role: str,
    permission: str,
) -> bool:
    return permission in permissions.get(role, set())


for role in ["admin", "editor", "viewer", "unknown"]:
    print(
        role,
        "read=",
        is_authorized(role, "read"),
        "delete=",
        is_authorized(role, "delete"),
    )


# ============================================================================
# 58. PRACTICAL MINI PROJECT: CACHE WITH EXPIRATION
# ============================================================================

section("58. CACHE WITH EXPIRATION")

import time


class ExpiringCache:
    def __init__(self, default_ttl_seconds: float):
        if default_ttl_seconds <= 0:
            raise ValueError("TTL must be positive")

        self.default_ttl_seconds = default_ttl_seconds
        self._values: dict[Hashable, tuple[Any, float]] = {}

    def set(
        self,
        key: Hashable,
        value: Any,
        ttl_seconds: float | None = None,
    ) -> None:
        ttl = (
            self.default_ttl_seconds
            if ttl_seconds is None
            else ttl_seconds
        )

        if ttl <= 0:
            raise ValueError("TTL must be positive")

        self._values[key] = (value, time.monotonic() + ttl)

    def get(self, key: Hashable) -> Any | None:
        item = self._values.get(key)

        if item is None:
            return None

        value, expiration = item

        if time.monotonic() >= expiration:
            del self._values[key]
            return None

        return value


expiring_cache = ExpiringCache(1)
expiring_cache.set("session", "ACTIVE")
print("Cache value:", expiring_cache.get("session"))


# ============================================================================
# 59. FINAL CHECKLIST
# ============================================================================

section("59. DICTIONARY STUDY CHECKLIST")

checklist = [
    "Create dictionaries with literals and dict().",
    "Understand unique hashable keys.",
    "Read values with [] and get().",
    "Add, update, and remove entries.",
    "Iterate over keys, values, and items.",
    "Use dictionary comprehensions.",
    "Understand shallow versus deep copying.",
    "Use defaultdict and Counter appropriately.",
    "Merge dictionaries with | and |=.",
    "Work with nested dictionaries.",
    "Serialize dictionary data as JSON.",
    "Build lookup tables and dispatch tables.",
    "Use dictionaries for indexes and graphs.",
    "Understand average-case O(1) lookup.",
    "Validate external dictionary data.",
    "Consider security when merging untrusted data.",
    "Use type annotations for complex mappings.",
    "Design dictionary-backed caches and state machines.",
]

for index, item in enumerate(checklist, start=1):
    print(f"{index:02d}. {item}")


section("60. COMPLETED")

print("Dictionary study script completed successfully.")
print("All demonstrations above are executable standard-library Python.")
