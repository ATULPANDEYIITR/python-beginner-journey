-- Day 20: Conditions and Loops
-- SQL demonstration of conditional logic (CASE WHEN) and iterative simulation.

-- Create a temporary table for transactions
CREATE TABLE IF NOT EXISTS transactions (
    id INT PRIMARY KEY,
    customer VARCHAR(50),
    amount DECIMAL(10, 2),
    category VARCHAR(50)
);

-- Populate sample data
INSERT INTO transactions (id, customer, amount, category) VALUES
(1, 'Alice', 120.00, 'Electronics'),
(2, 'Bob', -50.00, 'Books'),
(3, 'Charlie', 600.00, 'Electronics'),
(4, 'David', 50.00, 'Groceries'),
(5, 'Eve', 200.00, 'Books')
ON CONFLICT (id) DO NOTHING;

-- SQL Query demonstrating conditional logic (CASE WHEN) equivalent to if-elif-else
SELECT 
    id,
    customer,
    amount,
    -- Validation Condition
    CASE 
        WHEN amount <= 0 THEN 'INVALID'
        ELSE 'VALID'
    END AS status,
    -- Tiered Discount Logic
    CASE 
        WHEN amount > 500.00 THEN amount * 0.20
        WHEN amount > 100.00 THEN amount * 0.10
        ELSE 0.00
    END AS discount_applied,
    -- Net Amount Calculation
    CASE 
        WHEN amount > 500.00 THEN amount * 0.80
        WHEN amount > 100.00 THEN amount * 0.90
        ELSE amount
    END AS net_amount
FROM transactions;
