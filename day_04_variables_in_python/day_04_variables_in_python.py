"""
============================================================
PYTHON VARIABLES
============================================================

This program explains and demonstrates Python variables from
beginner to advanced level.

Topics covered:

1. What is a variable?
2. Creating variables
3. Variable naming rules
4. Assigning values
5. Multiple assignment
6. Multiple variables with multiple values
7. Assigning the same value to multiple variables
8. Dynamic typing
9. Checking the type of a variable
10. Changing the value and type of a variable
11. Common built-in data types
12. None
13. Boolean variables
14. Numeric variables
15. String variables
16. Collection variables
17. Variables and objects
18. Object identity
19. id()
20. is vs ==
21. Mutable and immutable objects
22. Variable reassignment
23. References and aliases
24. Shallow understanding of copying
25. Local variables
26. Global variables
27. global keyword
28. Function parameters as variables
29. Return values stored in variables
30. Variable scope
31. LEGB rule
32. nonlocal
33. Constants by convention
34. Type hints
35. Variable annotations
36. Type aliases
37. Unpacking
38. Extended unpacking
39. Swapping variables
40. Starred assignment
41. Underscore variable
42. Loop variables
43. Comprehension variables
44. Walrus operator :=
45. Variables inside classes
46. Instance variables
47. Class variables
48. Class vs instance attributes
49. Environment-related variables
50. Variables containing functions
51. Variables containing objects
52. First-class nature of functions
53. Namespace
54. locals()
55. globals()
56. del
57. Garbage collection concept
58. Reference counting concept
59. Common variable mistakes
60. Best practices
61. Advanced examples
62. Practical mini-project
============================================================
"""


# ============================================================
# 1. WHAT IS A VARIABLE?
# ============================================================

"""
A variable is a name that refers to an object/value in Python.

Example:

name = "Atul"

Here:
    name  -> variable name
    "Atul" -> object/value
    =      -> assignment operator

Unlike some programming languages, Python variables do not
need to be declared with a separate declaration statement.
"""

name = "Atul"
age = 30
salary = 50000.50

print(name)
print(age)
print(salary)


# ============================================================
# 2. CREATING VARIABLES
# ============================================================

first_name = "Atul"
age = 30
is_employee = True

print(first_name)
print(age)
print(is_employee)


# ============================================================
# 3. VARIABLE NAMING RULES
# ============================================================

"""
Valid variable names:

name
age
first_name
employee1
total_salary
_private_variable

Rules:

1. A variable name can contain letters.
2. A variable name can contain numbers.
3. A variable name can contain underscore.
4. A variable name cannot start with a number.
5. A variable name cannot contain spaces.
6. A variable name is case-sensitive.
7. Python keywords cannot be used as variable names.

Examples of valid names:
"""

user_name = "Atul"
age2 = 31
total_salary = 75000
_private_value = 100

print(user_name, age2, total_salary, _private_value)


"""
Invalid examples:

2name = "Atul"              # Cannot start with number
user name = "Atul"          # Spaces are not allowed
class = "Python"            # class is a keyword
"""

# Python is case-sensitive.
name = "Atul"
Name = "Rahul"

print(name)
print(Name)


# ============================================================
# 4. ASSIGNMENT
# ============================================================

"""
The = operator assigns an object to a variable.

It does NOT mean mathematical equality.

"""

x = 10

print(x)


# ============================================================
# 5. REASSIGNING A VARIABLE
# ============================================================

x = 10
print(x)

x = 20
print(x)

x = 30
print(x)


# ============================================================
# 6. VARIABLES CAN REFER TO DIFFERENT TYPES
# ============================================================

value = 100
print(value)

value = "Python"
print(value)

value = 3.14
print(value)

value = True
print(value)


# ============================================================
# 7. DYNAMIC TYPING
# ============================================================

"""
Python is dynamically typed.

The type belongs to the object, not permanently to the
variable name.

A variable can refer to an integer at one point and a string
later.
"""

data = 100
print(data)
print(type(data))

data = "Hello"
print(data)
print(type(data))

data = [1, 2, 3]
print(data)
print(type(data))


# ============================================================
# 8. CHECKING THE TYPE
# ============================================================

age = 30
name = "Atul"
salary = 50000.50
is_active = True

print(type(age))
print(type(name))
print(type(salary))
print(type(is_active))


# ============================================================
# 9. isinstance()
# ============================================================

"""
isinstance() checks whether an object belongs to a particular
type or class.
"""

