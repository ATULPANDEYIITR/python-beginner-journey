# Python Syntax and Comments

# A detailed executable learning script

"""
PYTHON SYNTAX AND COMMENTS

Python syntax is the collection of rules that determines how Python code
must be written and interpreted. Syntax includes indentation, statements,
expressions, identifiers, keywords, blocks, delimiters, whitespace, line
continuation, and comments.

Comments are pieces of explanatory text written inside source code that
are generally ignored by the Python interpreter during execution.

This script demonstrates Python syntax and comments from basic concepts
to more detailed language-level behavior.
"""

# =============================================================================

# 1. PYTHON STATEMENTS

# =============================================================================

# A statement is an instruction that Python can execute.

print("Python Syntax and Comments")

# Python reads statements according to the language grammar.

name = "Python"
version = 3

print(name)
print(version)

# A single line can contain multiple statements separated by semicolons.

# This syntax is valid, although it is generally less readable.

language = "Python"; category = "Programming Language"

print(language)
print(category)

# =============================================================================

# 2. INDENTATION

# =============================================================================

# Python uses indentation to define blocks of code.

# Unlike languages that commonly use braces {}, Python uses leading whitespace.

score = 85

if score >= 50:
print("The score is passing.")

# The indented statement belongs to the if block.

if score >= 90:
print("Grade: A")
elif score >= 75:
print("Grade: B")
else:
print("Grade: C")

# Consistent indentation is essential.

# Correct:

number = 10

if number > 0:
print("Positive number")
print("The condition evaluated to True")

# Incorrect indentation would produce an IndentationError.

#

# if number > 0:

# print("Positive number")

#

# The print statement must be indented because it belongs to the if block.

# =============================================================================

# 3. INDENTATION LEVELS AND NESTED BLOCKS

# =============================================================================

number = 12

if number > 0:
if number % 2 == 0:
print("The number is positive and even.")
else:
print("The number is positive and odd.")

# Each nested block has an additional indentation level.

# =============================================================================

# 4. WHITESPACE IN PYTHON

# =============================================================================

# Whitespace refers to spaces, tabs, and line breaks.

# Python uses whitespace structurally for indentation, but spaces around

# operators are primarily used for readability.

a = 10
b = 20

total = a + b

print(total)

# These expressions are interpreted similarly:

result_one = a+b
result_two = a + b

print(result_one)
print(result_two)

# The second style is generally easier to read.

# =============================================================================

# 5. IDENTIFIERS

# =============================================================================

# Identifiers are names given to variables, functions, classes, modules,

# and other Python objects.

student_name = "Aman"
student_age = 21
course_2026 = "Python"

print(student_name)
print(student_age)
print(course_2026)

# Rules for identifiers:

#

# 1. They may contain letters, digits, and underscores.

# 2. They cannot begin with a digit.

# 3. They cannot contain spaces.

# 4. They cannot use most special characters.

# 5. They cannot be Python keywords.

# 6. Python identifiers are case-sensitive.

first_name = "Rahul"
First_Name = "Different identifier"
FIRST_NAME = "Another identifier"

print(first_name)
print(First_Name)
print(FIRST_NAME)

# =============================================================================

# 6. VALID AND INVALID IDENTIFIER EXAMPLES

# =============================================================================

valid_identifier = True
_private_name = "Allowed"
value2 = 100
student_marks = 95

# Invalid examples are shown as comments because executing them would

# cause a SyntaxError.

# 2value = 10

# student name = "Rahul"

# class = "Python"

# total-marks = 100

# =============================================================================

# 7. PYTHON KEYWORDS

# =============================================================================

# Keywords are reserved words with special meaning in Python.

# Examples include:

#

# False     None      True

# and       as        assert

# async     await     break

# class     continue  def

# del       elif      else

# except    finally   for

# from      global    if

# import    in        is

# lambda    nonlocal  not

# or        pass      raise

# return    try       while

# with      yield

# A keyword cannot normally be used as an identifier.

# if = 10

# class = "Programming"

# The keyword module can be used to inspect Python's keyword collection.

import keyword

print("Python keywords:")
print(keyword.kwlist)

# =============================================================================

# 8. CASE SENSITIVITY

# =============================================================================

# Python is case-sensitive.

message = "lowercase"
Message = "capitalized"

print(message)
print(Message)

# These are two different identifiers.

# =============================================================================

# 9. PYTHON COMMENTS

# =============================================================================

# A single-line comment begins with the hash symbol.

print("Comments improve source code readability.")

# The Python interpreter generally ignores comments during execution.

