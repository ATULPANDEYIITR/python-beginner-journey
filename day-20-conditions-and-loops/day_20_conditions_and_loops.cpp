/**
 * Day 20: Conditions and Loops
 * 
 * C++ implementation of the Transaction Processor.
 */

#include <iostream>
#include <vector>
#include <string>
#include <iomanip>

struct Transaction {
    int id;
    std::string customer;
    double amount;
    std::string category;
};

struct ProcessResult {
    int processed_count;
    double total_discount_applied;
    double remaining_budget;
};

double calculateDiscount(double amount) {
    if (amount > 500.0) {
        return amount * 0.20;
    } else if (amount > 100.0) {
        return amount * 0.10;
    } else {
        return 0.0;
    }
}

ProcessResult processTransactions(const std::vector<Transaction>& transactions, double budget) {
    int totalProcessed = 0;
    double totalDiscounted = 0.0;
    double remainingBudget = budget;

    for (const auto& tx : transactions) {
        // 1. Validation Condition
        if (tx.amount <= 0) {
            std::cout << "[SKIP] Transaction " << tx.id << " for " << tx.customer 
                      << " skipped: Invalid amount ($" << std::fixed << std::setprecision(2) << tx.amount << ")\n";
            continue;
        }

        // 2. Calculate Discount
        double discount = calculateDiscount(tx.amount);
        double netAmount = tx.amount - discount;

        // 3. Budget Check Condition
        if (netAmount > remainingBudget) {
            std::cout << "[STOP] Transaction " << tx.id << " for " << tx.customer 
                      << " ($" << netAmount << ") exceeds remaining budget ($" << remainingBudget << "). Stopping process.\n";
            break;
        }

        // 4. Process Transaction
        remainingBudget -= netAmount;
        totalDiscounted += discount;
        totalProcessed++;

        std::cout << "[PROCESSED] Transaction " << tx.id << " for " << tx.customer 
                  << ": Original: $" << tx.amount << ", Discount: $" << discount 
                  << ", Net: $" << netAmount << "\n";
    }

    return {totalProcessed, totalDiscounted, remainingBudget};
}

int main() {
    // Hardcoded dataset matching the JSON/CSV files
    std::vector<Transaction> transactions = {
        {1, "Alice", 120.0, "Electronics"},
        {2, "Bob", -50.0, "Books"},
        {3, "Charlie", 600.0, "Electronics"},
        {4, "David", 50.0, "Groceries"},
        {5, "Eve", 200.0, "Books"}
    };

    double budgetLimit = 700.0;

    std::cout << "=== Starting C++ Transaction Processing ===\n";
    std::cout << "Initial Budget: $" << std::fixed << std::setprecision(2) << budgetLimit << "\n\n";

    ProcessResult result = processTransactions(transactions, budgetLimit);

    std::cout << "\n=== Processing Summary ===\n";
    std::cout << "Total Transactions Processed: " << result.processed_count << "\n";
    std::cout << "Total Discounts Applied: $" << result.total_discount_applied << "\n";
    std::cout << "Remaining Budget: $" << result.remaining_budget << "\n";

    return 0;
}