age = 30

print(isinstance(age, int))
print(isinstance(age, float))
print(isinstance(age, object))


# ============================================================
# 10. COMMON BUILT-IN DATA TYPES
# ============================================================

integer_value = 100
float_value = 99.99
complex_value = 3 + 4j
string_value = "Python"
boolean_value = True
none_value = None

list_value = [1, 2, 3]
tuple_value = (1, 2, 3)
set_value = {1, 2, 3}
dictionary_value = {"name": "Atul", "age": 30}

print(type(integer_value))
print(type(float_value))
print(type(complex_value))
print(type(string_value))
print(type(boolean_value))
print(type(none_value))
print(type(list_value))
print(type(tuple_value))
print(type(set_value))
print(type(dictionary_value))


# ============================================================
# 11. NONE
# ============================================================

"""
None represents the absence of a value.

It is a special singleton object of type NoneType.
"""

result = None

print(result)
print(type(result))

if result is None:
    print("No result available.")


# ============================================================
# 12. BOOLEAN VARIABLES
# ============================================================

is_logged_in = True
has_permission = False

print(is_logged_in)
print(has_permission)

if is_logged_in:
    print("User is logged in.")


# ============================================================
# 13. NUMERIC VARIABLES
# ============================================================

age = 30
height = 5.9
complex_number = 2 + 3j

print(age)
print(height)
print(complex_number)


# ============================================================
# 14. STRING VARIABLES
# ============================================================

name = "Atul"
message = "Welcome to Python"

print(name)
print(message)

full_message = message + ", " + name

print(full_message)


# ============================================================
# 15. COLLECTION VARIABLES
# ============================================================

numbers = [10, 20, 30]
coordinates = (10, 20)
unique_numbers = {1, 2, 3}
person = {
    "name": "Atul",
    "age": 30
}

print(numbers)
print(coordinates)
print(unique_numbers)
print(person)


# ============================================================
# 16. MULTIPLE ASSIGNMENT
# ============================================================

name, age, city = "Atul", 30, "Lucknow"

print(name)
print(age)
print(city)


# ============================================================
# 17. SAME VALUE TO MULTIPLE VARIABLES
# ============================================================

a = b = c = 100

print(a)
print(b)
print(c)


# ============================================================
# 18. MULTIPLE VALUES WITH UNPACKING
# ============================================================

numbers = [10, 20, 30]

x, y, z = numbers

print(x)
print(y)
print(z)


# ============================================================
# 19. VARIABLE SWAPPING
# ============================================================

a = 10
b = 20

print("Before:", a, b)

a, b = b, a

print("After:", a, b)


# ============================================================
# 20. EXTENDED UNPACKING
# ============================================================

numbers = [1, 2, 3, 4, 5]

first, *middle, last = numbers

print(first)
print(middle)
print(last)


# ============================================================
# 21. STARRED ASSIGNMENT
# ============================================================

numbers = [10, 20, 30, 40, 50, 60]

first, second, *remaining = numbers

print(first)
print(second)
print(remaining)


# ============================================================
# 22. UNDERSCORE VARIABLE
# ============================================================

"""
The underscore _ is commonly used when a value is intentionally
not needed.
"""

for _ in range(3):
    print("Python")


# ============================================================
# 23. LOOP VARIABLES
# ============================================================

numbers = [10, 20, 30]

for number in numbers:
    print(number)

print("Last value of number:", number)


# ============================================================
# 24. COMPREHENSION VARIABLES
# ============================================================

squares = [number * number for number in range(5)]

print(squares)

"""
In Python 3, the comprehension variable generally does not leak
into the surrounding scope.
"""

# print(number) may refer to another existing variable,
# depending on what existed before.


# ============================================================
# 25. VARIABLES AND OBJECTS
# ============================================================

"""
Python variables are names that reference objects.

For example:

x = 100

Conceptually:

x ---> 100

The name x refers to an integer object.
"""

x = 100

print(x)


# ============================================================
# 26. id()
# ============================================================

"""
id() returns the identity of an object during its lifetime.

It can be useful when studying whether two variables refer to
the same object.
"""

x = 100
y = x

print(id(x))
print(id(y))


# ============================================================
# 27. ALIASING
# ============================================================

"""
Two variables can refer to the same object.

This is called aliasing.
"""

numbers = [1, 2, 3]

other_numbers = numbers

print(numbers)
print(other_numbers)

other_numbers.append(4)

