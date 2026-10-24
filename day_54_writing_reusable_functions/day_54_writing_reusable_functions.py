from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Mapping, Sequence, TypeVar
import json
import logging
import math
import time


T = TypeVar("T")
R = TypeVar("R")


class ValidationError(ValueError):
    """Raised when reusable-function input violates a contract."""


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class FunctionMetrics:
    calls: int
    failures: int
    total_seconds: float

    @property
    def average_seconds(self) -> float:
        return self.total_seconds / self.calls if self.calls else 0.0


@dataclass
class Task:
    name: str
    operation: Callable[[Any], Any]
    input_data: Any
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str | None = None


@dataclass
class FunctionRegistry:
    """Stores named reusable functions and their execution statistics."""

    functions: dict[str, Callable[..., Any]] = field(default_factory=dict)
    _calls: dict[str, int] = field(default_factory=dict)
    _failures: dict[str, int] = field(default_factory=dict)
    _seconds: dict[str, float] = field(default_factory=dict)

    def register(self, name: str, function: Callable[..., Any]) -> None:
        if not name or not name.strip():
            raise ValidationError("Function name cannot be empty.")
        if not callable(function):
            raise TypeError("Registered object must be callable.")
        if name in self.functions:
            raise ValidationError(f"Function already registered: {name}")

        self.functions[name] = function
        self._calls[name] = 0
        self._failures[name] = 0
        self._seconds[name] = 0.0

    def call(self, name: str, *args: Any, **kwargs: Any) -> Any:
        if name not in self.functions:
            raise KeyError(f"Unknown function: {name}")

        started = time.perf_counter()
        self._calls[name] += 1

        try:
            return self.functions[name](*args, **kwargs)
        except Exception:
            self._failures[name] += 1
            raise
        finally:
            self._seconds[name] += time.perf_counter() - started

    def metrics(self, name: str) -> FunctionMetrics:
        if name not in self.functions:
            raise KeyError(f"Unknown function: {name}")

        return FunctionMetrics(
            calls=self._calls[name],
            failures=self._failures[name],
            total_seconds=self._seconds[name],
        )


def validate_non_empty_text(value: str, field_name: str = "value") -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string.")
    normalized = value.strip()
    if not normalized:
        raise ValidationError(f"{field_name} cannot be empty.")
    return normalized


def normalize_tags(tags: Iterable[str]) -> tuple[str, ...]:
    """Normalize, validate, deduplicate, and sort tags."""
    normalized: set[str] = set()

    for tag in tags:
        if not isinstance(tag, str):
            raise ValidationError("Every tag must be a string.")

        cleaned = tag.strip().lower()

        if not cleaned:
            continue

        if len(cleaned) > 40:
            raise ValidationError("A tag cannot exceed 40 characters.")

        normalized.add(cleaned)

    return tuple(sorted(normalized))


def calculate_statistics(values: Sequence[float]) -> dict[str, float]:
    """Return reusable statistical measures without mutating input."""
    if not values:
        raise ValidationError("At least one numeric value is required.")

    if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in values):
        raise ValidationError("All values must be finite numbers.")

    total = sum(values)
    mean = total / len(values)

    variance = sum((value - mean) ** 2 for value in values) / len(values)

    return {
        "count": len(values),
        "minimum": min(values),
        "maximum": max(values),
        "mean": mean,
        "population_stddev": math.sqrt(variance),
    }


def chunked(items: Sequence[T], size: int) -> Iterator[list[T]]:
    """Yield independent batches without changing the source sequence."""
    if size <= 0:
        raise ValidationError("Chunk size must be greater than zero.")

    for start in range(0, len(items), size):
        yield list(items[start:start + size])


def retry(
    attempts: int,
    delay_seconds: float = 0.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """Reusable decorator for bounded retry behavior."""

    if attempts <= 0:
        raise ValidationError("Attempts must be greater than zero.")
    if delay_seconds < 0:
        raise ValidationError("Delay cannot be negative.")

    def decorator(function: Callable[..., R]) -> Callable[..., R]:
        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            last_error: Exception | None = None

            for attempt in range(1, attempts + 1):
                try:
                    return function(*args, **kwargs)
                except exceptions as exc:
                    last_error = exc
                    if attempt < attempts and delay_seconds:
                        time.sleep(delay_seconds)

            assert last_error is not None
            raise last_error

        return wrapper

    return decorator


def safe_json_write(path: Path, payload: Mapping[str, Any]) -> None:
    """Write structured data atomically enough for ordinary application use."""
    if path.suffix.lower() != ".json":
        raise ValidationError("Output path must use the .json extension.")

    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_suffix(".tmp")

    try:
        temporary.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temporary.replace(path)
    except OSError as exc:
        raise OSError(f"Could not write JSON file: {path}") from exc


def build_task_pipeline(tasks: Sequence[Task]) -> list[Task]:
    """Execute independent tasks while preserving task state explicitly."""
    completed: list[Task] = []

    for task in tasks:
        if not validate_non_empty_text(task.name, "task.name"):
            raise ValidationError("Task name is invalid.")

        task.status = TaskStatus.RUNNING

        try:
            task.result = task.operation(task.input_data)
            task.status = TaskStatus.COMPLETED
        except Exception as exc:
            task.status = TaskStatus.FAILED
            task.error = str(exc)

        completed.append(task)

    return completed


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    registry = FunctionRegistry()

    registry.register("normalize_tags", normalize_tags)
    registry.register("statistics", calculate_statistics)
    registry.register("validate_text", validate_non_empty_text)

    tags = registry.call(
        "normalize_tags",
        [" Python ", "functions", "PYTHON", "reuse", "functions"],
    )

    statistics = registry.call(
        "statistics",
        [10, 20, 30, 40, 50],
    )

    text = registry.call(
        "validate_text",
        "Reusable functions reduce duplication.",
        "description",
    )

    print("Normalized tags:", tags)
    print("Statistics:", statistics)
    print("Validated text:", text)

    tasks = [
        Task(
            name="tag-normalization",
            operation=normalize_tags,
            input_data=["API", "api", "database"],
        ),
        Task(
            name="statistics",
            operation=calculate_statistics,
            input_data=[4, 8, 15, 16, 23, 42],
        ),
        Task(
            name="invalid-statistics",
            operation=calculate_statistics,
            input_data=[],
        ),
    ]

    for task in build_task_pipeline(tasks):
        print(
            f"task={task.name!r} status={task.status.value!r} "
            f"result={task.result!r} error={task.error!r}"
        )

    metrics = registry.metrics("statistics")
    print(
        "statistics metrics:",
        {
            "calls": metrics.calls,
            "failures": metrics.failures,
            "total_seconds": round(metrics.total_seconds, 8),
            "average_seconds": round(metrics.average_seconds, 8),
        },
    )

    output = Path("function_report.json")
    safe_json_write(
        output,
        {
            "tags": tags,
            "statistics": statistics,
            "metrics": {
                "calls": metrics.calls,
                "failures": metrics.failures,
                "average_seconds": metrics.average_seconds,
            },
        },
    )

    print(f"Report written to {output.resolve()}")

    assert normalize_tags(["A", "a", " B "]) == ("a", "b")
    assert list(chunked([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
    assert calculate_statistics([10, 20])["mean"] == 15

    try:
        calculate_statistics([])
    except ValidationError:
        print("Validation test passed.")

    try:
        normalize_tags(["x" * 41])
    except ValidationError:
        print("Length validation test passed.")


if __name__ == "__main__":
    main()