# =============================================================================

# 10. INLINE COMMENTS

# =============================================================================

age = 25  # Store the age of the student

print(age)

# Inline comments appear after executable code on the same physical line.

# They should be used carefully because excessive inline comments can reduce

# readability.

# =============================================================================

# 11. COMMENTS ON SEPARATE LINES

# =============================================================================

# Calculate the total price.

price = 500

# Calculate the quantity.

quantity = 3

# Multiply price by quantity.

total_price = price * quantity

print(total_price)

# =============================================================================

# 12. MULTI-LINE EXPLANATORY TEXT

# =============================================================================

# Python does not have a separate built-in multi-line comment token.

# Multiple lines can be commented individually.

# This is a comment.

# This is another comment.

# This is a third comment.

# Triple-quoted strings are often used as multi-line explanatory text.

"""
This text spans multiple lines.

It is technically a string literal.
It is not automatically a special multi-line comment.
"""

# =============================================================================

# 13. STRING LITERALS AND COMMENTS

# =============================================================================

text = "# This is part of a string, not a comment."

print(text)

# Python distinguishes between a hash character inside a string and a hash

# character beginning a comment.

# =============================================================================

# 14. COMMENTS ARE NOT EXECUTED

# =============================================================================

number = 10

# number = 1000

print(number)

# The assignment inside the comment has no effect on execution.

# =============================================================================

# 15. DOCUMENTATION STRINGS OR DOCSTRINGS

# =============================================================================

# A docstring is a string literal used to document modules, functions,

# classes, and methods.

