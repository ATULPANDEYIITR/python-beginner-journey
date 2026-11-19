from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("instance_attributes")


class ValidationError(ValueError):
    """Raised when an instance attribute violates its rules."""


class DeviceStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


@dataclass
class Device:
    """
    Each Device object owns its own instance attributes.

    Class attributes are shared by all instances.
    Instance attributes belong to individual objects.
    """

    # Class attribute: shared across Device instances.
    category: ClassVar[str] = "Network Equipment"
    default_status: ClassVar[DeviceStatus] = DeviceStatus.ACTIVE

    # Instance attributes.
    device_id: str
    name: str
    manufacturer: str
    temperature: float = 25.0
    status: DeviceStatus = DeviceStatus.ACTIVE
    configuration: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        self.device_id = self.device_id.strip()
        self.name = self.name.strip()
        self.manufacturer = self.manufacturer.strip()

        if not self.device_id:
            raise ValidationError("Device ID cannot be empty.")

        if not self.name:
            raise ValidationError("Device name cannot be empty.")

        if not self.manufacturer:
            raise ValidationError("Manufacturer cannot be empty.")

        if not isinstance(self.temperature, (int, float)):
            raise ValidationError("Temperature must be numeric.")

        if not -50 <= self.temperature <= 150:
            raise ValidationError("Temperature must be between -50 and 150.")

        if not isinstance(self.status, DeviceStatus):
            raise ValidationError("Invalid device status.")

        if not isinstance(self.configuration, dict):
            raise ValidationError("Configuration must be a dictionary.")

        if not isinstance(self.tags, list):
            raise ValidationError("Tags must be a list.")

    def update_attribute(self, attribute: str, value: Any) -> None:
        """Update an instance attribute after validation."""

        allowed = {
            "name",
            "manufacturer",
            "temperature",
            "status",
            "configuration",
            "tags",
        }

        if attribute not in allowed:
            raise ValidationError(
                f"Attribute '{attribute}' cannot be modified."
            )

        if attribute == "temperature":
            if not isinstance(value, (int, float)):
                raise ValidationError("Temperature must be numeric.")
            if not -50 <= value <= 150:
                raise ValidationError("Temperature is outside the valid range.")

        elif attribute == "status":
            if isinstance(value, str):
                try:
                    value = DeviceStatus(value)
                except ValueError as exc:
                    raise ValidationError("Unknown device status.") from exc

            if not isinstance(value, DeviceStatus):
                raise ValidationError("Invalid device status.")

        elif attribute == "configuration":
            if not isinstance(value, dict):
                raise ValidationError("Configuration must be a dictionary.")

        elif attribute == "tags":
            if not isinstance(value, list) or not all(
                isinstance(tag, str) for tag in value
            ):
                raise ValidationError("Tags must be a list of strings.")

        elif attribute in {"name", "manufacturer"}:
            if not isinstance(value, str) or not value.strip():
                raise ValidationError("Text attributes cannot be empty.")
            value = value.strip()

        setattr(self, attribute, value)

    def get_instance_attributes(self) -> dict[str, Any]:
        """Return attributes stored directly on this object."""

        result = {}

        for key, value in vars(self).items():
            if isinstance(value, Enum):
                result[key] = value.value
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value

        return result

    def describe(self) -> None:
        print(f"\nDevice: {self.name}")
        print(f"ID: {self.device_id}")
        print(f"Manufacturer: {self.manufacturer}")
        print(f"Temperature: {self.temperature} C")
        print(f"Status: {self.status.value}")
        print(f"Category (class attribute): {self.category}")

    def is_overheating(self, threshold: float = 70.0) -> bool:
        return self.temperature >= threshold

    def reset_temperature(self) -> None:
        self.temperature = 25.0


