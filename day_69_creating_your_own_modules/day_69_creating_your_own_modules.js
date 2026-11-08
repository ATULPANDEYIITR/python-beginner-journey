"use strict";

/*
 * Creating Your Own Modules
 * Node.js ES module architecture and event-driven module registry.
 *
 * Run with:
 * node --input-type=module module-system.js
 *
 * Demonstrates:
 * - Module contracts
 * - Module registration and discovery
 * - Semantic version validation
 * - Dependency resolution
 * - Event-driven lifecycle management
 * - Asynchronous execution
 * - Capability-based permissions
 * - Configuration validation
 * - Error isolation
 */

import { EventEmitter } from "node:events";
import { createHash, randomUUID } from "node:crypto";
import { pathToFileURL } from "node:url";
import path from "node:path";


class ModuleError extends Error {}
class ValidationError extends ModuleError {}
class DependencyError extends ModuleError {}
class PermissionError extends ModuleError {}


const ModuleState = Object.freeze({
    REGISTERED: "REGISTERED",
    INITIALIZED: "INITIALIZED",
    ACTIVE: "ACTIVE",
    FAILED: "FAILED",
    DISABLED: "DISABLED"
});


function validateName(name) {
    if (
        typeof name !== "string" ||
        !/^[a-z][a-z0-9_]*$/.test(name)
    ) {
        throw new ValidationError(`Invalid module name: ${name}`);
    }
}


function parseVersion(version) {
    if (
        typeof version !== "string" ||
        !/^\d+\.\d+\.\d+$/.test(version)
    ) {
        throw new ValidationError(
            `Invalid semantic version: ${version}`
        );
    }

    return version.split(".").map(Number);
}


function compareVersions(left, right) {
    const a = parseVersion(left);
    const b = parseVersion(right);

    for (let i = 0; i < 3; i++) {
        if (a[i] !== b[i]) {
            return a[i] - b[i];
        }
    }

    return 0;
}


