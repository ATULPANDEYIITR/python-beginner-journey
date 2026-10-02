"""
Nested Lists and Dictionaries
A self-contained progression from beginner structures to advanced hierarchical
data processing, validation, searching, transformation, aggregation, and
serialization.

Run:
    python nested_lists_dictionaries.py
"""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterator


def print_title(title: str) -> None:
    print(f"\n{'=' * 72}")
    print(title)
    print("=" * 72)


def beginner_nested_lists() -> None:
    print_title("Nested Lists: grids, rows, and records")

    matrix = [
        [10, 20, 30],
        [40, 50, 60],
        [70, 80, 90],
    ]

    print("Matrix:", matrix)
    print("Row 2:", matrix[1])
    print("Value at row 2, column 3:", matrix[1][2])

    total = sum(value for row in matrix for value in row)
    print("Total:", total)

    flattened = [value for row in matrix for value in row]
    print("Flattened:", flattened)

    matrix[0][1] = 25
    print("After updating matrix[0][1]:", matrix)

    # A shallow outer copy does not copy the inner lists.
    shallow_copy = matrix.copy()
    shallow_copy[0][0] = 999
    print("Original after shallow-copy mutation:", matrix)

    # deepcopy creates independent nested containers.
    independent_matrix = deepcopy(matrix)
    independent_matrix[0][0] = 111
    print("Original after deep-copy mutation:", matrix)
    print("Independent copy:", independent_matrix)


def nested_dictionaries() -> None:
    print_title("Nested Dictionaries: structured records")

    employee = {
        "id": "EMP-104",
        "name": "Anika Rao",
        "department": {
            "name": "Engineering",
            "location": "Bengaluru",
        },
        "contact": {
            "email": "anika@example.com",
            "phone": "+91-9000000000",
        },
        "skills": {
            "python": {"level": "advanced", "years": 5},
            "sql": {"level": "advanced", "years": 4},
        },
    }

    print("Employee:", json.dumps(employee, indent=2))
    print("Department:", employee["department"]["name"])
    print("Python experience:", employee["skills"]["python"]["years"])

    employee["skills"]["python"]["years"] += 1
    employee["contact"]["verified"] = True

    print("Updated Python experience:", employee["skills"]["python"]["years"])
    print("Contact verified:", employee["contact"]["verified"])


def mixed_nested_structure() -> None:
    print_title("Lists containing dictionaries containing lists")

    projects = [
        {
            "name": "Atlas",
            "status": "active",
            "team": ["Anika", "Ravi", "Meera"],
            "metrics": {
                "issues": [4, 2, 7],
                "deployments": {"successful": 12, "failed": 1},
            },
        },
        {
            "name": "Nova",
            "status": "completed",
            "team": ["Ravi", "Kabir"],
            "metrics": {
                "issues": [1, 3],
                "deployments": {"successful": 18, "failed": 2},
            },
        },
    ]

    for project in projects:
        issues = project["metrics"]["issues"]
        deployments = project["metrics"]["deployments"]
        total_deployments = deployments["successful"] + deployments["failed"]
        success_rate = deployments["successful"] / total_deployments * 100

        print(
            f"{project['name']}: "
            f"{len(project['team'])} team members, "
            f"{sum(issues)} issues, "
            f"{success_rate:.1f}% deployment success"
        )


def safe_nested_access(data: dict[str, Any], path: list[str]) -> Any:
    """
    Walk through a dictionary using a sequence of keys.

    This function intentionally raises KeyError or TypeError when the supplied
    path does not match the actual structure, making malformed data visible
    instead of silently returning an incorrect value.
    """
    current: Any = data

    for key in path:
        if not isinstance(current, dict):
            raise TypeError(
                f"Cannot access key {key!r}; "
                f"current value is {type(current).__name__}"
            )
        current = current[key]

    return current


def get_nested_value(
    data: dict[str, Any],
    path: list[str],
    default: Any = None,
) -> Any:
    """Safely retrieve a nested value without masking unrelated exceptions."""
    current: Any = data

    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]

    return current


