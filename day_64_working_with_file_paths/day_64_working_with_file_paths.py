from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath, PureWindowsPath
import os
import shutil
import tempfile


class PathKind(Enum):
    FILE = "file"
    DIRECTORY = "directory"
    MISSING = "missing"


class PathSecurityError(ValueError):
    pass


@dataclass(frozen=True)
class PathInfo:
    original: str
    normalized: Path
    kind: PathKind


class FilePathManager:
    """Demonstrates safe, portable filesystem-path operations."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def safe_path(self, relative: str) -> Path:
        if not relative or "\x00" in relative:
            raise PathSecurityError("Invalid path")

        candidate = (self.root / relative).resolve()

        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise PathSecurityError(
                f"Path escapes managed root: {relative!r}"
            ) from exc

        return candidate

    def create_directory(self, relative: str) -> Path:
        path = self.safe_path(relative)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_text(self, relative: str, content: str) -> Path:
        path = self.safe_path(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def inspect(self, relative: str) -> PathInfo:
        path = self.safe_path(relative)

        if path.is_file():
            kind = PathKind.FILE
        elif path.is_dir():
            kind = PathKind.DIRECTORY
        else:
            kind = PathKind.MISSING

        return PathInfo(relative, path, kind)

    def list_files(self, relative: str = ".") -> list[Path]:
        directory = self.safe_path(relative)

        if not directory.is_dir():
            raise NotADirectoryError(directory)

        return sorted(
            (p for p in directory.rglob("*") if p.is_file()),
            key=lambda p: str(p).lower(),
        )

    def extension_report(self, relative: str = ".") -> dict[str, int]:
        counts: dict[str, int] = {}

        for path in self.list_files(relative):
            suffix = path.suffix.lower() or "[no extension]"
            counts[suffix] = counts.get(suffix, 0) + 1

        return dict(sorted(counts.items()))

    def relative_to_root(self, path: Path) -> Path:
        return path.resolve().relative_to(self.root)

    def copy_file(self, source: str, destination: str) -> Path:
        source_path = self.safe_path(source)
        destination_path = self.safe_path(destination)

        if not source_path.is_file():
            raise FileNotFoundError(source_path)

        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)
        return destination_path


def demonstrate_path_syntax() -> None:
    print("POSIX:", PurePosixPath("/var/data/reports/report.csv"))
    print("Windows:", PureWindowsPath(r"C:\data\reports\report.csv"))

    path = Path("reports") / "2026" / "november" / "report.csv"
    print("Joined:", path)
    print("Name:", path.name)
    print("Stem:", path.stem)
    print("Suffix:", path.suffix)
    print("Parent:", path.parent)

    print("Absolute example:", Path("reports").absolute())
    print("Normalized example:", Path("reports") / ".." / "reports" / "data.csv")


def main() -> None:
    demonstrate_path_syntax()

    with tempfile.TemporaryDirectory(prefix="path_demo_") as temporary:
        manager = FilePathManager(Path(temporary))

        manager.create_directory("reports/2026/november")
        manager.create_directory("archive")

        manager.write_text(
            "reports/2026/november/report.txt",
            "Quarterly operational report\n",
        )
        manager.write_text(
            "reports/2026/november/data.csv",
            "id,value\n1,100\n2,250\n",
        )
        manager.write_text(
            "archive/README",
            "Archived files are retained here.\n",
        )

        print("\nManaged root:", manager.root)

        for name in [
            "reports/2026/november/report.txt",
            "reports/2026/november",
            "missing.txt",
        ]:
            info = manager.inspect(name)
            print(
                f"{info.original}: "
                f"{info.kind.value}, normalized={info.normalized}"
            )

        print("\nFiles:")
        for file_path in manager.list_files():
            print(" ", manager.relative_to_root(file_path))

        print("\nExtensions:", manager.extension_report())

        copied = manager.copy_file(
            "reports/2026/november/report.txt",
            "archive/report.txt",
        )
        print("Copied:", manager.relative_to_root(copied))

        try:
            manager.safe_path("../../outside.txt")
        except PathSecurityError as exc:
            print("Blocked traversal:", exc)

        try:
            manager.safe_path("reports/\x00bad")
        except PathSecurityError as exc:
            print("Blocked invalid path:", exc)

        assert manager.inspect("archive/report.txt").kind is PathKind.FILE
        assert manager.inspect("missing.txt").kind is PathKind.MISSING
        assert manager.extension_report()[".csv"] == 1

        print("\nPath workflow completed successfully.")


if __name__ == "__main__":
    main()
