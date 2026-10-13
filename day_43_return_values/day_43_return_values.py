"""
Return Values: From Fundamentals to Advanced Design

A self-contained exploration of return values through practical implementations:
- Explicit and implicit returns
- Multiple return values and structured results
- Early returns, guard clauses, and error signaling
- Optional values and result types
- Recursive returns and higher-order functions
- Generators versus ordinary return values
- Return-value validation, mutation, and aliasing
- Resource-safe operations, serialization, and testing
- Performance considerations and API design

Run with Python 3.10 or later:
    python return_values.py
"""

from __future__ import annotations

import json
import math
import statistics
import tempfile
import unittest
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Generic, Iterable, Iterator, TypeVar


T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")


class ReturnValueError(ValueError):
    """Raised when a returned value violates a domain contract."""


class OutcomeKind(Enum):
    SUCCESS = "success"
    FAILURE = "failure"


@dataclass(frozen=True)
class Result(Generic[T, E]):
    """
    Represents either a successful value or a failure.

    The invariant is that exactly one of value and error is present.
    None is not used as the failure indicator because None may itself
    be a legitimate successful result.
    """

    kind: OutcomeKind
    value: T | None = None
    error: E | None = None

    def __post_init__(self) -> None:
        if self.kind is OutcomeKind.SUCCESS and self.error is not None:
            raise ValueError("A successful result cannot contain an error.")
        if self.kind is OutcomeKind.FAILURE and self.value is not None:
            raise ValueError("A failed result cannot contain a value.")
        if self.kind is OutcomeKind.FAILURE and self.error is None:
            raise ValueError("A failed result must contain an error.")

    @classmethod
    def success(cls, value: T) -> Result[T, E]:
        return cls(kind=OutcomeKind.SUCCESS, value=value)

    @classmethod
    def failure(cls, error: E) -> Result[T, E]:
        return cls(kind=OutcomeKind.FAILURE, error=error)

    @property
    def is_success(self) -> bool:
        return self.kind is OutcomeKind.SUCCESS

    def unwrap(self) -> T:
        if not self.is_success:
            raise RuntimeError(f"Cannot unwrap failed result: {self.error}")
        return self.value  # type: ignore[return-value]

    def map(self, transform: Callable[[T], U]) -> Result[U, E]:
        """Transform a successful value without changing a failure."""
        if not self.is_success:
            return Result.failure(self.error)  # type: ignore[arg-type]
        return Result.success(transform(self.unwrap()))


@dataclass(frozen=True)
class PaymentReceipt:
    transaction_id: str
    amount: float
    currency: str
    status: str


def heading(title: str) -> None:
    print(f"\n{'=' * 68}\n{title}\n{'=' * 68}")


# Fundamental return behavior


def calculate_subtotal(prices: Iterable[float]) -> float:
    """Return a single numeric result after validating the input."""
    materialized = list(prices)
    if not materialized:
        return 0.0
    if any(not math.isfinite(price) or price < 0 for price in materialized):
        raise ValueError("Prices must be finite, non-negative numbers.")
    return round(sum(materialized), 2)


def find_customer(customers: dict[int, str], customer_id: int) -> str | None:
    """Return a matching name or None when no record exists."""
    return customers.get(customer_id)


def classify_order(total: float) -> str:
    """Demonstrate early returns for mutually exclusive conditions."""
    if not math.isfinite(total) or total < 0:
        raise ValueError("Order total must be finite and non-negative.")
    if total == 0:
        return "empty"
    if total < 100:
        return "standard"
    if total < 1000:
        return "priority"
    return "high_value"


def implicit_return_example(enabled: bool) -> None:
    """
    A function with no return statement returns None implicitly.
    The explicit return keeps control flow clear when disabled.
    """
    if not enabled:
        return
    print("The requested operation is enabled.")


def calculate_statistics(values: Iterable[float]) -> dict[str, float | int]:
    """Return a dictionary when named measurements are more useful."""
    numbers = list(values)
    if not numbers:
        raise ValueError("At least one measurement is required.")
    if any(not math.isfinite(value) for value in numbers):
        raise ValueError("Measurements must be finite.")
    return {
        "count": len(numbers),
        "minimum": min(numbers),
        "maximum": max(numbers),
        "mean": round(statistics.fmean(numbers), 3),
    }


