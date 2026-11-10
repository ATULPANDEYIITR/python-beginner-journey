#!/usr/bin/env python3
"""
Python Standard Library: Practical Engineering Toolkit

Demonstrates:
- Data structures and algorithms
- Dataclasses, enums, decorators and generators
- Iterators, context managers and type annotations
- JSON, CSV, pathlib and file handling
- SQLite database operations
- Threading, multiprocessing and asynchronous programming
- HTTP requests using urllib
- Logging, argparse, hashing and security
- Unit testing and performance measurement

Dependencies: Python 3.10+ standard library only.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import logging
import os
import platform
import sqlite3
import statistics
import tempfile
import threading
import time
import unittest
from collections import Counter, defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Callable, Generator, Iterable, Iterator, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(threadName)s %(message)s",
)
logger = logging.getLogger("stdlib_toolkit")


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobPriority(int, Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Job:
    job_id: int
    name: str
    priority: JobPriority = JobPriority.NORMAL
    status: JobStatus = JobStatus.PENDING
    attempts: int = 0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if self.job_id <= 0:
            raise ValueError("Job ID must be positive")
        if not self.name.strip():
            raise ValueError("Job name cannot be empty")
        if self.attempts < 0:
            raise ValueError("Attempts cannot be negative")


def timed(function: Callable) -> Callable:
    """Measure execution time without changing the function result."""

    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            return function(*args, **kwargs)
        finally:
            logger.debug(
                "%s executed in %.6f seconds",
                function.__name__,
                time.perf_counter() - start,
            )

    return wrapper


@contextmanager
def managed_resource(path: Path) -> Generator[Path, None, None]:
    """Create a directory and provide deterministic resource cleanup."""
    path.mkdir(parents=True, exist_ok=True)
    try:
        yield path
    finally:
        logger.debug("Resource scope completed: %s", path)


def validate_email(email: str) -> bool:
    """Basic format validation, not complete mailbox verification."""
    if not isinstance(email, str) or len(email) > 254:
        return False
    local, separator, domain = email.partition("@")
    return bool(
        separator
        and local
        and domain
        and "." in domain
        and not any(char.isspace() for char in email)
    )


def safe_hash(data: bytes) -> str:
    """Calculate a SHA-256 digest."""
    return hashlib.sha256(data).hexdigest()


def chunked(items: Iterable[Any], size: int) -> Iterator[list[Any]]:
    """Yield bounded batches without loading the entire input."""
    if size <= 0:
        raise ValueError("Chunk size must be positive")

    batch = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []

    if batch:
        yield batch


@lru_cache(maxsize=512)
def fibonacci(number: int) -> int:
    """Memoized recursive algorithm."""
    if number < 0:
        raise ValueError("Number cannot be negative")
    if number < 2:
        return number
    return fibonacci(number - 1) + fibonacci(number - 2)


def analyze_text(text: str) -> dict[str, Any]:
    """Analyze text using collections and string operations."""
    words = [
        word.strip(".,!?;:()[]{}\"'").lower()
        for word in text.split()
    ]
    words = [word for word in words if word]

    frequencies = Counter(words)

    return {
        "characters": len(text),
        "words": len(words),
        "unique_words": len(frequencies),
        "top_words": frequencies.most_common(5),
    }


class JobManager:
    """Thread-safe in-memory job management."""

    def __init__(self) -> None:
        self._jobs: dict[int, Job] = {}
        self._lock = threading.RLock()

    def add(self, job: Job) -> None:
        job.validate()
        with self._lock:
            if job.job_id in self._jobs:
                raise ValueError("Duplicate job ID")
            self._jobs[job.job_id] = job

    def transition(self, job_id: int, status: JobStatus) -> Job:
        transitions = {
            JobStatus.PENDING: {JobStatus.RUNNING},
            JobStatus.RUNNING: {
                JobStatus.COMPLETED,
                JobStatus.FAILED,
            },
            JobStatus.FAILED: {JobStatus.PENDING},
            JobStatus.COMPLETED: set(),
        }

        with self._lock:
            job = self._jobs.get(job_id)

            if job is None:
                raise KeyError(f"Unknown job: {job_id}")

            if status not in transitions[job.status]:
                raise ValueError(
                    f"Invalid transition: {job.status} -> {status}"
                )

            job.status = status

            if status == JobStatus.RUNNING:
                job.attempts += 1

            return job

    def list_jobs(self) -> list[Job]:
        with self._lock:
            return sorted(
                self._jobs.values(),
                key=lambda job: (
                    -job.priority.value,
                    job.job_id,
                ),
            )

    def statistics(self) -> dict[str, int]:
        with self._lock:
            return dict(
                Counter(job.status.value for job in self._jobs.values())
            )


class JobDatabase:
    """SQLite persistence using parameterized SQL."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.connection = sqlite3.connect(
            str(database_path),
            timeout=10,
        )
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self._initialize()

    def _initialize(self) -> None:
        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
                    priority INTEGER NOT NULL
                        CHECK(priority BETWEEN 1 AND 4),
                    status TEXT NOT NULL CHECK(
                        status IN (
                            'pending',
                            'running',
                            'completed',
                            'failed'
                        )
                    ),
                    attempts INTEGER NOT NULL DEFAULT 0
                        CHECK(attempts >= 0),
                    created_at TEXT NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}'
                )
            """)

            self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_status_priority
                ON jobs(status, priority DESC)
            """)

    def save(self, job: Job) -> None:
        job.validate()

        with self.connection:
            self.connection.execute(
                """
                INSERT INTO jobs (
                    job_id, name, priority, status,
                    attempts, created_at, metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                    name = excluded.name,
                    priority = excluded.priority,
                    status = excluded.status,
                    attempts = excluded.attempts,
                    metadata = excluded.metadata
                """,
                (
                    job.job_id,
                    job.name,
                    job.priority.value,
                    job.status.value,
                    job.attempts,
                    job.created_at,
                    json.dumps(job.metadata),
                ),
            )

    def get_all(self) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT * FROM jobs
            ORDER BY priority DESC, job_id
            """
        ).fetchall()

        return [
            {
                **dict(row),
                "metadata": json.loads(row["metadata"]),
            }
            for row in rows
        ]

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> JobDatabase:
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()


def export_csv(records: list[dict[str, Any]], path: Path) -> None:
    """Export structured records with explicit CSV field names."""
    if not records:
        return

    fieldnames = list(records[0].keys())

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def import_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def atomic_json_export(data: Any, path: Path) -> None:
    """Write JSON to a temporary file before replacing the destination."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")

    try:
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
            file.flush()
            os.fsync(file.fileno())

        temporary.replace(path)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def calculate_statistics(values: list[float]) -> dict[str, float]:
    if not values:
        raise ValueError("Cannot calculate statistics for empty input")

    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "minimum": min(values),
        "maximum": max(values),
        "standard_deviation": statistics.pstdev(values),
    }


