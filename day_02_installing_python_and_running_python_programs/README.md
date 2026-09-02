# Installing Python and Running Python Programs

## Python as a Programming Language and Runtime Environment

Python is a high-level, general-purpose programming language used for software development, automation, data analysis, web development, artificial intelligence, scientific computing, cybersecurity, scripting, and many other applications. A Python program is written as source code, usually stored in a file with the `.py` extension.

Examples of Python source files include:

```text
hello.py
calculator.py
student_records.py
data_processor.py
```

Writing Python code alone is not sufficient for execution. A Python interpreter is required to process and execute the instructions contained in a Python source file.

A simplified representation of Python program execution is:

```text
Python Source Code
        ↓
Python Interpreter
        ↓
Intermediate Processing / Bytecode
        ↓
Python Runtime
        ↓
Program Output
```

The exact internal execution process depends on the Python implementation being used. CPython, the most widely used implementation, compiles Python source code into bytecode and executes it through its runtime environment.

---

# The Python Interpreter

The Python interpreter is the executable program responsible for processing Python source code.

After Python has been installed, a terminal may provide commands such as:

```text
python
python3
py
```

The command available on a particular system depends on the operating system, Python distribution, installation method, and environment configuration.

A Python program may be executed using commands such as:

```text
python program.py
```

```text
python3 program.py
```

or, on many Windows installations:

```text
py program.py
```

The command identifies the Python interpreter and provides the Python source file as an argument.

---

# Checking the Python Installation

After installing Python, the installation should be verified through a terminal.

Common commands include:

### Windows

```text
python --version
```

or:

```text
py --version
```

### Linux and macOS

```text
python3 --version
```

Depending on the environment, the following may also work:

```text
python --version
```

The output should display the installed Python version, for example:

```text
Python 3.x.x
```

Python can also report information about the interpreter currently executing a program.

```python
import sys

print(sys.executable)
print(sys.version)
```

`sys.executable` identifies the Python executable currently running the program, while `sys.version` provides version information.

This distinction becomes important when multiple Python versions or environments exist on the same computer.

---

# Understanding Python Versions

Python versions generally follow this format:

```text
Major.Minor.Micro
```

For example:

```text
3.12.5
```

The components represent:

```text
3  → Major version
12 → Minor version
5  → Maintenance or micro version
```

The Python version can affect:

* Available language features
* Standard library functionality
* Package compatibility
* Security updates
* Project requirements

A single computer can contain multiple Python installations. For example:

```text
Python 3.10
Python 3.11
Python 3.12
Python 3.13
```

A Python project should therefore be associated with a specific interpreter rather than assuming that every `python` command refers to the same version.

---

# Installing Python on Windows

A typical Python installation on Windows consists of obtaining a Python distribution, running the installer, completing the installation process, and verifying the installation through PowerShell, Command Prompt, or Windows Terminal.

An important installation concept is the `PATH` environment variable.

`PATH` is used by the operating system to locate executable programs. When the Python installation directory is correctly available through `PATH`, the terminal can locate Python when a command such as the following is entered:

```text
python
```

If Python cannot be found, the terminal may report that the command is not recognized.

Windows installations may also provide the Python Launcher, which is commonly accessed using:

```text
py
```

Examples include:

```text
py --version
```

```text
py program.py
```

The launcher can be particularly useful when multiple Python versions are installed.

---

# Installing Python on macOS

macOS may contain Python-related software, but the Python environment used by the operating system should not automatically be treated as the development environment for personal projects.

Modern Python installations are commonly accessed using:

```text
python3
```

The installed version can be checked using:

```text
python3 --version
```

A Python program can then be executed using:

```text
python3 program.py
```

The exact command depends on the installation and environment configuration.

---

# Installing Python on Linux

Many Linux distributions use Python for operating system tools and system-level functionality. Because of this, modifying or replacing the system Python without understanding its role can create problems.

Python is commonly installed through the package management system associated with the Linux distribution.

After installation, the version can commonly be checked using:

```text
python3 --version
```

Python programs are commonly executed using:

```text
python3 program.py
```

The distinction between system-level Python and project-specific Python environments is particularly important in Linux development.

---

# The Terminal and Python Execution

A terminal is a text-based interface used to interact with an operating system.

Common terminal environments include:

### Windows

* Command Prompt
* PowerShell
* Windows Terminal

### Linux

* Bash
* Zsh
* Fish

