/*
 * LIST INDEXING AND SLICING
 * =========================
 *
 * A comprehensive executable JavaScript study program covering array
 * indexing and slicing from beginner concepts through advanced patterns.
 *
 * JavaScript calls its primary ordered collection an Array rather than
 * a Python-style list. JavaScript Arrays nevertheless support zero-based
 * indexing and several slicing mechanisms that make them useful for studying
 * the same conceptual ideas.
 *
 * Run with:
 *     node list_indexing_slicing.js
 *
 * Browser-specific APIs are intentionally avoided so the file remains
 * executable in Node.js.
 */

"use strict";

// ---------------------------------------------------------------------------
// SECTION 1: BASIC ARRAYS
// ---------------------------------------------------------------------------

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function show(label, value) {
    console.log(`${label}:`, value);
}

section("1. Creating Arrays");

const numbers = [10, 20, 30, 40, 50];
const names = ["Asha", "Ravi", "Meera", "Kiran"];
const mixed = [42, "JavaScript", 3.14, true, null];

show("numbers", numbers);
show("names", names);
show("mixed", mixed);
console.log("Length:", numbers.length);


// ---------------------------------------------------------------------------
// SECTION 2: POSITIVE INDEXING
// ---------------------------------------------------------------------------

section("2. Zero-Based Indexing");

for (let index = 0; index < numbers.length; index += 1) {
    console.log(`index ${index} -> value ${numbers[index]}`);
}

console.log("First:", numbers[0]);
console.log("Second:", numbers[1]);
console.log("Last:", numbers[numbers.length - 1]);


// ---------------------------------------------------------------------------
// SECTION 3: NEGATIVE INDEXING
// ---------------------------------------------------------------------------

section("3. Negative Indexing with at()");

console.log("Last using at(-1):", numbers.at(-1));
console.log("Second-last using at(-2):", numbers.at(-2));
console.log("First using at(-5):", numbers.at(-5));

/*
 * Traditional JavaScript bracket notation does not interpret numbers[-1]
 * as "last element". It creates or accesses a property named "-1".
 *
 * Modern JavaScript provides Array.prototype.at() for negative indexing.
 */
console.log("numbers[-1]:", numbers[-1]);


// ---------------------------------------------------------------------------
// SECTION 4: OUT-OF-RANGE INDEXING
// ---------------------------------------------------------------------------

section("4. Invalid Index Behavior");

console.log("numbers[100]:", numbers[100]);
console.log("numbers.at(100):", numbers.at(100));

/*
 * Unlike Python list indexing, JavaScript array indexing outside the
 * available range returns undefined instead of throwing IndexError.
 */


// ---------------------------------------------------------------------------
// SECTION 5: UPDATING ELEMENTS
// ---------------------------------------------------------------------------

section("5. Updating Elements");

const scores = [70, 82, 91, 64, 88];

console.log("Before:", scores);

scores[0] = 75;
scores[scores.length - 1] = 95;

console.log("After:", scores);


// ---------------------------------------------------------------------------
// SECTION 6: INSERTING AND DELETING
// ---------------------------------------------------------------------------

section("6. Array Structural Operations");

const items = ["A", "B", "D", "E"];

items.splice(2, 0, "C");
console.log("After insertion:", items);

items.splice(1, 1);
console.log("After deleting index 1:", items);

const removed = items.splice(1, 1)[0];
console.log("Removed value:", removed);
console.log("Current array:", items);


// ---------------------------------------------------------------------------
// SECTION 7: BASIC SLICE
// ---------------------------------------------------------------------------

section("7. Basic Array Slicing");

const sequence = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

console.log("sequence:", sequence);
console.log("slice(2, 6):", sequence.slice(2, 6));
console.log("slice(0, 4):", sequence.slice(0, 4));
console.log("slice(5, 9):", sequence.slice(5, 9));

/*
 * Array.prototype.slice(start, end):
 * - start is included.
 * - end is excluded.
 *
 * This mirrors the most important boundary rule of Python slicing.
 */


// ---------------------------------------------------------------------------
// SECTION 8: OMITTED BOUNDARIES
// ---------------------------------------------------------------------------

section("8. Omitted Slice Boundaries");

console.log("slice(0, 5):", sequence.slice(0, 5));
console.log("slice(5):", sequence.slice(5));
console.log("slice():", sequence.slice());


// ---------------------------------------------------------------------------
// SECTION 9: NEGATIVE SLICE BOUNDARIES
// ---------------------------------------------------------------------------

section("9. Negative Slice Boundaries");

console.log("slice(-5):", sequence.slice(-5));
console.log("slice(0, -2):", sequence.slice(0, -2));
console.log("slice(-7, -2):", sequence.slice(-7, -2));
console.log("slice(-4, -1):", sequence.slice(-4, -1));


// ---------------------------------------------------------------------------
// SECTION 10: SLICE CREATES A SHALLOW COPY
// ---------------------------------------------------------------------------

section("10. slice() as a Shallow Copy");

const original = [1, 2, 3, 4, 5];
const copied = original.slice();

copied[0] = 999;

console.log("Original:", original);
console.log("Copied:", copied);
console.log("Different arrays:", original !== copied);


