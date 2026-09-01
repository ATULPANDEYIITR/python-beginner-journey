# ============================================================
# INTRODUCTION TO PYTHON
# ============================================================
# This program demonstrates the basic concepts of Python,
# including output, comments, variables, data types, user input,
# type conversion, arithmetic operations, and simple expressions.
# ============================================================


# ============================================================
# 1. DISPLAYING OUTPUT
# ============================================================

print("========================================")
print("       WELCOME TO PYTHON PROGRAMMING")
print("========================================")

print("\nPython is a beginner-friendly programming language.")
print("This program demonstrates the basic concepts of Python.")


# ============================================================
# 2. UNDERSTANDING COMMENTS
# ============================================================

# Comments are used to explain Python code.
# Python ignores comments when executing the program.


# ============================================================
# 3. VARIABLES AND VALUES
# ============================================================

name = "Atul"
age = 30
city = "Lucknow"
country = "India"

print("\n========================================")
print("       VARIABLES AND INFORMATION")
print("========================================")

print("Name:", name)
print("Age:", age)
print("City:", city)
print("Country:", country)


# ============================================================
# 4. BASIC DATA TYPES
# ============================================================

name = "Atul"              # String
age = 30                   # Integer
height = 180.5             # Float
is_learning_python = True  # Boolean

print("\n========================================")
print("            BASIC DATA TYPES")
print("========================================")

print("Name:", name)
print("Data Type:", type(name))

print("\nAge:", age)
print("Data Type:", type(age))

print("\nHeight:", height)
print("Data Type:", type(height))

print("\nLearning Python:", is_learning_python)
print("Data Type:", type(is_learning_python))


# ============================================================
# 5. USER INPUT
# ============================================================

print("\n========================================")
print("              USER INPUT")
print("========================================")

user_name = input("Enter your name: ")
user_city = input("Enter your city: ")

print("\nHello,", user_name + "!")
print("You are from", user_city + ".")


# ============================================================
# 6. NUMERICAL INPUT AND TYPE CONVERSION
# ============================================================

print("\n========================================")
print("       NUMERICAL INPUT AND CONVERSION")
print("========================================")

user_age = input("Enter your age: ")

# Converting user input from string to integer
user_age = int(user_age)

next_year_age = user_age + 1

print("Next year, you will be", next_year_age, "years old.")


# ============================================================
# 7. BASIC ARITHMETIC OPERATIONS
# ============================================================

print("\n========================================")
print("        BASIC ARITHMETIC OPERATIONS")
print("========================================")

number1 = 20
number2 = 5

print("First Number:", number1)
print("Second Number:", number2)

print("\nAddition:", number1 + number2)
print("Subtraction:", number1 - number2)
print("Multiplication:", number1 * number2)
print("Division:", number1 / number2)


# ============================================================
# 8. WORKING WITH EXPRESSIONS
# ============================================================

print("\n========================================")
print("             PYTHON EXPRESSIONS")
print("========================================")

marks_python = 85
marks_sql = 90
marks_math = 80

total_marks = marks_python + marks_sql + marks_math
average_marks = total_marks / 3

print("Python Marks:", marks_python)
print("SQL Marks:", marks_sql)
print("Mathematics Marks:", marks_math)

print("\nTotal Marks:", total_marks)
print("Average Marks:", average_marks)


# ============================================================
# 9. COMBINING STRINGS AND VARIABLES
# ============================================================

print("\n========================================")
print("        COMBINING TEXT AND VARIABLES")
print("========================================")

learning_message = (
    name
    + " is learning Python programming and exploring "
    + "the fundamentals of programming."
)

print(learning_message)


# ============================================================
# 10. MULTIPLE VARIABLES
# ============================================================

print("\n========================================")
print("           MULTIPLE VARIABLES")
print("========================================")

language1, language2, language3 = "Python", "SQL", "JavaScript"

print("Language 1:", language1)
print("Language 2:", language2)
print("Language 3:", language3)


# ============================================================
# 11. UPDATING VARIABLES
# ============================================================

print("\n========================================")
print("            UPDATING VARIABLES")
print("========================================")

learning_hours = 2

print("Initial Learning Hours:", learning_hours)

learning_hours = learning_hours + 1

print("Updated Learning Hours:", learning_hours)


# ============================================================
# 12. SIMPLE BOOLEAN VALUES
# ============================================================

print("\n========================================")
print("             BOOLEAN VALUES")
print("========================================")

has_started_python = True
has_completed_introduction = False

print("Started Learning Python:", has_started_python)
print("Completed Introduction Module:", has_completed_introduction)


# ============================================================
# PROGRAM COMPLETION
# ============================================================

print("\n========================================")
print("      INTRODUCTION TO PYTHON COMPLETED")
print("========================================")

print("\nThank you for exploring Python fundamentals!")
print("Keep learning and keep practicing.")
