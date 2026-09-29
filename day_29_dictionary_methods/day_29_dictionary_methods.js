/*
 * Dictionary Methods: JavaScript Companion Study File
 *
 * JavaScript does not have a built-in type literally named "dictionary".
 * Plain objects and Map are the two major structures used for dictionary-like
 * key-value storage.
 *
 * This file starts with object fundamentals and progresses to Map, nested
 * structures, grouping, counting, validation, caching, dispatch tables,
 * serialization, and an application-style example.
 */

"use strict";

// ============================================================================
// 1. BASIC OBJECTS
// ============================================================================

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function show(label, value) {
    console.log(`${label}:`, value);
}

section("1. Creating Dictionary-Like Objects");

const emptyDictionary = {};

const student = {
    name: "Atul",
    age: 30,
    course: "Computer Science"
};

show("Empty object", emptyDictionary);
show("Student object", student);


// ============================================================================
// 2. ACCESSING PROPERTIES
// ============================================================================

section("2. Property Access");

show("Dot notation", student.name);
show("Bracket notation", student["course"]);

const dynamicKey = "age";
show("Dynamic bracket access", student[dynamicKey]);

// Missing object properties normally return undefined.
show("Missing property", student.salary);

if ("name" in student) {
    console.log("'name' exists in student.");
}


// ============================================================================
// 3. ADDING AND MODIFYING
// ============================================================================

section("3. Adding and Updating Properties");

student.role = "Developer";
student.age = 31;

student["location"] = "India";

show("Updated student", student);


// ============================================================================
// 4. OBJECT METHODS
// ============================================================================

section("4. Object.keys(), Object.values(), Object.entries()");

const inventory = {
    laptop: 5,
    monitor: 12,
    keyboard: 20
};

show("Object.keys()", Object.keys(inventory));
show("Object.values()", Object.values(inventory));
show("Object.entries()", Object.entries(inventory));

console.log("\nIterating with Object.entries():");

for (const [product, quantity] of Object.entries(inventory)) {
    console.log(`${product}: ${quantity}`);
}


// ============================================================================
// 5. HAS-OWN PROPERTY
// ============================================================================

section("5. Checking Own Properties");

show(
    "Object.has() existing",
    Object.has(inventory, "laptop")
);

show(
    "Object.has() missing",
    Object.has(inventory, "phone")
);

// hasOwnProperty can be shadowed by user-controlled data, so Object.has()
// is a robust modern alternative.
const unusualObject = {
    hasOwnProperty: "not a function",
    value: 100
};

show(
    "Safe own-property check",
    Object.has(unusualObject, "value")
);


// ============================================================================
// 6. DELETE
// ============================================================================

section("6. Deleting Properties");

const temporary = {
    a: 1,
    b: 2,
    c: 3
};

delete temporary.b;

show("After delete", temporary);


// ============================================================================
// 7. OBJECT ASSIGN
// ============================================================================

section("7. Object.assign()");

const defaults = {
    timeout: 30,
    retries: 3,
    debug: false
};

const custom = {
    timeout: 60,
    cache: true
};

const merged = Object.assign({}, defaults, custom);

show("Merged object", merged);

const target = { a: 1 };
Object.assign(target, { b: 2 }, { a: 10 });

show("Mutated target", target);


// ============================================================================
// 8. SPREAD SYNTAX
// ============================================================================

section("8. Object Spread");

const identity = {
    name: "Atul"
};

const professional = {
    role: "Developer"
};

const combined = {
    ...identity,
    ...professional
};

show("Combined object", combined);

const conflict = {
    ...{ role: "Student" },
    ...{ role: "Developer" }
};

show("Spread conflict resolution", conflict);


// ============================================================================
// 9. NESTED OBJECTS
// ============================================================================

section("9. Nested Dictionary-Like Structures");