### macOS

* Zsh
* Bash

A command generally consists of a command name followed by arguments.

For example:

```text
python hello.py
```

Here:

```text
python
```

identifies the interpreter command, while:

```text
hello.py
```

identifies the Python file to execute.

Another example is:

```text
python --version
```

Here, `--version` is an option that requests version information from Python.

---

# Working with Directories

Python programs are stored inside directories, also called folders.

Suppose a project exists at:

```text
C:\Users\Student\Documents\PythonProjects
```

The terminal often needs to be moved into the appropriate directory before executing a program.

The command commonly used to change directories is:

```text
cd
```

For example:

```text
cd Documents
```

To move to the parent directory:

```text
cd ..
```

The current working directory can commonly be displayed using:

```text
pwd
```

Files can be listed using commands such as:

```text
dir
```

on Windows environments, or:

```text
ls
```

on Linux and macOS systems.

Directory awareness is essential because Python execution depends on locating both the Python interpreter and the source file being executed.

---

# Creating a Python Source File

Python programs are normally stored in text files with the `.py` extension.

For example:

```text
hello.py
```

A Python source file can be created using:

* Visual Studio Code
* IDLE
* PyCharm
* Sublime Text
* Text editors
* Terminal-based editors

A simple Python program may contain:

```python
print("Hello, World!")
```

When saved as `hello.py`, it can be executed by a Python interpreter.

---

# The First Python Program

A conventional first Python program is:

```python
print("Hello, World!")
```

`print()` is a built-in Python function used to display output.

The value:

```python
"Hello, World!"
```

is a string.

A string represents textual data.

Python allows ordinary strings to be written using either single or double quotation marks.

```python
print("Python")
print('Python')
```

Both statements create and display strings.

---

# Running a Python Program

Suppose a Python file named `hello.py` exists in the current directory.

The program can be executed using one of the available interpreter commands:

```text
python hello.py
```

or:

```text
python3 hello.py
```

or:

```text
py hello.py
```

The execution process can be represented as:

```text
Terminal
   ↓
Python Interpreter Command
   ↓
Python Source File
   ↓
Instruction Processing
   ↓
Program Output
```

The interpreter reads the Python source file and executes its instructions according to Python's execution rules.

---

# Current Working Directory

Every running program operates within an execution context that includes a current working directory.

The current working directory affects:

* Relative file paths
* File reading
* File writing
* Certain module import behaviors
* Resource discovery

Python can display the current working directory using:

```python
import os

print(os.getcwd())
```

The `os.getcwd()` function returns the directory from which the process is currently operating.

---

# Interactive Python Mode

Python can also be used interactively.

Entering a Python interpreter command without specifying a file can start an interactive session.

For example:

```text
python
```

Python commonly displays an interactive prompt:

```text
>>>
```

Instructions can then be entered directly.

```text
>>> 10 + 20
30
```

```text
>>> print("Hello")
Hello
```

Interactive mode is useful for experimentation, testing expressions, inspecting objects, and learning syntax.

A Python script is generally more appropriate when code needs to be saved, organized, reused, or developed into a larger program.

---

# Expressions and Statements

An expression produces a value.

Examples:

```python
10 + 20
```

```python
5 * 8
```

```python
"Python" + " Programming"
```

A statement performs an action.

Examples include:

```python
x = 10
```

```python
print(x)
```

```python
if x > 5:
    print("Greater than five")
```

In interactive mode, Python can automatically display the result of an expression.

In a Python script, a value normally needs to be explicitly passed to `print()` if it should appear in the terminal output.

---

# Execution Order

Python generally executes instructions in a script from top to bottom.

For example:

```python
print("First")
print("Second")
print("Third")
```

The output is:

```text
First
Second
Third
```

Execution flow can be modified using:

* Conditional statements
* Loops
* Functions
* Exceptions
* Program termination

Understanding execution order is essential for debugging because a program does not necessarily execute every line in a source file.

---

# Comments

Comments provide explanatory information inside Python source code.

A single-line comment begins with:

```python
#
```

Example:

```python
# Store the number of students
student_count = 25
```

Comments are primarily intended for people reading and maintaining the code.

Useful comments explain context, reasoning, or decisions that are not immediately obvious from the source code.

---

# Multi-Line Strings and Docstrings

Python supports strings that span multiple lines through triple quotation marks.

```python
"""
This is a multi-line string.
"""
```

