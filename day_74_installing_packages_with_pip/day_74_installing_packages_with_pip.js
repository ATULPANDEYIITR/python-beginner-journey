"use strict";

/*
 * Installing Packages with pip
 * Event-driven package installation and policy evaluation.
 *
 * Runtime: Node.js 18+
 * Dependencies: Node.js standard library only.
 *
 * Default: simulation.
 * Execute actual pip installations with --execute.
 */

const { spawn } = require("node:child_process");
const fs = require("node:fs/promises");
const path = require("node:path");
const EventEmitter = require("node:events");

const PackageState = Object.freeze({
    PENDING: "PENDING",
    VALIDATED: "VALIDATED",
    RESOLVING: "RESOLVING",
    INSTALLING: "INSTALLING",
    INSTALLED: "INSTALLED",
    FAILED: "FAILED",
    SKIPPED: "SKIPPED"
});

class PackageError extends Error {
    constructor(message, code = "PACKAGE_ERROR") {
        super(message);
        this.name = "PackageError";
        this.code = code;
    }
}

class PackageSpec {
    constructor(name, version = null, options = {}) {
        this.name = name;
        this.version = version;
        this.hashes = options.hashes || [];
        this.state = PackageState.PENDING;
        this.createdAt = new Date().toISOString();
    }

    get requirement() {
        return this.version
            ? `${this.name}==${this.version}`
            : this.name;
    }
}

class PackageValidator {
    static validate(spec) {
        if (!(spec instanceof PackageSpec)) {
            throw new PackageError(
                "Expected a PackageSpec object."
            );
        }

        const namePattern =
            /^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$/;

        const versionPattern =
            /^[A-Za-z0-9][A-Za-z0-9.!+_-]*$/;

        if (!namePattern.test(spec.name)) {
            throw new PackageError(
                `Invalid package name: ${spec.name}`
            );
        }

        if (
            spec.version !== null &&
            !versionPattern.test(spec.version)
        ) {
            throw new PackageError(
                `Invalid package version: ${spec.version}`
            );
        }

        for (const hash of spec.hashes) {
            if (!/^sha256:[a-fA-F0-9]{64}$/.test(hash)) {
                throw new PackageError(
                    "Invalid SHA-256 package hash."
                );
            }
        }

        spec.state = PackageState.VALIDATED;
        return spec;
    }
}

class InstallationPolicy {
    constructor({
        allowedPackages = [],
        deniedPackages = [],
        requirePinnedVersions = false,
        requireHashes = false,
        allowUpgrade = false
    } = {}) {
        this.allowedPackages = new Set(
            allowedPackages.map(name => name.toLowerCase())
        );

        this.deniedPackages = new Set(
            deniedPackages.map(name => name.toLowerCase())
        );

        this.requirePinnedVersions = requirePinnedVersions;
        this.requireHashes = requireHashes;
        this.allowUpgrade = allowUpgrade;
    }

    evaluate(spec, options = {}) {
        const normalized = spec.name.toLowerCase();

        if (this.deniedPackages.has(normalized)) {
            throw new PackageError(
                `${spec.name} is prohibited by installation policy.`,
                "POLICY_DENIED"
            );
        }

        if (
            this.allowedPackages.size > 0 &&
            !this.allowedPackages.has(normalized)
        ) {
            throw new PackageError(
                `${spec.name} is not in the package allowlist.`,
                "NOT_ALLOWLISTED"
            );
        }

        if (
            this.requirePinnedVersions &&
            !spec.version
        ) {
            throw new PackageError(
                "A pinned version is required.",
                "UNPINNED_VERSION"
            );
        }

        if (
            this.requireHashes &&
            spec.hashes.length === 0
        ) {
            throw new PackageError(
                "A verified package hash is required.",
                "HASH_REQUIRED"
            );
        }

        if (options.upgrade && !this.allowUpgrade) {
            throw new PackageError(
                "Upgrade operations are not permitted.",
                "UPGRADE_DENIED"
            );
        }

        return true;
    }
}

