#!/usr/bin/env python3
"""
INTRODUCTION TO CLASSES AND OBJECTS
Demonstrates encapsulation, abstraction, inheritance, polymorphism,
composition, constructors, class methods, static methods, properties,
object identity, validation, exceptions, serialization, and testing.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import ClassVar


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class AccountStatus(Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"


class AccountError(Exception):
    """Base exception for account-related failures."""


class InsufficientFundsError(AccountError):
    """Raised when a withdrawal exceeds the available balance."""


class InvalidTransactionError(AccountError):
    """Raised when a transaction violates account rules."""


@dataclass(frozen=True)
class Transaction:
    transaction_id: int
    transaction_type: str
    amount: Decimal
    balance_after: Decimal
    timestamp: str

    def to_dict(self) -> dict:
        data = asdict(self)
        data["amount"] = str(self.amount)
        data["balance_after"] = str(self.balance_after)
        return data


class BankAccount:
    """Base class demonstrating encapsulation and object state."""

    _next_account_number: ClassVar[int] = 1001
    _total_accounts: ClassVar[int] = 0

    def __init__(self, owner: str, opening_balance: Decimal = Decimal("0")):
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("Account owner cannot be empty.")

        self.account_number = BankAccount._next_account_number
        BankAccount._next_account_number += 1
        BankAccount._total_accounts += 1

        self.owner = owner.strip()
        self._balance = Decimal("0")
        self._status = AccountStatus.ACTIVE
        self._transactions: list[Transaction] = []
        self._next_transaction_id = 1

        opening_balance = self._validate_amount(opening_balance)

        if opening_balance > 0:
            self.deposit(opening_balance)

    @staticmethod
    def _validate_amount(amount: Decimal) -> Decimal:
        if isinstance(amount, bool):
            raise ValueError("Amount must be numeric.")

        try:
            value = Decimal(str(amount))
        except Exception as exc:
            raise ValueError("Invalid monetary amount.") from exc

        if not value.is_finite() or value <= 0:
            raise ValueError("Amount must be positive and finite.")

        if value != value.quantize(Decimal("0.01")):
            raise ValueError("Maximum precision is two decimal places.")

        return value

    @property
    def balance(self) -> Decimal:
        """Expose balance without allowing unrestricted assignment."""
        return self._balance

    @property
    def status(self) -> AccountStatus:
        return self._status

    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return tuple(self._transactions)

    def _ensure_active(self) -> None:
        if self._status != AccountStatus.ACTIVE:
            raise AccountError(
                f"Account is {self._status.value}."
            )

    def _record_transaction(self, kind: str, amount: Decimal) -> None:
        transaction = Transaction(
            transaction_id=self._next_transaction_id,
            transaction_type=kind,
            amount=amount,
            balance_after=self._balance,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

        self._transactions.append(transaction)
        self._next_transaction_id += 1

        logger.info(
            "Account %s: %s %s; balance=%s",
            self.account_number,
            kind,
            amount,
            self._balance
        )

    def deposit(self, amount: Decimal) -> None:
        self._ensure_active()
        amount = self._validate_amount(amount)

        self._balance += amount
        self._record_transaction("deposit", amount)

    def withdraw(self, amount: Decimal) -> None:
        self._ensure_active()
        amount = self._validate_amount(amount)

        if amount > self._balance:
            raise InsufficientFundsError("Insufficient account balance.")

        self._balance -= amount
        self._record_transaction("withdrawal", amount)

    def freeze(self) -> None:
        self._ensure_active()
        self._status = AccountStatus.FROZEN

    def unfreeze(self) -> None:
        if self._status != AccountStatus.FROZEN:
            raise AccountError("Only frozen accounts can be unfrozen.")

        self._status = AccountStatus.ACTIVE

    def close(self) -> None:
        self._ensure_active()

        if self._balance != Decimal("0"):
            raise AccountError("Account must have zero balance before closure.")

        self._status = AccountStatus.CLOSED

    def calculate_interest(self) -> Decimal:
        """Polymorphic method implemented by specialized accounts."""
        return Decimal("0")

    def to_dict(self) -> dict:
        return {
            "account_number": self.account_number,
            "owner": self.owner,
            "balance": str(self.balance),
            "status": self.status.value,
            "transactions": [
                transaction.to_dict()
                for transaction in self.transactions
            ]
        }

    @classmethod
    def total_accounts(cls) -> int:
        return BankAccount._total_accounts

    def __str__(self) -> str:
        return (
            f"Account({self.account_number}, "
            f"owner={self.owner}, balance={self.balance}, "
            f"status={self.status.value})"
        )


class SavingsAccount(BankAccount):
    """Inheritance and method overriding."""

    def __init__(
        self,
        owner: str,
        opening_balance: Decimal = Decimal("0"),
        interest_rate: Decimal = Decimal("0.04"),
        minimum_balance: Decimal = Decimal("500")
    ):
        super().__init__(owner, opening_balance)

        self.interest_rate = Decimal(str(interest_rate))
        self.minimum_balance = Decimal(str(minimum_balance))

        if (
            not self.interest_rate.is_finite()
            or not Decimal("0") <= self.interest_rate <= Decimal("1")
        ):
            raise ValueError("Interest rate must be between 0 and 1.")

        if (
            not self.minimum_balance.is_finite()
            or self.minimum_balance < 0
        ):
            raise ValueError("Minimum balance cannot be negative.")

    def withdraw(self, amount: Decimal) -> None:
        amount = self._validate_amount(amount)

        if self.balance - amount < self.minimum_balance:
            raise InsufficientFundsError(
                "Withdrawal would violate the minimum balance."
            )

        super().withdraw(amount)

    def calculate_interest(self) -> Decimal:
        return (
            self.balance * self.interest_rate
        ).quantize(Decimal("0.01"))


class CurrentAccount(BankAccount):
    """A different withdrawal policy through polymorphism."""

    def __init__(
        self,
        owner: str,
        opening_balance: Decimal = Decimal("0"),
        overdraft_limit: Decimal = Decimal("1000")
    ):
        super().__init__(owner, opening_balance)

        self.overdraft_limit = Decimal(str(overdraft_limit))

        if (
            not self.overdraft_limit.is_finite()
            or self.overdraft_limit < 0
        ):
            raise ValueError("Overdraft limit cannot be negative.")

    def withdraw(self, amount: Decimal) -> None:
        self._ensure_active()
        amount = self._validate_amount(amount)

        if amount > self.balance + self.overdraft_limit:
            raise InsufficientFundsError("Overdraft limit exceeded.")

        self._balance -= amount
        self._record_transaction("withdrawal", amount)


class Bank:
    """Composition: a bank manages multiple account objects."""

    def __init__(self, name: str):
        if not name.strip():
            raise ValueError("Bank name cannot be empty.")

        self.name = name
        self._accounts: dict[int, BankAccount] = {}

    def add_account(self, account: BankAccount) -> None:
        if not isinstance(account, BankAccount):
            raise TypeError("Expected a BankAccount object.")

        if account.account_number in self._accounts:
            raise AccountError("Account already registered.")

        self._accounts[account.account_number] = account

    def get_account(self, account_number: int) -> BankAccount:
        try:
            return self._accounts[account_number]
        except KeyError as exc:
            raise AccountError("Account not found.") from exc

    def transfer(
        self,
        source_number: int,
        destination_number: int,
        amount: Decimal
    ) -> None:
        source = self.get_account(source_number)
        destination = self.get_account(destination_number)

        if source is destination:
            raise InvalidTransactionError(
                "Source and destination must differ."
            )

        amount = BankAccount._validate_amount(amount)

        # Validate both sides before changing either balance.
        source._ensure_active()
        destination._ensure_active()

        if source.balance - amount < Decimal("0"):
            if not isinstance(source, CurrentAccount):
                raise InsufficientFundsError("Insufficient funds.")

            if source.balance - amount < -source.overdraft_limit:
                raise InsufficientFundsError("Overdraft limit exceeded.")

        if (
            isinstance(destination, SavingsAccount)
            and destination.balance + amount < 0
        ):
            raise InvalidTransactionError("Invalid destination balance.")

        source.withdraw(amount)
        try:
            destination.deposit(amount)
        except Exception:
            # Roll back the source if the destination operation fails.
            source._balance += amount
            source._transactions.pop()
            source._next_transaction_id -= 1
            raise

    def report(self) -> dict:
        return {
            "bank": self.name,
            "account_count": len(self._accounts),
            "total_balance": str(
                sum(
                    (account.balance for account in self._accounts.values()),
                    Decimal("0")
                )
            ),
            "accounts": [
                account.to_dict()
                for account in self._accounts.values()
            ]
        }

    def export_json(self, filename: str) -> None:
        path = Path(filename)

        # Refuse to overwrite an existing file unexpectedly.
        with path.open("x", encoding="utf-8") as file:
            json.dump(self.report(), file, indent=2)


def run_tests() -> None:
    bank = Bank("Central Commercial Bank")

    savings = SavingsAccount(
        "Aarav Sharma",
        Decimal("10000"),
        Decimal("0.05"),
        Decimal("500")
    )

    current = CurrentAccount(
        "Meera Singh",
        Decimal("2000"),
        Decimal("3000")
    )

    bank.add_account(savings)
    bank.add_account(current)

    assert savings.balance == Decimal("10000")
    assert savings.calculate_interest() == Decimal("500.00")

    savings.deposit(Decimal("1000"))
    savings.withdraw(Decimal("500"))

    bank.transfer(
        savings.account_number,
        current.account_number,
        Decimal("1000")
    )

    assert savings.balance == Decimal("9500")
    assert current.balance == Decimal("3000")

    # Demonstrate an enforced savings minimum balance.
    try:
        savings.withdraw(Decimal("9200"))
    except InsufficientFundsError as exc:
        print("Expected failure:", exc)

    # Demonstrate state restrictions.
    current.freeze()

    try:
        current.deposit(Decimal("100"))
    except AccountError as exc:
        print("Expected failure:", exc)

    current.unfreeze()

    # Demonstrate overdraft functionality.
    current.withdraw(Decimal("3500"))
    assert current.balance == Decimal("-500")

    # Demonstrate polymorphism.
    accounts: list[BankAccount] = [savings, current]

    for account in accounts:
        print(account)
        print("Interest:", account.calculate_interest())

    print("\nBank report:")
    print(json.dumps(bank.report(), indent=2))

    assert BankAccount.total_accounts() >= 2

    # Demonstrate invalid input.
    try:
        savings.deposit(Decimal("-100"))
    except ValueError as exc:
        print("Validation failure:", exc)

    print("\nAll assertions passed.")


if __name__ == "__main__":
    run_tests()