def demonstrate_nested_access() -> None:
    print_title("Nested access, validation, and failure handling")

    configuration = {
        "application": {
            "database": {
                "host": "localhost",
                "port": 5432,
                "pool": {"minimum": 2, "maximum": 10},
            }
        }
    }

    print(
        "Database host:",
        safe_nested_access(
            configuration,
            ["application", "database", "host"],
        ),
    )

    print(
        "Missing timeout:",
        get_nested_value(
            configuration,
            ["application", "database", "timeout"],
            30,
        ),
    )

    try:
        safe_nested_access(configuration, ["application", "cache", "host"])
    except KeyError as exc:
        print("Expected missing-key error:", exc)


def transform_nested_data() -> None:
    print_title("Transforming nested structures")

    orders = [
        {
            "id": "ORD-1001",
            "customer": {"name": "Priya", "city": "Delhi"},
            "items": [
                {"sku": "KB-01", "name": "Keyboard", "quantity": 2, "price": 2500},
                {"sku": "MS-02", "name": "Mouse", "quantity": 1, "price": 1200},
            ],
        },
        {
            "id": "ORD-1002",
            "customer": {"name": "Rahul", "city": "Mumbai"},
            "items": [
                {"sku": "MN-03", "name": "Monitor", "quantity": 1, "price": 15000},
                {"sku": "HD-04", "name": "Drive", "quantity": 2, "price": 4500},
            ],
        },
    ]

    order_totals: dict[str, float] = {}

    for order in orders:
        total = sum(
            item["quantity"] * item["price"]
            for item in order["items"]
        )
        order_totals[order["id"]] = total

    print("Order totals:", order_totals)

    city_totals: dict[str, float] = defaultdict(float)
    for order in orders:
        city = order["customer"]["city"]
        city_totals[city] += order_totals[order["id"]]

    print("Totals by city:", dict(city_totals))


