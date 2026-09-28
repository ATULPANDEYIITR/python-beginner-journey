/*
 * DICTIONARIES IN JAVASCRIPT
 * ==========================
 *
 * JavaScript does not have one single "dictionary" type.
 * Plain objects and Map are both commonly used for key-value storage.
 *
 * This file begins with object-based dictionaries and then demonstrates
 * Map, WeakMap, serialization, dispatch tables, caching, indexing,
 * asynchronous use, validation, and a realistic data-processing example.
 *
 * Run with:
 *     node dictionaries.js
 */

"use strict";


// ============================================================================
// 1. BASIC OBJECT DICTIONARIES
// ============================================================================

console.log("\n=== 1. BASIC OBJECT DICTIONARIES ===");

const student = {
    name: "Atul",
    age: 25,
    course: "Computer Science"
};

console.log(student);
console.log("Name:", student.name);
console.log("Name using bracket notation:", student["name"]);

student.age = 26;
student.city = "Prayagraj";

console.log("Updated:", student);


// ============================================================================
// 2. KEYS AND VALUES
// ============================================================================

console.log("\n=== 2. KEYS AND VALUES ===");

console.log("Object.keys:", Object.keys(student));
console.log("Object.values:", Object.values(student));
console.log("Object.entries:", Object.entries(student));

for (const [key, value] of Object.entries(student)) {
    console.log(`${key} -> ${value}`);
}


// ============================================================================
// 3. PROPERTY EXISTENCE
// ============================================================================

console.log("\n=== 3. PROPERTY EXISTENCE ===");

const profile = {
    name: "Alice",
    age: 30,
    active: true
};

console.log("'name' in profile:", "name" in profile);
console.log("Own name property:", Object.hasOwn(profile, "name"));
console.log("Missing property:", profile.country);

if (profile.country === undefined) {
    console.log("country is undefined or absent");
}


// ============================================================================
// 4. DELETE AND UPDATE
// ============================================================================

console.log("\n=== 4. DELETE AND UPDATE ===");

const account = {
    balance: 1000,
    currency: "INR",
    status: "active"
};

account.balance += 500;
account.status = "verified";

delete account.status;

console.log(account);


// ============================================================================
// 5. OBJECT LITERALS AND COMPUTED KEYS
// ============================================================================

console.log("\n=== 5. COMPUTED KEYS ===");

const fieldName = "email";

const user = {
    name: "Alice",
    [fieldName]: "alice@example.com"
};

console.log(user);


// ============================================================================
// 6. OBJECT SPREAD
// ============================================================================

console.log("\n=== 6. OBJECT SPREAD ===");

const defaults = {
    timeout: 30,
    retries: 3,
    debug: false
};

const runtime = {
    timeout: 60,
    debug: true
};

const finalConfig = {
    ...defaults,
    ...runtime
};

console.log("Final configuration:", finalConfig);

console.log(
    "Later spread properties override earlier properties."
);


// ============================================================================
// 7. DESTRUCTURING
// ============================================================================

console.log("\n=== 7. DESTRUCTURING ===");

const employee = {
    name: "Bob",
    role: "Engineer",
    salary: 95000
};

const { name, role, salary } = employee;

console.log(name, role, salary);

const {
    department = "Unknown"
} = employee;

console.log("Default value:", department);


// ============================================================================
// 8. NESTED OBJECT DICTIONARIES
// ============================================================================

console.log("\n=== 8. NESTED OBJECTS ===");

const company = {
    name: "Example Systems",
    address: {
        city: "Prayagraj",
        country: "India"
    },
    employees: {
        101: {
            name: "Alice",
            department: "Engineering"
        },
        102: {
            name: "Bob",
            department: "Security"
        }
    }
};

console.log(company.address.city);
console.log(company.employees[101].name);


// ============================================================================
// 9. OPTIONAL CHAINING
// ============================================================================

console.log("\n=== 9. OPTIONAL CHAINING ===");

