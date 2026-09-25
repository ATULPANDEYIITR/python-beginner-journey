/*
 * TUPLES IN JAVASCRIPT
 * ====================
 *
 * JavaScript does not have a built-in Tuple type equivalent to Python's tuple.
 * Arrays are mutable sequences, so this file demonstrates:
 *
 * 1. Tuple-like arrays
 * 2. Object.freeze()
 * 3. Readonly-by-convention patterns
 * 4. Destructuring
 * 5. Rest/spread syntax
 * 6. Immutable data transformations
 * 7. Map/Set keys using object identity
 * 8. Records represented by arrays versus objects
 * 9. TypeScript-style conceptual tuples expressed in JavaScript
 * 10. A production-style transaction-processing case study
 *
 * Run with:
 *     node tuples.js
 *
 * The file uses only standard JavaScript and Node.js APIs.
 */

"use strict";


// ============================================================================
// 1. BASIC ARRAY STRUCTURE
// ============================================================================

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function subsection(title) {
    console.log(`\n--- ${title} ---`);
}


function basics() {
    section("1. Tuple-Like Structures in JavaScript");

    // JavaScript uses Array for ordered collections.
    // Unlike Python tuples, arrays are mutable.
    const coordinates = [10, 20];
    const mixedValues = ["Atul", 30, 88.5, true];

    console.log("Coordinates:", coordinates);
    console.log("Mixed values:", mixedValues);

    coordinates.push(30);
    console.log("Mutable array after push:", coordinates);

    // JavaScript has no built-in Python-style tuple literal:
    // (10, 20) is parsed as a parenthesized expression, not a tuple.
    console.log("typeof [10, 20]:", typeof [10, 20]);
}


// ============================================================================
// 2. FROZEN TUPLE-LIKE ARRAYS
// ============================================================================

function frozenArrays() {
    section("2. Object.freeze() as a Tuple-Like Technique");

    const coordinates = Object.freeze([10, 20]);

    console.log("Frozen coordinates:", coordinates);
    console.log("Frozen:", Object.isFrozen(coordinates));

    // In strict mode, changing a frozen array throws TypeError.
    try {
        coordinates[0] = 99;
    } catch (error) {
        console.log("Mutation rejected:", error.message);
    }

    try {
        coordinates.push(30);
    } catch (error) {
        console.log("push rejected:", error.message);
    }

    console.log("Coordinates after failed mutation:", coordinates);
}


// ============================================================================
// 3. SHALLOW IMMUTABILITY
// ============================================================================

function shallowImmutability() {
    section("3. Shallow Versus Deep Immutability");

    const value = Object.freeze([
        "configuration",
        { debug: false }
    ]);

    // The array itself is frozen, but the nested object is not.
    value[1].debug = true;

    console.log("Nested object changed:", value);

    // To make the nested structure immutable, nested objects also need
    // protection.
    const deeplyFrozen = Object.freeze([
        "configuration",
        Object.freeze({ debug: false })
    ]);

    try {
        deeplyFrozen[1].debug = true;
    } catch (error) {
        console.log("Nested mutation rejected:", error.message);
    }

    console.log("Deeply protected structure:", deeplyFrozen);
}


// ============================================================================
// 4. DESTRUCTURING
// ============================================================================

function destructuring() {
    section("4. Destructuring and Unpacking");

    const person = Object.freeze(["Atul", 30, "India"]);

    const [name, age, country] = person;

    console.log("Name:", name);
    console.log("Age:", age);
    console.log("Country:", country);

    // Rest syntax collects remaining elements into a new array.
    const [first, ...middle] = Object.freeze([10, 20, 30, 40]);
    console.log("First:", first);
    console.log("Rest:", middle);

    // Nested destructuring.
    const employee = Object.freeze([
        "E101",
        Object.freeze(["Atul", "Pandey"]),
        Object.freeze(["Engineering", "Python"])
    ]);

    const [
        employeeId,
        [firstName, lastName],
        [department, skill]
    ] = employee;

    console.log({
        employeeId,
        firstName,
        lastName,
        department,
        skill
    });
}


// ============================================================================
// 5. REST AND SPREAD
// ============================================================================

function restAndSpread() {
    section("5. Rest and Spread");

    const original = Object.freeze([1, 2, 3]);

    // Spread creates a new array.
    const expanded = [...original, 4, 5];

    console.log("Original:", original);
    console.log("Expanded copy:", expanded);

    // Destructuring with rest.
    const [head, ...tail] = original;
    console.log("Head:", head);
    console.log("Tail:", tail);

    // Immutable transformation.
    const replaced = original.map((value, index) =>
        index === 1 ? 99 : value
    );

    console.log("Original remains:", original);
    console.log("Transformed:", replaced);
}