def divide_with_status(
    numerator: float, denominator: float
) -> tuple[bool, float | str]:
    """
    Return two related values.

    A tuple is convenient for small results, but callers must understand
    which position represents status and which represents the payload.
    """
    if not math.isfinite(numerator) or not math.isfinite(denominator):
        return False, "Inputs must be finite."
    if denominator == 0:
        return False, "Division by zero is not permitted."
    return True, numerator / denominator


# Domain-specific return contracts


def normalize_email(email: str) -> Result[str, str]:
    """Return a normalized address or a specific validation failure."""
    candidate = email.strip().lower()
    if not candidate:
        return Result.failure("Email address is required.")
    if candidate.count("@") != 1:
        return Result.failure("Email address must contain one @ symbol.")
    local, domain = candidate.split("@")
    if not local or not domain or "." not in domain:
        return Result.failure("Email address has an invalid structure.")
    if any(character.isspace() for character in candidate):
        return Result.failure("Email address cannot contain whitespace.")
    return Result.success(candidate)


def create_payment(
    transaction_id: str,
    amount: float,
    currency: str,
    approved: bool,
) -> Result[PaymentReceipt, str]:
    """
    Simulate a payment service without moving real money.

    A return value communicates the outcome. A production payment service
    would also need durable idempotency, authorization, auditing, and
    integration with a trusted payment processor.
    """
    if not transaction_id.strip():
        return Result.failure("Transaction identifier is required.")
    if not math.isfinite(amount) or amount <= 0:
        return Result.failure("Payment amount must be positive and finite.")
    if currency not in {"USD", "EUR", "INR"}:
        return Result.failure("Unsupported currency.")
    if not approved:
        return Result.failure("Payment was declined.")

    receipt = PaymentReceipt(
        transaction_id=transaction_id,
        amount=round(amount, 2),
        currency=currency,
        status="accepted",
    )
    return Result.success(receipt)


def parse_integer(text: str) -> Result[int, str]:
    """Convert text while returning conversion failures as data."""
    candidate = text.strip()
    if not candidate:
        return Result.failure("An integer is required.")
    try:
        return Result.success(int(candidate))
    except ValueError:
        return Result.failure(f"Invalid integer: {candidate!r}")


def lookup_inventory(
    inventory: dict[str, int], sku: str
) -> Result[int, str]:
    """Distinguish a missing product from a product with zero stock."""
    normalized_sku = sku.strip().upper()
    if not normalized_sku:
        return Result.failure("SKU is required.")
    if normalized_sku not in inventory:
        return Result.failure(f"Unknown SKU: {normalized_sku}")
    return Result.success(inventory[normalized_sku])


def price_order(
    unit_price: float, quantity: int, discount_rate: float = 0.0
) -> Result[dict[str, float | int], str]:
    """Return a structured price breakdown after validating all inputs."""
    if not math.isfinite(unit_price) or unit_price < 0:
        return Result.failure("Unit price must be finite and non-negative.")
    if quantity <= 0:
        return Result.failure("Quantity must be positive.")
    if not math.isfinite(discount_rate) or not 0 <= discount_rate <= 1:
        return Result.failure("Discount rate must be between zero and one.")

    subtotal = unit_price * quantity
    discount = subtotal * discount_rate
    total = round(subtotal - discount, 2)

    return Result.success({
        "quantity": quantity,
        "subtotal": round(subtotal, 2),
        "discount": round(discount, 2),
        "total": total,
    })


# Recursive returns and higher-order return behavior


def factorial(number: int) -> int:
    """
    Return the result of a recursive computation.

    Each recursive branch must return its recursive result. Omitting that
    return would make the parent call receive None.
    """
    if isinstance(number, bool) or not isinstance(number, int):
        raise TypeError("Factorial requires an integer.")
    if number < 0:
        raise ValueError("Factorial is undefined for negative integers.")
    if number > 1000:
        raise ValueError("Input exceeds the demonstration limit.")
    if number in (0, 1):
        return 1
    return number * factorial(number - 1)


