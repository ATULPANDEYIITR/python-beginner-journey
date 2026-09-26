"use strict";

/*
 * SET OPERATIONS IN JAVASCRIPT
 * =============================
 *
 * Self-contained executable study file.
 * Run with:
 *     node set_operations.js
 *
 * JavaScript Set is a collection of unique values. It is useful for
 * membership testing, deduplication, set-like operations, graph traversal,
 * permissions, data reconciliation, and indexing.
 */

// ============================================================================
// 1. FUNDAMENTALS
// ============================================================================

function fundamentals() {
    console.log("\n" + "=".repeat(78));
    console.log("1. FUNDAMENTALS");
    console.log("=".repeat(78));

    const numbers = new Set([1, 2, 3, 3, 2, 1]);

    console.log("Unique values:", numbers);
    console.log("Size:", numbers.size);

    // JavaScript Set uses has() for membership testing.
    console.log("Has 2:", numbers.has(2));
    console.log("Has 99:", numbers.has(99));

    // Set has no index-based access. Convert to an array when positional
    // access is actually required.
    console.log("First element through iterator:", numbers.values().next().value);

    const emptySet = new Set();
    console.log("Empty set:", emptySet);

    // JavaScript Set can contain objects because object identity is used.
    const firstObject = { id: 1 };
    const secondObject = { id: 1 };
    const objectSet = new Set([firstObject, secondObject]);

    console.log("Two different objects:", objectSet.size);
    console.log("Same object reference:", objectSet.has(firstObject));
}

// ============================================================================
// 2. ADDING, DELETING, AND CLEARING
// ============================================================================

function mutationOperations() {
    console.log("\n" + "=".repeat(78));
    console.log("2. MUTATION OPERATIONS");
    console.log("=".repeat(78));

    const values = new Set([1, 2, 3]);

    values.add(4);
    values.add(4); // Adding an existing value does not create a duplicate.

    console.log("After add:", values);

    values.delete(2);
    console.log("After delete:", values);

    // delete() returns true when an element existed and was removed.
    console.log("Delete missing element:", values.delete(999));

    values.clear();
    console.log("After clear:", values);
}

// ============================================================================
// 3. ITERATION
// ============================================================================

function iterationExamples() {
    console.log("\n" + "=".repeat(78));
    console.log("3. ITERATION");
    console.log("=".repeat(78));

    const values = new Set(["alpha", "beta", "gamma"]);

    for (const value of values) {
        console.log("for...of:", value);
    }

    values.forEach((value) => {
        console.log("forEach:", value);
    });

    console.log("Array conversion:", [...values]);
}

// ============================================================================
// 4. SET-LIKE MATHEMATICAL OPERATIONS
// ============================================================================

function union(first, second) {
    return new Set([...first, ...second]);
}

function intersection(first, second) {
    // Iterate through the smaller set when possible.
    const [smaller, larger] =
        first.size <= second.size ? [first, second] : [second, first];

    return new Set([...smaller].filter((value) => larger.has(value)));
}

function difference(first, second) {
    return new Set([...first].filter((value) => !second.has(value)));
}

function symmetricDifference(first, second) {
    return new Set([
        ...[...first].filter((value) => !second.has(value)),
        ...[...second].filter((value) => !first.has(value)),
    ]);
}

function mathematicalOperations() {
    console.log("\n" + "=".repeat(78));
    console.log("4. MATHEMATICAL SET OPERATIONS");
    console.log("=".repeat(78));

    const A = new Set([1, 2, 3, 4]);
    const B = new Set([3, 4, 5, 6]);

    console.log("A:", A);
    console.log("B:", B);
    console.log("Union:", union(A, B));
    console.log("Intersection:", intersection(A, B));
    console.log("A - B:", difference(A, B));
    console.log("B - A:", difference(B, A));
    console.log("Symmetric difference:", symmetricDifference(A, B));
}

// ============================================================================
// 5. SUBSET, SUPERSET, AND DISJOINTNESS
// ============================================================================

