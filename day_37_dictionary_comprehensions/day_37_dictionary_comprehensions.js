"use strict";

/*
 * Dictionary comprehensions do not exist as a native JavaScript syntax.
 * JavaScript's closest practical mechanisms are:
 *   - Object.fromEntries()
 *   - Object.entries()
 *   - Object.keys()
 *   - Object.values()
 *   - Map
 *   - Array map/filter pipelines
 *
 * This file demonstrates how those mechanisms express the same
 * transformation ideas while preserving JavaScript-specific behavior.
 */

function heading(title) {
    console.log(`\n${"=".repeat(72)}\n${title}\n${"=".repeat(72)}`);
}

// ---------------------------------------------------------------------------
// Basic object construction
// ---------------------------------------------------------------------------

function basicConstruction() {
    heading("Basic dictionary-comprehension equivalent");

    const numbers = [1, 2, 3, 4, 5];

    // Object.fromEntries() converts [key, value] pairs into an object.
    const squares = Object.fromEntries(
        numbers.map(number => [number, number * number])
    );

    console.log(squares);
}

function transformation() {
    heading("Transforming an object");

    const prices = {
        keyboard: 2499,
        mouse: 1299,
        monitor: 18999,
        headset: 3499
    };

    const discounted = Object.fromEntries(
        Object.entries(prices)
            .map(([product, price]) => [product, Number((price * 0.90).toFixed(2))])
    );

    console.log(discounted);
}

// ---------------------------------------------------------------------------
// Filtering
// ---------------------------------------------------------------------------

function filtering() {
    heading("Filtering object entries");

    const scores = {
        Asha: 91,
        Rahul: 67,
        Meera: 84,
        Vikram: 48
    };

    const passed = Object.fromEntries(
        Object.entries(scores)
            .filter(([, score]) => score >= 50)
    );

    console.log(passed);
}

function conditionalValues() {
    heading("Conditional values");

    const scores = {
        Asha: 91,
        Rahul: 67,
        Meera: 84,
        Vikram: 48
    };

    const statuses = Object.fromEntries(
        Object.entries(scores)
            .map(([student, score]) => [
                student,
                score >= 50 ? "PASS" : "FAIL"
            ])
    );

    console.log(statuses);
}

// ---------------------------------------------------------------------------
// Key transformation
// ---------------------------------------------------------------------------

function keyTransformation() {
    heading("Transforming keys");

    const temperatures = {
        delhi: 31,
        mumbai: 29,
        lucknow: 30
    };

    const normalized = Object.fromEntries(
        Object.entries(temperatures)
            .map(([city, temperature]) => [city.toUpperCase(), temperature])
    );

    console.log(normalized);
}

// ---------------------------------------------------------------------------
// Inversion and duplicate handling
// ---------------------------------------------------------------------------

function invertObject() {
    heading("Inverting an object");

    const countries = {
        India: "IN",
        Japan: "JP",
        Germany: "DE"
    };

    const inverted = Object.fromEntries(
        Object.entries(countries)
            .map(([country, code]) => [code, country])
    );

    console.log(inverted);
}

function duplicateSafeGrouping() {
    heading("Duplicate-safe grouping");

    const employees = {
        Asha: "Engineering",
        Rahul: "Engineering",
        Meera: "Finance"
    };

    const groups = {};

    for (const [employee, department] of Object.entries(employees)) {
        if (!groups[department]) {
            groups[department] = [];
        }

        groups[department].push(employee);
    }

    const normalizedGroups = Object.fromEntries(
        Object.entries(groups).map(([department, people]) => [
            department,
            [...people]
        ])
    );

    console.log(normalizedGroups);
}

// ---------------------------------------------------------------------------
// Map provides behavior closer to arbitrary-key Python dictionaries.
// ---------------------------------------------------------------------------

function mapBasedTransformation() {
    heading("Using Map for dictionary-like behavior");

    const scores = new Map([
        ["Asha", 91],
        ["Rahul", 67],
        ["Meera", 84]
    ]);

    const highScores = new Map(
        [...scores.entries()]
            .filter(([, score]) => score >= 80)
            .map(([student, score]) => [student, score])
    );

    console.log(highScores);
}

