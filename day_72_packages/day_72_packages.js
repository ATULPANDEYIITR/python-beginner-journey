"use strict";

/*
 * Python Package Ecosystem:
 * Package registry, dependency policies, version validation,
 * dependency graph traversal, installation state, security auditing,
 * asynchronous operations, and lock-file generation.
 *
 * Runtime: Node.js 18+
 * No external npm dependencies.
 */

const crypto = require("node:crypto");
const fs = require("node:fs/promises");
const path = require("node:path");
const { EventEmitter } = require("node:events");


class PackageError extends Error {
    constructor(message) {
        super(message);
        this.name = "PackageError";
    }
}

class DependencyError extends PackageError {
    constructor(message) {
        super(message);
        this.name = "DependencyError";
    }
}

class PolicyError extends PackageError {
    constructor(message) {
        super(message);
        this.name = "PolicyError";
    }
}


function normalizeName(name) {
    if (typeof name !== "string") {
        throw new PackageError("Package name must be a string.");
    }

    if (
        !/^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,198}[A-Za-z0-9])?$/.test(name) ||
        name.includes("..")
    ) {
        throw new PackageError(`Invalid package name: ${name}`);
    }

    return name.replace(/[-_.]+/g, "-").toLowerCase();
}


function parseVersion(version) {
    if (typeof version !== "string") {
        throw new PackageError("Version must be a string.");
    }

    const match = version.match(
        /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/
    );

    if (!match) {
        throw new PackageError(`Invalid version: ${version}`);
    }

    return match.slice(1).map(Number);
}


function compareVersions(a, b) {
    const left = parseVersion(a);
    const right = parseVersion(b);

    for (let i = 0; i < 3; i++) {
        if (left[i] !== right[i]) {
            return left[i] - right[i];
        }
    }

    return 0;
}


function satisfies(version, constraint = "*") {
    if (constraint === "*") {
        return true;
    }

    const match = constraint.match(/^(==|!=|>=|<=|>|<)(.+)$/);

    if (!match) {
        throw new PackageError(
            `Unsupported constraint: ${constraint}`
        );
    }

    const comparison = compareVersions(version, match[2]);

    switch (match[1]) {
        case "==": return comparison === 0;
        case "!=": return comparison !== 0;
        case ">=": return comparison >= 0;
        case "<=": return comparison <= 0;
        case ">": return comparison > 0;
        case "<": return comparison < 0;
        default: return false;
    }
}


class PackageRecord {
    constructor({
        name,
        version,
        description,
        dependencies = [],
        license = "MIT",
        source = "pypi",
        status = "available"
    }) {
        this.name = normalizeName(name);
        parseVersion(version);

        if (!description || typeof description !== "string") {
            throw new PackageError("Package description is required.");
        }

        if (!Array.isArray(dependencies)) {
            throw new PackageError("Dependencies must be an array.");
        }

        this.version = version;
        this.description = description;
        this.dependencies = dependencies.map(dependency => {
            const dependencyName = normalizeName(dependency.name);

            if (dependencyName === this.name) {
                throw new DependencyError(
                    "Self-dependency is prohibited."
                );
            }

            return Object.freeze({
                name: dependencyName,
                constraint: dependency.constraint || "*"
            });
        });

        this.license = license;
        this.source = source;
        this.status = status;

        if (!["available", "blocked", "deprecated"].includes(status)) {
            throw new PackageError("Invalid package status.");
        }

        Object.freeze(this.dependencies);
    }

    toJSON() {
        return {
            name: this.name,
            version: this.version,
            description: this.description,
            dependencies: this.dependencies,
            license: this.license,
            source: this.source,
            status: this.status
        };
    }
}


class Registry {
    #packages = new Map();

    publish(packageRecord) {
        if (!(packageRecord instanceof PackageRecord)) {
            throw new PackageError("Invalid package record.");
        }

        const versions = this.#packages.get(packageRecord.name) || [];

        if (versions.some(
            item => item.version === packageRecord.version
        )) {
            throw new PackageError("Duplicate package version.");
        }

        versions.push(packageRecord);

        versions.sort(
            (a, b) => compareVersions(b.version, a.version)
        );

        this.#packages.set(packageRecord.name, versions);
    }

    find(name, constraint = "*") {
        const key = normalizeName(name);
        const candidates = this.#packages.get(key) || [];

        const selected = candidates.find(
            item =>
                item.status === "available" &&
                satisfies(item.version, constraint)
        );

        if (!selected) {
            throw new DependencyError(
                `No compatible release found for ${key} ${constraint}`
            );
        }

        return selected;
    }
}


class Resolver {
    constructor(registry) {
        this.registry = registry;
    }

    resolve(rootName, constraint = "*") {
        const ordered = [];
        const visited = new Set();
        const active = new Set();

        const visit = (name, required) => {
            const packageName = normalizeName(name);

            if (active.has(packageName)) {
                throw new DependencyError(
                    `Circular dependency: ${packageName}`
                );
            }

            const record = this.registry.find(
                packageName,
                required
            );

            const identity = `${record.name}@${record.version}`;

            if (visited.has(identity)) {
                return;
            }

            active.add(packageName);

            for (const dependency of record.dependencies) {
                visit(dependency.name, dependency.constraint);
            }

            active.delete(packageName);
            visited.add(identity);
            ordered.push(record);
        };

        visit(rootName, constraint);
        return ordered;
    }
}


class SecurityPolicy {
    constructor({
        blocked = [],
        allowedLicenses = ["MIT", "BSD-3-Clause", "Apache-2.0", "ISC"],
        allowedSources = ["pypi"]
    } = {}) {
        this.blocked = new Set(blocked.map(normalizeName));
        this.allowedLicenses = new Set(allowedLicenses);
        this.allowedSources = new Set(allowedSources);
    }

