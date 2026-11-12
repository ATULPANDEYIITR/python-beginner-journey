"use strict";

/*
 * Virtual Environment Lifecycle and Policy Manager
 *
 * Models:
 * - Environment registration
 * - Project isolation policies
 * - Runtime compatibility
 * - Dependency locking
 * - Environment state transitions
 * - Event-driven monitoring
 * - Environment retirement
 *
 * Runtime: Node.js 18+
 * Dependencies: Node.js standard library only
 */

const fs = require("node:fs/promises");
const path = require("node:path");
const crypto = require("node:crypto");
const EventEmitter = require("node:events");

const EnvironmentState = Object.freeze({
    CREATED: "CREATED",
    CONFIGURING: "CONFIGURING",
    READY: "READY",
    FAILED: "FAILED",
    RETIRED: "RETIRED"
});

const RuntimeType = Object.freeze({
    PYTHON: "PYTHON",
    NODE: "NODE",
    JAVA: "JAVA"
});

class EnvironmentError extends Error {
    constructor(message, code = "ENVIRONMENT_ERROR") {
        super(message);
        this.name = "EnvironmentError";
        this.code = code;
    }
}

class EnvironmentPolicy {

    constructor({
        allowedRuntimes,
        minimumDiskSpaceMB = 100,
        maximumPackages = 1000,
        allowGlobalPackages = false,
        requireLockfile = true
    }) {

        this.allowedRuntimes = new Set(allowedRuntimes);

        this.minimumDiskSpaceMB = minimumDiskSpaceMB;
        this.maximumPackages = maximumPackages;
        this.allowGlobalPackages = allowGlobalPackages;
        this.requireLockfile = requireLockfile;

        if (this.allowedRuntimes.size === 0) {
            throw new EnvironmentError(
                "At least one runtime must be allowed."
            );
        }

        if (minimumDiskSpaceMB < 0 || maximumPackages < 1) {
            throw new EnvironmentError(
                "Invalid policy limits."
            );
        }
    }

    evaluate(configuration) {

        const violations = [];

        if (!this.allowedRuntimes.has(configuration.runtime)) {
            violations.push("Runtime is not permitted.");
        }

        if (
            configuration.diskSpaceMB <
            this.minimumDiskSpaceMB
        ) {
            violations.push("Insufficient disk allocation.");
        }

        if (
            configuration.packages.length >
            this.maximumPackages
        ) {
            violations.push("Package limit exceeded.");
        }

        if (
            !this.allowGlobalPackages &&
            configuration.globalPackages
        ) {
            violations.push("Global package access is prohibited.");
        }

        if (
            this.requireLockfile &&
            !configuration.lockfile
        ) {
            violations.push("A dependency lockfile is required.");
        }

        return {
            permitted: violations.length === 0,
            violations
        };
    }
}

class VirtualEnvironment {

    constructor(configuration) {

        this.id = crypto.randomUUID();

        this.name = configuration.name;
        this.project = configuration.project;
        this.runtime = configuration.runtime;
        this.runtimeVersion = configuration.runtimeVersion;

        this.packages = new Map();

        this.diskSpaceMB = configuration.diskSpaceMB;
        this.globalPackages = Boolean(
            configuration.globalPackages
        );

        this.lockfile = Boolean(configuration.lockfile);

        this.state = EnvironmentState.CREATED;

        this.createdAt = new Date().toISOString();
        this.updatedAt = this.createdAt;

        this.history = [
            {
                state: this.state,
                timestamp: this.createdAt
            }
        ];
    }

    transition(nextState) {

        const transitions = {
            CREATED: ["CONFIGURING", "RETIRED"],
            CONFIGURING: ["READY", "FAILED", "RETIRED"],
            READY: ["CONFIGURING", "FAILED", "RETIRED"],
            FAILED: ["CONFIGURING", "RETIRED"],
            RETIRED: []
        };

        if (
            !transitions[this.state].includes(nextState)
        ) {
            throw new EnvironmentError(
                `Invalid transition: ${this.state} -> ${nextState}`
            );
        }

        this.state = nextState;
        this.updatedAt = new Date().toISOString();

        this.history.push({
            state: nextState,
            timestamp: this.updatedAt
        });
    }

