"""
POLYMORPHISM IN PYTHON
======================

Demonstrates:
1. Built-in polymorphism
2. Method overriding
3. Runtime polymorphism
4. Duck typing
5. Abstract base classes
6. Structural typing with Protocol
7. Operator overloading
8. Multiple inheritance
9. Composition and dependency injection
10. Factory-based object creation
11. Exception handling and validation
12. Unit-style assertions and performance considerations

Python 3.10+
Standard library only.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from math import pi
from typing import Protocol, Sequence
import logging
import math


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# 1. BUILT-IN POLYMORPHISM
# ============================================================

def demonstrate_builtin_polymorphism() -> None:
    """The same function behaves differently for different objects."""

    values = [
        [10, 20, 30],
        "Python",
        (1, 2, 3),
        {1, 2, 3}
    ]

    for value in values:
        print(f"{type(value).__name__}: length={len(value)}")


# ============================================================
# 2. METHOD OVERRIDING AND RUNTIME POLYMORPHISM
# ============================================================

class Employee:
    """Base class defining a common employee interface."""

    def __init__(self, name: str) -> None:
        if not name.strip():
            raise ValueError("Employee name cannot be empty.")

        self.name = name

    def calculate_salary(self) -> float:
        raise NotImplementedError(
            "Subclasses must implement calculate_salary()."
        )

    def describe(self) -> str:
        return (
            f"{self.name}: "
            f"Salary = {self.calculate_salary():,.2f}"
        )


class FullTimeEmployee(Employee):

    def __init__(
        self,
        name: str,
        monthly_salary: float,
        bonus: float = 0.0
    ) -> None:
        super().__init__(name)

        if not math.isfinite(monthly_salary) or monthly_salary < 0:
            raise ValueError("Invalid monthly salary.")

        if not math.isfinite(bonus) or bonus < 0:
            raise ValueError("Invalid bonus.")

        self.monthly_salary = monthly_salary
        self.bonus = bonus

    def calculate_salary(self) -> float:
        return self.monthly_salary + self.bonus


class ContractEmployee(Employee):

    def __init__(
        self,
        name: str,
        hourly_rate: float,
        hours_worked: float
    ) -> None:
        super().__init__(name)

        if not math.isfinite(hourly_rate) or hourly_rate < 0:
            raise ValueError("Invalid hourly rate.")

        if (
            not math.isfinite(hours_worked)
            or not 0 <= hours_worked <= 744
        ):
            raise ValueError("Hours must be between 0 and 744.")

        self.hourly_rate = hourly_rate
        self.hours_worked = hours_worked

    def calculate_salary(self) -> float:
        return self.hourly_rate * self.hours_worked


class CommissionEmployee(Employee):

    def __init__(
        self,
        name: str,
        base_salary: float,
        sales: float,
        commission_rate: float
    ) -> None:
        super().__init__(name)

        if not all(
            math.isfinite(value)
            for value in (base_salary, sales, commission_rate)
        ):
            raise ValueError("Financial values must be finite.")

        if base_salary < 0 or sales < 0:
            raise ValueError("Salary and sales cannot be negative.")

        if not 0 <= commission_rate <= 1:
            raise ValueError("Commission rate must be between 0 and 1.")

        self.base_salary = base_salary
        self.sales = sales
        self.commission_rate = commission_rate

    def calculate_salary(self) -> float:
        return self.base_salary + (
            self.sales * self.commission_rate
        )


def process_payroll(
    employees: Sequence[Employee]
) -> list[dict[str, str | float]]:
    """
    Runtime polymorphism:
    Each employee receives the same method call, but its
    concrete implementation determines the result.
    """

    payroll = []

    for employee in employees:
        salary = employee.calculate_salary()

        if not math.isfinite(salary):
            raise ArithmeticError("Invalid payroll calculation.")

        payroll.append({
            "employee": employee.name,
            "salary": salary,
            "description": employee.describe()
        })

    return payroll


# ============================================================
# 3. ABSTRACT BASE CLASSES
# ============================================================

class PaymentProcessor(ABC):
    """Defines a contract for payment implementations."""

    @abstractmethod
    def process_payment(self, amount: float) -> str:
        pass

    def validate_amount(self, amount: float) -> None:
        if not math.isfinite(amount) or amount <= 0:
            raise ValueError("Payment must be a positive finite amount.")


class CardPayment(PaymentProcessor):

    def process_payment(self, amount: float) -> str:
        self.validate_amount(amount)
        return f"Card payment processed: {amount:.2f}"


class BankTransfer(PaymentProcessor):

    def process_payment(self, amount: float) -> str:
        self.validate_amount(amount)
        return f"Bank transfer processed: {amount:.2f}"


class UpiPayment(PaymentProcessor):

    def process_payment(self, amount: float) -> str:
        self.validate_amount(amount)
        return f"UPI payment processed: {amount:.2f}"


def execute_payment(
    processor: PaymentProcessor,
    amount: float
) -> str:
    return processor.process_payment(amount)


# ============================================================
# 4. DUCK TYPING
# ============================================================

class PDFDocument:

    def render(self) -> str:
        return "PDF document rendered."


class HTMLDocument:

    def render(self) -> str:
        return "HTML document rendered."


class SpreadsheetDocument:

    def render(self) -> str:
        return "Spreadsheet document rendered."


def render_document(document: object) -> str:
    """
    Duck typing:
    The function requires a render() method rather than
    a particular inheritance relationship.
    """

    render_method = getattr(document, "render", None)

    if not callable(render_method):
        raise TypeError("Object must provide a callable render() method.")

    result = render_method()

    if not isinstance(result, str):
        raise TypeError("render() must return a string.")

    return result


# ============================================================
# 5. STRUCTURAL TYPING WITH PROTOCOL
# ============================================================

class Exportable(Protocol):
    def export(self) -> bytes:
        ...


@dataclass
class JSONReport:
    data: dict

    def export(self) -> bytes:
        import json
        return json.dumps(
            self.data,
            sort_keys=True,
            default=str
        ).encode("utf-8")


@dataclass
class TextReport:
    content: str

    def export(self) -> bytes:
        return self.content.encode("utf-8")


def save_report(
    report: Exportable,
    filename: str
) -> int:
    """
    Accepts any object implementing export().
    No explicit inheritance is required.
    """

    if not filename or filename != filename.strip():
        raise ValueError("Invalid filename.")

    if not filename.endswith((".json", ".txt")):
        raise ValueError("Unsupported report extension.")

    data = report.export()

    if not isinstance(data, bytes):
        raise TypeError("export() must return bytes.")

    if len(data) > 1_000_000:
        raise ValueError("Report exceeds maximum size.")

    with open(filename, "wb") as file:
        file.write(data)

    return len(data)


# ============================================================
# 6. OPERATOR OVERLOADING
# ============================================================

@dataclass(frozen=True)
class Vector:
    x: float
    y: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.x) or not math.isfinite(self.y):
            raise ValueError("Vector coordinates must be finite.")

    def __add__(self, other: object) -> Vector:
        if not isinstance(other, Vector):
            return NotImplemented

        return Vector(
            self.x + other.x,
            self.y + other.y
        )

    def __sub__(self, other: object) -> Vector:
        if not isinstance(other, Vector):
            return NotImplemented

        return Vector(
            self.x - other.x,
            self.y - other.y
        )

    def __mul__(self, scalar: float) -> Vector:
        if isinstance(scalar, bool) or not isinstance(scalar, (int, float)):
            return NotImplemented

        if not math.isfinite(scalar):
            raise ValueError("Scalar must be finite.")

        return Vector(
            self.x * scalar,
            self.y * scalar
        )

    def magnitude(self) -> float:
        return math.hypot(self.x, self.y)


# ============================================================
# 7. MULTIPLE INHERITANCE AND METHOD RESOLUTION ORDER
# ============================================================

class LoggerMixin:

    def log(self, message: str) -> None:
        logger.info(message)


class ValidatorMixin:

    @staticmethod
    def validate_non_empty(value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Value cannot be empty.")


class SecureService(LoggerMixin, ValidatorMixin):

    def execute(self, operation: str) -> str:
        self.validate_non_empty(operation)

        result = f"Executed operation: {operation}"
        self.log(result)

        return result


# ============================================================
# 8. COMPOSITION AND DEPENDENCY INJECTION
# ============================================================

class NotificationChannel(ABC):

    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        pass


class EmailChannel(NotificationChannel):

    def send(self, recipient: str, message: str) -> bool:
        if "@" not in recipient:
            raise ValueError("Invalid email recipient.")

        if not message.strip():
            raise ValueError("Message cannot be empty.")

        return True


class SMSChannel(NotificationChannel):

    def send(self, recipient: str, message: str) -> bool:
        if not recipient.isdigit() or not 8 <= len(recipient) <= 15:
            raise ValueError("Invalid telephone number.")

        if not message.strip():
            raise ValueError("Message cannot be empty.")

        return True


class NotificationService:
    """Uses composition rather than inheriting channel behavior."""

    def __init__(self, channel: NotificationChannel) -> None:
        self.channel = channel

    def notify(self, recipient: str, message: str) -> bool:
        return self.channel.send(recipient, message)


# ============================================================
# 9. FACTORY PATTERN AND POLYMORPHIC OBJECT CREATION
# ============================================================

class PaymentFactory:

    _processors = {
        "card": CardPayment,
        "bank": BankTransfer,
        "upi": UpiPayment
    }

    @classmethod
    def create(cls, payment_type: str) -> PaymentProcessor:
        if not isinstance(payment_type, str):
            raise TypeError("Payment type must be a string.")

        processor_class = cls._processors.get(payment_type.lower())

        if processor_class is None:
            raise ValueError("Unsupported payment type.")

        return processor_class()


# ============================================================
# 10. DEMONSTRATION AND VALIDATION
# ============================================================

def run_tests() -> None:

    print("\n1. BUILT-IN POLYMORPHISM")
    demonstrate_builtin_polymorphism()

    print("\n2. RUNTIME POLYMORPHISM")

    employees: list[Employee] = [
        FullTimeEmployee("Ananya", 75000, 10000),
        ContractEmployee("Rahul", 850, 160),
        CommissionEmployee("Priya", 30000, 200000, 0.05)
    ]

    for record in process_payroll(employees):
        print(record["description"])

    print("\n3. ABSTRACT CLASS POLYMORPHISM")

    processors = [
        CardPayment(),
        BankTransfer(),
        UpiPayment()
    ]

    for processor in processors:
        print(execute_payment(processor, 2500))

    print("\n4. DUCK TYPING")

    documents = [
        PDFDocument(),
        HTMLDocument(),
        SpreadsheetDocument()
    ]

    for document in documents:
        print(render_document(document))

    print("\n5. STRUCTURAL TYPING")

    json_report = JSONReport({
        "department": "Engineering",
        "employees": 3
    })

    text_report = TextReport("Monthly operational report")

    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as directory:
        json_path = str(Path(directory) / "report.json")
        text_path = str(Path(directory) / "report.txt")

        assert save_report(json_report, json_path) > 0
        assert save_report(text_report, text_path) > 0

        assert Path(json_path).exists()
        assert Path(text_path).exists()

        print("Reports exported successfully.")

    print("\n6. OPERATOR OVERLOADING")

    first = Vector(3, 4)
    second = Vector(1, 2)

    print("Addition:", first + second)
    print("Subtraction:", first - second)
    print("Scaling:", first * 2)
    print("Magnitude:", first.magnitude())

    print("\n7. MULTIPLE INHERITANCE")

    service = SecureService()
    print(service.execute("update_inventory"))

    print("\n8. COMPOSITION")

    email_service = NotificationService(EmailChannel())
    sms_service = NotificationService(SMSChannel())

    assert email_service.notify(
        "operations@example.com",
        "System operational."
    )

    assert sms_service.notify(
        "9876543210",
        "Alert: Service restored."
    )

    print("Notifications processed.")

    print("\n9. FACTORY")

    payment = PaymentFactory.create("upi")
    print(payment.process_payment(1500))

    print("\n10. EDGE CASE VALIDATION")

    invalid_cases = [
        lambda: FullTimeEmployee("", 50000),
        lambda: ContractEmployee("A", 100, -1),
        lambda: CardPayment().process_payment(-500),
        lambda: render_document(object()),
        lambda: PaymentFactory.create("cryptocurrency"),
        lambda: Vector(float("nan"), 2)
    ]

    for test in invalid_cases:
        try:
            test()
            raise AssertionError("Expected validation failure.")
        except (ValueError, TypeError, ArithmeticError):
            print("Invalid input rejected correctly.")

    print("\nAll tests passed.")


if __name__ == "__main__":
    run_tests()
