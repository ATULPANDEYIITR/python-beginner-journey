# Day 0: Python Operators
# This program demonstrates Arithmetic, Comparison, Assignment,
# Logical, Membership, and Identity Operators.


# ============================================================
# 1. ARITHMETIC OPERATORS
# ============================================================

print("\n========== ARITHMETIC OPERATORS ==========")

num1 = 20
num2 = 6

print("First Number:", num1)
print("Second Number:", num2)

# Addition
print("\nAddition (+):", num1 + num2)

# Subtraction
print("Subtraction (-):", num1 - num2)

# Multiplication
print("Multiplication (*):", num1 * num2)

# Division
print("Division (/):", num1 / num2)

# Floor Division
print("Floor Division (//):", num1 // num2)

# Modulus
print("Modulus (%):", num1 % num2)

# Exponentiation
print("Exponentiation (**):", num1 ** num2)


# ============================================================
# 2. COMPARISON OPERATORS
# ============================================================

print("\n========== COMPARISON OPERATORS ==========")

a = 10
b = 20

print("Value of a:", a)
print("Value of b:", b)

# Equal to
print("\na == b:", a == b)

# Not equal to
print("a != b:", a != b)

# Greater than
print("a > b:", a > b)

# Less than
print("a < b:", a < b)

# Greater than or equal to
print("a >= b:", a >= b)

# Less than or equal to
print("a <= b:", a <= b)


# ============================================================
# 3. ASSIGNMENT OPERATORS
# ============================================================

print("\n========== ASSIGNMENT OPERATORS ==========")

value = 10

print("\nInitial value:", value)

# Addition assignment
value += 5
print("After value += 5:", value)

# Subtraction assignment
value -= 3
print("After value -= 3:", value)

# Multiplication assignment
value *= 2
print("After value *= 2:", value)

# Division assignment
value /= 4
print("After value /= 4:", value)

# Floor division assignment
value //= 2
print("After value //= 2:", value)

# Modulus assignment
value %= 3
print("After value %= 3:", value)

# Exponentiation assignment
value **= 2
print("After value **= 2:", value)


# ============================================================
# 4. LOGICAL OPERATORS
# ============================================================

print("\n========== LOGICAL OPERATORS ==========")

age = 25
has_id = True

# AND operator
print("\nAge is 18 or above AND person has ID:")
print(age >= 18 and has_id)

# OR operator
print("\nPerson is either 18 or above OR has ID:")
print(age >= 18 or has_id)

# NOT operator
print("\nNOT has_id:")
print(not has_id)


# ============================================================
# 5. MEMBERSHIP OPERATORS
# ============================================================

print("\n========== MEMBERSHIP OPERATORS ==========")

languages = ["Python", "Java", "C++", "JavaScript"]

print("\nProgramming Languages:", languages)

# IN operator
print("\nIs Python in the list?")
print("Python" in languages)

# NOT IN operator
print("\nIs Ruby not in the list?")
print("Ruby" not in languages)


# Membership operators with strings

message = "I am learning Python"

print("\nMessage:", message)

print("\nIs 'Python' present in the message?")
print("Python" in message)

print("\nIs 'Java' not present in the message?")
print("Java" not in message)


# ============================================================
# 6. IDENTITY OPERATORS
# ============================================================

print("\n========== IDENTITY OPERATORS ==========")

list1 = [1, 2, 3]
list2 = [1, 2, 3]

# Both lists contain the same values
print("\nlist1:", list1)
print("list2:", list2)

# Equality checks whether values are equal
print("\nlist1 == list2:")
print(list1 == list2)

# Identity checks whether both variables refer to the same object
print("\nlist1 is list2:")
print(list1 is list2)


# Making list3 refer to the same object as list1

list3 = list1

print("\nlist3 = list1")

print("\nlist1 == list3:")
print(list1 == list3)

print("\nlist1 is list3:")
print(list1 is list3)

# IS NOT operator

print("\nlist1 is not list2:")
print(list1 is not list2)

print("\nlist1 is not list3:")
print(list1 is not list3)


# ============================================================
# PROGRAM COMPLETED
# ============================================================

print("\n========== END OF DAY 4 OPERATORS PROGRAM ==========")