Triple-quoted strings are also used for documentation strings, commonly called docstrings.

A function can contain a docstring:

```python
def calculate_total():
    """Calculate and return the total value."""
```

Docstrings can document:

* Modules
* Functions
* Classes
* Methods

They provide structured documentation associated with program components.

---

# Variables

A variable is a name associated with an object.

Example:

```python
age = 25
```

The name `age` refers to an integer object with the value `25`.

Python is dynamically typed. Variable names do not require a fixed type declaration before assignment.

For example:

```python
value = 10
value = "Python"
```

The name `value` can later refer to an object of another type.

Python objects still have types, and the operations available depend on those types.

---

# Basic Python Data Types

Common built-in data types include:

| Type       | Purpose                                  |
| ---------- | ---------------------------------------- |
| `int`      | Whole numbers                            |
| `float`    | Decimal numbers                          |
| `str`      | Text                                     |
| `bool`     | Boolean values                           |
| `list`     | Ordered mutable collection               |
| `tuple`    | Ordered immutable collection             |
| `set`      | Collection of unique elements            |
| `dict`     | Key-value mapping                        |
| `NoneType` | Represents the absence of a normal value |

Examples:

```python
age = 25
price = 99.95
name = "Python"
active = True
value = None
```

The type of an object can be inspected using:

```python
type(object_name)
```

---

# User Input

The `input()` function allows a Python program to receive input.

Example:

```python
name = input("Enter your name: ")
```

The value returned by `input()` is a string.

Even when the user enters:

```text
25
```

Python receives textual data equivalent to:

```python
"25"
```

Numerical conversion is therefore required when numerical operations are needed.

```python
age = int(input("Enter your age: "))
```

---

# Type Conversion

Python provides functions for converting values between types.

Common conversion functions include:

```python
int()
float()
str()
bool()
```

Examples:

```python
number = int("100")
decimal = float("45.5")
text = str(250)
```

Conversion can fail if the source value cannot validly be converted to the requested type.

For example:

```python
int("Python")
```

raises an error because `"Python"` does not represent an integer.

---

# Operators

Python provides operators for performing calculations and comparisons.

## Arithmetic Operators

```text
+   Addition
-   Subtraction
*   Multiplication
/   Division
//  Floor division
%   Remainder
**  Exponentiation
```

Example:

```python
a = 17
b = 5

print(a + b)
print(a - b)
print(a * b)
print(a / b)
print(a // b)
print(a % b)
print(a ** b)
```

## Comparison Operators

```text
==
!=
>
<
>=
<=
```

## Logical Operators

```text
and
or
not
```

## Assignment Operators

```text
=
+=
-=
*=
/=
```

---

# Conditional Statements

Conditional statements allow programs to select different execution paths.

Python uses:

```python
if
```

```python
elif
```

and:

```python
else
```

Example:

```python
marks = 78

if marks >= 90:
    print("Grade A")
elif marks >= 75:
    print("Grade B")
elif marks >= 50:
    print("Grade C")
else:
    print("Grade D")
```

Only the appropriate execution path is selected according to the conditions.

---

# Indentation

Indentation is part of Python syntax.

Example:

```python
if condition:
    print("Inside the condition")
```

The indented statement belongs to the conditional block.

Incorrect indentation can produce an:

```text
IndentationError
```

Four spaces are widely used for one level of indentation.

Tabs and spaces should not be mixed inconsistently.

---

# Loops

Loops repeat instructions.

Python primarily provides `for` and `while` loops.

A `for` loop:

```python
for number in range(1, 6):
    print(number)
```

A `while` loop:

```python
counter = 1

while counter <= 3:
    print(counter)
    counter += 1
```

Loops are essential for processing collections, repeating calculations, reading records, and automating repetitive tasks.

---

# Functions

Functions organize reusable logic.

A function is defined using:

```python
def
```

Example:

```python
def greet(name):
    print("Hello,", name)
```

The function can then be called:

```python
greet("Student")
```

Functions can accept parameters and return values.

```python
def add_numbers(a, b):
    return a + b
```

The returned value can be stored:

```python
result = add_numbers(10, 20)
```

Printing a value and returning a value are different operations.

---

# Errors and Tracebacks

Errors are a normal part of programming.

When a Python program encounters an exception, it commonly displays a traceback.

A traceback can provide information about:

* The source file
* The relevant line
* The execution sequence
* The error type
* The error message

