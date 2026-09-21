/*
 * Practice: Conditions and Loops
 * ==============================
 *
 * A standalone JavaScript study file covering conditions and loops from
 * beginner concepts through more advanced control-flow patterns.
 *
 * Run with:
 *   node conditions-and-loops.js
 *
 * Topics:
 * - Boolean values and comparisons
 * - if, else if, else
 * - logical operators
 * - truthy and falsy values
 * - strict equality
 * - ternary expressions
 * - switch
 * - for, while, do...while
 * - for...of and for...in
 * - break and continue
 * - nested loops
 * - array processing
 * - object processing
 * - validation
 * - searching and filtering
 * - Map and Set
 * - generators
 * - iterators
 * - asynchronous loops
 * - performance
 * - edge cases
 */

// ---------------------------------------------------------------------------
// Utility functions
// ---------------------------------------------------------------------------

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function subsection(title) {
    console.log(`\n--- ${title} ---`);
}

function demonstrate(label, value) {
    console.log(`${label}:`, value);
}

// ---------------------------------------------------------------------------
// 1. Boolean basics
// ---------------------------------------------------------------------------

function booleanBasics() {
    section("1. Boolean values and expressions");

    const isJavaScript = true;
    const isFinished = false;

    demonstrate("isJavaScript", isJavaScript);
    demonstrate("isFinished", isFinished);
    demonstrate("true && false", true && false);
    demonstrate("true || false", true || false);
    demonstrate("!true", !true);

    const age = 25;

    demonstrate("age >= 18", age >= 18);
    demonstrate("age === 25", age === 25);
    demonstrate("age !== 30", age !== 30);
    demonstrate("age < 18", age < 18);
}

// ---------------------------------------------------------------------------
// 2. Comparison operators
// ---------------------------------------------------------------------------

function comparisonExamples() {
    section("2. Comparison operators");

    const first = 10;
    const second = 20;

    const comparisons = {
        "10 === 20": first === second,
        "10 !== 20": first !== second,
        "10 < 20": first < second,
        "10 <= 20": first <= second,
        "10 > 20": first > second,
        "10 >= 20": first >= second
    };

    for (const [expression, result] of Object.entries(comparisons)) {
        console.log(`${expression.padEnd(12)} -> ${result}`);
    }

    // JavaScript's strict equality avoids implicit type conversion.
    demonstrate('5 === "5"', 5 === "5");
    demonstrate('5 == "5"', 5 == "5");
}

// ---------------------------------------------------------------------------
// 3. Logical operators
// ---------------------------------------------------------------------------

function logicalOperators() {
    section("3. Logical operators");

    const age = 30;
    const hasId = true;
    const isStudent = false;

    const canEnter = age >= 18 && hasId;
    const getsDiscount = isStudent || age >= 60;
    const needsId = !hasId;

    demonstrate("canEnter", canEnter);
    demonstrate("getsDiscount", getsDiscount);
    demonstrate("needsId", needsId);

    // && and || short-circuit. The second expression is evaluated only when
    // necessary to determine the final result.
    let user = null;

    if (user && user.name) {
        console.log(user.name);
    } else {
        console.log("Short-circuit prevented access to a property on null.");
    }
}

// ---------------------------------------------------------------------------
// 4. if / else if / else
// ---------------------------------------------------------------------------

function gradeClassifier(score) {
    if (!Number.isFinite(score) || score < 0 || score > 100) {
        return "Invalid score";
    }

    if (score >= 90) {
        return "A";
    } else if (score >= 80) {
        return "B";
    } else if (score >= 70) {
        return "C";
    } else if (score >= 60) {
        return "D";
    }

    return "F";
}

function conditionalStatements() {
    section("4. if, else if, and else");

    const scores = [95, 84, 72, 61, 43, -5, 101];

    for (const score of scores) {
        console.log(`Score ${String(score).padStart(3)}: ${gradeClassifier(score)}`);
    }

    const visitorAge = 22;
    const hasTicket = true;

    if (visitorAge >= 18) {
        if (hasTicket) {
            console.log("Nested condition: admission permitted.");
        } else {
            console.log("Nested condition: ticket required.");
        }
    } else {
        console.log("Nested condition: visitor is under the required age.");
    }
}

