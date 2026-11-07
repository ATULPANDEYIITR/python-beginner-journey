"""
Introduction to Python Modules
Demonstrates imports, module discovery, packages, namespaces,
module caching, dynamic imports, reusable utilities and plugin loading.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import math
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Callable


# ---------------------------------------------------------
# 1. Built-in modules
# ---------------------------------------------------------

def demonstrate_builtin_modules() -> None:
    print("\n1. BUILT-IN AND STANDARD-LIBRARY MODULES")

    print("Math square root:", math.sqrt(144))
    print("Math constant:", math.pi)
    print("Python version:", sys.version.split()[0])

    # Modules are cached after their first successful import.
    print("Math module cached:", sys.modules["math"] is math)


# ---------------------------------------------------------
# 2. Creating a reusable module
# ---------------------------------------------------------

class CalculationModule:
    """A class representing reusable module functionality."""

    @staticmethod
    def add(a: float, b: float) -> float:
        return a + b

    @staticmethod
    def multiply(a: float, b: float) -> float:
        return a * b

    @staticmethod
    def divide(a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Division by zero is not allowed")
        return a / b


def demonstrate_custom_module() -> None:
    print("\n2. CUSTOM MODULE FUNCTIONALITY")

    calculator = CalculationModule()

    print("Addition:", calculator.add(20, 10))
    print("Multiplication:", calculator.multiply(5, 6))
    print("Division:", calculator.divide(100, 4))

    try:
        calculator.divide(10, 0)
    except ZeroDivisionError as error:
        print("Handled error:", error)


# ---------------------------------------------------------
# 3. Module metadata and namespaces
# ---------------------------------------------------------

def demonstrate_module_metadata() -> None:
    print("\n3. MODULE METADATA")

    current_module = sys.modules[__name__]

    print("Module name:", current_module.__name__)
    print("Module file:", current_module.__file__)
    print("Module documentation:", current_module.__doc__.strip().splitlines()[0])

    print("Available public methods:")
    for name, member in inspect.getmembers(CalculationModule, inspect.isfunction):
        if not name.startswith("_"):
            print(" ", name)


# ---------------------------------------------------------
# 4. Packages and submodules
# ---------------------------------------------------------

def demonstrate_package_structure() -> None:
    print("\n4. PYTHON PACKAGE AND SUBMODULES")

    with tempfile.TemporaryDirectory() as temporary_directory:
        root = Path(temporary_directory)
        package = root / "analytics_package"

        package.mkdir()

        (package / "__init__.py").write_text(
            '"""Analytics package."""\n'
            'from .statistics import mean, maximum\n'
            '__version__ = "1.0.0"\n',
            encoding="utf-8"
        )

        (package / "statistics.py").write_text(
            """
def mean(values):
    if not values:
        raise ValueError("Values cannot be empty")
    return sum(values) / len(values)

def maximum(values):
    if not values:
        raise ValueError("Values cannot be empty")
    return max(values)