// ---------------------------------------------------------------------------
// SECTION 11: ALIASING
// ---------------------------------------------------------------------------

section("11. Aliasing");

const source = [10, 20, 30];
const alias = source;

alias[0] = 999;

console.log("Source:", source);
console.log("Alias:", alias);
console.log("Same array:", source === alias);


// ---------------------------------------------------------------------------
// SECTION 12: SHALLOW COPY WITH NESTED ARRAYS
// ---------------------------------------------------------------------------

section("12. Shallow Copy of Nested Arrays");

const nested = [
    [1, 2],
    [3, 4],
];

const shallowCopy = nested.slice();

shallowCopy[0][0] = 999;

console.log("Nested original:", nested);
console.log("Shallow copy:", shallowCopy);
console.log("Outer arrays differ:", nested !== shallowCopy);
console.log("Nested arrays shared:", nested[0] === shallowCopy[0]);


// ---------------------------------------------------------------------------
// SECTION 13: DEEP COPY
// ---------------------------------------------------------------------------

section("13. Deep Copy");

const nestedOriginal = [
    { id: 1, values: [10, 20] },
    { id: 2, values: [30, 40] },
];

const deepCopy = structuredClone(nestedOriginal);

deepCopy[0].values[0] = 999;

console.log("Original:", nestedOriginal);
console.log("Deep copy:", deepCopy);


// ---------------------------------------------------------------------------
// SECTION 14: ARRAY DESTRUCTURING
// ---------------------------------------------------------------------------

section("14. Destructuring");

const letters = ["A", "B", "C", "D", "E"];

const [first, second, ...remaining] = letters;

console.log("First:", first);
console.log("Second:", second);
console.log("Remaining:", remaining);


// ---------------------------------------------------------------------------
// SECTION 15: REST DESTRUCTURING AND SLICE
// ---------------------------------------------------------------------------

section("15. Destructuring Versus slice");

const data = [10, 20, 30, 40, 50];

const [head, ...tail] = data;

console.log("Head:", head);
console.log("Tail:", tail);
console.log("slice(1):", data.slice(1));


// ---------------------------------------------------------------------------
// SECTION 16: EVERY-OTHER ELEMENT
// ---------------------------------------------------------------------------

section("16. Stride Selection");

const values = Array.from({ length: 20 }, (_, index) => index);

const everySecond = values.filter((_, index) => index % 2 === 0);
const everyThird = values.filter((_, index) => index % 3 === 0);

console.log("Every second:", everySecond);
console.log("Every third:", everyThird);

/*
 * JavaScript Array.prototype.slice() does not support a third step
 * parameter like Python. Filtering by index is one way to express
 * stride-based selection.
 */


// ---------------------------------------------------------------------------
// SECTION 17: REVERSE SLICING
// ---------------------------------------------------------------------------

section("17. Reversing Arrays");

const forward = [0, 1, 2, 3, 4, 5];

const reversed = forward.slice().reverse();

console.log("Original:", forward);
console.log("Reversed copy:", reversed);

const inPlace = forward.slice();
inPlace.reverse();

console.log("In-place reverse copy:", inPlace);


// ---------------------------------------------------------------------------
// SECTION 18: MANUAL PYTHON-LIKE SLICE WITH STEP
// ---------------------------------------------------------------------------

section("18. Implementing Step-Based Slicing");

function normalizeIndex(index, length) {
    if (!Number.isInteger(index)) {
        throw new TypeError("Index must be an integer.");
    }

    if (index < 0) {
        return Math.max(length + index, 0);
    }

    return Math.min(index, length);
}

function pythonLikeSlice(array, start = null, stop = null, step = 1) {
    if (!Number.isInteger(step)) {
        throw new TypeError("Step must be an integer.");
    }

    if (step === 0) {
        throw new RangeError("Step cannot be zero.");
    }

    const length = array.length;

    if (step > 0) {
        let actualStart = start === null ? 0 : normalizeIndex(start, length);
        let actualStop = stop === null ? length : normalizeIndex(stop, length);

        const result = [];

        for (
            let index = actualStart;
            index < actualStop;
            index += step
        ) {
            result.push(array[index]);
        }

        return result;
    }

    let actualStart;
    let actualStop;

    if (start === null) {
        actualStart = length - 1;
    } else {
        actualStart = start < 0
            ? length + start
            : Math.min(start, length - 1);
    }

    if (stop === null) {
        actualStop = -1;
    } else {
        actualStop = stop < 0
            ? length + stop
            : stop;
    }

    const result = [];

    for (
        let index = actualStart;
        index > actualStop;
        index += step
    ) {
        if (index >= 0 && index < length) {
            result.push(array[index]);
        }
    }

    return result;
}

const alphabet = [..."ABCDEFGHIJ"];

console.log("Forward:", pythonLikeSlice(alphabet, 2, 7, 1));
console.log("Every second:", pythonLikeSlice(alphabet, 0, null, 2));
console.log("Reverse:", pythonLikeSlice(alphabet, null, null, -1));
console.log("Reverse section:", pythonLikeSlice(alphabet, 8, 2, -1));


// ---------------------------------------------------------------------------
// SECTION 19: SAFE INDEX ACCESS
// ---------------------------------------------------------------------------