print(numbers)
print(other_numbers)


# ============================================================
# 28. == VS IS
# ============================================================

"""
== checks value equality.

is checks object identity.
"""

list_a = [1, 2, 3]
list_b = [1, 2, 3]

print(list_a == list_b)
print(list_a is list_b)


# ============================================================
# 29. MUTABLE VS IMMUTABLE OBJECTS
# ============================================================

"""
Mutable objects can be changed after creation.

Examples:
    list
    dictionary
    set

Immutable objects cannot be changed after creation.

Examples:
    int
    float
    bool
    str
    tuple
    frozenset
"""

# Mutable example

numbers = [1, 2, 3]

numbers.append(4)

print(numbers)


# Immutable example

name = "Python"

# This does not modify the existing string object.
# A new string object is created.

name = name + " Programming"

print(name)


# ============================================================
# 30. VARIABLE REFERENCE CHANGES
# ============================================================

x = 10

print(x)

x = 20

print(x)

"""
The variable x is now associated with another object/value.
"""


# ============================================================
# 31. COPYING A LIST
# ============================================================

original = [1, 2, 3]

copy_list = original.copy()

copy_list.append(4)

print("Original:", original)
print("Copy:", copy_list)


# ============================================================
# 32. LOCAL VARIABLES
# ============================================================

def calculate_total():
    price = 100
    quantity = 5
    total = price * quantity

    print(total)


calculate_total()

"""
price, quantity and total are local variables.

They exist within the function's local scope.
"""


# ============================================================
# 33. FUNCTION PARAMETERS
# ============================================================

def greet(name):
    print("Hello", name)


greet("Atul")

"""
name is a local variable created as a function parameter.
"""


# ============================================================
# 34. RETURN VALUE STORED IN A VARIABLE
# ============================================================

def add(a, b):
    return a + b


result = add(10, 20)

print(result)


# ============================================================
# 35. GLOBAL VARIABLES
# ============================================================

"""
A variable created outside functions is normally in the global
scope of that module.
"""

company = "OpenAI"


def show_company():
    print(company)


show_company()


# ============================================================
# 36. MODIFYING GLOBAL VARIABLES
# ============================================================

counter = 0


def increase_counter():
    global counter
    counter += 1


increase_counter()
increase_counter()

print(counter)


# ============================================================
# 37. WHY GLOBAL SHOULD BE USED CAREFULLY
# ============================================================

"""
Global variables can make programs harder to understand because
many functions may depend on and modify the same state.

Prefer local variables, function arguments and return values
when possible.
"""


# ============================================================
# 38. NESTED FUNCTIONS AND NONLOCAL
# ============================================================

def outer():
    value = 10

    def inner():
        nonlocal value
        value += 5

    inner()

    return value


result = outer()

print(result)


# ============================================================
# 39. LEGB RULE
# ============================================================

"""
When Python searches for a variable name, it generally follows
the LEGB rule:

L = Local
E = Enclosing
G = Global
B = Built-in
"""

x = "global"


def outer_function():
    x = "enclosing"

    def inner_function():
        x = "local"
        print(x)

    inner_function()


outer_function()


# ============================================================
# 40. BUILT-IN NAMES
# ============================================================

"""
Python provides built-in names such as:

print
len
type
sum
max
min
range

Avoid unnecessarily using these names as your variables because
you can hide the built-in name.
"""

# Bad practice:
# list = [1, 2, 3]

# Better:
numbers = [1, 2, 3]

print(numbers)


# ============================================================
# 41. CONSTANTS BY CONVENTION
# ============================================================

"""
Python does not enforce constants at the language level.

By convention, constants are written in uppercase.
"""

PI = 3.141592653589793
MAX_CONNECTIONS = 100
DEFAULT_TIMEOUT = 30

print(PI)
print(MAX_CONNECTIONS)
print(DEFAULT_TIMEOUT)


# ============================================================
# 42. TYPE HINTS
# ============================================================

"""
Type hints allow programmers to document the expected type.

Python generally does not enforce the annotation at runtime.
"""

age: int = 30
name: str = "Atul"
salary: float = 50000.50
is_active: bool = True

print(age)
print(name)
print(salary)
print(is_active)


# ============================================================
# 43. VARIABLE ANNOTATIONS WITHOUT IMMEDIATE ASSIGNMENT
# ============================================================

"""
A variable can have an annotation without an assigned value.
"""

employee_name: str
employee_age: int

