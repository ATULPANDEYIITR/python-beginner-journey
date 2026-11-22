"""
STATIC METHODS: FUNDAMENTALS TO ADVANCED IMPLEMENTATION

Demonstrates:
1. Static method declaration and invocation.
2. Static methods versus instance methods and class methods.
3. Stateless utility operations.
4. Input validation and exception handling.
5. Shared class-level state.
6. Factory methods.
7. Mathematical operations.
8. Configuration validation.
9. Caching and memoization.
10. Unit testing and execution.

Requirements: Python 3.10+
Dependencies: Python standard library only.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any


# ============================================================
# 1. FUNDAMENTAL STATIC METHODS
# ============================================================

class Calculator:
    """A utility class containing operations that need no object state."""

    @staticmethod
    def add(a: float, b: float) -> float:
        return a + b

    @staticmethod
    def subtract(a: float, b: float) -> float:
        return a - b

    @staticmethod
    def multiply(a: float, b: float) -> float:
        return a * b

    @staticmethod
    def divide(a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Division by zero is not permitted.")
        return a / b

    @staticmethod
    def percentage(value: float, total: float) -> float:
        if total == 0:
            raise ValueError("Total cannot be zero.")
        return (value / total) * 100


# ============================================================
# 2. STATIC METHODS VERSUS INSTANCE METHODS
# ============================================================

class Employee:
    organization = "Technology Research Division"

    def __init__(self, employee_id: int, name: str, salary: float):
        if employee_id <= 0:
            raise ValueError("Employee ID must be positive.")
        if not name.strip():
            raise ValueError("Employee name cannot be empty.")
        if salary < 0 or not math.isfinite(salary):
            raise ValueError("Salary must be a finite non-negative number.")

        self.employee_id = employee_id
        self.name = name.strip()
        self.salary = salary

    def annual_salary(self) -> float:
        """Instance method: reads object-specific state."""
        return self.salary * 12

    @staticmethod
    def validate_employee_id(employee_id: int) -> bool:
        """Static method: validates input without accessing object state."""
        return isinstance(employee_id, int) and not isinstance(employee_id, bool) and employee_id > 0

    @classmethod
    def from_dictionary(cls, data: dict[str, Any]) -> Employee:
        """Class method: creates an object using the receiving class."""
        return cls(
            employee_id=int(data["employee_id"]),
            name=str(data["name"]),
            salary=float(data["salary"]),
        )


# ============================================================
# 3. STATIC METHODS FOR DATA VALIDATION
# ============================================================

class DataValidator:

    @staticmethod
    def validate_email(email: str) -> bool:
        if not isinstance(email, str):
            return False

        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        return re.fullmatch(pattern, email) is not None

    @staticmethod
    def validate_password(password: str) -> bool:
        if not isinstance(password, str) or len(password) < 12:
            return False

        return (
            any(char.isupper() for char in password)
            and any(char.islower() for char in password)
            and any(char.isdigit() for char in password)
            and any(not char.isalnum() for char in password)
        )

    @staticmethod
    def validate_amount(amount: float) -> bool:
        return (
            isinstance(amount, (int, float))
            and not isinstance(amount, bool)
            and math.isfinite(amount)
            and amount >= 0
        )


# ============================================================
# 4. STATIC METHODS FOR ENUMERATIONS AND BUSINESS RULES
# ============================================================

class TransactionType(Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class TransactionRules:

    @staticmethod
    def validate_transaction(
        transaction_type: TransactionType,
        amount: float,
    ) -> bool:
        if not isinstance(transaction_type, TransactionType):
            return False

        return DataValidator.validate_amount(amount) and amount > 0

    @staticmethod
    def calculate_balance(
        opening_balance: float,
        transaction_type: TransactionType,
        amount: float,
    ) -> float:
        if not DataValidator.validate_amount(opening_balance):
            raise ValueError("Invalid opening balance.")

        if not TransactionRules.validate_transaction(transaction_type, amount):
            raise ValueError("Invalid transaction.")

        if transaction_type == TransactionType.CREDIT:
            return opening_balance + amount

        if amount > opening_balance:
            raise ValueError("Insufficient funds.")

        return opening_balance - amount


# ============================================================
# 5. STATIC FACTORY METHODS AND IMMUTABLE DATA
# ============================================================

@dataclass(frozen=True)
class Product:
    product_id: int
    name: str
    price: float
    category: str


class ProductFactory:

    @staticmethod
    def create_product(
        product_id: int,
        name: str,
        price: float,
        category: str,
    ) -> Product:
        if product_id <= 0:
            raise ValueError("Product ID must be positive.")

        if not name.strip() or not category.strip():
            raise ValueError("Name and category are required.")

        if not DataValidator.validate_amount(price):
            raise ValueError("Invalid product price.")

        return Product(
            product_id=product_id,
            name=name.strip(),
            price=float(price),
            category=category.strip(),
        )

    @staticmethod
    def from_json(payload: str) -> Product:
        try:
            data = json.loads(payload)

            if not isinstance(data, dict):
                raise ValueError("Product JSON must contain an object.")

            return ProductFactory.create_product(
                product_id=data["product_id"],
                name=data["name"],
                price=data["price"],
                category=data["category"],
            )
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("Invalid product JSON.") from exc


# ============================================================
# 6. STATIC METHODS WITH CACHING
# ============================================================

class MathematicalUtilities:

    @staticmethod
    @lru_cache(maxsize=256)
    def factorial(number: int) -> int:
        if isinstance(number, bool) or not isinstance(number, int):
            raise TypeError("Factorial requires an integer.")

        if number < 0:
            raise ValueError("Factorial is undefined for negative integers.")

        if number > 1000:
            raise ValueError("Input exceeds the configured computation limit.")

        if number < 2:
            return 1

        return number * MathematicalUtilities.factorial(number - 1)

    @staticmethod
    def is_prime(number: int) -> bool:
        if isinstance(number, bool) or not isinstance(number, int):
            raise TypeError("Prime checking requires an integer.")

        if number < 2:
            return False

        if number % 2 == 0:
            return number == 2

        divisor = 3

        while divisor * divisor <= number:
            if number % divisor == 0:
                return False
            divisor += 2

        return True


# ============================================================
# 7. STATIC METHODS FOR SECURITY AND DATA INTEGRITY
# ============================================================

class SecurityUtilities:

    @staticmethod
    def sha256_digest(data: str) -> str:
        if not isinstance(data, str):
            raise TypeError("Input must be a string.")

        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    @staticmethod
    def verify_sha256(data: str, expected_digest: str) -> bool:
        if not isinstance(expected_digest, str):
            return False

        if re.fullmatch(r"[a-fA-F0-9]{64}", expected_digest) is None:
            return False

        actual = SecurityUtilities.sha256_digest(data)

        return hashlib.compare_digest(
            actual,
            expected_digest.lower(),
        ) if hasattr(hashlib, "compare_digest") else __import__("hmac").compare_digest(
            actual,
            expected_digest.lower(),
        )


# ============================================================
# 8. STATIC METHODS FOR FILE OPERATIONS
# ============================================================

class FileUtilities:

    @staticmethod
    def calculate_file_hash(file_path: str | Path) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():
            raise ValueError("The supplied path is not a regular file.")

        digest = hashlib.sha256()

        # Process large files incrementally to limit memory consumption.
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(65536), b""):
                digest.update(chunk)

        return digest.hexdigest()

    @staticmethod
    def read_json(file_path: str | Path) -> dict[str, Any]:
        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(f"JSON file not found: {path}")

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object.")

        return data


# ============================================================
# 9. ADVANCED STATIC POLICY EVALUATION
# ============================================================

@dataclass(frozen=True)
class AccessRequest:
    user_role: str
    resource: str
    operation: str


class AccessPolicy:

    ALLOWED_OPERATIONS = {
        "reader": {"read"},
        "analyst": {"read", "analyze"},
        "administrator": {"read", "analyze", "write", "delete"},
    }

    @staticmethod
    def evaluate(request: AccessRequest) -> bool:
        if not all(
            isinstance(value, str) and value.strip()
            for value in (
                request.user_role,
                request.resource,
                request.operation,
            )
        ):
            return False

        permissions = AccessPolicy.ALLOWED_OPERATIONS.get(
            request.user_role.lower()
        )

        return (
            permissions is not None
            and request.operation.lower() in permissions
        )


# ============================================================
# 10. STATIC METHODS FOR CONFIGURATION MANAGEMENT
# ============================================================

class ConfigurationValidator:

    REQUIRED_FIELDS = {"application", "environment", "port"}

    @staticmethod
    def validate(config: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []

        if not isinstance(config, dict):
            return False, ["Configuration must be a dictionary."]

        missing = ConfigurationValidator.REQUIRED_FIELDS - config.keys()

        if missing:
            errors.append(f"Missing fields: {sorted(missing)}")

        if "application" in config:
            if not isinstance(config["application"], str) or not config["application"].strip():
                errors.append("Application must be a non-empty string.")

        if "environment" in config:
            if config["environment"] not in {"development", "testing", "production"}:
                errors.append("Unsupported environment.")

        if "port" in config:
            port = config["port"]

            if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
                errors.append("Port must be an integer between 1 and 65535.")

        return len(errors) == 0, errors


# ============================================================
# 11. STATIC METHODS FOR AGGREGATION
# ============================================================

class Analytics:

    @staticmethod
    def calculate_statistics(values: list[float]) -> dict[str, float]:
        if not values:
            raise ValueError("At least one observation is required.")

        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            for value in values
        ):
            raise ValueError("All observations must be finite numbers.")

        count = len(values)
        mean = math.fsum(values) / count
        sorted_values = sorted(values)

        if count % 2:
            median = sorted_values[count // 2]
        else:
            median = (
                sorted_values[count // 2 - 1]
                + sorted_values[count // 2]
            ) / 2

        variance = math.fsum(
            (value - mean) ** 2 for value in values
        ) / count

        return {
            "count": count,
            "minimum": min(values),
            "maximum": max(values),
            "mean": mean,
            "median": median,
            "population_standard_deviation": math.sqrt(variance),
        }


# ============================================================
# 12. TESTING STATIC METHOD BEHAVIOR
# ============================================================

def run_tests() -> None:
    assert Calculator.add(10, 5) == 15
    assert Calculator.subtract(10, 5) == 5
    assert Calculator.multiply(10, 5) == 50
    assert Calculator.divide(10, 5) == 2
    assert Calculator.percentage(25, 100) == 25

    try:
        Calculator.divide(10, 0)
        raise AssertionError("Division by zero was not detected.")
    except ZeroDivisionError:
        pass

    assert Employee.validate_employee_id(101)
    assert not Employee.validate_employee_id(-1)

    employee = Employee.from_dictionary({
        "employee_id": 101,
        "name": "Aarav Sharma",
        "salary": 75000,
    })

    assert employee.annual_salary() == 900000

    assert DataValidator.validate_email("user@example.com")
    assert not DataValidator.validate_email("invalid-email")

    assert DataValidator.validate_password("StrongPassword123!")
    assert not DataValidator.validate_password("weak")

    assert TransactionRules.calculate_balance(
        1000,
        TransactionType.CREDIT,
        500,
    ) == 1500

    product = ProductFactory.create_product(
        1,
        "Enterprise Laptop",
        85000,
        "Electronics",
    )

    assert product.price == 85000

    assert MathematicalUtilities.factorial(5) == 120
    assert MathematicalUtilities.is_prime(97)
    assert not MathematicalUtilities.is_prime(100)

    digest = SecurityUtilities.sha256_digest("repository")
    assert SecurityUtilities.verify_sha256("repository", digest)
    assert not SecurityUtilities.verify_sha256("different", digest)

    request = AccessRequest(
        "analyst",
        "financial-report",
        "analyze",
    )

    assert AccessPolicy.evaluate(request)

    config = {
        "application": "StaticMethodService",
        "environment": "production",
        "port": 8080,
    }

    valid, errors = ConfigurationValidator.validate(config)
    assert valid and not errors

    statistics = Analytics.calculate_statistics([10, 20, 30, 40])
    assert statistics["mean"] == 25
    assert statistics["median"] == 25

    print("All static method tests passed.")


# ============================================================
# 13. EXECUTABLE APPLICATION
# ============================================================

def main() -> None:
    print("=" * 60)
    print("STATIC METHODS: EXECUTION DEMONSTRATION")
    print("=" * 60)

    print("\n1. Mathematical operations")
    print("Addition:", Calculator.add(25, 15))
    print("Division:", Calculator.divide(100, 4))

    print("\n2. Employee operations")
    employee = Employee(101, "Aarav Sharma", 75000)
    print("Employee:", employee.name)
    print("Annual salary:", employee.annual_salary())
    print("Valid ID:", Employee.validate_employee_id(101))

    print("\n3. Product factory")
    product = ProductFactory.from_json(
        '{"product_id": 501, "name": "Server", '
        '"price": 125000, "category": "Hardware"}'
    )
    print("Created product:", product)

    print("\n4. Cached computation")
    print("Factorial of 10:", MathematicalUtilities.factorial(10))
    print("Cache information:", MathematicalUtilities.factorial.cache_info())

    print("\n5. Transaction processing")
    balance = TransactionRules.calculate_balance(
        5000,
        TransactionType.DEBIT,
        1200,
    )
    print("Remaining balance:", balance)

    print("\n6. Access policy")
    access = AccessPolicy.evaluate(
        AccessRequest("administrator", "repository", "write")
    )
    print("Access granted:", access)

    print("\n7. Analytics")
    print(
        json.dumps(
            Analytics.calculate_statistics([12, 18, 24, 30, 36]),
            indent=2,
        )
    )

    print("\n8. Verification")
    run_tests()


if __name__ == "__main__":
    main()