def make_threshold_checker(threshold: float) -> Callable[[float], bool]:
    """
    Return a function.

    The returned closure retains the threshold from its enclosing scope.
    """
    if not math.isfinite(threshold):
        raise ValueError("Threshold must be finite.")

    def check(value: float) -> bool:
        return math.isfinite(value) and value >= threshold

    return check


def transform_records(
    records: Iterable[dict[str, object]],
    transform: Callable[[dict[str, object]], dict[str, object]],
) -> list[dict[str, object]]:
    """Return a transformed collection rather than modifying the input."""
    return [transform(record) for record in records]


# Generators return iterators and produce values over time.


def batches(
    records: Iterable[T], batch_size: int
) -> Iterator[list[T]]:
    """
    Yield bounded groups rather than returning one large materialized list.

    This is useful when processing repository events or review records
    that may be too large to hold in memory at once.
    """
    if batch_size <= 0:
        raise ValueError("Batch size must be positive.")

    current: list[T] = []
    for record in records:
        current.append(record)
        if len(current) == batch_size:
            yield current
            current = []

    if current:
        yield current


# Return-value aliasing and mutation


def unsafe_append_event(
    event: dict[str, object], history: list[dict[str, object]]
) -> list[dict[str, object]]:
    """
    Return the same list object after mutation.

    Callers holding another reference to history observe this change.
    """
    history.append(event)
    return history


def safe_append_event(
    event: dict[str, object], history: list[dict[str, object]]
) -> list[dict[str, object]]:
    """Return a new list to avoid changing the caller's collection."""
    return [*history, event]


# File operations and serialization