employee_name = "Atul"
employee_age = 30

print(employee_name)
print(employee_age)


# ============================================================
# 44. TYPE HINTS IN FUNCTIONS
# ============================================================

def calculate_area(length: float, width: float) -> float:
    return length * width


area = calculate_area(10.5, 5.0)

print(area)


# ============================================================
# 45. TYPE ALIASES
# ============================================================

"""
A type alias gives another name to a type or type expression.

Modern Python supports syntax such as:

type UserID = int

The exact syntax depends on the Python version.

For broad compatibility, this example uses a traditional alias.
"""

UserID = int

user_id: UserID = 1001

print(user_id)


# ============================================================
# 46. VARIABLES CONTAINING FUNCTIONS
# ============================================================

def greet_user():
    return "Hello from Python"


message_function = greet_user

print(message_function())


# ============================================================
# 47. FUNCTIONS ARE OBJECTS
# ============================================================

"""
Functions are objects in Python.

Therefore a function can be:

- assigned to a variable
- passed to another function
- stored in a list
- returned from another function
"""

def square(number):
    return number * number


operation = square

print(operation(5))


# ============================================================
# 48. FUNCTION PASSED AS A VARIABLE
# ============================================================

def apply_operation(value, operation):
    return operation(value)


result = apply_operation(10, square)

print(result)


# ============================================================
# 49. LAMBDA STORED IN A VARIABLE
# ============================================================

double = lambda number: number * 2

print(double(10))


# ============================================================
# 50. VARIABLES CONTAINING OBJECTS
# ============================================================

class Person:

    def __init__(self, name, age):
        self.name = name
        self.age = age


person = Person("Atul", 30)

print(person.name)
print(person.age)


# ============================================================
# 51. INSTANCE VARIABLES
# ============================================================

"""
Instance variables belong to individual objects.

self.name and self.age are instance variables.
"""

person1 = Person("Atul", 30)
person2 = Person("Rahul", 25)

print(person1.name)
print(person2.name)


# ============================================================
# 52. CLASS VARIABLES
# ============================================================

class Employee:

    company = "Example Corporation"

    def __init__(self, name):
        self.name = name


employee1 = Employee("Atul")
employee2 = Employee("Rahul")

print(employee1.company)
print(employee2.company)

print(employee1.name)
print(employee2.name)


# ============================================================
# 53. INSTANCE ATTRIBUTE VS CLASS ATTRIBUTE
# ============================================================

class Student:

    school = "Python School"

    def __init__(self, name):
        self.name = name


student1 = Student("Atul")

student1.school = "Advanced Python School"

print(student1.school)
print(Student.school)


# ============================================================
# 54. NAMESPACE
# ============================================================

"""
A namespace is a mapping between names and objects.

Examples include:

- local namespace
- global/module namespace
- class namespace
- built-in namespace
"""


x = 100
y = 200

print(globals()["x"])
print(globals()["y"])


# ============================================================
# 55. globals()
# ============================================================

"""
globals() returns a dictionary representing the current global
namespace.
"""

global_variable = "Hello"

print(globals()["global_variable"])


# ============================================================
# 56. locals()
# ============================================================

def demonstrate_locals():
    local_a = 10
    local_b = 20

    print(locals())


demonstrate_locals()


# ============================================================
# 57. del
# ============================================================

"""
del removes a name binding.

It does not necessarily mean that the underlying object is
immediately destroyed.
"""

temporary_value = 100

print(temporary_value)

del temporary_value

# The following would cause NameError:
# print(temporary_value)


# ============================================================
# 58. REFERENCE COUNTING CONCEPT
# ============================================================

"""
Python implementations commonly use reference counting as part
of memory management, especially CPython.

When no references remain to an object, it may become eligible
for cleanup.

The exact memory-management behavior depends on the Python
implementation.
"""

data = [1, 2, 3]

reference = data

del data

print(reference)


# ============================================================
# 59. VARIABLE SHADOWING
# ============================================================

name = "Global Name"


def demonstrate_shadowing():
    name = "Local Name"
    print(name)


demonstrate_shadowing()

print(name)


# ============================================================
# 60. BUILT-IN NAME SHADOWING
# ============================================================

"""
Avoid:

sum = 100
list = [1, 2, 3]
str = "hello"

because these names are also built into Python.

Example of good naming:
"""

total = 100
items = [1, 2, 3]
text = "hello"

print(total)
print(items)
print(text)


