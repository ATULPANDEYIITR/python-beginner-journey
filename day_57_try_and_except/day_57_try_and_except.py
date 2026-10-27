from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json
import logging
import tempfile
from typing import Any


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)


class OperationStatus(Enum):
    SUCCESS = "success"
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    STORAGE_ERROR = "storage_error"


class RepositoryError(Exception):
    """Base exception for repository workflow failures."""


class ValidationError(RepositoryError):
    """Raised when input violates a domain rule."""


class RepositoryNotFoundError(RepositoryError):
    """Raised when a requested repository cannot be found."""


class StorageError(RepositoryError):
    """Raised when persistent storage fails."""


@dataclass(frozen=True)
class OperationResult:
    status: OperationStatus
    message: str
    data: Any = None


@dataclass
class Repository:
    name: str
    owner: str
    protected: bool = False
    open_pull_requests: int = 0


class RepositoryStore:
    """Small JSON-backed store demonstrating targeted exception handling."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def _read(self) -> dict[str, Any]:
        try:
            text = self.path.read_text(encoding="utf-8")
            if not text.strip():
                return {}
            data = json.loads(text)
            if not isinstance(data, dict):
                raise StorageError("Repository store must contain a JSON object.")
            return data
        except FileNotFoundError:
            return {}
        except PermissionError as exc:
            raise StorageError("Repository store cannot be read.") from exc
        except json.JSONDecodeError as exc:
            raise StorageError(f"Repository store contains invalid JSON: {exc}") from exc
        except OSError as exc:
            raise StorageError(f"Unexpected storage error: {exc}") from exc

    def _write(self, data: dict[str, Any]) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(data, indent=2),
                encoding="utf-8",
            )
        except PermissionError as exc:
            raise StorageError("Repository store cannot be written.") from exc
        except OSError as exc:
            raise StorageError(f"Unexpected storage error: {exc}") from exc

    def save(self, repository: Repository) -> None:
        if not repository.name.strip():
            raise ValidationError("Repository name cannot be empty.")
        if not repository.owner.strip():
            raise ValidationError("Repository owner cannot be empty.")
        if repository.open_pull_requests < 0:
            raise ValidationError("Open Pull Requests cannot be negative.")

        data = self._read()
        data[repository.name] = {
            "owner": repository.owner,
            "protected": repository.protected,
            "open_pull_requests": repository.open_pull_requests,
        }
        self._write(data)

    def get(self, name: str) -> Repository:
        if not name.strip():
            raise ValidationError("Repository name cannot be empty.")

        data = self._read()

        try:
            record = data[name]
        except KeyError as exc:
            raise RepositoryNotFoundError(
                f"Repository '{name}' was not found."
            ) from exc

        try:
            return Repository(
                name=name,
                owner=str(record["owner"]),
                protected=bool(record["protected"]),
                open_pull_requests=int(record["open_pull_requests"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise StorageError(
                f"Repository '{name}' contains an invalid record."
            ) from exc


def divide_review_work(items: int, reviewers: int) -> float:
    """Demonstrates explicit validation before an operation that can fail."""
    if not isinstance(items, int) or not isinstance(reviewers, int):
        raise TypeError("items and reviewers must be integers.")
    if items < 0:
        raise ValueError("items cannot be negative.")
    if reviewers <= 0:
        raise ValueError("reviewers must be greater than zero.")

    return items / reviewers


def parse_review_payload(payload: str) -> dict[str, Any]:
    """Parse external data while preserving the original failure context."""
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValidationError("Review payload is not valid JSON.") from exc

    if not isinstance(data, dict):
        raise ValidationError("Review payload must be a JSON object.")

    required = {"reviewer", "decision"}
    missing = required - data.keys()
    if missing:
        raise ValidationError(
            f"Review payload is missing fields: {', '.join(sorted(missing))}."
        )

    return data


def evaluate_pull_request(
    *,
    source_branch: str,
    target_branch: str,
    approvals: int,
    required_approvals: int,
    checks_passed: bool,
    conversations_resolved: bool,
) -> OperationResult:
    try:
        if not source_branch.strip() or not target_branch.strip():
            raise ValidationError("Source and target branches are required.")

        if source_branch == target_branch:
            raise ValidationError("Source and target branches must differ.")

        if approvals < 0 or required_approvals < 0:
            raise ValidationError("Approval counts cannot be negative.")

        if approvals < required_approvals:
            return OperationResult(
                OperationStatus.VALIDATION_ERROR,
                "Required approvals have not been satisfied.",
            )

        if not checks_passed:
            return OperationResult(
                OperationStatus.VALIDATION_ERROR,
                "Required status checks have not passed.",
            )

        if not conversations_resolved:
            return OperationResult(
                OperationStatus.VALIDATION_ERROR,
                "All review conversations must be resolved.",
            )

        return OperationResult(
            OperationStatus.SUCCESS,
            "Pull Request is eligible for merge.",
        )

    except ValidationError as exc:
        logging.warning("Validation failure: %s", exc)
        return OperationResult(OperationStatus.VALIDATION_ERROR, str(exc))


def demonstrate_exception_chaining() -> None:
    try:
        int("not-a-number")
    except ValueError as exc:
        try:
            raise ValidationError("External numeric input was invalid.") from exc
        except ValidationError as chained:
            logging.info(
                "Exception chaining preserved the original cause: %s",
                chained.__cause__,
            )


def run_demo() -> None:
    with tempfile.TemporaryDirectory() as directory:
        store = RepositoryStore(Path(directory) / "repositories.json")

        repository = Repository(
            name="secure-platform",
            owner="engineering",
            protected=True,
            open_pull_requests=3,
        )

        try:
            store.save(repository)
            print("Repository saved.")
        except (ValidationError, StorageError) as exc:
            print(f"Save failed: {exc}")

        try:
            loaded = store.get("secure-platform")
            print(f"Loaded repository: {loaded.name}")
        except RepositoryError as exc:
            print(f"Repository lookup failed: {exc}")

        try:
            store.get("missing-repository")
        except RepositoryNotFoundError as exc:
            print(f"Expected lookup failure: {exc}")
        except RepositoryError as exc:
            print(f"Unexpected repository failure: {exc}")

        for reviewers in (2, 0, -1):
            try:
                result = divide_review_work(10, reviewers)
                print(f"Review workload: {result}")
            except (TypeError, ValueError) as exc:
                print(f"Workload failure for {reviewers} reviewers: {exc}")

        payloads = [
            '{"reviewer": "alice", "decision": "approved"}',
            '{"reviewer": "bob"}',
            '{"reviewer": "carol", "decision": ',
        ]

        for payload in payloads:
            try:
                review = parse_review_payload(payload)
                print(f"Accepted review: {review}")
            except ValidationError as exc:
                print(f"Review rejected: {exc}")

        result = evaluate_pull_request(
            source_branch="feature/retry-handling",
            target_branch="main",
            approvals=2,
            required_approvals=2,
            checks_passed=True,
            conversations_resolved=True,
        )
        print(result.message)

        result = evaluate_pull_request(
            source_branch="feature/broken-check",
            target_branch="main",
            approvals=2,
            required_approvals=2,
            checks_passed=False,
            conversations_resolved=True,
        )
        print(result.message)

        demonstrate_exception_chaining()


if __name__ == "__main__":
    run_demo()
