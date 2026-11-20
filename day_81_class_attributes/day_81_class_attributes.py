from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar
from threading import Lock
import json


class AttributeScope(Enum):
    CLASS = "class"
    INSTANCE = "instance"


class ValidationError(ValueError):
    pass


@dataclass
class AttributeDefinition:
    name: str
    value: Any
    scope: AttributeScope
    mutable: bool = False


class Repository:
    """
    Demonstrates class attributes and instance attributes.

    Class attributes are shared by instances unless an instance
    explicitly creates an attribute with the same name.
    """

    # Class attributes
    organization: ClassVar[str] = "OpenSystems"
    total_repositories: ClassVar[int] = 0
    maximum_repositories: ClassVar[int] = 100
    default_visibility: ClassVar[str] = "private"
    supported_languages: ClassVar[tuple[str, ...]] = (
        "Python", "JavaScript", "C++", "Java"
    )

    # Mutable class attribute, protected by a lock.
    registry: ClassVar[dict[str, "Repository"]] = {}
    _lock: ClassVar[Lock] = Lock()

    def __init__(
        self,
        name: str,
        owner: str,
        visibility: str | None = None,
    ):
        self._validate_text(name, "Repository name")
        self._validate_text(owner, "Owner")

        visibility = visibility or type(self).default_visibility

        if visibility not in {"public", "private", "internal"}:
            raise ValidationError("Invalid repository visibility.")

        self.name = name
        self.owner = owner
        self.visibility = visibility

        # Instance attribute: independently stored for every object.
        self.created_commits = 0
        self.active = True

        with Repository._lock:
            if name in Repository.registry:
                raise ValidationError("Repository already exists.")

            if Repository.total_repositories >= Repository.maximum_repositories:
                raise ValidationError("Repository capacity reached.")

            Repository.registry[name] = self
            Repository.total_repositories += 1

    @staticmethod
    def _validate_text(value: str, field_name: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"{field_name} cannot be empty.")

    def add_commit(self) -> None:
        if not self.active:
            raise ValidationError("Inactive repository cannot accept commits.")

        self.created_commits += 1

    @classmethod
    def get_repository(cls, name: str) -> Repository | None:
        return Repository.registry.get(name)

    @classmethod
    def change_default_visibility(cls, visibility: str) -> None:
        if visibility not in {"public", "private", "internal"}:
            raise ValidationError("Invalid default visibility.")

        cls.default_visibility = visibility

    @classmethod
    def statistics(cls) -> dict[str, Any]:
        with Repository._lock:
            return {
                "organization": cls.organization,
                "total_repositories": cls.total_repositories,
                "maximum_repositories": cls.maximum_repositories,
                "repositories": list(cls.registry.keys()),
            }

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "owner": self.owner,
            "visibility": self.visibility,
            "created_commits": self.created_commits,
            "organization": self.organization,
        }

    def close(self) -> None:
        with Repository._lock:
            if self.active:
                self.active = False

    def __repr__(self) -> str:
        return (
            f"Repository(name={self.name!r}, "
            f"owner={self.owner!r}, "
            f"commits={self.created_commits})"
        )


class EnterpriseRepository(Repository):
    """
    Demonstrates inherited class attributes and attribute shadowing.
    """

    organization: ClassVar[str] = "EnterpriseSystems"
    maximum_repositories: ClassVar[int] = 50
    compliance_required: ClassVar[bool] = True

    def __init__(
        self,
        name: str,
        owner: str,
        visibility: str = "internal",
    ):
        super().__init__(name, owner, visibility)
        self.audit_enabled = True


class AttributeInspector:
    """Inspects class-level and instance-level attribute storage."""

    @staticmethod
    def inspect(instance: object) -> dict[str, Any]:
        cls = type(instance)

        return {
            "class": cls.__name__,
            "class_attributes": {
                key: repr(value)
                for key, value in vars(cls).items()
                if not key.startswith("__")
            },
            "instance_attributes": vars(instance).copy(),
            "organization_lookup": instance.organization,
        }


