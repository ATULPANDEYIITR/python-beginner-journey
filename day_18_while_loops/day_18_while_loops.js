/*
 * WHILE LOOPS IN JAVASCRIPT
 * =========================
 *
 * A self-contained study file covering while loops from beginner through
 * advanced usage: counters, sentinels, validation, break, continue,
 * do...while, nested loops, iterators, algorithms, state machines,
 * asynchronous loops, retries, queues, edge cases, and performance.
 *
 * Run with:
 *     node while-loops.js
 */

// ---------------------------------------------------------------------------
// 1. BASIC WHILE LOOP
// ---------------------------------------------------------------------------

function basicWhile() {
    console.log("\n1. Basic while loop");

    let number = 1;

    while (number <= 5) {
        console.log(number);
        number++;
    }
}


// ---------------------------------------------------------------------------
// 2. COUNTERS AND CUSTOM STEPS
// ---------------------------------------------------------------------------

function counterExamples() {
    console.log("\n2. Counter examples");

    let increasing = 0;

    while (increasing < 5) {
        process.stdout.write(`${increasing} `);
        increasing++;
    }

    console.log();

    let decreasing = 5;

    while (decreasing > 0) {
        process.stdout.write(`${decreasing} `);
        decreasing--;
    }

    console.log();

    let step = 0;

    while (step <= 20) {
        if (step % 5 === 0) {
            console.log(`Multiple of five: ${step}`);
        }

        step += 2;
    }
}


// ---------------------------------------------------------------------------
// 3. INPUT-LIKE VALIDATION
// ---------------------------------------------------------------------------

function parsePositiveInteger(text) {
    const value = Number(text);

    if (!Number.isInteger(value) || value <= 0) {
        throw new Error("Value must be a positive integer.");
    }

    return value;
}

function validateFromSequence(values) {
    console.log("\n3. Repeated validation");

    let index = 0;

    while (index < values.length) {
        try {
            const value = parsePositiveInteger(values[index]);
            console.log(`Accepted: ${value}`);
            return value;
        } catch (error) {
            console.log(`Rejected ${JSON.stringify(values[index])}: ${error.message}`);
        }

        index++;
    }

    return null;
}


// ---------------------------------------------------------------------------
// 4. SENTINEL LOOP
// ---------------------------------------------------------------------------

function sumUntilSentinel(values, sentinel = -1) {
    let index = 0;
    let total = 0;

    while (index < values.length) {
        const value = values[index];

        if (value === sentinel) {
            break;
        }

        total += value;
        index++;
    }

    return total;
}


// ---------------------------------------------------------------------------
// 5. BREAK
// ---------------------------------------------------------------------------

function findFirst(values, target) {
    let index = 0;

    while (index < values.length) {
        if (values[index] === target) {
            break;
        }

        index++;
    }

    return index < values.length ? index : -1;
}


// ---------------------------------------------------------------------------
// 6. CONTINUE
// ---------------------------------------------------------------------------

function printOddNumbers(limit) {
    console.log("\n4. continue");

    let number = 0;

    while (number < limit) {
        number++;

        if (number % 2 === 0) {
            continue;
        }

        process.stdout.write(`${number} `);
    }

    console.log();
}


// ---------------------------------------------------------------------------
// 7. DO...WHILE
// ---------------------------------------------------------------------------

function doWhileExample() {
    console.log("\n5. do...while");

    /*
     * A normal while loop may execute zero times.
     * A do...while loop always executes its body at least once because the
     * condition is checked after the body.
     */
    let value = 100;

    while (value < 0) {
        console.log("This does not print.");
    }

    let attempts = 0;

    do {
        attempts++;
        console.log(`do...while iteration ${attempts}`);
    } while (attempts < 1);
}


// ---------------------------------------------------------------------------
// 8. NESTED WHILE LOOPS
// ---------------------------------------------------------------------------

function multiplicationTable(size) {
    console.log("\n6. Nested loops");

    let row = 1;

    while (row <= size) {
        let column = 1;
        const values = [];

        while (column <= size) {
            values.push(row * column);
            column++;
        }

        console.log(values.join("\t"));
        row++;
    }
}


// ---------------------------------------------------------------------------
// 9. STRING PROCESSING
// ---------------------------------------------------------------------------

function reverseString(text) {
    let index = text.length - 1;
    let result = "";

    while (index >= 0) {
        result += text[index];
        index--;
    }

    return result;
}

function countCharacters(text, target) {
    let index = 0;
    let count = 0;

    while (index < text.length) {
        if (text[index] === target) {
            count++;
        }

        index++;
    }

    return count;
}


