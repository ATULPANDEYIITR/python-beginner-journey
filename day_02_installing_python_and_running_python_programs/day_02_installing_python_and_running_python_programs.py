# ============================================================

# INSTALLING PYTHON AND RUNNING PYTHON PROGRAMS

# A Detailed Practical Guide from Basic Concepts to Advanced Usage

# ============================================================

"""
Python is a high-level, general-purpose programming language.

Before writing useful Python programs, it is important to understand
three separate things:

1. Installing Python
2. Understanding how Python executes code
3. Creating and running Python programs

A Python installation provides an interpreter that reads Python code
and executes it.

Python source code is normally stored in files with the extension:

.py

For example:

hello.py
calculator.py
data_analysis.py

When a Python program is executed, the Python interpreter processes
the instructions written in the file.
"""

# ============================================================

# PART 1: WHAT IS PYTHON?

# ============================================================

"""
Python is both the name of a programming language and the software
environment used to execute programs written in that language.

Consider the following instruction:

print("Hello, World!")

The computer's processor does not directly understand this instruction
in its original form.

The Python interpreter acts as the software responsible for processing
the Python instruction and coordinating its execution.

A simplified execution process is:

Python Source Code
|
v
Python Interpreter
|
v
Python Bytecode
|
v
Python Virtual Machine
|
v
Program Output

This internal process is simplified here because different Python
implementations can have different internal architectures.
"""

# ============================================================

# PART 2: PYTHON INTERPRETER

# ============================================================

"""
The Python interpreter is the program responsible for executing Python
code.

When Python is installed, commands become available in the terminal.

Depending on the operating system and installation method, common
commands include:

python
python3
py

For example:

python program.py

or:

python3 program.py

On many Windows installations, the Python Launcher can be used:

py program.py

The exact command depends on the operating system and the way Python
was installed.
"""

# ============================================================

# PART 3: CHECKING WHETHER PYTHON IS INSTALLED

# ============================================================

"""
After installation, Python should be verified from a terminal.

Common commands are:

Windows:

python --version

or:

py --version

macOS and Linux:

python3 --version

Sometimes:

python --version

The expected output contains the installed Python version.

For example:

Python 3.x.x

The exact version number will depend on the installed release.

Version checking is important because multiple versions of Python may
exist on the same computer.
"""

# Example of displaying the Python version from inside Python.

import sys

print("Python executable:", sys.executable)
print("Python version:", sys.version)
print()

# ============================================================

# PART 4: PYTHON 3 AND VERSION MANAGEMENT

# ============================================================

"""
Modern Python development generally uses Python 3.

Python versions normally follow a structure similar to:

Major.Minor.Micro

For example:

3.12.5

In this example:

3  = major version
12 = minor version
5  = micro or maintenance version

The Python version matters because:

* Language features can change.
* Standard library features can change.
* Third-party packages can have version requirements.
* Older programs may depend on older Python behavior.

A system may contain multiple Python installations.

For example:

Python 3.10
Python 3.11
Python 3.12
Python 3.13

Different projects may intentionally use different versions.
"""

# ============================================================

# PART 5: INSTALLING PYTHON ON WINDOWS

# ============================================================

"""
A typical Python installation process on Windows involves:

1. Obtaining an official Python installer.
2. Running the installer.
3. Selecting appropriate installation options.
4. Completing installation.
5. Verifying the installation in PowerShell or Command Prompt.

One particularly important installation concept is PATH.

PATH is an environment variable used by an operating system to locate
executable programs.

When the Python installation directory is available through PATH,
a terminal can locate Python when the user types:

python

Without a correct PATH configuration, the terminal may display an error
indicating that Python cannot be found.

The Python Launcher command:

py

can also provide a way to locate and run installed Python versions on
Windows.

Examples:

py --version

py -3.12

py program.py
"""

# ============================================================

# PART 6: INSTALLING PYTHON ON macOS

# ============================================================

"""
macOS systems may contain Python-related software already, but system
Python should not automatically be treated as the development version
for personal projects.

A separate modern Python installation may be required.

After installation, Python is commonly executed using:

python3

Example:

python3 --version

A program can commonly be executed using:

python3 program.py

The exact installation method and command availability can depend on
the Python distribution and installation method.
"""