class PackageRegistry {
    constructor() {
        this.packages = new Map();
    }

    register(spec) {
        const key = spec.name.toLowerCase();

        if (this.packages.has(key)) {
            const existing = this.packages.get(key);

            if (existing.version !== spec.version) {
                throw new PackageError(
                    `Conflicting package definitions: ${spec.name}`
                );
            }

            return existing;
        }

        this.packages.set(key, spec);
        return spec;
    }

    get(name) {
        return this.packages.get(name.toLowerCase());
    }

    list() {
        return [...this.packages.values()];
    }
}

class PipExecutor extends EventEmitter {
    constructor({
        python = process.platform === "win32"
            ? "python"
            : "python3",
        timeout = 300000,
        execute = false,
        upgrade = false
    } = {}) {
        super();

        this.python = python;
        this.timeout = timeout;
        this.execute = execute;
        this.upgrade = upgrade;

        if (!Number.isInteger(timeout) || timeout <= 0) {
            throw new PackageError(
                "Timeout must be a positive integer."
            );
        }
    }

    buildArguments(spec) {
        const args = ["-m", "pip", "install"];

        if (!this.execute) {
            args.push("--dry-run");
        }

        if (this.upgrade) {
            args.push("--upgrade");
        }

        if (spec.hashes.length > 0) {
            args.push("--require-hashes");
        }

        args.push(spec.requirement);

        return args;
    }

    run(command, args) {
        return new Promise((resolve, reject) => {
            const child = spawn(command, args, {
                shell: false,
                windowsHide: true,
                stdio: ["ignore", "pipe", "pipe"]
            });

            let stdout = "";
            let stderr = "";
            let settled = false;

            const timer = setTimeout(() => {
                if (!settled) {
                    child.kill();
                    settled = true;

                    reject(
                        new PackageError(
                            "Package installation timed out.",
                            "TIMEOUT"
                        )
                    );
                }
            }, this.timeout);

            child.stdout.on("data", chunk => {
                stdout += chunk.toString();
            });

            child.stderr.on("data", chunk => {
                stderr += chunk.toString();
            });

            child.on("error", error => {
                if (!settled) {
                    settled = true;
                    clearTimeout(timer);

                    reject(
                        new PackageError(
                            `Process execution failed: ${error.message}`
                        )
                    );
                }
            });

            child.on("close", code => {
                if (settled) return;

                settled = true;
                clearTimeout(timer);

                if (code !== 0) {
                    reject(
                        new PackageError(
                            stderr.trim() ||
                            `pip exited with status ${code}.`
                        )
                    );
                    return;
                }

                resolve({
                    stdout: stdout.trim(),
                    stderr: stderr.trim(),
                    exitCode: code
                });
            });
        });
    }

    async install(spec) {
        const args = this.buildArguments(spec);

        this.emit("installation:started", {
            package: spec.requirement,
            execute: this.execute
        });

        try {
            if (!this.execute) {
                spec.state = PackageState.VALIDATED;

                const result = {
                    package: spec.requirement,
                    state: spec.state,
                    command: [this.python, ...args],
                    message: "Simulation only. No package was installed."
                };

                this.emit("installation:completed", result);
                return result;
            }

            spec.state = PackageState.INSTALLING;

            const output = await this.run(
                this.python,
                args
            );

            spec.state = PackageState.INSTALLED;

            const result = {
                package: spec.requirement,
                state: spec.state,
                output
            };

            this.emit("installation:completed", result);
            return result;

        } catch (error) {
            spec.state = PackageState.FAILED;

            this.emit("installation:failed", {
                package: spec.requirement,
                error: error.message
            });

            throw error;
        }
    }
}

class InstallationService {
    constructor(policy, executor) {
        this.policy = policy;
        this.executor = executor;
        this.registry = new PackageRegistry();
        this.history = [];
        this.active = new Set();
    }

