"use strict";

/*
 * Set Comprehensions in JavaScript
 *
 * JavaScript does not have Python's native set-comprehension syntax.
 * The closest idiomatic representation is a Set constructed from an
 * iterable, often using Array.from(), map(), filter(), and a Set.
 *
 * This file therefore focuses on the semantics that set comprehensions
 * provide: transformation, filtering, uniqueness, nested iteration,
 * membership, relational operations, validation, and practical data
 * processing.
 */

function heading(title) {
    console.log(`\n${"=".repeat(72)}\n${title}\n${"=".repeat(72)}`);
}

function setFrom(iterable) {
    return new Set(iterable);
}

function sortedValues(set) {
    return [...set].sort((a, b) => {
        if (typeof a === "number" && typeof b === "number") {
            return a - b;
        }
        return String(a).localeCompare(String(b));
    });
}

function demonstrateBasicSets() {
    heading("Basic Set Construction");

    const numbers = [1, 2, 2, 3, 4, 4, 5];

    const squares = setFrom(numbers.map(number => number * number));
    const evenNumbers = setFrom(
        numbers.filter(number => number % 2 === 0)
    );

    console.log("Squares:", sortedValues(squares));
    console.log("Even numbers:", sortedValues(evenNumbers));

    // Set construction removes duplicate values automatically.
    const languages = setFrom(
        ["Python", "python", "SQL", "sql", "Java"]
            .map(language => language.toLowerCase())
    );

    console.log("Normalized languages:", sortedValues(languages));
}

function demonstrateFilteringAndTransformation() {
    heading("Filtering and Transformation");

    const transactions = [
        { account: "A100", amount: 2500 },
        { account: "A101", amount: 750 },
        { account: "A100", amount: 1250 },
        { account: "A102", amount: 4000 },
        { account: "A103", amount: -50 }
    ];

    const highValueAccounts = setFrom(
        transactions
            .filter(transaction => transaction.amount >= 2000)
            .map(transaction => transaction.account)
    );

    const positiveAmounts = setFrom(
        transactions
            .filter(transaction => transaction.amount > 0)
            .map(transaction => transaction.amount)
    );

    console.log("High-value accounts:", sortedValues(highValueAccounts));
    console.log("Positive amounts:", sortedValues(positiveAmounts));
}

function demonstrateNestedIteration() {
    heading("Nested Iteration");

    const letters = ["A", "B"];
    const numbers = [1, 2, 3];
    const combinations = new Set();

    // JavaScript requires explicit iteration where Python can express the
    // same operation with multiple `for` clauses in a set comprehension.
    for (const letter of letters) {
        for (const number of numbers) {
            combinations.add(`${letter}${number}`);
        }
    }

    console.log("Cartesian combinations:", sortedValues(combinations));

    const coordinates = new Set();

    for (let x = 0; x < 3; x += 1) {
        for (let y = 0; y < 3; y += 1) {
            if (x !== y) {
                coordinates.add(`${x},${y}`);
            }
        }
    }

    console.log("Distinct coordinate pairs:", sortedValues(coordinates));
}

function demonstrateSetAlgebra() {
    heading("Set Algebra");

    const requested = new Set(["read", "write", "delete", "audit"]);
    const granted = new Set(["read", "write", "audit"]);

    const missing = new Set(
        [...requested].filter(permission => !granted.has(permission))
    );

    const active = new Set(
        [...requested].filter(permission => granted.has(permission))
    );

    console.log("Missing:", sortedValues(missing));
    console.log("Intersection:", sortedValues(active));
}

function demonstrateStructuredRecords() {
    heading("Structured Records");

    const users = [
        {
            username: "anita",
            roles: new Set(["reader", "analyst"]),
            active: true
        },
        {
            username: "rahul",
            roles: new Set(["admin", "reader"]),
            active: true
        },
        {
            username: "meera",
            roles: new Set(["reader"]),
            active: false
        },
        {
            username: "vikas",
            roles: new Set(["analyst", "auditor"]),
            active: true
        }
    ];

    const activeUsers = setFrom(
        users
            .filter(user => user.active)
            .map(user => user.username)
    );

    const analysts = setFrom(
        users
            .filter(user => user.active && user.roles.has("analyst"))
            .map(user => user.username)
    );

    const activeRoles = new Set();

    for (const user of users) {
        if (user.active) {
            for (const role of user.roles) {
                activeRoles.add(role);
            }
        }
    }

    console.log("Active users:", sortedValues(activeUsers));
    console.log("Active analysts:", sortedValues(analysts));
    console.log("Active roles:", sortedValues(activeRoles));
}

