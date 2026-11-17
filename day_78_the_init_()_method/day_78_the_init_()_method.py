"""
THE __init__() METHOD
Python object initialization: fundamentals to advanced concepts.

Demonstrates:
- Constructors and object initialization
- self and instance attributes
- Default and parameterized initialization
- Attribute validation
- Constructor overloading alternatives
- Default mutable argument protection
- Constructor chaining through inheritance
- Composition
- Class attributes
- Dataclasses
- Object state management
- Serialization and reconstruction
- Unit-style assertions
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import json


# ============================================================
# 1. FUNDAMENTALS: BASIC __init__()
# ============================================================

class Student:
    def __init__(self, name, age):
        # self refers to the object currently being initialized.
        self.name = self._validate_name(name)
        self.age = self._validate_age(age)

    @staticmethod
    def _validate_name(name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Student name must be a non-empty string.")
        return name.strip()

    @staticmethod
    def _validate_age(age):
        if isinstance(age, bool) or not isinstance(age, int):
            raise TypeError("Age must be an integer.")
        if not 0 <= age <= 120:
            raise ValueError("Age must be between 0 and 120.")
        return age

    def introduce(self):
        return f"{self.name} is {self.age} years old."


# ============================================================
# 2. DEFAULT AND PARAMETERIZED INITIALIZATION
# ============================================================

class Employee:
    def __init__(
        self,
        employee_id,
        department="Engineering",
        active=True
    ):
        if not isinstance(employee_id, str) or not employee_id.strip():
            raise ValueError("Employee ID is required.")

        if not isinstance(department, str) or not department.strip():
            raise ValueError("Department cannot be empty.")

        if not isinstance(active, bool):
            raise TypeError("Active must be a boolean.")

        self.employee_id = employee_id.strip()
        self.department = department.strip()
        self.active = active

    def deactivate(self):
        self.active = False


# ============================================================
# 3. THE MUTABLE DEFAULT ARGUMENT PROBLEM
# ============================================================

class Project:
    def __init__(self, name, members=None):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Project name is required.")

        if members is None:
            members = []

        if not isinstance(members, list):
            raise TypeError("Members must be a list.")

        if any(not isinstance(member, str) for member in members):
            raise TypeError("Every member must be a string.")

        # Create a separate list for each object.
        self.name = name.strip()
        self.members = list(members)

    def add_member(self, member):
        if not isinstance(member, str) or not member.strip():
            raise ValueError("Member name is required.")

        member = member.strip()

        if member not in self.members:
            self.members.append(member)


# ============================================================
# 4. CLASS ATTRIBUTES AND INSTANCE ATTRIBUTES
# ============================================================

class DatabaseConnection:
    application_name = "Enterprise Application"
    total_connections = 0

    def __init__(self, host, port=5432):
        if not isinstance(host, str) or not host.strip():
            raise ValueError("Host is required.")

        if isinstance(port, bool) or not isinstance(port, int):
            raise TypeError("Port must be an integer.")

        if not 1 <= port <= 65535:
            raise ValueError("Invalid network port.")

        self.host = host.strip()
        self.port = port
        DatabaseConnection.total_connections += 1

    def endpoint(self):
        return f"{self.host}:{self.port}"


# ============================================================
# 5. ENUMS AND CONSTRUCTOR VALIDATION
# ============================================================

class AccountStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class BankAccount:
    def __init__(self, account_number, owner, balance=0.0):
        if not isinstance(account_number, str) or not account_number.strip():
            raise ValueError("Account number is required.")

        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("Account owner is required.")

        if isinstance(balance, bool) or not isinstance(balance, (int, float)):
            raise TypeError("Balance must be numeric.")

        if balance < 0 or balance != balance or balance == float("inf"):
            raise ValueError("Invalid initial balance.")

        self.account_number = account_number.strip()
        self.owner = owner.strip()
        self.balance = float(balance)
        self.status = AccountStatus.ACTIVE

    def deposit(self, amount):
        if self.status is not AccountStatus.ACTIVE:
            raise RuntimeError("Account is not active.")

        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("Deposit must be numeric.")

        if amount <= 0 or amount != amount or amount == float("inf"):
            raise ValueError("Deposit must be a positive finite amount.")

        self.balance += amount

    def suspend(self):
        if self.status is AccountStatus.CLOSED:
            raise RuntimeError("A closed account cannot be suspended.")

        self.status = AccountStatus.SUSPENDED


# ============================================================
# 6. CONSTRUCTOR CHAINING THROUGH INHERITANCE
# ============================================================

class Person:
    def __init__(self, name, email):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name is required.")

        if not isinstance(email, str) or "@" not in email:
            raise ValueError("A valid email address is required.")

        self.name = name.strip()
        self.email = email.strip()


class Manager(Person):
    def __init__(self, name, email, team_size):
        # Initialize inherited attributes.
        super().__init__(name, email)

        if isinstance(team_size, bool) or not isinstance(team_size, int):
            raise TypeError("Team size must be an integer.")

        if team_size < 0:
            raise ValueError("Team size cannot be negative.")

        self.team_size = team_size


# ============================================================
# 7. COMPOSITION: OBJECTS INITIALIZED WITH OTHER OBJECTS
# ============================================================

class Address:
    def __init__(self, city, country):
        if not city or not isinstance(city, str):
            raise ValueError("City is required.")

        if not country or not isinstance(country, str):
            raise ValueError("Country is required.")

        self.city = city.strip()
        self.country = country.strip()


class Organization:
    def __init__(self, name, address):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Organization name is required.")

        if not isinstance(address, Address):
            raise TypeError("Address must be an Address object.")

        self.name = name.strip()
        self.address = address


# ============================================================
# 8. FACTORY METHOD AS AN ALTERNATIVE TO OVERLOADING
# ============================================================

class Product:
    def __init__(self, name, price, category):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Product name is required.")

        if isinstance(price, bool) or not isinstance(price, (int, float)):
            raise TypeError("Price must be numeric.")

        if price < 0 or price != price or price == float("inf"):
            raise ValueError("Invalid product price.")

        if not isinstance(category, str) or not category.strip():
            raise ValueError("Category is required.")

        self.name = name.strip()
        self.price = float(price)
        self.category = category.strip()

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("Product data must be a dictionary.")

        required = {"name", "price", "category"}

        if set(data) != required:
            raise ValueError("Product data must contain exactly the required fields.")

        return cls(
            name=data["name"],
            price=data["price"],
            category=data["category"]
        )

    @classmethod
    def from_json(cls, json_text):
        try:
            data = json.loads(json_text)
        except (json.JSONDecodeError, TypeError) as exc:
            raise ValueError("Invalid product JSON.") from exc

        return cls.from_dict(data)


# ============================================================
# 9. DATACLASSES AND AUTOMATIC INITIALIZATION
# ============================================================

@dataclass
class ResearchProject:
    title: str
    principal_investigator: str
    budget: float
    collaborators: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("Project title cannot be empty.")

        if not self.principal_investigator.strip():
            raise ValueError("Principal investigator is required.")

        if self.budget < 0:
            raise ValueError("Budget cannot be negative.")

        if not all(
            isinstance(person, str) and person.strip()
            for person in self.collaborators
        ):
            raise ValueError("Collaborators must have valid names.")

        self.collaborators = [
            person.strip() for person in self.collaborators
        ]


# ============================================================
# 10. ADVANCED: OBJECT INITIALIZATION AND STATE MANAGEMENT
# ============================================================

class DeploymentState(Enum):
    CREATED = "created"
    VALIDATED = "validated"
    DEPLOYED = "deployed"
    FAILED = "failed"


class Deployment:
    def __init__(self, application, environment, configuration=None):
        if not isinstance(application, str) or not application.strip():
            raise ValueError("Application name is required.")

        allowed_environments = {"development", "testing", "production"}

        if environment not in allowed_environments:
            raise ValueError("Unsupported deployment environment.")

        configuration = {} if configuration is None else configuration

        if not isinstance(configuration, dict):
            raise TypeError("Configuration must be a dictionary.")

        self.application = application.strip()
        self.environment = environment
        self.configuration = dict(configuration)
        self.state = DeploymentState.CREATED
        self.created_at = datetime.now(timezone.utc)

    def validate(self):
        if not self.configuration.get("version"):
            raise ValueError("Application version is required.")

        self.state = DeploymentState.VALIDATED

    def deploy(self):
        if self.state is not DeploymentState.VALIDATED:
            raise RuntimeError("Deployment must be validated first.")

        self.state = DeploymentState.DEPLOYED

    def fail(self):
        if self.state is DeploymentState.DEPLOYED:
            raise RuntimeError("A completed deployment cannot be marked failed.")

        self.state = DeploymentState.FAILED


# ============================================================
# 11. CONSTRUCTOR-BASED RECONSTRUCTION
# ============================================================

def reconstruct_account(data):
    required = {"account_number", "owner", "balance"}

    if not isinstance(data, dict) or set(data) != required:
        raise ValueError("Invalid account representation.")

    # Reconstruction passes through the original constructor,
    # so validation is applied again.
    return BankAccount(**data)


# ============================================================
# 12. EXECUTABLE DEMONSTRATION
# ============================================================

def run_examples():
    print("\n1. Basic initialization")

    student = Student("Atul", 25)
    print(student.introduce())

    print("\n2. Default initialization")

    employee = Employee("EMP-101")
    print(employee.employee_id, employee.department, employee.active)

    print("\n3. Independent mutable attributes")

    project_a = Project("Security Research")
    project_b = Project("Cloud Research")

    project_a.add_member("Researcher A")

    assert project_a.members != project_b.members
    print(project_a.members, project_b.members)

    print("\n4. Class and instance attributes")

    connection = DatabaseConnection("localhost")
    print(connection.endpoint())
    print(DatabaseConnection.total_connections)

    print("\n5. Validated account initialization")

    account = BankAccount("ACC-1001", "Atul", 5000)
    account.deposit(1500)
    print(account.balance, account.status.value)

    print("\n6. Inheritance and super()")

    manager = Manager("Anita", "anita@example.com", 8)
    print(manager.name, manager.email, manager.team_size)

    print("\n7. Composition")

    address = Address("Lucknow", "India")
    organization = Organization("Research Lab", address)
    print(organization.name, organization.address.city)

    print("\n8. Alternative construction")

    product = Product.from_dict({
        "name": "Security Sensor",
        "price": 2499,
        "category": "Hardware"
    })

    print(product.name, product.price)

    print("\n9. Dataclass initialization")

    research = ResearchProject(
        "Federated Learning",
        "Dr. Sharma",
        250000,
        ["Researcher A", "Researcher B"]
    )

    print(asdict(research))

    print("\n10. Deployment state management")

    deployment = Deployment(
        "Risk Engine",
        "testing",
        {"version": "2.1.0"}
    )

    deployment.validate()
    deployment.deploy()

    print(deployment.state.value)

    print("\n11. Object reconstruction")

    restored = reconstruct_account({
        "account_number": "ACC-1002",
        "owner": "Rahul",
        "balance": 8000
    })

    print(restored.account_number, restored.balance)

    print("\n12. Edge-case validation")

    invalid_cases = [
        lambda: Student("", 20),
        lambda: Student("A", -1),
        lambda: Employee(""),
        lambda: BankAccount("ACC-1", "User", -100),
        lambda: Manager("User", "invalid-email", 5),
        lambda: Product("Device", -10, "Hardware"),
        lambda: ResearchProject("", "Researcher", 100)
    ]

    for operation in invalid_cases:
        try:
            operation()
        except (ValueError, TypeError) as exc:
            print(f"Rejected: {exc}")

    print("\n13. Automated assertions")

    assert student.name == "Atul"
    assert employee.department == "Engineering"
    assert account.balance == 6500
    assert manager.team_size == 8
    assert deployment.state is DeploymentState.DEPLOYED
    assert restored.balance == 8000

    print("All assertions passed.")


if __name__ == "__main__":
    run_examples()
