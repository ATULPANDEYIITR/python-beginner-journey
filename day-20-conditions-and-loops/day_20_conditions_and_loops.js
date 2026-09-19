/**
 * Day 20: Conditions and Loops
 * 
 * JavaScript implementation of the Transaction Processor.
 */

const fs = require('fs');
const path = require('path');

function calculateDiscount(amount) {
    if (amount > 500.0) {
        return amount * 0.20;
    } else if (amount > 100.0) {
        return amount * 0.10;
    } else {
        return 0.0;
    }
}

function processTransactions(transactions, budget) {
    let processedList = [];
    let totalProcessed = 0;
    let totalDiscounted = 0.0;
    let remainingBudget = parseFloat(budget);

    for (let i = 0; i < transactions.length; i++) {
        const tx = transactions[i];
        const txId = tx.id;
        const customer = tx.customer || "Unknown";
        const amount = parseFloat(tx.amount || 0.0);

        // 1. Validation Condition
        if (amount <= 0) {
            console.log(`[SKIP] Transaction ${txId} for ${customer} skipped: Invalid amount ($${amount.toFixed(2)})`);
            continue;
        }

        // 2. Calculate Discount
        const discount = calculateDiscount(amount);
        const netAmount = amount - discount;

        // 3. Budget Check Condition
        if (netAmount > remainingBudget) {
            console.log(`[STOP] Transaction ${txId} for ${customer} ($${netAmount.toFixed(2)}) exceeds remaining budget ($${remainingBudget.toFixed(2)}). Stopping process.`);
            break;
        }

        // 4. Process Transaction
        remainingBudget -= netAmount;
        totalDiscounted += discount;
        totalProcessed++;

        processedList.push({
            id: txId,
            customer: customer,
            original_amount: amount,
            discount: discount,
            net_amount: netAmount
        });
        console.log(`[PROCESSED] Transaction ${txId} for ${customer}: Original: $${amount.toFixed(2)}, Discount: $${discount.toFixed(2)}, Net: $${netAmount.toFixed(2)}`);
    }

    return {
        processed_count: totalProcessed,
        total_discount_applied: parseFloat(totalDiscounted.toFixed(2)),
        remaining_budget: parseFloat(remainingBudget.toFixed(2)),
        processed_transactions: processedList
    };
}

// Load JSON data
const jsonPath = path.join(__dirname, 'day_20_conditions_and_loops.json');
let transactionsData = [];
let budgetLimit = 700.0;

try {
    const fileContent = fs.readFileSync(jsonPath, 'utf8');
    const data = JSON.parse(fileContent);
    transactionsData = data.transactions || [];
    budgetLimit = data.budget_limit || 700.0;
} catch (err) {
    // Fallback data
    transactionsData = [
        { id: 1, customer: "Alice", amount: 120.0, category: "Electronics" },
        { id: 2, customer: "Bob", amount: -50.0, category: "Books" },
        { id: 3, customer: "Charlie", amount: 600.0, category: "Electronics" },
        { id: 4, customer: "David", amount: 50.0, category: "Groceries" },
        { id: 5, customer: "Eve", amount: 200.0, category: "Books" }
    ];
    budgetLimit = 700.0;
}

console.log("=== Starting JavaScript Transaction Processing ===");
console.log(`Initial Budget: $${budgetLimit.toFixed(2)}\n`);

const results = processTransactions(transactionsData, budgetLimit);

console.log("\n=== Processing Summary ===");
console.log(`Total Transactions Processed: ${results.processed_count}`);
console.log(`Total Discounts Applied: $${results.total_discount_applied.toFixed(2)}`);
console.log(`Remaining Budget: $${results.remaining_budget.toFixed(2)}`);