const incompleteUser = {
    name: "Carol"
};

console.log(
    "City:",
    incompleteUser.address?.city ?? "Unknown"
);

console.log(
    "Phone:",
    incompleteUser.contact?.phone ?? "Not supplied"
);


// ============================================================================
// 10. NULLISH COALESCING
// ============================================================================

console.log("\n=== 10. NULLISH COALESCING ===");

const settings = {
    timeout: 0,
    retries: null
};

console.log("timeout:", settings.timeout ?? 30);
console.log("retries:", settings.retries ?? 3);

// ?? differs from ||.
// || treats values such as 0 and "" as falsy.
// ?? only treats null and undefined as missing.

console.log("0 with ||:", settings.timeout || 30);
console.log("0 with ??:", settings.timeout ?? 30);


// ============================================================================
// 11. OBJECT PROTOTYPE SECURITY
// ============================================================================

console.log("\n=== 11. OBJECT PROTOTYPE CONSIDERATIONS ===");

const dictionaryObject = Object.create(null);

dictionaryObject["__proto__"] = "ordinary dictionary value";
dictionaryObject["constructor"] = "ordinary value";

console.log(dictionaryObject);
console.log(Object.keys(dictionaryObject));

console.log(
    "Object.create(null) removes the normal Object prototype."
);


// ============================================================================
// 12. MAP: THE DEDICATED KEY-VALUE COLLECTION
// ============================================================================

console.log("\n=== 12. MAP ===");

const userMap = new Map();

userMap.set("name", "Atul");
userMap.set("age", 25);
userMap.set("active", true);

console.log(userMap);
console.log("Name:", userMap.get("name"));
console.log("Size:", userMap.size);
console.log("Has age:", userMap.has("age"));

userMap.delete("active");

console.log("After delete:", userMap);


// ============================================================================
// 13. MAP WITH NON-STRING KEYS
// ============================================================================

console.log("\n=== 13. MAP KEY TYPES ===");

const objectKey = { id: 101 };

const mapWithComplexKeys = new Map();

mapWithComplexKeys.set(objectKey, "Employee record");
mapWithComplexKeys.set(42, "Integer key");
mapWithComplexKeys.set(true, "Boolean key");

console.log(mapWithComplexKeys.get(objectKey));
console.log(mapWithComplexKeys.get(42));


// ============================================================================
// 14. OBJECT KEYS ARE COERCED TO PROPERTY KEYS
// ============================================================================

console.log("\n=== 14. OBJECT VS MAP KEY BEHAVIOR ===");

const objectDictionary = {};
objectDictionary[42] = "number-like key";
objectDictionary["42"] = "string-like key";

console.log(
    "Object has one property:",
    objectDictionary
);

const distinctMap = new Map();
distinctMap.set(42, "number");
distinctMap.set("42", "string");

console.log("Map has two distinct keys:", distinctMap.size);
console.log(distinctMap.get(42));
console.log(distinctMap.get("42"));


// ============================================================================
// 15. MAP ITERATION
// ============================================================================

console.log("\n=== 15. MAP ITERATION ===");

const inventory = new Map([
    ["laptop", 5],
    ["keyboard", 12],
    ["mouse", 20]
]);

for (const [product, quantity] of inventory) {
    console.log(product, "->", quantity);
}

console.log("Keys:", [...inventory.keys()]);
console.log("Values:", [...inventory.values()]);
console.log("Entries:", [...inventory.entries()]);


// ============================================================================
// 16. OBJECT TO MAP AND MAP TO OBJECT
// ============================================================================

console.log("\n=== 16. CONVERSION ===");

const plainObject = {
    name: "Alice",
    age: 30
};

const convertedMap = new Map(Object.entries(plainObject));
console.log("Object -> Map:", convertedMap);

const convertedObject = Object.fromEntries(convertedMap);
console.log("Map -> Object:", convertedObject);


