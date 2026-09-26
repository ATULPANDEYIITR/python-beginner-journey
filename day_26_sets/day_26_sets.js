/*
 * SETS IN JAVASCRIPT
 *
 * A comprehensive executable study file covering Set fundamentals,
 * uniqueness, membership, mutation, set algebra, algorithms, edge cases,
 * object identity, performance, practical applications, and advanced
 * JavaScript-specific behavior.
 *
 * Run with:
 *     node sets_comprehensive.js
 */

"use strict";

// ============================================================================
// 1. BASIC SET FUNDAMENTALS
// ============================================================================

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function basicSets() {
    section("1. SET FUNDAMENTALS");

    // Set stores unique values.
    const numbers = new Set([1, 2, 3, 3, 4, 4]);

    console.log("Set:", numbers);
    console.log("Size:", numbers.size);
    console.log("Has 3:", numbers.has(3));
    console.log("Has 99:", numbers.has(99));

    // An empty Set requires new Set().
    const emptySet = new Set();
    console.log("Empty Set:", emptySet);

    // A string is iterable, so each character becomes an element.
    console.log("Characters:", new Set("banana"));
}


// ============================================================================
// 2. ADD, DELETE, CLEAR
// ============================================================================

function mutation() {
    section("2. SET MUTATION");

    const languages = new Set();

    // add() returns the Set, allowing chaining.
    languages
        .add("Python")
        .add("JavaScript")
        .add("C++")
        .add("Python");

    console.log("Languages:", languages);

    // Duplicate insertion does not increase size.
    console.log("Size after duplicate:", languages.size);

    // delete() returns true if an element existed and was removed.
    console.log("Deleted C++:", languages.delete("C++"));
    console.log("Deleted Rust:", languages.delete("Rust"));

    console.log("Remaining:", languages);

    languages.clear();
    console.log("After clear:", languages);
}


// ============================================================================
// 3. ITERATION
// ============================================================================

function iteration() {
    section("3. ITERATION");

    const values = new Set([10, 20, 30, 40]);

    values.forEach((value) => {
        console.log("forEach:", value);
    });

    for (const value of values) {
        console.log("for...of:", value);
    }

    console.log("Array conversion:", [...values]);
}


// ============================================================================
// 4. SET ORDER
// ============================================================================

function insertionOrder() {
    section("4. INSERTION ORDER");

    // JavaScript Set iteration follows insertion order.
    const values = new Set();

    values.add("third");
    values.add("first");
    values.add("second");
    values.add("first");

    console.log([...values]);

    console.log(
        "JavaScript Set preserves insertion order during iteration, "
        + "but it does not provide numeric indexing like an Array."
    );
}


// ============================================================================
// 5. SET ALGEBRA
// ============================================================================

function setAlgebra() {
    section("5. SET ALGEBRA");

    const first = new Set([1, 2, 3, 4]);
    const second = new Set([3, 4, 5, 6]);

    // Modern JavaScript runtimes provide these Set methods.
    console.log("Union:", first.union(second));
    console.log("Intersection:", first.intersection(second));
    console.log("Difference:", first.difference(second));
    console.log("Symmetric difference:", first.symmetricDifference(second));

    console.log("Subset:", new Set([1, 2]).isSubsetOf(first));
    console.log("Superset:", first.isSupersetOf(new Set([1, 2])));
    console.log("Disjoint:", first.isDisjointFrom(new Set([10, 11])));
}


// ============================================================================
// 6. COMPATIBILITY FALLBACK IMPLEMENTATIONS
// ============================================================================

function union(a, b) {
    return new Set([...a, ...b]);
}

function intersection(a, b) {
    return new Set([...a].filter((value) => b.has(value)));
}

function difference(a, b) {
    return new Set([...a].filter((value) => !b.has(value)));
}

function symmetricDifference(a, b) {
    return new Set([
        ...[...a].filter((value) => !b.has(value)),
        ...[...b].filter((value) => !a.has(value)),
    ]);
}

function isSubset(a, b) {
    for (const value of a) {
        if (!b.has(value)) {
            return false;
        }
    }
    return true;
}