// ---------------------------------------------------------------------------
// Nested structures
// ---------------------------------------------------------------------------

function nestedTransformation() {
    heading("Nested object transformation");

    const sales = {
        January: {
            North: 100,
            South: 120,
            West: 90
        },
        February: {
            North: 130,
            South: 110,
            West: 95
        }
    };

    const transformed = Object.fromEntries(
        Object.entries(sales).map(([month, regions]) => [
            month,
            Object.fromEntries(
                Object.entries(regions).map(([region, amount]) => [
                    region,
                    amount * 1000
                ])
            )
        ])
    );

    console.log(transformed);
}

// ---------------------------------------------------------------------------
// Parsing and indexing realistic records
// ---------------------------------------------------------------------------

function parseEmployeeRecords() {
    heading("Parsing and indexing records");

    const rawRecords = [
        "101,Asha,Engineering,95000",
        "102,Rahul,Finance,72000",
        "103,Meera,Engineering,105000"
    ];

    const employees = Object.fromEntries(
        rawRecords.map(record => {
            const fields = record.split(",").map(value => value.trim());

            if (fields.length !== 4) {
                throw new Error(`Invalid employee record: ${record}`);
            }

            const [idText, name, department, salaryText] = fields;
            const id = Number(idText);
            const salary = Number(salaryText);

            if (!Number.isInteger(id) || !Number.isFinite(salary)) {
                throw new Error(`Invalid numeric field: ${record}`);
            }

            return [
                String(id),
                { name, department, salary }
            ];
        })
    );

    const highValue = Object.fromEntries(
        Object.entries(employees)
            .filter(([, employee]) => employee.salary >= 90000)
    );

    console.log(highValue);
}

// ---------------------------------------------------------------------------
// Frequency analysis
// ---------------------------------------------------------------------------

function wordFrequency() {
    heading("Frequency analysis");

    const text = `
        data quality depends on clean data
        clean data supports reliable analysis
        reliable analysis supports reliable decisions
    `;

    const words = text
        .toLowerCase()
        .match(/[a-z]+/g) ?? [];

    const counts = new Map();

    for (const word of words) {
        counts.set(word, (counts.get(word) ?? 0) + 1);
    }

    const repeated = Object.fromEntries(
        [...counts.entries()]
            .filter(([, count]) => count >= 2)
    );

    console.log(repeated);
}

// ---------------------------------------------------------------------------
// Validation and error handling
// ---------------------------------------------------------------------------

function validateNumericObject(data) {
    if (
        data === null ||
        typeof data !== "object" ||
        Array.isArray(data)
    ) {
        throw new TypeError("Expected a plain object.");
    }

    for (const [key, value] of Object.entries(data)) {
        if (typeof key !== "string" || !Number.isInteger(value)) {
            throw new TypeError(`Invalid entry: ${key}=${value}`);
        }
    }
}

function validatedTransformation() {
    heading("Validation before transformation");

    const metrics = {
        orders: 120,
        returns: 7,
        customers: 83
    };

    validateNumericObject(metrics);

    const percentages = Object.fromEntries(
        Object.entries(metrics)
            .map(([key, value]) => [
                key,
                Number((value / 120 * 100).toFixed(2))
            ])
    );

    console.log(percentages);
}

// ---------------------------------------------------------------------------
// Event-driven workflow
// ---------------------------------------------------------------------------

class DataIndex {
    constructor(entries = []) {
        this.data = new Map(entries);
    }

    set(key, value) {
        if (typeof key !== "string" || key.trim() === "") {
            throw new TypeError("Index keys must be non-empty strings.");
        }

        this.data.set(key, value);
    }

    select(predicate) {
        return new DataIndex(
            [...this.data.entries()].filter(predicate)
        );
    }

    transform(transformer) {
        return new DataIndex(
            [...this.data.entries()].map(transformer)
        );
    }

    toObject() {
        return Object.fromEntries(this.data.entries());
    }
}

function eventDrivenIndexWorkflow() {
    heading("Reusable transformation pipeline");

    const index = new DataIndex([
        ["Asha", 91],
        ["Rahul", 67],
        ["Meera", 84],
        ["Vikram", 48]
    ]);

    const result = index
        .select(([, score]) => score >= 70)
        .transform(([name, score]) => [
            name.toUpperCase(),
            score
        ])
        .toObject();

    console.log(result);
}

