#!/usr/bin/env python3
"""
Creating Your Own Modules
A self-contained module development and management system.

Demonstrates:
- Module design and separation of concerns
- Public and private interfaces
- Module registration and discovery
- Dependency management
- Version compatibility
- Dynamic module loading
- Configuration and validation
- Lifecycle management
- Error isolation
- Testing and execution
"""

from __future__ import annotations

import importlib.util
import logging
import re
import sys
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Protocol


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("module_manager")


class ModuleError(Exception):
    """Base exception for module-related failures."""


class ModuleValidationError(ModuleError):
    pass


class DependencyError(ModuleError):
    pass


class ModuleExecutionError(ModuleError):
    pass


class ModuleState(Enum):
    REGISTERED = "registered"
    LOADED = "loaded"
    ACTIVE = "active"
    FAILED = "failed"
    DISABLED = "disabled"


@dataclass(frozen=True)
class ModuleDependency:
    name: str
    minimum_version: str = "1.0.0"


@dataclass
class ModuleMetadata:
    name: str
    version: str
    description: str
    author: str
    dependencies: tuple[ModuleDependency, ...] = ()
    permissions: frozenset[str] = frozenset()
    enabled: bool = True

    def validate(self) -> None:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", self.name):
            raise ModuleValidationError(
                f"Invalid module name: {self.name}"
            )

        if not re.fullmatch(r"\d+\.\d+\.\d+", self.version):
            raise ModuleValidationError(
                f"Invalid version: {self.version}"
            )

        if not self.description.strip():
            raise ModuleValidationError(
                "Module description cannot be empty."
            )


class ModuleInterface(Protocol):
    def initialize(self, configuration: dict[str, Any]) -> None:
        ...

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        ...

    def shutdown(self) -> None:
        ...


@dataclass
class ModuleRecord:
    metadata: ModuleMetadata
    implementation: ModuleInterface
    state: ModuleState = ModuleState.REGISTERED
    execution_count: int = 0
    last_error: str | None = None


def version_tuple(version: str) -> tuple[int, int, int]:
    try:
        return tuple(map(int, version.split(".")))
    except ValueError as exc:
        raise ModuleValidationError(
            f"Invalid semantic version: {version}"
        ) from exc


class ModuleManager:
    """Manages module registration, dependencies and execution."""

    def __init__(
        self,
        allowed_permissions: set[str] | None = None
    ):
        self._modules: dict[str, ModuleRecord] = {}
        self.allowed_permissions = allowed_permissions or {
            "read_data",
            "write_data",
            "calculate",
            "export_data"
        }

    def register(
        self,
        metadata: ModuleMetadata,
        implementation: ModuleInterface
    ) -> None:
        metadata.validate()

        if metadata.name in self._modules:
            raise ModuleValidationError(
                f"Module already registered: {metadata.name}"
            )

        unauthorized = (
            metadata.permissions - self.allowed_permissions
        )

        if unauthorized:
            raise ModuleValidationError(
                f"Unauthorized permissions: {sorted(unauthorized)}"
            )

        self._modules[metadata.name] = ModuleRecord(
            metadata=metadata,
            implementation=implementation
        )

        logger.info("Registered module: %s", metadata.name)

    def get_module(self, name: str) -> ModuleRecord:
        if name not in self._modules:
            raise ModuleValidationError(
                f"Unknown module: {name}"
            )
        return self._modules[name]

    def validate_dependencies(self, name: str) -> None:
        record = self.get_module(name)

        for dependency in record.metadata.dependencies:
            target = self.get_module(dependency.name)

            if not target.metadata.enabled:
                raise DependencyError(
                    f"Dependency {dependency.name} is disabled."
                )

            if version_tuple(target.metadata.version) < version_tuple(
                dependency.minimum_version
            ):
                raise DependencyError(
                    f"{dependency.name} requires version "
                    f"{dependency.minimum_version}."
                )

    def dependency_order(self, name: str) -> list[str]:
        """Return topological activation order and detect cycles."""

        visited: set[str] = set()
        visiting: set[str] = set()
        order: list[str] = []

        def visit(current: str) -> None:
            if current in visiting:
                raise DependencyError(
                    f"Circular dependency detected at {current}"
                )

            if current in visited:
                return

            visiting.add(current)
            record = self.get_module(current)

            for dependency in record.metadata.dependencies:
                self.get_module(dependency.name)
                visit(dependency.name)

            visiting.remove(current)
            visited.add(current)
            order.append(current)

        visit(name)
        return order

    def load(
        self,
        name: str,
        configuration: dict[str, Any] | None = None
    ) -> None:
        record = self.get_module(name)

        if not record.metadata.enabled:
            raise ModuleError(f"Module {name} is disabled.")

        if record.state == ModuleState.ACTIVE:
            return

        self.validate_dependencies(name)

        try:
            record.implementation.initialize(configuration or {})
            record.state = ModuleState.LOADED
            logger.info("Loaded module: %s", name)
        except Exception as exc:
            record.state = ModuleState.FAILED
            record.last_error = str(exc)
            raise ModuleExecutionError(
                f"Initialization failed for {name}: {exc}"
            ) from exc

    def activate(self, name: str) -> None:
        for dependency_name in self.dependency_order(name):
            dependency = self.get_module(dependency_name)

            if dependency.state == ModuleState.ACTIVE:
                continue

            if dependency.state == ModuleState.REGISTERED:
                self.load(dependency_name)

            if dependency.state != ModuleState.LOADED:
                raise ModuleExecutionError(
                    f"Cannot activate {dependency_name}."
                )

            dependency.state = ModuleState.ACTIVE

        logger.info("Activated module: %s", name)

    def execute(
        self,
        name: str,
        payload: dict[str, Any]
    ) -> dict[str, Any]:
        record = self.get_module(name)

        if record.state != ModuleState.ACTIVE:
            raise ModuleExecutionError(
                f"Module {name} is not active."
            )

        try:
            result = record.implementation.execute(payload)

            if not isinstance(result, dict):
                raise ModuleExecutionError(
                    "Module must return a dictionary."
                )

            record.execution_count += 1
            return result

        except Exception as exc:
            record.last_error = str(exc)
            raise ModuleExecutionError(
                f"Execution failed in {name}: {exc}"
            ) from exc

    def disable(self, name: str) -> None:
        record = self.get_module(name)

        if record.state == ModuleState.ACTIVE:
            record.implementation.shutdown()

        record.state = ModuleState.DISABLED
        logger.info("Disabled module: %s", name)

    def inventory(self) -> list[dict[str, Any]]:
        return [
            {
                "name": record.metadata.name,
                "version": record.metadata.version,
                "state": record.state.value,
                "executions": record.execution_count,
                "dependencies": [
                    dependency.name
                    for dependency in record.metadata.dependencies
                ],
                "last_error": record.last_error
            }
            for record in self._modules.values()
        ]


