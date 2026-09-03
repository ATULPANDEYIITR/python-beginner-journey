# Variables in Python

## Introduction

A variable in Python is a name used to refer to an object stored in memory.

Variables allow us to store information and use that information later in a program.

For example:

```
name = "Atul"
age = 25
salary = 50000
```

Here:

* `name` refers to the string `"Atul"`
* `age` refers to the integer `25`
* `salary` refers to the integer `50000`

Python variables do not require an explicit declaration of their data type. Python determines the type automatically from the value assigned to the variable.

## Creating a Variable

A variable is created when a value is assigned to a name.

```
name = "Atul"
age = 25
height = 5.9
is_student = True
```

The general syntax is:

```
variable_name = value
```

The `=` operator is called the assignment operator.

It assigns the object on the right-hand side to the variable name on the left-hand side.

## Basic Variable Examples

```
name = "Atul"
age = 25
city = "Lucknow"
temperature = 32.5
is_active = True

print(name)
print(age)
print(city)
print(temperature)
print(is_active)
```

## Variable Naming Rules

Python has specific rules for naming variables.

A variable name:

* Can contain letters
* Can contain numbers
* Can contain underscores
* Cannot start with a number
* Cannot contain spaces
* Cannot contain special characters such as `@`, `$`, `%`, `!`
* Cannot be a Python keyword
* Is case-sensitive

Valid examples:

```
name = "Atul"
age2 = 30
user_name = "admin"
total_amount = 5000
```

Invalid examples:

```
2age = 30
user-name = "Atul"
user name = "Atul"
@name = "Atul"
```

Python variable names are case-sensitive.

```
name = "Atul"
Name = "Rahul"
NAME = "Amit"
```

These are three different variables.

## Variable Naming Conventions

Python generally follows the `snake_case` naming convention.

```
first_name = "Atul"
last_name = "Pandey"
total_salary = 75000
employee_count = 100
```

Constants are commonly written using uppercase letters.

```
MAX_CONNECTIONS = 100
PI = 3.14159
DATABASE_TIMEOUT = 30
```

Python does not technically enforce constants. Uppercase naming is a convention that tells other programmers that the value should not normally be changed.

## Assignment and Reassignment

A variable can be reassigned.

```
age = 25
print(age)

age = 26
print(age)
```

The variable `age` first refers to `25` and later refers to `26`.

A variable can also change from one data type to another.

```
value = 100
print(value)

value = "Python"
print(value)
```

This is possible because Python uses dynamic typing.

## Dynamic Typing

Python is dynamically typed.

This means that a variable does not have a permanently fixed data type.

```
value = 100
print(type(value))

value = "Python"
print(type(value))

value = 3.14
print(type(value))
```

The variable name `value` can refer to objects of different types at different times.

## Checking the Type of a Variable

The `type()` function tells us the type of an object.

```
age = 25
print(type(age))

name = "Atul"
print(type(name))

salary = 50000.50
print(type(salary))

active = True
print(type(active))
```

## Using isinstance()

`isinstance()` checks whether an object belongs to a particular type.

```
age = 25

print(isinstance(age, int))
print(isinstance(age, str))
```

It returns either `True` or `False`.

Multiple types can also be checked.

```
value = 25

print(isinstance(value, (int, float)))
```

## Common Data Types Stored in Variables

### Integer

Integers are whole numbers.

```
age = 25
count = 100
temperature = -10
```

### Float

Floats represent decimal numbers.

```
price = 99.99
height = 5.9
temperature = 36.5
```

### Complex

Complex numbers contain a real and imaginary component.

```
number = 3 + 4j
```

### String

Strings contain text.

```
name = "Atul"
language = "Python"
```

### Boolean

Boolean values are either `True` or `False`.

```
is_logged_in = True
is_admin = False
```

### None

`None` represents the absence of a value.

```
result = None
```

The type of `None` is `NoneType`.

```
print(type(result))
```

## String Variables

Strings can be created using single or double quotation marks.

```
name = "Atul"
city = 'Lucknow'
```

String variables support many operations.

```
first_name = "Atul"
last_name = "Pandey"

full_name = first_name + " " + last_name

print(full_name)
```

Strings can also be formatted using f-strings.

