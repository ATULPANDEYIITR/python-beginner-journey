from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(Enum):
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ApplicationError(Exception):
    """Base exception for application-level failures."""


class ValidationError(ApplicationError):
    """Raised when input violates domain rules."""


class ConfigurationError(ApplicationError):
    """Raised when required configuration is invalid."""


class StorageError(ApplicationError):
    """Raised when persistent storage cannot be used."""


@dataclass(frozen=True)
class User:
    user_id: int
    name: str
    email: str


class UserRepository:
    """Small file-backed repository used to demonstrate exception propagation."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def save(self, user: User) -> None:
        try:
            with self.path.open("a", encoding="utf-8") as file:
                file.write(f"{user.user_id},{user.name},{user.email}\n")
        except OSError as exc:
            raise StorageError(f"Unable to save user to {self.path}") from exc


def validate_user(user_id: Any, name: Any, email: Any) -> User:
    if not isinstance(user_id, int) or isinstance(user_id, bool):
        raise ValidationError("user_id must be an integer")

    if user_id <= 0:
        raise ValidationError("user_id must be greater than zero")

    if not isinstance(name, str) or not name.strip():
        raise ValidationError("name must be a non-empty string")

    if not isinstance(email, str) or "@" not in email:
        raise ValidationError("email must contain '@'")

    return User(user_id, name.strip(), email.strip().lower())


def load_configuration(config: dict[str, Any]) -> str:
    database_url = config.get("database_url")

    if not isinstance(database_url, str) or not database_url.strip():
        raise ConfigurationError("database_url is required")

    return database_url.strip()


def divide(total: float, count: float) -> float:
    if count == 0:
        raise ZeroDivisionError("count cannot be zero")

    return total / count


def parse_integer(value: str) -> int:
    try:
        return int(value.strip())
    except (AttributeError, ValueError) as exc:
        raise ValidationError(f"Invalid integer value: {value!r}") from exc


def process_user(
    repository: UserRepository,
    user_id: Any,
    name: Any,
    email: Any,
) -> User:
    try:
        user = validate_user(user_id, name, email)
        repository.save(user)
        return user
    except ValidationError:
        # Validation failures are already meaningful to the caller.
        raise
    except StorageError:
        # Preserve the original exception chain.
        raise


def demonstrate_exception_chaining() -> None:
    try:
        parse_integer("not-a-number")
    except ValidationError as exc:
        print(f"Chained exception: {exc}")
        print(f"Original cause: {type(exc.__cause__).__name__}")


def demonstrate_cleanup() -> None:
    file_path = Path("temporary_exception_demo.txt")

    try:
        with file_path.open("w", encoding="utf-8") as file:
            file.write("resource acquired\n")
            raise RuntimeError("simulated processing failure")
    except RuntimeError as exc:
        print(f"Cleanup example: {exc}")
    finally:
        file_path.unlink(missing_ok=True)


def run_tests() -> None:
    valid = validate_user(1, "Ada", "ADA@EXAMPLE.COM")
    assert valid.email == "ada@example.com"

    try:
        validate_user(0, "Ada", "ada@example.com")
    except ValidationError:
        pass
    else:
        raise AssertionError("Expected ValidationError")

    try:
        divide(10, 0)
    except ZeroDivisionError:
        pass
    else:
        raise AssertionError("Expected ZeroDivisionError")

    try:
        parse_integer("abc")
    except ValidationError as exc:
        assert isinstance(exc.__cause__, ValueError)
    else:
        raise AssertionError("Expected ValidationError")

    try:
        load_configuration({})
    except ConfigurationError:
        pass
    else:
        raise AssertionError("Expected ConfigurationError")


def main() -> None:
    print("Raising Exceptions Demonstration")

    try:
        configuration = load_configuration(
            {"database_url": "postgresql://localhost/example"}
        )
        print(f"Configuration accepted: {configuration}")
    except ConfigurationError as exc:
        print(f"Configuration failure: {exc}")

    repository = UserRepository(Path("users_demo.csv"))

    try:
        user = process_user(repository, 101, "Grace Hopper", "Grace@Example.com")
        print(f"User stored: {user}")
    except ApplicationError as exc:
        print(f"Application failure: {exc}")

    try:
        process_user(repository, -4, "Invalid User", "invalid@example.com")
    except ValidationError as exc:
        print(f"Expected validation failure: {exc}")

    try:
        divide(25, 0)
    except ZeroDivisionError as exc:
        print(f"Expected arithmetic failure: {exc}")

    demonstrate_exception_chaining()
    demonstrate_cleanup()
    run_tests()

    print("All exception assertions passed.")


if __name__ == "__main__":
    main()
