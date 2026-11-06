from __future__ import annotations

import csv
import hashlib
import json
import logging
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, TypeVar


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("file_practice")

T = TypeVar("T")


class FileOperationError(Exception):
    """Base exception for file workflow failures."""


class ValidationError(FileOperationError):
    """Raised when input data violates application rules."""


class FileNotFoundErrorCustom(FileOperationError):
    """Raised when an expected file does not exist."""


class FileFormatError(FileOperationError):
    """Raised when a file contains invalid structured data."""


class StorageError(FileOperationError):
    """Raised when a storage operation fails."""


class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    task_id: int
    title: str
    priority: int
    status: TaskStatus
    created_at: str

    def validate(self) -> None:
        if self.task_id <= 0:
            raise ValidationError("Task ID must be positive.")

        if not self.title.strip():
            raise ValidationError("Task title cannot be empty.")

        if not 1 <= self.priority <= 5:
            raise ValidationError("Priority must be between 1 and 5.")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        try:
            task = cls(
                task_id=int(data["task_id"]),
                title=str(data["title"]),
                priority=int(data["priority"]),
                status=TaskStatus(data["status"]),
                created_at=str(data["created_at"]),
            )
            task.validate()
            return task
        except (KeyError, TypeError, ValueError) as exc:
            raise FileFormatError(
                f"Invalid task record: {exc}"
            ) from exc


class TaskRepository:
    """Persistent JSON repository with atomic file replacement."""

    def __init__(self, directory: Path):
        self.directory = directory.resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.file_path = self.directory / "tasks.json"

    def _serialize(self, tasks: list[Task]) -> str:
        return json.dumps(
            [asdict(task) for task in tasks],
            indent=2,
            ensure_ascii=False,
        )

    def save(self, tasks: list[Task]) -> None:
        for task in tasks:
            task.validate()

        temporary_path: Path | None = None

        try:
            content = self._serialize(tasks)

            # Write to a temporary file before replacing the destination.
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.directory,
                delete=False,
                suffix=".tmp",
            ) as temporary:
                temporary.write(content)
                temporary.flush()
                os.fsync(temporary.fileno())
                temporary_path = Path(temporary.name)

            os.replace(temporary_path, self.file_path)

        except OSError as exc:
            if temporary_path and temporary_path.exists():
                temporary_path.unlink(missing_ok=True)
            raise StorageError(
                f"Could not save tasks: {exc}"
            ) from exc

    def load(self) -> list[Task]:
        if not self.file_path.exists():
            return []

        try:
            with self.file_path.open(
                "r", encoding="utf-8"
            ) as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise FileFormatError(
                    "The JSON root must be a list."
                )

            tasks = [Task.from_dict(item) for item in data]

            identifiers = [task.task_id for task in tasks]
            if len(identifiers) != len(set(identifiers)):
                raise FileFormatError(
                    "Duplicate task IDs detected."
                )

            return tasks

        except json.JSONDecodeError as exc:
            raise FileFormatError(
                f"Invalid JSON at line {exc.lineno}: {exc.msg}"
            ) from exc
        except OSError as exc:
            raise StorageError(
                f"Could not read tasks: {exc}"
            ) from exc

    def add(self, task: Task) -> None:
        task.validate()
        tasks = self.load()

        if any(existing.task_id == task.task_id for existing in tasks):
            raise ValidationError(
                f"Task ID {task.task_id} already exists."
            )

        tasks.append(task)
        self.save(tasks)

    def update_status(
        self,
        task_id: int,
        status: TaskStatus
    ) -> Task:
        tasks = self.load()

        for task in tasks:
            if task.task_id == task_id:
                task.status = status
                self.save(tasks)
                return task

        raise ValidationError(
            f"Task ID {task_id} was not found."
        )

    def delete(self, task_id: int) -> bool:
        tasks = self.load()
        updated = [
            task for task in tasks
            if task.task_id != task_id
        ]

        if len(updated) == len(tasks):
            return False

        self.save(updated)
        return True