// ---------------------------------------------------------------------------
// 5. Truthy and falsy values
// ---------------------------------------------------------------------------

function truthinessExamples() {
    section("5. Truthy and falsy values");

    const values = [
        false,
        0,
        -0,
        0n,
        "",
        null,
        undefined,
        NaN,
        [],
        {},
        "0",
        -1,
        "JavaScript"
    ];

    for (const value of values) {
        console.log(`${String(value).padEnd(15)} -> ${Boolean(value)}`);
    }

    const names = [];

    if (names.length === 0) {
        console.log("The array is empty.");
    }

    // Important JavaScript peculiarity:
    // [] and {} are truthy even though they contain no elements/properties.
    if ([]) {
        console.log("An empty array is truthy in JavaScript.");
    }

    if ({}) {
        console.log("An empty object is truthy in JavaScript.");
    }
}

// ---------------------------------------------------------------------------
// 6. Ternary expressions
// ---------------------------------------------------------------------------

function ternaryExamples() {
    section("6. Conditional / ternary expressions");

    const age = 20;
    const status = age >= 18 ? "adult" : "minor";

    demonstrate("status", status);

    const number = 7;
    const parity = number % 2 === 0 ? "even" : "odd";

    demonstrate("parity", parity);

    // Ternaries are useful for small decisions. Deeply nested ternaries
    // generally reduce readability.
}

// ---------------------------------------------------------------------------
// 7. switch
// ---------------------------------------------------------------------------

function switchExamples() {
    section("7. switch statements");

    const operation = "multiply";
    const first = 8;
    const second = 4;
    let result;

    switch (operation) {
        case "add":
            result = first + second;
            break;
        case "subtract":
            result = first - second;
            break;
        case "multiply":
            result = first * second;
            break;
        case "divide":
            if (second === 0) {
                throw new Error("Division by zero is not allowed.");
            }
            result = first / second;
            break;
        default:
            throw new Error(`Unknown operation: ${operation}`);
    }

    console.log(`${operation}: ${result}`);
}

// ---------------------------------------------------------------------------
// 8. Validation
// ---------------------------------------------------------------------------

function validateInteger(value, minimum, maximum) {
    const number = Number(value);

    if (!Number.isInteger(number)) {
        throw new TypeError("Input must be an integer.");
    }

    if (number < minimum || number > maximum) {
        throw new RangeError(
            `Input must be between ${minimum} and ${maximum}.`
        );
    }

    return number;
}

function validationExamples() {
    section("8. Validation and error handling");

    const inputs = ["42", "abc", "101", "-4", "75"];

    for (const rawValue of inputs) {
        try {
            const value = validateInteger(rawValue, 0, 100);
            console.log(`${JSON.stringify(rawValue)} -> accepted as ${value}`);
        } catch (error) {
            console.log(`${JSON.stringify(rawValue)} -> rejected: ${error.message}`);
        }
    }
}

// ---------------------------------------------------------------------------
// 9. for loops
// ---------------------------------------------------------------------------

function basicForLoops() {
    section("9. for loops");

    const languages = ["Python", "JavaScript", "C++"];

    for (let index = 0; index < languages.length; index++) {
        console.log(`Learning ${languages[index]}`);
    }

    for (let number = 1; number <= 5; number++) {
        process.stdout.write(`${number} `);
    }
    console.log();

    for (let number = 10; number > 0; number -= 2) {
        process.stdout.write(`${number} `);
    }
    console.log();
}

// ---------------------------------------------------------------------------
// 10. for...of
// ---------------------------------------------------------------------------