function demonstrateStringProcessing() {
    heading("String Processing");

    const sentence =
        "Set constructions remove repeated values while transforming data.";

    const words = setFrom(
        sentence
            .split(/\s+/)
            .map(word => word.replace(/[.,!?]/g, "").toLowerCase())
            .filter(Boolean)
    );

    const vowels = setFrom(
        [...sentence.toLowerCase()].filter(character =>
            "aeiou".includes(character)
        )
    );

    console.log("Unique words:", sortedValues(words));
    console.log("Vowels:", sortedValues(vowels));
}

function demonstrateDataValidation() {
    heading("Validation");

    const values = [10, "20", 30, null, true, 10];

    // Number.isInteger() excludes strings and booleans.
    const integers = setFrom(
        values.filter(value => Number.isInteger(value))
    );

    const normalizedStrings = setFrom(
        values
            .filter(value => typeof value === "string")
            .map(value => value.toLowerCase())
    );

    console.log("Valid integers:", sortedValues(integers));
    console.log("Normalized strings:", sortedValues(normalizedStrings));
}

function demonstrateObjectIdentity() {
    heading("Object Identity and Uniqueness");

    const records = [
        { id: 1, name: "A" },
        { id: 1, name: "A" },
        { id: 2, name: "B" }
    ];

    // JavaScript Sets compare objects by identity, not structural equality.
    const objectSet = new Set(records);
    const uniqueIds = setFrom(records.map(record => record.id));

    console.log("Object references retained:", objectSet.size);
    console.log("Unique logical IDs:", sortedValues(uniqueIds));
}

function demonstratePermissionExpansion() {
    heading("Permission Expansion");

    const accounts = new Map([
        ["finance", new Set(["read", "write", "approve"])],
        ["analytics", new Set(["read", "export"])],
        ["support", new Set(["read", "comment"])],
        ["guest", new Set(["read"])]
    ]);

    const eligibleRoles = new Set();

    for (const [role, permissions] of accounts) {
        if (permissions.has("read") && permissions.has("approve")) {
            eligibleRoles.add(role);
        }
    }

    const elevatedPermissions = new Set();

    for (const permissions of accounts.values()) {
        for (const permission of permissions) {
            if (["write", "approve", "export"].includes(permission)) {
                elevatedPermissions.add(permission);
            }
        }
    }

    console.log("Approval-capable roles:", sortedValues(eligibleRoles));
    console.log("Elevated permissions:", sortedValues(elevatedPermissions));
}

function demonstrateGeneratorSemantics() {
    heading("Lazy Iteration versus Materialized Sets");

    function* doubledEvenNumbers(limit) {
        for (let number = 0; number <= limit; number += 1) {
            if (number % 2 === 0) {
                yield number * 2;
            }
        }
    }

    const lazyValues = doubledEvenNumbers(10);
    const materialized = new Set(lazyValues);

    console.log("Materialized unique values:", sortedValues(materialized));

    // Generators are lazy. Set construction consumes the generator and
    // materializes its unique values in memory.
}

function demonstratePerformance() {
    heading("Performance Characteristics");

    const values = Array.from({ length: 100000 }, (_, index) => index);

    const start = performance.now();

    const selected = new Set(
        values
            .filter(value => value % 3 === 0)
            .map(value => value * 2)
    );

    const elapsed = performance.now() - start;

    console.log("Unique results:", selected.size);
    console.log(`Transformation time: ${elapsed.toFixed(3)} ms`);

    // Set.has() is designed for efficient membership testing and avoids
    // repeatedly scanning an array with includes() for large collections.
    const probes = new Set(values);
    let found = 0;

    for (let value = 0; value < 100000; value += 10000) {
        if (probes.has(value)) {
            found += 1;
        }
    }

    console.log("Successful membership probes:", found);
}

function demonstrateRealisticWorkflow() {
    heading("Realistic Data-Cleaning Workflow");

    const rawEmails = [
        " Alice@example.com ",
        "alice@example.com",
        "BOB@example.com",
        " bob@example.com ",
        "",
        "invalid-address",
        "carol@example.org"
    ];

    const normalizedEmails = new Set();

    for (const rawEmail of rawEmails) {
        const email = rawEmail.trim().toLowerCase();

        if (
            email.includes("@") &&
            email.split("@").length === 2 &&
            email.split("@")[1].includes(".")
        ) {
            normalizedEmails.add(email);
        }
    }

    console.log("Unique normalized emails:");
    for (const email of [...normalizedEmails].sort()) {
        console.log(`  ${email}`);
    }
}

function main() {
    demonstrateBasicSets();
    demonstrateFilteringAndTransformation();
    demonstrateNestedIteration();
    demonstrateSetAlgebra();
    demonstrateStructuredRecords();
    demonstrateStringProcessing();
    demonstrateDataValidation();
    demonstrateObjectIdentity();
    demonstratePermissionExpansion();
    demonstrateGeneratorSemantics();
    demonstratePerformance();
    demonstrateRealisticWorkflow();
}

main();