Common Python errors include:

```text
SyntaxError
IndentationError
NameError
TypeError
ValueError
ZeroDivisionError
FileNotFoundError
ModuleNotFoundError
```

Reading the final lines of a traceback is particularly important because they commonly identify the exception that caused execution to stop.

---

# Syntax Errors

A syntax error occurs when Python code violates language rules.

Invalid code:

```python
if True
    print("Hello")
```

Correct code:

```python
if True:
    print("Hello")
```

The missing colon prevents Python from correctly interpreting the conditional statement.

Syntax errors generally prevent normal execution from beginning.

---

# Runtime Errors

Runtime errors occur while a syntactically valid program is executing.

Example:

```python
number = 10
result = number / 0
```

The syntax is valid, but division by zero raises an exception during execution.

---

# Logical Errors

Logical errors occur when a program executes successfully but produces an incorrect result.

Suppose the intended calculation is:

```python
total = price * quantity
```

The following code may execute without an error:

```python
total = price + quantity
```

The result is incorrect because the program logic does not represent the intended calculation.

Logical errors require testing, inspection, and reasoning.

---

# Running Python Programs from an IDE

An Integrated Development Environment provides tools that can simplify development.

Common features include:

* Code editing
* Syntax highlighting
* Debugging
* Breakpoints
* Code completion
* Integrated terminals
* Project management

An IDE Run button still depends on technical details such as:

* Selected Python interpreter
* Program file
* Current working directory
* Environment variables
* Command-line arguments

A program that behaves differently inside an IDE and a terminal may be running under different execution environments.

---

# Visual Studio Code and Python Execution

A common workflow in Visual Studio Code is:

1. Open a project folder.
2. Create or open a `.py` file.
3. Select the Python interpreter.
4. Write and save Python code.
5. Execute the program.

A frequent problem occurs when the editor uses a different interpreter from the one into which packages were installed.

For example, a package may be installed into one Python environment while the selected interpreter belongs to another environment.

The result may be:

```text
ModuleNotFoundError
```

even though the package appears to have been installed successfully.

---

# File Paths

Programs frequently work with files and directories.

An absolute path identifies a complete location.

Windows example:

```text
C:\Users\Student\Documents\data.txt
```

Linux or macOS example:

```text
/home/student/documents/data.txt
```

A relative path is interpreted from the current working directory.

Examples:

```text
data.txt
```

```text
data/data.txt
```

The `pathlib` module provides a structured approach to path handling.

```python
from pathlib import Path

print(Path.cwd())
```

---

# Python Source Code and Encoding

A Python source file is fundamentally a text file.

The file contains characters representing Python instructions.

Modern Python source files commonly use UTF-8 encoding.

A source file such as:

```text
program.py
```

may contain:

```python
print("Hello")
```

The interpreter reads the source code and processes it according to Python syntax and runtime rules.

---

# Python Bytecode

CPython generally compiles Python source code into an intermediate representation called bytecode.

Python may cache bytecode in directories such as:

```text
__pycache__
```

Cached bytecode files commonly use the extension:

```text
.pyc
```

Bytecode caching can improve subsequent module loading in appropriate circumstances.

The `.py` source file remains the primary file edited by the developer.

---

# Python Implementations

Python is a language, but different implementations can execute Python code.

Examples include:

* CPython
* PyPy
* Jython
* IronPython

CPython is the most widely used general-purpose implementation.

Different implementations may differ in:

* Runtime architecture
* Performance characteristics
* Memory behavior
* Platform integration
* Compatibility

---

# The Python Standard Library

Python includes a substantial collection of built-in modules known as the standard library.

Examples include:

```text
os
sys
math
json
datetime
pathlib
statistics
```

A module can be imported using:

```python
import math
```

Example:

```python
import math

print(math.sqrt(16))
```

Standard library modules provide functionality without requiring separate installation in a normal Python distribution.

---

# Third-Party Packages

Python can be extended through third-party packages.

Packages provide functionality for areas such as:

* Data analysis
* Web development
* Automation
* Machine learning
* Scientific computing
* Testing

Python packages are commonly managed using `pip`.

A package can be installed using:

```text
python -m pip install package_name
```

Using `python -m pip` explicitly connects the package installation command with a particular Python interpreter.

This is useful when multiple Python installations are available.

---

# Why `python -m pip` Matters

Suppose a computer contains multiple Python versions.