// ============================================================================
// 17. MAP TRANSFORMATIONS
// ============================================================================

console.log("\n=== 17. MAP TRANSFORMATIONS ===");

const scores = new Map([
    ["Alice", 85],
    ["Bob", 92],
    ["Carol", 78],
    ["David", 95]
]);

const passingScores = new Map(
    [...scores].filter(([, score]) => score >= 80)
);

const doubledScores = new Map(
    [...scores].map(([studentName, score]) => [
        studentName,
        score * 2
    ])
);

console.log("Passing:", passingScores);
console.log("Doubled:", doubledScores);


// ============================================================================
// 18. DICTIONARY COMPREHENSION EQUIVALENT
// ============================================================================

console.log("\n=== 18. OBJECT TRANSFORMATION ===");

const numbers = [1, 2, 3, 4, 5];

const squares = Object.fromEntries(
    numbers.map(number => [number, number * number])
);

console.log(squares);


// ============================================================================
// 19. FREQUENCY COUNTING
// ============================================================================

console.log("\n=== 19. FREQUENCY COUNTING ===");

function countWords(words) {
    const frequency = Object.create(null);

    for (const word of words) {
        frequency[word] = (frequency[word] ?? 0) + 1;
    }

    return frequency;
}

console.log(
    countWords(["python", "javascript", "python", "map"])
);


// ============================================================================
// 20. FREQUENCY COUNTING WITH MAP
// ============================================================================

console.log("\n=== 20. MAP FREQUENCY COUNTING ===");

function countValues(values) {
    const frequency = new Map();

    for (const value of values) {
        frequency.set(value, (frequency.get(value) ?? 0) + 1);
    }

    return frequency;
}

console.log(
    countValues(["a", "b", "a", "c", "a", "b"])
);


// ============================================================================
// 21. GROUPING DATA
// ============================================================================

console.log("\n=== 21. GROUPING ===");

const records = [
    { department: "Engineering", name: "Alice" },
    { department: "Security", name: "Bob" },
    { department: "Engineering", name: "Carol" },
    { department: "Security", name: "David" }
];

function groupBy(records, property) {
    const groups = new Map();

    for (const record of records) {
        const key = record[property];

        if (!groups.has(key)) {
            groups.set(key, []);
        }

        groups.get(key).push(record);
    }

    return groups;
}

const groupedRecords = groupBy(records, "department");

for (const [department, members] of groupedRecords) {
    console.log(department, members);
}


// ============================================================================
// 22. MODERN ARRAY GROUPING
// ============================================================================

console.log("\n=== 22. OBJECT GROUPING ===");

if (typeof Object.groupBy === "function") {
    const grouped = Object.groupBy(
        records,
        record => record.department
    );

    console.log(grouped);
} else {
    console.log(
        "Object.groupBy is unavailable in this runtime; using custom groupBy."
    );
}


// ============================================================================
// 23. DISPATCH TABLE
// ============================================================================

console.log("\n=== 23. DISPATCH TABLE ===");

function safeDivide(a, b) {
    if (b === 0) {
        throw new RangeError("Division by zero");
    }

    return a / b;
}

const operations = {
    add: (a, b) => a + b,
    subtract: (a, b) => a - b,
    multiply: (a, b) => a * b,
    divide: safeDivide
};

function executeOperation(operation, a, b) {
    const handler = operations[operation];

    if (typeof handler !== "function") {
        throw new Error(`Unsupported operation: ${operation}`);
    }

    return handler(a, b);
}

console.log(
    "6 * 7 =",
    executeOperation("multiply", 6, 7)
);

try {
    executeOperation("divide", 10, 0);
} catch (error) {
    console.log("Expected error:", error.message);
}


// ============================================================================
// 24. VALIDATION
// ============================================================================

console.log("\n=== 24. VALIDATION ===");

