#!/usr/bin/env python3
"""
Virtual Environments Management System

Demonstrates:
- Python virtual environment creation and management
- Environment isolation
- Package inventory and dependency tracking
- Environment validation
- Activation instructions
- Environment inspection and removal
- Security and operational safeguards

Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import venv

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


BASE_DIRECTORY = Path.cwd() / ".virtual-environments"
METADATA_FILE = "environment.json"
PYTHON_REQUIREMENTS = "requirements.txt"


class EnvironmentError(Exception):
    """Base exception for environment management."""


class EnvironmentExistsError(EnvironmentError):
    pass


class EnvironmentNotFoundError(EnvironmentError):
    pass


class EnvironmentValidationError(EnvironmentError):
    pass


@dataclass
class EnvironmentMetadata:
    name: str
    python_version: str
    executable: str
    created_at: str
    operating_system: str
    platform: str
    status: str = "created"


@dataclass
class PackageInfo:
    name: str
    version: str


class VirtualEnvironmentManager:

    def __init__(self, base_directory: Path = BASE_DIRECTORY):
        self.base_directory = base_directory.resolve()
        self.base_directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def validate_name(name: str) -> str:
        if not name or len(name) > 50:
            raise ValueError("Environment name must contain 1-50 characters.")

        if not all(c.isalnum() or c in "-_." for c in name):
            raise ValueError("Environment name contains invalid characters.")

        if name in {".", ".."}:
            raise ValueError("Invalid environment name.")

        return name

    def environment_path(self, name: str) -> Path:
        name = self.validate_name(name)
        path = (self.base_directory / name).resolve()

        if path.parent != self.base_directory:
            raise ValueError("Environment path escapes the managed directory.")

        return path

    @staticmethod
    def python_executable(path: Path) -> Path:
        if os.name == "nt":
            return path / "Scripts" / "python.exe"

        return path / "bin" / "python"

    def create(
        self,
        name: str,
        system_site_packages: bool = False,
        clear: bool = False
    ) -> EnvironmentMetadata:

        path = self.environment_path(name)

        if path.exists():
            if not clear:
                raise EnvironmentExistsError(
                    f"Environment '{name}' already exists."
                )

            if path.is_symlink():
                raise EnvironmentValidationError(
                    "Refusing to clear a symbolic-link directory."
                )

            shutil.rmtree(path)

        try:
            builder = venv.EnvBuilder(
                system_site_packages=system_site_packages,
                clear=False,
                symlinks=(os.name != "nt"),
                with_pip=True,
                prompt=name,
                upgrade_deps=False
            )

            builder.create(path)

            executable = self.python_executable(path)

            if not executable.is_file():
                raise EnvironmentValidationError(
                    "Python executable was not created."
                )

            version_result = subprocess.run(
                [str(executable), "--version"],
                capture_output=True,
                text=True,
                timeout=15,
                check=True
            )

            metadata = EnvironmentMetadata(
                name=name,
                python_version=version_result.stdout.strip()
                or version_result.stderr.strip(),
                executable=str(executable),
                created_at=datetime.now(timezone.utc).isoformat(),
                operating_system=platform.system(),
                platform=platform.platform()
            )

            metadata_path = path / METADATA_FILE

            metadata_path.write_text(
                json.dumps(asdict(metadata), indent=4),
                encoding="utf-8"
            )

            print(f"Environment created: {name}")

            return metadata

        except Exception:
            if path.exists() and not path.is_symlink():
                shutil.rmtree(path, ignore_errors=True)
            raise

    def list_environments(self) -> list[EnvironmentMetadata]:

        environments = []

        for path in sorted(self.base_directory.iterdir()):

            if not path.is_dir() or path.is_symlink():
                continue

            metadata_path = path / METADATA_FILE

            if not metadata_path.is_file():
                continue

            try:
                data = json.loads(
                    metadata_path.read_text(encoding="utf-8")
                )

                environments.append(
                    EnvironmentMetadata(**data)
                )

            except (OSError, ValueError, TypeError):
                print(
                    f"Warning: Invalid metadata in {path.name}",
                    file=sys.stderr
                )

        return environments

    def inspect(self, name: str) -> dict:

        path = self.environment_path(name)

        if not path.is_dir() or path.is_symlink():
            raise EnvironmentNotFoundError(name)

        executable = self.python_executable(path)

        if not executable.is_file():
            raise EnvironmentValidationError(
                "Environment Python executable is missing."
            )

        result = subprocess.run(
            [
                str(executable),
                "-c",
                (
                    "import sys, json; "
                    "print(json.dumps({"
                    "'executable': sys.executable, "
                    "'version': sys.version, "
                    "'prefix': sys.prefix, "
                    "'base_prefix': sys.base_prefix, "
                    "'isolated': sys.prefix != sys.base_prefix"
                    "}))"
                )
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=True
        )

        environment_info = json.loads(result.stdout)

        package_result = subprocess.run(
            [
                str(executable),
                "-m",
                "pip",
                "list",
                "--format=json"
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=True
        )

        environment_info["packages"] = json.loads(
            package_result.stdout
        )

        environment_info["path"] = str(path)

        return environment_info

    def install(
        self,
        name: str,
        packages: list[str]
    ) -> None:

        if not packages:
            raise ValueError("At least one package is required.")

        for package in packages:
            if not package.strip():
                raise ValueError("Empty package specification.")

            if package.startswith("-"):
                raise ValueError(
                    "Package specifications cannot be pip options."
                )

        path = self.environment_path(name)
        executable = self.python_executable(path)

        if not executable.is_file():
            raise EnvironmentNotFoundError(name)

        command = [
            str(executable),
            "-m",
            "pip",
            "install",
            "--"
        ] + packages

        subprocess.run(
            command,
            check=True,
            timeout=600
        )

    def freeze(self, name: str) -> list[str]:

        path = self.environment_path(name)
        executable = self.python_executable(path)

        if not executable.is_file():
            raise EnvironmentNotFoundError(name)

        result = subprocess.run(
            [
                str(executable),
                "-m",
                "pip",
                "freeze"
            ],
            capture_output=True,
            text=True,
            timeout=60,
            check=True
        )

        requirements = sorted(
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip()
        )

        requirements_file = path / PYTHON_REQUIREMENTS

        requirements_file.write_text(
            "\n".join(requirements) + "\n",
            encoding="utf-8"
        )

        return requirements

    def verify_isolation(self, name: str) -> bool:

        info = self.inspect(name)

        isolated = info["isolated"]

        if not isolated:
            raise EnvironmentValidationError(
                "Environment is not isolated from the base interpreter."
            )

        print("Isolation verification passed.")

        return True

    def activation_instructions(self, name: str) -> str:

        path = self.environment_path(name)

        if not path.is_dir() or path.is_symlink():
            raise EnvironmentNotFoundError(name)

        if os.name == "nt":
            return str(path / "Scripts" / "Activate.ps1")

        return f"source {path}/bin/activate"

    def remove(self, name: str) -> None:

        path = self.environment_path(name)

        if not path.exists():
            raise EnvironmentNotFoundError(name)

        if path.is_symlink():
            raise EnvironmentValidationError(
                "Refusing to remove a symbolic-link directory."
            )

        if not path.is_dir():
            raise EnvironmentValidationError(
                "Environment path is not a directory."
            )

        shutil.rmtree(path)

        print(f"Environment removed: {name}")


def demonstrate() -> None:

    manager = VirtualEnvironmentManager()

    print("\nVIRTUAL ENVIRONMENT MANAGEMENT")
    print("=" * 45)

    name = "demo-project"

    try:
        metadata = manager.create(name)

        print("\nEnvironment metadata:")
        print(json.dumps(asdict(metadata), indent=4))

        print("\nIsolation validation:")
        manager.verify_isolation(name)

        print("\nEnvironment inspection:")
        information = manager.inspect(name)

        print("Python:", information["version"].splitlines()[0])
        print("Executable:", information["executable"])
        print("Isolated:", information["isolated"])
        print("Installed packages:", len(information["packages"]))

        print("\nActivation instruction:")
        print(manager.activation_instructions(name))

        print("\nEnvironment inventory:")

        for environment in manager.list_environments():
            print(
                f"{environment.name}: "
                f"{environment.python_version}"
            )

        print("\nDependency snapshot:")

        requirements = manager.freeze(name)

        print("\n".join(requirements[:10]) or "No packages installed.")

    except EnvironmentError as error:
        print("Environment error:", error)

    finally:
        print("\nDemo completed. Environment retained for inspection.")


def main() -> None:

    parser = argparse.ArgumentParser(
        description="Virtual Environment Management CLI"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("name")
    create_parser.add_argument(
        "--system-site-packages",
        action="store_true"
    )
    create_parser.add_argument("--clear", action="store_true")

    inspect_parser = subparsers.add_parser("inspect")
    inspect_parser.add_argument("name")

    install_parser = subparsers.add_parser("install")
    install_parser.add_argument("name")
    install_parser.add_argument("packages", nargs="+")

    freeze_parser = subparsers.add_parser("freeze")
    freeze_parser.add_argument("name")

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("name")

    remove_parser = subparsers.add_parser("remove")
    remove_parser.add_argument("name")

    activate_parser = subparsers.add_parser("activate")
    activate_parser.add_argument("name")

    subparsers.add_parser("list")

    args = parser.parse_args()

    manager = VirtualEnvironmentManager()

    try:

        if args.command == "create":
            result = manager.create(
                args.name,
                args.system_site_packages,
                args.clear
            )
            print(json.dumps(asdict(result), indent=4))

        elif args.command == "inspect":
            print(json.dumps(manager.inspect(args.name), indent=4))

        elif args.command == "install":
            manager.install(args.name, args.packages)

        elif args.command == "freeze":
            print("\n".join(manager.freeze(args.name)))

        elif args.command == "verify":
            manager.verify_isolation(args.name)

        elif args.command == "remove":
            manager.remove(args.name)

        elif args.command == "activate":
            print(manager.activation_instructions(args.name))

        elif args.command == "list":
            for environment in manager.list_environments():
                print(
                    f"{environment.name} | "
                    f"{environment.python_version} | "
                    f"{environment.created_at}"
                )

    except (
        EnvironmentError,
        ValueError,
        OSError,
        subprocess.SubprocessError
    ) as error:

        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":

    if len(sys.argv) == 1:
        demonstrate()
    else:
        main()
