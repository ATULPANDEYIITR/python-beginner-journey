"""
Introduction to Functions
A self-contained progression from basic function calls to reusable,
validated, composable, and testable software functions.

Run with Python 3.10 or later:
    python introduction_to_functions.py
"""

from __future__ import annotations

import json
import math
import tempfile
import unittest
from collections import Counter
from dataclasses import asdict, dataclass
from functools import lru_cache, wraps
from pathlib import Path
from time import perf_counter
from typing import Callable, Iterable, TypeVar


def heading(title: str) -> None:
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


# A function packages a named operation behind a reusable interface.
def greet(name: str) -> str:
    return f"Hello, {name}!"


# Parameters receive input values; return sends a result back to the caller.
def calculate_rectangle_area(length: float, width: float) -> float:
    if length < 0 or width < 0:
        raise ValueError("Rectangle dimensions cannot be negative.")
    return length * width


# Default parameters are used only when the caller omits an argument.
def calculate_price(
    unit_price: float,
    quantity: int,
    discount_rate: float = 0.0,
) -> float:
    if not math.isfinite(unit_price) or unit_price < 0:
        raise ValueError("Unit price must be finite and non-negative.")
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise TypeError("Quantity must be an integer.")
    if quantity < 0:
        raise ValueError("Quantity cannot be negative.")
    if not math.isfinite(discount_rate) or not 0 <= discount_rate <= 1:
        raise ValueError("Discount rate must be between 0 and 1.")
    return round(unit_price * quantity * (1 - discount_rate), 2)


# *args collects extra positional arguments into a tuple.
def calculate_total(*amounts: float) -> float:
    if any(not math.isfinite(amount) or amount < 0 for amount in amounts):
        raise ValueError("Amounts must be finite and non-negative.")
    return round(sum(amounts), 2)


# **kwargs collects extra keyword arguments into a dictionary.
def build_profile(name: str, **attributes: object) -> dict[str, object]:
    if not name.strip():
        raise ValueError("Name cannot be empty.")
    return {"name": name.strip(), **attributes}


def summarize_scores(scores: Iterable[float]) -> dict[str, float]:
    values = list(scores)
    if not values:
        raise ValueError("At least one score is required.")
    if any(not math.isfinite(value) for value in values):
        raise ValueError("Scores must be finite.")
    return {
        "minimum": min(values),
        "maximum": max(values),
        "average": sum(values) / len(values),
    }


# Functions return tuples when callers need several related results.
def divide_with_remainder(dividend: int, divisor: int) -> tuple[int, int]:
    if divisor == 0:
        raise ZeroDivisionError("Divisor cannot be zero.")
    return divmod(dividend, divisor)


# Keyword-only parameters make important options explicit at call sites.
def format_currency(amount: float, *, currency: str = "INR") -> str:
    if not math.isfinite(amount):
        raise ValueError("Amount must be finite.")
    if not currency or not currency.isalpha() or len(currency) != 3:
        raise ValueError("Currency must be a three-letter code.")
    return f"{currency.upper()} {amount:,.2f}"


# A function without an explicit return statement returns None.
def print_receipt(total: float) -> None:
    print(f"Receipt total: {format_currency(total)}")


# Recursive functions solve a problem by calling themselves on a smaller input.
def factorial_recursive(number: int) -> int:
    if isinstance(number, bool) or not isinstance(number, int):
        raise TypeError("Factorial requires an integer.")
    if number < 0:
        raise ValueError("Factorial is undefined for negative integers.")
    if number > 900:
        raise ValueError("Input is too large for this recursive demonstration.")
    if number <= 1:
        return 1
    return number * factorial_recursive(number - 1)


# Iteration avoids the recursion-depth limitation for large inputs.
def factorial_iterative(number: int) -> int:
    if isinstance(number, bool) or not isinstance(number, int):
        raise TypeError("Factorial requires an integer.")
    if number < 0:
        raise ValueError("Factorial is undefined for negative integers.")
    result = 1
    for factor in range(2, number + 1):
        result *= factor
    return result


# Memoization stores previous results for repeated calls.
@lru_cache(maxsize=None)
def fibonacci(number: int) -> int:
    if isinstance(number, bool) or not isinstance(number, int):
        raise TypeError("Index must be an integer.")
    if number < 0:
        raise ValueError("Index cannot be negative.")
    if number > 2000:
        raise ValueError("Index exceeds the demonstration limit.")
    if number < 2:
        return number
    return fibonacci(number - 1) + fibonacci(number - 2)


