# Python Syntax and Comments

## Introduction

Python syntax refers to the formal rules that govern how Python programs are written. Every Python program is composed according to a grammatical structure understood by the Python interpreter. The interpreter must be able to recognize statements, expressions, names, operators, delimiters, indentation, blocks, and other syntactic components before the program can execute.

Comments are explanatory elements written inside Python source code. Their primary purpose is to improve readability and communicate information to people reading or maintaining the program. Comments can explain decisions, assumptions, constraints, complex logic, temporary implementation details, or the purpose of particular sections of code.

Python is known for emphasizing readability. Its syntax deliberately avoids unnecessary punctuation in many situations and uses indentation as a structural part of the language.

---

# 1. Python Statements

A statement is an instruction written for Python to execute or interpret.

Examples include variable assignments, function calls, conditional statements, loops, imports, function definitions, and class definitions.

```python
name = "Python"
print(name)
```

The assignment:

```python
name = "Python"
```

stores a reference to a string object using the identifier `name`.

The statement:

```python
print(name)
```

calls the built-in `print()` function.

Python normally treats a newline as the end of a statement.

```python
first = 10
second = 20
```

Python also permits multiple simple statements on one line when separated by semicolons.

```python
first = 10; second = 20
```

This is syntactically valid, although separating statements onto individual lines generally improves readability.

---

# 2. Python Expressions

An expression is a syntactic construction that evaluates to a value.

Examples include arithmetic operations:

```python
10 + 20
```

comparisons:

```python
10 > 5
```

function calls:

```python
len("Python")
```

and combinations of variables and operators:

```python
price * quantity
```

Expressions can be used inside statements.

```python
total = 10 + 20
```

Here, `10 + 20` is an expression and the complete line is an assignment statement.

---

# 3. Indentation

Indentation is one of the most important characteristics of Python syntax.

Many programming languages use braces to define blocks of code.

```text
{
    block of code
}
```

Python instead uses indentation.

```python
if score >= 50:
    print("Pass")
```

The indented `print()` statement belongs to the `if` block.

Indentation is not merely a visual convention in Python. It is part of the language syntax. Incorrect indentation can prevent a program from executing.

```python
if score >= 50:
print("Pass")
```

This structure is invalid because Python expects the block after the `if` statement to be indented.

Python code should use consistent indentation. Four spaces per indentation level is the common convention.

---

# 4. Nested Indentation

Python blocks can contain other blocks.

```python
if number > 0:
    if number % 2 == 0:
        print("Positive even number")
```

The first `if` statement introduces one block.

The second `if` statement is inside that block and therefore receives an additional indentation level.

Each indentation level communicates the hierarchical structure of the program.

---

# 5. Colons in Python Syntax

A colon frequently appears at the end of a statement that introduces a block.

Examples include:

```python
if condition:
```

```python
for item in collection:
```

```python
while condition:
```

```python
def function_name():
```

```python
class ClassName:
```

```python
try:
```

The colon indicates that an indented suite of statements follows.

Colons also have other purposes in Python, including dictionary syntax, slicing operations, and type annotations.

---

# 6. Identifiers

Identifiers are names used to refer to Python objects.

Examples include variable names:

```python
student_name = "Aman"
```

function names:

```python
def calculate_total():
    pass
```

and class names:

```python
class Student:
    pass
```

Python identifiers generally follow these rules:

* They may contain letters.
* They may contain digits.
* They may contain underscores.
* They cannot begin with a digit.
* They cannot contain spaces.
* They cannot normally contain arbitrary special characters.
* They cannot use reserved Python keywords as names.

Valid examples:

```python
name
student_name
value2
_private_value
```

Invalid examples:

```python
2value
student name
total-marks
```

Python identifiers are case-sensitive.

```python
name = "Python"
Name = "Programming"
NAME = "Language"
```

These are three separate identifiers.

---

# 7. Python Keywords

Keywords are reserved words with predefined meaning in Python.

Examples include:

```text
if
else
elif
for
while
def
class
return
import
from
try
except
True
False
None
```

