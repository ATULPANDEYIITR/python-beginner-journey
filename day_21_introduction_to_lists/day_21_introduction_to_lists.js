/*
 * Introduction to Lists
 * ======================
 *
 * JavaScript uses arrays for the role commonly played by lists in Python.
 * This file develops array knowledge from beginner level through advanced
 * practical data processing.
 *
 * Topics demonstrated:
 * - Creating arrays
 * - Indexing
 * - Updating
 * - Adding and removing values
 * - Array length
 * - Iteration
 * - map, filter, reduce
 * - find, findIndex, some, every
 * - includes and indexOf
 * - slice and splice
 * - sort and stable multi-key sorting
 * - copying and references
 * - nested arrays
 * - flattening
 * - destructuring
 * - spread syntax
 * - rest parameters
 * - stacks and queues
 * - grouping
 * - frequency counting
 * - chunking
 * - sliding windows
 * - binary search
 * - validation
 * - error handling
 * - performance considerations
 * - a practical student and inventory case study
 *
 * Run with:
 * node lists.js
 */

"use strict";

// -----------------------------------------------------------------------------
// 1. Basic arrays
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("1. Basic arrays");
console.log("=".repeat(78));

const emptyArray = [];
const numbers = [10, 20, 30, 40];
const mixedValues = [42, "JavaScript", 3.14, true, null];

console.log("Empty array:", emptyArray);
console.log("Numbers:", numbers);
console.log("Mixed values:", mixedValues);

// Arrays can contain duplicate values.
const duplicates = [5, 5, 7, 7, 7, 9];
console.log("Duplicates:", duplicates);


// -----------------------------------------------------------------------------
// 2. Array indexing
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("2. Array indexing");
console.log("=".repeat(78));

const languages = ["Python", "JavaScript", "C++", "Java", "Go"];

console.log("First:", languages[0]);
console.log("Second:", languages[1]);
console.log("Last:", languages[languages.length - 1]);

/*
 * JavaScript does not use Python's negative-index syntax directly.
 * at(-1) is the modern way to retrieve an item from the end.
 */
console.log("Last using at(-1):", languages.at(-1));
console.log("Second-last using at(-2):", languages.at(-2));


// -----------------------------------------------------------------------------
// 3. Updating values
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("3. Updating values");
console.log("=".repeat(78));

const temperatures = [25, 27, 30, 29];

console.log("Before:", temperatures);

temperatures[2] = 31;

console.log("After updating index 2:", temperatures);


// -----------------------------------------------------------------------------
// 4. Adding values
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("4. Adding values");
console.log("=".repeat(78));

const shopping = ["milk", "bread"];

shopping.push("eggs");
console.log("After push:", shopping);

shopping.unshift("fruit");
console.log("After unshift:", shopping);

shopping.splice(1, 0, "rice");
console.log("After inserting with splice:", shopping);

/*
 * push() adds to the end.
 * unshift() adds to the beginning.
 * splice() can insert, remove, and replace.
 *
 * Frequent unshift() operations can be expensive because existing elements
 * need to move to new indexes.
 */


// -----------------------------------------------------------------------------
// 5. Removing values
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("5. Removing values");
console.log("=".repeat(78));

const items = ["pen", "book", "bag", "pencil"];

const lastItem = items.pop();
console.log("Popped:", lastItem);
console.log("After pop:", items);

const firstItem = items.shift();
console.log("Shifted:", firstItem);
console.log("After shift:", items);

items.splice(1, 1);
console.log("After splice removal:", items);


// -----------------------------------------------------------------------------
// 6. Length and membership
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("6. Length and membership");
console.log("=".repeat(78));

const values = [10, 20, 30, 40];

console.log("Length:", values.length);
console.log("Contains 20:", values.includes(20));
console.log("Contains 99:", values.includes(99));

console.log("Index of 30:", values.indexOf(30));
console.log("Index of 99:", values.indexOf(99));