def recursive_walk(value: Any, path: tuple[Any, ...] = ()) -> Iterator[tuple[tuple[Any, ...], Any]]:
    """
    Recursively visit every leaf value in an arbitrarily nested combination
    of dictionaries and lists.

    Dictionary keys and list indexes are preserved in the generated path.
    """
    if isinstance(value, dict):
        for key, child in value.items():
            yield from recursive_walk(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from recursive_walk(child, path + (index,))
    else:
        yield path, value


def demonstrate_recursive_traversal() -> None:
    print_title("Recursive traversal of arbitrary nesting")

    document = {
        "profile": {
            "name": "Sanjay",
            "addresses": [
                {"city": "Pune", "postal_code": 411001},
                {"city": "Chennai", "postal_code": 600001},
            ],
        },
        "preferences": {
            "languages": ["Python", "SQL"],
            "notifications": {"email": True, "sms": False},
        },
    }

    for path, value in recursive_walk(document):
        print(f"{path} -> {value!r}")


def validate_customer(customer: Any) -> list[str]:
    """Return all detected structural validation errors."""
    errors: list[str] = []

    if not isinstance(customer, dict):
        return ["Customer must be a dictionary."]

    required_fields = {"id", "name", "address", "orders"}
    missing = required_fields - customer.keys()

    if missing:
        errors.append(f"Missing fields: {sorted(missing)}")

    if "id" in customer and not isinstance(customer["id"], str):
        errors.append("id must be a string.")

    if "address" in customer:
        address = customer["address"]
        if not isinstance(address, dict):
            errors.append("address must be a dictionary.")
        else:
            if not isinstance(address.get("city"), str):
                errors.append("address.city must be a string.")
            if not isinstance(address.get("postal_code"), int):
                errors.append("address.postal_code must be an integer.")

    if "orders" in customer:
        orders = customer["orders"]
        if not isinstance(orders, list):
            errors.append("orders must be a list.")
        else:
            for index, order in enumerate(orders):
                if not isinstance(order, dict):
                    errors.append(f"orders[{index}] must be a dictionary.")
                    continue
                if not isinstance(order.get("items"), list):
                    errors.append(f"orders[{index}].items must be a list.")

    return errors


def demonstrate_validation() -> None:
    print_title("Structural validation of nested data")

    valid_customer = {
        "id": "C-100",
        "name": "Aarav",
        "address": {
            "city": "Lucknow",
            "postal_code": 226001,
        },
        "orders": [
            {
                "id": "O-1",
                "items": [{"sku": "BOOK-1", "quantity": 2}],
            }
        ],
    }

    invalid_customer = {
        "id": 100,
        "name": "Broken Customer",
        "address": {"city": 42},
        "orders": {"id": "O-1"},
    }

    print("Valid customer errors:", validate_customer(valid_customer))
    print("Invalid customer errors:", validate_customer(invalid_customer))


def group_nested_records() -> None:
    print_title("Grouping nested records")

    transactions = [
        {"region": "North", "category": "Software", "amount": 12000},
        {"region": "North", "category": "Hardware", "amount": 18000},
        {"region": "South", "category": "Software", "amount": 9000},
        {"region": "North", "category": "Software", "amount": 7000},
        {"region": "South", "category": "Hardware", "amount": 11000},
    ]

    grouped: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for transaction in transactions:
        grouped[transaction["region"]][transaction["category"]].append(
            transaction["amount"]
        )

    normalized = {
        region: {
            category: {
                "count": len(amounts),
                "total": sum(amounts),
                "average": sum(amounts) / len(amounts),
            }
            for category, amounts in categories.items()
        }
        for region, categories in grouped.items()
    }

    print(json.dumps(normalized, indent=2))


def flatten_dictionary(
    data: dict[str, Any],
    prefix: str = "",
    separator: str = ".",
) -> dict[str, Any]:
    """
    Convert nested dictionaries into dotted paths.

    Lists remain values because flattening list indexes changes the semantic
    distinction between an ordered collection and a dictionary hierarchy.
    """
    flattened: dict[str, Any] = {}

    for key, value in data.items():
        path = f"{prefix}{separator}{key}" if prefix else str(key)

        if isinstance(value, dict):
            flattened.update(flatten_dictionary(value, path, separator))
        else:
            flattened[path] = value

    return flattened


def demonstrate_flattening() -> None:
    print_title("Flattening nested dictionaries")

    settings = {
        "server": {
            "http": {"host": "0.0.0.0", "port": 8080},
            "limits": {"requests_per_minute": 120},
        },
        "logging": {
            "level": "INFO",
            "outputs": ["console", "file"],
        },
    }

    print(json.dumps(flatten_dictionary(settings), indent=2))


def normalize_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Normalize selected nested fields into a flat reporting representation.
    This is useful when nested operational data must be consumed by a table
    or reporting system.
    """
    normalized: list[dict[str, Any]] = []

    for record in records:
        customer = record.get("customer", {})
        address = customer.get("address", {})
        normalized.append(
            {
                "order_id": record.get("id"),
                "customer_name": customer.get("name"),
                "city": address.get("city"),
                "item_count": sum(
                    item.get("quantity", 0)
                    for item in record.get("items", [])
                ),
            }
        )

    return normalized


def json_file_round_trip() -> None:
    print_title("Serialization of nested lists and dictionaries")

    payload = {
        "service": "inventory",
        "version": 3,
        "features": ["stock", "pricing"],
        "database": {
            "host": "localhost",
            "replicas": [
                {"host": "db-replica-1", "read_only": True},
                {"host": "db-replica-2", "read_only": True},
            ],
        },
    }

    output_path = Path("nested_data_demo.json")

    try:
        output_path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )
        restored = json.loads(output_path.read_text(encoding="utf-8"))
        print("Serialized and restored successfully.")
        print("Replica count:", len(restored["database"]["replicas"]))
    finally:
        if output_path.exists():
            output_path.unlink()


def compare_nested_structures() -> None:
    print_title("Equality, identity, and mutable nested data")

    first = {"items": [{"name": "A"}, {"name": "B"}]}
    second = {"items": [{"name": "A"}, {"name": "B"}]}

    print("Equal values:", first == second)
    print("Same outer object:", first is second)

    alias = first["items"]
    alias.append({"name": "C"})

    print("Mutation through alias:", first)

    copied = deepcopy(first)
    copied["items"].append({"name": "D"})

    print("Original after deepcopy mutation:", first)
    print("Independent copy:", copied)


@dataclass
class InventoryIndex:
    """
    Build indexes over nested inventory records.

    The source data stays nested for readability while indexes provide faster
    lookup by SKU and category.
    """

    products: list[dict[str, Any]]

    def __post_init__(self) -> None:
        self.by_sku: dict[str, dict[str, Any]] = {}
        self.by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for product in self.products:
            sku = product["sku"]
            category = product["category"]

            if sku in self.by_sku:
                raise ValueError(f"Duplicate SKU: {sku}")

            self.by_sku[sku] = product
            self.by_category[category].append(product)

    def find_sku(self, sku: str) -> dict[str, Any] | None:
        return self.by_sku.get(sku)

    def products_in_category(self, category: str) -> list[dict[str, Any]]:
        return list(self.by_category.get(category, []))


def advanced_inventory_case() -> None:
    print_title("Advanced case: nested inventory with indexes")

    products = [
        {
            "sku": "LAP-100",
            "name": "Developer Laptop",
            "category": "computing",
            "pricing": {"currency": "INR", "amount": 95000},
            "warehouses": [
                {"city": "Delhi", "quantity": 12},
                {"city": "Pune", "quantity": 8},
            ],
        },
        {
            "sku": "MON-200",
            "name": "4K Monitor",
            "category": "display",
            "pricing": {"currency": "INR", "amount": 42000},
            "warehouses": [
                {"city": "Delhi", "quantity": 5},
                {"city": "Pune", "quantity": 11},
            ],
        },
        {
            "sku": "LAP-300",
            "name": "Engineering Laptop",
            "category": "computing",
            "pricing": {"currency": "INR", "amount": 125000},
            "warehouses": [
                {"city": "Bengaluru", "quantity": 7},
            ],
        },
    ]

    index = InventoryIndex(products)

    product = index.find_sku("LAP-100")
    print("SKU lookup:", product["name"] if product else None)

    print(
        "Computing products:",
        [item["name"] for item in index.products_in_category("computing")],
    )

    warehouse_stock = Counter()
    for item in products:
        for warehouse in item["warehouses"]:
            warehouse_stock[warehouse["city"]] += warehouse["quantity"]

    print("Stock by warehouse:", dict(warehouse_stock))


def performance_notes() -> None:
    print_title("Performance characteristics")

    print("Direct nested dictionary lookup is approximately O(depth).")
    print("Scanning every record in a nested list is O(n).")
    print("Building a dictionary index is O(n) and can make repeated key lookups O(1) average.")
    print("Recursive traversal visits each contained value once, O(n) in the number of nodes.")
    print("Deep copying costs time and memory proportional to the copied nested structure.")


def main() -> None:
    beginner_nested_lists()
    nested_dictionaries()
    mixed_nested_structure()
    demonstrate_nested_access()
    transform_nested_data()
    demonstrate_recursive_traversal()
    demonstrate_validation()
    group_nested_records()
    demonstrate_flattening()

    records = [
        {
            "id": "ORD-7",
            "customer": {
                "name": "Neha",
                "address": {"city": "Hyderabad"},
            },
            "items": [
                {"sku": "A", "quantity": 3},
                {"sku": "B", "quantity": 2},
            ],
        }
    ]

    print_title("Nested-to-flat reporting transformation")
    print(normalize_records(records))

    json_file_round_trip()
    compare_nested_structures()
    advanced_inventory_case()
    performance_notes()

    print_title("Completed")
    print("All nested-list and nested-dictionary demonstrations completed.")


if __name__ == "__main__":
    main()
