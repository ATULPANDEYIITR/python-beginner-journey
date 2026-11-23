from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable
import json
import logging
import re
import unittest


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("property_examples")


class ValidationError(ValueError):
    pass


class PropertyAccessError(RuntimeError):
    pass


# 1. Basic property using getter and setter
class Temperature:
    def __init__(self, celsius: float):
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValidationError("Temperature must be numeric.")

        if not -273.15 <= value <= 1000:
            raise ValidationError("Temperature is outside the supported range.")

        self._celsius = float(value)

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValidationError("Fahrenheit must be numeric.")

        self.celsius = (value - 32) * 5 / 9


# 2. Read-only property
class Employee:
    def __init__(self, employee_id: int, name: str):
        if employee_id <= 0:
            raise ValidationError("Employee ID must be positive.")

        self._employee_id = employee_id
        self.name = name

    @property
    def employee_id(self) -> int:
        return self._employee_id


# 3. Computed properties
class Rectangle:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, value: float) -> None:
        if value <= 0:
            raise ValidationError("Width must be positive.")
        self._width = float(value)

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        if value <= 0:
            raise ValidationError("Height must be positive.")
        self._height = float(value)

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


# 4. Property with controlled deletion
class SecureDocument:
    def __init__(self, content: str):
        self._content = content

    @property
    def content(self) -> str:
        return self._content

    @content.deleter
    def content(self) -> None:
        self._content = "[DELETED]"


# 5. Property with caching
class ExpensiveReport:
    def __init__(self, values: list[int]):
        self.values = list(values)
        self._cached_total: int | None = None
        self.calculation_count = 0

    @property
    def total(self) -> int:
        if self._cached_total is None:
            self.calculation_count += 1
            self._cached_total = sum(self.values)
        return self._cached_total

    def add_value(self, value: int) -> None:
        self.values.append(value)
        self._cached_total = None


# 6. Property validation with multiple rules
class UserAccount:
    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(self, username: str, email: str, age: int):
        self.username = username
        self.email = email
        self.age = age
        self._active = True

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValidationError("Username must be text.")

        value = value.strip()

        if not 3 <= len(value) <= 30:
            raise ValidationError("Username must contain 3 to 30 characters.")

        if not re.fullmatch(r"[A-Za-z0-9_]+", value):
            raise ValidationError("Username contains invalid characters.")

        self._username = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValidationError("Email must be text.")

        value = value.strip().lower()

        if not self.EMAIL_PATTERN.fullmatch(value):
            raise ValidationError("Invalid email address.")

        self._email = value

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValidationError("Age must be an integer.")

        if not 18 <= value <= 120:
            raise ValidationError("Age must be between 18 and 120.")

        self._age = value

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValidationError("Active must be boolean.")
        self._active = value


# 7. Property overriding and inheritance
class Product:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        if value < 0:
            raise ValidationError("Price cannot be negative.")
        self._price = float(value)

    @property
    def display_price(self) -> str:
        return f"${self.price:.2f}"


class DiscountedProduct(Product):
    def __init__(self, name: str, price: float, discount: float):
        super().__init__(name, price)
        self.discount = discount

    @property
    def discount(self) -> float:
        return self._discount

    @discount.setter
    def discount(self, value: float) -> None:
        if not 0 <= value <= 100:
            raise ValidationError("Discount must be between 0 and 100.")
        self._discount = float(value)

    @property
    def final_price(self) -> float:
        return self.price * (1 - self.discount / 100)

    @property
    def display_price(self) -> str:
        return f"${self.final_price:.2f}"


# 8. Property backed by a descriptor
class PositiveNumber:
    def __init__(self, minimum: float = 0):
        self.minimum = minimum
        self.name: str | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{name}"

    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        if instance is None:
            return self
        return getattr(instance, self.name)

    def __set__(self, instance: Any, value: float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValidationError("Value must be numeric.")

        if value <= self.minimum:
            raise ValidationError(f"Value must be greater than {self.minimum}.")

        setattr(instance, self.name, float(value))


class BankAccount:
    balance = PositiveNumber(minimum=-0.01)

    def __init__(self, account_number: str, opening_balance: float):
        if not re.fullmatch(r"[A-Z0-9]{6,20}", account_number):
            raise ValidationError("Invalid account number.")

        self.account_number = account_number
        self.balance = opening_balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValidationError("Deposit must be positive.")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValidationError("Withdrawal must be positive.")
        if amount > self.balance:
            raise ValidationError("Insufficient funds.")
        self.balance -= amount


# 9. Property with timestamp management
class Record:
    def __init__(self, name: str):
        self.name = name
        self._updated_at = datetime.now(timezone.utc)

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Name cannot be empty.")

        self._name = value.strip()

        if hasattr(self, "_updated_at"):
            self._updated_at = datetime.now(timezone.utc)


# 10. Testing property behavior
class PropertyTests(unittest.TestCase):

    def test_temperature_conversion(self):
        temperature = Temperature(100)
        self.assertAlmostEqual(temperature.fahrenheit, 212)

        temperature.fahrenheit = 32
        self.assertAlmostEqual(temperature.celsius, 0)

    def test_invalid_temperature(self):
        with self.assertRaises(ValidationError):
            Temperature(-300)

    def test_read_only_property(self):
        employee = Employee(101, "Asha")

        with self.assertRaises(AttributeError):
            employee.employee_id = 102

    def test_computed_property(self):
        rectangle = Rectangle(5, 4)
        self.assertEqual(rectangle.area, 20)
        self.assertEqual(rectangle.perimeter, 18)

    def test_cached_property_pattern(self):
        report = ExpensiveReport([10, 20, 30])

        self.assertEqual(report.total, 60)
        self.assertEqual(report.total, 60)
        self.assertEqual(report.calculation_count, 1)

        report.add_value(40)

        self.assertEqual(report.total, 100)
        self.assertEqual(report.calculation_count, 2)

    def test_account_validation(self):
        account = UserAccount("atul_01", "ATUL@example.com", 30)

        self.assertEqual(account.email, "atul@example.com")

        with self.assertRaises(ValidationError):
            account.age = 15

    def test_descriptor(self):
        account = BankAccount("ABC12345", 1000)
        account.deposit(500)

        self.assertEqual(account.balance, 1500)

        with self.assertRaises(ValidationError):
            account.withdraw(2000)


def demonstrate() -> None:
    print("\nPROPERTY IMPLEMENTATION DEMONSTRATION")

    temperature = Temperature(25)
    print("Temperature:", temperature.celsius, "C")
    print("Fahrenheit:", temperature.fahrenheit)

    employee = Employee(101, "Asha")
    print("Employee ID:", employee.employee_id)

    rectangle = Rectangle(10, 5)
    print("Rectangle area:", rectangle.area)

    report = ExpensiveReport([100, 200, 300])
    print("Report total:", report.total)
    print("Report total cached:", report.total)
    print("Calculations:", report.calculation_count)

    product = DiscountedProduct("Laptop", 1000, 15)
    print("Discounted price:", product.display_price)

    account = BankAccount("BANK1234", 5000)
    account.deposit(1000)
    print("Account balance:", account.balance)

    record = Record("Repository Configuration")
    print("Updated at:", record.updated_at.isoformat())

    document = SecureDocument("Confidential information")
    print("Document:", document.content)
    del document.content
    print("After deletion:", document.content)


if __name__ == "__main__":
    demonstrate()
    unittest.main(argv=["properties.py"], exit=False)