// ---------------------------------------------------------------------------
// 10. ARRAY PROCESSING
// ---------------------------------------------------------------------------

function filterPositive(values) {
    const result = [];
    let index = 0;

    while (index < values.length) {
        if (values[index] > 0) {
            result.push(values[index]);
        }

        index++;
    }

    return result;
}

function calculateStatistics(values) {
    if (values.length === 0) {
        throw new Error("At least one value is required.");
    }

    let index = 0;
    let sum = 0;
    let minimum = values[0];
    let maximum = values[0];

    while (index < values.length) {
        const value = values[index];

        sum += value;

        if (value < minimum) {
            minimum = value;
        }

        if (value > maximum) {
            maximum = value;
        }

        index++;
    }

    return {
        count: values.length,
        sum,
        minimum,
        maximum,
        mean: sum / values.length
    };
}


// ---------------------------------------------------------------------------
// 11. FACTORIAL
// ---------------------------------------------------------------------------

function factorial(number) {
    if (!Number.isInteger(number) || number < 0) {
        throw new Error("Factorial requires a non-negative integer.");
    }

    let result = 1;
    let current = 2;

    while (current <= number) {
        result *= current;
        current++;
    }

    return result;
}


// ---------------------------------------------------------------------------
// 12. EUCLIDEAN ALGORITHM
// ---------------------------------------------------------------------------

function greatestCommonDivisor(a, b) {
    a = Math.abs(a);
    b = Math.abs(b);

    while (b !== 0) {
        [a, b] = [b, a % b];
    }

    return a;
}


// ---------------------------------------------------------------------------
// 13. BINARY SEARCH
// ---------------------------------------------------------------------------

function binarySearch(sortedValues, target) {
    let low = 0;
    let high = sortedValues.length - 1;

    while (low <= high) {
        const middle = low + Math.floor((high - low) / 2);
        const candidate = sortedValues[middle];

        if (candidate === target) {
            return middle;
        }

        if (candidate < target) {
            low = middle + 1;
        } else {
            high = middle - 1;
        }
    }

    return -1;
}


// ---------------------------------------------------------------------------
// 14. PRIME TESTING
// ---------------------------------------------------------------------------

function isPrime(number) {
    if (!Number.isInteger(number) || number < 2) {
        return false;
    }

    if (number === 2) {
        return true;
    }

    if (number % 2 === 0) {
        return false;
    }

    let divisor = 3;

    while (divisor * divisor <= number) {
        if (number % divisor === 0) {
            return false;
        }

        divisor += 2;
    }

    return true;
}


// ---------------------------------------------------------------------------
// 15. FIBONACCI
// ---------------------------------------------------------------------------

function fibonacciTerms(count) {
    if (!Number.isInteger(count) || count < 0) {
        throw new Error("Count must be a non-negative integer.");
    }

    const result = [];
    let first = 0;
    let second = 1;
    let index = 0;

    while (index < count) {
        result.push(first);
        [first, second] = [second, first + second];
        index++;
    }

    return result;
}


// ---------------------------------------------------------------------------
// 16. ITERATORS
// ---------------------------------------------------------------------------

function consumeIterator(iterable) {
    const iterator = iterable[Symbol.iterator]();
    const result = [];
    let nextResult = iterator.next();

    while (!nextResult.done) {
        result.push(nextResult.value);
        nextResult = iterator.next();
    }

    return result;
}


// ---------------------------------------------------------------------------
// 17. STATE MACHINE
// ---------------------------------------------------------------------------

class TrafficLight {
    constructor() {
        this.state = "RED";
        this.cycles = 0;
    }

    advance() {
        const transitions = {
            RED: "GREEN",
            GREEN: "YELLOW",
            YELLOW: "RED"
        };

        if (!(this.state in transitions)) {
            throw new Error(`Unknown traffic state: ${this.state}`);
        }

        this.state = transitions[this.state];
        this.cycles++;
    }
}

function simulateTrafficLight(cycles) {
    if (!Number.isInteger(cycles) || cycles < 0) {
        throw new Error("Cycles must be a non-negative integer.");
    }

    const light = new TrafficLight();
    const states = [light.state];
    let completed = 0;

    while (completed < cycles) {
        light.advance();
        states.push(light.state);
        completed++;
    }

    return states;
}


// ---------------------------------------------------------------------------
// 18. BOUNDED RETRIES
// ---------------------------------------------------------------------------