```
name = "Atul"
age = 25

message = f"My name is {name} and I am {age} years old."

print(message)
```

## Numeric Variables

Python supports arithmetic operations on numeric variables.

```
a = 10
b = 3

print(a + b)
print(a - b)
print(a * b)
print(a / b)
print(a // b)
print(a % b)
print(a ** b)
```

## Boolean Variables

Boolean variables are useful for representing conditions.

```
is_authenticated = True
has_permission = False
```

They are commonly used with conditional statements.

```
if is_authenticated:
    print("Access granted")
else:
    print("Access denied")
```

## Collection Variables

Python variables can refer to collections.

### List

```
numbers = [10, 20, 30, 40]
```

### Tuple

```
coordinates = (10, 20)
```

### Set

```
unique_numbers = {10, 20, 30}
```

### Dictionary

```
user = {
    "name": "Atul",
    "age": 25
}
```

## Multiple Assignment

Python allows multiple variables to be assigned in one statement.

```
name, age, city = "Atul", 25, "Lucknow"
```

This is equivalent to assigning the values individually.

```
name = "Atul"
age = 25
city = "Lucknow"
```

## Assigning the Same Value to Multiple Variables

Multiple variables can refer to the same value.

```
x = y = z = 100

print(x)
print(y)
print(z)
```

## Variable Unpacking

Values from an iterable can be assigned to multiple variables.

```
numbers = [10, 20, 30]

a, b, c = numbers

print(a)
print(b)
print(c)
```

## Extended Unpacking

The `*` operator can collect multiple values.

```
numbers = [10, 20, 30, 40, 50]

first, *middle, last = numbers

print(first)
print(middle)
print(last)
```

## Swapping Variables

Python allows variables to be swapped without using a temporary variable.

```
a = 10
b = 20

a, b = b, a

print(a)
print(b)
```

## Variables and Objects

In Python, variables are names that refer to objects.

For example:

```
age = 25
```

The integer object `25` exists in memory, and the name `age` refers to that object.

A useful way to understand Python variables is:

```
variable_name -> object
```

The variable itself is not the actual value. It is a reference to an object.

## Using id()

The `id()` function returns the identity of an object.

```
value = 100

print(id(value))
```

Two variables may refer to the same object.

```
a = 100
b = a

print(id(a))
print(id(b))
```

## Equality and Identity

`==` checks whether two objects have equal values.

`is` checks whether two variables refer to the same object.

```
a = [1, 2, 3]
b = [1, 2, 3]

print(a == b)
print(a is b)
```

The first comparison checks value equality.

The second checks object identity.

A common and important use of `is` is checking for `None`.

```
result = None

if result is None:
    print("No result")
```

## Aliasing

When two variables refer to the same mutable object, they are aliases.

```
numbers = [1, 2, 3]

another_numbers = numbers

another_numbers.append(4)

print(numbers)
print(another_numbers)
```

Both variables refer to the same list.

## Mutable and Immutable Objects

Some Python objects can be modified after creation. These are called mutable objects.

Examples include:

* Lists
* Dictionaries
* Sets

Some objects cannot be modified after creation. These are immutable objects.

Examples include:

* Integers
* Floats
* Strings
* Tuples
* Booleans

Example of a mutable object:

```
numbers = [1, 2, 3]
numbers.append(4)
```

Example of an immutable object:

```
name = "Python"
name = name + " Programming"
```

The original string is not modified. A new string object is created.

## Copying Variables

Consider:

```
original = [1, 2, 3]
copy = original
```

Changing `copy` also changes `original` because both names refer to the same list.

To create a separate list:

```
original = [1, 2, 3]
copy = original.copy()

copy.append(4)

print(original)
print(copy)
```

## Shallow Copy

A shallow copy creates a new outer object but does not recursively copy nested objects.

```
original = [[1, 2], [3, 4]]

copy = original.copy()

copy.append([5, 6])

print(original)
print(copy)
```

For nested mutable structures, the inner objects may still be shared.

## Deep Copy

`copy.deepcopy()` recursively copies nested objects.

```
import copy

original = [[1, 2], [3, 4]]

deep_copy = copy.deepcopy(original)

deep_copy[0].append(100)

print(original)
print(deep_copy)
```

## Local Variables

A variable created inside a function is normally local to that function.

