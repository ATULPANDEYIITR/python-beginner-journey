"""
Unpacking in Python
A comprehensive executable demonstration from fundamental sequence unpacking
through iterable unpacking, starred targets, dictionary unpacking, function
arguments, nested structures, pattern matching, validation, and advanced
real-world data-processing patterns.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections import deque
from itertools import islice
from pathlib import Path
from typing import Any, Iterable, Iterator


def heading(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def show(label: str, value: Any) -> None:
    print(f"{label}: {value!r}")


# ---------------------------------------------------------------------------
# Fundamental sequence unpacking
# ---------------------------------------------------------------------------

def demonstrate_basic_unpacking() -> None:
    heading("Basic sequence unpacking")

    employee = ("E104", "Atul", "Operations")
    employee_id, name, department = employee

    show("employee_id", employee_id)
    show("name", name)
    show("department", department)

    # Lists, tuples, and other finite iterables can all participate in
    # assignment unpacking as long as the number of produced values matches.
    coordinates = [28.6139, 77.2090]
    latitude, longitude = coordinates
    show("latitude", latitude)
    show("longitude", longitude)

    # Strings are iterables, so every character can become a target.
    first, second, third = "API"
    show("characters", (first, second, third))

    try:
        first, second = [10, 20, 30]
    except ValueError as exc:
        print(f"Too many values for targets: {exc}")

    try:
        first, second, third = [10, 20]
    except ValueError as exc:
        print(f"Too few values for targets: {exc}")


# ---------------------------------------------------------------------------
# Starred unpacking
# ---------------------------------------------------------------------------

def demonstrate_starred_unpacking() -> None:
    heading("Starred unpacking")

    values = [10, 20, 30, 40, 50]
    first, *middle, last = values

    show("first", first)
    show("middle", middle)
    show("last", last)

    first, second, *remaining = values
    show("first two", (first, second))
    show("remaining", remaining)

    *leading, second_last, last = values
    show("leading", leading)
    show("last two", (second_last, last))

    # A starred target always receives a list, even when the source is a tuple.
    *items, = (1, 2, 3)
    show("starred tuple result", items)

    # The starred target may legally receive zero values.
    first, *nothing = [99]
    show("first", first)
    show("empty starred target", nothing)

    # Only one starred target can occur at a single unpacking level.
    try:
        compile("a, *b, *c = [1, 2, 3]", "<unpacking>", "exec")
    except SyntaxError as exc:
        print(f"Multiple starred targets are invalid: {exc}")


# ---------------------------------------------------------------------------
# Nested unpacking
# ---------------------------------------------------------------------------

def demonstrate_nested_unpacking() -> None:
    heading("Nested unpacking")

    records = [
        ("E101", ("Engineering", "Platform"), 92000),
        ("E102", ("Operations", "Analytics"), 87000),
    ]

    for employee_id, (division, team), salary in records:
        print(
            f"id={employee_id}, division={division}, "
            f"team={team}, salary={salary}"
        )

    # The structure of the target mirrors the structure of the data.
    response = {
        "status": 200,
        "body": ("OK", {"request_id": "req-782"}),
    }

    status, (message, metadata) = response["status"], response["body"]
    show("status", status)
    show("message", message)
    show("metadata", metadata)

    # Starred targets can also appear inside nested structures.
    dataset = [
        ("sales", [120, 130, 125, 140]),
        ("support", [90, 95, 88]),
    ]

    for department, [first, *rest] in dataset:
        print(f"{department}: first={first}, remaining={rest}")


# ---------------------------------------------------------------------------
# Swapping and multiple assignment
# ---------------------------------------------------------------------------

def demonstrate_swapping() -> None:
    heading("Swapping and multiple assignment")

    left = "production"
    right = "staging"

    # Python evaluates the right-hand side before assigning targets, so no
    # temporary variable is required for a safe swap.
    left, right = right, left

    show("left after swap", left)
    show("right after swap", right)

    current, previous, baseline = 120, 110, 100
    current, previous, baseline = previous, baseline, current

    show("rotated values", (current, previous, baseline))


# ---------------------------------------------------------------------------
# Function argument unpacking
# ---------------------------------------------------------------------------

def calculate_risk_score(volatility: float, exposure: float, confidence: float) -> float:
    return round(volatility * exposure * confidence, 4)


def demonstrate_function_unpacking() -> None:
    heading("Function argument unpacking")

    values = (0.18, 0.75, 0.92)

    # * expands an iterable into positional arguments.
    score = calculate_risk_score(*values)
    show("positional expansion", score)

    configuration = {
        "volatility": 0.18,
        "exposure": 0.75,
        "confidence": 0.92,
    }

    # ** expands a mapping into keyword arguments. Keys must match the
    # function's parameter names unless the function accepts **kwargs.
    score = calculate_risk_score(**configuration)
    show("keyword expansion", score)

    mixed = (0.18, 0.75)
    named = {"confidence": 0.92}
    score = calculate_risk_score(*mixed, **named)
    show("mixed expansion", score)


# ---------------------------------------------------------------------------
# Function definitions that receive unpacked arguments
# ---------------------------------------------------------------------------

def collect_metrics(*values: float, **metadata: str) -> dict[str, Any]:
    return {
        "values": values,
        "metadata": metadata,
        "count": len(values),
    }


def demonstrate_variadic_unpacking() -> None:
    heading("Variadic arguments and unpacking")

    result = collect_metrics(
        91.2,
        88.7,
        94.5,
        source="production",
        owner="operations",
    )

    show("collected result", result)

    measurements = [72.5, 81.0, 77.5]
    labels = {"system": "warehouse", "region": "north"}

    result = collect_metrics(*measurements, **labels)
    show("expanded into variadic function", result)


# ---------------------------------------------------------------------------
# Iterable unpacking beyond lists and tuples
# ---------------------------------------------------------------------------

def generate_events() -> Iterator[str]:
    yield "created"
    yield "validated"
    yield "processed"
    yield "archived"


def demonstrate_iterable_unpacking() -> None:
    heading("Unpacking arbitrary iterables")

    first, *remaining = generate_events()

    show("first event", first)
    show("remaining events", remaining)

    values = iter(range(5))
    first, second, *rest = values

    show("first", first)
    show("second", second)
    show("rest", rest)

    # A deque is iterable and therefore can be unpacked.
    queue = deque(["request", "validate", "complete"])
    action, *future_actions = queue

    show("action", action)
    show("future_actions", future_actions)


# ---------------------------------------------------------------------------
# Dictionary unpacking
# ---------------------------------------------------------------------------

def demonstrate_dictionary_unpacking() -> None:
    heading("Dictionary unpacking")

    identity = {
        "id": "E101",
        "name": "Atul",
    }

    employment = {
        "department": "Operations",
        "role": "Analyst",
    }

    employee = {**identity, **employment}
    show("merged dictionary", employee)

    # Later keys override earlier keys when the same key occurs.
    defaults = {
        "timeout": 30,
        "retries": 3,
        "mode": "safe",
    }

    overrides = {
        "timeout": 60,
        "mode": "strict",
    }

    configuration = {**defaults, **overrides}
    show("configuration", configuration)

    # Python 3.9+ also supports the dictionary union operators.
    alternative = defaults | overrides
    show("dictionary union", alternative)

    # Dictionary unpacking is useful for constructing immutable-style
    # snapshots without mutating the original mapping.
    original = {"region": "north", "active": True}
    updated = {**original, "active": False}

    show("original", original)
    show("updated copy", updated)


# ---------------------------------------------------------------------------
# Sequence unpacking in loops
# ---------------------------------------------------------------------------

def demonstrate_loop_unpacking() -> None:
    heading("Unpacking in loops")

    employees = [
        ("E101", "Engineering", 92000),
        ("E102", "Operations", 87000),
        ("E103", "Finance", 99000),
    ]

    for employee_id, department, salary in employees:
        print(f"{employee_id}: {department}, salary={salary}")

    # enumerate() returns two-value tuples, making it natural for unpacking.
    for position, employee in enumerate(employees, start=1):
        employee_id, department, salary = employee
        print(f"{position}: {employee_id} -> {department}")

    # zip() produces tuples whose values can be unpacked directly.
    employee_ids = ["E101", "E102", "E103"]
    departments = ["Engineering", "Operations", "Finance"]

    for employee_id, department in zip(employee_ids, departments):
        print(f"{employee_id} works in {department}")


# ---------------------------------------------------------------------------
# Extended iterable unpacking with structured records
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    account: str
    amount: float
    tags: tuple[str, ...]


def summarize_transactions(transactions: Iterable[Transaction]) -> dict[str, float]:
    totals: dict[str, float] = {}

    for transaction in transactions:
        transaction_id, account, amount, *tag_values = (
            transaction.transaction_id,
            transaction.account,
            transaction.amount,
            *transaction.tags,
        )

        # The unpacking above demonstrates that a structured record can be
        # decomposed before domain-specific processing occurs.
        if not transaction_id or not account:
            raise ValueError("Transaction identity cannot be empty")

        if amount < 0:
            raise ValueError(f"Negative amount for {transaction_id}")

        totals[account] = totals.get(account, 0.0) + amount

        if "ignored" in tag_values:
            totals[account] -= amount

    return totals


def demonstrate_dataclass_unpacking() -> None:
    heading("Unpacking structured domain data")

    transactions = [
        Transaction("T001", "A-100", 1250.0, ("approved", "online")),
        Transaction("T002", "A-100", 500.0, ("approved",)),
        Transaction("T003", "A-200", 800.0, ("approved", "ignored")),
    ]

    totals = summarize_transactions(transactions)
    show("account totals", totals)


# ---------------------------------------------------------------------------
# Parsing records with unpacking
# ---------------------------------------------------------------------------

def parse_csv_like_record(line: str) -> dict[str, str]:
    fields = [field.strip() for field in line.split(",")]

    if len(fields) < 3:
        raise ValueError(
            "Record must contain at least id, department, and status"
        )

    record_id, department, status, *extra_fields = fields

    if not record_id:
        raise ValueError("Record ID cannot be empty")

    if not department:
        raise ValueError("Department cannot be empty")

    if status not in {"active", "inactive", "pending"}:
        raise ValueError(f"Unsupported status: {status}")

    return {
        "id": record_id,
        "department": department,
        "status": status,
        "extra_fields": "|".join(extra_fields),
    }


def demonstrate_record_parsing() -> None:
    heading("Unpacking during record parsing")

    lines = [
        "E101,Engineering,active,platform",
        "E102,Operations,pending,analytics",
        "E103,Finance,inactive",
    ]

    for line in lines:
        print(parse_csv_like_record(line))

    try:
        parse_csv_like_record("E999,,active")
    except ValueError as exc:
        print(f"Rejected record: {exc}")


# ---------------------------------------------------------------------------
# Unpacking file paths
# ---------------------------------------------------------------------------

def demonstrate_path_unpacking() -> None:
    heading("Unpacking pathlib-derived information")

    path = Path("/var/log/application/production.log")

    parent = path.parent
    filename = path.name
    suffix = path.suffix

    show("parent", parent)
    show("filename", filename)
    show("suffix", suffix)

    # pathlib.Path itself is not a sequence to unpack. The safe approach is
    # to explicitly convert its meaningful attributes into an iterable.
    path_parts = (str(parent), filename, suffix)
    parent_text, filename_text, extension = path_parts

    show("unpacked path information", (parent_text, filename_text, extension))


# ---------------------------------------------------------------------------
# Unpacking with APIs and response records
# ---------------------------------------------------------------------------

def process_api_response(response: dict[str, Any]) -> dict[str, Any]:
    required_keys = {"status", "data"}

    missing = required_keys - response.keys()
    if missing:
        raise ValueError(f"Missing API response keys: {sorted(missing)}")

    status = response["status"]
    payload = response["data"]

    if not isinstance(status, int):
        raise TypeError("status must be an integer")

    if status < 200 or status >= 600:
        raise ValueError("status must be an HTTP-style status code")

    if not isinstance(payload, dict):
        raise TypeError("data must be a dictionary")

    # Explicitly create an iterable because dictionary values have no
    # positional semantic contract by themselves.
    payload_values = (
        payload.get("request_id"),
        payload.get("records", []),
        payload.get("next_page"),
    )

    request_id, records, next_page = payload_values

    if not isinstance(records, list):
        raise TypeError("records must be a list")

    return {
        "status": status,
        "request_id": request_id,
        "record_count": len(records),
        "next_page": next_page,
    }


def demonstrate_api_unpacking() -> None:
    heading("Unpacking API response structures")

    response = {
        "status": 200,
        "data": {
            "request_id": "req-2048",
            "records": [
                {"id": "R1", "value": 18},
                {"id": "R2", "value": 21},
            ],
            "next_page": None,
        },
    }

    show("processed response", process_api_response(response))

    try:
        process_api_response({"status": 200})
    except ValueError as exc:
        print(f"Invalid response: {exc}")


# ---------------------------------------------------------------------------
# Generator consumption and a common unpacking pitfall
# ---------------------------------------------------------------------------

def demonstrate_generator_behavior() -> None:
    heading("Generator consumption and unpacking")

    def numbers() -> Iterator[int]:
        for value in range(1, 6):
            yield value

    generator = numbers()

    first, *rest = generator

    show("first generated value", first)
    show("rest generated values", rest)

    # The generator has now been consumed. Unpacking did not copy an invisible
    # reusable sequence; it consumed values from the iterator.
    show("remaining generator values", list(generator))

    # If the data must be reused, materialize it deliberately.
    reusable = list(numbers())
    first, *rest = reusable

    show("reusable first", first)
    show("reusable rest", rest)


# ---------------------------------------------------------------------------
# Memory and performance considerations
# ---------------------------------------------------------------------------

def demonstrate_performance_tradeoff() -> None:
    heading("Performance considerations")

    def streaming_values() -> Iterator[int]:
        yield from range(1_000_000)

    # Starred unpacking must collect all remaining values into a list. This
    # can be expensive for very large or unbounded iterators.
    first, *rest = streaming_values()

    show("first streamed value", first)
    print(f"Starred target materialized {len(rest):,} values.")

    # islice provides a streaming alternative when only a bounded prefix is
    # required and avoids materializing the remainder.
    iterator = streaming_values()
    first = next(iterator)
    preview = list(islice(iterator, 4))

    show("streaming first", first)
    show("streaming preview", preview)


# ---------------------------------------------------------------------------
# Safe handling of unknown iterable sizes
# ---------------------------------------------------------------------------

def first_and_optional_rest(values: Iterable[Any]) -> tuple[Any | None, list[Any]]:
    iterator = iter(values)

    try:
        first = next(iterator)
    except StopIteration:
        return None, []

    return first, list(iterator)


def demonstrate_unknown_sizes() -> None:
    heading("Handling unknown iterable sizes")

    for values in ([], [42], [42, 43, 44]):
        first, rest = first_and_optional_rest(values)
        print(f"source={values!r}, first={first!r}, rest={rest!r}")


# ---------------------------------------------------------------------------
# Structural pattern matching
# ---------------------------------------------------------------------------

def classify_message(message: object) -> str:
    match message:
        case ("ERROR", code, description):
            return f"error code={code}: {description}"
        case ("SUCCESS", code, *details):
            return f"success code={code}, details={details}"
        case {"status": "pending", "id": request_id}:
            return f"pending request={request_id}"
        case {"status": status, **remaining}:
            return f"status={status}, metadata={remaining}"
        case _:
            return "unrecognized message"


def demonstrate_pattern_matching() -> None:
    heading("Pattern matching and structural unpacking")

    messages = [
        ("ERROR", 503, "service unavailable"),
        ("SUCCESS", 200, "cached", "validated"),
        {"status": "pending", "id": "REQ-12"},
        {"status": "failed", "reason": "timeout"},
        "unexpected",
    ]

    for message in messages:
        print(classify_message(message))


# ---------------------------------------------------------------------------
# Designing functions around unpacking
# ---------------------------------------------------------------------------

def split_measurements(
    measurements: Iterable[float],
) -> tuple[float | None, list[float]]:
    first, *rest = measurements
    return first if "first" in locals() else None, rest


def normalize_record(record: tuple[str, str, float, str]) -> dict[str, Any]:
    record_id, category, value, status = record

    if status not in {"valid", "invalid"}:
        raise ValueError("status must be 'valid' or 'invalid'")

    return {
        "id": record_id,
        "category": category,
        "value": value,
        "status": status,
    }


def demonstrate_api_design() -> None:
    heading("API design with unpacking")

    records = [
        ("M001", "latency", 84.5, "valid"),
        ("M002", "latency", 125.2, "valid"),
    ]

    normalized = [normalize_record(record) for record in records]

    for record in normalized:
        print(record)

    first, rest = split_measurements([10.5, 20.5, 30.5])
    show("first measurement", first)
    show("remaining measurements", rest)

    first, rest = split_measurements([])
    show("empty input first", first)
    show("empty input rest", rest)


# ---------------------------------------------------------------------------
# Common mistakes
# ---------------------------------------------------------------------------

def demonstrate_common_mistakes() -> None:
    heading("Common unpacking mistakes")

    # Accidentally unpacking a string character-by-character.
    username = "Atul"
    first, *remaining = username
    show("string first character", first)
    show("string remaining characters", remaining)

    # The comma creates a tuple; parentheses alone do not.
    single_value_tuple = ("production",)
    not_a_tuple = ("production")

    show("single-value tuple", single_value_tuple)
    show("plain string", not_a_tuple)

    # Dictionary iteration yields keys, not key-value pairs.
    settings = {"timeout": 30, "retries": 3}

    key_a, key_b = settings
    show("unpacked dictionary keys", (key_a, key_b))

    # items() is the correct iterable when both keys and values are needed.
    for key, value in settings.items():
        print(f"{key}={value}")

    # The number of targets must agree unless a starred target absorbs the
    # variable-sized portion.
    try:
        first, second = []
    except ValueError as exc:
        print(f"Empty sequence error: {exc}")


# ---------------------------------------------------------------------------
# Validation-oriented unpacking
# ---------------------------------------------------------------------------

def validate_configuration(config: dict[str, Any]) -> dict[str, Any]:
    required = {"host", "port", "enabled"}
    missing = required - config.keys()

    if missing:
        raise ValueError(f"Missing configuration fields: {sorted(missing)}")

    host, port, enabled = (
        config["host"],
        config["port"],
        config["enabled"],
    )

    if not isinstance(host, str) or not host.strip():
        raise ValueError("host must be a non-empty string")

    if not isinstance(port, int) or isinstance(port, bool):
        raise TypeError("port must be an integer")

    if not 1 <= port <= 65535:
        raise ValueError("port must be between 1 and 65535")

    if not isinstance(enabled, bool):
        raise TypeError("enabled must be boolean")

    return {
        "host": host.strip(),
        "port": port,
        "enabled": enabled,
    }


def demonstrate_validation() -> None:
    heading("Validation before unpacking")

    valid = {
        "host": "api.internal",
        "port": 8443,
        "enabled": True,
    }

    show("validated configuration", validate_configuration(valid))

    invalid = {
        "host": "",
        "port": 70000,
        "enabled": "yes",
    }

    try:
        validate_configuration(invalid)
    except (ValueError, TypeError) as exc:
        print(f"Rejected configuration: {exc}")


# ---------------------------------------------------------------------------
# Practical ETL example
# ---------------------------------------------------------------------------

def process_sales_rows(rows: Iterable[tuple[str, str, float, str]]) -> dict[str, float]:
    totals: dict[str, float] = {}

    for row in rows:
        if len(row) != 4:
            raise ValueError(f"Expected four fields, received {len(row)}")

        transaction_id, region, amount, status = row

        if not transaction_id.strip():
            raise ValueError("transaction_id cannot be empty")

        if not region.strip():
            raise ValueError("region cannot be empty")

        if amount < 0:
            raise ValueError(f"Negative amount for {transaction_id}")

        if status == "completed":
            totals[region] = totals.get(region, 0.0) + amount
        elif status not in {"cancelled", "pending"}:
            raise ValueError(f"Unknown status: {status}")

    return totals


def demonstrate_etl() -> None:
    heading("Practical ETL workflow")

    rows = [
        ("TX001", "North", 12500.0, "completed"),
        ("TX002", "North", 3000.0, "pending"),
        ("TX003", "South", 8900.0, "completed"),
        ("TX004", "North", 1500.0, "cancelled"),
        ("TX005", "South", 2100.0, "completed"),
    ]

    totals = process_sales_rows(rows)
    show("completed sales by region", totals)

    try:
        process_sales_rows([
            ("TX999", "West", -10.0, "completed"),
        ])
    except ValueError as exc:
        print(f"Rejected ETL row: {exc}")


# ---------------------------------------------------------------------------
# Demonstrating assignment evaluation order
# ---------------------------------------------------------------------------

def demonstrate_assignment_semantics() -> None:
    heading("Assignment evaluation semantics")

    values = ["old-left", "old-right"]

    # The right-hand expression is evaluated before either target changes.
    values[0], values[1] = values[1], values[0]

    show("after simultaneous assignment", values)

    # This differs from sequential assignment, where the first assignment
    # changes the value observed by the second statement.
    left = "A"
    right = "B"

    left = right
    right = left

    show("sequential assignment", (left, right))


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

def main() -> None:
    demonstrate_basic_unpacking()
    demonstrate_starred_unpacking()
    demonstrate_nested_unpacking()
    demonstrate_swapping()
    demonstrate_function_unpacking()
    demonstrate_variadic_unpacking()
    demonstrate_iterable_unpacking()
    demonstrate_dictionary_unpacking()
    demonstrate_loop_unpacking()
    demonstrate_dataclass_unpacking()
    demonstrate_record_parsing()
    demonstrate_path_unpacking()
    demonstrate_api_unpacking()
    demonstrate_generator_behavior()
    demonstrate_performance_tradeoff()
    demonstrate_unknown_sizes()
    demonstrate_pattern_matching()
    demonstrate_api_design()
    demonstrate_common_mistakes()
    demonstrate_validation()
    demonstrate_etl()
    demonstrate_assignment_semantics()


if __name__ == "__main__":
    main()