class ModuleRegistry extends EventEmitter {
    #modules = new Map();
    #allowedPermissions = new Set([
        "calculate",
        "read_data",
        "write_data",
        "export_data"
    ]);

    constructor() {
        super();

        this.setMaxListeners(50);
    }

    register(metadata, implementation) {
        validateName(metadata.name);

        parseVersion(metadata.version);

        if (this.#modules.has(metadata.name)) {
            throw new ValidationError(
                `Duplicate module: ${metadata.name}`
            );
        }

        if (
            !metadata.description ||
            typeof metadata.description !== "string"
        ) {
            throw new ValidationError(
                "Module description is required."
            );
        }

        if (
            !implementation ||
            typeof implementation.initialize !== "function" ||
            typeof implementation.execute !== "function" ||
            typeof implementation.shutdown !== "function"
        ) {
            throw new ValidationError(
                "Implementation does not satisfy module contract."
            );
        }

        const permissions = new Set(
            metadata.permissions ?? []
        );

        for (const permission of permissions) {
            if (!this.#allowedPermissions.has(permission)) {
                throw new PermissionError(
                    `Unauthorized permission: ${permission}`
                );
            }
        }

        const record = {
            metadata: Object.freeze({
                ...metadata,
                dependencies: Object.freeze([
                    ...(metadata.dependencies ?? [])
                ]),
                permissions
            }),
            implementation,
            state: ModuleState.REGISTERED,
            executionCount: 0,
            lastError: null,
            configuration: {}
        };

        this.#modules.set(metadata.name, record);

        this.emit("module:registered", {
            name: metadata.name
        });

        return record;
    }

    get(name) {
        const record = this.#modules.get(name);

        if (!record) {
            throw new ValidationError(
                `Module not found: ${name}`
            );
        }

        return record;
    }

    inventory() {
        return Array.from(
            this.#modules.values(),
            record => ({
                name: record.metadata.name,
                version: record.metadata.version,
                state: record.state,
                executions: record.executionCount,
                lastError: record.lastError
            })
        );
    }

    resolveDependencies(name) {
        const visited = new Set();
        const active = new Set();
        const order = [];

        const visit = current => {
            if (active.has(current)) {
                throw new DependencyError(
                    `Circular dependency: ${current}`
                );
            }

            if (visited.has(current)) {
                return;
            }

            const record = this.get(current);

            active.add(current);

            for (const dependency of record.metadata.dependencies) {
                const required = this.get(dependency.name);

                if (
                    compareVersions(
                        required.metadata.version,
                        dependency.minimumVersion ?? "1.0.0"
                    ) < 0
                ) {
                    throw new DependencyError(
                        `Insufficient version of ${dependency.name}`
                    );
                }

                if (required.state === ModuleState.DISABLED) {
                    throw new DependencyError(
                        `Dependency ${dependency.name} is disabled.`
                    );
                }

                visit(dependency.name);
            }

            active.delete(current);
            visited.add(current);
            order.push(current);
        };

        visit(name);

        return order;
    }

    async activate(name, configurations = {}) {
        const order = this.resolveDependencies(name);

        for (const current of order) {
            const record = this.get(current);

            if (record.state === ModuleState.ACTIVE) {
                continue;
            }

            if (record.state === ModuleState.DISABLED) {
                throw new ModuleError(
                    `Module ${current} is disabled.`
                );
            }

            try {
                const configuration =
                    configurations[current] ?? {};

                await record.implementation.initialize(
                    Object.freeze({ ...configuration })
                );

                record.configuration = { ...configuration };
                record.state = ModuleState.ACTIVE;

                this.emit("module:activated", {
                    name: current
                });

            } catch (error) {
                record.state = ModuleState.FAILED;
                record.lastError = error.message;

                this.emit("module:failed", {
                    name: current,
                    error: error.message
                });

                throw new ModuleError(
                    `Activation failed for ${current}: ${error.message}`
                );
            }
        }
    }

    async execute(name, payload, callerPermissions = []) {
        const record = this.get(name);

        if (record.state !== ModuleState.ACTIVE) {
            throw new ModuleError(
                `Module ${name} is not active.`
            );
        }

        if (
            payload === null ||
            typeof payload !== "object" ||
            Array.isArray(payload)
        ) {
            throw new ValidationError(
                "Payload must be an object."
            );
        }

        const granted = new Set(callerPermissions);

        for (const permission of record.metadata.permissions) {
            if (!granted.has(permission)) {
                throw new PermissionError(
                    `Caller lacks ${permission} permission.`
                );
            }
        }

        const executionId = randomUUID();
        const start = performance.now();

        this.emit("execution:started", {
            executionId,
            name
        });

        try {
            const result = await record.implementation.execute(
                Object.freeze({ ...payload })
            );

            if (
                result === null ||
                typeof result !== "object" ||
                Array.isArray(result)
            ) {
                throw new ModuleError(
                    "Module must return an object."
                );
            }

            record.executionCount++;

            const event = {
                executionId,
                name,
                durationMs: performance.now() - start,
                resultHash: createHash("sha256")
                    .update(JSON.stringify(result))
                    .digest("hex")
            };

            this.emit("execution:completed", event);

            return {
                executionId,
                result,
                durationMs: event.durationMs
            };

        } catch (error) {
            record.lastError = error.message;

            this.emit("execution:failed", {
                executionId,
                name,
                error: error.message
            });

            throw new ModuleError(
                `Execution failed: ${error.message}`
            );
        }
    }

    async disable(name) {
        const record = this.get(name);

        if (record.state === ModuleState.DISABLED) {
            return;
        }

        const dependents = Array.from(
            this.#modules.values()
        ).filter(candidate =>
            candidate.metadata.dependencies.some(
                dependency => dependency.name === name
            ) && candidate.state === ModuleState.ACTIVE
        );

        if (dependents.length > 0) {
            throw new DependencyError(
                `Active dependents: ${
                    dependents.map(item =>
                        item.metadata.name
                    ).join(", ")
                }`
            );
        }

        if (record.state === ModuleState.ACTIVE) {
            await record.implementation.shutdown();
        }

        record.state = ModuleState.DISABLED;

        this.emit("module:disabled", { name });
    }
}


