"""
MULTIPLE INHERITANCE
Demonstration of multiple inheritance, method resolution order (MRO),
diamond inheritance, cooperative super(), mixins, abstract classes,
conflict detection, and composition.

Python 3.10+
No external dependencies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


# ============================================================
# 1. BASIC MULTIPLE INHERITANCE
# ============================================================

class Logger:
    def log(self, message: str) -> None:
        print(f"[LOG] {message}")


class Validator:
    def validate(self, value: Any) -> bool:
        if value is None:
            raise ValueError("Value cannot be None")
        return True


class RepositoryService(Logger, Validator):
    def save(self, value: Any) -> None:
        self.validate(value)
        self.log(f"Saving: {value}")


# ============================================================
# 2. DIAMOND INHERITANCE
# ============================================================

class Device:
    def __init__(self, name: str) -> None:
        self.name = name

    def describe(self) -> str:
        return f"Device: {self.name}"


class Camera(Device):
    def capture(self) -> str:
        return "Image captured"


class NetworkAdapter(Device):
    def connect(self) -> str:
        return "Network connected"


class SmartCamera(Camera, NetworkAdapter):
    def operate(self) -> list[str]:
        return [
            self.capture(),
            self.connect(),
            self.describe()
        ]


# ============================================================
# 3. METHOD RESOLUTION ORDER
# ============================================================

class A:
    def process(self) -> str:
        return "A"


class B(A):
    def process(self) -> str:
        return "B -> " + super().process()


class C(A):
    def process(self) -> str:
        return "C -> " + super().process()


class D(B, C):
    def process(self) -> str:
        return "D -> " + super().process()


# ============================================================
# 4. COOPERATIVE MULTIPLE INHERITANCE
# ============================================================

class WorkflowRoot:
    def __init__(self, **kwargs: Any) -> None:
        self.workflow_steps: list[str] = []
        super().__init__(**kwargs)


class AuthenticationMixin:
    def __init__(self, **kwargs: Any) -> None:
        self.workflow_steps: list[str]
        self.workflow_steps.append("Authentication")
        super().__init__(**kwargs)


class AuditMixin:
    def __init__(self, **kwargs: Any) -> None:
        self.workflow_steps: list[str]
        self.workflow_steps.append("Audit")
        super().__init__(**kwargs)


class NotificationMixin:
    def __init__(self, **kwargs: Any) -> None:
        self.workflow_steps: list[str]
        self.workflow_steps.append("Notification")
        super().__init__(**kwargs)


class EnterpriseWorkflow(
    AuthenticationMixin,
    AuditMixin,
    NotificationMixin,
    WorkflowRoot
):
    def __init__(self, workflow_name: str, **kwargs: Any) -> None:
        self.workflow_name = workflow_name
        super().__init__(**kwargs)


# ============================================================
# 5. ABSTRACT BASE CLASSES AND MULTIPLE INHERITANCE
# ============================================================

class Exportable(ABC):
    @abstractmethod
    def export(self) -> str:
        pass


class Compressible(ABC):
    @abstractmethod
    def compress(self, content: str) -> str:
        pass


class SecureDocument(Exportable, Compressible):
    def __init__(self, content: str) -> None:
        if not isinstance(content, str):
            raise TypeError("Document content must be a string")
        self.content = content

    def export(self) -> str:
        return self.content

    def compress(self, content: str) -> str:
        # A demonstrative compression representation.
        return f"COMPRESSED[{len(content)}]:{content}"


# ============================================================
# 6. MIXINS AND METHOD OVERRIDING
# ============================================================

class TimestampMixin:
    def timestamp(self) -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


class JsonMixin:
    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class SystemEvent(TimestampMixin, JsonMixin):
    event_id: int
    event_type: str
    description: str


# ============================================================
# 7. METHOD CONFLICTS AND EXPLICIT RESOLUTION
# ============================================================

class CSVExporter:
    def export_format(self) -> str:
        return "CSV"


class JSONExporter:
    def export_format(self) -> str:
        return "JSON"


class DataExporter(CSVExporter, JSONExporter):
    def export_format(self) -> str:
        # Explicitly select the intended parent implementation.
        return (
            f"Primary={CSVExporter.export_format(self)}, "
            f"Secondary={JSONExporter.export_format(self)}"
        )


# ============================================================
# 8. MULTIPLE INHERITANCE WITH STATE VALIDATION
# ============================================================

class ReadPermission:
    def can_read(self) -> bool:
        return True


class WritePermission:
    def can_write(self) -> bool:
        return True


class AdminAccount(ReadPermission, WritePermission):
    def __init__(self, username: str, active: bool = True) -> None:
        if not username or not username.strip():
            raise ValueError("Username cannot be empty")

        self.username = username.strip()
        self.active = active

    def authorize(self, operation: str) -> bool:
        if not self.active:
            return False

        permissions = {
            "read": self.can_read(),
            "write": self.can_write()
        }

        if operation not in permissions:
            raise ValueError(f"Unsupported operation: {operation}")

        return permissions[operation]


# ============================================================
# 9. MRO INSPECTION AND INHERITANCE ANALYSIS
# ============================================================

def inspect_class(cls: type) -> None:
    print(f"\nClass: {cls.__name__}")
    print("Direct bases:", [base.__name__ for base in cls.__bases__])
    print("MRO:", " -> ".join(c.__name__ for c in cls.__mro__))


def validate_mro(cls: type) -> bool:
    """Check that the class has a valid, consistent Python MRO."""
    try:
        cls.mro()
        return True
    except TypeError:
        return False


# ============================================================
# 10. COMPOSITION AS AN ALTERNATIVE
# ============================================================

@dataclass
class AuthenticationService:
    authenticated: bool = False

    def authenticate(self, username: str) -> bool:
        self.authenticated = bool(username.strip())
        return self.authenticated


@dataclass
class AuditService:
    records: list[str] = field(default_factory=list)

    def record(self, message: str) -> None:
        self.records.append(message)


class ComposedApplication:
    """Uses composition when independent behavior is preferable."""

    def __init__(
        self,
        authentication: AuthenticationService,
        audit: AuditService
    ) -> None:
        self.authentication = authentication
        self.audit = audit

    def execute(self, username: str) -> bool:
        if not self.authentication.authenticate(username):
            return False

        self.audit.record(f"Operation performed by {username}")
        return True


# ============================================================
# 11. AUTOMATED ASSERTIONS
# ============================================================

def run_tests() -> None:
    # Basic multiple inheritance.
    service = RepositoryService()
    assert isinstance(service, Logger)
    assert isinstance(service, Validator)
    assert service.validate("record") is True

    # Diamond inheritance.
    camera = SmartCamera("Security Camera")
    assert camera.capture() == "Image captured"
    assert camera.connect() == "Network connected"
    assert isinstance(camera, Device)

    # MRO and cooperative super().
    diamond = D()
    assert diamond.process() == "D -> B -> C -> A"
    assert D.__mro__ == (D, B, C, A, object)

    # Cooperative initialization.
    workflow = EnterpriseWorkflow("Release Workflow")
    assert workflow.workflow_name == "Release Workflow"
    assert workflow.workflow_steps == [
        "Authentication",
        "Audit",
        "Notification"
    ]

    # Abstract interfaces.
    document = SecureDocument("Confidential report")
    assert document.export() == "Confidential report"
    assert "COMPRESSED" in document.compress(document.export())

    # Mixins.
    event = SystemEvent(1, "DEPLOYMENT", "Release completed")
    assert event.to_dict()["event_id"] == 1
    assert event.timestamp()

    # Explicit conflict resolution.
    exporter = DataExporter()
    assert exporter.export_format() == "Primary=CSV, Secondary=JSON"

    # Permission handling.
    account = AdminAccount("operator")
    assert account.authorize("read")
    assert account.authorize("write")
    account.active = False
    assert not account.authorize("read")

    # Composition.
    app = ComposedApplication(
        AuthenticationService(),
        AuditService()
    )
    assert app.execute("operator")
    assert len(app.audit.records) == 1

    assert validate_mro(SmartCamera)

    try:
        AdminAccount("")
    except ValueError:
        pass
    else:
        raise AssertionError("Empty username should fail")

    try:
        account.authorize("delete")
    except ValueError:
        pass
    else:
        raise AssertionError("Unsupported operation should fail")


# ============================================================
# 12. EXECUTION
# ============================================================

def main() -> None:
    print("=" * 65)
    print("MULTIPLE INHERITANCE IN PYTHON")
    print("=" * 65)

    print("\n1. Basic multiple inheritance")
    RepositoryService().save({"id": 101, "status": "ACTIVE"})

    print("\n2. Diamond inheritance")
    camera = SmartCamera("Entrance Camera")
    for result in camera.operate():
        print(result)

    print("\n3. Method Resolution Order")
    inspect_class(D)
    print("Method result:", D().process())

    print("\n4. Cooperative initialization")
    workflow = EnterpriseWorkflow("Production Deployment")
    print("Execution steps:", workflow.workflow_steps)
    inspect_class(EnterpriseWorkflow)

    print("\n5. Abstract classes")
    document = SecureDocument("Enterprise data")
    print("Export:", document.export())
    print("Compression:", document.compress(document.export()))

    print("\n6. Mixins")
    event = SystemEvent(501, "LOGIN", "User authenticated")
    print("Event:", event.to_dict())
    print("Timestamp:", event.timestamp())

    print("\n7. Explicit method conflict resolution")
    print(DataExporter().export_format())

    print("\n8. Permission evaluation")
    account = AdminAccount("security_admin")
    print("Read:", account.authorize("read"))
    print("Write:", account.authorize("write"))

    print("\n9. Composition")
    app = ComposedApplication(AuthenticationService(), AuditService())
    print("Operation:", app.execute("security_admin"))
    print("Audit:", app.audit.records)

    print("\n10. Automated validation")
    run_tests()
    print("All tests passed.")


if __name__ == "__main__":
    main()