function forOfExamples() {
    section("10. for...of");

    const subjects = ["conditions", "loops", "functions", "objects"];

    for (const subject of subjects) {
        console.log(subject);
    }

    // for...of works with iterable values such as arrays, strings, Sets,
    // Maps, and generators.
    for (const character of "LOOP") {
        process.stdout.write(`${character} `);
    }
    console.log();
}

// ---------------------------------------------------------------------------
// 11. for...in
// ---------------------------------------------------------------------------

function forInExamples() {
    section("11. for...in");

    const inventory = {
        laptop: 8,
        keyboard: 15,
        mouse: 22
    };

    // for...in enumerates property keys.
    for (const product in inventory) {
        if (Object.hasOwn(inventory, product)) {
            console.log(`${product}: ${inventory[product]}`);
        }
    }

    // Object.entries() is often clearer when both key and value are needed.
    for (const [product, quantity] of Object.entries(inventory)) {
        console.log(`${product} -> ${quantity}`);
    }
}

// ---------------------------------------------------------------------------
// 12. while
// ---------------------------------------------------------------------------

function whileExamples() {
    section("12. while loops");

    let counter = 1;

    while (counter <= 5) {
        console.log(`Counter = ${counter}`);
        counter++;
    }

    // The state-changing operation is essential. Without counter++ this
    // loop would never reach its stopping condition.
}

// ---------------------------------------------------------------------------
// 13. do...while
// ---------------------------------------------------------------------------

function doWhileExamples() {
    section("13. do...while loops");

    let counter = 0;

    do {
        console.log(`Executed with counter = ${counter}`);
        counter++;
    } while (counter < 3);

    // A do...while always executes its body at least once.
}

// ---------------------------------------------------------------------------
// 14. break
// ---------------------------------------------------------------------------

function breakExamples() {
    section("14. break");

    const numbers = [4, 7, 11, 15, 21];
    const target = 15;

    for (const number of numbers) {
        console.log(`Checking ${number}`);

        if (number === target) {
            console.log("Target found; stopping early.");
            break;
        }
    }
}

// ---------------------------------------------------------------------------
// 15. continue
// ---------------------------------------------------------------------------

function continueExamples() {
    section("15. continue");

    for (let number = 1; number <= 10; number++) {
        if (number % 2 === 0) {
            continue;
        }

        process.stdout.write(`${number} `);
    }

    console.log();
}

// ---------------------------------------------------------------------------
// 16. Nested loops
// ---------------------------------------------------------------------------

function nestedLoops() {
    section("16. Nested loops");

    for (let row = 1; row <= 3; row++) {
        const values = [];

        for (let column = 1; column <= 4; column++) {
            values.push(row * column);
        }

        console.log(values);
    }

    // If the outer loop runs n times and the inner loop runs m times,
    // the body executes n * m times.
}

// ---------------------------------------------------------------------------
// 17. Pattern generation
// ---------------------------------------------------------------------------

function patternGeneration() {
    section("17. Pattern generation");

    for (let row = 1; row <= 5; row++) {
        console.log("*".repeat(row));
    }

    console.log();

    for (let row = 5; row >= 1; row--) {
        console.log("*".repeat(row));
    }
}

// ---------------------------------------------------------------------------
// 18. Array filtering and aggregation
// ---------------------------------------------------------------------------

function filteringAndAggregation() {
    section("18. Filtering and aggregation");

    const transactions = [1200, -300, 450, -150, 800, -50];

    let income = 0;
    let expenses = 0;

    for (const amount of transactions) {
        if (amount >= 0) {
            income += amount;
        } else {
            expenses += Math.abs(amount);
        }
    }

    console.log("Income:", income);
    console.log("Expenses:", expenses);
    console.log("Balance:", income - expenses);

    const positiveTransactions = transactions.filter(
        amount => amount > 0
    );

    console.log("Positive transactions:", positiveTransactions);
}

// ---------------------------------------------------------------------------
// 19. Searching
// ---------------------------------------------------------------------------

function linearSearch(items, target) {
    for (let index = 0; index < items.length; index++) {
        if (items[index] === target) {
            return index;
        }
    }

    return -1;
}

