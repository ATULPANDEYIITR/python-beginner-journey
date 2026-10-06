"""
Set Comprehensions: from fundamentals to advanced data-processing patterns.

This executable script focuses specifically on Python set comprehensions:
- creating sets from iterables
- filtering and transforming values
- deduplication
- nested iteration
- conditional expressions
- strings and structured records
- relationships between multiple sets
- validation and edge cases
- performance characteristics
- practical data-cleaning and analytical workflows
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isqrt
from time import perf_counter
from typing import Iterable, Iterator


def heading(title: str) -> None:
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def demonstrate_basic_set_comprehension() -> None:
    heading("Basic Set Comprehensions")

    numbers = [1, 2, 2, 3, 4, 4, 5]

    squares = {number * number for number in numbers}
    even_numbers = {number for number in numbers if number % 2 == 0}

    print("Input:", numbers)
    print("Squares:", sorted(squares))
    print("Even numbers:", sorted(even_numbers))

    # A set comprehension automatically removes duplicate results.
    duplicate_input = ["python", "python", "sql", "java", "sql"]
    languages = {language.lower() for language in duplicate_input}
    print("Unique normalized languages:", sorted(languages))


def demonstrate_filtering_and_transformation() -> None:
    heading("Filtering and Transformation")

    transactions = [
        {"account": "A100", "amount": 2500},
        {"account": "A101", "amount": 750},
        {"account": "A100", "amount": 1250},
        {"account": "A102", "amount": 4000},
        {"account": "A103", "amount": -50},
    ]

    high_value_accounts = {
        transaction["account"]
        for transaction in transactions
        if transaction["amount"] >= 2000
    }

    positive_amounts = {
        transaction["amount"]
        for transaction in transactions
        if transaction["amount"] > 0
    }

    print("High-value accounts:", sorted(high_value_accounts))
    print("Unique positive transaction amounts:", sorted(positive_amounts))


def demonstrate_conditional_expression() -> None:
    heading("Conditional Expression Inside a Set Comprehension")

    scores = [42, 55, 71, 88, 96]

    classifications = {
        "pass" if score >= 50 else "fail"
        for score in scores
    }

    print("Scores:", scores)
    print("Classifications:", classifications)

    # The expression before `for` transforms each selected element.
    parity_labels = {
        "even" if number % 2 == 0 else "odd"
        for number in range(1, 8)
    }
    print("Parity labels:", parity_labels)


def demonstrate_strings() -> None:
    heading("Set Comprehensions with Strings")

    sentence = "Set comprehensions remove repeated values while transforming data."

    words = {
        word.strip(".,!?").lower()
        for word in sentence.split()
        if word.strip(".,!?")
    }

    vowels = {
        character.lower()
        for character in sentence
        if character.lower() in "aeiou"
    }

    print("Unique words:", sorted(words))
    print("Vowels present:", sorted(vowels))


def demonstrate_nested_iteration() -> None:
    heading("Nested Iteration")

    left = {"A", "B"}
    right = {1, 2, 3}

    combinations = {
        f"{letter}{number}"
        for letter in left
        for number in right
    }

    print("Cartesian combinations:", sorted(combinations))

    # Multiple `for` clauses behave like nested loops.
    coordinate_pairs = {
        (x, y)
        for x in range(3)
        for y in range(3)
        if x != y
    }

    print("Distinct coordinate pairs:", sorted(coordinate_pairs))


def demonstrate_set_relationships() -> None:
    heading("Set Relationships")

    requested_permissions = {"read", "write", "delete", "audit"}
    granted_permissions = {"read", "write", "audit"}

    missing_permissions = {
        permission
        for permission in requested_permissions
        if permission not in granted_permissions
    }

    active_permissions = {
        permission
        for permission in granted_permissions
        if permission in requested_permissions
    }

    print("Missing permissions:", sorted(missing_permissions))
    print("Active requested permissions:", sorted(active_permissions))

    # Equivalent set algebra is often clearer when the operation itself
    # expresses the intent directly.
    print("Set difference:", sorted(requested_permissions - granted_permissions))
    print("Set intersection:", sorted(requested_permissions & granted_permissions))


@dataclass(frozen=True)
class User:
    username: str
    roles: frozenset[str]
    active: bool


def demonstrate_structured_records() -> None:
    heading("Set Comprehensions with Structured Records")

    users = [
        User("anita", frozenset({"reader", "analyst"}), True),
        User("rahul", frozenset({"admin", "reader"}), True),
        User("meera", frozenset({"reader"}), False),
        User("vikas", frozenset({"analyst", "auditor"}), True),
    ]

    active_usernames = {
        user.username
        for user in users
        if user.active
    }

    analyst_users = {
        user.username
        for user in users
        if "analyst" in user.roles and user.active
    }

    roles_used_by_active_users = {
        role
        for user in users
        if user.active
        for role in user.roles
    }

    print("Active users:", sorted(active_usernames))
    print("Active analysts:", sorted(analyst_users))
    print("Roles used by active users:", sorted(roles_used_by_active_users))


def demonstrate_prime_numbers(limit: int) -> None:
    heading("Algorithmic Example: Prime Numbers")

    if limit < 2:
        print("No primes below", limit)
        return

    def is_prime(number: int) -> bool:
        if number < 2:
            return False
        if number == 2:
            return True
        if number % 2 == 0:
            return False

        # Testing only through sqrt(number) avoids unnecessary divisors.
        for divisor in range(3, isqrt(number) + 1, 2):
            if number % divisor == 0:
                return False
        return True

    primes = {number for number in range(2, limit + 1) if is_prime(number)}
    print(f"Primes through {limit}:", sorted(primes))


def demonstrate_deduplication_pipeline() -> None:
    heading("Data-Cleaning Pipeline")

    raw_emails = [
        " Alice@example.com ",
        "alice@example.com",
        "BOB@example.com",
        " bob@example.com ",
        "",
        "invalid-address",
        "carol@example.org",
    ]

    normalized_emails = {
        email.strip().lower()
        for email in raw_emails
        if "@" in email and "." in email.split("@")[-1]
    }

    print("Normalized unique emails:")
    for email in sorted(normalized_emails):
        print(" ", email)


def demonstrate_dictionary_to_set() -> None:
    heading("Dictionary Data and Set Comprehensions")

    inventory = {
        "keyboard": {"category": "hardware", "stock": 12},
        "monitor": {"category": "hardware", "stock": 0},
        "python-book": {"category": "book", "stock": 7},
        "sql-book": {"category": "book", "stock": 0},
    }

    available_products = {
        product
        for product, details in inventory.items()
        if details["stock"] > 0
    }

    categories_with_stock = {
        details["category"]
        for details in inventory.values()
        if details["stock"] > 0
    }

    print("Available products:", sorted(available_products))
    print("Categories containing stock:", sorted(categories_with_stock))


def demonstrate_generator_difference() -> None:
    heading("Set Comprehension versus Generator Expression")

    numbers = range(1, 11)

    materialized_set = {number * 2 for number in numbers}
    lazy_generator = (number * 2 for number in numbers)

    print("Set:", sorted(materialized_set))
    print("Generator type:", type(lazy_generator).__name__)
    print("Generator values:", list(lazy_generator))

    # A set stores all unique results immediately.
    # A generator computes values as they are consumed and can therefore
    # represent much larger sequences without materializing them all.


def demonstrate_validation() -> None:
    heading("Validation and Failure Conditions")

    values = [10, "20", 30, None, 10]

    valid_integers = {
        value
        for value in values
        if isinstance(value, int) and not isinstance(value, bool)
    }

    print("Valid integer values:", sorted(valid_integers))

    try:
        invalid = {item.lower() for item in values}
        print(invalid)
    except AttributeError as exc:
        print("Expected failure:", exc)

    # Filtering before calling a type-specific method prevents this class
    # of runtime error.
    safe_strings = {
        item.lower()
        for item in values
        if isinstance(item, str)
    }
    print("Safe normalized strings:", sorted(safe_strings))


def demonstrate_unhashable_edge_case() -> None:
    heading("Hashability Edge Case")

    records = [
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
    ]

    try:
        # Dictionaries are mutable and therefore unhashable, so they cannot
        # themselves be elements of a Python set.
        unique_records = {record for record in records}
        print(unique_records)
    except TypeError as exc:
        print("Expected TypeError:", exc)

    # Extracting an immutable identity is the appropriate alternative.
    unique_ids = {record["id"] for record in records}
    print("Unique record IDs:", sorted(unique_ids))


def demonstrate_frozenset() -> None:
    heading("Frozenset as a Set-Comprehension Result")

    permission_sets = [
        {"read", "write"},
        {"read", "write"},
        {"read"},
    ]

    immutable_permission_sets = {
        frozenset(permissions)
        for permissions in permission_sets
    }

    print("Unique immutable permission groups:")
    for permissions in sorted(
        immutable_permission_sets,
        key=lambda item: (len(item), sorted(item)),
    ):
        print(" ", sorted(permissions))


def demonstrate_advanced_relationships() -> None:
    heading("Advanced Set Relationships")

    employees = {
        "alice": {"python", "sql", "git"},
        "bob": {"java", "sql", "git"},
        "carol": {"python", "javascript"},
        "david": {"sql", "docker"},
    }

    all_skills = {
        skill
        for skills in employees.values()
        for skill in skills
    }

    developers_with_sql = {
        name
        for name, skills in employees.items()
        if "sql" in skills
    }

    rare_skills = {
        skill
        for skill in all_skills
        if sum(skill in skills for skills in employees.values()) == 1
    }

    print("All skills:", sorted(all_skills))
    print("Employees with SQL:", sorted(developers_with_sql))
    print("Skills used by exactly one employee:", sorted(rare_skills))


def demonstrate_performance() -> None:
    heading("Performance Considerations")

    data = list(range(100_000))

    start = perf_counter()
    result = {number * 2 for number in data if number % 3 == 0}
    elapsed = perf_counter() - start

    print("Unique results:", len(result))
    print(f"Set comprehension time: {elapsed:.6f} seconds")

    # Average-case membership in a hash set is O(1), making repeated
    # membership tests substantially cheaper than scanning a large list.
    lookup_values = set(data)
    probes = range(0, 100_000, 10_000)

    start = perf_counter()
    found = {probe for probe in probes if probe in lookup_values}
    elapsed_lookup = perf_counter() - start

    print("Successful membership probes:", sorted(found))
    print(f"Hash-set membership processing: {elapsed_lookup:.6f} seconds")


def demonstrate_realistic_access_policy() -> None:
    heading("Realistic Access Policy")

    accounts = {
        "finance": {"read", "write", "approve"},
        "analytics": {"read", "export"},
        "support": {"read", "comment"},
        "guest": {"read"},
    }

    required_for_approval = {"read", "approve"}

    eligible_roles = {
        role
        for role, permissions in accounts.items()
        if required_for_approval <= permissions
    }

    elevated_permissions = {
        permission
        for permissions in accounts.values()
        for permission in permissions
        if permission in {"write", "approve", "export"}
    }

    print("Roles eligible for approval:", sorted(eligible_roles))
    print("Elevated permissions present:", sorted(elevated_permissions))


def demonstrate_common_mistakes() -> None:
    heading("Common Mistakes")

    numbers = [1, 2, 3, 4]

    # A set comprehension requires an iterable after `for`.
    # The following equivalent loop makes the underlying mechanism explicit.
    explicit = set()
    for number in numbers:
        if number % 2 == 0:
            explicit.add(number * 10)

    concise = {number * 10 for number in numbers if number % 2 == 0}

    print("Explicit construction:", sorted(explicit))
    print("Comprehension:", sorted(concise))

    # Set ordering should never be used as a business rule. Sorting is used
    # only for deterministic display.
    print("Deterministic display:", sorted(concise))


def main() -> None:
    demonstrate_basic_set_comprehension()
    demonstrate_filtering_and_transformation()
    demonstrate_conditional_expression()
    demonstrate_strings()
    demonstrate_nested_iteration()
    demonstrate_set_relationships()
    demonstrate_structured_records()
    demonstrate_prime_numbers(50)
    demonstrate_deduplication_pipeline()
    demonstrate_dictionary_to_set()
    demonstrate_generator_difference()
    demonstrate_validation()
    demonstrate_unhashable_edge_case()
    demonstrate_frozenset()
    demonstrate_advanced_relationships()
    demonstrate_performance()
    demonstrate_realistic_access_policy()
    demonstrate_common_mistakes()


if __name__ == "__main__":
    main()
