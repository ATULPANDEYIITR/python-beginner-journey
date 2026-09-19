/*
 * break, continue, and pass in Python
 * ------------------------------------
 *
 * This JavaScript file complements the Python study program by demonstrating
 * the equivalent loop-control ideas in JavaScript.
 *
 * Important distinction:
 * JavaScript has break and continue, but it does not have Python's pass
 * statement. An empty JavaScript block can be used when no action is required.
 *
 * The examples also demonstrate:
 * - for and while loops
 * - nested loops
 * - labeled break and continue
 * - arrays and filtering
 * - object-oriented processing
 * - exceptions
 * - generators
 * - asynchronous iteration
 * - practical record processing
 * - performance considerations
 *
 * Run with:
 *     node break-continue-pass.js
 */

"use strict";

// ---------------------------------------------------------------------------
// Utility
// ---------------------------------------------------------------------------

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function showResult(label, value) {
    console.log(`${label}:`, value);
}

// ---------------------------------------------------------------------------
// 1. Basic break
// ---------------------------------------------------------------------------

function demonstrateBreak() {
    section("1. Basic break");

    const values = [];

    for (let number = 1; number <= 10; number++) {
        if (number === 6) {
            break;
        }

        values.push(number);
    }

    showResult("Values before break", values);
}

// ---------------------------------------------------------------------------
// 2. Basic continue
// ---------------------------------------------------------------------------

function demonstrateContinue() {
    section("2. Basic continue");

    const oddNumbers = [];

    for (let number = 1; number <= 10; number++) {
        if (number % 2 === 0) {
            continue;
        }

        oddNumbers.push(number);
    }

    showResult("Odd numbers", oddNumbers);
}

// ---------------------------------------------------------------------------
// 3. Python pass equivalent
// ---------------------------------------------------------------------------

function demonstratePassEquivalent() {
    section("3. Python pass and JavaScript");

    const processed = [];

    for (let number = 1; number <= 5; number++) {
        if (number === 3) {
            // JavaScript has no pass keyword.
            // An empty block is a no-op, but it should be used intentionally.
        }

        // Unlike continue, execution reaches this statement.
        processed.push(number);
    }

    showResult("Empty-block result", processed);
}

// ---------------------------------------------------------------------------
// 4. Direct comparison
// ---------------------------------------------------------------------------

function demonstrateComparison() {
    section("4. break vs continue vs empty block");

    const breakResult = [];

    for (let number = 1; number <= 5; number++) {
        if (number === 3) {
            break;
        }

        breakResult.push(number);
    }

    const continueResult = [];

    for (let number = 1; number <= 5; number++) {
        if (number === 3) {
            continue;
        }

        continueResult.push(number);
    }

    const noOpResult = [];

    for (let number = 1; number <= 5; number++) {
        if (number === 3) {
            // Intentional no-op.
        }

        noOpResult.push(number);
    }

    showResult("break", breakResult);
    showResult("continue", continueResult);
    showResult("empty block", noOpResult);
}

// ---------------------------------------------------------------------------
// 5. Search
// ---------------------------------------------------------------------------

function firstMultipleOfSeven(values) {
    for (const value of values) {
        if (value % 7 === 0) {
            return value;
        }
    }

    return null;
}

function demonstrateSearch() {
    section("5. Search");

    const values = [11, 15, 22, 35, 48];

    showResult("First multiple of seven", firstMultipleOfSeven(values));
}

// ---------------------------------------------------------------------------
// 6. while loops
// ---------------------------------------------------------------------------

function demonstrateWhileLoops() {
    section("6. while loops");

    let counter = 0;
    const values = [];

    while (counter < 10) {
        counter++;

        if (counter === 7) {
            break;
        }

        values.push(counter);
    }

    showResult("while + break", values);

    counter = 0;
    const nonMultiplesOfThree = [];

    while (counter < 10) {
        counter++;

        if (counter % 3 === 0) {
            continue;
        }

        nonMultiplesOfThree.push(counter);
    }

    showResult("while + continue", nonMultiplesOfThree);
}

// ---------------------------------------------------------------------------
// 7. Nested loops
// ---------------------------------------------------------------------------

function demonstrateNestedLoops() {
    section("7. Nested loops");

    const result = [];

    for (let row = 0; row < 3; row++) {
        for (let column = 0; column < 5; column++) {
            if (column === 3) {
                break;
            }

            result.push([row, column]);
        }
    }

    showResult("Nearest-loop break", result);
}

// ---------------------------------------------------------------------------
// 8. Labeled break
// ---------------------------------------------------------------------------

function findCoordinate(matrix, target) {
    let found = null;

    searchRows:
    for (let row = 0; row < matrix.length; row++) {
        for (let column = 0; column < matrix[row].length; column++) {
            if (matrix[row][column] === target) {
                found = [row, column];
                break searchRows;
            }
        }
    }

    return found;
}