function isSubset(subset, superset) {
    for (const value of subset) {
        if (!superset.has(value)) {
            return false;
        }
    }
    return true;
}

function isDisjoint(first, second) {
    const [smaller, larger] =
        first.size <= second.size ? [first, second] : [second, first];

    for (const value of smaller) {
        if (larger.has(value)) {
            return false;
        }
    }

    return true;
}

function relationExamples() {
    console.log("\n" + "=".repeat(78));
    console.log("5. SET RELATIONS");
    console.log("=".repeat(78));

    const A = new Set([1, 2]);
    const B = new Set([1, 2, 3]);
    const C = new Set([8, 9]);

    console.log("A subset of B:", isSubset(A, B));
    console.log("B subset of A:", isSubset(B, A));
    console.log("A and C disjoint:", isDisjoint(A, C));
}

// ============================================================================
// 6. DEDUPLICATION
// ============================================================================

function deduplicationExamples() {
    console.log("\n" + "=".repeat(78));
    console.log("6. DEDUPLICATION");
    console.log("=".repeat(78));

    const input = [4, 2, 4, 1, 2, 3, 1];

    const unique = [...new Set(input)];

    console.log("Input:", input);
    console.log("Unique values:", unique);

    const emails = [
        "Alice@example.com",
        "alice@example.com",
        "bob@example.com",
        " BOB@example.com ",
    ];

    // Normalization is required when values that differ only in formatting
    // should be treated as the same logical entity.
    const normalizedEmails = new Set(
        emails.map((email) => email.trim().toLowerCase())
    );

    console.log("Normalized unique emails:", [...normalizedEmails]);
}

// ============================================================================
// 7. EDGE CASES AND JAVASCRIPT EQUALITY
// ============================================================================

function edgeCases() {
    console.log("\n" + "=".repeat(78));
    console.log("7. EDGE CASES AND EQUALITY");
    console.log("=".repeat(78));

    // Set uses SameValueZero-style equality:
    // NaN matches NaN, and +0 and -0 are considered the same value.
    const specialValues = new Set([NaN, NaN, +0, -0]);

    console.log("Special value count:", specialValues.size);
    console.log("Contains NaN:", specialValues.has(NaN));
    console.log("Contains -0:", specialValues.has(-0));

    // Objects are compared by reference, not by their contents.
    const objectA = { name: "Atul" };
    const objectB = { name: "Atul" };
    const objects = new Set([objectA, objectB]);

    console.log("Equal-looking objects stored separately:", objects.size);
    console.log("objectA found:", objects.has(objectA));
    console.log("New equivalent object found:", objects.has({ name: "Atul" }));
}

// ============================================================================
// 8. MULTISET LIMITATION
// ============================================================================

function frequencyMap(values) {
    const counts = new Map();

    for (const value of values) {
        counts.set(value, (counts.get(value) ?? 0) + 1);
    }

    return counts;
}

function multisetDifference(first, second) {
    const firstCounts = frequencyMap(first);
    const secondCounts = frequencyMap(second);
    const result = [];

    for (const [value, count] of firstCounts) {
        const remaining = count - (secondCounts.get(value) ?? 0);

        for (let i = 0; i < Math.max(0, remaining); i += 1) {
            result.push(value);
        }
    }

    return result;
}

function multisetExample() {
    console.log("\n" + "=".repeat(78));
    console.log("8. MULTISET LIMITATION");
    console.log("=".repeat(78));

    const first = ["a", "a", "a", "b", "c"];
    const second = ["a", "b"];

    console.log("Ordinary Set:", new Set(first));
    console.log("Frequency map:", frequencyMap(first));
    console.log("Multiset difference:", multisetDifference(first, second));
}

// ============================================================================
// 9. PERMISSIONS SYSTEM
// ============================================================================