# A function can accept another function as an argument.
T = TypeVar("T")
R = TypeVar("R")


def transform_all(
    values: Iterable[T],
    operation: Callable[[T], R],
) -> list[R]:
    return [operation(value) for value in values]


# A closure retains access to a variable from its enclosing scope.
def make_multiplier(factor: float) -> Callable[[float], float]:
    def multiply(value: float) -> float:
        return value * factor
    return multiply


# A decorator wraps a function while preserving its metadata.
def measured(function: Callable[..., R]) -> Callable[..., R]:
    @wraps(function)
    def wrapper(*args: object, **kwargs: object) -> R:
        started = perf_counter()
        try:
            return function(*args, **kwargs)
        finally:
            elapsed = perf_counter() - started
            print(f"{function.__name__} executed in {elapsed:.6f} seconds")
    return wrapper


@measured
def sum_squares(limit: int) -> int:
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise TypeError("Limit must be an integer.")
    if limit < 0:
        raise ValueError("Limit cannot be negative.")
    return sum(number * number for number in range(limit + 1))


# Dataclasses make domain records explicit without repeating boilerplate.
@dataclass(frozen=True)
class OrderLine:
    product: str
    unit_price: float
    quantity: int


def validate_order_line(line: OrderLine) -> None:
    if not line.product.strip():
        raise ValueError("Product name cannot be empty.")
    if not math.isfinite(line.unit_price) or line.unit_price < 0:
        raise ValueError("Unit price must be finite and non-negative.")
    if isinstance(line.quantity, bool) or not isinstance(line.quantity, int):
        raise TypeError("Quantity must be an integer.")
    if line.quantity <= 0:
        raise ValueError("Order quantity must be positive.")


def line_subtotal(line: OrderLine) -> float:
    validate_order_line(line)
    return round(line.unit_price * line.quantity, 2)


def calculate_tax(subtotal: float, tax_rate: float) -> float:
    if not math.isfinite(subtotal) or subtotal < 0:
        raise ValueError("Subtotal must be finite and non-negative.")
    if not math.isfinite(tax_rate) or not 0 <= tax_rate <= 1:
        raise ValueError("Tax rate must be between 0 and 1.")
    return round(subtotal * tax_rate, 2)


def create_invoice(
    lines: Iterable[OrderLine],
    *,
    discount_rate: float = 0.0,
    tax_rate: float = 0.18,
) -> dict[str, object]:
    order_lines = list(lines)
    if not order_lines:
        raise ValueError("An invoice must contain at least one order line.")
    if not math.isfinite(discount_rate) or not 0 <= discount_rate <= 1:
        raise ValueError("Invalid discount rate.")

    subtotals = [line_subtotal(line) for line in order_lines]
    subtotal = round(sum(subtotals), 2)
    discount = round(subtotal * discount_rate, 2)
    taxable_amount = round(subtotal - discount, 2)
    tax = calculate_tax(taxable_amount, tax_rate)
    total = round(taxable_amount + tax, 2)

    return {
        "lines": [
            {
                **asdict(line),
                "subtotal": line_subtotal(line),
            }
            for line in order_lines
        ],
        "subtotal": subtotal,
        "discount": discount,
        "taxable_amount": taxable_amount,
        "tax": tax,
        "total": total,
    }