// ============================================================================
// 6. INDEXING AND SLICING
// ============================================================================

function indexingAndSlicing() {
    section("6. Indexing and Slicing");

    const values = Object.freeze([
        "zero",
        "one",
        "two",
        "three",
        "four"
    ]);

    console.log("First:", values[0]);
    console.log("Last:", values[values.length - 1]);

    // slice() does not mutate the original array.
    console.log("Slice:", values.slice(1, 4));
    console.log("Original:", values);

    // Modern JavaScript supports at().
    console.log("Last with at(-1):", values.at(-1));

    // An out-of-range index returns undefined rather than throwing.
    console.log("Out of range:", values[100]);
}


// ============================================================================
// 7. COMPARISON
// ============================================================================

function comparison() {
    section("7. Array Comparison and Identity");

    const first = Object.freeze([1, 2]);
    const second = Object.freeze([1, 2]);

    // Arrays are objects, so === compares object identity.
    console.log("first === second:", first === second);

    const sameReference = first;
    console.log("first === sameReference:", first === sameReference);

    // A content comparison can be implemented explicitly.
    function arraysEqual(left, right) {
        if (left.length !== right.length) {
            return false;
        }

        return left.every((value, index) => value === right[index]);
    }

    console.log("Content equality:", arraysEqual(first, second));
}


// ============================================================================
// 8. IMMUTABLE RECORD FACTORY
// ============================================================================

function createTuple(values) {
    if (!Array.isArray(values)) {
        throw new TypeError("Tuple-like value must be an array");
    }

    // A shallow frozen copy prevents mutation of the original input from
    // changing the resulting tuple-like structure.
    return Object.freeze([...values]);
}


function tupleFactoryExample() {
    section("8. Tuple-Like Factory");

    const source = [10, 20, 30];
    const tuple = createTuple(source);

    source.push(40);

    console.log("Source:", source);
    console.log("Tuple-like snapshot:", tuple);

    try {
        tuple[0] = 99;
    } catch (error) {
        console.log("Mutation rejected:", error.message);
    }
}


// ============================================================================
// 9. VALIDATION
// ============================================================================

function validateCoordinate(value) {
    if (!Array.isArray(value)) {
        throw new TypeError("Coordinate must be an array");
    }

    if (value.length !== 2) {
        throw new RangeError("Coordinate must contain exactly two values");
    }

    const [x, y] = value;

    if (
        typeof x !== "number" ||
        !Number.isFinite(x) ||
        typeof y !== "number" ||
        !Number.isFinite(y)
    ) {
        throw new TypeError("Coordinate values must be finite numbers");
    }

    return Object.freeze([x, y]);
}


function validationExamples() {
    section("9. Validation");

    const validValues = [
        [10, 20],
        [-5.5, 4],
        [0, 0]
    ];

    for (const value of validValues) {
        console.log(value, "->", validateCoordinate(value));
    }

    const invalidValues = [
        [10],
        [10, 20, 30],
        ["10", 20],
        [Infinity, 20],
        "10,20"
    ];

    for (const value of invalidValues) {
        try {
            validateCoordinate(value);
        } catch (error) {
            console.log(
                JSON.stringify(value),
                "-> rejected:",
                error.message
            );
        }
    }
}


// ============================================================================
// 10. MAP KEYS AND IDENTITY
// ============================================================================

function mapKeys() {
    section("10. Tuple-Like Values as Map Keys");

    const firstCoordinate = Object.freeze([10, 20]);
    const secondCoordinate = Object.freeze([10, 20]);

    const locations = new Map();

    locations.set(firstCoordinate, "Point A");

    console.log("Using same reference:", locations.get(firstCoordinate));
    console.log("Using equal contents:", locations.get(secondCoordinate));

    // JavaScript arrays are not value-hashable like Python tuples.
    // A stable serialized key is one possible application-level solution.
    function coordinateKey([x, y]) {
        return `${x},${y}`;
    }

    const coordinateMap = new Map();
    coordinateMap.set(coordinateKey(firstCoordinate), "Point A");

    console.log(
        "Value-based lookup:",
        coordinateMap.get(coordinateKey(secondCoordinate))
    );
}


// ============================================================================
// 11. SYMBOLIC RECORDS
// ============================================================================

function recordsComparison() {
    section("11. Positional Records Versus Named Records");

    const positionalRecord = Object.freeze([
        "TX001",
        "ACC100",
        1500,
        "INR"
    ]);

    const namedRecord = Object.freeze({
        transactionId: "TX001",
        accountId: "ACC100",
        amount: 1500,
        currency: "INR"
    });

    console.log("Positional record:", positionalRecord);
    console.log("Named record:", namedRecord);

    // Positional structures are compact but depend on field order.
    console.log("Transaction ID:", positionalRecord[0]);

    // Named records make field meaning explicit.
    console.log("Transaction ID:", namedRecord.transactionId);
}