def read_text_file(path: Path) -> str:
    """Read UTF-8 text with explicit error handling."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError as exc:
        raise FileNotFoundErrorCustom(
            f"File does not exist: {path}"
        ) from exc
    except UnicodeDecodeError as exc:
        raise FileFormatError(
            f"File is not valid UTF-8: {path}"
        ) from exc
    except OSError as exc:
        raise StorageError(
            f"Could not read {path}: {exc}"
        ) from exc


def write_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with path.open("w", encoding="utf-8") as file:
            file.write(content)
    except OSError as exc:
        raise StorageError(
            f"Could not write {path}: {exc}"
        ) from exc


def calculate_file_hash(path: Path) -> str:
    """Calculate SHA-256 incrementally to avoid loading large files."""
    digest = hashlib.sha256()

    try:
        with path.open("rb") as file:
            while chunk := file.read(65536):
                digest.update(chunk)
    except OSError as exc:
        raise StorageError(
            f"Could not hash {path}: {exc}"
        ) from exc

    return digest.hexdigest()


def read_csv_records(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(
            "r", encoding="utf-8", newline=""
        ) as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames:
                raise FileFormatError("CSV header is missing.")

            required = {"task_id", "title", "priority"}
            if not required.issubset(reader.fieldnames):
                raise FileFormatError(
                    f"Missing CSV columns: {required - set(reader.fieldnames)}"
                )

            return list(reader)

    except csv.Error as exc:
        raise FileFormatError(
            f"CSV parsing failed: {exc}"
        ) from exc
    except OSError as exc:
        raise StorageError(
            f"CSV read failed: {exc}"
        ) from exc


def process_records(
    records: list[dict[str, Any]],
    processor: Callable[[dict[str, Any]], T],
) -> tuple[list[T], list[str]]:
    successful: list[T] = []
    errors: list[str] = []

    for index, record in enumerate(records, start=1):
        try:
            successful.append(processor(record))
        except (ValueError, TypeError, ValidationError) as exc:
            errors.append(f"Record {index}: {exc}")

    return successful, errors


def create_task(
    task_id: int,
    title: str,
    priority: int
) -> Task:
    task = Task(
        task_id=task_id,
        title=title,
        priority=priority,
        status=TaskStatus.PENDING,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    task.validate()
    return task


def run_tests(repository: TaskRepository) -> None:
    task = create_task(100, "Prepare quarterly report", 2)
    repository.add(task)

    loaded = repository.load()
    assert len(loaded) == 1
    assert loaded[0].title == "Prepare quarterly report"

    updated = repository.update_status(
        100, TaskStatus.COMPLETED
    )
    assert updated.status == TaskStatus.COMPLETED

    assert repository.delete(100)
    assert repository.load() == []

    try:
        create_task(101, "", 3)
        raise AssertionError("Empty title should fail.")
    except ValidationError:
        pass

    try:
        TaskRepository(repository.directory / "missing").load()
        # A missing repository file represents an empty repository.
    except FileOperationError as exc:
        raise AssertionError(str(exc)) from exc

    logger.info("All tests passed.")


def main() -> None:
    with tempfile.TemporaryDirectory(
        prefix="file_exception_practice_"
    ) as temporary_directory:

        root = Path(temporary_directory)
        repository = TaskRepository(root / "data")

        print("FILES AND EXCEPTIONS PRACTICE")
        print("=" * 40)

        tasks = [
            create_task(1, "Validate customer records", 1),
            create_task(2, "Generate monthly report", 3),
            create_task(3, "Archive completed requests", 5),
        ]

        for task in tasks:
            repository.add(task)

        repository.update_status(
            1, TaskStatus.COMPLETED
        )

        for task in repository.load():
            print(
                f"{task.task_id}: {task.title} | "
                f"Priority={task.priority} | "
                f"Status={task.status.value}"
            )

        report_path = root / "reports" / "report.txt"
        report_content = (
            "Task Processing Report\n"
            f"Generated: {datetime.now(timezone.utc).isoformat()}\n"
            f"Total tasks: {len(repository.load())}\n"
        )

        write_text_file(report_path, report_content)

        print("\nReport:")
        print(read_text_file(report_path))

        print(
            "SHA-256:",
            calculate_file_hash(report_path)
        )

        csv_path = root / "input.csv"
        write_text_file(
            csv_path,
            "task_id,title,priority\n"
            "10,Review security logs,2\n"
            "11,Backup database,1\n"
            "invalid,Missing identifier,3\n"
        )

        records = read_csv_records(csv_path)

        def convert_record(record: dict[str, str]) -> Task:
            return create_task(
                int(record["task_id"]),
                record["title"],
                int(record["priority"]),
            )

        valid_tasks, errors = process_records(
            records, convert_record
        )

        print("\nValid CSV records:", len(valid_tasks))
        for error in errors:
            print("Rejected:", error)

        run_tests(repository)


if __name__ == "__main__":
    try:
        main()
    except FileOperationError as exc:
        logger.error("Application error: %s", exc)
        raise SystemExit(1)
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
        raise SystemExit(130)