# File handling is separated from invoice calculation so each function
# has one responsibility and can be tested independently.
def save_invoice(invoice: dict[str, object], path: Path) -> None:
    path.write_text(
        json.dumps(invoice, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def load_invoice(path: Path) -> dict[str, object]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or "total" not in loaded:
        raise ValueError("Invoice file has an invalid structure.")
    total = loaded["total"]
    if isinstance(total, bool) or not isinstance(total, (int, float)):
        raise ValueError("Invoice total must be numeric.")
    if not math.isfinite(total) or total < 0:
        raise ValueError("Invoice total must be finite and non-negative.")
    return loaded


def group_words(text: str) -> dict[str, int]:
    # Normalize case and count words instead of repeatedly scanning the text.
    words = text.lower().split()
    return dict(Counter(words))


def compose(
    first: Callable[[T], R],
    second: Callable[[R], object],
) -> Callable[[T], object]:
    # Function composition applies the first transformation before the second.
    def composed(value: T) -> object:
        return second(first(value))
    return composed


class FunctionTests(unittest.TestCase):
    def test_rectangle_area(self) -> None:
        self.assertEqual(calculate_rectangle_area(5, 4), 20)

    def test_negative_dimension(self) -> None:
        with self.assertRaises(ValueError):
            calculate_rectangle_area(-1, 4)

    def test_default_discount(self) -> None:
        self.assertEqual(calculate_price(100, 2), 200)

    def test_discount(self) -> None:
        self.assertEqual(calculate_price(100, 2, 0.1), 180)

    def test_invalid_discount(self) -> None:
        with self.assertRaises(ValueError):
            calculate_price(100, 2, 1.5)

    def test_keyword_only_currency(self) -> None:
        self.assertEqual(format_currency(1250, currency="INR"), "INR 1,250.00")

    def test_division_by_zero(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            divide_with_remainder(10, 0)

    def test_factorial(self) -> None:
        self.assertEqual(factorial_iterative(5), 120)
        self.assertEqual(factorial_recursive(0), 1)

    def test_fibonacci(self) -> None:
        self.assertEqual([fibonacci(i) for i in range(8)], [0, 1, 1, 2, 3, 5, 8, 13])

    def test_transform(self) -> None:
        self.assertEqual(transform_all([1, 2, 3], lambda value: value * 2), [2, 4, 6])

    def test_invoice(self) -> None:
        invoice = create_invoice(
            [OrderLine("Keyboard", 1000, 2)],
            discount_rate=0.1,
            tax_rate=0.18,
        )
        self.assertEqual(invoice["subtotal"], 2000)
        self.assertEqual(invoice["discount"], 200)
        self.assertEqual(invoice["tax"], 324)
        self.assertEqual(invoice["total"], 2124)


def main() -> None:
    heading("Basic calls, parameters, and return values")
    print(greet("Atul"))
    print("Rectangle area:", calculate_rectangle_area(12, 8))
    print("Discounted order:", calculate_price(1250, 3, discount_rate=0.15))
    print("Combined total:", calculate_total(120.5, 80, 19.5))
    print("Profile:", build_profile("Atul", role="developer", active=True))
    print("Score statistics:", summarize_scores([72, 85, 91, 68, 94]))
    print("Division:", divide_with_remainder(17, 5))
    print("Currency:", format_currency(123456.78))
    print_receipt(1250)

    heading("Recursion, iteration, and caching")
    print("Recursive factorial of 6:", factorial_recursive(6))
    print("Iterative factorial of 20:", factorial_iterative(20))
    print("Fibonacci values:", [fibonacci(i) for i in range(12)])
    print("Fibonacci cache:", fibonacci.cache_info())

    heading("Higher-order functions and closures")
    print("Squared values:", transform_all([1, 2, 3, 4], lambda x: x * x))
    triple = make_multiplier(3)
    print("Triple 14:", triple(14))
    print("Word counts:", group_words("Functions simplify code functions improve reuse"))

    heading("Composed transformations")
    clean_name = lambda value: value.strip().title()
    add_label = lambda value: f"Customer: {value}"
    format_customer = compose(clean_name, add_label)
    print(format_customer("  atul pandey  "))

    heading("A practical invoice workflow")
    invoice = create_invoice(
        [
            OrderLine("Mechanical keyboard", 2499.00, 2),
            OrderLine("USB-C hub", 1799.00, 1),
            OrderLine("Laptop stand", 1299.00, 1),
        ],
        discount_rate=0.05,
        tax_rate=0.18,
    )
    print(json.dumps(invoice, indent=2))
    print("Invoice total:", format_currency(float(invoice["total"])))

    heading("File serialization and validation")
    with tempfile.TemporaryDirectory() as directory:
        invoice_path = Path(directory) / "invoice.json"
        save_invoice(invoice, invoice_path)
        restored = load_invoice(invoice_path)
        print("Saved and restored total:", restored["total"])

    heading("Measured execution")
    print("Sum of squares:", sum_squares(100_000))

    heading("Automated function tests")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FunctionTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)

    heading("Expected failures and edge cases")
    invalid_calls = [
        ("negative rectangle", lambda: calculate_rectangle_area(-2, 4)),
        ("zero divisor", lambda: divide_with_remainder(9, 0)),
        ("negative factorial", lambda: factorial_iterative(-1)),
        ("empty scores", lambda: summarize_scores([])),
        ("invalid currency", lambda: format_currency(10, currency="US")),
    ]
    for description, operation in invalid_calls:
        try:
            operation()
        except (TypeError, ValueError, ZeroDivisionError) as error:
            print(f"{description}: {type(error).__name__}: {error}")


if __name__ == "__main__":
    main()