# ============================================================

# PART 7: INSTALLING PYTHON ON LINUX

# ============================================================

"""
Many Linux distributions already use Python for system-level tools.

Because Python can be connected to operating system functionality,
care should be taken before modifying or replacing the system Python.

Linux distributions usually provide package-management tools for
installing Python.

The exact command depends on the Linux distribution.

After installation, verification commonly involves:

python3 --version

Programs are commonly executed using:

python3 program.py

The distinction between system Python and project-specific Python
becomes increasingly important in professional development.
"""

# ============================================================

# PART 8: UNDERSTANDING THE TERMINAL

# ============================================================

"""
A terminal provides a text-based interface for interacting with the
operating system.

Different operating systems provide different terminal environments.

Windows examples include:

* Command Prompt
* PowerShell
* Windows Terminal

Linux examples include:

* Bash
* Zsh
* Fish
* Terminal emulators

macOS commonly provides terminal environments such as:

* Zsh
* Bash

A terminal command usually follows this conceptual structure:

command arguments

For example:

python hello.py

Here:

python   = command
hello.py = argument representing the Python file

Another example:

python --version

Here:

python    = command
--version = command option
"""

# ============================================================

# PART 9: NAVIGATING DIRECTORIES

# ============================================================

"""
Python programs are stored inside directories.

A directory is another name for a folder.

Suppose a project exists at:

C:\Users\Student\Documents\PythonProjects

A terminal must often be moved into that directory before executing a
program.

The command used to change directories is commonly:

cd

For example:

cd Documents

To move upward one directory:

cd ..

To display the current directory:

Windows PowerShell:

pwd

Linux/macOS:

pwd

To list files, commands differ depending on the terminal environment.

Windows:

dir

Linux/macOS:

ls

Understanding directory navigation is essential because a Python
program cannot be executed by filename alone unless the terminal can
locate the file.
"""

# ============================================================

# PART 10: CREATING A PYTHON FILE

# ============================================================

"""
Python programs are usually stored in text files ending with:

.py

Example filename:

hello.py

The file can be created using:

* Visual Studio Code
* IDLE
* PyCharm
* Sublime Text
* Notepad or another text editor
* Terminal-based editors

The .py extension identifies the file as Python source code.

A simple Python file may contain:

print("Hello, World!")

When saved as:

hello.py

it can be executed by the Python interpreter.
"""

# ============================================================

# PART 11: FIRST PYTHON PROGRAM

# ============================================================

print("Hello, World!")

"""
The print() function displays information.

The structure:

print(...)

means that the print function is being called.

The text:

"Hello, World!"

is called a string.

A string is a sequence of characters.

Python supports both single and double quotes for ordinary strings.
"""

print('This is also a string.')
print("This is another string.")
print()

# ============================================================

# PART 12: RUNNING A PYTHON PROGRAM

# ============================================================

"""
Assume a file named:

hello.py

exists in the current directory.

The program can be executed using a command such as:

python hello.py

or:

python3 hello.py

or on many Windows systems:

py hello.py

The execution process can be represented as:

Terminal
|
v
Python Command
|
v
Python Interpreter
|
v
Reads hello.py
|
v
Executes instructions
|
v
Displays output
"""

# ============================================================

# PART 13: CURRENT WORKING DIRECTORY

# ============================================================

"""
Every running process has a current working directory.

When Python is executed from a terminal, the current directory affects:

* Relative file paths
* File reading
* File writing
* Module imports in certain situations

Python can display the current working directory using the os module.
"""

import os

current_directory = os.getcwd()

print("Current working directory:")
print(current_directory)
print()

# ============================================================

# PART 14: RUNNING PYTHON IN INTERACTIVE MODE

# ============================================================