function demonstrateLabeledBreak() {
    section("8. Labeled break");

    const matrix = [
        [10, 20, 30],
        [40, 50, 60],
        [70, 80, 90]
    ];

    showResult("Position of 80", findCoordinate(matrix, 80));

    /*
     * JavaScript supports labeled break, while Python does not.
     * In Python, a function return or a flag is commonly used to leave
     * multiple nested loops.
     */
}

// ---------------------------------------------------------------------------
// 9. Filtering
// ---------------------------------------------------------------------------

function filterPositiveIntegers(values) {
    const result = [];

    for (const value of values) {
        if (!Number.isInteger(value)) {
            continue;
        }

        if (value <= 0) {
            continue;
        }

        result.push(value);
    }

    return result;
}

function demonstrateFiltering() {
    section("9. Filtering with continue");

    const values = [10, -4, 3.5, 0, 18, 22];

    showResult(
        "Positive integers",
        filterPositiveIntegers(values)
    );
}

// ---------------------------------------------------------------------------
// 10. Exception handling
// ---------------------------------------------------------------------------

function parsePositiveIntegers(values) {
    const result = [];

    for (const text of values) {
        const number = Number(text);

        if (!Number.isInteger(number)) {
            continue;
        }

        if (number <= 0) {
            continue;
        }

        result.push(number);
    }

    return result;
}

function demonstrateValidation() {
    section("10. Validation");

    const inputs = ["10", "abc", "-7", "42", "3.14", "100"];

    showResult(
        "Parsed positive integers",
        parsePositiveIntegers(inputs)
    );

    try {
        JSON.parse("{invalid json}");
    } catch (error) {
        // continue could be used here if this were inside a larger record loop.
        showResult("Caught JSON error", error instanceof SyntaxError);
    }
}

// ---------------------------------------------------------------------------
// 11. Real-world transaction processing
// ---------------------------------------------------------------------------

function processTransactions(transactions) {
    let total = 0;
    let processed = 0;

    for (const transaction of transactions) {
        if (transaction.type === "STOP") {
            break;
        }

        if (transaction.type !== "SALE") {
            continue;
        }

        if (!Number.isFinite(transaction.amount)) {
            continue;
        }

        if (transaction.amount < 0) {
            continue;
        }

        total += transaction.amount;
        processed++;
    }

    return { total, processed };
}

function demonstrateTransactions() {
    section("11. Transaction processing");

    const transactions = [
        { type: "SALE", amount: 120.5 },
        { type: "REFUND", amount: 20 },
        { type: "SALE", amount: 75 },
        { type: "SALE", amount: -10 },
        { type: "SALE", amount: 200 },
        { type: "STOP", amount: 0 },
        { type: "SALE", amount: 9999 }
    ];

    showResult(
        "Transaction analysis",
        processTransactions(transactions)
    );
}

// ---------------------------------------------------------------------------
// 12. Object-oriented example
// ---------------------------------------------------------------------------

class Employee {
    constructor(name, department, salary, active) {
        this.name = name;
        this.department = department;
        this.salary = salary;
        this.active = active;
    }
}

function calculatePayroll(employees, department) {
    let payroll = 0;

    for (const employee of employees) {
        if (!employee.active) {
            continue;
        }

        if (employee.department !== department) {
            continue;
        }

        if (!Number.isFinite(employee.salary) || employee.salary < 0) {
            continue;
        }

        payroll += employee.salary;
    }

    return payroll;
}

function demonstrateClasses() {
    section("12. Class-based processing");

    const employees = [
        new Employee("Asha", "Engineering", 90000, true),
        new Employee("Rahul", "Sales", 70000, true),
        new Employee("Mira", "Engineering", 95000, false),
        new Employee("Vikram", "Engineering", 110000, true)
    ];

    showResult(
        "Engineering payroll",
        calculatePayroll(employees, "Engineering")
    );
}

// ---------------------------------------------------------------------------
// 13. Generator with continue
// ---------------------------------------------------------------------------

function* positiveValues(values) {
    for (const value of values) {
        if (value <= 0) {
            continue;
        }

        yield value;
    }
}

function firstLargeValue(values, minimum) {
    for (const value of values) {
        if (value < minimum) {
            continue;
        }

        return value;
    }

    return null;
}

function demonstrateGenerators() {
    section("13. Generators");

    showResult(
        "Positive generated values",
        [...positiveValues([-4, 2, 0, 7, -3, 10])]
    );

    showResult(
        "First value >= 8",
        firstLargeValue([1, 4, 7, 8, 12], 8)
    );
}

// ---------------------------------------------------------------------------
// 14. Async generator
// ---------------------------------------------------------------------------

async function* sensorStream() {
    yield { id: "S1", temperature: 21 };
    yield { id: "S2", temperature: 31 };
    yield { id: "S3", temperature: 82 };
    yield { id: "S4", temperature: 25 };
}

