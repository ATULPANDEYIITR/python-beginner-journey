"""
IMPORTING MODULES IN PYTHON
Demonstrates standard-library imports, aliases, selective imports,
packages, relative-import concepts, dynamic imports, module inspection,
caching, import errors, and safe module loading.

Compatible with Python 3.10+.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
import logging
import math
import os
import sys
import tempfile
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


# ---------------------------------------------------------
# 1. Logging configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger("module_importing")


# ---------------------------------------------------------
# 2. Fundamental import mechanisms
# ---------------------------------------------------------

# Importing an entire module.
import statistics

# Importing with an alias.
import datetime as dt

# Importing specific members.
from collections import Counter, defaultdict

# Importing multiple standard-library modules.
import os.path
import platform


def demonstrate_basic_imports() -> None:
    numbers = [10, 20, 30, 40, 50]

    print("\n1. BASIC IMPORTS")

    print("Square root:", math.sqrt(144))
    print("Mean:", statistics.mean(numbers))
    print("Date:", dt.date.today())
    print("Counter:", Counter(["Python", "Java", "Python"]))

    print("Operating system:", os.name)
    print("Platform:", platform.system())

    grouped: defaultdict[str, list[int]] = defaultdict(list)

    for number in numbers:
        grouped["even"].append(number)

    print("Grouped values:", dict(grouped))


# ---------------------------------------------------------
# 3. Module identity and namespace inspection
# ---------------------------------------------------------

def demonstrate_module_metadata() -> None:
    print("\n2. MODULE METADATA")

    print("Module name:", math.__name__)
    print("Module documentation:", math.__doc__[:60])
    print("Module file:", statistics.__file__)
    print("Python version:", sys.version.split()[0])

    print("Module members:", len(dir(math)))

    print("Available functions:", [
        name for name in dir(math)
        if not name.startswith("_")
    ][:10])


# ---------------------------------------------------------
# 4. Import caching
# ---------------------------------------------------------

def demonstrate_import_cache() -> None:
    print("\n3. IMPORT CACHE")

    first = importlib.import_module("json")
    second = importlib.import_module("json")

    print("Same module object:", first is second)
    print("Module cached:", "json" in sys.modules)

    # sys.modules prevents repeated module initialization.
    print("Cached module count:", len(sys.modules))


# ---------------------------------------------------------
# 5. Dynamic importing
# ---------------------------------------------------------

def dynamic_import(
    module_name: str,
    allowed_modules: set[str]
) -> types.ModuleType:

    if module_name not in allowed_modules:
        raise PermissionError(
            f"Module is not authorized: {module_name}"
        )

    try:
        return importlib.import_module(module_name)
    except ImportError as exc:
        logger.exception("Dynamic import failed")
        raise RuntimeError(
            f"Unable to import {module_name}"
        ) from exc


def demonstrate_dynamic_import() -> None:
    print("\n4. DYNAMIC IMPORT")

    allowed = {
        "json",
        "decimal",
        "fractions"
    }

    module = dynamic_import("decimal", allowed)

    result = module.Decimal("10.25") * module.Decimal("2")

    print("Loaded module:", module.__name__)
    print("Calculation:", result)

    try:
        dynamic_import("subprocess", allowed)
    except PermissionError as exc:
        print("Security restriction:", exc)


# ---------------------------------------------------------
# 6. Loading a module from a file
# ---------------------------------------------------------

def load_module_from_file(
    module_name: str,
    file_path: Path
) -> types.ModuleType:

    if not file_path.is_file():
        raise FileNotFoundError(file_path)

    if file_path.suffix != ".py":
        raise ValueError("Only Python files are accepted")

    resolved = file_path.resolve()

    spec = importlib.util.spec_from_file_location(
        module_name,
        resolved
    )

    if spec is None or spec.loader is None:
        raise ImportError("Unable to create module specification")

    module = importlib.util.module_from_spec(spec)

    # Register before execution to support module identity
    # and references during initialization.
    sys.modules[module_name] = module

    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise

    return module


def demonstrate_file_import() -> None:
    print("\n5. IMPORT FROM FILE")

    with tempfile.TemporaryDirectory() as directory:
        module_path = Path(directory) / "calculator_module.py"

        module_path.write_text(
            "def multiply(a, b):\n"
            "    return a * b\n"
            "\n"
            "CONSTANT = 100\n",
            encoding="utf-8"
        )

        module = load_module_from_file(
            "temporary_calculator",
            module_path
        )

        print("Module:", module.__name__)
        print("Multiplication:", module.multiply(12, 5))
        print("Constant:", module.CONSTANT)

        sys.modules.pop(module.__name__, None)


# ---------------------------------------------------------
# 7. Package structure and import concepts
# ---------------------------------------------------------

@dataclass
class PackageInfo:
    name: str
    modules: list[str]
    dependencies: list[str]


def demonstrate_package_structure() -> None:
    print("\n6. PACKAGE STRUCTURE")

    package = PackageInfo(
        name="analytics",
        modules=[
            "analytics.statistics",
            "analytics.reporting",
            "analytics.validation"
        ],
        dependencies=["math", "json", "statistics"]
    )

    print("Package:", package.name)
    print("Modules:", package.modules)
    print("Dependencies:", package.dependencies)

    print(
        "Absolute import example:",
        "from analytics.statistics import calculate_mean"
    )

    print(
        "Relative import example:",
        "from .statistics import calculate_mean"
    )

    print(
        "Parent-relative import example:",
        "from ..common import configuration"
    )


# ---------------------------------------------------------
# 8. Module dependency management
# ---------------------------------------------------------

@dataclass
class ModuleDefinition:
    name: str
    dependencies: list[str]
    initializer: Callable[[], Any]


class ModuleRegistry:

    def __init__(self) -> None:
        self.modules: dict[str, ModuleDefinition] = {}
        self.loaded: dict[str, Any] = {}
        self.loading: set[str] = set()

    def register(self, definition: ModuleDefinition) -> None:
        if definition.name in self.modules:
            raise ValueError(
                f"Duplicate module: {definition.name}"
            )

        self.modules[definition.name] = definition

    def load(self, name: str) -> Any:

        if name in self.loaded:
            return self.loaded[name]

        if name in self.loading:
            raise RuntimeError(
                f"Circular dependency detected: {name}"
            )

        if name not in self.modules:
            raise ModuleNotFoundError(name)

        definition = self.modules[name]

        self.loading.add(name)

        try:
            dependencies = {
                dependency: self.load(dependency)
                for dependency in definition.dependencies
            }

            result = definition.initializer()

            self.loaded[name] = {
                "instance": result,
                "dependencies": dependencies
            }

            return self.loaded[name]

        finally:
            self.loading.remove(name)


def demonstrate_registry() -> None:
    print("\n7. MODULE DEPENDENCIES")

    registry = ModuleRegistry()

    registry.register(
        ModuleDefinition(
            "configuration",
            [],
            lambda: {"environment": "development"}
        )
    )

    registry.register(
        ModuleDefinition(
            "database",
            ["configuration"],
            lambda: {"connected": True}
        )
    )

    registry.register(
        ModuleDefinition(
            "application",
            ["configuration", "database"],
            lambda: {"running": True}
        )
    )

    application = registry.load("application")

    print("Application:", application["instance"])
    print("Loaded modules:", list(registry.loaded))


# ---------------------------------------------------------
# 9. Import failure handling
# ---------------------------------------------------------

def demonstrate_import_errors() -> None:
    print("\n8. IMPORT ERRORS")

    try:
        importlib.import_module(
            "nonexistent_application_module"
        )

    except ModuleNotFoundError as exc:
        print("Missing module:", exc.name)

    except ImportError as exc:
        print("Import error:", exc)

    try:
        importlib.import_module("math.nonexistent_member")
    except (ModuleNotFoundError, ImportError) as exc:
        print("Invalid import:", type(exc).__name__)


# ---------------------------------------------------------
# 10. Module integrity verification
# ---------------------------------------------------------

def calculate_file_hash(file_path: Path) -> str:

    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(8192),
            b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


def demonstrate_integrity() -> None:
    print("\n9. MODULE FILE INTEGRITY")

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "trusted_module.py"

        path.write_text(
            "VALUE = 42\n",
            encoding="utf-8"
        )

        print("SHA-256:", calculate_file_hash(path))


# ---------------------------------------------------------
# 11. Assertions and practical validation
# ---------------------------------------------------------

def run_tests() -> None:

    assert math.sqrt(81) == 9
    assert statistics.mean([2, 4, 6]) == 4
    assert Counter(["a", "a", "b"])["a"] == 2

    registry = ModuleRegistry()

    registry.register(
        ModuleDefinition(
            "base",
            [],
            lambda: 10
        )
    )

    registry.register(
        ModuleDefinition(
            "derived",
            ["base"],
            lambda: 20
        )
    )

    assert registry.load("derived")["instance"] == 20
    assert "base" in registry.loaded

    print("\nAll validation tests passed.")


# ---------------------------------------------------------
# 12. Main execution
# ---------------------------------------------------------

def main() -> None:

    demonstrate_basic_imports()
    demonstrate_module_metadata()
    demonstrate_import_cache()
    demonstrate_dynamic_import()
    demonstrate_file_import()
    demonstrate_package_structure()
    demonstrate_registry()
    demonstrate_import_errors()
    demonstrate_integrity()
    run_tests()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Python module importing demonstration"
    )

    parser.parse_args()
    main()
