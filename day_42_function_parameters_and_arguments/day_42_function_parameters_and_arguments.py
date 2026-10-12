#!/usr/bin/env python3
"""Executable study of function parameters and arguments.

Run with: python function_parameters.py
Requires Python 3.10 or later. Uses only the standard library.
"""

from __future__ import annotations

import inspect
import json
import math
import statistics
import tempfile
import unittest
from dataclasses import dataclass
from functools import partial, wraps
from pathlib import Path
from typing import Callable, Iterable, TypeVar


T = TypeVar("T")


def heading(title: str) -> None:
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


# Parameters belong to a function definition. Arguments are values supplied
# when the function is called.
def calculate_total(price: float, quantity: int) -> float:
    return price * quantity


# Default values allow callers to omit selected arguments.
def calculate_invoice(
    price: float,
    quantity: int = 1,
    tax_rate: float = 0.0,
    discount: float = 0.0,
) -> float:
    if price < 0 or quantity < 0:
        raise ValueError("Price and quantity cannot be negative.")
    if not 0 <= tax_rate <= 1:
        raise ValueError("Tax rate must be between 0 and 1.")
    if not 0 <= discount <= 1:
        raise ValueError("Discount must be between 0 and 1.")

    subtotal = price * quantity * (1 - discount)
    return round(subtotal * (1 + tax_rate), 2)


# Positional arguments are matched by position; keyword arguments by name.
def describe_order(product: str, quantity: int, priority: bool = False) -> str:
    priority_label = "priority" if priority else "standard"
    return f"{quantity} x {product} ({priority_label})"


# *args collects extra positional arguments into a tuple.
def sum_values(*values: float) -> float:
    return sum(values)


# **kwargs collects extra keyword arguments into a dictionary.
def build_profile(name: str, **attributes: object) -> dict[str, object]:
    return {"name": name, **attributes}


# Parameters before / are positional-only. Parameters after * are
# keyword-only. This makes a public API's calling conventions explicit.
def convert_temperature(value: float, /, *, unit: str = "C") -> float:
    if unit == "C":
        return value
    if unit == "F":
        return value * 9 / 5 + 32
    if unit == "K":
        return value + 273.15
    raise ValueError(f"Unsupported temperature unit: {unit}")


# Mutable defaults persist across calls. A None sentinel prevents accidental
# sharing of a list between unrelated function calls.
def append_event(
    event: str,
    events: list[str] | None = None,
) -> list[str]:
    if events is None:
        events = []
    events.append(event)
    return events


# Python passes object references by assignment. Rebinding a local parameter
# does not replace the caller's variable, but mutating a shared object is
# visible to the caller.
def replace_local(items: list[str]) -> None:
    items = ["local replacement"]
    items.append("local only")


def mutate_shared(items: list[str]) -> None:
    items.append("added through shared reference")


def inspect_parameters(function: Callable[..., object]) -> None:
    signature = inspect.signature(function)
    print(f"{function.__name__}{signature}")
    for name, parameter in signature.parameters.items():
        default = (
            "<required>"
            if parameter.default is inspect.Parameter.empty
            else repr(parameter.default)
        )
        print(
            f"  {name}: kind={parameter.kind.description}, "
            f"default={default}"
        )


def apply_discount(
    amount: float,
    *,
    percentage: float,
    currency: str = "INR",
) -> str:
    if amount < 0 or not 0 <= percentage <= 100:
        raise ValueError("Invalid amount or discount percentage.")
    final_amount = amount * (1 - percentage / 100)
    return f"{currency} {final_amount:.2f}"


# A decorator forwards both positional and keyword arguments. functools.wraps
# preserves metadata and exposes the original signature to inspection tools.
def traced(function: Callable[..., T]) -> Callable[..., T]:
    @wraps(function)
    def wrapper(*args: object, **kwargs: object) -> T:
        print(
            f"Calling {function.__name__}: "
            f"positional={args}, keyword={kwargs}"
        )
        result = function(*args, **kwargs)
        print(f"Result: {result!r}")
        return result

    return wrapper


@traced
def calculate_shipping(weight_kg: float, *, express: bool = False) -> float:
    if weight_kg < 0:
        raise ValueError("Weight cannot be negative.")
    base = 50.0 + 12.0 * weight_kg
    return round(base * (1.8 if express else 1.0), 2)


# Higher-order functions accept functions as arguments.
def transform_all(
    values: Iterable[T],
    transform: Callable[[T], object],
) -> list[object]:
    return [transform(value) for value in values]


def validate_arguments(
    function: Callable[..., T],
    *args: object,
    **kwargs: object,
) -> T:
    """Bind arguments to a callable's signature before invoking it."""
    signature = inspect.signature(function)
    bound = signature.bind(*args, **kwargs)
    bound.apply_defaults()
    return function(*bound.args, **bound.kwargs)


@dataclass(frozen=True)
class Measurement:
    name: str
    value: float
    unit: str = "units"

    def as_record(self, *, precision: int = 2) -> dict[str, object]:
        if precision < 0 or precision > 10:
            raise ValueError("Precision must be between 0 and 10.")
        return {
            "name": self.name,
            "value": round(self.value, precision),
            "unit": self.unit,
        }


def summarize_measurements(
    *measurements: Measurement,
    include_values: bool = True,
) -> dict[str, object]:
    """Combine variadic positional objects and a keyword-only option."""
    if not measurements:
        raise ValueError("At least one measurement is required.")

    values = [measurement.value for measurement in measurements]
    result: dict[str, object] = {
        "count": len(values),
        "mean": statistics.fmean(values),
        "minimum": min(values),
        "maximum": max(values),
    }
    if include_values:
        result["measurements"] = [
            measurement.as_record() for measurement in measurements
        ]
    return result