"""
Python can run in interactive mode.

Interactive mode is started by entering a Python command without
specifying a Python file.

For example:

python

or:

python3

or:

py

Python then displays an interactive prompt, commonly represented by:

> > >

Instructions can be entered directly:

> > > print("Hello")
> > > Hello

> > > 10 + 20
> > > 30

Interactive mode is useful for:

* Testing small expressions
* Learning syntax
* Experimenting
* Inspecting objects
* Quickly checking behavior

A Python file is generally more suitable when code needs to be saved,
organized, reused, or developed into a larger program.
"""

# ============================================================

# PART 15: PYTHON EXPRESSIONS AND STATEMENTS

# ============================================================

"""
Python code consists of different types of instructions.

An expression produces a value.

Examples:

10 + 20

5 * 8

"Python" + " Programming"

A statement performs an action.

Examples:

x = 10

print(x)

if x > 5:
print("Greater than five")

The difference becomes especially visible in interactive mode.

An expression can display its resulting value automatically.

A script generally requires print() when the result needs to be
explicitly displayed.
"""

number_a = 10
number_b = 20

result = number_a + number_b

print("Result:", result)
print()

# ============================================================

# PART 16: PYTHON SOURCE CODE EXECUTION ORDER

# ============================================================

"""
Python generally executes a script from top to bottom.

Consider:

print("First")
print("Second")
print("Third")

The output will be:

First
Second
Third

Execution order can change because of:

* Conditional statements
* Loops
* Function calls
* Exceptions
* Program termination
  """

print("First instruction executed.")
print("Second instruction executed.")
print("Third instruction executed.")
print()

# ============================================================

# PART 17: COMMENTS

# ============================================================

"""
Comments are notes written inside source code.

A single-line Python comment begins with:

#

Example:

# Calculate the total price

Comments are normally ignored during program execution.

They are useful for:

* Explaining complex logic
* Documenting decisions
* Organizing source code
* Providing context

Good comments explain reasoning when the code itself does not make the
reason obvious.
"""

# This variable stores the number of students.

student_count = 25

print("Student count:", student_count)
print()

# ============================================================

# PART 18: MULTI-LINE TEXT AND DOCSTRINGS

# ============================================================

"""
Triple-quoted strings can span multiple lines.

They can be written using:

'''

or:

"""

They are frequently used as documentation strings, also called
docstrings.

A docstring can describe:

* A module
* A function
* A class
* A method

Example:

def calculate_total():
"""Calculate and return the total value."""
"""

def example_function():
"""
This is a function-level documentation string.

```
It describes the purpose of the function.
"""
return "Function executed successfully."
```

print(example_function())
print()

# ============================================================

# PART 19: VARIABLES

# ============================================================

"""
A variable is a name associated with an object.

Example:

age = 25

The name:

age

refers to the value:

25

Python is dynamically typed, meaning that a variable name does not need
a separately declared fixed type before assignment.

Example:

value = 10
value = "Python"

The name value can later refer to an object of a different type.

This does not mean that Python has no types.

Python objects have types, and operations depend on those types.
"""

name = "Python Learner"
age = 25
height = 178.5
is_learning = True

print(name)
print(age)
print(height)
print(is_learning)
print()

# ============================================================

# PART 20: CHECKING OBJECT TYPES

# ============================================================

"""
The type() function can be used to inspect an object's type.
"""

print(type(name))
print(type(age))
print(type(height))
print(type(is_learning))
print()

# ============================================================

# PART 21: BASIC DATA TYPES

# ============================================================

"""
Common built-in Python data types include:

int
Whole numbers.

float
Decimal or floating-point numbers.

str
Text.

bool
True or False values.

list
Ordered mutable collections.

tuple
Ordered immutable collections.

set
Collections of unique elements.

dict
Collections of key-value pairs.

NoneType
The type associated with None.
"""

integer_value = 100
floating_value = 99.95
text_value = "Python"
boolean_value = True
empty_value = None

print(integer_value)
print(floating_value)
print(text_value)
print(boolean_value)
print(empty_value)
print()

# ============================================================

# PART 22: USER INPUT

# ============================================================

"""
The input() function allows a program to receive text input.

Example:

name = input("Enter your name: ")

Important:

input() returns a string.

Even if the user enters:

25

Python receives:

"25"

Conversion is required when numerical input is needed.

Example:

age = int(input("Enter your age: "))
"""