section("19. Safe Index Access");

function safeGet(array, index, defaultValue = null) {
    if (!Number.isInteger(index)) {
        return defaultValue;
    }

    const value = array.at(index);
    return value === undefined ? defaultValue : value;
}

const colors = ["red", "green", "blue"];

console.log("Index 1:", safeGet(colors, 1));
console.log("Index -1:", safeGet(colors, -1));
console.log("Index 100:", safeGet(colors, 100, "missing"));
console.log("Invalid type:", safeGet(colors, "1", "invalid"));


// ---------------------------------------------------------------------------
// SECTION 20: NESTED ARRAY INDEXING
// ---------------------------------------------------------------------------

section("20. Nested Arrays");

const matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
];

console.log("First row:", matrix[0]);
console.log("Center:", matrix[1][1]);
console.log("Bottom-right:", matrix.at(-1).at(-1));

matrix[1][1] = 50;

console.log("Modified matrix:", matrix);


// ---------------------------------------------------------------------------
// SECTION 21: NESTED ARRAY SLICING
// ---------------------------------------------------------------------------

section("21. Nested Array Slicing");

const table = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
];

console.log("First two rows:", table.slice(0, 2));
console.log("Last two rows:", table.slice(-2));
console.log(
    "Columns 2 and 3:",
    table.map(row => row.slice(1, 3))
);


// ---------------------------------------------------------------------------
// SECTION 22: FILTERING A SLICE
// ---------------------------------------------------------------------------

section("22. Filtering a Selected Region");

const scoresArray = [45, 72, 81, 39, 90, 66, 54, 88];

const selectedRegion = scoresArray.slice(2, 7);
const passing = selectedRegion.filter(score => score >= 60);

console.log("Selected:", selectedRegion);
console.log("Passing:", passing);


// ---------------------------------------------------------------------------
// SECTION 23: MAP OVER A SLICE
// ---------------------------------------------------------------------------

section("23. Transforming a Selected Region");

const prices = [100, 200, 300, 400, 500];

const transformed = prices
    .slice(1, 4)
    .map(price => price * 1.18);

console.log("Original prices:", prices);
console.log("Selected prices:", prices.slice(1, 4));
console.log("With tax:", transformed);


// ---------------------------------------------------------------------------
// SECTION 24: SORTING A SLICE WITHOUT MUTATING ORIGINAL
// ---------------------------------------------------------------------------

section("24. Sorting a Selected Region");

const scoresForSorting = [72, 91, 88, 64, 97, 83, 79];

const sortedRegion = scoresForSorting
    .slice(1, 6)
    .sort((a, b) => b - a);

console.log("Original:", scoresForSorting);
console.log("Sorted selected region:", sortedRegion);


// ---------------------------------------------------------------------------
// SECTION 25: TOP-N
// ---------------------------------------------------------------------------

section("25. Top-N Selection");

const playerScores = [
    ["A", 91],
    ["B", 87],
    ["C", 99],
    ["D", 94],
    ["E", 88],
];

const topThree = playerScores
    .slice()
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3);

console.log("Top three:", topThree);


// ---------------------------------------------------------------------------
// SECTION 26: PAGINATION
// ---------------------------------------------------------------------------

section("26. Pagination");

const records = Array.from(
    { length: 25 },
    (_, index) => `record-${String(index + 1).padStart(2, "0")}`
);

function getPage(array, pageNumber, pageSize) {
    if (!Number.isInteger(pageNumber) || pageNumber < 1) {
        throw new RangeError("pageNumber must be a positive integer.");
    }

    if (!Number.isInteger(pageSize) || pageSize <= 0) {
        throw new RangeError("pageSize must be a positive integer.");
    }

    const start = (pageNumber - 1) * pageSize;
    return array.slice(start, start + pageSize);
}

for (let page = 1; page <= 6; page += 1) {
    console.log(`Page ${page}:`, getPage(records, page, 5));
}


// ---------------------------------------------------------------------------
// SECTION 27: CHUNKING
// ---------------------------------------------------------------------------

section("27. Chunking");

function chunk(array, size) {
    if (!Number.isInteger(size) || size <= 0) {
        throw new RangeError("Chunk size must be positive.");
    }

    const result = [];

    for (let start = 0; start < array.length; start += size) {
        result.push(array.slice(start, start + size));
    }

    return result;
}

console.log("Chunks:", chunk([1, 2, 3, 4, 5, 6, 7], 3));


// ---------------------------------------------------------------------------
// SECTION 28: SLIDING WINDOWS
// ---------------------------------------------------------------------------

section("28. Sliding Windows");

function slidingWindows(array, width) {
    if (!Number.isInteger(width) || width <= 0) {
        throw new RangeError("Width must be positive.");
    }

    if (width > array.length) {
        return [];
    }

    const result = [];

    for (let start = 0; start <= array.length - width; start += 1) {
        result.push(array.slice(start, start + width));
    }

    return result;
}

console.log(
    "Width-3 windows:",
    slidingWindows([10, 20, 30, 40, 50], 3)
);


// ---------------------------------------------------------------------------
// SECTION 29: ARRAY WITH HOLES
// ---------------------------------------------------------------------------

