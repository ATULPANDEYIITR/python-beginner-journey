#!/usr/bin/env python3
"""
Installing Python Packages with pip
-----------------------------------
Demonstrates package validation, installation planning, dependency
management, environment inspection, security checks, and subprocess
execution using Python's standard library.

Default execution is simulation-only. Use --execute to run pip.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("pip_manager")


class PackageState(Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    INSTALLING = "installing"
    INSTALLED = "installed"
    FAILED = "failed"


class PackageError(Exception):
    """Base exception for package management failures."""


class ValidationError(PackageError):
    pass


class InstallationError(PackageError):
    pass


@dataclass
class Package:
    name: str
    version: Optional[str] = None
    state: PackageState = PackageState.PENDING
    dependencies: list[str] = field(default_factory=list)

    @property
    def requirement(self) -> str:
        return f"{self.name}=={self.version}" if self.version else self.name


@dataclass
class InstallationResult:
    package: str
    state: str
    command: list[str]
    return_code: Optional[int]
    message: str


class PackageValidator:
    """Validates basic package names and requirement specifications."""

    NAME_PATTERN = re.compile(
        r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$"
    )
    VERSION_PATTERN = re.compile(
        r"^[A-Za-z0-9][A-Za-z0-9.!+_-]*$"
    )

    @classmethod
    def validate(cls, package: Package) -> None:
        name = package.name.strip()

        if not cls.NAME_PATTERN.fullmatch(name):
            raise ValidationError(f"Invalid package name: {name!r}")

        if package.version is not None:
            if not cls.VERSION_PATTERN.fullmatch(package.version):
                raise ValidationError(
                    f"Invalid version specification: {package.version!r}"
                )

        package.name = name
        package.state = PackageState.VALIDATED


class EnvironmentInspector:

    @staticmethod
    def python_version() -> str:
        return sys.version.split()[0]

    @staticmethod
    def pip_version() -> str:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            raise PackageError(
                result.stderr.strip() or "pip is unavailable."
            )

        return result.stdout.strip()

    @staticmethod
    def pip_available() -> bool:
        return shutil.which(sys.executable) is not None

    @staticmethod
    def installed_packages() -> list[dict]:
        result = subprocess.run(
            [
                sys.executable, "-m", "pip",
                "list", "--format=json"
            ],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            raise PackageError(result.stderr.strip())

        try:
            packages = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise PackageError("Invalid pip list output.") from exc

        return packages

    @staticmethod
    def verify_dependencies() -> str:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "check"],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            return result.stdout + result.stderr

        return result.stdout.strip() or "No broken requirements found."


class PipInstaller:
    """
    Executes pip through subprocess using argument lists.
    Avoids shell=True to prevent shell injection.
    """

    def __init__(
        self,
        timeout: int = 300,
        upgrade: bool = False,
        index_url: Optional[str] = None,
        trusted_hosts: Optional[list[str]] = None
    ):
        if timeout <= 0:
            raise ValueError("Timeout must be positive.")

        self.timeout = timeout
        self.upgrade = upgrade
        self.index_url = index_url
        self.trusted_hosts = trusted_hosts or []

        if index_url and not index_url.startswith("https://"):
            raise ValidationError(
                "Package index must use HTTPS."
            )

    def build_command(
        self,
        package: Package,
        dry_run: bool = True
    ) -> list[str]:

        command = [
            sys.executable,
            "-m",
            "pip",
            "install"
        ]

        if dry_run:
            command.append("--dry-run")

        if self.upgrade:
            command.append("--upgrade")

        if self.index_url:
            command.extend(["--index-url", self.index_url])

        for host in self.trusted_hosts:
            if not re.fullmatch(r"[A-Za-z0-9.-]+", host):
                raise ValidationError("Invalid trusted host.")
            command.extend(["--trusted-host", host])

        command.append(package.requirement)

        return command

    def install(
        self,
        package: Package,
        execute: bool = False
    ) -> InstallationResult:

        PackageValidator.validate(package)

        command = self.build_command(
            package,
            dry_run=not execute
        )

        if not execute:
            return InstallationResult(
                package.requirement,
                PackageState.VALIDATED.value,
                command,
                None,
                "Installation simulated. No system changes made."
            )

        package.state = PackageState.INSTALLING

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False
            )

            if result.returncode != 0:
                package.state = PackageState.FAILED

                raise InstallationError(
                    result.stderr.strip()
                    or "pip installation failed."
                )

            package.state = PackageState.INSTALLED

            return InstallationResult(
                package.requirement,
                package.state.value,
                command,
                result.returncode,
                result.stdout.strip() or "Installation completed."
            )

        except subprocess.TimeoutExpired as exc:
            package.state = PackageState.FAILED
            raise InstallationError(
                f"Installation exceeded {self.timeout} seconds."
            ) from exc

        except OSError as exc:
            package.state = PackageState.FAILED
            raise InstallationError(str(exc)) from exc


class RequirementsManager:
    """Reads and validates a basic requirements.txt file."""

    def __init__(self):
        self.packages: list[Package] = []

    def load(self, filepath: Path) -> list[Package]:
        if not filepath.is_file():
            raise FileNotFoundError(filepath)

        packages = []

        for line_number, raw_line in enumerate(
            filepath.read_text(encoding="utf-8").splitlines(),
            start=1
        ):
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if line.startswith(("-e ", "--", "-r ", "-c ")):
                raise ValidationError(
                    f"Unsupported requirement at line {line_number}: {line}"
                )

            match = re.fullmatch(
                r"([A-Za-z0-9][A-Za-z0-9._-]*)(?:==([A-Za-z0-9][A-Za-z0-9.!+_-]*))?",
                line
            )

            if not match:
                raise ValidationError(
                    f"Unsupported requirement at line {line_number}: {line}"
                )

            package = Package(
                name=match.group(1),
                version=match.group(2)
            )

            PackageValidator.validate(package)
            packages.append(package)

        self.packages = packages
        return packages


class InstallationManager:

    def __init__(self, installer: PipInstaller):
        self.installer = installer
        self.history: list[InstallationResult] = []

    def process(
        self,
        packages: list[Package],
        execute: bool = False
    ) -> list[InstallationResult]:

        results = []

        for package in packages:
            try:
                result = self.installer.install(
                    package,
                    execute=execute
                )
                results.append(result)
                self.history.append(result)

            except PackageError as exc:
                logger.error(
                    "Package %s failed: %s",
                    package.name,
                    exc
                )

                result = InstallationResult(
                    package.name,
                    PackageState.FAILED.value,
                    [],
                    None,
                    str(exc)
                )

                results.append(result)
                self.history.append(result)

        return results

    def save_report(self, filepath: Path) -> None:
        data = [
            {
                **asdict(item),
                "state": item.state,
            }
            for item in self.history
        ]

        filepath.write_text(
            json.dumps(data, indent=4),
            encoding="utf-8"
        )


def demonstrate() -> None:
    print("\n=== PYTHON PACKAGE MANAGEMENT WITH PIP ===")

    print("\n1. Environment information")

    try:
        print("Python:", EnvironmentInspector.python_version())
        print("pip:", EnvironmentInspector.pip_version())
    except PackageError as exc:
        logger.error("Environment inspection failed: %s", exc)
        return

    print("\n2. Package validation")

    packages = [
        Package("requests", "2.32.3"),
        Package("numpy"),
        Package("pandas", "2.2.3"),
        Package("invalid package name")
    ]

    installer = PipInstaller(timeout=300)
    manager = InstallationManager(installer)

    results = manager.process(packages)

    for result in results:
        print(
            f"{result.package}: {result.state}"
        )
        if result.command:
            print("Command:", " ".join(result.command))

    print("\n3. Installed packages")

    try:
        installed = EnvironmentInspector.installed_packages()

        for item in installed[:5]:
            print(
                f"{item['name']} == {item['version']}"
            )

        print(f"Total installed packages: {len(installed)}")

    except PackageError as exc:
        logger.error("Package listing failed: %s", exc)

    print("\n4. Dependency consistency")

    try:
        print(EnvironmentInspector.verify_dependencies())
    except PackageError as exc:
        logger.error("%s", exc)

    print("\n5. Installation history")

    for result in manager.history:
        print(
            f"{result.package}: {result.message}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Python pip package management utility."
    )

    parser.add_argument(
        "--install",
        nargs="+",
        metavar="PACKAGE",
        help="Install one or more packages."
    )

    parser.add_argument(
        "--requirements",
        type=Path,
        help="Load a basic requirements.txt file."
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute installations instead of simulating."
    )

    parser.add_argument(
        "--report",
        type=Path,
        default=Path("pip_installation_report.json")
    )

    parser.add_argument(
        "--upgrade",
        action="store_true"
    )

    args = parser.parse_args()

    installer = PipInstaller(upgrade=args.upgrade)
    manager = InstallationManager(installer)

    try:
        if args.install:
            packages = []

            for requirement in args.install:
                match = re.fullmatch(
                    r"([A-Za-z0-9][A-Za-z0-9._-]*)(?:==([A-Za-z0-9][A-Za-z0-9.!+_-]*))?",
                    requirement
                )

                if not match:
                    raise ValidationError(
                        f"Unsupported requirement: {requirement}"
                    )

                packages.append(
                    Package(match.group(1), match.group(2))
                )

        elif args.requirements:
            packages = RequirementsManager().load(
                args.requirements
            )

        else:
            demonstrate()
            return

        results = manager.process(
            packages,
            execute=args.execute
        )

        for result in results:
            print(
                f"{result.package}: {result.state} - {result.message}"
            )

        manager.save_report(args.report)

        print(f"\nReport saved to {args.report}")

        if args.execute:
            try:
                print(
                    "\nDependency check:",
                    EnvironmentInspector.verify_dependencies()
                )
            except PackageError as exc:
                logger.error("Dependency check failed: %s", exc)

    except (PackageError, OSError, ValueError) as exc:
        logger.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    demonstrate() if len(sys.argv) == 1 else main()