    async install(spec) {
        PackageValidator.validate(spec);

        this.policy.evaluate(spec, {
            upgrade: this.executor.upgrade
        });

        const key = spec.name.toLowerCase();

        if (this.active.has(key)) {
            throw new PackageError(
                `Installation already active: ${spec.name}`
            );
        }

        const existing = this.registry.get(spec.name);

        if (
            existing &&
            existing.version !== spec.version
        ) {
            throw new PackageError(
                `Conflicting versions requested for ${spec.name}.`
            );
        }

        this.active.add(key);

        try {
            const result = await this.executor.install(spec);

            this.registry.register(spec);
            this.history.push({
                ...result,
                timestamp: new Date().toISOString()
            });

            return result;

        } catch (error) {
            this.history.push({
                package: spec.requirement,
                state: PackageState.FAILED,
                error: error.message,
                timestamp: new Date().toISOString()
            });

            throw error;

        } finally {
            this.active.delete(key);
        }
    }

    async installBatch(specifications) {
        const results = [];

        // Sequential execution avoids uncontrolled concurrent pip mutations.
        for (const spec of specifications) {
            try {
                results.push({
                    success: true,
                    result: await this.install(spec)
                });
            } catch (error) {
                results.push({
                    success: false,
                    package: spec.requirement,
                    error: error.message
                });
            }
        }

        return results;
    }

    async saveReport(filename) {
        const destination = path.resolve(filename);

        await fs.writeFile(
            destination,
            JSON.stringify(
                this.history,
                null,
                2
            ),
            {
                encoding: "utf8",
                mode: 0o600
            }
        );

        return destination;
    }
}

async function inspectEnvironment(python) {
    const executor = new PipExecutor({
        python,
        execute: true
    });

    const commands = [
        ["--version"],
        ["list", "--format=json"],
        ["check"]
    ];

    for (const args of commands) {
        try {
            const result = await executor.run(
                python,
                ["-m", "pip", ...args]
            );

            console.log(`\n$ python -m pip ${args.join(" ")}`);
            console.log(result.stdout.slice(0, 1500));

        } catch (error) {
            console.error(error.message);
        }
    }
}

async function main() {
    const execute = process.argv.includes("--execute");

    const policy = new InstallationPolicy({
        allowedPackages: ["requests", "numpy", "pandas"],
        deniedPackages: ["malicious-package"],
        requirePinnedVersions: true,
        allowUpgrade: false
    });

    const executor = new PipExecutor({
        execute,
        timeout: 300000
    });

    executor.on("installation:started", event => {
        console.log(
            `[STARTED] ${event.package}`
        );
    });

    executor.on("installation:completed", event => {
        console.log(
            `[COMPLETED] ${event.package}: ${event.state}`
        );
    });

    executor.on("installation:failed", event => {
        console.error(
            `[FAILED] ${event.package}: ${event.error}`
        );
    });

    const service = new InstallationService(
        policy,
        executor
    );

    const packages = [
        new PackageSpec("requests", "2.32.3"),
        new PackageSpec("numpy", "2.1.3"),
        new PackageSpec("pandas", "2.2.3"),
        new PackageSpec("unapproved-library", "1.0.0"),
        new PackageSpec("malicious-package", "1.0.0")
    ];

    console.log("\n=== PIP INSTALLATION WORKFLOW ===");
    console.log(
        execute
            ? "Execution mode enabled."
            : "Simulation mode enabled."
    );

    const results = await service.installBatch(packages);

    for (const result of results) {
        console.log(
            result.success
                ? result.result
                : `Rejected: ${result.package} - ${result.error}`
        );
    }

    const report = await service.saveReport(
        "pip_installation_report.json"
    );

    console.log(`\nReport: ${report}`);

    if (process.argv.includes("--inspect")) {
        await inspectEnvironment(
            process.platform === "win32"
                ? "python"
                : "python3"
        );
    }
}

main().catch(error => {
    console.error("Fatal error:", error.message);
    process.exitCode = 1;
});