# ============================================================
# 61. VARIABLES AND EXPRESSIONS
# ============================================================

price = 100
quantity = 5

total = price * quantity

print(total)


# ============================================================
# 62. VARIABLES AND OPERATORS
# ============================================================

a = 10
b = 3

addition = a + b
subtraction = a - b
multiplication = a * b
division = a / b
floor_division = a // b
remainder = a % b
power = a ** b

print(addition)
print(subtraction)
print(multiplication)
print(division)
print(floor_division)
print(remainder)
print(power)


# ============================================================
# 63. AUGMENTED ASSIGNMENT
# ============================================================

score = 100

score += 10
print(score)

score -= 20
print(score)

score *= 2
print(score)

score /= 2
print(score)


# ============================================================
# 64. WALRUS OPERATOR :=
# ============================================================

"""
The assignment expression operator := allows an expression to
assign a value to a variable.

Example:
"""

if (length := len("Python")) > 5:
    print("Length:", length)


# ============================================================
# 65. WALRUS OPERATOR IN A LOOP
# ============================================================

data = [1, 2, 3, 4, 5]

index = 0

while index < len(data):
    current = data[index]
    print(current)
    index += 1


# ============================================================
# 66. UNPACKING DICTIONARIES
# ============================================================

person = {
    "name": "Atul",
    "age": 30
}

name = person["name"]
age = person["age"]

print(name)
print(age)


# ============================================================
# 67. STRUCTURAL UNPACKING WITH TUPLES
# ============================================================

employee = ("Atul", 30, "Security")

employee_name, employee_age, department = employee

print(employee_name)
print(employee_age)
print(department)


# ============================================================
# 68. NESTED UNPACKING
# ============================================================

data = ("Atul", (30, "Lucknow"))

name, (age, city) = data

print(name)
print(age)
print(city)


# ============================================================
# 69. PRACTICAL VARIABLE EXAMPLE
# ============================================================

product_name = "Laptop"
product_price = 65000
quantity = 2
discount_percentage = 10

subtotal = product_price * quantity
discount_amount = subtotal * discount_percentage / 100
final_amount = subtotal - discount_amount

print("Product:", product_name)
print("Price:", product_price)
print("Quantity:", quantity)
print("Subtotal:", subtotal)
print("Discount:", discount_amount)
print("Final Amount:", final_amount)


# ============================================================
# 70. VARIABLES WITH USER INPUT
# ============================================================

"""
input() returns a string.

Therefore, numerical input usually needs conversion.
"""

user_name = input("Enter your name: ")

print("Hello,", user_name)


# Example:

# age = input("Enter your age: ")
# age = int(age)
# print(age + 1)


# ============================================================
# 71. INPUT AND VARIABLE TYPES
# ============================================================

"""
Important:

input() -> always returns str
"""

# user_age = input("Enter age: ")
# print(type(user_age))


# ============================================================
# 72. CONVERSION OF VARIABLES
# ============================================================

value = "100"

integer_value = int(value)
float_value = float(value)

print(integer_value)
print(float_value)

print(type(integer_value))
print(type(float_value))


# ============================================================
# 73. BOOLEAN CONVERSION
# ============================================================

value = 1

boolean_value = bool(value)

print(boolean_value)


# ============================================================
# 74. VARIABLE TRUTHINESS
# ============================================================

"""
Many Python objects have a truth value.

Examples of generally false values:

False
None
0
0.0
""
[]
()
{}
set()

Most other objects are generally truthy.
"""

items = []

if items:
    print("Items exist.")
else:
    print("Items are empty.")


# ============================================================
# 75. CONDITIONAL VARIABLE ASSIGNMENT
# ============================================================

age = 20

status = "Adult" if age >= 18 else "Minor"

print(status)


# ============================================================
# 76. VARIABLE SCOPE EXAMPLE
# ============================================================

x = 10


def function_one():
    x = 20
    print("Inside:", x)


function_one()

print("Outside:", x)


# ============================================================
# 77. GLOBAL VS LOCAL
# ============================================================

message = "Global"


def show_message():
    message = "Local"
    print(message)


show_message()
print(message)


# ============================================================
# 78. NONLOCAL EXAMPLE
# ============================================================

def counter_factory():

    count = 0

    def increment():

        nonlocal count

        count += 1

        return count

    return increment


counter = counter_factory()

print(counter())
print(counter())
print(counter())


# ============================================================
# 79. CLOSURE AND VARIABLES
# ============================================================