Keywords cannot generally be used as identifiers.

```python
if = 10
```

This is invalid because `if` is part of Python's language grammar.

Python provides the `keyword` module for inspecting the keywords available in the interpreter.

```python
import keyword

print(keyword.kwlist)
```

The exact list may depend on the Python version because language features can introduce new keywords.

---

# 8. Whitespace

Whitespace includes spaces, tabs, and line breaks.

Python uses whitespace structurally for indentation.

```python
if condition:
    print("Inside the block")
```

Spaces around operators are usually not required for syntactic validity.

Both expressions are valid:

```python
total=10+20
```

```python
total = 10 + 20
```

The second form is generally easier to read.

Whitespace therefore has two different roles in Python:

1. It can define program structure through indentation.
2. It can improve readability when used around operators and expressions.

---

# 9. Single-Line Comments

A Python comment begins with the hash symbol.

```python
# This is a comment.
```

The Python interpreter generally ignores the comment when executing the program.

Comments can appear before statements.

```python
# Store the user's name.
name = "Aman"
```

They can explain the purpose of code, assumptions, implementation decisions, or behavior that may not be obvious from the code itself.

---

# 10. Inline Comments

Comments can also appear after executable code.

```python
age = 25  # Age of the student
```

The part after the hash symbol is treated as a comment.

Inline comments should be concise. Excessive inline comments can make code difficult to scan.

A useful inline comment explains information not immediately visible from the statement.

---

# 11. Comments Inside Strings

The hash symbol does not begin a comment when it appears inside a string literal.

```python
message = "# This is part of the string."
```

Python treats the entire content between the quotation marks as string data.

The interpretation of the hash symbol therefore depends on its syntactic context.

---

# 12. Multi-Line Comments

Python does not provide a separate multi-line comment token comparable to comment delimiters used by some other programming languages.

Multiple comment lines can be written using the hash symbol.

```python
# First line of explanation.
# Second line of explanation.
# Third line of explanation.
```

Triple-quoted strings are also frequently used for multi-line explanatory text.

```python
"""
This text spans
multiple lines.
"""
```

Technically, this construct is a string literal rather than a dedicated comment.

Its behavior depends on where it appears and whether the resulting string is assigned or used by Python.

---

# 13. Docstrings

A docstring is a documentation string.

Docstrings are typically placed immediately inside a module, function, class, or method.

```python
def calculate_square(number):
    """
    Return the square of the supplied number.
    """
    return number * number
```

A function docstring can be accessed programmatically.

```python
print(calculate_square.__doc__)
```

Docstrings differ from ordinary comments because they can become part of the documented object's metadata.

They are commonly used by documentation systems, development environments, interactive help systems, and inspection tools.

---

# 14. Comments and Docstrings

Comments and docstrings serve related but distinct purposes.

Comments primarily communicate information to people reading the source code.

```python
# Apply the security policy before allowing access.
```

A docstring documents a Python object.

```python
def authenticate():
    """
    Authenticate a user.
    """
```

A comment is generally not accessible as part of a function's metadata.

A docstring can be accessed through attributes such as:

```python
function_name.__doc__
```

---

# 15. Why Comments Are Used

Comments are most valuable when they explain information that the code itself cannot easily communicate.

Useful comments may explain:

* Why a particular implementation was selected.
* Why a condition exists.
* A business rule.
* A security requirement.
* A performance limitation.
* A compatibility requirement.
* A non-obvious algorithmic decision.
* An assumption about external data.

Example:

```python
# Limit processing to 100 records to avoid excessive memory consumption.
records = records[:100]
```

The comment explains the reason behind the operation.

---

# 16. Unhelpful Comments

A comment that simply repeats obvious code may provide little value.

```python
number = 10  # Assign 10 to number
```

The code already clearly communicates the assignment.

A more useful comment provides context.

```python
maximum_attempts = 5  # Required by the account security policy.
```

The comment communicates information not directly visible from the variable assignment.

---

