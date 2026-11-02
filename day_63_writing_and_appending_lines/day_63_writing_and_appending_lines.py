from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable


class WriteMode(Enum):
    WRITE = "write"
    APPEND = "append"


class FileOperationError(Exception):
    """Raised when a file operation cannot be completed safely."""


@dataclass
class WriteResult:
    path: Path
    mode: WriteMode
    bytes_written: int
    line_count: int


@dataclass
class FileManager:
    base_directory: Path
    encoding: str = "utf-8"
    max_file_size: int = 5 * 1024 * 1024
    audit_log: list[dict[str, object]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.base_directory = self.base_directory.resolve()
        self.base_directory.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, filename: str) -> Path:
        if not filename or filename.strip() in {".", ".."}:
            raise FileOperationError("A valid filename is required.")

        candidate = (self.base_directory / filename).resolve()

        try:
            candidate.relative_to(self.base_directory)
        except ValueError as exc:
            raise FileOperationError("Path escapes the configured directory.") from exc

        if candidate.is_dir():
            raise FileOperationError("The target path is a directory.")

        return candidate

    def _validate_content(self, content: str) -> None:
        if not isinstance(content, str):
            raise TypeError("Content must be a string.")

        encoded_size = len(content.encode(self.encoding))
        if encoded_size > self.max_file_size:
            raise FileOperationError(
                f"Content exceeds the {self.max_file_size} byte limit."
            )

    def write(self, filename: str, content: str) -> WriteResult:
        return self._save(filename, content, WriteMode.WRITE)

    def append(self, filename: str, content: str) -> WriteResult:
        return self._save(filename, content, WriteMode.APPEND)

    def _save(self, filename: str, content: str, mode: WriteMode) -> WriteResult:
        self._validate_content(content)
        path = self._safe_path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)

        if mode is WriteMode.WRITE:
            file_mode = "w"
        else:
            file_mode = "a"

        try:
            with path.open(file_mode, encoding=self.encoding, newline="") as handle:
                handle.write(content)
        except OSError as exc:
            raise FileOperationError(f"Unable to write {path.name}: {exc}") from exc

        bytes_written = len(content.encode(self.encoding))
        line_count = content.count("\n") + (1 if content and not content.endswith("\n") else 0)

        self.audit_log.append(
            {
                "operation": mode.value,
                "filename": str(path.relative_to(self.base_directory)),
                "bytes": bytes_written,
                "lines": line_count,
            }
        )

        return WriteResult(path, mode, bytes_written, line_count)

    def read(self, filename: str) -> str:
        path = self._safe_path(filename)

        if not path.exists():
            raise FileOperationError(f"File does not exist: {filename}")

        try:
            return path.read_text(encoding=self.encoding)
        except OSError as exc:
            raise FileOperationError(f"Unable to read {filename}: {exc}") from exc

    def append_lines(self, filename: str, lines: Iterable[str]) -> WriteResult:
        normalized: list[str] = []

        for line in lines:
            if not isinstance(line, str):
                raise TypeError("Every line must be a string.")
            normalized.append(line.rstrip("\r\n") + "\n")

        return self.append(filename, "".join(normalized))

    def file_size(self, filename: str) -> int:
        path = self._safe_path(filename)

        if not path.exists():
            raise FileOperationError(f"File does not exist: {filename}")

        return path.stat().st_size


def demonstrate() -> None:
    with TemporaryDirectory() as temporary_directory:
        manager = FileManager(Path(temporary_directory))

        initial = manager.write(
            "logs/application.log",
            "Application started\n",
        )

        manager.append(
            "logs/application.log",
            "Configuration loaded\n",
        )

        manager.append_lines(
            "logs/application.log",
            [
                "Database connection established",
                "Worker process started",
                "Application ready",
            ],
        )

        content = manager.read("logs/application.log")

        assert content == (
            "Application started\n"
            "Configuration loaded\n"
            "Database connection established\n"
            "Worker process started\n"
            "Application ready\n"
        )

        assert initial.mode is WriteMode.WRITE
        assert manager.file_size("logs/application.log") == len(
            content.encode("utf-8")
        )

        try:
            manager.append("../outside.txt", "blocked\n")
        except FileOperationError:
            pass
        else:
            raise AssertionError("Path traversal should have been rejected.")

        try:
            manager.read("missing.txt")
        except FileOperationError:
            pass
        else:
            raise AssertionError("Missing-file access should have failed.")

        print("File content:")
        print(content)
        print("Audit records:")
        for record in manager.audit_log:
            print(record)


if __name__ == "__main__":
    demonstrate()