// -----------------------------------------------------------------------------
// 7. Iteration
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("7. Iteration");
console.log("=".repeat(78));

const cities = ["Lucknow", "Delhi", "Mumbai", "Pune"];

for (const city of cities) {
    console.log("City:", city);
}

cities.forEach((city, index) => {
    console.log(`${index}: ${city}`);
});


// -----------------------------------------------------------------------------
// 8. Slice versus splice
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("8. slice() versus splice()");
console.log("=".repeat(78));

const original = [0, 1, 2, 3, 4, 5];

const portion = original.slice(1, 4);

console.log("Original after slice:", original);
console.log("slice(1, 4):", portion);

const mutableExample = [0, 1, 2, 3, 4, 5];

const removed = mutableExample.splice(2, 2);

console.log("Removed using splice:", removed);
console.log("Array after splice:", mutableExample);

/*
 * slice() returns a portion without changing the original array.
 * splice() changes the original array.
 */


// -----------------------------------------------------------------------------
// 9. Mapping
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("9. map()");
console.log("=".repeat(78));

const baseNumbers = [1, 2, 3, 4, 5];

const squares = baseNumbers.map(number => number * number);
const doubled = baseNumbers.map(number => number * 2);

console.log("Squares:", squares);
console.log("Doubled:", doubled);
console.log("Original:", baseNumbers);


// -----------------------------------------------------------------------------
// 10. Filtering
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("10. filter()");
console.log("=".repeat(78));

const evenNumbers = baseNumbers.filter(number => number % 2 === 0);
const greaterThanThree = baseNumbers.filter(number => number > 3);

console.log("Even numbers:", evenNumbers);
console.log("Greater than 3:", greaterThanThree);


// -----------------------------------------------------------------------------
// 11. Reduction
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("11. reduce()");
console.log("=".repeat(78));

const sum = baseNumbers.reduce(
    (total, number) => total + number,
    0
);

console.log("Sum:", sum);

const product = baseNumbers.reduce(
    (total, number) => total * number,
    1
);

console.log("Product:", product);

/*
 * reduce() is useful when a list must be transformed into one accumulated
 * result, such as a total, product, lookup object, or summary.
 */


// -----------------------------------------------------------------------------
// 12. some() and every()
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("12. some() and every()");
console.log("=".repeat(78));

console.log(
    "Some number is greater than 4:",
    baseNumbers.some(number => number > 4)
);

console.log(
    "Every number is positive:",
    baseNumbers.every(number => number > 0)
);

console.log("Empty every:", [].every(() => false));
console.log("Empty some:", [].some(() => true));


// -----------------------------------------------------------------------------
// 13. find() and findIndex()
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("13. find() and findIndex()");
console.log("=".repeat(78));

const studentRecords = [
    { name: "Asha", marks: 91 },
    { name: "Ravi", marks: 78 },
    { name: "Neha", marks: 96 }
];

const highScorer = studentRecords.find(student => student.marks >= 90);
const highScorerIndex = studentRecords.findIndex(
    student => student.marks >= 90
);

console.log("First high scorer:", highScorer);
console.log("Index:", highScorerIndex);


// -----------------------------------------------------------------------------
// 14. Sorting
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("14. Sorting");
console.log("=".repeat(78));

const unsorted = [10, 2, 30, 4, 25];

console.log(
    "Lexicographic/default sort:",
    [...unsorted].sort()
);

console.log(
    "Numeric ascending:",
    [...unsorted].sort((a, b) => a - b)
);

console.log(
    "Numeric descending:",
    [...unsorted].sort((a, b) => b - a)
);

/*
 * JavaScript's default sort compares values as strings.
 *
 * Therefore [10, 2, 30].sort() does not perform numeric sorting.
 *
 * For numbers, provide a comparator.
 */


// -----------------------------------------------------------------------------
// 15. Sorting objects
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("15. Sorting objects");
console.log("=".repeat(78));