For example:

```text
Python 3.11
Python 3.12
```

The command:

```text
pip install package_name
```

may use a different Python environment from:

```text
python program.py
```

This can result in a package being installed successfully but remaining unavailable to the interpreter running the program.

The command:

```text
python -m pip install package_name
```

helps establish which Python interpreter is responsible for running `pip`.

---

# Virtual Environments

A virtual environment is an isolated Python environment associated with a project.

Consider two projects:

```text
Project A → requires package version 1
Project B → requires package version 2
```

Installing all dependencies globally can create conflicts.

A virtual environment allows projects to maintain separate package installations.

A common command for creating an environment is:

```text
python -m venv .venv
```

The `.venv` directory contains a project-specific Python environment.

Activation procedures depend on the operating system and terminal.

Virtual environments are important because they separate project dependencies from unrelated Python projects.

---

# Python Interpreter Selection

A Python development environment contains several related but distinct components:

```text
Python language
Python interpreter
Python source file
Python environment
Installed packages
```

When executing:

```text
python program.py
```

several questions matter:

1. Which executable does `python` represent?
2. Which Python version is being used?
3. Which environment belongs to that interpreter?
4. Which packages are installed there?
5. Which source file is being executed?
6. What is the current working directory?

Many environment problems result from confusing these components.

The active interpreter can be inspected using:

```python
import sys

print(sys.executable)
```

---

# Command-Line Arguments

Python programs can receive information through command-line arguments.

Consider:

```text
python program.py input.txt
```

The program can inspect command-line arguments using:

```python
import sys

print(sys.argv)
```

`sys.argv` is a list containing command-line information.

The program filename and additional arguments can be processed by the program.

---

# Program Entry Points

A Python file can be executed directly or imported into another program.

The special variable:

```python
__name__
```

helps distinguish these situations.

A common pattern is:

```python
def main():
    print("Program running")

if __name__ == "__main__":
    main()
```

When the file is executed directly, the condition is satisfied and `main()` is called.

When the file is imported as a module, reusable definitions can be accessed without automatically executing the code guarded by the `__main__` condition.

---

# Modules and Imports

A Python source file can function as a module.

Suppose a file named:

```text
utilities.py
```

contains:

```python
def add(a, b):
    return a + b
```

Another Python program can import it:

```python
import utilities
```

and use:

```python
utilities.add(10, 20)
```

Python searches for modules through locations defined by its import system.

If a module cannot be found, Python may raise:

```text
ModuleNotFoundError
```

---

# Module Search Paths

Python maintains locations used to search for modules.

These can be inspected using:

```python
import sys

print(sys.path)
```

The module search path may include:

* Script-related locations
* Environment package directories
* Installed package directories
* Additional configured locations

Import behavior depends partly on this execution environment.

---

# Environment Variables

Environment variables provide configuration information to processes.

Important examples include:

```text
PATH
PYTHONPATH
```

`PATH` helps the operating system locate executable programs.

`PYTHONPATH` can influence locations searched by Python for modules.

Environment variables can significantly affect program execution and should be configured carefully.

---

# Running Python Modules

Python can execute modules using the `-m` option.

General form:

```text
python -m module_name
```

Examples:

```text
python -m pip
```

```text
python -m venv
```

The `-m` option tells Python to locate and execute a module.

This is particularly useful when interpreter selection matters.

---

# Shebang Lines

On Unix-like operating systems, executable Python scripts can begin with a shebang line.

Example:

```python
#!/usr/bin/env python3
```

The shebang can help the operating system determine which interpreter should execute the script when it is run directly.

Direct execution may also require appropriate file permissions.

---

# Exit Codes

Programs communicate execution status to the operating system through exit codes.

By convention:

```text
0
```

generally indicates successful completion.

A non-zero value generally indicates an error or another special termination condition.

Exit codes are useful when Python programs are executed from:

* Shell scripts
* Automation systems
* Continuous integration systems
* Other programs

---

# Debugging Python Programs

Debugging is the process of finding and correcting problems in software.

Common debugging techniques include:

* Reading traceback messages
* Inspecting variable values
* Using temporary `print()` statements
* Testing smaller sections
* Using breakpoints
* Using an IDE debugger
* Using Python debugging tools

Python also provides debugging support through modules such as `pdb`.

A debugger can pause execution and allow inspection of program state.

---

# Scripts, Modules, and Packages

