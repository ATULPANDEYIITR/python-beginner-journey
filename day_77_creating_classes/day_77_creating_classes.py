from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar
import json
import math
from pathlib import Path


class ValidationError(ValueError):
    """Raised when an object receives invalid data."""


class AccountStatus(Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"


@dataclass(frozen=True)
class Transaction:
    transaction_id: int
    transaction_type: str
    amount: float
    balance_after: float


class Account(ABC):
    """
    Abstract base class demonstrating encapsulation,
    inheritance, polymorphism, class variables and methods.
    """

    _next_id: ClassVar[int] = 1000
    account_count: ClassVar[int] = 0

    def __init__(self, owner: str, opening_balance: float = 0.0):
        if not isinstance(owner, str) or not owner.strip():
            raise ValidationError("Owner name cannot be empty.")

        if isinstance(opening_balance, bool) or not isinstance(
            opening_balance, (int, float)
        ):
            raise ValidationError("Balance must be numeric.")

        if not math.isfinite(opening_balance) or opening_balance < 0:
            raise ValidationError("Opening balance must be finite and non-negative.")

        self._account_id = Account._next_id
        Account._next_id += 1
        Account.account_count += 1

        self._owner = owner.strip()
        self._balance = float(opening_balance)
        self._status = AccountStatus.ACTIVE
        self._transactions: list[Transaction] = []
        self._transaction_sequence = 0

    @property
    def account_id(self) -> int:
        return self._account_id

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def status(self) -> AccountStatus:
        return self._status

    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return tuple(self._transactions)

    @staticmethod
    def validate_amount(amount: float) -> float:
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise ValidationError("Amount must be numeric.")

        amount = float(amount)

        if not math.isfinite(amount) or amount <= 0:
            raise ValidationError("Amount must be finite and positive.")

        return round(amount, 2)

    @classmethod
    def total_accounts(cls) -> int:
        return Account.account_count

    def _ensure_active(self) -> None:
        if self._status != AccountStatus.ACTIVE:
            raise RuntimeError(
                f"Account is {self._status.value}; transaction rejected."
            )

    def _record(self, transaction_type: str, amount: float) -> None:
        self._transaction_sequence += 1
        self._transactions.append(
            Transaction(
                transaction_id=self._transaction_sequence,
                transaction_type=transaction_type,
                amount=amount,
                balance_after=round(self._balance, 2),
            )
        )

    def deposit(self, amount: float) -> float:
        self._ensure_active()
        amount = self.validate_amount(amount)
        self._balance = round(self._balance + amount, 2)
        self._record("deposit", amount)
        return self._balance

    def withdraw(self, amount: float) -> float:
        self._ensure_active()
        amount = self.validate_amount(amount)

        if amount > self.available_balance():
            raise ValueError("Insufficient available balance.")

        self._balance = round(self._balance - amount, 2)
        self._record("withdrawal", amount)
        return self._balance

    @abstractmethod
    def available_balance(self) -> float:
        """Calculate the amount currently available for withdrawal."""

    def freeze(self) -> None:
        self._ensure_active()
        self._status = AccountStatus.FROZEN

    def unfreeze(self) -> None:
        if self._status != AccountStatus.FROZEN:
            raise RuntimeError("Only frozen accounts can be unfrozen.")
        self._status = AccountStatus.ACTIVE

    def close(self) -> None:
        if self._status == AccountStatus.CLOSED:
            raise RuntimeError("Account is already closed.")
        if self._balance != 0:
            raise RuntimeError("Account must have zero balance before closing.")
        self._status = AccountStatus.CLOSED

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self.account_id}, owner={self.owner}, "
            f"balance={self.balance:.2f}, status={self.status.value})"
        )

    def __repr__(self) -> str:
        return str(self)