// ============================================================================
// 12. HIGHER-ORDER FUNCTIONS
// ============================================================================

function higherOrderExamples() {
    section("12. Functional Processing");

    const numbers = Object.freeze([1, 2, 3, 4, 5]);

    const squares = Object.freeze(
        numbers.map(number => number * number)
    );

    const evenSquares = Object.freeze(
        squares.filter(number => number % 2 === 0)
    );

    const total = evenSquares.reduce(
        (sum, number) => sum + number,
        0
    );

    console.log("Numbers:", numbers);
    console.log("Squares:", squares);
    console.log("Even squares:", evenSquares);
    console.log("Total:", total);
}


// ============================================================================
// 13. ITERATORS AND GENERATORS
// ============================================================================

function* numberGenerator(limit) {
    for (let number = 0; number < limit; number++) {
        yield number;
    }
}


function iteratorExamples() {
    section("13. Iterators and Generators");

    const generator = numberGenerator(5);

    console.log(generator.next());
    console.log(generator.next());
    console.log(generator.next());

    const materialized = Object.freeze(
        [...generator]
    );

    console.log("Remaining generated values:", materialized);
}


// ============================================================================
// 14. ASYNCHRONOUS DATA
// ============================================================================

async function fetchLikeTransaction() {
    // This simulates an asynchronous API response without external services.
    await new Promise(resolve => setTimeout(resolve, 5));

    return Object.freeze([
        "TX100",
        "ACC200",
        750,
        "INR"
    ]);
}


async function asynchronousTupleExample() {
    section("14. Tuples in Asynchronous Application Code");

    const transaction = await fetchLikeTransaction();

    const [id, account, amount, currency] = transaction;

    console.log({
        id,
        account,
        amount,
        currency
    });
}


// ============================================================================
// 15. SORTING
// ============================================================================

function sortingExamples() {
    section("15. Sorting Tuple-Like Records");

    const records = Object.freeze([
        Object.freeze(["Atul", 88]),
        Object.freeze(["Riya", 95]),
        Object.freeze(["Aman", 88]),
        Object.freeze(["Zoya", 72])
    ]);

    // sort() mutates its array, so copy before sorting.
    const byScore = [...records].sort(
        (left, right) => right[1] - left[1]
    );

    console.log("Original:", records);
    console.log("By score:", byScore);

    const byName = [...records].sort(
        (left, right) => left[0].localeCompare(right[0])
    );

    console.log("By name:", byName);
}


// ============================================================================
// 16. EDGE CASES
// ============================================================================

function edgeCases() {
    section("16. Edge Cases");

    const empty = Object.freeze([]);
    const one = Object.freeze([42]);

    console.log("Empty:", empty);
    console.log("One element:", one);

    console.log("Empty length:", empty.length);
    console.log("Missing index:", one[10]);

    // NaN is not equal to itself.
    const special = Object.freeze([NaN]);

    console.log("NaN === NaN:", NaN === NaN);
    console.log(
        "Object.is(NaN, NaN):",
        Object.is(special[0], NaN)
    );

    // Object.freeze does not make primitive references special.
    const mixed = Object.freeze([
        null,
        undefined,
        false,
        0,
        ""
    ]);

    console.log("Mixed edge values:", mixed);
}


// ============================================================================
// 17. PERFORMANCE
// ============================================================================

function performanceExample() {
    section("17. Performance Considerations");

    const values = Object.freeze(
        Array.from({ length: 100_000 }, (_, index) => index)
    );

    console.time("map");
    const squares = values.map(value => value * value);
    console.timeEnd("map");

    console.log("Square count:", squares.length);

    // Object.freeze has a runtime cost and should be applied deliberately.
    // The right representation depends on mutation requirements and workload.
}


// ============================================================================
// 18. ERROR HANDLING
// ============================================================================

function errorHandling() {
    section("18. Error Handling");

    function divide(dividend, divisor) {
        if (typeof dividend !== "number" || typeof divisor !== "number") {
            throw new TypeError("Both operands must be numbers");
        }

        if (divisor === 0) {
            throw new RangeError("Division by zero is not allowed");
        }

        return Object.freeze([
            dividend / divisor,
            dividend % divisor
        ]);
    }

    try {
        console.log("Result:", divide(17, 5));
    } catch (error) {
        console.error(error.message);
    }

    try {
        divide(17, 0);
    } catch (error) {
        console.log("Expected failure:", error.message);
    }

    try {
        divide("17", 5);
    } catch (error) {
        console.log("Expected validation failure:", error.message);
    }
}