""",
            encoding="utf-8"
        )

        # Temporarily add the package's parent directory to the import path.
        sys.path.insert(0, str(root))

        try:
            importlib.invalidate_caches()

            analytics = importlib.import_module("analytics_package")

            print("Package version:", analytics.__version__)
            print("Mean:", analytics.mean([10, 20, 30, 40]))
            print("Maximum:", analytics.maximum([10, 20, 30, 40]))

            statistics_module = importlib.import_module(
                "analytics_package.statistics"
            )

            print("Submodule:", statistics_module.__name__)

        finally:
            sys.path.remove(str(root))

            for module_name in list(sys.modules):
                if module_name == "analytics_package" or module_name.startswith(
                    "analytics_package."
                ):
                    del sys.modules[module_name]


# ---------------------------------------------------------
# 5. Module discovery and dynamic imports
# ---------------------------------------------------------

def demonstrate_dynamic_imports() -> None:
    print("\n5. DYNAMIC IMPORTS")

    module_names = ["math", "statistics", "decimal"]

    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
            print(
                f"{module_name}: "
                f"loaded successfully, origin={module.__spec__.origin}"
            )
        except ImportError as error:
            print(f"Import failed for {module_name}: {error}")

    spec = importlib.util.find_spec("json")

    if spec is not None:
        print("JSON module location:", spec.origin)


# ---------------------------------------------------------
# 6. Module dependency management
# ---------------------------------------------------------

@dataclass(frozen=True)
class ModuleInfo:
    name: str
    version: str
    dependencies: tuple[str, ...]


class ModuleRegistry:
    """Maintains a validated collection of application modules."""

    def __init__(self) -> None:
        self._modules: dict[str, ModuleInfo] = {}

    def register(self, module: ModuleInfo) -> None:
        if not module.name.isidentifier():
            raise ValueError("Module name must be a valid identifier")

        if module.name in self._modules:
            raise ValueError(f"Module already registered: {module.name}")

        if not module.version:
            raise ValueError("Module version cannot be empty")

        if module.name in module.dependencies:
            raise ValueError("A module cannot depend on itself")

        self._modules[module.name] = module

    def resolve(self, name: str) -> list[str]:
        if name not in self._modules:
            raise KeyError(f"Unknown module: {name}")

        ordered: list[str] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(current: str) -> None:
            if current in visiting:
                raise ValueError(f"Circular dependency detected: {current}")

            if current in visited:
                return

            if current not in self._modules:
                raise KeyError(f"Missing dependency: {current}")

            visiting.add(current)

            for dependency in self._modules[current].dependencies:
                visit(dependency)

            visiting.remove(current)
            visited.add(current)
            ordered.append(current)

        visit(name)
        return ordered

    def list_modules(self) -> list[ModuleInfo]:
        return sorted(self._modules.values(), key=lambda item: item.name)


def demonstrate_module_registry() -> None:
    print("\n6. MODULE DEPENDENCY MANAGEMENT")

    registry = ModuleRegistry()

    registry.register(ModuleInfo("core", "1.0.0", ()))
    registry.register(ModuleInfo("database", "2.0.0", ("core",)))
    registry.register(ModuleInfo("reporting", "1.2.0", ("core", "database")))
    registry.register(ModuleInfo("dashboard", "1.0.0", ("reporting",)))

    print("Installation order:", registry.resolve("dashboard"))

    for module in registry.list_modules():
        print(f"{module.name}: v{module.version}")

    try:
        registry.resolve("unknown")
    except KeyError as error:
        print("Handled dependency error:", error)


# ---------------------------------------------------------
# 7. Safe module-based plugin execution
# ---------------------------------------------------------

@dataclass
class Plugin:
    name: str
    execute: Callable[[dict[str, int]], int]


def demonstrate_plugins() -> None:
    print("\n7. MODULE-BASED PLUGIN SYSTEM")

    plugins: dict[str, Plugin] = {
        "total": Plugin(
            "total",
            lambda data: sum(data.values())
        ),
        "largest": Plugin(
            "largest",
            lambda data: max(data.values()) if data else 0
        ),
    }

    dataset = {"sales": 1200, "services": 800, "support": 500}

    for name, plugin in plugins.items():
        result = plugin.execute(dataset)
        print(f"{name} plugin result:", result)

    try:
        requested_plugin = "unknown"

        if requested_plugin not in plugins:
            raise ValueError("Plugin is not registered")

    except ValueError as error:
        print("Plugin error:", error)


# ---------------------------------------------------------
# 8. Assertions and execution
# ---------------------------------------------------------

def run_tests() -> None:
    print("\n8. MODULE FUNCTIONALITY TESTS")

    assert CalculationModule.add(2, 3) == 5
    assert CalculationModule.multiply(4, 5) == 20
    assert CalculationModule.divide(20, 4) == 5

    registry = ModuleRegistry()
    registry.register(ModuleInfo("base", "1.0", ()))
    registry.register(ModuleInfo("application", "1.0", ("base",)))

    assert registry.resolve("application") == ["base", "application"]

    print("All tests passed.")


def main() -> None:
    demonstrate_builtin_modules()
    demonstrate_custom_module()
    demonstrate_module_metadata()
    demonstrate_package_structure()
    demonstrate_dynamic_imports()
    demonstrate_module_registry()
    demonstrate_plugins()
    run_tests()


if __name__ == "__main__":
    main()