const company = {
    name: "Example Technologies",
    address: {
        city: "Lucknow",
        country: "India"
    },
    departments: {
        engineering: {
            employees: 40,
            budget: 5000000
        },
        finance: {
            employees: 12,
            budget: 1800000
        }
    }
};

show(
    "Engineering budget",
    company.departments.engineering.budget
);


// ============================================================================
// 10. OPTIONAL CHAINING AND NULLISH COALESCING
// ============================================================================

section("10. Safe Nested Access");

show(
    "Existing nested property",
    company.departments.finance?.employees
);

show(
    "Missing nested property",
    company.departments.legal?.employees
);

const employeeCount =
    company.departments.legal?.employees ?? 0;

show("Missing value with fallback", employeeCount);


// ============================================================================
// 11. OBJECT DESTRUCTURING
// ============================================================================

section("11. Destructuring");

const {
    name: studentName,
    role: studentRole,
    missingField = "default value"
} = {
    name: "Atul",
    role: "Developer"
};

show("Destructured name", studentName);
show("Destructured role", studentRole);
show("Destructured default", missingField);


// ============================================================================
// 12. MAP: JAVASCRIPT'S DEDICATED KEY-VALUE COLLECTION
// ============================================================================

section("12. Map Fundamentals");

const userMap = new Map();

userMap.set("name", "Atul");
userMap.set("age", 30);
userMap.set("active", true);

show("Map size", userMap.size);
show("Map get()", userMap.get("name"));
show("Map has()", userMap.has("active"));

userMap.delete("active");

show("Map after delete()", [...userMap.entries()]);


// ============================================================================
// 13. MAP CONSTRUCTION
// ============================================================================

section("13. Creating Map from Entries");

const scoreMap = new Map([
    ["Python", 95],
    ["JavaScript", 88],
    ["C++", 91]
]);

show("Map", scoreMap);

for (const [subject, score] of scoreMap) {
    console.log(`${subject}: ${score}`);
}


// ============================================================================
// 14. OBJECT VS MAP
// ============================================================================

section("14. Object and Map Comparison");

const objectDictionary = {
    name: "Atul",
    score: 95
};

const mapDictionary = new Map([
    ["name", "Atul"],
    ["score", 95]
]);

show("Object keys", Object.keys(objectDictionary));
show("Map keys", [...mapDictionary.keys()]);

console.log(
    "Objects are natural for JSON-shaped records and fixed schemas."
);

console.log(
    "Map is designed specifically for dynamic key-value collections."
);

console.log(
    "Map supports keys of any value type, including objects."
);


// ============================================================================
// 15. MAP WITH NON-STRING KEYS
// ============================================================================

section("15. Map Supports Object Keys");

const objectKey = {
    id: 101
};

const objectKeyMap = new Map();

objectKeyMap.set(objectKey, "associated data");

show("Lookup with same object reference", objectKeyMap.get(objectKey));
show(
    "Lookup with different object",
    objectKeyMap.get({ id: 101 })
);

// Different object references are different Map keys even if their contents
// look identical.


section("16. Object Key Coercion");

const objectKeyExample = {};

objectKeyExample[1] = "integer-like property";
objectKeyExample["1"] = "string property replaces it";

show("Object key coercion", objectKeyExample);


// ============================================================================
// 17. COUNTING
// ============================================================================

section("17. Counting with Map");

const text = "mississippi";
const characterCounts = new Map();

for (const character of text) {
    const current = characterCounts.get(character) ?? 0;
    characterCounts.set(character, current + 1);
}

show("Character counts", [...characterCounts.entries()]);


// ============================================================================
// 18. GROUPING
// ============================================================================

section("18. Grouping with Map");

const employees = [
    { name: "Atul", department: "Engineering", salary: 90000 },
    { name: "Priya", department: "Engineering", salary: 95000 },
    { name: "Ravi", department: "Finance", salary: 80000 },
    { name: "Neha", department: "Finance", salary: 85000 }
];

const groups = new Map();

