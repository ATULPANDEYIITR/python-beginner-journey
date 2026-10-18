"""
Local and Global Variables
Demonstrates Python scope, name resolution, mutation, closures, classes,
comprehensions, exception behavior, and practical configuration management.
"""

from dataclasses import dataclass
from typing import Callable

# Module-level variables are accessible throughout this module.
APPLICATION_NAME = "Inventory Control"
DEFAULT_CURRENCY = "INR"
MAX_RETRIES = 3
request_counter = 0


def demonstrate_basic_scope() -> None:
    # A local variable exists within this function invocation.
    warehouse_name = "Lucknow Central"

    # Reading a global variable does not require the global keyword.
    print(f"Application: {APPLICATION_NAME}")
    print(f"Warehouse: {warehouse_name}")
    print(f"Currency: {DEFAULT_CURRENCY}")


def demonstrate_local_shadowing() -> None:
    # This local assignment shadows the module-level name.
    application_name = "Temporary Inventory Tool"
    print(f"Local name: {application_name}")
    print(f"Global name remains: {APPLICATION_NAME}")


def update_request_counter() -> int:
    global request_counter

    # Assignment to a module-level variable requires global.
    request_counter += 1
    return request_counter


def demonstrate_global_mutable_object() -> None:
    # Mutating a global dictionary does not require global.
    # Rebinding the dictionary name would require global.
    inventory_totals["products"] += 1
    print(f"Inventory totals: {inventory_totals}")


inventory_totals = {"products": 120, "warehouses": 4}


def calculate_order_value(
    unit_price: float,
    quantity: int,
    tax_rate: float = 0.18,
) -> float:
    """Calculate an order value using local intermediate variables."""
    if unit_price < 0:
        raise ValueError("Unit price cannot be negative.")
    if quantity < 0:
        raise ValueError("Quantity cannot be negative.")
    if not 0 <= tax_rate <= 1:
        raise ValueError("Tax rate must be between zero and one.")

    subtotal = unit_price * quantity
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount
    return round(total, 2)


def demonstrate_unbound_local_error() -> None:
    stock = 50
    try:
        # Python treats stock as local because it is assigned below.
        # Reading it before assignment raises UnboundLocalError.
        def incorrect_update() -> int:
            stock = stock + 10
            return stock

        incorrect_update()
    except UnboundLocalError as error:
        print(f"Expected scope error: {error}")


def demonstrate_closure() -> Callable[[int], int]:
    # remaining_stock belongs to the enclosing function, not the
    # nested function. nonlocal permits rebinding that enclosing name.
    remaining_stock = 100

    def reserve(quantity: int) -> int:
        nonlocal remaining_stock
        if quantity <= 0:
            raise ValueError("Reservation quantity must be positive.")
        if quantity > remaining_stock:
            raise ValueError("Insufficient stock.")

        remaining_stock -= quantity
        return remaining_stock

    return reserve


def make_price_adjuster(rate: float) -> Callable[[float], float]:
    if rate < -1:
        raise ValueError("Rate cannot reduce a price below zero.")

    # The returned function retains access to the enclosing rate.
    def adjust(price: float) -> float:
        if price < 0:
            raise ValueError("Price cannot be negative.")
        return round(price * (1 + rate), 2)

    return adjust


@dataclass
class Warehouse:
    name: str
    capacity: int
    stock: int = 0

    def receive(self, quantity: int) -> None:
        # These names resolve to instance attributes through self.
        if quantity <= 0:
            raise ValueError("Received quantity must be positive.")
        if self.stock + quantity > self.capacity:
            raise ValueError("Warehouse capacity exceeded.")
        self.stock += quantity

    def dispatch(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Dispatch quantity must be positive.")
        if quantity > self.stock:
            raise ValueError("Insufficient warehouse stock.")
        self.stock -= quantity


def demonstrate_comprehension_scope() -> None:
    product_ids = [101, 102, 103]

    # Comprehension variables do not leak into the surrounding scope
    # in Python 3.
    doubled_ids = [product_id * 2 for product_id in product_ids]
    print(f"Doubled product IDs: {doubled_ids}")

    try:
        print(product_id)
    except NameError:
        print("Comprehension variable is not available outside the comprehension.")


def demonstrate_scope_inspection() -> None:
    local_example = "function-local value"

    # locals() exposes the current local namespace for inspection.
    print(f"Selected local names: {locals()}")
    print(f"Global application name: {globals()['APPLICATION_NAME']}")
    print(f"Module name: {__name__}")

    # locals() and globals() are useful for diagnostics, but dynamic
    # namespace mutation should not be used as ordinary program design.


def demonstrate_default_argument_scope() -> None:
    # Default expressions are evaluated when the function is defined,
    # not each time it is called.
    def record_event(event: str, events: list[str] | None = None) -> list[str]:
        if events is None:
            events = []
        events.append(event)
        return events

    first = record_event("stock received")
    second = record_event("order dispatched")
    print(f"Independent event lists: {first} | {second}")


def main() -> None:
    print(f"=== {APPLICATION_NAME}: Variable Scope ===")

    demonstrate_basic_scope()
    demonstrate_local_shadowing()

    print(f"Request count: {update_request_counter()}")
    print(f"Request count: {update_request_counter()}")

    demonstrate_global_mutable_object()

    print(f"Order total: ₹{calculate_order_value(1250.0, 3):.2f}")

    demonstrate_unbound_local_error()

    reserve_stock = demonstrate_closure()
    print(f"Stock after reservation: {reserve_stock(25)}")
    print(f"Stock after reservation: {reserve_stock(15)}")

    apply_markup = make_price_adjuster(0.10)
    print(f"Price after markup: ₹{apply_markup(500):.2f}")

    warehouse = Warehouse("Lucknow", capacity=200)
    warehouse.receive(80)
    warehouse.dispatch(20)
    print(f"Remaining warehouse stock: {warehouse.stock}")

    demonstrate_comprehension_scope()
    demonstrate_scope_inspection()
    demonstrate_default_argument_scope()


if __name__ == "__main__":
    main()