```
def calculate():
    result = 100
    print(result)

calculate()
```

The variable `result` belongs to the local scope of the function.

## Function Parameters

Function parameters are variables available inside the function.

```
def greet(name):
    print(f"Hello, {name}")

greet("Atul")
```

Here, `name` is a parameter variable.

## Return Values Stored in Variables

A function can return a value that is stored in a variable.

```
def add(a, b):
    return a + b

result = add(10, 20)

print(result)
```

## Global Variables

A variable created outside a function belongs to the global scope.

```
company = "ABC Technologies"

def show_company():
    print(company)

show_company()
```

A function can read a global variable if it is accessible from that scope.

## The global Keyword

The `global` keyword allows a function to modify a global variable.

```
counter = 0

def increment():
    global counter
    counter += 1

increment()

print(counter)
```

Using global variables excessively can make programs harder to understand, so they should generally be used carefully.

## The nonlocal Keyword

`nonlocal` is used inside nested functions when we want to modify a variable belonging to an enclosing function.

```
def outer():
    value = 10

    def inner():
        nonlocal value
        value += 1
        print(value)

    inner()

outer()
```

## LEGB Rule

Python searches for variable names according to the LEGB rule.

LEGB stands for:

* Local
* Enclosing
* Global
* Built-in

Python searches these scopes in that order when resolving a variable name.

## Variable Shadowing

A variable in a narrower scope can have the same name as a variable in a wider scope.

```
name = "Global"

def show():
    name = "Local"
    print(name)

show()

print(name)
```

The local variable shadows the global variable inside the function.

## Avoiding Built-in Name Shadowing

Python provides built-in functions such as:

```
print()
len()
type()
sum()
list()
str()
```

It is better not to use these names for variables.

Avoid:

```
list = [1, 2, 3]
str = "Python"
sum = 100
```

Prefer:

```
numbers = [1, 2, 3]
text = "Python"
total = 100
```

## Variable Annotations

Python allows variables to have type annotations.

```
age: int = 25
name: str = "Atul"
salary: float = 50000.0
active: bool = True
```

Type annotations provide information about the expected type.

Python does not normally enforce these annotations at runtime.

## Type Hints

Type hints can make code easier to understand.

```
def calculate_salary(basic: float, bonus: float) -> float:
    return basic + bonus
```

The annotations communicate the expected types of the parameters and return value.

## Union Type Hints

Modern Python supports union syntax.

```
user_id: int | str = 101
```

This indicates that the variable may contain either an integer or a string.

## Functions as Variables

Functions are objects in Python and can be assigned to variables.

```
def greet():
    print("Hello")

message_function = greet

message_function()
```

## Lambda Functions Stored in Variables

A lambda function can also be assigned to a variable.

```
square = lambda x: x * x

print(square(5))
```

## Variables Containing Classes

Classes can also be assigned to variables.

```
class Person:
    pass

PersonClass = Person

person = PersonClass()
```

## Instance Variables

Instance variables belong to individual objects.

```
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

employee = Employee("Atul", 50000)

print(employee.name)
print(employee.salary)
```

Here, `name` and `salary` are instance attributes.

## Class Variables

Class variables belong to the class and can be shared among instances.

```
class Employee:
    company = "ABC Technologies"

    def __init__(self, name):
        self.name = name

employee1 = Employee("Atul")
employee2 = Employee("Rahul")

print(employee1.company)
print(employee2.company)
```

## Namespaces

A namespace is a mapping between names and objects.

Different parts of a Python program can have different namespaces.

Examples include:

* Local namespace
* Global namespace
* Built-in namespace
* Class namespace

The namespace concept helps Python determine which object a variable name refers to.

## globals()

`globals()` returns a dictionary representing the current global namespace.

```
name = "Atul"

print(globals()["name"])
```

It can be useful for inspecting global variables, although it should not normally be used as a substitute for clear variable design.

## locals()

`locals()` provides access to the current local namespace.

```
def show_variables():
    name = "Atul"
    age = 25

    print(locals())

show_variables()
```

## Deleting a Variable

The `del` statement removes a name.

```
value = 100

print(value)

del value
```

After deletion, attempting to access `value` will result in a `NameError`.

## Variable Lifetime

A variable name exists while it remains bound to an object within its relevant scope.