function isDisjoint(a, b) {
    const smaller = a.size <= b.size ? a : b;
    const larger = smaller === a ? b : a;

    for (const value of smaller) {
        if (larger.has(value)) {
            return false;
        }
    }

    return true;
}

function algebraFallbacks() {
    section("6. SET ALGEBRA IMPLEMENTED MANUALLY");

    const a = new Set([1, 2, 3]);
    const b = new Set([3, 4, 5]);

    console.log("Union:", union(a, b));
    console.log("Intersection:", intersection(a, b));
    console.log("Difference:", difference(a, b));
    console.log("Symmetric difference:", symmetricDifference(a, b));
    console.log("Subset:", isSubset(new Set([1, 2]), a));
    console.log("Disjoint:", isDisjoint(a, new Set([10, 11])));
}


// ============================================================================
// 7. DEDUPLICATION
// ============================================================================

function deduplication() {
    section("7. DEDUPLICATION");

    const emails = [
        "alice@example.com",
        "bob@example.com",
        "alice@example.com",
        "carol@example.com",
        "bob@example.com",
    ];

    const uniqueEmails = [...new Set(emails)];

    console.log("Original:", emails);
    console.log("Unique:", uniqueEmails);
}


// ============================================================================
// 8. SETS OF OBJECTS
// ============================================================================

function objectIdentity() {
    section("8. SETS AND OBJECT IDENTITY");

    const firstUser = { id: 1, name: "Alice" };
    const secondUser = { id: 1, name: "Alice" };

    // Objects are compared by reference, not structural content.
    const users = new Set([firstUser, secondUser, firstUser]);

    console.log("Set size:", users.size);
    console.log("Same object:", firstUser === secondUser);
    console.log("Same reference:", users.has(firstUser));

    // Structural deduplication requires an explicit key.
    const records = [
        { id: 1, name: "Alice" },
        { id: 1, name: "Alice" },
        { id: 2, name: "Bob" },
    ];

    const uniqueById = new Map(
        records.map((record) => [record.id, record])
    );

    console.log("Unique records by ID:", [...uniqueById.values()]);
}


// ============================================================================
// 9. SPECIAL VALUES
// ============================================================================

function specialValues() {
    section("9. SPECIAL VALUES");

    const values = new Set([
        NaN,
        NaN,
        0,
        -0,
        undefined,
        null,
    ]);

    // Set uses SameValueZero equality:
    // NaN equals NaN for membership purposes, and +0/-0 are equivalent.
    console.log("Set:", values);
    console.log("Has NaN:", values.has(NaN));
    console.log("Has 0:", values.has(0));
    console.log("Has -0:", values.has(-0));
}


// ============================================================================
// 10. SET COMPOSITION
// ============================================================================

function composeSetOperations() {
    section("10. COMPOSING SET OPERATIONS");

    const requested = new Set([
        "authentication",
        "authorization",
        "encryption",
    ]);

    const supported = new Set([
        "authentication",
        "authorization",
        "logging",
        "monitoring",
    ]);

    const missing = difference(requested, supported);
    const unused = difference(supported, requested);

    console.log("Missing capabilities:", missing);
    console.log("Supported but not requested:", unused);
    console.log("Compatible:", missing.size === 0);
}


// ============================================================================
// 11. TAG FILTERING
// ============================================================================

function tagFiltering() {
    section("11. TAG FILTERING");

    const articles = [
        {
            title: "Python Algorithms",
            tags: new Set(["python", "algorithms"]),
        },
        {
            title: "JavaScript Web APIs",
            tags: new Set(["javascript", "web"]),
        },
        {
            title: "Python Data Structures",
            tags: new Set(["python", "data"]),
        },
    ];

    const requiredTags = new Set(["python"]);

    const matching = articles.filter((article) =>
        isSubset(requiredTags, article.tags)
    );

    console.log(
        "Matching articles:",
        matching.map((article) => article.title)
    );
}


// ============================================================================
// 12. PERMISSION SYSTEM
// ============================================================================

function permissionSystem() {
    section("12. PERMISSION SYSTEM");

    const required = new Set(["read", "download"]);
    const granted = new Set(["read", "write", "download"]);

    const missing = difference(required, granted);

    console.log("Missing:", missing);
    console.log("Access granted:", missing.size === 0);
}