    evaluate(packages) {
        const violations = [];

        for (const item of packages) {
            if (this.blocked.has(item.name)) {
                violations.push(`${item.name}: blocked`);
            }

            if (!this.allowedLicenses.has(item.license)) {
                violations.push(
                    `${item.name}: prohibited license`
                );
            }

            if (!this.allowedSources.has(item.source)) {
                violations.push(
                    `${item.name}: untrusted package source`
                );
            }
        }

        return violations;
    }
}


class PackageEnvironment extends EventEmitter {
    #installed = new Map();

    constructor(name, policy) {
        super();

        if (!name.trim()) {
            throw new PackageError("Environment name is required.");
        }

        this.name = name;
        this.policy = policy;
    }

    get installed() {
        return Array.from(this.#installed.values());
    }

    async install(packages) {
        if (!Array.isArray(packages) || packages.length === 0) {
            throw new PackageError("Installation list is empty.");
        }

        this.emit("installation:started", {
            environment: this.name,
            count: packages.length
        });

        try {
            const violations = this.policy.evaluate(packages);

            if (violations.length) {
                throw new PolicyError(violations.join("; "));
            }

            // Prepare a new state before committing the installation.
            const nextState = new Map(this.#installed);

            for (const item of packages) {
                const existing = nextState.get(item.name);

                if (
                    existing &&
                    existing.version !== item.version
                ) {
                    throw new DependencyError(
                        `Version conflict: ${item.name}`
                    );
                }

                nextState.set(item.name, item);
            }

            this.#installed = nextState;

            this.emit("installation:completed", {
                environment: this.name,
                count: packages.length
            });

            return this.installed;

        } catch (error) {
            this.emit("installation:failed", {
                message: error.message
            });

            throw error;
        }
    }

    uninstall(name) {
        const key = normalizeName(name);

        if (!this.#installed.has(key)) {
            throw new PackageError("Package is not installed.");
        }

        const dependents = this.installed.filter(item =>
            item.dependencies.some(dep => dep.name === key)
        );

        if (dependents.length) {
            throw new DependencyError(
                `Required by: ${dependents.map(p => p.name).join(", ")}`
            );
        }

        this.#installed.delete(key);

        this.emit("package:uninstalled", { name: key });
    }
}


function createRegistry() {
    const registry = new Registry();

    registry.publish(new PackageRecord({
        name: "numpy",
        version: "2.1.0",
        description: "Numerical computing."
    }));

    registry.publish(new PackageRecord({
        name: "pandas",
        version: "2.2.0",
        description: "Data analysis.",
        dependencies: [
            { name: "numpy", constraint: ">=2.0.0" }
        ]
    }));

    registry.publish(new PackageRecord({
        name: "requests",
        version: "2.32.0",
        description: "HTTP requests."
    }));

    registry.publish(new PackageRecord({
        name: "analytics-toolkit",
        version: "1.0.0",
        description: "Analytics application dependencies.",
        dependencies: [
            { name: "pandas", constraint: ">=2.2.0" },
            { name: "requests", constraint: ">=2.30.0" }
        ]
    }));

    return registry;
}


async function createLockFile(packages, destination) {
    const lock = {
        lockVersion: 1,
        generatedAt: new Date().toISOString(),
        packages: packages.map(item => ({
            name: item.name,
            version: item.version,
            dependencies: item.dependencies
        }))
    };

    const serialized = JSON.stringify(lock, null, 2);
    const temporary = `${destination}.${crypto.randomUUID()}.tmp`;

    try {
        await fs.mkdir(path.dirname(path.resolve(destination)), {
            recursive: true
        });

        await fs.writeFile(temporary, serialized, {
            encoding: "utf8",
            flag: "wx",
            mode: 0o600
        });

        await fs.rename(temporary, destination);

    } catch (error) {
        await fs.rm(temporary, { force: true }).catch(() => {});
        throw new PackageError(
            `Lock-file creation failed: ${error.message}`
        );
    }
}


async function main() {
    const registry = createRegistry();
    const resolver = new Resolver(registry);

    const policy = new SecurityPolicy({
        blocked: ["malicious-library"]
    });

    const environment = new PackageEnvironment(
        "analytics-environment",
        policy
    );

    environment.on("installation:started", event => {
        console.log("Installation started:", event);
    });

    environment.on("installation:completed", event => {
        console.log("Installation completed:", event);
    });

    environment.on("installation:failed", event => {
        console.error("Installation failed:", event.message);
    });

    console.log("\n1. Resolve package dependencies");

    const packages = resolver.resolve("analytics-toolkit");

    console.table(
        packages.map(item => ({
            package: item.name,
            version: item.version
        }))
    );

    console.log("\n2. Evaluate package policy");

    const violations = policy.evaluate(packages);

    if (violations.length) {
        throw new PolicyError(violations.join("; "));
    }

    console.log("Policy passed.");

    console.log("\n3. Install packages");

    await environment.install(packages);

    console.log("\n4. Generate dependency lock file");

    await createLockFile(
        packages,
        path.resolve("package-lock.json")
    );

    console.log("\n5. Verify version constraints");

    console.assert(satisfies("2.1.0", ">=2.0.0"));
    console.assert(!satisfies("1.0.0", ">=2.0.0"));

    console.log("\n6. Attempt protected uninstallation");

    try {
        environment.uninstall("numpy");
    } catch (error) {
        console.log("Expected failure:", error.message);
    }

    console.log("\n7. Installed environment");

    console.table(
        environment.installed.map(item => ({
            name: item.name,
            version: item.version
        }))
    );
}


main().catch(error => {
    console.error("Application error:", error.message);
    process.exitCode = 1;
});