Local variables are generally created when a function executes and become unavailable as local names after the function finishes.

Global variables can remain available for the lifetime of the running program unless explicitly removed or their namespace is otherwise changed.

## Reference Counting Concept

In CPython, objects are primarily managed using reference counting along with a garbage collector for certain reference cycles.

When variables refer to an object, they contribute references to that object.

```
a = [1, 2, 3]
b = a
```

Both `a` and `b` refer to the same object.

When references are removed, the object may eventually become eligible for memory cleanup.

Python developers generally do not need to manually manage memory for ordinary variables.

## Augmented Assignment

Python provides operators that combine an operation with assignment.

```
value = 10

value += 5
value -= 2
value *= 3
value /= 2
```

Other augmented operators include:

```
value //= 2
value %= 2
value **= 2
```

## User Input Stored in Variables

The `input()` function allows a program to receive input from the user.

```
name = input("Enter your name: ")

print(f"Hello, {name}")
```

`input()` always returns a string.

If numeric input is required, it must be converted.

```
age = int(input("Enter your age: "))

print(age)
```

## Type Conversion

Variables can be converted between compatible data types.

```
value = "100"

number = int(value)

print(number)
print(type(number))
```

Other common conversions include:

```
int()
float()
str()
bool()
```

Example:

```
price = "99.50"

amount = float(price)

print(amount)
```

## Truthiness

Python evaluates many objects as either truthy or falsy in conditions.

Examples of commonly falsy values include:

```
False
None
0
0.0
""
[]
()
{}
set()
```

Example:

```
name = ""

if name:
    print("Name is available")
else:
    print("Name is empty")
```

## Conditional Expressions

A value can be assigned using a conditional expression.

```
age = 25

status = "Adult" if age >= 18 else "Minor"

print(status)
```

## Dictionary Variables

Dictionaries store key-value pairs.

```
employee = {
    "name": "Atul",
    "age": 25,
    "department": "Security"
}
```

Values can be accessed using keys.

```
name = employee["name"]
age = employee["age"]

print(name)
print(age)
```

## Nested Variable Structures

Variables can contain complex structures.

```
employee = {
    "name": "Atul",
    "skills": ["Python", "SQL", "Git"],
    "address": {
        "city": "Lucknow",
        "country": "India"
    }
}
```

Nested values can be accessed through multiple levels.

```
print(employee["skills"][0])
print(employee["address"]["city"])
```

## Unpacking Function Arguments

The `*` operator can unpack a sequence into positional arguments.

```
def add(a, b, c):
    return a + b + c

numbers = [10, 20, 30]

result = add(*numbers)

print(result)
```

The `**` operator can unpack a dictionary into keyword arguments.

```
def introduce(name, age):
    print(name, age)

person = {
    "name": "Atul",
    "age": 25
}

introduce(**person)
```

## Comprehension Variables

Variables are frequently used inside comprehensions.

List comprehension:

```
numbers = [1, 2, 3, 4, 5]

squares = [number ** 2 for number in numbers]

print(squares)
```

Dictionary comprehension:

```
numbers = [1, 2, 3, 4]

squares = {number: number ** 2 for number in numbers}

print(squares)
```

Set comprehension:

```
numbers = [1, 2, 2, 3, 3, 4]

unique_squares = {number ** 2 for number in numbers}

print(unique_squares)
```

## Exception Variables

An exception object can be assigned to a variable.

```
try:
    number = int("abc")
except ValueError as error:
    print(error)
```

Here, `error` contains information about the exception.

## Variables with with Statements

The `as` keyword can assign an object to a variable inside a `with` statement.

```
with open("example.txt", "w") as file:
    file.write("Hello Python")
```

Here, `file` refers to the file object managed by the context manager.

## Imported Modules as Variables

When importing a module, the module object can be accessed through a variable-like name.

```
import math

result = math.sqrt(25)

print(result)
```

An import alias can also be created.

```
import math as mathematics

print(mathematics.sqrt(25))
```

## Environment Variables

Environment variables can be accessed using the `os` module.

```
import os

username = os.getenv("USERNAME")

print(username)
```

Environment variables are commonly used for configuration information such as application settings and credentials.

Sensitive credentials should not be hard-coded directly into Python source files.

## Closures and Variables