def thread_worker(value: int) -> int:
    """Example of independent I/O-style work."""
    time.sleep(0.01)
    return value * value


def process_worker(value: int) -> int:
    """Top-level function suitable for process serialization."""
    return value * value


async def async_worker(value: int) -> int:
    await asyncio.sleep(0.01)
    return value * value


async def execute_async_batch(values: list[int]) -> list[int]:
    return await asyncio.gather(
        *(async_worker(value) for value in values)
    )


def download_json(
    url: str,
    timeout: float = 5.0,
    max_bytes: int = 1_000_000,
) -> Any:
    """Fetch JSON over HTTPS with bounded response size."""
    if not url.startswith("https://"):
        raise ValueError("Only HTTPS URLs are accepted")

    request = Request(
        url,
        headers={"User-Agent": "PythonStdlibToolkit/1.0"},
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            content = response.read(max_bytes + 1)

            if len(content) > max_bytes:
                raise ValueError("Response exceeds configured size limit")

            return json.loads(content.decode("utf-8"))

    except HTTPError as error:
        logger.error("HTTP failure: %s", error.code)
        raise
    except URLError as error:
        logger.error("Network failure: %s", error.reason)
        raise


def run_tests() -> None:
    class ToolkitTests(unittest.TestCase):
        def test_email(self) -> None:
            self.assertTrue(validate_email("user@example.com"))
            self.assertFalse(validate_email("invalid"))

        def test_fibonacci(self) -> None:
            self.assertEqual(fibonacci(10), 55)

        def test_chunks(self) -> None:
            self.assertEqual(
                list(chunked(range(5), 2)),
                [[0, 1], [2, 3], [4]],
            )

        def test_invalid_chunk(self) -> None:
            with self.assertRaises(ValueError):
                list(chunked([1], 0))

        def test_job_transitions(self) -> None:
            manager = JobManager()
            manager.add(Job(1, "Test job"))
            manager.transition(1, JobStatus.RUNNING)
            manager.transition(1, JobStatus.COMPLETED)

            self.assertEqual(
                manager.list_jobs()[0].status,
                JobStatus.COMPLETED,
            )

        def test_duplicate_job(self) -> None:
            manager = JobManager()
            manager.add(Job(1, "First"))

            with self.assertRaises(ValueError):
                manager.add(Job(1, "Second"))

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        ToolkitTests
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    if not result.wasSuccessful():
        raise SystemExit(1)


def run_demo(output_dir: Path) -> None:
    with managed_resource(output_dir):
        manager = JobManager()

        examples = [
            Job(
                1,
                "Process customer records",
                JobPriority.HIGH,
                metadata={"department": "operations"},
            ),
            Job(
                2,
                "Generate analytics report",
                JobPriority.NORMAL,
            ),
            Job(
                3,
                "Verify security configuration",
                JobPriority.CRITICAL,
            ),
        ]

        for job in examples:
            manager.add(job)

        manager.transition(1, JobStatus.RUNNING)
        manager.transition(1, JobStatus.COMPLETED)

        jobs = manager.list_jobs()

        database_path = output_dir / "jobs.sqlite3"

        with JobDatabase(database_path) as database:
            for job in jobs:
                database.save(job)

            records = database.get_all()

        atomic_json_export(records, output_dir / "jobs.json")
        export_csv(records, output_dir / "jobs.csv")

        report = {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "job_statistics": manager.statistics(),
            "text_analysis": analyze_text(
                "Python standard library automation and data processing"
            ),
            "fibonacci_20": fibonacci(20),
            "numeric_statistics": calculate_statistics(
                [10, 20, 30, 40, 50]
            ),
            "sha256": safe_hash(b"standard library"),
        }

        atomic_json_export(report, output_dir / "report.json")

        with ThreadPoolExecutor(max_workers=4) as executor:
            thread_results = list(
                executor.map(thread_worker, range(5))
            )

        with ProcessPoolExecutor(max_workers=2) as executor:
            process_results = list(
                executor.map(process_worker, range(5))
            )

        async_results = asyncio.run(
            execute_async_batch(list(range(5)))
        )

        print("\nJOB STATISTICS")
        print(json.dumps(report, indent=2))

        print("\nCONCURRENT EXECUTION")
        print("Threads:", thread_results)
        print("Processes:", process_results)
        print("Async:", async_results)

        print("\nPERSISTED JOBS")
        print(json.dumps(records, indent=2))

        print("\nOUTPUT DIRECTORY:", output_dir.resolve())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Python Standard Library Engineering Toolkit"
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("stdlib_output"),
        help="Output directory",
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Execute automated tests",
    )

    args = parser.parse_args()

    try:
        if args.test:
            run_tests()
        else:
            run_demo(args.output)

    except (OSError, sqlite3.Error, ValueError, KeyError) as error:
        logger.exception("Execution failed: %s", error)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