section("29. Sparse Arrays");

const sparse = [];
sparse[0] = "A";
sparse[3] = "D";

console.log("Sparse array:", sparse);
console.log("Length:", sparse.length);
console.log("Index 1:", sparse[1]);
console.log("Has own index 1:", Object.hasOwn(sparse, 1));

/*
 * A sparse array can contain missing positions. A missing position is
 * different from a position explicitly containing undefined.
 */


// ---------------------------------------------------------------------------
// SECTION 30: SLICE OF A SPARSE ARRAY
// ---------------------------------------------------------------------------

section("30. Slicing Sparse Arrays");

const sparseSlice = sparse.slice(0, 4);

console.log("Original sparse array:", sparse);
console.log("Sparse slice:", sparseSlice);
console.log("Has own index 1 in slice:", Object.hasOwn(sparseSlice, 1));


// ---------------------------------------------------------------------------
// SECTION 31: ARRAY-LIKE OBJECTS
// ---------------------------------------------------------------------------

section("31. Array-Like Objects");

const arrayLike = {
    0: "A",
    1: "B",
    2: "C",
    length: 3,
};

const converted = Array.from(arrayLike);

console.log("Array-like object:", arrayLike);
console.log("Converted array:", converted);
console.log("Slice after conversion:", converted.slice(1));


// ---------------------------------------------------------------------------
// SECTION 32: TYPED ARRAYS
// ---------------------------------------------------------------------------

section("32. Typed Array Slicing");

const typed = new Int32Array([10, 20, 30, 40, 50]);

console.log("Typed array:", typed);
console.log("Index 2:", typed[2]);
console.log("at(-1):", typed.at(-1));
console.log("slice(1, 4):", typed.slice(1, 4));

/*
 * Typed arrays are array-like but store fixed-width numeric values.
 * They provide specialized memory representation and APIs.
 */


// ---------------------------------------------------------------------------
// SECTION 33: SUBARRAY VERSUS SLICE
// ---------------------------------------------------------------------------

section("33. TypedArray slice() Versus subarray()");

const typedOriginal = new Int32Array([1, 2, 3, 4, 5]);

const copiedTyped = typedOriginal.slice(1, 4);
const sharedTyped = typedOriginal.subarray(1, 4);

sharedTyped[0] = 999;

console.log("Original after subarray mutation:", typedOriginal);
console.log("slice copy:", copiedTyped);
console.log("subarray view:", sharedTyped);

/*
 * TypedArray.slice() creates a copy.
 * TypedArray.subarray() creates a view over the same underlying memory.
 */


// ---------------------------------------------------------------------------
// SECTION 34: COPY METHODS
// ---------------------------------------------------------------------------

section("34. Common Array Copy Methods");

const base = [1, 2, 3, 4];

const copy1 = base.slice();
const copy2 = [...base];
const copy3 = Array.from(base);

console.log(copy1);
console.log(copy2);
console.log(copy3);
console.log(
    "All are separate arrays:",
    base !== copy1 && base !== copy2 && base !== copy3
);


// ---------------------------------------------------------------------------
// SECTION 35: CONCATENATING SLICES
// ---------------------------------------------------------------------------

section("35. Combining Slices");

const lettersForRotation = ["A", "B", "C", "D", "E"];

const rotatedLeft = lettersForRotation
    .slice(2)
    .concat(lettersForRotation.slice(0, 2));

console.log("Left rotation by two:", rotatedLeft);


// ---------------------------------------------------------------------------
// SECTION 36: ROTATION FUNCTIONS
// ---------------------------------------------------------------------------

section("36. Rotation Functions");

function normalizeRotation(positions, length) {
    if (length === 0) {
        return 0;
    }

    return ((positions % length) + length) % length;
}

function rotateLeft(array, positions) {
    if (array.length === 0) {
        return [];
    }

    const amount = normalizeRotation(positions, array.length);

    return array.slice(amount).concat(array.slice(0, amount));
}

function rotateRight(array, positions) {
    if (array.length === 0) {
        return [];
    }

    const amount = normalizeRotation(positions, array.length);

    if (amount === 0) {
        return array.slice();
    }

    return array.slice(-amount).concat(array.slice(0, -amount));
}

const rotationValues = [1, 2, 3, 4, 5];

console.log("Left 2:", rotateLeft(rotationValues, 2));
console.log("Right 2:", rotateRight(rotationValues, 2));
console.log("Left -1:", rotateLeft(rotationValues, -1));
console.log("Right -1:", rotateRight(rotationValues, -1));


// ---------------------------------------------------------------------------
// SECTION 37: REMOVE RANGE WITH SPLICE
// ---------------------------------------------------------------------------

section("37. Deleting a Range");

const removable = ["A", "B", "C", "D", "E", "F"];

removable.splice(2, 2);

console.log("After deleting C and D:", removable);


// ---------------------------------------------------------------------------
// SECTION 38: REPLACE RANGE WITH SPLICE
// ---------------------------------------------------------------------------

section("38. Replacing a Range");

const replaceable = ["A", "B", "C", "D", "E"];

replaceable.splice(1, 3, "X", "Y");

console.log("After replacement:", replaceable);


