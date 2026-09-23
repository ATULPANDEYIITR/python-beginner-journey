/*
LIST METHODS
============

A comprehensive executable JavaScript study file focused on the concepts
represented by Python-style list methods and their JavaScript equivalents.

JavaScript arrays are ordered, mutable collections. They can contain values
of different types and are dynamically sized.

The JavaScript API does not use exactly the same method names as Python.
Important mappings include:

Python append()  -> JavaScript push()
Python extend()  -> JavaScript concat() or push(...items)
Python insert()  -> splice()
Python remove()  -> splice(), filter(), or find-based logic
Python pop()     -> pop() / splice()
Python clear()   -> array.length = 0 or splice()
Python index()   -> indexOf()
Python count()   -> filter().length
Python sort()    -> sort()
Python reverse() -> reverse()
Python copy()    -> slice(), spread syntax, or structuredClone()

The examples progress from basic array operations to validation, object
sorting, stack/queue behavior, shallow/deep copying, performance,
asynchronous processing, and an integrated inventory case study.
*/

"use strict";

// ---------------------------------------------------------------------------
// 1. Utility functions
// ---------------------------------------------------------------------------

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function show(label, value) {
    console.log(`${label}:`, value);
}


// ---------------------------------------------------------------------------
// 2. Creating arrays
// ---------------------------------------------------------------------------

section("2. Creating Arrays");

const empty = [];
const numbers = [10, 20, 30, 40];
const mixed = ["Atul", 42, 3.14, true, null];
const repeated = Array(3).fill("JavaScript");

show("Empty array", empty);
show("Numbers", numbers);
show("Mixed array", mixed);
show("Repeated values", repeated);


// ---------------------------------------------------------------------------
// 3. Indexing
// ---------------------------------------------------------------------------

section("3. Indexing");

const languages = ["Python", "JavaScript", "C++", "Java"];

show("First element", languages[0]);
show("Last element", languages[languages.length - 1]);

// JavaScript returns undefined for an out-of-range array index.
show("Out-of-range index", languages[100]);


// ---------------------------------------------------------------------------
// 4. push(): equivalent to adding one item
// ---------------------------------------------------------------------------

section("4. push()");

const items = ["Python", "JavaScript"];

const pushResult = items.push("C++");

show("Array after push()", items);
show("Return value of push()", pushResult);

// push() adds one object even when that object is itself an array.
items.push(["Java", "Go"]);
show("Nested array created by push()", items);


// ---------------------------------------------------------------------------
// 5. Extending an array
// ---------------------------------------------------------------------------

section("5. Extending Arrays");

const tools = ["Git", "Docker"];

// concat() creates a new array.
const extended = tools.concat(["Kubernetes", "Terraform"]);

show("Original", tools);
show("Extended", extended);

// Spread syntax can mutate an existing array with push().
tools.push("Kubernetes", "Terraform");
show("After push() with spread-like arguments", tools);


// ---------------------------------------------------------------------------
// 6. splice(): insertion and removal
// ---------------------------------------------------------------------------

section("6. splice()");

const values = [10, 20, 40];

// Insert 30 at index 2.
values.splice(2, 0, 30);

show("After insertion", values);

// Remove one element at index 1.
const removedValues = values.splice(1, 1);

show("Removed values", removedValues);
show("Array after removal", values);


// ---------------------------------------------------------------------------
// 7. pop()
// ---------------------------------------------------------------------------

section("7. pop()");

const stack = ["first", "second", "third"];

const last = stack.pop();

show("Removed last element", last);
show("Remaining stack", stack);


// ---------------------------------------------------------------------------
// 8. shift() and unshift()
// ---------------------------------------------------------------------------

section("8. shift() and unshift()");

const queue = ["request-2", "request-3"];

queue.unshift("request-1");
show("After unshift()", queue);

const firstRequest = queue.shift();

show("Removed first request", firstRequest);
show("Remaining queue", queue);


// ---------------------------------------------------------------------------
// 9. Clearing an array
// ---------------------------------------------------------------------------

section("9. Clearing Arrays");

const clearable = [1, 2, 3, 4];

clearable.length = 0;

show("After length = 0", clearable);


// ---------------------------------------------------------------------------
// 10. indexOf()
// ---------------------------------------------------------------------------

section("10. indexOf()");

const names = ["Asha", "Rahul", "Neha", "Asha"];

show("First Asha index", names.indexOf("Asha"));
show("Missing value", names.indexOf("Vikram"));


// ---------------------------------------------------------------------------
// 11. includes()
// ---------------------------------------------------------------------------

section("11. includes()");

show("Has Neha", names.includes("Neha"));
show("Has Vikram", names.includes("Vikram"));


// ---------------------------------------------------------------------------
// 12. count equivalent
// ---------------------------------------------------------------------------

