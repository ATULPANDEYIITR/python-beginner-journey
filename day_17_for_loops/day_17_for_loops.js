/*
 * for-loops.js
 *
 * A comprehensive executable study file for JavaScript `for` loops.
 *
 * Run in Node.js:
 *     node for-loops.js
 *
 * The examples progress from basic syntax to iterators, generators,
 * asynchronous iteration, data processing, algorithms, validation,
 * performance, and production-oriented patterns.
 */

"use strict";

// -----------------------------------------------------------------------------
// Utility functions
// -----------------------------------------------------------------------------

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function subsection(title) {
    console.log(`\n--- ${title} ---`);
}

// -----------------------------------------------------------------------------
// 1. Basic for loop
// -----------------------------------------------------------------------------

function basicForLoop() {
    section("1. Basic for loops");

    // A traditional for loop has three parts:
    // initialization; condition; update.
    for (let number = 0; number < 5; number++) {
        console.log(number);
    }

    // The update expression can change by more than one.
    for (let number = 10; number >= 0; number -= 2) {
        console.log(number);
    }
}

// -----------------------------------------------------------------------------
// 2. Iterating arrays
// -----------------------------------------------------------------------------

function arrayIteration() {
    section("2. Array iteration");

    const languages = ["Python", "JavaScript", "C++"];

    for (let index = 0; index < languages.length; index++) {
        console.log(index, languages[index]);
    }

    // for...of is designed to iterate values from an iterable.
    for (const language of languages) {
        console.log(language);
    }

    // Array entries provide index-value pairs.
    for (const [index, language] of languages.entries()) {
        console.log(index, language);
    }
}

// -----------------------------------------------------------------------------
// 3. Strings
// -----------------------------------------------------------------------------

function stringIteration() {
    section("3. String iteration");

    const word = "JavaScript";

    for (let index = 0; index < word.length; index++) {
        console.log(index, word[index]);
    }

    // for...of handles Unicode code points more appropriately than indexing
    // for many Unicode characters.
    for (const character of "café") {
        console.log(character);
    }
}

// -----------------------------------------------------------------------------
// 4. Object properties
// -----------------------------------------------------------------------------

function objectIteration() {
    section("4. Object property iteration");

    const profile = {
        name: "Atul",
        role: "Developer",
        experience: 3
    };

    // Object.keys() creates an array of own enumerable property names.
    for (const key of Object.keys(profile)) {
        console.log(key, profile[key]);
    }

    // Object.entries() directly supplies [key, value].
    for (const [key, value] of Object.entries(profile)) {
        console.log(key, "=>", value);
    }
}

// -----------------------------------------------------------------------------
// 5. range-like iteration
// -----------------------------------------------------------------------------

function range(start, stop, step = 1) {
    if (step === 0) {
        throw new RangeError("step cannot be zero");
    }

    const values = [];

    if (step > 0) {
        for (let value = start; value < stop; value += step) {
            values.push(value);
        }
    } else {
        for (let value = start; value > stop; value += step) {
            values.push(value);
        }
    }

    return values;
}

function rangeExamples() {
    section("5. Building a range abstraction");

    console.log(range(0, 5));
    console.log(range(2, 10, 2));
    console.log(range(10, 0, -2));

    try {
        console.log(range(1, 5, 0));
    } catch (error) {
        console.log("expected error:", error.message);
    }
}

// -----------------------------------------------------------------------------
// 6. break
// -----------------------------------------------------------------------------

function breakExample() {
    section("6. break");

    for (let number = 1; number <= 10; number++) {
        if (number === 6) {
            break;
        }
        console.log(number);
    }

    const values = [5, 17, 23, 42, 81];
    const target = 42;
    let foundIndex = -1;

    for (let index = 0; index < values.length; index++) {
        if (values[index] === target) {
            foundIndex = index;
            break;
        }
    }

    console.log("found index:", foundIndex);
}

// -----------------------------------------------------------------------------
// 7. continue
// -----------------------------------------------------------------------------

function continueExample() {
    section("7. continue");

    for (let number = 1; number <= 10; number++) {
        if (number % 2 === 0) {
            continue;
        }

        console.log(number);
    }
}

// -----------------------------------------------------------------------------
// 8. Nested loops
// -----------------------------------------------------------------------------