    addPackage(name, version) {

        if (this.state === EnvironmentState.RETIRED) {
            throw new EnvironmentError(
                "Cannot modify a retired environment."
            );
        }

        if (
            typeof name !== "string" ||
            !/^[a-zA-Z0-9_.-]+$/.test(name)
        ) {
            throw new EnvironmentError(
                "Invalid package name."
            );
        }

        if (
            typeof version !== "string" ||
            !/^[a-zA-Z0-9.+_-]+$/.test(version)
        ) {
            throw new EnvironmentError(
                "Invalid package version."
            );
        }

        this.packages.set(name.toLowerCase(), version);
        this.updatedAt = new Date().toISOString();
    }

    removePackage(name) {

        if (this.state === EnvironmentState.RETIRED) {
            throw new EnvironmentError(
                "Cannot modify a retired environment."
            );
        }

        return this.packages.delete(name.toLowerCase());
    }

    dependencySnapshot() {

        return Object.fromEntries(
            [...this.packages.entries()].sort(
                ([a], [b]) => a.localeCompare(b)
            )
        );
    }

    toJSON() {

        return {
            id: this.id,
            name: this.name,
            project: this.project,
            runtime: this.runtime,
            runtimeVersion: this.runtimeVersion,
            state: this.state,
            packages: this.dependencySnapshot(),
            diskSpaceMB: this.diskSpaceMB,
            globalPackages: this.globalPackages,
            lockfile: this.lockfile,
            createdAt: this.createdAt,
            updatedAt: this.updatedAt,
            history: this.history
        };
    }
}

class EnvironmentRegistry extends EventEmitter {

    constructor(policy) {

        super();

        this.policy = policy;
        this.environments = new Map();
        this.projectIndex = new Map();
    }

    validateConfiguration(configuration) {

        const required = [
            "name",
            "project",
            "runtime",
            "runtimeVersion"
        ];

        for (const field of required) {
            if (
                typeof configuration[field] !== "string" ||
                configuration[field].trim() === ""
            ) {
                throw new EnvironmentError(
                    `Missing or invalid field: ${field}`
                );
            }
        }

        if (
            !/^[a-zA-Z0-9_-]+$/.test(configuration.name)
        ) {
            throw new EnvironmentError(
                "Environment name contains invalid characters."
            );
        }

        if (!Array.isArray(configuration.packages)) {
            throw new EnvironmentError(
                "Packages must be an array."
            );
        }

        const decision = this.policy.evaluate(configuration);

        if (!decision.permitted) {
            throw new EnvironmentError(
                decision.violations.join("; "),
                "POLICY_REJECTED"
            );
        }

        return true;
    }

    register(configuration) {

        this.validateConfiguration(configuration);

        if (this.environments.has(configuration.name)) {
            throw new EnvironmentError(
                "Environment name already exists."
            );
        }

        const environment = new VirtualEnvironment(
            configuration
        );

        for (const dependency of configuration.packages) {
            environment.addPackage(
                dependency.name,
                dependency.version
            );
        }

        this.environments.set(
            environment.name,
            environment
        );

        if (!this.projectIndex.has(environment.project)) {
            this.projectIndex.set(
                environment.project,
                new Set()
            );
        }

        this.projectIndex
            .get(environment.project)
            .add(environment.name);

        this.emit("environment:registered", environment.toJSON());

        return environment;
    }

    async configure(name, configurator) {

        const environment = this.get(name);

        if (typeof configurator !== "function") {
            throw new EnvironmentError(
                "Configurator must be a function."
            );
        }

        environment.transition(EnvironmentState.CONFIGURING);

        this.emit("environment:configuring", environment.toJSON());

        try {

            await configurator(environment);

            environment.transition(EnvironmentState.READY);

            this.emit("environment:ready", environment.toJSON());

        } catch (error) {

            environment.transition(EnvironmentState.FAILED);

            this.emit("environment:failed", {
                name,
                message: error.message
            });

            throw error;
        }

        return environment;
    }