const employees = [
    { name: "Asha", department: "IT", salary: 90000 },
    { name: "Ravi", department: "Finance", salary: 85000 },
    { name: "Neha", department: "IT", salary: 95000 },
    { name: "Arjun", department: "Finance", salary: 88000 }
];

const bySalary = [...employees].sort(
    (a, b) => b.salary - a.salary
);

console.log("By salary:", bySalary);

const byDepartmentThenSalary = [...employees].sort(
    (a, b) =>
        a.department.localeCompare(b.department) ||
        b.salary - a.salary
);

console.log("By department and salary:", byDepartmentThenSalary);


// -----------------------------------------------------------------------------
// 16. Copying and references
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("16. References and copies");
console.log("=".repeat(78));

const first = [1, 2, 3];
const reference = first;

reference[0] = 999;

console.log("First after reference modification:", first);
console.log("Reference:", reference);

/*
 * Arrays are objects. Assignment copies the reference, not the elements.
 *
 * Spread syntax creates a new shallow array.
 */

const independentCopy = [...first];

independentCopy[0] = 100;

console.log("Original:", first);
console.log("Independent shallow copy:", independentCopy);


// -----------------------------------------------------------------------------
// 17. Nested arrays and shallow copying
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("17. Nested arrays");
console.log("=".repeat(78));

const nested = [
    [1, 2],
    [3, 4]
];

const shallowNestedCopy = [...nested];

shallowNestedCopy[0][0] = 999;

console.log("Original nested array:", nested);
console.log("Shallow nested copy:", shallowNestedCopy);

/*
 * The outer array is copied, but the inner arrays are still shared.
 *
 * structuredClone() creates a deep clone for many ordinary data structures.
 */

const deepNestedCopy = structuredClone(nested);
deepNestedCopy[1][1] = 777;

console.log("Original after deep clone modification:", nested);
console.log("Deep copy:", deepNestedCopy);


// -----------------------------------------------------------------------------
// 18. Destructuring
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("18. Array destructuring");
console.log("=".repeat(78));

const coordinates = [10, 20, 30];

const [x, y, z] = coordinates;

console.log("x:", x);
console.log("y:", y);
console.log("z:", z);

const [firstValue, , thirdValue] = coordinates;

console.log("First:", firstValue);
console.log("Third:", thirdValue);


// -----------------------------------------------------------------------------
// 19. Rest syntax
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("19. Rest syntax");
console.log("=".repeat(78));

const [head, ...tail] = [10, 20, 30, 40];

console.log("Head:", head);
console.log("Tail:", tail);


// -----------------------------------------------------------------------------
// 20. Spread syntax
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("20. Spread syntax");
console.log("=".repeat(78));

const firstGroup = [1, 2, 3];
const secondGroup = [4, 5, 6];

const merged = [...firstGroup, ...secondGroup];

console.log("Merged:", merged);

const withExtraValue = [0, ...firstGroup, 99];

console.log("With extra values:", withExtraValue);


// -----------------------------------------------------------------------------
// 21. Flattening
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("21. Flattening");
console.log("=".repeat(78));

const nestedNumbers = [
    [1, 2],
    [3, [4, 5]],
    6
];

console.log("One level:", nestedNumbers.flat());
console.log("All levels:", nestedNumbers.flat(Infinity));


// -----------------------------------------------------------------------------
// 22. Flat mapping
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("22. flatMap()");
console.log("=".repeat(78));

const words = ["red blue", "green yellow"];

const splitWords = words.flatMap(
    wordGroup => wordGroup.split(" ")
);

console.log("Split words:", splitWords);


// -----------------------------------------------------------------------------
// 23. Frequency counting
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("23. Frequency counting");
console.log("=".repeat(78));

function countFrequencies(values) {
    const frequencies = new Map();

    for (const value of values) {
        frequencies.set(
            value,
            (frequencies.get(value) ?? 0) + 1
        );
    }

    return frequencies;
}

