"""
Reading and Writing CSV Files
Python 3.10+

Demonstrates:
- CSV reading and writing
- csv.reader and csv.writer
- DictReader and DictWriter
- Custom delimiters and quoting
- Header and schema validation
- Data cleaning and type conversion
- Streaming large files
- Atomic file writing
- Error handling
- Duplicate detection
- Aggregation and reporting
- CSV security and formula injection prevention
- Automated tests
"""

from __future__ import annotations

import csv
import io
import os
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Iterator


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "csv_data"

INPUT_FILE = DATA_DIR / "employees_input.csv"
OUTPUT_FILE = DATA_DIR / "employees_processed.csv"
REPORT_FILE = DATA_DIR / "department_report.csv"

EXPECTED_HEADERS = [
    "employee_id",
    "name",
    "department",
    "salary",
    "active",
]


# ---------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------

class CSVProcessingError(Exception):
    """Base exception for CSV processing."""


class CSVSchemaError(CSVProcessingError):
    """Raised when CSV columns do not match the expected schema."""


class CSVRowError(CSVProcessingError):
    """Raised when a CSV record contains invalid values."""


# ---------------------------------------------------------
# Domain model
# ---------------------------------------------------------

@dataclass(frozen=True)
class Employee:
    employee_id: int
    name: str
    department: str
    salary: Decimal
    active: bool


@dataclass
class ProcessingReport:
    total_rows: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0
    duplicate_rows: int = 0
    total_salary: Decimal = Decimal("0")


# ---------------------------------------------------------
# Validation and conversion
# ---------------------------------------------------------

def parse_employee(row: dict[str, str], line_number: int) -> Employee:
    try:
        employee_id = int(row["employee_id"].strip())

        name = row["name"].strip()
        department = row["department"].strip()

        salary = Decimal(row["salary"].strip())

        active_text = row["active"].strip().lower()

        if employee_id <= 0:
            raise ValueError("Employee ID must be positive")

        if not name:
            raise ValueError("Employee name cannot be empty")

        if not department:
            raise ValueError("Department cannot be empty")

        if not salary.is_finite() or salary < 0:
            raise ValueError("Salary must be a finite non-negative number")

        if active_text not in {"true", "false", "1", "0", "yes", "no"}:
            raise ValueError("Invalid active value")

        active = active_text in {"true", "1", "yes"}

        return Employee(
            employee_id=employee_id,
            name=name,
            department=department,
            salary=salary,
            active=active,
        )

    except (ValueError, InvalidOperation, KeyError, AttributeError) as exc:
        raise CSVRowError(
            f"Invalid data at line {line_number}: {exc}"
        ) from exc


def validate_headers(headers: list[str] | None) -> None:
    if headers is None:
        raise CSVSchemaError("CSV file is empty or has no header")

    normalized = [header.strip() for header in headers]

    if len(normalized) != len(set(normalized)):
        raise CSVSchemaError("Duplicate column names detected")

    if normalized != EXPECTED_HEADERS:
        raise CSVSchemaError(
            f"Expected columns {EXPECTED_HEADERS}, received {normalized}"
        )


# ---------------------------------------------------------
# CSV generation
# ---------------------------------------------------------

def create_sample_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    records = [
        [101, "Alice Johnson", "Engineering", "85000.50", "true"],
        [102, "Bob Smith", "Finance", "72000.00", "true"],
        [103, "Charlie Brown", "Engineering", "91000.00", "yes"],
        [104, "Diana Miller", "HR", "65000.75", "false"],
        [105, "Eva Wilson", "Finance", "78000.25", "true"],
        [106, "Frank Thomas", "Engineering", "88000.00", "true"],
        [107, "Grace Lee", "HR", "69000.00", "1"],
        [108, "Henry Clark", "Finance", "invalid", "true"],
        [101, "Duplicate Employee", "Engineering", "50000", "true"],
        [109, "Ivy Davis", "Marketing", "-500", "false"],
    ]

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)

        writer.writerow(EXPECTED_HEADERS)
        writer.writerows(records)


# ---------------------------------------------------------
# CSV reading using DictReader
# ---------------------------------------------------------

def read_employees(
    path: Path,
    report: ProcessingReport,
) -> Iterator[Employee]:

    seen_ids: set[int] = set()

    try:
        with path.open(
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as file:

            reader = csv.DictReader(file)

            validate_headers(reader.fieldnames)

            for line_number, row in enumerate(reader, start=2):
                report.total_rows += 1

                if None in row or any(value is None for value in row.values()):
                    report.invalid_rows += 1
                    print(f"Rejected line {line_number}: malformed column count")
                    continue

                try:
                    employee = parse_employee(row, line_number)

                    if employee.employee_id in seen_ids:
                        report.duplicate_rows += 1
                        print(
                            f"Rejected line {line_number}: duplicate employee ID"
                        )
                        continue

                    seen_ids.add(employee.employee_id)

                    report.valid_rows += 1
                    report.total_salary += employee.salary

                    yield employee

                except CSVRowError as exc:
                    report.invalid_rows += 1
                    print(exc)

    except FileNotFoundError as exc:
        raise CSVProcessingError(
            f"Input file does not exist: {path}"
        ) from exc

    except UnicodeDecodeError as exc:
        raise CSVProcessingError(
            "Input file is not valid UTF-8 text"
        ) from exc

    except csv.Error as exc:
        raise CSVProcessingError(
            f"CSV parsing failed: {exc}"
        ) from exc


# ---------------------------------------------------------
# CSV writing using DictWriter
# ---------------------------------------------------------

def spreadsheet_safe(value: object) -> str:
    """
    Prevent spreadsheet formula injection.

    Values beginning with formula-triggering characters are
    prefixed with an apostrophe before export.
    """
    text = str(value)

    if text.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")):
        return "'" + text

    return text


def employee_to_row(employee: Employee) -> dict[str, str]:
    return {
        "employee_id": str(employee.employee_id),
        "name": spreadsheet_safe(employee.name),
        "department": spreadsheet_safe(employee.department),
        "salary": str(employee.salary.quantize(Decimal("0.01"))),
        "active": str(employee.active).lower(),
    }


def write_employees_atomically(
    path: Path,
    employees: Iterable[Employee],
) -> None:

    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:

            temporary_path = Path(file.name)

            writer = csv.DictWriter(
                file,
                fieldnames=EXPECTED_HEADERS,
                quoting=csv.QUOTE_MINIMAL,
                extrasaction="raise",
            )

            writer.writeheader()

            for employee in employees:
                writer.writerow(employee_to_row(employee))

            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary_path, path)

    except OSError as exc:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()

        raise CSVProcessingError(
            f"Could not write CSV file: {exc}"
        ) from exc