# partial binds some arguments now and leaves the remaining arguments for
# a later call. It is useful for reusable configuration-specific functions.
calculate_indian_tax = partial(calculate_invoice, tax_rate=0.18)


def load_json(path: Path, *, max_bytes: int = 1_000_000) -> object:
    """Read bounded JSON input while handling expected filesystem failures."""
    if max_bytes <= 0:
        raise ValueError("max_bytes must be positive.")

    try:
        if path.stat().st_size > max_bytes:
            raise ValueError("JSON file exceeds the configured size limit.")
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON at line {exc.lineno}") from exc


class ParameterTests(unittest.TestCase):
    def test_default_arguments(self) -> None:
        self.assertEqual(calculate_invoice(100), 100.0)
        self.assertEqual(calculate_invoice(100, 2, 0.1), 220.0)

    def test_keyword_arguments(self) -> None:
        self.assertEqual(
            describe_order(product="Notebook", quantity=3, priority=True),
            "3 x Notebook (priority)",
        )

    def test_positional_only_parameter(self) -> None:
        self.assertAlmostEqual(convert_temperature(0, unit="F"), 32.0)
        with self.assertRaises(TypeError):
            convert_temperature(value=0)  # type: ignore[call-arg]

    def test_mutable_default_protection(self) -> None:
        first = append_event("created")
        second = append_event("updated")
        self.assertEqual(first, ["created"])
        self.assertEqual(second, ["updated"])

    def test_mutation_and_rebinding(self) -> None:
        items = ["original"]
        replace_local(items)
        self.assertEqual(items, ["original"])
        mutate_shared(items)
        self.assertEqual(items, ["original", "added through shared reference"])

    def test_argument_binding(self) -> None:
        self.assertEqual(
            validate_arguments(calculate_total, 4, quantity=3),
            12,
        )
        with self.assertRaises(TypeError):
            validate_arguments(calculate_total, 4, 3, 8)

    def test_invoice_validation(self) -> None:
        with self.assertRaises(ValueError):
            calculate_invoice(-1)
        with self.assertRaises(ValueError):
            calculate_invoice(100, tax_rate=2)

    def test_shipping(self) -> None:
        self.assertEqual(calculate_shipping.__name__, "calculate_shipping")
        self.assertEqual(calculate_shipping(2), 74.0)
        with self.assertRaises(ValueError):
            calculate_shipping(-1)

    def test_measurements(self) -> None:
        result = summarize_measurements(
            Measurement("latency", 20, "ms"),
            Measurement("throughput", 30, "req/s"),
            include_values=False,
        )
        self.assertEqual(result["count"], 2)
        self.assertNotIn("measurements", result)
        with self.assertRaises(ValueError):
            summarize_measurements()

    def test_partial_function(self) -> None:
        self.assertEqual(calculate_indian_tax(100, quantity=1), 118.0)

    def test_json_file_handling(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.json"
            path.write_text('{"status": "approved"}', encoding="utf-8")
            self.assertEqual(load_json(path), {"status": "approved"})
            path.write_text("{broken", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_json(path)
            with self.assertRaises(ValueError):
                load_json(path, max_bytes=1)


def main() -> None:
    heading("Basic parameter and argument binding")
    print("Positional call:", calculate_total(120.0, 3))
    print("Keyword call:", calculate_total(price=120.0, quantity=3))
    print("Mixed call:", calculate_total(120.0, quantity=3))
    print("Default invoice:", calculate_invoice(250.0))
    print("Discounted invoice:", calculate_invoice(
        250.0, quantity=2, tax_rate=0.18, discount=0.1
    ))

    heading("Variadic arguments and keyword-only configuration")
    print("Sum:", sum_values(4, 8, 12, 16))
    print("Profile:", build_profile(
        "Mira", department="Engineering", active=True
    ))
    print("Temperature:", convert_temperature(25, unit="F"))
    print("Discount:", apply_discount(500, percentage=12, currency="INR"))

    heading("Object references and safe defaults")
    first = append_event("pull-request-opened")
    second = append_event("review-requested")
    print("Independent event lists:", first, second)
    shared = ["draft"]
    replace_local(shared)
    print("After local rebinding:", shared)
    mutate_shared(shared)
    print("After shared mutation:", shared)

    heading("Signature inspection and binding")
    inspect_parameters(calculate_invoice)
    print("Bound invocation:", validate_arguments(
        calculate_total, 150, quantity=4
    ))

    heading("Decorators and higher-order functions")
    print("Standard shipping:", calculate_shipping(3))
    print("Express shipping:", calculate_shipping(3, express=True))
    print(
        "Transformed values:",
        transform_all([1, 2, 3, 4], lambda value: value * value),
    )

    heading("Domain objects and partial application")
    measurements = (
        Measurement("API latency", 42.7, "ms"),
        Measurement("Database latency", 18.2, "ms"),
        Measurement("Queue latency", 25.1, "ms"),
    )
    print("Statistics:", summarize_measurements(*measurements))
    print("Statistics without details:", summarize_measurements(
        *measurements, include_values=False
    ))
    print("Configured invoice:", calculate_indian_tax(1250, quantity=2))

    heading("Bounded file handling")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "metrics.json"
        path.write_text(
            '{"service":"payments","latency_ms":37}',
            encoding="utf-8",
        )
        print("Loaded metrics:", load_json(path))
        try:
            load_json(Path(directory) / "missing.json")
        except FileNotFoundError as error:
            print("Expected file failure:", error)

    heading("Executable verification")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ParameterTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