// ============================================================================
// 13. EVENT ANALYSIS
// ============================================================================

function eventAnalysis() {
    section("13. EVENT STREAM ANALYSIS");

    const events = [
        ["alice", "login"],
        ["bob", "login"],
        ["alice", "download"],
        ["carol", "login"],
        ["bob", "logout"],
    ];

    const loginUsers = new Set(
        events
            .filter(([, event]) => event === "login")
            .map(([user]) => user)
    );

    const logoutUsers = new Set(
        events
            .filter(([, event]) => event === "logout")
            .map(([user]) => user)
    );

    console.log("Login users:", loginUsers);
    console.log("Logout users:", logoutUsers);
    console.log("Active seen users:", difference(loginUsers, logoutUsers));
}


// ============================================================================
// 14. DATA VALIDATION
// ============================================================================

function validateRecords(records, requiredFields) {
    const failures = [];

    records.forEach((record, index) => {
        const presentFields = new Set(Object.keys(record));
        const missingFields = difference(requiredFields, presentFields);

        if (missingFields.size > 0) {
            failures.push({
                index,
                missingFields,
            });
        }
    });

    return failures;
}

function dataValidation() {
    section("14. DATA VALIDATION");

    const records = [
        { id: 1, name: "Alice", email: "alice@example.com" },
        { id: 2, name: "Bob" },
        { id: 3, name: "Carol", email: "carol@example.com" },
    ];

    const requiredFields = new Set(["id", "name", "email"]);

    console.log(validateRecords(records, requiredFields));
}


// ============================================================================
// 15. DUPLICATE DETECTION
// ============================================================================

function findDuplicates(values) {
    const seen = new Set();
    const duplicates = new Set();

    for (const value of values) {
        if (seen.has(value)) {
            duplicates.add(value);
        } else {
            seen.add(value);
        }
    }

    return duplicates;
}

function duplicateDetection() {
    section("15. DUPLICATE DETECTION");

    const values = [1, 2, 3, 2, 4, 5, 1, 3];

    console.log("Duplicates:", findDuplicates(values));
}


// ============================================================================
// 16. GRAPH NEIGHBOR ANALYSIS
// ============================================================================

function graphAnalysis() {
    section("16. GRAPH NEIGHBOR ANALYSIS");

    const graph = new Map([
        ["A", new Set(["B", "C"])],
        ["B", new Set(["A", "C", "D"])],
        ["C", new Set(["A", "B", "D"])],
        ["D", new Set(["B", "C"])],
    ]);

    const commonNeighbors = intersection(
        graph.get("A"),
        graph.get("B")
    );

    console.log("A neighbors:", graph.get("A"));
    console.log("B neighbors:", graph.get("B"));
    console.log("Common neighbors:", commonNeighbors);
}


// ============================================================================
// 17. POWER SET
// ============================================================================

function powerSet(values) {
    let subsets = [new Set()];

    for (const value of values) {
        const additions = subsets.map((subset) => {
            const copy = new Set(subset);
            copy.add(value);
            return copy;
        });

        subsets = [...subsets, ...additions];
    }

    return subsets;
}

function powerSetDemo() {
    section("17. POWER SET");

    const values = new Set([1, 2, 3]);
    const subsets = powerSet(values);

    console.log("Number of subsets:", subsets.length);
    console.log("Expected:", 2 ** values.size);

    subsets.forEach((subset) => {
        console.log([...subset]);
    });
}


// ============================================================================
// 18. SET AS A STATE TRACKER
// ============================================================================

class FeatureRegistry {
    constructor() {
        this.enabledFeatures = new Set();
    }

    enable(feature) {
        this.enabledFeatures.add(feature);
    }

    disable(feature) {
        this.enabledFeatures.delete(feature);
    }

    isEnabled(feature) {
        return this.enabledFeatures.has(feature);
    }

    list() {
        return [...this.enabledFeatures].sort();
    }
}

