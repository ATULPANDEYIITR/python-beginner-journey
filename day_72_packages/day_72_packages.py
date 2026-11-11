"""
Python Packages: Package Management, Dependency Resolution, Versioning,
Virtual Environments, Package Validation, Security Auditing, and Installation.

Uses only the Python standard library.
Compatible with Python 3.10+.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("package_manager")


class PackageError(Exception):
    """Base exception for package-management failures."""


class InvalidPackageError(PackageError):
    pass


class DependencyError(PackageError):
    pass


class SecurityError(PackageError):
    pass


class InstallationError(PackageError):
    pass


class PackageStatus(str, Enum):
    AVAILABLE = "available"
    INSTALLED = "installed"
    BLOCKED = "blocked"
    DEPRECATED = "deprecated"


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int = 0
    patch: int = 0

    @classmethod
    def parse(cls, value: str) -> Version:
        if not isinstance(value, str):
            raise InvalidPackageError("Version must be a string.")

        match = re.fullmatch(
            r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)",
            value.strip()
        )

        if not match:
            raise InvalidPackageError(
                f"Invalid version: {value}. Expected MAJOR.MINOR.PATCH."
            )

        return cls(*(int(part) for part in match.groups()))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True)
class Dependency:
    name: str
    constraint: str = "*"

    def __post_init__(self):
        validate_package_name(self.name)
        if not self.constraint.strip():
            raise InvalidPackageError("Dependency constraint cannot be empty.")


@dataclass
class Package:
    name: str
    version: Version
    description: str
    dependencies: list[Dependency] = field(default_factory=list)
    status: PackageStatus = PackageStatus.AVAILABLE
    license: str = "MIT"
    checksum: str = ""
    source: str = "pypi"

    def validate(self) -> None:
        validate_package_name(self.name)

        if not self.description.strip():
            raise InvalidPackageError("Package description is required.")

        if len(self.dependencies) > 100:
            raise InvalidPackageError("Too many dependencies.")

        dependency_names = [dep.name for dep in self.dependencies]

        if len(dependency_names) != len(set(dependency_names)):
            raise InvalidPackageError("Duplicate dependencies detected.")

        if self.name in dependency_names:
            raise DependencyError("A package cannot depend on itself.")

        if self.status == PackageStatus.BLOCKED:
            raise SecurityError(f"{self.name} is blocked.")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": str(self.version),
            "description": self.description,
            "dependencies": [
                asdict(dependency)
                for dependency in self.dependencies
            ],
            "status": self.status.value,
            "license": self.license,
            "checksum": self.checksum,
            "source": self.source
        }


def validate_package_name(name: str) -> None:
    if not isinstance(name, str):
        raise InvalidPackageError("Package name must be a string.")

    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9._-]{0,198}[A-Za-z0-9])?", name):
        raise InvalidPackageError(f"Invalid package name: {name}")

    if ".." in name:
        raise InvalidPackageError("Package names cannot contain consecutive dots.")


def normalize_name(name: str) -> str:
    validate_package_name(name)
    return re.sub(r"[-_.]+", "-", name).lower()


def satisfies(version: Version, constraint: str) -> bool:
    """Evaluate a restricted, explicit version constraint."""

    if constraint == "*":
        return True

    operators = ("==", "!=", ">=", "<=", ">", "<")

    for operator in operators:
        if constraint.startswith(operator):
            required = Version.parse(constraint[len(operator):])

            return {
                "==": version == required,
                "!=": version != required,
                ">=": version >= required,
                "<=": version <= required,
                ">": version > required,
                "<": version < required
            }[operator]

    raise InvalidPackageError(
        f"Unsupported version constraint: {constraint}"
    )


class PackageRepository:
    """In-memory representation of a package index."""

    def __init__(self):
        self.packages: dict[str, list[Package]] = {}

    def publish(self, package: Package) -> None:
        package.validate()
        key = normalize_name(package.name)

        versions = self.packages.setdefault(key, [])

        if any(existing.version == package.version for existing in versions):
            raise InvalidPackageError(
                f"{package.name} {package.version} already exists."
            )

        versions.append(package)
        versions.sort(key=lambda item: item.version, reverse=True)

    def get_versions(self, name: str) -> list[Package]:
        return self.packages.get(normalize_name(name), [])

    def resolve(
        self,
        name: str,
        constraint: str = "*"
    ) -> Package:

        candidates = [
            package
            for package in self.get_versions(name)
            if satisfies(package.version, constraint)
            and package.status == PackageStatus.AVAILABLE
        ]

        if not candidates:
            raise DependencyError(
                f"No available version of {name} satisfies {constraint}."
            )

        return candidates[0]


class DependencyResolver:
    """Resolve dependencies and detect circular dependency chains."""

    def __init__(self, repository: PackageRepository):
        self.repository = repository

    def resolve(self, name: str, constraint: str = "*") -> list[Package]:
        ordered: list[Package] = []
        visited: set[tuple[str, Version]] = set()
        active: set[str] = set()

        def visit(package_name: str, required: str) -> None:
            key = normalize_name(package_name)

            if key in active:
                raise DependencyError(
                    f"Circular dependency detected at {package_name}."
                )

            package = self.repository.resolve(package_name, required)
            identity = (key, package.version)

            if identity in visited:
                return

            active.add(key)

            for dependency in sorted(
                package.dependencies,
                key=lambda item: normalize_name(item.name)
            ):
                visit(dependency.name, dependency.constraint)

            active.remove(key)
            visited.add(identity)
            ordered.append(package)

        visit(name, constraint)
        return ordered


class SecurityAuditor:
    """Apply basic package-source and license policies."""

    def __init__(
        self,
        blocked_packages: Optional[set[str]] = None,
        allowed_licenses: Optional[set[str]] = None
    ):
        self.blocked = {
            normalize_name(name)
            for name in (blocked_packages or set())
        }
        self.allowed_licenses = allowed_licenses or {
            "MIT", "BSD-3-Clause", "Apache-2.0", "ISC"
        }

    def audit(self, packages: list[Package]) -> list[str]:
        issues = []

        for package in packages:
            if normalize_name(package.name) in self.blocked:
                issues.append(f"{package.name}: blocked package")

            if package.status == PackageStatus.BLOCKED:
                issues.append(f"{package.name}: repository block status")

            if package.license not in self.allowed_licenses:
                issues.append(
                    f"{package.name}: unapproved license {package.license}"
                )

            if package.source != "pypi":
                issues.append(
                    f"{package.name}: unapproved source {package.source}"
                )

        return issues


class Environment:
    """Simulate an isolated Python package environment."""

    def __init__(self, name: str):
        if not name.strip():
            raise ValueError("Environment name cannot be empty.")

        self.name = name
        self.installed: dict[str, Package] = {}

    def install(
        self,
        packages: list[Package],
        auditor: SecurityAuditor
    ) -> None:

        issues = auditor.audit(packages)

        if issues:
            raise SecurityError("; ".join(issues))

        # Validate all conflicts before modifying environment state.
        for package in packages:
            key = normalize_name(package.name)
            existing = self.installed.get(key)

            if existing and existing.version != package.version:
                raise InstallationError(
                    f"Version conflict for {package.name}: "
                    f"{existing.version} is installed."
                )

        for package in packages:
            key = normalize_name(package.name)
            self.installed[key] = package
            package.status = PackageStatus.INSTALLED

    def uninstall(self, name: str) -> None:
        key = normalize_name(name)

        if key not in self.installed:
            raise InstallationError(f"{name} is not installed.")

        dependents = [
            package.name
            for package in self.installed.values()
            if any(
                normalize_name(dep.name) == key
                for dep in package.dependencies
            )
        ]

        if dependents:
            raise InstallationError(
                f"Cannot uninstall {name}; required by {dependents}."
            )

        del self.installed[key]

    def list_packages(self) -> list[dict]:
        return [
            {
                "name": package.name,
                "version": str(package.version)
            }
            for package in sorted(
                self.installed.values(),
                key=lambda item: normalize_name(item.name)
            )
        ]


def create_demo_repository() -> PackageRepository:
    repository = PackageRepository()

    packages = [
        Package(
            "numpy",
            Version.parse("2.1.0"),
            "Numerical computing library."
        ),
        Package(
            "pandas",
            Version.parse("2.2.0"),
            "Data analysis library.",
            [Dependency("numpy", ">=2.0.0")]
        ),
        Package(
            "requests",
            Version.parse("2.32.0"),
            "HTTP client library."
        ),
        Package(
            "analytics-toolkit",
            Version.parse("1.0.0"),
            "Data processing toolkit.",
            [
                Dependency("pandas", ">=2.2.0"),
                Dependency("requests", ">=2.30.0")
            ]
        ),
        Package(
            "legacy-package",
            Version.parse("1.0.0"),
            "Blocked demonstration package.",
            status=PackageStatus.BLOCKED
        )
    ]

    for package in packages:
        repository.publish(package)

    return repository


def save_lock_file(
    packages: list[Package],
    destination: Path
) -> None:
    """Write deterministic dependency information."""

    data = {
        "lock_version": 1,
        "packages": [
            {
                "name": package.name,
                "version": str(package.version),
                "dependencies": [
                    {
                        "name": dependency.name,
                        "constraint": dependency.constraint
                    }
                    for dependency in package.dependencies
                ]
            }
            for package in packages
        ]
    }

    destination.parent.mkdir(parents=True, exist_ok=True)

    temporary = destination.with_suffix(destination.suffix + ".tmp")

    try:
        temporary.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8"
        )
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_lock_file(source: Path) -> dict:
    try:
        data = json.loads(source.read_text(encoding="utf-8"))

        if data.get("lock_version") != 1:
            raise ValueError("Unsupported lock-file version.")

        if not isinstance(data.get("packages"), list):
            raise ValueError("Invalid package list.")

        for item in data["packages"]:
            validate_package_name(item["name"])
            Version.parse(item["version"])

        return data

    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise PackageError(f"Cannot read lock file: {error}") from error


def run_demo() -> None:
    repository = create_demo_repository()
    resolver = DependencyResolver(repository)

    auditor = SecurityAuditor(
        blocked_packages={"malicious-library"}
    )

    environment = Environment("analytics-env")

    print("\nPYTHON PACKAGE MANAGEMENT DEMONSTRATION")

    print("\n1. Available package versions")

    for name in ("numpy", "pandas", "requests"):
        for package in repository.get_versions(name):
            print(f"{package.name} {package.version}")

    print("\n2. Dependency resolution")

    resolved = resolver.resolve("analytics-toolkit")

    for package in resolved:
        print(f"{package.name}=={package.version}")

    print("\n3. Security auditing")

    issues = auditor.audit(resolved)

    if issues:
        for issue in issues:
            print(issue)
    else:
        print("Security policy passed.")

    print("\n4. Installation")

    environment.install(resolved, auditor)

    for package in environment.list_packages():
        print(f"{package['name']}=={package['version']}")

    print("\n5. Lock-file generation")

    lock_path = Path("package-lock.json")
    save_lock_file(resolved, lock_path)

    loaded = load_lock_file(lock_path)
    print(f"Saved {len(loaded['packages'])} locked packages.")

    print("\n6. Version validation")

    assert satisfies(Version.parse("2.2.0"), ">=2.0.0")
    assert not satisfies(Version.parse("1.9.0"), ">=2.0.0")

    print("Version validation passed.")

    print("\n7. Dependency protection")

    try:
        environment.uninstall("numpy")
    except InstallationError as error:
        print(f"Expected protection: {error}")

    print("\n8. Package security failure")

    try:
        resolver.resolve("legacy-package")
    except PackageError as error:
        print(f"Expected failure: {error}")

    print("\n9. Final environment")

    print(json.dumps(environment.list_packages(), indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Python package management demonstration."
    )

    parser.add_argument(
        "--lock",
        type=Path,
        help="Validate and display an existing lock file."
    )

    arguments = parser.parse_args()

    try:
        if arguments.lock:
            data = load_lock_file(arguments.lock)
            print(json.dumps(data, indent=2))
        else:
            run_demo()

    except PackageError as error:
        logger.error("%s", error)
        sys.exit(1)


if __name__ == "__main__":
    main()
