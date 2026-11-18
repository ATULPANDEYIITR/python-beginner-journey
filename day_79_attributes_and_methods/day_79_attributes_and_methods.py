#!/usr/bin/env python3
"""
ATTRIBUTES AND METHODS
Demonstrates object-oriented programming through a secure banking model.

Concepts:
- Instance attributes
- Class attributes
- Public and private attributes
- Instance methods
- Class methods
- Static methods
- Properties and validation
- Encapsulation
- Inheritance
- Method overriding
- Polymorphism
- Composition
- Special methods
- Exceptions
- Unit-style assertions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import ClassVar
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# 1. ENUMERATIONS
# ---------------------------------------------------------

class AccountStatus(Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"


# ---------------------------------------------------------
# 2. CUSTOM EXCEPTIONS
# ---------------------------------------------------------

class AccountError(Exception):
    """Base exception for account operations."""


class InvalidAmountError(AccountError):
    """Raised when an invalid monetary amount is supplied."""


class InsufficientFundsError(AccountError):
    """Raised when an account lacks sufficient funds."""


class AccountUnavailableError(AccountError):
    """Raised when an account cannot perform transactions."""


# ---------------------------------------------------------
# 3. VALUE OBJECT
# ---------------------------------------------------------

@dataclass(frozen=True)
class Transaction:
    transaction_id: int
    transaction_type: str
    amount: Decimal
    balance_after: Decimal


# ---------------------------------------------------------
# 4. BASE CLASS
# ---------------------------------------------------------

class BankAccount:
    """
    Demonstrates different attribute and method categories.

    Instance attributes:
        account_number
        owner
        balance
        status

    Class attributes:
        bank_name
        minimum_balance
        account_count

    Private attributes:
        __transaction_history

    Instance methods:
        deposit()
        withdraw()
        transfer_to()

    Class methods:
        change_bank_name()
        create_account()

    Static methods:
        validate_amount()
        format_currency()
    """

    bank_name: ClassVar[str] = "National Digital Bank"
    minimum_balance: ClassVar[Decimal] = Decimal("0.00")
    account_count: ClassVar[int] = 0

    def __init__(
        self,
        account_number: str,
        owner: str,
        initial_balance: Decimal | str | int = "0.00"
    ):
        if not account_number or not account_number.strip():
            raise ValueError("Account number cannot be empty.")

        if not owner or not owner.strip():
            raise ValueError("Account owner cannot be empty.")

        self.account_number = account_number.strip()
        self.owner = owner.strip()

        self.__balance = self._to_decimal(initial_balance)
        self._validate_amount(self.__balance)

        self._status = AccountStatus.ACTIVE
        self.__transaction_history: list[Transaction] = []
        self.__transaction_sequence = 0

        BankAccount.account_count += 1

    # -----------------------------------------------------
    # ATTRIBUTE ACCESS
    # -----------------------------------------------------

    @property
    def balance(self) -> Decimal:
        """Read-only access to the account balance."""
        return self.__balance

    @property
    def status(self) -> AccountStatus:
        return self._status

    @property
    def transaction_history(self) -> tuple[Transaction, ...]:
        """Return an immutable snapshot of transaction history."""
        return tuple(self.__transaction_history)

    # -----------------------------------------------------
    # INTERNAL METHODS
    # -----------------------------------------------------

    @staticmethod
    def _to_decimal(value: Decimal | str | int) -> Decimal:
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise InvalidAmountError("Amount must be numeric.")

        if not amount.is_finite():
            raise InvalidAmountError("Amount must be finite.")

        if amount != amount.quantize(Decimal("0.01")):
            raise InvalidAmountError("Amounts support two decimal places.")

        return amount

    def _record_transaction(
        self,
        transaction_type: str,
        amount: Decimal
    ) -> None:
        self.__transaction_sequence += 1

        transaction = Transaction(
            transaction_id=self.__transaction_sequence,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=self.__balance
        )

        self.__transaction_history.append(transaction)

    def _ensure_active(self) -> None:
        if self._status != AccountStatus.ACTIVE:
            raise AccountUnavailableError(
                f"Account is {self._status.value}."
            )

    # -----------------------------------------------------
    # STATIC METHODS
    # -----------------------------------------------------

    @staticmethod
    def _validate_amount(amount: Decimal) -> None:
        if amount <= Decimal("0.00"):
            raise InvalidAmountError("Amount must be positive.")

    @staticmethod
    def format_currency(amount: Decimal) -> str:
        return f"INR {amount:,.2f}"

    # -----------------------------------------------------
    # INSTANCE METHODS
    # -----------------------------------------------------

    def deposit(self, amount: Decimal | str | int) -> Decimal:
        self._ensure_active()

        amount = self._to_decimal(amount)
        self._validate_amount(amount)

        self.__balance += amount
        self._record_transaction("DEPOSIT", amount)

        return self.__balance

    def withdraw(self, amount: Decimal | str | int) -> Decimal:
        self._ensure_active()

        amount = self._to_decimal(amount)
        self._validate_amount(amount)

        if self.__balance - amount < self.minimum_balance:
            raise InsufficientFundsError("Insufficient account balance.")

        self.__balance -= amount
        self._record_transaction("WITHDRAWAL", amount)

        return self.__balance

    def transfer_to(
        self,
        destination: BankAccount,
        amount: Decimal | str | int
    ) -> None:
        self._ensure_active()

        if not isinstance(destination, BankAccount):
            raise TypeError("Destination must be a BankAccount.")

        if destination is self:
            raise ValueError("Self-transfer is not permitted.")

        destination._ensure_active()

        amount = self._to_decimal(amount)
        self._validate_amount(amount)

        if self.__balance < amount:
            raise InsufficientFundsError("Insufficient funds.")

        # Validate both accounts before changing either balance.
        source_balance = self.__balance
        destination_balance = destination.__balance

        try:
            self.__balance -= amount
            destination.__balance += amount

            self._record_transaction("TRANSFER_OUT", amount)
            destination._record_transaction("TRANSFER_IN", amount)

        except Exception:
            self.__balance = source_balance
            destination.__balance = destination_balance
            raise

    def freeze(self) -> None:
        if self._status == AccountStatus.CLOSED:
            raise AccountUnavailableError("Closed accounts cannot be frozen.")

        self._status = AccountStatus.FROZEN

    def unfreeze(self) -> None:
        if self._status != AccountStatus.FROZEN:
            raise AccountUnavailableError("Account is not frozen.")

        self._status = AccountStatus.ACTIVE

    def close(self) -> None:
        if self.__balance != Decimal("0.00"):
            raise AccountError("Account must have zero balance before closure.")

        self._status = AccountStatus.CLOSED

    # -----------------------------------------------------
    # CLASS METHODS
    # -----------------------------------------------------

    @classmethod
    def change_bank_name(cls, new_name: str) -> None:
        if not new_name or not new_name.strip():
            raise ValueError("Bank name cannot be empty.")

        cls.bank_name = new_name.strip()

    @classmethod
    def create_account(
        cls,
        account_number: str,
        owner: str,
        initial_balance: Decimal | str | int = "0.00"
    ) -> BankAccount:
        return cls(account_number, owner, initial_balance)

    # -----------------------------------------------------
    # SPECIAL METHODS
    # -----------------------------------------------------

    def __str__(self) -> str:
        return (
            f"{self.owner} | {self.account_number} | "
            f"{self.format_currency(self.balance)} | "
            f"{self.status.value}"
        )

    def __repr__(self) -> str:
        return (
            f"BankAccount(account_number={self.account_number!r}, "
            f"owner={self.owner!r})"
        )


# ---------------------------------------------------------
# 5. INHERITANCE AND METHOD OVERRIDING
# ---------------------------------------------------------

class SavingsAccount(BankAccount):
    """Savings account with an interest-rate attribute."""

    def __init__(
        self,
        account_number: str,
        owner: str,
        initial_balance: Decimal | str | int = "0.00",
        interest_rate: Decimal | str = "4.00"
    ):
        super().__init__(account_number, owner, initial_balance)

        self.interest_rate = self._to_decimal(interest_rate)

        if self.interest_rate < 0 or self.interest_rate > 100:
            raise ValueError("Interest rate must be between 0 and 100.")

    def calculate_interest(self) -> Decimal:
        return (
            self.balance * self.interest_rate / Decimal("100")
        ).quantize(Decimal("0.01"))

    def apply_interest(self) -> Decimal:
        interest = self.calculate_interest()

        if interest > 0:
            self.deposit(interest)

        return interest

    def __str__(self) -> str:
        return (
            f"SavingsAccount({super().__str__()}, "
            f"Interest={self.interest_rate}%)"
        )


# ---------------------------------------------------------
# 6. POLYMORPHISM
# ---------------------------------------------------------

def display_account(account: BankAccount) -> None:
    """Accepts different account subclasses."""
    print(account)


# ---------------------------------------------------------
# 7. EXECUTION AND TESTING
# ---------------------------------------------------------

def main() -> None:
    print("\nATTRIBUTES AND METHODS DEMONSTRATION")
    print("=" * 55)

    account = BankAccount.create_account(
        "ACC1001",
        "Rahul Sharma",
        "50000.00"
    )

    savings = SavingsAccount(
        "ACC1002",
        "Priya Verma",
        "75000.00",
        "5.00"
    )

    print("\nInstance attributes:")
    print("Account number:", account.account_number)
    print("Owner:", account.owner)
    print("Balance:", account.balance)

    print("\nClass attributes:")
    print("Bank:", BankAccount.bank_name)
    print("Accounts created:", BankAccount.account_count)

    print("\nInstance methods:")
    account.deposit("5000.00")
    account.withdraw("2000.00")
    print("Updated balance:", account.balance)

    print("\nStatic methods:")
    print(BankAccount.format_currency(account.balance))

    print("\nClass methods:")
    BankAccount.change_bank_name("Enterprise Banking Group")
    print("Updated bank:", BankAccount.bank_name)

    print("\nInheritance and overriding:")
    display_account(account)
    display_account(savings)

    print("\nPolymorphism and specialized methods:")
    interest = savings.apply_interest()
    print("Interest applied:", interest)
    print("Savings balance:", savings.balance)

    print("\nAccount transfer:")
    account.transfer_to(savings, "3000.00")
    print("Source balance:", account.balance)
    print("Destination balance:", savings.balance)

    print("\nTransaction history:")
    for transaction in account.transaction_history:
        print(transaction)

    print("\nValidation and exception handling:")

    try:
        account.withdraw("1000000.00")
    except InsufficientFundsError as error:
        logger.warning("%s", error)

    try:
        account.deposit("-500.00")
    except InvalidAmountError as error:
        logger.warning("%s", error)

    try:
        account.balance = Decimal("100000.00")
    except AttributeError:
        print("Direct balance modification is prohibited.")

    print("\nState management:")
    account.freeze()

    try:
        account.deposit("100.00")
    except AccountUnavailableError as error:
        logger.warning("%s", error)

    account.unfreeze()

    # Automated correctness checks.
    assert account.balance == Decimal("50000.00")
    assert savings.balance == Decimal("81125.00")
    assert account.status == AccountStatus.ACTIVE
    assert len(account.transaction_history) == 3

    print("\nAll assertions passed.")
    print("Demonstration completed successfully.")


if __name__ == "__main__":
    main()