class CalculationModule:
    """Reusable arithmetic module."""

    def initialize(self, configuration: dict[str, Any]) -> None:
        self.precision = configuration.get("precision", 4)

        if not isinstance(self.precision, int):
            raise ValueError("Precision must be an integer.")

        if not 0 <= self.precision <= 12:
            raise ValueError("Precision must be between 0 and 12.")

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        operation = payload.get("operation")
        values = payload.get("values")

        if not isinstance(values, list) or not values:
            raise ValueError("Provide a non-empty values list.")

        if not all(
            isinstance(value, (int, float)) and
            not isinstance(value, bool)
            for value in values
        ):
            raise ValueError("All values must be numeric.")

        if operation == "sum":
            result = sum(values)
        elif operation == "average":
            result = sum(values) / len(values)
        elif operation == "maximum":
            result = max(values)
        elif operation == "minimum":
            result = min(values)
        else:
            raise ValueError(f"Unsupported operation: {operation}")

        return {
            "operation": operation,
            "result": round(result, self.precision),
            "input_count": len(values)
        }

    def shutdown(self) -> None:
        logger.info("Calculation module shutdown complete.")


class ReportingModule:
    """Reporting module dependent on calculation capabilities."""

    def initialize(self, configuration: dict[str, Any]) -> None:
        self.report_name = configuration.get(
            "report_name",
            "Module Execution Report"
        )

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        if "results" not in payload:
            raise ValueError("Report requires results.")

        results = payload["results"]

        if not isinstance(results, list):
            raise ValueError("Results must be a list.")

        return {
            "report": self.report_name,
            "record_count": len(results),
            "records": results
        }

    def shutdown(self) -> None:
        logger.info("Reporting module shutdown complete.")


def load_external_module(file_path: str, module_name: str):
    """
    Load a Python module from a file.

    Only load trusted, reviewed source files.
    Dynamic imports execute arbitrary Python code.
    """

    path = Path(file_path).resolve()

    if not path.is_file() or path.suffix != ".py":
        raise ModuleValidationError(
            "A valid Python source file is required."
        )

    specification = importlib.util.spec_from_file_location(
        module_name,
        path
    )

    if specification is None or specification.loader is None:
        raise ModuleValidationError(
            "Unable to construct module specification."
        )

    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)

    return module


def run_tests(manager: ModuleManager) -> None:
    assert "calculator" in manager._modules

    result = manager.execute(
        "calculator",
        {
            "operation": "average",
            "values": [10, 20, 30, 40]
        }
    )

    assert result["result"] == 25

    try:
        manager.execute(
            "calculator",
            {
                "operation": "divide",
                "values": [10, 0]
            }
        )
    except ModuleExecutionError:
        pass
    else:
        raise AssertionError("Unsupported operation was accepted.")

    try:
        manager.register(
            ModuleMetadata(
                name="calculator",
                version="1.0.0",
                description="Duplicate module",
                author="Test"
            ),
            CalculationModule()
        )
    except ModuleValidationError:
        pass
    else:
        raise AssertionError("Duplicate registration was accepted.")

    print("All module tests passed.")


def main() -> None:
    manager = ModuleManager()

    calculator_metadata = ModuleMetadata(
        name="calculator",
        version="1.2.0",
        description="Reusable arithmetic functionality",
        author="Engineering Team",
        permissions=frozenset({"calculate"})
    )

    reporting_metadata = ModuleMetadata(
        name="reporting",
        version="1.0.0",
        description="Structured calculation reporting",
        author="Engineering Team",
        dependencies=(
            ModuleDependency("calculator", "1.1.0"),
        ),
        permissions=frozenset({"read_data", "export_data"})
    )

    manager.register(
        calculator_metadata,
        CalculationModule()
    )

    manager.register(
        reporting_metadata,
        ReportingModule()
    )

    manager.activate("reporting")

    calculation = manager.execute(
        "calculator",
        {
            "operation": "average",
            "values": [120, 150, 180, 210]
        }
    )

    report = manager.execute(
        "reporting",
        {"results": [calculation]}
    )

    print("\nCalculation:")
    print(calculation)

    print("\nReport:")
    print(report)

    print("\nModule Inventory:")
    for item in manager.inventory():
        print(item)

    run_tests(manager)

    manager.disable("reporting")
    manager.disable("calculator")


if __name__ == "__main__":
    main()
