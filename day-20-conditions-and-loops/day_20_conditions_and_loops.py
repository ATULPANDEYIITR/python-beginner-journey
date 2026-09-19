"""
Day 20: Conditions and Loops

This script implements a Transaction Processor that demonstrates:
- 'for' loops to iterate over datasets
- 'while' loops to process queues
- 'if-elif-else' conditional structures
- 'break' and 'continue' control statements
"""

import json
import os

def calculate_discount(amount):
    """Calculates tiered discounts based on transaction amount."""
    if amount > 500.0:
        return amount * 0.20  # 20% discount
    elif amount > 100.0:
        return amount * 0.10  # 10% discount
    else:
        return 0.0  # No discount

def process_transactions(transactions, budget):
    """
    Processes a list of transactions under a strict budget limit.
    
    Rules:
    - Skip invalid transactions (amount <= 0) using 'continue'.
    - Apply tiered discounts.
    - Stop processing if the cumulative net cost exceeds the budget using 'break'.
    """
    processed_list = []
    total_processed = 0
    total_discounted = 0.0
    remaining_budget = float(budget)
    
    for tx in transactions:
        tx_id = tx.get("id")
        customer = tx.get("customer", "Unknown")
        amount = float(tx.get("amount", 0.0))
        category = tx.get("category", "General")
        
        # 1. Validation Condition (using continue)
        if amount <= 0:
            print(f"[SKIP] Transaction {tx_id} for {customer} skipped: Invalid amount (${amount:.2f})")
            continue
            
        # 2. Calculate Discount (using if-elif-else)
        discount = calculate_discount(amount)
        net_amount = amount - discount
        
        # 3. Budget Check Condition (using break)
        if net_amount > remaining_budget:
            print(f"[STOP] Transaction {tx_id} for {customer} (${net_amount:.2f}) exceeds remaining budget (${remaining_budget:.2f}). Stopping process.")
            break
            
        # 4. Process Transaction
        remaining_budget -= net_amount
        total_discounted += discount
        total_processed += 1
        
        processed_list.append({
            "id": tx_id,
            "customer": customer,
            "original_amount": amount,
            "discount": discount,
            "net_amount": net_amount
        })
        print(f"[PROCESSED] Transaction {tx_id} for {customer}: Original: ${amount:.2f}, Discount: ${discount:.2f}, Net: ${net_amount:.2f}")
        
    return {
        "processed_count": total_processed,
        "total_discount_applied": round(total_discounted, 2),
        "remaining_budget": round(remaining_budget, 2),
        "processed_transactions": processed_list
    }

if __name__ == "__main__":
    # Load sample data from JSON
    json_path = os.path.join(os.path.dirname(__file__), "day_20_conditions_and_loops.json")
    
    try:
        with open(json_path, "r") as file:
            data = json.load(file)
            transactions_data = data.get("transactions", [])
            budget_limit = data.get("budget_limit", 700.0)
    except FileNotFoundError:
        # Fallback dataset if file is missing
        transactions_data = [
            {"id": 1, "customer": "Alice", "amount": 120.0, "category": "Electronics"},
            {"id": 2, "customer": "Bob", "amount": -50.0, "category": "Books"},
            {"id": 3, "customer": "Charlie", "amount": 600.0, "category": "Electronics"},
            {"id": 4, "customer": "David", "amount": 50.0, "category": "Groceries"},
            {"id": 5, "customer": "Eve", "amount": 200.0, "category": "Books"}
        ]
        budget_limit = 700.0

    print("=== Starting Transaction Processing ===")
    print(f"Initial Budget: ${budget_limit:.2f}\n")
    
    results = process_transactions(transactions_data, budget_limit)
    
    print("\n=== Processing Summary ===")
    print(f"Total Transactions Processed: {results['processed_count']}")
    print(f"Total Discounts Applied: ${results['total_discount_applied']:.2f}")
    print(f"Remaining Budget: ${results['remaining_budget']:.2f}")