// ---------------------------------------------------------------------------
// SECTION 39: INSERT RANGE WITH SPLICE
// ---------------------------------------------------------------------------

section("39. Inserting a Range");

const insertable = ["A", "D"];

insertable.splice(1, 0, "B", "C");

console.log("After insertion:", insertable);


// ---------------------------------------------------------------------------
// SECTION 40: INDEX OF VALUE
// ---------------------------------------------------------------------------

section("40. Position Versus Value");

const duplicateValues = ["A", "B", "A", "C", "A"];

console.log("First A:", duplicateValues.indexOf("A"));
console.log("Last A:", duplicateValues.lastIndexOf("A"));
console.log("Selected positions:", duplicateValues.slice(0, 3));


// ---------------------------------------------------------------------------
// SECTION 41: FINDING WITH PREDICATES
// ---------------------------------------------------------------------------

section("41. Conditional Selection");

const measurements = [10, 35, 20, 70, 45, 90];

console.log(
    "Values >= 50:",
    measurements.filter(value => value >= 50)
);

console.log(
    "First value >= 50:",
    measurements.find(value => value >= 50)
);


// ---------------------------------------------------------------------------
// SECTION 42: INDEXED FILTERING
// ---------------------------------------------------------------------------

section("42. Selecting Positions by Rule");

const indexedValues = Array.from({ length: 12 }, (_, index) => index + 1);

const evenPositions = indexedValues.filter(
    (_, index) => index % 2 === 0
);

console.log("Original:", indexedValues);
console.log("Even positions:", evenPositions);


// ---------------------------------------------------------------------------
// SECTION 43: WINDOWED AVERAGE
// ---------------------------------------------------------------------------

section("43. Windowed Average");

function average(array) {
    if (array.length === 0) {
        return null;
    }

    return array.reduce((sum, value) => sum + value, 0) / array.length;
}

const sales = [120, 135, 128, 142, 155, 161, 149, 170];

const recentSales = sales.slice(-5);

console.log("Recent sales:", recentSales);
console.log("Average:", average(recentSales));


// ---------------------------------------------------------------------------
// SECTION 44: LOG PROCESSING
// ---------------------------------------------------------------------------

section("44. Log Processing");

const logs = [
    "INFO startup",
    "INFO database connected",
    "WARNING cache miss",
    "ERROR authentication failed",
    "ERROR database timeout",
    "INFO retry started",
    "INFO recovery complete",
];

const recentLogs = logs.slice(-4);
const errors = recentLogs.filter(entry => entry.startsWith("ERROR"));

console.log("Recent:", recentLogs);
console.log("Errors:", errors);


// ---------------------------------------------------------------------------
// SECTION 45: TABLE PROCESSING
// ---------------------------------------------------------------------------

section("45. Table Processing");

const employeeTable = [
    ["ID", "Name", "Score", "Status"],
    [1, "Asha", 91, "Pass"],
    [2, "Ravi", 84, "Pass"],
    [3, "Meera", 52, "Fail"],
    [4, "Kiran", 96, "Pass"],
];

const header = employeeTable[0];
const dataRows = employeeTable.slice(1);

console.log("Header:", header);
console.log("First two rows:", dataRows.slice(0, 2));
console.log("Names:", dataRows.map(row => row[1]));
console.log("Scores:", dataRows.map(row => row[2]));


// ---------------------------------------------------------------------------
// SECTION 46: FIXED-WIDTH TEXT
// ---------------------------------------------------------------------------

section("46. Fixed-Width Text");

const rawRecord = "INDIA     2026   ACTIVE  ";

const country = rawRecord.slice(0, 10).trim();
const year = rawRecord.slice(10, 18).trim();
const status = rawRecord.slice(18).trim();

console.log("Country:", country);
console.log("Year:", year);
console.log("Status:", status);


// ---------------------------------------------------------------------------
// SECTION 47: SAFE PAGINATION EDGE CASES
// ---------------------------------------------------------------------------

section("47. Pagination Edge Cases");

console.log("Past final page:", getPage(records, 100, 5));

try {
    getPage(records, 0, 5);
} catch (error) {
    console.log("Invalid page:", error.message);
}

try {
    getPage(records, 1, 0);
} catch (error) {
    console.log("Invalid page size:", error.message);
}


// ---------------------------------------------------------------------------
// SECTION 48: IMMUTABILITY PATTERN
// ---------------------------------------------------------------------------

section("48. Non-Mutating Array Operations");

const immutableSource = [5, 4, 3, 2, 1];

const sortedCopy = immutableSource.slice().sort((a, b) => a - b);
const reversedCopy = immutableSource.slice().reverse();
const middleCopy = immutableSource.slice(1, 4);

console.log("Source:", immutableSource);
console.log("Sorted copy:", sortedCopy);
console.log("Reversed copy:", reversedCopy);
console.log("Middle copy:", middleCopy);


// ---------------------------------------------------------------------------
// SECTION 49: COMMON MISTAKE: SLICE END IS EXCLUSIVE
// ---------------------------------------------------------------------------

section("49. Exclusive End Boundary");

const boundary = ["A", "B", "C", "D", "E"];

