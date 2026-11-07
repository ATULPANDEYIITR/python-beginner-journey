/**
 * Introduction to JavaScript Modules
 *
 * Demonstrates:
 * - ES module scope
 * - Named and default exports
 * - Module namespaces
 * - Built-in Node.js modules
 * - Dynamic imports
 * - Asynchronous module loading
 * - Dependency management
 * - Event-driven module communication
 *
 * Run: node introduction-to-modules.mjs
 */

import { EventEmitter } from "node:events";
import { pathToFileURL } from "node:url";
import path from "node:path";

// ---------------------------------------------------------
// 1. Module constants and private state
// ---------------------------------------------------------

const APPLICATION_VERSION = "1.0.0";

const internalState = {
    initialized: false,
    executionCount: 0
};

// ---------------------------------------------------------
// 2. Named exports
// ---------------------------------------------------------

export function add(a, b) {
    validateNumbers(a, b);
    return a + b;
}

export function multiply(a, b) {
    validateNumbers(a, b);
    return a * b;
}

export function divide(a, b) {
    validateNumbers(a, b);

    if (b === 0) {
        throw new RangeError("Division by zero is not allowed");
    }

    return a / b;
}

function validateNumbers(...values) {
    if (!values.every(Number.isFinite)) {
        throw new TypeError("All arguments must be finite numbers");
    }
}

// ---------------------------------------------------------
// 3. Default export
// ---------------------------------------------------------

export default class CalculatorModule {
    constructor(name = "Calculator") {
        if (!name.trim()) {
            throw new TypeError("Module name cannot be empty");
        }

        this.name = name;
    }

    calculate(operation, a, b) {
        const operations = {
            add,
            multiply,
            divide
        };

        if (!Object.hasOwn(operations, operation)) {
            throw new Error(`Unsupported operation: ${operation}`);
        }

        return operations[operation](a, b);
    }
}

// ---------------------------------------------------------
// 4. Module namespace and metadata
// ---------------------------------------------------------

export const moduleMetadata = Object.freeze({
    name: "calculator-module",
    version: APPLICATION_VERSION,
    format: "ECMAScript Module",
    exports: ["add", "multiply", "divide", "CalculatorModule"]
});

// ---------------------------------------------------------
// 5. Dependency registry
// ---------------------------------------------------------

export class DependencyRegistry {
    #modules = new Map();

    register(name, dependencies = []) {
        if (!/^[a-zA-Z][a-zA-Z0-9_-]*$/.test(name)) {
            throw new TypeError("Invalid module identifier");
        }

        if (this.#modules.has(name)) {
            throw new Error(`Module already registered: ${name}`);
        }

        if (!Array.isArray(dependencies) ||
            !dependencies.every(item => typeof item === "string")) {
            throw new TypeError("Dependencies must be an array of names");
        }

        if (dependencies.includes(name)) {
            throw new Error("A module cannot depend on itself");
        }

        this.#modules.set(name, Object.freeze([...dependencies]));
    }

    resolve(name) {
        if (!this.#modules.has(name)) {
            throw new Error(`Unknown module: ${name}`);
        }

        const result = [];
        const visiting = new Set();
        const visited = new Set();

        const visit = current => {
            if (visiting.has(current)) {
                throw new Error(`Circular dependency: ${current}`);
            }

            if (visited.has(current)) {
                return;
            }

            if (!this.#modules.has(current)) {
                throw new Error(`Missing dependency: ${current}`);
            }

            visiting.add(current);

            for (const dependency of this.#modules.get(current)) {
                visit(dependency);
            }

            visiting.delete(current);
            visited.add(current);
            result.push(current);
        };

        visit(name);
        return result;
    }

