"""
PROGRAMS ON VARIABLES IN PYTHON
===============================

A comprehensive study script covering Python variables from beginner to advanced
concepts through executable examples.

Topics covered:
1. Variables and assignment
2. Naming rules and conventions
3. Dynamic typing
4. Built-in data types
5. Multiple assignment
6. Type conversion
7. Variable scope
8. Mutable and immutable objects
9. Object identity and references
10. Copying variables and collections
11. Local, global, enclosing, and built-in scopes
12. global and nonlocal keywords
13. Constants by convention
14. Unpacking
15. Assignment expressions
16. Type annotations
17. Variables in classes and objects
18. Dataclasses
19. Closures
20. Common mistakes
21. Performance considerations
22. Security and production considerations
23. Practical programs involving variables
"""

from __future__ import annotations

import copy
import math
import statistics
import sys
from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# 1. INTRODUCTION TO VARIABLES
# =============================================================================

print("\n" + "=" * 80)
print("1. INTRODUCTION TO VARIABLES")
print("=" * 80)

# A variable is a name that refers to an object stored in memory.
name = "Atul"
age = 33
height = 178.5

print("Name:", name)
print("Age:", age)
print("Height:", height)

# Python variables do not require explicit declaration before assignment.
city = "Lucknow"
print("City:", city)

# The same variable can later refer to a different object.
value = 10
print("value =", value, "| type =", type(value).__name__)

value = "ten"
print("value =", value, "| type =", type(value).__name__)


# =============================================================================
# 2. VARIABLE NAMING RULES
# =============================================================================

print("\n" + "=" * 80)
print("2. VARIABLE NAMING RULES")
print("=" * 80)

# Valid variable names:
student_name = "Ravi"
_student_id = 101
score2 = 95

print(student_name, _student_id, score2)

# Python naming rules:
#
# 1. A variable name can contain letters, digits, and underscores.
# 2. It cannot start with a digit.
# 3. It cannot contain spaces.
# 4. It cannot contain most special characters.
# 5. Python keywords cannot be used as variable names.
# 6. Variable names are case-sensitive.

student = "A"
Student = "B"

print("student:", student)
print("Student:", Student)

# Recommended naming convention: snake_case
total_salary = 50000
average_score = 88.5

# Avoid unclear names in production code.
x = 10
number_of_students = 10

print("x:", x)
print("number_of_students:", number_of_students)


# =============================================================================
# 3. VARIABLES AND BUILT-IN DATA TYPES
# =============================================================================

print("\n" + "=" * 80)
print("3. VARIABLES AND BUILT-IN DATA TYPES")
print("=" * 80)

integer_value = 42
float_value = 3.14159
complex_value = 2 + 3j
string_value = "Python"
boolean_value = True
none_value = None

list_value = [1, 2, 3]
tuple_value = (1, 2, 3)
set_value = {1, 2, 3}
dictionary_value = {"name": "Atul", "age": 33}

variables = {
    "integer_value": integer_value,
    "float_value": float_value,
    "complex_value": complex_value,
    "string_value": string_value,
    "boolean_value": boolean_value,
    "none_value": none_value,
    "list_value": list_value,
    "tuple_value": tuple_value,
    "set_value": set_value,
    "dictionary_value": dictionary_value,
}

for variable_name, variable_value in variables.items():
    print(
        f"{variable_name:20} = {variable_value!r:30} "
        f"type = {type(variable_value).__name__}"
    )


# =============================================================================
# 4. DYNAMIC TYPING
# =============================================================================

print("\n" + "=" * 80)
print("4. DYNAMIC TYPING")
print("=" * 80)

# Python is dynamically typed.
# The object has a type, while a variable name refers to an object.

dynamic_variable = 100
print(dynamic_variable, type(dynamic_variable).__name__)

dynamic_variable = 99.9
print(dynamic_variable, type(dynamic_variable).__name__)

dynamic_variable = "One hundred"
print(dynamic_variable, type(dynamic_variable).__name__)

dynamic_variable = [1, 2, 3]
print(dynamic_variable, type(dynamic_variable).__name__)


# =============================================================================
# 5. CHECKING VARIABLE TYPE
# =============================================================================

print("\n" + "=" * 80)
print("5. CHECKING VARIABLE TYPE")
print("=" * 80)

number = 25

print("type(number):", type(number))
print("Is int:", isinstance(number, int))
print("Is float:", isinstance(number, float))
print("Is number:", isinstance(number, (int, float)))

# isinstance() is generally preferable to comparing type directly
# when subclasses are possible.


# =============================================================================
# 6. BASIC ASSIGNMENT OPERATORS
# =============================================================================

print("\n" + "=" * 80)
print("6. BASIC ASSIGNMENT OPERATORS")
print("=" * 80)

number = 10
print("Initial number:", number)

number += 5
print("After += 5:", number)

number -= 3
print("After -= 3:", number)

number *= 2
print("After *= 2:", number)

number /= 4
print("After /= 4:", number)