These terms describe different ways Python code can be organized.

## Script

A Python file primarily intended to be executed.

## Module

A Python file whose definitions can be imported.

## Package

A structured collection of Python modules.

A single Python file can sometimes act both as a script and a module.

The `if __name__ == "__main__":` pattern supports this dual use.

---

# REPL, Scripts, and Notebooks

Python code can be executed in several environments.

## REPL

Interactive, instruction-by-instruction execution.

## Script

Execution of a saved `.py` source file.

## Notebook

Execution organized into separate cells.

Each execution model has different practical uses.

A Python script is particularly suitable for conventional applications, automation, reusable programs, and reproducible execution.

---

# Execution Context

The behavior of a Python program can depend on its execution context.

Important factors include:

* Python version
* Python implementation
* Operating system
* Current working directory
* Virtual environment
* Installed packages
* Environment variables
* Command-line arguments

Python can inspect parts of this context:

```python
import sys
import os

print(sys.executable)
print(sys.version)
print(os.getcwd())
```

When a program behaves unexpectedly, identifying the active execution context is often necessary before changing the source code.

---

# Common Problems When Running Python Programs

## Python Command Cannot Be Found

Possible reasons include:

* Python is not installed.
* The terminal cannot locate the interpreter.
* PATH configuration is incomplete.
* A different interpreter command is required.

---

## Python File Cannot Be Found

Possible reasons include:

* Incorrect current directory
* Incorrect filename
* Typographical error
* Incorrect relative path

---

## ModuleNotFoundError

Possible reasons include:

* Package not installed
* Incorrect interpreter selected
* Package installed into another environment
* Incorrect virtual environment activation

---

## SyntaxError

The Python source code violates language syntax.

The reported line should be inspected carefully, although the actual cause can occasionally originate immediately before the line reported.

---

## IndentationError

Python code contains invalid indentation.

Python uses indentation to define code blocks, so indentation is part of program syntax.

---

## Program Appears Not to Do Anything

Possible reasons include:

* No output instruction exists.
* The expected code path was not reached.
* A condition evaluated differently from expectation.
* The program is waiting for input.
* The program completed without producing visible output.

---

# Python File Naming

Python filenames should be descriptive and simple.

Examples:

```text
calculator.py
student_records.py
data_processor.py
```

Spaces in Python filenames should generally be avoided because they complicate command-line usage.

Names that conflict with standard library modules should also be avoided.

Examples of problematic names include:

```text
math.py
random.py
json.py
```

A local file with one of these names can interfere with imports.

---

# Python Code Style

Readable Python code is easier to understand and maintain.

Important style practices include:

* Meaningful variable names
* Consistent indentation
* Logical program organization
* Focused functions
* Appropriate comments
* Clear file names

PEP 8 is a widely recognized Python style guide.

Style conventions do not usually determine whether Python can execute code, but they strongly influence maintainability and collaboration.

---

# A Practical Program Execution Cycle

The basic Python development process consists of a repeated cycle:

```text
Write Code
    ↓
Save File
    ↓
Run Program
    ↓
Observe Output
    ↓
Inspect Errors
    ↓
Modify Code
    ↓
Run Again
```

This cycle applies to small educational programs as well as large professional software projects.

The complexity of the project may change, but the relationship between source code, interpreter, execution environment, output, and debugging remains fundamental to Python development.

---

# Reproducible Python Execution

A Python program may behave differently on different systems if the execution environment differs.

Reproducible execution depends on identifying and managing:

* Python version
* Project dependencies
* Package versions
* Project structure
* Configuration
* Execution commands

Virtual environments help isolate dependencies.

Interpreter inspection helps confirm which Python installation is running a program.

Dependency management helps establish which packages and versions are required.

Together, these practices reduce the difference between a program that works only on one machine and a program that can be consistently executed in a controlled environment.

---

# Fundamental Relationship Between Installation and Execution

Installing Python provides an interpreter capable of processing Python source code.

A Python source file contains program instructions.

The terminal or an IDE invokes a selected interpreter.

The interpreter executes the program within a particular environment.

That environment determines important conditions such as:

```text
Python version
Python executable
Installed packages
Current directory
Environment variables
Command-line arguments
Operating system behavior
```

Understanding these relationships is essential because running a Python program is not only a matter of pressing a Run button. Program execution is the interaction between source code, interpreter selection, operating system behavior, file locations, dependencies, and runtime configuration.