async function analyzeSensorStream() {
    section("14. Async iteration");

    const accepted = [];

    for await (const reading of sensorStream()) {
        if (reading.temperature < 0) {
            continue;
        }

        if (reading.temperature >= 80) {
            break;
        }

        accepted.push(reading);
    }

    showResult("Accepted readings", accepted);
}

// ---------------------------------------------------------------------------
// 15. Performance comparison
// ---------------------------------------------------------------------------

function containsDuplicate(values) {
    const seen = new Set();

    for (const value of values) {
        if (seen.has(value)) {
            return true;
        }

        seen.add(value);
    }

    return false;
}

function demonstratePerformance() {
    section("15. Performance");

    const values = Array.from({ length: 10000 }, (_, index) => index);

    showResult("Duplicate present", containsDuplicate(values));
    showResult(
        "Duplicate present after insertion",
        containsDuplicate([...values, 9999])
    );

    /*
     * The Set-based algorithm is approximately O(n) average time.
     * An unrestricted nested-loop duplicate search is O(n^2).
     *
     * break/return helps terminate early, but it does not change the
     * worst-case complexity of an algorithm by itself.
     */
}

// ---------------------------------------------------------------------------
// 16. Common infinite-loop mistake
// ---------------------------------------------------------------------------

function demonstrateSafeWhile() {
    section("16. Safe while loop");

    let attempts = 0;
    const maximumAttempts = 5;

    while (true) {
        attempts++;

        if (attempts >= maximumAttempts) {
            break;
        }
    }

    showResult("Attempts", attempts);
}

// ---------------------------------------------------------------------------
// 17. Log analysis
// ---------------------------------------------------------------------------

function analyzeLogs(records) {
    const counts = {
        INFO: 0,
        WARNING: 0,
        ERROR: 0,
        CRITICAL: 0
    };

    for (const record of records) {
        const level = String(record.level).toUpperCase();

        if (level === "CRITICAL") {
            counts.CRITICAL++;
            break;
        }

        if (level === "DEBUG") {
            continue;
        }

        if (!record.message || !record.message.trim()) {
            continue;
        }

        if (!(level in counts)) {
            continue;
        }

        counts[level]++;
    }

    return counts;
}

function demonstrateLogAnalysis() {
    section("17. Log processing");

    const records = [
        { level: "INFO", message: "Request received" },
        { level: "DEBUG", message: "Internal value" },
        { level: "WARNING", message: "High latency" },
        { level: "ERROR", message: "Database failure" },
        { level: "INFO", message: "" },
        { level: "CRITICAL", message: "Database unavailable" },
        { level: "ERROR", message: "Ignored after critical boundary" }
    ];

    showResult("Log counts", analyzeLogs(records));
}

// ---------------------------------------------------------------------------
// 18. Explicit no-op design
// ---------------------------------------------------------------------------

function demonstrateNoOpDesign() {
    section("18. Intentional no-op");

    for (const value of [1, 2, 3]) {
        if (value < 0) {
            // Intentional no-op. This is the closest simple JavaScript
            // equivalent to an empty Python pass branch.
        } else {
            console.log(`Accepted: ${value}`);
        }
    }
}

// ---------------------------------------------------------------------------
// 19. Tests
// ---------------------------------------------------------------------------

function assertEqual(actual, expected, description) {
    const actualText = JSON.stringify(actual);
    const expectedText = JSON.stringify(expected);

    if (actualText !== expectedText) {
        throw new Error(
            `${description}: expected ${expectedText}, got ${actualText}`
        );
    }
}

function runTests() {
    section("19. Tests");

    const breakResult = [];

    for (let number = 0; number < 5; number++) {
        if (number === 3) {
            break;
        }

        breakResult.push(number);
    }

    assertEqual(
        breakResult,
        [0, 1, 2],
        "break test"
    );

    const continueResult = [];

    for (let number = 0; number < 5; number++) {
        if (number === 3) {
            continue;
        }

        continueResult.push(number);
    }

    assertEqual(
        continueResult,
        [0, 1, 2, 4],
        "continue test"
    );

    console.log("All JavaScript assertions passed.");
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
    demonstrateBreak();
    demonstrateContinue();
    demonstratePassEquivalent();
    demonstrateComparison();
    demonstrateSearch();
    demonstrateWhileLoops();
    demonstrateNestedLoops();
    demonstrateLabeledBreak();
    demonstrateFiltering();
    demonstrateValidation();
    demonstrateTransactions();
    demonstrateClasses();
    demonstrateGenerators();
    await analyzeSensorStream();
    demonstratePerformance();
    demonstrateSafeWhile();
    demonstrateLogAnalysis();
    demonstrateNoOpDesign();
    runTests();

    section("20. End");
    console.log("All JavaScript demonstrations completed.");
}

main().catch((error) => {
    console.error("Program failed:", error);
    process.exitCode = 1;
});
