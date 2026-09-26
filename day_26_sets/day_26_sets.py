"""
SETS: A comprehensive Python study program.

This standalone script teaches Python sets from absolute beginner concepts
through advanced usage. It also contains executable demonstrations, validation,
algorithms, performance observations, edge cases, and practical applications.

Run:
    python sets_comprehensive.py
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Iterable


# ============================================================================
# 1. FUNDAMENTALS
# ============================================================================

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def explain_basic_set() -> None:
    section("1. SET FUNDAMENTALS")

    # A set is an unordered collection of unique, hashable objects.
    numbers = {1, 2, 3, 4, 4, 3}

    # Duplicate values are automatically removed.
    print("Original literal: {1, 2, 3, 4, 4, 3}")
    print("Set result:", numbers)

    # Membership testing is one of the primary reasons to use sets.
    print("2 in numbers:", 2 in numbers)
    print("10 in numbers:", 10 in numbers)

    # An empty set must be created with set(), because {} creates a dictionary.
    empty_set = set()
    empty_dictionary = {}

    print("Empty set:", empty_set)
    print("Type of {}:", type(empty_dictionary).__name__)

    # A string is iterable, so set(string) creates a set of its characters.
    letters = set("banana")
    print("Characters in 'banana':", letters)


# ============================================================================
# 2. HASHABILITY
# ============================================================================

def demonstrate_hashability() -> None:
    section("2. HASHABILITY AND SET ELEMENTS")

    # Set elements must be hashable.
    # Integers, strings, tuples containing hashable values, and frozensets
    # are common hashable objects.
    valid = {
        42,
        "Python",
        (1, 2),
        frozenset({3, 4}),
    }

    print("Hashable elements:", valid)

    # Lists are mutable and therefore unhashable.
    try:
        invalid = {[1, 2, 3]}  # type: ignore
        print(invalid)
    except TypeError as error:
        print("List cannot be a set element:", error)

    # A tuple is hashable only when all of its contents are hashable.
    print("hash((1, 2)):", hash((1, 2)))

    try:
        hash((1, [2, 3]))
    except TypeError as error:
        print("Tuple containing a list is not hashable:", error)

    # frozenset is immutable and hashable, so it can itself be an element.
    nested_sets = {
        frozenset({1, 2}),
        frozenset({3, 4}),
    }
    print("Set of frozensets:", nested_sets)


# ============================================================================
# 3. CREATION
# ============================================================================

def demonstrate_creation() -> None:
    section("3. CREATING SETS")

    from_literal = {1, 2, 3}
    from_list = set([1, 2, 2, 3])
    from_tuple = set((4, 5, 5, 6))
    from_string = set("hello")
    from_generator = set(value * 2 for value in range(4))

    print("Literal:", from_literal)
    print("From list:", from_list)
    print("From tuple:", from_tuple)
    print("From string:", from_string)
    print("From generator:", from_generator)

    # set() accepts an iterable.
    values = range(5)
    print("From range:", set(values))


# ============================================================================
# 4. MUTABILITY AND BASIC METHODS
# ============================================================================

def demonstrate_mutation() -> None:
    section("4. SET MUTATION")

    values = {1, 2, 3}

    # add() inserts one element.
    values.add(4)
    print("After add(4):", values)

    # Adding an existing element has no effect.
    values.add(4)
    print("After adding 4 again:", values)

    # update() inserts elements from any iterable.
    values.update([5, 6], (7, 8))
    print("After update:", values)

    # remove() raises KeyError if the element does not exist.
    values.remove(8)
    print("After remove(8):", values)

    try:
        values.remove(100)
    except KeyError:
        print("remove(100) raised KeyError")

    # discard() silently does nothing when the value is absent.
    values.discard(100)
    print("After discard(100):", values)

    # pop() removes and returns an arbitrary element.
    removed = values.pop()
    print("Popped element:", removed)
    print("Remaining:", values)

    # clear() removes all elements.
    values.clear()
    print("After clear():", values)


# ============================================================================
# 5. SET OPERATIONS
# ============================================================================

def demonstrate_set_algebra() -> None:
    section("5. SET ALGEBRA")

    a = {1, 2, 3, 4}
    b = {3, 4, 5, 6}

    # Union: elements present in either set.
    print("Union:", a | b)
    print("Union method:", a.union(b))

    # Intersection: elements common to both sets.
    print("Intersection:", a & b)
    print("Intersection method:", a.intersection(b))

    # Difference: elements in the left set but not the right set.
    print("A - B:", a - b)
    print("B - A:", b - a)

    # Symmetric difference: elements in exactly one set.
    print("Symmetric difference:", a ^ b)
    print("Symmetric difference method:", a.symmetric_difference(b))

    # Operations can use more than two sets.
    c = {4, 5, 6, 7}
    print("Three-set union:", a | b | c)
    print("Three-set intersection:", a & b & c)


# ============================================================================
# 6. UPDATE VARIANTS
# ============================================================================

def demonstrate_in_place_operations() -> None:
    section("6. IN-PLACE SET OPERATIONS")

    values = {1, 2, 3}
    values |= {3, 4, 5}
    print("After |=:", values)

    values &= {2, 3, 4}
    print("After &=:", values)

    values -= {3}
    print("After -=:", values)

    values ^= {2, 8}
    print("After ^=:", values)

    # Named methods also have update variants.
    values.intersection_update({8, 9})
    print("After intersection_update:", values)


# ============================================================================
# 7. RELATIONSHIPS BETWEEN SETS
# ============================================================================

def demonstrate_relationships() -> None:
    section("7. SET RELATIONSHIPS")

    small = {1, 2}
    large = {1, 2, 3, 4}

    print("small <= large:", small <= large)
    print("small < large:", small < large)
    print("large >= small:", large >= small)
    print("large > small:", large > small)

    print("small.issubset(large):", small.issubset(large))
    print("large.issuperset(small):", large.issuperset(small))

    disjoint_a = {1, 2}
    disjoint_b = {3, 4}
    overlapping = {2, 3}

    print("Disjoint sets:", disjoint_a.isdisjoint(disjoint_b))
    print("Overlapping sets:", disjoint_a.isdisjoint(overlapping))


# ============================================================================
# 8. FROZENSET
# ============================================================================

def demonstrate_frozenset() -> None:
    section("8. FROZENSET")

    # frozenset is immutable.
    immutable = frozenset({1, 2, 3})
    print("frozenset:", immutable)

    try:
        immutable.add(4)  # type: ignore
    except AttributeError as error:
        print("Cannot mutate frozenset:", error)

    # frozenset supports set-algebra operations.
    print("Union:", immutable | {3, 4})
    print("Intersection:", immutable & {2, 3, 5})

    # It can be a dictionary key.
    permissions = {
        frozenset({"read", "write"}): "editor",
        frozenset({"read"}): "viewer",
    }
    print("Dictionary keyed by frozenset:", permissions)


# ============================================================================
# 9. SET COMPREHENSIONS
# ============================================================================

def demonstrate_comprehensions() -> None:
    section("9. SET COMPREHENSIONS")

    squares = {number * number for number in range(10)}
    print("Squares:", squares)

    even_squares = {
        number * number
        for number in range(20)
        if number % 2 == 0
    }
    print("Even squares:", even_squares)

    words = ["Python", "python", "SET", "set", "Data"]
    normalized = {word.lower() for word in words}
    print("Normalized unique words:", normalized)

    # Conditional expressions may be used inside comprehensions.
    labels = {
        "even" if number % 2 == 0 else "odd"
        for number in range(6)
    }
    print("Distinct labels:", labels)


# ============================================================================
# 10. ITERATION AND ORDER
# ============================================================================

def demonstrate_iteration() -> None:
    section("10. ITERATION")

    values = {10, 20, 30, 40}

    for value in values:
        print("Value:", value)

    # A set is not a sequence. Do not depend on iteration order.
    print("Set:", values)
    print("Sorted view:", sorted(values))

    # enumerate() works after creating an iterable view, but the numerical
    # position should not be interpreted as a stable set index.
    for position, value in enumerate(sorted(values), start=1):
        print(f"Sorted position {position}: {value}")


# ============================================================================
# 11. SETS AND DUPLICATE REMOVAL
# ============================================================================

def demonstrate_deduplication() -> None:
    section("11. DUPLICATE REMOVAL")

    records = [
        "alice@example.com",
        "bob@example.com",
        "alice@example.com",
        "carol@example.com",
        "bob@example.com",
    ]

    unique_records = set(records)
    print("Original count:", len(records))
    print("Unique count:", len(unique_records))
    print("Unique values:", unique_records)

    # If original order matters, a set alone is insufficient.
    ordered_unique = list(dict.fromkeys(records))
    print("Order-preserving unique values:", ordered_unique)


# ============================================================================
# 12. PRACTICAL TAG EXAMPLE
# ============================================================================

@dataclass
class Article:
    title: str
    tags: set[str]


def demonstrate_tags() -> None:
    section("12. PRACTICAL TAG SYSTEM")

    article = Article(
        title="Introduction to Algorithms",
        tags={"python", "algorithms", "data-structures"},
    )

    required_tags = {"python", "algorithms"}

    print("Article:", article.title)
    print("Tags:", article.tags)
    print("Contains all required tags:", required_tags <= article.tags)

    article.tags.add("education")
    print("Updated tags:", article.tags)


# ============================================================================
# 13. ACCESS CONTROL
# ============================================================================

def demonstrate_permissions() -> None:
    section("13. PERMISSION COMPARISON")

    user_permissions = {"read", "write", "download"}
    required_permissions = {"read", "download"}

    missing = required_permissions - user_permissions
    extra = user_permissions - required_permissions

    print("Missing permissions:", missing)
    print("Extra permissions:", extra)
    print("Access granted:", not missing)


# ============================================================================
# 14. RELATIONAL DATA ANALYSIS
# ============================================================================

def demonstrate_customer_analysis() -> None:
    section("14. CUSTOMER SET ANALYSIS")

    january_customers = {"A", "B", "C", "D", "E"}
    february_customers = {"C", "D", "E", "F", "G"}

    retained = january_customers & february_customers
    new_customers = february_customers - january_customers
    churned = january_customers - february_customers
    all_customers = january_customers | february_customers

    print("Retained:", retained)
    print("New:", new_customers)
    print("Churned:", churned)
    print("Total unique:", len(all_customers))


# ============================================================================
# 15. GRAPH NEIGHBOR ANALYSIS
# ============================================================================

def demonstrate_graph_neighbors() -> None:
    section("15. GRAPH NEIGHBOR SETS")

    graph = {
        "A": {"B", "C"},
        "B": {"A", "C", "D"},
        "C": {"A", "B", "D"},
        "D": {"B", "C"},
    }

    a_neighbors = graph["A"]
    b_neighbors = graph["B"]

    common = a_neighbors & b_neighbors
    exclusive_to_b = b_neighbors - a_neighbors

    print("A neighbors:", a_neighbors)
    print("B neighbors:", b_neighbors)
    print("Common neighbors:", common)
    print("Only B's neighbors:", exclusive_to_b)


# ============================================================================
# 16. BOOLEAN-LIKE SET LOGIC
# ============================================================================

def demonstrate_logical_relationships() -> None:
    section("16. SETS AS LOGICAL COLLECTIONS")

    required = {"authentication", "authorization"}
    available = {"authentication", "authorization", "logging"}

    # Subset testing answers an "all requirements satisfied?" question.
    all_requirements_met = required.issubset(available)

    # Intersection answers an "any shared capability?" question.
    requested = {"logging", "encryption"}
    shared = requested & available

    print("All requirements met:", all_requirements_met)
    print("Shared capabilities:", shared)


# ============================================================================
# 17. EDGE CASES
# ============================================================================

def demonstrate_edge_cases() -> None:
    section("17. EDGE CASES")

    empty = set()
    singleton = {1}

    print("Empty set:", empty)
    print("Empty set length:", len(empty))
    print("Empty set is subset of itself:", empty <= empty)
    print("Singleton:", singleton)

    # Any set is a subset of itself.
    values = {1, 2, 3}
    print("Reflexive subset:", values <= values)
    print("Proper subset:", values < values)

    # None is hashable and can be stored in a set.
    nullable_values = {None, 1, 2}
    print("Set containing None:", nullable_values)

    # Different numeric types can compare equal.
    mixed = {1, True, 1.0}
    print("{1, True, 1.0} becomes:", mixed)

    # NaN has unusual equality behavior.
    nan = float("nan")
    nan_set = {nan}
    print("NaN membership using same object:", nan in nan_set)


# ============================================================================
# 18. CUSTOM HASHABLE OBJECTS
# ============================================================================

@dataclass(frozen=True)
class User:
    user_id: int
    username: str


def demonstrate_custom_objects() -> None:
    section("18. CUSTOM HASHABLE OBJECTS")

    users = {
        User(1, "alice"),
        User(2, "bob"),
        User(1, "alice"),
    }

    print("Unique users:", users)

    # Frozen dataclasses are immutable and provide suitable equality/hash
    # behavior for this value-object use case.
    print("Number of users:", len(users))


# ============================================================================
# 19. SAFE SET CONVERSION
# ============================================================================

def unique_hashable_values(values: Iterable[Any]) -> set[Any]:
    """Return unique hashable values and raise a clear error otherwise."""
    result: set[Any] = set()

    for value in values:
        try:
            result.add(value)
        except TypeError as error:
            raise TypeError(
                f"Value {value!r} is not hashable and cannot be stored in a set."
            ) from error

    return result


def demonstrate_validation() -> None:
    section("19. VALIDATION")

    print(unique_hashable_values([1, 2, 2, 3]))

    try:
        unique_hashable_values([1, [2, 3]])
    except TypeError as error:
        print("Validation error:", error)


# ============================================================================
# 20. SET-BASED ALGORITHMS
# ============================================================================

def find_duplicates(values: Iterable[Any]) -> set[Any]:
    """Return values occurring more than once."""
    seen: set[Any] = set()
    duplicates: set[Any] = set()

    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)

    return duplicates


def find_missing_values(expected: Iterable[int], actual: Iterable[int]) -> set[int]:
    """Return expected values absent from the actual collection."""
    return set(expected) - set(actual)


def are_anagrams(first: str, second: str) -> bool:
    """
    Demonstrate a limitation of sets.

    A pure set comparison ignores character frequency, so this function
    intentionally uses Counter instead. This shows when a set is the wrong
    data structure for the problem.
    """
    from collections import Counter

    return Counter(first.replace(" ", "").lower()) == Counter(
        second.replace(" ", "").lower()
    )


def demonstrate_algorithms() -> None:
    section("20. SET-BASED ALGORITHMS")

    data = [1, 2, 3, 2, 4, 5, 1, 6]
    print("Duplicates:", find_duplicates(data))

    expected = range(1, 11)
    actual = [1, 2, 3, 5, 6, 7, 9, 10]
    print("Missing:", find_missing_values(expected, actual))

    print(
        "Anagram test:",
        are_anagrams("Dormitory", "Dirty room"),
    )


# ============================================================================
# 21. POWER SET
# ============================================================================

def power_set(values: set[Any]) -> list[frozenset[Any]]:
    """
    Generate the power set.

    A set containing n elements has 2^n subsets.
    frozenset is used because each subset must itself be hashable if we want
    to represent the collection of subsets as a set.
    """
    subsets: list[frozenset[Any]] = [frozenset()]

    for value in values:
        subsets += [subset | {value} for subset in subsets]

    return subsets


def demonstrate_power_set() -> None:
    section("21. POWER SET")

    values = {1, 2, 3}
    subsets = power_set(values)

    print("Input:", values)
    print("Number of subsets:", len(subsets))
    print("Expected:", 2 ** len(values))
    print("Subsets:", subsets)


# ============================================================================
# 22. SET PARTITIONS
# ============================================================================

def demonstrate_partition() -> None:
    section("22. PARTITIONING DATA WITH SETS")

    users = {"alice", "bob", "carol", "david"}
    administrators = {"alice", "david"}
    active_users = {"alice", "bob", "carol"}

    inactive_users = users - active_users
    active_non_admins = active_users - administrators

    print("All users:", users)
    print("Administrators:", administrators)
    print("Inactive users:", inactive_users)
    print("Active non-admins:", active_non_admins)


# ============================================================================
# 23. PERFORMANCE
# ============================================================================

def benchmark_membership() -> None:
    section("23. MEMBERSHIP PERFORMANCE")

    size = 200_000
    values = list(range(size))
    value_set = set(values)
    target = size - 1

    start = perf_counter()
    target in values
    list_time = perf_counter() - start

    start = perf_counter()
    target in value_set
    set_time = perf_counter() - start

    print(f"List membership time: {list_time:.8f} seconds")
    print(f"Set membership time:  {set_time:.8f} seconds")
    print(
        "Sets normally provide average O(1) membership testing, "
        "while lists provide O(n) membership testing."
    )


# ============================================================================
# 24. COMPLEXITY
# ============================================================================

def print_complexity_reference() -> None:
    section("24. COMPLEXITY REFERENCE")

    complexity = {
        "membership (average)": "O(1)",
        "membership (worst-case)": "O(n) in pathological hash-table behavior",
        "add (average)": "O(1)",
        "remove/discard (average)": "O(1)",
        "union": "O(n + m) for sets of sizes n and m",
        "intersection": "Approximately O(min(n, m)) for normal use",
        "difference": "O(n) where n is the left operand size",
        "iteration": "O(n)",
        "len": "O(1)",
        "power set": "O(2^n) output size",
    }

    for operation, cost in complexity.items():
        print(f"{operation:32} {cost}")


# ============================================================================
# 25. SECURITY CONSIDERATIONS
# ============================================================================

def demonstrate_security_considerations() -> None:
    section("25. SECURITY CONSIDERATIONS")

    allowed_roles = {"admin", "editor", "viewer"}
    supplied_role = "admin"

    # Membership checks can enforce allow-lists.
    if supplied_role in allowed_roles:
        print("Role exists in allow-list.")
    else:
        print("Role rejected.")

    # Normalize external text before membership testing when appropriate.
    raw_role = " Admin "
    normalized_role = raw_role.strip().lower()

    normalized_allowed_roles = {role.lower() for role in allowed_roles}

    print("Normalized role:", normalized_role)
    print("Accepted:", normalized_role in normalized_allowed_roles)

    print(
        "Security note: a set membership check only answers whether a value "
        "is in the collection. Authentication, authorization policy, input "
        "validation, and audit controls must still be implemented separately."
    )


# ============================================================================
# 26. COMMON MISTAKES
# ============================================================================

def demonstrate_common_mistakes() -> None:
    section("26. COMMON MISTAKES")

    # Mistake 1: expecting indexing.
    values = {10, 20, 30}

    try:
        print(values[0])  # type: ignore
    except TypeError as error:
        print("Sets do not support indexing:", error)

    # Mistake 2: using {} for an empty set.
    value = {}
    print("{} creates:", type(value).__name__)

    # Mistake 3: expecting stable ordering.
    print("Use sorted(values) when a deterministic ordered view is required.")

    # Mistake 4: mutating a set during iteration.
    values = {1, 2, 3, 4}

    try:
        for value in values:
            if value % 2 == 0:
                values.remove(value)
    except RuntimeError as error:
        print("Mutation during iteration can fail:", error)

    # Correct pattern: build a separate result.
    values = {1, 2, 3, 4}
    filtered = {value for value in values if value % 2 != 0}
    print("Safe filtered set:", filtered)


# ============================================================================
# 27. SET VS OTHER DATA STRUCTURES
# ============================================================================

def compare_data_structures() -> None:
    section("27. SET VS LIST VS DICTIONARY VS TUPLE")

    records = {
        "set": {
            "unique": True,
            "ordered_for_indexing": False,
            "primary_strength": "fast membership and set algebra",
            "mutable": True,
        },
        "list": {
            "unique": False,
            "ordered_for_indexing": True,
            "primary_strength": "sequence storage",
            "mutable": True,
        },
        "tuple": {
            "unique": False,
            "ordered_for_indexing": True,
            "primary_strength": "immutable sequence",
            "mutable": False,
        },
        "dict": {
            "unique": "keys are unique",
            "ordered_for_indexing": "key-based access",
            "primary_strength": "key-value mapping",
            "mutable": True,
        },
    }

    for name, properties in records.items():
        print(f"\n{name.upper()}")
        for key, value in properties.items():
            print(f"  {key}: {value}")


# ============================================================================
# 28. ADVANCED SET SUBCLASS
# ============================================================================

class NamedSet(set[str]):
    """A small set subclass showing that sets can be extended."""

    def __init__(self, values: Iterable[str] = (), name: str = "unnamed") -> None:
        super().__init__(values)
        self.name = name

    def describe(self) -> str:
        return f"{self.name}: {sorted(self)}"


def demonstrate_subclassing() -> None:
    section("28. SET SUBCLASSING")

    technologies = NamedSet(
        ["Python", "SQL", "Python"],
        name="Technology skills",
    )

    print(technologies.describe())


# ============================================================================
# 29. SET OPERATIONS WITH GENERAL ITERABLES
# ============================================================================

def demonstrate_iterable_arguments() -> None:
    section("29. SET METHODS AND ITERABLES")

    values = {1, 2, 3, 4}

    # Methods such as union() can accept iterable arguments.
    print("Union with list:", values.union([4, 5, 6]))
    print("Difference with tuple:", values.difference((2, 3)))

    # Operator forms require compatible set-like operands.
    try:
        print(values | [5, 6])  # type: ignore
    except TypeError as error:
        print("Operator with list:", error)


# ============================================================================
# 30. REAL-WORLD DATA QUALITY CHECK
# ============================================================================

def validate_required_fields(
    records: list[dict[str, Any]],
    required_fields: set[str],
) -> list[tuple[int, set[str]]]:
    """Return record indexes and missing required fields."""
    failures = []

    for index, record in enumerate(records):
        present = set(record.keys())
        missing = required_fields - present

        if missing:
            failures.append((index, missing))

    return failures


def demonstrate_data_quality() -> None:
    section("30. DATA QUALITY VALIDATION")

    records = [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Carol", "email": "carol@example.com"},
    ]

    required = {"id", "name", "email"}
    failures = validate_required_fields(records, required)

    for index, missing in failures:
        print(f"Record {index} is missing: {sorted(missing)}")


# ============================================================================
# 31. EVENT STREAM ANALYSIS
# ============================================================================

def demonstrate_event_analysis() -> None:
    section("31. EVENT STREAM ANALYSIS")

    events = [
        ("alice", "login"),
        ("bob", "login"),
        ("alice", "download"),
        ("alice", "logout"),
        ("carol", "login"),
        ("bob", "logout"),
    ]

    login_users = {
        user
        for user, event in events
        if event == "login"
    }

    logout_users = {
        user
        for user, event in events
        if event == "logout"
    }

    currently_logged_out = logout_users - login_users
    active_seen_users = login_users - logout_users

    print("Users who logged in:", login_users)
    print("Users who logged out:", logout_users)
    print("Login users not seen logging out:", active_seen_users)
    print("Logout users never seen logging in:", currently_logged_out)


# ============================================================================
# 32. API FEATURE COMPATIBILITY
# ============================================================================

def compatible_features(
    requested: set[str],
    supported: set[str],
) -> tuple[bool, set[str], set[str]]:
    """
    Return whether all requested features are supported, plus missing
    and unused capabilities.
    """
    missing = requested - supported
    unused = supported - requested
    return not missing, missing, unused


def demonstrate_feature_compatibility() -> None:
    section("32. FEATURE COMPATIBILITY")

    requested = {"json", "compression", "authentication"}
    supported = {"json", "authentication", "logging"}

    compatible, missing, unused = compatible_features(requested, supported)

    print("Compatible:", compatible)
    print("Missing:", missing)
    print("Unused supported features:", unused)


# ============================================================================
# 33. SET COPY SEMANTICS
# ============================================================================

def demonstrate_copying() -> None:
    section("33. COPYING SETS")

    original = {1, 2, 3}
    alias = original
    independent = original.copy()

    alias.add(4)

    print("Original after alias mutation:", original)
    print("Alias:", alias)
    print("Independent copy:", independent)

    # copy() creates a new set object, but nested mutable objects would still
    # require deeper copying if the set contained references to mutable data.
    print("original is alias:", original is alias)
    print("original is independent:", original is independent)


# ============================================================================
# 34. SET IDENTITY AND EQUALITY
# ============================================================================

def demonstrate_identity_and_equality() -> None:
    section("34. EQUALITY AND IDENTITY")

    first = {1, 2, 3}
    second = {3, 2, 1}
    third = first

    print("first == second:", first == second)
    print("first is second:", first is second)
    print("first is third:", first is third)


# ============================================================================
# 35. EXCEPTION HANDLING
# ============================================================================

def safe_remove(values: set[Any], value: Any) -> bool:
    """Remove a value and report whether removal occurred."""
    try:
        values.remove(value)
        return True
    except KeyError:
        return False


def demonstrate_exception_handling() -> None:
    section("35. ERROR HANDLING")

    values = {"Python", "JavaScript", "C++"}

    for language in ["Python", "Rust"]:
        removed = safe_remove(values, language)
        print(f"Removed {language!r}: {removed}")

    print("Remaining:", values)


# ============================================================================
# 36. TESTS
# ============================================================================

def run_assertion_tests() -> None:
    section("36. BUILT-IN TESTS")

    assert {1, 2, 2} == {1, 2}
    assert {1, 2} | {2, 3} == {1, 2, 3}
    assert {1, 2} & {2, 3} == {2}
    assert {1, 2} - {2, 3} == {1}
    assert {1, 2} ^ {2, 3} == {1, 3}
    assert {1, 2} <= {1, 2, 3}
    assert not ({1, 2} >= {1, 2, 3})
    assert find_duplicates([1, 2, 2, 3, 3]) == {2, 3}
    assert find_missing_values(range(1, 5), [1, 2, 4]) == {3}
    assert are_anagrams("listen", "silent")
    assert not are_anagrams("abc", "aabbcc")

    print("All assertions passed.")


# ============================================================================
# 37. STUDY CHECKLIST PRINTED AS DATA
# ============================================================================

def print_study_checklist() -> None:
    section("37. CONCEPT CHECKLIST")

    checklist = [
        "Set creation and uniqueness",
        "Hashability",
        "Membership testing",
        "add, update, remove, discard, pop, clear",
        "Union",
        "Intersection",
        "Difference",
        "Symmetric difference",
        "Subset and superset relationships",
        "Disjointness",
        "Set comprehensions",
        "frozenset",
        "Deduplication",
        "Set-based algorithms",
        "Complexity",
        "Edge cases",
        "Data validation",
        "Permission checks",
        "Real-world set algebra",
        "Limitations compared with other data structures",
    ]

    for number, item in enumerate(checklist, start=1):
        print(f"{number:02}. {item}")


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    """Run the complete educational demonstration."""
    explain_basic_set()
    demonstrate_hashability()
    demonstrate_creation()
    demonstrate_mutation()
    demonstrate_set_algebra()
    demonstrate_in_place_operations()
    demonstrate_relationships()
    demonstrate_frozenset()
    demonstrate_comprehensions()
    demonstrate_iteration()
    demonstrate_deduplication()
    demonstrate_tags()
    demonstrate_permissions()
    demonstrate_customer_analysis()
    demonstrate_graph_neighbors()
    demonstrate_logical_relationships()
    demonstrate_edge_cases()
    demonstrate_custom_objects()
    demonstrate_validation()
    demonstrate_algorithms()
    demonstrate_power_set()
    demonstrate_partition()
    benchmark_membership()
    print_complexity_reference()
    demonstrate_security_considerations()
    demonstrate_common_mistakes()
    compare_data_structures()
    demonstrate_subclassing()
    demonstrate_iterable_arguments()
    demonstrate_data_quality()
    demonstrate_event_analysis()
    demonstrate_feature_compatibility()
    demonstrate_copying()
    demonstrate_identity_and_equality()
    demonstrate_exception_handling()
    run_assertion_tests()
    print_study_checklist()

    section("END OF SETS STUDY PROGRAM")
    print("All demonstrations completed successfully.")


if __name__ == "__main__":
    main()
