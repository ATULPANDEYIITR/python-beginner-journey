#!/usr/bin/env python3
"""
Working with JSON
-----------------
Demonstrates JSON serialization, deserialization, validation, nested data,
file handling, querying, transformation, error handling, and secure processing.

Python standard library only.
"""

import json
import math
import hashlib
import logging
import tempfile
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

MAX_FILE_SIZE = 2 * 1024 * 1024
MAX_JSON_DEPTH = 30


class JSONValidationError(ValueError):
    pass


class RecordStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


@dataclass
class Customer:
    customer_id: int
    name: str
    email: str
    status: RecordStatus
    balance: float


@dataclass
class Order:
    order_id: int
    customer_id: int
    amount: float
    items: list[str]
    created_at: str


def validate_json_depth(value: Any, depth: int = 0) -> None:
    """Prevent excessively nested JSON structures."""
    if depth > MAX_JSON_DEPTH:
        raise JSONValidationError("Maximum JSON nesting depth exceeded")

    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise JSONValidationError("JSON object keys must be strings")
            validate_json_depth(item, depth + 1)

    elif isinstance(value, list):
        for item in value:
            validate_json_depth(item, depth + 1)


def reject_nonstandard_constant(value: str):
    """Reject NaN and Infinity, which are not valid JSON numbers."""
    raise JSONValidationError(f"Invalid JSON numeric constant: {value}")


def reject_duplicate_keys(pairs):
    """Reject duplicate object keys instead of silently overwriting them."""
    result = {}

    for key, value in pairs:
        if key in result:
            raise JSONValidationError(f"Duplicate JSON key: {key}")
        result[key] = value

    return result