function validateUser(data) {
    const errors = [];

    if (typeof data.name !== "string" || data.name.trim() === "") {
        errors.push("name must be a non-empty string");
    }

    if (
        typeof data.email !== "string" ||
        !data.email.includes("@")
    ) {
        errors.push("email must be a valid-looking string");
    }

    if (
        !Number.isInteger(data.age) ||
        data.age < 0
    ) {
        errors.push("age must be a non-negative integer");
    }

    return errors;
}

console.log(
    "Valid user:",
    validateUser({
        name: "Alice",
        email: "alice@example.com",
        age: 30
    })
);

console.log(
    "Invalid user:",
    validateUser({
        name: "",
        email: "invalid",
        age: -1
    })
);


// ============================================================================
// 25. MAP VS OBJECT
// ============================================================================

console.log("\n=== 25. MAP VS OBJECT ===");

console.log("Object is convenient for JSON-like records.");
console.log("Map is designed specifically for dynamic key-value collections.");
console.log("Map supports arbitrary key types.");
console.log("Object property keys are strings or symbols.");
console.log("Map exposes size directly.");
console.log("Map provides clear has/get/set/delete operations.");


// ============================================================================
// 26. WEAKMAP
// ============================================================================

console.log("\n=== 26. WEAKMAP ===");

const privateData = new WeakMap();

class User {
    constructor(name) {
        this.name = name;

        // The object itself is the key. The WeakMap does not prevent
        // garbage collection of an otherwise unreachable object key.
        privateData.set(this, {
            loginCount: 0
        });
    }

    login() {
        const data = privateData.get(this);
        data.loginCount += 1;
    }

    getLoginCount() {
        return privateData.get(this).loginCount;
    }
}

const userInstance = new User("Alice");
userInstance.login();
userInstance.login();

console.log(
    "WeakMap-backed private state:",
    userInstance.getLoginCount()
);


// ============================================================================
// 27. IMMUTABILITY
// ============================================================================

console.log("\n=== 27. IMMUTABILITY ===");

const original = {
    name: "Alice",
    preferences: {
        theme: "dark"
    }
};

const shallowCopy = {
    ...original
};

shallowCopy.name = "Bob";
shallowCopy.preferences.theme = "light";

console.log(
    "Nested object changed because spread is shallow:",
    original
);

console.log(
    "structuredClone is useful for supported structured data:"
);

if (typeof structuredClone === "function") {
    const deepCopy = structuredClone(original);
    deepCopy.preferences.theme = "blue";

    console.log("Original:", original);
    console.log("Clone:", deepCopy);
}


// ============================================================================
// 28. OBJECT.FREEZE
// ============================================================================

console.log("\n=== 28. OBJECT.FREEZE ===");

const frozenSettings = Object.freeze({
    timeout: 30,
    debug: false
});

try {
    frozenSettings.timeout = 60;
} catch (error) {
    console.log("Strict-mode freeze error:", error.message);
}

console.log("Frozen settings:", frozenSettings);


// ============================================================================
// 29. JSON SERIALIZATION
// ============================================================================

console.log("\n=== 29. JSON ===");

const configuration = {
    application: "DictionaryLab",
    version: 1,
    features: ["lookup", "validation"],
    database: {
        host: "localhost",
        port: 5432
    }
};

const jsonText = JSON.stringify(configuration, null, 2);

console.log(jsonText);

const decoded = JSON.parse(jsonText);

console.log("Decoded:", decoded);


// ============================================================================
// 30. JSON AND MAP LIMITATION
// ============================================================================

console.log("\n=== 30. MAP SERIALIZATION ===");

const mapData = new Map([
    ["name", "Alice"],
    ["age", 30]
]);

console.log(
    "Direct JSON.stringify(Map):",
    JSON.stringify(mapData)
);

const serializableMap = Object.fromEntries(mapData);

console.log(
    "Map converted to object:",
    JSON.stringify(serializableMap)
);


// ============================================================================
// 31. PROTOTYPE POLLUTION-AWARE MERGING
// ============================================================================