function searchExamples() {
    section("19. Linear search");

    const values = [12, 4, 19, 7, 31, 9];

    for (const target of [19, 100]) {
        console.log(`Target ${target}: index=${linearSearch(values, target)}`);
    }
}

// ---------------------------------------------------------------------------
// 20. Optimized pair search using Set
// ---------------------------------------------------------------------------

function findPairWithSum(numbers, target) {
    const seen = new Set();

    for (const number of numbers) {
        const required = target - number;

        if (seen.has(required)) {
            return [required, number];
        }

        seen.add(number);
    }

    return null;
}

function optimizedSearchExample() {
    section("20. Trading space for speed");

    const numbers = [3, 8, 12, 17, 21];

    console.log("Pair:", findPairWithSum(numbers, 29));
    console.log("Missing pair:", findPairWithSum(numbers, 100));
}

// ---------------------------------------------------------------------------
// 21. Map frequency counting
// ---------------------------------------------------------------------------

function frequencyCount(text) {
    const frequencies = new Map();

    for (const character of text.toLowerCase()) {
        if (!/[a-z]/.test(character)) {
            continue;
        }

        frequencies.set(
            character,
            (frequencies.get(character) ?? 0) + 1
        );
    }

    return frequencies;
}

function frequencyExample() {
    section("21. Frequency counting with Map");

    const frequencies = frequencyCount("Conditions and loops");

    console.log(Object.fromEntries(frequencies));
}

// ---------------------------------------------------------------------------
// 22. Matrix traversal
// ---------------------------------------------------------------------------

function matrixExample() {
    section("22. Matrix traversal");

    const matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ];

    let total = 0;

    for (const row of matrix) {
        for (const value of row) {
            total += value;
        }
    }

    console.log("Matrix:");

    for (const row of matrix) {
        console.log(row);
    }

    console.log("Total:", total);
}

// ---------------------------------------------------------------------------
// 23. Prime numbers
// ---------------------------------------------------------------------------

function isPrime(number) {
    if (!Number.isInteger(number) || number < 2) {
        return false;
    }

    if (number === 2) {
        return true;
    }

    if (number % 2 === 0) {
        return false;
    }

    const limit = Math.floor(Math.sqrt(number));

    for (let divisor = 3; divisor <= limit; divisor += 2) {
        if (number % divisor === 0) {
            return false;
        }
    }

    return true;
}

function primeExample() {
    section("23. Prime number detection");

    const primes = [];

    for (let number = 1; number <= 50; number++) {
        if (isPrime(number)) {
            primes.push(number);
        }
    }

    console.log(primes);
}

// ---------------------------------------------------------------------------
// 24. Fibonacci
// ---------------------------------------------------------------------------

function fibonacci(count) {
    if (!Number.isInteger(count) || count < 0) {
        throw new RangeError("count must be a non-negative integer.");
    }

    const result = [];
    let first = 0;
    let second = 1;

    for (let index = 0; index < count; index++) {
        result.push(first);
        [first, second] = [second, first + second];
    }

    return result;
}

function fibonacciExample() {
    section("24. Fibonacci sequence");

    console.log(fibonacci(15));
}

// ---------------------------------------------------------------------------
// 25. Generator functions
// ---------------------------------------------------------------------------

function* fibonacciGenerator(count) {
    if (!Number.isInteger(count) || count < 0) {
        throw new RangeError("count must be a non-negative integer.");
    }

    let first = 0;
    let second = 1;

    for (let index = 0; index < count; index++) {
        yield first;
        [first, second] = [second, first + second];
    }
}

function generatorExample() {
    section("25. Generator functions");

    for (const value of fibonacciGenerator(10)) {
        process.stdout.write(`${value} `);
    }

    console.log();
}

// ---------------------------------------------------------------------------
// 26. Custom iterator
// ---------------------------------------------------------------------------