console.log("slice(1, 4):", boundary.slice(1, 4));
console.log("Indexes selected:", [1, 2, 3]);


// ---------------------------------------------------------------------------
// SECTION 50: COMMON MISTAKE: SLICE DOES NOT MUTATE
// ---------------------------------------------------------------------------

section("50. slice() Does Not Mutate");

const nonMutating = [1, 2, 3, 4, 5];

const selected = nonMutating.slice(1, 4);

console.log("Selected:", selected);
console.log("Original:", nonMutating);


// ---------------------------------------------------------------------------
// SECTION 51: COMMON MISTAKE: splice() DOES MUTATE
// ---------------------------------------------------------------------------

section("51. splice() Mutates");

const mutating = [1, 2, 3, 4, 5];

const deleted = mutating.splice(1, 2);

console.log("Deleted:", deleted);
console.log("Mutated array:", mutating);


// ---------------------------------------------------------------------------
// SECTION 52: OPTIONAL CHAINING WITH at()
// ---------------------------------------------------------------------------

section("52. Optional Chaining and Nested Access");

const departments = [
    ["employee-001", "employee-002"],
    ["employee-003"],
];

console.log("First employee:", departments.at(0)?.at(0));
console.log("Missing department:", departments.at(10)?.at(0));


// ---------------------------------------------------------------------------
// SECTION 53: ARRAYS AS STACKS
// ---------------------------------------------------------------------------

section("53. Stack Operations");

const stack = [];

stack.push("A");
stack.push("B");
stack.push("C");

console.log("Stack:", stack);
console.log("Top:", stack.at(-1));

console.log("Pop:", stack.pop());
console.log("Remaining:", stack);


// ---------------------------------------------------------------------------
// SECTION 54: ARRAYS AS QUEUES
// ---------------------------------------------------------------------------

section("54. Queue-Like Operations");

const queue = ["A", "B", "C"];

console.log("First item:", queue[0]);
console.log("Shift:", queue.shift());
console.log("Remaining:", queue);

queue.push("D");

console.log("After enqueue:", queue);


// ---------------------------------------------------------------------------
// SECTION 55: PERFORMANCE OF FRONT REMOVAL
// ---------------------------------------------------------------------------

section("55. Array Performance Considerations");

/*
 * Access by numeric index is generally O(1).
 *
 * slice() is generally O(k), where k is the number of copied elements.
 *
 * splice() may require shifting many elements and can therefore be O(n).
 *
 * shift() and unshift() can also require moving many elements.
 *
 * For large queues, repeated shift() operations may be less appropriate
 * than maintaining a separate head index or using a specialized data
 * structure.
 */

const largeArray = Array.from({ length: 100_000 }, (_, index) => index);

console.time("10000 indexed reads");

let checksum = 0;

for (let index = 0; index < 10_000; index += 1) {
    checksum += largeArray[index];
}

console.timeEnd("10000 indexed reads");

console.log("Checksum:", checksum);


// ---------------------------------------------------------------------------
// SECTION 56: SLICE PERFORMANCE
// ---------------------------------------------------------------------------

section("56. Slice Performance Measurement");

console.time("100 slices");

let total = 0;

for (let iteration = 0; iteration < 100; iteration += 1) {
    total += largeArray.slice(10_000, 90_000).length;
}

console.timeEnd("100 slices");
console.log("Total copied lengths:", total);


// ---------------------------------------------------------------------------
// SECTION 57: GENERIC RANGE FUNCTION
// ---------------------------------------------------------------------------

section("57. Range-Like Utility");

function range(start, stop, step = 1) {
    if (!Number.isInteger(start) ||
        !Number.isInteger(stop) ||
        !Number.isInteger(step)) {
        throw new TypeError("Range parameters must be integers.");
    }

    if (step === 0) {
        throw new RangeError("Step cannot be zero.");
    }

    const result = [];

    if (step > 0) {
        for (let value = start; value < stop; value += step) {
            result.push(value);
        }
    } else {
        for (let value = start; value > stop; value += step) {
            result.push(value);
        }
    }

    return result;
}

console.log("range(0, 10, 2):", range(0, 10, 2));
console.log("range(10, 0, -2):", range(10, 0, -2));


// ---------------------------------------------------------------------------
// SECTION 58: RANGE COMBINED WITH SLICING
// ---------------------------------------------------------------------------

section("58. Generated Data and Selection");

const generated = range(0, 30, 1);

console.log("First ten:", generated.slice(0, 10));
console.log("Last five:", generated.slice(-5));


// ---------------------------------------------------------------------------
// SECTION 59: DATA WINDOW API
// ---------------------------------------------------------------------------

section("59. Offset and Limit API");

function window(array, offset = 0, limit = 10) {
    if (!Number.isInteger(offset) || offset < 0) {
        throw new RangeError("Offset must be a non-negative integer.");
    }

    if (!Number.isInteger(limit) || limit < 0) {
        throw new RangeError("Limit must be a non-negative integer.");
    }

    return array.slice(offset, offset + limit);
}

console.log("Window:", window(generated, 5, 10));
console.log("Empty window:", window(generated, 5, 0));
console.log("Past end:", window(generated, 100, 10));