function permissionSystem() {
    console.log("\n" + "=".repeat(78));
    console.log("9. PERMISSION SYSTEM");
    console.log("=".repeat(78));

    const required = new Set(["read", "write"]);
    const granted = new Set(["read", "write", "analytics"]);

    const authorized = isSubset(required, granted);
    const extra = difference(granted, required);
    const missing = difference(required, granted);

    console.log("Authorized:", authorized);
    console.log("Extra permissions:", extra);
    console.log("Missing permissions:", missing);
}

// ============================================================================
// 10. SEARCH INDEX
// ============================================================================

function buildInvertedIndex(documents) {
    const index = new Map();

    for (const [documentId, text] of Object.entries(documents)) {
        const words = new Set(
            text
                .toLowerCase()
                .split(/\s+/)
                .map((word) => word.replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, ""))
                .filter(Boolean)
        );

        for (const word of words) {
            if (!index.has(word)) {
                index.set(word, new Set());
            }

            index.get(word).add(documentId);
        }
    }

    return index;
}

function searchIndex(index, requiredTerms) {
    if (requiredTerms.length === 0) {
        return new Set();
    }

    const normalizedTerms = requiredTerms.map((term) => term.toLowerCase());

    let result = new Set(index.get(normalizedTerms[0]) ?? []);

    for (const term of normalizedTerms.slice(1)) {
        result = intersection(result, index.get(term) ?? new Set());
    }

    return result;
}

function searchExample() {
    console.log("\n" + "=".repeat(78));
    console.log("10. INVERTED INDEX");
    console.log("=".repeat(78));

    const documents = {
        doc1: "JavaScript supports Set operations and Map structures.",
        doc2: "Set operations are useful for data processing.",
        doc3: "JavaScript data structures include arrays sets and maps.",
    };

    const index = buildInvertedIndex(documents);

    console.log("Documents containing set:", index.get("set"));
    console.log(
        "Documents containing set and operations:",
        searchIndex(index, ["set", "operations"])
    );
}

// ============================================================================
// 11. GRAPH TRAVERSAL
// ============================================================================

function breadthFirstSearch(graph, start) {
    const visited = new Set();
    const queue = [start];
    let index = 0;

    while (index < queue.length) {
        const vertex = queue[index];
        index += 1;

        if (visited.has(vertex)) {
            continue;
        }

        visited.add(vertex);

        for (const neighbor of graph.get(vertex) ?? []) {
            if (!visited.has(neighbor)) {
                queue.push(neighbor);
            }
        }
    }

    return visited;
}

function graphExample() {
    console.log("\n" + "=".repeat(78));
    console.log("11. GRAPH APPLICATION");
    console.log("=".repeat(78));

    const graph = new Map([
        ["A", new Set(["B", "C"])],
        ["B", new Set(["A", "C", "D"])],
        ["C", new Set(["A", "B"])],
        ["D", new Set(["B"])],
    ]);

    console.log("Common neighbors A/B:", intersection(graph.get("A"), graph.get("B")));
    console.log("Reachable from A:", breadthFirstSearch(graph, "A"));
}

// ============================================================================
// 12. DATA RECONCILIATION
// ============================================================================

function reconciliation() {
    console.log("\n" + "=".repeat(78));
    console.log("12. DATA RECONCILIATION");
    console.log("=".repeat(78));

    const databaseIds = new Set([101, 102, 103, 104, 105]);
    const apiIds = new Set([103, 104, 105, 106, 107]);

    console.log("Common:", intersection(databaseIds, apiIds));
    console.log("Only database:", difference(databaseIds, apiIds));
    console.log("Only API:", difference(apiIds, databaseIds));
    console.log("All IDs:", union(databaseIds, apiIds));
}

// ============================================================================
// 13. ASYNCHRONOUS SET PROCESSING
// ============================================================================

