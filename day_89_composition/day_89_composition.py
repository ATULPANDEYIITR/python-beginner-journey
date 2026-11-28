"""
COMPOSITION IN PYTHON
=====================

Demonstrates object composition, dependency injection, delegation,
component reuse, nested composition, and runtime behavior.

Composition models a HAS-A relationship: an object contains other
objects and delegates responsibilities to them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol
from abc import ABC, abstractmethod
from enum import Enum
import json
import logging
from pathlib import Path


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# 1. Fundamental composition using ordinary classes
# ---------------------------------------------------------

class Engine:
    def __init__(self, horsepower: int):
        if horsepower <= 0:
            raise ValueError("Horsepower must be positive")

        self.horsepower = horsepower
        self.running = False

    def start(self) -> None:
        if self.running:
            raise RuntimeError("Engine is already running")

        self.running = True
        logger.info("Engine started")

    def stop(self) -> None:
        if not self.running:
            raise RuntimeError("Engine is not running")

        self.running = False
        logger.info("Engine stopped")


class Transmission:
    def __init__(self, gears: int):
        if gears < 1:
            raise ValueError("Transmission must have at least one gear")

        self.gears = gears
        self.current_gear = 0

    def shift(self, gear: int) -> None:
        if not 1 <= gear <= self.gears:
            raise ValueError("Invalid gear")

        self.current_gear = gear
        logger.info("Transmission shifted to gear %s", gear)


class Car:
    """
    Car composes Engine and Transmission.

    The Car delegates engine and transmission operations
    instead of implementing those responsibilities itself.
    """

    def __init__(
        self,
        engine: Engine,
        transmission: Transmission
    ):
        self.engine = engine
        self.transmission = transmission

    def start(self) -> None:
        self.engine.start()

    def drive(self, gear: int) -> None:
        if not self.engine.running:
            raise RuntimeError("Start the engine before driving")

        self.transmission.shift(gear)

    def stop(self) -> None:
        self.engine.stop()


# ---------------------------------------------------------
# 2. Composition using protocols and dependency injection
# ---------------------------------------------------------

class Storage(Protocol):
    def save(self, key: str, value: str) -> None:
        ...

    def load(self, key: str) -> str | None:
        ...


class MemoryStorage:
    def __init__(self):
        self.data: dict[str, str] = {}

    def save(self, key: str, value: str) -> None:
        self.data[key] = value

    def load(self, key: str) -> str | None:
        return self.data.get(key)


class FileStorage:
    def __init__(self, directory: Path):
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        # Restrict keys to safe filenames.
        if not key or not key.isalnum():
            raise ValueError("Storage key must be alphanumeric")

        return self.directory / f"{key}.json"

    def save(self, key: str, value: str) -> None:
        path = self._path(key)
        temporary = path.with_suffix(".tmp")

        try:
            temporary.write_text(value, encoding="utf-8")
            temporary.replace(path)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise

    def load(self, key: str) -> str | None:
        path = self._path(key)

        if not path.exists():
            return None

        return path.read_text(encoding="utf-8")


class UserRepository:
    def __init__(self, storage: Storage):
        self.storage = storage

    def save_user(self, user_id: str, user: dict) -> None:
        if not user_id:
            raise ValueError("User ID cannot be empty")

        if not isinstance(user, dict):
            raise TypeError("User must be a dictionary")

        serialized = json.dumps(user)
        self.storage.save(user_id, serialized)

    def get_user(self, user_id: str) -> dict | None:
        result = self.storage.load(user_id)

        if result is None:
            return None

        try:
            return json.loads(result)
        except json.JSONDecodeError as exc:
            raise ValueError("Stored user data is invalid") from exc


# ---------------------------------------------------------
# 3. Composition using abstract interfaces
# ---------------------------------------------------------

class NotificationChannel(ABC):

    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        pass


class EmailChannel(NotificationChannel):

    def send(self, recipient: str, message: str) -> bool:
        if "@" not in recipient:
            raise ValueError("Invalid email address")

        logger.info("Email sent to %s: %s", recipient, message)
        return True


class SMSChannel(NotificationChannel):

    def send(self, recipient: str, message: str) -> bool:
        if not recipient.isdigit():
            raise ValueError("Phone number must contain digits only")

        logger.info("SMS sent to %s: %s", recipient, message)
        return True


class NotificationService:
    """
    The service composes a notification channel.

    Different channel implementations can be injected without
    changing the notification service.
    """

    def __init__(self, channel: NotificationChannel):
        self.channel = channel

    def notify(self, recipient: str, message: str) -> bool:
        if not message.strip():
            raise ValueError("Message cannot be empty")

        return self.channel.send(recipient, message)


# ---------------------------------------------------------
# 4. Nested composition using dataclasses
# ---------------------------------------------------------

@dataclass
class Address:
    street: str
    city: str
    country: str

    def __post_init__(self):
        if not all(
            value.strip()
            for value in (self.street, self.city, self.country)
        ):
            raise ValueError("Address fields cannot be empty")


@dataclass
class Customer:
    customer_id: str
    name: str
    address: Address

    def __post_init__(self):
        if not self.customer_id.strip():
            raise ValueError("Customer ID cannot be empty")


@dataclass
class Product:
    product_id: str
    name: str
    price: float

    def __post_init__(self):
        if self.price < 0:
            raise ValueError("Price cannot be negative")


@dataclass
class OrderItem:
    product: Product
    quantity: int

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")

    @property
    def subtotal(self) -> float:
        return self.product.price * self.quantity


@dataclass
class Order:
    order_id: str
    customer: Customer
    items: list[OrderItem] = field(default_factory=list)

    def add_item(self, item: OrderItem) -> None:
        self.items.append(item)

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)

    def invoice(self) -> dict:
        return {
            "order_id": self.order_id,
            "customer": self.customer.name,
            "city": self.customer.address.city,
            "items": [
                {
                    "product": item.product.name,
                    "quantity": item.quantity,
                    "subtotal": item.subtotal
                }
                for item in self.items
            ],
            "total": self.total
        }


# ---------------------------------------------------------
# 5. Advanced composition: reusable application components
# ---------------------------------------------------------

class OrderStatus(Enum):
    CREATED = "created"
    VALIDATED = "validated"
    PAID = "paid"
    CANCELLED = "cancelled"


class PaymentProcessor:

    def charge(self, amount: float) -> str:
        if amount <= 0:
            raise ValueError("Payment amount must be positive")

        # Demonstration processor. No real financial transaction.
        return f"PAY-{int(amount * 100)}"


class Inventory:

    def __init__(self, stock: dict[str, int]):
        self.stock = dict(stock)

        if any(quantity < 0 for quantity in self.stock.values()):
            raise ValueError("Stock cannot be negative")

    def reserve(self, product_id: str, quantity: int) -> bool:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        available = self.stock.get(product_id, 0)

        if available < quantity:
            return False

        self.stock[product_id] -= quantity
        return True

    def release(self, product_id: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        self.stock[product_id] = (
            self.stock.get(product_id, 0) + quantity
        )


class OrderApplication:
    """
    Higher-level component composed from independent services.

    The application coordinates inventory, payment, and notification.
    """

    def __init__(
        self,
        inventory: Inventory,
        payment: PaymentProcessor,
        notifications: NotificationService
    ):
        self.inventory = inventory
        self.payment = payment
        self.notifications = notifications

    def process(
        self,
        order: Order,
        recipient: str
    ) -> dict:

        if not order.items:
            raise ValueError("Cannot process an empty order")

        reservations: list[tuple[str, int]] = []

        try:
            # Reserve every requested product.
            for item in order.items:
                product_id = item.product.product_id

                if not self.inventory.reserve(
                    product_id,
                    item.quantity
                ):
                    raise RuntimeError(
                        f"Insufficient inventory for {product_id}"
                    )

                reservations.append((product_id, item.quantity))

            # Charge only after successful inventory reservation.
            payment_reference = self.payment.charge(order.total)

            # Notification failure does not reverse a completed payment.
            try:
                self.notifications.notify(
                    recipient,
                    f"Order {order.order_id} paid successfully"
                )
                notification_sent = True
            except (ValueError, OSError) as exc:
                logger.error("Notification failed: %s", exc)
                notification_sent = False

            return {
                "order_id": order.order_id,
                "status": OrderStatus.PAID.value,
                "payment_reference": payment_reference,
                "total": order.total,
                "notification_sent": notification_sent
            }

        except Exception:
            # Compensate inventory reservations when processing fails.
            for product_id, quantity in reversed(reservations):
                self.inventory.release(product_id, quantity)

            raise


# ---------------------------------------------------------
# 6. Executable examples and verification
# ---------------------------------------------------------

def demonstrate_basic_composition() -> None:
    print("\n1. BASIC COMPOSITION")

    car = Car(
        engine=Engine(180),
        transmission=Transmission(6)
    )

    car.start()
    car.drive(3)
    car.stop()


def demonstrate_dependency_injection() -> None:
    print("\n2. DEPENDENCY INJECTION")

    storage = MemoryStorage()
    repository = UserRepository(storage)

    repository.save_user(
        "USER001",
        {"name": "Atul", "role": "developer"}
    )

    print(repository.get_user("USER001"))

    file_storage = FileStorage(Path("composition_data"))
    file_repository = UserRepository(file_storage)

    file_repository.save_user(
        "USER002",
        {"name": "Researcher", "active": True}
    )

    print(file_repository.get_user("USER002"))


def demonstrate_notifications() -> None:
    print("\n3. SERVICE COMPOSITION")

    email_service = NotificationService(EmailChannel())
    email_service.notify(
        "developer@example.com",
        "Build completed"
    )

    sms_service = NotificationService(SMSChannel())
    sms_service.notify(
        "9876543210",
        "Deployment completed"
    )


def demonstrate_nested_composition() -> Order:
    print("\n4. NESTED COMPOSITION")

    customer = Customer(
        customer_id="C001",
        name="Atul Pandey",
        address=Address(
            street="Sector 1",
            city="Lucknow",
            country="India"
        )
    )

    laptop = Product("P001", "Laptop", 65000)
    keyboard = Product("P002", "Keyboard", 2500)

    order = Order("ORD001", customer)

    order.add_item(OrderItem(laptop, 1))
    order.add_item(OrderItem(keyboard, 2))

    print(json.dumps(order.invoice(), indent=4))

    return order


def demonstrate_application_composition(order: Order) -> None:
    print("\n5. ADVANCED APPLICATION COMPOSITION")

    inventory = Inventory({
        "P001": 5,
        "P002": 10
    })

    application = OrderApplication(
        inventory=inventory,
        payment=PaymentProcessor(),
        notifications=NotificationService(EmailChannel())
    )

    result = application.process(
        order,
        "customer@example.com"
    )

    print(json.dumps(result, indent=4))
    print("Remaining inventory:", inventory.stock)


def demonstrate_failure_handling() -> None:
    print("\n6. FAILURE HANDLING")

    inventory = Inventory({"P001": 1})

    try:
        inventory.reserve("P001", 5)
    except ValueError as exc:
        print("Validation error:", exc)

    result = inventory.reserve("P001", 5)
    print("Reservation successful:", result)

    assert inventory.stock["P001"] == 1

    try:
        Car(
            Engine(0),
            Transmission(5)
        )
    except ValueError as exc:
        print("Invalid component:", exc)


def run_tests() -> None:
    print("\n7. AUTOMATED ASSERTIONS")

    engine = Engine(150)
    transmission = Transmission(5)
    car = Car(engine, transmission)

    assert car.engine is engine
    assert car.transmission is transmission

    car.start()
    assert engine.running

    car.drive(2)
    assert transmission.current_gear == 2

    car.stop()
    assert not engine.running

    storage = MemoryStorage()
    repository = UserRepository(storage)

    repository.save_user("TEST01", {"active": True})

    assert repository.get_user("TEST01") == {"active": True}

    address = Address("Main Road", "Lucknow", "India")
    customer = Customer("C100", "Test Customer", address)

    order = Order("O100", customer)
    order.add_item(OrderItem(Product("P100", "Monitor", 10000), 2))

    assert order.total == 20000

    inventory = Inventory({"P100": 3})

    assert inventory.reserve("P100", 2)
    assert inventory.stock["P100"] == 1

    inventory.release("P100", 2)
    assert inventory.stock["P100"] == 3

    print("All assertions passed.")


def main() -> None:
    demonstrate_basic_composition()
    demonstrate_dependency_injection()
    demonstrate_notifications()

    order = demonstrate_nested_composition()

    demonstrate_application_composition(order)
    demonstrate_failure_handling()
    run_tests()


if __name__ == "__main__":
    main()