for (const employee of employees) {
    if (!groups.has(employee.department)) {
        groups.set(employee.department, []);
    }

    groups.get(employee.department).push(employee);
}

show("Grouped employees", [...groups.entries()]);


// ============================================================================
// 19. GROUPING WITH REDUCE
// ============================================================================

section("19. Grouping with reduce()");

const groupedByDepartment = employees.reduce(
    (groupsObject, employee) => {
        const department = employee.department;

        if (!groupsObject[department]) {
            groupsObject[department] = [];
        }

        groupsObject[department].push(employee);
        return groupsObject;
    },
    {}
);

show("reduce() grouping", groupedByDepartment);


// ============================================================================
// 20. FILTERING OBJECT ENTRIES
// ============================================================================

section("20. Filtering Dictionary-Like Data");

const prices = {
    laptop: 75000,
    phone: 45000,
    tablet: 30000
};

const expensiveProducts = Object.fromEntries(
    Object.entries(prices)
        .filter(([, price]) => price >= 45000)
);

show("Expensive products", expensiveProducts);


// ============================================================================
// 21. TRANSFORMING OBJECT ENTRIES
// ============================================================================

section("21. Transforming Dictionary Values");

const discountedPrices = Object.fromEntries(
    Object.entries(prices)
        .map(([product, price]) => [
            product,
            Math.round(price * 0.90)
        ])
);

show("Discounted prices", discountedPrices);


// ============================================================================
// 22. SORTING
// ============================================================================

section("22. Sorting Object Entries");

const marks = {
    Atul: 92,
    Priya: 87,
    Ravi: 95,
    Neha: 81
};

const sortedByScore = Object.entries(marks)
    .sort(([, scoreA], [, scoreB]) => scoreB - scoreA);

show("Sorted scores", sortedByScore);


// ============================================================================
// 23. VALIDATION
// ============================================================================

section("23. Dictionary Validation");

function validateUserRecord(record) {
    const errors = [];

    if (typeof record.name !== "string") {
        errors.push("name must be a string");
    }

    if (
        typeof record.email !== "string" ||
        !record.email.includes("@")
    ) {
        errors.push("email must contain @");
    }

    if (
        typeof record.age !== "number" ||
        !Number.isInteger(record.age) ||
        record.age < 0
    ) {
        errors.push("age must be a non-negative integer");
    }

    return errors;
}

const validUser = {
    name: "Atul",
    email: "atul@example.com",
    age: 30
};

const invalidUser = {
    name: 100,
    email: "invalid",
    age: -5
};

show("Valid user errors", validateUserRecord(validUser));
show("Invalid user errors", validateUserRecord(invalidUser));


// ============================================================================
// 24. ALLOWLISTING
// ============================================================================

section("24. Allowlisting External Fields");

const requestData = {
    username: "atul",
    role: "user",
    isAdmin: true,
    debug: true
};

const allowedFields = new Set([
    "username",
    "role"
]);

const safeRequest = Object.fromEntries(
    Object.entries(requestData)
        .filter(([key]) => allowedFields.has(key))
);

show("Original request", requestData);
show("Allowlisted request", safeRequest);


// ============================================================================
// 25. SHALLOW COPYING
// ============================================================================

section("25. Shallow Copy Behavior");

const original = {
    name: "Atul",
    skills: ["Python", "SQL"]
};

const shallowCopy = { ...original };

shallowCopy.name = "Changed";
shallowCopy.skills.push("C++");

show("Original after shallow nested modification", original);
show("Shallow copy", shallowCopy);


// ============================================================================
// 26. DEEP COPY
// ============================================================================

section("26. Structured Clone");

const nestedOriginal = {
    name: "Atul",
    preferences: {
        theme: "dark",
        languages: ["Python", "JavaScript"]
    }
};

const deepCopy = structuredClone(nestedOriginal);

deepCopy.preferences.languages.push("C++");

show("Original", nestedOriginal);
show("Deep copy", deepCopy);