class SavingsAccount(Account):
    def __init__(
        self,
        owner: str,
        opening_balance: float = 0.0,
        minimum_balance: float = 1000.0,
        interest_rate: float = 0.04,
    ):
        super().__init__(owner, opening_balance)

        if minimum_balance < 0 or not math.isfinite(minimum_balance):
            raise ValidationError("Invalid minimum balance.")

        if not 0 <= interest_rate <= 1 or not math.isfinite(interest_rate):
            raise ValidationError("Interest rate must be between 0 and 1.")

        self.minimum_balance = float(minimum_balance)
        self.interest_rate = float(interest_rate)

    def available_balance(self) -> float:
        return max(0.0, self.balance - self.minimum_balance)

    def apply_interest(self) -> float:
        self._ensure_active()
        interest = round(self.balance * self.interest_rate, 2)

        if interest > 0:
            self._balance = round(self.balance + interest, 2)
            self._record("interest", interest)

        return interest


class CurrentAccount(Account):
    def __init__(
        self,
        owner: str,
        opening_balance: float = 0.0,
        overdraft_limit: float = 5000.0,
    ):
        super().__init__(owner, opening_balance)

        if overdraft_limit < 0 or not math.isfinite(overdraft_limit):
            raise ValidationError("Invalid overdraft limit.")

        self.overdraft_limit = float(overdraft_limit)

    def available_balance(self) -> float:
        return self.balance + self.overdraft_limit


@dataclass
class Bank:
    name: str
    accounts: dict[int, Account] = field(default_factory=dict)

    def add_account(self, account: Account) -> None:
        if account.account_id in self.accounts:
            raise ValueError("Duplicate account.")

        self.accounts[account.account_id] = account

    def find_account(self, account_id: int) -> Account:
        try:
            return self.accounts[account_id]
        except KeyError:
            raise KeyError(f"Account {account_id} not found.") from None

    def total_balance(self) -> float:
        return round(sum(a.balance for a in self.accounts.values()), 2)

    def report(self) -> list[dict]:
        return [
            {
                "account_id": account.account_id,
                "owner": account.owner,
                "type": type(account).__name__,
                "balance": account.balance,
                "status": account.status.value,
            }
            for account in self.accounts.values()
        ]

    def save_report(self, filename: str = "bank_report.json") -> None:
        # Resolve the output path and avoid writing outside the current directory.
        base = Path.cwd().resolve()
        destination = (base / filename).resolve()

        if destination.parent != base:
            raise ValueError("Report path must be inside the current directory.")

        destination.write_text(
            json.dumps(self.report(), indent=2),
            encoding="utf-8",
        )


def demonstrate_classes() -> None:
    bank = Bank("National Development Bank")

    savings = SavingsAccount(
        owner="Aarav Sharma",
        opening_balance=25000,
        minimum_balance=1000,
        interest_rate=0.05,
    )

    current = CurrentAccount(
        owner="Meera Verma",
        opening_balance=10000,
        overdraft_limit=5000,
    )

    bank.add_account(savings)
    bank.add_account(current)

    savings.deposit(5000)
    savings.withdraw(3000)
    savings.apply_interest()

    current.withdraw(12000)
    current.deposit(2000)

    # Polymorphism: both subclasses implement available_balance().
    for account in bank.accounts.values():
        print(account)
        print(f"Available: {account.available_balance():.2f}")

    print("\nBank report:")
    print(json.dumps(bank.report(), indent=2))

    print(f"\nTotal accounts: {Account.total_accounts()}")
    print(f"Total deposits: {bank.total_balance():.2f}")

    # Verify encapsulated state and business rules.
    assert savings.balance == 28350.0
    assert current.balance == 0.0
    assert len(savings.transactions) == 3

    try:
        savings.withdraw(100000)
    except ValueError as error:
        print(f"Expected validation error: {error}")

    try:
        savings.deposit(-100)
    except ValidationError as error:
        print(f"Expected validation error: {error}")

    current.freeze()

    try:
        current.deposit(500)
    except RuntimeError as error:
        print(f"Expected state error: {error}")

    current.unfreeze()
    current.close()

    assert current.status == AccountStatus.CLOSED

    print("\nAll class demonstrations passed.")


if __name__ == "__main__":
    demonstrate_classes()