# 17. Comments Must Remain Accurate

Incorrect comments can be dangerous because developers may trust them while misunderstanding the actual code.

For example:

```python
# Minimum age is 21.
minimum_age = 18
```

The comment and code contradict each other.

Maintaining comments is therefore part of maintaining source code.

An accurate and concise comment is more valuable than a detailed but outdated explanation.

---

# 18. Assignment Syntax

Python assignment generally follows this structure:

```python
identifier = value
```

Example:

```python
name = "Python"
```

Python supports multiple assignment.

```python
first, second = 10, 20
```

Python also supports chained assignment.

```python
x = y = z = 100
```

The language supports unpacking assignments.

```python
a, b, c = [1, 2, 3]
```

The sequence on the right side is unpacked into the identifiers on the left side.

---

# 19. Augmented Assignment

Augmented assignment combines an operation with assignment.

```python
counter += 1
```

This is commonly used to update values.

Other examples include:

```python
counter -= 1
counter *= 2
counter /= 2
```

---

# 20. Conditional Syntax

Python conditional statements use `if`, `elif`, and `else`.

```python
if score >= 90:
    print("A")
elif score >= 75:
    print("B")
else:
    print("C")
```

Every block is defined by indentation.

The conditional headers end with colons.

---

# 21. Loop Syntax

A `for` loop iterates over an iterable.

```python
for number in range(5):
    print(number)
```

A `while` loop continues while its condition evaluates to `True`.

```python
counter = 0

while counter < 5:
    print(counter)
    counter += 1
```

Both constructs use colons and indentation.

---

# 22. The `pass` Statement

Python blocks cannot normally be left syntactically empty.

The `pass` statement can act as a placeholder.

```python
def future_feature():
    pass
```

The function is syntactically complete even though it currently performs no operation.

`pass` can also be used in classes, conditional blocks, and loops.

---

# 23. Line Continuation

Python normally ends a statement when a physical line ends.

Long expressions can continue across multiple lines.

The preferred approach is usually implicit continuation within parentheses, brackets, or braces.

```python
total = (
    10
    + 20
    + 30
)
```

Lists also naturally support multi-line formatting.

```python
numbers = [
    10,
    20,
    30,
]
```

Python also supports explicit continuation using a backslash.

```python
total = 10 + 20 + \
        30 + 40
```

Parentheses are generally easier to maintain because backslashes can be affected by trailing whitespace or formatting mistakes.

---

# 24. Parentheses, Brackets, and Braces

Python uses different delimiters for different syntactic structures.

Parentheses are commonly used for grouping, function calls, and tuples.

```python
result = (10 + 5) * 2
```

```python
coordinates = (10, 20)
```

Square brackets are used for lists and indexing.

```python
languages = ["Python", "Java"]
```

```python
languages[0]
```

Curly braces are used for dictionaries and sets.

```python
student = {
    "name": "Aman",
    "age": 21,
}
```

```python
numbers = {1, 2, 3}
```

---

# 25. Commas

Commas separate elements in many Python structures.

```python
numbers = [1, 2, 3]
```

They also separate function arguments.

```python
print("Python", "Syntax", "Comments")
```

Commas are also essential in tuple syntax.

```python
coordinates = (10, 20)
```

A single-element tuple requires a comma.

```python
value = ("Python",)
```

Without the comma, the expression is simply a parenthesized string.

---

# 26. Trailing Commas

Python allows trailing commas in many collections and argument lists.

```python
languages = [
    "Python",
    "Java",
    "C++",
]
```

Trailing commas can make multi-line structures easier to modify and can produce cleaner differences when source code is tracked with version control systems.

---

# 27. String Syntax

Python supports both single-quoted and double-quoted strings.

```python
language = 'Python'
```

```python
language = "Python"
```

Triple quotes are used for multi-line strings.

```python
text = """
Python supports
multi-line strings.
"""
```

The choice between single and double quotation marks is usually based on consistency and the content of the string.

---

# 28. Escape Sequences

Escape sequences represent special characters inside strings.