console.log("\n=== 31. SAFE CONFIGURATION MERGING ===");

const trustedConfig = {
    debug: false,
    authenticationRequired: true
};

const allowedKeys = new Set([
    "language",
    "timeout"
]);

const externalConfig = {
    debug: true,
    timeout: 60
};

const safeExternalUpdates = Object.fromEntries(
    Object.entries(externalConfig)
        .filter(([key]) => allowedKeys.has(key))
);

const safeConfig = {
    ...trustedConfig,
    ...safeExternalUpdates
};

console.log(safeConfig);


// ============================================================================
// 32. LRU CACHE
// ============================================================================

console.log("\n=== 32. LRU CACHE ===");

class LRUCache {
    constructor(capacity) {
        if (!Number.isInteger(capacity) || capacity <= 0) {
            throw new RangeError("Capacity must be positive");
        }

        this.capacity = capacity;
        this.cache = new Map();
    }

    get(key) {
        if (!this.cache.has(key)) {
            return undefined;
        }

        const value = this.cache.get(key);

        // Reinsert to move the key to the newest position.
        this.cache.delete(key);
        this.cache.set(key, value);

        return value;
    }

    set(key, value) {
        if (this.cache.has(key)) {
            this.cache.delete(key);
        }

        this.cache.set(key, value);

        if (this.cache.size > this.capacity) {
            const oldestKey = this.cache.keys().next().value;
            this.cache.delete(oldestKey);
        }
    }

    entries() {
        return [...this.cache.entries()];
    }
}

const cache = new LRUCache(2);

cache.set("A", 100);
cache.set("B", 200);

console.log(cache.entries());

cache.get("A");
cache.set("C", 300);

console.log("After eviction:", cache.entries());


// ============================================================================
// 33. MEMOIZATION
// ============================================================================

console.log("\n=== 33. MEMOIZATION ===");

function memoizeUnary(functionToCache) {
    const cache = new Map();

    return function memoized(argument) {
        if (cache.has(argument)) {
            return cache.get(argument);
        }

        const result = functionToCache(argument);
        cache.set(argument, result);

        return result;
    };
}

const expensiveSquare = memoizeUnary(
    number => {
        return number * number;
    }
);

console.log(expensiveSquare(12));
console.log(expensiveSquare(12));


// ============================================================================
// 34. RECURSIVE DICTIONARY TRAVERSAL
// ============================================================================

console.log("\n=== 34. NESTED OBJECT FLATTENING ===");

function flattenObject(object, prefix = "", output = {}) {
    for (const [key, value] of Object.entries(object)) {
        const path = prefix ? `${prefix}.${key}` : key;

        if (
            value !== null &&
            typeof value === "object" &&
            !Array.isArray(value)
        ) {
            flattenObject(value, path, output);
        } else {
            output[path] = value;
        }
    }

    return output;
}

const nestedConfiguration = {
    application: {
        database: {
            host: "localhost",
            port: 5432
        },
        logging: {
            level: "INFO"
        }
    }
};

console.log(
    flattenObject(nestedConfiguration)
);


// ============================================================================
// 35. INVERTED INDEX
// ============================================================================

console.log("\n=== 35. INVERTED INDEX ===");

const documents = new Map([
    [1, "javascript maps support key value lookup"],
    [2, "objects support property lookup"],
    [3, "maps support arbitrary keys"]
]);

function buildInvertedIndex(documentMap) {
    const index = new Map();

    for (const [documentId, content] of documentMap) {
        const words = content.toLowerCase().split(/\s+/);

        for (const word of words) {
            if (!index.has(word)) {
                index.set(word, new Set());
            }

            index.get(word).add(documentId);
        }
    }

    return index;
}

const invertedIndex = buildInvertedIndex(documents);

console.log(
    "Documents containing 'maps':",
    [...(invertedIndex.get("maps") ?? [])]
);

