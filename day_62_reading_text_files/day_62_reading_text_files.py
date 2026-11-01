from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from collections import Counter
from typing import Iterable
import hashlib
import re
import tempfile


class TextFileError(Exception):
    """Base exception for text-file processing errors."""


class TextFileValidationError(TextFileError):
    """Raised when input configuration or content is invalid."""


class TextFileReadError(TextFileError):
    """Raised when a text file cannot be read safely."""


@dataclass(frozen=True)
class TextFileStats:
    path: Path
    characters: int
    lines: int
    words: int
    non_empty_lines: int
    unique_words: int
    sha256: str


@dataclass(frozen=True)
class SearchResult:
    line_number: int
    line: str


class TextFileReader:
    """
    Reads text files using explicit encoding, bounded file-size checks,
    streaming iteration, and deterministic statistics.
    """

    WORD_PATTERN = re.compile(r"\b[\w'-]+\b", re.UNICODE)

    def __init__(
        self,
        encoding: str = "utf-8",
        max_file_size: int = 5 * 1024 * 1024,
    ) -> None:
        if not encoding.strip():
            raise TextFileValidationError("Encoding cannot be empty.")
        if max_file_size <= 0:
            raise TextFileValidationError("max_file_size must be positive.")

        self.encoding = encoding
        self.max_file_size = max_file_size

    def validate_path(self, path: Path) -> None:
        if not path.exists():
            raise TextFileReadError(f"File does not exist: {path}")
        if not path.is_file():
            raise TextFileReadError(f"Path is not a regular file: {path}")

        size = path.stat().st_size
        if size > self.max_file_size:
            raise TextFileReadError(
                f"File is {size} bytes; configured limit is "
                f"{self.max_file_size} bytes."
            )

    def iter_lines(self, path: Path) -> Iterable[str]:
        self.validate_path(path)

        try:
            with path.open(
                "r",
                encoding=self.encoding,
                errors="strict",
                newline="",
            ) as file:
                yield from file
        except UnicodeError as exc:
            raise TextFileReadError(
                f"Unable to decode {path} using {self.encoding}."
            ) from exc
        except OSError as exc:
            raise TextFileReadError(f"Unable to read {path}: {exc}") from exc

    def read_text(self, path: Path) -> str:
        return "".join(self.iter_lines(path))

    def search(self, path: Path, term: str) -> list[SearchResult]:
        if not term:
            raise TextFileValidationError("Search term cannot be empty.")

        results: list[SearchResult] = []

        for line_number, line in enumerate(self.iter_lines(path), start=1):
            if term.casefold() in line.casefold():
                results.append(
                    SearchResult(
                        line_number=line_number,
                        line=line.rstrip("\r\n"),
                    )
                )

        return results

    def statistics(self, path: Path) -> TextFileStats:
        self.validate_path(path)

        characters = 0
        lines = 0
        non_empty_lines = 0
        words = 0
        frequencies: Counter[str] = Counter()

        digest = hashlib.sha256()

        for line in self.iter_lines(path):
            encoded = line.encode(self.encoding)
            digest.update(encoded)

            lines += 1
            characters += len(line)

            if line.strip():
                non_empty_lines += 1

            tokens = self.WORD_PATTERN.findall(line.casefold())
            words += len(tokens)
            frequencies.update(tokens)

        return TextFileStats(
            path=path,
            characters=characters,
            lines=lines,
            words=words,
            non_empty_lines=non_empty_lines,
            unique_words=len(frequencies),
            sha256=digest.hexdigest(),
        )

    def top_words(self, path: Path, limit: int = 10) -> list[tuple[str, int]]:
        if limit <= 0:
            raise TextFileValidationError("limit must be positive.")

        frequencies: Counter[str] = Counter()

        for line in self.iter_lines(path):
            frequencies.update(
                token.lower()
                for token in self.WORD_PATTERN.findall(line)
            )

        return frequencies.most_common(limit)


def create_demo_file() -> Path:
    temporary = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".txt",
        delete=False,
    )

    with temporary:
        temporary.write(
            "Reading text files requires explicit encoding.\n"
            "Streaming reads reduce memory usage.\n"
            "Validation prevents unsafe input.\n"
            "Streaming reads are useful for large files.\n"
        )

    return Path(temporary.name)


def main() -> None:
    reader = TextFileReader()

    demo_path = create_demo_file()

    try:
        print("=== Complete Text ===")
        print(reader.read_text(demo_path))

        print("=== Matching Lines ===")
        for result in reader.search(demo_path, "streaming"):
            print(f"{result.line_number}: {result.line}")

        print("\n=== Statistics ===")
        stats = reader.statistics(demo_path)
        print(f"File: {stats.path}")
        print(f"Characters: {stats.characters}")
        print(f"Lines: {stats.lines}")
        print(f"Non-empty lines: {stats.non_empty_lines}")
        print(f"Words: {stats.words}")
        print(f"Unique words: {stats.unique_words}")
        print(f"SHA-256: {stats.sha256}")

        print("\n=== Top Words ===")
        for word, count in reader.top_words(demo_path, 5):
            print(f"{word}: {count}")

        assert stats.lines == 4
        assert stats.non_empty_lines == 4
        assert len(reader.search(demo_path, "STREAMING")) == 2
        assert reader.top_words(demo_path, 1)[0][0] == "streaming"

        print("\nValidation checks passed.")

    finally:
        demo_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
