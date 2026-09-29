"""
Dictionary Methods: Beginner-to-Advanced Study Script

This standalone script teaches Python dictionary methods through executable
examples, progressing from fundamental dictionary operations to advanced
patterns involving nested dictionaries, grouping, counting, merging,
validation, copying, sorting, caching, serialization, and performance.

Run with:
    python dictionary_methods.py
"""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass, asdict
from time import perf_counter
import json
import math
import random
import string
from typing import Any, Iterable


# ============================================================================
# 1. FUNDAMENTALS
# ============================================================================

def section(title: str) -> None:
    """Print a consistent section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def show(label: str, value: Any) -> None:
    """Print a labeled value."""
    print(f"{label}: {value}")


section("1. Creating Dictionaries")

empty_dictionary = {}
student = {
    "name": "Atul",
    "age": 30,
    "course": "Computer Science",
}

show("Empty dictionary", empty_dictionary)
show("Student dictionary", student)

# Dictionary keys must be hashable. Strings, integers, tuples containing
# hashable values, and many immutable objects can be keys.
mixed_keys = {
    "name": "Atul",
    42: "integer key",
    (1, 2): "tuple key",
}
show("Dictionary with different key types", mixed_keys)

# Lists and dictionaries cannot be keys because they are mutable and
# therefore unhashable.
try:
    invalid = {[1, 2, 3]: "not allowed"}
except TypeError as error:
    show("Unhashable-key error", error)


section("2. Accessing Values")

profile = {
    "name": "Atul",
    "role": "Developer",
    "location": "India",
}

show("Direct access", profile["name"])
show("get() existing key", profile.get("role"))
show("get() missing key", profile.get("salary"))
show("get() with default", profile.get("salary", 0))

# Direct indexing raises KeyError for a missing key.
try:
    print(profile["salary"])
except KeyError as error:
    show("KeyError from []", error)


section("3. keys(), values(), and items()")

inventory = {
    "laptop": 5,
    "monitor": 12,
    "keyboard": 20,
}

show("keys()", inventory.keys())
show("values()", inventory.values())
show("items()", inventory.items())

print("\nIterating over keys:")
for product in inventory:
    print(" ", product)

print("\nIterating over values:")
for quantity in inventory.values():
    print(" ", quantity)

print("\nIterating over key-value pairs:")
for product, quantity in inventory.items():
    print(f"  {product}: {quantity}")


section("4. Adding and Updating Values")

account = {"name": "Atul", "balance": 1000}

account["balance"] = 1250
account["currency"] = "INR"

show("After direct assignment", account)

# update() accepts another mapping or an iterable of key-value pairs.
account.update({"balance": 1500, "status": "active"})
account.update([("verified", True)])

show("After update()", account)

# update() overwrites existing keys and creates missing keys.
account.update(balance=2000, branch="Lucknow")
show("After keyword update", account)


section("5. setdefault()")

settings = {"theme": "dark"}

# Existing key is not overwritten.
existing = settings.setdefault("theme", "light")

# Missing key is inserted with the supplied default.
language = settings.setdefault("language", "English")

show("Existing value returned", existing)
show("New value returned", language)
show("Dictionary after setdefault()", settings)

# setdefault() is useful when building groups.
groups: dict[str, list[str]] = {}

for name, department in [
    ("Atul", "Engineering"),
    ("Priya", "Engineering"),
    ("Ravi", "Finance"),
]:
    groups.setdefault(department, []).append(name)

show("Grouped data", groups)


section("6. pop()")

scores = {
    "Python": 95,
    "JavaScript": 88,
    "C++": 91,
}

python_score = scores.pop("Python")
show("Removed Python score", python_score)
show("After pop()", scores)

# A default prevents KeyError.
missing_score = scores.pop("Rust", 0)
show("Missing score with default", missing_score)

try:
    scores.pop("Java")
except KeyError as error:
    show("pop() missing-key error", error)


section("7. popitem()")

queue = {
    "first": 10,
    "second": 20,
    "third": 30,
}

last_item = queue.popitem()
show("Removed final inserted item", last_item)
show("Remaining dictionary", queue)

# Python dictionaries preserve insertion order. popitem() removes the last
# inserted key-value pair.


section("8. del and clear()")

temporary = {"a": 1, "b": 2, "c": 3}

del temporary["b"]
show("After del", temporary)

temporary.clear()
show("After clear()", temporary)


section("9. Membership Testing")

permissions = {
    "read": True,
    "write": True,
    "delete": False,
}

show("'read' in dictionary", "read" in permissions)
show("'admin' in dictionary", "admin" in permissions)
show("True in values", True in permissions.values())

# "in" checks keys by default.
show("'read' in keys", "read" in permissions.keys())


# ============================================================================
# 2. COPYING AND MUTABILITY
# ============================================================================

section("10. Assignment vs copy()")

original = {"name": "Atul", "skills": ["Python", "SQL"]}

reference = original
shallow_copy = original.copy()
deep_copy = deepcopy(original)

reference["name"] = "Changed Through Reference"
show("Original after reference modification", original)

shallow_copy["name"] = "Shallow Copy"
show("Original after shallow top-level modification", original)

# Nested mutable objects are still shared by a shallow copy.
shallow_copy["skills"].append("Git")
show("Original after nested shallow modification", original)

deep_copy["skills"].append("C++")
show("Original after deep-copy nested modification", original)
show("Deep copy", deep_copy)


section("11. fromkeys()")

fields = ["name", "email", "country"]
blank_record = dict.fromkeys(fields)

show("fromkeys() with None", blank_record)

template = dict.fromkeys(fields, "")
show("fromkeys() with empty string", template)

# Be careful when using a mutable object as the common default:
shared_list = dict.fromkeys(["a", "b"], [])
shared_list["a"].append("value")

show("Mutable fromkeys() result", shared_list)
show("Same list object", shared_list["a"] is shared_list["b"])

# Prefer a comprehension when each key needs its own mutable object.
independent_lists = {key: [] for key in ["a", "b"]}
independent_lists["a"].append("value")
show("Independent mutable defaults", independent_lists)


# ============================================================================
# 3. DICTIONARY COMPREHENSIONS
# ============================================================================

section("12. Dictionary Comprehensions")

squares = {number: number ** 2 for number in range(1, 6)}
show("Squares", squares)

even_squares = {
    number: number ** 2
    for number in range(1, 11)
    if number % 2 == 0
}
show("Even squares", even_squares)

words = ["python", "dictionary", "method"]
word_lengths = {word: len(word) for word in words}
show("Word lengths", word_lengths)


section("13. Transforming a Dictionary")

prices = {
    "laptop": 75000,
    "phone": 45000,
    "tablet": 30000,
}

discounted_prices = {
    product: round(price * 0.90)
    for product, price in prices.items()
}

show("Discounted prices", discounted_prices)


section("14. Filtering a Dictionary")

high_value = {
    product: price
    for product, price in prices.items()
    if price >= 45000
}

show("Products priced at least 45000", high_value)


# ============================================================================
# 4. MERGING DICTIONARIES
# ============================================================================

section("15. Merging with update()")

base_config = {
    "host": "localhost",
    "port": 8000,
    "debug": False,
}

production_config = {
    "host": "api.example.com",
    "debug": False,
}

merged_update = base_config.copy()
merged_update.update(production_config)

show("Merged with update()", merged_update)


section("16. Merging with | and |= Operators")

defaults = {"timeout": 30, "retries": 3}
custom = {"timeout": 60, "cache": True}

merged = defaults | custom
show("defaults | custom", merged)

defaults_copy = defaults.copy()
defaults_copy |= custom
show("defaults_copy after |=", defaults_copy)

# When duplicate keys exist, the right-hand dictionary wins.
show("Conflict resolution", {"x": 1} | {"x": 2})


section("17. Dictionary Unpacking")

identity = {"name": "Atul"}
professional = {"role": "Developer"}

combined = {**identity, **professional}
show("Unpacked dictionaries", combined)

# Later entries override earlier entries.
combined_conflict = {**{"role": "Student"}, **{"role": "Developer"}}
show("Unpacking conflict", combined_conflict)


# ============================================================================
# 5. NESTED DICTIONARIES
# ============================================================================

section("18. Nested Dictionaries")

company = {
    "name": "Example Technologies",
    "address": {
        "city": "Lucknow",
        "country": "India",
    },
    "departments": {
        "engineering": {
            "employees": 40,
            "budget": 5000000,
        },
        "finance": {
            "employees": 12,
            "budget": 1800000,
        },
    },
}

show("Company city", company["address"]["city"])
show(
    "Engineering budget",
    company["departments"]["engineering"]["budget"],
)


section("19. Safe Nested Access")

def nested_get(data: dict[str, Any], path: Iterable[str], default: Any = None) -> Any:
    """
    Safely retrieve a nested value.

    This is useful when the structure is not guaranteed to contain every key.
    """
    current: Any = data

    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]

    return current


show(
    "Existing nested value",
    nested_get(company, ["departments", "finance", "employees"]),
)
show(
    "Missing nested value",
    nested_get(company, ["departments", "legal", "employees"], 0),
)


# ============================================================================
# 6. COUNTING, GROUPING, AND INDEXING
# ============================================================================

section("20. Counting with a Normal Dictionary")

text = "mississippi"
frequency: dict[str, int] = {}

for character in text:
    frequency[character] = frequency.get(character, 0) + 1

show("Character frequency", frequency)


section("21. Counting with setdefault()")

transactions = [
    ("food", 500),
    ("travel", 1200),
    ("food", 300),
    ("utilities", 900),
    ("travel", 700),
]

totals: dict[str, int] = {}

for category, amount in transactions:
    totals[category] = totals.get(category, 0) + amount

show("Category totals", totals)


section("22. Counter")

counter = Counter(text)

show("Counter", counter)
show("Most common characters", counter.most_common(3))

# Counter supports arithmetic-like operations for multisets.
first = Counter("aabbcc")
second = Counter("bccddd")

show("Counter addition", first + second)
show("Counter intersection", first & second)
show("Counter union", first | second)


section("23. defaultdict")

department_members: defaultdict[str, list[str]] = defaultdict(list)

records = [
    ("Engineering", "Atul"),
    ("Engineering", "Priya"),
    ("Finance", "Ravi"),
]

for department, name in records:
    department_members[department].append(name)

show("defaultdict groups", dict(department_members))

word_count: defaultdict[str, int] = defaultdict(int)

for word in ["python", "python", "sql", "python"]:
    word_count[word] += 1

show("defaultdict counter", dict(word_count))


# ============================================================================
# 7. SORTING
# ============================================================================

section("24. Sorting Dictionary Items")

marks = {
    "Atul": 92,
    "Priya": 87,
    "Ravi": 95,
    "Neha": 81,
}

by_name = dict(sorted(marks.items()))
by_score = dict(sorted(marks.items(), key=lambda item: item[1]))
by_score_descending = dict(
    sorted(marks.items(), key=lambda item: item[1], reverse=True)
)

show("Sorted by name", by_name)
show("Sorted by score", by_score)
show("Sorted by descending score", by_score_descending)


section("25. Stable Sorting and Tie Handling")

results = {
    "A": 90,
    "B": 85,
    "C": 90,
    "D": 75,
}

ranked = sorted(
    results.items(),
    key=lambda item: (-item[1], item[0]),
)

show("Deterministically ranked results", ranked)


# ============================================================================
# 8. VALIDATION AND DATA CLEANING
# ============================================================================

section("26. Dictionary Validation")

def validate_user_record(record: dict[str, Any]) -> list[str]:
    """Return validation errors without mutating the input."""
    errors: list[str] = []

    required_fields = {"name", "email", "age"}

    missing_fields = required_fields - record.keys()

    for field in sorted(missing_fields):
        errors.append(f"Missing required field: {field}")

    if "name" in record and not isinstance(record["name"], str):
        errors.append("name must be a string")

    if "email" in record and (
        not isinstance(record["email"], str)
        or "@" not in record["email"]
    ):
        errors.append("email must contain @")

    if "age" in record and (
        not isinstance(record["age"], int)
        or isinstance(record["age"], bool)
        or record["age"] < 0
    ):
        errors.append("age must be a non-negative integer")

    return errors


valid_user = {
    "name": "Atul",
    "email": "atul@example.com",
    "age": 30,
}

invalid_user = {
    "name": 123,
    "email": "invalid",
    "age": -4,
}

show("Valid record errors", validate_user_record(valid_user))
show("Invalid record errors", validate_user_record(invalid_user))


section("27. Filtering Untrusted Dictionary Data")

raw_payload = {
    "name": "Atul",
    "email": "atul@example.com",
    "age": 30,
    "unexpected_admin_flag": True,
}

allowed_fields = {"name", "email", "age"}

clean_payload = {
    key: value
    for key, value in raw_payload.items()
    if key in allowed_fields
}

show("Raw payload", raw_payload)
show("Allowlisted payload", clean_payload)


# ============================================================================
# 9. FUNCTIONS THAT ACCEPT DICTIONARIES
# ============================================================================

section("28. **kwargs and Dictionary Arguments")

def create_user(**attributes: Any) -> dict[str, Any]:
    """Receive keyword arguments as a dictionary."""
    return {
        "id": 1001,
        **attributes,
    }


new_user = create_user(
    name="Atul",
    role="Developer",
    active=True,
)

show("Created user", new_user)

user_attributes = {
    "name": "Priya",
    "role": "Analyst",
    "active": True,
}

show("Dictionary unpacked into **kwargs", create_user(**user_attributes))


section("29. Dictionary Unpacking into Function Parameters")

def calculate_invoice(subtotal: float, tax_rate: float, discount: float = 0.0) -> float:
    taxable = max(subtotal - discount, 0)
    return taxable * (1 + tax_rate)


invoice_parameters = {
    "subtotal": 10000,
    "tax_rate": 0.18,
    "discount": 500,
}

invoice_total = calculate_invoice(**invoice_parameters)
show("Invoice total", round(invoice_total, 2))


# ============================================================================
# 10. RECURSIVE DICTIONARY UTILITIES
# ============================================================================

section("30. Recursive Dictionary Transformation")

def flatten_dictionary(
    data: dict[str, Any],
    prefix: str = "",
    separator: str = ".",
) -> dict[str, Any]:
    """
    Flatten nested dictionaries.

    Example:
        {"a": {"b": 1}} -> {"a.b": 1}

    Lists are treated as leaf values in this implementation.
    """
    flattened: dict[str, Any] = {}

    for key, value in data.items():
        current_key = f"{prefix}{separator}{key}" if prefix else str(key)

        if isinstance(value, dict):
            flattened.update(
                flatten_dictionary(value, current_key, separator)
            )
        else:
            flattened[current_key] = value

    return flattened


flattened_company = flatten_dictionary(company)
show("Flattened company dictionary", flattened_company)


section("31. Recursive Dictionary Merge")

def deep_merge(
    left: dict[str, Any],
    right: dict[str, Any],
) -> dict[str, Any]:
    """
    Recursively merge two dictionaries.

    If both values are dictionaries, merge them recursively.
    Otherwise, the right-hand value replaces the left-hand value.
    """
    result = deepcopy(left)

    for key, right_value in right.items():
        left_value = result.get(key)

        if isinstance(left_value, dict) and isinstance(right_value, dict):
            result[key] = deep_merge(left_value, right_value)
        else:
            result[key] = deepcopy(right_value)

    return result


configuration_a = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "pool": 5,
    },
    "logging": {
        "level": "INFO",
    },
}

configuration_b = {
    "database": {
        "host": "production.example.com",
        "pool": 20,
    },
    "logging": {
        "format": "json",
    },
}

show(
    "Deep merge result",
    deep_merge(configuration_a, configuration_b),
)


# ============================================================================
# 11. DICTIONARY VIEWS
# ============================================================================

section("32. Dynamic Dictionary Views")

data = {"a": 1, "b": 2}

keys_view = data.keys()
items_view = data.items()

data["c"] = 3

# Dictionary views reflect subsequent changes to the dictionary.
show("Dynamic keys view", list(keys_view))
show("Dynamic items view", list(items_view))

# Converting to list creates a snapshot at that moment.
keys_snapshot = list(data.keys())
data["d"] = 4

show("Keys snapshot", keys_snapshot)
show("Current keys", list(data.keys()))


# ============================================================================
# 12. DICTIONARY KEY SEMANTICS
# ============================================================================

section("33. Key Equality and Hashing")

key_demo = {
    1: "integer",
    True: "boolean overwrites integer because 1 == True",
}

show("Integer and boolean key interaction", key_demo)

# 1 and True compare equal and have equal hashes.
show("1 == True", 1 == True)
show("hash(1) == hash(True)", hash(1) == hash(True))


section("34. Mutable Objects Cannot Normally Be Dictionary Keys")

try:
    mutable_key = [1, 2]
    example = {mutable_key: "value"}
except TypeError as error:
    show("Mutable key error", error)

# A tuple can be a key if every element inside it is hashable.
valid_tuple_key = {(1, "python"): "valid tuple key"}
show("Hashable tuple key", valid_tuple_key)


# ============================================================================
# 13. JSON AND DICTIONARIES
# ============================================================================

section("35. JSON Serialization")

api_response = {
    "status": "success",
    "user": {
        "id": 1001,
        "name": "Atul",
    },
    "roles": ["developer", "researcher"],
}

json_text = json.dumps(api_response, indent=2)
show("JSON text", json_text)

restored = json.loads(json_text)

show("Restored Python object", restored)
show("Restored object type", type(restored).__name__)


section("36. JSON Serialization Constraints")

# JSON object keys are normally strings after serialization.
integer_key_dictionary = {1: "one", 2: "two"}

json_integer_keys = json.dumps(integer_key_dictionary)
restored_integer_keys = json.loads(json_integer_keys)

show("Original integer-key dictionary", integer_key_dictionary)
show("JSON representation", json_integer_keys)
show("Restored keys", restored_integer_keys)

# JSON cannot directly serialize arbitrary Python objects such as sets.
try:
    json.dumps({"values": {1, 2, 3}})
except TypeError as error:
    show("JSON unsupported-type error", error)


# ============================================================================
# 14. CACHING
# ============================================================================

section("37. Dictionary-Based Memoization")

def fibonacci_without_cache(number: int) -> int:
    if number <= 1:
        return number
    return (
        fibonacci_without_cache(number - 1)
        + fibonacci_without_cache(number - 2)
    )


def fibonacci_with_cache(
    number: int,
    cache: dict[int, int] | None = None,
) -> int:
    if cache is None:
        cache = {0: 0, 1: 1}

    if number not in cache:
        cache[number] = (
            fibonacci_with_cache(number - 1, cache)
            + fibonacci_with_cache(number - 2, cache)
        )

    return cache[number]


show("Fibonacci 10", fibonacci_with_cache(10))


# ============================================================================
# 15. LRU-STYLE CACHE USING ORDERED DICTIONARY
# ============================================================================

section("38. Practical Cache with functools.lru_cache")

from functools import lru_cache


@lru_cache(maxsize=128)
def expensive_square(number: int) -> int:
    """Demonstrate built-in caching backed by dictionary-like semantics."""
    return number * number


for value in [10, 10, 20, 10, 20]:
    print(f"square({value}) = {expensive_square(value)}")

show("Cache statistics", expensive_square.cache_info())


# ============================================================================
# 16. DATACLASS TO DICTIONARY
# ============================================================================

section("39. Dataclass Conversion")

@dataclass
class Product:
    product_id: int
    name: str
    price: float
    active: bool = True


product = Product(
    product_id=101,
    name="Laptop",
    price=75000,
)

product_dictionary = asdict(product)

show("Dataclass", product)
show("Dataclass converted with asdict()", product_dictionary)


# ============================================================================
# 17. PRACTICAL INVENTORY SYSTEM
# ============================================================================

section("40. Practical Dictionary-Based Inventory")

class Inventory:
    """
    Small inventory system demonstrating dictionaries as an in-memory
    application data structure.
    """

    def __init__(self) -> None:
        self._products: dict[str, dict[str, Any]] = {}

    def add_product(
        self,
        product_id: str,
        name: str,
        price: float,
        quantity: int,
    ) -> None:
        if not product_id:
            raise ValueError("product_id cannot be empty")

        if price < 0:
            raise ValueError("price cannot be negative")

        if quantity < 0:
            raise ValueError("quantity cannot be negative")

        if product_id in self._products:
            raise ValueError(f"Product already exists: {product_id}")

        self._products[product_id] = {
            "name": name,
            "price": price,
            "quantity": quantity,
        }

    def restock(self, product_id: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("restock quantity must be positive")

        product = self._products.get(product_id)

        if product is None:
            raise KeyError(f"Unknown product: {product_id}")

        product["quantity"] += quantity

    def sell(self, product_id: str, quantity: int) -> float:
        if quantity <= 0:
            raise ValueError("sale quantity must be positive")

        product = self._products.get(product_id)

        if product is None:
            raise KeyError(f"Unknown product: {product_id}")

        if product["quantity"] < quantity:
            raise ValueError("Insufficient stock")

        product["quantity"] -= quantity

        return product["price"] * quantity

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        product = self._products.get(product_id)

        if product is None:
            return None

        return product.copy()

    def low_stock(self, threshold: int = 5) -> dict[str, dict[str, Any]]:
        return {
            product_id: product.copy()
            for product_id, product in self._products.items()
            if product["quantity"] <= threshold
        }

    def total_value(self) -> float:
        return sum(
            product["price"] * product["quantity"]
            for product in self._products.values()
        )

    def snapshot(self) -> dict[str, dict[str, Any]]:
        return deepcopy(self._products)


inventory = Inventory()

inventory.add_product("P001", "Laptop", 75000, 10)
inventory.add_product("P002", "Keyboard", 2500, 3)
inventory.add_product("P003", "Monitor", 18000, 7)

inventory.restock("P002", 4)
sale_value = inventory.sell("P001", 2)

show("Sale value", sale_value)
show("Laptop", inventory.get_product("P001"))
show("Low-stock products", inventory.low_stock())
show("Inventory value", inventory.total_value())
show("Inventory snapshot", inventory.snapshot())


# ============================================================================
# 18. EDGE CASES
# ============================================================================

section("41. Important Edge Cases")

empty: dict[str, int] = {}

show("Empty get()", empty.get("missing"))
show("Empty keys", list(empty.keys()))
show("Empty values", list(empty.values()))
show("Empty items", list(empty.items()))

try:
    _ = empty["missing"]
except KeyError:
    print("Direct access to a missing key raises KeyError.")

try:
    empty.pop("missing")
except KeyError:
    print("pop() without a default raises KeyError.")

show("pop() with default", empty.pop("missing", None))


section("42. Modifying a Dictionary During Iteration")

mutable = {"a": 1, "b": 2, "c": 3}

try:
    for key in mutable:
        if key == "b":
            del mutable[key]
except RuntimeError as error:
    show("Unsafe mutation during iteration", error)

# Safe approach: iterate over a snapshot.
mutable = {"a": 1, "b": 2, "c": 3}

for key in list(mutable):
    if key == "b":
        del mutable[key]

show("Safely modified dictionary", mutable)


section("43. Duplicate Dictionary Keys")

duplicates = {
    "language": "Python",
    "language": "JavaScript",
}

# The later literal entry replaces the earlier one.
show("Duplicate-key result", duplicates)


# ============================================================================
# 19. PERFORMANCE
# ============================================================================

section("44. Dictionary Lookup Performance")

large_dictionary = {number: number * number for number in range(1_000_000)}
large_list = list(large_dictionary)

target = 999_999

start = perf_counter()
dictionary_result = target in large_dictionary
dictionary_time = perf_counter() - start

start = perf_counter()
list_result = target in large_list
list_time = perf_counter() - start

show("Dictionary membership result", dictionary_result)
show("List membership result", list_result)
show("Dictionary lookup time", dictionary_time)
show("List lookup time", list_time)

print(
    "\nDictionary average membership lookup is approximately O(1), "
    "while list membership is O(n)."
)


# ============================================================================
# 20. ADVANCED GROUPING
# ============================================================================

section("45. Grouping Objects with Dictionaries")

employees = [
    {"name": "Atul", "department": "Engineering", "salary": 90000},
    {"name": "Priya", "department": "Engineering", "salary": 95000},
    {"name": "Ravi", "department": "Finance", "salary": 80000},
    {"name": "Neha", "department": "Finance", "salary": 85000},
]

grouped_employees: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

for employee in employees:
    grouped_employees[employee["department"]].append(employee)

show("Employees grouped by department", dict(grouped_employees))


section("46. Aggregation with Dictionaries")

salary_totals: defaultdict[str, int] = defaultdict(int)
salary_counts: defaultdict[str, int] = defaultdict(int)

for employee in employees:
    department = employee["department"]
    salary_totals[department] += employee["salary"]
    salary_counts[department] += 1

average_salary = {
    department: salary_totals[department] / salary_counts[department]
    for department in salary_totals
}

show("Salary totals", dict(salary_totals))
show("Salary counts", dict(salary_counts))
show("Average salaries", average_salary)


# ============================================================================
# 21. INVERTING DICTIONARIES
# ============================================================================

section("47. Inverting a One-to-One Dictionary")

country_codes = {
    "India": "IN",
    "United States": "US",
    "Japan": "JP",
}

inverted = {code: country for country, code in country_codes.items()}

show("Original mapping", country_codes)
show("Inverted mapping", inverted)


section("48. Inverting a One-to-Many Dictionary")

department_map = {
    "Atul": "Engineering",
    "Priya": "Engineering",
    "Ravi": "Finance",
    "Neha": "Finance",
}

inverted_groups: defaultdict[str, list[str]] = defaultdict(list)

for employee, department in department_map.items():
    inverted_groups[department].append(employee)

show("Inverted grouped mapping", dict(inverted_groups))


# ============================================================================
# 22. DICTIONARY-BASED GRAPH
# ============================================================================

section("49. Graph Representation Using Dictionaries")

graph: dict[str, list[str]] = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C", "E"],
    "E": ["D"],
}

show("Graph adjacency dictionary", graph)


def breadth_first_search(
    graph_data: dict[str, list[str]],
    start: str,
) -> list[str]:
    """Perform breadth-first traversal using a dictionary adjacency list."""
    if start not in graph_data:
        return []

    visited = {start}
    queue = [start]
    order: list[str] = []

    while queue:
        current = queue.pop(0)
        order.append(current)

        for neighbor in graph_data.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order


show("BFS order", breadth_first_search(graph, "A"))


# ============================================================================
# 23. ADVANCED DICTIONARY PATTERNS
# ============================================================================

section("50. Dispatch Dictionary")

def add_numbers(a: float, b: float) -> float:
    return a + b


def subtract_numbers(a: float, b: float) -> float:
    return a - b


def multiply_numbers(a: float, b: float) -> float:
    return a * b


def divide_numbers(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


operations = {
    "+": add_numbers,
    "-": subtract_numbers,
    "*": multiply_numbers,
    "/": divide_numbers,
}


def calculate(expression_operator: str, a: float, b: float) -> float:
    operation = operations.get(expression_operator)

    if operation is None:
        raise ValueError(f"Unsupported operator: {expression_operator}")

    return operation(a, b)


for operator in operations:
    show(
        f"10 {operator} 5",
        calculate(operator, 10, 5),
    )


section("51. Configuration with Defaults")

DEFAULT_CONFIGURATION = {
    "host": "localhost",
    "port": 8000,
    "workers": 2,
    "debug": False,
    "timeout": 30,
}


def build_configuration(
    supplied: dict[str, Any],
) -> dict[str, Any]:
    configuration = DEFAULT_CONFIGURATION.copy()
    configuration.update(supplied)
    return configuration


show(
    "Application configuration",
    build_configuration(
        {
            "port": 9000,
            "workers": 4,
        }
    ),
)


# ============================================================================
# 24. SECURITY-RELATED DICTIONARY PRACTICES
# ============================================================================

section("52. Security-Oriented Dictionary Practices")

# Never trust arbitrary keys from external input when accessing sensitive
# configuration. An allowlist prevents unexpected fields from being accepted.
request_data = {
    "username": "atul",
    "role": "user",
    "is_admin": True,
    "debug": True,
}

allowed_request_fields = {"username", "role"}

safe_request = {
    key: value
    for key, value in request_data.items()
    if key in allowed_request_fields
}

show("Incoming request", request_data)
show("Allowlisted request", safe_request)

# Dictionary contents can contain secrets, so avoid printing sensitive
# dictionaries in real production logs.
credentials = {
    "username": "application",
    "password": "REDACTED",
}

show("Safe credential representation", {
    "username": credentials["username"],
    "password": "***",
})


# ============================================================================
# 25. TESTABLE FUNCTIONS
# ============================================================================

section("53. Assertions and Behavioral Tests")

def merge_settings(
    defaults: dict[str, Any],
    overrides: dict[str, Any],
) -> dict[str, Any]:
    result = defaults.copy()
    result.update(overrides)
    return result


assert merge_settings({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}
assert merge_settings({"a": 1}, {"a": 9}) == {"a": 9}
assert merge_settings({}, {"a": 1}) == {"a": 1}

print("All dictionary merge assertions passed.")


# ============================================================================
# 26. COMPREHENSIVE MINI PROJECT
# ============================================================================

section("54. Mini Project: Student Grade Management")

class GradeBook:
    """Dictionary-backed grade management system."""

    def __init__(self) -> None:
        self.students: dict[str, dict[str, Any]] = {}

    def add_student(self, student_id: str, name: str) -> None:
        if student_id in self.students:
            raise ValueError("Student ID already exists")

        self.students[student_id] = {
            "name": name,
            "grades": {},
        }

    def add_grade(
        self,
        student_id: str,
        subject: str,
        grade: float,
    ) -> None:
        student = self.students.get(student_id)

        if student is None:
            raise KeyError("Student does not exist")

        if not 0 <= grade <= 100:
            raise ValueError("Grade must be between 0 and 100")

        student["grades"][subject] = grade

    def average(self, student_id: str) -> float | None:
        student = self.students.get(student_id)

        if student is None:
            raise KeyError("Student does not exist")

        grades = student["grades"]

        if not grades:
            return None

        return sum(grades.values()) / len(grades)

    def report(self) -> dict[str, dict[str, Any]]:
        report: dict[str, dict[str, Any]] = {}

        for student_id, student in self.students.items():
            average = self.average(student_id)

            report[student_id] = {
                "name": student["name"],
                "grades": student["grades"].copy(),
                "average": None if average is None else round(average, 2),
            }

        return report


gradebook = GradeBook()

gradebook.add_student("S001", "Atul")
gradebook.add_student("S002", "Priya")

gradebook.add_grade("S001", "Python", 95)
gradebook.add_grade("S001", "SQL", 90)
gradebook.add_grade("S001", "C++", 88)

gradebook.add_grade("S002", "Python", 91)
gradebook.add_grade("S002", "SQL", 94)
gradebook.add_grade("S002", "C++", 89)

show("Gradebook report", gradebook.report())


# ============================================================================
# 27. PRACTICAL RULES AND REFERENCE
# ============================================================================

section("55. Dictionary Method Quick Reference")

method_reference = {
    "dict.get(key, default)": "Read safely without KeyError",
    "dict.keys()": "Dynamic view of keys",
    "dict.values()": "Dynamic view of values",
    "dict.items()": "Dynamic view of key-value pairs",
    "dict.update(...)": "Insert or overwrite multiple entries",
    "dict.setdefault(key, default)": "Read existing value or insert default",
    "dict.pop(key, default)": "Remove and return a key's value",
    "dict.popitem()": "Remove and return the last inserted pair",
    "dict.clear()": "Remove all entries",
    "dict.copy()": "Create a shallow copy",
    "dict.fromkeys(...)": "Create dictionary from keys",
}

for method, purpose in method_reference.items():
    print(f"{method:<42} -> {purpose}")


section("56. Complexity Reference")

complexity_reference = {
    "Average key lookup": "O(1)",
    "Average key insertion": "O(1)",
    "Average key deletion": "O(1)",
    "Membership test": "O(1) average",
    "Iteration": "O(n)",
    "Sorting dictionary items": "O(n log n)",
    "Copying dictionary": "O(n)",
}

for operation, complexity in complexity_reference.items():
    print(f"{operation:<32}: {complexity}")


# ============================================================================
# 28. FINAL INTEGRATED EXAMPLE
# ============================================================================

section("57. Integrated Data Processing Example")

orders = [
    {
        "order_id": "O1001",
        "customer": "Atul",
        "category": "Electronics",
        "amount": 75000,
        "status": "completed",
    },
    {
        "order_id": "O1002",
        "customer": "Priya",
        "category": "Books",
        "amount": 2500,
        "status": "completed",
    },
    {
        "order_id": "O1003",
        "customer": "Ravi",
        "category": "Electronics",
        "amount": 45000,
        "status": "cancelled",
    },
    {
        "order_id": "O1004",
        "customer": "Neha",
        "category": "Books",
        "amount": 3500,
        "status": "completed",
    },
]

completed_orders = {
    order["order_id"]: order
    for order in orders
    if order["status"] == "completed"
}

category_sales: defaultdict[str, float] = defaultdict(float)

for order in completed_orders.values():
    category_sales[order["category"]] += order["amount"]

customer_sales: defaultdict[str, float] = defaultdict(float)

for order in completed_orders.values():
    customer_sales[order["customer"]] += order["amount"]

largest_order = max(
    completed_orders.values(),
    key=lambda order: order["amount"],
    default=None,
)

analytics = {
    "completed_order_count": len(completed_orders),
    "category_sales": dict(category_sales),
    "customer_sales": dict(customer_sales),
    "largest_order": largest_order,
}

show("Integrated analytics", analytics)


section("58. Completed Study Demonstration")

print(
    """
The examples above demonstrate dictionary creation, access, mutation,
views, copying, merging, comprehensions, grouping, counting, sorting,
validation, nested structures, serialization, caching, dispatch tables,
graphs, configuration, security-oriented filtering, and application-style
data modeling.

Key practical rules:
1. Use [] when a missing key should be an error.
2. Use get() when a missing key is expected.
3. Use update() for explicit bulk mutation.
4. Use | for creating a merged dictionary without mutating either input.
5. Use copy() carefully because it is shallow.
6. Use deepcopy() when nested mutable structures must be independent.
7. Use setdefault() or defaultdict when building grouped structures.
8. Use dictionary comprehensions for clear transformations and filtering.
9. Treat dictionary keys as hash-based identifiers and understand equality.
10. Validate external dictionary data before trusting it.
"""
)