    list() {
        return [...this.#modules.keys()].sort();
    }
}

// ---------------------------------------------------------
// 6. Dynamic imports
// ---------------------------------------------------------

export async function loadStandardLibraryModule() {
    // Dynamic import returns a Promise containing the module namespace.
    const crypto = await import("node:crypto");

    return {
        randomIdentifier: crypto.randomUUID(),
        algorithm: crypto.getHashes().includes("sha256")
            ? "SHA-256"
            : "Unavailable"
    };
}

// ---------------------------------------------------------
// 7. Event-driven module communication
// ---------------------------------------------------------

export class ModuleEventBus extends EventEmitter {
    publish(eventName, payload) {
        if (typeof eventName !== "string" || !eventName.trim()) {
            throw new TypeError("Invalid event name");
        }

        if (payload === undefined) {
            throw new TypeError("Event payload is required");
        }

        this.emit(eventName, Object.freeze({ ...payload }));
    }
}

// ---------------------------------------------------------
// 8. Asynchronous module service
// ---------------------------------------------------------

export class ReportingModule {
    async generateReport(records) {
        if (!Array.isArray(records)) {
            throw new TypeError("Records must be an array");
        }

        if (!records.every(Number.isFinite)) {
            throw new TypeError("Records must contain finite numbers");
        }

        // Yield to the event loop before processing.
        await new Promise(resolve => setImmediate(resolve));

        return Object.freeze({
            count: records.length,
            total: records.reduce((sum, value) => sum + value, 0),
            average: records.length
                ? records.reduce((sum, value) => sum + value, 0) / records.length
                : 0
        });
    }
}

// ---------------------------------------------------------
// 9. Demonstration and validation
// ---------------------------------------------------------

async function main() {
    console.log("\n1. MODULE INFORMATION");
    console.log(moduleMetadata);

    console.log("\n2. MODULE FUNCTIONS");

    console.log("Addition:", add(20, 10));
    console.log("Multiplication:", multiply(5, 6));
    console.log("Division:", divide(100, 4));

    const calculator = new CalculatorModule("Financial Calculator");

    console.log("\n3. CLASS-BASED MODULE");
    console.log("Calculator:", calculator.name);
    console.log("Result:", calculator.calculate("multiply", 8, 5));

    console.log("\n4. MODULE DEPENDENCIES");

    const registry = new DependencyRegistry();

    registry.register("core");
    registry.register("database", ["core"]);
    registry.register("analytics", ["core", "database"]);
    registry.register("dashboard", ["analytics"]);

    console.log("Load order:", registry.resolve("dashboard"));
    console.log("Registered modules:", registry.list());

    console.log("\n5. DYNAMIC IMPORT");

    const cryptoInfo = await loadStandardLibraryModule();
    console.log(cryptoInfo);

    console.log("\n6. EVENT-DRIVEN MODULES");

    const bus = new ModuleEventBus();

    bus.on("report.completed", event => {
        console.log("Report received:", event);
        internalState.executionCount++;
    });

    bus.publish("report.completed", {
        module: "reporting",
        status: "success"
    });

    console.log("\n7. ASYNCHRONOUS MODULE");

    const reporting = new ReportingModule();

    const report = await reporting.generateReport([
        100, 200, 300, 400
    ]);

    console.log("Report:", report);

    console.log("\n8. ERROR HANDLING");

    const invalidCases = [
        () => add("10", 20),
        () => divide(10, 0),
        () => calculator.calculate("subtract", 5, 2),
        () => registry.resolve("missing")
    ];

    for (const test of invalidCases) {
        try {
            test();
        } catch (error) {
            console.log(`${error.name}: ${error.message}`);
        }
    }

    console.log("\n9. BUILT-IN NODE.JS MODULES");

    console.log("Current directory:", process.cwd());
    console.log("Path separator:", path.sep);
    console.log(
        "Current module URL:",
        import.meta.url || pathToFileURL(process.argv[1]).href
    );

    console.log("\n10. ASSERTIONS");

    if (add(2, 3) !== 5) {
        throw new Error("Addition test failed");
    }

    if (multiply(4, 5) !== 20) {
        throw new Error("Multiplication test failed");
    }

    if (report.average !== 250) {
        throw new Error("Reporting test failed");
    }

    internalState.initialized = true;

    console.log("All tests passed.");
    console.log("Initialized:", internalState.initialized);
    console.log("Event executions:", internalState.executionCount);
}

const isMainModule = process.argv[1] &&
    import.meta.url === pathToFileURL(
        path.resolve(process.argv[1])
    ).href;

if (isMainModule) {
    main().catch(error => {
        console.error("Application failure:", error.message);
        process.exitCode = 1;
    });
}