class Countdown {
    constructor(start) {
        if (!Number.isInteger(start) || start < 0) {
            throw new RangeError("start must be a non-negative integer.");
        }

        this.start = start;
    }

    *[Symbol.iterator]() {
        for (let current = this.start; current > 0; current--) {
            yield current;
        }
    }
}

function iteratorExample() {
    section("26. Custom iterable");

    for (const value of new Countdown(5)) {
        process.stdout.write(`${value} `);
    }

    console.log();
}

// ---------------------------------------------------------------------------
// 27. Sentinel-controlled processing
// ---------------------------------------------------------------------------

function processUntilSentinel(values, sentinel = -1) {
    let total = 0;

    for (const value of values) {
        if (value === sentinel) {
            break;
        }

        if (value < 0) {
            continue;
        }

        total += value;
    }

    return total;
}

function sentinelExample() {
    section("27. Sentinel-controlled loop");

    const values = [10, 20, -5, 30, 40, -1, 999];

    console.log("Input:", values);
    console.log("Total before sentinel:", processUntilSentinel(values));
}

// ---------------------------------------------------------------------------
// 28. Retry logic
// ---------------------------------------------------------------------------

function retryOperation(attempts, outcomes) {
    if (!Number.isInteger(attempts) || attempts <= 0) {
        throw new RangeError("attempts must be positive.");
    }

    for (let attempt = 1; attempt <= attempts; attempt++) {
        const success = outcomes[attempt - 1] ?? false;

        console.log(
            `Attempt ${attempt}: ${success ? "success" : "failure"}`
        );

        if (success) {
            return true;
        }
    }

    return false;
}

function retryExample() {
    section("28. Retry logic");

    console.log("Result:", retryOperation(4, [false, false, true]));
    console.log("Result:", retryOperation(3, [false, false, false]));
}

// ---------------------------------------------------------------------------
// 29. Business rule engine
// ---------------------------------------------------------------------------

function calculateShipping(weightKg, distanceKm, isMember, fragile) {
    if (!Number.isFinite(weightKg) || weightKg <= 0) {
        throw new RangeError("Weight must be positive.");
    }

    if (!Number.isFinite(distanceKm) || distanceKm < 0) {
        throw new RangeError("Distance cannot be negative.");
    }

    let cost = 50 + weightKg * 20 + distanceKm * 0.5;

    if (fragile) {
        cost += 100;
    }

    if (isMember) {
        cost *= 0.90;
    }

    if (weightKg > 20) {
        cost += 200;
    }

    return Math.round(cost * 100) / 100;
}

function businessRulesExample() {
    section("29. Multiple business rules");

    const orders = [
        { weight: 2, distance: 10, member: false, fragile: false },
        { weight: 5, distance: 100, member: true, fragile: true },
        { weight: 25, distance: 50, member: true, fragile: false }
    ];

    for (const order of orders) {
        const cost = calculateShipping(
            order.weight,
            order.distance,
            order.member,
            order.fragile
        );

        console.log(order, "-> shipping =", cost);
    }
}

// ---------------------------------------------------------------------------
// 30. Asynchronous loops
// ---------------------------------------------------------------------------

function delay(milliseconds) {
    return new Promise(resolve => setTimeout(resolve, milliseconds));
}

async function asynchronousLoopExample() {
    section("30. Asynchronous loops");

    // Awaiting inside a for...of loop processes items sequentially.
    // This is appropriate when later work depends on earlier work or when
    // the external service requires controlled request pacing.
    const tasks = ["load", "validate", "process"];

    for (const task of tasks) {
        await delay(5);
        console.log(`Completed: ${task}`);
    }

    // Promise.all starts independent operations together. It is not merely
    // another loop syntax; it changes concurrency behavior.
    const independentTasks = ["A", "B", "C"];

    await Promise.all(
        independentTasks.map(async task => {
            await delay(5);
            console.log(`Independent task completed: ${task}`);
        })
    );
}

// ---------------------------------------------------------------------------
// 31. Performance comparison
// ---------------------------------------------------------------------------