def load_json(path: Path) -> Result[object, str]:
    """Return decoded JSON or a useful error instead of leaking exceptions."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return Result.success(json.load(file))
    except FileNotFoundError:
        return Result.failure(f"File does not exist: {path}")
    except json.JSONDecodeError as exc:
        return Result.failure(
            f"Invalid JSON at line {exc.lineno}, column {exc.colno}."
        )
    except OSError as exc:
        return Result.failure(f"Could not read file: {exc}")


def save_json_atomically(path: Path, value: object) -> Result[Path, str]:
    """
    Write JSON to a temporary file before replacing the destination.

    The temporary file is created in the destination directory so the
    final replacement can normally use the same filesystem.
    """
    temporary_path: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            json.dump(value, file, indent=2, ensure_ascii=False, allow_nan=False)
            file.write("\n")
            file.flush()

        temporary_path.replace(path)
        return Result.success(path)
    except (OSError, TypeError, ValueError) as exc:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        return Result.failure(f"Could not save JSON: {exc}")


# Executable tests for return-value contracts


class ReturnValueTests(unittest.TestCase):
    def test_empty_subtotal(self) -> None:
        self.assertEqual(calculate_subtotal([]), 0.0)

    def test_subtotal_rounding(self) -> None:
        self.assertEqual(calculate_subtotal([12.30, 4.20]), 16.5)

    def test_invalid_subtotal(self) -> None:
        with self.assertRaises(ValueError):
            calculate_subtotal([10.0, -1.0])

    def test_missing_customer_is_none(self) -> None:
        self.assertIsNone(find_customer({}, 17))

    def test_classification(self) -> None:
        self.assertEqual(classify_order(0), "empty")
        self.assertEqual(classify_order(250), "priority")

    def test_statistics(self) -> None:
        self.assertEqual(
            calculate_statistics([2, 4, 6])["mean"],
            4.0,
        )

    def test_division_failure(self) -> None:
        success, result = divide_with_status(5, 0)
        self.assertFalse(success)
        self.assertIsInstance(result, str)

    def test_result_map(self) -> None:
        result = Result.success(5).map(lambda value: value * 2)
        self.assertEqual(result.unwrap(), 10)

    def test_result_failure_propagates(self) -> None:
        result = Result.failure("invalid").map(lambda value: value * 2)
        self.assertFalse(result.is_success)
        self.assertEqual(result.error, "invalid")

    def test_email_normalization(self) -> None:
        self.assertEqual(
            normalize_email("  PERSON@example.com ").unwrap(),
            "person@example.com",
        )

    def test_payment_decline(self) -> None:
        result = create_payment("TX-100", 50, "INR", approved=False)
        self.assertFalse(result.is_success)

    def test_inventory_zero_is_not_missing(self) -> None:
        result = lookup_inventory({"SKU-1": 0}, "sku-1")
        self.assertTrue(result.is_success)
        self.assertEqual(result.unwrap(), 0)

    def test_price_order(self) -> None:
        result = price_order(100, 3, 0.1)
        self.assertEqual(result.unwrap()["total"], 270.0)

    def test_factorial(self) -> None:
        self.assertEqual(factorial(5), 120)

    def test_generator_batches(self) -> None:
        self.assertEqual(
            list(batches(range(5), 2)),
            [[0, 1], [2, 3], [4]],
        )

    def test_safe_append_does_not_mutate_original(self) -> None:
        original: list[dict[str, object]] = [{"id": 1}]
        updated = safe_append_event({"id": 2}, original)
        self.assertEqual(len(original), 1)
        self.assertEqual(len(updated), 2)

    def test_json_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            payload = {"transaction_id": "TX-101", "amount": 125.50}
            saved = save_json_atomically(path, payload)
            self.assertTrue(saved.is_success)
            loaded = load_json(path)
            self.assertEqual(loaded.unwrap(), payload)


def demonstrate() -> None:
    heading("Single Values, Early Returns, and Optional Results")
    print("Subtotal:", calculate_subtotal([19.99, 8.50, 2.00]))
    print("Missing customer:", find_customer({10: "Asha"}, 99))
    print("Order classification:", classify_order(245.00))
    implicit_return_example(False)

    heading("Structured Return Values")
    print("Statistics:", calculate_statistics([12.5, 18.0, 20.5]))
    success, division = divide_with_status(144, 12)
    print("Division:", {"success": success, "result": division})

    heading("Explicit Success and Failure")
    print("Valid email:", normalize_email("  USER@Example.com "))
    print("Invalid email:", normalize_email("not-an-email"))
    print("Parsed integer:", parse_integer(" 2048 "))
    print("Invalid integer:", parse_integer("twenty"))

    inventory = {"LAPTOP-14": 12, "MONITOR-27": 0}
    print("Inventory:", lookup_inventory(inventory, "monitor-27"))
    print("Unknown SKU:", lookup_inventory(inventory, "keyboard"))

    heading("Payment and Order Contracts")
    payment = create_payment("TX-2026-0042", 1299.95, "INR", True)
    if payment.is_success:
        print("Receipt:", asdict(payment.unwrap()))
    else:
        print("Payment failure:", payment.error)

    print("Order:", price_order(749.50, 3, 0.05))
    print("Declined payment:", create_payment("TX-0043", 100, "INR", False))

    heading("Recursive and Higher-Order Return Values")
    print("Factorial:", factorial(8))
    expensive_order = make_threshold_checker(1000)
    print("Order exceeds threshold:", expensive_order(1250))
    records = [{"id": 1, "amount": 100}, {"id": 2, "amount": 200}]
    enriched = transform_records(
        records,
        lambda record: {**record, "review_required": record["amount"] >= 150},
    )
    print("Enriched records:", enriched)

    heading("Lazy Iteration and Object Identity")
    for group in batches(["PR-101", "PR-102", "PR-103", "PR-104", "PR-105"], 2):
        print("Batch:", group)

    history: list[dict[str, object]] = [{"event": "opened"}]
    same_history = unsafe_append_event({"event": "reviewed"}, history)
    print("Unsafe operation shares identity:", same_history is history)

    independent_history = safe_append_event({"event": "merged"}, history)
    print("Original history length:", len(history))
    print("Independent history length:", len(independent_history))

    heading("JSON Persistence and Error Reporting")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "receipt.json"
        payload = {
            "transaction_id": "TX-2026-0042",
            "amount": 1299.95,
            "currency": "INR",
        }
        print("Save result:", save_json_atomically(path, payload))
        print("Load result:", load_json(path))
        print("Missing file result:", load_json(Path(directory) / "missing.json"))

    heading("Automated Contract Tests")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReturnValueTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    demonstrate()