// ---------------------------------------------------------------------------
// Transaction classification
// ---------------------------------------------------------------------------

function classifyTransactions() {
    heading("Conditional classification");

    const transactions = {
        TX1001: 450,
        TX1002: 17500,
        TX1003: 89000,
        TX1004: -250,
        TX1005: 6200
    };

    const classification = Object.fromEntries(
        Object.entries(transactions).map(([id, amount]) => {
            const category =
                amount < 0 ? "invalid" :
                amount >= 50000 ? "high" :
                amount >= 10000 ? "medium" :
                "low";

            return [id, category];
        })
    );

    console.log(classification);
}

// ---------------------------------------------------------------------------
// Domain-specific indexing
// ---------------------------------------------------------------------------

function operationalReport() {
    heading("Operational report");

    const metrics = {
        ordersProcessed: 12450,
        ordersFailed: 137,
        ordersDelayed: 421,
        refunds: 82
    };

    if (metrics.ordersProcessed <= 0) {
        throw new RangeError("Processed orders must be positive.");
    }

    const rates = Object.fromEntries(
        Object.entries(metrics)
            .filter(([key]) => key !== "ordersProcessed")
            .map(([metric, value]) => [
                metric,
                Number((value / metrics.ordersProcessed * 100).toFixed(2))
            ])
    );

    const alerts = Object.fromEntries(
        Object.entries(rates)
            .filter(([, rate]) => rate >= 3)
    );

    console.log({
        rates,
        alerts,
        alertCount: Object.keys(alerts).length
    });
}

// ---------------------------------------------------------------------------
// Performance and memory discussion through executable comparison
// ---------------------------------------------------------------------------

function performanceComparison() {
    heading("Transformation performance");

    const values = Array.from({ length: 100_000 }, (_, index) => index + 1);

    const startMap = performance.now();

    const viaPipeline = Object.fromEntries(
        values.map(value => [value, value * value])
    );

    const mapDuration = performance.now() - startMap;

    const startLoop = performance.now();

    const viaLoop = {};
    for (const value of values) {
        viaLoop[value] = value * value;
    }

    const loopDuration = performance.now() - startLoop;

    console.log(`Object.fromEntries pipeline: ${mapDuration.toFixed(3)} ms`);
    console.log(`Explicit loop:               ${loopDuration.toFixed(3)} ms`);
    console.log(
        "Equivalent first value:",
        viaPipeline[1] === viaLoop[1]
    );

    /*
     * Both approaches materialize the entire object.
     * For large datasets, retaining every intermediate array produced by
     * map/filter can increase memory pressure. An explicit loop can process
     * records without creating those intermediate arrays.
     */
}

// ---------------------------------------------------------------------------
// Common semantic edge cases
// ---------------------------------------------------------------------------

function edgeCases() {
    heading("Edge cases");

    const duplicateKeyPairs = [
        ["status", "draft"],
        ["status", "approved"]
    ];

    const duplicateResult = Object.fromEntries(duplicateKeyPairs);

    // The last duplicate key wins.
    console.log("Duplicate key:", duplicateResult);

    const emptyResult = Object.fromEntries(
        Object.entries({ a: 1, b: 2 })
            .filter(([, value]) => value > 100)
    );

    console.log("Empty result:", emptyResult);

    const nullSafe = Object.fromEntries(
        Object.entries({
            first: null,
            second: 20,
            third: undefined
        }).map(([key, value]) => [
            key,
            value ?? 0
        ])
    );

    console.log("Null-normalized:", nullSafe);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
    basicConstruction();
    transformation();
    filtering();
    conditionalValues();
    keyTransformation();
    invertObject();
    duplicateSafeGrouping();
    mapBasedTransformation();
    nestedTransformation();
    parseEmployeeRecords();
    wordFrequency();
    validatedTransformation();
    eventDrivenIndexWorkflow();
    classifyTransactions();
    operationalReport();
    performanceComparison();
    edgeCases();
}

main();