def multiplier(factor):

    def multiply(number):
        return number * factor

    return multiply


double_number = multiplier(2)
triple_number = multiplier(3)

print(double_number(10))
print(triple_number(10))


# ============================================================
# 80. VARIABLE LIFETIME
# ============================================================

"""
A variable name exists within a particular namespace.

A local variable normally exists while the relevant function
execution and references require it.

An object can continue to exist as long as references to it
remain.
"""


# ============================================================
# 81. LIST ALIASING PROBLEM
# ============================================================

original = [1, 2, 3]

alias = original

alias.append(100)

print("Original:", original)
print("Alias:", alias)


# ============================================================
# 82. LIST COPYING
# ============================================================

original = [1, 2, 3]

copy_one = original.copy()
copy_two = original[:]
copy_three = list(original)

copy_one.append(4)
copy_two.append(5)
copy_three.append(6)

print("Original:", original)
print("copy_one:", copy_one)
print("copy_two:", copy_two)
print("copy_three:", copy_three)


# ============================================================
# 83. NESTED MUTABLE OBJECTS
# ============================================================

"""
A shallow copy copies the outer container but nested objects
can still be shared.
"""

original = [[1, 2], [3, 4]]

shallow_copy = original.copy()

shallow_copy[0].append(99)

print("Original:", original)
print("Shallow copy:", shallow_copy)


# ============================================================
# 84. DEEP COPY
# ============================================================

import copy

original = [[1, 2], [3, 4]]

deep_copy = copy.deepcopy(original)

deep_copy[0].append(99)

print("Original:", original)
print("Deep copy:", deep_copy)


# ============================================================
# 85. VARIABLE ANNOTATIONS WITH COLLECTIONS
# ============================================================

names: list[str] = ["Atul", "Rahul", "Amit"]

scores: list[int] = [80, 90, 95]

user: dict[str, object] = {
    "name": "Atul",
    "age": 30
}

print(names)
print(scores)
print(user)


# ============================================================
# 86. OPTIONAL VALUES
# ============================================================

from typing import Optional

middle_name: Optional[str] = None

middle_name = "Kumar"

print(middle_name)


# ============================================================
# 87. UNION TYPES
# ============================================================

"""
A variable may intentionally accept more than one type.

Modern Python supports:

str | int
"""

identifier: str | int = "EMP001"

print(identifier)

identifier = 1001

print(identifier)


# ============================================================
# 88. CONSTANTS AND CONFIGURATION
# ============================================================

DATABASE_HOST = "localhost"
DATABASE_PORT = 5432
DEBUG_MODE = True

print(DATABASE_HOST)
print(DATABASE_PORT)
print(DEBUG_MODE)


# ============================================================
# 89. ENVIRONMENT VARIABLES
# ============================================================

"""
Operating systems can provide environment variables.

Python can access them using os.environ or os.getenv().
"""

import os

python_path = os.getenv("PATH")

print("PATH exists:", python_path is not None)


# ============================================================
# 90. VARIABLES IN CLASSES
# ============================================================

class Car:

    wheels = 4

    def __init__(self, brand):
        self.brand = brand


car = Car("Toyota")

print(car.brand)
print(car.wheels)


# ============================================================
# 91. CLASS ATTRIBUTE MODIFICATION
# ============================================================

Car.wheels = 6

print(car.wheels)


# ============================================================
# 92. INSTANCE ATTRIBUTE MODIFICATION
# ============================================================

car.brand = "Honda"

print(car.brand)


# ============================================================
# 93. PROPERTY-LIKE BEHAVIOR WITH ATTRIBUTES
# ============================================================

class Account:

    def __init__(self, balance):
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount


account = Account(1000)

account.deposit(500)

print(account.balance)


# ============================================================
# 94. VARIABLES IN EXCEPTION HANDLING
# ============================================================

try:
    result = 10 / 2
except ZeroDivisionError as error:
    print("Error:", error)
else:
    print("Result:", result)


# ============================================================
# 95. EXCEPTION VARIABLE SCOPE
# ============================================================

"""
The variable used with 'except ... as error' is intended for
the exception handling block and Python clears the exception
target after the except clause.

This avoids keeping unnecessary references to the exception.
"""


# ============================================================
# 96. VARIABLES IN WITH STATEMENTS
# ============================================================

"""
The 'as' part of a with statement assigns an object to a name.
"""

from io import StringIO

stream = StringIO("Python variables")