# ---------------------------------------------------------
# Aggregation
# ---------------------------------------------------------

def generate_department_report(
    employees: Iterable[Employee],
    output_path: Path,
) -> list[dict[str, str]]:

    departments: dict[str, dict[str, Decimal | int]] = defaultdict(
        lambda: {
            "employee_count": 0,
            "total_salary": Decimal("0"),
        }
    )

    for employee in employees:
        if not employee.active:
            continue

        department = departments[employee.department]

        department["employee_count"] = (
            int(department["employee_count"]) + 1
        )

        department["total_salary"] = (
            Decimal(department["total_salary"]) + employee.salary
        )

    report_rows = []

    for department_name, values in sorted(departments.items()):
        count = int(values["employee_count"])
        total = Decimal(values["total_salary"])

        report_rows.append({
            "department": spreadsheet_safe(department_name),
            "employee_count": str(count),
            "total_salary": str(total.quantize(Decimal("0.01"))),
            "average_salary": str(
                (total / count).quantize(Decimal("0.01"))
            ),
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        headers = [
            "department",
            "employee_count",
            "total_salary",
            "average_salary",
        ]

        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(report_rows)

    return report_rows


# ---------------------------------------------------------
# Fundamental CSV reading and writing
# ---------------------------------------------------------

def demonstrate_basic_csv() -> None:
    data = [
        ["Product ID", "Product Name", "Price"],
        [1, "Laptop, Professional", "85000"],
        [2, "Wireless Mouse", "1200"],
        [3, 'Monitor "Ultra"', "18000"],
    ]

    buffer = io.StringIO(newline="")

    writer = csv.writer(buffer)
    writer.writerows(data)

    buffer.seek(0)

    reader = csv.reader(buffer)

    print("\nBasic CSV reader:")

    for row in reader:
        print(row)


# ---------------------------------------------------------
# Custom delimiter demonstration
# ---------------------------------------------------------

def demonstrate_custom_delimiter() -> None:
    data = [
        {"name": "Alice", "department": "Engineering"},
        {"name": "Bob", "department": "Finance"},
    ]

    buffer = io.StringIO(newline="")

    writer = csv.DictWriter(
        buffer,
        fieldnames=["name", "department"],
        delimiter=";",
    )

    writer.writeheader()
    writer.writerows(data)

    print("\nSemicolon-delimited CSV:")
    print(buffer.getvalue())


# ---------------------------------------------------------
# Automated validation tests
# ---------------------------------------------------------

def run_tests() -> None:
    employee = Employee(
        1,
        "Test User",
        "Engineering",
        Decimal("50000.00"),
        True,
    )

    assert parse_employee(
        {
            "employee_id": "1",
            "name": "Test User",
            "department": "Engineering",
            "salary": "50000",
            "active": "yes",
        },
        2,
    ) == employee

    assert spreadsheet_safe("Normal text") == "Normal text"
    assert spreadsheet_safe("=SUM(A1:A5)") == "'=SUM(A1:A5)"

    try:
        parse_employee(
            {
                "employee_id": "0",
                "name": "Invalid",
                "department": "Engineering",
                "salary": "100",
                "active": "true",
            },
            3,
        )
        raise AssertionError("Invalid employee ID was accepted")
    except CSVRowError:
        pass

    try:
        validate_headers(["name", "name"])
        raise AssertionError("Duplicate headers were accepted")
    except CSVSchemaError:
        pass

    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(["A,B", 'C"D', "Line 1\nLine 2"])

    buffer.seek(0)
    row = next(csv.reader(buffer))

    assert row == ["A,B", 'C"D', "Line 1\nLine 2"]

    print("\nAll tests passed.")


# ---------------------------------------------------------
# Main workflow
# ---------------------------------------------------------

def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    create_sample_csv(INPUT_FILE)

    demonstrate_basic_csv()
    demonstrate_custom_delimiter()

    report = ProcessingReport()

    employees = list(read_employees(INPUT_FILE, report))

    write_employees_atomically(OUTPUT_FILE, employees)

    department_report = generate_department_report(
        employees,
        REPORT_FILE,
    )

    print("\nProcessed employees:")

    for employee in employees:
        print(employee)

    print("\nDepartment report:")

    for row in department_report:
        print(row)

    print("\nProcessing statistics:")
    print(f"Total rows: {report.total_rows}")
    print(f"Valid rows: {report.valid_rows}")
    print(f"Invalid rows: {report.invalid_rows}")
    print(f"Duplicate rows: {report.duplicate_rows}")
    print(f"Total salary: {report.total_salary}")

    print(f"\nProcessed CSV: {OUTPUT_FILE}")
    print(f"Department CSV: {REPORT_FILE}")

    run_tests()


if __name__ == "__main__":
    main()