// ============================================================================
// 27. JSON SERIALIZATION
// ============================================================================

section("27. JSON Serialization");

const apiResponse = {
    status: "success",
    user: {
        id: 1001,
        name: "Atul"
    },
    roles: ["developer", "researcher"]
};

const jsonText = JSON.stringify(apiResponse, null, 2);

show("JSON text", jsonText);

const restored = JSON.parse(jsonText);

show("Restored object", restored);


// ============================================================================
// 28. MAP AND JSON
// ============================================================================

section("28. Serializing Map");

const serializableMap = new Map([
    ["name", "Atul"],
    ["age", 30]
]);

const mapAsObject = Object.fromEntries(serializableMap);

show("Map converted to object", mapAsObject);

const restoredMap = new Map(Object.entries(mapAsObject));

show("Restored Map", restoredMap);


// ============================================================================
// 29. DISPATCH TABLE
// ============================================================================

section("29. Function Dispatch Table");

function add(a, b) {
    return a + b;
}

function subtract(a, b) {
    return a - b;
}

function multiply(a, b) {
    return a * b;
}

function divide(a, b) {
    if (b === 0) {
        throw new Error("Cannot divide by zero");
    }

    return a / b;
}

const operations = {
    "+": add,
    "-": subtract,
    "*": multiply,
    "/": divide
};

function calculate(operator, a, b) {
    const operation = operations[operator];

    if (typeof operation !== "function") {
        throw new Error(`Unsupported operator: ${operator}`);
    }

    return operation(a, b);
}

for (const operator of Object.keys(operations)) {
    console.log(`10 ${operator} 5 = ${calculate(operator, 10, 5)}`);
}


// ============================================================================
// 30. CACHE
// ============================================================================

section("30. Map-Based Memoization");

const fibonacciCache = new Map([
    [0, 0],
    [1, 1]
]);

function fibonacci(number) {
    if (fibonacciCache.has(number)) {
        return fibonacciCache.get(number);
    }

    const value =
        fibonacci(number - 1) +
        fibonacci(number - 2);

    fibonacciCache.set(number, value);

    return value;
}

show("Fibonacci 40", fibonacci(40));
show("Cache size", fibonacciCache.size);


// ============================================================================
// 31. INVENTORY CLASS
// ============================================================================

section("31. Practical Inventory System");

class Inventory {
    constructor() {
        this.products = new Map();
    }

    addProduct(productId, name, price, quantity) {
        if (!productId) {
            throw new Error("productId cannot be empty");
        }

        if (price < 0) {
            throw new Error("price cannot be negative");
        }

        if (!Number.isInteger(quantity) || quantity < 0) {
            throw new Error(
                "quantity must be a non-negative integer"
            );
        }

        if (this.products.has(productId)) {
            throw new Error(`Product already exists: ${productId}`);
        }

        this.products.set(productId, {
            name,
            price,
            quantity
        });
    }

    restock(productId, quantity) {
        if (!Number.isInteger(quantity) || quantity <= 0) {
            throw new Error(
                "restock quantity must be a positive integer"
            );
        }

        const product = this.products.get(productId);

        if (!product) {
            throw new Error(`Unknown product: ${productId}`);
        }

        product.quantity += quantity;
    }

    sell(productId, quantity) {
        if (!Number.isInteger(quantity) || quantity <= 0) {
            throw new Error(
                "sale quantity must be a positive integer"
            );
        }

        const product = this.products.get(productId);

        if (!product) {
            throw new Error(`Unknown product: ${productId}`);
        }

        if (product.quantity < quantity) {
            throw new Error("Insufficient stock");
        }

        product.quantity -= quantity;

        return product.price * quantity;
    }

    getProduct(productId) {
        const product = this.products.get(productId);

        if (!product) {
            return null;
        }

        // Return a shallow copy so callers do not receive the exact
        // product record stored in the Map.
        return { ...product };
    }