with stream as file_object:
    content = file_object.read()
    print(content)


# ============================================================
# 97. VARIABLES AND IMPORTS
# ============================================================

import math

math_module = math

print(math_module.sqrt(25))


# ============================================================
# 98. VARIABLE NAME LOOKUP
# ============================================================

"""
Python resolves names through namespaces.

A simplified lookup order is:

Local
Enclosing
Global
Built-in
"""

value = "global"


def outer():
    value = "enclosing"

    def inner():
        print(value)

    inner()


outer()


# ============================================================
# 99. PRACTICAL STUDENT RECORD
# ============================================================

student_name: str = "Atul"
student_age: int = 30
student_marks: list[int] = [85, 90, 88]

total_marks = sum(student_marks)
average_marks = total_marks / len(student_marks)

print("Name:", student_name)
print("Age:", student_age)
print("Marks:", student_marks)
print("Total:", total_marks)
print("Average:", average_marks)


# ============================================================
# 100. PRACTICAL EMPLOYEE PAY CALCULATION
# ============================================================

employee_name = "Atul"
basic_salary = 40000
allowance = 10000
deduction = 5000

gross_salary = basic_salary + allowance
net_salary = gross_salary - deduction

print("Employee:", employee_name)
print("Gross Salary:", gross_salary)
print("Net Salary:", net_salary)


# ============================================================
# 101. PRACTICAL SECURITY CHECK
# ============================================================

username = "admin"
password_valid = True
account_active = True

access_granted = password_valid and account_active

if access_granted:
    print(username, "has access.")
else:
    print(username, "does not have access.")


# ============================================================
# 102. PRACTICAL INVENTORY EXAMPLE
# ============================================================

product = "Laptop"
price = 65000
stock = 10

is_available = stock > 0

print("Product:", product)
print("Price:", price)
print("Stock:", stock)
print("Available:", is_available)


# ============================================================
# 103. VARIABLES AND LIST COMPREHENSION
# ============================================================

numbers = [1, 2, 3, 4, 5]

squares = [number ** 2 for number in numbers]

print(squares)


# ============================================================
# 104. VARIABLES AND DICTIONARY COMPREHENSION
# ============================================================

numbers = [1, 2, 3, 4, 5]

square_dictionary = {
    number: number ** 2
    for number in numbers
}

print(square_dictionary)


# ============================================================
# 105. VARIABLES AND SET COMPREHENSION
# ============================================================

numbers = [1, 1, 2, 2, 3, 3]

unique_squares = {
    number ** 2
    for number in numbers
}

print(unique_squares)


# ============================================================
# 106. VARIABLE UNPACKING IN FUNCTION CALLS
# ============================================================

def add_three(a, b, c):
    return a + b + c


values = [10, 20, 30]

result = add_three(*values)

print(result)


# ============================================================
# 107. DICTIONARY UNPACKING
# ============================================================

def introduce(name, age):
    print("Name:", name)
    print("Age:", age)


person_data = {
    "name": "Atul",
    "age": 30
}

introduce(**person_data)


# ============================================================
# 108. VARIABLE REFERENCES AND IMMUTABILITY
# ============================================================

a = 10
b = a

print(a)
print(b)

b = 20

print(a)
print(b)


# ============================================================
# 109. MUTABILITY COMPARISON
# ============================================================

a = [1, 2]
b = a

b.append(3)

print("Mutable object:")
print("a:", a)
print("b:", b)

x = 10
y = x

y += 5

print("Immutable object:")
print("x:", x)
print("y:", y)


# ============================================================
# 110. DEL AND COLLECTION OBJECTS
# ============================================================

numbers = [1, 2, 3]

reference = numbers

del numbers

print(reference)


# ============================================================
# 111. ADVANCED VARIABLE EXAMPLE
# ============================================================

class BankAccount:

    bank_name = "Example Bank"

    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount: float) -> float:
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float) -> float:
        if amount > self.balance:
            raise ValueError("Insufficient balance")

        self.balance -= amount
        return self.balance


account_owner = "Atul"
initial_balance = 10000.0

account = BankAccount(
    account_owner,
    initial_balance
)

deposit_amount = 5000.0
withdraw_amount = 2000.0

account.deposit(deposit_amount)
account.withdraw(withdraw_amount)

print("Owner:", account.owner)
print("Balance:", account.balance)


# ============================================================
# 112. ADVANCED CLOSURE EXAMPLE
# ============================================================