Examples include:

```python
"\n"
```

for a new line,

```python
"\t"
```

for a tab,

and:

```python
"\\"
```

for a backslash.

Quotation marks can also be escaped.

```python
message = "Python is a \"high-level\" language."
```

---

# 29. Raw Strings

Raw strings are commonly created using the `r` prefix.

```python
path = r"C:\Users\Student\Documents"
```

Raw strings are useful when working with text containing many backslashes, such as file paths and some regular expressions.

---

# 30. Function Syntax

A Python function is defined using the `def` keyword.

```python
def greet(name):
    print("Hello", name)
```

The function header contains:

* The `def` keyword.
* The function name.
* Parentheses containing parameters.
* A colon.

The function body is indented.

A function can return a value.

```python
def add(first, second):
    return first + second
```

---

# 31. Default Parameters

Functions can define default values for parameters.

```python
def introduce(name, role="Student"):
    print(name, role)
```

The function can be called without explicitly providing the optional argument.

```python
introduce("Aman")
```

It can also be overridden.

```python
introduce("Aman", "Developer")
```

---

# 32. Keyword Arguments

Arguments can be supplied using parameter names.

```python
create_profile(
    name="Aman",
    age=25,
    city="Lucknow"
)
```

Keyword arguments can improve readability, particularly when functions have multiple parameters.

---

# 33. Variable-Length Arguments

The `*` syntax collects positional arguments.

```python
def calculate_sum(*numbers):
    return sum(numbers)
```

The `**` syntax collects keyword arguments.

```python
def display_details(**details):
    print(details)
```

These constructs are part of Python's flexible function call syntax.

---

# 34. Class Syntax

Classes are defined using the `class` keyword.

```python
class Student:
    pass
```

Classes can contain methods and attributes.

```python
class Student:

    def __init__(self, name):
        self.name = name
```

The constructor method is named `__init__`.

The `self` parameter refers to the instance being operated on.

---

# 35. Import Syntax

Python modules can be imported using the `import` statement.

```python
import math
```

Specific names can be imported.

```python
from math import sqrt
```

Modules can be assigned aliases.

```python
import math as mathematics
```

Import syntax makes functionality defined in other modules available to the current program.

---

# 36. Exception Handling Syntax

Python uses structured syntax for handling exceptions.

```python
try:
    value = int("100")
except ValueError:
    print("Invalid value")
finally:
    print("Finished")
```

The `try` block contains code that may raise an exception.

The `except` block handles specific exceptions.

The `finally` block executes as part of the cleanup and completion process.

---

# 37. Context Manager Syntax

The `with` statement manages a context.

A common example involves files.

```python
with open("example.txt", "w") as file:
    file.write("Python")
```

The indented block executes within the context.

Context managers are commonly used for resources that require structured setup and cleanup.

---

# 38. List Comprehension Syntax

List comprehensions provide a compact syntax for constructing lists.

```python
squares = [number ** 2 for number in range(1, 6)]
```

A conditional expression can be included.

```python
even_squares = [
    number ** 2
    for number in range(1, 11)
    if number % 2 == 0
]
```

Comprehensions are expressions and therefore produce values.

---

# 39. Conditional Expressions

Python provides a compact conditional expression.

```python
status = "Adult" if age >= 18 else "Minor"
```

The syntax differs from the multi-line `if` statement.

It is most appropriate when the conditional logic is simple and easily readable.

---

# 40. Lambda Expressions

Lambda expressions create anonymous functions.

```python
square = lambda number: number ** 2
```

The expression after the colon is evaluated and returned.

Lambda syntax is restricted to a single expression.

---

# 41. Type Annotation Syntax

Python supports optional type annotations.

```python
name: str = "Aman"
score: int = 95
```

Functions can annotate parameters and return values.

```python
def multiply(first: int, second: int) -> int:
    return first * second
```

Type annotations communicate intended types and can be used by static analysis tools, editors, documentation systems, and type checkers.

Standard Python execution does not automatically enforce every annotation at runtime.

