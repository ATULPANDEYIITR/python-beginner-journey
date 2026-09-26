"""
SET OPERATIONS
==============

A self-contained study file covering sets from absolute beginner through
advanced level, with executable examples, algorithms, validation, testing,
edge cases, performance considerations, and practical applications.

Run with:
    python set_operations.py
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Iterable


# ============================================================================
# 1. FUNDAMENTALS
# ============================================================================

def fundamentals() -> None:
    print("\n" + "=" * 78)
    print("1. FUNDAMENTALS")
    print("=" * 78)

    # A set stores unique hashable elements. Duplicate values disappear.
    numbers = {1, 2, 3, 3, 2, 1}
    print("Duplicates removed:", numbers)

    # An empty set must be created with set(), because {} creates a dictionary.
    empty_set = set()
    print("Empty set:", empty_set)

    # A set can contain numbers, strings, tuples, and other immutable/hashable
    # objects. Lists and dictionaries cannot directly be set elements.
    mixed = {10, "Python", (1, 2)}
    print("Hashable mixed set:", mixed)

    # Membership testing is a fundamental set operation.
    print("2 in numbers:", 2 in numbers)
    print("99 in numbers:", 99 in numbers)

    # Sets are unordered collections. Do not rely on printed order.
    # They do not support positional indexing.
    try:
        print(numbers[0])
    except TypeError as error:
        print("Indexing error:", error)

    # Cardinality means the number of elements in a set.
    print("Cardinality:", len(numbers))


# ============================================================================
# 2. CREATION AND CONVERSION
# ============================================================================

def creation_and_conversion() -> None:
    print("\n" + "=" * 78)
    print("2. CREATION AND CONVERSION")
    print("=" * 78)

    from_list = set([1, 2, 2, 4, 5])
    from_tuple = set((2, 3, 3, 6))
    from_string = set("banana")

    print("From list:", from_list)
    print("From tuple:", from_tuple)
    print("Unique characters:", from_string)

    # A dictionary converted to a set produces its keys.
    dictionary = {"id": 1, "name": "Atul"}
    print("Dictionary keys as set:", set(dictionary))

    # A frozenset is immutable and therefore hashable.
    immutable_set = frozenset({1, 2, 3})
    print("Frozenset:", immutable_set)

    # A frozenset can itself be an element of another set.
    nested_sets = {frozenset({1, 2}), frozenset({3, 4})}
    print("Set containing frozensets:", nested_sets)


# ============================================================================
# 3. ADDING AND REMOVING ELEMENTS
# ============================================================================

def mutation_operations() -> None:
    print("\n" + "=" * 78)
    print("3. ADDING AND REMOVING ELEMENTS")
    print("=" * 78)

    values = {1, 2, 3}

    values.add(4)
    print("After add:", values)

    values.update([5, 6, 6])
    print("After update:", values)

    # remove() raises KeyError when the element does not exist.
    values.remove(6)
    print("After remove:", values)

    # discard() silently does nothing when the element is absent.
    values.discard(999)
    print("After discard of missing value:", values)

    # pop() removes an arbitrary element. Never assume which element it removes.
    removed = values.pop()
    print("Arbitrarily removed:", removed)
    print("Remaining:", values)

    values.clear()
    print("After clear:", values)


# ============================================================================
# 4. MATHEMATICAL SET OPERATIONS
# ============================================================================

def mathematical_operations() -> None:
    print("\n" + "=" * 78)
    print("4. MATHEMATICAL SET OPERATIONS")
    print("=" * 78)

    A = {1, 2, 3, 4}
    B = {3, 4, 5, 6}

    # Union: elements belonging to A or B.
    print("Union:", A | B)
    print("Union method:", A.union(B))

    # Intersection: elements belonging to both A and B.
    print("Intersection:", A & B)
    print("Intersection method:", A.intersection(B))

    # Difference: elements in A that are not in B.
    print("A - B:", A - B)
    print("B - A:", B - A)

    # Symmetric difference: elements in exactly one of the two sets.
    print("Symmetric difference:", A ^ B)
    print("Symmetric difference method:", A.symmetric_difference(B))

    # Equivalent update operations mutate the left-hand set.
    C = A.copy()
    C |= B
    print("Union update:", C)

    C = A.copy()
    C &= B
    print("Intersection update:", C)

    C = A.copy()
    C -= B
    print("Difference update:", C)

    C = A.copy()
    C ^= B
    print("Symmetric-difference update:", C)


# ============================================================================
# 5. RELATIONS BETWEEN SETS
# ============================================================================

def set_relations() -> None:
    print("\n" + "=" * 78)
    print("5. RELATIONS BETWEEN SETS")
    print("=" * 78)

    A = {1, 2}
    B = {1, 2, 3}
    C = {4, 5}

    # Subset: every element of A is also in B.
    print("A <= B:", A <= B)
    print("A.issubset(B):", A.issubset(B))

    # Proper subset requires A != B.
    print("A < B:", A < B)

    # Superset is the reverse relationship.
    print("B >= A:", B >= A)
    print("B.issuperset(A):", B.issuperset(A))

    # Disjoint sets have no common elements.
    print("A and C disjoint:", A.isdisjoint(C))

    # Equal sets contain exactly the same elements regardless of insertion order.
    print("{1, 2} == {2, 1}:", {1, 2} == {2, 1})


# ============================================================================
# 6. SET COMPREHENSIONS
# ============================================================================

def set_comprehensions() -> None:
    print("\n" + "=" * 78)
    print("6. SET COMPREHENSIONS")
    print("=" * 78)

    # Set comprehension combines iteration, transformation, and uniqueness.
    squares = {number * number for number in range(1, 8)}
    print("Squares:", squares)

    even_squares = {
        number * number
        for number in range(1, 11)
        if number % 2 == 0
    }
    print("Even squares:", even_squares)

    words = ["apple", "Apple", "banana", "BANANA", "pear"]
    normalized_words = {word.lower() for word in words}
    print("Normalized unique words:", normalized_words)


# ============================================================================
# 7. REAL-WORLD EXAMPLE: USER ACCESS
# ============================================================================

def access_control_example() -> None:
    print("\n" + "=" * 78)
    print("7. REAL-WORLD EXAMPLE: ACCESS CONTROL")
    print("=" * 78)

    required_permissions = {"read", "write"}
    user_permissions = {"read", "write", "analytics"}

    has_required_access = required_permissions.issubset(user_permissions)
    extra_permissions = user_permissions - required_permissions
    missing_permissions = required_permissions - user_permissions

    print("Required permissions:", required_permissions)
    print("User permissions:", user_permissions)
    print("Authorized:", has_required_access)
    print("Extra permissions:", extra_permissions)
    print("Missing permissions:", missing_permissions)


# ============================================================================
# 8. REAL-WORLD EXAMPLE: DATA RECONCILIATION
# ============================================================================

def reconciliation_example() -> None:
    print("\n" + "=" * 78)
    print("8. REAL-WORLD EXAMPLE: DATA RECONCILIATION")
    print("=" * 78)

    database_ids = {101, 102, 103, 104, 105}
    api_ids = {103, 104, 105, 106, 107}

    common = database_ids & api_ids
    only_database = database_ids - api_ids
    only_api = api_ids - database_ids
    all_ids = database_ids | api_ids

    print("Common IDs:", common)
    print("Only database:", only_database)
    print("Only API:", only_api)
    print("Combined IDs:", all_ids)


# ============================================================================
# 9. FUNCTIONS THAT ACCEPT ITERABLES
# ============================================================================

def unique_preserving_order(values: Iterable[Any]) -> list[Any]:
    """
    Return unique values while preserving first-seen order.

    A plain set is excellent for uniqueness and membership, but its mathematical
    nature does not guarantee an application-level ordering contract.
    """
    seen: set[Any] = set()
    result: list[Any] = []

    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)

    return result


def multiset_difference(left: Iterable[Any], right: Iterable[Any]) -> list[Any]:
    """
    Demonstrate a limitation of ordinary sets.

    A set loses multiplicity, so this function uses a dictionary of counts to
    perform a multiset-style difference.
    """
    from collections import Counter

    left_counts = Counter(left)
    right_counts = Counter(right)
    result: list[Any] = []

    for value, count in left_counts.items():
        remaining = count - right_counts[value]
        result.extend([value] * max(0, remaining))

    return result


def advanced_collection_examples() -> None:
    print("\n" + "=" * 78)
    print("9. ADVANCED COLLECTION EXAMPLES")
    print("=" * 78)

    values = [4, 2, 4, 1, 2, 3, 1]
    print("Input:", values)
    print("set(values):", set(values))
    print("Ordered unique values:", unique_preserving_order(values))

    left = ["a", "a", "a", "b", "c"]
    right = ["a", "b"]
    print("Multiset difference:", multiset_difference(left, right))


# ============================================================================
# 10. HASHABILITY AND EDGE CASES
# ============================================================================

def hashability_and_edge_cases() -> None:
    print("\n" + "=" * 78)
    print("10. HASHABILITY AND EDGE CASES")
    print("=" * 78)

    # Mutable containers such as lists are not hashable and cannot be elements
    # of a normal set.
    try:
        invalid = {[1, 2], [3, 4]}
        print(invalid)
    except TypeError as error:
        print("Unhashable element:", error)

    # Tuples are hashable when all of their members are hashable.
    valid = {(1, 2), (3, 4)}
    print("Tuple elements:", valid)

    # A tuple containing a list is not hashable.
    try:
        invalid_tuple = {(1, [2, 3])}
        print(invalid_tuple)
    except TypeError as error:
        print("Unhashable nested value:", error)

    # NaN has unusual equality behavior. It is a floating-point special value,
    # not an ordinary mathematical real number.
    nan = float("nan")
    nan_set = {nan}
    print("NaN membership using the same object:", nan in nan_set)

    # None is hashable and can be stored normally.
    print("None in set:", {None, 1, 2})


# ============================================================================
# 11. RELATION TO OTHER COLLECTIONS
# ============================================================================

def collection_comparison() -> None:
    print("\n" + "=" * 78)
    print("11. COLLECTION COMPARISON")
    print("=" * 78)

    values = [1, 2, 2, 3]
    tuple_values = (1, 2, 2, 3)
    set_values = {1, 2, 2, 3}
    dictionary = {"a": 1, "b": 2}

    print("List preserves duplicates and order:", values)
    print("Tuple preserves duplicates and order:", tuple_values)
    print("Set stores unique values:", set_values)
    print("Dictionary maps keys to values:", dictionary)

    print("List membership:", 3 in values)
    print("Set membership:", 3 in set_values)


# ============================================================================
# 12. ALGORITHMIC IMPLEMENTATIONS
# ============================================================================

def manual_union(first: set[Any], second: set[Any]) -> set[Any]:
    result = set(first)
    result.update(second)
    return result


def manual_intersection(first: set[Any], second: set[Any]) -> set[Any]:
    # Iterate through the smaller set to reduce membership checks.
    smaller, larger = (
        (first, second) if len(first) <= len(second) else (second, first)
    )
    return {value for value in smaller if value in larger}


def manual_difference(first: set[Any], second: set[Any]) -> set[Any]:
    return {value for value in first if value not in second}


def manual_symmetric_difference(
    first: set[Any], second: set[Any]
) -> set[Any]:
    return (first - second) | (second - first)


def algorithmic_examples() -> None:
    print("\n" + "=" * 78)
    print("12. ALGORITHMIC IMPLEMENTATIONS")
    print("=" * 78)

    A = {1, 2, 3, 4}
    B = {3, 4, 5, 6}

    print("Manual union:", manual_union(A, B))
    print("Manual intersection:", manual_intersection(A, B))
    print("Manual difference:", manual_difference(A, B))
    print("Manual symmetric difference:", manual_symmetric_difference(A, B))


# ============================================================================
# 13. INVERTED INDEX
# ============================================================================

def build_inverted_index(documents: dict[str, str]) -> dict[str, set[str]]:
    """
    Map each normalized word to the documents containing it.

    This is a simplified search-engine-style inverted index.
    """
    index: dict[str, set[str]] = {}

    for document_id, text in documents.items():
        words = {
            word.strip(".,!?;:()[]{}\"'").lower()
            for word in text.split()
        }

        for word in words:
            if word:
                index.setdefault(word, set()).add(document_id)

    return index


def search_documents(
    index: dict[str, set[str]],
    required_terms: Iterable[str],
) -> set[str]:
    terms = [term.lower() for term in required_terms]

    if not terms:
        return set()

    matching_documents = index.get(terms[0], set()).copy()

    for term in terms[1:]:
        matching_documents &= index.get(term, set())

    return matching_documents


def inverted_index_example() -> None:
    print("\n" + "=" * 78)
    print("13. INVERTED INDEX")
    print("=" * 78)

    documents = {
        "doc1": "Python supports set operations and dictionaries.",
        "doc2": "Set operations are useful for data processing.",
        "doc3": "Python data structures include lists sets and dictionaries.",
    }

    index = build_inverted_index(documents)

    print("Documents containing 'python':", index.get("python", set()))
    print(
        "Documents containing both 'set' and 'operations':",
        search_documents(index, ["set", "operations"]),
    )


# ============================================================================
# 14. GRAPH APPLICATION
# ============================================================================

def graph_neighbors_example() -> None:
    print("\n" + "=" * 78)
    print("14. GRAPH APPLICATION")
    print("=" * 78)

    graph = {
        "A": {"B", "C"},
        "B": {"A", "C", "D"},
        "C": {"A", "B"},
        "D": {"B"},
    }

    # Neighbor sets make operations such as common-neighbor detection simple.
    common_neighbors = graph["A"] & graph["B"]
    print("Common neighbors of A and B:", common_neighbors)

    # A set is also useful for tracking visited graph vertices.
    visited: set[str] = set()
    stack = ["A"]

    while stack:
        vertex = stack.pop()

        if vertex in visited:
            continue

        visited.add(vertex)
        stack.extend(graph[vertex] - visited)

    print("Visited vertices:", visited)


# ============================================================================
# 15. PERFORMANCE
# ============================================================================

def performance_example() -> None:
    print("\n" + "=" * 78)
    print("15. PERFORMANCE")
    print("=" * 78)

    size = 100_000
    values = list(range(size))
    value_set = set(values)
    target = size - 1

    start = perf_counter()
    _ = target in values
    list_time = perf_counter() - start

    start = perf_counter()
    _ = target in value_set
    set_time = perf_counter() - start

    print(f"Membership in list: {list_time:.8f} seconds")
    print(f"Membership in set:  {set_time:.8f} seconds")
    print(
        "Typical set membership is average O(1), while list membership is O(n)."
    )
    print(
        "Measured times depend on hardware, Python version, workload, and cache."
    )


# ============================================================================
# 16. TESTS
# ============================================================================

def run_tests() -> None:
    print("\n" + "=" * 78)
    print("16. SELF-TESTS")
    print("=" * 78)

    A = {1, 2, 3}
    B = {3, 4, 5}

    assert A | B == {1, 2, 3, 4, 5}
    assert A & B == {3}
    assert A - B == {1, 2}
    assert A ^ B == {1, 2, 4, 5}
    assert {1, 2}.issubset(A)
    assert A.issuperset({1, 2})
    assert A.isdisjoint({8, 9})
    assert unique_preserving_order([1, 2, 1, 3]) == [1, 2, 3]
    assert multiset_difference(["a", "a", "b"], ["a"]) == ["a", "b"]

    print("All tests passed.")


# ============================================================================
# 17. PRACTICAL DATA-QUALITY PIPELINE
# ============================================================================

@dataclass
class DataQualityReport:
    total_records: int
    unique_records: int
    duplicates: set[str]
    blank_records: set[str]


def analyze_records(records: Iterable[str]) -> DataQualityReport:
    normalized = [record.strip().lower() for record in records]
    unique_records = set(normalized)

    duplicates = {
        value for value in unique_records if normalized.count(value) > 1
    }
    blank_records = {value for value in unique_records if not value}

    return DataQualityReport(
        total_records=len(normalized),
        unique_records=len(unique_records),
        duplicates=duplicates,
        blank_records=blank_records,
    )


def data_quality_example() -> None:
    print("\n" + "=" * 78)
    print("17. DATA-QUALITY PIPELINE")
    print("=" * 78)

    records = [
        "Alice@example.com",
        "alice@example.com",
        " bob@example.com ",
        "",
        "carol@example.com",
        "BOB@EXAMPLE.COM",
    ]

    report = analyze_records(records)

    print("Total records:", report.total_records)
    print("Unique records:", report.unique_records)
    print("Duplicates:", report.duplicates)
    print("Blank values:", report.blank_records)


# ============================================================================
# 18. ADVANCED NOTES
# ============================================================================

def advanced_notes() -> None:
    print("\n" + "=" * 78)
    print("18. ADVANCED NOTES")
    print("=" * 78)

    print("Set elements must be hashable.")
    print("Hashable objects need stable hashing/equality behavior.")
    print("Mutating an object in a way that changes its hash while it is used")
    print("as a set element would violate the set's lookup assumptions.")
    print("frozenset is the immutable counterpart of set.")
    print("set operations normally provide average constant-time membership.")
    print("Worst-case hash-table behavior can degrade under pathological collisions.")
    print("Set ordering should not be treated as an application contract.")
    print("Sets discard duplicates and therefore cannot represent multiplicity.")
    print("For counts, use a frequency map or Counter.")
    print("For deterministic presentation, sort the resulting set explicitly.")


# ============================================================================
# 19. MAIN
# ============================================================================

def main() -> None:
    print("=" * 78)
    print("SET OPERATIONS: BEGINNER TO ADVANCED")
    print("=" * 78)

    fundamentals()
    creation_and_conversion()
    mutation_operations()
    mathematical_operations()
    set_relations()
    set_comprehensions()
    access_control_example()
    reconciliation_example()
    advanced_collection_examples()
    hashability_and_edge_cases()
    collection_comparison()
    algorithmic_examples()
    inverted_index_example()
    graph_neighbors_example()
    performance_example()
    data_quality_example()
    advanced_notes()
    run_tests()

    print("\n" + "=" * 78)
    print("END OF SET OPERATIONS STUDY FILE")
    print("=" * 78)


if __name__ == "__main__":
    main()