function performanceExample() {
    section("31. Performance considerations");

    const size = 100000;
    const values = Array.from({ length: size }, (_, index) => index);

    let start = process.hrtime.bigint();
    let loopTotal = 0;

    for (const value of values) {
        loopTotal += value;
    }

    const loopDuration = Number(process.hrtime.bigint() - start) / 1e6;

    start = process.hrtime.bigint();
    const reduceTotal = values.reduce((sum, value) => sum + value, 0);
    const reduceDuration = Number(process.hrtime.bigint() - start) / 1e6;

    console.log("Loop total:", loopTotal);
    console.log("reduce total:", reduceTotal);
    console.log(`for...of time: ${loopDuration.toFixed(3)} ms`);
    console.log(`reduce time:   ${reduceDuration.toFixed(3)} ms`);

    // Timing varies between machines and runtime versions. Benchmarking is
    // useful for large workloads, but readability and algorithmic complexity
    // normally matter more than tiny timing differences.
}

// ---------------------------------------------------------------------------
// 32. Practical transaction classifier
// ---------------------------------------------------------------------------

function classifyTransaction(
    amount,
    countryMatches,
    knownDevice,
    transactionCountLastHour
) {
    if (!Number.isFinite(amount) || amount <= 0) {
        return "invalid";
    }

    if (
        !Number.isInteger(transactionCountLastHour) ||
        transactionCountLastHour < 0
    ) {
        return "invalid";
    }

    if (amount >= 100000) {
        return "manual_review";
    }

    if (!countryMatches && !knownDevice) {
        return "high_risk";
    }

    if (transactionCountLastHour > 20) {
        return "high_risk";
    }

    if (!countryMatches || !knownDevice) {
        return "review";
    }

    return "normal";
}

function transactionExample() {
    section("32. Practical rule-based classification");

    const transactions = [
        [2500, true, true, 2],
        [15000, false, true, 4],
        [300000, true, true, 1],
        [5000, false, false, 2],
        [1000, true, true, 25]
    ];

    for (const transaction of transactions) {
        console.log(
            transaction,
            "->",
            classifyTransaction(...transaction)
        );
    }
}

// ---------------------------------------------------------------------------
// 33. Main
// ---------------------------------------------------------------------------

async function main() {
    booleanBasics();
    comparisonExamples();
    logicalOperators();
    conditionalStatements();
    truthinessExamples();
    ternaryExamples();
    switchExamples();
    validationExamples();
    basicForLoops();
    forOfExamples();
    forInExamples();
    whileExamples();
    doWhileExamples();
    breakExamples();
    continueExamples();
    nestedLoops();
    patternGeneration();
    filteringAndAggregation();
    searchExamples();
    optimizedSearchExample();
    frequencyExample();
    matrixExample();
    primeExample();
    fibonacciExample();
    generatorExample();
    iteratorExample();
    sentinelExample();
    retryExample();
    businessRulesExample();
    await asynchronousLoopExample();
    performanceExample();
    transactionExample();

    section("Study checklist");

    const checklist = [
        "Can you write if, else if, and else conditions?",
        "Can you combine conditions with &&, ||, and !?",
        "Can you explain === versus ==?",
        "Can you explain JavaScript truthy and falsy values?",
        "Can you choose between if and a ternary expression?",
        "Can you explain when switch is useful?",
        "Can you use for, while, and do...while correctly?",
        "Can you explain for...of versus for...in?",
        "Can you use break and continue deliberately?",
        "Can you avoid off-by-one errors?",
        "Can you analyze nested-loop complexity?",
        "Can you use Set or Map for efficient data processing?",
        "Can you use generators for lazy iteration?",
        "Can you distinguish sequential async loops from concurrent Promise.all?",
        "Can you prevent accidental infinite loops?"
    ];

    for (const item of checklist) {
        console.log(`[ ] ${item}`);
    }
}

main().catch(error => {
    console.error("Program failed:", error);
    process.exitCode = 1;
});