function retryOperation(operation, maximumAttempts) {
    if (!Number.isInteger(maximumAttempts) || maximumAttempts <= 0) {
        throw new Error("maximumAttempts must be positive.");
    }

    let attempt = 1;

    while (attempt <= maximumAttempts) {
        try {
            if (operation()) {
                return true;
            }
        } catch (error) {
            console.log(`Attempt ${attempt} failed: ${error.message}`);
        }

        attempt++;
    }

    return false;
}


// ---------------------------------------------------------------------------
// 19. QUEUE PROCESSING
// ---------------------------------------------------------------------------

function processQueue(tasks, processor) {
    const results = [];
    let position = 0;

    /*
     * Using an index avoids repeatedly shifting the entire array with
     * shift(), which can make repeated queue removal unnecessarily costly.
     */
    while (position < tasks.length) {
        results.push(processor(tasks[position]));
        position++;
    }

    return results;
}


// ---------------------------------------------------------------------------
// 20. ASYNCHRONOUS WHILE LOOP
// ---------------------------------------------------------------------------

function delay(milliseconds) {
    return new Promise(resolve => setTimeout(resolve, milliseconds));
}

async function asynchronousRetry(operation, maximumAttempts, delayMs) {
    if (maximumAttempts <= 0) {
        throw new Error("maximumAttempts must be positive.");
    }

    let attempt = 1;

    while (attempt <= maximumAttempts) {
        try {
            if (await operation(attempt)) {
                return true;
            }
        } catch (error) {
            console.log(`Async attempt ${attempt}: ${error.message}`);
        }

        if (attempt < maximumAttempts && delayMs > 0) {
            await delay(delayMs);
        }

        attempt++;
    }

    return false;
}


// ---------------------------------------------------------------------------
// 21. PAGINATION SIMULATION
// ---------------------------------------------------------------------------

async function fetchPage(pageNumber) {
    /*
     * This local simulation represents a paginated API without requiring
     * network access.
     */
    await delay(1);

    const pages = {
        1: ["A", "B", "C"],
        2: ["D", "E", "F"],
        3: ["G"]
    };

    return pages[pageNumber] || [];
}

async function collectAllPages() {
    const records = [];
    let pageNumber = 1;

    while (true) {
        const page = await fetchPage(pageNumber);

        if (page.length === 0) {
            break;
        }

        records.push(...page);
        pageNumber++;
    }

    return records;
}


// ---------------------------------------------------------------------------
// 22. EVENT-LOOP FRIENDLY CHUNKING
// ---------------------------------------------------------------------------

async function processLargeArrayInChunks(values, chunkSize, processor) {
    if (chunkSize <= 0) {
        throw new Error("chunkSize must be positive.");
    }

    let position = 0;

    while (position < values.length) {
        const end = Math.min(position + chunkSize, values.length);

        while (position < end) {
            processor(values[position]);
            position++;
        }

        /*
         * Yield to the JavaScript event loop between chunks.
         * This pattern can help prevent a long synchronous loop from
         * monopolizing the event loop in browser or server applications.
         */
        await delay(0);
    }
}


// ---------------------------------------------------------------------------
// 23. SLIDING-WINDOW REQUEST LIMIT
// ---------------------------------------------------------------------------

function allowRequests(requestTimes, windowSize, maximumRequests) {
    if (windowSize <= 0 || maximumRequests <= 0) {
        throw new Error("Window size and limit must be positive.");
    }

    const decisions = [];
    let left = 0;
    let index = 0;

    while (index < requestTimes.length) {
        const currentTime = requestTimes[index];

        while (
            left < index &&
            requestTimes[left] <= currentTime - windowSize
        ) {
            left++;
        }

        const requestsInWindow = index - left + 1;
        decisions.push(requestsInWindow <= maximumRequests);

        index++;
    }

    return decisions;
}


// ---------------------------------------------------------------------------
// 24. EDGE CASES AND LIMITATIONS
// ---------------------------------------------------------------------------

function edgeCases() {
    console.log("\n7. Edge cases");

    console.log("Empty binary search:", binarySearch([], 10));
    console.log("0!:", factorial(0));
    console.log("GCD(0, 24):", greatestCommonDivisor(0, 24));
    console.log("GCD(24, 0):", greatestCommonDivisor(24, 0));
    console.log("Fibonacci(0):", fibonacciTerms(0));
    console.log("Prime 1:", isPrime(1));
    console.log("Prime 97:", isPrime(97));

    /*
     * JavaScript numbers are IEEE-754 double-precision floating-point
     * values. Very large integers can lose exact precision. BigInt is
     * available when exact integer arithmetic beyond Number's safe range
     * is required.
     */
    const unsafe = Number.MAX_SAFE_INTEGER + 1;
    console.log("Large Number example:", unsafe);
    console.log("Use BigInt for exact large integers:", 9007199254740993n);
}


