"""
PYTHON INHERITANCE
A complete executable demonstration of fundamental and advanced
object-oriented inheritance concepts using an employee payroll system.

Demonstrates:
- Single inheritance
- Multilevel inheritance
- Hierarchical inheritance
- Multiple inheritance
- Hybrid inheritance
- Abstract base classes
- Method overriding
- Method overloading alternatives
- super()
- MRO (Method Resolution Order)
- Polymorphism
- Mixins
- Encapsulation
- isinstance() and issubclass()
- Composition versus inheritance
- Validation and exception handling
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class EmploymentType(Enum):
    PERMANENT = "permanent"
    CONTRACT = "contract"
    INTERN = "intern"


class PayrollError(Exception):
    """Base exception for payroll operations."""


class ValidationError(PayrollError):
    """Raised when employee information is invalid."""


class EmployeeNotFoundError(PayrollError):
    """Raised when an employee cannot be found."""


@dataclass
class Employee(ABC):
    employee_id: int
    name: str
    department: str
    employment_type: EmploymentType
    _active: bool = field(default=True, repr=False)

    def __post_init__(self):
        if self.employee_id <= 0:
            raise ValidationError("Employee ID must be positive.")

        if not self.name.strip():
            raise ValidationError("Employee name cannot be empty.")

        if not self.department.strip():
            raise ValidationError("Department cannot be empty.")

    @abstractmethod
    def calculate_salary(self) -> float:
        """Every concrete employee must implement salary calculation."""

    def deactivate(self):
        self._active = False

    @property
    def is_active(self):
        return self._active

    def get_details(self):
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "department": self.department,
            "employment_type": self.employment_type.value,
            "active": self.is_active,
            "salary": round(self.calculate_salary(), 2),
        }

    def __str__(self):
        return (
            f"{self.name} | {self.department} | "
            f"Salary: {self.calculate_salary():.2f}"
        )


# Single inheritance
@dataclass
class PermanentEmployee(Employee):
    monthly_salary: float = 0.0
    annual_bonus: float = 0.0

    def __post_init__(self):
        super().__post_init__()

        if self.monthly_salary < 0 or self.annual_bonus < 0:
            raise ValidationError("Salary and bonus cannot be negative.")

    def calculate_salary(self):
        return self.monthly_salary + self.annual_bonus / 12


# Multilevel inheritance
@dataclass
class SeniorEmployee(PermanentEmployee):
    leadership_allowance: float = 0.0

    def __post_init__(self):
        super().__post_init__()

        if self.leadership_allowance < 0:
            raise ValidationError("Allowance cannot be negative.")

    def calculate_salary(self):
        return super().calculate_salary() + self.leadership_allowance


# Hierarchical inheritance
@dataclass
class ContractEmployee(Employee):
    hourly_rate: float = 0.0
    hours_worked: float = 0.0

    def __post_init__(self):
        super().__post_init__()

        if self.hourly_rate < 0:
            raise ValidationError("Hourly rate cannot be negative.")

        if not 0 <= self.hours_worked <= 744:
            raise ValidationError("Invalid monthly working hours.")

    def calculate_salary(self):
        return self.hourly_rate * self.hours_worked


@dataclass
class InternEmployee(Employee):
    monthly_stipend: float = 0.0

    def __post_init__(self):
        super().__post_init__()

        if self.monthly_stipend < 0:
            raise ValidationError("Stipend cannot be negative.")

    def calculate_salary(self):
        return self.monthly_stipend


# Multiple inheritance through mixins
class TaxableMixin:
    TAX_RATE = 0.10

    def calculate_tax(self, salary):
        if salary < 0:
            raise ValidationError("Salary cannot be negative.")

        return salary * self.TAX_RATE


class AuditableMixin:
    def audit_record(self):
        return {
            "class": type(self).__name__,
            "employee_id": self.employee_id,
            "mro": [
                cls.__name__ for cls in type(self).__mro__
            ],
        }


@dataclass
class TaxablePermanentEmployee(
    TaxableMixin,
    AuditableMixin,
    PermanentEmployee
):
    def calculate_net_salary(self):
        gross = self.calculate_salary()
        return gross - self.calculate_tax(gross)


# Hybrid inheritance
@dataclass
class DepartmentManager(
    TaxableMixin,
    AuditableMixin,
    SeniorEmployee
):
    management_bonus: float = 0.0

    def __post_init__(self):
        super().__post_init__()

        if self.management_bonus < 0:
            raise ValidationError("Management bonus cannot be negative.")

    def calculate_salary(self):
        return super().calculate_salary() + self.management_bonus

    def calculate_net_salary(self):
        gross = self.calculate_salary()
        return gross - self.calculate_tax(gross)


# Composition: a separate object handles payroll calculations.
@dataclass
class PayrollPolicy:
    deduction_rate: float = 0.10

    def __post_init__(self):
        if not 0 <= self.deduction_rate <= 1:
            raise ValidationError("Invalid deduction rate.")

    def net_salary(self, employee: Employee):
        return employee.calculate_salary() * (
            1 - self.deduction_rate
        )


class PayrollSystem:
    def __init__(self, policy: PayrollPolicy):
        self.policy = policy
        self._employees: dict[int, Employee] = {}

    def register(self, employee: Employee):
        if employee.employee_id in self._employees:
            raise ValidationError("Duplicate employee ID.")

        self._employees[employee.employee_id] = employee

    def get_employee(self, employee_id: int):
        try:
            return self._employees[employee_id]
        except KeyError as exc:
            raise EmployeeNotFoundError(
                f"Employee {employee_id} not found."
            ) from exc

    def process_payroll(self):
        results = []

        for employee in self._employees.values():
            if not employee.is_active:
                continue

            gross = employee.calculate_salary()
            net = self.policy.net_salary(employee)

            results.append({
                "employee_id": employee.employee_id,
                "name": employee.name,
                "gross_salary": round(gross, 2),
                "net_salary": round(net, 2),
            })

        return results

    def department_report(self):
        totals = {}

        for employee in self._employees.values():
            if not employee.is_active:
                continue

            totals[employee.department] = (
                totals.get(employee.department, 0)
                + employee.calculate_salary()
            )

        return {
            department: round(total, 2)
            for department, total in totals.items()
        }


def demonstrate_inheritance():
    print("\n=== PYTHON INHERITANCE DEMONSTRATION ===")

    permanent = PermanentEmployee(
        101, "Aarav", "Engineering",
        EmploymentType.PERMANENT,
        monthly_salary=70000,
        annual_bonus=120000
    )

    senior = SeniorEmployee(
        102, "Meera", "Engineering",
        EmploymentType.PERMANENT,
        monthly_salary=100000,
        annual_bonus=240000,
        leadership_allowance=15000
    )

    contractor = ContractEmployee(
        103, "Rohan", "Operations",
        EmploymentType.CONTRACT,
        hourly_rate=800,
        hours_worked=160
    )

    intern = InternEmployee(
        104, "Priya", "Research",
        EmploymentType.INTERN,
        monthly_stipend=25000
    )

    taxable = TaxablePermanentEmployee(
        105, "Ananya", "Finance",
        EmploymentType.PERMANENT,
        monthly_salary=85000,
        annual_bonus=60000
    )

    manager = DepartmentManager(
        106, "Vikram", "Engineering",
        EmploymentType.PERMANENT,
        monthly_salary=120000,
        annual_bonus=300000,
        leadership_allowance=20000,
        management_bonus=15000
    )

    employees: list[Employee] = [
        permanent,
        senior,
        contractor,
        intern,
        taxable,
        manager,
    ]

    # Polymorphism: the same method behaves differently
    # depending on the actual employee subclass.
    for employee in employees:
        print(employee)

    print("\n=== MULTIPLE INHERITANCE ===")
    print("Taxable salary:", taxable.calculate_salary())
    print("Net salary:", taxable.calculate_net_salary())
    print("Audit:", taxable.audit_record())

    print("\n=== HYBRID INHERITANCE ===")
    print("Manager gross:", manager.calculate_salary())
    print("Manager net:", manager.calculate_net_salary())
    print("Manager MRO:")

    for cls in DepartmentManager.__mro__:
        print(" ", cls.__name__)

    print("\n=== TYPE RELATIONSHIPS ===")
    print("Senior is Permanent:",
          isinstance(senior, PermanentEmployee))

    print("Permanent is Employee:",
          isinstance(permanent, Employee))

    print("Employee is abstract:",
          Employee.__abstractmethods__)

    print("Senior subclass of Employee:",
          issubclass(SeniorEmployee, Employee))

    print("\n=== COMPOSITION ===")
    policy = PayrollPolicy(deduction_rate=0.12)
    print("Composed policy net salary:",
          policy.net_salary(permanent))


def demonstrate_payroll():
    print("\n=== PAYROLL SYSTEM ===")

    system = PayrollSystem(
        PayrollPolicy(deduction_rate=0.12)
    )

    employees = [
        PermanentEmployee(
            201, "Kabir", "Technology",
            EmploymentType.PERMANENT,
            90000, 120000
        ),
        ContractEmployee(
            202, "Sana", "Technology",
            EmploymentType.CONTRACT,
            600, 150
        ),
        InternEmployee(
            203, "Dev", "Research",
            EmploymentType.INTERN,
            20000
        ),
    ]

    for employee in employees:
        system.register(employee)

    for record in system.process_payroll():
        print(record)

    print("\nDepartment totals:")
    print(system.department_report())

    system.get_employee(203).deactivate()

    print("\nAfter employee deactivation:")
    print(system.process_payroll())

    try:
        system.register(employees[0])
    except ValidationError as error:
        print("Expected validation error:", error)

    try:
        system.get_employee(999)
    except EmployeeNotFoundError as error:
        print("Expected lookup error:", error)


def run_tests():
    permanent = PermanentEmployee(
        1, "Test", "IT",
        EmploymentType.PERMANENT,
        50000, 12000
    )

    assert permanent.calculate_salary() == 51000

    senior = SeniorEmployee(
        2, "Senior", "IT",
        EmploymentType.PERMANENT,
        50000, 12000, 5000
    )

    assert senior.calculate_salary() == 56000
    assert isinstance(senior, Employee)
    assert issubclass(SeniorEmployee, PermanentEmployee)

    contractor = ContractEmployee(
        3, "Contractor", "IT",
        EmploymentType.CONTRACT,
        500, 100
    )

    assert contractor.calculate_salary() == 50000

    taxable = TaxablePermanentEmployee(
        4, "Taxable", "Finance",
        EmploymentType.PERMANENT,
        50000, 12000
    )

    assert taxable.calculate_net_salary() == 45900

    manager = DepartmentManager(
        5, "Manager", "IT",
        EmploymentType.PERMANENT,
        100000, 120000, 10000, 5000
    )

    assert manager.calculate_salary() == 125000
    assert manager.calculate_net_salary() == 112500

    try:
        PermanentEmployee(
            0, "Invalid", "IT",
            EmploymentType.PERMANENT,
            50000, 0
        )
    except ValidationError:
        pass
    else:
        raise AssertionError("Invalid employee was accepted.")

    try:
        Employee(
            6, "Abstract", "IT",
            EmploymentType.PERMANENT
        )
    except TypeError:
        pass
    else:
        raise AssertionError("Abstract class was instantiated.")

    print("\nAll automated assertions passed.")


def main():
    demonstrate_inheritance()
    demonstrate_payroll()
    run_tests()


if __name__ == "__main__":
    main()