A nested function can remember variables from its enclosing function.

```
def multiplier(factor):
    def multiply(number):
        return number * factor

    return multiply

double = multiplier(2)

print(double(10))
```

The inner function remembers the value of `factor`.

## Practical Example: Salary Calculation

```
basic_salary = 50000
allowance = 10000
bonus = 5000

total_salary = basic_salary + allowance + bonus

print("Basic Salary:", basic_salary)
print("Allowance:", allowance)
print("Bonus:", bonus)
print("Total Salary:", total_salary)
```

## Practical Example: Security Access Check

```
username = "admin"
password = "secure123"

entered_username = input("Enter username: ")
entered_password = input("Enter password: ")

if entered_username == username and entered_password == password:
    print("Access granted")
else:
    print("Access denied")
```

In real applications, passwords should never be stored directly in source code like this. Secure authentication systems and protected credential storage should be used.

## Practical Example: Inventory Management

```
product_name = "Laptop"
quantity = 25
price = 65000

inventory_value = quantity * price

print("Product:", product_name)
print("Quantity:", quantity)
print("Price:", price)
print("Inventory Value:", inventory_value)
```

## Practical Example: Employee Record

```
employee_name = "Atul Pandey"
employee_id = 101
department = "Security"
salary = 55000
is_active = True

print("Employee Name:", employee_name)
print("Employee ID:", employee_id)
print("Department:", department)
print("Salary:", salary)
print("Active:", is_active)
```

## Practical Example: Multiple Assignment

```
employee_name, employee_id, salary = "Atul", 101, 55000

print(employee_name)
print(employee_id)
print(salary)
```

## Practical Example: Variable References

```
first_list = [10, 20, 30]
second_list = first_list

second_list.append(40)

print(first_list)
print(second_list)
```

Because both variables refer to the same list object, modifying one affects the other.

## Best Practices for Variables

Use descriptive names.

```
total_salary = 75000
```

is better than:

```
x = 75000
```

Use `snake_case` for normal variable names.

```
employee_name = "Atul"
```

Avoid unnecessary abbreviations.

```
employee_count = 100
```

is generally clearer than:

```
emp_cnt = 100
```

Avoid using Python built-in names as variables.

Do not unnecessarily use global variables.

Keep variables meaningful and related to the data they represent.

Use type annotations when they improve readability.

```
employee_id: int = 101
```

Use constants in uppercase by convention.

```
MAX_USERS = 1000
```

Use `is None` when checking for `None`.

```
if result is None:
    print("No result")
```

Do not rely on `is` for normal value comparison.

Use:

```
if value == 10:
    print("Value is 10")
```

rather than:

```
if value is 10:
    print("Value is 10")
```

## Important Concepts Covered

Variables in Python are names that reference objects.

Variables are created through assignment.

Python uses dynamic typing.

A variable can refer to objects of different types during program execution.

The `type()` function identifies an object's type.

The `isinstance()` function checks whether an object belongs to a particular type.

Variables can contain integers, floats, strings, booleans, complex numbers, lists, tuples, sets, dictionaries and other Python objects.

Multiple assignment allows several variables to be assigned in one statement.

Unpacking allows values from collections to be assigned to variables.

The `*` operator can be used for extended unpacking and argument unpacking.

The `**` operator can unpack dictionaries into keyword arguments.

Python variables are references to objects.

The `id()` function can be used to inspect object identity.

`==` compares values while `is` compares object identity.

Mutable objects can be modified after creation.

Immutable objects cannot be modified after creation.

Aliasing occurs when multiple variable names refer to the same object.

Local, enclosing, global and built-in scopes are resolved according to the LEGB rule.

The `global` keyword allows modification of global variables from inside functions.

The `nonlocal` keyword allows modification of variables from an enclosing function scope.

Type annotations can document expected variable types.

Functions, classes and modules are also objects that can be referenced by variables.

`globals()` and `locals()` provide access to namespace dictionaries.

The `del` statement removes a variable binding.

Augmented assignment operators provide shorthand for common operations.

The `input()` function returns user input as a string.

Type conversion can be performed using functions such as `int()`, `float()`, `str()` and `bool()`.

Python supports truthy and falsy values.

Variables are fundamental to almost every Python program because they allow programs to store, reference, modify and process information.