number **= 2
print("After **= 2:", number)


# =============================================================================
# 7. MULTIPLE VARIABLE ASSIGNMENT
# =============================================================================

print("\n" + "=" * 80)
print("7. MULTIPLE VARIABLE ASSIGNMENT")
print("=" * 80)

# Different values assigned simultaneously.
first_name, last_name, age = "Atul", "Pandey", 33

print(first_name)
print(last_name)
print(age)

# Same value assigned to multiple variables.
a = b = c = 100

print("a =", a)
print("b =", b)
print("c =", c)

# Important mutable object warning:
# All variables below refer to the same list.
list_a = list_b = []

list_a.append("shared value")

print("list_a:", list_a)
print("list_b:", list_b)

# Safer approach: create independent lists.
list_c = []
list_d = []

list_c.append("only in list_c")

print("list_c:", list_c)
print("list_d:", list_d)


# =============================================================================
# 8. VARIABLE SWAPPING
# =============================================================================

print("\n" + "=" * 80)
print("8. VARIABLE SWAPPING")
print("=" * 80)

x = 10
y = 20

print("Before swap:", x, y)

# Python supports tuple unpacking for swapping.
x, y = y, x

print("After swap:", x, y)


# =============================================================================
# 9. UNPACKING VARIABLES
# =============================================================================

print("\n" + "=" * 80)
print("9. UNPACKING VARIABLES")
print("=" * 80)

coordinates = (10, 20)
x_coordinate, y_coordinate = coordinates

print("x_coordinate:", x_coordinate)
print("y_coordinate:", y_coordinate)

numbers = [10, 20, 30, 40, 50]

first, second, *remaining = numbers

print("first:", first)
print("second:", second)
print("remaining:", remaining)

first, *middle, last = numbers

print("first:", first)
print("middle:", middle)
print("last:", last)

# Ignore unwanted values using the conventional underscore name.
student_data = ("Atul", 33, "Lucknow", 95)

student_name, _, student_city, student_score = student_data

print(student_name, student_city, student_score)


# =============================================================================
# 10. TYPE CONVERSION
# =============================================================================

print("\n" + "=" * 80)
print("10. TYPE CONVERSION")
print("=" * 80)

integer_text = "100"
integer_number = int(integer_text)

print(integer_number, type(integer_number).__name__)

decimal_text = "25.75"
decimal_number = float(decimal_text)

print(decimal_number, type(decimal_number).__name__)

number = 500
number_as_text = str(number)

print(number_as_text, type(number_as_text).__name__)

print("bool(0):", bool(0))
print("bool(1):", bool(1))
print("bool(''):", bool(""))
print("bool('Python'):", bool("Python"))
print("bool([]):", bool([]))
print("bool([1]):", bool([1]))


# =============================================================================
# 11. SAFE TYPE CONVERSION
# =============================================================================

print("\n" + "=" * 80)
print("11. SAFE TYPE CONVERSION")
print("=" * 80)


