# Day 20: Conditions and Loops in Python

Welcome to Day 20 of your 120-day technical learning journey! Today, we are diving deep into the core control flow mechanisms of programming: **Conditions and Loops**. These concepts allow your code to make decisions, repeat operations efficiently, and handle complex, dynamic datasets.

---

## Learning Objectives
By the end of this day, you will be able to:
1. Master conditional branching using `if`, `elif`, and `else` statements.
2. Implement iterative logic using `for` and `while` loops.
3. Control loop execution dynamically using `break`, `continue`, and `pass`.
4. Write nested loops and conditional expressions (ternary operators).
5. Apply conditions and loops to parse, filter, and process structured datasets (JSON/CSV).
6. Understand performance implications and avoid common pitfalls like infinite loops.

---

## Why This Topic Matters
Without control flow, programs would execute sequentially from top to bottom, performing the exact same operations every run. Conditions and loops introduce **intelligence** and **scalability**:
- **Decision Making**: Allows programs to react to user input, system states, or data variations (e.g., "If the user is an admin, show the dashboard; otherwise, redirect to login").
- **Automation**: Enables processing millions of records with a few lines of code instead of writing repetitive statements.
- **Resource Management**: Helps manage execution flow, ensuring systems do not waste CPU cycles or memory.

---

## Core Concepts & Theory

### 1. Conditional Statements
Python uses boolean evaluation to decide which block of code to execute.

```python
if condition1:
    # Executed if condition1 is True
elif condition2:
    # Executed if condition1 is False and condition2 is True
else:
    # Executed if all previous conditions are False
```

#### Key Rules:
- **Indentation**: Python uses 4 spaces for indentation to define blocks. Incorrect indentation raises an `IndentationError`.
- **Short-Circuit Evaluation**: Logical operators `and` and `or` evaluate expressions from left to right and stop as soon as the outcome is certain.

### 2. Loops
Python provides two primary loop constructs:

#### A. `for` Loop (Definite Iteration)
Used to iterate over a sequence (list, tuple, dictionary, set, string, or range).
```python
for item in sequence:
    # Process item
```

#### B. `while` Loop (Indefinite Iteration)
Repeats a block of code as long as a specified condition remains `True`.
```python
while condition:
    # Keep executing
```

### 3. Loop Control Statements
- `break`: Terminates the loop immediately.
- `continue`: Skips the rest of the current iteration and jumps to the next one.
- `pass`: A null statement used as a placeholder where syntactically required.

---

## Practical Example: Transaction Processor
To demonstrate these concepts consistently across all files in this package, we will build a **Transaction Processor**. 

### Business Rules:
1. **Validation**: Skip transactions with invalid amounts (less than or equal to 0) using `continue`.
2. **Discounts**: Apply tiered discounts based on transaction value:
   - Amount > $500: 20% discount
   - Amount > $100: 10% discount
   - Otherwise: No discount
3. **Budget Limit**: Process transactions sequentially. If the cumulative net cost exceeds our budget, stop processing immediately using `break`.

---

## Implementation Directory

This package contains implementations of the Transaction Processor in multiple languages to highlight syntax differences and conceptual similarities:

- **Python**: `day_20_conditions_and_loops.py` (Core implementation)
- **JavaScript**: `day_20_conditions_and_loops.js` (Node.js compatible)
- **C++**: `day_20_conditions_and_loops.cpp` (High-performance compiled version)
- **SQL**: `day_20_conditions_and_loops.sql` (Database-level conditional processing)
- **Jupyter Notebook**: `day_20_conditions_and_loops.ipynb` (Interactive learning environment)

### Data Files
- **JSON**: `day_20_conditions_and_loops.json`
- **CSV**: `day_20_conditions_and_loops.csv`

---

## How to Run the Project

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Node.js (for JavaScript)
- g++ or any C++11 compatible compiler
- Docker (optional, for containerized execution)

### Running with Shell Script (Linux/macOS)
```bash
chmod +x day_20_conditions_and_loops.sh
./day_20_conditions_and_loops.sh
```

### Running with PowerShell (Windows)
```powershell
Set-ExecutionPolicy Bypass -Scope Process
.\day_20_conditions_and_loops.ps1
```

### Running with Docker
```bash
docker build -t day20-loops .
docker run --rm day20-loops
```

---

## Web Demonstration
An interactive web-based visualization of the transaction processing algorithm is available in `index.html` and `style.css`. Open `index.html` directly in any modern web browser to step through the conditions and loops visually.

---

## Common Mistakes & Debugging
1. **Infinite Loops**: Occur when a `while` loop's condition never becomes `False`. Always ensure the loop variable is updated inside the loop body.
2. **Off-by-One Errors**: Common when using `range()` or index-based loops. Remember that `range(0, 5)` generates numbers from 0 to 4 (5 is exclusive).
3. **Modifying a List While Iterating**: Can cause skipped elements or unexpected behavior. Instead, iterate over a copy of the list or use a list comprehension.
4. **Indentation Errors**: Mixing tabs and spaces in Python. Always use 4 spaces per indentation level.

---

## Interview Questions
1. **Q**: What is the difference between `break` and `continue`?
   - **A**: `break` exits the loop entirely, whereas `continue` skips only the remaining code in the current iteration and moves to the next iteration.
2. **Q**: Does Python support a `do-while` loop? How can you simulate it?
   - **A**: Python does not have a native `do-while` loop. You can simulate it using `while True:` and placing a conditional `break` at the end of the loop body.
3. **Q**: What is the purpose of the `else` clause in Python loops?
   - **A**: The `else` block executes only if the loop completes normally without encountering a `break` statement.

---

## Learning Outcomes
By completing today's exercises, you have mastered the fundamental building blocks of algorithmic logic. You can now write programs that analyze data dynamically, handle errors gracefully, and automate complex workflows.