function featureRegistryDemo() {
    section("18. FEATURE REGISTRY");

    const registry = new FeatureRegistry();

    registry.enable("dark-mode");
    registry.enable("notifications");
    registry.enable("analytics");

    console.log("Enabled:", registry.list());
    console.log("Analytics enabled:", registry.isEnabled("analytics"));

    registry.disable("analytics");

    console.log("After disabling analytics:", registry.list());
}


// ============================================================================
// 19. ITERABLE INPUT
// ============================================================================

function iterableInputs() {
    section("19. ITERABLE INPUTS");

    console.log("From array:", new Set([1, 2, 2, 3]));
    console.log("From string:", new Set("hello"));
    console.log("From generator:", new Set(
        (function* () {
            yield 1;
            yield 2;
            yield 2;
            yield 3;
        })()
    ));
}


// ============================================================================
// 20. PERFORMANCE
// ============================================================================

function performanceDemo() {
    section("20. MEMBERSHIP PERFORMANCE");

    const size = 200000;
    const array = Array.from({ length: size }, (_, index) => index);
    const set = new Set(array);
    const target = size - 1;

    const arrayStart = performance.now();
    array.includes(target);
    const arrayTime = performance.now() - arrayStart;

    const setStart = performance.now();
    set.has(target);
    const setTime = performance.now() - setStart;

    console.log(`Array includes: ${arrayTime.toFixed(6)} ms`);
    console.log(`Set has:        ${setTime.toFixed(6)} ms`);
    console.log(
        "Set membership is generally O(1) average-case, while "
        + "Array membership is O(n)."
    );
}


// ============================================================================
// 21. SET VS ARRAY
// ============================================================================

function compareStructures() {
    section("21. SET VS ARRAY");

    const array = ["Python", "Python", "JavaScript"];
    const set = new Set(array);

    console.log("Array preserves duplicates:", array);
    console.log("Set removes duplicates:", set);

    console.log(
        "Use Array when order, indexing, or duplicate occurrences matter."
    );
    console.log(
        "Use Set when uniqueness and membership are central requirements."
    );
}


// ============================================================================
// 22. ERROR HANDLING
// ============================================================================

function safeSetOperation() {
    section("22. ERROR HANDLING");

    const values = new Set([1, 2, 3]);

    function requireMember(set, value) {
        if (!set.has(value)) {
            throw new Error(`Value ${String(value)} is not present.`);
        }

        return true;
    }

    try {
        requireMember(values, 2);
        console.log("2 is present.");
        requireMember(values, 100);
    } catch (error) {
        console.log("Validation error:", error.message);
    }
}


// ============================================================================
// 23. ASYNCHRONOUS SET USAGE
// ============================================================================

async function asynchronousProcessing() {
    section("23. ASYNCHRONOUS PROCESSING");

    const processedIds = new Set();

    async function processEvent(eventId) {
        if (processedIds.has(eventId)) {
            return {
                eventId,
                processed: false,
                reason: "duplicate",
            };
        }

        // A real application might perform asynchronous I/O here.
        await Promise.resolve();

        processedIds.add(eventId);

        return {
            eventId,
            processed: true,
        };
    }

    const results = await Promise.all([
        processEvent("event-1"),
        processEvent("event-2"),
        processEvent("event-1"),
    ]);

    console.log(results);
    console.log("Processed IDs:", processedIds);
}


// ============================================================================
// 24. SECURITY ALLOW-LIST
// ============================================================================

function securityAllowList() {
    section("24. SECURITY ALLOW-LIST");

    const allowedMethods = new Set([
        "GET",
        "POST",
        "PUT",
    ]);

    const incomingMethod = "POST";

    if (allowedMethods.has(incomingMethod)) {
        console.log("HTTP method allowed.");
    } else {
        console.log("HTTP method rejected.");
    }

    console.log(
        "A Set allow-list is useful for membership checks, but it does not "
        + "replace authentication or authorization controls."
    );
}


// ============================================================================
// 25. EDGE CASES
// ============================================================================

