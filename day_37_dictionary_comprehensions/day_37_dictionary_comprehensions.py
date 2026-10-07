"""
Dictionary Comprehensions: beginner-to-advanced executable study.

This script focuses specifically on dictionary comprehensions:
- basic construction
- filtering
- transformation
- conditional values
- nested comprehensions
- inversion and grouping
- handling duplicates
- merging mappings
- parsing structured records
- frequency tables
- indexing data
- validation
- performance considerations
- common mistakes
- practical data-processing workflows

Run with Python 3.10+.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from time import perf_counter
from typing import Iterable


def heading(title: str) -> None:
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


# ---------------------------------------------------------------------------
# Fundamental dictionary comprehensions
# ---------------------------------------------------------------------------

def basic_comprehension() -> None:
    heading("Basic dictionary comprehension")

    numbers = range(1, 6)

    # The expression before the colon becomes the key.
    # The expression after the colon becomes the value.
    squares = {number: number * number for number in numbers}

    print("Squares:", squares)


def transformation_comprehension() -> None:
    heading("Transforming an existing mapping")

    prices = {
        "keyboard": 2499,
        "mouse": 1299,
        "monitor": 18999,
        "headset": 3499,
    }

    # Iterating over items() gives access to both keys and values.
    discounted_prices = {
        product: round(price * 0.90, 2)
        for product, price in prices.items()
    }

    print("Original:", prices)
    print("After 10% discount:", discounted_prices)


def key_transformation() -> None:
    heading("Transforming keys")

    temperatures_celsius = {
        "delhi": 31,
        "mumbai": 29,
        "lucknow": 30,
    }

    normalized = {
        city.upper(): temperature
        for city, temperature in temperatures_celsius.items()
    }

    print(normalized)


# ---------------------------------------------------------------------------
# Filtering and conditional values
# ---------------------------------------------------------------------------

def filtering() -> None:
    heading("Filtering entries")

    scores = {
        "Asha": 91,
        "Rahul": 67,
        "Meera": 84,
        "Vikram": 48,
        "Neha": 76,
    }

    # Only entries satisfying the condition are inserted.
    passed = {
        student: score
        for student, score in scores.items()
        if score >= 50
    }

    print("Passed:", passed)


def conditional_values() -> None:
    heading("Conditional expressions inside a comprehension")

    scores = {
        "Asha": 91,
        "Rahul": 67,
        "Meera": 84,
        "Vikram": 48,
    }

    # The if/else expression changes the value for every retained key.
    grades = {
        student: "PASS" if score >= 50 else "FAIL"
        for student, score in scores.items()
    }

    print("Grades:", grades)


def filtering_and_transformation() -> None:
    heading("Filtering and transformation together")

    inventory = {
        "SSD": 8,
        "RAM": 3,
        "GPU": 2,
        "CPU": 11,
        "HDD": 0,
    }

    low_stock = {
        item: quantity
        for item, quantity in inventory.items()
        if 0 < quantity < 5
    }

    print("Low-stock items:", low_stock)


# ---------------------------------------------------------------------------
# Dictionary methods and comprehension inputs
# ---------------------------------------------------------------------------

def keys_values_items() -> None:
    heading("Keys, values, and items")

    data = {"a": 10, "b": 20, "c": 30}

    from_keys = {key: key.upper() for key in data.keys()}
    from_values = {value: value * 2 for value in data.values()}
    from_items = {key: value + 100 for key, value in data.items()}

    print("From keys:", from_keys)
    print("From values:", from_values)
    print("From items:", from_items)


def zip_into_dictionary() -> None:
    heading("Building dictionaries from parallel sequences")

    names = ["Asha", "Rahul", "Meera"]
    scores = [91, 78, 86]

    if len(names) != len(scores):
        raise ValueError("Names and scores must have the same length.")

    result = {name: score for name, score in zip(names, scores)}

    print(result)


# ---------------------------------------------------------------------------
# Inverting mappings
# ---------------------------------------------------------------------------

def invert_mapping() -> None:
    heading("Inverting a dictionary")

    country_codes = {
        "India": "IN",
        "Japan": "JP",
        "Germany": "DE",
    }

    inverted = {
        code: country
        for country, code in country_codes.items()
    }

    print("Inverted:", inverted)


def demonstrate_duplicate_key_problem() -> None:
    heading("Duplicate keys during inversion")

    departments = {
        "Asha": "Engineering",
        "Rahul": "Engineering",
        "Meera": "Finance",
    }

    # A dictionary cannot preserve multiple values for the same key.
    # Rahul therefore replaces Asha when both map to "Engineering".
    naive = {
        department: employee
        for employee, department in departments.items()
    }

    print("Naive inversion:", naive)

    # When duplicates matter, use a list as the dictionary value.
    grouped: dict[str, list[str]] = defaultdict(list)

    for employee, department in departments.items():
        grouped[department].append(employee)

    grouped_result = {
        department: employees
        for department, employees in grouped.items()
    }

    print("Duplicate-safe grouping:", grouped_result)


# ---------------------------------------------------------------------------
# Nested comprehensions
# ---------------------------------------------------------------------------

def nested_comprehension() -> None:
    heading("Nested dictionary comprehension")

    matrix = {
        row: {
            column: row * column
            for column in range(1, 5)
        }
        for row in range(1, 4)
    }

    print("Multiplication matrix:")
    for row, values in matrix.items():
        print(row, values)


def flatten_nested_mapping() -> None:
    heading("Flattening a nested dictionary")

    departments = {
        "Engineering": {"Asha": 91, "Rahul": 87},
        "Finance": {"Meera": 94, "Vikram": 79},
    }

    flattened = {
        f"{department}:{employee}": score
        for department, employees in departments.items()
        for employee, score in employees.items()
    }

    print(flattened)


# ---------------------------------------------------------------------------
# Realistic data processing
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Employee:
    employee_id: int
    name: str
    department: str
    salary: int
    active: bool


def employee_index() -> None:
    heading("Indexing records by identifier")

    employees = [
        Employee(101, "Asha", "Engineering", 95000, True),
        Employee(102, "Rahul", "Finance", 72000, True),
        Employee(103, "Meera", "Engineering", 105000, False),
        Employee(104, "Vikram", "Operations", 68000, True),
    ]

    active_employee_index = {
        employee.employee_id: employee
        for employee in employees
        if employee.active
    }

    print("Active employee index:")
    for employee_id, employee in active_employee_index.items():
        print(employee_id, employee)


def salary_band_index() -> None:
    heading("Computing derived values")

    salaries = {
        "Asha": 95000,
        "Rahul": 72000,
        "Meera": 105000,
        "Vikram": 68000,
    }

    def band(salary: int) -> str:
        if salary >= 100000:
            return "senior"
        if salary >= 75000:
            return "mid"
        return "entry"

    bands = {
        employee: band(salary)
        for employee, salary in salaries.items()
    }

    print("Salary bands:", bands)


def parse_records() -> None:
    heading("Parsing structured records")

    raw_records = [
        "101,Asha,Engineering,95000",
        "102,Rahul,Finance,72000",
        "103,Meera,Engineering,105000",
    ]

    employees = {}
    for record in raw_records:
        parts = [part.strip() for part in record.split(",")]

        if len(parts) != 4:
            raise ValueError(f"Invalid employee record: {record}")

        employee_id_text, name, department, salary_text = parts

        try:
            employee_id = int(employee_id_text)
            salary = int(salary_text)
        except ValueError as exc:
            raise ValueError(f"Invalid numeric field: {record}") from exc

        employees[employee_id] = {
            "name": name,
            "department": department,
            "salary": salary,
        }

    high_value = {
        employee_id: employee
        for employee_id, employee in employees.items()
        if employee["salary"] >= 90000
    }

    print("High-value employees:", high_value)


# ---------------------------------------------------------------------------
# Frequency analysis
# ---------------------------------------------------------------------------

def word_frequency() -> None:
    heading("Frequency analysis")

    text = """
    data quality depends on clean data
    clean data supports reliable analysis
    reliable analysis supports reliable decisions
    """

    words = [
        word.strip(".,!?").lower()
        for word in text.split()
        if word.strip(".,!?")
    ]

    frequency = Counter(words)

    # Counter is useful when counting is the primary operation.
    # A comprehension is useful when deriving a new dictionary from it.
    frequent_words = {
        word: count
        for word, count in frequency.items()
        if count >= 2
    }

    print("Repeated words:", frequent_words)


# ---------------------------------------------------------------------------
# Conditional categorization
# ---------------------------------------------------------------------------

def transaction_classification() -> None:
    heading("Classifying transactions")

    transactions = {
        "TX1001": 450,
        "TX1002": 17500,
        "TX1003": 89000,
        "TX1004": -250,
        "TX1005": 6200,
    }

    classification = {
        transaction_id: (
            "invalid" if amount < 0
            else "high" if amount >= 50000
            else "medium" if amount >= 10000
            else "low"
        )
        for transaction_id, amount in transactions.items()
    }

    print(classification)


# ---------------------------------------------------------------------------
# Safe filtering and validation
# ---------------------------------------------------------------------------

def validate_mapping_input(data: dict[str, int]) -> None:
    if not isinstance(data, dict):
        raise TypeError("Expected a dictionary.")

    invalid = {
        key: value
        for key, value in data.items()
        if not isinstance(key, str) or not isinstance(value, int)
    }

    if invalid:
        raise ValueError(f"Invalid entries: {invalid}")


def validated_comprehension() -> None:
    heading("Validation before transformation")

    data = {
        "orders": 120,
        "returns": 7,
        "customers": 83,
    }

    validate_mapping_input(data)

    percentages = {
        key: round(value / 120 * 100, 2)
        for key, value in data.items()
    }

    print(percentages)


# ---------------------------------------------------------------------------
# Dictionary comprehension with sets and derived keys
# ---------------------------------------------------------------------------

def unique_domain_index() -> None:
    heading("Creating a domain index")

    emails = [
        "asha@example.com",
        "rahul@example.com",
        "meera@example.org",
        "asha@example.com",
    ]

    unique_domains = {
        email.split("@", 1)[1]
        for email in emails
        if "@" in email
    }

    domain_index = {
        domain: [
            email
            for email in emails
            if email.endswith("@" + domain)
        ]
        for domain in unique_domains
    }

    print("Domains:", unique_domains)
    print("Domain index:", domain_index)


# ---------------------------------------------------------------------------
# Merge and precedence behavior
# ---------------------------------------------------------------------------

def merge_mappings() -> None:
    heading("Merging mappings before comprehension")

    defaults = {
        "timeout": 30,
        "retries": 3,
        "region": "ap-south-1",
    }

    overrides = {
        "timeout": 60,
        "region": "eu-west-1",
    }

    merged = {**defaults, **overrides}

    # The later mapping wins when keys collide.
    normalized = {
        key: value
        for key, value in merged.items()
    }

    print("Merged configuration:", normalized)


# ---------------------------------------------------------------------------
# Advanced dictionary comprehension patterns
# ---------------------------------------------------------------------------

def transpose_mapping() -> None:
    heading("Transposing a rectangular mapping")

    sales = {
        "January": {"North": 100, "South": 120, "West": 90},
        "February": {"North": 130, "South": 110, "West": 95},
    }

    regions = {
        region
        for monthly_data in sales.values()
        for region in monthly_data
    }

    transposed = {
        region: {
            month: sales[month][region]
            for month in sales
        }
        for region in regions
    }

    print(transposed)


def aggregate_with_comprehension() -> None:
    heading("Aggregation using a derived index")

    orders = [
        {"customer": "Asha", "amount": 1200},
        {"customer": "Rahul", "amount": 800},
        {"customer": "Asha", "amount": 700},
        {"customer": "Meera", "amount": 2500},
        {"customer": "Rahul", "amount": 500},
    ]

    totals: dict[str, int] = defaultdict(int)

    for order in orders:
        customer = order.get("customer")
        amount = order.get("amount")

        if not isinstance(customer, str) or not customer:
            raise ValueError("Order has an invalid customer.")

        if not isinstance(amount, int) or amount < 0:
            raise ValueError("Order has an invalid amount.")

        totals[customer] += amount

    high_value_customers = {
        customer: total
        for customer, total in totals.items()
        if total >= 1500
    }

    print("High-value customers:", high_value_customers)


def comprehension_with_function() -> None:
    heading("Using a domain function inside a comprehension")

    def normalize_phone(phone: str) -> str:
        digits = "".join(character for character in phone if character.isdigit())

        if len(digits) == 10:
            return "+91" + digits

        if len(digits) == 12 and digits.startswith("91"):
            return "+" + digits

        raise ValueError(f"Unsupported phone number: {phone}")

    contacts = {
        "Asha": "98765-43210",
        "Rahul": "+91 91234 56789",
    }

    normalized = {
        name: normalize_phone(phone)
        for name, phone in contacts.items()
    }

    print(normalized)


# ---------------------------------------------------------------------------
# Performance comparison
# ---------------------------------------------------------------------------

def performance_comparison() -> None:
    heading("Performance characteristics")

    values = range(1, 200_000)

    start = perf_counter()
    comprehension_result = {
        number: number * number
        for number in values
    }
    comprehension_time = perf_counter() - start

    start = perf_counter()
    loop_result: dict[int, int] = {}
    for number in values:
        loop_result[number] = number * number
    loop_time = perf_counter() - start

    print(f"Comprehension: {comprehension_time:.6f}s")
    print(f"Loop:          {loop_time:.6f}s")
    print("Results equivalent:", comprehension_result == loop_result)

    # A comprehension creates the complete dictionary in memory.
    # For very large datasets, streaming or chunked processing may be better.


# ---------------------------------------------------------------------------
# Common mistakes and edge cases
# ---------------------------------------------------------------------------

def common_mistakes() -> None:
    heading("Common mistakes")

    # Mistake: using a mutable object as an accidental shared value.
    # Each comprehension iteration creates a separate list here.
    safe_lists = {
        key: []
        for key in ("a", "b", "c")
    }

    safe_lists["a"].append(10)

    print("Independent lists:", safe_lists)

    # Duplicate keys are silently overwritten.
    duplicate_keys = {
        "status": "draft",
        "status": "approved",
    }

    print("Duplicate key result:", duplicate_keys)

    # Filtering happens after the key/value expression is considered
    # syntactically, but only matching entries are inserted.
    positive = {
        number: number
        for number in [-2, -1, 0, 1, 2]
        if number > 0
    }

    print("Positive values:", positive)


def avoid_excessive_nesting() -> None:
    heading("Readability boundary")

    records = {
        "A": [10, 20, 30],
        "B": [40, 50],
        "C": [60],
    }

    # This is concise while remaining readable.
    totals = {
        key: sum(values)
        for key, values in records.items()
    }

    print("Totals:", totals)

    # Deeply nested comprehensions can become harder to verify and debug.
    # When the business rule becomes complex, a normal loop or helper
    # function is often clearer.


# ---------------------------------------------------------------------------
# Practical reporting workflow
# ---------------------------------------------------------------------------

def build_operational_report() -> None:
    heading("Practical operational report")

    raw_metrics = {
        "orders_processed": 12_450,
        "orders_failed": 137,
        "orders_delayed": 421,
        "refunds": 82,
    }

    if raw_metrics["orders_processed"] <= 0:
        raise ValueError("Processed order count must be positive.")

    rates = {
        metric.replace("_", " "): round(value / raw_metrics["orders_processed"] * 100, 2)
        for metric, value in raw_metrics.items()
        if metric != "orders_processed"
    }

    alerts = {
        metric: rate
        for metric, rate in rates.items()
        if rate >= 3.0
    }

    report = {
        "rates_percent": rates,
        "alerts": alerts,
        "alert_count": len(alerts),
    }

    print(report)


# ---------------------------------------------------------------------------
# Main executable demonstration
# ---------------------------------------------------------------------------

def main() -> None:
    basic_comprehension()
    transformation_comprehension()
    key_transformation()
    filtering()
    conditional_values()
    filtering_and_transformation()
    keys_values_items()
    zip_into_dictionary()
    invert_mapping()
    demonstrate_duplicate_key_problem()
    nested_comprehension()
    flatten_nested_mapping()
    employee_index()
    salary_band_index()
    parse_records()
    word_frequency()
    transaction_classification()
    validated_comprehension()
    unique_domain_index()
    merge_mappings()
    transpose_mapping()
    aggregate_with_comprehension()
    comprehension_with_function()
    performance_comparison()
    common_mistakes()
    avoid_excessive_nesting()
    build_operational_report()


if __name__ == "__main__":
    main()