const frequencyValues = ["A", "B", "A", "C", "B", "A"];

console.log(
    "Frequency:",
    [...countFrequencies(frequencyValues).entries()]
);


// -----------------------------------------------------------------------------
// 24. Deduplication
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("24. Deduplication");
console.log("=".repeat(78));

const repeated = [4, 2, 4, 7, 2, 9, 7, 1];

const unique = [...new Set(repeated)];

console.log("Original:", repeated);
console.log("Unique:", unique);


// -----------------------------------------------------------------------------
// 25. Grouping
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("25. Grouping records");
console.log("=".repeat(78));

function groupBy(records, keyFunction) {
    const groups = new Map();

    for (const record of records) {
        const key = keyFunction(record);

        if (!groups.has(key)) {
            groups.set(key, []);
        }

        groups.get(key).push(record);
    }

    return groups;
}

const groupedEmployees = groupBy(
    employees,
    employee => employee.department
);

for (const [department, members] of groupedEmployees) {
    console.log(department, members);
}


// -----------------------------------------------------------------------------
// 26. Chunking
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("26. Chunking");
console.log("=".repeat(78));

function chunkArray(values, size) {
    if (!Number.isInteger(size) || size <= 0) {
        throw new RangeError("Chunk size must be a positive integer.");
    }

    const chunks = [];

    for (let index = 0; index < values.length; index += size) {
        chunks.push(values.slice(index, index + size));
    }

    return chunks;
}

console.log(
    "Chunks:",
    chunkArray([1, 2, 3, 4, 5, 6, 7], 3)
);

try {
    chunkArray([1, 2, 3], 0);
} catch (error) {
    console.log("Handled invalid chunk size:", error.message);
}


// -----------------------------------------------------------------------------
// 27. Sliding windows
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("27. Sliding windows");
console.log("=".repeat(78));

function slidingWindows(values, size) {
    if (!Number.isInteger(size) || size <= 0) {
        throw new RangeError("Window size must be positive.");
    }

    const result = [];

    for (let index = 0; index + size <= values.length; index++) {
        result.push(values.slice(index, index + size));
    }

    return result;
}

console.log(
    slidingWindows([20, 22, 24, 23, 25], 3)
);


// -----------------------------------------------------------------------------
// 28. Rotation
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("28. Array rotation");
console.log("=".repeat(78));

function rotateRight(values, positions) {
    if (values.length === 0) {
        return [];
    }

    const normalized = ((positions % values.length) + values.length) %
        values.length;

    return [
        ...values.slice(-normalized),
        ...values.slice(0, values.length - normalized)
    ];
}

console.log("Rotate by 2:", rotateRight([1, 2, 3, 4, 5], 2));
console.log("Rotate by 7:", rotateRight([1, 2, 3, 4, 5], 7));
console.log("Rotate by -1:", rotateRight([1, 2, 3, 4, 5], -1));


// -----------------------------------------------------------------------------
// 29. Binary search
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("29. Binary search");
console.log("=".repeat(78));