def create_counter(start: int = 0):

    count = start

    def increment(step: int = 1):

        nonlocal count

        count += step

        return count

    return increment


counter = create_counter(100)

print(counter())
print(counter())
print(counter(10))


# ============================================================
# 113. ADVANCED FUNCTION VARIABLE EXAMPLE
# ============================================================

def multiply_by_two(value):
    return value * 2


def multiply_by_three(value):
    return value * 3


operations = {
    "double": multiply_by_two,
    "triple": multiply_by_three
}

print(operations["double"](10))
print(operations["triple"](10))


# ============================================================
# 114. ADVANCED NAMESPACE EXAMPLE
# ============================================================

global_example = "Global value"


def namespace_demo():

    local_example = "Local value"

    print("Local namespace:")
    print(locals())

    print("Global variable:")
    print(globals()["global_example"])


namespace_demo()


# ============================================================
# 115. BEST PRACTICES
# ============================================================

"""
Good variable naming:

student_name
total_price
number_of_users
is_authenticated
has_permission
average_score

Poor naming:

x
a
abc
thing
data1
temp

Short names can be appropriate in small mathematical loops,
but meaningful names are usually better in larger programs.
"""


# ============================================================
# 116. BOOLEAN NAMING
# ============================================================

is_active = True
is_authenticated = False
has_permission = True
can_edit = False

print(is_active)
print(is_authenticated)
print(has_permission)
print(can_edit)


# ============================================================
# 117. AVOID REUSING A VARIABLE FOR UNRELATED PURPOSES
# ============================================================

"""
Avoid:

data = "Atul"
data = 100
data = [1, 2, 3]

Prefer meaningful names:
"""

user_name = "Atul"
age = 100
numbers = [1, 2, 3]

print(user_name)
print(age)
print(numbers)


# ============================================================
# 118. FINAL PRACTICAL MINI PROJECT
# ============================================================

"""
Simple Employee Payroll Program

This combines:

- variables
- data types
- input
- type conversion
- arithmetic
- Boolean values
- conditions
- formatted output
- type hints
"""

employee_name: str = "Atul"
basic_salary: float = 50000.0
housing_allowance: float = 10000.0
transport_allowance: float = 5000.0
tax_rate: float = 10.0

gross_salary: float = (
    basic_salary
    + housing_allowance
    + transport_allowance
)

tax_amount: float = (
    gross_salary * tax_rate / 100
)

net_salary: float = gross_salary - tax_amount

is_taxable: bool = gross_salary > 0

print("\n========== EMPLOYEE PAYSLIP ==========")
print("Employee:", employee_name)
print("Basic Salary:", basic_salary)
print("Housing Allowance:", housing_allowance)
print("Transport Allowance:", transport_allowance)
print("Gross Salary:", gross_salary)
print("Tax Rate:", tax_rate)
print("Tax Amount:", tax_amount)
print("Net Salary:", net_salary)
print("Taxable:", is_taxable)


# ============================================================
# 119. FINAL CONCEPTUAL SUMMARY
# ============================================================

"""
Important ideas to remember:

1. A variable is a name referring to an object.
2. Python uses assignment to bind names to objects.
3. Python is dynamically typed.
4. A variable can refer to objects of different types at
   different times.
5. type() can be used to inspect an object's type.
6. isinstance() can test whether an object is an instance of
   a specified type.
7. Variables do not contain values in the same conceptual way
   as boxes in some beginner explanations; they refer to objects.
8. Multiple variables can refer to the same object.
9. Mutable objects can be changed.
10. Immutable objects cannot be changed in place.
11. == compares values.
12. is compares object identity.
13. Local variables belong to local scope.
14. Global variables belong to module/global scope.
15. nonlocal allows a nested function to modify a variable from
    an enclosing function scope.
16. Python follows the LEGB name-resolution rule.
17. Type hints document expected types but generally do not
    enforce them at runtime.
18. Constants are normally represented using uppercase names.
19. Functions are objects and can be assigned to variables.
20. Classes contain class attributes and can create instance
    attributes.
21. locals() and globals() expose namespace dictionaries.
22. del removes a name binding.
23. Unpacking allows multiple variables to receive values from
    an iterable.
24. The walrus operator := performs assignment within an
    expression.
25. Good variable names make programs easier to read and maintain.
"""


print("\n==========================================")
print("PYTHON VARIABLES - COMPLETE LESSON FINISHED")
print("==========================================")