section("12. Counting Values");

const votes = ["yes", "no", "yes", "yes", "no"];

const yesCount = votes.filter(vote => vote === "yes").length;
const noCount = votes.filter(vote => vote === "no").length;

show("Yes count", yesCount);
show("No count", noCount);


// ---------------------------------------------------------------------------
// 13. sort()
// ---------------------------------------------------------------------------

section("13. sort()");

const numericValues = [10, 2, 30, 4];

numericValues.sort();

show("Default JavaScript sort", numericValues);

// JavaScript's default sort compares string representations.
// Numeric sorting requires a comparison function.
numericValues.sort((a, b) => a - b);

show("Numeric ascending sort", numericValues);

numericValues.sort((a, b) => b - a);

show("Numeric descending sort", numericValues);


// ---------------------------------------------------------------------------
// 14. Sorting strings
// ---------------------------------------------------------------------------

section("14. String Sorting");

const words = ["banana", "Apple", "cherry", "apricot"];

words.sort((a, b) => a.localeCompare(b, undefined, {
    sensitivity: "base"
}));

show("Case-insensitive string sort", words);


// ---------------------------------------------------------------------------
// 15. reverse()
// ---------------------------------------------------------------------------

section("15. reverse()");

const sequence = [1, 2, 3, 4];

sequence.reverse();

show("Reversed sequence", sequence);


// ---------------------------------------------------------------------------
// 16. Copying arrays
// ---------------------------------------------------------------------------

section("16. Shallow Copies");

const original = [1, 2, 3];
const copied = [...original];

copied.push(4);

show("Original", original);
show("Copied", copied);
show("Same outer array?", original === copied);


// ---------------------------------------------------------------------------
// 17. Shallow copy with nested arrays
// ---------------------------------------------------------------------------

section("17. Nested Shallow Copies");

const nestedOriginal = [[1, 2], [3, 4]];
const nestedCopy = [...nestedOriginal];

nestedCopy[0].push(99);

show("Original after nested mutation", nestedOriginal);
show("Copy after nested mutation", nestedCopy);

console.log(
    "Shared nested object?",
    nestedOriginal[0] === nestedCopy[0]
);


// ---------------------------------------------------------------------------
// 18. Deep copy
// ---------------------------------------------------------------------------

section("18. Deep Copy");

const nestedData = [
    { name: "Asha", skills: ["Python", "SQL"] },
    { name: "Rahul", skills: ["JavaScript", "React"] }
];

const deepCopy = structuredClone(nestedData);

deepCopy[0].skills.push("Docker");

show("Original nested data", nestedData);
show("Deep copy", deepCopy);


// ---------------------------------------------------------------------------
// 19. map()
// ---------------------------------------------------------------------------

section("19. map()");

const inputNumbers = [1, 2, 3, 4, 5];

const squares = inputNumbers.map(number => number * number);

show("Original numbers", inputNumbers);
show("Squares", squares);


// ---------------------------------------------------------------------------
// 20. filter()
// ---------------------------------------------------------------------------

section("20. filter()");

const evenNumbers = inputNumbers.filter(number => number % 2 === 0);

show("Even numbers", evenNumbers);


// ---------------------------------------------------------------------------
// 21. reduce()
// ---------------------------------------------------------------------------

section("21. reduce()");

const total = inputNumbers.reduce(
    (sum, number) => sum + number,
    0
);

show("Total", total);


// ---------------------------------------------------------------------------
// 22. find() and findIndex()
// ---------------------------------------------------------------------------

section("22. find() and findIndex()");

const products = [
    { id: "P001", name: "Keyboard", stock: 12 },
    { id: "P002", name: "Mouse", stock: 4 },
    { id: "P003", name: "Monitor", stock: 0 }
];

const product = products.find(item => item.stock === 0);
const productIndex = products.findIndex(item => item.stock === 0);

show("Out-of-stock product", product);
show("Out-of-stock index", productIndex);


// ---------------------------------------------------------------------------
// 23. some() and every()
// ---------------------------------------------------------------------------

section("23. some() and every()");

show(
    "At least one item is out of stock",
    products.some(item => item.stock === 0)
);

show(
    "Every item has non-negative stock",
    products.every(item => item.stock >= 0)
);


// ---------------------------------------------------------------------------
// 24. Iteration
// ---------------------------------------------------------------------------

section("24. Iteration");

for (const productItem of products) {
    console.log(productItem.name);
}

products.forEach((productItem, index) => {
    console.log(index, productItem.name);
});


// ---------------------------------------------------------------------------
// 25. Stack implementation
// ---------------------------------------------------------------------------

section("25. Stack");

const taskStack = [];

taskStack.push("design");
taskStack.push("implement");
taskStack.push("test");

while (taskStack.length > 0) {
    const task = taskStack.pop();
    console.log("Processing:", task);
}


