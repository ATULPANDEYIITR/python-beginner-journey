"use strict";

/*
 * IMPORTING MODULES IN JAVASCRIPT
 *
 * Node.js ES modules demonstration.
 *
 * Run with:
 * node --input-type=module importing-modules.mjs
 *
 * The implementation explores static imports, dynamic imports,
 * module namespaces, dependency caching, module loading events,
 * circular dependency concepts, import validation, and failures.
 */

// ---------------------------------------------------------
// 1. Standard module imports
// ---------------------------------------------------------

import {
    createHash,
    randomUUID
} from "node:crypto";

import {
    readFile,
    writeFile,
    mkdtemp,
    rm
} from "node:fs/promises";

import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

import { EventEmitter } from "node:events";


// ---------------------------------------------------------
// 2. Module metadata
// ---------------------------------------------------------

const MODULE_NAME = "importing-modules";
const SUPPORTED_MODULES = new Set([
    "node:crypto",
    "node:os",
    "node:path",
    "node:events",
    "node:util"
]);

function displayModuleInformation() {
    console.log("\n1. MODULE INFORMATION");

    console.log("Module:", MODULE_NAME);
    console.log("Node version:", process.version);
    console.log("Platform:", process.platform);
    console.log("Architecture:", process.arch);
    console.log("Temporary directory:", os.tmpdir());
}


// ---------------------------------------------------------
// 3. Module namespace objects
// ---------------------------------------------------------

async function inspectModuleNamespace() {
    console.log("\n2. MODULE NAMESPACE");

    const cryptoModule = await import("node:crypto");

    console.log(
        "Namespace exports:",
        Object.keys(cryptoModule).slice(0, 10)
    );

    console.log(
        "Hash function available:",
        typeof cryptoModule.createHash === "function"
    );
}


// ---------------------------------------------------------
// 4. Dynamic module imports
// ---------------------------------------------------------

async function loadAuthorizedModule(specifier) {

    if (
        typeof specifier !== "string" ||
        !SUPPORTED_MODULES.has(specifier)
    ) {
        throw new Error(
            `Module is not in the import allowlist: ${specifier}`
        );
    }

    try {
        return await import(specifier);
    } catch (error) {
        throw new Error(
            `Failed to import ${specifier}: ${error.message}`,
            { cause: error }
        );
    }
}

async function demonstrateDynamicImports() {
    console.log("\n3. DYNAMIC IMPORT");

    const crypto = await loadAuthorizedModule("node:crypto");
    const osModule = await loadAuthorizedModule("node:os");

    console.log(
        "Generated identifier:",
        crypto.randomUUID()
    );

    console.log(
        "Free memory:",
        osModule.freemem()
    );

    try {
        await loadAuthorizedModule("node:child_process");
    } catch (error) {
        console.log("Import blocked:", error.message);
    }
}


// ---------------------------------------------------------
// 5. Module caching
// ---------------------------------------------------------

async function demonstrateModuleCaching() {
    console.log("\n4. MODULE CACHING");

    const first = await import("node:path");
    const second = await import("node:path");

    console.log(
        "Same namespace object:",
        first === second
    );

    console.log(
        "Resolved module:",
        first.default.sep
    );

    // ES modules are cached by resolved module identity.
    // Repeated imports normally reuse the evaluated module.
}


// ---------------------------------------------------------
// 6. Loading local modules dynamically
// ---------------------------------------------------------

async function demonstrateLocalModuleImport() {
    console.log("\n5. LOCAL MODULE IMPORT");

    const directory = await mkdtemp(
        path.join(os.tmpdir(), "module-demo-")
    );

    const moduleFile = path.join(
        directory,
        "calculator.mjs"
    );

    try {
        const source = `
            export const moduleName = "calculator";

            export function multiply(a, b) {
                if (!Number.isFinite(a) || !Number.isFinite(b)) {
                    throw new TypeError("Arguments must be finite numbers");
                }

                return a * b;
            }

            export default {
                version: "1.0"
            };
        `;

        await writeFile(
            moduleFile,
            source,
            { encoding: "utf8", flag: "wx" }
        );

        const moduleURL = pathToFileURL(moduleFile);

        const calculator = await import(moduleURL.href);

        console.log("Name:", calculator.moduleName);
        console.log("Version:", calculator.default.version);
        console.log("Calculation:", calculator.multiply(12, 8));

        try {
            calculator.multiply("12", 8);
        } catch (error) {
            console.log("Validation:", error.message);
        }

    } finally {
        await rm(directory, {
            recursive: true,
            force: true
        });
    }
}


// ---------------------------------------------------------
// 7. Event-driven module loading
// ---------------------------------------------------------

class ModuleLoader extends EventEmitter {

    constructor(allowlist) {
        super();

        this.allowlist = new Set(allowlist);
        this.cache = new Map();
        this.pending = new Map();
    }

    async load(specifier) {

        if (!this.allowlist.has(specifier)) {
            this.emit("rejected", specifier);

            throw new Error(
                `Unauthorized module: ${specifier}`
            );
        }

        if (this.cache.has(specifier)) {
            this.emit("cacheHit", specifier);
            return this.cache.get(specifier);
        }

        // Concurrent callers share the same pending Promise.
        if (this.pending.has(specifier)) {
            return this.pending.get(specifier);
        }

        this.emit("loading", specifier);

        const operation = import(specifier)
            .then(module => {
                this.cache.set(specifier, module);
                this.emit("loaded", specifier);

                return module;
            })
            .catch(error => {
                this.emit("failed", {
                    specifier,
                    message: error.message
                });

                throw error;
            })
            .finally(() => {
                this.pending.delete(specifier);
            });

        this.pending.set(specifier, operation);

        return operation;
    }
}