class Configuration:
    """Demonstrates safe shared immutable configuration."""

    environment: ClassVar[str] = "development"
    limits: ClassVar[tuple[int, int]] = (10, 100)

    def __init__(self, service_name: str):
        self.service_name = service_name

    @classmethod
    def set_environment(cls, environment: str) -> None:
        allowed = {"development", "testing", "production"}

        if environment not in allowed:
            raise ValidationError("Unsupported environment.")

        cls.environment = environment


def demonstrate_shared_mutable_attributes() -> None:
    print("\nMUTABLE CLASS ATTRIBUTE BEHAVIOR")

    class UnsafeCache:
        cache: ClassVar[dict[str, str]] = {}

    first = UnsafeCache()
    second = UnsafeCache()

    first.cache["status"] = "shared"

    assert second.cache["status"] == "shared"

    print("Shared dictionary:", second.cache)

    # Instance assignment shadows the class attribute.
    first.cache = {"status": "private"}

    assert first.cache["status"] == "private"
    assert second.cache["status"] == "shared"

    print("First instance:", first.cache)
    print("Second instance:", second.cache)


def demonstrate_instance_isolation() -> None:
    print("\nINSTANCE ATTRIBUTE ISOLATION")

    first = Repository("alpha", "atul")
    second = Repository("beta", "developer")

    first.add_commit()
    first.add_commit()
    second.add_commit()

    assert first.created_commits == 2
    assert second.created_commits == 1

    print(first.describe())
    print(second.describe())

    assert first.organization == second.organization

    # Shadowing affects only the first object.
    first.organization = "CustomOrganization"

    assert first.organization == "CustomOrganization"
    assert second.organization == "OpenSystems"

    print("First organization:", first.organization)
    print("Second organization:", second.organization)

    print("\nCLASS AND INSTANCE STORAGE")
    print(json.dumps(
        AttributeInspector.inspect(second),
        indent=2,
        default=str,
    ))


def demonstrate_inheritance() -> None:
    print("\nCLASS ATTRIBUTE INHERITANCE")

    enterprise = EnterpriseRepository(
        "secure-platform",
        "security-team",
    )

    standard = Repository("general-platform", "engineering")

    print("Standard organization:", standard.organization)
    print("Enterprise organization:", enterprise.organization)

    print("Standard limit:", Repository.maximum_repositories)
    print("Enterprise limit:", EnterpriseRepository.maximum_repositories)

    assert enterprise.compliance_required is True
    assert standard.organization == "OpenSystems"
    assert enterprise.organization == "EnterpriseSystems"

    # Updating a parent attribute does not overwrite a child shadow.
    Repository.organization = "UpdatedSystems"

    assert standard.organization == "UpdatedSystems"
    assert enterprise.organization == "EnterpriseSystems"


def demonstrate_class_methods() -> None:
    print("\nCLASS METHOD AND STATIC METHOD")

    Repository.change_default_visibility("internal")

    repository = Repository("analytics", "data-team")

    print("New repository visibility:", repository.visibility)
    print("Statistics:", Repository.statistics())

    Configuration.set_environment("production")

    config = Configuration("payment-service")

    print("Environment:", config.environment)
    print("Service:", config.service_name)


def demonstrate_edge_cases() -> None:
    print("\nVALIDATION AND EDGE CASES")

    try:
        Repository("", "owner")
    except ValidationError as error:
        print("Validation caught:", error)

    try:
        Repository.change_default_visibility("unknown")
    except ValidationError as error:
        print("Configuration caught:", error)

    repository = Repository("temporary", "tester")
    repository.close()

    try:
        repository.add_commit()
    except ValidationError as error:
        print("State validation caught:", error)

    # Class attribute changes are visible to instances without overrides.
    Repository.organization = "FinalOrganization"

    assert repository.organization == "FinalOrganization"

    # An instance override remains independent.
    repository.organization = "LocalOrganization"

    assert repository.organization == "LocalOrganization"


def main() -> None:
    print("=" * 65)
    print("CLASS ATTRIBUTES: PYTHON DEMONSTRATION")
    print("=" * 65)

    demonstrate_instance_isolation()
    demonstrate_shared_mutable_attributes()
    demonstrate_inheritance()
    demonstrate_class_methods()
    demonstrate_edge_cases()

    print("\nFINAL CLASS STATISTICS")
    print(json.dumps(Repository.statistics(), indent=2))

    print("\nEXECUTION COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