    get(name) {

        const environment = this.environments.get(name);

        if (!environment) {
            throw new EnvironmentError(
                `Environment '${name}' does not exist.`,
                "NOT_FOUND"
            );
        }

        return environment;
    }

    list(project = null) {

        if (project === null) {
            return [...this.environments.values()]
                .map(environment => environment.toJSON());
        }

        const names = this.projectIndex.get(project) || new Set();

        return [...names]
            .map(name => this.environments.get(name))
            .filter(Boolean)
            .map(environment => environment.toJSON());
    }

    retire(name) {

        const environment = this.get(name);

        environment.transition(EnvironmentState.RETIRED);

        this.emit("environment:retired", environment.toJSON());

        return environment;
    }

    async exportManifest(name, outputDirectory) {

        const environment = this.get(name);

        if (environment.state !== EnvironmentState.READY) {
            throw new EnvironmentError(
                "Only ready environments can be exported."
            );
        }

        const directory = path.resolve(outputDirectory);

        await fs.mkdir(directory, { recursive: true });

        const filename = `${environment.id}.json`;
        const destination = path.join(directory, filename);

        await fs.writeFile(
            destination,
            JSON.stringify(environment.toJSON(), null, 2),
            { flag: "wx", mode: 0o600 }
        );

        this.emit("manifest:exported", {
            name,
            destination
        });

        return destination;
    }
}

async function demonstrate() {

    const policy = new EnvironmentPolicy({
        allowedRuntimes: [
            RuntimeType.PYTHON,
            RuntimeType.NODE
        ],
        minimumDiskSpaceMB: 100,
        maximumPackages: 50,
        allowGlobalPackages: false,
        requireLockfile: true
    });

    const registry = new EnvironmentRegistry(policy);

    registry.on("environment:registered", event => {
        console.log("REGISTERED:", event.name);
    });

    registry.on("environment:ready", event => {
        console.log("READY:", event.name);
    });

    registry.on("environment:failed", event => {
        console.error("FAILED:", event.name, event.message);
    });

    const environment = registry.register({
        name: "analytics-dev",
        project: "analytics-platform",
        runtime: RuntimeType.PYTHON,
        runtimeVersion: "3.13",
        diskSpaceMB: 2048,
        globalPackages: false,
        lockfile: true,
        packages: [
            { name: "numpy", version: "2.3.0" },
            { name: "pandas", version: "2.3.0" },
            { name: "pytest", version: "8.4.0" }
        ]
    });

    await registry.configure(
        environment.name,
        async env => {

            await new Promise(resolve =>
                setTimeout(resolve, 50)
            );

            env.addPackage("requests", "2.32.4");
        }
    );

    console.log("\nEnvironment inventory:");

    console.log(
        JSON.stringify(
            registry.list("analytics-platform"),
            null,
            2
        )
    );

    console.log("\nDependency snapshot:");

    console.log(environment.dependencySnapshot());

    console.log("\nExporting manifest:");

    const outputDirectory = path.join(
        process.cwd(),
        "environment-manifests"
    );

    try {

        const manifest = await registry.exportManifest(
            environment.name,
            outputDirectory
        );

        console.log("Manifest:", manifest);

    } catch (error) {
        console.error("Export failed:", error.message);
    }

    console.log("\nTesting policy rejection:");

    try {

        registry.register({
            name: "invalid-environment",
            project: "analytics-platform",
            runtime: RuntimeType.JAVA,
            runtimeVersion: "17",
            diskSpaceMB: 512,
            globalPackages: true,
            lockfile: true,
            packages: []
        });

    } catch (error) {
        console.log("Rejected:", error.message);
    }

    console.log("\nRetiring environment:");

    registry.retire(environment.name);
}

demonstrate().catch(error => {
    console.error("Application failure:", error);
    process.exitCode = 1;
});