async function demonstrateEventDrivenLoading() {
    console.log("\n6. EVENT-DRIVEN LOADING");

    const loader = new ModuleLoader([
        "node:crypto",
        "node:path"
    ]);

    loader.on("loading", name => {
        console.log("Loading:", name);
    });

    loader.on("loaded", name => {
        console.log("Loaded:", name);
    });

    loader.on("cacheHit", name => {
        console.log("Cache hit:", name);
    });

    loader.on("rejected", name => {
        console.log("Rejected:", name);
    });

    loader.on("failed", event => {
        console.log("Failure:", event);
    });

    const [first, second] = await Promise.all([
        loader.load("node:crypto"),
        loader.load("node:crypto")
    ]);

    console.log("Concurrent result:", first === second);

    await loader.load("node:crypto");
}


// ---------------------------------------------------------
// 8. Import dependency graph
// ---------------------------------------------------------

class DependencyGraph {

    constructor() {
        this.dependencies = new Map();
    }

    addModule(name, dependencies = []) {

        if (this.dependencies.has(name)) {
            throw new Error(`Duplicate module: ${name}`);
        }

        if (
            !Array.isArray(dependencies) ||
            dependencies.some(
                item => typeof item !== "string" || !item.trim()
            )
        ) {
            throw new TypeError("Invalid dependency list");
        }

        this.dependencies.set(name, new Set(dependencies));
    }

    topologicalOrder() {

        const visited = new Set();
        const active = new Set();
        const result = [];

        const visit = name => {

            if (active.has(name)) {
                throw new Error(
                    `Circular dependency involving ${name}`
                );
            }

            if (visited.has(name)) {
                return;
            }

            if (!this.dependencies.has(name)) {
                throw new Error(
                    `Unknown dependency: ${name}`
                );
            }

            active.add(name);

            for (const dependency of this.dependencies.get(name)) {
                visit(dependency);
            }

            active.delete(name);
            visited.add(name);
            result.push(name);
        };

        for (const name of this.dependencies.keys()) {
            visit(name);
        }

        return result;
    }
}

function demonstrateDependencyGraph() {
    console.log("\n7. DEPENDENCY GRAPH");

    const graph = new DependencyGraph();

    graph.addModule("configuration");
    graph.addModule("database", ["configuration"]);
    graph.addModule("services", ["database"]);
    graph.addModule("application", [
        "configuration",
        "services"
    ]);

    console.log(
        "Loading order:",
        graph.topologicalOrder()
    );

    const circular = new DependencyGraph();

    circular.addModule("first", ["second"]);
    circular.addModule("second", ["first"]);

    try {
        circular.topologicalOrder();
    } catch (error) {
        console.log("Circular dependency:", error.message);
    }
}


// ---------------------------------------------------------
// 9. Module file integrity
// ---------------------------------------------------------

async function demonstrateIntegrity() {
    console.log("\n8. FILE INTEGRITY");

    const directory = await mkdtemp(
        path.join(os.tmpdir(), "integrity-demo-")
    );

    const file = path.join(directory, "module-data.json");

    try {
        const content = JSON.stringify({
            module: "analytics",
            version: 1,
            enabled: true
        });

        await writeFile(file, content, {
            encoding: "utf8",
            flag: "wx"
        });

        const stored = await readFile(file, "utf8");

        const hash = createHash("sha256")
            .update(stored)
            .digest("hex");

        console.log("SHA-256:", hash);
        console.log("Parsed:", JSON.parse(stored));

    } finally {
        await rm(directory, {
            recursive: true,
            force: true
        });
    }
}


// ---------------------------------------------------------
// 10. Validation tests
// ---------------------------------------------------------

async function runTests() {

    const graph = new DependencyGraph();

    graph.addModule("base");
    graph.addModule("service", ["base"]);

    const order = graph.topologicalOrder();

    if (
        order.indexOf("base") >
        order.indexOf("service")
    ) {
        throw new Error("Dependency ordering test failed");
    }

    const loader = new ModuleLoader(["node:path"]);

    const first = await loader.load("node:path");
    const second = await loader.load("node:path");

    if (first !== second) {
        throw new Error("Module caching test failed");
    }

    let rejected = false;

    try {
        await loader.load("node:fs");
    } catch {
        rejected = true;
    }

    if (!rejected) {
        throw new Error("Import authorization test failed");
    }

    console.log("\nAll JavaScript tests passed.");
}


// ---------------------------------------------------------
// 11. Application entry point
// ---------------------------------------------------------

async function main() {

    try {
        displayModuleInformation();

        await inspectModuleNamespace();
        await demonstrateDynamicImports();
        await demonstrateModuleCaching();
        await demonstrateLocalModuleImport();
        await demonstrateEventDrivenLoading();

        demonstrateDependencyGraph();

        await demonstrateIntegrity();
        await runTests();

        console.log("\nExecution completed.");

    } catch (error) {
        console.error("Application failure:", error);

        if (error.cause) {
            console.error("Underlying cause:", error.cause);
        }

        process.exitCode = 1;
    }
}

main();