# The following lines are commented out so that this learning script

# can run without requiring user interaction.

# user_name = input("Enter your name: ")

# print("Hello,", user_name)

# ============================================================

# PART 23: TYPE CONVERSION

# ============================================================

"""
Common conversion functions include:

int()
float()
str()
bool()

Examples:
"""

text_number = "100"
converted_number = int(text_number)

decimal_text = "45.5"
converted_decimal = float(decimal_text)

number = 250
converted_text = str(number)

print(converted_number)
print(converted_decimal)
print(converted_text)
print()

# ============================================================

# PART 24: OPERATORS

# ============================================================

"""
Python provides operators for performing operations.

Arithmetic operators:

*

-

*

/
//
%
**

Comparison operators:

==
!=

>

<

> =
> <=

Logical operators:

and
or
not

Assignment operators:

=
+=
-=
*=
/=
"""

a = 17
b = 5

print("Addition:", a + b)
print("Subtraction:", a - b)
print("Multiplication:", a * b)
print("Division:", a / b)
print("Floor division:", a // b)
print("Remainder:", a % b)
print("Exponentiation:", a ** b)
print()

# ============================================================

# PART 25: CONDITIONAL EXECUTION

# ============================================================

"""
Conditional statements allow a program to make decisions.

Python uses:

if
elif
else

Indentation is part of Python syntax.
"""

marks = 78

if marks >= 90:
print("Grade A")
elif marks >= 75:
print("Grade B")
elif marks >= 50:
print("Grade C")
else:
print("Grade D")

print()

# ============================================================

# PART 26: INDENTATION

# ============================================================

"""
Indentation is structurally important in Python.

Example:

if condition:
print("Inside the condition")

The indented code belongs to the if block.

Incorrect indentation can produce:

IndentationError

Professional Python code generally follows consistent indentation
conventions.

Four spaces are widely used for one indentation level.

Mixing tabs and spaces can cause problems and should be avoided.
"""

# ============================================================

# PART 27: LOOPS

# ============================================================

"""
Loops repeat code.

Python primarily provides:

for
while
"""

for number in range(1, 6):
print("For loop value:", number)

print()

counter = 1

while counter <= 3:
print("While loop value:", counter)
counter += 1

print()

# ============================================================

# PART 28: FUNCTIONS

# ============================================================

"""
Functions organize reusable logic.

A function is defined using:

def
"""

def greet(person_name):
"""Display a greeting for the supplied name."""
print("Hello,", person_name)

greet("Student")
print()

# ============================================================

# PART 29: RETURN VALUES

# ============================================================

"""
Functions can return values using:

return

Returning a value is different from printing a value.
"""

def add_numbers(first_number, second_number):
return first_number + second_number

sum_result = add_numbers(10, 15)

print("Returned result:", sum_result)
print()

# ============================================================

# PART 30: ERRORS WHILE RUNNING PYTHON PROGRAMS

# ============================================================

"""
Errors are an important part of programming.

Python commonly displays a traceback when an exception occurs.

A traceback provides information about:

* The location of the error
* The file involved
* The line involved
* The type of error

Common errors include:

SyntaxError
IndentationError
NameError
TypeError
ValueError
ZeroDivisionError
FileNotFoundError
ModuleNotFoundError
"""

# Example:

try:
division_result = 10 / 0
except ZeroDivisionError as error:
print("An error occurred:", error)

print()

# ============================================================

# PART 31: SYNTAX ERRORS

# ============================================================

"""
A syntax error occurs when Python code violates language syntax.

Example of invalid syntax:

if True
print("Hello")

The colon is missing.

Correct version:

if True:
print("Hello")

Syntax errors generally prevent the program from beginning normal
execution.
"""

# ============================================================

# PART 32: RUNTIME ERRORS

# ============================================================

"""
A runtime error occurs while the program is executing.

Example:

number = 10
result = number / 0

The program syntax is valid.

The problem occurs during execution because division by zero is not
permitted.
"""

# ============================================================

# PART 33: LOGICAL ERRORS

# ============================================================

"""
Logical errors occur when a program runs but produces an incorrect
result.

Example:

Expected calculation:

total = price * quantity

Incorrect calculation:

total = price + quantity

Python may execute the code without reporting an error, but the result
does not represent the intended logic.

Logical errors require testing and careful reasoning.
"""

price = 100
quantity = 3

correct_total = price * quantity

print("Correct total:", correct_total)
print()

# ============================================================

# PART 34: RUNNING PROGRAMS FROM AN IDE

# ============================================================

"""
An Integrated Development Environment, or IDE, can provide features
such as:

* Code editing
* Syntax highlighting
* Automatic formatting
* Debugging
* Project management
* Integrated terminals
* Code completion

When using an IDE, a Run button may appear to execute Python programs.

Internally, the IDE still needs to identify:

* Which Python interpreter to use
* Which Python file to execute
* Which working directory to use
* Which command-line arguments to provide

Understanding terminal execution makes IDE execution easier to debug.
"""

# ============================================================

# PART 35: RUNNING PYTHON IN VISUAL STUDIO CODE

# ============================================================

"""
A typical workflow in Visual Studio Code is:

1. Open a folder.
2. Create or open a .py file.
3. Install or select a Python interpreter.
4. Write Python code.
5. Save the file.
6. Run the program.

A common issue occurs when the editor has selected a different Python
interpreter than the one expected by the project.

This can lead to problems such as:

ModuleNotFoundError

even when a package appears to be installed.

The reason may be that the package was installed into one Python
environment while the program is being executed using another.
"""

# ============================================================

# PART 36: FILE PATHS

# ============================================================

"""
Programs often work with files.

A file path identifies the location of a file.

Examples of absolute paths:

Windows:

C:\Users\Student\Documents\data.txt

Linux/macOS:

/home/student/documents/data.txt

Relative paths are interpreted from the current working directory.

Example:

data.txt

or:

data/data.txt

Using pathlib is a modern and convenient approach for working with
paths.
"""

from pathlib import Path

current_path = Path.cwd()

print("Path object representing the current directory:")
print(current_path)
print()

# ============================================================

# PART 37: READING A PYTHON PROGRAM AS A FILE

# ============================================================

"""
A Python source file is fundamentally a text file.

For example, a file named:

program.py

may contain:

print("Hello")

Python reads the source code and processes it according to Python
language rules.

Source files should normally be saved with a text encoding that Python
can interpret correctly.

UTF-8 is widely used.
"""

# ============================================================

# PART 38: PYTHON BYTECODE

# ============================================================

"""
Python source code is not normally executed directly by the processor.

CPython, the most widely used Python implementation, compiles Python
source code into an intermediate representation called bytecode.

Bytecode may be cached in directories such as:

**pycache**

Cached files often use extensions such as:

.pyc

These files are implementation details and should not be confused with
the original Python source code.

The Python source file remains the primary editable program.
"""

# ============================================================

# PART 39: PYTHON IMPLEMENTATIONS

# ============================================================

"""
The word Python can refer to the language specification, while multiple
implementations can execute Python code.

Examples include:

CPython
PyPy
Jython
IronPython

CPython is the reference implementation most commonly used in general
Python development.

Different implementations can differ in:

* Performance
* Memory behavior
* Compatibility
* Runtime architecture
* Integration with other environments
  """

# ============================================================

# PART 40: PYTHON STANDARD LIBRARY

# ============================================================

"""
Python includes a large collection of modules known as the standard
library.

These modules are generally available with a standard Python
installation.

Examples include:

os
sys
math
json
datetime
pathlib
statistics

A module can be imported using:

import module_name
"""

import math

value = 16

print("Square root:", math.sqrt(value))
print()

# ============================================================

# PART 41: THIRD-PARTY PACKAGES

# ============================================================

"""
Python can be extended using packages developed by other organizations
and developers.

Examples include packages for:

* Data analysis
* Web development
* Machine learning
* Automation
* Testing

The Python package installer is commonly accessed using:

pip

A package can commonly be installed with:

python -m pip install package_name

Using:

python -m pip

is often useful because it explicitly connects pip execution with a
particular Python interpreter.

This can reduce confusion when multiple Python installations exist.
"""

# ============================================================

# PART 42: WHY 'python -m pip' IS IMPORTANT

# ============================================================

"""
Consider a system containing:

Python 3.11
Python 3.12

If the command:

pip install package_name

uses the pip associated with Python 3.11, but the program is executed
using Python 3.12, Python 3.12 may not find the installed package.

A more explicit command is conceptually:

python -m pip install package_name

The Python interpreter executes its associated pip module.

This helps ensure that the package is installed in the intended Python
environment.
"""

# ============================================================

# PART 43: VIRTUAL ENVIRONMENTS

# ============================================================

"""
A virtual environment is an isolated Python environment for a project.

Suppose Project A requires:

package_x version 1

Project B requires:

package_x version 2

A virtual environment allows each project to maintain its own package
environment.

A common creation command is:

python -m venv .venv

The directory:

.venv

contains an environment associated with that project.

Activation commands depend on the operating system and terminal.

Virtual environments reduce conflicts between project dependencies.
"""

# ============================================================

# PART 44: PYTHON INTERPRETER SELECTION

# ============================================================

"""
A Python project is executed by a specific interpreter.

It is important to distinguish:

Python language
Python source file
Python interpreter
Python environment
Installed packages

Consider the command:

python program.py

The command must resolve:

1. Which executable does 'python' refer to?
2. Which environment belongs to that executable?
3. Which program file is being executed?
4. What is the current working directory?

Many Python environment problems result from confusion between these
different components.
"""

print("This script is currently being executed by:")
print(sys.executable)
print()

# ============================================================

# PART 45: COMMAND-LINE ARGUMENTS

# ============================================================

"""
Python programs can receive command-line arguments.

Example command:

python program.py input.txt

The argument:

input.txt

can be accessed using sys.argv.

sys.argv is a list containing command-line information.
"""

print("Command-line arguments:")
print(sys.argv)
print()

# ============================================================

# PART 46: PROGRAM ENTRY POINTS

# ============================================================

"""
Python files can be executed directly or imported as modules.

The special variable:

**name**

helps distinguish these situations.

When a file is executed directly:

**name** == "**main**"

This pattern is commonly used:
"""

def main():
print("The main program is running.")

if **name** == "**main**":
main()

print()

# ============================================================

# PART 47: WHY THE **main** PATTERN MATTERS

# ============================================================

"""
A Python file can contain reusable functions and executable program
logic.

Consider:

def calculate():
return 10

if **name** == "**main**":
print(calculate())

When the file is imported by another Python program, the calculate()
function becomes available.

The code inside:

if **name** == "**main**":

does not automatically execute during a normal import.

This supports code organization and reuse.
"""

# ============================================================

# PART 48: IMPORTING MODULES

# ============================================================

"""
Python files can act as modules.

Suppose a file named:

utilities.py

contains:

def add(a, b):
return a + b

Another Python file can use:

import utilities

and then:

utilities.add(10, 20)

Python searches for modules using import-related paths and environment
configuration.

Incorrect module locations can produce:

ModuleNotFoundError
"""

# ============================================================

# PART 49: PYTHON MODULE SEARCH PATH

# ============================================================

"""
Python maintains information about locations used when searching for
modules.

This information can be inspected using:

sys.path

The search path can include:

* The script location
* Environment-specific locations
* Installed package directories
* Additional configured paths
  """

print("A portion of Python's module search path:")

for path_entry in sys.path[:5]:
print(path_entry)

print()

# ============================================================

# PART 50: ENVIRONMENT VARIABLES

# ============================================================

"""
Environment variables provide configuration information to processes.

Examples include:

PATH

PYTHONPATH

PATH helps the operating system locate executable programs.

PYTHONPATH can influence Python's module search locations.

Environment configuration should be handled carefully because incorrect
configuration can create confusing interpreter and import behavior.
"""

# ============================================================

# PART 51: RUNNING A MODULE

# ============================================================

"""
Python can execute a module using:

python -m module_name

Examples include:

python -m pip

python -m venv

The -m option tells Python to locate and execute a module.

This can be preferable to directly calling a separate executable when
multiple Python environments are present.
"""

# ============================================================

# PART 52: THE SHEBANG LINE

# ============================================================

"""
On Unix-like systems, executable Python scripts may begin with a
shebang line such as:

#!/usr/bin/env python3

This helps the operating system determine which interpreter should be
used when executing the script directly.

A script may also require executable permission.

The exact behavior depends on the operating system and environment.
"""

# ============================================================

# PART 53: EXIT CODES

# ============================================================

"""
Programs generally return an exit status to the operating system.

Conventionally:

0

often indicates successful completion.

A non-zero value generally indicates an error or special condition.

Python can explicitly terminate with an exit code.
"""

def demonstrate_exit_code_concept():
"""
This function demonstrates the concept without actually terminating
this educational script.
"""
status_code = 0
return status_code

print("Example success status code:", demonstrate_exit_code_concept())
print()

# ============================================================

# PART 54: DEBUGGING PYTHON PROGRAMS

# ============================================================

"""
Debugging is the process of identifying and correcting problems in
programs.

Basic debugging techniques include:

* Reading error messages carefully
* Inspecting traceback information
* Using print() temporarily
* Checking variable values
* Using an IDE debugger
* Using breakpoints
* Testing smaller sections of code

Python also provides the pdb debugging module.

Debuggers allow program execution to be paused so that variables and
execution flow can be inspected.
"""

# ============================================================

# PART 55: SIMPLE DEBUGGING WITH PRINT

# ============================================================

numbers = [10, 20, 30]

for item in numbers:
print("Processing item:", item)
doubled = item * 2
print("Doubled value:", doubled)

print()

# ============================================================

# PART 56: SCRIPT VS MODULE VS PACKAGE

# ============================================================

"""
These terms have related but different meanings.

Script:
A Python file primarily intended to be executed.

Module:
A Python file whose contents can be imported.

Package:
A structured collection of Python modules.

The same Python file can sometimes be used both as:

* A directly executed program
* An importable module

Program structure becomes increasingly important as projects grow.
"""

# ============================================================

# PART 57: REPL, SCRIPT, AND NOTEBOOK EXECUTION

# ============================================================

"""
Python code can be executed in different environments.

REPL:
Interactive command-by-command execution.

Script:
Execution of a saved .py file.

Notebook:
Execution organized into separate cells.

Each environment is useful for different purposes.

A Python script is generally appropriate when reproducible program
execution and conventional source-code organization are required.
"""

# ============================================================

# PART 58: RUNNING PYTHON FROM DIFFERENT LOCATIONS

# ============================================================

"""
Suppose the program exists at:

project/
program.py

If the terminal is inside project:

python program.py

may work.

If the terminal is in a parent directory, execution may require:

python project/program.py

The current directory affects relative paths inside the program.

For this reason, professional applications often use carefully designed
path handling instead of assuming that a program will always be started
from a particular terminal directory.
"""

# ============================================================

# PART 59: USING pathlib FOR RELIABLE PATH HANDLING

# ============================================================

"""
The pathlib module provides object-oriented path handling.

Example:

Path(**file**)

represents the current Python source file when the code is running from
a script.

The parent directory can be obtained using:

Path(**file**).parent
"""

script_path = Path(**file**).resolve() if "**file**" in globals() else Path.cwd()

print("Current script or execution location:")
print(script_path)
print()

# ============================================================

# PART 60: COMMON PROBLEMS WHEN RUNNING PYTHON

# ============================================================

"""
Problem 1:

'python' is not recognized.

Possible cause:

The Python executable is not available through PATH.

Problem 2:

No such file or directory.

Possible cause:

The terminal is not in the expected directory or the filename is
incorrect.

Problem 3:

ModuleNotFoundError.

Possible cause:

The package is not installed in the interpreter environment currently
running the program.

Problem 4:

Permission denied.

Possible cause:

Operating system file permissions.

Problem 5:

SyntaxError.

Possible cause:

Invalid Python syntax.

Problem 6:

The program appears to do nothing.

Possible causes:

* No output statements
* Code path not executed
* Program waiting for input
* Logic condition not satisfied
  """

# ============================================================

# PART 61: FILE NAMING CONSIDERATIONS

# ============================================================

"""
Python filenames should be chosen carefully.

Avoid naming files after standard library modules.

For example, creating files named:

random.py
math.py
json.py

can interfere with imports because Python may import the local file
instead of the intended standard library module.

Descriptive lowercase filenames are commonly used.

Examples:

student_records.py
data_processor.py
calculator.py

Names containing spaces should generally be avoided for Python source
files because they complicate command-line execution.
"""

# ============================================================

# PART 62: PYTHON CODE STYLE

# ============================================================

"""
Python code is easier to maintain when written consistently.

Common style principles include:

* Clear names
* Consistent indentation
* Logical organization
* Appropriate comments
* Reasonable line lengths
* Functions with focused responsibilities

Python's PEP 8 is a widely recognized style guide.

Code style does not usually change whether a program executes, but it
strongly affects readability and maintainability.
"""

# ============================================================

# PART 63: A COMPLETE SMALL PROGRAM

# ============================================================

"""
The following example combines several concepts:

* Variables
* Functions
* User input
* Type conversion
* Conditional logic
* Program entry point

The input lines remain commented out so the educational script can be
executed automatically.
"""

def calculate_square(number):
"""Return the square of a number."""
return number ** 2

def demonstrate_program():
sample_number = 12
squared_value = calculate_square(sample_number)

```
print("Original number:", sample_number)
print("Squared number:", squared_value)
```

demonstrate_program()
print()

# ============================================================

# PART 64: EXECUTION CONTEXT

# ============================================================

"""
The same Python code can behave differently depending on execution
context.

Important contextual factors include:

* Python version
* Python implementation
* Operating system
* Current working directory
* Virtual environment
* Installed packages
* Environment variables
* Command-line arguments

When diagnosing unexpected behavior, identifying the execution context
is often more useful than immediately changing the source code.
"""

print("Execution context information")
print("---------------------------")
print("Python executable:", sys.executable)
print("Python version:", sys.version.split()[0])
print("Working directory:", os.getcwd())
print()

# ============================================================

# PART 65: A PRACTICAL EXECUTION WORKFLOW

# ============================================================

"""
A typical workflow for running a Python program is:

1. Install Python.
2. Verify the interpreter version.
3. Create a project directory.
4. Open a terminal in that directory.
5. Create a .py file.
6. Write Python code.
7. Save the file.
8. Execute the file using the intended Python interpreter.
9. Read program output.
10. Investigate errors using traceback information.
11. Modify the source code.
12. Save and run again.

This cycle is the basic development loop:

Write
|
v
Save
|
v
Run
|
v
Observe
|
v
Debug
|
v
Modify
"""

# ============================================================

# PART 66: VERIFYING A PYTHON ENVIRONMENT PROGRAMMATICALLY

# ============================================================

"""
The following information can help identify which Python environment is
actually executing a program.
"""

import platform

print("System information")
print("Operating system:", platform.system())
print("Python executable:", sys.executable)
print("Python version:", platform.python_version())
print("Current directory:", Path.cwd())
print()

# ============================================================

# PART 67: UNDERSTANDING REPRODUCIBLE EXECUTION

# ============================================================

"""
A program is easier to reproduce when its execution environment is
clearly defined.

A reproducible Python project typically considers:

* Python version
* Required packages
* Package versions
* Project structure
* Configuration
* Execution command

A program that works on one computer may fail on another if these
conditions differ.

This is one reason virtual environments and dependency management are
important in professional Python development.
"""

# ============================================================

# PART 68: FINAL EXECUTABLE DEMONSTRATION

# ============================================================

"""
This final section demonstrates the fundamental relationship between
a Python source file and its execution.

When this file is saved with a .py extension and executed through a
Python interpreter, Python processes the instructions from the source
file according to the program's execution flow.
"""

def display_execution_message():
message = "Python program execution completed successfully."
print(message)

display_execution_message()