// ---------------------------------------------------------------------------
// SECTION 60: FEATURE EXTRACTION
// ---------------------------------------------------------------------------

section("60. Feature Extraction");

const featureRows = [
    ["A001", 0.81, 0.42, "positive"],
    ["A002", 0.74, 0.55, "positive"],
    ["A003", 0.31, 0.27, "negative"],
];

const identifiers = featureRows.map(row => row[0]);
const numericFeatures = featureRows.map(row => row.slice(1, 3));

console.log("Identifiers:", identifiers);
console.log("Numeric features:", numericFeatures);


// ---------------------------------------------------------------------------
// SECTION 61: GROUPED RECORDS
// ---------------------------------------------------------------------------

section("61. Grouped Data");

const organization = [
    [
        ["employee-001", "Engineering"],
        ["employee-002", "Security"],
    ],
    [
        ["employee-003", "Finance"],
        ["employee-004", "Operations"],
    ],
];

console.log("First department:", organization[0]);
console.log("Second employee in first department:", organization[0][1]);
console.log("Role:", organization[0][1][1]);


// ---------------------------------------------------------------------------
// SECTION 62: COPY NESTED DATA SAFELY
// ---------------------------------------------------------------------------

section("62. Nested Data Copying");

const nestedData = [
    { id: 1, tags: ["python", "data"] },
    { id: 2, tags: ["javascript", "web"] },
];

const shallowNested = nestedData.slice();
const deepNested = structuredClone(nestedData);

shallowNested[0].tags.push("shared");

console.log("Original after shallow mutation:", nestedData);
console.log("Deep copy:", deepNested);


// ---------------------------------------------------------------------------
// SECTION 63: CONDITIONAL SLICING
// ---------------------------------------------------------------------------

section("63. Conditional Data Followed by Slicing");

const transactionValues = [100, 500, 250, 900, 300, 1200, 450];

const highValues = transactionValues
    .filter(value => value >= 500)
    .slice(0, 3);

console.log("First three high-value transactions:", highValues);


// ---------------------------------------------------------------------------
// SECTION 64: SLICE FOLLOWED BY REDUCTION
// ---------------------------------------------------------------------------

section("64. Aggregating a Slice");

const dailySales = [120, 135, 128, 142, 155, 161, 149, 170];

const recent = dailySales.slice(-5);

const recentTotal = recent.reduce(
    (sum, value) => sum + value,
    0
);

console.log("Recent:", recent);
console.log("Total:", recentTotal);
console.log("Average:", recentTotal / recent.length);


// ---------------------------------------------------------------------------
// SECTION 65: FIXED-WIDTH BATCH PROCESSING
// ---------------------------------------------------------------------------

section("65. Batch Processing");

const jobs = Array.from(
    { length: 11 },
    (_, index) => `JOB-${String(index + 1).padStart(3, "0")}`
);

for (let start = 0; start < jobs.length; start += 4) {
    const batch = jobs.slice(start, start + 4);
    console.log("Processing batch:", batch);
}


// ---------------------------------------------------------------------------
// SECTION 66: SLIDING ANALYSIS
// ---------------------------------------------------------------------------

section("66. Moving Average");

const sensorValues = [10, 12, 11, 15, 18, 17, 20];

const windows = slidingWindows(sensorValues, 3);

const movingAverages = windows.map(average);

console.log("Windows:", windows);
console.log("Moving averages:", movingAverages);


// ---------------------------------------------------------------------------
// SECTION 67: ERROR HANDLING
// ---------------------------------------------------------------------------

section("67. Error Handling");

try {
    pythonLikeSlice([1, 2, 3], 0, 2, 0);
} catch (error) {
    console.log("Caught invalid step:", error.message);
}

try {
    chunk([1, 2, 3], 0);
} catch (error) {
    console.log("Caught invalid chunk size:", error.message);
}


// ---------------------------------------------------------------------------
// SECTION 68: CUSTOM ARRAY-LIKE CLASS
// ---------------------------------------------------------------------------

section("68. Custom Collection");

class IndexedCollection {
    constructor(values) {
        this.values = Array.from(values);
    }

    get(index) {
        return this.values.at(index);
    }

    slice(start, end) {
        return new IndexedCollection(this.values.slice(start, end));
    }

    toArray() {
        return this.values.slice();
    }

    get length() {
        return this.values.length;
    }
    
    toString() {
        return `IndexedCollection(${JSON.stringify(this.values)})`;
    }
}

const collection = new IndexedCollection([10, 20, 30, 40, 50]);

console.log("Collection:", collection.toString());
console.log("Index 2:", collection.get(2));
console.log("Last:", collection.get(-1));
console.log("Slice:", collection.slice(1, 4).toArray());


// ---------------------------------------------------------------------------
// SECTION 69: ITERATORS AND ARRAY FROM
// ---------------------------------------------------------------------------

section("69. Iterators");

const iterator = [10, 20, 30][Symbol.iterator]();

console.log(iterator.next());
console.log(iterator.next());
console.log(iterator.next());
console.log(iterator.next());

const iteratorArray = Array.from(
    new Set(["A", "B", "C", "A"])
);

console.log("Array from Set:", iteratorArray);