// ---------------------------------------------------------------------------
// 26. Queue implementation
// ---------------------------------------------------------------------------

section("26. Queue");

const requestQueue = [];
let queueHead = 0;

requestQueue.push("request-1");
requestQueue.push("request-2");
requestQueue.push("request-3");

// Using shift() repeatedly can become inefficient for very large queues.
// A head index avoids repeatedly shifting all remaining elements.
while (queueHead < requestQueue.length) {
    const request = requestQueue[queueHead];
    queueHead += 1;
    console.log("Handling:", request);
}


// ---------------------------------------------------------------------------
// 27. Deduplication
// ---------------------------------------------------------------------------

section("27. Deduplication");

const duplicateValues = [
    "Python",
    "Java",
    "Python",
    "C++",
    "Java"
];

const uniqueValues = [...new Set(duplicateValues)];

show("Original", duplicateValues);
show("Unique values", uniqueValues);


// ---------------------------------------------------------------------------
// 28. Array destructuring
// ---------------------------------------------------------------------------

section("28. Destructuring");

const coordinates = [10, 20, 30];

const [x, y, z] = coordinates;

show("x", x);
show("y", y);
show("z", z);

const [first, ...remaining] = coordinates;

show("First", first);
show("Remaining", remaining);


// ---------------------------------------------------------------------------
// 29. Validation
// ---------------------------------------------------------------------------

section("29. Validation");

function parsePositiveIntegers(input) {
    if (typeof input !== "string" || input.trim() === "") {
        throw new Error("Input must be a non-empty string.");
    }

    const result = [];

    for (const part of input.split(",")) {
        const cleaned = part.trim();

        if (!/^\d+$/.test(cleaned)) {
            throw new Error(`Invalid positive integer: ${cleaned}`);
        }

        const value = Number(cleaned);

        if (!Number.isSafeInteger(value) || value <= 0) {
            throw new Error(`Invalid numeric value: ${cleaned}`);
        }

        result.push(value);
    }

    return result;
}

for (const sample of ["10, 20, 30", "5, 0, 8", "10, abc, 20"]) {
    try {
        console.log(sample, "->", parsePositiveIntegers(sample));
    } catch (error) {
        console.log(sample, "-> validation error:", error.message);
    }
}


// ---------------------------------------------------------------------------
// 30. Sorting objects
// ---------------------------------------------------------------------------

section("30. Sorting Objects");

const employees = [
    { name: "Asha", salary: 85000 },
    { name: "Rahul", salary: 65000 },
    { name: "Neha", salary: 92000 }
];

employees.sort((a, b) => a.salary - b.salary);

show("Employees by salary", employees);

employees.sort((a, b) => {
    if (b.salary !== a.salary) {
        return b.salary - a.salary;
    }

    return a.name.localeCompare(b.name);
});

show("Employees by salary descending and name ascending", employees);


// ---------------------------------------------------------------------------
// 31. Mutation versus non-mutating methods
// ---------------------------------------------------------------------------

section("31. Mutation and Non-Mutation");

const source = [3, 1, 2];

const sortedSource = [...source].sort((a, b) => a - b);

show("Original", source);
show("Sorted copy", sortedSource);

// sort(), reverse(), push(), pop(), shift(), unshift(), splice() mutate.
// map(), filter(), concat(), slice() create new arrays.


// ---------------------------------------------------------------------------
// 32. Slice versus splice
// ---------------------------------------------------------------------------

section("32. slice() versus splice()");

const sliceSource = [10, 20, 30, 40];

const sliceResult = sliceSource.slice(1, 3);

show("slice() result", sliceResult);
show("After slice()", sliceSource);

const spliceSource = [10, 20, 30, 40];
const spliceResult = spliceSource.splice(1, 2);

show("splice() result", spliceResult);
show("After splice()", spliceSource);


// ---------------------------------------------------------------------------
// 33. Flattening nested arrays
// ---------------------------------------------------------------------------

section("33. Flattening");

const matrix = [
    [1, 2],
    [3, 4],
    [5, 6]
];

const flattened = matrix.flat();

show("Matrix", matrix);
show("Flattened", flattened);

const deeplyNested = [1, [2, [3, [4]]]];
show("Deep flatten", deeplyNested.flat(Infinity));


// ---------------------------------------------------------------------------
// 34. Practical inventory pipeline
// ---------------------------------------------------------------------------

section("34. Inventory Pipeline");

const inventory = [
    { sku: "KB001", name: "Keyboard", stock: 12, price: 2500 },
    { sku: "MS001", name: "Mouse", stock: 4, price: 1200 },
    { sku: "MN001", name: "Monitor", stock: 0, price: 18000 },
    { sku: "HD001", name: "Hard Drive", stock: 7, price: 6500 }
];