console.log(
    "Documents containing 'lookup':",
    [...(invertedIndex.get("lookup") ?? [])]
);


// ============================================================================
// 36. GRAPH USING MAP
// ============================================================================

console.log("\n=== 36. GRAPH ===");

const graph = new Map([
    ["A", ["B", "C"]],
    ["B", ["A", "D"]],
    ["C", ["A", "D"]],
    ["D", ["B", "C"]]
]);

function breadthFirstSearch(graphMap, start) {
    if (!graphMap.has(start)) {
        throw new Error(`Unknown start node: ${start}`);
    }

    const queue = [start];
    const visited = new Set([start]);
    const result = [];

    let index = 0;

    while (index < queue.length) {
        const current = queue[index++];
        result.push(current);

        for (const neighbor of graphMap.get(current) ?? []) {
            if (!visited.has(neighbor)) {
                visited.add(neighbor);
                queue.push(neighbor);
            }
        }
    }

    return result;
}

console.log(
    "BFS:",
    breadthFirstSearch(graph, "A")
);


// ============================================================================
// 37. WEIGHTED GRAPH
// ============================================================================

console.log("\n=== 37. WEIGHTED GRAPH ===");

const weightedGraph = new Map([
    ["A", new Map([["B", 4], ["C", 2]])],
    ["B", new Map([["C", 1], ["D", 5]])],
    ["C", new Map([["B", 1], ["D", 8], ["E", 10]])],
    ["D", new Map([["E", 2]])],
    ["E", new Map()]
]);

function dijkstra(graphMap, source) {
    if (!graphMap.has(source)) {
        throw new Error(`Unknown source: ${source}`);
    }

    const distances = new Map();

    for (const node of graphMap.keys()) {
        distances.set(node, Infinity);
    }

    distances.set(source, 0);

    const unvisited = new Set(graphMap.keys());

    while (unvisited.size > 0) {
        let current = null;
        let currentDistance = Infinity;

        for (const node of unvisited) {
            const distance = distances.get(node);

            if (distance < currentDistance) {
                current = node;
                currentDistance = distance;
            }
        }

        if (current === null) {
            break;
        }

        unvisited.delete(current);

        for (const [neighbor, weight] of graphMap.get(current)) {
            if (weight < 0) {
                throw new Error(
                    "Dijkstra requires non-negative edge weights"
                );
            }

            const candidate = currentDistance + weight;

            if (candidate < distances.get(neighbor)) {
                distances.set(neighbor, candidate);
            }
        }
    }

    return distances;
}

console.log(
    "Shortest paths:",
    [...dijkstra(weightedGraph, "A").entries()]
);


// ============================================================================
// 38. STATE MACHINE
// ============================================================================

console.log("\n=== 38. STATE MACHINE ===");

const transitions = {
    locked: {
        unlock: "unlocked"
    },
    unlocked: {
        lock: "locked",
        open: "open"
    },
    open: {
        close: "unlocked"
    }
};

function transitionState(state, event) {
    const nextState = transitions[state]?.[event];

    if (nextState === undefined) {
        throw new Error(
            `Invalid transition: ${state} + ${event}`
        );
    }

    return nextState;
}

let state = "locked";

for (const event of ["unlock", "open", "close", "lock"]) {
    state = transitionState(state, event);
    console.log(event, "->", state);
}


// ============================================================================
// 39. ERROR HANDLING
// ============================================================================

console.log("\n=== 39. ERROR HANDLING ===");

function requireProperty(object, key) {
    if (!Object.hasOwn(object, key)) {
        throw new TypeError(`Required property missing: ${key}`);
    }

    return object[key];
}

try {
    console.log(
        requireProperty({ name: "Alice" }, "email")
    );
} catch (error) {
    console.log("Handled:", error.message);
}


// ============================================================================
// 40. ASYNCHRONOUS DICTIONARY PROCESSING
// ============================================================================

console.log("\n=== 40. ASYNCHRONOUS PROCESSING ===");