def safe_integer_conversion(value: Any) -> int | None:
    """Convert a value to int and return None when conversion is invalid."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


test_values = ["123", "12.5", "hello", None, 45]

for item in test_values:
    converted = safe_integer_conversion(item)
    print(f"{item!r:10} -> {converted!r}")


# =============================================================================
# 12. OBJECT REFERENCES
# =============================================================================

print("\n" + "=" * 80)
print("12. OBJECT REFERENCES")
print("=" * 80)

number_a = 100
number_b = number_a

print("number_a:", number_a)
print("number_b:", number_b)

number_b = 200

print("After changing number_b")
print("number_a:", number_a)
print("number_b:", number_b)

# Immutable objects create a new object when their value changes.


# =============================================================================
# 13. MUTABLE AND IMMUTABLE OBJECTS
# =============================================================================

print("\n" + "=" * 80)
print("13. MUTABLE AND IMMUTABLE OBJECTS")
print("=" * 80)

# Immutable examples:
immutable_integer = 10
immutable_float = 10.5
immutable_string = "Python"
immutable_tuple = (1, 2, 3)

# Mutable examples:
mutable_list = [1, 2, 3]
mutable_dictionary = {"name": "Atul"}
mutable_set = {1, 2, 3}

print("Immutable integer:", immutable_integer)
print("Mutable list:", mutable_list)

# Mutating a list affects all references to that same list.
original_list = [1, 2, 3]
another_reference = original_list

another_reference.append(4)

print("original_list:", original_list)
print("another_reference:", another_reference)


# =============================================================================
# 14. IDENTITY: id() AND is
# =============================================================================

print("\n" + "=" * 80)
print("14. OBJECT IDENTITY")
print("=" * 80)

first_list = [1, 2, 3]
second_list = [1, 2, 3]
third_list = first_list

print("first_list == second_list:", first_list == second_list)
print("first_list is second_list:", first_list is second_list)

print("first_list == third_list:", first_list == third_list)
print("first_list is third_list:", first_list is third_list)

print("id(first_list):", id(first_list))
print("id(third_list):", id(third_list))

# Use "is" primarily for identity checks, especially with None.
value = None

if value is None:
    print("The variable refers to None.")

# Prefer:
# value is None
#
# Instead of:
# value == None


# =============================================================================
# 15. SHALLOW COPY
# =============================================================================

print("\n" + "=" * 80)
print("15. SHALLOW COPY")
print("=" * 80)

original = [1, 2, [3, 4]]

# Three common shallow-copy techniques.
copy_using_method = original.copy()
copy_using_slice = original[:]
copy_using_list = list(original)

copy_using_method.append(100)

print("original:", original)
print("copy_using_method:", copy_using_method)

# Nested mutable objects remain shared in shallow copies.
copy_using_slice[2].append(999)

print("After changing nested list")
print("original:", original)
print("copy_using_slice:", copy_using_slice)


# =============================================================================
# 16. DEEP COPY
# =============================================================================

print("\n" + "=" * 80)
print("16. DEEP COPY")
print("=" * 80)

original_nested = [1, 2, [3, 4]]
deep_copied = copy.deepcopy(original_nested)

deep_copied[2].append(500)

print("original_nested:", original_nested)
print("deep_copied:", deep_copied)


# =============================================================================
# 17. VARIABLE SCOPE
# =============================================================================

print("\n" + "=" * 80)
print("17. VARIABLE SCOPE")
print("=" * 80)

global_message = "I am a global variable"


def demonstrate_local_scope() -> None:
    local_message = "I am a local variable"

    print(global_message)
    print(local_message)


demonstrate_local_scope()

print("Outside function:", global_message)

# local_message cannot be accessed here because its scope is limited
# to the function where it was created.


# =============================================================================
# 18. LOCAL VARIABLE SHADOWING
# =============================================================================

print("\n" + "=" * 80)
print("18. VARIABLE SHADOWING")
print("=" * 80)

value = "global value"


def show_shadowing() -> None:
    value = "local value"
    print("Inside function:", value)


show_shadowing()
print("Outside function:", value)


# =============================================================================
# 19. THE global KEYWORD
# =============================================================================

print("\n" + "=" * 80)
print("19. THE global KEYWORD")
print("=" * 80)

counter = 0


def increment_global_counter() -> None:
    global counter
    counter += 1


increment_global_counter()
increment_global_counter()

print("counter:", counter)

# Excessive use of global variables can make programs difficult to test,
# debug, and maintain.


# =============================================================================
# 20. ENCLOSING SCOPE AND nonlocal
# =============================================================================

print("\n" + "=" * 80)
print("20. ENCLOSING SCOPE AND nonlocal")
print("=" * 80)


def create_counter():
    count = 0

    def increment():
        nonlocal count
        count += 1
        return count

    return increment


counter_function = create_counter()

print(counter_function())
print(counter_function())
print(counter_function())


# =============================================================================
# 21. LEGB RULE
# =============================================================================

print("\n" + "=" * 80)
print("21. LEGB VARIABLE LOOKUP RULE")
print("=" * 80)

# Python normally searches names in this order:
#
# L -> Local scope
# E -> Enclosing scope
# G -> Global scope
# B -> Built-in scope

scope_value = "global"


def outer_function():
    scope_value = "enclosing"

    def inner_function():
        scope_value = "local"
        print("Found:", scope_value)

    inner_function()
    print("Outer:", scope_value)


outer_function()
print("Global:", scope_value)

print("Built-in len([1, 2, 3]):", len([1, 2, 3]))


# =============================================================================
# 22. CONSTANTS BY CONVENTION
# =============================================================================

print("\n" + "=" * 80)
print("22. CONSTANTS BY CONVENTION")
print("=" * 80)

# Python does not enforce constants.
# Uppercase names communicate that values should not be modified.

PI = math.pi
MAX_LOGIN_ATTEMPTS = 5
DEFAULT_TIMEOUT_SECONDS = 30

print("PI:", PI)
print("MAX_LOGIN_ATTEMPTS:", MAX_LOGIN_ATTEMPTS)
print("DEFAULT_TIMEOUT_SECONDS:", DEFAULT_TIMEOUT_SECONDS)


# =============================================================================
# 23. VARIABLES AS FUNCTION PARAMETERS
# =============================================================================

print("\n" + "=" * 80)
print("23. VARIABLES AS FUNCTION PARAMETERS")
print("=" * 80)


def calculate_rectangle_area(length: float, width: float) -> float:
    return length * width


length = 10
width = 5

area = calculate_rectangle_area(length, width)

print("Area:", area)


# =============================================================================
# 24. FUNCTION ARGUMENTS AND OBJECT REFERENCES
# =============================================================================

print("\n" + "=" * 80)
print("24. FUNCTION ARGUMENTS AND REFERENCES")
print("=" * 80)


def modify_list(items: list[str]) -> None:
    items.append("new item")


shopping_list = ["milk", "bread"]

modify_list(shopping_list)

print("shopping_list:", shopping_list)


def reassign_number(number: int) -> None:
    number = 999
    print("Inside function:", number)


original_number = 100

reassign_number(original_number)

print("Outside function:", original_number)

# Python passes object references to functions.
# Mutating a mutable object affects the caller's object.
# Rebinding a local parameter does not rebind the caller's variable.


# =============================================================================
# 25. DEFAULT ARGUMENT PITFALL
# =============================================================================

print("\n" + "=" * 80)
print("25. MUTABLE DEFAULT ARGUMENT PITFALL")
print("=" * 80)


def unsafe_add_item(item: str, items: list[str] = []):
    items.append(item)
    return items


print("Unsafe call 1:", unsafe_add_item("A"))
print("Unsafe call 2:", unsafe_add_item("B"))

# The same default list is reused between calls.


def safe_add_item(item: str, items: list[str] | None = None):
    if items is None:
        items = []

    items.append(item)
    return items


print("Safe call 1:", safe_add_item("A"))
print("Safe call 2:", safe_add_item("B"))


# =============================================================================
# 26. COMPOUND DATA STRUCTURES
# =============================================================================

print("\n" + "=" * 80)
print("26. VARIABLES CONTAINING COLLECTIONS")
print("=" * 80)

student = {
    "name": "Atul",
    "age": 33,
    "skills": ["Python", "SQL", "Project Management"],
}

print("Student:", student)

student["age"] = 34
student["skills"].append("FastAPI")

print("Updated student:", student)


# =============================================================================
# 27. VARIABLE ANNOTATIONS
# =============================================================================

print("\n" + "=" * 80)
print("27. VARIABLE TYPE ANNOTATIONS")
print("=" * 80)

# Type annotations document intended types.
# Python normally does not enforce these annotations at runtime.

user_name: str = "Atul"
user_age: int = 33
user_height: float = 178.5
is_active: bool = True

scores: list[int] = [85, 90, 95]
student_scores: dict[str, int] = {"Math": 90, "Science": 88}

print(user_name, user_age, user_height, is_active)
print(scores)
print(student_scores)


# =============================================================================
# 28. ASSIGNMENT EXPRESSIONS (WALRUS OPERATOR)
# =============================================================================

print("\n" + "=" * 80)
print("28. ASSIGNMENT EXPRESSIONS")
print("=" * 80)

# := assigns a value and evaluates to that value.

numbers = [5, 10, 15, 20]

if (number_count := len(numbers)) > 3:
    print("Number of items:", number_count)


# =============================================================================
# 29. CLASS VARIABLES AND INSTANCE VARIABLES
# =============================================================================

print("\n" + "=" * 80)
print("29. CLASS VARIABLES AND INSTANCE VARIABLES")
print("=" * 80)


class Employee:
    # Class variable shared conceptually by all instances.
    company = "Example Technologies"

    def __init__(self, name: str, salary: float):
        # Instance variables belong to individual objects.
        self.name = name
        self.salary = salary

    def describe(self) -> str:
        return (
            f"Employee(name={self.name!r}, "
            f"salary={self.salary}, company={self.company!r})"
        )


employee_one = Employee("Asha", 50000)
employee_two = Employee("Ravi", 60000)

print(employee_one.describe())
print(employee_two.describe())

employee_one.name = "Asha Sharma"

print(employee_one.describe())


# =============================================================================
# 30. CLASS VARIABLE MUTABILITY PITFALL
# =============================================================================

print("\n" + "=" * 80)
print("30. MUTABLE CLASS VARIABLE PITFALL")
print("=" * 80)


class UnsafeTeam:
    members = []


unsafe_team_one = UnsafeTeam()
unsafe_team_two = UnsafeTeam()

unsafe_team_one.members.append("Alice")

print("unsafe_team_one.members:", unsafe_team_one.members)
print("unsafe_team_two.members:", unsafe_team_two.members)

# Both objects observe the same class-level list.


class SafeTeam:
    def __init__(self):
        self.members = []


safe_team_one = SafeTeam()
safe_team_two = SafeTeam()

safe_team_one.members.append("Alice")

print("safe_team_one.members:", safe_team_one.members)
print("safe_team_two.members:", safe_team_two.members)


# =============================================================================
# 31. DATACLASSES AND VARIABLES
# =============================================================================

print("\n" + "=" * 80)
print("31. DATACLASSES")
print("=" * 80)


@dataclass
class Product:
    name: str
    price: float
    quantity: int = 0
    tags: list[str] = field(default_factory=list)

    def inventory_value(self) -> float:
        return self.price * self.quantity


product = Product(
    name="Laptop",
    price=75000.0,
    quantity=3,
    tags=["electronics", "computer"],
)

print(product)
print("Inventory value:", product.inventory_value())


# =============================================================================
# 32. CLOSURES
# =============================================================================

print("\n" + "=" * 80)
print("32. CLOSURES")
print("=" * 80)


def create_multiplier(multiplier: float):
    """Return a function that remembers multiplier."""

    def multiply(value: float) -> float:
        return value * multiplier

    return multiply


double = create_multiplier(2)
triple = create_multiplier(3)

print("double(10):", double(10))
print("triple(10):", triple(10))


# =============================================================================
# 33. VARIABLE LIFETIME
# =============================================================================

print("\n" + "=" * 80)
print("33. VARIABLE LIFETIME")
print("=" * 80)


def calculate_sum():
    temporary_result = 10 + 20
    return temporary_result


result = calculate_sum()

print("Result:", result)

# temporary_result exists only during the function call.


# =============================================================================
# 34. DELETING VARIABLE NAMES
# =============================================================================

print("\n" + "=" * 80)
print("34. DELETING VARIABLE NAMES")
print("=" * 80)

temporary_variable = "temporary value"

print("Before deletion:", temporary_variable)

del temporary_variable

try:
    print(temporary_variable)
except NameError as error:
    print("NameError:", error)


# =============================================================================
# 35. VARIABLE TRUTHINESS
# =============================================================================

print("\n" + "=" * 80)
print("35. TRUTHINESS")
print("=" * 80)

truthiness_examples = [
    0,
    1,
    "",
    "Python",
    [],
    [1],
    {},
    {"name": "Atul"},
    None,
]

for example in truthiness_examples:
    print(f"{example!r:20} -> {bool(example)}")


# =============================================================================
# 36. COMPARISON: == VERSUS is
# =============================================================================

print("\n" + "=" * 80)
print("36. == VERSUS is")
print("=" * 80)

first = [1, 2, 3]
second = [1, 2, 3]
third = first

print("first == second:", first == second)
print("first is second:", first is second)

print("first == third:", first == third)
print("first is third:", first is third)


# =============================================================================
# 37. VARIABLE ALIASING
# =============================================================================

print("\n" + "=" * 80)
print("37. VARIABLE ALIASING")
print("=" * 80)

primary_scores = [80, 90, 100]
alias_scores = primary_scores

alias_scores.append(70)

print("primary_scores:", primary_scores)
print("alias_scores:", alias_scores)

# Both variable names refer to the same list.


# =============================================================================
# 38. PROGRAM: STUDENT MARK ANALYZER
# =============================================================================

print("\n" + "=" * 80)
print("38. PROGRAM: STUDENT MARK ANALYZER")
print("=" * 80)


def analyze_marks(marks: list[float]) -> dict[str, float | int | None]:
    """Analyze a collection of numeric marks safely."""

    if not marks:
        return {
            "count": 0,
            "minimum": None,
            "maximum": None,
            "average": None,
        }

    return {
        "count": len(marks),
        "minimum": min(marks),
        "maximum": max(marks),
        "average": statistics.mean(marks),
    }


student_marks = [78, 85, 92, 67, 88]

analysis = analyze_marks(student_marks)

for key, value in analysis.items():
    print(f"{key}: {value}")


# =============================================================================
# 39. PROGRAM: TEMPERATURE CONVERTER
# =============================================================================

print("\n" + "=" * 80)
print("39. PROGRAM: TEMPERATURE CONVERTER")
print("=" * 80)


def celsius_to_fahrenheit(celsius: float) -> float:
    return (celsius * 9 / 5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) * 5 / 9


temperature_celsius = 25.0
temperature_fahrenheit = celsius_to_fahrenheit(temperature_celsius)

print(f"{temperature_celsius}°C = {temperature_fahrenheit:.2f}°F")

temperature_fahrenheit = 98.6
temperature_celsius = fahrenheit_to_celsius(temperature_fahrenheit)

print(f"{temperature_fahrenheit}°F = {temperature_celsius:.2f}°C")


# =============================================================================
# 40. PROGRAM: BANK ACCOUNT USING INSTANCE VARIABLES
# =============================================================================

print("\n" + "=" * 80)
print("40. PROGRAM: BANK ACCOUNT")
print("=" * 80)


class BankAccount:
    def __init__(self, account_holder: str, opening_balance: float = 0.0):
        if opening_balance < 0:
            raise ValueError("Opening balance cannot be negative.")

        self.account_holder = account_holder
        self.balance = float(opening_balance)

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")

        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")

        if amount > self.balance:
            raise ValueError("Insufficient balance.")

        self.balance -= amount

    def get_balance(self) -> float:
        return self.balance


account = BankAccount("Atul", 1000)

account.deposit(500)
account.withdraw(300)

print("Account holder:", account.account_holder)
print("Current balance:", account.get_balance())


# =============================================================================
# 41. PROGRAM: VARIABLE-BASED INVENTORY SYSTEM
# =============================================================================

print("\n" + "=" * 80)
print("41. PROGRAM: INVENTORY SYSTEM")
print("=" * 80)


def add_stock(inventory: dict[str, int], product_name: str, quantity: int) -> None:
    if quantity <= 0:
        raise ValueError("Quantity must be positive.")

    inventory[product_name] = inventory.get(product_name, 0) + quantity


def remove_stock(
    inventory: dict[str, int],
    product_name: str,
    quantity: int,
) -> None:
    if quantity <= 0:
        raise ValueError("Quantity must be positive.")

    available_quantity = inventory.get(product_name, 0)

    if quantity > available_quantity:
        raise ValueError("Not enough stock available.")

    inventory[product_name] = available_quantity - quantity


inventory = {
    "Laptop": 5,
    "Mouse": 20,
    "Keyboard": 10,
}

add_stock(inventory, "Laptop", 2)
remove_stock(inventory, "Mouse", 5)

print("Inventory:", inventory)


# =============================================================================
# 42. PROGRAM: CONFIGURATION VARIABLES
# =============================================================================

print("\n" + "=" * 80)
print("42. CONFIGURATION VARIABLES")
print("=" * 80)


@dataclass(frozen=True)
class ApplicationConfig:
    application_name: str
    debug_mode: bool
    maximum_connections: int
    timeout_seconds: int


configuration = ApplicationConfig(
    application_name="Variable Demo",
    debug_mode=False,
    maximum_connections=100,
    timeout_seconds=30,
)

print(configuration)

# frozen=True prevents ordinary reassignment of dataclass fields.


# =============================================================================
# 43. MEMORY SIZE CONSIDERATIONS
# =============================================================================

print("\n" + "=" * 80)
print("43. MEMORY SIZE CONSIDERATIONS")
print("=" * 80)

small_integer = 10
large_list = list(range(1000))

print("Approximate size of small_integer:", sys.getsizeof(small_integer), "bytes")
print("Approximate size of large_list:", sys.getsizeof(large_list), "bytes")

# sys.getsizeof() reports the direct size of an object and does not always
# include the complete memory used by nested referenced objects.


# =============================================================================
# 44. PERFORMANCE: REBINDING VERSUS MUTATION
# =============================================================================

print("\n" + "=" * 80)
print("44. REBINDING VERSUS MUTATION")
print("=" * 80)

numbers = [1, 2, 3]

# Mutation changes the existing object.
numbers.append(4)
print("After mutation:", numbers)

# Rebinding makes the variable refer to another object.
numbers = numbers + [5]
print("After rebinding:", numbers)

# For repeated list extension, append/extend may be more efficient than
# repeatedly creating new lists through concatenation.


# =============================================================================
# 45. PERFORMANCE: STRING CONCATENATION
# =============================================================================

print("\n" + "=" * 80)
print("45. STRING VARIABLE PERFORMANCE")
print("=" * 80)

words = ["Python", "variables", "are", "important"]

sentence = " ".join(words)

print(sentence)

# join() is generally preferable to repeatedly concatenating many strings.


# =============================================================================
# 46. SECURITY CONSIDERATION: NEVER USE eval FOR VARIABLE CONVERSION
# =============================================================================

print("\n" + "=" * 80)
print("46. SECURITY CONSIDERATION")
print("=" * 80)

user_supplied_number = "25"

# Safe conversion:
converted_number = int(user_supplied_number)

print("Safe converted number:", converted_number)

# Do not use eval() for untrusted input.
# eval() can execute arbitrary Python expressions and can create severe
# security vulnerabilities when input is controlled by an attacker.


# =============================================================================
# 47. COMMON MISTAKE: USING A VARIABLE BEFORE ASSIGNMENT
# =============================================================================

print("\n" + "=" * 80)
print("47. COMMON MISTAKE: UNINITIALIZED VARIABLE")
print("=" * 80)


def demonstrate_unbound_local_error() -> None:
    try:
        print(result)
        result = 10
    except UnboundLocalError as error:
        print("UnboundLocalError:", error)


demonstrate_unbound_local_error()


# =============================================================================
# 48. COMMON MISTAKE: ACCIDENTAL SHADOWING OF BUILT-INS
# =============================================================================

print("\n" + "=" * 80)
print("48. COMMON MISTAKE: SHADOWING BUILT-INS")
print("=" * 80)

# Avoid assignments such as:
#
# list = [1, 2, 3]
# str = "text"
# int = 10
# max = 100
#
# These names replace access to the corresponding built-in within the scope.

numbers_for_maximum = [10, 50, 20]

maximum_value = max(numbers_for_maximum)

print("Maximum value:", maximum_value)


# =============================================================================
# 49. COMMON MISTAKE: COMPARING FLOATING-POINT VARIABLES DIRECTLY
# =============================================================================

print("\n" + "=" * 80)
print("49. FLOATING-POINT COMPARISON")
print("=" * 80)

calculated_value = 0.1 + 0.2
expected_value = 0.3

print("calculated_value:", calculated_value)
print("Direct equality:", calculated_value == expected_value)

print(
    "math.isclose:",
    math.isclose(calculated_value, expected_value, rel_tol=1e-9),
)


# =============================================================================
# 50. COMMON MISTAKE: MODIFYING A COLLECTION WHILE ITERATING
# =============================================================================

print("\n" + "=" * 80)
print("50. MODIFYING COLLECTIONS DURING ITERATION")
print("=" * 80)

values = [1, 2, 3, 4, 5, 6]

# Create a new list instead of removing items from the same list during
# iteration.
even_values = [value for value in values if value % 2 == 0]

print("Original:", values)
print("Even values:", even_values)


# =============================================================================
# 51. PRACTICAL PROGRAM: EXPENSE TRACKER
# =============================================================================

print("\n" + "=" * 80)
print("51. PRACTICAL PROGRAM: EXPENSE TRACKER")
print("=" * 80)


@dataclass
class Expense:
    category: str
    amount: float


class ExpenseTracker:
    def __init__(self):
        self.expenses: list[Expense] = []

    def add_expense(self, category: str, amount: float) -> None:
        if not category.strip():
            raise ValueError("Category cannot be empty.")

        if amount <= 0:
            raise ValueError("Expense amount must be positive.")

        self.expenses.append(
            Expense(
                category=category.strip(),
                amount=float(amount),
            )
        )

    def total_expense(self) -> float:
        return sum(expense.amount for expense in self.expenses)

    def expenses_by_category(self) -> dict[str, float]:
        totals: dict[str, float] = {}

        for expense in self.expenses:
            totals[expense.category] = (
                totals.get(expense.category, 0.0) + expense.amount
            )

        return totals


tracker = ExpenseTracker()

tracker.add_expense("Food", 500)
tracker.add_expense("Transport", 250)
tracker.add_expense("Food", 300)

print("Total expense:", tracker.total_expense())
print("By category:", tracker.expenses_by_category())


# =============================================================================
# 52. PRACTICAL PROGRAM: VARIABLE VALIDATION
# =============================================================================

print("\n" + "=" * 80)
print("52. VARIABLE VALIDATION")
print("=" * 80)


def validate_user_data(
    name: str,
    age: int,
    email: str,
) -> dict[str, Any]:
    errors: list[str] = []

    if not isinstance(name, str) or not name.strip():
        errors.append("Name must be a non-empty string.")

    if isinstance(age, bool) or not isinstance(age, int):
        errors.append("Age must be an integer.")
    elif age < 0 or age > 150:
        errors.append("Age must be between 0 and 150.")

    if not isinstance(email, str) or "@" not in email:
        errors.append("Email format is invalid.")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


valid_user = validate_user_data(
    name="Atul",
    age=33,
    email="atul@example.com",
)

invalid_user = validate_user_data(
    name="",
    age=-5,
    email="invalid-email",
)

print("Valid user:", valid_user)
print("Invalid user:", invalid_user)


# =============================================================================
# 53. PRACTICAL PROGRAM: VARIABLE-BASED STATISTICS
# =============================================================================

print("\n" + "=" * 80)
print("53. VARIABLE-BASED STATISTICS")
print("=" * 80)


def calculate_statistics(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {
            "count": 0,
            "sum": 0.0,
            "mean": None,
            "median": None,
            "minimum": None,
            "maximum": None,
        }

    numeric_values = [float(value) for value in values]

    return {
        "count": len(numeric_values),
        "sum": sum(numeric_values),
        "mean": statistics.mean(numeric_values),
        "median": statistics.median(numeric_values),
        "minimum": min(numeric_values),
        "maximum": max(numeric_values),
    }


data_points = [10, 20, 30, 40, 50]

statistics_result = calculate_statistics(data_points)

for metric, metric_value in statistics_result.items():
    print(f"{metric:10}: {metric_value}")


# =============================================================================
# 54. ADVANCED CONCEPT: DESCRIPTORS OF VARIABLES
# =============================================================================

print("\n" + "=" * 80)
print("54. ADVANCED CONCEPT: NAMES REFER TO OBJECTS")
print("=" * 80)

first_reference = {"status": "active"}
second_reference = first_reference

print("Same object:", first_reference is second_reference)

second_reference["status"] = "inactive"

print("first_reference:", first_reference)
print("second_reference:", second_reference)

# A useful mental model is:
#
# variable name -> object reference -> object
#
# Assignment generally binds a name to an object.


# =============================================================================
# 55. ADVANCED CONCEPT: COMPREHENSION VARIABLES
# =============================================================================

print("\n" + "=" * 80)
print("55. COMPREHENSION VARIABLES")
print("=" * 80)

number = 100

squares = [number * number for number in range(5)]

print("squares:", squares)

# In modern Python, the comprehension variable has its own scope.
print("Outer number remains:", number)


# =============================================================================
# 56. ADVANCED CONCEPT: GENERATORS AND VARIABLE LIFETIME
# =============================================================================

print("\n" + "=" * 80)
print("56. GENERATOR VARIABLES")
print("=" * 80)


def generate_squares(limit: int):
    for number in range(limit):
        yield number * number


square_generator = generate_squares(5)

print("Generator object:", square_generator)

for square in square_generator:
    print(square)


# =============================================================================
# 57. ADVANCED CONCEPT: NONLOCAL STATE
# =============================================================================

print("\n" + "=" * 80)
print("57. NONLOCAL STATE")
print("=" * 80)


def create_account(initial_balance: float):
    balance = float(initial_balance)

    def deposit(amount: float) -> float:
        nonlocal balance

        if amount <= 0:
            raise ValueError("Deposit must be positive.")

        balance += amount
        return balance

    def get_balance() -> float:
        return balance

    return deposit, get_balance


deposit_money, get_current_balance = create_account(1000)

deposit_money(500)

print("Current closure balance:", get_current_balance())


# =============================================================================
# 58. TESTING VARIABLE-RELATED FUNCTIONS
# =============================================================================

print("\n" + "=" * 80)
print("58. TESTING")
print("=" * 80)


def calculate_discount(price: float, discount_percentage: float) -> float:
    if price < 0:
        raise ValueError("Price cannot be negative.")

    if not 0 <= discount_percentage <= 100:
        raise ValueError("Discount percentage must be between 0 and 100.")

    return price * (1 - discount_percentage / 100)


assert calculate_discount(1000, 10) == 900
assert calculate_discount(1000, 0) == 1000
assert calculate_discount(1000, 100) == 0

try:
    calculate_discount(-100, 10)
except ValueError:
    print("Negative price validation works.")

try:
    calculate_discount(100, 150)
except ValueError:
    print("Discount validation works.")

print("All basic assertions passed.")


# =============================================================================
# 59. DESIGN PRINCIPLES FOR VARIABLES
# =============================================================================

print("\n" + "=" * 80)
print("59. DESIGN PRINCIPLES")
print("=" * 80)

# Good variable design principles demonstrated through meaningful names.

monthly_income = 100000
monthly_expenses = 65000
monthly_savings = monthly_income - monthly_expenses

savings_rate = monthly_savings / monthly_income

print("Monthly income:", monthly_income)
print("Monthly expenses:", monthly_expenses)
print("Monthly savings:", monthly_savings)
print("Savings rate:", f"{savings_rate:.2%}")

# Prefer names that describe meaning rather than implementation details.
#
# Poor:
# data = 100
# x = 25
#
# Better:
# annual_revenue = 100
# customer_count = 25


# =============================================================================
# 60. FINAL INTEGRATED PROGRAM
# =============================================================================

print("\n" + "=" * 80)
print("60. FINAL INTEGRATED PROGRAM: EMPLOYEE DATA ANALYZER")
print("=" * 80)


@dataclass
class EmployeeRecord:
    employee_id: int
    name: str
    department: str
    salary: float


class EmployeeAnalyzer:
    def __init__(self):
        self.records: dict[int, EmployeeRecord] = {}

    def add_employee(
        self,
        employee_id: int,
        name: str,
        department: str,
        salary: float,
    ) -> None:
        if employee_id in self.records:
            raise ValueError("Employee ID already exists.")

        if not name.strip():
            raise ValueError("Employee name cannot be empty.")

        if not department.strip():
            raise ValueError("Department cannot be empty.")

        if salary < 0:
            raise ValueError("Salary cannot be negative.")

        self.records[employee_id] = EmployeeRecord(
            employee_id=employee_id,
            name=name.strip(),
            department=department.strip(),
            salary=float(salary),
        )

    def total_salary(self) -> float:
        return sum(record.salary for record in self.records.values())

    def average_salary(self) -> float | None:
        if not self.records:
            return None

        return self.total_salary() / len(self.records)

    def department_salary_totals(self) -> dict[str, float]:
        totals: dict[str, float] = {}

        for record in self.records.values():
            totals[record.department] = (
                totals.get(record.department, 0.0) + record.salary
            )

        return totals

    def highest_paid_employee(self) -> EmployeeRecord | None:
        if not self.records:
            return None

        return max(
            self.records.values(),
            key=lambda record: record.salary,
        )


employee_analyzer = EmployeeAnalyzer()

employee_analyzer.add_employee(
    employee_id=101,
    name="Asha",
    department="Engineering",
    salary=900000,
)

employee_analyzer.add_employee(
    employee_id=102,
    name="Ravi",
    department="Engineering",
    salary=850000,
)

employee_analyzer.add_employee(
    employee_id=103,
    name="Neha",
    department="Marketing",
    salary=700000,
)

print("Total salary:", employee_analyzer.total_salary())
print("Average salary:", employee_analyzer.average_salary())
print("Department totals:", employee_analyzer.department_salary_totals())

highest_paid = employee_analyzer.highest_paid_employee()

if highest_paid is not None:
    print("Highest paid employee:", highest_paid.name)
    print("Highest salary:", highest_paid.salary)


# =============================================================================
# END OF SCRIPT
# =============================================================================

print("\n" + "=" * 80)
print("VARIABLES IN PYTHON: COMPLETE")
print("=" * 80)