---

# 42. Decorator Syntax

The `@` symbol is used with decorators.

```python
@decorator_name
def function_name():
    pass
```

A decorator modifies or wraps the behavior associated with another callable.

Decorator syntax provides a concise representation of function transformation.

---

# 43. Asynchronous Syntax

Python supports asynchronous programming using `async` and `await`.

```python
async def fetch_data():
    return "Data"
```

Asynchronous functions use a distinct syntax because they participate in Python's asynchronous execution model.

---

# 44. Match-Case Syntax

Modern Python versions support structural pattern matching.

```python
match command:
    case "start":
        print("Starting")
    case "stop":
        print("Stopping")
    case _:
        print("Unknown command")
```

The `match` statement uses indentation and colons in the same structured manner as other Python block statements.

---

# 45. Syntax Errors

A syntax error occurs when Python source code violates the language grammar.

Examples include a missing colon:

```python
if True
    print("Invalid")
```

incorrect indentation:

```python
if True:
print("Invalid")
```

and incomplete string literals:

```python
message = "Python
```

Syntax errors usually prevent Python from successfully parsing the program.

---

# 46. Syntax Errors and Runtime Errors

A program can be syntactically correct but still fail while executing.

```python
result = 10 / 0
```

This expression is syntactically valid.

The failure occurs during execution because division by zero is not permitted.

This distinction is important:

* Syntax errors occur when Python cannot correctly parse the source code.
* Runtime errors occur while syntactically valid code is being executed.

---

# 47. Python Syntax and Dynamic Typing

Python is dynamically typed.

A variable can refer to objects of different types at different times.

```python
value = 100
```

Later:

```python
value = "Python"
```

The assignment syntax remains the same.

The object associated with the identifier changes.

---

# 48. Code Structure and Readability

Python's syntax is designed to make program structure visible.

Indentation shows block relationships.

Function definitions separate reusable behavior.

Classes organize related state and behavior.

Comments provide contextual information.

Docstrings provide structured documentation.

Readable code combines correct syntax with clear naming, logical structure, and appropriate documentation.

---

# 49. Syntax and Style

Syntax determines whether Python code is grammatically valid.

Style determines how clearly that valid code is presented.

For example:

```python
total=10+20
```

and:

```python
total = 10 + 20
```

are both syntactically valid.

The second version follows a clearer formatting convention.

Python development commonly follows established style practices to make source code easier to read and maintain.

---

# 50. Professional Commenting Practices

Professional comments generally focus on information that cannot be communicated effectively through code alone.

Useful comments often explain:

* Reasoning.
* Constraints.
* Intent.
* Business requirements.
* Security decisions.
* Compatibility requirements.
* Performance considerations.

Comments should be concise, accurate, and maintained alongside the code.

A well-structured Python program often requires fewer comments because meaningful identifiers, small functions, clear structure, and appropriate abstractions already communicate much of the program's purpose.

---

# 51. Special Comment Forms

Some comments have significance outside ordinary program explanation.

A shebang can appear at the beginning of a Python file on Unix-like systems.

```python
#!/usr/bin/env python3
```

It can help the operating system determine which interpreter should execute the script.

An encoding declaration can also appear near the beginning of a source file.

```python
# -*- coding: utf-8 -*-
```

Modern Python source files generally use UTF-8 by default, but explicit declarations may still appear in source code for compatibility or clarity.

---

# 52. Relationship Between Syntax and Comments

Syntax determines how Python code is structured and interpreted.

Comments provide human-readable context around that structure.

Python syntax controls:

* Statements.
* Expressions.
* Indentation.
* Blocks.
* Identifiers.
* Keywords.
* Functions.
* Classes.
* Conditions.
* Loops.
* Imports.
* Exceptions.
* Delimiters.
* Operators.
* Type annotations.
* Modern language constructs.

Comments support maintainability by documenting the reasoning and context associated with these constructs.

Correct syntax allows Python to interpret a program.

Clear comments and documentation allow people to understand the purpose and decisions behind the program.