// ============================================================================
// 19. PRODUCTION-STYLE TRANSACTION PIPELINE
// ============================================================================

class TransactionProcessor {
    constructor() {
        this.transactions = [];
    }

    addTransaction(transaction) {
        const normalized = this.validateTransaction(transaction);
        this.transactions.push(normalized);
    }

    validateTransaction(transaction) {
        if (!Array.isArray(transaction)) {
            throw new TypeError("Transaction must be an array");
        }

        if (transaction.length !== 4) {
            throw new RangeError(
                "Transaction must contain four fields"
            );
        }

        const [id, accountId, amount, currency] = transaction;

        if (
            typeof id !== "string" ||
            typeof accountId !== "string" ||
            typeof currency !== "string"
        ) {
            throw new TypeError(
                "ID, account ID, and currency must be strings"
            );
        }

        if (
            typeof amount !== "number" ||
            !Number.isFinite(amount)
        ) {
            throw new TypeError("Amount must be a finite number");
        }

        return Object.freeze([
            id,
            accountId,
            amount,
            currency
        ]);
    }

    getTransactions() {
        return Object.freeze([...this.transactions]);
    }

    totalsByAccount() {
        const totals = new Map();

        for (const transaction of this.transactions) {
            const [, accountId, amount] = transaction;

            totals.set(
                accountId,
                (totals.get(accountId) ?? 0) + amount
            );
        }

        return totals;
    }
}


function transactionCaseStudy() {
    section("19. Production-Style Transaction Processor");

    const processor = new TransactionProcessor();

    const sourceTransactions = [
        ["TX001", "ACC100", 1500, "INR"],
        ["TX002", "ACC101", -250, "INR"],
        ["TX003", "ACC100", 750, "INR"]
    ];

    for (const transaction of sourceTransactions) {
        processor.addTransaction(transaction);
    }

    console.log("Transactions:", processor.getTransactions());

    const totals = processor.totalsByAccount();

    for (const [account, total] of totals) {
        console.log(`${account}: ${total}`);
    }
}


// ============================================================================
// 20. IMMUTABLE UPDATE PATTERN
// ============================================================================

function immutableUpdate() {
    section("20. Immutable Update Patterns");

    const original = Object.freeze([
        Object.freeze({ id: 1, active: false }),
        Object.freeze({ id: 2, active: true })
    ]);

    const updated = Object.freeze(
        original.map(record =>
            record.id === 1
                ? Object.freeze({ ...record, active: true })
                : record
        )
    );

    console.log("Original:", original);
    console.log("Updated:", updated);
}


// ============================================================================
// 21. TESTS
// ============================================================================

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}


function runTests() {
    section("21. Self-Tests");

    const tuple = Object.freeze([1, 2, 3]);

    assert(tuple.length === 3, "length");
    assert(tuple[1] === 2, "indexing");
    assert(tuple.slice(1, 3).join(",") === "2,3", "slicing");

    const [a, b, c] = tuple;

    assert(a === 1, "destructuring a");
    assert(b === 2, "destructuring b");
    assert(c === 3, "destructuring c");

    const coordinate = validateCoordinate([10, 20]);

    assert(coordinate[0] === 10, "coordinate x");
    assert(coordinate[1] === 20, "coordinate y");
    assert(Object.isFrozen(coordinate), "coordinate frozen");

    assert(
        arraysEqual([1, 2], [1, 2]),
        "array content equality"
    );

    assert(
        !arraysEqual([1, 2], [2, 1]),
        "array order sensitivity"
    );

    const processor = new TransactionProcessor();
    processor.addTransaction(["TX1", "A", 100, "INR"]);
    processor.addTransaction(["TX2", "A", -25, "INR"]);

    assert(
        processor.totalsByAccount().get("A") === 75,
        "transaction total"
    );

    console.log("All self-tests passed.");
}


// ============================================================================
// 22. MAIN
// ============================================================================

async function main() {
    basics();
    frozenArrays();
    shallowImmutability();
    destructuring();
    restAndSpread();
    indexingAndSlicing();
    comparison();
    tupleFactoryExample();
    validationExamples();
    mapKeys();
    recordsComparison();
    higherOrderExamples();
    iteratorExamples();
    await asynchronousTupleExample();
    sortingExamples();
    edgeCases();
    performanceExample();
    errorHandling();
    transactionCaseStudy();
    immutableUpdate();
    runTests();
}


main().catch(error => {
    console.error("Fatal error:", error);
    process.exitCode = 1;
});