function delayedValue(key, value, milliseconds) {
    return new Promise(resolve => {
        setTimeout(() => {
            resolve([key, value]);
        }, milliseconds);
    });
}

async function buildAsyncDictionary() {
    const entries = await Promise.all([
        delayedValue("serviceA", "ready", 10),
        delayedValue("serviceB", "ready", 5),
        delayedValue("serviceC", "ready", 1)
    ]);

    return Object.fromEntries(entries);
}


// ============================================================================
// 41. REALISTIC SALES ANALYTICS
// ============================================================================

console.log("\n=== 41. SALES ANALYTICS ===");

const sales = [
    {
        product: "Laptop",
        category: "Electronics",
        quantity: 2,
        price: 75000
    },
    {
        product: "Mouse",
        category: "Electronics",
        quantity: 5,
        price: 1200
    },
    {
        product: "Chair",
        category: "Furniture",
        quantity: 3,
        price: 8000
    },
    {
        product: "Laptop",
        category: "Electronics",
        quantity: 1,
        price: 75000
    }
];

function calculateSalesAnalytics(records) {
    const productRevenue = new Map();
    const categoryRevenue = new Map();
    const productQuantity = new Map();

    for (const record of records) {
        if (
            typeof record.product !== "string" ||
            typeof record.category !== "string" ||
            !Number.isFinite(record.quantity) ||
            !Number.isFinite(record.price) ||
            record.quantity < 0 ||
            record.price < 0
        ) {
            throw new TypeError("Invalid sales record");
        }

        const revenue = record.quantity * record.price;

        productRevenue.set(
            record.product,
            (productRevenue.get(record.product) ?? 0) + revenue
        );

        categoryRevenue.set(
            record.category,
            (categoryRevenue.get(record.category) ?? 0) + revenue
        );

        productQuantity.set(
            record.product,
            (productQuantity.get(record.product) ?? 0) +
            record.quantity
        );
    }

    return {
        productRevenue,
        categoryRevenue,
        productQuantity
    };
}

const analytics = calculateSalesAnalytics(sales);

console.log(
    "Product revenue:",
    [...analytics.productRevenue.entries()]
);

console.log(
    "Category revenue:",
    [...analytics.categoryRevenue.entries()]
);

console.log(
    "Product quantities:",
    [...analytics.productQuantity.entries()]
);


// ============================================================================
// 42. ROLE-BASED ACCESS CONTROL
// ============================================================================

console.log("\n=== 42. ROLE-BASED ACCESS CONTROL ===");

const permissions = new Map([
    ["admin", new Set(["read", "write", "delete"])],
    ["editor", new Set(["read", "write"])],
    ["viewer", new Set(["read"])]
]);

function isAuthorized(role, permission) {
    return permissions.get(role)?.has(permission) ?? false;
}

for (const role of ["admin", "editor", "viewer", "unknown"]) {
    console.log(
        role,
        "read:",
        isAuthorized(role, "read"),
        "delete:",
        isAuthorized(role, "delete")
    );
}


// ============================================================================
// 43. PERFORMANCE CONSIDERATIONS
// ============================================================================

console.log("\n=== 43. PERFORMANCE ===");

const largeMap = new Map();

for (let i = 0; i < 100000; i++) {
    largeMap.set(i, i);
}

const startTime = process.hrtime.bigint();

let total = 0;

for (let i = 0; i < 100000; i++) {
    total += largeMap.get(i);
}

const endTime = process.hrtime.bigint();

console.log("Lookup checksum:", total);
console.log(
    "100,000 Map lookups:",
    Number(endTime - startTime) / 1_000_000,
    "ms"
);

console.log(
    "Map operations are generally designed for efficient average-case lookup."
);
console.log(
    "Exact performance depends on the JavaScript engine, data size, and workload."
);


// ============================================================================
// 44. EDGE CASES
// ============================================================================

console.log("\n=== 44. EDGE CASES ===");