const lowStock = inventory.filter(
    item => item.stock > 0 && item.stock <= 5
);

const outOfStock = inventory.filter(
    item => item.stock === 0
);

const inventoryValue = inventory.reduce(
    (totalValue, item) => totalValue + item.stock * item.price,
    0
);

const sortedInventory = [...inventory].sort(
    (a, b) => b.price - a.price
);

show("Low stock", lowStock);
show("Out of stock", outOfStock);
show("Total inventory value", inventoryValue);
show("Sorted inventory", sortedInventory);


// ---------------------------------------------------------------------------
// 35. Edge cases
// ---------------------------------------------------------------------------

section("35. Edge Cases");

const emptyArray = [];

show("Empty array", emptyArray);
show("pop() from empty array", emptyArray.pop());
show("shift() from empty array", emptyArray.shift());
show("indexOf() missing value", emptyArray.indexOf("x"));
show("includes() missing value", emptyArray.includes("x"));


// ---------------------------------------------------------------------------
// 36. Equality and object references
// ---------------------------------------------------------------------------

section("36. Object Equality");

const objectA = { id: 1 };
const objectB = { id: 1 };

const objectArray = [objectA];

console.log("Same object reference:", objectArray.includes(objectA));
console.log("Different object with same data:", objectArray.includes(objectB));


// ---------------------------------------------------------------------------
// 37. Sparse arrays
// ---------------------------------------------------------------------------

section("37. Sparse Arrays");

const sparse = [];
sparse[2] = "value";

show("Sparse array", sparse);
show("Length", sparse.length);
show("Index 0", sparse[0]);

// Sparse arrays contain holes rather than explicit undefined values.
console.log("Has own index 0:", Object.hasOwn(sparse, 0));
console.log("Has own index 2:", Object.hasOwn(sparse, 2));


// ---------------------------------------------------------------------------
// 38. Performance comparison concept
// ---------------------------------------------------------------------------

section("38. Performance Considerations");

const largeArray = Array.from(
    { length: 200000 },
    (_, index) => index
);

console.time("push");
largeArray.push(200000);
console.timeEnd("push");

console.time("includes");
largeArray.includes(200000);
console.timeEnd("includes");

console.log(
    "Timing varies with hardware, runtime, memory pressure, and workload."
);


// ---------------------------------------------------------------------------
// 39. Async processing of array items
// ---------------------------------------------------------------------------

section("39. Asynchronous Array Processing");

function simulateRequest(id) {
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({
                id,
                status: "processed"
            });
        }, 5);
    });
}

async function processRequests(ids) {
    // Promise.all processes independent operations concurrently from the
    // caller's perspective, while preserving result order.
    return Promise.all(ids.map(id => simulateRequest(id)));
}


// ---------------------------------------------------------------------------
// 40. Custom helper methods
// ---------------------------------------------------------------------------

section("40. Custom List-Like Helpers");

function addUnique(array, value) {
    if (array.includes(value)) {
        return false;
    }

    array.push(value);
    return true;
}

const tags = [];

console.log("Added Python:", addUnique(tags, "Python"));
console.log("Added Python again:", addUnique(tags, "Python"));

show("Tags", tags);


// ---------------------------------------------------------------------------
// 41. Immutable-style update
// ---------------------------------------------------------------------------

section("41. Immutable-Style Updates");

const state = {
    selected: ["Python", "JavaScript"],
    count: 2
};

const nextState = {
    ...state,
    selected: [...state.selected, "C++"],
    count: state.count + 1
};

show("Original state", state);
show("Next state", nextState);


// ---------------------------------------------------------------------------
// 42. Integrated case study
// ---------------------------------------------------------------------------

section("42. Integrated Task Management Case Study");

const tasks = [
    {
        id: "T001",
        title: "Design database schema",
        priority: 3,
        status: "open"
    },
    {
        id: "T002",
        title: "Implement API",
        priority: 1,
        status: "open"
    },
    {
        id: "T003",
        title: "Write tests",
        priority: 2,
        status: "done"
    }
];

tasks.push({
    id: "T004",
    title: "Deploy application",
    priority: 1,
    status: "open"
});

const completedTasks = tasks.filter(
    task => task.status === "done"
);

const openTasks = tasks.filter(
    task => task.status === "open"
);

openTasks.sort((a, b) => a.priority - b.priority);

show("Completed tasks", completedTasks);
show("Open tasks by priority", openTasks);


// ---------------------------------------------------------------------------
// 43. Main asynchronous demonstration
// ---------------------------------------------------------------------------

async function main() {
    const results = await processRequests(["R001", "R002", "R003"]);

    section("43. Async Results");
    show("Processed requests", results);

    console.log("\nJavaScript list-method study execution completed.");
}

main().catch(error => {
    console.error("Unexpected execution error:", error);
});