function delay(milliseconds) {
    return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function asynchronousProcessing() {
    console.log("\n" + "=".repeat(78));
    console.log("13. ASYNCHRONOUS PROCESSING");
    console.log("=".repeat(78));

    const pendingJobs = new Set(["job-101", "job-102", "job-103"]);

    console.log("Pending jobs:", pendingJobs);

    // The Set tracks state while asynchronous work occurs.
    for (const job of [...pendingJobs]) {
        await delay(5);
        pendingJobs.delete(job);
        console.log(`Completed ${job}; remaining:`, pendingJobs.size);
    }
}

// ============================================================================
// 14. PERFORMANCE AND DESIGN NOTES
// ============================================================================

function performanceNotes() {
    console.log("\n" + "=".repeat(78));
    console.log("14. PERFORMANCE AND DESIGN NOTES");
    console.log("=".repeat(78));

    const largeArray = Array.from({ length: 100_000 }, (_, index) => index);
    const largeSet = new Set(largeArray);
    const target = 99_999;

    console.time("Array membership");
    largeArray.includes(target);
    console.timeEnd("Array membership");

    console.time("Set membership");
    largeSet.has(target);
    console.timeEnd("Set membership");

    console.log("Typical Set membership is average O(1).");
    console.log("Array includes() is O(n) in the general case.");
    console.log("Set construction costs O(n) for n input elements.");
    console.log("Set consumes memory for its hash/collection structure.");
}

// ============================================================================
// 15. ERROR HANDLING AND VALIDATION
// ============================================================================

function validateSet(value, name = "value") {
    if (!(value instanceof Set)) {
        throw new TypeError(`${name} must be a Set`);
    }

    return true;
}

function safeIntersection(first, second) {
    validateSet(first, "first");
    validateSet(second, "second");
    return intersection(first, second);
}

function validationExample() {
    console.log("\n" + "=".repeat(78));
    console.log("15. ERROR HANDLING AND VALIDATION");
    console.log("=".repeat(78));

    try {
        safeIntersection(new Set([1, 2]), [2, 3]);
    } catch (error) {
        console.log("Validation error:", error.message);
    }

    console.log(
        "Valid intersection:",
        safeIntersection(new Set([1, 2]), new Set([2, 3]))
    );
}

// ============================================================================
// 16. TESTS
// ============================================================================

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function runTests() {
    console.log("\n" + "=".repeat(78));
    console.log("16. SELF-TESTS");
    console.log("=".repeat(78));

    const A = new Set([1, 2, 3]);
    const B = new Set([3, 4, 5]);

    assert(
        [...union(A, B)].sort((a, b) => a - b).join(",") === "1,2,3,4,5",
        "union"
    );

    assert(
        [...intersection(A, B)].join(",") === "3",
        "intersection"
    );

    assert(
        [...difference(A, B)].sort((a, b) => a - b).join(",") === "1,2",
        "difference"
    );

    assert(
        [...symmetricDifference(A, B)]
            .sort((a, b) => a - b)
            .join(",") === "1,2,4,5",
        "symmetric difference"
    );

    assert(isSubset(new Set([1, 2]), A), "subset");
    assert(isDisjoint(A, new Set([8, 9])), "disjointness");

    assert(
        JSON.stringify([...new Set([1, 2, 1, 3])]) === JSON.stringify([1, 2, 3]),
        "deduplication"
    );

    assert(
        [...new Set([NaN, NaN])].length === 1,
        "NaN uniqueness"
    );

    console.log("All tests passed.");
}

// ============================================================================
// 17. MAIN
// ============================================================================

async function main() {
    console.log("=".repeat(78));
    console.log("SET OPERATIONS IN JAVASCRIPT: BEGINNER TO ADVANCED");
    console.log("=".repeat(78));

    fundamentals();
    mutationOperations();
    iterationExamples();
    mathematicalOperations();
    relationExamples();
    deduplicationExamples();
    edgeCases();
    multisetExample();
    permissionSystem();
    searchExample();
    graphExample();
    reconciliation();
    await asynchronousProcessing();
    performanceNotes();
    validationExample();
    runTests();

    console.log("\n" + "=".repeat(78));
    console.log("END OF SET OPERATIONS STUDY FILE");
    console.log("=".repeat(78));
}

main().catch((error) => {
    console.error("Program failed:", error);
    process.exitCode = 1;
});