    lowStock(threshold = 5) {
        const result = {};

        for (const [productId, product] of this.products) {
            if (product.quantity <= threshold) {
                result[productId] = { ...product };
            }
        }

        return result;
    }

    totalValue() {
        let total = 0;

        for (const product of this.products.values()) {
            total += product.price * product.quantity;
        }

        return total;
    }
}

const inventory = new Inventory();

inventory.addProduct("P001", "Laptop", 75000, 10);
inventory.addProduct("P002", "Keyboard", 2500, 3);
inventory.addProduct("P003", "Monitor", 18000, 7);

inventory.restock("P002", 4);

const saleValue = inventory.sell("P001", 2);

show("Sale value", saleValue);
show("Laptop", inventory.getProduct("P001"));
show("Low-stock products", inventory.lowStock());
show("Inventory value", inventory.totalValue());


// ============================================================================
// 32. ERROR HANDLING
// ============================================================================

section("32. Error Handling");

try {
    inventory.sell("UNKNOWN", 1);
} catch (error) {
    console.log("Handled inventory error:", error.message);
}

try {
    inventory.sell("P001", 1000);
} catch (error) {
    console.log("Handled stock error:", error.message);
}


// ============================================================================
// 33. MAP ITERATION
// ============================================================================

section("33. Map Iteration Methods");

const metrics = new Map([
    ["requests", 1500],
    ["errors", 12],
    ["latencyMs", 80]
]);

show("keys", [...metrics.keys()]);
show("values", [...metrics.values()]);
show("entries", [...metrics.entries()]);

metrics.forEach((value, key) => {
    console.log(`${key}: ${value}`);
});


// ============================================================================
// 34. OBJECT PROPERTY ORDER
// ============================================================================

section("34. Object Key Ordering Peculiarity");

const orderedObject = {};

orderedObject.z = "z";
orderedObject.a = "a";
orderedObject[2] = "two";
orderedObject[1] = "one";

show("Object.keys ordering", Object.keys(orderedObject));

console.log(
    "Integer-index-like keys have special ordering rules in JavaScript objects."
);

console.log(
    "Map preserves insertion order for its entries."
);


// ============================================================================
// 35. PROTOTYPE SAFETY
// ============================================================================

section("35. Prototype Considerations");

const nullPrototypeDictionary = Object.create(null);

nullPrototypeDictionary.name = "Atul";
nullPrototypeDictionary.role = "Developer";

show(
    "Null-prototype dictionary",
    nullPrototypeDictionary
);

show(
    "Own property using Object.has",
    Object.has(nullPrototypeDictionary, "name")
);


// ============================================================================
// 36. PERFORMANCE COMPARISON
// ============================================================================

section("36. Lookup Performance Experiment");

const largeObject = {};

for (let index = 0; index < 1_000_000; index++) {
    largeObject[index] = index * index;
}

const largeMap = new Map();

for (let index = 0; index < 1_000_000; index++) {
    largeMap.set(index, index * index);
}

const target = 999999;

let start = performance.now();
const objectResult = largeObject[target];
const objectTime = performance.now() - start;

start = performance.now();
const mapResult = largeMap.get(target);
const mapTime = performance.now() - start;

show("Object lookup result", objectResult);
show("Map lookup result", mapResult);
show("Object lookup timing in ms", objectTime);
show("Map lookup timing in ms", mapTime);

console.log(
    "Benchmark timings depend on the JavaScript runtime, hardware, and workload."
);


// ============================================================================
// 37. OBJECT FREEZING
// ============================================================================

section("37. Object.freeze()");

const configuration = Object.freeze({
    host: "localhost",
    port: 8000
});

show("Frozen configuration", configuration);

try {
    configuration.port = 9000;
} catch (error) {
    console.log("Strict-mode mutation error:", error.message);
}

show("Port remains", configuration.port);


// ============================================================================
// 38. MAP AND OBJECT CHOICES
// ============================================================================

section("38. Practical Selection Rules");

