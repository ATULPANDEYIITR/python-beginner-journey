"""
Unit tests for Day 20: Conditions and Loops
"""

import unittest
from day_20_conditions_and_loops import process_transactions, calculate_discount

class TestConditionsAndLoops(unittest.TestCase):
    
    def setUp(self):
        self.sample_transactions = [
            {"id": 1, "customer": "Alice", "amount": 120.0, "category": "Electronics"},
            {"id": 2, "customer": "Bob", "amount": -50.0, "category": "Books"},
            {"id": 3, "customer": "Charlie", "amount": 600.0, "category": "Electronics"},
            {"id": 4, "customer": "David", "amount": 50.0, "category": "Groceries"},
            {"id": 5, "customer": "Eve", "amount": 200.0, "category": "Books"}
        ]

    def test_calculate_discount(self):
        # Test high tier discount (> 500)
        self.assertEqual(calculate_discount(600.0), 120.0)
        # Test mid tier discount (> 100)
        self.assertEqual(calculate_discount(200.0), 20.0)
        # Test no discount (<= 100)
        self.assertEqual(calculate_discount(50.0), 0.0)

    def test_process_transactions_budget_limit(self):
        # Budget of 700 should process Alice, skip Bob, process Charlie, process David, and break on Eve
        results = process_transactions(self.sample_transactions, 700.0)
        
        self.assertEqual(results["processed_count"], 3)
        self.assertEqual(results["total_discount_applied"], 132.0)  # 12.0 (Alice) + 120.0 (Charlie) + 0.0 (David)
        self.assertEqual(results["remaining_budget"], 62.0)  # 700 - 108 - 480 - 50

    def test_process_transactions_empty(self):
        results = process_transactions([], 100.0)
        self.assertEqual(results["processed_count"], 0)
        self.assertEqual(results["remaining_budget"], 100.0)

if __name__ == "__main__":
    unittest.main()