def serialize_json(data: Any, pretty: bool = True) -> str:
    validate_json_depth(data)

    return json.dumps(
        data,
        indent=4 if pretty else None,
        separators=None if pretty else (",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True
    )


def deserialize_json(content: str) -> Any:
    if not isinstance(content, str):
        raise TypeError("JSON input must be a string")

    data = json.loads(
        content,
        parse_constant=reject_nonstandard_constant,
        object_pairs_hook=reject_duplicate_keys
    )

    validate_json_depth(data)
    return data


def validate_customer(data: Any) -> Customer:
    if not isinstance(data, dict):
        raise JSONValidationError("Customer must be a JSON object")

    required = {
        "customer_id",
        "name",
        "email",
        "status",
        "balance"
    }

    missing = required - data.keys()

    if missing:
        raise JSONValidationError(
            f"Missing fields: {sorted(missing)}"
        )

    customer_id = data["customer_id"]

    if isinstance(customer_id, bool) or not isinstance(customer_id, int):
        raise JSONValidationError("customer_id must be an integer")

    if customer_id <= 0:
        raise JSONValidationError("customer_id must be positive")

    name = data["name"]
    email = data["email"]

    if not isinstance(name, str) or not name.strip():
        raise JSONValidationError("Customer name cannot be empty")

    if not isinstance(email, str) or "@" not in email:
        raise JSONValidationError("Invalid email address")

    try:
        status = RecordStatus(data["status"])
    except ValueError:
        raise JSONValidationError("Invalid customer status")

    balance = data["balance"]

    if isinstance(balance, bool) or not isinstance(balance, (int, float)):
        raise JSONValidationError("Balance must be numeric")

    if not math.isfinite(balance) or balance < 0:
        raise JSONValidationError("Balance must be finite and non-negative")

    return Customer(
        customer_id=customer_id,
        name=name.strip(),
        email=email.strip().lower(),
        status=status,
        balance=float(balance)
    )


def find_value(data: Any, path: str) -> Any:
    """
    Retrieve nested values using dot-separated paths.
    Example: customer.address.city
    """
    current = data

    for part in path.split("."):
        if isinstance(current, dict):
            if part not in current:
                raise KeyError(f"Missing JSON property: {part}")
            current = current[part]

        elif isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                raise KeyError(f"Invalid array index: {part}")

        else:
            raise KeyError(f"Cannot access {part} in this value")

    return current


def update_nested_value(data: dict, path: str, value: Any) -> None:
    """Update an existing nested property."""
    parts = path.split(".")
    current = data

    for part in parts[:-1]:
        if not isinstance(current, dict) or part not in current:
            raise KeyError(f"Invalid path: {path}")
        current = current[part]

    if not isinstance(current, dict) or parts[-1] not in current:
        raise KeyError(f"Property does not exist: {path}")

    validate_json_depth(value)
    current[parts[-1]] = value


def calculate_order_total(order: dict) -> float:
    items = order.get("items", [])

    if not isinstance(items, list):
        raise JSONValidationError("Order items must be an array")

    total = 0.0

    for item in items:
        if not isinstance(item, dict):
            raise JSONValidationError("Each item must be an object")

        price = item.get("price")
        quantity = item.get("quantity")

        if isinstance(price, bool) or not isinstance(price, (int, float)):
            raise JSONValidationError("Invalid item price")

        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise JSONValidationError("Invalid item quantity")

        if not math.isfinite(price) or price < 0:
            raise JSONValidationError("Price must be finite and non-negative")

        if quantity <= 0:
            raise JSONValidationError("Quantity must be positive")

        total += price * quantity

    return round(total, 2)


def remove_sensitive_fields(data: Any) -> Any:
    """Recursively remove sensitive fields before external sharing."""
    sensitive = {
        "password",
        "token",
        "secret",
        "access_token",
        "api_key"
    }

    if isinstance(data, dict):
        return {
            key: remove_sensitive_fields(value)
            for key, value in data.items()
            if key.lower() not in sensitive
        }

    if isinstance(data, list):
        return [remove_sensitive_fields(item) for item in data]

    return data


def write_json_file(path: Path, data: Any) -> None:
    content = serialize_json(data)

    if len(content.encode("utf-8")) > MAX_FILE_SIZE:
        raise JSONValidationError("JSON output exceeds file size limit")

    # Write to a temporary file and replace the destination atomically.
    temporary = path.with_suffix(path.suffix + ".tmp")

    try:
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(path)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def read_json_file(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(path)

    if path.stat().st_size > MAX_FILE_SIZE:
        raise JSONValidationError("JSON input exceeds file size limit")

    content = path.read_text(encoding="utf-8")
    return deserialize_json(content)


def generate_checksum(data: Any) -> str:
    canonical = serialize_json(data, pretty=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def demonstrate_json_workflow() -> None:
    print("\n=== JSON Serialization ===")

    customer = Customer(
        customer_id=101,
        name="Atul Pandey",
        email="atul@example.com",
        status=RecordStatus.ACTIVE,
        balance=12500.50
    )

    customer_json = serialize_json({
        **asdict(customer),
        "status": customer.status.value
    })

    print(customer_json)

    print("\n=== JSON Deserialization ===")

    customer_data = deserialize_json(customer_json)
    validated_customer = validate_customer(customer_data)

    print(validated_customer)

    print("\n=== Nested JSON ===")

    order = {
        "order_id": 5001,
        "customer": {
            "customer_id": 101,
            "address": {
                "city": "Lucknow",
                "country": "India"
            }
        },
        "items": [
            {"product": "Laptop", "price": 65000, "quantity": 1},
            {"product": "Mouse", "price": 800, "quantity": 2}
        ],
        "payment": {
            "method": "card",
            "status": "completed"
        }
    }

    print("City:", find_value(order, "customer.address.city"))
    print("Order total:", calculate_order_total(order))

    print("\n=== Nested JSON Update ===")

    update_nested_value(
        order,
        "payment.status",
        "verified"
    )

    print("Payment status:", find_value(order, "payment.status"))

    print("\n=== JSON Array Processing ===")

    orders = [
        {"order_id": 1, "amount": 1200, "status": "completed"},
        {"order_id": 2, "amount": 2500, "status": "pending"},
        {"order_id": 3, "amount": 800, "status": "completed"}
    ]

    completed_orders = [
        item for item in orders
        if item["status"] == "completed"
    ]

    total_revenue = sum(
        item["amount"] for item in completed_orders
    )

    print("Completed orders:", completed_orders)
    print("Revenue:", total_revenue)

    print("\n=== Sensitive Data Filtering ===")

    api_response = {
        "user": "atul",
        "access_token": "secret-token",
        "profile": {
            "email": "atul@example.com",
            "password": "hidden",
            "department": "Engineering"
        }
    }

    sanitized = remove_sensitive_fields(api_response)
    print(serialize_json(sanitized))

    print("\n=== JSON File Handling ===")

    with tempfile.TemporaryDirectory() as directory:
        file_path = Path(directory) / "orders.json"

        write_json_file(file_path, order)
        loaded_order = read_json_file(file_path)

        print("Loaded order:", loaded_order["order_id"])
        print("SHA-256:", generate_checksum(loaded_order))

    print("\n=== JSON Error Handling ===")

    invalid_inputs = [
        '{"name": "Atul",}',
        '{"amount": NaN}',
        '{"name": "A", "name": "B"}'
    ]

    for content in invalid_inputs:
        try:
            deserialize_json(content)
        except (json.JSONDecodeError, JSONValidationError) as error:
            print("Rejected:", error)

    print("\n=== Assertions ===")

    assert find_value(order, "customer.address.city") == "Lucknow"
    assert calculate_order_total(order) == 66600.0
    assert len(completed_orders) == 2
    assert "access_token" not in sanitized

    print("All JSON workflow checks passed.")


if __name__ == "__main__":
    demonstrate_json_workflow()
