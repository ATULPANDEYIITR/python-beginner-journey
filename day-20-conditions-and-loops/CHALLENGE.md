# Day 20 Challenge: Conditions and Loops

Apply your knowledge of conditions and loops to solve these progressive challenges. Write your solutions in a new Python file or extend the existing implementation.

---

## Challenge 1: Beginner (Temperature Classifier)
**Goal**: Write a program that classifies a list of temperatures.
- **Input**: A list of temperatures in Celsius: `[0, 12, 35, -5, 22, 40, 18]`
- **Rules**:
  - If temp < 0: Print "Freezing"
  - If 0 <= temp <= 15: Print "Cold"
  - If 16 <= temp <= 30: Print "Warm"
  - If temp > 30: Print "Hot"
- **Constraint**: Use a `for` loop and `if-elif-else` statements.

---

## Challenge 2: Intermediate (Inventory Restock Predictor)
**Goal**: Help a warehouse manager identify items that need restocking and calculate the total cost to restock them.
- **Input**: A list of dictionaries representing inventory items:
  ```python
  inventory = [
      {"item": "Laptop", "stock": 5, "min_required": 10, "unit_cost": 800},
      {"item": "Mouse", "stock": 50, "min_required": 20, "unit_cost": 20},
      {"item": "Monitor", "stock": 3, "min_required": 8, "unit_cost": 250},
      {"item": "Keyboard", "stock": 12, "min_required": 15, "unit_cost": 45}
  ]
  ```
- **Rules**:
  - Loop through the inventory.
  - If `stock` is less than `min_required`, calculate the quantity to order (`min_required - stock`).
  - Calculate the cost for that item and add it to the running total.
  - Print the items to be ordered and their quantities.
  - Print the total restock cost at the end.

---

## Challenge 3: Advanced (Nested Loop Matrix Transposition)
**Goal**: Transpose a 2D matrix (swap rows and columns) using nested loops without using external libraries like NumPy.
- **Input**:
  ```python
  matrix = [
      [1, 2, 3],
      [4, 5, 6],
      [7, 8, 9]
  ]
  ```
- **Output**:
  ```python
  transposed = [
      [1, 4, 7],
      [2, 5, 8],
      [3, 6, 9]
  ]
  ```
- **Constraint**: Use nested `for` loops.

---

## Challenge 4: Expert (Custom Event Loop Engine)
**Goal**: Build a simple event loop simulation that processes tasks from a queue based on priority and execution time limits.
- **Input**: A queue of tasks:
  ```python
  tasks = [
      {"id": 1, "name": "Database Backup", "priority": "high", "duration": 3},
      {"id": 2, "name": "Send Emails", "priority": "low", "duration": 2},
      {"id": 3, "name": "Render Video", "priority": "critical", "duration": 8},
      {"id": 4, "name": "Clean Temp Files", "priority": "low", "duration": 1}
  ]
  ```
- **Rules**:
  - You have a maximum execution time budget of **10 units**.
  - Process tasks in order.
  - If a task's duration exceeds the remaining budget, skip it (`continue`) and look for a shorter task.
  - If the budget reaches exactly 0, stop processing (`break`).
  - Print a detailed log of executed tasks and the remaining budget.

---

## Challenge 5: Bonus (O(N) Two-Sum Solver)
**Goal**: Find two numbers in an array that add up to a specific target. 
- **Input**: `nums = [2, 7, 11, 15]`, `target = 9`
- **Constraint**: Optimize your solution to run in $O(N)$ time complexity using a single loop and a dictionary (hash map) instead of a nested $O(N^2)$ loop.
- **Output**: Indices of the two numbers (e.g., `[0, 1]`).