def calculate_square(number):
"""
Return the square of a numeric value.

```
The function accepts a number and multiplies it by itself.
"""
return number * number
```

print(calculate_square(5))
print(calculate_square.**doc**)

# =============================================================================

# 16. COMMENTS VERSUS DOCSTRINGS

# =============================================================================

# Comments:

# - Begin with

# - Are primarily intended for source-code readers

# - Are ignored by the Python interpreter as executable instructions

def example_function():
"""
This is a docstring.

```
It can be accessed programmatically.
"""
print("Function executed")
```

print(example_function.**doc**)

# =============================================================================

# 17. BASIC PYTHON SYNTAX WITH VARIABLES

# =============================================================================

city = "Lucknow"
population = 3500000
is_capital = True

print(city)
print(population)
print(is_capital)

# Assignment syntax follows this general form:

#

# identifier = value

# =============================================================================

# 18. EXPRESSIONS

# =============================================================================

# An expression produces a value.

addition = 10 + 5
multiplication = 10 * 5
comparison = 10 > 5

print(addition)
print(multiplication)
print(comparison)

# =============================================================================

# 19. STATEMENTS VERSUS EXPRESSIONS

# =============================================================================

# Expression:

value = 10 + 20

# Statement:

print(value)

# An expression calculates or evaluates a value.

# A statement performs an action or controls program execution.

# =============================================================================

# 20. FUNCTION SYNTAX

# =============================================================================

def greet(person):
print("Hello,", person)

greet("Student")

# Function structure:

#

# def function_name(parameters):

# indented_block

# =============================================================================

# 21. FUNCTION RETURN SYNTAX

# =============================================================================

def add_numbers(first, second):
return first + second

answer = add_numbers(10, 20)

print(answer)

# =============================================================================

# 22. CONDITIONAL SYNTAX

# =============================================================================

temperature = 32

if temperature > 30:
print("High temperature")
elif temperature == 30:
print("Temperature is exactly 30")
else:
print("Temperature is below 30")

# =============================================================================

# 23. COLONS IN PYTHON SYNTAX

# =============================================================================

# A colon often introduces an indented block.

value = 7

if value > 0:
print("Positive")

# Colons also appear in:

#

# - Function definitions

# - Class definitions

# - Loops

# - Exception handling

# - Dictionary key-value pairs

# - Slices

# =============================================================================

# 24. FOR LOOP SYNTAX

# =============================================================================

for number in range(1, 6):
print(number)

# The loop header ends with a colon.

# The loop body is indented.

# =============================================================================

# 25. WHILE LOOP SYNTAX

# =============================================================================

counter = 1

while counter <= 3:
print("Counter:", counter)
counter += 1

# =============================================================================

# 26. EMPTY BLOCKS AND PASS

# =============================================================================

# Python blocks cannot normally be completely empty.

def future_feature():
pass

future_feature()

# pass is a statement that performs no operation.

# It can serve as a syntactic placeholder.

# =============================================================================

# 27. LINE BREAKS

# =============================================================================

# Python normally treats a newline as the end of a statement.

x = 10
y = 20

print(x + y)

# =============================================================================

# 28. IMPLICIT LINE CONTINUATION

# =============================================================================

# Python allows expressions to continue across multiple lines when enclosed

# within parentheses, square brackets, or curly braces.

total = (
10
+ 20
+ 30
)

print(total)

numbers = [
10,
20,
30,
40
]

print(numbers)

# =============================================================================

# 29. EXPLICIT LINE CONTINUATION

# =============================================================================

# A backslash can explicitly continue a statement.

calculation = 10 + 20 + 
30 + 40

print(calculation)

# Parentheses are often clearer and less error-prone than backslash-based

# continuation.

# =============================================================================

# 30. PARENTHESES, BRACKETS, AND BRACES

# =============================================================================

# Parentheses: function calls, grouping, tuples

result = (10 + 5) * 2
print(result)

coordinates = (10, 20)
print(coordinates)

# Square brackets: lists and indexing

languages = ["Python", "Java", "C++"]
print(languages[0])

# Curly braces: dictionaries and sets

student = {
"name": "Aman",
"age": 21
}

print(student)

unique_numbers = {1, 2, 3, 3, 2}
print(unique_numbers)

# =============================================================================

# 31. COMMAS IN PYTHON SYNTAX

# =============================================================================

numbers = [1, 2, 3, 4]

print(numbers)

coordinates = (10, 20)

print(coordinates)

# Commas separate elements and arguments.

print("Python", "Syntax", "Comments")

# =============================================================================

# 32. TRAILING COMMAS

# =============================================================================

# A trailing comma is allowed in many Python structures.

languages = [
"Python",
"Java",
"C++",
]

print(languages)

single_item_tuple = ("Python",)

print(single_item_tuple)

# The comma is important for identifying a single-item tuple.

# =============================================================================

# 33. STRING QUOTATION SYNTAX

# =============================================================================

single_quoted = 'Python'
double_quoted = "Programming"

print(single_quoted)
print(double_quoted)

multi_line_text = """
Python supports
multi-line strings.
"""

print(multi_line_text)

# =============================================================================

# 34. ESCAPE CHARACTERS

# =============================================================================

message = "Python is called a "high-level" language."

print(message)

path_example = "C:\Users\Student"

print(path_example)

# Common escape sequences include:

#

# \n  New line

# \t  Tab

# \  Backslash

# "  Double quotation mark

# '  Single quotation mark

# =============================================================================

# 35. RAW STRINGS

# =============================================================================

windows_path = r"C:\Users\Student\Documents"

print(windows_path)

# The r prefix creates a raw string, reducing the interpretation of many

# backslash escape sequences.

# =============================================================================

# 36. PYTHON BLOCK STRUCTURE

# =============================================================================

def analyze_number(number):
if number > 0:
if number % 2 == 0:
return "Positive even number"
return "Positive odd number"

```
if number < 0:
    return "Negative number"

return "Zero"
```

print(analyze_number(8))
print(analyze_number(-5))
print(analyze_number(0))

# =============================================================================

# 37. COMMENTS FOR LOGICAL SECTIONS

# =============================================================================

# A useful comment explains why code exists, assumptions being made,

# constraints, unusual decisions, or non-obvious behavior.

# Limit processing to the first 100 records to prevent excessive memory use.

records = list(range(1000))
limited_records = records[:100]

print(len(limited_records))

# =============================================================================

# 38. UNHELPFUL COMMENTS

# =============================================================================

# The following type of comment usually adds little information:

number = 10  # Assign 10 to number

# The code itself already communicates the operation clearly.

# A more useful comment would explain context:

maximum_login_attempts = 5  # Security policy requires account review after repeated failures.

# =============================================================================

# 39. COMMENTING OUT CODE

# =============================================================================

status = "Active"

# print("This line is temporarily disabled.")

print(status)

# Commenting out code can be useful during temporary debugging, but long-term

# disabled code is generally better managed through version control.

# =============================================================================

# 40. SYNTAX ERRORS

# =============================================================================

# A SyntaxError occurs when Python source code violates the grammar rules.

# Missing colon example:

#

# if True

# print("Invalid")

# Invalid indentation example:

#

# if True:

# print("Invalid")

# Unclosed string example:

#

# text = "Python

# =============================================================================

# 41. SYNTAX ERRORS ARE DIFFERENT FROM RUNTIME ERRORS

# =============================================================================

# This code is syntactically valid:

dividend = 10
divisor = 0

# But division by zero would create a runtime error.

# The following line remains commented to keep this educational script running.

# result = dividend / divisor

# =============================================================================

# 42. PYTHON'S DYNAMIC TYPING AND SYNTAX

# =============================================================================

value = 100
print(value)

value = "Python"
print(value)

# The assignment syntax remains valid even when the type of the object changes.

# =============================================================================

# 43. MULTIPLE ASSIGNMENT

# =============================================================================

first, second = 10, 20

print(first)
print(second)

# Python supports unpacking syntax.

a, b, c = [1, 2, 3]

print(a, b, c)

# =============================================================================

# 44. CHAINED ASSIGNMENT

# =============================================================================

x = y = z = 100

print(x)
print(y)
print(z)

# =============================================================================

# 45. AUGMENTED ASSIGNMENT

# =============================================================================

counter = 10

counter += 5
print(counter)

counter -= 2
print(counter)

counter *= 3
print(counter)

# =============================================================================

# 46. COMPARISON OPERATORS

# =============================================================================

first_value = 10
second_value = 20

print(first_value == second_value)
print(first_value != second_value)
print(first_value < second_value)
print(first_value > second_value)
print(first_value <= second_value)
print(first_value >= second_value)

# =============================================================================

# 47. BOOLEAN SYNTAX

# =============================================================================

is_authenticated = True
is_admin = False

if is_authenticated and not is_admin:
print("Authenticated standard user")

# =============================================================================

# 48. MEMBERSHIP AND IDENTITY SYNTAX

# =============================================================================

languages = ["Python", "Java", "C++"]

print("Python" in languages)
print("Rust" not in languages)

first_list = [1, 2, 3]
second_list = first_list

print(first_list is second_list)
print(first_list == second_list)

# =============================================================================

# 49. IMPORT SYNTAX

# =============================================================================

import math

print(math.sqrt(25))

from math import factorial

print(factorial(5))

# Alias syntax:

import math as mathematics

print(mathematics.pi)

# =============================================================================

# 50. CLASS SYNTAX

# =============================================================================

class Student:
"""
Represent a student with a name and course.
"""

```
def __init__(self, name, course):
    self.name = name
    self.course = course

def display_information(self):
    print("Name:", self.name)
    print("Course:", self.course)
```

student = Student("Aman", "Python")

student.display_information()

# =============================================================================

# 51. EXCEPTION HANDLING SYNTAX

# =============================================================================

try:
value = int("100")
print(value)

except ValueError:
print("Conversion failed")

finally:
print("Execution of the exception-handling block completed.")

# =============================================================================

# 52. CONTEXT MANAGER SYNTAX

# =============================================================================

# The with statement creates a structured context.

sample_text = "Python syntax example."

with open("syntax_example.txt", "w", encoding="utf-8") as file:
file.write(sample_text)

# The file is managed automatically by the context manager.

# =============================================================================

# 53. LIST COMPREHENSION SYNTAX

# =============================================================================

squares = [number ** 2 for number in range(1, 6)]

print(squares)

even_squares = [
number ** 2
for number in range(1, 11)
if number % 2 == 0
]

print(even_squares)

# =============================================================================

# 54. CONDITIONAL EXPRESSIONS

# =============================================================================

age = 20

status = "Adult" if age >= 18 else "Minor"

print(status)

# =============================================================================

# 55. LAMBDA SYNTAX

# =============================================================================

square = lambda number: number ** 2

print(square(6))

# Lambda expressions are limited to a single expression.

# =============================================================================

# 56. TYPE ANNOTATION SYNTAX

# =============================================================================

student_name: str = "Aman"
student_score: int = 95

print(student_name)
print(student_score)

def multiply(first: int, second: int) -> int:
return first * second

print(multiply(5, 4))

# Type annotations communicate intended types but do not, by themselves,

# enforce runtime type checking in standard Python.

# =============================================================================

# 57. FUNCTION DEFAULT PARAMETERS

# =============================================================================

def introduce(name, role="Student"):
print(f"{name} is a {role}.")

introduce("Aman")
introduce("Rahul", "Developer")

# =============================================================================

# 58. KEYWORD ARGUMENT SYNTAX

# =============================================================================

def create_profile(name, age, city):
print(name, age, city)

create_profile(
name="Aman",
age=25,
city="Lucknow"
)

# =============================================================================

# 59. VARIABLE-LENGTH ARGUMENT SYNTAX

# =============================================================================

def calculate_sum(*numbers):
return sum(numbers)

print(calculate_sum(1, 2, 3, 4, 5))

def display_details(**details):
for key, value in details.items():
print(key, ":", value)

display_details(
name="Aman",
profession="Developer"
)

# =============================================================================

# 60. DECORATOR SYNTAX

# =============================================================================

def simple_decorator(function):
def wrapper():
print("Before function execution")
function()
print("After function execution")
return wrapper

@simple_decorator
def demonstrate_decorator():
print("Original function")

demonstrate_decorator()

# =============================================================================

# 61. ASYNC FUNCTION SYNTAX

# =============================================================================

# async and await are part of Python's syntax for asynchronous programming.

async def asynchronous_example():
return "Asynchronous function definition is syntactically valid."

# =============================================================================

# 62. MATCH-CASE SYNTAX

# =============================================================================

command = "start"

match command:
case "start":
print("Starting")
case "stop":
print("Stopping")
case _:
print("Unknown command")

# =============================================================================

# 63. THE IMPORTANCE OF READABLE SYNTAX

# =============================================================================

# Readable code reduces the probability of misunderstanding.

def calculate_average(values):
if not values:
return 0

```
return sum(values) / len(values)
```

marks = [80, 85, 90, 95]

print(calculate_average(marks))

# =============================================================================

# 64. COMMENT STYLE FOR COMPLEX LOGIC

# =============================================================================

def determine_discount(customer_type, purchase_amount):
# Premium customers receive a larger discount because their pricing
# category is based on membership status rather than purchase frequency.
if customer_type == "premium":
return purchase_amount * 0.20

```
# Standard customers receive a discount only after reaching the
# minimum purchase threshold.
if purchase_amount >= 10000:
    return purchase_amount * 0.10

return 0
```

print(determine_discount("premium", 5000))
print(determine_discount("standard", 12000))

# =============================================================================

# 65. COMMENT MAINTENANCE

# =============================================================================

# Comments must remain consistent with the code they describe.

minimum_age = 18

# A person must be at least 18 years old for this example.

if minimum_age >= 18:
print("Age requirement satisfied")

# An outdated comment can be more harmful than no comment because it can

# create an incorrect understanding of the program.

# =============================================================================

# 66. SHEBANG SYNTAX

# =============================================================================

# On Unix-like operating systems, Python scripts can begin with:

#

# #!/usr/bin/env python3

#

# This is called a shebang. It helps the operating system determine which

# interpreter should execute the file.

#

# It is written as a special comment and has significance primarily outside

# the normal Python language execution model.

# =============================================================================

# 67. ENCODING DECLARATIONS

# =============================================================================

# Python source files generally use UTF-8 encoding by default in modern Python.

#

# An explicit declaration can appear near the beginning of a source file:

#

# # -*- coding: utf-8 -*-

# =============================================================================

# 68. PYTHON SYNTAX AND CODE FORMATTERS

# =============================================================================

# Python syntax defines what is valid.

# Style conventions define what is readable and maintainable.

# Both examples below are syntactically valid:

total_one=10+20
total_two = 10 + 20

print(total_one)
print(total_two)

# Syntax determines whether code can be parsed.

# Style determines how clearly humans can understand the code.

# =============================================================================

# 69. PEP 8 AND COMMENT READABILITY

# =============================================================================

# Professional Python code generally follows established style conventions.

#

# Comments should:

# - Explain non-obvious decisions

# - Remain accurate

# - Use clear language

# - Be placed close to relevant code

# - Avoid repeating what obvious code already states

# =============================================================================

# 70. A COMBINED SYNTAX EXAMPLE

# =============================================================================

class CourseProgress:
"""
Track completed lessons for a course.
"""

```
def __init__(self, course_name: str):
    self.course_name = course_name
    self.completed_lessons = []

def complete_lesson(self, lesson_name: str) -> None:
    # Store the lesson name after completion.
    self.completed_lessons.append(lesson_name)

def display_progress(self) -> None:
    print(f"Course: {self.course_name}")

    if not self.completed_lessons:
        print("No lessons completed.")
        return

    print("Completed lessons:")

    for index, lesson in enumerate(self.completed_lessons, start=1):
        print(f"{index}. {lesson}")
```

progress = CourseProgress("Python Fundamentals")

progress.complete_lesson("Variables")
progress.complete_lesson("Python Syntax")
progress.complete_lesson("Comments")

progress.display_progress()

# =============================================================================

# 71. FINAL EXECUTION MESSAGE

# =============================================================================

print("Python syntax and comment demonstrations completed successfully.")