class DeviceRegistry:
    """Manage multiple independent Device instances."""

    def __init__(self) -> None:
        self.devices: dict[str, Device] = {}

    def register(self, device: Device) -> None:
        if device.device_id in self.devices:
            raise ValidationError("Device ID already exists.")

        self.devices[device.device_id] = device
        logger.info("Registered device %s", device.device_id)

    def get(self, device_id: str) -> Device:
        try:
            return self.devices[device_id]
        except KeyError as exc:
            raise ValidationError("Device does not exist.") from exc

    def update(
        self,
        device_id: str,
        attribute: str,
        value: Any
    ) -> None:
        device = self.get(device_id)
        device.update_attribute(attribute, value)

    def find_overheating(
        self,
        threshold: float = 70.0
    ) -> list[Device]:
        return [
            device
            for device in self.devices.values()
            if device.is_overheating(threshold)
        ]

    def report(self) -> list[dict[str, Any]]:
        return [
            device.get_instance_attributes()
            for device in self.devices.values()
        ]

    def save_json(self, filename: str) -> None:
        """Persist instance-specific state as JSON."""

        path = Path(filename)

        records = self.report()

        try:
            path.write_text(
                json.dumps(records, indent=4),
                encoding="utf-8"
            )
        except OSError as exc:
            logger.error("Unable to save registry: %s", exc)
            raise

    @classmethod
    def load_json(cls, filename: str) -> DeviceRegistry:
        """Reconstruct independent objects from persisted attributes."""

        path = Path(filename)

        try:
            records = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValidationError("Unable to load device data.") from exc

        if not isinstance(records, list):
            raise ValidationError("Invalid registry format.")

        registry = cls()

        for record in records:
            if not isinstance(record, dict):
                raise ValidationError("Invalid device record.")

            record = record.copy()
            record["status"] = DeviceStatus(record["status"])
            record["created_at"] = datetime.fromisoformat(
                record["created_at"]
            )

            registry.register(Device(**record))

        return registry


def demonstrate_instance_attributes() -> None:
    print("=" * 65)
    print("INSTANCE ATTRIBUTES: OBJECT STATE MANAGEMENT")
    print("=" * 65)

    # Creating independent objects.
    router = Device(
        device_id="DEV-001",
        name="Core Router",
        manufacturer="Cisco",
        temperature=42.5,
        configuration={"ip": "192.168.1.1", "ports": 24},
        tags=["network", "critical"]
    )

    firewall = Device(
        device_id="DEV-002",
        name="Enterprise Firewall",
        manufacturer="Fortinet",
        temperature=78.0,
        configuration={"ip": "192.168.1.2", "ports": 8},
        tags=["security", "critical"]
    )

    print("\n1. Independent instance attributes")

    router.describe()
    firewall.describe()

    print("\n2. Inspecting instance dictionaries")

    print("Router:", vars(router))
    print("Firewall:", vars(firewall))

    print("\n3. Changing one object's attribute")

    router.temperature = 35.0

    print("Router temperature:", router.temperature)
    print("Firewall temperature:", firewall.temperature)

    assert router.temperature != firewall.temperature

    print("\n4. Shared class attributes")

    print("Router category:", router.category)
    print("Firewall category:", firewall.category)

    print("\n5. Instance attribute shadowing")

    router.category = "Core Infrastructure"

    print("Router category:", router.category)
    print("Firewall category:", firewall.category)
    print("Class category:", Device.category)

    assert router.category != firewall.category
    assert Device.category == "Network Equipment"

    print("\n6. Dynamic instance attributes")

    router.location = "Lucknow Data Centre"
    print("Router location:", router.location)
    print("Firewall has location:", hasattr(firewall, "location"))

    print("\n7. Controlled attribute modification")

    router.update_attribute("temperature", 38.0)
    router.update_attribute("status", "maintenance")

    print("Updated temperature:", router.temperature)
    print("Updated status:", router.status.value)

    print("\n8. Invalid attribute modification")

    try:
        router.update_attribute("temperature", 250)
    except ValidationError as exc:
        print("Validation prevented update:", exc)

    print("\n9. Registry and filtering")

    registry = DeviceRegistry()
    registry.register(router)
    registry.register(firewall)

    overheating = registry.find_overheating()

    for device in overheating:
        print(
            f"Overheating: {device.name}, "
            f"{device.temperature} C"
        )

    print("\n10. Serialization")

    output_file = "device_instances.json"
    registry.save_json(output_file)

    restored = DeviceRegistry.load_json(output_file)

    for record in restored.report():
        print(json.dumps(record, indent=2))

    print("\n11. Independence verification")

    restored_router = restored.get("DEV-001")
    restored_firewall = restored.get("DEV-002")

    restored_router.configuration["ports"] = 48

    assert restored_firewall.configuration["ports"] == 8

    print("Independent nested instance attributes verified.")

    print("\n12. Exception handling")

    try:
        registry.register(router)
    except ValidationError as exc:
        print("Duplicate registration rejected:", exc)

    try:
        registry.get("DEV-999")
    except ValidationError as exc:
        print("Lookup failure handled:", exc)

    print("\nAll instance attribute demonstrations completed.")


if __name__ == "__main__":
    demonstrate_instance_attributes()