function binarySearch(values, target) {
    let left = 0;
    let right = values.length - 1;

    while (left <= right) {
        const middle = Math.floor((left + right) / 2);

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

const sortedNumbers = [10, 20, 30, 40, 50, 60];

console.log("Index of 40:", binarySearch(sortedNumbers, 40));
console.log("Index of 99:", binarySearch(sortedNumbers, 99));


// -----------------------------------------------------------------------------
// 30. Stack
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("30. Stack");
console.log("=".repeat(78));

const stack = [];

stack.push("first");
stack.push("second");
stack.push("third");

while (stack.length > 0) {
    console.log("Popped:", stack.pop());
}


// -----------------------------------------------------------------------------
// 31. Queue
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("31. Queue");
console.log("=".repeat(78));

/*
 * shift() removes the first element but can require moving many elements.
 * For very high-volume queues, a head-index technique or a specialized
 * queue implementation can avoid repeated shifting.
 */

const queue = ["customer-1", "customer-2", "customer-3"];
let queueHead = 0;

while (queueHead < queue.length) {
    console.log("Serving:", queue[queueHead]);
    queueHead++;
}


// -----------------------------------------------------------------------------
// 32. Matrix processing
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("32. Matrix processing");
console.log("=".repeat(78));

const matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
];

for (const row of matrix) {
    console.log(row);
}

console.log("Element [1][2]:", matrix[1][2]);

const flattenedMatrix = matrix.flat();

console.log("Flattened:", flattenedMatrix);


// -----------------------------------------------------------------------------
// 33. Matrix transpose
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("33. Matrix transpose");
console.log("=".repeat(78));

function transposeMatrix(matrix) {
    if (matrix.length === 0) {
        return [];
    }

    const width = matrix[0].length;

    if (!matrix.every(row => row.length === width)) {
        throw new Error("Matrix must be rectangular.");
    }

    return Array.from(
        { length: width },
        (_, column) => matrix.map(row => row[column])
    );
}

console.log(
    transposeMatrix([
        [1, 2, 3],
        [4, 5, 6]
    ])
);


// -----------------------------------------------------------------------------
// 34. Safe numeric validation
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("34. Numeric validation");
console.log("=".repeat(78));

function average(values) {
    if (!Array.isArray(values)) {
        throw new TypeError("Expected an array.");
    }

    if (values.length === 0) {
        throw new RangeError("At least one value is required.");
    }

    if (!values.every(
        value => typeof value === "number" && Number.isFinite(value)
    )) {
        throw new TypeError("Every value must be a finite number.");
    }

    return values.reduce((total, value) => total + value, 0) /
        values.length;
}

console.log("Average:", average([10, 20, 30]));

try {
    average([10, "20", 30]);
} catch (error) {
    console.log("Validation error:", error.message);
}


// -----------------------------------------------------------------------------
// 35. Practical student analysis
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("35. Student analysis");
console.log("=".repeat(78));

const students = [
    { name: "Asha", marks: [88, 91, 84] },
    { name: "Ravi", marks: [72, 68, 75] },
    { name: "Neha", marks: [95, 93, 97] },
    { name: "Arjun", marks: [35, 74, 61] }
];

function studentAverage(student) {
    return average(student.marks);
}

function studentPassed(student) {
    return (
        student.marks.length > 0 &&
        student.marks.every(mark => mark >= 40)
    );
}

for (const student of students) {
    console.log(
        student.name,
        "Average:",
        studentAverage(student).toFixed(2),
        "Passed:",
        studentPassed(student)
    );
}

const topStudent = [...students].sort(
    (a, b) => studentAverage(b) - studentAverage(a)
)[0];

console.log("Highest average:", topStudent.name);


// -----------------------------------------------------------------------------
// 36. Inventory analysis
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("36. Inventory analysis");
console.log("=".repeat(78));

const inventory = [
    { name: "Laptop", price: 65000, quantity: 3 },
    { name: "Mouse", price: 1200, quantity: 0 },
    { name: "Keyboard", price: 2500, quantity: 8 },
    { name: "Monitor", price: 18000, quantity: 2 }
];

const outOfStock = inventory.filter(
    product => product.quantity === 0
);

const inventoryValue = inventory.reduce(
    (total, product) =>
        total + product.price * product.quantity,
    0
);

console.log(
    "Out of stock:",
    outOfStock.map(product => product.name)
);

console.log("Inventory value:", inventoryValue);


// -----------------------------------------------------------------------------
// 37. Practical transaction processing
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("37. Transaction processing");
console.log("=".repeat(78));

const transactions = [
    { id: 101, category: "food", amount: 450 },
    { id: 102, category: "travel", amount: 2500 },
    { id: 103, category: "food", amount: 700 },
    { id: 104, category: "technology", amount: 15000 },
    { id: 105, category: "travel", amount: 1200 }
];

const validTransactions = transactions.filter(
    transaction =>
        Number.isFinite(transaction.amount) &&
        transaction.amount >= 0
);

const totalSpending = validTransactions.reduce(
    (total, transaction) => total + transaction.amount,
    0
);

const largestTransaction = validTransactions.reduce(
    (largest, transaction) =>
        transaction.amount > largest.amount ? transaction : largest
);

const categoryTotals = new Map();

for (const transaction of validTransactions) {
    categoryTotals.set(
        transaction.category,
        (categoryTotals.get(transaction.category) ?? 0) +
            transaction.amount
    );
}

console.log("Valid transactions:", validTransactions.length);
console.log("Total spending:", totalSpending);
console.log("Largest transaction:", largestTransaction);

console.log("Category totals:");
for (const [category, amount] of categoryTotals) {
    console.log(`  ${category}: ${amount}`);
}


// -----------------------------------------------------------------------------
// 38. Custom reusable list processor
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("38. Reusable list processor");
console.log("=".repeat(78));

class ListProcessor {
    constructor(values = []) {
        if (!Array.isArray(values)) {
            throw new TypeError("ListProcessor requires an array.");
        }

        this.values = [...values];
    }

    add(value) {
        this.values.push(value);
        return this;
    }

    removeFirstMatch(predicate) {
        const index = this.values.findIndex(predicate);

        if (index === -1) {
            return undefined;
        }

        return this.values.splice(index, 1)[0];
    }

    filter(predicate) {
        return new ListProcessor(this.values.filter(predicate));
    }

    map(transform) {
        return new ListProcessor(this.values.map(transform));
    }

    sort(compareFunction) {
        this.values.sort(compareFunction);
        return this;
    }

    toArray() {
        return [...this.values];
    }
}

const processor = new ListProcessor([5, 2, 8, 1]);

processor
    .add(10)
    .sort((a, b) => a - b);

console.log("Processed values:", processor.toArray());

const evenProcessor = processor.filter(
    value => value % 2 === 0
);

console.log("Even values:", evenProcessor.toArray());


// -----------------------------------------------------------------------------
// 39. Error handling
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("39. Error handling");
console.log("=".repeat(78));

function removeAt(values, index) {
    if (!Number.isInteger(index)) {
        throw new TypeError("Index must be an integer.");
    }

    if (index < 0 || index >= values.length) {
        throw new RangeError("Index is outside the valid range.");
    }

    return values.splice(index, 1)[0];
}

const removable = ["a", "b", "c"];

console.log("Removed:", removeAt(removable, 1));
console.log("Remaining:", removable);

try {
    removeAt(removable, 99);
} catch (error) {
    console.log("Handled:", error.message);
}


// -----------------------------------------------------------------------------
// 40. Performance considerations
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("40. Performance considerations");
console.log("=".repeat(78));

/*
 * Typical array behavior:
 *
 * Direct index access        approximately O(1)
 * push()                     amortized O(1)
 * pop()                      O(1)
 * shift()                    O(n)
 * unshift()                  O(n)
 * includes()                 O(n)
 * indexOf()                  O(n)
 * splice()                   commonly O(n)
 * sort()                     O(n log n) typical comparison-based behavior
 * map()                      O(n)
 * filter()                   O(n)
 * reduce()                   O(n)
 *
 * Complexity alone does not determine real performance. Data size,
 * JavaScript engine behavior, memory locality, allocation, and workload
 * patterns also matter.
 */

const performanceData = Array.from(
    { length: 100 },
    (_, index) => index
);

console.log(
    "Direct access:",
    performanceData[50]
);


// -----------------------------------------------------------------------------
// 41. Common mistake: sparse arrays
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("41. Sparse arrays");
console.log("=".repeat(78));

const sparse = [];

sparse[3] = "value";

console.log("Sparse array:", sparse);
console.log("Length:", sparse.length);

console.log(
    "Index 0 exists:",
    Object.hasOwn(sparse, 0)
);

console.log(
    "Index 3 exists:",
    Object.hasOwn(sparse, 3)
);

/*
 * Setting a distant index can create holes.
 * A sparse array is not identical to an array filled with undefined values.
 */


// -----------------------------------------------------------------------------
// 42. Common mistake: reference sharing
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("42. Reference sharing in repeated objects");
console.log("=".repeat(78));

const sharedObject = { value: 0 };

const sharedArray = Array(3).fill(sharedObject);

sharedArray[0].value = 100;

console.log("Shared object array:", sharedArray);

/*
 * Array(3).fill(sharedObject) places the same object reference into all
 * positions.
 *
 * To create independent objects, create a new object for each position.
 */

const independentObjects = Array.from(
    { length: 3 },
    () => ({ value: 0 })
);

independentObjects[0].value = 100;

console.log("Independent objects:", independentObjects);


// -----------------------------------------------------------------------------
// 43. Testing
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("43. Assertions");
console.log("=".repeat(78));

function runTests() {
    console.assert(
        JSON.stringify(chunkArray([1, 2, 3, 4, 5], 2)) ===
        JSON.stringify([[1, 2], [3, 4], [5]]),
        "chunkArray test failed"
    );

    console.assert(
        JSON.stringify(rotateRight([1, 2, 3], 1)) ===
        JSON.stringify([3, 1, 2]),
        "rotateRight test failed"
    );

    console.assert(
        binarySearch([10, 20, 30], 20) === 1,
        "binarySearch found test failed"
    );

    console.assert(
        binarySearch([10, 20, 30], 99) === -1,
        "binarySearch missing test failed"
    );

    console.assert(
        JSON.stringify([...new Set([1, 1, 2, 3])]) ===
        JSON.stringify([1, 2, 3]),
        "deduplication test failed"
    );

    console.assert(
        average([10, 20, 30]) === 20,
        "average test failed"
    );

    console.log("Assertions completed.");
}

runTests();


// -----------------------------------------------------------------------------
// 44. Integrated workflow
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("44. Integrated list-processing workflow");
console.log("=".repeat(78));

const rawScores = [
    "88",
    "91",
    "",
    "invalid",
    "76",
    "95"
];

const parsedScores = [];

for (const rawScore of rawScores) {
    const trimmed = rawScore.trim();

    if (trimmed === "") {
        continue;
    }

    const numericValue = Number(trimmed);

    if (Number.isFinite(numericValue)) {
        parsedScores.push(numericValue);
    } else {
        console.log(`Skipped invalid score: ${rawScore}`);
    }
}

const passingScores = parsedScores.filter(score => score >= 40);
const sortedScores = [...passingScores].sort((a, b) => b - a);

console.log("Parsed scores:", parsedScores);
console.log("Passing scores:", passingScores);
console.log("Sorted scores:", sortedScores);
console.log("Average:", average(passingScores));


// -----------------------------------------------------------------------------
// 45. Final practical distinctions
// -----------------------------------------------------------------------------

console.log("\n" + "=".repeat(78));
console.log("45. Practical distinctions");
console.log("=".repeat(78));

console.log(
    "Use arrays for ordered collections where positional access and iteration matter."
);

console.log(
    "Use Set when uniqueness and membership are primary concerns."
);

console.log(
    "Use Map when values need explicit key-based lookup."
);

console.log(
    "Use a queue design that avoids repeated shift() operations for high-volume workloads."
);

console.log(
    "Use immutable-style transformations such as map/filter when preserving the original array improves clarity."
);

console.log(
    "Use in-place methods such as sort/splice when mutation is intentional and controlled."
);

console.log("\nStudy file completed.");