class AnalyticsModule {
    async initialize(configuration) {
        this.precision = configuration.precision ?? 2;

        if (
            !Number.isInteger(this.precision) ||
            this.precision < 0 ||
            this.precision > 10
        ) {
            throw new ValidationError(
                "Precision must be an integer from 0 to 10."
            );
        }
    }

    async execute(payload) {
        const values = payload.values;
        const operation = payload.operation;

        if (
            !Array.isArray(values) ||
            values.length === 0 ||
            !values.every(
                value =>
                    typeof value === "number" &&
                    Number.isFinite(value)
            )
        ) {
            throw new ValidationError(
                "Provide a non-empty array of finite numbers."
            );
        }

        let result;

        switch (operation) {
            case "sum":
                result = values.reduce(
                    (total, value) => total + value,
                    0
                );
                break;

            case "average":
                result = values.reduce(
                    (total, value) => total + value,
                    0
                ) / values.length;
                break;

            case "maximum":
                result = Math.max(...values);
                break;

            default:
                throw new ValidationError(
                    `Unsupported operation: ${operation}`
                );
        }

        return {
            operation,
            result: Number(result.toFixed(this.precision)),
            inputCount: values.length
        };
    }

    async shutdown() {
        this.precision = null;
    }
}


class ReportingModule {
    async initialize(configuration) {
        this.title = configuration.title ??
            "Analytics Report";
    }

    async execute(payload) {
        if (!Array.isArray(payload.records)) {
            throw new ValidationError(
                "Report records must be an array."
            );
        }

        return {
            title: this.title,
            generatedAt: new Date().toISOString(),
            recordCount: payload.records.length,
            records: payload.records
        };
    }

    async shutdown() {
        this.title = null;
    }
}


async function loadTrustedESModule(filePath) {
    const absolutePath = path.resolve(filePath);

    if (path.extname(absolutePath) !== ".mjs") {
        throw new ValidationError(
            "Only .mjs modules are accepted."
        );
    }

    // Import executes the target module. Never import untrusted files.
    return import(pathToFileURL(absolutePath).href);
}


async function main() {
    const registry = new ModuleRegistry();

    registry.on("module:activated", event => {
        console.log("ACTIVATED:", event.name);
    });

    registry.on("execution:completed", event => {
        console.log(
            "EXECUTION:",
            event.name,
            event.durationMs.toFixed(3),
            "ms"
        );
    });

    registry.on("module:failed", event => {
        console.error("MODULE FAILURE:", event);
    });

    registry.register(
        {
            name: "analytics",
            version: "2.1.0",
            description: "Numerical analytics module",
            permissions: ["calculate"],
            dependencies: []
        },
        new AnalyticsModule()
    );

    registry.register(
        {
            name: "reporting",
            version: "1.0.0",
            description: "Structured report generation",
            permissions: ["read_data", "export_data"],
            dependencies: [
                {
                    name: "analytics",
                    minimumVersion: "2.0.0"
                }
            ]
        },
        new ReportingModule()
    );

    await registry.activate("reporting", {
        analytics: { precision: 3 },
        reporting: { title: "Monthly Analytics" }
    });

    const analytics = await registry.execute(
        "analytics",
        {
            operation: "average",
            values: [12, 24, 36, 48]
        },
        ["calculate"]
    );

    const report = await registry.execute(
        "reporting",
        {
            records: [analytics.result]
        },
        ["read_data", "export_data"]
    );

    console.log("\nAnalytics Result:");
    console.log(analytics);

    console.log("\nGenerated Report:");
    console.log(report);

    console.log("\nModule Inventory:");
    console.table(registry.inventory());

    try {
        await registry.execute(
            "analytics",
            {
                operation: "average",
                values: [1, 2]
            },
            []
        );
    } catch (error) {
        console.log("\nExpected permission failure:", error.message);
    }

    try {
        await registry.execute(
            "analytics",
            {
                operation: "unknown",
                values: [1, 2]
            },
            ["calculate"]
        );
    } catch (error) {
        console.log("\nExpected validation failure:", error.message);
    }

    await registry.disable("reporting");
    await registry.disable("analytics");
}


main().catch(error => {
    console.error("Application failure:", error);
    process.exitCode = 1;
});