const edgeCases = {
    zero: 0,
    emptyString: "",
    falseValue: false,
    nullValue: null
};

console.log("zero:", edgeCases.zero);
console.log("empty string:", edgeCases.emptyString);
console.log("false:", edgeCases.falseValue);
console.log("null:", edgeCases.nullValue);

console.log(
    "Use ?? when null and undefined should mean 'missing'."
);


// ============================================================================
// 45. OBJECT EQUALITY
// ============================================================================

console.log("\n=== 45. OBJECT KEY IDENTITY ===");

const keyA = { id: 1 };
const keyB = { id: 1 };

const identityMap = new Map();

identityMap.set(keyA, "A");

console.log("Same object:", identityMap.get(keyA));
console.log(
    "Different object with same contents:",
    identityMap.get(keyB)
);

console.log(
    "Objects are compared by identity, not structural contents."
);


// ============================================================================
// 46. CUSTOM KEY OBJECTS
// ============================================================================

console.log("\n=== 46. CUSTOM OBJECT KEYS ===");

class UserKey {
    constructor(id) {
        this.id = id;
    }
}

const customKeyMap = new Map();

const firstKey = new UserKey(101);
const equivalentLookingKey = new UserKey(101);

customKeyMap.set(firstKey, "Administrator");

console.log(customKeyMap.get(firstKey));
console.log(customKeyMap.get(equivalentLookingKey));

console.log(
    "JavaScript Map object keys use object identity."
);


// ============================================================================
// 47. DICTIONARY-BASED CACHE WITH TTL
// ============================================================================

console.log("\n=== 47. EXPIRING CACHE ===");

class ExpiringCache {
    constructor(defaultTtlMilliseconds) {
        if (
            !Number.isFinite(defaultTtlMilliseconds) ||
            defaultTtlMilliseconds <= 0
        ) {
            throw new RangeError("TTL must be positive");
        }

        this.defaultTtlMilliseconds = defaultTtlMilliseconds;
        this.entries = new Map();
    }

    set(key, value, ttlMilliseconds = this.defaultTtlMilliseconds) {
        if (ttlMilliseconds <= 0) {
            throw new RangeError("TTL must be positive");
        }

        this.entries.set(
            key,
            {
                value,
                expiresAt: Date.now() + ttlMilliseconds
            }
        );
    }

    get(key) {
        const entry = this.entries.get(key);

        if (!entry) {
            return undefined;
        }

        if (Date.now() >= entry.expiresAt) {
            this.entries.delete(key);
            return undefined;
        }

        return entry.value;
    }
}

const expiringCache = new ExpiringCache(1000);

expiringCache.set("session", "ACTIVE");

console.log(
    "Immediate cache lookup:",
    expiringCache.get("session")
);


// ============================================================================
// 48. TESTS
// ============================================================================

console.log("\n=== 48. ASSERTION TESTS ===");

function assertEqual(actual, expected, message) {
    if (actual !== expected) {
        throw new Error(
            `${message}: expected ${expected}, got ${actual}`
        );
    }
}

assertEqual(
    countWords(["A", "a"]).a,
    2,
    "Case-sensitive test"
);

assertEqual(
    executeOperation("add", 2, 3),
    5,
    "Addition"
);

assertEqual(
    isAuthorized("viewer", "read"),
    true,
    "Viewer read access"
);

assertEqual(
    isAuthorized("viewer", "delete"),
    false,
    "Viewer delete access"
);

console.log("All assertions passed.");


// ============================================================================
// 49. ASYNC MAIN
// ============================================================================

async function main() {
    const asyncDictionary = await buildAsyncDictionary();

    console.log(
        "\nAsync dictionary:",
        asyncDictionary
    );

    console.log(
        "\nJavaScript dictionary and Map demonstrations completed."
    );
}

main().catch(error => {
    console.error("Fatal error:", error);
    process.exitCode = 1;
});
