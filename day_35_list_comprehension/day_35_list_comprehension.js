"use strict";

/*
 * List Comprehensions in JavaScript
 *
 * JavaScript does not have Python's list-comprehension syntax.
 * Array methods provide the closest native model:
 *
 *   Python [expression for item in iterable if condition]
 *
 *   JavaScript iterable.filter(condition).map(expression)
 *
 * This file focuses on that distinction and builds a practical,
 * event-driven data-processing model using JavaScript-specific behavior.
 */

const printHeading = (title) => {
    console.log(`\n${"=".repeat(72)}\n${title}\n${"=".repeat(72)}`);
};

function basicMapping() {
    printHeading("Mapping: the transformation part of a comprehension");

    const numbers = [1, 2, 3, 4, 5];

    // map() creates a new array and does not mutate the source array.
    const squares = numbers.map((number) => number * number);
    const labels = numbers.map((number) => `item-${number}`);

    console.log("Squares:", squares);
    console.log("Labels:", labels);
}

function filteringAndMapping() {
    printHeading("Filtering followed by transformation");

    const records = [
        { name: "Alice", score: 91, active: true },
        { name: "Bob", score: 42, active: false },
        { name: "Carol", score: 77, active: true },
        { name: "David", score: 35, active: true }
    ];

    // filter() decides which records survive.
    // map() transforms the surviving records.
    const passingActiveNames = records
        .filter((record) => record.active && record.score >= 50)
        .map((record) => record.name);

    console.log("Passing active users:", passingActiveNames);
}

function conditionalTransformation() {
    printHeading("Conditional expressions");

    const scores = [35, 50, 72, 91, 48];

    const labels = scores.map((score) =>
        score >= 50 ? `${score}:pass` : `${score}:fail`
    );

    console.log("Score labels:", labels);
}

function nestedIteration() {
    printHeading("Nested iteration with flatMap()");

    const groups = [
        ["python", "sql"],
        ["javascript", "html"],
        ["cpp", "java"]
    ];

    // flatMap() expresses "transform each group, then flatten one level".
    const flattened = groups.flatMap((group) => group);
    console.log("Flattened values:", flattened);

    const pairs = [1, 2, 3].flatMap((left) =>
        [10, 20, 30].map((right) => ({
            left,
            right,
            product: left * right
        }))
    );

    console.log("Generated pairs:", pairs);
}

function setBasedComprehensionEquivalent() {
    printHeading("Set-style transformation");

    const values = [1, 2, 2, 3, 3, 3, 4];

    // JavaScript Set removes duplicate values after transformation.
    const uniqueSquares = new Set(
        values.map((value) => value * value)
    );

    console.log("Unique squares:", [...uniqueSquares]);
}

function objectProjection() {
    printHeading("Projecting records into objects");

    const products = [
        { name: "Keyboard", price: 79.99, stock: 12 },
        { name: "Monitor", price: 249.5, stock: 7 },
        { name: "Cable", price: 12.75, stock: 18 }
    ];

    const inventoryValues = products.map((product) => ({
        name: product.name,
        inventoryValue: Number(
            (product.price * product.stock).toFixed(2)
        )
    }));

    console.log("Inventory projections:", inventoryValues);
}

function validationPipeline() {
    printHeading("Validation before transformation");

    const input = [
        { name: "Alice", age: 31 },
        { name: "", age: 28 },
        { name: "Bob", age: -2 },
        { name: "Carol", age: 42 },
        { age: 25 }
    ];

    const validNames = input
        .filter((record) =>
            typeof record.name === "string" &&
            record.name.trim().length > 0 &&
            Number.isInteger(record.age) &&
            record.age >= 0 &&
            record.age <= 130
        )
        .map((record) => record.name.trim());

    console.log("Valid names:", validNames);
}

function demonstrateMutationDifference() {
    printHeading("Mutation and side effects");

    const original = [1, 2, 3];

    const mapped = original.map((number) => number * 2);

    console.log("Original:", original);
    console.log("Mapped:", mapped);

    // Array methods normally create new arrays. Mutating an object inside
    // a callback is still possible, but it introduces side effects and
    // can make data-processing pipelines harder to reason about.
    const objects = [{ value: 1 }, { value: 2 }];
    const projected = objects.map((object) => ({
        ...object,
        squared: object.value ** 2
    }));

    console.log("Immutable-style projection:", projected);
    console.log("Original objects remain:", objects);
}