// ---------------------------------------------------------------------------
// 25. TESTS
// ---------------------------------------------------------------------------

function runTests() {
    console.log("\n8. Tests");

    console.assert(factorial(0) === 1);
    console.assert(factorial(5) === 120);

    console.assert(greatestCommonDivisor(48, 18) === 6);

    console.assert(binarySearch([1, 3, 5, 7, 9], 7) === 3);
    console.assert(binarySearch([1, 3, 5, 7, 9], 8) === -1);

    console.assert(JSON.stringify(fibonacciTerms(6)) === "[0,1,1,2,3,5]");

    console.assert(isPrime(2));
    console.assert(isPrime(97));
    console.assert(!isPrime(1));
    console.assert(!isPrime(100));

    console.assert(reverseString("abc") === "cba");
    console.assert(countCharacters("banana", "a") === 3);

    console.assert(
        JSON.stringify(filterPositive([-2, 3, 0, 5])) === "[3,5]"
    );

    console.assert(findFirst([10, 20, 30], 20) === 1);
    console.assert(findFirst([10, 20, 30], 99) === -1);

    console.log("All synchronous assertions passed.");
}


// ---------------------------------------------------------------------------
// 26. ASYNCHRONOUS TESTS
// ---------------------------------------------------------------------------

async function runAsyncExamples() {
    console.log("\n9. Asynchronous while-loop examples");

    const records = await collectAllPages();
    console.log("Collected pages:", records);

    let operationAttempts = 0;

    const retryResult = await asynchronousRetry(
        async attempt => {
            operationAttempts++;
            return attempt >= 3;
        },
        5,
        1
    );

    console.log("Async retry result:", retryResult);

    const processed = [];

    await processLargeArrayInChunks(
        [1, 2, 3, 4, 5, 6],
        2,
        value => processed.push(value * 2)
    );

    console.log("Chunked processing:", processed);
}


// ---------------------------------------------------------------------------
// 27. MAIN
// ---------------------------------------------------------------------------

async function main() {
    console.log("=".repeat(72));
    console.log("WHILE LOOPS IN JAVASCRIPT: COMPLETE STUDY PROGRAM");
    console.log("=".repeat(72));

    basicWhile();
    counterExamples();

    console.log("\nValidation result:", validateFromSequence(["abc", "-4", "25"]));

    console.log(
        "\nSentinel sum:",
        sumUntilSentinel([10, 20, 30, -1, 999])
    );

    console.log("\nFirst index of 35:", findFirst([11, 23, 35, 47], 35));
    console.log("First index of 99:", findFirst([11, 23, 35, 47], 99));

    printOddNumbers(10);
    doWhileExample();
    multiplicationTable(4);

    console.log("\n10. String processing");
    console.log("Reverse:", reverseString("while loops"));
    console.log("Count:", countCharacters("while loops", "l"));

    console.log("\n11. Array processing");
    console.log("Positive:", filterPositive([-5, 0, 4, 8, -2]));
    console.log("Statistics:", calculateStatistics([10, 20, 30, 40]));

    console.log("\n12. Algorithms");
    console.log("5! =", factorial(5));
    console.log("GCD =", greatestCommonDivisor(84, 30));
    console.log(
        "Binary search:",
        binarySearch([2, 4, 6, 8, 10, 12], 8)
    );
    console.log("Primality of 97:", isPrime(97));
    console.log("Fibonacci:", fibonacciTerms(10));
    console.log("Iterator:", consumeIterator(new Set([2, 4, 6])));

    console.log("\n13. State machine");
    console.log("States:", simulateTrafficLight(6));

    console.log("\n14. Queue");
    console.log(
        processQueue(["compile", "test", "package"], task => task.toUpperCase())
    );

    console.log("\n15. Retry");
    let attempts = 0;
    console.log(
        retryOperation(() => {
            attempts++;
            return attempts >= 3;
        }, 5)
    );

    console.log("\n16. Sliding-window decisions");
    console.log(
        allowRequests([0, 1, 2, 3, 7, 8], 5, 3)
    );

    edgeCases();
    runTests();
    await runAsyncExamples();

    console.log("\nKey principles:");
    console.log("A while loop checks its condition before each iteration.");
    console.log("A do...while loop checks its condition after each iteration.");
    console.log("break terminates the nearest loop.");
    console.log("continue skips the remainder of the current iteration.");
    console.log("Async while loops can await promises without blocking the thread.");
    console.log("Bounded termination and explicit progress prevent infinite loops.");
}

main().catch(error => {
    console.error("Program failed:", error);
    process.exitCode = 1;
});