function edgeCases() {
    section("25. EDGE CASES");

    const values = new Set();

    console.log("Empty size:", values.size);
    console.log("Empty has undefined:", values.has(undefined));

    values.add(undefined);
    values.add(null);

    console.log("After adding undefined and null:", values);

    // NaN is considered equal to itself for Set membership.
    values.add(NaN);
    values.add(NaN);

    console.log("NaN occurs once:", values.has(NaN));

    // +0 and -0 are treated as the same Set value.
    values.add(0);
    values.add(-0);

    console.log("Zero membership:", values.has(0));
    console.log("Final size:", values.size);
}


// ============================================================================
// 26. MODIFYING DURING ITERATION
// ============================================================================

function mutationDuringIteration() {
    section("26. MUTATION DURING ITERATION");

    const values = new Set([1, 2, 3, 4]);

    for (const value of values) {
        if (value % 2 === 0) {
            values.delete(value);
        }
    }

    console.log("Result after deleting during iteration:", values);

    console.log(
        "JavaScript permits some Set mutations during iteration, but "
        + "complex mutation logic can make behavior difficult to reason about."
    );

    const original = new Set([1, 2, 3, 4]);
    const filtered = new Set(
        [...original].filter((value) => value % 2 !== 0)
    );

    console.log("Clear filtering approach:", filtered);
}


// ============================================================================
// 27. CUSTOM SET-BASED CLASS
// ============================================================================

class PermissionManager {
    constructor() {
        this.permissions = new Set();
    }

    grant(permission) {
        this.permissions.add(permission);
    }

    revoke(permission) {
        this.permissions.delete(permission);
    }

    has(permission) {
        return this.permissions.has(permission);
    }

    hasAll(requiredPermissions) {
        return isSubset(requiredPermissions, this.permissions);
    }

    missing(requiredPermissions) {
        return difference(requiredPermissions, this.permissions);
    }
}

function permissionManagerDemo() {
    section("27. PERMISSION MANAGER");

    const manager = new PermissionManager();

    manager.grant("read");
    manager.grant("write");

    const required = new Set(["read", "download"]);

    console.log("Has read:", manager.has("read"));
    console.log("Has all:", manager.hasAll(required));
    console.log("Missing:", manager.missing(required));

    manager.grant("download");

    console.log("Has all after grant:", manager.hasAll(required));
}


// ============================================================================
// 28. ASSERTION TESTS
// ============================================================================

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function runTests() {
    section("28. TESTS");

    assert(
        union(new Set([1, 2]), new Set([2, 3])).size === 3,
        "union"
    );

    assert(
        intersection(new Set([1, 2]), new Set([2, 3])).has(2),
        "intersection"
    );

    assert(
        difference(new Set([1, 2]), new Set([2, 3])).has(1),
        "difference"
    );

    assert(
        symmetricDifference(
            new Set([1, 2]),
            new Set([2, 3])
        ).size === 2,
        "symmetric difference"
    );

    assert(
        isSubset(new Set([1]), new Set([1, 2])),
        "subset"
    );

    assert(
        isDisjoint(new Set([1, 2]), new Set([3, 4])),
        "disjoint"
    );

    assert(
        findDuplicates([1, 1, 2, 3, 3]).size === 2,
        "duplicates"
    );

    assert(
        [...new Set([1, 1, 2])].length === 2,
        "deduplication"
    );

    console.log("All tests passed.");
}


// ============================================================================
// 29. MAIN
// ============================================================================

async function main() {
    basicSets();
    mutation();
    iteration();
    insertionOrder();
    setAlgebra();
    algebraFallbacks();
    deduplication();
    objectIdentity();
    specialValues();
    composeSetOperations();
    tagFiltering();
    permissionSystem();
    eventAnalysis();
    dataValidation();
    duplicateDetection();
    graphAnalysis();
    powerSetDemo();
    featureRegistryDemo();
    iterableInputs();
    performanceDemo();
    compareStructures();
    safeSetOperation();
    await asynchronousProcessing();
    securityAllowList();
    edgeCases();
    mutationDuringIteration();
    permissionManagerDemo();
    runTests();

    section("END OF JAVASCRIPT SET STUDY");
    console.log("All demonstrations completed.");
}

main().catch((error) => {
    console.error("Program failed:", error);
    process.exitCode = 1;
});