console.log("Use a plain object when:");
console.log("- Data naturally represents a record or JSON document.");
console.log("- Property names are mostly strings.");
console.log("- Interoperability with JSON is important.");

console.log("\nUse Map when:");
console.log("- Keys can have arbitrary types.");
console.log("- The collection is dynamically managed.");
console.log("- Frequent insertion/deletion and size checks are central.");
console.log("- Explicit key-value collection semantics are useful.");


// ============================================================================
// 39. INTEGRATED ORDER ANALYTICS
// ============================================================================

section("39. Integrated Dictionary Processing");

const orders = [
    {
        orderId: "O1001",
        customer: "Atul",
        category: "Electronics",
        amount: 75000,
        status: "completed"
    },
    {
        orderId: "O1002",
        customer: "Priya",
        category: "Books",
        amount: 2500,
        status: "completed"
    },
    {
        orderId: "O1003",
        customer: "Ravi",
        category: "Electronics",
        amount: 45000,
        status: "cancelled"
    },
    {
        orderId: "O1004",
        customer: "Neha",
        category: "Books",
        amount: 3500,
        status: "completed"
    }
];

const completedOrders = orders.filter(
    order => order.status === "completed"
);

const categorySales = new Map();

for (const order of completedOrders) {
    const previous = categorySales.get(order.category) ?? 0;

    categorySales.set(
        order.category,
        previous + order.amount
    );
}

const customerSales = new Map();

for (const order of completedOrders) {
    const previous = customerSales.get(order.customer) ?? 0;

    customerSales.set(
        order.customer,
        previous + order.amount
    );
}

const largestOrder = completedOrders.reduce(
    (largest, current) =>
        current.amount > largest.amount
            ? current
            : largest,
    completedOrders[0] ?? null
);

const analytics = {
    completedOrderCount: completedOrders.length,
    categorySales: Object.fromEntries(categorySales),
    customerSales: Object.fromEntries(customerSales),
    largestOrder
};

show("Order analytics", analytics);


// ============================================================================
// 40. ASSERTIONS
// ============================================================================

section("40. Behavioral Assertions");

function mergeSettings(defaultSettings, overrides) {
    return {
        ...defaultSettings,
        ...overrides
    };
}

console.assert(
    JSON.stringify(
        mergeSettings({ a: 1 }, { b: 2 })
    ) === JSON.stringify({ a: 1, b: 2 })
);

console.assert(
    mergeSettings({ a: 1 }, { a: 9 }).a === 9
);

console.assert(
    characterCounts.get("s") === 4
);

console.log("All JavaScript dictionary assertions passed.");


// ============================================================================
// 41. FINAL REFERENCE
// ============================================================================

section("41. Practical Reference");

const reference = {
    "Object.keys(object)": "Returns an array of own enumerable keys",
    "Object.values(object)": "Returns an array of own enumerable values",
    "Object.entries(object)": "Returns key-value pairs",
    "Object.fromEntries(entries)": "Creates an object from key-value pairs",
    "Object.assign(target, ...)": "Copies enumerable properties",
    "Object.has(object, key)": "Tests for an own property",
    "object[key]": "Reads or writes a property",
    "delete object[key]": "Removes a property",
    "map.set(key, value)": "Adds or replaces a Map entry",
    "map.get(key)": "Retrieves a Map value",
    "map.has(key)": "Checks for a Map key",
    "map.delete(key)": "Removes a Map entry",
    "map.clear()": "Removes all Map entries",
    "map.keys()": "Iterates Map keys",
    "map.values()": "Iterates Map values",
    "map.entries()": "Iterates Map key-value pairs"
};

for (const [operation, purpose] of Object.entries(reference)) {
    console.log(`${operation.padEnd(38)} -> ${purpose}`);
}

console.log(
    "\nDictionary-like collections are most effective when the data model, " +
    "key semantics, mutation behavior, validation requirements, and " +
    "serialization format are chosen deliberately."
);