function nestedLoops() {
    section("8. Nested loops");

    for (let row = 0; row < 3; row++) {
        let line = "";

        for (let column = 0; column < 4; column++) {
            line += `(${row},${column}) `;
        }

        console.log(line);
    }

    subsection("Multiplication table");

    for (let number = 1; number <= 5; number++) {
        const row = [];

        for (let multiplier = 1; multiplier <= 5; multiplier++) {
            row.push(number * multiplier);
        }

        console.log(row.join(" "));
    }
}

// -----------------------------------------------------------------------------
// 9. Searching
// -----------------------------------------------------------------------------

function linearSearch(values, target) {
    for (let index = 0; index < values.length; index++) {
        if (values[index] === target) {
            return index;
        }
    }

    return -1;
}

function binarySearch(values, target) {
    let left = 0;
    let right = values.length - 1;

    while (left <= right) {
        const middle = Math.floor((left + right) / 2);

        if (values[middle] === target) {
            return middle;
        }

        if (values[middle] < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}

function searchExamples() {
    section("9. Search algorithms");

    const values = [4, 8, 15, 16, 23, 42];

    console.log("linear:", linearSearch(values, 23));
    console.log("binary:", binarySearch(values, 23));
    console.log("missing:", binarySearch(values, 99));
}

// -----------------------------------------------------------------------------
// 10. Frequency counting
// -----------------------------------------------------------------------------

function frequencyExample() {
    section("10. Frequency counting");

    const values = [1, 2, 2, 3, 3, 3, 4];
    const frequency = new Map();

    for (const value of values) {
        frequency.set(value, (frequency.get(value) ?? 0) + 1);
    }

    console.log([...frequency.entries()]);
}

// -----------------------------------------------------------------------------
// 11. Accumulators
// -----------------------------------------------------------------------------

function accumulatorExample() {
    section("11. Accumulators");

    const values = [4, 8, 15, 16, 23, 42];

    let total = 0;

    for (const value of values) {
        total += value;
    }

    console.log("sum:", total);

    let maximum = values[0];

    for (const value of values.slice(1)) {
        if (value > maximum) {
            maximum = value;
        }
    }

    console.log("maximum:", maximum);
}

// -----------------------------------------------------------------------------
// 12. Array transformations
// -----------------------------------------------------------------------------

function transformationExample() {
    section("12. Transforming arrays");

    const values = [1, 2, 3, 4, 5];

    const squares = [];

    for (const value of values) {
        squares.push(value * value);
    }

    console.log("squares:", squares);

    const evenSquares = [];

    for (const value of values) {
        if (value % 2 === 0) {
            evenSquares.push(value * value);
        }
    }

    console.log("even squares:", evenSquares);
}

// -----------------------------------------------------------------------------
// 13. forEach comparison
// -----------------------------------------------------------------------------

function forEachComparison() {
    section("13. for versus forEach");

    const values = [10, 20, 30];

    // for gives direct control over index, break, continue, and update logic.
    for (let index = 0; index < values.length; index++) {
        console.log("for:", values[index]);
    }

    // forEach is useful for simple processing of every element, but break and
    // continue cannot be used to control the surrounding forEach callback.
    values.forEach((value, index) => {
        console.log("forEach:", index, value);
    });
}

// -----------------------------------------------------------------------------
// 14. Iterator protocol
// -----------------------------------------------------------------------------

function iteratorExample() {
    section("14. JavaScript iterator protocol");

    const values = [10, 20, 30];
    const iterator = values[Symbol.iterator]();

    console.log(iterator.next());
    console.log(iterator.next());
    console.log(iterator.next());
    console.log(iterator.next());

    // An iterator returns objects shaped like { value, done }.
}

// -----------------------------------------------------------------------------
// 15. Custom iterable
// -----------------------------------------------------------------------------

class Countdown {
    constructor(start) {
        if (!Number.isInteger(start) || start < 0) {
            throw new RangeError("start must be a non-negative integer");
        }

        this.start = start;
    }

    // Symbol.iterator makes an object compatible with for...of.
    *[Symbol.iterator]() {
        for (let current = this.start; current >= 0; current--) {
            yield current;
        }
    }
}

function customIterableExample() {
    section("15. Custom iterable");

    for (const value of new Countdown(5)) {
        console.log(value);
    }
}

// -----------------------------------------------------------------------------
// 16. Generator functions
// -----------------------------------------------------------------------------

function* fibonacciGenerator(limit) {
    if (!Number.isInteger(limit) || limit < 0) {
        throw new RangeError("limit must be a non-negative integer");
    }

    let first = 0;
    let second = 1;

    for (let count = 0; count < limit; count++) {
        yield first;
        [first, second] = [second, first + second];
    }
}

function generatorExample() {
    section("16. Generator functions");

    for (const number of fibonacciGenerator(10)) {
        console.log(number);
    }

    // A generator is lazy: values are produced when requested.
    const generator = fibonacciGenerator(1_000_000);

    console.log("first:", generator.next().value);
    console.log("second:", generator.next().value);
}

// -----------------------------------------------------------------------------
// 17. Generator pipeline
// -----------------------------------------------------------------------------

function* filterIterable(iterable, predicate) {
    for (const value of iterable) {
        if (predicate(value)) {
            yield value;
        }
    }
}

function* mapIterable(iterable, transformer) {
    for (const value of iterable) {
        yield transformer(value);
    }
}

function pipelineExample() {
    section("17. Lazy iterator pipeline");

    const source = range(1, 21);
    const evens = filterIterable(source, value => value % 2 === 0);
    const squares = mapIterable(evens, value => value * value);

    for (const value of squares) {
        console.log(value);
    }
}

// -----------------------------------------------------------------------------
// 18. Chunking
// -----------------------------------------------------------------------------

function* chunked(values, chunkSize) {
    if (!Number.isInteger(chunkSize) || chunkSize <= 0) {
        throw new RangeError("chunkSize must be a positive integer");
    }

    for (let start = 0; start < values.length; start += chunkSize) {
        yield values.slice(start, start + chunkSize);
    }
}

function chunkExample() {
    section("18. Batch processing");

    const records = range(1, 11);

    for (const batch of chunked(records, 3)) {
        console.log("processing:", batch);
    }
}

// -----------------------------------------------------------------------------
// 19. Matrix processing
// -----------------------------------------------------------------------------

function transpose(matrix) {
    if (matrix.length === 0) {
        return [];
    }

    const columnCount = matrix[0].length;

    for (const row of matrix) {
        if (row.length !== columnCount) {
            throw new Error("matrix must be rectangular");
        }
    }

    const result = [];

    for (let column = 0; column < columnCount; column++) {
        const newRow = [];

        for (let row = 0; row < matrix.length; row++) {
            newRow.push(matrix[row][column]);
        }

        result.push(newRow);
    }

    return result;
}

function matrixExample() {
    section("19. Matrix processing");

    const matrix = [
        [1, 2, 3],
        [4, 5, 6]
    ];

    console.log("transpose:", transpose(matrix));
}

// -----------------------------------------------------------------------------
// 20. Graph traversal
// -----------------------------------------------------------------------------

function breadthFirstSearch(graph, start) {
    if (!(start in graph)) {
        throw new Error(`unknown start node: ${start}`);
    }

    const queue = [start];
    const visited = new Set([start]);
    const traversal = [];

    for (let position = 0; position < queue.length; position++) {
        const current = queue[position];
        traversal.push(current);

        for (const neighbor of graph[current] ?? []) {
            if (!visited.has(neighbor)) {
                visited.add(neighbor);
                queue.push(neighbor);
            }
        }
    }

    return traversal;
}

function graphExample() {
    section("20. Graph traversal");

    const graph = {
        A: ["B", "C"],
        B: ["D"],
        C: ["E"],
        D: [],
        E: []
    };

    console.log(breadthFirstSearch(graph, "A"));
}

// -----------------------------------------------------------------------------
// 21. Validation
// -----------------------------------------------------------------------------

function validateUsers(records) {
    const validUsers = [];

    for (let index = 0; index < records.length; index++) {
        const record = records[index];

        if (record === null || typeof record !== "object") {
            throw new TypeError(`record ${index + 1} must be an object`);
        }

        if (!Number.isInteger(record.userId) || record.userId <= 0) {
            throw new Error(`record ${index + 1}: invalid userId`);
        }

        if (
            typeof record.email !== "string" ||
            !record.email.includes("@")
        ) {
            throw new Error(`record ${index + 1}: invalid email`);
        }

        if (typeof record.active !== "boolean") {
            throw new Error(`record ${index + 1}: invalid active flag`);
        }

        validUsers.push({
            userId: record.userId,
            email: record.email,
            active: record.active
        });
    }

    return validUsers;
}

function validationExample() {
    section("21. Validation");

    const records = [
        { userId: 1, email: "alice@example.com", active: true },
        { userId: 2, email: "bob@example.com", active: false }
    ];

    console.log(validateUsers(records));
}

// -----------------------------------------------------------------------------
// 22. Transaction processing
// -----------------------------------------------------------------------------

function processTransactions(transactions) {
    let successfulTotal = 0;
    let successfulCount = 0;
    let failedCount = 0;

    for (const transaction of transactions) {
        if (
            typeof transaction.amount !== "number" ||
            !Number.isFinite(transaction.amount) ||
            transaction.amount < 0
        ) {
            throw new Error(
                `invalid amount for ${transaction.transactionId}`
            );
        }

        if (transaction.status === "success") {
            successfulTotal += transaction.amount;
            successfulCount++;
        } else if (transaction.status === "failed") {
            failedCount++;
        } else {
            throw new Error(
                `unknown status for ${transaction.transactionId}`
            );
        }
    }

    return {
        successfulTotal,
        successfulCount,
        failedCount
    };
}

function transactionExample() {
    section("22. Transaction processing");

    const transactions = [
        { transactionId: "TX001", amount: 1200, status: "success" },
        { transactionId: "TX002", amount: 500, status: "failed" },
        { transactionId: "TX003", amount: 850, status: "success" }
    ];

    console.log(processTransactions(transactions));
}

// -----------------------------------------------------------------------------
// 23. Sorting with loops
// -----------------------------------------------------------------------------

function bubbleSort(values) {
    const result = [...values];

    for (let outer = 0; outer < result.length; outer++) {
        let swapped = false;

        for (
            let inner = 0;
            inner < result.length - outer - 1;
            inner++
        ) {
            if (result[inner] > result[inner + 1]) {
                [result[inner], result[inner + 1]] = [
                    result[inner + 1],
                    result[inner]
                ];

                swapped = true;
            }
        }

        if (!swapped) {
            break;
        }
    }

    return result;
}

function sortingExample() {
    section("23. Bubble sort");

    const values = [64, 34, 25, 12, 22, 11, 90];

    console.log("original:", values);
    console.log("sorted:", bubbleSort(values));
}

// -----------------------------------------------------------------------------
// 24. Loop complexity
// -----------------------------------------------------------------------------

function complexityExample() {
    section("24. Loop complexity");

    const values = range(0, 10);

    let operations = 0;

    // O(n)
    for (const value of values) {
        operations += value >= 0 ? 1 : 0;
    }

    console.log("single loop:", operations);

    operations = 0;

    // O(n^2)
    for (const first of values) {
        for (const second of values) {
            operations += first + second >= 0 ? 1 : 0;
        }
    }

    console.log("nested loops:", operations);
}

// -----------------------------------------------------------------------------
// 25. Performance measurement
// -----------------------------------------------------------------------------

function performanceExample() {
    section("25. Performance measurement");

    const values = range(0, 100_000);

    let total = 0;
    const start = performance.now();

    for (const value of values) {
        total += value;
    }

    const elapsed = performance.now() - start;

    console.log("result:", total);
    console.log(`for...of time: ${elapsed.toFixed(4)} ms`);

    // Benchmark results depend on runtime, machine, warm-up, and workload.
    // Use measurements from representative workloads before optimizing.
}

// -----------------------------------------------------------------------------
// 26. Error handling
// -----------------------------------------------------------------------------

function errorHandlingExample() {
    section("26. Error handling inside loops");

    const numerators = [10, 20, 30];
    const denominators = [2, 0, 5];

    for (let index = 0; index < numerators.length; index++) {
        try {
            if (denominators[index] === 0) {
                throw new RangeError("division by zero");
            }

            console.log(
                numerators[index] / denominators[index]
            );
        } catch (error) {
            console.log(
                `record ${index + 1} failed: ${error.message}`
            );
        }
    }
}

// -----------------------------------------------------------------------------
// 27. Async iteration
// -----------------------------------------------------------------------------

async function* asyncNumberStream(limit) {
    if (!Number.isInteger(limit) || limit < 0) {
        throw new RangeError("limit must be non-negative");
    }

    for (let number = 0; number < limit; number++) {
        // Promise.resolve() demonstrates an asynchronous yield point without
        // requiring an external service.
        await Promise.resolve();
        yield number;
    }
}

async function asyncIterationExample() {
    section("27. Asynchronous iteration");

    for await (const number of asyncNumberStream(5)) {
        console.log(number);
    }
}

// -----------------------------------------------------------------------------
// 28. Sequential versus parallel asynchronous work
// -----------------------------------------------------------------------------

function delayedValue(value, delayMilliseconds) {
    return new Promise(resolve => {
        setTimeout(() => resolve(value), delayMilliseconds);
    });
}

async function asyncConcurrencyExample() {
    section("28. Asynchronous loop design");

    const delays = [20, 10, 5];

    const sequentialResults = [];

    for (const delay of delays) {
        // Awaiting inside the loop makes each operation wait for the previous
        // one. This is appropriate when ordering or dependency matters.
        sequentialResults.push(await delayedValue(delay, delay));
    }

    console.log("sequential:", sequentialResults);

    // Promise.all starts independent operations without serially waiting for
    // each one. The loop builds the collection of promises.
    const promises = [];

    for (const delay of delays) {
        promises.push(delayedValue(delay, delay));
    }

    const parallelResults = await Promise.all(promises);
    console.log("parallel:", parallelResults);
}

// -----------------------------------------------------------------------------
// 29. Labelled loops
// -----------------------------------------------------------------------------

function labelledLoopExample() {
    section("29. Labelled loops");

    // Labels allow break or continue to target an outer loop.
    // They should be used sparingly because deeply nested control flow can
    // reduce readability.
    outerLoop:
    for (let row = 0; row < 3; row++) {
        for (let column = 0; column < 3; column++) {
            if (row === 1 && column === 1) {
                break outerLoop;
            }

            console.log(row, column);
        }
    }
}

// -----------------------------------------------------------------------------
// 30. Real-world report generation
// -----------------------------------------------------------------------------

function reportExample() {
    section("30. Report generation");

    const sales = [
        { product: "Laptop", quantity: 3, price: 70000 },
        { product: "Monitor", quantity: 5, price: 15000 },
        { product: "Keyboard", quantity: 10, price: 2500 }
    ];

    let grandTotal = 0;

    for (const sale of sales) {
        if (
            !Number.isFinite(sale.quantity) ||
            sale.quantity < 0 ||
            !Number.isFinite(sale.price) ||
            sale.price < 0
        ) {
            throw new Error(`invalid sale: ${sale.product}`);
        }

        const revenue = sale.quantity * sale.price;
        grandTotal += revenue;

        console.log(
            `${sale.product}: quantity=${sale.quantity}, revenue=${revenue}`
        );
    }

    console.log("grand total:", grandTotal);
}

// -----------------------------------------------------------------------------
// 31. Edge cases
// -----------------------------------------------------------------------------

function edgeCaseExample() {
    section("31. Edge cases");

    // The loop does not execute for an empty array.
    for (const value of []) {
        console.log(value);
    }

    console.log("empty loop completed");

    // Mutating an array during index-based iteration can be deliberate but
    // requires careful index management.
    const values = [1, 2, 3, 4, 5];

    for (let index = values.length - 1; index >= 0; index--) {
        if (values[index] % 2 === 0) {
            values.splice(index, 1);
        }
    }

    console.log("reverse-index removal:", values);
}

// -----------------------------------------------------------------------------
// 32. Assertions and tests
// -----------------------------------------------------------------------------

function assertEqual(actual, expected, message) {
    if (actual !== expected) {
        throw new Error(
            `${message}: expected ${expected}, received ${actual}`
        );
    }
}

function tests() {
    section("32. Tests");

    assertEqual(
        linearSearch([10, 20, 30], 20),
        1,
        "linear search"
    );

    assertEqual(
        linearSearch([10, 20, 30], 99),
        -1,
        "missing linear search"
    );

    assertEqual(
        binarySearch([10, 20, 30], 20),
        1,
        "binary search"
    );

    assertEqual(
        bubbleSort([3, 1, 2]).join(","),
        "1,2,3",
        "bubble sort"
    );

    assertEqual(
        bubbleSort([5, 5, 5]).join(","),
        "5,5,5",
        "duplicate sort"
    );

    console.log("all assertions passed");
}

// -----------------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------------

async function main() {
    basicForLoop();
    arrayIteration();
    stringIteration();
    objectIteration();
    rangeExamples();
    breakExample();
    continueExample();
    nestedLoops();
    searchExamples();
    frequencyExample();
    accumulatorExample();
    transformationExample();
    forEachComparison();
    iteratorExample();
    customIterableExample();
    generatorExample();
    pipelineExample();
    chunkExample();
    matrixExample();
    graphExample();
    validationExample();
    transactionExample();
    sortingExample();
    complexityExample();
    performanceExample();
    errorHandlingExample();
    await asyncIterationExample();
    await asyncConcurrencyExample();
    labelledLoopExample();
    reportExample();
    edgeCaseExample();
    tests();
}

main().catch(error => {
    console.error("Fatal error:", error);
    process.exitCode = 1;
});
