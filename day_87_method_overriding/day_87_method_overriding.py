from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PaymentResult:
    transaction_id: str
    amount: float
    status: PaymentStatus
    message: str


@dataclass
class Payment:
    transaction_id: str
    amount: float

    def __post_init__(self):
        if not self.transaction_id.strip():
            raise ValueError("Transaction ID cannot be empty")
        if self.amount <= 0:
            raise ValueError("Payment amount must be positive")


class PaymentProcessor(ABC):
    """Base class defining a common payment-processing contract."""

    def __init__(self, provider: str):
        self.provider = provider
        self.processed_transactions: set[str] = set()

    @abstractmethod
    def calculate_fee(self, amount: float) -> float:
        pass

    @abstractmethod
    def process_payment(self, payment: Payment) -> PaymentResult:
        pass

    def validate_payment(self, payment: Payment) -> None:
        if payment.amount <= 0:
            raise ValueError("Invalid payment amount")

        if payment.transaction_id in self.processed_transactions:
            raise ValueError("Duplicate transaction")

    def get_transaction_summary(self) -> dict:
        return {
            "provider": self.provider,
            "processed_count": len(self.processed_transactions),
        }


class CreditCardProcessor(PaymentProcessor):
    def calculate_fee(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return round(amount * 0.025 + 0.30, 2)

    def process_payment(self, payment: Payment) -> PaymentResult:
        self.validate_payment(payment)

        fee = self.calculate_fee(payment.amount)
        self.processed_transactions.add(payment.transaction_id)

        return PaymentResult(
            transaction_id=payment.transaction_id,
            amount=payment.amount + fee,
            status=PaymentStatus.COMPLETED,
            message=f"Credit card payment processed. Fee: {fee:.2f}",
        )


class BankTransferProcessor(PaymentProcessor):
    def calculate_fee(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return round(min(amount * 0.005, 15.00), 2)

    def process_payment(self, payment: Payment) -> PaymentResult:
        self.validate_payment(payment)

        fee = self.calculate_fee(payment.amount)
        self.processed_transactions.add(payment.transaction_id)

        return PaymentResult(
            transaction_id=payment.transaction_id,
            amount=payment.amount + fee,
            status=PaymentStatus.COMPLETED,
            message=f"Bank transfer processed. Fee: {fee:.2f}",
        )


class DigitalWalletProcessor(PaymentProcessor):
    def calculate_fee(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return 0.0 if amount >= 1000 else round(amount * 0.01, 2)

    def process_payment(self, payment: Payment) -> PaymentResult:
        self.validate_payment(payment)

        fee = self.calculate_fee(payment.amount)
        self.processed_transactions.add(payment.transaction_id)

        return PaymentResult(
            transaction_id=payment.transaction_id,
            amount=payment.amount + fee,
            status=PaymentStatus.COMPLETED,
            message=f"Digital wallet payment processed. Fee: {fee:.2f}",
        )


class CashbackWalletProcessor(DigitalWalletProcessor):
    """Demonstrates overriding an inherited concrete method."""

    def calculate_fee(self, amount: float) -> float:
        base_fee = super().calculate_fee(amount)
        cashback = min(amount * 0.002, 5.0)
        return round(max(0.0, base_fee - cashback), 2)

    def process_payment(self, payment: Payment) -> PaymentResult:
        result = super().process_payment(payment)
        return PaymentResult(
            transaction_id=result.transaction_id,
            amount=result.amount,
            status=result.status,
            message=result.message + " Cashback policy applied.",
        )


@dataclass
class PaymentGateway:
    processors: dict[str, PaymentProcessor] = field(default_factory=dict)

    def register(self, processor: PaymentProcessor) -> None:
        if processor.provider in self.processors:
            raise ValueError("Provider already registered")
        self.processors[processor.provider] = processor

    def execute(self, provider: str, payment: Payment) -> PaymentResult:
        processor = self.processors.get(provider)

        if processor is None:
            raise LookupError(f"Unknown payment provider: {provider}")

        # Dynamic dispatch selects the overridden implementation.
        return processor.process_payment(payment)


def demonstrate_method_overriding() -> None:
    print("METHOD OVERRIDING AND RUNTIME POLYMORPHISM")
    print("=" * 55)

    gateway = PaymentGateway()

    gateway.register(CreditCardProcessor("credit_card"))
    gateway.register(BankTransferProcessor("bank_transfer"))
    gateway.register(DigitalWalletProcessor("digital_wallet"))
    gateway.register(CashbackWalletProcessor("cashback_wallet"))

    payments = [
        ("credit_card", Payment("TXN-1001", 2500)),
        ("bank_transfer", Payment("TXN-1002", 5000)),
        ("digital_wallet", Payment("TXN-1003", 750)),
        ("cashback_wallet", Payment("TXN-1004", 750)),
    ]

    for provider, payment in payments:
        result = gateway.execute(provider, payment)

        print(f"\nProvider: {provider}")
        print(f"Transaction: {result.transaction_id}")
        print(f"Amount including fee: {result.amount:.2f}")
        print(f"Status: {result.status.value}")
        print(f"Result: {result.message}")

    print("\nPROCESSOR SUMMARIES")

    for provider, processor in gateway.processors.items():
        print(provider, processor.get_transaction_summary())

    print("\nDUPLICATE TRANSACTION TEST")

    try:
        gateway.execute(
            "credit_card",
            Payment("TXN-1001", 100),
        )
    except ValueError as error:
        print(f"Rejected: {error}")

    print("\nUNKNOWN PROVIDER TEST")

    try:
        gateway.execute(
            "unknown",
            Payment("TXN-1005", 100),
        )
    except LookupError as error:
        print(f"Rejected: {error}")


def demonstrate_super() -> None:
    print("\nSUPER() AND INHERITED BEHAVIOR")
    print("=" * 55)

    parent = DigitalWalletProcessor("parent_wallet")
    child = CashbackWalletProcessor("child_wallet")

    amount = 500

    print("Parent fee:", parent.calculate_fee(amount))
    print("Overridden child fee:", child.calculate_fee(amount))


def demonstrate_dynamic_dispatch() -> None:
    print("\nDYNAMIC DISPATCH")
    print("=" * 55)

    processors: list[PaymentProcessor] = [
        CreditCardProcessor("card"),
        BankTransferProcessor("bank"),
        DigitalWalletProcessor("wallet"),
        CashbackWalletProcessor("cashback"),
    ]

    for processor in processors:
        print(
            f"{processor.__class__.__name__}: "
            f"fee={processor.calculate_fee(2000):.2f}"
        )


def run_assertions() -> None:
    card = CreditCardProcessor("test_card")
    bank = BankTransferProcessor("test_bank")
    wallet = DigitalWalletProcessor("test_wallet")
    cashback = CashbackWalletProcessor("test_cashback")

    assert card.calculate_fee(100) == 2.8
    assert bank.calculate_fee(100) == 0.5
    assert wallet.calculate_fee(100) == 1.0
    assert cashback.calculate_fee(100) == 0.8

    assert cashback.calculate_fee(2000) == 0.0

    try:
        card.calculate_fee(-10)
        raise AssertionError("Negative amounts should be rejected")
    except ValueError:
        pass

    payment = Payment("TEST-001", 100)
    first = card.process_payment(payment)

    assert first.status == PaymentStatus.COMPLETED

    try:
        card.process_payment(payment)
        raise AssertionError("Duplicate payment should be rejected")
    except ValueError:
        pass

    print("\nAll assertions passed.")


if __name__ == "__main__":
    demonstrate_method_overriding()
    demonstrate_super()
    demonstrate_dynamic_dispatch()
    run_assertions()
