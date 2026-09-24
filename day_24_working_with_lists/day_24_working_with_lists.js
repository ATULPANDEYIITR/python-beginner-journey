"use strict";

/*
 * Working with Lists in JavaScript
 * --------------------------------
 *
 * JavaScript does not have a built-in type literally named "List".
 * The Array type provides the primary ordered, mutable collection used
 * similarly to Python lists.
 *
 * This file progresses from basic array operations to advanced patterns:
 * indexing, slicing, mutation, iteration, higher-order functions,
 * sorting, copying, nested arrays, stacks, queues, searching,
 * validation, asynchronous processing, and a practical case study.
 *
 * Run with:
 *     node working_with_lists.js
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
    console.log("\n" + "-".repeat(78));
    console.log(title);
    console.log("-".repeat(78));
}

function show(label, value) {
    console.log(`${label}:`, value);
}

// ---------------------------------------------------------------------------
// 1. Array fundamentals
// ---------------------------------------------------------------------------

function demonstrateFundamentals() {
    section("1. Array fundamentals");

    const empty = [];
    const numbers = [10, 20, 30, 40];
    const names = ["Alice", "Bob", "Charlie"];
    const mixed = [42, "JavaScript", 3.14, true, null];

    show("Empty array", empty);
    show("Numbers", numbers);
    show("Names", names);
    show("Mixed values", mixed);

    // Arrays preserve insertion order and can contain duplicate values.
    const repeated = ["red", "blue", "red", "green", "blue"];
    show("Duplicates", repeated);

    // Arrays can contain other arrays.
    const nested = [[1, 2], [3, 4], [5, 6]];
    show("Nested array", nested);

    show("Length", numbers.length);
    show("Array.isArray(numbers)", Array.isArray(numbers));
}

// ---------------------------------------------------------------------------
// 2. Indexing and safe access
// ---------------------------------------------------------------------------

function demonstrateIndexing() {
    section("2. Indexing");

    const values = ["zero", "one", "two", "three", "four"];

    show("First element", values[0]);
    show("Third element", values[2]);

    // JavaScript does not support Python-style negative indexing.
    // at() provides a convenient modern alternative.
    show("Last element with at(-1)", values.at(-1));
    show("Second-last with at(-2)", values.at(-2));

    // An out-of-range bracket access returns undefined rather than throwing.
    show("Out-of-range bracket access", values[100]);

    // at() also returns undefined when the position is absent.
    show("Out-of-range at()", values.at(100));
}

// ---------------------------------------------------------------------------
// 3. Slice and splice
// ---------------------------------------------------------------------------

function demonstrateSliceAndSplice() {
    section("3. slice() versus splice()");

    const values = [0, 1, 2, 3, 4, 5];

    // slice() returns a new array and does not mutate the source.
    const slice = values.slice(1, 4);
    show("slice(1, 4)", slice);
    show("Original after slice()", values);

    // splice() changes the original array.
    const removed = values.splice(2, 2);
    show("Removed by splice()", removed);
    show("Original after splice()", values);

    // splice() can insert without removing anything.
    values.splice(2, 0, 99, 100);
    show("After splice insertion", values);

    // splice() can replace existing elements.
    values.splice(1, 2, 200, 300);
    show("After splice replacement", values);
}

// ---------------------------------------------------------------------------
// 4. Adding and removing
// ---------------------------------------------------------------------------

function demonstrateMutationMethods() {
    section("4. Adding and removing elements");

    const values = [1, 2];

    values.push(3);
    show("After push()", values);

    values.push(4, 5);
    show("After multiple push values", values);

    const last = values.pop();
    show("pop() returned", last);
    show("After pop()", values);

    values.unshift(0);
    show("After unshift()", values);

    const first = values.shift();
    show("shift() returned", first);
    show("After shift()", values);

    // push/pop are generally suitable for stack operations.
    // Repeated shift/unshift operations can be expensive for large arrays.
}

// ---------------------------------------------------------------------------
// 5. Membership and searching
// ---------------------------------------------------------------------------

function demonstrateSearching() {
    section("5. Searching");

    const values = [12, 7, 25, 7, 42, 19];

    show("includes(25)", values.includes(25));
    show("includes(100)", values.includes(100));

    // indexOf returns the first matching position or -1.
    show("indexOf(7)", values.indexOf(7));
    show("indexOf(100)", values.indexOf(100));

    // lastIndexOf searches from the end.
    show("lastIndexOf(7)", values.lastIndexOf(7));

    // find returns the first matching value.
    show("find(value > 30)", values.find(value => value > 30));

    // findIndex returns the position of the first matching value.
    show("findIndex(value > 30)", values.findIndex(value => value > 30));

    // some() and every() answer predicate-based questions.
    show("some(value > 40)", values.some(value => value > 40));
    show("every(value > 0)", values.every(value => value > 0));
}

// ---------------------------------------------------------------------------
// 6. Iteration
// ---------------------------------------------------------------------------

function demonstrateIteration() {
    section("6. Iteration");

    const names = ["Alice", "Bob", "Charlie"];

    console.log("for...of:");
    for (const name of names) {
        console.log(" ", name);
    }

    console.log("forEach:");
    names.forEach((name, index) => {
        console.log(`  ${index}: ${name}`);
    });

    console.log("Traditional for:");
    for (let index = 0; index < names.length; index += 1) {
        console.log(`  ${index}: ${names[index]}`);
    }
}

// ---------------------------------------------------------------------------
// 7. map, filter, reduce
// ---------------------------------------------------------------------------

function demonstrateHigherOrderMethods() {
    section("7. map(), filter(), and reduce()");

    const numbers = [1, 2, 3, 4, 5];

    const squares = numbers.map(number => number * number);
    const evens = numbers.filter(number => number % 2 === 0);
    const total = numbers.reduce((sum, number) => sum + number, 0);

    show("Original", numbers);
    show("map squares", squares);
    show("filter evens", evens);
    show("reduce sum", total);

    // Chaining is useful for readable transformation pipelines.
    const result = numbers
        .filter(number => number % 2 !== 0)
        .map(number => number * 10)
        .reduce((sum, number) => sum + number, 0);

    show("Chained result", result);
}

// ---------------------------------------------------------------------------
// 8. Sorting
// ---------------------------------------------------------------------------

function demonstrateSorting() {
    section("8. Sorting");

    // Important JavaScript distinction:
    // Array.prototype.sort() mutates the original array.
    // The default comparator converts values to strings.
    const words = ["pear", "apple", "banana", "fig"];
    words.sort();
    show("Alphabetical sort", words);

    // Numeric sorting requires an explicit comparator.
    const numbers = [40, 5, 100, 25, 1];
    numbers.sort((a, b) => a - b);
    show("Numeric ascending", numbers);

    numbers.sort((a, b) => b - a);
    show("Numeric descending", numbers);

    const people = [
        { name: "Alice", age: 31 },
        { name: "Bob", age: 24 },
        { name: "Charlie", age: 29 }
    ];

    people.sort((a, b) => a.age - b.age);
    show("People sorted by age", people);

    // A comparator can express multiple sorting criteria.
    const products = [
        { name: "Laptop", rating: 4.5, price: 900 },
        { name: "Phone", rating: 4.7, price: 700 },
        { name: "Tablet", rating: 4.7, price: 500 }
    ];

    products.sort((a, b) => {
        if (b.rating !== a.rating) {
            return b.rating - a.rating;
        }
        return a.price - b.price;
    });

    show("Products by rating then price", products);
}

// ---------------------------------------------------------------------------
// 9. Copying arrays
// ---------------------------------------------------------------------------

function demonstrateCopying() {
    section("9. References and copying");

    const original = [1, 2, 3];
    const alias = original;

    alias.push(4);

    show("Original after alias mutation", original);
    show("alias === original", alias === original);

    // Spread syntax creates a new outer array.
    const shallowCopy = [...original];
    shallowCopy.push(5);

    show("Original after shallow-copy mutation", original);
    show("Shallow copy", shallowCopy);
    show("shallowCopy === original", shallowCopy === original);

    // Array.from() also creates a new outer array.
    const anotherCopy = Array.from(original);
    anotherCopy[0] = 999;

    show("Original after Array.from mutation", original);
    show("Array.from copy", anotherCopy);
}

// ---------------------------------------------------------------------------
// 10. Nested arrays and shallow-copy behavior
// ---------------------------------------------------------------------------

function demonstrateNestedArrays() {
    section("10. Nested arrays");

    const matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ];

    show("Matrix", matrix);
    show("Middle value", matrix[1][1]);

    const shallow = matrix.map(row => row.slice());
    shallow[0][0] = 999;

    show("Original after copied-row mutation", matrix);
    show("Independent row copy", shallow);

    // A common mistake is Array(3).fill([]), because every slot references
    // the same inner array.
    const incorrect = Array(3).fill([]);
    incorrect[0].push("shared");

    show("Shared-inner-array problem", incorrect);

    // map() creates three separate inner arrays.
    const correct = Array.from({ length: 3 }, () => []);
    correct[0].push("independent");

    show("Independent-inner-array structure", correct);
}

// ---------------------------------------------------------------------------
// 11. Flattening
// ---------------------------------------------------------------------------

function demonstrateFlattening() {
    section("11. Flattening");

    const nested = [[1, 2], [3, 4], [5]];

    show("flat()", nested.flat());

    const deeplyNested = [1, [2, [3, [4]]]];
    show("flat(Infinity)", deeplyNested.flat(Infinity));

    // flatMap combines map and one level of flattening.
    const sentences = ["a b", "c d"];
    const words = sentences.flatMap(sentence => sentence.split(" "));

    show("flatMap words", words);
}

// ---------------------------------------------------------------------------
// 12. Destructuring
// ---------------------------------------------------------------------------

function demonstrateDestructuring() {
    section("12. Destructuring");

    const values = [10, 20, 30, 40];

    const [first, second, ...remaining] = values;

    show("first", first);
    show("second", second);
    show("remaining", remaining);

    // Default values apply when the corresponding element is undefined.
    const [present, missing = 100] = [42];
    show("present", present);
    show("default value", missing);

    // Swapping can be performed without a temporary variable.
    let left = "L";
    let right = "R";

    [left, right] = [right, left];

    show("Swapped left", left);
    show("Swapped right", right);
}

// ---------------------------------------------------------------------------
// 13. Stack
// ---------------------------------------------------------------------------

function demonstrateStack() {
    section("13. Stack implementation");

    const stack = [];

    stack.push("task A");
    stack.push("task B");
    stack.push("task C");

    show("Stack", stack);
    show("Top item", stack.at(-1));
    show("Popped", stack.pop());
    show("Stack after pop", stack);
}

// ---------------------------------------------------------------------------
// 14. Queue
// ---------------------------------------------------------------------------

class Queue {
    constructor() {
        this.items = [];
        this.frontIndex = 0;
    }

    enqueue(value) {
        this.items.push(value);
    }

    dequeue() {
        if (this.frontIndex >= this.items.length) {
            return undefined;
        }

        const value = this.items[this.frontIndex];
        this.frontIndex += 1;

        // Periodically reclaim consumed storage.
        if (this.frontIndex > 32 && this.frontIndex * 2 > this.items.length) {
            this.items = this.items.slice(this.frontIndex);
            this.frontIndex = 0;
        }

        return value;
    }

    get size() {
        return this.items.length - this.frontIndex;
    }

    toArray() {
        return this.items.slice(this.frontIndex);
    }
}

function demonstrateQueue() {
    section("14. Queue implementation");

    const queue = new Queue();

    queue.enqueue("customer 1");
    queue.enqueue("customer 2");
    queue.enqueue("customer 3");

    show("Queue", queue.toArray());
    show("Dequeued", queue.dequeue());
    show("Queue after dequeue", queue.toArray());
    show("Queue size", queue.size);
}

// ---------------------------------------------------------------------------
// 15. Frequency analysis
// ---------------------------------------------------------------------------

function frequencyMap(values) {
    const frequencies = new Map();

    for (const value of values) {
        frequencies.set(value, (frequencies.get(value) ?? 0) + 1);
    }

    return frequencies;
}

function demonstrateFrequencyAnalysis() {
    section("15. Frequency analysis");

    const values = ["apple", "banana", "apple", "orange", "banana", "apple"];
    const frequencies = frequencyMap(values);

    show("Frequency map", frequencies);
    show("Frequency of apple", frequencies.get("apple"));
}

// ---------------------------------------------------------------------------
// 16. Remove duplicates while preserving order
// ---------------------------------------------------------------------------

function uniquePreservingOrder(values) {
    return [...new Set(values)];
}

function demonstrateUniqueValues() {
    section("16. Duplicate removal");

    const values = [4, 2, 4, 1, 2, 3, 1];

    show("Original", values);
    show("Unique values", uniquePreservingOrder(values));
}

// ---------------------------------------------------------------------------
// 17. Binary search
// ---------------------------------------------------------------------------

function binarySearch(values, target) {
    let left = 0;
    let right = values.length - 1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);

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

function demonstrateBinarySearch() {
    section("17. Binary search");

    const values = [3, 7, 12, 18, 24, 31, 42];

    show("Index of 18", binarySearch(values, 18));
    show("Index of 100", binarySearch(values, 100));

    console.log(
        "Binary search requires sorted input and runs in O(log n) time."
    );
}

// ---------------------------------------------------------------------------
// 18. Two-pointer algorithm
// ---------------------------------------------------------------------------

function findPairWithSum(sortedValues, target) {
    let left = 0;
    let right = sortedValues.length - 1;

    while (left < right) {
        const sum = sortedValues[left] + sortedValues[right];

        if (sum === target) {
            return [sortedValues[left], sortedValues[right]];
        }

        if (sum < target) {
            left += 1;
        } else {
            right -= 1;
        }
    }

    return null;
}

function demonstrateTwoPointers() {
    section("18. Two-pointer algorithm");

    const values = [1, 3, 4, 6, 8, 11, 15];

    show("Pair for 14", findPairWithSum(values, 14));
    show("Pair for 100", findPairWithSum(values, 100));
}

// ---------------------------------------------------------------------------
// 19. Chunking
// ---------------------------------------------------------------------------

function chunkArray(values, chunkSize) {
    if (!Number.isInteger(chunkSize) || chunkSize <= 0) {
        throw new RangeError("chunkSize must be a positive integer");
    }

    const chunks = [];

    for (let index = 0; index < values.length; index += chunkSize) {
        chunks.push(values.slice(index, index + chunkSize));
    }

    return chunks;
}

function demonstrateChunking() {
    section("19. Chunking");

    const values = Array.from({ length: 10 }, (_, index) => index + 1);

    show("Chunks of three", chunkArray(values, 3));

    try {
        chunkArray(values, 0);
    } catch (error) {
        show("Invalid chunk size", `${error.name}: ${error.message}`);
    }
}

// ---------------------------------------------------------------------------
// 20. Validation
// ---------------------------------------------------------------------------

function averagePositiveNumbers(values) {
    if (!Array.isArray(values)) {
        throw new TypeError("Expected an array");
    }

    if (values.length === 0) {
        throw new RangeError("At least one value is required");
    }

    const validated = values.map((value) => {
        if (
            typeof value !== "number" ||
            !Number.isFinite(value) ||
            value <= 0
        ) {
            throw new RangeError(
                `Expected a finite positive number, received ${value}`
            );
        }

        return value;
    });

    return validated.reduce((sum, value) => sum + value, 0) / validated.length;
}

function demonstrateValidation() {
    section("20. Validation and errors");

    show("Average", averagePositiveNumbers([10, 20, 30]));

    const invalidInputs = [
        [],
        [10, -5, 20],
        [10, "20", 30],
        [10, NaN, 30]
    ];

    for (const input of invalidInputs) {
        try {
            averagePositiveNumbers(input);
        } catch (error) {
            console.log(
                `Input ${JSON.stringify(input)} -> ${error.name}: ${error.message}`
            );
        }
    }
}

// ---------------------------------------------------------------------------
// 21. Matrix operations
// ---------------------------------------------------------------------------

function transposeMatrix(matrix) {
    if (matrix.length === 0) {
        return [];
    }

    const columnCount = matrix[0].length;

    if (!matrix.every(row => Array.isArray(row) && row.length === columnCount)) {
        throw new Error("Matrix must be rectangular");
    }

    return Array.from(
        { length: columnCount },
        (_, column) => matrix.map(row => row[column])
    );
}

function demonstrateMatrixOperations() {
    section("21. Matrix operations");

    const matrix = [
        [1, 2, 3],
        [4, 5, 6]
    ];

    const doubled = matrix.map(row =>
        row.map(value => value * 2)
    );

    show("Doubled matrix", doubled);
    show("Transpose", transposeMatrix(matrix));

    try {
        transposeMatrix([[1, 2], [3]]);
    } catch (error) {
        show("Invalid matrix", `${error.name}: ${error.message}`);
    }
}

// ---------------------------------------------------------------------------
// 22. Practical data pipeline
// ---------------------------------------------------------------------------

function demonstrateDataPipeline() {
    section("22. Practical data-processing pipeline");

    const rawScores = [
        "82",
        "91",
        "invalid",
        "76",
        "",
        "88",
        "105",
        "-4"
    ];

    const validScores = rawScores
        .map(value => Number(value))
        .filter(value => Number.isInteger(value) && value >= 0 && value <= 100);

    const normalized = validScores.map(score => score / 100);

    const average = validScores.length === 0
        ? 0
        : validScores.reduce((sum, score) => sum + score, 0) /
          validScores.length;

    show("Valid scores", validScores);
    show("Normalized scores", normalized);
    show("Average", average);
}

// ---------------------------------------------------------------------------
// 23. Objects stored in arrays
// ---------------------------------------------------------------------------

function demonstrateObjectArrays() {
    section("23. Arrays of objects");

    const students = [
        { name: "Alice", score: 91.5, attendance: 96 },
        { name: "Bob", score: 84, attendance: 91 },
        { name: "Charlie", score: 91.5, attendance: 88 }
    ];

    const passed = students.filter(student => student.score >= 85);

    students.sort((a, b) => {
        if (b.score !== a.score) {
            return b.score - a.score;
        }
        return b.attendance - a.attendance;
    });

    show("Passed students", passed);
    show("Sorted students", students);
}

// ---------------------------------------------------------------------------
// 24. Optional chaining and nullish values
// ---------------------------------------------------------------------------

function demonstrateSafeNestedAccess() {
    section("24. Safe nested access");

    const users = [
        { name: "Alice", profile: { city: "Lucknow" } },
        { name: "Bob" }
    ];

    for (const user of users) {
        // Optional chaining prevents an exception when profile is absent.
        const city = user.profile?.city ?? "Unknown";
        console.log(`${user.name}: ${city}`);
    }
}

// ---------------------------------------------------------------------------
// 25. Immutability-oriented updates
// ---------------------------------------------------------------------------

function demonstrateImmutablePatterns() {
    section("25. Immutability-oriented array updates");

    const original = [10, 20, 30];

    // Create a new array rather than changing the original.
    const added = [...original, 40];

    // Replace an item without mutating the original.
    const replaced = original.map(
        (value, index) => index === 1 ? 999 : value
    );

    // Remove an item without mutating the original.
    const removed = original.filter((_, index) => index !== 1);

    show("Original", original);
    show("Added", added);
    show("Replaced", replaced);
    show("Removed", removed);
}

// ---------------------------------------------------------------------------
// 26. Performance considerations
// ---------------------------------------------------------------------------

function demonstratePerformance() {
    section("26. Basic performance measurement");

    const size = 200_000;

    const appendStart = performance.now();
    const values = [];

    for (let index = 0; index < size; index += 1) {
        values.push(index);
    }

    const appendTime = performance.now() - appendStart;

    const mapStart = performance.now();
    const squares = values.map(value => value * value);
    const mapTime = performance.now() - mapStart;

    show("push loop milliseconds", appendTime.toFixed(3));
    show("map milliseconds", mapTime.toFixed(3));
    show("Result sizes", [values.length, squares.length]);

    console.log(
        "Microbenchmark values depend on the JavaScript engine and machine."
    );
}

// ---------------------------------------------------------------------------
// 27. Asynchronous list processing
// ---------------------------------------------------------------------------

function delayedDouble(value, delayMilliseconds) {
    return new Promise(resolve => {
        setTimeout(() => resolve(value * 2), delayMilliseconds);
    });
}

async function demonstrateAsyncProcessing() {
    section("27. Asynchronous array processing");

    const values = [1, 2, 3];

    // Promise.all preserves input order even though individual operations
    // may finish at different times.
    const results = await Promise.all(
        values.map((value, index) =>
            delayedDouble(value, (values.length - index) * 10)
        )
    );

    show("Asynchronous results", results);

    // Sequential processing is different from concurrent Promise creation.
    const sequentialResults = [];

    for (const value of values) {
        sequentialResults.push(await delayedDouble(value, 5));
    }

    show("Sequential results", sequentialResults);
}

// ---------------------------------------------------------------------------
// 28. Practical inventory case study
// ---------------------------------------------------------------------------

class InventoryManager {
    constructor(items = []) {
        this.items = [...items];
    }

    validateItem(item) {
        if (!item || typeof item !== "object") {
            throw new TypeError("Inventory item must be an object");
        }

        if (typeof item.sku !== "string" || item.sku.trim() === "") {
            throw new TypeError("SKU must be a non-empty string");
        }

        if (typeof item.name !== "string" || item.name.trim() === "") {
            throw new TypeError("Name must be a non-empty string");
        }

        if (!Number.isInteger(item.quantity) || item.quantity < 0) {
            throw new RangeError("Quantity must be a non-negative integer");
        }

        if (
            typeof item.price !== "number" ||
            !Number.isFinite(item.price) ||
            item.price < 0
        ) {
            throw new RangeError("Price must be a non-negative finite number");
        }
    }

    addItem(item) {
        this.validateItem(item);

        if (this.items.some(existing => existing.sku === item.sku)) {
            throw new Error(`Duplicate SKU: ${item.sku}`);
        }

        this.items.push({ ...item });
    }

    findBySku(sku) {
        return this.items.find(item => item.sku === sku);
    }

    adjustStock(sku, adjustment) {
        if (!Number.isInteger(adjustment)) {
            throw new TypeError("Stock adjustment must be an integer");
        }

        const item = this.findBySku(sku);

        if (!item) {
            throw new Error(`SKU not found: ${sku}`);
        }

        const newQuantity = item.quantity + adjustment;

        if (newQuantity < 0) {
            throw new RangeError("Stock quantity cannot become negative");
        }

        item.quantity = newQuantity;
    }

    totalValue() {
        return this.items.reduce(
            (total, item) => total + item.quantity * item.price,
            0
        );
    }

    expensiveFirst() {
        return [...this.items].sort((a, b) => b.price - a.price);
    }
}

function demonstrateInventoryCaseStudy() {
    section("28. Practical inventory case study");

    const manager = new InventoryManager();

    manager.addItem({
        sku: "LAP-001",
        name: "Laptop",
        quantity: 8,
        price: 75000
    });

    manager.addItem({
        sku: "PHN-002",
        name: "Phone",
        quantity: 15,
        price: 42000
    });

    manager.addItem({
        sku: "MON-003",
        name: "Monitor",
        quantity: 12,
        price: 18000
    });

    show("Initial inventory", manager.items);
    show("Total inventory value", manager.totalValue());

    manager.adjustStock("PHN-002", -3);

    show("After phone stock adjustment", manager.items);
    show("Expensive-first view", manager.expensiveFirst());

    try {
        manager.adjustStock("PHN-002", -100);
    } catch (error) {
        show("Rejected invalid stock adjustment", `${error.name}: ${error.message}`);
    }
}

// ---------------------------------------------------------------------------
// 29. Assertions
// ---------------------------------------------------------------------------

function demonstrateAssertions() {
    section("29. Lightweight testing");

    function uniquePreservingOrder(values) {
        return [...new Set(values)];
    }

    const tests = [
        { input: [], expected: [] },
        { input: [1], expected: [1] },
        { input: [1, 2, 1, 3], expected: [1, 2, 3] },
        { input: ["a", "a", "b"], expected: ["a", "b"] }
    ];

    for (const test of tests) {
        const actual = uniquePreservingOrder(test.input);
        const actualJSON = JSON.stringify(actual);
        const expectedJSON = JSON.stringify(test.expected);

        if (actualJSON !== expectedJSON) {
            throw new Error(
                `Test failed: expected ${expectedJSON}, got ${actualJSON}`
            );
        }
    }

    console.log(`Passed ${tests.length} array-processing tests.`);
}

// ---------------------------------------------------------------------------
// 30. Main runner
// ---------------------------------------------------------------------------

async function main() {
    demonstrateFundamentals();
    demonstrateIndexing();
    demonstrateSliceAndSplice();
    demonstrateMutationMethods();
    demonstrateSearching();
    demonstrateIteration();
    demonstrateHigherOrderMethods();
    demonstrateSorting();
    demonstrateCopying();
    demonstrateNestedArrays();
    demonstrateFlattening();
    demonstrateDestructuring();
    demonstrateStack();
    demonstrateQueue();
    demonstrateFrequencyAnalysis();
    demonstrateUniqueValues();
    demonstrateBinarySearch();
    demonstrateTwoPointers();
    demonstrateChunking();
    demonstrateValidation();
    demonstrateMatrixOperations();
    demonstrateDataPipeline();
    demonstrateObjectArrays();
    demonstrateSafeNestedAccess();
    demonstrateImmutablePatterns();
    demonstratePerformance();
    await demonstrateAsyncProcessing();
    demonstrateInventoryCaseStudy();
    demonstrateAssertions();

    section("Study program completed");
    console.log("All JavaScript array demonstrations completed successfully.");
}

main().catch(error => {
    console.error("Program failed:", error);
    process.exitCode = 1;
});
