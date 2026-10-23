from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from statistics import mean
from typing import Callable, Iterable, TypeVar


T = TypeVar("T")
U = TypeVar("U")


def map_items(items: Iterable[T], transform: Callable[[T], U]) -> list[U]:
    """Return one transformed value for every input value."""
    return list(map(transform, items))


def filter_items(items: Iterable[T], predicate: Callable[[T], bool]) -> list[T]:
    """Return only values satisfying the predicate."""
    return list(filter(predicate, items))


def reduce_items(
    items: Iterable[T],
    combine: Callable[[U, T], U],
    initial: U,
) -> U:
    """Fold an iterable into one accumulated result."""
    return reduce(combine, items, initial)


@dataclass(frozen=True)
class Employee:
    employee_id: int
    name: str
    department: str
    salary: float
    active: bool


def validate_employee(employee: Employee) -> None:
    if employee.employee_id <= 0:
        raise ValueError("employee_id must be positive")
    if not employee.name.strip():
        raise ValueError("employee name cannot be empty")
    if employee.salary < 0:
        raise ValueError("salary cannot be negative")
    if not employee.department.strip():
        raise ValueError("department cannot be empty")


def salary_projection(employee: Employee) -> float:
    # map() transforms each employee independently.
    return round(employee.salary * 1.08, 2)


def is_eligible(employee: Employee) -> bool:
    # filter() selects records without changing their structure.
    return employee.active and employee.salary >= 50000


def total_salary(total: float, employee: Employee) -> float:
    # reduce() combines many employee records into one aggregate value.
    return total + employee.salary


def build_department_report(employees: list[Employee]) -> dict[str, object]:
    for employee in employees:
        validate_employee(employee)

    active_employees = filter_items(
        employees,
        lambda employee: employee.active,
    )

    eligible_employees = filter_items(
        active_employees,
        is_eligible,
    )

    projected_salaries = map_items(
        eligible_employees,
        salary_projection,
    )

    total_current_salary = reduce_items(
        eligible_employees,
        total_salary,
        0.0,
    )

    total_projected_salary = reduce_items(
        projected_salaries,
        lambda total, salary: total + salary,
        0.0,
    )

    department_names = map_items(
        eligible_employees,
        lambda employee: employee.department,
    )

    unique_departments = set(department_names)

    average_salary = (
        total_current_salary / len(eligible_employees)
        if eligible_employees
        else 0.0
    )

    return {
        "eligible_employees": eligible_employees,
        "projected_salaries": projected_salaries,
        "departments": sorted(unique_departments),
        "total_current_salary": round(total_current_salary, 2),
        "total_projected_salary": round(total_projected_salary, 2),
        "average_salary": round(average_salary, 2),
    }


def demonstrate_composition(values: list[int]) -> dict[str, object]:
    # map -> filter -> reduce is a common functional data-processing pipeline.
    doubled = map_items(values, lambda value: value * 2)
    positive = filter_items(doubled, lambda value: value > 0)
    total = reduce_items(positive, lambda accumulator, value: accumulator + value, 0)

    return {
        "input": values,
        "mapped": doubled,
        "filtered": positive,
        "reduced": total,
    }


def main() -> None:
    employees = [
        Employee(101, "Asha", "Engineering", 72000, True),
        Employee(102, "Rahul", "Finance", 48000, True),
        Employee(103, "Meera", "Engineering", 81000, True),
        Employee(104, "Kabir", "Operations", 65000, False),
        Employee(105, "Nisha", "Finance", 59000, True),
    ]

    report = build_department_report(employees)

    print("Eligible employees:")
    for employee in report["eligible_employees"]:
        print(f"  {employee.employee_id}: {employee.name}")

    print("\nProjected salaries:")
    for employee, projected in zip(
        report["eligible_employees"],
        report["projected_salaries"],
    ):
        print(f"  {employee.name}: {projected:.2f}")

    print("\nDepartments:", ", ".join(report["departments"]))
    print("Current salary total:", report["total_current_salary"])
    print("Projected salary total:", report["total_projected_salary"])
    print("Average eligible salary:", report["average_salary"])

    print("\nPipeline:")
    print(demonstrate_composition([-4, -2, 1, 3, 5]))

    # Empty input is valid for all three operations when an explicit
    # initial value is supplied to reduce().
    print("\nEmpty reduce result:", reduce_items([], lambda a, b: a + b, 0))

    # A generator demonstrates that map(), filter(), and reduce() work
    # naturally with lazy iterable sources without requiring a list first.
    generated_values = (value for value in range(1, 6))
    squared = map(lambda value: value * value, generated_values)
    even_squares = filter(lambda value: value % 2 == 0, squared)
    generated_total = reduce(lambda total, value: total + value, even_squares, 0)
    print("Reduced generator result:", generated_total)


if __name__ == "__main__":
    main()
