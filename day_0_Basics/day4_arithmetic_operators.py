# Day 4: Python Arithmetic Operators

# Taking input from the user
num1 = float(input("Enter the first number: "))
num2 = float(input("Enter the second number: "))

# Addition
addition = num1 + num2
print("\nAddition:", addition)

# Subtraction
subtraction = num1 - num2
print("Subtraction:", subtraction)

# Multiplication
multiplication = num1 * num2
print("Multiplication:", multiplication)

# Division
if num2 != 0:
    division = num1 / num2
    print("Division:", division)
else:
    print("Division: Cannot divide by zero")

# Floor Division
if num2 != 0:
    floor_division = num1 // num2
    print("Floor Division:", floor_division)
else:
    print("Floor Division: Cannot divide by zero")

# Modulus
if num2 != 0:
    modulus = num1 % num2
    print("Modulus:", modulus)
else:
    print("Modulus: Cannot divide by zero")

# Exponentiation
exponentiation = num1 ** num2
print("Exponentiation:", exponentiation)
