"""
CLASS METHODS
A practical implementation of class-level behavior, alternative constructors,
shared class state, inheritance-aware factories, and object registries.

Run:
    python class_methods.py
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import ClassVar
from uuid import uuid4


class DomainError(Exception):
    """Raised when a domain operation violates a business rule."""


@dataclass
class Employee:
    employee_id: str
    name: str
    department: str
    salary: Decimal

    _registry: ClassVar[dict[str, "Employee"]] = {}
    _minimum_salary: ClassVar[Decimal] = Decimal("15000")
    _created_count: ClassVar[int] = 0

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        self.department = self.department.strip()

        if not self.name:
            raise ValueError("Employee name cannot be empty.")

        if not self.department:
            raise ValueError("Department cannot be empty.")

        if self.salary < self._minimum_salary:
            raise ValueError("Salary is below the permitted minimum.")

        if self.employee_id in self._registry:
            raise DomainError("Employee ID already exists.")

        type(self)._registry[self.employee_id] = self
        type(self)._created_count += 1

    # Class method: receives the class rather than an instance.
    @classmethod
    def from_record(cls, record: dict) -> "Employee":
        """Alternative constructor using a dictionary."""

        required = {"employee_id", "name", "department", "salary"}

        if not isinstance(record, dict):
            raise TypeError("Record must be a dictionary.")

        missing = required - record.keys()

        if missing:
            raise ValueError(f"Missing fields: {sorted(missing)}")

        try:
            salary = Decimal(str(record["salary"]))
        except (InvalidOperation, ValueError):
            raise ValueError("Salary must be a valid decimal.") from None

        return cls(
            employee_id=str(record["employee_id"]).strip(),
            name=str(record["name"]),
            department=str(record["department"]),
            salary=salary,
        )

    @classmethod
    def from_csv_line(cls, line: str) -> "Employee":
        """Alternative constructor using comma-separated input."""

        parts = [part.strip() for part in line.split(",")]

        if len(parts) != 4:
            raise ValueError(
                "Expected employee_id,name,department,salary."
            )

        return cls.from_record({
            "employee_id": parts[0],
            "name": parts[1],
            "department": parts[2],
            "salary": parts[3],
        })

    @classmethod
    def find_by_id(cls, employee_id: str) -> "Employee | None":
        """Retrieve an employee from the class registry."""

        return cls._registry.get(employee_id)

    @classmethod
    def get_all(cls) -> list["Employee"]:
        return list(cls._registry.values())

    @classmethod
    def count(cls) -> int:
        return len(cls._registry)

    @classmethod
    def change_minimum_salary(cls, amount: Decimal) -> None:
        """Update a class-level business policy."""

        amount = Decimal(str(amount))

        if amount <= 0:
            raise ValueError("Minimum salary must be positive.")

        cls._minimum_salary = amount

    @classmethod
    def department_report(cls) -> dict[str, dict]:
        """Aggregate employee information by department."""

        report: dict[str, dict] = {}

        for employee in cls._registry.values():
            department = employee.department

            if department not in report:
                report[department] = {
                    "employees": 0,
                    "total_salary": Decimal("0"),
                }

            report[department]["employees"] += 1
            report[department]["total_salary"] += employee.salary

        return report

    @classmethod
    def clear_registry(cls) -> None:
        """Reset the registry for isolated demonstrations."""

        cls._registry.clear()
        cls._created_count = 0

    @staticmethod
    def calculate_annual_salary(monthly_salary: Decimal) -> Decimal:
        """A static method does not receive cls or self."""

        if monthly_salary < 0:
            raise ValueError("Salary cannot be negative.")

        return monthly_salary * 12

    def give_raise(self, percentage: Decimal) -> None:
        """Instance method: modifies one employee."""

        if percentage <= 0 or percentage > 50:
            raise ValueError("Raise must be between 0 and 50 percent.")

        self.salary *= Decimal("1") + percentage / Decimal("100")


class ContractEmployee(Employee):
    """Specialized employee with inheritance-aware construction."""

    def __init__(
        self,
        employee_id: str,
        name: str,
        department: str,
        salary: Decimal,
        contract_months: int,
    ) -> None:

        if not 1 <= contract_months <= 60:
            raise ValueError("Contract duration must be 1-60 months.")

        self.contract_months = contract_months

        super().__init__(
            employee_id,
            name,
            department,
            salary,
        )

    @classmethod
    def from_record(cls, record: dict) -> "ContractEmployee":
        """The inherited factory constructs the requested subclass."""

        employee = super().from_record(
            {
                key: record[key]
                for key in ("employee_id", "name", "department", "salary")
            }
        )

        # The base factory invokes cls(...), so this subclass requires
        # its additional constructor argument.
        # This override provides the correct subclass construction.
        Employee._registry.pop(employee.employee_id, None)
        Employee._created_count -= 1

        return cls(
            employee.employee_id,
            employee.name,
            employee.department,
            employee.salary,
            int(record["contract_months"]),
        )


def demonstrate_class_methods() -> None:
    Employee.clear_registry()

    print("\n1. Alternative constructor")

    first = Employee.from_record({
        "employee_id": "EMP101",
        "name": "Ananya Sharma",
        "department": "Engineering",
        "salary": "65000",
    })

    second = Employee.from_csv_line(
        "EMP102,Rahul Verma,Security,72000"
    )

    print(first)
    print(second)

    print("\n2. Class-level registry")

    print("Employee count:", Employee.count())
    print("Lookup:", Employee.find_by_id("EMP101"))

    print("\n3. Shared class-level policy")

    Employee.change_minimum_salary(Decimal("20000"))
    print("Minimum salary:", Employee._minimum_salary)

    try:
        Employee.from_record({
            "employee_id": "EMP103",
            "name": "Test Employee",
            "department": "Testing",
            "salary": "18000",
        })
    except ValueError as error:
        print("Validation:", error)

    print("\n4. Inheritance-aware factory")

    contractor = ContractEmployee.from_record({
        "employee_id": "CON201",
        "name": "Meera Singh",
        "department": "Operations",
        "salary": "45000",
        "contract_months": 12,
    })

    print(type(contractor).__name__)
    print("Contract:", contractor.contract_months, "months")

    print("\n5. Instance-level operation")

    first.give_raise(Decimal("10"))
    print("Updated salary:", first.salary)

    print("\n6. Static method")

    annual = Employee.calculate_annual_salary(
        Decimal("65000")
    )
    print("Annual salary:", annual)

    print("\n7. Department aggregation")

    for department, details in Employee.department_report().items():
        print(department, details)

    print("\n8. Class-level versus instance-level behavior")

    print("Registry entries:", Employee.count())
    print("Created count:", Employee._created_count)

    print("\n9. Edge case")

    try:
        Employee.from_csv_line("INVALID,RECORD")
    except ValueError as error:
        print("Rejected:", error)

    print("\nExecution completed.")


if __name__ == "__main__":
    demonstrate_class_methods()