// ---------------------------------------------------------------------------
// SECTION 70: READ-ONLY VIEW PATTERN
// ---------------------------------------------------------------------------

section("70. Freezing an Array");

const frozen = Object.freeze([1, 2, 3]);

console.log("Frozen array:", frozen);

try {
    frozen[0] = 999;
} catch (error) {
    console.log("Frozen mutation error:", error.message);
}

console.log("After attempted mutation:", frozen);

/*
 * In strict mode, assigning to a frozen property throws.
 * Object.freeze is shallow. Nested objects require separate handling.
 */


// ---------------------------------------------------------------------------
// SECTION 71: DEEP FREEZE EXAMPLE
// ---------------------------------------------------------------------------

section("71. Deep Freeze");

function deepFreeze(value) {
    if (
        value !== null &&
        typeof value === "object" &&
        !Object.isFrozen(value)
    ) {
        Object.freeze(value);

        for (const child of Object.values(value)) {
            deepFreeze(child);
        }
    }

    return value;
}

const protectedData = deepFreeze([
    { name: "A", values: [1, 2] },
    { name: "B", values: [3, 4] },
]);

try {
    protectedData[0].values[0] = 999;
} catch (error) {
    console.log("Deep freeze mutation error:", error.message);
}

console.log("Protected data:", protectedData);


// ---------------------------------------------------------------------------
// SECTION 72: COMPARING SLICE AND SUBARRAY
// ---------------------------------------------------------------------------

section("72. Typed Array Memory Views");

const buffer = new ArrayBuffer(16);
const view = new Int32Array(buffer);

view.set([10, 20, 30, 40]);

const copiedView = view.slice(1, 3);
const memoryView = view.subarray(1, 3);

memoryView[0] = 999;

console.log("Original typed array:", view);
console.log("Copied slice:", copiedView);
console.log("Shared subarray:", memoryView);


// ---------------------------------------------------------------------------
// SECTION 73: INTEGRATED SALES CASE STUDY
// ---------------------------------------------------------------------------

section("73. Integrated Sales Case Study");

const salesRecords = [
    { id: "S001", amount: 1200, region: "North" },
    { id: "S002", amount: 850, region: "South" },
    { id: "S003", amount: 2100, region: "North" },
    { id: "S004", amount: 1750, region: "West" },
    { id: "S005", amount: 950, region: "East" },
    { id: "S006", amount: 3200, region: "North" },
    { id: "S007", amount: 1100, region: "South" },
    { id: "S008", amount: 2800, region: "West" },
    { id: "S009", amount: 1600, region: "East" },
    { id: "S010", amount: 4000, region: "North" },
];

const latestFive = salesRecords.slice(-5);

const highestThree = salesRecords
    .slice()
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 3);

const sampledRecords = salesRecords.filter(
    (_, index) => index % 2 === 0
);

console.log("Latest five:", latestFive);
console.log("Highest three:", highestThree);
console.log("Sampled records:", sampledRecords);


// ---------------------------------------------------------------------------
// SECTION 74: ASSERTION-BASED TESTING
// ---------------------------------------------------------------------------

section("74. Automated Tests");

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

const testValues = [0, 1, 2, 3, 4];

assert(testValues[0] === 0, "first element");
assert(testValues.at(-1) === 4, "last element");
assert(
    JSON.stringify(testValues.slice(1, 4)) === JSON.stringify([1, 2, 3]),
    "middle slice"
);
assert(
    JSON.stringify(testValues.slice(-2)) === JSON.stringify([3, 4]),
    "last two"
);
assert(
    JSON.stringify(testValues.slice().reverse()) ===
    JSON.stringify([4, 3, 2, 1, 0]),
    "reverse copy"
);
assert(
    JSON.stringify(pythonLikeSlice(testValues, 1, 5, 2)) ===
    JSON.stringify([1, 3]),
    "step slicing"
);

console.log("All tests passed.");


// ---------------------------------------------------------------------------
// SECTION 75: FINAL PRINCIPLES
// ---------------------------------------------------------------------------

section("75. Core Principles");

const principles = [
    "JavaScript arrays use zero-based numeric indexing.",
    "array.at(-1) provides convenient negative indexing.",
    "Traditional array[-1] is not negative indexing.",
    "Out-of-range bracket access returns undefined.",
    "slice(start, end) uses an inclusive start and exclusive end.",
    "slice() returns a new shallow array.",
    "slice() does not mutate the source array.",
    "splice() changes the source array.",
    "reverse() changes the array unless used on a copy.",
    "JavaScript slice() does not have Python's built-in step parameter.",
    "Filtering by index can implement stride-like selection.",
    "TypedArray.slice() creates a copy.",
    "TypedArray.subarray() creates a shared-memory view.",
    "Nested array slices are shallow.",
    "Large slices allocate memory proportional to copied elements.",
    "Repeated shift() operations can be costly for large queues.",
    "Array indexing is generally constant-time.",
    "Sorting is separate from slicing and normally mutates its receiver.",
    "Array methods should be selected according to mutation requirements.",
];

principles.forEach((principle, index) => {
    console.log(`${String(index + 1).padStart(2, "0")}. ${principle}`);
});

console.log("\nJavaScript indexing and slicing study program completed.");