async function demonstrateEventDrivenWorkflow() {
    printHeading("Event-driven processing");

    const events = [
        { type: "created", id: 101 },
        { type: "updated", id: 102 },
        { type: "created", id: 103 },
        { type: "deleted", id: 104 }
    ];

    // JavaScript-specific asynchronous behavior: processing can happen
    // through Promise-based event handlers without blocking the event loop.
    const createdIds = events
        .filter((event) => event.type === "created")
        .map((event) => event.id);

    const processed = await Promise.all(
        createdIds.map(async (id) => ({
            id,
            processedAt: new Date().toISOString()
        }))
    );

    console.log("Asynchronously processed records:", processed);
}

function demonstrateLazyAlternative() {
    printHeading("Lazy alternatives to eager arrays");

    function* squareGenerator(values) {
        for (const value of values) {
            yield value * value;
        }
    }

    const generator = squareGenerator([1, 2, 3, 4]);

    console.log("Generator first value:", generator.next().value);
    console.log("Generator second value:", generator.next().value);

    // A generator avoids allocating the complete transformed array.
    console.log("Remaining values:", [...generator]);
}

function demonstrateSparseArrays() {
    printHeading("Sparse-array behavior");

    const sparse = [];
    sparse[0] = 10;
    sparse[2] = 30;

    // map() skips holes in sparse arrays.
    const mapped = sparse.map((value) => value * 2);

    console.log("Sparse array:", sparse);
    console.log("Mapped sparse array:", mapped);
    console.log("Index 1 exists:", 1 in mapped);
}

function demonstrateErrorHandling() {
    printHeading("Failure handling");

    const records = [
        { name: "Alice", value: 10 },
        { name: "Bob", value: "not-a-number" },
        { name: "Carol", value: 30 }
    ];

    const safeValues = records
        .filter((record) =>
            typeof record.value === "number" &&
            Number.isFinite(record.value)
        )
        .map((record) => record.value * 2);

    console.log("Validated transformed values:", safeValues);

    try {
        const invalid = null;
        invalid.map((value) => value);
    } catch (error) {
        console.log(
            "Expected runtime failure:",
            error instanceof TypeError,
            error.message
        );
    }
}

function demonstratePerformance() {
    printHeading("Performance characteristics");

    const values = Array.from({ length: 100_000 }, (_, index) => index);

    const startMap = performance.now();
    const mapped = values.map((value) => value * 2);
    const mapDuration = performance.now() - startMap;

    const startLoop = performance.now();
    const loopResult = [];
    for (const value of values) {
        loopResult.push(value * 2);
    }
    const loopDuration = performance.now() - startLoop;

    console.log(`map() duration: ${mapDuration.toFixed(3)} ms`);
    console.log(`for...of duration: ${loopDuration.toFixed(3)} ms`);
    console.log("Equivalent first values:", mapped.slice(0, 5));
    console.log("Equivalent result length:", loopResult.length);
}

function demonstrateReadabilityBoundary() {
    printHeading("Readability boundary");

    const values = [1, 2, 3, 4, 5, 6];

    const readablePipeline = values
        .filter((value) => value % 2 === 0)
        .map((value) => value * value);

    console.log("Readable pipeline:", readablePipeline);

    // When processing requires several dependent rules, named functions
    // make the pipeline easier to test than a single dense callback.
    const isEligible = (value) =>
        Number.isInteger(value) && value >= 0 && value <= 100;

    const normalize = (value) => value / 100;

    const normalized = values
        .filter(isEligible)
        .map(normalize);

    console.log("Named-function pipeline:", normalized);
}

async function main() {
    basicMapping();
    filteringAndMapping();
    conditionalTransformation();
    nestedIteration();
    setBasedComprehensionEquivalent();
    objectProjection();
    validationPipeline();
    demonstrateMutationDifference();
    await demonstrateEventDrivenWorkflow();
    demonstrateLazyAlternative();
    demonstrateSparseArrays();
    demonstrateErrorHandling();
    demonstratePerformance();
    demonstrateReadabilityBoundary();
}

main().catch((error) => {
    console.error("Unexpected failure:", error);
    process.exitCode = 1;
});
